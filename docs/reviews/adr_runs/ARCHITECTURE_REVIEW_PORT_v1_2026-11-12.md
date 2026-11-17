# Adversarial design review — full detail

Spec: `docs/design/ARCHITECTURE_REVIEW_PORT.md` @ `66860696e2913d797bb627fde8dfc5b64a962b36`
Kinds: feature
Outcome: **BLOCKED**
Claims: 51 · Reviewers: 4 · Converged: 4

## Blocking reasons

- load-bearing claim C8 (premise) is REFUTED: No other dual-installed origin skill remains at b2611977f. .cursor/skills/ contains only architecture-review. post-merge-housekeeping exists only under .claude/ and never mentions skill_install. The two gate skills that were mirrored were deleted in 1d (remediation :6226-6229). The only importers of scripts.core.skill_install are scripts/core/architecture_review/__init__.py:10, which the spec deletes, and tests/test_skill_install.py. After the cutover, skill_install.py has no live consumer.
- load-bearing claim C12 (premise) is REFUTED: The cited follow-up covers only Cursor copies of adversarial-design-review and responding-to-adversarial-review, the 'gate'. It says nothing about architecture-review. Phase 1d's out-of-scope decision was about those two gate skills. Deleting hm:.cursor/skills/architecture-review/ removes Cursor's only architecture-review copy, and no filed follow-up covers that loss.
- load-bearing claim C15 (deletion) is REFUTED: No code reads the four files besides the skill: judge.py uses judge_prompt.md, and hooks, tests and other skills do not reference auditors/. But this repository's own registry row soft.react-boundaries (config/architecture/mandates.yml:51) names `auditor: react-boundaries`, which today resolves to auditors/react-boundaries.md. §6 changes only the two profiles, not config/architecture/mandates.yml. Once the file is deleted and §4.5 makes any non-rule-id value an UnknownMandateError, this repo's own row is a stranded consumer.
- load-bearing claim C16 (deletion) is REFUTED: Live origin readers remain that §5.4 and §5.6 neither repoint nor delete. tests/test_ui_logic_prepass.py:2 imports scripts.core.architecture_review.ui_logic_prepass, which moves under scripts/ci. tests/test_skill_install.py:28-41 asserts the real .claude and .cursor architecture-review trees and their auditors/ files exist. tests/test_arch_llm_judge.py:49-58 builds skill auditors dirs to test load_rubric. scripts/ci/arch_compliance/judge_calibration.py:61-62 calls load_rubric('three-tier-hfsm' / 'ui-logic-isolation'), which reads the deleted skill tree.
- load-bearing claim C17 (deletion) is REFUTED: The format matches: acf.baseline.Baseline has the same generated_at, commit, invocation and counts shape, keyed on mandate_id. But baseline_staleness catches the origin's scripts.core.exceptions.BaselineError (:88, :99), while acf.baseline.load_baseline raises AcfInputError through load_model_file. Repointed as the spec says, a malformed baseline crashes main() instead of printing NOTE and returning 0, which breaks the contract pinned by tests/test_baseline_staleness.py:58-67. In addition, acf is in neither hm requirements.txt nor requirements-lint.txt, so the import fails in origin CI.
- load-bearing claim C19 (mandate) is UNPROVEN: As written, the doctrine section governs only the adversarial-design-review gate's adr.yml. It records each default elsewhere in the package by name: 'Three defaults elsewhere in the package are outside this rule and recorded here'. The design fails loud on a missing review.yml (spec:133), which is consistent with the rule. But it also adds new defaults that the spec only asserts are not stand-ins: (a) a built-in exclusion list whose contents the spec never states and which the host does not declare (spec:154); (b) acf-mandate assuming doctrine_docs is empty, using ARCH_REL alone, when review.yml is absent (spec:147); (c) the first-segment subsystem rule when the list is empty; (d) surface absent meaning the whole tree. §6 does not extend the section to review.yml and does not record these defaults, as the section's convention requires. So the claim that none of them is 'a default standing in for a missing declaration' rests on argument, not on doctrine text. Case (b) in particular is a value assumed when the declaration is missing.
- load-bearing claim C21 (mandate) is UNPROVEN: The doctrine (ARCHITECTURE.md:127-131) makes RepoTree 'the one place runtime code turns a path string into a location in the host repository'; callers 'never join, resolve or compare against the root themselves'. REVIEW_REL (spec:121) and the hatch via RepoTree.file (spec:140) comply. The design also turns many other host path strings into locations: report_dir, baseline_path, sidecar_path, doctrine_docs, a rule's docs and inventory, policy_files, and surface/surface_exclude globs. The spec says nothing about how any of these are resolved. RepoTree offers only contained/file/directory/key (repo.py:53-73), with no glob and no write-target method. So the spec does not establish whether the report/sidecar writes and surface globbing go through RepoTree or join against the root.
- load-bearing claim C22 (mandate) is REFUTED: The doctrine requires one canonical implementation for 'the same operation, constant set, or decision procedure' (ARCHITECTURE.md:267-269). The design introduces a second decision procedure for whether an anchor resolves. doctrine_section matches a heading equal to the anchor and fails on zero or more than one match (spec:146). missing_anchors, which acf-mandate keeps using, accepts any stripped line equal to the anchor, heading or not, with no uniqueness check (registry.py:221-223). Both run over the same document set, but they disagree. An anchor that appears in both ARCH_REL and a doctrine_docs file, or that appears as a non-heading line, passes acf-mandate validation and then fails the review. The absorption is also incomplete: this repository's own soft.react-boundaries row still has `auditor: react-boundaries` (mandates.yml:51). §6 changes only the profiles.
- load-bearing claim C23 (mandate) is UNPROVEN: Reserving the detectors slot without building it complies: the model refuses the key (spec:106). The second half, that every new export has a live call site, is a universally quantified claim. The spec offers no recipe and names consumers for only some exports: parse_auditor_payload at step 6, REVIEW_REL and load_review_config at step 1. Nothing names the package or skill call site for ReviewRun, the rollup module, ReportWriteError, or which module renders the report. The no-completeness-claims rule (ARCHITECTURE.md:230-233) also applies here.
- load-bearing claim C29 (shape_fit) is REFUTED: I checked each ReviewHostConfig field against the host values that already exist. report_dir, baseline_path, sidecar_path and exclude are new and follow the AdrHostConfig shape (host.py:19-25). doctrine_docs is not new. It is a second declaration of the doctrine document set. The ADR host contract says the doctrine is 'not declared: it is ARCH_REL and the documents that file points to' (host.py:4-6). The approved ADR_GATE_HOST_CONTRACT.md decision 5 says 'No doctrine field is declared. A host whose doctrine lives elsewhere writes that file as a pointer' (:79-82). HM's ARCHITECTURE.md is that pointer, and it already names GEMINI.md (:5). Spec §5.3 then declares doctrine_docs: [GEMINI.md] again in review.yml, so the same list is held in two places that can drift apart. 'packs' also overlaps the per-row Mandate.languages (registry.py:16,56); see C34. So the claim that review.yml is 'not a second way to declare host values' fails on doctrine_docs.
- load-bearing claim C30 (shape_fit) is REFUTED: The two models do not serve different consumers today. The current review skill already maps auditor findings into acf.finding.Finding (SKILL.md:108: 'Map auditor findings into shared acf.finding.Finding rows'). acf.baseline.aggregate already consumes Finding (baseline.py:59-65). So the review and its drift baseline are consumers of Finding now. The design adds AuditorFinding for that same consumer and moves baseline over to it. The consumers only look different after this design creates the split. Both models share one job: recording one mandate-attributed violation at a POSIX file and line with a severity and a message (mandate_id/path/line/message/severity vs mandate_id/file/line/why/severity). §4.8 gives no written reason for not merging them.
- load-bearing claim C34 (shape_fit) is REFUTED: The plugin already says which technology a rule applies to in two places. Mandate.languages ('python'|'typescript'|'both'|'none', registry.py:16,56) filters rows per file language (detectors/host.py:192). The gate maps file suffix to language at cli_check_diff.py:152 ('.py') and :188 ({'.ts','.tsx'}). Packs add a third mapping from technology to files, reusing the same ids 'python' and 'typescript' with different extents: the review's typescript pack covers .js/.jsx/.mjs/.cjs, while the gate's 'typescript' covers only .ts/.tsx. The spec never says how a row's languages relates to the declared packs. In §4.7 step 4, every declared pack's hints for the rule are scanned regardless of the row's languages. A row with languages: python (as §5.1 gives every HM row) would therefore still get TypeScript candidates. That is a partial overlap, not a new concept.
- load-bearing claim C36 (sweep) is REFUTED: I grepped `auditor` outside docs/. This repository's own registry carries `auditor: react-boundaries` (config/architecture/mandates.yml:51, row soft.react-boundaries) and `auditor: fail-loud` (:142). The first is no longer a rule id once react-boundaries is absorbed. §4.5 joins every row that has an auditor, with no status filter, so this unenforced row raises UnknownMandateError on a review of this repository. config/architecture/mandates.yml is not in the §6 change surface. acf-mandate SKILL.md:47 also documents `auditor` as a 'Tier-3 auditor name', which goes stale. So the consumers are not limited to the skill and the two profile rows.
- load-bearing claim C38 (sweep) is REFUTED: I grepped missing_anchors. Besides acf-mandate SKILL.md:99, it is called with a single string at tests/test_self_host.py:40, plugins/arch-compliance/tests/test_profile_drift.py:30 and test_registry.py:60. A str is itself a Sequence[str], so after the change each character becomes its own 'text' and every anchor is reported missing. Those calls must change too. Separately, acf-setup SKILL.md:138-139 states the anchor contract in prose ('matched as literal substrings of ARCHITECTURE.md'). The doctrine records that skill as a by-eye anchor check that should be a missing_anchors caller (ARCHITECTURE.md:275-276). §4.6 moves the contract to ARCH_REL plus doctrine_docs, but §6 changes acf-setup only to write review.yml. The change does not touch only the one snippet.
- load-bearing claim C40 (sweep) is REFUTED: I grepped gemini_anchor across the whole HM checkout, not just scripts/ and tests/. config/architecture/dead_code_baseline.json:195 lists 'scripts/core/architecture/registry.py::MandateEntry.gemini_anchor' in the test_only lane (the lane opens at :151). That file is the floor for the dead-code ratchet (dead_code_ratchet.py:323). compare_lanes scores any new test_only key as growth (:379-381). After the rename, MandateEntry.arch_anchor is a new key and the stale entry departs. So a ratchet reads the field from config/, and the recipe's exclusion of config/ is not justified. :196-198 also list architecture_review/baseline.py symbols that §5.6 deletes; that is a shrink and is tolerated.
- load-bearing claim C50 (implementability) is REFUTED: The origin environments do not install acf. arch-guards.yml:36 installs only pyyaml, pydantic, pytest, pytest-timeout and requirements-lint.txt. regression-tests.yml installs requirements.txt, which names no acf or arch-compliance package. `git grep 'from acf|import acf' -- scripts tests` at b2611977f returns nothing. baseline_staleness.py is exercised by hm:tests/test_baseline_staleness.py:58-67 (test_main_never_crashes_on_malformed_baseline calls main() on a malformed baseline, which reaches the deferred import at :87). Repointed to acf.baseline, that test raises ModuleNotFoundError in CI. Even where acf is importable, the module catches `BaselineError` (hm import at :88). acf.baseline.load_baseline raises AcfInputError, not BaselineError (baseline.py:82-86), so a malformed baseline now crashes main(). The test asserts it never crashes. The pre-push hook runs it under `|| true` (hm:scripts/setup_git_hooks.py:138), so the breakage there would be silent.
- mandate claim C22 is REFUTED: The doctrine requires one canonical implementation for 'the same operation, constant set, or decision procedure' (ARCHITECTURE.md:267-269). The design introduces a second decision procedure for whether an anchor resolves. doctrine_section matches a heading equal to the anchor and fails on zero or more than one match (spec:146). missing_anchors, which acf-mandate keeps using, accepts any stripped line equal to the anchor, heading or not, with no uniqueness check (registry.py:221-223). Both run over the same document set, but they disagree. An anchor that appears in both ARCH_REL and a doctrine_docs file, or that appears as a non-heading line, passes acf-mandate validation and then fails the review. The absorption is also incomplete: this repository's own soft.react-boundaries row still has `auditor: react-boundaries` (mandates.yml:51). §6 changes only the profiles.
- mandate claim C28 is REFUTED: The claim covers 'any origin doctrine that governs the origin-stage changes of §5'. The origin repository's CLAUDE.md:128 governs a spec that deletes or relocates anything there. It requires the spec to write its consumer census, 'with the grep recipes recorded in the spec … before drafting the design section'. §5.6 deletes the origin skill trees and most of scripts/core/architecture_review, and moves ui_logic_prepass. The spec neither quotes nor follows this rule: §5.6 has no census recipe, and it misses live consumers (tests/test_skill_install.py:28-35 asserts the deleted skill tree exists).
- implementability claim C50 is REFUTED: The origin environments do not install acf. arch-guards.yml:36 installs only pyyaml, pydantic, pytest, pytest-timeout and requirements-lint.txt. regression-tests.yml installs requirements.txt, which names no acf or arch-compliance package. `git grep 'from acf|import acf' -- scripts tests` at b2611977f returns nothing. baseline_staleness.py is exercised by hm:tests/test_baseline_staleness.py:58-67 (test_main_never_crashes_on_malformed_baseline calls main() on a malformed baseline, which reaches the deferred import at :87). Repointed to acf.baseline, that test raises ModuleNotFoundError in CI. Even where acf is importable, the module catches `BaselineError` (hm import at :88). acf.baseline.load_baseline raises AcfInputError, not BaselineError (baseline.py:82-86), so a malformed baseline now crashes main(). The test asserts it never crashes. The pre-push hook runs it under `|| true` (hm:scripts/setup_git_hooks.py:138), so the breakage there would be silent.
- [hardening] §5.4 repoints hm baseline_staleness.py to acf.baseline.load_baseline, but no origin CI job installs acf. The origin test that calls main() (test_main_never_crashes_on_malformed_baseline) would fail with ModuleNotFoundError, and the spec states no step that makes acf importable in origin CI. (hm:.github/workflows/arch-guards.yml:36; hm:tests/test_baseline_staleness.py:58; hm:scripts/ci/baseline_staleness.py:87)

