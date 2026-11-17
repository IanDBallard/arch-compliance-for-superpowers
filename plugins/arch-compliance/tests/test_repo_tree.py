"""RepoTree is the one owner of repository path resolution."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from acf.exceptions import AcfInputError
from acf.repo import REVIEW_REL, RepoTree, path_matches


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


@pytest.mark.parametrize("key,pattern,hit", [
    ("tests/a.py", "tests/", True),
    ("plugins/arch-compliance/tests/x.py", "tests/", True),
    ("docs/reviews/r.md", "docs/reviews/", True),
    ("x/docs/reviews/r.md", "docs/reviews/", False),
    ("a/b/test_x.py", "test_*.py", True),
    ("templates/families/f.tex", "templates/families/**/*.tex", True),
    ("templates/families/a/b/f.tex", "templates/families/**/*.tex", True),
    ("admin/js/vendor/x/y.js", "admin/js/vendor/**", True),
    ("templates/families/a/style.yml", "templates/families/*/style.yml", True),
    ("templates/families/a/b/style.yml", "templates/families/*/style.yml", False),
    ("src/a.test.ts", "**/*.test.*", True),
    ("archive/x.py", "archive/", True),
    ("a.test.ts", "**/*.test.*", True),
    ("tests", "tests/", False),
    ("a/b.py", "a/?.py", True),
    ("a/bc.py", "a/?.py", False),
])
def test_path_matches_forms(key, pattern, hit):
    assert path_matches(key, pattern) is hit


def test_backslash_pattern_refused():
    with pytest.raises(AcfInputError, match="backslash"):
        path_matches("admin/js/a.js", "admin\\js\\**")


def test_leading_slash_pattern_refused(tmp_path):
    with pytest.raises(AcfInputError, match="leading /"):
        path_matches("src/a.py", "/src/**")
    with pytest.raises(AcfInputError, match="leading /"):
        RepoTree(tmp_path).files(["/src/**"], [])


def test_review_rel():
    assert REVIEW_REL.as_posix() == "config/architecture/review.yml"


def test_files_includes_excludes_and_stays_in_root(tmp_path):
    root = tmp_path / "root"
    for rel in ("a/x.py", "a/tests/y.py", "b/z.ts"):
        f = root / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("", encoding="utf-8")
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "o.py").write_text("", encoding="utf-8")
    try:
        (root / "link.py").symlink_to(outside / "o.py")
        (root / "linkdir").symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks unavailable")
    t = RepoTree(root)
    assert t.files(["**/*.py"], ["tests/"]) == [t.root / "a" / "x.py"]
    assert t.files(["**/*.py", "**/*.ts"], []) == [
        t.root / "a" / "tests" / "y.py", t.root / "a" / "x.py", t.root / "b" / "z.ts"]


@pytest.mark.parametrize("include,exclude", [(["a\\b"], []), (["**/*.py"], ["x\\y"]), (["*.zzz"], ["q\\"])])
def test_files_validates_every_pattern_up_front(tmp_path, include, exclude):
    with pytest.raises(AcfInputError, match="backslash"):
        RepoTree(tmp_path).files(include, exclude)   # empty tree, nothing evaluated


def test_files_unreadable_directory_fails_loud(tmp_path, monkeypatch):
    (tmp_path / "d").mkdir()
    real = os.walk

    def walk(top, onerror=None, followlinks=False):
        if onerror:
            onerror(PermissionError(13, "denied", str(tmp_path / "d")))
        return real(top, onerror=onerror, followlinks=followlinks)

    monkeypatch.setattr(os, "walk", walk)
    with pytest.raises(AcfInputError, match="cannot read directory"):
        RepoTree(tmp_path).files(["**"], [])
