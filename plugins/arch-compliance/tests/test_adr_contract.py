"""Schemas for the adversarial-design-review skill (fail loud, POSIX paths)."""
import json

import pytest
from pydantic import TypeAdapter, ValidationError

from acf.adr.contract import (
    Claim,
    ClaimVerdict,
    CompliancePayload,
    ConvergedFinding,
    ConvergenceCandidateGroup,
    DesignReviewRun,
    DocumentConflict,
    GateResult,
    HardeningPayload,
    MechanismTrace,
    RefuterPayload,
    ResponsibilityRelationship,
    ReviewerPayload,
    SweeperPayload,
)


def _refuter(**overrides):
    payload = {
        "reviewer": "refuter",
        "claim_verdicts": [
            {"id": "C1", "verdict": "REFUTED", "evidence": "scripts/core/x.py:12",
             "reasoning": "the cited block is absent"},
        ],
        "unanchored_findings": [],
        "looked_for_but_did_not_find": ["a seq*10 assignment anywhere under scripts/"],
    }
    payload.update(overrides)
    return payload


# --- POSIX enforcement (§10) -------------------------------------------------

def test_claim_rejects_backslash_citation():
    with pytest.raises(ValidationError, match="POSIX"):
        Claim(id="C1", family="premise", statement="x",
              spec_citation=r"scripts\core\x.py:12", load_bearing=True)


def test_claim_accepts_none_citation():
    claim = Claim(id="C1", family="premise", statement="x",
                  spec_citation=None, load_bearing=True)
    assert claim.spec_citation is None


def test_verdict_rejects_backslash_evidence():
    with pytest.raises(ValidationError, match="POSIX"):
        ClaimVerdict(id="C1", verdict="REFUTED",
                     evidence=r"scripts\core\x.py:12", reasoning="r")


def test_verdict_rejects_backslash_drive_path_in_evidence():
    with pytest.raises(ValidationError, match="POSIX"):
        ClaimVerdict(id="C1", verdict="REFUTED",
                     evidence=r"looked under C:\BookRoot\HistoricMansions\content",
                     reasoning="r")


def test_verdict_rejects_backslash_file_line_among_prose():
    # A Windows file:line buried in prose is still a fabricated-path anchor.
    with pytest.raises(ValidationError, match="POSIX"):
        ClaimVerdict(id="C1", verdict="REFUTED",
                     evidence=r"read scripts/a.py:3 and scripts\core\x.py:12",
                     reasoning="r")


# Free-text evidence quotes the searches a reviewer ran (refuter.md: "execute
# rather than reason"). A regex escape is not a path; rejecting it aborted a
# whole gate run on 2026-10-08 when both refuter dispatches quoted their grep.
@pytest.mark.parametrize("evidence", [
    r"grep 'os\.utime' over scripts/**/*.py: 0 hits; scripts/a/b.py:413",
    r"searched 'utime|st_mtime\s*=' — zero matches; scripts/x/y.py:327",
    r"rg '\d+\.\d+' found scripts/core/z.py:9",
])
def test_verdict_accepts_regex_backslashes_in_evidence(evidence):
    v = ClaimVerdict(id="C12", verdict="SURVIVED", evidence=evidence, reasoning="r")
    assert v.evidence == evidence


def test_verdict_accepts_backtick_quoted_regex_shaped_like_an_anchor():
    # Backtick code spans are as common as quotes in reviewer prose; a quoted
    # regex like `a\.py:3` is not a path.
    v = ClaimVerdict(id="C1", verdict="SURVIVED",
                     evidence=r"pattern `a\.py:3` matched at scripts/core/z.py:9",
                     reasoning="r")
    assert "`a\\.py:3`" in v.evidence


def test_evidence_validation_is_linear_on_backslash_dense_text():
    # Ambiguous character classes around the literal backslash made the
    # file:line regex backtrack polynomially (5000 repeats did not return in 60s).
    import time
    dense = ("a" + "\\") * 20000 + "end; scripts/core/z.py:9"
    start = time.perf_counter()
    ClaimVerdict(id="C1", verdict="SURVIVED", evidence=dense, reasoning="r")
    assert time.perf_counter() - start < 1.0


def test_unanchored_finding_accepts_regex_backslash_evidence():
    from acf.adr.contract import UnanchoredFinding
    f = UnanchoredFinding(summary="s", evidence=r"pattern 'a\.b' at scripts/q.py:1",
                          severity="advisory")
    assert "a\\.b" in f.evidence


def test_unanchored_finding_rejects_backslash_file_line():
    from acf.adr.contract import UnanchoredFinding
    with pytest.raises(ValidationError, match="POSIX"):
        UnanchoredFinding(summary="s", evidence=r"scripts\q.py:1", severity="advisory")


