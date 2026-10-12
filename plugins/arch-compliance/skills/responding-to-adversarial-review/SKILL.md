---
name: responding-to-adversarial-review
description: Use when an adversarial design review returns BLOCKED, when revising a spec against review findings, or when a spec has been blocked more than twice
---

# Responding to Adversarial Review

The gate blocks. This is what the **author** does next. `adversarial-design-review`
covers running the review and the cheap pre-dispatch stops; it does not cover
answering a finding.

**Core principle:** a finding cites where it was *found*, not where it *lives*.

This file is the procedure.

## 1. Triage before editing

Classify every finding first. They do not get the same response.

| Class | Tell | Response |
|---|---|---|
| Unswept propagation | The decision was already made elsewhere in the spec | Sweep (§2). Cheapest and most common. |
| Genuine defect | The mechanism or diagnosis is wrong | Redesign. Expensive. |
| Plan-time | Absorptions, advisories, "fold if you keep the design" | Record; do not fix now. |
| External-data UNPROVEN | Rests on data outside the tracked tree | Re-flag **not load-bearing**; do not "prove" it. |

**The signal that decides your whole response: was the *design* attacked, or only
its propagation?** If no reviewer attacked the mechanism, stop deliberating and run
a sweep pass.

**Re-run the design-simplification pass on every revision, not only the first
draft.** Use the host's design-simplification pass, if its doctrine defines one. Removability is
order-dependent: an element is often only visibly unnecessary after a *different*
element has been removed, so a pass that ran before the last revision has not seen
this one. The pass is cheap next to a re-run, and it is the only step here that asks
whether an element should exist at all; every other section of this skill assumes
the design and repairs its claims.

**Reviewer predicts class.** Compliance blocks skew **precision**; refuter and
hardening blocks skew **mechanism**. Recompute the current split from the ledger
rather than trusting a remembered figure:

```bash
python -c "
import json, collections
from acf.repo import resolve_repo
from acf.adr import load_host_config
repo = resolve_repo(None); cfg = load_host_config(repo)
rows = [json.loads(l) for l in open(repo / cfg.ledger_path, encoding='utf-8') if l.startswith('{')]
c = collections.Counter()
for r in rows:
    for lens, sev in (r.get('findings_by_lens_severity') or {}).items():
        c[lens] += sev.get('blocking', 0)
print(dict(c))"
```

## 2. Sweep the claim, not the cited line

For each decided change, in order:

1. State the claim in **one sentence**.
2. Grep the claim's **nouns** — 2–3 phrasings: the symbol, the section reference,
   the prose wording. Visiting the cited line is the recorded failure; a noun-net
   pass finds instances the report never cited.
3. **Validate the recipe before trusting it.** Run it and confirm every site already
   known — the review's citations, the spec's own census — appears in its hits. A
   recipe that cannot reproduce the known sites cannot be trusted on the unknown
   ones. Patterns inherit the blindness of the sites they were derived from: derive
   the recipe from the *claim* (the bare noun), then prove it against the known
   population.
4. Fix **every** hit, including slice tags, phase tags, Then-lists, decision rows,
   and change-surface entries. Implementers build task lists from those.
5. Re-run the same greps. Expect zero — a zero from an unvalidated recipe is not
   evidence (step 3).

Then run the controller's **pre-dispatch mechanical stop** (step 2b of
`adversarial-design-review`) on the revised spec *before* requesting a re-run:
literal tabs, placeholders, prior-verdict leaks, slice-tag vs sequencing, unresolved
citations. Run **§3 first**: the mechanical stop is syntactic — it passes a spec
whose new prose is false.

Three rules:

- **A finding recorded is not a finding fixed.** Writing it into a review record is
  provenance, not absorption. Absorption changes what a *planner* reads.
- **Fix the authoritative statement.** When prose and a table disagree, the table is
  what gets implemented from — and it is the one that keeps being left behind.
- **A deletion claim is a census obligation.** For every deletion the revision keeps,
  grep the deleted symbol *and its behaviour* across the tracked tree, then record the recipe and the measured counts **in the spec itself**
  — the census becomes the plan's acceptance instrument, re-run before each deletion
  task. A list enumerated from memory is always incomplete; a recipe recorded in the
  spec moves the refutation surface from the list to the recipe, which a reviewer
  can strengthen but rarely refute.

## 3. Verify the premises you just wrote

Before writing that a mandate, document, or module *owns* a rule: open it and quote
the line. A claim about what a document requires is refutable in one grep, and
reviewers run it.

**That rule generalizes, and the generalization is where revisions leak.** §2
propagates the *old* claim's fix; nothing in it looks at the sentences you wrote
*while* fixing. Premises authored during a response, immediately after reading the
relevant code, have blocked more runs than the original spec's premises did.

