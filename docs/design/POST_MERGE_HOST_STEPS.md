# Host Rules for `post-merge-housekeeping`, Each Read by the Step That Owns Its Concern

**Status:** v4 — draft for `/arch-compliance:adversarial-design-review`.
**Spec kinds:** `feature`
**Repo:** `IanDBallard/arch-compliance-for-superpowers`, `main` at `e9dd881` (release 0.3.2).
**Workstream:** HistoricMansions Workstream E, host roll-out step R5. Closes issue #50. A host
with a richer post-merge procedure than the portable skill can then cut over to it without
dropping steps.
**Supersedes, in part:** `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md` (v2, approved
2026-11-03). Its decision 1 lists four `## Post-merge` conventions and the single
"not declared … skipped" report form (`:36-41`); this design adds declarations, refines two
of the four and adds two report forms. Its checklist enumeration ("Its checklist steps
are:", `:104`, through step 8 at `:138`) gains steps 2.2 and 6.7, and its steps 1, 2, 4, 5,
6, 6.5 and 8 change as §4.2 lists. In particular its step 4 says "tick completed steps
`[x]`" (`:129`), and this design lets a host's declared plan record replace that one
clause. That spec's other content stands. It is not edited: an approved spec is not edited
after it clears.
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
reads "any non-Markdown tracking files declared under `## Post-merge`" (`SKILL.md:244-245`),
a fifth declaration the overview does not name. A host can declare *values* for those. It
cannot declare the rules below, each of which a live host procedure carries
(`cy:.claude/skills/post-merge-housekeeping/SKILL.md`, quoted):

| Host rule | Cayenne's text | Concern | Portable step that owns the concern today |
|---|---|---|---|
| A competing housekeeping run is already open | "Whether someone is already closing these books. Check this first, before writing a line" (`cy:...SKILL.md:21-28`, after Cayenne #60 and #61) | the merge itself | none |
| A cross-repository twin pull request has also merged | `cy:...SKILL.md:38-40` | the merge itself | none |
| The plan's status is a header, never ticks | "**Do not tick the checkboxes.** Where rulings amended steps during execution, ticking them asserts a history nobody verified; the header carries the truth instead" (`cy:...SKILL.md:65-66`) | how a merged plan's completed steps are marked | step 4, whose first sentence says "tick every completed step `[x]`" (`SKILL.md:235-236`) |
| Close tracked items the diff fixes | "For each `F-###` the body cites, read the diff and confirm the fix is there. A cited item the diff does not fix stays open" (`cy:...SKILL.md:76-83`) | reconciling tracking documents with the merge | step 5 (`SKILL.md:241-253`) |
| Take the next free item ID across the default branch and every open pull request | `cy:...SKILL.md:181-201` | filing deferred items into the tracking target | step 6 (`SKILL.md:262-266`) |
| Mark bug reports fixed only after the deploy is verified live | "mark each one **only after the deploy is verified live** above … Marking a report `fixed` **emails the tester**" (`cy:...SKILL.md:117-129`) | an action gated on the post-merge verification | step 1 verifies (`SKILL.md:117-126`); no step acts on its result |
| Extra report lines | `Gate:` and `Fixes:` (`cy:...SKILL.md:214-223`) | the end-of-run report | step 8 (`SKILL.md:372-377`) |

So a host whose procedure needs any of these must keep a local copy of the skill. That
leaves two live copies, which the workstream's strangler rule forbids, or a cutover that
silently drops steps.

This design gives each rule to the step that already owns its concern, as a refinement of
that step's declaration, and adds a declaration only where no step owns the concern: the
merge itself (pre-flight checks) and the report's extra fields. There is no general
"host steps" slot.

---

## 2. Decisions this design records

1. **Prose, not a parser.** The skill already reads `## Post-merge` as prose the agent
   interprets. No Python model, loader or test fixture parses it, and none is added (§6,
   recipe A). (author's call)
2. **Each host rule refines the declaration of the step that owns its concern.** §4.1 is
   the ownership table. A host rule is written on the owner's bullet in `## Post-merge`,
   and only the owning step reads it. A refinement replaces or extends exactly the clause
   §4.2 names, and the rest of the step stays unconditional. Two concerns have no owner
   today, and each gets one new bullet: **pre-flight checks** (checks on the merge
   itself) and **report fields**. (author's call)
3. **Declared, never defaulted.** An absent declaration adds nothing, and step 8 reports
   it as `<declaration>: not declared in ## Post-merge, skipped`. Three absent refinements
   have a built-in meaning, the skill's own portable clause: an absent plan record (step 4
   ticks), an absent filing rule (steps 6 and 6.5 write the item into the target) and an
   absent closing rule (step 5 updates status cells). Each is reported as `<rule>: not
   declared in ## Post-merge, portable rule applied`, and §4.4 records the three meanings
   in the doctrine's `## Declared, never defaulted`. (follows `## Declared, never
   defaulted`)
4. **Pre-flight checks read and decide. They never act.** Each check declares one of two
   outcomes:
   - **stop:** the run ends before step 2.5 and before step 2's cherry-pick of a stray, so
     no process, branch, worktree, checkout or document has been changed; the check's text
     says what the user should do;
   - **carry:** a fact recorded for steps 4, 5 and 8, such as "the twin pull request is
     unmerged, so the stage is in flight".

   A remedy that changes anything is reported for the user, never performed. A
   pre-flight check whose concern §4.1 gives to another step (the shared checkout, or
   whether the merge landed on the default branch) is not run, and is recorded as
   `pre-flight: restates <owner>, not run`. (author's call)
5. **One post-merge verification record, and post-deploy actions read only it.** Step 1
   records one result, `post-merge verification: <value>`, which replaces today's
   `post-merge CI check: not declared …` record. `passed` requires at least one
   verification declared on the post-merge CI bullet, and means every declared
   verification succeeded. Post-deploy actions, declared on the same bullet, run at step
   6.7 only when the record is `passed`, in declared order, and an action that fails stops
   the actions after it. A deferred step 6.7 re-runs step 1's verification first and
   reads the new record. (author's call)
6. **One statement of each rule.** Each rule is stated in the step that applies it. The
   new `## Host declarations` section of the skill holds only the §4.1 table, which names
   the owner and step for each concern and restates no rule. The skill's description, its
   Rationalizations row and its Red Flags bullet refer to "the plan record (step 4)"
   instead of restating ticking. The overview's report-form sentence is replaced, not
   appended to, so it states all three record forms once. (author's call)
7. **One release.** The skill text, its invariant test, the doctrine notes and the version
   bump to 0.3.3 land together. `## Release discipline`: "A change to a skill's prose
   bumps the plugin version" (`config/architecture/ARCHITECTURE.md:271-272`).

---

## 3. Non-goals

- Cayenne's cutover: writing its `## Post-merge` bullets and deleting
  `cy:.claude/skills/post-merge-housekeeping/` are a Cayenne adoption plan once this
  release ships, and that plan maps the rest of Cayenne's procedure. The same goes for
  HistoricMansions' cutover (its roadmap's `post-merge-housekeeping` row). §1's table
  names the rules that motivate the design, not every line of Cayenne's procedure.
- No portable check for a competing housekeeping run. Whether housekeeping lands through
  a pull request at all, and how one is recognised, is a host convention, so the check is
  a host's pre-flight declaration (§8).
- No change to steps 0, 2.5, 3, 3.5 or 7, and none to step 2 beyond the one sentence in
  §4.2 that orders its cherry-pick after step 2.2.
- No Python change. Nothing in the package or hooks parses `## Post-merge` (§6, recipe A).
- No host vocabulary in the skill. `## Prose names no host`: "Skill prose and runtime
  messages name no host repository, path or section"
  (`config/architecture/ARCHITECTURE.md:220-221`). Every example in the new prose is
  generic.

---

## 4. Design

### 4.1 Who owns what

| Concern | Declaration in `## Post-merge` | Read by |
|---|---|---|
| The shared checkout's HEAD, its lock or branch guard | branch-lock bullet (existing, unchanged) | step 0, again at step 3.5 |
| A worktree's background processes | daemon-probe bullet (existing, unchanged) | step 2.5 |
| Whether the merge landed on the default branch | none: step 1's content-presence check, which no host refines | step 1 |
| Post-merge CI and deploy verification | post-merge CI bullet (existing) | step 1, which writes the one verification record |
| Actions gated on that verification passing | post-merge CI bullet, refined with **post-deploy actions** | step 6.7 |
| Checks on the merge itself: a competing housekeeping run, a twin pull request | **pre-flight checks** bullet (new) | step 2.2 |
| How a merged plan's completed steps are marked | **plan record** bullet (new refinement of step 4's first clause) | step 4 |
| Which documents step 5 reconciles beyond its Markdown grep, and how items in them are closed | **tracking documents** bullet: today's "non-Markdown tracking files" declaration, named, refined with a **closing rule** per document | step 5 |
| Where deferred items and guard escapes are filed, and how | tracking-target bullet (existing), refined with a **filing rule** | steps 6, 6.5 |
| Extra report fields | **report fields** bullet (new) | step 8 |

Reconciling and filing are different concerns, so one file may be named on both the
tracking-documents bullet (what step 5 closes in it) and the tracking-target bullet (what
steps 6 and 6.5 add to it). Each bullet carries only its own concern's rule.

Every declaration is a bold-labelled bullet in the section body, as this repository
already writes them (`config/architecture/ARCHITECTURE.md:323-326`). A refinement is a
labelled sentence or sub-bullet inside its owner's bullet.

### 4.2 `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md`

- **Description** (`:3`): replace "unticked checkboxes in merged plans" with "merged plans
  whose status the plan record (step 4) has not recorded".
- **Overview** (`:16-24`): the list of conventions becomes the §4.1 declarations by name
  (branch lock, daemon probe, post-merge CI with its post-deploy actions, tracking target
  with its filing rule, tracking documents with their closing rules, pre-flight checks,
  plan record, report fields), each read by one step (see `## Host declarations`). The
  sentence at `:23-24` is replaced by: "Every declaration step 8 reports is recorded in one
  of three forms: `<declaration>: not declared in ## Post-merge, skipped`, `<rule>: not
  declared in ## Post-merge, portable rule applied`, or `<what>: … not run`."
- **New `## Host declarations`** (before `## The Checklist`): the §4.1 table, written
  generically. It names the owner and step for each concern and restates no rule.
- **Step 1** (`:117-126`): the sentence at `:123-126` is replaced by: "Also run every
  post-merge CI or deploy verification declared under `## Post-merge`. Record one result
  for steps 6.7 and 8, `post-merge verification: <value>`: `passed` when at least one
  verification is declared and every declared verification succeeded; `failed`; `in
  progress`; or `not declared in ## Post-merge, skipped` when none is declared. When `gh`
  is present, the same record also carries the `gh run list` result for the merge commit,
  which never makes it `passed` on its own."
- **Step 2** (`:139-140`): after "Cherry-pick doc-only strays onto `$default_branch`" add
  "once step 2.2 has run".
- **New `### 2.2 Host pre-flight checks`** (between steps 2 and 2.5). It runs in the main
  session once every step 1–2 result is collected, subagents included, and before step
  2.5. Read the pre-flight checks bullet. If it is absent, record `pre-flight: not
  declared in ## Post-merge, skipped`. Otherwise run each check in order, once per run,
  against every merged item:
  - a **stop** outcome ends the run for every item, naming the item and the check and
    saying what the user should do;
  - a **carry** outcome is recorded for steps 4, 5 and 8;
  - a check whose concern §4.1 gives to another step is not run, and is recorded as
    `pre-flight: restates <owner>, not run`.
- **Step 4** (`:235-236`): only the clause "tick every completed step `[x]`" changes. It
  becomes "mark completed steps as the plan record under `## Post-merge` declares, or, if
  none is declared, tick every completed step `[x]`". The merge annotation, the stale-text
  fix and the override-row record stay unconditional. Add: "Take step 2.2's carry facts
  into account (a stage recorded in flight is not marked complete). With no plan record
  declared, record `plan record: not declared in ## Post-merge, portable rule applied`."
  The heading becomes "Plan truthfulness — record it NOW".
- **Step 5** (`:243-253`): "non-Markdown tracking files declared under `## Post-merge`"
  becomes "the tracking documents declared under `## Post-merge`". After "Update them,
  with dates.", add: "Where a tracking document declares a closing rule, apply it to that
  document. Take step 2.2's carry facts into account. With no closing rule declared,
  record `closing rule: not declared in ## Post-merge, portable rule applied`."
- **Step 6** (`:262-266`) and **step 6.5** (`:349-351`): each item is written into the
  tracking target "following its declared filing rule (for example how an item's ID is
  allocated)". With none declared, record `filing rule: not declared in ## Post-merge,
  portable rule applied`.
- **New `### 6.7 Post-deploy actions`** between 6.5 (`:338`) and 7 (`:367`). Read the
  post-deploy actions on the post-merge CI bullet. If there are none, record
  `post-deploy actions: not declared in ## Post-merge, skipped`. Otherwise read step 1's
  `post-merge verification` record:
  - if it is not `passed`, record `post-deploy actions: verification <value>, not run`,
    and tell the user that a later run of step 6.7 re-runs step 1's verification first;
  - if it is `passed`, run the actions in declared order; an action that fails is
    reported, and each action after it is recorded as `<action>: not run (an earlier
    post-deploy action failed)`.

  These run in the main session with no subagents in flight, like everything from step
  3.5 on (`:38-42`).
- **Step 8** (`:372-377`): the report also lists step 1's verification record, every carry
  fact, every `not run` and `portable rule applied` record from steps 2.2, 4, 5, 6, 6.5 and
  6.7, and every field the report fields bullet declares, or `report fields: not declared
  in ## Post-merge, skipped`.
- **Rationalizations** (`:387`): the row becomes "'Checkboxes are ceremony; the merge is
  the record' | A plan whose status nobody recorded reads as 'not started'. Apply the plan
  record (step 4)."
- **Red Flags** (`:402`): the bullet becomes "A merged plan whose status the plan record
  (step 4) has not recorded".

### 4.3 Tests

`plugins/arch-compliance/tests/test_adr_skill_invariants.py::test_housekeeping_skill_invariants`
(`:105-133`) adds these to its required tuple (`:113-124`):
- `## Host declarations`, `### 2.2 Host pre-flight checks`, `### 6.7 Post-deploy actions`;
- `post-merge verification: <value>`;
- `pre-flight: not declared in ## Post-merge, skipped`;
- `restates <owner>, not run`;
- `portable rule applied`;
- `once step 2.2 has run`;
- `the plan record (step 4)`.

It also asserts that `Tick them.` and `post-merge CI check: not declared` no longer
appear in the body, so neither replaced statement can come back. The existing pin
`not declared in ## Post-merge, skipped` (`:118`) still holds.

`plugins/arch-compliance/tests/test_adr_skill_prose.py` already scans this skill against
`FORBIDDEN` (`HOUSEKEEPING`, `:14`). That list holds known origin-host vocabulary only, so
it cannot catch every host's words. The new prose is generic by construction (§3), and
the test needs no change.

`tests/test_self_host.py:58-59` pins this repository's `## Post-merge` heading and its
`No row: host operational declarations; no test enforces this.` line. §4.4 adds a line
between them and changes neither, so the test needs no change.

### 4.4 Doctrine, version, installed-skills check

- `config/architecture/ARCHITECTURE.md` `## Post-merge` (`:319-328`): add one line, before
  the `No row` line, saying this repository declares no pre-flight checks, plan record,
  tracking documents, filing rule, post-deploy actions or report fields. The
  installed-skills byte check stays under `## Release discipline` (`:272-276`), because it
  guards gate runs as well and checks the tooling, not the merge.
- `config/architecture/ARCHITECTURE.md` `## Declared, never defaulted` (`:189-216`): add
  one sentence recording the three built-in meanings of decision 3.
- `plugins/arch-compliance/.claude-plugin/plugin.json` and `pyproject.toml`: `0.3.2` →
  `0.3.3`.
- `scripts/check_installed_skills.py` already byte-checks `post-merge-housekeeping`
  (`config/architecture/ARCHITECTURE.md:273-275`). No change.

---

## 5. Shape fit

**What existing shape does this extend?** The host declaration in `## Post-merge`: bold
bullets the skill reads as prose, reporting an absent one as "not declared … skipped" and
never defaulting one (`SKILL.md:20-24`, `:62-64`, `:123-126`, `:180-184`, `:244-245`,
`:262-266`). Four of the new rules are refinements on the bullets of the steps that
already own them; step 5's existing tracking-files declaration is named; two bullets are
new.

**What second way does it create?** The §4.1 table is the check, row by row:
- **Shared checkout.** Still the branch-lock bullet only. A pre-flight check on it is
  refused as a restatement.
- **Landing on the default branch.** Still step 1's content-presence check only. A
  host's "base is the default branch" check is refused as a restatement; the content
  check already catches a merge into another base, because the content is missing from
  `origin/$default_branch`.
- **Deploy verification.** Still the post-merge CI bullet only, and step 1 writes one
  record of it, which replaces the record it writes today. Post-deploy actions read that
  record; they verify nothing.
- **Reconciliation.** One declaration, the tracking-documents bullet, names the documents
  step 5 reconciles and carries their closing rules.
- **Filing.** The tracking-target bullet only, with its filing rule.
- **Plan marking.** The plan record replaces one clause of step 4; the rest of step 4
  stays. The three other places that restated ticking refer to step 4.
- **Report forms.** The overview states the three forms once, replacing its single-form
  sentence.
- **Merge checks and report fields.** No existing declaration or step owns them (§1
  table, last column), so each new bullet is their only home.

**Lines touched.** §6's table lists, per line, each skill line this design edits and the
lines it places new steps between.

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

The skill lines this design edits, from a full read of the 414-line file at `e9dd881`:

| Lines | What they say today | Edit (§4.2) |
|---|---|---|
| 3 | Description: "unticked checkboxes in merged plans" | refer to the plan record (step 4) |
| 16-24 | Overview: the four conventions; the single "not declared … skipped" form | name every declaration; state the three record forms |
| 25-26 | Blank line, then `## The Checklist` | `## Host declarations` inserted before it |
| 123-126 | Step 1: declared verification; `post-merge CI check: not declared …` | one `post-merge verification` record |
| 139-140 | Step 2: "Cherry-pick doc-only strays onto `$default_branch`" | "once step 2.2 has run" |
| 153-155 | End of step 2; `### 2.5` heading | `### 2.2` inserted between |
| 233 | Step 4 heading | "record it NOW" |
| 235-236 | Step 4: "tick every completed step `[x]`" | the plan record or the portable clause; carry facts |
| 243-253 | Step 5: tracking-doc reconciliation, "non-Markdown tracking files declared" | tracking documents; closing rule; carry facts |
| 262-266 | Step 6: file into the declared tracking target | follow a declared filing rule |
| 349-351 | Step 6.5: file a live escape in the declared tracking target | follow a declared filing rule |
| 365-367 | End of step 6.5; `### 7.` heading | `### 6.7` inserted between |
| 372-377 | Step 8: the report | list the new records and report fields |
| 387 | Rationalizations: "Tick them." | refer to the plan record (step 4) |
| 402 | Red Flags: "A merged plan with unticked boxes" | refer to the plan record (step 4) |

Recipe B finds the tick rule's statements, which decision 6 reduces to one:

```bash
git grep -n -i -E "tick|checkbox" -- plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md
```

Output at `e9dd881`: lines 3, 233, 235, 387 and 402 (236 continues the sentence begun at
235). Each is in the table above.

Recipe C, the test pins on `## Post-merge`, in both test trees:

```bash
git grep -n "Post-merge" -- plugins/arch-compliance/tests tests
```

Output: `plugins/arch-compliance/tests/test_adr_skill_invariants.py:117-118` and
`tests/test_self_host.py:58`, whose next line (`:59`) pins the section's `No row` line.
§4.3 covers each.

---

## 7. Definition of done

1. `SKILL.md` carries the changes listed in §4.2. The new prose contains no `FORBIDDEN`
   vocabulary, and `Tick them.` and `post-merge CI check: not declared` are gone.
2. `test_housekeeping_skill_invariants` pins the strings in §4.3, asserts the two
   absences, and passes. `pytest -q` passes from the repository root, including
   `tests/test_self_host.py`.
3. `config/architecture/ARCHITECTURE.md` carries the `## Post-merge` "declares none" line
   and the `## Declared, never defaulted` sentence (§4.4).
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
| A host writes a rule on the wrong bullet, or as a pre-flight check | Decision 2 and §4.1 give each concern one declaration. A pre-flight check on another step's concern is refused as `pre-flight: restates <owner>, not run` and reported in step 8 |
| A pre-flight check's remedy changes something | Decision 4: checks only stop or carry, and a stop comes before step 2.5 and step 2's cherry-pick. Remedies go to the user |
| A side-effecting post-deploy action (one that emails users) runs on an unverified deploy | Decision 5: it runs only on `passed`, which needs at least one declared verification. A host whose actions need a live deploy declares a deploy check on the same bullet; `gh run list` alone never makes the record `passed` |
| A post-deploy action is deferred while verification is in progress | Decision 5: a later run of step 6.7 re-runs step 1's verification and reads the new record |
| A later post-deploy action runs on a failed earlier one's missing output | Decision 5: a failed action stops the actions after it |
| A host's plan record drops step 4's other duties | Decision 2: the plan record replaces one clause; the annotation, stale-text fix and override-row record stay |
| Every host must re-declare the competing-run check | Accepted (§3): recognising a competing housekeeping run is host-specific, so it stays a declaration |
| A multi-item run stops for one item's pre-flight check | Decision 4: a stop ends the run for every item before anything is changed; the user re-runs without that item |
