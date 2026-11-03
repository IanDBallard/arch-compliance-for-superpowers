# Adversarial design review — full detail

Spec: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` @ `4efe8616e1e25b178689c115dec5dd8f0e8f9ec7`
Kinds: feature
Outcome: **BLOCKED**
Claims: 39 · Reviewers: 4 · Converged: 5

## Blocking reasons

- load-bearing claim C25 (shape_fit) is REFUTED: The claim adjudicated novelty by subject (which pair is checked), not by verb. test_every_anchor_is_in_the_doctrine (test_self_host.py:28-31) is the same operation as test_profile_drift.py:30-34 — load_mandates, then 'arch_anchor in doctrine_text' per row — on a different (mandates, ARCHITECTURE.md) pair; the spec itself calls it 'the profile-drift check, applied to the host pair'. KNOWN_DETECTORS at test_self_host.py:15 is a third verbatim copy of the union the package already owns at cli_check_diff.py:25 (second copy: test_profile_drift.py:13). Mandate-id uniqueness: no code owner exists in the loader — MandateRegistry.by_id (registry.py:32-34) builds a dict and silently shadows a duplicate for every host, and /acf-setup only asks an agent to keep ids unique in prose (acf-setup SKILL.md:110); the new test (test_self_host.py:42-44) guards this one host from the wrong tier. The detector-path check for manual rows (test_self_host.py:34-39) extends the validation branch load_mandates already has for ast/guard rows (registry.py:49) as a sibling in a test instead of the loader. 'Nothing else checks' is literally true of the host pair and literally false of the checks.
- load-bearing claim C33 (implementability) is REFUTED: The cited skill text does not resolve the duplicate; it forbids resolving it. SKILL.md:110 reads: 'Keep every mandate id unique. If the same id appears in both (should not for stock profiles), stop and ask; never silently drop a row.' Both stock profiles carry ops.no-build-artifacts (python-service:34, react-app:23, identical bodies, both already languages: both), so the parenthetical premise is false and the prescribed behaviour is a stop-and-ask, not a merge rule yielding one row. The one row in config/architecture/mandates.yml:27-38 with the header comment 'kept once' (line 3) is the outcome of a human decision at that stop, and 'languages: both' is copied from the stock rows, not produced by the merge. Language detection (SKILL.md:49-63) is satisfiable here only via 'a clear app package' / 'substantial *.ts tree' (no root package.json; 3 .ts + 2 .tsx under plugins/arch-compliance/, package.json at detectors/typescript/), which the spec does not state either. The merged pair exists and is sound; the mechanism the claim attributes to SKILL.md:105-118 is not there.
- load-bearing claim C38 (implementability) is REFUTED: Two premises are false under the registry this branch creates. (a) 'sit on lines no future edit touches': the PostToolUse hook scans the whole file, not changed lines — scan_python_file(text, rel, added_lines=None) at posttooluse_gate.py:254 and scan_typescript_file(abs_path, added_lines=None) at :281. Any edit anywhere in bad_except.py, bad.tsx, or the three hasattr test modules re-emits the pre-existing finding; a BLOCK returns exit 2 as blocking feedback (:131-134), which is a block the author must override, not an 'acknowledged' finding. Line-scoping exists only in cli_check_diff.py:121. (b) 'the four pre-existing findings': §4.1 item 5 measured the python-service profile alone. Executed against the merged host registry (PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base dfff93f5 --json): 7 findings — bad_except.py:4 BLOCK fail-loud.bare-except; bad.tsx:4 BLOCK fail-loud.empty-catch; bad.tsx:7,8 WARN no-shims.explicit-any; and the three WARN no-shims.hasattr at test_adr_exceptions.py:22, test_adr_import_graph.py:46, test_adr_skill_prose.py:53. The second BLOCK fixture (bad.tsx, governed by mandates.yml:5-14) and its exemption-token question are never named in the spec. 'Blocks nothing on the day this merges' is true only trivially (no edit, no hook); the marker is present (.acf/enabled: 'enabled by /acf-setup 2026-10-24') so the gate is live.
- implementability claim C33 is REFUTED: The cited skill text does not resolve the duplicate; it forbids resolving it. SKILL.md:110 reads: 'Keep every mandate id unique. If the same id appears in both (should not for stock profiles), stop and ask; never silently drop a row.' Both stock profiles carry ops.no-build-artifacts (python-service:34, react-app:23, identical bodies, both already languages: both), so the parenthetical premise is false and the prescribed behaviour is a stop-and-ask, not a merge rule yielding one row. The one row in config/architecture/mandates.yml:27-38 with the header comment 'kept once' (line 3) is the outcome of a human decision at that stop, and 'languages: both' is copied from the stock rows, not produced by the merge. Language detection (SKILL.md:49-63) is satisfiable here only via 'a clear app package' / 'substantial *.ts tree' (no root package.json; 3 .ts + 2 .tsx under plugins/arch-compliance/, package.json at detectors/typescript/), which the spec does not state either. The merged pair exists and is sound; the mechanism the claim attributes to SKILL.md:105-118 is not there.
- implementability claim C38 is REFUTED: Two premises are false under the registry this branch creates. (a) 'sit on lines no future edit touches': the PostToolUse hook scans the whole file, not changed lines — scan_python_file(text, rel, added_lines=None) at posttooluse_gate.py:254 and scan_typescript_file(abs_path, added_lines=None) at :281. Any edit anywhere in bad_except.py, bad.tsx, or the three hasattr test modules re-emits the pre-existing finding; a BLOCK returns exit 2 as blocking feedback (:131-134), which is a block the author must override, not an 'acknowledged' finding. Line-scoping exists only in cli_check_diff.py:121. (b) 'the four pre-existing findings': §4.1 item 5 measured the python-service profile alone. Executed against the merged host registry (PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base dfff93f5 --json): 7 findings — bad_except.py:4 BLOCK fail-loud.bare-except; bad.tsx:4 BLOCK fail-loud.empty-catch; bad.tsx:7,8 WARN no-shims.explicit-any; and the three WARN no-shims.hasattr at test_adr_exceptions.py:22, test_adr_import_graph.py:46, test_adr_skill_prose.py:53. The second BLOCK fixture (bad.tsx, governed by mandates.yml:5-14) and its exemption-token question are never named in the spec. 'Blocks nothing on the day this merges' is true only trivially (no edit, no hook); the marker is present (.acf/enabled: 'enabled by /acf-setup 2026-10-24') so the gate is live.

## Absorptions

- PARTIAL_OVERLAP: 'tests/test_self_host.py::test_every_anchor_is_in_the_doctrine' shares responsibility 'assert every registry arch_anchor is a literal substring of the doctrine document' with plugins/arch-compliance/tests/test_profile_drift.py:30-34 — R = anchor-in-doctrine check. Extract one function in acf.registry (e.g. missing_anchors(registry, doctrine_text) -> list[str]); test_profile_drift's per-profile loop and the host test both collapse into one call each, and the prose instructions at acf-mandate/SKILL.md:104 and acf-setup/SKILL.md:137-138 run it instead of asking an agent to eyeball it.
- IDENTICAL: 'tests/test_self_host.py:15 KNOWN_DETECTORS' shares responsibility 'define the union of known detector ids' with plugins/arch-compliance/python/acf/cli_check_diff.py:25 — Delete the copy (and test_profile_drift.py:13's copy); import the package's constant from one exported home (acf.detectors or acf.registry).
- BOUNDARY_CUT: 'tests/test_self_host.py::test_mandate_ids_are_unique' shares responsibility 'reject duplicate mandate ids' with plugins/arch-compliance/python/acf/registry.py:32-34 — The loader is the natural owner and currently has the inverse behaviour (by_id shadows silently; acf-setup SKILL.md:110 asks an agent to keep ids unique). load_mandates raises AcfInputError on a repeated id for every host; the host test becomes a consumer of that refusal or is deleted.
- PARTIAL_OVERLAP: 'tests/test_self_host.py::test_every_manual_row_names_an_existing_test_module' shares responsibility "validate that a row's detector reference resolves to something real" with plugins/arch-compliance/python/acf/registry.py:45-52 — R = detector-reference validation. load_mandates already validates ast/guard detectors against known ids; give the same branch a manual case (detector is an existing file under the repo its callers already resolve — cli_check_diff.py:70 and both hooks hold the repo root), and the host test becomes a consumer.
- IDENTICAL: 'tests/test_self_host.py:14 CONFIG = ROOT / "config" / "architecture"' shares responsibility 'declare where ACF looks in a host repository' with plugins/arch-compliance/python/acf/repo.py:12-18 — Delete the spelling; import CONFIG_DIR/MANDATES_REL/ARCH_REL from acf.repo, as the design's own `## One owner for host paths` requires. test_repo_paths.py:18 cannot see root tests/, so the rule is unguarded there.
- IDENTICAL: 'scripts/check_installed_skills.py' shares responsibility 'byte-compare the installed gate skills against the clone' with hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:669-681 — Same algorithm and success string. The HM block is an executed, dated plan record and stays; HM's live instruction (hm:CLAUDE.md:17, reinstall after pulling) should invoke this script from the clone rather than carry its own — HM's change surface, by decision 1, not this spec's.
- PARTIAL_OVERLAP: 'CLAUDE.md:20-23 (before any gate run, byte-check; reinstall on mismatch)' shares responsibility 'state the pre-gate installed-skills byte-check rule' with config/architecture/ARCHITECTURE.md:142-148 — R = the Release-discipline rule text. The doctrine section owns the rule; CLAUDE.md keeps only the command line and points to `## Release discipline`.
- PARTIAL_OVERLAP: "config/architecture/ARCHITECTURE.md plugin sections' 'enforced by `<test>`. Row: `<id>`' sentences" shares responsibility 'name which test enforces a plugin rule' with config/architecture/mandates.yml:152 — R = rule-to-enforcement pointer. The row's `detector` field is the designed pointer (§5.2); the doctrine prose names the row id only and drops the test path, so a renamed test is edited once.
- IDENTICAL: 'docs/design/ADR_GATE_HOST_CONTRACT.md' shares responsibility 'hold the host-contract spec text' with hm:docs/design/ADR_GATE_HOST_CONTRACT.md:3 — As designed: the HM copy becomes a stub in §5.7 step 6. Until that lands, two full copies exist and any edit to either forks the record; the provenance block at :3-8 is the only signal of which is canonical.

## Converged findings

- [2 reviewers: refuter, sweeper] The doctrine's ## Declared text decoding section and spec §4.1 item 7 / §9 follow-up 1 count two subprocess text calls without a declared encoding; the tree has three. plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:49-56 runs node with text=True and no encoding and decodes its JSON findings with the locale codec, the same cp1252 hazard class, so the doctrine's census is false on the day it is written and the follow-up fixes two of three sites.
  - evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:53`
  - evidence: `config/architecture/ARCHITECTURE.md:134-140`
- [3 reviewers: compliance, sweeper, refuter] DoD 4 ('git diff --stat main shows no file outside §4.2') cannot pass at HEAD: the §4.2 disposition table omits scripts/check_installed_skills.py and tests/test_check_installed_skills.py, both branch-created, and tests/test_self_host.py carries a fourth test (mandate-id uniqueness) that §5.5 and DoD 1 do not describe. The spec's own allowlist is incomplete against the branch that implements it.
  - evidence: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:343`
  - evidence: `scripts/check_installed_skills.py:10`
  - evidence: `tests/test_check_installed_skills.py:1`
  - evidence: `tests/test_self_host.py:42`
- [2 reviewers: sweeper, compliance] tests/test_self_host.py:14 re-spells the host config directory (ROOT / 'config' / 'architecture' and the two file names) that acf.repo owns as CONFIG_DIR / MANDATES_REL / ARCH_REL, breaching the design's own ## One owner for host paths; the guard for that rule (plugins/arch-compliance/tests/test_repo_paths.py) scans only the package and hooks, so the root tests/ tree this design adds is invisible to it.
  - evidence: `tests/test_self_host.py:14`
  - evidence: `plugins/arch-compliance/python/acf/repo.py:12-18`
  - evidence: `plugins/arch-compliance/tests/test_repo_paths.py:19`