So, before requesting a mechanism-class re-run: author the **response record** at
the declared `runs_dir` as `<SPEC_STEM>_v<N>_response_<date>.md` (N = the blocked version
being answered). It carries: a header (spec path, reviewed commit, run-record
filename, declared revision class); **one entry per line of the blocked run detail's
`## Blocking reasons`** (by claim ID where the line names one, by quoted line
otherwise), each with its resolution — revised text, or **carried unchanged** with the
reason the refutation is answered without an edit (e.g. a `blocks_overturned`
refutation of the reviewer's evidence) — and the command that would *falsify* the
claim as answered, output pasted; and the **sentence-type sweep** (below). Commit the
record **on the branch that carries the revised spec, in or before the commit that
revises it** — the gate's step 2b-ii stops a re-run whose record is missing or
incomplete. Ten commands is a normal count, against a full re-run's cost (§4). A
revision that is precision-only end-to-end takes the controller verification pass
instead and owes no record.

Four rules the recorded failures earn:

- **Read the construct end-to-end** — `def` / `class` line to close. Never a window,
  never a filtered grep.
- **Existence is not fitness.** Naming an existing construct as your implementation
  device ("we will refuse via X", "Y already provides this hook") obligates reading
  X's definition end-to-end for **contract fit** — the parameters it requires, the
  invariants it assumes about its caller — not confirming X's line number. This is
  the hardening reviewer's implementability lens; run it on your own revision first.
- **Never assert a negative from an empty grep.** An empty result confirms the
  pattern missed, not that the thing is absent.
- **Quote adjacent, never paraphrase.** When a claim rests on someone else's words,
  the literal text goes beside the inference, in the same paragraph, where a
  mismatch is unmissable.

For a measurement the premise is the **input set**, not the computation. Print the
inputs before computing over them; a corrected algorithm over the wrong file
selection is stated as confidently as the first.

**Sentence-type sweep (required section of the response record).** Sweep the
*entire revised spec* — changed and carried text alike, since carried text was
authored under the same habits — for six refutation-prone sentence types; for each
hit either convert it to its replacement device or record why it stands. Each type
has produced at least one blocking verdict, and three recurred across successive
revisions until eliminated — which is why the sweep covers the whole spec, not the
diff.

| # | Refutation-prone type | Replacement device |
| --- | --- | --- |
| T1 | Population/consumer claim without a recipe | Shape recipe swept over the tree, validated against known sites before trusting negatives |
| T2 | Aggregate count or partition as a claim | Per-item disposition table, or the bare recipe — never a total as the claim |
| T3 | Universally quantified claim | Recipe backing the quantifier, or delete the quantifier |
| T4 | Prose-only measurement of tool/library behavior | In-tree executable pin (a committed test), not pasted output |
| T5 | Named hook/method/attribute without an existence receipt | `grep -n "def <name>"`-class receipt beside the claim |
| T6 | Mandate/doc attribution without the quoted trigger | The governing clause quoted adjacent to the inference |

The gate checks only that the section **exists** (presence, never quality).

## 4. Know what a re-run costs

Read the cost from the ledger, not from memory — figures carried in this file have
been wrong before. Exclude rows whose `tokens` is 0 or absent (unmeasured):

```bash
python -c "
import json, statistics
from acf.repo import resolve_repo
from acf.adr import load_host_config
repo = resolve_repo(None); cfg = load_host_config(repo)
rows = [json.loads(l) for l in open(repo / cfg.ledger_path, encoding='utf-8') if l.startswith('{')]
t = sorted(r['tokens'] for r in rows if r.get('outcome') and r.get('tokens'))
print('runs', len(t), 'median', statistics.median(t), 'p90', t[int(len(t)*0.9)], 'max', t[-1])"
```

The real cost of a preventable block is one full run's tokens **plus the wall-clock
of a blind dispatch plus the whole revision cycle** — enough to make every §2/§3 grep
pay for itself many times over, never enough to justify arguing a mechanism revision
down to a verification pass. When in doubt the gate treats a revision as mechanism;
the saving is in not introducing mechanism changes, not in arguing the class.

## 5. Stop conditions

- **Harm refuted twice** → the defect is probably not there. Consider retiring the
  spec to a filed gap rather than deriving a third harm story.
- **Blocking findings rising across your own revisions** → you are introducing
  faster than fixing. Stop editing; re-triage.
- **Design elements growing while you believe you are simplifying** → the
  simplification is not one.
- **A new false premise in each successive revision** → §3 is not being run. The
  gate is the audit, not your verification step.

## 6. Bookkeeping is part of the answer

A CLEARED or CLEARED_WITH_ABSORPTIONS run that skips the ledger row is how the
series became all-BLOCKED. Do not proceed to `writing-plans` until the controller
has re-read the row it just wrote. After merge, the host's post-merge process owns the
`absorbed` / `rejected` / `escapes` amendment — do not leave those at the write-time
zeros.

The response record (§3) is part of the same bookkeeping: it lives in
the declared `runs_dir`, is committed with the revision, and the spec body never
references it, prior verdicts, or reviewer roles (the step-2b archaeology stop still
applies to the spec).

Diagnosis belongs to the host's doctrine, not to this skill. Do not invent a competing owner.

## Common mistakes

- Fixing the cited line and moving on.
- Treating an advisory as a blocker, or a blocker as a wording fix.
- Answering an external-data UNPROVEN by adding more external data.
- Re-deriving a refuted harm instead of questioning the defect.
- Requesting a re-run before the mechanical stop is clean.
- Writing a claim broader than the evidence just gathered, then never re-testing it.
- Treating the gate as the step that verifies your premises.

## Related

`adversarial-design-review` is the gate. The host's doctrine owns diagnosis.
`superpowers:receiving-code-review` is the verify-don't-agree stance for code. GREEN is the next live re-run, not a claim
this file makes.
