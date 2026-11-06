# Adversarial design review — full detail

Spec: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md` @ `34337fed4cd62e5a8f3635e3f0a498057869ddd0`
Kinds: defect, feature
Outcome: **BLOCKED**
Claims: 89 · Reviewers: 4 · Converged: 2

## Blocking reasons

- load-bearing claim C19 (premise) is UNPROVEN: The factual half holds. The diff gate passes added lines and iterates git changed_files (ACMR). The hook passes None, takes paths from argv/stdin, filters by _CODE_SUFFIXES, and keeps out-of-repo absolute paths. The doctrinal half does not follow from the cited text. :211-215 says to remove non-contractual patterns 'in code paths you are changing' and not to expand to unrelated modules. Both dispatchers are code paths this design changes, so the rule does not plainly license adding the same three host calls to each. ## Single point of definition (:196-209) cuts the other way for a decision procedure needed by more than one module. I could not establish that the deferral is sanctioned by the rule it cites.
- load-bearing claim C54 (shape_fit) is REFUTED: The SUBSUMED half holds: citations.py:49-51 and :74-76 are the only string-level absolute and escape tests, and _WIN_DRIVE_RE (contract.py:95) really is ADJACENT. The claim fails where it waves fail_loud_ratchet.py:123 off as 'resolves paths for I/O, a different responsibility'. scan_ratchet takes params.baseline, a relative path string supplied by the registry, tests it with Path.is_absolute(), and joins it under repo_root with no containment check (:122-124). scan_tree likewise joins params.roots under root unchecked (:46). load_mandates' host-file check does the same job: it turns a registry-supplied relative string into an existing file under the host root, which is also an I/O check. After the design that job has two implementations. One uses looks_absolute and resolve_under_root (contained, platform-independent). The other uses Path.is_absolute and a bare join (uncontained, and on Windows it reads '/x' as relative). A search by behaviour (who joins registry params under the root?) finds the ratchet; the claim's search by helper name misses it.
- load-bearing claim C63 (shape_fit) is REFUTED: KNOWN_DETECTORS[...].call_sites declares where each built-in detector runs. The fact itself is decided by the gates' dispatch code: fail_loud_ratchet runs only because cli_check_diff.py:168-182 loops over it and _scan_paths has no such loop. After the design that is two owners of 'detector X runs at gate Y', the declared map and the hand-written dispatch. Nothing pins them together: test_builtin_detectors.py pins the map's values, not the gates' behaviour. Adding a ratchet call to the hook, or a new built-in to one gate only, would leave load_mandates accepting or refusing call sites wrongly, with no test failing. Smaller point: python_pack's detector-id literals (:72, :102, :152, :180) stay separate spellings from PYTHON_AST_DETECTOR_IDS (:16) and the map keys; §4.3 makes constants of mandate ids only.
- load-bearing claim C65 (shape_fit) is UNPROVEN: _ACTIVE_ROOT, _call_host and the conftest do not exist yet (Glob finds no conftest.py anywhere), so I have no site that corroborates the claim. As designed, host code also runs in a second wrapped region: exec_module in load_host_detector, which re-raises UnknownDetectorError rather than DetectorPackError. 'Single wrapped region' therefore holds only if module top-level code does not count as invoking a host callable. The nearest existing pattern, typescript_bridge.py:57-58 and :94-95 wrapping detector-pack failures as DetectorPackError, is ADJACENT.
- load-bearing claim C81 (implementability) is REFUTED: The universal 'never a traceback' does not hold for the design as written. (1) §4.4 item 3 places `fn = getattr(mod, attr, None)` after the exec_module handler and outside it. getattr with a default swallows only AttributeError, so a host module-level __getattr__ that raises anything else, a host-detector failure, escapes load_host_detector as a raw exception. Neither cli_check_diff.py:72 nor the widened hook except at :113 lists it, and the user gets a traceback. (2) make_line_lookup is called inside apply_registry, and both gates call apply_registry outside any try (cli_check_diff.py:82, posttooluse_gate.py:125). §4.5 says an OSError from read_text propagates, so a host guard hit naming an unreadable file also ends in a traceback. The _call_host wrapping itself (materialising inside the try, SystemExit included) is sound.
- mandate claim C48 is REFUTED: Doctrine (:198-200): a constant set needed by more than one module must have 'exactly one canonical implementation that every call site consumes'. The claim says each built-in mandate id is defined once, in a scanner-module constant 'read by both the scanner and KNOWN_DETECTORS'. That is false for the two TypeScript ids. The Node rules hard-code 'fail-loud.empty-catch' and 'no-shims.explicit-any'. The Python bridge copies item['mandate_id'] from the Node JSON and never reads TS_MANDATE_IDS. The design adds a second, Python-side definition (TS_MANDATE_IDS) that KNOWN_DETECTORS reads and no scanner reads. The two are tied only by a test that compares the strings. So the design introduces a new two-definition breach of the rule it claims to satisfy. A single point is available inside this design's scope, e.g. the bridge stamps mandate_id from TS_MANDATE_IDS[item['detector']] and refuses a Node value that disagrees. The other parts of the claim hold: the Python ids, runs_at, host loading and make_line_lookup.
- implementability claim C81 is REFUTED: The universal 'never a traceback' does not hold for the design as written. (1) §4.4 item 3 places `fn = getattr(mod, attr, None)` after the exec_module handler and outside it. getattr with a default swallows only AttributeError, so a host module-level __getattr__ that raises anything else, a host-detector failure, escapes load_host_detector as a raw exception. Neither cli_check_diff.py:72 nor the widened hook except at :113 lists it, and the user gets a traceback. (2) make_line_lookup is called inside apply_registry, and both gates call apply_registry outside any try (cli_check_diff.py:82, posttooluse_gate.py:125). §4.5 says an OSError from read_text propagates, so a host guard hit naming an unreadable file also ends in a traceback. The _call_host wrapping itself (materialising inside the try, SystemExit included) is sound.
- mechanism 'Refuse a host root containing acf/ or acf.py' has no named producer for the state it handles (an `acf.*` import by the plugin resolves to a module under the host root instead of plugins/arch-compliance/python/acf) — superstition

## Absorptions

- PARTIAL_OVERLAP: 'KNOWN_DETECTORS[...].call_sites (BuiltinDetector)' shares responsibility 'decide at which Tier-1 gate a built-in detector runs' with plugins/arch-compliance/python/acf/cli_check_diff.py:168-182 — R = 'detector X runs at gate Y'. Either have each gate's dispatch iterate over KNOWN_DETECTORS entries whose call_sites intersect its own set, so the map drives dispatch, or add a test that runs each gate against a registry holding every built-in row and asserts that the detectors which ran equal the map's call_sites. Either way the hand-written per-gate dispatch lists collapse into the map.
- PARTIAL_OVERLAP: 'acf.engine.resolve_under_root / looks_absolute' shares responsibility 'resolve a registry-supplied relative path string to a file under the host root' with plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:122-124 — R = joining a registry path param under the root. The ratchet's params.baseline and params.roots joins (:46, :122-124) become resolve_under_root consumers, with looks_absolute replacing Path.is_absolute, or the spec records them as named debt under Single point of definition.
- SUBSUMED: 'acf.engine.resolve_under_root / looks_absolute' shares responsibility 'string-level absolute and escape test' with plugins/arch-compliance/python/acf/adr/citations.py:49-51 — citations' _looks_absolute and _escapes_repo are deleted and call the engine helpers, as the spec states.
- IDENTICAL: '_to_findings (host runner)' shares responsibility 'assign Finding.severity from the registry row' with plugins/arch-compliance/python/acf/enforcement.py:52 — Leave severity assignment to apply_registry, the one sink every Tier-1 finding passes through. The host runner can set any placeholder, or the row severity only because Finding requires a value, and state that.
- IDENTICAL: 'make_line_lookup' shares responsibility 'look up the source line for exemption checks' with plugins/arch-compliance/python/acf/cli_check_diff.py:76-80 — Both closures (cli_check_diff.py:76-80 and posttooluse_gate.py:119-123) are deleted, as the spec states.
- PARTIAL_OVERLAP: 'scan_host_ast_file parse-or-skip' shares responsibility 'parse Python and skip on SyntaxError' with plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37 — A shared parse_or_none helper in acf.engine that the four scanners and the host runner consume. The spec defers it explicitly under Scoped refactor.
- mechanism 'Refuse a host root containing acf/ or acf.py' sits at rung 3 when rung 1 applies, with no written justification
- mechanism '_to_findings refusal of non-HostHit items and mismatched ast paths' sits at rung 3 when rung 1 applies, with no written justification

## Converged findings

- [2 reviewers: refuter, hardening] make_line_lookup lets an OSError from read_text propagate, and both gates call apply_registry outside any try (cli_check_diff.py:82, posttooluse_gate.py:125), so an unreadable path flagged by a host guard ends in a traceback rather than a typed acf error.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:82`
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:125`
- [2 reviewers: refuter, hardening] The loader's shadowing guard is misdirected: inserting the host root at sys.path[0] and refusing only a top-level acf/ or acf.py does not match the real risk (acf is already imported as a regular package before dispatch, while any other top-level host module can shadow a not-yet-imported module).
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:22-28`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:58, plugins/arch-compliance/python/acf/registry.py:60, plugins/arch-compliance/tests/test_registry.py:20-30`
- reasoning: I opened load_mandates. Line 58 skips any row whose status is not 'enforced'. Lines 60-63 raise UnknownDetectorError only for a detection in {ast, guard} whose detector is not in known_detectors. test_registry.py:20-30 pins the enforced-unknown case.

#### C2 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:47, plugins/arch-compliance/python/acf/cli_check_diff.py:98, plugins/arch-compliance/hooks/posttooluse_gate.py:231, plugins/arch-compliance/python/acf/registry.py:58`
- reasoning: apply_registry drops only rows with status == 'unenforced'. The diff gate's _active_mandates and the hook's inline filters also exclude only 'unenforced', so a partial row is live in both gates. load_mandates skips every non-enforced row (registry.py:58), so a partial ast/guard row with a non-built-in detector loads cleanly. Neither gate has a dispatch path for that detector (see C4).

#### C3 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:25, plugins/arch-compliance/python/acf/judge.py:29, plugins/arch-compliance/python/acf/registry.py:60`
- reasoning: KNOWN_DETECTORS is the frozenset union at :25. git grep 'KNOWN_DETECTORS' -- plugins tests shows only imports, load_mandates arguments and prose, so nothing extends it. I imported it: 13 ids, including the four llm_* ids. registry.py:60 checks only membership, so an ast row naming llm_fail_loud passes. No scanner in _scan_changed or _scan_paths dispatches on an llm id.

#### C4 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:112-182, plugins/arch-compliance/hooks/posttooluse_gate.py:229-294`
- reasoning: Both scan functions call only the imported built-in scanners: python_pack, facade_sinks, fsm_guard, the TypeScript bridge, build_artifacts, and the ratchet (diff gate only). Config-driven scanners are selected by exact built-in id constants. The grep for importlib|import_module|spec_from_file_location|exec_module over plugins/arch-compliance/python and hooks printed nothing.

#### C5 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:107, plugins/arch-compliance/hooks/posttooluse_gate.py:229-236, plugins/arch-compliance/python/acf/enforcement.py:46-48`
- reasoning: The hook calls load_mandates(mandates_path) with no known_detectors, so no detector validation runs. A row naming an unknown detector matches no scanner and no finding carries its id, so apply_registry emits nothing for it.

#### C6 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:108, plugins/arch-compliance/python/acf/exceptions.py:5, plugins/arch-compliance/python/acf/exceptions.py:13`
- reasoning: The hook catches only AcfInputError around load_mandates. UnknownDetectorError(AcfError) is a sibling of AcfInputError(AcfError), not a subclass, so it would escape uncaught.

#### C7 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:21, plugins/arch-compliance/python/acf/adr/ledger.py:42, plugins/arch-compliance/python/acf/adr/ledger.py:83`
- reasoning: I ran the git grep for call_sites over python and hooks. It printed exactly registry.py:21 and two surface_call_sites lines in ledger.py (:42, :83). The gate filters (cli_check_diff.py:98, posttooluse_gate.py:231/235/285) and apply_registry (enforcement.py:47) read only detector and status.

