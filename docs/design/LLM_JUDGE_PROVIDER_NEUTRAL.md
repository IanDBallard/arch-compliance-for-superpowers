# Tier-2 LLM Judge — Provider-Neutral Contract (`anthropic` Default + `gemini`)

**Status:** Approved (v1 — absorptions folded in)
**Date:** 2026-11-02
**Base commit:** `80b80f1`
**Adversarial review:** v1 — 2026-11-02, 4 reviewers, CLEARED_WITH_ABSORPTIONS (repo @ 08bcabe6cbd0535bab08d18a726a1f73ff45d5f1)

## 1. Problem

The Tier-2 LLM judge in `plugins/arch-compliance/python/acf/judge.py` defines a
provider-neutral protocol (`JudgeProvider`, `plugins/arch-compliance/python/acf/judge.py:47-48`),
an input/output model (`JudgeResult`, `plugins/arch-compliance/python/acf/judge.py:38-45`),
a confidence-gating conversion (`_to_finding`, `plugins/arch-compliance/python/acf/judge.py:126-143`),
and a prompt renderer (`_build_prompt`, `plugins/arch-compliance/python/acf/judge.py:146-157`),
but hardcodes Google Gemini (`GeminiProvider`, `GEMINI_API_KEY` / `GOOGLE_API_KEY`) as the
runtime implementation in `resolve_api_key` (`plugins/arch-compliance/python/acf/judge.py:51-52`)
and `run_judge` (`plugins/arch-compliance/python/acf/judge.py:106-115`), with no CLI or
environment-variable mechanism to select Anthropic Claude (`AnthropicProvider`) or override
the model in `plugins/arch-compliance/python/acf/cli_check_llm.py:16-50`.

## 2. Diagnosis at `80b80f1`

1. **`JudgeProvider` is already provider-neutral, but default resolution in `run_judge` is coupled to Gemini:**
   - `JudgeProvider` (`plugins/arch-compliance/python/acf/judge.py:47-48`) has a single
     method `def review(self, *, diff_text: str, mandate: Mandate) -> JudgeResult | None: ...`.
   - `resolve_api_key()` (`plugins/arch-compliance/python/acf/judge.py:51-52`) takes no
     provider parameter and reads `os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")`.
   - When `provider is None`, `run_judge` (`plugins/arch-compliance/python/acf/judge.py:106-115`)
     calls `resolve_api_key()`, raises `JudgeNotConfiguredError` at lines 109-112 if
     `enforced_llm` is non-empty and `not api_key`, returns `[]` at lines 113-114 if
     `not api_key`, and instantiates `GeminiProvider(api_key=api_key)` at line 115.
2. **Response parsing and `JudgeResult` construction inside `GeminiProvider.review` leave three error-surface gaps:**
   - `GeminiProvider.review` (`plugins/arch-compliance/python/acf/judge.py:72-80`) calls
     `client.post(...)`, `response.raise_for_status()`, and `response.json()` without
     translating `httpx.HTTPError` or `ValueError` into `JudgeResponseError`
     (`plugins/arch-compliance/python/acf/exceptions.py:21-22`).
   - `_parse_json_object` (`plugins/arch-compliance/python/acf/judge.py:168-179`) catches
     `json.JSONDecodeError` on `json.loads(text)` at lines 170-172 and extracts a `{...}`
     substring via `re.search(r"\{.*\}", text, flags=re.DOTALL)` at line 173, but calls
     `json.loads(match.group(0))` at line 176 outside a `try` block; if the matched braces
     contain invalid JSON, a raw `json.JSONDecodeError` escapes instead of
     `JudgeResponseError`.
   - `GeminiProvider.review` (`plugins/arch-compliance/python/acf/judge.py:85-92`) constructs
     `JudgeResult(...)` directly from `data.get(...)`; if the LLM returns an invalid
     literal for `severity` or `confidence` (or `null` when the key is present in `data`),
     Pydantic raises `ValidationError` rather than `JudgeResponseError`, and duplicating
     lines 82-92 in a second provider class would create two owners for JSON-to-`JudgeResult`
     materialization (`config/architecture/ARCHITECTURE.md:188-192`, `## Single point of definition`).
