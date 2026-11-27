# Architecture doctrine — arch-compliance plugin

This file and `config/architecture/mandates.yml` govern the code and prose of this
repository: the Python package under `plugins/arch-compliance/python/acf/`, the hooks
under `plugins/arch-compliance/hooks/`, the skill prose under
`plugins/arch-compliance/skills/`, the TypeScript bridge under
`plugins/arch-compliance/detectors/typescript/`, the plugin's tests and fixtures under
`plugins/arch-compliance/tests/`, the shipped check-diff action under `.github/actions/`,
and the repository-level `tests/`, `scripts/` and `config/`. The CI diff gate and the PostToolUse hook run the registry's detectors on
changed `.py`, `.ts` and `.tsx` files anywhere in the repository, host guards see every
changed file inside the repository, and rows run where their `call_sites` say; host rows
run only with an approval or, for the diff gate, `--trusted-checkout` (`**Trust
boundary.**`); prose and configuration are held to this file by review. Where a
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
The row runs at `ci` and `precommit` only (`acf-check-diff`; a row declaring `hook` is
refused at load), and `params.baseline` and each `params.roots` entry must name a path
inside the repository, each root an existing directory (`DetectorPackError` otherwise).

## Façade sinks

Optional config-driven rule: forbid direct writes to a protected path regex outside
allowlisted modules. Set `params.target_literal_re` / `allowlist_globs`, then flip
`status` to `enforced`. The row's `id` must be its detector's mandate id
(`facade.forbid-sink`) and the row must declare at least one Tier-1 call site.
Unenforced here: this repository has no `index.yml` façade.

## FSM transitions

Optional config-driven rule: writes to a state field must call a named validator in the
same function scope. Set `params.state_field` / `validator_name`, then enforce. The
row's `id` must be its detector's mandate id (`fsm.transition-guard`) and the row must
declare at least one Tier-1 call site. Unenforced here: this repository has no state
field.

## Soft fail-loud smells

Silent fallbacks and quiet degradation paths that deterministic AST rules cannot catch
may be reviewed via the LLM judge (`llm_fail_loud`).

## React boundaries

