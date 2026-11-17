# Adversarial design review — full detail

Spec: `docs/design/ARCHITECTURE_REVIEW_PORT.md` @ `b7965d0df048dabe26d8ebdded5db6b2300543c7`
Kinds: feature
Outcome: **BLOCKED**
Claims: 69 · Reviewers: 4 · Converged: 1

## Blocking reasons

- load-bearing claim C17 (deletion) is REFUTED: I reran recipes A, B and C. Most hits are dispositioned correctly, and grepping the deleted test-file names finds no CI job listing them; arch-guards.yml:41 runs test_mandate_registry_drift.py, which stays. The census still fails on three points. (1) The dead_code_baseline row's disposition says the ratchet will report MandateEntry.params as growth. It will not: vulture keeps one used_names set, and a Name load of `params` in scripts (tuner_print.py:216 and others) marks the field used (see C21). (2) Recipe B's 48 hits in hm:config/architecture/mandates.yml (gemini_anchor keys, e.g. :14) have no row in the census table; only §5.1's model-level wording covers them. (3) Recipe C's hit at exceptions.py:1525 (a docstring naming BaselineError) and the comment at setup_git_hooks.py:137 above the removed line are left undispositioned, so they go stale.
- load-bearing claim C21 (premise) is REFUTED: The --update-baseline mode exists (:493), and growth is name-keyed set arithmetic (:377-380). The 'exactly three keys' half is false. The ratchet's findings come from vulture scans of scripts/ (scan A) and scripts+tests (scan B) (:408). Vulture 2.16 marks any Name load as used in one shared used_names set (visit_Name). `params` is loaded as a local variable throughout scripts (tuner_print.py:216, :255, :256). I ran an in-memory vulture scan of a model declaring languages, params and arch_anchor beside a function that loads a local `params`. It reported languages and arch_anchor but not params. So MandateEntry.params is not reported, and growth is at most arch_anchor (test_only lane, like gemini_anchor at :195) and languages.
- load-bearing claim C23 (mandate) is UNPROVEN: Two parts hold: every review.yml field is required, and a missing file fails loud through require_file/load_model_file (loader.py:24-28, the same pattern as adr/host.py:28-33). The claim also says §4.4 records every built-in meaning the review gives an absent value, and the list leaves one out: an absent baseline file. load_baseline never returns None; absence is 'decided by the CALLER' (baseline.py:81-82). The current skill decides it by omitting drift (SKILL.md:140). The spec does not say what the rewritten step 7 does with an absent baseline_path, for drift or for staleness, which needs the baseline commit. It is not in §4.4's list. The case is live: this repository has no baseline (config/architecture holds only ARCHITECTURE.md, adr.yml and mandates.yml), and §5.7 deletes the origin baseline before running the review. So either an unrecorded built-in meaning re-enters for absence, or the first run fails loud. The spec establishes neither.
- load-bearing claim C26 (mandate) is UNPROVEN: The enumerated items hold: anchor_line is shared by missing_anchors (registry.py:220-223) and doctrine_section; extract_json_block replaces parser.py:53-63; write_text_record replaces the two write bodies. But the design adds a new glob matcher, acf.repo.path_matches, for surface, exclude and include patterns. The package keeps fnmatch for allowlist_globs (facade_sinks.py:59), which §4.2 hands to the same row's auditor next to path_matches-governed surface keys, and for the ratchet's exclude_globs (fail_loud_ratchet.py:68). §10 calls this 'a second matching dialect'. The doctrine's practice for this lifted rule is to record current breaches in the section itself (:269-277). §6's doctrine edits retire one breach and record no new one. Whether path matching is 'the same operation' under two dialects, and where the breach is recorded, is not established.
- load-bearing claim C62 (mandate) is REFUTED: The claim rests on 'call_sites select gate sites and the review is not a gate'. The doctrine's own closed vocabulary (:156-157) includes `audit`, a non-gate site: acf-mandate SKILL.md:43 says 'audit is not a Tier-1 gate'. Every row in this repository and in both profiles that carries an `auditor` already declares it (mandates.yml:47, :138; react-app profile :42; python-service profile :97). The doctrine's scope paragraph says 'rows run where their call_sites say' (:10-11). So call_sites do not only select gate sites, and the vocabulary has a review site that this design bypasses rather than complies with. The amendment §6 makes leaves `audit` in the closed vocabulary with no meaning and no consumer, and the spec never says what `audit` means afterwards: retired, kept as an annotation, or required. The decision may be right for the origin's reasons (decision 17), but it is a doctrine change whose consequences go unstated, not compliance with the current rule.
- load-bearing claim C64 (mechanism_justification) is REFUTED: check_auditors runs at write time only when a row is written through the acf-mandate skill's prose validation snippet (SKILL.md:83-110). That snippet is a manual procedure, not a chokepoint. Several write paths bypass it:
- Hand edits.
- acf-setup's profile copy; acf-setup runs no mandate validation.
- The 25 origin rows the cutover writes.
In the origin, the CI-time auditor-pointer test (test_mandate_registry_drift.py:83-94) is deleted on the grounds that check_auditors replaces it. But origin CI cannot import acf (§5), so a bad origin `auditor` is refused only when the review next runs. That is the outcome the claim says is avoided. In this repository, no CI test runs check_auditors over the self-host or profile rows either: test_profile_drift.py:14 and tests/test_self_host.py:38 check only anchors.
- mandate claim C62 is REFUTED: The claim rests on 'call_sites select gate sites and the review is not a gate'. The doctrine's own closed vocabulary (:156-157) includes `audit`, a non-gate site: acf-mandate SKILL.md:43 says 'audit is not a Tier-1 gate'. Every row in this repository and in both profiles that carries an `auditor` already declares it (mandates.yml:47, :138; react-app profile :42; python-service profile :97). The doctrine's scope paragraph says 'rows run where their call_sites say' (:10-11). So call_sites do not only select gate sites, and the vocabulary has a review site that this design bypasses rather than complies with. The amendment §6 makes leaves `audit` in the closed vocabulary with no meaning and no consumer, and the spec never says what `audit` means afterwards: retired, kept as an annotation, or required. The decision may be right for the origin's reasons (decision 17), but it is a doctrine change whose consequences go unstated, not compliance with the current rule.

## Absorptions

- ADJACENT exclusion of plugins/arch-compliance/python/acf/adr/ledger.py:200-213 for responsibility 'create parent directory, write UTF-8 text, wrap OSError' is unjustified in writing
- PARTIAL_OVERLAP: 'acf.repo.path_matches' shares responsibility 'decide whether a repository-relative path matches a host glob' with plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:68 — Responsibility R is host-glob matching over repository keys. path_matches and fnmatch at fail_loud_ratchet.py:68 and facade_sinks.py:59 both implement R in different dialects. The spec records the second dialect in §10 rather than collapsing it, because collapsing would change hosts' existing exclude_globs and allowlist_globs meanings.
- PARTIAL_OVERLAP: 'review built-in test-path and exclusion lists (§4.7 step 2)' shares responsibility 'default list of test and vendor paths excluded from a whole-tree walk' with plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:57-63 — Responsibility R is the built-in test/vendor exclusion set for whole-tree scans. Both the ratchet default and the review's built-in lists hard-code overlapping entries (tests/, test_*.py, *_test.py, .venv/, node_modules/) in different dialects. A single named constant set in one module, with each consumer translating into its matcher, would collapse both. Otherwise the duplicate needs recording beside the §10 dialect note.
- PARTIAL_OVERLAP: 'pack `files` globs' shares responsibility 'map a file to the technology whose rules or detectors apply' with plugins/arch-compliance/python/acf/cli_check_diff.py:152 — Responsibility R is file-to-technology mapping, implemented by cli_check_diff.py:152/188, posttooluse_gate.py:50 and the pack files globs. The spec defers one shared map to part two (§3, §10).
- PARTIAL_OVERLAP: 'acf.review.rules.check_auditors' shares responsibility "validate a row's reference against a known set or an existing repository file" with plugins/arch-compliance/python/acf/registry.py:158-197 — Responsibility R is row-reference validation (known id set, else RepoTree.file existence). load_mandates does it for detector and llm prompt refs; check_auditors would do it for auditor refs. A load_mandates keyword (for example auditor_ids plus repo_root, which it already takes) would make check_auditors a consumer, and the unknown-reference error class could be unified.
- PARTIAL_OVERLAP: 'AuditorFinding exemption handling (unspecified)' shares responsibility "decide whether a finding's line is exempted by an inline token" with plugins/arch-compliance/python/acf/enforcement.py:27-35 — Responsibility R is inline-exemption decisions. Either the review applies token_exempted with the row's exemption_tokens to each parsed AuditorFinding (the rule prompts then omit exemption prose), or the spec states that auditors judge exemptions and records the second owner. HTML-comment forms need a decision either way.
- IDENTICAL: 'ts-js pack ui-logic-isolation hints' shares responsibility 'UI-logic tell regexes' with hm:scripts/core/architecture_review/ui_logic_prepass.py:31-52 — Named duplicate until part two moves the staged check onto acf.review.prepass (spec §8, §10).
- mechanism 'TechPack loader refusals (add-on without base, detectors key, non-rule hint keys, uncompilable pattern)' sits at rung 3 when rung 1 applies, with no written justification

## Converged findings

- [2 reviewers: compliance, sweeper] The new path matcher adds a second glob dialect beside the fnmatch matching of allowlist_globs and the ratchet's exclude_globs (and the ratchet's own default test-path set); the spec notes it in §10 but does not record it under `## Single point of definition`.
  - evidence: `plugins/arch-compliance/python/acf/detectors/facade_sinks.py:59`
  - evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:57-68`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/skills/architecture-review/SKILL.md:72; plugins/arch-compliance/skills/architecture-review/SKILL.md:35-38; ls plugins/arch-compliance/skills/architecture-review/auditors/ = fail-loud.md, no-shims.md, posix-paths.md, react-boundaries.md`
