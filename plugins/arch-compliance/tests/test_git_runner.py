"""run_git decodes stdout as strict UTF-8, fails loud, and takes an environment."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

import acf.diff
from acf.diff import git_common_dir, run_git
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


_GIT_ID = ["-c", "user.name=T", "-c", "user.email=t@example.com"]


def _init_commit(repo: Path) -> None:
    _init(repo)
    subprocess.run(
        ["git", *_GIT_ID, "commit", "-q", "--allow-empty", "-m", "init"], cwd=repo, check=True
    )


def _worktree(repo: Path, path: Path) -> None:
    subprocess.run(
        ["git", *_GIT_ID, "worktree", "add", "-q", str(path), "-b", path.name.replace(" ", "-")],
        cwd=repo, check=True,
    )


def _pair(tmp_path: Path) -> tuple[Path, Path]:
    repo, wt = tmp_path / "repo", tmp_path / "wt"
    _init_commit(repo)
    _worktree(repo, wt)
    return repo, wt


def test_common_dir_main_and_worktree_equal(tmp_path):
    repo, wt = _pair(tmp_path)
    expected = subprocess.run(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
        cwd=repo, capture_output=True, text=True, check=True,
    ).stdout.strip()
    assert git_common_dir(repo) == (Path(expected), "")
    assert git_common_dir(wt) == (Path(expected), "")


def test_common_dir_subfolder_prefix(tmp_path):
    repo, wt = _pair(tmp_path)
    for root in (repo, wt):
        (root / "sub").mkdir()
        result = git_common_dir(root / "sub")
        assert result is not None and result[1] == "sub"


def test_common_dir_ignores_inherited_git_dir(tmp_path, monkeypatch):
    repo, wt = _pair(tmp_path)
    (wt / "sub").mkdir()
    git_dir = subprocess.run(
        ["git", "rev-parse", "--path-format=absolute", "--git-dir"],
        cwd=wt, capture_output=True, text=True, check=True,
    ).stdout.strip()
    monkeypatch.setenv("GIT_DIR", git_dir)
    result = git_common_dir(wt / "sub")
    assert result is not None and result[1] == "sub"


def test_common_dir_none_outside_repo(tmp_path):
    plain = tmp_path / "plain"
    plain.mkdir()
    assert subprocess.run(["git", "rev-parse"], cwd=plain, capture_output=True).returncode == 128
    assert git_common_dir(plain) is None


@pytest.mark.parametrize("failure", ["exit128", "exit1", "oserror"])
def test_common_dir_raises_on_other_failures(tmp_path, monkeypatch, failure):
    _init_commit(tmp_path)
    real = acf.diff.run_git
    calls = []

    def fake(repo, *args, env=None):
        calls.append(args)
        if len(calls) == 1:
            return real(repo, *args, env=env)
        if failure == "oserror":
            raise FileNotFoundError("git")
        code, err = (128, "fatal: other") if failure == "exit128" else (1, "")
        return subprocess.CompletedProcess(["git", *args], code, "", err)

    monkeypatch.setattr(acf.diff, "run_git", fake)
    with pytest.raises(GitError, match="cannot compute the approval key") as info:
        git_common_dir(tmp_path)
    if failure == "exit128":
        assert "fatal: other" in str(info.value)


def test_common_dir_path_with_space(tmp_path):
    repo, wt = tmp_path / "my repo", tmp_path / "my wt"
    _init_commit(repo)
    _worktree(repo, wt)
    a, b = git_common_dir(repo), git_common_dir(wt)
    assert a is not None and a == b
    assert "my repo" in a[0].as_posix()