3. **`cli_check_llm.py` exposes no provider or model arguments:**
   - `main` (`plugins/arch-compliance/python/acf/cli_check_llm.py:16-35`) defines
     `--diff-file`, `--mandates`, and `--json`, and calls `run_judge(diff_text, registry.mandates)`
     at line 49 with no provider or model arguments.
4. **Documentation and doctrine touchpoints name Gemini as the sole default:**
   - `plugins/arch-compliance/python/acf/judge.py:1` module docstring reads
     `"""Tier 2 LLM judge with confidence gating (Gemini default)."""`.
   - `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:133` reads
     `- Provider interface; **Gemini default**; API key via environment.`.
   - `README.md:38-45` and `docs/guides/SUPERPOWERS_COMPLEMENT.md:46-53` list
     `GEMINI_API_KEY` and `GOOGLE_API_KEY` in their environment variable tables.
   - `config/architecture/ARCHITECTURE.md:118-128` (`## Declared, never defaulted`) scopes
     its rule to `config/architecture/adr.yml` and records two package defaults outside
     that rule (`plugins/arch-compliance/python/acf/repo.py:23-26` and
     `plugins/arch-compliance/python/acf/repo.py:32-44`), without recording the Tier-2
     judge's provider/model defaults in `plugins/arch-compliance/python/acf/judge.py`.

## 3. Scope and Non-Goals

### In Scope
- Supporting two concrete `JudgeProvider` implementations in
  `plugins/arch-compliance/python/acf/judge.py`: `AnthropicProvider` (default,
  `claude-sonnet-4-6`) and `GeminiProvider` (`gemini-2.0-flash`).
- Deterministic provider and model resolution (`resolve_provider`, `resolve_api_key`)
  controlled by explicit parameters (`provider_name`, `model` on `run_judge` and
  `--provider`, `--model` on `acf-check-llm`) and environment variables
  (`ACF_JUDGE_PROVIDER`, `ACF_JUDGE_MODEL`), with **zero cross-provider fallback**.
- Consolidating response-text-to-`JudgeResult` parsing into one helper
  (`_result_from_text`) and normalizing HTTP, JSON, and Pydantic validation failures on
  provider responses into `JudgeResponseError`.
- Updating `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:133`,
  `config/architecture/ARCHITECTURE.md:118-128`, `README.md:38-45`, and
  `docs/guides/SUPERPOWERS_COMPLEMENT.md:46-53` so no document conflicts with the
  provider-neutral contract.

### Non-Goals
- Adding third-party provider SDK dependencies (`anthropic`, `google-genai`): both
  providers use `httpx.Client` (`pyproject.toml:9`, `httpx>=0.27`).
- Changing the Tier-2 judge prompt template (`plugins/arch-compliance/python/acf/judge_prompt.md`),
  `LLM_PROMPT_IDS` (`plugins/arch-compliance/python/acf/judge.py:23-30`), or
  confidence-gating semantics (`_to_finding`, `plugins/arch-compliance/python/acf/judge.py:126-143`).
- Modifying any skill under `plugins/arch-compliance/skills/`: no skill file names
  `GEMINI_API_KEY`, `GOOGLE_API_KEY`, `GeminiProvider`, or `gemini-2.0-flash` (verified by
  recipe in §A.1).

## 4. Design

### 4.1 Provider & Model Constants and Resolution (`plugins/arch-compliance/python/acf/judge.py`)

`plugins/arch-compliance/python/acf/judge.py` defines:

