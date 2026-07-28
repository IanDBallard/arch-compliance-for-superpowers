"""Shared path/scope helpers for ACF detectors.

Inline exemptions live only in ``acf.enforcement`` (registry-driven).
"""

from __future__ import annotations

from pathlib import Path


def posix_path(path: str | Path) -> str:
    if isinstance(path, Path):
        return path.as_posix()
    return path.replace("\\", "/")


def is_in_scope(line: int, added_lines: frozenset[int] | None) -> bool:
    """Diff-scope: empty/None means whole file; else only listed lines."""
    if not added_lines:
        return True
    return line in added_lines
