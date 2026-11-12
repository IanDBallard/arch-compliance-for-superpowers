# Adversarial design review — full detail

Spec: `docs/design/ARCHITECTURE_REVIEW_PORT.md` @ `f1511be7e5caea7b3a6b85ab5fe2859d06ab2ad2`
Kinds: feature
Outcome: **BLOCKED**
Claims: 60 · Reviewers: 4 · Converged: 2

## Blocking reasons

- load-bearing claim C10 (premise) is SURVIVED but its evidence ('hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:360') merely restates the spec's own citation ('hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:360') — not independent verification, treated as UNPROVEN
- load-bearing claim C21 (premise) is REFUTED: The --update-baseline mode exists (:493) and regenerates the baseline (:504-510). The claim that the only growth is languages and params is false, though. compare_lanes scores growth as current keys minus baseline keys per lane (:379-380), with no rename handling. MandateEntry.gemini_anchor is in the test_only lane (it starts at :151, the entry is at :195) because only tests read it (test_mandate_registry_drift.py:62). After the rename, MandateEntry.arch_anchor is a new test_only key and the ratchet reports it as growth too, so growth is three fields. This is a precision defect: §5.4's row already names the rename, but the claim and the PR's 'states that growth' should list arch_anchor as growth as well. I did not run the ratchet, so I cannot rule out other growth.
- load-bearing claim C23 (mandate) is REFUTED: `## Declared, never defaulted` allows a built-in default only when the section records it, as it does for the ratchet, resolve_repo and the judge's defaults (:193-202). The claim says the extension records 'the three built-in meanings' (built-in exclusion list, absent surface, empty subsystems; spec :136). The design has at least one more host-facing built-in meaning that is not recorded: a fixed test-path pattern list (`tests/`, `test_*.py`, `*_test.py`, `**/*.test.*`, `**/*.spec.*`). Step 2 explicitly separates it from 'the built-in exclusions' (:163), it applies again in step 3 (:164), and a host cannot declare it (review.yml has only `exclude`). The empty-list meanings of the optional RuleSettings keys (`surface_exclude`, `docs`, `exception_base` absent on row §3 but present on §3-exception-base, §5.2) are not recorded either. The required-field and missing-file half of the claim holds (§4.4, :124, :136). The 'three meanings' enumeration does not match the design.
- load-bearing claim C30 (mandate) is UNPROVEN: The auditor half holds: a contract violation marks the group FAILED, keeps the raw payload and makes the exit non-zero (:167). `## Fail loud` (:28-32) says failures must not disappear. run_git returns any non-zero status as data with check=False (diff.py:24-30). The spec maps 'a non-zero rev-list status' to 'commit not in history' (:168). So every other rev-list failure would be reported as a modeled warning that never changes the exit status: not a repository, unborn HEAD, safe.directory 'dubious ownership' refusal, a malformed commit field. A missing git binary raises (subprocess FileNotFoundError), so the narrow 'never folding missing git into not-in-history' statement is true. The design does not show that other git failures stay loud, and blame's 'unresolved' class (:168) has the same open question.
- load-bearing claim C41 (shape_fit) is UNPROVEN: The key names match: the facade detector reads target_literal_re and allowlist_globs (facade_sinks.py:35-36, mandates.yml:113-114), and the FSM detector reads state_field and validator_name (mandates.yml:129-130). The consequence 'a fact both need is declared once' holds only when the auditor sits on the built-in detector's own row. _check_builtin requires that row's id to equal the detector's fixed mandate id (registry.py:207-211; ARCHITECTURE.md:84-85), so a repository has at most one such row per detector. The spec's only concrete instance, origin §5.2, puts target_literal_re and allowlist_globs on two non-detector rows (§11, §11-inventory), which repeats the same fact in each. The mechanism that would make 'declared once' true is never shown.
- mandate claim C23 is REFUTED: `## Declared, never defaulted` allows a built-in default only when the section records it, as it does for the ratchet, resolve_repo and the judge's defaults (:193-202). The claim says the extension records 'the three built-in meanings' (built-in exclusion list, absent surface, empty subsystems; spec :136). The design has at least one more host-facing built-in meaning that is not recorded: a fixed test-path pattern list (`tests/`, `test_*.py`, `*_test.py`, `**/*.test.*`, `**/*.spec.*`). Step 2 explicitly separates it from 'the built-in exclusions' (:163), it applies again in step 3 (:164), and a host cannot declare it (review.yml has only `exclude`). The empty-list meanings of the optional RuleSettings keys (`surface_exclude`, `docs`, `exception_base` absent on row §3 but present on §3-exception-base, §5.2) are not recorded either. The required-field and missing-file half of the claim holds (§4.4, :124, :136). The 'three meanings' enumeration does not match the design.

## Absorptions

- PARTIAL_OVERLAP: 'acf.review.contract.AuditorFinding.severity' shares responsibility "classify an agent-produced finding's severity" with plugins/arch-compliance/python/acf/adr/contract.py:38 — Shared R: severity of a read-only agent's finding. Either reuse acf.adr.contract.Severity (mapping nit/suggestion to advisory) or state in writing why the review needs four levels where the ADR gate uses three.
- PARTIAL_OVERLAP: 'acf.repo.RepoTree.files plus the built-in exclusions of §4.7 step 2' shares responsibility 'enumerate repository files by glob minus default vendor/test exclusions' with plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:57-68 — Shared R: glob enumeration with exclusions. RepoTree.files becomes the single enumerator, the ratchet consumes it, and one default test-path set lives beside it. Otherwise the fnmatch-versus-Path.glob difference is recorded as debt.
- PARTIAL_OVERLAP: 'pack `files` globs' shares responsibility 'map file paths to a technology' with plugins/arch-compliance/hooks/posttooluse_gate.py:50 — Shared R: file-to-technology routing. Part two's single map must absorb the hook's _CODE_SUFFIXES as well as cli_check_diff.py:152/188, so §10 should name it.
- PARTIAL_OVERLAP: 'acf.registry.anchor_line' shares responsibility 'decide whether an anchor resolves in the doctrine' with plugins/arch-compliance/skills/acf-setup/SKILL.md:137-139 — The acf-setup step consumes missing_anchors/anchor_line instead of a by-eye check, and its 'literal substring' prose is reworded to line equality.
- IDENTICAL: 'ts-js pack ui-logic-isolation hints' shares responsibility 'flag UI-logic candidate lines by regex' with hm:scripts/core/architecture_review/ui_logic_prepass.py:31-52 — Named duplicate until part two moves the gate's staged check onto acf.review.prepass (spec §8, §10)

## Converged findings

- [3 reviewers: hardening, sweeper, compliance] File-glob and exclusion semantics are underspecified: RepoTree.files is defined by pathlib.Path.glob, which anchors the built-in exclusions (tests/, test_*.py, __pycache__/) at the root, and differs from the fnmatch dialect the facade detector and ratchet use for keys the rules now share.
  - evidence: `docs/design/ARCHITECTURE_REVIEW_PORT.md:163`
  - evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:57-68`
  - evidence: `plugins/arch-compliance/python/acf/detectors/facade_sinks.py:59`
- [2 reviewers: compliance, hardening] Staleness maps every non-zero rev-list status from run_git to 'commit not in history', folding other git failures into a report-only warning.
  - evidence: `plugins/arch-compliance/python/acf/diff.py:24-30`
  - evidence: `docs/design/ARCHITECTURE_REVIEW_PORT.md:168`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/skills/architecture-review/SKILL.md:72; plugins/arch-compliance/skills/architecture-review/SKILL.md:35-38; plugins/arch-compliance/skills/architecture-review/auditors/ (four files: fail-loud.md, no-shims.md, posix-paths.md, react-boundaries.md)`
- reasoning: SKILL.md:72 reads 'Default auditors (v1): fail-loud, no-shims, posix-paths, react-boundaries'. SKILL.md:35-38 lists the same four prompt files, and the auditors/ directory holds exactly those four files.

#### C2 — SURVIVED
- evidence: `hm:.claude/skills/architecture-review/SKILL.md:35-49 (rubric step), :53-61 (frontend and family-templates surfaces), :75-88 (nine auditors, pre-pass), :123-145 (blame provenance); git ls-tree b2611977f .claude/skills/architecture-review/auditors/ lists nine .md prompts`
- reasoning: At b2611977f the origin SKILL.md has a rubric extraction step (step 1), separate per-auditor surfaces (the Python, frontend and family-templates trees), the ui_logic_prepass candidate scan before dispatch, and step 6b, which classifies blame provenance. The auditors directory holds nine prompt files.

#### C3 — SURVIVED
- evidence: `hm:.claude/skills/architecture-review/auditors/metadata-facade.md:3; hm:.claude/skills/architecture-review/auditors/output-agnosticism.md:12-25; hm:.claude/skills/architecture-review/auditors/three-tier-hfsm.md:11-13`
- reasoning: metadata-facade.md:3 hard-codes ContentMetadataService and index.yml. output-agnosticism.md:12-25 lists the origin stage file paths. three-tier-hfsm.md:11-13 also hard-codes origin tier paths and engine.DEFAULT_BATCH_TIER_PATHS.

#### C4 — SURVIVED
- evidence: `hm:scripts/core/architecture/registry.py:21-34; hm:scripts/core/architecture/registry.py:79; plugins/arch-compliance/python/acf/registry.py:50-62`
- reasoning: The origin MandateEntry declares model_config extra='forbid' (:22) and gemini_anchor (:33), and has no languages, params or arch_anchor field. load_mandates validates every row through it (:79), so plugin fields would be refused. The plugin's Mandate requires languages and arch_anchor (registry.py:55,59), so the origin file must change before the plugin can read it.

#### C5 — SURVIVED
- evidence: `hm:scripts/core/architecture_review/baseline.py:62-69; hm:docs/architecture/compliance_baseline.json:7; hm:.claude/skills/architecture-review/auditors/three-tier-hfsm.md:47`
- reasoning: aggregate keys counts on result.mandate (baseline.py:67), and that value is the auditor's free-text label ('Three-Tier/HFSM' in the output contract at three-tier-hfsm.md:47; the baseline JSON holds labels such as 'Three-Tier/HFSM' and '§3 Fail-Loud'). yaml.safe_load over the origin registry shows auditor three-tier-hfsm on six rows: three-tier, three-tier-batch, three-tier-ambient, §5, §5-fsm-mechanism and path-provenance. Those counts cannot be split per mandate id.