```python
ProviderName = Literal["anthropic", "gemini"]
PROVIDER_NAMES: tuple[ProviderName, ...] = ("anthropic", "gemini")

DEFAULT_PROVIDER: ProviderName = "anthropic"
DEFAULT_ANTHROPIC_MODEL: str = "claude-sonnet-4-6"
DEFAULT_GEMINI_MODEL: str = "gemini-2.0-flash"
```

1. **Provider name resolution (`_resolve_provider_name(provider_name: str | None) -> ProviderName`):**
   - If `provider_name is not None`: `raw = provider_name.strip()`. If `not raw`, raise
     `JudgeNotConfiguredError("judge provider name must not be empty")`.
   - Else: `env_raw = (os.environ.get("ACF_JUDGE_PROVIDER") or "").strip()`, and
     `raw = env_raw if env_raw else DEFAULT_PROVIDER`.
   - If `raw not in PROVIDER_NAMES`: raise
     `JudgeNotConfiguredError(f"unknown judge provider {raw!r}; expected one of {PROVIDER_NAMES}")`.
2. **API key resolution (`resolve_api_key(provider_name: ProviderName) -> str | None`):**
   - Takes a required `provider_name: ProviderName` argument (no default argument).
   - When `provider_name == "anthropic"`: reads `(os.environ.get("ANTHROPIC_API_KEY") or "").strip() or None`.
   - When `provider_name == "gemini"`: reads
     `(os.environ.get("GEMINI_API_KEY") or "").strip() or (os.environ.get("GOOGLE_API_KEY") or "").strip() or None`.
   - If `provider_name not in PROVIDER_NAMES`: raises `JudgeNotConfiguredError`.
   - **Zero cross-provider fallback:** `"anthropic"` never inspects `GEMINI_API_KEY` or
     `GOOGLE_API_KEY`; `"gemini"` never inspects `ANTHROPIC_API_KEY`.
3. **Model resolution (`_resolve_model(provider_name: ProviderName, model: str | None) -> str`):**
   - If `model is not None`: `cleaned = model.strip()`. If `not cleaned`, raise
     `JudgeNotConfiguredError("judge model name must not be empty")`. Return `cleaned`.
   - Else: `env_model = (os.environ.get("ACF_JUDGE_MODEL") or "").strip()`. If `env_model`,
     return `env_model`.
   - Else: return `DEFAULT_ANTHROPIC_MODEL` when `provider_name == "anthropic"` and
     `DEFAULT_GEMINI_MODEL` when `provider_name == "gemini"`.
4. **Provider factory (`resolve_provider(*, provider_name: str | None = None, model: str | None = None, has_enforced: bool) -> JudgeProvider | None`):**
   - Resolves `resolved_name = _resolve_provider_name(provider_name)` and
     `resolved_model = _resolve_model(resolved_name, model)` first so invalid provider or
     model arguments fail loud even when no mandate is `status: enforced`.
   - Calls `api_key = resolve_api_key(resolved_name)`.
   - If `api_key is None`:
     - If `has_enforced`: raises `JudgeNotConfiguredError` naming the active provider and
       its required environment variable (`ANTHROPIC_API_KEY` for `"anthropic"`,
       `GEMINI_API_KEY or GOOGLE_API_KEY` for `"gemini"`).
     - Else: returns `None` (no enforced `detection: llm` mandate requires a live call).
   - Returns `AnthropicProvider(api_key=api_key, model=resolved_model)` when
     `resolved_name == "anthropic"` and `GeminiProvider(api_key=api_key, model=resolved_model)`
     when `resolved_name == "gemini"`.
5. **`run_judge` signature and dispatch (`plugins/arch-compliance/python/acf/judge.py`):**
   ```python
   def run_judge(
       diff_text: str,
       mandates: list[Mandate],
       provider: JudgeProvider | None = None,
       *,
       provider_name: str | None = None,
       model: str | None = None,
   ) -> list[Finding]:
   ```
   - Filters `llm_mandates = [m for m in mandates if m.detection == "llm"]`; if empty,
     returns `[]`.
   - Computes `enforced_llm = [m for m in llm_mandates if m.status == "enforced"]`.
   - When `provider is None`: calls
     `resolved = resolve_provider(provider_name=provider_name, model=model, has_enforced=bool(enforced_llm))`;
     if `resolved is None`, returns `[]`.

