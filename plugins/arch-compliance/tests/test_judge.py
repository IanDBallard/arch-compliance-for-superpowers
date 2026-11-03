from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from acf import cli_check_llm
from acf.exceptions import JudgeNotConfiguredError, JudgeResponseError
from acf.finding import Severity
from acf.judge import (
    DEFAULT_ANTHROPIC_MODEL,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_PROVIDER,
    LLM_PROMPT_IDS,
    PROVIDER_NAMES,
    AnthropicProvider,
    GeminiProvider,
    JudgeResult,
    _extract_anthropic_text,
    _extract_text,
    _parse_json_object,
    _result_from_text,
    resolve_api_key,
    resolve_provider,
    run_judge,
)
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


def _clear_judge_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in (
        "ACF_JUDGE_PROVIDER",
        "ACF_JUDGE_MODEL",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
    ):
        monkeypatch.delenv(var, raising=False)


def test_llm_prompt_ids_exported() -> None:
    assert isinstance(LLM_PROMPT_IDS, frozenset)
    assert "llm_react_boundaries" in LLM_PROMPT_IDS


def test_provider_constants_exported() -> None:
    assert DEFAULT_PROVIDER == "anthropic"
    assert DEFAULT_ANTHROPIC_MODEL == "claude-sonnet-4-6"
    assert DEFAULT_GEMINI_MODEL == "gemini-2.0-flash"
    assert PROVIDER_NAMES == ("anthropic", "gemini")


def test_judge_not_configured_hard_fails_anthropic_default_no_cross_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_judge_env(monkeypatch)
    # Even when Gemini keys are set, default anthropic provider must not fall back to them.
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-secret")
    monkeypatch.setenv("GOOGLE_API_KEY", "google-secret")
    with pytest.raises(JudgeNotConfiguredError, match="ANTHROPIC_API_KEY"):
        run_judge(diff_text="diff --git a/x.py b/x.py\n", mandates=[_llm_mandate()])


def test_judge_not_configured_hard_fails_gemini_no_cross_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_judge_env(monkeypatch)
    # Even when Anthropic key is set, explicit gemini provider must not fall back to it.
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-secret")
    with pytest.raises(JudgeNotConfiguredError, match="GEMINI_API_KEY"):
        run_judge(
            diff_text="diff --git a/x.py b/x.py\n",
            mandates=[_llm_mandate()],
            provider_name="gemini",
        )


def test_judge_not_configured_ok_without_enforced_llm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_judge_env(monkeypatch)
    findings = run_judge(
        diff_text="diff --git a/x.py b/x.py\n",
        mandates=[_llm_mandate(status="unenforced")],
    )
    assert findings == []


def test_whitespace_only_api_keys_treated_as_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_judge_env(monkeypatch)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "   ")
    assert resolve_api_key("anthropic") is None
    with pytest.raises(JudgeNotConfiguredError):
        run_judge(diff_text="diff --git a/x.py b/x.py\n", mandates=[_llm_mandate()])

    monkeypatch.setenv("GEMINI_API_KEY", "  ")
    monkeypatch.setenv("GOOGLE_API_KEY", "\t\n")
    assert resolve_api_key("gemini") is None


def test_unknown_or_empty_provider_or_model_raises_not_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_judge_env(monkeypatch)
    with pytest.raises(JudgeNotConfiguredError, match="unknown judge provider"):
        run_judge(
            diff_text="...",
            mandates=[_llm_mandate(status="unenforced")],
            provider_name="openai",
        )
    with pytest.raises(JudgeNotConfiguredError, match="must not be empty"):
        run_judge(
            diff_text="...",
            mandates=[_llm_mandate(status="unenforced")],
            provider_name="   ",
        )
    with pytest.raises(JudgeNotConfiguredError, match="must not be empty"):
        run_judge(
            diff_text="...",
            mandates=[_llm_mandate(status="unenforced")],
            model="   ",
        )
    monkeypatch.setenv("ACF_JUDGE_PROVIDER", "bedrock")
    with pytest.raises(JudgeNotConfiguredError, match="unknown judge provider"):
        run_judge(
            diff_text="...",
            mandates=[_llm_mandate(status="unenforced")],
        )


