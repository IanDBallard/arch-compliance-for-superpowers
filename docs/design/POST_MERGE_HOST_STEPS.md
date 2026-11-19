# Host Pre-flight Checks, Plan Record and Host Steps for `post-merge-housekeeping`

**Status:** v2 — draft for `/arch-compliance:adversarial-design-review`.
**Spec kinds:** `feature`
**Repo:** `IanDBallard/arch-compliance-for-superpowers`, `main` at `e9dd881` (release 0.3.2).
**Workstream:** HistoricMansions Workstream E, host roll-out step R5. Closes issue #50. A host
with a richer post-merge procedure than the portable skill can then cut over to it without
dropping steps.
**Supersedes, in part:** `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md` (v2, approved
2026-11-03). Its decision 1 lists four `## Post-merge` conventions (`:36-41`), and this
design adds four optional sub-sections. Its step 4 design says "tick completed steps `[x]`"
(`:129`), and this design lets a host's declared plan-record rule replace that. That spec's
other content stands. It is not edited: an approved spec is not edited after it clears.
**Governing mandates:** `config/architecture/ARCHITECTURE.md` sections `## Declared, never
defaulted` (`:189-216`), `## Prose names no host` (`:218-228`), `## No completeness claims`
(`:244-254`), `## Release discipline` (`:269-279`), `## Single point of definition`
(`:281-298`) and `## Post-merge` (`:319-328`).
**No state-machine surface.** The design adds or modifies no state machine and no
transition.

---

## 0. Citation convention

Unprefixed paths are this repository at `e9dd881`. Paths prefixed `cy:` are the sibling
repository `IanDBallard/Cayenne` at `fffc2954` (`main`). They are cited as the live
instance that motivates the design. No step of the design reads or writes them. The rules
relied on are quoted beside each citation.

---

## 1. Goal

`plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` reads a host's
operational conventions from the `## Post-merge` section of the host's doctrine. The
skill's overview names four of them (`SKILL.md:20-24`): "shared-checkout branch lock,
worktree daemon probe, post-merge CI workflows, and durable tracking target". Step 5 also
reads "any non-Markdown tracking files declared under `## Post-merge`" (`SKILL.md:244-245`).
A host can declare *values* for those. It cannot declare:

1. **A check on the merge itself, run before any teardown.** Examples:
   - Cayenne's "Whether someone is already closing these books. Check this first, before
     writing a line" (`cy:.claude/skills/post-merge-housekeeping/SKILL.md:21-28`, written
     after two sessions opened competing housekeeping pull requests, Cayenne #60 and #61);
   - its check that the merge's base is `main` (`:31-35`);
   - its check that a cross-repository twin pull request has also merged (`:38-40`).

   These are about the merge, not about the shared checkout's HEAD, which is all step 0's
   branch lock covers (`SKILL.md:62-67`).
2. **A plan-record rule that differs from step 4.** Step 4 says "open the plan, tick every
   completed step `[x]`, and add a merge annotation" (`SKILL.md:235-236`). Cayenne's rule
   is the opposite: "**Do not tick the checkboxes.** Where rulings amended steps during
   execution, ticking them asserts a history nobody verified; the header carries the truth
   instead" (`cy:...SKILL.md:65-66`).
3. **A host step with its own rules.** Examples:
   - closing `F-###` items in `cy:SpecificationDocumentation/FIX_ROADMAP.md` against the
     diff (`cy:...SKILL.md:76-83`);
   - taking the next free `F-###` across `main` and every open pull request (`:181-201`);
   - marking in-app bug reports fixed, which emails each tester, so it may run only after
     the deploy is verified live (`:117-129`).
4. **The host's report fields.** Cayenne's report has `Gate:` and `Fixes:` lines
   (`cy:...SKILL.md:214-223`) that step 8's one-or-two-sentence report does not carry.

So a host whose procedure needs any of these must keep a local copy of the skill. That
leaves two live copies, which the workstream's strangler rule forbids, or a cutover that
silently drops steps. This design adds four optional sub-sections to `## Post-merge`:
`### Pre-flight`, `### Plan record`, `### Host steps` and `### Report`. Each is the single
place for its concern, and none restates a concern an existing declaration already owns.

---

## 2. Decisions this design records

