# Architecture Compliance Constraints (ACF)

You are working in a host project with Architecture Compliance Framework enabled.
**Host architecture + mandate registry override Superpowers generic defaults** for plan
location, verification commands, fail-loud / no-shim expectations, and related rules.

## Active mandates

{{MANDATES}}

## Architecture excerpt

{{ARCHITECTURE_EXCERPT}}

## Enforcement expectations

- Do not introduce `BLOCK` mandate violations. Fix or exempt with a documented reason token.
- Treat `WARN` findings seriously; prefer fixing over silent workarounds.
- Prefer fail-loud errors over swallowed exceptions, empty catches, and hasattr shims.
- When unsure, re-read host `config/architecture/ARCHITECTURE.md` and `mandates.yml`.
