# Adversarial design review — full detail

Spec: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md` @ `51b5df51ac465ad5cfb102cc125109936b71a452`
Kinds: defect, feature
Outcome: **BLOCKED**
Claims: 126 · Reviewers: 4 · Converged: 0

## Blocking reasons

- load-bearing claim C76 (shape_fit) is REFUTED: I re-ran the recipe as a Grep over hooks/ and python/. It prints exactly posttooluse_gate.py:204 and :243, citations.py:76, and fail_loud_ratchet.py:60 and :123. A wider search (is_relative_to, isabs, commonpath, '..') found only citations.py:76. The listed instances are right. The 'one implementation' claim is not. validate_posix_rel_path (spec :125) decides containment lexically: it refuses absolute paths and '..'. It is the only containment decision a HostHit.path ever gets (spec :331). _to_findings emits the Finding whatever the path resolves to (spec :408). scan_host_guards calls file_under_root only to fetch exemption lines, and maps a path that resolves outside the root to [] while keeping the finding (spec :413). So 'does this host-supplied path lie in the repo' has a lexical answer for host hits and a resolved answer for registry rows and harness paths. The ratchet walk is a second gap: rglob under a contained root (fail_loud_ratchet.py:58) follows in-repo directory symlinks on Python 3.11/3.12, and its keys are contained only lexically. The parse_python half of the claim holds: the only non-test ast.parse/SyntaxError sites are the four scanners.

## Absorptions

- PARTIAL_OVERLAP: 'acf.engine.validate_posix_rel_path' shares responsibility 'decide whether an outside path string lies inside the repository' with plugins/arch-compliance/python/acf/adr/citations.py:74-76 — Keep resolve_under_root as the only containment predicate. Make validate_posix_rel_path a pure shape check (POSIX, normalized), and have HostHit consumers that need containment (scan_host_guards) refuse or flag a hit for which resolve_under_root returns None instead of keeping it with [] lines.
- SUBSUMED: 'acf.engine.resolve_under_root / file_under_root' shares responsibility 'decide containment of a path string in the root' with plugins/arch-compliance/hooks/posttooluse_gate.py:204 — The hook's is_absolute join and the relative_to/ValueError fallback (:242-245) are deleted, as are the ratchet's joins (:46, :122-124) and its walk except (:59-62). Each site keeps only relative_to(...).as_posix().
- PARTIAL_OVERLAP: 'ratchet load_baseline after the file_under_root switch' shares responsibility 'load, parse and refuse a JSON input file' with plugins/arch-compliance/python/acf/loader.py:43-77 — Give the ratchet baseline a Pydantic model loaded through load_model_file, as acf/baseline.py:86 already does, and map AcfInputError to DetectorPackError at the ratchet boundary. The missing-file, JSON and shape branches of fail_loud_ratchet.py:77-98 collapse into it.
- IDENTICAL: 'count_bare_excepts (rewritten to use parse_python)' shares responsibility 'decide whether an except handler is bare or broad' with plugins/arch-compliance/python/acf/detectors/python_pack.py:77-82 — count_bare_excepts calls python_pack._is_bare_or_exception (made public) instead of restating it at fail_loud_ratchet.py:31-34.
- PARTIAL_OVERLAP: "scan_host_guards file_lines fill (errors='replace')" shares responsibility "read a file's lines for exemption lookup" with plugins/arch-compliance/python/acf/cli_check_diff.py:125-126 — One acf.enforcement helper reads lines for the exemption check under one declared decoding policy. The gates' .py and .ts reads (cli_check_diff.py:125, :152; posttooluse_gate.py:251) and scan_host_guards consume it.
- PARTIAL_OVERLAP: 'load_host_detector _MODULE_CACHE' shares responsibility 'record which host module is already loaded' with tests/test_check_installed_skills.py:15-18 — Use sys.modules[name] (the name is a pure function of rel_path) as the only cache, and drop _MODULE_CACHE. The except branch and the fresh_host_loader fixture then manage one store.
- SUBSUMED: 'Mandate.runs_at / MandateRegistry.active' shares responsibility 'decide whether a row runs at a gate' with plugins/arch-compliance/python/acf/enforcement.py:47 — cli_check_diff._active_mandates (:94-99), the hook's inline filters (:229-236, :284-286) and apply_registry's status check (:47) all call runs_at.
- PARTIAL_OVERLAP: 'KNOWN_DETECTORS (BuiltinDetector.call_sites)' shares responsibility 'declare where each built-in detector runs' with plugins/arch-compliance/python/acf/cli_check_diff.py:168 — The table declares and each gate's dispatch decides. The §4.7 contract-against-dispatch test is the agreed tie, and both stay as two coupled owners.
- SUBSUMED: 'TS_MANDATE_IDS' shares responsibility 'define the TypeScript detector-to-mandate ids' with plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23 — The bridge stamps the Python value and refuses a Node literal that differs, so the Node literal becomes a checked echo.
- IDENTICAL: 'make_line_lookup' shares responsibility "look up a finding's source line" with plugins/arch-compliance/hooks/posttooluse_gate.py:119-123 — Both closures (cli_check_diff.py:76-80 and posttooluse_gate.py:119-123) are deleted and both gates call make_line_lookup.

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:58; plugins/arch-compliance/python/acf/registry.py:60-63; plugins/arch-compliance/tests/test_registry.py:20-30`
- reasoning: At line 58, load_mandates skips any row whose status is not 'enforced'. At 60-63 it raises UnknownDetectorError only when an enforced ast/guard row's detector is not in known_detectors. test_registry.py:20-30 pins this with an enforced ast row and an unknown detector.

#### C2 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:25; plugins/arch-compliance/python/acf/judge.py:29-36; plugins/arch-compliance/python/acf/registry.py:60`
- reasoning: Line 25 is the closed union. git grep KNOWN_DETECTORS -- plugins tests prints only reads (cli_check_diff:70, SKILL.md, test_profile_drift, test_self_host) and no extension. LLM_PROMPT_IDS holds 4 llm ids, so an ast row naming one passes the membership check at registry.py:60. No scanner dispatches on those ids (cli_check_diff.py:112-182).

#### C3 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:112-182; plugins/arch-compliance/hooks/posttooluse_gate.py:229-294`
- reasoning: Both loops call only imported built-in scanners, chosen by exact detector-id equality (_active_mandates :94-99; hook :229-236, :284-286). I ran the git grep for importlib|import_module|spec_from_file_location|exec_module over plugins/arch-compliance/python and hooks, and it printed nothing.

#### C4 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:106-110; plugins/arch-compliance/python/acf/exceptions.py:5; plugins/arch-compliance/python/acf/exceptions.py:13`
- reasoning: The try around load_mandates catches only AcfInputError. UnknownDetectorError(AcfError) is a sibling of AcfInputError, not a subclass. The hook's scan except at :115 catches only DetectorPackError.

#### C5 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:21; plugins/arch-compliance/python/acf/enforcement.py:47`
- reasoning: call_sites is list[str]. The git grep call_sites recipe prints registry.py:21 and ledger.py:42,83 (surface_call_sites) only. The gates filter on detector and status, and apply_registry filters on status only.

#### C6 — SURVIVED
- evidence: `config/architecture/mandates.yml:70; plugins/arch-compliance/tests/fixtures/mandates_valid.yml:18; plugins/arch-compliance/tests/test_hooks.py:198-216; plugins/arch-compliance/hooks/posttooluse_gate.py:254`
- reasoning: The row declares [ci]. The hook runs scan_python_file on every edited .py file, and apply_registry keeps the finding whatever its call_sites. The test seeds the fixture, whose hasattr row is also [ci], and asserts no-shims.hasattr appears in the hook context.

#### C7 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_import_graph.py:70-76; plugins/arch-compliance/python/acf/adr/contract.py:20; plugins/arch-compliance/hooks/posttooluse_gate.py:92-95; plugins/arch-compliance/python/acf/engine.py:6-8`
- reasoning: The test asserts only that the literal 'acf.adr' is absent from the two hook files, and its docstring states the intent. The hook imports acf.enforcement and acf.registry. contract.py imports acf.engine.contains_backslash, and engine imports only pathlib.

#### C8 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:214-218; plugins/arch-compliance/python/acf/judge.py:229-234`
- reasoning: run_judge selects detection=='llm' rows and uses status=='enforced' only for has_enforced. It reviews every llm row it is given and uses no Tier-1 filter.

#### C9 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:28; plugins/arch-compliance/hooks/posttooluse_gate.py:72-81; plugins/arch-compliance/tests/test_repo_paths.py:81-108`
- reasoning: Before the marker check the only acf import is acf.repo (stdlib only; acf/__init__.py is empty). The registry import is deferred to :91-95, after the exit-0 branch. test_repo_paths runs both hooks without the marker, with pydantic and yaml poisoned.

#### C10 — SURVIVED
- evidence: `.gitignore:8; .github/workflows/ci.yml:40; plugins/arch-compliance/python/acf/cli_check_diff.py:63-74`
- reasoning: .acf/ is ignored. CI runs python -m acf.cli_check_diff, and main() never reads ENABLED_REL.

#### C11 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:103-107; plugins/arch-compliance/python/acf/loader.py:70-73; plugins/arch-compliance/python/acf/cli_check_llm.py:54`
- reasoning: inject_constraints catches AcfInputError. A model_validator raising a non-ValueError exception propagates unwrapped: I checked with pydantic 2.13.3, and a custom Exception raised in an after-validator surfaced with its own type. cli_check_llm calls load_mandates with no handler, so an AcfInputError already exits non-zero there.

#### C12 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:91-92; plugins/arch-compliance/python/acf/cli_check_llm.py:10-13`
- reasoning: Both entry points import only acf.registry, loader, judge, finding and repo. Under the design, registry imports acf.engine and nothing from acf.detectors (spec §4.2), so neither can reach acf.detectors.host. load_mandates as written in §4.2 only stats the host file.

#### C13 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/baseline.py:78; config/architecture/adr.yml`
- reasoning: git ls-files config shows only ARCHITECTURE.md, adr.yml and mandates.yml, and no architecture-review host config. baseline.py is absent from the spec's §3 scope table and from §4.9.

#### C14 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:20; plugins/arch-compliance/python/acf/registry.py:24`
- reasoning: I parsed hm:config/architecture/mandates.yml at b652fab05: 48 rows, none with a languages or arch_anchor key. Both fields are required, with no defaults.

#### C15 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/arch_compliance/driver.py:150-161; plugins/arch-compliance/python/acf/cli_check_diff.py:110`
- reasoning: At b652fab05 the driver catches SyntaxError, raises in range mode, and otherwise appends a WARN with exc.lineno or 0. Its guards receive the diff's changed records (cf.content). acf-check-diff collects every changed path, which the design passes to scan_guard.

#### C16 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:198-200; plugins/arch-compliance/python/acf/cli_check_diff.py:115-156; plugins/arch-compliance/hooks/posttooluse_gate.py:238-282`
- reasoning: The diff loop uses git-changed paths, added_lines and a per-suffix branch. The hook loop uses harness paths, added_lines=None, _CODE_SUFFIXES, and rel_paths for every path. They differ in scope, collection and filter, as claimed. The design puts host selection, load, call and wrap in one module.

#### C17 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:50-53; plugins/arch-compliance/python/acf/detectors/fsm_guard.py:36-39; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:23-26`
- reasoning: Each wraps ast.parse in try/except SyntaxError, returning [] in three of them and 0 in count_bare_excepts.

#### C18 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:70; plugins/arch-compliance/tests/test_profile_drift.py:24; plugins/arch-compliance/tests/test_registry.py:30; tests/test_self_host.py:23`
- reasoning: I ran the recipe and the output matches the list exactly, including SKILL.md:95 and :141, architecture-review SKILL.md:62 and test_registry 10,17,30,47,57. Only the five named sites pass known_detectors. test_profile_drift passes it without repo_root, but the profiles have no host rows.

