# Adversarial design review — full detail

Spec: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` @ `9c8c283747f2e95bdc9aa348e2e89542f2c6ac06`
Kinds: defect, feature
Outcome: **BLOCKED**
Claims: 83 · Reviewers: 4 · Converged: 3

## Blocking reasons

- load-bearing claim C39 (mandate) is REFUTED: The lifted rule (verified at HM GEMINI.md:136) requires 'exactly one canonical implementation that every call site consumes'. The anchor check (registry.py:63-65), the detector union (cli_check_diff.py:25) and id uniqueness (registry.py:46-51) each have one definition, and the drift test, host test and /acf-mandate snippet consume them. 'Host paths one owner (acf.repo)' is false after this design: the executable snippet at architecture-review/SKILL.md:62 is `reg = load_mandates(Path("config/architecture/mandates.yml"))`, a second spelling of acf.repo.MANDATES_REL. The doctrine's high-frequency misses (206-208) name this exact shape. The doctrine's 'Current breach, recorded not hidden' (186-189) records only the two git runners, so this breach is hidden. Scoped refactor means the design need not change the snippet, but the single-point claim and the breach record must cover it.
- load-bearing claim C58 (sweep) is REFUTED: The claimed hit set is exactly what Glob docs/design/{ADR_,ARCH_COMPLIANCE_}*.md returns, so it is a name sweep. The claim itself demands a behaviour sweep. Swept by subject: ADVERSARIAL_DESIGN_REVIEW.md ('Approved design v1') is the gate's own origin spec. Everything it designs (the four-reviewer gate, claim extraction, the skills, the package) now lives in this plugin. It belongs with ADR_PER_FINDING_REVISION_CLASSING and ADR_REVISION_EVIDENCE..., which the spec includes as gate-behaviour specs, yet it is absent from section 1, section 7 and the section 10 disposition table. Likewise, ARCH_COMPLIANCE_SHIFT_LEFT_GATING is included even though it designs HM's own scripts/ci gating. On that same criterion, ARCHITECTURE_COMPLIANCE_FRAMEWORK.md (the ACF origin spec) and its TIER2/TIER3 siblings would also qualify. The inclusion rule is inconsistent and the list misses at least one instance.
- load-bearing claim C80 (implementability) is REFUTED: Read in-process, I dropped each heading line from the doctrine text and called missing_anchors on the host registry. For 12 anchors the row is reported. For `## Fail loud` (:24, anchor of two BLOCK rows) and `## React boundaries` (:92) it returns []. ARCHITECTURE.md:17 quotes both headings in backticks, and registry.py:65 tests only `arch_anchor in doctrine_text`. So removing either heading does not fail test_every_anchor_is_in_the_doctrine, and DoD item 2 is false for 2 of 14 anchors. The other two legs hold. A missing adr.yml makes load_model_file raise AcfInputError in test 1. A repeated id makes _registry() raise in tests 2 and 3.
- load-bearing claim C81 (implementability) is UNPROVEN: Python detection via the root pyproject.toml is sure. The TypeScript side is judgment prose with no deterministic hook. The tracked TS is three bridge sources (scan.ts, rules/emptyCatch.ts, rules/explicitAny.ts) and two fixtures. The only package.json is the private detector package, not 'a clear app package'; spec §5.2 itself says 'no React app'. Three files is hardly a 'substantial tree'. The plan (docs/plans/PLAN_PLUGIN_SELF_HOSTING.md:78) pre-answers languages = both and says 'announce this if detection says Python only', so the author does not rely on the clauses firing. The merge outcome is verified (see C65): one ops.no-build-artifacts row with languages: both, and stock anchors verbatim. That the clauses detect TypeScript is not shown. The fix is to state that the user answers 'both', as the plan already does.
- mandate claim C38 is REFUTED: The rule (T3: 'Universally quantified claim | Recipe backing the quantifier, or delete the quantifier'; doctrine 146-156) is not applied to this spec throughout. §0 (lines 29-31) asserts 'Every unprefixed citation in this spec is a full repository-relative path with no shorthand' with no recipe, and the spec itself falsifies it: `:47` at line 114, `:32-44` at line 257, the bare `ARCH_COMPLIANCE_FOR_SUPERPOWERS.md` at line 108, and `bad_except.py:4`, `bad.tsx:4`, `diff.py:28`, `citations.py:64`, `typescript_bridge.py:53` at lines 564-567. The controller had to resolve these as shorthand. Census item 15 (lines 175-176) asserts a negative, 'the package has no anchor-check function', and no appendix row backs it (the row at line 571 covers detector-union spellings only). The census's other per-item rows and the per-item DoD do hold; the self-application claim as stated does not.
- mandate claim C39 is REFUTED: The lifted rule (verified at HM GEMINI.md:136) requires 'exactly one canonical implementation that every call site consumes'. The anchor check (registry.py:63-65), the detector union (cli_check_diff.py:25) and id uniqueness (registry.py:46-51) each have one definition, and the drift test, host test and /acf-mandate snippet consume them. 'Host paths one owner (acf.repo)' is false after this design: the executable snippet at architecture-review/SKILL.md:62 is `reg = load_mandates(Path("config/architecture/mandates.yml"))`, a second spelling of acf.repo.MANDATES_REL. The doctrine's high-frequency misses (206-208) name this exact shape. The doctrine's 'Current breach, recorded not hidden' (186-189) records only the two git runners, so this breach is hidden. Scoped refactor means the design need not change the snippet, but the single-point claim and the breach record must cover it.
- implementability claim C80 is REFUTED: Read in-process, I dropped each heading line from the doctrine text and called missing_anchors on the host registry. For 12 anchors the row is reported. For `## Fail loud` (:24, anchor of two BLOCK rows) and `## React boundaries` (:92) it returns []. ARCHITECTURE.md:17 quotes both headings in backticks, and registry.py:65 tests only `arch_anchor in doctrine_text`. So removing either heading does not fail test_every_anchor_is_in_the_doctrine, and DoD item 2 is false for 2 of 14 anchors. The other two legs hold. A missing adr.yml makes load_model_file raise AcfInputError in test 1. A repeated id makes _registry() raise in tests 2 and 3.
- implementability claim C81 is UNPROVEN: Python detection via the root pyproject.toml is sure. The TypeScript side is judgment prose with no deterministic hook. The tracked TS is three bridge sources (scan.ts, rules/emptyCatch.ts, rules/explicitAny.ts) and two fixtures. The only package.json is the private detector package, not 'a clear app package'; spec §5.2 itself says 'no React app'. Three files is hardly a 'substantial tree'. The plan (docs/plans/PLAN_PLUGIN_SELF_HOSTING.md:78) pre-answers languages = both and says 'announce this if detection says Python only', so the author does not rely on the clauses firing. The merge outcome is verified (see C65): one ops.no-build-artifacts row with languages: both, and stock anchors verbatim. That the clauses detect TypeScript is not shown. The fix is to state that the user answers 'both', as the plan already does.
- implementability claim C83 is REFUTED: There are five manual rows and all five detector files exist under plugins/arch-compliance/tests/. But plugin.prose-names-no-host's title is 'Skill prose and runtime messages name no host'. Its detector, test_adr_code_portability.py, scans only acf/adr/*.py and two runtime strings in parser.py and gate.py; it reads no skill prose. Skill prose is checked by test_adr_skill_prose.py, which spec §5.2's table names as this row's source while the registry points elsewhere. So that detector does not enforce the named rule.

## Absorptions

- PARTIAL_OVERLAP: 'acf.registry.missing_anchors' shares responsibility "decide whether each row's arch_anchor is a literal substring of the doctrine" with plugins/arch-compliance/skills/acf-setup/SKILL.md:137 — missing_anchors is the one decider; /acf-setup Step 9's smoke check runs the /acf-mandate Validate snippet (load_mandates + KNOWN_DETECTORS + missing_anchors), and the Step 6 prose drops its by-eye check in favour of that command
- SUBSUMED: 'acf.cli_check_diff.KNOWN_DETECTORS consumers (snippet, drift test, host test)' shares responsibility 'name the set of detector ids a row may reference' with plugins/arch-compliance/python/acf/detectors/python_pack.py:25 — PYTHON_DETECTOR_IDS is a subset alias of a component of KNOWN_DETECTORS with no remaining consumer; delete it (and its re-export at detectors/__init__.py:9,35) or name its live consumer
- SUBSUMED: 'scripts/check_installed_skills.py' shares responsibility 'byte-compare the installed gate skills with the clone' with C:/Users/iball/Arduino/Projects/HistoricMansions/docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:669-681 — The script is the generalized container (clone as parameter, exit codes); the HM block stays as an executed record, and HM's live install instruction (hm CLAUDE.md:17) consumes the script (filed in section 10)
- IDENTICAL: 'tests/test_check_installed_skills.py SKILLS tuple' shares responsibility 'name the two gate skills' with scripts/check_installed_skills.py:18 — The test reads GATE_SKILLS from the module it already loads via _load_script() instead of re-spelling it
- IDENTICAL: 'docs/design/ADR_GATE_HOST_CONTRACT.md' shares responsibility "state the gate's host contract" with C:/Users/iball/Arduino/Projects/HistoricMansions/docs/design/ADR_GATE_HOST_CONTRACT.md:1 — Temporary by design: section 5.7 step 6 replaces HM's body with a stub naming this path; the provenance block marks this copy as the moved one
- mechanism 'Repeated-id refusal in load_mandates' sits at rung 3 when rung 1 applies, with no written justification

## Converged findings

- [2 reviewers: compliance, hardening] The plugin.prose-names-no-host row (status enforced) names plugins/arch-compliance/tests/test_adr_code_portability.py as its detector, which scans only acf/adr modules and two runtime strings and reads no skill prose; the skill prose this design changes (/acf-mandate SKILL.md) is checked by no test, and spec section 5.2 names test_adr_skill_prose.py as the row's source while the registry points elsewhere.
  - evidence: `config/architecture/mandates.yml:181-190`
  - evidence: `plugins/arch-compliance/tests/test_adr_code_portability.py:7`
  - evidence: `plugins/arch-compliance/tests/test_adr_skill_prose.py:12-19`
- [2 reviewers: refuter, compliance] Section 0's assertion that every unprefixed citation is a full repository-relative path with no shorthand (and that HM paths carry hm:) is false in the spec's own text: shorthand such as `:47`, `ARCHITECTURE.md`, `bad_except.py:4`, `diff.py:28` and unprefixed HM names (`GEMINI.md`, the section 10 table) appear, with no recipe backing the universal.
  - evidence: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:29-31`
  - evidence: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:114`
  - evidence: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:564-567`
- [2 reviewers: refuter, sweeper] Moving the /acf-mandate snippet to KNOWN_DETECTORS left the narrower alias PYTHON_DETECTOR_IDS exported with no consumer and a false comment ('used by CLI / drift tests'), against the doctrine's own ## Live consumers rule on a surface this design touched.
  - evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:24-25`
  - evidence: `plugins/arch-compliance/python/acf/detectors/__init__.py:9`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `git show c0281bf:.gitignore line 8 '.acf/'; git ls-tree --name-only c0281bf -> .claude-plugin .github .gitignore LICENSE README.md SECURITY.md docs plugins pyproject.toml; git ls-tree c0281bf config -> empty; plugins/arch-compliance/python/acf/repo.py:12 (CONFIG_DIR config/architecture, absent at base); plugins/arch-compliance/python/acf/repo.py:29 (ENABLED_REL .acf/enabled)`
- reasoning: Read the base tree directly. No config/ directory, .gitignore:8 is '.acf/', root documents are README.md and SECURITY.md only, and there is no CLAUDE.md at c0281bf.

#### C2 — SURVIVED
- evidence: `git ls-tree -r --name-only c0281bf docs -> docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md, docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md (v1 text, header 'draft v1 ... main at 8dabe82'), docs/guides/..., docs/plans/... ; no docs/reviews; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:102 (file unchanged c0281bf..HEAD)`
- reasoning: At the base, docs/design holds exactly those two files and docs/reviews/ is absent. Side note: docs/plans/PLAN_PLUGIN_SELF_HOSTING.md also already existed at c0281bf. This does not contradict the claim.

#### C3 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/host.py:24-25 (runs_dir, ledger_path, extra=forbid at :22); plugins/arch-compliance/python/acf/adr/host.py:30 (require_file ARCH_REL); plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:36 (the gate's only host read is load_host_config); plugins/arch-compliance/skills/adversarial-design-review/reviewers/compliance.md:12; plugins/arch-compliance/skills/adversarial-design-review/reviewers/compliance.md:47`
- reasoning: AdrHostConfig has exactly two fields with extra=forbid. load_host_config requires the doctrine at ARCH_REL. Grepping ADR_REL/load_host_config shows the gate and responding skills read host values only through it. compliance.md:12 and :47 say what the spec quotes. host.py is unchanged since c0281bf.

#### C4 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:110; plugins/arch-compliance/profiles/python-service/mandates.yml:34; plugins/arch-compliance/profiles/react-app/mandates.yml:23`
- reasoning: SKILL.md:110 reads verbatim as quoted. I loaded both profiles with yaml: the only shared id is ops.no-build-artifacts, and the two row dicts compare equal (languages: both). So the 'should not for stock profiles' parenthetical is false, and a two-language merge reaches the stop-and-ask. The profiles are unchanged since c0281bf.

#### C5 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:95-96 (targets); plugins/arch-compliance/skills/acf-setup/SKILL.md:105-116 (merged pair); plugins/arch-compliance/skills/acf-setup/SKILL.md:140-145 (Step 7 writes .acf/enabled); README.md:20`
- reasoning: Step 5 writes config/architecture/mandates.yml and ARCHITECTURE.md, merging both profiles for a polyglot host. Step 7 writes .acf/enabled. README.md:20 reads as quoted, and so did the base README.

#### C6 — SURVIVED
- evidence: `plugins/arch-compliance/tests/fixtures/python/bad_except.py:4; plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:4; plugins/arch-compliance/python/acf/enforcement.py:50; plugins/arch-compliance/python/acf/cli_check_diff.py:121; ran PYTHONUTF8=1 PYTHONPATH=plugins/arch-compliance/python python -m acf.cli_check_diff --repo . --base dfff93f5 --json at HEAD -> exit 0, 5 WARN (bad.tsx:7,:8 explicit-any; hasattr at test_adr_exceptions.py:22, test_adr_import_graph.py:46, test_adr_skill_prose.py:53)`
- reasoning: dfff93f5 is the root commit (rev-list --max-parents=0) and holds only one .md file, so --base dfff93f5 covers every code line. The CLI at HEAD gives the five WARN and exits 0. For the base code I could not make a worktree, so I reproduced it in memory: c0281bf content of every .py/.ts/.tsx through scan_python_file/scan_typescript_file and apply_registry with this branch's config/architecture/mandates.yml. Result: exactly 7 findings, 2 BLOCK (bad_except.py:4 fail-loud.bare-except, bad.tsx:4 fail-loud.empty-catch) plus the same 5 WARN. The only code differences c0281bf..HEAD that affect findings are the two token lines; the removed lines in test_profile_drift.py, test_registry.py and registry.py carry no findings.

#### C7 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:9; plugins/arch-compliance/python/acf/registry.py:19; plugins/arch-compliance/python/acf/registry.py:56; plugins/arch-compliance/python/acf/cli_check_diff.py:70`
- reasoning: Detection includes 'manual', and detector is a required str. The known-detector check runs only for enforced rows with detection in {ast, guard}, and only when known_detectors is passed. A manual row's detector is never checked, so a test-module path loads; the host registry loads through cli_check_diff with KNOWN_DETECTORS and five manual rows.

#### C8 — SURVIVED
- evidence: `git show c0281bf:plugins/arch-compliance/python/acf/registry.py lines 32-34 (by_id = {m.id: m for m in self.mandates}) and lines 37-53 (no repeat check); plugins/arch-compliance/python/acf/loader.py:67-71 (list validation, no id check); plugins/arch-compliance/python/acf/enforcement.py:43 (consumer uses by_id)`
- reasoning: At the base, load_mandates validates the rows and checks detectors only; it never compares ids. The loader just validates each row. by_id is a dict comprehension, so the last row with a repeated id wins. apply_registry looks rows up through by_id, so the first row is silently shadowed.

