# Adversarial design review — full detail

Spec: `docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md` @ `08bcabe6cbd0535bab08d18a726a1f73ff45d5f1`
Kinds: defect, feature
Outcome: **CLEARED_WITH_ABSORPTIONS**
Claims: 23 · Reviewers: 4 · Converged: 1

## Absorptions

- SUBSUMED: 'resolve_provider, _resolve_provider_name, _resolve_model, and resolve_api_key(provider_name) (plugins/arch-compliance/python/acf/judge.py)' shares responsibility 'Resolve the active Tier-2 judge provider, model, and API key from explicit arguments or environment variables and fail loud on missing credentials for enforced LLM mandates' with plugins/arch-compliance/python/acf/judge.py:51 — Replace the zero-argument Gemini-only resolve_api_key() at plugins/arch-compliance/python/acf/judge.py:51-52 and the inline GeminiProvider wiring in run_judge at plugins/arch-compliance/python/acf/judge.py:106-115 with parameterized resolve_api_key(provider_name) and resolve_provider.
- mechanism '_result_from_text null-coalescing on severity and confidence (\'if data.get("severity") is not None else mandate.severity\' and \'if data.get("confidence") is not None else "low"\')' sits at rung 5 when rung 3 applies, with no written justification

## Converged findings

- [2 reviewers: refuter, hardening] Section 3 Non-Goals cites pyproject.toml:14 for httpx>=0.27, which is declared at pyproject.toml:6-10 (line 9).
  - evidence: `pyproject.toml:9`
  - evidence: `docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:84-85`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:38-48, plugins/arch-compliance/python/acf/judge.py:126-157, plugins/arch-compliance/tests/test_judge.py:70-85, plugins/arch-compliance/tests/test_template.py:87-106`
- reasoning: Opened plugins/arch-compliance/python/acf/judge.py and verified JudgeResult is defined at lines 38-45, JudgeProvider(Protocol) with single method review(self, *, diff_text: str, mandate: Mandate) -> JudgeResult | None is at lines 47-48, _to_finding is at lines 126-143, and _build_prompt is at lines 146-157. Corroborated via plugins/arch-compliance/tests/test_judge.py:70-85 (JudgeProvider fake implementation and _to_finding conversion) and plugins/arch-compliance/tests/test_template.py:87-106 (_build_prompt template rendering tests).

#### C2 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:51-52, plugins/arch-compliance/python/acf/judge.py:106-115, plugins/arch-compliance/tests/test_judge.py:48-64`
- reasoning: Opened plugins/arch-compliance/python/acf/judge.py:51-52 confirming resolve_api_key() takes no arguments and returns os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY'), and lines 106-115 confirming run_judge calls resolve_api_key(), raises JudgeNotConfiguredError when enforced_llm is non-empty and not api_key, returns [] when not api_key, and instantiates GeminiProvider(api_key=api_key). Corroborated in plugins/arch-compliance/tests/test_judge.py:48-64 where tests only clear GEMINI_API_KEY and GOOGLE_API_KEY.

#### C3 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:72-80, plugins/arch-compliance/python/acf/exceptions.py:21-22`
- reasoning: Opened plugins/arch-compliance/python/acf/judge.py:72-80 and confirmed GeminiProvider.review calls client.post(...), response.raise_for_status(), and response.json() directly inside a with httpx.Client(timeout=60.0) block without catching httpx.HTTPError or ValueError/json.JSONDecodeError or translating them into JudgeResponseError (defined at plugins/arch-compliance/python/acf/exceptions.py:21-22).

#### C4 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:168-179, plugins/arch-compliance/tests/test_judge.py:136-138`
- reasoning: Opened plugins/arch-compliance/python/acf/judge.py:168-179 and verified _parse_json_object catches json.JSONDecodeError on json.loads(text) at lines 170-172 and extracts a brace substring via re.search(r'\{.*\}', text, flags=re.DOTALL) at line 173, but calls json.loads(match.group(0)) at line 176 outside any try block, allowing raw json.JSONDecodeError to escape when matched braces contain invalid JSON. Corroborated by plugins/arch-compliance/tests/test_judge.py:136-138 which only tests brace-free input.

#### C5 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:85-92, plugins/arch-compliance/python/acf/judge.py:38-45, plugins/arch-compliance/python/acf/exceptions.py:21-22`
- reasoning: Opened plugins/arch-compliance/python/acf/judge.py:85-92 and confirmed GeminiProvider.review constructs JudgeResult directly using data.get('severity', mandate.severity) and data.get('confidence', 'low') without a try/except ValidationError block. Because JudgeResult (lines 38-45) requires Literal['BLOCK', 'WARN'] for severity and Confidence ('high'|'medium'|'low') for confidence, an explicit null or invalid literal in data raises raw pydantic.ValidationError instead of JudgeResponseError (plugins/arch-compliance/python/acf/exceptions.py:21-22).

#### C6 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_llm.py:16-50, plugins/arch-compliance/python/acf/judge.py:95-99, pyproject.toml:20`
- reasoning: Opened plugins/arch-compliance/python/acf/cli_check_llm.py:16-50 and verified ArgumentParser(prog='acf-check-llm') defines only --diff-file (lines 18-23), --mandates (lines 24-29), and --json (lines 30-34), and calls run_judge(diff_text, registry.mandates) at line 49 with no provider or model arguments, matching run_judge's current signature at plugins/arch-compliance/python/acf/judge.py:95-99 and entry point at pyproject.toml:20.

