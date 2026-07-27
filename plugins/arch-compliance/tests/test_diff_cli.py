from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from acf.cli_check_diff import main

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

    code = main(["--mode", "staged", "--repo", str(repo)])
    assert code == 1


def test_staged_clean_file_exits_0(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    good = repo / "good.py"
    good.write_text(
        "def f():\n    try:\n        g()\n    except ValueError:\n        raise\n",
        encoding="utf-8",
    )
    _git(repo, "add", "good.py")

    code = main(["--mode", "staged", "--repo", str(repo)])
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

    code = main(["--mode", "staged", "--repo", str(repo)])
    assert code == 0


def test_unenforced_mandate_does_not_gate(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_mandates(repo, _BARE_EXCEPT_ROW.format(severity="BLOCK", status="unenforced"))
    _stage_bad_py(repo)

    code = main(["--mode", "staged", "--repo", str(repo)])
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

    code = main(["--mode", "staged", "--repo", str(repo)])
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

    assert main(["--mode", "worktree", "--repo", str(repo)]) == 0  # clean tree
    assert main(["--base", base, "--repo", str(repo)]) == 1


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

    assert main(["--base", base, "--repo", str(repo)]) == 0


def test_missing_mandates_fails_loud(tmp_path: Path) -> None:
    repo = tmp_path / "bare"
    repo.mkdir()
    _git(repo, "init")
    with pytest.raises(Exception):
        main(["--mode", "staged", "--repo", str(repo)])
