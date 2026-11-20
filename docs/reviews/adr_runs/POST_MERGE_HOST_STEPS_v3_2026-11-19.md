# Adversarial design review — full detail

Spec: `docs/design/POST_MERGE_HOST_STEPS.md` @ `290a051791c16e7e3ea78cfaade4eb7e571888bd`
Kinds: feature
Outcome: **BLOCKED**
Claims: 19 · Reviewers: 4 · Converged: 1

## Blocking reasons

- load-bearing claim C12 (shape_fit) is REFUTED: I checked the 4.1 table row by row against the skill. Three concerns end up with more than one declaration or record after this design lands. (1) Reconciliation: step 5 already reads its own declaration, 'non-Markdown tracking files declared under ## Post-merge' (SKILL.md:244-245). That declaration is not one of the four the overview names (SKILL.md:20-22). The spec's 4.1 row itself says 'tracking-target bullet, refined with a closing rule, plus step 5's tracking files'. The new closing rule is then applied 'to the documents it names' (spec 4.2, step 5). So which documents step 5 reconciles can be named on two bullets, and the claim's 'exactly one declaration' fails on the table's own text. (2) Step 1's verification result: SKILL.md:124-126 already records `post-merge CI check: not declared in ## Post-merge, skipped`, with the predicate 'gh absent and no check declared'. Spec 4.2 adds a second step-1 record, `post-merge verification: passed|failed|in progress|not declared ... skipped`, with a different predicate. (3) Step 4's body (SKILL.md:235-239) is one paragraph. Besides ticking, it adds the merge annotation, excises stale code blocks and records override rows. Spec 4.2 puts the whole 'existing tick rule' behind 'Otherwise:', and §6 labels 233-239 as 'the tick rule'. A declared plan record therefore drops those other duties too (a boundary cut, not a refinement). Steps 0 and 1 hold as single owners: no new bullet re-declares the branch lock (SKILL.md:62-64), and step 1's content check (SKILL.md:96-97) stays unrefined.

## Absorptions

- BOUNDARY_CUT: 'plan record bullet (step 4 refinement)' shares responsibility "record a merged plan's status, merge annotation and stale-text excision" with plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:235-239 — Scope the plan record to the status-marking sentence only. Keep the merge annotation, stale-block excision and override-row recording in step 4 unconditionally, so the host refinement replaces only 'tick every completed step [x]'.
- PARTIAL_OVERLAP: 'closing rule on the tracking-target bullet' shares responsibility 'name the documents step 5 reconciles' with plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:244-245 — Make one step-5 declaration (tracking documents) that carries both the list of non-Markdown tracking files and the closing rule applied to them. The closing rule's 'documents it names' and the existing tracking-files declaration both collapse into it, and the 4.1 row names it alone.
- PARTIAL_OVERLAP: "step 1 'post-merge verification:' record" shares responsibility 'record the post-merge CI and deploy verification outcome' with plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:123-126 — Use one step-1 verification record whose values (passed, failed, in progress, not declared/gh absent) replace the existing 'post-merge CI check: not declared' record. Step 8 and step 6.7 both read that single record.
- SUBSUMED: 'filing rule on the tracking-target bullet' shares responsibility 'file deferred items and guard escapes into the tracking target' with plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:262-266 — Already resolved as designed: the filing rule is a refinement written on the existing tracking-target declaration and read by the steps that already file (6, 6.5).

## Converged findings

- [3 reviewers: refuter, sweeper, hardening] Step 1's post-merge verification record does not decide what step 6.7 gates on: 'passed' is vacuously true with no declared verification, the 'not declared' value only arises when gh is absent, and the new record sits beside the existing 'post-merge CI check: not declared' record with a different predicate, so 6.7's 'no post-merge verification declared, not run' branch is unreachable on gh hosts and side-effecting actions can run on green CI alone.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:123-126`
  - evidence: `docs/design/POST_MERGE_HOST_STEPS.md:160-163`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:20-24, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:244-245, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:235-236, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:123-126, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:262-266, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:372-377`
- reasoning: I read all 414 lines of the skill at 290a051. The overview names exactly four conventions (:20-24), and step 5 adds non-Markdown tracking files (:244-245). Every other place the skill reads ## Post-merge is one of those four: the branch lock (:62-64), the daemon probe (:180-184), post-merge CI or deploy verification (:123-126), and the tracking target (:262-266, :350-351). Nothing reads a pre-flight check. Step 4 ticks unconditionally (:235-236), so a host cannot declare a plan record. Step 6 writes into the target and follows no host rule. No step acts on the result of step 1. Step 8 has no host-field slot (:372-377).

