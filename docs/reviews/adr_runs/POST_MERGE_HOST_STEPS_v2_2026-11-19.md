# Adversarial design review — full detail

Spec: `docs/design/POST_MERGE_HOST_STEPS.md` @ `021aa834a67d8a4d7661f90a9a698e47d73e7031`
Kinds: feature
Outcome: **BLOCKED**
Claims: 19 · Reviewers: 4 · Converged: 1

## Blocking reasons

- load-bearing claim C12 (shape_fit) is REFUTED: The checkout (step 0, SKILL.md:62-68), deploy verification (SKILL.md:123-126) and plan-record parts hold. The tracking concern does not. The spec's own section 4.1 table (POST_MERGE_HOST_STEPS.md:148) gives 'Where deferred items are filed' to the tracking-target bullet plus step 5's tracking files. Step 6 files deferred items into that target (SKILL.md:262-266), and step 5 reconciles tracking docs against the change (SKILL.md:243-253). Two of the three host steps that motivate the design (spec 1, item 3) do exactly that job with host rules. Closing F-### items in the fix roadmap against the diff (cy:...SKILL.md:76-83) is step-5 reconciliation of a tracking file. Taking the next free F-### across main and the open PRs (cy:...SKILL.md:181-201) is a rule for how step 6 files into the tracking target (cy:...SKILL.md:174-180 names FIX_ROADMAP.md as the default home for deferred items). Under decision 2 these host steps restate the tracking-target owner and would be refused as 'restates <owner>, not run'. Otherwise ### Host steps becomes a second place to declare how items are filed and reconciled. The refusal examples (spec :85-86) name only the checkout lock and deploy verification, so nothing in the design decides which way this goes. That is a second way to declare one concern, which the claim says cannot exist.

## Absorptions

- PARTIAL_OVERLAP: '### Host steps (fix-roadmap item closing and next-free-ID filing as motivating instances)' shares responsibility "file deferred items into, and reconcile, the host's tracking target" with plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:262-266 — Shared responsibility R is filing items into the tracking target and closing them there. Extend the tracking-target declaration into a 'tracking target and its filing/closing rules' declaration read by steps 5 and 6. The host's ID-allocation and close-against-diff rules then become values of that declaration, and Host steps keeps only actions no portable step owns (for example the post-deploy notification step).
- BOUNDARY_CUT: '### Host steps (closing fix-roadmap items against the diff)' shares responsibility 'reconcile tracking documents with the merged change' with plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:243-253 — Step 5 already reads 'non-Markdown tracking files declared under ## Post-merge'. Put the host's per-file closing rule there, so step 5 stays the single owner of tracking-doc reconciliation.
- PARTIAL_OVERLAP: '### Pre-flight (merge base is the default branch)' shares responsibility 'decide whether the merged work landed on the default branch' with plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:89-107 — Name step 1's merge verification as the owner of 'landed on the default branch' in the section 4.1 table. A base check then either becomes a cheap early input that step 1 consumes, or is refused as a restatement. State the precedence when they disagree.
- SUBSUMED: '### Plan record' shares responsibility "record a merged plan's status" with plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:233-239 — Already resolved by decision 6: step 4 becomes the container, and the tick rule becomes the portable default instance. The description (:3), Rationalizations (:387) and Red Flags (:402) collapse into references to step 4.
- SUBSUMED: '### Report' shares responsibility 'compose the end-of-run report' with plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:372-377 — Step 8 stays the single report. Host fields are additions read by step 8, and step 8 must also list host-step, restates and precondition-unmet records.

## Converged findings

- [2 reviewers: hardening, sweeper] Step 1a sits inside step 1, which multi-item runs may delegate to read-only subagents; the spec does not say whether pre-flight is delegated, how one item's stop affects the others, or who records carry facts.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:31-38`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:20-24; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:244-245; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:62-67; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:233-239; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:372-377`
- reasoning: I read the whole 414-line skill at 021aa834. The overview names exactly four conventions (20-24), and step 5 also reads declared non-Markdown tracking files (244-245). Every other read of `## Post-merge` serves one of those four: step 0 branch lock (62-64), step 1 CI/deploy (123-126), step 2.5 daemon probe and its data endpoint (180-193), steps 6 and 6.5 tracking target (262-266, 350-351). Step 4's tick rule is unconditional (235-236) and reads no host declaration. Step 8's report is fixed prose with no host-declared fields (374-377). Nothing reads a check on the merge itself or a host step.

#### C2 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:62-67; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:54-60; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:228-231; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:411-414`
- reasoning: Step 0 runs `branch --show-current` and `status --short` on the main checkout (57-60). It inspects a declared lock or branch-guard hook and stops if the checkout is on an unexpected branch, has foreign uncommitted work, or the lock names another branch (62-67). Step 3.5 (228-231) and When NOT to use (411-414) restate the same checkout-scoped concern. Nothing in step 0 looks at open PRs, the PR's base ref or a twin PR.

