"""The gate truth table for adversarial design review.

Implements the spec's blocking triggers 1-5 (of six; the sixth is upstream —
see below) and four absorption triggers, plus one provenance amendment folded
into trigger 1 — no other inferred extras. Reviewers escalate anything else
through the severity field of an unanchored finding, which is blocking
trigger 5.

The spec also names a contract-violation trigger ("any reviewer payload
failing the contract"). That one is enforced upstream by
``parser.parse_reviewer_payload`` raising ``ReviewerContractViolationError``,
so a malformed payload never reaches this function (plan decision D3) — it is
not one of the five numbered triggers below and is not re-implemented here.

Amendment (Architectural Contract 3, second sentence): "A reviewer may return
SURVIVED only if it independently reached the evidence. The spec's own
citation is not verification." ``ClaimVerdict`` already refuses a SURVIVED
whose evidence contains no file:line at all (contract.py's
``_survived_needs_a_resolved_site``) — but that check only asks "is there A
file:line here", not "is it a DIFFERENT file:line than the one already handed
to the reviewer in the claim". Nothing else in the system holds both the
claim (with its ``spec_citation``) and the verdict (with its ``evidence``) at
once; this module does, so it owns the check. A SURVIVED verdict whose
evidence resolves to the same file:line as its claim's own ``spec_citation``
is treated as UNPROVEN for rule 1 — it must block a load-bearing claim, and
must not affect a non-load-bearing one, exactly like any other UNPROVEN.
"""
from __future__ import annotations

from acf.adr.contract import (
    Claim,
    ClaimVerdict,
    ConvergedFinding,
    GateResult,
    HardeningPayload,
    Outcome,
    ReviewerPayload,
    SpecKind,
    SweeperPayload,
)
# Reuse the file:line pattern contract.py already uses to decide whether
# SURVIVED evidence names a resolved site at all. Duplicating that regex here
# would be a second implementation of "what counts as a file:line" (GEMINI.md
# §7) that could silently drift from the one contract.py enforces at
# construction time. contract.py is out of scope for this task (it is not
# edited), so the shared pattern is imported rather than re-declared; this
# codebase already imports leading-underscore module attributes across files
# in the same package when the alternative is a duplicate definition (e.g.
# ``scripts.core.build_scope._get_type_def``, ``scripts.core.asset_paths
# ._is_foreign_absolute``).
from acf.adr.contract import _FILE_LINE_RE
from acf.exceptions import SpecKindUndeterminedError

#: The single family the gate blocks on for each actionable spec kind. A pure
#: enhancement is never asked for a root cause, and the gate never blocks on a
#: missing one. ``docs`` specs never reach the gate — the skill declines.
LOAD_BEARING_FAMILY: dict[str, str | None] = {
    "defect": "root_cause",
    "feature": "shape_fit",
    "docs": None,
}

_ADVERSE = frozenset({"REFUTED", "UNPROVEN"})
# The relationship table's own required_resolution for IDENTICAL ("Delete the
# new one; consume the existing") and SUBSUMED ("Generalize the container,
# don't add a sibling") is a required action the author must take before
# proceeding — exactly what an absorption is. Omitting them from this set was
# a gap, not a decision: a sweeper that classifies a real duplicate as
# IDENTICAL produced no gate consequence at all unless it separately filed a
# blocking unanchored finding. ADJACENT (handled by its own unjustified-
# exclusion branch below) and DISJOINT are deliberately excluded here.
_ABSORB_RELATIONSHIPS = frozenset(
    {"IDENTICAL", "SUBSUMED", "PARTIAL_OVERLAP", "BOUNDARY_CUT"}
)


def _file_line_token(text: str) -> str | None:
    """Extract the first file:line token from ``text``, casefolded, or None."""
    match = _FILE_LINE_RE.search(text)
    return match.group(0).casefold() if match else None


def _file_line_tokens(text: str) -> set[str]:
    """Extract EVERY file:line token in ``text``, casefolded."""
    return {m.group(0).casefold() for m in _FILE_LINE_RE.finditer(text)}


