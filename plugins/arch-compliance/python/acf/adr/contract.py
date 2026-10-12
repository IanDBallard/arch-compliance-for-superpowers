"""Pydantic schemas for the adversarial-design-review skill.

Four blind reviewers each return one payload. The controller wraps them in a
``DesignReviewRun``, which is the single source of truth for the roll-up and the
ledger row.

GEMINI.md §10 — every path-bearing field is POSIX (no backslashes), enforced on
construction. GEMINI.md §3 — a payload that cannot express its own coverage is a
contract violation, not an empty pass. Architectural Contract 5 — a payload that
does not exactly match its schema (extra keys included) is not partially
accepted; it is a contract violation, same as an empty coverage pass.
"""
from __future__ import annotations

import re
from typing import Annotated, Literal, Union

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, field_validator, model_validator

from acf.engine import contains_backslash

SpecKind = Literal["defect", "feature", "docs"]
ClaimFamily = Literal[
    "premise", "root_cause", "compensation", "deletion",
    "mandate", "shape_fit", "sweep", "mechanism_justification",
    # `implementability` asks whether the code offers the hook a proposed
    # mechanism assumes — the chokepoint, the mutable field, the extension
    # point — with file:line. Added after one spec needed FIVE versions of a
    # single field rule: a serializer that did not exist, a raise that
    # contradicted the load invariant, a seam `model_validate` does not
    # provide, a chokepoint three other callers share. Every one was a claim
    # about the mechanism's existence, and `mechanism_justification` does not
    # ask it — that family adjudicates whether a mechanism is at the right
    # RUNG, not whether it can be BUILT.
    "implementability",
]
Verdict = Literal["SURVIVED", "UNPROVEN", "REFUTED"]
Severity = Literal["blocking", "important", "advisory"]
Relationship = Literal[
    "IDENTICAL", "SUBSUMED", "PARTIAL_OVERLAP",
    "BOUNDARY_CUT", "ADJACENT", "DISJOINT",
]
ReviewerName = Literal["refuter", "compliance", "sweeper", "hardening"]
ConflictKind = Literal["restates", "contradicts"]
#: Global Constraint — the only three gate outcomes, spelled once (GateResult,
#: DesignReviewRun). Do not respell this triple a third time.
Outcome = Literal["BLOCKED", "CLEARED_WITH_ABSORPTIONS", "CLEARED"]

#: Hardening ladder. 1 is the STRONGEST rung (make the state unrepresentable);
#: 5 is the weakest (recovery mechanism). A design at a numerically HIGHER rung
#: than the highest applicable one is the finding — do not invert this.
Rung = Annotated[int, Field(ge=1, le=5)]

#: A real path:line has an alphabetic extension (``.py``, ``.md``, ``.yml``).
#: A prose section reference like "section 3.1:2" must NOT satisfy this — the
#: extension group is deliberately ``[A-Za-z]+``, not ``[A-Za-z0-9]+``.
_FILE_LINE_RE = re.compile(r"[^\s:\\]+\.[A-Za-z]+:\d+")


def _reject_backslash(value: str) -> str:
    """§7/§10: the ONLY place this module tests a *path* field for a backslash.

    (Free-text evidence uses ``_reject_backslash_path_in_text`` below, which
    refuses only backslash *paths* inside prose.)

    Delegates to ``acf.engine.contains_backslash`` — the single
    point of definition GEMINI.md §10 requires — rather than reimplementing
    the substring test. This module still cannot adopt the origin host's
    ``PosixPathStr`` wholesale: ``PosixPathStr`` *normalizes* a backslash
    (by design, to tolerate legacy Windows-authored YAML already on disk).
    Every path-bearing field here is freshly emitted by a reviewer subagent
    in this run, not legacy data — normalizing a fabricated path would repair
    it instead of refusing it, defeating the reviewer-honesty contract this
    schema exists to enforce. Rejecting is correct here.

    Task 2 originally carried three inline ``# §10-path-field-ok:`` exemption
    comments on ``doc_path``/``evidence_file``/``spec_path`` (fields the
    ``§10-path-field`` arch detector matches by name) because those fields
    were then typed as plain ``str``, which the detector treats as an
    unmigrated path field unless exempted. Routing every path field through
    the ``PosixStr`` alias below instead of ``str`` moved them out of that
    detector's ``str``-shaped match (``_annotation_is_str_like`` in
    ``scripts/ci/arch_compliance/engine.py`` matches literal ``str``, not an
    ``Annotated`` alias by another name) — the arch-compliance gate no longer
    flags those three lines, so the exemption comments were removed rather
    than kept as dead cover for a finding that no longer fires. Re-verify
    with ``check_arch_compliance_diff`` if this alias is ever renamed.
    """
    if contains_backslash(value):
        raise ValueError(f"must be POSIX (no backslashes): {value!r}")
    return value


