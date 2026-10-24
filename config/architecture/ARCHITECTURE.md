# Architecture

Portable starter constraints merged by `/acf-setup` from the plugin's react-app and
python-service profiles. This host is polyglot: a Python package and a TypeScript
detector bridge. Replace this stub with the project's real architecture prose; keep the
heading strings that mandates anchor on.

## Fail loud

Errors must surface. Do not swallow failures in empty `catch` blocks or catch bodies
that only comment. Prefer explicit handling, rethrow, or reporting.

Failures must not disappear. Bare `except:` and broad `except Exception:` handlers that
swallow errors are forbidden unless explicitly exempted with a reason.

## No shims

Avoid type escape hatches. Explicit `any` annotations and `as any` assertions hide
contract breaks; prefer typed boundaries and narrow casts when unavoidable.

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

## React boundaries

Views render and wire UI; data fetching, domain aggregation, and business rules live
outside view components (hooks, services, or loaders). Soft smells that need judgment
are reviewed via the LLM judge (`llm_react_boundaries`).
