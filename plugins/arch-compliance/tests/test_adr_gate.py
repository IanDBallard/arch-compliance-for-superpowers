"""The gate truth table (spec: The gate). Exactly the spec's rules — no extras.

Plus the provenance amendment: a SURVIVED verdict whose evidence merely restates
the claim's own ``spec_citation`` (verbatim, or embedded in prose) is not
independent verification and is treated as UNPROVEN for rule 1.
"""
import pytest

from acf.adr.contract import (
    Claim,
    ClaimVerdict,
    HardeningPayload,
    MechanismTrace,
    RefuterPayload,
    ResponsibilityRelationship,
    SweeperPayload,
    UnanchoredFinding,
)
from acf.adr.gate import LOAD_BEARING_FAMILY, classify_outcome
from acf.exceptions import SpecKindUndeterminedError


def _claim(cid="C1", family="root_cause", load_bearing=True, spec_citation="scripts/x.py:1"):
    return Claim(id=cid, family=family, statement="s",
                 spec_citation=spec_citation, load_bearing=load_bearing)


def _refuter(verdicts, unanchored=None):
    return RefuterPayload(
        reviewer="refuter", claim_verdicts=verdicts,
        unanchored_findings=unanchored or [],
        looked_for_but_did_not_find=["nothing else"],
    )


def _verdict(cid="C1", verdict="SURVIVED", evidence=None):
    # NOTE (amendment fixture fix): the default SURVIVED evidence is a file:line
    # DISTINCT from _claim's default spec_citation ("scripts/x.py:1"), so every
    # brief-supplied test below — none of which is about provenance — continues
    # to exercise a genuinely independent SURVIVED, not an accidental citation
    # copy. The amendment-specific tests further down pass `evidence` explicitly
    # to construct the citation-copy case on purpose.
    if evidence is None:
        evidence = "scripts/y.py:9" if verdict == "SURVIVED" else "no such block"
    return ClaimVerdict(id=cid, verdict=verdict, evidence=evidence, reasoning="r")


def _sweeper(relationships):
    return SweeperPayload(
        reviewer="sweeper", claim_verdicts=[], unanchored_findings=[],
        looked_for_but_did_not_find=["x"], relationships=relationships,
        two_owner_counts={}, document_conflicts=[],
    )


def _hardening(traces):
    return HardeningPayload(
        reviewer="hardening", claim_verdicts=[], unanchored_findings=[],
        looked_for_but_did_not_find=["x"], mechanism_traces=traces,
    )


def _trace(producer="scripts/x.py:1", design_rung=2, highest=2, because=None):
    return MechanismTrace(
        mechanism="m", spec_citation=None, invalid_state="s", producer=producer,
        hardening_rejected_because=because, design_rung=design_rung,
        highest_applicable_rung=highest, repairs_rather_than_refuses=False,
    )


def _defect_ok():
    """A minimal defect spec that clears: root_cause SURVIVED plus a deletion claim."""
    claims = [_claim("C1", "root_cause"), _claim("C2", "deletion", load_bearing=False)]
    payloads = [_refuter([_verdict("C1"), _verdict("C2")])]
    return claims, payloads


# --- CLEARED ---------------------------------------------------------------

