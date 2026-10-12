"""Deterministic convergence candidate grouping (plan decision D2)."""
from acf.adr.contract import (
    ClaimVerdict,
    HardeningPayload,
    MechanismTrace,
    RefuterPayload,
    SweeperPayload,
    UnanchoredFinding,
)
from acf.adr.convergence import (
    evidence_file,
    group_convergence_candidates,
)


def _finding(summary, evidence, severity="important"):
    return UnanchoredFinding(summary=summary, evidence=evidence, severity=severity)


def _refuter(findings=None, verdicts=None):
    return RefuterPayload(
        reviewer="refuter", claim_verdicts=verdicts or [],
        unanchored_findings=findings or [],
        looked_for_but_did_not_find=["x"],
    )


def _sweeper(findings=None):
    return SweeperPayload(
        reviewer="sweeper", claim_verdicts=[], unanchored_findings=findings or [],
        looked_for_but_did_not_find=["x"], relationships=[],
        two_owner_counts={}, document_conflicts=[],
    )


def _hardening(findings=None):
    return HardeningPayload(
        reviewer="hardening", claim_verdicts=[], unanchored_findings=findings or [],
        looked_for_but_did_not_find=["x"],
        mechanism_traces=[MechanismTrace(
            mechanism="m", spec_citation=None, invalid_state="s",
            producer="scripts/x.py:1", hardening_rejected_because=None,
            design_rung=2, highest_applicable_rung=2,
            repairs_rather_than_refuses=False)],
    )


# --- evidence_file -------------------------------------------------------

def test_evidence_file_takes_the_token_before_the_first_colon():
    assert evidence_file("scripts/core/x.py:12") == "scripts/core/x.py"


def test_evidence_file_handles_a_line_range():
    assert evidence_file("docs/design/A.md:13-15") == "docs/design/a.md"


def test_evidence_file_case_folds():
    assert evidence_file("Scripts/Core/X.py:1") == "scripts/core/x.py"


def test_evidence_file_extracts_from_surrounding_prose():
    assert evidence_file("re-derived via git log at scripts/y.py:9 — absent") == "scripts/y.py"


def test_evidence_file_returns_none_when_no_file_token_is_present():
    assert evidence_file("no such block exists anywhere") is None


def test_evidence_file_does_not_mistake_a_prose_section_reference_for_a_file():
    # contract.py's _FILE_LINE_RE deliberately restricts the extension group to
    # [A-Za-z]+ (not [A-Za-z0-9]+) so that a prose reference like "section
    # 3.1:2" cannot be mistaken for a file named "3" with extension "1". This
    # module extracts a path (rather than merely detecting one), so the same
    # false positive would bucket an unrelated finding under a fabricated file
    # named "3" — prove that does not happen.
    assert evidence_file("see section 3.1:2 of the spec for the rule") is None


# --- grouping ------------------------------------------------------------

def test_two_reviewers_on_one_file_converge():
    payloads = [
        _refuter([_finding("migration cannot read its inputs", "scripts/mig.py:40")]),
        _sweeper([_finding("two owners of this write", "scripts/mig.py:44")]),
    ]
    groups = group_convergence_candidates(payloads)
    assert len(groups) == 1
    assert groups[0].evidence_file == "scripts/mig.py"
    assert sorted(groups[0].reviewers) == ["refuter", "sweeper"]
    assert len(groups[0].summaries) == 2


def test_one_reviewer_alone_is_not_convergence():
    payloads = [_refuter([_finding("a", "scripts/mig.py:40"),
                          _finding("b", "scripts/mig.py:44")])]
    assert group_convergence_candidates(payloads) == []


def test_three_reviewers_group_together():
    payloads = [
        _refuter([_finding("a", "scripts/mig.py:1")]),
        _sweeper([_finding("b", "scripts/mig.py:2")]),
        _hardening([_finding("c", "scripts/mig.py:3")]),
    ]
    groups = group_convergence_candidates(payloads)
    assert len(groups) == 1
    assert len(groups[0].reviewers) == 3


def test_adverse_claim_verdicts_participate_in_grouping():
    payloads = [
        _refuter(verdicts=[ClaimVerdict(id="C1", verdict="REFUTED",
                                        evidence="scripts/mig.py:40",
                                        reasoning="absent")]),
        _sweeper([_finding("two owners", "scripts/mig.py:44")]),
    ]
    groups = group_convergence_candidates(payloads)
    assert len(groups) == 1
    assert sorted(groups[0].reviewers) == ["refuter", "sweeper"]


def test_survived_verdicts_do_not_participate():
    payloads = [
        _refuter(verdicts=[ClaimVerdict(id="C1", verdict="SURVIVED",
                                        evidence="scripts/mig.py:40",
                                        reasoning="confirmed")]),
        _sweeper([_finding("two owners", "scripts/mig.py:44")]),
    ]
    assert group_convergence_candidates(payloads) == []