#: A Windows drive root (``C:\``) anywhere in free text.
_WIN_DRIVE_RE = re.compile(r"(?<![A-Za-z])[A-Za-z]:\\")
#: Token boundaries in evidence prose: whitespace and quoting/grouping marks.
_EVIDENCE_TOKEN_SPLIT_RE = re.compile(r"""[\s'"`()\[\]]+""")
#: A whole token shaped ``<path>.<ext>:<line>``. ``[^:]+`` stops at the colon,
#: so the match costs one pass per token — no cross-token backtracking.
_TOKEN_FILE_LINE_RE = re.compile(r"([^:]+)\.[A-Za-z]+:\d+")
#: A backslash used as a path separator: followed by a character that is not
#: ``.`` (``\.`` is the regex escape reviewers quote; ``scripts\core`` is not).
_SEPARATOR_BACKSLASH_RE = re.compile(r"\\[^.\\]")


def _is_backslash_file_line(token: str) -> bool:
    match = _TOKEN_FILE_LINE_RE.fullmatch(token.rstrip(",;."))
    return bool(match and _SEPARATOR_BACKSLASH_RE.search(match.group(1)))


def _reject_backslash_path_in_text(value: str) -> str:
    """Refuse a Windows path inside free-text evidence; allow other backslashes.

    ``ClaimVerdict.evidence`` and ``UnanchoredFinding.evidence`` are prose that
    *contains* ``file:line`` anchors, not paths. Reviewers quote the searches
    they executed, and a regex escape (``'os\\.utime'``, ``\\s*=``) is not a
    path — rejecting every backslash here aborted a whole gate run on
    2026-10-08 after both refuter dispatches quoted their grep. What this field
    must still refuse is a fabricated Windows path: a drive root or a
    backslash-separated ``file:line`` anchor.
    """
    if _WIN_DRIVE_RE.search(value) or any(
        _is_backslash_file_line(tok) for tok in _EVIDENCE_TOKEN_SPLIT_RE.split(value)
    ):
        raise ValueError(f"must be POSIX (no backslash paths): {value!r}")
    return value


PosixStr = Annotated[str, AfterValidator(_reject_backslash)]
"""A ``str`` field that REJECTS a backslash on construction (never normalizes).

Applied to every path-bearing field in this module. Errors carry the field's
own value, not a hand-typed label — the discarded ``_posix(value, field)``
helper this replaced (rung-eight of the near-copies it hand-wired) reported
the literal string ``"path"`` for both ``MechanismTrace`` fields, which was
wrong for one of them and is now moot: Pydantic's own error location already
names the real field, so the message needs no label at all.
"""

PosixEvidenceText = Annotated[str, AfterValidator(_reject_backslash_path_in_text)]
"""Free-text evidence: rejects backslash *paths*, permits other backslashes.

Only for reviewer prose that quotes searches alongside ``file:line`` anchors.
Every field that IS a path stays ``PosixStr``.

Accepted gap, by design: a bare backslash path with no line number
(``scripts\\core\\x.py``) passes. It is indistinguishable from a quoted
regex such as ``os\\.utime``, and it cannot fake verification — the
SURVIVED rule's ``_FILE_LINE_RE`` never matches a backslash segment.
"""