#### C6 — SURVIVED
- evidence: `hm:config/architecture/mandates.yml:10, :21, :32 (first auditor rows); recipe yaml.safe_load over git show b2611977f:config/architecture/mandates.yml returned 25 rows with a non-null auditor`
- reasoning: I ran the recipe. It printed 25 ids, and each id and origin auditor value matches a §5.2 row: §3 and §3-exception-base fail-loud; §4 and §4-mansion-slug-wire no-shims; three §10 rows posix-paths; three three-tier rows, §5, §5-fsm-mechanism and path-provenance three-tier-hfsm; §11 and §11-inventory metadata-facade; four §12 rows output-agnosticism; §13 schema-presentation; §6 and the two admin rows ui-logic-isolation; §14 and §14-size class-cohesion.

#### C7 — SURVIVED
- evidence: `hm:.claude/skills/architecture-review/SKILL.md:154; hm:.cursor/skills/architecture-review/SKILL.md:154; hm:scripts/core/architecture_review/_e2e_helper.py:261`
- reasoning: git grep _last_run at b2611977f outside docs hits only the two SKILL.md copies, and both are the writer at :154 (the .cursor twin is a second copy of that writer, not a reader). Searching build/architecture_review and golden-summary turns up _e2e_helper.py, which writes its own golden snapshot (:261) and never reads the sidecar. The only readers are historical plan docs under docs/.

#### C8 — SURVIVED
- evidence: `hm:scripts/ci/check_arch_compliance_llm.py:45-55; hm:scripts/ci/check_arch_compliance_llm.py:87-95; hm:scripts/ci/arch_compliance/llm_judge.py:88-98; hm:scripts/ci/arch_compliance/llm_judge.py:293; hm:scripts/ci/arch_compliance/judge_calibration.py:61-62`
- reasoning: _mandate_ids_for_path returns only §5 or §6. The CLI looks up by_id and passes the mandate object, so judge_changed_file has mandate.id at :293, and also uses it at :304. load_rubric opens <auditor>.md by name in a directory. judge_calibration hard-codes the names 'three-tier-hfsm' and 'ui-logic-isolation' and passes them to load_rubric. The unit tests that monkeypatch load_rubric (test_arch_llm_judge.py:158) keep the same signature.

#### C9 — SURVIVED
- evidence: `recipe git grep -l -E "^(from|import) acf" b2611977f -- scripts tests exited 1 with no output; a whole-tree variant hits only hm:docs/design/ADR_GATE_HOST_CONTRACT.md and an adr_runs doc; hm:scripts/ci/check_arch_compliance_llm.py:89`
- reasoning: I reproduced the recipe and it prints nothing. No origin code imports acf, and none of the cutover edits in §5.4 adds such an import. The origin CLI still only needs auditor to be non-null (:89), which stays true because the values become rule ids.

#### C10 — SURVIVED
- evidence: `hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:360`
- reasoning: Line 360 is the 1d Cursor/Cline follow-up, and it names only arch-compliance:adversarial-design-review and arch-compliance:responding-to-adversarial-review. architecture-review is not covered, so it needs a new row.

#### C11 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:19; plugins/arch-compliance/python/acf/judge.py:260`
- reasoning: The judge's only prompt-file read is _PROMPT_TEMPLATE, which is judge_prompt.md (:19), read at :260. git grep 'auditor' under plugins/arch-compliance/python finds nothing in judge.py. llm_react_boundaries is a prompt id in LLM_PROMPT_IDS (:31), not an auditor file path.

