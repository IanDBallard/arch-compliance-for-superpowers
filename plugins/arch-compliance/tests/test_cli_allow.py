from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

from acf.approval import (
    ApprovalState,
    approval_rows,
    check_approval,
    describe_approval,
    file_digests,
    fingerprint,
    read_store,
    repo_key,
    store_path,
)
from acf.cli_allow import main
from acf.detectors import load_gate_registry
from acf.exceptions import GitError, UnknownDetectorError
from acf.registry import HOOK_CALL_SITES
from acf.repo import MANDATES_REL

PY_DIR = Path(__file__).resolve().parents[1] / "python"
RULES_SOURCE = "def check(*a, **k):\n    return []\n"


def _host(mid: str, *, file: str = "rules.py") -> str:
    return f"""- id: {mid}
  title: {mid}
  severity: BLOCK
  detection: guard
  detector: hostdet/{file}:check
  languages: none
  call_sites: [hook]
  exemption_tokens: []
  status: enforced
  arch_anchor: "# Fail loud"
  params:
    name: "a"
"""


def _llm(detector: str) -> str:
    return f"""- id: llm-row
  title: llm-row
  severity: WARN
  detection: llm
  detector: {detector}
  languages: none
  call_sites: [audit]
  exemption_tokens: []
  status: enforced
  arch_anchor: "# Fail loud"
"""


def _repo(tmp_path: Path, rows: list[str]) -> Path:
    repo = tmp_path / "repo"
    (repo / "hostdet").mkdir(parents=True)
    (repo / "hostdet" / "rules.py").write_text(RULES_SOURCE, encoding="utf-8")
    mandates = repo / MANDATES_REL
    mandates.parent.mkdir(parents=True)
    mandates.write_text("\n".join(rows), encoding="utf-8")
    return repo


def test_allow_prints_and_writes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = _repo(tmp_path, [_host("host-a"), _host("host-b")])
    assert main(["--repo", str(repo)]) == 0
    out = capsys.readouterr().out
    digest = hashlib.sha256((repo / "hostdet" / "rules.py").read_bytes()).hexdigest()
    for fragment in ("host-a", "host-b", "hostdet/rules.py:check", "hostdet/rules.py", digest,
                     "imported modules are not covered"):
        assert fragment in out
    assert repo_key(repo).key in read_store(store_path()).repos