### 4.2 `AnthropicProvider` and `GeminiProvider` HTTP & Response Contract (`plugins/arch-compliance/python/acf/judge.py`)

Both concrete provider classes validate their constructor inputs so direct callers cannot
construct an unconfigured instance:
- `if not api_key or not api_key.strip(): raise JudgeNotConfiguredError(...)`
- `if not model or not model.strip(): raise JudgeNotConfiguredError(...)`

1. **`AnthropicProvider`:**
   - Endpoint constant: `_ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"` and
     `_ANTHROPIC_VERSION = "2023-06-01"`.
   - Constructor: `def __init__(self, api_key: str, model: str = DEFAULT_ANTHROPIC_MODEL) -> None`.
   - `review(self, *, diff_text: str, mandate: Mandate) -> JudgeResult | None`:
     - Renders `prompt = _build_prompt(diff_text=diff_text, mandate=mandate)`.
     - Sends `POST` via `httpx.Client(timeout=60.0)` to `_ANTHROPIC_URL` with headers
       `{"x-api-key": self.api_key, "anthropic-version": _ANTHROPIC_VERSION, "content-type": "application/json"}`
       and JSON body
       `{"model": self.model, "max_tokens": 1024, "temperature": 0, "messages": [{"role": "user", "content": prompt}]}`.
     - Catches `(httpx.HTTPError, ValueError)` around the request, `response.raise_for_status()`,
       and `response.json()`, raising `JudgeResponseError(f"Anthropic HTTP/JSON failure: {e}") from e`.
     - Extracts text via `_extract_anthropic_text(body)` and returns `_result_from_text(text, mandate)`.
   - `_extract_anthropic_text(body: dict) -> str`:
     - Verifies `isinstance(body, dict)` and `isinstance(body.get("content"), list)` with
       at least one element; collects `block["text"]` from dict elements where
       `block.get("type") == "text"` and `isinstance(block.get("text"), str)`.
     - Joins collected strings; if the joined string is empty or the shape check fails,
       raises `JudgeResponseError("unexpected Anthropic response shape")`.

2. **`GeminiProvider`:**
   - Endpoint constant: `_GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"`.
   - Constructor: `def __init__(self, api_key: str, model: str = DEFAULT_GEMINI_MODEL) -> None`.
   - `review(self, *, diff_text: str, mandate: Mandate) -> JudgeResult | None`:
     - Renders `prompt = _build_prompt(diff_text=diff_text, mandate=mandate)`.
     - Sends `POST` via `httpx.Client(timeout=60.0)` to `_GEMINI_URL.format(model=self.model)`
       with `params={"key": self.api_key}` and existing `payload`.
     - Catches `(httpx.HTTPError, ValueError)` around the request, `response.raise_for_status()`,
       and `response.json()`, raising `JudgeResponseError(f"Gemini HTTP/JSON failure: {e}") from e`.
     - Extracts text via `_extract_text(body)` and returns `_result_from_text(text, mandate)`.
   - `_extract_text(body: dict) -> str`:
     - Extracts `parts = body["candidates"][0]["content"]["parts"]` as before and also raises
       `JudgeResponseError` if `not isinstance(parts, list)` or the joined text is empty.

### 4.3 Shared Prompt & Result Materialization (`_result_from_text`, `_parse_json_object`)

To satisfy `## Single point of definition` (`config/architecture/ARCHITECTURE.md:188-192`)
and close the two parser/validation escape paths diagnosed in §2 item 2:

