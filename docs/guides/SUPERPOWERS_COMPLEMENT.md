# Superpowers Complement Guide

Architecture Compliance Framework (ACF) is a **Claude Code marketplace plugin** that complements [Superpowers](https://github.com/obra/superpowers). Superpowers owns workflow *shape* (planning, subagent dispatch, verification rituals). This plugin owns mandate *content*, enforcement gates, audit, and constraint injection.

## Install order

1. **Install Superpowers first** (official or your marketplace equivalent), for example:

   ```text
   /plugin install superpowers@claude-plugins-official
   ```

2. **Then** add this marketplace and install the plugin:

   ```text
   /plugin marketplace add IanDBallard/arch-compliance-for-superpowers
   /plugin install arch-compliance@arch-compliance-for-superpowers
   ```

3. In the **host** repo, run `/acf-setup` (writes `config/architecture/` and `.acf/enabled`).

Do not run `/acf-setup` until Superpowers is installed. ACF is a companion, not a replacement.

## Override contract

When both Superpowers and ACF are installed:

| Concern | Owner |
|---|---|
| Workflow skills (`writing-plans`, subagent dispatch, verification rituals) | Superpowers |
| Mandate registry, detectors, LLM judge, audit, constraint injection | This plugin |
| Plan location, DoD / verification commands, fail-loud / no-shim expectations | **Host architecture + registry win** |

Where plugin defaults or injected constraints conflict with Superpowers generics, **host `ARCHITECTURE.md` + `config/architecture/mandates.yml` win**. Hooks inject that contract into SubagentStart so implementers see host rules, not only Superpowers prose.

## Skills

| Skill | Role |
|---|---|
| `/acf-setup` | Detect languages; copy matching profile(s) into host `config/architecture/`; point at `ARCHITECTURE.md`; write `.acf/enabled`; print pre-commit/CI snippets; smoke `acf-check-diff`. |
| `/acf-mandate` | Add / edit / deprecate registry rows with schema validation. Does not generate detector code. |
| `/architecture-review` | Tier-3 audit + optional baseline / drift report. |

## Environment variables

Tier-2 LLM judge (Gemini by default) needs a key when any mandate is `status: enforced` and `detection: llm`:

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Preferred Gemini API key |
| `GOOGLE_API_KEY` | Accepted fallback |

If neither is set (and no explicit judge provider is wired), the gate **hard-fails** — no silent skip of enforced LLM mandates.

Deterministic Tier-1 gates (`acf-check-diff`, PostToolUse) do not require these keys.

## Friend success bar (React)

A Claude Code user who already has Superpowers should be able to:

1. Install this marketplace plugin.
2. Run `/acf-setup` on a React / TypeScript app (no Historic Mansions internals).
3. Plant a known Tier-1 violation (for example an empty `catch` that swallows errors).
4. See `acf-check-diff` (or the PostToolUse hook) **fail**.
5. Fix the violation and see the gate **pass**.
6. Optionally customize mandates with `/acf-mandate` and run `/architecture-review`.

That path is the ship bar for “friend can use this without reading HM.”

## Local development (this repo)

From the marketplace repo root:

```bash
pip install -e ".[dev]"
acf-check-diff --mode worktree      # local working-tree diff
acf-check-diff --base origin/main   # CI: diff vs merge-base
pytest
```

Plugin hooks live under `plugins/arch-compliance/hooks/hooks.json` and invoke `python` — ensure `python` on PATH is Python 3.11+ with the `acf` package installed. Hooks are a true no-op until the host has `.acf/enabled`; with that marker present, a missing `config/architecture/mandates.yml` or missing Python deps fail loud. The PostToolUse gate exits 2 on `BLOCK` findings so Claude receives them as blocking feedback. Enforcement follows the host registry: `unenforced` rows never gate, severity comes from the row, and `exemption_tokens` work as inline `# token: reason` / `// token: reason` comments.

## Related docs

- Design: [`docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md`](../design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md)
- Implementation plan: [`docs/plans/PLAN_ARCH_COMPLIANCE_FOR_SUPERPOWERS.md`](../plans/PLAN_ARCH_COMPLIANCE_FOR_SUPERPOWERS.md)
