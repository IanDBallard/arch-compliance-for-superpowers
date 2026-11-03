---
name: post-merge-housekeeping
description: Use when a PR has just merged or a branch is otherwise finished, before starting the next task — and when noticing stale worktrees, orphaned/zombie test servers still listening after a worktree was pruned, unticked checkboxes in merged plans, or tracking docs that contradict merged code.
---

# Post-Merge Housekeeping

## Overview

Merged is not finished. Every step below exists because skipping it once cost a
false-alarm investigation. This checklist is the looking.

**Core principle: run the discovery checks even though everything *seems* done —
"found nothing" is a valid result, silence is not.**

**Platform & host declarations.** Steps 1–3 and 3.5–8 use `git` and run anywhere.
Step 2.5 has a PowerShell branch (Windows developer nodes) and a POSIX branch (Linux,
macOS, Docker, cloud sessions); run the one that matches the host OS and state which
you ran. `gh` is not present in every environment; steps 1, 2, and 6 name the
fallbacks. Host-specific operational conventions (shared-checkout branch lock,
worktree daemon probe, post-merge CI workflows, and durable tracking target) are read
from the `## Post-merge` section of the host's doctrine (`acf.repo.ARCH_REL`, or a
document it points to). When `## Post-merge` omits a check, report `<check>: not
declared in ## Post-merge, skipped` in step 8 rather than skipping silently.

## The Checklist (run from the main checkout root, in order)

**Steps 1–2 are read-only. Do not move the main checkout's HEAD to run them** — see
step 0.

**Multi-item runs — parallelize the reads only.** For a single just-merged PR, run
steps 1–2 inline; a subagent is pure overhead there. When more than one branch/plan
needs steps 1–2, or step 5's discovery grep spans many docs, dispatch one read-only
subagent per item in parallel, giving each the exact commands to run. Each subagent
must return **raw command output**, not summaries — the no-silencing rule (step 0)
applies to subagents too. Only reads delegate, and only in the pre-checkout phase:
dispatch the step-5 discovery alongside steps 1–2 — none of it needs a checkout — and
collect every subagent result before step 3.5. The doc edits that discovery feeds are
main-session work like the rest. Teardown (step 3) and everything from step 3.5
onward stay in the main session, sequential, with no subagents in flight: the
branch-lock STOP gate must be able to ask the user, and no agent — reader or writer —
may touch the shared main checkout while the main session is mutating it.

### 0. The main checkout may be shared — check before you mutate it

The main checkout is shared by every worktree and, on some hosts, by another live
session. `git checkout` / `git pull` there are **side effects on someone else's
workspace**, and they are not needed for any verification in steps 1–2.

The line is *whose* state you are changing. Deleting the branch and worktree you
just merged (step 3) is your own work and needs no permission. Moving the main
checkout's HEAD, or committing to it (step 3.5 onward), affects the shared workspace.

So: before the first command that moves or commits to the main checkout — i.e.
before step 3.5:

```bash
git -C <main-checkout> branch --show-current
git -C <main-checkout> status --short
```

Also inspect any shared-checkout branch lock or branch-guard hook declared under
`## Post-merge` in the host's doctrine (if none is declared, record `branch lock: not
declared in ## Post-merge, skipped` in step 8). If the checkout is on an unexpected
in-flight branch, has uncommitted work that is not yours, or a declared branch lock
names another branch, **STOP and ask the user.** Another workstream owns the
checkout. Never bypass a host branch guard via an environment variable or `--no-verify`
and never rewrite another session's lock file yourself.

Also: never suppress these commands' output (`-q`, `2>/dev/null` on the checkout
itself). A silenced `git checkout` cannot be reconstructed afterwards when someone
asks what you changed.

### 1. Resolve default branch, verify content landed, & check post-merge CI — read-only, no checkout (squash-aware)

Fetch from `origin` and resolve the remote default branch once without writing any
local ref:

```bash
git fetch origin
default_branch=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')
if [ -z "$default_branch" ]; then
  default_branch=$(git ls-remote --symref origin HEAD | awk '/^ref:/ {sub("refs/heads/", "", $2); print $2}')
fi
```

If `$default_branch` is still empty, **STOP and ask the user** — never guess `main`.