#### C8 — SURVIVED
- evidence: `config/architecture/mandates.yml:70, plugins/arch-compliance/tests/fixtures/mandates_valid.yml:18, plugins/arch-compliance/tests/test_hooks.py:199-218, plugins/arch-compliance/python/acf/detectors/python_pack.py:97`
- reasoning: mandates.yml:70 declares call_sites: [ci] for no-shims.hasattr, and the fixture row at mandates_valid.yml:18 is the same. The hook always runs scan_python_file (posttooluse_gate.py:254), which stamps no-shims.hasattr (python_pack.py:97), and apply_registry ignores call_sites. test_hooks.py:199-218 asserts no-shims.hasattr appears in the hook's additionalContext, so routing by call_sites must change that test.

#### C9 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80, plugins/arch-compliance/hooks/posttooluse_gate.py:119-123, plugins/arch-compliance/hooks/posttooluse_gate.py:248-252, plugins/arch-compliance/python/acf/enforcement.py:49-50`
- reasoning: The two closures are textually identical and read only file_lines. The diff gate fills file_lines only in the .py branch (:126) and the .ts/.tsx branch (:152). The hook fills it after skipping non-code suffixes (:248-252). Any other path returns '' and token_exempted cannot match.

#### C10 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_import_graph.py:70-76, plugins/arch-compliance/python/acf/adr/contract.py:20, plugins/arch-compliance/hooks/posttooluse_gate.py:92-95, plugins/arch-compliance/python/acf/engine.py:8`
- reasoning: The test checks only that the literal 'acf.adr' is absent from the two hook files, and its docstring states the graph intent. The hook imports acf.enforcement and acf.registry (:92-95). contract.py:20 imports contains_backslash from acf.engine. engine.py imports only pathlib, so helpers placed there keep the direction acf.adr -> acf.engine.

#### C11 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:214, plugins/arch-compliance/python/acf/judge.py:218, plugins/arch-compliance/python/acf/cli_check_llm.py:61-66`
- reasoning: run_judge selects rows by detection == 'llm' (:214) and uses status == 'enforced' only to set has_enforced for provider resolution (:218-225). cli_check_llm passes registry.mandates unfiltered. Neither touches _active_mandates or the hook filters.

#### C12 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:28, plugins/arch-compliance/hooks/posttooluse_gate.py:72-81, plugins/arch-compliance/hooks/posttooluse_gate.py:91-95, plugins/arch-compliance/tests/test_repo_paths.py:74-78`
- reasoning: The only module-scope acf import is acf.repo (:28), and test_repo_paths pins it as stdlib-only. The enabled-marker check returns 0 at :72-81, before mandates are located (:83) and before the deferred imports (:91-95). Any host import would come after this point.

#### C13 — SURVIVED
- evidence: `.gitignore:8, .github/workflows/ci.yml:40, plugins/arch-compliance/python/acf/cli_check_diff.py:63-70`
- reasoning: .gitignore:8 lists .acf/, and git ls-files .acf prints nothing. CI runs python -m acf.cli_check_diff at ci.yml:40. main() goes from resolve_repo straight to load_mandates with no ENABLED_REL check, and grep finds no ENABLED in cli_check_diff.

#### C14 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:104-105, plugins/arch-compliance/python/acf/cli_check_llm.py:54`
- reasoning: inject_constraints wraps load_mandates in 'except AcfInputError' and returns 1. cli_check_llm calls load_mandates bare, so an AcfInputError propagates and the process exits non-zero. A refusal raised as AcfInputError needs no new handling at either site.

#### C15 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:91-92, plugins/arch-compliance/hooks/inject_constraints.py:110, plugins/arch-compliance/python/acf/cli_check_llm.py:54-66`
- reasoning: After load_mandates, the SubagentStart hook only renders a template (_render_constraints: acf.loader.require_file, acf.template). cli_check_llm only calls run_judge. Neither imports acf.detectors or any scanner, so under the design neither has a path to load_host_detector. The spec's load_mandates code does path resolution and is_file only.

#### C16 — SURVIVED
- evidence: `plugins/arch-compliance/skills/architecture-review/SKILL.md:62`
- reasoning: git ls-files plugins/arch-compliance/python/acf | grep -i review printed nothing (rc=1). The only architecture-review artefacts are the skill markdown and its auditors. Not load-bearing.

#### C17 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:20, plugins/arch-compliance/python/acf/registry.py:24, C:/Users/iball/Arduino/Projects/HistoricMansions/config/architecture/mandates.yml:5`
- reasoning: In git show b652fab05:config/architecture/mandates.yml, grepping for languages|arch_anchor matched no line; only id and detector lines printed, e.g. :5 '§3'. Mandate declares both languages (:20) and arch_anchor (:24) without defaults, so those rows fail Mandate validation today.

#### C18 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/arch_compliance/driver.py:144, C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/arch_compliance/driver.py:153-161, plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37`
- reasoning: At b652fab05, run() sets fail_loud_unparseable = mode == 'range'. On SyntaxError it raises in range mode, otherwise it appends a WARN 'parse' finding with exc.lineno or 0. Guards receive cf.content from the mode-dependent changed_files. The plugin's scanners return [] on SyntaxError. The proposed scan_guard signature carries no mode.

#### C19 — UNPROVEN
- evidence: `config/architecture/ARCHITECTURE.md:211-215, config/architecture/ARCHITECTURE.md:196-209, plugins/arch-compliance/python/acf/cli_check_diff.py:115-156, plugins/arch-compliance/hooks/posttooluse_gate.py:238-282`
- reasoning: The factual half holds. The diff gate passes added lines and iterates git changed_files (ACMR). The hook passes None, takes paths from argv/stdin, filters by _CODE_SUFFIXES, and keeps out-of-repo absolute paths. The doctrinal half does not follow from the cited text. :211-215 says to remove non-contractual patterns 'in code paths you are changing' and not to expand to unrelated modules. Both dispatchers are code paths this design changes, so the rule does not plainly license adding the same three host calls to each. ## Single point of definition (:196-209) cuts the other way for a decision procedure needed by more than one module. I could not establish that the deferral is sanctioned by the rule it cites.

#### C20 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37, plugins/arch-compliance/python/acf/detectors/fsm_guard.py:36-39`
- reasoning: scan_python_file returns [] on SyntaxError. fsm_guard follows the same convention.

#### C21 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:104, plugins/arch-compliance/python/acf/cli_check_diff.py:70, plugins/arch-compliance/tests/test_registry.py:30, tests/test_self_host.py:23`
- reasoning: I ran git grep -n 'load_mandates(' -- plugins tests excluding registry.py. The output matches the spec's list exactly, including SKILL.md:95 and the prose line :141. Only cli_check_diff.py:70, SKILL.md:95, test_profile_drift.py:24, test_registry.py:30 and test_self_host.py:23 pass known_detectors.

#### C22 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:125, plugins/arch-compliance/python/acf/cli_check_diff.py:82, plugins/arch-compliance/tests/test_enforcement.py:54`
- reasoning: git grep -n 'apply_registry(' -- '*.py' printed the def at enforcement.py:37, posttooluse_gate.py:125, cli_check_diff.py:82, and test_enforcement.py at 54, 60, 66, 72, 84, 94, 104, 110, 125, 130. Nothing else.

#### C23 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99, plugins/arch-compliance/hooks/posttooluse_gate.py:285, plugins/arch-compliance/python/acf/enforcement.py:47, plugins/arch-compliance/hooks/inject_constraints.py:158`
- reasoning: Both recipes reproduce exactly. The narrow one hits posttooluse_gate.py:231/235/285, cli_check_diff.py:94/98/112/113/158/168 and enforcement.py:47. The wider .status recipe adds registry.py:58, judge.py:218 and the display f-string at inject_constraints.py:158.

#### C24 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/build_artifacts.py:31, plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:132, plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23, plugins/arch-compliance/python/acf/enforcement.py:46`
- reasoning: git grep mandate_id over the detectors printed one literal per scanner at the cited lines; python_pack has :67, :97, :144 and :172. The TS rules stamp fail-loud.empty-catch and no-shims.explicit-any, and the bridge copies item['mandate_id'] (typescript_bridge.py:85). apply_registry looks the row up by finding.mandate_id.

#### C25 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:168-182, plugins/arch-compliance/hooks/posttooluse_gate.py:213-295`
- reasoning: scan_ratchet is called only in cli_check_diff. The hook's _scan_paths imports and calls build_artifacts, facade_sinks, fsm_guard, python_pack and typescript_bridge, with no ratchet. The other built-ins run in both gates: python :127/:254, TS :153-156/:278-282, facade/fsm :128-150/:255-277, build :158-166/:284-294.

#### C26 — SURVIVED
- evidence: `config/architecture/mandates.yml:70, plugins/arch-compliance/tests/fixtures/mandates_valid.yml:18, plugins/arch-compliance/tests/test_diff_cli.py:71-81, plugins/arch-compliance/tests/test_hooks.py:222-226`
- reasoning: I loaded every ast/guard row in config/architecture/mandates.yml, both profiles and mandates_valid.yml. Every active row's id equals its detector's stamped id, every active row declares ci (and hook, except no-shims.hasattr [ci]), and every declared site is within the contract. The ratchet rows are unenforced; no ast/guard row is partial or contains ':'. Inline test rows: test_diff_cli's _BARE_EXCEPT_ROW ([ci, hook], enforced/unenforced) passes. test_registry's manual rows are skipped, and not_a_real_detector raises as intended. test_judge:390 is llm. test_hooks:222 only flips statuses to unenforced. Direct Mandate constructions are ast with ['ci'] or llm.

#### C27 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/loader.py:70-73, plugins/arch-compliance/python/acf/registry.py:33-41, plugins/arch-compliance/tests/test_registry.py:40-47, plugins/arch-compliance/tests/test_enforcement.py:19-30`
- reasoning: load_model_file catches only ValidationError, and AcfInputError derives from Exception rather than ValueError, so pydantic v2 does not wrap it. _unique_ids already raises AcfInputError from a model_validator, and test_registry:40-47 observes that type. Direct constructions are test_enforcement (ast, active, call_sites ['ci'], built-in detector) and test_judge:41 / test_template:73 (llm). None trips the proposed _row_shape.

#### C28 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:91-112, plugins/arch-compliance/tests/test_profile_drift.py:7, tests/test_self_host.py:14, config/architecture/ARCHITECTURE.md:228`
- reasoning: Each user imports it from acf.cli_check_diff, passes it to load_mandates, calls sorted() on it (which yields mapping keys) or names it in prose. None uses frozenset-only operations. test_registry.py:30 passes a frozenset literal; under the design's known.get() that would fail, and the spec lists it to change.

#### C29 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:63, plugins/arch-compliance/hooks/posttooluse_gate.py:65, plugins/arch-compliance/hooks/hooks.json:22, pyproject.toml:19`
- reasoning: main() resolves repo once. The hook is spawned per PostToolUse event as a fresh python process (hooks.json:22). The console-script entry is the only other production entry. git grep finds no in-process loop over main() outside tests; test_diff_cli imports main in-process.

#### C30 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:25, plugins/arch-compliance/python/acf/detectors/__init__.py:11-28, plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:14`
- reasoning: Executed: len(KNOWN_DETECTORS) == 13. That is 3 python_pack ids, 4 guard ids, 2 TS ids and 4 llm ids, so 9 without the llm ids.

#### C31 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/citations.py:49-51, plugins/arch-compliance/python/acf/adr/citations.py:74-76, plugins/arch-compliance/python/acf/adr/citations.py:161-163`
- reasoning: git grep finds the two private helpers referenced only at :161 and :163; no test imports them. The old regex ^([A-Za-z]:[\\/]|/|\\\\) needs a separator after the drive colon, while the proposed ^([A-Za-z]:|/|\\\\) does not. The only newly-absolute strings are therefore '<letter>:<non-separator>…', i.e. drive-relative forms. _escapes_repo and resolve_under_root(...) is None compute the same containment test.

