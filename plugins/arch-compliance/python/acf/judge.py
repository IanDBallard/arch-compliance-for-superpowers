"""Tier 2 LLM judge with confidence gating (provider-neutral: Anthropic default, Gemini supported)."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Literal, Protocol

import httpx
from pydantic import BaseModel, ValidationError

from acf.exceptions import JudgeNotConfiguredError, JudgeResponseError
from acf.finding import Finding, Severity
from acf.registry import Mandate
from acf.template import render_template

_PROMPT_TEMPLATE = Path(__file__).resolve().parent / "judge_prompt.md"

Confidence = Literal["high", "medium", "low"]
ProviderName = Literal["anthropic", "gemini"]
PROVIDER_NAMES: tuple[ProviderName, ...] = ("anthropic", "gemini")

DEFAULT_PROVIDER: ProviderName = "anthropic"
DEFAULT_ANTHROPIC_MODEL: str = "claude-sonnet-4-6"
DEFAULT_GEMINI_MODEL: str = "gemini-2.0-flash"

LLM_PROMPT_IDS: frozenset[str] = frozenset(
    {
        "llm_react_boundaries",
        "llm_fail_loud",
        "llm_no_shims",
        "llm_posix_paths",
    }
)

_ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
_ANTHROPIC_VERSION = "2023-06-01"

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


def _resolve_provider_name(provider_name: str | None) -> ProviderName:
    if provider_name is not None:
        raw = provider_name.strip()
        if not raw:
            raise JudgeNotConfiguredError("judge provider name must not be empty")
    else:
        env_raw = (os.environ.get("ACF_JUDGE_PROVIDER") or "").strip()
        raw = env_raw if env_raw else DEFAULT_PROVIDER
    if raw not in PROVIDER_NAMES:
        raise JudgeNotConfiguredError(
            f"unknown judge provider {raw!r}; expected one of {PROVIDER_NAMES}"
        )
    return raw  # type: ignore[return-value]


def _resolve_model(provider_name: ProviderName, model: str | None) -> str:
    if model is not None:
        cleaned = model.strip()
        if not cleaned:
            raise JudgeNotConfiguredError("judge model name must not be empty")
        return cleaned
    env_model = (os.environ.get("ACF_JUDGE_MODEL") or "").strip()
    if env_model:
        return env_model
    if provider_name == "anthropic":
        return DEFAULT_ANTHROPIC_MODEL
    return DEFAULT_GEMINI_MODEL


def resolve_api_key(provider_name: ProviderName) -> str | None:
    if provider_name == "anthropic":
        return (os.environ.get("ANTHROPIC_API_KEY") or "").strip() or None
    if provider_name == "gemini":
        return (
            (os.environ.get("GEMINI_API_KEY") or "").strip()
            or (os.environ.get("GOOGLE_API_KEY") or "").strip()
            or None
        )
    raise JudgeNotConfiguredError(
        f"unknown judge provider {provider_name!r}; expected one of {PROVIDER_NAMES}"
    )


class AnthropicProvider:
    """HTTP Anthropic Messages API provider (no silent skip on errors)."""

    def __init__(self, api_key: str, model: str = DEFAULT_ANTHROPIC_MODEL) -> None:
        if not api_key or not api_key.strip():
            raise JudgeNotConfiguredError("AnthropicProvider api_key must not be empty")
        if not model or not model.strip():
            raise JudgeNotConfiguredError("AnthropicProvider model must not be empty")
        self.api_key = api_key.strip()
        self.model = model.strip()

    def review(self, *, diff_text: str, mandate: Mandate) -> JudgeResult | None:
        prompt = _build_prompt(diff_text=diff_text, mandate=mandate)
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": _ANTHROPIC_VERSION,
            "content-type": "application/json",
        }
        payload = {
            "model": self.model,
            "max_tokens": 1024,
            "temperature": 0,
            "messages": [{"role": "user", "content": prompt}],
        }
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    _ANTHROPIC_URL,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                body = response.json()
        except (httpx.HTTPError, ValueError) as e:
            raise JudgeResponseError(f"Anthropic HTTP/JSON failure: {e}") from e

        text = _extract_anthropic_text(body)
        return _result_from_text(text, mandate)


class GeminiProvider:
    """HTTP Gemini generateContent provider (no silent skip on errors)."""

    def __init__(self, api_key: str, model: str = DEFAULT_GEMINI_MODEL) -> None:
        if not api_key or not api_key.strip():
            raise JudgeNotConfiguredError("GeminiProvider api_key must not be empty")
        if not model or not model.strip():
            raise JudgeNotConfiguredError("GeminiProvider model must not be empty")
        self.api_key = api_key.strip()
        self.model = model.strip()

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
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    url,
                    params={"key": self.api_key},
                    json=payload,
                )
                response.raise_for_status()
                body = response.json()
        except (httpx.HTTPError, ValueError) as e:
            raise JudgeResponseError(f"Gemini HTTP/JSON failure: {e}") from e

        text = _extract_text(body)
        return _result_from_text(text, mandate)


def resolve_provider(
    *,
    provider_name: str | None = None,
    model: str | None = None,
    has_enforced: bool,
) -> JudgeProvider | None:
    resolved_name = _resolve_provider_name(provider_name)
    resolved_model = _resolve_model(resolved_name, model)
    api_key = resolve_api_key(resolved_name)
    if api_key is None:
        if has_enforced:
            required_vars = (
                "ANTHROPIC_API_KEY"
                if resolved_name == "anthropic"
                else "GEMINI_API_KEY or GOOGLE_API_KEY"
            )
            raise JudgeNotConfiguredError(
                f"enforced detection:llm mandate(s) with provider {resolved_name!r} "
                f"require {required_vars} (or an explicit JudgeProvider); refusing silent skip"
            )
        return None
    if resolved_name == "anthropic":
        return AnthropicProvider(api_key=api_key, model=resolved_model)
    return GeminiProvider(api_key=api_key, model=resolved_model)


def run_judge(
    diff_text: str,
    mandates: list[Mandate],
    provider: JudgeProvider | None = None,
    *,
    provider_name: str | None = None,
    model: str | None = None,
) -> list[Finding]:
    llm_mandates = [m for m in mandates if m.detection == "llm"]
    if not llm_mandates:
        return []

    enforced_llm = [m for m in llm_mandates if m.status == "enforced"]
    resolved = provider
    if resolved is None:
        resolved = resolve_provider(
            provider_name=provider_name,
            model=model,
            has_enforced=bool(enforced_llm),
        )
        if resolved is None:
            return []

    findings: list[Finding] = []
    for mandate in llm_mandates:
        result = resolved.review(diff_text=diff_text, mandate=mandate)
        if result is None:
            continue
        findings.append(_to_finding(result, mandate))
    return findings


def _to_finding(result: JudgeResult, mandate: Mandate) -> Finding:
    # Registry severity is the ceiling; the judge can only demote — either
    # explicitly (its own WARN verdict) or via sub-high confidence.
    severity = Severity(mandate.severity)
    if severity == Severity.BLOCK and (
        result.severity == "WARN" or result.confidence != "high"
    ):
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
    return render_template(
        _PROMPT_TEMPLATE.read_text(encoding="utf-8"),
        {
            "MANDATE_ID": mandate.id,
            "TITLE": mandate.title,
            "SEVERITY": mandate.severity,
            "DETECTOR": mandate.detector,
            "ARCH_ANCHOR": mandate.arch_anchor,
            "DIFF_TEXT": diff_text,
        },
    )


def _extract_anthropic_text(body: dict) -> str:
    if not isinstance(body, dict):
        raise JudgeResponseError("unexpected Anthropic response shape: body is not a dict")
    content = body.get("content")
    if not isinstance(content, list) or not content:
        raise JudgeResponseError("unexpected Anthropic response shape: missing content list")
    chunks: list[str] = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            text_val = block.get("text")
            if isinstance(text_val, str):
                chunks.append(text_val)
    joined = "".join(chunks).strip()
    if not joined:
        raise JudgeResponseError("unexpected Anthropic response shape: empty text content")
    return joined


def _extract_text(body: dict) -> str:
    try:
        parts = body["candidates"][0]["content"]["parts"]
        if not isinstance(parts, list) or not parts:
            raise JudgeResponseError("unexpected Gemini response shape: empty parts")
        joined = "".join(str(p.get("text", "")) for p in parts).strip()
    except (KeyError, IndexError, TypeError, AttributeError) as e:
        raise JudgeResponseError(f"unexpected Gemini response shape: {e}") from e
    if not joined:
        raise JudgeResponseError("unexpected Gemini response shape: empty text")
    return joined


def _parse_json_object(text: str) -> dict:
    text = text.strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            raise JudgeResponseError("judge response was not JSON") from None
        try:
            data = json.loads(match.group(0))
        except json.JSONDecodeError as e:
            raise JudgeResponseError(f"judge response contained invalid JSON: {e}") from e
    if not isinstance(data, dict):
        raise JudgeResponseError("judge JSON root must be an object")
    return data


def _result_from_text(text: str, mandate: Mandate) -> JudgeResult | None:
    data = _parse_json_object(text)
    if not data.get("violation", False):
        return None
    try:
        return JudgeResult(
            mandate_id=mandate.id,
            severity=data.get("severity", mandate.severity),
            confidence=data.get("confidence", "low"),
            message=str(data.get("message") or "LLM judge finding"),
            path=data.get("path"),
            line=data.get("line"),
        )
    except ValidationError as e:
        raise JudgeResponseError(f"invalid judge result fields: {e}") from e
