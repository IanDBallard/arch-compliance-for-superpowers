# Architecture Review Port: Generic Rules, Technology Packs and Repository Settings

**Status:** Draft (v2)
**Date:** 2026-11-12
**Spec kinds:** `feature`
**Repo:** `IanDBallard/arch-compliance-for-superpowers`, `main` at `50d727f` (branch `feat/architecture-review-port`).
**Roadmap:** workstream E phase 2, part one of two (`hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md`, section "Workstream E — Portable governance skills"). Part two, moving the origin repository's enforcement gate onto `acf-check-diff`, is a separate later spec (§10).
**Governing mandates:** `config/architecture/ARCHITECTURE.md` sections `## Fail loud` (`:26-44`), `## No shims` (`:45-56`), `## POSIX paths` (`:57-67`), `## React boundaries` (`:101-107`), `## One base exception` (`:108-113`), `## One owner for host paths` (`:114-141`), `## Declared, never defaulted` (`:187-203`), `## Prose names no host` (`:204-213`), `## Live consumers` (`:222-227`), `## No completeness claims` (`:228-239`), `## Declared text decoding` (`:240-252`), `## Release discipline` (`:253-264`), `## Single point of definition` (`:265-279`). For the origin stage (§5), the origin repository's spec-authoring rule quoted in §5.
**No state-machine surface.** This design adds or modifies no state machine and no transition.

---

## 0. Citation convention

Unprefixed paths are this repository at `50d727f`. `hm:` paths are the HistoricMansions checkout at `b2611977f`; every rule of that repository this spec relies on is quoted where it is used. `cy:` paths are the Cayenne checkout at `d0d749bc`, cited only for its file types and Svelte idiom; nothing in `cy:` changes. Paths are POSIX.

---

## 1. Intent

The plugin's `/architecture-review` is a generic rewrite with four auditors (`plugins/arch-compliance/skills/architecture-review/SKILL.md:72`). The origin repository's review is richer: nine auditors, a doctrine rubric step, per-auditor file surfaces, a deterministic UI pre-pass and a blame-based provenance section (`hm:.claude/skills/architecture-review/SKILL.md:31-158`). Its auditors hard-code the origin repository's paths, class names and section numbers, for example *"`ContentMetadataService` is the only allowed accessor for `index.yml` content"* (`hm:.claude/skills/architecture-review/auditors/metadata-facade.md:3`) and the stage file lists in `hm:.claude/skills/architecture-review/auditors/output-agnosticism.md:12-25`.

The goal is to keep the origin review's capabilities and move every repository dependency out of the plugin, so any repository supplies its own. The decisions of §2 split what the review knows into three layers that change for different reasons: the rule, the technology the rule is read in, and the repository's settings.

---

## 2. Decisions

| # | Decision | Made by |
|---|---|---|
| 1 | Port with capabilities kept; repository dependencies isolated so a repository supplies its own components. | user, 2026-11-12 |
| 2 | Rules are technology-independent. What a rule looks like in one technology is a separate, plugin-shipped **technology pack**, not a repository setting. | user, 2026-11-12 |
| 3 | A **hatch** lets a repository supply its own auditor prompt for a rule that does not generalise. | user, 2026-11-12 |
| 4 | Scope excludes performance and code-quality rules. Security is out of scope except where a rule states *where* enforcement must live; row-level security on client-reachable tables is in. | user, 2026-11-12 |
| 5 | The first release ships packs for the origin repository's stack and Cayenne's: Python, TypeScript/JavaScript, Svelte, React, HTML templates, SQL. | user, 2026-11-12 |
| 6 | Two specs: this one builds the framework and ports the review, with the origin cutover; the enforcement gate migrates later against it. | user, 2026-11-12 |
| 7 | Cursor support for the origin `architecture-review` is lost at cutover and a follow-up row is filed on the origin roadmap board (§5.5). | user, 2026-11-12 |
| 8 | Baseline staleness moves into the plugin's roll-up; the origin's pre-push staleness check is deleted (§4.7 step 7, §5.4). | user, 2026-11-12 |
| 9 | Every rule is opt-in through a mandate row; no rule runs by default. | author |
| 10 | A rule's settings are read from the row's `params`, one flat namespace shared with the row's detector, so a fact both need is declared once; a rule's settings keys reuse the key names of the built-in detector that checks the same subject (§4.2). | author |
| 11 | The pack format reserves a `detectors` slot whose shape this spec fixes and part two adds; this spec ships `hints` only (`## Live consumers`). | author |
| 12 | The origin repository's drift baseline is reset at cutover, not migrated (§5.6). | author |
| 13 | The plugin's `react-boundaries` auditor is absorbed into the generic `ui-logic-isolation` rule. | author |
| 14 | A repository-supplied auditor prompt needs no `acf-allow` approval: it is text read by read-only agents, as the audited code is. This spec adds no repository-supplied executable code. | author |
| 15 | The origin review's JSON sidecar is not ported: its only reader is the origin golden-summary helper, which the cutover deletes (§5.4, recipe A, which matches `_last_run`). | author |
| 16 | The doctrine document set is not declared by the review; it is `ARCH_REL` plus the documents `ARCH_REL` names, as the ADR host contract already defines it (§4.6). | author |

---

## 3. Non-goals