- reasoning: Line 72 lists the four default auditors. Lines 35-38 name the same four prompt files, and the auditors/ directory holds exactly those four.

#### C2 — SURVIVED
- evidence: `hm:.claude/skills/architecture-review/SKILL.md:3; hm:.claude/skills/architecture-review/SKILL.md:35-49; hm:.claude/skills/architecture-review/SKILL.md:53-61; hm:.claude/skills/architecture-review/SKILL.md:68-88; hm:.claude/skills/architecture-review/SKILL.md:123-145`
- reasoning: At b2611977f each capability is in the file. The frontmatter (:3) and step 3 (:68, :75-78) give nine auditors. Step 1 (:35-49) extracts the rubric. The frontend and family-template lists are per-auditor surfaces (:53-61). The ui_logic_prepass scan runs before dispatch (:80-88). Step 6b (:123-145) classifies finding provenance by blame.

#### C3 — SURVIVED
- evidence: `hm:.claude/skills/architecture-review/auditors/metadata-facade.md:3; hm:.claude/skills/architecture-review/auditors/output-agnosticism.md:12-25; hm:.claude/skills/architecture-review/auditors/three-tier-hfsm.md:11-13`
- reasoning: metadata-facade.md:3 names ContentMetadataService and index.yml. output-agnosticism.md:12-25 lists concrete scripts/ stage files. three-tier-hfsm.md:11-13 hard-codes tier path lists, which corroborates the same pattern.

#### C4 — SURVIVED
- evidence: `hm:scripts/core/architecture/registry.py:22; hm:scripts/core/architecture/registry.py:33; hm:scripts/core/architecture/registry.py:79`
- reasoning: MandateEntry has extra='forbid' (:22) and gemini_anchor: str (:33). It has no languages, params or arch_anchor field. load_mandates validates every row through it (:79), so a row carrying the plugin's fields would be rejected until the model changes.

#### C5 — SURVIVED
- evidence: `hm:scripts/core/architecture_review/baseline.py:67; hm:docs/architecture/compliance_baseline.json:7; hm:.claude/skills/architecture-review/auditors/three-tier-hfsm.md:47; yaml.safe_load of hm:config/architecture/mandates.yml (six rows with auditor three-tier-hfsm)`
- reasoning: aggregate keys counts on (result.mandate, subsystem) (:67). result.mandate is the auditor's free-text label, 'Three-Tier/HFSM' in the prompt's contract (:47) and in the baseline (:7). Loading the registry gives six rows with auditor three-tier-hfsm: three-tier, three-tier-batch, three-tier-ambient, §5, §5-fsm-mechanism and path-provenance. A count cannot be split back across those six ids.

#### C6 — SURVIVED
- evidence: `PYTHONUTF8=1 python yaml.safe_load over git show b2611977f:config/architecture/mandates.yml: 48 rows, 25 with auditor; hm:config/architecture/mandates.yml:14`
- reasoning: I ran the recipe. It printed 25 rows, and their id-to-auditor pairs match every row of the §5.2 table exactly, the grouping included.

#### C7 — SURVIVED
- evidence: `git grep -n -E 'last_run|build/architecture_review' b2611977f: code hits only hm:.claude/skills/architecture-review/SKILL.md:154 and hm:.cursor/skills/architecture-review/SKILL.md:154; other hits only in docs, e.g. hm:docs/plans/PLAN_ARCHITECTURE_REVIEW_SKILL.md:2108`
- reasoning: Recipe A, and a wider grep over the whole tree, find _last_run outside docs only at the writer and its Cursor twin. The comment at the writer says the file is for golden-summary generation. The only reader is a historical plan step in docs/plans. No live code or test reads the sidecar.

#### C8 — SURVIVED
- evidence: `hm:scripts/ci/check_arch_compliance_llm.py:45-55; hm:scripts/ci/check_arch_compliance_llm.py:77-93; hm:scripts/ci/arch_compliance/llm_judge.py:93; hm:scripts/ci/arch_compliance/llm_judge.py:293; hm:scripts/ci/arch_compliance/judge_calibration.py:61-62`
- reasoning: _mandate_ids_for_path returns only §5 or §6, so the judge only looks up those rows (:87-93). Their auditors are three-tier-hfsm and ui-logic-isolation. load_rubric builds <dir>/<name>.md (:93). judge_changed_file holds mandate.id at :293, so a name map keyed on the id is feasible. judge_calibration passes literal prompt names into load_rubric (:61-62).

#### C9 — SURVIVED
- evidence: `git grep -l -E '^(from|import) acf' b2611977f -- scripts tests: no output (rc=1); git grep -n -E '^\s*(from|import) acf\b' b2611977f: only hm:docs/design/ADR_GATE_HOST_CONTRACT.md:340 and an adr_runs doc`
- reasoning: The recipe prints nothing. A wider grep that allows indentation and covers the whole tree matches acf imports only inside docs code samples. No requirements or workflow file names acf.

#### C10 — SURVIVED
- evidence: `hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:360; hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:6474-6475`
- reasoning: Row :360 names only arch-compliance:adversarial-design-review and arch-compliance:responding-to-adversarial-review. The phase 1d outcome follow-up at :6474-6475 is also scoped to 'the two skills'. Nothing covers architecture-review.

#### C11 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:19; plugins/arch-compliance/python/acf/judge.py:260; plugins/arch-compliance/python/acf/judge.py:29-36`
- reasoning: The only file judge.py reads is _PROMPT_TEMPLATE = judge_prompt.md (:19, read at :260). A grep for auditor or skills in judge.py finds nothing. LLM_PROMPT_IDS holds detector ids such as llm_react_boundaries, not auditor names, so the auditor rename does not touch it.

