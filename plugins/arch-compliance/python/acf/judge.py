"""Tier 2 LLM judge with confidence gating (Gemini default)."""

from __future__ import annotations

import json
import os
import re
from typing import Literal, Protocol

import httpx
from pydantic import BaseModel

from acf.exceptions import JudgeNotConfiguredError
from acf.finding import Finding, Severity
from acf.registry import Mandate

Confidence = Literal["high", "medium", "low"]

LLM_PROMPT_IDS: frozenset[str] = frozenset(
    {
        "llm_react_boundaries",
        "llm_fail_loud",
        "llm_no_shims",
        "llm_posix_paths",
    }
)

_GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "{model}:generateContent"
)


class JudgeResult(BaseModel):
    mandate_id: str
    severity: Literal["BLOCK", "WARN"]
    confidence: Confidence
    message: str
    path: str | None = None
    line: int | None = None


class JudgeProvider(Protocol):
    def review(self, *, diff_text: str, mandate: Mandate) -> JudgeResult | None: ...


def resolve_api_key() -> str | None:
    return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")


class GeminiProvider:
    """HTTP Gemini generateContent provider (no silent skip on errors)."""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash") -> None:
        self.api_key = api_key
        self.model = model

    def review(self, *, diff_text: str, mandate: Mandate) -> JudgeResult | None:
        prompt = _build_prompt(diff_text=diff_text, mandate=mandate)
        url = _GEMINI_URL.format(model=self.model)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0,
                "responseMimeType": "application/json",
            },
        }
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                url,
                params={"key": self.api_key},
                json=payload,
            )
            response.raise_for_status()
            body = response.json()

        text = _extract_text(body)
        data = _parse_json_object(text)
        if not data.get("violation", False):
            return None
        return JudgeResult(
            mandate_id=mandate.id,
            severity=data.get("severity", mandate.severity),
            confidence=data.get("confidence", "low"),
            message=str(data.get("message") or "LLM judge finding"),
            path=data.get("path"),
            line=data.get("line"),
        )


def run_judge(
    diff_text: str,
    mandates: list[Mandate],
    provider: JudgeProvider | None = None,
) -> list[Finding]:
    llm_mandates = [m for m in mandates if m.detection == "llm"]
    if not llm_mandates:
        return []

    enforced_llm = [m for m in llm_mandates if m.status == "enforced"]
    resolved = provider
    if resolved is None:
        api_key = resolve_api_key()
        if enforced_llm and not api_key:
            raise JudgeNotConfiguredError(
                "enforced detection:llm mandate(s) require GEMINI_API_KEY or "
                "GOOGLE_API_KEY (or an explicit JudgeProvider); refusing silent skip"
            )
        if not api_key:
            return []
        resolved = GeminiProvider(api_key=api_key)

    findings: list[Finding] = []
    for mandate in llm_mandates:
        result = resolved.review(diff_text=diff_text, mandate=mandate)
        if result is None:
            continue
        findings.append(_to_finding(result, mandate))
    return findings


def _to_finding(result: JudgeResult, mandate: Mandate) -> Finding:
    severity = Severity(mandate.severity)
    if severity == Severity.BLOCK and result.confidence != "high":
        severity = Severity.WARN
    return Finding(
        mandate_id=result.mandate_id,
        severity=severity,
        path=result.path or "<diff>",
        line=result.line if result.line is not None else 0,
        message=result.message,
        detector=mandate.detector,
        confidence=result.confidence,
        detection="llm",
    )


def _build_prompt(*, diff_text: str, mandate: Mandate) -> str:
    return (
        "You are an architecture compliance judge.\n"
        f"Mandate id: {mandate.id}\n"
        f"Title: {mandate.title}\n"
        f"Severity: {mandate.severity}\n"
        f"Detector/prompt id: {mandate.detector}\n"
        f"Architecture anchor: {mandate.arch_anchor}\n\n"
        "Review the unified diff. Respond with JSON only:\n"
        '{"violation": bool, "severity": "BLOCK"|"WARN", '
        '"confidence": "high"|"medium"|"low", "message": string, '
        '"path": string|null, "line": int|null}\n'
        "Set violation=false when the diff does not violate the mandate.\n\n"
        f"DIFF:\n{diff_text}\n"
    )


def _extract_text(body: dict) -> str:
    try:
        parts = body["candidates"][0]["content"]["parts"]
        return "".join(str(p.get("text", "")) for p in parts)
    except (KeyError, IndexError, TypeError) as e:
        raise JudgeNotConfiguredError(f"unexpected Gemini response shape: {e}") from e


def _parse_json_object(text: str) -> dict:
    text = text.strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise JudgeNotConfiguredError("Gemini response was not JSON") from None
        data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise JudgeNotConfiguredError("Gemini JSON root must be an object")
    return data