#### C3 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:3; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:233; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:235-236; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:387; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:402; C:/Users/iball/AppData/Local/Temp/claude/87e26b93c6dabf01/7ee83bd0-9038-461f-98de-0102609a84f5/scratchpad/cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:65-66`
- reasoning: I ran `git grep -n -i -E 'tick|checkbox|\[x\]'` on the skill. Its hits are lines 3, 233, 235, 236 (the continuation of 235), 387 and 402 and nothing else, so the tick rule lives at exactly the cited lines. Step 4 says 'tick every completed step `[x]`' (235-236). The Cayenne snapshot says 'Do not tick the checkboxes' at :65-66 and repeats it at :235 ('checkboxes are **not** status').

#### C4 — SURVIVED
- evidence: `C:/Users/iball/AppData/Local/Temp/claude/87e26b93c6dabf01/7ee83bd0-9038-461f-98de-0102609a84f5/scratchpad/cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:21-28; C:/Users/iball/AppData/Local/Temp/claude/87e26b93c6dabf01/7ee83bd0-9038-461f-98de-0102609a84f5/scratchpad/cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:31-35; C:/Users/iball/AppData/Local/Temp/claude/87e26b93c6dabf01/7ee83bd0-9038-461f-98de-0102609a84f5/scratchpad/cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:38-40; C:/Users/iball/AppData/Local/Temp/claude/87e26b93c6dabf01/7ee83bd0-9038-461f-98de-0102609a84f5/scratchpad/cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:76-83; C:/Users/iball/AppData/Local/Temp/claude/87e26b93c6dabf01/7ee83bd0-9038-461f-98de-0102609a84f5/scratchpad/cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:117-129; C:/Users/iball/AppData/Local/Temp/claude/87e26b93c6dabf01/7ee83bd0-9038-461f-98de-0102609a84f5/scratchpad/cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:181-201; C:/Users/iball/AppData/Local/Temp/claude/87e26b93c6dabf01/7ee83bd0-9038-461f-98de-0102609a84f5/scratchpad/cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:214-223`
- reasoning: I read the Cayenne snapshot. Each item is at the cited lines: the open-PR race check naming #60/#61 (21-28), the base-is-main check citing #125 (31-35), the RecipeParser twin check (38-40), F-### closure against the diff (76-83), deploy-gated bug-report marking that emails the tester (117-129), next-free F-### across main and open PRs (181-201), and a report template with `Gate:` and `Fixes:` lines (214-223).

#### C5 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:24; plugins/arch-compliance/python/acf/adr/host.py:30; plugins/arch-compliance/hooks/inject_constraints.py:165-168; plugins/arch-compliance/tests/test_adr_skill_invariants.py:117-118`
- reasoning: I ran recipe A (`git grep -n 'Post-merge'` over python/ and hooks/): no output. I also ran a case-insensitive `post.merge` over the same paths: the only hits are two docstring/comment mentions of the skill name in acf/adr/ledger.py:103,137, and neither parses a section. `git grep ARCH_REL` in plugins/ finds two package/hook consumers: host.py:30 (require_file, existence only) and inject_constraints.py:165-168 (reads the whole text and truncates it). The other ARCH_REL uses are skill prose (acf-mandate anchors, architecture-review), not package or hook code. registry.missing_anchors (registry.py:229) takes the text as a parameter and matches anchor lines; it does not parse `## Post-merge`.

#### C6 — SURVIVED
- evidence: `docs/design/POST_MERGE_HOST_STEPS.md:125-128; docs/design/POST_MERGE_HOST_STEPS.md:25-28; config/architecture/ARCHITECTURE.md:319-328`
- reasoning: None of the design's mechanisms (§4.2 skill text, §4.3 test strings, §4.4 doctrine line and version bump) reads or writes a Cayenne or HistoricMansions file. This repo's own `## Post-merge` (ARCHITECTURE.md:319-328) is the only host doctrine the design touches. Cayenne is cited only as a motivating instance, and DoD item 6 only names the cutovers in the PR body. Nothing in the release waits on either cutover.

#### C7 — SURVIVED
- evidence: `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:36-41; docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:129; docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:2-3`
- reasoning: In the approved spec (status at :2-3), decision 1 lists four conventions at :36-39, and the not-declared rule follows at :41. Its step 4 says 'tick completed steps `[x]`' at :129. `git diff --stat e9dd881 HEAD` shows the branch adds only the new spec, its review records and a ledger line; POST_MERGE_HOUSEKEEPING_SKILL.md is unedited. The old spec's step 8 rule (:138, 'listing the outcome of every check') and its not-declared rule (:41) are extended by the new sub-sections, not contradicted.

### Unanchored findings

