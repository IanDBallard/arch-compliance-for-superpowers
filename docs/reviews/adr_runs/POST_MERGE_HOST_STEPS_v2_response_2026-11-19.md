# Author response record — `docs/design/POST_MERGE_HOST_STEPS.md` v2

- **Spec:** `docs/design/POST_MERGE_HOST_STEPS.md`
- **Reviewed commit (v2):** `021aa834a67d8a4d7661f90a9a698e47d73e7031`
- **Run detail answered:** `docs/reviews/adr_runs/POST_MERGE_HOST_STEPS_v2_2026-11-19.md`
- **Declared revision class:** mechanism. v3 changes:
  - the generic `### Host steps` slot is removed;
  - each host rule becomes a refinement on the bullet of the portable step that owns its concern: closing rule (step 5) and filing rule (steps 6, 6.5) on the tracking-target bullet, post-deploy actions (new step 6.7) on the post-merge CI bullet, plan record (step 4);
  - new declarations only where no step owns the concern: pre-flight checks (merge checks, now step 2.2) and report fields;
  - step 1 records the verification result that post-deploy actions read;
  - pre-flight moves from step 1a to step 2.2, in the main session after every step 1–2 result is collected;
  - the `restates <owner>` refusal now applies to pre-flight checks only.

  The re-run is in full.

## Blocking reasons

### C12 — `load-bearing claim C12 (shape_fit) is REFUTED`

- **Blocking line:** `load-bearing claim C12 (shape_fit) is REFUTED: The checkout (step 0, SKILL.md:62-68), deploy verification (SKILL.md:123-126) and plan-record parts hold. The tracking concern does not. ... Two of the three host steps that motivate the design (spec 1, item 3) do exactly that job with host rules. ... Otherwise ### Host steps becomes a second place to declare how items are filed and reconciled. ... That is a second way to declare one concern, which the claim says cannot exist.`
- **Resolution (revised text):** v3 takes the sweeper's own `required_resolution` for both relationships.
  1. **`PARTIAL_OVERLAP` with step 6 (`SKILL.md:262-266`):** the next-free-ID rule is now a **filing rule** on the tracking-target bullet, read by steps 6 and 6.5 (§4.1 row "Filing deferred items and guard escapes"; §4.2 step 6 and 6.5 edits).
  2. **`BOUNDARY_CUT` with step 5 (`SKILL.md:243-253`):** closing items against the diff is now a **closing rule** on the tracking-target bullet, read by step 5 only (§4.1 row "Reconciling tracking documents with the merge"; §4.2 step 5 edit).
  3. **No generic slot remains.** `### Host steps` is gone. The one motivating host action no step owned, deploy-gated bug-report marking, is a **post-deploy action** on the post-merge CI bullet, run at step 6.7 only when step 1 recorded `passed` (decision 5). §1's table now names, for each motivating rule, the portable step that owns its concern today. §5 walks the §4.1 table row by row.
  4. **The sweeper's advisory `PARTIAL_OVERLAP` for the base check (`SKILL.md:89-107`)** is resolved the way it proposed: §4.1 names step 1's content-presence check as the owner of "landed on the default branch", and a pre-flight base check is refused as a restatement.
- **Falsification command and output** (run at the v3 working tree, before commit):

