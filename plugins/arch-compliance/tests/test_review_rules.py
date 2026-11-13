"""Rule settings, RULES, check_auditors and row selection."""
from __future__ import annotations

import pytest

from acf.exceptions import AcfInputError, UnknownMandateError
from acf.registry import MandateRegistry
from acf.review.rules import (
    RULES,
    FailLoudSettings,
    RuleSettings,
    check_auditors,
    group_rows,
    select_rows,
)


def _row(**over):
    row = {
        "id": "r1",
        "title": "t",
        "severity": "WARN",
        "detection": "llm",
        "detector": "some-prompt",
        "languages": "none",
        "call_sites": ["ci"],
        "exemption_tokens": [],
        "status": "enforced",
        "arch_anchor": "## A",
        "auditor": "fail-loud",
    }
    row.update(over)
    return row


def _registry(*rows):
    return MandateRegistry.model_validate({"mandates": list(rows), "source_path": "m.yml"})


def test_wrong_type_names_mandate(tmp_path):
    reg = _registry(_row(auditor="single-owner", params={"allowlist_globs": "x"}))
    with pytest.raises(AcfInputError, match="'r1'"):
        check_auditors(reg, tmp_path)


def test_undeclared_key_listed_on_ast_row_refused_on_llm_row(tmp_path):
    params = {"zeta": 1, "alpha": 2, "surface": ["a/**"]}
    ast = _registry(_row(detection="ast", detector="builtin", params=params))
    (row,) = check_auditors(ast, tmp_path)
    assert row.undeclared == ["alpha", "zeta"]
    assert row.settings.surface == ["a/**"]
    llm = _registry(_row(params=params))
    with pytest.raises(AcfInputError, match=r"'r1'.*alpha.*zeta"):
        check_auditors(llm, tmp_path)


def test_unknown_auditor_and_missing_hatch(tmp_path):
    with pytest.raises(UnknownMandateError, match="nope"):
        check_auditors(_registry(_row(auditor="nope")), tmp_path)
    with pytest.raises(UnknownMandateError, match=r"r1.*p\.md"):
        check_auditors(_registry(_row(auditor="p.md")), tmp_path)


def test_hatch_resolves(tmp_path):
    (tmp_path / "p.md").write_text("x", encoding="utf-8")
    (row,) = check_auditors(_registry(_row(auditor="p.md")), tmp_path)
    assert row.prompt == (tmp_path / "p.md").resolve()
    assert row.settings is None
    assert row.undeclared == []


def test_rule_row_has_no_prompt(tmp_path):
    (row,) = check_auditors(_registry(_row()), tmp_path)
    assert row.prompt is None
    assert isinstance(row.settings, FailLoudSettings)


def test_inactive_row_not_reviewed(tmp_path):
    assert check_auditors(_registry(_row(status="unenforced")), tmp_path) == []


def test_row_without_auditor_not_reviewed(tmp_path):
    assert check_auditors(_registry(_row(auditor=None)), tmp_path) == []


def test_reviewed_whatever_call_sites(tmp_path):
    reg = _registry(_row(call_sites=["ci"]), _row(id="r2", call_sites=["audit"]))
    assert [r.mandate.id for r in check_auditors(reg, tmp_path)] == ["r1", "r2"]


def test_uncompilable_target_literal_re(tmp_path):
    reg = _registry(_row(auditor="single-owner", params={"target_literal_re": "("}))
    with pytest.raises(AcfInputError, match="'r1'"):
        check_auditors(reg, tmp_path)


def test_select_rows_unknown_id(tmp_path):
    rows = check_auditors(_registry(_row(), _row(id="r2")), tmp_path)
    assert select_rows(rows, None) is rows
    assert [r.mandate.id for r in select_rows(rows, ["r2"])] == ["r2"]
    with pytest.raises(UnknownMandateError, match="zz"):
        select_rows(rows, ["r1", "zz"])


def test_absent_settings_are_off(tmp_path):
    (row,) = check_auditors(_registry(_row()), tmp_path)
    assert row.settings.exception_base is None
    assert row.settings.surface is None
    assert row.settings.surface_exclude == []
    assert row.settings.docs == []


def test_nested_models_forbid_extra_keys(tmp_path):
    reg = _registry(_row(params={"exception_base": {"class_name": "E", "module": "m", "x": 1}}))
    with pytest.raises(AcfInputError, match="'r1'"):
        check_auditors(reg, tmp_path)


def test_rules_table_has_twelve_rules():
    assert len(RULES) == 12
    assert all(issubclass(m, RuleSettings) for m in RULES.values())


def test_group_rows_keeps_first_seen_order(tmp_path):
    reg = _registry(
        _row(id="a", auditor="no-shims"),
        _row(id="b", auditor="fail-loud"),
        _row(id="c", auditor="no-shims"),
    )
    groups = group_rows(check_auditors(reg, tmp_path))
    assert list(groups) == ["no-shims", "fail-loud"]
    assert [r.mandate.id for r in groups["no-shims"]] == ["a", "c"]