def test_mechanism_trace_rejects_backslash_producer():
    with pytest.raises(ValidationError, match="POSIX"):
        MechanismTrace(mechanism="m", spec_citation=None, invalid_state="s",
                       producer=r"scripts\x.py:1", hardening_rejected_because=None,
                       design_rung=5, highest_applicable_rung=2,
                       repairs_rather_than_refuses=True)


def test_design_review_run_rejects_backslash_spec_path():
    with pytest.raises(ValidationError, match="POSIX"):
        DesignReviewRun(spec_path=r"docs\design\X.md", spec_kinds=["feature"],
                        commit_sha="abc1234", claims=[], payloads=[],
                        converged=[], outcome="CLEARED")


def test_design_review_run_rejects_backslash_commit_sha():
    # commit_sha is PosixStr for symmetry with LedgerRow.commit_sha, which has
    # always been PosixStr: the ledger row is written FROM this run's fields, so a
    # value this model accepted and the ledger refuses is an asymmetry that fails
    # at the wrong layer (after four reviewer dispatches have already been paid
    # for). Same reasoning the branch applied to the other path-bearing fields.
    with pytest.raises(ValidationError, match="POSIX"):
        DesignReviewRun(spec_path="docs/design/X.md", spec_kinds=["feature"],
                        commit_sha=r"abc1234\HEAD", claims=[], payloads=[],
                        converged=[], outcome="CLEARED")


def test_converged_finding_rejects_backslash_evidence():
    with pytest.raises(ValidationError, match="POSIX"):
        ConvergedFinding(summary="s", reviewers=["refuter", "hardening"],
                         evidence=[r"scripts\core\x.py:1"])


def test_convergence_candidate_group_requires_two_distinct_reviewers():
    # Symmetry with ConvergedFinding's identical rule. A candidate group is the
    # INPUT to the controller's sameness adjudication, so a group naming one
    # reviewer twice would present a single reviewer's two findings to the
    # controller as convergence evidence. min_length=2 alone does not catch it —
    # ["refuter", "refuter"] has length 2 — which is why the validator exists and
    # why this test passes a repeat rather than a single-element list.
    with pytest.raises(ValidationError, match="DISTINCT"):
        ConvergenceCandidateGroup(evidence_file="scripts/x.py",
                                  reviewers=["refuter", "refuter"],
                                  summaries=["a", "b"])


# --- refute-by-default (Architectural Contract 3) ---------------------------

def test_survived_requires_a_file_line_the_reviewer_resolved():
    with pytest.raises(ValidationError, match="file:line"):
        ClaimVerdict(id="C1", verdict="SURVIVED",
                     evidence="the spec says so", reasoning="r")


def test_survived_accepts_a_file_line_embedded_in_prose():
    verdict = ClaimVerdict(
        id="C1", verdict="SURVIVED",
        evidence="re-derived via git log; the block is live at scripts/core/x.py:88",
        reasoning="r",
    )
    assert verdict.verdict == "SURVIVED"


def test_survived_rejects_a_prose_section_number_masquerading_as_a_file_line():
    # "3.1:2" matches the OLD [A-Za-z0-9]+ extension class but must not match
    # the tightened one — a section reference is not a file the reviewer resolved.
    with pytest.raises(ValidationError, match="file:line"):
        ClaimVerdict(id="C1", verdict="SURVIVED",
                     evidence="matches the design at section 3.1:2", reasoning="r")


def test_refuted_needs_evidence_but_not_a_line_number():
    verdict = ClaimVerdict(id="C1", verdict="REFUTED",
                           evidence="no such block exists under scripts/",
                           reasoning="grepped the whole tree")
    assert verdict.verdict == "REFUTED"


def test_blank_evidence_is_always_a_violation():
    with pytest.raises(ValidationError, match="evidence"):
        ClaimVerdict(id="C1", verdict="UNPROVEN", evidence="   ", reasoning="r")


# --- silence is not coverage (Architectural Contract 4) ---------------------

def test_both_coverage_fields_empty_is_a_contract_violation():
    with pytest.raises(ValidationError, match="looked_for_but_did_not_find"):
        RefuterPayload(**_refuter(unanchored_findings=[],
                                  looked_for_but_did_not_find=[]))


def test_unanchored_findings_alone_satisfies_coverage():
    payload = RefuterPayload(**_refuter(
        unanchored_findings=[{"summary": "s", "evidence": "scripts/x.py:1",
                              "severity": "blocking"}],
        looked_for_but_did_not_find=[],
    ))
    assert payload.unanchored_findings[0].severity == "blocking"


def test_looked_for_alone_satisfies_coverage():
    payload = RefuterPayload(**_refuter())
    assert payload.unanchored_findings == []


# --- exactly one schema, no partial acceptance (Architectural Contract 5) --