- [2 reviewers: sweeper, compliance] tests/test_self_host.py duplicates two definitions the design's lifted ## Single point of definition forbids: KNOWN_DETECTORS (test_self_host.py:15) is a third copy of the union owned at plugins/arch-compliance/python/acf/cli_check_diff.py:25 (second copy: test_profile_drift.py:13), and the anchor-in-doctrine loop (test_self_host.py:28-31) repeats test_profile_drift.py:30-34 on a second pair instead of a shared acf.registry function both consume.
  - evidence: `tests/test_self_host.py:15`
  - evidence: `tests/test_self_host.py:28`
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:25`
  - evidence: `plugins/arch-compliance/tests/test_profile_drift.py:13`
- [2 reviewers: compliance, sweeper] config/architecture/ARCHITECTURE.md:3-6 says the doctrine governs four subtrees under plugins/arch-compliance/, none of them the root tests/ and scripts/ directories this design creates, while the CI step and the PostToolUse hook apply the registry to every changed file in the repository: two statements of the governed population, and the narrower one excludes the only code the spec adds.
  - evidence: `config/architecture/ARCHITECTURE.md:3`
  - evidence: `tests/test_self_host.py:14`
  - evidence: `.github/workflows/ci.yml:40`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `.gitignore:8; README.md:20; plugins/arch-compliance/python/acf/repo.py:12-21`
- reasoning: git ls-tree 8dabe82 (the spec's pin) shows no config/architecture/ and no .acf/, and README.md as the only root .md; .gitignore:8 is `.acf/` at both 8dabe82 and c0281bf; repo.py:12-21 fixes the declaration paths (config/architecture/{mandates.yml,ARCHITECTURE.md,adr.yml}) that were absent. The spec's fact holds at its own pin. Two precision caveats are filed as an advisory finding, not a refutation: at c0281bf (the branch base) SECURITY.md is also a root document (added in 9d0974e), and the plugin tree is not byte-identical between 8dabe82 and c0281bf (git diff --stat adds tests/test_adr_skill_invariants.py and changes detectors/typescript/package.json) — the latter is the controller's framing, not the spec's.

#### C2 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/host.py:19-33; plugins/arch-compliance/python/acf/repo.py:18-21; plugins/arch-compliance/skills/adversarial-design-review/reviewers/compliance.md:12,47`
- reasoning: host.py:19-25 is AdrHostConfig with exactly runs_dir and ledger_path (extra=forbid); load_host_config at :28-33 requires repo/ARCH_REL then loads repo/ADR_REL, and repo.py:18-21 pins those to config/architecture/ARCHITECTURE.md and adr.yml. compliance.md:12 says read config/architecture/ARCHITECTURE.md in full then every document it points to; :47 says check the doctrine's self-declared high-frequency misses first. No diff in either file between c0281bf and HEAD.

#### C3 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:90-118; plugins/arch-compliance/detectors/typescript/package.json:1; plugins/arch-compliance/python/acf/registry.py:1`
- reasoning: SKILL.md:90-97 writes config/architecture/mandates.yml and ARCHITECTURE.md; :105-116 is the 'Both languages (preferred: one merged pair)' procedure. ls confirms plugins/arch-compliance/detectors/typescript/ holds package.json, package-lock.json, tsconfig.json, src/, and plugins/arch-compliance/python/acf/ is the Python package. The HEAD mandates.yml:1-3 header and ARCHITECTURE.md:11-14 record that the merge was done.

#### C4 — SURVIVED
- evidence: `plugins/arch-compliance/tests/fixtures/python/bad_except.py:4; plugins/arch-compliance/tests/test_adr_exceptions.py:22; plugins/arch-compliance/tests/test_adr_import_graph.py:46; plugins/arch-compliance/tests/test_adr_skill_prose.py:53`
- reasoning: Re-ran `PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base dfff93f5 --mandates plugins/arch-compliance/profiles/python-service/mandates.yml --json` at HEAD (dfff93f5 confirmed as the sole root via git rev-list --max-parents=0). Output: exactly 4 findings — 1 BLOCK fail-loud.bare-except at bad_except.py:4 and 3 WARN no-shims.hasattr at the three test modules above; nothing under acf/. Measured at HEAD rather than 8dabe82, but the branch's added files contribute no finding.

#### C5 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:8,18,45-52; plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; tests/test_self_host.py:34-39`
- reasoning: registry.py:8 Detection Literal includes "manual"; :18 `detector: str` is required; :49 checks known_detectors only when `m.detection in {"ast", "guard"}` (and only for status enforced, :47). cli_check_diff.py:94-99 selects mandates by detector id for the four config-driven detectors only, so a manual row naming a test path is never dispatched and cannot crash the scan — which the HEAD run in C4-style with the host registry would exercise. The HEAD rows do name test modules (mandates.yml:148-201) and tests/test_self_host.py:34-39 pins their existence.

#### C6 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:24-30; plugins/arch-compliance/python/acf/adr/citations.py:62-65; plugins/arch-compliance/python/acf/diff.py:75; .github/workflows/ci.yml:11`
- reasoning: Both runners call subprocess.run with capture_output=True, text=True and no encoding. Reproduced on this node (Python 3.13.2, locale.getpreferredencoding() = cp1252): the same command as C4 without PYTHONUTF8 prints `Exception in thread Thread-31 (_readerthread)` ending in encodings/cp1252.py:23, then the main thread dies at diff.py:75 with `AttributeError: 'NoneType' object has no attribute 'splitlines'` (stdout is None after the reader thread died). `git diff dfff93f5...HEAD` fails cp1252 decoding at byte 0x9d. ci.yml:11 is ubuntu-latest. Note a third undeclared-encoding subprocess at detectors/typescript_bridge.py:49-56 — filed as an unanchored finding since the spec and doctrine say two.

#### C7 — SURVIVED
- evidence: `.github/workflows/ci.yml:34-35; .github/workflows/ci.yml:39-40; plugins/arch-compliance/python/acf/cli_check_diff.py:28`
- reasoning: git show c0281bf:.github/workflows/ci.yml has a single Python test step `Run pytest` / `run: pytest` at :34-35 and no acf.cli_check_diff / acf-check-diff invocation (the only other run step is `npm test` for the TS self-test). HEAD adds the diff-gate step at :39-40, confirming it was absent before.

#### C8 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_host_acceptance.py:26-40; plugins/arch-compliance/tests/test_adr_host_acceptance.py:74-94`
- reasoning: _host() at :26-40 builds tmp_path/host with config/architecture/adr.yml, ARCHITECTURE.md and a git init; the test at :74-94 calls load_host_config, classify_citations, write_run_detail and append_row directly from acf.adr — Python API calls, no skill or plugin invocation.

#### C9 — SURVIVED
- evidence: `hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:5276-5277; hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:5281`
- reasoning: At HM 6de1c790 (git show), criterion 5 'A second repository (Cayenne) can install the plugin and run the gate with its own declared configuration and no HM paths anywhere' is at :5276-5277 and 'Item 5 is the one that proves the objective rather than approximating it' at :5281. The cited range :5264-5269 shows the preamble and criteria 1-2 at that same commit, so the lines had not 'since moved' — the citation was off at the pin. Fact survives; citation precision filed as advisory.

#### C10 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/hooks.json:4-26; plugins/arch-compliance/hooks/posttooluse_gate.py:72-81; plugins/arch-compliance/hooks/inject_constraints.py:71-80; plugins/arch-compliance/python/acf/repo.py:29`
- reasoning: hooks.json registers SubagentStart matcher '*' and PostToolUse matcher 'Write|Edit|MultiEdit'; both scripts test repo/ENABLED_REL (.acf/enabled, repo.py:29) and exit 0 with {continue:true} when absent (posttooluse_gate.py:72-81, inject_constraints.py:71-80). The deferral's core — no-op without the marker, gate on with it — holds. The 'nothing else changes' gloss is not strictly true: the same marker also activates SubagentStart constraint injection (inject_constraints.py:82-130 renders the doctrine excerpt once enabled), which this very dispatch received. Filed as an important unanchored finding rather than a refutation because the spec's own §4.1 item 11 names both hooks; §5.4 just omits the second effect.

#### C11 — SURVIVED
- evidence: `pyproject.toml:3; pyproject.toml:23; plugins/arch-compliance/.claude-plugin/plugin.json:3`
- reasoning: git show c0281bf:pyproject.toml — :3 `version = "0.2.0"`, :23 `testpaths = ["plugins/arch-compliance/tests"]` (single entry); git show c0281bf:plugins/arch-compliance/.claude-plugin/plugin.json:3 `"version": "0.2.0"`. HEAD pyproject.toml:23 now lists both entries; version unchanged at 0.2.0 in both files.

#### C12 — SURVIVED
- evidence: `CLAUDE.md:33-37; .github/workflows/ci.yml:11; .github/workflows/ci.yml:39-40; plugins/arch-compliance/python/acf/adr/citations.py:81,86,98,103`
- reasoning: CLAUDE.md:33-37 carries the PYTHONUTF8=1 note; ci.yml:11 runs on ubuntu-latest and the diff-gate step at :39-40 therefore never hits the cp1252 path. The acceptance run itself uses the citation runner (check-ignore, rev-parse, rev-list, ls-files at citations.py:81,86,98,103): I checked that none of its outputs can carry non-cp1252 bytes here — `git ls-files` has 0 non-ASCII names and rev-list prints hashes — so no step of the design depends on the fix on this node either. The one Windows-exposed command (the diff gate, DoD 3) is the one the note covers.

