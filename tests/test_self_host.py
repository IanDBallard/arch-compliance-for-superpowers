"""This repository is a host of its own gate: the declaration, the doctrine and the
registry agree (spec docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md §5.5)."""
from __future__ import annotations

from pathlib import Path

from acf.adr import load_host_config
from acf.detectors import ALL_PYTHON_DETECTOR_IDS
from acf.detectors.typescript_bridge import TS_DETECTOR_IDS
from acf.judge import LLM_PROMPT_IDS
from acf.registry import load_mandates

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "architecture"
KNOWN_DETECTORS = ALL_PYTHON_DETECTOR_IDS | TS_DETECTOR_IDS | LLM_PROMPT_IDS


def _registry():
    return load_mandates(CONFIG / "mandates.yml", known_detectors=KNOWN_DETECTORS)


def test_declaration_names_the_reviews_tree():
    cfg = load_host_config(ROOT)
    assert cfg.runs_dir == "docs/reviews/adr_runs"
    assert cfg.ledger_path == "docs/reviews/adversarial_design_ledger.jsonl"


def test_every_anchor_is_in_the_doctrine():
    doctrine = (CONFIG / "ARCHITECTURE.md").read_text(encoding="utf-8")
    missing = [m.id for m in _registry().mandates if m.arch_anchor not in doctrine]
    assert missing == []


def test_every_manual_row_names_an_existing_test_module():
    rows = [m for m in _registry().mandates if m.detection == "manual"]
    assert rows, "no manual rows: Task 4 adds five"
    missing = [m.id for m in rows if not (ROOT / m.detector).is_file()
               or not m.detector.startswith("plugins/arch-compliance/tests/")]
    assert missing == []


def test_mandate_ids_are_unique():
    ids = [m.id for m in _registry().mandates]
    assert sorted(set(ids)) == sorted(ids)