- Moving any AST detector or script guard, or the origin repository's LLM judge, onto the plugin (part two, §10).
- Script-block extraction for `.svelte` files: the review auditors read `.svelte` text and pack hints are regular expressions over it; deterministic Svelte detectors belong to part two.
- Unifying the gate's file-suffix routing (`plugins/arch-compliance/python/acf/cli_check_diff.py:152`, `:188`) with pack `files` globs: part two, when packs gain detectors (§10).
- New rules beyond the twelve in §4.2. Deferred candidates: single point of definition; contract fidelity of schema migrations.
- Changing the gate's Tier-2 judge (`plugins/arch-compliance/python/acf/judge.py`): its prompts come from `judge_prompt.md` (`judge.py:19`) and it reads no auditor file.

---

## 4. Design

### 4.1 Layers

| Layer | Example (single owner) | Lives in | Trust |
|---|---|---|---|
| Rule: principle, what to flag, severity rubric | "a declared artifact is read and written only through its declared owner" | `plugins/arch-compliance/skills/architecture-review/rules/<rule>.md` plus its settings model in `acf.review.rules` | plugin |
| Technology pack: the shapes a rule takes in one technology | Python: `open(`, `yaml.safe_load`; TypeScript: `fs.read`, `supabase.from(` | `plugins/arch-compliance/python/acf/review/packs/<pack>.yml` | plugin |
| Repository settings | `target_literal_re: 'index\.ya?ml'`, `allowlist_globs: [<owner module>]` | the mandate row's `params` | data |
| Hatch | a rule with no generic form | a repository Markdown prompt named by the row's `auditor` | data (decision 14) |

### 4.2 Rule library

Each rule has a prompt file and a settings model registered in `acf.review.rules.RULES: dict[str, type[RuleSettings]]`. A settings model reads the keys it declares from the row's `params` and validates their types; keys it does not declare belong to the row's detector or to nobody, and the report lists, per reviewed row, every `params` key the rule did not read, so an unread key is visible rather than silently ignored. `RuleSettings` declares the keys every rule reads: `surface: list[str] | None` (globs; absent means the target tree of §4.7 step 2), `surface_exclude: list[str]` and `docs: list[str]` (repository documents the auditor reads in full).

| Rule id | Principle | Settings keys beyond `RuleSettings` | Source |
|---|---|---|---|
| `fail-loud` | Errors halt and report; no broad catch, silent success default or interface probing | `exception_base: {class_name, module}` | `hm:…/auditors/fail-loud.md`; plugin `auditors/fail-loud.md` |
| `no-shims` | No compatibility branches, soft fallbacks, internal retries or migration shims | `exempt_paths` | `hm:…/auditors/no-shims.md`; plugin `auditors/no-shims.md` |
| `posix-paths` | Persisted paths are POSIX strings of a declared path type | `path_types` | plugin `auditors/posix-paths.md` |
| `class-cohesion` | A class holds one responsibility; judged by cohesion, not size | `facades` (exempt from width) | `hm:…/auditors/class-cohesion.md` |
| `ui-logic-isolation` | The UI renders and dispatches; it does not decide domain rules or mirror backend state | none | `hm:…/auditors/ui-logic-isolation.md`; plugin `auditors/react-boundaries.md` |
| `single-owner` | A declared persisted artifact is read and written only through its declared owner; an inventory tracks known exceptions | `target_literal_re`, `allowlist_globs` (the keys of the `facade.forbid-sink` detector, `config/architecture/ARCHITECTURE.md:80-86`), `inventory` | `hm:…/auditors/metadata-facade.md` |
| `pipeline-isolation` | Shared stages never branch on the output variant; variant stages consume only the canonical intermediate artifact | `shared_stages`, `variant_stages`, `exempt`, `variant_terms`, `raw_sources`, `canonical_artifact` | `hm:…/auditors/output-agnosticism.md` |
| `presentation-as-data` | Appearance values live in a declared style schema; every element × variant pair is declared; one live schema version | `bindings`, `style_schema`, `element_key`, `variant_key` | `hm:…/auditors/schema-presentation.md` |
| `layer-boundaries` | Code in one tier reaches another tier's resources only through a declared boundary | `tiers: [{name, paths}]`, `crossings: [{from_tier, to_tier, root_names, via}]` | `hm:…/auditors/three-tier-hfsm.md` rules 1, 2, 5 |
| `state-machine-discipline` | State changes only through the declared transition path; transitions raise their declared failure types | `state_field`, `validator_name` (the keys of the `fsm.transition-guard` detector, `config/architecture/ARCHITECTURE.md:88-94`), `base_classes` | `hm:…/auditors/three-tier-hfsm.md` rules 3, 4 |
| `path-provenance` | An externally sourced path is classified by the declared cross-platform helper, never by the host platform's absolute-path test | `classifier` | `hm:…/auditors/three-tier-hfsm.md` rule 6 |
| `data-access-boundary` | Access control is enforced at the data layer, not trusted to the client | `client_paths`, `policy_files`, `privileged_credentials`, `replication_rules` | new (decision 4) |

For `data-access-boundary`, a table is client-reachable when code under `client_paths` names it or a file in `replication_rules` selects it. The rule flags a client-reachable table whose `policy_files` never enable row-level security on it; a `privileged_credentials` name appearing under `client_paths`; and a query in `replication_rules` that selects a client-reachable table's rows without filtering by the authenticated user.