1. **`_parse_json_object(text: str) -> dict`:**
   - Strips `text`. Attempts `json.loads(text)`.
   - On `json.JSONDecodeError`, searches `re.search(r"\{.*\}", text, flags=re.DOTALL)`. If
     no match, raises `JudgeResponseError("judge response was not JSON") from None`.
   - Wraps `json.loads(match.group(0))` in `try ... except json.JSONDecodeError as e: raise JudgeResponseError(f"judge response contained invalid JSON: {e}") from e`.
   - If `not isinstance(data, dict)`, raises `JudgeResponseError("judge JSON root must be an object")`.
2. **`_result_from_text(text: str, mandate: Mandate) -> JudgeResult | None`:**
   - Calls `data = _parse_json_object(text)`.
   - If `not data.get("violation", False)`, returns `None`.
   - Uses `data.get("severity", mandate.severity)` and `data.get("confidence", "low")` so
     omitted keys take the mandate/low default, whereas an explicit JSON `null` (`None`) or
     invalid literal is refused rather than silently repaired.
   - Constructs `JudgeResult(...)` inside `try ... except ValidationError as e: raise JudgeResponseError(f"invalid judge result fields: {e}") from e`.

### 4.4 CLI Wiring (`plugins/arch-compliance/python/acf/cli_check_llm.py`)

`plugins/arch-compliance/python/acf/cli_check_llm.py` imports `PROVIDER_NAMES` and
`run_judge` from `acf.judge` and adds two optional CLI flags to `ArgumentParser(prog="acf-check-llm")`:

- `--provider`: `choices=PROVIDER_NAMES`, `default=None`,
  `help="LLM judge provider (default: ACF_JUDGE_PROVIDER or 'anthropic')"`.
- `--model`: `type=str`, `default=None`,
  `help="LLM model override (default: ACF_JUDGE_MODEL or provider default)"`.

Line 49 of `plugins/arch-compliance/python/acf/cli_check_llm.py` becomes:

```python
findings = run_judge(
    diff_text,
    registry.mandates,
    provider_name=args.provider,
    model=args.model,
)
```

The `--mandates` help string on `plugins/arch-compliance/python/acf/cli_check_llm.py:28`
(`help="Path to mandates.yml (default: config/architecture/mandates.yml under cwd)",`) is
preserved verbatim so `ALLOWED_DOC_LINES["python/acf/cli_check_llm.py"]` in
`plugins/arch-compliance/tests/test_repo_paths.py:37-39` remains satisfied.

### 4.5 Doctrine, Design Document, and Guide Alignment

1. **`config/architecture/ARCHITECTURE.md:118-128` (`## Declared, never defaulted`):**
   - Extend the recorded package defaults outside `config/architecture/adr.yml` from two to
     three, adding the Tier-2 LLM judge's provider and model defaults
     (`DEFAULT_PROVIDER = "anthropic"`, `DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-6"`,
     `DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"` in
     `plugins/arch-compliance/python/acf/judge.py`), while stating that provider API keys
     are never defaulted or cross-provider-fallback-resolved.
2. **`docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:133` (`### Tier 2 — LLM judgment layer (full)`):**
   - Replace `- Provider interface; **Gemini default**; API key via environment.` with:
     `- Provider interface; **Anthropic default (`claude-sonnet-4-6`)**, **Gemini supported (`gemini-2.0-flash`)**; provider/model selectable via `--provider` / `ACF_JUDGE_PROVIDER` and `--model` / `ACF_JUDGE_MODEL`; API key via provider-specific environment variable with no cross-provider fallback.`
3. **`README.md:38-45` and `docs/guides/SUPERPOWERS_COMPLEMENT.md:46-53` (`## Environment variables`):**
   - Document `ACF_JUDGE_PROVIDER` (`anthropic` default, or `gemini`), `ACF_JUDGE_MODEL`
     (optional model override), `ANTHROPIC_API_KEY` (required when provider is
     `anthropic`), and `GEMINI_API_KEY` / `GOOGLE_API_KEY` (required when provider is
     `gemini`), noting that missing the active provider's key hard-fails when any
     `detection: llm` mandate is `status: enforced` (with no cross-provider fallback).