- **important**: Decision 5 gates host steps on 'step 1's recorded post-merge CI or deploy result', but step 1 only says to run any declared CI/deploy verification and records nothing except the not-declared/gh-absent case. §4.2 does not change step 1 to record a pass/fail result, so the precondition for a side-effecting host step (one that emails testers) reads a value no step is told to produce.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:123-126`
- **advisory**: The superseded spec's checklist enumeration ('Its checklist steps are:' at :104 through step 8 at :138) gains steps 1a and 6.7 under this design, but the Supersedes header names only decision 1 (:36-41) and step 4 (:129) as superseded.
  - evidence: `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:104`

### Looked for but did not find

- a 'Post-merge' string (any case) in plugins/arch-compliance/python or plugins/arch-compliance/hooks that parses the section rather than naming the skill
- an ARCH_REL consumer in package or hook code other than host.py:30 and inject_constraints.py:165
- a tick/checkbox/[x] line in the skill other than 3, 233, 235-236, 387, 402
- any existing skill line that reads a host-declared check on open PRs, PR base ref or twin PRs
- an edit to docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md in e9dd881..021aa834
- a mismatch between the spec's cited ARCHITECTURE.md lines (:220-221, :271-272, :319-328, :323-326) and their content
- a 'Post-merge' test pin other than test_adr_skill_invariants.py:117-118

## compliance

### Claim verdicts

#### C8 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:191-204; docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:41; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:23-24; docs/design/POST_MERGE_HOST_STEPS.md:89-94`
- reasoning: The mandate's text covers the gate's adr.yml values ('no default stands in for a missing declaration ... fails loud') and the review's review.yml values. It also lets a built-in meaning stand for an absent value when the doctrine records it (:196-204). The approved predecessor spec applied this section to `## Post-merge` as 'no silent skipping': an absent check is reported in step 8, not left out (POST_MERGE_HOUSEKEEPING_SKILL.md:41). The live skill does this at SKILL.md:23-24. Decision 3 keeps that shape. Each absent sub-section adds nothing and gets a named step-8 line. The one built-in meaning, the portable plan-record rule, is the skill's own existing procedure, not an invented host value, and it is reported as 'portable rule applied'. No host value is made up. One residual gap is filed as an advisory finding: unlike the review's absent-value meanings, this built-in meaning is not recorded in the doctrine section.

#### C9 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:220-227; plugins/arch-compliance/tests/test_adr_skill_prose.py:14-39; plugins/arch-compliance/tests/test_adr_skill_prose.py:73-79; docs/design/POST_MERGE_HOST_STEPS.md:159-197`
- reasoning: The mandate says: 'Skill prose and runtime messages name no host repository, path or section'. Its row checks the housekeeping skill against an enumerated FORBIDDEN list of known origin-host (HistoricMansions) vocabulary. test_adr_skill_prose.py already includes HOUSEKEEPING/SKILL.md in FILES (:14, :21). The list (:31-39) holds origin-host words only, as both the doctrine (:226-227) and the claim say. Every prose fragment §4.2 proposes is generic: step names, sub-section headings that belong to the plugin's own `## Post-merge` convention, 'twin pull request', 'cherry-picking onto the default branch'. None names Cayenne, HistoricMansions or a host path. So the test needs no change, and §7 item 1 keeps the FORBIDDEN check as a done criterion.

#### C10 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:271-276; plugins/arch-compliance/.claude-plugin/plugin.json:3; pyproject.toml:3; scripts/check_installed_skills.py:18-23`
- reasoning: The mandate says: 'A change to a skill's prose bumps the plugin version in plugin.json and pyproject.toml'. Before a gate or housekeeping run, the four skill trees are byte-checked. Both files are at 0.3.2 today, and the spec bumps both to 0.3.3 (§4.4, §7 item 4). check_installed_skills.py already lists post-merge-housekeeping in GATE_SKILLS, so no script change is needed. §7 item 5 runs the check after reinstall.

#### C11 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:283-285; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:3; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:235-236; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:387; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:402; docs/design/POST_MERGE_HOST_STEPS.md:143-152`
- reasoning: The lifted rule says a decision procedure needed in more than one place 'must have exactly one canonical implementation that every call site consumes'. Today the tick rule is stated four times: the description (:3), step 4 (:235-236), the Rationalizations row (:387) and the Red Flags bullet (:402). Decision 6 leaves the rule only in step 4, and the other three refer to 'the plan-record rule (step 4)'. §4.3 pins this, and its 'Tick them.' absence assertion keeps the restatement from coming back. The §4.1 table gives each concern exactly one owner, and the restates-not-run rule refuses a second owner. The claim holds for decisions 2 and 6. A separate repetition of decisions 4 and 5 inside the new prose is filed as an advisory finding.

### Unanchored findings