def _is_uncorroborated_citation_copy(claim: Claim, verdict: ClaimVerdict) -> bool:
    """True when a SURVIVED verdict offers nothing beyond the claim's own citation.

    Comparison is by extracted file:line token, not naive full-string equality —
    the evidence may embed the citation in prose ("Confirmed per ... at
    scripts/x.py:1, no further check needed") rather than repeat it bare, and a
    full-string comparison would miss exactly that failure mode. If the claim
    has no ``spec_citation`` there is nothing to have copied, so the rule
    cannot fire.

    **Every** token in the evidence is compared, not just the first. The rule is
    "the spec's own citation is not verification", not "citing the spec's line
    at all is disqualifying": a reviewer that resolves the cited line *and*
    reaches further has done more work, not less. Matching on the first token
    alone downgraded two such verdicts in the v6 run of this gate against
    ``COLLECTION_ORDERING_SINGLE_OWNER.md`` (2026-08-11) — evidence citing the
    claim's line plus an independently-found second line was treated as an
    uncorroborated copy, inflating that run's blocking count. Worse, the
    first-token rule rewarded evidence that conspicuously *avoids* the cited
    line, which is the opposite of the discipline Constraint 3 exists to impose.
    """
    if verdict.verdict != "SURVIVED" or claim.spec_citation is None:
        return False
    citation_token = _file_line_token(claim.spec_citation)
    evidence_tokens = _file_line_tokens(verdict.evidence)
    if citation_token is None or not evidence_tokens:
        return False
    # Fires only when the citation is the ONLY line the evidence offers.
    return evidence_tokens == {citation_token}


