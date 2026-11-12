from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

from acf.approval import (
    STORE_REL,
    ApprovalState,
    approval_rows,
    check_approval,
    file_digests,
    fingerprint,
    read_store,
    reason,
    require_approval,
    store_path,
    write_approval,
)
from acf.detectors import KNOWN_DETECTORS
from acf.exceptions import AcfInputError
from acf.registry import (
    DIFF_CALL_SITES,
    HOOK_CALL_SITES,
    MandateRegistry,
    load_mandates,
)

PY_DIR = Path(__file__).resolve().parents[1] / "python"


def _host(mid: str, sites: str, *, file: str = "rules.py", param: str = "a") -> str:
    return f"""- id: {mid}
  title: {mid}
  severity: BLOCK
  detection: guard
  detector: hostdet/{file}:check
  languages: none
  call_sites: {sites}
  exemption_tokens: []
  status: enforced
  arch_anchor: "# Fail loud"
  params:
    name: "{param}"
"""


def _manual(title: str) -> str:
    return f"""- id: manual-row
  title: {title}
  severity: WARN
  detection: manual
  detector: none
  languages: none
  call_sites: [audit]
  exemption_tokens: []
  status: enforced
  arch_anchor: "# Fail loud"
"""


def _repo(tmp_path: Path, rows: list[str]) -> Path:
    repo = tmp_path / "repo"
    (repo / "hostdet").mkdir(parents=True)
    (repo / "hostdet" / "rules.py").write_text("def check(*a, **k):\n    return []\n", encoding="utf-8")
    (repo / "hostdet" / "other.py").write_text("def check(*a, **k):\n    return []\n", encoding="utf-8")
    _write_rows(repo, rows)
    return repo


def _write_rows(repo: Path, rows: list[str]) -> None:
    (repo / "mandates.yml").write_text("\n".join(rows), encoding="utf-8")


def _registry(repo: Path) -> MandateRegistry:
    return load_mandates(repo / "mandates.yml", known_detectors=KNOWN_DETECTORS, repo_root=repo)


def test_store_path_under_home() -> None:
    assert store_path() == Path.home() / ".acf" / "approvals.json"
    assert STORE_REL == Path(".acf") / "approvals.json"


def test_store_path_runtime_error_is_acf_input_error(monkeypatch) -> None:
    def boom() -> Path:
        raise RuntimeError("no home")

    monkeypatch.setattr(Path, "home", staticmethod(boom))
    with pytest.raises(AcfInputError):
        store_path()


def test_read_store_missing_is_empty(tmp_path: Path) -> None:
    store = read_store(tmp_path / "nope.json")
    assert store.version == 1 and store.repos == {}


@pytest.mark.parametrize(
    "content",
    ["{not json", '{"version": 1, "repos": {}, "x": 1}', ""],
    ids=["invalid-json", "wrong-shape", "empty-file"],
)
def test_read_store_refusals_name_the_path(tmp_path: Path, content: str) -> None:
    path = tmp_path / "approvals.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(AcfInputError) as info:
        read_store(path)
    assert path.as_posix() in str(info.value) or str(path) in str(info.value)


def test_fingerprint_changes(tmp_path: Path) -> None:
    base_rows = [_host("h1", "[hook]"), _manual("t1")]
    repo = _repo(tmp_path, base_rows)

    def fp() -> str:
        rows = approval_rows(_registry(repo))
        return fingerprint(rows, file_digests(repo, rows))

    base = fp()
    _write_rows(repo, [_host("h1", "[hook]", param="b"), _manual("t1")])
    assert fp() != base  # params change
    _write_rows(repo, base_rows + [_host("h2", "[hook]")])
    assert fp() != base  # added host row
    _write_rows(repo, base_rows)
    assert fp() == base
    (repo / "hostdet" / "rules.py").write_text("def check(*a, **k):\n    return [1]\n", encoding="utf-8")
    assert fp() != base  # detector byte change
    (repo / "hostdet" / "rules.py").write_text("def check(*a, **k):\n    return []\n", encoding="utf-8")
    assert fp() == base
    _write_rows(repo, [_host("h1", "[hook]"), _manual("t2")])
    assert fp() == base  # built-in row change
    ci_rows = base_rows + [_host("h3", "[ci]")]
    _write_rows(repo, ci_rows)
    with_ci = fp()
    _write_rows(repo, base_rows + [_host("h3", "[ci]", param="z")])
    assert fp() != with_ci  # [ci]-only host row change


def test_fingerprint_stable_across_hash_seeds(tmp_path: Path) -> None:
    repo = _repo(tmp_path, [_host("h1", "[hook, ci]"), _host("h2", "[ci]", file="other.py", param="q")])
    code = (
        "import sys; from pathlib import Path; "
        "from acf.approval import approval_rows, file_digests, fingerprint; "
        "from acf.detectors import KNOWN_DETECTORS; from acf.registry import load_mandates; "
        "repo = Path(sys.argv[1]); "
        "reg = load_mandates(repo / 'mandates.yml', known_detectors=KNOWN_DETECTORS, repo_root=repo); "
        "rows = approval_rows(reg); "
        "print(fingerprint(rows, file_digests(repo, rows)))"
    )
    outputs = set()
    for seed in ("1", "2", "3"):
        env = {**os.environ, "PYTHONHASHSEED": seed, "PYTHONPATH": str(PY_DIR), "PYTHONUTF8": "1"}
        proc = subprocess.run(
            [sys.executable, "-c", code, str(repo)],
            capture_output=True, text=True, env=env, check=False,
        )
        assert proc.returncode == 0, proc.stderr
        outputs.add(proc.stdout.strip())
    assert len(outputs) == 1 and next(iter(outputs))


