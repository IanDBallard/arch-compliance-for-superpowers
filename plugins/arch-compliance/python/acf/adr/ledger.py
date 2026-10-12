"""Append-only efficacy ledger for the adversarial design-review gate.

The gate ships mandatory-for-all on one datapoint. This ledger exists so the
decision to NARROW it later rests on observation rather than fatigue. It is a
measurement instrument, not a control: nothing in the pipeline reads it, and no
reviewer is aware of it.

Predictors are recorded BEFORE dispatch so they cannot be back-fitted to the
outcome. Rows are read by eye after ~10-15 runs — see the spec's "Reading the
ledger". The number that decides the gate's future is
``blocks_overturned / BLOCKED``, the false-block rate.

``date`` is passed in as an ISO string and never computed here, so a workflow
script (where clock access is unavailable) can still write a row.
"""
from __future__ import annotations

import datetime
import json
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from acf.adr.contract import (
    PosixStr,
    ReviewerName,
    Severity,
    SpecKind,
)
from acf.exceptions import LedgerWriteError

#: JSONL has no comment syntax, so the preamble is the file's first OBJECT
#: (plan decision D6). Nothing in the pipeline reads the ledger, so no consumer
#: needs to skip it. Compact separators so the preamble line matches the
#: compact formatting every row line already gets from ``model_dump_json``.
LEDGER_PREAMBLE = {
    "_comment": (
        "Adversarial design-review efficacy ledger. Every figure here is a proxy: "
        "defects PREVENTED are unobservable because the counterfactual is invisible. "
        "Read by eye, sorted by surface_call_sites; do not fit a model. Holdout rows "
        "(holdout=true) are a separate population - a narrowing the holdout does not "
        "support is reverted. This file is append-only: post-hoc counters (e.g. "
        "escapes) are corrected by appending a superseding row for the same "
        "spec_path+commit_sha, never by editing this file - a reader takes the "
        "LAST such row."
    ),
}

#: Must stay in step with GEMINI.md item 8's trigger list, because
#: ``filter_would_skip`` is derived from it: the mandate names "a public interface"
#: as a trigger, so a member for it must exist or a public-interface-only spec is
#: recorded ``filter_would_skip=true`` when the narrowed filter would in fact KEEP
#: it — biasing the one number the future narrowing decision rests on.
TouchedSurface = Literal[
    "facade", "persistence_format", "hfsm", "metadata_facade",
    "public_interface", "ui", "none",
]

_ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class LedgerRow(BaseModel):
    """One review run: predictors recorded before dispatch, outcome fields after.

    ``extra="forbid"`` — the persisted-schema convention this repo uses
    throughout (e.g. ``scripts/schemas/oakville_import.py``,
    ``scripts/core/book_registry.py``); a typo'd or fabricated key must fail
    loudly at construction rather than being silently dropped.
    """

    model_config = ConfigDict(extra="forbid")

    # --- recorded BEFORE dispatch (predictors) ---
    spec_path: PosixStr = Field(min_length=1)
    commit_sha: PosixStr = Field(min_length=1)
    date: str                                  # ISO, passed in
    spec_kinds: list[SpecKind] = Field(min_length=1)
    new_design_elements: int = Field(ge=0)
    phases: int = Field(ge=0)
    cited_files: int = Field(ge=0)
    touched_surfaces: list[TouchedSurface] = Field(min_length=1)
    surface_call_sites: int = Field(ge=0)      # blast radius
    filter_would_skip: bool                    # would a narrowed trigger list skip this?
    holdout: bool                              # run ONLY because sampled despite the filter

    # --- recorded AFTER ---
    outcome: Literal["BLOCKED", "CLEARED_WITH_ABSORPTIONS", "CLEARED"]
    findings_by_lens_severity: dict[ReviewerName, dict[Severity, int]]
    converged_count: int = Field(ge=0)
    absorbed: int = Field(ge=0)                # findings the author folded in
    rejected: int = Field(ge=0)                # declined, with reason recorded in the spec
    blocks_overturned: int = Field(ge=0)       # BLOCKED verdicts the author refuted
    # gt=0, not ge=0: a run that dispatched reviewers cannot have cost zero
    # tokens or taken zero seconds. The v6 run wrote tokens=0 despite SKILL.md
    # already saying "round, do not fabricate a number you did not measure" —
    # the exhortation did not hold, so the contract enforces it. An unmeasured
    # value now fails at construction instead of silently corrupting the cost
    # series the narrowing decision reads.
    tokens: int = Field(gt=0)
    wall_clock_s: int = Field(gt=0)

    # --- recorded LATER by post-merge-housekeeping ---
    escapes: int = Field(default=0, ge=0)

    # --- revision-disposition counters (re-runs only; None on first runs) ---
    # Of the claims named in this run's "## Blocking reasons", how many were
    # carried unchanged from the prior reviewed version vs new/revised
    # (delta), per Claim.revision_disposition. The series prices claim-level
    # delta-only re-runs: that lane may be proposed only if refuted_carryover
    # stays 0 across ~15-20 consecutive ledgered re-runs; any nonzero value
    # is an escape that lane would have shipped, and resets the count
    # (spec: ADR_REVISION_EVIDENCE_AND_CARRYOVER_INSTRUMENTATION.md §3 D3).
    # None = unknown (first run); a measured zero is written as 0.
    refuted_carryover: int | None = Field(default=None, ge=0)
    refuted_delta: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def _carryover_counters_paired(self) -> "LedgerRow":
        if (self.refuted_carryover is None) != (self.refuted_delta is None):
            raise ValueError(
                "refuted_carryover and refuted_delta are set together or not "
                "at all: a re-run measures both; a first run knows neither"
            )
        return self

    @field_validator("date")
    @classmethod
    def _iso_date(cls, v: str) -> str:
        return _validate_iso_date(v)


