# Architecture Review Port: Generic Rules, Technology Packs and Repository Settings

**Status:** Draft (v1)
**Date:** 2026-11-12
**Spec kinds:** `feature`
**Repo:** `IanDBallard/arch-compliance-for-superpowers`, `main` at `50d727f` (branch `feat/architecture-review-port`).
**Roadmap:** workstream E phase 2, part one of two (`hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md`, section "Workstream E — Portable governance skills"). Part two, moving the origin repository's enforcement gate onto `acf-check-diff`, is a separate later spec (§10).
**Governing mandates:** `config/architecture/ARCHITECTURE.md` sections `## Fail loud` (`:26-44`), `## No shims` (`:45-56`), `## POSIX paths` (`:57-67`), `## React boundaries` (`:101-107`), `## One base exception` (`:108-113`), `## One owner for host paths` (`:114-141`), `## Declared, never defaulted` (`:187-203`), `## Prose names no host` (`:204-213`), `## Live consumers` (`:222-227`), `## No completeness claims` (`:228-239`), `## Release discipline` (`:253-264`), `## Single point of definition` (`:265-279`).
**No state-machine surface.** This design adds or modifies no state machine and no transition.

---

## 0. Citation convention

Unprefixed paths are this repository at `50d727f`. `hm:` paths are the HistoricMansions checkout at `b2611977f`; every rule of that repository this spec relies on is quoted where it is used. `cy:` paths are the Cayenne checkout at `d0d749bc`, cited only for its file types; nothing in `cy:` changes. Paths are POSIX.

---

## 1. Intent

The plugin's `/architecture-review` is a generic rewrite with four auditors (`plugins/arch-compliance/skills/architecture-review/SKILL.md:72`). The origin repository's review is richer: nine auditors, a doctrine rubric step, per-auditor file surfaces, a deterministic UI pre-pass, a blame-based provenance section and a JSON sidecar (`hm:.claude/skills/architecture-review/SKILL.md:31-158`). Its auditors hard-code the origin repository's paths, class names and section numbers, for example *"`ContentMetadataService` is the only allowed accessor for `index.yml` content"* (`hm:.claude/skills/architecture-review/auditors/metadata-facade.md:3`) and the twelve stage file lists in `hm:.claude/skills/architecture-review/auditors/output-agnosticism.md:12-32`.

The goal is to keep every capability of the origin repository's review and move every repository dependency out of the plugin, so any repository supplies its own. The decisions of §2 split what the review knows into three layers that change for different reasons: the rule, the technology the rule is read in, and the repository's settings.

---

## 2. Decisions

| # | Decision | Made by |
|---|---|---|
| 1 | Port with capabilities kept; repository dependencies isolated so a repository supplies its own components. | user |
| 2 | Rules are technology-independent. What a rule looks like in one technology is a separate, plugin-shipped **technology pack**, not a repository setting. | user |
| 3 | A **hatch** lets a repository supply its own auditor prompt for a rule that does not generalise. | user |
| 4 | Scope excludes performance and code-quality rules. Security is out of scope except where a rule states *where* enforcement must live; row-level security on client-reachable tables is in. | user |
| 5 | The first release ships packs for the origin repository's stack and Cayenne's: Python, TypeScript/JavaScript, Svelte, React, HTML templates, SQL. | user |
| 6 | Two specs: this one builds the framework and ports the review; the enforcement gate migrates later against it. | user |
| 7 | Every rule is opt-in through a mandate row; no rule runs by default. | author |
| 8 | A rule's repository settings live under `params.review` on the mandate row, leaving other `params` keys to detectors. | author |
| 9 | The pack format reserves a `detectors` slot whose shape this spec fixes and part two adds (§4.3); this spec ships `hints` only, because a field nothing reads is dead code (`## Live consumers`). | author |
| 10 | The origin repository's drift baseline is reset at cutover, not migrated (§5.5). | author |
| 11 | The plugin's `react-boundaries` auditor is absorbed into the generic `ui-logic-isolation` rule, with React shapes in the React pack (§4.10). | author |
| 12 | A repository-supplied auditor prompt needs no `acf-allow` approval: it is text read by read-only agents, as the audited code is. This spec adds no repository-supplied executable code. | author |
| 13 | Cursor copies of the skill are out of scope, as in phase 1d (`hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md`, "Workstream E 1d follow-up — Cursor / Cline gate access"). | author |