## Absorptions

- PARTIAL_OVERLAP: 'ReviewHostConfig.doctrine_docs' shares responsibility 'declare the set of doctrine documents beyond ARCH_REL' with plugins/arch-compliance/python/acf/adr/host.py:4 — One owner of the doctrine set: either the ARCH_REL pointer list, read by a shared acf helper that both the review and the ADR gate consume (and acf-mandate through missing_anchors), or a declared doctrine_docs that the ADR gate also reads, with ADR decision 5 amended on the record. Not both.
- PARTIAL_OVERLAP: 'acf.review.aggregator.parse_auditor_payload' shares responsibility "extract exactly one fenced json block from an agent's final message, parse it and validate it against a strict model" with plugins/arch-compliance/python/acf/adr/parser.py:53 — Extract the fence regex, the zero/many-block check and the JSON decode into one acf helper (for example acf.agent_payload.extract_json_block(payload, subject) raising a single base contract-violation error). parse_reviewer_payload and parse_auditor_payload become consumers that keep only their own policy: identity check plus abort, vs FAILED group.
- PARTIAL_OVERLAP: 'AuditorContractViolationError' shares responsibility 'signal that an agent payload breaks its dispatched contract' with plugins/arch-compliance/python/acf/exceptions.py:45 — One AgentContractViolationError (or reuse ReviewerContractViolationError renamed) raised by the shared extractor, with each skill's policy at its call site.
- PARTIAL_OVERLAP: 'acf.review.contract.AuditorFinding' shares responsibility 'record one mandate-attributed violation at a POSIX file:line with a severity and a message' with plugins/arch-compliance/python/acf/finding.py:11 — Keep aggregate typed on a minimal shared shape, (mandate_id, path) as a Protocol or a projection to Finding, so baseline does not fork per finding model. AuditorFinding keeps its review-only fields (snippet, why, suggested_fix, four-level severity) and state in the spec why Finding is not reused, since the current skill already maps into it.
- PARTIAL_OVERLAP: 'acf.review.packs.TechPack.files and ReviewHostConfig.packs' shares responsibility 'decide which files belong to a technology and which technology a rule applies to' with plugins/arch-compliance/python/acf/registry.py:16 — One technology vocabulary: pack ids as the canonical language ids, with the pack `files` globs as the single file-to-technology map that the gate's suffix routing (cli_check_diff.py:152,188) and Mandate.languages filtering (detectors/host.py:192) also consume. Or state in the spec how a row's languages narrows the packs whose hints it receives.
- PARTIAL_OVERLAP: 'single-owner / state-machine-discipline settings under params.review' shares responsibility 'declare a protected artifact and its owners; declare the state field and its transition validator' with config/architecture/mandates.yml:112 — One declaration of each host value, read by both the AST detector and the review rule. For example, the rule's settings model reads the detector's params keys, or the detector row carries `auditor` and the review derives its settings from the same params, instead of a parallel params.review copy.
- SUBSUMED: 'acf.baseline.aggregate over AuditorFinding; subsystem_of with declared prefixes' shares responsibility 'fold findings into (mandate_id, subsystem) counts' with plugins/arch-compliance/python/acf/baseline.py:59 — Extend in place, as the spec does. The prefix rule generalises the first-segment rule, with no sibling module.
- PARTIAL_OVERLAP: 'acf.review.prepass' shares responsibility 'scan lines with regex tells and emit file:line [tell] snippet candidates' with hm:scripts/core/architecture_review/ui_logic_prepass.py:55 — After cutover, the gate-owned HM staged check should consume acf.review.prepass with the plugin's packs rather than keep its own _TELLS copy. Otherwise name the duplicate tell set and its owner until part two.
- PARTIAL_OVERLAP: 'ReportWriteError' shares responsibility 'fail loud when a review record cannot be persisted' with plugins/arch-compliance/python/acf/baseline.py:68 — One write helper (mkdir parents, write_text utf-8, wrap OSError with the POSIX path) consumed by save_baseline, write_run_detail and the new report and sidecar writers. Each may keep its own subject string.
- ADJACENT exclusion of plugins/arch-compliance/python/acf/adr/rollup.py:1 for responsibility 'render a terminal roll-up of a run' is unjustified in writing

## Converged findings

- [3 reviewers: refuter, compliance, sweeper] This repository's own registry row soft.react-boundaries keeps `auditor: react-boundaries`; config/architecture/mandates.yml is missing from the §6 change surface, so after the absorption §4.5 raises UnknownMandateError on this repository's own review.
  - evidence: `config/architecture/mandates.yml:51`
- [2 reviewers: refuter, hardening] Repointing hm baseline_staleness.py to acf.baseline.load_baseline breaks it: the origin repository does not install acf in CI, and acf raises AcfInputError where the module catches the origin BaselineError, so tests/test_baseline_staleness.py:58-67 fails.
  - evidence: `hm:scripts/ci/baseline_staleness.py:87`
  - evidence: `hm:tests/test_baseline_staleness.py:58`
  - evidence: `plugins/arch-compliance/python/acf/baseline.py:82`
- [2 reviewers: refuter, compliance] The §5.4/§5.6 origin deletion and move list has no consumer census and misses live consumers: tests/test_skill_install.py asserts the deleted skill trees, tests/test_ui_logic_prepass.py imports the moved module.
  - evidence: `hm:tests/test_skill_install.py:28-41`
  - evidence: `hm:tests/test_ui_logic_prepass.py:2`
- [2 reviewers: compliance, hardening] The review adds defaults that `## Declared, never defaulted` does not record, notably acf-mandate using ARCH_REL alone when review.yml is absent.
  - evidence: `config/architecture/ARCHITECTURE.md:187-203`
  - evidence: `docs/design/ARCHITECTURE_REVIEW_PORT.md:147`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/skills/architecture-review/SKILL.md:72; plugins/arch-compliance/skills/architecture-review/SKILL.md:35-38`
- reasoning: At 66860696, SKILL.md:72 lists the default auditors as fail-loud, no-shims, posix-paths and react-boundaries. Lines 35-38 load exactly those four prompt files, and the auditors/ directory holds only those four .md files (I listed it).

#### C2 — SURVIVED
- evidence: `hm:.claude/skills/architecture-review/SKILL.md:35-47,53-61,68,80-88,123-145,154-156; hm:scripts/core/architecture_review/ui_logic_prepass.py:65`
- reasoning: In git show b2611977f, step 1 is the rubric step (extract_gemini_rubric plus the manifest). Lines 53-61 define the frontend and family-template surfaces. Line 68 dispatches 'default = all nine', and ls-tree shows nine auditor .md files. Lines 80-88 hold the §6 deterministic pre-pass, which ui_logic_prepass.py:65 resolve_frontend_files implements. Lines 123-145 hold the blame provenance and lines 154-156 the _last_run.json sidecar.

#### C3 — SURVIVED
- evidence: `hm:.claude/skills/architecture-review/auditors/metadata-facade.md:3; hm:.claude/skills/architecture-review/auditors/output-agnosticism.md:12-25; hm:.claude/skills/architecture-review/auditors/three-tier-hfsm.md:11-13`
- reasoning: metadata-facade.md:3 hard-codes ContentMetadataService and index.yml. output-agnosticism.md:12-25 hard-codes the stage-1 and stage-2 file lists. three-tier-hfsm.md:11-13 hard-codes the origin tier path lists and BookSession. All of these are origin-specific values.

#### C4 — SURVIVED
- evidence: `hm:scripts/ci/arch_compliance/llm_judge.py:91-93; hm:scripts/ci/baseline_staleness.py:87; hm:scripts/ci/check_ui_prepass_staged.py:17`
- reasoning: I ran `git grep -n architecture_review b2611977f -- scripts/ci`. It returns exactly those three files. Outside scripts/ci, no non-test, non-doc code imports the package; the only reader is the prose pointer at hm:config/architecture/ARCHITECTURE.md:9, which the spec handles. One caveat goes beyond the importer count: scripts/ci/arch_compliance/judge_calibration.py:56-62 reads the skill tree indirectly through load_rubric (reported as an unanchored finding).

#### C5 — SURVIVED
- evidence: `hm:scripts/core/architecture/registry.py:21-34; hm:scripts/core/architecture/registry.py:79`
- reasoning: MandateEntry has extra='forbid' and fields id through remediation, including gemini_anchor. It has no languages, params or arch_anchor field. load_mandates validates every row through MandateEntry.model_validate at :79, so an unknown key raises MandateRegistryError.

#### C6 — SURVIVED
- evidence: `hm:docs/architecture/compliance_baseline.json; hm:scripts/core/architecture_review/baseline.py:31-35,62-69`
- reasoning: The baseline has 23 cells keyed on free-text labels such as 'Three-Tier/HFSM' and '§3 Fail-Loud'. baseline.py:67 keys on result.mandate (the auditor label). My yaml.safe_load run shows three-tier-hfsm is the auditor on six rows (three-tier, three-tier-batch, three-tier-ambient, §5, §5-fsm-mechanism, path-provenance), so its counts cannot be split per mandate id.

#### C7 — SURVIVED
- evidence: `hm:config/architecture/mandates.yml (yaml.safe_load at b2611977f); hm:scripts/core/architecture/registry.py:29`
- reasoning: I ran the recipe. 25 of 48 rows carry auditor, and the ids and auditor values match §5.2 row for row: §3 and §3-exception-base fail-loud; §4 and §4-mansion-slug-wire no-shims; three §10 rows posix-paths; six three-tier-hfsm rows; §11 and §11-inventory metadata-facade; four §12 rows output-agnosticism; §13 schema-presentation; §6 plus the two admin rows ui-logic-isolation; §14 and §14-size class-cohesion.

#### C8 — REFUTED
- evidence: `git ls-tree b2611977f .cursor/skills/ (architecture-review only); hm:scripts/core/architecture_review/__init__.py:10; hm:tests/test_skill_install.py:7; hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:6228-6233`
- reasoning: No other dual-installed origin skill remains at b2611977f. .cursor/skills/ contains only architecture-review. post-merge-housekeeping exists only under .claude/ and never mentions skill_install. The two gate skills that were mirrored were deleted in 1d (remediation :6226-6229). The only importers of scripts.core.skill_install are scripts/core/architecture_review/__init__.py:10, which the spec deletes, and tests/test_skill_install.py. After the cutover, skill_install.py has no live consumer.

#### C9 — SURVIVED
- evidence: `hm:.claude/skills/architecture-review/SKILL.md:53-61; hm:scripts/core/architecture_review/ui_logic_prepass.py:65-80`
- reasoning: resolve_frontend_files(repo_root) takes no glob argument, so --paths (which SKILL.md:24 says replaces only the **/*.py include) never reaches it. The code excludes only /vendor/. The prose global exclusions (dist/, build/, worktrees/ and similar) are root-level prefixes, so no file under admin/ can match them, and the effective behaviour equals 'kept the global exclusions'.

#### C10 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:19; plugins/arch-compliance/python/acf/judge.py:259-266; plugins/arch-compliance/python/acf/judge_prompt.md:1-6`
- reasoning: The judge's only prompt source is judge_prompt.md (judge.py:19), filled with mandate id, title, severity, detector and arch_anchor (:259-266). judge.py never reads mandate.auditor or any auditors/ file. A grep for 'auditor' in judge.py returns nothing, and llm_react_boundaries appears only in LLM_PROMPT_IDS (:31).