#### C32 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80, plugins/arch-compliance/hooks/posttooluse_gate.py:119-123, plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:135, plugins/arch-compliance/python/acf/detectors/build_artifacts.py:34`
- reasoning: For a path in file_lines, the old code returns '' for an empty list or an out-of-range line. The new code (lines is not None, then a range check) returns the same results, including [] -> ''. For other paths it adds a disk read. Note the consequence: line-1 findings from the ratchet and build-artifact guards on files outside file_lines can now be exempted (see unanchored finding).

#### C33 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99, plugins/arch-compliance/hooks/posttooluse_gate.py:229-236, config/architecture/mandates.yml:70, plugins/arch-compliance/tests/fixtures/mandates_valid.yml:18`
- reasoning: The old filters are detector == X and status != 'unenforced'. runs_at adds only the call_sites intersection. Census: every active built-in row declares ci, so nothing changes at the diff gate. At the hook, only rows lacking hook/posttooluse drop: the no-shims.hasattr rows in mandates.yml, the python-service profile and the fixture.

#### C34 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:21, plugins/arch-compliance/python/acf/registry.py:60, plugins/arch-compliance/skills/acf-mandate/SKILL.md:112`
- reasoning: LLM_PROMPT_IDS is imported only at :21 for the union. registry.py:60 consults known_detectors only for ast/guard rows. The only other readers are the skill's sorted() print and the tests. Removing the llm ids changes only ast/guard rows naming an llm id, plus the printed union in the skill, which the spec rewrites.

#### C35 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:67, plugins/arch-compliance/tests/test_repo_paths.py:53-71`
- reasoning: A module constant with the same string value emits identical Findings. Grepping tests for getsource or scanner filenames found nothing that pins scanner source text. The only source-text scan, test_repo_paths, matches config.{0,6}architecture, which mandate-id constants do not contain.

### Unanchored findings

- **important**: make_line_lookup lets exemptions apply to findings that could never be exempted before: synthetic line-1 findings from fail_loud_ratchet and no_build_artifacts on files outside file_lines. A token on line 1 of such a file now suppresses a whole-file ratchet growth or a build-artifact block. The spec presents this as only 'adds a disk read'.
  - evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:135`
- **advisory**: make_line_lookup lets an OSError from read_text propagate. apply_registry is called outside both gates' try/except (cli_check_diff.py:82, posttooluse_gate.py:125), so an unreadable non-code path (permissions, file locked on Windows) crashes with a traceback rather than a typed acf error.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:82`
- **advisory**: The design adds the same three host-dispatch calls to both Tier-1 dispatchers. That duplicates a decision procedure in tension with ## Single point of definition, and the cited ## Scoped refactor text applies to code paths being changed rather than licensing the duplication.
  - evidence: `config/architecture/ARCHITECTURE.md:196-209`
- **advisory**: load_host_detector inserts the host root at sys.path[0] and refuses only a top-level acf/ or acf.py. Any other top-level host module or package can shadow a not-yet-imported stdlib or third-party module for the rest of the process.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:25-26`

### Looked for but did not find

- any test or module other than citations.py referencing _looks_absolute or _escapes_repo
- any ast/guard row in config/architecture/mandates.yml, the profiles, mandates_valid.yml or inline test YAML whose detector contains ':' or whose status is partial
- any frozenset-only operation (|, &, -) on KNOWN_DETECTORS outside cli_check_diff.py:25
- any production in-process caller looping cli_check_diff.main over several repositories
- any test reading scanner module source text that a mandate-id constant would break
- a .acf/enabled check anywhere in cli_check_diff.py
- languages or arch_anchor keys in hm:config/architecture/mandates.yml at b652fab05
- deleted paths in changed_files output (it uses --diff-filter=ACMR, acf/diff.py:56)

## compliance

### Claim verdicts

#### C36 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:29-30; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:300-308; plugins/arch-compliance/python/acf/detectors/python_pack.py:77-82`
- reasoning: Doctrine: broad handlers that 'swallow errors are forbidden unless explicitly exempted with a reason'. The _call_host try block calls the host, refuses None/str/bytes, and calls list(raw) inside the try. So a generator that raises mid-iteration, a HostHit ValidationError raised inside the generator, and SystemExit all become DetectorPackError. KeyboardInterrupt is not caught. The loader's import handler re-raises UnknownDetectorError, so neither handler swallows anything. One overstatement: the doctrine does not strictly require the token here. These handlers re-raise, and the shipped detector would not flag them anyway, because _is_bare_or_exception matches only a bare handler or Name('Exception'), never a tuple. The token does no harm. Every §6.1 row names a component and an error that §4.2–§4.5 actually implement.

#### C37 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:235-251; plugins/arch-compliance/python/acf/cli_check_diff.py:168-182; plugins/arch-compliance/hooks/posttooluse_gate.py:213-295`
- reasoning: The ratchet runs only in _scan_changed. The hook's _scan_paths has no ratchet call, so a DIFF_CALL_SITES-only contract for fail_loud_ratchet is accurate. _check_builtin refuses three things: a detector missing from the map (LLM ids are excluded per §4.3), id != contract.mandate_id, and a Tier-1 site outside contract.call_sites. _row_shape refuses an active ast/guard row with no Tier-1 site. Row ids are unique, so the stamped-id rule leaves no orphan row. Every remaining Tier-1 subset ({ci}, {precommit}, {hook}, {posttooluse}) meets DIFF_CALL_SITES or HOOK_CALL_SITES, so the row reaches a gate that runs its detector. Host rows go through registry.active(call_sites, detection=...) in both runners.

#### C38 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:220-224; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:321; config/architecture/mandates.yml:171`
- reasoning: The doctrine section's literal scope is the ADR gate's adr.yml values. Row plugin.declared-never-defaulted generalises it: 'A value the gate cannot derive is declared by the host, never defaulted'. The design follows that. load_mandates raises AcfInputError when an active host row arrives with repo_root=None and never derives a root from the mandates path. apply_registry's call_sites is a required keyword-only argument, and scan_host_ast_file/scan_host_guards/make_line_lookup take repo_root positionally. Precision note: the repo_root refusal applies only when known_detectors is passed. Without it, a host row loads with no root, but nothing then runs host code, so no default stands in.

#### C39 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:295; plugins/arch-compliance/python/acf/detectors/python_pack.py:91; config/architecture/ARCHITECTURE.md:48-49`
- reasoning: Doctrine: 'Do not probe optional attributes with hasattr to paper over missing interfaces.' The design does getattr(mod, attr, None), then raises UnknownDetectorError when the result is not callable. That is a refusal, not a fallback, and the shipped no_shims_hasattr detector flags only Name('hasattr') calls. Every host failure path in §6.1 raises a typed error. The one skip is an unparseable Python file, which §4.4 item 6 declares as the built-in convention. It is not a host-detector failure (see the advisory finding).

#### C40 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/engine.py:17-24; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:110-112; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:229-231`
- reasoning: contains_backslash already exists in acf.engine, and validate_posix_rel_path calls it before looks_absolute and the segment checks. HostHit.path takes that function as an AfterValidator, so every host Finding.path is a validated relative POSIX string. The new messages that interpolate a Path use .as_posix(): (repo_root / rel_path).as_posix() and _ACTIVE_ROOT.as_posix(). The others interpolate an already-validated rel_path string. Nothing new is persisted with str(path).

#### C41 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/exceptions.py:13; plugins/arch-compliance/python/acf/exceptions.py:29; config/architecture/ARCHITECTURE.md:101`
- reasoning: Doctrine: 'Every ACF exception subclasses AcfError and nothing else.' AcfInputError (:5), UnknownDetectorError (:13) and DetectorPackError (:29) each have exactly the base AcfError. The design adds no exception class; HostHit validation errors are wrapped in DetectorPackError.

#### C42 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:15; plugins/arch-compliance/python/acf/repo.py:32; plugins/arch-compliance/tests/test_repo_paths.py:14`
- reasoning: acf.repo declares MANDATES_REL and resolve_repo. None of the code shown for engine.py, registry.py, detectors/__init__.py or host.py contains a config/architecture literal. host.py spells only 'acf' and 'acf.py', for the shadowing check, which is not a host config path. The test_repo_paths regex would catch a violation in the python/ and hooks/ trees. The rewritten acf-mandate snippet uses resolve_repo(None) and repo / MANDATES_REL.

#### C43 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:137-138; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:221-251; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:304-306`
- reasoning: Doctrine: 'Skill prose and runtime messages name no host repository, path or section.' Every literal runtime message in §4.2 and §4.4 names only the mandate id, the detector reference, the call-site sets or the running host's own root/path value. None names HistoricMansions or an hm: path. The §4.8 prose changes are described in host-neutral terms. The hm: references appear only in the spec's own rationale, not in shipped text.

#### C44 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:471-488; config/architecture/ARCHITECTURE.md:155-156`
- reasoning: Doctrine: 'An export has a live call site in the package, a hook or a skill.' Each §6.2 export has a non-test caller in §4.2–§4.6, e.g. HostHit in _to_findings, TIER1_CALL_SITES in _row_shape/_check_builtin, is_active in runs_at/load_mandates, make_line_lookup in both gates. One row is inaccurate: TS_MANDATE_IDS is listed as read by 'their scanners', but typescript_bridge.py:85 takes mandate_id from the Node JSON. KNOWN_DETECTORS still consumes it, so it stays live. A separate finding covers an existing export this design orphans.

#### C45 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:503-513; config/architecture/ARCHITECTURE.md:161-164`
- reasoning: The quantified claims I sampled are each backed by a re-runnable git grep/python recipe in §1 or the Appendix, or are per-item tables (§4.3, §4.7, §6.1, §6.2). Sampled: 'nothing extends KNOWN_DETECTORS', 'every built-in scanner stamps one fixed mandate_id', 'no dynamic loader exists', 'None is refused by _row_shape', 'no row is partial', the load_mandates/apply_registry caller sets. 'Every new load-time refusal without known_detectors is AcfInputError' is backed by the §6.1 per-item table.

#### C46 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:337; plugins/arch-compliance/python/acf/cli_check_diff.py:152; config/architecture/ARCHITECTURE.md:173-174`
- reasoning: The rule requires a declared encoding on subprocess text calls and on file reads. It says nothing about the errors= policy. Both new reads declare encoding='utf-8', and the TypeScript-branch read is the same strict utf-8 read that exists today at :152. errors='replace' therefore does not breach this rule. The host runners call in-process callables and add no subprocess.

#### C47 — SURVIVED
- evidence: `pyproject.toml:3; plugins/arch-compliance/.claude-plugin/plugin.json:3`
- reasoning: Doctrine (:186-187) names plugin.json and pyproject.toml. Both read "0.2.2" today, and §4.8 bumps both to "0.2.3". The acf-mandate and acf-setup skill prose changes trigger the rule. No other non-docs file carries 0.2.2.

#### C48 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:85; plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23; plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:258`
- reasoning: Doctrine (:198-200): a constant set needed by more than one module must have 'exactly one canonical implementation that every call site consumes'. The claim says each built-in mandate id is defined once, in a scanner-module constant 'read by both the scanner and KNOWN_DETECTORS'. That is false for the two TypeScript ids. The Node rules hard-code 'fail-loud.empty-catch' and 'no-shims.explicit-any'. The Python bridge copies item['mandate_id'] from the Node JSON and never reads TS_MANDATE_IDS. The design adds a second, Python-side definition (TS_MANDATE_IDS) that KNOWN_DETECTORS reads and no scanner reads. The two are tied only by a test that compares the strings. So the design introduces a new two-definition breach of the rule it claims to satisfy. A single point is available inside this design's scope, e.g. the bridge stamps mandate_id from TS_MANDATE_IDS[item['detector']] and refuses a Node value that disagrees. The other parts of the claim hold: the Python ids, runs_at, host loading and make_line_lookup.

#### C49 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/citations.py:49-51; plugins/arch-compliance/python/acf/adr/citations.py:74-76; config/architecture/ARCHITECTURE.md:198-200`
- reasoning: Scoped refactor forbids expanding into unrelated modules. citations.py is changed only to delete _looks_absolute/_escapes_repo once acf.engine gains equivalents. Leaving them would create a second implementation, which Single point of definition forbids. The citations change is therefore compelled by a sibling rule, not scope creep, and the spec discloses the one classification change (drive-relative becomes external). The line-lookup and active-row consolidations sit in the gate code this design rewires. The shared dispatcher and the parse helper are declared non-goals.

