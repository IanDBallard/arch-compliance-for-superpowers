# Python Service Architecture

Portable starter constraints for Python service hosts. Replace this stub with your
project's real architecture prose; keep the heading strings that mandates anchor on.

## Fail loud

Failures must not disappear. Bare `except:` and broad `except Exception:` handlers that
swallow errors are forbidden unless explicitly exempted with a reason.

## No shims

Do not probe optional attributes with `hasattr` to paper over missing interfaces.
Prefer explicit protocols, typed optionals, or clear control flow.

## POSIX paths

When persisting paths to YAML/JSON, use `Path.as_posix()` — do not `str(path)` path-like
names into dump/serialization payloads.

## Build artifacts

Do not stage or commit generated trees such as `dist/` or `build/`.

## Fail-loud ratchet

Optional whole-tree freeze of bare/broad-except counts. Enable the mandate and commit a
`config/architecture/fail_loud_ratchet.json` baseline (`{"files": {"path.py": N}}`).

## Façade sinks

Optional config-driven rule: forbid direct writes to a protected path regex outside
allowlisted modules. Set `params.target_literal_re` / `allowlist_globs`, then flip
`status` to `enforced`.

## FSM transitions

Optional config-driven rule: writes to a state field must call a named validator in the
same function scope. Set `params.state_field` / `validator_name`, then enforce.

## Soft fail-loud smells

Silent fallbacks and quiet degradation paths that deterministic AST rules cannot catch
may be reviewed via the LLM judge (`llm_fail_loud`).