def test_reviewer_payload_forbids_unrecognized_keys():
    with pytest.raises(ValidationError, match="extra_forbidden"):
        HardeningPayload(reviewer="hardening", claim_verdicts=[], unanchored_findings=[],
                         looked_for_but_did_not_find=["x"], mechanism_traces=[],
                         silent_paths=["FABRICATED"], confidence=0.9)


def test_claim_forbids_unrecognized_keys():
    with pytest.raises(ValidationError, match="extra_forbidden"):
        Claim(id="C1", family="premise", statement="x", spec_citation=None,
              load_bearing=True, made_up_field="oops")


# --- per-reviewer required fields (D1: discriminated union) -----------------

def test_sweeper_must_supply_relationships():
    with pytest.raises(ValidationError, match="relationships"):
        SweeperPayload(reviewer="sweeper", claim_verdicts=[],
                       unanchored_findings=[],
                       looked_for_but_did_not_find=["x"])


def test_sweeper_payload_accepts_nested_relationship_and_conflict_models():
    payload = SweeperPayload(
        reviewer="sweeper", claim_verdicts=[], unanchored_findings=[],
        looked_for_but_did_not_find=["x"],
        relationships=[ResponsibilityRelationship(
            new_element="OrderFacade", responsibility="assign book_order",
            existing_site="scripts/core/collection.py:44",
            relationship="PARTIAL_OVERLAP",
            required_resolution="extract a single derive-on-write owner",
            non_merge_justification=None)],
        two_owner_counts={"assign book_order": 5},
        document_conflicts=[DocumentConflict(
            doc_path="docs/design/COLLECTION_RESET_GUARDRAILS.md", doc_line=13,
            contract_quote="a single-writer intent API is disproportionate",
            conflict_kind="contradicts")],
    )
    assert payload.two_owner_counts["assign book_order"] == 5


def test_hardening_must_supply_mechanism_traces():
    with pytest.raises(ValidationError, match="mechanism_traces"):
        HardeningPayload(reviewer="hardening", claim_verdicts=[],
                         unanchored_findings=[],
                         looked_for_but_did_not_find=["x"])


def test_compliance_must_supply_unstated_mandates():
    with pytest.raises(ValidationError, match="unstated_mandates"):
        CompliancePayload(reviewer="compliance", claim_verdicts=[],
                          unanchored_findings=[],
                          looked_for_but_did_not_find=["x"])


def test_compliance_accepts_an_empty_unstated_mandate_list():
    payload = CompliancePayload(reviewer="compliance", claim_verdicts=[],
                                unanchored_findings=[],
                                looked_for_but_did_not_find=["§11 surfaces"],
                                unstated_mandates=[])
    assert payload.unstated_mandates == []


def test_reviewer_literal_is_pinned_per_class():
    with pytest.raises(ValidationError, match="reviewer"):
        RefuterPayload(**_refuter(reviewer="sweeper"))


# --- discriminated union round-trips through JSON (D1) ----------------------

def test_reviewer_payload_round_trips_refuter_from_json():
    payload = TypeAdapter(ReviewerPayload).validate_json(json.dumps(_refuter()))
    assert isinstance(payload, RefuterPayload)


def test_reviewer_payload_round_trips_compliance_from_json():
    text = json.dumps({
        "reviewer": "compliance", "claim_verdicts": [], "unanchored_findings": [],
        "looked_for_but_did_not_find": ["§11 surfaces"], "unstated_mandates": ["§11"],
    })
    payload = TypeAdapter(ReviewerPayload).validate_json(text)
    assert isinstance(payload, CompliancePayload)


def test_reviewer_payload_round_trips_sweeper_from_json():
    text = json.dumps({
        "reviewer": "sweeper", "claim_verdicts": [], "unanchored_findings": [],
        "looked_for_but_did_not_find": ["x"],
        "relationships": [{
            "new_element": "OrderFacade", "responsibility": "assign book_order",
            "existing_site": "scripts/core/collection.py:44",
            "relationship": "PARTIAL_OVERLAP",
            "required_resolution": "extract a single derive-on-write owner",
            "non_merge_justification": None,
        }],
        "two_owner_counts": {"assign book_order": 5},
        "document_conflicts": [],
    })
    payload = TypeAdapter(ReviewerPayload).validate_json(text)
    assert isinstance(payload, SweeperPayload)


def test_reviewer_payload_round_trips_hardening_from_json():
    text = json.dumps({
        "reviewer": "hardening", "claim_verdicts": [], "unanchored_findings": [],
        "looked_for_but_did_not_find": ["x"],
        "mechanism_traces": [{
            "mechanism": "m", "spec_citation": None, "invalid_state": "s",
            "producer": "scripts/x.py:1", "hardening_rejected_because": None,
            "design_rung": 3, "highest_applicable_rung": 3,
            "repairs_rather_than_refuses": False,
        }],
    })
    payload = TypeAdapter(ReviewerPayload).validate_json(text)
    assert isinstance(payload, HardeningPayload)