def test_clean_defect_spec_clears():
    claims, payloads = _defect_ok()
    result = classify_outcome(spec_kinds=["defect"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "CLEARED"
    assert result.blocking_reasons == []
    assert result.absorptions == []


def test_clean_feature_spec_clears():
    claims = [_claim("C1", "shape_fit")]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=[_refuter([_verdict("C1")])], converged=[])
    assert result.outcome == "CLEARED"


# --- blocking rule 1: load-bearing REFUTED / UNPROVEN ---------------------

def test_load_bearing_refuted_blocks():
    claims, _ = _defect_ok()
    payloads = [_refuter([_verdict("C1", "REFUTED"), _verdict("C2")])]
    result = classify_outcome(spec_kinds=["defect"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "BLOCKED"
    assert any("C1" in r and "REFUTED" in r for r in result.blocking_reasons)


def test_load_bearing_unproven_blocks_exactly_like_refuted():
    claims, _ = _defect_ok()
    payloads = [_refuter([_verdict("C1", "UNPROVEN"), _verdict("C2")])]
    result = classify_outcome(spec_kinds=["defect"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "BLOCKED"
    assert any("UNPROVEN" in r for r in result.blocking_reasons)


def test_non_load_bearing_refuted_does_not_block():
    claims = [_claim("C1", "root_cause"),
              _claim("C2", "deletion", load_bearing=False),
              _claim("C3", "premise", load_bearing=False)]
    payloads = [_refuter([_verdict("C1"), _verdict("C2"), _verdict("C3", "REFUTED")])]
    result = classify_outcome(spec_kinds=["defect"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "CLEARED"


def test_unadjudicated_load_bearing_claim_blocks_as_unproven():
    claims, _ = _defect_ok()
    payloads = [_refuter([_verdict("C2")])]        # C1 never adjudicated
    result = classify_outcome(spec_kinds=["defect"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "BLOCKED"
    assert any("C1" in r and "no verdict" in r for r in result.blocking_reasons)


def test_verdicts_for_unextracted_claim_ids_are_named_in_the_block_reason():
    # A verdict whose id matches no extracted claim is discarded by rule 1's
    # lookup — correct, and it fails safe. But the resulting DIAGNOSIS misled: the
    # author saw only "C1 received no verdict from any reviewer" and concluded the
    # reviewers went silent, when in fact they adjudicated ids nobody extracted (a
    # stale claim list, or a reviewer that renumbered). The orphan ids are now
    # named inside rule 1's own reason rather than as a sixth blocking trigger, so
    # the outcome is unchanged — hence the two assertions on outcome and reason
    # count below, which would catch a fix that added a trigger instead.
    claims, _ = _defect_ok()
    payloads = [_refuter([_verdict("C99"), _verdict("C2")])]  # C1 unadjudicated
    result = classify_outcome(spec_kinds=["defect"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "BLOCKED"
    reason = next(r for r in result.blocking_reasons if "C1" in r and "no verdict" in r)
    assert "C99" in reason, reason
    # No extra blocking reason was introduced for the orphan itself.
    assert len([r for r in result.blocking_reasons if "C99" in r]) == 1


def test_no_orphan_note_when_every_verdict_matches_a_claim():
    # The mirror case, and the one that proves the note is derived rather than
    # always appended: same unadjudicated-C1 block, but with no orphan verdict,
    # must carry no orphan clause at all.
    claims, _ = _defect_ok()
    payloads = [_refuter([_verdict("C2")])]
    result = classify_outcome(spec_kinds=["defect"], claims=claims,
                              payloads=payloads, converged=[])
    reason = next(r for r in result.blocking_reasons if "C1" in r and "no verdict" in r)
    assert "unextracted" not in reason, reason


# --- blocking rule 2: missing kind-keyed load-bearing family -------------

def test_defect_spec_without_a_root_cause_claim_blocks():
    claims = [_claim("C2", "deletion", load_bearing=False)]
    result = classify_outcome(spec_kinds=["defect"], claims=claims,
                              payloads=[_refuter([_verdict("C2")])], converged=[])
    assert result.outcome == "BLOCKED"
    assert any("root_cause" in r for r in result.blocking_reasons)


def test_feature_spec_without_a_root_cause_claim_never_blocks_on_one():
    claims = [_claim("C1", "shape_fit")]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=[_refuter([_verdict("C1")])], converged=[])
    assert result.outcome == "CLEARED"
    assert not any("root_cause" in r for r in result.blocking_reasons)


def test_feature_spec_without_a_shape_fit_claim_blocks():
    claims = [_claim("C1", "premise", load_bearing=False)]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=[_refuter([_verdict("C1")])], converged=[])
    assert result.outcome == "BLOCKED"
    assert any("shape_fit" in r for r in result.blocking_reasons)


def test_dual_kind_spec_requires_both_load_bearing_families():
    claims = [_claim("C1", "root_cause"), _claim("C2", "deletion", load_bearing=False)]
    result = classify_outcome(spec_kinds=["defect", "feature"], claims=claims,
                              payloads=[_refuter([_verdict("C1"), _verdict("C2")])],
                              converged=[])
    assert result.outcome == "BLOCKED"
    assert any("shape_fit" in r for r in result.blocking_reasons)


# --- blocking rule 3: mandate REFUTED ------------------------------------

def test_refuted_mandate_claim_blocks():
    claims = [_claim("C1", "shape_fit"), _claim("C2", "mandate", load_bearing=False)]
    payloads = [_refuter([_verdict("C1"), _verdict("C2", "REFUTED")])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "BLOCKED"
    assert any("mandate" in r for r in result.blocking_reasons)


def test_unproven_mandate_claim_alone_does_not_block():
    claims = [_claim("C1", "shape_fit"), _claim("C2", "mandate", load_bearing=False)]
    payloads = [_refuter([_verdict("C1"), _verdict("C2", "UNPROVEN")])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "CLEARED"


# --- blocking rule 4: superstition (no named producer) -------------------

def test_mechanism_with_no_producer_blocks():
    claims = [_claim("C1", "shape_fit")]
    payloads = [_refuter([_verdict("C1")]), _hardening([_trace(producer=None)])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "BLOCKED"
    assert any("no named producer" in r for r in result.blocking_reasons)


# --- blocking rule 5: blocking-severity unanchored finding ---------------

def test_blocking_unanchored_finding_blocks():
    claims = [_claim("C1", "shape_fit")]
    unanchored = [UnanchoredFinding(summary="migration cannot read its own inputs",
                                    evidence="scripts/x.py:9", severity="blocking")]
    payloads = [_refuter([_verdict("C1")], unanchored=unanchored)]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "BLOCKED"
    assert any("migration cannot read" in r for r in result.blocking_reasons)


def test_advisory_unanchored_finding_does_not_block():
    claims = [_claim("C1", "shape_fit")]
    unanchored = [UnanchoredFinding(summary="naming nit", evidence="scripts/x.py:9",
                                    severity="advisory")]
    payloads = [_refuter([_verdict("C1")], unanchored=unanchored)]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "CLEARED"


# --- absorptions ---------------------------------------------------------

def _rel(relationship, justification=None):
    return ResponsibilityRelationship(
        new_element="E", responsibility="R", existing_site="scripts/y.py:3",
        relationship=relationship, required_resolution="name R",
        non_merge_justification=justification,
    )


def test_partial_overlap_absorbs():
    claims = [_claim("C1", "shape_fit")]
    payloads = [_refuter([_verdict("C1")]), _sweeper([_rel("PARTIAL_OVERLAP")])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "CLEARED_WITH_ABSORPTIONS"
    assert any("PARTIAL_OVERLAP" in a for a in result.absorptions)


def test_boundary_cut_absorbs():
    claims = [_claim("C1", "shape_fit")]
    payloads = [_refuter([_verdict("C1")]), _sweeper([_rel("BOUNDARY_CUT")])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "CLEARED_WITH_ABSORPTIONS"


def test_unjustified_adjacent_exclusion_absorbs():
    claims = [_claim("C1", "shape_fit")]
    payloads = [_refuter([_verdict("C1")]), _sweeper([_rel("ADJACENT")])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "CLEARED_WITH_ABSORPTIONS"
    assert any("ADJACENT" in a for a in result.absorptions)


def test_justified_adjacent_exclusion_clears():
    claims = [_claim("C1", "shape_fit")]
    payloads = [_refuter([_verdict("C1")]),
                _sweeper([_rel("ADJACENT", "different cadence and consumer")])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "CLEARED"


def test_disjoint_relationship_clears():
    claims = [_claim("C1", "shape_fit")]
    payloads = [_refuter([_verdict("C1")]), _sweeper([_rel("DISJOINT")])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "CLEARED"


def test_mechanism_below_its_highest_applicable_rung_absorbs():
    # design_rung 5 (recovery) when rung 1 (unrepresentable) applies, unjustified.
    claims = [_claim("C1", "shape_fit")]
    payloads = [_refuter([_verdict("C1")]),
                _hardening([_trace(design_rung=5, highest=1)])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "CLEARED_WITH_ABSORPTIONS"
    assert any("rung 5" in a and "rung 1" in a for a in result.absorptions)


def test_mechanism_below_its_rung_with_written_justification_clears():
    claims = [_claim("C1", "shape_fit")]
    payloads = [_refuter([_verdict("C1")]),
                _hardening([_trace(design_rung=5, highest=1,
                                   because="genuine external boundary, filed as debt")])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "CLEARED"


def test_mechanism_at_its_highest_applicable_rung_clears():
    claims = [_claim("C1", "shape_fit")]
    payloads = [_refuter([_verdict("C1")]),
                _hardening([_trace(design_rung=2, highest=2)])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "CLEARED"


def test_defect_spec_with_no_deletion_claim_absorbs_rather_than_blocks():
    claims = [_claim("C1", "root_cause")]
    result = classify_outcome(spec_kinds=["defect"], claims=claims,
                              payloads=[_refuter([_verdict("C1")])], converged=[])
    assert result.outcome == "CLEARED_WITH_ABSORPTIONS"
    assert any("deletion" in a and "addition-only" in a for a in result.absorptions)


def test_feature_spec_with_no_deletion_claim_clears():
    claims = [_claim("C1", "shape_fit")]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=[_refuter([_verdict("C1")])], converged=[])
    assert result.outcome == "CLEARED"


# --- fix round 2: IDENTICAL and SUBSUMED must also absorb -----------------
#
# The relationship table's own required_resolution for each is a required
# action the author must take before proceeding — "Delete the new one;
# consume the existing" (IDENTICAL) and "Generalize the container, don't add
# a sibling" (SUBSUMED). Before this fix only PARTIAL_OVERLAP and BOUNDARY_CUT
# triggered an absorption; a sweeper classifying a real duplicate as
# IDENTICAL produced nothing at all unless it separately filed a blocking
# unanchored finding, which is luck, not mechanism (task-10-acceptance.md
# Friction 6). ADJACENT and DISJOINT keep their existing, unmodified handling.

@pytest.mark.parametrize("relationship,should_absorb", [
    ("IDENTICAL", True),
    ("SUBSUMED", True),
    ("PARTIAL_OVERLAP", True),
    ("BOUNDARY_CUT", True),
    ("ADJACENT", True),   # via the pre-existing unjustified-ADJACENT branch,
                           # not via _ABSORB_RELATIONSHIPS — untouched by this fix
    ("DISJOINT", False),
])
def test_relationship_absorption_trigger_set(relationship, should_absorb):
    """Each of the six relationships has a defined, individually-owned trigger.

    Asserting the relationship NAME appears in the sole absorption string (and
    that exactly one absorption fired) means a wrong expected outcome for one
    relationship cannot be masked by a neighboring rule firing instead — e.g.
    if IDENTICAL were (wrongly) left out of the trigger set, this case would
    fail on both the outcome and the absorption count, not silently pass
    because DISJOINT's or ADJACENT's branch happened to also be quiet.
    """
    claims = [_claim("C1", "shape_fit")]
    payloads = [_refuter([_verdict("C1")]), _sweeper([_rel(relationship)])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    if should_absorb:
        assert result.outcome == "CLEARED_WITH_ABSORPTIONS"
        assert len(result.absorptions) == 1
        assert relationship in result.absorptions[0]
    else:
        assert result.outcome == "CLEARED"
        assert result.absorptions == []


def test_identical_absorption_message_carries_its_own_required_resolution():
    # An author reading an IDENTICAL absorption needs "delete and consume",
    # not the generic sentence a PARTIAL_OVERLAP gets. The message must embed
    # the reviewer-supplied required_resolution text verbatim — a hardcoded
    # generic string invented by this gate would not vary per relationship
    # and this assertion would fail against it.
    claims = [_claim("C1", "shape_fit")]
    rel = ResponsibilityRelationship(
        new_element="SlugNormalizer.normalize",
        responsibility="shape a title into a slug",
        existing_site="scripts/x.py:26",
        relationship="IDENTICAL",
        required_resolution="Delete the new one; consume the existing.",
        non_merge_justification=None,
    )
    payloads = [_refuter([_verdict("C1")]), _sweeper([rel])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "CLEARED_WITH_ABSORPTIONS"
    assert any(
        "IDENTICAL" in a and "Delete the new one; consume the existing." in a
        for a in result.absorptions
    ), result.absorptions


def test_subsumed_absorption_message_carries_its_own_required_resolution():
    # Same proof for SUBSUMED, whose required_resolution text differs from
    # IDENTICAL's — confirms the message isn't a relationship-independent
    # template that happens to work for one case.
    claims = [_claim("C1", "shape_fit")]
    rel = ResponsibilityRelationship(
        new_element="WideSpecialCase",
        responsibility="handle a special case of an existing responsibility",
        existing_site="scripts/x.py:40",
        relationship="SUBSUMED",
        required_resolution="Generalize the container, don't add a sibling.",
        non_merge_justification=None,
    )
    payloads = [_refuter([_verdict("C1")]), _sweeper([rel])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "CLEARED_WITH_ABSORPTIONS"
    assert any(
        "SUBSUMED" in a and "Generalize the container, don't add a sibling." in a
        for a in result.absorptions
    ), result.absorptions


# --- precedence ----------------------------------------------------------

def test_blocking_wins_over_absorptions():
    claims = [_claim("C1", "shape_fit")]
    payloads = [_refuter([_verdict("C1", "REFUTED")]),
                _sweeper([_rel("PARTIAL_OVERLAP")])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "BLOCKED"
    assert result.absorptions, "absorptions are still reported alongside a block"


def test_docs_kind_has_no_load_bearing_family():
    assert LOAD_BEARING_FAMILY["docs"] is None


# --- amendment: SURVIVED evidence that merely restates spec_citation -----
# Architectural Contract 3: "A reviewer may return SURVIVED only if it
# independently reached the evidence. The spec's own citation is not
# verification." Nothing before this task checked the second sentence — a
# reviewer could copy the claim's own spec_citation into its evidence field
# verbatim (or wrapped in prose) and pass the contract.py file:line check
# trivially, because that check only asks "is there A file:line here", not
# "is it a DIFFERENT file:line than the one already handed to the reviewer".

def test_survived_evidence_verbatim_citation_blocks():
    # C1's spec_citation is "scripts/x.py:1" (the _claim default). The
    # reviewer's "evidence" is the identical string — it re-typed the claim's
    # own citation instead of resolving anything itself.
    claims = [_claim("C1", "shape_fit")]
    payloads = [_refuter([_verdict("C1", evidence="scripts/x.py:1")])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "BLOCKED"
    assert any(
        "C1" in r and "restates" in r and "own citation" in r
        for r in result.blocking_reasons
    ), result.blocking_reasons


def test_survived_evidence_citation_embedded_in_prose_blocks():
    # Same citation, but dressed up as prose rather than typed bare — the
    # naive-full-string-equality failure mode the brief amendment calls out.
    claims = [_claim("C1", "shape_fit")]
    payloads = [_refuter([_verdict(
        "C1",
        evidence="Confirmed per the spec's own note at scripts/x.py:1, no further check needed.",
    )])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "BLOCKED"
    assert any(
        "C1" in r and "restates" in r and "own citation" in r
        for r in result.blocking_reasons
    ), result.blocking_reasons


def test_survived_with_genuinely_different_evidence_still_clears():
    # A real independent SURVIVED (a file:line distinct from the citation,
    # same shape as the default _verdict() evidence used throughout the rest
    # of this file) must not be caught by the amendment.
    claims = [_claim("C1", "shape_fit", spec_citation="scripts/x.py:1")]
    payloads = [_refuter([_verdict("C1", evidence="scripts/q.py:42")])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "CLEARED"
    assert result.blocking_reasons == []


def test_refuted_implementability_claim_blocks():
    # Added after the ordering spec needed FIVE versions of one field rule.
    # v5 named a model_serializer that did not exist; v6 a raise that
    # contradicted the load invariant; v7 a seam model_validate does not
    # provide; v8 a chokepoint three other callers share. Each was a claim
    # about whether the code offers the hook the mechanism assumes — and no
    # claim family asked that. mechanism_justification asks whether a mechanism
    # is at the right RUNG, not whether it can be BUILT.
    claims = [_claim("C1", "implementability")]
    payloads = [_refuter([_verdict("C1", verdict="REFUTED", evidence="scripts/q.py:42")])]
    result = classify_outcome(spec_kinds=["defect"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "BLOCKED"
    assert any("C1" in r and "implementability" in r for r in result.blocking_reasons), \
        result.blocking_reasons


def test_unproven_implementability_claim_blocks_too():
    # Stricter than `mandate`, deliberately. "I could not find the hook this
    # mechanism needs" and "the hook is not there" have the same consequence
    # for an implementer, and the whole point is to stop shipping a mechanism
    # whose existence was assumed rather than checked.
    claims = [_claim("C1", "implementability")]
    payloads = [_refuter([_verdict("C1", verdict="UNPROVEN", evidence="scripts/q.py:42")])]
    result = classify_outcome(spec_kinds=["defect"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "BLOCKED"


def test_survived_implementability_claim_does_not_block():
    # A defect spec must also carry a root_cause claim (pre-existing rule), so
    # the fixture supplies a satisfied one — otherwise this would pass for the
    # wrong reason.
    claims = [_claim("C0", "root_cause"), _claim("C1", "implementability")]
    payloads = [_refuter([
        _verdict("C0", evidence="scripts/p.py:7"),
        _verdict("C1", evidence="scripts/q.py:42"),
    ])]
    result = classify_outcome(spec_kinds=["defect"], claims=claims,
                              payloads=payloads, converged=[])
    # Not CLEARED outright — a defect spec with no `deletion` claim trips the
    # addition-only absorption. What matters here is that nothing BLOCKS.
    assert result.outcome != "BLOCKED"
    assert result.blocking_reasons == []


def test_survived_evidence_citing_the_claim_plus_more_does_not_block():
    # Found by the v6 run of /adversarial-design-review on
    # COLLECTION_ORDERING_SINGLE_OWNER.md (2026-08-11): two claims (C7, C13)
    # were marked SURVIVED with evidence that CONFIRMED the spec's citation and
    # then added independent file:lines of the reviewer's own — and both were
    # downgraded to UNPROVEN, inflating the run's blocking count.
    #
    # The rule is "the spec's own citation is not verification", not "citing
    # the spec's line at all is disqualifying". A reviewer that resolves the
    # cited line AND reaches further has done more work, not less; punishing it
    # rewards evidence that conspicuously avoids the citation. The rule must
    # fire only when the citation is the ONLY file:line the evidence offers.
    claims = [_claim("C1", "shape_fit", spec_citation="scripts/x.py:1")]
    payloads = [_refuter([_verdict(
        "C1",
        evidence="scripts/x.py:1 applies the transform; scripts/q.py:42 is the no-groups branch",
    )])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "CLEARED"
    assert result.blocking_reasons == []


def test_survived_evidence_repeating_only_the_citation_twice_still_blocks():
    # The complement: more than one token, but every token is the citation.
    # Restating the same line twice is not corroboration.
    claims = [_claim("C1", "shape_fit", spec_citation="scripts/x.py:1")]
    payloads = [_refuter([_verdict(
        "C1",
        evidence="scripts/x.py:1 as the spec says, and again at scripts/x.py:1",
    )])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "BLOCKED"
    assert any(
        "C1" in r and "restates" in r and "own citation" in r
        for r in result.blocking_reasons
    ), result.blocking_reasons


def test_survived_with_no_spec_citation_cannot_trigger_amendment():
    # spec_citation=None means there is nothing to copy, so the rule can
    # never fire — even though the claim itself is a finding elsewhere
    # (Claim.spec_citation is None ⇒ "None is itself a finding", per
    # contract.py, but that is not this gate's concern).
    claims = [_claim("C1", "shape_fit", spec_citation=None)]
    payloads = [_refuter([_verdict("C1", evidence="scripts/anything.py:1")])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "CLEARED"
    assert result.blocking_reasons == []


def test_non_load_bearing_citation_copy_does_not_block():
    # Rule 1 (and therefore the amendment riding on it) is scoped to
    # load_bearing claims only. A non-load-bearing claim whose SURVIVED
    # verdict merely restates its own citation must not block.
    claims = [
        _claim("C1", "shape_fit", spec_citation="scripts/a.py:5"),
        _claim("C2", "premise", load_bearing=False, spec_citation="scripts/b.py:7"),
    ]
    payloads = [_refuter([
        _verdict("C1", evidence="scripts/q.py:99"),          # genuinely independent
        _verdict("C2", evidence="scripts/b.py:7"),            # copies its own citation
    ])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "CLEARED"
    assert result.blocking_reasons == []


# --- fix round 1: casefold normalization ----------------------------------

def test_survived_evidence_citation_copy_with_different_case_blocks():
    # The amendment names normalization explicitly: evidence and spec_citation
    # must be compared casefolded, not byte-for-byte. On a Windows-primary
    # repo, "Scripts/X.py:1" and "scripts/x.py:1" name the same file:line —
    # without casefolding, this differently-cased copy would slip past the
    # rule as if it were independent evidence.
    claims = [_claim("C1", "shape_fit", spec_citation="scripts/X.py:1")]
    payloads = [_refuter([_verdict("C1", evidence="scripts/x.py:1")])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "BLOCKED"
    assert any(
        "C1" in r and "restates" in r and "own citation" in r
        for r in result.blocking_reasons
    ), result.blocking_reasons


# --- fix round 1: rung absorption must not hide behind a producer block --

def test_superstitious_and_under_hardened_trace_reports_both():
    # A trace with no producer AND sitting below its highest applicable rung
    # used to report only the producer block (the rung check was an `elif`
    # on the producer check). The spec's absorption trigger carries no
    # producer precondition, and "absorptions are still reported alongside a
    # block" — both findings must surface from a single pass.
    claims = [_claim("C1", "shape_fit")]
    payloads = [_refuter([_verdict("C1")]),
                _hardening([_trace(producer=None, design_rung=5, highest=1)])]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    assert result.outcome == "BLOCKED"
    assert any("no named producer" in r for r in result.blocking_reasons)
    assert result.absorptions, "the rung absorption must not be hidden by the block"
    assert any("rung 5" in a and "rung 1" in a for a in result.absorptions)


# --- fix round 1: unrecognized spec kind fails loud -----------------------

def test_unrecognized_spec_kind_raises_typed_error():
    # classify_outcome is called with loose components before DesignReviewRun
    # validates anything (SpecKind is a Literal there, not here). A misspelled
    # or invented kind must not silently resolve to "no family required" via
    # dict.get — that would let a defect-shaped spec with no root_cause claim
    # clear the gate on a typo. LOAD_BEARING_FAMILY.get(...) is banned here;
    # deletion of the explicit membership check would make this test fail
    # with a plain None-required pass-through instead of the raise below.
    claims = [_claim("C1", "root_cause")]
    with pytest.raises(SpecKindUndeterminedError, match="not_a_real_kind"):
        classify_outcome(spec_kinds=["not_a_real_kind"], claims=claims,
                         payloads=[_refuter([_verdict("C1")])], converged=[])


def test_docs_kind_still_resolves_without_raising():
    # "docs" is a legal key (mapped to None), so it must NOT hit the
    # unrecognized-kind raise added above — only genuinely unknown strings do.
    claims = [_claim("C1", "premise", load_bearing=False)]
    result = classify_outcome(spec_kinds=["docs"], claims=claims,
                              payloads=[_refuter([_verdict("C1")])], converged=[])
    assert result.outcome == "CLEARED"
