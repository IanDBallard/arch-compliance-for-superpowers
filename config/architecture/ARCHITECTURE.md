# Architecture doctrine — arch-compliance plugin

This file and `config/architecture/mandates.yml` govern the code and prose of this
repository: the Python package under `plugins/arch-compliance/python/acf/`, the hooks
under `plugins/arch-compliance/hooks/`, the skill prose under
`plugins/arch-compliance/skills/`, the TypeScript bridge under
`plugins/arch-compliance/detectors/typescript/`, the plugin's tests and fixtures under
`plugins/arch-compliance/tests/`, and the repository-level `tests/`, `scripts/` and
`config/`. The CI diff gate and the PostToolUse hook run the registry's detectors on
changed `.py`, `.ts` and `.tsx` files anywhere in the repository; prose and
configuration are held to this file by review. Where a
Superpowers default conflicts with a rule here, the rule here wins
(`docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:51`, principle 5). The five governing
principles at `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51` are not restated
here.

The stock sections (`## Fail loud` through `## React boundaries`) come from the plugin's
react-app and python-service profiles, merged during `/acf-setup`; the one id both
profiles carry, `ops.no-build-artifacts`, is kept once. This host is polyglot: a Python
package and a TypeScript detector bridge. Rules lifted from another repository are
quoted with their attribution (HistoricMansions at commit `22eae4f9`) so this file is
complete on its own.

## Fail loud

Errors must surface. Do not swallow failures in empty `catch` blocks or catch bodies
that only comment. Prefer explicit handling, rethrow, or reporting.

Failures must not disappear. Bare `except:` and broad `except Exception:` handlers that
swallow errors are forbidden unless explicitly exempted with a reason.

The two detector fixtures that exist to contain these patterns
(`plugins/arch-compliance/tests/fixtures/python/bad_except.py`,
`plugins/arch-compliance/tests/fixtures/typescript/bad.tsx`) carry the row's exemption
token with a reason on the flagged line; the detector tests call the scanners directly
and still see the finding.

Lifted: "Never use bare `except:` blocks. Raise custom descriptive exceptions immediately
when data or dependencies are missing" (HistoricMansions `GEMINI.md` §3, `hm:GEMINI.md:103`).
"No 'defaulting' to None to avoid a crash" (`hm:GEMINI.md:104`). "`hasattr()`-based
interface probing and silent degradation … are shims" (`hm:GEMINI.md:105`).

## No shims

Avoid type escape hatches. Explicit `any` annotations and `as any` assertions hide
contract breaks; prefer typed boundaries and narrow casts when unavoidable.

Do not probe optional attributes with `hasattr` to paper over missing interfaces.
Prefer explicit protocols, typed optionals, or clear control flow.

Lifted: "Temporary 'bridge' code, compatibility shims, or 'just-in-case' logic to mask
architectural misalignments are forbidden" (HistoricMansions `GEMINI.md` §4,
`hm:GEMINI.md:111`).

## POSIX paths

When persisting paths to YAML/JSON, use `Path.as_posix()` — do not `str(path)` path-like
names into dump/serialization payloads.

Lifted: "Path strings persisted to YAML or JSON must use POSIX format" (HistoricMansions
`GEMINI.md` §10, `hm:GEMINI.md:189`). "`Path.as_posix()` alone is not sufficient …
normalization is a string-level substitution" (`hm:GEMINI.md:191`). This plugin is
stricter than the lifted text: its persisted path fields refuse a backslash rather than
normalize it (`PosixStr`, `plugins/arch-compliance/python/acf/adr/contract.py:129`).

## Build artifacts

Do not stage or commit generated trees such as `dist/` or `build/`.

## Fail-loud ratchet

Optional whole-tree freeze of bare/broad-except counts. Enable the mandate and commit a
`config/architecture/fail_loud_ratchet.json` baseline (`{"files": {"path.py": N}}`).

## Façade sinks

Optional config-driven rule: forbid direct writes to a protected path regex outside
allowlisted modules. Set `params.target_literal_re` / `allowlist_globs`, then flip
`status` to `enforced`. Unenforced here: this repository has no `index.yml` façade.

