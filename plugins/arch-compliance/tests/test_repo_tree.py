"""RepoTree is the one owner of repository path resolution."""
from __future__ import annotations

from pathlib import Path

import pytest

from acf.repo import RepoTree


def test_contained_refuses_escape(tmp_path):
    t = RepoTree(tmp_path)
    assert t.contained("../x") is None
    assert t.contained(str(tmp_path.parent / "elsewhere.py")) is None


def test_contained_absolute_inside_root(tmp_path):
    assert RepoTree(tmp_path).contained(str(tmp_path / "a.py")) == (tmp_path / "a.py").resolve()


def test_contained_symlink_escape(tmp_path):
    outside = tmp_path / "out"
    outside.mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    try:
        (repo / "link").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("platform cannot create symlinks")
    assert RepoTree(repo).contained("link/a.py") is None


@pytest.mark.parametrize("exc", [RuntimeError, ValueError])
def test_contained_maps_resolve_errors(tmp_path, monkeypatch, exc):
    tree = RepoTree(tmp_path)  # resolve the root before patching

    def boom(self, strict=False):
        raise exc("x")

    monkeypatch.setattr(Path, "resolve", boom)
    assert tree.contained("a.py") is None


def test_file_and_directory(tmp_path):
    (tmp_path / "d").mkdir()
    (tmp_path / "f.py").write_text("x", encoding="utf-8")
    t = RepoTree(tmp_path)
    assert t.file("f.py") and t.file("d") is None and t.file("missing.py") is None
    assert t.directory("d") and t.directory("f.py") is None


def test_key(tmp_path):
    t = RepoTree(tmp_path)
    assert t.key(t.root / "a" / "b.py") == "a/b.py"