#### C2 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:117-126, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:233-239, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:241-253, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:255-266, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:372-377`
- reasoning: I checked each row against the live skill. No step checks for a competing housekeeping run or a twin PR: steps 0-2 cover the checkout, content presence, CI and stranded commits. Step 4 owns the plan record and says to tick every completed step (:235-236). Step 5 owns tracking-doc reconciliation (:241-253). Step 6 owns filing into the tracking target (:262-266). Step 1 verifies CI and deploy (:117-126), and grepping for 'deploy' finds no later step that acts on the result. Step 8 owns the report (:372-377). Each line range the spec cites matches.

#### C3 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:117-126, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:372-377`
- reasoning: Step 1 says to 'Verify the post-merge workflow', run gh run list and run any declared verification. Its only recorded string is the skip, and only when gh is absent and nothing is declared (:124-126). Step 8 (:372-377) lists the 'nothing stranded' result, the sweep branch that ran, and the not-declared skips. It defines no CI pass/fail record.

#### C4 — SURVIVED
- evidence: `C:/Users/iball/AppData/Local/Temp/claude/87e26b93c6dabf01/7ee83bd0-9038-461f-98de-0102609a84f5/scratchpad/cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:21-28, .../cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:38-40, .../cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:65-66, .../cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:76-83, .../cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:181-201, .../cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:117-129, .../cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:214-223`
- reasoning: I read the Cayenne snapshot. Each cited range carries what the spec says: the race check for open PRs, with #60/#61 (:21-28); the cross-repo twin (:38-40); 'Do not tick the checkboxes' (:65-66); F-### closure against the diff (:76-83); next free F-### taken from main and every open PR (:181-201); bug-report marking gated on a live deploy, which emails the tester (:117-129); and the report with Gate: and Fixes: lines (:214-223). The spec's quotes match the text.

#### C5 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:24, plugins/arch-compliance/python/acf/adr/host.py:30, plugins/arch-compliance/hooks/inject_constraints.py:165-168`
- reasoning: I ran `git grep -n "Post-merge" -- plugins/arch-compliance/python plugins/arch-compliance/hooks`, which returned nothing. A case-insensitive post.merge grep found only comments in ledger.py and the skill list in scripts/check_installed_skills.py; neither parses the section. A git grep for ARCH_REL in python/ and hooks/ finds only repo.py:24 (definition), host.py:30 (require_file, existence only) and inject_constraints.py:165-168 (reads the whole text and truncates it, parsing no section).

#### C6 — SURVIVED
- evidence: `docs/design/POST_MERGE_HOST_STEPS.md:29-31, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:20-24`
- reasoning: `git grep -i cayenne -- plugins scripts config` returns nothing, so no plugin code, test or doctrine reads Cayenne. The §4 deliverables are the plugin SKILL.md, its invariant test, ARCHITECTURE.md and the version files, all in this repo. §0 states no step reads or writes cy: paths. Done items 1-5 are all in-repo; item 6 only names the cutovers in the PR body.

#### C7 — SURVIVED
- evidence: `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:36-41, docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:104, docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:129, docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:138, docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:3`
- reasoning: I opened the approved spec. Lines 36-40 list the four conventions, and :41 is the no-silent-skip rule. :104 contains 'Its checklist steps are:'. :129 says 'tick completed steps `[x]`'. :138 is the Step 7 and Step 8 bullet. :3 shows status v2, approved. `git diff e9dd881 HEAD --stat` shows the file unchanged on this branch: only the new spec, review runs and ledger lines were added.

### Unanchored findings

- **important**: Decision 5 says post-deploy actions depend on one recorded result (passed/failed/in progress/not declared). But step 6.7 also branches on 'no declared verification', and that value cannot be read from the record. Step 1's 'not declared' record only fires when gh is absent and nothing is declared. With gh present, no host verification declared and post-deploy actions declared, step 1 would record `passed` from gh run list alone. Step 6.7 would then run the actions, though decision 5 and the §8 risk row say actions with no declared verification never run.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:124-126`

### Looked for but did not find

- any code under plugins/arch-compliance/python or plugins/arch-compliance/hooks that parses or matches '## Post-merge' or 'Post-merge'
- a consumer of ARCH_REL beyond repo.py:24, host.py:30 and inject_constraints.py:165
- a step in post-merge-housekeeping/SKILL.md after step 1 that acts on the CI or deploy verification result
- a step in the current skill that checks for a competing housekeeping PR or a cross-repo twin PR
- any reference to Cayenne in plugins/, scripts/ or config/ that would make this design depend on the Cayenne cutover
- tick/checkbox lines in SKILL.md beyond 3, 233, 235, 387 and 402 (recipe B output confirmed)
- test pins for 'Post-merge' beyond test_adr_skill_invariants.py:117-118 (recipe C output confirmed)

## compliance

### Claim verdicts

