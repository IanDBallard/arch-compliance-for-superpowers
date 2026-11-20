# Host Rules for `post-merge-housekeeping` — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let a host declare pre-flight checks, a plan record, tracking documents with closing rules, a filing rule, post-deploy actions and report fields in its doctrine's `## Post-merge`. Each is read by the one housekeeping step that owns its concern, so a host can cut over from a local copy without dropping steps.

**Architecture:** Prose-only change to one skill (`post-merge-housekeeping/SKILL.md`), pinned by its existing invariant test. The doctrine and version files follow. No Python package or hook code changes.

**Tech Stack:** Markdown skill prose, pytest. No new dependency.

**Spec:** `docs/design/POST_MERGE_HOST_STEPS.md` (v4, CLEARED_WITH_ABSORPTIONS, repo @ `d85d32da`; absorptions folded at `90fe465`). The spec's §4.2 is the authority for every prose edit. Its §6 table gives the line numbers at `e9dd881`, which are unchanged on this branch. Section references (§N) below are to that spec.

## Global Constraints

- **No host vocabulary in skill prose.** `## Prose names no host`: "Skill prose and runtime messages name no host repository, path or section." `plugins/arch-compliance/tests/test_adr_skill_prose.py` enforces its `FORBIDDEN` list; every example stays generic.
- **No backslash anywhere in skill prose** (`test_adr_skill_invariants.py:70-76`).
- **Record strings are exact.** Use them verbatim:
  - `post-merge verification: <value>`, with values `passed`, `failed`, `in progress`, `not declared in ## Post-merge, skipped`;
  - `pre-flight: not declared in ## Post-merge, skipped`;
  - `pre-flight: restates <owner>, not run`;
  - `plan record: not declared in ## Post-merge, portable rule applied`;
  - `tracking documents: not declared in ## Post-merge, skipped`;
  - `closing rule: not declared in ## Post-merge, portable rule applied`;
  - `filing rule: not declared in ## Post-merge, portable rule applied`;
  - `post-deploy actions: not declared in ## Post-merge, skipped`;
  - `post-deploy actions: verification <value>, not run`;
  - `<action>: not run (an earlier post-deploy action failed)`;
  - `report fields: not declared in ## Post-merge, skipped`.
- **Headings are exact:** `## Host declarations`, `### 2.2 Host pre-flight checks`, `### 6.7 Post-deploy actions`, `### 4. Plan truthfulness — record it NOW`.
- **Each rule is stated once, in the step that applies it** (decision 6). `## Host declarations` holds only the §4.1 ownership table.
- **The strings `Tick them.` and `post-merge CI check: not declared` must be gone from the skill.**
- **Version `0.3.3`** in `plugins/arch-compliance/.claude-plugin/plugin.json` and `pyproject.toml` (both `0.3.2` today).
- **Never `pip install -e` from this worktree.** The editable `acf` install points at the main checkout. Tests here read skill files relative to the test file, so they test this worktree's prose.
- **Verification**, from the worktree root: `PYTHONUTF8=1 python -m pytest -q`. The baseline at `90fe465` is recorded in Task 4 step 1.

## Review Focus

1. **A host declares post-deploy actions but its only declared verification is a CI workflow.** The record may be `passed` from that workflow's run, and the actions run. That is the spec's rule (§4.2 step 1). The prose must say so plainly, not leave it to inference. Pinned by the Task 1 string `counts toward passed`.
2. **A run where `gh` is absent and nothing is declared.** It must still produce exactly one record, `post-merge verification: not declared in ## Post-merge, skipped`, and no leftover `post-merge CI check` line. Pinned by Task 1's absence assertion.
3. **A host declares a plan record.** Step 4's merge annotation, stale-text fix and override-row sentences must survive unchanged. Pinned by Task 2's assertion that `add a merge annotation` and `Record any override` are still present.
4. **A multi-item run.** A pre-flight stop ends the run for every item before step 2.5, and step 2's cherry-pick waits for step 2.2. Pinned by Task 1's `once step 2.2 has run` string and the `### 2.2` heading preceding `### 2.5`.
5. **A later re-run of step 6.7.** It re-runs step 1's verification first, and step 8 names each action as run, failed or not run (§9 item 1). Pinned by Task 3's strings.

---

### Task 1: Step 1's single verification record, step 2.2 pre-flight, overview and `## Host declarations`