#### C9 — SURVIVED
- evidence: `git show c0281bf:plugins/arch-compliance/skills/acf-mandate/SKILL.md lines 91-97; plugins/arch-compliance/python/acf/detectors/python_pack.py:25; plugins/arch-compliance/python/acf/detectors/build_artifacts.py:10; plugins/arch-compliance/python/acf/detectors/__init__.py:11-18`
- reasoning: The base snippet builds known = PYTHON_DETECTOR_IDS | TS_DETECTOR_IDS | LLM_PROMPT_IDS. PYTHON_DETECTOR_IDS = PYTHON_AST_DETECTOR_IDS (three AST ids); guard ids live in GUARD_DETECTOR_IDS. I evaluated that union and loaded both stock profiles with it. Both raised: UnknownDetectorError: enforced mandate 'ops.no-build-artifacts' references unknown detector 'no_build_artifacts'. The detectors directory is unchanged since c0281bf.

#### C10 — SURVIVED
- evidence: `git show c0281bf:plugins/arch-compliance/skills/acf-mandate/SKILL.md line 104; plugins/arch-compliance/skills/acf-mandate/SKILL.md:105-107 (HEAD replacement)`
- reasoning: Line 104 at c0281bf reads 'Also verify each `arch_anchor` is a substring of `config/architecture/ARCHITECTURE.md` (same discipline as profile drift tests).'

#### C11 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:25; git show c0281bf:plugins/arch-compliance/tests/test_profile_drift.py lines 13 and 30-34; git grep -n 'arch_anchor' c0281bf -- plugins/arch-compliance/python -> only registry.py:23 (field) and judge.py:154 (prompt variable)`
- reasoning: git grep 'KNOWN_DETECTORS =' at c0281bf finds cli_check_diff.py:25 and test_profile_drift.py:13 in code; the third hit is a plan document. The drift test checks anchors with its own loop. The base package has no anchor-check function.

#### C12 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:24-30; plugins/arch-compliance/python/acf/adr/citations.py:62-65; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:49-56; plugins/arch-compliance/skills/acf-mandate/SKILL.md:111; .github/workflows/ci.yml:11`
- reasoning: grep -rn 'text=True' over python/ and hooks/ finds exactly diff.py:28, citations.py:64 and typescript_bridge.py:53, none with an encoding; those are the only subprocess calls in the package and hooks. This node's locale is cp1252 with utf8_mode 0. I decoded each 'git diff dfff93f5...HEAD -U0 -- <file>' as cp1252: four fail on U+201D (bytes e2 80 9d; 0x9d is undefined in cp1252), including plugins/arch-compliance/skills/acf-mandate/SKILL.md and architecture-review/SKILL.md. CI is ubuntu-latest.

