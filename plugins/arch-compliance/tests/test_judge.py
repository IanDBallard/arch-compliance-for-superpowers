from __future__ import annotations

import json
from pathlib import Path

import pytest

from acf.exceptions import JudgeNotConfiguredError
from acf.finding import Severity
from acf.judge import LLM_PROMPT_IDS, JudgeResult, run_judge
from acf.registry import Mandate

CORPUS = Path(__file__).parent / "fixtures" / "judge_corpus"


def _llm_mandate(
    *,
    mandate_id: str = "soft.react-boundaries",
    severity: str = "BLOCK",
    status: str = "enforced",
    detector: str = "llm_react_boundaries",
) -> Mandate:
    return Mandate(
        id=mandate_id,
        title="LLM soft smell",
        severity=severity,  # type: ignore[arg-type]
        detection="llm",
        detector=detector,
        languages="both",
        call_sites=["ci"],
        exemption_tokens=[],
        status=status,  # type: ignore[arg-type]
        arch_anchor="# Soft smells",
    )


def test_llm_prompt_ids_exported() -> None:
    assert isinstance(LLM_PROMPT_IDS, frozenset)
    assert "llm_react_boundaries" in LLM_PROMPT_IDS


def test_judge_not_configured_hard_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    with pytest.raises(JudgeNotConfiguredError):
        run_judge(diff_text="diff --git a/x.py b/x.py\n", mandates=[_llm_mandate()])


def test_judge_not_configured_ok_without_enforced_llm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    findings = run_judge(
        diff_text="diff --git a/x.py b/x.py\n",
        mandates=[_llm_mandate(status="unenforced")],
    )
    assert findings == []


def test_confidence_gating() -> None:
    mandate = _llm_mandate(severity="BLOCK")

    class MediumProvider:
        def review(self, *, diff_text: str, mandate: Mandate) -> JudgeResult:
            return JudgeResult(
                mandate_id=mandate.id,
                severity="BLOCK",
                confidence="medium",
                message="Possible boundary leak",
                path="src/App.tsx",
                line=12,
            )

    findings = run_judge(
        diff_text="...",
        mandates=[mandate],
        provider=MediumProvider(),
    )
    assert len(findings) == 1
    assert findings[0].severity == Severity.WARN
    assert findings[0].confidence == "medium"
    assert findings[0].detection == "llm"


def test_high_confidence_keeps_block() -> None:
    mandate = _llm_mandate(severity="BLOCK")

    class HighProvider:
        def review(self, *, diff_text: str, mandate: Mandate) -> JudgeResult:
            return JudgeResult(
                mandate_id=mandate.id,
                severity="BLOCK",
                confidence="high",
                message="Clear boundary leak",
                path="src/App.tsx",
                line=4,
            )

    findings = run_judge(
        diff_text="...",
        mandates=[mandate],
        provider=HighProvider(),
    )
    assert len(findings) == 1
    assert findings[0].severity == Severity.BLOCK


def test_corpus_fixtures_with_fake_provider() -> None:
    files = sorted(CORPUS.glob("*.json"))
    assert len(files) >= 8
    python_n = sum(1 for p in files if json.loads(p.read_text(encoding="utf-8"))["language"] == "python")
    ts_n = sum(1 for p in files if json.loads(p.read_text(encoding="utf-8"))["language"] == "typescript")
    assert python_n >= 4
    assert ts_n >= 4

    for path in files:
        fixture = json.loads(path.read_text(encoding="utf-8"))
        mandate = _llm_mandate(
            mandate_id=fixture["mandate_id"],
            detector=fixture["detector"],
            severity=fixture.get("mandate_severity", "BLOCK"),
        )

        class FakeProvider:
            def review(self, *, diff_text: str, mandate: Mandate) -> JudgeResult | None:
                assert diff_text == fixture["diff_text"]
                if fixture["expected_label"] == "clean":
                    return None
                return JudgeResult(
                    mandate_id=mandate.id,
                    severity=fixture.get("expected_severity", "BLOCK"),
                    confidence=fixture["expected_confidence"],
                    message=fixture.get("message", "fixture finding"),
                    path=fixture.get("path"),
                    line=fixture.get("line"),
                )

        findings = run_judge(
            diff_text=fixture["diff_text"],
            mandates=[mandate],
            provider=FakeProvider(),
        )
        if fixture["expected_label"] == "clean":
            assert findings == [], path.name
        else:
            assert len(findings) == 1, path.name
            expected_sev = fixture.get("expected_finding_severity")
            if expected_sev is None:
                if (
                    fixture.get("mandate_severity", "BLOCK") == "BLOCK"
                    and fixture["expected_confidence"] != "high"
                ):
                    expected_sev = "WARN"
                else:
                    expected_sev = fixture.get("expected_severity", "BLOCK")
            assert findings[0].severity.value == expected_sev, path.name
            assert findings[0].confidence == fixture["expected_confidence"], path.name
