# Adversarial design review — full detail

Spec: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md` @ `7da3f560feb0cfb3d144520e9ee4a3e33eebea65`
Kinds: defect, feature
Outcome: **BLOCKED**
Claims: 135 · Reviewers: 4 · Converged: 1

## Blocking reasons

- load-bearing claim C37 (premise) is REFUTED: The RepoTree.file None cases hold. The conclusion that a permission-denied stat 'ends in UnknownDetectorError or DetectorPackError, not a traceback' does not. The design says _collect_paths lets the OSError propagate, and _collect_paths is called at posttooluse_gate.py:112, outside any try: the scan try at :113-117 catches only DetectorPackError today and AcfInputError/DetectorPackError/UnknownDetectorError under the design. So in the hook it is an uncaught OSError traceback, as it is today. Likewise _scan_changed's tree.file runs under cli_check_diff.py:72, whose tuple has no OSError. The 'not a traceback' guarantee holds only for the four callers that wrap the call themselves.
- load-bearing claim C52 (deletion) is REFUTED: The reference facts hold: git grep shows only the definitions plus :161 and :163, and no test imports them. But 'exactly two behaviours change' is false. The spec's own section 4.1 (line 189) says 'Three behaviours change' and section 4.9 lists the third: a citation with an embedded NUL. Today _escapes_repo's (root / path).resolve() raises ValueError on it (on POSIX, and on 3.11 per the spec); under RepoTree.contained it classifies as unresolved. The claim's count contradicts the sections it cites.

## Absorptions

- SUBSUMED: 'RepoTree.contained / RepoTree.file' shares responsibility 'decide whether a path string names a location inside the repository root' with plugins/arch-compliance/hooks/posttooluse_gate.py:203-204 — The hook's is_absolute/resolve join and relative_to/except ValueError fallback (:242-245) collapse into RepoTree.file plus RepoTree.key, as the spec states.
- SUBSUMED: 'RepoTree.directory / RepoTree.key' shares responsibility 'contain ratchet roots and key walked files' with plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:46 — The roots join (:46), the exists-skip (:56-57) and the walk filter (:59-62) collapse into RepoTree.directory and RepoTree.key.
- PARTIAL_OVERLAP: 'RepoTree.file (load_baseline existence check)' shares responsibility 'load, parse and refuse a JSON input file' with plugins/arch-compliance/python/acf/loader.py:43-77 — Shared responsibility R is load-parse-refuse of an input file. Give the baseline a pydantic model (files: dict[str, int]) and load it through load_model_file after RepoTree.file containment, re-raising AcfInputError as DetectorPackError in scan_ratchet. load_baseline's is_file check, json.loads, shape checks and the untyped read error collapse into load_model_file.
- PARTIAL_OVERLAP: 'make_line_lookup' shares responsibility 'fetch a 1-based source line with bounds, empty when out of range' with plugins/arch-compliance/python/acf/detectors/fsm_guard.py:56 — Shared responsibility R is the bounded 1-based line fetch. Extract a stdlib helper (e.g. acf.engine.line_at(lines, line) -> str). make_line_lookup's body and fsm_guard's inline snippet expression both become callers of it.
- IDENTICAL: 'make_line_lookup' shares responsibility 'path-keyed line lookup passed to apply_registry' with plugins/arch-compliance/python/acf/cli_check_diff.py:76-80 — Both gate closures (here and posttooluse_gate.py:119-123) are deleted and the gates consume make_line_lookup.
- SUBSUMED: 'validate_hit_fields' shares responsibility "validate an external hit's line and message" with plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:88-89 — The bridge's int()/str() coercion becomes a validate_hit_fields call; HostHit uses the same function.
- PARTIAL_OVERLAP: 'scan_host_guards input (in_repo)' shares responsibility 'define the changed-path population a guard receives' with plugins/arch-compliance/python/acf/cli_check_diff.py:161-163 — Shared responsibility R is the set of changed paths handed to guards. Compute one guard-input list per gate and pass it to both scan_build_artifact_paths and scan_host_guards, or state why built-in guards see deleted paths and host guards do not.

## Converged findings

- [2 reviewers: hardening, sweeper] In acf-check-diff, host guards receive only the changed paths RepoTree.file accepts, so a deleted path never reaches them, while the built-in build-artifact guard still receives every git-changed path; this contradicts the spec's statement that a guard may flag a deleted file and that host guards see every changed path.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:118-120`
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:161-163`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:48-64; plugins/arch-compliance/python/acf/registry.py:60-63; plugins/arch-compliance/tests/test_registry.py:20-30`
- reasoning: I read load_mandates. Line 58 skips every row whose status is not 'enforced'. Lines 60-63 raise UnknownDetectorError only when detection is ast or guard and the detector is not in known_detectors. test_registry.py:20-30 pins the enforced-unknown case.

#### C2 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:25; plugins/arch-compliance/python/acf/judge.py:29-36; plugins/arch-compliance/python/acf/registry.py:60`
- reasoning: KNOWN_DETECTORS is defined once at :25 as ALL_PYTHON_DETECTOR_IDS | TS_DETECTOR_IDS | LLM_PROMPT_IDS. I ran git grep KNOWN_DETECTORS over plugins and tests: every hit only imports it, passes it on or prints it, and none extends it. Because the union contains the four LLM ids (judge.py:29-36), an enforced ast row naming llm_fail_loud passes the check at registry.py:60. No scanner in _scan_changed or _scan_paths dispatches on that id.

#### C3 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; plugins/arch-compliance/hooks/posttooluse_gate.py:216-236; plugins/arch-compliance/hooks/posttooluse_gate.py:284-286`
- reasoning: Both scan functions call only the imported built-in scanners. Rows are selected by exact built-in detector-id constants. I ran the stated git grep for importlib|import_module|spec_from_file_location|exec_module over the python and hooks directories, and it printed nothing.

#### C4 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:106-110; plugins/arch-compliance/python/acf/exceptions.py:5; plugins/arch-compliance/python/acf/exceptions.py:13`
- reasoning: The hook wraps load_mandates in except AcfInputError only. UnknownDetectorError(AcfError) is a sibling of AcfInputError(AcfError), not a subclass, so it would escape that handler.

#### C5 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:21; plugins/arch-compliance/python/acf/enforcement.py:46-47; plugins/arch-compliance/python/acf/adr/ledger.py:83`
- reasoning: The git grep for call_sites over python and hooks printed registry.py:21 plus ledger.py:42 and :83, which are about surface_call_sites. apply_registry filters on status only, and the gate filters (cli_check_diff.py:98, posttooluse_gate.py:231,235,285) use detector and status only.

#### C6 — SURVIVED
- evidence: `config/architecture/mandates.yml:64-73; plugins/arch-compliance/tests/fixtures/mandates_valid.yml:12-21; plugins/arch-compliance/tests/test_hooks.py:199-218`
- reasoning: The repository row declares call_sites [ci]. The fixture copied by _seed_host has the identical row. The test asserts that 'no-shims.hasattr' appears in the hook's additionalContext. The hook never reads call_sites, so the row is reported today, and routing by call_sites would break this test.

#### C7 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_import_graph.py:70-76; plugins/arch-compliance/hooks/posttooluse_gate.py:92-95; plugins/arch-compliance/python/acf/adr/contract.py:20; plugins/arch-compliance/python/acf/adr/host.py:16`
- reasoning: The test asserts only that the literal 'acf.adr' is absent from the two hook sources, and its docstring states the intent. The hook imports acf.enforcement and acf.registry. acf.adr already imports acf.engine (contract.py:20) and acf.repo (host.py:16), so placing the helpers in engine or repo keeps acf.adr out of the hook's import graph.

#### C8 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:213-218; plugins/arch-compliance/python/acf/judge.py:230; plugins/arch-compliance/python/acf/cli_check_llm.py:61-63`
- reasoning: run_judge selects rows by detection == 'llm' and reviews every one of them at :230. status == 'enforced' at :218 only feeds has_enforced to provider resolution. cli_check_llm passes registry.mandates unfiltered. The judge uses none of the Tier-1 filters.

#### C9 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:28; plugins/arch-compliance/hooks/posttooluse_gate.py:72-81; plugins/arch-compliance/hooks/posttooluse_gate.py:91-95`
- reasoning: Before line 72 the module imports only stdlib modules and acf.repo (acf/__init__.py is empty). The marker check returns 0 at :81 before mandates_path at :83 and before the deferred imports at :91-95.

#### C10 — SURVIVED
- evidence: `.gitignore:8; .github/workflows/ci.yml:40; plugins/arch-compliance/python/acf/cli_check_diff.py:63-74`
- reasoning: .acf/ is gitignored and CI runs python -m acf.cli_check_diff. cli_check_diff never references ENABLED_REL or .acf, so it does not check the marker today, and a CI checkout would not carry one.

#### C11 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:103-107; plugins/arch-compliance/python/acf/cli_check_llm.py:54; plugins/arch-compliance/python/acf/loader.py:70-73`
- reasoning: The SubagentStart hook catches AcfInputError around load_mandates. cli_check_llm leaves load_mandates uncaught, so it exits non-zero. A non-ValidationError raised in a validator propagates with its own type through load_model_file.

#### C12 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:104; plugins/arch-compliance/python/acf/cli_check_llm.py:10-13; plugins/arch-compliance/python/acf/judge.py:14-17`
- reasoning: Neither entry point imports a detector module or the scan path. cli_check_llm imports finding, judge, registry and repo, and judge imports exceptions, finding, registry and template. Under the design, load_mandates does only syntax and stat checks, so nothing on these paths reaches load_host_detector.

#### C13 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/baseline.py:78; config/architecture/mandates.yml:1`
- reasoning: git ls-files config lists only ARCHITECTURE.md, adr.yml and mandates.yml, so no architecture-review host configuration exists. The spec names baseline.py only in its non-goals, as not modified.

#### C14 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:20; plugins/arch-compliance/python/acf/registry.py:24; hm:config/architecture/mandates.yml:5-14`
- reasoning: In the HistoricMansions checkout at b652fab05, grep -c for 'languages:|arch_anchor:' returns 0. Its rows carry gemini_anchor instead. Mandate requires both languages and arch_anchor.

#### C15 — SURVIVED
- evidence: `hm:scripts/ci/arch_compliance/driver.py:150-163; hm:scripts/ci/arch_compliance/driver.py:92-96`
- reasoning: The driver emits a WARN Finding with exc.lineno or 0 on SyntaxError and raises in range mode. _scan_facade_guards reads cf.content, the staged, HEAD or range blob, so its result depends on diff mode.

#### C16 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:198-200; plugins/arch-compliance/python/acf/cli_check_diff.py:121; plugins/arch-compliance/hooks/posttooluse_gate.py:248-249`
- reasoning: The two existing loops differ in diff scope (added lines against None), path collection (git changed_files against harness paths) and file filter (suffix branches against _CODE_SUFFIXES). The host procedure is specified once, in acf.detectors.host, and each gate only calls it.

#### C17 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:50-53; plugins/arch-compliance/python/acf/detectors/fsm_guard.py:36-39; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:23-26`
- reasoning: Each of the four wraps ast.parse(text) in except SyntaxError and returns [] (or 0 for the ratchet), at exactly the cited lines.

#### C18 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_registry.py:30; plugins/arch-compliance/tests/test_profile_drift.py:24; tests/test_self_host.py:23`
- reasoning: I ran git grep -n 'load_mandates(' over plugins and tests, excluding registry.py. It printed exactly the listed hits, and only cli_check_diff.py:70, SKILL.md:95, test_profile_drift.py:24, test_registry.py:30 and test_self_host.py:23 pass known_detectors. None of the registries those callers load has a host row.

#### C19 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:125; plugins/arch-compliance/python/acf/cli_check_diff.py:82; plugins/arch-compliance/tests/test_enforcement.py:54`
- reasoning: git grep -n 'apply_registry(' -- '*.py' printed the definition, the two gate calls and test_enforcement at :54, 60, 66, 72, 84, 94, 104, 110, 125 and 130, exactly as stated.

#### C20 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; plugins/arch-compliance/hooks/posttooluse_gate.py:229-236; plugins/arch-compliance/python/acf/enforcement.py:47; plugins/arch-compliance/hooks/inject_constraints.py:158`
- reasoning: I ran both recipes. The narrow one gives posttooluse_gate.py:231, 235, 285, cli_check_diff.py:94, 98, 112, 113, 158, 168 and enforcement.py:47. The wider .status recipe adds registry.py:58, judge.py:218 and inject_constraints.py:158, which is display only.

#### C21 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/build_artifacts.py:31; plugins/arch-compliance/python/acf/detectors/fsm_guard.py:59; plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23; plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15; plugins/arch-compliance/python/acf/enforcement.py:46`
- reasoning: Every Finding construction in the scanners uses a fixed literal mandate_id at the cited lines (python_pack 67/97/144/172, facade_sinks 69, fail_loud_ratchet 132). apply_registry looks the row up by finding.mandate_id, so a row with any other id never matches.

#### C22 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:168-182; plugins/arch-compliance/hooks/posttooluse_gate.py:213-295; plugins/arch-compliance/hooks/posttooluse_gate.py:254`
- reasoning: _scan_paths has no scan_ratchet import or call. scan_python_file, scan_typescript_file, facade, fsm and build-artifact all run in both gates, at the lines given in the section 4.3 table.

#### C23 — SURVIVED
- evidence: `config/architecture/mandates.yml:64-73; plugins/arch-compliance/tests/test_registry.py:20-37; plugins/arch-compliance/tests/test_diff_cli.py:71-81; plugins/arch-compliance/tests/test_judge.py:385-395; plugins/arch-compliance/tests/test_hooks.py:220-226`
- reasoning: I ran a read-only Python census applying _row_shape, _check_builtin, the reserved-id rule and the CallSite vocabulary to every row of the repository, profile and fixture registries. Every row printed an empty problem list. Inline rows: test_diff_cli's row is [ci, hook] and matches its contract. test_registry's manual [audit] rows are not ast/guard rows. test_judge's llm row is unenforced. test_registry's not_a_real_detector row with [ci] passes _row_shape and raises UnknownDetectorError as intended. The only fixture edit, in test_hooks.py:223 (to status: unenforced), makes rows inactive, which skips the checks.

#### C24 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/loader.py:70-73; plugins/arch-compliance/python/acf/registry.py:33-41; plugins/arch-compliance/tests/test_enforcement.py:19-30; plugins/arch-compliance/tests/test_template.py:73-84`
- reasoning: load_model_file catches only ValidationError. AcfInputError is not a ValueError, so pydantic does not wrap it, and test_registry.py:46 already relies on _unique_ids raising it. test_enforcement builds active ast rows with call_sites ['ci'], which contains a Tier-1 site and is not a host reference. test_judge.py:41 and test_template.py:73 build llm rows, which _row_shape skips.

#### C25 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:91-112; plugins/arch-compliance/tests/test_profile_drift.py:7; tests/test_self_host.py:14`
- reasoning: Every use either imports the name, passes it as known_detectors, or calls sorted(), which yields keys for a Mapping. None uses set algebra or set-only methods. ARCHITECTURE.md:228 names it in prose.

#### C26 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:63; plugins/arch-compliance/hooks/posttooluse_gate.py:65; plugins/arch-compliance/hooks/hooks.json:24`
- reasoning: main resolves one repo per invocation. The hook is launched as a fresh python process per PostToolUse event (hooks.json command) and resolves one repo at :65.

#### C27 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:16-22; plugins/arch-compliance/python/acf/detectors/__init__.py:11-28; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:14; plugins/arch-compliance/python/acf/judge.py:29-36`
- reasoning: Today: 3 python_pack ids + 4 guard ids + 2 TS ids + 4 LLM ids = 13, all distinct. After the design: 9 built-in ids.

#### C28 — SURVIVED
- evidence: `config/architecture/mandates.yml:132-142; plugins/arch-compliance/python/acf/judge.py:29-36; plugins/arch-compliance/skills/acf-mandate/SKILL.md:56; plugins/arch-compliance/skills/acf-mandate/SKILL.md:121`
- reasoning: My census found the active llm rows to be soft.fail-loud (llm_fail_loud, partial) in the repository registry and the python-service profile, and soft.react-boundaries (llm_react_boundaries, partial) in the react-app profile. Both ids are in LLM_PROMPT_IDS. The fixture and test_diff_cli inline registries have no llm row, and test_judge's llm row is unenforced and is loaded by cli_check_llm, which will not pass llm_prompt_ids.

#### C29 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:400; plugins/arch-compliance/python/acf/cli_check_diff.py:72`
- reasoning: getattr with a default suppresses only AttributeError. That is language semantics: a module __getattr__ raising RuntimeError escapes it. The specified try covers both exec_module and the lookup, re-raises KeyboardInterrupt and wraps everything else as UnknownDetectorError. cli_check_diff's except tuple at :72 already lists UnknownDetectorError, and the hook's scan except is widened by section 4.6. The cached-is-None branch removes only an entry this call registered.

#### C30 — SURVIVED
- evidence: `pyproject.toml:5; plugins/arch-compliance/python/acf/adr/citations.py:76; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:162`
- reasoning: requires-python is >=3.11. Python 3.11 and 3.12 Path.resolve call check_eloop and raise RuntimeError on ELOOP. I read the local 3.13 source: resolve is a bare os.path.realpath, which does not raise on a loop in non-strict mode. On POSIX, realpath's lstat raises ValueError on an embedded NUL. RepoTree.contained maps both to None, and each specified caller turns None into its typed error or the unresolved kind.

#### C31 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:82-95; plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:21-28; plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:18-22`
- reasoning: The Finding construction sits inside try/except (KeyError, TypeError, ValueError), which re-raises DetectorPackError, so a dict KeyError or a ValueError from validate_hit_fields would be wrapped. The rules emit detector empty_catch and explicit_any, take line from getStartLineNumber() (a JSON integer of at least 1, which becomes a Python int) and use non-empty literal messages.

#### C32 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:22-28; plugins/arch-compliance/hooks/hooks.json:24; pyproject.toml:19-20; .github/workflows/ci.yml:40; hm:scripts/ci/metadata_facade_guard.py:66`
- reasoning: The hook runs as a script, so sys.path[0] is the hooks directory and not the host cwd. It inserts python/ at 0 when absent and imports acf.repo at :28. The console script's sys.path[0] is the script directory. python -m from the repository root puts the cwd first. The HM guard imports scripts.ci..., which resolves once the HM root (which has scripts/__init__.py) is on sys.path. Caveat: the insert is conditional (see unanchored finding).

#### C33 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:29-61; hm:scripts/ci/run_guards.py:107-111; hm:scripts/ci/run_guards.py:116; hm:scripts/ci/run_guards.py:126-130; hm:scripts/ci/run_guards.py:317-321`
- reasoning: The parser offers only --mode, --base, --repo, --mandates and --json. run_guards refuses an unknown site, filters rows with `site not in entry.call_sites`, refuses an empty selection, and defaults --site to 'ci'.

#### C34 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:124-152; plugins/arch-compliance/hooks/posttooluse_gate.py:248-252; plugins/arch-compliance/python/acf/detectors/build_artifacts.py:27-34; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:135`
- reasoning: file_lines is written only in the .py and .ts/.tsx branches. Ratchet and build-artifact findings use line=1. A staged dist/x.py is .py, so it enters file_lines under its git key, and lstrip('./') leaves 'dist/x.py' unchanged, so the keys match.