def test_resolve_provider_selects_anthropic_and_gemini_with_env_and_overrides(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _clear_judge_env(monkeypatch)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-123")
    p1 = resolve_provider(has_enforced=True)
    assert isinstance(p1, AnthropicProvider)
    assert p1.api_key == "sk-ant-123"
    assert p1.model == DEFAULT_ANTHROPIC_MODEL

    monkeypatch.setenv("ACF_JUDGE_PROVIDER", "gemini")
    monkeypatch.setenv("ACF_JUDGE_MODEL", "gemini-2.5-pro")
    monkeypatch.setenv("GOOGLE_API_KEY", "goog-456")
    p2 = resolve_provider(has_enforced=True)
    assert isinstance(p2, GeminiProvider)
    assert p2.api_key == "goog-456"
    assert p2.model == "gemini-2.5-pro"

    # Explicit args override env vars
    p3 = resolve_provider(
        provider_name="anthropic",
        model="claude-opus-4-6",
        has_enforced=True,
    )
    assert isinstance(p3, AnthropicProvider)
    assert p3.model == "claude-opus-4-6"


def test_provider_constructors_reject_empty_key_or_model() -> None:
    with pytest.raises(JudgeNotConfiguredError):
        AnthropicProvider(api_key="   ")
    with pytest.raises(JudgeNotConfiguredError):
        AnthropicProvider(api_key="sk-ant", model="  ")
    with pytest.raises(JudgeNotConfiguredError):
        GeminiProvider(api_key="")
    with pytest.raises(JudgeNotConfiguredError):
        GeminiProvider(api_key="gem-key", model="")


def test_anthropic_provider_http_and_review(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            pass

        def json(self) -> dict:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "violation": True,
                                "severity": "BLOCK",
                                "confidence": "high",
                                "message": "React view fetches directly",
                                "path": "src/View.tsx",
                                "line": 15,
                            }
                        ),
                    }
                ]
            }

    class FakeClient:
        def __init__(self, *, timeout: float) -> None:
            captured["timeout"] = timeout

        def __enter__(self) -> FakeClient:
            return self

        def __exit__(self, *args: object) -> None:
            pass

        def post(self, url: str, *, headers: dict, json: dict) -> FakeResponse:
            captured["url"] = url
            captured["headers"] = headers
            captured["json"] = json
            return FakeResponse()

    monkeypatch.setattr(httpx, "Client", FakeClient)
    provider = AnthropicProvider(api_key="sk-ant-test", model="claude-sonnet-4-6")
    res = provider.review(diff_text="+ fetch('/api')", mandate=_llm_mandate())
    assert res is not None
    assert res.mandate_id == "soft.react-boundaries"
    assert res.severity == "BLOCK"
    assert res.confidence == "high"
    assert res.path == "src/View.tsx"
    assert res.line == 15
    assert captured["url"] == "https://api.anthropic.com/v1/messages"
    assert captured["headers"]["x-api-key"] == "sk-ant-test"
    assert captured["headers"]["anthropic-version"] == "2023-06-01"
    assert captured["json"]["model"] == "claude-sonnet-4-6"
    assert captured["json"]["temperature"] == 0


def test_provider_http_error_translates_to_judge_response_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FailingClient:
        def __init__(self, *, timeout: float) -> None:
            pass

        def __enter__(self) -> FailingClient:
            return self

        def __exit__(self, *args: object) -> None:
            pass

        def post(self, *args: object, **kwargs: object) -> object:
            raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(httpx, "Client", FailingClient)
    with pytest.raises(JudgeResponseError, match="Anthropic HTTP/JSON failure"):
        AnthropicProvider(api_key="sk-ant").review(
            diff_text="...", mandate=_llm_mandate()
        )
    with pytest.raises(JudgeResponseError, match="Gemini HTTP/JSON failure"):
        GeminiProvider(api_key="gem-key").review(
            diff_text="...", mandate=_llm_mandate()
        )


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


