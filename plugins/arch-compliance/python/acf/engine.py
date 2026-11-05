"""Shared path/scope helpers for ACF detectors.

Inline exemptions live only in ``acf.enforcement`` (registry-driven).
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

_ABSOLUTE_RE = re.compile(r"^([A-Za-z]:|/|\\\\)")


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


def looks_absolute(path: str) -> bool:
    """True for a drive-prefixed (``C:`` or ``C:/``), root-anchored or UNC path."""
    return bool(_ABSOLUTE_RE.match(path))


def validate_posix_rel_path(value: str) -> str:
    """Refuse anything but a normalized, relative POSIX path."""
    if not value or value != value.strip():
        raise ValueError(f"path must be a non-empty relative POSIX path: {value!r}")
    if contains_backslash(value):
        raise ValueError(f"path must be POSIX (no backslashes): {value!r}")
    if looks_absolute(value) or value.endswith("/"):
        raise ValueError(f"path must be relative with no trailing '/': {value!r}")
    if any(part in ("", ".", "..") for part in value.split("/")):
        raise ValueError(f"path must not contain empty, '.' or '..' segments: {value!r}")
    return value


def validate_hit_fields(line: object, message: object) -> tuple[int, str]:
    """Refuse a detector hit's line and message unless exactly an int >= 1 and a non-empty str."""
    if type(line) is not int or line < 1:
        raise ValueError(f"hit line must be an int >= 1: {line!r}")
    if type(message) is not str or not message:
        raise ValueError(f"hit message must be a non-empty str: {message!r}")
    return line, message


def parse_python(text: str) -> ast.Module | None:
    """Parse Python source; None when it does not parse (the scanners' skip convention)."""
    try:
        return ast.parse(text)
    except SyntaxError:
        return None


def is_in_scope(line: int, added_lines: frozenset[int] | None) -> bool:
    """Diff-scope: empty/None means whole file; else only listed lines."""
    if not added_lines:
        return True
    return line in added_lines
