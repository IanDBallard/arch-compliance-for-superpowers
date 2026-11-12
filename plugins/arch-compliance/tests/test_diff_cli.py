from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from acf.approval import write_approval
from acf.cli_check_diff import main
from acf.detectors import load_gate_registry
from acf.repo import MANDATES_REL

FIXTURES = Path(__file__).parent / "fixtures"
MANDATES_SRC = FIXTURES / "mandates_valid.yml"


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")
    mandates_dir = repo / "config" / "architecture"
    mandates_dir.mkdir(parents=True)
    shutil.copy(MANDATES_SRC, mandates_dir / "mandates.yml")
    _git(repo, "add", "config/architecture/mandates.yml")
    _git(repo, "commit", "-m", "init mandates")
    return repo


def test_staged_bare_except_exits_1(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    bad = repo / "bad.py"
    bad.write_text(
        "def f():\n    try:\n        g()\n    except Exception:\n        pass\n",
        encoding="utf-8",
    )
    _git(repo, "add", "bad.py")

    code = main(["--mode", "staged", "--repo", str(repo), "--call-site", "ci"])
    assert code == 1


def test_staged_clean_file_exits_0(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    good = repo / "good.py"
    good.write_text(
        "def f():\n    try:\n        g()\n    except ValueError:\n        raise\n",
        encoding="utf-8",
    )
    _git(repo, "add", "good.py")

    code = main(["--mode", "staged", "--repo", str(repo), "--call-site", "ci"])
    assert code == 0


def _write_mandates(repo: Path, yaml_text: str) -> None:
    (repo / "config" / "architecture" / "mandates.yml").write_text(
        yaml_text, encoding="utf-8"
    )


_BARE_EXCEPT_ROW = """- id: fail-loud.bare-except
  title: Bare except and broad Exception handlers
  severity: {severity}
  detection: ast
  detector: fail_loud_bare_except
  languages: python
  call_sites: [ci, hook]
  exemption_tokens: [fail-loud.bare-except-ok]
  status: {status}
  arch_anchor: "# Fail loud"
"""


_HASATTR_ROW = """- id: no-shims.hasattr
  title: hasattr shims
  severity: WARN
  detection: ast
  detector: no_shims_hasattr
  languages: python
  call_sites: [ci]
  exemption_tokens: [no-shims.hasattr-ok]
  status: enforced
  arch_anchor: "# No shims"
"""


def _stage_bad_py(repo: Path) -> None:
    bad = repo / "bad.py"
    bad.write_text(
        "def f():\n    try:\n        g()\n    except Exception:\n        pass\n",
        encoding="utf-8",
    )
    _git(repo, "add", "bad.py")


def test_registry_severity_demotes_block_to_warn(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_mandates(repo, _BARE_EXCEPT_ROW.format(severity="WARN", status="enforced"))
    _stage_bad_py(repo)

    code = main(["--mode", "staged", "--repo", str(repo), "--call-site", "ci"])
    assert code == 0


def test_unenforced_mandate_does_not_gate(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_mandates(
        repo,
        _BARE_EXCEPT_ROW.format(severity="BLOCK", status="unenforced") + _HASATTR_ROW,
    )
    _stage_bad_py(repo)

    code = main(["--mode", "staged", "--repo", str(repo), "--call-site", "ci"])
    assert code == 0


def test_registry_exemption_token_exempts_line(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    bad = repo / "bad.py"
    bad.write_text(
        "def f():\n"
        "    try:\n"
        "        g()\n"
        "    except Exception:  # fail-loud.bare-except-ok: CLI top-level guard\n"
        "        raise SystemExit(1)\n",
        encoding="utf-8",
    )
    _git(repo, "add", "bad.py")

    code = main(["--mode", "staged", "--repo", str(repo), "--call-site", "ci"])
    assert code == 0


def _head_sha(repo: Path) -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def test_base_mode_flags_violation_committed_after_base(tmp_path: Path) -> None:
    """CI use case: a clean checkout has no staged/worktree diff; --base must
    still catch violations committed on the branch since the base ref."""
    repo = _init_repo(tmp_path)
    base = _head_sha(repo)

    bad = repo / "bad.py"
    bad.write_text(
        "def f():\n    try:\n        g()\n    except Exception:\n        pass\n",
        encoding="utf-8",
    )
    _git(repo, "add", "bad.py")
    _git(repo, "commit", "-m", "add bad handler")

    assert main(["--mode", "worktree", "--repo", str(repo), "--call-site", "ci"]) == 0  # clean tree
    assert main(["--base", base, "--repo", str(repo), "--call-site", "ci"]) == 1


def test_base_mode_ignores_violations_already_in_base(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    bad = repo / "legacy.py"
    bad.write_text(
        "def f():\n    try:\n        g()\n    except Exception:\n        pass\n",
        encoding="utf-8",
    )
    _git(repo, "add", "legacy.py")
    _git(repo, "commit", "-m", "legacy violation in base")
    base = _head_sha(repo)

    good = repo / "clean.py"
    good.write_text("def g():\n    return 1\n", encoding="utf-8")
    _git(repo, "add", "clean.py")
    _git(repo, "commit", "-m", "clean change")

    assert main(["--base", base, "--repo", str(repo), "--call-site", "ci"]) == 0


def test_invalid_base_ref_exits_1(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = _init_repo(tmp_path)
    code = main(["--base", "does-not-exist-ref", "--repo", str(repo), "--call-site", "ci"])
    assert code == 1
    err = capsys.readouterr().err
    assert "acf:" in err
    assert "git" in err.lower()


def test_missing_mandates_fails_loud(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = tmp_path / "bare"
    repo.mkdir()
    _git(repo, "init")
    code = main(["--mode", "staged", "--repo", str(repo), "--call-site", "ci"])
    assert code == 1
    assert "mandates file not found" in capsys.readouterr().err


def test_run_git_reports_nonzero_as_data(tmp_path):
    """run_git never raises on a non-zero status; the caller decides."""
    from acf.diff import run_git

    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    proc = run_git(tmp_path, "rev-parse", "--verify", "refs/heads/nope")
    assert proc.returncode != 0
    assert proc.stdout == "" or "nope" not in proc.stdout


def test_run_git_returns_stdout_on_success(tmp_path):
    from acf.diff import run_git

    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    proc = run_git(tmp_path, "rev-parse", "--is-inside-work-tree")
    assert proc.returncode == 0
    assert proc.stdout.strip() == "true"


def test_git_wrapper_still_raises_on_nonzero(tmp_path):
    """The existing contract is unchanged: _git raises, callers rely on it."""
    from acf.diff import _git as acf_git
    from acf.exceptions import GitError

    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    with pytest.raises(GitError) as excinfo:
        acf_git(tmp_path, "rev-parse", "--verify", "refs/heads/nope")
    assert "rev-parse" in str(excinfo.value)


def test_git_wrapper_raises_outside_a_repository(tmp_path):
    """Review Focus 5: a directory that is not a git repository."""
    from acf.diff import _git as acf_git
    from acf.diff import run_git
    from acf.exceptions import GitError

    plain = tmp_path / "not_a_repo"
    plain.mkdir()
    with pytest.raises(GitError):
        acf_git(plain, "status", "--porcelain")
    proc = run_git(plain, "status", "--porcelain")
    assert proc.returncode != 0


def test_ci_only_row_reports_at_ci_not_at_precommit(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _init_repo(tmp_path)
    row = _BARE_EXCEPT_ROW.format(severity="BLOCK", status="enforced").replace(
        "[ci, hook]", "[ci]"
    )
    _write_mandates(repo, row + _HASATTR_ROW.replace("[ci]", "[precommit]"))
    _stage_bad_py(repo)

    assert main(["--mode", "staged", "--repo", str(repo), "--call-site", "ci"]) == 1
    assert "fail-loud.bare-except" in capsys.readouterr().out
    assert main(["--mode", "staged", "--repo", str(repo), "--call-site", "precommit"]) == 0
    assert "fail-loud.bare-except" not in capsys.readouterr().out


def test_call_site_is_required(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    with pytest.raises(SystemExit):
        main(["--mode", "staged", "--repo", str(repo)])


def test_site_with_no_active_row_is_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _init_repo(tmp_path)
    row = _BARE_EXCEPT_ROW.format(severity="BLOCK", status="enforced").replace(
        "[ci, hook]", "[ci]"
    )
    _write_mandates(repo, row)
    _stage_bad_py(repo)

    code = main(["--mode", "staged", "--repo", str(repo), "--call-site", "precommit"])
    assert code == 1
    assert "selects no active" in capsys.readouterr().err


# ---------------------------------------------------------------- host detectors

_HOST_MODULE = '''from acf.detectors.host import HostHit


def scan_ast(text, path, added_lines, *, tree, params):
    for n, line in enumerate(text.splitlines(), 1):
        if "HOST_MARKER" in line:
            yield HostHit(path=path, line=n, message="host ast marker")


def scan_guard(repo_root, changed_files, *, params):
    for rel in changed_files:
        if rel.endswith(".md"):
            yield HostHit(path=rel, line=1, message="host guard on a document")
'''


def _host_rows(sites: str) -> str:
    return f"""- id: host.ast-marker
  title: Host ast marker
  severity: BLOCK
  detection: ast
  detector: hostdet/rules.py:scan_ast
  languages: python
  call_sites: {sites}
  exemption_tokens: [host.ast-marker-ok]
  status: enforced
  arch_anchor: "# Host"
- id: host.doc-guard
  title: Host doc guard
  severity: BLOCK
  detection: guard
  detector: hostdet/rules.py:scan_guard
  languages: none
  call_sites: {sites}
  exemption_tokens: [host.doc-ok]
  status: enforced
  arch_anchor: "# Host"
"""


def _host_repo(tmp_path: Path, rows: str) -> Path:
    repo = _init_repo(tmp_path)
    (repo / "hostdet").mkdir()
    (repo / "hostdet" / "rules.py").write_text(_HOST_MODULE, encoding="utf-8")
    _write_mandates(repo, rows)
    return repo


def _approve(repo: Path) -> None:
    write_approval(repo, load_gate_registry(repo, repo / MANDATES_REL))


def _json_ids(capsys: pytest.CaptureFixture[str]) -> list[tuple[str, str]]:
    import json

    out = capsys.readouterr().out
    return sorted((f["mandate_id"], f["path"]) for f in json.loads(out))


def test_host_ast_and_guard_rows_run_at_ci_and_block(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], fresh_host_loader
) -> None:
    repo = _host_repo(tmp_path, _host_rows("[ci]"))
    _approve(repo)
    (repo / "pkg").mkdir()
    (repo / "pkg" / "a.py").write_text("x = 1  # HOST_MARKER\n", encoding="utf-8")
    (repo / "notes.md").write_text("plain text\n", encoding="utf-8")
    _git(repo, "add", "pkg/a.py", "notes.md")

    code = main(["--mode", "staged", "--repo", str(repo), "--call-site", "ci", "--json"])
    assert code == 1
    assert _json_ids(capsys) == [
        ("host.ast-marker", "pkg/a.py"),
        ("host.doc-guard", "notes.md"),
    ]


def _stage_host_inputs(repo: Path) -> None:
    (repo / "pkg").mkdir()
    (repo / "pkg" / "a.py").write_text("x = 1  # HOST_MARKER\n", encoding="utf-8")
    (repo / "notes.md").write_text("plain text\n", encoding="utf-8")
    _git(repo, "add", "pkg/a.py", "notes.md")


_CI_ARGS = ["--mode", "staged", "--call-site", "ci", "--json"]


def test_host_rows_unapproved_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], fresh_host_loader
) -> None:
    repo = _host_repo(tmp_path, _host_rows("[ci]"))
    marker = tmp_path / "host-imported.marker"
    (repo / "hostdet" / "rules.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('ran', encoding='utf-8')\n"
        + _HOST_MODULE,
        encoding="utf-8",
    )
    _stage_host_inputs(repo)

    code = main(["--repo", str(repo), *_CI_ARGS])
    err = capsys.readouterr().err
    assert code == 1
    assert "acf-allow" in err
    assert "--trusted-checkout" in err
    assert not marker.exists()


def test_host_rows_trusted_checkout_runs(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], fresh_host_loader
) -> None:
    repo = _host_repo(tmp_path, _host_rows("[ci]"))
    _stage_host_inputs(repo)

    code = main(["--repo", str(repo), *_CI_ARGS, "--trusted-checkout"])
    assert code == 1
    assert _json_ids(capsys) == [
        ("host.ast-marker", "pkg/a.py"),
        ("host.doc-guard", "notes.md"),
    ]


def test_host_rows_approved_runs_without_flag(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], fresh_host_loader
) -> None:
    repo = _host_repo(tmp_path, _host_rows("[ci]"))
    _approve(repo)
    _stage_host_inputs(repo)

    code = main(["--repo", str(repo), *_CI_ARGS])
    assert code == 1
    assert _json_ids(capsys) == [
        ("host.ast-marker", "pkg/a.py"),
        ("host.doc-guard", "notes.md"),
    ]


def test_no_host_rows_no_approval_unchanged(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _stage_bad_py(repo)
    _git(repo, "add", "bad.py")

    assert main(["--repo", str(repo), "--mode", "staged", "--call-site", "ci"]) == 1


def test_hook_only_host_row_does_not_refuse_ci(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], fresh_host_loader
) -> None:
    rows = _host_rows("[hook]")
    rows = rows[: rows.index("- id: host.doc-guard")]
    repo = _host_repo(tmp_path, rows + _BARE_EXCEPT_ROW.format(severity="BLOCK", status="enforced"))
    _stage_bad_py(repo)
    _git(repo, "add", "bad.py")

    code = main(["--repo", str(repo), *_CI_ARGS])
    assert code == 1
    assert _json_ids(capsys) == [("fail-loud.bare-except", "bad.py")]


def test_stale_approval_refused(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], fresh_host_loader
) -> None:
    repo = _host_repo(tmp_path, _host_rows("[ci]"))
    _approve(repo)
    (repo / "hostdet" / "rules.py").write_text(_HOST_MODULE + "\n# edited\n", encoding="utf-8")
    _stage_host_inputs(repo)

    code = main(["--repo", str(repo), *_CI_ARGS])
    assert code == 1
    assert "changed since approval" in capsys.readouterr().err


def test_host_guard_exemption_token_on_a_non_code_file_is_honoured(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], fresh_host_loader
) -> None:
    repo = _host_repo(tmp_path, _host_rows("[ci]"))
    _approve(repo)
    (repo / "notes.md").write_text("# host.doc-ok: generated changelog\n", encoding="utf-8")
    _git(repo, "add", "notes.md")

    code = main(["--mode", "staged", "--repo", str(repo), "--call-site", "ci", "--json"])
    assert code == 0
    assert _json_ids(capsys) == []


def test_host_guard_only_row_at_precommit_passes_selection_and_reports(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], fresh_host_loader
) -> None:
    """Review Focus 4: a host guard row alone selects the precommit site."""
    rows = _host_rows("[precommit]")
    guard_only = rows[rows.index("- id: host.doc-guard") :]
    repo = _host_repo(tmp_path, guard_only)
    _approve(repo)
    (repo / "notes.md").write_text("plain text\n", encoding="utf-8")
    _git(repo, "add", "notes.md")

    code = main(
        ["--mode", "staged", "--repo", str(repo), "--call-site", "precommit", "--json"]
    )
    assert code == 1
    assert _json_ids(capsys) == [("host.doc-guard", "notes.md")]