## FSM transitions

Optional config-driven rule: writes to a state field must call a named validator in the
same function scope. Set `params.state_field` / `validator_name`, then enforce.
Unenforced here: this repository has no state field.

## Soft fail-loud smells

Silent fallbacks and quiet degradation paths that deterministic AST rules cannot catch
may be reviewed via the LLM judge (`llm_fail_loud`).

## React boundaries

Views render and wire UI; data fetching, domain aggregation, and business rules live
outside view components (hooks, services, or loaders). Soft smells that need judgment
are reviewed via the LLM judge (`llm_react_boundaries`). Unenforced here: there is no
React app; the TypeScript in this repository is a detector bridge.

## One base exception

Every ACF exception subclasses `AcfError` and nothing else; no stdlib mixin such as
`ValueError` or `KeyError` joins the bases. Source: phase 1b decision. Row:
`plugin.one-base-exception`.

## One owner for host paths

`acf.repo` is the one declaration of where ACF looks inside a host repository, and it
imports only the standard library (`plugins/arch-compliance/python/acf/repo.py:1-6`).
Row: `plugin.one-owner-host-paths`; its test scans `plugins/arch-compliance/python/` and
`plugins/arch-compliance/hooks/`. The repository-level `tests/` and `scripts/` follow
the rule by importing the `acf.repo` constants, which review checks. Current breach in an
executable skill snippet, recorded not hidden:
`plugins/arch-compliance/skills/architecture-review/SKILL.md:62` spells
`Path("config/architecture/mandates.yml")` instead of importing `acf.repo.MANDATES_REL`;
reconciling the skill snippet is spec `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md`
§9 follow-up 4.

## Declared, never defaulted

The adversarial-design-review gate's host values are declared by the host in
`config/architecture/adr.yml`; no default stands in for a missing declaration, and a
missing declaration fails loud. Source: phase 1c decision 4,
`plugins/arch-compliance/python/acf/adr/host.py:19-33`. Row:
`plugin.declared-never-defaulted`. Three defaults elsewhere in the package are outside
this rule and recorded here: the fail-loud ratchet's baseline path when a row omits
`params.baseline` (`plugins/arch-compliance/python/acf/repo.py:23-26`), `resolve_repo`
falling back to the process directory (`plugins/arch-compliance/python/acf/repo.py:32-44`,
documented there as a fallback), and the Tier-2 LLM judge's default provider and models
when `--provider` / `ACF_JUDGE_PROVIDER` or `--model` / `ACF_JUDGE_MODEL` are omitted
(`DEFAULT_PROVIDER = "anthropic"`, `DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-6"`,
`DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"` in
`plugins/arch-compliance/python/acf/judge.py:25-27`; provider API keys are never
defaulted or cross-provider-fallback-resolved).

## Prose names no host