def test_reviewer_payload_rejects_discriminator_body_mismatch():
    # reviewer: "sweeper" but only the base fields — no sweeper-only extras.
    text = json.dumps({
        "reviewer": "sweeper", "claim_verdicts": [], "unanchored_findings": [],
        "looked_for_but_did_not_find": ["x"],
    })
    with pytest.raises(ValidationError):
        TypeAdapter(ReviewerPayload).validate_json(text)


# --- derived silent_paths (D7) ---------------------------------------------

def test_silent_paths_is_derived_from_the_traces():
    payload = HardeningPayload(
        reviewer="hardening", claim_verdicts=[], unanchored_findings=[],
        looked_for_but_did_not_find=["x"],
        mechanism_traces=[
            MechanismTrace(mechanism="normalize-on-validate", spec_citation=None,
                           invalid_state="book_order has gaps", producer=None,
                           hardening_rejected_because=None, design_rung=5,
                           highest_applicable_rung=1,
                           repairs_rather_than_refuses=True),
            MechanismTrace(mechanism="strict load", spec_citation=None,
                           invalid_state="book_order missing", producer="scripts/x.py:9",
                           hardening_rejected_because="external boundary",
                           design_rung=3, highest_applicable_rung=3,
                           repairs_rather_than_refuses=False),
        ],
    )
    assert payload.silent_paths == ["normalize-on-validate"]


# --- rung bounds -----------------------------------------------------------

@pytest.mark.parametrize("rung", [0, 6])
def test_rungs_are_bounded_one_to_five(rung: int):
    with pytest.raises(ValidationError, match="design_rung"):
        MechanismTrace(mechanism="m", spec_citation=None, invalid_state="s",
                       producer="scripts/x.py:1", hardening_rejected_because=None,
                       design_rung=rung, highest_applicable_rung=1,
                       repairs_rather_than_refuses=False)


@pytest.mark.parametrize("rung", [0, 6])
def test_highest_applicable_rung_is_bounded_one_to_five(rung: int):
    with pytest.raises(ValidationError, match="highest_applicable_rung"):
        MechanismTrace(mechanism="m", spec_citation=None, invalid_state="s",
                       producer="scripts/x.py:1", hardening_rejected_because=None,
                       design_rung=1, highest_applicable_rung=rung,
                       repairs_rather_than_refuses=False)


# --- convergence + gate result --------------------------------------------

def test_converged_finding_requires_at_least_two_reviewers():
    with pytest.raises(ValidationError, match="reviewers"):
        ConvergedFinding(summary="s", reviewers=["refuter"],
                         evidence=["scripts/x.py:1"])


def test_converged_finding_accepts_two_reviewers():
    finding = ConvergedFinding(summary="s", reviewers=["refuter", "hardening"],
                               evidence=["scripts/x.py:1", "scripts/y.py:2"])
    assert len(finding.reviewers) == 2


def test_converged_finding_rejects_duplicate_reviewer():
    with pytest.raises(ValidationError, match="DISTINCT"):
        ConvergedFinding(summary="s", reviewers=["refuter", "refuter"],
                         evidence=["scripts/x.py:1", "scripts/y.py:2"])


def test_converged_finding_rejects_unknown_reviewer_name():
    with pytest.raises(ValidationError):
        ConvergedFinding(summary="s", reviewers=["bob", "carol"],
                         evidence=["scripts/x.py:1", "scripts/y.py:2"])


def test_gate_result_defaults_are_empty_lists():
    result = GateResult(outcome="CLEARED")
    assert result.blocking_reasons == []
    assert result.absorptions == []


def test_design_review_run_requires_at_least_one_spec_kind():
    with pytest.raises(ValidationError, match="spec_kinds"):
        DesignReviewRun(spec_path="docs/design/X.md", spec_kinds=[],
                        commit_sha="abc1234", claims=[], payloads=[],
                        converged=[], outcome="CLEARED")


# --- revision disposition (M3) -----------------------------------------------

def _disposition_claim(**overrides):
    fields = dict(id="C1", family="premise", statement="x",
                  spec_citation="scripts/x.py:1", load_bearing=True)
    fields.update(overrides)
    return Claim(**fields)


def test_claim_disposition_defaults_to_none():
    # First runs carry no disposition; None must be the constructed default so
    # every existing call site is unaffected.
    assert _disposition_claim().revision_disposition is None


def test_claim_disposition_accepts_carried_and_delta():
    for value in ("carried", "delta"):
        assert _disposition_claim(
            revision_disposition=value).revision_disposition == value


def test_claim_disposition_rejects_unknown_string():
    with pytest.raises(ValidationError):
        _disposition_claim(revision_disposition="modified")
