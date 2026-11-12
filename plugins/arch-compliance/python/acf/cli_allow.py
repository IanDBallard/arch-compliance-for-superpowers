"""CLI: person-run approval of a repository's host detector rows.

Shows the rows and detector files being approved, then records a fingerprint-bound
approval in the per-user store. Run by the user, never by an agent.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from acf.approval import (
    ApprovalState,
    approval_rows,
    file_digests,
    read_store,
    reason,
    store_path,
    write_approval,
)
from acf.detectors import load_gate_registry
from acf.exceptions import AcfInputError, UnknownDetectorError
from acf.registry import MandateRegistry
from acf.repo import MANDATES_REL, RepoTree, resolve_repo

_HELPER_LIMIT = (
    "Note: imported modules are not covered; a change confined to a module a detector "
    "imports runs under this approval."
)


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
    args = parser.parse_args(argv)

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
        if RepoTree(repo).contained(str(store)) is not None:
            raise AcfInputError(reason(ApprovalState.STORE_IN_REPO, store))
        digests = file_digests(repo, rows)
        print("Approving these host detector rows:")
        for row in rows:
            print(f"  {row.id}  {row.detector}")
        print("and these detector files (SHA-256):")
        for rel_path, digest in digests.items():
            print(f"  {rel_path}  {digest}")
        print(_HELPER_LIMIT)
        write_approval(repo, registry, digests=digests)
        print(f"Approved {RepoTree(repo).root.as_posix()} in {store.as_posix()}.")
    except (AcfInputError, UnknownDetectorError) as exc:
        print(f"acf: {exc}", file=sys.stderr)
        return 1
    return 0


def _revoke(repo: Path) -> int:
    store = store_path()
    key = RepoTree(repo).root.as_posix()
    if key not in read_store(store).repos:
        print(f"No approval recorded for {key}; nothing to remove.")
        return 0
    # Revoking reads no rows; an empty registry keeps it independent of mandates.yml.
    write_approval(repo, MandateRegistry(mandates=[], source_path=""), revoke=True)
    print(f"Removed the approval for {key} from {store.as_posix()}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
