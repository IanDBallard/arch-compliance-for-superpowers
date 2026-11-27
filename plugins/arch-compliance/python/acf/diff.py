"""Git diff helpers for diff-scoped architecture checks."""

from __future__ import annotations

import os
import re
import subprocess
from collections.abc import Mapping
from pathlib import Path
from typing import Literal

from acf.exceptions import GitError

DiffMode = Literal["staged", "worktree"]

_HUNK_RE = re.compile(r"^@@\s+-\d+(?:,\d+)?\s+\+(\d+)(?:,(\d+))?\s+@@")


def run_git(
    repo: Path, *args: str, env: Mapping[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    """Invoke git and return the completed process, non-zero status included.

    The one place that knows how to invoke git. Callers that treat a non-zero
    status as a failure should use ``_git``; callers that need the status as
    data (an exit code that MEANS something, such as ``check-ignore``) use this.
    Raises ``GitError`` when stdout is not UTF-8, whatever the exit status.
    """
    proc = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        check=False,
        env=env,
    )
    try:
        stdout = proc.stdout.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise GitError(
            f"git {' '.join(args)}: output is not UTF-8 at byte {exc.start}"
        ) from exc
    stderr = proc.stderr.decode("utf-8", errors="replace")
    return subprocess.CompletedProcess(proc.args, proc.returncode, stdout, stderr)


def git_common_dir(repo: Path) -> tuple[Path, str] | None:
    """Return ``(common git dir, prefix of repo inside the work tree)``.

    The common dir is identical for a main checkout and each linked worktree.
    Returns ``None`` only when ``repo`` is not inside a git repository (exit 128
    with ``not a git repository``); every other failure raises ``GitError``.
    Git's repository-locating variables are removed from the environment so a
    hook's inherited ``GIT_DIR`` cannot change the prefix.
    """

    def fail(detail: str) -> GitError:
        return GitError(
            f"cannot compute the approval key for {repo.as_posix()}: "
            f"git rev-parse failed: {detail}"
        )

    try:
        names = run_git(repo, "rev-parse", "--local-env-vars")
        if names.returncode != 0:
            raise fail((names.stderr or "").strip() or str(names.returncode))
        drop = set(names.stdout.split())
        env = {k: v for k, v in os.environ.items() if k not in drop}
        env["LC_ALL"] = "C"
        proc = run_git(
            repo,
            "rev-parse", "--path-format=absolute", "--git-common-dir", "--show-prefix",
            env=env,
        )
    except OSError as exc:
        raise fail(str(exc)) from exc
    if proc.returncode == 0:
        lines = proc.stdout.splitlines()
        if len(lines) == 2:
            return Path(lines[0]), lines[1].rstrip("/")
        raise fail(f"unexpected output {proc.stdout!r}")
    if proc.returncode == 128 and "not a git repository" in proc.stderr:
        return None
    raise fail((proc.stderr or "").strip() or str(proc.returncode))


def _git(repo: Path, *args: str) -> str:
    """Run git and return stdout, raising ``GitError`` on a non-zero status."""
    proc = run_git(repo, *args)
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        raise GitError(f"git {' '.join(args)} failed: {err or proc.returncode}")
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
