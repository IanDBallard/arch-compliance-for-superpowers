# Architecture doctrine — arch-compliance plugin

This file and `config/architecture/mandates.yml` govern the Python package under
`plugins/arch-compliance/python/acf/`, the hooks under `plugins/arch-compliance/hooks/`,
the skill prose under `plugins/arch-compliance/skills/` and the TypeScript bridge under
`plugins/arch-compliance/detectors/typescript/`. Where a Superpowers default conflicts
with a rule here, the rule here wins (`docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-52`,
principle 5). The five governing principles stated there are not restated here; a mandate
row that needs one of them names it by its anchor below.

The stock sections (`## Fail loud` through `## React boundaries`) were merged by
`/acf-setup` from the plugin's react-app and python-service profiles. This host is
polyglot: a Python package and a TypeScript detector bridge. Rules lifted from another
repository are quoted with their attribution so this file is complete on its own.

## Fail loud

Errors must surface. Do not swallow failures in empty `catch` blocks or catch bodies
that only comment. Prefer explicit handling, rethrow, or reporting.

Failures must not disappear. Bare `except:` and broad `except Exception:` handlers that
swallow errors are forbidden unless explicitly exempted with a reason.

Lifted: "Never use bare `except:` blocks. Raise custom descriptive exceptions immediately
when data or dependencies are missing" (HistoricMansions `GEMINI.md` §3, `hm:GEMINI.md:102-106`).
"No 'defaulting' to None to avoid a crash" (same). "`hasattr()`-based interface probing and
silent degradation … are shims" (same).

## No shims

Avoid type escape hatches. Explicit `any` annotations and `as any` assertions hide
contract breaks; prefer typed boundaries and narrow casts when unavoidable.

Do not probe optional attributes with `hasattr` to paper over missing interfaces.
Prefer explicit protocols, typed optionals, or clear control flow.

Lifted: "Temporary 'bridge' code, compatibility shims, or 'just-in-case' logic to mask
architectural misalignments are forbidden" (HistoricMansions `GEMINI.md` §4,
`hm:GEMINI.md:110-112`).

## POSIX paths

When persisting paths to YAML/JSON, use `Path.as_posix()` — do not `str(path)` path-like
names into dump/serialization payloads.

Lifted: "Path strings persisted to YAML or JSON must use POSIX format" (HistoricMansions
`GEMINI.md` §10, `hm:GEMINI.md:190-194`). "`Path.as_posix()` alone is not sufficient …
normalization is a string-level substitution" (same).

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
`ValueError` or `KeyError` joins the bases. Source: phase 1b decision, enforced by
`plugins/arch-compliance/tests/test_adr_exceptions.py`. Row: `plugin.one-base-exception`.

## One owner for host paths

`acf.repo` is the only declaration of where ACF looks inside a host repository, and it
imports only the standard library. Source: `plugins/arch-compliance/tests/test_repo_paths.py:53,74`.
Row: `plugin.one-owner-host-paths`.

## Declared, never defaulted

A value the gate cannot derive from the tree is declared by the host in
`config/architecture/adr.yml`; no default stands in for a missing declaration, and a
missing declaration fails loud. Source: phase 1c decision 4,
`plugins/arch-compliance/python/acf/adr/host.py`, enforced by
`plugins/arch-compliance/tests/test_adr_host.py`. Row: `plugin.declared-never-defaulted`.

## Prose names no host

Skill prose and runtime messages name no host repository, path or section; a host
reaches the gate only through its declaration and its doctrine. Source:
`plugins/arch-compliance/tests/test_adr_code_portability.py:11,21` (runtime, the row's test)
and `plugins/arch-compliance/tests/test_adr_skill_prose.py` (prose).
Row: `plugin.prose-names-no-host`.

## Frozen ledger format

A `LedgerRow` or `LedgerAmendment` field changes only through a spec and a gate run; the
ledger is append-only and nothing moves. A verification pass writes no ledger record; the
spec's header line is its record. Source:
`plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:443-452`, enforced by
`plugins/arch-compliance/tests/test_adr_ledger.py`. Row: `plugin.frozen-ledger-format`.

## Live consumers

An export has a live call site in the package, a hook or a skill. A test is not a
consumer: a function only tests call is dead code with a test attached. Source: reviewer
ruling on `run_git`, plugin PR #9. No row: no test enforces this yet.

## No completeness claims

No spec claim, test assertion or doctrine sentence is load-bearing on "every", "all",
"only", "complete", "untouched" or "no second". A test that must bound a population
allowlists per line with a reason. Source:
`plugins/arch-compliance/skills/adversarial-design-review/claims/extraction.md:71`, and the
HistoricMansions verdict matrix (seven claims adverse in every run, all universal).
No row: no test enforces this yet.

## Declared text decoding

Every subprocess call that reads text declares `encoding="utf-8"`; every file read of
prose declares its encoding. The two git runners (`plugins/arch-compliance/python/acf/diff.py:24-30`,
`plugins/arch-compliance/python/acf/adr/citations.py:62-65`) breach this today and are
declared debt (spec `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` §9, follow-up 1);
the test arrives with the fix. No row: no test enforces this yet.

## Release discipline

A change to a skill's prose bumps the plugin version in
`plugins/arch-compliance/.claude-plugin/plugin.json` and `pyproject.toml`; the installed
copy is byte-checked against the clone (`scripts/check_installed_skills.py`) before a gate
run. Source: phase 1d spec v3 block (cache drift) and 1d plan Task 8 step 1.
No row: no test enforces this yet.

## Single point of definition

Lifted: "When the same operation, constant set, or decision procedure … is needed by more
than one module, it must have exactly one canonical implementation that every call site
consumes" (HistoricMansions `GEMINI.md` §7, `hm:GEMINI.md:134`). Current breach, recorded
not hidden: two git runners, `plugins/arch-compliance/python/acf/diff.py:17` (`run_git`) and
`plugins/arch-compliance/python/acf/adr/citations.py:54` (`_git`); the consolidation is
spec §9 follow-up 1. No row: no test enforces this yet.

## Scoped refactor

Lifted: "Within an approved plan or ticket, remove legacy dependencies or non-contractual
patterns in code paths you are changing. Do not expand scope to unrelated modules"
(HistoricMansions `GEMINI.md` §7, `hm:GEMINI.md:129`). No row: no test enforces this yet.

## High-frequency misses

The compliance reviewer checks these first:

- A completeness claim in a spec or test ("every", "all", "only", "complete", "untouched").
- A default that re-enters for a declared value.
- A host name in skill prose or a runtime message.
- A stdlib mixin on an exception class.
- A subprocess text call without an encoding.
