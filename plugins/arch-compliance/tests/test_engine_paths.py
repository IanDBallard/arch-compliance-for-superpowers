"""contains_backslash detects what posix_path normalizes."""
from __future__ import annotations

import ast

import pytest

from acf.engine import (
    contains_backslash,
    looks_absolute,
    parse_python,
    posix_path,
    validate_hit_fields,
    validate_posix_rel_path,
)


@pytest.mark.parametrize(
    "value,expected",
    [
        ("scripts/core/x.py", False),
        ("", False),
        ("scripts\\core\\x.py", True),
        ("C:\\Users\\x", True),
        ("a/b\\c", True),
    ],
)
def test_contains_backslash(value: str, expected: bool) -> None:
    assert contains_backslash(value) is expected


def test_predicate_and_normalizer_agree() -> None:
    """Anything the predicate flags, the normalizer changes - and vice versa."""
    for value in ("a/b", "a\\b", "", "a\\b/c"):
        assert contains_backslash(value) == (posix_path(value) != value)


@pytest.mark.parametrize("ok", ["scripts/ci/guard.py", "a/b/c.py", "guard.py"])
def test_validate_posix_rel_path_accepts(ok: str) -> None:
    assert validate_posix_rel_path(ok) == ok


@pytest.mark.parametrize(
    "bad",
    ["", " a.py", "a\\b.py", "/a.py", "a/", "C:/a.py", "C:a.py",
     "a//b.py", "./a.py", "a/./b.py", "../a.py", "a/../b.py"],
)
def test_validate_posix_rel_path_refuses(bad: str) -> None:
    with pytest.raises(ValueError):
        validate_posix_rel_path(bad)


def test_looks_absolute() -> None:
    assert looks_absolute("C:a") and looks_absolute("/x") and looks_absolute("\\\\srv\\s")
    assert not looks_absolute("a/b.py")


def test_validate_hit_fields() -> None:
    assert validate_hit_fields(1, "m") == (1, "m")
    for line, msg in [("5", "m"), (True, "m"), (0, "m"), (1, ""), (1, b"m")]:
        with pytest.raises(ValueError):
            validate_hit_fields(line, msg)


def test_parse_python() -> None:
    assert isinstance(parse_python("x = 1"), ast.Module)
    assert parse_python("def (") is None
