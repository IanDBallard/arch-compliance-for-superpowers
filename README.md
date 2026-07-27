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
acf-check-diff --mode staged        # local: staged or --mode worktree
acf-check-diff --base origin/main   # CI: diff vs merge-base (needs full git history)
pytest
```

`acf-check-diff` scans git-changed `.py` / `.ts` / `.tsx` against the host mandate registry. `BLOCK` findings exit non-zero. In CI use `--base` — a fresh checkout has an empty staged/worktree diff.

The registry drives enforcement: `status: unenforced` rows never gate, severity comes from the registry row, and a finding line can be exempted inline with a reason — `# <token>: reason` (Python) or `// <token>: reason` (TypeScript), using the row's `exemption_tokens`.

## Hooks

Plugin `hooks/hooks.json` registers:

- **SubagentStart** — `inject_constraints.py` injects host mandates + an ARCHITECTURE excerpt into subagent context.
- **PostToolUse** (`Write|Edit|MultiEdit`) — `posttooluse_gate.py` runs Tier-1 detectors on edited `.py`/`.ts`/`.tsx` files. `BLOCK` findings exit 2 so Claude receives them as blocking feedback; `WARN` findings come back as additional context.

Hooks are a true no-op (exit 0, no third-party imports) until `.acf/enabled` exists; with the marker present, a missing `config/architecture/mandates.yml` or missing Python deps fail loud with an actionable message.

## Friend success bar

After `/acf-setup` on a React repo: plant a Tier-1 violation → gate fails; fix it → gate passes — without reading Historic Mansions. Customize with `/acf-mandate`; audit with `/architecture-review`.

## License

[GPL-3.0](LICENSE).
