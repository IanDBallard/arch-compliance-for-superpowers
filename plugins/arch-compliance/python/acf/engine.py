"""Shared exemption and path helpers for ACF detectors."""

from __future__ import annotations

import re
from pathlib import Path


def posix_path(path: str | Path) -> str:
    if isinstance(path, Path):
        return path.as_posix()
    return path.replace("\\", "/")


def line_exempted(line: str, tokens: frozenset[str] | set[str]) -> bool:
    """Return True if ``line`` has a valid exemption for any mandate token.

    Accepted forms (reason must be non-empty):
    - ``# <token>-ok: <reason>``
    - ``# arch-ok: <token> <reason>``
    """
    for token in tokens:
        escaped = re.escape(token)
        m1 = re.search(rf"#\s*{escaped}-ok\s*:\s*(\S.*)$", line)
        if m1 and m1.group(1).strip():
            return True
        m2 = re.search(rf"#\s*arch-ok\s*:\s*{escaped}\s+(\S.*)$", line)
        if m2 and m2.group(1).strip():
            return True
    return False


def is_in_scope(line: int, added_lines: frozenset[int] | None) -> bool:
    """Diff-scope: empty/None means whole file; else only listed lines."""
    if not added_lines:
        return True
    return line in added_lines
