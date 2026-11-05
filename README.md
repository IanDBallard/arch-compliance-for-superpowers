# arch-compliance-for-superpowers

Architecture Compliance Framework (ACF) companion for [Superpowers](https://github.com/obra/superpowers) on Claude Code. Provides a mandate registry, dual TypeScript/Python compliance gates, LLM judge, and audit trail.

**Full guide:** [docs/guides/SUPERPOWERS_COMPLEMENT.md](docs/guides/SUPERPOWERS_COMPLEMENT.md)

## Prerequisites

- **Superpowers** installed first (`superpowers@claude-plugins-official` or equivalent). ACF complements Superpowers; it does not replace it.
- **`python` (3.11+) on PATH** — hooks invoke `python`, not `python3`. On macOS/Linux make sure `python` resolves to Python 3 (venv, conda, pyenv, or `python-is-python3`), with the `acf` package installed into it (see below).
- **Node.js** — only for TypeScript hosts; `/acf-setup` runs `npm ci` in the plugin's `detectors/typescript/` directory.

## Install (Claude Code)

```text
/plugin marketplace add IanDBallard/arch-compliance-for-superpowers
/plugin install arch-compliance@arch-compliance-for-superpowers
```

Then in the **host** repo run `/acf-setup` (writes `config/architecture/` and `.acf/enabled`).

### Override contract

Superpowers owns workflow shape. This plugin owns mandates, gates, audit, and constraint injection. Where they conflict, **host architecture + mandate registry win** over Superpowers generics (plan location, verification commands, fail-loud / no-shim expectations). The `adversarial-design-review` skill is one such override: it is a gate between Superpowers' brainstorming and writing-plans steps, run where the host's doctrine requires it.

## Skills

| Skill | Role |
|---|---|
| `/acf-setup` | Bootstrap host `config/architecture/`, enable hooks marker, smoke the diff gate |
| `/acf-mandate` | Add / edit / deprecate rows in `mandates.yml` |
| `/architecture-review` | Faceted audit + optional baseline / drift |
| `/adversarial-design-review` | Spec-stage adversarial review gate; the host declares `config/architecture/adr.yml` |
| `/responding-to-adversarial-review` | Answering a blocked adversarial-design-review gate run |
| `/post-merge-housekeeping` | Post-merge verification, worktree/branch teardown, doc reconciliation, and ADR ledger amendment |

## Environment variables

For the Tier-2 LLM judge (required when enforced `detection: llm` mandates are active):

| Variable | Purpose |
|---|---|
| `ACF_JUDGE_PROVIDER` | Judge provider: `anthropic` (default) or `gemini` (overridden by `--provider`) |
| `ACF_JUDGE_MODEL` | Optional model override (default: `claude-sonnet-4-6` for `anthropic`, `gemini-2.0-flash` for `gemini`; overridden by `--model`) |
| `ANTHROPIC_API_KEY` | Required API key when provider is `anthropic` |
| `GEMINI_API_KEY` | Preferred Gemini API key when provider is `gemini` |
| `GOOGLE_API_KEY` | Accepted Gemini API key when `GEMINI_API_KEY` is unset and provider is `gemini` |

Missing the active provider's key → hard fail for enforced LLM mandates (no silent skip and no cross-provider fallback).

## Local Python package

From this repo root (developers / CI):

```bash
pip install -e ".[dev]"
acf-check-diff --mode staged --call-site precommit        # local: staged or --mode worktree
acf-check-diff --base origin/main --call-site ci          # CI: diff vs merge-base (needs full git history)
pytest
```

`acf-check-diff` scans git-changed `.py` / `.ts` / `.tsx` against the host mandate registry, and host guards see every changed file inside the repository. `--call-site {ci,precommit}` is required: the gates run the active rows whose `call_sites` declare that site. `BLOCK` findings exit non-zero. In CI use `--base` — a fresh checkout has an empty staged/worktree diff.

Portable Python detectors (enable via profile / `/acf-mandate`):

| Detector id | Mandate id | Call sites | Notes |
|---|---|---|---|
| `fail_loud_bare_except` | `fail-loud.bare-except` | `ci`, `precommit`, `hook`, `posttooluse` | AST |
| `no_shims_hasattr` | `no-shims.hasattr` | `ci`, `precommit`, `hook`, `posttooluse` | AST |
| `posix_paths_str_serialization` | `posix-paths.str-serialization` | `ci`, `precommit`, `hook`, `posttooluse` | AST |
| `no_build_artifacts` | `ops.no-build-artifacts` | `ci`, `precommit`, `hook`, `posttooluse` | Guard; `params.path_prefixes` |
| `fail_loud_ratchet` | `fail-loud.ratchet` | `ci`, `precommit` | Guard; needs baseline JSON; never runs at the hook |
| `forbid_facade_sink` | `facade.forbid-sink` | `ci`, `precommit`, `hook`, `posttooluse` | Config AST; `params.target_literal_re` |
| `fsm_transition_guard` | `fsm.transition-guard` | `ci`, `precommit`, `hook`, `posttooluse` | Config AST; `params.state_field` / `validator_name` |

The call-sites column is each built-in's contract in `acf.detectors.KNOWN_DETECTORS`; an active row for a built-in must carry that mandate id and declare no Tier-1 site at which its detector does not run. `plugins/arch-compliance/tests/test_builtin_detectors.py` pins this table to that map. A host can also run its own detector: an `ast` or `guard` row whose `detector` is `<path>.py:<callable>` (a file inside the repository), returning `HostHit` values.

The registry drives enforcement: `status: unenforced` rows never gate; `enforced` and `partial` both gate (partial means coverage is incomplete, not advisory-only), and a row gates only at the call sites it declares (a `[ci]`-only row is not reported by the PostToolUse hook or by a `--call-site precommit` run). Severity comes from the registry row. Inline exemptions use only the row's `exemption_tokens` — `# <token>: reason` (Python) or `// <token>: reason` (TypeScript). Detectors emit raw findings; they do not interpret exemption comments.

### `acf.adr` — the adversarial-design-review gate

The gate's Python package lives here: claim and payload models, outcome
classification, citation resolution, convergence grouping, the efficacy ledger
and the run-detail writer. The persisted ledger format is the one a host
already has, so an existing ledger stays readable.

**The gate's skills live here too** (`skills/adversarial-design-review/`,
`skills/responding-to-adversarial-review/`). A host enables them by writing
`config/architecture/adr.yml` (`runs_dir`, `ledger_path`) and keeping its doctrine
at `config/architecture/ARCHITECTURE.md`, which may point to other documents; a
pointer still carries every heading its mandates' `arch_anchor` values name.