1. **Prose, not a parser.** The skill already reads `## Post-merge` as prose the agent
   interprets. No Python model, loader or test fixture parses it, and none is added (§6,
   recipe A). (author's call)
2. **One owner per concern.** The table in §4.1 assigns each concern to exactly one
   declaration:
   - the shared checkout's HEAD and lock stay with the branch-lock bullet (step 0);
   - post-merge CI and deploy verification stay with the post-merge CI bullet (step 1);
   - checks on the merge itself go to `### Pre-flight`;
   - host actions go to `### Host steps`;
   - the plan-record rule goes to `### Plan record`.

   A sub-section that restates a concern another declaration owns (a pre-flight check on
   the checkout lock, a host step that verifies a deploy) is a doctrine error. The skill
   reports it in step 8 as `<sub-section>: restates <owner>, not run` and does not run
   it. (author's call)
3. **Declared, never defaulted.** An absent sub-section adds nothing, and step 8 reports
   it: `pre-flight: not declared in ## Post-merge, skipped`, `host steps: not declared in
   ## Post-merge, skipped`, `report: not declared in ## Post-merge, skipped`. An absent
   `### Plan record` leaves the skill's own rule in force, reported as `plan record: not
   declared in ## Post-merge, portable rule applied`. (follows `## Declared, never
   defaulted`)
4. **A pre-flight check reads and decides. It never acts.** Each check declares one of
   two outcomes:
   - **stop:** the run ends, and the check's text says what the user should do;
   - **carry:** a fact recorded for later steps, such as "the twin pull request is
     unmerged, so the stage is in flight".

   A remedy that changes anything (adding to an existing pull request, cherry-picking
   onto the default branch) is reported for the user, never performed by the check.
   Pre-flight runs as step 1a, after step 1 has resolved `$default_branch` and before
   step 1 verifies content. It can use the default branch, and it runs while every step
   is still read-only. (author's call)
5. **Host steps add work and depend only on what is recorded.** They run as step 6.7,
   after step 6.5 and before step 7, in declared order. A host step may declare a
   precondition on step 1's recorded post-merge CI or deploy result, or on an earlier
   host step's result. If the precondition does not hold (that check failed or was not
   run), the step is recorded as `<host step>: precondition unmet (<what>), not run`, and
   any step that depends on it is not run either. A host step never verifies a deploy
   itself (decision 2). (author's call)
6. **One statement of the plan-record rule.** Step 4 states the rule once: the host's
   `### Plan record` if declared, else the portable tick rule. The skill's description,
   its Rationalizations row and its Red Flags bullet refer to "the plan-record rule
   (step 4)" instead of restating ticking. (author's call)
7. **One release.** The skill text, its invariant test, the doctrine note and the version
   bump to 0.3.3 land together. `## Release discipline`: "A change to a skill's prose
   bumps the plugin version" (`config/architecture/ARCHITECTURE.md:271-272`).

---

## 3. Non-goals

- Cayenne's cutover: its `## Post-merge` sub-sections and the deletion of
  `cy:.claude/skills/post-merge-housekeeping/` are a Cayenne adoption plan once this
  release ships. The same goes for HistoricMansions' cutover (its roadmap's
  `post-merge-housekeeping` row).
- No change to steps 0, 2, 2.5, 3, 3.5, 5, 6, 6.5 or 7 beyond the sentences that hand off
  to the new sub-sections.
- No Python change. Nothing in the package or hooks parses `## Post-merge` (§6, recipe A).
- No host vocabulary in the skill. `## Prose names no host`: "Skill prose and runtime
  messages name no host repository, path or section"
  (`config/architecture/ARCHITECTURE.md:220-221`). Every example in the new prose is
  generic.

---

## 4. Design

### 4.1 Who owns what

| Concern | Single owner | Read at |
|---|---|---|
| The shared checkout's HEAD, its lock or branch guard | the branch-lock bullet (existing) | step 0, and again at step 3.5 |
| A worktree's background processes | the daemon-probe bullet (existing) | step 2.5 |
| Post-merge CI and deploy verification | the post-merge CI bullet (existing) | step 1 |
| Where deferred items are filed | the tracking-target bullet (existing), plus step 5's tracking files | steps 5, 6, 6.5 |
| Checks on the merge itself: who else is housekeeping it, its base, its twins | `### Pre-flight` (new) | step 1a |
| How a merged plan's status is recorded | `### Plan record` (new) | step 4 |
| Host actions after the portable steps | `### Host steps` (new) | step 6.7 |
| Extra report fields | `### Report` (new) | step 8 |

The existing declarations stay bullets in the section body, as this repository writes
them (`config/architecture/ARCHITECTURE.md:323-326`).

### 4.2 `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md`

- **Description** (`:3`): replace "unticked checkboxes in merged plans" with "merged plans
  whose status the plan-record rule (step 4) has not recorded".
- **Overview** (`:16-24`): after the four declared conventions, add one sentence naming the
  four sub-sections and pointing to a new `## Host sub-sections` section.
- **New `## Host sub-sections`** (before `## The Checklist`): the §4.1 table and decisions
  2–5, written generically, including the `restates <owner>, not run` rule.
- **Step 1** (`:74-126`): after `$default_branch` is resolved (`:80-87`), insert
  **`### 1a. Host pre-flight checks`**. Read `### Pre-flight`. If it is absent, record
  `pre-flight: not declared in ## Post-merge, skipped`. Otherwise run each check in order.
  - A **stop** outcome ends the run, saying which check stopped it and what it tells the
    user to do.
  - A **carry** outcome is recorded and restated in step 8.
  - A check that restates a concern §4.1 gives another owner is not run, and is recorded
    as `pre-flight: restates <owner>, not run`.
- **Step 4** (`:233-239`): the heading becomes "Plan truthfulness — record it NOW". The
  body opens with "The plan-record rule is the host's `### Plan record` under
  `## Post-merge` if declared, and otherwise the rule below." Then comes the existing tick
  rule, unchanged, as the portable rule. If no `### Plan record` is declared, record
  `plan record: not declared in ## Post-merge, portable rule applied`.
- **New `### 6.7 Host steps`** between 6.5 (`:338`) and 7 (`:367`). Read `### Host steps`.
  If it is absent, record `host steps: not declared in ## Post-merge, skipped`. Otherwise
  run each in declared order under decisions 2 and 5:
  - check its precondition against what is recorded;
  - a step whose precondition does not hold is recorded as `<host step>: precondition
    unmet (<what>), not run`;
  - a step that depends on a step that was not run is not run either;
  - a step that fails is reported, and steps that do not depend on it still run.

  These steps run in the main session with no subagents in flight, like everything from
  step 3.5 on (`:38-42`).
- **Step 8** (`:372-377`): add "every carry fact from step 1a, and every field the host's
  `### Report` declares, or `report: not declared in ## Post-merge, skipped`".
- **Rationalizations** (`:387`): the row becomes "'Checkboxes are ceremony; the merge is
  the record' | A plan whose status nobody recorded reads as 'not started'. Apply the
  plan-record rule (step 4)." Add a row: "A host step looks redundant with a portable
  step, so skip it | It is there because the portable step missed something on that host.
  Run both; report both."
- **Red Flags** (`:402`): the bullet becomes "A merged plan whose status the plan-record
  rule (step 4) has not recorded".

### 4.3 Tests

`plugins/arch-compliance/tests/test_adr_skill_invariants.py::test_housekeeping_skill_invariants`
(`:105-133`) adds these to its required tuple (`:113-124`):
- `### Pre-flight`, `### Plan record`, `### Host steps`, `### Report`;
- `pre-flight: not declared in ## Post-merge, skipped`;
- `host steps: not declared in ## Post-merge, skipped`;
- `plan record: not declared in ## Post-merge, portable rule applied`;
- `precondition unmet`, `restates <owner>, not run`;
- `the plan-record rule (step 4)`.

It also asserts that `Tick them.` no longer appears in the body, so the old unconditional
restatement cannot come back.

`plugins/arch-compliance/tests/test_adr_skill_prose.py` already scans this skill against
`FORBIDDEN` (`HOUSEKEEPING`, `:14`). That list holds known origin-host vocabulary only, so
it cannot catch every host's words. The new prose is generic by construction (§3), and
the test needs no change.

### 4.4 Doctrine, version, installed-skills check

- `config/architecture/ARCHITECTURE.md` `## Post-merge` (`:319-328`): add one line saying
  this repository declares no `### Pre-flight`, `### Plan record`, `### Host steps` or
  `### Report`.
- `plugins/arch-compliance/.claude-plugin/plugin.json` and `pyproject.toml`: `0.3.2` →
  `0.3.3`.
- `scripts/check_installed_skills.py` already byte-checks `post-merge-housekeeping`
  (`config/architecture/ARCHITECTURE.md:273-275`). No change.

---

## 5. Shape fit

**What existing shape does this extend?** The host declaration in `## Post-merge`. The
skill reads host values from it as prose, reports an absent one as "not declared …
skipped", and never defaults one (`SKILL.md:20-24`, `:62-64`, `:123-126`, `:180-184`,
`:244-245`, `:262-266`). The four sub-sections are more declarations in the same section,
read the same way.

