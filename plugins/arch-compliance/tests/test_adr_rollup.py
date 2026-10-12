"""Terminal roll-up formatting for an adversarial design review run."""
from acf.adr.contract import (
    Claim,
    ClaimVerdict,
    CompliancePayload,
    ConvergedFinding,
    DesignReviewRun,
    DocumentConflict,
    GateResult,
    HardeningPayload,
    MechanismTrace,
    RefuterPayload,
    SweeperPayload,
    UnanchoredFinding,
)
from acf.adr.rollup import format_rollup


def _run(**overrides):
    payload = RefuterPayload(
        reviewer="refuter",
        claim_verdicts=[ClaimVerdict(id="C1", verdict="REFUTED",
                                     evidence="scripts/mig.py:40",
                                     reasoning="the cited block is absent")],
        unanchored_findings=[UnanchoredFinding(
            summary="migration cannot read its own inputs",
            evidence="scripts/mig.py:44", severity="blocking")],
        looked_for_but_did_not_find=["a seq*10 block under scripts/"],
    )
    fields = {
        "spec_path": "docs/design/TOPIC.md",
        "spec_kinds": ["defect"],
        "commit_sha": "03fdaa83",
        "claims": [Claim(id="C1", family="root_cause", statement="s",
                         spec_citation="scripts/mig.py:40", load_bearing=True)],
        "payloads": [payload],
        "converged": [],
        "outcome": "BLOCKED",
    }
    fields.update(overrides)
    return DesignReviewRun(**fields)


def _sweeper(two_owner_counts, document_conflicts=None):
    return SweeperPayload(
        reviewer="sweeper", claim_verdicts=[], unanchored_findings=[],
        looked_for_but_did_not_find=["a second assigner"], relationships=[],
        two_owner_counts=two_owner_counts,
        document_conflicts=document_conflicts if document_conflicts is not None else [],
    )


def _compliance(unstated_mandates):
    return CompliancePayload(
        reviewer="compliance", claim_verdicts=[], unanchored_findings=[],
        looked_for_but_did_not_find=["§12: no format token reaches Stage 1"],
        unstated_mandates=unstated_mandates,
    )


def test_header_names_the_spec_outcome_and_commit():
    text = format_rollup(_run(), GateResult(outcome="BLOCKED",
                                            blocking_reasons=["C1 is REFUTED"]))
    assert "docs/design/TOPIC.md" in text
    assert "BLOCKED" in text
    assert "03fdaa83" in text


def test_reviewer_count_and_claim_count_are_reported():
    text = format_rollup(_run(), GateResult(outcome="BLOCKED"))
    assert "1 reviewer" in text
    assert "1 claim" in text


def test_converged_findings_print_before_blocking_reasons():
    converged = [ConvergedFinding(summary="migration read-path deadlock",
                                  reviewers=["refuter", "sweeper", "hardening"],
                                  evidence=["scripts/mig.py:40"])]
    text = format_rollup(_run(converged=converged),
                         GateResult(outcome="BLOCKED", blocking_reasons=["C1 is REFUTED"]))
    assert text.index("migration read-path deadlock") < text.index("C1 is REFUTED")
    assert "3 reviewers" in text


def test_converged_section_states_when_there_is_none():
    text = format_rollup(_run(), GateResult(outcome="CLEARED"))
    assert "No convergence" in text


def test_blocking_reasons_are_listed():
    result = GateResult(outcome="BLOCKED",
                        blocking_reasons=["C1 is REFUTED", "no named producer for 'x'"])
    text = format_rollup(_run(), result)
    assert "no named producer" in text


def test_absorptions_are_listed_under_their_own_heading():
    result = GateResult(outcome="CLEARED_WITH_ABSORPTIONS",
                        absorptions=["PARTIAL_OVERLAP: 'E' shares R"])
    text = format_rollup(_run(outcome="CLEARED_WITH_ABSORPTIONS"), result)
    assert "Absorptions" in text
    assert "PARTIAL_OVERLAP" in text


def test_cleared_run_says_so_plainly():
    text = format_rollup(_run(outcome="CLEARED"), GateResult(outcome="CLEARED"))
    assert "No blocking findings" in text
    assert "no absorptions" in text.lower()