**Files:**
- Modify: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` (`:16-24` overview, before `:26` new section, `:123-126` step 1, `:139-140` step 2, between `:153` and `:155` new step 2.2)
- Test: `plugins/arch-compliance/tests/test_adr_skill_invariants.py` (`test_housekeeping_skill_invariants`, `:105-133`)

**Interfaces:**
- Produces:
  - the step-1 record `post-merge verification: <value>`, read by Task 3's step 6.7 and step 8;
  - step 2.2's carry facts, read by Task 2's steps 4 and 5;
  - the `## Host declarations` table, which Tasks 2 and 3 must not restate.

- [ ] **Step 1: Write the failing test.** Append to the `required` tuple in `test_housekeeping_skill_invariants`:
  - `"## Host declarations"`
  - `"### 2.2 Host pre-flight checks"`
  - `"post-merge verification: <value>"`
  - `"counts toward passed"`
  - `"pre-flight: not declared in ## Post-merge, skipped"`
  - `"restates <owner>, not run"`
  - `"once step 2.2 has run"`
  - `"portable rule applied"`

  After the loop, add:

  ```python
  assert "post-merge CI check: not declared" not in body
  assert body.index("### 2.2 Host pre-flight checks") < body.index("### 2.5 ")
  assert body.index("## Host declarations") < body.index("## The Checklist")
  ```

- [ ] **Step 2: Run it to verify it fails.**
  Run: `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_adr_skill_invariants.py::test_housekeeping_skill_invariants -q`
  Expected: FAIL, `missing required housekeeping invariant: ## Host declarations`.

- [ ] **Step 3: Edit the overview (`:16-24`).** Follow §4.2 "Overview".
  - Name every declaration: branch lock; daemon probe; post-merge CI with its post-deploy actions; tracking target with its filing rule; tracking documents with their closing rules; pre-flight checks; plan record; report fields. Each is read by one step (see `## Host declarations`).
  - Replace the sentence at `:23-24` with the three-form sentence quoted in §4.2. Its middle form, `<rule>: not declared in ## Post-merge, portable rule applied`, carries the `portable rule applied` pin.

- [ ] **Step 4: Insert `## Host declarations`** before `## The Checklist`. It is the §4.1 table, written generically, with columns Concern | Declaration in `## Post-merge` | Read by. It has one row per §4.1 row and states no rule. Add one sentence: a file may appear on both the tracking-documents and tracking-target bullets, because reconciling and filing are different concerns.

- [ ] **Step 5: Replace step 1's `:123-126` sentence** with the §4.2 step-1 text. It covers:
  - running every declared verification;
  - the one record and its four values;
  - "a CI workflow named on the post-merge CI bullet is a declared verification, and its run for the merge commit counts toward passed";
  - the `gh run list` result carried in the same record;
  - runs of workflows the bullet does not name never make it `passed`.

- [ ] **Step 6: Step 2 (`:139-140`).** After "Cherry-pick doc-only strays onto `$default_branch`", insert "once step 2.2 has run".

- [ ] **Step 7: Insert `### 2.2 Host pre-flight checks`** before `### 2.5`. Follow §4.2 "New `### 2.2`":
  - it runs in the main session once every step 1–2 result is collected, subagents included, and before step 2.5;
  - absent → `pre-flight: not declared in ## Post-merge, skipped`;
  - otherwise each check runs in order, once per run, against every merged item;
  - **stop** ends the run for every item, naming the item and the check and what the user should do;
  - **carry** is recorded for steps 4, 5 and 8;
  - a check on a concern `## Host declarations` gives another step → `pre-flight: restates <owner>, not run`;
  - a remedy that changes anything is reported to the user, never performed.

- [ ] **Step 8: Run the test and the prose test.**
  Run: `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_adr_skill_invariants.py plugins/arch-compliance/tests/test_adr_skill_prose.py -q`
  Expected: all pass.

- [ ] **Step 9: Commit.**

  ```bash
  git add plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md plugins/arch-compliance/tests/test_adr_skill_invariants.py
  git commit -m "feat(housekeeping): one post-merge verification record, host pre-flight checks (step 2.2), host declarations table"
  ```

---

### Task 2: Plan record (step 4), tracking documents and closing rule (step 5), filing rule (steps 6, 6.5), single tick statement

