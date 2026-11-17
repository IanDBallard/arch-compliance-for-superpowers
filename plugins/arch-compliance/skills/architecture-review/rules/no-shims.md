# Rule: no-shims

**Principle.** No compatibility branches, soft fallbacks, internal retries or
migration shims. When a contract changes, every caller moves; nothing papers over the
break.

## Settings

- `surface`, `surface_exclude`: already applied by the controller; you audit the
  row's surface as given.
- `docs`: documents to read in full before auditing (for example a migration plan
  that names a shim's removal date).
- `exempt_paths`: path patterns of files where version or platform sniffing is the
  file's job (bootstrap, environment layout, CI tooling). In a file matching one of
  `{exempt_paths}`, do not flag version sniffing (check 4); every other check still
  applies there. When empty, no file is exempt.

An absent scalar turns its check off; an absent list is empty.

## Flag

1. **Compatibility branches.** Dispatch keyed on an old type or a legacy attribute:
   `isinstance(x, LegacyThing)`, `hasattr(x, "legacy_field")`, a check for a field
   that only an old payload shape carries, a schema or format version switch that
   keeps more than one live shape.
2. **Soft fallbacks.** A handler or conditional that returns a degraded default so the
   system continues in a wrong state instead of failing (`except ...: return {}`,
   `value ?? oldValue`, "try the new path, else the old one").
3. **Internal retries.** A retry loop (`for _ in range(n)`, `while attempts < n`, a
   retry decorator or helper) around an in-process call. Retries belong only at real
   external boundaries.
4. **Version sniffing.** `sys.version_info`, a package `__version__` check, a runtime
   feature probe or user-agent switch that selects behaviour, outside `{exempt_paths}`.
5. **Explicit shims.** Comments or names that say so: "remove after migration",
   "legacy path", "back-compat", "shim", "deprecated alias", a re-export kept for old
   importers.
6. **Type escape hatches.** `any`, `as any`, `# type: ignore` or an unchecked cast used
   to push an incompatible value across a shared boundary.

## Do not flag

- A retry with a timeout around genuine external I/O (network, a remote service, a
  transiently locked file).
- A narrow, documented cast at a single serialisation boundary.
- Version handling whose subject is an external input format the repository does not
  own and must accept (say so in `why` if you are unsure, as a `suggestion`).

## Severity

- `blocking`: a retry loop around an in-process call; a type-sniffing compatibility
  branch; an escape hatch hiding a broken contract at a shared boundary.
- `important`: an explicit shim comment or alias; a soft fallback returning a sentinel
  on a failure path.
- `nit`: version sniffing in a low-risk, tooling-only path.
- `suggestion`: a branch that may be a shim but needs human judgment; name the
  ambiguity in `why`.

## Examples

```python
for attempt in range(3):
    result = normalise(text)        # blocking: in-process call retried
    if result:
        break
```

```python
for attempt in range(3):
    response = session.get(url, timeout=5)   # not flagged: network boundary
    if response.ok:
        break
```
