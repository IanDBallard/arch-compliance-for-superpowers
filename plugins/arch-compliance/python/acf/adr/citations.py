"""Classify the paths a spec cites, so reviewers know what they are being handed.

Step 2 of the gate exists because a reviewer given a path that does not exist
returns UNPROVEN for a file it merely failed to find — and UNPROVEN on a
load-bearing claim blocks (Amendment 1). The original rule stated that as *every
cited path must exist in the working tree*, which is not the same requirement and
is false of specs that are doing their job:

``historical``
    "commit ``4594501a`` touches only ``scripts/ai/file_tracker.py``" is a true
    statement about the past. That file was deleted in ``41cbe8e9``. The blanket
    existence check hard-failed a correct citation (2026-08-11, ordering v7).
``proposed``
    The command the spec exists to introduce has no file yet, by definition.
``external``
    Live book roots and gitignored build artifacts are outside the tree on
    purpose.

Each kind uses a signal that already exists — the filesystem, ``git check-ignore``,
``git rev-list`` — rather than asking spec authors to adopt a marking convention.
Only ``unresolved`` is an error, and it is the one the controller hard-fails on.

There is no shared git-invocation helper in this repo (``git_safety``,
``freshness`` and the CI guards each run the specific command they need), so this
module does the same rather than inventing a general runner no caller asked for.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Iterable, Literal

from acf.exceptions import CitationHistoryUnavailableError

CitationKind = Literal[
    "current", "historical", "external", "proposed", "asserted_absent", "unresolved"
]

#: Trailing ``:12`` / ``:12-34`` / ``:12,34`` line references on a cited path.
_LINE_SUFFIX_RE = re.compile(r":[\d,\-–\s]+$")


def _bare_path(citation: str) -> str:
    """Strip a trailing line reference from ``citation``."""
    return _LINE_SUFFIX_RE.sub("", citation.strip()).strip()


def _looks_absolute(path: str) -> bool:
    """True for a drive-letter or root-anchored path — necessarily outside the tree."""
    return bool(re.match(r"^([A-Za-z]:[\\/]|/|\\\\)", path))


def _git(
    args: list[str], repo_root: Path, *, answers: tuple[int, ...] = (0,)
) -> subprocess.CompletedProcess[str]:
    """Run git; any exit code outside ``answers`` means git could not answer.

    That is raised, never read as a negative answer: a failing ``ls-files`` is
    not "nothing is tracked", and a fatal ``check-ignore`` is not "not ignored".
    """
    result = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        capture_output=True, text=True, check=False,
    )
    if result.returncode not in answers:
        raise CitationHistoryUnavailableError(
            f"git {' '.join(args)} failed in {repo_root.as_posix()} "
            f"(exit {result.returncode}): {result.stderr.strip()}"
        )
    return result


def _escapes_repo(path: str, repo_root: Path) -> bool:
    root = repo_root.resolve()
    return not (root / path).resolve().is_relative_to(root)


def _is_ignored(path: str, repo_root: Path) -> bool:
    # check-ignore: 0 = ignored, 1 = not ignored; anything else is a failure.
    return _git(["check-ignore", "-q", path], repo_root, answers=(0, 1)).returncode == 0


def _require_full_history(repo_root: Path) -> None:
    """A shallow clone cannot say whether a path was ever committed."""
    shallow = _git(["rev-parse", "--is-shallow-repository"], repo_root).stdout.strip()
    if shallow == "true":
        raise CitationHistoryUnavailableError(
            f"{repo_root.as_posix()} is a shallow clone: the commits that would show "
            "whether a cited path ever existed are not in it, so a historical "
            "citation cannot be told from an unresolved one. Run "
            "`git fetch --unshallow` and re-run the gate."
        )


def _existed_ever(path: str, repo_root: Path) -> bool:
    _require_full_history(repo_root)
    result = _git(["rev-list", "-n", "1", "--all", "--", path], repo_root)
    return bool(result.stdout.strip())


def _tracked_files(repo_root: Path) -> list[str]:
    return _git(["ls-files"], repo_root).stdout.split()


def _resolve_by_suffix(path: str, repo_root: Path) -> str | None:
    """Return the tracked file ``path`` is a suffix of, or None.

    Specs name a file in full once and then use its basename as prose shorthand
    ("the sanitizer at ``collection.py:262``"). Treating that as unresolved
    called 52 of the ordering spec's 97 citations broken; every one of them was
    shorthand for a file plainly in the tree.

    A **suffix** match, deliberately — not a fuzzy or basename-anywhere one. It
    is deterministic and it does not rescue a wrong path: Amendment 1's original
    incident, ``scripts/api/routes/content.py`` against a tree whose routes live
    at ``scripts/cms_server/routes/``, is not a suffix of anything tracked and
    still fails. Shortest match wins when several qualify, so a basename
    resolves to the file that bears it rather than to some longer coincidence.
    """
    needle = path.lstrip("./")
    matches = [
        tracked for tracked in _tracked_files(repo_root)
        if tracked == needle or tracked.endswith("/" + needle)
    ]
    return min(matches, key=len) if matches else None


def resolve_citation(
    citation: str,
    *,
    repo_root: Path,
    proposed: frozenset[str] = frozenset(),
    asserted_absent: frozenset[str] = frozenset(),
) -> tuple[CitationKind, str | None]:
    """Return ``(kind, resolved_path)`` for ``citation``.

    ``resolved_path`` is the repo-relative path a reviewer should open, with any
    shorthand expanded — the controller hands that over rather than making four
    reviewers repeat the lookup, or guess.

    ``proposed`` is checked first: a spec declaring it will create a path means
    the new file, whatever the archaeology says about that name. Everything else
    is decided by evidence, cheapest signal first.
    """
    path = _bare_path(citation)
    if path in proposed or citation.strip() in proposed:
        return "proposed", path
    if path in asserted_absent or citation.strip() in asserted_absent:
        # The spec cites this precisely BECAUSE it does not exist — "the diff
        # baseline exists in no book root" is the finding, not a broken
        # reference. Declared by the controller off the spec, like `proposed`,
        # rather than guessed: absence is only meaningful when it is claimed.
        return "asserted_absent", None
    # Absoluteness is decided BEFORE existence: an absolute path is outside the
    # working tree whether or not it happens to be mounted right now. Testing
    # existence first made the verdict depend on the environment — a live book
    # root classified `current` while its Drive was mounted and `external` when
    # it dropped, which is both wrong and non-reproducible. (The mount really
    # did come and go twice on 2026-08-11.)
    if _looks_absolute(path):
        return "external", path
    if _escapes_repo(path, repo_root):
        # A relative path that climbs out of the tree names nothing the repo
        # can vouch for; git would answer it with a fatal "outside repository"
        # (exit 128), which is not a git-history failure. Unresolved, as before.
        return "unresolved", None
    if (repo_root / path).exists():
        return "current", path
    # Suffix resolution runs BEFORE the ignore test: a tracked file is by
    # definition not ignored, and `git check-ignore` answers about the *string*
    # it is handed, not about the file the citation means. `.gitignore` carries
    # `check_*.py` for stray root-level scripts, so the bare shorthand
    # `check_book_tier_drift.py` matched it while
    # scripts/maintenance/check_book_tier_drift.py sat tracked in the tree —
    # and the reviewer was told "external: outside the repo, unavailable to
    # you" about a file it needed to open (found running the gate, 2026-08-11).
    suffix_match = _resolve_by_suffix(path, repo_root)
    if suffix_match is not None:
        return "current", suffix_match
    if _is_ignored(path, repo_root):
        return "external", path
    if _existed_ever(path, repo_root):
        return "historical", path
    return "unresolved", None


def classify_citation(
    citation: str,
    *,
    repo_root: Path,
    proposed: frozenset[str] = frozenset(),
    asserted_absent: frozenset[str] = frozenset(),
) -> CitationKind:
    """Return the kind of path ``citation`` denotes. See :func:`resolve_citation`."""
    kind, _ = resolve_citation(citation, repo_root=repo_root, proposed=proposed,
                               asserted_absent=asserted_absent)
    return kind


def classify_citations(
    citations: Iterable[str],
    *,
    repo_root: Path,
    proposed: frozenset[str] = frozenset(),
    asserted_absent: frozenset[str] = frozenset(),
) -> dict[str, CitationKind]:
    """Map every citation to its kind, preserving the caller's original strings."""
    return {
        citation: classify_citation(citation, repo_root=repo_root, proposed=proposed,
                                    asserted_absent=asserted_absent)
        for citation in citations
    }