def test_check_approval_states(tmp_path: Path, monkeypatch) -> None:
    repo = _repo(tmp_path, [_host("h1", "[hook]")])
    assert check_approval(repo, _registry(_repo(tmp_path / "x", [_manual("t")])), HOOK_CALL_SITES).state is ApprovalState.NOT_NEEDED
    reg = _registry(repo)
    assert check_approval(repo, reg, HOOK_CALL_SITES).state is ApprovalState.MISSING
    write_approval(repo, reg)
    expected = hashlib.sha256((repo / "hostdet" / "rules.py").read_bytes()).hexdigest()
    result = check_approval(repo, reg, HOOK_CALL_SITES)
    assert result.state is ApprovalState.APPROVED
    assert result.digests == {"hostdet/rules.py": expected}
    (repo / "hostdet" / "rules.py").write_text("def check(*a, **k):\n    return [2]\n", encoding="utf-8")
    stale = check_approval(repo, reg, HOOK_CALL_SITES)
    assert stale.state is ApprovalState.STALE and stale.digests == {}
    monkeypatch.setenv("HOME", str(repo))
    monkeypatch.setenv("USERPROFILE", str(repo))
    in_repo = check_approval(repo, reg, HOOK_CALL_SITES)
    assert in_repo.state is ApprovalState.STORE_IN_REPO and in_repo.digests == {}
    with pytest.raises(AcfInputError, match="is inside the repository"):
        write_approval(repo, reg)


def test_not_needed_when_call_sites_select_no_host_row(tmp_path: Path) -> None:
    repo = _repo(tmp_path, [_host("h1", "[hook]")])
    assert check_approval(repo, _registry(repo), DIFF_CALL_SITES).state is ApprovalState.NOT_NEEDED


def test_one_approval_covers_hook_and_diff(tmp_path: Path) -> None:
    repo = _repo(tmp_path, [_host("h1", "[hook]"), _host("h2", "[ci]", file="other.py")])
    reg = _registry(repo)
    write_approval(repo, reg)
    assert check_approval(repo, reg, HOOK_CALL_SITES).state is ApprovalState.APPROVED
    assert check_approval(repo, reg, DIFF_CALL_SITES).state is ApprovalState.APPROVED


def test_require_approval_raises_with_refusal_text(tmp_path: Path) -> None:
    repo = _repo(tmp_path, [_host("h1", "[hook]"), _host("h0", "[hook]")])
    reg = _registry(repo)
    with pytest.raises(AcfInputError) as info:
        require_approval(repo, reg, HOOK_CALL_SITES)
    message = str(info.value)
    assert message.startswith(
        "host detectors need approval: no approval for this repository; rows: h0, h1. "
    )
    assert "acf-allow" in message and "--trusted-checkout" in message
    write_approval(repo, reg)
    assert require_approval(repo, reg, HOOK_CALL_SITES).state is ApprovalState.APPROVED


def test_reason_strings() -> None:
    store = Path("/h/.acf/approvals.json")
    assert reason(ApprovalState.STALE, store) == "the host rows or detector files changed since approval"
    assert reason(ApprovalState.STORE_IN_REPO, store) == (
        "the approval store /h/.acf/approvals.json is inside the repository"
    )


def test_revoke_removes_only_that_repo(tmp_path: Path) -> None:
    repo_a = _repo(tmp_path / "a", [_host("h1", "[hook]")])
    repo_b = _repo(tmp_path / "b", [_host("h1", "[hook]")])
    write_approval(repo_a, _registry(repo_a))
    write_approval(repo_b, _registry(repo_b))
    write_approval(repo_a, _registry(repo_a), revoke=True)
    keys = set(read_store(store_path()).repos)
    assert keys == {repo_b.resolve().as_posix()}


def test_write_approval_preserves_other_repos(tmp_path: Path) -> None:
    repo_a = _repo(tmp_path / "a", [_host("h1", "[hook]")])
    repo_b = _repo(tmp_path / "b", [_host("h1", "[hook]", param="other")])
    write_approval(repo_a, _registry(repo_a))
    entry_a = read_store(store_path()).repos[repo_a.resolve().as_posix()]
    write_approval(repo_b, _registry(repo_b))
    repos = read_store(store_path()).repos
    assert repos[repo_a.resolve().as_posix()] == entry_a
    assert set(repos) == {repo_a.resolve().as_posix(), repo_b.resolve().as_posix()}
    assert not list(store_path().parent.glob("*.tmp"))


def test_file_digests_unreadable_file_refused(tmp_path: Path) -> None:
    repo = _repo(tmp_path, [_host("h1", "[hook]")])
    reg = _registry(repo)
    (repo / "hostdet" / "rules.py").unlink()
    with pytest.raises(AcfInputError, match="hostdet/rules.py"):
        file_digests(repo, approval_rows(reg))


def test_two_rows_one_file_single_digest(tmp_path: Path) -> None:
    repo = _repo(tmp_path, [_host("h1", "[hook]"), _host("h2", "[ci]")])
    digests = file_digests(repo, approval_rows(_registry(repo)))
    assert list(digests) == ["hostdet/rules.py"]