#### C13 — SURVIVED
- evidence: `hm:docs/design/ADR_GATE_HOST_CONTRACT.md:80-81; plugins/arch-compliance/python/acf/adr/ledger.py:188-231; plugins/arch-compliance/python/acf/adr/rollup.py:66; docs/design/ADR_GATE_HOST_CONTRACT.md:3-8`
- reasoning: Decision 6 text verified at both 6de1c790 and 3e1a2390 (:80-81, 'moves to the plugin repository after 1d's acceptance run'). Ledger count: at the hm-1d branch 3e1a2390 the plugin-spec rows are 7 EXTRACTION + 3 HM_CUTOVER + 4 HOST_CONTRACT + 3 PLUGIN_COMPONENT + 3 REVISION_EVIDENCE + 1 amendment = 21, matching the spec (HM main at 6de1c790 had 18; HM HEAD now 24 after the 1d v4 run). Append-only: ledger.py exposes only append_row/append_amendment (:222,:231) over _append_json_line (:188); nothing in acf opens a row's spec_path as a file (rollup.py:66 only renders the string), so 'resolving' is for human readers and the stub suffices. The HEAD copy carries the provenance line (:3-8); the HM stub is not yet written, consistent with §5.7 step 6 being post-merge.

#### C14 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/citations.py:49-51,146-185; plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:76-81,101; hm:docs/reviews/adr_runs/ADR_GATE_HOST_CONTRACT_v3_2026-10-12.md:28,35,247`
- reasoning: resolve_citation at :146-185 tests proposed, asserted_absent, absolute (:49-51 regex needs a one-letter drive or root, so `hm:` does not match), escaping, existing, suffix, ignored, historical, then returns unresolved; no branch recognises a repository prefix. SKILL.md:76-81 raises UnresolvableCitationError on any unresolved citation before dispatch and :101 labels unresolved 'hard fail before dispatch'. The HM v3 run detail at :28,35,247 carries `acf:plugins/arch-compliance/...` evidence paths, confirming reviewers opened sibling-checkout files under that convention.

#### C15 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51; config/architecture/ARCHITECTURE.md:7-9`
- reasoning: Lines 43-51 are '## Governing principles (portable)' listing 1 Fail loud, 2 No shims, 3 POSIX paths, 4 Registry is the spine, 5 Superpowers override contract. The HEAD doctrine points back to them at ARCHITECTURE.md:7-9 as the spec's §5.2 last paragraph says.

#### C16 — REFUTED
- evidence: `hm:GEMINI.md:103-105; hm:GEMINI.md:111; hm:GEMINI.md:129; hm:GEMINI.md:136; hm:GEMINI.md:189,191`
- reasoning: At HM 6de1c790 (git show): the three fail-loud sentences sit at :103 (bare except), :104 (defaulting to None), :105 (hasattr ... are shims) — inside :102-106, correct; the no-shims sentence at :111 — inside :110-112, correct; 'Refactor within scope' at :129 — correct. But 'Single point of definition' is at :136, not :134 (:134 is the in-memory encapsulation bullet), and the first POSIX sentence 'Path strings persisted to YAML or JSON must use POSIX format' is at :189, outside :190-194 (only the second, `Path.as_posix()` alone is not sufficient, is inside at :191). Two of five locations are wrong at the pinned commit; the quoted text exists in every case, so this is precision only (non-load-bearing) and carries into ARCHITECTURE.md:47,154 which repeat the same line numbers.

#### C17 — SURVIVED
- evidence: `hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:666-681; scripts/check_installed_skills.py:22-33; CLAUDE.md:20-23`
- reasoning: Task 8 step 1 at HM plan :666-681 is an inline Python block that rglobs the two gate skill dirs in the clone and filecmp.cmp(shallow=False)s each file against <INSTALL_PATH>/skills/<skill>/..., printing 'installed gate skills identical to the clone'. scripts/check_installed_skills.py:22-33 is the same algorithm (same two skills at :18, same filecmp call at :31, same message at :46). I ran it against the node's installPath from installed_plugins.json (0.2.0): exit 0, identical. The plan is ticked merged (HM PR #435, :11), so the start condition in §5.7 step 1 is now met.

### Unanchored findings

- **important**: The doctrine's 'Declared text decoding' section and spec §4.1 item 7 count two undeclared-encoding subprocess calls, but the TypeScript bridge is a third (text=True, no encoding) — the doctrine's own high-frequency miss applies to a site the doctrine says does not exist, and §9 follow-up 1 fixes only two of three.
  - evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:53`
- **important**: Writing .acf/enabled activates SubagentStart constraint injection as well as the PostToolUse gate; §5.4 describes only the gate, and every reviewer dispatched in this repository (this one included) now receives the doctrine excerpt as hook context, which the spec's blind-review framing in §6 does not account for.
  - evidence: `plugins/arch-compliance/hooks/inject_constraints.py:71-130`
- **advisory**: The branch carries tests/test_check_installed_skills.py, which §4.2's disposition table does not list, so DoD 4 ('git diff --stat main shows no file outside §4.2') fails as written.
  - evidence: `tests/test_check_installed_skills.py:1`
- **advisory**: tests/test_self_host.py has four tests (test_mandate_ids_are_unique added) where §5.5 and DoD 1 specify three.
  - evidence: `tests/test_self_host.py:42`
- **advisory**: At the branch base c0281bf SECURITY.md is a second root document and the plugin tree differs from 8dabe82 (test_adr_skill_invariants.py added, TS package.json changed); decision 2's 'README.md only' and the run's 'byte-identical' framing are both stale against the base, though neither changes the doctrine-absence premise.
  - evidence: `SECURITY.md:1`
- **advisory**: Three HM citations are off at the pinned commit, not 'since moved': criterion 5 is at REMEDIATION :5276-5277 and its 'proves the objective' sentence at :5281 (cited :5264-5269); GEMINI.md 'Single point of definition' is at :136 (cited :134); the first POSIX-paths sentence is at :189 (cited :190-194) — and ARCHITECTURE.md repeats the GEMINI line numbers.
  - evidence: `config/architecture/ARCHITECTURE.md:47`
- **advisory**: §4.1 item 13 and §5.7 step 1 describe 1d as unmerged and the plugin as uninstalled; both are now false (HM PR #435 squash 812f9c2b7 on 2026-10-23, plugin 0.2.0 installed and byte-identical), and the spec's ledger count of 21 was taken from the hm-1d branch 3e1a2390 rather than the hm: pin 6de1c790 (18 there, 24 at HM HEAD) — status lines worth refreshing before the record is minted.
  - evidence: `hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:11`

### Looked for but did not find

- A reader anywhere in plugins/arch-compliance/python/acf that opens a ledger row's spec_path as a file (only rollup.py:66 renders the string), which would make the HM stub load-bearing
- A dispatch path for `detection: manual` rows in cli_check_diff.py or enforcement.py that would run or reject a row whose detector is a test-module path
- Non-ASCII tracked filenames (git ls-files: 0) or cp1252-undecodable commit messages in this repository that would crash the citation runner's git calls during the acceptance run on Windows
- Any change to plugins/arch-compliance/skills/ on this branch (git diff --stat c0281bf HEAD lists none) that would owe a version bump under the doctrine's Release discipline
- A repository-prefix branch (`hm:`/`acf:`) in resolve_citation that would classify a prefixed path as anything but unresolved
- A stub already written at HistoricMansions docs/design/ADR_GATE_HOST_CONTRACT.md (still the 512-line v4 body at HM HEAD 22eae4f9, as expected before §5.7 step 6)
- docs/reviews/ or a tracked .acf/enabled at HEAD (neither exists; docs/ holds design/, guides/, plans/)

## compliance

### Claim verdicts

#### C18 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:50; config/architecture/mandates.yml:148-201; config/architecture/ARCHITECTURE.md:83, config/architecture/ARCHITECTURE.md:89, config/architecture/ARCHITECTURE.md:95, config/architecture/ARCHITECTURE.md:103, config/architecture/ARCHITECTURE.md:111; tests/test_self_host.py:28-39; plugins/arch-compliance/tests/test_adr_exceptions.py:35, plugins/arch-compliance/tests/test_repo_paths.py:53, plugins/arch-compliance/tests/test_adr_host.py:49, plugins/arch-compliance/tests/test_adr_code_portability.py:11, plugins/arch-compliance/tests/test_adr_ledger.py:70`
- reasoning: The principle's actual text is at line 50, not 49: '4. Registry is the spine — prose anchors, detectors, auditors, and call sites must agree or tests fail' (line 49 is principle 3, POSIX paths; the spec's :49 is off by one, filed as an advisory precision finding). The design satisfies the principle as stated: mandates.yml:148-201 carries five detection: manual rows whose detector strings are the five test modules, each of which I opened and each of which enforces the named rule; every arch_anchor in the file (nine stock, five plugin) is a literal '## ' heading in ARCHITECTURE.md; tests/test_self_host.py:28-31 pins anchor presence and :34-39 pins that each manual detector is an existing file under plugins/arch-compliance/tests/. One nuance: the anchor test (:30) checks substring membership, not heading-ness, which matches spec §5.2's own wording ('literal substring of the file') but is weaker than the claim's 'literal heading'; at HEAD all fourteen anchors are headings, so the claim holds in fact.

#### C19 — SURVIVED
- evidence: `config/architecture/adr.yml:1-2; plugins/arch-compliance/python/acf/adr/host.py:22-25; plugins/arch-compliance/python/acf/adr/host.py:28-33; plugins/arch-compliance/tests/test_adr_host.py:37-52; plugins/arch-compliance/python/acf/adr/run_detail.py:33-35; docs/design/ADR_GATE_HOST_CONTRACT.md:77-78; config/architecture/ARCHITECTURE.md:95-101`
- reasoning: Doctrine text (ARCHITECTURE.md:97-99): 'A value the gate cannot derive from the tree is declared by the host in config/architecture/adr.yml; no default stands in for a missing declaration, and a missing declaration fails loud.' 1c decision 4 (ADR_GATE_HOST_CONTRACT.md:77-78): 'The two defaults that phase 1b ported verbatim are deleted, not kept as fallbacks.' adr.yml:1-2 declares both values. AdrHostConfig (host.py:24-25) types both as required fields with no default and extra=forbid (:22); load_host_config (:30-33) refuses an absent doctrine then an absent/invalid declaration. A grep of acf/ for runs_dir and ledger_path finds no defaulted re-entry: the only other site is run_detail_path (run_detail.py:34), whose runs_dir is keyword-required. test_adr_host.py:40-45 parametrizes absent, missing-key, empty and backslash declarations and asserts refusal.

