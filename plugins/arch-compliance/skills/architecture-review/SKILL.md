---
name: architecture-review
description: Use when running /architecture-review, auditing host architecture compliance across facets, comparing drift to docs/architecture/compliance_baseline.json, or updating that baseline with --update-baseline.
---

# /architecture-review

Codebase-wide architectural-conformance audit for the **host** repo. Read-only auditors; controller may write the report and optional baseline.

**Prerequisite:** Host has been bootstrapped with `/acf-setup` (registry at `config/architecture/mandates.yml`). Superpowers must be installed (parallel dispatch uses `dispatching-parallel-agents`).

## Invocation

`/architecture-review [--paths <glob>] [--include-tests] [--mandates <id,...>] [--update-baseline]`

| Flag | Meaning |
|------|---------|
| `--paths <glob>` | Replace default include set. Cache/build/worktree exclusions still apply. |
| `--include-tests` | Drop test-path exclusions. |
| `--mandates <id,...>` | Comma-separated **mandate registry ids**. Run only auditors covering those mandates. Unknown id → `UnknownMandateError` (hard fail). Omit = all known auditors with matching registry facets. |
| `--update-baseline` | After the run, write aggregated counts to `docs/architecture/compliance_baseline.json`. Without it, baseline is read-only input for drift. |

## Host paths

```text
<host>/config/architecture/mandates.yml
<host>/config/architecture/ARCHITECTURE.md
<host>/docs/architecture/ARCHITECTURE_REVIEW_<YYYY-MM-DD>.md   # report output
<host>/docs/architecture/compliance_baseline.json              # optional baseline
```

Plugin auditor prompts (relative to plugin root / `${CLAUDE_PLUGIN_ROOT}`):

```text
skills/architecture-review/auditors/fail-loud.md
skills/architecture-review/auditors/no-shims.md
skills/architecture-review/auditors/posix-paths.md
skills/architecture-review/auditors/react-boundaries.md
```

## Checklist

1. Resolve host registry + mandate facet filter
2. Resolve target file tree (fail loud if empty)
3. Map selected mandates → auditor prompt files
4. Dispatch parallel read-only auditors
5. Parse payloads; assemble findings
6. Compute report-only drift vs baseline
7. Write Markdown report under `docs/architecture/`
8. Optionally `--update-baseline`
9. Print terminal roll-up

## Step 1 — Resolve mandates / facets

Load host registry only:

```python
from pathlib import Path
from acf.registry import load_mandates
from acf.exceptions import UnknownMandateError

reg = load_mandates(Path("config/architecture/mandates.yml"))
```

If `--mandates` is set, split on commas and strip. For each id:

- If `id not in reg.by_id` → raise `UnknownMandateError` with the bad id (hard fail; do not continue).
- Collect selected mandate rows.

If `--mandates` omitted, use all registry rows that declare an `auditor` field (or the default auditor set below when mapping by facet name).

**Default auditors (v1):** `fail-loud`, `no-shims`, `posix-paths`, `react-boundaries`.

Resolve which auditors to run:

- Prefer mandate `auditor` values for selected rows.
- Also include an auditor when its facet name matches a selected mandate id prefix / known mapping (e.g. `fail-loud.*` → `fail-loud`).
- Deduplicate auditor names. Unknown auditor prompt file → hard fail with the missing path.

## Step 2 — Resolve target tree

Default includes: `**/*.{py,ts,tsx,js,jsx,yml,yaml,json}` (adjust if host is clearly single-language).

Default exclusions: `tests/`, `test_*.py`, `*_test.py`, `**/*.test.*`, `**/*.spec.*`, `.venv/`, `__pycache__/`, `node_modules/`, `.worktrees/`, `worktrees/`, `dist/`, `build/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`, `.git/`.

Apply `--paths` to replace includes; `--include-tests` to drop test exclusions.

If the resolved set is empty → raise `EmptyTargetTreeError` with glob + cwd. Cap lists at ~4000 paths; all paths POSIX (`Path.as_posix()`).