#### C11 — SURVIVED
- evidence: `cy:cayenne-web/src/lib/features/bugReport/BugReportSheetBody.svelte:41-42; grep 'svelte' plugins/arch-compliance/python (no hits)`
- reasoning: In raw .svelte text, the <script> body and its domain computations (for example $derived(message.trim() === '') at :41) sit inline, so line regexes and a Read-only agent can see them without extraction. The plugin has no svelte-aware code today, and the spec adds no deterministic detector, so nothing in this spec needs script-block extraction.

#### C12 — REFUTED
- evidence: `hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:360; hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:6474-6476`
- reasoning: The cited follow-up covers only Cursor copies of adversarial-design-review and responding-to-adversarial-review, the 'gate'. It says nothing about architecture-review. Phase 1d's out-of-scope decision was about those two gate skills. Deleting hm:.cursor/skills/architecture-review/ removes Cursor's only architecture-review copy, and no filed follow-up covers that loss.

#### C13 — SURVIVED
- evidence: `hm:scripts/ci/arch_compliance/llm_judge.py:88-98; hm:scripts/ci/arch_compliance/llm_judge.py:288-293; hm:scripts/ci/arch_compliance/judge_calibration.py:61-62`
- reasoning: load_rubric only builds <dir>/<name>.md and reads it. Its production caller judge_changed_file has mandate.id (duck-typed .id at :288). The other caller, judge_calibration, has case['mandate'] (the mandate id §5/§6). Re-keying is therefore feasible. However, judge_calibration currently hard-codes auditor names, and §5.4 does not list it (reported as an unanchored finding).

#### C14 — SURVIVED
- evidence: `hm:config/architecture/ARCHITECTURE.md:8-9; hm:.claude/skills/architecture-review/SKILL.md:45-47`
- reasoning: ARCHITECTURE.md:8-9 names `.claude/skills/architecture-review/rubric/arch-docs-manifest.yml` as the list of architecture documents to read. That file lives inside the deleted skill tree (SKILL.md:46 loads it), so the pointer must move with it.

#### C15 — REFUTED
- evidence: `config/architecture/mandates.yml:41-51; plugins/arch-compliance/skills/architecture-review/SKILL.md:72-80`
- reasoning: No code reads the four files besides the skill: judge.py uses judge_prompt.md, and hooks, tests and other skills do not reference auditors/. But this repository's own registry row soft.react-boundaries (config/architecture/mandates.yml:51) names `auditor: react-boundaries`, which today resolves to auditors/react-boundaries.md. §6 changes only the two profiles, not config/architecture/mandates.yml. Once the file is deleted and §4.5 makes any non-rule-id value an UnknownMandateError, this repo's own row is a stranded consumer.

#### C16 — REFUTED
- evidence: `hm:tests/test_ui_logic_prepass.py:2; hm:tests/test_skill_install.py:18,28-41; hm:tests/test_arch_llm_judge.py:49-58; hm:scripts/ci/arch_compliance/judge_calibration.py:56-62`
- reasoning: Live origin readers remain that §5.4 and §5.6 neither repoint nor delete. tests/test_ui_logic_prepass.py:2 imports scripts.core.architecture_review.ui_logic_prepass, which moves under scripts/ci. tests/test_skill_install.py:28-41 asserts the real .claude and .cursor architecture-review trees and their auditors/ files exist. tests/test_arch_llm_judge.py:49-58 builds skill auditors dirs to test load_rubric. scripts/ci/arch_compliance/judge_calibration.py:61-62 calls load_rubric('three-tier-hfsm' / 'ui-logic-isolation'), which reads the deleted skill tree.

#### C17 — REFUTED
- evidence: `hm:scripts/ci/baseline_staleness.py:87-104; plugins/arch-compliance/python/acf/baseline.py:78-86; plugins/arch-compliance/python/acf/loader.py:61-73; hm:tests/test_baseline_staleness.py:58-67`
- reasoning: The format matches: acf.baseline.Baseline has the same generated_at, commit, invocation and counts shape, keyed on mandate_id. But baseline_staleness catches the origin's scripts.core.exceptions.BaselineError (:88, :99), while acf.baseline.load_baseline raises AcfInputError through load_model_file. Repointed as the spec says, a malformed baseline crashes main() instead of printing NOTE and returning 0, which breaks the contract pinned by tests/test_baseline_staleness.py:58-67. In addition, acf is in neither hm requirements.txt nor requirements-lint.txt, so the import fails in origin CI.

### Unanchored findings

- **important**: This repository's own registry keeps `auditor: react-boundaries` and has no review.yml. Neither is in the §6 change surface, so after 0.3.0 the plugin's own /architecture-review fails with UnknownMandateError or a missing review.yml.
  - evidence: `config/architecture/mandates.yml:51`
- **important**: judge_calibration.py, a fourth scripts/ci consumer of the skill auditors directory (through load_rubric), hard-codes the auditor names 'three-tier-hfsm' and 'ui-logic-isolation'. §5.4 does not list it, so it breaks when the prompts are re-keyed by mandate id and the skill tree is deleted.
  - evidence: `hm:scripts/ci/arch_compliance/judge_calibration.py:61-62`
- **important**: The origin Python environment does not install acf (absent from requirements.txt, requirements-lint.txt and the arch-guards workflow pip line). Repointing baseline_staleness to acf.baseline makes the pre-push hook and tests/test_baseline_staleness.py depend on a package that origin CI lacks, and the spec does not say how acf gets there.
  - evidence: `hm:.github/workflows/arch-guards.yml:36`
- **advisory**: The svelte pack's hint source is `$:` reactive statements, but Cayenne uses Svelte 5 runes: zero `$:` lines and 111 files with `$derived`. The pack as described would miss Cayenne's actual reactive domain computations.
  - evidence: `cy:cayenne-web/src/lib/features/bugReport/BugReportSheetBody.svelte:41`
- **advisory**: Deleting the review package orphans the origin's ArchitectureReviewError family (RubricMissingError, AuditorFailedError and others) and their entries in engine.py's exception list. It also leaves stale baseline entries for deleted paths (debt_baseline.json scripts/core/architecture_review/contract.py, dead_code_baseline.json :44-46,196-201). §5.6 does not address any of these.
  - evidence: `hm:scripts/core/exceptions.py:1241-1280`
- **advisory**: §5.2 sets the §13 surface to `templates/families/**`, which is broader than the origin family set (only *.tex, *.css and */style.yml), so the port changes the auditor's file surface. In addition, the origin subsystem_of returns 'other' for unmatched paths, and the spec does not say what a non-empty prefix list does for unmatched paths.
  - evidence: `hm:.claude/skills/architecture-review/SKILL.md:58-61`

### Looked for but did not find

- Any reference to plugins/arch-compliance/skills/architecture-review/auditors/ from judge.py, hooks, tests or other skills (grep 'auditors' outside the skill: none)
- A second dual-installed origin skill under hm:.cursor/skills/ at b2611977f (only architecture-review is present)
- An import of scripts.core.architecture_review in hm .github workflows, pyproject.toml, pytest.ini or setup_git_hooks.py
- An acf dependency anywhere in hm requirements*.txt or pyproject.toml
- Any reading of mandate.auditor inside the plugin judge (judge.py, judge_prompt.md)

## compliance

### Claim verdicts

#### C18 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_skill_prose.py:13-25; docs/design/ARCHITECTURE_REVIEW_PORT.md:88; docs/design/ARCHITECTURE_REVIEW_PORT.md:253; docs/design/ARCHITECTURE_REVIEW_PORT.md:269`
- reasoning: ARCHITECTURE.md:206-212 says skill prose names no host repository, path or section, and that test_adr_skill_prose.py enforces this today for the two gate skills and post-merge-housekeeping only. The design says rule prompts carry no repository values; every value arrives through the row's settings (§4.2). §6 and §7 extend the explicit FILES/FORBIDDEN check (test_adr_skill_prose.py:13-25) to architecture-review, and rules/ sits under that skill. The claim holds as scoped. A coverage gap outside its scope, the pack files, is filed separately.

#### C19 — UNPROVEN
- evidence: `config/architecture/ARCHITECTURE.md:189-202; docs/design/ARCHITECTURE_REVIEW_PORT.md:133; docs/design/ARCHITECTURE_REVIEW_PORT.md:147; docs/design/ARCHITECTURE_REVIEW_PORT.md:154`
- reasoning: As written, the doctrine section governs only the adversarial-design-review gate's adr.yml. It records each default elsewhere in the package by name: 'Three defaults elsewhere in the package are outside this rule and recorded here'. The design fails loud on a missing review.yml (spec:133), which is consistent with the rule. But it also adds new defaults that the spec only asserts are not stand-ins: (a) a built-in exclusion list whose contents the spec never states and which the host does not declare (spec:154); (b) acf-mandate assuming doctrine_docs is empty, using ARCH_REL alone, when review.yml is absent (spec:147); (c) the first-segment subsystem rule when the list is empty; (d) surface absent meaning the whole tree. §6 does not extend the section to review.yml and does not record these defaults, as the section's convention requires. So the claim that none of them is 'a default standing in for a missing declaration' rests on argument, not on doctrine text. Case (b) in particular is a value assumed when the declaration is missing.

