# React App Architecture

Portable starter constraints for TypeScript/React hosts. Replace this stub with your
project's real architecture prose; keep the heading strings that mandates anchor on.

## Fail loud

Errors must surface. Do not swallow failures in empty `catch` blocks or catch bodies
that only comment. Prefer explicit handling, rethrow, or reporting.

## No shims

Avoid type escape hatches. Explicit `any` annotations and `as any` assertions hide
contract breaks; prefer typed boundaries and narrow casts when unavoidable.

## React boundaries

Views render and wire UI; data fetching, domain aggregation, and business rules live
outside view components (hooks, services, or loaders). Soft smells that need judgment
are reviewed via the LLM judge (`llm_react_boundaries`).
