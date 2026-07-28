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

from acf.engine import posix_path
from acf.exceptions import DetectorPackError
from acf.finding import Finding, Severity

FAIL_LOUD_RATCHET_DETECTOR_ID = "fail_loud_ratchet"


def count_bare_excepts(text: str) -> int:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return 0
    count = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue
        if node.type is None:
            count += 1
        elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
            count += 1
    return count


def scan_tree(
    repo_root: Path,
    *,
    roots: list[str] | None = None,
    exclude_globs: list[str] | None = None,
) -> dict[str, int]:
    """Return POSIX-relative path → bare/broad-except count (counts ≥ 1 only)."""
    root = repo_root.resolve()
    search_roots = [root / r for r in (roots or ["."])]
    excludes = exclude_globs or [
        "**/tests/**",
        "**/test_*.py",
        "**/*_test.py",
        "**/.venv/**",
        "**/node_modules/**",
    ]
    counts: dict[str, int] = {}
    for search in search_roots:
        if not search.exists():
            continue
        for path in search.rglob("*.py"):
            try:
                rel = path.relative_to(root).as_posix()
            except ValueError:
                continue
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
    if not path.is_file():
        raise DetectorPackError(
            f"fail_loud_ratchet: baseline not found: {path.as_posix()}"
        )
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
    baseline_file = Path(baseline_path)
    if not baseline_file.is_absolute():
        baseline_file = repo_root / baseline_file
    baseline = load_baseline(baseline_file)
    current = scan_tree(repo_root, roots=roots, exclude_globs=exclude_globs)
    growth = compare_to_baseline(current, baseline)
    findings: list[Finding] = []
    for path, (old, new) in sorted(growth.items()):
        findings.append(
            Finding(
                mandate_id="fail-loud.ratchet",
                severity=Severity.BLOCK,
                path=path,
                line=1,
                message=(
                    f"Fail-loud ratchet growth: bare/broad-except count "
                    f"{old} → {new} (baseline {baseline_file.as_posix()})"
                ),
                detector=FAIL_LOUD_RATCHET_DETECTOR_ID,
                detection="guard",
            )
        )
    return findings
