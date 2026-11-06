"""Fail-loud count ratchet — freeze legacy bare/broad-except stock.

Diff gates block *new* violations on added lines; this ratchet freezes the
legacy whole-tree count so debt cannot grow silently.
"""

from __future__ import annotations

import ast
import fnmatch
import json
from pathlib import Path
from typing import Any

from acf.detectors.python_pack import is_bare_or_exception
from acf.engine import parse_python, posix_path
from acf.exceptions import DetectorPackError
from acf.finding import Finding, Severity
from acf.repo import RepoTree

FAIL_LOUD_RATCHET_DETECTOR_ID = "fail_loud_ratchet"
FAIL_LOUD_RATCHET_MANDATE_ID = "fail-loud.ratchet"


def count_bare_excepts(text: str) -> int:
    tree = parse_python(text)
    if tree is None:
        return 0
    return sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, ast.ExceptHandler) and is_bare_or_exception(node)
    )


def scan_tree(
    repo_root: Path,
    *,
    roots: list[str] | None = None,
    exclude_globs: list[str] | None = None,
) -> dict[str, int]:
    """Return POSIX-relative path → bare/broad-except count (counts ≥ 1 only)."""
    tree = RepoTree(repo_root)
    search_roots: list[Path] = []
    for r in roots or ["."]:
        try:
            located = tree.directory(r)
        except OSError as exc:
            raise DetectorPackError(
                f"fail_loud_ratchet: roots entry {r!r} cannot be checked: {exc}"
            ) from exc
        if located is None:
            raise DetectorPackError(
                f"fail_loud_ratchet: roots entry {r!r} is not a directory inside the repository"
            )
        search_roots.append(located)
    excludes = exclude_globs or [
        "**/tests/**",
        "**/test_*.py",
        "**/*_test.py",
        "**/.venv/**",
        "**/node_modules/**",
    ]
    counts: dict[str, int] = {}
    for search in search_roots:
        for path in search.rglob("*.py"):
            rel = tree.key(path)
            if any(fnmatch.fnmatch(rel, g) for g in excludes):
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except OSError as exc:
                raise DetectorPackError(
                    f"fail_loud_ratchet: unreadable {rel}: {exc}"
                ) from exc
            n = count_bare_excepts(text)
            if n:
                counts[rel] = n
    return counts


def load_baseline(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DetectorPackError(
            f"fail_loud_ratchet: invalid JSON baseline {path.as_posix()}: {exc}"
        ) from exc
    if not isinstance(data, dict) or "files" not in data:
        raise DetectorPackError(
            f"fail_loud_ratchet: baseline must be an object with a 'files' map: "
            f"{path.as_posix()}"
        )
    files = data["files"]
    if not isinstance(files, dict):
        raise DetectorPackError(
            f"fail_loud_ratchet: baseline 'files' must be an object: {path.as_posix()}"
        )
    return data


def compare_to_baseline(
    current: dict[str, int],
    baseline: dict[str, Any],
) -> dict[str, tuple[int, int]]:
    """Return path → (baseline_count, current_count) for growth only."""
    prior = {posix_path(k): int(v) for k, v in baseline.get("files", {}).items()}
    growth: dict[str, tuple[int, int]] = {}
    for path, count in current.items():
        old = prior.get(path, 0)
        if count > old:
            growth[path] = (old, count)
    return growth


def scan_ratchet(
    repo_root: Path,
    *,
    baseline_path: str | Path,
    roots: list[str] | None = None,
    exclude_globs: list[str] | None = None,
) -> list[Finding]:
    tree = RepoTree(repo_root)
    try:
        baseline_file = tree.file(str(baseline_path))
    except OSError as exc:
        raise DetectorPackError(
            f"fail_loud_ratchet: baseline {str(baseline_path)!r} cannot be checked: {exc}"
        ) from exc
    if baseline_file is None:
        raise DetectorPackError(
            f"fail_loud_ratchet: baseline {str(baseline_path)!r} is not a file inside the repository"
        )
    baseline = load_baseline(baseline_file)
    current = scan_tree(repo_root, roots=roots, exclude_globs=exclude_globs)
    growth = compare_to_baseline(current, baseline)
    findings: list[Finding] = []
    for path, (old, new) in sorted(growth.items()):
        findings.append(
            Finding(
                mandate_id=FAIL_LOUD_RATCHET_MANDATE_ID,
                severity=Severity.BLOCK,
                path=path,
                line=1,
                message=(
                    f"Fail-loud ratchet growth: bare/broad-except count "
                    f"{old} → {new} (baseline {tree.key(baseline_file)})"
                ),
                detector=FAIL_LOUD_RATCHET_DETECTOR_ID,
                detection="guard",
            )
        )
    return findings
