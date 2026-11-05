# Adversarial design review — full detail

Spec: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md` @ `ac526748ac3877dfab9b45884928aaee03b371fc`
Kinds: defect, feature
Outcome: **BLOCKED**
Claims: 103 · Reviewers: 4 · Converged: 2

## Blocking reasons

- load-bearing claim C61 (shape_fit) is REFUTED: I searched by behaviour: a host-declared path string joined under the repository root. The ratchet joins are one such site, but not the only other one. AdrHostConfig.runs_dir and ledger_path are host-declared relative path strings, validated only by PosixStr (backslashes refused; absolute paths and '..' segments allowed). The gate skill, the housekeeping skill and test_adr_host_acceptance.py:85,90 join them as `repo / cfg.runs_dir` and `repo / cfg.ledger_path` with no absolute or containment test. That is the same job as validate_posix_rel_path plus resolve_under_root. The claim's sweep was keyed to 'registry' paths and missed this host-config owner, so the debt list in §3/§4.8 is incomplete.
- load-bearing claim C72 (shape_fit) is UNPROVEN: The design is proposed, so I have no implementation site to resolve. The no-conftest half holds: Glob finds no conftest.py anywhere, so fresh_host_loader would be the only reset. The 'exactly two regions' half is doubtful. Both handlers format `{exc}` inside the except block, which calls the host exception's __str__ outside the try. _to_findings reads hit.path on what may be a host subclass of HostHit. Either path can run host code that raises unwrapped.
- mandate claim C52 is REFUTED: ARCHITECTURE.md:161-164 says a claim about the tree cannot rest on 'only' or 'no second' unless a re-runnable recipe backs the quantifier, and :221 lists this as the first high-frequency miss. The §6 Single point of definition row (spec :486) says 'One breach remains, recorded in the doctrine: the ratchet's path joins'. That is a census of the remaining breaches with no recipe and no per-item table behind it. The Appendix has no breach-census row. It is also false (see C55). So not every population claim carries a recipe.
- mandate claim C55 is REFUTED: The doctrine requires one canonical implementation of any procedure needed by more than one module, and it requires current breaches to be 'recorded not hidden'. The claim says that within the Tier-1 gates 'the one remaining breach' is the ratchet's path joins. Inside the two Tier-1 gates, however, the procedure that turns a row's params into scanner kwargs is implemented twice, token for token: target_literal_re default '', allowlist_globs [], atomic_is_sink True, state_field and validator_name ''. It is at cli_check_diff.py:128-150 and posttooluse_gate.py:255-277, and the build-artifact path_prefixes extraction is duplicated at :158-166 and :284-294. The design edits exactly these loops: it replaces their filters with registry.active and adds the host calls. Yet it neither consolidates the duplication nor adds it to the doctrine's breach list (§4.8 adds only the ratchet). So the claim that only one breach remains is false.
- mandate claim C56 is REFUTED: The doctrine says to remove non-contractual patterns 'in code paths you are changing' and not to expand scope to unrelated modules. The design changes no ADR-gate behaviour except through this consolidation, yet it rewrites citations.py's resolve_citation (:161-167) to use engine helpers. That also changes ADR-gate classification: 'C:a/b.py' becomes external, and a symlink loop now classifies as unresolved instead of raising. So the claim that the consolidations touch only paths the design changes is false for citations. The spec applies the opposite test elsewhere: it leaves the ratchet's identical path joins alone 'because the ratchet is otherwise untouched here' (spec :89). By that same test, the acf.adr consolidation is out of scope.

## Absorptions

- PARTIAL_OVERLAP: 'KNOWN_DETECTORS mapping (acf.detectors)' shares responsibility 'enumerate the built-in Tier-1 detector ids' with plugins/arch-compliance/python/acf/detectors/__init__.py:28 — Make KNOWN_DETECTORS the single definition of the built-in id set. Either derive ALL_PYTHON_DETECTOR_IDS, GUARD_DETECTOR_IDS, PYTHON_AST_DETECTOR_IDS and TS_DETECTOR_IDS from it (by contract field, or by adding a detection kind to BuiltinDetector), or delete whichever lose their last runtime consumer. The equality test then becomes unnecessary.
- IDENTICAL: 'TS_MANDATE_IDS' shares responsibility 'enumerate the TypeScript detector ids' with plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:14 — Set TS_DETECTOR_IDS = frozenset(TS_MANDATE_IDS), or drop it, so the TS id set is spelled once.
- PARTIAL_OVERLAP: 'validate_posix_rel_path / resolve_under_root' shares responsibility 'validate a host-declared relative path string and contain it under the root' with plugins/arch-compliance/python/acf/adr/host.py:24-25 — AdrHostConfig.runs_dir and ledger_path should validate through validate_posix_rel_path, and their joins should go through resolve_under_root. At minimum, record them beside the ratchet as a ## Single point of definition breach.
- PARTIAL_OVERLAP: 'looks_absolute / resolve_under_root' shares responsibility 'registry path string to a file under the root' with plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:122-124 — The ratchet's baseline and roots joins become resolve_under_root consumers (recorded by the spec as debt).
- SUBSUMED: 'looks_absolute / resolve_under_root' shares responsibility 'absolute-path and escape tests on a cited path' with plugins/arch-compliance/python/acf/adr/citations.py:49-51 — Delete citations' private helpers; citations.py:161,:163 call the acf.engine helpers.
- SUBSUMED: 'Mandate.runs_at / MandateRegistry.active' shares responsibility 'decide which rows run at a Tier-1 gate' with plugins/arch-compliance/python/acf/cli_check_diff.py:94-99 — _active_mandates, the hook's three inline filters and apply_registry's status check all call runs_at/active.
- IDENTICAL: 'make_line_lookup' shares responsibility 'map (path, line) to source text for exemption checks' with plugins/arch-compliance/python/acf/cli_check_diff.py:76-80 — Delete both gate closures (cli_check_diff.py:76-80, posttooluse_gate.py:119-123); both gates call make_line_lookup.
- PARTIAL_OVERLAP: 'KNOWN_DETECTORS call_sites' shares responsibility 'declare at which gate each built-in detector runs' with plugins/arch-compliance/python/acf/cli_check_diff.py:168-182 — Accepted two-owner arrangement tied by the contract-against-dispatch test. A shared dispatcher reading the contract would collapse it, and the spec lists that as a non-goal.

## Converged findings

- [3 reviewers: compliance, hardening, refuter] scan_host_guards maps only some unreadable flagged paths to []: a missing file (no is_file check after a non-strict resolve), a directory, or a symlink loop on Python 3.13 reaches read_text, raises OSError and fails the gate as DetectorPackError instead of leaving the finding in place.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:353`
- [2 reviewers: compliance, sweeper] KNOWN_DETECTORS' keys become a second definition of the built-in detector-id set; ALL_PYTHON_DETECTOR_IDS and TS_DETECTOR_IDS (and the sets they are built from) lose their only runtime consumer at cli_check_diff.py:25 and are left as test-only exports.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:25`
  - evidence: `plugins/arch-compliance/python/acf/detectors/__init__.py:11-28`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:48-64; plugins/arch-compliance/python/acf/registry.py:58; plugins/arch-compliance/python/acf/registry.py:60-63; plugins/arch-compliance/tests/test_registry.py:20-30`
- reasoning: I read load_mandates. Line 58 skips any row whose status is not 'enforced'. Line 60 raises UnknownDetectorError only when the detection is ast or guard and the detector is not in known_detectors. test_registry.py:20-30 pins the enforced unknown-detector case.

#### C2 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:47; plugins/arch-compliance/python/acf/cli_check_diff.py:98; plugins/arch-compliance/hooks/posttooluse_gate.py:231; plugins/arch-compliance/hooks/posttooluse_gate.py:285; plugins/arch-compliance/python/acf/registry.py:58`
- reasoning: Each link holds. apply_registry drops only 'unenforced' rows. Both gates filter rows with != 'unenforced'. load_mandates skips every non-enforced row, so a partial row is never checked against known_detectors. A partial row naming a non-built-in id therefore loads, and no scanner dispatches on that id.

#### C3 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:25; plugins/arch-compliance/python/acf/judge.py:29-36; plugins/arch-compliance/python/acf/registry.py:60`
- reasoning: The recipe git grep KNOWN_DETECTORS finds only the definition, the load_mandates pass, skill prose and imports in tests. Nothing extends the set. Executing len(KNOWN_DETECTORS) prints 13, including the 4 llm_* ids. registry.py:60 checks only membership, so an enforced ast row naming llm_fail_loud passes.

#### C4 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; plugins/arch-compliance/python/acf/cli_check_diff.py:124-182; plugins/arch-compliance/hooks/posttooluse_gate.py:229-236; plugins/arch-compliance/hooks/posttooluse_gate.py:284-286`
- reasoning: The git grep for importlib, import_module, spec_from_file_location and exec_module over python/ and hooks/ printed nothing. Both scan functions call only imported built-in scanners. One nuance: scan_python_file and scan_typescript_file run on every code file without row selection, while only the facade, fsm, build and ratchet scanners are selected by id. That does not affect the claim that no non-built-in detector can run.

#### C5 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:107; plugins/arch-compliance/hooks/posttooluse_gate.py:229-236`
- reasoning: The hook calls load_mandates(mandates_path) with no known_detectors argument. An unknown id therefore loads, matches no scanner, and yields no findings.

#### C6 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:108; plugins/arch-compliance/python/acf/exceptions.py:5; plugins/arch-compliance/python/acf/exceptions.py:13`
- reasoning: The hook catches only AcfInputError around the load. UnknownDetectorError subclasses AcfError directly, so it would escape as a traceback unless the hook also catches it.

#### C7 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:21; plugins/arch-compliance/python/acf/adr/ledger.py:42; plugins/arch-compliance/python/acf/adr/ledger.py:83; plugins/arch-compliance/python/acf/enforcement.py:47`
- reasoning: I ran the recipe grep. It prints exactly registry.py:21 and the two surface_call_sites lines in ledger.py. apply_registry tests only status.

#### C8 — SURVIVED
- evidence: `config/architecture/mandates.yml:70; plugins/arch-compliance/tests/fixtures/mandates_valid.yml:18; plugins/arch-compliance/tests/test_hooks.py:199-217; plugins/arch-compliance/tests/test_hooks.py:55-62`
- reasoning: The no-shims.hasattr row declares [ci] in both the repository registry and the fixture. _seed_host copies the fixture. The test asserts that 'no-shims.hasattr' appears in the hook's additionalContext. It is reported because scan_python_file runs unconditionally and apply_registry ignores call_sites.

#### C9 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80; plugins/arch-compliance/hooks/posttooluse_gate.py:119-123; plugins/arch-compliance/python/acf/cli_check_diff.py:126; plugins/arch-compliance/python/acf/cli_check_diff.py:152; plugins/arch-compliance/hooks/posttooluse_gate.py:248-252; plugins/arch-compliance/python/acf/enforcement.py:49-50`
- reasoning: The two closures are token-identical. file_lines is filled only in the .py and .ts/.tsx branches, and the hook skips non-code suffixes at :248. Any other path returns ''.

#### C10 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_import_graph.py:70-76; plugins/arch-compliance/python/acf/adr/contract.py:20; plugins/arch-compliance/hooks/posttooluse_gate.py:92-95; plugins/arch-compliance/python/acf/engine.py:6-8`
- reasoning: The test checks only for the literal text 'acf.adr' in the hook files. The hook imports acf.enforcement and acf.registry. contract.py imports acf.engine. acf.engine imports only pathlib and never acf.adr.

#### C11 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:213-218; plugins/arch-compliance/python/acf/cli_check_llm.py:54-66`
- reasoning: run_judge selects rows by detection == 'llm' and uses status == 'enforced' only for has_enforced. cli_check_llm passes registry.mandates unfiltered. No Tier-1 filter is involved.

#### C12 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:72-81; plugins/arch-compliance/hooks/posttooluse_gate.py:28; plugins/arch-compliance/python/acf/repo.py:9`
- reasoning: Before the marker check, the hook imports only argparse, json, sys, pathlib and acf.repo, and acf.repo imports only pathlib. The acf package __init__ is empty. The return 0 at :81 comes before the mandates load and the deferred imports at :91.

#### C13 — SURVIVED
- evidence: `.gitignore:8; .github/workflows/ci.yml:40; plugins/arch-compliance/python/acf/cli_check_diff.py:22`
- reasoning: .acf/ is ignored. CI runs python -m acf.cli_check_diff. cli_check_diff imports MANDATES_REL, RATCHET_BASELINE_REL and resolve_repo, never ENABLED_REL, and grep finds no marker check there.

#### C14 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:103-107; plugins/arch-compliance/python/acf/cli_check_llm.py:54`
- reasoning: inject_constraints wraps load_mandates in except AcfInputError and returns 1. cli_check_llm calls load_mandates bare, so an AcfInputError escapes and the process exits non-zero, as today.

#### C15 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:90-92; plugins/arch-compliance/python/acf/cli_check_llm.py:10-13`
- reasoning: inject_constraints imports only acf.exceptions, acf.registry and acf.loader. cli_check_llm imports acf.finding, acf.judge, acf.registry and acf.repo. Neither imports acf.detectors, so under the design neither reaches host.py.

#### C16 — SURVIVED
- evidence: `plugins/arch-compliance/skills/architecture-review/SKILL.md:62`
- reasoning: git ls-files plugins/arch-compliance/python/acf | grep -i review printed nothing (exit 1). Architecture-review exists only as skill markdown files.

#### C17 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:20; plugins/arch-compliance/python/acf/registry.py:24`
- reasoning: git show b652fab05:config/architecture/mandates.yml in HistoricMansions has 48 rows. grep for 'languages' or 'arch_anchor' matches nothing. The rows use gemini_anchor, and Mandate requires both fields.

#### C18 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/arch_compliance/driver.py:144; C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/arch_compliance/driver.py:151-161; C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/arch_compliance/driver.py:92; plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37`
- reasoning: The driver sets fail_loud_unparseable = mode == 'range' and otherwise appends a WARN Finding with exc.lineno or 0. Its guards consume cf.content, the staged, HEAD or range blob (docstring at :92). The built-in scanner returns [] on SyntaxError.

#### C19 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:198-200; plugins/arch-compliance/python/acf/cli_check_diff.py:121; plugins/arch-compliance/hooks/posttooluse_gate.py:254; plugins/arch-compliance/hooks/posttooluse_gate.py:177-210`
- reasoning: The quote is accurate. The two loops do differ: the diff gate uses added lines and changed_files(), while the hook passes added_lines=None and collects paths from argv and stdin. One overstatement: the file filter is the same in both loops (.py, .ts, .tsx). The real filter-side difference is build artifacts: the diff gate passes every changed path, deletions included, and the hook passes only existing files.

#### C20 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37`
- reasoning: try: ast.parse(text) except SyntaxError: return [].

#### C21 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:104; plugins/arch-compliance/tests/test_registry.py:30; tests/test_self_host.py:23; plugins/arch-compliance/skills/architecture-review/SKILL.md:62`
- reasoning: I ran the recipe grep. It prints exactly the listed sites, including test_registry.py:10,17,30,47,57 and the prose at SKILL.md:141. Only cli_check_diff:70, acf-mandate SKILL.md:95, test_profile_drift:24, test_registry:30 and test_self_host:23 pass known_detectors.