---

## 3. Non-goals

- Moving any AST detector or script guard, or the origin repository's LLM judge, onto the plugin (part two, §10).
- Script-block extraction for `.svelte` files. The review auditors read `.svelte` text directly and pack hints are regular expressions over that text; deterministic Svelte detectors need extraction and belong to part two.
- New rules beyond the twelve in §4.2. Candidate rules raised during design and deferred: single point of definition, contract fidelity of schema migrations.
- Changing the gate's Tier-2 judge (`plugins/arch-compliance/python/acf/judge.py`) or its `llm_react_boundaries` prompt id (`judge.py:31`).

---

## 4. Design

### 4.1 Layers

| Layer | Example (single owner) | Lives in | Trust |
|---|---|---|---|
| Rule: principle, what to flag, severity rubric | "a declared artifact is read and written only through its declared owner" | `plugins/arch-compliance/skills/architecture-review/rules/<rule>.md` plus its settings model in `acf.review.rules` | plugin |
| Technology pack: the shapes a rule takes in one technology | Python: `open(`, `yaml.safe_load`, `Path(...) / "x"`; TypeScript: `fs.read`, `supabase.from(` | `plugins/arch-compliance/python/acf/review/packs/<pack>.yml` | plugin |
| Repository settings | artifact `index.yml`, owner `ContentMetadataService` | the mandate row's `params.review` | data |
| Hatch | a rule with no generic form | a repository Markdown prompt named by the row's `auditor` | data (decision 12) |

### 4.2 Rule library

Each rule has a prompt file and a settings model (Pydantic, `extra="forbid"`) registered in `acf.review.rules.RULES: dict[str, type[RuleSettings]]`. `RuleSettings` carries the fields every rule accepts: `surface: list[str] | None` (globs; absent means the whole target tree), `surface_exclude: list[str]` (default empty) and `docs: list[str]` (repository documents the auditor reads in full; default empty). The "Source" column names the origin auditor whose method the rule generalises.

| Rule id | Principle | Settings beyond `RuleSettings` | Source |
|---|---|---|---|
| `fail-loud` | Errors halt and report; no broad catch, silent success default or interface probing | `exception_base: {class_name, module} \| None` | `hm:…/auditors/fail-loud.md`; plugin `auditors/fail-loud.md` |
| `no-shims` | No compatibility branches, soft fallbacks, internal retries or migration shims | `exempt_paths: list[str]` | `hm:…/auditors/no-shims.md`; plugin `auditors/no-shims.md` |
| `posix-paths` | Persisted paths are POSIX strings of a declared path type | `path_types: list[str]` | plugin `auditors/posix-paths.md` |
| `class-cohesion` | A class holds one responsibility; judged by cohesion, not size | `facades: list[str]` (exempt from width) | `hm:…/auditors/class-cohesion.md` |
| `ui-logic-isolation` | The UI renders and dispatches; it does not decide domain rules or mirror backend state | none | `hm:…/auditors/ui-logic-isolation.md`; plugin `auditors/react-boundaries.md` |
| `single-owner` | A declared persisted artifact (file pattern or table) is read and written only through its declared owner; an inventory tracks known exceptions | `artifacts: list[str]`, `owners: list[str]`, `inventory: str \| None` | `hm:…/auditors/metadata-facade.md` |
| `pipeline-isolation` | Shared stages never branch on the output variant; variant stages consume only the canonical intermediate artifact | `shared_stages`, `variant_stages`, `exempt: list[str]`; `variant_terms`, `raw_sources: list[str]`; `canonical_artifact: str` | `hm:…/auditors/output-agnosticism.md` |
| `presentation-as-data` | Appearance values live in a declared style schema; every element × variant pair is declared; one live schema version | `bindings`, `style_schema: list[str]`; `element_key`, `variant_key: str` | `hm:…/auditors/schema-presentation.md` |
| `layer-boundaries` | Code in one tier reaches another tier's resources only through a declared boundary | `tiers: list[{name, paths}]`, `crossings: list[{from_tier, to_tier, root_names, via}]` | `hm:…/auditors/three-tier-hfsm.md` rules 1, 2, 5 |
| `state-machine-discipline` | State changes only inside the declared transition method; transitions raise their declared failure types | `markers`, `transition_methods`, `base_classes: list[str]` | `hm:…/auditors/three-tier-hfsm.md` rules 3, 4 |
| `path-provenance` | An externally sourced path is classified by the declared cross-platform helper, never by the host platform's absolute-path test | `classifier: str` | `hm:…/auditors/three-tier-hfsm.md` rule 6 |
| `data-access-boundary` | Access control is enforced at the data layer, not trusted to the client: client-reachable tables enforce row-level policy, and privileged credentials never reach client code | `client_paths`, `policy_files`, `privileged_credentials`, `replication_rules: list[str]` | new (decision 4) |

