# Adversarial design review — full detail

Spec: `docs/design/POST_MERGE_HOST_STEPS.md` @ `d85d32dadb4868f6a8a46adc4513150648c843ee`
Kinds: feature
Outcome: **CLEARED_WITH_ABSORPTIONS**
Claims: 19 · Reviewers: 4 · Converged: 1

## Absorptions

- SUBSUMED: "a host 'merged into the default branch' pre-flight check" shares responsibility 'verify the merge landed on the default branch' with plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:105-107 — Consume step 1's content-presence check. The spec already refuses such a pre-flight check as a restatement of step 1.
- IDENTICAL: 'post-merge verification record' shares responsibility 'record the outcome of post-merge CI/deploy verification' with plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:123-126 — Replace the existing 'post-merge CI check: not declared' record with the one new record, as the spec does, and pin the absence of the old one in the invariant test.
- SUBSUMED: 'plan record refinement' shares responsibility "mark a merged plan's completed steps" with plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:235-236 — Generalize step 4's clause so the portable tick becomes the built-in instance of a declared plan record. The spec does this, and the description, Rationalizations and Red Flags lines refer to step 4.
- SUBSUMED: 'closing rule on the tracking documents bullet' shares responsibility 'close or update tracked items the merge fixed' with plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:244-253 — Extend step 5's existing tracking-files declaration, named, with a per-document closing rule. The status-cell update is the built-in instance.
- SUBSUMED: 'filing rule on the tracking-target bullet' shares responsibility 'decide how deferred items are written into the tracking target' with config/architecture/ARCHITECTURE.md:326 — Have the existing bullet's filing text become this host's declared filing rule rather than recording 'no filing rule' in §4.4.
- SUBSUMED: 'report fields bullet' shares responsibility 'decide what the end-of-run report lists' with plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:372-377 — Treat report fields as a refinement read by step 8, not as an unowned concern, and align decision 2 and §5 with the §1 table.

## Converged findings

- [2 reviewers: refuter, hardening] Step 1's rule that the gh run list result never makes the verification record passed on its own is ambiguous for a host whose declared post-merge verification is itself a CI workflow read through gh, as this repository's post-merge CI bullet declares; whether such a host's record can ever be passed is unstated.
  - evidence: `config/architecture/ARCHITECTURE.md:325`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:20-24; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:244-245; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:62-64; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:180-184; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:262-266; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:372-377`
- reasoning: I read the whole skill at d85d32d. The overview names exactly four conventions (:20-22). Step 5 alone reads 'non-Markdown tracking files declared under ## Post-merge' (:244-245), which the overview does not list. Every other ## Post-merge read is one of the four: the branch lock (:62-64), the daemon probe (:180-184), the post-merge CI/deploy check (:123-126) and the tracking target (:262-266, :350-351). No step reads a declaration for checks on the merge itself, a plan-marking rule, a filing rule or closing rule, an action gated on verification, or extra report fields. Step 8 (:372-377) reports only the 'not declared' form and has no host-declared fields.

#### C2 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:235-236; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:241-253; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:262-266; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:117-126; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:372-377; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:128-153`
- reasoning: I checked each row of the ownership column. Steps 0-2 (:44-153) check the checkout, content presence and stranded commits. None of them checks for a competing housekeeping run or a twin PR. Step 4's first sentence ticks every completed step (:235-236). Step 5 reconciles tracking docs (:241-253). Step 6 files deferred items into the tracking target (:262-266). Step 1 runs gh run list and any declared verification (:117-126) but records no result for a later step to act on, and no later step reads it. Step 8 is the report (:372-377).

#### C3 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:117-126; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:374-377`
- reasoning: Step 1 runs 'gh run list --branch "$default_branch" --limit 5' and 'any post-merge CI or deploy verification declared'. The only record it names is 'post-merge CI check: not declared in ## Post-merge, skipped', written when gh is absent and nothing is declared (:124-126). Step 8 (:374-377) lists only 'not declared ... skipped' checks, process-sweep branch and stranded/docs findings, so no pass/fail verification record exists today.

#### C4 — SURVIVED
- evidence: `C:/Users/iball/AppData/Local/Temp/claude/87e26b93c6dabf01/7ee83bd0-9038-461f-98de-0102609a84f5/scratchpad/cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:21-28; cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:38-40; cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:65-66; cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:76-83; cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:117-129; cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:181-201; cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:218; cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:220`
- reasoning: I opened the Cayenne snapshot at the cited lines. :21-28 is the open-PR check citing #60/#61. :38-40 is the RecipeParser twin check. :65-66 is 'Do not tick the checkboxes'. :76-83 closes F-### items against the diff. :117-129 marks bug reports only after the deploy is verified live and says marking emails the tester. :181-201 takes the next free ID from main and every open PR. The report block (:214-223) carries Gate: (:218) and Fixes: (:220). Each quote matches.