#### C35 — SURVIVED
- evidence: `config/architecture/mandates.yml:5-130; plugins/arch-compliance/profiles/python-service/mandates.yml:18; plugins/arch-compliance/tests/fixtures/mandates_valid.yml:7`
- reasoning: git grep -n precommit -- '*.yml' printed nothing (exit 1). My census counted ast/guard rows declaring ci: 9 in the repository registry, 7 in python-service, 3 in react-app and 3 in the fixture. Every active ast/guard row declares ci, so adding precommit to each selects the same active rows.

#### C36 — SURVIVED
- evidence: `pyproject.toml:7; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:371-379; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:439`
- reasoning: I ran a read-only snippet under pydantic 2.13.3. The before validator received a dict for both kwargs construction and model_validate. model_construct hits with b'a.py', '5' or True, re-validated through dict(item.__dict__), were all refused, and plain str/int values were accepted. I verified one 2.x version only, but mode='before' semantics have been stable since 2.0.

#### C37 — REFUTED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:112-117; plugins/arch-compliance/python/acf/cli_check_diff.py:69-74; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:185`
- reasoning: The RepoTree.file None cases hold. The conclusion that a permission-denied stat 'ends in UnknownDetectorError or DetectorPackError, not a traceback' does not. The design says _collect_paths lets the OSError propagate, and _collect_paths is called at posttooluse_gate.py:112, outside any try: the scan try at :113-117 catches only DetectorPackError today and AcfInputError/DetectorPackError/UnknownDetectorError under the design. So in the hook it is an uncaught OSError traceback, as it is today. Likewise _scan_changed's tree.file runs under cli_check_diff.py:72, whose tuple has no OSError. The 'not a traceback' guarantee holds only for the four callers that wrap the call themselves.

#### C38 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/host.py:24-25; docs/design/ADR_GATE_HOST_CONTRACT.md:295-301`
- reasoning: Both fields are PosixStr with min_length 1. The approved contract explicitly declines refusing absolute or '..' values. The spec lists host.py as unchanged (sections 5.1 and 5.2) and adds no refusal for those fields.

#### C39 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:122-124; config/architecture/mandates.yml:97-98; plugins/arch-compliance/profiles/python-service/mandates.yml:58-59; plugins/arch-compliance/tests/test_portable_guards.py:100-107; plugins/arch-compliance/python/acf/cli_check_diff.py:72`
- reasoning: The shipped values are the relative baseline config/architecture/fail_loud_ratchet.json and roots ['.']. The only tested call is scan_tree(tmp_path, roots=['pkg']) after mkdir pkg. contained(abs-inside-root) resolves to itself and is_relative_to(root), so it is accepted. DetectorPackError is in the :72 tuple. Note: the baseline file is not tracked, but both shipped ratchet rows are unenforced, and today's load_baseline (:78-81) refuses a missing file too.

#### C40 — SURVIVED
- evidence: `hm:scripts/ci/genre_conditional_guard.py:32-40; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:439`
- reasoning: @dataclass (not frozen) Finding's __str__ calls self.line_text.strip(). I ran a snippet: ValueError(obj) where obj.__str__ calls None.strip(), and str() of it raised AttributeError, which confirms BaseException.__str__ delegates to str(args[0]).

#### C41 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:429`
- reasoning: list(raw) iterates to StopIteration or propagates the generator's exception, which finalizes the generator. Both happen inside the try, before the _revalidate comprehension, so no generator is left suspended and any finally body runs inside the wrapped region.

#### C42 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_diff_cli.py:102-108; plugins/arch-compliance/tests/test_diff_cli.py:84-90; plugins/arch-compliance/tests/fixtures/mandates_valid.yml:1-32`
- reasoning: Every other main() test uses the fixture (active rows with ci) or the enforced WARN row, or fails before selection: test_missing_mandates fails at load. The staged bad.py is 'def f(): try: g() except Exception: pass' with no hasattr, so an added no_shims_hasattr [ci] row emits nothing, and _check_builtin accepts it (id matches, ci is in TIER1).

#### C43 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:203-204; plugins/arch-compliance/hooks/posttooluse_gate.py:238-246; plugins/arch-compliance/python/acf/repo.py:41-44; plugins/arch-compliance/tests/test_hooks.py:165-250`
- reasoning: For relative p, (root/p).resolve() equals today's (repo/p).resolve(). For absolute p, root/p is p, so the result equals p.resolve(). repo is already resolved, so RepoTree.root equals repo and the keys match. Every test_hooks path is repo/'bad.py' or similar; none is outside the repository.

#### C44 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:57-58; plugins/arch-compliance/python/acf/enforcement.py:47; config/architecture/mandates.yml:140`
- reasoning: partial rows gate because only 'unenforced' is dropped. My census found partial rows only as llm rows with valid prompt ids. No shipped or fixture partial row names a missing detector or prompt.

#### C45 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:46; plugins/arch-compliance/python/acf/cli_check_diff.py:127; plugins/arch-compliance/hooks/posttooluse_gate.py:254; plugins/arch-compliance/hooks/posttooluse_gate.py:279-282`
- reasoning: scan_python_file and scan_typescript_file run unconditionally on every changed file of their language, and routing is by mandate_id. The census's reserved-id check (built-in id on a non-built-in active row) flagged no row in any shipped or fixture registry.

#### C46 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:162; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:454`
- reasoning: contained() uses non-strict resolve, which follows existing symlinks, so a lexically valid path through an in-repo directory symlink to the outside fails is_relative_to. A missing tail is accepted. _to_findings is the stated sole Finding constructor for both runners.

#### C47 — SURVIVED
- evidence: `docs/design/evidence/HOST_DETECTOR_EXTENSION_POINT/path_census.py:35-59; docs/design/evidence/HOST_DETECTOR_EXTENSION_POINT/path_census_a338cad.txt:1; plugins/arch-compliance/hooks/posttooluse_gate.py:22-26`
- reasoning: I ran the script at HEAD, which differs from a338cad only under docs (git diff --stat outside docs printed nothing). Its output diffed identical to the committed file. from_file_dunder exempts Path(__file__).resolve(), and is_constantish exempts repo / MANDATES_REL. Every non-allowlisted hit sits at a site the spec switches.

#### C48 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:204; plugins/arch-compliance/hooks/posttooluse_gate.py:243; plugins/arch-compliance/python/acf/cli_check_diff.py:116-122; plugins/arch-compliance/python/acf/adr/citations.py:163-169`
- reasoning: For an existing in-repo file or directory: the hook key is relative_to of the same resolved path. The diff gate keeps posix = Path(rel).as_posix(). Citations apply the same containment test, and exists() on the resolved path is true exactly when it is true on the joined path. The ratchet walk keys differ only for the two stated cases.

#### C49 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:47; plugins/arch-compliance/python/acf/registry.py:58; plugins/arch-compliance/python/acf/cli_check_diff.py:98`
- reasoning: The gates and apply_registry treat partial as live, but load_mandates skips non-enforced rows before the detector check. A partial ast row naming foo loads with KNOWN_DETECTORS, and no scanner dispatches on foo.

#### C50 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:107; plugins/arch-compliance/hooks/posttooluse_gate.py:229-236`
- reasoning: The hook calls load_mandates(mandates_path) with no known_detectors. _scan_paths matches rows only by built-in id constants, so an unknown detector row is silently inert.

#### C51 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80; plugins/arch-compliance/hooks/posttooluse_gate.py:119-123; plugins/arch-compliance/python/acf/enforcement.py:49-50`
- reasoning: The two closures are token-identical and read only file_lines, which is populated only for .py/.ts/.tsx files. A missing entry returns '', so token_exempted sees no token.

#### C52 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/adr/citations.py:74-76; plugins/arch-compliance/python/acf/adr/citations.py:161-163; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:189`
- reasoning: The reference facts hold: git grep shows only the definitions plus :161 and :163, and no test imports them. But 'exactly two behaviours change' is false. The spec's own section 4.1 (line 189) says 'Three behaviours change' and section 4.9 lists the third: a citation with an embedded NUL. Today _escapes_repo's (root / path).resolve() raises ValueError on it (on POSIX, and on 3.11 per the spec); under RepoTree.contained it classifies as unresolved. The claim's count contradicts the sections it cites.

#### C53 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; config/architecture/mandates.yml:70; plugins/arch-compliance/profiles/python-service/mandates.yml:18; plugins/arch-compliance/tests/fixtures/mandates_valid.yml:18`
- reasoning: My census shows every active built-in row declares ci (and precommit after the change), and declares hook except no-shims.hasattr, which is [ci] in the repository registry, the python-service profile and the fixture. The ratchet never ran in the hook.

#### C54 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:21; plugins/arch-compliance/python/acf/registry.py:60; plugins/arch-compliance/skills/acf-mandate/SKILL.md:112`
- reasoning: known_detectors is consulted only for ast/guard rows, and no KNOWN_DETECTORS consumer reads it for llm rows. The only other observable change is the skill's printed sorted(KNOWN_DETECTORS) listing, which is display, not gating.

#### C55 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_repo_paths.py:53-71; plugins/arch-compliance/tests/test_adr_code_portability.py:15-23`
- reasoning: I searched the tests for read_text and getsource. The source-text tests scan only for config/architecture spellings or for acf.adr modules. None reads the scanner modules' mandate_id literals, and a constant with the same value emits the same Finding.

#### C56 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80; plugins/arch-compliance/hooks/posttooluse_gate.py:119-123`
- reasoning: The proposed make_line_lookup body is token-identical to both closures and reads no file. Results change only where scan_host_guards adds entries, which is new host-guard behaviour.

#### C57 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/__init__.py:11-28; plugins/arch-compliance/python/acf/detectors/python_pack.py:16; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:14; plugins/arch-compliance/tests/test_typescript_pack.py:6`
- reasoning: git grep -n _DETECTOR_IDS over plugins and tests printed exactly the listed hits, and the spec rewrites each one. Outside plugins and tests, only approved-spec prose mentions them.

#### C58 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/facade_sinks.py:24-25; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:46; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:88-90; plugins/arch-compliance/python/acf/detectors/build_artifacts.py:23; plugins/arch-compliance/python/acf/cli_check_diff.py:135-137`
- reasoning: allowlist_globs: absent, None, [] and any iterable behave the same under `for glob in x or []` as under list(x or []). atomic_is_sink is used only in a truthiness test, so it matches bool(). path_prefixes iterates `path_prefixes or defaults`, which matches list(prefixes) if prefixes else None. Required strings are unchanged.

#### C59 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/facade_sinks.py:51-52; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:24-25; plugins/arch-compliance/python/acf/detectors/fsm_guard.py:37-38`
- reasoning: git grep for 'ast.parse(' and 'SyntaxError' over the python and hooks directories prints only these four scanners. parse_python catches exactly SyntaxError, as they do, and returns None, so each keeps its empty result.

#### C60 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:55-62; plugins/arch-compliance/tests/test_portable_guards.py:107; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:126`
- reasoning: rglob yields search/<relative> lexically, so with search resolved and contained under root, relative_to cannot raise. The grep shows scan_tree called only at fail_loud_ratchet.py:126 and test_portable_guards.py:107.

#### C61 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:77-82; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:31-34; plugins/arch-compliance/python/acf/detectors/python_pack.py:13-14`
- reasoning: Both test whether type is None, or is ast.Name with id 'Exception'. git grep shows the only other caller is python_pack.py:61 and no test names it. python_pack imports only acf.engine and acf.finding, so no cycle.

### Unanchored findings

- **advisory**: _scan_changed's switch to tree.file leaves a permission-denied stat uncaught: cli_check_diff's except tuple has no OSError, so it is a traceback, the same as is_file() at :119 today. Section 6.1 lists stat OSError refusals only for load_mandates, load_host_detector and scan_host_guards, and never states the diff-gate case.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:72`
- **advisory**: The hook inserts python/ at sys.path[0] only when it is not already on sys.path. Under the documented pip install -e the path may already be present, in which case the hooks directory stays first, so Decision 6's row for the hook ('inserts the plugin's python/ at sys.path[0], ahead of the hooks directory') is conditional. The host root is still not on the path, so the conclusion holds.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:25-26`
- **advisory**: test_repo_paths pins acf/repo.py's imports to {__future__, pathlib}. RepoTree, added to repo.py, must therefore stay pathlib-only (no os or ast), and the spec's section 4.7 table does not name this existing constraint.
  - evidence: `plugins/arch-compliance/tests/test_repo_paths.py:74-78`

### Looked for but did not find

- any call of acf.cli_check_diff.main outside test_diff_cli.py whose registry has no active ast/guard row (git grep cli_check_diff over *.py, *.yml, *.toml, *.json)
- any shipped, profile or fixture row that is partial and names a non-existent detector or prompt id
- any non-built-in active row (llm, manual, host) using a built-in mandate id in the repository, profile or fixture registries
- any registry row in *.yml declaring precommit (git grep printed nothing)
- any call_sites value outside ci, hook and audit in *.yml or in test Mandate(...) constructions
- any test reading the scanner modules' source text that would see the mandate_id literal-to-constant change
- any importlib, import_module, spec_from_file_location or exec_module use in plugins/arch-compliance/python or plugins/arch-compliance/hooks
- any site besides the four scanners that wraps ast.parse in a SyntaxError skip under plugins/arch-compliance/python or hooks
- a difference between path_census.py output at HEAD and the committed path_census_a338cad.txt (diff showed none)

## compliance

### Claim verdicts

#### C62 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:29-30; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:642-667; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:413; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:433; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:451; plugins/arch-compliance/python/acf/detectors/python_pack.py:77-82; plugins/arch-compliance/python/acf/cli_check_diff.py:69-74; plugins/arch-compliance/hooks/posttooluse_gate.py:113-117`
- reasoning: The doctrine at :29-30 reads 'Bare except: and broad except Exception: handlers that swallow errors are forbidden unless explicitly exempted with a reason'. Each §6.1 row names a component and a typed error, and the gates' except tuples (cli_check_diff.py:72, and the hook scan handler that §4.6 extends) catch those errors and exit non-zero. The load handler (:413) and the call handler (:433) re-raise as UnknownDetectorError or DetectorPackError. Only _describe (:451) swallows, and only a failure to format the message; the typed error is still raised. All three carry the fail-loud.bare-except-ok token with a reason. They are except BaseException handlers, which the shipped predicate (python_pack.py:77-82) does not flag, as the spec says. One item in the claim does not match the design. The claim lists 'a TypeScript item with ... differing mandate_id' as refused. §6.1 (:663) refuses only an unknown detector or a bad line or message. The design (§4.3, :354) removes mandate_id from the Node output and stamps it from TS_MANDATE_IDS, so a differing id cannot reach a Finding: it is ignored, not refused. That is still fail-loud in substance, but the claim's wording should match §6.1.

#### C63 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:329-345; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:238-257; plugins/arch-compliance/python/acf/registry.py:56-63; plugins/arch-compliance/python/acf/cli_check_diff.py:94-99`
- reasoning: Today load_mandates checks only enforced rows and admits LLM prompt ids for ast rows (registry.py:58-60, KNOWN_DETECTORS includes LLM_PROMPT_IDS). In the design: _check_builtin (:329-345) refuses an unknown detector (UnknownDetectorError), an id differing from contract.mandate_id, and any Tier-1 site outside contract.call_sites (AcfInputError). _row_shape (:247-251) refuses an active ast/guard row with no Tier-1 site. KNOWN_DETECTORS omits LLM prompt ids, and the ratchet maps to DIFF_CALL_SITES (§4.3 table). Built-in dispatch is by file suffix and registry.active(sites, detector=...), not by detection or languages, so the declared detection kind cannot hide a row. Host rows are routed by scan_host_ast_file/scan_host_guards with registry.active(call_sites, ...) in both gates. The claim holds as the design states it, and the §4.7 contract-against-dispatch test ties the contracts to the gates' actual dispatch.

#### C64 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:120-123; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:628; plugins/arch-compliance/python/acf/repo.py:23-26`
- reasoning: The section governs 'The adversarial-design-review gate's host values ... declared by the host in config/architecture/adr.yml' (:120-123) and records three out-of-scope defaults, including the ratchet baseline default (repo.py:23-26), which the design keeps. The design adds no adr.yml value. §6 (:628) says the design follows the practice by choice for repo_root, apply_registry's call_sites and --call-site, without claiming the section requires it. The design matches: load_mandates refuses a missing repo_root for an active host row, call_sites is a required keyword, and --call-site is required=True. The existing str(params.get(key, "")) for required scanner params is only centralised, and the scanners still refuse an empty value (facade_sinks.py:32-37, fsm_guard.py:29-34).

#### C65 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:48-49; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:410; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:419-420`
- reasoning: The doctrine says 'Do not probe optional attributes with hasattr to paper over missing interfaces' (:48-49). The loader uses getattr(mod, attr, None) (:410), then 'if not callable(fn): raise UnknownDetectorError' (:419-420); there is no hasattr. Every load, call and result failure is re-raised as a typed error (§6.1). _describe's constant message appears only inside an error that is still raised, so it is not a silent fallback.

#### C66 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:57-58; plugins/arch-compliance/python/acf/engine.py:17-24; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:129; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:319; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:396`
- reasoning: The rule is 'When persisting paths to YAML/JSON, use Path.as_posix()'. Findings are JSON-dumped by both gates. HostHit.path passes validate_posix_rel_path, which calls contains_backslash (engine.py:17-24; spec :129) and refuses a backslash. The hook's key comes from RepoTree.key (.as_posix()). The new messages render Paths with .as_posix() (:319, :324, :396). str(root) is appended to sys.path only, which is not persistence.

#### C67 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:101-102; plugins/arch-compliance/python/acf/exceptions.py:13; plugins/arch-compliance/python/acf/exceptions.py:29`
- reasoning: exceptions.py:5, :13 and :29 define AcfInputError, UnknownDetectorError and DetectorPackError, each subclassing AcfError alone, as :101-102 requires. The design's code defines no exception class; HostHit and BuiltinDetector are a BaseModel and a dataclass.

#### C68 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_repo_paths.py:14-25; plugins/arch-compliance/python/acf/registry.py:1-7; plugins/arch-compliance/python/acf/detectors/__init__.py:1-35; plugins/arch-compliance/skills/acf-mandate/SKILL.md:93; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:537`
- reasoning: engine.py, registry.py and detectors/__init__.py spell no config/architecture path today. The design's code for them and for host.py adds none, and the row's test scans python/ and hooks/ for that spelling (test_repo_paths.py:14-25). The acf-mandate snippet already imports MANDATES_REL from acf.repo (SKILL.md:93). §4.8 (:537) rewrites it to use resolve_repo(None) and repo / MANDATES_REL.

#### C69 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:137-138; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:396; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:533-549`
- reasoning: The rule: 'Skill prose and runtime messages name no host repository, path or section'. The §4.2-§4.4 messages are generic ('host detectors already loaded from {root}; one host root per process', 'active mandate ... references unknown detector'), and their paths are runtime values, not hard-coded host names. The §4.8 skill, README and guide edits (:533-549) describe call sites, host detectors and the .acf opt-in, and name no origin host. Origin-host references appear only in the spec's own rationale.