#### C8 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:196-204; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:23-24; docs/design/POST_MERGE_HOST_STEPS.md:176-184`
- reasoning: The section reads 'no default stands in for a missing declaration' (:191-193). It also already allows a built-in meaning for an absent value, provided the meaning is recorded in the section: 'The review gives some absent or empty values a built-in meaning, recorded here' (:196-204). The design does exactly that. §4.4 adds a sentence recording the three meanings: plan record, closing rule and filing rule all fall back to the portable rule. Each fallback is also reported in step 8 as 'portable rule applied' (spec :176-184, :198-201). That extends the skill's existing report-not-silently-skip rule (SKILL.md:23-24). The other absent declarations add nothing and are reported as 'skipped': pre-flight checks, post-deploy actions and report fields (spec :166-167, :186-187, :200-201). So no default re-enters for a declared value. The spec's step 4 and step 5 text applies a declared rule first and uses the portable rule only when none is declared.

#### C9 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_skill_prose.py:31-39; plugins/arch-compliance/tests/test_adr_skill_prose.py:73-79; config/architecture/ARCHITECTURE.md:226-227`
- reasoning: The mandate reads 'Skill prose and runtime messages name no host repository, path or section'. The row's test scans HOUSEKEEPING/SKILL.md (test_adr_skill_prose.py:14,21) against a FORBIDDEN list. That list is origin-host vocabulary only (:31-39, and the doctrine itself says so at :226-227), so the claim's 'only' holds. The new prose quoted in spec §4.2 names no host repository or path. Its one example, 'how an item's ID is allocated', is generic. It names the `## Post-merge` section, but that is the plugin's own declaration contract: the existing skill names it already (SKILL.md:22-24) and the invariant test requires it (test_adr_skill_invariants.py:117-118). The test runs on whatever text is in the skill and needs no edit.

#### C10 — SURVIVED
- evidence: `plugins/arch-compliance/.claude-plugin/plugin.json:3; pyproject.toml:3; config/architecture/ARCHITECTURE.md:271-276`
- reasoning: The mandate reads 'A change to a skill's prose bumps the plugin version in plugin.json and pyproject.toml' (:271-272). It also says the installed copy of post-merge-housekeeping is byte-checked before a gate or housekeeping run (:272-276). Both version files are 0.3.2 today (plugin.json:3, pyproject.toml:3), and §4.4 bumps both to 0.3.3. DoD item 5 adds the post-merge reinstall and the check_installed_skills.py comparison. The design keeps the check under Release discipline and does not turn it into a pre-flight check. That matches the doctrine, which scopes the check to gate runs as well as housekeeping runs.

#### C11 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:233-236; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:3; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:387; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:402; docs/design/POST_MERGE_HOST_STEPS.md:174-177`
- reasoning: The lifted rule requires 'exactly one canonical implementation that every call site consumes' (ARCHITECTURE.md:283-285). Today the tick rule is stated at SKILL.md:233-236 and restated at :3 ('unticked checkboxes'), :387 ('Tick them.') and :402 ('unticked boxes'). Spec recipe B matches those lines, which I verified. The design keeps the rule in step 4 (spec :174-177) and makes the other three refer to 'the plan record (step 4)' (spec :153-154, :202-206). It also pins the absence of 'Tick them.' in the test (§4.3). The new `## Host declarations` table names an owner and a step for each concern and restates no rule. Step 2.2's restatement refusal reads that table and does not redefine ownership. The design meets the rule as it applies to prose.

### Unanchored findings


### Looked for but did not find

- ## High-frequency misses, completeness claims: the spec makes four quantified claims, and each has a re-runnable recipe or a doctrine line behind it. Recipe A backs 'no Python parses ## Post-merge'. Recipe B backs the tick lines; I verified 3, 233, 235, 387 and 402 against SKILL.md. Recipe C backs the test pins at test_adr_skill_invariants.py:117-118. 'Origin-host vocabulary only' is backed by ARCHITECTURE.md:226-227. Cleared.
- ## High-frequency misses, a default re-entering for a declared value: steps 4, 5, 6 and 6.5 apply the declared rule first and use the portable rule only when none is declared. Cleared.
- ## High-frequency misses, a host name in prose: the new prose examples are generic, and the FORBIDDEN scan still runs on the edited SKILL.md. Cleared.
- ## High-frequency misses, stdlib exception mixin and subprocess encoding: the design has no Python change (spec §3). Not touched.
- ## High-frequency misses, a check re-implemented in a skill instead of consumed from the package: the new steps run no registry, anchor or path check. Not touched.
- ## One owner for host paths: the design adds no executable skill snippet and no path join. The existing step-6 python block is unchanged. Not touched.
- ## Frozen ledger format: step 6's LedgerAmendment block and its fields are unchanged. Only the filing-rule sentence is added. Not touched.
- ## Live consumers: the design adds no export. Not touched.
- ## Declared text decoding / ## Fail loud / ## No shims / ## POSIX paths / ## One base exception: no runtime code changes. Not touched.
- ## Host detectors and call sites / ## Façade sinks / ## FSM transitions / ## Fail-loud ratchet: no mandates.yml row or detector changes. Not touched.
- ## Scoped refactor: the edits stay inside the housekeeping skill, its invariant test, the doctrine notes and the version files. No unrelated module is in scope. Cleared.
- ## Post-merge: the spec already names this section, and §4.4 adds a 'declares none' line in the same bold-bullet shape (ARCHITECTURE.md:321-328). Cleared.
- unstated_mandates is empty: every doctrine section the design touches is named in the spec's Governing mandates header (spec :17-20).