- **advisory**: The absent-`### Plan record` built-in meaning (the portable tick rule applies) is a built-in meaning for an absent declaration. `## Declared, never defaulted` records each such meaning for the review ('recorded here'), but §4.4 adds a line only to `## Post-merge` and does not record this meaning in `## Declared, never defaulted`.
  - evidence: `config/architecture/ARCHITECTURE.md:196-204`
- **advisory**: §8 says 'The §4.1 table is the single statement, and the steps point to it'. But §4.2 restates the decision 4 and decision 5 rules in two places. They appear in the new `## Host sub-sections` (decisions 2-5) and again in the bodies of step 1a and step 6.7: stop/carry, `restates <owner>, not run`, precondition unmet, dependents not run. That gives two statements of each rule in one skill, against `## Single point of definition`.
  - evidence: `docs/design/POST_MERGE_HOST_STEPS.md:163-185`

### Looked for but did not find

- ## High-frequency misses / completeness claim without a recipe: the spec's 'every line the design touches is in that list' (§5) is backed by recipe B's re-runnable git grep (§6). The by-eye read of all 414 lines is stated as a second method, not as the only backing. The section is named as governing — no finding.
- ## High-frequency misses / host name in skill prose: the proposed prose fragments in §4.2 are generic — see C9.
- ## One base exception, ## Declared text decoding, ## POSIX paths, ## Fail loud, ## No shims: §3 says there is no Python change, and recipe A shows no package or hook code reads `## Post-merge` — not touched.
- ## One owner for host paths: no new executable skill snippet is added. The skill still locates the doctrine through acf.repo.ARCH_REL (SKILL.md:22) — not touched.
- ## High-frequency misses / a check re-implemented in a skill instead of consumed from the package: the new steps read doctrine prose. They re-implement no acf.registry, KNOWN_DETECTORS or acf.repo check — not touched.
- ## Frozen ledger format: step 6's LedgerAmendment snippet is unchanged (§3 non-goals) — not touched.
- ## Live consumers: no export is added or removed — not touched.
- ## Scoped refactor: edits are limited to the housekeeping SKILL.md lines in the recipe B table, one invariant test, one doctrine line and two version fields — within scope.
- ## Host detectors and call sites, ## Fail-loud ratchet, ## Façade sinks, ## FSM transitions, ## React boundaries, ## Soft fail-loud smells, ## Build artifacts: no mandates.yml row, detector or generated tree is touched.
- ## Post-merge: named as governing. §4.4 adds a 'declares none' line for this repository's own four sub-sections.

## sweeper

### Claim verdicts

#### C12 — REFUTED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:262-266; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:243-253; docs/design/POST_MERGE_HOST_STEPS.md:148; cy:.claude/skills/post-merge-housekeeping/SKILL.md:76-83; cy:.claude/skills/post-merge-housekeeping/SKILL.md:174-186`
- reasoning: The checkout (step 0, SKILL.md:62-68), deploy verification (SKILL.md:123-126) and plan-record parts hold. The tracking concern does not. The spec's own section 4.1 table (POST_MERGE_HOST_STEPS.md:148) gives 'Where deferred items are filed' to the tracking-target bullet plus step 5's tracking files. Step 6 files deferred items into that target (SKILL.md:262-266), and step 5 reconciles tracking docs against the change (SKILL.md:243-253). Two of the three host steps that motivate the design (spec 1, item 3) do exactly that job with host rules. Closing F-### items in the fix roadmap against the diff (cy:...SKILL.md:76-83) is step-5 reconciliation of a tracking file. Taking the next free F-### across main and the open PRs (cy:...SKILL.md:181-201) is a rule for how step 6 files into the tracking target (cy:...SKILL.md:174-180 names FIX_ROADMAP.md as the default home for deferred items). Under decision 2 these host steps restate the tracking-target owner and would be refused as 'restates <owner>, not run'. Otherwise ### Host steps becomes a second place to declare how items are filed and reconciled. The refusal examples (spec :85-86) name only the checkout lock and deploy verification, so nothing in the design decides which way this goes. That is a second way to declare one concern, which the claim says cannot exist.

#### C13 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_skill_invariants.py:117-118; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:123-126; plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:232`
- reasoning: Searched by behaviour across plugins/arch-compliance (skills, hooks, python, tests) for: a host-declared check run before a skill proceeds ('pre-?flight', 'before (any|the) (gate|run)', 'step 0', 'check_installed_skills'); host-declared extra steps or report fields ('host step', 'declared (under|in) ##', "host's doctrine", 'doctrine declares'); and plan-record rules ('tick', 'checkbox', 'plan record'). In Python files, 'merge|housekeeping' hits only adr/ledger.py's docstrings (:103, :137) and the test pins in test_adr_skill_invariants.py:117-118. Every "host's doctrine" hit in the other skills (responding-to-adversarial-review/SKILL.md:232, :246; adversarial-design-review/SKILL.md:3, :472) concerns diagnosis ownership, not post-merge procedure. No skill, hook or package module gives a host a pre-flight, host-step, plan-record or report-field mechanism. The nearest pre-run check is the doctrine's installed-skills byte check (config/architecture/ARCHITECTURE.md:272-276), which lives in scripts/, not in a skill, hook or module (see the advisory finding).