#### C50 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:147-148; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:60-72`
- reasoning: Doctrine: 'A LedgerRow or LedgerAmendment field changes only through a spec and a gate run.' The §3 in-scope table lists no change to acf/adr/ledger.py or any ledger model. The spec cites ledger.py only for unrelated surface_call_sites grep hits.

#### C51 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:50; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:123; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:125`
- reasoning: Principle 4: 'prose anchors, detectors, auditors, and call sites must agree or tests fail'. The built-in contracts and call-site routing implement exactly that. Principles 1–3 are respected: typed refusals, one registry façade and one Finding schema (HostHit is converted, not a parallel schema), POSIX paths. :123 and :125 call for 'Extension points for project-specific detectors', which host ast/guard references provide.

#### C52 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:49-50; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:333-345`
- reasoning: A '' line makes token_exempted false, so the finding is kept, never suppressed. A missing or out-of-root file has no line that could carry an exemption token, so [] hides nothing. read_text is not wrapped, so an OSError propagates. In cli_check_diff, apply_registry runs outside the :69-74 try, so the traceback reaches the operator. errors='replace' cannot hide an ASCII token.

### Unanchored findings

- **important**: Removing LLM_PROMPT_IDS from KNOWN_DETECTORS leaves acf.judge.LLM_PROMPT_IDS with no runtime consumer. Its only non-test use is cli_check_diff.py:21/:25, and judge.py itself never reads it. That breaches ## Live consumers (a test-only export is dead code). acf-mandate SKILL.md:56 and :121 still say llm rows 'require a known prompt id in LLM_PROMPT_IDS', which nothing enforces, and §4.8 does not touch those lines.
  - evidence: `plugins/arch-compliance/python/acf/judge.py:29`
- **advisory**: scan_host_ast_file returns [] on SyntaxError, so a host ast detector never sees an unparseable changed Python file and nothing reports the skip. This copies the built-in convention, and §3 discloses the divergence from the origin driver. It is a silent path under ## Fail loud that the doctrine table does not mention.
  - evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37`

### Looked for but did not find

- ## High-frequency misses: re-checked all six. Completeness claims carry recipes. repo_root/call_sites have no re-entering default. No host name appears in runtime messages. No new exception class or mixin. No new subprocess. test_self_host.py:40 and the skill snippet consume resolve_under_root/load_mandates/MANDATES_REL rather than re-implementing them. Nothing found.
- ## Build artifacts: the design only adds a TIER1 contract for no_build_artifacts and leaves the guard's behaviour unchanged. Not otherwise touched.
- ## Fail-loud ratchet: the ratchet is restricted to DIFF_CALL_SITES, which matches the code (cli_check_diff.py:168-182). This repository's row is [ci] and unenforced, so it still loads. The new section in §4.8 covers it.
- ## Façade sinks / ## FSM transitions: the one-active-row-per-built-in-detector consequence is stated in Decision 3, and this repository's rows have matching ids. Not an unstated mandate.
- ## Soft fail-loud smells / ## React boundaries: llm rows are outside the ast/guard checks and the Tier-2 judge is unchanged (judge.py:218). Only the LLM_PROMPT_IDS orphaning above arises.
- ## Post-merge: no operational declaration is touched.
- ## Release discipline (installed-copy clause): the hooks run the installed python/. The spec names this section and bumps the version, and the gate-skill byte check is unaffected.
- unstated_mandates is empty because the spec's governing list (Fail loud through Scoped refactor, plus the five portable principles) covers every doctrine section this design touches.

## sweeper

### Claim verdicts

#### C53 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; plugins/arch-compliance/hooks/posttooluse_gate.py:231; plugins/arch-compliance/hooks/posttooluse_gate.py:285; plugins/arch-compliance/python/acf/enforcement.py:47; plugins/arch-compliance/python/acf/judge.py:218`
- reasoning: I grepped `unenforced|.status|call_sites` across the plugin, excluding tests. The active-row filters are cli_check_diff.py:98, posttooluse_gate.py:231, :235 and :285, enforcement.py:47 and registry.py:58. The design replaces each of them. The other status reads are judge.py:218 (Tier-2, out of scope by Decision 2) and inject_constraints.py:158 (display only). cli_check_llm.py:61-66 calls run_judge and never calls apply_registry. No other Tier-1 site filters rows.

#### C54 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:46; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:122-124; plugins/arch-compliance/python/acf/adr/citations.py:49-51`
- reasoning: The SUBSUMED half holds: citations.py:49-51 and :74-76 are the only string-level absolute and escape tests, and _WIN_DRIVE_RE (contract.py:95) really is ADJACENT. The claim fails where it waves fail_loud_ratchet.py:123 off as 'resolves paths for I/O, a different responsibility'. scan_ratchet takes params.baseline, a relative path string supplied by the registry, tests it with Path.is_absolute(), and joins it under repo_root with no containment check (:122-124). scan_tree likewise joins params.roots under root unchecked (:46). load_mandates' host-file check does the same job: it turns a registry-supplied relative string into an existing file under the host root, which is also an I/O check. After the design that job has two implementations. One uses looks_absolute and resolve_under_root (contained, platform-independent). The other uses Path.is_absolute and a bare join (uncontained, and on Windows it reads '/x' as relative). A search by behaviour (who joins registry params under the root?) finds the ratchet; the claim's search by helper name misses it.

#### C55 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:84-92; plugins/arch-compliance/python/acf/enforcement.py:52`
- reasoning: The bridge's coercion decodes untyped JSON dicts and takes mandate_id, severity and detector from the subprocess payload (typescript_bridge.py:85-90). Its severity is overwritten later anyway by enforcement.py:52. The host runner receives typed HostHit objects and takes the id and severity from the row. The input formats share nothing, so ADJACENT is right.

#### C56 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:238-255; plugins/arch-compliance/python/acf/judge.py:247`
- reasoning: _to_finding sits at judge.py:238-255 in the worktree, two lines off from the cited :236-253. It demotes BLOCK to WARN by confidence (:242-245), admits path '<diff>' and line 0 (:249-250), and takes mandate_id from result.mandate_id rather than the row (:247). Each of these differs from the host contract, so a shared constructor would have to parameterize away most of its body. ADJACENT holds.