## sweeper

### Claim verdicts

#### C12 — REFUTED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:244-245`
- reasoning: I checked the 4.1 table row by row against the skill. Three concerns end up with more than one declaration or record after this design lands. (1) Reconciliation: step 5 already reads its own declaration, 'non-Markdown tracking files declared under ## Post-merge' (SKILL.md:244-245). That declaration is not one of the four the overview names (SKILL.md:20-22). The spec's 4.1 row itself says 'tracking-target bullet, refined with a closing rule, plus step 5's tracking files'. The new closing rule is then applied 'to the documents it names' (spec 4.2, step 5). So which documents step 5 reconciles can be named on two bullets, and the claim's 'exactly one declaration' fails on the table's own text. (2) Step 1's verification result: SKILL.md:124-126 already records `post-merge CI check: not declared in ## Post-merge, skipped`, with the predicate 'gh absent and no check declared'. Spec 4.2 adds a second step-1 record, `post-merge verification: passed|failed|in progress|not declared ... skipped`, with a different predicate. (3) Step 4's body (SKILL.md:235-239) is one paragraph. Besides ticking, it adds the merge annotation, excises stale code blocks and records override rows. Spec 4.2 puts the whole 'existing tick rule' behind 'Otherwise:', and §6 labels 233-239 as 'the tick rule'. A declared plan record therefore drops those other duties too (a boundary cut, not a refinement). Steps 0 and 1 hold as single owners: no new bullet re-declares the branch lock (SKILL.md:62-64), and step 1's content check (SKILL.md:96-97) stays unrefined.

#### C13 — SURVIVED
- evidence: `plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:83`
- reasoning: I searched by behaviour across the tree, excluding docs/reviews/. The case-insensitive terms were pre-?flight, plan record, report field, post-deploy, closing rule and filing rule. I also searched 'Post-merge' to find every reader of the section. Outside the spec, the only pre-flight hit is the responding skill's 'delta pre-flight' (responding-to-adversarial-review/SKILL.md:83). That is a revision-classification dispatch for the gate, not a merge check, so it does not overlap. Only post-merge-housekeeping/SKILL.md reads ## Post-merge. Among tests, tests/test_self_host.py:58-59 pins the section, but it only asserts that the heading and its 'No row' line exist. acf-setup, acf-mandate and architecture-review carry no ## Post-merge template. No hook or package module parses the section.

#### C14 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:236`
- reasoning: I read the full 414-line skill and resolved every listed span. Line 3 is the description. 16-24 is the platform and host declarations paragraph. 25-26 is the blank line before the Checklist heading. 117-126 is the post-merge CI check. 153-155 covers the end of step 2 and the 2.5 heading. 233-239 is step 4. 243-253 is the step 5 body. 262-266 is step 6's filing sentence. 349-351 is step 6.5's filing. 365-367 covers the end of 6.5 and the step 7 heading. 372-377 is step 8. 387 is the Rationalizations row and 402 the Red Flags bullet. I re-ran recipe B (tick|checkbox, case-insensitive) across every skill: lines 3, 233, 235, 387 and 402 of this skill only. A behaviour search for `[x]`, 'plan truth' and 'unchecked' under plugins/ found only 233 and 236 in this skill (236 continues 235), so the tick rule has no statement that the name grep missed.

### Unanchored findings

