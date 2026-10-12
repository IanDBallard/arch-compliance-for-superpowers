"""The run-detail sidecar: a review's findings must outlive the run that made them.

Provenance. Three times on 2026-08-11 a completed review's findings were nearly
or actually lost while its ledger row survived:

1. The v4 backfill of ``absorbed``/``rejected`` had to be *reconstructed from the
   spec's own account of itself*, because no payload archive existed — and that
   reconstruction inherited an error (a §14 citation recorded as absorbed that
   had never been applied), overstating absorbed by one.
2. The v6 run wrote its detail to gitignored ``.claude/tmp/``.
3. ``architecture_review`` has written a ``_last_run.json`` sidecar since it
   shipped; ``adversarial_design`` never did.

The ledger records *that* a review happened and what it cost. Only the detail
records *what it said*, and ``absorbed``/``rejected`` cannot be adjudicated
against counts.
"""
from __future__ import annotations

import pytest

from acf.adr.contract import (
    Claim,
    ClaimVerdict,
    DesignReviewRun,
    RefuterPayload,
    UnanchoredFinding,
)
from acf.adr.gate import classify_outcome
from acf.adr.run_detail import (
    render_run_detail,
    run_detail_path,
    write_run_detail,
)
from acf.exceptions import RunDetailWriteError


def _run(outcome="BLOCKED"):
    claims = [
        Claim(id="C1", family="root_cause", statement="X causes Y",
              spec_citation="scripts/x.py:1", load_bearing=True),
    ]
    payloads = [
        RefuterPayload(
            reviewer="refuter",
            claim_verdicts=[ClaimVerdict(
                id="C1", verdict="REFUTED",
                evidence="scripts/q.py:42",
                reasoning="Re-derived independently; the cited mechanism is absent.",
            )],
            unanchored_findings=[UnanchoredFinding(
                summary="A stale citation the claim list never covered",
                evidence="scripts/z.py:7",
                severity="important",
            )],
            looked_for_but_did_not_find=["a second producer"],
        ),
    ]
    result = classify_outcome(spec_kinds=["defect"], claims=claims,
                              payloads=payloads, converged=[])
    run = DesignReviewRun(
        spec_path="docs/design/SOME_SPEC.md", spec_kinds=["defect"],
        commit_sha="a" * 40, claims=claims, payloads=payloads,
        converged=[], outcome=result.outcome,
    )
    return run, result


def test_detail_carries_what_the_ledger_cannot():
    # The whole point: verdict, evidence, reasoning and unanchored findings —
    # none of which the counts-only ledger row preserves.
    run, result = _run()
    text = render_run_detail(run, result)
    assert "C1" in text
    assert "REFUTED" in text
    assert "scripts/q.py:42" in text, "evidence must survive"
    assert "Re-derived independently" in text, "reasoning must survive"
    assert "A stale citation" in text, "unanchored findings must survive"
    assert "a second producer" in text, "looked-for-but-did-not-find must survive"


def test_detail_records_the_run_identity_for_ledger_matching():
    # A detail file that cannot be matched to its ledger row is an orphan:
    # amendments key on spec_path + commit_sha.
    run, result = _run()
    text = render_run_detail(run, result)
    assert "docs/design/SOME_SPEC.md" in text
    assert "a" * 40 in text
    assert "BLOCKED" in text


def test_detail_path_is_posix_and_lands_under_the_tracked_runs_dir(tmp_path):
    # §10, and "tracked" is the requirement that failed at v6 — .claude/tmp is
    # gitignored, docs/reviews/adr_runs is not.
    path = run_detail_path("docs/design/SOME_SPEC.md", version=6,
                           date="2026-08-11", runs_dir=tmp_path)
    assert "\\" not in path.as_posix()
    assert path.name == "SOME_SPEC_v6_2026-08-11.md"


def test_write_creates_parent_and_round_trips(tmp_path):
    run, result = _run()
    path = tmp_path / "nested" / "detail.md"
    write_run_detail(run, result, path)
    assert path.read_text(encoding="utf-8") == render_run_detail(run, result)


def test_write_fails_loud_rather_than_skipping(tmp_path):
    # §3: an unwritable sidecar aborts. Silently skipping it would reproduce
    # exactly the v6 outcome (a ledger row whose findings no longer exist)
    # while looking like success.
    run, result = _run()
    clash = tmp_path / "occupied"
    clash.write_text("not a directory", encoding="utf-8")
    with pytest.raises(RunDetailWriteError):
        write_run_detail(run, result, clash / "detail.md")


def test_detail_archives_claim_statements_and_disposition():
    # M4: the response-record author and the N+2 carryover adjudication both
    # need the claim STATEMENTS, which verdicts-by-ID do not preserve.
    run, result = _run()
    text = render_run_detail(run, result)
    assert "## Claims" in text
    assert "X causes Y" in text, "statement must be archived, not just the ID"
    assert "[root_cause]" in text
    assert "[load-bearing]" in text
    assert "(carried)" not in text and "(delta)" not in text, \
        "no disposition marker on a first run"


def test_detail_prints_disposition_when_set():
    run, result = _run()
    run = run.model_copy(update={"claims": [
        run.claims[0].model_copy(update={"revision_disposition": "carried"}),
    ]})
    text = render_run_detail(run, result)
    assert "(carried)" in text


def test_run_detail_path_requires_runs_dir():
    with pytest.raises(TypeError):
        run_detail_path("docs/X.md", version=1, date="2026-10-12")  # type: ignore[call-arg]
