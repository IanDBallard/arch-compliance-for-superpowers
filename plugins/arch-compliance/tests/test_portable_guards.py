"""Tests for config-driven / repo-level portable Python guards."""

from __future__ import annotations

from pathlib import Path

import pytest

from acf.detectors.build_artifacts import scan_build_artifact_paths
from acf.detectors.facade_sinks import scan_facade_sinks
from acf.detectors.fail_loud_ratchet import (
    compare_to_baseline,
    count_bare_excepts,
    scan_tree,
)
from acf.detectors.fsm_guard import scan_fsm_writes
from acf.exceptions import DetectorPackError


def test_build_artifact_flags_dist_path() -> None:
    findings = scan_build_artifact_paths(
        ["src/a.py", "dist/out.js"],
        path_prefixes=["dist/", "build/"],
    )
    assert len(findings) == 1
    assert findings[0].mandate_id == "ops.no-build-artifacts"
    assert findings[0].path == "dist/out.js"


def test_build_artifact_clean() -> None:
    assert scan_build_artifact_paths(["src/a.py"], path_prefixes=["dist/"]) == []


def test_facade_sink_open_write_detected() -> None:
    text = 'def save():\n    open("data/index.yml", "w").write("x")\n'
    findings = scan_facade_sinks(
        text,
        "svc/writer.py",
        added_lines=frozenset({2}),
        target_literal_re=r"index\.ya?ml",
        allowlist_globs=[],
        atomic_is_sink=True,
    )
    assert any(f.mandate_id == "facade.forbid-sink" for f in findings)


def test_facade_sink_allowlisted_path_skipped() -> None:
    text = 'def save():\n    open("data/index.yml", "w").write("x")\n'
    findings = scan_facade_sinks(
        text,
        "services/metadata.py",
        added_lines=frozenset({2}),
        target_literal_re=r"index\.ya?ml",
        allowlist_globs=["services/**"],
        atomic_is_sink=True,
    )
    assert findings == []


def test_facade_requires_target_pattern() -> None:
    with pytest.raises(DetectorPackError):
        scan_facade_sinks(
            "x = 1\n",
            "a.py",
            added_lines=None,
            target_literal_re="",
            allowlist_globs=[],
            atomic_is_sink=True,
        )


def test_fsm_write_without_validator() -> None:
    text = "def advance(obj):\n    obj.machine_state = 'DONE'\n"
    findings = scan_fsm_writes(
        text,
        "fsm.py",
        added_lines=frozenset({2}),
        state_field="machine_state",
        validator_name="validate_transition",
    )
    assert any(f.mandate_id == "fsm.transition-guard" for f in findings)


def test_fsm_write_with_validator_clean() -> None:
    text = (
        "def advance(obj):\n"
        "    validate_transition(obj.machine_state, 'DONE')\n"
        "    obj.machine_state = 'DONE'\n"
    )
    findings = scan_fsm_writes(
        text,
        "fsm.py",
        added_lines=frozenset({2, 3}),
        state_field="machine_state",
        validator_name="validate_transition",
    )
    assert findings == []


def test_fail_loud_ratchet_growth(tmp_path: Path) -> None:
    src = tmp_path / "pkg"
    src.mkdir()
    (src / "a.py").write_text(
        "def f():\n    try:\n        g()\n    except Exception:\n        pass\n",
        encoding="utf-8",
    )
    counts = scan_tree(tmp_path, roots=["pkg"], exclude_globs=["**/tests/**"])
    assert counts.get("pkg/a.py") == 1
    baseline = {"files": {"pkg/a.py": 0}}
    growth = compare_to_baseline(counts, baseline)
    assert growth == {"pkg/a.py": (0, 1)}


def test_count_bare_excepts_unit() -> None:
    text = "try:\n    x()\nexcept Exception:\n    pass\n"
    assert count_bare_excepts(text) == 1