def test_two_owner_counts_of_two_or_more_are_surfaced():
    # 2 is the actual boundary (">= 2"), so pin it directly rather than only
    # exercising a count comfortably above it. A responsibility sitting at
    # exactly 1 (a single, unambiguous owner) must be excluded — if the
    # filter were weakened to ">= 1" or dropped entirely, "assign page" would
    # wrongly appear and this test would catch it.
    run = _run(
        payloads=[_sweeper({"assign book_order": 2, "assign page": 1})],
        claims=[], outcome="CLEARED",
    )
    text = format_rollup(run, GateResult(outcome="CLEARED"))
    assert "assign book_order" in text
    assert "assign page" not in text


def test_unstated_mandates_are_surfaced_when_present():
    # §11/§12/etc. are checked by NEITHER of the gate's five blocking triggers
    # nor its four absorption triggers (gate.py never imports CompliancePayload
    # at all) — this roll-up section is the ONLY place an unstated mandate ever
    # reaches the author. Assert on the header text format_rollup itself
    # constructs ("Unstated governing mandates:"), not merely the payload's
    # own string, so a section that silently stopped rendering would still
    # fail this test even if the raw mandate text happened to appear elsewhere.
    payload = _compliance(["§11 — index.yml write bypasses the metadata façade"])
    run = _run(payloads=[payload], claims=[], outcome="CLEARED_WITH_ABSORPTIONS")
    text = format_rollup(run, GateResult(outcome="CLEARED_WITH_ABSORPTIONS"))
    assert "Unstated governing mandates:" in text
    assert "§11 — index.yml write bypasses the metadata façade" in text


def test_unstated_mandates_section_is_absent_when_empty():
    # The mirror case: an empty list must not print the header at all — a
    # CLEARED spec that named every governing section gets nothing printed,
    # same rule as the two-owner block.
    payload = _compliance([])
    run = _run(payloads=[payload], claims=[], outcome="CLEARED")
    text = format_rollup(run, GateResult(outcome="CLEARED"))
    assert "Unstated governing mandates:" not in text


def test_document_conflicts_are_surfaced_when_present():
    # document_conflicts is likewise consulted by neither gate.py trigger —
    # a design rejected on the record and re-proposed must not reach CLEARED
    # silently. The assertion pins the exact "doc_path:doc_line (kind)" line
    # format_rollup constructs by joining three separate model fields — that
    # joined string does not exist anywhere in the payload itself, so this
    # proves the roll-up performed the join, not merely echoed a field.
    conflict = DocumentConflict(
        doc_path="docs/design/ORDERING.md", doc_line=42,
        contract_quote="derive-on-write is the sole write path",
        conflict_kind="contradicts",
    )
    payload = _sweeper({}, document_conflicts=[conflict])
    run = _run(payloads=[payload], claims=[], outcome="CLEARED_WITH_ABSORPTIONS")
    text = format_rollup(run, GateResult(outcome="CLEARED_WITH_ABSORPTIONS"))
    assert "Document conflicts:" in text
    assert "docs/design/ORDERING.md:42 (contradicts)" in text


def test_document_conflicts_section_is_absent_when_empty():
    payload = _sweeper({}, document_conflicts=[])
    run = _run(payloads=[payload], claims=[], outcome="CLEARED")
    text = format_rollup(run, GateResult(outcome="CLEARED"))
    assert "Document conflicts:" not in text


def test_next_step_names_the_gate_consequence():
    # All three _NEXT_STEP values contain "writing-plans", so asserting only
    # that substring would still pass even if the outcome->message mapping
    # were scrambled (e.g. a hardcoded CLEARED message emitted regardless of
    # the real outcome) — the worst failure mode for this function: telling
    # a blocked author to proceed. Pin each outcome by wording unique to it,
    # and pin the negation explicitly: BLOCKED must carry it, the other two
    # must not.
    blocked = format_rollup(_run(), GateResult(outcome="BLOCKED",
                                               blocking_reasons=["C1 is REFUTED"]))
    assert "do not proceed" in blocked

    absorbed = format_rollup(
        _run(outcome="CLEARED_WITH_ABSORPTIONS"),
        GateResult(outcome="CLEARED_WITH_ABSORPTIONS",
                   absorptions=["PARTIAL_OVERLAP: 'E' shares R"]),
    )
    assert "fold the findings below into the spec body" in absorbed
    assert "do not proceed" not in absorbed

    cleared = format_rollup(_run(outcome="CLEARED"), GateResult(outcome="CLEARED"))
    assert "proceed to writing-plans" in cleared
    assert "do not proceed" not in cleared


