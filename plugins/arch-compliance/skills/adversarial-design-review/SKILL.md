---
name: adversarial-design-review
description: Spec-stage gate. Dispatches four blind, read-only reviewers against a committed spec to attack its claims — diagnosis, mandates, partial duplication, and mechanism-vs-hardening — then blocks or clears the move to writing-plans. Mandatory between brainstorming and writing-plans where the host's doctrine requires it. Read-only; the author does every edit.
---

# /adversarial-design-review

Attack a design document before it becomes a plan. Read-only.

This file is the procedure.

## Invocation

`/adversarial-design-review <path/to/SPEC.md>`

One positional argument: the path to a committed spec. `git status --porcelain <spec>`
must print nothing; any output means the working tree has uncommitted changes to that
file — say so and stop. Reviewers adjudicate the committed text. Run the gate from
the host repository's root: step 0 resolves the process directory as the host root and
refuses (naming the path) if `config/architecture/adr.yml` is not there.

## What this gate exists to catch

Three failure classes that otherwise reach implementation: a plausible-but-wrong
diagnosis; a new abstraction that *partially* duplicates an existing one; a design
that adds a recovery mechanism where it should harden the failure point.

## Execution steps (controller)

**Load the host's values first.** Run the block below; it stops the run before any reviewer is dispatched if the host has no `config/architecture/adr.yml` or no `config/architecture/ARCHITECTURE.md`. Every later Python step reuses `repo` and `cfg`.

```python
from acf.repo import resolve_repo
from acf.adr import load_host_config
repo = resolve_repo(None)
cfg = load_host_config(repo)
```

**1. Classify the spec kind.** Read the spec in full. Emit a *set* — a spec can be
both a fix and an enhancement. Follow `claims/extraction.md` for the rules.

| Kind | Load-bearing (blocking) family |
|---|---|
| `defect` / guardrail-gap / arch-finding | `root_cause` |
| `feature` (pure enhancement) | `shape_fit` |
| `docs` / measurement | — decline, stating why |

`defect`, `feature`, and `docs` are the only legal kinds. A pure enhancement is
**never** asked for a root cause. If the spec is neither a defect nor a feature and is
not declared docs/measurement, do not invent a kind and do not dispatch. Stop here and
raise it yourself, naming what you read and why it fit neither:

```python
from acf.exceptions import SpecKindUndeterminedError
raise SpecKindUndeterminedError(
    "spec is neither a defect nor a feature and is not declared docs/measurement: "
    + your_reasoning
)
```

(`classify_outcome` raises the same exception at step 8 as a backstop for a bad kind
*string* that slipped past this check — by then the reviewers have already run.)

If the only kind is `docs`, print a one-paragraph decline naming the spec, the
classification, and the reason this gate adds nothing — then stop. Do not dispatch.

**2. Classify every citation before dispatch.** Collect every `file:line` and every
bare path the spec cites, then classify — do not merely test for existence:

```python
from pathlib import Path
from acf.adr.citations import (
    classify_citations, unresolved_citations,
)
kinds = classify_citations(cited, repo_root=repo, proposed=proposed_paths)
unresolved = unresolved_citations(cited, repo_root=repo, proposed=proposed_paths)
if unresolved:
    from acf.exceptions import UnresolvableCitationError
    raise UnresolvableCitationError(
        "spec cites paths that do not exist in the repo: " + ", ".join(unresolved)
    )
```

Classification needs git to answer: a **shallow clone** (every cloud session) cannot
tell a `historical` path from an `unresolved` one, so it raises
`CitationHistoryUnavailableError` naming the remedy (`git fetch --unshallow`) — as does
any failing git command. Never catch it to fall back to `unresolved`; fetch the history
and re-run the step.

`proposed_paths` is the set of paths the spec says it will **create** — read them off
the spec in step 1, together with the paths it cites *because they do not exist*.
Everything else is decided from evidence:

| Kind | Meaning | Passed to reviewers as |
|---|---|---|
| `current` | in the working tree, **or shorthand that suffix-matches one tracked file** | the **resolved full path** to open |
| `historical` | not in the tree, but in git history | "this was deleted; the citation is about the past — do not hunt it" |
| `proposed` | the spec declares it will create this | "does not exist yet, by design" |
| `asserted_absent` | the spec cites it *because it does not exist* | "its absence is the finding; do not hunt it" |
| `external` | gitignored (build artifacts) or absolute (outside the repository) | "outside the repo; unavailable to you" |
| `unresolved` | none of the above | **hard fail before dispatch** |

Shorthand (a basename or partial path) resolves by suffix match against
`git ls-files`, shortest wins — deterministic, never a guess, and a wrong path is a
suffix of nothing tracked and still hard-fails. Use `resolve_citation()` for the
resolved path. **Hand every reviewer the kind alongside the resolved path**: a
reviewer that knows a path is `historical` does not return `UNPROVEN` for a file it
merely failed to find, and `UNPROVEN` on a load-bearing claim blocks.

**2b. Pre-dispatch mechanical stop.** These classes are decidable without a
reviewer. Run them against the committed spec and **stop before step 3** on any hit —
print the hits, name them mechanical, and hand the author
`responding-to-adversarial-review`. No claim extraction, no dispatch, no run detail,
no ledger row.

- Literal tab characters anywhere in the spec.
- Placeholders still in the body: TODO, TBD, FIXME, or a triple question mark.
- Revision archaeology: a sentence that attributes a finding or a BLOCKED/CLEARED
  outcome to a prior version (`vN`), a named reviewer, or a previous gate run. The
  Status line's own version number is not archaeology. A supersession heading that
  restates the *claim* without the prior verdict is not archaeology.
- Slice or phase tags that disagree with the sequencing section: every `[S1]` /
  `[Phase 0]` tag on a change-surface or Then-list must name the landing slice the
  sequencing prose assigns.

Unresolved citations are already a hard fail in step 2.

**2b-ii. Revision-evidence check (re-runs only).** A run is a re-run when a run
detail for this spec exists in this checkout under the declared `runs_dir` — a file
shaped `<SPEC_STEM>_v<N>_<date>.md`, **excluding** files with a `_response_` segment.
Read the most recent one's `Outcome:` line.

- **BLOCKED** → require the author response record under the declared `runs_dir`,
  named `<SPEC_STEM>_v<N>_response_<date>.md` (`N` = the blocked
  run's own version). Its entries must cover
  **every line** of that detail's `## Blocking reasons` (by claim ID where the line
  names one, by quoted line otherwise); every mechanism-class resolution must carry
  a command+output block; a **Sentence-type sweep** section must be present
  (presence only — its quality is never adjudicated). Anything missing is a
  mechanical stop: print what is missing, hand the author
  `responding-to-adversarial-review`, no dispatch, no ledger row.
- **Any cleared variant** (including `CLEARED_WITH_ABSORPTIONS` and
  `CLEARED_BY_VERIFICATION_PASS`) → no evidence stop, but still a re-run for step 3.
- **No run detail, but a response record for this stem exists** → the branch carries
  a revision answering a review this checkout cannot see. Stop and say so — no
  dispatch, no ledger row. Never treat it as a first run.
- Neither → first run.

Never adjudicate whether a pasted command or its output actually supports the
revision; that is the reviewers' job, blind.

**WARN lane (advisory, never a stop):** on a re-run, `grep -Ei` the spec's changed
lines for aggregates (`[0-9]+ (hits|rows|sites|consumers|classes|owners|intersects)`)
and universal quantifiers (`(every|all|only) .*(and only|nothing else|none other)`),
and print hits as warnings. False positives are expected; the sentence-type sweep in
the response record is the authoritative check.

**3. Extract claims.** Follow `claims/extraction.md`. Produce a numbered list of
`Claim` objects:

```python
from acf.adr import Claim
claims = [
    Claim(id="C1", family="root_cause", statement="…",
          spec_citation="src/x.py:12", load_bearing=True),
    # …
]
```

Assign each to exactly one reviewer's subset by family:

| Reviewer | Claim families |
|---|---|
| `refuter` | `premise`, `root_cause`, `compensation`, `deletion` |
| `compliance` | `mandate` |
| `sweeper` | `shape_fit`, `sweep` |
| `hardening` | `mechanism_justification`, `implementability` |