## 5. Document Relationships

| Document | Relationship | Scope & Disposition |
|---|---|---|
| `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md` | `ADJACENT` | Parent v1 architecture spec for the 3-tier plugin; §Tier 2 line 133 is updated in lockstep (§4.5 item 2) so the parent spec and this Tier-2 provider spec do not conflict. Kept separate because `ARCH_COMPLIANCE_FOR_SUPERPOWERS.md` covers the whole plugin (Tier 1, Tier 2, Tier 3, hooks, skills, profiles). |
| `docs/design/ADR_GATE_HOST_CONTRACT.md` | `DISJOINT` | Governs the adversarial-design-review gate (`acf.adr`). Its §4.2 table row at line 221 and §A receipt at line 512 record historical grep hits for `GEMINI` in `judge.py` at the Phase 1d commit to explain why `judge.py` was not an origin-host `GEMINI.md` leak. |
| `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` | `DISJOINT` | Governs self-hosting this repository under its own gate (`config/architecture/`). Its §4.1 item 15 (line 199) and §A receipt (line 632) record a historical grep at `c0281bf` for `arch_anchor` matching `judge.py:154`. |

## 6. Doctrine Compliance

| Doctrine Anchor (`config/architecture/ARCHITECTURE.md`) | Mandate ID (`config/architecture/mandates.yml`) | How This Design Complies |
|---|---|---|
| `## Fail loud` (`:24-41`) | `fail-loud.bare-except` | No bare `except:` or silent broad catches. Missing API keys for `status: enforced` LLM mandates, empty/whitespace provider or model arguments, and unknown provider names raise `JudgeNotConfiguredError`. HTTP errors, invalid JSON, empty content blocks, and Pydantic validation errors on judge responses raise `JudgeResponseError`. |
| `## No shims` (`:43-53`) | `no-shims.hasattr` | Zero cross-provider fallback (`anthropic` never falls back to `GEMINI_API_KEY`; `gemini` never falls back to `ANTHROPIC_API_KEY`). `resolve_api_key(provider_name: ProviderName)` takes a required parameter with no legacy zero-arg wrapper. |
| `## POSIX paths` (`:55-64`) | `posix-paths.str-serialization` | No `str(path)` into YAML/JSON serialization. |
| `## One base exception` (`:99-103`) | `plugin.one-base-exception` | Reuses `JudgeNotConfiguredError` and `JudgeResponseError` (`plugins/arch-compliance/python/acf/exceptions.py:17-22`), both of which subclass `AcfError` alone. |
| `## One owner for host paths` (`:105-116`) | `plugin.one-owner-host-paths` | `cli_check_llm.py:40` continues to resolve `MANDATES_REL` via `acf.repo`, and `cli_check_llm.py:28` keeps its exact allowlisted `--mandates` help string in `plugins/arch-compliance/tests/test_repo_paths.py:37-39`. |
| `## Declared, never defaulted` (`:118-128`) | `plugin.declared-never-defaulted` | `config/architecture/adr.yml` host declarations are untouched; the Tier-2 judge's CLI/env provider and model defaults in `plugins/arch-compliance/python/acf/judge.py` are explicitly recorded in `config/architecture/ARCHITECTURE.md` `## Declared, never defaulted`. |
| `## Prose names no host` (`:130-136`) | `plugin.adr-code-names-no-host`, `plugin.gate-prose-names-no-host` | Neither `acf/adr/` nor any skill prose under `plugins/arch-compliance/skills/` is modified, and runtime messages in `acf/judge.py` and `acf/cli_check_llm.py` name no host repository, path, or section. |
| `## Live consumers` (`:146-150`) | *(doctrine rule)* | `PROVIDER_NAMES` and `run_judge` are consumed by `plugins/arch-compliance/python/acf/cli_check_llm.py`; `LLM_PROMPT_IDS` is consumed by `plugins/arch-compliance/python/acf/cli_check_diff.py:21, 25`; `DEFAULT_PROVIDER`, `DEFAULT_ANTHROPIC_MODEL`, `DEFAULT_GEMINI_MODEL`, `AnthropicProvider`, `GeminiProvider`, `resolve_api_key`, and `resolve_provider` are called in the runtime resolution chain `cli_check_llm.main -> run_judge -> resolve_provider -> resolve_api_key`. |
| `## Declared text decoding` (`:164-175`) | *(doctrine rule)* | `_PROMPT_TEMPLATE.read_text(encoding="utf-8")` in `judge.py` and `args.diff_file.read_text(encoding="utf-8")` in `cli_check_llm.py` declare `encoding="utf-8"`. |
| `## Single point of definition` (`:188-200`) | *(doctrine rule)* | Both `AnthropicProvider.review` and `GeminiProvider.review` delegate prompt rendering to `_build_prompt` and response-text-to-`JudgeResult` parsing/validation to `_result_from_text` (which delegates JSON extraction to `_parse_json_object`). |

