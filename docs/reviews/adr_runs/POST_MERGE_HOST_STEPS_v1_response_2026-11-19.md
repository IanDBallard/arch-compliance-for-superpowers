# Author response record — `docs/design/POST_MERGE_HOST_STEPS.md` v1

- **Spec:** `docs/design/POST_MERGE_HOST_STEPS.md`
- **Reviewed commit (v1):** `510b8626dd53ecaa712d434bb584fa89f949eb54`
- **Run detail answered:** `docs/reviews/adr_runs/POST_MERGE_HOST_STEPS_v1_2026-11-19.md`
- **Declared revision class:** mechanism. v2 changes:
  - the one-owner-per-concern rule, with a refusal for restatements;
  - where pre-flight runs (step 1a);
  - pre-flight outcomes (stop or carry; no remedies);
  - host-step dependency handling;
  - the single statement of the plan-record rule.
  
  The re-run is in full.

## Blocking reasons

### C11 — `load-bearing claim C11 (shape_fit) is REFUTED`

- **Blocking line:** `load-bearing claim C11 (shape_fit) is REFUTED: The shape exists: the skill reads host values from ## Post-merge as prose and reports a missing one as 'not declared ... skipped' ... so 'no second way' does not hold as stated.`
- **Resolution (revised text):**
  1. **Decision 2 ("One owner per concern") and the §4.1 table assign each concern one declaration:**
     - the shared checkout stays with the branch-lock bullet (step 0);
     - post-merge CI and deploy verification stay with the post-merge CI bullet (step 1);
     - checks on the merge itself go to `### Pre-flight`;
     - host actions go to `### Host steps`;
     - the plan-record rule goes to `### Plan record`.
     
     A sub-section that restates another owner's concern is refused and reported as `restates <owner>, not run`. That answers the sweeper's two `PARTIAL_OVERLAP` relationships: pre-flight against step 0 (`SKILL.md:62-67`), and host steps against step 1 (`SKILL.md:123-126`).
  2. **Decision 5:** a host step never verifies a deploy. It may only declare a precondition on step 1's recorded result.
  3. **Decision 6 and §4.2 (the converged finding and the `BOUNDARY_CUT`):** step 4 becomes the single statement of the plan-record rule. The description (`:3`), the Rationalizations row (`:387`) and the Red Flags bullet (`:402`) now refer to "the plan-record rule (step 4)". §4.3 asserts that `Tick them.` is absent.
  4. **§5 Shape fit** names each overlap and how decision 2 removes it.
  5. **A "Supersedes, in part" header line** answers the document conflicts: `POST_MERGE_HOUSEKEEPING_SKILL.md:36` (the list of four) and `:129` (the tick rule). The cleared spec is not edited.
- **Falsification command and output** (run at the v2 working tree, before commit):

```text
$ git grep -n "Post-merge" -- plugins/arch-compliance/python plugins/arch-compliance/hooks
(no output)

$ grep -n -E "Tick them|unticked|tick every|tick the checkboxes" plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md
3:description: ... unticked checkboxes in merged plans, or tracking docs that contradict merged code.
233:### 4. Plan truthfulness — tick the checkboxes NOW
235:If the branch executed a tracked implementation plan, open the plan, tick every
387:| "Checkboxes are ceremony; the merge is the record" | Merged plans with unticked boxes read as "not started" to the next reader. Tick them. |
402:- A merged plan with unticked boxes
```

The second command lists all five places the skill states or presupposes the tick rule: lines 3, 233, 235, 387 and 402. v2's §4.2 changes each of them: the description, the step 4 heading and body, the Rationalizations row and the Red Flags bullet. The claim "step 4 is the single statement" is falsified if a sixth hit appears, or if one of these five stays unchanged in the implementation. §4.3's absent-`Tick them.` assertion pins line 387.

## Other findings absorbed (not blocking)

- **C13 (sweep, refuted, not load-bearing).** §6 recipe B now matches by behaviour (`Post-merge|declared|declares|tick|unticked|checkbox`). A per-line table lists every reading site, including `:188-189`, `:193`, `:225-228` and `:412-413`, and says which ones the design touches. "New sites go next to an existing one" is gone.
- **Hardening: `$default_branch`.** Pre-flight is now step 1a, after `:80-87` resolves it.
- **Hardening and refuter: a mutating remedy, and outcomes that are not stops.** Decision 4: a check stops or carries, and a remedy goes to the user.
- **Hardening: dependent host steps.** Decision 5: a step that depends on a step that was not run is not run.
- **Sweeper: no absent report for Plan record.** Decision 3 and §4.3 add `plan record: not declared in ## Post-merge, portable rule applied`.
- **Refuter: citation precision.** The bullets are now cited at `ARCHITECTURE.md:323-326`.
- **Compliance advisory: `FORBIDDEN` is origin-host vocabulary only.** §4.3 now says so instead of relying on the test for every host.

## Sentence-type sweep

| # | Refutation-prone type | Hits in `docs/design/POST_MERGE_HOST_STEPS.md` v2 | Disposition |
|---|---|---|---|
| T1 | Population or consumer claim without a recipe | "Nothing in the package or hooks parses `## Post-merge`" (§3, decision 1) | Backed by §6 recipe A (no output) and a second method: the `ARCH_REL` consumers `acf/adr/host.py:30` and `hooks/inject_constraints.py:165-168` |
| T2 | Aggregate count or partition as a claim | "four sub-sections", "four conventions", "414 lines" | Each is enumerated beside the count (§1, §4.1 table). 414 is `wc -l` of `SKILL.md` at `e9dd881` |
| T3 | Universally quantified claim | "every line of the skill that reads a declared value" (§5) | Backed by §6 recipe B and its per-line table. The table states what the recipe could miss (a reading with none of the matched words) and that a full read found none |
| T4 | Prose-only measurement of tool or library behaviour | None | No tool behaviour is measured in prose |
| T5 | Named hook, method or attribute without an existence receipt | `ARCH_REL`, `test_housekeeping_skill_invariants`, `FORBIDDEN`, `$default_branch` resolution | Each carries a `file:line`: `repo.py:24`, `test_adr_skill_invariants.py:105-133`, `test_adr_skill_prose.py:14`, `SKILL.md:80-87` |
| T6 | Mandate or document attribution without the quoted trigger | `## Prose names no host`, `## Release discipline`, the superseded spec's decision 1 and step 4 | Each is quoted beside its citation (§2 decision 7, §3, the header) |
| T7 | Completeness claim backed only by a recipe validated on known sites | "five places the skill states the tick rule" | The grep's output is the census and is pasted above. The implementation is checked against it, and §4.3 pins the absence of `Tick them.` |
