"""Auditor payload parsing, inline exemptions and the report."""
from __future__ import annotations

import json
from datetime import date

import pytest

from acf.exceptions import AuditorContractViolationError, ReportWriteError
from acf.registry import MandateRegistry
from acf.repo import RepoTree
from acf.review.aggregator import (
    GroupResult,
    apply_exemptions,
    parse_auditor_payload,
    render_report,
    write_report,
)
from acf.review.contract import AuditorFinding, AuditorPayload
from acf.review.host import ReviewHostConfig
from acf.review.rules import check_auditors


def _cfg(report_dir="reports"):
    return ReviewHostConfig(
        report_dir=report_dir,
        baseline_path="base.json",
        baseline_max_age_days=30,
        baseline_max_commits=50,
        packs=[],
        subsystems=[],
        exclude=[],
    )


def _rows(tmp_path, tokens=("allow-x",)):
    row = {
        "id": "r1",
        "title": "t",
        "severity": "WARN",
        "detection": "llm",
        "detector": "some-prompt",
        "languages": "both",
        "call_sites": ["ci"],
        "exemption_tokens": list(tokens),
        "status": "enforced",
        "arch_anchor": "## A",
        "auditor": "fail-loud",
    }
    reg = MandateRegistry.model_validate({"mandates": [row], "source_path": "m.yml"})
    return check_auditors(reg, tmp_path)


def _finding(**over):
    base = dict(
        mandate_id="r1",
        path="src/a.py",
        line=2,
        snippet="y = 2",
        severity="important",
        rule="no-bare-except",
        why="because",
        suggested_fix="fix it",
    )
    base.update(over)
    return base


def _payload(findings, group="g1"):
    body = {"group": group, "files_examined": 1, "findings": findings, "errors": []}
    return "text\n```json\n" + json.dumps(body) + "\n```\n"


@pytest.fixture
def tree(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\ny = 2  # allow-x: ok\n", encoding="utf-8")
    return RepoTree(tmp_path)


def _parse(tmp_path, tree, payload, surfaces=None):
    return parse_auditor_payload(
        payload,
        group="g1",
        rows=_rows(tmp_path),
        surfaces=surfaces if surfaces is not None else {"r1": ["src/a.py"]},
        tree=tree,
    )


def test_good_payload_parses(tmp_path, tree):
    result = _parse(tmp_path, tree, _payload([_finding()]))
    assert result.group == "g1" and result.findings[0].line == 2


def test_unknown_mandate_is_violation(tmp_path, tree):
    with pytest.raises(AuditorContractViolationError, match="r9"):
        _parse(tmp_path, tree, _payload([_finding(mandate_id="r9")]))


def test_group_mismatch_is_violation(tmp_path, tree):
    with pytest.raises(AuditorContractViolationError, match="other"):
        _parse(tmp_path, tree, _payload([], group="other"))


def test_out_of_surface_path_is_violation(tmp_path, tree):
    with pytest.raises(AuditorContractViolationError, match="src/b.py"):
        _parse(tmp_path, tree, _payload([_finding(path="src/b.py")]))


def test_line_past_end_is_violation(tmp_path, tree):
    with pytest.raises(AuditorContractViolationError, match="past the end"):
        _parse(tmp_path, tree, _payload([_finding(line=3)]))


def test_schema_failure_names_group(tmp_path, tree):
    bad = "```json\n" + json.dumps({"group": "g1"}) + "\n```"
    with pytest.raises(AuditorContractViolationError, match="g1"):
        _parse(tmp_path, tree, bad)


def test_extractor_failure_is_violation(tmp_path, tree):
    with pytest.raises(AuditorContractViolationError):
        _parse(tmp_path, tree, "no block here")


def test_exempted_line_dropped_and_counted(tmp_path, tree):
    rows = {r.mandate.id: r for r in _rows(tmp_path)}
    kept_f = AuditorFinding(**_finding(line=1, snippet="x = 1"))
    exempt_f = AuditorFinding(**_finding(line=2))
    kept, exempted = apply_exemptions([kept_f, exempt_f], rows, tree)
    assert kept == [kept_f] and exempted == 1


def test_row_without_tokens_keeps_finding(tmp_path, tree):
    rows = {r.mandate.id: r for r in _rows(tmp_path, tokens=())}
    finding = AuditorFinding(**_finding())
    assert apply_exemptions([finding], rows, tree) == ([finding], 0)


def test_render_report_shows_failed_and_ok():
    finding = AuditorFinding(**_finding())
    ok = GroupResult(
        group="g1",
        status="OK",
        payload=AuditorPayload(group="g1", files_examined=1, findings=[finding], errors=[]),
        raw="",
        error=None,
    )
    failed = GroupResult(
        group="g2", status="FAILED", payload=None, raw="RAW-GARBAGE", error="bad contract"
    )
    text = render_report(
        commit="abc123",
        invocation="/architecture-review",
        results=[ok, failed],
        findings=[finding],
        exempted=2,
        rollup_md="ROLLUP-BODY",
    )
    assert "abc123" in text and "/architecture-review" in text
    assert "g1" in text and "g2" in text and "FAILED" in text
    assert "src/a.py:2" in text and "no-bare-except" in text and "r1" in text
    assert "2 findings exempted" in text
    assert "ROLLUP-BODY" in text
    assert "## Failed groups" in text and "RAW-GARBAGE" in text and "bad contract" in text
    assert text.index("## Findings") < text.index("ROLLUP-BODY") < text.index("## Failed groups")


def test_render_report_without_failures_has_no_failed_section():
    ok = GroupResult(
        group="g1",
        status="OK",
        payload=AuditorPayload(group="g1", files_examined=0, findings=[], errors=[]),
        raw="",
        error=None,
    )
    text = render_report(
        commit="c", invocation="i", results=[ok], findings=[], exempted=0, rollup_md="R"
    )
    assert "## Failed groups" not in text


def test_second_same_day_report_gets_suffix(tmp_path):
    tree = RepoTree(tmp_path)
    cfg = _cfg()
    today = date(2026, 11, 12)
    first = write_report(tree, cfg, "one", today)
    second = write_report(tree, cfg, "two", today)
    third = write_report(tree, cfg, "three", today)
    assert first.name == "ARCHITECTURE_REVIEW_2026-11-12.md"
    assert second.name == "ARCHITECTURE_REVIEW_2026-11-12_2.md"
    assert third.name == "ARCHITECTURE_REVIEW_2026-11-12_3.md"
    assert first.read_text(encoding="utf-8") == "one"


def test_report_dir_outside_root_is_write_error(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    with pytest.raises(ReportWriteError, match="escape"):
        write_report(RepoTree(root), _cfg(report_dir="../escape"), "x", date(2026, 11, 12))


def test_failed_group_fence_encloses_raw_payload_with_inner_fence():
    raw = "intro\n```json\n{}\n```\ntail"
    failed = GroupResult(group="g2", status="FAILED", payload=None, raw=raw, error="bad")
    text = render_report(
        commit="c", invocation="i", results=[failed], findings=[], exempted=0, rollup_md="R"
    )
    fence = "````"
    assert f"\n{fence}\n{raw}\n{fence}\n" in text