#### C14 — REFUTED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:284; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:292-293; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:313; config/architecture/ARCHITECTURE.md:191-192; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:225`
- reasoning: I re-ran recipe B by eye over the full 415-line file. The listed rows do match, though 225 inside '225-228' does not match the regex and the table drops line 236, the rest of the tick-rule sentence begun at 235. The claim says a full read finds no reading site the recipe misses, and that is false. Step 6 reads the host's declared values: '(repo / ADR_REL).is_file()' (:284), 'cfg = load_host_config(repo)' (:293), 'cfg.runs_dir' (:298) and 'repo / cfg.ledger_path' (:313). The doctrine states these values are 'declared by the host in config/architecture/adr.yml' (ARCHITECTURE.md:191-192). None of those lines contains a recipe word. The 'host branch guard' sites (:225, :392) also read a host-declared guard with no recipe word. The recipe swept by vocabulary, the omission is the kind of miss that method produces, and the table leaves these lines out.

### Unanchored findings

- **important**: Two of the spec's three motivating host steps (closing F-### items in the fix roadmap against the diff, and taking the next free F-### across main and open PRs) restate the tracking concern that section 4.1 gives to the tracking-target bullet and step 5's tracking files. Decision 2 then either refuses them as 'restates <owner>, not run', which defeats the cutover the design exists for, or lets ### Host steps become a second owner of how items are filed and reconciled. The design should extend the tracking-target declaration to carry host filing and closing rules (ID allocation, closing against the diff), or state that a host step may refine a tracking-target behaviour and say how that differs from a restatement.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:262-266`
- **advisory**: Pre-flight's 'its base is the default branch' check (section 4.1 row, spec :149) and step 1's content-presence verification on origin/$default_branch (SKILL.md:89-107) both decide whether the merge landed on the default branch. Section 4.1 lists no owner for step 1's merge verification, so the 'restates <owner>' refusal cannot apply, and the two checks may disagree with no stated precedence.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:89-107`
- **advisory**: The step 8 edit in section 4.2 (spec :189-190) adds only carry facts and ### Report fields. Decision 2 says 'restates <owner>, not run' is reported in step 8, and decision 5 records '<host step>: precondition unmet (<what>), not run'. Neither those records, nor host-step failures, nor 'plan record: not declared in ## Post-merge, portable rule applied' fits step 8's existing '<check>: not declared in ## Post-merge, skipped' template (SKILL.md:374-377), so step 8 has no stated duty to report them.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:374-377`
- **advisory**: Step 1a sits inside step 1, which multi-item runs hand to parallel read-only subagents that return raw output (SKILL.md:31-39). The design does not say whether a pre-flight 'stop' from one subagent ends the whole run or only that item, or who records carry facts.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:31-39`
- **advisory**: This repository already declares a check that runs before every post-merge-housekeeping run (the installed-skills byte check, ARCHITECTURE.md:272-276), and the approved housekeeping spec once placed an installed-skill check in step 0 (POST_MERGE_HOUSEKEEPING_SKILL.md:44). Yet section 4.4 has the doctrine say the repository declares no ### Pre-flight. The design should say whether host pre-run tool checks belong under ### Pre-flight or stay outside it, because otherwise 'checks before housekeeping proceeds' has two declaration homes.
  - evidence: `config/architecture/ARCHITECTURE.md:272-276`

### Looked for but did not find

- Python or hook parsing of '## Post-merge' or its sub-sections: grep 'merge|housekeeping' over *.py in plugins/arch-compliance (only ledger.py docstrings and test pins)
- Another skill offering host-declared pre-flight, host steps, plan-record or report fields: grep 'pre-?flight|host step|plan record|declared (under|in) ##|host's doctrine' over plugins/
- A second statement of the tick rule inside the skill beyond :3, :233-239, :387, :402: grep 'tick|checkbox' over the skill
- An approved document rejecting host-extensible post-merge steps: grep 'Post-merge|housekeeping' across docs/design and config/architecture (POST_MERGE_HOUSEKEEPING_SKILL.md decision 1 allows doctrine-driven conventions and forbids only a new YAML file)

### Relationships

- PARTIAL_OVERLAP: `### Host steps (fix-roadmap item closing and next-free-ID filing as motivating instances)` — responsibility `file deferred items into, and reconcile, the host's tracking target` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:262-266`
  - resolution: Shared responsibility R is filing items into the tracking target and closing them there. Extend the tracking-target declaration into a 'tracking target and its filing/closing rules' declaration read by steps 5 and 6. The host's ID-allocation and close-against-diff rules then become values of that declaration, and Host steps keeps only actions no portable step owns (for example the post-deploy notification step).
