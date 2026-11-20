# Adversarial design review — full detail

Spec: `docs/design/POST_MERGE_HOST_STEPS.md` @ `510b8626dd53ecaa712d434bb584fa89f949eb54`
Kinds: feature
Outcome: **BLOCKED**
Claims: 18 · Reviewers: 4 · Converged: 1

## Blocking reasons

- load-bearing claim C11 (shape_fit) is REFUTED: The shape exists: the skill reads host values from `## Post-merge` as prose and reports a missing one as 'not declared ... skipped' (SKILL.md:20-24, 62-64, 123-126, 180-184). The doctrine declares them as bullets (ARCHITECTURE.md:321-326). It is the nearest shape. But the generic `### Pre-flight` and `### Host steps` lists cover concerns that existing bullets already handle, so a host now has two ways to declare the same convention. (1) Step 0 already runs a host-declared stop check before mutation: the shared-checkout branch lock or branch guard, 'STOP and ask the user' (SKILL.md:62-67). A pre-flight check such as 'another session is already doing this housekeeping' is the same kind of check: another owner holds this work, so stop. The branch lock itself could also be written as a pre-flight check. The spec gives no rule for which form a host must use, or what happens when both are present. (2) Step 1 already runs 'any post-merge CI or deploy verification declared under ## Post-merge' (SKILL.md:123-126). The spec's own example host-step precondition is 'only after the deploy declared under post-merge CI is verified live' (spec decision 4). A host can put deploy verification in the bullet (run at step 1), in a host step (run at 6.7), or in a host step's precondition, and nothing makes one canonical. The section is still the single place to declare, but within it the extension creates a second channel for these concerns, so 'no second way' does not hold as stated.

## Absorptions

- PARTIAL_OVERLAP: '### Pre-flight sub-section and step -1' shares responsibility 'stop the run on a host-declared condition before mutating shared state' with plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:62-67 — Shared responsibility R: a host-declared 'another owner holds this work, stop' gate. Make `### Pre-flight` the single container for host stop checks and treat the branch-lock bullet as one standard pre-flight check (or state that the branch lock must stay a bullet and pre-flight must not restate it). Step 0's lock inspection then consumes the same list.
- PARTIAL_OVERLAP: '### Host steps (step 6.7) with preconditions' shares responsibility 'verify a declared deploy or post-merge CI result' with plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:123-126 — Shared responsibility R: deploy verification. A host-step precondition about a deploy should cite step 1's recorded result of the declared post-merge CI/deploy check rather than re-verify it. State that host steps may not declare a deploy verification of their own.
- BOUNDARY_CUT: '### Plan record sub-section' shares responsibility "decide how a merged plan's completion is recorded" with plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:235-236 — The override takes over step 4's rule but leaves restatements at :3, :387 and :402 asserting the portable rule. Make step 4 the only statement of the plan-record rule, and make the rationalization, red flag and description refer to 'the plan-record rule (step 4)'.

## Converged findings