#### C12 — SURVIVED
- evidence: `cy:cayenne-web/src/lib/features/bugReport/BugReportSheetBody.svelte:1; cy:cayenne-web/src/lib/features/bugReport/BugReportSheetBody.svelte:36-43`
- reasoning: The runes ($state( at :36-39, $derived( at :41-43) sit as plain text in the <script lang="ts"> block (:1) of the raw .svelte file. A line regex over the file text matches them without extracting the script block, and auditors get Read/Grep (§4.7 step 5). See the advisory below about the cited example being view state.

#### C13 — SURVIVED
- evidence: `hm:config/architecture/ARCHITECTURE.md:8-9; hm:.claude/skills/architecture-review/rubric/arch-docs-manifest.yml:4-5`
- reasoning: The pointer's step 3 names .claude/skills/architecture-review/rubric/arch-docs-manifest.yml, which is inside the skill tree that gets deleted. The manifest's own header (:4-5) says the ADR compliance reviewer reads it through ARCHITECTURE.md. It therefore has a live reader and has to move, with the pointer updated.

#### C14 — SURVIVED
- evidence: `hm:GEMINI.md:100, :108, :114, :120, :127, :139, :171, :181, :206, :221, :251, :270; plugins/arch-compliance/python/acf/registry.py:220-223; hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:352`
- reasoning: The set of gemini_anchor values over the origin registry has 12 distinct entries (§3 to §14), and each one equals a '## ' heading line of GEMINI.md at the lines listed. missing_anchors tests whether the stripped anchor is in the set of stripped doctrine lines, so adding those 12 headings verbatim to the pointer resolves every row. :352 contains the quoted 'met only vacuously' sentence.

#### C15 — SURVIVED
- evidence: `hm:scripts/builders/fsm_base.py:14, :54, :56-67, :69-79, :93-96, :43`
- reasoning: DeclaredFSM (:14) has transition (:56) and transition_to (:69), and both delegate to _apply (:67, :79). _apply is the only post-construction writer of current_state (:95), and the comment at :54 says so. __init__ also assigns the initial state (:43), which is construction, not a transition.

#### C16 — SURVIVED
- evidence: `config/architecture/mandates.yml:51; plugins/arch-compliance/profiles/react-app/mandates.yml:46; config/architecture/mandates.yml:142; plugins/arch-compliance/profiles/python-service/mandates.yml:101`
- reasoning: git grep 'auditor:' outside docs gives four rows: the two react-boundaries rows that §4.10 changes and the two fail-loud rows. git grep for 'auditors/' and 'auditors' under plugins, scripts, config and README finds the auditors directory named only in the SKILL.md that gets rewritten (:35-38, :98). No test, script or Python module reads an auditor file (judge.py reads only judge_prompt.md).

#### C17 — SURVIVED
- evidence: `recipe A re-run at b2611977f; hits outside the deleted trees: hm:config/architecture/ARCHITECTURE.md:9, hm:config/architecture/coverage_map.yml:111, hm:scripts/ci/arch_compliance/engine.py:816, hm:scripts/ci/check_ui_prepass_staged.py:17, hm:scripts/setup_git_hooks.py:138, hm:tests/test_mandate_registry_drift.py:84, hm:scripts/schemas/types.py:9 and the rest listed in §5.4`
- reasoning: I re-ran recipes A, B and C. Every non-docs hit outside the deleted trees maps to a §5.4 row: the three scripts/ci importers, llm_judge, the fixtures, coverage_map, mandates.yml:516, types.py:9, the dead_code and debt baselines, setup_git_hooks, test_push_scope_hook, the engine mirror and the test files. Extra searches found no other live reader: arch-docs-manifest (only the pointer), compliance_baseline (only the deleted skill and staleness module), deleted test names in config/CI, '.cursor/skills' outside the deleted tree (none), and pyproject or pre-commit config. Minor imprecisions are reported as unanchored findings and do not change any disposition.

#### C18 — SURVIVED
- evidence: `hm:scripts/core/exceptions.py:1227, :1241-1280, :1380, :1452, :1456; hm:scripts/ci/arch_compliance/engine.py:815-843; hm:scripts/ci/baseline_staleness.py:32, :88`
- reasoning: Recipe C plus SkillLayoutError and BaselineStalenessError: the raisers, importers and tests are scripts/core/architecture_review/*, skill_install.py, baseline_staleness.py (:32, :88), and test_arch_baseline, test_arch_facets, test_arch_review_aggregator, test_arch_review_contract, test_arch_review_rubric, test_baseline_staleness and test_skill_install. All of these are deleted under §5.4. Apart from those, the names appear only in the engine name mirror and in one docstring (exceptions.py:1525, see findings). No remaining class subclasses a deleted class.

#### C19 — SURVIVED
- evidence: `hm:scripts/setup_git_hooks.py:137-138; hm:tests/test_push_scope_hook.py:21, :25-26; git grep -i staleness outside docs`
- reasoning: Outside its own module and test, the staleness checker is invoked only by the generated pre-push line at setup_git_hooks.py:138, and that line is asserted only at test_push_scope_hook.py:21 and :25-26. The other staleness hits in the tree are unrelated (Zotero, locks, image freshness). The comment at :137 and already-installed hooks are left over; see findings.

#### C20 — SURVIVED
- evidence: `hm:scripts/core/architecture_review/__init__.py:10; git ls-tree -d --name-only b2611977f .cursor/skills/ prints only .cursor/skills/architecture-review`
- reasoning: git grep skill_install over scripts, tests, .claude and .cursor finds the package import at __init__.py:10, its own test and SKILL.md prose. .claude/skills holds architecture-review and post-merge-housekeeping, and .cursor/skills holds only architecture-review, so no other dual-installed skill depends on the helper.

#### C21 — REFUTED
- evidence: `hm:scripts/ci/dead_code_ratchet.py:493; hm:scripts/ci/dead_code_ratchet.py:377-380; hm:config/architecture/dead_code_baseline.json:151, :195; hm:tests/test_mandate_registry_drift.py:62`
- reasoning: The --update-baseline mode exists (:493) and regenerates the baseline (:504-510). The claim that the only growth is languages and params is false, though. compare_lanes scores growth as current keys minus baseline keys per lane (:379-380), with no rename handling. MandateEntry.gemini_anchor is in the test_only lane (it starts at :151, the entry is at :195) because only tests read it (test_mandate_registry_drift.py:62). After the rename, MandateEntry.arch_anchor is a new test_only key and the ratchet reports it as growth too, so growth is three fields. This is a precision defect: §5.4's row already names the rename, but the claim and the PR's 'states that growth' should list arch_anchor as growth as well. I did not run the ratchet, so I cannot rule out other growth.

### Unanchored findings

- **advisory**: The svelte pack's cited example of 'runes computing domain values' is view state: the file marks lines 35-41 'View state only', so the proposed `$state(`/`$derived(`/`$effect(` hints will flag every rune and seed mostly false candidates.
  - evidence: `cy:cayenne-web/src/lib/features/bugReport/BugReportSheetBody.svelte:35`
- **advisory**: A manifest-listed origin doctrine document, which auditors now read through ARCH_REL, still says path-provenance is enforced by the `three-tier-hfsm` auditor; the cutover renames that to the path-provenance rule, and recipe A excludes docs/ so no §5.4 row covers it (likewise docs/architecture/ARCH_COMPLIANCE_FRAMEWORK_OVERVIEW.md:50,86 describe the deleted 8-auditor skill).
  - evidence: `hm:docs/architecture/CONFIG_AFFILIATION_AND_OVERRIDES.md:141`
- **advisory**: The §5.4 dead_code_baseline row lists lines 44-46,195-201,265 under recipes A and B, but the baseline also holds entries for three deleted exception classes, matched only by recipe C, at lines 237, 239 and 240; regeneration removes them, but the site list is incomplete.
  - evidence: `hm:config/architecture/dead_code_baseline.json:237`
- **advisory**: Removing setup_git_hooks.py:138 leaves its comment at :137 orphaned, and developer clones' already-generated .git/hooks/pre-push keeps calling the deleted module (harmless only because of `|| true`); the spec does not say to regenerate hooks.
  - evidence: `hm:scripts/setup_git_hooks.py:137`
- **advisory**: A surviving docstring names the deleted BaselineError and its 'one handler' (the deleted baseline_staleness); §5.4 does not edit it.
  - evidence: `hm:scripts/core/exceptions.py:1525`
- **advisory**: The moved manifest's header still says it is loaded as rubric for the three-tier/HFSM and §11 auditors, which stops being true when it moves to config/architecture/.
  - evidence: `hm:.claude/skills/architecture-review/rubric/arch-docs-manifest.yml:1-3`

### Looked for but did not find

- an origin row with no `detector`, which the plugin's required `detector: str` would refuse when it reads the origin mandates file (all 48 rows set one)
- an origin call_sites value outside the plugin's CallSite literal (only ci, precommit, posttooluse and audit occur)
- a reader of build/architecture_review/_last_run.json anywhere outside docs/
- any `from acf`/`import acf` in origin scripts/ or tests/
- a non-docs consumer of arch-docs-manifest.yml other than the pointer and the deleted rubric module and tests
- a CI, config or pre-commit reference to any test file or module §5.4 deletes
- a second dual-installed skill under .cursor/skills/ that would still need skill_install
- a plugin test, script or Python module that reads skills/architecture-review/auditors/*.md
- an exception class subclassing one of the deleted origin exception classes
- a test asserting coverage_map backstop 'auditor:<name>' strings against auditor prompt files

## compliance

### Claim verdicts

#### C22 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_skill_prose.py:13-25; plugins/arch-compliance/tests/test_adr_skill_prose.py:42-47; docs/design/ARCHITECTURE_REVIEW_PORT.md:92; docs/design/ARCHITECTURE_REVIEW_PORT.md:317`
- reasoning: The doctrine says skill prose and runtime messages name no host repository, path or section (ARCHITECTURE.md:206-207). The prose test is an enumerated FILES list checked against a FORBIDDEN vocabulary (test_adr_skill_prose.py:13-25, :42-47), so adding the architecture-review tree and the pack files to it is a direct extension. The spec states that rule prompts carry no repository values, which reach the auditor only as row settings (§4.2, :92), and §6/§7 extend the test (:317, :337). The claim holds for the prose surfaces it names. The runtime-message half of the section is a separate gap, filed as an unanchored finding.

#### C23 — REFUTED
- evidence: `docs/design/ARCHITECTURE_REVIEW_PORT.md:163; docs/design/ARCHITECTURE_REVIEW_PORT.md:164; docs/design/ARCHITECTURE_REVIEW_PORT.md:136; config/architecture/ARCHITECTURE.md:189-202`
- reasoning: `## Declared, never defaulted` allows a built-in default only when the section records it, as it does for the ratchet, resolve_repo and the judge's defaults (:193-202). The claim says the extension records 'the three built-in meanings' (built-in exclusion list, absent surface, empty subsystems; spec :136). The design has at least one more host-facing built-in meaning that is not recorded: a fixed test-path pattern list (`tests/`, `test_*.py`, `*_test.py`, `**/*.test.*`, `**/*.spec.*`). Step 2 explicitly separates it from 'the built-in exclusions' (:163), it applies again in step 3 (:164), and a host cannot declare it (review.yml has only `exclude`). The empty-list meanings of the optional RuleSettings keys (`surface_exclude`, `docs`, `exception_base` absent on row §3 but present on §3-exception-base, §5.2) are not recorded either. The required-field and missing-file half of the claim holds (§4.4, :124, :136). The 'three meanings' enumeration does not match the design.

#### C24 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_exceptions.py:35-45; plugins/arch-compliance/python/acf/exceptions.py:1; docs/design/ARCHITECTURE_REVIEW_PORT.md:307`
- reasoning: `## One base exception` (:110-112) says every ACF exception subclasses AcfError and nothing else. test_adr_exceptions.py:35-45 asserts this across the whole acf.exceptions module, so the two new classes listed in §6 (:307, 'each deriving from AcfError alone') are enforced automatically. ReviewerContractViolationError keeps its place in ADR_TYPES (:11). The reused EmptyTargetTreeError and UnknownMandateError already derive from AcfError (exceptions.py:9, :25).

#### C25 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:11-26; plugins/arch-compliance/python/acf/repo.py:47-73; config/architecture/ARCHITECTURE.md:127-140; docs/design/ARCHITECTURE_REVIEW_PORT.md:171`
- reasoning: acf.repo is where host-relative constants live (CONFIG_DIR, ADR_REL and the others, repo.py:11-26). REVIEW_REL joins them, in the same pattern as ADR_REL. RepoTree is the one path-to-location owner (repo.py:47-73; doctrine :127-131). The design adds `files` to RepoTree rather than globbing in callers. It routes hatch prompts through RepoTree.file (:143), write targets through `contained` and reads through `file`/`directory` (:171). The guard test scans all of plugins/arch-compliance/python/ (:131-133), so the new acf.review package falls under it with no extra wiring.

#### C26 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:220-223; plugins/arch-compliance/python/acf/adr/parser.py:26; plugins/arch-compliance/python/acf/adr/parser.py:53-70; plugins/arch-compliance/python/acf/adr/run_detail.py:183-191`
- reasoning: The existing missing_anchors tests equality against stripped doctrine lines (registry.py:221-223). That is the 'stripped text equals the anchor' procedure anchor_line is specified to implement, so rewriting missing_anchors on it can keep the same result. The fence regex, the one-block check and the JSON decode are in parse_reviewer_payload (parser.py:26, :53-70) and move to one extractor. run_detail's mkdir-write-wrap (run_detail.py:183-191) is the shape write_text_record absorbs. Each duplicated procedure gets one owner. One residual single-point concern, the glob dialect, is filed as an unanchored finding.

#### C27 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:91-99; docs/design/ARCHITECTURE_REVIEW_PORT.md:180-196; docs/design/ARCHITECTURE_REVIEW_PORT.md:111`
- reasoning: `## Live consumers` (:224-226) requires each export to have a call site in the package, a hook or a skill, not only a test. The §4.8 table names a package or skill-step call site for every new export (:182-196). anchor_line's consumer missing_anchors is live in a skill: acf-mandate/SKILL.md:91 imports it and :99 calls it. The pack `detectors` key is refused, not built (:111). The sidecar is dropped (decision 15).

#### C28 — SURVIVED
- evidence: `pyproject.toml:3; plugins/arch-compliance/.claude-plugin/plugin.json:3; scripts/check_installed_skills.py:18-34; docs/design/ARCHITECTURE_REVIEW_PORT.md:316`
- reasoning: `## Release discipline` (:255-262) requires a skill-prose change to bump the version in plugin.json and pyproject.toml. Both read 0.2.5 today (pyproject.toml:3, plugin.json:3), and §6 moves both to 0.3.0 (:320). The installed-skill check iterates a GATE_SKILLS tuple (check_installed_skills.py:18-34), so covering architecture-review means adding a tuple entry, which §6 lists (:316), along with the doctrine edit (:315).

#### C29 — SURVIVED
- evidence: `config/architecture/mandates.yml:51; config/architecture/mandates.yml:142; plugins/arch-compliance/profiles/react-app/mandates.yml:46; plugins/arch-compliance/profiles/python-service/mandates.yml:101; docs/design/ARCHITECTURE_REVIEW_PORT.md:250-254`
- reasoning: `## No completeness claims` (:230-233) requires a re-runnable recipe behind any tree quantifier. Each of the four named claims carries one: §5.4 recipes A/B/C (:252-254), §4.10's `git grep -n "auditor:"` (:204), §5's acf-import grep (:215) and decision 15's pointer to recipe A (:45). I reran the §4.10 search over non-docs files. It yields exactly the four row hits the spec names plus registry.py:61, the field declaration the spec cites separately in §4.5. One smaller negative claim lacks a recipe: §3's 'it reads no auditor file' for judge.py (:56). It is not among the four claims.

#### C30 — UNPROVEN
- evidence: `plugins/arch-compliance/python/acf/diff.py:17-30; docs/design/ARCHITECTURE_REVIEW_PORT.md:168; docs/design/ARCHITECTURE_REVIEW_PORT.md:167`
- reasoning: The auditor half holds: a contract violation marks the group FAILED, keeps the raw payload and makes the exit non-zero (:167). `## Fail loud` (:28-32) says failures must not disappear. run_git returns any non-zero status as data with check=False (diff.py:24-30). The spec maps 'a non-zero rev-list status' to 'commit not in history' (:168). So every other rev-list failure would be reported as a modeled warning that never changes the exit status: not a repository, unborn HEAD, safe.directory 'dubious ownership' refusal, a malformed commit field. A missing git binary raises (subprocess FileNotFoundError), so the narrow 'never folding missing git into not-in-history' statement is true. The design does not show that other git failures stay loud, and blame's 'unresolved' class (:168) has the same open question.

#### C31 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/contract.py:129; config/architecture/ARCHITECTURE.md:59-66; docs/design/ARCHITECTURE_REVIEW_PORT.md:175`
- reasoning: `## POSIX paths` governs persisted paths, and this plugin enforces it by refusing backslashes through PosixStr (doctrine :64-66, contract.py:129). The persisted path fields use PosixStr: AuditorFinding.path (:175), report_dir, baseline_path and subsystems (:128-133). Caveat: review.yml `exclude` and the RuleSettings glob/path keys (`surface`, `surface_exclude`, `docs`) are typed plain str or list[str]. They are host inputs, not persisted output, so the doctrine rule is not breached, but 'review.yml paths are PosixStr' is true only of the path-typed fields.

#### C32 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:242-251; plugins/arch-compliance/python/acf/diff.py:24-30; docs/design/ARCHITECTURE_REVIEW_PORT.md:171`
- reasoning: The doctrine requires subprocess text calls to declare encoding='utf-8' and lists run_git (diff.py:24-30) as declared debt (:246-251). The design adds no new subprocess call: staleness and blame go through run_git. It declares UTF-8 for every package file read (:171). Two caveats. The spec's §4.7 step 7 cites the gap at ARCHITECTURE.md:265-279 (Single point of definition, runner consolidation), but the encoding debt is recorded at :246-251. Blame output carries source-line text, so the new consumers widen exposure to the recorded debt on a non-UTF-8 locale. The pre-pass reading target-tree files is covered by 'every file the package reads', but the parenthetical list omits it and the decode-failure behaviour is not stated.

#### C33 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/CLAUDE.md:128; C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/arch_compliance/engine.py:815-843; C:/Users/iball/Arduino/Projects/HistoricMansions/config/architecture/ARCHITECTURE.md:9`
- reasoning: The quote matches hm:CLAUDE.md:128 verbatim: a census with grep recipes recorded in the spec and validated against known sites. §5.4 records recipes A-C and states they reproduce the known sites (:250). I spot-checked two. Recipe C's names occur at hm engine.py:815-821 and :842-843, matching the census row. Recipe A's `architecture-review` term occurs at hm ARCHITECTURE.md:9, matching the :8-9 row.

#### C34 — SURVIVED
- evidence: `docs/design/ADR_GATE_HOST_CONTRACT.md:79-86; plugins/arch-compliance/python/acf/registry.py:220-223; C:/Users/iball/Arduino/Projects/HistoricMansions/config/architecture/mandates.yml:14`
- reasoning: Decision 5 reads the doctrine from ARCH_REL and every document it points to, declares no doctrine field, and requires a pointer to carry every arch_anchor heading (ADR_GATE_HOST_CONTRACT.md:79-86). The review declares no doctrine documents (decision 16, §4.6), and anchors resolve in ARCH_REL through the same stripped-line rule missing_anchors uses (registry.py:221-223). The origin registry's gemini_anchor values reduce to twelve distinct GEMINI.md headings, §3 through §14 (hm mandates.yml:14 through :550), matching §5.5's 'twelve'.

### Unanchored findings

- **important**: Review row selection ignores `call_sites`: an active row joins the review whenever `auditor` is set (§4.5), with no reference to the closed vocabulary's `audit` site, which contradicts the doctrine's 'rows run where their call_sites say' and acf-mandate's 'A row runs only at the sites it declares'; the spec does not name `## Host detectors and call sites` or say what `audit` now means.
  - evidence: `docs/design/ARCHITECTURE_REVIEW_PORT.md:140; config/architecture/ARCHITECTURE.md:11; plugins/arch-compliance/skills/acf-mandate/SKILL.md:43`
- **important**: Staleness treats every non-zero `rev-list` status from run_git as 'commit not in history', a report-only warning, so other git failures (not a repository, dubious-ownership refusal, malformed baseline commit) disappear into a modeled state, the origin's own fold (hm baseline_staleness.py:73-74) carried over.
  - evidence: `docs/design/ARCHITECTURE_REVIEW_PORT.md:168; plugins/arch-compliance/python/acf/diff.py:24-30; C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/baseline_staleness.py:73-74`
- **important**: The built-in test-path pattern list (step 2, distinct from 'the built-in exclusions') is a host-facing built-in meaning that the planned `## Declared, never defaulted` extension does not record among its 'three built-in meanings', and a host cannot declare its own test layout.
  - evidence: `docs/design/ARCHITECTURE_REVIEW_PORT.md:163; docs/design/ARCHITECTURE_REVIEW_PORT.md:136`
- **advisory**: `## Prose names no host` also covers runtime messages, but the only enforcing test for package messages scans `acf/adr/*.py` alone, so the new `acf.review` package's messages are unenforced. §6's doctrine edits also leave stale the section's enumeration of which skills the prose test checks.
  - evidence: `plugins/arch-compliance/tests/test_adr_code_portability.py:7; config/architecture/ARCHITECTURE.md:208-212; docs/design/ARCHITECTURE_REVIEW_PORT.md:315`
- **advisory**: Decision 10 shares `allowlist_globs` between the `facade.forbid-sink` detector, which matches with fnmatch (`*` crosses `/`), and the `single-owner` rule, while the review's new RepoTree.files uses pathlib.Path.glob semantics: one declared string, two matching dialects (`## Single point of definition`), unstated in the spec.
  - evidence: `plugins/arch-compliance/python/acf/detectors/facade_sinks.py:59; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:68; docs/design/ARCHITECTURE_REVIEW_PORT.md:163`
- **advisory**: §4.7 step 7 cites the run_git encoding gap as ARCHITECTURE.md:265-279 (Single point of definition, two git runners); the encoding debt is recorded under `## Declared text decoding` at :246-251.
  - evidence: `docs/design/ARCHITECTURE_REVIEW_PORT.md:168; config/architecture/ARCHITECTURE.md:246-251`

### Looked for but did not find

- ## Build artifacts: the review writes only report_dir and baseline_path; dist/ and build/ appear only as read exclusions. Not touched.
- ## Fail-loud ratchet, ## Façade sinks, ## FSM transitions: the design reuses the facade and FSM detectors' params key names (cited :80-86, :88-94) but changes no detector or row shape. No conflict.
- ## Frozen ledger format: write_text_record changes how run_detail is written, but the run detail is not the ledger, and no LedgerRow or LedgerAmendment field changes. Not touched.
- ## One base exception: two new exceptions, both AcfError-only, covered by the module-wide test. Cleared.
- High-frequency miss, a stdlib mixin on an exception: none in the design.
- High-frequency miss, a check re-implemented instead of consumed: the review consumes load_mandates (:140) and builds anchor resolution on the helper missing_anchors uses. Cleared.
- ## Post-merge: no change to the operational declarations.
- ## Soft fail-loud smells: the soft.fail-loud row (status partial, auditor fail-loud) now dispatches through the fail-loud rule. Consistent with 'may be reviewed via the LLM judge', no conflict.
- ## Release discipline: the version bump and the extended check are both planned. Cleared.

### Unstated mandates

- ## Host detectors and call sites: this section defines the closed call_sites vocabulary, including `audit`, and the intro says rows run where their call_sites say. The review's row selection (§4.5) ignores call_sites, and the spec never names this section.
- ## Scoped refactor: the change surface edits ADR-gate modules (acf/adr/parser.py, acf/adr/run_detail.py) and baseline.py to share helpers. Single point of definition justifies it, but the spec does not cite the scoping rule or say why these edits are inside the approved scope.

## sweeper

### Claim verdicts

#### C35 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/host.py:19-33; config/architecture/adr.yml:1-2; plugins/arch-compliance/python/acf/repo.py:15-26`
- reasoning: AdrHostConfig (extra=forbid, PosixStr fields, require_file(ARCH_REL) then load_model_file) is the shape ReviewHostConfig follows. I compared each proposed field with adr.yml (runs_dir, ledger_path), the acf.repo constants (MANDATES_REL, ARCH_REL, ADR_REL, RATCHET_BASELINE_REL) and the Mandate row fields (registry.py:50-62). report_dir, baseline_path, the thresholds, subsystems and exclude appear nowhere else. `packs` overlaps in part with the rows' `languages` (python/typescript), but it is finer-grained (react, svelte, html-templates, sql), so it does not duplicate a declared value.

#### C36 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/finding.py:11-19; plugins/arch-compliance/python/acf/baseline.py:59-65; plugins/arch-compliance/python/acf/adr/contract.py:38`
- reasoning: Finding carries severity BLOCK/WARN, detector, confidence and detection, and has no snippet, why or suggested_fix. The stated reason holds. aggregate reads only finding.mandate_id and finding.path (baseline.py:63), so a two-field protocol is the real interface and baseline does not fork. Caveat: after SKILL.md:108 is removed, no live caller passes Finding to aggregate; only test_baseline.py does. The nearest existing shape for an agent-produced finding is the ADR UnanchoredFinding/Severity (contract.py:38, 210-215: blocking/important/advisory), and the spec does not weigh it (see unanchored findings).

#### C37 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/parser.py:26-70; plugins/arch-compliance/python/acf/judge.py:303-317`
- reasoning: I searched by behaviour (the ```json fence regex, json.loads over agent output) across python/, hooks/ and skills. The only fenced-block extractor is parser.py:26-70. judge._parse_json_object (judge.py:303-317) also pulls JSON out of LLM text, but it parses unfenced provider responses with a lenient `\{.*\}` fallback, which is a different contract. The spec leaves it out of scope (§3). test_adr_skill_invariants.py:36 has a fence regex, but that is test code over skill prose. So 'single implementation of fenced-JSON extraction' holds.

#### C38 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/baseline.py:68-75; plugins/arch-compliance/python/acf/adr/run_detail.py:178-191; plugins/arch-compliance/python/acf/approval.py:7-10`
- reasoning: I grepped write_text, .write( and mkdir( across python/, hooks/ and scripts/. save_baseline and write_run_detail are the same mkdir-parent, UTF-8 write and wrap-OSError sequence, so the claim's scope (baseline, run detail, report) is right. A third writer with the same responsibility exists: approval.write_approval (approval.py:177-192). Its docstring (approval.py:7-10) records on purpose why it shares no helper with save_baseline (atomic replace of a per-user store written by concurrent processes). ledger.py:209-213 appends rather than writing a record. Neither breaks the scoped claim.

#### C39 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:220-223; plugins/arch-compliance/python/acf/judge.py:266; plugins/arch-compliance/hooks/inject_constraints.py:165-168`
- reasoning: I grepped arch_anchor and missing_anchors across all .py files. The only resolver is missing_anchors. judge.py:266 only substitutes the anchor text into a prompt. inject_constraints.py:165-168 reads ARCH_REL whole, with no section extraction, and the hooks contain no heading parsing. Runtime code therefore has no second resolver or extractor. Caveat outside 'code': acf-setup SKILL.md:137-139 still does a by-eye anchor check (a breach recorded at ARCHITECTURE.md:275-276), and the spec edits that file without retiring it. Several documents also describe the match as a 'literal substring', which contradicts the line-equality procedure (see findings).

#### C40 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:16; plugins/arch-compliance/python/acf/cli_check_diff.py:152; plugins/arch-compliance/python/acf/cli_check_diff.py:188; plugins/arch-compliance/hooks/posttooluse_gate.py:50`
- reasoning: Language = Literal[python, typescript, both, none] exists at registry.py:16, and packs reuse it for `language`. The gate routes .py at cli_check_diff.py:152 and .ts/.tsx at :188, so ts-js (adding .js/.jsx/.mjs/.cjs) is the pack whose extent differs. The deferral to part two is stated. Not named: the PostToolUse hook has its own suffix map (_CODE_SUFFIXES, posttooluse_gate.py:50), a further file-to-technology owner that §3 and §10 do not list.

#### C41 — UNPROVEN
- evidence: `plugins/arch-compliance/python/acf/detectors/facade_sinks.py:35-36; plugins/arch-compliance/python/acf/registry.py:207-211; config/architecture/mandates.yml:102-130`
- reasoning: The key names match: the facade detector reads target_literal_re and allowlist_globs (facade_sinks.py:35-36, mandates.yml:113-114), and the FSM detector reads state_field and validator_name (mandates.yml:129-130). The consequence 'a fact both need is declared once' holds only when the auditor sits on the built-in detector's own row. _check_builtin requires that row's id to equal the detector's fixed mandate id (registry.py:207-211; ARCHITECTURE.md:84-85), so a repository has at most one such row per detector. The spec's only concrete instance, origin §5.2, puts target_literal_re and allowlist_globs on two non-detector rows (§11, §11-inventory), which repeats the same fact in each. The mechanism that would make 'declared once' true is never shown.

#### C42 — SURVIVED
- evidence: `hm:scripts/core/architecture_review/ui_logic_prepass.py:31-62`
- reasoning: A case-insensitive grep for prepass, pre-pass and candidates over plugins/ finds no pre-pass, only ADR convergence candidates, a different job. The origin tells at ui_logic_prepass.py:31-52 and scan_text at :55-62 are the named duplicate that stays in the moved gate module (§5.4, §8). Note: the tells exclude origin-specific identifiers (resp|response|ui_state|uiState|data at :48), and the ts-js pack copies them with no settings substitution.

#### C43 — SURVIVED
- evidence: `config/architecture/mandates.yml:51; config/architecture/mandates.yml:142; plugins/arch-compliance/profiles/react-app/mandates.yml:46; plugins/arch-compliance/profiles/python-service/mandates.yml:101`
- reasoning: I grepped for auditor in every spelling (auditor:, auditor=, 'auditor') outside docs/ and found exactly these four rows plus the model field (registry.py:61). No test fixture or template emits an auditor key. In this repository, row :51 (soft.react-boundaries) is status: unenforced (:49), so it is not reviewed after the rename either.

#### C44 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:99; tests/test_self_host.py:40; plugins/arch-compliance/tests/test_profile_drift.py:30; plugins/arch-compliance/tests/test_registry.py:60`
- reasoning: A grep for missing_anchors finds exactly these four callers plus the definition (registry.py:220). Caveat: missing_anchors strips the anchor as well as the line (registry.py:222-223), while §4.6 defines anchor_line as matching 'stripped text equals the anchor' and is silent on stripping the anchor. The result is identical only if anchor_line strips both sides.

#### C45 — SURVIVED
- evidence: `config/architecture/mandates.yml:41-51; config/architecture/mandates.yml:132-142; plugins/arch-compliance/profiles/react-app/mandates.yml:36-46; plugins/arch-compliance/profiles/python-service/mandates.yml:91-101`
- reasoning: None of the four auditor rows carries a params block. Every params block in these files (mandates.yml:37-38, 96-99, 112-115, 128-130) sits on a row without an auditor.

#### C46 — SURVIVED
- evidence: `plugins/arch-compliance/skills/architecture-review/SKILL.md:115; plugins/arch-compliance/tests/test_baseline.py:8`
- reasoning: I grepped acf.baseline, 'from acf import baseline' and each exported function name outside docs/. The consumers are the skill snippet (SKILL.md:115-137) and test_baseline.py. approval.py:7-10 names save_baseline only in a docstring, and its prose describes save_baseline's current write path, which this design changes.

#### C47 — SURVIVED
- evidence: `hm:scripts/core/architecture/registry.py:33; hm:config/architecture/dead_code_baseline.json:195; hm:tests/test_mandate_registry_drift.py:62`
- reasoning: I grepped gemini_anchor outside docs/, including the hidden .claude, .cursor and .github trees, which hold no hits. Hits are in mandates.yml, registry.py:33, dead_code_baseline.json:195 and the three test files. Pydantic reads fields by name, and MandateEntry has no generic field iteration or alias, so a name recipe matches the behaviour here. Note: test_mandate_registry_drift.py:60-62 checks anchors as substrings of GEMINI.md. After the rename it keeps doing that, beside the plugin's line-equality check against ARCH_REL.

### Unanchored findings

- **important**: Decision 10's 'declared once' rests on a rule row sharing params with a detector row, but each built-in detector reports only to one fixed mandate id, so at most one row per repository can carry both. The origin cutover already declares target_literal_re/allowlist_globs on two non-detector rows (§11, §11-inventory).
  - evidence: `plugins/arch-compliance/python/acf/registry.py:207-211`
- **advisory**: AuditorFinding adds a third severity vocabulary (blocking/important/nit/suggestion) beside the gate's BLOCK/WARN and the ADR gate's agent-finding scale blocking/important/advisory. The spec justifies the split against acf.finding.Finding only, not against the nearest agent-finding shape.
  - evidence: `plugins/arch-compliance/python/acf/adr/contract.py:38`
- **advisory**: §4.6 quotes the host contract's 'literal substrings' rule as its authority, then defines anchor resolution as stripped-line equality. The quoted contract and the skill prose (acf-mandate, acf-setup) still say substring.
  - evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:46`
- **advisory**: The PostToolUse hook has its own file-suffix-to-technology map, which §3 and §10 do not name when they defer unifying file-to-technology routing to part two.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:50`
- **advisory**: RepoTree.files introduces pathlib.Path.glob semantics. The fail-loud ratchet (rglob plus fnmatch excludes, with its own test-path defaults) and the facade detector (fnmatch over allowlist_globs, a key the single-owner rule now shares) use fnmatch, so the plugin has two glob dialects and two default test-exclusion lists.
  - evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:57-68`
- **advisory**: The spec edits acf-setup SKILL.md and retires the architecture-review:62 breach, but leaves the recorded by-eye anchor check in acf-setup in place, a second anchor procedure in an executable skill.
  - evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:137-139`
- **advisory**: After cutover the origin keeps a separate anchor check (substring of GEMINI.md) under the renamed arch_anchor field, while the plugin checks line equality in ARCH_REL. The two decision procedures for 'anchor resolves' run against different files.
  - evidence: `hm:tests/test_mandate_registry_drift.py:60-62`

### Looked for but did not find

- second fenced-JSON extractor in plugin code: grep ```json, json.loads, re.compile over python/ hooks/ skills/
- second doctrine-section extractor or heading parser: grep startswith("#"), heading, section in hooks/ and python/
- other readers of arch_anchor in runtime code: grep arch_anchor over **/*.py
- rows carrying auditor plus params: grep auditor in every spelling over config/, profiles/, tests/
- existing pre-pass or regex candidate scanner in the plugin: grep prepass, pre-pass, candidates
- other consumers of acf.baseline: grep acf.baseline, baseline function names, BaselineError outside docs/
- host values duplicated between review.yml and adr.yml/acf.repo/Mandate: read adr.yml, repo.py, registry.py:50-62
- gemini_anchor readers in hidden origin trees: grep .claude, .cursor, .github

### Relationships

- ADJACENT: `acf.loader.write_text_record` — responsibility `write a text record: make the parent directory, write UTF-8, wrap OSError with the POSIX path` — existing `plugins/arch-compliance/python/acf/approval.py:177-192`
  - resolution: none; keep approval outside the helper
  - non-merge: approval.py:7-10 records that the per-user store is rewritten by concurrent processes and must be replaced atomically (temporary file, then os.replace). The new helper writes in place.
- ADJACENT: `acf.agent_payload.extract_json_block` — responsibility `extract a JSON object from LLM output` — existing `plugins/arch-compliance/python/acf/judge.py:303-317`
  - resolution: none in this spec
  - non-merge: The judge parses unfenced provider JSON with a lenient fallback, and §3 puts the judge out of scope. The fenced exactly-one-block contract is different.
- PARTIAL_OVERLAP: `acf.review.contract.AuditorFinding.severity` — responsibility `classify an agent-produced finding's severity` — existing `plugins/arch-compliance/python/acf/adr/contract.py:38`
  - resolution: Shared R: severity of a read-only agent's finding. Either reuse acf.adr.contract.Severity (mapping nit/suggestion to advisory) or state in writing why the review needs four levels where the ADR gate uses three.
- PARTIAL_OVERLAP: `acf.repo.RepoTree.files plus the built-in exclusions of §4.7 step 2` — responsibility `enumerate repository files by glob minus default vendor/test exclusions` — existing `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:57-68`
  - resolution: Shared R: glob enumeration with exclusions. RepoTree.files becomes the single enumerator, the ratchet consumes it, and one default test-path set lives beside it. Otherwise the fnmatch-versus-Path.glob difference is recorded as debt.
- PARTIAL_OVERLAP: `pack `files` globs` — responsibility `map file paths to a technology` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:50`
  - resolution: Shared R: file-to-technology routing. Part two's single map must absorb the hook's _CODE_SUFFIXES as well as cli_check_diff.py:152/188, so §10 should name it.
- PARTIAL_OVERLAP: `acf.registry.anchor_line` — responsibility `decide whether an anchor resolves in the doctrine` — existing `plugins/arch-compliance/skills/acf-setup/SKILL.md:137-139`
  - resolution: The acf-setup step consumes missing_anchors/anchor_line instead of a by-eye check, and its 'literal substring' prose is reworded to line equality.
- IDENTICAL: `ts-js pack ui-logic-isolation hints` — responsibility `flag UI-logic candidate lines by regex` — existing `hm:scripts/core/architecture_review/ui_logic_prepass.py:31-52`
  - resolution: Named duplicate until part two moves the gate's staged check onto acf.review.prepass (spec §8, §10)

### Two-owner counts

- write a text record with parent mkdir and OSError wrap: 2
- extract a JSON object from LLM output: 2
- file-to-technology routing: 3
- enumerate repository files by glob minus exclusions: 2
- default test-path exclusion set: 2
- finding severity vocabulary: 3
- anchor-resolves decision (plugin and origin): 2
- UI-logic regex tells: 2

### Document conflicts

- `docs/design/ADR_GATE_HOST_CONTRACT.md:84` (restates): because the plugin matches those as literal substrings of this file
- `plugins/arch-compliance/skills/acf-mandate/SKILL.md:46` (contradicts): Literal substring of ARCHITECTURE.md (usually a `##` heading)
- `plugins/arch-compliance/skills/acf-setup/SKILL.md:139` (contradicts): mandate `arch_anchor` values are matched as literal substrings of ARCHITECTURE.md

## hardening

### Claim verdicts

#### C48 — SURVIVED
- evidence: `hm:.claude/skills/architecture-review/auditors/metadata-facade.md:3; hm:.claude/skills/architecture-review/auditors/fail-loud.md:3; plugins/arch-compliance/skills/architecture-review/auditors/fail-loud.md:1-3`
- reasoning: Per-repository copies do mix host data into rule prose. The origin metadata-facade auditor hard-codes ContentMetadataService and index.yml at :3. The origin fail-loud auditor names 'the Historic Mansions architecture-review skill' at :3. The plugin already has a second fail-loud prompt stating the same principle, so the rule prose is repeated across the two copies. Splitting rule, pack and row params puts each fact in one place.

#### C49 — SURVIVED
- evidence: `hm:scripts/core/architecture_review/contract.py:41; hm:docs/architecture/compliance_baseline.json:6`
- reasoning: The origin AuditorResult carries a free-text `mandate: str` (contract.py:41), and the baseline keys counts on labels such as 'Three-Tier/HFSM' and '§11 Metadata Façade' (compliance_baseline.json:6). These are not registry ids, so the free-text identity is real. Grouping by `auditor` caps dispatches at the number of distinct auditor values. The origin registry has 25 rows with auditor set but only 8 distinct values, which map to 12 rule ids or fewer. Requiring mandate_id to be one of the group's rows is a refusal, not a repair.

#### C50 — SURVIVED
- evidence: `hm:.claude/skills/architecture-review/SKILL.md:90; plugins/arch-compliance/skills/architecture-review/SKILL.md:106`
- reasoning: The producer of a malformed payload is an LLM sub-agent, which is a genuine external boundary. Both the origin skill (:90) and the current plugin skill (:106) already mark the group FAILED, keep the raw payload and exit non-zero. The failure is surfaced, not silenced: the raw text is kept and the exit status is non-zero. Hardening the producer is not available, because the agent's output cannot be made unrepresentable.

#### C51 — SURVIVED
- evidence: `hm:scripts/ci/baseline_staleness.py:87; hm:scripts/setup_git_hooks.py:138`
- reasoning: The origin staleness script imports load_baseline from scripts.core.architecture_review.baseline (:87), which §5.4 deletes. It runs on pre-push (setup_git_hooks.py:138). Keeping the script would mean either keeping the deleted module or importing acf's baseline loader in origin hooks and CI. Moving staleness into the plugin roll-up removes that need. The thresholds are carried over as review.yml fields.

#### C52 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:253-263; scripts/check_installed_skills.py:18-22`
- reasoning: The order is sound: origin acceptance runs through the installed 0.3.0 plugin, so the plugin release must exist first, and a patch release before the origin merge keeps the origin PR on a released plugin. The confirmation step is weaker than the claim implies, because the check covers skill trees only (ARCHITECTURE.md:260-261, GATE_SKILLS at check_installed_skills.py:18-22). This is filed as an unanchored finding.

#### C53 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:50-62; plugins/arch-compliance/python/acf/registry.py:91-98; plugins/arch-compliance/python/acf/registry.py:16`
- reasoning: Mandate declares no model_config, so pydantic's default extra='ignore' applies and `remediation` (origin mandates.yml:103, 21 rows) is tolerated. With no detector arguments, load_mandates (registry.py:150-198) skips the known_detectors and llm_prompt_ids checks. _row_shape applies host-detector checks only when the detector contains ':' (registry.py:30-31, 94-96). No origin ast/guard detector (for example `_find_bare_except`, `scripts/ci/metadata_facade_guard.py`) contains ':'. Every active origin ast/guard row declares ci or precommit, so the Tier-1 check passes. Origin severity/detection/status/call_sites values all fall inside the Literals (BLOCK/WARN; guard/ast/llm/manual; enforced/partial; ci/precommit/posttooluse/audit). The Language literal (:16) accepts python, typescript and none. This depends on the §5.1 migration adding `languages` and renaming gemini_anchor to arch_anchor, both required fields.

#### C54 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:61-62; plugins/arch-compliance/python/acf/registry.py:75-88`
- reasoning: `auditor: str | None` and `params: dict[str, Any] | None` exist. The only params constraint is JSON-only (:75-88), so nested settings such as exception_base {class_name, module} and lists of tier objects validate. No other code reads `auditor`: grep over plugin and scripts Python finds only registry.py:61.

#### C55 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:53-69; pyproject.toml:5`
- reasoning: contained/file/directory exist at repo.py:53-69, and requires-python >=3.11 is at pyproject.toml:5. A read-only Path.glob('acf/**/repo.py') on plugins/arch-compliance/python returned acf/repo.py, so `**` matches zero directories. The include side holds. The exclusion side does not, and is filed separately: under Path.glob semantics, `test_*.py` and `tests/` match only at the root.

#### C56 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:24-30`
- reasoning: run_git calls subprocess.run(['git', ...], check=False) with no try/except. A non-zero status comes back as data, and a missing git binary raises FileNotFoundError out of subprocess. That is a change from the origin, which folded OSError into the 'not in history' None at hm:scripts/ci/baseline_staleness.py:65-73. Caveat: a non-zero rev-list status also covers other git failures (not a repo, bad object name), and the spec folds those into 'commit not in history'. That is advisory only.

#### C57 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/parser.py:53-70; plugins/arch-compliance/tests/test_adr_parser.py:46-57; plugins/arch-compliance/tests/test_adr_exceptions.py:24-32`
- reasoning: The fence regex (:26), the zero/multiple-block checks and json.loads (:53-70) do not depend on the reviewer schema; only the `expected_reviewer` label is interpolated, and `subject` covers that. The identity check (:72-77) stays in the caller. The parser tests match on 'no ```json fenced block', 'multiple \(2\)' and 'JSON parse failed' (test_adr_parser.py:46-57), so the extractor must keep those message fragments. test_adr_exceptions requires __bases__ == (AcfError,) for every exception in the module (:24-45), which the new AuditorContractViolationError and ReportWriteError are specified to satisfy.

#### C58 — SURVIVED
- evidence: `hm:scripts/ci/dead_code_ratchet.py:504-512; hm:scripts/ci/dead_code_ratchet.py:406-408`
- reasoning: :493 is the argparse flag declaration. The mode body at :504-512 derives lanes from fresh scans of repo_root/scripts and scripts+tests (:406-408) on the working tree, and writes the baseline. So running it after the other edits records the edited tree's unread fields, including MandateEntry.languages and params.

#### C59 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_skill_prose.py:13-20; plugins/arch-compliance/tests/test_adr_skill_prose.py:43-48`
- reasoning: FILES is an explicit path list (:13-20), and the forbidden-literal scan iterates it (:43-48). Adding the architecture-review skill files and python/acf/review/packs/*.yml is a list extension. Note: FORBIDDEN includes 'docs/reviews' and 'docs/architecture', so the rewritten SKILL.md must not name origin report paths, which is consistent with report_dir being declared.

#### C60 — SURVIVED
- evidence: `hm:scripts/ci/arch_compliance/llm_judge.py:293; hm:scripts/ci/arch_compliance/llm_judge.py:304`
- reasoning: :293 is `rubric = load_rubric(mandate.auditor, repo_root=repo_root)` inside judge_changed_file. `mandate.id` is used in the same function at :304, so the id is in scope for a {'§5': 'three-tier-hfsm', '§6': 'ui-logic-isolation'} map. The other load_rubric caller, judge_calibration.py:62, passes a name directly, as §5.4 states. check_arch_compliance_llm.py:89 tests only `auditor is None`, which stays false.

### Unanchored findings

- **important**: §4.7 step 2 says RepoTree.files patterns follow pathlib.Path.glob. Under that root-anchored meaning, the built-in exclusions `tests/`, `test_*.py`, `*_test.py`, `__pycache__/` and `node_modules/` match only at the repository root. In this repository plugins/arch-compliance/tests/test_*.py (about 40 files found by `**/test_*.py`) would therefore enter the target tree. The spec states no separate any-depth or basename semantics for `exclude`, so two implementers would build different trees.
  - evidence: `docs/design/ARCHITECTURE_REVIEW_PORT.md:163`
- **important**: The cutover's install confirmation (§5 stage 1) extends scripts/check_installed_skills.py to the architecture-review skill tree, but that check compares skill trees only. The review's settings models, pre-pass, aggregator and all six pack YAML files live under python/acf/review/, which the check does not compare (doctrine :260-261). A stale installed python package would pass the check and could run the origin acceptance against code that is not the release.
  - evidence: `config/architecture/ARCHITECTURE.md:260-261`
- **advisory**: Validation of `auditor` values moves from an origin CI test (deleted in §5.4) to review run time only (§4.5 step 1). In both repositories, a mistyped auditor rule id or a missing hatch .md file in mandates.yml is therefore caught only the next time someone runs the review, not at the commit that writes it. The plugin's own load path (load_mandates, or the acf-mandate check that already calls missing_anchors) could refuse it at the producer, and the spec does not say why it does not.
  - evidence: `plugins/arch-compliance/python/acf/registry.py:150-198`

### Looked for but did not find

- Extra='forbid' on Mandate that would reject origin `remediation` keys: absent (registry.py:50-62)
- Any current plugin code that validates `auditor` values: none besides the field declaration at registry.py:61
- Origin ast/guard detector strings containing ':' that would trip host-row validation: none of the 42 ast/guard rows
- A second origin caller of load_rubric that passes mandate.auditor besides llm_judge.py:293: only judge_calibration.py:62, which passes a name
- A repair-on-load or normalize step in the design: none; unread params keys are listed rather than dropped, and contract violations mark the group FAILED with non-zero exit

### Mechanism traces

- **Auditor contract violation marks group FAILED and run continues with non-zero exit**
  - invalid state: an auditor final message with zero or more than one ```json block, undecodable JSON, a schema violation, or a finding whose mandate_id is not among the group's rows
  - producer: `hm:.claude/skills/architecture-review/SKILL.md:90`
  - rung 5 (highest applicable 5); repairs=False
  - hardening rejected because: one malformed payload should not discard the other groups' findings; any FAILED group makes the exit status non-zero
  - spec citation: `docs/design/ARCHITECTURE_REVIEW_PORT.md:167`
- **Report lists every params key the rule did not read**
  - invalid state: a row's params contains a key that neither the rule's settings model nor the row's detector reads (for example a misspelt settings key)
  - producer: `plugins/arch-compliance/python/acf/detectors/facade_sinks.py:21-26`
  - rung 5 (highest applicable 3); repairs=False
  - hardening rejected because: keys it does not declare belong to the row's detector or to nobody; one flat namespace so a fact both need is declared once (decision 10)
  - spec citation: `docs/design/ARCHITECTURE_REVIEW_PORT.md:73`
- **Baseline staleness warning in roll-up**
  - invalid state: baseline generated_at older than baseline_max_age_days, rev-list count baseline..HEAD greater than baseline_max_commits, or baseline commit absent from history
  - producer: `hm:scripts/ci/baseline_staleness.py:65-73`
  - rung 5 (highest applicable 5); repairs=False
  - hardening rejected because: Neither changes the exit status (advisory signal, decision 8)
  - spec citation: `docs/design/ARCHITECTURE_REVIEW_PORT.md:168`
- **Shared extract_json_block extractor**
  - invalid state: two parsers each owning a copy of the fence regex and the exactly-one-block check
  - producer: `plugins/arch-compliance/python/acf/adr/parser.py:26`
  - rung 2 (highest applicable 2); repairs=False
  - spec citation: `docs/design/ARCHITECTURE_REVIEW_PORT.md:176`
- **anchor_line single decision procedure**
  - invalid state: missing_anchors and doctrine_section deciding anchor resolution by different rules
  - producer: `plugins/arch-compliance/python/acf/registry.py:220-223`
  - rung 2 (highest applicable 2); repairs=False
  - spec citation: `docs/design/ARCHITECTURE_REVIEW_PORT.md:152`
- **write_text_record shared writer**
  - invalid state: a record write that raises a bare OSError or writes without utf-8 encoding
  - producer: `plugins/arch-compliance/python/acf/baseline.py:68-75`
  - rung 2 (highest applicable 2); repairs=False
  - spec citation: `docs/design/ARCHITECTURE_REVIEW_PORT.md:177`
- **Runtime refusal of unknown auditor value (UnknownMandateError)**
  - invalid state: an active row whose auditor is neither a key of RULES nor a path ending in .md that resolves via RepoTree.file
  - producer: `config/architecture/mandates.yml:51`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: the plugin refuses an unknown auditor at run time (§4.5), and origin CI cannot import the plugin's rule list
  - spec citation: `docs/design/ARCHITECTURE_REVIEW_PORT.md:144`
- **Origin baseline reset at cutover**
  - invalid state: baseline counts keyed on free-text auditor labels such as 'Three-Tier/HFSM' that span several mandate ids
  - producer: `hm:docs/architecture/compliance_baseline.json:6`
  - rung 4 (highest applicable 4); repairs=False
  - hardening rejected because: the three-tier-hfsm label spans six rows, so no count splits across mandate ids
  - spec citation: `docs/design/ARCHITECTURE_REVIEW_PORT.md:291`

## Claims

- **C1** [premise]: The plugin's current /architecture-review defaults to four auditors (fail-loud, no-shims, posix-paths, react-boundaries).
  - spec citation: `plugins/arch-compliance/skills/architecture-review/SKILL.md:72`
- **C2** [premise] [load-bearing]: The origin review's capabilities the port keeps are: nine auditors, a doctrine rubric step, per-auditor file surfaces, a deterministic UI pre-pass and a blame-based provenance section.
  - spec citation: `hm:.claude/skills/architecture-review/SKILL.md:31-158`
- **C3** [premise]: The origin auditors hard-code origin-repository values (owner class names, artifact names, stage file lists).
  - spec citation: `hm:.claude/skills/architecture-review/auditors/metadata-facade.md:3; hm:.claude/skills/architecture-review/auditors/output-agnosticism.md:12-25`
- **C4** [premise] [load-bearing]: The origin MandateEntry is extra='forbid' and has gemini_anchor but no languages, params or arch_anchor, so the origin model must change before the origin mandates file can carry plugin fields.
  - spec citation: `hm:scripts/core/architecture/registry.py:21-34`
- **C5** [premise] [load-bearing]: The origin drift baseline keys counts on a free-text auditor label, and the three-tier-hfsm label spans six rows, so counts cannot be split across mandate ids; hence a reset, not a migration.
  - spec citation: `hm:docs/architecture/compliance_baseline.json; §5.2`
- **C6** [premise] [load-bearing]: The origin rows with an auditor value are the 25 rows of §5.2 with the origin auditor shown (recipe: yaml.safe_load over hm:config/architecture/mandates.yml at b2611977f filtered on auditor).
  - spec citation: `hm:config/architecture/mandates.yml`
- **C7** [premise] [load-bearing]: Nothing reads the origin review's JSON sidecar: recipe A of §5.4 matches `_last_run` only at its writer, hm:.claude/skills/architecture-review/SKILL.md:154. This is why the sidecar is not ported.
  - spec citation: `§2 row 15`
- **C8** [premise] [load-bearing]: The origin LLM judge routes only §5 and §6, so it reads only the three-tier-hfsm and ui-logic-isolation prompts; load_rubric reads a prompt file by name; its caller at llm_judge.py:293 has the mandate id; judge_calibration.py passes prompt names and needs no change once load_rubric reads the new directory.
  - spec citation: `hm:scripts/ci/check_arch_compliance_llm.py:43-53; hm:scripts/ci/arch_compliance/llm_judge.py:88-98`
- **C9** [premise] [load-bearing]: No origin file imports acf today (recipe: `git grep -l -E "^(from|import) acf" b2611977f -- scripts tests` prints nothing), and the cutover adds none, so origin CI needs no new dependency.
  - spec citation: `§5`
- **C10** [premise] [load-bearing]: Deferral: the existing origin Cursor follow-up (remediation :360) covers only the two gate skills, so the cutover files a new row for architecture-review (user decision, spec §2 row 7).
  - spec citation: `hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:360`
- **C11** [premise] [load-bearing]: Deferral: absorbing react-boundaries leaves the plugin's Tier-2 judge unaffected, because the judge builds prompts from judge_prompt.md and reads no auditor file.
  - spec citation: `plugins/arch-compliance/python/acf/judge.py (judge.py:19)`
- **C12** [premise] [load-bearing]: Deferral: .svelte script extraction is not needed here, because auditors read .svelte text and pack hints are regular expressions over it.
  - spec citation: `§3`
- **C13** [premise] [load-bearing]: The origin ARCHITECTURE.md pointer names the docs manifest inside the skill tree, so the manifest moves to hm:config/architecture/arch-docs-manifest.yml with the pointer updated.
  - spec citation: `hm:config/architecture/ARCHITECTURE.md:8-9`
- **C14** [premise] [load-bearing]: The origin rows use twelve distinct anchors, all headings of hm:GEMINI.md; adding them as headings to the origin pointer makes the plugin's missing_anchors resolve every origin row, and meets the obligation the origin roadmap records as unmet ('host-contract decision 5 ... is met only vacuously').
  - spec citation: `§5.5; hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:352`
- **C15** [premise]: In the origin, DeclaredFSM.transition and transition_to are the transition methods and _apply the only state writer.
  - spec citation: `hm:scripts/builders/fsm_base.py:14,56,69,93-95`
- **C16** [deletion] [load-bearing]: Deleting plugins/arch-compliance/skills/architecture-review/auditors/ strands no consumer once §4.10 changes the two rows naming react-boundaries (config/architecture/mandates.yml:51, the react-app profile); the fail-loud rows keep a valid rule id.
  - spec citation: `§4.10`
- **C17** [deletion] [load-bearing]: The §5.4 census (recipes A, B, C) is complete for what the origin cutover deletes, moves or renames, every listed disposition is correct, and after the cutover no live origin importer or reader of a deleted or moved file remains (check scripts, tests, config, CI workflows, hooks, Markdown outside docs/).
  - spec citation: `§5.4`
- **C18** [deletion] [load-bearing]: Deleting the origin exception classes SkillLayoutError, the six review classes, BaselineStalenessError, UnknownMandateError and BaselineError leaves no raiser, importer or test of them outside the files §5.4 deletes, apart from the engine.py:815-843 name mirror §5.4 edits.
  - spec citation: `hm:scripts/core/exceptions.py:1227,1241-1280,1380,1452,1456`
- **C19** [deletion] [load-bearing]: Removing the origin staleness check needs only: deleting baseline_staleness.py and its test, removing the pre-push line at setup_git_hooks.py:138, and editing test_push_scope_hook.py:21,25-26; nothing else invokes it.
  - spec citation: `§5.4`
- **C20** [deletion] [load-bearing]: Deleting hm:scripts/core/skill_install.py is safe: its only importer outside its own test is scripts/core/architecture_review/__init__.py:10, and .cursor/skills/ holds only architecture-review.
  - spec citation: `§5.4`
- **C21** [premise] [load-bearing]: The origin dead-code ratchet has an --update-baseline mode (dead_code_ratchet.py:493) that regenerates its baseline; after the cutover edits its only growth is MandateEntry.languages and MandateEntry.params.
  - spec citation: `hm:scripts/ci/dead_code_ratchet.py:493`
- **C22** [mandate] [load-bearing]: Rule prompts, the rewritten skill and the pack files name no host (`## Prose names no host`), and the forbidden-vocabulary test is extended to the skill directory and the pack files.
  - spec citation: `config/architecture/ARCHITECTURE.md:204-213`
- **C23** [mandate] [load-bearing]: The design complies with `## Declared, never defaulted`: review.yml fields are all required and a missing file fails loud; the section is extended to name review.yml and records the three built-in meanings (built-in exclusion list, absent surface, empty subsystems).
  - spec citation: `config/architecture/ARCHITECTURE.md:187-203; §4.4`
- **C24** [mandate]: AuditorContractViolationError and ReportWriteError derive from AcfError alone, and ReviewerContractViolationError is unchanged (`## One base exception`, test_adr_exceptions.py).
  - spec citation: `config/architecture/ARCHITECTURE.md:108-113`
- **C25** [mandate] [load-bearing]: The design complies with `## One owner for host paths`: review.yml is located by acf.repo.REVIEW_REL, and every host path string becomes a location through RepoTree, including the new RepoTree.files for globbing.
  - spec citation: `config/architecture/ARCHITECTURE.md:114-141; §4.7`
- **C26** [mandate] [load-bearing]: The design complies with `## Single point of definition`: anchor resolution has one helper (anchor_line) shared by missing_anchors and the review; payload extraction one function; record writes one helper; react-boundaries absorbed; the auditor contract stated once.
  - spec citation: `config/architecture/ARCHITECTURE.md:265-279; §4.6, §4.8`
- **C27** [mandate] [load-bearing]: The design complies with `## Live consumers`: §4.8's table names a live call site for each new export, the pack detectors slot is not built, and the sidecar is dropped.
  - spec citation: `config/architecture/ARCHITECTURE.md:222-227; §4.8`
- **C28** [mandate]: The design complies with `## Release discipline`: the version goes to 0.3.0 in pyproject.toml and plugin.json and the installed-skill check covers architecture-review.
  - spec citation: `config/architecture/ARCHITECTURE.md:253-264`
- **C29** [mandate]: The spec's tree claims comply with `## No completeness claims`: each population claim (§5.4 census, §4.10 auditor consumers, §5 acf imports, §2 row 15 sidecar reader) carries its recipe.
  - spec citation: `config/architecture/ARCHITECTURE.md:228-239`
- **C30** [mandate] [load-bearing]: The design complies with `## Fail loud` and `## No shims`: an auditor contract violation marks the group FAILED, keeps the raw payload and exits non-zero; staleness tells a missing git (raises) from a commit not in history (reported), never folding one into the other.
  - spec citation: `config/architecture/ARCHITECTURE.md:26-56; §4.7 steps 6-7`
- **C31** [mandate]: Declared and persisted paths are POSIX: review.yml paths and AuditorFinding.path are PosixStr (`## POSIX paths`).
  - spec citation: `config/architecture/ARCHITECTURE.md:57-67`
- **C32** [mandate] [load-bearing]: The design complies with `## Declared text decoding`: every file the package reads is read as UTF-8, and git output decoding goes through run_git, whose missing encoding is a gap the doctrine already records.
  - spec citation: `config/architecture/ARCHITECTURE.md:240-252; §4.7`
- **C33** [mandate]: The origin stage follows the origin rule it quotes, 'Census before contract' (hm:CLAUDE.md:128): §5.4 records the census with recipes validated against known sites.
  - spec citation: `hm:CLAUDE.md:128; §5`
- **C34** [mandate] [load-bearing]: The design complies with the ADR host contract's decision 5 (docs/design/ADR_GATE_HOST_CONTRACT.md:79-86): no doctrine field is declared and anchors live as headings in ARCH_REL, including the origin pointer's twelve added headings.
  - spec citation: `docs/design/ADR_GATE_HOST_CONTRACT.md:79-86`
- **C35** [shape_fit] [load-bearing]: ReviewHostConfig in config/architecture/review.yml follows AdrHostConfig and declares no host value that adr.yml, mandates.yml or ARCH_REL already carries.
  - spec citation: `plugins/arch-compliance/python/acf/adr/host.py:28-33; §4.4`
- **C36** [shape_fit] [load-bearing]: AuditorFinding is kept beside acf.finding.Finding with a stated reason (different severity scale and provenance fields), and acf.baseline.aggregate is typed on the protocol both share (mandate_id, path), so baseline does not fork per model.
  - spec citation: `plugins/arch-compliance/python/acf/finding.py:11-19; §4.8`
- **C37** [shape_fit] [load-bearing]: acf.agent_payload.extract_json_block becomes the single implementation of fenced-JSON extraction, consumed by both parse_reviewer_payload and parse_auditor_payload.
  - spec citation: `plugins/arch-compliance/python/acf/adr/parser.py:26-60; §4.8`
- **C38** [shape_fit] [load-bearing]: acf.loader.write_text_record becomes the single write helper for the baseline, the ADR run detail and the review report.
  - spec citation: `plugins/arch-compliance/python/acf/baseline.py:68-75; plugins/arch-compliance/python/acf/adr/run_detail.py:178-190`
- **C39** [shape_fit] [load-bearing]: acf.registry.anchor_line is the single anchor-resolution procedure and acf.review.doctrine_section the only doctrine-section extractor; no other plugin code resolves or extracts by arch_anchor.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:220-223; §4.6`
- **C40** [shape_fit] [load-bearing]: Packs declare `language` in the existing Mandate Language vocabulary, so they add no third technology vocabulary; the pack whose file extent differs from the gate's routing is named ts-js; unifying file-to-technology maps with the gate is deferred to part two.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:16; §4.3`
- **C41** [shape_fit] [load-bearing]: Rule settings read from the row's flat params, and the single-owner and state-machine-discipline rules reuse the facade.forbid-sink and fsm.transition-guard detector key names, so a fact a detector and a rule both need is declared once.
  - spec citation: `config/architecture/ARCHITECTURE.md:80-94; §4.2`
- **C42** [shape_fit]: acf.review.prepass is the only pre-pass in the plugin; the origin tell set kept in the moved gate module is a named duplicate until part two.
  - spec citation: `§4.3; §8`
- **C43** [sweep] [load-bearing]: The rows naming an auditor in this repository are config/architecture/mandates.yml:51 and :142 and the two profile rows (recipe `git grep -n "auditor:" -- ':!docs'`); §4.10 changes the two react-boundaries rows.
  - spec citation: `§4.10`
- **C44** [sweep] [load-bearing]: Rewriting missing_anchors on anchor_line with the same signature and result leaves its callers (acf-mandate SKILL.md:99, tests/test_self_host.py:40, test_profile_drift.py:30, test_registry.py:60) unchanged.
  - spec citation: `§4.6`
- **C45** [sweep] [load-bearing]: No current row in this repository's registry or the plugin profiles carries both an auditor and detector params, so moving rule settings into flat params collides with no existing key.
  - spec citation: `§4.2`
- **C46** [sweep] [load-bearing]: The only consumers of acf.baseline are the architecture-review skill snippet and plugins/arch-compliance/tests/test_baseline.py, which §6 lists.
  - spec citation: `plugins/arch-compliance/python/acf/baseline.py`
- **C47** [sweep] [load-bearing]: Recipe B (`git grep -n gemini_anchor b2611977f -- ':!docs'`) covers every reader of the origin gemini_anchor field, including the dead-code baseline in config/.
  - spec citation: `§5.4`
- **C48** [mechanism_justification] [load-bearing]: Three layers plus a hatch are needed rather than per-repository copies of auditors, because copies repeat rule prose and mix host data into it.
  - spec citation: `§2 rows 1-3; §4.1`
- **C49** [mechanism_justification] [load-bearing]: One dispatch per rule (grouping rows), with findings attributed by mandate_id, bounds dispatch count and fixes the origin's free-text identity.
  - spec citation: `§4.5`
- **C50** [mechanism_justification] [load-bearing]: Auditor contract violations mark the group FAILED and the run continues with a non-zero exit, because one malformed payload should not discard the other groups' findings.
  - spec citation: `§4.7 step 6`
- **C51** [mechanism_justification] [load-bearing]: Baseline staleness moves into the plugin's roll-up (user decision) rather than the origin installing acf in CI, removing the origin's only would-be import of acf.
  - spec citation: `§2 row 8; §4.7 step 7`
- **C52** [mechanism_justification] [load-bearing]: The cutover is sequenced plugin release first, origin PR second, with plugin defects fixed by patch release before the origin PR merges.
  - spec citation: `§5`
- **C53** [implementability] [load-bearing]: Plugin load_mandates(path) with no detector arguments will load the migrated origin mandates file: extra keys such as remediation are tolerated, origin ast/guard rows with non-host detector names pass the row validators, and languages values python, typescript and none are accepted.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_llm.py:54; plugins/arch-compliance/python/acf/registry.py:61`
- **C54** [implementability] [load-bearing]: Mandate already has auditor and params fields, so rule ids in auditor and rule settings in flat params need no plugin schema change.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:61-62`
- **C55** [implementability] [load-bearing]: RepoTree's contained, file and directory exist, and a RepoTree.files built on pathlib.Path.glob gives `**` the zero-or-more-directories meaning on the Python 3.11 floor (pyproject requires-python >=3.11).
  - spec citation: `plugins/arch-compliance/python/acf/repo.py:53-73; §4.7 step 2`
- **C56** [implementability] [load-bearing]: acf.diff.run_git returns the exit status as data (check=False) and lets a missing git raise, so staleness can tell 'commit not in history' from 'git missing'.
  - spec citation: `plugins/arch-compliance/python/acf/diff.py:17-30`
- **C57** [implementability] [load-bearing]: The extraction in adr/parser.py:26-60 can move into extract_json_block(payload, *, subject, error) with parse_reviewer_payload passing ReviewerContractViolationError, leaving the ADR parser tests and test_adr_exceptions.py passing.
  - spec citation: `plugins/arch-compliance/python/acf/adr/parser.py:26-60; plugins/arch-compliance/tests/test_adr_exceptions.py:24-45`
- **C58** [implementability] [load-bearing]: The origin dead-code ratchet's --update-baseline mode (dead_code_ratchet.py:493) regenerates the baseline from the edited tree, so the cutover PR can record the growth it states.
  - spec citation: `hm:scripts/ci/dead_code_ratchet.py:493`
- **C59** [implementability]: The forbidden-vocabulary test can be extended to the architecture-review skill directory and the YAML pack files.
  - spec citation: `plugins/arch-compliance/tests/test_adr_skill_prose.py`
- **C60** [implementability] [load-bearing]: The origin llm_judge caller at :293 has the row's mandate id in scope, so it can map §5 and §6 to prompt names in one dict.
  - spec citation: `hm:scripts/ci/arch_compliance/llm_judge.py:293`