#### C20 — SURVIVED
- evidence: `config/architecture/adr.yml:1-2; plugins/arch-compliance/python/acf/adr/host.py:24-25; plugins/arch-compliance/python/acf/adr/contract.py:60-91; plugins/arch-compliance/python/acf/adr/contract.py:129; plugins/arch-compliance/tests/test_adr_host.py:45; config/architecture/ARCHITECTURE.md:41-48; hm:GEMINI.md:189-191`
- reasoning: Doctrine (ARCHITECTURE.md:43-48): persisted YAML/JSON paths use POSIX form, with the lifted HM text 'Path strings persisted to YAML or JSON must use POSIX format' (now at hm:GEMINI.md:189; the spec's 190-194 has shifted by one line in the current HM checkout, as the controller warned). adr.yml:1-2 holds two relative forward-slash paths. host.py:24-25 types both as PosixStr, which contract.py:129 defines as Annotated[str, AfterValidator(_reject_backslash)] and :89-90 raises ValueError on any backslash — it refuses, never normalizes, a deliberate choice the module documents at :66-74. test_adr_host.py:45 ('backslash' case) asserts the refusal. Two precision notes that do not unseat the claim: 'relative' is not enforced by the type, only pinned by exact-value equality in tests/test_self_host.py:24-25; and the lifted HM text prescribes string-level normalization while the plugin rejects — the doctrine quotes HM's sentence without noting the plugin's stricter stance.

#### C21 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:48; config/architecture/ARCHITECTURE.md:7-9; config/architecture/ARCHITECTURE.md:29-39; CLAUDE.md:3-5; plugins/arch-compliance/skills/adversarial-design-review/reviewers/compliance.md:12; hm:GEMINI.md:111`
- reasoning: Principle 2's actual text (:48): 'No shims — one registry façade; one finding schema; do not dual-run parallel mandate lists.' The design keeps one registry (mandates.yml) and one doctrine file that points rather than duplicates: ARCHITECTURE.md:8-9 says 'The five governing principles stated there are not restated here; a mandate row that needs one of them names it by its anchor below', and CLAUDE.md:3-5 is a pointer to the doctrine pair plus process rules, which is the shape the host contract sanctions (compliance.md:12: the doctrine is 'the file and every document it points to'). One caveat for the author: the doctrine's own ## No shims section (:29-39) carries the type-escape, hasattr and lifted bridge-code rules only — nothing about parallel mandate lists — so the 'one registry' content lives solely at the pointed-to principle 2; a reader of the doctrine alone would not find it, but the pointer is the design's stated mechanism, so the claim holds.

#### C22 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:51; CLAUDE.md:7-23; CLAUDE.md:25-31; README.md:22-24; plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:430-456; plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:1`
- reasoning: Principle 5's actual text (:51): 'where this plugin's plan/DoD/constraint defaults conflict with Superpowers generics, the host architecture + registry win; document that explicitly.' CLAUDE.md:7-9 states the override rule, :11-14 record spec and plan locations, :15-19 make the gate brainstorming's terminal state with BLOCKED returning through arch-compliance:responding-to-adversarial-review (the skill exists at the path cited) and the re-run scope deferred to the gate skill (whose revision-class rule I read at SKILL.md:430-456), :20-23 add the byte-check precondition, and :25-31 record the citation convention. README.md:22-24 carries the same override contract at the repository level. The documentation the principle demands exists and is explicit.

#### C23 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:125-132; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:334-350; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:90-137; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:141-155; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:399-410`
- reasoning: Doctrine text (:127-129): no claim is load-bearing on 'every/all/only/complete/untouched/no second', and 'A test that must bound a population allowlists per line with a reason.' DoD items 1-3 and 5-8 are per-item and each names a command or artifact. The census (§4.1) states each item as a measured result and the appendix (:399-410) records the command and output beside it. DoD item 4's second clause ('git diff --stat main shows no file outside §4.2') is a universal negative, but it is exactly the form the rule's second sentence sanctions: a bounded population (the branch diff) checked against a per-line allowlist with a reason column (§4.2's table). So the rule is applied, and the claim holds as a statement about form. The allowlist's content is wrong at HEAD, which I file separately as an important finding rather than as a refutation of the claim.

### Unanchored findings

- **important**: DoD item 4 ('no file outside §4.2') cannot pass at HEAD: the §4.2 disposition table omits scripts/check_installed_skills.py and tests/test_check_installed_skills.py, both branch-created files whose docstrings cite this spec's §5.3 — the doctrine's own high-frequency miss #1 (a completeness claim in a spec) with an incomplete allowlist.
  - evidence: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:343; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:141-155; scripts/check_installed_skills.py:10; tests/test_check_installed_skills.py:1`
- **advisory**: The spec cites docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:49 for 'Registry is the spine' (§7 and claim C18), but line 49 is principle 3 (POSIX paths); the registry principle is line 50 — a one-line citation slip, non-mechanical.
  - evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:49-50; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:324`
- **advisory**: ## No completeness claims forbids a 'doctrine sentence' load-bearing on 'every' or 'only', yet the doctrine's own rule sentences are universals ('Every ACF exception', 'acf.repo is the only declaration', 'Every subprocess call') and a row-named test asserts over a whole module without a per-line allowlist; the rule needs its scope stated (factual claims about the tree vs normative rules; enumeration-bounded populations) or it adjudicates inconsistently.
  - evidence: `config/architecture/ARCHITECTURE.md:127; config/architecture/ARCHITECTURE.md:85; config/architecture/ARCHITECTURE.md:91; config/architecture/ARCHITECTURE.md:136; plugins/arch-compliance/tests/test_adr_exceptions.py:35`
- **advisory**: The doctrine's governing-scope sentence names four trees under plugins/arch-compliance/ and none of the root tests/ or scripts/ directories this spec creates, so the two code files the spec adds are ungoverned by the doctrine's own words while the CI diff gate scans the whole repository; within them, tests/test_self_host.py:14 re-spells the host config directory by hand rather than consuming acf.repo.ARCH_REL / MANDATES_REL (## One owner for host paths, whose test scans only python/ and hooks/).
  - evidence: `config/architecture/ARCHITECTURE.md:3-6; tests/test_self_host.py:14; plugins/arch-compliance/python/acf/repo.py:15-18; plugins/arch-compliance/tests/test_repo_paths.py:19; .github/workflows/ci.yml:40`
- **advisory**: tests/test_self_host.py:15 adds a third composition of the KNOWN_DETECTORS union already built in cli_check_diff.py and test_profile_drift.py — the lifted ## Single point of definition rule ('exactly one canonical implementation that every call site consumes') applied to the spec's own new test.
  - evidence: `tests/test_self_host.py:15; plugins/arch-compliance/python/acf/cli_check_diff.py:25; plugins/arch-compliance/tests/test_profile_drift.py:13; config/architecture/ARCHITECTURE.md:152-153`
- **advisory**: ## Declared, never defaulted generalizes 1c decision 4 to 'a value the gate cannot derive', but acf.repo.RATCHET_BASELINE_REL is a default that re-enters when a mandate omits params.baseline and resolve_repo falls back to cwd (self-described 'a genuine fallback'); the doctrine neither scopes 'the gate' to the ADR gate nor records these as current breaches the way ## Single point of definition and ## Declared text decoding do — high-frequency miss #2's shape.
  - evidence: `config/architecture/ARCHITECTURE.md:97-99; plugins/arch-compliance/python/acf/repo.py:23-26; plugins/arch-compliance/python/acf/repo.py:44; config/architecture/mandates.yml:97`

### Looked for but did not find

- ## Fail loud: read both new code files (tests/test_self_host.py, scripts/check_installed_skills.py) end to end — no bare or broad except, no defaulted return; the script exits 1 on any missing or differing file (scripts/check_installed_skills.py:41-47) and 2 on bad arguments. Not breached.
- ## POSIX paths beyond adr.yml: the five manual-row detector strings (config/architecture/mandates.yml:152,163,174,185,196) and the ratchet baseline (:97) are forward-slash; scripts/check_installed_skills.py:32 emits as_posix(); no str(path) serialization added. Not breached.
- ## Build artifacts: nothing staged under dist/ or build/; .gitignore:6-7 excludes both. Not touched.
- ## Frozen ledger format: spec §3 declares no change to LedgerRow/LedgerAmendment; docs/reviews/ is absent at HEAD (Glob), to be created by the acceptance run as §4.2 says. Not touched.
- ## Prose names no host: CLAUDE.md:28 and ARCHITECTURE.md name HistoricMansions, but the rule scopes to skill prose and runtime messages (config/architecture/ARCHITECTURE.md:105); the seven skill files are unchanged by this spec (§3) and remain under plugins/arch-compliance/tests/test_adr_skill_prose.py:18-19. Not breached.
- ## Declared text decoding: new code reads with encoding='utf-8' (tests/test_self_host.py:29) or compares bytes (scripts/check_installed_skills.py:31, filecmp); no new subprocess call; the two breaches the doctrine records match what I read at plugins/arch-compliance/python/acf/diff.py:24-30 and plugins/arch-compliance/python/acf/adr/citations.py:62-65. Not breached by this design.
- ## Release discipline: plugins/arch-compliance/.claude-plugin/plugin.json:3 and pyproject.toml:3 both read 0.2.0; the spec changes no skill prose (§3), so no bump is due; the byte-check script exists at the path CLAUDE.md:20 names. Not breached.
- ## Scoped refactor: §3 non-goals leave the git runners and detectors untouched; config/architecture/ARCHITECTURE.md:137-140 and :154-157 record the breaches instead of fixing them in this slice. Honoured.
- ## Façade sinks / ## FSM transitions / ## React boundaries: rows set unenforced with an inline reason (config/architecture/mandates.yml:40,101,117) matching the doctrine's 'Unenforced here' sentences (:63, :69, :80-81). Consistent.
- High-frequency misses #3 (host name in skill prose — none changed), #4 (stdlib mixin — no new exception class), #5 (subprocess text call without encoding — none added): each checked against the branch's new files; none present.
- ## One base exception: the design adds no exception type; plugins/arch-compliance/tests/test_adr_exceptions.py:35-45 still covers the module. Not touched.

### Unstated mandates

- ## One owner for host paths — tests/test_self_host.py:14 is a new hand-spelling of the host config directory outside acf.repo (acf.repo.ARCH_REL and MANDATES_REL exist at plugins/arch-compliance/python/acf/repo.py:15-18); spec §5.5 says nothing about this section governing its own test, and the row's test (plugins/arch-compliance/tests/test_repo_paths.py:19) never scans the root tests/ directory.
- ## Single point of definition — the spec lifts the rule (§5.2) but is silent on it for tests/test_self_host.py:15, which adds a third copy of the KNOWN_DETECTORS union (plugins/arch-compliance/python/acf/cli_check_diff.py:25, plugins/arch-compliance/tests/test_profile_drift.py:13).
- Doctrine scope (config/architecture/ARCHITECTURE.md:3-6) — the spec creates root-level tests/ and scripts/ (§4.2) and says nothing about adding them to the trees the doctrine governs; as written the doctrine does not reach the only code this spec adds.

## sweeper

### Claim verdicts

#### C24 — SURVIVED
- evidence: `config/architecture/adr.yml:1-2; plugins/arch-compliance/python/acf/adr/host.py:19-33; plugins/arch-compliance/python/acf/repo.py:21; config/architecture/mandates.yml:144-157; plugins/arch-compliance/python/acf/registry.py:8-25; docs/design/ADR_GATE_HOST_CONTRACT.md:72-74,102-104`
- reasoning: The declaration is one file with exactly the two keys AdrHostConfig admits (host.py:22-27 extra=forbid, read at repo/ADR_REL from repo.py:21); the doctrine is at the fixed ARCH_REL path (repo.py:18, require_file at host.py:30). The plugin's own rules are rows of the one Mandate schema (registry.py:13-25; Detection already includes 'manual' at :8), under the stock header that records the /acf-setup merge (mandates.yml:1-3, ARCHITECTURE.md:11-14). Searched for a second declaration surface (grep 'runs_dir|ledger_path|adr.yml' over the tree: only adr.yml, host.py, tests, README prose, CLAUDE.md prose) and a second rules document: none. The host contract's own non-goal (ADR_GATE_HOST_CONTRACT.md:102-104, adr.yml is authored by hand, not by /acf-setup) is consistent with §4.2's 'Create (§5.1)' for adr.yml; decision 7's phrase 'not by hand' overstates only in wording. One restatement exists but is not a second rules document: CLAUDE.md:20-23 carries the Release-discipline rule text that ARCHITECTURE.md:142-148 also carries (filed as advisory).

#### C25 — REFUTED
- evidence: `plugins/arch-compliance/tests/test_profile_drift.py:13,26-34; tests/test_self_host.py:15,28-31,42-44; plugins/arch-compliance/python/acf/cli_check_diff.py:25; plugins/arch-compliance/python/acf/registry.py:32-34,45-52; plugins/arch-compliance/skills/acf-setup/SKILL.md:110; plugins/arch-compliance/skills/acf-mandate/SKILL.md:104`
- reasoning: The claim adjudicated novelty by subject (which pair is checked), not by verb. test_every_anchor_is_in_the_doctrine (test_self_host.py:28-31) is the same operation as test_profile_drift.py:30-34 — load_mandates, then 'arch_anchor in doctrine_text' per row — on a different (mandates, ARCHITECTURE.md) pair; the spec itself calls it 'the profile-drift check, applied to the host pair'. KNOWN_DETECTORS at test_self_host.py:15 is a third verbatim copy of the union the package already owns at cli_check_diff.py:25 (second copy: test_profile_drift.py:13). Mandate-id uniqueness: no code owner exists in the loader — MandateRegistry.by_id (registry.py:32-34) builds a dict and silently shadows a duplicate for every host, and /acf-setup only asks an agent to keep ids unique in prose (acf-setup SKILL.md:110); the new test (test_self_host.py:42-44) guards this one host from the wrong tier. The detector-path check for manual rows (test_self_host.py:34-39) extends the validation branch load_mandates already has for ast/guard rows (registry.py:49) as a sibling in a test instead of the loader. 'Nothing else checks' is literally true of the host pair and literally false of the checks.

#### C26 — SURVIVED
- evidence: `scripts/check_installed_skills.py:22-33; tests/test_check_installed_skills.py:10-12; plugins/arch-compliance/tests/test_adr_skill_invariants.py:1-5; plugins/arch-compliance/tests/test_packaging.py:31-40; README.md:93-95; hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:666-684; hm:CLAUDE.md:17`
- reasoning: Redid the search by behaviour: grep 'installed_plugins|installPath|filecmp|byte-check|byte-identical|identical to the clone' over the whole tree hits only the new script, its test, CLAUDE.md/ARCHITECTURE.md prose, the spec/plan, README:94 (the dual-tree tests deliberately not ported) and a convergence.py docstring. test_adr_skill_invariants.py:5 states 'the dual-tree byte-identity pins are not ported'; test_packaging.py compares tracked files against a built wheel, a different pair. The only prior form is the executed inline block at hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:669-681 (same algorithm, same success string), outside this repository; HM's live instruction is hm:CLAUDE.md:17 ('reinstall after pulling the clone'). HM's scripts/core/skill_install.py compares a host's .claude/ and .cursor/ trees, a different pair.

#### C27 — SURVIVED
- evidence: `hm:docs/design/ADR_GATE_HM_CUTOVER.md:3; hm:docs/design/ADR_GATE_HOST_CONTRACT.md:3,80-81; hm:docs/design/ADR_EXTRACTION_TO_PLUGIN.md:3; hm:docs/design/ADR_GATE_PLUGIN_COMPONENT.md:3; hm:docs/design/ADR_GATE_HM_ADOPTION.md:3; hm:docs/design/ADR_PER_FINDING_REVISION_CLASSING.md:3; hm:docs/design/ADR_REVISION_EVIDENCE_AND_CARRYOVER_INSTRUMENTATION.md:3; hm:docs/design/ARCH_COMPLIANCE_SHIFT_LEFT_GATING.md:3-8`
- reasoning: Redid the sweep two ways. By name: glob docs/design/{ADR_*,ARCH_COMPLIANCE_*}.md in HM returns exactly eight files, the spec's eight (ADR_GATE_HM_CUTOVER.md is now on HM main, not only the branch). By behaviour: grep 'arch-compliance-for-superpowers|plugins/arch-compliance|acf:' over hm docs/design returns five files, all within the eight; the looser grep 'superpowers|arch-compliance|acf.adr' (case-insensitive) returns sixteen, and the eight extra files (ADVERSARIAL_DESIGN_REVIEW.md, ARCHITECTURE_REVIEW_SKILL.md, six book/CMS specs) mention Superpowers skills only — grep 'plugin|arch-compliance' inside the first two returns nothing. Statuses as claimed: superseded (ADR_EXTRACTION_TO_PLUGIN:3; ARCH_COMPLIANCE_SHIFT_LEFT_GATING:8 'Superseded (2026-08-01)… historical design record'), v3 do-not-redispatch, draft v1, filed-gap stub, v4 draft. Note for sequencing, not a refutation: HM's host-contract copy is still the full v4 text at HM main (hm:…HOST_CONTRACT.md:3), so two full copies exist until §5.7 step 6's stub lands.

#### C28 — SURVIVED
- evidence: `config/architecture/mandates.yml:40-51,86-99,101-130; plugins/arch-compliance/profiles/python-service/mandates.yml:47-60; plugins/arch-compliance/tests/test_portable_guards.py:35,79-95; plugins/arch-compliance/detectors/typescript/src/scan.ts; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:1`
- reasoning: grep 'index\.ya?ml' over python/, hooks/ and skills/ (profiles excluded): no writer; the only matches are string fixtures inside detector tests (test_portable_guards.py:35,48) and ledger-text fixtures. grep 'fsm_state|validate_transition': only mandates.yml params and the same test's string fixtures. glob src/**/*.tsx under detectors/typescript: none; the bridge is scan.ts plus two rule files. The 'other rows have a subject' half holds: .py and .ts sources exist for the enforced rows. Precision note: a fourth row is unenforced at HEAD, fail-loud.ratchet (mandates.yml:86-99), inherited from the profile (python-service/mandates.yml:55) with no config/architecture/fail_loud_ratchet.json present (glob config/architecture/*: three files); the claim's 'three' counts the spec's edits, not the file's unenforced rows.

### Unanchored findings

- **important**: The doctrine's `## Declared text decoding` section (ARCHITECTURE.md:134-140) and spec §4.1 item 7 / §9 follow-up 1 count two subprocess text calls without a declared encoding, but the tree has three: typescript_bridge.py:49-56 is a `subprocess.run(..., text=True)` with no `encoding`, decoding node's JSON findings with the locale codec — the same cp1252 hazard class the section describes; the doctrine rests on a false census the day it is written.
  - evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:53`
- **important**: tests/test_self_host.py re-declares the host config layout (`ROOT / "config" / "architecture"`, `/ "mandates.yml"`, `/ "ARCHITECTURE.md"`) that `acf.repo` owns as CONFIG_DIR/MANDATES_REL/ARCH_REL (repo.py:12-18), breaching the design's own `## One owner for host paths` (ARCHITECTURE.md:89-93); the guard that enforces that rule, test_repo_paths.py:18, scans only plugins/arch-compliance/python and hooks, so the root tests/ tree this design adds is invisible to it — the test should import the constants.
  - evidence: `tests/test_self_host.py:14`
- **important**: The anchor-in-doctrine loop (test_self_host.py:28-31 vs test_profile_drift.py:30-34) and the known-detector union (test_self_host.py:15 vs test_profile_drift.py:13 vs the package owner cli_check_diff.py:25) are duplicated, breaching the `## Single point of definition` rule the design lifts into ARCHITECTURE.md:150-157; extract one `acf.registry` function (registry + doctrine text -> missing anchors) and export the union once, with both tests, `/acf-mandate` step at acf-mandate/SKILL.md:104 and `/acf-setup` at acf-setup/SKILL.md:137-138 as consumers.
  - evidence: `tests/test_self_host.py:28`
- **advisory**: Mandate-id uniqueness is enforced only by a host-tier test for this repository (test_self_host.py:42-44) and by /acf-setup prose (acf-setup/SKILL.md:110) while the loader's MandateRegistry.by_id silently shadows a duplicate for every host; the check belongs in load_mandates (raise AcfInputError on a repeated id), after which the host test becomes a consumer or is deleted.
  - evidence: `plugins/arch-compliance/python/acf/registry.py:34`
- **advisory**: ARCHITECTURE.md:3-6 states the doctrine governs four subtrees (python package, hooks, skill prose, TypeScript bridge), but the CI step (ci.yml:40) and the PostToolUse hook apply the registry to every changed .py/.ts in the repository, including root tests/ and scripts/ that this design creates and plugins/arch-compliance/tests; two statements of the governed population, one of which excludes the files the gate just ran on.
  - evidence: `config/architecture/ARCHITECTURE.md:3`
- **advisory**: CLAUDE.md:20-23 restates the `## Release discipline` rule in full (byte-check before any gate run, reinstall on mismatch) that ARCHITECTURE.md:142-148 already states; spec §7 calls CLAUDE.md 'a pointer and process file… not a second doctrine', so it should carry the command and point at the section rather than restate the rule.
  - evidence: `CLAUDE.md:20`
- **advisory**: The five manual rows carry `call_sites: [review]`, a value no code reads (registry.py:20 is an unvalidated list[str]; grep 'call_sites' in python/ and hooks/ finds no consumer) and that the design document's vocabulary does not list (ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:104: precommit, ci, posttooluse, audit); the spec never names it — a declared value with no consumer and no definition.
  - evidence: `config/architecture/mandates.yml:154`
- **advisory**: tests/test_check_installed_skills.py exists at HEAD but appears nowhere in spec §4.2's disposition table, while DoD 4 requires `git diff --stat main` to show no file outside §4.2; the plan (PLAN_PLUGIN_SELF_HOSTING.md:420) lists it, so plan and spec disagree on the change surface.
  - evidence: `tests/test_check_installed_skills.py:1`

### Looked for but did not find

- A second declaration of runs_dir/ledger_path or a second reader of adr.yml: grep 'runs_dir|ledger_path|adr\.yml|ADR_REL' over python/, hooks/, skills/, root — only host.py, repo.py:21, the gate skill's load_host_config step, adr.yml, tests and prose
- A runtime (package-level) anchor check a host could call instead of a test: grep 'arch_anchor' in python/ — only the Mandate field (registry.py:23) and the judge prompt substitution (judge.py:154); no substring check exists in the package
- An existing consumer of `detection == "manual"`: grep '"manual"|\.detection' in python/ and hooks/ — registry.py:8 literal, judge.py:100 (llm only), inject_constraints.py:159 renders the field; nothing dispatches or validates manual rows
- An existing comparer of the installed plugin cache against the clone in this repository: grep 'installed_plugins|installPath|filecmp|byte-identical' — only the new script/test, README:94 (not-ported note), convergence.py docstring
- HM specs about the plugin outside the ADR_*/ARCH_COMPLIANCE_* glob: grep 'arch-compliance-for-superpowers|plugins/arch-compliance|acf:' and case-insensitive 'superpowers|arch-compliance|acf.adr' over hm docs/design — no file outside the eight names the plugin
- A live index.yml writer, a state-field writer under a validator, or a React view in this repository: grep 'index\.ya?ml', 'fsm_state|validate_transition', glob src/**/*.tsx — fixtures-in-strings and params only
- File reads of prose without a declared encoding in python/ and hooks/: grep 'read_text\(' — every call passes encoding="utf-8"; the only undeclared decodes are the three subprocess text calls
- A second definition of the gate's brainstorming-terminal-state rule inside this repository beyond CLAUDE.md:15-19 and README.md:24: none (HM's hm:CLAUDE.md:27-33 is the sibling host's own copy, by decision 1)

### Relationships

- PARTIAL_OVERLAP: `tests/test_self_host.py::test_every_anchor_is_in_the_doctrine` — responsibility `assert every registry arch_anchor is a literal substring of the doctrine document` — existing `plugins/arch-compliance/tests/test_profile_drift.py:30-34`
  - resolution: R = anchor-in-doctrine check. Extract one function in acf.registry (e.g. missing_anchors(registry, doctrine_text) -> list[str]); test_profile_drift's per-profile loop and the host test both collapse into one call each, and the prose instructions at acf-mandate/SKILL.md:104 and acf-setup/SKILL.md:137-138 run it instead of asking an agent to eyeball it.
- IDENTICAL: `tests/test_self_host.py:15 KNOWN_DETECTORS` — responsibility `define the union of known detector ids` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:25`
  - resolution: Delete the copy (and test_profile_drift.py:13's copy); import the package's constant from one exported home (acf.detectors or acf.registry).
- BOUNDARY_CUT: `tests/test_self_host.py::test_mandate_ids_are_unique` — responsibility `reject duplicate mandate ids` — existing `plugins/arch-compliance/python/acf/registry.py:32-34`
  - resolution: The loader is the natural owner and currently has the inverse behaviour (by_id shadows silently; acf-setup SKILL.md:110 asks an agent to keep ids unique). load_mandates raises AcfInputError on a repeated id for every host; the host test becomes a consumer of that refusal or is deleted.
- PARTIAL_OVERLAP: `tests/test_self_host.py::test_every_manual_row_names_an_existing_test_module` — responsibility `validate that a row's detector reference resolves to something real` — existing `plugins/arch-compliance/python/acf/registry.py:45-52`
  - resolution: R = detector-reference validation. load_mandates already validates ast/guard detectors against known ids; give the same branch a manual case (detector is an existing file under the repo its callers already resolve — cli_check_diff.py:70 and both hooks hold the repo root), and the host test becomes a consumer.
- IDENTICAL: `tests/test_self_host.py:14 CONFIG = ROOT / "config" / "architecture"` — responsibility `declare where ACF looks in a host repository` — existing `plugins/arch-compliance/python/acf/repo.py:12-18`
  - resolution: Delete the spelling; import CONFIG_DIR/MANDATES_REL/ARCH_REL from acf.repo, as the design's own `## One owner for host paths` requires. test_repo_paths.py:18 cannot see root tests/, so the rule is unguarded there.
- ADJACENT: `tests/test_self_host.py::test_declaration_names_the_reviews_tree` — responsibility `load a host declaration through load_host_config and pin its values` — existing `plugins/arch-compliance/tests/test_adr_host.py:24-28`
  - resolution: None; keep both.
  - non-merge: test_adr_host.py exercises the contract on a fixture host (reviews/runs); the host test pins this repository's declared values. Different subject; both are consumers of load_host_config.
- IDENTICAL: `scripts/check_installed_skills.py` — responsibility `byte-compare the installed gate skills against the clone` — existing `hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:669-681`
  - resolution: Same algorithm and success string. The HM block is an executed, dated plan record and stays; HM's live instruction (hm:CLAUDE.md:17, reinstall after pulling) should invoke this script from the clone rather than carry its own — HM's change surface, by decision 1, not this spec's.
- ADJACENT: `scripts/check_installed_skills.py` — responsibility `assert two skill trees are byte-identical` — existing `hm:scripts/core/skill_install.py`
  - resolution: None.
  - non-merge: HM's comparer pairs a host's .claude/ and .cursor/ trees (a Cursor-twin property); this script pairs Claude Code's install cache with the source clone. README.md:93-95 records the decision not to port the former.
- ADJACENT: `config/architecture/ARCHITECTURE.md stock sections (`## Fail loud` … `## React boundaries`)` — responsibility `state the stock rule prose under its anchor` — existing `plugins/arch-compliance/profiles/python-service/mandates.yml:1-102`
  - resolution: None.
  - non-merge: Template and instance by design: /acf-setup copies the profile pair into the host (acf-setup/SKILL.md:90-118) and ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:129 says bundled profiles are templates only; the host copy is meant to diverge.
- PARTIAL_OVERLAP: `CLAUDE.md:20-23 (before any gate run, byte-check; reinstall on mismatch)` — responsibility `state the pre-gate installed-skills byte-check rule` — existing `config/architecture/ARCHITECTURE.md:142-148`
  - resolution: R = the Release-discipline rule text. The doctrine section owns the rule; CLAUDE.md keeps only the command line and points to `## Release discipline`.
- PARTIAL_OVERLAP: `config/architecture/ARCHITECTURE.md plugin sections' 'enforced by `<test>`. Row: `<id>`' sentences` — responsibility `name which test enforces a plugin rule` — existing `config/architecture/mandates.yml:152`
  - resolution: R = rule-to-enforcement pointer. The row's `detector` field is the designed pointer (§5.2); the doctrine prose names the row id only and drops the test path, so a renamed test is edited once.
- IDENTICAL: `docs/design/ADR_GATE_HOST_CONTRACT.md` — responsibility `hold the host-contract spec text` — existing `hm:docs/design/ADR_GATE_HOST_CONTRACT.md:3`
  - resolution: As designed: the HM copy becomes a stub in §5.7 step 6. Until that lands, two full copies exist and any edit to either forks the record; the provenance block at :3-8 is the only signal of which is canonical.
- ADJACENT: `CLAUDE.md:7-19 Superpowers overrides (spec/plan locations, brainstorming terminal state)` — responsibility `record a host's session process overriding Superpowers defaults` — existing `hm:CLAUDE.md:21-33`
  - resolution: None.
  - non-merge: Each host owns its own process file (decision 1); the plugin's README.md:24 names the override contract once and both hosts instantiate it.

### Two-owner counts

- assert every arch_anchor is a substring of the doctrine (code + prose): 4
- define the known-detector id union: 3
- spell the host config directory in code (repo.py:12, test_adr_host.py:15, tests/test_self_host.py:14): 3
- reject duplicate mandate ids (test_self_host.py:42-44; acf-setup/SKILL.md:110 prose): 2
- name which test enforces a plugin rule (mandates.yml detector field; ARCHITECTURE.md 'enforced by' sentences): 2
- state the pre-gate installed-skills byte-check rule (ARCHITECTURE.md:142-148; CLAUDE.md:20-23): 2
- installed-vs-clone skill comparison algorithm (scripts/check_installed_skills.py; hm plan :669-681 record): 2
- hold the host-contract spec text until the HM stub lands: 2
- subprocess text decode without declared encoding (doctrine says 2, tree has 3): 3
- state the population the registry governs (ARCHITECTURE.md:3-6 four subtrees; ci.yml:40 + cli_check_diff whole-repo diff): 2

### Document conflicts

- `docs/design/ADR_GATE_HOST_CONTRACT.md:87` (restates): This spec stays in this repository until 1d, and moves to the plugin repository after 1d's acceptance run.
- `docs/design/ADR_GATE_HOST_CONTRACT.md:89` (contradicts): The first live gate run from the plugin is 1d's: this repository on its own declaration, then a second repository (the workstream's exit criterion 5).
- `docs/design/ADR_GATE_HOST_CONTRACT.md:102` (restates): Writing `adr.yml` from `/acf-setup`. A host authors the two-line file; a missing file is refused with its path named
- `docs/design/ADR_GATE_HOST_CONTRACT.md:426` (restates): Telling an AI reviewer which host mandates to weigh | the host's doctrine (read by the compliance reviewer) and the ACF mandate registry | Debt, by decision 1; reconciling them is phase 2's registry work
- `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:111` (restates): A drift test fails when example/profile prose anchors, registry rows, and registered detector ids disagree.
- `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:50` (restates): Registry is the spine — prose anchors, detectors, auditors, and call sites must agree or tests fail.
- `README.md:93` (restates): The origin host's skill-install tests (which assert its `.claude/` and `.cursor/` skill trees are byte-identical) are deliberately not ported: they test a property of a host, not of this plugin, and mean nothing here.

## hardening

### Claim verdicts

#### C29 — SURVIVED
- evidence: `pyproject.toml:23-24; tests/test_self_host.py:7,13,23; plugins/arch-compliance/python/acf/adr/host.py:22-33; config/architecture/adr.yml:1-2; plugins/arch-compliance/python/acf/adr/__init__.py:24,60`
- reasoning: pyproject.toml:23 now reads testpaths = ["plugins/arch-compliance/tests", "tests"] (c0281bf had only the plugin dir, git show c0281bf:pyproject.toml:23); pythonpath (line 24) is a session-wide sys.path entry, so the root tests import acf the same way. tests/test_self_host.py:7 imports load_host_config, which acf.adr exports (__init__.py:24,60). ROOT = parents[1] of tests/ = repo root; load_host_config(ROOT) requires config/architecture/ARCHITECTURE.md (host.py:30, exists at HEAD) then validates adr.yml against AdrHostConfig extra=forbid with two PosixStr fields (host.py:22-25); adr.yml carries exactly runs_dir and ledger_path (adr.yml:1-2). No basename collision: plugins/arch-compliance/tests holds no test_self_host.py or test_check_installed_skills.py. Not run (no test execution), but every hook the claim assumes is present.

#### C30 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:45-52; plugins/arch-compliance/python/acf/cli_check_diff.py:70,94-99,112-113; plugins/arch-compliance/python/acf/enforcement.py:46-52; plugins/arch-compliance/python/acf/detectors/python_pack.py:70,100,147,175; config/architecture/mandates.yml:148-201`
- reasoning: load_mandates raises UnknownDetectorError only when status == enforced AND detection in {ast, guard} AND detector unknown (registry.py:47-49); the five manual rows (mandates.yml:148-201, detection: manual, status: enforced) skip the check. In the diff gate, detectors tag findings with fixed ids (python_pack.py:70 fail-loud.bare-except, :100 no-shims.hasattr, :147/:175 posix-paths.str-serialization; grep of acf/detectors for 'plugin.' is empty), _active_mandates matches m.detector against detector-id constants a test-module path never equals (cli_check_diff.py:94-99), and apply_registry only drops/re-severities by finding.mandate_id (enforcement.py:46-52). Executed: PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main with this registry printed 'No findings.' exit 0; --base dfff93f5 produced findings for stock ids only. The PostToolUse hook loads the same file without known_detectors (posttooluse_gate.py:107) and is equally indifferent.

#### C31 — SURVIVED
- evidence: `.github/workflows/ci.yml:15,32-34,36-40; plugins/arch-compliance/python/acf/cli_check_diff.py:65-67,72-74,89-91; plugins/arch-compliance/python/acf/repo.py:15`
- reasoning: ci.yml:15 sets fetch-depth: 0 with the merge-base comment; ci.yml:39-40 runs python -m acf.cli_check_diff --repo . --base "origin/${{ github.base_ref || 'main' }}" after pytest (36-37) and after npm ci (32-34, so a changed .ts file cannot raise DetectorPackError). With --mandates absent the registry path is repo / MANDATES_REL (cli_check_diff.py:65-67) = config/architecture/mandates.yml (repo.py:15). Exit 1 on any BLOCK finding (cli_check_diff.py:89-91). Caveat for the author, not the spec: the extracted word 'only' is not literally true — GitError/AcfInputError/UnknownDetectorError/DetectorPackError also return 1 (cli_check_diff.py:72-74); that is the desired fail-loud path and the spec's own §5.6 sentence ('It fails the job on a BLOCK finding') does not say 'only'.

#### C32 — SURVIVED
- evidence: `scripts/check_installed_skills.py:18,22-33; CLAUDE.md:20-23; tests/test_check_installed_skills.py:40-61; hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:666-680`
- reasoning: Executed claude plugin list --json: entry arch-compliance@arch-compliance-for-superpowers, version 0.2.0, installPath C:\Users\iball\.claude\plugins\cache\arch-compliance-for-superpowers\arch-compliance\0.2.0. ls of that path shows .claude-plugin/ detectors/ hooks/ profiles/ python/ skills/ tests/, and skills/ holds the same five skill directories as plugins/arch-compliance/skills/. diff -rq plugins/arch-compliance/skills <installPath>/skills is empty. The script walks the clone's two gate-skill trees and compares each file at the same relative path under <installPath>/skills/ with filecmp.cmp(shallow=False) (script:22-33) — the HM plan's Task 8 step 1 inline block, lifted verbatim in structure. Ran it: 'installed gate skills identical to the clone', exit 0. The comparison is well defined and currently passes.

#### C33 — REFUTED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:110; plugins/arch-compliance/profiles/python-service/mandates.yml:34; plugins/arch-compliance/profiles/react-app/mandates.yml:23; config/architecture/mandates.yml:3,27-38`
- reasoning: The cited skill text does not resolve the duplicate; it forbids resolving it. SKILL.md:110 reads: 'Keep every mandate id unique. If the same id appears in both (should not for stock profiles), stop and ask; never silently drop a row.' Both stock profiles carry ops.no-build-artifacts (python-service:34, react-app:23, identical bodies, both already languages: both), so the parenthetical premise is false and the prescribed behaviour is a stop-and-ask, not a merge rule yielding one row. The one row in config/architecture/mandates.yml:27-38 with the header comment 'kept once' (line 3) is the outcome of a human decision at that stop, and 'languages: both' is copied from the stock rows, not produced by the merge. Language detection (SKILL.md:49-63) is satisfiable here only via 'a clear app package' / 'substantial *.ts tree' (no root package.json; 3 .ts + 2 .tsx under plugins/arch-compliance/, package.json at detectors/typescript/), which the spec does not state either. The merged pair exists and is sound; the mechanism the claim attributes to SKILL.md:105-118 is not there.

#### C34 — SURVIVED
- evidence: `config/architecture/mandates.yml:1-3,40-51,101-131; config/architecture/ARCHITECTURE.md:11-14,16,29,41,50,54,59,65,71,76; plugins/arch-compliance/profiles/python-service/ARCHITECTURE.md:6-41; plugins/arch-compliance/profiles/react-app/ARCHITECTURE.md:6-20`
- reasoning: The setup skill was exercised on this host: .acf/enabled reads 'enabled by /acf-setup 2026-10-24' and mandates.yml:1-3 records the two-profile merge. Diffability holds: diff of profiles/python-service/mandates.yml against the host file shows every python-profile row present with unchanged body (only position and the manual-row appendix differ); the three react rows are present. All eight python-profile ## anchors (Fail loud, No shims, POSIX paths, Build artifacts, Fail-loud ratchet, Façade sinks, FSM transitions, Soft fail-loud smells) and the react anchors (Fail loud, No shims, Build artifacts, React boundaries) appear verbatim as headings in ARCHITECTURE.md:16-76. Non-applicable rows are status: unenforced with a comment, not deleted (mandates.yml:40-51 react-boundaries, 101-131 facade/fsm). The one premise slip is advisory and filed below: only soft.react-boundaries was actually flipped (stock react-app row is partial); facade.forbid-sink and fsm.transition-guard are already unenforced in the stock python-service profile.

#### C35 — SURVIVED
- evidence: `config/architecture/mandates.yml:148-201; plugins/arch-compliance/python/acf/registry.py:49; config/architecture/ARCHITECTURE.md:123,132,140,148,157,163; tests/test_self_host.py:34-39; plugins/arch-compliance/hooks/inject_constraints.py:159; plugins/arch-compliance/tests/test_adr_host.py:37-58`
- reasoning: Five manual rows (mandates.yml:148-201) name test modules that all exist: test_adr_exceptions.py, test_repo_paths.py, test_adr_host.py, test_adr_code_portability.py, test_adr_ledger.py (ls confirmed). Six prose-only sections end with 'No row: no test enforces this yet.' (ARCHITECTURE.md:123,132,140,148,157,163 — the four plugin sections plus the two lifted anchors Single point of definition and Scoped refactor). No row names a future test, so test_self_host.py:34-39 (is_file() and the plugins/arch-compliance/tests/ prefix) holds at HEAD. The 'pointer' premise is grounded in registry.py:49 (manual rows bypass the known-detector check) and the rows have a live consumer beyond pointing: inject_constraints.py:159 renders every row into SubagentStart context ('detection=manual, detector=...'), which is how this reviewer received them. test_adr_host.py:37-58 does enforce declared-never-defaulted (absent/unknown-key/missing-field/backslash all refused), so the row's detector is a real enforcer.

#### C36 — SURVIVED
- evidence: `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:20,30-36; plugins/arch-compliance/python/acf/adr/host.py:28-33; plugins/arch-compliance/skills/adversarial-design-review/reviewers/compliance.md:12,47; config/architecture/ARCHITECTURE.md:165-173`
- reasoning: The gate cannot run from this repository before this branch: SKILL.md:30-36 loads load_host_config(repo) first and stops before dispatch when config/architecture/adr.yml or ARCHITECTURE.md is absent (host.py:30 require_file on the doctrine, :31-33 on the declaration); neither file existed at c0281bf (git diff --stat c0281bf..HEAD lists both as created). The compliance reviewer reads config/architecture/ARCHITECTURE.md and every document it points to (compliance.md:12) and checks self-declared high-frequency misses first (compliance.md:47), which the new doctrine supplies at ARCHITECTURE.md:165-173. So the mechanism the decision depends on — a binding run that reads doctrine this branch declares — has its hook. The second half ('the doctrine's first test is whether four blind reviewers can hold this design to it') is a recorded decision, not a tree-derivable fact; noted, not scored. One structural observation for the author (not a hardening finding): the author of the doctrine and of the spec under review are the same change, so the compliance reviewer's unstated-mandate search is bounded by what the author chose to write down.

#### C37 — SURVIVED
- evidence: `CLAUDE.md:33-37; .github/workflows/ci.yml:11; plugins/arch-compliance/python/acf/diff.py:24-30,68; plugins/arch-compliance/python/acf/adr/citations.py:62-65,81,86,98,103; config/architecture/ARCHITECTURE.md:134-140`
- reasoning: All three legs hold. (1) The fix is a code change in diff.py:28 / citations.py:64 (text=True, no encoding) — outside declaration-and-doctrine, and git diff --stat c0281bf..HEAD -- plugins/ is empty, so the branch kept to that. (2) CI runs on ubuntu-latest (ci.yml:11). (3) CLAUDE.md:35-36 gives the PYTHONUTF8=1 form of the diff-gate command. Coverage check of the note: the only runner that decodes file content is diff.py (changed_files/added_lines, :56,:68 run git diff); the citation runner's four git calls return paths and SHAs only (check-ignore :81, rev-parse :86, rev-list :98, ls-files :103; git escapes non-ASCII paths by default), so the exposed path on a Windows node is the one the note covers. The breach is recorded as debt in the doctrine (ARCHITECTURE.md:134-140). Rung distance is real (a workaround at rung 5 where the producer fix is one keyword argument on two lines) and is filed as an advisory finding below; the written justification exists.

#### C38 — REFUTED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:131-134,254,281; plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:4,7,8; plugins/arch-compliance/tests/fixtures/python/bad_except.py:4; config/architecture/mandates.yml:5-14`
- reasoning: Two premises are false under the registry this branch creates. (a) 'sit on lines no future edit touches': the PostToolUse hook scans the whole file, not changed lines — scan_python_file(text, rel, added_lines=None) at posttooluse_gate.py:254 and scan_typescript_file(abs_path, added_lines=None) at :281. Any edit anywhere in bad_except.py, bad.tsx, or the three hasattr test modules re-emits the pre-existing finding; a BLOCK returns exit 2 as blocking feedback (:131-134), which is a block the author must override, not an 'acknowledged' finding. Line-scoping exists only in cli_check_diff.py:121. (b) 'the four pre-existing findings': §4.1 item 5 measured the python-service profile alone. Executed against the merged host registry (PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base dfff93f5 --json): 7 findings — bad_except.py:4 BLOCK fail-loud.bare-except; bad.tsx:4 BLOCK fail-loud.empty-catch; bad.tsx:7,8 WARN no-shims.explicit-any; and the three WARN no-shims.hasattr at test_adr_exceptions.py:22, test_adr_import_graph.py:46, test_adr_skill_prose.py:53. The second BLOCK fixture (bad.tsx, governed by mandates.yml:5-14) and its exemption-token question are never named in the spec. 'Blocks nothing on the day this merges' is true only trivially (no edit, no hook); the marker is present (.acf/enabled: 'enabled by /acf-setup 2026-10-24') so the gate is live.

#### C39 — SURVIVED
- evidence: `.github/workflows/ci.yml:3-7,15,40; plugins/arch-compliance/python/acf/diff.py:42-45,56`
- reasoning: The hook exists: ci.yml:40 runs --base "origin/${{ github.base_ref || 'main' }}" and ci.yml:15 fetches full history (actions/checkout fetch-depth 0 fetches all remote branches, so origin/<base> is present). diff.py:42-45 turns --base into the three-dot form <base>...HEAD, i.e. merge-base(base, HEAD)..HEAD (diff.py:56). github.base_ref is populated on pull_request events with the base branch name and is empty on push, where the || 'main' default applies; since on.pull_request.branches is [main] (ci.yml:6-7) the expression always resolves to origin/main here. Unexercised: the branch is not pushed (git ls-remote --heads origin feat/self-host is empty) and no Actions run exists, so DoD 7 remains open; this verdict rests on the workflow text and GitHub's documented context semantics, not on an observed run. Note the push-to-main degenerate case filed below.

### Unanchored findings

- **important**: §5.4's installation premise is false twice under the design's own registry: the PostToolUse hook scans whole files (added_lines=None), not changed lines, so any edit to a fixture or a hasattr test re-fires its finding and a BLOCK returns exit 2; and the merged registry carries 7 pre-existing findings, not 4, including a second BLOCK in tests/fixtures/typescript/bad.tsx:4 (fail-loud.empty-catch) that the spec never names or dispositions.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:254`
- **important**: The acf-setup skill's merge rule says a duplicate id across stock profiles 'should not' occur and prescribes stop-and-ask, yet both stock profiles carry ops.no-build-artifacts, so every polyglot bootstrap trips a case the skill denies; the spec attributes the resolution to the skill (C33) and files no follow-up to fix either the skill text or the profiles.
  - evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:110`
- **advisory**: The byte-check covers only the two gate skills, but the hooks execute the cached copy's hooks/ and python/acf (posttooluse_gate.py:22-26 prepends the installed plugin's python dir), and the new ## Release discipline section says 'the installed copy is byte-checked against the clone' without that scope qualifier — stale hook or package code in the cache is unguarded.
  - evidence: `scripts/check_installed_skills.py:18`
- **advisory**: On every push to main the CI step diffs origin/main...HEAD where HEAD is origin/main, so merge-base(HEAD, HEAD) = HEAD and the step can never report; §5.6 describes this as the first run after merge, but it is every push event — only pull_request runs gate anything.
  - evidence: `.github/workflows/ci.yml:40`
- **advisory**: The PYTHONUTF8 note is a rung-5 operator workaround where the rung-3 producer fix is encoding="utf-8" on two subprocess.run calls; the written justification (scope) exists and the doctrine records the debt, but the note plus the doctrine section are longer than the fix they defer.
  - evidence: `plugins/arch-compliance/python/acf/diff.py:28`
- **advisory**: DoD 1 says --collect-only lists 'the three new tests'; the branch adds four in tests/test_self_host.py (a mandate-id uniqueness test the spec does not describe) plus three in tests/test_check_installed_skills.py — the spec and the branch disagree on the acceptance count.
  - evidence: `tests/test_self_host.py:42`
- **advisory**: §5.2 says three stock rows 'are set status: unenforced'; only soft.react-boundaries was changed (stock react-app row is partial) — facade.forbid-sink and fsm.transition-guard arrive unenforced from the stock python-service profile, so the sentence overstates the merge's edits.
  - evidence: `config/architecture/mandates.yml:49`

### Looked for but did not find

- A detector or enforcement path that emits or errors on a detection: manual row — none: acf/detectors contains no 'plugin.' id, _active_mandates matches detector-id constants only, apply_registry filters by finding id; gate run against origin/main returned No findings exit 0
- A repair-on-load or normalizer anywhere in the added files — none; every added mechanism (four tests, CI step, hook marker, byte-check) refuses with a non-zero exit rather than rewriting state
- A code writer of config/architecture/adr.yml — none; /acf-setup's checklist (acf-setup/SKILL.md:20-22) writes mandates.yml, ARCHITECTURE.md and .acf/enabled only; the declaration is hand-authored and the gate's load block refuses a bad one before dispatch
- A change to plugin code on the branch — none; git diff --stat c0281bf..HEAD -- plugins/ is empty, consistent with §3
- A test-module basename collision between tests/ and plugins/arch-compliance/tests/ — none
- A citation-runner git call that decodes file content on Windows — none; check-ignore, rev-parse, rev-list, ls-files return paths and SHAs; only diff.py decodes diff bodies
- An exemption token on the two BLOCK fixtures — none in bad_except.py or bad.tsx, as the spec says for the python fixture; the spec does not address bad.tsx at all

### Mechanism traces

- **self-host test 1 — the declaration loads and names docs/reviews/ (tests/test_self_host.py:22-25)**
  - invalid state: config/architecture/adr.yml is absent, fails AdrHostConfig validation, or its runs_dir / ledger_path do not equal docs/reviews/adr_runs and docs/reviews/adversarial_design_ledger.jsonl
  - producer: `config/architecture/adr.yml:1-2 (hand-authored; no code path writes it — plugins/arch-compliance/skills/acf-setup/SKILL.md:20-22 lists the setup skill's writes as mandates.yml, ARCHITECTURE.md and .acf/enabled)`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:275`
- **self-host test 2 — every arch_anchor is a literal substring of ARCHITECTURE.md (tests/test_self_host.py:28-31)**
  - invalid state: a Mandate row in config/architecture/mandates.yml whose arch_anchor is not a substring of config/architecture/ARCHITECTURE.md
  - producer: `plugins/arch-compliance/skills/acf-setup/SKILL.md:113-116 (the Step 5 prose merge that may rename or drop a heading) and hand edits to either file; plugins/arch-compliance/python/acf/registry.py:37-53 loads rows without checking anchors against the doctrine`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: "the profile-drift check, applied to the host pair instead of the profiles" (spec §5.5 item 2) — a reuse rationale; no rejection of a load-time refusal is written
  - spec citation: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:277`
- **self-host test 3 — every detection: manual row's detector is an existing test module (tests/test_self_host.py:34-39)**
  - invalid state: a row with detection == manual whose detector string is not an existing file under plugins/arch-compliance/tests/
  - producer: `config/architecture/mandates.yml:148-201 (hand-authored rows); plugins/arch-compliance/python/acf/registry.py:49 exempts manual rows from the known-detector check, so the loader accepts any string`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: "the registry row is a pointer from the rule to its enforcement, not a promise of enforcement that does not exist" (spec §5.2) and "No new detector, no change to any detector" (spec §3) — a loader-side refusal would be a plugin code change the spec excludes
  - spec citation: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:280`
- **self-host test 4 — mandate ids are unique (tests/test_self_host.py:42-44; not in the spec)**
  - invalid state: two rows in config/architecture/mandates.yml with the same id
  - producer: `plugins/arch-compliance/profiles/python-service/mandates.yml:34 and plugins/arch-compliance/profiles/react-app/mandates.yml:23 (both stock profiles carry ops.no-build-artifacts, so the /acf-setup union of SKILL.md:109-110 produces the duplicate unless a human intervenes); plugins/arch-compliance/python/acf/registry.py:33-34 by_id silently keeps the last duplicate`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `None`
- **CI step — acf-check-diff against origin/<base> (.github/workflows/ci.yml:39-40)**
  - invalid state: an added line in merge-base(origin/<base>, HEAD)..HEAD of a .py/.ts/.tsx file that matches an enforced BLOCK row's detector and carries no exemption token
  - producer: `any commit on a pull-request branch; the earlier line of defence is the PostToolUse hook at plugins/arch-compliance/hooks/posttooluse_gate.py:254 — CI re-checks what the hook saw per edit, line-scoped via plugins/arch-compliance/python/acf/cli_check_diff.py:121`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:285-286`
- **.acf/enabled marker turning on the PostToolUse Tier-1 gate for this repository's edits**
  - invalid state: an edited .py/.ts/.tsx file whose full text (not only the edited lines) contains a pattern an enforced row's detector flags
  - producer: `every Write/Edit/MultiEdit tool call (plugins/arch-compliance/hooks/hooks.json:18-22); the scan is whole-file at plugins/arch-compliance/hooks/posttooluse_gate.py:254 and :281, which is why the spec's changed-lines framing does not describe this mechanism`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:261-262`
- **installed-skills byte-check before a gate run (scripts/check_installed_skills.py)**
  - invalid state: a file under <installPath>/skills/{adversarial-design-review,responding-to-adversarial-review}/ that is absent or byte-different from the same relative path under plugins/arch-compliance/skills/
  - producer: `the plugin cache copy at C:/Users/iball/.claude/plugins/cache/arch-compliance-for-superpowers/arch-compliance/0.2.0/skills, written by `claude plugin install` (hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md:664-677 Task 8 step 1 context) and left behind when plugins/arch-compliance/skills/ changes in the clone`
  - rung 5 (highest applicable 5); repairs=False
  - hardening rejected because: "Byte-check before the run (§5.3); reinstall on mismatch, as 1d does" (spec §9 risk table) — the cache is Claude Code's, a boundary outside this tree
  - spec citation: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:250`
- **CLAUDE.md Windows note — run the diff gate with PYTHONUTF8=1**
  - invalid state: git diff output containing a byte sequence outside the host locale codec (cp1252) decoded by subprocess.run(text=True) without an encoding argument
  - producer: `plugins/arch-compliance/python/acf/diff.py:24-30 (run_git: text=True, no encoding) and plugins/arch-compliance/python/acf/adr/citations.py:62-65 (same shape; its callers decode only paths and SHAs)`
  - rung 5 (highest applicable 3); repairs=False
  - hardening rejected because: "this spec's theme is declaration and doctrine, not the git runner" (spec §3) and "One plan, no spec: a defect with a test" (spec §9 follow-up 1)
  - spec citation: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:255`
- **status: unenforced on stock rows whose surface does not exist here (guard flag)**
  - invalid state: a finding with mandate_id in {soft.react-boundaries, facade.forbid-sink, fsm.transition-guard} reported for a repository with no React views, no index.yml façade and no state field
  - producer: `plugins/arch-compliance/python/acf/cli_check_diff.py:112-113,128-150 (facade and fsm scans run for every active row) and the LLM judge for soft.react-boundaries; _active_mandates excludes unenforced rows so no finding is produced (cli_check_diff.py:94-99, enforcement.py:47)`
  - rung 1 (highest applicable 1); repairs=False
  - hardening rejected because: "not deleted, so the file stays diffable against the profile" (spec §5.2)
  - spec citation: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:180`

## Claims

- **C1** [premise] [load-bearing]: Before this branch (plugin main c0281bf, the spec pins 8dabe82 with identical plugin files) this repository had no doctrine and no declaration: config/architecture/ was absent, .acf/enabled was absent and gitignored, and README.md was the only root document.
  - spec citation: `.gitignore:8`
- **C2** [premise] [load-bearing]: The host contract reads two declared values and the doctrine path (plugins/arch-compliance/python/acf/adr/host.py:19-32); the compliance reviewer reads config/architecture/ARCHITECTURE.md in full and every document it points to, and checks a doctrine's self-declared high-frequency misses first (plugins/arch-compliance/skills/adversarial-design-review/reviewers/compliance.md:12,47).
  - spec citation: `plugins/arch-compliance/python/acf/adr/host.py:19-32`
- **C3** [premise] [load-bearing]: /acf-setup writes config/architecture/mandates.yml and ARCHITECTURE.md from a profile and merges both profiles into one pair for a two-language host (plugins/arch-compliance/skills/acf-setup/SKILL.md:90-118); this repository has Python under plugins/arch-compliance/python/ and TypeScript with its own package.json under plugins/arch-compliance/detectors/typescript/.
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:90-118`
- **C4** [premise]: The python-service profile run over this repository's whole history (--base dfff93f5, the root commit) reports 4 findings: 1 BLOCK fail-loud.bare-except in plugins/arch-compliance/tests/fixtures/python/bad_except.py and 3 WARN no-shims.hasattr in three test modules; the package itself reports none.
  - spec citation: `plugins/arch-compliance/tests/fixtures/python/bad_except.py`
- **C5** [premise] [load-bearing]: The registry schema accepts detection: manual rows and requires a detector string on every row, but checks that string against known detectors only for ast and guard rows (plugins/arch-compliance/python/acf/registry.py:8-18,49), so a manual row can name the test that enforces it.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:8-18,49`
- **C6** [premise] [load-bearing]: run_git (plugins/arch-compliance/python/acf/diff.py:24-30) and the citation module's own runner (plugins/arch-compliance/python/acf/adr/citations.py:62-65) decode git output with the locale codec (text=True, no encoding), so on a Windows node with a cp1252 locale a diff containing a character outside cp1252 raises inside the subprocess reader thread; CI runs on Linux and is unaffected.
  - spec citation: `plugins/arch-compliance/python/acf/diff.py:24-30`
- **C7** [premise]: At c0281bf CI runs pytest only (.github/workflows/ci.yml:34-35); the diff gate is not run on this repository's own changes.
  - spec citation: `.github/workflows/ci.yml:34-35`
- **C8** [premise] [load-bearing]: The plugin's acceptance test for a non-origin host builds a fixture host in a temporary directory and exercises the storage path through the Python API (plugins/arch-compliance/tests/test_adr_host_acceptance.py:74-96); it is not a live skill run from the installed plugin.
  - spec citation: `plugins/arch-compliance/tests/test_adr_host_acceptance.py:74-96`
- **C9** [premise]: HM's workstream exit criterion 5 names Cayenne as the second repository and says it proves the objective rather than approximating it (hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:5264-5269 at the spec's pinned HM commit; the lines have since moved).
  - spec citation: `hm:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md:5264-5269`
- **C10** [premise] [load-bearing]: Deferral: the plugin's hooks fire on every subagent start and every Write/Edit in every repository where the plugin is installed and no-op without .acf/enabled (plugins/arch-compliance/hooks/hooks.json; plugins/arch-compliance/hooks/posttooluse_gate.py:72-76), so writing the marker here turns the PostToolUse gate on for this repository's own edits and nothing else changes.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:72-76`
- **C11** [premise]: At c0281bf the test suite is collected from the single testpaths entry plugins/arch-compliance/tests (pyproject.toml) and the plugin version is 0.2.0 (plugins/arch-compliance/.claude-plugin/plugin.json:3, pyproject.toml:3).
  - spec citation: `pyproject.toml`
- **C12** [premise] [load-bearing]: Deferral: the git-runner decoding defect can stay a filed follow-up during this phase because CI runs on Linux and the spec's own commands run with PYTHONUTF8=1 on Windows (the note is in CLAUDE.md), so no step of this design depends on the fix.
  - spec citation: `plugins/arch-compliance/python/acf/diff.py:24-30`
- **C13** [premise] [load-bearing]: Deferral: HM's ledger holds 21 records for plugin-related specs, matched to HM spec paths; because the ledger is append-only and nothing migrates, leaving those rows in HM and placing a stub at the moved spec's HM path keeps them resolving.
  - spec citation: `hm:docs/design/ADR_GATE_HOST_CONTRACT.md:80-81`
- **C14** [premise] [load-bearing]: The gate's citation resolver has no notion of another repository: a prefixed path classifies unresolved (plugins/arch-compliance/python/acf/adr/citations.py:129-187) and an unresolved citation hard-fails before dispatch (plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:76-82,101); HM's host-contract runs handled acf: citations by the controller mapping them to the sibling checkout (hm:docs/reviews/adr_runs/ADR_GATE_HOST_CONTRACT_v3_2026-10-12.md:28,35,247).
  - spec citation: `plugins/arch-compliance/python/acf/adr/citations.py:129-187`
- **C15** [premise]: The plugin's existing design document states five portable governing principles at docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-52, including fail loud, no shims, POSIX paths, registry-is-the-spine and the Superpowers override contract.
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-52`
- **C16** [premise]: The rules the doctrine lifts from HM's GEMINI.md exist at the cited lines: the three fail-loud sentences at hm:GEMINI.md:102-106, the no-shims sentence at :110-112, scoped refactor at :129, single point of definition at :134, and the two POSIX-path sentences at :190-194.
  - spec citation: `hm:GEMINI.md:102-106`
- **C17** [premise] [load-bearing]: Deferral: the 1d plan's Task 8 step 1 block (hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md, Task 8) is a byte-for-byte comparison of the installed gate skills against the clone, so scripts/check_installed_skills.py reproduces an algorithm that already exists rather than inventing one.
  - spec citation: `hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md`
- **C18** [mandate] [load-bearing]: Registry is the spine (docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:49, now restated by config/architecture/ARCHITECTURE.md): each plugin-specific rule that an existing test enforces is a mandates.yml row whose detector names that test module, every row's arch_anchor is a literal heading of ARCHITECTURE.md, and tests/test_self_host.py pins both.
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:49`
- **C19** [mandate]: Declared, never defaulted (the doctrine's own section; 1c decision 4): config/architecture/adr.yml declares both storage values and no default re-enters in acf.adr.host for a missing declaration.
  - spec citation: `plugins/arch-compliance/python/acf/adr/host.py:22-27`
- **C20** [mandate]: POSIX paths (doctrine ## POSIX paths; principle 3): adr.yml carries relative forward-slash paths and the model types them PosixStr, refusing a backslash.
  - spec citation: `plugins/arch-compliance/python/acf/adr/host.py:22-27`
- **C21** [mandate] [load-bearing]: No shims (doctrine ## No shims; principle 2): CLAUDE.md is a pointer and process file, not a second doctrine, and ARCHITECTURE.md points to the design document's five principles rather than restating them, so there is one rules document and one registry.
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-52`
- **C22** [mandate] [load-bearing]: The Superpowers override contract (principle 5, 'document that explicitly') is met by CLAUDE.md recording the spec and plan locations, the gate as brainstorming's terminal state with BLOCKED returning through the responding skill, and the citation convention.
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:51`
- **C23** [mandate]: The doctrine's ## No completeness claims rule is applied to this spec itself: its definition of done is eight per-item, falsifiable checks rather than a universal, and its census (section 4.1) lists what was found by command rather than asserting that nothing else exists.
  - spec citation: `plugins/arch-compliance/skills/adversarial-design-review/claims/extraction.md:71`
- **C24** [shape_fit] [load-bearing]: The design extends the host contract as designed (one declaration file at config/architecture/adr.yml and the fixed doctrine path) and the /acf-setup bootstrap, and creates no second way to declare a host or to express a rule: the plugin's own rules are mandates.yml rows in the plugin's own registry format, not a second kind of rules document.
  - spec citation: `docs/design/ADR_GATE_HOST_CONTRACT.md`
- **C25** [shape_fit] [load-bearing]: tests/test_self_host.py duplicates no existing check: plugins/arch-compliance/tests/test_profile_drift.py checks the shipped profiles' anchors, not the host pair, and nothing else in the repository checks the host declaration, the host registry's anchors, the manual rows' detector paths or mandate-id uniqueness.
  - spec citation: `plugins/arch-compliance/tests/test_profile_drift.py`
- **C26** [shape_fit] [load-bearing]: scripts/check_installed_skills.py has one owner in this repository: no existing script or test compares the installed plugin cache against the clone; the only prior form of the comparison is an inline block in HM's 1d plan, outside this repository.
  - spec citation: `hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md`
- **C27** [sweep] [load-bearing]: Pattern sweep for specs about the plugin living in another repository: the hits are the eight files in HM's docs/design matching ADR_* or ARCH_COMPLIANCE_*; of these the host contract moves here, the 1d cutover stays because its change surface is HM's, and the six named in section 10 stay beside their ledger rows as superseded, draft or stub documents.
  - spec citation: `hm:docs/design/ADR_GATE_HOST_CONTRACT.md:80-81`
- **C28** [sweep]: The three stock rows set unenforced (facade.forbid-sink, fsm.transition-guard, soft.react-boundaries) have no live subject in this repository (no index.yml writer, no state field written under a validator, no React view), while the other stock rows do.
  - spec citation: `plugins/arch-compliance/profiles/python-service/mandates.yml`
- **C29** [implementability] [load-bearing]: tests/test_self_host.py at the repository root is collected and imports acf: pyproject.toml's pythonpath entry serves the root tests directory once testpaths gains it, and load_host_config(ROOT) accepts the spec's adr.yml.
  - spec citation: `pyproject.toml`
- **C30** [implementability] [load-bearing]: A detection: manual row whose detector is a test-module path loads through load_mandates with the known-detector check and produces neither a finding nor an error in the diff gate: detectors emit findings by mandate id for ast and guard rows only, and apply_registry only filters (plugins/arch-compliance/python/acf/cli_check_diff.py; plugins/arch-compliance/python/acf/enforcement.py).
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:8-18,49`
- **C31** [implementability] [load-bearing]: python -m acf.cli_check_diff --repo . --base origin/<base> runs in CI with fetch-depth 0 and reads the host registry at config/architecture/mandates.yml by default (acf.repo.MANDATES_REL), exiting non-zero only on a BLOCK finding on changed lines.
  - spec citation: `.github/workflows/ci.yml:34-35`
- **C32** [implementability] [load-bearing]: claude plugin list --json reports the installed plugin's installPath, under which skills/ holds the same relative files as the clone's plugins/arch-compliance/skills/, so a file-by-file byte comparison (scripts/check_installed_skills.py) is well defined.
  - spec citation: `hm:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md`
- **C33** [implementability] [load-bearing]: /acf-setup, run from this repository's root, detects both languages and offers one merged pair, and the duplicate id ops.no-build-artifacts across the two stock profiles resolves to one row with languages: both (plugins/arch-compliance/skills/acf-setup/SKILL.md:105-118).
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:105-118`
- **C34** [mechanism_justification] [load-bearing]: Bootstrapping the host pair through /acf-setup rather than hand-writing it is justified: it exercises the setup skill on a real host and keeps the pair diffable against the stock profiles (every stock anchor verbatim, non-applicable rows kept as status: unenforced rather than deleted).
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:90-118`
- **C35** [mechanism_justification] [load-bearing]: Giving a registry row only to the doctrine sections an existing test already enforces (five sections) and leaving the other four as prose marked 'no row' is justified because a row is a pointer from rule to enforcement, not a promise of enforcement; no row names a future test, so the self-host test's detector check holds on merge day.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:8-18,49`
- **C36** [mechanism_justification] [load-bearing]: Making the acceptance run the spec's own binding review (decision 5) rather than reviewing the spec elsewhere first is justified because the doctrine the spec proposes cannot be read by the gate until this branch declares it, and the doctrine's first test is whether four blind reviewers can hold this design to it.
  - spec citation: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md`
- **C37** [mechanism_justification]: Filing the git-runner decoding defect as a follow-up rather than fixing it here is justified: the fix is a code change outside the spec's theme (declaration and doctrine), CI is on Linux, and the CLAUDE.md PYTHONUTF8 note covers Windows until the fix lands.
  - spec citation: `plugins/arch-compliance/python/acf/diff.py:24-30`
- **C38** [implementability] [load-bearing]: With .acf/enabled present the PostToolUse gate runs the Tier-1 detectors on this repository's edits; the four pre-existing findings sit on lines no future edit touches unless it edits them, and the bare-except fixture carries no exemption token because the detector tests need it unmodified, so the gate blocks nothing on the day this merges.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:72-76`
- **C39** [implementability] [load-bearing]: The CI step's base expression origin/${{ github.base_ref || 'main' }} resolves to the PR's base branch on pull_request events and to main on push events, so acf-check-diff always has a merge-base to diff against with fetch-depth 0.
  - spec citation: `.github/workflows/ci.yml:34-35`