Views render and wire UI; data fetching, domain aggregation, and business rules live
outside view components (hooks, services, or loaders). Soft smells that need judgment
are reviewed via the LLM judge (`llm_react_boundaries`) and, in `/architecture-review`,
by the `ui-logic-isolation` rule (the row's `auditor`). Unenforced here: there is no
React app; the TypeScript in this repository is a detector bridge.

## One base exception

Every ACF exception subclasses `AcfError` and nothing else; no stdlib mixin such as
`ValueError` or `KeyError` joins the bases. Source: phase 1b decision. Row:
`plugin.one-base-exception`.

## One owner for host paths

`acf.repo` is the one declaration of where ACF looks inside a host repository and of the
per-user approval store's path relative to the home directory (`STORE_REL`), and it
imports only the standard library and `acf.exceptions` (itself stdlib-only)
(`plugins/arch-compliance/python/acf/repo.py:1-8`).
Row: `plugin.one-owner-host-paths`; its test scans `plugins/arch-compliance/python/` and
`plugins/arch-compliance/hooks/`. The repository-level `tests/` and `scripts/` follow
the rule by importing the `acf.repo` constants, which review checks. Executable skill snippets
follow the rule too, which review checks.

`acf.repo.RepoTree` is the one place runtime code turns a path string into a location in
the host repository: containment (`contained`), an existing file or directory (`file`,
`directory`) and the repository-relative key of a location it returned (`key`). Callers
hand it the string they hold and never join, resolve or compare against the root
themselves. `plugins/arch-compliance/tests/test_repo_tree_guard.py` enforces this over
`plugins/arch-compliance/python/` and `plugins/arch-compliance/hooks/`, outside
`acf/repo.py`. Three functions are allowlisted, each with its reason:
`cli_check_diff.main` and `cli_check_llm.main` resolve the operator's `--mandates`
argument, a file the operator names that may lie outside the repository, and
`scan_typescript_file` resolves the file a gate already chose, to hand the Node
subprocess an absolute path. Blind spots, stated rather than claimed covered: a
repository root held in a variable the guard does not name; paths built by string
concatenation or `os.path.join`; paths passed through attributes. The guard's scope is
runtime code; executable skill snippets are outside it.

## Host detectors and call sites

**Reference syntax.** For an `ast` or `guard` row, a `detector` containing `:` is a host
reference, `<posix_rel_path.py>:<callable_name>`: a relative POSIX path ending in `.py`
inside the repository, and a callable name that is a Python identifier. Any other value
is a built-in detector id.

**`HostHit` contract.** A host callable returns `acf.detectors.host.HostHit` values
(`path`, `line >= 1`, a non-empty `message`), never `Finding`. The runner builds each
`Finding` from the hit and the mandate row, so a host cannot attach a finding to another
row. Every failure raised while the runner calls host code becomes a typed ACF error.
Host `ast` rows declare `languages` in `python`, `typescript` or `both`; host guards see
every changed file inside the repository.

**Call-site rule.** `call_sites` is a closed vocabulary: `ci`, `precommit`, `hook`,
`posttooluse` and `audit`. `ci` and `precommit` are the diff sites
(`acf.registry.DIFF_CALL_SITES`); `hook` and `posttooluse` are two spellings of the one
PostToolUse site (`HOOK_CALL_SITES`); together they are the Tier-1 sites
(`TIER1_CALL_SITES`). `precommit` is the local git-hook site, whichever hook (pre-commit or
pre-push) runs it. `acf-check-diff` requires `--call-site {ci,precommit}` and runs
only rows that are active (not `unenforced`) and declare that site; a site that selects
no active `ast` or `guard` row is refused, not reported as a clean run. The PostToolUse
hook runs rows declaring `hook` or `posttooluse`. A row declaring only `[ci]` is not
reported by the hook or by a `precommit` run. An active `ast` or `guard` row declares at
least one Tier-1 site. `call_sites` select the Tier-1 gate sites and nothing else: the
`auditor` field, not `call_sites`, selects the rows `/architecture-review` reviews, so an
active row with `auditor` set joins the review whatever sites it declares. `audit` keeps
its present meaning, an annotation that a row is held by review rather than by a Tier-1
gate; no package code reads it, and the review neither requires nor reads it.

**Built-in contracts.** `acf.detectors.KNOWN_DETECTORS` maps each built-in `ast` and
`guard` detector id to its mandate id and the sites at which a gate runs it
(`acf.cli_check_diff` re-exports it). `fail_loud_ratchet` runs at `ci` and `precommit`
only; every other built-in runs at every Tier-1 site. An active built-in row must carry
its detector's mandate id and may declare no Tier-1 site at which its detector does not run, and
every built-in mandate id is reserved: no other kind of active row may use one.
`status: partial` gates like `enforced`, so it is held to the same rules; a row whose
detector or prompt does not exist yet is `unenforced`.

**Trust boundary.** Both gates run host code only when `~/.acf/approvals.json` holds an
approval matching the fingerprint of the active host rows and their files, or, for
`acf-check-diff`, when the invocation passes `--trusted-checkout`. The approval is keyed
by the repository's git common directory and the host's prefix inside it (the folder for
a directory that is not a git repository), so it covers every worktree whose host rows
and files match. An agent may start `acf-allow --fingerprint`; the plugin's PreToolUse
hook makes it prompt, and the user's answer is the approval. The PostToolUse hook also
needs `.acf/enabled`; without an approval it runs the built-ins and reports the skipped
host rows, and the diff gate refuses.
Committing `.acf/` approves no host code. The wrapping guarantees typed errors, not
confinement: a host module runs in the gate's process with its privileges.
`load_mandates` never imports host code. In hook mode, gate failures exit `2`.

No row: enforced by plugins/arch-compliance/tests/test_host_detectors.py, test_builtin_detectors.py, test_registry.py, test_hooks.py, test_diff_cli.py, test_approval.py, test_cli_allow.py, test_approval_prompt.py, test_cli_approval_status.py and test_git_runner.py (which pins G1 to G3, behind the repository key).

## Declared, never defaulted

The adversarial-design-review gate's host values are declared by the host in
`config/architecture/adr.yml`; no default stands in for a missing declaration, and a
missing declaration fails loud. The `/architecture-review` host values are declared in
`config/architecture/review.yml` (`report_dir`, `baseline_path`, `baseline_max_age_days`,
`baseline_max_commits`, `packs`, `subsystems`, `exclude`; every field required, and a
missing file fails loud naming `/acf-setup`). The review gives some absent or empty values
a built-in meaning, recorded here: the built-in exclusion list and the built-in test-path
list, both added to by `exclude`, the test-path list alone dropped by `--include-tests`;
an absent `surface`; an empty `subsystems` list, which keeps the first-segment bucketing
rule; no file at `baseline_path`, which omits the drift, staleness and provenance sections
and makes the roll-up say `no baseline (run --update-baseline to set one)`; and an absent
rule setting: every rule settings key is optional, an absent scalar (for example
`exception_base`, `inventory`, `style_schema`, `classifier`) turns off the check that uses
it, and an absent list (for example `surface_exclude`, `docs`, `bindings`) is empty.
Source: phase 1c decision 4,
`plugins/arch-compliance/python/acf/adr/host.py:19-33`. Row:
`plugin.declared-never-defaulted`. `post-merge-housekeeping` gives three absent
`## Post-merge` refinements a built-in meaning, recorded here: an absent plan record,
where step 4 ticks completed steps; an absent filing rule, where steps 6 and 6.5 write
the item into the tracking target; and an absent closing rule, where step 5 updates
status cells. Each is reported as
`<rule>: not declared in ## Post-merge, portable rule applied`. Four defaults elsewhere in the package are outside
this rule and recorded here: the fail-loud ratchet's baseline path when a row omits
`params.baseline` (`plugins/arch-compliance/python/acf/repo.py:33-36`), `resolve_repo`
falling back to the process directory (`plugins/arch-compliance/python/acf/repo.py:45-57`,
documented there as a fallback), the approval key, which is the folder when git reports
the directory is not a repository (`acf.approval.repo_key`; `describe_approval` prints the
scope), and the Tier-2 LLM judge's default provider and models
when `--provider` / `ACF_JUDGE_PROVIDER` or `--model` / `ACF_JUDGE_MODEL` are omitted
(`DEFAULT_PROVIDER = "anthropic"`, `DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-6"`,
`DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"` in
`plugins/arch-compliance/python/acf/judge.py:25-27`; provider API keys are never
defaulted or cross-provider-fallback-resolved). The check-diff action's inputs are outside
the rule too, being action inputs and not host declarations a gate reads, and are recorded
here: `repo` `.`, `trusted-checkout` `true` (the workflow file is the opt-in), `base` derived
from the event (`origin/<github.base_ref>`, else `origin/<default branch>`),
`python-version` `3.12` and `node-version` `22` (`.github/actions/check-diff/action.yml`).
The pre-push step's `ACF_PREPUSH_OPTIONAL` has no default: unset, or any value but `1`,
refuses.

## Prose names no host

Skill prose and runtime messages name no host repository, path or section; a host
reaches the gate only through its declaration and its doctrine. Rows:
`plugin.adr-code-names-no-host` (the gate's package and runtime messages) and
`plugin.gate-prose-names-no-host` (`plugins/arch-compliance/tests/test_adr_skill_prose.py`
checks the two gate skills, `post-merge-housekeeping`, and `architecture-review` with its
rule prompts and technology packs, plus the string constants of
`plugins/arch-compliance/python/acf/review/`, against the enumerated `FORBIDDEN` list of
known origin-host (`HistoricMansions`) vocabulary; the other three skills in
`plugins/arch-compliance/skills/`, `acf-mandate`, `acf-setup` and `acf-approve`, have no row yet).

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
their subprocesses over this repository's own fixtures and are outside it. Two calls
breach the rule today and are declared debt:
`plugins/arch-compliance/python/acf/adr/citations.py:59-61` (`_git`) and
`plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:120-126` (the Node
scanner). Recipe: `grep -rn "text=True" plugins/arch-compliance/python plugins/arch-compliance/hooks`.
The fix and its test are spec `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` §9,
follow-up 1. No row: no test enforces this yet.

## Release discipline

A change to a skill's prose bumps the plugin version in
`plugins/arch-compliance/.claude-plugin/plugin.json` and `pyproject.toml`. Before a gate
or `post-merge-housekeeping` run, the installed copy of the two gate skills,
`post-merge-housekeeping` and `architecture-review` is byte-checked against the clone
(`scripts/check_installed_skills.py`); on a mismatch the plugin is reinstalled from the
clone and the session restarted. The check covers those four skill trees only: the hooks
run the installed copy's `hooks/` and `python/` (`plugins/arch-compliance/hooks/posttooluse_gate.py:22-26`),
which it does not compare. Source: phase 1d spec risk table (cache drift) and 1d plan
Task 8 step 1. Whoever merges a version bump tags its merge commit on `main` `v<version>`,
once `main`'s CI run for that commit has passed, and pushes the tag; hosts pin the
check-diff action to that tag. No row: no test enforces this yet.

## Single point of definition

Lifted: "When the same operation, constant set, or decision procedure … is needed by more
than one module, it must have exactly one canonical implementation that every call site
consumes" (HistoricMansions `GEMINI.md` §7, `hm:GEMINI.md:136`). Current breaches,
recorded not hidden: two git runners, `plugins/arch-compliance/python/acf/diff.py:19`
(`run_git`) and `plugins/arch-compliance/python/acf/adr/citations.py:51` (`_git`),
consolidated in spec `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` §9 follow-up 1;
a skill snippet that by-eyes a package helper,
`plugins/arch-compliance/skills/acf-setup/SKILL.md:137` (by-eye anchor check instead of
`acf.registry.missing_anchors`), tracked in spec
`docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` §9 follow-up 4; and two path-glob
dialects, `acf.repo.path_matches` (the review's target tree) and `fnmatch`
(`plugins/arch-compliance/python/acf/detectors/facade_sinks.py:59`,
`plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:68`), kept apart
because moving the ratchet onto `path_matches` would change what a host's existing
`exclude_globs` means (spec `docs/design/ARCHITECTURE_REVIEW_PORT.md` §10); and three
installs of the plugin and its TypeScript detectors for three environments, kept apart
because merging them would make the `test` job install twice or put pytest in hosts'
runners: `/acf-setup` step 4 (a developer machine), the `test` job in
`.github/workflows/ci.yml` (`.[dev]`, for pytest and the TypeScript self-test) and the
check-diff action (a host's runner, its own virtual environment; spec
`docs/design/CHECK_DIFF_HOST_WIRING.md` §5); the approval command set, encoded twice: the
approval hook's `APPROVAL_NEEDLES` and the `permissions.ask` rules `/acf-setup` offers the
user (the rules live in the user's settings, which the plugin cannot import, so the copy
stays; `plugins/arch-compliance/tests/test_approval_prompt.py` pins the two); the hooks'
`sys.path` insert, now in three hooks (follow-up 3 of
`docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md` §9); and a second
"imports only the standard library" check, the AST walk in `test_approval_prompt.py` beside
the regex in `test_repo_module_imports_only_stdlib`
(`plugins/arch-compliance/tests/test_repo_paths.py:74-78`), which that follow-up folds
into one helper. No row: no test enforces this yet.

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
  `acf.detectors.KNOWN_DETECTORS`, the `acf.repo` constants).

## Post-merge

Host operational declarations read by `post-merge-housekeeping`:

- **Shared-checkout branch lock:** none declared.
- **Worktree daemon probe:** none declared (tests spawn no background server).
- **Post-merge CI workflows:** `.github/workflows/ci.yml` (`test` and `action` jobs on `main`).
- **Durable tracking target:** GitHub Issues on `IanDBallard/arch-compliance-for-superpowers`. **Filing rule:** file with `gh issue create`, so filing a follow-up or guard escape never edits an already-cleared spec.

This repository declares no pre-flight checks, plan record, tracking documents, post-deploy actions or report fields.

No row: host operational declarations; no test enforces this.