class _StrictModel(BaseModel):
    """Base for every schema in this module (Architectural Contract 5).

    ``extra="forbid"`` — a reviewer payload carrying an undeclared key (a
    fabricated ``silent_paths``, an invented ``confidence`` score) is a
    contract violation, not a tolerated extra: "exactly one JSON block
    matching its schema … no partial acceptance." Declared once here, for the
    same reason ``PosixStr`` above replaces eight near-identical field
    validators instead of adding a ninth: independent per-class copies of the
    same declarative rule are exactly the shape that drifts (§7).
    """

    model_config = ConfigDict(extra="forbid")


class Claim(_StrictModel):
    """One falsifiable assertion extracted from the spec."""

    id: str = Field(min_length=1)          # C1, C2, …
    family: ClaimFamily
    statement: str = Field(min_length=1)
    spec_citation: PosixStr | None         # as the SPEC cites it; None is itself a finding
    load_bearing: bool                     # True when the mechanism changes if this is false
    # Re-runs only; None on first runs. Assigned by the CONTROLLER at
    # extraction time, before dispatch, by claim identity against the prior
    # run's archived "## Claims" list — never handed to any reviewer
    # (spec: ADR_REVISION_EVIDENCE_AND_CARRYOVER_INSTRUMENTATION.md M3).
    revision_disposition: Literal["carried", "delta"] | None = None


class ClaimVerdict(_StrictModel):
    """A reviewer's adjudication of one claim."""

    id: str = Field(min_length=1)
    verdict: Verdict
    evidence: PosixEvidenceText            # what the reviewer resolved ITSELF
    reasoning: str = Field(min_length=1)

    @field_validator("evidence")
    @classmethod
    def _evidence_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("evidence must not be blank; say what you looked at")
        return v

    @model_validator(mode="after")
    def _survived_needs_a_resolved_site(self) -> "ClaimVerdict":
        # Architectural Contract 3: the spec's own citation never counts as
        # verification. SURVIVED requires a file:line the reviewer reached itself.
        if self.verdict == "SURVIVED" and not _FILE_LINE_RE.search(self.evidence):
            raise ValueError(
                "SURVIVED requires evidence containing a file:line the reviewer "
                f"resolved itself; got {self.evidence!r}"
            )
        return self


class UnanchoredFinding(_StrictModel):
    """A finding the claim list did not think to ask for."""

    summary: str = Field(min_length=1)
    evidence: PosixEvidenceText = Field(min_length=1)
    severity: Severity


class MechanismTrace(_StrictModel):
    """One mechanism the design adds, placed on the hardening ladder."""

    mechanism: str = Field(min_length=1)
    spec_citation: PosixStr | None
    invalid_state: str = Field(min_length=1)   # a predicate over data, not a story
    producer: PosixStr | None                  # POSIX file:line; None ⇒ superstition (blocking)
    hardening_rejected_because: str | None     # written justification, or None if absent
    design_rung: Rung
    highest_applicable_rung: Rung
    repairs_rather_than_refuses: bool          # second-order tell: fails by silence


class ResponsibilityRelationship(_StrictModel):
    """One (new responsibility × nearest existing shape) classification."""

    new_element: str = Field(min_length=1)
    responsibility: str = Field(min_length=1)
    existing_site: PosixStr = Field(min_length=1)
    relationship: Relationship
    required_resolution: str = Field(min_length=1)
    # null is legal; the gate reports an unjustified ADJACENT exclusion as an
    # absorption finding rather than this model refusing to construct it.
    non_merge_justification: str | None


class DocumentConflict(_StrictModel):
    """An Approved doc stating a contract the spec restates or contradicts."""

    doc_path: PosixStr = Field(min_length=1)
    doc_line: int = Field(ge=1)
    contract_quote: str = Field(min_length=1)
    conflict_kind: ConflictKind