#### C13 — SURVIVED
- evidence: `CLAUDE.md:35-36 (PYTHONUTF8 Windows note); .github/workflows/ci.yml:11 (ubuntu-latest); plugins/arch-compliance/python/acf/adr/citations.py:103 (ls-files); plugins/arch-compliance/python/acf/adr/citations.py:86; plugins/arch-compliance/python/acf/adr/citations.py:98; plugins/arch-compliance/hooks/posttooluse_gate.py:254`
- reasoning: The Windows note exists and CI is Linux. The only callers of acf.diff are cli_check_diff (the diff gate the note covers, including /acf-setup's smoke run). The hooks do not call git. The acceptance run's citation classification goes through citations._git, whose stdout is ASCII: ls-files has no non-ASCII tracked names (checked), rev-list prints SHAs, rev-parse prints true/false, check-ignore -q prints nothing. The TS bridge's scanner sources are pure ASCII, so its output decodes. I found no step that sends non-cp1252 bytes through these calls on Windows without the note.

#### C14 — SURVIVED
- evidence: `git show c0281bf:.github/workflows/ci.yml lines 34-39 (pytest, then npm test; no cli_check_diff step; checkout without fetch-depth); .github/workflows/ci.yml:39-40 (step added on branch)`
- reasoning: The base workflow runs pip install, npm ci, pytest and the TS self-test only. The diff-gate step and fetch-depth: 0 exist only on the branch.

#### C15 — UNPROVEN
- evidence: `plugins/arch-compliance/tests/test_adr_host_acceptance.py:74; plugins/arch-compliance/tests/test_adr_host_acceptance.py:80-91; ~/.claude/plugins/installed_plugins.json (installedAt 2026-10-22)`
- reasoning: The cited half holds: the test builds a fixture host under tmp_path and drives load_host_config, classify_citations, write_run_detail and append_row through the Python API, with no skill run. The uncited half ('a live skill run from the installed plugin has not happened outside HM') is a universal negative over other repositories that I cannot re-derive. The plugin repo at c0281bf has no docs/reviews/, but that is not proof for other hosts. Not load-bearing.

#### C16 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:5405-5406; C:/Users/iball/Arduino/Projects/HistoricMansions/docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:5410`
- reasoning: git grep at 22eae4f9: :5405 '5. A second repository (Cayenne) can install the plugin and run the gate with its' continues at :5406, and :5410 'Item 5 is the one that proves the objective rather than approximating it'.

#### C17 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/hooks.json:4-26; plugins/arch-compliance/hooks/posttooluse_gate.py:72-81; plugins/arch-compliance/hooks/inject_constraints.py:71-80; plugins/arch-compliance/hooks/inject_constraints.py:153-175; plugins/arch-compliance/hooks/posttooluse_gate.py:254; plugins/arch-compliance/hooks/posttooluse_gate.py:281; plugins/arch-compliance/hooks/posttooluse_gate.py:131-134`
- reasoning: hooks.json registers SubagentStart (matcher *) and PostToolUse (Write|Edit|MultiEdit). Both hooks exit 0 without the marker. ENABLED_REL is read only by these two hooks (grep). SubagentStart renders the rows and a doctrine excerpt. PostToolUse scans with added_lines=None and, on BLOCK in hook format, prints to stderr and returns 2. One omission, filed as an unanchored finding: PostToolUse also runs the build-artifact path guard on every edited path.

#### C18 — SURVIVED
- evidence: `pyproject.toml:23 (git show c0281bf: testpaths = ["plugins/arch-compliance/tests"], version = "0.2.0" at :3); plugins/arch-compliance/.claude-plugin/plugin.json:3 (c0281bf: "version": "0.2.0")`
- reasoning: Versions read at c0281bf. I could not run pytest --collect-only (test execution is forbidden), so I counted statically. Parsing every test_*.py under plugins/arch-compliance/tests at c0281bf and expanding the 16 parametrize decorators gives exactly 404 test items, with no unresolved parametrize argument.

#### C19 — SURVIVED
- evidence: `scripts/check_installed_skills.py:46; ran python scripts/check_installed_skills.py C:/Users/iball/.claude/plugins/cache/arch-compliance-for-superpowers/arch-compliance/0.2.0 -> 'installed gate skills identical to the clone', exit 0; C:/Users/iball/.claude/plugins/cache/arch-compliance-for-superpowers/arch-compliance/0.2.0/.claude-plugin/plugin.json:3 (0.2.0)`
- reasoning: Ran the check. installed_plugins.json records arch-compliance@arch-compliance-for-superpowers at scope user, version 0.2.0, gitCommitSha c0281bf, installPath as stated. known_marketplaces.json gives the source as a directory, the local clone. In HM, 812f9c2b has date 2026-10-23 and is an ancestor of 22eae4f9.

#### C20 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/config/architecture/mandates.yml:14 (gemini_anchor); plugins/arch-compliance/python/acf/registry.py:20 (languages required); load_mandates(<hm>/config/architecture/mandates.yml) with this branch's package -> AcfInputError (languages Field required)`
- reasoning: HM's file has 48 rows, 48 with gemini_anchor, 0 with arch_anchor or languages, and no repeated id. It does not load through acf.registry.load_mandates. git -C <hm> grep for acf.registry, acf.cli_check_diff and acf-check-diff at 22eae4f9 hits only docs/design/ and docs/reviews/ files. HM's own load_mandates calls are its scripts.core.architecture.registry, and HM has no .acf/ marker, so the plugin hooks no-op there.

#### C21 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/ledger.py:75; plugins/arch-compliance/python/acf/adr/run_detail.py:42; plugins/arch-compliance/python/acf/adr/rollup.py:66; plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:369`
- reasoning: Grepped spec_path across python/, hooks/ and skills/. It is a validated string field (PosixStr), a filename stem for run-detail naming, rendered text, and a match key for amendments and the read-back. Nothing opens a ledger row's spec_path as a file or requires it to resolve in the ledger's repository.

#### C22 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/citations.py:129; plugins/arch-compliance/python/acf/adr/citations.py:147-185; plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:76-82; plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:101; C:/Users/iball/Arduino/Projects/HistoricMansions/docs/reviews/adr_runs/ADR_GATE_HOST_CONTRACT_v3_2026-10-12.md:35`
- reasoning: Ran resolve_citation on 'hm:GEMINI.md:103', 'hm:docs/design/ADR_GATE_HOST_CONTRACT.md:80-81', 'hm:CLAUDE.md:21-35' and 'acf:README.md:84': each returned ('unresolved', None). SKILL.md raises UnresolvableCitationError before dispatch. The HM v3 run record dispatched (Outcome BLOCKED), and its reviewer evidence at :28, :35 and :247 cites acf:-prefixed plugin paths with line numbers, consistent with mapped paths being opened. Small imprecision: the spec's test order omits the asserted_absent step (citations.py:150). It does not change the result.

#### C23 — REFUTED
- evidence: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:115; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:108; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:564; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:540-547; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:57`
- reasoning: The spec contains many unprefixed shorthand citations: `ARCHITECTURE.md` (:115, :184, :244, :296, :477), `ARCH_COMPLIANCE_FOR_SUPERPOWERS.md` (:108), `adr.yml` (:257), `hooks.json` (:515), `:47` (:114), `:32-44` (:257), and in the appendix `bad_except.py:4`, `bad.tsx:4`, `diff.py:28`, `citations.py:64`, `typescript_bridge.py:53`, `cli_check_diff.py:25`, `test_profile_drift.py:13` (:564-571). It also names HM files without the hm: prefix: `GEMINI.md` (:57, :502) and the eight HM spec basenames in the §10 table (:540-547). Both halves of the §0 assertion are false as written.

#### C24 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/docs/design/ADR_GATE_HOST_CONTRACT.md:80-81; docs/design/ADR_GATE_HOST_CONTRACT.md:3-8 (provenance block in the copy)`
- reasoning: At 22eae4f9, lines 80-81 read '6. **This spec stays in this repository until 1d, and moves to the plugin repository after 1d's acceptance run.**' The quote matches, apart from bold markup.

#### C25 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:103; C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:104; C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:105; C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:111; C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:129; C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:136; C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:189; C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:191`
- reasoning: git grep at 22eae4f9 puts each quoted rule on exactly the stated line. The quoted text matches, with ellipses where the doctrine elides (for example :105 '`hasattr()`-based interface probing and silent degradation (...) are shims').

#### C26 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:61; plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:443`
- reasoning: GEMINI.md:61 says 'append the superseding ledger amendment' for a verification pass. The plugin skill at :443 says 'A verification pass writes no ledger record.' The conflict is real. Its deferral is a scheduling choice, not a fact to check.

#### C27 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:102; plugins/arch-compliance/skills/acf-mandate/SKILL.md:122; plugins/arch-compliance/python/acf/registry.py:19; plugins/arch-compliance/python/acf/registry.py:56`
- reasoning: The design doc defines detector as 'Detector fn / guard module / LLM prompt id' and gives no meaning for manual rows. The skill line covers grep/guard/manual with 'Document how humans or external tools satisfy the mandate'. The loader types detector as str and checks it only for ast and guard. Caveat: the SKILL:122 evidence also covers guard rows, which the loader does validate, so it is weak support for 'free text'. The registry contract itself (registry.py:19, :56) still holds.

#### C28 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_profile_drift.py:7; plugins/arch-compliance/tests/test_profile_drift.py:27; plugins/arch-compliance/skills/acf-mandate/SKILL.md:91; plugins/arch-compliance/skills/acf-mandate/SKILL.md:99; plugins/arch-compliance/python/acf/registry.py:47; plugins/arch-compliance/tests/test_enforcement.py:34`
- reasoning: On HEAD, the drift test imports KNOWN_DETECTORS and calls missing_anchors; its own union and loop are gone. The snippet imports KNOWN_DETECTORS and missing_anchors; there is no PYTHON_DETECTOR_IDS and no 'Also verify ... by eye' sentence (git grep). load_mandates refuses repeats. The only other MandateRegistry constructor is a test helper. Nothing reads what was removed. Leftover: the PYTHON_DETECTOR_IDS alias itself still exists with no consumer (unanchored finding).

#### C29 — SURVIVED
- evidence: `docs/plans/PLAN_PLUGIN_SELF_HOSTING.md:78; config/architecture/mandates.yml:27; plugins/arch-compliance/skills/acf-setup/SKILL.md:110`
- reasoning: The plan's bootstrap step fixes the answer in advance: duplicate id ops.no-build-artifacts = keep one row, languages: both. The host registry carries exactly one such row and loads through the refusing loader (the CLI run succeeded). So the bootstrap does not depend on the false parenthetical, and SKILL.md:110 is unchanged on the branch.

#### C30 — SURVIVED
- evidence: `git diff --stat c0281bf HEAD -- plugins/arch-compliance/python/acf/adr/ plugins/arch-compliance/python/acf/detectors/ plugins/arch-compliance/detectors/typescript/src/ plugins/arch-compliance/skills/adversarial-design-review/ plugins/arch-compliance/skills/responding-to-adversarial-review/ plugins/arch-compliance/hooks/ -> empty; plugins/arch-compliance/python/acf/adr/ledger.py:75`
- reasoning: There is no diff in any of those trees. The full plugins/ diff touches only plugin.json, registry.py, acf-mandate/SKILL.md, the two fixtures and three tests.

#### C31 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:213; C:/Users/iball/Arduino/Projects/HistoricMansions/docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:5122`
- reasoning: At 22eae4f9, :213 is the 1d follow-up row 'plugin `hooks.json` passes `--quiet-disabled`', and :5122 is the 1a row naming 'one git runner'.

#### C32 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/CLAUDE.md:17; C:/Users/iball/Arduino/Projects/HistoricMansions/CLAUDE.md:21-35; C:/Users/iball/Arduino/Projects/HistoricMansions/docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:666; C:/Users/iball/Arduino/Projects/HistoricMansions/docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:669-681`
- reasoning: HM CLAUDE.md:17 is the arch-compliance install instruction, and :21-35 is the 'Superpowers skill defaults — project overrides' pointer-and-process block. Plan lines 669-681 are the python heredoc byte-check, under the checked step '- [x] **Step 1: Cache byte-identity (DoD 7)**' (:666), so it is an executed record.

### Unanchored findings

- **important**: Decision 8 removes the snippet's narrower union but leaves the narrower alias PYTHON_DETECTOR_IDS exported with zero consumers (no package, hook, skill or test use) and a false comment ('Back-compat alias used by CLI / drift tests'); that is the doctrine's own '## Live consumers' rule broken on a surface this design touches, and it leaves the trap that caused the /acf-mandate bug.
  - evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:25`
- **advisory**: The §10 table's unprefixed HM spec basename `ADR_GATE_HOST_CONTRACT.md` suffix-resolves to this repository's new copy (docs/design/ADR_GATE_HOST_CONTRACT.md), so the resolver silently classes an HM reference (its 4 HM ledger rows) as current here instead of failing it.
  - evidence: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:540`
- **advisory**: §4.1 item 11 and §5.4 describe PostToolUse as scanning edited .py/.ts/.tsx files, but with the marker it also runs the enforced build-artifact path guard over every edited path, including non-code files, so an edit under dist/ or build/ returns a BLOCK (exit 2) too.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:284-294`

### Looked for but did not find

- any subprocess call in plugins/arch-compliance/python or plugins/arch-compliance/hooks other than diff.py:24, citations.py:62 and typescript_bridge.py:49
- any consumer of ENABLED_REL / .acf/enabled other than the two hooks
- any package, hook or skill code that opens a ledger row's spec_path as a file
- a third spelling of the ALL_PYTHON|TS|LLM detector union at c0281bf outside cli_check_diff.py:25 and test_profile_drift.py:13 (the snippet's narrower union aside)
- an anchor-check function in the acf package at c0281bf
- a repeated mandate id in HM's 48-row registry at 22eae4f9
- an `import acf` / `from acf` in HM tracked code outside docs/
- a diff c0281bf..HEAD in acf/adr, acf/detectors, detectors/typescript/src, hooks/, or the two gate skill trees
- non-ASCII tracked file names (which would make citations._git ls-files output non-ASCII)
- non-ASCII text in the TypeScript scanner sources that the cp1252-decoded bridge output would carry
- any finding from the root commit dfff93f5's content (it holds only docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md)
- a §4.2-unlisted path in git diff --stat c0281bf HEAD

## compliance

### Claim verdicts

#### C33 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:50; config/architecture/mandates.yml:148-201; config/architecture/ARCHITECTURE.md:99-138; tests/test_self_host.py:32-42; plugins/arch-compliance/python/acf/registry.py:63-65`
- reasoning: Principle 4 reads 'prose anchors, detectors, auditors, and call sites must agree or tests fail'. Five detection: manual rows exist (mandates.yml:148-201). Each detector names an existing module under plugins/arch-compliance/tests/: test_adr_exceptions, test_repo_paths, test_adr_host, test_adr_code_portability, test_adr_ledger. Each arch_anchor is a heading in ARCHITECTURE.md (lines 99, 105, 113, 125, 132), and every stock anchor survives (lines 24-92). test_self_host.py pins both properties through missing_anchors and an existing-file check. Each doctrine section names its row id and not the row's detector path. Caveats, filed separately: ## Prose names no host additionally names a different test path (test_adr_skill_prose.py, ARCHITECTURE.md:129-130) that no row points to and no test pins. The 'call sites' part of principle 4 is neither pinned nor accurate for the manual rows.

#### C34 — SURVIVED
- evidence: `config/architecture/adr.yml:1-2; plugins/arch-compliance/python/acf/adr/host.py:19-33; config/architecture/ARCHITECTURE.md:113-123; plugins/arch-compliance/python/acf/repo.py:23-26; plugins/arch-compliance/python/acf/repo.py:32-44`
- reasoning: adr.yml declares exactly runs_dir and ledger_path. AdrHostConfig gives both fields Field(min_length=1) with no default, and extra='forbid'. load_host_config requires the doctrine document and then loads the declaration, so a missing value fails loud. The doctrine section states that scope and names the two package defaults outside it: the ratchet baseline at repo.py:23-26 and the resolve_repo cwd fallback at repo.py:32-44, which its own docstring calls a fallback.

#### C35 — SURVIVED
- evidence: `config/architecture/adr.yml:1-2; plugins/arch-compliance/python/acf/adr/host.py:24-25; plugins/arch-compliance/python/acf/adr/contract.py:129-130; config/architecture/ARCHITECTURE.md:60-64`
- reasoning: adr.yml holds relative forward-slash paths. Both host fields are typed PosixStr, which is AfterValidator(_reject_backslash) with the docstring 'REJECTS a backslash on construction (never normalizes)'. The doctrine quotes hm:GEMINI.md:189 and :191 accurately (checked against HM GEMINI.md lines 189 and 191) and records that the plugin refuses rather than normalizes. Precision note: PosixStr is defined at contract.py:129, not :128 as the spec and doctrine cite; line 128 is blank.

#### C36 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:48; CLAUDE.md:20-23; config/architecture/ARCHITECTURE.md:13-15`
- reasoning: Principle 2 literally reads 'one registry façade; one finding schema; do not dual-run parallel mandate lists'. 'One rules document' is a fair reading of the no-parallel-lists clause. CLAUDE.md carries no mandate list. Its byte-check bullet gives the command and says 'The rule and what to do on a mismatch are the doctrine's ## Release discipline', which points rather than restates. ARCHITECTURE.md:13-15 cites the five principles at :43-51 and says they 'are not restated here'.

#### C37 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:51; CLAUDE.md:9-37; config/architecture/ARCHITECTURE.md:11-13`
- reasoning: Principle 5 requires that where the plugin's defaults conflict with Superpowers generics the host wins, and to 'document that explicitly'. CLAUDE.md does so: spec location (11-12), plan location (13-14), terminal state with the BLOCKED return through responding-to-adversarial-review and re-run scope by revision class (15-19), the byte-check command (20-23), the citation convention (25-31) and the PYTHONUTF8 note (33-37). This matches HM's override form at hm:CLAUDE.md:21-35. The doctrine also states the precedence at ARCHITECTURE.md:11-13.

#### C38 — REFUTED
- evidence: `plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:152; config/architecture/ARCHITECTURE.md:146-156; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:29-31; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:114; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:564-567; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:175-176`
- reasoning: The rule (T3: 'Universally quantified claim | Recipe backing the quantifier, or delete the quantifier'; doctrine 146-156) is not applied to this spec throughout. §0 (lines 29-31) asserts 'Every unprefixed citation in this spec is a full repository-relative path with no shorthand' with no recipe, and the spec itself falsifies it: `:47` at line 114, `:32-44` at line 257, the bare `ARCH_COMPLIANCE_FOR_SUPERPOWERS.md` at line 108, and `bad_except.py:4`, `bad.tsx:4`, `diff.py:28`, `citations.py:64`, `typescript_bridge.py:53` at lines 564-567. The controller had to resolve these as shorthand. Census item 15 (lines 175-176) asserts a negative, 'the package has no anchor-check function', and no appendix row backs it (the row at line 571 covers detector-union spellings only). The census's other per-item rows and the per-item DoD do hold; the self-application claim as stated does not.

#### C39 — REFUTED
- evidence: `plugins/arch-compliance/skills/architecture-review/SKILL.md:62; plugins/arch-compliance/python/acf/repo.py:15; config/architecture/ARCHITECTURE.md:182-189; config/architecture/ARCHITECTURE.md:206-208`
- reasoning: The lifted rule (verified at HM GEMINI.md:136) requires 'exactly one canonical implementation that every call site consumes'. The anchor check (registry.py:63-65), the detector union (cli_check_diff.py:25) and id uniqueness (registry.py:46-51) each have one definition, and the drift test, host test and /acf-mandate snippet consume them. 'Host paths one owner (acf.repo)' is false after this design: the executable snippet at architecture-review/SKILL.md:62 is `reg = load_mandates(Path("config/architecture/mandates.yml"))`, a second spelling of acf.repo.MANDATES_REL. The doctrine's high-frequency misses (206-208) name this exact shape. The doctrine's 'Current breach, recorded not hidden' (186-189) records only the two git runners, so this breach is hidden. Scoped refactor means the design need not change the snippet, but the single-point claim and the breach record must cover it.

#### C40 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:1-29; tests/test_self_host.py:16; tests/test_self_host.py:23; config/architecture/ARCHITECTURE.md:105-111; plugins/arch-compliance/tests/test_repo_paths.py:17-25`
- reasoning: acf.repo declares CONFIG_DIR, MANDATES_REL, ARCH_REL, ADR_REL and ENABLED_REL, and imports only __future__ and pathlib. tests/test_self_host.py imports ARCH_REL and MANDATES_REL rather than re-spelling them. scripts/check_installed_skills.py spells no config/architecture path. The doctrine states the row's test scope (python/ and hooks/; test_repo_paths.py runs `git ls-files python hooks`) and that the root trees are checked by review.

#### C41 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:3-11; plugins/arch-compliance/python/acf/cli_check_diff.py:115-156; plugins/arch-compliance/hooks/posttooluse_gate.py:35; .github/workflows/ci.yml:39-40`
- reasoning: The opening paragraph lists the package, hooks, skill prose, TypeScript bridge, plugin tests and fixtures, and root tests/, scripts/ and config/. Its statement about detectors holds in code. The diff CLI scans every changed path by suffix (.py, .ts, .tsx) with no directory filter, the hook's _CODE_SUFFIXES is {.py, .ts, .tsx}, and CI runs the diff gate. Prose and configuration are left to review.

#### C42 — SURVIVED
- evidence: `plugins/arch-compliance/.claude-plugin/plugin.json:3; pyproject.toml:3; config/architecture/ARCHITECTURE.md:171-180; plugins/arch-compliance/hooks/posttooluse_gate.py:22-26`
- reasoning: /acf-mandate SKILL.md changes, and both version fields read 0.2.1. The doctrine says a skill prose change bumps both files, and that the byte check covers the two gate skill trees only, not the installed hooks/ and python/ that the hooks run. posttooluse_gate.py:22-26 confirms that: it puts its own plugin root's python/ on sys.path.

#### C43 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:1-65; config/architecture/ARCHITECTURE.md:158-169; plugins/arch-compliance/python/acf/diff.py:24-30; plugins/arch-compliance/python/acf/adr/citations.py:62-65; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:49-56`
- reasoning: The only package or hook file the design changes is registry.py, which makes no subprocess call. A search for text=True across python/ and hooks/ finds only the three recorded breaches (diff.py:28, citations.py:64, typescript_bridge.py:53). Every read_text in package and hooks declares encoding='utf-8'. The doctrine records the three breaches with the grep recipe and puts plugin tests outside its scope (161-163).

#### C44 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:46-51; plugins/arch-compliance/python/acf/exceptions.py:5; plugins/arch-compliance/skills/acf-mandate/SKILL.md:99-101; scripts/check_installed_skills.py:42-45`
- reasoning: AcfInputError is `class AcfInputError(AcfError)` with no stdlib mixin. The refusal names the sorted repeated ids. missing_anchors returns a list and defaults nothing. The snippet calls sys.exit(message), which exits 1 and names the rows. The script returns 1 and prints each differing or missing path. No new bare or broad except appears. Caveat: when the clone's gate-skill directory is absent, the script passes without comparing anything (filed as advisory).

#### C45 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:85-112; plugins/arch-compliance/python/acf/registry.py:48-51; config/architecture/ARCHITECTURE.md:125-130`
- reasoning: I read the changed /acf-mandate prose and the new loader message. Neither names a host repository (no HistoricMansions, GEMINI, HM path or section). The only paths named are the plugin's own fixed host layout (config/architecture/...), which the gate prose also uses and the prose test does not forbid. The cited enforcement does not cover either surface, though (filed as important): test_adr_skill_prose.py scans seven gate files only, and test_adr_code_portability.py scans acf/adr/*.py only.

#### C46 — SURVIVED
- evidence: `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:443-453; config/architecture/ARCHITECTURE.md:132-138; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:180-205`
- reasoning: The skill states 'A verification pass writes no ledger record' and that the spec header line is the record. The doctrine records both that and the spec-and-gate-run rule for LedgerRow and LedgerAmendment fields. The disposition table lists no acf/adr module, so no ledger model is changed. test_adr_ledger.py:580-596 pins LedgerRow's dump against a real record.

#### C47 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:140-144; plugins/arch-compliance/skills/acf-mandate/SKILL.md:91-101; plugins/arch-compliance/python/acf/cli_check_diff.py:70`
- reasoning: The doctrine reads 'An export has a live call site in the package, a hook or a skill'. missing_anchors is called by the /acf-mandate skill snippet; that is its only non-test consumer, which the rule allows. KNOWN_DETECTORS is used by the diff CLI itself (line 70) and by the snippet. The repeated-id refusal sits in load_mandates, which the CLIs and hooks call.

#### C48 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:191-195; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:193-198; plugins/arch-compliance/python/acf/diff.py:17-30; plugins/arch-compliance/tests/fixtures/python/bad_except.py:4`
- reasoning: The lifted text (verified at HM GEMINI.md:129) reads 'remove ... non-contractual patterns in code paths you are changing. Do not expand scope to unrelated modules'. The package change is confined to registry.py; the drift test and snippet converge on the package checks; the fixtures gain only the exemption token. The git runners (diff.py:17-30), the decoding calls and the /acf-setup prose are unchanged and filed in §9.

### Unanchored findings

- **important**: The plugin.prose-names-no-host row is status: enforced, but its detector test_adr_code_portability.py scans only acf/adr/*.py, and the prose test the doctrine names covers only the seven gate files. Neither the /acf-mandate SKILL.md this design changes nor the new acf/registry.py refusal message is checked by any test, and unlike ## One owner for host paths the doctrine section does not state that scope.
  - evidence: `plugins/arch-compliance/tests/test_adr_code_portability.py:7; plugins/arch-compliance/tests/test_adr_code_portability.py:14; plugins/arch-compliance/tests/test_adr_skill_prose.py:12-17; config/architecture/mandates.yml:181-190; config/architecture/ARCHITECTURE.md:125-130`
- **advisory**: The new test_acf_mandate_skill.py builds the host layout by spelling 'config'/'architecture' instead of using acf.repo.CONFIG_DIR, MANDATES_REL or ARCH_REL. That is the high-frequency miss the doctrine names, a constant re-spelled in a test, and it falls outside both the row's scan and the doctrine's review statement.
  - evidence: `plugins/arch-compliance/tests/test_acf_mandate_skill.py:29; config/architecture/ARCHITECTURE.md:206-208`
- **advisory**: scripts/check_installed_skills.py iterates the clone's skill directories with rglob. If a gate-skill directory is absent or renamed while GATE_SKILLS is unchanged, it compares nothing and prints 'installed gate skills identical to the clone' with exit 0, which is a vacuous pass of the pre-gate check.
  - evidence: `scripts/check_installed_skills.py:25-33`
- **advisory**: The five manual rows declare call_sites: [audit], but they are enforced by pytest in CI and no auditor runs them. No code reads call_sites, so principle 4's 'call sites must agree or tests fail' is neither pinned nor accurate for these rows.
  - evidence: `config/architecture/mandates.yml:154; .github/workflows/ci.yml:36-37; plugins/arch-compliance/python/acf/registry.py:21`
- **advisory**: The spec and the doctrine cite PosixStr at contract.py:128; it is defined at :129, and line 128 is blank.
  - evidence: `plugins/arch-compliance/python/acf/adr/contract.py:129; config/architecture/ARCHITECTURE.md:64`

### Looked for but did not find

- ## Fail loud: new code (registry.py, scripts/check_installed_skills.py, tests/test_self_host.py) has no bare or broad except and no None default for a missing value; the fixture tokens carry reasons (bad_except.py:4, bad.tsx:4). Cleared.
- ## No shims: no new hasattr probe or any in package or hook code; the five WARN rows are dispositioned in spec §5.4. Cleared.
- ## POSIX paths: adr.yml uses forward slashes; the loader message uses path.as_posix(); the snippet uses ARCH_REL.as_posix(). Cleared.
- ## Build artifacts: plugins/arch-compliance/detectors/typescript holds only .gitignore, package.json, package-lock.json and tsconfig.json; no dist/ or build/ is added. Not touched.
- ## Fail-loud ratchet, ## Façade sinks, ## FSM transitions, ## React boundaries: rows unenforced, each with a reason comment (mandates.yml:40, 101, 117), and their doctrine sections say why. Cleared.
- ## One base exception: no new exception class; AcfInputError is reused (exceptions.py:5). Cleared.
- ## Declared, never defaulted: no default re-enters for runs_dir or ledger_path (host.py:24-25). Cleared.
- ## Frozen ledger format: no acf/adr module in the disposition table. Cleared.
- ## Declared text decoding: the only text=True sites in python/ and hooks/ are the three recorded breaches. Cleared.
- ## Release discipline: plugin.json:3 and pyproject.toml:3 both read 0.2.1. Cleared.
- ## High-frequency misses: checked first. No host name in the changed prose; no stdlib mixin; no new subprocess text call; KNOWN_DETECTORS and missing_anchors are consumed rather than re-implemented in the snippet, drift test and host test. The re-spellings found are in architecture-review/SKILL.md:62 (C39) and test_acf_mandate_skill.py:29 (advisory).

### Unstated mandates

- ## Soft fail-loud smells — soft.fail-loud stays status: partial with call_sites [ci, audit] (mandates.yml:132-142), and /acf-mandate SKILL.md:45 says partial still gates. The CI this design defines (§5.6, ci.yml:39-40) runs only the diff CLI, which never runs llm rows, and no judge is configured. Spec §5.2 dispositions three rows and §11 the TypeScript rows, but is silent on how or whether this one is run here.

## sweeper

### Claim verdicts

#### C49 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/host.py:19-33; plugins/arch-compliance/python/acf/repo.py:21; docs/design/ADR_GATE_HOST_CONTRACT.md:239-252; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:50; config/architecture/mandates.yml:148-201; CLAUDE.md:3-5`
- reasoning: The host contract's one declaration (ADR_REL = config/architecture/adr.yml, AdrHostConfig extra=forbid with runs_dir/ledger_path) and the fixed doctrine path (ARCH_REL, required by load_host_config) exist as the moved spec's section 5.1-5.2 describes. config/architecture/adr.yml is the only declaration file under config/. The plugin's own rules are rows in the same Mandate schema (detection: manual), loaded by the same load_mandates. CLAUDE.md:3-5 points to the doctrine and carries process overrides only. I found no second declaration mechanism: Grep for adr.yml / runs_dir / ledger_path found only the host.py loader and the tests.

#### C50 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:63-65; tests/test_self_host.py:34; plugins/arch-compliance/tests/test_profile_drift.py:27; plugins/arch-compliance/skills/acf-mandate/SKILL.md:99`
- reasoning: I grepped arch_anchor across the tree, excluding docs/reviews. The only substring check in code is missing_anchors (registry.py:65). test_self_host.py:34, test_profile_drift.py:27 and the /acf-mandate snippet (SKILL.md:99) all consume it. judge.py:154 only substitutes the anchor into a prompt. Within the claim's scope ('code, tests or skill prose that the design touches') this holds. Outside that scope, /acf-setup SKILL.md:137-138 still tells the agent to check by eye that every arch_anchor appears in the doctrine. The design does not touch that skill, but it means decision 8's unscoped 'the one anchor-in-doctrine check' is not yet true of all skill prose (filed as an advisory unanchored finding).

#### C51 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:25; tests/test_self_host.py:14; plugins/arch-compliance/tests/test_profile_drift.py:7; plugins/arch-compliance/skills/acf-mandate/SKILL.md:91; plugins/arch-compliance/python/acf/judge.py:16`
- reasoning: I grepped TS_DETECTOR_IDS|LLM_PROMPT_IDS|ALL_PYTHON_DETECTOR_IDS|PYTHON_DETECTOR_IDS|KNOWN_DETECTORS and every load_mandates(...known_detectors=...) call. There is one union expression (cli_check_diff.py:25). The host test, the drift test and the skill snippet import it. The only other known_detectors argument is test_registry.py:30's deliberate one-id fixture. The reason it stays in the CLI holds: judge.py:16 imports acf.registry. Side effect: PYTHON_DETECTOR_IDS (python_pack.py:24-25) was the base snippet's component and is now an alias with no consumer, and its comment 'used by CLI / drift tests' is false (advisory finding). It is not a second union spelling.

#### C52 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:46-51; plugins/arch-compliance/tests/test_registry.py:40-47; plugins/arch-compliance/python/acf/enforcement.py:43; plugins/arch-compliance/skills/acf-setup/SKILL.md:110; tests/test_self_host.py:22-42`
- reasoning: load_mandates now raises AcfInputError on any repeated id before building MandateRegistry, so by_id (registry.py:34, consumed at enforcement.py:43) can no longer shadow a row from a loaded file. The only other MandateRegistry constructions are in tests (test_enforcement.py:34). acf-setup SKILL.md:110 still carries the false parenthetical, which is filed (spec section 9 item 4). tests/test_self_host.py has no uniqueness test. acf-mandate SKILL.md:65 'fail if collision' is authoring prose, now backed by the snippet's loader call.

#### C53 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:52-59; tests/test_self_host.py:37-42; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:102; plugins/arch-compliance/skills/acf-mandate/SKILL.md:122`
- reasoning: The loader branch checks membership of an enforced ast/guard row's detector in a known-id set. The host test checks that a manual row's detector is an existing file under plugins/arch-compliance/tests/. These are different predicates over different populations, and :102 and SKILL.md:122 leave a manual row's detector open, so ADJACENT with the spec's written justification stands. Caveat: docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:184 says 'Unknown detector id referenced by an enforced row → drift/registry validation fail', and the design neither cites nor reconciles that line while adding five enforced manual rows (filed as a document conflict and an important unanchored finding).

#### C54 — SURVIVED
- evidence: `tests/test_self_host.py:16; tests/test_self_host.py:23; tests/test_self_host.py:33; scripts/check_installed_skills.py:18-32; plugins/arch-compliance/python/acf/repo.py:12-21`
- reasoning: I grepped *.py for "config"/"architecture"/"mandates.yml"/"ARCHITECTURE.md"/"adr.yml" literals. In root tests/ and scripts/ (Glob: three files), test_self_host.py imports ARCH_REL/MANDATES_REL and uses load_host_config for adr.yml. check_installed_skills.py and test_check_installed_skills.py spell no config path. The spellings found are all in plugin tests that build fixture hosts (test_diff_cli.py:31, test_hooks.py:59, the new test_acf_mandate_skill.py:29-32). Those are outside this claim's scope.

#### C55 — SURVIVED
- evidence: `scripts/check_installed_skills.py:22-33; C:/Users/iball/Arduino/Projects/HistoricMansions/docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:669-681`
- reasoning: By behaviour I grepped filecmp|installPath|installed_plugins|byte-identical|plugins/cache across the tree. The only comparer of installed against clone is scripts/check_installed_skills.py; hooks and plugin tests have none. Its loop matches the HM inline block: the same two skills, rglob, relative path under <inst>/skills/<skill>, filecmp shallow=False, and the same success string. The script adds a clone parameter and exit codes. Minor second owner: tests/test_check_installed_skills.py:12 re-spells the gate-skill tuple instead of reading GATE_SKILLS from the loaded module.

#### C56 — SURVIVED
- evidence: `CLAUDE.md:20-23; config/architecture/ARCHITECTURE.md:171-180`
- reasoning: CLAUDE.md's byte-check bullet gives the command and INSTALL_PATH's source, then defers to '## Release discipline' for the rule and the mismatch procedure. The doctrine section states the rule (version bump, byte check, reinstall plus restart on mismatch, the scope gap). I grepped README.md, SECURITY.md, skill prose and the design doc for bump|reinstall|byte: no third statement of the rule. The rule lives in one place.

#### C57 — SURVIVED
- evidence: `docs/design/ADR_GATE_HOST_CONTRACT.md:3-8; docs/design/ADR_GATE_HOST_CONTRACT.md:497; C:/Users/iball/Arduino/Projects/HistoricMansions/docs/design/ADR_GATE_HOST_CONTRACT.md:490; docs/plans/PLAN_PLUGIN_SELF_HOSTING.md:370`
- reasoning: The local copy opens with a provenance block (lines 3-8) naming the HM path and HM commit 86f93f95. The plan's recipe records that as the file's last HM commit. The body is verbatim: I compared lines 1-130 against HM 1-120, and the appendix heading sits exactly 7 lines later (497 vs 490), which is the provenance block. HM's full copy is still present, so two full copies exist until step 6.

#### C58 — REFUTED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/docs/design/ADVERSARIAL_DESIGN_REVIEW.md:1-3; C:/Users/iball/Arduino/Projects/HistoricMansions/docs/design/ARCHITECTURE_COMPLIANCE_FRAMEWORK.md:1-16; C:/Users/iball/Arduino/Projects/HistoricMansions/docs/design/ARCH_COMPLIANCE_SHIFT_LEFT_GATING.md:1-3`
- reasoning: The claimed hit set is exactly what Glob docs/design/{ADR_,ARCH_COMPLIANCE_}*.md returns, so it is a name sweep. The claim itself demands a behaviour sweep. Swept by subject: ADVERSARIAL_DESIGN_REVIEW.md ('Approved design v1') is the gate's own origin spec. Everything it designs (the four-reviewer gate, claim extraction, the skills, the package) now lives in this plugin. It belongs with ADR_PER_FINDING_REVISION_CLASSING and ADR_REVISION_EVIDENCE..., which the spec includes as gate-behaviour specs, yet it is absent from section 1, section 7 and the section 10 disposition table. Likewise, ARCH_COMPLIANCE_SHIFT_LEFT_GATING is included even though it designs HM's own scripts/ci gating. On that same criterion, ARCHITECTURE_COMPLIANCE_FRAMEWORK.md (the ACF origin spec) and its TIER2/TIER3 siblings would also qualify. The inclusion rule is inconsistent and the list misses at least one instance.

#### C59 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/docs/reviews/adversarial_design_ledger.jsonl:176-179; C:/Users/iball/Arduino/Projects/HistoricMansions/docs/reviews/adversarial_design_ledger.jsonl:209-218; C:/Users/iball/Arduino/Projects/HistoricMansions/docs/reviews/adversarial_design_ledger.jsonl:337-349; C:/Users/iball/Arduino/Projects/HistoricMansions/docs/reviews/adversarial_design_ledger.jsonl:389-390; C:/Users/iball/Arduino/Projects/HistoricMansions/docs/design/ADR_GATE_PLUGIN_COMPONENT.md:3; C:/Users/iball/Arduino/Projects/HistoricMansions/docs/design/ADR_PER_FINDING_REVISION_CLASSING.md:3`
- reasoning: Grep of spec_path values in HM's ledger: REVISION_EVIDENCE 4 (176-179), EXTRACTION 7 (209-215), PLUGIN_COMPONENT 3 (216-218), HOST_CONTRACT 4 (337-339, 344), HM_CUTOVER 6 (346-349, 389-390), and none for ADOPTION, PER_FINDING or SHIFT_LEFT. All counts match. Status lines match: EXTRACTION 'Superseded — not for review', PLUGIN_COMPONENT 'v3 … do not re-dispatch', ADOPTION 'draft v1', PER_FINDING 'pre-brainstorm stub', REVISION_EVIDENCE 'v4 — draft'. One precision nit: SHIFT_LEFT's Status line reads 'Design approved', and its 'Superseded (2026-08-01)' note covers only the section 11 diff path.

#### C60 — SURVIVED
- evidence: `config/architecture/mandates.yml:40-50; config/architecture/mandates.yml:101-130; plugins/arch-compliance/profiles/python-service/mandates.yml:70; plugins/arch-compliance/profiles/python-service/mandates.yml:85; plugins/arch-compliance/profiles/react-app/mandates.yml:44`
- reasoning: facade.forbid-sink and fsm.transition-guard are unenforced in the profile (python-service :70, :85) and in the merged file, each with a one-line reason comment (mandates.yml:101, :117). soft.react-boundaries is partial in react-app (:44) and unenforced here with a comment (:40). The remaining stock rows (empty-catch, explicit-any, no-build-artifacts, bare-except, hasattr, posix-paths, soft.fail-loud) have Python or TypeScript subjects in this repository. fail-loud.ratchet is also unenforced, with no comment, but it arrives unenforced from the profile (:55) as an optional row, not for lack of a subject. The claim does not cover it.

#### C61 — SURVIVED
- evidence: `README.md:93-95; pyproject.toml:23; tests/test_self_host.py:18`
- reasoning: README.md:93-95 records the precedent: tests that 'test a property of a host, not of this plugin' are kept out of the plugin tree. The root tests/ is collected through the second testpaths entry (pyproject.toml:23) and anchors on the repository root (test_self_host.py:18), which a shipped plugin copy would not have. That is the nearest shape, and it does not fork the plugin's test tree. Side effect: pyproject.toml:15 and :36 comments say 'tests/test_packaging.py'. Now that root tests/ exists, that path no longer points at the file; it lives under plugins/arch-compliance/tests/ (advisory finding).

#### C62 — REFUTED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:270-281; C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:137; C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:193; C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:112; C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:102`
- reasoning: I grepped GEMINI.md's headings and read sections 2-10 and 14. The exclusion list (sections 5, 6, 11, 10-book-root, 12, 13) is justified for those sections. But the claim that 'the HM rules that do apply to Python here are the ones section 5.2 lists' is false. Five rules have a subject in this Python package and appear in neither the lifted nor the excluded set: section 14 Class Cohesion / no god objects (:270-281); section 7 'Pydantic Configs … must be valid at load time' (:137), which AdrHostConfig follows and the host contract cites; section 10 'Persist what you validated' (:193), relevant to the ledger and run-detail writers; section 4 'Zero Fallbacks' (:112); section 3 'Strict Typing … Use Pydantic' (:102). The exclusion sweep was done by named section, not by applicability.

### Unanchored findings

- **important**: The design adds five enforced manual rows whose detector is a test-file path and rests on 'the registry contract leaves it free text' (spec section 3, section 5.5, citing :102). The plugin's design document states the opposite for enforced rows, 'Unknown detector id referenced by an enforced row → drift/registry validation fail', and the spec never names or reconciles that line.
  - evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:184; config/architecture/mandates.yml:151-156`
- **advisory**: The /acf-setup skill still has the agent confirm by eye that every arch_anchor survives in the doctrine (Step 6), and its smoke check (Step 9) runs only cli_check_diff, which never checks anchors. Decision 8's 'missing_anchors is the one anchor-in-doctrine check' therefore has a second, prose owner in the bootstrap path this design itself uses. Resolution: Step 9 runs the /acf-mandate Validate snippet (or missing_anchors).
  - evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:137-138; plugins/arch-compliance/skills/acf-setup/SKILL.md:212-226; plugins/arch-compliance/python/acf/registry.py:63`
- **advisory**: Moving the /acf-mandate snippet to KNOWN_DETECTORS removed the last live consumer of PYTHON_DETECTOR_IDS. The alias is still exported, and its comment 'Back-compat alias used by CLI / drift tests' is now false, which breaches the doctrine's own '## Live consumers' and '## Scoped refactor' rules in a code path the design changed.
  - evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:24-25; plugins/arch-compliance/python/acf/detectors/__init__.py:9; config/architecture/ARCHITECTURE.md:142`
- **advisory**: The spec-sweep for plugin-subject HM specs swept by filename prefix. It omits ADVERSARIAL_DESIGN_REVIEW.md, the gate's own approved origin spec whose whole subject now lives in the plugin, so section 10's disposition table has no row for it.
  - evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/docs/design/ADVERSARIAL_DESIGN_REVIEW.md:1-3`
- **advisory**: The doctrine claims to draw on GEMINI.md where a rule applies to Python, but it leaves out applicable rules without justifying the exclusion: section 14 class cohesion, section 7 Pydantic configs, section 10 persist-what-you-validated, section 4 zero fallbacks, section 3 strict typing.
  - evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:270; C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:137; C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:193`
- **advisory**: With root tests/ added as a testpaths entry, pyproject.toml's comments naming 'tests/test_packaging.py' now point at a path that does not exist (the file is plugins/arch-compliance/tests/test_packaging.py), and the design edits this file without touching them.
  - evidence: `pyproject.toml:15; pyproject.toml:36; plugins/arch-compliance/tests/test_packaging.py:1`

### Looked for but did not find

- A second anchor-in-doctrine substring check in code or tests: grep 'arch_anchor', 'not in doctrine', 'not in arch_text' over plugins/, tests/, scripts/; only registry.py:65 (prose by-eye instruction found at acf-setup SKILL.md:137)
- A second detector-id union: grep 'TS_DETECTOR_IDS|LLM_PROMPT_IDS|ALL_PYTHON_DETECTOR_IDS|PYTHON_DETECTOR_IDS|KNOWN_DETECTORS' and every 'known_detectors=' argument; only cli_check_diff.py:25 builds it
- Another repeated-id check in code: grep 'Counter|repeat|unique|duplicate' in plugins/arch-compliance; only registry.py:46 (prose at acf-setup SKILL.md:110, acf-mandate SKILL.md:65)
- Another installed-vs-clone comparer: grep 'filecmp|installPath|installed_plugins|byte-identical|plugins/cache' across scripts, tests, hooks; only scripts/check_installed_skills.py
- A second statement of the release-discipline rule: grep 'bump|reinstall|cached copy|byte' in README.md, SECURITY.md, skill prose, ARCH_COMPLIANCE_FOR_SUPERPOWERS.md; only ARCHITECTURE.md:171-180
- Host config path literals in root tests/ and scripts/: grep '"config"|"architecture"|mandates.yml|ARCHITECTURE.md|adr.yml' in *.py; none in tests/test_self_host.py, tests/test_check_installed_skills.py, scripts/check_installed_skills.py
- A second host-declaration mechanism: grep 'adr.yml|runs_dir|ledger_path' in plugin python; only acf/adr/host.py via acf.repo.ADR_REL
- Another validator of a manual row's detector string: grep 'detection == "manual"' and 'is_file()' over detector in plugins/; none outside tests/test_self_host.py
- Raw YAML reads of mandates.yml bypassing load_mandates: grep 'safe_load|yaml.load' in *.py; only acf/loader.py:64 (the loader itself)
- HM plugin-subject specs outside docs/design: grep 'arch-compliance-for-superpowers|acf:plugins' in HM docs/ excluding design, reviews, plans; only docs/architecture/SKILL_PROVENANCE.md (a provenance record, not a spec)
- Stock rows with no subject beyond the three named: read each merged row in config/architecture/mandates.yml against this repository's Python/TS population; none

### Relationships

- PARTIAL_OVERLAP: `acf.registry.missing_anchors` — responsibility `decide whether each row's arch_anchor is a literal substring of the doctrine` — existing `plugins/arch-compliance/skills/acf-setup/SKILL.md:137`
  - resolution: missing_anchors is the one decider; /acf-setup Step 9's smoke check runs the /acf-mandate Validate snippet (load_mandates + KNOWN_DETECTORS + missing_anchors), and the Step 6 prose drops its by-eye check in favour of that command
- DISJOINT: `tests/test_self_host.py::test_every_anchor_is_in_the_doctrine` — responsibility `check this host's anchors against its doctrine` — existing `plugins/arch-compliance/tests/test_profile_drift.py:27`
  - resolution: Both consume acf.registry.missing_anchors over different populations (this host vs the bundled profiles); nothing to collapse
- ADJACENT: `load_mandates repeated-id refusal` — responsibility `refuse two rows with one id` — existing `plugins/arch-compliance/skills/acf-setup/SKILL.md:110`
  - resolution: none beyond filed follow-up 4
  - non-merge: The prose governs a human merge choice (which row to keep) before a file exists; the loader refuses after the file exists. They act at different stages, and the loader is the enforcement both rely on.
- ADJACENT: `tests/test_self_host.py::test_every_manual_row_names_an_existing_test_module` — responsibility `validate a mandate row's detector string` — existing `plugins/arch-compliance/python/acf/registry.py:56`
  - resolution: Reconcile with docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:184 in writing
  - non-merge: The loader checks known-id membership for enforced ast/guard rows; the host test checks file existence under plugins/arch-compliance/tests/ for manual rows, which is this host's convention (ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:102, acf-mandate SKILL.md:122).
- SUBSUMED: `acf.cli_check_diff.KNOWN_DETECTORS consumers (snippet, drift test, host test)` — responsibility `name the set of detector ids a row may reference` — existing `plugins/arch-compliance/python/acf/detectors/python_pack.py:25`
  - resolution: PYTHON_DETECTOR_IDS is a subset alias of a component of KNOWN_DETECTORS with no remaining consumer; delete it (and its re-export at detectors/__init__.py:9,35) or name its live consumer
- SUBSUMED: `scripts/check_installed_skills.py` — responsibility `byte-compare the installed gate skills with the clone` — existing `C:/Users/iball/Arduino/Projects/HistoricMansions/docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:669-681`
  - resolution: The script is the generalized container (clone as parameter, exit codes); the HM block stays as an executed record, and HM's live install instruction (hm CLAUDE.md:17) consumes the script (filed in section 10)
- IDENTICAL: `tests/test_check_installed_skills.py SKILLS tuple` — responsibility `name the two gate skills` — existing `scripts/check_installed_skills.py:18`
  - resolution: The test reads GATE_SKILLS from the module it already loads via _load_script() instead of re-spelling it
- IDENTICAL: `docs/design/ADR_GATE_HOST_CONTRACT.md` — responsibility `state the gate's host contract` — existing `C:/Users/iball/Arduino/Projects/HistoricMansions/docs/design/ADR_GATE_HOST_CONTRACT.md:1`
  - resolution: Temporary by design: section 5.7 step 6 replaces HM's body with a stub naming this path; the provenance block marks this copy as the moved one
- ADJACENT: `CLAUDE.md byte-check bullet` — responsibility `state when and how to byte-check the installed skills` — existing `config/architecture/ARCHITECTURE.md:171-180`
  - resolution: none
  - non-merge: CLAUDE.md carries only the command and points to the doctrine section, which alone states the rule and the mismatch procedure.
- ADJACENT: `config/architecture/ARCHITECTURE.md lifted HM quotes` — responsibility `state the fail-loud / no-shims / POSIX / single-point-of-definition rules` — existing `C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:103`
  - resolution: none
  - non-merge: Quoted with attribution at a fixed HM commit so the doctrine reads alone without the sibling checkout; drift is visible and accepted (spec section 9 risk row).

### Two-owner counts

- decide whether an arch_anchor is present in the doctrine (missing_anchors; /acf-setup by-eye instruction): 2
- refuse or prevent a repeated mandate id (load_mandates; /acf-setup merge prose): 2
- name the two gate skills (scripts/check_installed_skills.py:18; tests/test_check_installed_skills.py:12): 2
- byte-compare installed gate skills with the clone (script; HM executed plan block): 2
- full text of the host-contract spec (this repo; HM until stub): 2
- run git as a subprocess (acf/diff.py:17; acf/adr/citations.py:54), declared breach: 2

### Document conflicts

- `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:184` (contradicts): Unknown detector id referenced by an enforced row → drift/registry validation fail.
- `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:109` (restates): Single Pydantic-validated loader is the only read façade for mandate metadata.
- `docs/design/ADR_GATE_HOST_CONTRACT.md:102` (restates): Writing `adr.yml` from `/acf-setup`. A host authors the two-line file; a missing file is refused with its path named
- `README.md:93` (restates): The origin host's skill-install tests ... are deliberately not ported: they test a property of a host, not of this plugin

## hardening

### Claim verdicts

#### C63 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:46-51; plugins/arch-compliance/profiles/python-service/mandates.yml:34; plugins/arch-compliance/profiles/react-app/mandates.yml:23; config/architecture/mandates.yml:27`
- reasoning: The refusal sits in load_mandates, which is the only runtime constructor of MandateRegistry (registry.py:60; the only other constructor is a test at plugins/arch-compliance/tests/test_enforcement.py:34). It raises AcfInputError naming the ids and does not normalise. Producer of the duplicate: both stock profiles carry ops.no-build-artifacts, and the /acf-setup merge unions them. Upgrade risk: this repository's registry loads with no repeat (the read-only load_mandates call returned 16 rows). I called load_mandates on C:/Users/iball/Arduino/Projects/HistoricMansions/config/architecture/mandates.yml with the branch package and got AcfInputError for the missing `languages` field. yaml.safe_load of that file gives 48 rows with no repeated id. HM has no .acf/ directory, and `git grep` for acf.registry / acf.cli_check_diff / acf-check-diff outside docs/ in HM returns nothing. So HM is not reached.

#### C64 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:16; plugins/arch-compliance/python/acf/cli_check_diff.py:21; plugins/arch-compliance/python/acf/cli_check_diff.py:195-196; tests/test_self_host.py:14; plugins/arch-compliance/tests/test_profile_drift.py:7; plugins/arch-compliance/skills/acf-mandate/SKILL.md:91`
- reasoning: judge.py:16 imports Mandate from acf.registry, and cli_check_diff.py:21 takes LLM_PROMPT_IDS from acf.judge. So acf.registry cannot hold the union without a cycle. cli_check_diff has only imports and constants at module level; main() runs only under the __main__ guard (:195-196), so importing it has no side effect. Every consumer imports the one name: test_self_host.py:14, test_profile_drift.py:7 and the skill snippet at SKILL.md:91. The rest of the tree has no other `KNOWN_DETECTORS =` spelling. I ran the extracted snippet, which imports it, and it exited 0.

#### C65 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:110; config/architecture/mandates.yml:1-3; config/architecture/mandates.yml:40-50`
- reasoning: I diffed every row of both stock profiles against the host mandates.yml by field. The only difference is soft.react-boundaries status partial->unenforced (mandates.yml:40-50), which carries its reason comment. facade.forbid-sink and fsm.transition-guard arrive unenforced from the profile. No stock row was deleted, and ops.no-build-artifacts is kept once. All stock `##` headings of both profiles are present verbatim in config/architecture/ARCHITECTURE.md. Grepping acf-setup SKILL.md for adr.yml finds nothing, so the skill does not write the declaration, which matches authoring it by hand.

#### C66 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_python_pack.py:10-12; plugins/arch-compliance/tests/test_typescript_pack.py:35; plugins/arch-compliance/python/acf/enforcement.py:50; plugins/arch-compliance/tests/fixtures/python/bad_except.py:4`
- reasoning: The only consumers of bad_except.py / bad.tsx are test_python_pack.py, test_typescript_pack.py and detectors/typescript/src/scan.ts. All three call the scanners directly and none goes through apply_registry, so the token (honoured only at enforcement.py:50) cannot hide the finding from them. The token is a per-line refusal override that must carry a reason (enforcement.py:31-33). It is not a repair, and it leaves both BLOCK rows enforced for every other file.

#### C67 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:26-34; plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:4; plugins/arch-compliance/detectors/typescript/src/scan.ts:97`
- reasoning: token_exempted matches `(?:#|//)\s*<token>\s*:\s*(\S.*)$`, so both fixture forms match. I called scan_python_file and scan_typescript_file directly in a read-only python -c. They return [('fail-loud.bare-except', 4)] and [('fail-loud.empty-catch', 4), ('no-shims.explicit-any', 7), ('no-shims.explicit-any', 8)], three TS findings, which is what scan.ts:97 asserts (`bad.length !== 3`). I did not run npm test, per the rules; the self-test uses the same scan path that returned three findings.

#### C68 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:125-154; plugins/arch-compliance/hooks/posttooluse_gate.py:131-134; plugins/arch-compliance/hooks/posttooluse_gate.py:254`
- reasoning: I ran the branch's hook by hand (--format hook --repo .) on each fixture, and also the installed 0.2.0 copy's hook, which is the one hooks.json runs. Results: bad_except.py gave `no findings` with exit 0. bad.tsx gave additionalContext with only the two WARN no-shims.explicit-any lines (7, 8) and exit 0. apply_registry runs before the has_block test at :126, so exit 2 at :134 is reached only for a non-exempt BLOCK.

#### C69 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:38-39; plugins/arch-compliance/hooks/inject_constraints.py:153-176; config/architecture/ARCHITECTURE.md:1-80`
- reasoning: _render_constraints reads only the static constraints_template.md, each row's id/severity/status/title/detection/detector, and the first 4000 characters (_ARCH_EXCERPT_MAX) of ARCHITECTURE.md. That covers roughly lines 1-80: scope, stock sections and lifted quotes. None of these sources carries a review verdict or run reference; the mandates.yml comments are not rendered. The hook opens no docs/reviews path. This is true only of the hook; see the advisory finding on other channels into a reviewer's context.

#### C70 — SURVIVED
- evidence: `pyproject.toml:23-24; tests/test_self_host.py:26-29; plugins/arch-compliance/python/acf/adr/host.py:22-25; config/architecture/adr.yml:1-2`
- reasoning: testpaths = [plugins/arch-compliance/tests, tests] and pythonpath = [plugins/arch-compliance/python]. No test basename under tests/ collides with one under the plugin tests. I ran load_host_config(repo) read-only and got runs_dir='docs/reviews/adr_runs' ledger_path='docs/reviews/adversarial_design_ledger.jsonl', exactly the two keys under extra='forbid'.

#### C71 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_acf_mandate_skill.py:20-25; plugins/arch-compliance/tests/test_acf_mandate_skill.py:50-59; plugins/arch-compliance/skills/acf-mandate/SKILL.md:87-101`
- reasoning: SKILL.md has exactly one `## Validate`. The extraction regex matched its one bash python -c block (I ran the same regex read-only), and the snippet has no inner double quotes to end the match early. Read in-process: python-service registry + doctrine gives missing_anchors [] stock and ['fail-loud.bare-except'] with `## Fail loud` renamed. The snippet sys.exit's a message on a non-empty list, so it exits non-zero and names the id.

#### C72 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:91-101; config/architecture/mandates.yml:27-38`
- reasoning: The snippet loads with known_detectors=KNOWN_DETECTORS, prints rows and exits on missing_anchors. I ran the extracted snippet from this repository's root: rc 0, 'OK: 16 mandates', including the enforced guard row ops.no-build-artifacts. The c0281bf snippet (git show c0281bf:.../acf-mandate/SKILL.md) built `PYTHON_DETECTOR_IDS | TS_DETECTOR_IDS | LLM_PROMPT_IDS`, which lacks the guard ids.

#### C73 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:46-51; plugins/arch-compliance/python/acf/cli_check_diff.py:72-74; plugins/arch-compliance/hooks/posttooluse_gate.py:106-110; plugins/arch-compliance/hooks/inject_constraints.py:103-106; plugins/arch-compliance/python/acf/cli_check_llm.py:42; plugins/arch-compliance/tests/test_registry.py:40-56`
- reasoning: The raise comes before the MandateRegistry is built. The diff CLI and both hooks catch AcfInputError, print it and return 1; the LLM CLI does not catch it, so it ends in a traceback and a non-zero exit. No caller swallows it. Two more callers are not in the list: the architecture-review skill snippet (skills/architecture-review/SKILL.md:62) and the /acf-mandate snippet, and both fail loud through an uncaught raise. Both named tests exist. Caveat: the hooks that run here are the installed 0.2.0 copy, whose registry.py has no refusal until reinstall (recorded in spec §9). Also, a hook exit 1 is visible to the user but does not block the model.

#### C74 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:56; plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; plugins/arch-compliance/python/acf/judge.py:100; plugins/arch-compliance/python/acf/enforcement.py:46-48`
- reasoning: known_detectors is checked only for ast/guard. Dispatch is by detector id (_active_mandates, and the hook's equivalent filters at posttooluse_gate.py:229-236, 284-285); judge uses only detection=='llm'. No detector emits a plugin.* id, so apply_registry has nothing to keep. I ran the diff CLI over the branch with the five manual rows present: 'No findings.', exit 0 vs origin/main. Neither hook errored on the fixtures.

#### C75 — SURVIVED
- evidence: `.github/workflows/ci.yml:13-15; .github/workflows/ci.yml:29-40; plugins/arch-compliance/python/acf/diff.py:42-45; plugins/arch-compliance/python/acf/cli_check_diff.py:89-91`
- reasoning: Checkout has fetch-depth: 0. pip install -e and npm ci run before pytest and the step. The step's command matches the spec. The base is `<base>...HEAD` (three-dot); on a push to main, origin/main == HEAD, so the diff is empty. A BLOCK returns 1, failing the job. On a PR, HEAD is the merge ref, whose merge-base with origin/main is the base tip, so the scope is the PR's changes.

#### C76 — SURVIVED
- evidence: `scripts/check_installed_skills.py:22-47; tests/test_check_installed_skills.py:40-61`
- reasoning: The script has the same algorithm as the HM plan block (C:/Users/iball/Arduino/Projects/HistoricMansions/docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:669-681), with the clone as a parameter and filecmp shallow=False. It prints the stated line with exit 0, or each bad path with exit 1. I ran it against C:/Users/iball/.claude/plugins/cache/arch-compliance-for-superpowers/arch-compliance/0.2.0 and got 'installed gate skills identical to the clone', exit 0. The cache has skills/ at the same relative layout. The three tests cover identical, changed-byte and missing cases.

#### C77 — SURVIVED
- evidence: `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:30; plugins/arch-compliance/python/acf/adr/host.py:28-33`
- reasoning: The gate stops before dispatch unless the host has adr.yml and ARCHITECTURE.md (load_host_config with require_file). `git ls-tree c0281bf` has no config/. So this doctrine cannot be the compliance standard of any run until the branch declares it; a run from HM would judge against HM's doctrine. Hence plumbing and review are the same run.

#### C78 — SURVIVED
- evidence: `.github/workflows/ci.yml:11; CLAUDE.md:35-36; plugins/arch-compliance/python/acf/diff.py:24-30`
- reasoning: CI runs on ubuntu-latest. I ran the diff CLI on this node (cp1252, utf8_mode 0) without PYTHONUTF8. A reader thread raised UnicodeDecodeError on byte 0x9d, then AttributeError on stdout None, exit 1. That is loud, not silent. With PYTHONUTF8=1 it gave exit 0. So the CLAUDE.md note does cover the one breaking site. Weak leg: the 'outside this spec's theme' reason is in tension with §3's theme 'the checks they rest on', since the diff gate is the check §5.6 and DoD 3 add. The producer fix is three encoding= arguments. The justification is written, so this is not a ladder finding; see the advisory finding.

#### C79 — SURVIVED
- evidence: `plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:7; plugins/arch-compliance/tests/test_adr_exceptions.py:22; plugins/arch-compliance/tests/test_adr_import_graph.py:46; plugins/arch-compliance/tests/test_adr_skill_prose.py:53`
- reasoning: I ran it with PYTHONUTF8=1 and PYTHONPATH=plugins/arch-compliance/python. `--base origin/main` (origin/main = merge-base = c0281bf) gave 'No findings.', exit 0. `--base dfff93f5` gave exactly five WARN: bad.tsx:7 and :8 explicit-any, and hasattr at test_adr_exceptions.py:22, test_adr_import_graph.py:46 and test_adr_skill_prose.py:53, exit 0.

#### C80 — REFUTED
- evidence: `config/architecture/ARCHITECTURE.md:17; config/architecture/ARCHITECTURE.md:24; config/architecture/ARCHITECTURE.md:92; plugins/arch-compliance/python/acf/registry.py:65`
- reasoning: Read in-process, I dropped each heading line from the doctrine text and called missing_anchors on the host registry. For 12 anchors the row is reported. For `## Fail loud` (:24, anchor of two BLOCK rows) and `## React boundaries` (:92) it returns []. ARCHITECTURE.md:17 quotes both headings in backticks, and registry.py:65 tests only `arch_anchor in doctrine_text`. So removing either heading does not fail test_every_anchor_is_in_the_doctrine, and DoD item 2 is false for 2 of 14 anchors. The other two legs hold. A missing adr.yml makes load_model_file raise AcfInputError in test 1. A repeated id makes _registry() raise in tests 2 and 3.

#### C81 — UNPROVEN
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:53-55; plugins/arch-compliance/detectors/typescript/package.json:1-15`
- reasoning: Python detection via the root pyproject.toml is sure. The TypeScript side is judgment prose with no deterministic hook. The tracked TS is three bridge sources (scan.ts, rules/emptyCatch.ts, rules/explicitAny.ts) and two fixtures. The only package.json is the private detector package, not 'a clear app package'; spec §5.2 itself says 'no React app'. Three files is hardly a 'substantial tree'. The plan (docs/plans/PLAN_PLUGIN_SELF_HOSTING.md:78) pre-answers languages = both and says 'announce this if detection says Python only', so the author does not rely on the clauses firing. The merge outcome is verified (see C65): one ops.no-build-artifacts row with languages: both, and stock anchors verbatim. That the clauses detect TypeScript is not shown. The fix is to state that the user answers 'both', as the plan already does.

#### C82 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:104; config/architecture/mandates.yml:148-201; config/architecture/ARCHITECTURE.md:144`
- reasoning: `audit` is in the design document's call_sites vocabulary. The five manual rows all use call_sites: [audit]. The six unrowed sections (Live consumers :144, No completeness claims :156, Declared text decoding :169, Release discipline :180, Single point of definition :189, Scoped refactor :195) each end 'No row: no test enforces this yet.' One deviation: ARCHITECTURE.md:129-130 names a test path (test_adr_skill_prose.py), against §5.2's 'names the row id, not the test path' (see C83).

#### C83 — REFUTED
- evidence: `config/architecture/mandates.yml:181-190; plugins/arch-compliance/tests/test_adr_code_portability.py:7-8; plugins/arch-compliance/tests/test_adr_skill_prose.py:12-19`
- reasoning: There are five manual rows and all five detector files exist under plugins/arch-compliance/tests/. But plugin.prose-names-no-host's title is 'Skill prose and runtime messages name no host'. Its detector, test_adr_code_portability.py, scans only acf/adr/*.py and two runtime strings in parser.py and gate.py; it reads no skill prose. Skill prose is checked by test_adr_skill_prose.py, which spec §5.2's table names as this row's source while the registry points elsewhere. So that detector does not enforce the named rule.

### Unanchored findings

- **important**: The anchor check (missing_anchors, a literal substring test) is passed by the doctrine's own prose quoting an anchor. ARCHITECTURE.md:17 quotes `## Fail loud` and `## React boundaries`, so deleting either heading passes test_self_host and the /acf-mandate snippet. Matching the anchor against whole heading lines would close this at the same rung.
  - evidence: `config/architecture/ARCHITECTURE.md:17`
- **advisory**: The plugin.prose-names-no-host row points at test_adr_code_portability.py, which covers only the acf/adr modules and two runtime strings. Spec §5.2 names test_adr_skill_prose.py as the source, and the doctrine section (ARCHITECTURE.md:129-130) names a test path, against §5.2's own rule.
  - evidence: `config/architecture/mandates.yml:185`
- **advisory**: The repeated-id refusal sits at rung 3 in the loader. Rung 1, a validator on MandateRegistry that makes a duplicate-id registry impossible to construct, was not considered. The gap is small, because registry.py:60 is the only runtime constructor; test_enforcement.py:34 builds one directly.
  - evidence: `plugins/arch-compliance/python/acf/registry.py:33-35`
- **advisory**: The PYTHONUTF8=1 note is an environment workaround (rung 5) for a producer whose fix is three `encoding=` arguments. The crash comes from added_lines running for every changed file, prose included, before the suffix filter at cli_check_diff.py:121. The 'outside the theme' reason conflicts with §3's 'the checks they rest on'.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:121`
- **advisory**: Reviewers are blind to prior verdicts only through the SubagentStart hook. In this run the harness's own injected context (recent commit subjects, auto-memory) reached this reviewer, including a subject stating the v1 acceptance run was BLOCKED. The §5.4 sentence 'so reviewers stay blind ... to prior verdicts' overstates what the hook guarantees.
  - evidence: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:337-338`

### Looked for but did not find

- A second runtime constructor of MandateRegistry that bypasses the repeated-id refusal (only registry.py:60; test_enforcement.py:34 is a test)
- A second spelling of the detector-id union in the package, hooks, skills or tests (only cli_check_diff.py:25; hooks load without known_detectors)
- A consumer of bad_except.py or bad.tsx that goes through apply_registry and expects the BLOCK (only direct scanner tests and scan.ts self-test)
- Any review verdict or run reference in the SubagentStart hook's rendered inputs (template, row fields, first 4000 chars of ARCHITECTURE.md)
- A dispatch path by which a detection: manual row reaches a detector or the judge (none: id-based dispatch, judge filters llm)
- An HM tracked caller of acf.registry or acf-check-diff outside docs/ (none), or an HM .acf/ marker (absent)
- Silent failure of the diff gate under the cp1252 locale (it crashes loud with exit 1, not a clean pass)
- Gate-skill files listed by directory scan such that installed-only extra files would matter (the gate SKILL.md names its reviewer files explicitly)

### Mechanism traces

- **Repeated-id refusal in load_mandates**
  - invalid state: a mandates.yml list in which two rows share the same `id`
  - producer: `plugins/arch-compliance/skills/acf-setup/SKILL.md:110`
  - rung 3 (highest applicable 1); repairs=False
  - spec citation: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:364-371`
- **missing_anchors anchor-in-doctrine check**
  - invalid state: a registry row whose arch_anchor heading is absent from ARCHITECTURE.md as a heading line
  - producer: `config/architecture/ARCHITECTURE.md:17`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: "because the registry matches `arch_anchor` as a literal substring" (§5.2)
  - spec citation: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:372-376`
- **KNOWN_DETECTORS as the one detector union**
  - invalid state: a consumer validating registry rows against a detector-id set different from the diff CLI's (e.g. lacking guard ids)
  - producer: `plugins/arch-compliance/python/acf/cli_check_diff.py:25`
  - rung 2 (highest applicable 2); repairs=False
  - hardening rejected because: "because `acf.registry` cannot import `acf.judge` (which imports `acf.registry`)"
  - spec citation: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:377-380`
- **test_every_manual_row_names_an_existing_test_module**
  - invalid state: a detection: manual row whose detector is not an existing file under plugins/arch-compliance/tests/
  - producer: `config/architecture/mandates.yml:148-201`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: "A loader rule 'a manual detector is a file' would bind every host to this one's convention (§3)."
  - spec citation: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:395-403`
- **Row exemption token on the two fixture lines**
  - invalid state: a BLOCK finding from the hook or diff gate on a fixture line that must contain the forbidden pattern
  - producer: `plugins/arch-compliance/hooks/posttooluse_gate.py:254`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: "The fixture exists to contain the pattern ... the detector test calls the scanner directly, which still flags the line."
  - spec citation: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:349-350`
- **scripts/check_installed_skills.py byte check**
  - invalid state: a file of the clone's two gate-skill trees missing from, or byte-different in, <INSTALL_PATH>/skills/
  - producer: `plugins/arch-compliance/hooks/posttooluse_gate.py:22-26`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: "reinstall on mismatch, as 1d does" (§9); hooks/package scope deferred to follow-up 5
  - spec citation: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:316-325`
- **PYTHONUTF8=1 Windows note in CLAUDE.md**
  - invalid state: git subprocess stdout bytes undecodable under the locale codec (cp1252: 0x81/0x8D/0x8F/0x90/0x9D)
  - producer: `plugins/arch-compliance/python/acf/diff.py:24-30`
  - rung 5 (highest applicable 2); repairs=False
  - hardening rejected because: "Both are filed (§9): this spec's theme is declaration, doctrine and the checks they rest on." and "One plan, no spec: a defect with a test."
  - spec citation: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:314`
- **CI diff-gate step**
  - invalid state: a non-exempt BLOCK finding on an added line of a pull request
  - producer: `.github/workflows/ci.yml:40`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:405-414`

## Claims

- **C1** [premise] [load-bearing] (carried): At plugin main c0281bf (before this design) config/architecture/ is absent, .acf/ is gitignored (.gitignore:8), the root documents are README.md and SECURITY.md, and there is no CLAUDE.md. Verify at c0281bf (git ls-tree / git show), not at the branch head, where these files now exist.
  - spec citation: `.gitignore:8`
- **C2** [premise] (delta): At c0281bf docs/design/ holds ARCH_COMPLIANCE_FOR_SUPERPOWERS.md and this spec (docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md), and docs/reviews/ is absent. The spec offers no command or line citation for this beyond the appendix's git ls-tree row.
  - spec citation: `None`
- **C3** [premise] [load-bearing] (carried): The gate's host contract reads exactly two declared values (runs_dir, ledger_path) plus the doctrine path (plugins/arch-compliance/python/acf/adr/host.py:19-33); the compliance reviewer prompt reads the doctrine and each document it points to (plugins/arch-compliance/skills/adversarial-design-review/reviewers/compliance.md:12) and checks a doctrine's self-declared high-frequency misses first (compliance.md:47).
  - spec citation: `plugins/arch-compliance/python/acf/adr/host.py:19-33`
- **C4** [premise] [load-bearing] (delta): The /acf-setup merge rule for a two-language host does not resolve a repeated mandate id: it reads 'Keep every mandate id unique. If the same id appears in both (should not for stock profiles), stop and ask; never silently drop a row.' (plugins/arch-compliance/skills/acf-setup/SKILL.md:110). Both stock profiles carry ops.no-build-artifacts with identical bodies (plugins/arch-compliance/profiles/python-service/mandates.yml:34, plugins/arch-compliance/profiles/react-app/mandates.yml:23), so the parenthetical is false and a polyglot bootstrap of this repository reaches the stop-and-ask.
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:110`
- **C5** [premise] [load-bearing] (carried): /acf-setup writes config/architecture/mandates.yml and config/architecture/ARCHITECTURE.md from a profile and, for a two-language host, merges both profiles into one pair (plugins/arch-compliance/skills/acf-setup/SKILL.md:90-118); it also writes .acf/enabled (README.md:20: 'run /acf-setup (writes config/architecture/ and .acf/enabled)').
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:90-118`
- **C6** [premise] [load-bearing] (delta): The merged host registry (this branch's config/architecture/ files), run over this repository's whole history (--base dfff93f5, claimed to be the root commit) against the code at c0281bf, reports exactly seven findings: two BLOCK (plugins/arch-compliance/tests/fixtures/python/bad_except.py:4 fail-loud.bare-except; plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:4 fail-loud.empty-catch) and five WARN (bad.tsx:7 and :8 no-shims.explicit-any; no-shims.hasattr at plugins/arch-compliance/tests/test_adr_exceptions.py:22, plugins/arch-compliance/tests/test_adr_import_graph.py:46, plugins/arch-compliance/tests/test_adr_skill_prose.py:53). The set of exemption tokens the design adds rests on these being the only BLOCK findings. Obligation: this names a guard's output; run it (read-only CLI; it writes nothing) rather than reason about it. On Windows set PYTHONUTF8=1 and PYTHONPATH=plugins/arch-compliance/python. The spec's own evidence is the appendix recipe only.
  - spec citation: `None`
- **C7** [premise] [load-bearing] (carried): The registry schema accepts detection: manual rows and requires a detector string on every row, but checks that string against known detectors only for ast and guard rows (plugins/arch-compliance/python/acf/registry.py:9,19,56), so a manual row may carry a free-text detector such as a test-module path.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:9,19,56`
- **C8** [root_cause] [load-bearing] (delta): Root cause of the silent-shadow defect: at c0281bf load_mandates accepts two rows with the same id without refusing, and MandateRegistry.by_id builds a dict over the rows and keeps the last of the two (git show c0281bf:plugins/arch-compliance/python/acf/registry.py, lines 33-34), so a host whose registry repeats an id has one row silently shadowed. Verify each link at c0281bf: no refusal in the loader, and by_id last-wins.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py`
- **C9** [root_cause] [load-bearing] (delta): Root cause of the /acf-mandate validation failure: at c0281bf the skill's validation snippet builds its known-detector union from PYTHON_DETECTOR_IDS (with TS_DETECTOR_IDS and LLM_PROMPT_IDS), and PYTHON_DETECTOR_IDS equals the Python AST detector ids only (plugins/arch-compliance/python/acf/detectors/python_pack.py:25), excluding guard ids; therefore the snippet raises UnknownDetectorError on a stock profile's enforced guard row ops.no-build-artifacts (detector no_build_artifacts). Verify the snippet text at c0281bf (git show c0281bf:plugins/arch-compliance/skills/acf-mandate/SKILL.md) and each link.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/python_pack.py:25`
- **C10** [premise] (delta): At c0281bf the /acf-mandate skill asks the agent to check anchors by eye, at line 104: 'Also verify each arch_anchor is a substring of config/architecture/ARCHITECTURE.md'.
  - spec citation: `None`
- **C11** [premise] [load-bearing] (delta): At c0281bf the detector-id union is spelled in two places, plugins/arch-compliance/python/acf/cli_check_diff.py:25 and plugins/arch-compliance/tests/test_profile_drift.py (line 13 per the appendix), the anchor-in-doctrine check is a loop inside that test, and the package has no anchor-check function. This is the duplication decision 8 removes.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:25`
- **C12** [premise] (delta): Three subprocess calls in the package decode their output with the locale codec (text=True, no encoding): plugins/arch-compliance/python/acf/diff.py:24-30, plugins/arch-compliance/python/acf/adr/citations.py:62-65 and plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:49-56; the appendix recipe (grep -rn 'text=True' over plugins/arch-compliance/python and plugins/arch-compliance/hooks) is said to find exactly these. On a Windows node with a cp1252 locale the first raises inside the subprocess reader thread on a diff holding a character outside cp1252, which this repository's skill prose contains. CI runs on Linux (.github/workflows/ci.yml:11).
  - spec citation: `plugins/arch-compliance/python/acf/diff.py:24-30`
- **C13** [premise] [load-bearing] (carried): Deferral: the text-decoding defect (and the two git runners) can stay a filed follow-up in this phase (spec section 3, section 9 follow-up 1) because CI runs on Linux and on Windows the diff gate is run with PYTHONUTF8=1 (the CLAUDE.md Windows note), so no step of this design, including the acceptance run's own citation classification on this node, depends on the fix. Obligation: verify the condition still holds (that the Windows note exists in CLAUDE.md, CI is Linux, and nothing else in this design's steps runs the undeclared-decoding calls on Windows on non-cp1252 input without the note).
  - spec citation: `.github/workflows/ci.yml:11`
- **C14** [premise] (carried): At c0281bf CI (.github/workflows/ci.yml) runs pytest and the TypeScript self-test, and does not run the diff gate (acf.cli_check_diff / acf-check-diff) on this repository's own changes.
  - spec citation: `None`
- **C15** [premise] (carried): The plugin's acceptance test for a non-origin host builds a fixture host in a temporary directory and exercises the storage path through the Python API (plugins/arch-compliance/tests/test_adr_host_acceptance.py:74), not through a live skill run; a live skill run from the installed plugin has not happened outside HM (uncited). Not load-bearing: the acceptance design (a live run, section 6) would be the same if a prior live run existed.
  - spec citation: `plugins/arch-compliance/tests/test_adr_host_acceptance.py:74`
- **C16** [premise] (carried): HM's workstream E exit criterion 5 names Cayenne as the second repository (hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:5405-5406) and says 'Item 5 is the one that proves the objective rather than approximating it' (:5410), at HM 22eae4f9.
  - spec citation: `hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:5405-5406`
- **C17** [premise] [load-bearing] (delta): The plugin's hooks run on each subagent start and each Write/Edit/MultiEdit in a repository where the plugin is installed (plugins/arch-compliance/hooks/hooks.json) and no-op without .acf/enabled (plugins/arch-compliance/hooks/posttooluse_gate.py:72-81, plugins/arch-compliance/hooks/inject_constraints.py:71-80). With the marker: SubagentStart injects the registry's rows and a doctrine excerpt into the subagent's context (inject_constraints.py:153); PostToolUse scans the whole edited file, not its changed lines (added_lines=None at posttooluse_gate.py:254,281), and on a BLOCK finding exits 2, returning the findings as blocking feedback after the write (posttooluse_gate.py:131-134). These are the two and only effects the marker has.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:72-81`
- **C18** [premise] (carried): At c0281bf, 404 tests are collected from the single testpaths entry plugins/arch-compliance/tests (pyproject.toml), and the plugin version is 0.2.0 (pyproject.toml and plugins/arch-compliance/.claude-plugin/plugin.json).
  - spec citation: `pyproject.toml`
- **C19** [premise] [load-bearing] (delta): Sequencing start condition (section 5.7 step 1) is met: HM merged 1d on 2026-10-23 as 812f9c2b; the plugin is installed on this node at user scope from the clone, version 0.2.0, and its two gate skills (adversarial-design-review, responding-to-adversarial-review) are byte-identical to the clone (scripts/check_installed_skills.py). The installed plugin's location on this node is the installPath recorded in ~/.claude/plugins/installed_plugins.json (C:/Users/iball/.claude/plugins/cache/arch-compliance-for-superpowers/arch-compliance/0.2.0). Obligation: run the check (read-only) rather than read it.
  - spec citation: `scripts/check_installed_skills.py`
- **C20** [premise] [load-bearing] (delta): Deferral: the loader's new repeated-id refusal does not reach HM. HM's config/architecture/mandates.yml at 22eae4f9 is in HM's own schema (rows carry gemini_anchor and no languages or arch_anchor), so it does not load through load_mandates at all; and HM's tracked files name acf.registry, acf.cli_check_diff and acf-check-diff only in docs/design/ and docs/reviews/ prose. HM checkout: C:/Users/iball/Arduino/Projects/HistoricMansions/ (main at 22eae4f9). Obligation: execute the appendix recipe (load_mandates on HM's file with this branch's package; git -C <hm> grep) rather than reason.
  - spec citation: `None`
- **C21** [premise] [load-bearing] (carried): Deferral (non-goal, section 3): no ledger migration is needed. HM's ledger records for plugin-related specs stay in HM matched to their HM spec paths; the ledger is append-only; a moved spec leaves a stub at its HM path naming its new home, so a reader following a row's spec_path finds it. Condition to verify: nothing in the plugin package opens a ledger row's spec_path as a file or requires it to resolve in the repository that holds the ledger.
  - spec citation: `hm:docs/design/ADR_GATE_HOST_CONTRACT.md:80-81`
- **C22** [premise] [load-bearing] (carried): The gate's citation resolver has no notion of another repository: a prefixed path such as hm:x classifies as unresolved (resolve_citation, plugins/arch-compliance/python/acf/adr/citations.py:129, tests proposed, absolute, escaping, existing, suffix, ignored, historical, then gives up), and an unresolved citation is a hard fail before dispatch (plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:76-82,101). HM's host-contract runs handled their acf: citations by the controller mapping each prefixed path to the sibling checkout (hm:docs/reviews/adr_runs/ADR_GATE_HOST_CONTRACT_v3_2026-10-12.md:28,35,247).
  - spec citation: `plugins/arch-compliance/python/acf/adr/citations.py:129`
- **C23** [premise] (delta): Section 0 asserts that every unprefixed citation in this spec is a full repository-relative path with no shorthand, and that unprefixed paths are this repository while HM paths carry the hm: prefix. Precision/citation-form claim: check it against the spec's own text.
  - spec citation: `None`
- **C24** [premise] (delta): The HM host-contract spec's decision 6 reads 'This spec stays in this repository until 1d, and moves to the plugin repository after 1d's acceptance run.' (hm:docs/design/ADR_GATE_HOST_CONTRACT.md:80-81 at 22eae4f9).
  - spec citation: `hm:docs/design/ADR_GATE_HOST_CONTRACT.md:80-81`
- **C25** [premise] (carried): The HM rules the doctrine lifts exist with the quoted text at hm:GEMINI.md (HM 22eae4f9): bare except at :103, 'No defaulting to None' at :104, hasattr probing as shims at :105, temporary bridge code at :111, scoped refactor at :129, single point of definition at :136, POSIX format for persisted paths at :189, and 'Path.as_posix() alone is not sufficient' at :191.
  - spec citation: `hm:GEMINI.md:103`
- **C26** [premise] (delta): Deferral (decision 4): hm:GEMINI.md:61 says to 'append the superseding ledger amendment', which conflicts with the plugin's verification-pass rule (a verification pass writes no ledger record); it is corrected by the later housekeeping spec, not here, and 1d stays frozen. Not load-bearing: the sentence is HM's change surface and this design is the same whether or not it conflicts.
  - spec citation: `hm:GEMINI.md:61`
- **C27** [premise] [load-bearing] (delta): Deferral (non-goal, section 3): the registry contract leaves a detection: manual row's detector string free text, so the loader must not validate it. Evidence offered: the design document defines detector as 'Detector fn / guard module / LLM prompt id' (docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:102) and the /acf-mandate skill tells a manual row's author to 'Document how humans or external tools satisfy the mandate' (plugins/arch-compliance/skills/acf-mandate/SKILL.md:122).
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:102`
- **C28** [deletion] [load-bearing] (delta): What the design removes: test_profile_drift.py's own detector-union spelling and its anchor loop, the /acf-mandate snippet's narrower PYTHON_DETECTOR_IDS-based union and its 'verify each arch_anchor by eye' sentence, and MandateRegistry's silent last-wins on a repeated id; each is replaced by a consumer of the package (KNOWN_DETECTORS, missing_anchors, the loader's refusal). Verify each removal is complete on the branch head (no remaining copy) and safe (nothing still reads what was removed).
  - spec citation: `plugins/arch-compliance/tests/test_profile_drift.py`
- **C29** [premise] [load-bearing] (delta): Deferral (section 3, section 9 follow-up 4): the /acf-setup duplicate-id prose (plugins/arch-compliance/skills/acf-setup/SKILL.md:110, false 'should not for stock profiles' parenthetical) is left unchanged in this phase. Condition: this phase's bootstrap does not depend on the prose being right, because the answer at the stop-and-ask ('keep one row') is the user's, given in advance in the plan.
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:110`
- **C30** [premise] [load-bearing] (delta): Non-goal held: the design makes no change to the persisted ledger format, LedgerRow, LedgerAmendment or the TouchedSurface vocabulary, no change to any detector's logic, and no change to the gate skills' prose. Verify on the branch: git diff c0281bf..HEAD over plugins/arch-compliance/python/acf/adr/, plugins/arch-compliance/python/acf/detectors/, plugins/arch-compliance/detectors/typescript/src/, and plugins/arch-compliance/skills/adversarial-design-review/ and responding-to-adversarial-review/.
  - spec citation: `None`
- **C31** [premise] (delta): Deferrals to existing HM roadmap rows: the hook quiet flag (--quiet-disabled in hooks.json) was already filed by 1d (hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:213), and the 1a roadmap row already describes 'one git runner' (same file :5122). Not load-bearing: the design files them either way.
  - spec citation: `hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:213`
- **C32** [premise] (delta): HM's live install instruction is hm:CLAUDE.md:17 and HM's CLAUDE.md has the pointer-and-process form at hm:CLAUDE.md:21-35; the 1d plan's inline byte-check block is hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:669-681 and is an executed plan record.
  - spec citation: `hm:CLAUDE.md:17`
- **C33** [mandate] [load-bearing] (carried): Registry is the spine (docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:50): the plugin's own rules become config/architecture/mandates.yml rows with anchors; each doctrine section whose rule an existing test enforces (five sections) has a detection: manual row whose detector names that test module, and the doctrine section names the row id, not the test path; every row's arch_anchor is a literal substring of config/architecture/ARCHITECTURE.md; tests/test_self_host.py pins the anchors and the manual detectors.
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:50`
- **C34** [mandate] (carried): Declared, never defaulted (doctrine section; 1c decision 4): config/architecture/adr.yml declares both storage values and no default stands in for a missing declaration in acf.adr.host; the doctrine section states its scope and names the two package defaults outside it (plugins/arch-compliance/python/acf/repo.py:23-26, :32-44).
  - spec citation: `plugins/arch-compliance/python/acf/adr/host.py:19-33`
- **C35** [mandate] (carried): POSIX paths (doctrine section; lifted hm:GEMINI.md:189,191): adr.yml carries relative forward-slash paths, the model types them PosixStr which refuses a backslash rather than normalizing it (plugins/arch-compliance/python/acf/adr/contract.py:128), and the doctrine records that the plugin refuses rather than normalizes.
  - spec citation: `plugins/arch-compliance/python/acf/adr/contract.py:128`
- **C36** [mandate] [load-bearing] (carried): No shims / one rules document (principle 2, docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51): CLAUDE.md is a pointer and process file, not a second doctrine; it carries the byte-check command and points to the doctrine's ## Release discipline rather than restating the rule; and config/architecture/ARCHITECTURE.md points to the design document's five governing principles rather than restating them.
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51`
- **C37** [mandate] [load-bearing] (carried): The Superpowers override contract (principle 5, 'document that explicitly') is met by CLAUDE.md recording spec and plan locations, the gate as brainstorming's terminal state with BLOCKED returning through arch-compliance:responding-to-adversarial-review and re-run scope following the gate skill's revision class, the pre-gate byte-check command, the citation convention, and the PYTHONUTF8 Windows note.
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51`
- **C38** [mandate] (carried): The doctrine's ## No completeness claims rule (a factual claim about the tree is not load-bearing on a universal quantifier unless a re-runnable recipe backs it; source plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:152) is applied to this spec itself: its census lists per-item results with appendix commands, and its definition of done is per-item checks.
  - spec citation: `plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:152`
- **C39** [mandate] [load-bearing] (delta): Single point of definition (lifted hm:GEMINI.md:136, 'exactly one canonical implementation that every call site consumes'): after this design the anchor-in-doctrine check has one implementation (acf.registry.missing_anchors), the detector-id union one definition (acf.cli_check_diff.KNOWN_DETECTORS), mandate-id uniqueness one owner (the loader's refusal), and host paths one owner (acf.repo); the drift test, the host test and the /acf-mandate snippet consume them. The two git runners (plugins/arch-compliance/python/acf/diff.py:17, plugins/arch-compliance/python/acf/adr/citations.py:54) are recorded in the doctrine as the current breach.
  - spec citation: `hm:GEMINI.md:136`
- **C40** [mandate] (delta): One owner for host paths (doctrine section; plugins/arch-compliance/python/acf/repo.py:1-6): acf.repo is the one declaration of where ACF looks in a host and imports the standard library alone; the root tests/ and scripts/ this design adds import the acf.repo constants rather than re-spelling config/architecture paths; the doctrine states that the row's test scans plugins/arch-compliance/python/ and plugins/arch-compliance/hooks/ and that the root trees are checked by review.
  - spec citation: `plugins/arch-compliance/python/acf/repo.py:1-6`
- **C41** [mandate] (delta): Doctrine scope: config/architecture/ARCHITECTURE.md's opening paragraph states the population it governs (the package, the hooks, the skill prose, the TypeScript bridge, the plugin's tests and fixtures, and the repository-level tests/, scripts/ and config/), and states that the CI diff gate and the PostToolUse hook run the registry's detectors on changed .py, .ts and .tsx files anywhere in the repository while prose and configuration are held to the doctrine by review.
  - spec citation: `None`
- **C42** [mandate] (delta): Release discipline (doctrine section): this design changes a skill's prose (/acf-mandate SKILL.md), so the version is bumped to 0.2.1 in both pyproject.toml and plugins/arch-compliance/.claude-plugin/plugin.json; the doctrine section states that the byte check covers the two gate skills only and not the installed copy's hooks and package code, which the hooks run (plugins/arch-compliance/hooks/posttooluse_gate.py:22-26).
  - spec citation: `None`
- **C43** [mandate] (delta): Declared text decoding (doctrine section): the code this design adds or changes in the package and hooks introduces no subprocess text call without encoding='utf-8'; the doctrine records the three existing breaches with their recipe and states that the plugin's tests are outside the section's scope.
  - spec citation: `None`
- **C44** [mandate] (delta): Fail loud and One base exception: the new repeated-id refusal raises AcfInputError (an AcfError subclass with no stdlib mixin) naming each repeated id (plugins/arch-compliance/python/acf/registry.py:46-51); missing_anchors returns rather than defaults; the /acf-mandate snippet exits non-zero naming the rows with a missing anchor; scripts/check_installed_skills.py exits non-zero on any differing or missing file; no new code adds a bare or broad except or a None default for a missing value.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:46-51`
- **C45** [mandate] (delta): Prose names no host (doctrine section; plugins/arch-compliance/tests/test_adr_skill_prose.py): the skill prose this design changes (/acf-mandate SKILL.md) and any runtime message it adds (the loader's refusal) name no host repository, path or section.
  - spec citation: `plugins/arch-compliance/tests/test_adr_skill_prose.py`
- **C46** [mandate] (delta): Frozen ledger format (doctrine section; plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:443-452): the design changes no LedgerRow or LedgerAmendment field, and the doctrine section records that a verification pass writes no ledger record.
  - spec citation: `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:443-452`
- **C47** [mandate] [load-bearing] (delta): Live consumers (doctrine section: an export has a live call site in the package, a hook or a skill; a test is not a consumer): missing_anchors has a live consumer outside the tests (the /acf-mandate validation snippet), and KNOWN_DETECTORS has a live consumer (the diff CLI, and the snippet). Decision 8 rests on each generic check having a live non-test consumer.
  - spec citation: `None`
- **C48** [mandate] (delta): Scoped refactor (lifted hm:GEMINI.md:129): the design removes non-contractual patterns only in the code paths it changes (registry loader, drift test, /acf-mandate snippet, two fixtures) and does not expand into unrelated modules (the git runners, the decoding calls and the /acf-setup prose are filed, not changed).
  - spec citation: `hm:GEMINI.md:129`
- **C49** [shape_fit] [load-bearing] (carried): The design extends existing shape: the host contract as designed (one declaration file config/architecture/adr.yml and the fixed doctrine path; docs/design/ADR_GATE_HOST_CONTRACT.md section 5), the /acf-setup bootstrap, and the registry-is-the-spine principle (docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:50). It creates no second way to declare a host or to express a rule: the plugin's own rules are mandates.yml rows in the plugin's own registry format, and CLAUDE.md is a pointer and process file, not a second doctrine.
  - spec citation: `docs/design/ADR_GATE_HOST_CONTRACT.md`
- **C50** [shape_fit] [load-bearing] (delta): Anchor-in-doctrine check: tests/test_self_host.py's anchor test and plugins/arch-compliance/tests/test_profile_drift.py both consume acf.registry.missing_anchors (plugins/arch-compliance/python/acf/registry.py:63); there is one implementation and no other anchor-check loop or by-eye instruction remains in code, tests or skill prose that the design touches.
  - spec citation: `plugins/arch-compliance/tests/test_profile_drift.py`
- **C51** [shape_fit] [load-bearing] (delta): Detector-id union: tests/test_self_host.py, test_profile_drift.py and the /acf-mandate snippet all import KNOWN_DETECTORS from acf.cli_check_diff (plugins/arch-compliance/python/acf/cli_check_diff.py:25); there is one definition and no other spelling of the union remains in code or skills.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:25`
- **C52** [shape_fit] [load-bearing] (delta): Repeated-id check: the loader refuses a repeated id (one owner); MandateRegistry.by_id's silent last-wins is the existing element it replaces; the /acf-setup prose (plugins/arch-compliance/skills/acf-setup/SKILL.md:110) stays with its false parenthetical filed; no host-tier uniqueness test remains.
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:110`
- **C53** [shape_fit] [load-bearing] (delta): The manual-row detector check in tests/test_self_host.py (each manual row's detector is an existing file under plugins/arch-compliance/tests/) is adjacent to, not a duplicate of, load_mandates' ast/guard detector branch (plugins/arch-compliance/python/acf/registry.py:56): it is this host's policy, not the registry contract, so it stays in the host test rather than merging into the loader.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:56`
- **C54** [shape_fit] [load-bearing] (delta): Host config paths in the root tests/ and scripts/ this design adds are imported from acf.repo (plugins/arch-compliance/python/acf/repo.py:12-21); there is no second spelling of config/architecture/, mandates.yml, ARCHITECTURE.md or adr.yml paths in tests/test_self_host.py or scripts/check_installed_skills.py.
  - spec citation: `plugins/arch-compliance/python/acf/repo.py:12-21`
- **C55** [shape_fit] [load-bearing] (carried): scripts/check_installed_skills.py has one owner in this repository: no other script, test or hook compares the installed plugin against the clone; its algorithm is the same as the executed inline block at hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:669-681 (HM, outside this repository), which stays as a record.
  - spec citation: `hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:669-681`
- **C56** [shape_fit] (delta): CLAUDE.md's byte-check line carries only the command and points to the doctrine's ## Release discipline for the rule and the mismatch procedure; the rule is stated once (in the doctrine).
  - spec citation: `None`
- **C57** [shape_fit] [load-bearing] (delta): docs/design/ADR_GATE_HOST_CONTRACT.md is a copy of hm:docs/design/ADR_GATE_HOST_CONTRACT.md with a provenance block naming the canonical copy and the HM commit; two full copies exist until section 5.7 step 6 replaces HM's with a stub.
  - spec citation: `hm:docs/design/ADR_GATE_HOST_CONTRACT.md`
- **C58** [sweep] [load-bearing] (carried): Pattern sweep for specs about the plugin living in another repository: the hits are exactly the eight HM files hm:docs/design/ADR_*.md plus hm:docs/design/ARCH_COMPLIANCE_SHIFT_LEFT_GATING.md (ADR_GATE_HOST_CONTRACT, ADR_GATE_HM_CUTOVER, ADR_EXTRACTION_TO_PLUGIN, ADR_GATE_PLUGIN_COMPONENT, ADR_GATE_HM_ADOPTION, ADR_PER_FINDING_REVISION_CLASSING, ADR_REVISION_EVIDENCE_AND_CARRYOVER_INSTRUMENTATION, ARCH_COMPLIANCE_SHIFT_LEFT_GATING). Two are live: the host contract moves here and the 1d cutover stays because its change surface is HM's; the other six stay beside their HM ledger rows. Sweep by behaviour (specs whose subject is the plugin), not only by file name.
  - spec citation: `None`
- **C59** [sweep] (delta): Section 10's per-spec HM ledger row counts at 22eae4f9 (records in C:/Users/iball/Arduino/Projects/HistoricMansions/docs/reviews/adversarial_design_ledger.jsonl whose spec_path equals docs/design/<name>.md): ADR_GATE_HOST_CONTRACT 4, ADR_GATE_HM_CUTOVER 6, ADR_EXTRACTION_TO_PLUGIN 7, ADR_GATE_PLUGIN_COMPONENT 3, ADR_GATE_HM_ADOPTION 0, ADR_PER_FINDING_REVISION_CLASSING 0, ADR_REVISION_EVIDENCE_AND_CARRYOVER_INSTRUMENTATION 4, ARCH_COMPLIANCE_SHIFT_LEFT_GATING 0; and their statuses (superseded, v3 not re-dispatched, draft, stub, v4 draft, superseded) as the table says. Precision counts, not load-bearing.
  - spec citation: `None`
- **C60** [sweep] (carried): The stock rows set unenforced have no subject in this repository: facade.forbid-sink and fsm.transition-guard arrive unenforced from the python-service profile, and soft.react-boundaries is changed from partial because there is no React app (the TypeScript here is a detector bridge); each carries a one-line reason comment; the other stock rows have a subject here.
  - spec citation: `None`
- **C61** [shape_fit] [load-bearing] (delta): Root tests/ as a second pyproject testpaths entry fits existing shape: tests that are a property of this repository, not of the shipped plugin tree, are kept out of plugins/arch-compliance/ (README.md:93-95 keeps host-property tests out of it), so test_self_host.py and test_check_installed_skills.py live at the root.
  - spec citation: `README.md:93-95`
- **C62** [sweep] (delta): Exclusion sweep: the HM GEMINI.md rules the doctrine does not lift (HFSM section 5, UI isolation section 6, the metadata facade section 11, book-root resolution section 10, the content pipeline sections 12 and 13) have no subject in the plugin, so leaving them out is justified; the HM rules that do apply to Python here are the ones section 5.2 lists.
  - spec citation: `None`
- **C63** [mechanism_justification] [load-bearing] (delta): Refusing a repeated id in load_mandates (hardening the producer, for every host) rather than a host-tier uniqueness test or a recovery/normalising step is justified: a host that carried a duplicate had a row silently shadowed, and the refusal names it. The upgrade risk is bounded because this repository's registry has no repeated id and HM's registry is not read by load_mandates.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:46-51`
- **C64** [implementability] [load-bearing] (delta): KNOWN_DETECTORS stays in acf.cli_check_diff (plugins/arch-compliance/python/acf/cli_check_diff.py:25) because acf.registry cannot import acf.judge, which imports acf.registry; the /acf-mandate snippet, test_profile_drift.py and tests/test_self_host.py can import it from acf.cli_check_diff without an import cycle or side effect.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:25`
- **C65** [mechanism_justification] [load-bearing] (carried): Bootstrapping the host pair through /acf-setup rather than by hand (decision 7) is justified: it exercises the setup skill on a real host and keeps the pair diffable against the stock profiles (every stock anchor verbatim; non-applicable rows kept as status: unenforced rather than deleted). config/architecture/adr.yml is authored by hand because the skill does not write it.
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:90-118`
- **C66** [mechanism_justification] [load-bearing] (delta): Giving the two BLOCK fixture lines their row's exemption token with a reason (rather than a status flip, deleting the fixtures, or excluding the tests tree from the gate) is justified because the fixtures exist to contain the pattern and the detector tests call the scanners directly, bypassing the registry layer that honours the token.
  - spec citation: `plugins/arch-compliance/python/acf/enforcement.py:50`
- **C67** [implementability] [load-bearing] (delta): The registry layer honours a row exemption token on the flagged line (plugins/arch-compliance/python/acf/enforcement.py:50), in the forms '# fail-loud.bare-except-ok: <reason>' (Python) and '// fail-loud.empty-catch-ok: <reason>' (TypeScript), while scan_python_file and scan_typescript_file called directly still flag those lines, and the TypeScript self-test (npm test --prefix plugins/arch-compliance/detectors/typescript) still counts three findings in bad.tsx.
  - spec citation: `plugins/arch-compliance/python/acf/enforcement.py:50`
- **C68** [implementability] [load-bearing] (delta): With the two tokens in place, the PostToolUse hook on an edit to plugins/arch-compliance/tests/fixtures/python/bad_except.py or plugins/arch-compliance/tests/fixtures/typescript/bad.tsx returns WARN context only and exits 0 (the hook applies the registry layer that honours the token), whereas a BLOCK would exit 2 (plugins/arch-compliance/hooks/posttooluse_gate.py:131-134).
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:131-134`
- **C69** [implementability] [load-bearing] (delta): The SubagentStart hook's injected text carries no review verdict: _render_constraints renders the registry rows and a doctrine excerpt alone (plugins/arch-compliance/hooks/inject_constraints.py:153-176), so reviewers dispatched in this repository stay blind to each other and to prior verdicts. Check what the excerpt and the rows can contain in this repository's config/architecture/ files.
  - spec citation: `plugins/arch-compliance/hooks/inject_constraints.py:153-176`
- **C70** [implementability] [load-bearing] (carried): tests/test_self_host.py at the repository root is collected through the added testpaths entry in pyproject.toml, imports acf (through the configured pythonpath), and config/architecture/adr.yml loads through load_host_config (AdrHostConfig is extra='forbid', plugins/arch-compliance/python/acf/adr/host.py:22) declaring exactly the two paths of section 5.1.
  - spec citation: `pyproject.toml`
- **C71** [implementability] [load-bearing] (delta): plugins/arch-compliance/tests/test_acf_mandate_skill.py extracts the /acf-mandate validation snippet from the skill as written and runs it against a host built from the python-service profile: it exits 0 on the stock pair and non-zero, naming fail-loud.bare-except, when ## Fail loud is renamed. The extraction is robust to the skill's actual structure (it finds the right block).
  - spec citation: `plugins/arch-compliance/tests/test_acf_mandate_skill.py`
- **C72** [implementability] [load-bearing] (delta): The /acf-mandate snippet loads the registry with known_detectors=KNOWN_DETECTORS, prints the rows, and exits non-zero naming the rows whose anchor missing_anchors reports, so it accepts a stock profile's enforced guard row (ops.no-build-artifacts) that the c0281bf snippet rejected.
  - spec citation: `plugins/arch-compliance/skills/acf-mandate/SKILL.md`
- **C73** [implementability] [load-bearing] (delta): load_mandates raises AcfInputError naming each repeated id (plugins/arch-compliance/python/acf/registry.py:46-51) before MandateRegistry.by_id is built; its callers are the diff CLI, the LLM CLI and both hooks, and each surfaces the refusal (fails loud) rather than swallowing it. Pinned by test_a_repeated_mandate_id_is_refused in plugins/arch-compliance/tests/test_registry.py; missing_anchors (registry.py:63) pinned by test_missing_anchors_names_rows_whose_anchor_is_absent.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:46-51`
- **C74** [implementability] [load-bearing] (carried): A detection: manual row whose detector is a test-module path loads through load_mandates with known_detectors=KNOWN_DETECTORS and produces neither a finding nor an error in the diff gate (python -m acf.cli_check_diff) or in either hook: detectors dispatch by detector id for ast and guard rows only, and the registry layer only filters.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:56`
- **C75** [implementability] [load-bearing] (delta): The CI step: with checkout fetch-depth: 0, `python -m acf.cli_check_diff --repo . --base "origin/${{ github.base_ref || 'main' }}"` after pytest reads the host registry by default; on a pull_request event it diffs the branch against its merge-base with the base branch and fails the job on a BLOCK finding on an added line; on a push to main the base is main itself, --base diffs the merge-base three-dot range (plugins/arch-compliance/python/acf/diff.py:42-45), which is empty, and the step reports nothing and passes. The CI job must have the package importable and (for .ts/.tsx) the TypeScript bridge's dependencies installed for the step to run as described.
  - spec citation: `plugins/arch-compliance/python/acf/diff.py:42-45`
- **C76** [implementability] [load-bearing] (carried): scripts/check_installed_skills.py takes the installed plugin's directory, compares each file under the clone's two gate-skill trees (plugins/arch-compliance/skills/adversarial-design-review/ and responding-to-adversarial-review/) with the file at the same relative path under <INSTALL_PATH>/skills/ (filecmp.cmp(..., shallow=False)), prints 'installed gate skills identical to the clone' and exits 0, or prints each differing or missing path and exits 1; the installed cache's layout has skills/ at the same relative paths; tests/test_check_installed_skills.py pins three cases (identical, one changed byte, one missing installed file). Installed path on this node: C:/Users/iball/.claude/plugins/cache/arch-compliance-for-superpowers/arch-compliance/0.2.0.
  - spec citation: `hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:669-681`
- **C77** [mechanism_justification] [load-bearing] (carried): Making the acceptance run this spec's own binding review from this repository (decision 5, section 6) rather than reviewing it elsewhere first is justified because the doctrine the spec proposes cannot be read by the gate until this branch declares it; 1d's acceptance accepted any outcome because it proved plumbing, whereas here plumbing and review are the same run.
  - spec citation: `None`
- **C78** [mechanism_justification] [load-bearing] (carried): Filing the text-decoding fix and the one-git-runner consolidation as a follow-up (one plan, no spec) rather than fixing them here is justified: the fix is outside this spec's theme (declaration, doctrine and the checks they rest on), CI is on Linux, and the CLAUDE.md PYTHONUTF8=1 note covers Windows until the fix lands.
  - spec citation: `plugins/arch-compliance/python/acf/diff.py:24-30`
- **C79** [implementability] [load-bearing] (delta): Definition of done item 3: `python -m acf.cli_check_diff --repo . --base origin/main` from the root, with PYTHONUTF8=1 on Windows and PYTHONPATH=plugins/arch-compliance/python, exits 0 on the branch; with --base dfff93f5 it reports exactly the five WARN rows of section 5.4 and exits 0. Obligation: run it (read-only CLI).
  - spec citation: `None`
- **C80** [implementability] [load-bearing] (delta): Definition of done item 2: deleting config/architecture/adr.yml, or removing one anchor heading from config/architecture/ARCHITECTURE.md, fails tests/test_self_host.py; a duplicated row in config/architecture/mandates.yml fails it through the loader's refusal. Adjudicate by reading the three tests of tests/test_self_host.py and the code they call (do not mutate files or run tests).
  - spec citation: `None`
- **C81** [implementability] [load-bearing] (delta): /acf-setup run from this repository's root detects both languages, Python through pyproject.toml and TypeScript through the skill's '(or a clear app package)' and 'substantial tree' clauses (plugins/arch-compliance/skills/acf-setup/SKILL.md:53-55) since there is no root package.json and the TypeScript package is plugins/arch-compliance/detectors/typescript/package.json, and offers one merged pair; the duplicate-id stop is answered 'keep one row' by the user in advance, yielding one ops.no-build-artifacts row with languages: both, and every stock anchor survives verbatim.
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:53-55`
- **C82** [mechanism_justification] [load-bearing] (carried): Giving a detection: manual row only to the doctrine sections an existing test enforces (five sections), and ending the others with 'No row: no test enforces this yet.', is justified because a row is a pointer from rule to enforcement, not a promise; the manual rows use call_sites: [audit] from the design document's vocabulary (docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:104).
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:104`
- **C83** [implementability] (delta): config/architecture/mandates.yml on the branch has exactly five detection: manual rows (plugin.one-base-exception, plugin.one-owner-host-paths, plugin.declared-never-defaulted, plugin.prose-names-no-host, plugin.frozen-ledger-format) and each one's detector is an existing file under plugins/arch-compliance/tests/ that enforces the named rule.
  - spec citation: `None`