- BOUNDARY_CUT: `### Host steps (closing fix-roadmap items against the diff)` — responsibility `reconcile tracking documents with the merged change` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:243-253`
  - resolution: Step 5 already reads 'non-Markdown tracking files declared under ## Post-merge'. Put the host's per-file closing rule there, so step 5 stays the single owner of tracking-doc reconciliation.
- PARTIAL_OVERLAP: `### Pre-flight (merge base is the default branch)` — responsibility `decide whether the merged work landed on the default branch` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:89-107`
  - resolution: Name step 1's merge verification as the owner of 'landed on the default branch' in the section 4.1 table. A base check then either becomes a cheap early input that step 1 consumes, or is refused as a restatement. State the precedence when they disagree.
- ADJACENT: `### Pre-flight (someone else is already housekeeping this merge)` — responsibility `detect a competing session` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:62-68`
  - resolution: None
  - non-merge: The branch lock guards the shared checkout's HEAD. The pre-flight check guards against competing housekeeping pull requests opened from different checkouts. These are different objects, as the spec states at :48-49 and :239-241.
- ADJACENT: `### Host steps (post-deploy tester notification)` — responsibility `act only after deploy is verified` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:123-126`
  - resolution: None
  - non-merge: The host step consumes step 1's recorded deploy result as a precondition (decision 5) and never re-verifies the deploy. Verification stays with the post-merge CI bullet.
- SUBSUMED: `### Plan record` — responsibility `record a merged plan's status` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:233-239`
  - resolution: Already resolved by decision 6: step 4 becomes the container, and the tick rule becomes the portable default instance. The description (:3), Rationalizations (:387) and Red Flags (:402) collapse into references to step 4.
- SUBSUMED: `### Report` — responsibility `compose the end-of-run report` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:372-377`
  - resolution: Step 8 stays the single report. Host fields are additions read by step 8, and step 8 must also list host-step, restates and precondition-unmet records.

### Two-owner counts

- file deferred items into the host tracking target (including ID allocation): 2
- reconcile tracking documents against the merged diff: 2
- decide the merge landed on the default branch: 2
- host-declared checks run before a housekeeping run proceeds: 2

### Document conflicts

