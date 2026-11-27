"""run_git decodes stdout as strict UTF-8, fails loud, and takes an environment."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from acf.diff import run_git
from acf.exceptions import GitError


def _init(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)


def test_run_git_raises_on_non_utf8_stdout(tmp_path):
    _init(tmp_path)
    oid = subprocess.run(
        ["git", "hash-object", "-w", "--stdin"],
        cwd=tmp_path, input=b"\xff\xfe", capture_output=True, check=True,
    ).stdout.decode("ascii").strip()
    with pytest.raises(GitError, match="cat-file"):
        run_git(tmp_path, "cat-file", "-p", oid)


@pytest.mark.parametrize("name", ["Á", "é"])
def test_run_git_returns_non_ascii_path_intact(tmp_path, name):
    repo = tmp_path / name
    _init(repo)
    out = run_git(repo, "rev-parse", "--absolute-git-dir").stdout
    assert out is not None
    assert out.strip().endswith(f"{name}/.git")


def test_run_git_passes_env(tmp_path):
    _init(tmp_path)
    proc = run_git(
        tmp_path, "var", "GIT_AUTHOR_IDENT", env={**os.environ, "GIT_AUTHOR_NAME": "Zed", "GIT_AUTHOR_EMAIL": "z@example.com"}
    )
    assert proc.stdout.startswith("Zed")