#### C20 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/exceptions.py:1; plugins/arch-compliance/python/acf/exceptions.py:45; docs/design/ARCHITECTURE_REVIEW_PORT.md:166`
- reasoning: ARCHITECTURE.md:110 reads 'Every ACF exception subclasses `AcfError` and nothing else'. The spec declares both new exceptions as 'each subclassing `AcfError` only' (spec:166). The parallel ReviewerContractViolationError(AcfError) at exceptions.py:45 shows the pattern is established. EmptyTargetTreeError and UnknownMandateError, which the design also uses, already exist as AcfError subclasses (exceptions.py:9, :25).

#### C21 — UNPROVEN
- evidence: `plugins/arch-compliance/python/acf/repo.py:47-73; docs/design/ARCHITECTURE_REVIEW_PORT.md:121; docs/design/ARCHITECTURE_REVIEW_PORT.md:125-131; docs/design/ARCHITECTURE_REVIEW_PORT.md:140`
- reasoning: The doctrine (ARCHITECTURE.md:127-131) makes RepoTree 'the one place runtime code turns a path string into a location in the host repository'; callers 'never join, resolve or compare against the root themselves'. REVIEW_REL (spec:121) and the hatch via RepoTree.file (spec:140) comply. The design also turns many other host path strings into locations: report_dir, baseline_path, sidecar_path, doctrine_docs, a rule's docs and inventory, policy_files, and surface/surface_exclude globs. The spec says nothing about how any of these are resolved. RepoTree offers only contained/file/directory/key (repo.py:53-73), with no glob and no write-target method. So the spec does not establish whether the report/sidecar writes and surface globbing go through RepoTree or join against the root.

#### C22 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/registry.py:220-223; docs/design/ARCHITECTURE_REVIEW_PORT.md:146-147; config/architecture/mandates.yml:51`
- reasoning: The doctrine requires one canonical implementation for 'the same operation, constant set, or decision procedure' (ARCHITECTURE.md:267-269). The design introduces a second decision procedure for whether an anchor resolves. doctrine_section matches a heading equal to the anchor and fails on zero or more than one match (spec:146). missing_anchors, which acf-mandate keeps using, accepts any stripped line equal to the anchor, heading or not, with no uniqueness check (registry.py:221-223). Both run over the same document set, but they disagree. An anchor that appears in both ARCH_REL and a doctrine_docs file, or that appears as a non-heading line, passes acf-mandate validation and then fails the review. The absorption is also incomplete: this repository's own soft.react-boundaries row still has `auditor: react-boundaries` (mandates.yml:51). §6 changes only the profiles.

#### C23 — UNPROVEN
- evidence: `config/architecture/ARCHITECTURE.md:224-226; docs/design/ARCHITECTURE_REVIEW_PORT.md:106; docs/design/ARCHITECTURE_REVIEW_PORT.md:158; docs/design/ARCHITECTURE_REVIEW_PORT.md:242`
- reasoning: Reserving the detectors slot without building it complies: the model refuses the key (spec:106). The second half, that every new export has a live call site, is a universally quantified claim. The spec offers no recipe and names consumers for only some exports: parse_auditor_payload at step 6, REVIEW_REL and load_review_config at step 1. Nothing names the package or skill call site for ReviewRun, the rollup module, ReportWriteError, or which module renders the report. The no-completeness-claims rule (ARCHITECTURE.md:230-233) also applies here.

#### C24 — SURVIVED
- evidence: `pyproject.toml:3; plugins/arch-compliance/.claude-plugin/plugin.json:3; docs/design/ARCHITECTURE_REVIEW_PORT.md:256`
- reasoning: ARCHITECTURE.md:255-256: 'A change to a skill's prose bumps the plugin version in plugin.json and pyproject.toml'. Both files read 0.2.5 today, and §6 bumps both to 0.3.0. The claim is limited to the bump and holds. The installed-copy check half of the section is filed separately.

#### C25 — SURVIVED
- evidence: `docs/design/ARCHITECTURE_REVIEW_PORT.md:189; docs/design/ARCHITECTURE_REVIEW_PORT.md:193; docs/design/ARCHITECTURE_REVIEW_PORT.md:218; config/architecture/ARCHITECTURE.md:230-233`
- reasoning: Each of the three named populations carries a re-runnable recipe: `git grep -n gemini_anchor -- scripts tests`, yaml.safe_load filtered on auditor, and `git grep -n architecture_review -- scripts/ci`. My own search of the origin tree for gemini_anchor in code and tests found exactly the four files the spec lists. A separate problem is filed below: the §5.6 deletion population has no consumer census and misses live consumers.

#### C26 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:29; config/architecture/ARCHITECTURE.md:53-54; docs/design/ARCHITECTURE_REVIEW_PORT.md:158`
- reasoning: Fail loud: 'Errors must surface … Prefer explicit handling, rethrow, or reporting' (:28-29). No shims forbids logic that masks misalignment (:53-54). Under step 6 the violating group is marked FAILED, its raw payload and error are kept and reported, and any FAILED group makes the exit status non-zero (spec:158). The failure is surfaced and gates the run; no default stands in for the missing result. That is reporting, not a soft fallback.

#### C27 — UNPROVEN
- evidence: `config/architecture/ARCHITECTURE.md:59-66; docs/design/ARCHITECTURE_REVIEW_PORT.md:125-129; docs/design/ARCHITECTURE_REVIEW_PORT.md:164`
- reasoning: The doctrine requires persisted paths to be POSIX. This plugin is stricter and refuses a backslash through PosixStr (adr/contract.py:129). The spec labels the review.yml fields 'POSIX path' but names no type. The contract it ports (spec:164; the origin contract.py:30-34) validates only AuditorFinding.file. ReviewRun.target_root and exclusions, the sidecar fields, carry no POSIX validator in the origin. The spec says nothing about baseline cells or the report's path strings. So the design does not establish the claim for the report, sidecar or baseline.

#### C28 — REFUTED
- evidence: `hm:CLAUDE.md:128; hm:tests/test_skill_install.py:28-35; docs/design/ARCHITECTURE_REVIEW_PORT.md:234`
- reasoning: The claim covers 'any origin doctrine that governs the origin-stage changes of §5'. The origin repository's CLAUDE.md:128 governs a spec that deletes or relocates anything there. It requires the spec to write its consumer census, 'with the grep recipes recorded in the spec … before drafting the design section'. §5.6 deletes the origin skill trees and most of scripts/core/architecture_review, and moves ui_logic_prepass. The spec neither quotes nor follows this rule: §5.6 has no census recipe, and it misses live consumers (tests/test_skill_install.py:28-35 asserts the deleted skill tree exists).

### Unanchored findings

- **important**: Anchor resolution would have two implementations: acf-mandate's missing_anchors (any stripped line, no uniqueness check) and the review's doctrine_section (heading match, exactly once). A row can pass acf-mandate validation and then fail the review, which breaches Single point of definition.
  - evidence: `plugins/arch-compliance/python/acf/registry.py:220-223`
- **important**: §5 stage 1 relies on scripts/check_installed_skills.py to confirm the installed 0.3.0 architecture-review skill, but the script byte-checks only adversarial-design-review, responding-to-adversarial-review and post-merge-housekeeping (and never python/). The spec does not extend it, so the origin acceptance run has no drift check on the skill or package it exercises.
  - evidence: `scripts/check_installed_skills.py:18-21`
- **important**: This repository's own soft.react-boundaries row keeps `auditor: react-boundaries`. §6 rewrites only the two profiles, so after the auditors/ deletion this row names neither a rule id nor a .md prompt, and §4.5 turns that into UnknownMandateError.
  - evidence: `config/architecture/mandates.yml:51`
- **important**: The §5.6 origin deletions break live consumers the spec does not list. tests/test_skill_install.py:28-35 asserts .claude/skills/architecture-review/SKILL.md and auditors/ exist. tests/test_ui_logic_prepass.py:2 imports scripts.core.architecture_review.ui_logic_prepass, which §5.4 moves. No consumer census recipe backs the deletion list.
  - evidence: `hm:tests/test_skill_install.py:34`
- **important**: Declared text decoding is not addressed. The new provenance step runs git blame, a subprocess text read, and the package reads rule prompts, hatch prompts, doctrine_docs and pack files. The spec does not require encoding='utf-8', a doctrine high-frequency miss.
  - evidence: `config/architecture/ARCHITECTURE.md:242-244`
- **advisory**: Pack hints for the python pack are drawn from the origin auditors' 'Detection patterns' sections, which carry origin vocabulary (42 hits for HistoricMansions/scripts/core/GEMINI/index.yml/ContentMetadata across the nine origin auditors). The pack files live under python/acf/review/packs/, outside both no-host tests: test_adr_skill_prose scans the skills tree and test_adr_code_portability scans only acf/adr/*.py.
  - evidence: `plugins/arch-compliance/tests/test_adr_code_portability.py:7`
- **advisory**: The doctrine records the SKILL.md:62 `Path("config/architecture/mandates.yml")` breach under One owner for host paths and Single point of definition. The §4.7 rewrite removes that line, but §6's ARCHITECTURE.md edits do not retire these recorded breaches, so the doctrine would cite a line that no longer exists.
  - evidence: `config/architecture/ARCHITECTURE.md:121-125`
- **advisory**: Declared, never defaulted is scoped to adr.yml and lists each package default it excludes. §6 neither extends it to review.yml nor records the review's new defaults: the built-in exclusions, acf-mandate's ARCH_REL-only fallback and the empty-subsystems first-segment rule. Its row, plugin.declared-never-defaulted, still points only at test_adr_host.py.
  - evidence: `config/architecture/ARCHITECTURE.md:189-194`

### Looked for but did not find

- ## Build artifacts: the origin sidecar_path under build/ is written at runtime, not staged or committed; the plugin change surface adds no generated tree.
- ## Fail-loud ratchet, ## Façade sinks, ## FSM transitions: this design adds no detector rows and changes no ratchet baseline; pack `detectors` is reserved and refused by the model.
- ## Host detectors and call sites (Trust boundary): the hatch is Markdown read by read-only agents and the spec adds no repository-supplied executable code (decision 12, §4.9); no host ast/guard row is added.
- ## Frozen ledger format: no LedgerRow or LedgerAmendment field is touched.
- ## Soft fail-loud smells: this repository's soft.fail-loud row has auditor `fail-loud`, which stays a valid rule id; judge.py is out of scope (§3).
- ## Scoped refactor: plugin changes stay within the review, registry anchor helper, baseline and profiles that the feature needs.
- ## Post-merge: no change to the host's operational declarations.

### Unstated mandates

- ## Declared text decoding — the new provenance step (git blame, §4.7 step 7) is a subprocess text read, and the package reads prompt, doctrine and pack files. The rule requires encoding='utf-8' on each, and the spec's Governing mandates list omits the section.

## sweeper

### Claim verdicts