#### C70 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:155-157; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:671-695; plugins/arch-compliance/python/acf/detectors/__init__.py:30-35`
- reasoning: The rule: 'An export has a live call site in the package, a hook or a skill. A test is not a consumer.' §6.2 (:671-695) names a package, hook or skill caller for each new export. RepoTree.file/directory/key are used by load_mandates, load_host_detector, scan_host_guards, scan_ratchet/scan_tree and the hook. parse_python has four scanners plus scan_host_ast_file. The *_args functions and make_line_lookup are used by both gates. DIFF/HOOK/TIER1 sets feed argparse, the hook, _row_shape and KNOWN_DETECTORS. HostHit is used by _revalidate/_to_findings. LLM_PROMPT_IDS feeds acf-check-diff's load_mandates and the Validate snippet. The five deleted sets, including their __all__ entries (__init__.py:30-35), go with their only users, which switch to KNOWN_DETECTORS. The acf.cli_check_diff re-export stays used by that module's own load_mandates call.

#### C71 — UNPROVEN
- evidence: `config/architecture/ARCHITECTURE.md:161-165; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:444`
- reasoning: The doctrine requires that a claim about the tree is 'not load-bearing on "every", "all", "only" ... unless a recipe that a reader can re-run backs the quantifier'. Almost every population claim in the spec carries a recipe or is a per-item table. But §4.4 item 4 (:444) states a whole-tree negative about the sibling repository, 'No origin-host code raises an exception carrying such an object today', with no recipe. The design rests nothing on that sentence (the _describe guard and its test stand without it), so the doctrine itself is not breached. The claim's broader statement that every population claim carries a recipe is still not established. The fix is to add a recipe or delete the sentence.

#### C72 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:173-174; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:497; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:459; plugins/arch-compliance/python/acf/cli_check_diff.py:152`
- reasoning: The rule: 'every subprocess call ... that reads text declares encoding="utf-8"; every file read of prose declares its encoding'. The TypeScript-branch read (:497, replacing cli_check_diff.py:152) and scan_host_guards' read_text(encoding="utf-8", errors="replace") (:459) both declare utf-8. The rule governs the declared encoding, not the error policy. The design's code adds no subprocess. The bridge's existing text=True call stays declared debt (ARCHITECTURE.md:177-181).

#### C73 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:186-187; pyproject.toml:3; plugins/arch-compliance/.claude-plugin/plugin.json:3; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:549`
- reasoning: The rule: 'A change to a skill's prose bumps the plugin version in plugins/arch-compliance/.claude-plugin/plugin.json and pyproject.toml'. Both read "0.2.2" today (pyproject.toml:3, plugin.json:3), and §4.8 (:549) bumps both to "0.2.3". The acf-mandate and acf-setup skills' prose changes, so the bump is required and planned. The gate skills are untouched, so the installed-skill byte check is unaffected.

#### C74 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:198-200; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:551-567; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:24-25`
- reasoning: The rule asks for 'exactly one canonical implementation that every call site consumes'. Each §4.9 row (:551-567) deletes the listed definition and names its replacement and live-reference recipe. The citations helpers, the five id sets, the _line_lookup closures, _active_mandates and the inline filters, the inline params extraction, the ratchet joins and walk filter, the four parse-and-skips, and test_self_host's is_file check are all switched. The *_args functions pass optional params through, so the scanner signature defaults (facade_sinks.py:24-25) stay the one default. Decision 8 explicitly disclaims completeness.

#### C75 — UNPROVEN
- evidence: `config/architecture/ARCHITECTURE.md:213-215; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:563; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:598; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:103`
- reasoning: The doctrine: 'remove legacy dependencies or non-contractual patterns in code paths you are changing. Do not expand scope to unrelated modules.' Decision 8 and §4.9 delete the listed duplicates, and §3 (:103) keeps the two pre-existing dispatch loops, so the substance complies. The claim's last clause does not match the spec at 7da3f56: it says the join-and-is_file in _scan_changed (cli_check_diff.py:118-119) 'is a different job recorded as ADJACENT'. The spec instead deletes it in §4.9 (:563) and records it as SUBSUMED in §5.2 (:598), switching it to RepoTree.file. Neither 'different job' nor 'ADJACENT' appears in the spec. That clause cannot be established from the design; the claim looks stale against v9.

#### C76 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:147-148; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:80-96`
- reasoning: The rule: 'A LedgerRow or LedgerAmendment field changes only through a spec and a gate run'. The in-scope table (:80-96) touches no ledger module. The only acf.adr change is citations.py consuming looks_absolute and RepoTree, which changes some citation classifications but no ledger model.

#### C77 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:50; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:123; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:125; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:517`
- reasoning: Checked against each principle. Principle 1: every load refusal is typed. Principle 2: the single Finding schema is kept and HostHit is converted, never emitted. Principle 3: POSIX paths are kept. Principle 4 ('Registry is the spine — ... detectors, auditors, and call sites must agree or tests fail', :50) is directly served by the built-in contracts, the call-site routing and the contract-against-dispatch test (:517). Principle 5 is unaffected. :123 and :125 each call for 'Extension points for project-specific detectors'; host ast rows for python and typescript and host guard rows meet both.

#### C78 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:454; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:459; plugins/arch-compliance/python/acf/cli_check_diff.py:69-74; plugins/arch-compliance/hooks/posttooluse_gate.py:113-117`
- reasoning: _to_findings (:454) refuses a hit whose RepoTree.contained is None with DetectorPackError. scan_host_guards (:459) maps a contained path that RepoTree.file rejects to [], which leaves the finding in place: with no lines, no exemption token can drop it, so the error is fail-safe. An OSError from the stat or read becomes DetectorPackError. The read sits inside each gate's scan try: _scan_changed runs inside the try at cli_check_diff.py:69-74, and _scan_paths inside the hook's try at :113-117, whose tuple §4.6 extends. make_line_lookup only indexes a mapping.

#### C79 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:72-73; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:38-74; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:567; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:542`
- reasoning: The section reads 'Optional whole-tree freeze of bare/broad-except counts. Enable the mandate and commit a config/architecture/fail_loud_ratchet.json baseline'. The design keeps the whole-tree walk and count (fail_loud_ratchet.py:38-74; is_bare_or_exception is token-identical). It routes the ratchet to DIFF_CALL_SITES through KNOWN_DETECTORS, refused at load for hook. §4.9 (:567) replaces the silent 'if not search.exists(): continue' and the unconditional joins with RepoTree.file/directory, raising DetectorPackError for an escaping or missing baseline or root. §4.8 (:542) adds both constraints to the section's enablement text.

#### C80 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:107-110; plugins/arch-compliance/tests/test_repo_paths.py:17-25; plugins/arch-compliance/tests/test_repo_paths.py:74-78; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:156-183; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:534`
- reasoning: The section makes acf.repo the one declaration of where ACF looks in a host, stdlib-only, with a test scanning python/ and hooks/ (test_repo_paths.py:17-25 runs git ls-files python hooks; :74-78 allows only __future__ and pathlib). The design's RepoTree (:156-183) uses only pathlib and builtins, so it passes that test. test_repo_tree_guard.py scans the same two directories. I grepped python/ and hooks/ for .resolve(/relative_to(/is_relative_to(/joinpath(/os.path.* and repo-named '/' joins; the hits match the committed census exactly (posttooluse_gate.py:204, :243; cli_check_diff.py:66, :118; cli_check_llm.py:50; citations.py:75-76, :168; fail_loud_ratchet.py:45-46, :60, :124; typescript_bridge.py:27; plus __file__-based and repo.py sites). So after migration only the three allowlisted functions remain, as the test asserts. §4.8 (:534) adds the rule to the section.

### Unanchored findings

- **advisory**: RepoTree.contained maps a symlink-loop RuntimeError to None. In the PostToolUse hook's _collect_paths, an edited path through a symlink loop on Python 3.11/3.12 is therefore skipped silently; today it raises from (repo / p).resolve(). §4.1's list of caller outcomes, which ends 'it never ends as a traceback', omits this silent skip, which sits close to the lifted 'No defaulting to None to avoid a crash' rule.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:166`
- **advisory**: §4.4 item 4 states a whole-tree negative about the sibling repository ('No origin-host code raises an exception carrying such an object today') with no recipe. It is not load-bearing, but it should carry a recipe or be deleted.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:444`

### Looked for but did not find

- ## High-frequency misses: checked each first. Completeness claims: one non-load-bearing gap, filed advisory. A default re-entering for a declared value: none new; the required scanner params' "" is refused by facade_sinks.py:32-37 and fsm_guard.py:29-34. Host names in prose or messages: none. A stdlib mixin on an exception: no new exception class. A subprocess text call without encoding: none added. A package check re-implemented in a test or skill: the snippet consumes load_mandates, KNOWN_DETECTORS and LLM_PROMPT_IDS.
- ## Build artifacts (:66-68): the design changes only how no_build_artifacts receives params and its call_sites; the contract test generates its fixture tree under tmp_path and never commits it. Not governing beyond that.
- ## Soft fail-loud smells / ## React boundaries: llm rows gain prompt-id validation only. The shipped llm rows (soft.fail-loud partial, soft.react-boundaries) name ids in LLM_PROMPT_IDS, and the Tier-2 judge is unchanged. Not touched.
- ## Post-merge: host operational declarations; not touched by this design.
- ## Release discipline second clause (installed-skill byte check): this design changes no gate or housekeeping skill tree, so the check's scope is unaffected.

### Unstated mandates

- ## Façade sinks (:75-79) and ## FSM transitions (:81-85) — this design rewrites both sections' enablement instructions (§4.8) and adds load-time constraints to their rows (id must equal facade.forbid-sink / fsm.transition-guard; at least one Tier-1 site; params now flow through facade_sink_args/fsm_guard_args), yet the §6 doctrine-compliance table and the Governing mandates header omit both sections.

## sweeper

### Claim verdicts

#### C81 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99 plugins/arch-compliance/hooks/posttooluse_gate.py:229-236 plugins/arch-compliance/hooks/posttooluse_gate.py:284-286 plugins/arch-compliance/python/acf/enforcement.py:47 plugins/arch-compliance/python/acf/judge.py:218`
- reasoning: I searched by behaviour (status != / == "unenforced", status == "enforced", .status reads, call_sites reads) across python/ and hooks/. The Tier-1 active-row filters are exactly cli_check_diff._active_mandates, the hook's three inline filters and apply_registry's status test, and the design replaces each one. The only other status reads are judge.py:218 (Tier-2, excluded by scope) and the display-only inject_constraints.py:158. No call_sites reader exists today besides the field declaration.