def classify_outcome(
    *,
    spec_kinds: list[SpecKind],
    claims: list[Claim],
    payloads: list[ReviewerPayload],
    converged: list[ConvergedFinding],
) -> GateResult:
    """Classify a run's outcome from its claims and reviewer payloads.

    ``converged`` is accepted so the signature is complete for the controller and
    the roll-up; convergence raises confidence in a finding, never the outcome —
    the underlying findings already carry their own severity.
    """
    blocking: list[str] = []
    absorptions: list[str] = []

    verdicts = {v.id: v for payload in payloads for v in payload.claim_verdicts}
    families = {c.family for c in claims}

    # A verdict whose id matches no extracted claim is discarded by the lookup in
    # rule 1 — it fails safe, since an id nobody extracted can never establish
    # anything. But the resulting *diagnosis* misleads: the author sees every real
    # claim report "received no verdict from any reviewer" and concludes the
    # reviewers went silent, when in fact they adjudicated ids that do not exist
    # (a stale claim list, or a reviewer that renumbered). Naming the orphans
    # inside rule 1's own reason, rather than as a sixth blocking trigger, keeps
    # the spec's trigger count intact — this changes no outcome, only the text of
    # a block that already fires.
    orphan_ids = sorted(
        {v.id for payload in payloads for v in payload.claim_verdicts}
        - {c.id for c in claims}
    )
    orphan_note = (
        " (reviewers did return verdicts for unextracted claim ids "
        f"{', '.join(repr(i) for i in orphan_ids)}, which adjudicate nothing)"
        if orphan_ids else ""
    )

    # Blocking 1 — a load-bearing claim that a second reader could not re-derive.
    for claim in claims:
        if not claim.load_bearing:
            continue
        verdict = verdicts.get(claim.id)
        if verdict is None:
            blocking.append(
                f"load-bearing claim {claim.id} ({claim.family}) received no verdict "
                "from any reviewer — an unadjudicated claim is not established"
                f"{orphan_note}"
            )
        elif _is_uncorroborated_citation_copy(claim, verdict):
            blocking.append(
                f"load-bearing claim {claim.id} ({claim.family}) is SURVIVED but its "
                f"evidence ({verdict.evidence!r}) merely restates the spec's own "
                f"citation ({claim.spec_citation!r}) — not independent verification, "
                "treated as UNPROVEN"
            )
        elif verdict.verdict in _ADVERSE:
            blocking.append(
                f"load-bearing claim {claim.id} ({claim.family}) is "
                f"{verdict.verdict}: {verdict.reasoning}"
            )

    # Blocking 2 — the kind's load-bearing family is absent from the claim list.
    for kind in spec_kinds:
        if kind not in LOAD_BEARING_FAMILY:
            # classify_outcome takes loose components before DesignReviewRun
            # validates anything, so an unrecognized kind must fail loud here
            # rather than silently resolve to "no family required" — that
            # would let a misspelled or invented kind bypass rule 2 entirely
            # for a defect/feature spec that never named a real load-bearing
            # claim (§3/§4: no silent None default).
            raise SpecKindUndeterminedError(
                f"unrecognized spec kind {kind!r}; legal kinds are "
                f"{sorted(LOAD_BEARING_FAMILY)}"
            )
        required = LOAD_BEARING_FAMILY[kind]
        if required is not None and required not in families:
            blocking.append(
                f"spec classifies as {kind!r} but extracts no {required!r} claim"
            )

    # Blocking 3 — a compliance claim refuted outright.
    for claim in claims:
        if claim.family != "mandate":
            continue
        verdict = verdicts.get(claim.id)
        if verdict is not None and verdict.verdict == "REFUTED":
            blocking.append(
                f"mandate claim {claim.id} is REFUTED: {verdict.reasoning}"
            )

    # Blocking 3b — a mechanism whose hook could not be shown to exist.
    #
    # Stricter than rule 3: UNPROVEN blocks as well as REFUTED. "The hook is
    # not there" and "I could not find the hook" have the same consequence for
    # an implementer, and this family exists precisely because mechanisms kept
    # shipping on assumed existence — five versions of one field rule, each
    # naming a hook (a serializer, a seam, a chokepoint) that a one-minute grep
    # would have refuted.
    for claim in claims:
        if claim.family != "implementability":
            continue
        verdict = verdicts.get(claim.id)
        if verdict is not None and verdict.verdict in _ADVERSE:
            blocking.append(
                f"implementability claim {claim.id} is {verdict.verdict}: "
                f"{verdict.reasoning}"
            )

    for payload in payloads:
        # Blocking 4 — superstition: a mechanism with no producer to point at.
        if isinstance(payload, HardeningPayload):
            for trace in payload.mechanism_traces:
                if trace.producer is None:
                    blocking.append(
                        f"mechanism {trace.mechanism!r} has no named producer for the "
                        f"state it handles ({trace.invalid_state}) — superstition"
                    )
                # Absorption — sitting below the highest applicable rung. Rung 1 is
                # strongest, so a numerically HIGHER design rung is the weaker design.
                # A SEPARATE `if`, not `elif` on the producer check: the absorption
                # trigger as specified carries no producer precondition, and a trace
                # that is both superstitious and under-hardened must report both
                # findings in one pass rather than hiding the second behind the
                # first (absorptions are still reported alongside a block).
                if (
                    trace.design_rung > trace.highest_applicable_rung
                    and not trace.hardening_rejected_because
                ):
                    absorptions.append(
                        f"mechanism {trace.mechanism!r} sits at rung {trace.design_rung} "
                        f"when rung {trace.highest_applicable_rung} applies, with no "
                        "written justification"
                    )

        # Blocking 5 — a reviewer marked a finding blocking on its own authority.
        for finding in payload.unanchored_findings:
            if finding.severity == "blocking":
                blocking.append(
                    f"[{payload.reviewer}] {finding.summary} ({finding.evidence})"
                )

        # Absorptions — partial duplication and unjustified exclusions.
        if isinstance(payload, SweeperPayload):
            for rel in payload.relationships:
                if rel.relationship in _ABSORB_RELATIONSHIPS:
                    absorptions.append(
                        f"{rel.relationship}: {rel.new_element!r} shares responsibility "
                        f"{rel.responsibility!r} with {rel.existing_site} — "
                        f"{rel.required_resolution}"
                    )
                elif rel.relationship == "ADJACENT" and not rel.non_merge_justification:
                    absorptions.append(
                        f"ADJACENT exclusion of {rel.existing_site} for responsibility "
                        f"{rel.responsibility!r} is unjustified in writing"
                    )

    # Absorption — an addition-only fix, which §1.7 calls presumptively papering over.
    if "defect" in spec_kinds and "deletion" not in families:
        absorptions.append(
            "defect spec extracts no deletion claim — an addition-only design is "
            "presumptively papering over the crack (§1.7)"
        )

    # Annotated with the ``Outcome`` alias contract.py already spells once: the
    # bare-string branches below otherwise widen to ``str``, which
    # ``GateResult.outcome`` (a Literal) will not accept. A cast would assert the
    # narrowing instead of letting the checker verify each branch against the
    # alias, which is the part worth having.
    outcome: Outcome
    if blocking:
        outcome = "BLOCKED"
    elif absorptions:
        outcome = "CLEARED_WITH_ABSORPTIONS"
    else:
        outcome = "CLEARED"
    return GateResult(outcome=outcome, blocking_reasons=blocking, absorptions=absorptions)