A rule prompt names no repository (`## Prose names no host`): every repository value reaches the auditor as a row's settings. One output contract, `plugins/arch-compliance/skills/architecture-review/rules/_contract.md`, is given to every auditor with its rule prompt.

### 4.3 Technology packs

A pack file is loaded by `acf.review.packs.TechPack` (`extra="forbid"`):

```yaml
id: ts-js
language: typescript   # a Mandate Language value: python, typescript or none
extends: null          # or the id of the base pack an add-on builds on
files: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx", "**/*.mjs", "**/*.cjs"]
hints:
  ui-logic-isolation:
    - pattern: '\.(filter|reduce)\('
      tell: client-side aggregation
```

`language` ties a pack to the vocabulary rows already use (`plugins/arch-compliance/python/acf/registry.py:16`). A row receives hints from the declared packs whose `language` matches the row's `languages` (`both` matches `python` and `typescript`) and from declared packs whose `language` is `none` (markup and data: `html-templates`, `sql`). A pack's hints scan only files matching its own `files` globs within the row's surface; `extends` adds one thing, that the base pack's hints also scan the add-on's files. An add-on declared without its base is refused. `hints` keys must be rule ids in `RULES` and each `pattern` must compile. Pack ids differ from language ids where the file extent differs: the review's `ts-js` covers JavaScript, the gate's `typescript` routing covers `.ts`/`.tsx` (§3).

Reserved for part two: `detectors: {<rule id>: [<built-in detector id>]}`, each a key of `KNOWN_DETECTORS`. This spec's model refuses the key.

| Pack | `language` | Extends | Rules with hints | Hint source |
|---|---|---|---|---|
| `python` | python | — | fail-loud, no-shims, posix-paths, single-owner, pipeline-isolation, layer-boundaries, state-machine-discipline, path-provenance | the origin auditors' "Detection patterns", with repository values replaced by settings references |
| `ts-js` | typescript | — | fail-loud, no-shims, ui-logic-isolation, single-owner, data-access-boundary | the origin pre-pass tells (`hm:scripts/core/architecture_review/ui_logic_prepass.py:31-52`); `supabase.from(`; `createClient(` with a key named in `privileged_credentials` |
| `react` | typescript | `ts-js` | ui-logic-isolation | plugin `auditors/react-boundaries.md` "Check" |
| `svelte` | typescript | `ts-js` | ui-logic-isolation | Svelte 5 runes computing domain values: `$derived(`, `$state(`, `$effect(` (`cy:cayenne-web/src/lib/features/bugReport/BugReportSheetBody.svelte:41`) |
| `html-templates` | none | — | ui-logic-isolation, presentation-as-data | written for this rule: inline event handlers and template conditionals that decide domain state; inline style values |
| `sql` | none | — | data-access-boundary, single-owner, no-shims | `create table` without `enable row level security`; views named as legacy or compatibility views |

### 4.4 Repository declaration

A repository declares the review's host values in `config/architecture/review.yml`, located by a new `acf.repo.REVIEW_REL` and loaded by `acf.review.host.load_review_config` into `ReviewHostConfig` (`extra="forbid"`, every field required, built on `acf.loader.require_file` and `load_model_file` as `load_host_config` is at `plugins/arch-compliance/python/acf/adr/host.py:28-33`):

| Field | Type | Meaning |
|---|---|---|
| `report_dir` | `PosixStr` | where `ARCHITECTURE_REVIEW_<date>.md` is written |
| `baseline_path` | `PosixStr` | the drift baseline |
| `baseline_max_age_days` | int > 0 | staleness threshold (§4.7 step 7) |
| `baseline_max_commits` | int > 0 | staleness threshold (§4.7 step 7) |
| `packs` | list of pack ids | technologies the repository uses; their `files` globs form the default target tree |
| `subsystems` | list of `PosixStr` prefixes | drift buckets, longest prefix wins and an unmatched path is `other`; an empty list keeps the first-segment rule of `plugins/arch-compliance/python/acf/baseline.py:50-56` |
| `exclude` | list of globs | added to the built-in exclusions of §4.7 step 2 |

`PosixStr` is the existing backslash-refusing alias (`plugins/arch-compliance/python/acf/adr/contract.py:129`). A missing `review.yml` fails loud and names `/acf-setup`. `## Declared, never defaulted` is extended to name `review.yml`, and records the review's three built-in meanings: the built-in exclusion list, an absent `surface`, and an empty `subsystems` list.

### 4.5 Mandate rows

The review reads `MANDATES_REL` with `load_mandates` and no detector arguments, as `plugins/arch-compliance/python/acf/cli_check_llm.py:54` does. An active row (`Mandate.is_active`) joins the review when its `auditor` field is set (`registry.py:61`):

- `auditor` is a rule id in `RULES` → its settings are read from `params` (§4.2); a wrong type fails loud with the mandate id.
- `auditor` ends in `.md` → a repository prompt (the hatch), resolved through `RepoTree.file`; a missing file fails loud; `params` passes to the auditor as given (JSON-only already: `registry.py:75-88`).
- Anything else → `UnknownMandateError` naming the row and the value.

