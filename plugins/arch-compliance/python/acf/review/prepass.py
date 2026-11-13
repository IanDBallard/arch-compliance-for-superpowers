"""The target tree, each row's surface, and the hint pre-pass that feeds the auditors."""
from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from acf.exceptions import AcfInputError, EmptyTargetTreeError
from acf.repo import RepoTree, path_matches
from acf.review.host import ReviewHostConfig
from acf.review.packs import TechPack, hint_files, packs_for_row
from acf.review.rules import ReviewRow

BUILTIN_EXCLUDES: tuple[str, ...] = (
    ".git/",
    ".venv/",
    "__pycache__/",
    "node_modules/",
    ".worktrees/",
    "worktrees/",
    "dist/",
    "build/",
    ".mypy_cache/",
    ".pytest_cache/",
    ".ruff_cache/",
)
TEST_PATHS: tuple[str, ...] = (
    "tests/",
    "test_*.py",
    "*_test.py",
    "**/*.test.*",
    "**/*.spec.*",
)
_SNIPPET_MAX = 200


def _excludes(cfg: ReviewHostConfig, include_tests: bool, *extra: str) -> list[str]:
    tests = [] if include_tests else list(TEST_PATHS)
    return [*extra, *BUILTIN_EXCLUDES, *cfg.exclude, *tests]


def target_tree(
    tree: RepoTree,
    cfg: ReviewHostConfig,
    packs: dict[str, TechPack],
    *,
    paths: Sequence[str] | None,
    include_tests: bool,
) -> list[str]:
    if paths:
        include = list(paths)
    else:
        include = [glob for pack in packs.values() for glob in pack.files]
    keys = sorted(tree.key(p) for p in tree.files(include, _excludes(cfg, include_tests)))
    if not keys:
        raise EmptyTargetTreeError(
            f"the target tree is empty: no file matches {include} outside the exclusions"
        )
    return keys


def row_surface(
    tree: RepoTree,
    cfg: ReviewHostConfig,
    packs: dict[str, TechPack],
    row: ReviewRow,
    target: list[str],
    *,
    include_tests: bool,
) -> list[str]:
    settings = row.settings
    declared = settings.surface if settings is not None else None
    surface_exclude = settings.surface_exclude if settings is not None else []
    if declared is not None:
        files = tree.files(declared, _excludes(cfg, include_tests, *surface_exclude))
        keys = sorted(tree.key(p) for p in files)
        if not keys:
            raise AcfInputError(
                f"mandate {row.mandate.id!r}: surface {declared} matches no file"
            )
        return keys
    globs = [g for pack in packs_for_row(row.mandate, packs) for g in pack.files]
    return [
        key
        for key in target
        if any(path_matches(key, g) for g in globs)
        and not any(path_matches(key, e) for e in surface_exclude)
    ]


@dataclass(frozen=True)
class Candidate:
    path: str
    line: int
    tell: str
    snippet: str


def scan(
    tree: RepoTree, row: ReviewRow, surface: list[str], packs: dict[str, TechPack]
) -> list[Candidate]:
    candidates: list[Candidate] = []
    cache: dict[str, list[str]] = {}

    def lines_of(key: str) -> list[str]:
        if key not in cache:
            location = tree.file(key)
            if location is None:
                raise AcfInputError(f"{key}: not a file inside the repository")
            try:
                cache[key] = location.read_text(encoding="utf-8").splitlines()
            except UnicodeDecodeError as exc:
                raise AcfInputError(f"{key}: not UTF-8 ({exc})") from exc
        return cache[key]

    for pack in packs_for_row(row.mandate, packs):
        hints = pack.hints.get(row.mandate.auditor or "", [])
        if not hints:
            continue
        globs = hint_files(pack, packs)
        keys = [k for k in surface if any(path_matches(k, g) for g in globs)]
        compiled = [(re.compile(h.pattern), h.tell) for h in hints]
        for key in keys:
            for number, text in enumerate(lines_of(key), start=1):
                for regex, tell in compiled:
                    if regex.search(text):
                        snippet = text.strip()[:_SNIPPET_MAX]
                        candidates.append(Candidate(key, number, tell, snippet))
    return sorted(candidates, key=lambda c: (c.path, c.line, c.tell))


def render_candidates(cands: list[Candidate]) -> str:
    return "\n".join(f"{c.path}:{c.line} [{c.tell}] {c.snippet}" for c in cands)
