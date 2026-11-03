# The Plugin as a Host of Its Own Gate

**Status:** v3 — 2026-11-02, approved by user; cleared acceptance run (§6).
**Adversarial review:** v3 — 2026-11-02, 4 reviewers, CLEARED (repo @ 2254c9c56ee27c8b5ff56aeb29368b54ddc0d960)
**Repo:** `IanDBallard/arch-compliance-for-superpowers`, `main` at `c0281bf`; the design is
implemented on branch `feat/self-host`.
**Workstream:** HistoricMansions workstream E, portable governance. Proposed phase number: **1e**
(the second-repository run currently called 1e becomes 1f when this spec's roadmap row lands; see §10).

## 0. Citation convention

Unprefixed paths are this repository on branch `feat/self-host`, which carries this
design's implementation; a path that `main` at `c0281bf` lacks is one this design creates
(§4.2). A statement about `main` before this design says "at `c0281bf`", and its
appendix command reads that commit with `git show c0281bf:<path>`. Paths prefixed `hm:`
are `HistoricMansionsV3` at `22eae4f9` (`main`).

The gate's citation resolver has no notion of another repository: a prefixed path
classifies as `unresolved` (`resolve_citation`, `plugins/arch-compliance/python/acf/adr/citations.py:129`,
tests `proposed`, absolute, escaping, existing, suffix, ignored, historical, then gives
up), and an unresolved citation is a hard fail before dispatch
(`plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:76-82,101`). HM's
host-contract runs handled their `acf:` citations by precedent: the controller mapped each
prefixed path to the sibling checkout and the reviewers opened the files there
(`hm:docs/reviews/adr_runs/ADR_GATE_HOST_CONTRACT_v3_2026-10-12.md:28,35,247`). The
acceptance run of this spec (§6) follows that precedent: before classification the
controller rewrites `hm:` to `C:/Users/iball/Arduino/Projects/HistoricMansions/`, hands
reviewers the mapped paths, and counts them as cited files. Unprefixed citations in
this spec use repository-relative paths (`hm:` citations use HM-relative paths) without
`...` ellipses or bare `:line` continuations, because the resolver's suffix match works on
whole path components (`plugins/arch-compliance/python/acf/adr/citations.py:32-44`) and an
ellipsis resolves to nothing.

Independently of that mapping, **each rule this spec lifts from another repository (§5.2 lists the eight lifted clauses) is
quoted in the doctrine, not only pointed to**, so the doctrine reads on its own and a
reviewer on a node without the sibling checkout can still verify it.

## 1. Goal

This repository runs the plugin's own adversarial-design-review gate on its own specs, under
its own declared configuration and its own written doctrine, so that a spec about the
plugin is reviewed and recorded where the files it changes live.

Today a spec about the plugin or its extracted architecture-compliance framework is written
in HM's `docs/design/`, reviewed by HM's gate against HM's doctrine, and recorded in HM's
ledger. Twelve specs in `hm:docs/design/` have the ADR gate or ACF as their subject (seven
post-plugin `ADR_*.md` specs and five pre-extraction HM origin specs; per-spec ledger rows
and executed census recipe in §10 and the appendix). That is the same split for prose and
review that phases 1b-1d remove for code.

## 2. Decisions this design records

Inputs, not tree-derivable claims:

1. **A spec lives in the repository whose files its change surface names.** A mixed spec
   splits along that line: a plugin-side spec here and a host-side adoption spec or plan
   there, instead of one HM spec carrying a plugin PR inside a task as 1c did. (user, 2026-10-22)
2. **The plugin's doctrine is proposed by this spec.** There is no written doctrine for
   this repository at `c0281bf` (§4.1 item 1). The doctrine lifts the eight general clauses
   listed in §5.2 from HM's `hm:GEMINI.md` and combines them with nine sections from this
   plugin's own review record. (user, 2026-10-22)
3. **Post-merge-housekeeping is extracted to the plugin in its own spec, after this one.**
   It is not in scope here. HM's workstream exit criterion 6, which records the skill as
   "HM-local by decision", is revised by that spec, not this one. (user, 2026-10-22)
4. **Phase 1d stays frozen at its merged text.** The `hm:GEMINI.md:61` sentence ("append
   the superseding ledger amendment") that conflicts with the plugin's verification-pass
   rule is corrected by the housekeeping spec, which rewrites that item anyway. (author's
   call, user accepted)
5. **Acceptance is a live gate run on this spec from this repository, and its verdict
   binds** (§6). 1d's acceptance accepted any outcome because it proved plumbing; here the
   plumbing and the review are the same run. (author's call)
6. **The host-contract spec moves here in this phase**, as its own decision 6 schedules
   (`hm:docs/design/ADR_GATE_HOST_CONTRACT.md:80-81`: "This spec stays in this repository
   until 1d, and moves to the plugin repository after 1d's acceptance run."). Its ledger
   rows stay in HM (§3).
7. **Bootstrap through `/acf-setup`, not by hand.** The plugin's own setup skill writes the
   mandate registry and doctrine pair for a host (`README.md:20`: "run `/acf-setup` (writes
   `config/architecture/` and `.acf/enabled`)"); this repository is a host and uses it. The
   declaration `config/architecture/adr.yml` is not written by the skill and is authored
   by hand (§5.1). (author's call)
8. **A generic check lives in the package; a host test keeps only its host's policy.**
   `MandateRegistry` refuses a repeated mandate id during model validation,
   `acf.registry.missing_anchors` is the one anchor-in-doctrine check, and
   `acf.cli_check_diff.KNOWN_DETECTORS` is the one detector-id union; this repository's
   tests and the `/acf-mandate` skill consume them (§5.5). Two existing skill-prose breaches
   in `/architecture-review` and `/acf-setup` are recorded in the doctrine and filed as §9
   follow-up 4 under `## Scoped refactor`. (author's call)

## 3. Non-goals

- No change to the persisted ledger format, `LedgerRow`, `LedgerAmendment` or the
  `TouchedSurface` vocabulary. The ledger-schema redesign stays a filed follow-up.
- No ledger migration. HM's records for plugin-related specs stay in HM, matched to their
  HM spec paths; the ledger is append-only. A moved spec leaves a stub at its HM path
  naming its new home, so a reader following a row's `spec_path` finds it.
- No new detector and no change to a detector's logic. No `architecture-review`
  movement; phase 2 stays blocked on the extension point.
- No loader validation of a `detection: manual` row's `detector` string: the registry
  contract leaves it free text (§5.5). This repository's own policy for its manual rows
  is a host test.
- No housekeeping extraction (decision 3). No Cayenne change.
- No Cursor twin and no dual-tree identity test: this repository ships one tree.
- No fix to the undeclared text decoding of three subprocess calls (§4.1 item 7) and no
  rewrite of the `/acf-setup` or `/architecture-review` skill prose (§4.1 item 4, §5.2).
  Both are filed (§9): this spec's theme is declaration, doctrine and the checks they rest on.

## 4. What this touches

### 4.1 Census (2026-10-24, updated 2026-11-02; commands in the appendix)

1. At `c0281bf`, `config/architecture/` is absent and `.acf/` is ignored (`.gitignore:8`).
   The root documents are `README.md` and `SECURITY.md`; there is no `CLAUDE.md`.
2. At `c0281bf`, `docs/design/` holds `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md` and
   this spec; `docs/reviews/` is absent.
3. The host contract reads two declared values and the doctrine path
   (`plugins/arch-compliance/python/acf/adr/host.py:19-33`); the compliance reviewer reads
   the doctrine and each document it points to
   (`plugins/arch-compliance/skills/adversarial-design-review/reviewers/compliance.md:12`)
   and checks a doctrine's self-declared high-frequency misses first
   (`plugins/arch-compliance/skills/adversarial-design-review/reviewers/compliance.md:47`).
4. `/acf-setup` writes `config/architecture/mandates.yml` and
   `config/architecture/ARCHITECTURE.md` from a profile, merging both profiles for a
   two-language host (`plugins/arch-compliance/skills/acf-setup/SKILL.md:90-118`). Its merge
   rule reads: "Keep every mandate `id` unique. If the same `id` appears in both (should not
   for stock profiles), stop and ask; never silently drop a row."
   (`plugins/arch-compliance/skills/acf-setup/SKILL.md:110`). Both stock profiles carry
   `ops.no-build-artifacts` with identical bodies
   (`plugins/arch-compliance/profiles/python-service/mandates.yml:34`,
   `plugins/arch-compliance/profiles/react-app/mandates.yml:23`), so the parenthetical is
   false and a polyglot bootstrap reaches the stop-and-ask. Language detection: Python is
   detected through `pyproject.toml`; because there is no root `package.json` and the
   TypeScript detector bridge is a three-file package under
   `plugins/arch-compliance/detectors/typescript/package.json`, `/acf-setup`'s "(or a clear
   app package)" and "substantial tree" clauses
   (`plugins/arch-compliance/skills/acf-setup/SKILL.md:53-55`) may report Python only, so
   the user supplies `both` at the language prompt (`docs/plans/PLAN_PLUGIN_SELF_HOSTING.md:78`).
5. The merged host registry, run over this repository's history at the base
   (`--base dfff93f5`, the root commit) with the code at `c0281bf`, reports seven
   findings, listed one per row with their disposition in §5.4.
6. The registry schema accepts `detection: manual` rows and requires a `detector` string on
   every row, but checks that string against known detectors only for `ast` and `guard`
   rows (`plugins/arch-compliance/python/acf/registry.py:9,19,56`). At `c0281bf`,
   `MandateRegistry.by_id` builds a dict over the rows and keeps the last of two rows with
   one id (`git show c0281bf:plugins/arch-compliance/python/acf/registry.py`, lines 33-34),
   and the loader does not refuse the repeat (appendix).
7. Three subprocess calls in the package decode their output with the locale codec
   (`text=True`, no `encoding`): `plugins/arch-compliance/python/acf/diff.py:24-30`,
   `plugins/arch-compliance/python/acf/adr/citations.py:62-65` and
   `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:49-56`. On a Windows
   node with a cp1252 locale the first raises inside the reader thread on a diff holding a
   character outside cp1252, which this repository's skill prose contains. CI runs on
   Linux (`.github/workflows/ci.yml:11`).
8. At `c0281bf` CI runs `pytest` and the TypeScript self-test, and not the diff gate.
9. The plugin's acceptance test for a non-origin host builds a fixture host in a temporary
   directory and exercises the storage path through the Python API
   (`plugins/arch-compliance/tests/test_adr_host_acceptance.py:74`). A live skill run from
   the installed plugin has not happened outside HM.
10. HM's exit criterion 5 names Cayenne as the second repository
    (`hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:5405-5406`) and says
    "Item 5 is the one that proves the objective rather than approximating it"
    (`hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:5410`).
11. The plugin's hooks run on each subagent start and each Write/Edit/MultiEdit in a
    repository where the plugin is installed (`plugins/arch-compliance/hooks/hooks.json`),
    and no-op without `.acf/enabled` (`plugins/arch-compliance/hooks/posttooluse_gate.py:72-81`,
    `plugins/arch-compliance/hooks/inject_constraints.py:71-80`). With the marker:
    SubagentStart injects the registry's rows and a doctrine excerpt into the subagent's
    context (`plugins/arch-compliance/hooks/inject_constraints.py:153`); PostToolUse runs
    the build-artifact path guard on edited paths
    (`plugins/arch-compliance/hooks/posttooluse_gate.py:284-294`) and scans the whole edited
    `.py`, `.ts` or `.tsx` file, not its changed lines (`added_lines=None` at
    `plugins/arch-compliance/hooks/posttooluse_gate.py:254,281`), and on a BLOCK finding
    exits 2, which returns the findings to the session as blocking feedback after the write
    (`plugins/arch-compliance/hooks/posttooluse_gate.py:131-134`).
12. At `c0281bf`, 404 tests are collected from the single `testpaths` entry
    `plugins/arch-compliance/tests` (`pyproject.toml`), and the plugin version is `0.2.0`.
13. Start condition (§5.7 step 1) is met: HM merged 1d on 2026-10-23 (`812f9c2b`); the
    plugin is installed on this node at user scope from the clone at `c0281bf`, version
    `0.2.0`, and its two gate skills are byte-identical to the clone
    (`scripts/check_installed_skills.py`).
14. At `c0281bf` the `/acf-mandate` validation snippet builds its detector union from
    `PYTHON_DETECTOR_IDS`, which equals `PYTHON_AST_DETECTOR_IDS`
    (`git show c0281bf:plugins/arch-compliance/python/acf/detectors/python_pack.py`, line 25),
    so it raises `UnknownDetectorError` on a stock profile's enforced guard row
    `ops.no-build-artifacts`. It also asks the agent to check anchors by eye: "Also verify
    each `arch_anchor` is a substring of `config/architecture/ARCHITECTURE.md`"
    (`git show c0281bf:plugins/arch-compliance/skills/acf-mandate/SKILL.md`, line 104).
    Two other skill lines carry the same class of breach:
    `plugins/arch-compliance/skills/architecture-review/SKILL.md:62` spells
    `Path("config/architecture/mandates.yml")` instead of `acf.repo.MANDATES_REL`, and
    `plugins/arch-compliance/skills/acf-setup/SKILL.md:137` instructs a by-eye anchor check
    ("Quickly confirm every `arch_anchor` in `config/architecture/mandates.yml` exists in
    `ARCHITECTURE.md`").
15. At `c0281bf` the detector-id union is spelled in
    `plugins/arch-compliance/python/acf/cli_check_diff.py:25` and in
    `plugins/arch-compliance/tests/test_profile_drift.py`, and the anchor check is a loop in
    `plugins/arch-compliance/tests/test_profile_drift.py`; the package has no anchor-check
    function (`git grep -n "arch_anchor" c0281bf -- plugins/arch-compliance/python` matches
    only the field declaration in `plugins/arch-compliance/python/acf/registry.py:23` and the
    prompt template key in `plugins/arch-compliance/python/acf/judge.py:154`).

### 4.2 Disposition

| Path | Change | Why |
|---|---|---|
| `config/architecture/adr.yml` | Create by hand (§5.1) | The two host values the gate cannot derive |
| `config/architecture/mandates.yml` | Create via `/acf-setup`, then extend (§5.2) | The registry is the spine; the plugin's own rules become rows |
| `config/architecture/ARCHITECTURE.md` | Create via `/acf-setup`, then extend (§5.2) | The doctrine the compliance reviewer reads |
| `.acf/enabled` | Written by `/acf-setup`, per developer, ignored | Turns the hooks on here (§5.4) |
| `CLAUDE.md` | Create (§5.3) | Session process |
| `README.md` | Add one paragraph | Says this repository is a host of its own gate and where its records are |
| `scripts/check_installed_skills.py` | Create (§5.3) | The pre-gate byte check of the installed gate skills |
| `tests/test_check_installed_skills.py` | Create (§5.3) | Pins that script (imports `GATE_SKILLS` from the script) |
| `tests/test_self_host.py` | Create (§5.5) | This host's policy: its declared values, its anchors, its manual rows |
| `pyproject.toml` | `testpaths` gains `tests`; version `0.2.1`; update `tests/test_packaging.py` comment path | Root tests are a property of this repository, not of the shipped plugin tree (`README.md:93-95` keeps host-property tests out of it); version per `## Release discipline` |
| `plugins/arch-compliance/.claude-plugin/plugin.json` | Version `0.2.1` | A skill's prose changes (`/acf-mandate`) |
| `plugins/arch-compliance/python/acf/registry.py` | Refuse a repeated id on `MandateRegistry`; add line-exact `missing_anchors` (§5.5) | Decision 8 |
| `plugins/arch-compliance/python/acf/detectors/python_pack.py`, `plugins/arch-compliance/python/acf/detectors/__init__.py` | Remove unused `PYTHON_DETECTOR_IDS` alias (§5.5) | `## No shims` / `## Live consumers`: zero callers after `/acf-mandate` imports `KNOWN_DETECTORS` |
| `plugins/arch-compliance/tests/test_registry.py` | Two tests (§5.5) | Pin the repeated-id refusal and the line-exact `missing_anchors` function |
| `plugins/arch-compliance/tests/test_profile_drift.py` | Consume `missing_anchors` and `KNOWN_DETECTORS` (§5.5) | Decision 8 |
| `plugins/arch-compliance/skills/acf-mandate/SKILL.md` | Validation snippet consumes the package (§5.5) | Decision 8; §4.1 item 14 |
| `plugins/arch-compliance/tests/test_acf_mandate_skill.py` | Create (§5.5) | Runs that snippet as written against a stock-profile host |
| `plugins/arch-compliance/tests/fixtures/python/bad_except.py`, `plugins/arch-compliance/tests/fixtures/typescript/bad.tsx` | Row exemption token with a reason on the flagged line (§5.4) | The two BLOCK findings of §4.1 item 5 |
| `.github/workflows/ci.yml` | Full-history checkout; one step (§5.6) | `acf-check-diff --base` on this repository's own changes |
| `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md` | Reconcile `detector` table cell and error bullet with `manual` rows (§5.5) | Matches `plugins/arch-compliance/python/acf/registry.py:56` |
| `docs/design/ADR_GATE_HOST_CONTRACT.md` | Create, copied from `hm:docs/design/ADR_GATE_HOST_CONTRACT.md` with a provenance block | Decision 6 |
| `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` | This spec | |
| `docs/plans/PLAN_PLUGIN_SELF_HOSTING.md` | Follows this spec | The plan argues from the spec |
| `docs/reviews/adr_runs/`, `docs/reviews/adversarial_design_ledger.jsonl` | Written by gate runs and their response records (§6) | Records |
| `hm:docs/design/ADR_GATE_HOST_CONTRACT.md` | Replace body with a stub naming the new path (HM, docs-only) | §3 |
| `hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md` | Workstream E rows (§10) (HM, docs-only) | The roadmap is HM's scheduling surface |

## 5. Design

### 5.1 The declaration

`config/architecture/adr.yml` is exactly:

```yaml
runs_dir: docs/reviews/adr_runs
ledger_path: docs/reviews/adversarial_design_ledger.jsonl
```

The same two names HM uses, so a reader of either repository finds the records in the same
place. No other key: `AdrHostConfig` is `extra="forbid"` (`plugins/arch-compliance/python/acf/adr/host.py:22`).

### 5.2 The doctrine

`/acf-setup` is run from the repository root with both languages (the user supplies `both`
at the language prompt, §4.1 item 4) and one merged pair. At the duplicate-id stop of §4.1
item 4 the answer is "keep one row": the two stock rows are identical and both already say
`languages: both`, so the merged file carries one `ops.no-build-artifacts` row. Both
answers are the user's, given in advance in the plan and recorded in its ledger; the skill
does not produce them. Every stock anchor survives verbatim (`## Fail loud`, `## No shims`,
`## POSIX paths`, `## Build artifacts`, `## Fail-loud ratchet`, `## Façade sinks`,
`## FSM transitions`, `## Soft fail-loud smells`, `## React boundaries`), matched against
stripped lines of `config/architecture/ARCHITECTURE.md` by `missing_anchors` (§5.5).

Three stock rows have no subject here and are `status: unenforced`, not deleted, so the
file stays diffable against the profiles: `facade.forbid-sink` and `fsm.transition-guard`
arrive unenforced from the python-service profile, and `soft.react-boundaries` is changed
from `partial` (no React app; the TypeScript here is a detector bridge). Each carries a
one-line comment with its reason.

The doctrine's opening paragraph states the population it governs: the package, the
hooks, the skill prose, the TypeScript bridge, the plugin's tests and fixtures, and the
repository-level `tests/`, `scripts/` and `config/`. The CI diff gate and the PostToolUse
hook run the registry's detectors on changed `.py`, `.ts` and `.tsx` files anywhere in the
repository; prose and configuration are held to the doctrine by review.

Then `config/architecture/ARCHITECTURE.md` gains the plugin's own sections. A section whose
rule an existing test enforces gets one or more `detection: manual` rows in
`config/architecture/mandates.yml` whose `detector` names that test module (§4.1 item 6);
each row is a pointer from the rule to its enforcement, and the doctrine section names the
row id, not the test path, so a renamed test is edited in one place. Five sections have
rows (six manual rows in total: `## Prose names no host` has two rows because two separate
test modules enforce its code and gate-skill halves). The other four plugin sections, and
the two lifted anchors below, end with "No row: no test enforces this yet."; a row is added
in the change that adds the test. The manual rows use `call_sites: [audit]` from the design
document's vocabulary (`docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:104`).

| Section | Rule | Source | Row |
|---|---|---|---|
| `## One base exception` | Each ACF exception subclasses `AcfError` and nothing else; no stdlib mixin. | 1b decision | `plugin.one-base-exception` (BLOCK) |
| `## One owner for host paths` | `acf.repo` is the one declaration of where ACF looks in a host and imports the standard library alone. Its row's test scans `plugins/arch-compliance/python/` and `plugins/arch-compliance/hooks/`; the root `tests/` and `scripts/` import the `acf.repo` constants, checked by review. Current breach in an executable skill snippet recorded: `plugins/arch-compliance/skills/architecture-review/SKILL.md:62` (§9 follow-up 4). | `plugins/arch-compliance/python/acf/repo.py:1-6` | `plugin.one-owner-host-paths` (WARN) |
| `## Declared, never defaulted` | The gate's host values are declared in `config/architecture/adr.yml`; no default stands in for a missing declaration. Scope stated: two package defaults outside it are named (`plugins/arch-compliance/python/acf/repo.py:23-26`, `plugins/arch-compliance/python/acf/repo.py:32-44`). | 1c decision 4; `plugins/arch-compliance/python/acf/adr/host.py:19-33` | `plugin.declared-never-defaulted` (BLOCK) |
| `## Prose names no host` | Skill prose and runtime messages name no host repository, path or section. The two rows cover the gate's package/runtime messages and the two gate skills' prose; the other three skills in `plugins/arch-compliance/skills/` have no row yet. | `plugins/arch-compliance/tests/test_adr_code_portability.py`, `plugins/arch-compliance/tests/test_adr_skill_prose.py` | `plugin.adr-code-names-no-host` (WARN), `plugin.gate-prose-names-no-host` (WARN) |
| `## Frozen ledger format` | A `LedgerRow` or `LedgerAmendment` field changes only through a spec and a gate run. A verification pass writes no ledger record; the spec header line is its record. | `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:443-452` | `plugin.frozen-ledger-format` (BLOCK) |
| `## Live consumers` | An export has a live call site in the package, a hook or a skill. A test is not a consumer. | Reviewer ruling on `run_git`, plugin PR #9 | none |
| `## No completeness claims` | A factual claim about the tree is not load-bearing on a universal quantifier unless a re-runnable recipe backs it; a normative rule states a requirement, and its row's test is its recipe. | `plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:152` (type T3, quoted) | none |
| `## Declared text decoding` | A subprocess call in the package or hooks that reads text declares `encoding="utf-8"`. Three breaches recorded with their recipe (§4.1 item 7); the plugin's tests are outside the scope. | §4.1 item 7 | none |
| `## Release discipline` | A skill prose change bumps the version; the two gate skills are byte-checked before a gate run. The check does not cover the installed copy's hooks and package code, which the hooks run (`plugins/arch-compliance/hooks/posttooluse_gate.py:22-26`). | 1d risk table, `hm:docs/design/ADR_GATE_HM_CUTOVER.md:264`; 1d plan Task 8 step 1 | none |

The eight lifted HM clauses are quoted under the anchors they belong to, with their
attribution, so the reviewer reads them here (lines at `hm:` `22eae4f9`). Under
`## Fail loud`: "Never use bare `except:` blocks. Raise custom descriptive exceptions
immediately when data or dependencies are missing" (`hm:GEMINI.md:103`); "No 'defaulting'
to None to avoid a crash" (`hm:GEMINI.md:104`); "`hasattr()`-based interface probing and
silent degradation … are shims" (`hm:GEMINI.md:105`). Under `## No shims`: "Temporary
'bridge' code, compatibility shims, or 'just-in-case' logic to mask architectural
misalignments are forbidden" (`hm:GEMINI.md:111`). Under a new
`## Single point of definition`: "When the same operation, constant set, or decision
procedure … is needed by more than one module, it must have exactly one canonical
implementation that every call site consumes" (`hm:GEMINI.md:136`), with the two git
runners (`plugins/arch-compliance/python/acf/diff.py:17`,
`plugins/arch-compliance/python/acf/adr/citations.py:54`) and the two skill-prose breaches
(`plugins/arch-compliance/skills/architecture-review/SKILL.md:62`,
`plugins/arch-compliance/skills/acf-setup/SKILL.md:137`) recorded beside it as current
breaches (§9 follow-ups 1 and 4). Under `## POSIX paths`: "Path strings persisted to YAML
or JSON must use POSIX format" (`hm:GEMINI.md:189`); "`Path.as_posix()` alone is not
sufficient … normalization is a string-level substitution" (`hm:GEMINI.md:191`), with the
note that the plugin refuses a backslash rather than normalizing it (`PosixStr`,
`plugins/arch-compliance/python/acf/adr/contract.py:129`). Under `## Scoped refactor`:
"Within an approved plan or ticket, remove legacy dependencies or non-contractual
patterns in code paths you are changing. Do not expand scope to unrelated modules"
(`hm:GEMINI.md:129`).

Other HM `hm:GEMINI.md` sections (§1 workflow, §2 git/worktrees, §5 HFSM, §6 UI isolation,
§7 dead-code/pass-through/test-colocation sub-bullets, §8 config & secrets, §9 logging, §10
book-root resolution, §11 metadata façade, §12/§13 content pipeline) are either HM-domain
rules or session workflow and are not lifted into `config/architecture/ARCHITECTURE.md`.

The doctrine ends with `## High-frequency misses`, which the compliance reviewer checks
first: a completeness claim with no recipe behind it; a default that re-enters for a
declared value; a host name in prose; a stdlib mixin on an exception; a subprocess text
call without an encoding; a check re-implemented in a test or a skill instead of consumed
from the package.

The plugin's existing design document keeps its five governing principles
(`docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51`); `config/architecture/ARCHITECTURE.md`
points to them and does not restate them.

### 5.3 Session process (`CLAUDE.md`) and the byte check

A short file, pointing at the doctrine and recording what Superpowers' defaults do not
know about this repository, in the form HM's `CLAUDE.md` uses (`hm:CLAUDE.md:21-35`):

- Specs at `docs/design/<TOPIC>.md`, plans at `docs/plans/PLAN_<TOPIC>.md`.
- Brainstorming's terminal state is `/arch-compliance:adversarial-design-review <spec>`
  then `writing-plans`; `BLOCKED` returns to the spec through
  `arch-compliance:responding-to-adversarial-review`; re-run scope follows the revision
  class as the gate skill states it.
- Before a gate run: the command `python scripts/check_installed_skills.py <INSTALL_PATH>`;
  the rule and the mismatch procedure live in the doctrine's `## Release discipline`,
  which `CLAUDE.md` points to rather than restates.
- Citation convention for specs here: unprefixed paths are this repository; another
  repository is cited with a prefix for the reader and its rule is quoted, as §0 says.
- Windows note until §9 follow-up 1 lands: run the diff gate with `PYTHONUTF8=1`.

`scripts/check_installed_skills.py` takes the installed plugin's directory, compares each
file under the clone's two gate-skill trees (`GATE_SKILLS`) with the file at the same
relative path under `<INSTALL_PATH>/skills/` (`filecmp.cmp(..., shallow=False)`), prints
`installed gate skills identical to the clone` and exits 0, or prints each differing or
missing path and exits 1. It is the 1d plan's inline block
(`hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:669-681`) made a script with the clone as a
parameter; that block is an executed plan record and stays. HM's live install
instruction (`hm:CLAUDE.md:17`) could call this script from the clone; that is HM's change
surface (decision 1) and is filed (§10). `tests/test_check_installed_skills.py` imports
`GATE_SKILLS` from the script and pins three cases: identical trees, one changed byte, one
missing installed file.

### 5.4 Installation and the hooks

The plugin is installed on the developer's node from this clone (§4.1 item 13); this spec
adds no install step. `/acf-setup` writes `.acf/enabled`, and the marker turns on both
hooks for this repository (§4.1 item 11):

- **SubagentStart** injects the registry's rows and the first part of the doctrine into
  each subagent started here, the gate's reviewers included. The injected text is the
  doctrine and the registry, which the compliance reviewer reads anyway; it carries no
  review verdict (`_render_constraints` renders the rows and the excerpt alone,
  `plugins/arch-compliance/hooks/inject_constraints.py:153-176`), so with respect to
  hook-injected context reviewers stay blind to each other and to prior verdicts.
- **PostToolUse** checks edited paths against the build-artifact path guard
  (`plugins/arch-compliance/hooks/posttooluse_gate.py:284-294`) and scans each edited `.py`,
  `.ts` or `.tsx` file whole (`added_lines=None` at
  `plugins/arch-compliance/hooks/posttooluse_gate.py:254,281`). A WARN finding is returned
  as context and the hook exits 0. A BLOCK finding exits 2 and returns the findings to the
  session as blocking feedback; the write has already happened.

Because the AST scan is whole-file, a finding already in a file returns on any edit to that
file. The census of §4.1 item 5 is the population this concerns; each finding has a
disposition:

| Finding at the base | Severity | Disposition |
|---|---|---|
| `plugins/arch-compliance/tests/fixtures/python/bad_except.py:4` `fail-loud.bare-except` | BLOCK | The fixture exists to contain the pattern. The line carries `# fail-loud.bare-except-ok: <reason>`; the registry layer honours the token (`plugins/arch-compliance/python/acf/enforcement.py:50`), and the detector test calls the scanner directly, which still flags the line. |
| `plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:4` `fail-loud.empty-catch` | BLOCK | Same, with `// fail-loud.empty-catch-ok: <reason>`; the TypeScript self-test still counts three findings in the file. |
| `plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:7`, `plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:8` `no-shims.explicit-any` | WARN | Context only; the fixture must contain `any`. |
| `plugins/arch-compliance/tests/test_adr_exceptions.py:22` `no-shims.hasattr` | WARN | Context only; the test asserts that a name exists on a module. |
| `plugins/arch-compliance/tests/test_adr_import_graph.py:46` `no-shims.hasattr` | WARN | Context only; the test asserts a module's public surface. |
| `plugins/arch-compliance/tests/test_adr_skill_prose.py:53` `no-shims.hasattr` | WARN | Context only; the test asserts that an imported name exists. |

With the two tokens in place the same command reports the five WARN rows and exits 0
(appendix). A future BLOCK on a legitimate line takes its row's exemption token with a
reason, never a status flip (§9).

### 5.5 The package checks and the self-host test

Decision 8 puts each generic check in the package, with a live consumer outside the tests:

- **Repeated ids.** `MandateRegistry._unique_ids` (`@model_validator(mode="after")` at
  `plugins/arch-compliance/python/acf/registry.py:33-41`) raises `AcfInputError` naming each
  repeated id when `load_mandates` constructs `MandateRegistry`. Its callers are the diff
  CLI, the LLM CLI and both hooks. HM is not reached by the change: its
  `hm:config/architecture/mandates.yml` at `22eae4f9` is in HM's own schema (rows carry
  `gemini_anchor` and no `languages` or `arch_anchor`), so it does not load through
  `load_mandates`, and HM's tracked files name `acf.registry` and `acf-check-diff` only in
  design and review prose (appendix). Pinned by
  `test_a_repeated_mandate_id_is_refused` in `plugins/arch-compliance/tests/test_registry.py`.
- **Anchors.** `missing_anchors(registry, doctrine_text) -> list[str]`
  (`plugins/arch-compliance/python/acf/registry.py:67-70`) returns the ids whose
  `arch_anchor.strip()` is not in `{line.strip() for line in doctrine_text.splitlines()}`,
  so an inline backtick mention of a heading in prose cannot satisfy the check. Consumers:
  the `/acf-mandate` validation snippet (live),
  `plugins/arch-compliance/tests/test_profile_drift.py`, and `tests/test_self_host.py`.
  Pinned by `test_missing_anchors_names_rows_whose_anchor_is_absent` (which includes an
  inline backtick-quoted heading in the fixture doctrine).
- **Detector union.** `KNOWN_DETECTORS` stays where the diff CLI defines it
  (`plugins/arch-compliance/python/acf/cli_check_diff.py:25`), because `acf.registry`
  cannot import `acf.judge` (which imports `acf.registry`). The `/acf-mandate` snippet,
  the drift test and the host test import it, and the unused compatibility alias
  `PYTHON_DETECTOR_IDS` is removed from
  `plugins/arch-compliance/python/acf/detectors/python_pack.py` and
  `plugins/arch-compliance/python/acf/detectors/__init__.py`.
- **The `/acf-mandate` snippet** loads the registry with `KNOWN_DETECTORS`, prints the
  rows, and exits non-zero naming the rows whose anchor `missing_anchors` reports.
  `plugins/arch-compliance/tests/test_acf_mandate_skill.py` extracts the snippet from the
  skill and runs it against a host built from the python-service profile: it exits 0 on
  the stock pair and non-zero, naming `fail-loud.bare-except`, when `## Fail loud` is
  renamed.

`tests/test_self_host.py` at the repository root, collected through the added
`testpaths` entry, imports `ARCH_REL` and `MANDATES_REL` from `acf.repo` and the checks
above, and keeps this host's policy in three tests:

1. `test_declaration_names_the_reviews_tree`: `config/architecture/adr.yml` loads through
   `load_host_config` and declares the two paths of §5.1.
2. `test_every_anchor_is_in_the_doctrine`: `missing_anchors` over this host's pair is empty.
3. `test_every_manual_row_names_an_existing_test_module`: this host's registry has manual
   rows, and each one's `detector` is an existing file under `plugins/arch-compliance/tests/`.

The third test stays in the host because it is this host's policy, not the registry's
contract: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:102,184` defines `detector` as
"Detector fn / guard module / LLM prompt id / manual verification pointer" and scopes
unknown-detector validation to enforced `ast` and `guard` rows, and the `/acf-mandate`
skill tells a `manual` row's author to "Document how humans or external tools satisfy the
mandate" (`plugins/arch-compliance/skills/acf-mandate/SKILL.md:122`). A loader rule
"a manual detector is a file" would bind every host to this one's convention (§3).

### 5.6 CI

The checkout fetches full history (`fetch-depth: 0`) and one step runs after `pytest`
in `.github/workflows/ci.yml`:
`python -m acf.cli_check_diff --repo . --base "origin/${{ github.base_ref || 'main' }}"`
with the host registry. On a `pull_request` event it diffs the branch against its
merge-base with the base branch and fails the job on a BLOCK finding on an added line. On
a `push` to `main` the base is `main` itself; `--base` diffs the merge-base three-dot
range (`plugins/arch-compliance/python/acf/diff.py:42-45`), which is empty, and the step reports
nothing; pull requests are where it gates.

### 5.7 Sequencing

1. **Start condition:** 1d has merged in HM, the plugin is installed on the node from this
   clone, and the installed gate skills match the clone (§4.1 item 13). Met.
2. Branch `feat/self-host` from `main` at `c0281bf`, in its own worktree.
3. §5.1–§5.6, the host-contract spec copy, the README paragraph.
4. Byte check, then the acceptance run (§6) on this spec from the worktree root. Records
   committed on the branch.
5. PR, squash-merge.
6. HM: one docs-only commit with the stub and the roadmap rows (§10), through HM's normal
   flow.

## 6. Acceptance

From the branch's worktree, after step 3 of §5.7 and before merge: run
`/arch-compliance:adversarial-design-review docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md`.
The run must complete end to end through the installed plugin skill, write its run detail
under `docs/reviews/adr_runs/` and a row of `docs/reviews/adversarial_design_ledger.jsonl`,
and the row must be read back as the skill requires. **The verdict binds:** `BLOCKED`
returns to this spec through the responding skill, and the re-run scope follows the
revision class. A revision to a §5.2 or §5.5 rule is a mechanism revision and re-runs in
full, blind. The records are committed on the branch; `main` is untouched until the run
clears.

The compliance reviewer in that run reads the doctrine this spec creates. That is the
point: the doctrine's first test is whether four blind reviewers can hold this design to it.

## 7. Shape fit

**Extends:** the host contract as designed (one declaration file, the fixed doctrine path:
`docs/design/ADR_GATE_HOST_CONTRACT.md` §5), the `/acf-setup` bootstrap, and the
registry-is-the-spine principle (`docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:50`): the
plugin's own rules become registry rows with anchors, in the plugin's own format.

**Relationships, checked by behaviour (appendix recipes):**

| New element | Existing element with the same responsibility | Relationship |
|---|---|---|
| `tests/test_self_host.py` anchor test | `plugins/arch-compliance/tests/test_profile_drift.py` loop at `c0281bf`; `/acf-mandate` by-eye instruction at `c0281bf`; `plugins/arch-compliance/skills/acf-setup/SKILL.md:137` by-eye instruction | The two tests and `/acf-mandate` consume `missing_anchors`; `plugins/arch-compliance/skills/acf-setup/SKILL.md:137` is recorded as a current breach in the doctrine and filed (§9 follow-up 4) |
| `tests/test_self_host.py` detector union | `plugins/arch-compliance/python/acf/cli_check_diff.py:25`; the drift test's copy at `c0281bf`; the `/acf-mandate` snippet's narrower union at `c0281bf` | All three import `KNOWN_DETECTORS`; one definition; unused `PYTHON_DETECTOR_IDS` removed |
| Repeated-id check | `MandateRegistry.by_id` (silent last-wins at `c0281bf`); `/acf-setup` prose (`plugins/arch-compliance/skills/acf-setup/SKILL.md:110`) | `MandateRegistry._unique_ids` refuses at model validation; the prose stays and its false parenthetical is filed (§9 follow-up 4) |
| Manual-row detector check | `load_mandates`'s `ast`/`guard` branch (`plugins/arch-compliance/python/acf/registry.py:60`) | Adjacent, not merged: host policy, not registry contract (§5.5) |
| Host config paths in `tests/test_self_host.py` and `/acf-mandate` | `acf.repo` (`plugins/arch-compliance/python/acf/repo.py:12-21`); `plugins/arch-compliance/skills/architecture-review/SKILL.md:62` literal path | `tests/test_self_host.py` and `/acf-mandate` import `acf.repo`; `plugins/arch-compliance/skills/architecture-review/SKILL.md:62` is recorded as a current breach in the doctrine and filed (§9 follow-up 4) |
| `scripts/check_installed_skills.py` | `hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:669-681` (executed record) | Same algorithm, now a reusable script; `tests/test_check_installed_skills.py` imports `GATE_SKILLS` from the script; the HM record stays |
| `CLAUDE.md` byte-check line | `## Release discipline` in the doctrine | `CLAUDE.md` carries the command and points to the rule |
| `docs/design/ADR_GATE_HOST_CONTRACT.md` | `hm:docs/design/ADR_GATE_HOST_CONTRACT.md` | Two full copies until §5.7 step 6 replaces HM's with a stub; the provenance block names the canonical one |

**Second way created:** none created by this design; the two pre-existing skill-prose
breaches (`plugins/arch-compliance/skills/architecture-review/SKILL.md:62` and
`plugins/arch-compliance/skills/acf-setup/SKILL.md:137`) are recorded in the table above
and in `config/architecture/ARCHITECTURE.md` and filed in §9 follow-up 4. The `CLAUDE.md`
is a pointer and process file of the kind HM already has, not a second doctrine. **Pattern
sweep:** specs in `hm:docs/design/` whose subject is the ADR gate or ACF: the twelve files
of §1 and §10 (executed census script in the appendix). One moves here
(`hm:docs/design/ADR_GATE_HOST_CONTRACT.md`); one is live on HM's change surface
(`hm:docs/design/ADR_GATE_HM_CUTOVER.md`) and stays; five post-plugin specs and five
pre-extraction HM origin specs stay in HM beside their ledger rows and git history, listed
in §10.

## 8. Definition of done

1. `python -m pytest -q` from the root passes, and `--collect-only` lists these tests:
   the three of `tests/test_self_host.py` (§5.5), the three of
   `tests/test_check_installed_skills.py` (§5.3), the two added to
   `plugins/arch-compliance/tests/test_registry.py`, and the two of
   `plugins/arch-compliance/tests/test_acf_mandate_skill.py`.
2. Deleting `config/architecture/adr.yml`, or removing any one of the 14 anchor headings from
   `config/architecture/ARCHITECTURE.md`, fails `tests/test_self_host.py`; a duplicated row in
   `config/architecture/mandates.yml` fails it through `MandateRegistry._unique_ids`; restoring
   passes.
3. `python -m acf.cli_check_diff --repo . --base origin/main` from the root, with
   `PYTHONUTF8=1` on Windows and the branch's package on the path, exits 0 on the branch;
   with `--base dfff93f5` it reports the five WARN rows of §5.4 and exits 0.
4. `npm test --prefix plugins/arch-compliance/detectors/typescript` prints
   `self-test OK: bad.tsx (3 findings)`.
5. `/acf-setup` was used for the bootstrap and its choices are recorded in the plan's
   ledger; each path in `git diff --stat main` has a row in §4.2.
6. The acceptance run of §6 cleared (`CLEARED` or `CLEARED_WITH_ABSORPTIONS`, absorptions
   folded in) and its run detail and ledger row are committed on the branch.
7. `docs/design/ADR_GATE_HOST_CONTRACT.md` exists here with a provenance block naming its
   HM origin and the HM commit it was copied at.
8. The CI step of §5.6 ran green on the PR.
9. The HM docs-only commit of §10 is merged, or its PR is open and linked from the plan.

## 9. Risks and filed follow-ups

| Risk | Mitigation |
|---|---|
| The installed plugin serves stale gate prose during the acceptance run | Byte check before the run (§5.3); reinstall on mismatch, as 1d does |
| The installed copy's hooks and package code lag the clone, and the hooks run them | Recorded in `## Release discipline`; follow-up 5 extends the byte check |
| A stock rule fires on plugin code during an edit | WARN returns context, not a block; a BLOCK on a legitimate line takes the row's exemption token with a reason, never a status flip (§5.4) |
| The repeated-id refusal breaks a host's registry on upgrade | This repository's registry has no repeated id (`tests/test_self_host.py` loads it); HM's registry is not read by `load_mandates` (§5.5); a host that carried a duplicate had a row silently shadowed, and the refusal names it |
| The doctrine's lifted rules drift from HM's `hm:GEMINI.md` | They are quoted with an attribution and a line at a named HM commit; drift is visible on either side and is not a defect, since the plugin's doctrine is its own |
| A spec here cites HM files the reviewers cannot open | §0: quote, never only point |

Filed follow-ups, each to a roadmap row in HM (the scheduling surface today) and, once the
housekeeping skill is extracted, to the plugin's own board:

1. **Text decoding and one git runner.** The three subprocess calls of §4.1 item 7 declare
   `encoding="utf-8"`, and the two git runners become one, which the 1a roadmap row
   already describes ("one git runner", `hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:5122`).
   One plan, no spec: a defect with a test.
2. **Post-merge-housekeeping extraction** (decision 3), the next spec. It also corrects
   `hm:GEMINI.md:61` and adds the row-identity rule for amendments after a verification
   pass or user override.
3. **Hook quiet flag** (`--quiet-disabled` in `plugins/arch-compliance/hooks/hooks.json`),
   already filed by 1d (`hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:213`).
4. **Skill prose alignment (`/acf-setup` and `/architecture-review`).**
   `plugins/arch-compliance/skills/acf-setup/SKILL.md:110` says a repeated id "should not"
   occur across stock profiles when both carry `ops.no-build-artifacts`;
   `plugins/arch-compliance/skills/acf-setup/SKILL.md:137` instructs a by-eye anchor check
   instead of `acf.registry.missing_anchors`; and
   `plugins/arch-compliance/skills/architecture-review/SKILL.md:62` spells
   `Path("config/architecture/mandates.yml")` instead of `acf.repo.MANDATES_REL`. Reconcile
   all three skill snippets.
5. **Byte check scope.** Extend `scripts/check_installed_skills.py` to the installed
   hooks and package code the hooks run, comparing the clone's tracked files under
   `plugins/arch-compliance/hooks/` and `plugins/arch-compliance/python/acf/`.

## 10. Roadmap effect (HM workstream E, docs-only)

- New row **1e**: this spec, with the plan's path and this repository's PR.
- The second-repository run becomes **1f**, and exit criterion 5 reads "a second
  repository can install the plugin and run the gate with its own declared configuration
  and no HM paths anywhere; the plugin repository is the first such host (1e), Cayenne the
  foreign-stack proof (1f)". Criterion 6 is left for the housekeeping spec.
- The 1c row records that `hm:docs/design/ADR_GATE_HOST_CONTRACT.md` moved here, with the
  stub's path.
- Priority-board rows for §9 follow-ups 1, 2, 4 and 5, and one for HM's install
  instruction calling `scripts/check_installed_skills.py` (§5.3).
- The twelve HM specs in `hm:docs/design/` whose subject is the ADR gate or ACF, with their
  HM ledger rows at `22eae4f9` (recipe in the appendix) and their disposition:

| HM spec | Ledger rows | Disposition |
|---|---|---|
| `hm:docs/design/ADR_GATE_HOST_CONTRACT.md` | 4 | Moves here (decision 6); HM keeps a stub |
| `hm:docs/design/ADR_GATE_HM_CUTOVER.md` | 6 | Stays: HM's change surface |
| `hm:docs/design/ADR_EXTRACTION_TO_PLUGIN.md` | 7 | Stays, superseded |
| `hm:docs/design/ADR_GATE_PLUGIN_COMPONENT.md` | 3 | Stays, v3, not re-dispatched |
| `hm:docs/design/ADR_GATE_HM_ADOPTION.md` | 0 | Stays, draft |
| `hm:docs/design/ADR_PER_FINDING_REVISION_CLASSING.md` | 0 | Stays, stub |
| `hm:docs/design/ADR_REVISION_EVIDENCE_AND_CARRYOVER_INSTRUMENTATION.md` | 4 | Stays, v4 draft |
| `hm:docs/design/ADVERSARIAL_DESIGN_REVIEW.md` | 0 | Stays, pre-extraction HM origin spec for the gate |
| `hm:docs/design/ARCHITECTURE_COMPLIANCE_FRAMEWORK.md` | 0 | Stays, pre-extraction HM origin spec for Tier 1 ACF |
| `hm:docs/design/ARCHITECTURE_COMPLIANCE_FRAMEWORK_TIER2_LLM_JUDGE.md` | 0 | Stays, pre-extraction HM origin spec for Tier 2 LLM judge |
| `hm:docs/design/ARCHITECTURE_COMPLIANCE_FRAMEWORK_TIER3_AUDIT.md` | 0 | Stays, pre-extraction HM origin spec for Tier 3 audit |
| `hm:docs/design/ARCH_COMPLIANCE_SHIFT_LEFT_GATING.md` | 0 | Stays, pre-extraction HM origin spec, superseded |

A future revival of a staying spec is authored here under decision 1.

## 11. Left to the builder

- The exact wording of each doctrine section and of the README paragraph, within §5.2's
  table and sources.
- Whether the TypeScript bridge's stock rows stay `enforced` given that `npm ci` is needed
  for the bridge; `unenforced` with a reason is acceptable.

## Appendix — premise verification (2026-10-24, updated 2026-11-02)

| Claim | Command | Result |
|---|---|---|
| No doctrine or declaration at the base | `git ls-tree --name-only c0281bf` and `git ls-tree c0281bf config` | root `.md`: `README.md`, `SECURITY.md`; no `config/` |
| 404 tests at the base | `git worktree add <tmp> c0281bf` then `python -m pytest --collect-only -q` | `404 tests collected` (the branch base's own baseline run: `404 passed`) |
| Seven findings under the host registry at the base code | in a detached worktree at `c0281bf` with `npm ci` in its TypeScript bridge and this branch's three `config/architecture/` files copied in: `PYTHONUTF8=1 PYTHONPATH=<worktree>/plugins/arch-compliance/python python -m acf.cli_check_diff --repo . --base dfff93f5 --json` | exit 1; 2 BLOCK (`plugins/arch-compliance/tests/fixtures/python/bad_except.py:4`, `plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:4`), 5 WARN (§5.4 table) |
| Five WARN and exit 0 after the tokens | `PYTHONUTF8=1 PYTHONPATH=plugins/arch-compliance/python python -m acf.cli_check_diff --repo . --base dfff93f5` | the five WARN rows of §5.4; exit 0 |
| Scanners still flag both fixture lines | `scan_python_file` on `plugins/arch-compliance/tests/fixtures/python/bad_except.py`; `scan_typescript_file` on `plugins/arch-compliance/tests/fixtures/typescript/bad.tsx` | `fail-loud.bare-except` line 4; `fail-loud.empty-catch` line 4, `no-shims.explicit-any` lines 7 and 8 |
| Three undeclared-decoding calls in the package | `git grep -n "text=True" -- plugins/arch-compliance/python plugins/arch-compliance/hooks` | `plugins/arch-compliance/python/acf/diff.py:28`, `plugins/arch-compliance/python/acf/adr/citations.py:64`, `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:53` |
| The base snippet rejects a guard row | the `/acf-mandate` snippet at `c0281bf` run against `config/architecture/mandates.yml` | `UnknownDetectorError: enforced mandate 'ops.no-build-artifacts' references unknown detector 'no_build_artifacts'` |
| Silent last-wins at the base | two rows with id `a` loaded by `load_mandates` at `c0281bf` | 2 rows loaded, `by_id` keeps 1 (the second) |
| HM's registry is outside `load_mandates` | `load_mandates(<hm>/config/architecture/mandates.yml)` with the branch's package; `yaml.safe_load` of the same file; `git -C <hm> grep -n -e 'acf\.registry' -e 'acf\.cli_check_diff' -e 'acf-check-diff'` | `AcfInputError` (rows lack `languages`, `arch_anchor`); 48 rows keyed with `gemini_anchor`, no repeated id; grep hits in `docs/design/` and `docs/reviews/` only |
| Detector-union spellings at the base | `git grep -n "KNOWN_DETECTORS =" c0281bf` and the snippet's `known =` line | `plugins/arch-compliance/python/acf/cli_check_diff.py:25`, `plugins/arch-compliance/tests/test_profile_drift.py:13`; snippet builds `PYTHON_DETECTOR_IDS \| TS_DETECTOR_IDS \| LLM_PROMPT_IDS` |
| No anchor-check function in the package at the base | `git grep -n "arch_anchor" c0281bf -- plugins/arch-compliance/python` | `c0281bf:plugins/arch-compliance/python/acf/registry.py:23` (field declaration) and `c0281bf:plugins/arch-compliance/python/acf/judge.py:154` (prompt template key); no function |
| Host-path and anchor-check spellings across `.py` and `SKILL.md` on the branch | `git grep -n -E "mandates\.yml|ARCHITECTURE\.md|adr\.yml|arch_anchor|missing_anchors" -- "*.py" "plugins/arch-compliance/skills/*/SKILL.md"` | package owner in `plugins/arch-compliance/python/acf/repo.py` and `plugins/arch-compliance/python/acf/registry.py`; consumers in `plugins/arch-compliance/skills/acf-mandate/SKILL.md:99`, `plugins/arch-compliance/tests/test_profile_drift.py:27`, `tests/test_self_host.py:34`; recorded skill-prose breaches in `plugins/arch-compliance/skills/architecture-review/SKILL.md:62` and `plugins/arch-compliance/skills/acf-setup/SKILL.md:137` |
| Dropping any of the 14 anchor headings fails `missing_anchors` | for each unique `m.arch_anchor` in `config/architecture/mandates.yml`, remove the matching line from `config/architecture/ARCHITECTURE.md` and assert `missing_anchors(reg, dropped) == [m.id for m in reg.mandates if m.arch_anchor == anchor]` | 14/14 unique anchors (across all 17 rows) return the expected missing row ids |
| Whole-file hook scan and build-artifact path guard | `git grep -n -E "added_lines=None|no_build_artifacts" -- plugins/arch-compliance/hooks/posttooluse_gate.py` | `added_lines=None` at lines 254, 281; `check_build_artifact_paths` at lines 284-294 |
| Hook exit 2 on BLOCK | `sed -n 131,134p plugins/arch-compliance/hooks/posttooluse_gate.py` | `return 2` with the blocking-feedback comment |
| Duplicate across stock profiles | `git grep -n "^- id: ops.no-build-artifacts" -- plugins/arch-compliance/profiles/` | `plugins/arch-compliance/profiles/python-service/mandates.yml:34`, `plugins/arch-compliance/profiles/react-app/mandates.yml:23` |
| HM 1d merged | `git -C <hm> log -1 --format=%h,%cd --date=short 812f9c2b` | `812f9c2b,2026-10-23` |
| HM specs whose subject is the ADR gate or ACF and their ledger rows | scan all 46 `hm:docs/design/*.md` titles/subjects and count ledger rows in `hm:docs/reviews/adversarial_design_ledger.jsonl` per `spec_path` | 12 specs (7 `hm:docs/design/ADR_*.md` with 4, 6, 7, 3, 0, 0, 4 rows; 5 pre-extraction origin specs `hm:docs/design/ADVERSARIAL_DESIGN_REVIEW.md`, `hm:docs/design/ARCHITECTURE_COMPLIANCE_FRAMEWORK.md`, `hm:docs/design/ARCHITECTURE_COMPLIANCE_FRAMEWORK_TIER2_LLM_JUDGE.md`, `hm:docs/design/ARCHITECTURE_COMPLIANCE_FRAMEWORK_TIER3_AUDIT.md`, `hm:docs/design/ARCH_COMPLIANCE_SHIFT_LEFT_GATING.md` with 0 rows each; §10 table) |
| HM exit criterion 5 | `git -C <hm> grep -n -E "second repository \(Cayenne\)|proves the objective" -- docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md` | lines 5405, 5410 |
| Lifted HM sentences | `git -C <hm> grep -n -E "Never use bare|defaulting|interface probing and silent|Temporary .bridge|Refactor within scope|Single point of definition|must use POSIX format|alone is not sufficient" -- GEMINI.md` | lines 103, 104, 105, 111, 129, 136, 189, 191 |
| Host-contract decision 6 | `sed -n 80,81p <hm>/docs/design/ADR_GATE_HOST_CONTRACT.md` | quoted in §2 item 6 |
| Hooks no-op without the marker | `sed -n 72,81p plugins/arch-compliance/hooks/posttooluse_gate.py` | exit 0 with an optional stderr note |