For `data-access-boundary`, a table is client-reachable when code under `client_paths` names it or a file in `replication_rules` selects it. The rule flags: a client-reachable table whose `policy_files` never enable row-level security on it; a `privileged_credentials` name appearing under `client_paths`; and a query in `replication_rules` that selects a client-reachable table's rows without filtering by the authenticated user, so replication exposes rows that row-level security would hide.

A rule prompt names no repository (`## Prose names no host`): every repository value reaches the auditor as a row's settings. One output contract, `plugins/arch-compliance/skills/architecture-review/rules/_contract.md`, is given to every auditor with its rule prompt, so the JSON shape is stated once.

### 4.3 Technology packs

A pack file is loaded by `acf.review.packs.TechPack` (`extra="forbid"`):

```yaml
id: typescript
extends: null          # or the id of the base pack an add-on builds on
files: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx", "**/*.mjs", "**/*.cjs"]
hints:
  ui-logic-isolation:
    - pattern: '\.(filter|reduce)\('
      tell: client-side aggregation
```

`hints` keys must be rule ids in `RULES`; each `pattern` must compile as a Python regular expression. A repository declaring an add-on pack without its base is refused. A pack's hints scan only files matching that pack's own `files` globs, and `extends` adds one thing: the base pack's hints also scan the add-on's files. So with `svelte` declared, the TypeScript `ui-logic-isolation` hints scan `.svelte` files too; Python hints never scan an `.html` file, even inside a surface; React hints scan only `.tsx` and `.jsx`. An add-on inherits no `files` and repeats no base hint. Pack hints feed the pre-pass (§4.7 step 4), which generalises the origin repository's §6-only pre-pass (`hm:scripts/core/architecture_review/ui_logic_prepass.py:26-50`) to every rule.

Reserved for part two: `detectors: {<rule id>: [<built-in detector id>]}`, each id a key of `KNOWN_DETECTORS`. This spec's model does not accept the key, so part two adds it with its first consumer.

First-release packs and the rules each carries hints for:

| Pack | Extends | Rules with hints | Hint sources |
|---|---|---|---|
| `python` | — | fail-loud, no-shims, posix-paths, single-owner, pipeline-isolation, layer-boundaries, state-machine-discipline, path-provenance | the origin auditors' "Detection patterns" sections |
| `typescript` | — | fail-loud, no-shims, ui-logic-isolation, single-owner, data-access-boundary | the origin pre-pass tells; `supabase.from(`, `createClient(` with a service key |
| `react` | typescript | ui-logic-isolation | plugin `auditors/react-boundaries.md` "Check" |
| `svelte` | typescript | ui-logic-isolation | `$:` reactive statements and `<script>` blocks computing domain values |
| `html-templates` | — | ui-logic-isolation, presentation-as-data | the origin pre-pass's HTML tells |
| `sql` | — | data-access-boundary, single-owner, no-shims | `create table` without `enable row level security`; `create view` named as a legacy or compatibility view |

### 4.4 Repository declaration

A repository declares the review's host values in `config/architecture/review.yml`, located by a new `acf.repo.REVIEW_REL` and loaded by `acf.review.host.load_review_config` into `ReviewHostConfig` (`extra="forbid"`, every field required, following `AdrHostConfig` at `plugins/arch-compliance/python/acf/adr/host.py:19-25`):