#### C29 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/adr/host.py:4 docs/design/ADR_GATE_HOST_CONTRACT.md:80 hm:config/architecture/ARCHITECTURE.md:5 plugins/arch-compliance/python/acf/registry.py:56`
- reasoning: I checked each ReviewHostConfig field against the host values that already exist. report_dir, baseline_path, sidecar_path and exclude are new and follow the AdrHostConfig shape (host.py:19-25). doctrine_docs is not new. It is a second declaration of the doctrine document set. The ADR host contract says the doctrine is 'not declared: it is ARCH_REL and the documents that file points to' (host.py:4-6). The approved ADR_GATE_HOST_CONTRACT.md decision 5 says 'No doctrine field is declared. A host whose doctrine lives elsewhere writes that file as a pointer' (:79-82). HM's ARCHITECTURE.md is that pointer, and it already names GEMINI.md (:5). Spec §5.3 then declares doctrine_docs: [GEMINI.md] again in review.yml, so the same list is held in two places that can drift apart. 'packs' also overlaps the per-row Mandate.languages (registry.py:16,56); see C34. So the claim that review.yml is 'not a second way to declare host values' fails on doctrine_docs.

#### C30 — REFUTED
- evidence: `plugins/arch-compliance/skills/architecture-review/SKILL.md:108 plugins/arch-compliance/python/acf/baseline.py:59 plugins/arch-compliance/python/acf/finding.py:11 hm:scripts/core/architecture_review/contract.py:19`
- reasoning: The two models do not serve different consumers today. The current review skill already maps auditor findings into acf.finding.Finding (SKILL.md:108: 'Map auditor findings into shared acf.finding.Finding rows'). acf.baseline.aggregate already consumes Finding (baseline.py:59-65). So the review and its drift baseline are consumers of Finding now. The design adds AuditorFinding for that same consumer and moves baseline over to it. The consumers only look different after this design creates the split. Both models share one job: recording one mandate-attributed violation at a POSIX file and line with a severity and a message (mandate_id/path/line/message/severity vs mandate_id/file/line/why/severity). §4.8 gives no written reason for not merging them.

#### C31 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/baseline.py:59 plugins/arch-compliance/skills/architecture-review/SKILL.md:117`
- reasoning: I searched for subsystem_of, 'def aggregate' and 'subsystem' under plugins/. The only implementation is acf/baseline.py:50-65. The only other references are the skill snippet (SKILL.md:115-125) and test_baseline.py. Extending aggregate and subsystem_of in place leaves one owner. One side effect: aggregate's input type changes from Finding to AuditorFinding, which breaks test_baseline.py:63-73. Spec §7 lists only the prefix tests for that file.

#### C32 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:32 hm:scripts/core/architecture_review/ui_logic_prepass.py:55`
- reasoning: I searched by behaviour (a per-line regex scan producing file:line candidates) using re.compile/re.search/re.finditer across acf/. The only per-line text scan is enforcement.py:32, which finds exemption tokens. That is a different job. Inside the plugin, the generic pre-pass duplicates nothing. Outside it, the origin scan_text and _TELLS (ui_logic_prepass.py:31-62) survive the cutover as gate-owned code (spec §5.4). The same tells will then live both there and in the plugin's typescript/html-templates hints. That is filed as an unanchored finding because it falls outside this claim's plugin scope.

#### C33 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:222 plugins/arch-compliance/hooks/inject_constraints.py:166 plugins/arch-compliance/python/acf/judge.py:266`
- reasoning: I searched for arch_anchor, heading and doctrine across the plugin's .py files. missing_anchors only tests whether the anchor is a stripped line (registry.py:222-223). inject_constraints reads the whole doctrine and truncates it at 4000 characters (:165-168). The judge passes the anchor string into its prompt and never extracts the section (judge.py:266). No existing code extracts the section under an anchor.

#### C34 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/registry.py:16 plugins/arch-compliance/python/acf/detectors/host.py:192 plugins/arch-compliance/python/acf/cli_check_diff.py:188`
- reasoning: The plugin already says which technology a rule applies to in two places. Mandate.languages ('python'|'typescript'|'both'|'none', registry.py:16,56) filters rows per file language (detectors/host.py:192). The gate maps file suffix to language at cli_check_diff.py:152 ('.py') and :188 ({'.ts','.tsx'}). Packs add a third mapping from technology to files, reusing the same ids 'python' and 'typescript' with different extents: the review's typescript pack covers .js/.jsx/.mjs/.cjs, while the gate's 'typescript' covers only .ts/.tsx. The spec never says how a row's languages relates to the declared packs. In §4.7 step 4, every declared pack's hints for the rule are scanned regardless of the row's languages. A row with languages: python (as §5.1 gives every HM row) would therefore still get TypeScript candidates. That is a partial overlap, not a new concept.

#### C35 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/__init__.py:33 plugins/arch-compliance/python/acf/registry.py:55`
- reasoning: KNOWN_DETECTORS maps a built-in detector id to its mandate id and call sites (detectors/__init__.py:33-45). Pack hints are regex tells handed to a prompt. They are different data with different consumers. Note for part two: the reserved detectors slot {rule id: [detector ids]} would become a third rule-to-detector mapping next to each row's `detector` field (registry.py:55) and KNOWN_DETECTORS. This spec does not ship it.

#### C36 — REFUTED
- evidence: `config/architecture/mandates.yml:51 config/architecture/mandates.yml:142 plugins/arch-compliance/skills/acf-mandate/SKILL.md:47`
- reasoning: I grepped `auditor` outside docs/. This repository's own registry carries `auditor: react-boundaries` (config/architecture/mandates.yml:51, row soft.react-boundaries) and `auditor: fail-loud` (:142). The first is no longer a rule id once react-boundaries is absorbed. §4.5 joins every row that has an auditor, with no status filter, so this unenforced row raises UnknownMandateError on a review of this repository. config/architecture/mandates.yml is not in the §6 change surface. acf-mandate SKILL.md:47 also documents `auditor` as a 'Tier-3 auditor name', which goes stale. So the consumers are not limited to the skill and the two profile rows.

#### C37 — SURVIVED
- evidence: `plugins/arch-compliance/skills/architecture-review/SKILL.md:115 plugins/arch-compliance/tests/test_baseline.py:8`
- reasoning: I grepped acf.baseline, 'from acf import baseline' and 'baseline import'. The only non-test importer is the architecture-review skill snippet (SKILL.md:115). Under the doctrine's `## Live consumers` ('A test is not a consumer'), the claim holds. However, test_baseline.py:8-17 and :63-73 call aggregate with Finding and will break when its input type changes. §7 does not list that change.

#### C38 — REFUTED
- evidence: `tests/test_self_host.py:40 plugins/arch-compliance/tests/test_profile_drift.py:30 plugins/arch-compliance/tests/test_registry.py:60 plugins/arch-compliance/skills/acf-setup/SKILL.md:139`
- reasoning: I grepped missing_anchors. Besides acf-mandate SKILL.md:99, it is called with a single string at tests/test_self_host.py:40, plugins/arch-compliance/tests/test_profile_drift.py:30 and test_registry.py:60. A str is itself a Sequence[str], so after the change each character becomes its own 'text' and every anchor is reported missing. Those calls must change too. Separately, acf-setup SKILL.md:138-139 states the anchor contract in prose ('matched as literal substrings of ARCHITECTURE.md'). The doctrine records that skill as a by-eye anchor check that should be a missing_anchors caller (ARCHITECTURE.md:275-276). §4.6 moves the contract to ARCH_REL plus doctrine_docs, but §6 changes acf-setup only to write review.yml. The change does not touch only the one snippet.

#### C39 — SURVIVED
- evidence: `config/architecture/mandates.yml:96 config/architecture/mandates.yml:112 plugins/arch-compliance/profiles/python-service/mandates.yml:57 plugins/arch-compliance/python/acf/detectors/host.py:205`
- reasoning: I grepped for a `review:` key, params.review, ["review"] and get("review") across the tracked tree outside docs/. Nothing matched. Every params block in the registry and both profiles uses path_prefixes, baseline/roots/exclude_globs, target_literal_re/allowlist_globs/atomic_is_sink or state_field/validator_name. No built-in detector reads a `review` key. Host detectors receive the whole params dict (host.py:205), so a host detector would see params.review, but no current consumer reads it.

#### C40 — REFUTED
- evidence: `hm:config/architecture/dead_code_baseline.json:195 hm:scripts/ci/dead_code_ratchet.py:380`
- reasoning: I grepped gemini_anchor across the whole HM checkout, not just scripts/ and tests/. config/architecture/dead_code_baseline.json:195 lists 'scripts/core/architecture/registry.py::MandateEntry.gemini_anchor' in the test_only lane (the lane opens at :151). That file is the floor for the dead-code ratchet (dead_code_ratchet.py:323). compare_lanes scores any new test_only key as growth (:379-381). After the rename, MandateEntry.arch_anchor is a new key and the stale entry departs. So a ratchet reads the field from config/, and the recipe's exclusion of config/ is not justified. :196-198 also list architecture_review/baseline.py symbols that §5.6 deletes; that is a shrink and is tolerated.

### Unanchored findings

- **important**: review.yml's doctrine_docs re-declares the doctrine document set that the approved ADR host contract (decision 5) says is never declared and is read from ARCH_REL's pointers. The spec does not name that decision, and the HM declaration (§5.3) repeats GEMINI.md, which HM's ARCHITECTURE.md pointer already names.
  - evidence: `docs/design/ADR_GATE_HOST_CONTRACT.md:80`
- **important**: acf.review.aggregator.parse_auditor_payload and AuditorContractViolationError re-implement the existing check for exactly one fenced JSON block, parsed and schema-validated, plus its contract-violation exception, from acf/adr/parser.py. Only the failure policy differs (abort vs FAILED group).
  - evidence: `plugins/arch-compliance/python/acf/adr/parser.py:26`
- **important**: Technology packs add a third mapping from technology to files beside Mandate.languages and the gate's suffix routing. They reuse the same ids with different extents (the typescript pack includes .js/.jsx; the gate's typescript is .ts/.tsx), and §4.7 ignores a row's languages when choosing hints.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:188`
- **important**: This repository's own registry row soft.react-boundaries keeps `auditor: react-boundaries`. It is missing from the §6 change surface, and §4.5 joins rows by auditor without a status filter, so a review here raises UnknownMandateError once react-boundaries is absorbed.
  - evidence: `config/architecture/mandates.yml:51`
- **important**: Decision 8 makes a repository declare the same host values twice. single-owner's artifacts/owners restate facade.forbid-sink's target_literal_re/allowlist_globs, and state-machine-discipline's markers/transition_methods restate fsm.transition-guard's state_field/validator_name, under params.review beside the detector's params.
  - evidence: `config/architecture/mandates.yml:112`
- **important**: Renaming gemini_anchor to arch_anchor grows the test_only lane of HM's dead-code ratchet baseline (config/), which the §5.1 recipe excludes. The cutover PR's ratchet check fails unless the baseline is updated, and §5 does not list that update.
  - evidence: `hm:config/architecture/dead_code_baseline.json:195`
- **advisory**: After cutover, the origin's UI tells live in two places: hm:scripts/ci (moved ui_logic_prepass.py, §5.4) and the plugin's typescript/html-templates pack hints. That is two owners of one tell set until part two, and the spec does not name it.
  - evidence: `hm:scripts/core/architecture_review/ui_logic_prepass.py:31`
