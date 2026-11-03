# Adversarial design review — full detail

Spec: `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md` @ `19ff011267f7e2e2bdfafc2e9a59fc72dd03b7b6`
Kinds: feature
Outcome: **BLOCKED**
Claims: 20 · Reviewers: 4 · Converged: 1

## Blocking reasons

- load-bearing claim C4 (premise) is REFUTED: Two citations and one quoted line in this claim are false against the current tree. First, in plugins/arch-compliance/python/acf/adr/run_detail.py, line 47 is 'out: list[str] = []' inside _verdict_lines(payload); the filename template 'return Path(runs_dir) / f"{stem}_v{version}_{date}.md"' is at line 43 (and the Appendix at docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:277 quotes 'Line 47: name = f"{stem}_v{version}_{date}.md"', a variable assignment that does not exist in run_detail.py). Second, in plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md, line 110 is the Markdown table delimiter '|---|---|---|' inside section 2a; the response-record filename pattern ('<SPEC_STEM>_v<N>_response_<date>.md') is at line 133 (corroborated by plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:134). Only line 84 of plugins/arch-compliance/python/acf/adr/run_detail.py ('f"Spec: `{run.spec_path}` @ `{run.commit_sha}`"' as line 3 of render_run_detail output) holds.

## Absorptions

- PARTIAL_OVERLAP: 'Step 6 run-detail file selector (<STEM>_v<N>_<YYYY-MM-DD>.md excluding _response_, highest integer N) in plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md' shares responsibility 'Select the most recent full-dispatch run-detail file <STEM>_v<N>_<date>.md (excluding _response_ files) in repo / cfg.runs_dir for a spec' with plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:128-131 — Extract a shared run-detail lookup helper in plugins/arch-compliance/python/acf/adr/run_detail.py (alongside run_detail_path at :33-44) or align the prose rule in plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:128-131 and plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md Step 6 so both select the highest integer version N among <STEM>_v<N>_<YYYY-MM-DD>.md files (excluding _response_ files).
- SUBSUMED: 'Step 6 LedgerAmendment + append_amendment snippet in plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md' shares responsibility 'Construct LedgerAmendment and append a superseding JSONL record to repo / cfg.ledger_path' with plugins/arch-compliance/python/acf/adr/ledger.py:132-172 — none
- SUBSUMED: 'HOUSEKEEPING additions to FILES, FORBIDDEN, and _python_bodies() in plugins/arch-compliance/tests/test_adr_skill_prose.py' shares responsibility 'Verify skill prose portability against FORBIDDEN origin-host vocabulary and parse fenced Python blocks with ast.parse' with plugins/arch-compliance/tests/test_adr_skill_prose.py:12-54 — none
- SUBSUMED: 'HOUSEKEEPING and test_housekeeping_skill_invariants() in plugins/arch-compliance/tests/test_adr_skill_invariants.py' shares responsibility 'Verify skill YAML frontmatter, absence of backslashes, and required acf imports and prose invariants' with plugins/arch-compliance/tests/test_adr_skill_invariants.py:41-99 — none
- SUBSUMED: "'post-merge-housekeeping' entry in GATE_SKILLS in scripts/check_installed_skills.py" shares responsibility 'Byte-compare clone skill files against installed plugin skill files under <INSTALL_PATH>/skills/' with scripts/check_installed_skills.py:18-33 — none

## Converged findings

- [3 reviewers: refuter, sweeper, hardening] The run-detail filename pattern `^<STEM>_v([0-9]+)_([0-9]{4}-[0-9]{2}-[0-9]{2})\.md$` contains a literal backslash (`\.`), which will fail `test_no_skill_file_contains_a_backslash` (`plugins/arch-compliance/tests/test_adr_skill_invariants.py:70-73`) if written into `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md`.
  - evidence: `plugins/arch-compliance/tests/test_adr_skill_invariants.py:70-73`
  - evidence: `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:53`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:363, plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:223, docs/design/ADR_GATE_HOST_CONTRACT.md:213`
- reasoning: Opened both skill files and the host-contract spec. plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:362-364 states that absorbed, rejected, blocks_overturned, and escapes 'are amended later by the host's post-merge process appending a superseding record'. plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:223-224 states 'After merge, the host's post-merge process owns the absorbed / rejected / escapes amendment'. docs/design/ADR_GATE_HOST_CONTRACT.md:213 records replacing post-merge-housekeeping with 'by the host's post-merge process' because post-merge-housekeeping was still HM-local.

#### C2 — SURVIVED
- evidence: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:563-565, docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:62-68, C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:61`
- reasoning: Opened docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md at lines 62-68 (Decisions 3 and 4) and lines 563-565 (follow-up 2), as well as C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:61. Lines 563-565 explicitly list '2. Post-merge-housekeeping extraction (decision 3), the next spec. It also corrects hm:GEMINI.md:61 and adds the row-identity rule for amendments after a verification pass or user override.'

#### C3 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/ledger.py:139-140, plugins/arch-compliance/python/acf/adr/ledger.py:163-166, plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:443-453, plugins/arch-compliance/tests/test_adr_ledger.py:455-471`
- reasoning: Verified in plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:443-453 ('A verification pass writes no ledger record'), plugins/arch-compliance/python/acf/adr/ledger.py:139-140 (LedgerAmendment docstring stating records are 'matched to the original row by spec_path + commit_sha'), and plugins/arch-compliance/python/acf/adr/ledger.py:163-166 (absorbed, rejected, blocks_overturned, and escapes all declared as int | None = Field(default=None, ge=0), corroborated by test_amendment_counters_are_all_optional at plugins/arch-compliance/tests/test_adr_ledger.py:455-471).

