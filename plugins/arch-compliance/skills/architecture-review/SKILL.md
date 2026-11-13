---
name: architecture-review
description: Use when running /architecture-review, auditing a host repository's code against its reviewed mandates, comparing drift to the host's declared baseline, or updating that baseline with --update-baseline.
---

# /architecture-review

Codebase-wide architectural-conformance audit of the **host** repository. Auditors are read-only; the controller alone writes the report and, on request, the baseline.

**Prerequisite:** the host has been bootstrapped with `/acf-setup`: it declares `config/architecture/mandates.yml` and `config/architecture/review.yml`, and `config/architecture/ARCHITECTURE.md` carries every `arch_anchor` heading its reviewed mandates name. Superpowers must be installed (dispatch uses `dispatching-parallel-agents`).

## Invocation

`/architecture-review [--paths <glob>] [--include-tests] [--mandates <id,...>] [--update-baseline]`

| Flag | Meaning |
|------|---------|
| `--paths <glob>` | Replace the default include set (the declared packs' `files`). Built-in and declared exclusions still apply. A row that declares its own `surface` ignores it. A row without a declared `surface` whose default surface is then empty is dropped from the run and listed in the report under "Not in scope under --paths". |
| `--include-tests` | Drop the test-path exclusions. |
| `--mandates <id,...>` | Comma-separated mandate ids. Run only those reviewed rows. An id that matches no reviewed row raises `UnknownMandateError`. Omit to review every reviewed row. |
| `--update-baseline` | After the run, write the aggregated counts to the host's `baseline_path`. Without it the baseline is read-only input for drift. Only a full run saves a baseline: with any FAILED group, or with `--mandates`, `--paths` or `--include-tests`, the run is partial and raises `BaselineError` after the report is written. |

A *reviewed row* is an active mandate row with an `auditor` set, whatever its `call_sites`. Every location below comes from `review.yml` (`cfg.report_dir`, `cfg.baseline_path`) or from the registry; this skill declares none.

Set the flags once, then run the steps in order. Each block reuses the names the earlier ones bound.

```python
paths = None            # --paths <glob>, as a list; None when absent
include_tests = False   # --include-tests
mandate_ids = None      # --mandates a,b as ["a", "b"]; None when absent
update_baseline = False # --update-baseline
invocation = "/architecture-review"  # the exact command line, flags included
skill_dir = "<base directory>"  # this skill's base directory, as the harness announces it when the skill loads
```

## Step 1 — Load the host and select the rows

```python
from acf.registry import load_mandates
from acf.repo import MANDATES_REL, RepoTree, resolve_repo
from acf.review.host import load_review_config
from acf.review.packs import load_packs
from acf.review.rules import check_auditors, group_rows, select_rows

repo = resolve_repo(None)
tree = RepoTree(repo)
cfg = load_review_config(repo)
registry = load_mandates(repo / MANDATES_REL)
packs = load_packs(cfg.packs)
rows = select_rows(check_auditors(registry, repo), mandate_ids)
groups = group_rows(rows)
```

A missing `review.yml` or `mandates.yml` stops the run and points at `/acf-setup`. An empty `rows` is a finished run with nothing to review: say so and stop.

## Step 2 — Resolve the target tree

```python
from acf.review.prepass import target_tree

target = target_tree(tree, cfg, packs, paths=paths, include_tests=include_tests)
```

An empty tree raises `EmptyTargetTreeError`. Every path is a repository-relative POSIX key.

## Step 3 — Surfaces and doctrine sections

```python
from acf.exceptions import AcfInputError
from acf.repo import ARCH_REL
from acf.review import doctrine_section
from acf.review.prepass import row_surface

doctrine_file = tree.file(ARCH_REL.as_posix())
if doctrine_file is None:
    raise AcfInputError(f"the doctrine file {ARCH_REL.as_posix()} is missing; run /acf-setup")
doctrine_text = doctrine_file.read_text(encoding="utf-8")

surfaces = {}
out_of_scope = []  # rows whose default surface is empty under --paths
for row in rows:
    surface = row_surface(
        tree, cfg, packs, row, target, include_tests=include_tests, paths_given=bool(paths)
    )
    if surface:
        surfaces[row.mandate.id] = surface
    else:
        out_of_scope.append(row.mandate.id)
rows = [row for row in rows if row.mandate.id in surfaces]
groups = group_rows(rows)

sections = {
    row.mandate.id: doctrine_section(
        doctrine_text, row.mandate.arch_anchor, mandate_id=row.mandate.id
    )
    for row in rows
}
```

A declared `surface` that matches no file, and an `arch_anchor` that matches no doctrine line, each fail loud naming the mandate id. A row without a declared `surface` whose default surface (its packs' files in the target tree) is empty fails loud too, naming the mandate id, its `languages` and the declared packs; under `--paths` that row is instead dropped, `rows` and `groups` are recomputed without it, and the report lists it under "Not in scope under --paths". If every row is dropped, there is nothing to review under `--paths`: say so and stop.

## Step 4 — Pre-pass candidates

```python
from acf.review.prepass import render_candidates, scan

candidates = {
    row.mandate.id: render_candidates(scan(tree, row, surfaces[row.mandate.id], packs))
    for row in rows
}
```

Candidates are hints, not findings; precision is the auditor's job. A rule with no hints is still reviewed, with an empty candidate list.

## Step 5 — Dispatch one read-only agent per group

Assemble each group's brief, then dispatch every group in parallel with Superpowers **`dispatching-parallel-agents`**.

```python
from pathlib import Path

rules_dir = Path(skill_dir) / "rules"


def read_prompt(path: Path) -> str:
    if not path.is_file():
        raise AcfInputError(f"auditor prompt file not found: {path.as_posix()}")
    return path.read_text(encoding="utf-8")


contract = read_prompt(rules_dir / "_contract.md")
payloads: dict[str, str] = {}  # filled below: each agent's final message, under its group

briefs = {}
for group, group_members in groups.items():
    first = group_members[0]
    prompt_file = first.prompt if first.prompt is not None else rules_dir / f"{group}.md"
    briefs[group] = {
        "group": group,
        "prompt": read_prompt(prompt_file),
        "contract": contract,
        "rows": [
            {
                "id": row.mandate.id,
                "title": row.mandate.title,
                "settings": (
                    row.settings.model_dump(exclude_none=True)
                    if row.settings is not None
                    else row.mandate.params
                ),
                "surface": surfaces[row.mandate.id],
                "doctrine_section": sections[row.mandate.id],
                "docs": row.settings.docs if row.settings is not None else [],
                "candidates": candidates[row.mandate.id],
            }
            for row in group_members
        ],
        "instruction": (
            f"Read `{ARCH_REL.as_posix()}` in full, "
            "then every document it points to"
        ),
    }
```

Each agent receives exactly its `briefs[group]`:

1. its group id (`group`), which the payload's `group` field must echo exactly;
2. the rule prompt (`rules/<id>.md` under the skill's base directory, or the host's own prompt file for a `.md` auditor);
3. `_contract.md`, the finding contract;
4. its rows, each with id, title and settings (the validated settings for a rule, the raw `params` for a host prompt);
5. each row's surface, doctrine section, `docs` and candidates;
6. the instruction: *Read `config/architecture/ARCHITECTURE.md` in full, then every document it points to.*

Tool allowlist: `Read`, `Grep`, `Glob` only. No `Edit`, `Write` or mutating shell. The tree is not mutated during the audit; the controller writes only the report and baseline after the agents return. When each agent returns, store its final message in `payloads[group]`.

## Step 6 — Parse the payloads

```python
from acf.exceptions import AuditorContractViolationError
from acf.review.aggregator import GroupResult, parse_auditor_payload

results = []
for group, group_members in groups.items():
    raw = payloads.get(group, "")
    try:
        parsed = parse_auditor_payload(
            raw,
            group=group,
            rows=group_members,
            surfaces=surfaces,
            tree=tree,
        )
    except AuditorContractViolationError as error:
        results.append(GroupResult(group, "FAILED", None, raw, str(error)))
    else:
        results.append(GroupResult(group, "OK", parsed, raw, None))
```

A contract violation marks that group FAILED, keeps its raw payload and the error, and the run continues with the other groups.

## Step 7 — Exemptions and roll-up

```python
from datetime import datetime, timezone
from acf.review.aggregator import apply_exemptions
from acf.review.rollup import render_rollup

all_findings = [f for r in results if r.payload is not None for f in r.payload.findings]
findings, exempted = apply_exemptions(
    all_findings, {row.mandate.id: row for row in rows}, tree
)
now = datetime.now(timezone.utc)
rollup_md = render_rollup(
    repo=repo, cfg=cfg, findings=findings, results=results, now=now
)
```

With no file at `cfg.baseline_path` the roll-up says `no baseline (run --update-baseline to set one)`. With one it adds drift, staleness and provenance. None of them changes the exit status.

## Step 8 — Report, optional baseline, exit

```python
from acf.baseline import Baseline, BaselineCell, aggregate, save_baseline
from acf.diff import run_git
from acf.exceptions import BaselineError
from acf.review.aggregator import render_report, write_report
from acf.review.rollup import exit_status

head = run_git(repo, "rev-parse", "HEAD")
if head.returncode != 0:
    raise AcfInputError("git rev-parse HEAD failed: " + head.stderr.strip())
commit = head.stdout.strip()

report_md = render_report(
    commit=commit,
    invocation=invocation,
    results=results,
    findings=findings,
    exempted=exempted,
    rollup_md=rollup_md,
    rows=rows,
    out_of_scope=out_of_scope,
)
# The report is named by the local date; `now` stays UTC for the baseline timestamp.
report_path = write_report(tree, cfg, report_md, now.astimezone().date())
print(rollup_md)
print(f"report: {tree.key(report_path)}")
status = exit_status(results)

if update_baseline:
    partial = []
    if status != 0:
        partial.append("a group FAILED")
    if mandate_ids:
        partial.append("--mandates selects a subset of the rows")
    if paths:
        partial.append("--paths narrows the target tree")
    if include_tests:
        partial.append("--include-tests widens the target tree")
    if partial:
        raise BaselineError(
            "--update-baseline refused: the run is partial ("
            + "; ".join(partial)
            + "); the report was written, the baseline was not"
        )
    baseline_file = tree.contained(cfg.baseline_path)
    if baseline_file is None:
        raise BaselineError(f"baseline path {cfg.baseline_path!r} escapes the repository root")
    counts = aggregate(findings, prefixes=cfg.subsystems)
    save_baseline(
        baseline_file,
        Baseline(
            generated_at=now.isoformat(),
            commit=commit,
            invocation=invocation,
            counts=[
                BaselineCell(mandate_id=mandate_id, subsystem=subsystem, count=count)
                for (mandate_id, subsystem), count in sorted(counts.items())
            ],
        ),
    )

raise SystemExit(status)
```

Write the report, print the roll-up and the report's repository-relative POSIX path, then exit with `status` (the block ends in `raise SystemExit(status)`): `1` when any group FAILED, else `0`. With `--update-baseline`, a partial run (any FAILED group, `--mandates`, `--paths` or `--include-tests`) raises `BaselineError` naming why, after the report is written; only a full, clean run saves the baseline. Drift, staleness and provenance are informational and never change it. A report or baseline that cannot be written fails the run loudly; the report is never streamed to the terminal as a fallback.

## Constraints

1. Auditors are read-only.
2. The host's `mandates.yml` is the only mandate list; `call_sites` never select review rows.
3. Every rule is opt-in through an active mandate row with an `auditor`.
4. An unknown `--mandates` id raises `UnknownMandateError`.
5. A malformed or unreadable baseline fails loud; baseline writes happen only with `--update-baseline`, on a full run with no FAILED group.

## Failure modes

| Condition | Behaviour |
|-----------|-----------|
| Missing `mandates.yml` or `review.yml` | Hard fail; run `/acf-setup` |
| Unknown `--mandates` id | `UnknownMandateError` |
| Empty target tree | `EmptyTargetTreeError` |
| Declared surface matches nothing, or anchor matches nothing | `AcfInputError` naming the mandate id |
| Default surface empty (no declared `surface`) | `AcfInputError` naming the mandate id, its `languages` and the declared packs; under `--paths` the row is dropped and listed under "Not in scope under --paths" |
| Auditor payload violates the contract | Group FAILED, raw payload kept, run continues, exit status 1 |
| Report path unwritable | `ReportWriteError` |
| `--update-baseline` on a partial run (any FAILED group, `--mandates`, `--paths`, `--include-tests`) | Report written, then `BaselineError` naming why; the baseline is not saved |
| Baseline unwritable | `BaselineError` |

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Letting auditors Edit or Write | Read-only; the controller writes the report and baseline |
| Treating drift as a gate | Report only; it never changes the exit status |
| Writing the baseline without `--update-baseline` | Only write when the flag is set |
| Hand-parsing a payload | Use `parse_auditor_payload` |
| Hard-coding a report or baseline location | Take it from `cfg.report_dir` and `cfg.baseline_path` |
