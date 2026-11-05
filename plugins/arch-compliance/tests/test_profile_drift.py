"""Drift checks: profile mandates stay aligned with ARCHITECTURE.md anchors."""

from __future__ import annotations

from pathlib import Path

from acf.detectors import KNOWN_DETECTORS
from acf.judge import LLM_PROMPT_IDS
from acf.registry import load_mandates, missing_anchors

PROFILES = Path(__file__).resolve().parents[1] / "profiles"


def test_profile_arch_anchors_match_architecture_md() -> None:
    profile_dirs = sorted(p for p in PROFILES.iterdir() if p.is_dir())
    assert profile_dirs, f"no profiles under {PROFILES.as_posix()}"

    for profile_dir in profile_dirs:
        mandates_path = profile_dir / "mandates.yml"
        arch_path = profile_dir / "ARCHITECTURE.md"
        assert mandates_path.is_file(), f"missing {mandates_path.as_posix()}"
        assert arch_path.is_file(), f"missing {arch_path.as_posix()}"

        arch_text = arch_path.read_text(encoding="utf-8")
        regs = load_mandates(
            mandates_path, known_detectors=KNOWN_DETECTORS, llm_prompt_ids=LLM_PROMPT_IDS
        )
        assert regs.mandates, f"{profile_dir.name}: empty mandates.yml"

        missing = missing_anchors(regs, arch_text)
        assert missing == [], (
            f"{profile_dir.name}: arch_anchor of {missing} not found in {arch_path.as_posix()}"
        )