**What second way does it create?** None, by decision 2 and the §4.1 table.
- **The checkout vs the merge.** The branch lock still owns the shared checkout.
  `### Pre-flight` owns checks on the merge, which no existing declaration covers, and a
  pre-flight check on the checkout is refused as a restatement.
- **Deploy verification.** The post-merge CI bullet still owns it. A host step can only
  depend on its recorded result, and a host step that verifies a deploy is refused as a
  restatement.
- **The plan-record rule.** Stated once, in step 4. The three other places that restated
  it now refer to step 4.

**Pattern sweep.** §6, recipe B lists, by behaviour, every line of the skill that reads a
declared value or states the plan-record rule. Every line the design touches is in that
list.

---

## 6. Premise verification (authoring time, 2026-11-19, at `e9dd881`)

Recipe A, any package or hook code that reads the doctrine's `## Post-merge`:

```bash
git grep -n "Post-merge" -- plugins/arch-compliance/python plugins/arch-compliance/hooks
```

Output: no lines. The second method is the consumers of `ARCH_REL`
(`plugins/arch-compliance/python/acf/repo.py:24`):
- `plugins/arch-compliance/python/acf/adr/host.py:30` checks that the file exists;
- `plugins/arch-compliance/hooks/inject_constraints.py:165-168` injects the doctrine text
  as context, truncated, and parses no section.