#### C57 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:25-26; plugins/arch-compliance/hooks/inject_constraints.py:29; tests/test_check_installed_skills.py:15-18`
- reasoning: I grepped importlib, import_module, spec_from_file_location, exec_module, runpy, exec( and sys.path.insert across every *.py. In plugin runtime code the only hits are the two hooks inserting the plugin's own python/ directory. The single dynamic loader is in a repository-level test, and it loads a fixed script, not a path from the registry. Nothing in the plugin executes code from a path the registry supplies. The hooks' insertion serves a different purpose (bootstrapping the plugin's own package), so ADJACENT is right. HistoricMansions has no top-level acf, yaml or pydantic that the root insertion could shadow.

#### C58 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80; plugins/arch-compliance/hooks/posttooluse_gate.py:119-123; plugins/arch-compliance/python/acf/enforcement.py:23`
- reasoning: I grepped `line_lookup|LineLookup|_lookup(` across the repository. The only production closures are the two token-identical ones; LineLookup is declared once, at enforcement.py:23. cli_check_llm.py and judge.py never call apply_registry (cli_check_llm.py:61-66). The only other lookups are test doubles in test_enforcement.py. No skill snippet builds one.

#### C59 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:95; plugins/arch-compliance/tests/test_profile_drift.py:24; plugins/arch-compliance/skills/architecture-review/SKILL.md:62; tests/test_self_host.py:40-41`
- reasoning: The acf-mandate snippet and the profile drift test both consume load_mandates with KNOWN_DETECTORS. The architecture-review skill calls load_mandates without known_detectors, so it reaches only the row-shape checks. acf-setup only states the expected outcome in prose (acf-setup SKILL.md:224). test_self_host.py:40-41 checks only manual rows against a host prefix, which is host policy. I found no independent check of detector ids or call sites.

#### C60 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:242-246`
- reasoning: The try/except ValueError at :242-245 already tells in-repo from out-of-repo paths: out-of-repo paths get the absolute posix string, and every path is appended to rel_paths at :246. Recording in-repo paths from that same branch adds no second test, and rel_paths keeps its current contents for the build-artifact guard at :284-294.

#### C61 — SURVIVED
- evidence: `config/architecture/mandates.yml:70; config/architecture/mandates.yml:138; plugins/arch-compliance/profiles/python-service/mandates.yml:18; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:104; plugins/arch-compliance/skills/acf-mandate/SKILL.md:43`
- reasoning: I grepped call_sites across the corpus. The shipped registries, the profiles and the test fixtures use only ci, hook and audit. The parent doc lists precommit, ci, posttooluse and audit, and the skill lists ci, hook and audit. Every audit-bearing ast or guard row also carries ci, and the audit-only rows are manual. No code reads call_sites today (registry.py:21 is the only hit), so audit is read by no Tier-1 gate. HistoricMansions' registry also uses only precommit, posttooluse, ci and audit. No shipped row is misrouted.

#### C62 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_hooks.py:199-218; plugins/arch-compliance/tests/test_registry.py:30; plugins/arch-compliance/tests/test_profile_drift.py:24; plugins/arch-compliance/tests/test_python_pack.py:36; plugins/arch-compliance/tests/test_judge.py:67`
- reasoning: I grepped the tests for hasattr, apply_registry(, KNOWN_DETECTORS, LLM_PROMPT_IDS, _looks_absolute and _escapes_repo. test_hooks.py:217 is the only test that depends on a [ci]-only row being reported. The other hook tests use the fixture's [ci, hook] rows. test_registry.py:30's frozenset is covered by the spec. test_profile_drift.py:24 and test_self_host.py:23 load rows that satisfy the new built-in contracts (ids match and call sites are a subset of TIER1). test_python_pack.py:36 asserts the literal value, which the constant keeps. test_judge.py:67 checks the judge's own LLM_PROMPT_IDS, which is unchanged. No test imports citations' private helpers. test_diff_cli.py copies mandates_valid.yml, all of whose rows declare ci.

#### C63 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:168-182; plugins/arch-compliance/hooks/posttooluse_gate.py:213-295; plugins/arch-compliance/python/acf/detectors/python_pack.py:16`
- reasoning: KNOWN_DETECTORS[...].call_sites declares where each built-in detector runs. The fact itself is decided by the gates' dispatch code: fail_loud_ratchet runs only because cli_check_diff.py:168-182 loops over it and _scan_paths has no such loop. After the design that is two owners of 'detector X runs at gate Y', the declared map and the hand-written dispatch. Nothing pins them together: test_builtin_detectors.py pins the map's values, not the gates' behaviour. Adding a ratchet call to the hook, or a new built-in to one gate only, would leave load_mandates accepting or refusing call sites wrongly, with no test failing. Smaller point: python_pack's detector-id literals (:72, :102, :152, :180) stay separate spellings from PYTHON_AST_DETECTOR_IDS (:16) and the map keys; §4.3 makes constants of mandate ids only.

#### C64 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:59-62; plugins/arch-compliance/hooks/posttooluse_gate.py:243`
- reasoning: Both cited sites take an already-resolved absolute Path, return its relative string, and skip anything outside the root. resolve_under_root goes the other way, from a relative string to a contained Path. As stated, the claim is true. These are not the nearest same-direction shapes, though: fail_loud_ratchet.py:46 (params.roots) and :122-124 (params.baseline) do relative-string-to-path-under-root without containment. That gap is filed under C54.

#### C65 — UNPROVEN
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:57-58`
- reasoning: _ACTIVE_ROOT, _call_host and the conftest do not exist yet (Glob finds no conftest.py anywhere), so I have no site that corroborates the claim. As designed, host code also runs in a second wrapped region: exec_module in load_host_detector, which re-raises UnknownDetectorError rather than DetectorPackError. 'Single wrapped region' therefore holds only if module top-level code does not count as invoking a host callable. The nearest existing pattern, typescript_bridge.py:57-58 and :94-95 wrapping detector-pack failures as DetectorPackError, is ADJACENT.

#### C66 — REFUTED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:18; tests/test_self_host.py:5`
- reasoning: I grepped `KNOWN_DETECTORS|known detector|detector union|.ts\`|.tsx` across shipped docs and skills. acf-mandate SKILL.md:18 ('Validate with `load_mandates` + known detector union') is not among the §4.8 sites, yet §4.8 rewrites the 'union' wording at :106-112 to 'built-in contracts'. test_self_host.py:5's docstring ('`KNOWN_DETECTORS` the one detector union') sits in a file whose :23 and :40 §4.7 edits, but is left unchanged. The other sites (README:62, :106; ARCHITECTURE.md:9-11; ARCH_COMPLIANCE:161, :184; PLUGIN_SELF_HOSTING:84, :266-268, :373-376; acf-setup :150, :159; hook docstring :12) are covered.

### Unanchored findings

- **important**: KNOWN_DETECTORS.call_sites declares which gate runs each built-in detector, but the gates' hand-written dispatch decides it. That leaves two unpinned owners: a ratchet call added to the hook, or a new built-in wired into one gate only, silently desynchronizes load_mandates' call-site refusal from what actually runs.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:168-182`
- **advisory**: After the design, the fail-loud ratchet still resolves registry-supplied relative paths (params.roots, params.baseline) with Path.is_absolute and an uncontained join, while load_mandates and the host loader use looks_absolute and resolve_under_root. That is two implementations of 'registry path string to file under host root', with different absolute semantics on Windows. C54 classifies the ratchet as a different responsibility, but it is the same one.
  - evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:122-124`
- **advisory**: The host runner's _to_findings sets severity=Severity(mandate.severity), which apply_registry already does unconditionally for every finding. That gives a third owner of 'severity comes from the row', redundant on the Tier-1 path.
  - evidence: `plugins/arch-compliance/python/acf/enforcement.py:52`
- **advisory**: The §4.8 prose sweep misses acf-mandate SKILL.md:18 ('known detector union') and the test_self_host.py:5 docstring, both of which the KNOWN_DETECTORS change makes stale.
  - evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:18`

### Looked for but did not find

- A third LineLookup or exemption-line reader (grep: line_lookup, LineLookup, _lookup(, token_exempted, exemption_tokens)
- An existing dynamic loader of registry-supplied code paths (grep: importlib, import_module, spec_from_file_location, exec_module, runpy, exec(, sys.path.insert)
- Another active-row filter in a Tier-1 site (grep: unenforced, .status, _active_mandates, call_sites)
- An independent detector-id or call-site validator in skills or tests (grep: load_mandates, known_detectors, detector in acf-setup, acf-mandate and architecture-review SKILL.md, test_profile_drift.py, test_self_host.py)
- Another string-level absolute or under-root test (grep: is_relative_to, [A-Za-z]:, is_absolute(, relative_to(, absolute, '..')
- Call-site vocabulary outside {ci, precommit, hook, posttooluse, audit} (grep: call_sites in yml, md and py, including the hm: registry)
- Existing tests that depend on hook reporting [ci]-only rows, on the old apply_registry signature, or on LLM ids in KNOWN_DETECTORS (grep: hasattr, apply_registry(, KNOWN_DETECTORS, LLM_PROMPT_IDS in tests)

### Relationships

- PARTIAL_OVERLAP: `KNOWN_DETECTORS[...].call_sites (BuiltinDetector)` — responsibility `decide at which Tier-1 gate a built-in detector runs` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:168-182`
  - resolution: R = 'detector X runs at gate Y'. Either have each gate's dispatch iterate over KNOWN_DETECTORS entries whose call_sites intersect its own set, so the map drives dispatch, or add a test that runs each gate against a registry holding every built-in row and asserts that the detectors which ran equal the map's call_sites. Either way the hand-written per-gate dispatch lists collapse into the map.
- PARTIAL_OVERLAP: `acf.engine.resolve_under_root / looks_absolute` — responsibility `resolve a registry-supplied relative path string to a file under the host root` — existing `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:122-124`
  - resolution: R = joining a registry path param under the root. The ratchet's params.baseline and params.roots joins (:46, :122-124) become resolve_under_root consumers, with looks_absolute replacing Path.is_absolute, or the spec records them as named debt under Single point of definition.
- SUBSUMED: `acf.engine.resolve_under_root / looks_absolute` — responsibility `string-level absolute and escape test` — existing `plugins/arch-compliance/python/acf/adr/citations.py:49-51`
  - resolution: citations' _looks_absolute and _escapes_repo are deleted and call the engine helpers, as the spec states.
- ADJACENT: `resolve_under_root` — responsibility `relative/absolute path conversion` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:242-245`
  - resolution: none
  - non-merge: These are opposite directions: the cited site turns an already-resolved absolute Path into a relative string, and resolve_under_root turns a relative string into a contained Path.
- IDENTICAL: `_to_findings (host runner)` — responsibility `assign Finding.severity from the registry row` — existing `plugins/arch-compliance/python/acf/enforcement.py:52`
  - resolution: Leave severity assignment to apply_registry, the one sink every Tier-1 finding passes through. The host runner can set any placeholder, or the row severity only because Finding requires a value, and state that.
- ADJACENT: `_to_findings (host runner)` — responsibility `build Finding from detector output and row` — existing `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:84-92`
  - resolution: none
  - non-merge: The bridge decodes untyped JSON from a plugin-owned subprocess and takes the id from the payload; the host runner takes typed HostHit objects and the id from the row.
- ADJACENT: `_to_findings (host runner)` — responsibility `build Finding from detector output and row` — existing `plugins/arch-compliance/python/acf/judge.py:238-255`
  - resolution: none
  - non-merge: The judge demotes by confidence, admits '<diff>' and line 0, and takes mandate_id from the result. The host runner does none of these.
- IDENTICAL: `make_line_lookup` — responsibility `look up the source line for exemption checks` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80`
  - resolution: Both closures (cli_check_diff.py:76-80 and posttooluse_gate.py:119-123) are deleted, as the spec states.
- ADJACENT: `Mandate.runs_at / MandateRegistry.active` — responsibility `decide whether a row is live at a gate` — existing `plugins/arch-compliance/python/acf/judge.py:218`
  - resolution: none
  - non-merge: Tier-2 reads status only to decide whether a provider is required, and reviews every llm row (Decision 2).
- ADJACENT: `load_host_detector sys.path insertion` — responsibility `put a code root on sys.path` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:25-26`
  - resolution: none
  - non-merge: The hooks bootstrap the plugin's own package at start-up. The loader inserts one host root once and refuses shadowing of acf.
- PARTIAL_OVERLAP: `scan_host_ast_file parse-or-skip` — responsibility `parse Python and skip on SyntaxError` — existing `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37`
  - resolution: A shared parse_or_none helper in acf.engine that the four scanners and the host runner consume. The spec defers it explicitly under Scoped refactor.

### Two-owner counts

- decide which Tier-1 gate runs a built-in detector: 3
- resolve a registry-supplied relative path under the host root: 2
- test whether a registry-supplied path string is absolute: 2
- assign Finding.severity from the registry row: 3
- build Finding from detector output plus mandate row: 4
- parse Python source and skip on SyntaxError: 5
- decide whether a mandate row is live: 2
- spell a built-in Python detector id: 2
- list built-in detector ids with their mandate ids: 2
- Tier-1 dispatch loop over changed paths: 2

### Document conflicts

- `docs/design/ADR_GATE_HOST_CONTRACT.md:302` (restates): a refusal would be a second implementation of the repo-relative test that ... citations.py:49 (`_looks_absolute`) and `:74` (`_escapes_repo`) already own
- `config/architecture/ARCHITECTURE.md:226` (restates): A check re-implemented in a test or a skill instead of consumed from the package (... `acf.cli_check_diff.KNOWN_DETECTORS` ...)
- `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:84` (restates): `acf.cli_check_diff.KNOWN_DETECTORS` is the one detector-id union

## hardening

### Claim verdicts

#### C67 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:72; plugins/arch-compliance/hooks/posttooluse_gate.py:113-117; plugins/arch-compliance/hooks/inject_constraints.py:104; plugins/arch-compliance/python/acf/cli_check_llm.py:54`
- reasoning: In the design, the file-existence check is in load_mandates under `known_detectors`, and both gates pass that argument. The import runs at dispatch inside _scan_changed and _scan_paths, which sit under cli_check_diff.py:71-72 (UnknownDetectorError is already listed) and under the hook's scan try at :113 (widened in §4.6). So the deferral works as claimed. One supporting reason is overstated. inject_constraints.py:104 and cli_check_llm.py:54 call load_mandates without known_detectors. An import placed in the same `known_detectors is not None` block would never run for them, so 'importing at load would run host code in SubagentStart/acf-check-llm' holds only for an import placed in the Mandate validator. The remaining reason still carries the decision: the hook loads with known_detectors, so an import at load there would import [ci]-only guards on every edit.

#### C68 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:46; plugins/arch-compliance/python/acf/detectors/python_pack.py:67; plugins/arch-compliance/python/acf/cli_check_diff.py:168-182`
- reasoning: Findings are matched to rows by mandate_id (enforcement.py:46). Built-in scanners stamp fixed ids (python_pack.py:67/97/144, build_artifacts.py:31, facade_sinks.py:69, fsm_guard.py:59, fail_loud_ratchet.py:132, emptyCatch.ts:23, explicitAny.ts:15). The id==contract.mandate_id check therefore guarantees a built-in row receives its findings. The ratchet runs only in the diff gate (cli_check_diff.py:168; there is no call in posttooluse_gate.py:213-295), so the per-detector call_sites contract plus the Tier-1-site rule guarantee that some gate runs every active built-in row. Host rows build Finding from the row itself, so their findings always land on that row. A host ast row with languages none is refused, and every other language value maps to a scanned suffix. I found no active ast/guard row shape that passes these checks and runs at no gate.

#### C69 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:63; plugins/arch-compliance/hooks/posttooluse_gate.py:65; plugins/arch-compliance/tests/test_diff_cli.py:48`
- reasoning: cli_check_diff.main resolves one repo per invocation (:63). The hook resolves once per fresh process (:65). The pyproject entry points (pyproject.toml:19-20) are per process. Grepping skills/ and scripts/ found no production caller that runs main() repeatedly in-process. The only multi-root producer is in-process test calls such as test_diff_cli.py:48/61/98, and they go through the proposed fixture. The refusal raises AcfInputError, and nothing repairs in production.

#### C70 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:67; plugins/arch-compliance/python/acf/detectors/build_artifacts.py:31; plugins/arch-compliance/python/acf/cli_check_diff.py:168-182`
- reasoning: Every scanner hard-codes its mandate_id, and the ratchet runs only in acf-check-diff, so the contract records facts that already exist. A read-only run of the Appendix recipe over config/architecture/mandates.yml, the profiles and the fixtures printed no pair of active rows sharing a built-in detector and no id/detector mismatch. The one-row-per-built-in cost therefore affects no shipped registry.

#### C71 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/cli_check_llm.py:54; plugins/arch-compliance/hooks/inject_constraints.py:105`
- reasoning: inject_constraints.py:105 catches AcfInputError. cli_check_llm.py:54 calls load_mandates with no try at all, so the new refusals reach the user as an uncaught traceback, not as handled errors. The spec's own §3 says 'uncaught'. 'No caller change' is still true, since today's behaviour for a malformed registry is the same traceback. 'Each already handles AcfInputError' is false for one of the two callers. Not load-bearing.

#### C72 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37`
- reasoning: Each built-in scanner parses for itself (python_pack.py:35 and the facade/fsm/ratchet scanners each do their own ast.parse). The design adds one shared parse for N host ast rows and leaves built-in parsing unchanged. That is implementable: the tree is built once in scan_host_ast_file and passed as a keyword.

#### C73 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:46-52; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:85`
- reasoning: apply_registry looks up by_id.get(finding.mandate_id) (:46) and takes severity from that row (:52). A host-supplied mandate_id would therefore pick the row. The TypeScript bridge shows the existing pattern of trusting a producer's mandate_id (:85). Returning HostHit and building Finding from the row removes that state rather than checking it.

#### C74 — SURVIVED
- evidence: `.gitignore:8; .github/workflows/ci.yml:40; plugins/arch-compliance/hooks/posttooluse_gate.py:72-81`
- reasoning: .acf/ is gitignored (.gitignore:8), so a CI checkout never has .acf/enabled. CI invokes cli_check_diff explicitly (ci.yml:40). The hook exits 0 before any third-party import when the marker is absent (:72-81). Requiring the marker in acf-check-diff would disable CI, so the stated trade-off is accurate.

#### C75 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:27-52; plugins/arch-compliance/hooks/posttooluse_gate.py:254; config/architecture/mandates.yml:70`
- reasoning: scan_python_file is called unconditionally in both gates (posttooluse_gate.py:254, cli_check_diff.py:127). It emits all three python_pack mandate ids without reading the registry, and scan_typescript_file does the same for both TS ids. Selecting with registry.active therefore cannot stop a no-shims.hasattr finding, whose row is [ci] only (mandates.yml:70), from surviving in the hook. Only the sink filter can, so the filter is not redundant. The claim's parenthetical is wrong: spec Decision 2 does state this reason and cites python_pack.py:27-52.

#### C76 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:14-27; plugins/arch-compliance/python/acf/registry.py:29-41`
- reasoning: Mandate is a plain BaseModel with no model_config. It has id, severity, detection, detector, languages (a Literal that includes 'none'), call_sites list[str], status and params dict|None. MandateRegistry already carries a model_validator and a @property (by_id, :43-45), so adding a property, a method and a model_validator is compatible. pydantic 2.13.3 is installed.

#### C77 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/finding.py:6-19; plugins/arch-compliance/python/acf/registry.py:17`
- reasoning: Finding's required fields are mandate_id, severity, path, line, message and detector. confidence is optional, and detection defaults to 'ast' and is settable. Severity is a str Enum with values BLOCK/WARN, and Mandate.severity is Literal['BLOCK','WARN'], so Severity(mandate.severity) constructs.

#### C78 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:23; plugins/arch-compliance/python/acf/enforcement.py:43-52`
- reasoning: by_id is at :43/:46, the status drop at :47, and exemption and severity handling at :49-52. LineLookup is Callable[[str,int],str] (:23), which a closure returned by make_line_lookup satisfies.

#### C79 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:69-72; plugins/arch-compliance/python/acf/cli_check_diff.py:110; plugins/arch-compliance/python/acf/cli_check_diff.py:151-152`
- reasoning: load_mandates is at :70 and _scan_changed at :71, both inside the try. The except at :72 lists GitError, AcfInputError, UnknownDetectorError and DetectorPackError. The closure and apply_registry are at :76-82. In the .py branch, repo, text (:125), posix (:122), lines (:121) and registry are in scope after the fsm loop at :140-150. The .ts branch reads at :152, where the result can be bound to text. `changed` (:110) is in scope after the ratchet loop at :168-182.

#### C80 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:91-125; plugins/arch-compliance/hooks/posttooluse_gate.py:229-252; plugins/arch-compliance/hooks/posttooluse_gate.py:284-294`
- reasoning: The deferred imports are at :91-104. The load try is at :106-110 and catches only AcfInputError. The scan try is at :113-117 and catches only DetectorPackError, so it can be widened. The lookup and apply_registry are at :119-125. The inline filters are at :229-236 and :284-286, and the relative_to/ValueError fallback is at :242-245. text (:251) and rel (:243) are in scope in both the .py and TypeScript branches. The build-artifact loop is at :284-294.

#### C81 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:72; plugins/arch-compliance/python/acf/cli_check_diff.py:82; plugins/arch-compliance/hooks/posttooluse_gate.py:125`
- reasoning: The universal 'never a traceback' does not hold for the design as written. (1) §4.4 item 3 places `fn = getattr(mod, attr, None)` after the exec_module handler and outside it. getattr with a default swallows only AttributeError, so a host module-level __getattr__ that raises anything else, a host-detector failure, escapes load_host_detector as a raw exception. Neither cli_check_diff.py:72 nor the widened hook except at :113 lists it, and the user gets a traceback. (2) make_line_lookup is called inside apply_registry, and both gates call apply_registry outside any try (cli_check_diff.py:82, posttooluse_gate.py:125). §4.5 says an OSError from read_text propagates, so a host guard hit naming an unreadable file also ends in a traceback. The _call_host wrapping itself (materialising inside the try, SystemExit included) is sound.

#### C82 — SURVIVED
- evidence: `pyproject.toml:23-24; plugins/arch-compliance/tests/test_diff_cli.py:9; plugins/arch-compliance/python/acf/__init__.py:1`
- reasoning: As code, everything here can be built: module globals, a single sys.path insert, a sha256-named module registered before exec_module and removed on failure, and a monkeypatch-based fixture. No conftest.py exists today, so there is no collision. pytest's pythonpath already makes acf importable (pyproject.toml:24), and test_diff_cli.py imports and calls main in-process (:9, :48). The acf/ / acf.py refusal can be implemented, but its stated purpose cannot occur. acf is a regular package (acf/__init__.py exists) and is already in sys.modules before any dispatch (posttooluse_gate.py:28), so `acf.*` submodule imports resolve through acf.__path__ and never consult the inserted host root. See the mechanism trace.

#### C83 — SURVIVED
- evidence: `C:/Python313/Lib/dataclasses.py:757`
- reasoning: dataclasses._is_type runs `ns = sys.modules.get(cls.__module__).__dict__` (Python 3.13.2, :757) for string annotations with no module prefix. Under `from __future__ import annotations`, a module missing from sys.modules makes this raise AttributeError on None. Registering the module before exec_module prevents that. spec_from_file_location accepts an arbitrary name.

#### C84 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:5-7; plugins/arch-compliance/python/acf/judge.py:16; plugins/arch-compliance/python/acf/adr/contract.py:20; plugins/arch-compliance/tests/test_adr_import_graph.py:54-76`
- reasoning: registry imports pydantic, exceptions and loader. engine is stdlib-only and imports no acf module, so registry→engine adds no cycle. judge→registry stays one-way. detectors/__init__ already imports the scanner modules, and adding registry (which never imports detectors) adds no cycle. acf.adr already imports acf.engine (contract.py:20). The import-graph test forbids only `scripts` imports in acf.adr and the literal 'acf.adr' in the hooks. The hook importing acf.detectors and acf.detectors.host reaches registry, finding, engine and exceptions, not judge or adr.

#### C85 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:53-55; plugins/arch-compliance/python/acf/registry.py:64; plugins/arch-compliance/python/acf/loader.py:67-73`
- reasoning: load_mandates calls load_model_file(path, Mandate, subject='mandates file', fmt='yaml', many=True) (:53-55) and returns MandateRegistry(mandates=..., source_path=path.as_posix()) (:64). The loader converts only ValidationError (loader.py:72), so an AcfInputError raised by a model_validator keeps its type.

#### C86 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_repo_paths.py:47-48; plugins/arch-compliance/hooks/posttooluse_gate.py:11`
- reasoning: The pinned string at test_repo_paths.py:48 is exactly the docstring text at posttooluse_gate.py:11. No pin matches :12.

#### C87 — SURVIVED
- evidence: `config/architecture/mandates.yml:60; plugins/arch-compliance/python/acf/enforcement.py:31; plugins/arch-compliance/python/acf/detectors/python_pack.py:78-82`
- reasoning: mandates.yml:60 declares [fail-loud.bare-except-ok], and enforcement.py:31 honours `# token: reason` on the flagged line. The design's handlers are `except (Exception, SystemExit)`, an ast.Tuple, which _is_bare_or_exception (python_pack.py:78-82) never flags. So the handlers pass the gate, but because they are not detected at all; the token is redundant for them.

#### C88 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/engine.py:8; plugins/arch-compliance/python/acf/engine.py:17-24`
- reasoning: engine imports only pathlib and defines contains_backslash. Adding re stays stdlib-only.

#### C89 — SURVIVED
- evidence: `README.md:68-74; plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23; plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15; plugins/arch-compliance/tests/test_registry.py:24`
- reasoning: The README table rows (:68-74) carry the detector id and mandate id in backticked columns that can be parsed. The TS rules stamp literal mandate_id strings at the cited lines. test_registry.py:20-29 and :33-36 show the inline-YAML pattern the new cases can copy.

### Unanchored findings

- **important**: The acf/ / acf.py host-root refusal guards a state that cannot occur: acf is a regular package already in sys.modules before any host dispatch, so its submodule imports resolve via acf.__path__ and never reach the inserted host root. The refusal has no producer and would reject a legitimate host with a top-level acf directory.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:28`
- **important**: Two host-originated failures escape both gates' fail-loud handlers as tracebacks: getattr(mod, attr, None) sits outside the import handler, so a module __getattr__ raising anything but AttributeError escapes, and make_line_lookup's propagating OSError runs inside apply_registry, which is outside every try.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:82`
- **advisory**: Rung 1 was not considered for ast hits: a host ast callable returns a HostHit carrying a path that must equal the scanned file. A path-less ast hit type would make the mismatch unrepresentable and remove _to_findings' expected_path refusal.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:309`
- **advisory**: The hook adds a parallel in_repo_rel_paths list instead of hardening the producer: the relative_to fallback at :244-245 puts absolute out-of-repo paths into rel_paths. Fixing that producer would give one path list, not two.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:244-245`
- **advisory**: The detector field now carries two meanings, chosen by whether it contains ':', the same one-field-two-meanings pattern §1 item 3 criticises for call_sites. A structured host reference field would make malformed separators unrepresentable.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:38`
- **advisory**: fail-loud.bare-except does not flag `except (Exception, ...)` tuples, so the design's two broad handlers, and any host-code pattern like them, bypass the detector entirely and the exemption token is decorative.
  - evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:78-82`

### Looked for but did not find

- A second production caller of cli_check_diff.main or _scan_changed running several roots in one process (searched skills/, scripts/, pyproject entry points): none
- An existing conftest.py that would collide with the proposed plugins/arch-compliance/tests/conftest.py: none
- An import cycle from acf.detectors -> acf.registry or acf.registry -> acf.engine: none (engine is stdlib-only and imports no acf module)
- A shipped registry with two active rows on one built-in detector, or a row id differing from its detector's stamped mandate id: none (Appendix recipe run read-only)
- A pydantic path that would wrap AcfInputError from a model_validator into ValidationError: loader.py converts only ValidationError, and non-ValueError exceptions propagate
- A top-level acf directory in the hm: checkout root: none
- A built-in scanner that consults call_sites before emitting: none, which confirms the apply_registry filter has a real producer

### Mechanism traces

- **Mandate._row_shape model_validator**
  - invalid state: row.detection in {ast,guard} and (':' in detector and not parseable as <rel.py>:<identifier>) OR (status!='unenforced' and call_sites ∩ TIER1 == ∅) OR (host ref, detection=='ast', active, languages=='none')
  - producer: `plugins/arch-compliance/python/acf/loader.py:71`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:166`
- **_check_builtin contract in load_mandates**
  - invalid state: active built-in ast/guard row with detector ∉ KNOWN_DETECTORS, or id != KNOWN_DETECTORS[detector].mandate_id, or (call_sites ∩ TIER1) − contract.call_sites ≠ ∅
  - producer: `plugins/arch-compliance/python/acf/detectors/python_pack.py:67`
  - rung 3 (highest applicable 2); repairs=False
  - hardening rejected because: Every built-in scanner stamps one fixed mandate_id ... Consequence, accepted: with unique row ids, a host has at most one active row per built-in detector ... no shipped registry has such a pair (Appendix).
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:235`
- **apply_registry call_sites filter**
  - invalid state: Finding f where registry.by_id[f.mandate_id] exists but not runs_at(gate_call_sites)
  - producer: `plugins/arch-compliance/hooks/posttooluse_gate.py:254`
  - rung 2 (highest applicable 2); repairs=False
  - hardening rejected because: This filter is needed at that one sink because the built-in scanners emit findings without consulting the registry
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:321`
- **Host-file existence check (load_mandates and load_host_detector)**
  - invalid state: active host row whose resolve_under_root(repo_root, rel_path) is None or not is_file()
  - producer: `config/architecture/mandates.yml:70`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:229`
- **One host root per process refusal (_ACTIVE_ROOT)**
  - invalid state: load_host_detector called with repo_root.resolve() != _ACTIVE_ROOT in one process
  - producer: `plugins/arch-compliance/tests/test_diff_cli.py:48`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: Production callers resolve one repository per process ... In-process tests over several roots reset the loader through a test fixture (§4.6).
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:48`
- **Refuse a host root containing acf/ or acf.py**
  - invalid state: an `acf.*` import by the plugin resolves to a module under the host root instead of plugins/arch-compliance/python/acf
  - producer: `None`
  - rung 3 (highest applicable 1); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:292`
- **HostHit model validation**
  - invalid state: host hit with path failing validate_posix_rel_path, line < 1, or empty message
  - producer: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/arch_compliance/driver.py:158`
  - rung 1 (highest applicable 1); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:275`
- **_to_findings refusal of non-HostHit items and mismatched ast paths**
  - invalid state: item not isinstance HostHit, or detection=='ast' and hit.path != scanned path
  - producer: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/arch_compliance/driver.py:150-163`
  - rung 3 (highest applicable 1); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:309`
- **_call_host wrapped region and load_host_detector import handler**
  - invalid state: host module import, callable or iteration raises (SystemExit included) or returns None/str/bytes/non-iterable
  - producer: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/arch_compliance/driver.py:155`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:296`
- **make_line_lookup lazy read with errors="replace" and empty-string fallback**
  - invalid state: finding.path names a file not in file_lines whose bytes are not valid UTF-8, or which is missing/outside root
  - producer: `plugins/arch-compliance/python/acf/cli_check_diff.py:126`
  - rung 5 (highest applicable 5); repairs=True
  - hardening rejected because: an exemption token is ASCII, so a stray undecodable byte elsewhere on the line must neither crash apply_registry nor hide the token. A missing or out-of-root file yields "", which leaves the finding in place.
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:331`
- **Hook in_repo_rel_paths parallel list**
  - invalid state: rel_paths entry that is an absolute POSIX path (edited file outside repo)
  - producer: `plugins/arch-compliance/hooks/posttooluse_gate.py:245`
  - rung 5 (highest applicable 2); repairs=True
  - hardening rejected because: rel_paths keeps its current contents for the build-artifact guard.
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:362`
- **scan_host_ast_file skip on SyntaxError**
  - invalid state: changed .py file whose text fails ast.parse
  - producer: `plugins/arch-compliance/python/acf/cli_check_diff.py:125`
  - rung 5 (highest applicable 3); repairs=True
  - hardening rejected because: on SyntaxError it returns [], the convention of scan_python_file
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:312`

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
- **C19** [premise] [load-bearing]: Deferral: no shared Tier-1 dispatcher. _scan_changed and _scan_paths differ in diff scope (added lines vs whole file), path collection and file filter, so adding the same three host calls to each, rather than extracting a common dispatcher, is within ## Scoped refactor (ARCHITECTURE.md:211-215).
  - spec citation: `config/architecture/ARCHITECTURE.md:211-215`
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
- **C32** [deletion] [load-bearing]: Deleting the two _line_lookup closures (cli_check_diff.py:76-80, posttooluse_gate.py:119-123) in favour of make_line_lookup preserves their behaviour for every file already in file_lines and only adds a disk read (under the repo root, errors=replace) for files not in it.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80`
- **C33** [deletion] [load-bearing]: Deleting cli_check_diff._active_mandates and the hook's inline filters in favour of registry.active(call_sites, detector=...) changes no selection except by call_sites: for every shipped registry, the only built-in row that stops running at a gate is no-shims.hasattr leaving the PostToolUse hook (it declares [ci]).
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99`
- **C34** [deletion] [load-bearing]: Removing LLM_PROMPT_IDS from KNOWN_DETECTORS (and the import at cli_check_diff.py:21) changes behaviour only for ast/guard rows naming an LLM prompt id: load_mandates consults known_detectors only for ast/guard rows, and no other code reads KNOWN_DETECTORS for llm rows.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:21`
- **C35** [deletion] [load-bearing]: Replacing the literal mandate ids in the five scanner modules with module constants changes no emitted finding, and no test asserts on the scanner source text in a way the change would break.
  - spec citation: `None`
- **C36** [mandate] [load-bearing]: ## Fail loud: every invalid state in spec §6.1 is refused by the named component with the named error. In particular a host callable that raises, returns a generator that raises or yields an invalid HostHit while consumed, or calls sys.exit, becomes DetectorPackError because _call_host materialises the result with list(raw) inside a try catching (Exception, SystemExit); and the two broad handlers in acf.detectors.host (import failure; host callable failure) re-raise as typed errors and carry the fail-loud.bare-except-ok token with a reason, as ARCHITECTURE.md:29-30 requires.
  - spec citation: `None`
- **C37** [mandate] [load-bearing]: ## Fail loud: no active built-in ast/guard row can load with known_detectors yet never receive a finding from either Tier-1 gate: _check_builtin refuses a detector not in KNOWN_DETECTORS (LLM prompt ids are not keys), a row id that differs from the detector's stamped mandate_id, and any declared Tier-1 call site outside the detector's contract call_sites (fail_loud_ratchet: DIFF only); and Mandate._row_shape refuses an active ast/guard row with no Tier-1 site. Host rows are dispatched by both gates' host runners at any Tier-1 site.
  - spec citation: `None`
- **C38** [mandate] [load-bearing]: ## Declared, never defaulted: load_mandates requires an explicit repo_root for an active host detector row (AcfInputError otherwise, never derived), and apply_registry's new call_sites keyword has no default.
  - spec citation: `config/architecture/ARCHITECTURE.md:118-133`
- **C39** [mandate]: ## No shims: callable lookup is getattr(mod, attr, None) followed by callable() and a raise; no hasattr, and no host-detector failure has a silent fallback.
  - spec citation: `config/architecture/ARCHITECTURE.md:43-53`
- **C40** [mandate]: ## POSIX paths: HostHit.path is validated by validate_posix_rel_path (which refuses backslashes) and error messages use .as_posix().
  - spec citation: `config/architecture/ARCHITECTURE.md:55-64`
- **C41** [mandate]: ## One base exception: the design adds no exception class and uses AcfInputError, UnknownDetectorError and DetectorPackError (exceptions.py:5, :13, :29), all subclassing AcfError.
  - spec citation: `plugins/arch-compliance/python/acf/exceptions.py:5`
- **C42** [mandate]: ## One owner for host paths: acf/engine.py, acf/registry.py, acf/detectors/__init__.py and the new acf/detectors/host.py spell no config/architecture path, and the acf-mandate skill snippet takes MANDATES_REL and resolve_repo from acf.repo.
  - spec citation: `None`
- **C43** [mandate]: ## Prose names no host: the runtime messages in §4.2-§4.4 and the prose changes in §4.8 name no origin host.
  - spec citation: `config/architecture/ARCHITECTURE.md:135-143`
- **C44** [mandate]: ## Live consumers: each export in §6.2 has the named runtime caller (e.g. HostHit is used by _to_findings and imported by host code; TIER1_CALL_SITES by load_mandates; Mandate.is_active by runs_at and load_mandates).
  - spec citation: `config/architecture/ARCHITECTURE.md:153-157`
- **C45** [mandate]: ## No completeness claims: every population claim in the spec carries a re-runnable recipe (§1, §3, Appendix) or is a per-item table, as ARCHITECTURE.md:159-169 requires.
  - spec citation: `config/architecture/ARCHITECTURE.md:159-169`
- **C46** [mandate]: ## Declared text decoding: the new read_text calls (cli_check_diff.py TypeScript branch, make_line_lookup) declare encoding="utf-8", errors="replace" in make_line_lookup is permitted by that rule, and no subprocess is added.
  - spec citation: `config/architecture/ARCHITECTURE.md:171-182`
- **C47** [mandate]: ## Release discipline: because shipped skill prose changes, the version is bumped 0.2.2 -> 0.2.3 in both files ARCHITECTURE.md:186-187 names (pyproject.toml:3, plugins/arch-compliance/.claude-plugin/plugin.json:3).
  - spec citation: `config/architecture/ARCHITECTURE.md:184-194`
- **C48** [mandate]: ## Single point of definition: within the Tier-1 gates, the absolute and under-root string tests are defined once in acf.engine, row activity once in Mandate.runs_at, each built-in mandate id once in a scanner-module constant (read by both the scanner and KNOWN_DETECTORS), host loading and running once in acf.detectors.host, and line lookup once in make_line_lookup.
  - spec citation: `None`
- **C49** [mandate]: ## Scoped refactor: the consolidations (line lookup, active-row filters, citations' path helpers) touch only code paths this design changes; the shared dispatcher is a declared non-goal.
  - spec citation: `config/architecture/ARCHITECTURE.md:211-215`
- **C50** [mandate]: ## Frozen ledger format: the design changes no ledger model.
  - spec citation: `config/architecture/ARCHITECTURE.md:145-151`
- **C51** [mandate]: The design complies with the five portable governing principles at docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51 and fulfils that spec's call for project-specific detector extension points (:102, :123, :125).
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51`
- **C52** [mandate]: ## Fail loud: make_line_lookup returning [] for a missing or out-of-root file, and errors="replace" decoding, hide no failure: OSError from read_text propagates, and a missing file can only mean no exemption token exists.
  - spec citation: `config/architecture/ARCHITECTURE.md:24-41`
- **C53** [shape_fit] [load-bearing]: Mandate.runs_at and MandateRegistry.active become the single definition of 'this row runs at this gate' for the Tier-1 gates; after the change no other Tier-1 site (cli_check_diff, posttooluse_gate, enforcement, the host runners) keeps its own active-row filter.
  - spec citation: `None`
- **C54** [shape_fit] [load-bearing]: looks_absolute and resolve_under_root in acf.engine subsume citations' private helpers and are the only absolute-test and under-root test used by validate_posix_rel_path, load_mandates, load_host_detector, make_line_lookup and acf/adr/citations.py; PosixStr (adr/contract.py:129) and _WIN_DRIVE_RE (adr/contract.py:95) are ADJACENT (backslash/drive detection inside persisted ADR text), and the other path handling (posttooluse_gate.py:204, fail_loud_ratchet.py:123) resolves paths for I/O, a different responsibility.
  - spec citation: `plugins/arch-compliance/python/acf/adr/citations.py:74-76`
- **C55** [shape_fit] [load-bearing]: Building Finding from a validated HostHit in acf.detectors.host is ADJACENT to, not a partial duplicate of, the TypeScript bridge's JSON-to-Finding coercion (typescript_bridge.py:75-95), because the inputs share no format.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:75-95`
- **C56** [shape_fit] [load-bearing]: Building Finding from a HostHit is ADJACENT to the judge's _to_finding (judge.py:236-253): the judge demotes severity by confidence and admits path="<diff>" and line=0, while host findings take severity from the row and require a relative path and line >= 1, so no shared constructor is warranted.
  - spec citation: `plugins/arch-compliance/python/acf/judge.py:236-253`
- **C57** [shape_fit] [load-bearing]: acf/detectors/host.py partially duplicates no existing mechanism: nothing in the plugin today loads or executes code from a registry-supplied file path, and the loader's one-time sys.path insertion of a host root (refusing a second root and a root containing acf/ or acf.py) is ADJACENT to the hooks' own start-up insertion of the plugin's python/ directory (posttooluse_gate.py:22-26, inject_constraints.py:28-29).
  - spec citation: `None`
- **C58** [shape_fit] [load-bearing]: make_line_lookup consolidates the only two line-lookup closures passed to apply_registry; no third LineLookup implementation exists (e.g. in cli_check_llm.py, the judge, or any skill snippet) that would remain a second definition.
  - spec citation: `None`
- **C59** [shape_fit] [load-bearing]: Detector-reference validation lives in two cooperating places only, Mandate._row_shape (row-local rules, every caller) and load_mandates with known_detectors (built-in contracts and host-file existence); no other validator (the acf-mandate skill's ## Validate snippet, test_profile_drift.py, the architecture-review skill, acf-setup) independently checks detector ids or call sites in a way that would diverge.
  - spec citation: `None`
- **C60** [shape_fit]: Host dispatch in the hook reuses the hook's existing abs_path.relative_to(repo) try/except ValueError (posttooluse_gate.py:242-245) to record in-repo paths in a separate in_repo_rel_paths list, rather than adding a second in-repo test; rel_paths keeps its current contents for the build-artifact guard.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:242-245`
- **C61** [sweep] [load-bearing]: Sweep: the call-site vocabulary in use across shipped registries and docs is {ci, precommit, hook, posttooluse, audit} (config/architecture/mandates.yml; ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:104); every value except audit falls in DIFF_CALL_SITES or HOOK_CALL_SITES, and audit is read by no Tier-1 gate, so the partition misroutes no shipped row.
  - spec citation: `None`
- **C62** [sweep] [load-bearing]: Sweep: the test changes in spec §4.7 cover every existing test the design breaks: the ten apply_registry calls in test_enforcement.py, test_hooks.py:199-218 (the [ci]-only row reported by the hook), test_registry.py:30 (frozenset known_detectors), tests/test_self_host.py:23; no other existing test depends on the hook reporting a [ci]-only row, on apply_registry's old signature, on citations._looks_absolute/_escapes_repo, on KNOWN_DETECTORS containing LLM prompt ids or being a frozenset, on scanner source literals, or on load_mandates accepting an active row the new rules refuse.
  - spec citation: `None`
- **C63** [shape_fit] [load-bearing]: KNOWN_DETECTORS (Mapping of BuiltinDetector) is the single definition of which built-in detector reports to which mandate and runs at which call sites; no other place in the plugin (docs, skills, tests, profiles) keeps a second, divergent list of built-in detector ids or their mandate ids that would drift from it, other than the TypeScript rule files, whose agreement test_builtin_detectors.py pins.
  - spec citation: `None`
- **C64** [shape_fit] [load-bearing]: resolve_under_root (relative string -> contained Path) is ADJACENT to abs_path.relative_to(repo) at posttooluse_gate.py:242-245 and the ratchet walk filter at fail_loud_ratchet.py:59-62 (resolved absolute Path -> relative string): they are opposite operations, not two implementations of one.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:242-245`
- **C65** [shape_fit] [load-bearing]: _call_host is the single wrapped region for invoking host callables in both runners, and the fresh_host_loader fixture in plugins/arch-compliance/tests/conftest.py is the single reset of host-loader state; no production code path resets _ACTIVE_ROOT.
  - spec citation: `None`
- **C66** [sweep]: The prose sites in spec section 4.8 cover every shipped doc that states the PostToolUse hook scans only .py/.ts/.tsx files, that the hook reports [ci]-only rows, that detectors must be built-in ids or that the known detector union includes LLM prompt ids, or that .acf/ may be committed without noting it enables host code.
  - spec citation: `None`
- **C67** [mechanism_justification] [load-bearing]: Deferring host import to dispatch (load_mandates checks reference syntax, Tier-1 site, languages, built-in contracts and host-file existence, and imports nothing) is justified: a missing file still fails at load, an import failure or missing callable fails loud at dispatch as UnknownDetectorError caught by both gates' except tuples, and importing at load would run host code in the SubagentStart hook and acf-check-llm and import CI-only guards on every edit.
  - spec citation: `None`
- **C68** [mechanism_justification] [load-bearing]: The row-shape checks on Mandate (host-reference syntax, a Tier-1 site, host ast languages) together with the per-detector BuiltinDetector contracts (known id, matching mandate_id, declared Tier-1 sites within the contract's call_sites) are sufficient to prevent an active ast/guard row that loads with known_detectors yet is run by neither acf-check-diff (DIFF_CALL_SITES) nor the hook (HOOK_CALL_SITES), or whose findings land on no row.
  - spec citation: `None`
- **C69** [mechanism_justification] [load-bearing]: Refusing a second host root in one process (AcfInputError) rather than evicting the old root is justified: every production caller resolves one repository per process, so the refusal never fires in production, and the only multi-root producer (in-process tests) is handled by the test-only fresh_host_loader fixture; no repair mechanism lives in production code.
  - spec citation: `None`
- **C70** [mechanism_justification] [load-bearing]: Declaring, per built-in detector, the mandate id it reports to and the call sites where a gate runs it (BuiltinDetector in KNOWN_DETECTORS) is justified over the alternatives: the scanners stamp fixed mandate ids and run at fixed gates, so the contract records an existing fact rather than adding a capability; the accepted cost (at most one active row per built-in detector) affects no shipped registry.
  - spec citation: `None`
- **C71** [mechanism_justification]: Moving the row-local rules onto a Mandate model_validator (rather than keeping them in load_mandates) is justified because it makes the SubagentStart hook, acf-check-llm and any direct Mandate construction reject the same malformed rows as the gates, with no caller change since each already handles AcfInputError.
  - spec citation: `None`
- **C72** [mechanism_justification]: Parsing a Python file once and sharing the tree across every host ast detector on it is justified by avoiding N parses per file; built-in scanners keep their own parses unchanged.
  - spec citation: `None`
- **C73** [mechanism_justification] [load-bearing]: Having host callables return HostHit (path, line, message) and building Finding in the runner from the mandate row, rather than accepting Finding and overwriting fields, is justified because apply_registry matches findings to rows by mandate_id (enforcement.py:37-53) and a host-supplied mandate_id/detector/severity could otherwise attach a finding to the wrong row.
  - spec citation: `None`
- **C74** [mechanism_justification] [load-bearing]: Treating the host's own pre-commit/CI invocation of acf-check-diff as its opt-in to running host code, and gating only the automatic hooks on .acf/enabled, is justified because .acf/ is gitignored and CI would otherwise be disabled; a user who runs acf-check-diff manually in an untrusted checkout is the residual case the design accepts.
  - spec citation: `.gitignore:8`
- **C75** [mechanism_justification] [load-bearing]: The call_sites filter added to apply_registry is needed in addition to the scanners' registry.active(call_sites) selection, because some built-in scanners emit findings by detector id without consulting the registry's call_sites, so without the filter a finding for a row not declared at this gate would survive. (The spec states the filter but gives no reason it is not redundant.)
  - spec citation: `None`
- **C76** [implementability] [load-bearing]: Mandate (registry.py:14-27) is a Pydantic BaseModel exposing every field the design reads: id, severity, status, detection, detector, call_sites (list[str]), languages (Literal including 'none'), and params (dict or None); adding an @property is_active and a plain method runs_at to it, and a method active to MandateRegistry, is compatible with its model_config.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:14-27`
- **C77** [implementability] [load-bearing]: Finding (acf/finding.py) can be constructed as Finding(mandate_id=, severity=Severity(mandate.severity), path=, line=, message=, detector=, detection=): those are its fields, Severity is constructible from Mandate.severity's value, and no other required field is missing.
  - spec citation: `None`
- **C78** [implementability] [load-bearing]: apply_registry (enforcement.py) looks up each finding's row via registry.by_id, drops it on the status check at :47 (replaceable by runs_at), and handles exemptions and severity at :49-52 using a LineLookup type that make_line_lookup can return.
  - spec citation: `plugins/arch-compliance/python/acf/enforcement.py:47`
- **C79** [implementability] [load-bearing]: cli_check_diff.py has the hook points the design names with the needed names in scope: load at :70 inside a try whose except tuple at :72 lists AcfInputError, UnknownDetectorError and DetectorPackError (and wraps both load and scan); lookup and apply_registry at :76-82; in the .py branch after scan_fsm_writes (:140-150) repo, text, posix, lines and registry; in the .ts/.tsx branch (:151-156) a read that can bind text; and after the ratchet loop (:168-182) the changed-file list.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:72`
- **C80** [implementability] [load-bearing]: posttooluse_gate.py has the hook points the design names: deferred imports at :91-104, the load try at :106-110, the scan try at :113-117 (whose except can be widened to AcfInputError, DetectorPackError, UnknownDetectorError), lookup/apply_registry at :119-125, inline filters at :229-236 and :284-286, the relative_to with ValueError fallback at :242-245 where an in_repo_rel_paths list can be recorded, the build-artifact loop at :284-294, and text and rel in scope in the .py and TypeScript branches of _scan_paths.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:113-117`
- **C81** [implementability] [load-bearing]: Host-detector failures reach an existing fail-loud handler in both gates, never a traceback: dispatch-time loading raises UnknownDetectorError or AcfInputError (second root, acf shadow), and _call_host wraps every exception from the call and from materialising its result (generator bodies and HostHit ValidationError included) plus SystemExit as DetectorPackError; acf-check-diff's except at :72 and the hook's widened scan except catch all three.
  - spec citation: `None`
- **C82** [implementability] [load-bearing]: load_host_detector's design is implementable as stated: a module-level _ACTIVE_ROOT and _MODULE_CACHE, inserting the root at sys.path[0] once, a module name derived from sha256(rel_path), registering in sys.modules before exec_module and removing it on failure, and refusing a root containing acf/ or acf.py so a host package cannot shadow the plugin's acf imports; and the conftest fresh_host_loader fixture (reset both globals, restore sys.path, drop added sys.modules keys) isolates in-process tests over several tmp roots, including test_diff_cli.py's in-process main() calls.
  - spec citation: `None`
- **C83** [implementability] [load-bearing]: Registering the module in sys.modules under its name before spec.loader.exec_module(mod) is what lets a host module define a @dataclass under `from __future__ import annotations` (dataclasses resolves sys.modules[cls.__module__]); importlib.util.spec_from_file_location with a synthetic name supports this.
  - spec citation: `None`
- **C84** [implementability] [load-bearing]: The imports the design adds are cycle-free and allowed: acf.registry imports acf.engine, dataclass and Mapping, and nothing from acf.detectors; acf.detectors/__init__ imports acf.registry (BuiltinDetector, call-site sets) and the scanner modules' constants without a cycle; acf.cli_check_diff re-exports KNOWN_DETECTORS from acf.detectors; acf.detectors.host imports registry, finding, engine and exceptions; acf/adr/citations.py importing acf.engine is permitted by test_adr_import_graph.py; and the hook's new deferred imports (from acf.detectors, not acf.cli_check_diff) do not reach acf.adr or acf.judge.
  - spec citation: `plugins/arch-compliance/tests/test_adr_import_graph.py:70-76`
- **C85** [implementability] [load-bearing]: load_mandates today loads rows via load_model_file(path, Mandate, subject='mandates file', fmt='yaml', many=True) returning a list of Mandate, and builds MandateRegistry(mandates=..., source_path=path.as_posix()), so the §4.2 body is a drop-in extension of the existing function.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:48-64`
- **C86** [implementability]: plugins/arch-compliance/tests/test_repo_paths.py:47-48 pins the text of posttooluse_gate.py's docstring line :11 and not :12, so rewording :12 and keeping :11 verbatim breaks no test.
  - spec citation: `plugins/arch-compliance/tests/test_repo_paths.py:47-48`
- **C87** [implementability] [load-bearing]: config/architecture/mandates.yml:60 declares fail-loud.bare-except-ok as the exemption token for the fail-loud.bare-except detector, and that detector honours it on an `except Exception` line, so the two handlers in acf.detectors.host pass the repository's own gate.
  - spec citation: `config/architecture/mandates.yml:60`
- **C88** [implementability]: acf/engine.py already defines contains_backslash and is stdlib-only, so adding looks_absolute, resolve_under_root and validate_posix_rel_path with `import re` and `from pathlib import Path` keeps it stdlib-only and gives validate_posix_rel_path its backslash test without a new dependency.
  - spec citation: `plugins/arch-compliance/python/acf/engine.py`
- **C89** [implementability] [load-bearing]: The new tests are implementable against the shipped files: test_builtin_detectors.py can parse the README.md detector table (:66-74) for detector ids and mandate ids and read mandate_id values from emptyCatch.ts:23 and explicitAny.ts:15; and the test_registry.py cases (a fail_loud_ratchet row declaring hook, a fail_loud_bare_except row with another id, an ast row naming an LLM prompt id, a module that raises at import not imported by load_mandates) can be expressed as inline YAML registries like the existing :24 and :35 rows.
  - spec citation: `None`