## 7. Mechanism and Hardening Trace

| Added / Updated Mechanism | Producer (`file:line` target) | Consumer (`file:line` target) | Failure-Mode Guard |
|---|---|---|---|
| `resolve_provider` & `resolve_api_key` | `plugins/arch-compliance/python/acf/cli_check_llm.py` (`main` passing `provider_name=args.provider, model=args.model` into `run_judge`) | `plugins/arch-compliance/python/acf/judge.py` (`run_judge` calling `resolve_provider` and invoking `resolved.review(...)`) | Rejects unknown/empty provider names and empty explicit models with `JudgeNotConfiguredError`; strips whitespace from env vars so whitespace-only keys are treated as `None`; never falls back across providers. |
| `AnthropicProvider` (`review` + `_extract_anthropic_text`) | `plugins/arch-compliance/python/acf/judge.py` (`resolve_provider` returning `AnthropicProvider(api_key=..., model=...)`) | `plugins/arch-compliance/python/acf/judge.py` (`run_judge` calling `resolved.review(diff_text=diff_text, mandate=mandate)`) | Constructor rejects empty/whitespace `api_key` or `model` with `JudgeNotConfiguredError`; HTTP/JSON failures raise `JudgeResponseError`; missing/empty `content` text blocks raise `JudgeResponseError`. |
| `_result_from_text` & hardened `_parse_json_object` | `plugins/arch-compliance/python/acf/judge.py` (`AnthropicProvider.review` and `GeminiProvider.review`) | `plugins/arch-compliance/python/acf/judge.py` (`run_judge` receiving `JudgeResult \| None` and passing to `_to_finding`) | Catches `json.JSONDecodeError` on both raw text and regex-extracted `{...}` block, and catches Pydantic `ValidationError` on `JudgeResult`, raising `JudgeResponseError`. |

## 8. Verification and Definition of Done

