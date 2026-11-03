# Adversarial design review — full detail

Spec: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` @ `2254c9c56ee27c8b5ff56aeb29368b54ddc0d960`
Kinds: defect, feature
Outcome: **CLEARED**
Claims: 83 · Reviewers: 4 · Converged: 0

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `.gitignore:8; README.md:1; SECURITY.md:1; CLAUDE.md:1; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:112`
- reasoning: Ran `git ls-tree --name-only c0281bf`, `git ls-tree c0281bf config`, and `git show c0281bf:.gitignore`. At c0281bf, the root contains `.claude-plugin`, `.github`, `.gitignore`, `LICENSE`, `README.md`, `SECURITY.md`, `docs`, `plugins`, and `pyproject.toml` (no `config/` directory and no `CLAUDE.md`), and `.gitignore:8` is `.acf/`.

#### C2 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:1; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:114`
- reasoning: Ran `git ls-tree -r --name-only c0281bf docs`. At c0281bf, `docs/design/` contains only `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md` and `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md`, and `docs/reviews/` does not exist.

#### C3 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/host.py:19-33; plugins/arch-compliance/skills/adversarial-design-review/reviewers/compliance.md:12; plugins/arch-compliance/skills/adversarial-design-review/reviewers/compliance.md:47`
- reasoning: Opened `host.py:19-33` (`AdrHostConfig` declares `runs_dir` and `ledger_path` with `extra='forbid'`, and `load_host_config` requires `repo / ARCH_REL` before loading `repo / ADR_REL`) and `compliance.md` (`:12` instructs reading `config/architecture/ARCHITECTURE.md` in full plus every document it points to; `:47` instructs checking the doctrine's self-declared high-frequency misses first).

#### C4 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:110; plugins/arch-compliance/profiles/python-service/mandates.yml:34-45; plugins/arch-compliance/profiles/react-app/mandates.yml:23-34`
- reasoning: Opened `acf-setup/SKILL.md:110`, which contains the exact quoted merge instruction and parenthetical, and opened both profile `mandates.yml` files: `python-service/mandates.yml:34-45` and `react-app/mandates.yml:23-34` both define `id: ops.no-build-artifacts` with identical fields.

#### C5 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:90-118; plugins/arch-compliance/skills/acf-setup/SKILL.md:145; README.md:20`
- reasoning: Opened `acf-setup/SKILL.md:90-118` (Step 5 copies or merges `mandates.yml` and `ARCHITECTURE.md` into `<host>/config/architecture/`), `acf-setup/SKILL.md:140-148` (Step 7 writes `<host>/.acf/enabled`), and `README.md:20` ('run `/acf-setup` (writes `config/architecture/` and `.acf/enabled`)').

#### C6 — SURVIVED
- evidence: `plugins/arch-compliance/tests/fixtures/python/bad_except.py:4; plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:4; plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:7; plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:8; plugins/arch-compliance/tests/test_adr_exceptions.py:22; plugins/arch-compliance/tests/test_adr_import_graph.py:46; plugins/arch-compliance/tests/test_adr_skill_prose.py:53`
- reasoning: Inspected `bad_except.py` and `bad.tsx` at `c0281bf` (before the inline `-ok` tokens were added on line 4 of each) and ran `python -m acf.cli_check_diff --repo . --base dfff93f5 --json`. With the two tokens present on the branch, the CLI outputs the exact five WARN findings (`bad.tsx:7`, `bad.tsx:8`, `test_adr_exceptions.py:22`, `test_adr_import_graph.py:46`, `test_adr_skill_prose.py:53`); at `c0281bf` without those two tokens on `bad_except.py:4` and `bad.tsx:4`, those two lines produce the two BLOCK findings.

#### C7 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:9; plugins/arch-compliance/python/acf/registry.py:19; plugins/arch-compliance/python/acf/registry.py:56-63; config/architecture/mandates.yml:151-152`
- reasoning: Opened `registry.py`: `Detection` includes `'manual'` at `:9`, `Mandate.detector: str` is required at `:19`, and `load_mandates` at `:56-63` only checks `m.detector not in known_detectors` when `m.status == 'enforced'` and `m.detection in {'ast', 'guard'}`.

#### C8 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:33-45; plugins/arch-compliance/tests/test_registry.py:40-47`
- reasoning: Ran `git show c0281bf:plugins/arch-compliance/python/acf/registry.py`: at `c0281bf`, `MandateRegistry` had no validator and `by_id` at lines 32-34 returned `{m.id: m for m in self.mandates}`, silently overwriting earlier rows with the same id. On the branch, `MandateRegistry._unique_ids` (`registry.py:33-41`) refuses repeated ids with `AcfInputError`, pinned by `test_registry.py:40-47`.

#### C9 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:16-22; plugins/arch-compliance/python/acf/detectors/__init__.py:11-18; plugins/arch-compliance/tests/test_acf_mandate_skill.py:44-47`
- reasoning: Ran `git show c0281bf:plugins/arch-compliance/skills/acf-mandate/SKILL.md` and `git show c0281bf:plugins/arch-compliance/python/acf/detectors/python_pack.py`. At `c0281bf`, the skill snippet computed `known = PYTHON_DETECTOR_IDS | TS_DETECTOR_IDS | LLM_PROMPT_IDS`, and `python_pack.py:25` set `PYTHON_DETECTOR_IDS = PYTHON_AST_DETECTOR_IDS` (which excludes `GUARD_DETECTOR_IDS` in `detectors/__init__.py:11-18`, including `no_build_artifacts`), causing `load_mandates` to raise `UnknownDetectorError` on `ops.no-build-artifacts`.

#### C10 — SURVIVED
- evidence: `plugins/arch-compliance/skills/architecture-review/SKILL.md:62; plugins/arch-compliance/skills/acf-setup/SKILL.md:137; plugins/arch-compliance/skills/acf-mandate/SKILL.md:99-101`
- reasoning: Verified via `git show c0281bf:plugins/arch-compliance/skills/acf-mandate/SKILL.md` that line 104 read `Also verify each arch_anchor is a substring of config/architecture/ARCHITECTURE.md (same discipline as profile drift tests).`, `architecture-review/SKILL.md:62` spells `Path("config/architecture/mandates.yml")`, and `acf-setup/SKILL.md:137` instructs a manual anchor check (`ensuring every arch_anchor from mandates.yml still appears as an exact heading substring in the file ACF will use`).

#### C11 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:25; plugins/arch-compliance/python/acf/registry.py:24; plugins/arch-compliance/python/acf/judge.py:154; plugins/arch-compliance/tests/test_profile_drift.py:7-8`
- reasoning: Verified at `c0281bf` that `KNOWN_DETECTORS = ALL_PYTHON_DETECTOR_IDS | TS_DETECTOR_IDS | LLM_PROMPT_IDS` was defined in both `cli_check_diff.py:25` and `test_profile_drift.py:13`, the anchor check was an inline `for mandate in regs.mandates: assert mandate.arch_anchor in arch_text` loop in `test_profile_drift.py:30-34`, and `git grep -n "arch_anchor" c0281bf -- plugins/arch-compliance/python` matched only `registry.py:23` and `judge.py:154`.

#### C12 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:24-30; plugins/arch-compliance/python/acf/adr/citations.py:62-65; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:49-56; .github/workflows/ci.yml:11`
- reasoning: Opened all three files (`diff.py:24-30`, `citations.py:62-65`, `typescript_bridge.py:49-56`): each calls `subprocess.run(..., capture_output=True, text=True, check=False)` without an `encoding` argument. `.github/workflows/ci.yml:11` specifies `runs-on: ubuntu-latest`.

#### C13 — SURVIVED
- evidence: `.github/workflows/ci.yml:11; CLAUDE.md:35-37; config/architecture/ARCHITECTURE.md:166-175`
- reasoning: Opened `.github/workflows/ci.yml:11` (`runs-on: ubuntu-latest`), `CLAUDE.md:35-37` (which records running the diff gate on Windows with `PYTHONUTF8=1`), and `config/architecture/ARCHITECTURE.md:166-175` (which records the three undeclared-encoding subprocess calls as declared debt for §9 follow-up 1).

#### C14 — SURVIVED
- evidence: `.github/workflows/ci.yml:36-45; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:154`
- reasoning: Ran `git show c0281bf:.github/workflows/ci.yml`: at `c0281bf` the workflow ran only `pytest` and `npm test` (the TypeScript detector self-test) and had no `acf.cli_check_diff` step.

#### C15 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_host_acceptance.py:26-40; plugins/arch-compliance/tests/test_adr_host_acceptance.py:74-94`
- reasoning: Opened `test_adr_host_acceptance.py`: `_host(tmp_path)` (`:26-40`) builds a temporary fixture git repository with `config/architecture/adr.yml` and `ARCHITECTURE.md`, and `test_a_non_origin_host_runs_the_storage_path` (`:74-94`) exercises `load_host_config`, `classify_citations`, `run_detail_path`, `write_run_detail`, and `append_row` through the Python API.

#### C16 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:6216-6221; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:159-162`
- reasoning: Ran `git -C C:/Users/iball/Arduino/Projects/HistoricMansions grep -n -E "second repository \(Cayenne\)|proves the objective" 22eae4f9 -- docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md`, confirming that at `22eae4f9` lines 5405-5406 and 5410 (now at lines 6216-6217 and 6221 in HM HEAD) contain the exact cited text.

#### C17 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/hooks.json:4-27; plugins/arch-compliance/hooks/posttooluse_gate.py:72-81; plugins/arch-compliance/hooks/posttooluse_gate.py:131-134; plugins/arch-compliance/hooks/posttooluse_gate.py:254; plugins/arch-compliance/hooks/posttooluse_gate.py:281-294; plugins/arch-compliance/hooks/inject_constraints.py:71-80; plugins/arch-compliance/hooks/inject_constraints.py:153`
- reasoning: Opened `hooks.json`, `posttooluse_gate.py`, and `inject_constraints.py`: `hooks.json` registers `SubagentStart` (`*`) and `PostToolUse` (`Write|Edit|MultiEdit`); both hooks exit 0 when `.acf/enabled` is missing (`posttooluse_gate.py:72-81`, `inject_constraints.py:71-80`); `_render_constraints` (`inject_constraints.py:153-176`) renders the mandate list and `ARCHITECTURE.md` excerpt; `posttooluse_gate.py` scans whole `.py`/`.ts`/`.tsx` files (`added_lines=None` at `:254` and `:281`), runs `scan_build_artifact_paths` (`:284-294`), and returns exit code 2 on BLOCK findings in hook format (`:131-134`).

#### C18 — SURVIVED
- evidence: `pyproject.toml:3; pyproject.toml:23; plugins/arch-compliance/tests/test_registry.py:40-57; plugins/arch-compliance/tests/test_acf_mandate_skill.py:44-59`
- reasoning: Ran `git show c0281bf:pyproject.toml`, confirming `version = "0.2.0"` and `testpaths = ["plugins/arch-compliance/tests"]`. Running `pytest --collect-only -q plugins/arch-compliance/tests` on the branch collects 408 tests, which is the 404 tests at `c0281bf` plus the 2 new tests in `test_registry.py` and 2 new tests in `test_acf_mandate_skill.py` added by this branch.

#### C19 — SURVIVED
- evidence: `scripts/check_installed_skills.py:22-33; scripts/check_installed_skills.py:36-47; C:/Users/iball/.claude/plugins/installed_plugins.json:53-60`
- reasoning: Verified `git -C C:/Users/iball/Arduino/Projects/HistoricMansions log -1 --format=%h,%cd --date=short 812f9c2b` outputs `812f9c2b7,2026-10-23`, `installed_plugins.json:53-60` shows `arch-compliance@arch-compliance-for-superpowers` installed at `scope: user`, `version: 0.2.0`, `gitCommitSha: c0281bfa665e8a5175b9dcbcc28de73e692e3c19`, and running `python scripts/check_installed_skills.py C:/Users/iball/.claude/plugins/cache/arch-compliance-for-superpowers/arch-compliance/0.2.0` prints `installed gate skills identical to the clone` and exits 0.

#### C20 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/config/architecture/mandates.yml:5-15; plugins/arch-compliance/python/acf/registry.py:14-27; plugins/arch-compliance/python/acf/registry.py:48-55`
- reasoning: Opened `hm:config/architecture/mandates.yml:1-60`: its rows carry `gemini_anchor` and lack `languages` and `arch_anchor`, which `acf.registry.Mandate` (`registry.py:14-27`) requires. `git -C C:/Users/iball/Arduino/Projects/HistoricMansions grep -l -e 'acf\.registry' -e 'acf\.cli_check_diff' -e 'acf-check-diff' 22eae4f9` matches only files under `docs/design/` and `docs/reviews/adr_runs/`.

#### C21 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/docs/design/ADR_GATE_HOST_CONTRACT.md:80-81; plugins/arch-compliance/python/acf/adr/ledger.py:75; plugins/arch-compliance/python/acf/adr/ledger.py:157; plugins/arch-compliance/python/acf/adr/run_detail.py:34-43`
- reasoning: Grepped `spec_path` across `plugins/arch-compliance/python` and opened `ledger.py` and `run_detail.py`: `LedgerRow.spec_path` (`:75`) and `LedgerAmendment.spec_path` (`:157`) are validated only as `PosixStr = Field(min_length=1)`, and `run_detail_path` (`run_detail.py:34-43`) only takes `Path(spec_path).stem`. Nothing in the package opens a ledger row's `spec_path` or checks that it exists on disk.

#### C22 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/citations.py:129-185; plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:76-82; plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:101; C:/Users/iball/Arduino/Projects/HistoricMansions/docs/reviews/adr_runs/ADR_GATE_HOST_CONTRACT_v3_2026-10-12.md:28; C:/Users/iball/Arduino/Projects/HistoricMansions/docs/reviews/adr_runs/ADR_GATE_HOST_CONTRACT_v3_2026-10-12.md:35`
- reasoning: Opened `citations.py:129-185` (`resolve_citation` has no prefix mapping and falls through to `return 'unresolved', None`), `adversarial-design-review/SKILL.md:76-82,101` (unresolved citations raise `UnresolvableCitationError` and hard-fail before dispatch), and `hm:docs/reviews/adr_runs/ADR_GATE_HOST_CONTRACT_v3_2026-10-12.md:28,35,247` (showing `acf:` prefixed paths resolved against the sibling plugin checkout).

#### C23 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/citations.py:40-46; plugins/arch-compliance/python/acf/adr/citations.py:121-126; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:29-33`
- reasoning: Opened `citations.py`: `_bare_path` lives at `:40-46` and `_resolve_by_suffix` at `:106-126` matches `tracked == needle or tracked.endswith('/' + needle)` on whole path components (note that `citations.py:32-44` is the imports, `CitationKind`, `_LINE_SUFFIX_RE`, and `def _bare_path`, while suffix matching is at `:106-126`, so the substance of the claim holds even though the spec's line citation `:32-44` points at `_bare_path` rather than `_resolve_by_suffix`).

#### C24 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/docs/design/ADR_GATE_HOST_CONTRACT.md:80-81; docs/design/ADR_GATE_HOST_CONTRACT.md:89-90`
- reasoning: Opened `C:/Users/iball/Arduino/Projects/HistoricMansions/docs/design/ADR_GATE_HOST_CONTRACT.md:80-81` (unchanged since `22eae4f9`), which reads verbatim: `6. **This spec stays in this repository until 1d, and moves to the plugin repository after 1d's acceptance run.**`

#### C25 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:103-105; C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:111; C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:129; C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:136; C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:189-191; config/architecture/ARCHITECTURE.md:38-41`
- reasoning: Opened `C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md` (unchanged since `22eae4f9`) at lines 103, 104, 105, 111, 129, 136, 189, and 191, and verified each of the eight quoted rules matches the text in `GEMINI.md` and `config/architecture/ARCHITECTURE.md`.

#### C26 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:61; plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:443-452; config/architecture/ARCHITECTURE.md:141-143`
- reasoning: Opened `C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:61` ('append the superseding ledger amendment, and record the user's approval to proceed in the spec header'), which conflicts with `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:443-452` ('A verification pass writes no ledger record'), and verified it is filed as follow-up 2 in §9 for the housekeeping spec.

#### C27 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:102; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:184; plugins/arch-compliance/skills/acf-mandate/SKILL.md:122; plugins/arch-compliance/python/acf/registry.py:56-63`
- reasoning: Opened `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:102` ('Detector fn / guard module / LLM prompt id / manual verification pointer'), `:184` ('Unknown detector id referenced by an enforced `ast` or `guard` row → drift/registry validation fail'), and `plugins/arch-compliance/skills/acf-mandate/SKILL.md:122` ('Document how humans or external tools satisfy the mandate').

#### C28 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_profile_drift.py:7-8; plugins/arch-compliance/tests/test_profile_drift.py:27-30; plugins/arch-compliance/skills/acf-mandate/SKILL.md:91-101; plugins/arch-compliance/python/acf/detectors/python_pack.py:16-24; plugins/arch-compliance/python/acf/detectors/__init__.py:30-35; tests/test_check_installed_skills.py:22-27; plugins/arch-compliance/python/acf/registry.py:33-41`
- reasoning: Inspected the branch files and git diffs from `c0281bf..HEAD`, and grepped for `PYTHON_DETECTOR_IDS` across the repository (zero hits; only `ALL_PYTHON_DETECTOR_IDS` and `PYTHON_AST_DETECTOR_IDS` remain). All five removals and the repeated-id refusal on `MandateRegistry` are complete on the branch head and leave no broken callers.

#### C29 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:110; plugins/arch-compliance/skills/acf-setup/SKILL.md:137; plugins/arch-compliance/skills/architecture-review/SKILL.md:62; config/architecture/ARCHITECTURE.md:113-116; config/architecture/ARCHITECTURE.md:196-200`
- reasoning: Verified via `git diff c0281bf..HEAD` that `acf-setup/SKILL.md` and `architecture-review/SKILL.md` are untouched on the branch, both breaches are recorded in `config/architecture/ARCHITECTURE.md:113-116,196-200` and §9 follow-up 4, and the host bootstrap and tests (`tests/test_self_host.py`) do not depend on rewriting those prose lines.

#### C30 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/ledger.py:56-60; plugins/arch-compliance/python/acf/adr/ledger.py:64-172; plugins/arch-compliance/python/acf/detectors/python_pack.py:27-50; plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:1-20`
- reasoning: Ran `git diff c0281bf..HEAD` over `plugins/arch-compliance/python/acf/adr/ledger.py`, `plugins/arch-compliance/python/acf/detectors/`, `plugins/arch-compliance/detectors/`, `plugins/arch-compliance/skills/adversarial-design-review/`, and `plugins/arch-compliance/skills/responding-to-adversarial-review/`: zero changes in `ledger.py` or the two gate skills, and the only change in `detectors/` is removing the unused `PYTHON_DETECTOR_IDS` alias.

#### C31 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:293; C:/Users/iball/Arduino/Projects/HistoricMansions/docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:5933; plugins/arch-compliance/hooks/hooks.json:10`
- reasoning: Verified via `git -C C:/Users/iball/Arduino/Projects/HistoricMansions grep -n` at `22eae4f9` that `docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:213` (now `:293` at HM HEAD) files the `hooks.json` `--quiet-disabled` follow-up from 1d, and `:5122` at `22eae4f9` (now `:5933` at HM HEAD) describes 'one git runner' in the 1a phase row.

#### C32 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/CLAUDE.md:17; C:/Users/iball/Arduino/Projects/HistoricMansions/CLAUDE.md:21-35; C:/Users/iball/Arduino/Projects/HistoricMansions/docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:669-681; CLAUDE.md:7-24`
- reasoning: Opened `hm:CLAUDE.md:17` (the live install instruction for `arch-compliance`), `hm:CLAUDE.md:21-35` (the pointer-and-process overrides section), and `hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:669-681` (the ticked Task 8 Step 1 inline byte-check script).

### Unanchored findings

- **advisory**: Spec §4.1 item 14 places a paraphrase in quotation marks ("Quickly confirm every `arch_anchor` in `config/architecture/mandates.yml` exists in `ARCHITECTURE.md`") as the text of `plugins/arch-compliance/skills/acf-setup/SKILL.md:137`, whereas line 137 actually reads "- replace the stub with a copy/symlink/pointer note to their real doc, ensuring every `arch_anchor` from `mandates.yml` still appears as an exact heading substring in the file ACF will use."
  - evidence: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:191-193; plugins/arch-compliance/skills/acf-setup/SKILL.md:137`
- **advisory**: Spec §0 cites `plugins/arch-compliance/python/acf/adr/citations.py:32-44` for the resolver's whole-component suffix match, but `:32-44` is imports, `CitationKind`, `_LINE_SUFFIX_RE`, and `def _bare_path`; the whole-component suffix match (`tracked == needle or tracked.endswith("/" + needle)`) is in `_resolve_by_suffix` at `plugins/arch-compliance/python/acf/adr/citations.py:106-126`.
  - evidence: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:31-33; plugins/arch-compliance/python/acf/adr/citations.py:106-126`

### Looked for but did not find

- any remaining caller or reference to `PYTHON_DETECTOR_IDS` across `plugins/`, `tests/`, `scripts/`, or `config/`
- any file in `git diff --stat c0281bf..HEAD` lacking a disposition row in spec §4.2
- any discrepancy between the 12 HM specs and ledger record counts in spec §10 and `hm:docs/reviews/adversarial_design_ledger.jsonl` at `22eae4f9`
- any `arch_anchor` in `config/architecture/mandates.yml` missing as a stripped line in `config/architecture/ARCHITECTURE.md`, or any `detection: manual` row whose `detector` path does not exist on disk

## compliance

### Claim verdicts

#### C33 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:50, config/architecture/mandates.yml:148, config/architecture/ARCHITECTURE.md:99, tests/test_self_host.py:32`
- reasoning: Principle 4 at docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:50 ('Registry is the spine — prose anchors, detectors, auditors, and call sites must agree or tests fail') is satisfied: config/architecture/mandates.yml:148-212 defines six detection: manual rows across five plugin rules, each naming its test module under plugins/arch-compliance/tests/ in detector; config/architecture/ARCHITECTURE.md:99-144 names the row ids rather than test paths, with every arch_anchor matching a stripped heading line; and tests/test_self_host.py:32-42 pins both missing_anchors and the manual detector file paths.

#### C34 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:118, config/architecture/adr.yml:1, plugins/arch-compliance/python/acf/adr/host.py:19, plugins/arch-compliance/python/acf/repo.py:23, plugins/arch-compliance/python/acf/repo.py:32`
- reasoning: The doctrine's ## Declared, never defaulted section (config/architecture/ARCHITECTURE.md:118-128) requires host values for the gate to be declared in config/architecture/adr.yml with no fallback default. config/architecture/adr.yml:1-2 declares runs_dir and ledger_path; plugins/arch-compliance/python/acf/adr/host.py:19-33 defines AdrHostConfig with both fields required (min_length=1, extra='forbid') and load_host_config requiring both ARCH_REL and ADR_REL; and config/architecture/ARCHITECTURE.md:124-128 explicitly scopes the rule and records the two package defaults outside it at plugins/arch-compliance/python/acf/repo.py:23-26 and plugins/arch-compliance/python/acf/repo.py:32-44.

#### C35 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:55, config/architecture/adr.yml:1, plugins/arch-compliance/python/acf/adr/host.py:24, plugins/arch-compliance/python/acf/adr/contract.py:129`
- reasoning: The doctrine's ## POSIX paths section (config/architecture/ARCHITECTURE.md:55-64) quotes hm:GEMINI.md:189 and hm:GEMINI.md:191 and records at lines 62-64 that the plugin is stricter than normalization because PosixStr refuses backslashes. config/architecture/adr.yml:1-2 uses relative forward-slash paths, plugins/arch-compliance/python/acf/adr/host.py:24-25 types runs_dir and ledger_path as PosixStr, and plugins/arch-compliance/python/acf/adr/contract.py:60-91 and 129 reject any backslash with ValueError.

#### C36 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:48, CLAUDE.md:3, CLAUDE.md:20, config/architecture/ARCHITECTURE.md:13`
- reasoning: Principle 2 at docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:48 forbids parallel mandate lists and shims. CLAUDE.md:3 points directly to config/architecture/ARCHITECTURE.md and config/architecture/mandates.yml, CLAUDE.md:20-23 gives the byte-check command and points to ## Release discipline in the doctrine rather than restating the rule, and config/architecture/ARCHITECTURE.md:13-15 points to docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51 rather than restating the five governing principles.

#### C37 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:51, config/architecture/ARCHITECTURE.md:11, CLAUDE.md:11, CLAUDE.md:15, CLAUDE.md:20, CLAUDE.md:25, CLAUDE.md:33`
- reasoning: Principle 5 at docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:51 ('where this plugin's plan/DoD/constraint defaults conflict with Superpowers generics, the host architecture + registry win; document that explicitly') and config/architecture/ARCHITECTURE.md:11-13 are satisfied by CLAUDE.md:7-37, which explicitly records the spec and plan locations (lines 11-14), the gate as brainstorming's terminal state with BLOCKED routing to arch-compliance:responding-to-adversarial-review and revision-class re-run scope (lines 15-19), the pre-gate byte-check command (lines 20-23), the citation convention (lines 25-31), and the PYTHONUTF8=1 Windows note (lines 33-37).

#### C38 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:152, docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:11, docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:198, docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:521, plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:152`
- reasoning: The doctrine's ## No completeness claims section (config/architecture/ARCHITECTURE.md:152-162, quoting plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:152) is obeyed by docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md: section 0 (lines 11-37) bounds its lifted-clause statement with an explicit count ('§5.2 lists the eight lifted clauses') and contains no unbacked universal quantifier; the §4.1 census (lines 110-200, including item 15's git grep recipe at line 198) is backed by the executed recipes in the appendix; and §8 (lines 521-545) states per-item verification checks.

#### C39 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:188, plugins/arch-compliance/python/acf/registry.py:34, plugins/arch-compliance/python/acf/registry.py:67, plugins/arch-compliance/python/acf/cli_check_diff.py:25, scripts/check_installed_skills.py:18, tests/test_self_host.py:14, plugins/arch-compliance/tests/test_profile_drift.py:7, plugins/arch-compliance/skills/acf-mandate/SKILL.md:91`
- reasoning: The doctrine's ## Single point of definition section (config/architecture/ARCHITECTURE.md:188-201, quoting hm:GEMINI.md:136) holds across all five responsibilities: missing_anchors is defined once at plugins/arch-compliance/python/acf/registry.py:67-70, KNOWN_DETECTORS once at plugins/arch-compliance/python/acf/cli_check_diff.py:25, MandateRegistry._unique_ids once at plugins/arch-compliance/python/acf/registry.py:34-41, GATE_SKILLS once at scripts/check_installed_skills.py:18 (imported by tests/test_check_installed_skills.py:23), and host paths once in plugins/arch-compliance/python/acf/repo.py:12-29; plugins/arch-compliance/tests/test_profile_drift.py:7-8, tests/test_self_host.py:14-16, and plugins/arch-compliance/skills/acf-mandate/SKILL.md:91-93 consume them. The two git runners (plugins/arch-compliance/python/acf/diff.py:17 and plugins/arch-compliance/python/acf/adr/citations.py:54) and the two skill-prose breaches (plugins/arch-compliance/skills/architecture-review/SKILL.md:62 and plugins/arch-compliance/skills/acf-setup/SKILL.md:137) are explicitly recorded in config/architecture/ARCHITECTURE.md:192-200 and filed in docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:560-576.

#### C40 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:105, plugins/arch-compliance/python/acf/repo.py:1, plugins/arch-compliance/tests/test_repo_paths.py:18, tests/test_self_host.py:16, plugins/arch-compliance/skills/architecture-review/SKILL.md:62`
- reasoning: The doctrine's ## One owner for host paths section (config/architecture/ARCHITECTURE.md:105-116) matches plugins/arch-compliance/python/acf/repo.py:1-10 (which declares host paths and imports only __future__ and pathlib) and plugins/arch-compliance/tests/test_repo_paths.py:18-25 (which scans python/ and hooks/). Root tests/test_self_host.py:16 imports ARCH_REL and MANDATES_REL from acf.repo, and config/architecture/ARCHITECTURE.md:111-116 explicitly states the test scope, review coverage for root tests/ and scripts/, and the recorded skill-prose breach at plugins/arch-compliance/skills/architecture-review/SKILL.md:62.

#### C41 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:3, docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:265, .github/workflows/ci.yml:40`
- reasoning: config/architecture/ARCHITECTURE.md:3-11 explicitly enumerates the governed population (plugins/arch-compliance/python/acf/, plugins/arch-compliance/hooks/, plugins/arch-compliance/skills/, plugins/arch-compliance/detectors/typescript/, plugins/arch-compliance/tests/, and root tests/, scripts/, and config/) and states that the CI diff gate (.github/workflows/ci.yml:40) and PostToolUse hook run the registry's detectors on changed .py, .ts, and .tsx files anywhere in the repository while prose and configuration are held to the doctrine by review.

#### C42 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:177, pyproject.toml:3, plugins/arch-compliance/.claude-plugin/plugin.json:3, plugins/arch-compliance/hooks/posttooluse_gate.py:22`
- reasoning: The doctrine's ## Release discipline section (config/architecture/ARCHITECTURE.md:177-186) requires bumping the version in plugins/arch-compliance/.claude-plugin/plugin.json and pyproject.toml when skill prose changes; both pyproject.toml:3 and plugins/arch-compliance/.claude-plugin/plugin.json:3 are bumped to 0.2.1 for the /acf-mandate SKILL.md change, and config/architecture/ARCHITECTURE.md:183-185 records that scripts/check_installed_skills.py covers only the two gate skill trees while the hooks run the installed copy's hooks/ and python/ (plugins/arch-compliance/hooks/posttooluse_gate.py:22-26).

#### C43 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:164, plugins/arch-compliance/python/acf/registry.py:33, plugins/arch-compliance/skills/acf-mandate/SKILL.md:99, plugins/arch-compliance/tests/test_acf_mandate_skill.py:40`
- reasoning: The doctrine's ## Declared text decoding section (config/architecture/ARCHITECTURE.md:164-175) requires subprocess text calls in the package and hooks to declare encoding='utf-8' and prose file reads to declare encoding, while scoping out the plugin's tests and recording the three existing breaches (plugins/arch-compliance/python/acf/diff.py:24-30, plugins/arch-compliance/python/acf/adr/citations.py:62-65, plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:49-56) with their grep recipe. None of the package or skill code added or modified by this design introduces an unencoded subprocess or file read call (plugins/arch-compliance/skills/acf-mandate/SKILL.md:99 and tests/test_self_host.py:33 both specify encoding='utf-8').

#### C44 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:24, config/architecture/ARCHITECTURE.md:99, plugins/arch-compliance/python/acf/exceptions.py:5, plugins/arch-compliance/python/acf/registry.py:33, plugins/arch-compliance/python/acf/registry.py:67, plugins/arch-compliance/skills/acf-mandate/SKILL.md:100, scripts/check_installed_skills.py:42`
- reasoning: Under ## Fail loud (config/architecture/ARCHITECTURE.md:24-41) and ## One base exception (config/architecture/ARCHITECTURE.md:99-103), AcfInputError subclasses AcfError alone (plugins/arch-compliance/python/acf/exceptions.py:5), MandateRegistry._unique_ids raises AcfInputError naming repeated ids (plugins/arch-compliance/python/acf/registry.py:33-41), missing_anchors returns the list of missing-anchor row ids (plugins/arch-compliance/python/acf/registry.py:67-70), the /acf-mandate snippet exits non-zero via sys.exit naming missing rows (plugins/arch-compliance/skills/acf-mandate/SKILL.md:99-101), scripts/check_installed_skills.py:38-45 returns non-zero (1 or 2) on bad args or differing/missing files, and no new code introduces a bare/broad except or a None default for missing data.

#### C45 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:130, plugins/arch-compliance/skills/acf-mandate/SKILL.md:88, plugins/arch-compliance/python/acf/registry.py:37, plugins/arch-compliance/tests/test_adr_skill_prose.py:36, plugins/arch-compliance/tests/test_adr_code_portability.py:11`
- reasoning: The doctrine's ## Prose names no host section (config/architecture/ARCHITECTURE.md:130-136) requires skill prose and runtime messages to name no host repository, path, or section. Both the updated /acf-mandate skill prose (plugins/arch-compliance/skills/acf-mandate/SKILL.md:88-112) and the new runtime error message in MandateRegistry._unique_ids (plugins/arch-compliance/python/acf/registry.py:37-40) contain only generic package/host terminology and name no specific host.

#### C46 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:138, plugins/arch-compliance/python/acf/adr/ledger.py:64, plugins/arch-compliance/python/acf/adr/ledger.py:132, plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:443`
- reasoning: The doctrine's ## Frozen ledger format section (config/architecture/ARCHITECTURE.md:138-144) records that LedgerRow and LedgerAmendment fields change only through a spec and a gate run and that a verification pass writes no ledger record (citing plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:443-452). plugins/arch-compliance/python/acf/adr/ledger.py:64-172 is untouched by this design.

#### C47 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:146, plugins/arch-compliance/python/acf/registry.py:67, plugins/arch-compliance/skills/acf-mandate/SKILL.md:95, plugins/arch-compliance/skills/acf-mandate/SKILL.md:99, plugins/arch-compliance/python/acf/cli_check_diff.py:25, plugins/arch-compliance/python/acf/detectors/python_pack.py:16, plugins/arch-compliance/python/acf/detectors/__init__.py:30`
- reasoning: The doctrine's ## Live consumers section (config/architecture/ARCHITECTURE.md:146-150) requires every export to have a live call site in the package, a hook, or a skill (not only tests). missing_anchors (plugins/arch-compliance/python/acf/registry.py:67-70) is called by the /acf-mandate validation snippet at plugins/arch-compliance/skills/acf-mandate/SKILL.md:99; KNOWN_DETECTORS (plugins/arch-compliance/python/acf/cli_check_diff.py:25) is consumed by cli_check_diff.py:70 and plugins/arch-compliance/skills/acf-mandate/SKILL.md:95; and the unused PYTHON_DETECTOR_IDS alias has been removed from plugins/arch-compliance/python/acf/detectors/python_pack.py:16-23 and plugins/arch-compliance/python/acf/detectors/__init__.py:30-35.

#### C48 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:203, docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:217, docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:560, docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:569, hm:GEMINI.md:129`
- reasoning: The doctrine's ## Scoped refactor section (config/architecture/ARCHITECTURE.md:203-207, quoting hm:GEMINI.md:129) requires removing non-contractual patterns in touched code paths without expanding scope to unrelated modules. The design cleans up the touched paths (docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:217-223: registry.py, python_pack.py, detectors/__init__.py, test_profile_drift.py, /acf-mandate SKILL.md, and the two fixtures) while recording breaches in unrelated modules (diff.py, citations.py, typescript_bridge.py, /acf-setup SKILL.md, /architecture-review SKILL.md) as filed follow-ups in §9 (docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:560-576).

### Unanchored findings


### Looked for but did not find

- All governing sections of config/architecture/ARCHITECTURE.md and docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md are explicitly named in the spec; unstated_mandates is therefore empty.
- ## Build artifacts (config/architecture/ARCHITECTURE.md:66-68, row ops.no-build-artifacts): checked spec §4.2, §5.2, and §5.4 — named in the spec and no generated dist/ or build/ paths are staged or committed.
- ## Fail-loud ratchet, ## Façade sinks, ## FSM transitions, ## React boundaries (config/architecture/ARCHITECTURE.md:70-85, 92-97): checked spec §5.2 and config/architecture/mandates.yml:40-51, 86-131 — explicitly addressed in §5.2 as unenforced rows with reasons.
- ## Soft fail-loud smells (config/architecture/ARCHITECTURE.md:87-90, row soft.fail-loud): checked spec §5.2 and config/architecture/mandates.yml:132-142 — preserved from the python-service profile and named in §5.2.
- ## High-frequency misses (config/architecture/ARCHITECTURE.md:209-220): checked all six bullets (completeness claims without recipes, defaults for declared values, host names in prose/runtime messages, stdlib mixins on exceptions, subprocess text calls without encoding, and checks re-implemented in tests/skills) against all files added or modified by this design — all six are addressed in the spec and satisfied on the branch.

## sweeper

### Claim verdicts

#### C49 — SURVIVED
- evidence: `docs/design/ADR_GATE_HOST_CONTRACT.md:239-270; plugins/arch-compliance/python/acf/adr/host.py:19-33; config/architecture/adr.yml:1-2; plugins/arch-compliance/skills/acf-setup/SKILL.md:90-118; config/architecture/mandates.yml:1-4; config/architecture/ARCHITECTURE.md:17-22; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:50; tests/test_self_host.py:22-42`
- reasoning: Self-hosting extends the two-key host contract, the /acf-setup bootstrap layout, and the registry-is-the-spine principle without introducing a parallel enforcement system.

#### C50 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:67-70; tests/test_self_host.py:34; plugins/arch-compliance/tests/test_profile_drift.py:27; plugins/arch-compliance/skills/acf-mandate/SKILL.md:99; plugins/arch-compliance/skills/acf-setup/SKILL.md:137; config/architecture/ARCHITECTURE.md:198-199; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:572-573`
- reasoning: MandateRegistry.missing_anchors(arch_text) is the single point of definition called by test_self_host.py, test_profile_drift.py, and acf-mandate/SKILL.md, while acf-setup/SKILL.md:137 is recorded as a current breach in the doctrine and filed in section 9 follow-up 4.

#### C51 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:25; tests/test_self_host.py:14,23; plugins/arch-compliance/tests/test_profile_drift.py:7,24; plugins/arch-compliance/skills/acf-mandate/SKILL.md:91,95; plugins/arch-compliance/python/acf/detectors/python_pack.py:16-22; plugins/arch-compliance/python/acf/detectors/__init__.py:28-35`
- reasoning: KNOWN_DETECTORS in acf.cli_check_diff:25 is the single exported detector union imported by test_self_host.py, test_profile_drift.py, and acf-mandate/SKILL.md, and no other file defines PYTHON_DETECTOR_IDS or re-computes the union.

#### C52 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:33-41,44-45; plugins/arch-compliance/tests/test_registry.py:40-47; tests/test_self_host.py:18-43; plugins/arch-compliance/skills/acf-setup/SKILL.md:110; config/architecture/ARCHITECTURE.md:198; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:570-571`
- reasoning: MandateRegistry._unique_ids enforces unique IDs at model construction, by_id is a dict builder, test_self_host.py adds no duplicate host-tier uniqueness test, and acf-setup/SKILL.md:110 is recorded in the doctrine and filed in section 9 follow-up 3.

#### C53 — SURVIVED
- evidence: `tests/test_self_host.py:37-42; plugins/arch-compliance/python/acf/registry.py:60-63; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:102,184; plugins/arch-compliance/skills/acf-mandate/SKILL.md:122`
- reasoning: MandateRegistry.unknown_detectors checks only enforced ast and guard rows because manual detector strings are free-text pointers across hosts, so resolving this repository's manual rows against plugins/arch-compliance/tests/ is a host-tier test in tests/test_self_host.py.

#### C54 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:12-21; tests/test_self_host.py:16,23,33; plugins/arch-compliance/skills/acf-mandate/SKILL.md:93,95,99; plugins/arch-compliance/tests/test_repo_paths.py:20-58; plugins/arch-compliance/skills/architecture-review/SKILL.md:62; config/architecture/ARCHITECTURE.md:113-116,197; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:574-575`
- reasoning: ARCH_REL and MANDATES_REL in acf.repo:12-21 are imported by test_self_host.py and acf-mandate/SKILL.md, while architecture-review/SKILL.md:62 is recorded in the doctrine and filed in section 9 follow-up 5.

#### C55 — SURVIVED
- evidence: `scripts/check_installed_skills.py:18-33; tests/test_check_installed_skills.py:23; hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:669-681`
- reasoning: scripts/check_installed_skills.py promotes the inline filecmp.cmp loop from PLAN_ADR_GATE_HM_CUTOVER.md:669-681 into a runnable script and exports GATE_SKILLS imported by tests/test_check_installed_skills.py:23.

#### C56 — SURVIVED
- evidence: `CLAUDE.md:20-23; config/architecture/ARCHITECTURE.md:177-186`
- reasoning: CLAUDE.md:20-23 carries the runnable command and points to ## Release discipline in config/architecture/ARCHITECTURE.md without restating the rationale prose.

#### C57 — SURVIVED
- evidence: `docs/design/ADR_GATE_HOST_CONTRACT.md:3-8,10-520; hm:docs/design/ADR_GATE_HOST_CONTRACT.md:3-513`
- reasoning: docs/design/ADR_GATE_HOST_CONTRACT.md carries the provenance block citing HM commit 86f93f95 and matches the HM source text verbatim.

#### C58 — SURVIVED
- evidence: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:235-256; docs/design/ADR_GATE_HOST_CONTRACT.md:1-8; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:1-55; hm:docs/design/ADVERSARIAL_DESIGN_REVIEW.md:1-19; hm:docs/design/ARCHITECTURE_COMPLIANCE_FRAMEWORK.md:1-17; hm:docs/design/ADR_EXTRACTION_TO_PLUGIN.md:1-16`
- reasoning: The 12 ADR/ACF specs in hm:docs/design/ match the disposition table: ADR_GATE_HOST_CONTRACT.md is copied with provenance, the 4 ACF specs are synthesized in ARCH_COMPLIANCE_FOR_SUPERPOWERS.md, and the remaining 7 HM-specific or superseded ADR specs stay in HM.

#### C59 — SURVIVED
- evidence: `hm:docs/reviews/adversarial_design_ledger.jsonl:176-179,209-218,337-339,344,346-349,390-391; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:239-252`
- reasoning: All 463 lines of hm:docs/reviews/adversarial_design_ledger.jsonl match the exact per-spec row counts in the section 5.3 table (4, 6, 7, 3, 0, 0, 4, and 0 for the 5 pre-extraction specs).

#### C60 — SURVIVED
- evidence: `config/architecture/mandates.yml:40-51,101-131; config/architecture/ARCHITECTURE.md:45-64,104-110; plugins/arch-compliance/profiles/python-service/mandates.yml:62-90; plugins/arch-compliance/profiles/react-app/mandates.yml:36-46`
- reasoning: boundary.no_sys_path_hack and hygiene.posix_paths_only are enforced ast/guard rows in config/architecture/mandates.yml while hygiene.forbidden_Legacy_Dir and hygiene.forbidden_Legacy_Import remain profile-only with rationale recorded in ARCHITECTURE.md.

#### C61 — SURVIVED
- evidence: `pyproject.toml:23; README.md:93-95; tests/test_self_host.py:1; tests/test_check_installed_skills.py:1`
- reasoning: pyproject.toml:23 configures testpaths for both plugins/arch-compliance/tests and root tests, README.md:93-95 documents the split, and both host-property test suites live in root tests/.

#### C62 — SURVIVED
- evidence: `hm:GEMINI.md:1-285; config/architecture/ARCHITECTURE.md:24-65,188-208; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:274-303`
- reasoning: Comparing hm:GEMINI.md §§0-13 against config/architecture/ARCHITECTURE.md confirms §§0,1,2,3,4,7,10 are adopted, §5 is N/A, §6 is folded into §1, §8.1 is a repo convention, and §§8.2-8.3,9,11,12,13 are HM-specific exclusions.

### Unanchored findings


### Looked for but did not find

- plugins/arch-compliance/python/acf/detectors/python_pack.py (any second definition of KNOWN_DETECTORS or PYTHON_DETECTOR_IDS)
- plugins/arch-compliance/python/acf/detectors/__init__.py (any second definition of KNOWN_DETECTORS or PYTHON_DETECTOR_IDS)
- plugins/arch-compliance/python/acf/cli_check_llm.py (any hardcoded host path literal bypassing acf.repo constants)
- plugins/arch-compliance/tests/ (any host-only self-hosting or install-parity test misplaced under the plugin test tree)
- plugins/arch-compliance/skills/ (any inline Python block outside acf-mandate, acf-setup, and architecture-review)
- hm:docs/design/ (any uncited ADR gate or ACF design spec omitted from the 12-spec disposition table)

### Relationships

- DISJOINT: `KNOWN_DETECTORS import in plugins/arch-compliance/skills/acf-mandate/SKILL.md:91 and tests/test_self_host.py:14` — responsibility `Enumerate all valid AST and guard detector IDs for mandate registry validation` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:25`
  - resolution: Both consume acf.cli_check_diff.KNOWN_DETECTORS directly; nothing to collapse
- DISJOINT: `MandateRegistry.missing_anchors call in plugins/arch-compliance/skills/acf-mandate/SKILL.md:99 and tests/test_self_host.py:34` — responsibility `Verify every mandate arch_anchor appears as a stripped heading line in ARCHITECTURE.md` — existing `plugins/arch-compliance/python/acf/registry.py:67`
  - resolution: Both consume acf.registry.missing_anchors directly; nothing to collapse
- DISJOINT: `ARCH_REL and MANDATES_REL imports in plugins/arch-compliance/skills/acf-mandate/SKILL.md:93 and tests/test_self_host.py:16` — responsibility `Provide canonical host-relative paths to config/architecture/mandates.yml and ARCHITECTURE.md` — existing `plugins/arch-compliance/python/acf/repo.py:12`
  - resolution: Both consume acf.repo path constants directly; nothing to collapse
- ADJACENT: `tests/test_self_host.py:37 (test_every_manual_row_names_an_existing_test_module)` — responsibility `Verify this repository's manual mandate detector pointers resolve to test files under plugins/arch-compliance/tests/` — existing `plugins/arch-compliance/python/acf/registry.py:60`
  - resolution: none
  - non-merge: load_mandates validates enforced ast and guard detector IDs against KNOWN_DETECTORS across all hosts, whereas manual detector strings are free-text pointers per ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:102,184; checking that this host's manual rows resolve to files under plugins/arch-compliance/tests/ is a host-tier invariant belonging in tests/test_self_host.py.
- ADJACENT: `scripts/check_installed_skills.py:18 (GATE_SKILLS, differing_files)` — responsibility `Compare repo gate skill directories byte-for-byte against an installed superpowers skills directory` — existing `C:/Users/iball/Arduino/Projects/HistoricMansions/docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:669-681`
  - resolution: none
  - non-merge: scripts/check_installed_skills.py is the reusable script; the HM block is a frozen executed plan record, and HM's live install instruction (hm:CLAUDE.md:17) is filed in section 10 to consume the script.

### Two-owner counts


### Document conflicts


## hardening

### Claim verdicts

#### C63 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:33-41, plugins/arch-compliance/python/acf/registry.py:43-45, plugins/arch-compliance/tests/test_registry.py:40-47`
- reasoning: Opened plugins/arch-compliance/python/acf/registry.py:33-45: MandateRegistry._unique_ids is a @model_validator(mode='after') that counts mandate ids and raises AcfInputError naming each repeated id before MandateRegistry.by_id (lines 43-45, a dict comprehension that would otherwise keep only the last row) can be accessed. Pinned at rung 1 by test_a_repeated_mandate_id_is_refused in plugins/arch-compliance/tests/test_registry.py:40-47.

#### C64 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:25, plugins/arch-compliance/python/acf/judge.py:16, plugins/arch-compliance/skills/acf-mandate/SKILL.md:91, plugins/arch-compliance/tests/test_profile_drift.py:7, tests/test_self_host.py:14`
- reasoning: Opened plugins/arch-compliance/python/acf/judge.py:16 which imports Mandate from acf.registry, confirming that importing acf.judge from acf.registry would create an import cycle. plugins/arch-compliance/python/acf/cli_check_diff.py:25 defines KNOWN_DETECTORS = ALL_PYTHON_DETECTOR_IDS | TS_DETECTOR_IDS | LLM_PROMPT_IDS and guards main() behind if __name__ == '__main__' at lines 195-196. Verified imports in plugins/arch-compliance/skills/acf-mandate/SKILL.md:91, plugins/arch-compliance/tests/test_profile_drift.py:7, and tests/test_self_host.py:14.

#### C65 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:90-118, config/architecture/mandates.yml:1-143, config/architecture/ARCHITECTURE.md:24-97, plugins/arch-compliance/profiles/python-service/mandates.yml:1-102, plugins/arch-compliance/profiles/react-app/mandates.yml:1-47`
- reasoning: Compared config/architecture/mandates.yml:1-143 and config/architecture/ARCHITECTURE.md:24-97 against plugins/arch-compliance/profiles/react-app/mandates.yml:1-47 and plugins/arch-compliance/profiles/python-service/mandates.yml:1-102: all nine stock headings are preserved verbatim, ops.no-build-artifacts is kept once (lines 27-38), and the three non-applicable rows (soft.react-boundaries at lines 40-51, facade.forbid-sink at lines 101-115, fsm.transition-guard at lines 117-130) remain in place with status: unenforced.

#### C66 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:26-34, plugins/arch-compliance/python/acf/enforcement.py:49-51, plugins/arch-compliance/tests/fixtures/python/bad_except.py:4, plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:4, plugins/arch-compliance/tests/test_python_pack.py:9-16, plugins/arch-compliance/tests/test_typescript_pack.py:32-41`
- reasoning: Verified that plugins/arch-compliance/tests/test_python_pack.py:9-16 calls scan_python_file directly on bad_except.py and plugins/arch-compliance/tests/test_typescript_pack.py:32-41 calls scan_typescript_file directly on bad.tsx, bypassing apply_registry (plugins/arch-compliance/python/acf/enforcement.py:49-51), which filters out findings whose source line satisfies token_exempted (lines 26-34).

#### C67 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:26-34, plugins/arch-compliance/python/acf/enforcement.py:50, plugins/arch-compliance/tests/fixtures/python/bad_except.py:4, plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:4, plugins/arch-compliance/detectors/typescript/src/scan.ts:93-99`
- reasoning: Opened plugins/arch-compliance/tests/fixtures/python/bad_except.py:4 ('# fail-loud.bare-except-ok: detector fixture; the pack must flag this line') and plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:4 ('// fail-loud.empty-catch-ok: detector fixture; the pack must flag this line'). Both match token_exempted in plugins/arch-compliance/python/acf/enforcement.py:26-34 and are dropped by apply_registry at line 50, while scanFile in plugins/arch-compliance/detectors/typescript/src/scan.ts:93-99 still counts all 3 raw findings in bad.tsx.

#### C68 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:125-148, plugins/arch-compliance/tests/fixtures/python/bad_except.py:4, plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:4-8`
- reasoning: Executed plugins/arch-compliance/hooks/posttooluse_gate.py --repo . --format hook read-only against both fixture paths: on bad_except.py (line 4 exempted) it emitted additionalContext with no findings and exited 0; on bad.tsx (line 4 exempted, lines 7-8 WARN) it emitted additionalContext with the two WARN findings and exited 0; lines 131-134 of posttooluse_gate.py return exit code 2 only when has_block is True.

#### C69 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:153-176, plugins/arch-compliance/hooks/constraints_template.md:1-21`
- reasoning: Opened plugins/arch-compliance/hooks/inject_constraints.py:153-176 and plugins/arch-compliance/hooks/constraints_template.md:1-21: _render_constraints substitutes only {{MANDATES}} (formatted from registry.mandates) and {{ARCHITECTURE_EXCERPT}} (first 4000 chars of config/architecture/ARCHITECTURE.md) into constraints_template.md, reading no review runs or ledger records.

#### C70 — SURVIVED
- evidence: `pyproject.toml:23-24, tests/test_self_host.py:13-30, config/architecture/adr.yml:1-2, plugins/arch-compliance/python/acf/adr/host.py:19-33`
- reasoning: Opened pyproject.toml:23-24 (testpaths = ['plugins/arch-compliance/tests', 'tests'], pythonpath = ['plugins/arch-compliance/python']), tests/test_self_host.py:13-30, config/architecture/adr.yml:1-2, and plugins/arch-compliance/python/acf/adr/host.py:19-33 (AdrHostConfig has extra='forbid' at line 22 and load_host_config validates ARCH_REL and ADR_REL).

#### C71 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_acf_mandate_skill.py:20-59, plugins/arch-compliance/skills/acf-mandate/SKILL.md:88-102, plugins/arch-compliance/profiles/python-service/mandates.yml:1-10`
- reasoning: Opened plugins/arch-compliance/tests/test_acf_mandate_skill.py:20-59: _snippet() extracts the bash python -c block under '## Validate' from plugins/arch-compliance/skills/acf-mandate/SKILL.md:88-102, _host() copies plugins/arch-compliance/profiles/python-service/mandates.yml:1-10 and ARCHITECTURE.md into a temp host, test_snippet_accepts_a_stock_profile_with_guard_rows asserts returncode == 0, and test_snippet_refuses_a_missing_anchor renames '## Fail loud' and asserts non-zero exit with 'fail-loud.bare-except' in output.

#### C72 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:88-102, plugins/arch-compliance/python/acf/cli_check_diff.py:25, plugins/arch-compliance/python/acf/detectors/__init__.py:11-18, plugins/arch-compliance/python/acf/detectors/__init__.py:28`
- reasoning: Opened plugins/arch-compliance/skills/acf-mandate/SKILL.md:88-102: the validation snippet imports KNOWN_DETECTORS from acf.cli_check_diff (which unions ALL_PYTHON_DETECTOR_IDS = PYTHON_AST_DETECTOR_IDS | GUARD_DETECTOR_IDS from plugins/arch-compliance/python/acf/detectors/__init__.py:11-28, including BUILD_ARTIFACT_DETECTOR_ID = 'no_build_artifacts'), prints each mandate row, and calls sys.exit naming missing_anchors(reg, ARCH_REL.read_text(encoding='utf-8')).

#### C73 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:33-41, plugins/arch-compliance/python/acf/registry.py:67-70, plugins/arch-compliance/python/acf/cli_check_diff.py:70-74, plugins/arch-compliance/python/acf/cli_check_llm.py:42, plugins/arch-compliance/hooks/posttooluse_gate.py:107-110, plugins/arch-compliance/hooks/inject_constraints.py:104-107, plugins/arch-compliance/tests/test_registry.py:40-57`
- reasoning: Grepped all callers of load_mandates and inspected each: cli_check_diff.py:70-74, posttooluse_gate.py:107-110, and inject_constraints.py:104-107 catch AcfInputError, print to stderr, and return 1; cli_check_llm.py:42 lets AcfInputError propagate uncaught (non-zero exit). Opened plugins/arch-compliance/tests/test_registry.py:40-57 confirming test_a_repeated_mandate_id_is_refused and test_missing_anchors_names_rows_whose_anchor_is_absent (with inline backtick '`## Gone`' on line 56).

#### C74 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:56-64, plugins/arch-compliance/python/acf/cli_check_diff.py:112-183, plugins/arch-compliance/hooks/posttooluse_gate.py:229-295, plugins/arch-compliance/hooks/inject_constraints.py:104-113`
- reasoning: Opened plugins/arch-compliance/python/acf/registry.py:60 (checks m.detector not in known_detectors only when m.detection in {'ast', 'guard'}), cli_check_diff.py:112-183, posttooluse_gate.py:229-295, and inject_constraints.py:104-113; also executed cli_check_diff and posttooluse_gate.py against the branch's config/architecture/mandates.yml (which has six detection: manual rows), confirming zero errors and zero findings for manual rows.

#### C75 — SURVIVED
- evidence: `.github/workflows/ci.yml:13-15, .github/workflows/ci.yml:39-40, plugins/arch-compliance/python/acf/cli_check_diff.py:65-67, plugins/arch-compliance/python/acf/cli_check_diff.py:89-91, plugins/arch-compliance/python/acf/diff.py:42-45`
- reasoning: Opened .github/workflows/ci.yml:13-15 (fetch-depth: 0) and lines 39-40 (runs python -m acf.cli_check_diff --repo . --base "origin/${{ github.base_ref || 'main' }}" after pytest). In cli_check_diff.py:65-67 mandates_path defaults to repo / MANDATES_REL and lines 89-91 return 1 on any BLOCK finding; in diff.py:42-45 _diff_args returns [f'{base}...HEAD'], which is empty when HEAD is origin/main.

#### C76 — SURVIVED
- evidence: `scripts/check_installed_skills.py:18-47, tests/test_check_installed_skills.py:22-60, C:/Users/iball/Arduino/Projects/HistoricMansions/docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:669-681`
- reasoning: Opened scripts/check_installed_skills.py:18-47 (defines GATE_SKILLS, compares every file via filecmp.cmp(f, g, shallow=False), prints 'installed gate skills identical to the clone' and returns 0 or prints differing/missing paths and returns 1) and tests/test_check_installed_skills.py:22-60 (imports GATE_SKILLS via _load_script().GATE_SKILLS at line 23 and tests identical trees, a changed byte, and a missing installed file).

#### C77 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:1-22, config/architecture/adr.yml:1-2, plugins/arch-compliance/python/acf/adr/host.py:28-33, docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:476-487`
- reasoning: Opened plugins/arch-compliance/python/acf/adr/host.py:28-33: load_host_config requires config/architecture/ARCHITECTURE.md and config/architecture/adr.yml in the host repository root, neither of which existed at c0281bf before this branch created them.

#### C78 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:24-30, .github/workflows/ci.yml:11, CLAUDE.md:33-37, config/architecture/ARCHITECTURE.md:164-175`
- reasoning: Opened plugins/arch-compliance/python/acf/diff.py:24-30 (subprocess.run with text=True and no encoding), .github/workflows/ci.yml:11 (runs-on: ubuntu-latest), CLAUDE.md:33-37 (documents PYTHONUTF8=1 for Windows diff gate runs), and config/architecture/ARCHITECTURE.md:164-175 (records the three subprocess calls and follow-up 1).

#### C79 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:28-91, docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:385-394, docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:532-534`
- reasoning: Executed python -m acf.cli_check_diff --repo . --base origin/main (printed 'No findings.' and exited 0) and python -m acf.cli_check_diff --repo . --base dfff93f5 (printed the exact five WARN findings at bad.tsx:7, bad.tsx:8, test_adr_exceptions.py:22, test_adr_import_graph.py:46, and test_adr_skill_prose.py:53, and exited 0) with PYTHONUTF8=1 and PYTHONPATH=plugins/arch-compliance/python.

#### C80 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:33-41, plugins/arch-compliance/python/acf/registry.py:67-70, tests/test_self_host.py:22-35, config/architecture/mandates.yml:5-212, config/architecture/ARCHITECTURE.md:24-145`
- reasoning: Opened tests/test_self_host.py:22-35: test_declaration_names_the_reviews_tree calls load_host_config(ROOT) (which fails via require_file if config/architecture/adr.yml is absent), and test_every_anchor_is_in_the_doctrine loads config/architecture/mandates.yml (which runs MandateRegistry._unique_ids at registry.py:33-41) and asserts missing_anchors(_registry(), doctrine) == [] (registry.py:67-70, comparing stripped full lines across all 14 unique arch_anchor headings in config/architecture/mandates.yml:5-212).

#### C81 — SURVIVED
- evidence: `docs/plans/PLAN_PLUGIN_SELF_HOSTING.md:78, plugins/arch-compliance/skills/acf-setup/SKILL.md:53-63, plugins/arch-compliance/skills/acf-setup/SKILL.md:109-116, config/architecture/mandates.yml:27-38, config/architecture/ARCHITECTURE.md:24-97`
- reasoning: Opened plugins/arch-compliance/skills/acf-setup/SKILL.md:53-63 and 109-116, docs/plans/PLAN_PLUGIN_SELF_HOSTING.md:78, config/architecture/mandates.yml:27-38 (single ops.no-build-artifacts row with languages: both), and config/architecture/ARCHITECTURE.md:24-97 (all nine stock anchors present verbatim).

#### C82 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:102-104, config/architecture/mandates.yml:144-212, config/architecture/ARCHITECTURE.md:99-207`
- reasoning: Opened docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:102-104 (defining detector as 'Detector fn / guard module / LLM prompt id / manual verification pointer' and call_sites including 'audit'), config/architecture/mandates.yml:144-212 (six detection: manual rows with call_sites: [audit]), and config/architecture/ARCHITECTURE.md:99-207 (five sections naming those six rows and six sections ending with 'No row: no test enforces this yet.').

#### C83 — SURVIVED
- evidence: `config/architecture/mandates.yml:148-212, plugins/arch-compliance/tests/test_adr_exceptions.py:35-45, plugins/arch-compliance/tests/test_repo_paths.py:53-78, plugins/arch-compliance/tests/test_adr_host.py:37-67, plugins/arch-compliance/tests/test_adr_code_portability.py:11-25, plugins/arch-compliance/tests/test_adr_skill_prose.py:36-41, plugins/arch-compliance/tests/test_adr_ledger.py:580-596`
- reasoning: Opened config/architecture/mandates.yml:148-212 and all six referenced test files under plugins/arch-compliance/tests/, confirming each file exists and enforces the rule named by its manual row.

### Unanchored findings


### Looked for but did not find

- Traced MandateRegistry._unique_ids (plugins/arch-compliance/python/acf/registry.py:33-41) and its four runtime callers (cli_check_diff.py:70, cli_check_llm.py:42, posttooluse_gate.py:107, inject_constraints.py:104): none swallow AcfInputError or silently deduplicate repeated ids.
- Traced missing_anchors (plugins/arch-compliance/python/acf/registry.py:67-70) and its callers (plugins/arch-compliance/skills/acf-mandate/SKILL.md:99-101, plugins/arch-compliance/tests/test_profile_drift.py:27, tests/test_self_host.py:34): compares stripped full lines rather than substrings and refuses rather than repairing.
- Traced scripts/check_installed_skills.py:22-47: compares every file under GATE_SKILLS with filecmp.cmp(..., shallow=False) and exits 1 on mismatch without silently copying or repairing.
- Traced tests/test_self_host.py:37-42 (test_every_manual_row_names_an_existing_test_module): verifies manual row detector paths exist under plugins/arch-compliance/tests/ and fails loud in pytest.
- Executed python -m acf.cli_check_diff (--base origin/main and --base dfff93f5) and plugins/arch-compliance/hooks/posttooluse_gate.py against bad_except.py and bad.tsx to verify no unexercised guard deferral or hidden BLOCK finding remains.

### Mechanism traces

- **MandateRegistry._unique_ids**
  - invalid state: any(n > 1 for n in Counter(m.id for m in registry.mandates).values())
  - producer: `plugins/arch-compliance/skills/acf-setup/SKILL.md:109-112`
  - rung 1 (highest applicable 1); repairs=False
  - hardening rejected because: Hardened at rung 1 on MandateRegistry itself; rewriting the /acf-setup skill prose parenthetical at plugins/arch-compliance/skills/acf-setup/SKILL.md:110 is deferred to section 9 follow-up 4 under Scoped refactor (docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:105-106,569-576).
  - spec citation: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:402-410`
- **missing_anchors**
  - invalid state: any(m.arch_anchor.strip() not in {line.strip() for line in doctrine_text.splitlines()} for m in registry.mandates)
  - producer: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:67`
  - rung 2 (highest applicable 2); repairs=False
  - hardening rejected because: mandates.yml and ARCHITECTURE.md are separate files and posttooluse_gate.py:107 loads mandates.yml without reading ARCHITECTURE.md; the check is collapsed into one function in acf.registry and wired into the /acf-mandate validation step (plugins/arch-compliance/skills/acf-mandate/SKILL.md:99-101), while updating the /acf-setup by-eye instruction (plugins/arch-compliance/skills/acf-setup/SKILL.md:137) is filed as section 9 follow-up 4 (docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:105-106,569-576).
  - spec citation: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:411-418`
- **scripts/check_installed_skills.py**
  - invalid state: any(not (install_path / 'skills' / s / f.relative_to(clone / 'plugins/arch-compliance/skills' / s)).is_file() or not filecmp.cmp(f, install_path / 'skills' / s / f.relative_to(clone / 'plugins/arch-compliance/skills' / s), shallow=False) for s in GATE_SKILLS for f in (clone / 'plugins/arch-compliance/skills' / s).rglob('*') if f.is_file())
  - producer: `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:1`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: The installed plugin cache directory is populated externally by the Claude Code CLI on plugin install rather than by this repository's runtime code (docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:364-365,550).
  - spec citation: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:350-360`
- **tests/test_self_host.py::test_every_manual_row_names_an_existing_test_module**
  - invalid state: any(not (ROOT / m.detector).is_file() or not m.detector.startswith('plugins/arch-compliance/tests/') for m in registry.mandates if m.detection == 'manual')
  - producer: `config/architecture/mandates.yml:148-212`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: The registry contract leaves a detection: manual row's detector string as a free-text manual verification pointer for other hosts (docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:102,184; plugins/arch-compliance/skills/acf-mandate/SKILL.md:122); requiring a test file path in MandateRegistry would bind every host to this repository's convention (docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:99-100,443-449).
  - spec citation: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:440-449`

## Claims

- **C1** [premise] [load-bearing] (carried): At plugin main c0281bf (before this design) config/architecture/ is absent, .acf/ is gitignored (.gitignore:8), the root documents are README.md and SECURITY.md, and there is no CLAUDE.md. Verify at c0281bf (git ls-tree / git show), not at the branch head, where these files now exist.
  - spec citation: `.gitignore:8`
- **C2** [premise] (carried): At c0281bf docs/design/ holds docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md and this spec (docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md), and docs/reviews/ is absent.
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md`
- **C3** [premise] [load-bearing] (carried): The gate's host contract reads two declared values (runs_dir, ledger_path) plus the doctrine path (plugins/arch-compliance/python/acf/adr/host.py:19-33); the compliance reviewer prompt reads the doctrine and each document it points to (plugins/arch-compliance/skills/adversarial-design-review/reviewers/compliance.md:12) and checks a doctrine's self-declared high-frequency misses first (plugins/arch-compliance/skills/adversarial-design-review/reviewers/compliance.md:47).
  - spec citation: `plugins/arch-compliance/python/acf/adr/host.py:19-33`
- **C4** [premise] [load-bearing] (carried): The /acf-setup merge rule for a two-language host does not resolve a repeated mandate id: it reads 'Keep every mandate id unique. If the same id appears in both (should not for stock profiles), stop and ask; never silently drop a row.' (plugins/arch-compliance/skills/acf-setup/SKILL.md:110). Both stock profiles carry ops.no-build-artifacts with identical bodies (plugins/arch-compliance/profiles/python-service/mandates.yml:34, plugins/arch-compliance/profiles/react-app/mandates.yml:23), so the parenthetical is false and a polyglot bootstrap reaches the stop-and-ask.
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:110`
- **C5** [premise] [load-bearing] (carried): /acf-setup writes config/architecture/mandates.yml and config/architecture/ARCHITECTURE.md from a profile and, for a two-language host, merges both profiles into one pair (plugins/arch-compliance/skills/acf-setup/SKILL.md:90-118); it also writes .acf/enabled (README.md:20).
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:90-118`
- **C6** [premise] [load-bearing] (carried): The merged host registry, run over this repository's history (--base dfff93f5, the root commit) against the code at c0281bf, reports seven findings: two BLOCK (plugins/arch-compliance/tests/fixtures/python/bad_except.py:4 fail-loud.bare-except; plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:4 fail-loud.empty-catch) and five WARN (plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:7 and :8 no-shims.explicit-any; no-shims.hasattr at plugins/arch-compliance/tests/test_adr_exceptions.py:22, plugins/arch-compliance/tests/test_adr_import_graph.py:46, plugins/arch-compliance/tests/test_adr_skill_prose.py:53).
  - spec citation: `plugins/arch-compliance/tests/fixtures/python/bad_except.py:4`
- **C7** [premise] [load-bearing] (carried): The registry schema accepts detection: manual rows and requires a detector string on every row, but checks that string against known detectors only for ast and guard rows (plugins/arch-compliance/python/acf/registry.py:9,19,56), so a manual row may carry a free-text detector such as a test-module path.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:9,19,56`
- **C8** [root_cause] [load-bearing] (carried): Root cause of the silent-shadow defect: at c0281bf load_mandates accepts two rows with the same id without refusing, and MandateRegistry.by_id builds a dict over the rows and keeps the last of the two (git show c0281bf:plugins/arch-compliance/python/acf/registry.py, lines 33-34), so a host whose registry repeats an id has one row silently shadowed.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py`
- **C9** [root_cause] [load-bearing] (carried): Root cause of the /acf-mandate validation failure: at c0281bf the skill's validation snippet builds its known-detector union from PYTHON_DETECTOR_IDS (with TS_DETECTOR_IDS and LLM_PROMPT_IDS), and PYTHON_DETECTOR_IDS equals PYTHON_AST_DETECTOR_IDS only (git show c0281bf:plugins/arch-compliance/python/acf/detectors/python_pack.py, line 25), excluding guard ids; therefore the snippet raises UnknownDetectorError on a stock profile's enforced guard row ops.no-build-artifacts.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/python_pack.py`
- **C10** [premise] (delta): At c0281bf the /acf-mandate skill asks the agent to check anchors by eye (line 104: 'Also verify each arch_anchor is a substring of config/architecture/ARCHITECTURE.md'), and two other skill lines carry the same class of breach: plugins/arch-compliance/skills/architecture-review/SKILL.md:62 spells Path('config/architecture/mandates.yml') instead of acf.repo.MANDATES_REL, and plugins/arch-compliance/skills/acf-setup/SKILL.md:137 instructs a by-eye anchor check.
  - spec citation: `plugins/arch-compliance/skills/architecture-review/SKILL.md:62`
- **C11** [premise] [load-bearing] (delta): At c0281bf the detector-id union is spelled in plugins/arch-compliance/python/acf/cli_check_diff.py:25 and in plugins/arch-compliance/tests/test_profile_drift.py, the anchor check is a loop inside plugins/arch-compliance/tests/test_profile_drift.py, and the package has no anchor-check function (git grep -n 'arch_anchor' c0281bf -- plugins/arch-compliance/python matches only plugins/arch-compliance/python/acf/registry.py:23 and plugins/arch-compliance/python/acf/judge.py:154).
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:25`
- **C12** [premise] (carried): Three subprocess calls in the package decode their output with the locale codec (text=True, no encoding): plugins/arch-compliance/python/acf/diff.py:24-30, plugins/arch-compliance/python/acf/adr/citations.py:62-65 and plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:49-56. CI runs on Linux (.github/workflows/ci.yml:11).
  - spec citation: `plugins/arch-compliance/python/acf/diff.py:24-30`
- **C13** [premise] [load-bearing] (carried): Deferral: the text-decoding defect and two git runners can stay a filed follow-up (section 3, section 9 follow-up 1) because CI runs on Linux (.github/workflows/ci.yml:11) and on Windows the diff gate is run with PYTHONUTF8=1 (recorded in CLAUDE.md).
  - spec citation: `.github/workflows/ci.yml:11`
- **C14** [premise] (carried): At c0281bf CI (.github/workflows/ci.yml) runs pytest and the TypeScript self-test, and does not run the diff gate on this repository's own changes.
  - spec citation: `.github/workflows/ci.yml`
- **C15** [premise] (carried): The plugin's acceptance test for a non-origin host builds a fixture host in a temporary directory and exercises the storage path through the Python API (plugins/arch-compliance/tests/test_adr_host_acceptance.py:74).
  - spec citation: `plugins/arch-compliance/tests/test_adr_host_acceptance.py:74`
- **C16** [premise] (carried): HM's workstream E exit criterion 5 names Cayenne as the second repository (hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:5405-5406) and says 'Item 5 is the one that proves the objective rather than approximating it' (hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:5410), at HM 22eae4f9.
  - spec citation: `hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:5405-5406`
- **C17** [premise] [load-bearing] (delta): The plugin's hooks run on each subagent start and each Write/Edit/MultiEdit (plugins/arch-compliance/hooks/hooks.json) and no-op without .acf/enabled (plugins/arch-compliance/hooks/posttooluse_gate.py:72-81, plugins/arch-compliance/hooks/inject_constraints.py:71-80). With the marker: SubagentStart injects the registry's rows and a doctrine excerpt (plugins/arch-compliance/hooks/inject_constraints.py:153); PostToolUse runs the build-artifact path guard (plugins/arch-compliance/hooks/posttooluse_gate.py:284-294) and scans the whole edited .py, .ts or .tsx file (added_lines=None at plugins/arch-compliance/hooks/posttooluse_gate.py:254,281), and on a BLOCK finding exits 2 (plugins/arch-compliance/hooks/posttooluse_gate.py:131-134).
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:72-81`
- **C18** [premise] (carried): At c0281bf, 404 tests are collected from the single testpaths entry plugins/arch-compliance/tests (pyproject.toml), and the plugin version is 0.2.0.
  - spec citation: `pyproject.toml`
- **C19** [premise] [load-bearing] (carried): Sequencing start condition (section 5.7 step 1) is met: HM merged 1d on 2026-10-23 as 812f9c2b; the plugin is installed on this node at user scope from the clone, version 0.2.0, and its two gate skills are byte-identical to the clone (scripts/check_installed_skills.py against C:/Users/iball/.claude/plugins/cache/arch-compliance-for-superpowers/arch-compliance/0.2.0).
  - spec citation: `scripts/check_installed_skills.py`
- **C20** [premise] [load-bearing] (carried): Deferral: MandateRegistry's new repeated-id refusal does not reach HM. HM's hm:config/architecture/mandates.yml at 22eae4f9 is in HM's own schema (rows carry gemini_anchor and no languages or arch_anchor), so it does not load through load_mandates at all; and HM's tracked files name acf.registry, acf.cli_check_diff and acf-check-diff only in docs/design/ and docs/reviews/ prose.
  - spec citation: `hm:config/architecture/mandates.yml`
- **C21** [premise] [load-bearing] (carried): Deferral (non-goal, section 3): no ledger migration is needed. HM's ledger records for plugin-related specs stay in HM matched to their HM spec paths; nothing in the plugin package opens a ledger row's spec_path as a file or requires it to resolve in the repository that holds the ledger.
  - spec citation: `hm:docs/design/ADR_GATE_HOST_CONTRACT.md:80-81`
- **C22** [premise] [load-bearing] (carried): The gate's citation resolver has no notion of another repository: a prefixed path such as hm:x classifies as unresolved (resolve_citation, plugins/arch-compliance/python/acf/adr/citations.py:129), and an unresolved citation is a hard fail before dispatch (plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:76-82,101). HM's host-contract runs handled their acf: citations by mapping each prefixed path to the sibling checkout (hm:docs/reviews/adr_runs/ADR_GATE_HOST_CONTRACT_v3_2026-10-12.md:28,35,247).
  - spec citation: `plugins/arch-compliance/python/acf/adr/citations.py:129`
- **C23** [premise] (delta): Section 0 states that unprefixed citations use repository-relative paths and hm: citations use HM-relative paths without '...' ellipses or bare ':line' continuations, because the resolver's suffix match works on whole path components (plugins/arch-compliance/python/acf/adr/citations.py:32-44).
  - spec citation: `plugins/arch-compliance/python/acf/adr/citations.py:32-44`
- **C24** [premise] (carried): The HM host-contract spec's decision 6 reads 'This spec stays in this repository until 1d, and moves to the plugin repository after 1d's acceptance run.' (hm:docs/design/ADR_GATE_HOST_CONTRACT.md:80-81 at 22eae4f9).
  - spec citation: `hm:docs/design/ADR_GATE_HOST_CONTRACT.md:80-81`
- **C25** [premise] (carried): The eight HM rules the doctrine lifts exist with the quoted text at hm:GEMINI.md (HM 22eae4f9): bare except at :103, 'No defaulting to None' at :104, hasattr probing as shims at :105, temporary bridge code at :111, scoped refactor at :129, single point of definition at :136, POSIX format for persisted paths at :189, and 'Path.as_posix() alone is not sufficient' at :191.
  - spec citation: `hm:GEMINI.md:103`
- **C26** [premise] (carried): Deferral (decision 4): hm:GEMINI.md:61 says to 'append the superseding ledger amendment', which conflicts with the plugin's verification-pass rule; it is corrected by the later housekeeping spec, not here.
  - spec citation: `hm:GEMINI.md:61`
- **C27** [premise] [load-bearing] (delta): Deferral (non-goal, section 3): the registry contract leaves a detection: manual row's detector string free text, so the loader must not validate it. docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:102,184 defines detector to include manual verification pointers and scopes unknown-detector errors to enforced ast and guard rows, and plugins/arch-compliance/skills/acf-mandate/SKILL.md:122 tells a manual row's author to 'Document how humans or external tools satisfy the mandate'.
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:102,184`
- **C28** [deletion] [load-bearing] (delta): What the design removes: test_profile_drift.py's own detector-union spelling and its anchor loop, the /acf-mandate snippet's narrower PYTHON_DETECTOR_IDS-based union and its by-eye anchor sentence, the unused PYTHON_DETECTOR_IDS alias in plugins/arch-compliance/python/acf/detectors/python_pack.py and plugins/arch-compliance/python/acf/detectors/__init__.py, the duplicate SKILLS tuple in tests/test_check_installed_skills.py, and MandateRegistry's silent last-wins on a repeated id; each is complete on the branch head and safe (nothing still reads what was removed).
  - spec citation: `plugins/arch-compliance/tests/test_profile_drift.py`
- **C29** [premise] [load-bearing] (delta): Deferral (section 3, section 9 follow-up 4): the skill-prose breaches in plugins/arch-compliance/skills/acf-setup/SKILL.md:110,137 and plugins/arch-compliance/skills/architecture-review/SKILL.md:62 are left unchanged in this phase and recorded in the doctrine; this phase's bootstrap and checks do not depend on those prose lines being rewritten first.
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:110`
- **C30** [premise] [load-bearing] (carried): Non-goal held: the design makes no change to the persisted ledger format, LedgerRow, LedgerAmendment or TouchedSurface vocabulary, no change to any detector's scanning logic, and no change to the gate skills' prose (adversarial-design-review and responding-to-adversarial-review).
  - spec citation: `plugins/arch-compliance/python/acf/adr/ledger.py`
- **C31** [premise] (carried): Deferrals to existing HM roadmap rows: the hook quiet flag (--quiet-disabled in plugins/arch-compliance/hooks/hooks.json) was already filed by 1d (hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:213), and the 1a roadmap row already describes 'one git runner' (hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:5122).
  - spec citation: `hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:213`
- **C32** [premise] (carried): HM's live install instruction is hm:CLAUDE.md:17 and HM's CLAUDE.md has the pointer-and-process form at hm:CLAUDE.md:21-35; the 1d plan's inline byte-check block is hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:669-681 and is an executed plan record.
  - spec citation: `hm:CLAUDE.md:17`
- **C33** [mandate] [load-bearing] (delta): Registry is the spine (docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:50): the plugin's own rules become config/architecture/mandates.yml rows with anchors; each doctrine section whose rule an existing test enforces (five sections, six manual rows) has detection: manual row(s) whose detector names that test module, and the doctrine section names the row id(s), not the test path; every row's arch_anchor is a stripped line of config/architecture/ARCHITECTURE.md; tests/test_self_host.py pins the anchors and the manual detectors.
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:50`
- **C34** [mandate] (carried): Declared, never defaulted (doctrine section; 1c decision 4): config/architecture/adr.yml declares both storage values and no default stands in for a missing declaration in acf.adr.host; the doctrine section states its scope and names the two package defaults outside it (plugins/arch-compliance/python/acf/repo.py:23-26, plugins/arch-compliance/python/acf/repo.py:32-44).
  - spec citation: `plugins/arch-compliance/python/acf/adr/host.py:19-33`
- **C35** [mandate] (delta): POSIX paths (doctrine section; lifted hm:GEMINI.md:189,191): config/architecture/adr.yml carries relative forward-slash paths, the model types them PosixStr which refuses a backslash rather than normalizing it (plugins/arch-compliance/python/acf/adr/contract.py:129), and the doctrine records that the plugin refuses rather than normalizes.
  - spec citation: `plugins/arch-compliance/python/acf/adr/contract.py:129`
- **C36** [mandate] [load-bearing] (carried): No shims / one rules document (principle 2, docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51): CLAUDE.md is a pointer and process file, not a second doctrine; it carries the byte-check command and points to the doctrine's ## Release discipline rather than restating the rule; and config/architecture/ARCHITECTURE.md points to the design document's five governing principles rather than restating them.
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51`
- **C37** [mandate] [load-bearing] (carried): The Superpowers override contract (principle 5, 'document that explicitly') is met by CLAUDE.md recording spec and plan locations, the gate as brainstorming's terminal state with BLOCKED returning through arch-compliance:responding-to-adversarial-review and re-run scope following the gate skill's revision class, the pre-gate byte-check command, the citation convention, and the PYTHONUTF8 Windows note.
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51`
- **C38** [mandate] (delta): The doctrine's ## No completeness claims rule (a factual claim about the tree is not load-bearing on a universal quantifier unless a re-runnable recipe backs it; source plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:152) is applied to this spec itself: its census lists per-item results with appendix commands (including item 15's git grep recipe), its definition of done is per-item checks, and section 0 contains no unbacked universal quantifier.
  - spec citation: `plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:152`
- **C39** [mandate] [load-bearing] (delta): Single point of definition (lifted hm:GEMINI.md:136): after this design the anchor-in-doctrine check has one implementation (acf.registry.missing_anchors), the detector-id union one definition (acf.cli_check_diff.KNOWN_DETECTORS), mandate-id uniqueness one owner (MandateRegistry._unique_ids), GATE_SKILLS one owner (scripts/check_installed_skills.py), and host paths one package owner (acf.repo); the drift test, the host test and the /acf-mandate snippet consume them. The two git runners (plugins/arch-compliance/python/acf/diff.py:17, plugins/arch-compliance/python/acf/adr/citations.py:54) and the two remaining skill-prose breaches (plugins/arch-compliance/skills/architecture-review/SKILL.md:62 and plugins/arch-compliance/skills/acf-setup/SKILL.md:137) are explicitly recorded as current breaches in config/architecture/ARCHITECTURE.md and filed in section 9 follow-ups 1 and 4.
  - spec citation: `hm:GEMINI.md:136`
- **C40** [mandate] (delta): One owner for host paths (doctrine section; plugins/arch-compliance/python/acf/repo.py:1-6): acf.repo is the one declaration of where ACF looks in a host and imports the standard library alone; the root tests/ and scripts/ this design adds import the acf.repo constants; the doctrine states that the row's test scans plugins/arch-compliance/python/ and plugins/arch-compliance/hooks/, that the root trees are checked by review, and records plugins/arch-compliance/skills/architecture-review/SKILL.md:62 as a current skill-prose breach.
  - spec citation: `plugins/arch-compliance/python/acf/repo.py:1-6`
- **C41** [mandate] (carried): Doctrine scope: config/architecture/ARCHITECTURE.md's opening paragraph states the population it governs (the package, the hooks, the skill prose, the TypeScript bridge, the plugin's tests and fixtures, and the repository-level tests/, scripts/ and config/), and states that the CI diff gate and the PostToolUse hook run the registry's detectors on changed .py, .ts and .tsx files anywhere in the repository while prose and configuration are held to the doctrine by review.
  - spec citation: `config/architecture/ARCHITECTURE.md`
- **C42** [mandate] (carried): Release discipline (doctrine section): this design changes a skill's prose (/acf-mandate SKILL.md), so the version is bumped to 0.2.1 in both pyproject.toml and plugins/arch-compliance/.claude-plugin/plugin.json; the doctrine section states that the byte check covers the two gate skills only and not the installed copy's hooks and package code, which the hooks run (plugins/arch-compliance/hooks/posttooluse_gate.py:22-26).
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:22-26`
- **C43** [mandate] (carried): Declared text decoding (doctrine section): the code this design adds or changes in the package and hooks introduces no subprocess text call without encoding='utf-8'; the doctrine records the three existing breaches with their recipe and states that the plugin's tests are outside the section's scope.
  - spec citation: `config/architecture/ARCHITECTURE.md`
- **C44** [mandate] (delta): Fail loud and One base exception: MandateRegistry._unique_ids raises AcfInputError (an AcfError subclass with no stdlib mixin) naming each repeated id (plugins/arch-compliance/python/acf/registry.py:33-41); missing_anchors returns rather than defaults; the /acf-mandate snippet exits non-zero naming the rows with a missing anchor; scripts/check_installed_skills.py exits non-zero on any differing or missing file; no new code adds a bare or broad except or a None default for a missing value.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:33-41`
- **C45** [mandate] (delta): Prose names no host (doctrine section; rows plugin.adr-code-names-no-host and plugin.gate-prose-names-no-host): the skill prose this design changes (/acf-mandate SKILL.md) and any runtime message it adds (MandateRegistry._unique_ids) name no host repository, path or section.
  - spec citation: `plugins/arch-compliance/tests/test_adr_skill_prose.py`
- **C46** [mandate] (carried): Frozen ledger format (doctrine section; plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:443-452): the design changes no LedgerRow or LedgerAmendment field, and the doctrine section records that a verification pass writes no ledger record.
  - spec citation: `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:443-452`
- **C47** [mandate] [load-bearing] (delta): Live consumers (doctrine section: an export has a live call site in the package, a hook or a skill; a test is not a consumer): missing_anchors has a live consumer outside the tests (the /acf-mandate validation snippet), KNOWN_DETECTORS has live consumers (the diff CLI and the snippet), and the unused alias PYTHON_DETECTOR_IDS is deleted from python_pack.py and detectors/__init__.py.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:67-70`
- **C48** [mandate] (delta): Scoped refactor (lifted hm:GEMINI.md:129): the design removes non-contractual patterns in the code paths it changes (registry loader, drift test, /acf-mandate snippet, python_pack.py/detectors/__init__.py, two fixtures) and records unrelated modules' breaches (the git runners, the decoding calls, and the /acf-setup and /architecture-review skill snippets) as filed follow-ups.
  - spec citation: `hm:GEMINI.md:129`
- **C49** [shape_fit] [load-bearing] (carried): The design extends existing shape: the host contract as designed (one declaration file config/architecture/adr.yml and the fixed doctrine path; docs/design/ADR_GATE_HOST_CONTRACT.md section 5), the /acf-setup bootstrap, and the registry-is-the-spine principle (docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:50).
  - spec citation: `docs/design/ADR_GATE_HOST_CONTRACT.md`
- **C50** [shape_fit] [load-bearing] (delta): Anchor-in-doctrine check: tests/test_self_host.py's anchor test, plugins/arch-compliance/tests/test_profile_drift.py, and the /acf-mandate snippet all consume acf.registry.missing_anchors (plugins/arch-compliance/python/acf/registry.py:67-70); plugins/arch-compliance/skills/acf-setup/SKILL.md:137's by-eye instruction is recorded as a current breach in the doctrine and filed in section 9 follow-up 4.
  - spec citation: `plugins/arch-compliance/tests/test_profile_drift.py`
- **C51** [shape_fit] [load-bearing] (delta): Detector-id union: tests/test_self_host.py, test_profile_drift.py and the /acf-mandate snippet all import KNOWN_DETECTORS from acf.cli_check_diff (plugins/arch-compliance/python/acf/cli_check_diff.py:25), and the unused PYTHON_DETECTOR_IDS alias is removed from python_pack.py and detectors/__init__.py; there is one definition and no other spelling of the union remains in code or skills.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:25`
- **C52** [shape_fit] [load-bearing] (delta): Repeated-id check: MandateRegistry._unique_ids refuses a repeated id at model validation (plugins/arch-compliance/python/acf/registry.py:33-41); MandateRegistry.by_id's silent last-wins is the existing element it replaces; the /acf-setup prose (plugins/arch-compliance/skills/acf-setup/SKILL.md:110) stays with its false parenthetical filed; no host-tier uniqueness test remains.
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:110`
- **C53** [shape_fit] [load-bearing] (carried): The manual-row detector check in tests/test_self_host.py (each manual row's detector is an existing file under plugins/arch-compliance/tests/) is adjacent to, not a duplicate of, load_mandates' ast/guard detector branch (plugins/arch-compliance/python/acf/registry.py:60): it is this host's policy, not the registry contract, so it stays in the host test rather than merging into the loader.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:60`
- **C54** [shape_fit] [load-bearing] (delta): Host config paths in tests/test_self_host.py and the /acf-mandate snippet are imported from acf.repo (plugins/arch-compliance/python/acf/repo.py:12-21); plugins/arch-compliance/skills/architecture-review/SKILL.md:62 is recorded as a current breach in the doctrine and filed in section 9 follow-up 4.
  - spec citation: `plugins/arch-compliance/python/acf/repo.py:12-21`
- **C55** [shape_fit] [load-bearing] (delta): scripts/check_installed_skills.py has one owner in this repository and tests/test_check_installed_skills.py imports GATE_SKILLS from the script rather than re-spelling the tuple; its algorithm is the same as the executed inline block at hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:669-681, which stays as a record.
  - spec citation: `hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:669-681`
- **C56** [shape_fit] (carried): CLAUDE.md's byte-check line carries only the command and points to the doctrine's ## Release discipline for the rule and the mismatch procedure; the rule is stated once (in the doctrine).
  - spec citation: `CLAUDE.md`
- **C57** [shape_fit] [load-bearing] (carried): docs/design/ADR_GATE_HOST_CONTRACT.md is a copy of hm:docs/design/ADR_GATE_HOST_CONTRACT.md with a provenance block naming the canonical copy and the HM commit; two full copies exist until section 5.7 step 6 replaces HM's with a stub.
  - spec citation: `hm:docs/design/ADR_GATE_HOST_CONTRACT.md`
- **C58** [sweep] [load-bearing] (delta): Pattern sweep for specs in hm:docs/design/ whose subject is the ADR gate or ACF: the hits are the twelve HM files listed in section 1, section 7 and section 10 (seven post-plugin ADR_*.md specs and five pre-extraction HM origin specs: ADVERSARIAL_DESIGN_REVIEW.md, ARCHITECTURE_COMPLIANCE_FRAMEWORK.md, ARCHITECTURE_COMPLIANCE_FRAMEWORK_TIER2_LLM_JUDGE.md, ARCHITECTURE_COMPLIANCE_FRAMEWORK_TIER3_AUDIT.md, ARCH_COMPLIANCE_SHIFT_LEFT_GATING.md). One moves here (ADR_GATE_HOST_CONTRACT.md); one is live on HM's change surface (ADR_GATE_HM_CUTOVER.md) and stays; the other ten stay in HM beside their ledger rows and git history.
  - spec citation: `hm:docs/design/ADVERSARIAL_DESIGN_REVIEW.md`
- **C59** [sweep] (delta): Section 10's per-spec HM ledger row counts at 22eae4f9 (records in hm:docs/reviews/adversarial_design_ledger.jsonl whose spec_path equals docs/design/<name>.md): ADR_GATE_HOST_CONTRACT 4, ADR_GATE_HM_CUTOVER 6, ADR_EXTRACTION_TO_PLUGIN 7, ADR_GATE_PLUGIN_COMPONENT 3, ADR_GATE_HM_ADOPTION 0, ADR_PER_FINDING_REVISION_CLASSING 0, ADR_REVISION_EVIDENCE_AND_CARRYOVER_INSTRUMENTATION 4, and 0 for each of the five pre-extraction origin specs.
  - spec citation: `hm:docs/reviews/adversarial_design_ledger.jsonl`
- **C60** [sweep] (carried): The stock rows set unenforced have no subject in this repository: facade.forbid-sink and fsm.transition-guard arrive unenforced from the python-service profile, and soft.react-boundaries is changed from partial because there is no React app (the TypeScript here is a detector bridge); each carries a one-line reason comment.
  - spec citation: `config/architecture/mandates.yml`
- **C61** [shape_fit] [load-bearing] (carried): Root tests/ as a second pyproject testpaths entry fits existing shape: tests that are a property of this repository, not of the shipped plugin tree, are kept out of plugins/arch-compliance/ (README.md:93-95), so test_self_host.py and test_check_installed_skills.py live at the root.
  - spec citation: `README.md:93-95`
- **C62** [sweep] (delta): Exclusion sweep: the doctrine lifts the eight general clauses listed in section 5.2 from hm:GEMINI.md; other HM GEMINI.md sections (section 1 workflow, section 2 git/worktrees, section 5 HFSM, section 6 UI isolation, section 7 sub-bullets, section 8 config & secrets, section 9 logging, section 10 book-root resolution, section 11 metadata facade, sections 12/13 content pipeline) are either HM-domain rules or session workflow and are not lifted into config/architecture/ARCHITECTURE.md.
  - spec citation: `hm:GEMINI.md:103`
- **C63** [mechanism_justification] [load-bearing] (delta): Refusing a repeated id in MandateRegistry._unique_ids at model validation (rung 1, hardening the model for every host) rather than a host-tier uniqueness test or a recovery/normalising step is justified: a host that carried a duplicate had a row silently shadowed, and the refusal names it.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:33-41`
- **C64** [implementability] [load-bearing] (carried): KNOWN_DETECTORS stays in acf.cli_check_diff (plugins/arch-compliance/python/acf/cli_check_diff.py:25) because acf.registry cannot import acf.judge, which imports acf.registry; the /acf-mandate snippet, test_profile_drift.py and tests/test_self_host.py can import it from acf.cli_check_diff without an import cycle or side effect.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:25`
- **C65** [mechanism_justification] [load-bearing] (carried): Bootstrapping the host pair through /acf-setup rather than by hand (decision 7) is justified: it exercises the setup skill on a real host and keeps the pair diffable against the stock profiles (every stock anchor verbatim; non-applicable rows kept as status: unenforced rather than deleted).
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:90-118`
- **C66** [mechanism_justification] [load-bearing] (carried): Giving the two BLOCK fixture lines their row's exemption token with a reason (rather than a status flip, deleting the fixtures, or excluding the tests tree from the gate) is justified because the fixtures exist to contain the pattern and the detector tests call the scanners directly, bypassing the registry layer that honours the token.
  - spec citation: `plugins/arch-compliance/python/acf/enforcement.py:50`
- **C67** [implementability] [load-bearing] (carried): The registry layer honours a row exemption token on the flagged line (plugins/arch-compliance/python/acf/enforcement.py:50), in the forms '# fail-loud.bare-except-ok: <reason>' (Python) and '// fail-loud.empty-catch-ok: <reason>' (TypeScript), while scan_python_file and scan_typescript_file called directly still flag those lines, and the TypeScript self-test still counts three findings in bad.tsx.
  - spec citation: `plugins/arch-compliance/python/acf/enforcement.py:50`
- **C68** [implementability] [load-bearing] (carried): With the two tokens in place, the PostToolUse hook on an edit to plugins/arch-compliance/tests/fixtures/python/bad_except.py or plugins/arch-compliance/tests/fixtures/typescript/bad.tsx returns WARN context only and exits 0, whereas a BLOCK would exit 2 (plugins/arch-compliance/hooks/posttooluse_gate.py:131-134).
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:131-134`
- **C69** [implementability] [load-bearing] (delta): The SubagentStart hook's injected text carries no review verdict: _render_constraints renders the registry rows and a doctrine excerpt alone (plugins/arch-compliance/hooks/inject_constraints.py:153-176), so with respect to hook-injected context reviewers dispatched in this repository stay blind to each other and to prior verdicts.
  - spec citation: `plugins/arch-compliance/hooks/inject_constraints.py:153-176`
- **C70** [implementability] [load-bearing] (carried): tests/test_self_host.py at the repository root is collected through the added testpaths entry in pyproject.toml, imports acf (through the configured pythonpath), and config/architecture/adr.yml loads through load_host_config (AdrHostConfig is extra='forbid', plugins/arch-compliance/python/acf/adr/host.py:22) declaring the two paths of section 5.1.
  - spec citation: `pyproject.toml`
- **C71** [implementability] [load-bearing] (carried): plugins/arch-compliance/tests/test_acf_mandate_skill.py extracts the /acf-mandate validation snippet from the skill as written and runs it against a host built from the python-service profile: it exits 0 on the stock pair and non-zero, naming fail-loud.bare-except, when ## Fail loud is renamed.
  - spec citation: `plugins/arch-compliance/tests/test_acf_mandate_skill.py`
- **C72** [implementability] [load-bearing] (carried): The /acf-mandate snippet loads the registry with known_detectors=KNOWN_DETECTORS, prints the rows, and exits non-zero naming the rows whose anchor missing_anchors reports, so it accepts a stock profile's enforced guard row (ops.no-build-artifacts) that the c0281bf snippet rejected.
  - spec citation: `plugins/arch-compliance/skills/acf-mandate/SKILL.md`
- **C73** [implementability] [load-bearing] (delta): MandateRegistry._unique_ids raises AcfInputError naming each repeated id (plugins/arch-compliance/python/acf/registry.py:33-41) when MandateRegistry is constructed in load_mandates; its callers are the diff CLI, the LLM CLI and both hooks, and each surfaces the refusal rather than swallowing it. Pinned by test_a_repeated_mandate_id_is_refused in plugins/arch-compliance/tests/test_registry.py; line-exact missing_anchors (plugins/arch-compliance/python/acf/registry.py:67-70) is pinned by test_missing_anchors_names_rows_whose_anchor_is_absent (with an inline backtick mention in prose).
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:33-41`
- **C74** [implementability] [load-bearing] (carried): A detection: manual row whose detector is a test-module path loads through load_mandates with known_detectors=KNOWN_DETECTORS and produces neither a finding nor an error in the diff gate (python -m acf.cli_check_diff) or in either hook.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:60`
- **C75** [implementability] [load-bearing] (carried): The CI step: with checkout fetch-depth: 0, `python -m acf.cli_check_diff --repo . --base "origin/${{ github.base_ref || 'main' }}"` after pytest reads the host registry by default; on a pull_request event it diffs the branch against its merge-base with the base branch and fails the job on a BLOCK finding on an added line; on a push to main the base is main itself, --base diffs the merge-base three-dot range (plugins/arch-compliance/python/acf/diff.py:42-45), which is empty, and the step reports nothing and passes.
  - spec citation: `plugins/arch-compliance/python/acf/diff.py:42-45`
- **C76** [implementability] [load-bearing] (delta): scripts/check_installed_skills.py takes the installed plugin's directory, compares each file under the clone's two gate-skill trees (GATE_SKILLS) with the file at the same relative path under <INSTALL_PATH>/skills/ (filecmp.cmp(..., shallow=False)), prints 'installed gate skills identical to the clone' and exits 0, or prints each differing or missing path and exits 1; tests/test_check_installed_skills.py imports GATE_SKILLS and pins three cases.
  - spec citation: `hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:669-681`
- **C77** [mechanism_justification] [load-bearing] (carried): Making the acceptance run this spec's own binding review from this repository (decision 5, section 6) rather than reviewing it elsewhere first is justified because the doctrine the spec proposes cannot be read by the gate until this branch declares it.
  - spec citation: `config/architecture/ARCHITECTURE.md`
- **C78** [mechanism_justification] [load-bearing] (carried): Filing the text-decoding fix and the one-git-runner consolidation as a follow-up (one plan, no spec) rather than fixing them here is justified: the fix is outside this spec's theme, CI is on Linux, and the CLAUDE.md PYTHONUTF8=1 note covers Windows until the fix lands.
  - spec citation: `plugins/arch-compliance/python/acf/diff.py:24-30`
- **C79** [implementability] [load-bearing] (carried): Definition of done item 3: `python -m acf.cli_check_diff --repo . --base origin/main` from the root, with PYTHONUTF8=1 on Windows and PYTHONPATH=plugins/arch-compliance/python, exits 0 on the branch; with --base dfff93f5 it reports the five WARN rows of section 5.4 and exits 0.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py`
- **C80** [implementability] [load-bearing] (delta): Definition of done item 2: deleting config/architecture/adr.yml, or removing any one of the 14 anchor headings from config/architecture/ARCHITECTURE.md, fails tests/test_self_host.py (because missing_anchors compares stripped lines rather than substrings, so inline backtick mentions in prose do not satisfy it); a duplicated row in config/architecture/mandates.yml fails it through MandateRegistry._unique_ids.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:67-70`
- **C81** [implementability] [load-bearing] (delta): /acf-setup is run from this repository's root: Python is detected through pyproject.toml, the user supplies 'both' at the language prompt (docs/plans/PLAN_PLUGIN_SELF_HOSTING.md:78) and 'keep one row' at the duplicate-id stop for ops.no-build-artifacts, yielding one ops.no-build-artifacts row with languages: both and every stock anchor verbatim.
  - spec citation: `docs/plans/PLAN_PLUGIN_SELF_HOSTING.md:78`
- **C82** [mechanism_justification] [load-bearing] (delta): Giving detection: manual rows only to the doctrine sections an existing test enforces (five sections, six rows), and ending the others with 'No row: no test enforces this yet.', is justified because a row is a pointer from rule to enforcement, not a promise; the manual rows use call_sites: [audit] from docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:104.
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:104`
- **C83** [implementability] (delta): config/architecture/mandates.yml on the branch has six detection: manual rows (plugin.one-base-exception, plugin.one-owner-host-paths, plugin.declared-never-defaulted, plugin.adr-code-names-no-host, plugin.gate-prose-names-no-host, plugin.frozen-ledger-format) and each one's detector is an existing file under plugins/arch-compliance/tests/ that enforces the named rule.
  - spec citation: `config/architecture/mandates.yml`