- [3 reviewers: compliance, refuter, sweeper] ### Plan record overrides the tick rule only in step 4; the same rule is restated unconditionally in the skill's description (SKILL.md:3), the Rationalizations row 'Tick them.' (:387) and the Red Flag 'A merged plan with unticked boxes' (:402), so a host declaring 'do not tick' still gets instructions to tick.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:3`
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:387`
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:402`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:20-24; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:62-64; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:123-126; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:180-184; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:244-245; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:262-266; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:349-351; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:374-377`
- reasoning: Read the whole skill at 510b862. Every ## Post-merge reading site is one of: branch lock (:62-64), post-merge CI/deploy verification (:123-126), worktree daemon probe (:180-184), non-Markdown tracking files (:244-245), durable tracking target (:262-266, :349-351), plus the generic absent-value report (:22-24, :374-377). Nothing reads a host check before step 0. Step 4 (:233-239) has no override hook. No site runs an arbitrary host action, and step 8 is a fixed one-or-two-sentence report with no host fields. Nuance: :123-124 ('any post-merge CI or deploy verification declared') is open-ended, but only for CI/deploy verification. It is not a general host-step slot, so the claim holds.

#### C2 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:233-236; C:/Users/iball/AppData/Local/Temp/claude/87e26b93c6dabf01/7ee83bd0-9038-461f-98de-0102609a84f5/scratchpad/cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:62-66`
- reasoning: The portable step 4 heading is 'tick the checkboxes NOW', and its body says to tick every completed step [x] and add a merge annotation (PR #, SHA, date). The Cayenne snapshot :65-66 says 'Do not tick the checkboxes' and has a **Merged:** header carry the truth. Cayenne :50 also says plan checkboxes are not the record. The two rules are opposites, as claimed.

#### C3 — SURVIVED
- evidence: `C:/Users/iball/AppData/Local/Temp/claude/87e26b93c6dabf01/7ee83bd0-9038-461f-98de-0102609a84f5/scratchpad/cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:21-28; .../cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:31-35; .../cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:38-40; .../cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:76-83; .../cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:181-201; .../cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:117-129; .../cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:214-223`
- reasoning: Opened each range in the snapshot. Each item is where the spec says: the open-PR race check, listed first, citing #60/#61 (:21-28); the base-is-main check citing #125 (:31-35); the RecipeParser twin check (:38-40); F-### closure against the diff (:76-83); next free F-### taken from main and every open PR (:181-201); bug-report marking that runs only after the deploy is verified live and emails the tester (:117-129); and a report template with Gate: and Fixes: lines (:218, :220).

#### C4 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:165-168; plugins/arch-compliance/python/acf/adr/host.py:30; plugins/arch-compliance/python/acf/repo.py:24`
- reasoning: Recipe A (git grep -n 'Post-merge' over python and hooks) at HEAD 510b862 printed nothing. Second method: a case-insensitive grep -rniE 'post[-_ ]?merge' over the same trees, untracked files included, found only docstring and comment mentions in acf/adr/ledger.py:103,137. I then traced every consumer of ARCH_REL (repo.py:24). acf/adr/host.py:30 only checks that the file exists. hooks/inject_constraints.py:165-168 injects the whole doctrine text, cut off at _ARCH_EXCERPT_MAX=4000 chars, and parses no section. Nothing parses ## Post-merge, so skill prose is its only reader.

#### C5 — SURVIVED
- evidence: `docs/design/POST_MERGE_HOST_STEPS.md:20-22; docs/design/POST_MERGE_HOST_STEPS.md:91-94; docs/design/POST_MERGE_HOST_STEPS.md:225-239`
- reasoning: Every change in §4 is to files in this repository: the skill, the invariant test, ARCHITECTURE.md, plugin.json, pyproject.toml. §0 says no step reads or writes cy: paths. The only cross-repo item is DoD 6 (:237-239), which names the cutovers in the PR body and HM's workstream table. That is bookkeeping, not a dependency. I could not open HM's roadmap row; the deferral does not depend on it.

#### C6 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_skill_invariants.py:117-118; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:117; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:413`
- reasoning: Ran recipe B at 510b862. It printed exactly lines 22, 23, 24, 63, 64, 117, 123, 125, 180, 183, 245, 263, 264, 350, 376, 413, and line 117 is the 'Post-merge CI check' heading. Ran recipe C. It printed only test_adr_skill_invariants.py:117 ('## Post-merge') and :118 ('not declared in ## Post-merge, skipped'), inside test_housekeeping_skill_invariants (:105-133).

### Unanchored findings

- **important**: §4.2 changes only the body of step 4 for a host ### Plan record override. Other portable prose still tells the agent to tick boxes and calls unticked boxes a problem: the step 4 heading, the Rationalizations row, the Red Flags bullet and the frontmatter description. A host with a 'do not tick' rule would still get contradicting instructions, and §3 says those sections are unchanged.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:233; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:387; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:402; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:3`
- **advisory**: §4.1 models every ### Pre-flight check as 'what result stops the run'. Two of the three Cayenne checks the spec cites as motivation do not stop the run. The twin check changes the roadmap wording to 'in flight'. The race check says to add findings to the existing PR rather than open a second one. Neither fits a stop-only shape, so the 'without dropping steps' cutover is not shown for them.
  - evidence: `C:/Users/iball/AppData/Local/Temp/claude/87e26b93c6dabf01/7ee83bd0-9038-461f-98de-0102609a84f5/scratchpad/cy_snapshot/.claude/skills/post-merge-housekeeping/SKILL.md:38-40`
- **advisory**: The spec says this repo's existing declarations are bullets at ARCHITECTURE.md:321-326. Line 321 is the intro sentence; the four bullets are at :323-326, and :328 is the 'No row' line. The citation is slightly imprecise.
  - evidence: `config/architecture/ARCHITECTURE.md:321-328`

### Looked for but did not find

- any Python or hook code that parses a '## Post-merge' heading or its sub-sections (recipe A plus a case-insensitive post[-_ ]?merge grep over python/ and hooks/)
- an existing slot in the portable skill for a host action outside CI/deploy verification, or for extra step-8 report fields
- any test besides test_adr_skill_invariants.py:117-118 that pins '## Post-merge' strings
- a FORBIDDEN entry that the proposed generic sub-section names (### Pre-flight, ### Plan record, ### Host steps, ### Report) would trip (test_adr_skill_prose.py:31-39)

## compliance

### Claim verdicts

#### C7 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:23-24; config/architecture/ARCHITECTURE.md:191-193; docs/design/POST_MERGE_HOST_STEPS.md:129-131`
- reasoning: The mandate's text says 'no default stands in for a missing declaration' (ARCHITECTURE.md:191-193). Its scope is the gate's adr.yml and the review's review.yml, so it covers ## Post-merge only in spirit. The design keeps the skill's existing absent-value pattern ('When ## Post-merge omits a check, report <check>: not declared in ## Post-merge, skipped', SKILL.md:23-24). It extends that pattern to the four sub-sections, at step -1, step 6.7 and step 8 (spec :129-131, :138-139, :144-145), and the skill never invents a host step. Keeping the portable tick rule when ### Plan record is absent is the skill's own behaviour, not a default replacing a host value. The claim holds.

#### C8 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:220-221; plugins/arch-compliance/tests/test_adr_skill_prose.py:14-21; plugins/arch-compliance/tests/test_adr_skill_prose.py:73-79`
- reasoning: The mandate's text is 'Skill prose and runtime messages name no host repository, path or section' (ARCHITECTURE.md:220-221). HOUSEKEEPING/SKILL.md is already in FILES (test_adr_skill_prose.py:14,21), and test_the_prose_names_no_origin_host scans every line against FORBIDDEN (:73-79), so the test needs no change. The examples the spec gives for the new prose ('a gate line and a fixes line', 'only after the deploy declared under post-merge CI is verified live') are generic. Cayenne's name and paths appear only in the spec, never in the planned skill text. The new sub-section headings (### Pre-flight and the rest) belong to the skill's own contract, not to a host section. One caveat: FORBIDDEN holds only HistoricMansions vocabulary, so the test cannot catch Cayenne vocabulary (see the unanchored finding).

#### C9 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:271-275; pyproject.toml:3; plugins/arch-compliance/.claude-plugin/plugin.json:3; scripts/check_installed_skills.py:21`
- reasoning: The mandate says 'A change to a skill's prose bumps the plugin version in plugin.json and pyproject.toml'. It also says the installed copy of post-merge-housekeeping is byte-checked before a gate or housekeeping run (ARCHITECTURE.md:271-275). Both files are at 0.3.2 today (pyproject.toml:3, plugin.json:3), and the spec bumps them to 0.3.3 (spec :167-168, DoD 4). check_installed_skills.py already lists post-merge-housekeeping (:21), so it needs no change, and DoD 5 reinstalls the plugin and byte-checks it after the merge. The claim's 'post-merge byte check' is a fair paraphrase of the mandate's 'before the next run' check.

#### C10 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:283-285; config/architecture/ARCHITECTURE.md:319-321; docs/design/POST_MERGE_HOST_STEPS.md:182-185`
- reasoning: The lifted text asks for 'exactly one canonical implementation that every call site consumes' (ARCHITECTURE.md:283-285). The ## Post-merge section stays the one host declaration 'read by post-merge-housekeeping' (:319-321). The four sub-sections are added inside it, and no second reader or parser is created (spec decision 1, :65-68; :182-185). The design removes the second live procedure (a host's local skill copy) rather than adding one. One tick-rule restatement problem inside the skill is filed separately; it does not create a second host-declaration point.

### Unanchored findings

- **important**: ### Plan record overrides the tick rule only in step 4. The skill also states that rule in its description (SKILL.md:3, 'unticked checkboxes in merged plans'), in the Rationalizations row 'Checkboxes are ceremony ... Tick them.' (:387) and in the Red Flag 'A merged plan with unticked boxes' (:402). The spec's §3/§4.2 scope leaves those three sites unchanged, so a host that declares 'do not tick' gets a skill that tells it to STOP and tick: one rule restated in four places, and the override reaches one.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:387`
- **advisory**: The spec relies on test_adr_skill_prose.py's FORBIDDEN check to keep host vocabulary out of the new prose. But FORBIDDEN lists only HistoricMansions vocabulary, and the motivating host for every new example is Cayenne (F-###, FIX_ROADMAP, Gate:/Fixes: report lines, emailing testers). Cayenne vocabulary leaking into the skill would pass the test unchanged, so for this host the claim is held by review alone.
  - evidence: `plugins/arch-compliance/tests/test_adr_skill_prose.py:31-39`

### Looked for but did not find

- ## Fail loud / ## Soft fail-loud smells: a failed host step 'is reported, and the remaining steps still run' (spec :141-142). That is a report, not a swallow, and no Python changes.
- ## No shims, ## POSIX paths, ## Build artifacts, ## Fail-loud ratchet, ## Façade sinks, ## FSM transitions, ## React boundaries: no code, serialization, detector or UI surface touched (spec §3 'No Python change').
- ## One base exception, ## Declared text decoding, ## Live consumers: no exception class, subprocess call or export is added.
- ## One owner for host paths: the skill already names the doctrine through acf.repo.ARCH_REL (SKILL.md:22), and the design adds no executable snippet that builds a host path.
- ## Host detectors and call sites: no mandate row, detector or call_sites change.
- ## Frozen ledger format: the step-6 LedgerAmendment snippet is unchanged.
- ## No completeness claims: named by the spec. 'Nothing else in the package reads ## Post-merge' is backed by recipes A and B (spec §6); a grep of plugins/arch-compliance outside SKILL.md finds only test_adr_skill_invariants.py:117-118, which matches recipe C.
- ## High-frequency misses: no check re-implemented outside the package (no package code reads ## Post-merge); no stdlib mixin; no subprocess text call; host-name risk covered under C8.
- Registry anchors (ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:50, principle 4): missing_anchors matches stripped doctrine lines (registry.py:220-232), and adding one line inside ## Post-merge moves no anchored heading.
- unstated_mandates is empty: the spec's Governing mandates line names every section I found governing this design.

## sweeper

### Claim verdicts

#### C11 — REFUTED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:62-67, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:123-126, config/architecture/ARCHITECTURE.md:321-326`
- reasoning: The shape exists: the skill reads host values from `## Post-merge` as prose and reports a missing one as 'not declared ... skipped' (SKILL.md:20-24, 62-64, 123-126, 180-184). The doctrine declares them as bullets (ARCHITECTURE.md:321-326). It is the nearest shape. But the generic `### Pre-flight` and `### Host steps` lists cover concerns that existing bullets already handle, so a host now has two ways to declare the same convention. (1) Step 0 already runs a host-declared stop check before mutation: the shared-checkout branch lock or branch guard, 'STOP and ask the user' (SKILL.md:62-67). A pre-flight check such as 'another session is already doing this housekeeping' is the same kind of check: another owner holds this work, so stop. The branch lock itself could also be written as a pre-flight check. The spec gives no rule for which form a host must use, or what happens when both are present. (2) Step 1 already runs 'any post-merge CI or deploy verification declared under ## Post-merge' (SKILL.md:123-126). The spec's own example host-step precondition is 'only after the deploy declared under post-merge CI is verified live' (spec decision 4). A host can put deploy verification in the bullet (run at step 1), in a host step (run at 6.7), or in a host step's precondition, and nothing makes one canonical. The section is still the single place to declare, but within it the extension creates a second channel for these concerns, so 'no second way' does not hold as stated.

#### C12 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:165-166, plugins/arch-compliance/python/acf/registry.py:18-20, plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:83`
- reasoning: I searched by behaviour, not name, across plugins/arch-compliance for: host-declared pre-run checks, host-declared extra steps, host-declared plan-record rules, and host-declared report fields. Terms: pre-?flight, precondition, host step, extra step, call_sites, 'before step', 'declared under', post-merge, housekeeping, ARCH_REL, ARCHITECTURE.md. Findings: inject_constraints.py:165-166 reads the whole doctrine as a context excerpt and parses no section. registry.py:18-20 has call_sites, which route mandates to gates, not workflow steps. The 'delta pre-flight' in responding-to-adversarial-review/SKILL.md:83 is a fixed internal step of the gate, not something a host declares. acf-setup and acf-mandate have no Post-merge or host-step concept, and the profile ARCHITECTURE.md files declare no `## Post-merge`. No other skill, hook or package module gives a host a pre-flight, extra-step or plan-record mechanism. The partial overlaps that do exist are inside the same skill (see C11), outside this claim's 'elsewhere' scope.

#### C13 — REFUTED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:188-192, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:225-228, plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:387`
- reasoning: I re-ran recipe B. The literal 'Post-merge' hits match the spec's list (22-24, 63-64, 117, 123, 125, 180, 183, 245, 263-264, 350, 376, 413). But the recipe searches for the string, not for what a line does. Several lines read `## Post-merge` declarations without the string: 'the host's declared functional data endpoint' (SKILL.md:188-192), 'a host branch guard blocks you here' (:225) and 'If a declared lock is held' (:228). So 'every reading site is listed' is false. The placement half also fails. Step 4 (:233) is not an existing `## Post-merge` reading site, so the Plan record handoff does not 'go next to an existing one'. The new step -1 and the new `## Host sub-sections` section are not next to any listed site. And the portable tick rule that `### Plan record` overrides is also stated at :3 (frontmatter description), :387 (rationalization 'Tick them.') and :402 (red flag 'A merged plan with unticked boxes'). A sweep by behaviour would have found these, and §4.2 does not touch them.

### Unanchored findings

- **important**: `### Plan record` changes only step 4. The tick rule it overrides is restated, unconditionally, in the rationalization table ('Checkboxes are ceremony ... Tick them.'), the Red Flags list ('A merged plan with unticked boxes') and the frontmatter description. So on a host that declares 'do not tick', the skill still tells the agent that unticked boxes are a red flag and must be ticked.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:387`
- **advisory**: `### Pre-flight` partly overlaps step 0's host-declared branch-lock stop gate, and `### Host steps` (and its preconditions) partly overlaps step 1's declared post-merge CI or deploy verification. The spec gives no rule for which form a host uses, or how the skill acts when both declare the same concern.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:62-67`
- **advisory**: Decision 2 says every absent sub-section is reported as '<sub-section>: not declared in ## Post-merge, skipped'. But §4.2 gives step 4 no absent-value report for `### Plan record`, and §4.3 pins no 'plan record: not declared' string. So one of the four sub-sections has no declared-never-defaulted report.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:233-236`
- **advisory**: The spec extends the approved list of exactly four `## Post-merge` conventions and makes the approved tick rule overridable. Both come from decision 1 of the governing approved spec (POST_MERGE_HOUSEKEEPING_SKILL.md), which this spec never names or amends.
  - evidence: `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:36-41`

### Looked for but did not find

- A host-declared pre-run or stop check in other skills, hooks or the package: grep pre-?flight|precondition|before step|declared under across plugins/arch-compliance
- A host-declared extra workflow step: grep 'host step|extra step|call_sites' (call_sites only routes mandates)
- Python readers of the `## Post-merge` section: grep Post-merge, ARCH_REL and ARCHITECTURE.md in *.py (inject_constraints reads the whole document only)
- acf-setup or the profiles scaffolding a `## Post-merge` section: grep post-merge|housekeeping in skills/acf-setup and profiles (none)
- An earlier rejection of a host-extensible housekeeping procedure: grep 'host steps|pre-flight|plan record|local copy|tick rule' in docs/ excluding docs/reviews (none found; only POST_MERGE_HOUSEKEEPING_SKILL.md decision 1's list of four conventions)

### Relationships

- PARTIAL_OVERLAP: `### Pre-flight sub-section and step -1` — responsibility `stop the run on a host-declared condition before mutating shared state` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:62-67`
  - resolution: Shared responsibility R: a host-declared 'another owner holds this work, stop' gate. Make `### Pre-flight` the single container for host stop checks and treat the branch-lock bullet as one standard pre-flight check (or state that the branch lock must stay a bullet and pre-flight must not restate it). Step 0's lock inspection then consumes the same list.
- PARTIAL_OVERLAP: `### Host steps (step 6.7) with preconditions` — responsibility `verify a declared deploy or post-merge CI result` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:123-126`
  - resolution: Shared responsibility R: deploy verification. A host-step precondition about a deploy should cite step 1's recorded result of the declared post-merge CI/deploy check rather than re-verify it. State that host steps may not declare a deploy verification of their own.
- BOUNDARY_CUT: `### Plan record sub-section` — responsibility `decide how a merged plan's completion is recorded` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:235-236`
  - resolution: The override takes over step 4's rule but leaves restatements at :3, :387 and :402 asserting the portable rule. Make step 4 the only statement of the plan-record rule, and make the rationalization, red flag and description refer to 'the plan-record rule (step 4)'.
- ADJACENT: `### Report sub-section` — responsibility `list the fields of the step-8 report` — existing `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:374-377`
  - resolution: None; it appends to step 8's existing report.
  - non-merge: Step 8 owns the report and `### Report` only adds declared fields to it. Nothing else declares report fields, so there is no second owner.
- ADJACENT: `Doctrine reading of `## Post-merge` sub-sections` — responsibility `read the host doctrine` — existing `plugins/arch-compliance/hooks/inject_constraints.py:165-166`
  - resolution: None.
  - non-merge: The hook injects the whole doctrine, truncated, as session context and parses no section. The skill's prose reading of `## Post-merge` is a different job.

### Two-owner counts

- host-declared stop-before-mutation check (step 0 branch lock + ### Pre-flight): 2
- declared deploy/post-merge CI verification (step 1 + ### Host steps precondition): 2
- statement of the plan-record tick rule (SKILL.md:3, :235, :387, :402): 4

### Document conflicts

- `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:36` (restates): Host-specific operational conventions are read from a named `## Post-merge` section in the host's doctrine ... 1. Shared-checkout branch lock ... 2. Worktree daemon probe ... 3. Post-merge CI / deploy workflows ... 4. Durable tracking target
- `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:129` (contradicts): If the branch executed a tracked implementation plan, tick completed steps `[x]`, annotate the merge (PR #, squash SHA, date)

## hardening

### Claim verdicts

#### C14 — SURVIVED
- evidence: `docs/design/POST_MERGE_HOST_STEPS.md:55-57; docs/design/POST_MERGE_HOST_STEPS.md:182-185; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:235-236; cy:.claude/skills/post-merge-housekeeping/SKILL.md:65`
- reasoning: The claim's spec_citation (SKILL.md:233-239) is step 4's tick rule. That shows the portable behaviour the override replaces, not a justification. The written justification is in the spec. §1:55-57 rejects host-local copies because they leave two live copies or a cutover that drops steps. §5:182-185 says a host keeping its own procedure has two live procedures, and that covers 'point to a host procedure the skill runs in full', because such a procedure would replace the portable steps. I confirmed the gap is real. The portable step 4 says 'tick every completed step [x]' (SKILL.md:235-236). The live host rule is 'Do not tick the checkboxes' (cy:...SKILL.md:65). The current section offers no override hook: ARCHITECTURE.md:321-326 has only the four bullet declarations. The design extends an existing declaration point. It adds no recovery layer.

#### C15 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:39-42; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:338; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:367`
- reasoning: SKILL.md:39-42 keeps 'everything from step 3.5 onward' in the main session, sequential, with no subagents in flight. Step 6.5 starts at :338 and step 7 at :367, with no intervening step. A new 6.7 placed there is after 3.5, so the existing rule already covers it. The only subagent dispatch the skill allows is pre-checkout reads, collected before step 3.5 (:36-38), so none can be in flight at 6.7. The checkout is already held from step 3.5 (:213-221), so host steps that edit tracked docs have the checkout they need.

#### C16 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:28-29; plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:54-55; cy:.claude/skills/post-merge-housekeeping/SKILL.md:21`
- reasoning: Steps 1-2 are read-only and must not move the main checkout's HEAD (:28-29). Step 0's shared-checkout gate applies only 'before the first command that moves or commits to the main checkout — i.e. before step 3.5' (:54-55). So a read before step 1 does not touch the gate. The motivating checks are reads: listing open PRs (cy:21-28), the PR's baseRefName (cy:31) and a twin PR's merge state. Caveat (see unanchored findings): a base-branch check needs $default_branch, which the portable skill resolves only in step 1 (:80-87), and the cy base check's remedy is a mutating cherry-pick (cy:34-35).

#### C17 — SURVIVED
- evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:123-126; cy:.claude/skills/post-merge-housekeeping/SKILL.md:117-118`
- reasoning: Step 1 already runs 'any post-merge CI or deploy verification declared under ## Post-merge' (:123-124) in the same main-session run, before step 6.7. So the deploy-verified fact is produced earlier in the run, and the agent can read it, or re-run it, when it checks a host step's precondition. The motivating host step names exactly this precondition: 'only after the deploy is verified live' (cy:117-118). Refusing on an unmet precondition is a rung-3 refusal, not a repair. The skill has no structured record of step 1's result, only session context. That is consistent with Decision 1 (prose, not a parser), and the check stays implementable.

#### C18 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_skill_invariants.py:113-125; plugins/arch-compliance/tests/test_adr_skill_prose.py:31-39`
- reasoning: test_housekeeping_skill_invariants iterates a literal tuple of required substrings (:113-124) and asserts each one is in the body (:125). Adding seven string literals there is enough to pin them. The prose test scans HOUSEKEEPING/SKILL.md line by line against FORBIDDEN (:21, :73-79). None of the seven new strings contains any FORBIDDEN literal (:31-39), so the prose test needs no change. git grep at 510b862 shows the only test pins on 'Post-merge' are invariants.py:117-118, as recipe C states.

### Unanchored findings

- **advisory**: A pre-flight check runs before step 1, but a base-branch check (the cy example) needs $default_branch, which only step 1 resolves (with its own 'never guess main' STOP). The spec does not say whether pre-flight may use step 1's resolution or must resolve its own.
  - evidence: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:80-87`
- **advisory**: The pre-flight model is 'stop condition holds -> run ends, check says what to do'. One motivating check's remedy is a mutating action that continues the housekeeping (cherry-pick onto main in a new PR and record both numbers). The spec does not say whether the portable run resumes afterwards, or that the read-only claim (Risk row 2) covers only the check, not its remedy.
  - evidence: `cy:.claude/skills/post-merge-housekeeping/SKILL.md:34`
- **advisory**: Step 6.7 says a failed host step is reported and the remaining host steps still run. Host steps can depend on one another, for example taking the next free ID before filing items under it, and the design gives no way to declare that dependency. A later step can then run on a failed earlier step's missing output, a silent-continuation path.
  - evidence: `cy:.claude/skills/post-merge-housekeeping/SKILL.md:181`

### Looked for but did not find

- Any Python reader of ## Post-merge in plugins/arch-compliance/python or hooks (git grep 'Post-merge' returns nothing; the only post-merge hits are comments in acf/adr/ledger.py:103,137), so no loader or validator is needed or bypassed
- Test pins on 'Post-merge' other than test_adr_skill_invariants.py:117-118
- Any FORBIDDEN literal in the seven new pinned strings
- A repair-on-load, normalizer or fallback among the added mechanisms: absent sub-sections are reported as 'not declared ... skipped', never defaulted

### Mechanism traces

- **### Pre-flight checks (step -1 stop gate)**
  - invalid state: An open housekeeping PR already exists for the same merge, OR the merged PR's baseRefName != the default branch, OR a declared cross-repo twin PR is unmerged
  - producer: `cy:.claude/skills/post-merge-housekeeping/SKILL.md:21`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: The producer is outside this plugin: concurrent sessions and forge retargeting. The spec makes the check a declared stop at the start of the run, so the run never acts on that state: 'the first whose stop condition holds ends the run' (§4.1, Decision 3).
  - spec citation: `docs/design/POST_MERGE_HOST_STEPS.md:129-134`
- **Host-step precondition check (precondition unmet, not run)**
  - invalid state: A side-effecting host step whose declared precondition (e.g. deploy verified live) is false when the step is reached
  - producer: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:123-126`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: Deploy lag is external. The skill refuses rather than runs around it, and a host that omits a precondition 'owns that choice in its doctrine' (§8 Risks row 3).
  - spec citation: `docs/design/POST_MERGE_HOST_STEPS.md:79-82`
- **### Plan record override of step 4's tick rule**
  - invalid state: A merged plan whose checkboxes are ticked [x] although rulings amended those steps during execution, asserting an unverified history
  - producer: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:235-236`
  - rung 2 (highest applicable 2); repairs=False
  - hardening rejected because: Hardening is the design itself: the writer (step 4) applies the host's declared rule in place of the tick rule, at the single write point.
  - spec citation: `docs/design/POST_MERGE_HOST_STEPS.md:135-137`

## Claims

- **C1** [premise] [load-bearing]: The portable skill reads exactly four named host conventions (branch lock, worktree daemon probe, post-merge CI workflows, durable tracking target) plus step 5's non-Markdown tracking files from ## Post-merge, and has no slot for a host pre-flight check, a host plan-record override, a host step or host report fields.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:20-24`
- **C2** [premise] [load-bearing]: Step 4 of the portable skill instructs ticking every completed plan step [x] plus a merge annotation, and Cayenne's local copy instructs the opposite (do not tick checkboxes; a status header carries the truth).
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:235-236`
- **C3** [premise] [load-bearing]: Cayenne's local housekeeping skill contains a first-step open-PR race check (#60/#61), a base-is-main check (#125), a cross-repo twin check, F-### closure against the diff, cross-PR F-### allocation, deploy-gated bug-report marking that emails testers, and a report with Gate:/Fixes: fields. (cy: maps to a snapshot of Cayenne at fffc2954.)
  - spec citation: `cy:.claude/skills/post-merge-housekeeping/SKILL.md:21-28`
- **C4** [premise] [load-bearing]: No Python code in the package or hooks reads the doctrine's ## Post-merge section (recipe A: git grep -n 'Post-merge' -- plugins/arch-compliance/python plugins/arch-compliance/hooks prints nothing); the skill prose is the only reader. Run the recipe and a second method.
  - spec citation: `plugins/arch-compliance/python/acf/repo.py`
- **C5** [premise]: Deferral: Cayenne's and HistoricMansions' cutovers are out of scope here and become adoption plans once this release ships; nothing in this design depends on them.
  - spec citation: `cy:.claude/skills/post-merge-housekeeping/SKILL.md`
- **C6** [premise]: Recipe B (git grep -n 'Post-merge' on the skill) prints lines 22, 23, 24, 63, 64, 117, 123, 125, 180, 183, 245, 263, 264, 350, 376, 413, and recipe C finds the only test pins at test_adr_skill_invariants.py:117-118.
  - spec citation: `plugins/arch-compliance/tests/test_adr_skill_invariants.py:117-118`
- **C7** [mandate] [load-bearing]: An absent sub-section is reported as '<sub-section>: not declared in ## Post-merge, skipped' and never defaulted, complying with ## Declared, never defaulted.
  - spec citation: `config/architecture/ARCHITECTURE.md:189-216`
- **C8** [mandate]: The new skill prose names no host repository, path or section, complying with ## Prose names no host and passing test_adr_skill_prose.py's FORBIDDEN check without changes.
  - spec citation: `config/architecture/ARCHITECTURE.md:218-228`
- **C9** [mandate]: Changing the skill prose requires bumping the plugin version in plugin.json and pyproject.toml (0.3.2 to 0.3.3) and a post-merge installed-skills byte check, per ## Release discipline.
  - spec citation: `config/architecture/ARCHITECTURE.md:269-279`
- **C10** [mandate]: The design keeps a single point of definition: one place a host declares post-merge conventions (## Post-merge) and one skill that reads it.
  - spec citation: `config/architecture/ARCHITECTURE.md:281-298`
- **C11** [shape_fit] [load-bearing]: The four sub-sections extend the existing ## Post-merge host-declaration shape (read as prose by the skill, absent value reported as not declared ... skipped) and create no second way for a host to declare post-merge conventions.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:20-24`
- **C12** [shape_fit] [load-bearing]: Nowhere else in the plugin (other skills, hooks, package, acf-setup) already provides a host-declared pre-flight, extra-step or plan-record mechanism that these sub-sections would partially duplicate.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md`
- **C13** [sweep]: Every reading site of ## Post-merge in the skill is listed by recipe B, and each new reading site goes next to an existing one (overview, step 4, after 6.5, step 8), never in a new file.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:350`
- **C14** [mechanism_justification] [load-bearing]: Adding host-declared pre-flight checks, a plan-record override, host steps and report fields to the portable skill is justified over the alternatives (hosts keep local skills; or ## Post-merge points to a host procedure the skill runs in full).
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:233-239`
- **C15** [implementability] [load-bearing]: Host steps can run after step 6.5 and before step 7 in the main session with no subagents in flight, consistent with the skill's existing rule that teardown and everything from step 3.5 onward stay in the main session.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:38-42`
- **C16** [implementability] [load-bearing]: Pre-flight checks can run before step 0 as reads that never touch the main checkout, consistent with the skill's read-only steps 1-2 and step 0's shared-checkout rule.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:44-72`
- **C17** [implementability] [load-bearing]: A host step's declared precondition (e.g. deploy verified live) can be checked by the agent from what earlier steps produced (step 1's post-merge CI and deploy verification), so an unmet precondition is recorded as not run rather than run around.
  - spec citation: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md:117-126`
- **C18** [implementability]: test_housekeeping_skill_invariants can pin the seven new strings by adding them to its existing required tuple; the prose test needs no change.
  - spec citation: `plugins/arch-compliance/tests/test_adr_skill_invariants.py:105-133`