- **important**: A declared plan record replaces all of step 4's single paragraph, not just its tick sentence. That removes the merge annotation, stale-code-block excision and override-row recording for any host that declares one, which is a boundary cut on step 4 rather than a refinement of how status is recorded.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:235-239`
- **important**: Two declarations can name the documents step 5 reconciles: the existing tracking-files declaration (SKILL.md:244-245) and the new closing rule's 'documents it names' on the tracking-target bullet. That leaves two owners for one input, and the overview's list of four conventions omits the first.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:244-245`
- **important**: Step 1 would emit two records for the post-merge verification outcome with different 'not declared' predicates: the existing one at :124-126 and the new `post-merge verification:` record that step 6.7 reads. The spec does not merge them, so the gating input to 6.7 has two sources in one step.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:123-126`
- **advisory**: The overview still states one absent-declaration report form, '<check>: not declared in ## Post-merge, skipped'. The design adds 'portable rule applied' and 'restates <owner>, not run' forms, but its overview edit only appends a sentence, so the old single-form rule survives beside the new ones.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:23-24`
- **advisory**: Recipe C searched only plugins/arch-compliance/tests and missed tests/test_self_host.py:58-59, which pins the doctrine's ## Post-merge heading and its 'No row: host operational declarations; no test enforces this.' line. The §4.4 'declares none' line must leave both intact.
  - evidence: `tests/test_self_host.py:58-59`

### Looked for but did not find

- another reader or parser of ## Post-merge in skills, hooks, package or tests: 'Post-merge' over the tree excluding docs/reviews/
- an existing pre-flight, plan-record, closing-rule, filing-rule, post-deploy or report-field mechanism: case-insensitive 'pre-?flight|plan record|report field|post-deploy|closing rule|filing rule'
- other statements of the plan tick rule: case-insensitive 'tick|checkbox' over plugins/arch-compliance/skills, plus '\[x\]|plan truth|unchecked' over plugins/
- a ## Post-merge scaffold in acf-setup or another skill that would become a second list of declarations: 'Post-merge' in plugins/arch-compliance/skills
- user-facing skill descriptions restating the tick rule: 'housekeeping' in README.md (only the :35 table row, no tick wording)

### Relationships

- BOUNDARY_CUT: `plan record bullet (step 4 refinement)` — responsibility `record a merged plan's status, merge annotation and stale-text excision` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:235-239`
  - resolution: Scope the plan record to the status-marking sentence only. Keep the merge annotation, stale-block excision and override-row recording in step 4 unconditionally, so the host refinement replaces only 'tick every completed step [x]'.
- PARTIAL_OVERLAP: `closing rule on the tracking-target bullet` — responsibility `name the documents step 5 reconciles` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:244-245`
  - resolution: Make one step-5 declaration (tracking documents) that carries both the list of non-Markdown tracking files and the closing rule applied to them. The closing rule's 'documents it names' and the existing tracking-files declaration both collapse into it, and the 4.1 row names it alone.
- PARTIAL_OVERLAP: `step 1 'post-merge verification:' record` — responsibility `record the post-merge CI and deploy verification outcome` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:123-126`
  - resolution: Use one step-1 verification record whose values (passed, failed, in progress, not declared/gh absent) replace the existing 'post-merge CI check: not declared' record. Step 8 and step 6.7 both read that single record.
- ADJACENT: `step 2.2 host pre-flight checks (stop outcome)` — responsibility `halt the run before mutation when another party owns the work` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:62-68`
  - resolution: none; the restates rule refuses pre-flight checks on the branch-lock concern
  - non-merge: Step 0 guards the shared checkout's HEAD and lock on this machine. A competing housekeeping run or an unmerged twin pull request is a forge-level fact that holds across clones and sessions, so step 0's checks cannot see it, and the spec routes any checkout-level pre-flight back to step 0 as a restatement.
- ADJACENT: `step 6.7 post-deploy actions` — responsibility `act on a verified deploy` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:123-124`
  - resolution: none beyond the single verification record above
  - non-merge: Step 1 verifies and never acts. Step 6.7 acts and never verifies, and it consumes step 1's recorded result rather than re-running any verification.
- ADJACENT: `report fields bullet` — responsibility `add lines to the end-of-run report` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:374-377`
  - resolution: none
  - non-merge: Step 8 fixes the portable report content. The bullet only appends host-declared fields to that one step and adds no second report.
- SUBSUMED: `filing rule on the tracking-target bullet` — responsibility `file deferred items and guard escapes into the tracking target` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:262-266`
  - resolution: Already resolved as designed: the filing rule is a refinement written on the existing tracking-target declaration and read by the steps that already file (6, 6.5).

### Two-owner counts