#### C5 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:24; plugins/arch-compliance/python/acf/adr/host.py:30; plugins/arch-compliance/hooks/inject_constraints.py:165-168`
- reasoning: I ran 'git grep -n "Post-merge" -- plugins/arch-compliance/python plugins/arch-compliance/hooks' at d85d32d and it returned no lines. 'git grep ARCH_REL' shows the package and hook consumers. host.py:30 calls require_file only. inject_constraints.py:165-168 reads the whole text and truncates it to _ARCH_EXCERPT_MAX without parsing any section. The other ARCH_REL users are skill prose (acf-mandate, architecture-review, which parse anchors or read the whole doc) and tests/test_self_host.py. None is package or hook code that parses ## Post-merge.

#### C6 — SURVIVED
- evidence: `C:/Users/iball/AppData/Local/Temp/claude/87e26b93c6dabf01/7ee83bd0-9038-461f-98de-0102609a84f5/scratchpad/cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:1-3; config/architecture/ARCHITECTURE.md:319-328`
- reasoning: Cayenne's skill is a host-local copy (its frontmatter describes Cayenne-specific files). §4 edits only this repo's skill, its test, its doctrine and its versions. This repo's own ## Post-merge (ARCHITECTURE.md:319-328) is the only host doctrine the change touches, and its test pin (tests/test_self_host.py:58-59) is unaffected. No step in §4.2-§4.4 reads or requires a Cayenne or HistoricMansions declaration.

#### C7 — SURVIVED
- evidence: `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:36-41; docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:104; docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:129; docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:138`
- reasoning: I numbered the lines of the approved spec. :36 introduces the ## Post-merge conventions, :37-40 are the four, and :41 is the 'not declared in ## Post-merge, skipped' rule. :104 ends with 'Its checklist steps are:'. :129 says 'tick completed steps [x]'. :138 is Step 7/Step 8. The spec is supersede-only, which is consistent with no edit to that file in the design.

### Unanchored findings

- **advisory**: The new step-1 rule says the gh run list result 'never makes it passed on its own'. It does not say whether a declared post-merge CI workflow that is checked through gh run list counts as a declared verification. This repo's own declaration is exactly such a workflow, so whether its record can ever be 'passed' is ambiguous.
  - evidence: `config/architecture/ARCHITECTURE.md:325`
- **advisory**: Decision 4 says a stop at step 2.2 leaves nothing changed. Step 1 already ran 'git fetch origin', which updates remote-tracking refs. The no-change guarantee holds for the listed objects (process, branch, worktree, checkout, document) but not for the refs.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:80`

### Looked for but did not find

- any package or hook code under plugins/arch-compliance/python or plugins/arch-compliance/hooks that matches 'Post-merge' (git grep returned nothing)
- a tick/checkbox statement in the housekeeping SKILL.md outside lines 3, 233, 235, 387 and 402 (recipe B re-run)
- a test pin on 'Post-merge' outside test_adr_skill_invariants.py:117-118 and tests/test_self_host.py:58 (recipe C re-run)
- an existing step in SKILL.md that acts on step 1's verification result
- a version other than 0.3.2 in plugin.json or pyproject.toml
- a mismatch between the cited ARCHITECTURE.md section line ranges (:189, :218, :244, :269, :281, :319) and the actual headings

## compliance

### Claim verdicts

#### C8 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:196-204; docs/design/POST_MERGE_HOST_STEPS.md:196-211; docs/design/POST_MERGE_HOST_STEPS.md:266-267`
- reasoning: The section says 'no default stands in for a missing declaration' but also sets the precedent the design follows: 'The review gives some absent or empty values a built-in meaning, recorded here' (:196-204). The design records the three built-in meanings (absent plan record means step 4 ticks; absent closing rule means step 5 updates status cells; absent filing rule means steps 6/6.5 write the item) in that section (§4.4, :266-267). Each one is reported as 'portable rule applied' at the step that applies it (§4.2 step 4 :199-201, step 5 :205-207, steps 6/6.5 :208-211). Every other absent declaration adds nothing and is reported 'not declared ... skipped'. No value is silently substituted, and the existing STOP when no tracking target is declared (SKILL.md:264-266) is untouched. The claim holds.

#### C9 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_skill_prose.py:14; plugins/arch-compliance/tests/test_adr_skill_prose.py:31-39; config/architecture/ARCHITECTURE.md:220-228`
- reasoning: Doctrine: 'Skill prose and runtime messages name no host repository, path or section'. Its row checks against 'the enumerated FORBIDDEN list of known origin-host (HistoricMansions) vocabulary' (:226-227). test_adr_skill_prose.py already includes HOUSEKEEPING/SKILL.md in FILES (:14, :21), and FORBIDDEN (:31-39) holds origin-host vocabulary only. The new prose in §4.2 uses generic labels (pre-flight checks, plan record, closing rule, filing rule, report fields) and names no Cayenne or HistoricMansions path. The cy: citations are only in the spec. The test needs no change, as claimed.

