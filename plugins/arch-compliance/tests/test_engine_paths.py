"""contains_backslash detects what posix_path normalizes."""
from __future__ import annotations

import pytest

from acf.engine import contains_backslash, posix_path


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
