# arch-compliance-for-superpowers

Architecture Compliance Framework (ACF) companion for [Superpowers](https://github.com/obra/superpowers) on Claude Code. Provides a mandate registry, dual TypeScript/Python compliance gates, LLM judge, and audit trail.

## Install

```
/plugin marketplace add IanDBallard/arch-compliance-for-superpowers
/plugin install arch-compliance@arch-compliance-for-superpowers
```

Then run `/acf-setup` in the host repo (writes `config/architecture/` and `.acf/enabled`).

## Hooks

Plugin `hooks/hooks.json` registers:

- **SubagentStart** — `inject_constraints.py` injects host mandates + an ARCHITECTURE excerpt into subagent context.
- **PostToolUse** (`Write|Edit|MultiEdit`) — `posttooluse_gate.py` runs Tier-1 detectors on edited `.py`/`.ts`/`.tsx` files and returns findings.

Hooks no-op until `.acf/enabled` exists; with the marker present, a missing `config/architecture/mandates.yml` fails loud (non-zero).