#### C4 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/adr/run_detail.py:43, plugins/arch-compliance/python/acf/adr/run_detail.py:47, plugins/arch-compliance/python/acf/adr/run_detail.py:84, plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:110, plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:133`
- reasoning: Two citations and one quoted line in this claim are false against the current tree. First, in plugins/arch-compliance/python/acf/adr/run_detail.py, line 47 is 'out: list[str] = []' inside _verdict_lines(payload); the filename template 'return Path(runs_dir) / f"{stem}_v{version}_{date}.md"' is at line 43 (and the Appendix at docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:277 quotes 'Line 47: name = f"{stem}_v{version}_{date}.md"', a variable assignment that does not exist in run_detail.py). Second, in plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md, line 110 is the Markdown table delimiter '|---|---|---|' inside section 2a; the response-record filename pattern ('<SPEC_STEM>_v<N>_response_<date>.md') is at line 133 (corroborated by plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:134). Only line 84 of plugins/arch-compliance/python/acf/adr/run_detail.py ('f"Spec: `{run.spec_path}` @ `{run.commit_sha}`"' as line 3 of render_run_detail output) holds.

#### C5 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/.claude/skills/post-merge-housekeeping/SKILL.md:14, C:/Users/iball/Arduino/Projects/HistoricMansions/.claude/skills/post-merge-housekeeping/SKILL.md:59, C:/Users/iball/Arduino/Projects/HistoricMansions/.claude/skills/post-merge-housekeeping/SKILL.md:113, docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:88-96`
- reasoning: Executed both §4.1 regex recipes against C:/Users/iball/Arduino/Projects/HistoricMansions/.claude/skills/post-merge-housekeeping/SKILL.md (349 lines). Recipe A matched the exact 7 lines [14, 113, 124, 159, 214, 278, 326]. Recipe B matched 18 lines total [59, 64, 125, 126, 134, 141, 144, 155, 158, 161, 169, 278, 286, 287, 325, 326, 334, 347], and excluding the 2 lines already in Recipe A (278, 326) yielded the exact 16 additional lines [59, 64, 125, 126, 134, 141, 144, 155, 158, 161, 169, 286, 287, 325, 334, 347]. All 23 line numbers are listed in the §4.2 disposition table (docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:88-96).

#### C6 — SURVIVED
- evidence: `scripts/check_installed_skills.py:18, tests/test_check_installed_skills.py:23`
- reasoning: Opened both files. scripts/check_installed_skills.py:18 defines GATE_SKILLS = ("adversarial-design-review", "responding-to-adversarial-review"), and tests/test_check_installed_skills.py:22-28 defines _skill_tree(base: Path) with 'for skill in _load_script().GATE_SKILLS:' at line 23 to populate temporary fixture directories.

#### C7 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_skill_prose.py:12-28, plugins/arch-compliance/tests/test_adr_skill_prose.py:36-54`
- reasoning: Opened plugins/arch-compliance/tests/test_adr_skill_prose.py. Lines 12-19 define FILES (7 files across GATE and RESPOND) and FORBIDDEN; lines 22-28 define _python_bodies() extracting fenced python blocks and python -c bodies; lines 36-41 check FILES against FORBIDDEN; and lines 44-54 parse every body in _python_bodies() with ast.parse and verify that every 'from acf...' import symbol exists on the imported module.

#### C8 — SURVIVED
- evidence: `pyproject.toml:3, plugins/arch-compliance/.claude-plugin/plugin.json:3`
- reasoning: Opened both files: pyproject.toml:3 has 'version = "0.2.1"' and plugins/arch-compliance/.claude-plugin/plugin.json:3 has '"version": "0.2.1"'.

### Unanchored findings

- **important**: The run-detail filename regex specified for Step 6 (`^<STEM>_v([0-9]+)_([0-9]{4}-[0-9]{2}-[0-9]{2})\.md$`) contains a literal backslash (`\.`), which will cause `test_no_skill_file_contains_a_backslash` (`plugins/arch-compliance/tests/test_adr_skill_invariants.py:70-73`) to fail if placed in `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md`.
  - evidence: `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:53, docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:176, docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:263, plugins/arch-compliance/tests/test_adr_skill_invariants.py:70-73`
- **important**: Section 4.2 row 3 attributes `Name LIKE 'python%'` to lines `:124-126, :134, :141, :144, :155, :158-159, :161, :326, :334` of `hm:.claude/skills/post-merge-housekeeping/SKILL.md`, but `Name LIKE 'python%'` is actually at line 133, and line 143 (`curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:PORT/api/health`, which carries both an HM probe URL and a forbidden `\n` backslash) is missed by both Recipe A and Recipe B.
  - evidence: `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:80, docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:92, C:/Users/iball/Arduino/Projects/HistoricMansions/.claude/skills/post-merge-housekeeping/SKILL.md:133, C:/Users/iball/Arduino/Projects/HistoricMansions/.claude/skills/post-merge-housekeeping/SKILL.md:143`