Rows are grouped by `auditor`: one dispatch per rule id or prompt path, carrying every row that names it with its id, title, settings and doctrine section. A finding names its row by `mandate_id`, which must be one of the group's rows.

### 4.6 Doctrine sections

A new module `acf.doctrine` owns the doctrine document set and anchor resolution:

- `doctrine_paths(repo) -> list[str]`: `ARCH_REL` followed by each backticked token in `ARCH_REL`'s text (a trailing `:line` suffix stripped) that `RepoTree.file` resolves to an existing `.md` file, in order of first appearance. This is the set the ADR host contract already names, *"`config/architecture/ARCHITECTURE.md`, and … every document it points to. No doctrine field is declared"* (`docs/design/ADR_GATE_HOST_CONTRACT.md:79-81`); the ADR gate's own reading of it is unchanged.
- `anchor_section(texts, anchor) -> str`: the lines from the heading line equal to `anchor` (stripped) to the next heading of the same or a higher level. An anchor that is not a heading line exactly once across `texts` fails loud.
- `registry.missing_anchors(registry, texts: list[str])` returns the ids whose anchor `anchor_section` cannot resolve, so the review and the `acf-mandate` check apply one rule. It refuses a bare `str` with `TypeError`, since a `str` is itself a sequence of strings.

Measured at the cited commits by loading each registry with `yaml.safe_load` and counting, for each row's anchor, the stripped heading lines equal to it across the doctrine texts: every anchor in `config/architecture/mandates.yml` (17 rows), in both profiles, and in `hm:config/architecture/mandates.yml` (48 rows, against the origin pointer's documents) is a heading line found exactly once. Callers that change: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:91-99` (passes the texts of `doctrine_paths`), `tests/test_self_host.py:40`, `plugins/arch-compliance/tests/test_profile_drift.py:30`, `plugins/arch-compliance/tests/test_registry.py:60`; `plugins/arch-compliance/skills/acf-setup/SKILL.md:138-139` restates the rule. Known limit: in the origin repository the `acf-mandate` check loads through `load_gate_registry`, which refuses the origin's engine detector names until part two.

### 4.7 Controller procedure

The skill (`plugins/arch-compliance/skills/architecture-review/SKILL.md`, rewritten) keeps the origin invocation: `[--paths <glob>] [--include-tests] [--mandates <id,...>] [--update-baseline]`.

1. Load `review.yml`, the registry and the declared packs; validate every reviewed row (§4.5).
2. Resolve the target tree through `RepoTree.files(globs, exclude)`: files matching the packs' `files` globs, or `--paths`, minus the built-in exclusions (`.git/`, `.venv/`, `__pycache__/`, `node_modules/`, `.worktrees/`, `worktrees/`, `dist/`, `build/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`), `exclude`, and the test paths (`tests/`, `test_*.py`, `*_test.py`, `**/*.test.*`, `**/*.spec.*`) unless `--include-tests`. An empty tree raises `EmptyTargetTreeError`.
3. For each group, resolve each row's surface and doctrine section. A row with no `surface` uses the target tree. A row with a `surface` uses `RepoTree.files(surface, …)` minus `surface_exclude`, the built-in exclusions, `exclude` and test paths unless `--include-tests`; `--paths` does not narrow it, as the origin's frontend and template lists ignored `--paths` (`hm:.claude/skills/architecture-review/SKILL.md:51-61`). A declared `surface` matching no file fails loud with the mandate id.
4. Pre-pass: run the hints of the packs each row receives (§4.3) over its surface; render candidates as `file:line [tell] snippet`. A rule with no hints is still reviewed, without candidates.
5. Dispatch one read-only agent per group (tools `Read`, `Grep`, `Glob`), giving it the rule or repository prompt, `_contract.md`, its rows, surfaces, doctrine sections, `docs` and candidates.
6. Parse each payload with `acf.review.aggregator.parse_auditor_payload`, built on the shared extractor of §4.8. A contract violation marks that group FAILED, keeps its raw payload and error, and the run continues; any FAILED group makes the exit status non-zero.
7. Drift (report-only) against `baseline_path`, then staleness: the roll-up warns when the baseline is older than `baseline_max_age_days`, more than `baseline_max_commits` commits behind `HEAD`, or its commit is not in history (ported from `hm:scripts/ci/baseline_staleness.py:24-76`); then provenance: blame each finding's line and classify it against the baseline commit as pre-baseline, post-baseline, uncommitted or unresolved (ported from `hm:.claude/skills/architecture-review/SKILL.md:123-145`). Neither changes the exit status. Every `git` subprocess runs with `encoding="utf-8"`.
8. Render the report under `report_dir` (a same-day report gets a numeric suffix), optionally write the baseline, print the roll-up.

Every file the package reads (rule and repository prompts, doctrine documents, pack files, `review.yml`) is read with `encoding="utf-8"` (`## Declared text decoding`). Every host path string becomes a location through `RepoTree` (`contained` for write targets, `file`/`directory` for reads, the new `files` for globbing).

### 4.8 Contract, payloads, writes, baseline

