"""CLI: read-only review of a repository's host detector approval.

Prints the approval state, then the review ``acf-allow`` prints (key and scope, rows,
detector files with SHA-256, fingerprint, imported-helper limit). Writes nothing.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from acf.approval import approval_rows, check_approval, describe_approval, file_digests
from acf.detectors import load_gate_registry
from acf.exceptions import AcfInputError, GitError, UnknownDetectorError
from acf.registry import TIER1_CALL_SITES
from acf.repo import MANDATES_REL, resolve_repo


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="acf-approval-status",
        description="Print this repository's host detector approval state and review. Writes nothing.",
    )
    parser.add_argument("--repo", type=Path, default=None, help="Repository root (default: cwd)")
    args = parser.parse_args(argv)

    repo: Path = resolve_repo(args.repo)
    try:
        registry = load_gate_registry(repo, repo / MANDATES_REL)
        approval = check_approval(repo, registry, TIER1_CALL_SITES)
        print(f"state: {approval.state.name}")
        rows = approval_rows(registry)
        if not rows:
            print("There are no host detector rows to approve.")
            return 0
        digests = file_digests(repo, rows)
        for line in describe_approval(repo, rows, digests):
            print(line)
    except (AcfInputError, GitError, UnknownDetectorError) as exc:
        print(f"acf: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
