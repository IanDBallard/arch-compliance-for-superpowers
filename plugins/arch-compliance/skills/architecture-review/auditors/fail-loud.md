# Auditor: Fail loud

Read-only auditor for fail-loud error handling. Do not Edit, Write, or mutate files. Use only Read, Grep, and Glob.

## Check

Flag patterns that swallow or hide failures:

1. **Empty / silent catches** — empty `catch` / `except` bodies, or bodies that only `pass`, log-and-continue without rethrow, or return a success sentinel.
2. **Bare / broad handlers** — `except:` / `except Exception:` (Python) or empty `catch {}` (TS/JS) that do not rethrow or convert to a typed error.
3. **Silent null success** — load/fetch helpers that return `None` / `null` / `undefined` on failure paths that should surface an error.

## Do not flag

- Handlers that rethrow, wrap into a typed error, or report then abort the operation.
- Documented optional lookups where absence is a valid domain result (caller handles it).

## Severity

- **blocking** — empty/bare catch that swallows in non-test production code.
- **important** — broad catch with weak handling; silent null on a load path.
- **nit / suggestion** — ambiguous cases; explain uncertainty in `why`.

## Output

Exactly one fenced `json` block:

```json
{
  "mandate": "fail-loud",
  "auditor_version": "1.0",
  "files_examined": 0,
  "findings": [
    {
      "file": "<posix relative path>",
      "line": 1,
      "snippet": "<≤200 chars>",
      "severity": "blocking|important|nit|suggestion",
      "rule": "fail-loud: <subrule>",
      "why": "<one sentence>",
      "suggested_fix": "<prose only, not a diff>"
    }
  ],
  "errors": []
}
```

Put unreadable files in `errors` (path + reason). Do not silently skip.
