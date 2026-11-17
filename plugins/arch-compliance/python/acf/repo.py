"""Host repository layout: the one declaration of where ACF looks in a host.

It imports only the standard library and ``acf.exceptions`` (itself stdlib-only), on
purpose. Both hooks import this at module scope, before the
``.acf/enabled`` gate decides whether ACF is active at all, so this module must
never pull in a third-party package.
"""
from __future__ import annotations

import os
import re
from collections.abc import Sequence
from pathlib import Path

from acf.exceptions import AcfInputError

#: Host-relative directory holding the mandate registry and the doctrine document.
CONFIG_DIR = Path("config") / "architecture"

#: Host-relative path to the mandate registry.
MANDATES_REL = CONFIG_DIR / "mandates.yml"

#: Host-relative path to the host's architecture doctrine document.
ARCH_REL = CONFIG_DIR / "ARCHITECTURE.md"

#: Host-relative path to the adversarial-design-review gate's declaration.
ADR_REL = CONFIG_DIR / "adr.yml"

#: Host-relative default for the fail-loud ratchet baseline. A mandate may
#: override it via its ``params.baseline``; this is the value used when it does
#: not.
RATCHET_BASELINE_REL = CONFIG_DIR / "fail_loud_ratchet.json"

#: Host-relative path to the architecture review's declaration.
REVIEW_REL = CONFIG_DIR / "review.yml"

#: Host-relative marker that activates ACF in a host repository.
ENABLED_REL = Path(".acf") / "enabled"


def resolve_repo(explicit: Path | None, stdin_cwd: str | None = None) -> Path:
    """Resolve the host repository root.

    Precedence: an explicit ``--repo`` argument, then the invoking directory a
    harness supplies on stdin, then the process directory. The last branch is a
    genuine fallback, not a guarantee -- a caller that needs certainty must pass
    ``explicit``.
    """
    if explicit is not None:
        return explicit.resolve()
    if stdin_cwd:
        return Path(str(stdin_cwd)).resolve()
    return Path.cwd().resolve()


def _glob_regex(pattern: str) -> str:
    """Regex source for a glob: ``**/`` is zero or more directories, trailing ``/**`` everything below, ``*`` and ``?`` stay within a segment."""
    out: list[str] = []
    i = 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:[^/]+/)*")
            i += 3
        elif pattern.startswith("/**", i) and i + 3 == len(pattern):
            out.append("/.+")
            i += 3
        elif pattern[i] == "*":
            while i < len(pattern) and pattern[i] == "*":
                i += 1
            out.append("[^/]*")
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return "".join(out)


def _check_pattern(pattern: str) -> None:
    if "\\" in pattern:
        raise AcfInputError(f"glob pattern {pattern!r} contains a backslash; write host paths with '/'")
    if pattern.startswith("/"):
        raise AcfInputError(
            f"glob pattern {pattern!r} has a leading /; write it relative to the repository root"
        )


def path_matches(key: str, pattern: str) -> bool:
    """Whether the repository-relative POSIX ``key`` matches ``pattern``.

    ``dir/`` with one segment matches any directory of that name at any depth;
    with several segments it matches that directory from the root and
    everything below it. A pattern with no ``/`` matches a basename at any
    depth. Any other pattern matches the whole key.
    """
    _check_pattern(pattern)
    if pattern.endswith("/"):
        body = pattern[:-1]
        if "/" not in body:
            segment = re.compile(_glob_regex(body))
            return any(segment.fullmatch(part) for part in key.split("/")[:-1])
        return re.match(_glob_regex(body) + "/", key) is not None
    if "/" not in pattern:
        return re.fullmatch(_glob_regex(pattern), key.rsplit("/", 1)[-1]) is not None
    return re.fullmatch(_glob_regex(pattern), key) is not None


class RepoTree:
    """The one place a path string becomes a location in the host repository."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def contained(self, path: str) -> Path | None:
        """``path`` resolved against the root (an absolute ``path`` is taken as is); None when it leaves the root or cannot be resolved."""
        try:
            candidate = (self.root / path).resolve()
        except (RuntimeError, ValueError):  # symlink loop on Python 3.11 and 3.12; embedded NUL
            return None
        return candidate if candidate.is_relative_to(self.root) else None

    def file(self, path: str) -> Path | None:
        """The existing regular file ``path`` names inside the root, else None. An OSError from stat propagates."""
        candidate = self.contained(path)
        return candidate if candidate is not None and candidate.is_file() else None

    def directory(self, path: str) -> Path | None:
        """The existing directory ``path`` names inside the root, else None. An OSError from stat propagates."""
        candidate = self.contained(path)
        return candidate if candidate is not None and candidate.is_dir() else None

    def key(self, location: Path) -> str:
        """The repository-relative POSIX key of a location this tree returned, or of a path walked beneath one."""
        return location.relative_to(self.root).as_posix()

    def files(self, include: Sequence[str], exclude: Sequence[str]) -> list[Path]:
        """Regular files under the root matching any ``include`` and no ``exclude``, sorted by key.

        An unreadable directory raises AcfInputError. Symlinked directories are not descended into; a symlinked file that resolves outside the root is skipped.
        """
        for pattern in (*include, *exclude):
            _check_pattern(pattern)

        def refuse(error: OSError) -> None:
            raise AcfInputError(f"cannot read directory {error.filename!r} under the repository root: {error}") from error

        found: dict[str, Path] = {}
        for directory, _dirs, names in os.walk(self.root, onerror=refuse, followlinks=False):
            for name in names:
                location = Path(directory) / name
                key = self.key(location)
                if not any(path_matches(key, p) for p in include) or any(path_matches(key, p) for p in exclude):
                    continue
                if self.contained(key) is None or not location.is_file():
                    continue
                found[key] = location
        return [found[k] for k in sorted(found)]