def count_cited_files(citations: Iterable[str]) -> int:
    """Return the ledger's ``cited_files`` predictor: unique paths, any kind.

    Counting is this function's job rather than the controller's judgement,
    because the predictor drifted between runs of the same spec — 85 on one
    (a regex over backticked tokens, counting bare basenames and repeats), 38 on
    the next (unique resolvable repo files), for a spec that had grown. Both were
    defensible readings; neither was the same metric, which silently broke the
    comparability the ledger exists to provide.

    Line references are stripped, so ``x.py:10`` and ``x.py:20`` are one file.
    Every kind counts — ``historical``, ``proposed`` and ``external`` paths were
    genuinely handed to reviewers, and excluding them would undercount the
    spec's evidential reach.
    """
    return len({_bare_path(citation) for citation in citations if _bare_path(citation)})


def unresolved_citations(
    citations: Iterable[str],
    *,
    repo_root: Path,
    proposed: frozenset[str] = frozenset(),
    asserted_absent: frozenset[str] = frozenset(),
) -> list[str]:
    """Return only the citations the gate must hard-fail on.

    ``historical``, ``proposed`` and ``external`` are **not** errors — they are
    passed to reviewers with their kind attached so no reviewer wastes a verdict
    hunting a file that was never supposed to be there.
    """
    kinds = classify_citations(citations, repo_root=repo_root, proposed=proposed,
                               asserted_absent=asserted_absent)
    return [citation for citation, kind in kinds.items() if kind == "unresolved"]