- **Finding.** `acf.review.contract.AuditorFinding` carries `mandate_id`, `path` (`PosixStr`), `line`, `snippet`, `severity` (`blocking`, `important`, `nit`, `suggestion`), `rule`, `why`, `suggested_fix`. The gate's `acf.finding.Finding` (`plugins/arch-compliance/python/acf/finding.py:11-19`) is not reused because its severity is the gate's `BLOCK`/`WARN` and it carries detector provenance (`detector`, `confidence`, `detection`) that an auditor finding does not have, while it lacks `snippet`, `why` and `suggested_fix`. `acf.baseline.aggregate` is typed on a protocol of the two fields both models share, `mandate_id` and `path`, so one aggregation serves both. The current skill's mapping into `Finding` (`plugins/arch-compliance/skills/architecture-review/SKILL.md:108`) is removed with the rewrite.
- **Payload extraction.** The fence regex, the exactly-one-block check and the JSON decode of `plugins/arch-compliance/python/acf/adr/parser.py:26-60` move to `acf.agent_payload.extract_json_block(payload, *, subject)`, raising a new `AgentContractViolationError(AcfError)`. `ReviewerContractViolationError` subclasses it, and `parse_reviewer_payload` and `parse_auditor_payload` keep only their own policy (identity check and abort, versus a FAILED group).
- **Writes.** `acf.loader.write_text_record(path, text, *, error)` makes the parent directory, writes UTF-8 text and wraps `OSError` in `error` with the POSIX path. `save_baseline` (`baseline.py:68-75`), `write_run_detail` (`plugins/arch-compliance/python/acf/adr/run_detail.py:178-190`) and the report writer use it; the report's error is a new `ReportWriteError(AcfError)`.
- **Baseline.** `aggregate` folds by `(mandate_id, subsystem)`; `subsystem_of` takes the declared prefix list. Drift never changes the exit status.

New exports and their live call sites (`## Live consumers`):

| Export | Call site |
|---|---|
| `acf.repo.REVIEW_REL`, `acf.review.host.load_review_config` | skill step 1 |
| `acf.repo.RepoTree.files` | skill steps 2–3 |
| `acf.review.rules.RULES` and settings models | skill step 1 |
| `acf.review.packs.TechPack` loader | skill step 1 |
| `acf.review.prepass` scan | skill step 4 |
| `acf.doctrine.doctrine_paths`, `anchor_section` | skill step 3; `acf-mandate` check |
| `acf.agent_payload.extract_json_block`, `AgentContractViolationError` | `parse_reviewer_payload`; `parse_auditor_payload` (skill step 6) |
| `acf.review.contract` models | skill steps 6–8 |
| `acf.review.aggregator` (`parse_auditor_payload`, report render) | skill steps 6, 8 |
| `acf.review.rollup` (including staleness) | skill steps 7–8 |
| `acf.loader.write_text_record`, `ReportWriteError` | `save_baseline`, `write_run_detail`, skill step 8 |

### 4.9 Hatch

A row whose `auditor` names a repository `.md` file is dispatched with that prompt and `_contract.md`. Shapes a repository needs that no pack carries go in the row's `params` as text the auditor reads. This spec adds no repository-supplied code, so `acf-allow` is not involved (decision 14).

### 4.10 Absorbing `react-boundaries`

`plugins/arch-compliance/skills/architecture-review/auditors/react-boundaries.md` and `ui-logic-isolation` state one rule in two places. The React pack carries its "Check" and "Do not flag" shapes as hints. The rows naming `auditor: react-boundaries` change to `auditor: ui-logic-isolation`: `config/architecture/mandates.yml:51` and `plugins/arch-compliance/profiles/react-app/mandates.yml:36-46` (from `git grep -n "auditor:" -- ':!docs'`; the other hits, `config/architecture/mandates.yml:142` and the python-service profile, name `fail-loud`, which stays a rule id). `plugins/arch-compliance/skills/acf-mandate/SKILL.md:47` describes `auditor` as a rule id or a repository prompt path.

---

## 5. Origin repository cutover

The cutover is part of this spec. It lands in two stages, in order:

1. **Plugin stage.** The changes of §6 merge in this repository and release as `0.3.0`. The origin repository's developer reinstalls the plugin, and `scripts/check_installed_skills.py`, extended to the `architecture-review` skill tree, confirms the installed skill matches the release.
2. **Origin stage.** One PR in `hm:` makes the changes of §5.1–§5.6. Acceptance item 2 (§9) runs on that branch through the installed `0.3.0` plugin, as the last change before merge, as phase 1d's acceptance run did (`hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md`, phase 1d row: *"a live acceptance gate run through the installed plugin on the branch as the last change before squash-merge"*).

The spec is done when both stages have merged. A plugin defect the origin stage exposes is fixed by a plugin patch release before the origin PR merges. No origin file imports `acf` today (`git grep -l -E "^(from|import) acf" b2611977f -- scripts tests` prints nothing) and the cutover adds no such import, so origin CI needs no new dependency.

The origin repository's spec-authoring rule governs this stage: *"A spec that deletes or relocates anything writes its consumer census — with the grep recipes recorded in the spec, validated by confirming they reproduce every already-known site — before drafting the design section"* (`hm:CLAUDE.md:128`). §5.4 is that census.

### 5.1 Registry schema

`hm:scripts/core/architecture/registry.py:21-34` (`MandateEntry`, `extra="forbid"`) gains `languages` and `params`, and renames `gemini_anchor` to `arch_anchor`. Every row gains `languages`: `python` for rows whose subject is Python code, `typescript` for the admin JavaScript rows (`§6`, `admin-literal-type-gating`, `admin-notification-mechanism`), `none` otherwise. The field's consumers are in §5.4 (recipe B).