#### C19 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:125; plugins/arch-compliance/python/acf/cli_check_diff.py:82; plugins/arch-compliance/tests/test_enforcement.py:54`
- reasoning: git grep apply_registry( prints exactly those sites plus the def at enforcement.py:37.

#### C20 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; plugins/arch-compliance/hooks/posttooluse_gate.py:231; plugins/arch-compliance/python/acf/enforcement.py:47`
- reasoning: Both recipes reproduce the listed lines. The wider .status recipe adds registry.py:58, judge.py:218 and inject_constraints.py:158, and the last is display-only in _render_constraints.

#### C21 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/build_artifacts.py:31; plugins/arch-compliance/python/acf/detectors/python_pack.py:67; plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23; plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15; plugins/arch-compliance/python/acf/enforcement.py:46`
- reasoning: Each detector stamps one literal id: python_pack 67/97/144/172, facade 69, ratchet 132, fsm 59, and the TS literals. The bridge copies item['mandate_id']. apply_registry looks rows up by finding.mandate_id. See the unanchored finding for the converse case.

#### C22 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:168-182; plugins/arch-compliance/hooks/posttooluse_gate.py:213-295`
- reasoning: The hook never imports or calls scan_ratchet. Python, TS, facade, fsm and build-artifact dispatch appear in both gates at the §4.3 line numbers (cli 127, 128-150, 153-156, 158-166; hook 254, 255-277, 279-282, 284-294).

#### C23 — SURVIVED
- evidence: `config/architecture/mandates.yml:5-130; plugins/arch-compliance/tests/fixtures/mandates_valid.yml:1-32; plugins/arch-compliance/tests/test_diff_cli.py:71-81; plugins/arch-compliance/tests/test_registry.py:23-25; plugins/arch-compliance/tests/test_hooks.py:223-224`
- reasoning: I parsed every shipped registry and fixture. Every active ast/guard row's id equals its detector's stamped id. Every active row declares ci, and all but hasattr also declare hook, which the TIER1 contract covers. The ratchet rows are unenforced, and no row uses a host ref. Inline rows: test_diff_cli bare-except [ci, hook]; test_registry 'x'/not_a_real_detector, which raises UnknownDetectorError first; a manual row; test_judge an unenforced llm row. The only fixture edit, in test_hooks, flips rows to unenforced.

#### C24 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/loader.py:70-73; plugins/arch-compliance/python/acf/registry.py:33-41; plugins/arch-compliance/tests/test_enforcement.py:19-30; plugins/arch-compliance/tests/test_judge.py:41-52; plugins/arch-compliance/tests/test_template.py:73-84`
- reasoning: The loader converts only ValidationError, and a probe confirmed that a custom exception escapes a pydantic after-validator unwrapped. _unique_ids relies on the same propagation through direct MandateRegistry construction. The test rows are ast with call_sites ['ci'] and no colon in the detector, or llm, which _row_shape skips.

#### C25 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:91-112; plugins/arch-compliance/tests/test_profile_drift.py:7-24; tests/test_self_host.py:14-23; config/architecture/ARCHITECTURE.md:226-228`
- reasoning: Each user imports the name, passes it to load_mandates, calls sorted() on it (keys of a Mapping), or names it in prose. A re-export keeps all of these working. test_registry.py:30 is the only frozenset literal.

#### C26 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:63; plugins/arch-compliance/hooks/posttooluse_gate.py:65; plugins/arch-compliance/hooks/hooks.json`
- reasoning: Each main resolves one repo. hooks.json runs posttooluse_gate.py as a fresh command per Write/Edit event.

#### C27 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:16-22; plugins/arch-compliance/python/acf/detectors/__init__.py:11-28; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:14; plugins/arch-compliance/python/acf/judge.py:29-36`
- reasoning: 3 python_pack ids, 4 guard ids, 2 TS ids and 4 LLM ids make 13; without the LLM ids, 9.

#### C28 — SURVIVED
- evidence: `config/architecture/mandates.yml:132-142; plugins/arch-compliance/python/acf/judge.py:29-36; plugins/arch-compliance/skills/acf-mandate/SKILL.md:56`
- reasoning: The census shows active llm rows soft.fail-loud (llm_fail_loud, partial) in config and python-service, and soft.react-boundaries (partial) in react-app, all in LLM_PROMPT_IDS. test_diff_cli has no llm rows, and test_judge.py:390 is unenforced.

#### C29 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:349-370; plugins/arch-compliance/python/acf/cli_check_diff.py:72`
- reasoning: In the design code, exec_module and getattr sit in one try. On failure the module is popped only when the cache does not hold it, so a failed exec drops it and a failed lookup on a cached module keeps it. getattr's default suppresses only AttributeError. :72 already catches UnknownDetectorError, and the scan call runs inside that try.

#### C30 — SURVIVED
- evidence: `pyproject.toml:5; C:/Program Files/KiCad/9.0/bin/Lib/pathlib.py:987-1005; C:/Python313/Lib/pathlib/__init__.py`
- reasoning: requires-python is >=3.11. KiCad bundles a 3.11 stdlib whose Path.resolve non-strict stats the result and raises RuntimeError('Symlink loop') on ELOOP. The 3.13 resolve is plain os.path.realpath(strict=False), which raises nothing. The design maps RuntimeError to None, and the callers treat None as missing or unresolved.

#### C31 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:82-95; plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23-28; plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15-22`
- reasoning: Finding construction sits in the try whose except (KeyError, TypeError, ValueError) re-raises DetectorPackError, so a dict KeyError and a raised ValueError are both converted. The Node rules emit fail-loud.empty-catch/empty_catch and no-shims.explicit-any/explicit_any, which equal the proposed mapping.

#### C32 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:22-28; pyproject.toml:19-20; .github/workflows/ci.yml:40; C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/metadata_facade_guard.py:66`
- reasoning: The hook inserts python/ at index 0 and imports acf.repo first. The console script entry is acf.cli_check_diff:main. CI runs -m from the checkout root. HM line 66 is 'from scripts.ci.arch_compliance.facade_sinks import (', and HM's scripts/__init__.py exists, so the import resolves against the host root.

#### C33 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:29-61; C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/run_guards.py:107-130; C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/run_guards.py:317-321`
- reasoning: acf-check-diff has only --mode, --base, --repo, --mandates and --json. At b652fab05, run_guards refuses an unknown site (107-111), filters with 'site not in entry.call_sites' (116), refuses an empty selection (126-130), and --site defaults to 'ci'.

#### C34 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:126; plugins/arch-compliance/python/acf/cli_check_diff.py:152; plugins/arch-compliance/hooks/posttooluse_gate.py:248-252; plugins/arch-compliance/python/acf/detectors/build_artifacts.py:27-34`
- reasoning: file_lines is filled only in the .py and .ts/.tsx branches. The ratchet (:135) and build-artifact (:34) findings use line 1. A staged dist/x.py goes through the .py branch, so its lines are keyed by its git path.

#### C35 — SURVIVED
- evidence: `config/architecture/mandates.yml:11-124; plugins/arch-compliance/tests/fixtures/mandates_valid.yml:7-29`
- reasoning: No *.yml contains 'precommit'. The census of ast/guard rows declaring ci gives 9/7/3/3, as stated. acf-check-diff today runs every active row regardless of site, so adding precommit to every ci row preserves the selection.

#### C36 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:389-397; pyproject.toml:7`
- reasoning: Probe with pydantic 2.13.3 on an equivalent frozen model: normal validation of a str subclass, int subclass, IntEnum and even bool for line all yield exact str/int in __dict__. So _revalidate accepts genuine hits, and its exact-type check (type(True) is bool) refuses model_construct values. Older pydantic>=2.0 releases were not checked; a difference there would fail loud, not silently.

#### C37 — SURVIVED
- evidence: `C:/Python313/Lib/pathlib/_abc.py:31; C:/Python313/Lib/pathlib/_abc.py:476-491; C:/Program Files/KiCad/9.0/bin/Lib/pathlib.py:1261-1273; plugins/arch-compliance/hooks/posttooluse_gate.py:239`
- reasoning: On 3.11 and 3.13, is_file ignores ENOENT, ENOTDIR, EBADF and ELOOP and re-raises any other OSError. A loop on 3.11 is RuntimeError in resolve, which the design catches. Each §4.2/§4.4/§4.9 caller wraps OSError. The hook's _collect_paths is called at :112 outside any try, so there an OSError is a traceback, as at :239 today, which the claim states.

#### C38 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/host.py:24-25; docs/design/ADR_GATE_HOST_CONTRACT.md:295-302`
- reasoning: The fields are PosixStr min_length=1, and the contract quote is present. The spec mentions the fields only at its §5.2 ADJACENT row and changes nothing there.

#### C39 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:122-124; plugins/arch-compliance/tests/test_portable_guards.py:100-107; plugins/arch-compliance/python/acf/cli_check_diff.py:72`
- reasoning: The test creates tmp_path/'pkg' (:102) and calls scan_tree(roots=['pkg']). The shipped baseline and roots values are relative POSIX with no '..'. An absolute in-root string survives because base/abs gives abs. DetectorPackError is in the :72 tuple. The shipped baseline file is absent here, but the row is unenforced, as today.

#### C40 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/genre_conditional_guard.py:32-40`
- reasoning: At b652fab05, a plain @dataclass Finding(path_name, line_no, line_text, reason) has __str__ calling self.line_text.strip(). With line_text=None, str(ValueError(obj)) goes through BaseException.__str__ into obj.__str__ and raises AttributeError.

#### C41 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:375-386`
- reasoning: list(raw) runs inside the try before any _revalidate, so the iterator is exhausted, which runs its finally, or raises from within the try. No live generator remains when an item is later refused.

#### C42 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_diff_cli.py:102-108; plugins/arch-compliance/tests/test_diff_cli.py:84-90`
- reasoning: Every other main() test uses the fixture (active rows) or the enforced _BARE_EXCEPT_ROW. test_missing_mandates_fails_loud fails at load. No other test imports cli_check_diff.main. bad.py contains no hasattr. This holds if the test passes --call-site ci, since a [ci] row would not select under precommit.

#### C43 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:203-209; plugins/arch-compliance/hooks/posttooluse_gate.py:239-245; plugins/arch-compliance/python/acf/repo.py:40-44`
- reasoning: repo is always resolved. (repo.resolve()/raw).resolve() equals today's join for both relative and absolute raw strings, so in-repo keys are unchanged. Only resolved paths outside repo (today keyed absolute) are dropped. The recipe grep for outside|out_of_repo|absolute in test_hooks.py prints nothing, and all test paths are under the seeded repo.

#### C44 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:57-58; config/architecture/mandates.yml:140`
- reasoning: :57 says partial still gates, and :58 advises partial for a missing detector or prompt. The only partial rows (soft.fail-loud, soft.react-boundaries) name existing prompt ids. Decision 3 and §4.8 record the consequence and the upgrade note. The skill's :122 ('often unenforced/partial' for guard rows) is also in the §4.8 rewrite list.

#### C45 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:47; plugins/arch-compliance/python/acf/registry.py:58; plugins/arch-compliance/python/acf/cli_check_diff.py:98`
- reasoning: Partial rows pass the gate filters and apply_registry. load_mandates' check skips them. Nothing dispatches a non-built-in id.

#### C46 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:107; plugins/arch-compliance/hooks/posttooluse_gate.py:254`
- reasoning: load_mandates(mandates_path) is called with no known_detectors. 'Zero findings' holds unless the row's id coincides with a built-in stamped id, since scan_python_file and scan_typescript_file run unconditionally (see the unanchored finding). That edge does not affect the validation defect.

#### C47 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80; plugins/arch-compliance/hooks/posttooluse_gate.py:119-123; plugins/arch-compliance/python/acf/enforcement.py:49-50`
- reasoning: The two closures are token-identical and read only file_lines, which is filled for code suffixes only. A missing key yields ''.

#### C48 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/citations.py:49-51; plugins/arch-compliance/python/acf/adr/citations.py:74-76; plugins/arch-compliance/python/acf/adr/citations.py:161-167`
- reasoning: The grep finds only the defs and the two call sites, and no test imports them. The old regex requires [\\/] after the drive letter while the new one does not, which changes only drive-relative strings. Two-letter prefixes such as 'hm:' match neither. _escapes_repo raised on a loop on 3.11 (KiCad pathlib.py:987-1005), and the new helper returns None.

#### C49 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; config/architecture/mandates.yml:70; plugins/arch-compliance/profiles/python-service/mandates.yml:18`
- reasoning: The census shows every active built-in row declares [ci, hook] except no-shims.hasattr ([ci]) in config, python-service and the fixture. The ratchet row is [ci] and unenforced, and the hook never runs the ratchet.

#### C50 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:60; plugins/arch-compliance/python/acf/cli_check_diff.py:21`
- reasoning: The membership test is gated on detection in {ast, guard}. The KNOWN_DETECTORS grep shows no llm-row consumer in code. The import at :21 is used only at :25 today.

#### C51 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_repo_paths.py:53-71; plugins/arch-compliance/tests/test_adr_code_portability.py:14`
- reasoning: The only tests that read plugin source text scan for config.architecture, read acf/adr files, or read the hook files. None reads scanner modules for mandate-id literals, and constants with the same value emit identical findings.

#### C52 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:430-436`
- reasoning: make_line_lookup's body is identical to the closures. At a338cad no host guards exist, so file_lines is unchanged.

#### C53 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/__init__.py:9-34; plugins/arch-compliance/python/acf/detectors/python_pack.py:16; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:14; plugins/arch-compliance/tests/test_typescript_pack.py:6`
- reasoning: The grep output equals the spec's list. No other frozenset of built-in ids exists in python/. The only other site is test_registry.py:30, which §4.7 rewrites. The proposed TS_MANDATE_IDS keys feed KNOWN_DETECTORS rather than duplicating it.

#### C54 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/facade_sinks.py:24-25; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:46; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:88-90; plugins/arch-compliance/python/acf/detectors/build_artifacts.py:16; plugins/arch-compliance/python/acf/detectors/build_artifacts.py:23`
- reasoning: Results are equivalent rather than literally equal. When allowlist_globs is absent or null the gates pass [] where the default is None, but 'allowlist_globs or []' treats them alike. atomic_is_sink is only truth-tested, and iterating the raw path_prefixes value matches iterating list(value).

#### C55 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:23-26`
- reasoning: git grep for SyntaxError|ast.parse|compile( over python and hooks finds only the four scanner sites (the compile( hits are re.compile).

#### C56 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:45-62; plugins/arch-compliance/tests/test_portable_guards.py:107`
- reasoning: rglob yields paths lexically under the search root. A search root that is resolved and is_relative_to(root) makes path.relative_to(root) total. The git grep for scan_tree finds only scan_ratchet:126 and the test.

### Unanchored findings

- **important**: A host ast/guard row, or any llm/grep/manual row, whose id equals a built-in stamped mandate_id still receives that built-in's findings. scan_python_file and scan_typescript_file run unconditionally on every changed file, and apply_registry matches only by mandate_id. _check_builtin covers only non-host ast/guard rows, so the design neither refuses nor states this.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:127`
- **advisory**: The claim that acf-check-diff's argument defaults equal the scanners' signature defaults is equivalence, not equality: absent allowlist_globs is passed as [] against a default of None, harmless only because facade_sinks.py:46 iterates 'allowlist_globs or []'.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:136`
- **advisory**: The shipped fail-loud.ratchet baseline config/architecture/fail_loud_ratchet.json does not exist in this repository. It is harmless while the row is unenforced, but any upgrade note that tells hosts to enable the ratchet should say the baseline must be committed first.
  - evidence: `config/architecture/mandates.yml:97`

### Looked for but did not find

- any dynamic import (importlib, import_module, spec_from_file_location, exec_module) under plugins/arch-compliance/python or hooks
- any code reading Mandate.call_sites under plugins/arch-compliance/python or hooks
- any *.yml declaring precommit in this repository
- any test in test_hooks.py passing an out-of-repo path to the PostToolUse gate
- any other caller of cli_check_diff.main besides test_diff_cli.py
- any Python parse-and-skip site besides the four scanners
- any test reading scanner module source text for mandate-id literals
- any partial row in shipped or fixture registries naming a non-existent detector or prompt id
- any HM row carrying languages or arch_anchor at b652fab05
- a second frozenset of built-in detector ids elsewhere in plugins/arch-compliance/python

## compliance

### Claim verdicts

#### C57 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:29-30; plugins/arch-compliance/python/acf/detectors/python_pack.py:77-82; config/architecture/mandates.yml:60; plugins/arch-compliance/python/acf/cli_check_diff.py:69-74; plugins/arch-compliance/python/acf/detectors/fsm_guard.py:29-34`
- reasoning: The doctrine forbids bare/broad handlers 'that swallow errors ... unless explicitly exempted with a reason' (:29-30). In the design the load and call handlers re-raise everything except KeyboardInterrupt as UnknownDetectorError or DetectorPackError, so they swallow nothing. Only _describe swallows, and only a failure to format; it returns a constant message inside the typed error, which is still raised, and carries the registry's real token fail-loud.bare-except-ok (mandates.yml:60) with a reason. The shipped detector matches only bare or `Exception` handlers (python_pack.py:77-82), so `except BaseException` is not flagged; the token is still the doctrine's exemption mechanism. acf-check-diff's existing except tuple (cli_check_diff.py:72) already covers AcfInputError, UnknownDetectorError and DetectorPackError around load and scan, so the new 'selects no active row' refusal and the host errors surface as exit 1. The scanners' own empty-param refusals are already loud (facade_sinks.py:32-37, fsm_guard.py:29-34).

#### C58 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:46-47; plugins/arch-compliance/python/acf/registry.py:56-63; plugins/arch-compliance/python/acf/cli_check_diff.py:25`
- reasoning: Today the receipt problems are real. apply_registry matches findings by stamped mandate_id (enforcement.py:46). load_mandates checks only `enforced` rows (registry.py:58). KNOWN_DETECTORS includes the LLM ids (cli_check_diff.py:25). The design's _check_builtin closes each case: it refuses an unknown id (LLM ids are no longer keys), an id other than the contract's mandate_id, and a Tier-1 site outside the contract's call_sites. Mandate._row_shape refuses an active ast/guard row with no Tier-1 site. Every remaining built-in row's id equals the stamped id and its sites are served, so it can receive findings. The TypeScript scanners run regardless of a row's languages field, so no languages mismatch drops a row. Host rows go through scan_host_ast_file and scan_host_guards in both gates at whichever site the gate declares.

#### C59 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:120-123; plugins/arch-compliance/python/acf/adr/host.py:19-25`
- reasoning: The section's text: 'The adversarial-design-review gate's host values are declared by the host in config/architecture/adr.yml; no default stands in...' (:120-122). Those values are AdrHostConfig.runs_dir and ledger_path (host.py:19-25), and the design does not touch them. The spec's §6 row says the section governs adr.yml and that the design follows the practice 'by choice' (required repo_root for host rows, no default for apply_registry's call_sites, --call-site required=True). It does not claim the section requires this, so the paraphrase is accurate.

#### C60 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:48-49; plugins/arch-compliance/python/acf/detectors/python_pack.py:91`
- reasoning: The doctrine says: 'Do not probe optional attributes with hasattr to paper over missing interfaces' (:48-49), and the detector flags only `hasattr` calls (python_pack.py:91). The design looks up with getattr(mod, attr, None) and raises UnknownDetectorError when the result is not callable, so it never degrades silently. Every host load, call or result failure becomes a typed error (§4.4 items 3-4), and no path falls back to a default detector or to an empty result.

#### C61 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:57-64; plugins/arch-compliance/python/acf/engine.py:17-24`
- reasoning: The doctrine requires Path.as_posix() for persisted paths and notes this plugin refuses backslashes rather than normalizing them (:62-64). HostHit.path goes through validate_posix_rel_path, which calls the existing contains_backslash (engine.py:17-24) and refuses. That path becomes Finding.path, which is emitted as JSON. The design's messages build Path values with .as_posix() ((repo_root / rel_path).as_posix(), _ACTIVE_ROOT.as_posix()) and otherwise print already-validated POSIX strings.

#### C62 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/exceptions.py:5; plugins/arch-compliance/python/acf/exceptions.py:13; plugins/arch-compliance/python/acf/exceptions.py:29; config/architecture/ARCHITECTURE.md:101-102`
- reasoning: AcfInputError(AcfError), UnknownDetectorError(AcfError) and DetectorPackError(AcfError) each subclass AcfError alone with no stdlib mixin, as :101-102 requires. The design declares no new exception class.

#### C63 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:12-18; plugins/arch-compliance/python/acf/repo.py:32; config/architecture/ARCHITECTURE.md:107-108`
- reasoning: acf.repo declares CONFIG_DIR, MANDATES_REL and ARCH_REL (repo.py:12-18) and resolve_repo (:32). The new and changed engine, registry and detectors code takes repo_root or registry rows as input and spells no config/architecture literal. The rewritten acf-mandate snippet uses resolve_repo(None) / MANDATES_REL. The existing snippet already imports ARCH_REL and MANDATES_REL from acf.repo (acf-mandate SKILL.md:93).

#### C64 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:137-138; plugins/arch-compliance/skills/acf-mandate/SKILL.md:43`
- reasoning: The rule: 'Skill prose and runtime messages name no host repository, path or section' (:137-138). The §4.2-§4.4 messages are generic (host detector refs, mandate ids, generic placeholders). The §4.8 skill edits, such as the call-site vocabulary at acf-mandate SKILL.md:43, describe sites without naming the origin host. The spec's own attribution of `posttooluse` to the origin host (Decision 2) is design-doc text and is not specified as skill prose.

#### C65 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:21; plugins/arch-compliance/python/acf/judge.py:29; plugins/arch-compliance/python/acf/detectors/__init__.py:28-35; config/architecture/ARCHITECTURE.md:155-156`
- reasoning: The rule: an export needs a live call site in the package, a hook or a skill; tests do not count (:155-156). Each §6.2 export has a named package, hook or skill caller (gates, runners, load_mandates, _collect_paths, the four scanners). A grep for LLM_PROMPT_IDS outside docs finds only judge.py:29 (definition), cli_check_diff.py:21/:25 and tests, so cli_check_diff's load_mandates(llm_prompt_ids=...) keeps it live. The five deleted *_DETECTOR_IDS sets have no non-test users besides cli_check_diff.py:10/:16/:25 and detectors/__init__.py, which are rewritten, and test_typescript_pack.py:6/:14, which is repointed. None is left dead.

#### C66 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:161-164; plugins/arch-compliance/tests/test_hooks.py:186-194`
- reasoning: The rule requires a re-runnable recipe behind every/all/only/no-second quantifiers (:161-164). I sampled the spec's population claims: KNOWN_DETECTORS extenders, call_sites readers, the shipped rows that add precommit, partial rows, duplicate built-in pairs, load_mandates/apply_registry callers, shipped acf-check-diff invocations, _DETECTOR_IDS users and the active-row filters. Each carries a git grep or python recipe (§1, §4.8, §4.9, Appendix) or is a per-item table (§4.3, §6.1, §6.2). The weakest is the word-grep for 'no test exercises' an out-of-repo hook path. Inspection agrees with it: the hook tests pass in-repo absolute paths (test_hooks.py:186-194, :206-214).

#### C67 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:173-174; plugins/arch-compliance/python/acf/cli_check_diff.py:152; plugins/arch-compliance/hooks/posttooluse_gate.py:251`
- reasoning: The rule: subprocess text calls declare encoding='utf-8' and every prose file read declares its encoding (:173-174). The rule does not regulate the errors= policy. The TypeScript-branch read already declares utf-8 (cli_check_diff.py:152), and the design only binds it to `text`. The hook already reads every code file with utf-8 (:251), so its host runner calls add no read. scan_host_guards declares encoding='utf-8'. The design adds no subprocess. Module execution via importlib is source decoding, not a prose read.

#### C68 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:186-187; pyproject.toml:3; plugins/arch-compliance/.claude-plugin/plugin.json:3`
- reasoning: The rule: 'A change to a skill's prose bumps the plugin version in plugin.json and pyproject.toml' (:186-187). Both files read 0.2.2 at line 3. §4.8 edits acf-mandate and acf-setup prose and bumps both files to 0.2.3, and §7 item 3 verifies it.

#### C69 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:128-166; plugins/arch-compliance/hooks/posttooluse_gate.py:255-294; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:24-25; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:46`
- reasoning: The lifted rule asks for one canonical implementation consumed by every call site (ARCHITECTURE.md:198-200). The params extraction is duplicated token-for-token across the two gates (cli_check_diff.py:128-166 vs posttooluse_gate.py:255-294), and the design deletes it for one *_args function per scanner. Passing allowlist_globs/atomic_is_sink through only when present preserves today's coercions: the scanner iterates `allowlist_globs or []` (facade_sinks.py:46) and tests atomic_is_sink by truthiness (:88-90), so a null behaves as list(None or [])/bool(None) did. The signature defaults (:24-25) become the only defaults. The other listed duplicates are each confirmed at their cited sites: the _line_lookup closures, the active-row filters, the four ast.parse skips, test_self_host.py:40 and the ratchet's joins. The spec expressly disclaims completeness of §4.9.

#### C70 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:213-215; plugins/arch-compliance/python/acf/cli_check_diff.py:118-119`
- reasoning: The rule: 'remove legacy dependencies or non-contractual patterns in code paths you are changing. Do not expand scope to unrelated modules' (:213-214). Each §4.9 deletion is a definition that a new helper duplicates, in a module the design already edits. The citations.py change is required because its private helpers move to the shared engine. _scan_changed's `repo / path` + is_file() (cli_check_diff.py:118-119) takes git-supplied repo-relative paths, so ADJACENT is a fair disposition. Keeping the two pre-existing dispatch loops, each calling the one host procedure, stays within scope.

#### C71 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:147-148; plugins/arch-compliance/python/acf/adr/ledger.py:64; plugins/arch-compliance/python/acf/adr/ledger.py:132`
- reasoning: The section freezes LedgerRow and LedgerAmendment fields (ledger.py:64, :132). The spec's §3 in-scope table and §4.9 touch nothing in acf/adr except citations.py's two path helpers, and ledger.py appears only as a grep result in §1 item 3.

#### C72 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:47-50; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:102; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:123`
- reasoning: Principle 1, typed errors with no silent defaults on registry load, is served by the new load-time refusals. Principle 2, one finding schema, holds because HostHit is converted into the single Finding type by the runner. Principle 3, POSIX paths, holds via HostHit validation. Principle 4 says 'detectors, auditors, and call sites must agree or tests fail' (:50), and the design adds call-site/contract agreement plus the contract-against-dispatch test. The parent defines detector as 'Detector fn / guard module' (:102) and calls for 'Extension points for project-specific detectors' (:123, :125); the host ref syntax and runners provide that.

#### C73 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:49-50; plugins/arch-compliance/hooks/posttooluse_gate.py:113-117; plugins/arch-compliance/python/acf/cli_check_diff.py:69-74`
- reasoning: apply_registry drops a finding only when the looked-up line carries a token (enforcement.py:49-50). An empty line list yields '' and therefore keeps the finding, so the [] mapping can only over-report. errors='replace' cannot corrupt an ASCII token in UTF-8 text. scan_host_guards runs inside _scan_changed, which is within the try at cli_check_diff.py:69-74, and inside _scan_paths, which is within the hook's scan try at :113-117. The design extends that try to UnknownDetectorError and it already has DetectorPackError, so the wrapped OSError reaches each gate's handler. make_line_lookup only indexes a mapping.

#### C74 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:72-73; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:46; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:56-57; plugins/arch-compliance/python/acf/cli_check_diff.py:168-182`
- reasoning: The doctrine: 'Optional whole-tree freeze of bare/broad-except counts. Enable the mandate and commit a ... baseline' (:72-73). The freeze stays intact: scan_tree counts plus compare_to_baseline, run only from acf-check-diff (cli_check_diff.py:168-182), now declared as DIFF_CALL_SITES in KNOWN_DETECTORS. The design replaces the unchecked join `root / r` (:46) and the silent `if not search.exists(): continue` (:56-57) with containment and existence refusals (DetectorPackError). The baseline existence check already raises (:78-81). The symlinked-root re-keying edge is disclosed in §4.9. §4.8 adds both constraints to :72-73.

### Unanchored findings


### Looked for but did not find

- High-frequency misses (ARCHITECTURE.md:217-228): completeness claims carry recipes. No default re-enters for a declared value: --call-site is required, repo_root is required for host rows, and apply_registry's call_sites has no default. No host name appears in runtime messages. No stdlib mixin. No subprocess is added. Tests consume load_mandates, KNOWN_DETECTORS and file_under_root rather than re-implementing them. The :228 KNOWN_DETECTORS citation is updated in §4.8. All clear.
- ## Build artifacts (:66-68): the design only centralizes build_artifact_args and the mandate-id constant. build_artifact_args({'path_prefixes': []}) still yields the scanner default, as `list(prefixes) if prefixes else None` does today (cli_check_diff.py:160-164). The rule about not committing generated trees is untouched.
- ## Façade sinks / ## FSM transitions (:75-85): only the params extraction moves. Both scanners already refuse empty required params loudly (facade_sinks.py:32-37, fsm_guard.py:29-34). Both rows are unenforced here. Not governing beyond §4.9.
- ## Soft fail-loud smells / ## React boundaries (:87-97): llm rows. The new llm_prompt_ids check accepts the shipped partial soft.fail-loud row (llm_fail_loud is a prompt id). The Tier-2 judge is unchanged. Not touched.
- ## Post-merge (:230-239): host operational declarations. The design changes none.
- ## Fail loud fixture paragraph (:32-36): the design adds no in-repo fixture carrying broad except patterns that the gates would scan. Its host-module test fixtures live under tmp_path.

## sweeper

### Claim verdicts

#### C75 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; plugins/arch-compliance/hooks/posttooluse_gate.py:229-236; plugins/arch-compliance/hooks/posttooluse_gate.py:284-286; plugins/arch-compliance/python/acf/enforcement.py:47`
- reasoning: I searched for the behaviour rather than the name: every status read in plugins/arch-compliance (\.status\b, "unenforced", "enforced", excluding adr/). The Tier-1 active-row filters are cli_check_diff.py:98, posttooluse_gate.py:231, :235, :285 and enforcement.py:47. The spec replaces each with Mandate.runs_at or MandateRegistry.active (§4.5, §4.6), and the host runners select through registry.active (§4.4 items 6-7). The other status reads are load-time (registry.py:58, which becomes is_active), Tier-2 (judge.py:218, out of scope by Decision 2), or display-only (inject_constraints.py:158, acf-mandate SKILL.md:98). After the change no Tier-1 site keeps its own active filter.

#### C76 — REFUTED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:125; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:331; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:413; plugins/arch-compliance/python/acf/adr/citations.py:76; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:58-60`
- reasoning: I re-ran the recipe as a Grep over hooks/ and python/. It prints exactly posttooluse_gate.py:204 and :243, citations.py:76, and fail_loud_ratchet.py:60 and :123. A wider search (is_relative_to, isabs, commonpath, '..') found only citations.py:76. The listed instances are right. The 'one implementation' claim is not. validate_posix_rel_path (spec :125) decides containment lexically: it refuses absolute paths and '..'. It is the only containment decision a HostHit.path ever gets (spec :331). _to_findings emits the Finding whatever the path resolves to (spec :408). scan_host_guards calls file_under_root only to fetch exemption lines, and maps a path that resolves outside the root to [] while keeping the finding (spec :413). So 'does this host-supplied path lie in the repo' has a lexical answer for host hits and a resolved answer for registry rows and harness paths. The ratchet walk is a second gap: rglob under a contained root (fail_loud_ratchet.py:58) follows in-repo directory symlinks on Python 3.11/3.12, and its keys are contained only lexically. The parse_python half of the claim holds: the only non-test ast.parse/SyntaxError sites are the four scanners.

#### C77 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:84-92; plugins/arch-compliance/hooks/posttooluse_gate.py:279-282; plugins/arch-compliance/python/acf/cli_check_diff.py:153-156`
- reasoning: The bridge decodes untyped JSON dicts from a Node subprocess. It coerces severity, path (posix_path normalizes; it does not refuse) and line, and copies detector from the JSON. Both gates then overwrite the bridge's path with their own key (posttooluse_gate.py:280, cli_check_diff.py:154), so the bridge and the host runner do not even share path validation. The host runner takes typed HostHit objects and stamps mandate_id, detector and detection from the row. The only shared piece is the Finding constructor.

#### C78 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:238-255; plugins/arch-compliance/python/acf/judge.py:247`
- reasoning: _to_finding is at judge.py:238-255. The claim's spec_citation of 236-253 is two lines off; the spec body's 238-255 is correct. It demotes severity by confidence (:241-245) and defaults path to '<diff>' and line to 0 (:249-250), so a shared constructor with host findings is not warranted. One overlap the claim does not name: the judge stamps mandate_id from the provider's result (:247), not from the row it reviewed. That is the very attach-to-the-wrong-row exposure Decision 5 removes for host code, and Tier-2 keeps it (see the unanchored finding).

#### C79 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:25-26; plugins/arch-compliance/hooks/inject_constraints.py:28-29; tests/test_check_installed_skills.py:15-18`
- reasoning: I searched the whole tracked tree outside docs/ for importlib, import_module, spec_from_file_location, exec_module, runpy, __import__, exec( and sys.path mutation. In plugin runtime code the only hits are the two hooks' identical start-up sys.path.insert(0, plugin python/). The only by-path module load is tests/test_check_installed_skills.py:15-18, a test loading a fixed repository script, which is ADJACENT. Nothing loads code from a registry-supplied path. The new loader does keep a second cache, _MODULE_CACHE, next to sys.modules, keyed by a name derived from rel_path (see the advisory finding). That overlaps the stdlib, not a plugin mechanism.

#### C80 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80; plugins/arch-compliance/hooks/posttooluse_gate.py:119-123; plugins/arch-compliance/python/acf/detectors/fsm_guard.py:56`
- reasoning: I searched for LineLookup, line_lookup and 'lines[line - 1]' across the tree, docs excluded. The only LineLookup implementations passed to apply_registry are the two closures; test_enforcement.py passes test-local lambdas. fsm_guard.py:56 indexes lines to build a message snippet, a different job. cli_check_llm, the judge and the skills have no line lookup.

#### C81 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:56-63; plugins/arch-compliance/skills/acf-mandate/SKILL.md:95; plugins/arch-compliance/tests/test_profile_drift.py:24; plugins/arch-compliance/skills/architecture-review/SKILL.md:62`
- reasoning: I searched for known_detectors, KNOWN_DETECTORS and call_sites in every non-docs file. Each validator site consumes load_mandates rather than re-implementing it: the acf-mandate snippet (:95), test_profile_drift (:24), test_self_host (:23) and architecture-review (:62, no known_detectors). acf-setup has no detector check. test_self_host.py:40-41 checks only manual-row paths. No site independently checks detector ids or call sites on rows. The bridge's TS_MANDATE_IDS lookup validates scanner output, not rows.

#### C82 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:254; plugins/arch-compliance/python/acf/enforcement.py:46-47; plugins/arch-compliance/python/acf/cli_check_diff.py:168`
- reasoning: The built-in scanners run unconditionally (posttooluse_gate.py:254, cli_check_diff.py:127), and registry-selected ones dispatch only for rows the active filter returns (cli_check_diff.py:168). Take a gate that dispatches a detector its contract excludes. A row declaring that site is refused by _check_builtin. A row not declaring it has its findings dropped at the single sink, which today drops at enforcement.py:46-47 and gains the runs_at check. So the reverse drift over-refuses loudly and never silently drops a row. The forward drift (table says runs, gate does not dispatch) is caught by the contract-against-dispatch test.

#### C83 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:204; plugins/arch-compliance/hooks/posttooluse_gate.py:242-245; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:46; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:59-62`
- reasoning: Both sites decide containment by hand today. The hook joins or resolves (:204), then falls back to the absolute string on ValueError (:244-245). The ratchet joins roots with no containment (:46) and skips on ValueError (:61-62). After the switch, repo comes from resolve_repo (.resolve(), repo.py:41-44) and resolve_under_root resolves the same base, so relative_to(...).as_posix() cannot fail at :243. The rglob results under a resolved search root are lexically under root, so the :60 conversion cannot fail either. §4.1, §4.6, §4.9 and §5.2 agree. The resolved-versus-lexical caveat for walked symlinks is recorded under C76.

#### C84 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:65; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:398; plugins/arch-compliance/hooks/posttooluse_gate.py:72-81`
- reasoning: I searched the spec for every 'host code' and 'fresh_host_loader' occurrence (lines 51, 63-66, 398, 467-475, 631). Decision 7 (:65) states the guarantee and its limit: atexit handlers and threads are not confined. The other statements are narrower: load_mandates runs no host code, and _to_findings runs no host code because it sees only rebuilt HostHits (:398). None claims host code runs only inside the wrapped regions. In the wrapped code, callable() (outside the try) runs no host code. fresh_host_loader is the only reset; production has none, by the one-root rule.

#### C85 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:85; plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23; plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15`
- reasoning: A Grep for 'fail-loud.empty-catch' and 'no-shims.explicit-any' outside .yml and .md files found Python hits only in tests (test_baseline, test_enforcement, test_typescript_pack). The Node rule literals (emptyCatch.ts:23, explicitAny.ts:15) and scan.ts self-test expectations (:94-96) are the Node side. Today the bridge copies item['mandate_id'] (:85); the spec replaces that with the TS_MANDATE_IDS lookup plus a runtime comparison.

#### C86 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:52; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:86`
- reasoning: Every Tier-1 producer sets a severity: the scanners hard-code it, the bridge takes it from the Node JSON (:86), and the host runner takes it from the row. All of them pass through apply_registry, which overwrites severity from the row (enforcement.py:52), at both gates (cli_check_diff.py:82, posttooluse_gate.py:125). The judge's own severity is Tier-2 and does not pass through it.

#### C87 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:118-119; plugins/arch-compliance/python/acf/diff.py:56`
- reasoning: changed_files is `git diff --name-only --diff-filter=ACMR` (diff.py:56), so its paths are repo-relative and never registry- or host-supplied. One residual asymmetry, not a duplication of file_under_root's job: a tracked symlink pointing outside the repo is read through by is_file()/read_text at :119/:125, while the hook's new file_under_root drops it (see the advisory finding).

#### C88 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/loader.py:24-28; plugins/arch-compliance/hooks/inject_constraints.py:165; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:78-81`
- reasoning: require_file takes a built Path and always raises AcfInputError. Its live caller passes an operator file (inject_constraints.py:165). The ratchet already keeps a phase-typed not-found refusal (fail_loud_ratchet.py:78-81, DetectorPackError). The error type is a real difference. The ratchet's load_baseline does stay a hand-rolled second JSON loader next to load_model_file, and the spec edits it without naming that (see the advisory finding and document_conflicts).

#### C89 — SURVIVED
- evidence: `config/architecture/mandates.yml:70; plugins/arch-compliance/profiles/python-service/mandates.yml:18; plugins/arch-compliance/tests/fixtures/mandates_valid.yml:18; hm:config/architecture/mandates.yml:246; hm:scripts/ci/run_guards.py:116`
- reasoning: I collected every call_sites value in the tracked .yml files and the inline test registries. This repository and its profiles use ci, hook and audit; tests also use []. The origin host uses precommit, posttooluse, ci and audit (hm mandates.yml, 48 rows). All are in CallSite. In this repository, 9 ast/guard rows declare ci (python-service 7, react-app 3, fixture 3), which matches the Appendix. Once precommit is added, every active ast/guard row reaches a DIFF site where its detector runs. The [ci]-only ratchet rows are unenforced. No Tier-1 gate reads audit; the origin host's runner selects by site itself (run_guards.py:116).

#### C90 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_diff_cli.py:102-108; plugins/arch-compliance/tests/test_registry.py:30; plugins/arch-compliance/tests/test_typescript_pack.py:6; plugins/arch-compliance/tests/test_hooks.py:199-218; tests/test_self_host.py:40`
- reasoning: I counted the main([...]) calls in test_diff_cli: :48, :61, :98, :107, :124, :153, :154, :173, :178, :191, ten as listed. The ten apply_registry calls in test_enforcement match too. I checked for imports of every deleted name (_DETECTOR_IDS, _looks_absolute, _escapes_repo); only test_typescript_pack :6 and :14 import any. I checked the direct Mandate constructions (test_enforcement.py:19 is ast with [ci], active, so it passes _row_shape; test_judge and test_template build llm rows) and the inline registries. test_portable_guards, test_adr_import_graph, test_repo_paths and the other hook tests stay valid under the new refusals. I found no breaking test beyond the listed set.

#### C91 — REFUTED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:228`
- reasoning: The §4.8 recipe sweeps by tool name. My grep reproduces its hits, and each listed site exists (ci.yml:40, README.md:57-58, acf-setup SKILL.md:24/:184/:193/:206/:207/:217/:219/:250, acf-mandate SKILL.md:131, CLAUDE.md:36, the guide's :82-83, PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:454). A behaviour sweep for instructions to run the CLI also finds acf-setup SKILL.md:228, the friend-bar tip 're-run with `--mode staged`'. That line does not contain the tool name, so the recipe misses it. After the change that re-run exits 2 without --call-site precommit. The method misses instructions that run the CLI without naming it.

#### C92 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:72-73; config/architecture/ARCHITECTURE.md:226-228; plugins/arch-compliance/skills/acf-mandate/SKILL.md:58; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:161`
- reasoning: Each named site exists and is stale under the revision: the ratchet's enablement text, the KNOWN_DETECTORS location, the partial-row advice, and 'PostToolUse | Diff-scoped Tier 1 on edited .py/.ts/.tsx'. I read the rest of ARCHITECTURE.md, the README Tier-1 and Hooks sections, SUPERPOWERS_COMPLEMENT.md:55-93, and ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:90-195. Every other stale line I found is already in another §4.8 row.

### Unanchored findings

- **advisory**: There are two containment rules for path strings from outside the code: validate_posix_rel_path refuses absolute paths and '..' lexically, and it is the only check a HostHit.path receives. resolve_under_root decides by resolution everywhere else. A host hit whose path leaves the root through an in-repo symlink still becomes a Finding (its lines map to []). This contradicts the 'one implementation' framing of §4.1 and §6, and the Approved ADR contract's view that a '..' refusal would be a second repo-relative test.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:125`
- **advisory**: The spec edits fail_loud_ratchet.load_baseline (swapping its is_file check for file_under_root) but keeps its hand-rolled JSON load, parse and shape refusals. load_model_file is the declared single load-parse-validate-refuse path, and the Approved ADR contract records this function as 'a pre-existing second loader outside this phase'. The design does not name that record.
  - evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:77-98`
- **advisory**: The bare/broad-except predicate is defined twice, in python_pack._is_bare_or_exception and in the body of count_bare_excepts. §4.9 rewrites count_bare_excepts' parse in this change but leaves its private copy of the predicate.
  - evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:31-34`
- **advisory**: Reading file lines for the exemption check will have three owners with two decoding policies. The gates read strictly (cli_check_diff.py:125 and :152, posttooluse_gate.py:251), so a non-UTF-8 code file raises an uncaught UnicodeDecodeError. scan_host_guards reads with errors='replace', on the stated rationale that a stray byte must not crash the gate, which applies equally to the gate reads.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:125`
- **advisory**: load_host_detector keeps _MODULE_CACHE keyed by rel_path next to sys.modules keyed by a name derived from rel_path, so two stores record 'host module loaded'. The except path and the fresh_host_loader fixture must keep both in step.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:349`
- **advisory**: After the change the two Tier-1 gates disagree on an in-repo symlink pointing outside the repository. The hook's file_under_root drops it, while acf-check-diff's join-and-is_file follows it, scans the target under the link's path, and hands that path to host runners.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:118-119`
- **advisory**: The judge's _to_finding takes mandate_id from the provider's result rather than from the row it reviewed, so a provider can attach a finding to another row. Decision 5 removes that exposure for host code, but the Tier-2 producer keeps it and the spec does not mention it.
  - evidence: `plugins/arch-compliance/python/acf/judge.py:247`

### Looked for but did not find

- a third LineLookup implementation (terms: LineLookup, line_lookup, 'lines[line - 1]') outside the two gate closures
- another plugin runtime site that loads code by path (terms: importlib, import_module, spec_from_file_location, exec_module, runpy, __import__, exec()
- another containment test (terms: is_relative_to, isabs, commonpath, startswith(".."), '..') beyond citations.py:76
- a non-test Python spelling of the TS mandate ids (terms: fail-loud.empty-catch, no-shims.explicit-any)
- another active-row filter at a Tier-1 site (terms: .status, "unenforced", "enforced")
- another detector-id or call-site validator in skills or tests (terms: known_detectors, KNOWN_DETECTORS, call_sites)
- a call_sites value outside {ci, precommit, hook, posttooluse, audit} in this repo or hm:config/architecture/mandates.yml (term: call_sites:)
- another parse-or-skip in runtime code (terms: ast.parse(, except SyntaxError)

### Relationships

- PARTIAL_OVERLAP: `acf.engine.validate_posix_rel_path` — responsibility `decide whether an outside path string lies inside the repository` — existing `plugins/arch-compliance/python/acf/adr/citations.py:74-76`
  - resolution: Keep resolve_under_root as the only containment predicate. Make validate_posix_rel_path a pure shape check (POSIX, normalized), and have HostHit consumers that need containment (scan_host_guards) refuse or flag a hit for which resolve_under_root returns None instead of keeping it with [] lines.
- SUBSUMED: `acf.engine.resolve_under_root / file_under_root` — responsibility `decide containment of a path string in the root` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:204`
  - resolution: The hook's is_absolute join and the relative_to/ValueError fallback (:242-245) are deleted, as are the ratchet's joins (:46, :122-124) and its walk except (:59-62). Each site keeps only relative_to(...).as_posix().
- PARTIAL_OVERLAP: `ratchet load_baseline after the file_under_root switch` — responsibility `load, parse and refuse a JSON input file` — existing `plugins/arch-compliance/python/acf/loader.py:43-77`
  - resolution: Give the ratchet baseline a Pydantic model loaded through load_model_file, as acf/baseline.py:86 already does, and map AcfInputError to DetectorPackError at the ratchet boundary. The missing-file, JSON and shape branches of fail_loud_ratchet.py:77-98 collapse into it.
- IDENTICAL: `count_bare_excepts (rewritten to use parse_python)` — responsibility `decide whether an except handler is bare or broad` — existing `plugins/arch-compliance/python/acf/detectors/python_pack.py:77-82`
  - resolution: count_bare_excepts calls python_pack._is_bare_or_exception (made public) instead of restating it at fail_loud_ratchet.py:31-34.
- PARTIAL_OVERLAP: `scan_host_guards file_lines fill (errors='replace')` — responsibility `read a file's lines for exemption lookup` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:125-126`
  - resolution: One acf.enforcement helper reads lines for the exemption check under one declared decoding policy. The gates' .py and .ts reads (cli_check_diff.py:125, :152; posttooluse_gate.py:251) and scan_host_guards consume it.
- PARTIAL_OVERLAP: `load_host_detector _MODULE_CACHE` — responsibility `record which host module is already loaded` — existing `tests/test_check_installed_skills.py:15-18`
  - resolution: Use sys.modules[name] (the name is a pure function of rel_path) as the only cache, and drop _MODULE_CACHE. The except branch and the fresh_host_loader fixture then manage one store.
- ADJACENT: `load_host_detector sys.path append` — responsibility `make a code root importable` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:25-26`
  - resolution: none
  - non-merge: The hooks prepend the plugin's own python/ at process start; the loader appends one host root once, on first dispatch, under the one-root rule. Their position, timing and owner all differ.
- ADJACENT: `_to_findings (HostHit -> Finding)` — responsibility `build a Finding from an external producer's result` — existing `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:84-92`
  - resolution: none
  - non-merge: The bridge decodes untyped JSON, and the gates overwrite its path anyway. The host runner gets typed HostHits and stamps identity from the row. Only the Finding constructor is shared.
- ADJACENT: `_to_findings (HostHit -> Finding)` — responsibility `stamp a Finding's identity from the row the producer ran for` — existing `plugins/arch-compliance/python/acf/judge.py:238-255`
  - resolution: none
  - non-merge: The judge demotes severity by confidence and allows a <diff> path and line 0, so no shared constructor. It does take mandate_id from the provider (:247) rather than the row, which the spec does not mention.
- ADJACENT: `file_under_root in the hook's _collect_paths` — responsibility `decide which edited or changed path is an in-repo file to scan` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:118-119`
  - resolution: none
  - non-merge: git supplies repo-relative paths (diff.py:56). The two gates still disagree on tracked symlinks that point outside the repo.
- ADJACENT: `file_under_root callers' not-found refusals` — responsibility `refuse a missing input file` — existing `plugins/arch-compliance/python/acf/loader.py:24-28`
  - resolution: none
  - non-merge: require_file takes a built Path and always raises AcfInputError. These callers first decide containment of a string and raise their phase's error type.
- SUBSUMED: `Mandate.runs_at / MandateRegistry.active` — responsibility `decide whether a row runs at a gate` — existing `plugins/arch-compliance/python/acf/enforcement.py:47`
  - resolution: cli_check_diff._active_mandates (:94-99), the hook's inline filters (:229-236, :284-286) and apply_registry's status check (:47) all call runs_at.
- ADJACENT: `Mandate.runs_at` — responsibility `decide whether a row is reviewed` — existing `plugins/arch-compliance/python/acf/judge.py:214-218`
  - resolution: none
  - non-merge: Tier-2 reviews every llm row it is given and reads status only to decide whether a provider is required (Decision 2 scope).
- PARTIAL_OVERLAP: `KNOWN_DETECTORS (BuiltinDetector.call_sites)` — responsibility `declare where each built-in detector runs` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:168`
  - resolution: The table declares and each gate's dispatch decides. The §4.7 contract-against-dispatch test is the agreed tie, and both stay as two coupled owners.
- SUBSUMED: `TS_MANDATE_IDS` — responsibility `define the TypeScript detector-to-mandate ids` — existing `plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23`
  - resolution: The bridge stamps the Python value and refuses a Node literal that differs, so the Node literal becomes a checked echo.
- IDENTICAL: `make_line_lookup` — responsibility `look up a finding's source line` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:119-123`
  - resolution: Both closures (cli_check_diff.py:76-80 and posttooluse_gate.py:119-123) are deleted and both gates call make_line_lookup.

### Two-owner counts

- decide containment of an outside path string in the repo root (resolve_under_root; validate_posix_rel_path lexically): 2
- decide whether an except handler is bare or broad (python_pack._is_bare_or_exception; count_bare_excepts): 2
- load, parse and refuse a JSON input file (load_model_file; fail_loud_ratchet.load_baseline): 2
- read file lines for the exemption check (cli_check_diff; posttooluse_gate; scan_host_guards): 3
- declare or decide where a built-in detector runs (KNOWN_DETECTORS; gate dispatch): 2
- record a loaded host module (_MODULE_CACHE; sys.modules): 2
- make a code root importable via sys.path (posttooluse_gate; inject_constraints; load_host_detector): 3
- build a Finding from an external producer's result (host _to_findings; typescript_bridge; judge _to_finding): 3
- map detector id to mandate id (KNOWN_DETECTORS; README detector table, pinned by test): 2
- decide which edited or changed path is an in-repo file to scan (hook file_under_root; diff gate join-and-is_file): 2

### Document conflicts

- `docs/design/ADR_GATE_HOST_CONTRACT.md:300` (contradicts): a refusal would be a second implementation of the repo-relative test that acf:plugins/arch-compliance/python/acf/adr/citations.py:49 (_looks_absolute) and :74 (_escapes_repo) already own
- `docs/design/ADR_GATE_HOST_CONTRACT.md:292` (restates): fail_loud_ratchet.load_baseline (acf:plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:77-98) is a pre-existing second loader outside this phase.
- `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:161` (contradicts): PostToolUse | Diff-scoped Tier 1 on edited `.py` / `.ts` / `.tsx` (and configured config paths); feed findings into the turn.

## hardening

### Claim verdicts

#### C93 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:72, plugins/arch-compliance/hooks/posttooluse_gate.py:107, plugins/arch-compliance/hooks/inject_constraints.py:104, plugins/arch-compliance/python/acf/cli_check_llm.py:54`
- reasoning: The load-time checks in the §4.2 body read only strings and the filesystem. cli_check_diff.py:72 already catches UnknownDetectorError around both load and scan, and the hook's scan except is widened to it (§4.6). The hook passes known_detectors (the design changes :107), so an import at load would import every active host module, CI-only guards included, on every edit. That point holds. One sub-reason is inaccurate: inject_constraints.py:104 and cli_check_llm.py:54 pass no known_detectors, so an import placed under the known_detectors branch would not run there either. The other reasons carry the claim.

#### C94 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:127, plugins/arch-compliance/python/acf/enforcement.py:46, plugins/arch-compliance/python/acf/cli_check_diff.py:168`
- reasoning: Built-in dispatch is unconditional per file type (cli_check_diff.py:127, posttooluse_gate.py:254). Routing is by mandate_id (enforcement.py:46). The ratchet is diff-only (:168). So the remaining failure modes are: an id mismatch (_check_builtin id test), a site the detector does not run at (_check_builtin unserved test), no Tier-1 site (_row_shape), and a host row whose file is missing (load) or whose callable is missing (dispatch, fail loud). Host findings take the row's id in _to_findings. I enumerated detection/detector mismatches (for example a built-in under detection guard): they still run, because built-in dispatch ignores detection.

#### C95 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:63, plugins/arch-compliance/hooks/posttooluse_gate.py:65, plugins/arch-compliance/tests/test_diff_cli.py:48`
- reasoning: Each production entry resolves the repo once (cli_check_diff.py:63; hook :65, one process per edit). The only multi-root producer is in-process tests calling main() over several tmp repos (test_diff_cli.py:48 and others). The refusal is rung 3 and nothing in production repairs. Rung 1 does not apply: sys.path and sys.modules are global to the process.

#### C96 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:67, plugins/arch-compliance/python/acf/detectors/python_pack.py:97, plugins/arch-compliance/python/acf/cli_check_diff.py:168, config/architecture/mandates.yml:63`
- reasoning: The scanners stamp literal mandate ids (python_pack.py:67, :97; the ratchet at :132). The ratchet runs only in cli_check_diff (:168). I loaded every shipped registry (this repo, both profiles, the fixture): each built-in detector appears in at most one row, so the one-row-per-detector cost hits no shipped registry.

#### C97 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:104, plugins/arch-compliance/python/acf/cli_check_llm.py:54, plugins/arch-compliance/python/acf/loader.py:72, plugins/arch-compliance/python/acf/registry.py:37`
- reasoning: inject_constraints.py:104-105 catches AcfInputError. cli_check_llm.py:54 calls load_mandates with no try. load_model_file converts only ValidationError (loader.py:72), so an AcfInputError raised inside a validator keeps its type, as _unique_ids already relies on (registry.py:37; test_registry.py:46).

#### C98 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:35, plugins/arch-compliance/python/acf/detectors/facade_sinks.py:51`
- reasoning: Each built-in scanner parses on its own (python_pack.py:35, facade_sinks.py:51). The host runner adds a single parse per file, shared by every host ast row. Not load-bearing.

#### C99 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:46, plugins/arch-compliance/python/acf/finding.py:12`
- reasoning: apply_registry looks the row up by finding.mandate_id (enforcement.py:46), and Finding.mandate_id is a free str (finding.py:12). A host-built Finding could therefore route to any row. HostHit has no mandate_id field and forbids extras, so that state is unrepresentable (rung 1).

#### C100 — SURVIVED
- evidence: `.gitignore:8, plugins/arch-compliance/hooks/posttooluse_gate.py:73, .github/workflows/ci.yml:40`
- reasoning: .acf/ is ignored (.gitignore:8), so a CI checkout lacks the marker. The hook exits 0 without it (posttooluse_gate.py:72-81). CI invokes the diff gate explicitly (ci.yml:40). The residual case is stated and accepted.

#### C101 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:127, plugins/arch-compliance/python/acf/detectors/python_pack.py:46, plugins/arch-compliance/hooks/posttooluse_gate.py:254`
- reasoning: scan_python_file is called for every changed .py file with no row selection (cli_check_diff.py:127, hook :254). It emits hasattr findings regardless of rows (python_pack.py:46-49). So without the sink filter a [ci]-only no-shims.hasattr finding would survive in the hook. The spec states this reason at Decision 2 (python_pack.py:27-52). The filter is not redundant.

#### C102 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:26, pyproject.toml:19, C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/__init__.py:1`
- reasoning: The hook inserts python/ at sys.path[0] (:25-26), and the console script's sys.path[0] is its own directory, so an appended host root cannot shadow earlier entries. Checked on this machine: site-packages already exposes a namespace 'scripts' (pywin32 win32/scripts). The origin host's scripts/ is a regular package (scripts/__init__.py exists). Import machinery prefers a later regular package over an earlier namespace portion, so host intra-repo imports still resolve. The stated cost (an earlier entry wins) fails loud whenever the submodule is absent.

#### C103 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:71, plugins/arch-compliance/hooks/posttooluse_gate.py:114, plugins/arch-compliance/python/acf/enforcement.py:49`
- reasoning: Both gates call their scan function inside their scan try (cli_check_diff.py:69-74; hook :113-117). apply_registry today does only line_lookup plus regex (enforcement.py:49-52). Reading inside scan_host_guards therefore keeps the sink free of I/O and routes OSError to an existing handler.

#### C104 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:16, plugins/arch-compliance/python/acf/judge.py:29`
- reasoning: judge.py:16 imports acf.registry, so registry importing judge would be a cycle, and judge.py:11 pulls in httpx. Every shipped llm row names an id in LLM_PROMPT_IDS (verified by loading all registries). Not load-bearing. See the advisory on rung 2: the ids could live in a module registry can import.

#### C105 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/run_guards.py:116, C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/run_guards.py:319, plugins/arch-compliance/python/acf/cli_check_diff.py:61`
- reasoning: The origin runner selects rows per site (run_guards.py:116) and defaults --site to ci (:317-321), as the spec states. A required argparse flag turns a missing value into a usage error at the invocation, rung 3 at the producer.

#### C106 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/run_guards.py:126, plugins/arch-compliance/profiles/python-service/mandates.yml:18`
- reasoning: No shipped row declares precommit today (verified; for example profiles/python-service/mandates.yml:18 is [ci]). Without the precommit additions plus the empty-selection refusal, a --call-site precommit run would select nothing and report clean. The origin refuses that at run_guards.py:126-130.

#### C107 — SURVIVED
- evidence: `C:/Python313/Lib/site-packages/pydantic/main.py:317, C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/genre_conditional_guard.py:33`
- reasoning: model_construct (pydantic main.py:317) bypasses validation, and a subclass can define properties, so touching an unvalidated item's fields can run host code or yield non-str values. The host already defines its own finding classes with custom methods (genre_conditional_guard.py:33-40). Exact-type checks and a rebuild inside the try keep that inside the wrapped region.

#### C108 — SURVIVED
- evidence: `docs/design/ADR_GATE_HOST_CONTRACT.md:295, plugins/arch-compliance/python/acf/adr/host.py:24`
- reasoning: The approved contract's 'Not adopted' paragraph (ADR_GATE_HOST_CONTRACT.md:295-301) declines refusing absolute or .. values in runs_dir and ledger_path (host.py:24-25). The design keeps those fields unchanged and deletes only the duplicates listed in §4.9. Not load-bearing.

#### C109 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/genre_conditional_guard.py:39, plugins/arch-compliance/python/acf/cli_check_diff.py:73`
- reasoning: genre_conditional_guard.py:33-40 is a non-frozen dataclass whose __str__ calls self.line_text.strip(). I found no live host code that raises an exception carrying such an object, so the producer is the host-callable boundary in general, which is genuinely external. The gate prints str(exc) of the typed error (cli_check_diff.py:73), so a raising host __str__ must be absorbed before that point.

#### C110 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:14, plugins/arch-compliance/python/acf/registry.py:21, plugins/arch-compliance/python/acf/registry.py:11`
- reasoning: Mandate is a plain BaseModel with no model_config (registry.py:14-26). It has the fields id, severity, status, detection, detector, call_sites list[str] (:21), languages Literal including 'none' (:11, :20) and params dict|None (:26). A property and methods on a BaseModel are compatible, and MandateRegistry already carries the property by_id (:43-45).

#### C111 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/finding.py:11, plugins/arch-compliance/python/acf/finding.py:6, plugins/arch-compliance/python/acf/registry.py:17`
- reasoning: Finding's required fields are mandate_id, severity, path, line, message and detector; confidence and detection have defaults (finding.py:11-19). Severity is a str Enum of BLOCK/WARN (:6-8), matching Mandate.severity's Literal (registry.py:17).

#### C112 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:47, plugins/arch-compliance/python/acf/enforcement.py:23, plugins/arch-compliance/python/acf/enforcement.py:43`
- reasoning: by_id is at :43 and the lookup at :46. The status drop is at :47. Exemptions and severity are at :49-52. LineLookup = Callable[[str, int], str] at :23, which a closure-returning make_line_lookup satisfies.

#### C113 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:72, plugins/arch-compliance/python/acf/cli_check_diff.py:70, plugins/arch-compliance/python/acf/cli_check_diff.py:109`
- reasoning: load is at :70 and the scan at :71 inside the try. The except at :72 lists GitError, AcfInputError, UnknownDetectorError and DetectorPackError. The lookup and apply are at :76-82. In the .py branch, text, posix, lines and repo are in scope and registry is a parameter (:102-150). The .ts branch reads at :152. changed (:110) and file_lines (:109) are in scope after the ratchet loop.

#### C114 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:113, plugins/arch-compliance/hooks/posttooluse_gate.py:204, plugins/arch-compliance/hooks/posttooluse_gate.py:251`
- reasoning: Every cited span matches the file. Deferred imports are at :91-104, the load try at :106-110 and the scan try at :113-117. The lookup and apply are at :119-125. The resolve/dedupe loop is at :202-209, the is_file skip at :239 and relative_to/ValueError at :242-245. The filters are at :229-236 and :284-286, and the build-artifact loop at :284-294. text is bound at :251 before the .py/else split, so it is in scope in both branches, with rel at :243.

#### C115 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:72, plugins/arch-compliance/hooks/posttooluse_gate.py:115, plugins/arch-compliance/python/acf/enforcement.py:49`
- reasoning: I traced each host-touching step. Module exec and getattr sit in one BaseException try. callable() runs no host code. The call, list(raw) and _revalidate sit in one try. _describe wraps formatting. scan_host_guards' stat and read are wrapped. All of it runs inside the scan functions, which sit under cli_check_diff.py:72 and the hook's widened :115 except. apply_registry does only lookup plus regex. Post-return host code (atexit, threads) is the accepted residual of Decision 7.

#### C116 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_diff_cli.py:9, plugins/arch-compliance/tests/test_diff_cli.py:48`
- reasoning: test_diff_cli imports main and calls it in process (:9, :48, :154 ...). Module globals can be monkeypatched. spec_from_file_location/module_from_spec give the synthetic name. The except branch's cache-identity test pops sys.modules only for a fresh module that failed. Caveat filed as advisory: the fixture's __file__ criterion misses namespace subpackages.

#### C117 — SURVIVED
- evidence: `C:/Python313/Lib/dataclasses.py:757`
- reasoning: dataclasses evaluates string annotations via sys.modules.get(cls.__module__).__dict__ (dataclasses.py:757). module_from_spec sets __name__ to spec.name, the synthetic name, so registering it before exec_module is what makes that lookup succeed.

#### C118 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_import_graph.py:76, plugins/arch-compliance/python/acf/adr/contract.py:20, plugins/arch-compliance/python/acf/judge.py:16, plugins/arch-compliance/python/acf/engine.py:8`
- reasoning: engine imports only pathlib (:8), so registry → engine is acyclic. registry imports nothing from detectors, and no scanner imports registry or judge (I grepped detector imports). adr already imports engine (contract.py:20). The import-graph test checks only the literal text 'acf.adr' in the hook files (:74-76) and the 'scripts' prefix in adr. judge imports registry (:16), not the reverse.

#### C119 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:53, plugins/arch-compliance/python/acf/registry.py:64`
- reasoning: load_model_file(path, Mandate, subject='mandates file', fmt='yaml', many=True) is at :53-55 and MandateRegistry(mandates=mandates, source_path=path.as_posix()) at :64. Only the known_detectors type changes (frozenset to Mapping), and test_registry.py:30 is updated per §4.7.

#### C120 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_repo_paths.py:48, plugins/arch-compliance/hooks/posttooluse_gate.py:11`
- reasoning: The allowlist entry for the hook (test_repo_paths.py:47-48) is the :11 line verbatim. Line :12 contains no config/architecture spelling and no other test pins it (grep).

#### C121 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:80, config/architecture/mandates.yml:60`
- reasoning: _is_bare_or_exception matches only type None or Name 'Exception' (:78-82). count_bare_excepts uses the same test (fail_loud_ratchet.py:31-34), so an except BaseException handler is not flagged. mandates.yml:60 is the bare-except-ok token line.

#### C122 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/engine.py:17, plugins/arch-compliance/python/acf/engine.py:8`
- reasoning: contains_backslash is at :17. The only import is pathlib (:8). Adding re and ast keeps engine stdlib-only. Not load-bearing.

#### C123 — SURVIVED
- evidence: `README.md:66, plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23, plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15, plugins/arch-compliance/tests/test_registry.py:24`
- reasoning: The README table (:66-74) has 7 Python detector rows with mandate ids, matching the 'every Python key' wording. The TS rule lines carry mandate_id: "..." literals. test_registry builds inline YAML rows at :22-27 and :33-37, the pattern the new cases need.

#### C124 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_diff_cli.py:25, plugins/arch-compliance/tests/test_hooks.py:14, plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:30`
- reasoning: test_diff_cli already builds tmp git repos and runs main in process (:25, :48). test_hooks runs the gate in a subprocess (:14, :22-29). The TS detectors need node_modules (typescript_bridge.py:30-35), which CI installs. The ratchet needs a fixture baseline file. Every detector can be triggered by a small fixture tree.

#### C125 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:184, plugins/arch-compliance/hooks/posttooluse_gate.py:295, plugins/arch-compliance/python/acf/cli_check_diff.py:109`
- reasoning: file_lines is local to _scan_changed (:109, returned at :184) and to _scan_paths (:226, :295). Calling scan_host_guards inside both functions puts it under each gate's scan try (cli_check_diff.py:71; hook :114). Filling only missing keys preserves gate reads.

#### C126 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:61, plugins/arch-compliance/python/acf/cli_check_diff.py:69`
- reasoning: The parser is built at :29-61. With required=True and choices, argparse raises SystemExit(2) inside main for a missing or unknown value. The try at :69-74 already catches AcfInputError, so a post-load empty-selection raise there prints and exits 1.

### Unanchored findings

- **advisory**: fresh_host_loader removes only sys.modules entries whose __file__ is under the served root, so a namespace subpackage such as the origin host's scripts.ci (no __init__.py; __file__ is None) stays cached with its __path__ pointing at a previous test root and can leak across in-process tests over several roots.
  - evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/metadata_facade_guard.py:66`
- **advisory**: C93's reason that importing at load would run host code in the SubagentStart hook and acf-check-llm does not hold, because those callers pass no known_detectors and the host checks sit under that branch. The remaining reasons (CI-only guards imported on every edit) carry the decision, so the stated reason should be corrected.
  - evidence: `plugins/arch-compliance/hooks/inject_constraints.py:104`
- **advisory**: The llm prompt-id rule is enforced only where acf-check-diff passes llm_prompt_ids. Moving LLM_PROMPT_IDS to a stdlib-only module that acf.registry can import (judge imports registry, so the reverse is the cycle) would give it one owner and enforce it on every load, the hook and SubagentStart included, without pulling httpx.
  - evidence: `plugins/arch-compliance/python/acf/judge.py:29`
- **advisory**: The TypeScript bridge keeps the Node rules' literal mandate_id and refuses a mismatch at run time. Dropping mandate_id from the Node output and stamping from TS_MANDATE_IDS alone would remove both the second spelling and the check (rung 2 instead of rung 3).
  - evidence: `plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23`

### Looked for but did not find

- A production producer of a second host root: each entry point resolves one repo (cli_check_diff.py:63, posttooluse_gate.py:65); only in-process tests do
- A traceback path for host-detector failures outside both gates' scan try: none; load, call, consume, rebuild, format and guard-file read are all wrapped
- A shipped registry with two active rows for one built-in detector, a built-in row whose id differs from its stamped mandate id, or an llm row naming an unknown prompt id: none, after loading all four registries
- A live origin-host site raising an exception that carries a host object with a raising __str__: none found by grep; _describe guards the external host boundary generically
- A shadowing hazard from the appended host root for the origin host: site-packages exposes a namespace 'scripts' on this machine, but the origin host's scripts/ is a regular package and wins
- resolve_under_root mapping a symlink loop to None: classifies the path as not a contained file, which is semantically accurate; cleared
- scan_host_guards filling [] for a missing or outside flagged path: leaves the finding non-exempt (fail-safe), not a repair
- Ratchet roots/baseline: the design replaces the silent 'if not search.exists(): continue' skip (fail_loud_ratchet.py:56-57) with a refusal, which hardens the producer
- fresh_host_loader: test-only reset, no production repair mechanism

### Mechanism traces

- **Mandate._row_shape model_validator**
  - invalid state: row.detection in {ast,guard} and (':' in detector and parse_host_detector_ref fails) or (status != unenforced and not TIER1_CALL_SITES & set(call_sites)) or (active host ast row and languages == 'none')
  - producer: `plugins/arch-compliance/python/acf/loader.py:71`
  - rung 1 (highest applicable 1); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:206`
- **_check_builtin built-in contract (load_mandates with known_detectors)**
  - invalid state: active built-in ast/guard row with detector not in KNOWN_DETECTORS, or id != KNOWN_DETECTORS[detector].mandate_id, or TIER1_CALL_SITES & call_sites not a subset of the contract's call_sites
  - producer: `plugins/arch-compliance/python/acf/detectors/python_pack.py:67`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: Consequence, accepted: with unique row ids (registry.py:33-41), a host has at most one active row per built-in detector.
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:287`
- **Host detector file existence check in load_mandates**
  - invalid state: active host ast/guard row whose file_under_root(repo_root, rel_path) is None or whose stat raises OSError
  - producer: `plugins/arch-compliance/python/acf/registry.py:53`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:272`
- **llm_prompt_ids refusal in load_mandates**
  - invalid state: row.status != unenforced and row.detection == 'llm' and row.detector not in LLM_PROMPT_IDS
  - producer: `plugins/arch-compliance/python/acf/judge.py:29`
  - rung 3 (highest applicable 2); repairs=False
  - hardening rejected because: The PostToolUse hook does not pass it: the hook runs no `llm` row, and importing `acf.judge` would add `httpx` (`plugins/arch-compliance/python/acf/judge.py:11`) to every edit.
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:253`
- **apply_registry call_sites filter**
  - invalid state: finding whose row exists but not row.runs_at(gate_call_sites)
  - producer: `plugins/arch-compliance/python/acf/cli_check_diff.py:127`
  - rung 2 (highest applicable 2); repairs=False
  - hardening rejected because: This filter is needed at that one sink because the built-in scanners emit findings without consulting the registry (`plugins/arch-compliance/python/acf/detectors/python_pack.py:27-52`).
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:425`
- **Empty call-site selection refusal in acf-check-diff**
  - invalid state: registry.active(frozenset({args.call_site})) contains no row with detection in {ast,guard}
  - producer: `plugins/arch-compliance/profiles/python-service/mandates.yml:18`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:444`
- **One host root per process refusal (load_host_detector)**
  - invalid state: load_host_detector called with repo_root.resolve() != _ACTIVE_ROOT where _ACTIVE_ROOT is not None
  - producer: `plugins/arch-compliance/tests/test_diff_cli.py:48`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: One host root per process, refused rather than repaired
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:346`
- **Wrapped host module exec and callable lookup (UnknownDetectorError, sys.modules removal on failed exec)**
  - invalid state: spec_from_file_location returns None, exec_module raises any non-KeyboardInterrupt exception, getattr raises, or the attribute is not callable
  - producer: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/metadata_facade_guard.py:66`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:361`
- **_call_host with _revalidate**
  - invalid state: host callable raises, returns None/str/bytes/non-iterable, or yields an item where type(item) is not HostHit or whose fields are not exactly str/int/str or fail HostHit validation
  - producer: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/genre_conditional_guard.py:33`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:373`
- **_describe constant-message fallback**
  - invalid state: f'{type(exc).__name__}: {exc}' raises for a host exception (for example args[0].__str__ raises)
  - producer: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/genre_conditional_guard.py:39`
  - rung 5 (highest applicable 5); repairs=True
  - hardening rejected because: because `str(exc)` runs host code after the `try` has exited
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:400`
- **_to_findings ast path check**
  - invalid state: mandate.detection == 'ast' and hit.path != expected_path
  - producer: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/genre_conditional_guard.py:35`
  - rung 3 (highest applicable 1); repairs=False
  - hardening rejected because: The `ast` path check refuses rather than making a wrong path unrepresentable, because one `HostHit` type serves both callable kinds, and a path-less `ast` hit would be a second type carrying the same facts.
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:408`
- **TypeScript bridge TS_MANDATE_IDS cross-check**
  - invalid state: Node scanner item with detector not in TS_MANDATE_IDS or item['mandate_id'] != TS_MANDATE_IDS[item['detector']]
  - producer: `plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23`
  - rung 3 (highest applicable 2); repairs=False
  - hardening rejected because: the bridge stamps the Python value and refuses a Node value that differs (§4.3), so the Node literal is a checked echo, not a second source.
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:312`
- **Ratchet baseline/roots containment and existence refusal**
  - invalid state: params.baseline with file_under_root(repo, baseline) is None, or a params.roots entry with resolve_under_root(repo, r) is None or not is_dir()
  - producer: `config/architecture/mandates.yml:97`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:514`

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
- **C29** [premise] [load-bearing]: getattr(mod, attr, None) swallows only AttributeError, so a host module-level __getattr__ raising anything else escapes a bare lookup; in spec §4.4 item 3 exec_module and the lookup share one try whose `except BaseException` handler re-raises KeyboardInterrupt and turns every other exception into UnknownDetectorError, which cli_check_diff.py:72 and the hook's widened scan except catch. A failed exec_module removes the module from sys.modules; a failed lookup on a cached module leaves it cached.
  - spec citation: `None`
- **C30** [premise] [load-bearing]: pyproject.toml:5 allows Python 3.11, where a non-strict Path.resolve() raises RuntimeError on a symlink loop (3.13 does not); resolve_under_root catching RuntimeError and returning None makes a looping host path report as a missing file at load (UnknownDetectorError), yield [] exemption lines in scan_host_guards, or classify as unresolved in citations, never a traceback.
  - spec citation: `pyproject.toml:5`
- **C31** [premise] [load-bearing]: The TypeScript bridge's Finding construction sits in a try at typescript_bridge.py:82-95 whose except (KeyError, TypeError, ValueError) re-raises as DetectorPackError (:94-95); stamping mandate_id=TS_MANDATE_IDS[item['detector']] and raising ValueError on a differing item['mandate_id'] inside it yields DetectorPackError for an unknown detector or a mismatch, and the Node rules' literals (emptyCatch.ts:23, explicitAny.ts:15) equal the TS_MANDATE_IDS values, so no shipped finding is refused.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:82-95`
- **C32** [premise] [load-bearing]: Decision 6's entry-point table is accurate: the PostToolUse hook inserts the plugin's python/ at sys.path[0] ahead of the hooks directory (posttooluse_gate.py:22-26) and imports acf first (:28), so the host root is not on sys.path before the loader appends it; the acf-check-diff console script (pyproject.toml:19-20) likewise; under python -m acf.cli_check_diff run from the host root (.github/workflows/ci.yml:40) the working directory is already sys.path[0], so appending changes nothing there. Host intra-repo imports such as hm:scripts/ci/metadata_facade_guard.py:66 resolve against the host root in the documented invocations.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:22-28`
- **C33** [premise] [load-bearing]: acf-check-diff today has no argument naming its call site (cli_check_diff.py:29-61 offers --mode, --base, --repo, --mandates, --json), so it cannot tell a pre-commit run from a CI run; the origin host's guard runner selects rows per --site (hm:scripts/ci/run_guards.py:116), refuses an unknown site (:107-111) and an empty selection (:126-130), with --site defaulting to ci (:317-321).
  - spec citation: `hm:scripts/ci/run_guards.py:116`
- **C34** [premise] [load-bearing]: file_lines holds only changed .py/.ts/.tsx files (cli_check_diff.py:126, :152; posttooluse_gate.py:248-252) plus, under the design, files a host guard flagged; built-in line-1 findings (fail_loud_ratchet.py:135, build_artifacts.py:34) on any other file still get '' and stay non-exemptable, as at a338cad, and a staged dist/x.py is already in file_lines today.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:135`
- **C35** [premise] [load-bearing]: No shipped or fixture registry row declares precommit today (git grep -n precommit -- '*.yml' prints nothing); adding precommit to each ast/guard row that declares ci (9 rows in config/architecture/mandates.yml, 7 in profiles/python-service, 3 in profiles/react-app, 3 in tests/fixtures/mandates_valid.yml) makes acf-check-diff --call-site precommit select exactly the rows acf-check-diff runs today, and refusing a site that selects no active ast/guard row prevents a clean report over an empty selection.
  - spec citation: `None`
- **C36** [premise] [load-bearing]: _revalidate (type(item) is HostHit, then exact type(...) is str/int/str checks on the item's __dict__ values, then HostHit.model_validate) inside _call_host's try refuses a host subclass and a model_construct or mutated hit with non-exact field types (b'a.py', '5', True, objects), rebuilds genuine hits unchanged (normal validation already yields exact str and int), and leaves _to_findings running no host code.
  - spec citation: `None`
- **C37** [premise] [load-bearing]: acf.engine.file_under_root (resolve_under_root, then Path.is_file, OSError from stat propagating) returns None for a missing path, a directory, an out-of-root path and a symlink loop on Python 3.11 to 3.13, and each runtime caller in spec §4.2, §4.4 and §4.9 (load_mandates, load_host_detector, scan_host_guards, scan_ratchet) catches OSError around it and raises its typed error, while the PostToolUse hook's _collect_paths lets it propagate exactly as its is_file() at posttooluse_gate.py:239 does today, so a permission-denied stat ends in UnknownDetectorError or DetectorPackError, not a traceback.
  - spec citation: `None`
- **C38** [premise] [load-bearing]: The design leaves AdrHostConfig.runs_dir and ledger_path (plugins/arch-compliance/python/acf/adr/host.py:24-25) unchanged, consistent with the approved ADR gate contract's decision not to refuse absolute or '..' values there ('That is a visible host choice, not a state the gate must prevent', ADR_GATE_HOST_CONTRACT.md:295-301); no section of the spec validates, tests or documents those fields as refused.
  - spec citation: `docs/design/ADR_GATE_HOST_CONTRACT.md:295-301`
- **C39** [premise] [load-bearing]: Switching the ratchet to file_under_root for params.baseline and to resolve_under_root plus an is_dir check for each params.roots entry refuses an entry that escapes the root (an absolute path outside it included), loops, or (for roots) names no existing directory, still accepts an absolute path inside the root as today, refuses no shipped or tested value (baseline config/architecture/fail_loud_ratchet.json, roots ['.'], RATCHET_BASELINE_REL, test_portable_guards.py:107 roots=['pkg'] after creating tmp_path/'pkg'), and raises DetectorPackError, which acf-check-diff already catches (cli_check_diff.py:72).
  - spec citation: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:122-124`
- **C40** [premise] [load-bearing]: A host exception whose str() raises has a concrete producer: BaseException.__str__ returns str(args[0]) for a one-argument exception, and hm:scripts/ci/genre_conditional_guard.py:33-40 declares a non-frozen dataclass Finding whose __str__ calls self.line_text.strip(); a dataclass does not enforce its annotations, so ValueError(Finding('a.md', 3, None, '...')) raises AttributeError when formatted, the case _describe handles inside each handler.
  - spec citation: `hm:scripts/ci/genre_conditional_guard.py:33-40`
- **C41** [premise] [load-bearing]: In _call_host, items = list(raw) inside the try consumes a host iterator to completion, or lets its exception propagate, before _revalidate runs, so a generator the runner holds is never left suspended when _revalidate refuses an item, and any finally body of that generator runs inside the wrapped region.
  - spec citation: `None`
- **C42** [premise] [load-bearing]: test_unenforced_mandate_does_not_gate is the only existing test whose registry has no active ast/guard row, so it is the only existing test the empty-selection refusal reaches; an added active no-shims.hasattr row with call_sites [ci] does not fire on the staged bad.py (which contains no hasattr), so the test still exits 0 and still shows the unenforced row does not gate.
  - spec citation: `plugins/arch-compliance/tests/test_diff_cli.py:102-108`
- **C43** [premise] [load-bearing]: Replacing the hook's `abs_path = p.resolve() if p.is_absolute() else (repo / p).resolve()` (posttooluse_gate.py:203-204) with file_under_root(repo, raw), and deleting _scan_paths' is_file skip (:239) and try/except ValueError (:242-245), keeps every edited in-repo regular file the hook scans today under the same repo-relative key, for relative and absolute harness strings alike, and drops only edited files outside the repository; abs_path.relative_to(repo) then cannot fail because resolve_repo returns a resolved path (repo.py:41-44); no test in plugins/arch-compliance/tests/test_hooks.py exercises an out-of-repo path.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:203-204`
- **C44** [premise] [load-bearing]: Because a partial row gates like an enforced one (acf-mandate SKILL.md:57), the design's load refusals (unknown built-in detector, unknown llm prompt id, malformed host reference) reach partial rows; a host that followed :58's advice to prefer partial for a detector or prompt that does not exist yet is refused at load until it sets such rows to unenforced; no shipped or fixture registry in this repository has a partial row naming a detector or prompt that does not exist; and the spec lists this as an accepted consequence with an upgrade-note step (Decision 3, §4.8).
  - spec citation: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:57-58`
- **C45** [root_cause] [load-bearing]: Root cause of the registry/gate disagreement: a status: partial row is live in both Tier-1 gates (enforcement.py:47 drops only 'unenforced'; the gates' row filters likewise), yet load_mandates never checks it, so a host can name a non-built-in detector in a partial ast/guard row today, load cleanly with known_detectors=KNOWN_DETECTORS, and have nothing ever execute it.
  - spec citation: `plugins/arch-compliance/python/acf/enforcement.py:47`
- **C46** [root_cause] [load-bearing]: Root cause of the hook defect: posttooluse_gate.py:107 calls load_mandates(mandates_path) without known_detectors, so an active row naming an unknown detector is never validated in the PostToolUse hook and produces zero findings at edit time instead of failing loud.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:107`
- **C47** [root_cause] [load-bearing]: Root cause of the exemption defect: the _line_lookup closures (cli_check_diff.py:76-80, posttooluse_gate.py:119-123) are token-identical and consult only file_lines, which holds changed .py/.ts/.tsx files (cli_check_diff.py:126, :152; posttooluse_gate.py:248-252), so a finding on any other file gets "" and apply_registry (enforcement.py:49-50) cannot see an inline exemption token on it.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80`
- **C48** [deletion] [load-bearing]: Deleting citations._looks_absolute (:49-51) and _escapes_repo (:74-76) is safe: their only references are the call sites at citations.py:161 and :163, no test imports them, resolve_citation keeps its order, and exactly two behaviours change, both stated in spec §4.1 and §4.9: a drive-relative string such as 'C:a/b.py' classifies external, and on Python 3.11 and 3.12 a symlink-loop citation classifies unresolved instead of raising RuntimeError.
  - spec citation: `plugins/arch-compliance/python/acf/adr/citations.py:74-76`
- **C49** [deletion] [load-bearing]: Deleting cli_check_diff._active_mandates and the hook's inline filters in favour of registry.active(call_sites, detector=...) changes no selection except by call_sites: for every shipped registry, the only built-in row that stops running at a gate is no-shims.hasattr leaving the PostToolUse hook (it declares [ci]).
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99`
- **C50** [deletion] [load-bearing]: Removing LLM_PROMPT_IDS from KNOWN_DETECTORS changes behaviour only for ast/guard rows naming an LLM prompt id: load_mandates consults known_detectors only for ast/guard rows (registry.py:60), and no code reads KNOWN_DETECTORS for llm rows. The import at cli_check_diff.py:21 stays and feeds load_mandates(..., llm_prompt_ids=LLM_PROMPT_IDS), so LLM_PROMPT_IDS keeps a runtime consumer.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:21`
- **C51** [deletion] [load-bearing]: Replacing the literal mandate ids in the five scanner modules with module constants changes no emitted finding, and no test asserts on the scanner source text in a way the change would break.
  - spec citation: `None`
- **C52** [deletion] [load-bearing]: Deleting the two _line_lookup closures (cli_check_diff.py:76-80, posttooluse_gate.py:119-123) for make_line_lookup(file_lines), which is their body unchanged and reads no file, changes no exemption result for any finding at a338cad. The only new lines in file_lines are those scan_host_guards adds for files a host guard flags, so a built-in finding on such a file becomes exemptable as built-in findings on changed code files already are; a built-in finding on any other file still gets ''.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80`
- **C53** [deletion] [load-bearing]: Deleting the five detector-id sets (PYTHON_AST_DETECTOR_IDS, GUARD_DETECTOR_IDS, CONFIG_AST_DETECTOR_IDS, ALL_PYTHON_DETECTOR_IDS, TS_DETECTOR_IDS) touches only the references git grep -n "_DETECTOR_IDS" -- plugins tests prints, each of which the spec rewrites, and leaves KNOWN_DETECTORS as the only set of built-in detector ids in plugins/arch-compliance/python.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/__init__.py:11-28`
- **C54** [deletion] [load-bearing]: Replacing the inline params extraction in both gates with facade_sink_args, fsm_guard_args and build_artifact_args (required arguments as str(params.get(key, '')); allowlist_globs and atomic_is_sink passed unchanged when the key is present, null included; path_prefixes only when present and non-empty) produces the same scanner call for every row as today, because the scanners' signature defaults (facade_sinks.py:24-25, build_artifacts.py:16, :23) equal what the gates pass today when the param is absent.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/facade_sinks.py:24-25`
- **C55** [deletion] [load-bearing]: Replacing the four parse-and-skip copies with acf.engine.parse_python changes no scanner output, and no other site in plugins/arch-compliance/python parses Python with a SyntaxError skip.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37`
- **C56** [deletion] [load-bearing]: Once each params.roots entry is resolved and contained with resolve_under_root, every path rglob yields under it keeps the resolved root as a lexical prefix, so the walk filter's except ValueError: continue (fail_loud_ratchet.py:59-62) cannot fire and deleting that branch changes no count; scan_tree's callers are scan_ratchet and test_portable_guards.py:107.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:59-62`
- **C57** [mandate] [load-bearing]: ## Fail loud: every invalid state in spec §6.1 is refused by the named component with the named error, including: acf-check-diff without --call-site (usage error, exit 2) or with a site selecting no active ast/guard row (AcfInputError); a host module whose import or callable lookup raises any exception but KeyboardInterrupt (UnknownDetectorError); a host callable or its result raising any exception but KeyboardInterrupt, or yielding a non-exact-type or invalid HostHit (DetectorPackError); a host path whose stat raises OSError (typed error at each caller); a ratchet roots entry naming no existing directory (DetectorPackError); a TypeScript item with an unknown detector or differing mandate_id; an llm row with an unknown prompt id. Of the design's three broad handlers, the load and call handlers re-raise as typed errors; _describe's handler swallows only a failure to format the host's exception, returning a constant message inside the typed error still raised, and carries the fail-loud.bare-except-ok token with its reason, as ARCHITECTURE.md:29-30 permits for a handler 'explicitly exempted with a reason'.
  - spec citation: `None`
- **C58** [mandate] [load-bearing]: ## Fail loud: no active built-in ast/guard row can load with known_detectors yet never receive a finding from either Tier-1 gate: _check_builtin refuses a detector not in KNOWN_DETECTORS (LLM prompt ids are not keys), a row id that differs from the detector's stamped mandate_id, and any declared Tier-1 call site outside the detector's contract call_sites (fail_loud_ratchet: DIFF only); and Mandate._row_shape refuses an active ast/guard row with no Tier-1 site. Host rows are dispatched by both gates' host runners at any Tier-1 site.
  - spec citation: `None`
- **C59** [mandate]: ## Declared, never defaulted governs the ADR gate's host values in config/architecture/adr.yml and this design adds none of those; the spec states that it follows the same practice by choice for the values it adds (repo_root required for an active host row, apply_registry's call_sites keyword without a default, --call-site required) and does not claim the section requires it.
  - spec citation: `config/architecture/ARCHITECTURE.md:118-133`
- **C60** [mandate]: ## No shims: callable lookup is getattr(mod, attr, None) followed by callable() and a raise; no hasattr, and no host-detector failure has a silent fallback.
  - spec citation: `config/architecture/ARCHITECTURE.md:43-53`
- **C61** [mandate]: ## POSIX paths: HostHit.path is validated by validate_posix_rel_path (which refuses backslashes) and error messages use .as_posix().
  - spec citation: `config/architecture/ARCHITECTURE.md:55-64`
- **C62** [mandate]: ## One base exception: the design adds no exception class and uses AcfInputError, UnknownDetectorError and DetectorPackError (exceptions.py:5, :13, :29), all subclassing AcfError.
  - spec citation: `plugins/arch-compliance/python/acf/exceptions.py:5`
- **C63** [mandate]: ## One owner for host paths: acf/engine.py, acf/registry.py, acf/detectors/__init__.py and the new acf/detectors/host.py spell no config/architecture path, and the acf-mandate skill snippet takes MANDATES_REL and resolve_repo from acf.repo.
  - spec citation: `None`
- **C64** [mandate]: ## Prose names no host: the runtime messages in §4.2-§4.4 and the prose changes in §4.8 name no origin host.
  - spec citation: `config/architecture/ARCHITECTURE.md:135-143`
- **C65** [mandate]: ## Live consumers: each new export in §6.2 has the named non-test caller (file_under_root: load_mandates, load_host_detector, scan_host_guards, scan_ratchet, the hook's _collect_paths; parse_python: four scanners and scan_host_ast_file; the *_args functions: both gates; CallSite: Mandate.call_sites; DIFF_CALL_SITES: acf-check-diff's --call-site choices and KNOWN_DETECTORS), acf.judge.LLM_PROMPT_IDS keeps a runtime consumer, and the five deleted detector-id sets leave no dead export behind.
  - spec citation: `None`
- **C66** [mandate]: ## No completeness claims: every population claim in the spec carries a re-runnable recipe (§1, §3, Appendix) or is a per-item table, as ARCHITECTURE.md:159-169 requires.
  - spec citation: `config/architecture/ARCHITECTURE.md:159-169`
- **C67** [mandate]: ## Declared text decoding: the new read_text calls (cli_check_diff.py TypeScript branch, scan_host_guards' read of flagged files) declare encoding='utf-8'; errors='replace' in scan_host_guards is permitted by that rule, which governs the declared encoding; no subprocess is added.
  - spec citation: `None`
- **C68** [mandate]: ## Release discipline: because shipped skill prose changes, the version is bumped 0.2.2 -> 0.2.3 in both files ARCHITECTURE.md:186-187 names (pyproject.toml:3, plugins/arch-compliance/.claude-plugin/plugin.json:3).
  - spec citation: `config/architecture/ARCHITECTURE.md:184-194`
- **C69** [mandate]: ## Single point of definition: each existing definition listed in spec §4.9 is deleted and its callers switched (citations' path helpers, the five detector-id sets, the line-lookup closures, the active-row filters, the duplicated params extraction, the ratchet's joins, existence check and unreachable walk-filter branch, the four parse-and-skip copies, test_self_host's resolve-and-is_file), the scanners' signature defaults stay the one default for optional params, and the spec makes no claim that §4.9 lists every duplicate in the tree.
  - spec citation: `None`
- **C70** [mandate]: ## Scoped refactor: Decision 8 deletes the existing definitions §4.9 lists, each duplicated by a new definition in this design, in the code paths it changes, and makes no claim beyond that list; the two pre-existing dispatch loops stay (two call sites of one procedure), and the git-supplied join-and-is_file in _scan_changed (cli_check_diff.py:118-119) is a different job recorded as ADJACENT.
  - spec citation: `config/architecture/ARCHITECTURE.md:213-215`
- **C71** [mandate]: ## Frozen ledger format: the design changes no ledger model.
  - spec citation: `config/architecture/ARCHITECTURE.md:145-151`
- **C72** [mandate]: The design complies with the five portable governing principles at docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51 and fulfils that spec's call for project-specific detector extension points (:102, :123, :125).
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51`
- **C73** [mandate]: ## Fail loud: scan_host_guards mapping a flagged path for which file_under_root returns None (missing, directory, outside the root, symlink loop) to [] and decoding with errors='replace' hides no failure: such a path has no line that could carry an exemption token, so the finding stays; an OSError from the stat or the read raises DetectorPackError inside each gate's scan try; and make_line_lookup does no I/O.
  - spec citation: `None`
- **C74** [mandate] [load-bearing]: ## Fail-loud ratchet: the design keeps the ratchet's whole-tree freeze unchanged, routes it to ci and precommit only through KNOWN_DETECTORS, refuses a baseline or roots entry outside the repository or a roots entry naming no directory (DetectorPackError), and §4.8 adds both constraints to the section's enablement instruction (ARCHITECTURE.md:72-73).
  - spec citation: `config/architecture/ARCHITECTURE.md:70-73`
- **C75** [shape_fit] [load-bearing]: Mandate.runs_at and MandateRegistry.active become the single definition of 'this row runs at this gate' for the Tier-1 gates; after the change no other Tier-1 site (cli_check_diff, posttooluse_gate, enforcement, the host runners) keeps its own active-row filter.
  - spec citation: `None`
- **C76** [shape_fit] [load-bearing]: After the design, deciding whether a path string from outside the code (registry row, host hit, harness payload) lies inside the repository root has one implementation, acf.engine.resolve_under_root, used directly or through file_under_root by validate_posix_rel_path's callers, citations.py, the ratchet, load_mandates, load_host_detector, scan_host_guards, the PostToolUse hook's _collect_paths and tests/test_self_host.py:40; recipe `git grep -n "is_absolute()\|relative_to(" -- plugins/arch-compliance/hooks plugins/arch-compliance/python` prints posttooluse_gate.py:204 and :243, citations.py:76, fail_loud_ratchet.py:60 and :123, of which the spec switches or deletes :204, the except around :243, citations.py:76 and :123, and keeps :243 and :60 only as conversions of an already-contained Path; parse_python is the one parse-or-skip (four scanners and scan_host_ast_file).
  - spec citation: `None`
- **C77** [shape_fit] [load-bearing]: Building Finding from a validated HostHit in acf.detectors.host is ADJACENT to, not a partial duplicate of, the TypeScript bridge's JSON-to-Finding coercion (typescript_bridge.py:75-95), because the inputs share no format.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:75-95`
- **C78** [shape_fit] [load-bearing]: Building Finding from a HostHit is ADJACENT to the judge's _to_finding (judge.py:238-255): the judge demotes severity by confidence and admits path="<diff>" and line=0, while host findings take severity from the row and require a relative path and line >= 1, so no shared constructor is warranted.
  - spec citation: `plugins/arch-compliance/python/acf/judge.py:236-253`
- **C79** [shape_fit] [load-bearing]: acf/detectors/host.py partially duplicates no existing mechanism: nothing in the plugin today loads or executes code from a registry-supplied file path, and the loader's one-time append of a host root to the end of sys.path is ADJACENT to the hooks' own start-up insertion of the plugin's python/ directory (posttooluse_gate.py:22-26, inject_constraints.py:28-29).
  - spec citation: `None`
- **C80** [shape_fit] [load-bearing]: make_line_lookup consolidates the only two line-lookup closures passed to apply_registry; no third LineLookup implementation exists (e.g. in cli_check_llm.py, the judge, or any skill snippet) that would remain a second definition.
  - spec citation: `None`
- **C81** [shape_fit] [load-bearing]: Detector-reference validation lives in two cooperating places only, Mandate._row_shape (row-local rules, every caller) and load_mandates with known_detectors (built-in contracts and host-file existence); no other validator (the acf-mandate skill's ## Validate snippet, test_profile_drift.py, the architecture-review skill, acf-setup) independently checks detector ids or call sites in a way that would diverge.
  - spec citation: `None`
- **C82** [shape_fit] [load-bearing]: The §4.7 contract-against-dispatch test ties KNOWN_DETECTORS' call_sites to the gates' dispatch: a detector the table says runs at a gate but which that gate does not dispatch fails the test; the opposite drift cannot attach a finding to any loaded row, because _check_builtin refuses a row declaring that site and apply_registry drops a finding whose row does not run at the gate, so it over-refuses and never silently drops a row.
  - spec citation: `None`
- **C83** [shape_fit] [load-bearing]: resolve_under_root SUBSUMES the PostToolUse hook's Path.is_absolute() join with its relative_to/except ValueError containment test (posttooluse_gate.py:203-204, :242-245) and the ratchet walk filter's except ValueError (fail_loud_ratchet.py:59-62): each decides by hand whether a path lies in the root; the spec deletes those branches and keeps only relative_to(...).as_posix() as the conversion of an already-contained Path to its key, and §4.1, §4.6, §4.9 and §5.2 state this consistently.
  - spec citation: `None`
- **C84** [shape_fit] [load-bearing]: The spec's account of where host code runs is consistent: Decision 7 guarantees that every failure raised while a runner calls host code (module execution, callable lookup, the call, consuming and rebuilding its result, formatting its exception) becomes a typed ACF error, and states that the wrapping does not confine host code (atexit handlers, threads); no other section claims that host code runs only inside the wrapped regions; and the fresh_host_loader fixture is the single reset of loader state.
  - spec citation: `None`
- **C85** [shape_fit] [load-bearing]: TS_MANDATE_IDS is the single Python definition of the TypeScript mandate ids: the bridge stamps from it, KNOWN_DETECTORS reads it, and no other non-test Python site spells 'fail-loud.empty-catch' or 'no-shims.explicit-any' as a runtime value; the Node literals are checked against it on every finding.
  - spec citation: `None`
- **C86** [shape_fit]: apply_registry is the single owner of Finding.severity on the Tier-1 path (enforcement.py:52); the host runner's severity value is a required-field fill that apply_registry overwrites, as §4.4 item 5 and §5.2 state.
  - spec citation: `None`
- **C87** [shape_fit] [load-bearing]: The join-and-is_file in _scan_changed (cli_check_diff.py:118-119) is ADJACENT to file_under_root, not a duplicate: its path comes only from git diff --name-only --diff-filter=ACMR (diff.py:56), is repo-relative by construction, and is never registry- or host-supplied, so file_under_root's containment job does not apply.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:118-119`
- **C88** [shape_fit]: The not-found refusals of file_under_root's callers (load_mandates, load_host_detector, scan_ratchet) are ADJACENT to acf.loader.require_file (loader.py:24-28): require_file takes an already-built Path for an operator input file and always raises AcfInputError, while these callers first decide containment of a registry-supplied string and raise their phase's error (UnknownDetectorError at load, DetectorPackError in the ratchet).
  - spec citation: `plugins/arch-compliance/python/acf/loader.py:24-28`
- **C89** [sweep] [load-bearing]: Sweep: the call-site vocabulary in use across shipped registries, tests and the origin host is within CallSite {ci, precommit, hook, posttooluse, audit}; after each ast/guard row declaring ci also declares precommit, every active ast/guard row routes to at least one Tier-1 site at which its detector runs, and audit stays read by no Tier-1 gate.
  - spec citation: `None`
- **C90** [sweep] [load-bearing]: Sweep: the test changes in spec §4.7 cover every existing test the design breaks or makes stale, including test_unenforced_mandate_does_not_gate (test_diff_cli.py:102-108, which gains an active no-shims.hasattr row so the empty-selection refusal does not fire), the ten main([...]) calls in test_diff_cli.py (now passing --call-site), the ten apply_registry calls in test_enforcement.py, test_hooks.py:199-218, test_registry.py:30, test_typescript_pack.py:6 and :14, tests/test_self_host.py:23, :40 and :5, test_acf_mandate_skill.py:2 and test_portable_guards.py.
  - spec citation: `None`
- **C91** [sweep]: The §4.7/§4.8 sites cover every shipped doc, skill, docstring, config and test the design makes stale: each command line or instruction for acf-check-diff that the §4.8 recipe prints (.github/workflows/ci.yml:40, README.md:57-58, acf-setup SKILL.md:24, :184, :193, :206, :207, :217, :219, :250 and its success criteria, acf-mandate SKILL.md:131, CLAUDE.md:36, docs/guides/SUPERPOWERS_COMPLEMENT.md:82-83, PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:454), the upgrade note for previously installed hosts (README.md, acf-setup SKILL.md), KNOWN_DETECTORS described as a union, the hook's call-site behaviour, apply_registry's drop rules, and the deleted detector-id sets.
  - spec citation: `None`
- **C92** [sweep]: The §4.8 rows cover the prose this revision makes stale: ARCHITECTURE.md ## Fail-loud ratchet enablement text (:72-73), ARCHITECTURE.md:226-228 naming acf.cli_check_diff.KNOWN_DETECTORS, the acf-mandate SKILL.md:58 partial-row advice and the upgrade note for partial rows, and docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:161 (PostToolUse scans in-repo paths only).
  - spec citation: `None`
- **C93** [mechanism_justification] [load-bearing]: Deferring host import to dispatch (load_mandates checks reference syntax, Tier-1 site, languages, built-in contracts and host-file existence, and imports nothing) is justified: a missing file still fails at load, an import failure or missing callable fails loud at dispatch as UnknownDetectorError caught by both gates' except tuples, and importing at load would run host code in the SubagentStart hook and acf-check-llm and import CI-only guards on every edit.
  - spec citation: `None`
- **C94** [mechanism_justification] [load-bearing]: The row-shape checks on Mandate (host-reference syntax, a Tier-1 site, host ast languages) together with the per-detector BuiltinDetector contracts (known id, matching mandate_id, declared Tier-1 sites within the contract's call_sites) are sufficient to prevent an active ast/guard row that loads with known_detectors yet is run by neither acf-check-diff (DIFF_CALL_SITES) nor the hook (HOOK_CALL_SITES), or whose findings land on no row.
  - spec citation: `None`
- **C95** [mechanism_justification] [load-bearing]: Refusing a second host root in one process (AcfInputError) rather than evicting the old root is justified: every production caller resolves one repository per process, so the refusal never fires in production, and the only multi-root producer (in-process tests) is handled by the test-only fresh_host_loader fixture; no repair mechanism lives in production code.
  - spec citation: `None`
- **C96** [mechanism_justification] [load-bearing]: Declaring, per built-in detector, the mandate id it reports to and the call sites where a gate runs it (BuiltinDetector in KNOWN_DETECTORS) is justified over the alternatives: the scanners stamp fixed mandate ids and run at fixed gates, so the contract records an existing fact rather than adding a capability; the accepted cost (at most one active row per built-in detector) affects no shipped registry.
  - spec citation: `None`
- **C97** [mechanism_justification] [load-bearing]: Moving the row-local rules onto a Mandate model_validator (rather than keeping them in load_mandates) is justified because it makes the SubagentStart hook, acf-check-llm and any direct Mandate construction reject the same malformed rows as the gates; inject_constraints.py catches AcfInputError around load_mandates, and acf-check-llm (cli_check_llm.py:54) leaves it uncaught, so a malformed row there already ends non-zero and the new refusals reach it the same way (spec §3 In scope table).
  - spec citation: `None`
- **C98** [mechanism_justification]: Parsing a Python file once and sharing the tree across every host ast detector on it is justified by avoiding N parses per file; built-in scanners keep their own parses unchanged.
  - spec citation: `None`
- **C99** [mechanism_justification] [load-bearing]: Having host callables return HostHit (path, line, message) and building Finding in the runner from the mandate row, rather than accepting Finding and overwriting fields, is justified because apply_registry matches findings to rows by mandate_id (enforcement.py:37-53) and a host-supplied mandate_id/detector/severity could otherwise attach a finding to the wrong row.
  - spec citation: `None`
- **C100** [mechanism_justification] [load-bearing]: Treating the host's own pre-commit/CI invocation of acf-check-diff as its opt-in to running host code, and gating only the automatic hooks on .acf/enabled, is justified because .acf/ is gitignored and CI would otherwise be disabled; a user who runs acf-check-diff manually in an untrusted checkout is the residual case the design accepts.
  - spec citation: `.gitignore:8`
- **C101** [mechanism_justification] [load-bearing]: The call_sites filter added to apply_registry is needed in addition to the scanners' registry.active(call_sites) selection, because some built-in scanners emit findings by detector id without consulting the registry's call_sites, so without the filter a finding for a row not declared at this gate would survive. (The spec states the filter but gives no reason it is not redundant.)
  - spec citation: `None`
- **C102** [mechanism_justification] [load-bearing]: Appending the host root to the end of sys.path rather than inserting it at the front is justified: it adds no shadowing of standard-library, third-party or plugin modules under the hook and console-script entry points, keeps host intra-repo absolute imports working from the host root, and its stated cost (a host top-level name an earlier entry provides resolves to that entry) fails at import or callable lookup as UnknownDetectorError in the common case; dropping the acf/ refusal removes a check with no producer.
  - spec citation: `None`
- **C103** [mechanism_justification] [load-bearing]: Reading flagged files in scan_host_guards, inside each gate's scan try, instead of lazily in the line lookup is justified: it keeps apply_registry free of I/O and new errors, converts an unreadable file to DetectorPackError where both gates already report it, and limits new exemption lines to files a host guard flagged.
  - spec citation: `None`
- **C104** [mechanism_justification]: Enforcing llm prompt ids at load (llm_prompt_ids, passed by acf-check-diff) is justified: it gives acf.judge.LLM_PROMPT_IDS a runtime consumer after it leaves KNOWN_DETECTORS, makes the acf-mandate skill's stated rule true, and refuses no shipped row; registry.py cannot import acf.judge, so the ids are passed in rather than imported.
  - spec citation: `None`
- **C105** [mechanism_justification] [load-bearing]: A required --call-site argument on acf-check-diff, rather than a default or a site derived from --mode/--base, is justified: the origin host's per-site row selection (hm:scripts/ci/run_guards.py:116), the fact that a missing value then fails loud (usage error) instead of silently running the wrong rows, and the practice of declaring rather than defaulting, which the spec applies by choice (the ## Declared, never defaulted section governs only the ADR gate's host values); the cost, adding the flag at each existing invocation, is listed per site.
  - spec citation: `None`
- **C106** [mechanism_justification] [load-bearing]: Refusing a --call-site that selects no active ast/guard row (AcfInputError), and adding precommit to every shipped row that declares ci, are justified together: without them the documented pre-commit invocation would run no row and report clean, the false green the origin host's runner already refuses (hm:scripts/ci/run_guards.py:126-130).
  - spec citation: `None`
- **C107** [mechanism_justification] [load-bearing]: Rebuilding each yielded item inside _call_host (exact type, exact field types, then validation) is justified over checking the type in _to_findings: field access and comparisons on an unvalidated host object can run host code, so they must happen inside the wrapped region, and a rebuilt HostHit holds only plain str and int values.
  - spec citation: `None`
- **C108** [mechanism_justification]: Decision 8 (delete the existing definitions §4.9 lists and switch their callers) is justified over recording them as debt: it removes code, removes completeness claims about remaining breaches, and each switch's behaviour change is checked against every shipped value (spec §4.9, Appendix); where an approved spec chose otherwise (AdrHostConfig's path fields, ADR_GATE_HOST_CONTRACT.md:295-301), the design keeps that decision.
  - spec citation: `None`
- **C109** [mechanism_justification] [load-bearing]: _describe (format the host exception inside its own try, fall back to a constant message for any exception but KeyboardInterrupt) is justified by a named producer: an exception carrying an origin-host object whose __str__ raises (hm:scripts/ci/genre_conditional_guard.py:33-40); without it, formatting the typed error's message would raise outside the wrapped region and end in a traceback.
  - spec citation: `None`
- **C110** [implementability] [load-bearing]: Mandate (registry.py:14-27) is a Pydantic BaseModel exposing every field the design reads: id, severity, status, detection, detector, call_sites (list[str]), languages (Literal including 'none'), and params (dict or None); adding an @property is_active and a plain method runs_at to it, and a method active to MandateRegistry, is compatible with its model_config.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:14-27`
- **C111** [implementability] [load-bearing]: Finding (acf/finding.py) can be constructed as Finding(mandate_id=, severity=Severity(mandate.severity), path=, line=, message=, detector=, detection=): those are its fields, Severity is constructible from Mandate.severity's value, and no other required field is missing.
  - spec citation: `None`
- **C112** [implementability] [load-bearing]: apply_registry (enforcement.py) looks up each finding's row via registry.by_id, drops it on the status check at :47 (replaceable by runs_at), and handles exemptions and severity at :49-52 using a LineLookup type that make_line_lookup can return.
  - spec citation: `plugins/arch-compliance/python/acf/enforcement.py:47`
- **C113** [implementability] [load-bearing]: cli_check_diff.py has the hook points the design names with the needed names in scope: load at :70 inside a try whose except tuple at :72 lists AcfInputError, UnknownDetectorError and DetectorPackError (and wraps both load and scan); lookup and apply_registry at :76-82; in the .py branch after scan_fsm_writes (:140-150) repo, text, posix, lines and registry; in the .ts/.tsx branch (:151-156) a read that can bind text; and after the ratchet loop (:168-182) the changed-file list.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:72`
- **C114** [implementability] [load-bearing]: posttooluse_gate.py has the hook points the design names: deferred imports at :91-104, the load try at :106-110, the scan try at :113-117 (whose except can be widened to AcfInputError, DetectorPackError, UnknownDetectorError), lookup/apply_registry at :119-125, _collect_paths' resolve-and-dedupe loop at :200-209 where file_under_root replaces the join, the is_file skip at :239 and the relative_to/ValueError fallback at :242-245 that are deleted, inline filters at :229-236 and :284-286, the build-artifact loop at :284-294, and text and rel in scope in the .py and TypeScript branches of _scan_paths.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:113-117`
- **C115** [implementability] [load-bearing]: Host-detector failures reach an existing fail-loud handler in both gates, never a traceback: load_host_detector raises UnknownDetectorError for any exception but KeyboardInterrupt during import or lookup and for a stat OSError, AcfInputError for a second root; _call_host raises DetectorPackError for any exception but KeyboardInterrupt from the call, from consuming the result and from rebuilding each item; scan_host_guards raises DetectorPackError for a stat or read OSError; apply_registry does no I/O; cli_check_diff.py:72 and the hook's widened scan except catch all three error types.
  - spec citation: `None`
- **C116** [implementability] [load-bearing]: load_host_detector is implementable as stated: module-level _ACTIVE_ROOT and _MODULE_CACHE, a one-time sys.path.append of the root, file_under_root for the module path, spec_from_file_location with a None spec or loader refused inside the wrapped region, registering in sys.modules before exec_module and removing it if exec_module raises, and exec plus getattr in one try; and the fresh_host_loader fixture isolates in-process tests over several roots, including test_diff_cli.py's in-process main() calls.
  - spec citation: `None`
- **C117** [implementability] [load-bearing]: Registering the module in sys.modules under its name before spec.loader.exec_module(mod) is what lets a host module define a @dataclass under `from __future__ import annotations` (dataclasses resolves sys.modules[cls.__module__]); importlib.util.spec_from_file_location with a synthetic name supports this.
  - spec citation: `None`
- **C118** [implementability] [load-bearing]: The imports the design adds are cycle-free and allowed: acf.registry imports acf.engine, dataclass and Mapping, and nothing from acf.detectors; acf.detectors/__init__ imports acf.registry (BuiltinDetector, call-site sets) and the scanner modules' constants without a cycle; acf.cli_check_diff re-exports KNOWN_DETECTORS from acf.detectors; acf.detectors.host imports registry, finding, engine and exceptions; acf/adr/citations.py importing acf.engine is permitted by test_adr_import_graph.py; and the hook's new deferred imports (from acf.detectors, not acf.cli_check_diff) do not reach acf.adr or acf.judge.
  - spec citation: `plugins/arch-compliance/tests/test_adr_import_graph.py:70-76`
- **C119** [implementability] [load-bearing]: load_mandates today loads rows via load_model_file(path, Mandate, subject='mandates file', fmt='yaml', many=True) returning a list of Mandate, and builds MandateRegistry(mandates=..., source_path=path.as_posix()), so the §4.2 body is a drop-in extension of the existing function.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:48-64`
- **C120** [implementability]: plugins/arch-compliance/tests/test_repo_paths.py:47-48 pins the text of posttooluse_gate.py's docstring line :11 and not :12, so rewording :12 and keeping :11 verbatim breaks no test.
  - spec citation: `plugins/arch-compliance/tests/test_repo_paths.py:47-48`
- **C121** [implementability]: config/architecture/mandates.yml:60 declares fail-loud.bare-except-ok for fail-loud.bare-except; the design's handlers are `except BaseException` handlers, which _is_bare_or_exception (python_pack.py:78-82) does not flag because it matches only a bare handler or the name Exception, so they pass the gate whether or not they carry the token, and spec §6 says so.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/python_pack.py:78-82`
- **C122** [implementability]: acf/engine.py already defines contains_backslash and is stdlib-only, so adding looks_absolute, resolve_under_root and validate_posix_rel_path with `import re` and `from pathlib import Path` keeps it stdlib-only and gives validate_posix_rel_path its backslash test without a new dependency.
  - spec citation: `plugins/arch-compliance/python/acf/engine.py`
- **C123** [implementability] [load-bearing]: The new tests are implementable against the shipped files: test_builtin_detectors.py can parse the README.md detector table (:66-74) for detector ids and mandate ids and read mandate_id values from emptyCatch.ts:23 and explicitAny.ts:15; and the test_registry.py cases (a fail_loud_ratchet row declaring hook, a fail_loud_bare_except row with another id, an ast row naming an LLM prompt id, a module that raises at import not imported by load_mandates) can be expressed as inline YAML registries like the existing :24 and :35 rows.
  - spec citation: `None`
- **C124** [implementability] [load-bearing]: The contract-against-dispatch test is implementable: acf-check-diff runs in process on a temporary git repository once with --call-site ci and once with --call-site precommit, and the hook in a subprocess with .acf/enabled; a fixture tree can trigger each built-in detector the table assigns to that gate, with one active row per such detector declaring only that gate's sites.
  - spec citation: `None`
- **C125** [implementability] [load-bearing]: scan_host_guards(repo_root, changed_files, registry, file_lines, *, call_sites) is implementable in both gates: file_lines is in scope after each gate's dispatch (cli_check_diff _scan_changed returns it; _scan_paths builds it), the call can run inside _scan_changed and _scan_paths so it sits under each gate's scan try, and filling only missing keys keeps the gate's own reads.
  - spec citation: `None`
- **C126** [implementability] [load-bearing]: The required --call-site argument is implementable at cli_check_diff.py:29-71: argparse required=True with choices=sorted(DIFF_CALL_SITES) exits 2 on a missing or unknown value (SystemExit in process, so test_diff_cli asserts it with pytest.raises), sites = frozenset({args.call_site}) reaches _scan_changed and apply_registry, and the empty-selection refusal can raise AcfInputError inside the existing try at :69-74.
  - spec citation: `None`