**Files:**
- Modify: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` (`:3`, `:233-236`, `:243-253`, `:262-266`, `:349-351`, `:387`, `:402`; line numbers shift after Task 1, so locate by the quoted text)
- Test: `plugins/arch-compliance/tests/test_adr_skill_invariants.py`

**Interfaces:**
- Consumes: step 2.2's carry facts (Task 1).

- [ ] **Step 1: Write the failing test.** Append to `required`:
  - `"### 4. Plan truthfulness — record it NOW"`
  - `"plan record: not declared in ## Post-merge, portable rule applied"`
  - `"tracking documents declared under ## Post-merge"`
  - `"tracking documents: not declared in ## Post-merge, skipped"`
  - `"closing rule: not declared in ## Post-merge, portable rule applied"`
  - `"filing rule: not declared in ## Post-merge, portable rule applied"`
  - `"the plan record (step 4)"`
  - `"add a merge annotation"`
  - `"Record any override"`

  Add `assert "Tick them." not in body` and `assert "non-Markdown tracking files declared" not in body`.

- [ ] **Step 2: Run it to verify it fails.**
  Run: `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_adr_skill_invariants.py::test_housekeeping_skill_invariants -q`
  Expected: FAIL, `missing required housekeeping invariant: ### 4. Plan truthfulness — record it NOW`.

- [ ] **Step 3: Step 4.**
  - Heading → `### 4. Plan truthfulness — record it NOW`.
  - Only the clause "tick every completed step `[x]`" changes, to "mark completed steps as the plan record under `## Post-merge` declares, or, if none is declared, tick every completed step `[x]`".
  - The merge annotation, stale-text and override-row text stays word for word.
  - Append the carry-facts sentence and the `plan record: … portable rule applied` record from §4.2.

- [ ] **Step 4: Step 5.**
  - "non-Markdown tracking files declared under `## Post-merge`" → "tracking documents declared under `## Post-merge`".
  - After "Update them, with dates.", add the §4.2 step-5 text: apply a declared closing rule per document; take carry facts into account; record the two absences (`tracking documents: … skipped`, `closing rule: … portable rule applied`).

- [ ] **Step 5: Steps 6 and 6.5.**
  - In each filing sentence, after "tracking target", add "following its declared filing rule (for example how an item's ID is allocated)".
  - Add the `filing rule: … portable rule applied` record once, in step 6, and have step 6.5 refer to it.
  - Leave both STOP sentences unchanged.

- [ ] **Step 6: Single tick statement.**
  - Description (`:3`): "unticked checkboxes in merged plans" → "merged plans whose status the plan record (step 4) has not recorded".
  - Rationalizations row (`:387`) → "'Checkboxes are ceremony; the merge is the record' | A plan whose status nobody recorded reads as 'not started'. Apply the plan record (step 4)."
  - Red Flags (`:402`) → "A merged plan whose status the plan record (step 4) has not recorded".

- [ ] **Step 7: Run the tests and recipe B.**
  Run: `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_adr_skill_invariants.py plugins/arch-compliance/tests/test_adr_skill_prose.py -q`
  Expected: all pass.
  Run: `git grep -n -i -E "tick|checkbox" -- plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md`
  Expected: two hits only. One is step 4's portable clause ("tick every completed step `[x]`"). The other is the Rationalizations row's quoted excuse ("Checkboxes are ceremony"), which states no rule.

- [ ] **Step 8: Commit.**

  ```bash
  git add plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md plugins/arch-compliance/tests/test_adr_skill_invariants.py
  git commit -m "feat(housekeeping): plan record, tracking documents with closing rules, filing rule; one statement of the tick rule"
  ```

---

### Task 3: Step 6.7 post-deploy actions and the step-8 report

**Files:**
- Modify: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` (new step between `### 6.5` and `### 7.`; step 8)
- Test: `plugins/arch-compliance/tests/test_adr_skill_invariants.py`

**Interfaces:**
- Consumes: Task 1's `post-merge verification` record; every `not run`, `portable rule applied` and carry record from Tasks 1–2.

- [ ] **Step 1: Write the failing test.** Append to `required`:
  - `"### 6.7 Post-deploy actions"`
  - `"post-deploy actions: not declared in ## Post-merge, skipped"`
  - `"post-deploy actions: verification <value>, not run"`
  - `"not run (an earlier post-deploy action failed)"`
  - `"re-runs step 1's verification first"`
  - `"report fields: not declared in ## Post-merge, skipped"`

  Add `assert body.index("### 6.5 ") < body.index("### 6.7 Post-deploy actions") < body.index("### 7. ")`.

- [ ] **Step 2: Run it to verify it fails.**
  Run: `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_adr_skill_invariants.py::test_housekeeping_skill_invariants -q`
  Expected: FAIL, `missing required housekeeping invariant: ### 6.7 Post-deploy actions`.

- [ ] **Step 3: Insert `### 6.7 Post-deploy actions`.** Follow §4.2:
  - no actions → `post-deploy actions: not declared in ## Post-merge, skipped`;
  - record not `passed` → `post-deploy actions: verification <value>, not run`, and the step says that a later run of step 6.7 re-runs step 1's verification first;
  - `passed` → run in declared order; a failure is reported, and each later action gets `<action>: not run (an earlier post-deploy action failed)`;
  - these run in the main session with no subagents in flight.