```text
$ grep -n -i -E "host steps?\b|### Host|### Pre-flight|### Plan record|### Report" docs/design/POST_MERGE_HOST_STEPS.md
62:"host steps" slot.

$ grep -n "restates <owner>" docs/design/POST_MERGE_HOST_STEPS.md
93:   `pre-flight: restates <owner>, not run`. (author's call)
173:    `pre-flight: restates <owner>, not run`.
215:- `restates <owner>, not run`;
345:| A host writes a rule on the wrong bullet, or as a pre-flight check | ... refused as `pre-flight: restates <owner>, not run` and reported in step 8 |

$ grep -n -E "closing rule|filing rule" docs/design/POST_MERGE_HOST_STEPS.md | cut -c1-110
78:   an absent plan record (step 4 ticks), an absent filing rule (steps 6 and 6.5 write the
79:   item into the target) and an absent closing rule (step 5 updates status cells). Each is
143:| Reconciling tracking documents with the merge | tracking-target bullet, refined with a **closing rule**,
144:| Filing deferred items and guard escapes | tracking-target bullet, refined with a **filing rule** | steps
156:  declare pre-flight checks, a plan record, a filing rule, a closing rule, post-deploy
179:  target declares a closing rule, apply it to the documents it names. Otherwise record
180:  `closing rule: not declared in ## Post-merge, portable rule applied`."
182:  tracking target "following its declared filing rule (for example how an item's ID is
183:  allocated)". With none declared, record `filing rule: not declared in ## Post-merge,
231:  this repository declares no pre-flight checks, plan record, filing rule, closing rule,
261:- **Tracking.** Still the tracking-target bullet only. Closing and filing rules are
297:| 243-253 | Step 5: tracking-doc reconciliation | apply a declared closing rule |
298:| 262-266 | Step 6: file into the declared tracking target | follow a declared filing rule |
299:| 349-351 | Step 6.5: file a live escape in the declared tracking target | follow a declared filing rule |
```

The first command shows the only surviving "host steps" text is the sentence that says there is no such slot. The second shows the refusal applies only to pre-flight checks. The third shows the closing and filing rules are declared on the tracking-target bullet and read only by steps 5, 6 and 6.5. The answer is falsified if any §4.1 concern has two declarations, or if a motivating rule in §1's table has no owning step in §4.1.

## Other findings absorbed (not blocking)

- **C14 (sweep, refuted, not load-bearing).** The completeness claim is gone. §6 now lists, per line, only the skill lines the design edits and the lines new steps go between. Recipe B is narrowed to the tick rule (`tick|checkbox`), whose output (3, 233, 235, 387, 402; 236 continues 235) is the census decision 6 acts on. The `cfg` reads in step 6 read `adr.yml`, not `## Post-merge`, and the design does not touch them.
- **Refuter (important): step 1 records no pass/fail result.** §4.2 step 1 now records `post-merge verification: passed | failed | in progress | not declared …`, and step 6.7 reads it.
- **Refuter: the Supersedes header names only decision 1 and step 4.** It now also names the checklist enumeration (`:104` to `:138`) and the steps that change.
- **Hardening and sweeper: multi-item delegation of pre-flight.** Pre-flight is now step 2.2, in the main session after every step 1–2 result is collected, once per run; a stop ends the run for every item before step 2.5's first mutation (decision 4, §8).
- **Hardening: a host step with no precondition runs unconditionally.** Gone with host steps. Post-deploy actions have one fixed precondition, step 1's `passed` record, and never run without a declared verification.
- **Hardening: the competing-run check could be portable.** Rejected in §3 and §8: recognising a competing housekeeping run (whether housekeeping lands by pull request at all) is host-specific.
- **Sweeper: step 8 has no duty to report the new records.** §4.2 step 8 now lists carry facts, every `not run` and `portable rule applied` record, and report fields.
- **Sweeper: the installed-skills check as a pre-flight.** §4.4: it stays under `## Release discipline`, because it guards gate runs too and checks tooling, not the merge.
- **Compliance: the absent-plan-record meaning is not recorded in `## Declared, never defaulted`.** §4.4 adds a sentence there recording all three built-in meanings (plan record, filing rule, closing rule).
- **Compliance: decisions 4–5 repeated in the skill's new section and the step bodies.** Decision 6: the new `## Host declarations` section holds only the ownership table, and each rule is stated once, in its step.

## Sentence-type sweep

| # | Refutation-prone type | Hits in `docs/design/POST_MERGE_HOST_STEPS.md` v3 | Disposition |
|---|---|---|---|
| T1 | Population or consumer claim without a recipe | "Nothing in the package or hooks parses `## Post-merge`" (§3, decision 1) | Backed by §6 recipe A (no output) and a second method, the `ARCH_REL` consumers `acf/adr/host.py:30` and `hooks/inject_constraints.py:165-168` |
| T2 | Aggregate count or partition as a claim | "four of them", "three declarations", "three built-in meanings", "four of the new rules are refinements; two are new bullets", "414-line" | Each count is enumerated beside it (§1 quote, decision 3, §4.1 table). 414 is `wc -l` of `SKILL.md` at `e9dd881` |
| T3 | Universally quantified claim | "every step 1–2 result is collected", "every item", "each concern one declaration" | The first two are procedure, not claims about the tree. The third is the §4.1 table itself, checked row by row in §5. The former "every line that reads a declared value" claim is deleted |
| T4 | Prose-only measurement of tool or library behaviour | None | No tool behaviour is measured |
| T5 | Named hook, method or attribute without an existence receipt | `ARCH_REL`, `test_housekeeping_skill_invariants`, `FORBIDDEN`, step 2.5's first mutation | `repo.py:24`, `test_adr_skill_invariants.py:105-133`, `test_adr_skill_prose.py:14`; step 2.5 begins at `SKILL.md:155`, and the §6 table cites the insertion point `153-155` |
| T6 | Mandate or document attribution without the quoted trigger | `## Prose names no host`, `## Release discipline`, the superseded spec, Cayenne's rules | Each is quoted beside its citation (§2 decision 7, §3, the header, §1 table) |
| T7 | Completeness claim backed only by a recipe validated on known sites | "Recipe B ... Output at `e9dd881`: lines 3, 233, 235, 387 and 402" | The grep output is the census decision 6 acts on, pasted in §6; §4.3 pins the absence of `Tick them.`. The §6 edit table is a list of what the design edits, not a completeness claim |