Verify the merge and content presence straight off `origin/$default_branch` without
touching HEAD:

```bash
gh pr view <N> --json mergedAt,mergeCommit,headRefOid

# content presence, straight off the remote ref — no working-tree change:
git show "origin/$default_branch:<path/to/file>" | grep -q '<line the branch added>' && echo PRESENT || echo MISSING
git grep '<symbol the branch added>' "origin/$default_branch" -- <path>
```

**No `gh` on this host?** Take `mergedAt` and the merge/squash SHA from the commit on
`origin/$default_branch`:
`git log --format='%H %cI %s' -1 --grep='(#<N>)' "origin/$default_branch"`. If that
finds nothing, ask the user for the PR's merge commit rather than guessing.

Verify by **content presence** (a function, route, test, or doc line the branch
added), never by SHA ancestry — squash merges make `git branch --merged` and ancestry
checks lie.

`git show "origin/$default_branch:<path>"` and `git grep ... "origin/$default_branch"`
answer this without touching HEAD. **A checkout here buys nothing** — if you find
yourself running one to "verify the merge", you are mutating shared state for a read.

**Do NOT use `git diff "$default_branch" <branch>` "expect empty" as the merged-proof**
— it is non-empty whenever `$default_branch` contains *other* merged work, and "empty"
tells you nothing either way.

**Post-merge CI check:** Verify the post-merge workflow on `$default_branch`:

```bash
gh run list --branch "$default_branch" --limit 5
```

Also run any post-merge CI or deploy verification declared under `## Post-merge` in
the host's doctrine. If `gh` is absent and no post-merge CI check is declared under
`## Post-merge`, report `post-merge CI check: not declared in ## Post-merge, skipped`
in step 8.

### 2. Stranded-commit check (the one everyone skips)

```bash
head=$(gh pr view <N> --json headRefOid --jq .headRefOid)   # the commit the forge merged
git log --format='%h %cI %s' "$head"..<branch>              # read-only; no checkout needed
```

Any commit listed is stranded — it exists nowhere but the branch, unless its content
reached `origin/$default_branch` some other way (prove that by the commit's **whole**
diff, every added line, not a sampled phrase: later edits reword rows, so a phrase can
match while the change it belonged to is missing). A post-merge push also silently
**recreates the just-deleted remote branch**. Cherry-pick doc-only strays onto
`$default_branch`; anything with code goes through a follow-up PR.

**Compare against `headRefOid`, never against `mergedAt`.** A commit's timestamp
records when it was made, not when it was pushed. A commit made before the merge but
pushed after it, or never pushed, predates `mergedAt` yet is not in the merge. On
2026-10-28 the timestamp check passed three branches whose extra commits never reached
the default branch.

**No `gh`?** The merged head is not recoverable from a squash commit. Treat every
`"origin/$default_branch"..<branch>` commit as stranded until its whole diff is shown
on `origin/$default_branch`.

A branch with **no PR** has no merged head: every commit in
`"origin/$default_branch"..<branch>` is a candidate, checked the same way.

### 2.5 Worktree process & resource sweep — REQUIRED before any `git worktree remove`

`git worktree remove` does not kill processes launched from that worktree. A background
test server, simulator, or watcher survives with its working tree deleted out from
under it: an in-memory `/health` endpoint can still answer 200 while every data
endpoint fails, and test runners that reuse an existing server port adopt the zombie
and fail deterministically across every checkout.

First, check for any lingering process whose command line or working directory
references the worktree path or slug being removed:

**Windows (PowerShell):**

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.CommandLine -and $_.CommandLine.Contains('<worktree-slug>') } |
  Select-Object ProcessId, Name, CreationDate, CommandLine
```

**POSIX (Linux, macOS, Docker, cloud sessions):**

```bash
pgrep -af '<worktree-slug>'
```

Second, check whether `## Post-merge` in the host's doctrine declares a **worktree
daemon probe** (process filter and functional/data readiness endpoint). If declared,
run that probe for every candidate listener; if not declared, report
`worktree daemon probe: not declared in ## Post-merge, skipped` in step 8 (still
reporting the result of the worktree-slug process check above).

