"""CLI: person-run approval of a repository's host detector rows.

Shows the rows and detector files being approved, then records a fingerprint-bound
approval in the per-user store. An agent may start it, and only the user's answer at a
Claude Code permission prompt approves; ``--fingerprint`` binds that answer to the
reviewed bytes.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from acf.approval import (
    SCOPE_TEXT,
    ApprovalState,
    _store_inside_repo,
    approval_rows,
    describe_approval,
    file_digests,
    fingerprint,
    read_store,
    reason,
    repo_key,
    store_path,
    write_approval,
)
from acf.detectors import load_gate_registry
from acf.exceptions import AcfInputError, GitError, UnknownDetectorError
from acf.registry import MandateRegistry
from acf.repo import MANDATES_REL, resolve_repo

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="acf-allow",
        description="Approve this repository's host detector rows and the files they name.",
    )
    parser.add_argument("--repo", type=Path, default=None, help="Repository root (default: cwd)")
    parser.add_argument(
        "--revoke",
        action="store_true",
        help="Remove this repository's approval instead of recording one",
    )
    parser.add_argument(
        "--fingerprint",
        metavar="HEX",
        default=None,
        help="Approve only if the current fingerprint equals HEX (see acf-approval-status)",
    )
    args = parser.parse_args(argv)

    if (
        os.environ.get("CLAUDE_CODE_CHILD_SESSION") == "1"
        and args.fingerprint is None
        and not args.revoke
    ):
        print(
            "acf: run from Claude Code, acf-allow needs --fingerprint: run "
            "acf-approval-status and pass the fingerprint it prints, or run acf-allow in a "
            "terminal outside Claude Code",
            file=sys.stderr,
        )
        return 1

    repo: Path = resolve_repo(args.repo)
    try:
        if args.revoke:
            return _revoke(repo)
        registry = load_gate_registry(repo, repo / MANDATES_REL)
        rows = approval_rows(registry)
        if not rows:
            print("No host detector rows are active; nothing to approve.")
            return 0
        store = store_path()
        if _store_inside_repo(repo, store):
            raise AcfInputError(reason(ApprovalState.STORE_IN_REPO, store))
        digests = file_digests(repo, rows)
        current = fingerprint(rows, digests)
        if args.fingerprint is not None and args.fingerprint != current:
            print(
                "acf: the host rows or detector files changed since the review "
                f"(reviewed {args.fingerprint}, now {current}); nothing approved",
                file=sys.stderr,
            )
            return 1
        for line in describe_approval(repo, rows, digests):
            print(line)
        write_approval(repo, registry, digests=digests)
        key = repo_key(repo)
        print(f"Approved {key.key} ({SCOPE_TEXT[key.scope]}) in {store.as_posix()}.")
    except (AcfInputError, GitError, UnknownDetectorError) as exc:
        print(f"acf: {exc}", file=sys.stderr)
        return 1
    return 0


def _revoke(repo: Path) -> int:
    store = store_path()
    key = repo_key(repo).key
    if key not in read_store(store).repos:
        print(f"No approval recorded for {key}; nothing to remove.")
        return 0
    # Revoking reads no rows; an empty registry keeps it independent of mandates.yml.
    write_approval(repo, MandateRegistry(mandates=[], source_path=""), revoke=True)
    print(f"Removed the approval for {key} from {store.as_posix()}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
