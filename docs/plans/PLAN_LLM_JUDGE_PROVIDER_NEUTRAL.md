# Plan: Tier-2 LLM Judge — Provider-Neutral Contract (`anthropic` Default + `gemini`)

**Status:** Executed
**Date:** 2026-11-02
**Spec:** `docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md` (CLEARED_WITH_ABSORPTIONS @ `08bcabe`)

## Files to Modify

| File | Action | Task |
|---|---|---|
| `plugins/arch-compliance/tests/test_judge.py` | **Modify.** Add TDD contract tests for `AnthropicProvider`, `GeminiProvider`, `resolve_api_key`, `resolve_provider`, zero cross-provider fallback, whitespace-only env vars, HTTP/JSON/Pydantic `JudgeResponseError` handling, and `cli_check_llm.main` `--provider` / `--model` flags. | Task 1 |
| `plugins/arch-compliance/python/acf/judge.py` | **Modify.** Add `ProviderName`, `PROVIDER_NAMES`, `DEFAULT_PROVIDER`, `DEFAULT_ANTHROPIC_MODEL`, `DEFAULT_GEMINI_MODEL`, `AnthropicProvider`, `_extract_anthropic_text`, `_result_from_text`, `resolve_api_key(provider_name)`, and `resolve_provider`; harden `GeminiProvider`, `_extract_text`, and `_parse_json_object`. | Task 2 |
| `plugins/arch-compliance/python/acf/cli_check_llm.py` | **Modify.** Add `--provider` (`choices=PROVIDER_NAMES`) and `--model` flags and pass `provider_name=args.provider, model=args.model` to `run_judge`. | Task 2 |
| `config/architecture/ARCHITECTURE.md` | **Modify.** Record the Tier-2 judge's provider and model defaults in `## Declared, never defaulted` (`:118-128`). | Task 3 |
| `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md` | **Modify.** Update §Tier 2 line 133 from Gemini-only default to provider-neutral (`Anthropic default`, `Gemini supported`). | Task 3 |
| `README.md` | **Modify.** Update `## Environment variables` (`:38-45`) to document `ACF_JUDGE_PROVIDER`, `ACF_JUDGE_MODEL`, `ANTHROPIC_API_KEY`, and `GEMINI_API_KEY` / `GOOGLE_API_KEY`. | Task 3 |
| `docs/guides/SUPERPOWERS_COMPLEMENT.md` | **Modify.** Update `## Environment variables` (`:46-53`) to match `README.md`. | Task 3 |

## Task 1 — Write Failing Tests (`plugins/arch-compliance/tests/test_judge.py`)

1. Add tests covering:
   - `DEFAULT_PROVIDER == "anthropic"`, `DEFAULT_ANTHROPIC_MODEL == "claude-sonnet-4-6"`, `DEFAULT_GEMINI_MODEL == "gemini-2.0-flash"`, `PROVIDER_NAMES == ("anthropic", "gemini")`.
   - Default provider (`"anthropic"`) raises `JudgeNotConfiguredError` on `enforced` LLM mandate when `ANTHROPIC_API_KEY` is unset, even when `GEMINI_API_KEY` and `GOOGLE_API_KEY` are set (zero cross-provider fallback).
   - `provider_name="gemini"` (and `ACF_JUDGE_PROVIDER="gemini"`) raises `JudgeNotConfiguredError` on `enforced` LLM mandate when `GEMINI_API_KEY` and `GOOGLE_API_KEY` are unset, even when `ANTHROPIC_API_KEY` is set.
   - Unknown provider (`provider_name="openai"` or `ACF_JUDGE_PROVIDER="openai"`), empty provider (`provider_name="  "`), or empty model (`model="  "`) raises `JudgeNotConfiguredError` even when LLM mandates are `status="unenforced"`.
   - Whitespace-only API keys (`ANTHROPIC_API_KEY="   "`, `GEMINI_API_KEY="   "`) are treated as `None` and raise `JudgeNotConfiguredError` on `enforced` LLM mandates.
   - `AnthropicProvider` and `GeminiProvider` constructors reject empty/whitespace `api_key` or `model` with `JudgeNotConfiguredError`.
   - `AnthropicProvider.review` sends `POST https://api.anthropic.com/v1/messages` with `x-api-key`, `anthropic-version: 2023-06-01`, `model`, `max_tokens: 1024`, `temperature: 0`, and parses `content[0].text` into `JudgeResult | None`; HTTP errors raise `JudgeResponseError`.
   - `GeminiProvider.review` sends `POST` to `_GEMINI_URL` with `params={"key": ...}` and parses `candidates[0].content.parts` into `JudgeResult | None`; HTTP errors raise `JudgeResponseError`.
   - `_extract_anthropic_text`, `_extract_text`, `_parse_json_object` (including malformed JSON inside `{...}` braces), and `_result_from_text` (including `confidence="invalid"` and explicit `severity=None` / `confidence=None`) raise `JudgeResponseError`.
   - `cli_check_llm.main` parses `--provider` and `--model` and forwards them to `run_judge`.

## Task 2 — Implement Provider-Neutral Judge & CLI (`judge.py`, `cli_check_llm.py`)

1. Implement `ProviderName`, `PROVIDER_NAMES`, `DEFAULT_PROVIDER`, `DEFAULT_ANTHROPIC_MODEL`, `DEFAULT_GEMINI_MODEL`, `_resolve_provider_name`, `_resolve_model`, `resolve_api_key`, `resolve_provider`, `AnthropicProvider`, `GeminiProvider`, `_extract_anthropic_text`, `_extract_text`, `_result_from_text`, and hardened `_parse_json_object` in `plugins/arch-compliance/python/acf/judge.py`.
2. Update `plugins/arch-compliance/python/acf/cli_check_llm.py` to add `--provider` and `--model` and pass `provider_name=args.provider, model=args.model` to `run_judge`.
3. Run `python -m pytest plugins/arch-compliance/tests/test_judge.py -v` and confirm all tests pass.

## Task 3 — Align Doctrine, Design Doc, and Guides (`ARCHITECTURE.md`, `ARCH_COMPLIANCE_FOR_SUPERPOWERS.md`, `README.md`, `SUPERPOWERS_COMPLEMENT.md`)

1. Update `config/architecture/ARCHITECTURE.md` (`## Declared, never defaulted`) to record the Tier-2 judge's provider and model defaults in `plugins/arch-compliance/python/acf/judge.py`.
2. Update `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:133`, `README.md:38-45`, and `docs/guides/SUPERPOWERS_COMPLEMENT.md:46-53`.
3. Run full `PYTHONUTF8=1 python -m pytest` and `PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main`.