**This repository is a host of its own gate.** It declares
`config/architecture/adr.yml`, keeps its doctrine and registry under
`config/architecture/`, and records its reviews under `docs/reviews/` (spec
`docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md`). Specs about the plugin are
written, reviewed and recorded here.

The origin host's skill-install tests (which assert its `.claude/` and
`.cursor/` skill trees are byte-identical) are deliberately not ported: they
test a property of a host, not of this plugin, and mean nothing here.

## Hooks

Plugin `hooks/hooks.json` registers:

- **SubagentStart** — `inject_constraints.py` injects host mandates + an ARCHITECTURE excerpt into subagent context.
- **PostToolUse** (`Write|Edit|MultiEdit`) — `posttooluse_gate.py` runs the active rows declaring `hook` or `posttooluse` on edited `.py`/`.ts`/`.tsx` files, and host guards on every edited path inside the repository (edited files outside the repository are not scanned). `BLOCK` findings exit 2 so Claude receives them as blocking feedback; `WARN` findings come back as additional context.

Hooks are a true no-op (exit 0, no third-party imports) until `.acf/enabled` exists; with the marker present, a missing `config/architecture/mandates.yml` or missing Python deps fail loud with an actionable message.

### Upgrading a host installed before `--call-site` (v0.2.3)

- `acf-check-diff` now requires `--call-site {ci,precommit}`; add it to your pre-commit and CI configuration (omitting it exits 2 with a usage error).
- Registries copied from a profile before this release declare no `precommit` site on their `ast`/`guard` rows (typically `[ci, hook]`). Add `precommit` to each row you want checked in pre-commit, or your `--call-site precommit` run is refused ("selects no active" mandate, exit 1), never a silent pass.
- Set `status: unenforced` on any `partial` row whose detector or prompt does not exist yet; an active (`enforced` or `partial`) row naming a missing one is refused when the registry loads.
- Load-time refusals also cover a `call_sites` value outside `ci`, `precommit`, `hook`, `posttooluse`, `audit` (for example `pre-commit` is refused; use `precommit`), an active `ast`/`guard` row whose only site is `audit`, and an active non-built-in row that reuses a built-in mandate id (reserved).

## Friend success bar

After `/acf-setup` on a React repo: plant a Tier-1 violation → gate fails (`acf-check-diff --call-site precommit`, or the PostToolUse hook); fix it → gate passes — without reading Historic Mansions. Customize with `/acf-mandate`; audit with `/architecture-review`.

## License

[GPL-3.0-or-later](LICENSE).