| Field | Type | Meaning |
|---|---|---|
| `report_dir` | POSIX path | where `ARCHITECTURE_REVIEW_<date>.md` is written |
| `baseline_path` | POSIX path | the drift baseline |
| `sidecar_path` | POSIX path | the run's JSON sidecar |
| `packs` | list of pack ids | technologies the repository uses; their `files` globs form the default target tree |
| `doctrine_docs` | list of POSIX paths | documents beyond `ARCH_REL` that hold `arch_anchor` headings (may be empty) |
| `subsystems` | list of path prefixes | drift buckets, longest prefix wins; an empty list keeps the first-segment rule of `plugins/arch-compliance/python/acf/baseline.py:50-56` |
| `exclude` | list of globs | added to the built-in exclusions |

A missing `review.yml` fails loud and names `/acf-setup` (`## Declared, never defaulted`).

### 4.5 Mandate rows

The review reads `MANDATES_REL` with `load_mandates` and no detector arguments, as `plugins/arch-compliance/python/acf/cli_check_llm.py:54` does. A row joins the review when its `auditor` field is set (`plugins/arch-compliance/python/acf/registry.py:61`):

- `auditor` is a rule id in `RULES` → `params.review` is validated by that rule's settings model; an invalid value fails loud with the mandate id.
- `auditor` ends in `.md` → a repository prompt (the hatch), resolved through `RepoTree.file`; a missing file fails loud. `params.review` passes through unvalidated (it is already JSON-only: `registry.py:75-88`).
- Anything else → `UnknownMandateError` naming the row and the value.

Rows are grouped by `auditor`: one dispatch per rule id or prompt path, carrying every row that names it with its id, title, settings and doctrine section. Findings name the row they belong to by `mandate_id`, which must be one of the rows handed to that auditor.

### 4.6 Doctrine sections

`acf.review.doctrine.doctrine_section(texts, anchor)` returns the lines from the heading equal to `anchor` (stripped) to the next heading of the same or a higher level, across `ARCH_REL` plus `doctrine_docs`. An anchor found zero times or more than once fails loud. `missing_anchors` (`registry.py:220-223`) takes a sequence of doctrine texts instead of one, so the `acf-mandate` check and the review resolve anchors over the same document set; `acf-mandate`'s snippet (`plugins/arch-compliance/skills/acf-mandate/SKILL.md:91-99`) passes `ARCH_REL` plus `doctrine_docs` when `review.yml` exists and `ARCH_REL` alone otherwise.

### 4.7 Controller procedure

The skill (`plugins/arch-compliance/skills/architecture-review/SKILL.md`, rewritten) keeps the origin invocation: `[--paths <glob>] [--include-tests] [--mandates <id,...>] [--update-baseline]`.

1. Load `review.yml`, the registry and the declared packs; validate every reviewed row (§4.5).
2. Resolve the target tree: files on disk matching the packs' `files` globs, or `--paths`, minus the built-in exclusions, `exclude`, and test paths unless `--include-tests`. An empty tree raises `EmptyTargetTreeError`.
3. For each dispatch group, resolve each row's surface and its doctrine section. A row with no `surface` uses the target tree of step 2. A row with a `surface` uses the files on disk matching it, minus `surface_exclude`, the built-in exclusions, `exclude`, and test paths unless `--include-tests`; it is not restricted to pack globs and `--paths` does not narrow it, as the origin's frontend and template lists ignored `--paths` (`hm:.claude/skills/architecture-review/SKILL.md:53-61`). A declared `surface` that matches no file fails loud with the mandate id: it is a settings error, not an empty run.
4. Pre-pass: run the hint patterns of every declared pack that has hints for the group's rule over the group's surfaces; render candidates as `file:line [tell] snippet`. A rule with no hints in any declared pack is still reviewed, without candidates.
5. Dispatch one read-only agent per group (tools `Read`, `Grep`, `Glob`), giving it the rule prompt or repository prompt, `_contract.md`, its rows, surfaces, doctrine sections, `docs` and candidates.
6. Parse each payload (`acf.review.aggregator.parse_auditor_payload`). A contract violation marks that group FAILED, keeps the raw payload and error, and the run continues; any FAILED group makes the exit status non-zero.
7. Drift (report-only) against `baseline_path`, then provenance: blame each finding's line and classify it against the baseline commit as pre-baseline, post-baseline, uncommitted or unresolved (ported unchanged from `hm:.claude/skills/architecture-review/SKILL.md:123-145`).
8. Render the report to `report_dir` (no overwrite: a same-day report gets a numeric suffix), write the sidecar, optionally write the baseline, print the roll-up.