**Re-runs: assign `revision_disposition` per claim, before dispatch.** Judge by claim
identity against the most recent run detail's `## Claims` list — the same file 2b-ii
anchored on: `carried` when that list contains a statement-equivalent claim about the
same subject (IDs need not match; extraction renumbers per run); `delta` otherwise;
**ambiguity resolves to `delta`**. The git diff between the reviewed commits is
auxiliary evidence, never the rule. If the most recent detail has no `## Claims`
section (it predates the section, or is a verification-pass record), fall back to the
latest detail that has one, else to blocking-reason prose plus the diff. Dispositions
are held with the step-4 predictors and are **never** handed to reviewers.

**4. Capture the ledger predictors — before dispatch,** so they cannot be back-fitted
to the outcome: `spec_path` (POSIX), `commit_sha` (`git rev-parse HEAD`), `date`
(ISO, from the environment's current date), `spec_kinds`, `new_design_elements`,
`phases`, `cited_files`, `touched_surfaces`, `surface_call_sites`,
`filter_would_skip`, `holdout` — plus, on re-runs, each claim's `revision_disposition`.
Definitions are pinned under step 10.

**5. Dispatch four blind reviewers in one parallel batch** via
`superpowers:dispatching-parallel-agents`. Each agent receives its own prompt file
content — `reviewers/refuter.md`, `reviewers/compliance.md`, `reviewers/sweeper.md`,
or `reviewers/hardening.md` — plus:

- The **full spec text**.
- **Its own claim subset only**: id, family, statement, `spec_citation`,
  `load_bearing`. That field list is exhaustive — `revision_disposition` never
  travels; a disposition handed to a reviewer is prior-run archaeology.
- Its tool allowlist: `refuter`, `hardening` — `Read`, `Grep`, `Glob`, **read-only**
  `Bash`; `compliance`, `sweeper` — `Read`, `Grep`, `Glob`.
- The repo root and the current commit SHA.
- Every citation's resolved path and kind (step 2).
- For the sweeper only: the paths it must exclude from its corpus — `repo / cfg.runs_dir` itself, the ledger file `repo / cfg.ledger_path`, and the directory that contains each of them only when that directory is not the repository root.

The prompt file already carries the reviewer's output schema and identity string. The
reviewer echoes the identity back verbatim as the `reviewer` field of its payload;
`parse_reviewer_payload` hard-fails if that field disagrees with the name it was
dispatched under.

**Do not** tell any reviewer that other reviewers exist, what they are looking at, or
what they found. Do not read any payload until all four dispatches have returned —
convergence is only evidence if it was reached blind. Each payload is the return value
of the dispatch call that spawned it; never send a running reviewer a follow-up
message to ask for it.

**6. Parse each payload.**

```python
from acf.adr import parse_reviewer_payload
payloads = [
    parse_reviewer_payload(raw[name], name)
    for name in ("refuter", "compliance", "sweeper", "hardening")
]
```

`ReviewerContractViolationError` **aborts the run**: surface the message verbatim.
There is no per-reviewer FAILED status and no partial acceptance — absorbing a
malformed verdict is indistinguishable from a clean pass. Re-dispatch that reviewer
once with the same inputs; on a second violation, report the raw payload and stop.

**7. Group convergence candidates, then adjudicate them yourself.**

```python
from acf.adr import group_convergence_candidates
candidates = group_convergence_candidates(payloads)
```

For each candidate group, read the summaries and decide whether the reviewers reached
**the same finding** or merely touched the same file. Over-grouping is the intended
failure mode — discard the coincidences. For each genuine one, construct:

```python
from acf.adr import ConvergedFinding
converged = [
    ConvergedFinding(summary="…", reviewers=["refuter", "hardening"], evidence=["…"]),
    # …
]
```

This judgment is yours; the Python only narrowed the field.

**8. Classify the outcome.**

```python
from acf.adr import classify_outcome, DesignReviewRun
result = classify_outcome(
    spec_kinds=spec_kinds, claims=claims, payloads=payloads, converged=converged,
)
run = DesignReviewRun(
    spec_path=spec_path, spec_kinds=spec_kinds, commit_sha=commit_sha,
    claims=claims, payloads=payloads, converged=converged, outcome=result.outcome,
)
```

Do **not** re-rate, soften, or filter a reviewer's severity before this call. You are
not a severity authority. `classify_outcome` already treats a `SURVIVED` verdict whose
only evidence is the claim's own `spec_citation` as UNPROVEN (Constraint 3); do not
pre-empt that judgment and do not soften it after the fact either way.

**9. Print the roll-up.**

```python
from acf.adr import format_rollup
print(format_rollup(run, result))
```

Then print the full finding detail below the roll-up, grouped by reviewer, with every
`file:line` intact. The roll-up is a summary; the author triages from the detail. The
spec's header line is constructed in step 11, not here.

**9b. Write the run detail — before the ledger row, and never skipped.**

```python
from pathlib import Path
from acf.adr import run_detail_path, write_run_detail
detail = run_detail_path(spec_path, version=N, date=today_iso, runs_dir=repo / cfg.runs_dir)   # N as in step 11
write_run_detail(run, result, detail)
```

This lands under the declared `runs_dir` — tracked. The ledger is counts-only, so
this file is the only record of what the review actually *said*, and it is what a
later `absorbed`/`rejected` amendment is adjudicated against. `RunDetailWriteError`
aborts the run; do **not** proceed to the ledger row without the detail.

**10. Append one ledger row.**

```python
from pathlib import Path
from acf.adr import LedgerRow, append_row
append_row(
    LedgerRow(
        # predictors captured in step 4, verbatim
        spec_path=spec_path, commit_sha=commit_sha, date=today_iso,
        spec_kinds=spec_kinds, new_design_elements=..., phases=..., cited_files=...,
        touched_surfaces=..., surface_call_sites=...,
        filter_would_skip=..., holdout=...,
        # re-runs only — from the step-3 dispositions of the claims named in
        # THIS run's "## Blocking reasons"; None/None on first runs, 0/0 on a
        # CLEARED re-run (measured zeros):
        refuted_carryover=..., refuted_delta=...,
        # outcomes
        outcome=result.outcome,
        findings_by_lens_severity=..., converged_count=len(converged),
        absorbed=0, rejected=0, blocks_overturned=0,
        tokens=..., wall_clock_s=...,
    ),
    repo / cfg.ledger_path,
)
```

**Predictor definitions — pinned.** These figures only mean anything as a *series*.
Use these definitions verbatim; if one is wrong, change it **here**, never in one run.

- `cited_files` — **computed, not judged**, via `count_cited_files(cited)` from
  `acf.adr.citations`. Line references are stripped;
  `historical`, `proposed`, and `external` all count — they were handed to reviewers.
- `phases` — every stage the design sequences, prerequisite slices included: the
  number of things that must land in order, not headings that say Phase N.
- `new_design_elements` — every element the design introduces that does not exist
  today: a module, function, exception, command, schema field, guard, or CI task.
  Count elements, not the tasks that build them.
- `surface_call_sites` — call sites of the **touched surface**, not of the spec's
  subject: a façade's call sites; a public interface's callers. The blast-radius
  proxy.
- `touched_surfaces` — closed set: `facade`, `persistence_format`, `hfsm`,
  `metadata_facade`, `public_interface`, `ui`, `none`. Pick every one the design
  touches. The ledger rejects an empty list.
- `spec_kinds` — non-empty; the ledger rejects an empty list.
- `findings_by_lens_severity` — `dict[ReviewerName, dict[Severity, int]]`. Outer keys
  are exactly the four reviewer names; inner keys are exactly `blocking`,
  `important`, `advisory`. Include reviewers who found nothing as all-zero counts.
- `holdout` — `false` for every run until a narrower trigger filter ships.
- `filter_would_skip` — derived, not guessed: `true` when `touched_surfaces` contains
  none of `facade`, `persistence_format`, `hfsm`, `metadata_facade`,
  `public_interface`. Change it together with `TouchedSurface` in `acf.adr.ledger`, the persisted
  vocabulary it is a subset of.
- `tokens`, `wall_clock_s` — measured integers, both **`gt=0`** in the contract: the
  summed token count of the four dispatches plus your own; elapsed seconds from step
  1 to this step. Round; never fabricate. Exclude any row with `tokens: 0` when reading the series.
- `date` — a genuine ISO `YYYY-MM-DD`; the ledger rejects a placeholder.

A value outside these shapes raises Pydantic's `ValidationError` at `LedgerRow(...)`,
one line above `append_row`. `LedgerWriteError` fires only once construction has
succeeded and the write itself fails.

`absorbed`, `rejected`, and `blocks_overturned` are `0` at write time. They, and
`escapes`, are amended later by the host's post-merge process **appending a superseding
record** for the same `spec_path` + `commit_sha` — the ledger is append-only, never
edited in place; a reader takes the last such record. `LedgerWriteError` aborts;
never skip the row.

**The write is unconditional on outcome.** After `append_row`, re-read the last
non-preamble line of the ledger file and confirm it contains this run's `spec_path`,
`commit_sha`, and `outcome`. If that read fails or disagrees, stop — no step 11, no
header line, no `writing-plans`. That read is the proof the row exists, on CLEARED as
much as on BLOCKED.

**Commit the run detail and the ledger append on the reviewed branch before reporting
the outcome.** Step 2b-ii keys on these files; an uncommitted detail makes the next
re-run look like a first run.

Print the claim-verdict counts from the payloads you hold — SURVIVED / UNPROVEN /
REFUTED, and how many REFUTED were load-bearing. The ledger schema does not persist
them; the run detail plus this print are the record, and
`findings_by_lens_severity` alone can show `blocking: 0` on a BLOCKED run.

If this checkout is a linked worktree (`git rev-parse --git-common-dir` is not this
tree's own `.git`), say so: the ledger row and run detail are local to this branch. A
JSONL append will conflict on merge; resolve it by keeping every unique
`spec_path`+`commit_sha` record from both sides, never by taking one side. Do not
invent a second write path.

**11. State the next step; for a non-`BLOCKED` outcome, mint the header line
yourself.** Neither the header nor an offer of `writing-plans` may happen until the
step-10 re-read succeeded.

- `BLOCKED`: name the specific claims and findings that must be resolved, state the
  revision class (mechanism vs precision-only), hand the author
  `responding-to-adversarial-review`, and stop. There is no header line for a blocked
  run.
- `CLEARED_WITH_ABSORPTIONS`: list what must be folded into the spec body (or carried
  as an Implementation Decision Override with written rationale) before
  `writing-plans`, then hand the author the header line.
- `CLEARED`: hand the author the header line directly.

```
**Adversarial review:** vN — <date>, <reviewer count> reviewers, <OUTCOME> (repo @ <sha>)
```

- `<date>` is the ISO date captured in step 4.
- `N` is **the spec's own current version** — the number in its Status line, read in
  step 1. Only if the spec carries no version is `N` one more than the count of
  `**Adversarial review:**` header lines already present (the first run on a spec is
  `v1`). That count undercounts whenever earlier reviews predate the header
  convention, so a Status-line version always wins.
- `<reviewer count>` is `len(run.payloads)`; `<sha>` is `run.commit_sha`; `<OUTCOME>`
  is `result.outcome`.
- No `spec_path`: the line is pasted inside that very spec.

## Absorption is the author's edit

This skill never edits the spec. A `BLOCKED` finding is answered with
`responding-to-adversarial-review` — sweep the *claim* (nouns, not the cited line),
then the step-2b mechanical stop, then request the re-run. The only metadata this
skill adds is the step-11 header line:

```
**Adversarial review:** v2 — 2026-08-10, 4 reviewers, CLEARED (repo @ 25748b46)
```

A spec revision is a **new version**, and re-run scope follows the revision class. A revision that changes any **mechanism** — a contract, schema,
state, exception, sequencing gate, suppression or migration rule; anything the design
adds, removes or redefines — is a different design and re-runs **in full**; reviewers
must be blind to prior verdicts or they anchor. A revision that changes **only factual
precision or wording** (a corrected measurement, a citation form, a mandate
attribution, a change-surface entry for an already-implied file) takes a **controller
verification pass** instead of a dispatch: re-measure every corrected fact against the
live tree, re-grep every absorbed claim's sweep across the whole spec, and record
the user's approval to proceed in the spec header, minting:

```
**Adversarial review:** vN — <date>, verification pass over the v<N-1> full run
(BLOCKED; all blocking findings precision-class, absorbed and re-measured),
user-approved (repo @ <sha>)
```

**A verification pass writes no ledger record.** No model accepts one: a
verification pass is not a dispatch, so `LedgerRow` rejects it (its `outcome`
Literal has no `CLEARED_BY_VERIFICATION_PASS`, and it requires the dispatch
measurements — `tokens`, `wall_clock_s`, `findings_by_lens_severity` — that a pass
never produces), and `LedgerAmendment` cannot express a clearance at all (it carries
no `outcome`, and matches on `spec_path` + `commit_sha`, which a pass has no
dispatch commit for). Both are `extra="forbid"`. Do not hand-write a
verification-pass record around that contract. Until a model exists, the **spec header line above is the record** —
mint it, and leave the ledger alone. Adding the model is a
persistence-format change: it needs a spec and a gate run, not an inline fix during
a pass.

Re-measuring named facts is not adjudication. **When any doubt exists about which
class a revision is, it is a mechanism revision.**

## Constraints (architectural contract)

1. Reviewers are blind to each other — one parallel batch, no payload read early.
2. Reviewers are read-only — no Edit, no Write, no test execution.
3. Refute-by-default: `SURVIVED` needs a `file:line` the reviewer resolved itself.
   The spec's own citation is not verification — `classify_outcome` treats a
   SURVIVED verdict whose only evidence is the claim's own `spec_citation` as
   UNPROVEN, and UNPROVEN on a load-bearing claim blocks.
4. Silence is not coverage: both `unanchored_findings` and
   `looked_for_but_did_not_find` empty is a contract violation.
5. One JSON block per reviewer; a violation aborts the run.
6. Python judges nothing — classification, extraction, and convergence adjudication
   are yours; the gate truth table is Python's.
7. Mechanical defects do not consume a blind dispatch (steps 2b/2b-ii).
   Diagnosis belongs to the host's doctrine, not to this gate.

## Failure modes

| Condition | Exception | Behaviour |
|---|---|---|
| Spec is docs/measurement only | — | Decline with a stated reason; no dispatch. |
| Step 2b mechanical hit | — | Stop before extract/dispatch; no ledger row. |
| 2b-ii: response record missing, blocking line uncovered, or sweep section absent | — | Mechanical stop before extract/dispatch; no ledger row; hand the author responding-to-adversarial-review. |
| 2b-ii: response record present but its run detail absent | — | Stop and say so; no dispatch, no ledger row — never treat as a first run. |
| Spec fits neither defect nor feature (step 1) | `SpecKindUndeterminedError` | You raise it yourself, before dispatch; name what you read and why it fit neither. |
| An unrecognized kind string reaches the gate (step 8) | `SpecKindUndeterminedError` | `classify_outcome` raises as a backstop, naming the offending kind and the legal set (`defect`, `feature`, `docs`) — reviewers have already run by this point. |
| A cited path classifies `unresolved` | `UnresolvableCitationError` | Hard fail before dispatch; list every unresolved path. `historical` / `proposed` / `external` are NOT errors — pass them to reviewers with their kind. |
| Reviewer payload malformed | `ReviewerContractViolationError` | Re-dispatch once, then abort with the raw payload. |
| Run detail unwritable | `RunDetailWriteError` | Hard fail; DO NOT proceed to the ledger row without the detail. |
| `tokens`/`wall_clock_s` unmeasured | `ValidationError` at `LedgerRow(...)` | Both are `gt=0`; measure them rather than passing a placeholder. |
| Ledger unwritable | `LedgerWriteError` | Hard fail; DO NOT proceed without the row. |