#### C10 — SURVIVED
- evidence: `plugins/arch-compliance/.claude-plugin/plugin.json:3; pyproject.toml:3; config/architecture/ARCHITECTURE.md:271-276`
- reasoning: The doctrine says 'A change to a skill's prose bumps the plugin version in plugin.json and pyproject.toml', and the installed copy of post-merge-housekeeping is byte-checked by scripts/check_installed_skills.py before a gate or housekeeping run. Both files are at 0.3.2 today (plugin.json:3, pyproject.toml:3). The design bumps both to 0.3.3 (§4.4) and runs the installed-skills check after the merge (§7 item 5). Keeping that check under ## Release discipline rather than making it a host pre-flight declaration matches the doctrine: the check guards gate runs as well as housekeeping runs, and it checks the tooling, not the merge.

#### C11 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:283-285; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:3; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:387; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:402; docs/design/POST_MERGE_HOST_STEPS.md:166-232`
- reasoning: The mandate requires 'exactly one canonical implementation that every call site consumes' for a shared decision procedure. A case-insensitive grep for tick|checkbox finds lines 3, 233, 235, 387 and 402, matching the spec's recipe B. §4.2 rewrites every one of them: the description, the Rationalizations row and the Red Flags bullet now point to 'the plan record (step 4)'. Step 4 alone states the rule. The new ## Host declarations section holds only the ownership table, and the overview's single report-form sentence (SKILL.md:23-24) is replaced rather than added to. Each new rule is stated only in the step that applies it: the restatement refusal in 2.2, the gate on verification passing in 6.7. The design meets the mandate as applied to skill prose.

### Unanchored findings

- **advisory**: Decision 3 says every absent declaration is reported in step 8 as '<declaration>: not declared in ## Post-merge, skipped', but §4.2's step 5 gives a record only for an absent closing rule. It gives none for an absent tracking-documents bullet, so that one absence goes unreported, against the design's own reading of ## Declared, never defaulted.
  - evidence: `docs/design/POST_MERGE_HOST_STEPS.md:203-207`

### Looked for but did not find

- High-frequency miss, completeness claim without a recipe: §6 recipes A, B and C back the 'no lines', tick-line and test-pin claims. I re-ran B and C with Grep and they match (SKILL.md:3,233,235,387,402; test_adr_skill_invariants.py:117-118; tests/test_self_host.py:58-59).
- High-frequency miss, a default that re-enters for a declared value: none. A declared plan record, closing rule or filing rule replaces the portable clause, and the portable clause applies only when nothing is declared.
- High-frequency miss, host name in skill prose: the new prose is generic, and the cy: citations stay in the spec.
- High-frequency misses, stdlib exception mixin and subprocess without an encoding: not touched (no Python change, §3).
- High-frequency miss, a check re-implemented instead of consumed: no new snippet re-implements acf.registry or acf.repo logic.
- ## One owner for host paths (executable skill snippets): no new executable snippet is added, so not touched.
- ## Frozen ledger format: step 6's LedgerAmendment block is unchanged, so not touched.
- ## Live consumers: no new export, so not touched.
- ## Declared text decoding: no subprocess or file-read code, so not touched.
- ## Post-merge: named by the spec. The added line goes before the 'No row' line, which tests/test_self_host.py:59 pins unchanged.
- ## Host detectors and call sites, Trust boundary, Fail loud, No shims, POSIX paths, FSM, Facade sinks, React boundaries: none applies to a prose-only skill change.
- ## Scoped refactor: the edits stay inside the housekeeping skill, its invariant test, the doctrine notes and the version files, with no unrelated module expanded.

## sweeper

### Claim verdicts

#### C12 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:244-245, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:123-126, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:235-236, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:372-377, config/architecture/ARCHITECTURE.md:323-326`
- reasoning: I read the whole skill and the host's ## Post-merge section and checked each concern by what it does. Closing rule: step 5 already reads 'non-Markdown tracking files declared under ## Post-merge' (SKILL.md:244-245), and the design names that existing declaration rather than adding a second one. Plan record: it replaces only the tick clause at :235-236, and the annotation and override-row duties at :236-239 stay. Verification: step 1's single record at :123-126 is replaced, not duplicated. Filing rule: it sits on the existing tracking-target bullet (ARCHITECTURE.md:326), which already carries filing-shaped text. Post-deploy actions: nothing in the skill acts on step 1's result today. Pre-flight: step 0 (:62-68) guards only the shared checkout's ownership, and step 1 (:105-107) guards content landing. The design routes both concerns back to those steps through the 'restates <owner>, not run' rule, so no second declaration path is created. Report fields: step 8 reads them, and no existing declaration carries them. One inconsistency: the spec's §1 table names step 8 as the owner of the report concern, while decision 2 and §5 say no step owns report fields. This is wording, not a second declaration path, and is filed below as advisory.

