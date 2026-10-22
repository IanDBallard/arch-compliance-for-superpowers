"""Invariants of the gate's prose, ported from the origin host's skill-install tests.

Each test here was a pin in that host's tests/test_adversarial_design_skill_install.py or
tests/test_responding_to_adversarial_review_skill_install.py; the host deletes those once
these land. The dual-tree byte-identity pins are not ported: the plugin ships one tree.
"""
from __future__ import annotations

import re
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[1] / "skills"
GATE = SKILLS / "adversarial-design-review"
RESPOND = SKILLS / "responding-to-adversarial-review"
REVIEWERS = ("refuter", "compliance", "sweeper", "hardening")
EXPECTED_GATE_FILES = {
    "SKILL.md",
    "claims/extraction.md",
    "reviewers/refuter.md",
    "reviewers/compliance.md",
    "reviewers/sweeper.md",
    "reviewers/hardening.md",
}
ENTRY_POINTS = (
    "parse_reviewer_payload",
    "group_convergence_candidates",
    "classify_outcome",
    "format_rollup",
    "append_row",
)
#: Only real import lines count — the symbols are also discussed in prose.
_ACF_ADR_IMPORT_RE = re.compile(r"^from acf\.adr import .*$", re.MULTILINE)
#: A real fence starts a line by itself; a mid-sentence mention must not satisfy it.
_JSON_FENCE_START_RE = re.compile(r"^```json$", re.MULTILINE)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_both_skills_have_frontmatter_with_a_name_and_description():
    for root in (GATE, RESPOND):
        body = _read(root / "SKILL.md")
        assert body.startswith("---\n"), root.name
        assert f"name: {root.name}\n" in body, root.name
        assert "description:" in body, root.name


def test_gate_names_the_pre_dispatch_stop_and_the_ledger_reread():
    body = _read(GATE / "SKILL.md")
    assert "**2b. Pre-dispatch mechanical stop.**" in body
    assert "responding-to-adversarial-review" in body
    assert "re-read the last" in body
    assert "unconditional on outcome" in body


def test_gate_references_every_reviewer_prompt():
    body = _read(GATE / "SKILL.md")
    for reviewer in REVIEWERS:
        assert f"reviewers/{reviewer}.md" in body, reviewer


def test_gate_imports_every_python_entry_point():
    imported = "\n".join(_ACF_ADR_IMPORT_RE.findall(_read(GATE / "SKILL.md")))
    assert imported, "no `from acf.adr import ...` line found"
    for symbol in ENTRY_POINTS:
        assert symbol in imported, f"{symbol} must be imported in a real `from acf.adr import` line"


def test_no_skill_file_contains_a_backslash():
    for root in (GATE, RESPOND):
        for path in sorted(root.rglob("*.md")):
            assert "\\" not in _read(path), path.relative_to(SKILLS).as_posix()


def test_gate_file_set_is_exactly_the_expected_six():
    present = {p.relative_to(GATE).as_posix() for p in GATE.rglob("*") if p.is_file()}
    assert present == EXPECTED_GATE_FILES


def test_every_reviewer_prompt_carries_the_read_only_footer_and_output_fence():
    for reviewer in REVIEWERS:
        body = _read(GATE / "reviewers" / f"{reviewer}.md")
        assert "You MUST NOT edit the spec" in body, reviewer
        assert _JSON_FENCE_START_RE.search(body), f"{reviewer}.md must state its output contract"


def test_no_reviewer_prompt_mentions_another_reviewer():
    for reviewer in REVIEWERS:
        body = _read(GATE / "reviewers" / f"{reviewer}.md").lower()
        for other in (r for r in REVIEWERS if r != reviewer):
            assert other not in body, f"{reviewer}.md names another reviewer: {other}"


def test_responding_skill_points_at_the_gate_and_the_mechanical_stop():
    body = _read(RESPOND / "SKILL.md")
    assert "adversarial-design-review" in body
    assert "pre-dispatch mechanical stop" in body
    assert "sweep the claim" in body.lower()
