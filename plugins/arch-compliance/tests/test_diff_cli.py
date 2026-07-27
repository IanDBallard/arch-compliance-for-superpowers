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


def test_missing_mandates_fails_loud(tmp_path: Path) -> None:
    repo = tmp_path / "bare"
    repo.mkdir()
    _git(repo, "init")
    with pytest.raises(Exception):
        main(["--mode", "staged", "--repo", str(repo)])