#### C13 — SURVIVED
- evidence: `plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:83, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:62-68`
- reasoning: I searched the tracked tree, minus docs/reviews/, by behaviour and by name for pre-flight/preflight, filing rule, closing rule, report field, post-deploy and plan record. I also searched *.py for 'Post-merge' and read the other skills for tick/checkbox and post-merge-housekeeping mentions. The only same-vocabulary hit outside this spec is the responding skill's 'delta pre-flight' (responding-to-adversarial-review/SKILL.md:83). That is a gate-revision dispatch with no relation to merge-state checks, so it is ADJACENT. Inside the housekeeping skill, the nearest shapes are step 0's STOP gate (:62-68) and step 1's content check, and the design consumes both instead of duplicating them. No hook or package module reads ## Post-merge: the *.py grep for 'Post-merge' hits only tests/test_self_host.py:58 and plugins/arch-compliance/tests/test_adr_skill_invariants.py:117-118.

#### C14 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:3, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:233, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:387, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:402, plugins/arch-compliance/tests/test_adr_skill_invariants.py:117-118, tests/test_self_host.py:58-59`
- reasoning: I re-ran recipe B myself (case-insensitive tick|checkbox over the skill) and got lines 3, 233, 235, 387 and 402, with the sentence at 235 running onto 236 ('step `[x]`'). I also searched by behaviour for '[x]' and for plan-status wording; that added only 236, which is already covered. I checked each line range in the §6 table against the 414-line file: 16-24 overview, 25-26 blank line plus the Checklist heading, 123-126 step 1 record, 139-140 cherry-pick sentence, 153-155 end of step 2 plus the 2.5 heading, 243-253 step 5, 262-266 step 6, 349-351 step 6.5 filing, 365-367 end of 6.5 plus the 7 heading, 372-377 step 8. All match. Recipe C: a case-sensitive 'Post-merge' search over both test trees hits test_adr_skill_invariants.py:117-118 and tests/test_self_host.py:58, and :59 pins the 'No row' line. test_adr_skill_prose.py:14 contains only the lowercase skill directory name and pins nothing in the section.

### Unanchored findings

- **advisory**: The spec contradicts itself on who owns the report-fields concern. Its §1 table gives the end-of-run report to step 8 (SKILL.md:372-377). Decision 2 and §5 call report fields an unowned concern 'per the §1 table, last column'. The new bullet is in fact a refinement read by step 8, not a home for an unowned concern.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:372-377`
- **advisory**: §4.4 adds a doctrine line saying this repository declares no filing rule. Its tracking-target bullet already carries a filing constraint: file through gh issue create so a follow-up never edits a cleared spec. After the change, step 6 would report 'filing rule: not declared …, portable rule applied' while the host bullet states a rule in all but label.
  - evidence: `config/architecture/ARCHITECTURE.md:326`

### Looked for but did not find

- Another skill, hook or package module that runs host-declared checks before housekeeping mutates anything: searched pre-flight, preflight, 'Post-merge' in *.py, plugins/arch-compliance/hooks and the python package
- Another statement of the plan tick rule outside post-merge-housekeeping/SKILL.md in the plugin's skills: searched tick, checkbox and \[x\] across plugins/arch-compliance/skills
- Another mechanism gating an action on a post-merge verification result: searched post-deploy, 'verified live', 'gh run list' across the tree
- Another place that allocates tracking-item IDs or closes tracked items: searched 'filing rule', 'closing rule', 'next free', 'F-###' across the tracked tree, docs/reviews/ excluded
- Another declared report-field or report-form mechanism: searched 'report field', 'not declared in ## Post-merge' across skills and tests

### Relationships

- ADJACENT: `pre-flight checks bullet and step 2.2` — responsibility `decide to STOP before shared state is mutated` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:62-68`
  - resolution: None: the spec's 'pre-flight: restates <owner>, not run' rule routes checkout-ownership checks back to step 0.
  - non-merge: Step 0 decides who owns the shared checkout. Step 2.2 decides on facts about the merge itself (a competing housekeeping run, an unmerged twin), which step 0 never inspects. The design refuses any pre-flight check on step 0's concern.
- SUBSUMED: `a host 'merged into the default branch' pre-flight check` — responsibility `verify the merge landed on the default branch` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:105-107`
  - resolution: Consume step 1's content-presence check. The spec already refuses such a pre-flight check as a restatement of step 1.
- IDENTICAL: `post-merge verification record` — responsibility `record the outcome of post-merge CI/deploy verification` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:123-126`
  - resolution: Replace the existing 'post-merge CI check: not declared' record with the one new record, as the spec does, and pin the absence of the old one in the invariant test.