- name the documents step 5 reconciles (tracking-files declaration + closing rule's named documents): 2
- record step 1's post-merge verification outcome (existing CI-check record + new verification record): 2
- absent-declaration report format (overview single form + new 'portable rule applied' / 'restates <owner>, not run' forms): 2

### Document conflicts

- `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:41` (restates): If the host doctrine has no `## Post-merge` section or does not declare one of (1)–(3), the Step 8 summary must explicitly report `<check>: not declared in ## Post-merge, skipped` rather than omitting it silently.
- `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:129` (contradicts): If the branch executed a tracked implementation plan, tick completed steps `[x]`, annotate the merge (PR #, squash SHA, date), and remove or update any plan code blocks that review rounds superseded.
- `config/architecture/ARCHITECTURE.md:191` (restates): The adversarial-design-review gate's host values are declared by the host in `config/architecture/adr.yml`; no default stands in for a missing declaration, and a missing declaration fails loud.

## hardening

### Claim verdicts

#### C15 — SURVIVED
- evidence: `docs/design/POST_MERGE_HOST_STEPS.md:55-57, docs/design/POST_MERGE_HOST_STEPS.md:117-119, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:264-266, config/architecture/ARCHITECTURE.md:196-203`
- reasoning: I checked each rejected alternative against a written reason in the spec. Local copies are rejected because they leave two live copies, which the strangler rule forbids (:55-57). A general slot is rejected by decision 2's one-owner-per-concern rule (:59-62, :71-75). A portable competing-run check is rejected because recognising a competing run is a host convention (:117-119, risk row :349). The mechanisms the design adds all refuse: a stop ends the run (:85-86), restatements are 'not run' (:91-93), and post-deploy actions are 'not run' unless step 1 recorded passed (:188-194). Each refusal is reported, and that matches the existing STOP precedent at SKILL.md:264-266. The three portable-rule meanings for absent declarations are fallbacks, not refusals. They are reported, never silent ('portable rule applied'), and are to be recorded in doctrine the same way review.yml's built-in meanings already are (ARCHITECTURE.md:196-203). This claim survives, but see the unanchored finding on how weak the 'passed' predicate is.

#### C16 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:28-29, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:155, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:188`
- reasoning: Steps 1-2 are declared read-only (SKILL.md:28-29), and step 2.5 starts at :155. Its first mutation is the zombie Stop-Process/kill (:188), which comes before teardown at step 3 (:195-204). The point between 2 and 2.5 (:153-155) therefore follows every read and precedes every mutation the checklist names. Subagent results are already collected in the main session (:36-38). Moving the collection point for step 1-2 results earlier, to before 2.2, needs no new hook. A stop that ends the run for every item at that point comes before any mutation. Two caveats: `git fetch origin` (:80) writes remote-tracking refs, and step 2's 'Cherry-pick doc-only strays' (:139-140) is phrased inside a read-only step. See the advisory finding.

#### C17 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:117-126, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:38-42, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:365-367`
- reasoning: Step 1 already runs the post-merge CI check and the declared verification (:117-126). One added sentence there can record a result in the session. The 6.5/7 boundary (:365-367) is a real insertion point. Lines :38-42 state that everything from 3.5 on is main-session and sequential with no subagents in flight, so 6.7 inherits that. The hook exists. The predicate the gate keys on is unsound and the 'run step 6.7 once it passes' re-entry has no hook. Both are filed as unanchored findings.

#### C18 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:251-253, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:262-266, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:349-351`
- reasoning: Step 5 ends with 'Update them, with dates.' (:253), which is a clean append point for a closing-rule sentence. Step 6's write into the declared tracking target and its no-target STOP (:262-266) are untouched by a phrase qualifying how the item is written. A filing rule only exists when a tracking-target bullet exists, so the STOP branch is unaffected. Step 6.5's filing sentence and its stop-and-ask (:349-351) can take the same qualifier. None of the three sentences changes reconciliation scope or STOP behaviour.

#### C19 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_skill_invariants.py:113-125, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:387`
- reasoning: The required tuple is a plain substring loop (:113-125), so adding strings works. 'Tick them.' occurs today only at SKILL.md:387, the Rationalizations row that §4.2 rewrites, so an absence assertion is satisfiable after the edit. `git grep -n "Post-merge" -- plugins/arch-compliance/tests` returns only test_adr_skill_invariants.py:117-118, which matches recipe C. test_adr_skill_prose.py lists HOUSEKEEPING/SKILL.md in FILES (:21) and checks FORBIDDEN vocabulary only, so generic new prose needs no change there.

### Unanchored findings

- **important**: Step 1's 'post-merge verification: passed' is defined as 'the run for the merge commit and every declared verification succeeded'. That makes it true for a green CI run with no deploy verification declared, because the condition is vacuous when nothing is declared. A side-effecting post-deploy action (the motivating case emails testers) then runs on green CI alone. This defeats decision 5's 'Declared actions with no declared verification are never run' and the §8 risk mitigation. The motivating host rule says verified live 'not just a green run'.
  - evidence: `docs/design/POST_MERGE_HOST_STEPS.md:160-163`
- **important**: The spec never says when step 1 records `not declared in ## Post-merge, skipped`. The existing text emits that string only when `gh` is absent AND nothing is declared, so with `gh` present step 1 always records passed, failed or in progress. Step 6.7's 'no post-merge verification declared, not run' branch is then unreachable on gh hosts.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:124-126`
- **important**: Step 6.7 tells the user to 'run step 6.7 once it passes', but 6.7 reads a result held only in the step-1 session. A later standalone run of 6.7 has no record, or a stale 'in progress' one, to gate on. Housekeeping usually runs right after a merge, so 'in progress' is the common case and the deferred path has no hook. The spec should say that a deferred 6.7 re-runs step 1's verification first.
  - evidence: `docs/design/POST_MERGE_HOST_STEPS.md:190-191`
- **advisory**: Decision 4 says a carry fact is recorded 'for later steps and the report' (for example the twin pull request is unmerged, so the stage is in flight). §4.2 records carry facts for step 8 only, and no step-4/5/7 sentence reads them, so the 'in flight' fact never reaches the plan/roadmap edits it exists to shape.
  - evidence: `docs/design/POST_MERGE_HOST_STEPS.md:171`
- **advisory**: The guarantee that a 2.2 stop ends the run 'before any step mutates anything' rests on step 2's 'Cherry-pick doc-only strays onto $default_branch' being deferred. That instruction is phrased inside a step declared read-only, and step 1's `git fetch origin` writes remote-tracking refs before 2.2.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:139-140`

### Looked for but did not find

- Any Python parser, loader or hook that reads the doctrine's ## Post-merge section, so the prose-only mechanisms need no code hook. `git grep -n "Post-merge"` over plugins/arch-compliance/python and hooks gave no hits, and none were needed
- A repair-on-read or silent-default mechanism in the design. Every absence is reported as 'not declared … skipped' or 'portable rule applied'
- A mutation between steps 1-2 and step 2.5 other than git fetch's remote-tracking refs and the ambiguously placed step-2 cherry-pick
- A second occurrence of 'Tick them.' in SKILL.md that would survive the §4.2 edits (only :387)
- Any post-deploy action that runs with subagents in flight. Lines :38-42 cover everything from 3.5 on

### Mechanism traces

- **pre-flight check stop outcome (step 2.2)**
  - invalid state: an open housekeeping pull request (or other in-progress run) exists for the same merged item when a new run starts, or a declared twin pull request is unmerged
  - producer: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:215`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: Whether housekeeping lands through a pull request at all, and how one is recognised, is a host convention, so the check is a host's pre-flight declaration (§8).
  - spec citation: `docs/design/POST_MERGE_HOST_STEPS.md:164-170`
- **pre-flight restatement refusal (`pre-flight: restates <owner>, not run`)**
  - invalid state: a pre-flight-checks bullet entry whose concern appears in the §4.1 table under a different owning step
  - producer: `config/architecture/ARCHITECTURE.md:319-326`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: Prose, not a parser. The skill already reads ## Post-merge as prose the agent interprets. No Python model, loader or test fixture parses it, and none is added.
  - spec citation: `docs/design/POST_MERGE_HOST_STEPS.md:172-173`
- **post-deploy actions gated on step 1's recorded verification (step 6.7)**
  - invalid state: a declared post-deploy action executes while step 1's record is not `passed` or no verification is declared
  - producer: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:123-126`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/POST_MERGE_HOST_STEPS.md:185-194`
- **failed post-deploy action stops later actions**
  - invalid state: a post-deploy action runs after an earlier declared action in the same run returned failure
  - producer: `docs/design/POST_MERGE_HOST_STEPS.md:192`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/POST_MERGE_HOST_STEPS.md:192-194`
- **built-in portable rule for an absent plan record, closing rule or filing rule (decision 3)**
  - invalid state: the host doctrine's ## Post-merge has no plan-record, closing-rule or filing-rule refinement on the owning bullet
  - producer: `config/architecture/ARCHITECTURE.md:319-326`
  - rung 5 (highest applicable 5); repairs=False
  - hardening rejected because: Three absent refinements have a built-in meaning, the skill's own portable rule … Each is reported as `<rule>: not declared in ## Post-merge, portable rule applied`, and §4.4 records the three meanings in the doctrine's ## Declared, never defaulted.
  - spec citation: `docs/design/POST_MERGE_HOST_STEPS.md:76-82`
- **test asserts `Tick them.` is absent from the skill body**
  - invalid state: post-merge-housekeeping/SKILL.md body contains the substring 'Tick them.'
  - producer: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:387`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/POST_MERGE_HOST_STEPS.md:220-221`

## Claims

- **C1** [premise] [load-bearing]: The portable skill reads four named host conventions (branch lock, worktree daemon probe, post-merge CI workflows, durable tracking target) plus step 5's tracking files from ## Post-merge; a host cannot declare checks on the merge itself, a plan-record rule, a filing or closing rule, an action gated on the post-merge verification, or extra report fields.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:20-24`
- **C2** [premise] [load-bearing]: For each motivating rule in §1's table, the 'portable step that owns the concern today' column is correct: no step owns checks on the merge itself (competing run, twin PR); step 4 owns the plan record and ticks; step 5 owns reconciling tracking docs; step 6 owns filing into the tracking target; step 1 verifies post-merge CI/deploy and no step acts on its result; step 8 owns the report.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:117-126`
- **C3** [premise] [load-bearing]: Step 1 runs the post-merge CI check and any declared verification but records no pass/fail result other than the not-declared/gh-absent skip.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:117-126`
- **C4** [premise]: Cayenne's local skill holds the open-PR race check (#60/#61), the twin check, the do-not-tick plan-record rule, F-### closure against the diff, next-free F-### allocation across main and open PRs, deploy-gated bug-report marking that emails testers, and a report with Gate:/Fixes: lines, at the cited lines (cy: maps to a snapshot at fffc2954).
  - spec citation: `cy:.claude/skills/post-merge-housekeeping/SKILL.md:21-28`
- **C5** [premise] [load-bearing]: No package or hook code parses ## Post-merge (recipe A empty); ARCH_REL's consumers are host.py:30 (existence) and inject_constraints.py:165-168 (whole-text injection).
  - spec citation: `plugins/arch-compliance/python/acf/repo.py:24`
- **C6** [premise]: Deferral: Cayenne's and HistoricMansions' cutovers are adoption work after this release; nothing in this design depends on them.
  - spec citation: `cy:.claude/skills/post-merge-housekeeping/SKILL.md`
- **C7** [premise]: The approved spec POST_MERGE_HOUSEKEEPING_SKILL.md lists four conventions in decision 1 (:36-41), enumerates its checklist from :104 to step 8 at :138, and says tick completed steps at :129; this spec supersedes those parts without editing that spec.
  - spec citation: `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:36-41`
- **C8** [mandate] [load-bearing]: Absent declarations are reported and never defaulted; the three built-in meanings (absent plan record, filing rule, closing rule -> the skill's own portable rule, reported as 'portable rule applied') are recorded in ## Declared, never defaulted, complying with that section.
  - spec citation: `config/architecture/ARCHITECTURE.md:189-216`
- **C9** [mandate]: The new skill prose names no host repository, path or section (## Prose names no host); test_adr_skill_prose.py needs no change, and its FORBIDDEN list covers origin-host vocabulary only.
  - spec citation: `config/architecture/ARCHITECTURE.md:218-228`
- **C10** [mandate]: The skill-prose change ships with a version bump to 0.3.3 in plugin.json and pyproject.toml and an installed-skills byte check, per ## Release discipline; the installed-skills check stays under ## Release discipline rather than becoming a pre-flight check.
  - spec citation: `config/architecture/ARCHITECTURE.md:269-279`
- **C11** [mandate]: Each rule stated once in the step that applies it, the ## Host declarations section holding only the ownership table, and the plan-record rule referred to as 'the plan record (step 4)' elsewhere, satisfy ## Single point of definition.
  - spec citation: `config/architecture/ARCHITECTURE.md:281-298`
- **C12** [shape_fit] [load-bearing]: Each host rule is a refinement on the ## Post-merge bullet of the portable step that already owns its concern (closing rule -> step 5, filing rule -> steps 6/6.5, post-deploy actions -> post-merge CI bullet read at 6.7, plan record -> step 4), and new bullets are added only for concerns no step owns (pre-flight merge checks, report fields); so the §4.1 table gives every concern exactly one declaration and the design creates no second way to declare any concern, including landing on the default branch (step 1) and the shared checkout (step 0).
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:20-24`
- **C13** [shape_fit] [load-bearing]: No other skill, hook or package module already gives a host a pre-flight, plan-record, filing/closing-rule, post-deploy-action or report-field mechanism that these declarations would partially duplicate.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md`
- **C14** [sweep]: The §6 table lists the skill lines the design edits (3, 16-24, 117-126, 233-239, 243-253, 262-266, 349-351, 372-377, 387, 402) and the insertion points (25-26, 153-155, 365-367) correctly, and recipe B's output (3, 233, 235, 387, 402, with 236 continuing 235) is every statement of the tick rule in the skill.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:233-239`
- **C15** [mechanism_justification] [load-bearing]: Refining the owning steps' declarations is justified over hosts keeping local copies, a general host-steps slot, or a portable competing-run check; and the mechanisms refuse (stop, not run, restates) rather than repair.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:233-239`
- **C16** [implementability] [load-bearing]: Pre-flight can run as step 2.2 in the main session after every step 1-2 result (including subagent results) is collected and before step 2.5's first mutation, once per run, with a stop ending the run for every item before anything is mutated.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:28-42`
- **C17** [implementability] [load-bearing]: Post-deploy actions can run as step 6.7 between 6.5 and 7 in the main session with no subagents in flight, gated on the result step 1 is changed to record ('post-merge verification: passed|failed|in progress|not declared'), with a failed action stopping later ones.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:38-42`
- **C18** [implementability] [load-bearing]: Step 5 can apply a declared closing rule and steps 6 and 6.5 a declared filing rule as one added sentence each, without changing those steps' existing filing, reconciliation or STOP behaviour.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:262-266`
- **C19** [implementability]: test_housekeeping_skill_invariants can pin the new strings by extending its required tuple and assert 'Tick them.' is absent; the prose test needs no change.
  - spec citation: `plugins/arch-compliance/tests/test_adr_skill_invariants.py:105-133`