### 5.2 Row dispositions

The rows with an `auditor` value (recipe: `yaml.safe_load` over `hm:config/architecture/mandates.yml` at `b2611977f`, filtered on `auditor`; 25 rows):

| Row | Origin auditor | Rule | `params` |
|---|---|---|---|
| `§3` | fail-loud | fail-loud | — |
| `§3-exception-base` | fail-loud | fail-loud | `exception_base: {class_name: HistoricMansionsError, module: scripts/core/exceptions.py}` |
| `§4` | no-shims | no-shims | `exempt_paths: [scripts/core/repo_layout.py]` |
| `§4-mansion-slug-wire` | no-shims | no-shims | — |
| `§10`, `§10-discarded-validation` | posix-paths | posix-paths | — |
| `§10-path-field` | posix-paths | posix-paths | `path_types: [PosixPathStr]` |
| `three-tier`, `three-tier-batch`, `three-tier-ambient` | three-tier-hfsm | layer-boundaries | tiers and crossings from `hm:…/auditors/three-tier-hfsm.md:11-13` and its rules 1, 2, 5 |
| `§5`, `§5-fsm-mechanism` | three-tier-hfsm | state-machine-discipline | `base_classes: [DeclaredFSM]`, `validator_name: transition` (`hm:scripts/builders/fsm_base.py:14`, `:56`) |
| `path-provenance` | three-tier-hfsm | path-provenance | `classifier: scripts/core/asset_paths.py::is_platform_absolute` |
| `§11`, `§11-inventory` | metadata-facade | single-owner | `target_literal_re: 'index\.ya?ml'`, `allowlist_globs: [scripts/core/content_metadata_service.py]`, `inventory: docs/architecture/CONTENT_METADATA_ACCESS_INVENTORY.md`, `docs: [docs/architecture/IMAGES_YAML_FACADE.md]` |
| `§12.stage1`, `§12.stage2`, `§12.stage1-genre`, `§12.stage2-genre-hardcode` | output-agnosticism | pipeline-isolation | stage lists from `hm:…/auditors/output-agnosticism.md:12-32`, `variant_terms: [pdf, epub, html, genre]`, `raw_sources: ['\.docx']`, `canonical_artifact: build/` |
| `§13` | schema-presentation | presentation-as-data | `surface: ["templates/families/**/*.tex", "templates/families/**/*.css", "templates/families/*/style.yml"]`, `element_key: structural_realizations`, `variant_key: genres` |
| `§6`, `admin-literal-type-gating`, `admin-notification-mechanism` | ui-logic-isolation | ui-logic-isolation | `surface: ["admin/*.html", "admin/js/**/*.js"]`, `surface_exclude: ["admin/js/vendor/**"]` |
| `§14`, `§14-size` | class-cohesion | class-cohesion | `facades: [ContentMetadataService, CollectionService, ImagesYamlService]` |

### 5.3 Declaration

