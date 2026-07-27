from __future__ import annotations

import json
from pathlib import Path

import pytest

from acf.baseline import (
    Baseline,
    BaselineCell,
    DriftReport,
    aggregate,
    compute_drift,
    load_baseline,
    save_baseline,
    subsystem_of,
)
from acf.exceptions import BaselineError
from acf.finding import Finding, Severity


def _finding(
    mandate_id: str,
    path: str,
    *,
    line: int = 1,
    message: str = "x",
    detector: str = "test",
) -> Finding:
    return Finding(
        mandate_id=mandate_id,
        severity=Severity.WARN,
        path=path,
        line=line,
        message=message,
        detector=detector,
    )


def _baseline(cells: dict[tuple[str, str], int]) -> Baseline:
    return Baseline(
        generated_at="2026-07-27",
        commit="abc1234",
        invocation="/architecture-review",
        counts=[
            BaselineCell(mandate_id=m, subsystem=s, count=c)
            for (m, s), c in cells.items()
        ],
    )


def test_subsystem_of_first_segment() -> None:
    assert subsystem_of("src/components/App.tsx") == "src/"
    assert subsystem_of("plugins/arch-compliance/foo.py") == "plugins/"
    assert subsystem_of("admin/js/app.js") == "admin/"
    assert subsystem_of("README.md") == "other"


def test_subsystem_of_normalizes_backslashes() -> None:
    assert subsystem_of("src\\lib\\x.py") == "src/"


def test_aggregate_counts_by_mandate_and_subsystem() -> None:
    findings = [
        _finding("fail-loud.empty-catch", "src/a.ts"),
        _finding("fail-loud.empty-catch", "src/b.ts"),
        _finding("fail-loud.empty-catch", "lib/c.ts"),
        _finding("no-shims.explicit-any", "src/d.ts"),
    ]
    counts = aggregate(findings)
    assert counts[("fail-loud.empty-catch", "src/")] == 2
    assert counts[("fail-loud.empty-catch", "lib/")] == 1
    assert counts[("no-shims.explicit-any", "src/")] == 1


def test_save_then_load_round_trip(tmp_path: Path) -> None:
    data = _baseline({("fail-loud.empty-catch", "src/"): 2})
    path = tmp_path / "docs" / "architecture" / "compliance_baseline.json"
    save_baseline(path, data)
    loaded = load_baseline(path)
    assert loaded.commit == "abc1234"
    assert loaded.counts[0].mandate_id == "fail-loud.empty-catch"
    assert loaded.counts[0].subsystem == "src/"
    assert loaded.counts[0].count == 2
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert "/" in raw["counts"][0]["subsystem"]
    assert "\\" not in json.dumps(raw)


def test_load_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(BaselineError):
        load_baseline(tmp_path / "nope.json")


def test_load_malformed_json_raises(tmp_path: Path) -> None:
    path = tmp_path / "b.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(BaselineError):
        load_baseline(path)


def test_load_invalid_schema_raises(tmp_path: Path) -> None:
    path = tmp_path / "b.json"
    path.write_text(json.dumps({"generated_at": "x"}), encoding="utf-8")
    with pytest.raises(BaselineError):
        load_baseline(path)


def test_compute_drift_deltas_worsening_first() -> None:
    current = {
        ("fail-loud.empty-catch", "src/"): 5,
        ("no-shims.explicit-any", "lib/"): 1,
    }
    base = _baseline(
        {
            ("fail-loud.empty-catch", "src/"): 2,
            ("no-shims.explicit-any", "lib/"): 4,
        }
    )
    report = compute_drift(current, base)
    assert isinstance(report, DriftReport)
    assert report.rows[0].mandate_id == "fail-loud.empty-catch"
    assert report.rows[0].delta == 3
    assert report.rows[-1].mandate_id == "no-shims.explicit-any"
    assert report.rows[-1].delta == -3


def test_compute_drift_filtered_run_omits_non_run_mandates() -> None:
    current = {("soft.react-boundaries", "src/"): 1}
    base = _baseline(
        {
            ("fail-loud.empty-catch", "src/"): 9,
            ("soft.react-boundaries", "src/"): 1,
        }
    )
    report = compute_drift(current, base)
    assert {r.mandate_id for r in report.rows} == {"soft.react-boundaries"}


def test_compute_drift_resolved_cell_shows_current_zero() -> None:
    current = {("soft.react-boundaries", "src/"): 1}
    base = _baseline({("soft.react-boundaries", "admin/"): 3})
    by_sub = {r.subsystem: r for r in compute_drift(current, base).rows}
    assert by_sub["admin/"].current_count == 0
    assert by_sub["admin/"].delta == -3
    assert by_sub["src/"].delta == 1


def test_compute_drift_empty_current_is_empty_universe() -> None:
    base = _baseline({("fail-loud.empty-catch", "src/"): 9})
    assert compute_drift({}, base).rows == []