- **advisory**: Changing missing_anchors to take a sequence breaks three test callers that pass a single str. A str is a Sequence[str], so each character becomes a text. acf-setup's anchor prose is also left stating the ARCHITECTURE.md-only contract.
  - evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:139`
- **advisory**: ReportWriteError is a third exception for 'a review record could not be written'. The other two are BaselineError's write side and RunDetailWriteError, each wrapping the same mkdir+write_text+OSError shape.
  - evidence: `plugins/arch-compliance/python/acf/adr/run_detail.py:183`
- **advisory**: aggregate's input changes from Finding to AuditorFinding, but §7 lists only the prefix tests for test_baseline.py. Its existing Finding-based aggregate test breaks.
  - evidence: `plugins/arch-compliance/tests/test_baseline.py:63`

### Looked for but did not find

- an existing doctrine-section extractor: arch_anchor, heading, doctrine, startswith("#") across plugins/arch-compliance/**/*.py
- an existing per-line regex candidate scanner in acf/: re.compile, re.search, re.finditer
- an existing params key named review: '^\s+review\s*:', params.review, ["review"], get("review") across the tree outside docs/
- other aggregate/subsystem implementations: subsystem_of, 'def aggregate', subsystem under plugins/
- other importers of acf.baseline: 'acf.baseline', 'from acf import baseline', 'baseline import'
- an existing review host config file or REVIEW_REL constant: acf/repo.py constants
- no-overwrite report naming elsewhere: run_detail_path in acf/adr/run_detail.py (keyed by version, not a numeric suffix)

### Relationships

- PARTIAL_OVERLAP: `ReviewHostConfig.doctrine_docs` — responsibility `declare the set of doctrine documents beyond ARCH_REL` — existing `plugins/arch-compliance/python/acf/adr/host.py:4`
  - resolution: One owner of the doctrine set: either the ARCH_REL pointer list, read by a shared acf helper that both the review and the ADR gate consume (and acf-mandate through missing_anchors), or a declared doctrine_docs that the ADR gate also reads, with ADR decision 5 amended on the record. Not both.
- PARTIAL_OVERLAP: `acf.review.aggregator.parse_auditor_payload` — responsibility `extract exactly one fenced json block from an agent's final message, parse it and validate it against a strict model` — existing `plugins/arch-compliance/python/acf/adr/parser.py:53`
  - resolution: Extract the fence regex, the zero/many-block check and the JSON decode into one acf helper (for example acf.agent_payload.extract_json_block(payload, subject) raising a single base contract-violation error). parse_reviewer_payload and parse_auditor_payload become consumers that keep only their own policy: identity check plus abort, vs FAILED group.
- PARTIAL_OVERLAP: `AuditorContractViolationError` — responsibility `signal that an agent payload breaks its dispatched contract` — existing `plugins/arch-compliance/python/acf/exceptions.py:45`
  - resolution: One AgentContractViolationError (or reuse ReviewerContractViolationError renamed) raised by the shared extractor, with each skill's policy at its call site.
- PARTIAL_OVERLAP: `acf.review.contract.AuditorFinding` — responsibility `record one mandate-attributed violation at a POSIX file:line with a severity and a message` — existing `plugins/arch-compliance/python/acf/finding.py:11`
  - resolution: Keep aggregate typed on a minimal shared shape, (mandate_id, path) as a Protocol or a projection to Finding, so baseline does not fork per finding model. AuditorFinding keeps its review-only fields (snippet, why, suggested_fix, four-level severity) and state in the spec why Finding is not reused, since the current skill already maps into it.
- PARTIAL_OVERLAP: `acf.review.packs.TechPack.files and ReviewHostConfig.packs` — responsibility `decide which files belong to a technology and which technology a rule applies to` — existing `plugins/arch-compliance/python/acf/registry.py:16`
  - resolution: One technology vocabulary: pack ids as the canonical language ids, with the pack `files` globs as the single file-to-technology map that the gate's suffix routing (cli_check_diff.py:152,188) and Mandate.languages filtering (detectors/host.py:192) also consume. Or state in the spec how a row's languages narrows the packs whose hints it receives.
- PARTIAL_OVERLAP: `single-owner / state-machine-discipline settings under params.review` — responsibility `declare a protected artifact and its owners; declare the state field and its transition validator` — existing `config/architecture/mandates.yml:112`
  - resolution: One declaration of each host value, read by both the AST detector and the review rule. For example, the rule's settings model reads the detector's params keys, or the detector row carries `auditor` and the review derives its settings from the same params, instead of a parallel params.review copy.
- SUBSUMED: `acf.baseline.aggregate over AuditorFinding; subsystem_of with declared prefixes` — responsibility `fold findings into (mandate_id, subsystem) counts` — existing `plugins/arch-compliance/python/acf/baseline.py:59`
  - resolution: Extend in place, as the spec does. The prefix rule generalises the first-segment rule, with no sibling module.
- PARTIAL_OVERLAP: `acf.review.prepass` — responsibility `scan lines with regex tells and emit file:line [tell] snippet candidates` — existing `hm:scripts/core/architecture_review/ui_logic_prepass.py:55`
  - resolution: After cutover, the gate-owned HM staged check should consume acf.review.prepass with the plugin's packs rather than keep its own _TELLS copy. Otherwise name the duplicate tell set and its owner until part two.
- PARTIAL_OVERLAP: `ReportWriteError` — responsibility `fail loud when a review record cannot be persisted` — existing `plugins/arch-compliance/python/acf/baseline.py:68`
  - resolution: One write helper (mkdir parents, write_text utf-8, wrap OSError with the POSIX path) consumed by save_baseline, write_run_detail and the new report and sidecar writers. Each may keep its own subject string.
- ADJACENT: `acf.review.host.load_review_config` — responsibility `require the doctrine document, then load a strict host declaration` — existing `plugins/arch-compliance/python/acf/adr/host.py:28`
  - resolution: None beyond consuming acf.loader.require_file/load_model_file, as load_host_config does.
  - non-merge: Two different declaration files with disjoint fields, both built on the shared acf.loader primitives (load_model_file, require_file). The common logic already has one owner, and ADR decision 2 chose a separate file per gate.
- ADJACENT: `acf.review.rollup` — responsibility `render a terminal roll-up of a run` — existing `plugins/arch-compliance/python/acf/adr/rollup.py:1`
  - resolution: None.
- ADJACENT: `TechPack.hints` — responsibility `name the shapes a rule takes in one technology` — existing `plugins/arch-compliance/python/acf/detectors/__init__.py:33`
  - resolution: None in this spec. In part two, the detectors slot must not become a third rule-to-detector map beside the row's `detector` field and KNOWN_DETECTORS.
  - non-merge: Hints are regex tells handed to an LLM auditor. KNOWN_DETECTORS maps AST detector ids to mandate ids and call sites. They hold different data for different consumers.

### Two-owner counts

- declare the doctrine document set (ARCH_REL pointers vs review.yml doctrine_docs): 2
- extract and validate a single fenced json block from an agent payload: 2
- agent payload contract-violation exception: 2
- mandate-attributed violation record (Finding vs AuditorFinding): 2
- map files to a technology (gate suffix routing, Mandate.languages, pack files globs): 3
- declare protected artifact and owners (facade.forbid-sink params vs single-owner params.review): 2
- declare state field and transition validator (fsm.transition-guard params vs state-machine-discipline params.review): 2
- UI logic tell set (HM gate-owned ui_logic_prepass vs plugin pack hints): 2
- fail-loud write of a review record (BaselineError, RunDetailWriteError, ReportWriteError): 3
- state the arch_anchor resolution contract (missing_anchors vs acf-setup prose): 2

### Document conflicts

- `docs/design/ADR_GATE_HOST_CONTRACT.md:80` (contradicts): The doctrine is read from the plugin's single doctrine path, `config/architecture/ARCHITECTURE.md`, and from every document it points to. No doctrine field is declared.
- `docs/design/ADR_GATE_HOST_CONTRACT.md:251` (contradicts): The doctrine is not declared here: it is `config/architecture/ARCHITECTURE.md`
- `plugins/arch-compliance/skills/acf-setup/SKILL.md:139` (contradicts): mandate `arch_anchor` values are matched as literal substrings of ARCHITECTURE.md
- `plugins/arch-compliance/skills/architecture-review/SKILL.md:108` (contradicts): Map auditor findings into shared `acf.finding.Finding` rows where possible

## hardening

### Claim verdicts

#### C41 — SURVIVED
- evidence: `plugins/arch-compliance/skills/architecture-review/auditors/fail-loud.md:1; hm:.claude/skills/architecture-review/auditors/metadata-facade.md:3; hm:.claude/skills/architecture-review/auditors/output-agnosticism.md:12`
- reasoning: The duplication the justification names is live today. The plugin ships its own fail-loud, no-shims and posix-paths auditor prose, and the origin ships separate copies of fail-loud and no-shims. The origin copies hard-code host values: ContentMetadataService and index.yml at metadata-facade.md:3, stage file lists at output-agnosticism.md:12-32. So per-repository full copies already repeat rule prose and mix host data into it. Splitting rule prose (plugin) from settings (params.review) removes the repetition: data moves to rows, and rule text exists once.

#### C42 — SURVIVED
- evidence: `hm:scripts/core/architecture_review/contract.py:41; plugins/arch-compliance/python/acf/registry.py:61`
- reasoning: The origin AuditorResult carries a free-text `mandate: str` at contract.py:41, which is the identity problem being fixed. The plugin Mandate has `auditor: str | None` at registry.py:61, so rows can be grouped by that value. Requiring each finding's mandate_id to be among the group's rows refuses bad attribution as a contract violation (spec §4.5, §7 test_review_aggregator) rather than repairing it. Dispatch count is bounded by the distinct auditor values. In the origin file, 30 auditor-bearing rows collapse to 9 distinct values.

#### C43 — SURVIVED
- evidence: `hm:.claude/skills/architecture-review/SKILL.md:90; hm:.claude/skills/architecture-review/SKILL.md:185; plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:232`
- reasoning: Per-group FAILED, keeping the raw payload and continuing with a non-zero exit, is the origin's existing behaviour (SKILL.md:90, :185), not a new recovery mechanism. The ADR gate aborts instead (adversarial-design-review/SKILL.md:232). The handling refuses the malformed payload and does not repair it: the raw payload and error are kept, and the exit is non-zero, so the failure stays visible. The producer is an external LLM agent, which cannot be hardened beyond the contract prompt, so rung 3 at the boundary is the highest that applies.

#### C44 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:61; config/architecture/ARCHITECTURE.md:187`
- reasoning: A surface glob that matches nothing can only come from repository data (params.review.surface). Failing loud with the mandate id is rung 3 at the reader of that data, consistent with `## Declared, never defaulted` (ARCHITECTURE.md:187). Rung 1 does not apply: whether a glob matches files on disk cannot be expressed in the settings schema. Nothing is silently skipped.

#### C45 — SURVIVED
- evidence: `scripts/check_installed_skills.py:1; hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:1`
- reasoning: The installed-skill check that stage 1 relies on exists (scripts/check_installed_skills.py). The release-then-consumer order matches the phase 1d precedent quoted in §5. The sequencing is coherent as stated. It does not cover the origin CI dependency on acf for baseline_staleness.py, which is filed under C50 and as unanchored findings.