Skill prose and runtime messages name no host repository, path or section; a host
reaches the gate only through its declaration and its doctrine. Rows:
`plugin.adr-code-names-no-host` (the gate's package and runtime messages) and
`plugin.gate-prose-names-no-host` (`plugins/arch-compliance/tests/test_adr_skill_prose.py`
checks the two gate skills and `post-merge-housekeeping` against the enumerated
`FORBIDDEN` list of known origin-host (`HistoricMansions`) vocabulary; the other three
skills in `plugins/arch-compliance/skills/` have no row yet).

## Frozen ledger format

A `LedgerRow` or `LedgerAmendment` field changes only through a spec and a gate run; the
ledger is append-only and nothing moves. A verification pass writes no ledger record; the
spec's header line is its record. Source:
`plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:443-452`. Row:
`plugin.frozen-ledger-format`.

## Live consumers

An export has a live call site in the package, a hook or a skill. A test is not a
consumer: a function only tests call is dead code with a test attached. Source: reviewer
ruling on `run_git`, plugin PR #9. No row: no test enforces this yet.

## No completeness claims

A factual claim about the tree, in a spec or a test assertion, is not load-bearing on
"every", "all", "only", "complete", "untouched" or "no second" unless a recipe that a
reader can re-run backs the quantifier. A test that must bound a population allowlists
per line with a reason. A normative rule in this file ("every ACF exception subclasses
`AcfError`") states a requirement, not a census; its row's test is the recipe. Source:
the responding skill's sentence type T3, "Universally quantified claim | Recipe backing
the quantifier, or delete the quantifier"
(`plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:152`).
No row: no test enforces this yet.

## Declared text decoding

Every subprocess call in the package or the hooks that reads text declares
`encoding="utf-8"`; every file read of prose declares its encoding. The scope is runtime
code, which decodes a host's diffs, paths and scanner output; the plugin's tests run
their subprocesses over this repository's own fixtures and are outside it. Three calls
breach the rule today and are declared debt: `plugins/arch-compliance/python/acf/diff.py:24-30` (`run_git`),
`plugins/arch-compliance/python/acf/adr/citations.py:62-65` (`_git`) and
`plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:49-56` (the Node
scanner). Recipe: `grep -rn "text=True" plugins/arch-compliance/python plugins/arch-compliance/hooks`.
The fix and its test are spec `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` §9,
follow-up 1. No row: no test enforces this yet.

## Release discipline

A change to a skill's prose bumps the plugin version in
`plugins/arch-compliance/.claude-plugin/plugin.json` and `pyproject.toml`. Before a gate
or `post-merge-housekeeping` run, the installed copy of the two gate skills and
`post-merge-housekeeping` is byte-checked against the clone
(`scripts/check_installed_skills.py`); on a mismatch the plugin is reinstalled from the
clone and the session restarted. The check covers those three skill trees only: the hooks
run the installed copy's `hooks/` and `python/` (`plugins/arch-compliance/hooks/posttooluse_gate.py:22-26`),
which it does not compare. Source: phase 1d spec risk table (cache drift) and 1d plan
Task 8 step 1. No row: no test enforces this yet.

## Single point of definition

Lifted: "When the same operation, constant set, or decision procedure … is needed by more
than one module, it must have exactly one canonical implementation that every call site
consumes" (HistoricMansions `GEMINI.md` §7, `hm:GEMINI.md:136`). Current breaches,
recorded not hidden: two git runners, `plugins/arch-compliance/python/acf/diff.py:17`
(`run_git`) and `plugins/arch-compliance/python/acf/adr/citations.py:54` (`_git`),
consolidated in spec `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` §9 follow-up 1;
and two skill snippets that re-spell or by-eye a package helper,
`plugins/arch-compliance/skills/architecture-review/SKILL.md:62` (`Path("config/architecture/mandates.yml")` instead of `acf.repo.MANDATES_REL`) and
`plugins/arch-compliance/skills/acf-setup/SKILL.md:137` (by-eye anchor check instead of
`acf.registry.missing_anchors`), tracked in spec
`docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` §9 follow-up 4. No row: no test
enforces this yet.

## Scoped refactor

Lifted: "Within an approved plan or ticket, remove legacy dependencies or non-contractual
patterns in code paths you are changing. Do not expand scope to unrelated modules"
(HistoricMansions `GEMINI.md` §7, `hm:GEMINI.md:129`). No row: no test enforces this yet.

## High-frequency misses

The compliance reviewer checks these first:

- A completeness claim in a spec or test with no recipe behind it.
- A default that re-enters for a declared value.
- A host name in skill prose or a runtime message.
- A stdlib mixin on an exception class.
- A subprocess text call without an encoding.
- A check re-implemented in a test or a skill instead of consumed from the package
  (`acf.registry.load_mandates`, `acf.registry.missing_anchors`,
  `acf.cli_check_diff.KNOWN_DETECTORS`, the `acf.repo` constants).

## Post-merge

Host operational declarations read by `post-merge-housekeeping`:

- **Shared-checkout branch lock:** none declared.
- **Worktree daemon probe:** none declared (tests spawn no background server).
- **Post-merge CI workflows:** `.github/workflows/ci.yml` (`test` job on `main`).
- **Durable tracking target:** GitHub Issues on `IanDBallard/arch-compliance-for-superpowers` (`gh issue create`), so filing a follow-up or guard escape never edits an already-cleared spec.

No row: host operational declarations; no test enforces this.