- SUBSUMED: `plan record refinement` — responsibility `mark a merged plan's completed steps` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:235-236`
  - resolution: Generalize step 4's clause so the portable tick becomes the built-in instance of a declared plan record. The spec does this, and the description, Rationalizations and Red Flags lines refer to step 4.
- SUBSUMED: `closing rule on the tracking documents bullet` — responsibility `close or update tracked items the merge fixed` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:244-253`
  - resolution: Extend step 5's existing tracking-files declaration, named, with a per-document closing rule. The status-cell update is the built-in instance.
- SUBSUMED: `filing rule on the tracking-target bullet` — responsibility `decide how deferred items are written into the tracking target` — existing `config/architecture/ARCHITECTURE.md:326`
  - resolution: Have the existing bullet's filing text become this host's declared filing rule rather than recording 'no filing rule' in §4.4.
- SUBSUMED: `report fields bullet` — responsibility `decide what the end-of-run report lists` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:372-377`
  - resolution: Treat report fields as a refinement read by step 8, not as an unowned concern, and align decision 2 and §5 with the §1 table.
- ADJACENT: `step 6.7 post-deploy actions` — responsibility `gate host actions on the verification outcome` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:117-126`
  - resolution: None: step 6.7 reads step 1's record, and a deferred run re-invokes step 1 rather than re-implementing it.
  - non-merge: Step 1 verifies and records. Step 6.7 only reads that record and acts. It verifies nothing itself, so no verification logic is duplicated.
- ADJACENT: `step 2.2 stop outcome` — responsibility `stop a skill run on a precondition before acting` — existing `plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:83`
  - resolution: None.
  - non-merge: The responding skill's delta pre-flight checks a spec revision before a gate re-run. It shares the word only and has no merge, checkout or tracking concern.

### Two-owner counts

- stop the housekeeping run on a precondition before mutation (step 0 checkout gate, step 1 empty default-branch gate, step 2.2 pre-flight stop): 3

### Document conflicts