#### C7 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:133, README.md:38-45, docs/guides/SUPERPOWERS_COMPLEMENT.md:46-53`
- reasoning: Opened docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:133 which reads '- Provider interface; **Gemini default**; API key via environment.', and opened README.md:38-45 and docs/guides/SUPERPOWERS_COMPLEMENT.md:46-53 which both list only GEMINI_API_KEY and GOOGLE_API_KEY in their environment variable tables.

#### C8 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:56, plugins/arch-compliance/hooks/inject_constraints.py:1-30, plugins/arch-compliance/hooks/posttooluse_gate.py:1-30`
- reasoning: Ran git grep -n -i -E 'GEMINI_API_KEY|GOOGLE_API_KEY|ANTHROPIC_API_KEY|GeminiProvider|AnthropicProvider|gemini-2\.0-flash' -- plugins/arch-compliance/skills plugins/arch-compliance/hooks, which exited with code 1 and 0 matches, and inspected plugins/arch-compliance/skills/acf-mandate/SKILL.md:56 confirming it states 'judge must be configured at runtime or gates hard-fail' without naming a specific provider or API key variable.

#### C9 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:51, plugins/arch-compliance/python/acf/judge.py:107, plugins/arch-compliance/tests/test_judge.py:10-16`
- reasoning: Ran git grep -n 'resolve_api_key' -- plugins/ tests/ scripts/ and confirmed the only two occurrences are its definition at plugins/arch-compliance/python/acf/judge.py:51 and its call at plugins/arch-compliance/python/acf/judge.py:107; opened plugins/arch-compliance/tests/test_judge.py:10-16 confirming resolve_api_key is not imported in the test suite.

#### C10 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:51-115, plugins/arch-compliance/python/acf/cli_check_llm.py:11, plugins/arch-compliance/python/acf/cli_check_llm.py:49, plugins/arch-compliance/tests/test_judge.py:10-16`
- reasoning: Grepped the entire repository for resolve_api_key, GeminiProvider, and run_judge. Confirmed resolve_api_key() and GeminiProvider are only referenced inside plugins/arch-compliance/python/acf/judge.py:51-115, while plugins/arch-compliance/python/acf/cli_check_llm.py:11,49 and plugins/arch-compliance/tests/test_judge.py:10-16 import only run_judge, JudgeResult, LLM_PROMPT_IDS, _extract_text, and _parse_json_object, making the deletion and signature replacement safe.

### Unanchored findings

- **advisory**: Section 3 Non-Goals cites pyproject.toml:14 for the httpx>=0.27 dependency, but httpx>=0.27 is declared at pyproject.toml:9 while line 14 is a comment under optional-dependencies.
  - evidence: `pyproject.toml:9, docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:85`
- **advisory**: Section 6 (Live consumers row) cites plugins/arch-compliance/python/acf/cli_check_diff.py:16, 25 as consuming LLM_PROMPT_IDS, but LLM_PROMPT_IDS is imported on line 21 and used on line 25 (line 16 imports TS_DETECTOR_IDS).
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:21, docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:284`

### Looked for but did not find

- Any caller of resolve_api_key() or GeminiProvider outside plugins/arch-compliance/python/acf/judge.py across plugins/, tests/, and scripts/
- Any occurrence of GEMINI_API_KEY, GOOGLE_API_KEY, or GeminiProvider under plugins/arch-compliance/skills/ or plugins/arch-compliance/hooks/
- Any conflict between cli_check_llm.py argument additions and ALLOWED_DOC_LINES in plugins/arch-compliance/tests/test_repo_paths.py:37-39

## compliance

### Claim verdicts

#### C11 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:24-41, docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:108-142, docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:163-219, plugins/arch-compliance/python/acf/exceptions.py:17-22`
- reasoning: The doctrine at config/architecture/ARCHITECTURE.md:24-41 forbids bare/broad swallowing catches, silent degradation, and defaulting to None to avoid a crash. The design in docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:108-142 and :163-219 raises JudgeNotConfiguredError on missing API keys for enforced LLM mandates, empty/whitespace provider or model arguments, and unknown provider names, and raises JudgeResponseError on HTTP/JSON failures, empty/misshapen response blocks, regex-extracted invalid JSON, and Pydantic JudgeResult ValidationErrors.

#### C12 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:43-53, docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:115-122, plugins/arch-compliance/python/acf/judge.py:51-52`
- reasoning: The doctrine at config/architecture/ARCHITECTURE.md:43-53 forbids hasattr probing, temporary bridge code, compatibility shims, and masking logic. In docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:115-122, resolve_api_key(provider_name: ProviderName) replaces the zero-arg resolve_api_key() at plugins/arch-compliance/python/acf/judge.py:51-52 with a required parameter, no legacy wrapper, and zero cross-provider API-key fallback between anthropic and gemini.

