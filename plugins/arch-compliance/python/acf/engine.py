"""Shared path/scope helpers for ACF detectors.

Inline exemptions live only in ``acf.enforcement`` (registry-driven).
"""

from __future__ import annotations

from pathlib import Path


def posix_path(path: str | Path) -> str:
    if isinstance(path, Path):
        return path.as_posix()
    return path.replace("\\", "/")


def contains_backslash(value: str) -> bool:
    """True if ``value`` carries a platform-native separator.

    The refusing counterpart to ``posix_path``: this detects, that normalizes.
    Persisted paths are refused rather than silently fixed, so a producer
    writing a Windows path learns about it.
    """
    return "\\" in value


def is_in_scope(line: int, added_lines: frozenset[int] | None) -> bool:
    """Diff-scope: empty/None means whole file; else only listed lines."""
    if not added_lines:
        return True
    return line in added_lines