- **advisory**: Selecting the run-detail file in `repo / cfg.runs_dir` solely by highest integer `int(version)` does not break ties when a spec version is re-run on a later date (as occurred in `C:/Users/iball/Arduino/Projects/HistoricMansions/docs/reviews/adr_runs/MARGIN_WRAP_FOOTNOTE_COLLISION_v1_2026-08-18.md` and `MARGIN_WRAP_FOOTNOTE_COLLISION_v1_2026-08-19.md`); breaking ties by `(int(version), date)` makes selection deterministic.
  - evidence: `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:53, docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:176`

### Looked for but did not find

- Any syntax error or unresolved `acf.*` import in the proposed Step 6 fenced Python block at docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:144-172 when parsed with ast.parse
- Any discrepancy in config/architecture/ARCHITECTURE.md section line ranges cited at docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:8, 190-197
- Any hardcoded skill list in tests/test_check_installed_skills.py or .claude-plugin/marketplace.json that would conflict with adding post-merge-housekeeping to GATE_SKILLS

## compliance

### Claim verdicts

#### C9 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:118-133, plugins/arch-compliance/python/acf/adr/host.py:19-33, docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:36-41, docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:106-138`
- reasoning: ARCHITECTURE.md:118-133 (## Declared, never defaulted) requires host-specific values that cannot be derived to be declared by the host rather than defaulted, failing or reporting loudly when absent. In docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:36-41 and :106-138, runs_dir and ledger_path are loaded via load_host_config (plugins/arch-compliance/python/acf/adr/host.py:19-33) from config/architecture/adr.yml, host post-merge operational conventions are read from ## Post-merge in the host's doctrine, omitted checks (branch lock, worktree daemon probe, post-merge CI) are explicitly reported in Step 8 as '<check>: not declared in ## Post-merge, skipped', and an omitted tracking target when follow-ups exist stops and asks the user.

#### C10 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:105-116, plugins/arch-compliance/python/acf/repo.py:21, plugins/arch-compliance/python/acf/repo.py:32-44, docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:145-150`
- reasoning: ARCHITECTURE.md:105-116 (## One owner for host paths) mandates that acf.repo is the single declaration of where ACF looks inside a host repository and that callers import acf.repo constants rather than spelling literal config/architecture/ paths. The Step 6 Python snippet in docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:145-150 imports ADR_REL and resolve_repo from acf.repo (defined at plugins/arch-compliance/python/acf/repo.py:21 and :32-44) and checks (repo / ADR_REL).is_file() without literal config/architecture/ strings.

#### C11 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:193-206, plugins/arch-compliance/python/acf/adr/run_detail.py:36-43, plugins/arch-compliance/python/acf/adr/run_detail.py:84, plugins/arch-compliance/python/acf/adr/ledger.py:146-149, docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:154-159, docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:176`
- reasoning: ARCHITECTURE.md:193-206 (## Single point of definition) requires a single canonical procedure rather than parallel implementations or fallbacks. Consistent with plugins/arch-compliance/python/acf/adr/ledger.py:146-149 (no ledger read-back in the pipeline) and plugins/arch-compliance/python/acf/adr/run_detail.py:36-43, 84 (which writes '{stem}_v{version}_{date}.md' with line 3 'Spec: `<run.spec_path>` @ `<run.commit_sha>`'), docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:154-159 and :176 define one procedure to obtain dispatch_commit_sha (selecting the highest integer version N among <STEM>_v<N>_<YYYY-MM-DD>.md in repo / cfg.runs_dir, excluding _response_ files, and reading line 3) without a second JSONL ledger parser or spec-header fallback.

#### C12 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:135-141, config/architecture/ARCHITECTURE.md:157-167, config/architecture/mandates.yml:192-201, plugins/arch-compliance/tests/test_adr_skill_prose.py:12-20, docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:190-198, docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:206-209`
- reasoning: ARCHITECTURE.md:135-141 (## Prose names no host) and ARCHITECTURE.md:157-167 (## No completeness claims) require that skill prose contain no origin-host names and that claims about the tree be scoped to what their recipe actually checks rather than an unbacked universal quantifier. In docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:190-198 and :206-209, plugins/arch-compliance/tests/test_adr_skill_prose.py:12-20 is extended to include post-merge-housekeeping/SKILL.md and four additional HistoricMansions housekeeping literals in FORBIDDEN, and both ARCHITECTURE.md:135-141 and config/architecture/mandates.yml:193 scope plugin.gate-prose-names-no-host to that enumerated list of known origin-host vocabulary.

#### C13 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:143-149, config/architecture/ARCHITECTURE.md:99-103, plugins/arch-compliance/python/acf/adr/ledger.py:64-172, plugins/arch-compliance/python/acf/exceptions.py:1-67, docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:60-62, docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:144-172`
- reasoning: ARCHITECTURE.md:143-149 (## Frozen ledger format) and ARCHITECTURE.md:99-103 (## One base exception) require that LedgerRow and LedgerAmendment fields change only through a dedicated persistence spec and that every ACF exception subclass AcfError alone. As stated in docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:60-62 and :144-172, this design does not modify LedgerRow or LedgerAmendment in plugins/arch-compliance/python/acf/adr/ledger.py:64-172, adds no exception class to plugins/arch-compliance/python/acf/exceptions.py:1-67, and uses no bare assert in the Step 6 skill prose snippet.

#### C14 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:182-191, plugins/arch-compliance/.claude-plugin/plugin.json:3, pyproject.toml:3, scripts/check_installed_skills.py:18, CLAUDE.md:20-23, docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:184-200`
- reasoning: ARCHITECTURE.md:182-191 (## Release discipline) requires bumping the plugin version in plugins/arch-compliance/.claude-plugin/plugin.json and pyproject.toml whenever skill prose changes and byte-checking installed gate skills via scripts/check_installed_skills.py. In docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:184-200, the design bumps version from '0.2.1' to '0.2.2' in plugins/arch-compliance/.claude-plugin/plugin.json:3 and pyproject.toml:3, adds 'post-merge-housekeeping' to GATE_SKILLS in scripts/check_installed_skills.py:18, and updates CLAUDE.md:20-23 and config/architecture/ARCHITECTURE.md:186-189.

### Unanchored findings


### Looked for but did not find

- All governing sections of config/architecture/ARCHITECTURE.md and docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51 are explicitly named in the spec header (docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:8-9), so unstated_mandates is empty.
- ## Build artifacts (config/architecture/ARCHITECTURE.md:66-68): checked whether the design stages or commits generated trees such as dist/ or build/ — not touched by this design.
- ## Fail-loud ratchet (config/architecture/ARCHITECTURE.md:70-73): checked whether bare/broad-except baseline counts or config/architecture/fail_loud_ratchet.json are affected — unenforced and not touched by this design.
- ## Façade sinks (config/architecture/ARCHITECTURE.md:75-79): checked whether any protected sink path is written — unenforced in this repository and not touched by this design.
- ## FSM transitions (config/architecture/ARCHITECTURE.md:81-85): checked whether any state machine or state field transition is added or modified — explicitly declared absent at docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:9 and not touched by this design.
- ## Soft fail-loud smells (config/architecture/ARCHITECTURE.md:87-90): checked whether the Step 6 Python snippet or test additions introduce silent fallback smells — none found; missing host config is gated explicitly on (repo / ADR_REL).is_file() and unmeasured counters are left None rather than defaulted to 0.
- ## React boundaries (config/architecture/ARCHITECTURE.md:92-97): checked whether any TypeScript/React view code is touched — unenforced here and not touched by this design.
- ## High-frequency misses (config/architecture/ARCHITECTURE.md:214-225): checked all six items (unbacked completeness claims, defaults re-entering for declared values, origin-host names in skill prose, stdlib mixins on exceptions, subprocess text calls without encoding, and package checks re-implemented in skills/tests) against docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md — all six are satisfied and cleared.

## sweeper

### Claim verdicts

#### C15 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/host.py:19-33, plugins/arch-compliance/python/acf/repo.py:18-44, plugins/arch-compliance/python/acf/adr/ledger.py:132-172, plugins/arch-compliance/python/acf/adr/ledger.py:231-237, plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:32-37`
- reasoning: Verified that plugins/arch-compliance/python/acf/repo.py:18-44 defines ARCH_REL, ADR_REL, and resolve_repo; plugins/arch-compliance/python/acf/adr/host.py:19-33 defines AdrHostConfig (extra='forbid') and load_host_config(repo); and plugins/arch-compliance/python/acf/adr/ledger.py:132-172, 231-237 defines LedgerAmendment and append_amendment (all re-exported in plugins/arch-compliance/python/acf/adr/__init__.py:18-24). Existing skills plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:32-37 and plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:45-48 consume resolve_repo and load_host_config in the same way, and docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:33-41, 144-172 introduces no second host config file or loader.

#### C16 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_skill_prose.py:12-54, plugins/arch-compliance/tests/test_adr_skill_invariants.py:41-99, scripts/check_installed_skills.py:18-33, tests/test_check_installed_skills.py:22-28`
- reasoning: Checked all test modules under plugins/arch-compliance/tests/ and tests/, plus scripts/check_installed_skills.py. plugins/arch-compliance/tests/test_adr_skill_prose.py:12-54 is the sole owner of skill-prose origin-host literal scanning (FILES, FORBIDDEN) and fenced Python AST/import checking (_python_bodies); plugins/arch-compliance/tests/test_adr_skill_invariants.py:41-99 is the sole owner of skill frontmatter, no-backslash, and entry-point import invariants; and scripts/check_installed_skills.py:18-33 (tested via GATE_SKILLS in tests/test_check_installed_skills.py:22-28) is the sole owner of installed-skill byte comparison.

#### C17 — SURVIVED
- evidence: `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:363, plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:223, docs/design/ADR_GATE_HOST_CONTRACT.md:213`
- reasoning: Read all 15 Markdown files across plugins/arch-compliance/skills/ (adversarial-design-review/SKILL.md, claims/extraction.md, reviewers/{refuter,compliance,sweeper,hardening}.md, responding-to-adversarial-review/SKILL.md, architecture-review/SKILL.md, architecture-review/auditors/{fail-loud,no-shims,posix-paths,react-boundaries}.md, acf-setup/SKILL.md, acf-mandate/SKILL.md). The only occurrences of 'post-merge process' (or any post-merge handoff phrase) are plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:363 and plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:223, matching the Phase 1c disposition in docs/design/ADR_GATE_HOST_CONTRACT.md:213.

### Unanchored findings

- **advisory**: Both adversarial-design-review Step 2b-ii and post-merge-housekeeping Step 6 specify prose rules for selecting the most recent <STEM>_v<N>_<date>.md run-detail file (excluding _response_ files) in runs_dir, but only post-merge-housekeeping specifies sorting by integer int(version) so v10 sorts after v9.
  - evidence: `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:128-131`
- **advisory**: The run-detail filename regex in docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:53, 176, 263 uses a backslash escape before .md$ that must be omitted or written without a backslash inside plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md so test_no_skill_file_contains_a_backslash passes.
  - evidence: `plugins/arch-compliance/tests/test_adr_skill_invariants.py:70-73`

### Looked for but did not find

- A second host configuration loader or YAML schema for housekeeping settings across plugins/arch-compliance/python/acf/ (searched load_model_file, require_file, ADR_REL, ARCH_REL)
- Any other occurrence of 'post-merge', 'housekeeping', 'append_amendment', or 'LedgerAmendment' across plugins/arch-compliance/skills/ outside adversarial-design-review/SKILL.md:363 and responding-to-adversarial-review/SKILL.md:223
- Any missed HistoricMansions-specific path or stack literal in hm:.claude/skills/post-merge-housekeeping/SKILL.md:1-350 beyond the 23 lines dispositioned in docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:86-97
- Any contradiction between docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md and approved design docs docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md, docs/design/ADR_GATE_HOST_CONTRACT.md, and docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md

### Relationships

- ADJACENT: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` — responsibility `Orchestrate post-merge verification, worktree/branch teardown, tracking-doc reconciliation, and post-merge ADR ledger amendment` — existing `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:301-325`
  - resolution: none
  - non-merge: adversarial-design-review and responding-to-adversarial-review govern pre-merge spec review and revision response before writing-plans, whereas post-merge-housekeeping runs after a branch/PR merges to verify content on the default branch, clean up worktrees/branches, reconcile docs, and append post-merge LedgerAmendment records.
- PARTIAL_OVERLAP: `Step 6 run-detail file selector (<STEM>_v<N>_<YYYY-MM-DD>.md excluding _response_, highest integer N) in plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` — responsibility `Select the most recent full-dispatch run-detail file <STEM>_v<N>_<date>.md (excluding _response_ files) in repo / cfg.runs_dir for a spec` — existing `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:128-131`
  - resolution: Extract a shared run-detail lookup helper in plugins/arch-compliance/python/acf/adr/run_detail.py (alongside run_detail_path at :33-44) or align the prose rule in plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:128-131 and plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md Step 6 so both select the highest integer version N among <STEM>_v<N>_<YYYY-MM-DD>.md files (excluding _response_ files).
- SUBSUMED: `Step 6 LedgerAmendment + append_amendment snippet in plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` — responsibility `Construct LedgerAmendment and append a superseding JSONL record to repo / cfg.ledger_path` — existing `plugins/arch-compliance/python/acf/adr/ledger.py:132-172`
  - resolution: none
- ADJACENT: `## Post-merge section in config/architecture/ARCHITECTURE.md` — responsibility `Declare host-specific operational conventions in config/architecture/ARCHITECTURE.md for skill prose to read` — existing `config/architecture/ARCHITECTURE.md:214-226`
  - resolution: none
  - non-merge: config/architecture/ARCHITECTURE.md:214-226 (## High-frequency misses) declares host review priorities read by the compliance reviewer during spec review, whereas ## Post-merge declares post-merge operational conventions (branch lock, worktree daemon probe, CI workflow, tracking target) read by post-merge-housekeeping.
- SUBSUMED: `HOUSEKEEPING additions to FILES, FORBIDDEN, and _python_bodies() in plugins/arch-compliance/tests/test_adr_skill_prose.py` — responsibility `Verify skill prose portability against FORBIDDEN origin-host vocabulary and parse fenced Python blocks with ast.parse` — existing `plugins/arch-compliance/tests/test_adr_skill_prose.py:12-54`
  - resolution: none
- SUBSUMED: `HOUSEKEEPING and test_housekeeping_skill_invariants() in plugins/arch-compliance/tests/test_adr_skill_invariants.py` — responsibility `Verify skill YAML frontmatter, absence of backslashes, and required acf imports and prose invariants` — existing `plugins/arch-compliance/tests/test_adr_skill_invariants.py:41-99`
  - resolution: none
- SUBSUMED: `'post-merge-housekeeping' entry in GATE_SKILLS in scripts/check_installed_skills.py` — responsibility `Byte-compare clone skill files against installed plugin skill files under <INSTALL_PATH>/skills/` — existing `scripts/check_installed_skills.py:18-33`
  - resolution: none

### Two-owner counts

- select_latest_run_detail_file_excluding_response_in_runs_dir: 2

### Document conflicts


## hardening

### Claim verdicts

#### C18 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/__init__.py:18-24, plugins/arch-compliance/python/acf/adr/ledger.py:132-172, plugins/arch-compliance/python/acf/adr/ledger.py:231-237, plugins/arch-compliance/python/acf/adr/host.py:28-33, plugins/arch-compliance/python/acf/repo.py:21, plugins/arch-compliance/python/acf/repo.py:32-44, plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:310-321, plugins/arch-compliance/tests/test_adr_skill_prose.py:44-54`
- reasoning: Verified the fenced Python block at docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:144-172 against Python's ast.parse rules and the live package exports. Ellipsis (...) keyword-argument values for absorbed, rejected, blocks_overturned, and escapes are valid ast.Constant(value=Ellipsis) expressions identical to plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:310-321, which test_every_python_body_parses_and_its_acf_imports_exist (plugins/arch-compliance/tests/test_adr_skill_prose.py:44-54) already parses. Every imported symbol exists in the live package: LedgerAmendment and append_amendment in plugins/arch-compliance/python/acf/adr/ledger.py:132, 231 (re-exported at plugins/arch-compliance/python/acf/adr/__init__.py:18-23, 48, 52), load_host_config in plugins/arch-compliance/python/acf/adr/host.py:28 (re-exported at plugins/arch-compliance/python/acf/adr/__init__.py:24, 60), and ADR_REL and resolve_repo in plugins/arch-compliance/python/acf/repo.py:21, 32.

#### C19 — SURVIVED
- evidence: `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:109-116, hm:.claude/skills/post-merge-housekeeping/SKILL.md:26-27, hm:.claude/skills/post-merge-housekeeping/SKILL.md:70-95, config/architecture/ARCHITECTURE.md:118-122`
- reasoning: Verified Step 1's two-step remote default-branch resolution at docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:110-116. Calling git symbolic-ref --short refs/remotes/origin/HEAD with one ref argument is a pure read of the local symbolic ref, and the fallback git ls-remote --symref origin HEAD queries the remote over the network without writing refs/remotes/origin/HEAD locally (unlike git remote set-head origin --auto), preserving the read-only invariant of Steps 1-2 (hm:.claude/skills/post-merge-housekeeping/SKILL.md:26-27, 70-95). If both commands return empty, docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:116 explicitly stops and asks the user rather than guessing main, honoring ## Declared, never defaulted (config/architecture/ARCHITECTURE.md:118-122).

#### C20 — SURVIVED
- evidence: `tests/test_self_host.py:32-34, plugins/arch-compliance/python/acf/registry.py:67-70, config/architecture/mandates.yml:1-213, config/architecture/ARCHITECTURE.md:24-212`
- reasoning: Verified tests/test_self_host.py:32-34 (test_every_anchor_is_in_the_doctrine), which delegates to missing_anchors in plugins/arch-compliance/python/acf/registry.py:67-70 ({line.strip() for line in doctrine_text.splitlines()}). Across all 17 rows in config/architecture/mandates.yml:5-212 there are 14 distinct arch_anchor headings, all present as exact ## heading lines in config/architecture/ARCHITECTURE.md:24-143. Updating the prose body of ## Prose names no host (config/architecture/ARCHITECTURE.md:135-141) and ## Release discipline (config/architecture/ARCHITECTURE.md:182-191), appending a new ## Post-merge section ending with 'No row: host operational declarations; no test enforces this.' (matching config/architecture/ARCHITECTURE.md:155, 167, 180, 191, 205-206, 212), and editing only the title field of plugin.gate-prose-names-no-host at config/architecture/mandates.yml:193 preserves all 14 arch_anchor heading lines.

### Unanchored findings

- **advisory**: Spec prose at docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:53, :176, and :263 writes the Step 6 run-detail filename regex with a backslash escape for the dot before md, which if copied verbatim into plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md would fail test_no_skill_file_contains_a_backslash at plugins/arch-compliance/tests/test_adr_skill_invariants.py:70-73 (SKILL.md prose should use the backslash-free pattern at docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:156 or a character class [.]md$).
  - evidence: `plugins/arch-compliance/tests/test_adr_skill_invariants.py:70-73, docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:53`

### Looked for but did not find

- Checked whether tests/test_check_installed_skills.py hardcodes the 2-element GATE_SKILLS tuple when GATE_SKILLS in scripts/check_installed_skills.py:18 expands to 3 skills; verified tests/test_check_installed_skills.py:23 iterates dynamically over _load_script().GATE_SKILLS.
- Checked whether test_host_values_are_passed_explicitly or test_no_python_c_body_opens_a_literal_ledger_path in plugins/arch-compliance/tests/test_adr_skill_prose.py:63-83 would fail when HOUSEKEEPING / 'SKILL.md' is added to _python_bodies(); verified neither is broken by Step 6's LedgerAmendment snippet.
- Checked whether LedgerAmendment in plugins/arch-compliance/python/acf/adr/ledger.py:132-172 requires integer defaults (0) for unmeasured counters; verified absorbed, rejected, blocks_overturned, and escapes all default to None (:163-166) with extra='forbid' (:155).

### Mechanism traces

- **Step 6 dispatch_commit_sha resolution from line 3 of the highest-int(version) run-detail file in repo / cfg.runs_dir**
  - invalid state: LedgerAmendment.commit_sha does not equal the prior full dispatch's LedgerRow.commit_sha because the spec header carries a verification-pass or user-override SHA without a LedgerRow, or because lexicographic sorting in runs_dir selected an author _response_ file or ordered v10 before v9
  - producer: `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:437-453`
  - rung 2 (highest applicable 2); repairs=False
  - hardening rejected because: Governed by ## Frozen ledger format (config/architecture/ARCHITECTURE.md:143-149) and plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:443-453: a controller verification pass is not a 4-reviewer dispatch and intentionally writes no LedgerRow, making the run-detail file written by plugins/arch-compliance/python/acf/adr/run_detail.py:43, 84 the single canonical persisted record per full dispatch.
  - spec citation: `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:53`
- **Step 6 (repo / ADR_REL).is_file() guard before load_host_config(repo) and append_amendment(...)**
  - invalid state: (repo / 'config/architecture/adr.yml').is_file() is False on a host repository that uses arch-compliance without enabling the optional ADR gate, where unconditional load_host_config(repo) raises AcfInputError
  - producer: `plugins/arch-compliance/python/acf/adr/host.py:28-33`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: load_host_config(repo) at plugins/arch-compliance/python/acf/adr/host.py:28-33 is governed by ## Declared, never defaulted (config/architecture/ARCHITECTURE.md:118-124) and must fail loud when ADR is invoked without config/architecture/adr.yml, whereas post-merge-housekeeping also runs in hosts and on branches that do not use ADR (docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:48, 264).
  - spec citation: `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:149`
- **Extending GATE_SKILLS in scripts/check_installed_skills.py and FILES/_python_bodies in test_adr_skill_prose.py and test_adr_skill_invariants.py to include post-merge-housekeeping**
  - invalid state: Installed copy of post-merge-housekeeping/SKILL.md drifts from the repository clone, or plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md contains FORBIDDEN origin-host vocabulary, backslashes, or broken acf imports
  - producer: `scripts/check_installed_skills.py:18`
  - rung 2 (highest applicable 2); repairs=False
  - hardening rejected because: Collapses installed-skill byte checking and prose/AST invariant checking into the existing single-owner guards (scripts/check_installed_skills.py:18-33, plugins/arch-compliance/tests/test_adr_skill_prose.py:12-54, plugins/arch-compliance/tests/test_adr_skill_invariants.py:41-73) per ## Single point of definition and ## Release discipline (config/architecture/ARCHITECTURE.md:182-206).
  - spec citation: `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:185`

## Claims

- **C1** [premise] [load-bearing]: In plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:363 and plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:223, the prose currently delegates post-merge ledger amendments to 'the host's post-merge process', as recorded by docs/design/ADR_GATE_HOST_CONTRACT.md:213.
  - spec citation: `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:363`
- **C2** [premise] [load-bearing]: docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:563-565 schedules the post-merge-housekeeping extraction spec as follow-up 2 and specifies that it adds the row-identity rule for amendments after a verification pass or user override.
  - spec citation: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:563-565`
- **C3** [premise] [load-bearing]: A controller verification pass (plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:443-453) writes no LedgerRow; LedgerAmendment matches its target LedgerRow by spec_path + commit_sha (plugins/arch-compliance/python/acf/adr/ledger.py:139-140) and its optional counters absorbed, rejected, blocks_overturned, and escapes default to None (plugins/arch-compliance/python/acf/adr/ledger.py:163-166).
  - spec citation: `plugins/arch-compliance/python/acf/adr/ledger.py:139-140`
- **C4** [premise] [load-bearing]: plugins/arch-compliance/python/acf/adr/run_detail.py:47 names full-dispatch detail files '{stem}_v{version}_{date}.md' and line 84 renders 'Spec: `{run.spec_path}` @ `{run.commit_sha}`' as line 3 of the markdown output, while author response files in runs_dir are named '<STEM>_v<N>_response_<date>.md' (plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:110).
  - spec citation: `plugins/arch-compliance/python/acf/adr/run_detail.py:47`
- **C5** [premise] [load-bearing]: Running §4.1 Recipe A and Recipe B against hm:.claude/skills/post-merge-housekeeping/SKILL.md (349 lines at b652fab05) selects 7 lines under Recipe A (:14, :113, :124, :159, :214, :278, :326) and 16 additional lines under Recipe B (:59, :64, :125, :126, :134, :141, :144, :155, :158, :161, :169, :286, :287, :325, :334, :347), all 23 of which are placed in §4.2.
  - spec citation: `hm:.claude/skills/post-merge-housekeeping/SKILL.md:14`
- **C6** [premise] [load-bearing]: scripts/check_installed_skills.py:18 defines GATE_SKILLS = ('adversarial-design-review', 'responding-to-adversarial-review'), and tests/test_check_installed_skills.py:23 iterates over _load_script().GATE_SKILLS to build its temporary fixture trees.
  - spec citation: `scripts/check_installed_skills.py:18`
- **C7** [premise] [load-bearing]: plugins/arch-compliance/tests/test_adr_skill_prose.py:12-28 checks FILES (the 7 gate skill files) against FORBIDDEN and parses fenced ```python blocks and python -c bodies in _python_bodies() with ast.parse, verifying that every 'from acf...' import resolves.
  - spec citation: `plugins/arch-compliance/tests/test_adr_skill_prose.py:12-28`
- **C8** [premise]: pyproject.toml:3 and plugins/arch-compliance/.claude-plugin/plugin.json:3 both currently carry version '0.2.1'.
  - spec citation: `pyproject.toml:3`
- **C9** [mandate] [load-bearing]: ## Declared, never defaulted (config/architecture/ARCHITECTURE.md:118-133): host-specific post-merge conventions are read from ## Post-merge in the host's doctrine (and ledger_path/runs_dir from config/architecture/adr.yml); when ## Post-merge omits a check (branch lock, worktree daemon probe, post-merge CI), Step 8 explicitly reports '<check>: not declared in ## Post-merge, skipped' rather than skipping silently.
  - spec citation: `config/architecture/ARCHITECTURE.md:118-133`
- **C10** [mandate] [load-bearing]: ## One owner for host paths (config/architecture/ARCHITECTURE.md:105-116): the Step 6 Python snippet in post-merge-housekeeping/SKILL.md imports ADR_REL and resolve_repo from acf.repo (plugins/arch-compliance/python/acf/repo.py:21, 32-44) rather than spelling literal config/architecture/ paths.
  - spec citation: `config/architecture/ARCHITECTURE.md:105-116`
- **C11** [mandate] [load-bearing]: ## Single point of definition (config/architecture/ARCHITECTURE.md:193-206): Step 6 defines a single recipe to obtain dispatch_commit_sha (the highest integer N among <STEM>_v<N>_<YYYY-MM-DD>.md in repo / cfg.runs_dir, excluding _response_ files, reading line 3) and does not embed a second JSONL ledger parser in skill prose or a second spec-header fallback.
  - spec citation: `config/architecture/ARCHITECTURE.md:193-206`
- **C12** [mandate] [load-bearing]: ## Prose names no host and ## No completeness claims (config/architecture/ARCHITECTURE.md:135-141, 157-167): plugins/arch-compliance/tests/test_adr_skill_prose.py is extended to check post-merge-housekeeping/SKILL.md against the enumerated FORBIDDEN list of known origin-host (HistoricMansions) vocabulary, and both the doctrine and config/architecture/mandates.yml:193 scope the row's claim to that enumerated vocabulary rather than an unbacked universal quantifier.
  - spec citation: `config/architecture/ARCHITECTURE.md:135-141`
- **C13** [mandate] [load-bearing]: ## Frozen ledger format (config/architecture/ARCHITECTURE.md:143-149) and ## One base exception (config/architecture/ARCHITECTURE.md:99-103): this design modifies neither LedgerRow nor LedgerAmendment in plugins/arch-compliance/python/acf/adr/ledger.py:67-172, adds no exception class, and uses no bare assert in skill prose.
  - spec citation: `config/architecture/ARCHITECTURE.md:143-149`
- **C14** [mandate] [load-bearing]: ## Release discipline (config/architecture/ARCHITECTURE.md:182-191): changing skill prose bumps the version in plugins/arch-compliance/.claude-plugin/plugin.json:3 and pyproject.toml:3 from '0.2.1' to '0.2.2', adds 'post-merge-housekeeping' to GATE_SKILLS in scripts/check_installed_skills.py:18, and updates CLAUDE.md and ARCHITECTURE.md:186-189.
  - spec citation: `config/architecture/ARCHITECTURE.md:182-191`
- **C15** [shape_fit] [load-bearing]: plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md extends plugins/arch-compliance/skills/ alongside adversarial-design-review and responding-to-adversarial-review, consuming the existing acf.repo (ADR_REL, resolve_repo) and acf.adr (load_host_config, LedgerAmendment, append_amendment) surface without adding a second host config file or loader.
  - spec citation: `plugins/arch-compliance/python/acf/adr/host.py:19-33`
- **C16** [shape_fit] [load-bearing]: Extending FILES, FORBIDDEN, and _python_bodies() in plugins/arch-compliance/tests/test_adr_skill_prose.py:12-28, extending plugins/arch-compliance/tests/test_adr_skill_invariants.py:41-99, and adding 'post-merge-housekeeping' to GATE_SKILLS in scripts/check_installed_skills.py:18 reuse the single existing owners of skill-prose portability testing, skill-invariant testing, and installed-skill byte checking.
  - spec citation: `plugins/arch-compliance/tests/test_adr_skill_prose.py:12-28`
- **C17** [sweep] [load-bearing]: Across plugins/arch-compliance/skills/, the only occurrences of 'post-merge process' are plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:363 and plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:223, both of which are re-pointed to 'post-merge-housekeeping'.
  - spec citation: `plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:223`
- **C18** [implementability] [load-bearing]: The fenced ```python block in §5.2 parses cleanly under ast.parse (using Ellipsis `...` placeholders for absorbed, rejected, blocks_overturned, escapes, matching plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:310-321), and every symbol it imports from acf.adr (LedgerAmendment, append_amendment, load_host_config) and acf.repo (ADR_REL, resolve_repo) exists in the package.
  - spec citation: `plugins/arch-compliance/python/acf/adr/__init__.py:18-24`
- **C19** [implementability] [load-bearing]: Step 1's default-branch resolution (`git symbolic-ref --short refs/remotes/origin/HEAD` with read-only fallback `git ls-remote --symref origin HEAD`) mutates no local refs during the read-only Steps 1-2 phase and fails loud by stopping to ask the user if both return empty.
  - spec citation: `hm:.claude/skills/post-merge-housekeeping/SKILL.md:70-95`
- **C20** [implementability] [load-bearing]: Adding ## Post-merge (ending with 'No row: host operational declarations; no test enforces this.') to config/architecture/ARCHITECTURE.md and updating plugin.gate-prose-names-no-host's title in config/architecture/mandates.yml:193 preserves all 14 mandate arch_anchor substrings verified by tests/test_self_host.py:31-34.
  - spec citation: `tests/test_self_host.py:31-34`
