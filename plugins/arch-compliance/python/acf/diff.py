"""Git diff helpers for diff-scoped architecture checks."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Literal

DiffMode = Literal["staged", "worktree"]

_HUNK_RE = re.compile(r"^@@\s+-\d+(?:,\d+)?\s+\+(\d+)(?:,(\d+))?\s+@@")


def _git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {err or proc.returncode}")
    return proc.stdout


def _diff_args(mode: DiffMode, base: str | None) -> list[str]:
    if base is not None:
        # Three-dot: diff from merge-base(base, HEAD) to HEAD — the CI scope.
        return [f"{base}...HEAD"]
    if mode == "staged":
        return ["--cached"]
    return []


def changed_files(
    repo: Path, mode: DiffMode = "staged", base: str | None = None
) -> list[str]:
    """Return paths changed in the given scope (repo-relative, as git reports
    them). ``base`` overrides ``mode`` and diffs merge-base(base, HEAD)..HEAD."""
    out = _git(repo, "diff", *_diff_args(mode, base), "--name-only", "--diff-filter=ACMR")
    return [line.strip() for line in out.splitlines() if line.strip()]


def added_lines(
    repo: Path,
    path: str | Path,
    mode: DiffMode = "staged",
    base: str | None = None,
) -> set[int]:
    """Return 1-based line numbers added for ``path`` in the given scope."""
    rel = Path(path).as_posix()
    out = _git(repo, "diff", *_diff_args(mode, base), "-U0", "--", rel)
    return _parse_added_lines(out)


def _parse_added_lines(diff_text: str) -> set[int]:
    lines: set[int] = set()
    new_line: int | None = None
    for raw in diff_text.splitlines():
        if raw.startswith("@@"):
            m = _HUNK_RE.match(raw)
            if not m:
                new_line = None
                continue
            new_line = int(m.group(1))
            continue
        if new_line is None:
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            lines.add(new_line)
            new_line += 1
        elif raw.startswith("-") and not raw.startswith("---"):
            continue
        elif raw.startswith("\\"):
            continue
        else:
            # context line (rare with -U0) or other
            if raw.startswith(" ") or not raw.startswith(("+", "-", "@")):
                new_line += 1
    return lines