`hm:config/architecture/review.yml`: `report_dir: docs/reviews`, `baseline_path: docs/architecture/compliance_baseline.json`, `baseline_max_age_days: 30`, `baseline_max_commits: 250` (the origin's thresholds, `hm:scripts/ci/baseline_staleness.py:19-20`), `packs: [python, ts-js, html-templates]`, `subsystems` copied from `hm:scripts/core/architecture_review/baseline.py:20-28`, `exclude: [archive/, MagicMock/, temp_e2e_root/]`.

### 5.4 Consumer census and dispositions

Recipes, run at `b2611977f`, each reproducing the sites already known (the three `scripts/ci` importers, the skill trees, the four `gemini_anchor` code and test files):

- **A** `git grep -n -E "architecture_review|architecture-review|skill_install|ui_logic_prepass|baseline_staleness|BaselineStalenessError|_last_run" b2611977f -- ':!docs' ':!*.md'`
- **B** `git grep -n gemini_anchor b2611977f -- ':!docs'`
- **C** `git grep -n -E "ArchitectureReviewError|RubricMissingError|AuditorFailedError|AuditorContractViolationError|EmptyTargetTreeError|ReportWriteError|UnknownMandateError|BaselineError" b2611977f -- scripts tests`

| Site (`hm:`) | Recipe | Disposition |
|---|---|---|
| `.claude/skills/architecture-review/`, `.cursor/skills/architecture-review/` | A | deleted |
| `scripts/core/architecture_review/` (`__init__`, `_e2e_helper`, `aggregator`, `baseline`, `contract`, `facets`, `rollup`, `rubric`) | A | deleted |
| `scripts/core/architecture_review/ui_logic_prepass.py` | A | moves to `scripts/ci/ui_logic_prepass.py`; its CLI root `Path(__file__).parents[3]` (`:96-97`) becomes `parents[2]` |
| `scripts/ci/check_ui_prepass_staged.py:17`, `tests/test_ui_logic_prepass.py:2` | A | import from `scripts.ci.ui_logic_prepass` |
| `scripts/ci/arch_compliance/llm_judge.py:88-98` | A | `load_rubric(name)` reads `scripts/ci/arch_compliance/judge_prompts/<name>.md`; the four prompts the llm rows use (`three-tier-hfsm`, `ui-logic-isolation`, `schema-presentation`, `class-cohesion`) move there unchanged, as the gate's own copies; the caller at `:293` maps the row's mandate id to the prompt name in one dict, because the rows' `auditor` values become rule ids |
| `scripts/ci/arch_compliance/judge_calibration.py:61-62` | A (through `load_rubric`) | unchanged: it passes prompt names, which `load_rubric` resolves in the new directory |
| `tests/test_arch_llm_judge.py:49-58` | A | builds the `judge_prompts` directory instead of the skill trees |
| `tests/fixtures/arch_judge_corpus/s5_bad_boolean_flags.py:4`, `s5_bad_state_mutation_outside_transition.py:4` | A | comments point to `judge_prompts/three-tier-hfsm.md` |
| `scripts/ci/baseline_staleness.py`, `tests/test_baseline_staleness.py`, `scripts/setup_git_hooks.py:138`, `tests/test_push_scope_hook.py:21,25` | A | the module and its test are deleted; the pre-push line and its two assertions are removed (decision 8) |
| `scripts/core/skill_install.py`, `tests/test_skill_install.py` | A | deleted: recipe A finds `scripts/core/architecture_review/__init__.py:10` as the module's only importer outside its own test, and `git ls-tree -d --name-only b2611977f .cursor/skills/` lists only `architecture-review` |
| `tests/test_arch_baseline.py`, `test_arch_facets.py`, `test_arch_review_aggregator.py`, `test_arch_review_contract.py`, `test_arch_review_rollup.py`, `test_arch_review_rubric.py`, `test_rubric_extract_section6.py`; `tests/fixtures/architecture_review_skill/` | A | deleted with the modules they test |
| `tests/test_mandate_registry_drift.py:84-93` | A | the auditor-pointer test is deleted: the plugin refuses an unknown `auditor` at run time (§4.5), and origin CI cannot import the plugin's rule list |
| `config/architecture/ARCHITECTURE.md:8-9` | A | points to `config/architecture/arch-docs-manifest.yml`, where the manifest moves |
| `config/architecture/coverage_map.yml:111,118,290,294,332,336,339,341,343,354,358` | A | backstop strings name the new rule ids and the moved pre-pass path |
| `config/architecture/mandates.yml:516` | A | remediation text names the moved pre-pass path |
| `scripts/schemas/types.py:9` | A | docstring no longer names the deleted contract |
| `config/architecture/dead_code_baseline.json:44-46,196-201,265` | A | entries for deleted symbols removed (a shrink) |
| `config/architecture/dead_code_baseline.json:195` | B | key renamed to `MandateEntry.arch_anchor`, so the ratchet sees no new test-only key |
| `config/architecture/debt_baseline.json:131` | A | entry for the deleted contract module removed |
| `scripts/core/architecture/registry.py:33`, `tests/test_arch_mandate_registry.py:24,48,65,81,90`, `tests/test_mandate_registry_drift.py:43,60,62`, `tests/test_run_guards.py:111` | B | renamed to `arch_anchor` |
| `scripts/core/exceptions.py:1241-1280` (six review classes), `:1380` (`BaselineStalenessError`), `:1452` (`UnknownMandateError`), `:1456` (`BaselineError`) | C, A | deleted: their raisers and their tests are deleted above |
| `scripts/ci/arch_compliance/engine.py:815-843` | C | the deleted classes' names leave the exception-name mirror |

### 5.5 Cursor follow-up

The cutover PR adds a Parked row to the origin roadmap board for Cursor access to `arch-compliance:architecture-review`, beside the existing row for the two gate skills (`hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:360`), which names only *"`arch-compliance:adversarial-design-review` and `arch-compliance:responding-to-adversarial-review`"*.

### 5.6 Baseline reset

The origin baseline counts one label per auditor, and the `three-tier-hfsm` label spans six rows (§5.2), so no count splits across mandate ids. The cutover PR deletes `hm:docs/architecture/compliance_baseline.json` and runs `/arch-compliance:architecture-review --update-baseline` once; the prior baseline stays in git history.

---

## 6. Change surface (this repository)

| Path | Change |
|---|---|
| `plugins/arch-compliance/python/acf/review/` (new) | modules `__init__`, `contract`, `host`, `rules`, `packs`, `prepass`, `aggregator`, `rollup`; six pack files under `packs/` |
| `plugins/arch-compliance/python/acf/doctrine.py` (new) | `doctrine_paths`, `anchor_section` |
| `plugins/arch-compliance/python/acf/agent_payload.py` (new) | `extract_json_block` |
| `plugins/arch-compliance/python/acf/adr/parser.py` | uses `extract_json_block` |
| `plugins/arch-compliance/python/acf/repo.py` | `REVIEW_REL`; `RepoTree.files` |
| `plugins/arch-compliance/python/acf/registry.py` | `missing_anchors` over a list of texts, through `anchor_section` |
| `plugins/arch-compliance/python/acf/loader.py` | `write_text_record` |
| `plugins/arch-compliance/python/acf/baseline.py` | aggregates the shared protocol; declared subsystem prefixes; writes through `write_text_record` |
| `plugins/arch-compliance/python/acf/adr/run_detail.py` | writes through `write_text_record` |
| `plugins/arch-compliance/python/acf/exceptions.py` | `AgentContractViolationError`; `ReviewerContractViolationError` subclasses it; `ReportWriteError` |
| `plugins/arch-compliance/skills/architecture-review/SKILL.md` | rewritten (§4.7) |
| `plugins/arch-compliance/skills/architecture-review/rules/` (new) | twelve rule prompts and `_contract.md` |
| `plugins/arch-compliance/skills/architecture-review/auditors/` | deleted (four files) |
| `plugins/arch-compliance/skills/acf-mandate/SKILL.md` | `:47` auditor description; `:91-99` anchor check over `doctrine_paths` |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md` | `:138-139` anchor rule; writes `review.yml` |
| `config/architecture/mandates.yml`, `plugins/arch-compliance/profiles/react-app/mandates.yml` | `auditor: ui-logic-isolation` (§4.10) |
| `config/architecture/review.yml` (new) | this repository's declaration: `packs: [python, ts-js]` |
| `config/architecture/ARCHITECTURE.md` | `## React boundaries` names the rule; `## Declared, never defaulted` names `review.yml` and records §4.4's built-in meanings; `## One owner for host paths` (`:121-125`) and `## Single point of definition` (`:273-274`) retire the recorded `architecture-review/SKILL.md:62` breach; `## Release discipline` names the extended check |
| `scripts/check_installed_skills.py` | covers `architecture-review` |
| `plugins/arch-compliance/tests/test_adr_skill_prose.py` | the forbidden-vocabulary check covers `architecture-review` and the pack files |
| `tests/test_self_host.py`, `plugins/arch-compliance/tests/test_profile_drift.py`, `plugins/arch-compliance/tests/test_registry.py`, `plugins/arch-compliance/tests/test_baseline.py` | callers of the changed signatures |
| `README.md` | 0.3.0 upgrade note: `review.yml` is required; `auditor` values are rule ids |
| `pyproject.toml:3`, `plugins/arch-compliance/.claude-plugin/plugin.json:3` | `0.2.5` → `0.3.0` |

---

## 7. Tests

- `test_review_rules.py`: every `RULES` key has a prompt file and every prompt file a key; a wrong-typed key fails with the mandate id; unread `params` keys are listed; an unknown `auditor` raises `UnknownMandateError`; an inactive row is not reviewed.
- `test_review_packs.py`: each pack loads; hint keys are rule ids; patterns compile; an add-on without its base is refused; a `detectors` key is refused; a `python` row receives `python` and `none`-language hints and no `ts-js` hints.
- `test_review_host.py`: a missing field, an extra field, a backslash path and a missing file each fail loud.
- `test_doctrine.py`: `doctrine_paths` order and existence filtering; section bounds by heading level; zero, two or non-heading matches fail; `missing_anchors` refuses a `str`.
- `test_agent_payload.py`: zero blocks, two blocks and bad JSON raise `AgentContractViolationError`; the ADR parser's existing tests pass unchanged.
- `test_review_prepass.py`: candidates per pack, language and surface; `surface_exclude` applies; no hints yields no candidates.
- `test_review_aggregator.py`: payload parsing; a finding outside the group's rows is a violation; the report does not overwrite.
- `test_review_rollup.py`: staleness by age, by commits and by a missing commit; no warning when fresh.
- `test_repo.py`: `RepoTree.files` matches, excludes and stays inside the root.
- `test_baseline.py`: aggregation over both finding models; prefix subsystems, longest wins, `other` for unmatched; empty list keeps first-segment behaviour.
- `test_loader.py`: `write_text_record` wraps `OSError` in the given error.
- Prose: no rule prompt, skill file or pack file contains the forbidden origin vocabulary.

---

## 8. Risks

| Risk | Handling |
|---|---|
| Generic prompts lose precision the origin auditors' hard-coded lists gave | Settings carry the lists; acceptance compares finding counts per rule on the origin repository (§9). |
| `presentation-as-data` assumes a style schema with element and variant keys | The keys are settings; a repository without such a schema does not enable the rule. |
| Svelte and SQL hints are regular expressions over raw text | They seed candidates; the auditor decides. |
| A shared `params` key means different things to a detector and a rule | Rule keys reuse the built-in detector's key names for the same subject (decision 10); the report lists keys a rule did not read. |
| Staleness now shows when the review runs, not on every origin push | Decision 8. |
| The origin pre-pass tells live in the moved gate module and in the `ts-js` pack until part two | Part two moves the gate's staged check onto the plugin (§10). |

---

## 9. Acceptance

1. Suite and diff gate pass in this repository; this repository's own `/arch-compliance:architecture-review` runs end to end.
2. On the origin repository's cutover branch, `/arch-compliance:architecture-review` runs end to end; per rule, its finding count is compared with the last origin report, and differences are listed in the cutover PR.
3. A scratch repository with only `ts-js` and `svelte` packs and one `ui-logic-isolation` row runs end to end with no origin path anywhere.

---

## 10. Follow-ups

- Part two: the origin repository's detectors, guards and judge onto `acf-check-diff`, including the pack `detectors` slot, Svelte script extraction, one file-to-technology map shared with the gate's suffix routing, and the gate's staged UI check moved onto `acf.review.prepass`.
- Phase 1e: Cayenne installs the plugin.