def test_llm_warn_severity_demotes_block_even_at_high_confidence() -> None:
    """The judge's own WARN verdict must not be silently escalated back to
    BLOCK by the mandate row."""
    mandate = _llm_mandate(severity="BLOCK")

    class WarnProvider:
        def review(self, *, diff_text: str, mandate: Mandate) -> JudgeResult:
            return JudgeResult(
                mandate_id=mandate.id,
                severity="WARN",
                confidence="high",
                message="Borderline; not blocking",
                path="src/App.tsx",
                line=9,
            )

    findings = run_judge(diff_text="...", mandates=[mandate], provider=WarnProvider())
    assert len(findings) == 1
    assert findings[0].severity == Severity.WARN


def test_malformed_provider_responses_raise_response_error() -> None:
    mandate = _llm_mandate()
    with pytest.raises(JudgeResponseError):
        _parse_json_object("this is not json at all")
    with pytest.raises(JudgeResponseError):
        _parse_json_object("prose before {not: valid json} prose after")
    with pytest.raises(JudgeResponseError):
        _extract_text({"unexpected": "shape"})
    with pytest.raises(JudgeResponseError):
        _extract_anthropic_text({"unexpected": "shape"})
    with pytest.raises(JudgeResponseError):
        _extract_anthropic_text({"content": [{"type": "text", "text": ""}]})
    with pytest.raises(JudgeResponseError):
        _result_from_text(
            json.dumps({"violation": True, "confidence": "invalid-level"}),
            mandate,
        )
    with pytest.raises(JudgeResponseError):
        _result_from_text(
            json.dumps({"violation": True, "severity": None, "confidence": "high"}),
            mandate,
        )


def test_response_error_is_not_configuration_error() -> None:
    assert not issubclass(JudgeResponseError, JudgeNotConfiguredError)


def test_cli_check_llm_forwards_provider_and_model(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    diff_file = tmp_path / "sample.diff"
    diff_file.write_text("diff --git a/a.py b/a.py\n", encoding="utf-8")
    mandates_file = tmp_path / "mandates.yml"
    mandates_file.write_text(
        "- id: soft.fail-loud\n"
        "  title: Soft fail-loud\n"
        "  severity: WARN\n"
        "  detection: llm\n"
        "  detector: llm_fail_loud\n"
        "  languages: python\n"
        "  call_sites: [ci]\n"
        "  exemption_tokens: []\n"
        "  status: unenforced\n"
        "  arch_anchor: '## Fail loud'\n",
        encoding="utf-8",
    )
    called: dict = {}

    def fake_run_judge(
        diff_text: str,
        mandates: list[Mandate],
        provider: object = None,
        *,
        provider_name: str | None = None,
        model: str | None = None,
    ) -> list:
        called["provider_name"] = provider_name
        called["model"] = model
        return []

    monkeypatch.setattr(cli_check_llm, "run_judge", fake_run_judge)
    rc = cli_check_llm.main(
        [
            "--diff-file",
            str(diff_file),
            "--mandates",
            str(mandates_file),
            "--provider",
            "gemini",
            "--model",
            "gemini-2.5-flash",
        ]
    )
    assert rc == 0
    assert called["provider_name"] == "gemini"
    assert called["model"] == "gemini-2.5-flash"


def test_corpus_fixtures_with_fake_provider() -> None:
    files = sorted(CORPUS.glob("*.json"))
    assert len(files) >= 8
    python_n = sum(
        1
        for p in files
        if json.loads(p.read_text(encoding="utf-8"))["language"] == "python"
    )
    ts_n = sum(
        1
        for p in files
        if json.loads(p.read_text(encoding="utf-8"))["language"] == "typescript"
    )
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