def test_allow_no_host_rows_writes_nothing(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = _repo(tmp_path, [_llm("llm_fail_loud")])
    assert main(["--repo", str(repo)]) == 0
    assert not store_path().exists()
    assert "No host detector rows" in capsys.readouterr().out


def test_allow_missing_detector_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = _repo(tmp_path, [_host("host-a", file="absent.py")])
    assert main(["--repo", str(repo)]) == 1
    assert "absent.py" in capsys.readouterr().err
    assert not store_path().exists()


def test_allow_store_inside_repo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _repo(tmp_path, [_host("host-a")])
    monkeypatch.setenv("HOME", str(repo))
    monkeypatch.setenv("USERPROFILE", str(repo))
    assert main(["--repo", str(repo)]) == 1
    assert "inside the repository" in capsys.readouterr().err


def test_allow_revoke(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = _repo(tmp_path, [_host("host-a")])
    assert main(["--repo", str(repo)]) == 0
    capsys.readouterr()
    assert main(["--repo", str(repo), "--revoke"]) == 0
    assert "Removed" in capsys.readouterr().out
    assert repo_key(repo).key not in read_store(store_path()).repos


def test_allow_revoke_without_entry(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = _repo(tmp_path, [_host("host-a")])
    assert main(["--repo", str(repo), "--revoke"]) == 0
    assert "nothing to remove" in capsys.readouterr().out


def test_allow_relative_repo_matches_absolute_check(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _repo(tmp_path, [_host("host-a")])
    monkeypatch.chdir(repo)
    assert main(["--repo", "."]) == 0
    registry = load_gate_registry(repo, repo / MANDATES_REL)
    assert check_approval(repo, registry, HOOK_CALL_SITES).state is ApprovalState.APPROVED


def test_load_gate_registry_refuses_unknown_prompt_id(tmp_path: Path) -> None:
    repo = _repo(tmp_path, [_llm("no-such-prompt")])
    with pytest.raises(UnknownDetectorError):
        load_gate_registry(repo, repo / MANDATES_REL)


def test_detectors_import_does_not_import_httpx() -> None:
    env = {**os.environ, "PYTHONPATH": PY_DIR.as_posix()}
    result = subprocess.run(
        [sys.executable, "-c", "import acf.detectors, sys; print('httpx' in sys.modules)"],
        capture_output=True,
        text=True,
        env=env,
        check=True,
    )
    assert result.stdout.strip() == "False"


def _git_init(repo: Path) -> None:
    subprocess.run(["git", "init", "-q", str(repo)], check=True)


def _current(repo: Path) -> str:
    registry = load_gate_registry(repo, repo / MANDATES_REL)
    rows = approval_rows(registry)
    return fingerprint(rows, file_digests(repo, rows))


def _store_bytes() -> bytes | None:
    store = store_path()
    return store.read_bytes() if store.exists() else None


def test_fingerprint_match_writes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = _repo(tmp_path, [_host("host-a")])
    _git_init(repo)
    assert main(["--repo", str(repo), "--fingerprint", _current(repo)]) == 0
    assert repo_key(repo).key in read_store(store_path()).repos
    assert "every worktree of this repository" in capsys.readouterr().out


def test_fingerprint_mismatch_refuses(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = _repo(tmp_path, [_host("host-a")])
    before = _store_bytes()
    assert main(["--repo", str(repo), "--fingerprint", "deadbeef"]) == 1
    err = capsys.readouterr().err
    assert "reviewed deadbeef" in err
    assert _current(repo) in err
    assert "nothing approved" in err
    assert _store_bytes() == before


def test_child_session_requires_fingerprint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _repo(tmp_path, [_host("host-a")])
    monkeypatch.setenv("CLAUDE_CODE_CHILD_SESSION", "1")
    assert main(["--repo", str(repo)]) == 1
    assert "needs --fingerprint" in capsys.readouterr().err
    assert _store_bytes() is None
    assert main(["--repo", str(repo), "--fingerprint", _current(repo)]) == 0
    assert repo_key(repo).key in read_store(store_path()).repos


def test_child_session_revoke_without_fingerprint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _repo(tmp_path, [_host("host-a")])
    assert main(["--repo", str(repo)]) == 0
    monkeypatch.setenv("CLAUDE_CODE_CHILD_SESSION", "1")
    assert main(["--repo", str(repo), "--revoke"]) == 0
    assert repo_key(repo).key not in read_store(store_path()).repos


def test_child_session_revoke_ignores_fingerprint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _repo(tmp_path, [_host("host-a")])
    assert main(["--repo", str(repo)]) == 0
    monkeypatch.setenv("CLAUDE_CODE_CHILD_SESSION", "1")
    assert main(["--repo", str(repo), "--revoke", "--fingerprint", "bad"]) == 0
    assert repo_key(repo).key not in read_store(store_path()).repos


def test_allow_reports_key_git_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _repo(tmp_path, [_host("host-a")])

    def boom(_repo: Path) -> None:
        raise GitError("cannot compute the approval key for x: y")

    monkeypatch.setattr("acf.approval.git_common_dir", boom)
    assert main(["--repo", str(repo)]) == 1
    assert "acf: cannot compute the approval key" in capsys.readouterr().err


def test_allow_review_lines_equal_describe_approval(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _repo(tmp_path, [_host("host-a"), _host("host-b")])
    assert main(["--repo", str(repo)]) == 0
    lines = capsys.readouterr().out.splitlines()
    rows = approval_rows(load_gate_registry(repo, repo / MANDATES_REL))
    expected = describe_approval(repo, rows, file_digests(repo, rows))
    assert lines[:-1] == expected
    assert lines[-1].startswith(f"Approved {repo_key(repo).key} (this folder only) in ")
