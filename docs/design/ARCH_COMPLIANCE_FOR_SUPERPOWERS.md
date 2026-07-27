# Architecture Compliance for Superpowers — Design Spec

**Status:** Approved design (brainstorming complete) — pending implementation plan.  
**Author:** Cursor agent with project owner.  
**Date:** 2026-07-27.  
**Repo:** `IanDBallard/arch-compliance-for-superpowers`  
**Local path:** `c:\Users\iball\Projects\arch-compliance-for-superpowers`

## Purpose

Ship a **Claude Code marketplace plugin** that complements [Superpowers](https://github.com/obra/superpowers) the way Historic Mansions’ Architecture Compliance Framework (ACF) does in-repo: Superpowers owns workflow *shape*; this plugin owns mandate *content*, enforcement gates, audit, and constraint injection.

Target user: a Claude Code terminal-first developer (React/TypeScript primary, Python also supported) who already installs Superpowers via `/plugin install`.

## Problem statement

Superpowers skills (`writing-plans`, `subagent-driven-development`, `verification-before-completion`, etc.) are intentionally generic. Without a project-specific compliance spine:

1. Mandates live only in prose and drift from whatever detectors exist.
2. Implementer subagents start without architecture constraints.
3. “Done” is not tied to a machine-checkable mandate registry.
4. Debt stays unquantified — no coverage map, baseline, or drift.

Historic Mansions solved this with a four-tier ACF tightly coupled to `GEMINI.md` and HM-specific façades. Friends need the **same spine**, not the HM domain rules.

## Goals

1. Installable Claude Code marketplace + plugin (`/plugin marketplace add` → `/plugin install`).
2. Four-tier ACF spine: mandate registry → deterministic dual packs → full LLM judge → audit + baseline/drift.
3. Equal **TypeScript/React** and **Python** detector packs.
4. First-class skills: `/acf-setup`, `/acf-mandate`, `/architecture-review`.
5. Hooks that inject host-project constraints into Superpowers subagent flows and optionally gate PostToolUse edits.
6. Example profiles that are **not** Historic Mansions–locked; host projects own `mandates.yml` + architecture prose.

## Non-goals (v1)

- No auto-remediation of findings.
- No Cursor marketplace packaging (Claude-first; Cursor can follow later).
- No HM-specific three-tier / ContentMetadataService / family-template detectors in default packs.
- No CI-blocking compliance ratchet (baseline/drift is report-first).
- No silent skip when an enforced `detection: llm` mandate runs without a configured judge.

## Governing principles (portable)

These are plugin invariants, not HM copy-paste:

1. **Fail loud** — typed errors; no bare swallow; no silent empty defaults for registry/config load.
2. **No shims** — one registry façade; one finding schema; do not dual-run parallel mandate lists.
3. **POSIX paths** in committed YAML/JSON (`.as_posix()` / forward slashes).
4. **Registry is the spine** — prose anchors, detectors, auditors, and call sites must agree or tests fail.
5. **Superpowers override contract** — where this plugin’s plan/DoD/constraint defaults conflict with Superpowers generics, the host architecture + registry win; document that explicitly.

## Architecture

### Repo & install shape

```text
arch-compliance-for-superpowers/
├── .claude-plugin/marketplace.json
├── README.md
├── docs/
│   ├── design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md   # this spec
│   └── guides/…                                    # Superpowers complement, setup
└── plugins/arch-compliance/
    ├── .claude-plugin/plugin.json
    ├── skills/
    │   ├── acf-setup/
    │   ├── acf-mandate/
    │   └── architecture-review/
    ├── hooks/                    # SubagentStart / PostToolUse
    ├── scripts/                  # check-diff, check-llm, audit helpers
    ├── config/                   # registry schema + bundled examples
    ├── detectors/
    │   ├── python/
    │   └── typescript/
    └── profiles/
        ├── react-app/
        └── python-service/
```

**Friend install:**

```text
/plugin marketplace add IanDBallard/arch-compliance-for-superpowers
/plugin install arch-compliance@arch-compliance-for-superpowers
```

Prerequisite: Superpowers installed (`superpowers@claude-plugins-official` or equivalent).

### Tier 0 — Mandate registry

Host project file (default): `config/architecture/mandates.yml`.

Each row declares at least:

| Field | Meaning |
|---|---|
| `id` | Stable mandate id (e.g. `fail-loud.bare-except`) |
| `title` | Short title |
| `severity` | `BLOCK` \| `WARN` |
| `detection` | `ast` \| `llm` \| `grep` \| `guard` \| `manual` |
| `detector` | Detector fn / guard module / LLM prompt id |
| `languages` | `python` \| `typescript` \| `both` \| `none` |
| `call_sites` | e.g. `precommit`, `ci`, `posttooluse`, `audit` |
| `exemption_tokens` | Tokens recognized in `# mandate-ok:` style comments |
| `status` | `enforced` \| `partial` \| `unenforced` |
| `arch_anchor` | Heading/anchor in host `ARCHITECTURE.md` (or equivalent) |

Single Pydantic-validated loader is the only read façade for mandate metadata.

A **drift test** fails when example/profile prose anchors, registry rows, and registered detector ids disagree.

### Tier 1 — Deterministic engine (dual packs)

Shared finding schema:

```text
{mandate_id, severity, path, line, message, detector, confidence?}
```

Paths in findings and baselines use POSIX form.

**Python pack (equal peer):** AST/path rules for portable fail-loud / no-shim / path-style smells (bare `except`, silent broad catches, `hasattr` interface probing, backslash paths in committed YAML/JSON). Extension points for project-specific detectors.

**TypeScript/React pack (equal peer):** portable rules for React/TS codebases (e.g. empty catch swallows, `any` escape hatches where configured, forbidden path style in committed config, detectable “logic in view” patterns that can be made deterministic). Extension points for project-specific detectors.

Diff-scoped scanning is the default for commit/CI gates. `BLOCK` findings are authoritative.

Config resolution always prefers the **host project** paths produced by `/acf-setup`, not the plugin’s bundled profile copies (bundled profiles are templates only).

### Tier 2 — LLM judgment layer (full)

- Provider interface; **Gemini default**; API key via environment.
- Confidence-gated: high confidence → `BLOCK`, else `WARN` (threshold configurable).
- Calibration fixtures for both Python and TS/React soft smells; document precision/recall honesty.
- If a mandate is `status: enforced` and `detection: llm` but the judge is not configured, the gate **hard-fails** (no silent skip).

### Tier 3 — Audit + baseline/drift

`/architecture-review`:

- Facet selection from registry (`--mandates`).
- Scope selection (`--paths`, include-tests flag).
- Parallel auditors driven by registry facets / prompt files.
- Writes a Markdown report; optional `--update-baseline` writes machine-readable baseline JSON.
- Drift vs baseline is **report-only** in v1 (no CI ratchet).

### Claude skills (v1)

| Skill | Role |
|---|---|
| `/acf-setup` | Detect languages; copy matching profile into host `config/architecture/`; help point at `ARCHITECTURE.md`; wire hooks + optional pre-commit/CI snippets; smoke `check-diff`. |
| `/acf-mandate` | Add/edit/deprecate registry rows with schema validation; set detection/severity/status; remind which detector/auditor stubs still need code. Not full detector codegen. |
| `/architecture-review` | Tier 3 audit + baseline/drift. |

### Hooks

| Hook | Behavior |
|---|---|
| SubagentStart (or Task-equivalent) | Inject host-project constraints derived from registry / architecture prose so Superpowers implementers see mandates. |
| PostToolUse | Diff-scoped Tier 1 on edited `.py` / `.ts` / `.tsx` (and configured config paths); feed findings into the turn. |

### Superpowers complement contract

Document in README + a short guide:

- Superpowers = workflow skills.
- This plugin = mandate registry, gates, auditors, constraint injection.
- Host architecture + registry override Superpowers generic defaults for plan location, verification commands, and fail-loud/no-shim expectations when both are installed.

## Profiles

Bundled starters (templates, not runtime defaults after setup):

- `profiles/react-app/` — React/TS-oriented mandate set + sample `ARCHITECTURE.md` stubs.
- `profiles/python-service/` — Python-oriented mandate set + stubs.

A dual-language host may merge both via `/acf-setup`.

## Error handling

- Missing/malformed `mandates.yml` → typed load error, non-zero CLI exit.
- Unknown mandate id in `/architecture-review --mandates` → hard fail.
- Unknown detector id referenced by an enforced row → drift/registry validation fail.
- Unconfigured LLM judge with enforced llm mandates → hard fail at judge call site.
- Empty target tree for audit → hard fail with glob/cwd context.

## Verification / Definition of Done (design-level)

Before calling the plugin shippable:

1. Unit tests for registry loader, finding schema, Python pack, TypeScript pack.
2. CLI smoke tests of `check-diff` against fixture trees (planted violations fail; clean trees pass).
3. LLM judge unit/integration tests with fixtures + calibration notes.
4. Plugin install smoke via `claude --plugin-dir ./plugins/arch-compliance`.
5. Documented `/plugin marketplace add IanDBallard/arch-compliance-for-superpowers` path after GitHub publish.
6. Friend success bar: after `/acf-setup` on a React repo, planted violation fails the gate, fix passes — without reading Historic Mansions.

## Friend success bar

A Claude Code user who already has Superpowers can install this marketplace plugin, run `/acf-setup` on a React app, customize mandates with `/acf-mandate`, and use `/architecture-review` plus commit/CI gates without copying Historic Mansions internals.

## Open implementation notes (non-blocking for this spec)

- Exact TS parser/tooling choice (e.g. tree-sitter vs ts-morph vs ESLint custom rules invoked from Python/Node CLI) is an implementation plan decision; packs must remain equal peers in the registry.
- Marketplace name string in `marketplace.json` should match install docs (`arch-compliance-for-superpowers`).
- GitHub repo visibility: public preferred so the friend can add the marketplace without special access (confirm at publish time).
