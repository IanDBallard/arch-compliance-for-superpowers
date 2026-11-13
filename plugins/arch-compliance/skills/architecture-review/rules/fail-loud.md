# Rule: fail-loud

**Principle.** Errors halt and report. No broad catch that swallows a failure, no
silent success default on a failure path, no interface probing in place of typed
dispatch.

## Settings

- `surface`, `surface_exclude`: already applied by the controller; you audit the
  row's surface as given.
- `docs`: documents to read in full before auditing (for example a list of documented
  optional lookups).
- `exception_base`: `{class_name, module}`, the repository's root exception type and
  the module that declares it. When set, read `{module}` once at the start and note
  every class that derives from `{class_name}` there. When absent, the exception-base
  check is off.

An absent scalar turns its check off; an absent list is empty.

## Flag

1. **Bare or broad handlers that swallow.** A catch-all handler (`except:`,
   `except Exception:`, `catch (e) {}`, `.catch(() => {})`) whose body passes,
   returns a success-shaped default (`None`, `[]`, `{}`, `null`, `false`), assigns a
   fallback, or logs and continues, without re-raising or converting to a typed error.
2. **Silent null success.** A load, fetch, find or get operation whose failure branch
   (not found, unreadable, invalid) returns `None`/`null`/`undefined` so the caller
   proceeds as if nothing went wrong.
3. **Interface probing.** `hasattr(...)`, `getattr(x, name, default)` or
   `"name" in obj` used as the condition that chooses behaviour, where a typed variant
   or a declared interface should decide.
4. **Exception outside the declared base** (only with `exception_base` set). A new
   exception class whose bases do not include `{class_name}` or one of its
   descendants.

## Do not flag

- A handler that re-raises, wraps into a typed error, or reports and then aborts the
  operation.
- A documented optional lookup where absence is a valid domain answer and the caller
  handles it (the docstring or type says so; it is not a load).
- A narrow handler for one named exception that the code then handles fully.
- Probing in a logging or diagnostic branch that chooses no behaviour (at most `nit`).

## Severity

- `blocking`: a bare or broad handler that swallows in non-test code; an exception
  class outside `{class_name}`; probing in a dispatch position.
- `important`: a broad handler with weak handling (logs, then continues on a degraded
  value); silent null on a load or fetch path.
- `nit`: probing outside a dispatch position.
- `suggestion`: a pattern that may break the rule but needs human judgment; name the
  ambiguity in `why`.

## Examples

```python
try:
    record = load_record(record_id)
except Exception:
    record = None          # blocking: swallowed, caller proceeds
```

```python
try:
    do_work()
except Exception:
    log.exception("work failed")
    raise                  # not flagged: re-raised
```
