# Author response record — `docs/design/POST_MERGE_HOST_STEPS.md` v3

- **Spec:** `docs/design/POST_MERGE_HOST_STEPS.md`
- **Reviewed commit (v3):** `290a051791c16e7e3ea78cfaade4eb7e571888bd`
- **Run detail answered:** `docs/reviews/adr_runs/POST_MERGE_HOST_STEPS_v3_2026-11-19.md`
- **Declared revision class:** mechanism. v4 changes:
  - step 1 writes one `post-merge verification` record, which replaces today's `post-merge CI check: not declared` record, and `passed` needs a declared verification;
  - the plan record replaces one clause of step 4, not the paragraph;
  - step 5's existing tracking-files declaration becomes the named **tracking documents** bullet, which carries the closing rule (the closing rule leaves the tracking-target bullet);
  - the overview's report-form sentence is replaced so it states the three forms once;
  - carry facts reach steps 4 and 5; a deferred step 6.7 re-runs step 1's verification; step 2's cherry-pick waits for step 2.2.

  No element is added. The re-run is in full.

## Blocking reasons

### C12 — `load-bearing claim C12 (shape_fit) is REFUTED`

- **Blocking line:** `load-bearing claim C12 (shape_fit) is REFUTED: I checked the 4.1 table row by row against the skill. Three concerns end up with more than one declaration or record after this design lands. (1) Reconciliation ... (2) Step 1's verification result ... (3) Step 4's body ... Steps 0 and 1 hold as single owners ...`
- **Resolution (revised text):** each of the three takes the reviewer's `required_resolution`.
  1. **Reconciliation (`PARTIAL_OVERLAP` with `SKILL.md:244-245`).** §4.1 now has one row, "Which documents step 5 reconciles beyond its Markdown grep, and how items in them are closed", owned by the **tracking documents** bullet: today's "non-Markdown tracking files" declaration, named, with a closing rule per document. §4.2 step 5 rewrites `:244-245` to read that bullet. The closing rule is no longer on the tracking-target bullet. §4.1's note states that a file may appear on both bullets because reconciling (step 5) and filing (steps 6, 6.5) are different concerns, each with its own rule.
  2. **Step 1's record (`PARTIAL_OVERLAP` with `SKILL.md:123-126`).** Decision 5 and §4.2 step 1: one record, `post-merge verification: <value>`, which replaces the sentence at `:123-126` and its `post-merge CI check: not declared …` string. §4.3 asserts the old string is absent. `passed` needs at least one declared verification, so the converged finding (vacuous `passed`; unreachable "not declared" case on `gh` hosts) is closed: with none declared, the record is `not declared in ## Post-merge, skipped`, whether or not `gh` is present, and `gh run list` never makes it `passed` alone.
  3. **Step 4 (`BOUNDARY_CUT` with `SKILL.md:235-239`).** §4.2 step 4: only the clause "tick every completed step `[x]`" changes. The merge annotation, stale-text fix and override-row record stay unconditional (decision 2, §8 row).
- **Falsification command and output** (run at the v4 working tree, before commit):

```text
$ grep -n -E "post-merge CI check|post-merge verification" docs/design/POST_MERGE_HOST_STEPS.md | cut -c1-120
54:| Mark bug reports fixed only after the deploy is verified live | ...
99:5. **One post-merge verification record, and post-deploy actions read only it.** Step 1
100:   records one result, `post-merge verification: <value>`, which replaces today's
101:   `post-merge CI check: not declared …` record. `passed` requires at least one
179:  for steps 6.7 and 8, `post-merge verification: <value>`: `passed` when at least one
215:  `post-merge verification` record:
239:- `post-merge verification: <value>`;
246:It also asserts that `Tick them.` and `post-merge CI check: not declared` no longer
330:| 123-126 | Step 1: declared verification; `post-merge CI check: not declared …` | one `post-merge verification` r
367:   vocabulary, and `Tick them.` and `post-merge CI check: not declared` are gone.

$ grep -n -E "tracking files|tracking documents" docs/design/POST_MERGE_HOST_STEPS.md | cut -c1-120
42:reads "any non-Markdown tracking files declared under `## Post-merge`" (`SKILL.md:244-245`),
52:| Close tracked items the diff fixes | ...
152:| Which documents step 5 reconciles beyond its Markdown grep, and how items in them are closed | **tracking document
170:  with its filing rule, tracking documents with their closing rules, pre-flight checks,
203:- **Step 5** (`:243-253`): "non-Markdown tracking files declared under `## Post-merge`"
204:  becomes "the tracking documents declared under `## Post-merge`". After "Update them,
263:  tracking documents, filing rule, post-deploy actions or report fields. The
335:| 243-253 | Step 5: tracking-doc reconciliation, "non-Markdown tracking files declared" | tracking documents; closin