#### C82 — SURVIVED
- evidence: `docs/design/evidence/HOST_DETECTOR_EXTENSION_POINT/path_census_a338cad.txt:1-17 plugins/arch-compliance/python/acf/repo.py:32-44 plugins/arch-compliance/python/acf/cli_check_diff.py:66 plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:27`
- reasoning: I re-grepped python/ and hooks/ for .resolve(, relative_to, is_relative_to, joinpath, os.path.*, root-named '/' joins, and .exists()/.is_file()/.is_dir(). Every non-__file__, non-constant site is in the census: citations.py:75,76,168; ratchet :45,46,60,124; cli_check_diff:118; hook :204,243. The census also lists the three allowlisted resolves. resolve_repo lives in the excluded acf/repo.py, and ledger.py:218 uses .absolute() only for an error message. ast.parse/except SyntaxError occurs only in the four scanners parse_python replaces. Scope caveat: executable skill snippets join `repo / cfg.ledger_path` by hand, but they sit outside the python/ and hooks/ scope the claim states (see unanchored finding).

#### C83 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:88-89 plugins/arch-compliance/python/acf/cli_check_diff.py:154 plugins/arch-compliance/hooks/posttooluse_gate.py:280 plugins/arch-compliance/python/acf/enforcement.py:52`
- reasoning: The bridge coerces line and message at :88-89. Both gates overwrite the bridge's path with their own key (:154, :280), and apply_registry overwrites severity (:52), so the private parts really are different. Built-in Python scanners build Finding directly from trusted AST line numbers (for example fsm_guard.py:53), so the only external hit sources are the bridge and host callables, and both go through validate_hit_fields.

#### C84 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:238-255 plugins/arch-compliance/python/acf/finding.py:11-19`
- reasoning: _to_finding sits at judge.py:238-255. The claim's spec_citation of 236-253 is off by two; the body's 238-255 is right. It demotes severity by verdict and confidence, takes mandate_id from the LLM result rather than the row, and admits path '<diff>' and line 0. Host findings take id and severity from the row and require line >= 1. Finding (finding.py:11-19) has no constructor of its own to share, so ADJACENT holds. A third Finding mapper exists only as skill prose (architecture-review SKILL.md:108).

#### C85 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:22-26 plugins/arch-compliance/hooks/inject_constraints.py:28-29 tests/test_check_installed_skills.py:15-18`
- reasoning: I grepped importlib/import_module/spec_from_file_location/exec_module/runpy/exec( repo-wide. Runtime code has none. The only file-path module loader is a test helper (tests/test_check_installed_skills.py:15-18) that loads one fixed repository script; it is test-only and not registry-driven. The only sys.path edits are the hooks' plugin-root inserts. No module cache or sys.modules use exists in python/ or hooks/.

#### C86 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80 plugins/arch-compliance/hooks/posttooluse_gate.py:119-123 plugins/arch-compliance/python/acf/enforcement.py:23`
- reasoning: A search for line_lookup, LineLookup and `lines[line - 1]` finds only the two closures and the test stub _no_lines; cli_check_llm, the judge and the skills have none. fsm_guard.py:56 re-states the same bounded 1-based index rule inline for its message snippet. That is not a path-keyed LineLookup, so the claim holds, but it is recorded as a partial overlap.

#### C87 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:95 plugins/arch-compliance/tests/test_profile_drift.py:24 tests/test_self_host.py:40`
- reasoning: The acf-mandate snippet and the drift test both consume load_mandates rather than re-checking ids. acf-setup and architecture-review contain no detector-id or call-site check; architecture-review checks auditor prompt files only. The one independent detector-path check, tests/test_self_host.py:40, covers manual rows and host-specific policy, and the spec already records it as SUBSUMED in mechanism.

#### C88 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:46-47 plugins/arch-compliance/python/acf/cli_check_diff.py:168 plugins/arch-compliance/hooks/posttooluse_gate.py:284`
- reasoning: apply_registry routes by mandate_id alone (:46), and every built-in id is reserved for its built-in row. A finding from a detector a gate dispatches against the table can therefore land only on that built-in row. That row is either refused by _check_builtin (it declares the site) or dropped by runs_at (it does not). The forward drift is what the dispatch test asserts. Today the ratchet is dispatched only in cli_check_diff (:168) and not in the hook's loop at :284, which matches the DIFF_CALL_SITES entry.

#### C89 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:203-204 plugins/arch-compliance/hooks/posttooluse_gate.py:242-245 plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:59-62 docs/design/HOST_DETECTOR_EXTENSION_POINT.md:588`
- reasoning: Both sites decide containment by hand: the hook with is_absolute/resolve and relative_to/except ValueError, the ratchet with relative_to/except ValueError. Once roots are RepoTree.directory results, rglob yields lexical children of the resolved root (directory symlinks are not followed), so RepoTree.key cannot fail. §4.6 (spec :506), §4.9 (:567) and §5.2 (:588) agree on deleting both except branches. One wording nit: §3 and §5.2's baseline/roots row say 'RepoTree.contained' where §4.9 says file/directory, but file and directory wrap contained, so this is not a fork.

#### C90 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:65 docs/design/HOST_DETECTOR_EXTENSION_POINT.md:444 docs/design/HOST_DETECTOR_EXTENSION_POINT.md:515`
- reasoning: Decision 7 (:65) states both the typed-error guarantee and its limit (atexit, threads). The other non-execution statements in the spec are narrower and true as written: :444 says _to_findings runs no host code after rebuild, and :51 says load_mandates imports nothing. None says host code runs only inside the wrapped regions. The callable() check and the error text after the region run no host code. The conftest fixture (:515) is the only reset; the sys.modules pop on a failed load is a rollback, not a reset.

#### C91 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:85 plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23 plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15 plugins/arch-compliance/detectors/typescript/src/scan.ts:94-96`
- reasoning: I grepped both id strings repo-wide. The only runtime spellings are the two Node rule literals and scan.ts's self-test (:83, :94-96), all of which the spec rewrites. The bridge currently copies item['mandate_id'] (:85). Python hits are tests (test_enforcement, test_baseline, test_typescript_pack) and YAML registries, which hold row data rather than runtime values.

#### C92 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:52 plugins/arch-compliance/python/acf/cli_check_diff.py:82-89 plugins/arch-compliance/hooks/posttooluse_gate.py:125-126`
- reasoning: Both gates take their exit decision from apply_registry's output. :52 replaces every kept finding's severity with the row's, so scanner, bridge (Severity(item['severity'])) and host-runner severities are all overwritten fills.

#### C93 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:118-119 plugins/arch-compliance/python/acf/cli_check_diff.py:161-163 plugins/arch-compliance/hooks/posttooluse_gate.py:204`
- reasoning: The join-and-is_file at :118-119 is a by-hand containment-free version of RepoTree.file. Findings and added_lines stay keyed by git's `rel`, and the build-artifact guard still receives the full `changed` list (:163). Side note: built-in guards and host guards will now see different populations of changed paths (unanchored finding).

#### C94 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/loader.py:24-28 plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:78-81`
- reasoning: require_file takes a built Path, has no containment case and always raises AcfInputError. The callers in question raise phase errors: DetectorPackError in the ratchet today (:78-81), and UnknownDetectorError at load. ADJACENT is justified.

#### C95 — REFUTED
- evidence: `docs/design/ADR_GATE_HOST_CONTRACT.md:292-294 plugins/arch-compliance/python/acf/loader.py:1-7 plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:77-98 config/architecture/ARCHITECTURE.md:213-215`
- reasoning: The cited ADR text calls load_baseline 'a pre-existing second loader outside this phase'. That is a deferral of a named duplicate, not an approved ruling that the two loaders do different jobs. load_model_file's docstring (loader.py:1-7) claims every input file goes through it. load_baseline repeats that job (existence check, JSON parse, shape refusal) and differs only in its error type and the lack of a model, so the relationship is PARTIAL_OVERLAP, not ADJACENT. This design also edits load_baseline (it replaces the :78 existence check), so the 'outside this phase' reason no longer applies, and `## Scoped refactor` and Decision 8 cover it. The errors='replace' half of the claim is sound.

#### C96 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:398 docs/design/HOST_DETECTOR_EXTENSION_POINT.md:515`
- reasoning: The design keeps one record, sys.modules under a sha256(rel_path)-derived name (:398). _ACTIVE_ROOT is root state, not a per-module cache, and the fixture (:515) resets both. Nothing in python/ or hooks/ uses sys.modules or lru_cache today, so no second cache exists. Caveat: the name is a function of the rel_path spelling, not of the file, so two spellings of one file (case-insensitive FS, symlink) load twice. The claim's wording is still accurate.

#### C97 — SURVIVED
- evidence: `config/architecture/mandates.yml:70 config/architecture/mandates.yml:92 C:/Users/iball/Arduino/Projects/HistoricMansions/config/architecture/mandates.yml:11 plugins/arch-compliance/tests/test_template.py:80`
- reasoning: I re-grepped every call_sites value in yml files, inline test YAML and direct Mandate constructions, plus hm's 48 rows. Values are only ci, hook, audit, precommit and posttooluse (hm). Every active ast/guard row in this repo declares ci, and the only [ci]-only guard is the unenforced ratchet. The empty-list row (test_template.py:80) is an llm row, which _row_shape skips.

#### C98 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_diff_cli.py:102-108 plugins/arch-compliance/tests/test_registry.py:30 plugins/arch-compliance/tests/test_typescript_pack.py:6 plugins/arch-compliance/tests/test_hooks.py:199-218`
- reasoning: I swept tests by behaviour: main([...]) calls, apply_registry calls, frozenset known_detectors, imports of the deleted sets and private citation helpers, inline YAML with unknown detectors or ids that mismatch their built-in, ratchet path arguments, and the hook docstring pin (test_repo_paths.py:47-48). Each break is in the listed set. test_self_host.py:14 keeps working through the re-export, and test_portable_guards.py:107 uses an in-repo root. I found no other break.

#### C99 — SURVIVED
- evidence: `.github/workflows/ci.yml:40 plugins/arch-compliance/skills/acf-setup/SKILL.md:228 docs/guides/SUPERPOWERS_COMPLEMENT.md:70-71 README.md:112`
- reasoning: I searched for invocations by name and by behaviour ('--mode staged', '--base', 'gate fails', 'diff gate', 'smoke'). Every command line or instruction that runs the gate is listed. The remaining hits are tool-name mentions (README.md:30, :62; SUPERPOWERS_COMPLEMENT.md:40, :61; ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:152, :193) or receipts of past runs. No .pre-commit-config or other workflow exists in the tree.

#### C100 — REFUTED
- evidence: `plugins/arch-compliance/profiles/python-service/ARCHITECTURE.md:27-28 plugins/arch-compliance/profiles/python-service/ARCHITECTURE.md:33 plugins/arch-compliance/profiles/python-service/ARCHITECTURE.md:39`
- reasoning: The python-service profile doctrine, which /acf-setup copies into hosts, carries the same `## Fail-loud ratchet` 'Enable the mandate and commit a … baseline' text and the same façade and FSM enablement instructions that §4.8 rewrites only in config/architecture/ARCHITECTURE.md. The design's new constraints make the profile text stale: the ratchet is ci/precommit-only with in-repo roots, and a row's id must equal its detector's mandate id with a Tier-1 site. The sweep was done per file, not per piece of prose.

### Unanchored findings

- **advisory**: The profile doctrine template carries the ratchet, façade and FSM enablement prose that §4.8 updates only in this repository's ARCHITECTURE.md, so hosts installed by /acf-setup get instructions missing the new load-time constraints.
  - evidence: `plugins/arch-compliance/profiles/python-service/ARCHITECTURE.md:27`
- **advisory**: load_baseline is a second load-parse-refuse loader beside load_model_file (loader.py:1-7 claims it is the only one); the design edits it but keeps it apart under an ADJACENT label the cited ADR text does not support, and leaves its read_text OSError (fail_loud_ratchet.py:83) untyped.
  - evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:77-98`
- **advisory**: After the design the diff gate gives built-in and host guards different path populations: the build-artifact guard gets every git-changed path, deleted ones included, while host guards get only paths RepoTree.file accepts. A host guard can never see a deletion, although §4.4 item 5 says a guard may flag a deleted file.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:161-163`
- **advisory**: make_line_lookup's bounded 1-based line rule is also written inline in fsm_guard's message snippet, so a second copy of the rule remains.
  - evidence: `plugins/arch-compliance/python/acf/detectors/fsm_guard.py:56`
- **advisory**: Decision 9 calls RepoTree 'the one place runtime code turns a path string into a location in the host repository', yet executable skill snippets join host-declared path strings to the root by hand (repo / cfg.ledger_path, repo / cfg.runs_dir), outside the guard's scanned dirs and missing from its stated blind spots.
  - evidence: `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:323`
- **advisory**: HOOK_CALL_SITES makes 'hook' and 'posttooluse' two accepted spellings of one site in the shared CallSite vocabulary, a compatibility alias that lets two hosts' registries diverge in naming.
  - evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/config/architecture/mandates.yml:11`

### Looked for but did not find

- another Tier-1 active-row filter: grep 'status != "unenforced"', 'status == "unenforced"', '.status', 'call_sites' in python/ and hooks/
- another path-to-repo-location site: grep '.resolve(', 'relative_to(', 'is_relative_to', 'joinpath', 'realpath|abspath|relpath|commonpath|os.path.join', root-named '/' joins, '.exists()|.is_file()|.is_dir()'
- another parse-or-skip: grep 'ast.parse', 'except SyntaxError' in python/, hooks/, skills/
- a dynamic module loader or module cache: grep 'importlib|import_module|spec_from_file_location|exec_module|runpy|exec(|__import__', 'sys.modules|lru_cache', 'sys.path'
- a third LineLookup: grep 'line_lookup|LineLookup|def _lookup|lines[line - 1]'
- other runtime spellings of TS mandate ids: grep 'fail-loud.empty-catch|no-shims.explicit-any' repo-wide
- another detector-id or call-site validator: grep 'KNOWN_DETECTORS|known_detectors|call_sites|detector' in the acf-setup, acf-mandate and architecture-review skills, test_profile_drift, test_self_host
- unlisted acf-check-diff invocations: grep 'acf-check-diff|cli_check_diff|--mode staged|--base|gate fails|diff gate|smoke', plus .pre-commit-config, workflows, Makefile
- call-site values outside CallSite: grep 'call_sites' in all yml (this repo and hm) and in inline test YAML and direct Mandate constructions

### Relationships

- SUBSUMED: `RepoTree.contained / RepoTree.file` — responsibility `decide whether a path string names a location inside the repository root` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:203-204`
  - resolution: The hook's is_absolute/resolve join and relative_to/except ValueError fallback (:242-245) collapse into RepoTree.file plus RepoTree.key, as the spec states.
- SUBSUMED: `RepoTree.directory / RepoTree.key` — responsibility `contain ratchet roots and key walked files` — existing `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:46`
  - resolution: The roots join (:46), the exists-skip (:56-57) and the walk filter (:59-62) collapse into RepoTree.directory and RepoTree.key.
- PARTIAL_OVERLAP: `RepoTree.file (load_baseline existence check)` — responsibility `load, parse and refuse a JSON input file` — existing `plugins/arch-compliance/python/acf/loader.py:43-77`
  - resolution: Shared responsibility R is load-parse-refuse of an input file. Give the baseline a pydantic model (files: dict[str, int]) and load it through load_model_file after RepoTree.file containment, re-raising AcfInputError as DetectorPackError in scan_ratchet. load_baseline's is_file check, json.loads, shape checks and the untyped read error collapse into load_model_file.
- PARTIAL_OVERLAP: `make_line_lookup` — responsibility `fetch a 1-based source line with bounds, empty when out of range` — existing `plugins/arch-compliance/python/acf/detectors/fsm_guard.py:56`
  - resolution: Shared responsibility R is the bounded 1-based line fetch. Extract a stdlib helper (e.g. acf.engine.line_at(lines, line) -> str). make_line_lookup's body and fsm_guard's inline snippet expression both become callers of it.
- IDENTICAL: `make_line_lookup` — responsibility `path-keyed line lookup passed to apply_registry` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80`
  - resolution: Both gate closures (here and posttooluse_gate.py:119-123) are deleted and the gates consume make_line_lookup.
- ADJACENT: `Mandate.runs_at / MandateRegistry.active` — responsibility `decide which rows are live at a gate` — existing `plugins/arch-compliance/python/acf/judge.py:218`
  - resolution: none
  - non-merge: Tier-2 reviews every llm row it is given and reads status == 'enforced' only to decide whether a provider is required; it neither routes by call site nor drops rows.
- ADJACENT: `HostHit -> Finding (_to_findings)` — responsibility `build a Finding from a mandate row and a hit` — existing `plugins/arch-compliance/python/acf/judge.py:238-255`
  - resolution: none
  - non-merge: The judge demotes severity by confidence, takes mandate_id from the model result, and admits path '<diff>' and line 0. Host findings take id and severity from the row and require a relative path and line >= 1.
- SUBSUMED: `validate_hit_fields` — responsibility `validate an external hit's line and message` — existing `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:88-89`
  - resolution: The bridge's int()/str() coercion becomes a validate_hit_fields call; HostHit uses the same function.
- ADJACENT: `load_host_detector` — responsibility `load a Python module from a file path` — existing `tests/test_check_installed_skills.py:15-18`
  - resolution: none
  - non-merge: A test helper loads one fixed repository script with no sys.modules registration, root policy or error typing; it is not runtime code and has no registry input.
- ADJACENT: `load_host_detector sys.path append` — responsibility `put a root on the import path` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:22-26`
  - resolution: none
  - non-merge: The hooks insert the plugin's own python/ at the front at start-up; the loader appends one host root once per process at dispatch, with different placement and purpose.
- ADJACENT: `Decision 9 RepoTree as sole path owner` — responsibility `join a host-declared path string to the repository root` — existing `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:323`
  - resolution: none
  - non-merge: ADR record locations may be absolute by the approved decision at docs/design/ADR_GATE_HOST_CONTRACT.md:295-301, so they are not containment cases. The spec should still name skill snippets as outside the guard's scope.
- PARTIAL_OVERLAP: `scan_host_guards input (in_repo)` — responsibility `define the changed-path population a guard receives` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:161-163`
  - resolution: Shared responsibility R is the set of changed paths handed to guards. Compute one guard-input list per gate and pass it to both scan_build_artifact_paths and scan_host_guards, or state why built-in guards see deleted paths and host guards do not.
- ADJACENT: `load_baseline/require_file refusal (C94)` — responsibility `refuse a missing file` — existing `plugins/arch-compliance/python/acf/loader.py:24-28`
  - resolution: none
  - non-merge: require_file takes a built Path and always raises AcfInputError; the new callers decide containment of a registry string and raise their phase's error.

### Two-owner counts

- load-parse-refuse an input file (load_model_file, fail_loud_ratchet.load_baseline): 2
- bounded 1-based source-line fetch (make_line_lookup, fsm_guard.py:56): 2
- row liveness decision (Mandate.runs_at for Tier-1, judge.py:218 for Tier-2): 2
- build a Finding from a mandate row (host _to_findings, judge._to_finding, architecture-review skill mapping): 3
- join a path string to the repo root (RepoTree, ADR skill snippets repo / cfg.*): 2
- load a Python module from a file path (load_host_detector, tests/test_check_installed_skills.py): 2
- changed-path population handed to guards in the diff gate (changed for build-artifact, in_repo for host guards): 2
- name of the edit-time call site (hook, posttooluse): 2

### Document conflicts

- `docs/design/ADR_GATE_HOST_CONTRACT.md:292` (restates): fail_loud_ratchet.load_baseline ... is a pre-existing second loader outside this phase.
- `docs/design/ADR_GATE_HOST_CONTRACT.md:301` (contradicts): a refusal would be a second implementation of the repo-relative test that ... citations.py:49 (_looks_absolute) and :74 (_escapes_repo) already own.
- `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:418` (contradicts): KNOWN_DETECTORS stays where the diff CLI defines it (plugins/arch-compliance/python/acf/cli_check_diff.py:25)
- `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:389` (contradicts): plugins/arch-compliance/tests/test_adr_exceptions.py:22 no-shims.hasattr | WARN | Context only
- `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:161` (contradicts): PostToolUse | Diff-scoped Tier 1 on edited .py / .ts / .tsx (and configured config paths); feed findings into the turn.
- `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:184` (restates): Unknown detector id referenced by an enforced ast or guard row → drift/registry validation fail.
- `plugins/arch-compliance/profiles/python-service/ARCHITECTURE.md:27` (restates): Optional whole-tree freeze of bare/broad-except counts. Enable the mandate and commit a config/architecture/fail_loud_ratchet.json baseline

## hardening

### Claim verdicts

#### C101 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:56-63; plugins/arch-compliance/python/acf/cli_check_diff.py:69-74; plugins/arch-compliance/hooks/posttooluse_gate.py:106-117; plugins/arch-compliance/hooks/inject_constraints.py:104; plugins/arch-compliance/python/acf/cli_check_llm.py:54`
- reasoning: Load-time checks live in the known_detectors branch (registry.py:56-63), so the host-file existence check still fails at load in both gates. Dispatch runs inside each gate's scan try: cli_check_diff.py:69-74 wraps load and scan and its except at :72 already lists UnknownDetectorError, and the hook's scan except at :113-117 is widened to include it. The hook passes known_detectors (§4.6), so importing at load would import every host module, [ci]-only guards included, on every edit. That part of the justification holds. One leg is weaker than stated: inject_constraints.py:104 and cli_check_llm.py:54 call load_mandates without known_detectors, so an import placed in that branch would never run host code there. The decision still stands on the hook leg.

#### C102 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:124-182; plugins/arch-compliance/hooks/posttooluse_gate.py:253-294; plugins/arch-compliance/python/acf/enforcement.py:46`
- reasoning: I traced each kind of active ast/guard row. Built-in rows: id must equal the contract's mandate_id, so findings stamped by the scanner land on the row (enforcement.py:46 routes by id). Their declared Tier-1 sites must lie within the contract's call_sites, and those match real dispatch: python_pack, TS, facade and fsm run in both gates (cli_check_diff.py:124-156, posttooluse_gate.py:253-282), build-artifacts in both (:158-166, :284-294), and the ratchet only in the diff gate (:168-182). Host rows: they need a Tier-1 site, a host ast row needs a language in {python, typescript, both}, and the runner builds findings from mandate.id, so they always land on a row. Reserved ids block a non-built-in row from capturing built-in findings. Unique ids plus id equality allow at most one active row per built-in detector. I found no row shape that loads yet runs nowhere.

#### C103 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:63; plugins/arch-compliance/hooks/posttooluse_gate.py:65; plugins/arch-compliance/tests/test_diff_cli.py:48`
- reasoning: Each production entry point resolves one repo per process: cli_check_diff.py:63 and posttooluse_gate.py:65, and the hook is a fresh subprocess per edit. The only multi-root producer is in-process tests, which call main() on different tmp_path repos (test_diff_cli.py:48, :61, :98, ...). The design refuses with AcfInputError at the producer boundary (rung 3) and resets state only in a test fixture, so no repair runs in production.

#### C104 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:67; plugins/arch-compliance/python/acf/detectors/python_pack.py:97; plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23; plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:6; config/architecture/mandates.yml:60`
- reasoning: The scanners stamp fixed mandate_id literals (python_pack.py:67, :97; the TS rules) and run at fixed gates (cli_check_diff.py:168-182 is the only ratchet call). The contract records facts that already exist. I ran a read-only YAML dump over the shipped and fixture registries. Every ast/guard row's id equals its detector's stamped id, no active built-in detector appears twice in one file, and the only ratchet rows are unenforced [ci]. So the one-row-per-detector cost hits no shipped registry.

#### C105 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:103-107; plugins/arch-compliance/python/acf/cli_check_llm.py:54; plugins/arch-compliance/python/acf/registry.py:33-41; plugins/arch-compliance/python/acf/loader.py:70-73`
- reasoning: inject_constraints.py:103-107 wraps load_mandates in except AcfInputError. cli_check_llm.py:54 calls load_mandates with no handler. load_model_file converts only ValidationError (loader.py:70-73), so an AcfInputError raised by a model_validator keeps its type. The existing MandateRegistry._unique_ids (registry.py:33-41, pinned by test_registry.py:40) already does exactly this. Rules on the model run at every construction (rung 1 for row shape), not only in the gates.

#### C106 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:35`
- reasoning: Built-in scanners each parse on their own (python_pack.py:35; the facade, fsm and ratchet modules likewise). The design keeps those parses and calls parse_python once per file for host ast rows only. This is an optimisation, not a recovery mechanism.

#### C107 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:46; plugins/arch-compliance/python/acf/finding.py:11-19`
- reasoning: apply_registry looks up rows by finding.mandate_id (enforcement.py:46). Finding carries a settable mandate_id, detector and severity (finding.py:11-19). Having hosts return HostHit with only path, line and message makes a wrong-row finding unrepresentable (rung 1), where accepting Finding and overwriting fields would be a repair.

#### C108 — SURVIVED
- evidence: `.gitignore:8; .github/workflows/ci.yml:40; plugins/arch-compliance/hooks/posttooluse_gate.py:72-81`
- reasoning: .acf/ is gitignored (.gitignore:8), so a CI checkout never has the marker. The CI step at ci.yml:40 invokes the diff gate explicitly. The hook exits 0 before the deferred imports when .acf/enabled is absent (posttooluse_gate.py:72-81). The residual case (a manual run in an untrusted checkout) is stated.

#### C109 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:27-52; plugins/arch-compliance/python/acf/cli_check_diff.py:127; plugins/arch-compliance/hooks/posttooluse_gate.py:254`
- reasoning: scan_python_file emits all three detectors' findings unconditionally (python_pack.py:41-51). Both gates call it with no registry (cli_check_diff.py:127, posttooluse_gate.py:254), and scan_typescript_file does the same. A [ci]-only no-shims.hasattr finding produced in the hook would survive without the sink filter. The filter sits at apply_registry, which already owns the status drop (enforcement.py:47), so it is a single sink (rung 2), not a second definition.

#### C110 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:22-26; pyproject.toml:19-20; .github/workflows/ci.yml:40`
- reasoning: The hook inserts the plugin's python/ at sys.path[0] (posttooluse_gate.py:22-26). The console script (pyproject.toml:19-20) starts with the script directory first. Appending the host root therefore adds no shadowing in either. The -m invocation (ci.yml:40) already puts cwd first, and the spec states this rather than claiming it is removed. The stated cost is real but bounded: a host top-level name that an earlier entry provides with the same callable name would resolve silently. The spec limits the fail-loud claim to 'the common case'. The dropped acf/ refusal is a removal, so I did not trace it.

#### C111 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:69-74; plugins/arch-compliance/hooks/posttooluse_gate.py:113-117; plugins/arch-compliance/python/acf/enforcement.py:49`
- reasoning: Both gates call the scan inside a try whose except lists DetectorPackError (cli_check_diff.py:72, posttooluse_gate.py:115). scan_host_guards runs inside _scan_changed / _scan_paths, so its OSError-to-DetectorPackError conversion reaches those handlers. apply_registry stays a pure lookup (enforcement.py:49). Reading lazily in line_lookup would put I/O and a new raise outside the try, at cli_check_diff.py:82 and posttooluse_gate.py:125.

#### C112 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:16; plugins/arch-compliance/python/acf/cli_check_diff.py:21`
- reasoning: acf.judge imports acf.registry (judge.py:16), so registry importing judge would be a cycle. Passing the ids in is required. cli_check_diff.py:21 already imports LLM_PROMPT_IDS, so the runtime consumer exists.

#### C113 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/run_guards.py:116; C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/run_guards.py:317-321; plugins/arch-compliance/python/acf/cli_check_diff.py:29-61`
- reasoning: The origin runner selects rows per site at run_guards.py:116 (`if site not in entry.call_sites`) and defaults --site to ci (:317-321), as the spec says. The diff gate's argparse block (cli_check_diff.py:29-61) can take a required choices argument, which exits 2 on a missing value. That is fail loud at the invocation (rung 3), not a default.

#### C114 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/run_guards.py:126-130; plugins/arch-compliance/python/acf/cli_check_diff.py:69-74`
- reasoning: run_guards.py:126-130 refuses a site that resolves to zero guards ('refusing to report a green run'). The shipped dump shows no row declares precommit today, so without the row additions a precommit run selects nothing. The refusal can sit inside the try at cli_check_diff.py:69-74. One asymmetry: the PostToolUse hook gets no matching refusal. See the unanchored findings.

#### C115 — SURVIVED
- evidence: `C:/Users/iball/AppData/Roaming/Python/Python313/site-packages/pydantic/main.py:1; plugins/arch-compliance/python/acf/finding.py:11`
- reasoning: Pydantic 2.13.3 BaseModel stores field values in the instance __dict__. The exact-type check `type(item) is not HostHit` runs before any attribute access, so `item.__dict__` reaches the normal descriptor, not a host override. The before-validator then refuses anything that is not exactly str/int/str, so the rebuilt HostHit holds only plain values. All of this sits inside the wrapped try. The rebuild refuses rather than repairs (rung 3 at an external boundary).

#### C116 — SURVIVED
- evidence: `docs/design/ADR_GATE_HOST_CONTRACT.md:295-301; plugins/arch-compliance/python/acf/adr/citations.py:75-76`
- reasoning: This is a deletion decision, so no producer trace applies. The duplicates it names exist (citations.py:75-76, matching the census). The carve-out it keeps is the approved 'Not adopted' text at ADR_GATE_HOST_CONTRACT.md:295-301.

#### C117 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/genre_conditional_guard.py:32-40`
- reasoning: genre_conditional_guard.py:32-40 declares a non-frozen @dataclass Finding whose __str__ calls self.line_text.strip(). A None line_text, which the dataclass does not prevent, makes str() raise. So the object class that produces the invalid state exists in host code. The spec admits that no host code raises such an exception today. The mechanism sits at a genuine external boundary (arbitrary host code), where rung 5 is legitimate. It degrades only the message: the typed error is still raised.

#### C118 — SURVIVED
- evidence: `docs/design/evidence/HOST_DETECTOR_EXTENSION_POINT/path_census_a338cad.txt:1; plugins/arch-compliance/hooks/posttooluse_gate.py:204; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:46; C:/Users/iball/Arduino/Projects/HistoricMansions/GEMINI.md:131`
- reasoning: As a second method I ran git grep for .resolve(/.relative_to(/is_relative_to(/joinpath(/os.path.* and for `<rootname> / `. The non-__file__ and non-repo.py hits match the committed census exactly: citations.py:75,76,168; cli_check_diff.py:66 (allowlisted), :118; cli_check_llm.py:50 (allowlisted); fail_loud_ratchet.py:45,46,60,124; typescript_bridge.py:27 (allowlisted); posttooluse_gate.py:204,243. So the guard can start green once those sites migrate. A façade plus a guard is rung 2 (single owner, enforced); helpers alone would leave several owners. GEMINI.md:131 is the quoted façade rule. The blind spots are stated.

#### C119 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:14-27; plugins/arch-compliance/python/acf/registry.py:33-45`
- reasoning: Mandate declares id, severity, status, detection, detector, languages (a Literal that includes 'none'), call_sites list[str] and params dict|None, and sets no model_config. MandateRegistry already carries a model_validator and an @property (registry.py:33-45), so a property, a method and a validator are compatible with the model.

#### C120 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/finding.py:6-19`
- reasoning: Finding's required fields are mandate_id, severity, path, line, message and detector. detection defaults to 'ast' and confidence is optional. Severity is a str Enum with values BLOCK/WARN, the same Literal as Mandate.severity, so Severity(mandate.severity) constructs.

#### C121 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:47; plugins/arch-compliance/python/acf/enforcement.py:23; plugins/arch-compliance/python/acf/enforcement.py:43-52`
- reasoning: apply_registry looks up by_id (:43, :46), drops on status at :47, and handles exemptions at :49-51 and severity at :52. LineLookup is Callable[[str, int], str] at :23, which make_line_lookup's closure satisfies.

#### C122 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:72; plugins/arch-compliance/python/acf/cli_check_diff.py:115-156; plugins/arch-compliance/python/acf/cli_check_diff.py:168-184`
- reasoning: Load is at :70 inside the try. The except at :72 lists GitError, AcfInputError, UnknownDetectorError and DetectorPackError around both load and scan. Lookup and apply are at :76-82. In the .py branch, repo, text, posix, lines and the registry are in scope after :150. The .ts branch reads at :152, which can bind text. `changed` is in scope after the ratchet loop, at :184.

#### C123 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:113-117; plugins/arch-compliance/hooks/posttooluse_gate.py:91-110; plugins/arch-compliance/hooks/posttooluse_gate.py:200-209; plugins/arch-compliance/hooks/posttooluse_gate.py:229-294`
- reasoning: Every named site is where the claim puts it: deferred imports at :91-104, the load try at :106-110, the scan try at :113-117, lookup/apply at :119-125, and the resolve/dedupe loop at :200-209. The is_file skip is at :239, relative_to/ValueError at :242-245, and the inline filters at :229-236 and :284-286. text (bound at :251 before the branch) and rel are in scope in both the .py and TS branches.

#### C124 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:72; plugins/arch-compliance/hooks/posttooluse_gate.py:113-117; plugins/arch-compliance/python/acf/enforcement.py:43-53`
- reasoning: All host entry (load_host_detector, _call_host, _to_findings, scan_host_guards' read) runs inside scan_host_ast_file / scan_host_guards, which are called inside _scan_changed / _scan_paths. Those sit under cli_check_diff.py:69-74 (except :72 has all three types) and the hook's scan try at :113-117, which is widened to all three. apply_registry (enforcement.py:43-53) does no I/O and receives only rebuilt hits. callable(fn) after the region reads a type slot, not host code. Host code that runs after return (atexit, threads) is stated as unconfined.

#### C125 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_diff_cli.py:48; plugins/arch-compliance/tests/test_diff_cli.py:154; C:/Python313/Lib/dataclasses.py:757`
- reasoning: Each step uses stdlib APIs that exist: spec_from_file_location with a synthetic name, module_from_spec, registering in sys.modules before exec_module, and pop on failure. test_diff_cli calls main() in process over separate tmp_path repos (:48, :61, :98, :154). Only the new host cases trigger the loader, and they use the fixture, which resets _ACTIVE_ROOT and drops _acf_host_ keys and modules under the served root. That covers cached host top-level packages such as `scripts`.

#### C126 — SURVIVED
- evidence: `C:/Python313/Lib/dataclasses.py:757; C:/Python313/Lib/dataclasses.py:760`
- reasoning: dataclasses resolves string annotations through sys.modules.get(cls.__module__).__dict__ (dataclasses.py:757, :760 on 3.13.2). A synthetic-name module not yet registered gives None.__dict__, an AttributeError. Registering before exec_module is the required hook.

#### C127 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_import_graph.py:70-76; plugins/arch-compliance/python/acf/judge.py:16; plugins/arch-compliance/python/acf/engine.py:8; plugins/arch-compliance/python/acf/repo.py:9; plugins/arch-compliance/python/acf/loader.py:15-18; plugins/arch-compliance/python/acf/adr/host.py:16`
- reasoning: engine.py and repo.py import only pathlib. loader imports yaml, pydantic and acf.exceptions. No scanner module imports acf.registry or acf.detectors (grep of the detectors' imports), so acf.detectors/__init__ -> acf.registry has no back edge. judge imports registry, not the reverse. acf.adr already imports acf.repo (adr/host.py:16). The hook's new imports (acf.detectors, acf.registry, acf.enforcement) do not reach acf.adr or acf.judge. The test at :70-76 checks hook source text only.

#### C128 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:48-64; plugins/arch-compliance/python/acf/loader.py:67-73`
- reasoning: registry.py:53-55 calls load_model_file(path, Mandate, subject='mandates file', fmt='yaml', many=True), and :64 returns MandateRegistry(mandates=..., source_path=path.as_posix()). With many=True, loader.py:67-73 returns a list of models.

#### C129 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_repo_paths.py:47-48; plugins/arch-compliance/hooks/posttooluse_gate.py:11-12`
- reasoning: The pinned string is posttooluse_gate.py:11 ('If enabled and ... mandates.yml is missing'). A grep for 'Otherwise scan' (line :12) under tests finds nothing.

#### C130 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:78-82; config/architecture/mandates.yml:60`
- reasoning: _is_bare_or_exception matches only `node.type is None` or `ast.Name` with id 'Exception'. An `except BaseException` handler is not flagged. mandates.yml:60 declares the fail-loud.bare-except-ok token.

#### C131 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/engine.py:8; plugins/arch-compliance/python/acf/engine.py:17-24; plugins/arch-compliance/python/acf/repo.py:9`
- reasoning: engine.py imports only pathlib (:8) and defines contains_backslash at :17-24. repo.py imports only pathlib (:9), and its docstring (:1-6) states the stdlib-only contract that both hooks rely on.

#### C132 — SURVIVED
- evidence: `README.md:66-74; plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23; plugins/arch-compliance/tests/test_registry.py:24`
- reasoning: The README table header is at :66 and its rows run :68-74, with detector-id and mandate-id columns. emptyCatch.ts:23 and the explicitAny rule each carry a literal mandate_id. test_registry.py:21-28 and :33-37 build inline YAML rows, the shape the new cases need.

#### C133 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_hooks.py:22-29; plugins/arch-compliance/tests/test_diff_cli.py:48`
- reasoning: test_hooks.py has a subprocess runner (:22-29), and test_diff_cli drives main() in process on temporary git repos (:48 and onward). Every built-in detector can be triggered by a generated fixture: .py and .ts content, a dist/ path, and a ratchet baseline. With the --call-site argument, the diff gate can be run once per site.

#### C134 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:109; plugins/arch-compliance/python/acf/cli_check_diff.py:184; plugins/arch-compliance/hooks/posttooluse_gate.py:226; plugins/arch-compliance/hooks/posttooluse_gate.py:295`
- reasoning: file_lines is a local built in _scan_changed (:109, returned at :184) and in _scan_paths (:226, returned at :295). Both functions run under their gate's scan try, so a call before their return statements is wrapped.

#### C135 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:29-61; plugins/arch-compliance/python/acf/cli_check_diff.py:69-74`
- reasoning: The parser at :29-61 uses plain add_argument calls, so required=True with choices is a drop-in; argparse raises SystemExit(2). The try at :69-74 encloses the load, so an empty-selection AcfInputError raised after the load reaches the except at :72. sites can be threaded into _scan_changed (:71) and into apply_registry at :82.

### Unanchored findings

- **important**: In acf-check-diff, host guards receive only changed paths that RepoTree.file accepts (existing in-repo regular files), so a deleted path never reaches them. That contradicts §4.4 item 5 ('a guard may flag a deleted file') and the §4.8 prose for README.md:62/:76/:106 and ARCHITECTURE.md:9-11 ('host guards see every changed path'), while the built-in build-artifact guard keeps receiving the full `changed` list. A host guard that checks deletions silently sees nothing.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:118-120`
- **advisory**: The empty-selection refusal ('refusing to report a clean run') is added only to acf-check-diff. The PostToolUse hook, now routed by call_sites, reports 'no findings' on every edit when no active ast/guard row declares hook or posttooluse, which is the same false green the design refuses at the diff gate.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:106-117`

### Looked for but did not find

- A production caller that resolves more than one repository per process (cli_check_diff.py:63 and posttooluse_gate.py:65 are the only roots); none found, so the one-root refusal has only test producers
- A built-in scanner that consults call_sites before emitting (python_pack.py:27-52 and the TS bridge do not); so the apply_registry filter is not redundant
- Path-to-repo-location sites outside the committed census: a git grep for resolve/relative_to/is_relative_to/joinpath/os.path.* and root-named '/' joins found no extra site in plugins/arch-compliance/python or hooks beyond __file__-based and acf/repo.py ones
- A shipped or fixture registry with two active rows for one built-in detector, a row id that disagrees with its detector's stamped id, or an active ratchet row declaring hook; none found
- Rung 1 for the built-in id-equality and reserved-id refusals: routing built-in findings by detector would replace them with an equivalent 'one active row per built-in detector' refusal, so rung 3 is the highest that applies
- A path by which an exception from host code escapes both gates' except tuples; none, since every host entry runs inside _scan_changed/_scan_paths under the scan try
- A dataclasses hook other than sys.modules[cls.__module__] that would make pre-registration unnecessary; none (dataclasses.py:757)

### Mechanism traces

- **apply_registry call_sites filter (Mandate.runs_at at the sink)**
  - invalid state: a Finding f with by_id[f.mandate_id] active but call_sites ∩ row.call_sites = ∅ for the running gate
  - producer: `plugins/arch-compliance/python/acf/detectors/python_pack.py:41-51`
  - rung 2 (highest applicable 2); repairs=False
  - hardening rejected because: This filter is needed at that one sink because the built-in scanners emit findings without consulting the registry
  - spec citation: `None`
- **Mandate._row_shape model_validator**
  - invalid state: a Mandate with detection in {ast,guard} whose detector contains ':' but fails parse_host_detector_ref; or active with call_sites ∩ TIER1 = ∅; or active host ast with languages == 'none'
  - producer: `config/architecture/mandates.yml:55-62`
  - rung 1 (highest applicable 1); repairs=False
  - spec citation: `None`
- **load_mandates built-in contract checks (_check_builtin, reserved built-in mandate ids)**
  - invalid state: an active row r where (r is built-in and (r.detector not in KNOWN_DETECTORS or r.id != contract.mandate_id or TIER1 ∩ r.call_sites ⊄ contract.call_sites)) or (r is not built-in and r.id in {c.mandate_id})
  - producer: `plugins/arch-compliance/python/acf/registry.py:56-63`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: the scanners stamp fixed mandate ids and run at fixed gates, so the contract records an existing fact rather than adding a capability
  - spec citation: `None`
- **acf-check-diff empty-selection refusal and required --call-site**
  - invalid state: registry.active({site}) contains no row with detection in {ast,guard}
  - producer: `plugins/arch-compliance/profiles/python-service/mandates.yml:18`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `None`
- **load_host_detector one-root-per-process refusal**
  - invalid state: a load_host_detector call with RepoTree(repo_root).root != _ACTIVE_ROOT
  - producer: `plugins/arch-compliance/tests/test_diff_cli.py:48`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: every production caller resolves one repository per process ... no repair mechanism lives in production code
  - spec citation: `None`
- **sys.modules pre-registration and removal on failed load**
  - invalid state: sys.modules[name] holds a partially executed host module after exec_module or lookup raised
  - producer: `C:/Python313/Lib/dataclasses.py:757`
  - rung 2 (highest applicable 2); repairs=False
  - hardening rejected because: The module is registered in sys.modules before exec_module, which dataclasses needs to resolve string annotations
  - spec citation: `None`
- **_call_host wrapped call, consumption and _revalidate rebuild**
  - invalid state: an item from a host callable's result with type(item) is not HostHit, or with fields not exactly str/int>=1/non-empty str, or a call/iteration that raises
  - producer: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/genre_conditional_guard.py:32-40`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: field access and comparisons on an unvalidated host object can run host code, so they must happen inside the wrapped region
  - spec citation: `None`
- **_describe constant-message fallback**
  - invalid state: an exception exc from host code for which str(exc) or type(exc).__name__ raises
  - producer: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/genre_conditional_guard.py:39-40`
  - rung 5 (highest applicable 5); repairs=True
  - hardening rejected because: No origin-host code raises an exception carrying such an object today, so the helper guards the boundary with arbitrary host code rather than a known failure.
  - spec citation: `None`
- **_to_findings containment and ast-path refusals**
  - invalid state: a HostHit h with RepoTree(root).contained(h.path) is None, or (row.detection == 'ast' and h.path != expected_path)
  - producer: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/metadata_facade_guard.py:66`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: one HostHit type serves both callable kinds, and a path-less ast hit would be a second type carrying the same facts
  - spec citation: `None`
- **scan_host_guards lenient line read (errors=replace) and missing-file [] fill**
  - invalid state: a file named by a host guard hit whose bytes are not valid UTF-8, or which does not exist as a regular file
  - producer: `plugins/arch-compliance/hooks/posttooluse_gate.py:251`
  - rung 5 (highest applicable 5); repairs=True
  - hardening rejected because: a guard may flag any file, a binary or a document included, and these lines serve only the exemption-token lookup, so a stray byte is replaced rather than raised
  - spec citation: `None`
- **RepoTree.contained mapping RuntimeError/ValueError from resolve to None**
  - invalid state: a path string p for which (root / p).resolve() raises RuntimeError (symlink loop on 3.11/3.12) or ValueError (embedded NUL)
  - producer: `plugins/arch-compliance/python/acf/adr/citations.py:76`
  - rung 3 (highest applicable 3); repairs=True
  - hardening rejected because: RepoTree.contained maps the loop to None, the value every caller already treats as "not under the root"
  - spec citation: `None`
- **RepoTree façade with test_repo_tree_guard AST guard**
  - invalid state: runtime code outside acf/repo.py joins, resolves or compares a path string against the repository root
  - producer: `plugins/arch-compliance/hooks/posttooluse_gate.py:204`
  - rung 2 (highest applicable 2); repairs=False
  - hardening rejected because: helpers leave each caller holding the root and a raw string, so nothing stops a new site from joining or resolving by hand
  - spec citation: `None`
- **TypeScript bridge validate_hit_fields and TS_MANDATE_IDS lookup**
  - invalid state: a Node scanner item whose detector is not a TS_MANDATE_IDS key, or whose line is not an int >= 1, or whose message is not a non-empty str
  - producer: `plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:21-25`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `None`
- **Ratchet baseline/roots containment and existence refusals**
  - invalid state: params.baseline or a params.roots entry that escapes the root, loops, or (for roots) names no existing directory
  - producer: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:46`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `None`

## Claims

- **C1** [premise] [load-bearing]: Today load_mandates (registry.py:48-64) skips every row whose status is not 'enforced' (:58) and raises UnknownDetectorError (:60-63) only for an enforced ast/guard row whose detector is not in known_detectors.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:58`
- **C2** [premise] [load-bearing]: KNOWN_DETECTORS (cli_check_diff.py:25) is the closed union ALL_PYTHON_DETECTOR_IDS | TS_DETECTOR_IDS | LLM_PROMPT_IDS and nothing extends it (recipe: git grep -n "KNOWN_DETECTORS" -- plugins tests); because it includes the LLM prompt ids, an active ast row naming an LLM prompt id passes load_mandates' known_detectors check today although no Tier-1 scanner dispatches on that id.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:25`
- **C3** [premise] [load-bearing]: Neither gate can execute a non-built-in detector: _scan_changed (cli_check_diff.py:102-184) and _scan_paths (posttooluse_gate.py:213-295) call only built-in scanners, selected by exact built-in id (cli_check_diff.py:94-99, posttooluse_gate.py:229-236, :284-286), and no dynamic loader exists in the plugin runtime (git grep for importlib|import_module|spec_from_file_location|exec_module over plugins/arch-compliance/python and plugins/arch-compliance/hooks prints nothing).
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:102-184`
- **C4** [premise] [load-bearing]: posttooluse_gate.py:108 catches only AcfInputError around load_mandates, and UnknownDetectorError subclasses AcfError, not AcfInputError (exceptions.py:5, :13), so passing known_detectors in the hook requires also catching UnknownDetectorError there.
  - spec citation: `plugins/arch-compliance/python/acf/exceptions.py:13`
- **C5** [premise] [load-bearing]: Mandate.call_sites is list[str] (registry.py:21) and no Tier-1 gate reads it: the gates select rows on detector id and status only and apply_registry on status only; git grep -n "call_sites" -- plugins/arch-compliance/python plugins/arch-compliance/hooks prints only registry.py:21 and two unrelated surface_call_sites lines in acf/adr/ledger.py.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:21`
- **C6** [premise] [load-bearing]: This repository's no-shims.hasattr row declares call_sites: [ci] (config/architecture/mandates.yml:70), the PostToolUse hook reports it at edit time today, and plugins/arch-compliance/tests/test_hooks.py:199-218 is a test that pins that behaviour (so unifying call_sites routing necessarily changes that test).
  - spec citation: `plugins/arch-compliance/tests/test_hooks.py:199-218`
- **C7** [premise] [load-bearing]: test_hooks_do_not_reach_acf_adr pins only the literal text 'acf.adr' in the two hook files and states the intent that acf.adr must never enter the hooks' import graph; acf.registry and acf.enforcement are imported by the PostToolUse hook; and acf.adr already imports acf.engine (adr/contract.py:20). So moving the two path helpers into acf.engine keeps the dependency direction acf.adr -> acf.engine and keeps acf.adr out of the hook's graph.
  - spec citation: `plugins/arch-compliance/tests/test_adr_import_graph.py:70-76`
- **C8** [premise] [load-bearing]: The Tier-2 judge selects llm rows by detection and reads status == 'enforced' only to decide whether a provider is required (judge.py:213-218); it does not use the Tier-1 row filters being replaced, so leaving it unchanged creates no divergence the design must resolve.
  - spec citation: `plugins/arch-compliance/python/acf/judge.py:213-218`
- **C9** [premise] [load-bearing]: Trust seam: posttooluse_gate.py:72-81 exits 0 when .acf/enabled is absent, before importing anything beyond acf.repo and before loading mandates.yml, so no host module can be imported by the hook without the marker.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:72-81`
- **C10** [premise] [load-bearing]: .acf/ is gitignored (.gitignore:8) and this repository's CI invokes acf.cli_check_diff (.github/workflows/ci.yml:40), so a CI checkout never carries .acf/enabled; acf-check-diff does not check the marker today, and requiring it there would disable CI.
  - spec citation: `.gitignore:8`
- **C11** [premise] [load-bearing]: hooks/inject_constraints.py catches AcfInputError around its load_mandates call (:104-105), so making a malformed host reference raise AcfInputError needs no change there; cli_check_llm.py:54 also needs none.
  - spec citation: `plugins/arch-compliance/hooks/inject_constraints.py:105`
- **C12** [premise] [load-bearing]: Because load_mandates never imports host code under the design (validation is syntax, call sites, languages and file existence only), the SubagentStart hook (inject_constraints.py:104) and acf-check-llm (cli_check_llm.py:54) run no host code; no other path from those two entry points reaches load_host_detector.
  - spec citation: `plugins/arch-compliance/hooks/inject_constraints.py:104`
- **C13** [premise]: Deferral: no architecture-review host configuration file exists and this design adds no architecture-review runtime code; the existing compliance-baseline module that architecture-review uses (plugins/arch-compliance/python/acf/baseline.py) is not modified by any section of the spec. (Not load-bearing.)
  - spec citation: `None`
- **C14** [premise] [load-bearing]: Deferral: the origin host's mandate rows (hm:config/architecture/mandates.yml at b652fab05) carry no languages or arch_anchor field, both of which Mandate requires (registry.py:20, :24), so they need rewriting at cutover regardless of this design; no change to HistoricMansions is needed in this slice.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:20`
- **C15** [premise] [load-bearing]: Deferral: the origin host's driver reports unparseable changed files (hm:scripts/ci/arch_compliance/driver.py:150-163) and its guards can depend on diff mode; scan_host_ast_file skips unparseable files like the built-in scanners and scan_guard receives no diff mode, and these gaps are left to the cutover spec. A host needing parse-failure reporting can declare it as a guard (scan_guard receives repo_root and every changed path, enough to re-parse).
  - spec citation: `hm:scripts/ci/arch_compliance/driver.py:150-163`
- **C16** [premise] [load-bearing]: No shared Tier-1 dispatcher is needed for ## Single point of definition: the host decision procedure (row selection, loading, calling, wrapping, Finding construction, guard-line reading and its precedence rule) has one implementation in acf.detectors.host, and each gate only calls scan_host_ast_file and scan_host_guards as it already calls each built-in scanner; the two pre-existing dispatch loops (cli_check_diff.py:102-184, posttooluse_gate.py:213-295) differ in diff scope, path collection and file filter and are not a second implementation of that procedure.
  - spec citation: `config/architecture/ARCHITECTURE.md:198-200`
- **C17** [premise]: Each of the four built-in scanners that parse Python (python_pack.py:34-37, facade_sinks.py:50-53, fsm_guard.py:36-39, fail_loud_ratchet.py:23-26) wraps ast.parse in try/except SyntaxError and returns its empty result; acf.engine.parse_python returns None on SyntaxError, and scan_host_ast_file and each scanner keep their empty result on None.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37`
- **C18** [premise] [load-bearing]: Appendix receipt: the load_mandates callers outside registry.py are exactly those the git grep recipe prints (inject_constraints.py:104, posttooluse_gate.py:107, cli_check_diff.py:70, cli_check_llm.py:54, acf-mandate SKILL.md:95 plus prose at :141, architecture-review SKILL.md:62, test_profile_drift.py:24, test_registry.py:10,17,30,47,57, tests/test_self_host.py:23); only cli_check_diff.py:70, SKILL.md:95, test_profile_drift.py:24, test_registry.py:30 and test_self_host.py:23 pass known_detectors, and the others reach only the syntax check. (Load-bearing: a caller passing known_detectors without repo_root raises AcfInputError on any active host row.)
  - spec citation: `None`
- **C19** [premise] [load-bearing]: Appendix receipt: apply_registry's callers are exactly posttooluse_gate.py:125, cli_check_diff.py:82 and test_enforcement.py at :54, 60, 66, 72, 84, 94, 104, 110, 125, 130 (recipe git grep -n "apply_registry(" -- '*.py'), so adding a required keyword call_sites touches only those.
  - spec citation: `None`
- **C20** [premise] [load-bearing]: Appendix receipt: the Tier-1 active-row filters are exactly cli_check_diff._active_mandates (:94-99; used at :112, :113, :158, :168), the hook's inline filters (posttooluse_gate.py:229-236 and :284-286, matched at :231, :235, :285) and apply_registry's status check (enforcement.py:47); the wider .status recipe adds only registry.py:58 (replaced), judge.py:218 (Tier-2) and a display-only read at inject_constraints.py:158.
  - spec citation: `None`
- **C21** [premise] [load-bearing]: Every built-in Tier-1 scanner stamps exactly one fixed mandate_id on its findings (build_artifacts.py:31, facade_sinks.py:69, fail_loud_ratchet.py:132, fsm_guard.py:59, python_pack.py:67/97/144/172; TypeScript emptyCatch.ts:23 and explicitAny.ts:15), and apply_registry matches findings to rows by mandate_id (enforcement.py:46), so a row whose id differs from its detector's stamped id never receives a finding.
  - spec citation: `None`
- **C22** [premise] [load-bearing]: fail_loud_ratchet runs only in acf-check-diff (cli_check_diff.py:168-182); the hook's _scan_paths has no ratchet call. Every other built-in ast/guard detector (three python_pack ids, two TS ids, forbid_facade_sink, fsm_transition_guard, no_build_artifacts) runs in both gates, at the lines in the spec's section 4.3 table.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:168-182`
- **C23** [premise] [load-bearing]: Executed census: applying the section 4.2 _check_builtin rules with the section 4.3 table and the Mandate._row_shape rules refuses no row in config/architecture/mandates.yml, plugins/arch-compliance/profiles/*/mandates.yml, plugins/arch-compliance/tests/fixtures/mandates_valid.yml, or any inline YAML registry in plugins/arch-compliance/tests (test_diff_cli.py, test_registry.py, test_judge.py, test_hooks.py), except test_registry.py's not_a_real_detector row, which is meant to raise UnknownDetectorError. Also check rows that test_hooks.py and test_diff_cli.py write by editing copied fixtures.
  - spec citation: `None`
- **C24** [premise] [load-bearing]: An AcfInputError raised inside a Mandate model_validator propagates with its own type through load_model_file (which catches only pydantic ValidationError, loader.py:70-73) and through direct Mandate(...) construction; MandateRegistry._unique_ids (registry.py:33-41) already relies on this. Direct Mandate construction in tests (test_enforcement.py:19, test_judge.py:41, test_template.py:73) is not refused by the new _row_shape validator.
  - spec citation: `plugins/arch-compliance/python/acf/loader.py:70-73`
- **C25** [premise] [load-bearing]: Every current user of KNOWN_DETECTORS (cli_check_diff.py:25,70; acf-mandate SKILL.md:91,95,106,111,112; test_profile_drift.py:7,24; tests/test_self_host.py:5,14,23; ARCHITECTURE.md:228) keeps working when it becomes a Mapping[str, BuiltinDetector] re-exported from acf.detectors, including sorted(KNOWN_DETECTORS) in the skill. test_registry.py:30 passes a frozenset and is listed to change.
  - spec citation: `None`
- **C26** [premise] [load-bearing]: Every production caller resolves exactly one repository per process (cli_check_diff.py:63; posttooluse_gate.py:65, a fresh process per edit), so refusing a second host root in load_host_detector never fires in production; only in-process tests over several roots need the fresh_host_loader fixture.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:63`
- **C27** [premise]: KNOWN_DETECTORS has 13 ids today (9 Python and TypeScript ids plus 4 LLM prompt ids) and 9 after the design. (Precision fact.)
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:25`
- **C28** [premise] [load-bearing]: load_mandates with llm_prompt_ids=LLM_PROMPT_IDS refuses no shipped row: every active llm row in config/architecture/mandates.yml, plugins/arch-compliance/profiles/*/mandates.yml, tests/fixtures/mandates_valid.yml and the inline registries loaded by acf-check-diff, tests/test_self_host.py or the acf-mandate snippet names an id in acf.judge.LLM_PROMPT_IDS (judge.py:29-36); the acf-mandate SKILL.md:56 and :121 prompt-id rule is then enforced at acf-check-diff.
  - spec citation: `None`
- **C29** [premise] [load-bearing]: getattr(mod, attr, None) swallows only AttributeError, so a host module-level __getattr__ raising anything else escapes a bare lookup; in spec §4.4 item 3 exec_module and the lookup share one try whose `except BaseException` handler re-raises KeyboardInterrupt and turns every other exception into UnknownDetectorError, which cli_check_diff.py:72 and the hook's widened scan except catch. sys.modules is the one record of a loaded host module: a failure while this call is the first to load the module removes the entry it registered; a failed lookup on a module an earlier call loaded leaves it registered.
  - spec citation: `None`
- **C30** [premise] [load-bearing]: pyproject.toml:5 allows Python 3.11, where a non-strict Path.resolve() raises RuntimeError on a symlink loop (3.13 does not), and on POSIX an embedded NUL makes resolve() raise ValueError; RepoTree.contained catching both and returning None makes such a host path report as a missing file at load (UnknownDetectorError), be refused as a host hit (DetectorPackError in _to_findings), or classify as unresolved in citations, never a traceback.
  - spec citation: `pyproject.toml:5`
- **C31** [premise] [load-bearing]: The TypeScript bridge's Finding construction sits in a try at typescript_bridge.py:82-95 whose except (KeyError, TypeError, ValueError) re-raises as DetectorPackError (:94-95); stamping mandate_id=TS_MANDATE_IDS[item['detector']] and calling validate_hit_fields(item['line'], item['message']) inside it yields DetectorPackError for an unknown detector or a refused line or message; the Node rules emit detectors empty_catch and explicit_any (emptyCatch.ts:28, explicitAny.ts:22), an integer line >= 1 and a non-empty message, so no finding the pack produces today is refused once the rules stop emitting mandate_id.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:82-95`
- **C32** [premise] [load-bearing]: Decision 6's entry-point table is accurate: the PostToolUse hook inserts the plugin's python/ at sys.path[0] ahead of the hooks directory (posttooluse_gate.py:22-26) and imports acf first (:28), so the host root is not on sys.path before the loader appends it; the acf-check-diff console script (pyproject.toml:19-20) likewise; under python -m acf.cli_check_diff run from the host root (.github/workflows/ci.yml:40) the working directory is already sys.path[0], so appending changes nothing there. Host intra-repo imports such as hm:scripts/ci/metadata_facade_guard.py:66 resolve against the host root in the documented invocations.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:22-28`
- **C33** [premise] [load-bearing]: acf-check-diff today has no argument naming its call site (cli_check_diff.py:29-61 offers --mode, --base, --repo, --mandates, --json), so it cannot tell a pre-commit run from a CI run; the origin host's guard runner selects rows per --site (hm:scripts/ci/run_guards.py:116), refuses an unknown site (:107-111) and an empty selection (:126-130), with --site defaulting to ci (:317-321).
  - spec citation: `hm:scripts/ci/run_guards.py:116`
- **C34** [premise] [load-bearing]: file_lines holds only changed .py/.ts/.tsx files (cli_check_diff.py:126, :152; posttooluse_gate.py:248-252) plus, under the design, files a host guard flagged; built-in line-1 findings (fail_loud_ratchet.py:135, build_artifacts.py:34) on any other file still get '' and stay non-exemptable, as at a338cad, and a staged dist/x.py is already in file_lines today.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:135`
- **C35** [premise] [load-bearing]: No shipped or fixture registry row declares precommit today (git grep -n precommit -- '*.yml' prints nothing); adding precommit to each ast/guard row that declares ci (9 rows in config/architecture/mandates.yml, 7 in profiles/python-service, 3 in profiles/react-app, 3 in tests/fixtures/mandates_valid.yml) makes acf-check-diff --call-site precommit select exactly the rows acf-check-diff runs today, and refusing a site that selects no active ast/guard row prevents a clean report over an empty selection.
  - spec citation: `None`
- **C36** [premise] [load-bearing]: HostHit's mode='before' model_validator (spec §4.4 item 1) receives the raw field mapping for both HostHit(...) and HostHit.model_validate(dict), so it refuses a field that is not exactly str, int and str before pydantic's lax coercion runs; _revalidate (type(item) is HostHit, then HostHit.model_validate(dict(item.__dict__))) inside _call_host's try therefore refuses a host subclass and a model_construct'ed or mutated hit with b'a.py', '5', True or object values on any pydantic 2.x, accepts a hit built from plain str and int values, and leaves _to_findings running no host code.
  - spec citation: `None`
- **C37** [premise] [load-bearing]: acf.repo.RepoTree.file (RepoTree.contained, then Path.is_file, OSError from stat propagating) returns None for a missing path, a directory, an out-of-root path and a symlink loop on Python 3.11 to 3.13, and each runtime caller in spec §4.2, §4.4 and §4.9 (load_mandates, load_host_detector, scan_host_guards, scan_ratchet) catches OSError around it and raises its typed error, while the PostToolUse hook's _collect_paths lets it propagate exactly as its is_file() at posttooluse_gate.py:239 does today, so a permission-denied stat ends in UnknownDetectorError or DetectorPackError, not a traceback.
  - spec citation: `None`
- **C38** [premise] [load-bearing]: The design leaves AdrHostConfig.runs_dir and ledger_path (plugins/arch-compliance/python/acf/adr/host.py:24-25) unchanged, consistent with the approved ADR gate contract's decision not to refuse absolute or '..' values there ('That is a visible host choice, not a state the gate must prevent', ADR_GATE_HOST_CONTRACT.md:295-301); no section of the spec validates, tests or documents those fields as refused.
  - spec citation: `docs/design/ADR_GATE_HOST_CONTRACT.md:295-301`
- **C39** [premise] [load-bearing]: Switching the ratchet to RepoTree.file for params.baseline and RepoTree.directory for each params.roots entry, with walked files keyed by RepoTree.key, refuses an entry that escapes the root (an absolute path outside it included), loops, or (for roots) names no existing directory, still accepts an absolute path inside the root as today, refuses no shipped or tested value (baseline config/architecture/fail_loud_ratchet.json, roots ['.'], RATCHET_BASELINE_REL, test_portable_guards.py:107 roots=['pkg'] after creating tmp_path/'pkg'), and raises DetectorPackError, which acf-check-diff already catches (cli_check_diff.py:72); the key-spelling changes it causes (a symlinked root, a root spelled in another case on a case-insensitive file system) are stated in spec §4.9.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:122-124`
- **C40** [premise] [load-bearing]: A host exception whose str() raises has a concrete producer: BaseException.__str__ returns str(args[0]) for a one-argument exception, and hm:scripts/ci/genre_conditional_guard.py:33-40 declares a non-frozen dataclass Finding whose __str__ calls self.line_text.strip(); a dataclass does not enforce its annotations, so ValueError(Finding('a.md', 3, None, '...')) raises AttributeError when formatted, the case _describe handles inside each handler.
  - spec citation: `hm:scripts/ci/genre_conditional_guard.py:33-40`
- **C41** [premise] [load-bearing]: In _call_host, items = list(raw) inside the try consumes a host iterator to completion, or lets its exception propagate, before _revalidate runs, so a generator the runner holds is never left suspended when _revalidate refuses an item, and any finally body of that generator runs inside the wrapped region.
  - spec citation: `None`
- **C42** [premise] [load-bearing]: test_unenforced_mandate_does_not_gate is the only existing test whose registry has no active ast/guard row, so it is the only existing test the empty-selection refusal reaches; an added active no-shims.hasattr row with call_sites [ci] does not fire on the staged bad.py (which contains no hasattr), so the test still exits 0 and still shows the unenforced row does not gate.
  - spec citation: `plugins/arch-compliance/tests/test_diff_cli.py:102-108`
- **C43** [premise] [load-bearing]: Replacing the hook's `abs_path = p.resolve() if p.is_absolute() else (repo / p).resolve()` (posttooluse_gate.py:203-204) with RepoTree(repo).file(raw), and deleting _scan_paths' is_file skip (:239) and try/except ValueError (:242-245), keeps every edited in-repo regular file the hook scans today under the same repo-relative key, for relative and absolute harness strings alike, and drops only edited files outside the repository; abs_path.relative_to(repo) then cannot fail because resolve_repo returns a resolved path (repo.py:41-44); no test in plugins/arch-compliance/tests/test_hooks.py exercises an out-of-repo path.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:203-204`
- **C44** [premise] [load-bearing]: Because a partial row gates like an enforced one (acf-mandate SKILL.md:57), the design's load refusals (unknown built-in detector, unknown llm prompt id, malformed host reference) reach partial rows; a host that followed :58's advice to prefer partial for a detector or prompt that does not exist yet is refused at load until it sets such rows to unenforced; no shipped or fixture registry in this repository has a partial row naming a detector or prompt that does not exist; and the spec lists this as an accepted consequence with an upgrade-note step (Decision 3, §4.8).
  - spec citation: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:57-58`
- **C45** [premise] [load-bearing]: An active row that is not a built-in ast/guard row (a host ast/guard row, or an llm, grep or manual row) whose id equals a built-in mandate id would receive that built-in scanner's findings, because scan_python_file and scan_typescript_file run on every changed file of their language (cli_check_diff.py:127, :153-156; posttooluse_gate.py:254, :279-282) and apply_registry routes each finding by mandate_id alone (enforcement.py:46); load_mandates with known_detectors refusing such a row (AcfInputError, spec §4.2 and Decision 3) refuses no shipped or fixture row (Appendix census).
  - spec citation: `plugins/arch-compliance/python/acf/enforcement.py:46`
- **C46** [premise] [load-bearing]: _to_findings refusing any host hit for which RepoTree(repo_root).contained(hit.path) is None refuses a validate_posix_rel_path-valid path that escapes the repository through an in-repo directory symlink, accepts a contained path whether or not the file exists (non-strict resolve), and is applied to every host finding in both runners (spec §4.4 items 5-7), so no host-supplied path outside the repository becomes a Finding.
  - spec citation: `None`
- **C47** [premise] [load-bearing]: Run over the tree at a338cad, the Decision 9 guard rules (docs/design/evidence/HOST_DETECTOR_EXTENSION_POINT/path_census.py) print exactly the sites in the committed output path_census_a338cad.txt and the Appendix row; they do not flag Path(__file__)-rooted resolves (posttooluse_gate.py:22-26) or joins with a constant (repo / MANDATES_REL); and once the sites the spec switches are migrated, the only remaining hits are the three allowlisted functions, so test_repo_tree_guard.py passes against the design as written.
  - spec citation: `docs/design/evidence/HOST_DETECTOR_EXTENSION_POINT/path_census.py`
- **C48** [premise] [load-bearing]: For every value a migrated site handles today that names an existing regular file or directory inside the repository, RepoTree gives the result the old code gave: the hook keeps its resolved-path key (posttooluse_gate.py:204, :243), the diff gate keeps git's spelling for its keys (cli_check_diff.py:118-122), citations classify the same, and the ratchet keys walked files as before except for the stated cases (a symlinked root; a root spelled in another case on a case-insensitive file system).
  - spec citation: `None`
- **C49** [root_cause] [load-bearing]: Root cause of the registry/gate disagreement: a status: partial row is live in both Tier-1 gates (enforcement.py:47 drops only 'unenforced'; the gates' row filters likewise), yet load_mandates never checks it, so a host can name a non-built-in detector in a partial ast/guard row today, load cleanly with known_detectors=KNOWN_DETECTORS, and have nothing ever execute it.
  - spec citation: `plugins/arch-compliance/python/acf/enforcement.py:47`
- **C50** [root_cause] [load-bearing]: Root cause of the hook defect: posttooluse_gate.py:107 calls load_mandates(mandates_path) without known_detectors, so an active row naming an unknown detector is never validated in the PostToolUse hook and produces zero findings at edit time instead of failing loud.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:107`
- **C51** [root_cause] [load-bearing]: Root cause of the exemption defect: the _line_lookup closures (cli_check_diff.py:76-80, posttooluse_gate.py:119-123) are token-identical and consult only file_lines, which holds changed .py/.ts/.tsx files (cli_check_diff.py:126, :152; posttooluse_gate.py:248-252), so a finding on any other file gets "" and apply_registry (enforcement.py:49-50) cannot see an inline exemption token on it.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80`
- **C52** [deletion] [load-bearing]: Deleting citations._looks_absolute (:49-51) and _escapes_repo (:74-76) is safe: their only references are the call sites at citations.py:161 and :163, no test imports them, resolve_citation keeps its order, and exactly two behaviours change, both stated in spec §4.1 and §4.9: a drive-relative string such as 'C:a/b.py' classifies external, and on Python 3.11 and 3.12 a symlink-loop citation classifies unresolved instead of raising RuntimeError.
  - spec citation: `plugins/arch-compliance/python/acf/adr/citations.py:74-76`
- **C53** [deletion] [load-bearing]: Deleting cli_check_diff._active_mandates and the hook's inline filters in favour of registry.active(call_sites, detector=...) changes no selection except by call_sites: for every shipped registry, the only built-in row that stops running at a gate is no-shims.hasattr leaving the PostToolUse hook (it declares [ci]).
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99`
- **C54** [deletion] [load-bearing]: Removing LLM_PROMPT_IDS from KNOWN_DETECTORS changes behaviour only for ast/guard rows naming an LLM prompt id: load_mandates consults known_detectors only for ast/guard rows (registry.py:60), and no code reads KNOWN_DETECTORS for llm rows. The import at cli_check_diff.py:21 stays and feeds load_mandates(..., llm_prompt_ids=LLM_PROMPT_IDS), so LLM_PROMPT_IDS keeps a runtime consumer.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:21`
- **C55** [deletion] [load-bearing]: Replacing the literal mandate ids in the five scanner modules with module constants changes no emitted finding, and no test asserts on the scanner source text in a way the change would break.
  - spec citation: `None`
- **C56** [deletion] [load-bearing]: Deleting the two _line_lookup closures (cli_check_diff.py:76-80, posttooluse_gate.py:119-123) for make_line_lookup(file_lines), which is their body unchanged and reads no file, changes no exemption result for any finding at a338cad. The only new lines in file_lines are those scan_host_guards adds for files a host guard flags, so a built-in finding on such a file becomes exemptable as built-in findings on changed code files already are; a built-in finding on any other file still gets ''.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80`
- **C57** [deletion] [load-bearing]: Deleting the five detector-id sets (PYTHON_AST_DETECTOR_IDS, GUARD_DETECTOR_IDS, CONFIG_AST_DETECTOR_IDS, ALL_PYTHON_DETECTOR_IDS, TS_DETECTOR_IDS) touches only the references git grep -n "_DETECTOR_IDS" -- plugins tests prints, each of which the spec rewrites, and leaves KNOWN_DETECTORS as the only set of built-in detector ids in plugins/arch-compliance/python.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/__init__.py:11-28`
- **C58** [deletion] [load-bearing]: Replacing the inline params extraction in both gates with facade_sink_args, fsm_guard_args and build_artifact_args (required arguments as str(params.get(key, '')); allowlist_globs and atomic_is_sink passed unchanged when the key is present, null included; path_prefixes only when present and non-empty) produces the same scanner call for every row as today, because the scanners' signature defaults (facade_sinks.py:24-25, build_artifacts.py:16, :23) equal what the gates pass today when the param is absent.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/facade_sinks.py:24-25`
- **C59** [deletion] [load-bearing]: Replacing the four parse-and-skip copies with acf.engine.parse_python changes no scanner output, and no other site in plugins/arch-compliance/python parses Python with a SyntaxError skip.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37`
- **C60** [deletion] [load-bearing]: Once each params.roots entry is resolved and contained with RepoTree.contained, every path rglob yields under it keeps the resolved root as a lexical prefix, so the walk filter's except ValueError: continue (fail_loud_ratchet.py:59-62) cannot fire and deleting that branch changes no count; scan_tree's callers are scan_ratchet and test_portable_guards.py:107.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:59-62`
- **C61** [deletion] [load-bearing]: Replacing count_bare_excepts' inline bare-or-Exception test (fail_loud_ratchet.py:31-34) with python_pack's predicate (python_pack.py:77-82, renamed is_bare_or_exception) changes no count, since the two tests accept exactly the same handlers; the predicate's only other caller is python_pack.py:61, no test references it by name, and the ratchet importing python_pack creates no import cycle.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:31-34`
- **C62** [mandate] [load-bearing]: ## Fail loud: every invalid state in spec §6.1 is refused by the named component with the named error, including: acf-check-diff without --call-site (usage error, exit 2) or with a site selecting no active ast/guard row (AcfInputError); a host module whose import or callable lookup raises any exception but KeyboardInterrupt (UnknownDetectorError); a host callable or its result raising any exception but KeyboardInterrupt, or yielding a non-exact-type or invalid HostHit (DetectorPackError); a host path whose stat raises OSError (typed error at each caller); a ratchet roots entry naming no existing directory (DetectorPackError); a TypeScript item with an unknown detector or differing mandate_id; an llm row with an unknown prompt id. Of the design's three broad handlers, the load and call handlers re-raise as typed errors; _describe's handler swallows only a failure to format the host's exception, returning a constant message inside the typed error still raised, and carries the fail-loud.bare-except-ok token with its reason, as ARCHITECTURE.md:29-30 permits for a handler 'explicitly exempted with a reason'.
  - spec citation: `None`
- **C63** [mandate] [load-bearing]: ## Fail loud: no active built-in ast/guard row can load with known_detectors yet never receive a finding from either Tier-1 gate: _check_builtin refuses a detector not in KNOWN_DETECTORS (LLM prompt ids are not keys), a row id that differs from the detector's stamped mandate_id, and any declared Tier-1 call site outside the detector's contract call_sites (fail_loud_ratchet: DIFF only); and Mandate._row_shape refuses an active ast/guard row with no Tier-1 site. Host rows are dispatched by both gates' host runners at any Tier-1 site.
  - spec citation: `None`
- **C64** [mandate]: ## Declared, never defaulted governs the ADR gate's host values in config/architecture/adr.yml and this design adds none of those; the spec states that it follows the same practice by choice for the values it adds (repo_root required for an active host row, apply_registry's call_sites keyword without a default, --call-site required) and does not claim the section requires it.
  - spec citation: `config/architecture/ARCHITECTURE.md:118-133`
- **C65** [mandate]: ## No shims: callable lookup is getattr(mod, attr, None) followed by callable() and a raise; no hasattr, and no host-detector failure has a silent fallback.
  - spec citation: `config/architecture/ARCHITECTURE.md:43-53`
- **C66** [mandate]: ## POSIX paths: HostHit.path is validated by validate_posix_rel_path (which refuses backslashes) and error messages use .as_posix().
  - spec citation: `config/architecture/ARCHITECTURE.md:55-64`
- **C67** [mandate]: ## One base exception: the design adds no exception class and uses AcfInputError, UnknownDetectorError and DetectorPackError (exceptions.py:5, :13, :29), all subclassing AcfError.
  - spec citation: `plugins/arch-compliance/python/acf/exceptions.py:5`
- **C68** [mandate]: ## One owner for host paths: acf/engine.py, acf/registry.py, acf/detectors/__init__.py and the new acf/detectors/host.py spell no config/architecture path, and the acf-mandate skill snippet takes MANDATES_REL and resolve_repo from acf.repo.
  - spec citation: `None`
- **C69** [mandate]: ## Prose names no host: the runtime messages in §4.2-§4.4 and the prose changes in §4.8 name no origin host.
  - spec citation: `config/architecture/ARCHITECTURE.md:135-143`
- **C70** [mandate]: ## Live consumers: each new export in §6.2 has the named non-test caller (RepoTree.file: load_mandates, load_host_detector, scan_host_guards, scan_ratchet, the hook's _collect_paths; parse_python: four scanners and scan_host_ast_file; the *_args functions: both gates; CallSite: Mandate.call_sites; DIFF_CALL_SITES: acf-check-diff's --call-site choices and KNOWN_DETECTORS), acf.judge.LLM_PROMPT_IDS keeps a runtime consumer, and the five deleted detector-id sets leave no dead export behind.
  - spec citation: `None`
- **C71** [mandate]: ## No completeness claims: every population claim in the spec carries a re-runnable recipe (§1, §3, Appendix) or is a per-item table, as ARCHITECTURE.md:159-169 requires.
  - spec citation: `config/architecture/ARCHITECTURE.md:159-169`
- **C72** [mandate]: ## Declared text decoding: the new read_text calls (cli_check_diff.py TypeScript branch, scan_host_guards' read of flagged files) declare encoding='utf-8'; errors='replace' in scan_host_guards is permitted by that rule, which governs the declared encoding; no subprocess is added.
  - spec citation: `None`
- **C73** [mandate]: ## Release discipline: because shipped skill prose changes, the version is bumped 0.2.2 -> 0.2.3 in both files ARCHITECTURE.md:186-187 names (pyproject.toml:3, plugins/arch-compliance/.claude-plugin/plugin.json:3).
  - spec citation: `config/architecture/ARCHITECTURE.md:184-194`
- **C74** [mandate]: ## Single point of definition: each existing definition listed in spec §4.9 is deleted and its callers switched (citations' path helpers, the five detector-id sets, the line-lookup closures, the active-row filters, the duplicated params extraction, the ratchet's joins, existence check and unreachable walk-filter branch, the four parse-and-skip copies, test_self_host's resolve-and-is_file), the scanners' signature defaults stay the one default for optional params, and the spec makes no claim that §4.9 lists every duplicate in the tree.
  - spec citation: `None`
- **C75** [mandate]: ## Scoped refactor: Decision 8 deletes the existing definitions §4.9 lists, each duplicated by a new definition in this design, in the code paths it changes, and makes no claim beyond that list; the two pre-existing dispatch loops stay (two call sites of one procedure), and the git-supplied join-and-is_file in _scan_changed (cli_check_diff.py:118-119) is a different job recorded as ADJACENT.
  - spec citation: `config/architecture/ARCHITECTURE.md:213-215`
- **C76** [mandate]: ## Frozen ledger format: the design changes no ledger model.
  - spec citation: `config/architecture/ARCHITECTURE.md:145-151`
- **C77** [mandate]: The design complies with the five portable governing principles at docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51 and fulfils that spec's call for project-specific detector extension points (:102, :123, :125).
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51`
- **C78** [mandate]: ## Fail loud: a host hit whose path resolves outside the repository is refused (DetectorPackError in _to_findings) rather than kept; scan_host_guards mapping a contained flagged path for which RepoTree.file returns None (missing, directory, a 3.13 symlink loop) to [] and decoding with errors='replace' hides no failure, because such a path has no line that could carry an exemption token, so the finding stays; an OSError from the stat or the read raises DetectorPackError inside each gate's scan try; and make_line_lookup does no I/O.
  - spec citation: `None`
- **C79** [mandate] [load-bearing]: ## Fail-loud ratchet: the design keeps the ratchet's whole-tree freeze unchanged, routes it to ci and precommit only through KNOWN_DETECTORS, refuses a baseline or roots entry outside the repository or a roots entry naming no directory (DetectorPackError), and §4.8 adds both constraints to the section's enablement instruction (ARCHITECTURE.md:72-73).
  - spec citation: `config/architecture/ARCHITECTURE.md:70-73`
- **C80** [mandate] [load-bearing]: ## One owner for host paths: acf.repo stays the one declaration of where ACF looks in a host and stays stdlib-only, and it also becomes the one owner of turning a path string into a repository location (RepoTree, Decision 9), enforced by test_repo_tree_guard.py over the same directories the section's existing test scans (plugins/arch-compliance/python/ and hooks/); §4.8 adds this to the section.
  - spec citation: `config/architecture/ARCHITECTURE.md:105-116`
- **C81** [shape_fit] [load-bearing]: Mandate.runs_at and MandateRegistry.active become the single definition of 'this row runs at this gate' for the Tier-1 gates; after the change no other Tier-1 site (cli_check_diff, posttooluse_gate, enforcement, the host runners) keeps its own active-row filter.
  - spec citation: `None`
- **C82** [shape_fit] [load-bearing]: After the design, turning a path string into a location in the host repository has one owner, acf.repo.RepoTree, used by load_mandates, load_host_detector, _to_findings, scan_host_guards, scan_ratchet and scan_tree, _scan_changed, the hook's _collect_paths and _scan_paths, citations.py and tests/test_self_host.py:40; no runtime site in plugins/arch-compliance/python or hooks outside acf/repo.py joins the root with a non-constant, resolves a repository path or tests containment, apart from the three allowlisted functions (cli_check_diff.main, cli_check_llm.main, scan_typescript_file) whose stated reasons hold; validate_posix_rel_path checks only a string's shape; parse_python is the one parse-or-skip.
  - spec citation: `None`
- **C83** [shape_fit] [load-bearing]: validate_hit_fields SUBSUMES the TypeScript bridge's int(item['line']) / str(item['message']) coercion (typescript_bridge.py:88-89) and HostHit's former field constraints: both Tier-1 hit sources check line and message with the one function, and what stays separate is genuinely different (the bridge's absolute path, which each gate replaces at cli_check_diff.py:154 and posttooluse_gate.py:280, and its Node severity, which apply_registry overwrites; a host hit's validated relative path and row-derived id and severity).
  - spec citation: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:88-89`
- **C84** [shape_fit] [load-bearing]: Building Finding from a HostHit is ADJACENT to the judge's _to_finding (judge.py:238-255): the judge demotes severity by confidence and admits path="<diff>" and line=0, while host findings take severity from the row and require a relative path and line >= 1, so no shared constructor is warranted.
  - spec citation: `plugins/arch-compliance/python/acf/judge.py:236-253`
- **C85** [shape_fit] [load-bearing]: acf/detectors/host.py partially duplicates no existing mechanism: nothing in the plugin today loads or executes code from a registry-supplied file path, and the loader's one-time append of a host root to the end of sys.path is ADJACENT to the hooks' own start-up insertion of the plugin's python/ directory (posttooluse_gate.py:22-26, inject_constraints.py:28-29).
  - spec citation: `None`
- **C86** [shape_fit] [load-bearing]: make_line_lookup consolidates the only two line-lookup closures passed to apply_registry; no third LineLookup implementation exists (e.g. in cli_check_llm.py, the judge, or any skill snippet) that would remain a second definition.
  - spec citation: `None`
- **C87** [shape_fit] [load-bearing]: Detector-reference validation lives in two cooperating places only, Mandate._row_shape (row-local rules, every caller) and load_mandates with known_detectors (built-in contracts and host-file existence); no other validator (the acf-mandate skill's ## Validate snippet, test_profile_drift.py, the architecture-review skill, acf-setup) independently checks detector ids or call sites in a way that would diverge.
  - spec citation: `None`
- **C88** [shape_fit] [load-bearing]: The §4.7 contract-against-dispatch test ties KNOWN_DETECTORS' call_sites to the gates' dispatch: a detector the table says runs at a gate but which that gate does not dispatch fails the test; the opposite drift cannot attach a finding to any loaded row, because _check_builtin refuses a row declaring that site and apply_registry drops a finding whose row does not run at the gate, so it over-refuses and never silently drops a row.
  - spec citation: `None`
- **C89** [shape_fit] [load-bearing]: RepoTree SUBSUMES the PostToolUse hook's Path.is_absolute() join with its relative_to/except ValueError containment test (posttooluse_gate.py:203-204, :242-245) and the ratchet walk filter's except ValueError and relative_to conversion (fail_loud_ratchet.py:59-62): each decides by hand whether a path lies in the root; the spec deletes those branches, both sites convert a contained Path to its key with RepoTree.key and keep no relative_to call of their own, and §4.1, §4.6, §4.9 and §5.2 state this consistently.
  - spec citation: `None`
- **C90** [shape_fit] [load-bearing]: The spec's account of where host code runs is consistent: Decision 7 guarantees that every failure raised while a runner calls host code (module execution, callable lookup, the call, consuming and rebuilding its result, formatting its exception) becomes a typed ACF error, and states that the wrapping does not confine host code (atexit handlers, threads); no other section claims that host code runs only inside the wrapped regions; and the fresh_host_loader fixture is the single reset of loader state.
  - spec citation: `None`
- **C91** [shape_fit] [load-bearing]: TS_MANDATE_IDS is the single definition of the TypeScript mandate ids: the bridge stamps from it, KNOWN_DETECTORS reads it, the Node rules no longer emit a mandate_id literal (the spec deletes emptyCatch.ts:23, explicitAny.ts:15 and the Finding type's field at emptyCatch.ts:4), and no other non-test Python site spells 'fail-loud.empty-catch' or 'no-shims.explicit-any' as a runtime value.
  - spec citation: `None`
- **C92** [shape_fit]: apply_registry is the single owner of Finding.severity on the Tier-1 path (enforcement.py:52); the host runner's severity value is a required-field fill that apply_registry overwrites, as §4.4 item 5 and §5.2 state.
  - spec citation: `None`
- **C93** [shape_fit] [load-bearing]: The diff gate's join-and-is_file in _scan_changed (cli_check_diff.py:118-119) is SUBSUMED by RepoTree.file: the gate asks the façade which changed paths are files inside the repository and which file to read, so it agrees with the hook on containment and symlinks, skips a tracked symlink whose target leaves the repository, and hands host guards only the accepted paths; its finding keys stay the git spelling, which the build-artifact guard and added_lines also use.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:118-119`
- **C94** [shape_fit]: The not-found refusals of RepoTree.file's callers (load_mandates, load_host_detector, scan_ratchet) are ADJACENT to acf.loader.require_file (loader.py:24-28): require_file takes an already-built Path for an operator input file and always raises AcfInputError, while these callers first decide containment of a registry-supplied string and raise their phase's error (UnknownDetectorError at load, DetectorPackError in the ratchet).
  - spec citation: `plugins/arch-compliance/python/acf/loader.py:24-28`
- **C95** [shape_fit]: load_baseline beside load_model_file is ADJACENT by an approved decision (ADR_GATE_HOST_CONTRACT.md:292-294 records it as a pre-existing second loader outside this phase), and the design changes only how the baseline path is resolved and contained; scan_host_guards' errors='replace' line read is ADJACENT to the gates' strict reads of the code files they parse, because its lines serve only the exemption-token lookup and a guard may flag a binary or a document.
  - spec citation: `docs/design/ADR_GATE_HOST_CONTRACT.md:292-294`
- **C96** [shape_fit] [load-bearing]: The loader keeps one record of loaded host modules, sys.modules under a name that is a pure function of rel_path; no second cache keyed by rel_path exists in the design, and the fresh_host_loader fixture resets the loader's state by resetting _ACTIVE_ROOT and removing the _acf_host_ entries a test added.
  - spec citation: `None`
- **C97** [sweep] [load-bearing]: Sweep: the call-site vocabulary in use across shipped registries, tests and the origin host is within CallSite {ci, precommit, hook, posttooluse, audit}; after each ast/guard row declaring ci also declares precommit, every active ast/guard row routes to at least one Tier-1 site at which its detector runs, and audit stays read by no Tier-1 gate.
  - spec citation: `None`
- **C98** [sweep] [load-bearing]: Sweep: the test changes in spec §4.7 cover every existing test the design breaks or makes stale, including test_unenforced_mandate_does_not_gate (test_diff_cli.py:102-108, which gains an active no-shims.hasattr row so the empty-selection refusal does not fire), the ten main([...]) calls in test_diff_cli.py (now passing --call-site), the ten apply_registry calls in test_enforcement.py, test_hooks.py:199-218, test_registry.py:30, test_typescript_pack.py:6 and :14, tests/test_self_host.py:23, :40 and :5, test_acf_mandate_skill.py:2 and test_portable_guards.py.
  - spec citation: `None`
- **C99** [sweep]: The §4.7/§4.8 sites cover every shipped doc, skill, docstring, config and test the design makes stale, including each command line or instruction that runs acf-check-diff whether or not it names the tool: the sites the §4.8 recipe prints (.github/workflows/ci.yml:40, README.md:57-58, acf-setup SKILL.md:24, :184, :193, :206, :207, :217, :219, :250 and its success criteria, acf-mandate SKILL.md:131, CLAUDE.md:36, docs/guides/SUPERPOWERS_COMPLEMENT.md:82-83, PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:454), plus the instructions that run the gate without a command line (acf-setup SKILL.md:228, SUPERPOWERS_COMPLEMENT.md:70-71, README.md:112); the upgrade note for previously installed hosts; KNOWN_DETECTORS described as a union; the hook's call-site behaviour; apply_registry's drop rules; and the deleted detector-id sets.
  - spec citation: `None`
- **C100** [sweep]: The §4.8 rows cover the prose this revision makes stale: ARCHITECTURE.md ## Fail-loud ratchet enablement text (:72-73), ARCHITECTURE.md:226-228 naming acf.cli_check_diff.KNOWN_DETECTORS, the acf-mandate SKILL.md:58 partial-row advice and the upgrade note for partial rows, and docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:161 (PostToolUse scans in-repo paths only).
  - spec citation: `None`
- **C101** [mechanism_justification] [load-bearing]: Deferring host import to dispatch (load_mandates checks reference syntax, Tier-1 site, languages, built-in contracts and host-file existence, and imports nothing) is justified: a missing file still fails at load, an import failure or missing callable fails loud at dispatch as UnknownDetectorError caught by both gates' except tuples, and importing at load would run host code in the SubagentStart hook and acf-check-llm and import CI-only guards on every edit.
  - spec citation: `None`
- **C102** [mechanism_justification] [load-bearing]: The row-shape checks on Mandate (host-reference syntax, a Tier-1 site, host ast languages) together with the per-detector BuiltinDetector contracts (known id, matching mandate_id, declared Tier-1 sites within the contract's call_sites) are sufficient to prevent an active ast/guard row that loads with known_detectors yet is run by neither acf-check-diff (DIFF_CALL_SITES) nor the hook (HOOK_CALL_SITES), or whose findings land on no row.
  - spec citation: `None`
- **C103** [mechanism_justification] [load-bearing]: Refusing a second host root in one process (AcfInputError) rather than evicting the old root is justified: every production caller resolves one repository per process, so the refusal never fires in production, and the only multi-root producer (in-process tests) is handled by the test-only fresh_host_loader fixture; no repair mechanism lives in production code.
  - spec citation: `None`
- **C104** [mechanism_justification] [load-bearing]: Declaring, per built-in detector, the mandate id it reports to and the call sites where a gate runs it (BuiltinDetector in KNOWN_DETECTORS) is justified over the alternatives: the scanners stamp fixed mandate ids and run at fixed gates, so the contract records an existing fact rather than adding a capability; the accepted cost (at most one active row per built-in detector) affects no shipped registry.
  - spec citation: `None`
- **C105** [mechanism_justification] [load-bearing]: Moving the row-local rules onto a Mandate model_validator (rather than keeping them in load_mandates) is justified because it makes the SubagentStart hook, acf-check-llm and any direct Mandate construction reject the same malformed rows as the gates; inject_constraints.py catches AcfInputError around load_mandates, and acf-check-llm (cli_check_llm.py:54) leaves it uncaught, so a malformed row there already ends non-zero and the new refusals reach it the same way (spec §3 In scope table).
  - spec citation: `None`
- **C106** [mechanism_justification]: Parsing a Python file once and sharing the tree across every host ast detector on it is justified by avoiding N parses per file; built-in scanners keep their own parses unchanged.
  - spec citation: `None`
- **C107** [mechanism_justification] [load-bearing]: Having host callables return HostHit (path, line, message) and building Finding in the runner from the mandate row, rather than accepting Finding and overwriting fields, is justified because apply_registry matches findings to rows by mandate_id (enforcement.py:37-53) and a host-supplied mandate_id/detector/severity could otherwise attach a finding to the wrong row.
  - spec citation: `None`
- **C108** [mechanism_justification] [load-bearing]: Treating the host's own pre-commit/CI invocation of acf-check-diff as its opt-in to running host code, and gating only the automatic hooks on .acf/enabled, is justified because .acf/ is gitignored and CI would otherwise be disabled; a user who runs acf-check-diff manually in an untrusted checkout is the residual case the design accepts.
  - spec citation: `.gitignore:8`
- **C109** [mechanism_justification] [load-bearing]: The call_sites filter added to apply_registry is needed in addition to the scanners' registry.active(call_sites) selection, because some built-in scanners emit findings by detector id without consulting the registry's call_sites, so without the filter a finding for a row not declared at this gate would survive. (The spec states the filter but gives no reason it is not redundant.)
  - spec citation: `None`
- **C110** [mechanism_justification] [load-bearing]: Appending the host root to the end of sys.path rather than inserting it at the front is justified: it adds no shadowing of standard-library, third-party or plugin modules under the hook and console-script entry points, keeps host intra-repo absolute imports working from the host root, and its stated cost (a host top-level name an earlier entry provides resolves to that entry) fails at import or callable lookup as UnknownDetectorError in the common case; dropping the acf/ refusal removes a check with no producer.
  - spec citation: `None`
- **C111** [mechanism_justification] [load-bearing]: Reading flagged files in scan_host_guards, inside each gate's scan try, instead of lazily in the line lookup is justified: it keeps apply_registry free of I/O and new errors, converts an unreadable file to DetectorPackError where both gates already report it, and limits new exemption lines to files a host guard flagged.
  - spec citation: `None`
- **C112** [mechanism_justification]: Enforcing llm prompt ids at load (llm_prompt_ids, passed by acf-check-diff) is justified: it gives acf.judge.LLM_PROMPT_IDS a runtime consumer after it leaves KNOWN_DETECTORS, makes the acf-mandate skill's stated rule true, and refuses no shipped row; registry.py cannot import acf.judge, so the ids are passed in rather than imported.
  - spec citation: `None`
- **C113** [mechanism_justification] [load-bearing]: A required --call-site argument on acf-check-diff, rather than a default or a site derived from --mode/--base, is justified: the origin host's per-site row selection (hm:scripts/ci/run_guards.py:116), the fact that a missing value then fails loud (usage error) instead of silently running the wrong rows, and the practice of declaring rather than defaulting, which the spec applies by choice (the ## Declared, never defaulted section governs only the ADR gate's host values); the cost, adding the flag at each existing invocation, is listed per site.
  - spec citation: `None`
- **C114** [mechanism_justification] [load-bearing]: Refusing a --call-site that selects no active ast/guard row (AcfInputError), and adding precommit to every shipped row that declares ci, are justified together: without them the documented pre-commit invocation would run no row and report clean, the false green the origin host's runner already refuses (hm:scripts/ci/run_guards.py:126-130).
  - spec citation: `None`
- **C115** [mechanism_justification] [load-bearing]: Rebuilding each yielded item inside _call_host (exact type, exact field types, then validation) is justified over checking the type in _to_findings: field access and comparisons on an unvalidated host object can run host code, so they must happen inside the wrapped region, and a rebuilt HostHit holds only plain str and int values.
  - spec citation: `None`
- **C116** [mechanism_justification]: Decision 8 (delete the existing definitions §4.9 lists and switch their callers) is justified over recording them as debt: it removes code, removes completeness claims about remaining breaches, and each switch's behaviour change is checked against every shipped value (spec §4.9, Appendix); where an approved spec chose otherwise (AdrHostConfig's path fields, ADR_GATE_HOST_CONTRACT.md:295-301), the design keeps that decision.
  - spec citation: `None`
- **C117** [mechanism_justification] [load-bearing]: _describe (format the host exception inside its own try, fall back to a constant message for any exception but KeyboardInterrupt) is justified by a named producer: an exception carrying an origin-host object whose __str__ raises (hm:scripts/ci/genre_conditional_guard.py:33-40); without it, formatting the typed error's message would raise outside the wrapped region and end in a traceback.
  - spec citation: `None`
- **C118** [mechanism_justification] [load-bearing]: A repository-path façade with a guard test (Decision 9) is justified over shared helper functions: helpers leave each caller holding the root and a raw string, so nothing stops a new site from joining or resolving by hand and the 'one implementation' claim rests on an enumeration of callers; the façade plus an AST guard makes a second owner fail a test, follows the origin host's persistence-façade pattern (hm:GEMINI.md:131), and its blind spots and three allowlisted functions are stated.
  - spec citation: `None`
- **C119** [implementability] [load-bearing]: Mandate (registry.py:14-27) is a Pydantic BaseModel exposing every field the design reads: id, severity, status, detection, detector, call_sites (list[str]), languages (Literal including 'none'), and params (dict or None); adding an @property is_active and a plain method runs_at to it, and a method active to MandateRegistry, is compatible with its model_config.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:14-27`
- **C120** [implementability] [load-bearing]: Finding (acf/finding.py) can be constructed as Finding(mandate_id=, severity=Severity(mandate.severity), path=, line=, message=, detector=, detection=): those are its fields, Severity is constructible from Mandate.severity's value, and no other required field is missing.
  - spec citation: `None`
- **C121** [implementability] [load-bearing]: apply_registry (enforcement.py) looks up each finding's row via registry.by_id, drops it on the status check at :47 (replaceable by runs_at), and handles exemptions and severity at :49-52 using a LineLookup type that make_line_lookup can return.
  - spec citation: `plugins/arch-compliance/python/acf/enforcement.py:47`
- **C122** [implementability] [load-bearing]: cli_check_diff.py has the hook points the design names with the needed names in scope: load at :70 inside a try whose except tuple at :72 lists AcfInputError, UnknownDetectorError and DetectorPackError (and wraps both load and scan); lookup and apply_registry at :76-82; in the .py branch after scan_fsm_writes (:140-150) repo, text, posix, lines and registry; in the .ts/.tsx branch (:151-156) a read that can bind text; and after the ratchet loop (:168-182) the changed-file list.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:72`
- **C123** [implementability] [load-bearing]: posttooluse_gate.py has the hook points the design names: deferred imports at :91-104, the load try at :106-110, the scan try at :113-117 (whose except can be widened to AcfInputError, DetectorPackError, UnknownDetectorError), lookup/apply_registry at :119-125, _collect_paths' resolve-and-dedupe loop at :200-209 where RepoTree.file replaces the join, the is_file skip at :239 and the relative_to/ValueError fallback at :242-245 that are deleted, inline filters at :229-236 and :284-286, the build-artifact loop at :284-294, and text and rel in scope in the .py and TypeScript branches of _scan_paths.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:113-117`
- **C124** [implementability] [load-bearing]: Host-detector failures reach an existing fail-loud handler in both gates, never a traceback: load_host_detector raises UnknownDetectorError for any exception but KeyboardInterrupt during import or lookup and for a stat OSError, AcfInputError for a second root; _call_host raises DetectorPackError for any exception but KeyboardInterrupt from the call, from consuming the result and from rebuilding each item; scan_host_guards raises DetectorPackError for a stat or read OSError; apply_registry does no I/O; cli_check_diff.py:72 and the hook's widened scan except catch all three error types.
  - spec citation: `None`
- **C125** [implementability] [load-bearing]: load_host_detector is implementable as stated: a module-level _ACTIVE_ROOT, sys.modules under a name derived from rel_path as the one record of a loaded module, a one-time sys.path.append of the root, RepoTree.file for the module path, spec_from_file_location with a None spec or loader refused inside the wrapped region, registering in sys.modules before exec_module and removing the entry when this call registered it and the load or lookup raises, and exec plus getattr in one try; the fresh_host_loader fixture, which resets _ACTIVE_ROOT and deletes the _acf_host_ sys.modules keys a test added, isolates in-process tests over several roots, including test_diff_cli.py's in-process main() calls.
  - spec citation: `None`
- **C126** [implementability] [load-bearing]: Registering the module in sys.modules under its name before spec.loader.exec_module(mod) is what lets a host module define a @dataclass under `from __future__ import annotations` (dataclasses resolves sys.modules[cls.__module__]); importlib.util.spec_from_file_location with a synthetic name supports this.
  - spec citation: `None`
- **C127** [implementability] [load-bearing]: The imports the design adds are cycle-free and allowed: acf.registry imports acf.engine and acf.repo (both stdlib-only), dataclass and Mapping, and nothing from acf.detectors; acf.detectors/__init__ imports acf.registry and the scanner modules' constants without a cycle; acf.cli_check_diff re-exports KNOWN_DETECTORS from acf.detectors; acf.detectors.host imports registry, repo, finding, engine and exceptions; acf/adr/citations.py importing acf.engine and acf.repo is permitted by test_adr_import_graph.py (acf.adr already imports acf.repo at adr/host.py:16); and the hook's new deferred imports (from acf.detectors, not acf.cli_check_diff) do not reach acf.adr or acf.judge.
  - spec citation: `plugins/arch-compliance/tests/test_adr_import_graph.py:70-76`
- **C128** [implementability] [load-bearing]: load_mandates today loads rows via load_model_file(path, Mandate, subject='mandates file', fmt='yaml', many=True) returning a list of Mandate, and builds MandateRegistry(mandates=..., source_path=path.as_posix()), so the §4.2 body is a drop-in extension of the existing function.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:48-64`
- **C129** [implementability]: plugins/arch-compliance/tests/test_repo_paths.py:47-48 pins the text of posttooluse_gate.py's docstring line :11 and not :12, so rewording :12 and keeping :11 verbatim breaks no test.
  - spec citation: `plugins/arch-compliance/tests/test_repo_paths.py:47-48`
- **C130** [implementability]: config/architecture/mandates.yml:60 declares fail-loud.bare-except-ok for fail-loud.bare-except; the design's handlers are `except BaseException` handlers, which _is_bare_or_exception (python_pack.py:78-82) does not flag because it matches only a bare handler or the name Exception, so they pass the gate whether or not they carry the token, and spec §6 says so.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/python_pack.py:78-82`
- **C131** [implementability]: acf/engine.py already defines contains_backslash and imports only pathlib, so adding looks_absolute, validate_posix_rel_path, validate_hit_fields and parse_python with `import ast` and `import re` keeps it stdlib-only; acf/repo.py imports only the standard library (repo.py:1-6), so adding RepoTree there keeps it importable by both hooks at module scope before the .acf/enabled check.
  - spec citation: `plugins/arch-compliance/python/acf/engine.py`
- **C132** [implementability] [load-bearing]: The new tests are implementable against the shipped files: test_builtin_detectors.py can parse the README.md detector table (:66-74) for detector ids and mandate ids and read mandate_id values from emptyCatch.ts:23 and explicitAny.ts:15; and the test_registry.py cases (a fail_loud_ratchet row declaring hook, a fail_loud_bare_except row with another id, an ast row naming an LLM prompt id, a module that raises at import not imported by load_mandates) can be expressed as inline YAML registries like the existing :24 and :35 rows.
  - spec citation: `None`
- **C133** [implementability] [load-bearing]: The contract-against-dispatch test is implementable: acf-check-diff runs in process on a temporary git repository once with --call-site ci and once with --call-site precommit, and the hook in a subprocess with .acf/enabled; a fixture tree can trigger each built-in detector the table assigns to that gate, with one active row per such detector declaring only that gate's sites.
  - spec citation: `None`
- **C134** [implementability] [load-bearing]: scan_host_guards(repo_root, changed_files, registry, file_lines, *, call_sites) is implementable in both gates: file_lines is in scope after each gate's dispatch (cli_check_diff _scan_changed returns it; _scan_paths builds it), the call can run inside _scan_changed and _scan_paths so it sits under each gate's scan try, and filling only missing keys keeps the gate's own reads.
  - spec citation: `None`
- **C135** [implementability] [load-bearing]: The required --call-site argument is implementable at cli_check_diff.py:29-71: argparse required=True with choices=sorted(DIFF_CALL_SITES) exits 2 on a missing or unknown value (SystemExit in process, so test_diff_cli asserts it with pytest.raises), sites = frozenset({args.call_site}) reaches _scan_changed and apply_registry, and the empty-selection refusal can raise AcfInputError inside the existing try at :69-74.
  - spec citation: `None`