| Verdict | Predicate | Action |
| --- | --- | --- |
| **Zombie** | Its command line or working directory (`readlink /proc/<pid>/cwd` on POSIX) belongs to a worktree being removed in step 3 or no longer listed in `git worktree list`, OR its `/health` port answers while the host's declared functional data endpoint fails | Windows: `Stop-Process -Id <pid>` (add `-Force` only if the plain stop fails). POSIX: `kill <pid>`, then `kill -9 <pid>` only if it survives. Re-run the query and confirm the PID is gone |
| **Healthy** | Belongs to a live checkout and the host's declared functional data endpoint succeeds | Leave it — it may belong to a live session. Name it in the step-8 report |

An in-memory health flag is NOT evidence of health when its backing directory was
deleted with a worktree. Always probe a functional data endpoint when the host
declares one. State the sweep result in the step-8 report either way.

### 3. Teardown

```bash
git ls-remote --heads origin <branch>          # exists again? see step 2
git push origin --delete <branch>              # after step 2 is clear
git worktree remove <worktree-path>            # from main checkout, never from inside the worktree
git branch -D <branch>                         # -d refuses on squash merges; -D only AFTER step 1+2 verification
git fetch --prune origin                       # REQUIRED — see below
git worktree prune && git worktree list
git branch -a                                  # must show no dead branches
```

**`git fetch --prune` is not optional.** When the forge auto-deletes the branch on
merge, `git push origin --delete` is a **no-op** — the remote branch is already gone —
and *nothing* removes the local `remotes/origin/<branch>` ref. `git branch -a` then
keeps listing branches that do not exist, and dead branches get re-reported as live
unmerged work. `ls-remote` saying "gone" is not the same as pruning the local view.

### 3.5 Now — and only now — take the checkout

Steps 4–6 edit tracked docs and commit them, so this is the first point that
genuinely needs `$default_branch` checked out on the main checkout. Re-run step 0's
checks, then:

```bash
git -C <main-checkout> checkout "$default_branch" && git -C <main-checkout> pull --ff-only   # NOT -q; you must be able to say what moved
```

Watch for `checkout: moving from <X> to <default_branch>` where `<X>` is not
`$default_branch` — you have just moved someone's workspace. If a host branch guard
blocks you here, that is the guard **working**: return to step 0 and ask, do not
bypass.

If a declared lock is held by another workstream and the user has not released it,
stop here. Steps 1–3 are already done and are the time-critical half (stranded
commits, ghost branches). Steps 4–7 are bookkeeping and can wait for the checkout —
say so and leave the changes unstaged rather than forcing them in.

### 4. Plan truthfulness — tick the checkboxes NOW

