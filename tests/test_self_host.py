"""This repository is a host of its own gate: the declaration, the doctrine and the
registry agree (spec docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md §5.5).

Every generic check is the package's: the registry loader refuses a repeated id,
`missing_anchors` is the one anchor check, `KNOWN_DETECTORS` the built-in detector contracts,
and `acf.repo` the one declaration of host paths. What stays here is this host's own
policy: its declared values, and that its manual rows point at the plugin's tests.
"""
from __future__ import annotations

from pathlib import Path

from acf.adr import load_host_config
from acf.detectors import KNOWN_DETECTORS
from acf.judge import LLM_PROMPT_IDS
from acf.registry import load_mandates, missing_anchors
from acf.repo import ARCH_REL, MANDATES_REL, RepoTree

ROOT = Path(__file__).resolve().parents[1]
MANUAL_DETECTOR_PREFIX = "plugins/arch-compliance/tests/"


def _registry():
    return load_mandates(
        ROOT / MANDATES_REL,
        known_detectors=KNOWN_DETECTORS,
        llm_prompt_ids=LLM_PROMPT_IDS,
        repo_root=ROOT,
    )


def test_declaration_names_the_reviews_tree():
    cfg = load_host_config(ROOT)
    assert cfg.runs_dir == "docs/reviews/adr_runs"
    assert cfg.ledger_path == "docs/reviews/adversarial_design_ledger.jsonl"


def test_every_anchor_is_in_the_doctrine():
    doctrine = (ROOT / ARCH_REL).read_text(encoding="utf-8")
    assert missing_anchors(_registry(), doctrine) == []


def test_every_manual_row_names_an_existing_test_module():
    rows = [m for m in _registry().mandates if m.detection == "manual"]
    assert rows, "this host's registry carries manual rows"
    missing = [m.id for m in rows if RepoTree(ROOT).file(m.detector) is None
               or not m.detector.startswith(MANUAL_DETECTOR_PREFIX)]
    assert missing == []


def test_doctrine_declares_post_merge_and_installed_skills_include_housekeeping():
    doctrine = (ROOT / ARCH_REL).read_text(encoding="utf-8")
    assert "## Post-merge\n" in doctrine
    assert "No row: host operational declarations; no test enforces this." in doctrine
    check_script = (ROOT / "scripts" / "check_installed_skills.py").read_text(encoding="utf-8")
    assert '"post-merge-housekeeping"' in check_script