#### C46 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:50; plugins/arch-compliance/python/acf/registry.py:91; plugins/arch-compliance/python/acf/registry.py:157; plugins/arch-compliance/python/acf/cli_check_llm.py:54`
- reasoning: Mandate (registry.py:50-62) declares no model_config, so pydantic's default extra='ignore' tolerates the origin's `remediation` key (it is dropped silently). load_mandates (registry.py:150-198) runs detector checks only when known_detectors or llm_prompt_ids are passed, and cli_check_llm.py:54 passes neither. Executed check: read the 48 rows of hm:config/architecture/mandates.yml at b2611977f in memory, renamed gemini_anchor to arch_anchor, set languages to 'python' and then to 'none', and ran Mandate.model_validate on every row. There were zero failures. Origin guard detectors such as `scripts/ci/x.py` contain no ':' and are not host rows. Every active ast/guard row has a Tier-1 call site. The row-shape language check at :104 applies only to host ast rows.

#### C47 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:61; plugins/arch-compliance/python/acf/registry.py:62; plugins/arch-compliance/python/acf/registry.py:76`
- reasoning: `auditor: str | None = None` is at :61 and `params: dict[str, Any] | None = None` is at :62. The only constraint on params is the JSON-only validator at :75-88, so nested `review:` mappings of strings and lists pass. No schema change is needed.

#### C48 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:61; plugins/arch-compliance/python/acf/repo.py:53; plugins/arch-compliance/python/acf/registry.py:187`
- reasoning: RepoTree.file (repo.py:61-64) returns the existing regular file inside the root, else None, after containment via contained() (:53-59). OSError from stat propagates. load_mandates already uses it this way for host detector files (registry.py:187-197), which is the same pattern the hatch needs.

#### C49 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/__init__.py:33`
- reasoning: KNOWN_DETECTORS is a MappingProxyType of detector id to BuiltinDetector. Executed: its keys are empty_catch, explicit_any, fail_loud_bare_except, fail_loud_ratchet, forbid_facade_sink, fsm_transition_guard, no_build_artifacts, no_shims_hasattr and posix_paths_str_serialization.

#### C50 — REFUTED
- evidence: `hm:.github/workflows/arch-guards.yml:36; hm:tests/test_baseline_staleness.py:58; hm:scripts/ci/baseline_staleness.py:87; plugins/arch-compliance/python/acf/baseline.py:82`
- reasoning: The origin environments do not install acf. arch-guards.yml:36 installs only pyyaml, pydantic, pytest, pytest-timeout and requirements-lint.txt. regression-tests.yml installs requirements.txt, which names no acf or arch-compliance package. `git grep 'from acf|import acf' -- scripts tests` at b2611977f returns nothing. baseline_staleness.py is exercised by hm:tests/test_baseline_staleness.py:58-67 (test_main_never_crashes_on_malformed_baseline calls main() on a malformed baseline, which reaches the deferred import at :87). Repointed to acf.baseline, that test raises ModuleNotFoundError in CI. Even where acf is importable, the module catches `BaselineError` (hm import at :88). acf.baseline.load_baseline raises AcfInputError, not BaselineError (baseline.py:82-86), so a malformed baseline now crashes main(). The test asserts it never crashes. The pre-push hook runs it under `|| true` (hm:scripts/setup_git_hooks.py:138), so the breakage there would be silent.