If the branch executed a tracked implementation plan, open the plan, tick every
completed step `[x]`, and add a merge annotation (PR #, merge/squash SHA, date). If
review rounds changed the approach, fix the plan text or excise stale code blocks (a
stale block that contradicts shipped code is worse than none). Record any override
rows that changed.

### 5. Tracking-doc reconciliation (out-of-branch residue)

The in-branch doc ripple covers docs you edited. This step finds the ones you didn't
across all tracked Markdown files (plus any non-Markdown tracking files declared under
`## Post-merge` in the host's doctrine):

```bash
git grep -il "<changed-surface-keyword>" -- '*.md'
```

For each hit, check: status cells and tables that describe the old behavior ("not
atomic", "pending", "in flight"), counts your change moved, and revision histories.
Update them, with dates.

### 6. Review-round sweep — file every deferred item & amend the ADR ledger

Re-read the review verdicts — PR comments (`gh pr view <N> --comments`) AND
in-session reviewer reports if reviews ran via subagents — for anything tagged
"follow-up", "out of scope", "pre-existing", or "not a blocker". **No `gh` or
non-GitHub host?** Sweep in-session subagent review reports and branch commit
messages, and ask the user for any external PR/MR review notes rather than skipping.
Each item gets **written into the durable tracking target declared under
`## Post-merge` in the host's doctrine** (or plan / project memory if appropriate)
before you move on. If `## Post-merge` declares no tracking target and deferred items
exist, **STOP and ask the user** where to file them — chat history is not a filing
system; unfiled follow-ups evaporate.

**Spec filing-claims audit.** If the merged branch shipped or implemented a spec,
grep the spec for "filed", "recorded in", "to be written", and "follow-up" claims and
verify each one resolves — the named doc exists, the named table has the row. Derive
the rows to add from the **spec's** own filing statements, never from the plan's
transcription of them.

**Spec-stage attribution (adversarial-review ledger input).** When filing a review
follow-up or a defect found in CI or production, record whether a spec-stage lens
could have caught it, and which one: `refuter` (a false claim about the current
system), `compliance` (an unnamed or misstated mandate), `sweeper` (partial
duplication of an existing responsibility), `hardening` (a recovery mechanism where
the producer should have been hardened), or `none`. Record that lens name in the
tracking entry itself (neither `LedgerRow` nor `LedgerAmendment` has a prose lens
field, and both models enforce `extra="forbid"`).

When the merged work had a spec-stage review under `adversarial-design-review` and
`(repo / ADR_REL).is_file()` is true, append a `LedgerAmendment` from the checkout
root:

```python
from acf.adr import LedgerAmendment, append_amendment, load_host_config
from acf.repo import ADR_REL, resolve_repo

repo = resolve_repo(None)
if (repo / ADR_REL).is_file():
    cfg = load_host_config(repo)
    append_amendment(
        LedgerAmendment(
            spec_path=spec_path,
            # The commit_sha of the last full 4-reviewer dispatch for spec_path:
            # among files in `repo / cfg.runs_dir` shaped
            # `<STEM>_v<N>_<YYYY-MM-DD>.md` (excluding `_response_` files), pick
            # the highest `(int(N), YYYY-MM-DD)` and read `<commit_sha>` from
            # line 3 (`Spec: `<spec_path>` @ `<commit_sha>``):
            commit_sha=dispatch_commit_sha,
            date=today_iso,
            # From the spec's own absorption/response record when the merged work
            # had a spec-stage review; pass None for any counter not measured here:
            absorbed=...,
            rejected=...,
            blocks_overturned=...,
            # Count of review follow-ups or CI/production defects from this merge
            # attributed to a spec-stage lens (refuter/compliance/sweeper/hardening):
            escapes=...,
        ),
        repo / cfg.ledger_path,
    )
```

**Single-source row identity (`dispatch_commit_sha`):** A controller verification pass
or user override after a blocked full run updates the spec's `**Adversarial review:**`
header to the verification-pass or override commit SHA, but writes **no** `LedgerRow`.
`LedgerAmendment` matches the prior `LedgerRow` by `spec_path` + `commit_sha`.
Meanwhile, `repo / cfg.runs_dir` also holds author response records named
`<SPEC_STEM>_v<N>_response_<date>.md`, which have no `Spec: ... @ ...` line, and
lexicographic sorting fails once `N >= 10`. Always resolve `dispatch_commit_sha` by
selecting the file in `repo / cfg.runs_dir` shaped `<STEM>_v<N>_<YYYY-MM-DD>.md`
(excluding `_response_` files) with the **highest `(int(N), YYYY-MM-DD)`** and reading
`<commit_sha>` from its line 3 (``Spec: `<spec_path>` @ `<commit_sha>` ``). Never take
`commit_sha` from the spec header and never parse the ledger file inline.

**Counter provenance (`absorbed`, `rejected`, `blocks_overturned`, `escapes`):**
`LedgerRow` writes zero counters at dispatch time. Fill `absorbed`, `rejected`, and
`blocks_overturned` from the spec's absorption/response record, and fill `escapes`
with the count of review follow-ups or CI/production defects attributed to a
spec-stage lens. Pass `None` for any counter not measured by this step — never
overwrite an unknown count with zero. `date` is required (`YYYY-MM-DD`) and has no
default. If the merged work had no spec-stage review, record `none` and skip
`append_amendment`.

### 6.5 Guard escape check — only if this slice retired a defect class

Skip when the slice shipped no guard and retired no defect class (docs, plan-only,
measurement slices). Otherwise ask exactly one question:

> **What ALREADY gets through the guard we just shipped? Name one live instance —
> file and line — or state, after actually searching, that you found none.**

Not "what *would* get through" — that phrasing yields categories and hypotheticals,
and every gap filed as a hypothetical so far was materially wrong until someone
hunted a live instance. The searched-for-and-found-none answer is recorded with the
search you ran, so the next reader can re-run it. File any live finding in the
durable tracking target declared under `## Post-merge` in the host's doctrine (if none
is declared, stop and ask the user where to file it). "Nothing — it checks the
behaviour, not a code shape" is a valid and valuable answer; write that down too, with
the evidence.

**A filed gap is a hypothesis, not a finding.** Whoever picks a gap up must re-derive
it against the live code before building on it.

Bias the answer toward **behaviour over shape**: a guard reasoning about a *value's
provenance* can assert harm; a guard reasoning about *code shape* can only assert
suspicion, and a new spelling walks straight past it. A guard that checks
declarations does not see the same defect hand-rolled in a helper body.

**A guard whose claimed scope exceeds its real scope is worse than no guard** — it
tells the next reader the question is settled. Check the guard's announced scope
against what it can actually see.

### 7. Memory / status notes

Update project memory entries whose status this merge changed (roadmap progress,
"in flight on node X", environment facts learned).

### 8. Report before moving on

Tell the user in one or two sentences what housekeeping found — including "nothing
stranded, docs clean", which step-2.5 process-sweep branch ran, and any host-specific
check reported as `<check>: not declared in ## Post-merge, skipped` — *then* start the
next task.

## Rationalizations vs Reality

| Excuse | Reality |
| --- | --- |
| "User is eager / it's 9pm — housekeeping can wait" | It waited 18 days once and cost a full false-alarm investigation. The checklist is ~10 minutes. |
| "Git says the branch is unmerged, so keep it" | Squash merges *always* look unmerged. Verify content, then delete. |
| "Every branch commit predates `mergedAt`, so nothing is stranded" | A timestamp says when a commit was made, not when it was pushed. Compare against `headRefOid`. Three commits were nearly lost this way on 2026-10-28. |
| "`git diff default_branch branch` was empty/clean" | That check is broken in both directions — use content presence + the stranded-commit log. |
| "Checkboxes are ceremony; the merge is the record" | Merged plans with unticked boxes read as "not started" to the next reader. Tick them. |
| "The reviewer's follow-up is small, I'll remember it" | Nobody remembered. File it or do it now. |
| "The branch docs were updated in-branch, so docs are done" | Out-of-branch docs (roadmaps, audits, inventories) drift independently — grep for them. |
| "Step 1 says checkout the default branch, so I'll checkout first" | It does not. Steps 1–2 are read-only (`git show "origin/$default_branch:<path>"`). A checkout there mutates a checkout other worktrees and sessions share, to answer a question that needs no mutation. |
| "It was probably already on the default branch" | Then the checkout was pointless; if it wasn't, you moved someone's workspace. Look first (step 0). Running it `-q 2>/dev/null` means you cannot answer "what did you change?" afterwards. |
| "The branch guard is in my way" | The guard is the other workstream telling you the checkout is theirs. Bypassing a host branch guard or editing another session's lock file are both off-limits — ask. |
| "`/health` says 200, the server is fine" | An in-memory health flag outlives the deletion of the server's backing directory. Probe a functional data endpoint (step 2.5) — a husk answers health and fails everything else. |
| "No worktree of mine spawned a server" | The sweep costs one command and catches *other* sessions' orphans too. A zombie once sat for three days across multiple housekeeping runs because nobody looked. |
| "I'm on Linux, the sweep is PowerShell" | It has a POSIX branch. Run it. |

## Red Flags — STOP and run the checklist

- About to say "let's start the next feature" within minutes of a merge
- A worktree or branch you can't immediately account for
- A background test-server listener you can't immediately account for
- A merged plan with unticked boxes
- Pushing anything to a feature branch after its PR merged
- A reviewer note containing "follow-up" or "out of scope" that isn't filed anywhere

## When NOT to use

- Mid-review iteration (PR open, worktree still needed) — keep the workspace.
- Branches the user explicitly said to keep.
- Worktrees owned by another node/session (check with the user before touching).
- **The shared main checkout itself, when another workstream holds it.** The same
  caution as worktrees applies to the shared checkout's HEAD: a branch lock declared
  under `## Post-merge`, an in-flight branch, or uncommitted work that is not yours.
  Steps 1–3 are still safe (read-only); stop before step 3.5.