**react-boundaries** may prefer TS/TSX/JSX (and related frontend) files when present; other auditors use the full resolved set (or language-appropriate subsets).

## Step 3 — Dispatch parallel auditors

Use Superpowers **`dispatching-parallel-agents`**: one read-only sub-agent per auditor name.

Each agent receives:

1. Full contents of `skills/architecture-review/auditors/<name>.md`
2. The resolved file list (POSIX paths)
3. Tool allowlist: `Read`, `Grep`, `Glob` only — **no** `Edit`, `Write`, or mutating shell

Do not mutate the tree during audit. Controllers write only the report / baseline after agents return.

## Step 4 — Parse payloads

Expect each auditor’s final message to contain exactly one fenced `json` block with findings (file, line, severity, why, suggested_fix prose). On malformed payload: mark that auditor `FAILED`, keep raw text + error, continue others; final exit non-zero if any failed.

Map auditor findings into shared `acf.finding.Finding` rows where possible (`mandate_id`, POSIX `path`, `line`, `message`, `detector` = auditor name).

## Step 5 — Drift (report-only, before render)

```python
from datetime import date
from pathlib import Path
from acf import baseline as bl

current = bl.aggregate(findings)
baseline_path = Path("docs/architecture/compliance_baseline.json")
drift_section = None
drift_line = None
if baseline_path.is_file():
    base = bl.load_baseline(baseline_path)  # fail-loud on malformed
    report = bl.compute_drift(current, base)
    drift_section = bl.render_drift_section(report, base)
    drift_line = bl.format_drift_line(report, base.commit)

if update_baseline:  # --update-baseline
    snapshot = bl.Baseline(
        generated_at=date.today().isoformat(),
        commit=commit_sha,  # git rev-parse HEAD
        invocation=invocation_string,
        counts=[
            bl.BaselineCell(mandate_id=m, subsystem=s, count=c)
            for (m, s), c in sorted(current.items())
        ],
    )
    bl.save_baseline(baseline_path, snapshot)
```

- No baseline file → omit Drift section; rollup notes `no baseline (run --update-baseline to set one)`.
- **Drift never changes exit status** (report-only; no CI ratchet in v1).

## Step 6 — Write Markdown report

Write under host:

```text
docs/architecture/ARCHITECTURE_REVIEW_<YYYY-MM-DD>.md
```

Create `docs/architecture/` if needed. Include: commit/branch, invocation, files examined, per-auditor status, findings table, and `drift_section` when present. All persisted paths POSIX.

On write failure → hard fail with path; do not stream the report to the terminal as a silent fallback.

## Step 7 — Terminal roll-up

Print a short summary: auditor OK/FAILED counts, finding totals by severity, report path, and drift line (or “no baseline…”).

## Constraints

1. Auditors are read-only.
2. Host `config/architecture/mandates.yml` is the only mandate list — never treat plugin profiles as runtime defaults after setup.
3. Unknown `--mandates` id → `UnknownMandateError`.
4. Malformed baseline → `BaselineError` (fail loud).
5. Drift is informational only.

## Failure modes

| Condition | Behaviour |
|-----------|-----------|
| Missing `mandates.yml` | Hard fail; suggest `/acf-setup` |
| Unknown `--mandates` id | `UnknownMandateError` |
| Empty target tree | `EmptyTargetTreeError` |
| Malformed baseline JSON | `BaselineError` |
| Auditor crash / bad JSON | Mark FAILED; continue; non-zero exit |
| Report path unwritable | Hard fail |

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Editing plugin profiles instead of auditing host tree | Audit the host workspace |
| Treating drift as a gate | Report only; do not fail the run on Δ |
| Writing baseline without `--update-baseline` | Only write when the flag is set |
| Letting auditors Edit/Write | Read-only; controller writes report/baseline |
| Swallowing unknown mandate ids | Hard fail with `UnknownMandateError` |