#### C13 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:99-103, plugins/arch-compliance/python/acf/exceptions.py:17-22, plugins/arch-compliance/tests/test_adr_exceptions.py:35-45, docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:280`
- reasoning: The doctrine at config/architecture/ARCHITECTURE.md:99-103 requires every ACF exception to subclass AcfError alone without stdlib mixins (enforced by plugins/arch-compliance/tests/test_adr_exceptions.py:35-45). The design adds no new exception classes and raises only JudgeNotConfiguredError and JudgeResponseError defined in plugins/arch-compliance/python/acf/exceptions.py:17-22, both of which subclass AcfError alone.

#### C14 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:105-116, plugins/arch-compliance/python/acf/cli_check_llm.py:28-41, plugins/arch-compliance/tests/test_repo_paths.py:37-39, docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:241-244`
- reasoning: The doctrine at config/architecture/ARCHITECTURE.md:105-116 designates acf.repo as the sole declaration of host paths. In plugins/arch-compliance/python/acf/cli_check_llm.py:37-41, MANDATES_REL continues to be resolved via acf.repo, and docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:241-244 preserves the exact --mandates help string at cli_check_llm.py:28 allowlisted in plugins/arch-compliance/tests/test_repo_paths.py:37-39.

#### C15 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:118-128, config/architecture/adr.yml:1-2, docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:248-254, plugins/arch-compliance/python/acf/repo.py:23-44`
- reasoning: The doctrine at config/architecture/ARCHITECTURE.md:118-128 forbids defaults for config/architecture/adr.yml host declarations while explicitly recording package defaults outside that rule (currently the two in plugins/arch-compliance/python/acf/repo.py:23-44). The design leaves config/architecture/adr.yml:1-2 untouched and updates config/architecture/ARCHITECTURE.md:118-128 (per docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:248-254) to explicitly record the Tier-2 judge's provider and model defaults alongside the existing two recorded defaults while never defaulting or cross-provider-fallback-resolving API keys.

#### C16 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:146-150, docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:99-159, docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:222-239, plugins/arch-compliance/python/acf/cli_check_diff.py:21-25`
- reasoning: The doctrine at config/architecture/ARCHITECTURE.md:146-150 requires every export to have a live call site in the package, a hook, or a skill (not only tests). In the design (docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:99-159, :222-239, :284), cli_check_llm.py consumes PROVIDER_NAMES and run_judge; cli_check_diff.py:21-25 consumes LLM_PROMPT_IDS; and run_judge -> resolve_provider -> _resolve_provider_name / _resolve_model / resolve_api_key consumes DEFAULT_PROVIDER, DEFAULT_ANTHROPIC_MODEL, DEFAULT_GEMINI_MODEL, AnthropicProvider, and GeminiProvider at runtime.

#### C17 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:188-200, docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:172-219, plugins/arch-compliance/python/acf/judge.py:146-179`
- reasoning: The doctrine at config/architecture/ARCHITECTURE.md:188-200 requires a single canonical implementation when the same operation or decision procedure is needed by more than one caller. In docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:172-219, both AnthropicProvider.review and GeminiProvider.review delegate prompt rendering to _build_prompt (plugins/arch-compliance/python/acf/judge.py:146-157) and response-text-to-JudgeResult parsing and validation to _result_from_text (which delegates JSON extraction to _parse_json_object).

### Unanchored findings


### Looked for but did not find