class ReviewerPayloadBase(_StrictModel):
    """Fields every reviewer returns."""

    claim_verdicts: list[ClaimVerdict]
    unanchored_findings: list[UnanchoredFinding]
    looked_for_but_did_not_find: list[str]

    @model_validator(mode="after")
    def _silence_is_not_coverage(self) -> "ReviewerPayloadBase":
        # Architectural Contract 4: a reviewer that found nothing must say what it
        # looked for. Both lists empty is a contract violation, not a clean pass.
        if not self.unanchored_findings and not self.looked_for_but_did_not_find:
            raise ValueError(
                "empty unanchored_findings requires a non-empty "
                "looked_for_but_did_not_find: silence is not coverage"
            )
        return self


class RefuterPayload(ReviewerPayloadBase):
    reviewer: Literal["refuter"]


class CompliancePayload(ReviewerPayloadBase):
    reviewer: Literal["compliance"]
    unstated_mandates: list[str]               # governing mandates the spec fails to name


class SweeperPayload(ReviewerPayloadBase):
    reviewer: Literal["sweeper"]
    relationships: list[ResponsibilityRelationship]
    two_owner_counts: dict[str, int]           # responsibility -> implementations after landing
    document_conflicts: list[DocumentConflict]


class HardeningPayload(ReviewerPayloadBase):
    reviewer: Literal["hardening"]
    mechanism_traces: list[MechanismTrace]

    @property
    def silent_paths(self) -> list[str]:
        """Mechanisms that repair rather than refuse (D7 — derived, never stored twice)."""
        return [t.mechanism for t in self.mechanism_traces if t.repairs_rather_than_refuses]


ReviewerPayload = Annotated[
    Union[RefuterPayload, CompliancePayload, SweeperPayload, HardeningPayload],
    Field(discriminator="reviewer"),
]


class ConvergenceCandidateGroup(_StrictModel):
    """Mechanical grouping output (D2). Sameness is the controller's adjudication."""

    evidence_file: PosixStr = Field(min_length=1)
    reviewers: list[ReviewerName] = Field(min_length=2)
    summaries: list[str]

    @field_validator("reviewers")
    @classmethod
    def _distinct_reviewers(cls, v: list[str]) -> list[str]:
        # Symmetry with ConvergedFinding below: a candidate group is the input to
        # the controller's sameness adjudication, and a group naming one reviewer
        # twice would present a single reviewer's two findings as convergence
        # evidence. Unreachable from group_convergence_candidates today (it keys
        # its buckets by reviewer name, so a repeat cannot be produced), but the
        # rule is the same rule and belongs on both models rather than only on
        # the one whose producer happens to be looser.
        if len(set(v)) < 2:
            raise ValueError(
                f"convergence requires at least two DISTINCT reviewers, got {v!r}"
            )
        return v


class ConvergedFinding(_StrictModel):
    """A finding reached independently by ≥2 blind reviewers. Reported first."""

    summary: str = Field(min_length=1)
    reviewers: list[ReviewerName] = Field(min_length=2)
    evidence: list[PosixStr]

    @field_validator("reviewers")
    @classmethod
    def _distinct_reviewers(cls, v: list[str]) -> list[str]:
        # Convergence is the highest-confidence signal this design produces;
        # a repeated name would fabricate it from a single reviewer's finding.
        if len(set(v)) < 2:
            raise ValueError(
                f"convergence requires at least two DISTINCT reviewers, got {v!r}"
            )
        return v


class GateResult(_StrictModel):
    """Outcome plus the reasons, so the roll-up never re-derives them."""

    outcome: Outcome
    blocking_reasons: list[str] = Field(default_factory=list)
    absorptions: list[str] = Field(default_factory=list)


class DesignReviewRun(_StrictModel):
    """One /adversarial-design-review invocation."""

    spec_path: PosixStr = Field(min_length=1)
    spec_kinds: list[SpecKind] = Field(min_length=1)
    commit_sha: PosixStr = Field(min_length=1)   # PosixStr to match LedgerRow.commit_sha
    claims: list[Claim]
    payloads: list[ReviewerPayload]
    converged: list[ConvergedFinding]
    outcome: Outcome
