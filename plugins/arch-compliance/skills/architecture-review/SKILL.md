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
| `--paths <glob>` | Replace the default include set (the declared packs' `files`). Built-in and declared exclusions still apply. A row that declares its own `surface` ignores it. |
| `--include-tests` | Drop the test-path exclusions. |
| `--mandates <id,...>` | Comma-separated mandate ids. Run only those reviewed rows. An id that matches no reviewed row raises `UnknownMandateError`. Omit to review every reviewed row. |
| `--update-baseline` | After the run, write the aggregated counts to the host's `baseline_path`. Without it the baseline is read-only input for drift. |

A *reviewed row* is an active mandate row with an `auditor` set, whatever its `call_sites`. Every location below comes from `review.yml` (`cfg.report_dir`, `cfg.baseline_path`) or from the registry; this skill declares none.

Set the flags once, then run the steps in order. Each block reuses the names the earlier ones bound.

```python
paths = None            # --paths <glob>, as a list; None when absent
include_tests = False   # --include-tests
mandate_ids = None      # --mandates a,b as ["a", "b"]; None when absent
update_baseline = False # --update-baseline
invocation = "/architecture-review"  # the exact command line, flags included
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

surfaces = {
    row.mandate.id: row_surface(
        tree, cfg, packs, row, target, include_tests=include_tests
    )
    for row in rows
}
sections = {
    row.mandate.id: doctrine_section(
        doctrine_text, row.mandate.arch_anchor, mandate_id=row.mandate.id
    )
    for row in rows
}
```

A declared `surface` that matches no file, and an `arch_anchor` that matches no doctrine line, each fail loud naming the mandate id.

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
import os
from pathlib import Path

plugin_root = Path(os.environ["CLAUDE_PLUGIN_ROOT"])
rules_dir = plugin_root / "skills" / "architecture-review" / "rules"
contract = (rules_dir / "_contract.md").read_text(encoding="utf-8")

briefs = {}
for group, group_members in groups.items():
    first = group_members[0]
    prompt_file = first.prompt if first.prompt is not None else rules_dir / f"{group}.md"
    briefs[group] = {
        "prompt": prompt_file.read_text(encoding="utf-8"),
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
            "Read `config/architecture/ARCHITECTURE.md` in full, "
            "then every document it points to"
        ),
    }
```

Each agent receives exactly its `briefs[group]`:

1. the rule prompt (`rules/<id>.md` under `${CLAUDE_PLUGIN_ROOT}`, or the host's own prompt file for a `.md` auditor);
2. `_contract.md`, the finding contract;
3. its rows, each with id, title and settings (the validated settings for a rule, the raw `params` for a host prompt);
4. each row's surface, doctrine section, `docs` and candidates;
5. the instruction: *Read `config/architecture/ARCHITECTURE.md` in full, then every document it points to.*

Tool allowlist: `Read`, `Grep`, `Glob` only. No `Edit`, `Write` or mutating shell. The tree is not mutated during the audit; the controller writes only the report and baseline after the agents return. Each agent's final message is its payload, kept as `payloads[group]`.

## Step 6 — Parse the payloads

```python
from acf.exceptions import AuditorContractViolationError
from acf.review.aggregator import GroupResult, parse_auditor_payload

results = []
for group, group_members in groups.items():
    raw = payloads[group]
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
)
report_path = write_report(tree, cfg, report_md, now.date())

if update_baseline:
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

print(rollup_md)
print(f"report: {report_path}")
status = exit_status(results)
```

Print the roll-up and the report path, then finish with exit status `status`: `1` when any group FAILED, else `0`. Drift, staleness and provenance are informational and never change it. A report or baseline that cannot be written fails the run loudly; the report is never streamed to the terminal as a fallback.

## Constraints

1. Auditors are read-only.
2. The host's `mandates.yml` is the only mandate list; `call_sites` never select review rows.
3. Every rule is opt-in through an active mandate row with an `auditor`.
4. An unknown `--mandates` id raises `UnknownMandateError`.
5. A malformed or unreadable baseline fails loud; baseline writes happen only with `--update-baseline`.

## Failure modes

| Condition | Behaviour |
|-----------|-----------|
| Missing `mandates.yml` or `review.yml` | Hard fail; run `/acf-setup` |
| Unknown `--mandates` id | `UnknownMandateError` |
| Empty target tree | `EmptyTargetTreeError` |
| Declared surface matches nothing, or anchor matches nothing | `AcfInputError` naming the mandate id |
| Auditor payload violates the contract | Group FAILED, raw payload kept, run continues, exit status 1 |
| Report path unwritable | `ReportWriteError` |
| Baseline unwritable | `BaselineError` |

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Letting auditors Edit or Write | Read-only; the controller writes the report and baseline |
| Treating drift as a gate | Report only; it never changes the exit status |
| Writing the baseline without `--update-baseline` | Only write when the flag is set |
| Hand-parsing a payload | Use `parse_auditor_payload` |
| Hard-coding a report or baseline location | Take it from `cfg.report_dir` and `cfg.baseline_path` |