- config/architecture/ARCHITECTURE.md:152-162 (## No completeness claims, high-frequency miss 1): checked universal quantifiers in docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:89-91, :121-122, :284, :315-351 — every tree census claim (no skill naming provider/key strings, resolve_api_key call sites, _extract_text/_parse_json_object call sites) is backed by a re-runnable git grep recipe in §A.1-A.3
- config/architecture/ARCHITECTURE.md:118-128 (## Declared, never defaulted, high-frequency miss 2): checked whether any default re-enters for a declared host value — config/architecture/adr.yml is untouched and package defaults in judge.py are explicitly recorded in ARCHITECTURE.md §4.5 item 1
- config/architecture/ARCHITECTURE.md:130-136 (## Prose names no host, high-frequency miss 3): checked runtime error messages in docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:109-219 and CLI help strings in :225-228 — none name any host repository, path, or section ( explicitly addressed in §6 line 283)
- config/architecture/ARCHITECTURE.md:99-103 (## One base exception, high-frequency miss 4): checked exception classes used — no new exceptions or stdlib mixins are introduced
- config/architecture/ARCHITECTURE.md:164-175 (## Declared text decoding, high-frequency miss 5): checked file reads and subprocess calls — no subprocess calls are added, and _PROMPT_TEMPLATE.read_text(encoding='utf-8') in judge.py:148 and args.diff_file.read_text(encoding='utf-8') in cli_check_llm.py:45 declare encoding='utf-8' (§6 line 285)
- config/architecture/ARCHITECTURE.md:188-200 & :218-220 (## Single point of definition, high-frequency miss 6): checked whether tests or skills re-implement package helpers — cli_check_llm.py imports PROVIDER_NAMES from acf.judge rather than re-spelling provider literals
- config/architecture/ARCHITECTURE.md:55-64 (## POSIX paths): checked path serialization in docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md — no str(path) into YAML/JSON dump/serialization payloads (§6 line 279)
- config/architecture/ARCHITECTURE.md:66-98 (## Build artifacts, ## Fail-loud ratchet, ## Façade sinks, ## FSM transitions, ## Soft fail-loud smells, ## React boundaries): checked against change surface — not touched by this design
- config/architecture/ARCHITECTURE.md:138-144 (## Frozen ledger format): checked against change surface — ledger models in acf.adr.ledger are not touched by this design
- config/architecture/ARCHITECTURE.md:177-186 (## Release discipline): checked skill prose under plugins/arch-compliance/skills/ — §3 Non-Goals line 89-91 and §A.1 verify no skill prose changes, so no plugin version bump is triggered
- config/architecture/ARCHITECTURE.md:203-207 (## Scoped refactor): checked scope in §3 and §4 — legacy zero-arg resolve_api_key() and unguarded JSON/Pydantic parsing in the changed judge.py code path are removed without expanding scope to unrelated modules; unstated_mandates is returned empty because the spec accounts for all governing doctrine sections

## sweeper

### Claim verdicts

#### C18 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:47-48, plugins/arch-compliance/python/acf/judge.py:55-93, plugins/arch-compliance/python/acf/judge.py:118-123, plugins/arch-compliance/python/acf/judge.py:146-157, plugins/arch-compliance/python/acf/judge.py:168-179, config/architecture/ARCHITECTURE.md:188-192`
- reasoning: Verified in plugins/arch-compliance/python/acf/judge.py:47-48 that JudgeProvider defines review(self, *, diff_text: str, mandate: Mandate) -> JudgeResult | None, consumed by run_judge at plugins/arch-compliance/python/acf/judge.py:98,119. GeminiProvider.review (plugins/arch-compliance/python/acf/judge.py:62-92) currently calls _build_prompt (line 63, defined at lines 146-157) and _parse_json_object (line 82, defined at lines 168-179) before constructing JudgeResult inline at lines 83-92. Extracting lines 82-92 into _result_from_text and having both AnthropicProvider.review and GeminiProvider.review delegate to _build_prompt and _result_from_text (which calls _parse_json_object) keeps a single owner for prompt rendering, JSON object extraction, and JudgeResult materialization in compliance with config/architecture/ARCHITECTURE.md:188-192.

#### C19 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:133, README.md:38-45, docs/guides/SUPERPOWERS_COMPLEMENT.md:46-53, config/architecture/ARCHITECTURE.md:118-128, docs/design/ADR_GATE_HOST_CONTRACT.md:221, docs/design/ADR_GATE_HOST_CONTRACT.md:512, docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:199, docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:632, plugins/arch-compliance/skills/acf-mandate/SKILL.md:56`
- reasoning: Swept all tracked markdown, skill, profile, hook, and config files (excluding docs/reviews) for Tier-2 LLM judge provider, model, and environment variable references (GEMINI_API_KEY, GOOGLE_API_KEY, ANTHROPIC_API_KEY, Gemini, Anthropic, claude, gemini-2.0-flash, Tier 2, detection: llm, defaults). Confirmed that docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:133, README.md:38-45, docs/guides/SUPERPOWERS_COMPLEMENT.md:46-53, and config/architecture/ARCHITECTURE.md:118-128 are the only non-historical prose documents stating the Tier-2 judge's default provider, model, or environment variables (skills such as plugins/arch-compliance/skills/acf-mandate/SKILL.md:56,121 and profile docs plugins/arch-compliance/profiles/python-service/ARCHITECTURE.md:41-44 and plugins/arch-compliance/profiles/react-app/ARCHITECTURE.md:20-24 are already provider-neutral), and verified that docs/design/ADR_GATE_HOST_CONTRACT.md:221,512 and docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:199,632 are historical grep census records.

### Unanchored findings


### Looked for but did not find

- Other HTTP or LLM client wrappers in the repository (searched httpx, urllib, requests, Anthropic, Gemini, generateContent, messages across plugins/arch-compliance/python, plugins/arch-compliance/hooks, scripts, tests)
- Other environment variable readers or API key resolvers (searched os.environ, getenv, API_KEY, resolve_api_key, ACF_JUDGE across plugins/arch-compliance/python, plugins/arch-compliance/hooks, scripts)
- Other callers of run_judge, resolve_api_key, GeminiProvider, _extract_text, or _parse_json_object outside judge.py, cli_check_llm.py, and test_judge.py (searched across plugins/, tests/, scripts/)
- Unlisted non-historical prose or skill files naming Gemini as the Tier-2 judge default or listing GEMINI_API_KEY/GOOGLE_API_KEY (inspected CLAUDE.md, SECURITY.md, plugins/arch-compliance/skills/*/SKILL.md, plugins/arch-compliance/skills/architecture-review/auditors/*.md, plugins/arch-compliance/profiles/*/*, plugins/arch-compliance/hooks/constraints_template.md)

### Relationships

- ADJACENT: `AnthropicProvider (plugins/arch-compliance/python/acf/judge.py)` — responsibility `Implement JudgeProvider.review over an HTTP LLM endpoint and unpack provider-specific response envelopes into text` — existing `plugins/arch-compliance/python/acf/judge.py:55`
  - resolution: none
  - non-merge: AnthropicProvider and GeminiProvider implement the same JudgeProvider protocol for two distinct wire protocols (Anthropic POST /v1/messages with x-api-key and anthropic-version headers and content[i].text blocks vs Gemini POST :generateContent with key query param, generationConfig.responseMimeType, and candidates[0].content.parts[i].text), while delegating shared prompt construction to _build_prompt and JSON-to-JudgeResult materialization to _result_from_text.
- SUBSUMED: `resolve_provider, _resolve_provider_name, _resolve_model, and resolve_api_key(provider_name) (plugins/arch-compliance/python/acf/judge.py)` — responsibility `Resolve the active Tier-2 judge provider, model, and API key from explicit arguments or environment variables and fail loud on missing credentials for enforced LLM mandates` — existing `plugins/arch-compliance/python/acf/judge.py:51`
  - resolution: Replace the zero-argument Gemini-only resolve_api_key() at plugins/arch-compliance/python/acf/judge.py:51-52 and the inline GeminiProvider wiring in run_judge at plugins/arch-compliance/python/acf/judge.py:106-115 with parameterized resolve_api_key(provider_name) and resolve_provider.
- ADJACENT: `_result_from_text and hardened _parse_json_object (plugins/arch-compliance/python/acf/judge.py)` — responsibility `Extract a JSON object from LLM output text and validate it against a Pydantic schema, translating parse and validation errors into an AcfError subclass` — existing `plugins/arch-compliance/python/acf/adr/parser.py:43`
  - resolution: none
  - non-merge: parse_reviewer_payload in acf.adr.parser enforces ADR Architectural Contract 5 (requiring a single ```json fenced block, verifying reviewer identity, validating a ReviewerPayload discriminated union, and formatting a schema key diff into ReviewerContractViolationError), whereas _parse_json_object and _result_from_text parse unfenced or brace-extracted JSON from a Tier-2 judge response, short-circuit to None when violation is false, apply mandate severity and low confidence defaults, and raise JudgeResponseError.
- ADJACENT: `_result_from_text (plugins/arch-compliance/python/acf/judge.py)` — responsibility `Validate parsed data against a Pydantic BaseModel and translate ValidationError into a domain AcfError` — existing `plugins/arch-compliance/python/acf/loader.py:43`
  - resolution: none
  - non-merge: load_model_file in acf.loader reads on-disk YAML/JSON configuration or baseline files by Path and raises AcfInputError naming the file subject and path, whereas _result_from_text validates an in-memory LLM response dictionary after checking the violation flag and raises JudgeResponseError, which must remain distinct from input/configuration errors.
- DISJOINT: `--provider and --model CLI flags on acf-check-llm (plugins/arch-compliance/python/acf/cli_check_llm.py)` — responsibility `Parse CLI arguments for architecture compliance commands` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:28`
  - resolution: none

### Two-owner counts

- JudgeProvider HTTP transport and response envelope text extraction (AnthropicProvider vs GeminiProvider in plugins/arch-compliance/python/acf/judge.py): 2
- LLM/reviewer text-to-JSON extraction and Pydantic validation (_result_from_text/_parse_json_object in plugins/arch-compliance/python/acf/judge.py vs parse_reviewer_payload in plugins/arch-compliance/python/acf/adr/parser.py:43): 2
- Pydantic model validation wrapping ValidationError into an AcfError subclass (load_model_file in plugins/arch-compliance/python/acf/loader.py:43, parse_reviewer_payload in plugins/arch-compliance/python/acf/adr/parser.py:79, _result_from_text in plugins/arch-compliance/python/acf/judge.py): 3

### Document conflicts


## hardening

### Claim verdicts

#### C20 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:51-52, plugins/arch-compliance/python/acf/judge.py:95-123, plugins/arch-compliance/python/acf/exceptions.py:17-18, plugins/arch-compliance/python/acf/cli_check_llm.py:49, docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:108-160`
- reasoning: Inspected plugins/arch-compliance/python/acf/judge.py:51-52 and 95-123: today resolve_api_key() reads GEMINI_API_KEY or GOOGLE_API_KEY without stripping whitespace or accepting a provider argument, and run_judge instantiates GeminiProvider directly at line 115. In docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:108-160, resolve_provider resolves _resolve_provider_name and _resolve_model before calling resolve_api_key(resolved_name), strips whitespace from explicit args and env vars (ACF_JUDGE_PROVIDER, ACF_JUDGE_MODEL, ANTHROPIC_API_KEY, GEMINI_API_KEY, GOOGLE_API_KEY), and raises JudgeNotConfiguredError (plugins/arch-compliance/python/acf/exceptions.py:17-18) with zero cross-provider fallback.

#### C21 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:38-45, plugins/arch-compliance/python/acf/judge.py:55-93, plugins/arch-compliance/python/acf/judge.py:160-179, plugins/arch-compliance/python/acf/exceptions.py:17-22, docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:163-219`
- reasoning: Inspected plugins/arch-compliance/python/acf/judge.py:55-93 and 160-179: GeminiProvider.__init__ (lines 58-60) does not validate empty/whitespace api_key or model, GeminiProvider.review (lines 72-80) does not catch httpx.HTTPError or ValueError, _parse_json_object (line 176) calls json.loads(match.group(0)) outside a try block, and JudgeResult construction (lines 85-92) does not catch pydantic.ValidationError. Section 4.2 and Section 4.3 (docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:163-219) harden all four failure points to raise JudgeNotConfiguredError or JudgeResponseError (plugins/arch-compliance/python/acf/exceptions.py:17-22), though Section 4.3 lines 216-217 introduce a null-coalescing repair on severity/confidence that conflicts with Section 8 line 307 (flagged separately).

#### C22 — SURVIVED
- evidence: `pyproject.toml:6-10, pyproject.toml:14, plugins/arch-compliance/python/acf/judge.py:11-12, docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:83-85`
- reasoning: Opened pyproject.toml:6-10 and plugins/arch-compliance/python/acf/judge.py:11-12: pyproject.toml declares 'pydantic>=2.0' at line 7 and 'httpx>=0.27' at line 9 under [project].dependencies, and judge.py:11-12 already imports httpx and pydantic, confirming that AnthropicProvider and _result_from_text require no new runtime dependencies. Note that docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:84 cites pyproject.toml:14 (which is a comment line under [project.optional-dependencies]) instead of pyproject.toml:9, and pyproject.toml:7 specifies pydantic>=2.0 rather than pydantic>=2.6.

#### C23 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_llm.py:16-50, pyproject.toml:18-20, plugins/arch-compliance/tests/test_repo_paths.py:37-39, plugins/arch-compliance/tests/test_repo_paths.py:53-71`
- reasoning: Grepped all callers of run_judge across the repository and opened pyproject.toml:18-20, plugins/arch-compliance/python/acf/cli_check_llm.py:16-50, and plugins/arch-compliance/tests/test_repo_paths.py:37-71. cli_check_llm.py:49 is the sole non-test caller of run_judge, wired to acf-check-llm in pyproject.toml:20. test_host_config_dir_has_one_code_owner in test_repo_paths.py:53-71 checks lines matching CONFIG_ARCH_RE against ALLOWED_DOC_LINES['python/acf/cli_check_llm.py'] (lines 37-39), which matches cli_check_llm.py:28 verbatim and is unaffected by adding --provider and --model flags.

### Unanchored findings

- **important**: Section 4.3 (_result_from_text) coalesces null severity and confidence to defaults ('if data.get("severity") is not None else mandate.severity'), silently repairing explicit JSON nulls and contradicting Section 2 (line 44) and Section 8 (line 307), which require _result_from_text(severity=None) to raise JudgeResponseError.
  - evidence: `docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:43-45, docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:216-218, docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:307, plugins/arch-compliance/python/acf/judge.py:87-88`
- **advisory**: Section 3 Non-Goals cites pyproject.toml:14 for httpx>=0.27, but pyproject.toml:14 is a comment in [project.optional-dependencies]; runtime dependencies (pydantic>=2.0 and httpx>=0.27) are declared at pyproject.toml:6-10.
  - evidence: `docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:84, pyproject.toml:6-10, pyproject.toml:14`

### Looked for but did not find

- Searched all callers of run_judge and resolve_api_key across plugins/, tests/, and scripts/ for any secondary CLI or hook entrypoint that bypasses resolve_provider or cli_check_llm.py:49; none found.
- Traced resolve_provider and resolve_api_key in docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:108-142 for any cross-provider API key fallback between ANTHROPIC_API_KEY and GEMINI_API_KEY/GOOGLE_API_KEY; none found.
- Traced AnthropicProvider and GeminiProvider HTTP transport and text extraction in docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:163-200 for silent error suppression or empty-text pass-through; all transport and shape failures raise JudgeResponseError.

### Mechanism traces

- **resolve_provider and resolve_api_key (_resolve_provider_name, _resolve_model, resolve_api_key, resolve_provider)**
  - invalid state: provider_name is empty/whitespace or not in ('anthropic', 'gemini'), model is empty/whitespace, or the active provider's environment variable (ANTHROPIC_API_KEY or GEMINI_API_KEY/GOOGLE_API_KEY) is unset or whitespace-only when an enforced detection=='llm' mandate is evaluated
  - producer: `plugins/arch-compliance/python/acf/cli_check_llm.py:49`
  - rung 2 (highest applicable 2); repairs=False
  - hardening rejected because: CLI --provider is constrained at rung 1 via argparse choices=PROVIDER_NAMES in cli_check_llm.py, while environment variables (os.environ in judge.py:51-52) and direct Python callers of run_judge (judge.py:95-115) cross an external process/caller boundary that must be validated in one place (resolve_provider) and fail loud with JudgeNotConfiguredError.
  - spec citation: `docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:108-142`
- **AnthropicProvider and GeminiProvider constructor and HTTP/response-shape guards (__init__, review, _extract_anthropic_text, _extract_text)**
  - invalid state: Provider instance constructed with empty/whitespace api_key or model, HTTP call raises httpx.HTTPError or returns non-JSON (ValueError), or provider JSON body lacks non-empty text content blocks
  - producer: `plugins/arch-compliance/python/acf/judge.py:58-81`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: Direct callers can pass arbitrary strings to provider constructors and HTTP responses arrive from external LLM endpoints (api.anthropic.com and generativelanguage.googleapis.com) whose status and payload structure cannot be statically guaranteed before the network call.
  - spec citation: `docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:163-200`
- **_parse_json_object regex-brace JSONDecodeError guard and _result_from_text ValidationError guard**
  - invalid state: LLM text response contains matched '{...}' braces with invalid JSON syntax or JSON fields that violate JudgeResult's Pydantic schema (Literal['BLOCK', 'WARN'] for severity, Literal['high', 'medium', 'low'] for confidence, int|None for line)
  - producer: `plugins/arch-compliance/python/acf/judge.py:82-92`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: LLM text responses are untrusted external boundary inputs produced by remote models over HTTP; consolidating JSON-to-JudgeResult construction into _result_from_text establishes a single owner (rung 2) that fails loud with JudgeResponseError (rung 3).
  - spec citation: `docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:207-218`
- **_result_from_text null-coalescing on severity and confidence ('if data.get("severity") is not None else mandate.severity' and 'if data.get("confidence") is not None else "low"')**
  - invalid state: Parsed LLM JSON dict contains explicit null for non-nullable fields: data['severity'] is None or data['confidence'] is None when data.get('violation') is truthy
  - producer: `plugins/arch-compliance/python/acf/judge.py:87-88`
  - rung 5 (highest applicable 3); repairs=True
  - spec citation: `docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:216-217`

## Claims

- **C1** [premise] [load-bearing]: JudgeProvider in plugins/arch-compliance/python/acf/judge.py:47-48 defines a single method review(self, *, diff_text: str, mandate: Mandate) -> JudgeResult | None, JudgeResult is defined at lines 38-45, _to_finding at lines 126-143, and _build_prompt at lines 146-157.
  - spec citation: `plugins/arch-compliance/python/acf/judge.py:38-157`
- **C2** [root_cause] [load-bearing]: resolve_api_key() in plugins/arch-compliance/python/acf/judge.py:51-52 takes no provider parameter and reads only GEMINI_API_KEY or GOOGLE_API_KEY, and run_judge at lines 106-115 calls resolve_api_key() and instantiates GeminiProvider(api_key=api_key) when provider is None.
  - spec citation: `plugins/arch-compliance/python/acf/judge.py:51-115`
- **C3** [root_cause] [load-bearing]: GeminiProvider.review in plugins/arch-compliance/python/acf/judge.py:72-80 calls client.post, response.raise_for_status(), and response.json() without translating httpx.HTTPError or ValueError into JudgeResponseError.
  - spec citation: `plugins/arch-compliance/python/acf/judge.py:72-80`
- **C4** [root_cause] [load-bearing]: _parse_json_object in plugins/arch-compliance/python/acf/judge.py:168-179 catches json.JSONDecodeError on json.loads(text) at lines 170-172 and matches {...} via re.search at line 173, but calls json.loads(match.group(0)) at line 176 outside a try block so malformed JSON inside matched braces raises raw json.JSONDecodeError instead of JudgeResponseError.
  - spec citation: `plugins/arch-compliance/python/acf/judge.py:168-179`
- **C5** [root_cause] [load-bearing]: GeminiProvider.review in plugins/arch-compliance/python/acf/judge.py:85-92 constructs JudgeResult directly from data.get(...) without catching pydantic.ValidationError or guarding against explicit null values for severity/confidence when the key is present in data.
  - spec citation: `plugins/arch-compliance/python/acf/judge.py:85-92`
- **C6** [premise] [load-bearing]: main in plugins/arch-compliance/python/acf/cli_check_llm.py:16-50 defines only --diff-file, --mandates, and --json and calls run_judge(diff_text, registry.mandates) at line 49 with no provider or model arguments.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_llm.py:16-50`
- **C7** [premise]: docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:133 states 'Provider interface; **Gemini default**; API key via environment.', and README.md:38-45 and docs/guides/SUPERPOWERS_COMPLEMENT.md:46-53 list only GEMINI_API_KEY and GOOGLE_API_KEY.
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:133`
- **C8** [premise] [load-bearing]: No file under plugins/arch-compliance/skills or plugins/arch-compliance/hooks matches GEMINI_API_KEY, GOOGLE_API_KEY, ANTHROPIC_API_KEY, GeminiProvider, AnthropicProvider, or gemini-2.0-flash (verified by executing the git grep recipe in §A.1).
  - spec citation: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:56`
- **C9** [premise] [load-bearing]: resolve_api_key has only two occurrences across plugins/, tests/, and scripts/ at 80b80f1: its definition at plugins/arch-compliance/python/acf/judge.py:51 and its call at plugins/arch-compliance/python/acf/judge.py:107 (verified by §A.2).
  - spec citation: `plugins/arch-compliance/python/acf/judge.py:51-107`
- **C10** [deletion] [load-bearing]: The design removes the parameterless resolve_api_key() signature (replacing it with resolve_api_key(provider_name: ProviderName)), removes inline Gemini-only resolution in run_judge (lines 106-115), and removes inline JudgeResult construction from GeminiProvider.review (lines 82-92, replaced by _result_from_text).
  - spec citation: `plugins/arch-compliance/python/acf/judge.py:51-115`
- **C11** [mandate]: The design complies with ## Fail loud (config/architecture/ARCHITECTURE.md:24-41, fail-loud.bare-except): missing API keys for enforced LLM mandates, empty/whitespace provider or model arguments, and unknown provider names raise JudgeNotConfiguredError, and HTTP/JSON/Pydantic response failures raise JudgeResponseError.
  - spec citation: `config/architecture/ARCHITECTURE.md:24-41`
- **C12** [mandate]: The design complies with ## No shims (config/architecture/ARCHITECTURE.md:43-53, no-shims.hasattr): zero cross-provider API-key fallback exists between anthropic and gemini, and resolve_api_key(provider_name: ProviderName) requires its parameter with no legacy zero-argument wrapper.
  - spec citation: `config/architecture/ARCHITECTURE.md:43-53`
- **C13** [mandate]: The design complies with ## One base exception (config/architecture/ARCHITECTURE.md:99-103, plugin.one-base-exception): it adds no new exception classes and raises only JudgeNotConfiguredError and JudgeResponseError from plugins/arch-compliance/python/acf/exceptions.py:17-22, which subclass AcfError alone.
  - spec citation: `plugins/arch-compliance/python/acf/exceptions.py:17-22`
- **C14** [mandate]: The design complies with ## One owner for host paths (config/architecture/ARCHITECTURE.md:105-116, plugin.one-owner-host-paths): cli_check_llm.py:40 continues to resolve MANDATES_REL via acf.repo and preserves the exact --mandates help string allowlisted in plugins/arch-compliance/tests/test_repo_paths.py:37-39.
  - spec citation: `plugins/arch-compliance/tests/test_repo_paths.py:37-39`
- **C15** [mandate]: The design complies with ## Declared, never defaulted (config/architecture/ARCHITECTURE.md:118-128, plugin.declared-never-defaulted): config/architecture/adr.yml host declarations are untouched, and the Tier-2 judge's CLI/env provider and model defaults in plugins/arch-compliance/python/acf/judge.py are explicitly recorded in config/architecture/ARCHITECTURE.md ## Declared, never defaulted.
  - spec citation: `config/architecture/ARCHITECTURE.md:118-128`
- **C16** [mandate]: The design complies with ## Live consumers (config/architecture/ARCHITECTURE.md:146-150): every public symbol in acf.judge (PROVIDER_NAMES, DEFAULT_PROVIDER, DEFAULT_ANTHROPIC_MODEL, DEFAULT_GEMINI_MODEL, AnthropicProvider, GeminiProvider, resolve_api_key, resolve_provider, run_judge, LLM_PROMPT_IDS) is consumed in the runtime chain across cli_check_llm.py, cli_check_diff.py, and judge.py.
  - spec citation: `config/architecture/ARCHITECTURE.md:146-150`
- **C17** [mandate]: The design complies with ## Single point of definition (config/architecture/ARCHITECTURE.md:188-200): both AnthropicProvider.review and GeminiProvider.review delegate prompt rendering to _build_prompt and response-text-to-JudgeResult materialization to _result_from_text.
  - spec citation: `config/architecture/ARCHITECTURE.md:188-200`
- **C18** [shape_fit] [load-bearing]: AnthropicProvider and GeminiProvider both implement the existing JudgeProvider protocol (plugins/arch-compliance/python/acf/judge.py:47-48) and share _build_prompt, _result_from_text, and _parse_json_object so there is one owner for prompt rendering, JSON extraction, and JudgeResult construction.
  - spec citation: `plugins/arch-compliance/python/acf/judge.py:47-48`
- **C19** [sweep]: Updating docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:133, README.md:38-45, docs/guides/SUPERPOWERS_COMPLEMENT.md:46-53, and config/architecture/ARCHITECTURE.md:118-128 covers all non-historical prose documents in the repository that state the Tier-2 judge's default provider or environment variables, while docs/design/ADR_GATE_HOST_CONTRACT.md:221,512 and docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:199,632 are historical grep census tables.
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:133`
- **C20** [mechanism_justification] [load-bearing]: resolve_provider and resolve_api_key in plugins/arch-compliance/python/acf/judge.py validate provider_name and model before checking API keys, strip whitespace from environment variables, and refuse cross-provider fallback so misconfigured or whitespace-only environment variables fail loud with JudgeNotConfiguredError.
  - spec citation: `plugins/arch-compliance/python/acf/judge.py:95-123`
- **C21** [mechanism_justification] [load-bearing]: AnthropicProvider and GeminiProvider validate non-empty api_key and model in __init__, catch (httpx.HTTPError, ValueError) around HTTP/JSON transport, and delegate to _result_from_text which catches json.JSONDecodeError (including on regex-matched braces) and pydantic.ValidationError to raise JudgeResponseError.
  - spec citation: `plugins/arch-compliance/python/acf/judge.py:55-93`
- **C22** [implementability] [load-bearing]: pyproject.toml:14 already declares httpx>=0.27 and pydantic>=2.6 as runtime dependencies of the acf package, so AnthropicProvider and _result_from_text require no new package dependencies.
  - spec citation: `pyproject.toml:14`
- **C23** [implementability] [load-bearing]: plugins/arch-compliance/python/acf/cli_check_llm.py:16-50 is the sole CLI entrypoint for run_judge (pyproject.toml:20 acf-check-llm = 'acf.cli_check_llm:main'), and adding --provider and --model while keeping line 28's --mandates help string unchanged preserves plugins/arch-compliance/tests/test_repo_paths.py:37-39.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_llm.py:16-50`