- `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:129` (contradicts): If the branch executed a tracked implementation plan, tick completed steps `[x]`, annotate the merge (PR #, squash SHA, date)
- `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:40` (restates): Durable tracking target (the roadmap, remediation ledger, or issue tracker where deferred review items and guard escapes are filed).
- `config/architecture/ARCHITECTURE.md:273` (restates): Before a gate or `post-merge-housekeeping` run, the installed copy of the two gate skills, `post-merge-housekeeping` and `architecture-review` is byte-checked against the clone

## hardening

### Claim verdicts

#### C15 — SURVIVED
- evidence: `docs/design/POST_MERGE_HOST_STEPS.md:64-68; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:66; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:87; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:233-239`
- reasoning: The written justification is spec:64-68. A local copy leaves two live copies or a cutover that drops steps, and each sub-section is the single place for its concern. A pointer to a host procedure run in full is not rejected by name. It falls under the same argument, because a full host procedure would restate steps the portable skill owns. That is the restatement decision 2 refuses. The mechanisms the design adds refuse rather than repair. A pre-flight 'stop' ends the run, the same STOP pattern the skill already uses at SKILL.md:66 and :87. A restating sub-section is 'not run'. An unmet precondition is 'not run', and so is anything that depends on it. Each is reported in step 8. The plan-record rule replaces the tick rule at SKILL.md:233-239 as a declaration and repairs no state. There is one non-refusing default: a host step with no declared precondition runs unconditionally (spec:329). That is filed separately as advisory.

#### C16 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:80-87; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:28-29; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:89-98`
- reasoning: $default_branch is resolved at SKILL.md:80-85, with a STOP at :87 if it is empty. Content verification starts at :89. A seam therefore exists between them. SKILL.md:28-29 declares steps 1-2 read-only. The first mutations come later: step 2.5's process kills at :188, teardown at :197-205, and the checkout at :220. Step 1a therefore runs while everything so far is read-only and the main checkout is untouched. One case is unspecified. In multi-item runs, steps 1-2 may be delegated to subagents (SKILL.md:31-38), and the spec does not say whether 1a goes with them. That is filed as an advisory finding.

#### C17 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:38-42; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:338; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:367`
- reasoning: Step 6.5 starts at SKILL.md:338 and step 7 at :367, so a step 6.7 fits between them. SKILL.md:39-42 says everything from step 3.5 on stays in the main session, sequential, with no subagents in flight. A step inserted after 6.5 inherits that rule with no new hook. Side note: SKILL.md:228-231 defers 'Steps 4-7' when a lock is held, which covers 6.7. Host steps are then deferred too, which is a refusal, not a repair.

#### C18 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:117-126; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:372-377`
- reasoning: Step 1 runs `gh run list` and every declared post-merge CI or deploy verification (SKILL.md:117-126). When neither applies, it records 'post-merge CI check: not declared ... skipped'. Step 8 (:372-377) already reports what housekeeping found, so step 1's outcome is in the run's record for a later step to read. The SKILL never tells the agent to record the pass/fail result as a named fact. The result exists as command output in the main session, which is where step 6.7 runs (:38-42). Results of earlier host steps are produced in the same sequential session. Every failure case resolves to 'not run': a CI run still in progress, a gh-absent skip, or a failed check. That direction is safe.

#### C19 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_skill_invariants.py:113-125; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:387; plugins/arch-compliance/tests/test_adr_skill_prose.py:31-38`
- reasoning: The required tuple at test_adr_skill_invariants.py:113-124 is a plain substring loop (`assert required in body`, :125). Appending strings works, and so does adding `assert 'Tick them.' not in body`. `git grep 'Tick them'` finds only SKILL.md:387, which the design rewrites. The FORBIDDEN list (test_adr_skill_prose.py:31-38) holds origin-host vocabulary, and the strings the spec proposes contain none of it. No other test pins the step-4 heading or 'tick the checkboxes'. A repo-wide git grep for 'Plan truthfulness', 'tick the checkboxes' and 'Tick them' outside SKILL.md found nothing.

### Unanchored findings

- **advisory**: A host step with no declared precondition runs unconditionally, including a side-effecting one such as an email-sending step. The risk row accepts this ('A host that declares no precondition owns that choice'). Requiring every host step to state its precondition, or 'none', would make the unguarded case an explicit declaration instead of a silent default.
  - evidence: `docs/design/POST_MERGE_HOST_STEPS.md:329`
- **advisory**: Step 1a sits inside step 1, which the skill lets the agent delegate per item to read-only subagents in multi-item runs. The spec does not say whether pre-flight is delegated. It also does not say how one item's 'stop' affects the other items, or whether a per-run check such as 'who else is housekeeping' runs once or once per item.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:31-38`
- **advisory**: The motivating pre-flight check, a competing housekeeping PR already open, guards against a hazard produced by concurrent runs of the portable skill itself. Leaving it as a host-declared pre-flight means every host must re-declare it. Hardening the producer would mean a portable check in the skill.
  - evidence: `cy:.claude/skills/post-merge-housekeeping/SKILL.md:21-28`

### Looked for but did not find

- Python consumers of the doctrine's ## Post-merge contents. git grep 'Post-merge' over the package and hooks returns nothing. acf.review.doctrine_section (plugins/arch-compliance/python/acf/review/__init__.py:14-30) ends a section only at a heading of the same or higher level, so new ### sub-sections stay inside ## Post-merge. No mandates.yml row anchors ## Post-merge.
- Tests other than test_housekeeping_skill_invariants and test_adr_skill_prose that pin the step-4 tick wording or heading: none found.
- A repair-on-read in the design. The plan-record override is a declaration that replaces the tick rule, not a normalizer. Carry facts are recorded, not acted on. Pre-flight remedies go to the user and are never performed.

### Mechanism traces

- **restates <owner>, not run**
  - invalid state: An entry under ### Pre-flight or ### Host steps whose concern the section 4.1 table assigns to another declaration, for example a pre-flight check on the checkout lock or a host step that verifies a deploy
  - producer: `config/architecture/ARCHITECTURE.md:319`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: Prose, not a parser. The skill already reads `## Post-merge` as prose the agent interprets. No Python model, loader or test fixture parses it, and none is added
  - spec citation: `docs/design/POST_MERGE_HOST_STEPS.md:85-88`
- **host step precondition, precondition unmet (<what>), not run, plus dependent not-run cascade**
  - invalid state: A host step whose declared precondition names step 1's post-merge CI or deploy result, or an earlier host step's result, where that result is failed, in progress, or not run
  - producer: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:117-126`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: A host that declares no precondition owns that choice in its doctrine
  - spec citation: `docs/design/POST_MERGE_HOST_STEPS.md:106-112`
- **### 1a. Host pre-flight checks (stop / carry)**
  - invalid state: A merge for which another housekeeping PR is already open, or whose base is not $default_branch, or whose cross-repository twin PR is unmerged
  - producer: `cy:.claude/skills/post-merge-housekeeping/SKILL.md:21-28`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/POST_MERGE_HOST_STEPS.md:95-105`

## Claims

- **C1** [premise] [load-bearing]: The portable skill reads four named host conventions (branch lock, worktree daemon probe, post-merge CI workflows, durable tracking target) plus step 5's tracking files from ## Post-merge, and has no slot for a check on the merge itself, a host plan-record rule, a host step or host report fields.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:20-24`
- **C2** [premise] [load-bearing]: Step 0's branch-lock declaration covers only the shared checkout's HEAD, lock or branch guard; it does not cover checks on the merge itself (who else is housekeeping it, its base, its twins).
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:62-67`
- **C3** [premise] [load-bearing]: Step 4 instructs ticking every completed step [x]; the tick rule is stated or presupposed at exactly SKILL.md lines 3, 233, 235, 387 and 402 (the grep in the response-record style recipe), and Cayenne's local copy says do not tick (cy: maps to a snapshot at fffc2954).
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:233-236`
- **C4** [premise]: Cayenne's local skill holds the open-PR race check (#60/#61), base-is-main check (#125), twin check, F-### closure against the diff, cross-PR F-### allocation, deploy-gated bug-report marking that emails testers, and a report with Gate:/Fixes: lines.
  - spec citation: `cy:.claude/skills/post-merge-housekeeping/SKILL.md:21-28`
- **C5** [premise] [load-bearing]: No package or hook code parses ## Post-merge (recipe A empty); ARCH_REL's consumers are host.py:30 (existence) and inject_constraints.py:165-168 (whole-text injection).
  - spec citation: `plugins/arch-compliance/python/acf/repo.py:24`
- **C6** [premise]: Deferral: Cayenne's and HistoricMansions' cutovers are adoption work after this release; nothing in this design depends on them.
  - spec citation: `cy:.claude/skills/post-merge-housekeeping/SKILL.md`
- **C7** [premise]: The approved spec POST_MERGE_HOUSEKEEPING_SKILL.md decision 1 lists four conventions (:36-41) and its step 4 design says tick completed steps (:129); this spec supersedes only those two parts without editing that spec.
  - spec citation: `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:36-41`
- **C8** [mandate] [load-bearing]: Absent sub-sections are reported (pre-flight/host steps/report: not declared ... skipped; plan record: not declared ..., portable rule applied) and never defaulted, complying with ## Declared, never defaulted.
  - spec citation: `config/architecture/ARCHITECTURE.md:189-216`
- **C9** [mandate]: The new skill prose names no host repository, path or section (## Prose names no host); test_adr_skill_prose.py needs no change, and its FORBIDDEN list covers origin-host vocabulary only.
  - spec citation: `config/architecture/ARCHITECTURE.md:218-228`
- **C10** [mandate]: The skill-prose change ships with a version bump to 0.3.3 in plugin.json and pyproject.toml and an installed-skills byte check, per ## Release discipline.
  - spec citation: `config/architecture/ARCHITECTURE.md:269-279`
- **C11** [mandate]: One owner per concern (decision 2) and one statement of the plan-record rule (decision 6) satisfy ## Single point of definition.
  - spec citation: `config/architecture/ARCHITECTURE.md:281-298`
- **C12** [shape_fit] [load-bearing]: The four sub-sections extend the existing ## Post-merge declaration shape and, with decision 2's one-owner rule and the restates-<owner> refusal, create no second way to declare any concern: the branch lock still owns the checkout, the post-merge CI bullet still owns deploy verification, and the plan-record rule is stated once in step 4.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:20-24`
- **C13** [shape_fit] [load-bearing]: No other skill, hook or package module already gives a host a pre-flight, host-step, plan-record or report-field mechanism that these sub-sections would partially duplicate.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md`
- **C14** [sweep]: Recipe B (git grep -n -i -E 'Post-merge|declared|declares|tick|unticked|checkbox' on the skill) plus the per-line table lists every line of the skill that reads a declared value or states the plan-record rule; lines 2, 6 and 138 are correctly excluded; a full read finds no reading site the recipe misses.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:188-193`
- **C15** [mechanism_justification] [load-bearing]: Adding host sub-sections to the portable skill is justified over hosts keeping local copies or pointing to a host procedure the skill runs in full, and the mechanisms refuse (stop, not run, restates) rather than repair.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:233-239`
- **C16** [implementability] [load-bearing]: Pre-flight can run as step 1a, after step 1 resolves $default_branch (SKILL.md:80-87) and before content verification, while every step is still read-only and the main checkout untouched.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:80-87`
- **C17** [implementability] [load-bearing]: Host steps can run as step 6.7 between 6.5 and 7 in the main session with no subagents in flight, under the existing rule that everything from step 3.5 on is main-session and sequential.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:38-42`
- **C18** [implementability] [load-bearing]: A host step's precondition on step 1's recorded CI/deploy result or on an earlier host step's result can be checked by the agent from what the run recorded, so unmet preconditions and dependents are recorded as not run.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:117-126`
- **C19** [implementability]: test_housekeeping_skill_invariants can pin the new strings by extending its required tuple and assert 'Tick them.' is absent; the prose test needs no change.
  - spec citation: `plugins/arch-compliance/tests/test_adr_skill_invariants.py:105-133`