class LedgerAmendment(BaseModel):
    """A superseding record for one prior ``LedgerRow``, never a rewrite of it.

    The ledger is append-only (see ``LEDGER_PREAMBLE``): a post-hoc counter
    learned after the original row was written — ``escapes`` from
    ``post-merge-housekeeping``, or a later correction to ``absorbed`` /
    ``rejected`` / ``blocks_overturned`` — is recorded by appending one of
    these, matched to the original row by ``spec_path`` + ``commit_sha``. A
    reader takes the LAST record for a given spec+commit as authoritative.

    Carries only what identifies the run and what changes. Deliberately does
    NOT carry any of ``LedgerRow``'s pre-dispatch predictors (``spec_kinds``,
    ``touched_surfaces``, etc.) — a short record with just the run identity
    and the counters being corrected already reads as its own record type
    rather than a corrupted/truncated row. Nothing reads this file back to
    find the row being amended (no read-back exists here or anywhere in the
    pipeline); the amender is expected to already know which spec+commit it
    is amending.

    ``extra="forbid"`` for the same reason as ``LedgerRow``: a fabricated or
    typo'd key must fail loudly at construction, not be silently dropped.
    """

    model_config = ConfigDict(extra="forbid")

    spec_path: PosixStr = Field(min_length=1)
    commit_sha: PosixStr = Field(min_length=1)
    date: str                                  # ISO, passed in — see LedgerRow.date

    # Optional: an amender sets only the counter(s) it knows, leaving the rest
    # None so a reader is never told "0" when the true answer is "unknown".
    absorbed: int | None = Field(default=None, ge=0)
    rejected: int | None = Field(default=None, ge=0)
    blocks_overturned: int | None = Field(default=None, ge=0)
    escapes: int | None = Field(default=None, ge=0)

    @field_validator("date")
    @classmethod
    def _iso_date(cls, v: str) -> str:
        return _validate_iso_date(v)


def _validate_iso_date(v: str) -> str:
    """Shared by ``LedgerRow.date`` and ``LedgerAmendment.date`` (§7: one rule,
    not two independent copies of the same regex + calendar check)."""
    if not _ISO_DATE_RE.match(v):
        raise ValueError(f"date must be ISO YYYY-MM-DD, passed in by the caller: {v!r}")
    try:
        datetime.date.fromisoformat(v)
    except ValueError as e:
        raise ValueError(
            f"date must be ISO YYYY-MM-DD, passed in by the caller: {v!r}"
        ) from e
    return v


def _append_json_line(line: str, path: Path) -> None:
    """Shared durability contract for every append to the ledger file.

    Creates the file with the preamble when it does not exist (or is a
    pre-existing 0-byte placeholder); otherwise appends ``line`` untouched.
    Never truncates or rewrites. Raises ``LedgerWriteError`` on any
    ``OSError`` — never degrade to skipping the write, or the measurement
    silently stops being a measurement. Used by both ``append_row`` and
    ``append_amendment``: the durability logic (preamble-on-first-write,
    append-only open mode, fail-loud on ``OSError``) is a single mechanism,
    not two near-identical copies of it (§7).
    """
    target = Path(path)
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        # A pre-existing 0-byte file (touch'd, a crashed first run, a checked-in
        # empty placeholder) must still receive the preamble — `not exists()`
        # alone is False for it and would permanently skip the warning.
        needs_preamble = target.stat().st_size == 0 if target.exists() else True
        with target.open("a", encoding="utf-8", newline="\n") as handle:
            if needs_preamble:
                handle.write(
                    json.dumps(LEDGER_PREAMBLE, ensure_ascii=False, separators=(",", ":"))
                    + "\n"
                )
            handle.write(line + "\n")
    except OSError as e:
        # `.absolute()`, not `.resolve()`: resolve() can itself raise, and we
        # are already inside the except clause for an OSError.
        raise LedgerWriteError(
            f"cannot append to the efficacy ledger at {target.absolute().as_posix()}: {e}"
        ) from e


def append_row(row: LedgerRow, path: Path) -> None:
    """Append one row. Creates the file with the preamble; never truncates or rewrites.

    Raises ``LedgerWriteError`` when the ledger cannot be written — never degrade to
    skipping the row, or the measurement silently stops being a measurement.
    """
    _append_json_line(row.model_dump_json(), path)


def append_amendment(amendment: LedgerAmendment, path: Path) -> None:
    """Append one amendment — a superseding record for a prior row, never a rewrite.

    Same durability contract as ``append_row`` (see ``_append_json_line``): creates
    the preamble on first write, append-only, ``LedgerWriteError`` on ``OSError``.
    """
    _append_json_line(amendment.model_dump_json(), path)