#### C12 — SURVIVED
- evidence: `cy:cayenne-web/src/lib/features/bugReport/BugReportSheetBody.svelte:1; cy:cayenne-web/src/lib/features/bugReport/BugReportSheetBody.svelte:36; cy:cayenne-web/src/lib/features/bugReport/BugReportSheetBody.svelte:41`
- reasoning: The runes ($state( at :36, $derived( at :41) sit as plain text inside the <script lang="ts"> block that opens at :1. A regular expression over the raw file matches them, and a Read-only auditor sees them, so no extraction step is needed for hints.

#### C13 — SURVIVED
- evidence: `hm:config/architecture/ARCHITECTURE.md:9; hm:scripts/core/architecture_review/_e2e_helper.py:241; git grep arch-docs-manifest outside docs: only the pointer, the two SKILL.md copies and _e2e_helper`
- reasoning: Pointer line 9 names .claude/skills/architecture-review/rubric/arch-docs-manifest.yml, which is inside the deleted skill tree. Its other code consumers (rubric.py via SKILL.md, and _e2e_helper) are deleted, so the move needs only the pointer edit.

#### C14 — SURVIVED
- evidence: `yaml.safe_load set of gemini_anchor = 12 values; hm:GEMINI.md:100,108,114,120,127,139,171,181,206,221,251,270 (all twelve as '## ' headings); plugins/arch-compliance/python/acf/registry.py:220-223; hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:352`
- reasoning: There are twelve distinct anchors, and each equals a GEMINI.md heading line verbatim. missing_anchors tests stripped-line membership, so adding those exact lines to the pointer resolves every row. Line 352 records decision 5 as 'met only vacuously because this registry anchors with gemini_anchor'; the rename plus the headings meet it.

#### C15 — SURVIVED
- evidence: `hm:scripts/builders/fsm_base.py:54; hm:scripts/builders/fsm_base.py:67; hm:scripts/builders/fsm_base.py:79; hm:scripts/builders/fsm_base.py:95; hm:scripts/builders/fsm_base.py:43`
- reasoning: transition (:56) and transition_to (:69) both end in self._apply (:67, :79). _apply assigns current_state at :95, and the section comment at :54 calls these the only writers. One nuance: __init__ also sets the initial current_state at :43, so _apply is the only writer after construction.

#### C16 — SURVIVED
- evidence: `git grep -n -E 'auditors|react-boundaries' -- ':!docs' (outside the skill dir): config/architecture/mandates.yml:51; plugins/arch-compliance/profiles/react-app/mandates.yml:46; config/architecture/mandates.yml:142; plugins/arch-compliance/profiles/python-service/mandates.yml:101`
- reasoning: Outside the skill directory, the only consumers that name an auditor are the two react-boundaries rows §4.10 changes. The other react-boundaries hits are mandate ids (soft.react-boundaries) in fixtures and tests, not auditor names. The fail-loud rows keep a rule id that exists in §4.2. Inside the skill, only SKILL.md (rewritten) references auditors/.

#### C17 — REFUTED
- evidence: `hm:scripts/cms_server/routes/tuner_print.py:216; hm:config/architecture/mandates.yml:14; hm:scripts/core/exceptions.py:1525; hm:scripts/setup_git_hooks.py:137`
- reasoning: I reran recipes A, B and C. Most hits are dispositioned correctly, and grepping the deleted test-file names finds no CI job listing them; arch-guards.yml:41 runs test_mandate_registry_drift.py, which stays. The census still fails on three points. (1) The dead_code_baseline row's disposition says the ratchet will report MandateEntry.params as growth. It will not: vulture keeps one used_names set, and a Name load of `params` in scripts (tuner_print.py:216 and others) marks the field used (see C21). (2) Recipe B's 48 hits in hm:config/architecture/mandates.yml (gemini_anchor keys, e.g. :14) have no row in the census table; only §5.1's model-level wording covers them. (3) Recipe C's hit at exceptions.py:1525 (a docstring naming BaselineError) and the comment at setup_git_hooks.py:137 above the removed line are left undispositioned, so they go stale.

#### C18 — SURVIVED
- evidence: `recipe C plus SkillLayoutError/BaselineStalenessError grep: hm:scripts/core/architecture_review/aggregator.py:20; hm:scripts/core/architecture_review/facets.py:13; hm:scripts/core/architecture_review/baseline.py:17; hm:scripts/ci/baseline_staleness.py:88; hm:scripts/core/skill_install.py:17; hm:tests/test_arch_review_contract.py:13; hm:scripts/ci/arch_compliance/engine.py:815-843; hm:tests/test_type_registry_require.py:40`
- reasoning: Every raiser and importer is in a file §5.4 deletes: aggregator, rubric, facets, baseline, skill_install, baseline_staleness, and their tests. The exception is the name mirror in engine.py, which §5.4 edits. No other class subclasses the deleted bases. The mirror's only test consumer checks UnknownContentTypeError, not these names. The remaining reference is the exceptions.py:1525 docstring, which is prose.

#### C19 — SURVIVED
- evidence: `hm:scripts/setup_git_hooks.py:138; hm:tests/test_push_scope_hook.py:21; hm:tests/test_push_scope_hook.py:25-26; git grep baseline_staleness outside docs: only the module, its test, setup_git_hooks.py:138 and test_push_scope_hook.py`
- reasoning: The only invocation is the pre-push line at :138. The only test pin is test_push_scope_hook.py:21 and :25-26, where the ordering assertion becomes predicate < tier. No workflow or jobs.yml references the module. A cosmetic orphan remains: the comment at setup_git_hooks.py:137.

#### C20 — SURVIVED
- evidence: `hm:scripts/core/architecture_review/__init__.py:10; hm:tests/test_skill_install.py:7; git ls-tree -d --name-only b2611977f .cursor/skills/ = architecture-review only`
- reasoning: Grepping skill_install and its exported function names finds importers only in architecture_review/__init__.py and test_skill_install.py. test_mandate_registry_drift.py:86 reaches it through the wrapper, and that test is deleted by §5.4. The dead_code_baseline entry is regenerated. .cursor/skills holds only architecture-review.

#### C21 — REFUTED
- evidence: `hm:scripts/ci/dead_code_ratchet.py:493; hm:scripts/ci/dead_code_ratchet.py:408; hm:scripts/cms_server/routes/tuner_print.py:216; hm:config/architecture/dead_code_baseline.json:195`
- reasoning: The --update-baseline mode exists (:493), and growth is name-keyed set arithmetic (:377-380). The 'exactly three keys' half is false. The ratchet's findings come from vulture scans of scripts/ (scan A) and scripts+tests (scan B) (:408). Vulture 2.16 marks any Name load as used in one shared used_names set (visit_Name). `params` is loaded as a local variable throughout scripts (tuner_print.py:216, :255, :256). I ran an in-memory vulture scan of a model declaring languages, params and arch_anchor beside a function that loads a local `params`. It reported languages and arch_anchor but not params. So MandateEntry.params is not reported, and growth is at most arch_anchor (test_only lane, like gemini_anchor at :195) and languages.

#### C63 — SURVIVED
- evidence: `hm:scripts/ci/run_guards.py:113-125; hm:tests/test_run_guards.py:91-94; yaml.safe_load of origin registry: §11, §11-inventory, admin-literal-type-gating, admin-notification-mechanism are detection guard, status enforced, auditor set`
- reasoning: site_guard_modules collects every enforced guard row whose call_sites include the site (:113-125). Four auditor-bearing rows are enforced guards. Adding 'audit' to them makes site_guard_modules('audit') return their modules. That violates the fixture assertion at test_run_guards.py:91-94 and the zero-guard raise the test expects.

### Unanchored findings

- **important**: The §5.4 dead-code row says the cutover PR will state three growth keys, but vulture's name-based use check counts the many `params` locals in scripts, so MandateEntry.params is never reported and the PR's stated growth would be wrong.
  - evidence: `hm:scripts/cms_server/routes/tuner_print.py:216`
- **advisory**: Recipe B's gemini_anchor hits in the origin mandates file (48 row keys) have no row in the §5.4 census table; the rename of each row key is implied only by §5.1's model change.
  - evidence: `hm:config/architecture/mandates.yml:14`
- **advisory**: Recipe C matches a docstring naming BaselineError in a kept exception class; §5.4 deletes BaselineError but gives this stale prose reference no disposition.
  - evidence: `hm:scripts/core/exceptions.py:1525`
- **advisory**: Removing the pre-push staleness line leaves its preceding comment ('Advisory: warn when the compliance drift baseline is stale') orphaned unless it goes too.
  - evidence: `hm:scripts/setup_git_hooks.py:137`

### Looked for but did not find

- any live (non-docs) reader of build/architecture_review/_last_run.json
- a CI workflow or jobs.yml entry naming a test file §5.4 deletes (test_arch_baseline, test_arch_facets, test_arch_review_*, test_rubric_extract_section6, test_skill_install, test_baseline_staleness)
- a test pinning _HM_KNOWN_SUBCLASS_NAMES to the full exceptions.py class set, which would force more mirror edits
- an origin registry row lacking a detector value, which the plugin Mandate model requires
- an origin detector value containing ':' that the plugin would treat as a host detector row
- a call_sites value in the origin registry outside the plugin CallSite literal
- a reference to arch-docs-manifest.yml outside the pointer, the skill trees and _e2e_helper
- an import of scripts.core.architecture_review inside ui_logic_prepass.py that would break its move
- a Name or attribute load of 'languages' or 'arch_anchor' in origin scripts/

## compliance

### Claim verdicts

#### C22 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:206-212; plugins/arch-compliance/tests/test_adr_skill_prose.py:13-25`
- reasoning: The doctrine says skill prose and runtime messages name no host repository, path or section. Its prose row is test_adr_skill_prose.py, which today checks only the two gate skills and housekeeping against an enumerated FORBIDDEN list (:13-25). Spec §6 and §7 extend that check's FILES to architecture-review (rule prompts, _contract.md, SKILL.md) and the pack files, and §4.2 requires rule prompts to carry repository values only through settings. The claim, which covers prose scope only, holds as designed. Two related gaps are filed separately: the FORBIDDEN list does not cover the port's own vocabulary, and the acf.review runtime messages fall under neither row.

#### C23 — UNPROVEN
- evidence: `plugins/arch-compliance/python/acf/baseline.py:81-82; plugins/arch-compliance/skills/architecture-review/SKILL.md:140`
- reasoning: Two parts hold: every review.yml field is required, and a missing file fails loud through require_file/load_model_file (loader.py:24-28, the same pattern as adr/host.py:28-33). The claim also says §4.4 records every built-in meaning the review gives an absent value, and the list leaves one out: an absent baseline file. load_baseline never returns None; absence is 'decided by the CALLER' (baseline.py:81-82). The current skill decides it by omitting drift (SKILL.md:140). The spec does not say what the rewritten step 7 does with an absent baseline_path, for drift or for staleness, which needs the baseline commit. It is not in §4.4's list. The case is live: this repository has no baseline (config/architecture holds only ARCHITECTURE.md, adr.yml and mandates.yml), and §5.7 deletes the origin baseline before running the review. So either an unrecorded built-in meaning re-enters for absence, or the first run fails loud. The spec establishes neither.

#### C24 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_exceptions.py:35-45; plugins/arch-compliance/python/acf/exceptions.py:45-46`
- reasoning: Doctrine: every ACF exception subclasses AcfError and nothing else. Spec §4.8 and §6 add AuditorContractViolationError and ReportWriteError, each deriving from AcfError alone, and leave ReviewerContractViolationError(AcfError) unchanged (exceptions.py:45-46). The module-wide test at test_adr_exceptions.py:35-45 enforces single-base for every class in the module, so the new classes are covered without new test code.

#### C25 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:47-73; plugins/arch-compliance/tests/test_repo_tree_guard.py:99; plugins/arch-compliance/python/acf/adr/host.py:31-32`
- reasoning: Doctrine: acf.repo is the one declaration of host paths, stdlib-only, and RepoTree is the one place a path string becomes a location. REVIEW_REL joins ADR_REL in acf.repo. Loading it as `repo / REVIEW_REL` follows adr/host.py:31-32, and the guard spares constant joins (test_repo_tree_guard.py:99). RepoTree.files and path_matches are added inside acf/repo.py (stdlib-only matching is possible). Hatch prompts resolve through RepoTree.file and write targets through contained (§4.5, §4.7). Pack files ship inside the package, so they are not host paths.

#### C26 — UNPROVEN
- evidence: `plugins/arch-compliance/python/acf/detectors/facade_sinks.py:59; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:68; config/architecture/ARCHITECTURE.md:269-277`
- reasoning: The enumerated items hold: anchor_line is shared by missing_anchors (registry.py:220-223) and doctrine_section; extract_json_block replaces parser.py:53-63; write_text_record replaces the two write bodies. But the design adds a new glob matcher, acf.repo.path_matches, for surface, exclude and include patterns. The package keeps fnmatch for allowlist_globs (facade_sinks.py:59), which §4.2 hands to the same row's auditor next to path_matches-governed surface keys, and for the ratchet's exclude_globs (fail_loud_ratchet.py:68). §10 calls this 'a second matching dialect'. The doctrine's practice for this lifted rule is to record current breaches in the section itself (:269-277). §6's doctrine edits retire one breach and record no new one. Whether path matching is 'the same operation' under two dialects, and where the breach is recorded, is not established.

#### C27 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:91-99; config/architecture/ARCHITECTURE.md:224-226`
- reasoning: Doctrine: an export has a live call site in the package, a hook or a skill; a test is not a consumer. §4.8's table names a package or skill call site for each new export. The acf-mandate validation snippet that will call check_auditors exists today and already consumes missing_anchors (SKILL.md:91-99). anchor_line's consumer is missing_anchors plus doctrine_section. The pack `detectors` slot is refused, not built (§4.3, decision 11), and the sidecar is not ported (decision 15).

#### C28 — SURVIVED
- evidence: `pyproject.toml:3; plugins/arch-compliance/.claude-plugin/plugin.json:3; scripts/check_installed_skills.py:18-22`
- reasoning: Doctrine: a skill-prose change bumps plugin.json and pyproject.toml, and the installed-skill byte check covers the gate skills. Both version files read 0.2.5 today. §6 bumps both to 0.3.0 and extends GATE_SKILLS (check_installed_skills.py:18-22) to architecture-review. §5 step 1 adds a separate acf version check, because the doctrine (:260-262) says the byte check does not cover python/.

#### C29 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:19; HistoricMansions/scripts/ci/check_ui_prepass_staged.py:17`
- reasoning: Doctrine: a quantified tree claim needs a re-runnable recipe. The four population claims named each carry one: §5.4 recipes A-C, §4.10 `git grep -n "auditor:"`, §5 `git grep -l -E "^(from|import) acf"`, and recipe A for the sidecar. I re-ran recipe A's pattern over the origin checkout outside docs/. Every hit, for example check_ui_prepass_staged.py:17, appears in §5.4's table. §3's 'reads no auditor file' matches judge.py:19, its only prompt source. One scope mismatch is filed as advisory: §5 says 'No origin file' while its recipe searches only scripts/ and tests/.

#### C30 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:17-30; plugins/arch-compliance/python/acf/baseline.py:78-86`
- reasoning: Doctrine: errors surface; no silent defaults or masking. run_git returns the CompletedProcess with check=False (diff.py:17-30), so rev-list, merge-base and blame exit codes reach the report as data with git's stderr. A missing git raises FileNotFoundError from subprocess.run, which is not a typed AcfError but does fail the run. The merge-base --is-ancestor mapping (0, 1, other) matches git's contract. A FAILED auditor group keeps its raw payload and forces a non-zero exit (§4.7 step 6). None of these is a swallowed failure or a guessed cause.

#### C31 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/contract.py:129`
- reasoning: Doctrine: persisted paths are POSIX; this plugin refuses backslashes through PosixStr (contract.py:129). report_dir, baseline_path, the subsystems entries and AuditorFinding.path are PosixStr (§4.4, §4.8). Baseline subsystem keys derive from the PosixStr finding path. The rule-settings path keys (surface, docs, inventory, policy_files) are declared inputs, not persisted fields, and the spec does not type them PosixStr. The claim does not assert that they are.

#### C32 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:24-30; plugins/arch-compliance/python/acf/loader.py:60`
- reasoning: Doctrine: subprocess text calls declare encoding; run_git (diff.py:24-30) is recorded debt. The review adds no new subprocess call site; it calls run_git, the breach the doctrine already records. File reads go through load_model_file, which reads UTF-8 (loader.py:60), or explicit UTF-8 reads (§4.7). An advisory is filed: the new `git blame` callers decode source-file text, which widens how far the debt reaches on Windows.

#### C33 — SURVIVED
- evidence: `HistoricMansions/CLAUDE.md:128; HistoricMansions/scripts/ci/check_ui_prepass_staged.py:17`
- reasoning: The quote at hm:CLAUDE.md:128 matches the spec verbatim. §5.4 records recipes A-C and names the known sites they reproduce. My run of recipe A's pattern over the origin checkout outside docs/ returned 42 files, and each falls under a §5.4 row (for example check_ui_prepass_staged.py:17, the hm:.cursor skill tree, coverage_map.yml and engine.py).

#### C34 — SURVIVED
- evidence: `docs/design/ADR_GATE_HOST_CONTRACT.md:79-86; plugins/arch-compliance/python/acf/registry.py:220-223; HistoricMansions/config/architecture/ARCHITECTURE.md:1-16`
- reasoning: Decision 5: the doctrine is ARCH_REL plus the documents it points to; no doctrine field is declared; a pointer carries every arch_anchor heading. ReviewHostConfig has no doctrine field (§4.4). doctrine_section reads only ARCH_REL through anchor_line, which keeps missing_anchors' line equality (registry.py:220-223). The origin pointer today has no section headings (hm ARCHITECTURE.md:1-16). The origin's anchors are full '## N. …' lines (hm mandates.yml:14 and others), and their 12 distinct values match the twelve headings §5.5 adds.

#### C62 — REFUTED
- evidence: `config/architecture/ARCHITECTURE.md:156-157; plugins/arch-compliance/skills/acf-mandate/SKILL.md:43; config/architecture/mandates.yml:47`
- reasoning: The claim rests on 'call_sites select gate sites and the review is not a gate'. The doctrine's own closed vocabulary (:156-157) includes `audit`, a non-gate site: acf-mandate SKILL.md:43 says 'audit is not a Tier-1 gate'. Every row in this repository and in both profiles that carries an `auditor` already declares it (mandates.yml:47, :138; react-app profile :42; python-service profile :97). The doctrine's scope paragraph says 'rows run where their call_sites say' (:10-11). So call_sites do not only select gate sites, and the vocabulary has a review site that this design bypasses rather than complies with. The amendment §6 makes leaves `audit` in the closed vocabulary with no meaning and no consumer, and the spec never says what `audit` means afterwards: retired, kept as an annotation, or required. The decision may be right for the origin's reasons (decision 17), but it is a doctrine change whose consequences go unstated, not compliance with the current rule.

#### C68 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/parser.py:53-63; plugins/arch-compliance/python/acf/adr/run_detail.py:183-191`
- reasoning: Doctrine: within an approved change, fix the code paths you change; do not expand into unrelated modules. The parser.py change moves its fence, count and decode logic (:53-63) into the shared extractor, which the review needs and Single point of definition requires. The run_detail.py and baseline.py changes replace their mkdir/write/wrap bodies (run_detail.py:183-191, baseline.py:70-74) with write_text_record. Each is a call site of a helper this design introduces. Advisory, filed below: run_detail's error message carries operator advice beyond the POSIX path, and the spec's write_text_record message shape does not say it is kept.

### Unanchored findings

- **important**: Dropping call_sites from review selection leaves the closed-vocabulary site `audit` with no meaning or consumer, and the spec's doctrine sentence does not say what becomes of it, although every auditor row here and in both profiles declares it.
  - evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:43`
- **important**: The spec never says what happens when baseline_path does not exist (omit drift and staleness, or fail loud), yet this repository has no baseline and §5.7 deletes the origin's before running the review; whichever the answer, it belongs in §4.4's list of recorded absent-value meanings.
  - evidence: `plugins/arch-compliance/python/acf/baseline.py:81-82`
- **important**: path_matches adds a second glob dialect next to the fnmatch matching of allowlist_globs and the ratchet's exclude_globs, both in the same params namespace. §10 says so, but §6's doctrine edits do not record it under `## Single point of definition`, as that section's 'recorded not hidden' practice requires.
  - evidence: `plugins/arch-compliance/python/acf/detectors/facade_sinks.py:59`
- **important**: The new acf/review package's runtime messages and the pack YAML fall under neither name-no-host check: the code-portability test scans only acf/adr, and the extended FORBIDDEN list lacks the vocabulary this port carries over (for example HistoricMansions, §-section numbers, origin class names).
  - evidence: `plugins/arch-compliance/tests/test_adr_code_portability.py:7-8`
- **advisory**: §5 says 'No origin file imports acf today', but its recipe searches only `-- scripts tests`, so the recipe does not cover the quantifier's scope (`## No completeness claims`).
  - evidence: `config/architecture/ARCHITECTURE.md:230-232`
- **advisory**: The new `git blame` callers decode arbitrary source text through run_git, which uses the locale codec. On Windows a non-ASCII line raises UnicodeDecodeError instead of producing a returncode, so the recorded encoding debt now reaches the review's provenance step.
  - evidence: `plugins/arch-compliance/python/acf/diff.py:24-30`
- **advisory**: §6 rewords the anchor rule to line equality only at acf-mandate :46, :109-110 and acf-setup :138-139; acf-setup:115 and acf-mandate:67 still say 'literal substrings' and 'exact string must appear'.
  - evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:115`
- **advisory**: write_text_record's message shape is the POSIX path plus the OSError, but run_detail's current error carries operator advice that the spec does not say is kept. This could change the ADR gate's behaviour, which the scoped-refactor claim says stays unchanged.
  - evidence: `plugins/arch-compliance/python/acf/adr/run_detail.py:187-191`

### Looked for but did not find

- ## One base exception: the new exceptions derive from AcfError alone and the module-wide test covers them. No mixin.
- ## Frozen ledger format: no LedgerRow or LedgerAmendment field changes; run_detail's writer is not the ledger. Not touched.
- ## Build artifacts: no generated tree is staged. Not touched.
- ## Fail-loud ratchet: its file walk and fnmatch excludes are explicitly left unchanged (§10). Not touched.
- ## Façade sinks / ## FSM transitions: the review reuses their params key names but does not change the detectors' row rules (id equals mandate id, Tier-1 site). Not touched.
- ## Soft fail-loud smells / ## React boundaries: the soft.fail-loud row's auditor stays a rule id; React boundaries is named as governing and edited (§6).
- ## Post-merge: no host operational declaration changes.
- ## High-frequency misses: walked each. Completeness recipes present except the §5 scope (advisory). Default re-entering: absent baseline (important). Host vocabulary: runtime and FORBIDDEN gaps (important). Stdlib mixin: none. Subprocess text without encoding: no new call site. Check re-implemented in a skill: anchor resolution, check_auditors and load_mandates are consumed from the package.
- unstated_mandates is empty: the spec's Governing mandates line names every doctrine section this design touches. The sections it leaves out are cleared above as not touched.

## sweeper

### Claim verdicts

#### C35 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/host.py:19-33; plugins/arch-compliance/python/acf/repo.py:12-26; config/architecture/mandates.yml:96-99`
- reasoning: AdrHostConfig (host.py:19-25) is extra=forbid, built on require_file plus load_model_file, so ReviewHostConfig copies an existing shape. acf.repo declares MANDATES_REL, ARCH_REL, ADR_REL and RATCHET_BASELINE_REL, and none of them is a review report directory, a compliance baseline path, a staleness threshold, a pack list or a subsystem list. adr.yml carries only runs_dir and ledger_path. The nearest existing host-level exclusion is the fail_loud_ratchet row's params.exclude_globs (mandates.yml:99), which is scoped to that one detector, not to a repository-wide review tree. Rows' `languages` is per row, not a repository technology list. I found no field duplicated in adr.yml, mandates.yml or ARCH_REL.

#### C36 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/finding.py:11-19; plugins/arch-compliance/python/acf/baseline.py:59-65; plugins/arch-compliance/tests/test_baseline.py:63-73`
- reasoning: Finding carries BLOCK/WARN severity plus detector, confidence and detection, and has no snippet, why or suggested_fix, as the spec says. aggregate reads only finding.mandate_id and finding.path (baseline.py:63), so typing it on a two-field protocol changes no behaviour and one aggregation serves both models. Its consumers are SKILL.md:117 (removed with the rewrite) and test_baseline.py:70.

#### C37 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/parser.py:26; plugins/arch-compliance/python/acf/adr/parser.py:53-70; plugins/arch-compliance/python/acf/judge.py:303-317`
- reasoning: I searched by behaviour for the fence regex, `(?P<body>`, '```json' and json.loads across the plugin's python, hooks and tests. The only fenced-JSON extractor is parser.py:26/53-70. judge.py:303-317 (_parse_json_object) extracts a bare JSON object (raw text, then `\{.*\}`), not a fenced block. That is a different contract for a different provider response, so it stays ADJACENT. test_adr_parser.py:46 and :132-133 pin the message text ('no ```json fenced block', raw payload echoed), so extract_json_block has to keep that wording for 'tests unchanged' to hold.

#### C38 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/baseline.py:70-74; plugins/arch-compliance/python/acf/adr/run_detail.py:183-191; plugins/arch-compliance/python/acf/approval.py:7-10`
- reasoning: I grepped for mkdir(parents and write_text( across the package. Five writers exist: baseline.py:71-72, run_detail.py:184-185, approval.py:179-185 (temp file plus os.replace), ledger.py:202-213 (append-only with preamble) and, once added, the review report. The claim names only the first two plus the report, and those share the exact shape: make the parent, write UTF-8 text, wrap OSError with the POSIX path. approval.py and ledger.py have different write semantics (atomic replace, append). approval.py:7-10 and docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:128 already justify in writing that approval shares no helper with save_baseline, so the exclusion is recorded.

#### C39 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:220-223; plugins/arch-compliance/python/acf/judge.py:258-269`
- reasoning: I grepped for missing_anchors, arch_anchor, heading and section extraction across the plugin's python and skills. The only resolver is missing_anchors (registry.py:222-223, stripped-line set membership). judge.py:266 passes mandate.arch_anchor into the prompt template as a literal string without resolving or extracting it. No section extractor exists today; adversarial-design-review reviewers read ARCHITECTURE.md whole. acf-setup/SKILL.md:137-139 does a by-eye anchor check in prose, which the spec rewords and the doctrine already records (ARCHITECTURE.md:275-276).

#### C40 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:16; plugins/arch-compliance/python/acf/cli_check_diff.py:188; plugins/arch-compliance/hooks/posttooluse_gate.py:50`
- reasoning: Language = Literal['python','typescript','both','none'] (registry.py:16). Pack `language` takes a subset of it, so the design adds no third language vocabulary. The gate routes only .py and {.ts,.tsx} (cli_check_diff.py:152, :188) and the hook only {.py,.ts,.tsx} (posttooluse_gate.py:50), so a ts-js pack covering .js/.mjs/.cjs really does have a different extent, and naming it differently is justified. Pack `files` globs do add a third file-to-technology map; the spec defers unifying the maps (§3, §10), and the count is recorded below.

#### C41 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/facade_sinks.py:21-27; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:58-59; plugins/arch-compliance/python/acf/detectors/fsm_guard.py:18-23`
- reasoning: facade_sink_args reads target_literal_re, allowlist_globs and atomic_is_sink, and matches allowlist_globs with fnmatch.fnmatch (:59). fsm_guard_args reads state_field and validator_name. Both pick known keys with params.get and ignore any other key, so rule keys on the same row do not disturb the detectors. The claim's two enumerated rules reuse exactly those names. Decision 10 as written is broader, though: see the unanchored finding on the fail-loud rule's surface/surface_exclude versus the ratchet's roots/exclude_globs.

#### C42 — SURVIVED
- evidence: `hm:scripts/core/architecture_review/ui_logic_prepass.py:31-52; hm:scripts/ci/check_ui_prepass_staged.py:17`
- reasoning: A case-insensitive grep for 'prepass' and 'pre-pass' over the plugin's python, hooks and skills finds no pre-pass, and the plugin has no regex candidate scanner over files. The origin tell set (_TELLS, ui_logic_prepass.py:31-52) stays in the moved gate module for its staged-check consumer, and the ts-js pack copies it. That is the named duplicate the spec records in §8.

#### C43 — SURVIVED
- evidence: `plugins/arch-compliance/profiles/react-app/mandates.yml:46; plugins/arch-compliance/profiles/python-service/mandates.yml:101; config/architecture/mandates.yml:51`
- reasoning: I redid the sweep by behaviour as well as by key: grep for 'auditor:', "'auditor'", '"auditor"', 'auditor=' and 'react-boundaries' over the tree excluding docs. Rows with an auditor are mandates.yml:51 (react-boundaries), :142 (fail-loud), react-app:46 (react-boundaries) and python-service:101 (fail-loud). No test, fixture or Python code builds a Mandate with an auditor value (registry.py:61 is the only code mention). The remaining react-boundaries hits are mandate ids or the llm_react_boundaries prompt id, not auditor values.

#### C44 — SURVIVED
- evidence: `tests/test_self_host.py:40; plugins/arch-compliance/tests/test_profile_drift.py:30; plugins/arch-compliance/tests/test_registry.py:60; plugins/arch-compliance/skills/acf-mandate/SKILL.md:99`
- reasoning: A grep for missing_anchors outside docs gives exactly these four call sites, plus doctrine mentions (ARCHITECTURE.md:276, :296). All four call missing_anchors(registry, text) and compare the list result, so a rewrite with the same signature and result leaves them unchanged.

#### C45 — SURVIVED
- evidence: `config/architecture/mandates.yml:41-51; config/architecture/mandates.yml:132-142; plugins/arch-compliance/profiles/react-app/mandates.yml:36-46; plugins/arch-compliance/profiles/python-service/mandates.yml:91-101`
- reasoning: None of the four auditor rows has a params block. The rows that do carry params (ops.no-build-artifacts, fail-loud.ratchet, facade.forbid-sink, fsm.transition-guard) carry no auditor. The judge does not read params (its only `params=` is an HTTP query, judge.py:168).

#### C46 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_baseline.py:8-17; plugins/arch-compliance/skills/architecture-review/SKILL.md:115`
- reasoning: I grepped for 'acf.baseline', 'from acf import baseline', aggregate(, subsystem_of( and save_baseline( outside docs. The only importers are test_baseline.py:8 and the skill snippet SKILL.md:115-137. approval.py:7 names save_baseline in a docstring only. Note that test_baseline.py:52-60 calls subsystem_of with one argument, and §6 does not list those lines (see advisory).

#### C47 — SURVIVED
- evidence: `hm:scripts/core/architecture/registry.py:33; hm:tests/test_mandate_registry_drift.py:62; hm:config/architecture/dead_code_baseline.json:195`
- reasoning: A field rename is read by attribute or key name, so a name grep is the behaviourally correct sweep here. In the HM working tree outside docs, gemini_anchor appears at registry.py:33, test_arch_mandate_registry.py (24, 48, 65, 81, 90), test_mandate_registry_drift.py (43, 60, 62), test_run_guards.py:111, dead_code_baseline.json:195 and 48 data keys in config/architecture/mandates.yml. A grep for 'anchor' in scripts/ci/arch_compliance and scripts/core/architecture_review finds no other reader. Recipe B therefore covers every reader. The census table does not list the 48 mandates.yml data keys the recipe also prints (advisory).

#### C65 — SURVIVED
- evidence: `hm:scripts/core/architecture/registry.py:21-34; config/architecture/mandates.yml:142; plugins/arch-compliance/profiles/python-service/mandates.yml:101`
- reasoning: In this repository and the profiles, the non-ast/guard reviewed rows (mandates.yml:51, :142; react-app:46; python-service:101) carry no params at all. Origin MandateEntry has extra=forbid and no params field (hm registry.py:21-34), so no origin row has params today. I checked every key §5.2 assigns against the §4.2 table plus RuleSettings (surface, surface_exclude, docs): exception_base, exempt_paths, path_types, tiers/crossings, base_classes, classifier, target_literal_re/allowlist_globs/inventory, the stage lists/variant_terms/raw_sources/canonical_artifact, element_key/variant_key, and facades. Each is a key its rule declares.

#### C67 — SURVIVED
- evidence: `hm:scripts/core/architecture_review/contract.py:16; plugins/arch-compliance/python/acf/adr/contract.py:38`
- reasoning: The origin auditor Severity is Literal['blocking','important','nit','suggestion'] (hm contract.py:16), and the ADR gate's is Literal['blocking','important','advisory'] (adr/contract.py:38). The four-level set is a straight port of the origin contract. No review severity feeds a block decision (drift and provenance never change exit status, §4.7).

#### C69 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:57-68; config/architecture/mandates.yml:99`
- reasoning: The ratchet matches repository keys with fnmatch.fnmatch (:68), where `*` crosses `/` and `**/test_*.py` does not match a root-level test_x.py. Under the spec's path_matches, `**` stands for zero or more segments and `*` for characters within one segment, so the same host glob (mandates.yml:99) would select different files. Keeping the ratchet's dialect and recording it in §10 avoids silently changing hosts' exclude_globs. facade_sinks.py:59 is a second fnmatch site that the review also keeps (allowlist_globs).

### Unanchored findings

- **important**: The spec does not say who decides inline exemptions for review findings. The origin ui-logic-isolation auditor and the plugin react-boundaries auditor tell the LLM to honour exemption comments, including `<!-- §6-ok -->` and `arch-ok: §6` forms, while the package's single owner acf.enforcement.token_exempted recognises only `#`/`//` row exemption_tokens. Porting the prompts without a decision gives exemption two owners, and either origin vocabulary in rule prompts or HTML-comment exemptions the gate cannot see.
  - evidence: `plugins/arch-compliance/python/acf/enforcement.py:27-35; plugins/arch-compliance/skills/architecture-review/auditors/react-boundaries.md:53; hm:.claude/skills/architecture-review/auditors/ui-logic-isolation.md:47-60`
- **advisory**: Decision 10 says a rule's settings keys reuse the key names of the built-in detector that checks the same subject. The fail-loud rule scopes files with RuleSettings surface/surface_exclude (path_matches), while the fail_loud_ratchet detector on the same subject scopes with roots/exclude_globs (fnmatch). A ratchet row given `auditor: fail-loud` would declare its file scope twice in two dialects, contrary to the 'declared once on one row' claim.
  - evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:57-68; config/architecture/mandates.yml:96-99`
- **advisory**: `subsystem_of takes the declared prefix list` changes a function that test_baseline.py:52-60 calls with one argument, but §6 lists only test_baseline.py:8-17 and :63-73 as edits.
  - evidence: `plugins/arch-compliance/tests/test_baseline.py:52-60`
- **advisory**: check_auditors repeats the reference-validation shape load_mandates already owns (a known-set check plus RepoTree.file existence for a host-named file, raising UnknownDetectorError), yet raises UnknownMandateError, which the skill uses for an unknown --mandates id. Two validators of row references, with two error classes for one kind of fault.
  - evidence: `plugins/arch-compliance/python/acf/registry.py:158-197; plugins/arch-compliance/skills/architecture-review/SKILL.md:67`
- **advisory**: Recipe B prints the 48 `gemini_anchor:` data keys in hm:config/architecture/mandates.yml, which must be renamed because MandateEntry is extra=forbid. The §5.4 census table gives that file only the recipe-A row (:516), so the rename's largest site set has no disposition row.
  - evidence: `hm:scripts/core/architecture/registry.py:22; hm:config/architecture/mandates.yml:14`

### Looked for but did not find

- a second fenced-JSON extractor: grep for '```json', '(?P<body>', 'fenced' and json.loads across plugins/arch-compliance python, hooks and tests (judge.py:303 extracts bare JSON, which is adjacent)
- a second anchor resolver or doctrine-section extractor: grep for arch_anchor, missing_anchors, heading, section and startswith("#" in the package and skills
- an existing pre-pass or regex candidate scanner in the plugin: grep -i 'prepass|pre-pass|tell' and re.compile/finditer over acf/
- an existing repository-wide review host declaration or REVIEW_REL-like constant: acf/repo.py constants and the config/architecture/ listing
- other auditor-value writers or readers: grep for 'auditor:', "'auditor'", '"auditor"', 'auditor=' and react-boundaries outside docs
- other acf.baseline consumers: grep for 'acf.baseline', 'from acf import baseline', aggregate(, subsystem_of( and save_baseline( outside docs
- rows that carry both an auditor and params: read config/architecture/mandates.yml and both profiles
- origin readers of gemini_anchor beyond recipe B: grep for 'anchor' in hm scripts/ci/arch_compliance and scripts/core/architecture_review
- detectors that refuse unknown params keys (which would make shared flat params collide): facade_sink_args, fsm_guard_args, build_artifacts and the cli_check_diff ratchet params reads; all ignore unknown keys

### Relationships

- ADJACENT: `acf.agent_payload.extract_json_block` — responsibility `extract and decode a JSON object from LLM output text` — existing `plugins/arch-compliance/python/acf/judge.py:303-317`
  - resolution: none; different input contract (bare JSON with brace-search fallback versus exactly one fenced block)
  - non-merge: The judge parses a provider response that is a bare JSON object and tolerates surrounding prose. The reviewer and auditor contracts require exactly one fenced block and refuse anything else. Merging would loosen one contract or tighten the other.
- ADJACENT: `acf.loader.write_text_record` — responsibility `create parent directory, write UTF-8 text, wrap OSError with the POSIX path` — existing `plugins/arch-compliance/python/acf/approval.py:179-192`
  - resolution: none
  - non-merge: approval.py:7-10 and HOST_DETECTOR_LOCAL_APPROVAL.md:128 record that the per-user store is replaced atomically (temp file plus os.replace) under concurrent writers, so it shares no helper with the in-place baseline write.
- ADJACENT: `acf.loader.write_text_record` — responsibility `create parent directory, write UTF-8 text, wrap OSError` — existing `plugins/arch-compliance/python/acf/adr/ledger.py:200-213`
  - resolution: none
- PARTIAL_OVERLAP: `acf.repo.path_matches` — responsibility `decide whether a repository-relative path matches a host glob` — existing `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:68`
  - resolution: Responsibility R is host-glob matching over repository keys. path_matches and fnmatch at fail_loud_ratchet.py:68 and facade_sinks.py:59 both implement R in different dialects. The spec records the second dialect in §10 rather than collapsing it, because collapsing would change hosts' existing exclude_globs and allowlist_globs meanings.
- PARTIAL_OVERLAP: `review built-in test-path and exclusion lists (§4.7 step 2)` — responsibility `default list of test and vendor paths excluded from a whole-tree walk` — existing `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:57-63`
  - resolution: Responsibility R is the built-in test/vendor exclusion set for whole-tree scans. Both the ratchet default and the review's built-in lists hard-code overlapping entries (tests/, test_*.py, *_test.py, .venv/, node_modules/) in different dialects. A single named constant set in one module, with each consumer translating into its matcher, would collapse both. Otherwise the duplicate needs recording beside the §10 dialect note.
- PARTIAL_OVERLAP: `pack `files` globs` — responsibility `map a file to the technology whose rules or detectors apply` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:152`
  - resolution: Responsibility R is file-to-technology mapping, implemented by cli_check_diff.py:152/188, posttooluse_gate.py:50 and the pack files globs. The spec defers one shared map to part two (§3, §10).
- PARTIAL_OVERLAP: `acf.review.rules.check_auditors` — responsibility `validate a row's reference against a known set or an existing repository file` — existing `plugins/arch-compliance/python/acf/registry.py:158-197`
  - resolution: Responsibility R is row-reference validation (known id set, else RepoTree.file existence). load_mandates does it for detector and llm prompt refs; check_auditors would do it for auditor refs. A load_mandates keyword (for example auditor_ids plus repo_root, which it already takes) would make check_auditors a consumer, and the unknown-reference error class could be unified.
- PARTIAL_OVERLAP: `AuditorFinding exemption handling (unspecified)` — responsibility `decide whether a finding's line is exempted by an inline token` — existing `plugins/arch-compliance/python/acf/enforcement.py:27-35`
  - resolution: Responsibility R is inline-exemption decisions. Either the review applies token_exempted with the row's exemption_tokens to each parsed AuditorFinding (the rule prompts then omit exemption prose), or the spec states that auditors judge exemptions and records the second owner. HTML-comment forms need a decision either way.
- IDENTICAL: `ts-js pack ui-logic-isolation hints` — responsibility `UI-logic tell regexes` — existing `hm:scripts/core/architecture_review/ui_logic_prepass.py:31-52`
  - resolution: Named duplicate until part two moves the staged check onto acf.review.prepass (spec §8, §10).
- ADJACENT: `acf.review.contract.AuditorFinding` — responsibility `carry one finding with mandate_id and POSIX path` — existing `plugins/arch-compliance/python/acf/finding.py:11-19`
  - resolution: Shared protocol (mandate_id, path) consumed by acf.baseline.aggregate
  - non-merge: Different severity scale (four review levels versus BLOCK/WARN) and different provenance fields (detector, confidence, detection versus snippet, why, suggested_fix), stated in spec §4.8.

### Two-owner counts

- file-to-technology mapping: 3
- host-glob matching dialects over repository keys: 2
- built-in test/vendor exclusion list for whole-tree scans: 2
- inline exemption-token decision: 2
- row-reference validation (known set or repository file): 2
- UI-logic tell regex set: 2
- mkdir-parent plus UTF-8 write plus OSError wrap: 3
- git subprocess runner: 2

### Document conflicts

- `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:128` (restates): the approval store is a per-user file read and rewritten by concurrent processes, so it is replaced whole rather than written in place, and no helper is shared
- `docs/design/ADR_GATE_HOST_CONTRACT.md:82` (restates): A pointer file still carries every heading its mandates' `arch_anchor` values name, because the plugin matches those as literal substrings of this file

## hardening

### Claim verdicts

#### C48 — SURVIVED
- evidence: `hm:.claude/skills/architecture-review/auditors/metadata-facade.md:3; hm:scripts/core/architecture_review/contract.py:41`
- reasoning: The origin auditor prose hard-codes host values in the rule text itself: metadata-facade.md:3 names `ContentMetadataService` and `index.yml` inside the principle. Copying auditors per repository would therefore repeat that prose with host data baked in. The three-layer split puts host values in params and technology shapes in packs, which removes the mixing. The hatch covers the residue that does not generalise.

#### C49 — SURVIVED
- evidence: `hm:scripts/core/architecture_review/contract.py:41; hm:scripts/core/architecture_review/contract.py:26`
- reasoning: The origin identifies each result by a free-text `mandate: str` (contract.py:41) and each finding by a free-text `rule: str` (:26). Nothing ties either to a registry row. Grouping by `auditor` caps dispatches at the number of distinct auditor values: 25 origin rows collapse to 9 rule ids per §5.2. Requiring `mandate_id` to be one of the group's rows is a refusal at the parse boundary, so free-text identity becomes a checked one.

#### C50 — SURVIVED
- evidence: `hm:.claude/skills/architecture-review/SKILL.md:90; hm:scripts/core/architecture_review/contract.py:58`
- reasoning: This is the origin's existing per-auditor FAILED policy (SKILL.md:90; the statuses Literal at contract.py:58), ported. It is not a silent repair: the raw payload and error are kept, the group is marked FAILED and the exit status is non-zero. The producer of the bad state is an external LLM agent, which is a genuine boundary. Aborting the whole run would discard valid findings from other groups without making the bad payload any louder.

#### C51 — SURVIVED
- evidence: `hm:scripts/ci/baseline_staleness.py:65-75; plugins/arch-compliance/python/acf/baseline.py:26-31`
- reasoning: The plugin Baseline already carries `generated_at` and `commit` (baseline.py:26-31), which is everything the staleness check needs. No origin file imports acf, so keeping the check in origin CI would add a dependency there. The port also hardens it. The origin swallowed a missing git (`except OSError: return None`, baseline_staleness.py:71-72) and conflated it with 'commit not in history' (:73-74). The spec makes a missing git raise and reports git's own error text.

#### C52 — SURVIVED
- evidence: `scripts/check_installed_skills.py:18-34; config/architecture/ARCHITECTURE.md:256-262`
- reasoning: The origin stage runs `/arch-compliance:architecture-review` through the installed plugin, which cannot happen before 0.3.0 is released and installed. The installed-skill check compares skill trees only (check_installed_skills.py:18-34, ARCHITECTURE.md:256-262), so the spec's added acf.__file__ / version / HEAD record is what closes the Python half. Fixing plugin defects by patch release before the origin merge keeps the dependency order acyclic.

#### C53 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:50-62; plugins/arch-compliance/python/acf/registry.py:91-109; plugins/arch-compliance/python/acf/loader.py:71`
- reasoning: `Mandate` declares no model_config (registry.py:50-62), so pydantic's default extra='ignore' tolerates `remediation`. I ran yaml.safe_load over hm:config/architecture/mandates.yml@b2611977f: 48 rows; detection values all fall within ast/llm/grep/guard/manual; call_sites all fall within ci/precommit/posttooluse/audit; every detector is non-null and contains no ':', so no row is a host row. All 42 active ast/guard rows declare precommit or ci, which satisfies the Tier-1 check at registry.py:99. `_check_builtin` only runs when known_detectors is passed (registry.py:164), and the review passes none. `Language` includes python, typescript and none (registry.py:16).

#### C54 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:61-62; plugins/arch-compliance/python/acf/cli_check_diff.py:157; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:21-27`
- reasoning: `auditor: str | None` and `params: dict[str, Any] | None` exist (registry.py:61-62), and params is constrained only to JSON values (:75-88). The built-in detectors read params flat and pick only their own keys (facade_sinks.py:21-27; fsm_guard.py:18-23; build_artifacts.py:15-18). Extra rule keys on the same row therefore do not break the gate.

#### C55 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:53-73; pyproject.toml:5; .github/workflows/ci.yml:20`
- reasoning: contained, file and directory exist (repo.py:53-69), and key (:71-73) yields the repo-relative POSIX key a matcher needs. Path.glob treats an interior `**` as zero or more directories: Path('.').glob('**/pyproject.toml') returned the root pyproject.toml. The floor is >=3.11 (pyproject.toml:5). Caveat, filed separately: Path.glob alone cannot give §4.7 step 2's other forms, so it may serve only as a walker.

#### C56 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:24-30; plugins/arch-compliance/python/acf/diff.py:33-39`
- reasoning: run_git calls subprocess.run with check=False and has no try (diff.py:24-30). A non-zero exit therefore comes back as returncode data, and a missing git binary raises FileNotFoundError uncaught. `_git` (:33-39) is the existing consumer that turns status into GitError, which confirms that status-as-data is the runner's contract.

#### C57 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/parser.py:53-70; plugins/arch-compliance/tests/test_adr_parser.py:46-57; plugins/arch-compliance/tests/test_adr_exceptions.py:35-45`
- reasoning: Lines 53-70 are pure extraction: fence match, the zero and many checks, and json.loads. They are parameterised only by the reviewer name (usable as `subject`) and the exception class. The identity and schema checks (:72-98) stay in parse_reviewer_payload. The tests match on message substrings ('no ```json fenced block', 'multiple \(2\)', 'JSON parse failed'), so they pass if the helper keeps those strings. The only external importer is acf/adr/__init__.py:25 (parse_reviewer_payload). A new AuditorContractViolationError(AcfError) satisfies the whole-module single-base test (test_adr_exceptions.py:35-45).

#### C58 — SURVIVED
- evidence: `hm:scripts/ci/dead_code_ratchet.py:504-512; hm:scripts/ci/dead_code_ratchet.py:387-409`
- reasoning: `--update-baseline` (:493) re-runs both vulture scans over the working tree's scripts/ and tests/ (:387-409) and writes fresh lanes (:504-512). Note: --update-baseline seeds silently. The growth rows are printed only by the default --check path (:555, :567-569), so the PR has to run --check before regenerating to observe the three growth keys it states.

#### C59 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_skill_prose.py:13-25; plugins/arch-compliance/tests/test_adr_skill_prose.py:42-47`
- reasoning: The check is a plain FILES list scanned line by line for FORBIDDEN literals (:13-25, :42-47). Adding the architecture-review tree and the pack YAML files is a list extension. Caveat, filed as advisory: FORBIDDEN contains 'docs/reviews' and 'docs/architecture'.

#### C60 — SURVIVED
- evidence: `hm:scripts/ci/arch_compliance/llm_judge.py:304; hm:scripts/ci/check_arch_compliance_llm.py:45-53`
- reasoning: judge_changed_file receives the mandate object and already uses mandate.id at :304. The only ids the caller routes are '§5' and '§6' (check_arch_compliance_llm.py:45-53), so a two-entry dict keyed on mandate.id at :293 is in scope. The tests monkeypatch load_rubric with signature (auditor, repo_root=None) and still receive a name.

#### C61 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:71-73; hm:scripts/ci/check_arch_compliance_llm.py:40-42`
- reasoning: I mapped each listed pattern to exactly one form:
- whole path with `**`: pack globs `**/*.ts`, `admin/js/**/*.js`, `**/*.test.*`;
- trailing `/**`: `admin/js/vendor/**`;
- `*` within one segment: `templates/families/*/style.yml`;
- single segment with trailing `/`, any depth: `tests/`, `archive/`;
- multi-segment trailing `/`, from the root: `docs/reviews/`;
- basename (no `/`): `test_*.py`.
No pattern satisfies two forms with different results. git ls-tree of origin@b2611977f shows nested `scripts/tests`, `tests/tests` and `docs/archive`, all deterministically covered by the any-depth rule. The origin judge's narrower `startswith('tests/')` (check_arch_compliance_llm.py:40-42) is a different, separate predicate. Keys come from RepoTree.key (repo.py:71-73) as POSIX.

#### C64 — REFUTED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:83-110; hm:tests/test_mandate_registry_drift.py:83-94; plugins/arch-compliance/tests/test_profile_drift.py:14`
- reasoning: check_auditors runs at write time only when a row is written through the acf-mandate skill's prose validation snippet (SKILL.md:83-110). That snippet is a manual procedure, not a chokepoint. Several write paths bypass it:
- Hand edits.
- acf-setup's profile copy; acf-setup runs no mandate validation.
- The 25 origin rows the cutover writes.
In the origin, the CI-time auditor-pointer test (test_mandate_registry_drift.py:83-94) is deleted on the grounds that check_auditors replaces it. But origin CI cannot import acf (§5), so a bad origin `auditor` is refused only when the review next runs. That is the outcome the claim says is avoided. In this repository, no CI test runs check_auditors over the self-host or profile rows either: test_profile_drift.py:14 and tests/test_self_host.py:38 check only anchors.

#### C66 — SURVIVED
- evidence: `pyproject.toml:2-3; pyproject.toml:31-32`
- reasoning: The distribution name is 'acf' and its package is found under plugins/arch-compliance/python (pyproject.toml:31-32), so importlib.metadata.version('acf') reads the installed dist-info. For an editable install that dist-info is frozen at install time, so it shows 0.3.0 only after a reinstall. That is a loud mismatch, not a silent pass, and acf.__file__ plus HEAD close the remaining gap. No git tag is involved.

### Unanchored findings

- **important**: The cutover deletes the origin's CI-time auditor-pointer test and relies on check_auditors, which origin CI cannot run. An invalid or typo'd `auditor` in the origin registry moves from refused at commit (rung 3 at the producer) to refused only at the next review run. The spec states no replacement CI check and adds none for this repository's own self-host or profile rows.
  - evidence: `hm:tests/test_mandate_registry_drift.py:83-94`
- **advisory**: On ast/guard rows, params keys the rule does not declare are listed in the report rather than refused (§4.2). A typo'd rule key (for example `surfce`) silently falls back to the absent-key default. Yet for built-in detector rows the detector's key set is fixed in code (facade_sink_args, fsm_guard_args, build_artifact_args), so rule keys plus detector keys could be refused exactly, leaving list-only tolerance for host-detector rows.
  - evidence: `plugins/arch-compliance/python/acf/detectors/facade_sinks.py:21-27`
- **advisory**: If RepoTree.files passes include patterns to pathlib.Path.glob rather than walking and filtering every key through path_matches, it becomes a second matching dialect:
- On 3.11/3.12 (CI runs 3.12) a trailing `/**` yields directories only.
- On 3.13 a trailing `/**` also yields files.
- Path.glob cannot express the any-depth `tests/` or basename forms.
The spec should state that Path.glob is used only as a walker.
  - evidence: `.github/workflows/ci.yml:20`
- **advisory**: The forbidden-vocabulary list contains 'docs/reviews' and 'docs/architecture'. The spec's own §4.7 step 2 example pattern `docs/reviews/` would fail the extended prose test if the rewritten SKILL.md reproduced it.
  - evidence: `plugins/arch-compliance/tests/test_adr_skill_prose.py:20-25`

### Looked for but did not find

- A silent repair in the payload path: the FAILED-group policy keeps the raw payload and error and forces a non-zero exit (cleared).
- A soft git fallback in staleness or provenance: the spec removes the origin's `except OSError: return None` (hm:scripts/ci/baseline_staleness.py:71-72) and lets a missing git raise through run_git (cleared).
- A migration shim for `auditor: react-boundaries` rows in existing hosts: none is added; check_auditors raises UnknownMandateError and the README note documents it (fail loud, no shim; cleared).
- Repair-on-load in the pack or host-declaration loaders: TechPack and ReviewHostConfig are extra='forbid' with refusals for an add-on without its base, a detectors key, unknown hint keys and backslash paths (cleared).
- A second producer of anchor resolution: anchor_line becomes the single decision procedure under missing_anchors and doctrine_section (cleared).
- The existing backslash normalisation in acf.baseline.subsystem_of (baseline.py:52) is pre-existing, not added by this design; AuditorFinding.path is PosixStr, so the repair is unreachable for review findings (not traced).

### Mechanism traces

- **acf.review.rules.check_auditors**
  - invalid state: an active row whose auditor is set and is neither a key of RULES nor a path ending in .md that RepoTree.file resolves, or whose params fail the rule settings model's types
  - producer: `plugins/arch-compliance/profiles/react-app/mandates.yml:46`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/ARCHITECTURE_REVIEW_PORT.md:141`
- **finding mandate_id must be one of the group's rows**
  - invalid state: AuditorFinding.mandate_id not in the set of ids of the rows dispatched in that group
  - producer: `hm:scripts/core/architecture_review/contract.py:41`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: the auditor is an external LLM agent; its output is a genuine boundary validated at parse
  - spec citation: `docs/design/ARCHITECTURE_REVIEW_PORT.md:147`
- **contract violation marks the group FAILED and the run continues with a non-zero exit**
  - invalid state: an auditor final message with zero or several ```json blocks, undecodable JSON, or JSON failing the AuditorFinding schema
  - producer: `hm:.claude/skills/architecture-review/SKILL.md:90`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: one malformed payload should not discard the other groups' findings; the producer is an external agent
  - spec citation: `docs/design/ARCHITECTURE_REVIEW_PORT.md:168`
- **baseline staleness warning in the roll-up**
  - invalid state: today - Baseline.generated_at > baseline_max_age_days, or git rev-list --count <Baseline.commit>..HEAD > baseline_max_commits, or that rev-list exits non-zero
  - producer: `plugins/arch-compliance/python/acf/baseline.py:68-75`
  - rung 5 (highest applicable 5); repairs=False
  - hardening rejected because: decision 8: staleness is report-only and moves from the origin pre-push hook into the review roll-up; drift never changes exit status
  - spec citation: `docs/design/ARCHITECTURE_REVIEW_PORT.md:169`
- **undeclared params keys listed per row on ast/guard rows**
  - invalid state: a key in Mandate.params of an ast/guard row that is declared neither by the row's rule settings model nor by the row's detector
  - producer: `plugins/arch-compliance/python/acf/registry.py:62`
  - rung 5 (highest applicable 3); repairs=True
  - hardening rejected because: keys the rule does not declare may belong to the row's detector, so the report lists them per row
  - spec citation: `docs/design/ARCHITECTURE_REVIEW_PORT.md:74`
- **declared surface matching no file fails loud; empty target tree raises EmptyTargetTreeError**
  - invalid state: RepoTree.files(surface, ...) returns an empty set for a row with surface declared, or the resolved target tree is empty
  - producer: `hm:config/architecture/mandates.yml`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/ARCHITECTURE_REVIEW_PORT.md:165`
- **unresolved arch_anchor fails loud with the mandate id**
  - invalid state: a reviewed row whose arch_anchor.strip() equals no stripped line of ARCH_REL
  - producer: `plugins/arch-compliance/python/acf/registry.py:220-223`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/ARCHITECTURE_REVIEW_PORT.md:154`
- **TechPack loader refusals (add-on without base, detectors key, non-rule hint keys, uncompilable pattern)**
  - invalid state: a pack file whose extends names an undeclared pack, which carries a detectors key, whose hints keys are not in RULES, or which has a pattern that re.compile rejects
  - producer: `plugins/arch-compliance/python/acf/registry.py:16`
  - rung 3 (highest applicable 1); repairs=False
  - spec citation: `docs/design/ARCHITECTURE_REVIEW_PORT.md:110`

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
- **C21** [premise] [load-bearing]: The origin dead-code ratchet has an --update-baseline mode (dead_code_ratchet.py:493) that regenerates its baseline; after the cutover edits the ratchet, which matches keys by name, reports exactly three keys as growth: MandateEntry.arch_anchor, MandateEntry.languages and MandateEntry.params.
  - spec citation: `hm:scripts/ci/dead_code_ratchet.py:377-380,493`
- **C22** [mandate] [load-bearing]: Rule prompts, the rewritten skill and the pack files name no host (`## Prose names no host`), and the forbidden-vocabulary test is extended to the skill directory and the pack files.
  - spec citation: `config/architecture/ARCHITECTURE.md:204-213`
- **C23** [mandate] [load-bearing]: The design complies with `## Declared, never defaulted`: review.yml fields are all required and a missing file fails loud; the section is extended to name review.yml and records every built-in meaning the review gives an absent or empty value: the built-in exclusion list, the built-in test-path list, an absent surface, an empty subsystems list, and absent rule settings (every rule settings key is optional; an absent scalar turns its check off, an absent list is empty).
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
- **C30** [mandate] [load-bearing]: The design complies with `## Fail loud` and `## No shims`: an auditor contract violation marks the group FAILED, keeps the raw payload and exits non-zero; a non-zero rev-list is reported as "staleness unknown" with git's own error text, provenance maps merge-base --is-ancestor exit 0/1/other to pre-baseline/post-baseline/unresolved, a failed blame is unresolved with git's text, and a missing git raises; no git failure is reported as a guessed cause.
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
- **C41** [shape_fit] [load-bearing]: Rule settings read from the row's flat params with one key vocabulary shared with the row's detector (single-owner and state-machine-discipline reuse the facade.forbid-sink and fsm.transition-guard key names and, for allowlist_globs, its fnmatch matching rule); on one row a fact both need is declared once, and across rows it may repeat as between detector rows today.
  - spec citation: `config/architecture/ARCHITECTURE.md:80-94; §2 row 10; §4.2`
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
- **C61** [implementability] [load-bearing]: One matcher, acf.repo.path_matches, gives every include, surface and exclusion pattern the spec and its origin declaration use (pack globs, admin/js/**/*.js, admin/js/vendor/**, templates/families/*/style.yml, tests/, test_*.py, **/*.test.*, docs/reviews/-style multi-segment directories, archive/) a single unambiguous meaning under the three pattern forms of §4.7 step 2.
  - spec citation: `§4.7 step 2`
- **C62** [mandate] [load-bearing]: Selecting review rows by `auditor` independently of `call_sites`, with a sentence added to the call-site rule saying so, complies with `## Host detectors and call sites` (rows run where their call_sites say), because call_sites select gate sites and the review is not a gate.
  - spec citation: `config/architecture/ARCHITECTURE.md:142-186; §4.5`
- **C63** [premise] [load-bearing]: Adding `audit` to the origin's reviewed rows instead would make the origin guard runner run enforced guard rows that declare it and conflict with hm:tests/test_run_guards.py:86-98; this is why decision 17 rejects it.
  - spec citation: `hm:scripts/ci/run_guards.py:105-130`
- **C64** [mechanism_justification] [load-bearing]: acf.review.rules.check_auditors, called by the review and by the acf-mandate validation snippet, refuses a bad auditor value when the row is written rather than only when the review next runs.
  - spec citation: `§4.5`
- **C65** [sweep] [load-bearing]: No reviewed row whose detection is not ast or guard, in this repository, the profiles or origin §5.2, carries a params key its named rule does not declare, so refusing undeclared keys on such rows rejects no row the spec relies on.
  - spec citation: `§4.2; §5.2`
- **C66** [implementability] [load-bearing]: The installed acf reports its version through importlib.metadata as 'acf' (pyproject name), so the cutover PR can record version 0.3.0, acf.__file__ and that checkout's HEAD without a git tag.
  - spec citation: `pyproject.toml:2-3; §5`
- **C67** [shape_fit]: AuditorFinding's four-level severity is justified against both the gate's BLOCK/WARN and the ADR gate's three-level Severity (acf/adr/contract.py:38), because it ports the origin auditor contract's levels and feeds no block decision.
  - spec citation: `§4.8`
- **C68** [mandate]: The edits to acf/adr/parser.py, acf/adr/run_detail.py and acf/baseline.py stay within `## Scoped refactor`, as call sites of the helpers this design introduces.
  - spec citation: `config/architecture/ARCHITECTURE.md:280-284; §4.8`
- **C69** [shape_fit]: Keeping the fail-loud ratchet's own fnmatch file walk, recorded in §10 as a second matching dialect, is preferable to moving it onto path_matches, which would change the meaning of hosts' existing exclude_globs.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:57-68; §10`