$ git grep -n "Post-merge" -- plugins/arch-compliance/tests tests
plugins/arch-compliance/tests/test_adr_skill_invariants.py:117:        "## Post-merge",
plugins/arch-compliance/tests/test_adr_skill_invariants.py:118:        "not declared in ## Post-merge, skipped",
tests/test_self_host.py:58:    assert "## Post-merge\n" in doctrine
```

Every `post-merge CI check` hit is the old record named as replaced or asserted absent; the only record the design writes is `post-merge verification`. Every "tracking files" hit is today's text, quoted where it is replaced by the tracking documents bullet. The answer is falsified if any §4.1 concern has two declarations or two records, or if step 4's annotation, stale-text or override-row duty is conditional on the plan record.

## Other findings absorbed (not blocking)

- **Hardening (important): a deferred step 6.7 has no record to read.** Decision 5 and §4.2 step 6.7: a later run of step 6.7 re-runs step 1's verification first.
- **Hardening (advisory): carry facts reach only step 8.** Decision 4 and §4.2 steps 4 and 5 now take step 2.2's carry facts into account.
- **Hardening (advisory): step 2's cherry-pick and `git fetch` before step 2.2.** §4.2 step 2 orders the cherry-pick after step 2.2. Decision 4's stop guarantee is restated as "before step 2.5 and before step 2's cherry-pick, so no process, branch, worktree, checkout or document has been changed"; `git fetch`'s remote-tracking refs are not among them.
- **Sweeper (advisory): the overview's single report form survives beside the new forms.** Decision 6 and §4.2 overview: the sentence at `:23-24` is replaced by one that states the three forms.
- **Sweeper (advisory): recipe C missed `tests/test_self_host.py:58-59`.** Recipe C now searches both test trees, and §4.3 and §4.4 say the new doctrine line goes before the `No row` line and changes neither pinned line.
- **Sweeper document conflicts.** `POST_MERGE_HOUSEKEEPING_SKILL.md:41` (the single report form) is now named in the Supersedes header with decision 1. `:129` was already named. `ARCHITECTURE.md:191` is the gate's `adr.yml` rule, which §4.4's new sentence in the same section sits beside without changing.

## Sentence-type sweep

| # | Refutation-prone type | Hits in `docs/design/POST_MERGE_HOST_STEPS.md` v4 | Disposition |
|---|---|---|---|
| T1 | Population or consumer claim without a recipe | "Nothing in the package or hooks parses `## Post-merge`" (§3, decision 1); "the test pins on `## Post-merge`" (§6) | Recipe A (no output) plus the `ARCH_REL` consumers; recipe C over both test trees, output pasted above |
| T2 | Aggregate count or partition as a claim | "four of them", "three built-in meanings", "three record forms", "Four of the new rules are refinements", "two bullets are new", "414-line" | Each is enumerated beside the count (§1 quote, decision 3, §4.2 overview text, §4.1 table). 414 is `wc -l` of `SKILL.md` at `e9dd881` |
| T3 | Universally quantified claim | "every step 1–2 result is collected", "every item", "each concern one declaration", "no process, branch, worktree, checkout or document has been changed" | The first two are procedure. The third is the §4.1 table, walked row by row in §5. The fourth is bounded by naming the two places changes begin (step 2.5, step 2's cherry-pick) and excludes remote-tracking refs by name |
| T4 | Prose-only measurement of tool or library behaviour | None | No tool behaviour is measured |
| T5 | Named hook, method or attribute without an existence receipt | `ARCH_REL`, `test_housekeeping_skill_invariants`, `FORBIDDEN`, `test_self_host.py` pins, step 2's cherry-pick sentence | `repo.py:24`, `test_adr_skill_invariants.py:105-133`, `test_adr_skill_prose.py:14`, `tests/test_self_host.py:58-59`, `SKILL.md:139-140` |
| T6 | Mandate or document attribution without the quoted trigger | `## Prose names no host`, `## Release discipline`, the superseded spec, Cayenne's rules | Each is quoted beside its citation (§2 decision 7, §3, the header, §1 table) |
| T7 | Completeness claim backed only by a recipe validated on known sites | "Recipe B ... lines 3, 233, 235, 387 and 402" | The grep output is the census decision 6 acts on; §4.3 pins the absence of `Tick them.`. The §6 edit table lists what the design edits and claims no more |