- `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:129` (contradicts): If the branch executed a tracked implementation plan, tick completed steps `[x]`, annotate the merge (PR #, squash SHA, date)
- `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:118` (contradicts): If `gh` is absent and no CI check is declared under `## Post-merge`, record `post-merge CI check: not declared / gh absent, skipped` in Step 8.
- `config/architecture/ARCHITECTURE.md:326` (contradicts): **Durable tracking target:** GitHub Issues on `IanDBallard/arch-compliance-for-superpowers` (`gh issue create`), so filing a follow-up or guard escape never edits an already-cleared spec.

## hardening

### Claim verdicts

#### C15 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:123-126; docs/design/POST_MERGE_HOST_STEPS.md:57-59; docs/design/POST_MERGE_HOST_STEPS.md:126-128; docs/design/POST_MERGE_HOST_STEPS.md:212-220; cy:.claude/skills/post-merge-housekeeping/SKILL.md:117-129`
- reasoning: The spec gives written reasons for each rejected alternative. Local copies leave two live copies, which the strangler rule forbids (spec :57-59). There is no general slot, and each concern goes to its owning step (:61-64). No portable competing-run check, because recognising one is a host convention (:126-128). Every mechanism added refuses. Pre-flight either stops before any mutation or carries a fact. A restatement is recorded as 'not run'. Post-deploy actions run only on 'passed', which needs at least one declared verification. A failed action stops the ones after it. The motivating producer of the bad state is external: the Cayenne bug-report mark emails a tester (cy:...:117-121). Hardening that producer in this repo is not possible, so gating at the skill is the strongest rung available. Today's step 1 (SKILL.md:123-126) only reports. The new record replaces that report, so no repair is introduced. I filed two refusal-quality gaps separately as unanchored findings: the restatement refusal of a base-branch check, and the missing record of completed actions on a re-run. They do not falsify this claim.

#### C16 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:31-42; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:139-140; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:153-155; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:28-29`
- reasoning: Steps 1-2 are read-only (SKILL.md:28-29). The subagents used on multi-item runs return raw output, and the main session collects it (:31-42). Today collection is required only before 3.5. Collecting earlier, before a new 2.2, is a stricter ordering the prose can carry. Read-only step-5 discovery subagents may still be in flight at 2.2, which is harmless. Steps 0-2 contain one mutation: step 2's doc-only cherry-pick (:139-140). The spec reorders it to 'once step 2.2 has run'. Step 1's 'git fetch origin' (:80) updates only remote-tracking refs, not a branch, worktree, checkout or document. Step 2.5 is the first step that kills processes, and it begins at :155, so a stop at 2.2 precedes it. Carry facts are main-session state, and steps 4 and 5 run later in the same session after 3.5 (:213-253). The hook exists.

#### C17 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:117-126; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:338; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:367; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:38-42`
- reasoning: Step 1's existing record sentence is at :123-126 and can be replaced by the single 'post-merge verification' record. The only occurrence of 'post-merge CI check: not declared' is at :125, and grep shows no other consumer. Step 6.5 starts at :338 and step 7 at :367, so a 6.7 slot exists between them. Everything from 3.5 on is main-session with no subagents in flight (:38-42), so gating 6.7 on a main-session record works. Step 1's verification commands are read-only and need no checkout, so they can be re-run standalone, which makes a 'deferred 6.7 re-runs step 1 first' instruction buildable. Weaknesses are filed as unanchored findings: spec §4.2 states the re-run only as a message to the user, and nothing records which actions have run.

#### C18 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:235-239; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:243-253; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:262-266; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:349-351`
- reasoning: Step 4's tick clause is one clause of the sentence at :235-236. The merge annotation shares that sentence but is a separate conjunct. The stale-text fix (:236-238) and the override-row record (:238-239) are separate sentences, so the tick clause can be replaced alone. Step 5's declaration phrase sits at :244-245 and 'Update them, with dates.' at :253, which is a clean insertion point. Step 6's filing sentence is at :262-264, and its no-target STOP at :264-266 is a separate sentence. A filing rule refines how an item is written and leaves the STOP alone. Step 6.5's filing clause and its stop-and-ask are at :349-351. Each edit touches only the named clause.

#### C19 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_skill_invariants.py:113-124; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:125; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:387; plugins/arch-compliance/tests/test_adr_skill_prose.py:31-39; tests/test_self_host.py:57-59`
- reasoning: The required tuple at :113-124 is a plain substring loop, so new pins append cleanly. 'Tick them.' occurs only at SKILL.md:387 and 'post-merge CI check: not declared' only at :125. Both are replaced, so absence asserts hold. The existing pin 'not declared in ## Post-merge, skipped' survives in the new forms. No FORBIDDEN literal (prose :31-39) appears in the proposed new prose. test_self_host checks only that the '## Post-merge\n' heading and the 'No row' line exist (:57-59), so an inserted line breaks neither. The backslash test (invariants :73-76) and the python-body count are unaffected by the proposed text.

### Unanchored findings

- **important**: The design refuses a host's 'merged into the default branch' pre-flight check as a restatement of step 1. Step 1's content-presence check names no outcome on MISSING (only 'echo PRESENT || echo MISSING'), and its gh query does not read baseRefName. A stacked PR merged into a dead base (Cayenne #125) therefore loses the host's fail-loud check and gets no stop.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:93-96`
- **important**: Step 6.7 records only that later actions were 'not run'. It keeps no record of which actions already succeeded, so a later re-run after a mid-list failure or deferral restarts from the first action. That repeats side effects such as emailing testers, which is the risk the gate exists to prevent.
  - evidence: `docs/design/POST_MERGE_HOST_STEPS.md:212-220`
- **advisory**: Spec §4.2's step 6.7 text states the 're-run step 1's verification first' rule only as something to tell the user, not as an instruction the step itself carries. The skill also has no partial-run entry point. A full re-run after step 3's teardown hits step 2's 'git log "$head"..<branch>' against a deleted branch.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:131-132`
- **advisory**: 'gh run list never makes it passed on its own' is ambiguous for a host whose declared post-merge verification is itself a CI workflow read through gh, as this repository's bullet declares. The record's 'passed' condition may be misread.
  - evidence: `config/architecture/ARCHITECTURE.md:325`

### Looked for but did not find

- Any mutation in steps 0-2 other than step 2's doc-only cherry-pick that precedes step 2.2 (step 1's fetch updates only remote-tracking refs)
- Any other occurrence of 'Tick them.' or 'post-merge CI check: not declared' in plugins/, tests/ or config/ that the absence asserts would break
- Any Python or hook code reading '## Post-merge' that the prose-only design would bypass (git grep over plugins/arch-compliance/python and hooks finds none)
- A FORBIDDEN literal in the proposed new prose
- A repair-on-read or normalizer among the added mechanisms: every added mechanism either stops, records 'not run', or applies a reported built-in clause

### Mechanism traces

- **Host pre-flight checks (step 2.2) with stop/carry outcomes**
  - invalid state: a merged item for which another open housekeeping PR for the same merge exists, or whose cross-repository twin PR is unmerged
  - producer: `cy:.claude/skills/post-merge-housekeeping/SKILL.md:21-28`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: Whether housekeeping lands through a pull request at all, and how one is recognised, is a host convention, so the check is a host's pre-flight declaration (§8).
  - spec citation: `docs/design/POST_MERGE_HOST_STEPS.md:186-195`
- **pre-flight: restates <owner>, not run**
  - invalid state: a declared pre-flight check whose concern §4.1 assigns to another step (shared checkout, or landing on the default branch)
  - producer: `cy:.claude/skills/post-merge-housekeeping/SKILL.md:31-35`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: Decision 2 and §4.1 give each concern one declaration. A pre-flight check on another step's concern is refused as `pre-flight: restates <owner>, not run` and reported in step 8
  - spec citation: `docs/design/POST_MERGE_HOST_STEPS.md:96-98`
- **post-merge verification record gating post-deploy actions (step 6.7 runs only on passed)**
  - invalid state: a post-deploy action executed for a merge commit when no declared verification for that commit has succeeded
  - producer: `cy:.claude/skills/post-merge-housekeeping/SKILL.md:117-121`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: Decision 5: it runs only on `passed`, which needs at least one declared verification; `gh run list` alone never makes the record `passed`
  - spec citation: `docs/design/POST_MERGE_HOST_STEPS.md:99-106`
- **a failed post-deploy action stops the actions after it**
  - invalid state: post-deploy action k+1 executes after action k in declared order failed
  - producer: `docs/design/POST_MERGE_HOST_STEPS.md:218`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: Decision 5: a failed action stops the actions after it.
  - spec citation: `docs/design/POST_MERGE_HOST_STEPS.md:218-220`
- **deferred step 6.7 re-runs step 1's verification first**
  - invalid state: a later step 6.7 reading a post-merge verification record written before the deploy completed (value 'in progress' or 'failed')
  - producer: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:117-126`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/POST_MERGE_HOST_STEPS.md:104-106`
- **portable rule applied when plan record, closing rule or filing rule is absent**
  - invalid state: a host doctrine whose ## Post-merge section carries no plan record, closing rule or filing rule
  - producer: `config/architecture/ARCHITECTURE.md:319-328`
  - rung 2 (highest applicable 2); repairs=False
  - hardening rejected because: Three absent refinements have a built-in meaning, the skill's own portable clause ... §4.4 records the three meanings in the doctrine's `## Declared, never defaulted`.
  - spec citation: `docs/design/POST_MERGE_HOST_STEPS.md:79-86`
- **test asserts 'Tick them.' and 'post-merge CI check: not declared' are absent**
  - invalid state: post-merge-housekeeping/SKILL.md body contains 'Tick them.' or 'post-merge CI check: not declared'
  - producer: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:387`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/POST_MERGE_HOST_STEPS.md:246-248`

## Claims

- **C1** [premise] [load-bearing]: The portable skill reads four named host conventions (branch lock, worktree daemon probe, post-merge CI workflows, durable tracking target) plus step 5's non-Markdown tracking files (a fifth declaration the overview does not name) from ## Post-merge; a host cannot declare checks on the merge itself, a plan-record rule, a filing or closing rule, an action gated on the post-merge verification, or extra report fields.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:20-24`
- **C2** [premise] [load-bearing]: For each motivating rule in section 1's table, the 'portable step that owns the concern today' column is correct: no step owns checks on the merge itself (competing run, twin PR); step 4's first sentence ticks completed steps; step 5 owns reconciling tracking docs; step 6 owns filing into the tracking target; step 1 verifies post-merge CI/deploy and no step acts on its result; step 8 owns the report.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:117-126`
- **C3** [premise] [load-bearing]: Step 1 runs the post-merge CI check and any declared verification and records only one string, 'post-merge CI check: not declared in ## Post-merge, skipped', when gh is absent and nothing is declared; it records no pass/fail result.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:117-126`
- **C4** [premise]: Cayenne's local skill holds the open-PR race check (#60/#61), the twin check, the do-not-tick plan-record rule, F-### closure against the diff, next-free F-### allocation across main and open PRs, deploy-gated bug-report marking that emails testers, and a report with Gate:/Fixes: lines, at the cited lines (cy: maps to a snapshot at fffc2954).
  - spec citation: `cy:.claude/skills/post-merge-housekeeping/SKILL.md:21-28`
- **C5** [premise] [load-bearing]: No package or hook code parses ## Post-merge (recipe A empty); ARCH_REL's consumers are host.py:30 (existence) and inject_constraints.py:165-168 (whole-text injection).
  - spec citation: `plugins/arch-compliance/python/acf/repo.py:24`
- **C6** [premise]: Deferral: Cayenne's and HistoricMansions' cutovers are adoption work after this release; nothing in this design depends on them.
  - spec citation: `cy:.claude/skills/post-merge-housekeeping/SKILL.md`
- **C7** [premise]: The approved spec POST_MERGE_HOUSEKEEPING_SKILL.md lists four conventions and the single not-declared report form in decision 1 (:36-41), enumerates its checklist from :104 to step 8 at :138, and says tick completed steps at :129; this spec supersedes those parts without editing that spec.
  - spec citation: `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:36-41`
- **C8** [mandate] [load-bearing]: Absent declarations are reported as 'not declared ... skipped' and never defaulted; the three built-in meanings (absent plan record, filing rule, closing rule -> the skill's own portable clause, reported as 'portable rule applied') are recorded in ## Declared, never defaulted, complying with that section.
  - spec citation: `config/architecture/ARCHITECTURE.md:189-216`
- **C9** [mandate]: The new skill prose names no host repository, path or section (## Prose names no host); test_adr_skill_prose.py needs no change, and its FORBIDDEN list covers origin-host vocabulary only.
  - spec citation: `config/architecture/ARCHITECTURE.md:218-228`
- **C10** [mandate]: The skill-prose change ships with a version bump to 0.3.3 in plugin.json and pyproject.toml and an installed-skills byte check, per ## Release discipline; the installed-skills check stays under ## Release discipline rather than becoming a pre-flight check.
  - spec citation: `config/architecture/ARCHITECTURE.md:269-279`
- **C11** [mandate]: Each rule stated once in the step that applies it, the ## Host declarations section holding only the ownership table, the overview's report-form sentence replaced rather than appended to, and the tick rule referred to as 'the plan record (step 4)' elsewhere, satisfy ## Single point of definition.
  - spec citation: `config/architecture/ARCHITECTURE.md:281-298`
- **C12** [shape_fit] [load-bearing]: Each host rule is a refinement on the ## Post-merge bullet of the portable step that owns its concern (closing rule on the tracking-documents bullet, which is step 5's existing tracking-files declaration named; filing rule on the tracking-target bullet for steps 6/6.5; post-deploy actions on the post-merge CI bullet read at 6.7; plan record replacing only step 4's tick clause); step 1 writes one verification record that replaces its existing one; and new bullets are added only for concerns no step owns (pre-flight merge checks, report fields). So the 4.1 table gives every concern exactly one declaration and one record, and the design creates no second way to declare any concern, including landing on the default branch (step 1), the shared checkout (step 0) and the report forms.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:20-24`
- **C13** [shape_fit] [load-bearing]: No other skill, hook or package module already gives a host a pre-flight, plan-record, filing/closing-rule, post-deploy-action or report-field mechanism that these declarations would partially duplicate.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md`
- **C14** [sweep]: The section 6 table lists the skill lines the design edits (3, 16-24, 123-126, 139-140, 233, 235-236, 243-253, 262-266, 349-351, 372-377, 387, 402) and the insertion points (25-26, 153-155, 365-367) correctly; recipe B's output (3, 233, 235, 387, 402, with 236 continuing 235) is every statement of the tick rule in the skill; recipe C over both test trees finds every test pin on ## Post-merge.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:233-239`
- **C15** [mechanism_justification] [load-bearing]: Refining the owning steps' declarations is justified over hosts keeping local copies, a general host-steps slot, or a portable competing-run check; and the mechanisms refuse (stop, not run, restates) rather than repair, with post-deploy actions never run unless a declared verification passed.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:233-239`
- **C16** [implementability] [load-bearing]: Pre-flight can run as step 2.2 in the main session after every step 1-2 result (including subagent results) is collected, before step 2.5 and before step 2's doc-only cherry-pick (reordered to 'once step 2.2 has run'), once per run, with a stop ending the run for every item before any process, branch, worktree, checkout or document is changed; carry facts can be read by steps 4 and 5.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:28-42`
- **C17** [implementability] [load-bearing]: Step 1 can write one record 'post-merge verification: passed|failed|in progress|not declared in ## Post-merge, skipped' (passed only with at least one declared verification; gh run list never sufficient alone) replacing its existing record, and post-deploy actions can run as step 6.7 between 6.5 and 7 in the main session gated on it, with a failed action stopping later ones and a deferred 6.7 re-running step 1's verification first.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:38-42`
- **C18** [implementability] [load-bearing]: Step 4 can replace only its tick clause with the plan record while keeping the merge annotation, stale-text fix and override-row record unconditional; step 5 can read the tracking-documents bullet and apply a closing rule; steps 6 and 6.5 a filing rule; each without changing those steps' other filing, reconciliation or STOP behaviour.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:262-266`
- **C19** [implementability]: test_housekeeping_skill_invariants can pin the new strings and assert 'Tick them.' and 'post-merge CI check: not declared' are absent while its existing 'not declared in ## Post-merge, skipped' pin still holds; the prose test and tests/test_self_host.py need no change.
  - spec citation: `plugins/arch-compliance/tests/test_adr_skill_invariants.py:105-133`