def test_no_header_line_when_cleared():
    # format_rollup does not mint the spec's provenance header (the
    # "**Adversarial review:** vN — <date>, ..." line pasted into the spec).
    # DesignReviewRun carries neither a version nor a date, so only the
    # controller — which holds both — can construct that line; this
    # roll-up's job is the terminal summary only. Pinned per outcome (this
    # test, plus the two below) so the ownership boundary stays guarded
    # rather than merely un-asserted.
    text = format_rollup(_run(outcome="CLEARED"), GateResult(outcome="CLEARED"))
    assert "**Adversarial review:**" not in text


def test_no_header_line_when_cleared_with_absorptions():
    text = format_rollup(
        _run(outcome="CLEARED_WITH_ABSORPTIONS"),
        GateResult(outcome="CLEARED_WITH_ABSORPTIONS",
                   absorptions=["PARTIAL_OVERLAP: 'E' shares R"]),
    )
    assert "**Adversarial review:**" not in text


def test_no_header_line_when_blocked():
    text = format_rollup(_run(), GateResult(outcome="BLOCKED",
                                             blocking_reasons=["C1 is REFUTED"]))
    assert "**Adversarial review:**" not in text


def test_rollup_emits_no_backslash_when_no_input_field_carries_one():
    # Renamed from test_rollup_never_emits_backslashes, which overstated what is
    # true now that the whole-text scan is gone: the roll-up adds no backslash of
    # its own, but it faithfully passes through one a reviewer put in a prose
    # field (see the two tests below, which is the intended behavior). This still
    # guards the roll-up's OWN template text — path fields are PosixStr-validated
    # upstream, so with clean inputs the output must be clean.
    text = format_rollup(_run(), GateResult(outcome="BLOCKED",
                                             blocking_reasons=["C1 is REFUTED"]))
    assert "\\" not in text


def test_zero_reviewers_and_no_convergence_render_without_raising():
    # The schema permits an empty payloads list and an empty converged list.
    # format_rollup must render this shape without raising, and the
    # pluralization at zero must read "0 reviewers" (plural), not the
    # grammatically wrong "0 reviewer".
    run = _run(payloads=[], claims=[], outcome="CLEARED")
    text = format_rollup(run, GateResult(outcome="CLEARED"))
    assert "0 reviewers" in text
    assert "No convergence" in text


def test_backslash_in_a_gate_reason_renders_instead_of_raising():
    # Replaces test_backslash_in_a_gate_reason_fails_loud, whose intent has been
    # inverted deliberately, not deleted. The old whole-text scan aborted the run
    # on ANY backslash, but path fields are already PosixStr-validated at
    # construction — the scan could only ever fire on a *prose* field, where a
    # backslash is legitimate content. A blocking reason quoting a Windows path
    # as the defect it is reporting must still reach the author: the caller prints
    # the roll-up before appending the ledger row, so raising here cost both.
    result = GateResult(outcome="BLOCKED", blocking_reasons=[r"scripts\mig.py is wrong"])
    text = format_rollup(_run(), result)
    assert r"scripts\mig.py is wrong" in text


def test_a_reviewer_quoting_a_regex_in_reasoning_renders_intact():
    # The executed failure from the whole-branch review: a refuter adjudicating a
    # claim about this codebase's own file:line regex cannot state its reasoning
    # without a backslash. The gate correctly returns BLOCKED; under the old scan
    # format_rollup then raised, so the run produced no roll-up AND no ledger row.
    reasoning = r"the regex is \d+ not \w+, and its path class is [^\s:\\]+"
    payload = RefuterPayload(
        reviewer="refuter",
        claim_verdicts=[ClaimVerdict(id="C1", verdict="REFUTED",
                                     evidence="scripts/core/adversarial_design/contract.py:47",
                                     reasoning=reasoning)],
        unanchored_findings=[],
        looked_for_but_did_not_find=["a second file:line expression"],
    )
    run = _run(payloads=[payload])
    text = format_rollup(run, GateResult(outcome="BLOCKED",
                                         blocking_reasons=[f"C1 is REFUTED: {reasoning}"]))
    # Byte-intact, not merely "did not raise" — a repair-by-normalization fix
    # (stripping or doubling the backslashes) would also stop the raise while
    # silently corrupting the regex the reviewer is reporting.
    assert reasoning in text