#### C51 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_skill_prose.py:13; plugins/arch-compliance/tests/test_adr_skill_prose.py:42`
- reasoning: The check iterates an explicit FILES list (:13-19) against a FORBIDDEN literal list (:20-25) in test_the_prose_names_no_origin_host (:42-47). Covering architecture-review means adding its SKILL.md, the twelve rules/*.md files and _contract.md to FILES (or a glob). The check itself is path-agnostic. test_the_seven_files_moved (:37) asserts FILES exist, so the new entries must exist too. That holds for files this spec creates.

### Unanchored findings

- **blocking**: §5.4 repoints hm baseline_staleness.py to acf.baseline.load_baseline, but no origin CI job installs acf. The origin test that calls main() (test_main_never_crashes_on_malformed_baseline) would fail with ModuleNotFoundError, and the spec states no step that makes acf importable in origin CI.
  - evidence: `hm:.github/workflows/arch-guards.yml:36; hm:tests/test_baseline_staleness.py:58; hm:scripts/ci/baseline_staleness.py:87`
- **important**: baseline_staleness.py catches the origin BaselineError around load_baseline, but acf.baseline.load_baseline raises AcfInputError. After the repoint, a malformed baseline crashes main() instead of printing the NOTE the test requires, and the pre-push hook's `|| true` hides that crash.
  - evidence: `plugins/arch-compliance/python/acf/baseline.py:82; hm:scripts/ci/baseline_staleness.py:88; hm:scripts/setup_git_hooks.py:138`
- **advisory**: §4.6 says acf-mandate and the review resolve anchors over the same document set. But acf-mandate loads through load_gate_registry with KNOWN_DETECTORS, and on the origin repo that refuses the origin's ast rows (e.g. `_find_bare_except` is not a key), so before part two the shared anchor check cannot run there.
  - evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:95; plugins/arch-compliance/python/acf/registry.py:201; plugins/arch-compliance/python/acf/detectors/__init__.py:33`
- **advisory**: acf-mandate's new behaviour (ARCH_REL plus doctrine_docs when review.yml exists, ARCH_REL alone otherwise) branches on whether a file is present. It is a default that the doctrine's list of recorded exceptions to `## Declared, never defaulted` does not include.
  - evidence: `config/architecture/ARCHITECTURE.md:193; docs/design/ARCHITECTURE_REVIEW_PORT.md:147`

### Looked for but did not find

- Pack-hint pre-pass (§4.7 step 4): seeds candidates and repairs nothing; a rule with no hints is still reviewed. Not a recovery mechanism.
- Same-day report numeric suffix (§4.7 step 8): a non-destructive write that repairs no invalid state. Cleared.
- Hatch params.review pass-through (§4.5): validation is left to the repository prompt by decision 12 and no data is repaired. Cleared.
- Empty `subsystems` list keeping first-segment bucketing: chosen by an explicitly declared (required) field, not a default for an absent one. Cleared.
- Plugin Mandate extra-key handling: extra='ignore' (default) drops `remediation` silently. That is tolerance, not repair, and the spec relies on it.
- Producer of auditor-label baseline cells: hm:scripts/core/architecture_review/baseline.py (save_baseline). The plugin Baseline already refuses that shape (BaselineCell requires mandate_id, extra='forbid'), so a stale origin baseline cannot load silently.

### Mechanism traces

- **contract violation marks the group FAILED; the run continues; exit non-zero**
  - invalid state: an auditor payload with not exactly one fenced JSON block, or one failing the AuditorResult schema, or one with a finding whose mandate_id is not among the group's row ids
  - producer: `docs/design/ARCHITECTURE_REVIEW_PORT.md:157`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/ARCHITECTURE_REVIEW_PORT.md:158`
- **declared surface matching no file fails loud**
  - invalid state: a row with params.review.surface set where the set of files on disk matching surface, minus the exclusions, is empty
  - producer: `docs/design/ARCHITECTURE_REVIEW_PORT.md:209`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: it is a settings error, not an empty run
  - spec citation: `docs/design/ARCHITECTURE_REVIEW_PORT.md:155`
- **baseline reset at cutover**
  - invalid state: baseline cells keyed by a free-text auditor label spanning several mandate rows, rather than keyed by mandate_id
  - producer: `hm:scripts/core/architecture_review/baseline.py:75`
  - rung 4 (highest applicable 4); repairs=False
  - hardening rejected because: one label spans up to six rows (three-tier-hfsm covers six rows in §5.2), so no count can be split across mandate ids
  - spec citation: `docs/design/ARCHITECTURE_REVIEW_PORT.md:230`
- **missing_anchors over a sequence of doctrine texts; acf-mandate passes ARCH_REL plus doctrine_docs when review.yml exists**
  - invalid state: a row whose arch_anchor is a heading in a doctrine_docs file but not in ARCH_REL, which acf-mandate reports missing while the review resolves it
  - producer: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:99`
  - rung 2 (highest applicable 2); repairs=False
  - spec citation: `docs/design/ARCHITECTURE_REVIEW_PORT.md:147`

## Claims

- **C1** [premise]: The plugin's current /architecture-review is a generic rewrite whose default auditor set is four auditors (fail-loud, no-shims, posix-paths, react-boundaries).
  - spec citation: `plugins/arch-compliance/skills/architecture-review/SKILL.md:72`
- **C2** [premise] [load-bearing]: The origin repository's review has these capabilities, which the port must keep: nine auditors, a doctrine rubric step, per-auditor file surfaces (frontend and family-template lists), a deterministic UI pre-pass, a blame-based provenance section, and a JSON sidecar.
  - spec citation: `hm:.claude/skills/architecture-review/SKILL.md:31-158`
- **C3** [premise]: The origin auditors hard-code origin-repository values (owner class names, artifact names, stage file lists), which is why they cannot move to the plugin as they are.
  - spec citation: `hm:.claude/skills/architecture-review/auditors/metadata-facade.md:3; hm:.claude/skills/architecture-review/auditors/output-agnosticism.md:12-32`
- **C4** [premise] [load-bearing]: Exactly three origin gate files under scripts/ci import the origin review package (recipe: `git grep -n architecture_review -- scripts/ci` at b2611977f): llm_judge.py (load_rubric reads `<auditor>.md` from the skill's auditors directory as the judge prompt), baseline_staleness.py:87 (load_baseline), check_ui_prepass_staged.py:17 (scan_text). Run the recipe; also check whether any other non-test, non-doc origin code outside scripts/ci imports the package or reads the skill tree, since §5.6 deletes both.
  - spec citation: `hm:scripts/ci/arch_compliance/llm_judge.py:88-98; hm:scripts/ci/baseline_staleness.py:87; hm:scripts/ci/check_ui_prepass_staged.py:17`
- **C5** [premise] [load-bearing]: The origin registry model MandateEntry is extra='forbid' and has gemini_anchor but no languages, params or arch_anchor fields, so adding plugin fields to the origin mandates file without changing the model would break the origin gate's loader.
  - spec citation: `hm:scripts/core/architecture/registry.py:21-34`
- **C6** [premise] [load-bearing]: The origin drift baseline keys each count on a free-text auditor label (e.g. 'Three-Tier/HFSM'), and one label spans up to six mandate rows, so counts cannot be split across mandate ids; this is why the baseline is reset rather than migrated.
  - spec citation: `hm:docs/architecture/compliance_baseline.json; §5.2 table`
- **C7** [premise] [load-bearing]: The origin rows with an `auditor` value are the 25 rows listed in §5.2 with the origin auditor shown for each (recipe: yaml.safe_load over hm:config/architecture/mandates.yml filtered on auditor). Run the recipe and compare row ids and auditor values.
  - spec citation: `hm:config/architecture/mandates.yml`
- **C8** [premise] [load-bearing]: Deferral: hm:scripts/core/skill_install.py stays because the other dual-installed origin skill still uses it after the cutover.
  - spec citation: `hm:scripts/core/skill_install.py`
- **C9** [premise]: The origin review's frontend and family-template file lists ignored --paths but kept the global exclusions.
  - spec citation: `hm:.claude/skills/architecture-review/SKILL.md:53-61`
- **C10** [premise] [load-bearing]: Deferral: absorbing the react-boundaries auditor into ui-logic-isolation leaves the plugin's Tier-2 judge unaffected, because the judge's llm_react_boundaries prompt id does not read the auditor file plugins/arch-compliance/skills/architecture-review/auditors/react-boundaries.md.
  - spec citation: `plugins/arch-compliance/python/acf/judge.py (judge.py:31)`
- **C11** [premise] [load-bearing]: Deferral: script-block extraction for .svelte files is not needed by this spec, because the review auditors read .svelte text directly and pack hints are regular expressions over that text; only deterministic detectors (part two) need extraction.
  - spec citation: `§3 Non-goals`
- **C12** [premise] [load-bearing]: Deferral: Cursor copies of the skill are out of scope, as recorded for phase 1d; deleting the origin .cursor architecture-review tree is acceptable because a filed follow-up covers Cursor gate access.
  - spec citation: `hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md ('Workstream E 1d follow-up — Cursor / Cline gate access')`
- **C13** [premise] [load-bearing]: The origin LLM judge can take its five prompts from a gate-owned directory keyed by mandate id without other behaviour change: load_rubric only reads a prompt file by name, and its callers have the mandate id available.
  - spec citation: `hm:scripts/ci/arch_compliance/llm_judge.py:88-98`
- **C14** [premise] [load-bearing]: The origin docs manifest (rubric/arch-docs-manifest.yml) is cited by the origin ARCHITECTURE.md pointer, so it must move out of the skill tree to hm:config/architecture/arch-docs-manifest.yml with the pointer updated.
  - spec citation: `hm:config/architecture/ARCHITECTURE.md:9-10`
- **C15** [deletion] [load-bearing]: Deleting plugins/arch-compliance/skills/architecture-review/auditors/ (four files) strands no consumer: nothing but the architecture-review skill reads those files (check the judge, hooks, tests, profiles, other skills).
  - spec citation: `plugins/arch-compliance/skills/architecture-review/auditors/`
- **C16** [deletion] [load-bearing]: After §5.4 moves ui_logic_prepass.py and repoints the three gate files and tests/test_mandate_registry_drift.py, deleting the origin skill trees, the rest of hm:scripts/core/architecture_review/ and the listed tests leaves no live origin importer or reader of the deleted files (check scripts, tests, config, CI workflows, hooks).
  - spec citation: `§5.4, §5.6`
- **C17** [deletion] [load-bearing]: Deleting hm:docs/architecture/compliance_baseline.json and re-setting it with one --update-baseline run loses no consumer: baseline_staleness.py reads it through acf.baseline.load_baseline after the cutover and accepts the new format.
  - spec citation: `§5.5; hm:scripts/ci/baseline_staleness.py:87`
- **C18** [mandate] [load-bearing]: Rule prompts and the rewritten skill name no host repository, path or section (`## Prose names no host`), and the forbidden-vocabulary test is extended to cover architecture-review.
  - spec citation: `config/architecture/ARCHITECTURE.md:204-213; plugins/arch-compliance/tests/test_adr_skill_prose.py`
- **C19** [mandate] [load-bearing]: The review's host values comply with `## Declared, never defaulted`: review.yml fields are all required and a missing file fails loud; RuleSettings defaults (surface absent = whole target tree, empty surface_exclude and docs), the built-in exclusion list, and acf-mandate using ARCH_REL alone when review.yml is absent are not defaults standing in for a missing declaration.
  - spec citation: `config/architecture/ARCHITECTURE.md:187-203; §4.2, §4.4, §4.6`
- **C20** [mandate]: The two new exceptions AuditorContractViolationError and ReportWriteError subclass AcfError only (`## One base exception`).
  - spec citation: `config/architecture/ARCHITECTURE.md:108-113`
- **C21** [mandate] [load-bearing]: The design complies with `## One owner for host paths`: review.yml is located by a new acf.repo.REVIEW_REL, and the hatch prompt path is resolved through RepoTree.file.
  - spec citation: `config/architecture/ARCHITECTURE.md:114-141`
- **C22** [mandate] [load-bearing]: The design complies with `## Single point of definition`: react-boundaries is absorbed rather than kept beside ui-logic-isolation; the auditor output contract is stated once in _contract.md; the review and acf-mandate resolve anchors over one doctrine document set.
  - spec citation: `config/architecture/ARCHITECTURE.md:265-279; §4.2, §4.6, §4.10`
- **C23** [mandate] [load-bearing]: The design complies with `## Live consumers` by reserving the pack `detectors` slot without building it, and every new export (§6) has a live call site in the package, a hook or a skill.
  - spec citation: `config/architecture/ARCHITECTURE.md:222-227; §4.3`
- **C24** [mandate]: The design complies with `## Release discipline`: the skill prose change bumps the version to 0.3.0 in pyproject.toml and plugin.json.
  - spec citation: `config/architecture/ARCHITECTURE.md:253-264`
- **C25** [mandate]: The spec's population claims comply with `## No completeness claims`: each (gemini_anchor consumers, rows with an auditor, gate importers of the review package) is backed by a recipe a reader can re-run.
  - spec citation: `config/architecture/ARCHITECTURE.md:228-239; §5.1, §5.2, §5.4`
- **C26** [mandate] [load-bearing]: Marking an auditor group FAILED on a contract violation, keeping its raw payload and error, continuing the other groups, and exiting non-zero complies with `## Fail loud` and `## No shims` (it is not a soft fallback).
  - spec citation: `config/architecture/ARCHITECTURE.md:26-56; §4.7 step 6`
- **C27** [mandate]: Persisted paths (report, sidecar, baseline cells, review.yml values) are POSIX (`## POSIX paths`).
  - spec citation: `config/architecture/ARCHITECTURE.md:57-67`
- **C28** [mandate]: Every origin-repository rule the spec relies on is quoted where used (the repository CLAUDE.md citation convention, restated in §0), including any origin doctrine that governs the origin-stage changes of §5.
  - spec citation: `§0; CLAUDE.md 'Citation convention for specs here'`
- **C29** [shape_fit] [load-bearing]: config/architecture/review.yml with ReviewHostConfig follows the AdrHostConfig pattern and is not a second way to declare host values that adr.yml or mandates.yml already carry.
  - spec citation: `plugins/arch-compliance/python/acf/adr/host.py:19-25`
- **C30** [shape_fit] [load-bearing]: acf.review.contract.AuditorFinding is not a partial duplicate of the existing acf.finding.Finding (the gate's finding model); the two serve different consumers.
  - spec citation: `§4.8`
- **C31** [shape_fit] [load-bearing]: acf.baseline is extended in place (aggregate over AuditorFinding, declared subsystem prefixes) rather than duplicated.
  - spec citation: `plugins/arch-compliance/python/acf/baseline.py:50-56`
- **C32** [shape_fit] [load-bearing]: The generic pre-pass (acf.review.prepass) is the only pre-pass in the plugin; it generalises the origin's UI-only pre-pass and duplicates nothing existing in the plugin.
  - spec citation: `hm:scripts/core/architecture_review/ui_logic_prepass.py:26-50; §4.3`
- **C33** [shape_fit] [load-bearing]: acf.review.doctrine.doctrine_section is the only doctrine-section extractor; no existing plugin code (for example the constraint-injection hook or the ADR gate) already extracts a doctrine section by arch_anchor.
  - spec citation: `§4.6`
- **C34** [shape_fit] [load-bearing]: Technology packs are a new concept that does not duplicate Mandate.languages or the existing gate detector packs (python_pack.py, the TypeScript bridge) — a second way to say which technology a rule applies to.
  - spec citation: `§4.3`
- **C35** [shape_fit]: Pack hints for the review and the gate's built-in detectors (KNOWN_DETECTORS) are two consumers of different data, not two definitions of the same shape.
  - spec citation: `§4.3`
- **C36** [sweep] [load-bearing]: Consumers of mandate `auditor` values in this repository are the architecture-review skill and the two profile rows (react-app soft.react-boundaries, python-service fail-loud), so changing auditor values to rule ids touches only those.
  - spec citation: `plugins/arch-compliance/profiles/react-app/mandates.yml:36-46; profiles/python-service/mandates.yml`
- **C37** [sweep] [load-bearing]: The only consumer of acf.baseline in this repository is the architecture-review skill.
  - spec citation: `plugins/arch-compliance/python/acf/baseline.py`
- **C38** [sweep] [load-bearing]: The only caller of missing_anchors is the acf-mandate skill snippet, so changing its signature to take a sequence of texts touches only that snippet.
  - spec citation: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:91-99`
- **C39** [sweep] [load-bearing]: No existing mandate row in this repository's registry or the plugin profiles uses a `params` key named `review`, so the `params.review` namespace collides with nothing.
  - spec citation: `§2 decision 8`
- **C40** [sweep] [load-bearing]: The consumers of the origin gemini_anchor field that the rename must update are the ones listed in §5.1 (recipe `git grep -n gemini_anchor -- scripts tests`); the recipe's exclusion of config/ and docs/ is justified, i.e. no file outside scripts/ and tests/ reads the field at runtime or in a ratchet.
  - spec citation: `§5.1`
- **C41** [mechanism_justification] [load-bearing]: Three layers (rule, technology pack, repository settings) plus a hatch are needed rather than letting each repository keep full copies of the auditors it needs, because copies duplicate rule prose per repository.
  - spec citation: `§2 decisions 1-3, §4.1`
- **C42** [mechanism_justification] [load-bearing]: One dispatch per rule (grouping all rows naming it) rather than one per row, with findings attributed by mandate_id, keeps dispatch count to the rules in use while fixing the origin's free-text identity.
  - spec citation: `§4.5`
- **C43** [mechanism_justification] [load-bearing]: Auditor contract violations mark the group FAILED and the run continues (unlike the ADR gate, which aborts), because one auditor's malformed payload should not discard the other groups' findings; the exit status is non-zero.
  - spec citation: `§4.7 step 6`
- **C44** [mechanism_justification]: A declared surface that matches no file fails loud rather than skipping, because it signals a settings error.
  - spec citation: `§4.7 step 3`
- **C45** [mechanism_justification] [load-bearing]: The cutover is sequenced plugin release first, origin PR second, with plugin defects found by the origin run fixed by a patch release before the origin PR merges.
  - spec citation: `§5`
- **C46** [implementability] [load-bearing]: Plugin load_mandates(path) with no detector arguments (as cli_check_llm.py:54 calls it) will load the migrated origin mandates file: the plugin Mandate model tolerates the origin's extra keys (e.g. remediation), and its row validators accept origin ast/guard rows whose detectors are not host references and the `languages` values §5.1 assigns.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_llm.py:54; plugins/arch-compliance/python/acf/registry.py:61`
- **C47** [implementability] [load-bearing]: Mandate already has `auditor: str | None` and `params: dict | None` fields, so `params.review` and rule-id auditor values need no plugin schema change.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:61`
- **C48** [implementability] [load-bearing]: acf.repo.RepoTree provides a `file` method that resolves a repository-relative POSIX path to an existing file (or None), usable to resolve a hatch prompt path.
  - spec citation: `§4.5`
- **C49** [implementability]: KNOWN_DETECTORS exists as a mapping of built-in detector ids, so the reserved pack `detectors` slot can name keys of it.
  - spec citation: `§4.3`
- **C50** [implementability] [load-bearing]: The origin CI environment that runs baseline_staleness.py and check_ui_prepass_staged.py can import acf (the plugin package), so repointing baseline_staleness.py to acf.baseline.load_baseline will not break the origin CI job.
  - spec citation: `§5.4; hm:scripts/ci/baseline_staleness.py:87`
- **C51** [implementability]: The forbidden-vocabulary test plugins/arch-compliance/tests/test_adr_skill_prose.py is structured so its check can be extended to the architecture-review skill directory.
  - spec citation: `plugins/arch-compliance/tests/test_adr_skill_prose.py`
