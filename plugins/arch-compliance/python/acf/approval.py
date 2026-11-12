"""Per-user, fingerprint-bound approval of a repository's host detector rows.

The store lives at ``~/.acf/approvals.json``, outside every repository, keyed by the
repository's resolved root. One fingerprint covers every active host row and the
files those rows name, so the hook, the diff gate and ``acf-allow`` agree.

``write_approval`` sits beside ``save_baseline`` (``acf/baseline.py``), which writes an
in-repository artifact in place and raises ``BaselineError``. The approval store is a
per-user file read and rewritten by concurrent processes, so it is replaced whole
(temporary file, then ``os.replace``) and no helper is shared with ``save_baseline``.
"""
from __future__ import annotations

import enum
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from acf.exceptions import AcfInputError
from acf.loader import load_model_file
from acf.registry import (
    TIER1_CALL_SITES,
    Mandate,
    MandateRegistry,
    parse_host_detector_ref,
)
from acf.repo import RepoTree

#: Relative to ``Path.home()``.
STORE_REL = Path(".acf") / "approvals.json"


class ApprovalEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    fingerprint: str
    approved: str


class ApprovalStore(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: Literal[1] = 1
    repos: dict[str, ApprovalEntry] = Field(default_factory=dict)


class ApprovalState(enum.Enum):
    NOT_NEEDED = "not_needed"
    APPROVED = "approved"
    MISSING = "missing"
    STALE = "stale"
    STORE_IN_REPO = "store_in_repo"


@dataclass(frozen=True)
class Approval:
    state: ApprovalState
    digests: dict[str, str] = field(default_factory=dict)


def store_path() -> Path:
    try:
        return Path.home() / STORE_REL
    except RuntimeError as exc:
        raise AcfInputError(f"cannot locate the approval store: {exc}") from exc


def read_store(path: Path) -> ApprovalStore:
    if not path.is_file():
        return ApprovalStore()
    return load_model_file(path, ApprovalStore, subject="approval store", fmt="json")


def approval_rows(registry: MandateRegistry) -> list[Mandate]:
    return sorted(registry.host_rows(TIER1_CALL_SITES), key=lambda m: m.id)


def file_digests(repo: Path, rows: list[Mandate]) -> dict[str, str]:
    tree = RepoTree(repo)
    digests: dict[str, str] = {}
    for row in rows:
        rel_path, _ = parse_host_detector_ref(row.detector)
        if rel_path in digests:
            continue
        try:
            located = tree.file(rel_path)
            if located is None:
                raise AcfInputError(
                    f"host detector file not found: {rel_path!r} under {tree.root.as_posix()}"
                )
            digests[rel_path] = hashlib.sha256(located.read_bytes()).hexdigest()
        except OSError as exc:
            raise AcfInputError(f"cannot read host detector file {rel_path!r}: {exc}") from exc
    return digests


def fingerprint(rows: list[Mandate], digests: dict[str, str]) -> str:
    text = json.dumps(
        {"rows": [m.model_dump(mode="json") for m in rows], "files": digests},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def reason(state: ApprovalState, store: Path) -> str:
    if state is ApprovalState.MISSING:
        return "no approval for this repository"
    if state is ApprovalState.STALE:
        return "the host rows or detector files changed since approval"
    if state is ApprovalState.STORE_IN_REPO:
        return f"the approval store {store.as_posix()} is inside the repository"
    raise ValueError(f"no reason text for approval state {state.name}")


def _store_inside_repo(repo: Path, store: Path) -> bool:
    return RepoTree(repo).contained(str(store)) is not None


def check_approval(
    repo: Path, registry: MandateRegistry, call_sites: frozenset[str]
) -> Approval:
    if not registry.host_rows(call_sites):
        return Approval(ApprovalState.NOT_NEEDED, {})
    store = store_path()
    if _store_inside_repo(repo, store):
        return Approval(ApprovalState.STORE_IN_REPO, {})
    rows = approval_rows(registry)
    digests = file_digests(repo, rows)
    entry = read_store(store).repos.get(RepoTree(repo).root.as_posix())
    if entry is None:
        return Approval(ApprovalState.MISSING, {})
    if entry.fingerprint != fingerprint(rows, digests):
        return Approval(ApprovalState.STALE, {})
    return Approval(ApprovalState.APPROVED, digests)


def require_approval(
    repo: Path, registry: MandateRegistry, call_sites: frozenset[str]
) -> Approval:
    result = check_approval(repo, registry, call_sites)
    if result.state in (ApprovalState.NOT_NEEDED, ApprovalState.APPROVED):
        return result
    ids = ", ".join(m.id for m in approval_rows(registry))
    raise AcfInputError(
        f"host detectors need approval: {reason(result.state, store_path())}; rows: {ids}. "
        "Ask the user to review the detector files and run acf-allow; a CI workflow, "
        "or a run with --mandates naming another file, passes --trusted-checkout."
    )


def write_approval(repo: Path, registry: MandateRegistry, *, revoke: bool = False) -> None:
    store = store_path()
    if _store_inside_repo(repo, store):
        raise AcfInputError(reason(ApprovalState.STORE_IN_REPO, store))
    key = RepoTree(repo).root.as_posix()
    data = read_store(store)
    if revoke:
        data.repos.pop(key, None)
    else:
        rows = approval_rows(registry)
        data.repos[key] = ApprovalEntry(
            fingerprint=fingerprint(rows, file_digests(repo, rows)),
            approved=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )
    tmp_name: str | None = None
    try:
        store.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            dir=store.parent, delete=False, suffix=".tmp", mode="w", encoding="utf-8"
        ) as handle:
            tmp_name = handle.name
            handle.write(data.model_dump_json(indent=2) + "\n")
        os.replace(tmp_name, store)
    except OSError as exc:
        if tmp_name is not None:
            try:
                os.unlink(tmp_name)
            except OSError:  # fail-loud.bare-except-ok: best-effort cleanup; the original error is raised below
                pass
        raise AcfInputError(f"cannot write approval store {store.as_posix()}: {exc}") from exc