def test_document_conflict_quote_is_printed_truncated():
    # The quote is the part that makes "previously rejected on the record"
    # actionable; doc_path:line alone only says something over there disagrees.
    short = DocumentConflict(
        doc_path="docs/design/ORDERING.md", doc_line=42,
        contract_quote="derive-on-write is the sole write path",
        conflict_kind="contradicts",
    )
    text = format_rollup(
        _run(payloads=[_sweeper({}, document_conflicts=[short])], claims=[],
             outcome="CLEARED_WITH_ABSORPTIONS"),
        GateResult(outcome="CLEARED_WITH_ABSORPTIONS"),
    )
    assert '"derive-on-write is the sole write path"' in text

    # And a long one is elided rather than blowing the one-screen budget: assert
    # the head survives and the tail does NOT, so a no-op _truncate would fail.
    long_quote = "A" * 200 + "TAIL"
    text = format_rollup(
        _run(payloads=[_sweeper({}, document_conflicts=[DocumentConflict(
            doc_path="docs/design/ORDERING.md", doc_line=9,
            contract_quote=long_quote, conflict_kind="restates")])],
            claims=[], outcome="CLEARED_WITH_ABSORPTIONS"),
        GateResult(outcome="CLEARED_WITH_ABSORPTIONS"),
    )
    assert "..." in text
    assert "TAIL" not in text


def test_silent_repair_mechanisms_are_surfaced_when_present():
    # The spec: a mechanism that repairs rather than refuses "is flagged
    # regardless of rung". gate.py has no trigger for repairs_rather_than_refuses
    # (it is none of the five blocking or four absorption triggers, and the
    # under-hardening absorption keys on rung distance, which this trace does not
    # trip — design_rung == highest_applicable_rung below, deliberately). So this
    # section is the only path from the flag to the author. Assert on the header
    # the roll-up itself constructs, not merely the mechanism name, so a section
    # that stopped rendering still fails even if the name appeared elsewhere.
    payload = HardeningPayload(
        reviewer="hardening", claim_verdicts=[], unanchored_findings=[],
        looked_for_but_did_not_find=["a rung-1 encoding of the invalid state"],
        mechanism_traces=[MechanismTrace(
            mechanism="self-heal the missing index.yml key",
            spec_citation="docs/design/TOPIC.md:12",
            invalid_state="index.yml lacks book_order",
            producer="scripts/mig.py:88",
            hardening_rejected_because=None,
            design_rung=3, highest_applicable_rung=3,
            repairs_rather_than_refuses=True,
        )],
    )
    run = _run(payloads=[payload], claims=[], outcome="CLEARED")
    text = format_rollup(run, GateResult(outcome="CLEARED"))
    assert "Mechanisms that repair rather than refuse (failure by silence):" in text
    assert "self-heal the missing index.yml key" in text


def test_silent_repair_section_is_absent_when_no_mechanism_repairs():
    # Mirror case, and the one that proves the section is derived from the flag
    # rather than printed for every hardening payload: same trace with
    # repairs_rather_than_refuses=False must print no header at all.
    payload = HardeningPayload(
        reviewer="hardening", claim_verdicts=[], unanchored_findings=[],
        looked_for_but_did_not_find=["a rung-1 encoding of the invalid state"],
        mechanism_traces=[MechanismTrace(
            mechanism="refuse the missing index.yml key",
            spec_citation="docs/design/TOPIC.md:12",
            invalid_state="index.yml lacks book_order",
            producer="scripts/mig.py:88",
            hardening_rejected_because=None,
            design_rung=3, highest_applicable_rung=3,
            repairs_rather_than_refuses=False,
        )],
    )
    run = _run(payloads=[payload], claims=[], outcome="CLEARED")
    text = format_rollup(run, GateResult(outcome="CLEARED"))
    assert "repair rather than refuse" not in text