- [ ] **Step 4: Step 8.** Add the §4.2 step-8 list:
  - step 1's verification record;
  - every carry fact;
  - every `not run` and `portable rule applied` record from steps 2.2, 4, 5, 6, 6.5 and 6.7;
  - each post-deploy action as run, failed or not run (§9 item 1);
  - every declared report field, or `report fields: not declared in ## Post-merge, skipped`.

- [ ] **Step 5: Run the tests.**
  Run: `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_adr_skill_invariants.py plugins/arch-compliance/tests/test_adr_skill_prose.py -q`
  Expected: all pass.

- [ ] **Step 6: Commit.**

  ```bash
  git add plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md plugins/arch-compliance/tests/test_adr_skill_invariants.py
  git commit -m "feat(housekeeping): post-deploy actions gated on the verification record (step 6.7); step 8 reports every record"
  ```

---

### Task 4: Doctrine notes, version 0.3.3, full suite

**Files:**
- Modify: `config/architecture/ARCHITECTURE.md` (`## Declared, never defaulted` `:189-216`; `## Post-merge` `:319-328`)
- Modify: `plugins/arch-compliance/.claude-plugin/plugin.json:3`, `pyproject.toml:3`
- Test: `tests/test_self_host.py:57-61` (unchanged; must still pass)

- [ ] **Step 1: Record the baseline.**
  Run: `PYTHONUTF8=1 python -m pytest -q` at the commit before Task 1.
  Expected: record the pass count in the ledger. Every later run must match it, since this plan adds asserts to an existing test, not new tests.

- [ ] **Step 2: `## Post-merge`.**
  - The tracking-target bullet (`:326`) labels its existing rule: append "**Filing rule:** file with `gh issue create`, so filing a follow-up or guard escape never edits an already-cleared spec." Then delete the duplicate "so filing a follow-up…" clause from the bullet's first sentence, so the rule is stated once.
  - Add one line before the `No row` line: "This repository declares no pre-flight checks, plan record, tracking documents, post-deploy actions or report fields."
  - The `## Post-merge` heading and the line `No row: host operational declarations; no test enforces this.` stay byte-identical.

- [ ] **Step 3: `## Declared, never defaulted`.** After the review's built-in meanings sentence, add one sentence. `post-merge-housekeeping` gives three absent refinements a built-in meaning, recorded here:
  - an absent plan record → step 4 ticks completed steps;
  - an absent filing rule → steps 6 and 6.5 write the item into the target;
  - an absent closing rule → step 5 updates status cells.

  Each is reported as `<rule>: not declared in ## Post-merge, portable rule applied`.

- [ ] **Step 4: Version.** Change `0.3.2` → `0.3.3` in `plugin.json` and `pyproject.toml`.

- [ ] **Step 5: Full suite and diff gate.**
  Run: `PYTHONUTF8=1 python -m pytest -q`
  Expected: the step-1 count, all passing (including `tests/test_self_host.py`).
  Run: `PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main --call-site ci`
  Expected: exit 0.

- [ ] **Step 6: Commit.**

  ```bash
  git add config/architecture/ARCHITECTURE.md plugins/arch-compliance/.claude-plugin/plugin.json pyproject.toml
  git commit -m "chore: doctrine notes for host post-merge declarations; release 0.3.3"
  ```

---

### Task 5: Pull request (stop for approval), then post-merge

- [ ] **Step 1: STOP and ask the user before pushing.** Show the branch's commit list and the PR body draft. The body must name:
  - issue #50 as closed;
  - the Cayenne and HistoricMansions cutovers as adoption work this release unblocks: R5 in HistoricMansions' Workstream E table, and its `post-merge-housekeeping` cutover row;
  - the two §9 follow-ups (step 1 MISSING outcome; per-action "already done" check).

  It ends with "🤖 Generated with [Claude Code](https://claude.com/claude-code)".

- [ ] **Step 2: After the user approves, push and open the PR.** Bind it with the ccd_pr tools.

- [ ] **Step 3: After merge (user-approved), run `post-merge-housekeeping`.**
  - Reinstall the plugin; `python scripts/check_installed_skills.py <INSTALL_PATH>` must print `installed gate skills identical to the clone` (DoD 5).
  - File the two §9 follow-ups with `gh issue create`.
  - Append the `LedgerAmendment` for `dispatch_commit_sha` `d85d32dadb4868f6a8a46adc4513150648c843ee` (the v4 run).