### 4.8 Contract, aggregation, baseline

`acf.review.contract` ports `AuditorFinding`, `AuditorResult` and `ReviewRun` (`hm:scripts/core/architecture_review/contract.py`, 59 lines) with `mandate_id` replacing the free-text `mandate` label. `acf.baseline.aggregate` folds `AuditorFinding` rows by `(mandate_id, subsystem)`; `subsystem_of` gains the declared prefix list. Severities stay `blocking`, `important`, `nit`, `suggestion`. Drift never changes the exit status.

New exceptions, each subclassing `AcfError` only (`## One base exception`): `AuditorContractViolationError`, `ReportWriteError`.

### 4.9 Hatch

A row whose `auditor` names a repository `.md` file is dispatched with that prompt and `_contract.md`. Shapes a repository needs that no pack carries go in that row's settings as text the auditor reads; this spec adds no repository-supplied code, so `acf-allow` is not involved (decision 12).

### 4.10 Absorbing `react-boundaries`

`plugins/arch-compliance/skills/architecture-review/auditors/react-boundaries.md` and `ui-logic-isolation` state one rule in two places (`## Single point of definition`). The React pack carries its "Check" and "Do not flag" shapes as hints; the react-app profile row `soft.react-boundaries` (`plugins/arch-compliance/profiles/react-app/mandates.yml:36-46`) changes `auditor: react-boundaries` to `auditor: ui-logic-isolation`. Its `detector: llm_react_boundaries` is the gate's judge and is unchanged (§3).

---

## 5. Origin repository cutover

The cutover is part of this spec. It lands in two stages, in order:

1. **Plugin stage.** The changes of §6 merge in this repository and release as `0.3.0`. The origin repository's developer reinstalls the plugin, and `scripts/check_installed_skills.py` confirms the installed skill matches the release.
2. **Origin stage.** One PR in `hm:` makes the changes of §5.1–§5.6. Acceptance item 2 (§9) runs on that branch through the installed `0.3.0` plugin, as the last change before merge, as phase 1d's acceptance run did (`hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md`, phase 1d row: *"a live acceptance gate run through the installed plugin on the branch as the last change before squash-merge"*).

The spec is done when both stages have merged. A defect the origin stage exposes in the plugin is fixed by a plugin patch release before the origin PR merges.

### 5.1 Registry schema

`hm:scripts/core/architecture/registry.py:21-34` (`MandateEntry`, `extra="forbid"`) gains `languages` and `params`, and renames `gemini_anchor` to `arch_anchor`. Consumers of the field in code and tests, from `git grep -n gemini_anchor -- scripts tests` at `b2611977f`: `hm:scripts/core/architecture/registry.py:33`, `hm:tests/test_arch_mandate_registry.py:24,48,65,81,90`, `hm:tests/test_mandate_registry_drift.py:43,60,62`, `hm:tests/test_run_guards.py:111`. Every row gains `languages` (`python` for Python-tree rows, `none` for rows whose subject is not code in one language).

### 5.2 Row dispositions

The rows with an `auditor` value, from `yaml.safe_load` over `hm:config/architecture/mandates.yml` filtered on `auditor`:

| Row | Origin auditor | Rule | `params.review` |
|---|---|---|---|
| `§3` | fail-loud | fail-loud | — |
| `§3-exception-base` | fail-loud | fail-loud | `exception_base: {class_name: HistoricMansionsError, module: scripts/core/exceptions.py}` |
| `§4` | no-shims | no-shims | `exempt_paths: [scripts/core/repo_layout.py]` |
| `§4-mansion-slug-wire` | no-shims | no-shims | — |
| `§10`, `§10-discarded-validation` | posix-paths | posix-paths | — |
| `§10-path-field` | posix-paths | posix-paths | `path_types: [PosixPathStr]` |
| `three-tier`, `three-tier-batch`, `three-tier-ambient` | three-tier-hfsm | layer-boundaries | tiers and crossings from `hm:…/auditors/three-tier-hfsm.md:11-13` and rules 1, 2, 5 |
| `§5`, `§5-fsm-mechanism` | three-tier-hfsm | state-machine-discipline | `markers: [scripts/core/transition_validator.py]`, `base_classes: [DeclaredFSM]` |
| `path-provenance` | three-tier-hfsm | path-provenance | `classifier: scripts/core/asset_paths.py::is_platform_absolute` |
| `§11`, `§11-inventory` | metadata-facade | single-owner | `artifacts: [index.yml]`, `owners: [ContentMetadataService]`, `inventory: docs/architecture/CONTENT_METADATA_ACCESS_INVENTORY.md`, `docs: [docs/architecture/IMAGES_YAML_FACADE.md]` |
| `§12.stage1`, `§12.stage2`, `§12.stage1-genre`, `§12.stage2-genre-hardcode` | output-agnosticism | pipeline-isolation | stage lists from `hm:…/auditors/output-agnosticism.md:12-32`, `variant_terms: [pdf, epub, html, genre]`, `raw_sources: ['\.docx']`, `canonical_artifact: build/` |
| `§13` | schema-presentation | presentation-as-data | `surface: ["templates/families/**"]`, `element_key: structural_realizations`, `variant_key: genres` |
| `§6`, `admin-literal-type-gating`, `admin-notification-mechanism` | ui-logic-isolation | ui-logic-isolation | `surface: ["admin/*.html", "admin/js/**/*.js"]`, `surface_exclude: ["admin/js/vendor/**"]` |
| `§14`, `§14-size` | class-cohesion | class-cohesion | `facades: [ContentMetadataService, CollectionService, ImagesYamlService]` |

### 5.3 Declaration

`hm:config/architecture/review.yml`: `report_dir: docs/reviews`, `baseline_path: docs/architecture/compliance_baseline.json`, `sidecar_path: build/architecture_review/_last_run.json`, `packs: [python, typescript, html-templates]`, `doctrine_docs: [GEMINI.md]`, `subsystems` copied from `hm:scripts/core/architecture_review/baseline.py:20-28`, `exclude: [archive/, MagicMock/, temp_e2e_root/]`.

### 5.4 What the enforcement gate keeps

Three gate files import the review package, from `git grep -n architecture_review -- scripts/ci` at `b2611977f`. Each keeps working before part two:

| Gate file | Uses | After cutover |
|---|---|---|
| `hm:scripts/ci/arch_compliance/llm_judge.py:88-98` | `load_rubric(auditor)` reads `<auditor>.md` from the skill's auditors directory as the judge prompt | the five prompts the llm rows use move to a gate-owned directory, keyed by mandate id in `hm:scripts/ci/arch_compliance/llm_judge.py`, because the rows' `auditor` values become rule ids |
| `hm:scripts/ci/baseline_staleness.py:87` | `load_baseline` from the review package | `acf.baseline.load_baseline` |
| `hm:scripts/ci/check_ui_prepass_staged.py:17` | `scan_text` from `ui_logic_prepass` | `hm:scripts/core/architecture_review/ui_logic_prepass.py` moves under `hm:scripts/ci/` as gate-owned code |

`hm:tests/test_mandate_registry_drift.py:84-93` (auditor pointers resolve to prompt files) changes to check that each `auditor` is a plugin rule id.

### 5.5 Baseline reset

The origin baseline counts one label per auditor, and one label spans up to six rows (three-tier-hfsm covers six rows in §5.2), so no count can be split across mandate ids. The cutover PR deletes `hm:docs/architecture/compliance_baseline.json` and runs `/arch-compliance:architecture-review --update-baseline` once; the prior baseline stays in git history.

### 5.6 Deletions

`hm:.claude/skills/architecture-review/` and `hm:.cursor/skills/architecture-review/`; from `hm:scripts/core/architecture_review/`, every module except the one §5.4 moves; their tests (`hm:tests/test_arch_baseline.py`, `hm:tests/test_arch_facets.py`, `hm:tests/test_arch_review_aggregator.py`, `hm:tests/test_arch_review_contract.py`, `hm:tests/test_arch_review_rollup.py`, `hm:tests/test_arch_review_rubric.py`, `hm:tests/test_rubric_extract_section6.py`, and the fixture `hm:tests/fixtures/architecture_review_skill/`). `hm:scripts/core/skill_install.py` stays: the other dual-installed skill uses it. The docs manifest moves to `hm:config/architecture/arch-docs-manifest.yml`, and `hm:config/architecture/ARCHITECTURE.md:9-10`, which reads *"The architecture documents listed, in order, in `.claude/skills/architecture-review/rubric/arch-docs-manifest.yml`"*, points to the new path.