Recipe B, the skill's lines that read a declared value or state the plan-record rule. It
matches by what the line does, not by the string `Post-merge`:

```bash
git grep -n -i -E "Post-merge|declared|declares|tick|unticked|checkbox" -- plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md
```

| Lines | What they do | Touched by this design |
|---|---|---|
| 3 | Description: "unticked checkboxes in merged plans" | yes: refers to the plan-record rule |
| 20-24 | Overview: the four conventions; the "not declared … skipped" rule | yes: names the sub-sections |
| 62-67 | Step 0: the branch lock or guard; STOP | no: the owner of the checkout concern |
| 74, 117, 123-125 | Step 1: post-merge CI and deploy verification | yes: step 1a goes after `:80-87` |
| 180-183, 188-189, 193 | Step 2.5: the daemon probe and the host's declared data endpoint | no |
| 225-228 | Step 3.5: a host branch guard; a declared lock is held | no: the same owner as step 0 |
| 233, 235 | Step 4: the tick rule | yes: the single statement of the plan-record rule |
| 244-245 | Step 5: declared tracking files | no |
| 262-264, 350-351 | Steps 6 and 6.5: the declared tracking target | no; step 6.7 goes after 6.5 |
| 376 | Step 8: report the not-declared checks | yes: adds carry facts and report fields |
| 387 | Rationalizations: "Tick them." | yes: refers to the plan-record rule |
| 402 | Red Flags: "A merged plan with unticked boxes" | yes: refers to the plan-record rule |
| 412-413 | When NOT to use: a declared branch lock | no |

Line 138 ("A post-merge push") matches `Post-merge` but reads no declaration. Lines 2 and
6 are the skill's name and title. The table leaves those three out. A behaviour this
recipe could miss would read a host value with none of these words. Reading the whole file
(414 lines) found no such line.

Recipe C, the test pins:

```bash
git grep -n "Post-merge" -- plugins/arch-compliance/tests
```

Output: `test_adr_skill_invariants.py:117-118`. These are the two strings §4.3 adds to.

---

## 7. Definition of done

1. `SKILL.md` carries the changes listed in §4.2. The new prose contains no `FORBIDDEN`
   vocabulary, and `Tick them.` is gone.
2. `test_housekeeping_skill_invariants` pins the strings in §4.3, asserts `Tick them.` is
   absent, and passes. `pytest -q` passes from the repository root.
3. `config/architecture/ARCHITECTURE.md` `## Post-merge` carries the one-line "declares
   none" note (§4.4).
4. The version is `0.3.3` in `plugin.json` and `pyproject.toml`.
5. After the merge, the plugin is reinstalled and `scripts/check_installed_skills.py`
   reports the installed copy identical to the clone.
6. The PR body names issue #50 as closed. It also names the Cayenne and HistoricMansions
   cutovers as adoption work this release unblocks: R5 in HistoricMansions' workstream E
   table, and its `post-merge-housekeeping` cutover row.

---

## 8. Risks

| Risk | Mitigation |
|---|---|
| A host declares the same concern twice | Decision 2 gives each concern one owner. The skill refuses the restatement as `restates <owner>, not run` and reports it in step 8 |
| A pre-flight check's remedy changes something | Decision 4: checks only stop or carry. Remedies go to the user in the report |
| A side-effecting host step (one that emails users) runs before its precondition holds | Decision 5: the precondition is checked against step 1's recorded result, and an unmet one means not run. A host that declares no precondition owns that choice in its doctrine |
| A later host step runs on a failed earlier step's missing output | Decision 5: a step that depends on a step that was not run is not run either |
| The prose grows the skill past easy reading | §4.2 adds one section and two short steps. The §4.1 table is the single statement, and the steps point to it |