def test_findings_without_a_file_token_are_excluded():
    payloads = [
        _refuter([_finding("a", "nothing anywhere")]),
        _sweeper([_finding("b", "also nothing")]),
    ]
    assert group_convergence_candidates(payloads) == []


def test_different_files_do_not_converge():
    payloads = [
        _refuter([_finding("a", "scripts/one.py:1")]),
        _sweeper([_finding("b", "scripts/two.py:1")]),
    ]
    assert group_convergence_candidates(payloads) == []


def test_groups_are_ordered_by_reviewer_count_then_file():
    payloads = [
        _refuter([_finding("a", "scripts/bbb.py:1"), _finding("c", "scripts/aaa.py:1")]),
        _sweeper([_finding("b", "scripts/bbb.py:2"), _finding("d", "scripts/aaa.py:2")]),
        _hardening([_finding("e", "scripts/bbb.py:3")]),
    ]
    groups = group_convergence_candidates(payloads)
    assert [g.evidence_file for g in groups] == ["scripts/bbb.py", "scripts/aaa.py"]
    assert [len(g.reviewers) for g in groups] == [3, 2]


def test_a_reviewer_is_counted_once_per_group():
    payloads = [
        _refuter([_finding("a", "scripts/mig.py:1"), _finding("b", "scripts/mig.py:2")]),
        _sweeper([_finding("c", "scripts/mig.py:3")]),
    ]
    groups = group_convergence_candidates(payloads)
    assert sorted(groups[0].reviewers) == ["refuter", "sweeper"]
    assert len(groups[0].summaries) == 3


def test_ordering_tiebreak_is_by_file_when_reviewer_counts_are_equal():
    # test_groups_are_ordered_by_reviewer_count_then_file uses 3-reviewer
    # bbb.py vs. 2-reviewer aaa.py, so the primary key (count) alone already
    # determines that order — the secondary key (file) is never exercised.
    # Force a genuine tie on the primary key so only the file tiebreak can
    # decide the order, and check the alphabetically-earlier file wins.
    payloads = [
        _refuter([_finding("a", "scripts/zzz.py:1"), _finding("c", "scripts/aaa.py:1")]),
        _sweeper([_finding("b", "scripts/zzz.py:2"), _finding("d", "scripts/aaa.py:2")]),
    ]
    groups = group_convergence_candidates(payloads)
    assert [len(g.reviewers) for g in groups] == [2, 2]
    assert [g.evidence_file for g in groups] == ["scripts/aaa.py", "scripts/zzz.py"]


def test_same_reviewer_unanchored_finding_and_adverse_verdict_count_once():
    # The once-per-reviewer dedup (test_a_reviewer_is_counted_once_per_group)
    # is only proven within a single adverse-signal type there (two
    # UnanchoredFindings). Prove it also holds when one reviewer contributes
    # BOTH an UnanchoredFinding and a non-SURVIVED ClaimVerdict for the same
    # file — both feed the same "add" call in the implementation, but that is
    # exactly the kind of internal detail a passing test should not assume.
    payloads = [
        _refuter(
            findings=[_finding("a", "scripts/mig.py:1")],
            verdicts=[ClaimVerdict(id="C1", verdict="REFUTED",
                                    evidence="scripts/mig.py:2",
                                    reasoning="absent")],
        ),
        _sweeper([_finding("b", "scripts/mig.py:3")]),
    ]
    groups = group_convergence_candidates(payloads)
    assert len(groups) == 1
    group = groups[0]
    assert sorted(group.reviewers) == ["refuter", "sweeper"]
    assert len(group.reviewers) == len(set(group.reviewers))
    assert len(group.summaries) == 3


def test_reviewers_list_has_no_duplicate_entries():
    # Addition 2. ConvergenceCandidateGroup.reviewers carries min_length=2 but,
    # unlike ConvergedFinding.reviewers, no distinctness validator. The ruling
    # was that this is safe because THIS module's producer builds the list from
    # dictionary keys, so it cannot emit a duplicate name — prove that property
    # directly (not merely via a sorted-list equality that would also pass if
    # duplicates happened to sort predictably).
    payloads = [
        _refuter([_finding("a", "scripts/mig.py:1"),
                  _finding("b", "scripts/mig.py:2"),
                  _finding("c", "scripts/mig.py:3")]),
        _sweeper([_finding("d", "scripts/mig.py:4")]),
    ]
    groups = group_convergence_candidates(payloads)
    assert len(groups) == 1
    group = groups[0]
    assert len(group.reviewers) == len(set(group.reviewers))
    assert sorted(group.reviewers) == ["refuter", "sweeper"]


def test_grouping_is_deterministic_across_payload_order():
    a = _refuter([_finding("a", "scripts/mig.py:1")])
    b = _sweeper([_finding("b", "scripts/mig.py:2")])
    assert group_convergence_candidates([a, b]) == group_convergence_candidates([b, a])
