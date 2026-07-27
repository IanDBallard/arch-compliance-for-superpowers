# arch-compliance-for-superpowers

Architecture Compliance Framework (ACF) companion for [Superpowers](https://github.com/obra/superpowers) on Claude Code. Provides a mandate registry, dual TypeScript/Python compliance gates, LLM judge, and audit trail.

**Full guide:** [docs/guides/SUPERPOWERS_COMPLEMENT.md](docs/guides/SUPERPOWERS_COMPLEMENT.md)

## Prerequisite

Install **Superpowers** first (`superpowers@claude-plugins-official` or equivalent). ACF complements Superpowers; it does not replace it.

## Install (Claude Code)

```text
/plugin marketplace add IanDBallard/arch-compliance-for-superpowers
/plugin install arch-compliance@arch-compliance-for-superpowers
```

Then in the **host** repo run `/acf-setup` (writes `config/architecture/` and `.acf/enabled`).

### Override contract

Superpowers owns workflow shape. This plugin owns mandates, gates, audit, and constraint injection. Where they conflict, **host architecture + mandate registry win** over Superpowers generics (plan location, verification commands, fail-loud / no-shim expectations).

## Skills

| Skill | Role |
|---|---|
| `/acf-setup` | Bootstrap host `config/architecture/`, enable hooks marker, smoke the diff gate |
| `/acf-mandate` | Add / edit / deprecate rows in `mandates.yml` |
| `/architecture-review` | Faceted audit + optional baseline / drift |

## Environment variables

For the Tier-2 LLM judge (required when enforced `detection: llm` mandates are active):

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Preferred Gemini API key |
| `GOOGLE_API_KEY` | Accepted fallback |

Missing both → hard fail for enforced LLM mandates (no silent skip).

## Local Python package

From this repo root (developers / CI):

```bash
pip install -e ".[dev]"
acf-check-diff --mode staged   # or --mode worktree
pytest
```

`acf-check-diff` scans git-changed `.py` / `.ts` / `.tsx` against the host (or fixture) mandate registry. `BLOCK` findings exit non-zero.

## Hooks

Plugin `hooks/hooks.json` registers:

- **SubagentStart** — `inject_constraints.py` injects host mandates + an ARCHITECTURE excerpt into subagent context.
- **PostToolUse** (`Write|Edit|MultiEdit`) — `posttooluse_gate.py` runs Tier-1 detectors on edited `.py`/`.ts`/`.tsx` files and returns findings.

Hooks no-op until `.acf/enabled` exists; with the marker present, a missing `config/architecture/mandates.yml` fails loud (non-zero).

## Friend success bar

After `/acf-setup` on a React repo: plant a Tier-1 violation → gate fails; fix it → gate passes — without reading Historic Mansions. Customize with `/acf-mandate`; audit with `/architecture-review`.
