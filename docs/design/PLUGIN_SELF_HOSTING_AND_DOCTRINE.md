# The Plugin as a Host of Its Own Gate

**Status:** draft v1 — 2026-10-22, awaiting user approval of the design; not yet reviewed.
**Adversarial review:** none yet. This spec is the first one the plugin's gate reviews from
this repository, and that run is its acceptance (§6).
**Repo:** `IanDBallard/arch-compliance-for-superpowers`, `main` at `8dabe82`.
**Workstream:** HistoricMansions workstream E, portable governance. Proposed phase number: **1e**
(the second-repository run currently called 1e becomes 1f when this spec's roadmap row lands; see §10).

## 0. Citation convention

Unprefixed paths are this repository at `8dabe82`. Paths prefixed `hm:` are
`HistoricMansionsV3` at `6de1c790` (`main`); paths prefixed `hm-1d:` are its cutover branch
`feat/adr-gate-hm-cutover` at `3e1a2390`, which holds the 1d spec and plan.

The gate's citation resolver has no notion of another repository: a prefixed path classifies
as `unresolved` (`plugins/arch-compliance/python/acf/adr/citations.py:129-187` tests
`proposed`, absolute, escaping, existing, suffix, ignored, historical, then gives up), and
an unresolved citation is a hard fail before dispatch
(`plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:76-82,101`). HM's
host-contract runs handled their `acf:` citations by precedent: the controller mapped each
prefixed path to the sibling checkout and the reviewers opened the files there
(`hm:docs/reviews/adr_runs/ADR_GATE_HOST_CONTRACT_v3_2026-10-12.md:28,35,247`). The
acceptance run of this spec (§6) follows that precedent: before classification the
controller rewrites `hm:` to `C:/Users/iball/Arduino/Projects/HistoricMansions/` and
`hm-1d:` to that repository's cutover worktree path, hands reviewers the mapped paths, and
counts them as cited files. Every unprefixed citation in this spec is a full
repository-relative path with no shorthand, because the resolver's suffix match works on
whole path components and an ellipsis resolves to nothing.

Independently of that mapping, **every rule this spec lifts from another repository is
quoted in the doctrine, never pointed to**, so the doctrine is complete on its own and a
future reviewer on a node without the sibling checkout can still verify it.

## 1. Goal

This repository runs the plugin's own adversarial-design-review gate on its own specs, under
its own declared configuration and its own written doctrine, so that a spec about the
plugin is reviewed and recorded where the files it changes live.

Today a spec about the plugin is written in HM's `docs/design/`, reviewed by HM's gate
against HM's doctrine, and recorded in HM's ledger. Eight such specs sit there
(`hm:docs/design/ADR_*.md`, `hm:docs/design/ARCH_COMPLIANCE_SHIFT_LEFT_GATING.md`), holding
21 of HM's ledger records. That is the same split for prose and review that phases 1b-1d
remove for code.

## 2. Decisions this design records (user, 2026-10-22)

Inputs, not tree-derivable claims:

1. **A spec lives in the repository whose files its change surface names.** A mixed spec
   splits along that line: a plugin-side spec here and a host-side adoption spec or plan
   there, instead of one HM spec carrying a plugin PR inside a task as 1c did.
2. **The plugin's doctrine is proposed by this spec.** No written doctrine exists for this
   repository (`ls *.md` at the root: `README.md` only; no `config/architecture/`). The
   doctrine draws on HM's `GEMINI.md` where a rule applies to Python, and on this plugin's
   own review record. (user)
3. **Post-merge-housekeeping is extracted to the plugin in its own spec, after this one.**
   It is not in scope here. HM's workstream exit criterion 6, which records the skill as
   "HM-local by decision", is revised by that spec, not this one. (user: "I'm ok holding it")
4. **Phase 1d stays frozen at v4.** The GEMINI.md §1 item 8 sentence that conflicts with the
   plugin's verification-pass rule is corrected by the housekeeping spec, which rewrites that
   item anyway. (author's call, user accepted)
5. **Acceptance is a live gate run on this spec from this repository, and its verdict
   binds** (§6). 1d's acceptance accepts any outcome because it proves plumbing; here the
   plumbing and the review are the same run. (author's call)
6. **The host-contract spec moves here in this phase**, as its own decision 6 schedules
   (`hm-1d:docs/design/ADR_GATE_HOST_CONTRACT.md:80-81`: "moves to the plugin repository
   after 1d's acceptance run"). Its ledger rows stay in HM (§3).
7. **Bootstrap through `/acf-setup`, not by hand.** The plugin's own setup skill writes the
   mandate registry and doctrine pair for a host (`README.md:20`); this repository is a host
   and uses it. (author's call)

## 3. Non-goals

- No change to the persisted ledger format, `LedgerRow`, `LedgerAmendment` or the
  `TouchedSurface` vocabulary. The ledger-schema redesign stays a filed follow-up.
- No ledger migration. HM's 21 records for plugin-related specs stay in HM, matched to their
  HM spec paths; the ledger is append-only and nothing moves. A moved spec leaves a stub at
  its HM path naming its new home, so those rows keep resolving.
- No new detector, no change to any detector, no `architecture-review` movement. Phase 2
  stays blocked on the extension point.
- No housekeeping extraction (decision 3). No Cayenne change.
- No Cursor twin and no dual-tree identity test: this repository ships one tree.
- No fix to the git-runner decoding defect found while authoring (§4.1, item 7). It is filed
  (§9), not folded in: this spec's theme is declaration and doctrine, not the git runner.

## 4. What this touches

### 4.1 Census (authoring time, 2026-10-22; commands in the appendix)

1. `config/architecture/` is absent. `.acf/enabled` is absent and ignored (`.gitignore:8`).
2. `docs/design/` holds one document (`ARCH_COMPLIANCE_FOR_SUPERPOWERS.md`); `docs/plans/`
   holds four; `docs/reviews/` is absent. No `CLAUDE.md`.
3. The host contract reads two declared values and the doctrine path
   (`plugins/arch-compliance/python/acf/adr/host.py:19-32`); the doctrine is the file and
   every document it points to (`plugins/arch-compliance/skills/adversarial-design-review/reviewers/compliance.md:12`), and the reviewer checks a
   doctrine's self-declared high-frequency misses first (`plugins/arch-compliance/skills/adversarial-design-review/reviewers/compliance.md:47`).
4. `/acf-setup` writes `config/architecture/mandates.yml` and `ARCHITECTURE.md` from a
   profile, merging both profiles for a two-language host
   (`plugins/arch-compliance/skills/acf-setup/SKILL.md:90-118`). This repository has Python
   under `plugins/arch-compliance/python/` and TypeScript under
   `plugins/arch-compliance/detectors/typescript/`.
5. The python-service profile, run over this repository's whole history
   (`--base dfff93f5`, the root commit), reports 4 findings: 1 BLOCK, `fail-loud.bare-except`
   in `plugins/arch-compliance/tests/fixtures/python/bad_except.py` (a detector fixture that
   must contain a bare except), and 3 WARN `no-shims.hasattr` in three test modules. The
   package itself reports none.
6. The registry schema accepts `detection: manual` rows and requires a `detector` string on
   every row, but checks that string against known detectors only for `ast` and `guard`
   (`plugins/arch-compliance/python/acf/registry.py:8-18,49`). A manual row can therefore name
   the test that enforces it.
7. The measurement in item 5 crashed until `PYTHONUTF8=1` was set: `run_git` decodes git's
   output with the locale codec (`plugins/arch-compliance/python/acf/diff.py:24-30`,
   `text=True`, no `encoding`), and so does the citation module's own runner
   (`plugins/arch-compliance/python/acf/adr/citations.py:62-65`). On a Windows host with a cp1252 locale, a diff
   containing a character outside cp1252 (this repository's skill prose has many) raises
   inside the reader thread. CI runs on Linux and is unaffected.
8. CI runs `pytest` only (`.github/workflows/ci.yml:34-35`); the diff gate is not run on
   this repository's own changes.
9. The plugin's acceptance test for a non-origin host builds a fixture host in a temporary
   directory and exercises the storage path through the Python API
   (`plugins/arch-compliance/tests/test_adr_host_acceptance.py:74-96`). No live skill run
   from the installed plugin has happened outside HM.
10. HM's exit criterion 5 names Cayenne as the second repository and says it "proves the
    objective rather than approximating it"
    (`hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:5264-5269`).
11. The plugin's hooks fire on every subagent start and every Write/Edit in every repository
    where the plugin is installed, and no-op without `.acf/enabled`
    (`plugins/arch-compliance/hooks/hooks.json`, `plugins/arch-compliance/hooks/posttooluse_gate.py:72-76`). Writing
    the marker here turns the PostToolUse gate on for this repository's own edits.
12. Tests: 395 collected at `8dabe82`, from the single `testpaths` entry
    `plugins/arch-compliance/tests` (`pyproject.toml`). Plugin version `0.2.0`
    (`plugins/arch-compliance/.claude-plugin/plugin.json:3`, `pyproject.toml:3`).
13. Not yet true at authoring: 1d has not merged (`feat/adr-gate-hm-cutover` at `3e1a2390`
    is not an ancestor of HM `main`), and the node has no `arch-compliance` plugin installed.
    §5.7 step 1 is therefore a real wait, not a formality.

### 4.2 Disposition

| Path | Change | Why |
|---|---|---|
| `config/architecture/adr.yml` | Create (§5.1) | The two host values the gate cannot derive |
| `config/architecture/mandates.yml` | Create via `/acf-setup`, then extend (§5.2) | The registry is the spine; the plugin's own rules become rows |
| `config/architecture/ARCHITECTURE.md` | Create via `/acf-setup`, then extend (§5.2) | The doctrine the compliance reviewer reads |
| `.acf/enabled` | Written by `/acf-setup`, per developer, ignored | Turns the hooks on here |
| `CLAUDE.md` | Create (§5.3) | Session process: spec and plan locations, the gate before `writing-plans`, the cache check |
| `README.md` | Add one paragraph | Says this repository is a host of its own gate and where its records are |
| `tests/test_self_host.py` (repository root) | Create (§5.5) | Existence of what the declaration and doctrine name; every row's anchor in the doctrine |
| `pyproject.toml` | `testpaths` gains the root `tests/` directory | The self-host test is a property of this repository, not of the shipped plugin tree (`README.md:87-89` keeps host-property tests out of it) |
| `.github/workflows/ci.yml` | Add one step (§5.6) | `acf-check-diff --base origin/main` on this repository's own changes |
| `docs/design/ADR_GATE_HOST_CONTRACT.md` | Create, copied from `hm:docs/design/ADR_GATE_HOST_CONTRACT.md` with a provenance line | Decision 6 |
| `docs/reviews/adr_runs/`, `docs/reviews/adversarial_design_ledger.jsonl` | Created by the acceptance run (§6) | First records |
| `hm:docs/design/ADR_GATE_HOST_CONTRACT.md` | Replace body with a stub naming the new path (HM, docs-only) | Ledger rows keep resolving (§3) |
| `hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md` | Workstream E rows (§10) (HM, docs-only) | The roadmap is the only scheduling surface |

## 5. Design

### 5.1 The declaration

`config/architecture/adr.yml` is exactly:

```yaml
runs_dir: docs/reviews/adr_runs
ledger_path: docs/reviews/adversarial_design_ledger.jsonl
```

The same two names HM uses, so a reader of either repository finds the records in the same
place. No other key: `AdrHostConfig` is `extra="forbid"` (`plugins/arch-compliance/python/acf/adr/host.py:22-27`).

### 5.2 The doctrine

`/acf-setup` is run from the repository root. It detects both languages and proposes one
merged `mandates.yml` and one merged `ARCHITECTURE.md` from the two stock profiles; the
merge is accepted. Every stock anchor survives verbatim (`## Fail loud`, `## No shims`,
`## POSIX paths`, `## Build artifacts`, `## Fail-loud ratchet`, `## Façade sinks`,
`## FSM transitions`, `## Soft fail-loud smells`, and the React anchors), because the
registry matches `arch_anchor` as a literal substring of the file.

The stock rows that do not apply here are set `status: unenforced`, not deleted, so the
file stays diffable against the profile: `facade.forbid-sink` (no `index.yml` here),
`fsm.transition-guard` (no state field), `soft.react-boundaries` (no React app; the
TypeScript here is a detector bridge).

Then `ARCHITECTURE.md` gains the plugin's own sections. A section whose rule an existing
test already enforces also gets a `detection: manual` row in `mandates.yml` whose
`detector` names that test module (§4.1 item 6): the registry row is a pointer from the
rule to its enforcement, not a promise of enforcement that does not exist. Five sections
qualify today (one base exception, one owner for host paths, declared-never-defaulted,
prose-names-no-host, frozen ledger format). The other four, and the two lifted anchors
below, are doctrine prose without a row; each says so in its last sentence ("no row: no
test enforces this yet"), and a row is added in the change that adds the test. No row
names a future test, so §5.5's third check holds on the day this merges. Each section
states the rule in one or two sentences and names its source. The sections, with their
sources:

| Section | Rule | Source |
|---|---|---|
| `## One base exception` | Every ACF exception subclasses `AcfError` and nothing else; no stdlib mixin. | 1b decision; `plugins/arch-compliance/tests/test_adr_exceptions.py` |
| `## One owner for host paths` | `acf.repo` is the only declaration of where ACF looks in a host, and it imports only the standard library. | `plugins/arch-compliance/tests/test_repo_paths.py:53,74` |
| `## Declared, never defaulted` | A value the gate cannot derive is declared by the host; no default stands in for a missing declaration. | 1c decision 4; `plugins/arch-compliance/python/acf/adr/host.py` |
| `## Prose names no host` | Skill prose and runtime messages name no host repository, path or section. | `plugins/arch-compliance/tests/test_adr_code_portability.py:11,21` (row); `plugins/arch-compliance/tests/test_adr_skill_prose.py` (prose) |
| `## Frozen ledger format` | A `LedgerRow` or `LedgerAmendment` field changes only through a spec and a gate run. A verification pass writes no ledger record; the spec header line is its record. | `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:443-452`; row names `plugins/arch-compliance/tests/test_adr_ledger.py` |
| `## Live consumers` (no row) | An export has a live call site in the package, a hook or a skill. A test is not a consumer. | Reviewer ruling on `run_git`, plugin PR #9 |
| `## No completeness claims` (no row) | No spec claim, test assertion or doctrine sentence is load-bearing on "every", "all", "only", "complete", "untouched" or "no second". A test that must bound a population allowlists per line with a reason. | `plugins/arch-compliance/skills/adversarial-design-review/claims/extraction.md:71`; the HM verdict matrix (seven claims adverse in every run, all universal) |
| `## Declared text decoding` (no row) | Every subprocess call that reads text declares `encoding="utf-8"`; every file read of prose declares its encoding. | §4.1 item 7 (two breaches today, declared debt in §9; the test arrives with the fix) |
| `## Release discipline` (no row) | A change to a skill's prose bumps the plugin version; the installed copy is byte-checked against the clone before a gate run. | 1d spec v3 block (cache drift); 1d plan Task 8 step 1 |

The lifted HM rules are quoted under the stock anchors they belong to, with their
attribution, so the reviewer reads them here. Under `## Fail loud`: "Never use bare
`except:` blocks. Raise custom descriptive exceptions immediately when data or
dependencies are missing"; "No 'defaulting' to None to avoid a crash"; "`hasattr()`-based
interface probing and silent degradation … are shims" (`hm:GEMINI.md:102-106`). Under
`## No shims`: "Temporary 'bridge' code, compatibility shims, or 'just-in-case' logic to
mask architectural misalignments are forbidden" (`hm:GEMINI.md:110-112`). Under a new
`## Single point of definition`: "When the same operation, constant set, or decision
procedure … is needed by more than one module, it must have exactly one canonical
implementation that every call site consumes" (`hm:GEMINI.md:134`), with the two git
runners (`plugins/arch-compliance/python/acf/diff.py:17`,
`plugins/arch-compliance/python/acf/adr/citations.py:54`) recorded beside it as the current breach, not
hidden. Under `## POSIX paths`: "Path strings persisted to YAML or JSON must use POSIX
format"; "`Path.as_posix()` alone is not sufficient … normalization is a string-level
substitution" (`hm:GEMINI.md:190-194`). Under `## Scoped refactor`: "Within an approved
plan or ticket, remove legacy dependencies or non-contractual patterns in code paths you
are changing. Do not expand scope to unrelated modules" (`hm:GEMINI.md:129`).

Rules of HM's that do not apply are not lifted: HFSM (§5), UI isolation (§6), the metadata
façade (§11), book-root resolution (§10), the content pipeline (§12, §13).

The doctrine ends with `## High-frequency misses`, which the compliance reviewer checks
first: a completeness claim in a spec or test; a default that re-enters for a declared
value; a host name in prose; a stdlib mixin on an exception; a subprocess text call
without an encoding.

The plugin's existing design document keeps its five "governing principles"
(`docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-52`); `ARCHITECTURE.md` points to it and
restates nothing from it that a mandate row does not need.

### 5.3 Session process (`CLAUDE.md`)

A short file, pointing at the doctrine and recording what Superpowers' defaults do not
know about this repository, in the form HM's `CLAUDE.md` uses
(`hm:CLAUDE.md:18-30`):

- Specs at `docs/design/<TOPIC>.md`, plans at `docs/plans/PLAN_<TOPIC>.md`.
- Brainstorming's terminal state is `/arch-compliance:adversarial-design-review <spec>`
  then `writing-plans`; `BLOCKED` returns to the spec through
  `arch-compliance:responding-to-adversarial-review`; re-run scope follows the revision
  class as the gate skill states it.
- Before any gate run, the installed plugin's gate-skill files are byte-checked against
  this clone (the script in `hm-1d:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md` Task 8 step 1,
  copied here as `scripts/check_installed_skills.py` or kept inline; builder's choice).
- Citation convention for specs here: unprefixed paths are this repository; another
  repository is cited with a prefix for the reader and its rule is quoted, as §0 says.
- Windows note until §9 item 1 is fixed: run the diff gate with `PYTHONUTF8=1`.

### 5.4 Installation

The plugin is installed on the developer's node by 1d (`hm-1d:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md`
Task 2) from this clone; this spec adds no install step. What changes here is the
marker: `/acf-setup` writes `.acf/enabled`, which makes the PostToolUse gate run the
Tier-1 detectors on every edit in this repository. The 4 findings in §4.1 item 5 are not
on changed lines of any future edit unless those lines change, and the one BLOCK is in a
fixture whose purpose is to contain the pattern; it carries no exemption token because the
detector tests need it unmodified. If a future edit touches that fixture, the edit is made
with the hook's finding acknowledged, not silenced.

### 5.5 The self-host test

`tests/test_self_host.py` at the repository root, collected through the added `testpaths`
entry (`pyproject.toml` today lists only `plugins/arch-compliance/tests`), importing `acf`
the way the plugin's own tests do. Three tests, each falsifiable by deleting or editing
one file:

1. `config/architecture/adr.yml` loads through `load_host_config` and both paths it names
   are under `docs/reviews/`.
2. `config/architecture/ARCHITECTURE.md` exists, and every `arch_anchor` in
   `config/architecture/mandates.yml` is a literal substring of it (the profile-drift
   check, applied to the host pair instead of the profiles).
3. Every `detection: manual` row's `detector` names an existing test module under
   `plugins/arch-compliance/tests/`.

### 5.6 CI

One step after `pytest` in `.github/workflows/ci.yml`:
`python -m acf.cli_check_diff --repo . --base origin/main` with the host registry. It fails
the job on a BLOCK finding on changed lines. On the first run after merge it reports
nothing, because the base is the merge itself.

### 5.7 Sequencing

1. **Start condition, not met at authoring:** 1d has merged in HM (its Task 9), which
   implies its Task 1 pins are on this repository's `main` and its Task 2 has installed the
   plugin on the node from this clone (at authoring, `feat/adr-gate-hm-cutover` is not an
   ancestor of HM `main` and the node's `installed_plugins.json` lists no `arch-compliance`).
   This spec adds no install step and does not start before that.
2. Branch `feat/self-host` from `main` here, at or after the 1d pin merge, in its own worktree.
3. §5.1, §5.2, §5.3, §5.5, §5.6, the host-contract spec copy, the README paragraph.
4. Cache byte-check, then the acceptance run (§6) on this spec, from the worktree root.
   Records committed on the branch.
5. PR, squash-merge.
6. HM: one docs-only commit with the stub and the roadmap rows (§10), through HM's normal
   flow, after 1d's own roadmap edits (its Task 6) are on HM `main`, so the two never
   touch the workstream table at once.

## 6. Acceptance

From the branch's worktree, after step 3 of §5.7 and before merge: run
`/arch-compliance:adversarial-design-review docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md`.
The run must complete end to end through the installed plugin skill, write its run detail
under `docs/reviews/adr_runs/` and the first row of `docs/reviews/adversarial_design_ledger.jsonl`,
and the row must be read back as the skill requires. **The verdict binds:** `BLOCKED`
returns to this spec through the responding skill, and the re-run scope follows the
revision class. Any revision to §5.2's rules is a mechanism revision and re-runs in full,
blind. Both records are committed on the branch; `main` is untouched until the run clears.

The compliance reviewer in that run reads the doctrine this spec creates. That is the
point: the doctrine's first test is whether four blind reviewers can hold this design to it.

## 7. Shape fit

**Extends:** the host contract as designed (one declaration file, the fixed doctrine path:
`hm-1d:docs/design/ADR_GATE_HOST_CONTRACT.md` §5), the `/acf-setup` bootstrap, and the
registry-is-the-spine principle (`docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:49`): the
plugin's own rules become registry rows with anchors, in the plugin's own format, rather
than a second kind of rules document. **Second way created:** none for the gate or the
registry. The `CLAUDE.md` is a pointer and process file of the kind HM already has, not a
second doctrine. **Day-one design:** the same; a plugin that ships a host contract would
have been its own first host. **Pattern sweep:** specs about the plugin living in another
repository. Found: eight in HM (§1). Two are live and move or are superseded by this
phase's rule (the host contract, moved; the 1d cutover, HM's own change surface, stays);
six are superseded, draft or stub and stay beside their ledger rows, listed in §10.

## 8. Definition of done

1. `python -m pytest -q` from the root passes, and `--collect-only` lists the three new
   tests under the root `tests/` directory beside the plugin's own.
2. Deleting `config/architecture/adr.yml`, or `ARCHITECTURE.md`, or removing one anchor
   heading from `ARCHITECTURE.md`, fails `tests/test_self_host.py`; restoring it passes.
3. `python -m acf.cli_check_diff --repo . --base origin/main` from the root, with
   `PYTHONUTF8=1` on Windows, exits 0 on the branch.
4. `/acf-setup` was used for the bootstrap and its merge choices are recorded in the plan's
   ledger; `git diff --stat main` shows no file outside §4.2.
5. The acceptance run of §6 cleared (`CLEARED` or `CLEARED_WITH_ABSORPTIONS`, absorptions
   folded in) and its run detail and ledger row are committed on the branch.
6. `docs/design/ADR_GATE_HOST_CONTRACT.md` exists here with a provenance line naming its HM
   origin and the HM commit it was copied at.
7. The CI step of §5.6 ran green on the PR.
8. The HM docs-only commit of §10 is merged, or its PR is open and linked from this spec's
   plan.

## 9. Risks and filed follow-ups

| Risk | Mitigation |
|---|---|
| The installed plugin serves stale gate prose during the acceptance run | Byte-check before the run (§5.3); reinstall on mismatch, as 1d does |
| The hooks now gate this repository's edits and a stock rule misfires on plugin code (for example a `hasattr` in a test) | WARN rows return context, not a block; a BLOCK on a legitimate line takes the row's exemption token with a reason, never a status flip |
| The doctrine's lifted rules drift from HM's `GEMINI.md` | They are quoted with an attribution and a line; drift is visible on either side and is not a defect, since the plugin's doctrine is its own |
| A spec here cites HM files the reviewers cannot open | §0: quote, never point |

Filed follow-ups, each to a roadmap row in HM (the only scheduling surface) and, once the
housekeeping skill is extracted, to the plugin's own board:

1. **Git runner decoding.** `run_git` and the citation runner decode with the locale codec
   (§4.1 item 7). Fix: `encoding="utf-8"` on both, and the one-runner consolidation the 1a
   roadmap row already claims (`hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:5029`, "one git runner") but the tree
   does not show. One plan, no spec: a defect with a test.
2. **Post-merge-housekeeping extraction** (decision 3), the next spec. It also corrects
   `hm:GEMINI.md:61` and adds the row-identity rule for amendments after a verification
   pass or user override.
3. **Hook quiet flag** (`--quiet-disabled` in `hooks.json`), already filed by 1d.

## 10. Roadmap effect (HM workstream E, docs-only)

- New row **1e**: this spec, with the plan's path and this repository's PR.
- The second-repository run becomes **1f**, and exit criterion 5 reads "a second
  repository can install the plugin and run the gate with its own declared configuration
  and no HM paths anywhere; the plugin repository is the first such host (1e), Cayenne the
  foreign-stack proof (1f)". Criterion 6 is left for the housekeeping spec.
- The 1c row records that `ADR_GATE_HOST_CONTRACT.md` moved here, with the stub's path.
- The six specs that stay: `ADR_EXTRACTION_TO_PLUGIN.md` (superseded),
  `ADR_GATE_PLUGIN_COMPONENT.md` (v3, do not re-dispatch), `ADR_GATE_HM_ADOPTION.md` (draft),
  `ADR_PER_FINDING_REVISION_CLASSING.md` (stub), `ADR_REVISION_EVIDENCE_AND_CARRYOVER_INSTRUMENTATION.md`
  (v4 draft), `ARCH_COMPLIANCE_SHIFT_LEFT_GATING.md`. Each stays with its ledger rows; a
  future revival of any of them is authored here under decision 1.

## 11. Left to the builder

- Whether the cache byte-check lives as a script under `scripts/` or inline in `CLAUDE.md`.
- The exact wording of each doctrine section and of the README paragraph, within §5.2's
  table and sources.
- Severity of each manual row (`BLOCK` for the frozen-format, one-base-exception and
  declared-not-defaulted rules; `WARN` elsewhere is the author's suggestion).
- Whether the TypeScript bridge's stock rows stay `enforced` given that `npm ci` is needed
  for the bridge tests; `unenforced` with a reason is acceptable.

## Appendix — premise verification (authoring time)

| Claim | Command | Result |
|---|---|---|
| No doctrine or declaration here | `ls config/architecture .acf *.md` | `config/architecture` and `.acf` absent; `README.md` only |
| 395 tests | `python -m pytest --collect-only -q` | `395 tests collected` |
| Profile over full history: 4 findings | `PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base dfff93f5 --mandates plugins/arch-compliance/profiles/python-service/mandates.yml --json` | 1 BLOCK (`tests/fixtures/python/bad_except.py`), 3 WARN `no-shims.hasattr` (three test modules) |
| The same command without `PYTHONUTF8` crashes | as above, without the variable | `UnicodeDecodeError` in `subprocess._readerthread`, `cp1252.py:23`; exit 1 |
| Manual rows allowed, detector string required | `sed -n 8,18p plugins/arch-compliance/python/acf/registry.py` | `Detection = Literal[…, "manual"]`; `detector: str` |
| CI runs pytest only | `grep -n run .github/workflows/ci.yml` | one step, `pytest` |
| Acceptance test is a fixture host | `sed -n 74,96p plugins/arch-compliance/tests/test_adr_host_acceptance.py` | builds `tmp_path/host`, calls the Python API |
| HM exit criterion 5 names Cayenne | `sed -n 5264,5269p hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md` | quoted in §4.1 item 10 |
| Host-contract decision 6 | `sed -n 80,81p hm-1d:docs/design/ADR_GATE_HOST_CONTRACT.md` | quoted in §2 item 6 |
| Hooks no-op without the marker | `sed -n 72,76p plugins/arch-compliance/hooks/posttooluse_gate.py` | exit 0 with optional stderr warning |