1. **Unit & contract tests (`plugins/arch-compliance/tests/test_judge.py`):**
   - Default provider is `"anthropic"` (`DEFAULT_PROVIDER == "anthropic"`, `DEFAULT_ANTHROPIC_MODEL == "claude-sonnet-4-6"`, `DEFAULT_GEMINI_MODEL == "gemini-2.0-flash"`).
   - When `provider` is omitted and `ACF_JUDGE_PROVIDER` is unset, `run_judge` with an `enforced` LLM mandate raises `JudgeNotConfiguredError` when `ANTHROPIC_API_KEY` is unset — even when `GEMINI_API_KEY` and `GOOGLE_API_KEY` are set (proving zero cross-provider fallback).
   - When `provider_name="gemini"` (or `ACF_JUDGE_PROVIDER="gemini"`), `run_judge` with an `enforced` LLM mandate raises `JudgeNotConfiguredError` when `GEMINI_API_KEY` and `GOOGLE_API_KEY` are unset — even when `ANTHROPIC_API_KEY` is set.
   - Unknown provider name (`provider_name="openai"` or `ACF_JUDGE_PROVIDER="openai"`) raises `JudgeNotConfiguredError` even when all LLM mandates are `status: partial` or `status: unenforced` (as long as `llm_mandates` is non-empty).
   - Whitespace-only API keys (`ANTHROPIC_API_KEY="   "`, `GEMINI_API_KEY="   "`) are treated as unset (`None`) and raise `JudgeNotConfiguredError` on `enforced` LLM mandates.
   - `AnthropicProvider` and `GeminiProvider` constructors reject empty/whitespace `api_key` or `model` with `JudgeNotConfiguredError`.
   - `AnthropicProvider.review` sends `POST` to `https://api.anthropic.com/v1/messages` with `x-api-key`, `anthropic-version: 2023-06-01`, `model`, `max_tokens: 1024`, `temperature: 0`, and parses `{"content": [{"type": "text", "text": "..."}]}` into `JudgeResult | None`.
   - `GeminiProvider.review` sends `POST` to `_GEMINI_URL.format(model=...)` with `params={"key": ...}` and parses `candidates[0].content.parts` into `JudgeResult | None`.
   - `_extract_anthropic_text`, `_extract_text`, `_parse_json_object` (including malformed JSON inside `{...}` braces), and `_result_from_text` (including invalid Pydantic field values such as `confidence="invalid"` or `severity=None`) raise `JudgeResponseError`.
   - `cli_check_llm.main` accepts `--provider` (`anthropic`, `gemini`) and `--model` and forwards them to `run_judge`.
2. **Repository-wide test suite and gates:**
   - `PYTHONUTF8=1 python -m pytest` passes across both `plugins/arch-compliance/tests` and `tests`.
   - `PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main` exits `0` with no findings.

## A. Receipts at `80b80f1`

### A.1 Skill prose check for provider/key names

Command:
```bash
git grep -n -i -E "GEMINI_API_KEY|GOOGLE_API_KEY|ANTHROPIC_API_KEY|GeminiProvider|AnthropicProvider|gemini-2\.0-flash" -- plugins/arch-compliance/skills plugins/arch-compliance/hooks
```
Output at `80b80f1`: empty (exit code 1, 0 matches).

### A.2 `resolve_api_key` call sites across repository

Command:
```bash
git grep -n "resolve_api_key" -- plugins/ tests/ scripts/
```
Output at `80b80f1`:
```text
plugins/arch-compliance/python/acf/judge.py:51:def resolve_api_key() -> str | None:
plugins/arch-compliance/python/acf/judge.py:107:        api_key = resolve_api_key()
```

### A.3 `_extract_text` and `_parse_json_object` call sites across repository

Command:
```bash
git grep -n -E "_extract_text|_parse_json_object" -- plugins/ tests/ scripts/
```
Output at `80b80f1`:
```text
plugins/arch-compliance/python/acf/judge.py:81:        text = _extract_text(body)
plugins/arch-compliance/python/acf/judge.py:82:        data = _parse_json_object(text)
plugins/arch-compliance/python/acf/judge.py:160:def _extract_text(body: dict) -> str:
plugins/arch-compliance/python/acf/judge.py:168:def _parse_json_object(text: str) -> dict:
plugins/arch-compliance/tests/test_judge.py:13:    _extract_text,
plugins/arch-compliance/tests/test_judge.py:14:    _parse_json_object,
plugins/arch-compliance/tests/test_judge.py:138:        _parse_json_object("this is not json at all")
plugins/arch-compliance/tests/test_judge.py:140:        _extract_text({"unexpected": "shape"})
```