#### C22 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:125; plugins/arch-compliance/python/acf/cli_check_diff.py:82; plugins/arch-compliance/tests/test_enforcement.py:54`
- reasoning: git grep 'apply_registry(' prints the two gate calls and the ten test_enforcement lines listed, besides the definition at enforcement.py:37.

#### C23 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; plugins/arch-compliance/hooks/posttooluse_gate.py:231; plugins/arch-compliance/hooks/posttooluse_gate.py:285; plugins/arch-compliance/python/acf/judge.py:218; plugins/arch-compliance/hooks/inject_constraints.py:158`
- reasoning: I ran both recipes. The output matches exactly: cli :94,98,112,113,158,168; hook :231,235,285; enforcement :47. The wider .status recipe adds registry.py:58, judge.py:218 and inject_constraints.py:158.

#### C24 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/build_artifacts.py:31; plugins/arch-compliance/python/acf/detectors/python_pack.py:97; plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23; plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15; plugins/arch-compliance/python/acf/enforcement.py:46`
- reasoning: I grepped every Finding( in the detectors. Each Python construction uses a literal mandate_id at the listed lines. The bridge copies item['mandate_id'] (typescript_bridge.py:85), which the Node rules stamp as literals. apply_registry looks rows up by finding.mandate_id.

#### C25 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:168-182; plugins/arch-compliance/hooks/posttooluse_gate.py:213-295; plugins/arch-compliance/hooks/posttooluse_gate.py:254; plugins/arch-compliance/hooks/posttooluse_gate.py:278-282`
- reasoning: The hook's _scan_paths imports no ratchet module and has no ratchet call. Every table line in section 4.3 matches the code: cli :127, :128-150, :153-156, :158-166; hook :254, :255-277, :278-282, :284-294.

#### C26 — SURVIVED
- evidence: `config/architecture/mandates.yml:70; plugins/arch-compliance/tests/fixtures/mandates_valid.yml:18; plugins/arch-compliance/tests/test_registry.py:24-25; plugins/arch-compliance/tests/test_diff_cli.py:74-77; plugins/arch-compliance/tests/test_hooks.py:223-225`
- reasoning: I executed a census script implementing _row_shape and _check_builtin over the repository registry, both profiles and the fixture. No row was flagged for host ref, missing Tier-1 site, unknown detector, id mismatch or unserved site. The inline rows also pass: test_diff_cli [ci, hook], test_registry manual [audit], test_judge llm, and test_registry not_a_real_detector, which is meant to raise UnknownDetectorError. The only edit of a copied fixture is test_hooks.py:223, which replaces status: enforced with unenforced. Direct Mandate construction is ast [ci] (test_enforcement) or llm.

#### C27 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/loader.py:70-73; plugins/arch-compliance/python/acf/registry.py:33-41; plugins/arch-compliance/tests/test_registry.py:40-47; plugins/arch-compliance/tests/test_enforcement.py:19-29; plugins/arch-compliance/tests/test_template.py:73-80`
- reasoning: load_model_file catches only ValidationError, and AcfInputError is not a ValueError, so pydantic does not wrap it. test_registry:40-47 pins that _unique_ids raises AcfInputError. Direct constructions are ast with call_sites [ci] (Tier-1 present) or llm (skipped by _row_shape).

#### C28 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_profile_drift.py:24; tests/test_self_host.py:23; plugins/arch-compliance/skills/acf-mandate/SKILL.md:112; plugins/arch-compliance/tests/test_registry.py:30`
- reasoning: Every use either imports the name, passes it to load_mandates, calls sorted() on it (works on Mapping keys) or names it in prose. No set operations, | or membership on values. test_registry:30 passes a frozenset, which has no .get().

#### C29 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:63; plugins/arch-compliance/hooks/posttooluse_gate.py:65; plugins/arch-compliance/hooks/hooks.json`
- reasoning: Each main() resolves one repo. hooks.json starts a fresh python process for each PostToolUse event.

#### C30 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:25; plugins/arch-compliance/python/acf/detectors/python_pack.py:16-22; plugins/arch-compliance/python/acf/detectors/__init__.py:11-18; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:14`
- reasoning: Executed, it printed 13 ids: 3 python_pack, 4 guard, 2 TypeScript and 4 llm. Removing the llm ids leaves 9.

#### C31 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/citations.py:49-51; plugins/arch-compliance/python/acf/adr/citations.py:74-76; plugins/arch-compliance/python/acf/adr/citations.py:161; plugins/arch-compliance/python/acf/adr/citations.py:163`
- reasoning: git grep finds code references only at :49, :74, :161 and :163, and no test uses them. The old regex requires a separator after 'X:'; the new one does not, so only drive-relative strings newly become external. One further behaviour change is not a classification change: on 3.11/3.12 a symlink-loop citation used to raise RuntimeError from _escapes_repo and now classifies as unresolved (see unanchored finding).

#### C32 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80; plugins/arch-compliance/hooks/posttooluse_gate.py:119-123; plugins/arch-compliance/python/acf/cli_check_diff.py:152`
- reasoning: The proposed make_line_lookup body matches the closures token for token and does no I/O. The section 4.6 wiring adds file_lines entries only through scan_host_guards. The TypeScript-branch rebinding stores the same text.

#### C33 — SURVIVED
- evidence: `config/architecture/mandates.yml:70; plugins/arch-compliance/tests/fixtures/mandates_valid.yml:18; plugins/arch-compliance/python/acf/cli_check_diff.py:94-99`
- reasoning: In my executed census, every active ast or guard row in every shipped registry declares ci, and all declare hook except no-shims.hasattr. That row is [ci] in the repository registry, the python-service profile and the fixture.

#### C34 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:60; plugins/arch-compliance/python/acf/cli_check_diff.py:21; plugins/arch-compliance/tests/test_profile_drift.py:24`
- reasoning: known_detectors is consulted only under detection in {ast, guard}. No KNOWN_DETECTORS consumer inspects llm rows.

#### C35 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:67; plugins/arch-compliance/tests/test_hooks.py:196`
- reasoning: git grep of the tests for scanner filenames, getsource or reads of the detectors directory found nothing. Tests assert only the emitted id values, which the constants keep.

#### C36 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:29-36; config/architecture/mandates.yml:70; plugins/arch-compliance/tests/test_judge.py:389-392`
- reasoning: In my census, the active llm rows are soft.fail-loud (llm_fail_loud) and the profiles' soft.react-boundaries (llm_react_boundaries). All are in LLM_PROMPT_IDS. The inline test_judge row is unenforced.

#### C37 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:72; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:319-330`
- reasoning: Executed: getattr(m, 'f', None) with a module __getattr__ raising RuntimeError lets the error escape; raising AttributeError returns None. In the spec block, a failed exec leaves _MODULE_CACHE unset, so the guard pops the module from sys.modules. A failed lookup on a cached module keeps it. cli_check_diff.py:72 catches UnknownDetectorError.

#### C38 — SURVIVED
- evidence: `pyproject.toml:5; C:/Python313/Lib/pathlib/_local.py:664-670`
- reasoning: requires-python >=3.11. CPython 3.11 Lib/pathlib.py (fetched from upstream) has resolve() call stat() in non-strict mode, and check_eloop raises RuntimeError('Symlink loop'). Python 3.13 resolve is plain realpath with no RuntimeError. On 3.13 the guard-file case differs (see unanchored finding).

#### C39 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:82-95; plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23; plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:28; plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15; plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:22`
- reasoning: The try runs from :82 to :93, and except (KeyError, TypeError, ValueError) re-raises DetectorPackError at :94-95. The Node rules emit detector 'empty_catch' with mandate 'fail-loud.empty-catch', and 'explicit_any' with 'no-shims.explicit-any', which matches TS_MANDATE_IDS.

#### C40 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:22-28; plugins/arch-compliance/hooks/hooks.json; pyproject.toml:19-20; .github/workflows/ci.yml:40; C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/metadata_facade_guard.py:66`
- reasoning: The hook runs as a script, so the host root is not on sys.path. The console script and python -m behave as stated. The HM guard does from scripts.ci.arch_compliance.facade_sinks import, which resolves once the root is on the path. One imprecision: sys.path.insert(0, python/) puts the plugin's python/ before the hooks directory, not after it as the table says. The conclusion is unaffected.

#### C41 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:29-61; plugins/arch-compliance/hooks/hooks.json`
- reasoning: argparse offers --mode, --base, --repo, --mandates and --json, and none names a call site. The hook is registered once, under PostToolUse. Caveat: --base, whose help text says 'use in CI', versus staged mode is a de facto proxy for CI versus pre-commit.

#### C42 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:135; plugins/arch-compliance/python/acf/detectors/build_artifacts.py:34; plugins/arch-compliance/python/acf/cli_check_diff.py:124-126`
- reasoning: Both scanners emit line=1. Any existing changed .py file, dist/x.py included, enters file_lines at :126. Other paths get ''.

### Unanchored findings

- **advisory**: On Python 3.13, resolve_under_root does not return None for a symlink loop, so a host guard hit on a looping path makes read_text raise OSError, which surfaces as DetectorPackError (gate exit 1) rather than the [] exemption lines the spec states; behaviour differs between 3.11/3.12 and 3.13.
  - evidence: `C:/Python313/Lib/pathlib/_local.py:670`
- **advisory**: Replacing _escapes_repo with resolve_under_root also changes symlink-loop citations on 3.11/3.12 from an uncaught RuntimeError to 'unresolved', a second behaviour change beside the drive-relative one that C31 calls the only change.
  - evidence: `plugins/arch-compliance/python/acf/adr/citations.py:74-76`
- **advisory**: Decision 6's table says sys.path[0] is the hooks directory, then the plugin's python/, but the hook inserts python/ at index 0, ahead of the hooks directory.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:25-26`
- **advisory**: scan_build_artifact_paths rewrites finding paths with lstrip('./'), which strips leading dots, so a build-artifact finding on a dot-prefixed code path (e.g. '.next/x.py') does not match its file_lines key, and the 'line-1 built-in findings on a changed code file are exemptable' statement fails for such paths.
  - evidence: `plugins/arch-compliance/python/acf/detectors/build_artifacts.py:27`
- **advisory**: Section 4.4 item 3 never shows where spec_from_file_location is called, or whether a None spec (or spec.loader) is handled inside the wrapped region, so that refusal path is unspecified.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:322`

### Looked for but did not find

- any dynamic import (importlib, import_module, spec_from_file_location, exec_module) under plugins/arch-compliance/python or hooks
- any reader of Mandate.call_sites in plugin runtime code
- a shipped or test registry row that the proposed _row_shape or _check_builtin rules would refuse (other than test_registry's not_a_real_detector)
- an active llm row in any shipped registry whose detector is not in LLM_PROMPT_IDS
- a test that reads scanner source text or references citations._looks_absolute or _escapes_repo
- a set operation or value access on KNOWN_DETECTORS by any consumer
- an .acf/enabled marker check in acf-check-diff
- an architecture-review runtime module under plugins/arch-compliance/python/acf

## compliance

### Claim verdicts

#### C43 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:317-333; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:336-346; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:82-95; plugins/arch-compliance/python/acf/cli_check_diff.py:69-72; plugins/arch-compliance/hooks/posttooluse_gate.py:113-117`
- reasoning: ARCHITECTURE.md:26-30 asks that errors surface and that broad handlers not swallow. The module-exec and getattr lookup sit in one try that re-raises UnknownDetectorError, and the not-callable case raises too. _call_host materialises list(raw) inside its try and re-raises DetectorPackError, which covers SystemExit and invalid HostHit. The TS lookup and compare run inside the bridge's existing try, whose except (KeyError, TypeError, ValueError) at :94-95 re-raises DetectorPackError. scan_host_guards' read runs inside each gate's scan try, which the spec widens for the hook. The llm prompt-id refusal is in load_mandates with llm_prompt_ids. Every broad handler re-raises a typed AcfError, so none swallows.

#### C44 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:257-273; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:181-200; plugins/arch-compliance/python/acf/enforcement.py:46; plugins/arch-compliance/python/acf/registry.py:56-63`
- reasoning: Today registry.py:58 skips every non-enforced row, and enforcement.py:46 matches findings to rows by mandate_id, so a partial or mis-id'd row loads and gets nothing. In the design, _check_builtin refuses three things: an unknown key (LLM prompt ids are no longer keys), id != contract.mandate_id, and Tier-1 sites outside contract.call_sites. _row_shape refuses an active ast/guard row with no Tier-1 site. The KNOWN_DETECTORS table gives fail_loud_ratchet DIFF_CALL_SITES only, and both gates' host runners select through registry.active(call_sites). The claim matches the design.

#### C45 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:242-246; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:360; config/architecture/ARCHITECTURE.md:126-128`
- reasoning: The doctrine says no default stands in for a missing declaration, and a missing declaration fails loud. load_mandates raises AcfInputError when an active host row has no repo_root, and it never derives one. apply_registry's call_sites is keyword-only with no default. The callers' repo comes from resolve_repo's cwd fallback, which ARCHITECTURE.md:126-128 already records as an allowed exception. So the claim holds without a new unrecorded default.

#### C46 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:324; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:331-332; config/architecture/ARCHITECTURE.md:48-49`
- reasoning: The doctrine forbids probing optional attributes with hasattr to paper over missing interfaces. The design looks up getattr(mod, attr, None) and then raises UnknownDetectorError when the result is not callable, so a missing interface fails loud rather than degrading. No hasattr is used, and none of the host load or call paths returns a fallback value.

#### C47 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:299; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:119-129; plugins/arch-compliance/python/acf/engine.py:17-24; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:252`
- reasoning: The doctrine asks for POSIX persisted paths, and this host is stricter: it refuses a backslash rather than normalizing it (ARCHITECTURE.md:62-64). HostHit.path runs through validate_posix_rel_path, which calls contains_backslash (engine.py:17-24) and raises. The error messages that build paths use .as_posix(), at spec :252 and :314. Every Finding.path that host hits produce, and that --json serializes, is a validated POSIX string.

#### C48 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/exceptions.py:13; plugins/arch-compliance/python/acf/exceptions.py:29; config/architecture/ARCHITECTURE.md:101-102`
- reasoning: The doctrine says every ACF exception subclasses AcfError alone. AcfInputError (:5), UnknownDetectorError (:13) and DetectorPackError (:29) each subclass AcfError only. The design reuses these three and defines no new exception class.

#### C49 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:12-15; plugins/arch-compliance/tests/test_repo_paths.py:14; plugins/arch-compliance/hooks/posttooluse_gate.py:11; plugins/arch-compliance/python/acf/repo.py:32-44`
- reasoning: acf.repo owns CONFIG_DIR and MANDATES_REL, and test_repo_paths fails on any config.{0,6}architecture spelling outside the exact-text allowlist. None of the new code in the design spells that path. The spec keeps posttooluse_gate.py:11, whose text the allowlist pins, verbatim. The new skill snippet takes resolve_repo and MANDATES_REL from acf.repo.

#### C50 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:137-138; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:314; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:416-432`
- reasoning: The doctrine says runtime messages and skill prose name no host repository, path or section. The new runtime messages say 'host detector', 'host root' and 'mandate'; none names HistoricMansions or any of its paths. The §4.8 prose changes to skills, README and guides use the generic term 'host'. The hm: references appear only in the spec's own justification text.

#### C51 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:512-533; plugins/arch-compliance/python/acf/judge.py:29-36; plugins/arch-compliance/python/acf/cli_check_diff.py:21`
- reasoning: The doctrine asks that an export have a live call site in the package, a hook or a skill. Each new export in §6.2 names a non-test caller. LLM_PROMPT_IDS keeps cli_check_diff's import (:21) as an argument to load_mandates, plus the skill snippet. TS_MANDATE_IDS is read by the bridge. The claim as stated holds. Separately, two existing exports lose their only runtime consumer; that is filed as an unanchored finding.

#### C52 — REFUTED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:486; config/architecture/ARCHITECTURE.md:161-164; config/architecture/ARCHITECTURE.md:221`
- reasoning: ARCHITECTURE.md:161-164 says a claim about the tree cannot rest on 'only' or 'no second' unless a re-runnable recipe backs the quantifier, and :221 lists this as the first high-frequency miss. The §6 Single point of definition row (spec :486) says 'One breach remains, recorded in the doctrine: the ratchet's path joins'. That is a census of the remaining breaches with no recipe and no per-item table behind it. The Appendix has no breach-census row. It is also false (see C55). So not every population claim carries a recipe.

#### C53 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:173-174; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:353; plugins/arch-compliance/python/acf/cli_check_diff.py:152`
- reasoning: The doctrine asks every subprocess text call to declare encoding='utf-8' and every prose file read to declare its encoding; it says nothing about an errors= policy. Both new reads declare encoding='utf-8': the bound read in the TypeScript branch (replacing :152) and scan_host_guards' read_text. The design adds no subprocess in the package or the hooks.

#### C54 — SURVIVED
- evidence: `pyproject.toml:3; plugins/arch-compliance/.claude-plugin/plugin.json:3; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:432`
- reasoning: ARCHITECTURE.md:186-187 says a change to skill prose bumps the version in plugin.json and pyproject.toml. Both files currently read 0.2.2 at line 3. §4.8 changes the acf-mandate and acf-setup skill prose and bumps both files to 0.2.3. .claude-plugin/marketplace.json carries no version.

#### C55 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:128-150; plugins/arch-compliance/hooks/posttooluse_gate.py:255-277; config/architecture/ARCHITECTURE.md:198-209; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:486`
- reasoning: The doctrine requires one canonical implementation of any procedure needed by more than one module, and it requires current breaches to be 'recorded not hidden'. The claim says that within the Tier-1 gates 'the one remaining breach' is the ratchet's path joins. Inside the two Tier-1 gates, however, the procedure that turns a row's params into scanner kwargs is implemented twice, token for token: target_literal_re default '', allowlist_globs [], atomic_is_sink True, state_field and validator_name ''. It is at cli_check_diff.py:128-150 and posttooluse_gate.py:255-277, and the build-artifact path_prefixes extraction is duplicated at :158-166 and :284-294. The design edits exactly these loops: it replaces their filters with registry.active and adds the host calls. Yet it neither consolidates the duplication nor adds it to the doctrine's breach list (§4.8 adds only the ratchet). So the claim that only one breach remains is false.

#### C56 — REFUTED
- evidence: `config/architecture/ARCHITECTURE.md:213-215; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:72; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:134; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:89; plugins/arch-compliance/python/acf/adr/citations.py:161-167`
- reasoning: The doctrine says to remove non-contractual patterns 'in code paths you are changing' and not to expand scope to unrelated modules. The design changes no ADR-gate behaviour except through this consolidation, yet it rewrites citations.py's resolve_citation (:161-167) to use engine helpers. That also changes ADR-gate classification: 'C:a/b.py' becomes external, and a symlink loop now classifies as unresolved instead of raising. So the claim that the consolidations touch only paths the design changes is false for citations. The spec applies the opposite test elsewhere: it leaves the ratchet's identical path joins alone 'because the ratchet is otherwise untouched here' (spec :89). By that same test, the acf.adr consolidation is out of scope.

#### C57 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:69-81; plugins/arch-compliance/python/acf/adr/ledger.py:1`
- reasoning: ARCHITECTURE.md:147-148 says LedgerRow and LedgerAmendment fields change only through a spec and a gate run. The scope table does not list acf/adr/ledger.py, and no test in §4.7 touches the ledger. The only ledger mention is the call_sites grep finding the unrelated surface_call_sites in ledger.py, which stays unchanged. The DoD's ledger row is an append, not a model change.

#### C58 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:123; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:125; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:50; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:257-273`
- reasoning: :123 and :125 each call for 'Extension points for project-specific detectors'; the host reference syntax and runners supply them. Principle 4 asks that detectors and call sites agree 'or tests fail'; the design makes call_sites load-bearing, adds the _check_builtin contract and adds a contract-against-dispatch test. Fail loud, POSIX and the registry-façade principles hold through typed refusals, validate_posix_rel_path, and one loader with one finding schema.

#### C59 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:49-50; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:353; config/architecture/ARCHITECTURE.md:26-27`
- reasoning: A flagged path with no readable lines gives line_lookup '' (as make_line_lookup does today). With '', token_exempted cannot match, so apply_registry keeps the finding: the fallback fails closed and hides no finding. errors='replace' cannot hide an ASCII token. The design routes OSError to DetectorPackError inside the scan try, and make_line_lookup does no I/O. An advisory finding notes that the existence check needed for 'missing -> []' is not stated.

### Unanchored findings

- **important**: Replacing cli_check_diff.py:25 with an import of acf.detectors.KNOWN_DETECTORS removes the only runtime consumer of the existing exports ALL_PYTHON_DETECTOR_IDS and TS_DETECTOR_IDS. After that, their only users are the new and existing tests (test_builtin_detectors, test_typescript_pack:14), which ## Live consumers calls dead code, and §6.2 does not address it.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:25`
- **important**: The params-to-kwargs procedure for facade, fsm and build-artifact rows is duplicated across both Tier-1 gates. The design edits those exact loops yet neither consolidates the duplication nor records it in ## Single point of definition, while claiming a single remaining breach.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:255-294`
- **advisory**: scan_host_guards reads resolve_under_root(repo_root, hit.path) and then read_text. A non-strict resolve returns a Path for a missing in-root file, so read_text raises FileNotFoundError (an OSError), which the spec routes to DetectorPackError. That contradicts the stated 'missing -> []' unless an unstated is_file check comes first. A guard flagging a deleted changed path would then fail the gate.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:353`

### Looked for but did not find

- ## High-frequency misses — 'A check re-implemented in a test or a skill': the skill snippet and tests keep consuming load_mandates and KNOWN_DETECTORS, and the re-export keeps the name at ARCHITECTURE.md:228 resolvable. tests/test_self_host.py:40 moves to resolve_under_root. No re-implementation found.
- ## High-frequency misses — 'A stdlib mixin on an exception class': no exception class is added.
- ## High-frequency misses — 'A subprocess text call without an encoding': the design adds no subprocess.
- ## High-frequency misses — 'A default that re-enters for a declared value': repo_root and call_sites are refused or required. The only default the new callers use is resolve_repo's cwd fallback, which is already recorded at ARCHITECTURE.md:126-128.
- ## Build artifacts: the no_build_artifacts contract is TIER1, which matches the existing dispatch in both gates. The rule is unchanged.
- ## Fail-loud ratchet: given DIFF_CALL_SITES only, which matches cli_check_diff.py:168-182 and the absence of a ratchet call in the hook. This repository's ratchet row is [ci] and unenforced, so it is not refused.
- ## Façade sinks / ## FSM transitions: they gain only mandate-id constants. The spec declares no state-machine surface and no transition logic changes. These sections are not otherwise touched.
- ## Soft fail-loud smells / ## React boundaries: the llm rows here use prompt ids in LLM_PROMPT_IDS (judge.py:29-36), so the new llm_prompt_ids check does not refuse them. Tier-2 is unchanged.
- ## Post-merge: host operational declarations are not touched by this design.
- Unstated mandates: walked every doctrine section from ## Fail loud to ## Post-merge. Every section this design's surface touches is already named in the spec header and the §6 table, so unstated_mandates is empty.

## sweeper

### Claim verdicts

#### C60 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; plugins/arch-compliance/hooks/posttooluse_gate.py:229-236; plugins/arch-compliance/hooks/posttooluse_gate.py:284-286; plugins/arch-compliance/python/acf/enforcement.py:47`
- reasoning: I grepped plugins/ for `.status` and the string 'unenforced'. Outside tests it matches only the four Tier-1 filters the spec replaces, registry.py:58 (replaced by is_active), judge.py:218 (Tier-2, out of scope by Decision 2), inject_constraints.py:158 (display only) and acf-mandate SKILL.md:98 (print only). After the change, the only call-site test in the spec is _check_builtin's TIER1 intersection. That is a contract check, not a second 'runs at' filter.

#### C61 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/adr/host.py:24-25; plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:292; plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:323; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:122-124`
- reasoning: I searched by behaviour: a host-declared path string joined under the repository root. The ratchet joins are one such site, but not the only other one. AdrHostConfig.runs_dir and ledger_path are host-declared relative path strings, validated only by PosixStr (backslashes refused; absolute paths and '..' segments allowed). The gate skill, the housekeeping skill and test_adr_host_acceptance.py:85,90 join them as `repo / cfg.runs_dir` and `repo / cfg.ledger_path` with no absolute or containment test. That is the same job as validate_posix_rel_path plus resolve_under_root. The claim's sweep was keyed to 'registry' paths and missed this host-config owner, so the debt list in §3/§4.8 is incomplete.

#### C62 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:70-95`
- reasoning: The bridge decodes a JSON list from a subprocess and coerces each dict through posix_path, int() and Severity(), catching KeyError, TypeError and ValueError. The host runner receives typed, validated HostHit objects. The only shared step is the final Finding(...) call, and the inputs share no format, so the non-merge holds. Note: §5.2's justification says the bridge takes mandate_id 'from it' (the Node JSON). That contradicts §4.3, where mandate_id comes from TS_MANDATE_IDS. The prose is stale, but the non-merge still holds.

#### C63 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:238-255; plugins/arch-compliance/python/acf/judge.py:320-332`
- reasoning: _to_finding demotes BLOCK to WARN on the judge's verdict or confidence. It admits path '<diff>' and line 0, takes mandate_id from JudgeResult (set from mandate.id at :326) and sets confidence. Its output is not routed through apply_registry: cli_check_llm.py:61-73 uses the severity directly. The shared part is only the stamping of detector and detection, so ADJACENT is fair. The spec's cited range judge.py:236-253 is off by two lines; the function is at :238-255.

#### C64 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:22-26; plugins/arch-compliance/hooks/inject_constraints.py:28-29; tests/test_check_installed_skills.py:15-18`
- reasoning: I grepped importlib, import_module, spec_from_file_location, exec_module, runpy, __import__, exec( and sys.path.insert/append across *.py and *.md, excluding docs/reviews. Runtime code has only the two hooks' insertion of the plugin's own python/ directory at sys.path[0]. The only dynamic loader is test-only (test_check_installed_skills.py) and loads a plugin script, not a registry path. The TS bridge runs a plugin-owned script, and the judge uses HTTP.

#### C65 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-82; plugins/arch-compliance/hooks/posttooluse_gate.py:119-125`
- reasoning: I grepped line_lookup, LineLookup and `[line - 1]` across the tree, excluding docs. The only LineLookup closures passed to apply_registry are these two. fsm_guard.py:56 indexes lines for a message snippet, not a lookup handed to apply_registry. cli_check_llm.py and judge.py never call apply_registry. The test lambdas in test_enforcement are test-only.

#### C66 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:95; plugins/arch-compliance/skills/architecture-review/SKILL.md:62; plugins/arch-compliance/tests/test_profile_drift.py:24`
- reasoning: Every validator I found consumes load_mandates rather than re-checking detector ids or call sites: the acf-mandate snippet, architecture-review, test_profile_drift, test_self_host.py:23 and acf-setup. architecture-review only checks mandate ids against reg.by_id. No skill or test re-implements a detector-id or call-site check.

#### C67 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:242-246; plugins/arch-compliance/hooks/posttooluse_gate.py:290-291`
- reasoning: On ValueError the existing try/except falls back to the absolute posix path. rel_paths therefore mixes in-repo and out-of-repo entries and feeds scan_build_artifact_paths at :290-291. Recording the in-repo branch in a separate list reuses the one existing test and leaves the build-artifact input unchanged. The repo is resolved (repo.py:41-44) and abs_path is resolved (:204), so relative_to compares like with like.

#### C68 — SURVIVED
- evidence: `config/architecture/mandates.yml:70; plugins/arch-compliance/profiles/python-service/mandates.yml:18; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:104`
- reasoning: I grepped call_sites across the tree, excluding docs/reviews. Shipped registries use ci, hook and audit; the parent design doc lists precommit, ci, posttooluse and audit. test_template.py:80 uses [] on an llm row, which _row_shape skips. Every active ast/guard row carries ci. audit appears only on llm/manual rows and on ci,audit llm rows, and no Tier-1 gate reads it. HistoricMansions rows are out of scope here.

#### C69 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_registry.py:30; plugins/arch-compliance/tests/test_profile_drift.py:24; plugins/arch-compliance/tests/test_hooks.py:199-218`
- reasoning: I grepped tests for apply_registry, KNOWN_DETECTORS, _looks_absolute/_escapes_repo, _active_mandates, the hook script, '"detector"' and mandate_id literals. Findings: test_registry:30 passes a frozenset, which the spec covers. test_profile_drift:24 and the acf-mandate snippet test load the profiles. Every profile row satisfies the new contracts: ids equal the stamped ids, every active ast/guard row has ci, and ratchet rows are [ci] and unenforced. test_typescript_pack reads real Node output, whose literals match TS_MANDATE_IDS. test_judge:67 asserts that LLM_PROMPT_IDS is a frozenset, not KNOWN_DETECTORS. I found no other dependent test.

#### C70 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:168-182; plugins/arch-compliance/hooks/posttooluse_gate.py:213-295; plugins/arch-compliance/python/acf/enforcement.py:46-47`
- reasoning: The only built-in whose dispatch differs per gate is the ratchet, which runs only in the diff gate. With the contract DIFF-only, _check_builtin refuses a row declaring hook. If the hook ever dispatched the ratchet, its finding would map to a row that does not run_at HOOK and be dropped at the one sink. Under-dispatch shows up as a missing mandate_id in the per-gate fixture assertion. Both directions are covered as stated.

#### C71 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:242-245; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:59-62; plugins/arch-compliance/python/acf/adr/citations.py:74-76`
- reasoning: The hook and ratchet relativize an already-resolved absolute Path. resolve_under_root, which subsumes citations' _escapes_repo, joins and resolves a relative string. They share only the stdlib containment predicate (relative_to / is_relative_to), a single call that is not worth extracting. ADJACENT is defensible. The containment decision still has three owners after the change, recorded in two_owner_counts.

#### C72 — UNPROVEN
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:329; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:344; plugins/arch-compliance/tests/test_hooks.py:22-37`
- reasoning: The design is proposed, so I have no implementation site to resolve. The no-conftest half holds: Glob finds no conftest.py anywhere, so fresh_host_loader would be the only reset. The 'exactly two regions' half is doubtful. Both handlers format `{exc}` inside the except block, which calls the host exception's __str__ outside the try. _to_findings reads hit.path on what may be a host subclass of HostHit. Either path can run host code that raises unwrapped.

#### C73 — SURVIVED
- evidence: `tests/test_self_host.py:5; plugins/arch-compliance/tests/test_acf_mandate_skill.py:2; plugins/arch-compliance/skills/acf-mandate/SKILL.md:18; README.md:106`
- reasoning: I grepped *.md and *.py (docs/reviews excluded) for 'detector union', 'known union', KNOWN_DETECTORS, '.py/.ts/.tsx', PostToolUse and apply_registry drop rules. Every stale site I found is in §4.7/§4.8. The one residual is config/architecture/ARCHITECTURE.md:228, which names `acf.cli_check_diff.KNOWN_DETECTORS` as the package check to consume. It still resolves through the re-export, so it is not stale, only no longer the canonical home.

#### C74 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:85; plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23; plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15`
- reasoning: I grepped plugins/ (tests excluded) for both literals. They appear only in YAML profiles, skill prose, the Node rules and scan.ts self-tests; no Python runtime site has them. Today the bridge copies item['mandate_id'] at :85; under v4 it stamps from TS_MANDATE_IDS. Adjacent duplicate: TS_DETECTOR_IDS (:14) will equal TS_MANDATE_IDS' keys, a second spelling of the TS id set the spec does not collapse (see findings).

#### C75 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:52; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:133; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:86`
- reasoning: Every scanner fills severity because Finding requires it (the ratchet hard-codes BLOCK, the TS bridge reads Node). apply_registry overwrites it from the row for every kept finding, and both Tier-1 gates route all findings through it (cli_check_diff.py:82, posttooluse_gate.py:125). The judge sets its own severity but sits outside the Tier-1 path.

### Unanchored findings

- **important**: KNOWN_DETECTORS' keys become a second definition of the built-in detector-id set. ALL_PYTHON_DETECTOR_IDS, GUARD_DETECTOR_IDS, PYTHON_AST_DETECTOR_IDS and TS_DETECTOR_IDS stay, lose their only runtime consumer (cli_check_diff.py:25), and the new test pins the two definitions equal instead of collapsing them. That breaches ## Single point of definition and ## Live consumers, and the self-hosting spec removed PYTHON_DETECTOR_IDS on the same grounds (PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:421-424).
  - evidence: `plugins/arch-compliance/python/acf/detectors/__init__.py:11-28`
- **important**: The spec records the ratchet as the only other owner of 'host-declared path string to a file under the root', but AdrHostConfig.runs_dir/ledger_path are joined as `repo / cfg.runs_dir` / `repo / cfg.ledger_path` with only PosixStr (no absolute or containment test). This third owner is missing from the §3/§4.8 debt list and from the §5.2 PosixStr ADJACENT row.
  - evidence: `plugins/arch-compliance/python/acf/adr/host.py:24-25`
- **advisory**: TS_DETECTOR_IDS (a frozenset) and the new TS_MANDATE_IDS keys spell the same two TypeScript detector ids side by side in typescript_bridge.py; the spec neither derives one from the other nor records it.
  - evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:14`
- **advisory**: §5.2 justifies the bridge-vs-host non-merge by saying the bridge 'takes mandate_id and severity from' the Node JSON, which contradicts §4.3, where the bridge stamps mandate_id from TS_MANDATE_IDS.
  - evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:84-92`
- **advisory**: Host code can run outside the two wrapped regions. Both handlers format the host exception with `{exc}` after the try has exited, and _to_findings reads attributes of what may be a host subclass of HostHit, so a raising __str__ or descriptor escapes as a traceback rather than a typed error.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:344`
- **advisory**: The spec cites the judge's _to_finding at judge.py:236-253; it is at :238-255 in the tree under review.
  - evidence: `plugins/arch-compliance/python/acf/judge.py:238`

### Looked for but did not find

- another active-row or status filter on the Tier-1 path: `.status`, 'unenforced', `_active_mandates` across plugins/ (only the sites the spec replaces, plus the judge and display-only reads)
- another LineLookup passed to apply_registry: line_lookup, LineLookup, `[line - 1]` (only the two gate closures)
- an existing loader of registry-supplied code: importlib, import_module, spec_from_file_location, exec_module, runpy, exec(, __import__, sys.path.insert/append (test-only loader in tests/test_check_installed_skills.py)
- an independent detector-id or call-site validator in skills or tests: 'detector', known_detectors, call_sites in acf-mandate/acf-setup/architecture-review SKILL.md and tests (all consume load_mandates)
- a call-site value outside {ci, precommit, hook, posttooluse, audit}: call_sites across YAML, *.py and *.md
- a non-test Python spelling of 'fail-loud.empty-catch' or 'no-shims.explicit-any' (none)
- a test depending on the old apply_registry signature, citations' private helpers, a frozenset KNOWN_DETECTORS or Node-copied mandate_id: apply_registry, _looks_absolute, _escapes_repo, KNOWN_DETECTORS, '"detector"' in tests
- an existing conftest.py that would clash with the new fixture (none)

### Relationships

- PARTIAL_OVERLAP: `KNOWN_DETECTORS mapping (acf.detectors)` — responsibility `enumerate the built-in Tier-1 detector ids` — existing `plugins/arch-compliance/python/acf/detectors/__init__.py:28`
  - resolution: Make KNOWN_DETECTORS the single definition of the built-in id set. Either derive ALL_PYTHON_DETECTOR_IDS, GUARD_DETECTOR_IDS, PYTHON_AST_DETECTOR_IDS and TS_DETECTOR_IDS from it (by contract field, or by adding a detection kind to BuiltinDetector), or delete whichever lose their last runtime consumer. The equality test then becomes unnecessary.
- IDENTICAL: `TS_MANDATE_IDS` — responsibility `enumerate the TypeScript detector ids` — existing `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:14`
  - resolution: Set TS_DETECTOR_IDS = frozenset(TS_MANDATE_IDS), or drop it, so the TS id set is spelled once.
- PARTIAL_OVERLAP: `validate_posix_rel_path / resolve_under_root` — responsibility `validate a host-declared relative path string and contain it under the root` — existing `plugins/arch-compliance/python/acf/adr/host.py:24-25`
  - resolution: AdrHostConfig.runs_dir and ledger_path should validate through validate_posix_rel_path, and their joins should go through resolve_under_root. At minimum, record them beside the ratchet as a ## Single point of definition breach.
- PARTIAL_OVERLAP: `looks_absolute / resolve_under_root` — responsibility `registry path string to a file under the root` — existing `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:122-124`
  - resolution: The ratchet's baseline and roots joins become resolve_under_root consumers (recorded by the spec as debt).
- SUBSUMED: `looks_absolute / resolve_under_root` — responsibility `absolute-path and escape tests on a cited path` — existing `plugins/arch-compliance/python/acf/adr/citations.py:49-51`
  - resolution: Delete citations' private helpers; citations.py:161,:163 call the acf.engine helpers.
- ADJACENT: `resolve_under_root` — responsibility `decide whether a path lies under the repository root` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:242-245`
  - resolution: none
  - non-merge: The hook and ratchet relativize an already-resolved absolute Path; resolve_under_root joins and resolves a relative string. They share only one stdlib predicate call.
- SUBSUMED: `Mandate.runs_at / MandateRegistry.active` — responsibility `decide which rows run at a Tier-1 gate` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99`
  - resolution: _active_mandates, the hook's three inline filters and apply_registry's status check all call runs_at/active.
- ADJACENT: `host _to_findings` — responsibility `construct a Finding from a mandate row plus an external location record` — existing `plugins/arch-compliance/python/acf/judge.py:238-255`
  - resolution: none
  - non-merge: The judge demotes severity by confidence, admits path '<diff>' and line 0, and bypasses apply_registry. Host findings take the row's severity, require a relative path and line >= 1, and pass through apply_registry.
- ADJACENT: `host _to_findings` — responsibility `coerce an external detector's output into Finding` — existing `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:75-95`
  - resolution: none
  - non-merge: The bridge decodes untyped JSON from a subprocess; the host runner consumes validated HostHit objects. The only shared step is the Finding constructor.
- IDENTICAL: `make_line_lookup` — responsibility `map (path, line) to source text for exemption checks` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80`
  - resolution: Delete both gate closures (cli_check_diff.py:76-80, posttooluse_gate.py:119-123); both gates call make_line_lookup.
- ADJACENT: `load_host_detector sys.path append` — responsibility `put a code root on sys.path` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:22-26`
  - resolution: none
  - non-merge: The hooks insert the plugin's own python/ directory at start-up; the loader appends the host root once per process, at dispatch time.
- PARTIAL_OVERLAP: `KNOWN_DETECTORS call_sites` — responsibility `declare at which gate each built-in detector runs` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:168-182`
  - resolution: Accepted two-owner arrangement tied by the contract-against-dispatch test. A shared dispatcher reading the contract would collapse it, and the spec lists that as a non-goal.

### Two-owner counts

- enumerate built-in Tier-1 detector ids (KNOWN_DETECTORS keys; ALL_PYTHON_DETECTOR_IDS|TS_DETECTOR_IDS): 2
- enumerate TypeScript detector ids (TS_DETECTOR_IDS; TS_MANDATE_IDS keys): 2
- host-declared path string to a location under the root (acf.engine helpers; fail_loud_ratchet joins; AdrHostConfig runs_dir/ledger_path joins): 3
- decide whether a path lies under the repo root (resolve_under_root; hook relative_to; ratchet walk filter): 3
- declare where a built-in detector runs (KNOWN_DETECTORS call_sites; each gate's dispatch code): 2
- per-gate dispatch loop over changed files (cli_check_diff._scan_changed; posttooluse_gate._scan_paths): 2
- parse Python and skip on SyntaxError (python_pack; facade_sinks; fsm_guard; fail_loud_ratchet; scan_host_ast_file): 5
- build a Finding from a mandate row plus a location (judge._to_finding; host _to_findings): 2
- row activity definition (Mandate.runs_at for Tier-1; judge status==enforced for Tier-2): 2

### Document conflicts

- `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:418` (contradicts): `KNOWN_DETECTORS` stays where the diff CLI defines it (`plugins/arch-compliance/python/acf/cli_check_diff.py:25`)
- `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:421` (contradicts): the unused compatibility alias `PYTHON_DETECTOR_IDS` is removed
- `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:161` (restates): PostToolUse | Diff-scoped Tier 1 on edited `.py` / `.ts` / `.tsx` (and configured config paths)
- `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:104` (restates): `call_sites` | e.g. `precommit`, `ci`, `posttooluse`, `audit`

## hardening

### Claim verdicts

#### C76 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:72; plugins/arch-compliance/hooks/posttooluse_gate.py:113-117; plugins/arch-compliance/hooks/inject_constraints.py:104; plugins/arch-compliance/python/acf/cli_check_llm.py:54`
- reasoning: cli_check_diff.py:72 already catches UnknownDetectorError around both load and scan. The hook's scan except at :113-117 is widened to include it (§4.6), so a dispatch-time import failure or a missing callable fails loud in both gates. The load-time existence check keeps the missing-file case at load. The decisive reason holds: the hook loads with known_detectors, so importing at load would import [ci]-only guards and ast modules on every edit. One sub-reason is inaccurate. inject_constraints.py:104 and cli_check_llm.py:54 call load_mandates without known_detectors, and the host checks sit inside the known_detectors branch, so even a load-time import there would not run host code in those callers. The deferral is still justified; filed as advisory.

#### C77 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:56-63; plugins/arch-compliance/python/acf/cli_check_diff.py:127; plugins/arch-compliance/python/acf/enforcement.py:46`
- reasoning: Built-in rows: _row_shape forces call_sites∩TIER1≠∅ and _check_builtin forces (call_sites∩TIER1)⊆contract.call_sites. Together, an active row runs at at least one gate that dispatches its detector, and its id equals the stamped mandate_id that apply_registry matches on (enforcement.py:46). Built-in dispatch is by detector id, not by the detection field (cli_check_diff.py:127 and :153-156 run unconditionally), so a detection/detector mismatch still runs. Host rows: a Tier-1 site is required, host ast rows must declare python/typescript/both, and the runner stamps mandate.id, so findings always land on the row. The contract's accuracy is tied to dispatch by the contract-against-dispatch test. Residual: a misspelled Tier-1 site beside a valid one silently narrows routing. The row still runs at one gate, so this claim survives; the gap is filed separately.

#### C78 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:63; plugins/arch-compliance/hooks/posttooluse_gate.py:65; plugins/arch-compliance/tests/test_diff_cli.py:9`
- reasoning: main() resolves one repo once (cli_check_diff.py:63), and the hook resolves one repo per subprocess (posttooluse_gate.py:65, hooks.json:22). I grepped plugins/arch-compliance for other callers of cli_check_diff, _scan_changed and posttooluse_gate. The only in-process caller is test_diff_cli.py:9, which calls main() repeatedly over tmp repos: that is the only multi-root producer. Existing tests without host rows never reach the loader, because the runners return before loading when no host row is selected. The refusal raises (rung 3); the only reset is the test fixture.

#### C79 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:67; plugins/arch-compliance/python/acf/detectors/build_artifacts.py:31; plugins/arch-compliance/python/acf/cli_check_diff.py:168-182`
- reasoning: Each scanner stamps a literal mandate_id: python_pack.py:67/97/144/172, build_artifacts.py:31, facade_sinks.py:69, fail_loud_ratchet.py:132, fsm_guard.py:59. The ratchet runs only in cli_check_diff (:168-182); the hook's _scan_paths has no ratchet call. I ran the Appendix recipe over config/architecture/mandates.yml, both profiles and fixtures/mandates_valid.yml. No file has two rows naming the same built-in detector, and every built-in row's id equals its stamped id. So the one-row-per-detector cost affects no shipped registry.

#### C80 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/loader.py:70-73; plugins/arch-compliance/hooks/inject_constraints.py:104-107; plugins/arch-compliance/python/acf/cli_check_llm.py:54`
- reasoning: load_model_file converts only ValidationError (loader.py:70-73), so AcfInputError raised in a model_validator propagates with its own type, exactly as _unique_ids already does (registry.py:33-41). inject_constraints catches AcfInputError at :105. Caveat: cli_check_llm.py:54 does not catch it; it exits non-zero with a traceback. The spec's §3 states this honestly ('uncaught AcfInputError'), so 'no caller change' holds, but 'each already handles' overstates it. Direct constructions (test_enforcement.py:19: active ast, call_sites [ci]) pass the new validator.

#### C81 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37; plugins/arch-compliance/python/acf/cli_check_diff.py:127`
- reasoning: Built-in scanners each parse independently (python_pack.py:34-37), and the design leaves them alone. One parse shared by N host ast detectors saves N-1 parses; the stated justification is factual. A hazard the spec does not state: the shared ast.Module is mutable, so one host detector that transforms the tree changes what the next one sees (filed as advisory).

#### C82 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:46; plugins/arch-compliance/python/acf/finding.py:12`
- reasoning: apply_registry looks rows up by finding.mandate_id (enforcement.py:46), and Finding.mandate_id is a free str (finding.py:12). A host-supplied Finding could therefore attach to any row. HostHit has no mandate_id, severity or detector field (extra='forbid'), so the wrong-row state cannot be constructed (rung 1).

#### C83 — SURVIVED
- evidence: `.gitignore:8; .github/workflows/ci.yml:40; plugins/arch-compliance/hooks/posttooluse_gate.py:72-81`
- reasoning: .gitignore:8 is '.acf/', so a CI checkout lacks .acf/enabled. ci.yml:40 invokes python -m acf.cli_check_diff explicitly, so requiring the marker would disable CI. The hook returns 0 at :72-81 before any deferred import, so the automatic path stays gated. The residual manual-run case is stated in the spec as accepted.

#### C84 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:127; plugins/arch-compliance/hooks/posttooluse_gate.py:254; plugins/arch-compliance/python/acf/detectors/python_pack.py:27-52`
- reasoning: scan_python_file (python_pack.py:27-52) emits all three Python detectors' findings without a registry argument. It is called unconditionally in both gates (cli_check_diff.py:127, posttooluse_gate.py:254), and scan_typescript_file likewise (cli_check_diff.py:153-156, posttooluse_gate.py:279-282). registry.active selection covers only facade, FSM, build-artifact, ratchet and host rows. Without the sink filter, e.g. the [ci]-only no-shims.hasattr (mandates.yml:70) would still be reported by the hook. The filter is not redundant. The spec does give a reason, at Decision 2.

#### C85 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:22-28; pyproject.toml:19; .github/workflows/ci.yml:40`
- reasoning: Under the hook, sys.path[0] is the hooks directory, then the plugin python/ is inserted (:22-26), and acf is imported at :28 before any host code. Under the console script (pyproject.toml:19), sys.path[0] is the script dir. Appending puts the host root after both, adding no shadowing. Under -m from the host root (ci.yml:40), cwd is already first, which is pre-existing. A host top-level name provided earlier on the path resolves to that earlier module. Normally the needed submodule or attribute is then missing, so the failure surfaces as UnknownDetectorError from the wrapped exec/getattr region. Same-named modules carrying the needed attribute stay possible, but the spec scopes the claim to 'the common case'.

#### C86 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:72; plugins/arch-compliance/hooks/posttooluse_gate.py:113-117; plugins/arch-compliance/python/acf/enforcement.py:49`
- reasoning: Both scan calls (_scan_changed at cli_check_diff.py:71, _scan_paths at posttooluse_gate.py:114) sit inside the try whose except handles DetectorPackError. apply_registry calls only line_lookup (enforcement.py:49), so moving the read into scan_host_guards keeps it I/O-free. Edge not covered by the spec's mapping: a guard hit naming a directory resolves, and read_text then raises IsADirectoryError/PermissionError (OSError). That becomes DetectorPackError and fails the gate rather than leaving the finding (advisory).

#### C87 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:29-36; plugins/arch-compliance/python/acf/judge.py:16; plugins/arch-compliance/skills/acf-mandate/SKILL.md:56`
- reasoning: judge.py:16 imports acf.registry, so registry cannot import judge without a cycle; passing ids in is required. SKILL.md:56 states the prompt-id rule. Every shipped llm detector (llm_react_boundaries, llm_fail_loud) is in LLM_PROMPT_IDS (judge.py:29-36), so nothing shipped is refused. Note: run_judge never dispatches on the id; it only renders it into the prompt (judge.py:265). The check's protected state has no runtime consequence, and it runs in acf-check-diff, not acf-check-llm (advisory).

#### C88 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:14-27; plugins/arch-compliance/python/acf/registry.py:43-45`
- reasoning: Mandate is a pydantic BaseModel with no model_config (default extra='ignore', not frozen). It has id, severity, detection, detector, languages (a Literal including 'none' at :11), call_sites list[str] (:21), status and params dict|None (:26). MandateRegistry already carries a @property (by_id at :43-45) and a model_validator, so adding is_active, runs_at, active and _row_shape is compatible.

#### C89 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/finding.py:6-19`
- reasoning: Finding's required fields are mandate_id, severity (Severity), path, line, message and detector; confidence and detection are defaulted. Severity is a str Enum with BLOCK/WARN (:6-8), and Mandate.severity is Literal['BLOCK','WARN'], so Severity(mandate.severity) constructs.

#### C90 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:23; plugins/arch-compliance/python/acf/enforcement.py:46-52`
- reasoning: by_id lookup at :46, the status drop at :47, exemption at :49-51 and severity at :52. LineLookup = Callable[[str,int],str] at :23 matches make_line_lookup's return.

#### C91 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:69-72; plugins/arch-compliance/python/acf/cli_check_diff.py:110; plugins/arch-compliance/python/acf/cli_check_diff.py:152`
- reasoning: Load at :70 and scan at :71 sit in one try; the except at :72 lists GitError, AcfInputError, UnknownDetectorError and DetectorPackError. lookup/apply are at :76-82. In the .py branch, repo, text (:125), posix (:122), lines (:121) and registry are in scope after :150. The .ts branch read at :152 can bind text. changed (:110) is in scope after the ratchet loop (:168-182).

#### C92 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:91-125; plugins/arch-compliance/hooks/posttooluse_gate.py:229-252; plugins/arch-compliance/hooks/posttooluse_gate.py:284-294`
- reasoning: Deferred imports are at :91-104, the load try at :106-110 and the scan try at :113-117 (except DetectorPackError only). lookup/apply are at :119-125 and the inline filters at :229-236 and :284-286. relative_to with the ValueError fallback is at :242-245. text (:251) and rel (:243) are in scope for both the .py branch (:253) and the else/TypeScript branch (:278). The build-artifact loop is at :284-294.

#### C93 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:72; plugins/arch-compliance/hooks/posttooluse_gate.py:113-117; plugins/arch-compliance/python/acf/loader.py:70-73`
- reasoning: Both host runners are called inside each gate's scan function, which sits under the scan try (cli_check_diff.py:71-72; the hook's :113-117, widened per §4.6). Load-time refusals (AcfInputError via the validator, which loader.py:70-73 does not rewrap; UnknownDetectorError from the file check) reach the load try. The hook's load except gains UnknownDetectorError. _call_host covers the call plus list(raw); _to_findings refuses non-HostHit items. A directory hit raises OSError → DetectorPackError, which is still handled. Pre-existing non-AcfError escapes (UnicodeDecodeError on the strict utf-8 reads; ValueError from ast.parse on NUL bytes under 3.11, which scan_python_file hits first) are unchanged by this design.

#### C94 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_diff_cli.py:9; plugins/arch-compliance/hooks/posttooluse_gate.py:25-26; C:/Python313/Lib/dataclasses.py:757`
- reasoning: The module globals, the sha256-derived name and register-then-exec with pop on failure are all expressible with importlib.util; monkeypatch.setattr on module globals works when the loader reads them by name at call time. test_diff_cli.py:9 imports main at collection, so acf.detectors.host is already in sys.modules before any fixture snapshot and is not evicted. Caveat: deleting every sys.modules key added during a test also evicts lazily imported third-party or plugin submodules first touched in that test (advisory).

#### C95 — SURVIVED
- evidence: `C:/Python313/Lib/dataclasses.py:757; pyproject.toml:5`
- reasoning: dataclasses._is_type does sys.modules.get(cls.__module__).__dict__ (dataclasses.py:757) for string annotations matching its module-identifier regex. An unregistered module gives an AttributeError on None, so registering before exec_module is required. spec_from_file_location(name, path) sets the module __name__ to the synthetic name, which becomes cls.__module__. Checked on 3.13; pyproject.toml:5 allows >=3.11, where the same lookup exists.

#### C96 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:5-7; plugins/arch-compliance/python/acf/judge.py:16; plugins/arch-compliance/python/acf/adr/contract.py:20; plugins/arch-compliance/python/acf/detectors/__init__.py:5-9; plugins/arch-compliance/tests/test_adr_import_graph.py:74-76`
- reasoning: registry imports only pydantic, exceptions and loader; adding engine (stdlib) adds no cycle. The scanner modules import only engine, finding and exceptions, never acf.detectors or registry, so __init__ importing registry and the scanner constants is acyclic. judge imports registry (:16), confirming registry must not import judge. acf.adr already imports acf.engine (contract.py:20). test_adr_import_graph.py:74-76 checks only the literal 'acf.adr' text in the hook files. acf.detectors → registry → loader/engine does not reach acf.adr or acf.judge.

#### C97 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:53-64`
- reasoning: load_mandates calls load_model_file(path, Mandate, subject='mandates file', fmt='yaml', many=True) at :53-55 and returns MandateRegistry(mandates=mandates, source_path=path.as_posix()) at :64. The §4.2 body extends it in place. Note: test_registry.py:30 currently passes a frozenset, which §4.7 changes to KNOWN_DETECTORS.

#### C98 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_repo_paths.py:47-48; plugins/arch-compliance/hooks/posttooluse_gate.py:11-12`
- reasoning: test_repo_paths.py:47-48 allowlists exactly the :11 text. The test (:55-66) flags any line matching config.{0,6}architecture that is not allowlisted. Line :12 carries no such text, and a grep for 'Otherwise scan' finds it nowhere else. Rewording :12 breaks nothing, provided the new wording does not name the config directory.

#### C99 — SURVIVED
- evidence: `config/architecture/mandates.yml:60; plugins/arch-compliance/python/acf/detectors/python_pack.py:77-82`
- reasoning: mandates.yml:60 is exemption_tokens: [fail-loud.bare-except-ok] on the fail-loud.bare-except row. _is_bare_or_exception flags only type None or ast.Name 'Exception'. A tuple handler is ast.Tuple and is not flagged.

#### C100 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/engine.py:8; plugins/arch-compliance/python/acf/engine.py:17-24`
- reasoning: engine.py imports only __future__ and pathlib (:8) and defines contains_backslash at :17-24. Adding re keeps it stdlib-only.

#### C101 — SURVIVED
- evidence: `README.md:66-74; plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23; plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15; plugins/arch-compliance/tests/test_registry.py:20-30`
- reasoning: README.md:66-74 is a parseable pipe table of detector id / mandate id for the seven Python ids (the TS ids are absent, consistent with the 'every Python key' wording). emptyCatch.ts:23 and explicitAny.ts:15 hold the literal mandate_id strings. test_registry.py:20-30 shows the inline-YAML pattern that the new cases can follow.

#### C102 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/build_artifacts.py:23; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:28-34; plugins/arch-compliance/hooks/posttooluse_gate.py:239-246`
- reasoning: dist/ is a default prefix (build_artifacts.py:23). The hook passes existing files to rel_paths (:239-246), so a dist/x.py fixture triggers the guard in both gates. The TS bridge requires the pack's node_modules (:28-34), which the existing TS tests already depend on. The ratchet runs only in the diff gate. The facade and FSM scanners take params from the row. Each row declaring only its gate's sites passes _row_shape and _check_builtin.

#### C103 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:109; plugins/arch-compliance/python/acf/cli_check_diff.py:184; plugins/arch-compliance/hooks/posttooluse_gate.py:226; plugins/arch-compliance/hooks/posttooluse_gate.py:295`
- reasoning: file_lines is a local dict in _scan_changed (:109, returned at :184) and in _scan_paths (:226, returned at :295). Both functions run inside their gate's scan try, so a call before the return sits under it, and mutating missing keys preserves the gate's own entries.

### Unanchored findings

- **important**: call_sites becomes routing-significant but stays a free list[str]. A misspelled Tier-1 site next to a valid one (e.g. [ci, hooks]) loads cleanly and silently drops the row from the PostToolUse gate. The rung-1 fix, a Literal call-site vocabulary that makes the typo unconstructable, is never considered.
  - evidence: `plugins/arch-compliance/python/acf/registry.py:21`
- **advisory**: One mutable ast.Module is shared across every host ast detector on a file, so a detector that transforms the tree silently changes what later detectors see. The spec states no immutability contract and no per-detector copy.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:351`
- **advisory**: scan_host_guards maps only missing, outside or unresolvable paths to []. A guard hit naming a directory resolves, then read_text raises OSError, and the whole gate fails with DetectorPackError instead of reporting the finding.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:353`
- **advisory**: The fresh_host_loader fixture deletes every sys.modules key added during a test, which also evicts third-party or plugin submodules first imported in that test and risks class-identity mismatches in later tests. Restricting it to _acf_host_* names and modules loaded from the host root would be safer.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:404`
- **advisory**: The llm prompt-id load check guards a value no runtime code dispatches on: run_judge only renders the detector into prompt text. The check also runs in acf-check-diff, not acf-check-llm where llm rows are consumed, so its justification ('a runtime consumer for LLM_PROMPT_IDS') is close to circular.
  - evidence: `plugins/arch-compliance/python/acf/judge.py:265`
- **advisory**: One of C76's reasons for deferring import is inaccurate. The SubagentStart hook and acf-check-llm never pass known_detectors, so a load-time import placed in the known_detectors branch would not run host code there; the real reason is the PostToolUse hook importing CI-only modules on every edit.
  - evidence: `plugins/arch-compliance/hooks/inject_constraints.py:104`

### Looked for but did not find

- Any production caller that resolves more than one repository per process (grep of cli_check_diff/_scan_changed/posttooluse_gate across plugins/arch-compliance): none; only test_diff_cli.py:9 in-process main() calls
- A shipped registry row that the new row-shape or built-in contract checks would refuse (Appendix recipe run over config, both profiles and fixtures): none
- A shipped llm row whose detector is outside LLM_PROMPT_IDS: none
- A cycle introduced by acf.detectors importing acf.registry: none; the scanner modules import only engine/finding/exceptions
- A path from the hook's new deferred imports to acf.adr or acf.judge: none
- A built-in scanner that consults registry call_sites: none, which confirms the apply_registry filter is not redundant
- A repair-on-load or normalize-on-validate in the design's production code: none; every load and dispatch mechanism refuses with a typed AcfError
- A test pinning posttooluse_gate.py docstring line :12: none

### Mechanism traces

- **Mandate._row_shape model_validator**
  - invalid state: row.detection in {ast,guard} and (':' in detector and the host reference is malformed) or (status != unenforced and call_sites ∩ TIER1 = ∅) or (active host ast row and languages == 'none')
  - producer: `plugins/arch-compliance/python/acf/loader.py:71`
  - rung 1 (highest applicable 1); repairs=False
  - hardening rejected because: Row-shape rules live on Mandate; rules that need outside data live in load_mandates.
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:182`
- **_check_builtin built-in detector contract in load_mandates**
  - invalid state: active built-in ast/guard row with detector ∉ KNOWN_DETECTORS, or id != KNOWN_DETECTORS[detector].mandate_id, or (call_sites ∩ TIER1) − contract.call_sites ≠ ∅
  - producer: `plugins/arch-compliance/python/acf/loader.py:71`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: registry.py imports ... nothing from acf.detectors; rules that need outside data live in load_mandates.
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:257`
- **load_mandates llm_prompt_ids check**
  - invalid state: status != unenforced and detection == 'llm' and detector ∉ LLM_PROMPT_IDS
  - producer: `plugins/arch-compliance/python/acf/loader.py:71`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: registry.py cannot import acf.judge, so the ids are passed in rather than imported.
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:229`
- **Host detector file existence check in load_mandates**
  - invalid state: active host ast/guard row where resolve_under_root(repo_root, rel_path) is None or not a file, or repo_root is None
  - producer: `plugins/arch-compliance/python/acf/loader.py:71`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: Import and callable lookup happen only at dispatch (§4.4), so load_mandates runs no host code for any caller.
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:248`
- **apply_registry call_sites filter**
  - invalid state: finding f where registry.by_id[f.mandate_id].runs_at(gate_call_sites) is False
  - producer: `plugins/arch-compliance/python/acf/cli_check_diff.py:127`
  - rung 2 (highest applicable 2); repairs=False
  - hardening rejected because: This filter is needed at that one sink because the built-in scanners emit findings without consulting the registry.
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:41`
- **TS_MANDATE_IDS stamping and mismatch refusal in typescript_bridge**
  - invalid state: Node scanner item with detector ∉ TS_MANDATE_IDS or mandate_id != TS_MANDATE_IDS[detector]
  - producer: `plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23`
  - rung 2 (highest applicable 1); repairs=False
  - hardening rejected because: the bridge stamps the Python value and refuses a Node value that differs (§4.3), so the Node literal is a checked echo, not a second source.
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:280`
- **HostHit model (frozen, extra=forbid, validated path/line/message)**
  - invalid state: host result carrying mandate_id/severity/detector, or a path that is absolute/backslashed/dot-segmented, line < 1, or empty message
  - producer: `hm:scripts/ci/metadata_facade_guard.py:184`
  - rung 1 (highest applicable 1); repairs=False
  - hardening rejected because: The runner builds each Finding from the hit and the mandate row, so a host cannot attach a finding to the wrong row and no field is overwritten.
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:295`
- **_to_findings refusal of non-HostHit items and mismatched ast paths**
  - invalid state: item not isinstance HostHit, or (detection == 'ast' and hit.path != expected_path)
  - producer: `hm:scripts/ci/metadata_facade_guard.py:184`
  - rung 3 (highest applicable 1); repairs=False
  - hardening rejected because: The ast path check refuses rather than making a wrong path unrepresentable, because one HostHit type serves both callable kinds, and a path-less ast hit would be a second type carrying the same facts.
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:348`
- **_call_host wrapped call and materialisation**
  - invalid state: host callable raises (SystemExit included), returns None/str/bytes/non-iterable, or its iterator raises while consumed
  - producer: `hm:scripts/ci/metadata_facade_guard.py:184`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: Host code is an external boundary; the runner re-raises as DetectorPackError rather than swallowing.
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:335`
- **load_host_detector one-root-per-process refusal**
  - invalid state: load_host_detector called with repo_root.resolve() != _ACTIVE_ROOT within one process
  - producer: `plugins/arch-compliance/tests/test_diff_cli.py:9`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: Production callers resolve one repository per process ... In-process tests over several roots reset the loader through a test fixture.
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:49`
- **sys.modules removal when exec_module raises**
  - invalid state: sys.modules[_acf_host_<hash>] holds a partially executed module whose exec_module raised
  - producer: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:321`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: The module is registered in sys.modules before exec_module, which dataclasses needs to resolve string annotations, and removed if exec_module raises.
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:327`
- **fresh_host_loader test fixture**
  - invalid state: _ACTIVE_ROOT/_MODULE_CACHE, sys.path or sys.modules still hold a previous test's host root or modules
  - producer: `plugins/arch-compliance/tests/test_diff_cli.py:9`
  - rung 5 (highest applicable 5); repairs=True
  - hardening rejected because: In-process tests over several roots reset the loader through a test fixture (§4.6).
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:404`
- **resolve_under_root mapping RuntimeError (symlink loop) to None**
  - invalid state: (root / rel).resolve() raises RuntimeError on Python 3.11/3.12 because of a symlink loop
  - producer: `plugins/arch-compliance/python/acf/adr/citations.py:76`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: resolve_under_root maps the loop to None, the value every caller already treats as "not under the root" ... it never ends as a traceback.
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:114`
- **scan_host_guards filling file_lines for flagged files (errors="replace")**
  - invalid state: host-guard finding f with f.path ∉ file_lines, so line_lookup returns '' and the row's exemption token is invisible
  - producer: `plugins/arch-compliance/python/acf/cli_check_diff.py:126`
  - rung 2 (highest applicable 2); repairs=True
  - hardening rejected because: The guard read uses errors="replace" because an exemption token is ASCII: a stray undecodable byte elsewhere on the line must neither crash the gate nor hide the token.
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:353`
- **Hook in_repo_rel_paths restriction for host dispatch**
  - invalid state: edited path outside repo whose rel is an absolute POSIX string reaching host ast/guard dispatch
  - producer: `plugins/arch-compliance/hooks/posttooluse_gate.py:245`
  - rung 2 (highest applicable 2); repairs=False
  - hardening rejected because: rel_paths keeps its current contents for the build-artifact guard. Only in-repo paths reach host dispatch.
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:396`
- **KNOWN_DETECTORS call-site contract plus contract-against-dispatch test**
  - invalid state: KNOWN_DETECTORS[d].call_sites differs from the set of gates whose dispatch code actually runs detector d
  - producer: `plugins/arch-compliance/python/acf/cli_check_diff.py:168-182`
  - rung 3 (highest applicable 2); repairs=False
  - hardening rejected because: No shared Tier-1 dispatcher ... Merging them is left out to keep this change small.
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:46`

## Claims

- **C1** [premise] [load-bearing]: Today load_mandates (registry.py:48-64) skips every row whose status is not 'enforced' (:58) and raises UnknownDetectorError (:60-63) only for an enforced ast/guard row whose detector is not in known_detectors.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:58`
- **C2** [root_cause] [load-bearing]: Root cause of the registry/gate disagreement: a status: partial row is live in both Tier-1 gates (enforcement.py:47 drops only 'unenforced'; the gates' row filters likewise), yet load_mandates never checks it, so a host can name a non-built-in detector in a partial ast/guard row today, load cleanly with known_detectors=KNOWN_DETECTORS, and have nothing ever execute it.
  - spec citation: `plugins/arch-compliance/python/acf/enforcement.py:47`
- **C3** [premise] [load-bearing]: KNOWN_DETECTORS (cli_check_diff.py:25) is the closed union ALL_PYTHON_DETECTOR_IDS | TS_DETECTOR_IDS | LLM_PROMPT_IDS and nothing extends it (recipe: git grep -n "KNOWN_DETECTORS" -- plugins tests); because it includes the LLM prompt ids, an active ast row naming an LLM prompt id passes load_mandates' known_detectors check today although no Tier-1 scanner dispatches on that id.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:25`
- **C4** [premise] [load-bearing]: Neither gate can execute a non-built-in detector: _scan_changed (cli_check_diff.py:102-184) and _scan_paths (posttooluse_gate.py:213-295) call only built-in scanners, selected by exact built-in id (cli_check_diff.py:94-99, posttooluse_gate.py:229-236, :284-286), and no dynamic loader exists in the plugin runtime (git grep for importlib|import_module|spec_from_file_location|exec_module over plugins/arch-compliance/python and plugins/arch-compliance/hooks prints nothing).
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:102-184`
- **C5** [root_cause] [load-bearing]: Root cause of the hook defect: posttooluse_gate.py:107 calls load_mandates(mandates_path) without known_detectors, so an active row naming an unknown detector is never validated in the PostToolUse hook and produces zero findings at edit time instead of failing loud.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:107`
- **C6** [premise] [load-bearing]: posttooluse_gate.py:108 catches only AcfInputError around load_mandates, and UnknownDetectorError subclasses AcfError, not AcfInputError (exceptions.py:5, :13), so passing known_detectors in the hook requires also catching UnknownDetectorError there.
  - spec citation: `plugins/arch-compliance/python/acf/exceptions.py:13`
- **C7** [premise] [load-bearing]: Mandate.call_sites is list[str] (registry.py:21) and no Tier-1 gate reads it: the gates select rows on detector id and status only and apply_registry on status only; git grep -n "call_sites" -- plugins/arch-compliance/python plugins/arch-compliance/hooks prints only registry.py:21 and two unrelated surface_call_sites lines in acf/adr/ledger.py.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:21`
- **C8** [premise] [load-bearing]: This repository's no-shims.hasattr row declares call_sites: [ci] (config/architecture/mandates.yml:70), the PostToolUse hook reports it at edit time today, and plugins/arch-compliance/tests/test_hooks.py:199-218 is a test that pins that behaviour (so unifying call_sites routing necessarily changes that test).
  - spec citation: `plugins/arch-compliance/tests/test_hooks.py:199-218`
- **C9** [root_cause] [load-bearing]: Root cause of the exemption defect: the _line_lookup closures (cli_check_diff.py:76-80, posttooluse_gate.py:119-123) are token-identical and consult only file_lines, which holds changed .py/.ts/.tsx files (cli_check_diff.py:126, :152; posttooluse_gate.py:248-252), so a finding on any other file gets "" and apply_registry (enforcement.py:49-50) cannot see an inline exemption token on it.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80`
- **C10** [premise] [load-bearing]: test_hooks_do_not_reach_acf_adr pins only the literal text 'acf.adr' in the two hook files and states the intent that acf.adr must never enter the hooks' import graph; acf.registry and acf.enforcement are imported by the PostToolUse hook; and acf.adr already imports acf.engine (adr/contract.py:20). So moving the two path helpers into acf.engine keeps the dependency direction acf.adr -> acf.engine and keeps acf.adr out of the hook's graph.
  - spec citation: `plugins/arch-compliance/tests/test_adr_import_graph.py:70-76`
- **C11** [premise] [load-bearing]: The Tier-2 judge selects llm rows by detection and reads status == 'enforced' only to decide whether a provider is required (judge.py:213-218); it does not use the Tier-1 row filters being replaced, so leaving it unchanged creates no divergence the design must resolve.
  - spec citation: `plugins/arch-compliance/python/acf/judge.py:213-218`
- **C12** [premise] [load-bearing]: Trust seam: posttooluse_gate.py:72-81 exits 0 when .acf/enabled is absent, before importing anything beyond acf.repo and before loading mandates.yml, so no host module can be imported by the hook without the marker.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:72-81`
- **C13** [premise] [load-bearing]: .acf/ is gitignored (.gitignore:8) and this repository's CI invokes acf.cli_check_diff (.github/workflows/ci.yml:40), so a CI checkout never carries .acf/enabled; acf-check-diff does not check the marker today, and requiring it there would disable CI.
  - spec citation: `.gitignore:8`
- **C14** [premise] [load-bearing]: hooks/inject_constraints.py catches AcfInputError around its load_mandates call (:104-105), so making a malformed host reference raise AcfInputError needs no change there; cli_check_llm.py:54 also needs none.
  - spec citation: `plugins/arch-compliance/hooks/inject_constraints.py:105`
- **C15** [premise] [load-bearing]: Because load_mandates never imports host code under the design (validation is syntax, call sites, languages and file existence only), the SubagentStart hook (inject_constraints.py:104) and acf-check-llm (cli_check_llm.py:54) run no host code; no other path from those two entry points reaches load_host_detector.
  - spec citation: `plugins/arch-compliance/hooks/inject_constraints.py:104`
- **C16** [premise]: Deferral: no architecture-review runtime package and no architecture-review host configuration file exist at a338cad (recipe git ls-files plugins/arch-compliance/python/acf | grep -i review prints nothing); both belong to an unwritten Spec 2b. (Not load-bearing: this design touches neither.)
  - spec citation: `None`
- **C17** [premise] [load-bearing]: Deferral: the origin host's mandate rows (hm:config/architecture/mandates.yml at b652fab05) carry no languages or arch_anchor field, both of which Mandate requires (registry.py:20, :24), so they need rewriting at cutover regardless of this design; no change to HistoricMansions is needed in this slice.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:20`
- **C18** [premise] [load-bearing]: Deferral: the origin host's driver reports unparseable changed files (hm:scripts/ci/arch_compliance/driver.py:150-163) and its guards can depend on diff mode; scan_host_ast_file skips unparseable files like the built-in scanners and scan_guard receives no diff mode, and these gaps are left to the cutover spec. A host needing parse-failure reporting can declare it as a guard (scan_guard receives repo_root and every changed path, enough to re-parse).
  - spec citation: `hm:scripts/ci/arch_compliance/driver.py:150-163`
- **C19** [premise] [load-bearing]: No shared Tier-1 dispatcher is needed for ## Single point of definition: the host decision procedure (row selection, loading, calling, wrapping, Finding construction, guard-line reading and its precedence rule) has one implementation in acf.detectors.host, and each gate only calls scan_host_ast_file and scan_host_guards as it already calls each built-in scanner; the two pre-existing dispatch loops (cli_check_diff.py:102-184, posttooluse_gate.py:213-295) differ in diff scope, path collection and file filter and are not a second implementation of that procedure.
  - spec citation: `config/architecture/ARCHITECTURE.md:198-200`
- **C20** [premise]: scan_python_file returns [] on SyntaxError (python_pack.py:34-37), the convention scan_host_ast_file copies.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37`
- **C21** [premise] [load-bearing]: Appendix receipt: the load_mandates callers outside registry.py are exactly those the git grep recipe prints (inject_constraints.py:104, posttooluse_gate.py:107, cli_check_diff.py:70, cli_check_llm.py:54, acf-mandate SKILL.md:95 plus prose at :141, architecture-review SKILL.md:62, test_profile_drift.py:24, test_registry.py:10,17,30,47,57, tests/test_self_host.py:23); only cli_check_diff.py:70, SKILL.md:95, test_profile_drift.py:24, test_registry.py:30 and test_self_host.py:23 pass known_detectors, and the others reach only the syntax check. (Load-bearing: a caller passing known_detectors without repo_root raises AcfInputError on any active host row.)
  - spec citation: `None`
- **C22** [premise] [load-bearing]: Appendix receipt: apply_registry's callers are exactly posttooluse_gate.py:125, cli_check_diff.py:82 and test_enforcement.py at :54, 60, 66, 72, 84, 94, 104, 110, 125, 130 (recipe git grep -n "apply_registry(" -- '*.py'), so adding a required keyword call_sites touches only those.
  - spec citation: `None`
- **C23** [premise] [load-bearing]: Appendix receipt: the Tier-1 active-row filters are exactly cli_check_diff._active_mandates (:94-99; used at :112, :113, :158, :168), the hook's inline filters (posttooluse_gate.py:229-236 and :284-286, matched at :231, :235, :285) and apply_registry's status check (enforcement.py:47); the wider .status recipe adds only registry.py:58 (replaced), judge.py:218 (Tier-2) and a display-only read at inject_constraints.py:158.
  - spec citation: `None`
- **C24** [premise] [load-bearing]: Every built-in Tier-1 scanner stamps exactly one fixed mandate_id on its findings (build_artifacts.py:31, facade_sinks.py:69, fail_loud_ratchet.py:132, fsm_guard.py:59, python_pack.py:67/97/144/172; TypeScript emptyCatch.ts:23 and explicitAny.ts:15), and apply_registry matches findings to rows by mandate_id (enforcement.py:46), so a row whose id differs from its detector's stamped id never receives a finding.
  - spec citation: `None`
- **C25** [premise] [load-bearing]: fail_loud_ratchet runs only in acf-check-diff (cli_check_diff.py:168-182); the hook's _scan_paths has no ratchet call. Every other built-in ast/guard detector (three python_pack ids, two TS ids, forbid_facade_sink, fsm_transition_guard, no_build_artifacts) runs in both gates, at the lines in the spec's section 4.3 table.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:168-182`
- **C26** [premise] [load-bearing]: Executed census: applying the section 4.2 _check_builtin rules with the section 4.3 table and the Mandate._row_shape rules refuses no row in config/architecture/mandates.yml, plugins/arch-compliance/profiles/*/mandates.yml, plugins/arch-compliance/tests/fixtures/mandates_valid.yml, or any inline YAML registry in plugins/arch-compliance/tests (test_diff_cli.py, test_registry.py, test_judge.py, test_hooks.py), except test_registry.py's not_a_real_detector row, which is meant to raise UnknownDetectorError. Also check rows that test_hooks.py and test_diff_cli.py write by editing copied fixtures.
  - spec citation: `None`
- **C27** [premise] [load-bearing]: An AcfInputError raised inside a Mandate model_validator propagates with its own type through load_model_file (which catches only pydantic ValidationError, loader.py:70-73) and through direct Mandate(...) construction; MandateRegistry._unique_ids (registry.py:33-41) already relies on this. Direct Mandate construction in tests (test_enforcement.py:19, test_judge.py:41, test_template.py:73) is not refused by the new _row_shape validator.
  - spec citation: `plugins/arch-compliance/python/acf/loader.py:70-73`
- **C28** [premise] [load-bearing]: Every current user of KNOWN_DETECTORS (cli_check_diff.py:25,70; acf-mandate SKILL.md:91,95,106,111,112; test_profile_drift.py:7,24; tests/test_self_host.py:5,14,23; ARCHITECTURE.md:228) keeps working when it becomes a Mapping[str, BuiltinDetector] re-exported from acf.detectors, including sorted(KNOWN_DETECTORS) in the skill. test_registry.py:30 passes a frozenset and is listed to change.
  - spec citation: `None`
- **C29** [premise] [load-bearing]: Every production caller resolves exactly one repository per process (cli_check_diff.py:63; posttooluse_gate.py:65, a fresh process per edit), so refusing a second host root in load_host_detector never fires in production; only in-process tests over several roots need the fresh_host_loader fixture.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:63`
- **C30** [premise]: KNOWN_DETECTORS has 13 ids today (9 Python and TypeScript ids plus 4 LLM prompt ids) and 9 after the design. (Precision fact.)
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:25`
- **C31** [deletion] [load-bearing]: Deleting citations._looks_absolute (:49-51) and _escapes_repo (:74-76) is safe: their only references are the call sites at citations.py:161 and :163 (no test or other module imports them), resolve_citation (:129-185) keeps its order, and replacing them with acf.engine.looks_absolute and resolve_under_root changes exactly one classification: a drive-relative string such as "C:a/b.py" becomes external.
  - spec citation: `plugins/arch-compliance/python/acf/adr/citations.py:49-51`
- **C32** [deletion] [load-bearing]: Deleting the two _line_lookup closures (cli_check_diff.py:76-80, posttooluse_gate.py:119-123) for make_line_lookup(file_lines), which is their body unchanged and reads no file, changes no exemption result for any finding at a338cad. The only new lines in file_lines are those scan_host_guards adds for files a host guard flags, so a built-in finding on such a file becomes exemptable as built-in findings on changed code files already are; a built-in finding on any other file still gets ''.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80`
- **C33** [deletion] [load-bearing]: Deleting cli_check_diff._active_mandates and the hook's inline filters in favour of registry.active(call_sites, detector=...) changes no selection except by call_sites: for every shipped registry, the only built-in row that stops running at a gate is no-shims.hasattr leaving the PostToolUse hook (it declares [ci]).
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99`
- **C34** [deletion] [load-bearing]: Removing LLM_PROMPT_IDS from KNOWN_DETECTORS changes behaviour only for ast/guard rows naming an LLM prompt id: load_mandates consults known_detectors only for ast/guard rows (registry.py:60), and no code reads KNOWN_DETECTORS for llm rows. The import at cli_check_diff.py:21 stays and feeds load_mandates(..., llm_prompt_ids=LLM_PROMPT_IDS), so LLM_PROMPT_IDS keeps a runtime consumer.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:21`
- **C35** [deletion] [load-bearing]: Replacing the literal mandate ids in the five scanner modules with module constants changes no emitted finding, and no test asserts on the scanner source text in a way the change would break.
  - spec citation: `None`
- **C36** [premise] [load-bearing]: load_mandates with llm_prompt_ids=LLM_PROMPT_IDS refuses no shipped row: every active llm row in config/architecture/mandates.yml, plugins/arch-compliance/profiles/*/mandates.yml, tests/fixtures/mandates_valid.yml and the inline registries loaded by acf-check-diff, tests/test_self_host.py or the acf-mandate snippet names an id in acf.judge.LLM_PROMPT_IDS (judge.py:29-36); the acf-mandate SKILL.md:56 and :121 prompt-id rule is then enforced at acf-check-diff.
  - spec citation: `None`
- **C37** [premise] [load-bearing]: getattr(mod, attr, None) swallows only AttributeError, so a host module-level __getattr__ raising anything else escapes a bare lookup; in v4 §4.4 item 3 exec_module and the lookup share one try catching (Exception, SystemExit) that raises UnknownDetectorError, which cli_check_diff.py:72 and the hook's widened scan except catch. A failed exec_module removes the module from sys.modules; a failed lookup on a cached module leaves it cached.
  - spec citation: `None`
- **C38** [premise] [load-bearing]: pyproject.toml:5 allows Python 3.11, where a non-strict Path.resolve() raises RuntimeError on a symlink loop (3.13 does not); resolve_under_root catching RuntimeError and returning None makes a looping host path report as a missing file at load (UnknownDetectorError), yield [] exemption lines in scan_host_guards, or classify as unresolved in citations, never a traceback.
  - spec citation: `pyproject.toml:5`
- **C39** [premise] [load-bearing]: The TypeScript bridge's Finding construction sits in a try at typescript_bridge.py:82-95 whose except (KeyError, TypeError, ValueError) re-raises as DetectorPackError (:94-95); stamping mandate_id=TS_MANDATE_IDS[item['detector']] and raising ValueError on a differing item['mandate_id'] inside it yields DetectorPackError for an unknown detector or a mismatch, and the Node rules' literals (emptyCatch.ts:23, explicitAny.ts:15) equal the TS_MANDATE_IDS values, so no shipped finding is refused.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:82-95`
- **C40** [premise] [load-bearing]: Decision 6's entry-point table is accurate: under the PostToolUse hook (hooks.json runs posttooluse_gate.py; sys.path[0] is the hooks dir, then the plugin python/ at :22-26) and the acf-check-diff console script (pyproject.toml:19-20), the host root is not on sys.path before the loader appends it and the plugin's acf is imported first (:28); under python -m acf.cli_check_diff run from the host root (.github/workflows/ci.yml:40) the working directory is already sys.path[0], so appending changes nothing there and the existing exposure is neither created nor removed by the design. Host intra-repo imports such as hm:scripts/ci/metadata_facade_guard.py:66 resolve against the host root in the documented invocations.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:22-28`
- **C41** [premise]: No caller today tells ci from precommit or hook from posttooluse: acf-check-diff is the one diff-gate entry for both CI and pre-commit and receives no flag saying which, and the hook is one script; so DIFF_CALL_SITES and HOOK_CALL_SITES each merging two names, a consequence Decision 2 states, loses no information a caller supplies.
  - spec citation: `None`
- **C42** [premise] [load-bearing]: file_lines holds only changed .py/.ts/.tsx files (cli_check_diff.py:126, :152; posttooluse_gate.py:248-252) plus, after v4, files a host guard flagged; built-in line-1 findings (fail_loud_ratchet.py:135, build_artifacts.py:34) on any other file still get '' and stay non-exemptable, as at a338cad, and a staged dist/x.py is already in file_lines today.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:135`
- **C43** [mandate] [load-bearing]: ## Fail loud: every invalid state in spec §6.1 is refused by the named component with the named error, including: a host module whose import or callable lookup raises (one wrapped region, UnknownDetectorError); a host callable that raises, a generator that raises or yields an invalid HostHit while consumed, or sys.exit (_call_host, DetectorPackError); an unreadable file a host guard flags (scan_host_guards, DetectorPackError); a TypeScript scanner item with an unknown detector or a differing mandate_id (DetectorPackError); and an active llm row with an unknown prompt id (UnknownDetectorError). The broad handlers re-raise typed errors, so none swallows.
  - spec citation: `None`
- **C44** [mandate] [load-bearing]: ## Fail loud: no active built-in ast/guard row can load with known_detectors yet never receive a finding from either Tier-1 gate: _check_builtin refuses a detector not in KNOWN_DETECTORS (LLM prompt ids are not keys), a row id that differs from the detector's stamped mandate_id, and any declared Tier-1 call site outside the detector's contract call_sites (fail_loud_ratchet: DIFF only); and Mandate._row_shape refuses an active ast/guard row with no Tier-1 site. Host rows are dispatched by both gates' host runners at any Tier-1 site.
  - spec citation: `None`
- **C45** [mandate] [load-bearing]: ## Declared, never defaulted: load_mandates requires an explicit repo_root for an active host detector row (AcfInputError otherwise, never derived), and apply_registry's new call_sites keyword has no default.
  - spec citation: `config/architecture/ARCHITECTURE.md:118-133`
- **C46** [mandate]: ## No shims: callable lookup is getattr(mod, attr, None) followed by callable() and a raise; no hasattr, and no host-detector failure has a silent fallback.
  - spec citation: `config/architecture/ARCHITECTURE.md:43-53`
- **C47** [mandate]: ## POSIX paths: HostHit.path is validated by validate_posix_rel_path (which refuses backslashes) and error messages use .as_posix().
  - spec citation: `config/architecture/ARCHITECTURE.md:55-64`
- **C48** [mandate]: ## One base exception: the design adds no exception class and uses AcfInputError, UnknownDetectorError and DetectorPackError (exceptions.py:5, :13, :29), all subclassing AcfError.
  - spec citation: `plugins/arch-compliance/python/acf/exceptions.py:5`
- **C49** [mandate]: ## One owner for host paths: acf/engine.py, acf/registry.py, acf/detectors/__init__.py and the new acf/detectors/host.py spell no config/architecture path, and the acf-mandate skill snippet takes MANDATES_REL and resolve_repo from acf.repo.
  - spec citation: `None`
- **C50** [mandate]: ## Prose names no host: the runtime messages in §4.2-§4.4 and the prose changes in §4.8 name no origin host.
  - spec citation: `config/architecture/ARCHITECTURE.md:135-143`
- **C51** [mandate]: ## Live consumers: each new export in §6.2 has the named non-test caller, and the existing acf.judge.LLM_PROMPT_IDS, which leaves KNOWN_DETECTORS, keeps a runtime consumer (acf-check-diff's load_mandates(..., llm_prompt_ids=...)) and a skill consumer (the acf-mandate ## Validate snippet); TS_MANDATE_IDS is read by scan_typescript_file and KNOWN_DETECTORS.
  - spec citation: `None`
- **C52** [mandate]: ## No completeness claims: every population claim in the spec carries a re-runnable recipe (§1, §3, Appendix) or is a per-item table, as ARCHITECTURE.md:159-169 requires.
  - spec citation: `config/architecture/ARCHITECTURE.md:159-169`
- **C53** [mandate]: ## Declared text decoding: the new read_text calls (cli_check_diff.py TypeScript branch, scan_host_guards' read of flagged files) declare encoding='utf-8'; errors='replace' in scan_host_guards is permitted by that rule, which governs the declared encoding; no subprocess is added.
  - spec citation: `None`
- **C54** [mandate]: ## Release discipline: because shipped skill prose changes, the version is bumped 0.2.2 -> 0.2.3 in both files ARCHITECTURE.md:186-187 names (pyproject.toml:3, plugins/arch-compliance/.claude-plugin/plugin.json:3).
  - spec citation: `config/architecture/ARCHITECTURE.md:184-194`
- **C55** [mandate]: ## Single point of definition: within the Tier-1 gates, the absolute and under-root string tests are defined once in acf.engine, row activity once in Mandate.runs_at, each built-in Python mandate id once in a scanner constant, the TypeScript mandate ids once in TS_MANDATE_IDS (the bridge stamps from it and refuses a differing Node value), host loading, running and guard-line reading once in acf.detectors.host, and line lookup once in make_line_lookup; where each built-in runs is declared in KNOWN_DETECTORS and tied to the gates' dispatch by the contract-against-dispatch test; the one remaining breach, the ratchet's path joins, is recorded in the doctrine's breach list.
  - spec citation: `None`
- **C56** [mandate]: ## Scoped refactor: the consolidations (line lookup, active-row filters, citations' path helpers) touch only code paths this design changes; the shared dispatcher is a declared non-goal.
  - spec citation: `config/architecture/ARCHITECTURE.md:211-215`
- **C57** [mandate]: ## Frozen ledger format: the design changes no ledger model.
  - spec citation: `config/architecture/ARCHITECTURE.md:145-151`
- **C58** [mandate]: The design complies with the five portable governing principles at docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51 and fulfils that spec's call for project-specific detector extension points (:102, :123, :125).
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51`
- **C59** [mandate]: ## Fail loud: scan_host_guards mapping a missing, out-of-root or unresolvable flagged path to [] and decoding with errors='replace' hides no failure: such a path has no line that could carry an exemption token, so the finding stays; an OSError while reading raises DetectorPackError inside each gate's scan try; and make_line_lookup does no I/O.
  - spec citation: `None`
- **C60** [shape_fit] [load-bearing]: Mandate.runs_at and MandateRegistry.active become the single definition of 'this row runs at this gate' for the Tier-1 gates; after the change no other Tier-1 site (cli_check_diff, posttooluse_gate, enforcement, the host runners) keeps its own active-row filter.
  - spec citation: `None`
- **C61** [shape_fit] [load-bearing]: looks_absolute and resolve_under_root in acf.engine subsume citations' private helpers and are the absolute and under-root tests used by validate_posix_rel_path, load_mandates, load_host_detector, scan_host_guards and acf/adr/citations.py; the fail-loud ratchet's params.baseline/params.roots joins (fail_loud_ratchet.py:46, :122-124) are the one other registry-path-to-file implementation and are recorded as PARTIAL_OVERLAP debt (§3, §4.1, §4.8, §5.2) rather than claimed adjacent.
  - spec citation: `None`
- **C62** [shape_fit] [load-bearing]: Building Finding from a validated HostHit in acf.detectors.host is ADJACENT to, not a partial duplicate of, the TypeScript bridge's JSON-to-Finding coercion (typescript_bridge.py:75-95), because the inputs share no format.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:75-95`
- **C63** [shape_fit] [load-bearing]: Building Finding from a HostHit is ADJACENT to the judge's _to_finding (judge.py:236-253): the judge demotes severity by confidence and admits path="<diff>" and line=0, while host findings take severity from the row and require a relative path and line >= 1, so no shared constructor is warranted.
  - spec citation: `plugins/arch-compliance/python/acf/judge.py:236-253`
- **C64** [shape_fit] [load-bearing]: acf/detectors/host.py partially duplicates no existing mechanism: nothing in the plugin today loads or executes code from a registry-supplied file path, and the loader's one-time append of a host root to the end of sys.path is ADJACENT to the hooks' own start-up insertion of the plugin's python/ directory (posttooluse_gate.py:22-26, inject_constraints.py:28-29).
  - spec citation: `None`
- **C65** [shape_fit] [load-bearing]: make_line_lookup consolidates the only two line-lookup closures passed to apply_registry; no third LineLookup implementation exists (e.g. in cli_check_llm.py, the judge, or any skill snippet) that would remain a second definition.
  - spec citation: `None`
- **C66** [shape_fit] [load-bearing]: Detector-reference validation lives in two cooperating places only, Mandate._row_shape (row-local rules, every caller) and load_mandates with known_detectors (built-in contracts and host-file existence); no other validator (the acf-mandate skill's ## Validate snippet, test_profile_drift.py, the architecture-review skill, acf-setup) independently checks detector ids or call sites in a way that would diverge.
  - spec citation: `None`
- **C67** [shape_fit]: Host dispatch in the hook reuses the hook's existing abs_path.relative_to(repo) try/except ValueError (posttooluse_gate.py:242-245) to record in-repo paths in a separate in_repo_rel_paths list, rather than adding a second in-repo test; rel_paths keeps its current contents for the build-artifact guard.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:242-245`
- **C68** [sweep] [load-bearing]: Sweep: the call-site vocabulary in use across shipped registries and docs is {ci, precommit, hook, posttooluse, audit} (config/architecture/mandates.yml; ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:104); every value except audit falls in DIFF_CALL_SITES or HOOK_CALL_SITES, and audit is read by no Tier-1 gate, so the partition misroutes no shipped row.
  - spec citation: `None`
- **C69** [sweep] [load-bearing]: Sweep: the test changes in spec §4.7 cover every existing test the design breaks or makes stale: the ten apply_registry calls in test_enforcement.py, test_hooks.py:199-218, test_registry.py:30, tests/test_self_host.py:23 and its :5 docstring, the test_acf_mandate_skill.py:2 docstring; no other existing test depends on the hook reporting a [ci]-only row, apply_registry's old signature, citations' private helpers, KNOWN_DETECTORS containing LLM prompt ids or being a frozenset, the TypeScript bridge copying mandate_id from Node, scanner source literals, or load_mandates accepting a row the new rules refuse.
  - spec citation: `None`
- **C70** [shape_fit] [load-bearing]: The §4.7 contract-against-dispatch test ties KNOWN_DETECTORS' call_sites to the gates' dispatch: a detector the table says runs at a gate but which that gate does not dispatch fails the test; the opposite drift cannot attach a finding to any loaded row, because _check_builtin refuses a row declaring that site and apply_registry drops a finding whose row does not run at the gate, so it over-refuses and never silently drops a row.
  - spec citation: `None`
- **C71** [shape_fit] [load-bearing]: resolve_under_root (relative string -> contained Path) is ADJACENT to abs_path.relative_to(repo) at posttooluse_gate.py:242-245 and the ratchet walk filter at fail_loud_ratchet.py:59-62 (resolved absolute Path -> relative string): they are opposite operations, not two implementations of one.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:242-245`
- **C72** [shape_fit] [load-bearing]: Host code runs in exactly two wrapped regions with distinct errors: module execution plus callable lookup in load_host_detector (UnknownDetectorError) and calling plus consuming the result in _call_host (DetectorPackError); the fresh_host_loader fixture in plugins/arch-compliance/tests/conftest.py is the single reset of loader state, and no production path resets _ACTIVE_ROOT.
  - spec citation: `None`
- **C73** [sweep]: The §4.7/§4.8 sites cover every shipped doc, skill, module docstring and test docstring made stale by the design: KNOWN_DETECTORS described as a union including LLM prompt ids or 'the one detector union' (acf-mandate SKILL.md:18, :106-112; tests/test_self_host.py:5; test_acf_mandate_skill.py:2; PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:84, :418-420, :425, :500), the hook scanning only code files or reporting [ci]-only rows, apply_registry's drop rules (enforcement.py:6-8), and the call-site vocabulary.
  - spec citation: `None`
- **C74** [shape_fit] [load-bearing]: Under v4 TS_MANDATE_IDS is the single Python definition of the TypeScript mandate ids: the bridge stamps from it, KNOWN_DETECTORS reads it, and no other non-test Python site spells 'fail-loud.empty-catch' or 'no-shims.explicit-any' as a runtime value; the Node literals are checked against it on every finding.
  - spec citation: `None`
- **C75** [shape_fit]: apply_registry is the single owner of Finding.severity on the Tier-1 path (enforcement.py:52); the host runner's severity value is a required-field fill that apply_registry overwrites, as §4.4 item 5 and §5.2 state.
  - spec citation: `None`
- **C76** [mechanism_justification] [load-bearing]: Deferring host import to dispatch (load_mandates checks reference syntax, Tier-1 site, languages, built-in contracts and host-file existence, and imports nothing) is justified: a missing file still fails at load, an import failure or missing callable fails loud at dispatch as UnknownDetectorError caught by both gates' except tuples, and importing at load would run host code in the SubagentStart hook and acf-check-llm and import CI-only guards on every edit.
  - spec citation: `None`
- **C77** [mechanism_justification] [load-bearing]: The row-shape checks on Mandate (host-reference syntax, a Tier-1 site, host ast languages) together with the per-detector BuiltinDetector contracts (known id, matching mandate_id, declared Tier-1 sites within the contract's call_sites) are sufficient to prevent an active ast/guard row that loads with known_detectors yet is run by neither acf-check-diff (DIFF_CALL_SITES) nor the hook (HOOK_CALL_SITES), or whose findings land on no row.
  - spec citation: `None`
- **C78** [mechanism_justification] [load-bearing]: Refusing a second host root in one process (AcfInputError) rather than evicting the old root is justified: every production caller resolves one repository per process, so the refusal never fires in production, and the only multi-root producer (in-process tests) is handled by the test-only fresh_host_loader fixture; no repair mechanism lives in production code.
  - spec citation: `None`
- **C79** [mechanism_justification] [load-bearing]: Declaring, per built-in detector, the mandate id it reports to and the call sites where a gate runs it (BuiltinDetector in KNOWN_DETECTORS) is justified over the alternatives: the scanners stamp fixed mandate ids and run at fixed gates, so the contract records an existing fact rather than adding a capability; the accepted cost (at most one active row per built-in detector) affects no shipped registry.
  - spec citation: `None`
- **C80** [mechanism_justification]: Moving the row-local rules onto a Mandate model_validator (rather than keeping them in load_mandates) is justified because it makes the SubagentStart hook, acf-check-llm and any direct Mandate construction reject the same malformed rows as the gates, with no caller change since each already handles AcfInputError.
  - spec citation: `None`
- **C81** [mechanism_justification]: Parsing a Python file once and sharing the tree across every host ast detector on it is justified by avoiding N parses per file; built-in scanners keep their own parses unchanged.
  - spec citation: `None`
- **C82** [mechanism_justification] [load-bearing]: Having host callables return HostHit (path, line, message) and building Finding in the runner from the mandate row, rather than accepting Finding and overwriting fields, is justified because apply_registry matches findings to rows by mandate_id (enforcement.py:37-53) and a host-supplied mandate_id/detector/severity could otherwise attach a finding to the wrong row.
  - spec citation: `None`
- **C83** [mechanism_justification] [load-bearing]: Treating the host's own pre-commit/CI invocation of acf-check-diff as its opt-in to running host code, and gating only the automatic hooks on .acf/enabled, is justified because .acf/ is gitignored and CI would otherwise be disabled; a user who runs acf-check-diff manually in an untrusted checkout is the residual case the design accepts.
  - spec citation: `.gitignore:8`
- **C84** [mechanism_justification] [load-bearing]: The call_sites filter added to apply_registry is needed in addition to the scanners' registry.active(call_sites) selection, because some built-in scanners emit findings by detector id without consulting the registry's call_sites, so without the filter a finding for a row not declared at this gate would survive. (The spec states the filter but gives no reason it is not redundant.)
  - spec citation: `None`
- **C85** [mechanism_justification] [load-bearing]: Appending the host root to the end of sys.path rather than inserting it at the front is justified: it adds no shadowing of standard-library, third-party or plugin modules under the hook and console-script entry points, keeps host intra-repo absolute imports working from the host root, and its stated cost (a host top-level name an earlier entry provides resolves to that entry) fails at import or callable lookup as UnknownDetectorError in the common case; dropping the acf/ refusal removes a check with no producer.
  - spec citation: `None`
- **C86** [mechanism_justification] [load-bearing]: Reading flagged files in scan_host_guards, inside each gate's scan try, instead of lazily in the line lookup is justified: it keeps apply_registry free of I/O and new errors, converts an unreadable file to DetectorPackError where both gates already report it, and limits new exemption lines to files a host guard flagged.
  - spec citation: `None`
- **C87** [mechanism_justification]: Enforcing llm prompt ids at load (llm_prompt_ids, passed by acf-check-diff) is justified: it gives acf.judge.LLM_PROMPT_IDS a runtime consumer after it leaves KNOWN_DETECTORS, makes the acf-mandate skill's stated rule true, and refuses no shipped row; registry.py cannot import acf.judge, so the ids are passed in rather than imported.
  - spec citation: `None`
- **C88** [implementability] [load-bearing]: Mandate (registry.py:14-27) is a Pydantic BaseModel exposing every field the design reads: id, severity, status, detection, detector, call_sites (list[str]), languages (Literal including 'none'), and params (dict or None); adding an @property is_active and a plain method runs_at to it, and a method active to MandateRegistry, is compatible with its model_config.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:14-27`
- **C89** [implementability] [load-bearing]: Finding (acf/finding.py) can be constructed as Finding(mandate_id=, severity=Severity(mandate.severity), path=, line=, message=, detector=, detection=): those are its fields, Severity is constructible from Mandate.severity's value, and no other required field is missing.
  - spec citation: `None`
- **C90** [implementability] [load-bearing]: apply_registry (enforcement.py) looks up each finding's row via registry.by_id, drops it on the status check at :47 (replaceable by runs_at), and handles exemptions and severity at :49-52 using a LineLookup type that make_line_lookup can return.
  - spec citation: `plugins/arch-compliance/python/acf/enforcement.py:47`
- **C91** [implementability] [load-bearing]: cli_check_diff.py has the hook points the design names with the needed names in scope: load at :70 inside a try whose except tuple at :72 lists AcfInputError, UnknownDetectorError and DetectorPackError (and wraps both load and scan); lookup and apply_registry at :76-82; in the .py branch after scan_fsm_writes (:140-150) repo, text, posix, lines and registry; in the .ts/.tsx branch (:151-156) a read that can bind text; and after the ratchet loop (:168-182) the changed-file list.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:72`
- **C92** [implementability] [load-bearing]: posttooluse_gate.py has the hook points the design names: deferred imports at :91-104, the load try at :106-110, the scan try at :113-117 (whose except can be widened to AcfInputError, DetectorPackError, UnknownDetectorError), lookup/apply_registry at :119-125, inline filters at :229-236 and :284-286, the relative_to with ValueError fallback at :242-245 where an in_repo_rel_paths list can be recorded, the build-artifact loop at :284-294, and text and rel in scope in the .py and TypeScript branches of _scan_paths.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:113-117`
- **C93** [implementability] [load-bearing]: Host-detector failures reach an existing fail-loud handler in both gates, never a traceback: module execution and callable lookup raise UnknownDetectorError, a second root raises AcfInputError, _call_host wraps every exception from the call and from materialising its result plus SystemExit as DetectorPackError, an unreadable flagged file raises DetectorPackError inside the scan try, a looping host path resolves to None, and apply_registry does no I/O; cli_check_diff.py:72 and the hook's widened scan except catch all three error types.
  - spec citation: `None`
- **C94** [implementability] [load-bearing]: load_host_detector is implementable as stated: module-level _ACTIVE_ROOT and _MODULE_CACHE, a one-time sys.path.append of the root, a module name from sha256(rel_path), registering in sys.modules before exec_module and removing it if exec_module raises, and exec plus getattr in one try; and the conftest fresh_host_loader fixture (reset both globals, restore sys.path, drop added sys.modules keys) isolates in-process tests over several roots, including test_diff_cli.py's in-process main() calls.
  - spec citation: `None`
- **C95** [implementability] [load-bearing]: Registering the module in sys.modules under its name before spec.loader.exec_module(mod) is what lets a host module define a @dataclass under `from __future__ import annotations` (dataclasses resolves sys.modules[cls.__module__]); importlib.util.spec_from_file_location with a synthetic name supports this.
  - spec citation: `None`
- **C96** [implementability] [load-bearing]: The imports the design adds are cycle-free and allowed: acf.registry imports acf.engine, dataclass and Mapping, and nothing from acf.detectors; acf.detectors/__init__ imports acf.registry (BuiltinDetector, call-site sets) and the scanner modules' constants without a cycle; acf.cli_check_diff re-exports KNOWN_DETECTORS from acf.detectors; acf.detectors.host imports registry, finding, engine and exceptions; acf/adr/citations.py importing acf.engine is permitted by test_adr_import_graph.py; and the hook's new deferred imports (from acf.detectors, not acf.cli_check_diff) do not reach acf.adr or acf.judge.
  - spec citation: `plugins/arch-compliance/tests/test_adr_import_graph.py:70-76`
- **C97** [implementability] [load-bearing]: load_mandates today loads rows via load_model_file(path, Mandate, subject='mandates file', fmt='yaml', many=True) returning a list of Mandate, and builds MandateRegistry(mandates=..., source_path=path.as_posix()), so the §4.2 body is a drop-in extension of the existing function.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:48-64`
- **C98** [implementability]: plugins/arch-compliance/tests/test_repo_paths.py:47-48 pins the text of posttooluse_gate.py's docstring line :11 and not :12, so rewording :12 and keeping :11 verbatim breaks no test.
  - spec citation: `plugins/arch-compliance/tests/test_repo_paths.py:47-48`
- **C99** [implementability]: config/architecture/mandates.yml:60 declares fail-loud.bare-except-ok for fail-loud.bare-except; the design's handlers are tuple handlers `except (Exception, SystemExit)`, which _is_bare_or_exception (python_pack.py:78-82) does not flag, so they pass the gate whether or not they carry the token, and the spec says the token marks breadth for readers.
  - spec citation: `None`
- **C100** [implementability]: acf/engine.py already defines contains_backslash and is stdlib-only, so adding looks_absolute, resolve_under_root and validate_posix_rel_path with `import re` and `from pathlib import Path` keeps it stdlib-only and gives validate_posix_rel_path its backslash test without a new dependency.
  - spec citation: `plugins/arch-compliance/python/acf/engine.py`
- **C101** [implementability] [load-bearing]: The new tests are implementable against the shipped files: test_builtin_detectors.py can parse the README.md detector table (:66-74) for detector ids and mandate ids and read mandate_id values from emptyCatch.ts:23 and explicitAny.ts:15; and the test_registry.py cases (a fail_loud_ratchet row declaring hook, a fail_loud_bare_except row with another id, an ast row naming an LLM prompt id, a module that raises at import not imported by load_mandates) can be expressed as inline YAML registries like the existing :24 and :35 rows.
  - spec citation: `None`
- **C102** [implementability] [load-bearing]: The contract-against-dispatch test is implementable: for acf-check-diff in process on a temporary git repository and for the hook in a subprocess with .acf/enabled, a fixture tree can trigger each built-in detector the table assigns to that gate (python_pack's three ids, facade sink and FSM guard with params, build artifacts via a dist/ path, the ratchet via a baseline below the current count, and the two TypeScript rules via the Node pack the existing TypeScript tests use), with one active row per such detector declaring only that gate's sites.
  - spec citation: `None`
- **C103** [implementability] [load-bearing]: scan_host_guards(repo_root, changed_files, registry, file_lines, *, call_sites) is implementable in both gates: file_lines is in scope after each gate's dispatch (cli_check_diff _scan_changed returns it; _scan_paths builds it), the call can run inside _scan_changed and _scan_paths so it sits under each gate's scan try, and filling only missing keys keeps the gate's own reads.
  - spec citation: `None`