---

## 6. Change surface (this repository)

| Path | Change |
|---|---|
| `plugins/arch-compliance/python/acf/review/` (new) | modules `__init__`, `contract`, `host`, `rules`, `packs`, `doctrine`, `prepass`, `aggregator`, `rollup`; six pack files under `packs/` |
| `plugins/arch-compliance/python/acf/repo.py` | `REVIEW_REL` |
| `plugins/arch-compliance/python/acf/registry.py` | `missing_anchors` takes a sequence of texts |
| `plugins/arch-compliance/python/acf/baseline.py` | aggregates `AuditorFinding`; declared subsystem prefixes |
| `plugins/arch-compliance/python/acf/exceptions.py` | `AuditorContractViolationError`, `ReportWriteError` |
| `plugins/arch-compliance/skills/architecture-review/SKILL.md` | rewritten (§4.7) |
| `plugins/arch-compliance/skills/architecture-review/rules/` (new) | twelve rule prompts and `_contract.md` |
| `plugins/arch-compliance/skills/architecture-review/auditors/` | deleted (four files, superseded by `rules/`) |
| `plugins/arch-compliance/skills/acf-mandate/SKILL.md` | anchor check over the doctrine set (§4.6) |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md` | writes `review.yml` |
| `plugins/arch-compliance/profiles/react-app/mandates.yml`, `profiles/python-service/mandates.yml` | `auditor` values are rule ids (§4.10) |
| `plugins/arch-compliance/tests/test_adr_skill_prose.py` | the forbidden-vocabulary check covers `architecture-review` |
| `config/architecture/ARCHITECTURE.md` | `## React boundaries` names the `ui-logic-isolation` rule; `## Prose names no host` lists the new coverage |
| `README.md` | 0.3.0 upgrade note: `review.yml` is required; `auditor` values are rule ids |
| `pyproject.toml:3`, `plugins/arch-compliance/.claude-plugin/plugin.json:3` | `0.2.5` → `0.3.0` |

---

## 7. Tests

- `test_review_rules.py`: every `RULES` key has a prompt file and every prompt file a key; each settings model refuses an unknown key; a row naming an unknown rule raises `UnknownMandateError`.
- `test_review_packs.py`: each shipped pack loads; hint keys are rule ids; patterns compile; an add-on without its base is refused; a `detectors` key is refused.
- `test_review_host.py`: a missing field, an extra field and a missing file each fail loud.
- `test_review_doctrine.py`: section bounds by heading level; zero or two matches fail loud; `missing_anchors` over two texts.
- `test_review_prepass.py`: candidates per pack and surface; `surface_exclude` applies; a rule with no hints yields no candidates and no error.
- `test_review_aggregator.py`: payload parsing ported from `hm:tests/test_arch_review_aggregator.py`; a finding whose `mandate_id` is not among the group's rows is a contract violation; the report does not overwrite.
- `test_baseline.py`: prefix subsystems, longest wins; empty list keeps first-segment behaviour.
- Prose: no rule prompt or skill file contains the forbidden origin vocabulary.

---

## 8. Risks

| Risk | Handling |
|---|---|
| Generic prompts lose precision the origin auditors' hard-coded lists gave | Settings carry the lists; acceptance compares finding counts per rule on the origin repository before and after (§9). |
| `presentation-as-data` assumes a style schema with element and variant keys | The keys are settings; a repository without such a schema does not enable the rule. |
| Svelte and SQL hints are regular expressions over raw text | They seed candidates; the auditor decides. |
| A repository sets `params.review` keys a later detector also wants | Detector settings live outside `params.review` (decision 8). |

---

## 9. Acceptance

1. Suite and diff gate pass in this repository.
2. On the origin repository's cutover branch, `/arch-compliance:architecture-review` runs end to end; per rule, its finding count is compared with the last origin report, and differences are listed in the cutover PR.
3. A scratch repository with only `typescript` and `svelte` packs and one `ui-logic-isolation` row runs end to end with no origin path anywhere.

---

## 10. Follow-ups

- Part two: the origin repository's detectors, guards and judge onto `acf-check-diff`, including the pack `detectors` slot and Svelte script extraction.
- Phase 1e: Cayenne installs the plugin.
