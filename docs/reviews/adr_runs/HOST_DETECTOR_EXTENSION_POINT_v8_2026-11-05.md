# Adversarial design review — full detail

Spec: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md` @ `ce6ccb364708c6107d6f08e4c7c9b0fcc7ca10df`
Kinds: defect, feature
Outcome: **BLOCKED**
Claims: 131 · Reviewers: 4 · Converged: 0

## Blocking reasons

- load-bearing claim C45 (premise) is REFUTED: The claim's causal link covers only the five ids stamped by scan_python_file and scan_typescript_file. It fails for facade.forbid-sink, fsm.transition-guard, ops.no-build-artifacts and fail-loud.ratchet. Those scanners run only per active row whose detector equals the built-in id (cli_check_diff.py:112-113, :158, :168; hook :229-236, :284). Under the design such a row must carry that same id, which unique ids (registry.py:33-41) forbid alongside a host row. So a non-built-in row using one of those four ids receives no findings. The refusal is over-broad there; it is harmless, because no shipped row has such an id.
- load-bearing claim C50 (deletion) is REFUTED: The references are only :49, :74, :161 and :163, and no test imports the helpers, so the deletion is safe. The order is kept. But 'exactly two behaviours change' is false. _escapes_repo lets ValueError escape for a citation with an embedded NUL. On 3.11, resolve's non-strict p.stat() catches only OSError, on any platform. On POSIX, realpath's os.lstat (posixpath.py:451-452) catches only OSError. resolve_under_root catches ValueError and returns None, so such a citation now classifies 'unresolved' instead of raising. That is a third change, listed in neither §4.1 nor §4.9.
- load-bearing claim C80 (shape_fit) is REFUTED: The stated reason, that the inputs share no format, is false at the record level. Each Node item is a JSON object carrying path, line and message, a superset of HostHit's three fields. After v8 both sites (1) validate an untrusted detector-emitted hit and refuse a malformed one as DetectorPackError (typescript_bridge.py:94-95 vs _call_host/_revalidate), and (2) stamp mandate_id from a plugin-side source rather than the detector's echo (TS_MANDATE_IDS vs the row). The spec's §5.2 says they share only the Finding constructor; they share the hit-validation responsibility too. The two validators diverge. The bridge coerces line with lax int() (so '5' or True pass), checks neither line >= 1 nor that message is non-empty, and its path is overwritten by the gate (cli_check_diff.py:154). HostHit refuses all of these. The shared responsibility is 'validate a detector hit's line and message'; the bridge's absolute path and Node-supplied severity are its private parts.
- load-bearing claim C90 (shape_fit) is REFUTED: A git-listed path is repo-relative as a string. But file_under_root's job, as §4.4 item 5 and §5.2 define it, includes resolution through in-repo symlinks, and that job does apply here: git diff --name-only --diff-filter=ACMR (diff.py:56) lists a changed tracked symlink, and is_file() at cli_check_diff.py:119 follows it, so the diff gate reads and scans a target outside the repository under the link's path. After this design the hook, via file_under_root, skips the same file and keys an in-repo link by its target path, so the two gates map one changed path to different files. Worse, scan_host_guards receives the gate's `changed` list unfiltered; a guard that flags such a path is then refused by _to_findings' resolve_under_root as DetectorPackError, failing the gate on a hit the gate itself supplied. The responsibility 'map a changed path to the in-repo file a gate scans' has two owners that disagree.

## Absorptions

- PARTIAL_OVERLAP: "file_under_root in the hook's _collect_paths" shares responsibility 'map a changed or edited path string to the in-repo file a Tier-1 gate scans' with plugins/arch-compliance/python/acf/cli_check_diff.py:118-119 — Both gates resolve a changed path through file_under_root (or one helper such as resolve_changed_file(repo, rel) built on it). The diff gate's lexical repo / path + is_file() collapses into it, and scan_host_guards receives only the contained list, as the hook's rel_paths already are.
- PARTIAL_OVERLAP: 'HostHit validation plus _to_findings' shares responsibility 'validate a detector-emitted (path, line, message) hit and refuse a malformed one as DetectorPackError' with plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:79-95 — One hit-field validator (strict int line >= 1, non-empty str message) that both the bridge's item loop and HostHit apply. The bridge keeps its private parts (absolute path from Node, overwritten by the gate; Node severity; TS_MANDATE_IDS stamping), and the host runner keeps row-derived id and severity.
- SUBSUMED: 'looks_absolute, resolve_under_root' shares responsibility 'decide whether a path string lies inside the repository' with plugins/arch-compliance/python/acf/adr/citations.py:49-51 — citations' private _looks_absolute and _escapes_repo (:49-51, :74-76) are deleted and both call sites consume acf.engine, as the spec states.
- mechanism 'TS bridge mandate_id comparison against TS_MANDATE_IDS' sits at rung 3 when rung 1 applies, with no written justification

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:56-63; plugins/arch-compliance/tests/test_registry.py:20-30`
- reasoning: load_mandates only runs its check when known_detectors is given (:56). It skips status != 'enforced' (:58) and raises UnknownDetectorError only for ast/guard rows whose detector is not in the set (:60-63). test_registry.py:20-30 pins the enforced unknown-detector raise.

#### C2 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:25; plugins/arch-compliance/python/acf/judge.py:29-36; plugins/arch-compliance/python/acf/registry.py:60`
- reasoning: KNOWN_DETECTORS is the frozenset union ALL_PYTHON|TS|LLM_PROMPT_IDS (:25). The recipe git grep shows no other assignment or extension, only imports and load_mandates arguments. The LLM ids are in it (judge.py:29-36), so an ast row naming one passes the membership test at registry.py:60. No scanner dispatches on those ids: the gates select by fixed built-in detector constants.

#### C3 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; plugins/arch-compliance/hooks/posttooluse_gate.py:229-236; plugins/arch-compliance/hooks/posttooluse_gate.py:284-286`
- reasoning: Both loops call only the imported built-in scanners, selected by equality with the built-in detector-id constants. git grep for importlib|import_module|spec_from_file_location|exec_module over python/ and hooks/ printed nothing.

#### C4 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:106-110; plugins/arch-compliance/python/acf/exceptions.py:5; plugins/arch-compliance/python/acf/exceptions.py:13`
- reasoning: The hook wraps load_mandates in `except AcfInputError` only. UnknownDetectorError(AcfError) is a sibling of AcfInputError(AcfError), not a subclass, so it would escape uncaught.

#### C5 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:21; plugins/arch-compliance/python/acf/enforcement.py:47; plugins/arch-compliance/python/acf/adr/ledger.py:83`
- reasoning: The git grep printed exactly registry.py:21 and ledger.py:42 and :83 (surface_call_sites). The gate filters (cli_check_diff.py:98; posttooluse_gate.py:231, :235, :285) test detector and status only. apply_registry tests status only (:47).

#### C6 — SURVIVED
- evidence: `config/architecture/mandates.yml:64-72; plugins/arch-compliance/tests/fixtures/mandates_valid.yml:12-21; plugins/arch-compliance/tests/test_hooks.py:199-218`
- reasoning: The repository row declares [ci] (:70), and so does the fixture's identical row (:18). The hook test edits warn.py with hasattr and asserts 'no-shims.hasattr' in additionalContext (:217). Today the hook ignores call_sites, so it reports the row.

#### C7 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_import_graph.py:70-76; plugins/arch-compliance/python/acf/adr/contract.py:20; plugins/arch-compliance/hooks/posttooluse_gate.py:91-95; plugins/arch-compliance/python/acf/engine.py:6-8`
- reasoning: The test docstring states the intent and the assert checks only the substring 'acf.adr' in the two hook sources. The hook imports acf.enforcement and acf.registry (:92, :95). contract.py:20 imports acf.engine. engine.py imports only pathlib, so the helpers there do not pull acf.adr into the hook's graph.

#### C8 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:214-230`
- reasoning: run_judge selects llm rows by detection (:214), reads status == 'enforced' only to compute has_enforced for resolve_provider (:218-221), and reviews every llm row (:230). It uses no Tier-1 filter.

#### C9 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:28; plugins/arch-compliance/hooks/posttooluse_gate.py:72-81; plugins/arch-compliance/hooks/posttooluse_gate.py:91-107`
- reasoning: The only module-scope acf import is acf.repo (:28). The marker check returns 0 at :81, before the deferred imports (:91-95) and before load_mandates (:107).

#### C10 — SURVIVED
- evidence: `.gitignore:8; .github/workflows/ci.yml:40`
- reasoning: .acf/ is ignored, so a checkout never carries the marker. CI runs `python -m acf.cli_check_diff`, and cli_check_diff.py has no marker check (grep for ENABLED_REL in python/ hits only repo.py).

#### C11 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:103-107; plugins/arch-compliance/python/acf/cli_check_llm.py:54`
- reasoning: inject_constraints catches AcfInputError around load_mandates (:104-105). cli_check_llm calls load_mandates bare at :54, so an AcfInputError already ends the run uncaught with a non-zero exit.

#### C12 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:104-110; plugins/arch-compliance/python/acf/cli_check_llm.py:54-66`
- reasoning: After load_mandates, inject only renders text from the rows (_render_constraints), and cli_check_llm only calls run_judge over llm rows. Neither reaches any dispatch path. Under the spec, load_mandates checks only syntax and file existence.

#### C13 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/baseline.py:7-16`
- reasoning: git ls-files config shows only ARCHITECTURE.md, adr.yml and mandates.yml, so there is no architecture-review host config. baseline.py imports neither the registry nor enforcement, so the design's changes do not reach it.

#### C14 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:20; plugins/arch-compliance/python/acf/registry.py:24; C:/Users/iball/Arduino/Projects/HistoricMansions/config/architecture/mandates.yml:5-14`
- reasoning: At b652fab05, the HM rows carry gemini_anchor and no languages or arch_anchor (a grep count of 'languages:|arch_anchor:' is 0). Both fields are required with no default in Mandate.

#### C15 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/arch_compliance/driver.py:146-163`
- reasoning: At b652fab05 the driver catches SyntaxError and raises in range mode or appends a WARN with `exc.lineno or 0`. It passes the diff-mode `changed` objects (with content) to _scan_facade_guards at :162. The spec's scan_guard signature receives repo_root and paths, not a mode.

#### C16 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:198-200; plugins/arch-compliance/python/acf/cli_check_diff.py:110-121; plugins/arch-compliance/hooks/posttooluse_gate.py:238-254`
- reasoning: The two loops differ as claimed. The diff gate uses git changed_files, added_lines scoping and repo/rel. The hook uses harness paths, resolves them and scans whole files (added_lines=None). Under the spec, host selection and running live only in acf.detectors.host.

#### C17 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:50-53; plugins/arch-compliance/python/acf/detectors/fsm_guard.py:36-39; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:23-26`
- reasoning: Each wraps ast.parse(text) in `except SyntaxError` and returns [] (or 0 in the ratchet).

#### C18 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:70; plugins/arch-compliance/tests/test_registry.py:30; tests/test_self_host.py:23; plugins/arch-compliance/tests/test_profile_drift.py:24`
- reasoning: I ran the recipe. It printed exactly the listed sites. Only cli_check_diff:70, SKILL.md:95, test_profile_drift:24, test_registry:30 and test_self_host:23 pass known_detectors. None of their registries has a host row.

#### C19 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:125; plugins/arch-compliance/python/acf/cli_check_diff.py:82; plugins/arch-compliance/tests/test_enforcement.py:54`
- reasoning: git grep -n 'apply_registry(' -- '*.py' printed the definition (enforcement.py:37) plus exactly the listed twelve call sites.

#### C20 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; plugins/arch-compliance/hooks/posttooluse_gate.py:229-236; plugins/arch-compliance/python/acf/enforcement.py:47; plugins/arch-compliance/hooks/inject_constraints.py:158`
- reasoning: Both recipes printed exactly the listed lines. The wider .status recipe adds registry.py:58, judge.py:218 and inject_constraints.py:158 (an f-string display).

#### C21 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/build_artifacts.py:31; plugins/arch-compliance/python/acf/detectors/python_pack.py:67; plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23; plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15; plugins/arch-compliance/python/acf/enforcement.py:46`
- reasoning: The grep shows one literal mandate_id per detector at the listed lines. The TS rules emit fixed literals. apply_registry looks the row up by finding.mandate_id alone.

#### C22 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:168-182; plugins/arch-compliance/hooks/posttooluse_gate.py:213-295`
- reasoning: scan_ratchet is imported and called only in cli_check_diff (grep). _scan_paths calls python_pack, TS, facade, fsm and build-artifacts at :254, :279-282, :255-277 and :284-294.

#### C23 — SURVIVED
- evidence: `config/architecture/mandates.yml:64-72; plugins/arch-compliance/tests/test_diff_cli.py:71-81; plugins/arch-compliance/tests/test_registry.py:20-30; plugins/arch-compliance/tests/test_hooks.py:220-226`
- reasoning: I executed a census script applying CallSite, _row_shape (Tier-1 site for active ast/guard), the reserved-id rule, _check_builtin (id equals mandate_id; sites within the contract, with the ratchet DIFF-only) and the llm prompt-id rule. It covered the repository, both profiles and the fixture: every row returned ok. The inline rows also pass: test_diff_cli _BARE_EXCEPT_ROW [ci,hook]; test_registry manual [audit] rows; test_judge.py:390 unenforced llm. test_hooks.py:223 only flips every status to unenforced. The only refusal is test_registry's not_a_real_detector (UnknownDetectorError).

#### C24 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/loader.py:70-73; plugins/arch-compliance/tests/test_registry.py:40-47; plugins/arch-compliance/tests/test_enforcement.py:19-30`
- reasoning: load_model_file catches only ValidationError. I executed a check on pydantic 2.13.3: a model_validator raising a non-ValueError Exception subclass propagates with its own type. test_registry.py:46 relies on this for _unique_ids. test_enforcement.py:19 builds an active ast row with [ci] and a built-in detector, which passes _row_shape. test_judge.py:41 and test_template.py:73 build llm rows, which _row_shape skips.

#### C25 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:112; plugins/arch-compliance/tests/test_profile_drift.py:7-24; tests/test_self_host.py:14-23`
- reasoning: Every user imports the name from acf.cli_check_diff (kept as a re-export), passes it to load_mandates, uses sorted() (which yields the keys of a Mapping), or names it in prose. None uses set algebra. test_registry.py:30's frozenset is listed to change.

#### C26 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:63; plugins/arch-compliance/hooks/posttooluse_gate.py:65; plugins/arch-compliance/python/acf/repo.py:32-44`
- reasoning: Each main() resolves exactly one repo through resolve_repo. The hook is a fresh subprocess per invocation (hooks.json command). Only in-process test calls (test_diff_cli) reuse a process.

#### C27 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/__init__.py:11-28; plugins/arch-compliance/python/acf/detectors/python_pack.py:16-22; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:14; plugins/arch-compliance/python/acf/judge.py:29-36`
- reasoning: 3 python_pack ids + 4 guard ids + 2 TS ids = 9, plus 4 LLM ids = 13. The nine non-LLM ids are the spec's map keys.

#### C28 — SURVIVED
- evidence: `config/architecture/mandates.yml:132-142; plugins/arch-compliance/python/acf/judge.py:29-36; plugins/arch-compliance/skills/acf-mandate/SKILL.md:56`
- reasoning: In the census the active llm rows are soft.fail-loud (llm_fail_loud) in the repository and python-service, and soft.react-boundaries (llm_react_boundaries) in react-app. All are in LLM_PROMPT_IDS. The inline test_diff_cli rows are ast only. The test_judge row is unenforced.

#### C29 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:72; plugins/arch-compliance/hooks/posttooluse_gate.py:113-117`
- reasoning: I executed it: a module __getattr__ raising RuntimeError escapes getattr(mod, 'zz', None), because only AttributeError is swallowed. The spec's shared try with `except BaseException` re-raises KeyboardInterrupt and pops sys.modules only when cached is None. cli_check_diff.py:72 already catches UnknownDetectorError, and the hook's scan except is widened to include it.

#### C30 — SURVIVED
- evidence: `pyproject.toml:5; C:/Program Files/KiCad/9.0/bin/Lib/pathlib.py:981-1005; C:/Python313/Lib/pathlib/_local.py:670`
- reasoning: requires-python is >=3.11. The 3.11 stdlib Path.resolve raises RuntimeError on ELOOP (check_eloop). Its non-strict p.stat() catches only OSError, so a NUL path raises ValueError. 3.13 resolve is plain realpath with no RuntimeError. The callers treat None as missing, refused or unresolved.

#### C31 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:82-95; plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23-28; plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15-22`
- reasoning: Finding construction sits in a try whose except (KeyError, TypeError, ValueError) re-raises DetectorPackError. A dict lookup KeyError and an explicit ValueError land there. The Node rules emit empty_catch→fail-loud.empty-catch and explicit_any→no-shims.explicit-any, matching TS_MANDATE_IDS.

#### C32 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:22-28; plugins/arch-compliance/hooks/hooks.json:20; pyproject.toml:19-20; .github/workflows/ci.yml:40; C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/metadata_facade_guard.py:66`
- reasoning: The hook runs as `python <plugin>/hooks/posttooluse_gate.py`, so sys.path[0] is the hooks dir, not the cwd. python/ is inserted at 0 when absent. The console script is acf.cli_check_diff:main. CI uses -m from the repo root, so the cwd is first. HM :66 is `from scripts.ci.arch_compliance.facade_sinks import`.

#### C33 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:29-61; C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/run_guards.py:107-130; C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/run_guards.py:317-321`
- reasoning: The parser offers only --mode, --base, --repo, --mandates and --json. At b652fab05, run_guards refuses an unknown site (:108-111), filters by `site not in entry.call_sites` (:116), refuses an empty selection (:126-130), and defaults --site to ci (:319).

#### C34 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:124-126; plugins/arch-compliance/python/acf/cli_check_diff.py:151-152; plugins/arch-compliance/hooks/posttooluse_gate.py:248-252; plugins/arch-compliance/python/acf/detectors/build_artifacts.py:27-34`
- reasoning: file_lines is filled only in the .py and .ts/.tsx branches. A staged dist/x.py hits the .py branch under key 'dist/x.py', and the build-artifact finding path (after lstrip('./')) equals that key. Ratchet findings on unchanged files get ''.

#### C35 — SURVIVED
- evidence: `config/architecture/mandates.yml:5-130; plugins/arch-compliance/profiles/python-service/mandates.yml:18; plugins/arch-compliance/tests/fixtures/mandates_valid.yml:1-32`
- reasoning: `git grep -n precommit -- '*.yml'` exited 1 with no output. The census counts of ast/guard rows declaring ci are 9, 7, 3 and 3. No shipped active ast/guard row lacks ci, so ci∪precommit selection equals today's status-only selection.

#### C36 — SURVIVED
- evidence: `pyproject.toml:7`
- reasoning: I executed it on the installed pydantic 2.13.3. A frozen model built normally from a str subclass, a bool, an int subclass, an IntEnum, 2.0 or '5' stores exact str and int in __dict__, so the exact-type checks pass genuine hits. model_construct(path=b'a', ...) stores bytes in __dict__, which _revalidate refuses. I verified this only on 2.13.3; pyproject allows pydantic>=2.0.

#### C37 — SURVIVED
- evidence: `C:/Program Files/KiCad/9.0/bin/Lib/pathlib.py:1261-1276; C:/Python313/Lib/pathlib/_abc.py:31-40; plugins/arch-compliance/hooks/posttooluse_gate.py:239`
- reasoning: On 3.11 and 3.13, is_file ignores ENOENT/ENOTDIR/EBADF/ELOOP and re-raises other OSErrors. 3.11 resolve raises RuntimeError on a loop, which resolve_under_root maps to None. The spec's load_mandates code wraps file_under_root in `except OSError`. The hook's propagation matches today's :239, which also ends uncaught (see the unanchored finding).

#### C38 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/host.py:24-25; docs/design/ADR_GATE_HOST_CONTRACT.md:295-301`
- reasoning: The fields are PosixStr only, and the contract's 'Not adopted' paragraph says what is quoted. The spec mentions runs_dir/ledger_path only in its §5.2 ADJACENT row, as unchanged.

#### C39 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:122-125; plugins/arch-compliance/tests/test_portable_guards.py:100-107; plugins/arch-compliance/profiles/python-service/mandates.yml:58-59; plugins/arch-compliance/python/acf/cli_check_diff.py:72`
- reasoning: The shipped values are a relative baseline and roots ['.'], and test_portable_guards creates tmp_path/'pkg' before roots=['pkg']. An absolute path inside the root resolves under base. A missing baseline already raises DetectorPackError today (load_baseline :78). cli_check_diff.py:72 catches DetectorPackError.

#### C40 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/genre_conditional_guard.py:32-40`
- reasoning: At b652fab05 there is an @dataclass (non-frozen) Finding whose __str__ calls self.line_text.strip(). I executed a replica: str(ValueError(Finding('a.md',3,None,'...'))) raises AttributeError, and so does the f-string _describe uses.

#### C41 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:388`
- reasoning: items = list(raw) sits inside the try before _revalidate runs. list() drives a generator to StopIteration or to its raise, so the generator's finally runs inside that call. No item is revalidated while the generator is suspended.

#### C42 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_diff_cli.py:84-108; plugins/arch-compliance/tests/test_diff_cli.py:185-193`
- reasoning: The other main() tests use the fixture (active rows) or an enforced _BARE_EXCEPT_ROW. test_missing_mandates fails at load. Only :102-108 has an all-unenforced registry. bad.py (:87) contains no hasattr. This holds when that test passes --call-site ci (see the unanchored finding on precommit).

#### C43 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:202-210; plugins/arch-compliance/hooks/posttooluse_gate.py:238-246; plugins/arch-compliance/python/acf/repo.py:40-44`
- reasoning: resolve_under_root computes (repo.resolve()/raw).resolve(), the same value as today's branch for both absolute and relative raw. is_relative_to plus is_file keeps exactly the in-repo regular files today's relative_to keyed relatively. The grep of test_hooks.py for outside|out_of_repo|absolute exited 1, and every test passes paths under repo.

#### C44 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:57-58; plugins/arch-compliance/skills/acf-mandate/SKILL.md:68`
- reasoning: :57 says partial gates and :58 advises partial or unenforced for a missing detector or prompt. The census found partial rows only as llm rows with valid prompt ids. The spec's Decision 3 and §4.8 record the consequence and the upgrade note.

#### C45 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:112-113; plugins/arch-compliance/python/acf/cli_check_diff.py:158; plugins/arch-compliance/python/acf/cli_check_diff.py:168; plugins/arch-compliance/python/acf/registry.py:33-41`
- reasoning: The claim's causal link covers only the five ids stamped by scan_python_file and scan_typescript_file. It fails for facade.forbid-sink, fsm.transition-guard, ops.no-build-artifacts and fail-loud.ratchet. Those scanners run only per active row whose detector equals the built-in id (cli_check_diff.py:112-113, :158, :168; hook :229-236, :284). Under the design such a row must carry that same id, which unique ids (registry.py:33-41) forbid alongside a host row. So a non-built-in row using one of those four ids receives no findings. The refusal is over-broad there; it is harmless, because no shipped row has such an id.

#### C46 — SURVIVED
- evidence: `C:/Python313/Lib/pathlib/_local.py:664-670; C:/Program Files/KiCad/9.0/bin/Lib/pathlib.py:981-1005`
- reasoning: Non-strict resolve follows symlinks, dangling ones included, without requiring existence. So an in-repo directory symlink to outside resolves outside and is refused, while a contained missing path is accepted. The spec applies _to_findings in both runners (§4.4 items 6-7).

#### C47 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:47; plugins/arch-compliance/python/acf/registry.py:58; plugins/arch-compliance/python/acf/cli_check_diff.py:98`
- reasoning: apply_registry and the gate filters drop only 'unenforced'. load_mandates skips every row that is not 'enforced'. A partial ast row with an unknown detector loads, and no scanner selects it.

#### C48 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:107; plugins/arch-compliance/hooks/posttooluse_gate.py:229-236`
- reasoning: The hook calls load_mandates(mandates_path) with no known_detectors. Its dispatch selects only built-in ids, so an unknown-detector row yields nothing.

#### C49 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80; plugins/arch-compliance/hooks/posttooluse_gate.py:119-123; plugins/arch-compliance/python/acf/enforcement.py:49-50`
- reasoning: The two closures are token-identical and read only file_lines, which is populated only in the code-suffix branches. apply_registry passes the looked-up line to token_exempted.

#### C50 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/adr/citations.py:74-76; plugins/arch-compliance/python/acf/adr/citations.py:163; C:/Program Files/KiCad/9.0/bin/Lib/pathlib.py:999-1004; C:/Program Files/KiCad/9.0/bin/Lib/posixpath.py:451-452`
- reasoning: The references are only :49, :74, :161 and :163, and no test imports the helpers, so the deletion is safe. The order is kept. But 'exactly two behaviours change' is false. _escapes_repo lets ValueError escape for a citation with an embedded NUL. On 3.11, resolve's non-strict p.stat() catches only OSError, on any platform. On POSIX, realpath's os.lstat (posixpath.py:451-452) catches only OSError. resolve_under_root catches ValueError and returns None, so such a citation now classifies 'unresolved' instead of raising. That is a third change, listed in neither §4.1 nor §4.9.

#### C51 — SURVIVED
- evidence: `config/architecture/mandates.yml:70; plugins/arch-compliance/profiles/python-service/mandates.yml:18; plugins/arch-compliance/tests/fixtures/mandates_valid.yml:18`
- reasoning: In the census every active shipped ast/guard row declares ci, and every one except no-shims.hasattr also declares hook. The ratchet rows are [ci] and unenforced. So ci or precommit selects today's rows, and HOOK_CALL_SITES drops only no-shims.hasattr (the same id in the repository and in python-service).

#### C52 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:60; plugins/arch-compliance/python/acf/cli_check_diff.py:21`
- reasoning: The known_detectors check applies only to ast/guard rows. The KNOWN_DETECTORS users I listed never use it for llm rows. The :21 import is used today only at :25.

#### C53 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_repo_paths.py:53-67; plugins/arch-compliance/tests/test_python_pack.py:10`
- reasoning: A constant with the same value emits identical findings. Grepping tests for reads of detector source finds only test_repo_paths' config/architecture spelling scan, which mandate-id constants do not trip, plus fixture-input reads.

#### C54 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80; plugins/arch-compliance/hooks/posttooluse_gate.py:119-123`
- reasoning: The make_line_lookup body in the spec equals both closures. File_lines content changes only by scan_host_guards' additions (the TS branch binds the same text).

#### C55 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/__init__.py:9-34; plugins/arch-compliance/tests/test_typescript_pack.py:6; plugins/arch-compliance/tests/test_typescript_pack.py:14`
- reasoning: The git grep printed exactly the spec's list, and every site is rewritten by §4.3 or §4.7.

#### C56 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/facade_sinks.py:24-25; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:46; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:88-90; plugins/arch-compliance/python/acf/detectors/build_artifacts.py:16; plugins/arch-compliance/python/acf/detectors/build_artifacts.py:23`
- reasoning: The scanner uses `allowlist_globs or []` and treats atomic_is_sink by truthiness only, so passing a raw value (None included) equals today's list(... or []) and bool(...). An absent key falls to the defaults None→[] and True. path_prefixes is handled by `or` defaulting and iteration, equivalent to list(prefixes) if prefixes else None.

#### C57 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:35-36; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:51-52`
- reasoning: git grep for ast.parse|except SyntaxError over python/ and hooks/ finds only the four scanners, and parse_python is the same try and except.

#### C58 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:45-62; plugins/arch-compliance/tests/test_portable_guards.py:107`
- reasoning: rglob yields search/<parts> lexically. With search resolved and is_relative_to(root.resolve()), relative_to(root) cannot raise. git grep shows scan_tree called only at fail_loud_ratchet.py:126 and in the test.

#### C59 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:31-34; plugins/arch-compliance/python/acf/detectors/python_pack.py:61; plugins/arch-compliance/python/acf/detectors/python_pack.py:77-82`
- reasoning: Both test node.type is None, or an ast.Name with id 'Exception'. The predicate's only caller is :61, and no test names it. python_pack imports only acf.engine and acf.finding, so the ratchet importing it creates no cycle.

### Unanchored findings

- **advisory**: §4.7 says every test_diff_cli main() call passes --call-site without saying which value. _BARE_EXCEPT_ROW declares [ci, hook] with no precommit and is not in the Appendix's 'add precommit' list, so a precommit value would make test_registry_severity_demotes_block_to_warn hit the new empty-selection refusal (exit 1, not the expected 0).
  - evidence: `plugins/arch-compliance/tests/test_diff_cli.py:77`
- **advisory**: A permission-denied stat in the hook's _collect_paths still ends in an uncaught OSError traceback under the design, because _collect_paths is called outside any try. 'Not a traceback' therefore holds only for load_mandates, load_host_detector, scan_host_guards and scan_ratchet.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:112`
- **advisory**: _revalidate's guarantee that normal validation yields exact str and int was verified only on pydantic 2.13.3, while pyproject.toml admits pydantic>=2.0. On an older 2.x that preserved str subclasses, a genuinely constructed HostHit could be refused.
  - evidence: `pyproject.toml:7`

### Looked for but did not find

- any dynamic import (importlib|import_module|spec_from_file_location|exec_module) in plugins/arch-compliance/python or hooks
- any yml row declaring precommit before the change
- any shipped or fixture row that the design's load rules refuse, beyond test_registry's not_a_real_detector (executed census)
- any shipped partial ast/guard row or partial llm row naming an unknown detector or prompt id
- any test in test_hooks.py passing a path outside the repository
- any other ast.parse-with-SyntaxError-skip site in plugins/arch-compliance/python
- any reference to _looks_absolute or _escapes_repo outside citations.py:49, :74, :161 and :163 in *.py
- any test that imports _is_bare_or_exception or reads detector source text in a way mandate-id constants would break
- any use of KNOWN_DETECTORS as a set (union or difference) that a Mapping would break

## compliance

### Claim verdicts

#### C60 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:29-30; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:594-623; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:409-416; plugins/arch-compliance/python/acf/registry.py:56-63; plugins/arch-compliance/hooks/posttooluse_gate.py:106-117`
- reasoning: The doctrine forbids bare and broad handlers 'that swallow errors ... unless explicitly exempted with a reason' (:29-30). In the §6.1 table each listed invalid state maps to a named component and a typed AcfError subclass. The load and call handlers re-raise everything except KeyboardInterrupt as UnknownDetectorError or DetectorPackError, so they swallow nothing. _describe's handler is the only one that swallows: it returns a constant string inside an error that is still raised, and its token carries a real reason (spec :412). Today the gaps the claim closes are real: registry.py:58 skips every non-enforced row, and the hook loads without known_detectors (:107) and catches only AcfInputError (:108) and DetectorPackError (:115). The design widens both except tuples. The llm prompt-id refusal reaches acf-check-diff and the skill snippet only, not the hook, and Decision 4 and §6.1 say so.

#### C61 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:296-312; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:205-224; plugins/arch-compliance/python/acf/cli_check_diff.py:168-182; plugins/arch-compliance/python/acf/enforcement.py:46-47`
- reasoning: Every shape today that loads but never fires has a refusal in _check_builtin: an unknown detector (LLM ids are no longer keys), an id other than the stamped mandate_id (apply_registry matches by id, enforcement.py:46), and a Tier-1 site outside the detector's contract (the ratchet is dispatched only at cli_check_diff.py:168-182). _row_shape refuses an active ast/guard row with no Tier-1 site. I checked whether an fsm or facade row with missing params could load and stay silent. It cannot: the scanners raise DetectorPackError on an empty state_field, validator_name or target_literal_re (fsm_guard.py:29-34, facade_sinks.py:32-37), so the failure is loud, though at scan time rather than at load.

#### C62 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:120-124; plugins/arch-compliance/python/acf/repo.py:23-26; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:584; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:453`
- reasoning: The section's text limits the rule to the ADR gate's host values in config/architecture/adr.yml (:120-123) and records three defaults outside it (:124-133), among them the ratchet baseline default (repo.py:23-26), which the design keeps at its one site. The spec says the section does not require its choices and that it follows the practice by choice. The design does what it says: --call-site is required with choices (spec :453), apply_registry's call_sites keyword has no default, and an active host row without repo_root raises AcfInputError. The new *_args functions keep the existing '' fallback for required params, but the scanners refuse '' loudly, so no default stands in for a declared value.

#### C63 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:48-49; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:369; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:378-379`
- reasoning: The doctrine forbids probing optional attributes with hasattr 'to paper over missing interfaces' (:48-49). The design does getattr(mod, attr, None) inside the wrapped region (spec :369) and then raises UnknownDetectorError when the result is not callable (:378-379). It is not a probe that degrades quietly, and no host-detector failure path ends in a fallback value.

#### C64 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/engine.py:17-24; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:129-130; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:340; config/architecture/ARCHITECTURE.md:57-64`
- reasoning: contains_backslash exists in acf.engine (engine.py:17-24). validate_posix_rel_path calls it and raises on a backslash (spec :129-130), and HostHit.path goes through it as an AfterValidator (:340). That matches the doctrine's stricter stance of refusing rather than normalizing (:62-64). Error messages format paths with .as_posix() ((repo_root / rel_path).as_posix(), _ACTIVE_ROOT.as_posix()) or as the already-POSIX reference string.

#### C65 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/exceptions.py:1; plugins/arch-compliance/python/acf/exceptions.py:13; plugins/arch-compliance/python/acf/exceptions.py:29; config/architecture/ARCHITECTURE.md:101-102`
- reasoning: AcfInputError (:5), UnknownDetectorError (:13) and DetectorPackError (:29) each subclass AcfError alone, and AcfError (:1) subclasses Exception. The design's code blocks raise only those three classes and define no new exception class, which satisfies 'Every ACF exception subclasses AcfError and nothing else' (:101-102).

#### C66 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:15; plugins/arch-compliance/tests/test_repo_paths.py:53-67; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:495; plugins/arch-compliance/skills/acf-mandate/SKILL.md:93-95`
- reasoning: The rule is that acf.repo is the one declaration of host paths, and test_repo_paths scans python/ and hooks/ for any config.{0,6}architecture spelling. None of the design's code blocks for engine, registry, detectors/__init__ or host.py spells that directory. The acf-mandate snippet already imports MANDATES_REL from acf.repo (SKILL.md:93). The §4.8 rewrite builds the path as resolve_repo(None) / MANDATES_REL (spec :495), so it still consumes the acf.repo constant.

#### C67 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:137-138; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:181-183; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:412-415; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:453`
- reasoning: The doctrine requires that skill prose and runtime messages 'name no host repository, path or section' (:137-138). The runtime messages in §4.2-§4.4 and §4.6 are generic: the host-reference syntax error, 'host exception (message unavailable)', and the 'selects no active' refusal. The skill-prose edits in §4.8 describe call sites, the .acf/enabled opt-in and upgrade steps without naming the origin host. The 'posttooluse' spelling in CallSite is already in the parent spec's vocabulary and names no host.

#### C68 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:625-651; plugins/arch-compliance/python/acf/cli_check_diff.py:21; plugins/arch-compliance/python/acf/detectors/__init__.py:30-35`
- reasoning: §6.2 is a per-item table that pairs each new export with a non-test caller in the package or a hook, for example file_under_root with load_mandates, load_host_detector, scan_host_guards, scan_ratchet and _collect_paths. LLM_PROMPT_IDS is defined in judge.py:29, and its one runtime consumer today is cli_check_diff.py:21/:25. It keeps that consumer through load_mandates(..., llm_prompt_ids=...). The five deleted sets are the names exported at detectors/__init__.py:30-35 plus python_pack.py:16 and typescript_bridge.py:14, and their consumers switch to KNOWN_DETECTORS, so no export is left dead.

#### C69 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:161-165; plugins/arch-compliance/tests/test_diff_cli.py:48; plugins/arch-compliance/tests/test_hooks.py:199-218; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:660-681`
- reasoning: I checked the spec's quantified claims against the tree. Each carries a recipe in §1, §4.8, §4.9 or the Appendix, or is a per-item list. The list of ten main([...]) calls in §4.7 matches the test_diff_cli.py hits exactly (:48, :61, :98, :107, :124, :153, :154, :173, :178, :191). The 'no test exercises the dropped case' recipe against test_hooks.py prints nothing, as claimed. The only fixture YAML is mandates_valid.yml (Glob), which the Appendix recipes cover, and the repository-level tests/ declares no call_sites.

#### C70 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:173-175; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:422; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:459`
- reasoning: The rule covers subprocess text calls and file reads of prose in runtime code (:173-175). The new reads, candidate.read_text in scan_host_guards (spec :422) and the TypeScript branch's abs_path.read_text (:459), both declare encoding='utf-8'. errors='replace' does not touch the declared encoding. No new runtime subprocess appears; the subprocess in the hook test sits in tests, which the rule's scope excludes.

#### C71 — SURVIVED
- evidence: `pyproject.toml:3; plugins/arch-compliance/.claude-plugin/plugin.json:3; config/architecture/ARCHITECTURE.md:186-187; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:507`
- reasoning: Both files read 0.2.2 today. The doctrine says 'A change to a skill's prose bumps the plugin version in plugin.json and pyproject.toml' (:186-187). §4.8 edits the acf-mandate and acf-setup skills and bumps both files to 0.2.3 (spec :507).

#### C72 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80; plugins/arch-compliance/hooks/posttooluse_gate.py:119-123; plugins/arch-compliance/python/acf/detectors/python_pack.py:77-82; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:31-34; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:24-25`
- reasoning: The §4.9 rows match the tree. The two _line_lookup closures are token-identical, the ratchet's bare-or-Exception test matches python_pack's predicate, and the params extraction is duplicated at cli_check_diff.py:128-166 and posttooluse_gate.py:255-294. Today the gates add a second default for optional params (bool(params.get('atomic_is_sink', True))). With *_args passing a key only when it is present, the scanner signature defaults (facade_sinks.py:24-25, build_artifacts.py:16) become the one default. The spec claims nothing beyond its list.

#### C73 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:213-215; plugins/arch-compliance/python/acf/cli_check_diff.py:118-119; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:96`
- reasoning: The rule reads 'remove legacy dependencies or non-contractual patterns in code paths you are changing. Do not expand scope to unrelated modules' (:213-215). The deletions are confined to the paths the design edits. Keeping the two dispatch loops is justified as two call sites of one procedure (spec :96). The _scan_changed join at cli_check_diff.py:118-119 takes git-supplied relative paths and only checks is_file, so recording it as ADJACENT is accurate.

#### C74 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:147-148; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:75-89`
- reasoning: The section covers LedgerRow and LedgerAmendment fields (:147-148). The in-scope file table (spec :75-89) does not include plugins/arch-compliance/python/acf/adr/ledger.py or any ledger model. The only acf.adr change is citations.py consuming the engine path helpers.

#### C75 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:47-51; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:102; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:123; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:125; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:296-312`
- reasoning: Principle 1 (typed errors, no swallow) is met per C60. Principle 2 (one registry façade, one finding schema): host hits are rebuilt into the single Finding type, and rows load only through load_mandates. Principle 3 (POSIX) is met per C64. Principle 4 says detectors and 'call sites must agree or tests fail', and the design makes call_sites route rows and refuses contract disagreement at load (spec :296-312). Principle 5 is untouched. :102 names 'guard module', and :123 and :125 each call for 'Extension points for project-specific detectors', which the host ast/guard callables provide.

#### C76 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:417; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:422; plugins/arch-compliance/python/acf/enforcement.py:49-50; plugins/arch-compliance/hooks/posttooluse_gate.py:113-117`
- reasoning: _to_findings refuses an escaping or unresolvable hit with DetectorPackError (spec :417). apply_registry drops a finding only when token_exempted finds the token on the looked-up line (enforcement.py:49-50). A [] entry or a replacement character therefore can only keep a finding, never hide one. The OSError raised as DetectorPackError lands inside each gate's scan try: the hook's except at :115 already catches DetectorPackError and the design widens it. make_line_lookup only indexes the mapping it is given.

#### C77 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:72-73; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:46; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:56-57; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:122-124; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:500`
- reasoning: The section reads 'Optional whole-tree freeze ... Enable the mandate and commit a ... baseline' (:72-73). The design keeps the counting and baseline comparison (fail_loud_ratchet.py:101-144). The joins at :46 and :122-124 do no containment and :56-57 skips a missing root silently; the design replaces those with resolve_under_root, an is_dir check and DetectorPackError. That turns a silent zero count into a loud refusal and agrees with Fail loud. The KNOWN_DETECTORS contract limits the ratchet to DIFF_CALL_SITES. §4.8 adds the routing and containment constraints to :72-73 (spec :500). The symlinked-root key change is disclosed in §4.9.

### Unanchored findings

- **advisory**: The profile drift test is not in §4.7 and keeps calling load_mandates with known_detectors only. The bundled profile registries that /acf-setup copies into hosts are therefore never checked against LLM_PROMPT_IDS, although Decision 4 makes that rule enforced for host registries through acf-check-diff.
  - evidence: `plugins/arch-compliance/tests/test_profile_drift.py:24`
- **advisory**: Two of the three broad handlers carry the literal placeholder '# fail-loud.bare-except-ok: <reason>'. Fail loud requires an explicit reason, and token_exempted would accept '<reason>' as a non-empty reason, so the spec should state each reason as it does for _describe.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:370`
- **advisory**: The contract-against-dispatch test's 'fixture tree that triggers every built-in detector' must be generated under tmp_path at run time. If committed, it would be flagged by this repository's own CI diff gate. Adding exemption tokens to it, as the doctrine's existing fixtures do, would make apply_registry drop the very findings the test asserts. The spec does not say where the tree lives.
  - evidence: `config/architecture/ARCHITECTURE.md:32-36`
- **advisory**: The design edits scan_typescript_file (its Finding construction), and the same function holds a declared Declared-text-decoding breach: a subprocess.run(text=True) call with no encoding. The spec does not say whether Scoped refactor leaves that debt to self-hosting spec §9 follow-up 1.
  - evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:49-56`
- **advisory**: The full-validation call load_mandates(..., known_detectors=KNOWN_DETECTORS, llm_prompt_ids=LLM_PROMPT_IDS, repo_root=repo) is assembled by hand in acf-check-diff, the acf-mandate snippet and tests/test_self_host.py rather than taken from one package entry point. A future validation keyword would have to be added at each site, which is the doctrine's high-frequency miss of a check re-assembled in a skill or test.
  - evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:95`

### Looked for but did not find

- ## High-frequency misses (ARCHITECTURE.md:217-228): checked each listed miss first. No unbacked completeness claim found (C69). No default re-enters for a declared value, because the '' fallbacks for required params are refused by fsm_guard.py:29-34 and facade_sinks.py:32-37. No host name in runtime messages. No stdlib exception mixin. No new subprocess text call. Skill and test checks consume load_mandates and KNOWN_DETECTORS (one assembly-duplication advisory filed).
- ## Build artifacts (ARCHITECTURE.md:66-68): the design changes only how the no_build_artifacts guard is called (build_artifact_args, call-site routing, out-of-repo hook paths dropped); for in-repo paths its prefixes and its finding behaviour are unchanged (build_artifacts.py:13-43), and the rule (do not stage generated trees) is not otherwise touched.
- ## Soft fail-loud smells and ## React boundaries (ARCHITECTURE.md:87-97): the design adds prompt-id validation for active llm rows. This repository's llm_fail_loud and llm_react_boundaries rows (mandates.yml:41-50, :132-142) name valid prompt ids, and the Tier-2 judge is unchanged.
- ## Post-merge (ARCHITECTURE.md:230-239): no housekeeping declaration or CI workflow name changes; ci.yml:40 only gains --call-site ci.
- ## One owner for host paths: test_repo_paths.py:53-67 would flag any new config/architecture spelling in python/ or hooks/, and none of the proposed code adds one.
- ## Release discipline, installed-skill check: the design does not change the three skill trees that check_installed_skills.py covers (the two gate skills and post-merge-housekeeping), so only the version bump applies (C71).

### Unstated mandates

- ## Façade sinks (ARCHITECTURE.md:75-79) and ## FSM transitions (ARCHITECTURE.md:81-85): these are the doctrine's enablement instructions for the two config-driven rows ('Set params.target_literal_re / allowlist_globs, then flip status to enforced'; 'Set params.state_field / validator_name, then enforce'). The design rewrites how those params reach the scanners (facade_sink_args, fsm_guard_args). It also changes what enabling such a row now requires: the row id must equal the detector's mandate id, and at least one Tier-1 site where a gate runs it. §4.8 adds the matching constraints to the ## Fail-loud ratchet instruction but is silent on these two sections.

## sweeper

### Claim verdicts

#### C78 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99, plugins/arch-compliance/hooks/posttooluse_gate.py:229-236, plugins/arch-compliance/hooks/posttooluse_gate.py:284-286, plugins/arch-compliance/python/acf/enforcement.py:47`
- reasoning: I grepped for status != / == 'unenforced', _active_mandates and .status reads across python/ and hooks/. Today the Tier-1 active-row filters are exactly the six sites the spec replaces: cli_check_diff.py:94-99 (plus its four callers), posttooluse_gate.py:231, :235, :285 and enforcement.py:47. Three other sites read status, and none of them is a Tier-1 gate filter: registry.py:58 (load-time, replaced by is_active), judge.py:218 (Tier-2) and inject_constraints.py:158 (display only). After the change, _row_shape and _check_builtin each intersect call_sites with TIER1_CALL_SITES themselves rather than calling runs_at. They are load-time contract checks, not gate filters, so the claim holds.

#### C79 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/citations.py:76, plugins/arch-compliance/hooks/posttooluse_gate.py:204, plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:46, plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:124, tests/test_self_host.py:40`
- reasoning: Searched by behaviour for relative_to(, is_relative_to, is_absolute(, os.path.commonpath/relpath/isabs/realpath, drive-letter regexes and root joins across the plugin, tests/ and scripts/. The only hand-rolled 'is this string under the root' decisions today are citations.py:74-76, the hook's join at :204 and relative_to/except at :242-245, and the ratchet's joins at :46, :122-124 with its except at :59-62. The spec routes each of them through resolve_under_root. The remaining joins are either plugin-owned constants (repo / MANDATES_REL and similar), citations.py:168 (it runs after the escape test), or the operator's --mandates argument. The ADR host fields runs_dir and ledger_path stay uncontained by approved decision. ast.parse with an except SyntaxError appears only in the four scanners (python_pack.py:35, facade_sinks.py:51, fsm_guard.py:37, fail_loud_ratchet.py:24). One caveat, filed under C90: the diff gate's git-listed paths are never contained.

#### C80 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:84-92, plugins/arch-compliance/python/acf/cli_check_diff.py:154`
- reasoning: The stated reason, that the inputs share no format, is false at the record level. Each Node item is a JSON object carrying path, line and message, a superset of HostHit's three fields. After v8 both sites (1) validate an untrusted detector-emitted hit and refuse a malformed one as DetectorPackError (typescript_bridge.py:94-95 vs _call_host/_revalidate), and (2) stamp mandate_id from a plugin-side source rather than the detector's echo (TS_MANDATE_IDS vs the row). The spec's §5.2 says they share only the Finding constructor; they share the hit-validation responsibility too. The two validators diverge. The bridge coerces line with lax int() (so '5' or True pass), checks neither line >= 1 nor that message is non-empty, and its path is overwritten by the gate (cli_check_diff.py:154). HostHit refuses all of these. The shared responsibility is 'validate a detector hit's line and message'; the bridge's absolute path and Node-supplied severity are its private parts.

#### C81 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:241-245, plugins/arch-compliance/python/acf/judge.py:247-250`
- reasoning: Opened _to_finding, which is at judge.py:238-255; the claim's spec_citation 236-253 is off by two. It demotes severity from the row ceiling by verdict and confidence (:241-245), admits path='<diff>' and line=0 (:249-250), and takes mandate_id from the model result (:247). No apply_registry call exists on the Tier-2 path: grep finds apply_registry only in the two Tier-1 gates and in test_enforcement. The host runner takes severity and id from the row and needs line >= 1. The only shared step is the Finding constructor, so ADJACENT holds.

#### C82 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:25-26, plugins/arch-compliance/hooks/inject_constraints.py:28-29, tests/test_check_installed_skills.py:15-18`
- reasoning: Grepped importlib, import_module, spec_from_file_location, exec_module, runpy, __import__, exec( and sys.path.insert/append over plugins/, tests/ and scripts/. Under plugins/ the only hits are the two hooks' insertion of the plugin's own python/ directory (posttooluse_gate.py:26, inject_constraints.py:29) and a test's importlib.import_module of skill-prose module names (test_adr_skill_prose.py:57). The only file-path module loader in the tree is the test tests/test_check_installed_skills.py:15-18, which loads a fixed script path and registers nothing in sys.modules. Nothing loads code from a registry-supplied path. The origin host's dotted import_module runner (hm:scripts/ci/run_guards.py:38, :165) is outside the plugin.

#### C83 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80, plugins/arch-compliance/hooks/posttooluse_gate.py:119-123, plugins/arch-compliance/python/acf/detectors/fsm_guard.py:56`
- reasoning: Grepped line_lookup, LineLookup, apply_registry and the 'lines[line - 1]' bounded fetch. Exactly two non-test LineLookup closures are passed to apply_registry, the ones named; cli_check_llm, the judge and the skills have none. test_enforcement.py defines stub lookups (_no_lines and inline functions), which are test fixtures. fsm_guard.py:56 repeats the same bounded 1-based fetch for its message snippet, but it is not a LineLookup and never reaches apply_registry. That is ADJACENT, recorded under relationships.

#### C84 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:95, plugins/arch-compliance/tests/test_profile_drift.py:24, plugins/arch-compliance/skills/architecture-review/SKILL.md:62`
- reasoning: Searched the skills, tests and hooks for code that checks detector ids or call_sites. The acf-mandate snippet (:95), test_profile_drift.py:24 and tests/test_self_host.py:23 all delegate to load_mandates(known_detectors=...); none compares ids itself. architecture-review SKILL.md:62 loads without known_detectors and checks nothing. acf-setup's checks are by-eye anchor and id-uniqueness steps (:110, :137), not detector checks. The README detector table is prose that the new test pins, not a validator.

#### C85 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:168-182, plugins/arch-compliance/hooks/posttooluse_gate.py:284-295, plugins/arch-compliance/python/acf/enforcement.py:46`
- reasoning: Today the ratchet is dispatched only by the diff gate (cli_check_diff.py:168-182), and the hook's dispatch ends at the build-artifact loop (posttooluse_gate.py:284-295), which matches the §4.3 table. Findings route by id alone (enforcement.py:46), so the reverse drift (a gate dispatching a detector the table excludes) needs a row that declares that gate's site. _check_builtin refuses such a row at load, and apply_registry's runs_at drops anything else. The forward drift shows up as a missing mandate_id in the test's exact-set assertion. Both of the claim's directions hold.

#### C86 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:204, plugins/arch-compliance/hooks/posttooluse_gate.py:242-245, plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:59-62, plugins/arch-compliance/python/acf/repo.py:41-44`
- reasoning: Each named site decides containment by hand. Once each root is contained, rglob from a resolved in-root search yields paths that are lexically under root, so relative_to(root) at fail_loud_ratchet.py:60 cannot fail. In the hook, file_under_root returns a path under root.resolve(), and resolve_repo returns a resolved repo (repo.py:41-44), so relative_to(repo) cannot fail either. §4.1, §4.6 (_collect_paths bullet), §4.9 (hook row and last row) and §5.2 (second row) all say the except branches go and only the relative_to(...).as_posix() conversion stays.

#### C87 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:65, docs/design/HOST_DETECTOR_EXTENSION_POINT.md:407, docs/design/HOST_DETECTOR_EXTENSION_POINT.md:476`
- reasoning: Read every passage of the spec that says where host code runs. Decision 7 (:65) states the guarantee and the non-confinement. §4.4 item 4 (:407) claims only that _to_findings invokes no host-defined method through the rebuilt hits, which is not a claim that host code runs nowhere else. A host module that monkeypatches plugin objects at import, or a host thread, falls under Decision 7's 'does not confine'. Decision 4 and the SubagentStart bullet claim only that load_mandates imports no host module, and registry.py:48-64 has no import machinery. fresh_host_loader (:476) is the only reset §4.7 defines. The hook cases run in subprocesses, and the in-process host cases in test_diff_cli use the fixture.

#### C88 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:85, plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23, plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15`
- reasoning: Grepped 'fail-loud.empty-catch' and 'no-shims.explicit-any' across .py, .ts and .json. Outside tests, the only Python site is the bridge, which today copies item['mandate_id'] (:85). The other hits are the Node rule literals, scan.ts:94-96 (Node self-test) and Python tests (test_baseline, test_enforcement, test_typescript_pack). The Node detector keys empty_catch and explicit_any (emptyCatch.ts:28, explicitAny.ts:22) match the proposed TS_MANDATE_IDS keys.

#### C89 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:52, plugins/arch-compliance/python/acf/cli_check_diff.py:82, plugins/arch-compliance/hooks/posttooluse_gate.py:125-126`
- reasoning: On both Tier-1 paths every reported finding passes through apply_registry, which overwrites severity from the row (:52), before the BLOCK test (cli_check_diff.py:89, posttooluse_gate.py:126). The severities that scanners, the Node pack and the host runner fill in are all overwritten. The judge's row-capped severity (judge.py:241) is Tier-2 and never reaches apply_registry.

#### C90 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:118-119, plugins/arch-compliance/python/acf/diff.py:56`
- reasoning: A git-listed path is repo-relative as a string. But file_under_root's job, as §4.4 item 5 and §5.2 define it, includes resolution through in-repo symlinks, and that job does apply here: git diff --name-only --diff-filter=ACMR (diff.py:56) lists a changed tracked symlink, and is_file() at cli_check_diff.py:119 follows it, so the diff gate reads and scans a target outside the repository under the link's path. After this design the hook, via file_under_root, skips the same file and keys an in-repo link by its target path, so the two gates map one changed path to different files. Worse, scan_host_guards receives the gate's `changed` list unfiltered; a guard that flags such a path is then refused by _to_findings' resolve_under_root as DetectorPackError, failing the gate on a hit the gate itself supplied. The responsibility 'map a changed path to the in-repo file a gate scans' has two owners that disagree.

#### C91 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/loader.py:24-28, plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:78-81, plugins/arch-compliance/hooks/inject_constraints.py:165`
- reasoning: require_file takes a built Path and always raises AcfInputError. Its callers are loader.py:58, inject_constraints.py:165 and adr/host.py:30, all operator or plugin-declared files. The pre-existing ratchet refusal (fail_loud_ratchet.py:78-81) already needs DetectorPackError, which confirms that the phase-specific error type is a real private responsibility. Containment of a registry string has no counterpart in require_file.

#### C92 — SURVIVED
- evidence: `docs/design/ADR_GATE_HOST_CONTRACT.md:292-294, plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:77-98, plugins/arch-compliance/python/acf/cli_check_diff.py:125`
- reasoning: The approved doc records load_baseline (fail_loud_ratchet.py:77-98) as 'a pre-existing second loader outside this phase'; the design touches only its path resolution. The gates' strict utf-8 reads (cli_check_diff.py:125, :152; posttooluse_gate.py:251) feed parsers, while the guard-file read feeds only token_exempted. ARCHITECTURE.md:171-182 requires a declared encoding, which the errors='replace' read still has.

#### C93 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:355, docs/design/HOST_DETECTOR_EXTENSION_POINT.md:476, tests/test_check_installed_skills.py:15-18`
- reasoning: The design keeps no cache of loaded modules other than sys.modules under the hash name: _ACTIVE_ROOT is root state, not a per-path cache. The tree's only existing file loader (the test at tests/test_check_installed_skills.py:15-18) keeps none either. The fixture resets _ACTIVE_ROOT, sys.path and the added _acf_host_ or under-root modules. Advisory note: the name is a function of the rel_path string, not of the file, so on a case-insensitive filesystem or through a symlinked directory, two spellings of one file get two records and the module executes twice.

#### C94 — SURVIVED
- evidence: `config/architecture/mandates.yml:70, plugins/arch-compliance/profiles/python-service/mandates.yml:53, hm:config/architecture/mandates.yml:11`
- reasoning: Grepped every call_sites value in .yml and .py in this repository and in HistoricMansions' registry. Here the values are ci, hook and audit; HistoricMansions uses precommit, posttooluse, ci and audit. No multi-line list forms exist. test_template.py:80 is [] on an llm row, which _row_shape skips. Every active ast/guard row here declares ci, and the only [ci]-only active row is no-shims.hasattr, a TIER1 detector. The ratchet rows are unenforced. Nothing in either repository routes audit to a Tier-1 gate.

#### C95 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_diff_cli.py:102-108, plugins/arch-compliance/tests/test_registry.py:30, plugins/arch-compliance/tests/test_typescript_pack.py:6`
- reasoning: Read test_diff_cli, test_hooks, test_registry, test_enforcement, test_typescript_pack, test_portable_guards, test_profile_drift, test_acf_mandate_skill, test_repo_paths, test_adr_import_graph, test_packaging, test_adr_citations and tests/test_self_host. Counted ten main([...]) calls (:48, :61, :98, :107, :124, :153, :154, :173, :178, :191) and ten apply_registry calls. Grepped the tests for every symbol the design deletes or renames (_DETECTOR_IDS, _active_mandates, _looks_absolute, _escapes_repo, _is_bare_or_exception, _line_lookup); hits only at the listed lines. The other tests survive the change: fixture and profile rows satisfy _check_builtin, no test passes an out-of-repo path to the hook, and test_hooks:220-234 is unaffected because the hook has no empty-selection refusal.

#### C96 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:228, docs/guides/SUPERPOWERS_COMPLEMENT.md:70, README.md:57`
- reasoning: Grepped acf-check-diff, acf.cli_check_diff and also bare 'check-diff' (a behaviour sweep the spec's by-name recipe would miss). The extra hits are docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:71, :152 and :193, descriptive mentions in the parent design that spell no flags. There is no .pre-commit-config, Makefile or second workflow, and the only workflow invocation is ci.yml:40. The acf-setup, README and guide sites match the §4.8 list.

#### C97 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:72-73, config/architecture/ARCHITECTURE.md:226-228, plugins/arch-compliance/skills/acf-mandate/SKILL.md:58, docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:161`
- reasoning: Opened each cited line; each states the pre-revision contract. Then searched ARCHITECTURE.md, the acf-mandate and acf-setup skills, README, the guide and the parent design for partial-row advice, ratchet enablement, the home of KNOWN_DETECTORS and PostToolUse scope. The other stale hits (acf-mandate :68, :138; parent design :104, :184; ARCHITECTURE.md:9-11) are already in §4.8 rows.

### Unanchored findings

- **advisory**: The diff gate maps git-listed paths to files by a lexical join that follows symlinks out of the repository, while the hook (via file_under_root) and _to_findings contain them; the two gates then scan different files for one changed path, and a host guard that flags a changed out-of-repo symlink it was handed fails the diff gate with DetectorPackError.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:118-119`
- **advisory**: The TypeScript bridge's per-item validation (lax int(line), no line >= 1 or non-empty-message check) is a weaker second validator of the same detector-hit fields HostHit validates strictly, so the two Tier-1 hit sources disagree on what a valid hit is.
  - evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:88-89`

### Looked for but did not find

- dynamic loading of code from a registry path: importlib|import_module|spec_from_file_location|exec_module|runpy|__import__|exec( over plugins/, tests/, scripts/ (only the test-only fixed-path loader tests/test_check_installed_skills.py:15)
- another containment decision: relative_to(|is_relative_to|is_absolute(|os.path.commonpath|relpath|isabs|realpath and (repo|root|ROOT) / joins over the plugin
- a third LineLookup passed to apply_registry: line_lookup|LineLookup|lines[line - 1]|apply_registry
- non-test Python spellings of the TS mandate ids: fail-loud.empty-catch|no-shims.explicit-any over *.py,*.ts,*.json
- another parse-or-skip: ast.parse(|except SyntaxError over *.py
- independent detector-id or call-site validators in skills and tests: load_mandates|known_detectors|KNOWN_DETECTORS|detector in skills and tests
- call-site values outside CallSite: call_sites over *.yml and *.py here and in hm:config/architecture/mandates.yml, including block-list forms
- unlisted gate invocations: acf-check-diff|acf.cli_check_diff|bare check-diff, .pre-commit-config, Makefile, other workflows
- a design previously rejected on the record and now re-proposed: PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:418-424 (KNOWN_DETECTORS home) and ADR_GATE_HOST_CONTRACT.md:287-303; none found, as the spec updates both

### Relationships

- PARTIAL_OVERLAP: `file_under_root in the hook's _collect_paths` — responsibility `map a changed or edited path string to the in-repo file a Tier-1 gate scans` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:118-119`
  - resolution: Both gates resolve a changed path through file_under_root (or one helper such as resolve_changed_file(repo, rel) built on it). The diff gate's lexical repo / path + is_file() collapses into it, and scan_host_guards receives only the contained list, as the hook's rel_paths already are.
- PARTIAL_OVERLAP: `HostHit validation plus _to_findings` — responsibility `validate a detector-emitted (path, line, message) hit and refuse a malformed one as DetectorPackError` — existing `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:79-95`
  - resolution: One hit-field validator (strict int line >= 1, non-empty str message) that both the bridge's item loop and HostHit apply. The bridge keeps its private parts (absolute path from Node, overwritten by the gate; Node severity; TS_MANDATE_IDS stamping), and the host runner keeps row-derived id and severity.
- ADJACENT: `HostHit to Finding construction` — responsibility `build a Finding whose severity derives from the mandate row` — existing `plugins/arch-compliance/python/acf/judge.py:238-255`
  - resolution: none
  - non-merge: The judge demotes from the row ceiling by verdict and confidence, admits path '<diff>' and line 0, and takes mandate_id from the model. Tier-2 findings never pass through apply_registry. The host runner's severity is a required-field fill that apply_registry overwrites.
- ADJACENT: `make_line_lookup` — responsibility `fetch a 1-based source line with bounds, empty string otherwise` — existing `plugins/arch-compliance/python/acf/detectors/fsm_guard.py:56`
  - resolution: none
  - non-merge: fsm_guard reads a line of the text it already holds to build a message snippet; make_line_lookup serves exemption lookup over the gate's file map. Same bounds rule, different inputs and consumers.
- ADJACENT: `load_host_detector sys.path append` — responsibility `put a directory on sys.path once per process` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:25-26`
  - resolution: none
  - non-merge: The hooks prepend the plugin's own python/ at start-up so they can import acf. The loader appends a host root at dispatch time, after every existing entry. Position and purpose differ.
- ADJACENT: `MandateRegistry.active(call_sites, detection='guard') in scan_host_guards` — responsibility `select the guard rows that run at a declared call site, refusing a site that selects nothing` — existing `hm:scripts/ci/run_guards.py:94-131`
  - resolution: none
  - non-merge: The origin host's runner is outside this repository and is left to the cutover spec (§3 non-goals). The plugin's refusal is in acf-check-diff (§4.6), not in the runner.
- ADJACENT: `validate_posix_rel_path` — responsibility `refuse a backslash in a path string with a ValueError` — existing `plugins/arch-compliance/python/acf/adr/contract.py:89-90`
  - resolution: none
  - non-merge: Both already consume the one primitive, acf.engine.contains_backslash. PosixStr lives in acf.adr (pydantic), which the hook graph must not import, and it accepts absolute or '..' paths by approved decision (ADR_GATE_HOST_CONTRACT.md:295-301).
- ADJACENT: `file_under_root callers' not-found refusals` — responsibility `refuse an absent input file with a typed error` — existing `plugins/arch-compliance/python/acf/loader.py:24-28`
  - resolution: none
  - non-merge: require_file has no containment step and always raises AcfInputError. These callers contain a registry string first and need their phase's error, as the pre-existing ratchet refusal at fail_loud_ratchet.py:78-81 already does.
- SUBSUMED: `looks_absolute, resolve_under_root` — responsibility `decide whether a path string lies inside the repository` — existing `plugins/arch-compliance/python/acf/adr/citations.py:49-51`
  - resolution: citations' private _looks_absolute and _escapes_repo (:49-51, :74-76) are deleted and both call sites consume acf.engine, as the spec states.

### Two-owner counts

- map a changed/edited path string to the file a Tier-1 gate scans: 2
- validate a detector-emitted hit (path, line, message) and refuse it as DetectorPackError: 2
- set Finding.severity from the mandate row: 3
- intersect a row's call_sites with a site set: 3
- fetch a bounded 1-based line or empty string: 2
- refuse an absent input file with a typed error: 2
- select guard rows per call site (plugin and origin host until cutover): 2

### Document conflicts

- `docs/design/ADR_GATE_HOST_CONTRACT.md:300` (restates): a refusal would be a second implementation of the repo-relative test that citations.py:49 (_looks_absolute) and :74 (_escapes_repo) already own
- `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:418` (contradicts): KNOWN_DETECTORS stays where the diff CLI defines it (cli_check_diff.py:25)
- `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:161` (contradicts): PostToolUse | Diff-scoped Tier 1 on edited .py / .ts / .tsx (and configured config paths)
- `plugins/arch-compliance/skills/acf-mandate/SKILL.md:58` (contradicts): Prefer partial or unenforced when the detector/prompt does not exist yet.
- `config/architecture/ARCHITECTURE.md:9` (contradicts): The CI diff gate and the PostToolUse hook run the registry's detectors on changed .py, .ts and .tsx files

## hardening

### Claim verdicts

#### C98 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:107 plugins/arch-compliance/hooks/inject_constraints.py:104 plugins/arch-compliance/python/acf/cli_check_llm.py:54 plugins/arch-compliance/python/acf/cli_check_diff.py:72`
- reasoning: Under the design the hook passes known_detectors, so importing at load would import every host module, [ci]-only guards included, on each edit. The deferral is justified on that ground alone. A missing file still fails at load (spec load_mandates body), and dispatch errors are UnknownDetectorError, which cli_check_diff.py:72 already catches and the hook's widened scan except catches. Caveat: inject_constraints.py:104 and cli_check_llm.py:54 call load_mandates(path) without known_detectors. An import placed in the known_detectors branch would therefore not run host code there, so the SubagentStart and acf-check-llm part of the justification is weaker than the claim says (filed as an advisory finding).

#### C99 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:46 plugins/arch-compliance/python/acf/detectors/python_pack.py:67 plugins/arch-compliance/python/acf/registry.py:33-41 plugins/arch-compliance/hooks/posttooluse_gate.py:251-282`
- reasoning: Traced each shape. (1) A built-in row's id is forced to equal the stamped mandate_id (python_pack.py:67, :97; TS stamped from TS_MANDATE_IDS), so findings land on it via by_id at enforcement.py:46. (2) Unserved Tier-1 sites are refused by _check_builtin, and the hook runs scan_python_file and scan_typescript_file on every code file regardless of row (posttooluse_gate.py:251-282). (3) Host rows get mandate.id from the runner, and ids are unique (registry.py:33-41). (4) A row with no Tier-1 site is refused by _row_shape. Mismatches the contracts do not check: detection kind (guard vs ast) for built-ins and languages for built-ins. Neither stops the row from running, because dispatch is by detector id and file suffix. I found no active ast/guard row shape that loads yet runs at neither gate.

#### C100 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:63 plugins/arch-compliance/hooks/posttooluse_gate.py:65 plugins/arch-compliance/tests/test_diff_cli.py:48`
- reasoning: Each production entry resolves exactly one repo per process: main() resolves the repo once at cli_check_diff.py:63 and posttooluse_gate.py:65, and the hook is a fresh subprocess per edit. The only multi-root producer is in-process tests, where test_diff_cli calls main() over separate tmp_path repos (:48, :61, ...). Those tests are covered by the test-only fixture. The refusal raises AcfInputError rather than evicting, so no repair code sits in production.

#### C101 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:67 plugins/arch-compliance/python/acf/detectors/python_pack.py:97 plugins/arch-compliance/python/acf/cli_check_diff.py:168-182 config/architecture/mandates.yml:57`
- reasoning: The scanners stamp literal mandate ids (python_pack.py:67, :97), and the ratchet runs only in cli_check_diff (:168-182; the hook's _scan_paths has no ratchet call). The contract therefore records existing facts. I grepped detector: across the shipped registries and fixtures: each built-in detector appears at most once per file, so the one-active-row cost hits no shipped registry.

#### C102 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:104-105 plugins/arch-compliance/python/acf/cli_check_llm.py:54 plugins/arch-compliance/python/acf/loader.py:70-73 plugins/arch-compliance/tests/test_registry.py:46-47`
- reasoning: inject_constraints wraps load_mandates in except AcfInputError (:104-105). cli_check_llm.py:54 calls load_mandates bare. load_model_file converts only ValidationError (loader.py:70-73), so an AcfInputError raised in a model_validator propagates with its own type. The existing _unique_ids already relies on this (registry.py:33-41), and test_registry.py:46-47 tests it.

#### C103 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37 plugins/arch-compliance/python/acf/detectors/facade_sinks.py:51`
- reasoning: Built-in scanners each parse their own text (python_pack.py:35, facade_sinks.py:51). Sharing one parse across N host ast rows on a file is a plain efficiency choice and leaves the built-in parse count unchanged.

#### C104 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:46-52 plugins/arch-compliance/python/acf/finding.py:11-19`
- reasoning: apply_registry routes a finding to its row by finding.mandate_id alone (:46), so a host-supplied mandate_id would attach the finding to any row. Finding carries mandate_id, detector and severity as plain fields (finding.py:11-19). HostHit omits them, which makes misrouting unrepresentable (rung 1).

#### C105 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:72-81 .github/workflows/ci.yml:40`
- reasoning: .gitignore:8 lists .acf/. The hook exits 0 before any acf import beyond acf.repo when .acf/enabled is absent (posttooluse_gate.py:72-81). CI runs python -m acf.cli_check_diff at ci.yml:40 from a fresh checkout that cannot carry the gitignored marker. Requiring the marker there would disable CI, so the stated residual case is the honest one.

#### C106 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:27-52 plugins/arch-compliance/python/acf/cli_check_diff.py:127 plugins/arch-compliance/hooks/posttooluse_gate.py:254`
- reasoning: scan_python_file (python_pack.py:27-52) takes no registry, and both gates call it on every changed .py file (cli_check_diff.py:127, posttooluse_gate.py:254). scan_typescript_file behaves the same way. Without the sink filter, a [ci]-only no-shims.hasattr finding would survive in the hook. The filter is therefore not redundant with registry.active selection. The claim's parenthetical is inaccurate: Decision 2 does state this reason, citing python_pack.py:27-52.

#### C107 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:22-28 pyproject.toml:19-20`
- reasoning: The hook inserts the plugin's python/ at sys.path[0] and imports acf at :28 before any host root exists. The console scripts (pyproject.toml:19-20) start with sys.path[0] set to the script directory. Appending the host root therefore adds no shadowing. The plugin's acf is already in sys.modules, so a host acf/ cannot replace it, and the dropped refusal had no producer. A shadowed host top-level name fails at import or getattr inside the wrapped region as UnknownDetectorError.

#### C108 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:69-74 plugins/arch-compliance/hooks/posttooluse_gate.py:113-117 plugins/arch-compliance/python/acf/enforcement.py:49`
- reasoning: _scan_changed and _scan_paths both run inside each gate's try (cli_check_diff.py:69-74, posttooluse_gate.py:113-117). Each except already lists DetectorPackError, so reading inside scan_host_guards reaches an existing handler. A lazy read in line_lookup would run at enforcement.py:49, which is outside both trys.

#### C109 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:16 plugins/arch-compliance/python/acf/judge.py:29-36 plugins/arch-compliance/python/acf/registry.py:58-60`
- reasoning: judge.py:16 imports acf.registry.Mandate, so registry importing judge would be a cycle, and judge also pulls in httpx (:11). Today registry.py:60 checks known_detectors only for ast/guard rows, so nothing enforces llm prompt ids. All four shipped llm detectors are in LLM_PROMPT_IDS (:29-36).

#### C110 — SURVIVED
- evidence: `hm:scripts/ci/run_guards.py:116 hm:scripts/ci/run_guards.py:317-321 config/architecture/ARCHITECTURE.md:120-123`
- reasoning: The origin runner filters rows per site at :116 and defaults --site to ci at :318-320. The doctrine section text at ARCHITECTURE.md:120-123 scopes it to adr.yml host values, as the claim says. A required argparse flag fails with a usage error instead of silently choosing a site.

#### C111 — SURVIVED
- evidence: `hm:scripts/ci/run_guards.py:126-130 plugins/arch-compliance/profiles/python-service/mandates.yml:5`
- reasoning: The origin runner refuses a site that resolves to zero guards (:126-130). No shipped row declares precommit today (Appendix; profile rows declare [ci, hook]). Without both changes, --call-site precommit would select nothing and report clean.

#### C112 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:82-95 hm:scripts/ci/genre_conditional_guard.py:39-40`
- reasoning: Host objects define dunder methods that run code (genre_conditional_guard.py:39-40). Attribute access or comparison on a host subclass instance runs that code. Doing the exact-type check, the field-type check and model_validate inside the try keeps every such call wrapped, the same convert-inside-try pattern the TS bridge already uses (:82-95). type() and the instance __dict__ data descriptor cannot be overridden by the instance.

#### C113 — SURVIVED
- evidence: `docs/design/ADR_GATE_HOST_CONTRACT.md:295-301 plugins/arch-compliance/python/acf/adr/host.py:24-25`
- reasoning: The approved spec records 'Not adopted: a refusal of absolute paths or .. segments' for runs_dir and ledger_path (:295-301). Those fields are PosixStr only (host.py:24-25). The design leaves them unchanged, as claimed.

#### C114 — SURVIVED
- evidence: `hm:scripts/ci/genre_conditional_guard.py:40 hm:scripts/ci/genre_conditional_guard.py:52`
- reasoning: Finding.__str__ calls self.line_text.strip() (:40) on a non-frozen dataclass, so an instance built with a non-str line_text makes str() raise. Without _describe, the f-string in the raise inside the except handler would raise AttributeError past the gate's except tuple, giving a traceback. Caveat: the producer is latent. HM's only construction passes a str line (:52), and no HM code raises an exception carrying a Finding. The mechanism rests on the genuine external boundary (arbitrary host code), not on a live producer (advisory finding filed).

#### C115 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:9-11 plugins/arch-compliance/python/acf/registry.py:43-45`
- reasoning: Mandate declares id, severity, detection, detector, languages (Literal with 'none', :11), call_sites list[str], status and params dict|None, and sets no model_config. MandateRegistry already carries an @property (by_id, :43-45) next to a model_validator, so a property and plain methods are compatible.

#### C116 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/finding.py:6-19 plugins/arch-compliance/python/acf/registry.py:17`
- reasoning: Finding's required fields are mandate_id, severity, path, line, message and detector. confidence and detection have defaults. Severity is a str Enum with BLOCK and WARN (finding.py:6-8), and Mandate.severity is Literal BLOCK/WARN (registry.py:17), so Severity(m.severity) constructs.

#### C117 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:23 plugins/arch-compliance/python/acf/enforcement.py:43-52`
- reasoning: by_id lookup is at :43/:46, the unenforced drop at :47, the exemption check at :49-51 and severity at :52. LineLookup is Callable[[str, int], str] (:23), which make_line_lookup's _lookup satisfies.

#### C118 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:69-82 plugins/arch-compliance/python/acf/cli_check_diff.py:121-156 plugins/arch-compliance/python/acf/cli_check_diff.py:168-184`
- reasoning: Load is at :70 and scan at :71, inside a try whose except at :72 lists GitError, AcfInputError, UnknownDetectorError and DetectorPackError. The lookup closure and apply_registry are at :76-82. In the .py branch, repo, text (:125), posix (:122), lines (:121) and registry are in scope after :150. The TS branch reads at :152 and can bind text. changed (:110) and file_lines (:109) are in scope after :182.

#### C119 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:91-125 plugins/arch-compliance/hooks/posttooluse_gate.py:200-209 plugins/arch-compliance/hooks/posttooluse_gate.py:229-294`
- reasoning: Every named point is at the stated lines: deferred imports :91-104, load try :106-110, scan try :113-117 (DetectorPackError only today), lookup and apply_registry :119-125, resolve and dedupe :200-209, is_file skip :239, relative_to/ValueError :242-245, filters :229-236 and :284-286, build loop :284-294. text (:251) and rel (:243) are in scope in both the .py and the else/TS branch.

#### C120 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:72 plugins/arch-compliance/hooks/posttooluse_gate.py:113-117 plugins/arch-compliance/python/acf/exceptions.py:5-30`
- reasoning: Both runners are called inside _scan_changed and _scan_paths, which sit under each gate's try. The three error types are AcfError subclasses (exceptions.py:5, :13, :29), and cli_check_diff.py:72 plus the widened hook except list all three. apply_registry stays I/O-free. One residual path is filed as an advisory: isinstance(exc, KeyboardInterrupt) inside the handlers can run host code via a __class__ override.

#### C121 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_diff_cli.py:48 plugins/arch-compliance/python/acf/cli_check_diff.py:63 C:/Python313/Lib/dataclasses.py:757`
- reasoning: The stdlib supplies every piece: importlib.util.spec_from_file_location with a synthetic name, module_from_spec, sys.modules registration before exec_module, and getattr inside a try. dataclasses needs that registration (:757). test_diff_cli calls main() in process per tmp repo (:48 and others), and main resolves the root afresh each call (:63). Resetting _ACTIVE_ROOT and deleting the _acf_host_ keys therefore isolates tests.

#### C122 — SURVIVED
- evidence: `C:/Python313/Lib/dataclasses.py:757 C:/Python313/Lib/dataclasses.py:760`
- reasoning: dataclasses._is_type evaluates sys.modules.get(cls.__module__).__dict__ for string annotations (:757, :760). If the synthetic module is not registered first, that is None.__dict__, an AttributeError. Registering before exec_module is therefore required and sufficient.

#### C123 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:16 plugins/arch-compliance/python/acf/detectors/__init__.py:5-9 plugins/arch-compliance/tests/test_adr_import_graph.py:63-66`
- reasoning: acf.engine imports only pathlib. registry imports exceptions and loader, never acf.detectors. The detectors package and its scanners import only engine, finding and exceptions (__init__.py:5-9 and the scanner headers), so adding registry to __init__ creates no cycle. The import-graph test bans only 'scripts' imports from acf.adr and the literal 'acf.adr' in the hooks (:63-66, :70-76), so citations importing acf.engine is allowed. judge imports registry (:16), not the other way round, and nothing in acf.detectors imports judge or adr.

#### C124 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:53-55 plugins/arch-compliance/python/acf/registry.py:64 plugins/arch-compliance/python/acf/loader.py:43-50`
- reasoning: load_mandates calls load_model_file(path, Mandate, subject='mandates file', fmt='yaml', many=True) at :53-55 and returns MandateRegistry(mandates=..., source_path=path.as_posix()) at :64. The loader signature matches (loader.py:43-50).

#### C125 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_repo_paths.py:47-48 plugins/arch-compliance/hooks/posttooluse_gate.py:11-12`
- reasoning: The allowlist entry for posttooluse_gate.py pins exactly the :11 text (mandates.yml missing: non-zero exit). The :12 text contains no config/architecture spelling, so the CONFIG_ARCH_RE scan does not touch a reworded :12 that names no path.

#### C126 — SURVIVED
- evidence: `config/architecture/mandates.yml:60 plugins/arch-compliance/python/acf/detectors/python_pack.py:77-82`
- reasoning: The row's exemption_tokens is [fail-loud.bare-except-ok] (:60). _is_bare_or_exception flags only node.type None or Name 'Exception' (:78-81), so except BaseException is not flagged.

#### C127 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/engine.py:8 plugins/arch-compliance/python/acf/engine.py:17-24`
- reasoning: engine imports only pathlib (:8) and defines contains_backslash (:17-24). The design also needs import ast for parse_python, which is stdlib too, so the module stays stdlib-only.

#### C128 — SURVIVED
- evidence: `README.md:66-74 plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23 plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15 plugins/arch-compliance/tests/test_registry.py:23-26`
- reasoning: The README table (:66-74) lists the seven Python detector ids with their mandate ids in two backticked columns, which a test can parse. The TS literals sit at the cited lines. test_registry already builds inline YAML registries as strings (:23-26, :33-37), so the new cases fit that pattern.

#### C129 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_diff_cli.py:25-48 plugins/arch-compliance/tests/test_hooks.py:22-29`
- reasoning: test_diff_cli already builds a temp git repo and calls main() in process (:25-48), and test_hooks runs the hook in a subprocess (:22-29). Rows declaring only [ci], only [precommit] or only hook sites pass _row_shape and _check_builtin. The TS detectors need node_modules, which scan_typescript_file requires (typescript_bridge.py:30-35) and which the TS tests already need.

#### C130 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:109-110 plugins/arch-compliance/hooks/posttooluse_gate.py:226-227`
- reasoning: file_lines and changed are locals of _scan_changed (:109-110), and file_lines and rel_paths are locals of _scan_paths (:226-227). A call before each function's return therefore sits inside the gate's scan try.

#### C131 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:29-61 plugins/arch-compliance/python/acf/cli_check_diff.py:69-74`
- reasoning: The parser is built at :29-61. argparse's required=True with choices calls parser.error, which is SystemExit(2) in process. The try at :69-74 wraps load and scan and catches AcfInputError, so an empty-selection raise placed between them reaches the handler and returns 1.

### Unanchored findings

- **important**: The TS bridge's runtime check that a Node finding's mandate_id equals TS_MANDATE_IDS[detector] exists only because the Node rules keep emitting a duplicate literal. Rung 1 would be to drop mandate_id from the rule output and key the TS self-test on detector, making drift unrepresentable. The spec never weighs this and keeps three artefacts (Node literal, runtime comparison, pinning test) for one fact.
  - evidence: `plugins/arch-compliance/detectors/typescript/src/scan.ts:83`
- **advisory**: Both broad handlers re-raise KeyboardInterrupt via isinstance(exc, KeyboardInterrupt) inside the except body. For a non-subclass, isinstance falls back to reading exc.__class__, which a host exception can override to raise, so the error escapes the handler untyped. A preceding 'except KeyboardInterrupt: raise' clause matches on the real type and runs no host code.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:371`
- **advisory**: _describe's named producer is latent. The origin host builds Finding only with a str line_text and never raises an exception carrying one, so the mechanism stands on the generic external-host boundary, not on a live producer, and should say so.
  - evidence: `hm:scripts/ci/genre_conditional_guard.py:52`
- **advisory**: Part of Decision 4's import-deferral rationale is wrong. The SubagentStart hook and acf-check-llm call load_mandates without known_detectors, so an import placed in the known_detectors branch would never run there; only the PostToolUse hook (which now passes known_detectors) supports deferring.
  - evidence: `plugins/arch-compliance/hooks/inject_constraints.py:104`
- **advisory**: The ast-hit path check refuses at rung 3 where rung 1 applies: a path-less ast hit type, with the runner supplying the path. The written reason ('a second type carrying the same facts') is weak because that type would carry fewer facts.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:417`

### Looked for but did not find

- A shipped registry with two active rows naming the same built-in detector (grep of detector: across mandates.yml, both profiles and the fixture): none
- A production caller that resolves more than one repo root per process: none; only in-process tests (test_diff_cli main calls)
- A cycle from acf.registry to acf.detectors or acf.judge: none; judge imports registry, not the reverse
- A test pinning posttooluse_gate.py docstring line 12: none; only line 11 is allowlisted
- A repair-on-read for host findings: none; HostHit carries no mandate_id, detector or severity, and the runner builds Finding from the row
- A silent path where a host import or call failure is swallowed: none; each wraps to UnknownDetectorError or DetectorPackError inside a gate try

### Mechanism traces

- **Mandate._row_shape model_validator**
  - invalid state: an ast/guard row with ':' in detector whose path or callable is malformed, or an active ast/guard row with no call_sites intersecting TIER1_CALL_SITES, or an active host ast row with languages == 'none'
  - producer: `config/architecture/mandates.yml:57`
  - rung 1 (highest applicable 1); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:206`
- **CallSite Literal on Mandate.call_sites**
  - invalid state: a call_sites entry not in {ci, precommit, hook, posttooluse, audit}
  - producer: `plugins/arch-compliance/python/acf/registry.py:21`
  - rung 1 (highest applicable 1); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:206`
- **_check_builtin and reserved-id refusal in load_mandates**
  - invalid state: an active built-in ast/guard row with detector not in KNOWN_DETECTORS, or id != contract.mandate_id, or a Tier-1 site not in contract.call_sites; or an active non-built-in row whose id is a built-in mandate_id
  - producer: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:58`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:296`
- **llm_prompt_ids check in load_mandates**
  - invalid state: an active llm row whose detector is not in LLM_PROMPT_IDS
  - producer: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:58`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:257`
- **apply_registry call_sites filter (runs_at)**
  - invalid state: a finding whose row's call_sites do not intersect the gate's sites
  - producer: `plugins/arch-compliance/python/acf/detectors/python_pack.py:27-52`
  - rung 2 (highest applicable 2); repairs=False
  - hardening rejected because: This filter is needed at that one sink because the built-in scanners emit findings without consulting the registry
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:434`
- **empty --call-site selection refusal in acf-check-diff**
  - invalid state: registry.active({site}) contains no ast or guard row
  - producer: `plugins/arch-compliance/profiles/python-service/mandates.yml:5`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:453`
- **one host root per process refusal (_ACTIVE_ROOT)**
  - invalid state: load_host_detector called with repo_root.resolve() != _ACTIVE_ROOT in one process
  - producer: `plugins/arch-compliance/tests/test_diff_cli.py:48`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: Production callers resolve one repository per process ... In-process tests over several roots reset the loader through a test fixture
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:355`
- **fresh_host_loader test fixture**
  - invalid state: _ACTIVE_ROOT or _acf_host_ sys.modules entries left by a prior test's root
  - producer: `plugins/arch-compliance/tests/test_diff_cli.py:48`
  - rung 5 (highest applicable 5); repairs=True
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:476`
- **load_host_detector wrapped exec/getattr with sys.modules rollback**
  - invalid state: a host module that raises during exec_module or __getattr__, or lacks the callable; or a half-executed module left in sys.modules
  - producer: `hm:scripts/ci/metadata_facade_guard.py:66`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:371`
- **_call_host wrapping and _revalidate exact-type rebuild**
  - invalid state: a host callable that raises, returns None/str/bytes/non-iterable, or yields an item where type(item) is not HostHit or whose path/line/message are not exactly str/int/str
  - producer: `hm:scripts/ci/genre_conditional_guard.py:33-40`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:398`
- **_describe constant-message fallback**
  - invalid state: a host exception e for which str(e) or type(e).__name__ raises
  - producer: `hm:scripts/ci/genre_conditional_guard.py:40`
  - rung 5 (highest applicable 5); repairs=True
  - hardening rejected because: str(exc) runs host code after the try has exited. That code can raise
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:409`
- **_to_findings containment and ast expected_path refusal**
  - invalid state: a HostHit whose resolve_under_root(repo_root, path) is None, or an ast-row hit whose path != the scanned file's path
  - producer: `hm:scripts/ci/metadata_facade_guard.py:66`
  - rung 3 (highest applicable 1); repairs=False
  - hardening rejected because: The ast path check refuses rather than making a wrong path unrepresentable, because one HostHit type serves both callable kinds, and a path-less ast hit would be a second type carrying the same facts.
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:417`
- **scan_host_guards lenient line fill for exemption lookup**
  - invalid state: a guard finding whose path is not a key of the gate's file_lines, so its exemption token is invisible
  - producer: `plugins/arch-compliance/python/acf/cli_check_diff.py:126`
  - rung 2 (highest applicable 2); repairs=True
  - hardening rejected because: a guard may flag any file, a binary or a document included, and these lines serve only the exemption-token lookup, so a stray byte is replaced rather than raised
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:422`
- **TS bridge mandate_id comparison against TS_MANDATE_IDS**
  - invalid state: a Node scanner item whose mandate_id != TS_MANDATE_IDS[item['detector']] or whose detector is not a key
  - producer: `plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23`
  - rung 3 (highest applicable 1); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:321`
- **resolve_under_root mapping RuntimeError/ValueError to None**
  - invalid state: a path string whose resolve() raises (symlink loop on 3.11/3.12, embedded NUL) or resolves outside root
  - producer: `plugins/arch-compliance/hooks/posttooluse_gate.py:204`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:120`
- **ratchet baseline/roots containment refusal**
  - invalid state: params.baseline or a params.roots entry that escapes repo_root, loops, is missing, or (for roots) is not an existing directory
  - producer: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:124`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:524`

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
- **C30** [premise] [load-bearing]: pyproject.toml:5 allows Python 3.11, where a non-strict Path.resolve() raises RuntimeError on a symlink loop (3.13 does not), and on POSIX an embedded NUL makes resolve() raise ValueError; resolve_under_root catching both and returning None makes such a host path report as a missing file at load (UnknownDetectorError), be refused as a host hit (DetectorPackError in _to_findings), or classify as unresolved in citations, never a traceback.
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
- **C45** [premise] [load-bearing]: An active row that is not a built-in ast/guard row (a host ast/guard row, or an llm, grep or manual row) whose id equals a built-in mandate id would receive that built-in scanner's findings, because scan_python_file and scan_typescript_file run on every changed file of their language (cli_check_diff.py:127, :153-156; posttooluse_gate.py:254, :279-282) and apply_registry routes each finding by mandate_id alone (enforcement.py:46); load_mandates with known_detectors refusing such a row (AcfInputError, spec §4.2 and Decision 3) refuses no shipped or fixture row (Appendix census).
  - spec citation: `plugins/arch-compliance/python/acf/enforcement.py:46`
- **C46** [premise] [load-bearing]: _to_findings refusing any host hit for which resolve_under_root(repo_root, hit.path) is None refuses a validate_posix_rel_path-valid path that escapes the repository through an in-repo directory symlink, accepts a contained path whether or not the file exists (non-strict resolve), and is applied to every host finding in both runners (spec §4.4 items 5-7), so no host-supplied path outside the repository becomes a Finding.
  - spec citation: `None`
- **C47** [root_cause] [load-bearing]: Root cause of the registry/gate disagreement: a status: partial row is live in both Tier-1 gates (enforcement.py:47 drops only 'unenforced'; the gates' row filters likewise), yet load_mandates never checks it, so a host can name a non-built-in detector in a partial ast/guard row today, load cleanly with known_detectors=KNOWN_DETECTORS, and have nothing ever execute it.
  - spec citation: `plugins/arch-compliance/python/acf/enforcement.py:47`
- **C48** [root_cause] [load-bearing]: Root cause of the hook defect: posttooluse_gate.py:107 calls load_mandates(mandates_path) without known_detectors, so an active row naming an unknown detector is never validated in the PostToolUse hook and produces zero findings at edit time instead of failing loud.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:107`
- **C49** [root_cause] [load-bearing]: Root cause of the exemption defect: the _line_lookup closures (cli_check_diff.py:76-80, posttooluse_gate.py:119-123) are token-identical and consult only file_lines, which holds changed .py/.ts/.tsx files (cli_check_diff.py:126, :152; posttooluse_gate.py:248-252), so a finding on any other file gets "" and apply_registry (enforcement.py:49-50) cannot see an inline exemption token on it.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80`
- **C50** [deletion] [load-bearing]: Deleting citations._looks_absolute (:49-51) and _escapes_repo (:74-76) is safe: their only references are the call sites at citations.py:161 and :163, no test imports them, resolve_citation keeps its order, and exactly two behaviours change, both stated in spec §4.1 and §4.9: a drive-relative string such as 'C:a/b.py' classifies external, and on Python 3.11 and 3.12 a symlink-loop citation classifies unresolved instead of raising RuntimeError.
  - spec citation: `plugins/arch-compliance/python/acf/adr/citations.py:74-76`
- **C51** [deletion] [load-bearing]: Deleting cli_check_diff._active_mandates and the hook's inline filters in favour of registry.active(call_sites, detector=...) changes no selection except by call_sites: for every shipped registry, the only built-in row that stops running at a gate is no-shims.hasattr leaving the PostToolUse hook (it declares [ci]).
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99`
- **C52** [deletion] [load-bearing]: Removing LLM_PROMPT_IDS from KNOWN_DETECTORS changes behaviour only for ast/guard rows naming an LLM prompt id: load_mandates consults known_detectors only for ast/guard rows (registry.py:60), and no code reads KNOWN_DETECTORS for llm rows. The import at cli_check_diff.py:21 stays and feeds load_mandates(..., llm_prompt_ids=LLM_PROMPT_IDS), so LLM_PROMPT_IDS keeps a runtime consumer.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:21`
- **C53** [deletion] [load-bearing]: Replacing the literal mandate ids in the five scanner modules with module constants changes no emitted finding, and no test asserts on the scanner source text in a way the change would break.
  - spec citation: `None`
- **C54** [deletion] [load-bearing]: Deleting the two _line_lookup closures (cli_check_diff.py:76-80, posttooluse_gate.py:119-123) for make_line_lookup(file_lines), which is their body unchanged and reads no file, changes no exemption result for any finding at a338cad. The only new lines in file_lines are those scan_host_guards adds for files a host guard flags, so a built-in finding on such a file becomes exemptable as built-in findings on changed code files already are; a built-in finding on any other file still gets ''.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80`
- **C55** [deletion] [load-bearing]: Deleting the five detector-id sets (PYTHON_AST_DETECTOR_IDS, GUARD_DETECTOR_IDS, CONFIG_AST_DETECTOR_IDS, ALL_PYTHON_DETECTOR_IDS, TS_DETECTOR_IDS) touches only the references git grep -n "_DETECTOR_IDS" -- plugins tests prints, each of which the spec rewrites, and leaves KNOWN_DETECTORS as the only set of built-in detector ids in plugins/arch-compliance/python.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/__init__.py:11-28`
- **C56** [deletion] [load-bearing]: Replacing the inline params extraction in both gates with facade_sink_args, fsm_guard_args and build_artifact_args (required arguments as str(params.get(key, '')); allowlist_globs and atomic_is_sink passed unchanged when the key is present, null included; path_prefixes only when present and non-empty) produces the same scanner call for every row as today, because the scanners' signature defaults (facade_sinks.py:24-25, build_artifacts.py:16, :23) equal what the gates pass today when the param is absent.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/facade_sinks.py:24-25`
- **C57** [deletion] [load-bearing]: Replacing the four parse-and-skip copies with acf.engine.parse_python changes no scanner output, and no other site in plugins/arch-compliance/python parses Python with a SyntaxError skip.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37`
- **C58** [deletion] [load-bearing]: Once each params.roots entry is resolved and contained with resolve_under_root, every path rglob yields under it keeps the resolved root as a lexical prefix, so the walk filter's except ValueError: continue (fail_loud_ratchet.py:59-62) cannot fire and deleting that branch changes no count; scan_tree's callers are scan_ratchet and test_portable_guards.py:107.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:59-62`
- **C59** [deletion] [load-bearing]: Replacing count_bare_excepts' inline bare-or-Exception test (fail_loud_ratchet.py:31-34) with python_pack's predicate (python_pack.py:77-82, renamed is_bare_or_exception) changes no count, since the two tests accept exactly the same handlers; the predicate's only other caller is python_pack.py:61, no test references it by name, and the ratchet importing python_pack creates no import cycle.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:31-34`
- **C60** [mandate] [load-bearing]: ## Fail loud: every invalid state in spec §6.1 is refused by the named component with the named error, including: acf-check-diff without --call-site (usage error, exit 2) or with a site selecting no active ast/guard row (AcfInputError); a host module whose import or callable lookup raises any exception but KeyboardInterrupt (UnknownDetectorError); a host callable or its result raising any exception but KeyboardInterrupt, or yielding a non-exact-type or invalid HostHit (DetectorPackError); a host path whose stat raises OSError (typed error at each caller); a ratchet roots entry naming no existing directory (DetectorPackError); a TypeScript item with an unknown detector or differing mandate_id; an llm row with an unknown prompt id. Of the design's three broad handlers, the load and call handlers re-raise as typed errors; _describe's handler swallows only a failure to format the host's exception, returning a constant message inside the typed error still raised, and carries the fail-loud.bare-except-ok token with its reason, as ARCHITECTURE.md:29-30 permits for a handler 'explicitly exempted with a reason'.
  - spec citation: `None`
- **C61** [mandate] [load-bearing]: ## Fail loud: no active built-in ast/guard row can load with known_detectors yet never receive a finding from either Tier-1 gate: _check_builtin refuses a detector not in KNOWN_DETECTORS (LLM prompt ids are not keys), a row id that differs from the detector's stamped mandate_id, and any declared Tier-1 call site outside the detector's contract call_sites (fail_loud_ratchet: DIFF only); and Mandate._row_shape refuses an active ast/guard row with no Tier-1 site. Host rows are dispatched by both gates' host runners at any Tier-1 site.
  - spec citation: `None`
- **C62** [mandate]: ## Declared, never defaulted governs the ADR gate's host values in config/architecture/adr.yml and this design adds none of those; the spec states that it follows the same practice by choice for the values it adds (repo_root required for an active host row, apply_registry's call_sites keyword without a default, --call-site required) and does not claim the section requires it.
  - spec citation: `config/architecture/ARCHITECTURE.md:118-133`
- **C63** [mandate]: ## No shims: callable lookup is getattr(mod, attr, None) followed by callable() and a raise; no hasattr, and no host-detector failure has a silent fallback.
  - spec citation: `config/architecture/ARCHITECTURE.md:43-53`
- **C64** [mandate]: ## POSIX paths: HostHit.path is validated by validate_posix_rel_path (which refuses backslashes) and error messages use .as_posix().
  - spec citation: `config/architecture/ARCHITECTURE.md:55-64`
- **C65** [mandate]: ## One base exception: the design adds no exception class and uses AcfInputError, UnknownDetectorError and DetectorPackError (exceptions.py:5, :13, :29), all subclassing AcfError.
  - spec citation: `plugins/arch-compliance/python/acf/exceptions.py:5`
- **C66** [mandate]: ## One owner for host paths: acf/engine.py, acf/registry.py, acf/detectors/__init__.py and the new acf/detectors/host.py spell no config/architecture path, and the acf-mandate skill snippet takes MANDATES_REL and resolve_repo from acf.repo.
  - spec citation: `None`
- **C67** [mandate]: ## Prose names no host: the runtime messages in §4.2-§4.4 and the prose changes in §4.8 name no origin host.
  - spec citation: `config/architecture/ARCHITECTURE.md:135-143`
- **C68** [mandate]: ## Live consumers: each new export in §6.2 has the named non-test caller (file_under_root: load_mandates, load_host_detector, scan_host_guards, scan_ratchet, the hook's _collect_paths; parse_python: four scanners and scan_host_ast_file; the *_args functions: both gates; CallSite: Mandate.call_sites; DIFF_CALL_SITES: acf-check-diff's --call-site choices and KNOWN_DETECTORS), acf.judge.LLM_PROMPT_IDS keeps a runtime consumer, and the five deleted detector-id sets leave no dead export behind.
  - spec citation: `None`
- **C69** [mandate]: ## No completeness claims: every population claim in the spec carries a re-runnable recipe (§1, §3, Appendix) or is a per-item table, as ARCHITECTURE.md:159-169 requires.
  - spec citation: `config/architecture/ARCHITECTURE.md:159-169`
- **C70** [mandate]: ## Declared text decoding: the new read_text calls (cli_check_diff.py TypeScript branch, scan_host_guards' read of flagged files) declare encoding='utf-8'; errors='replace' in scan_host_guards is permitted by that rule, which governs the declared encoding; no subprocess is added.
  - spec citation: `None`
- **C71** [mandate]: ## Release discipline: because shipped skill prose changes, the version is bumped 0.2.2 -> 0.2.3 in both files ARCHITECTURE.md:186-187 names (pyproject.toml:3, plugins/arch-compliance/.claude-plugin/plugin.json:3).
  - spec citation: `config/architecture/ARCHITECTURE.md:184-194`
- **C72** [mandate]: ## Single point of definition: each existing definition listed in spec §4.9 is deleted and its callers switched (citations' path helpers, the five detector-id sets, the line-lookup closures, the active-row filters, the duplicated params extraction, the ratchet's joins, existence check and unreachable walk-filter branch, the four parse-and-skip copies, test_self_host's resolve-and-is_file), the scanners' signature defaults stay the one default for optional params, and the spec makes no claim that §4.9 lists every duplicate in the tree.
  - spec citation: `None`
- **C73** [mandate]: ## Scoped refactor: Decision 8 deletes the existing definitions §4.9 lists, each duplicated by a new definition in this design, in the code paths it changes, and makes no claim beyond that list; the two pre-existing dispatch loops stay (two call sites of one procedure), and the git-supplied join-and-is_file in _scan_changed (cli_check_diff.py:118-119) is a different job recorded as ADJACENT.
  - spec citation: `config/architecture/ARCHITECTURE.md:213-215`
- **C74** [mandate]: ## Frozen ledger format: the design changes no ledger model.
  - spec citation: `config/architecture/ARCHITECTURE.md:145-151`
- **C75** [mandate]: The design complies with the five portable governing principles at docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51 and fulfils that spec's call for project-specific detector extension points (:102, :123, :125).
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51`
- **C76** [mandate]: ## Fail loud: a host hit whose path resolves outside the repository is refused (DetectorPackError in _to_findings) rather than kept; scan_host_guards mapping a contained flagged path for which file_under_root returns None (missing, directory, a 3.13 symlink loop) to [] and decoding with errors='replace' hides no failure, because such a path has no line that could carry an exemption token, so the finding stays; an OSError from the stat or the read raises DetectorPackError inside each gate's scan try; and make_line_lookup does no I/O.
  - spec citation: `None`
- **C77** [mandate] [load-bearing]: ## Fail-loud ratchet: the design keeps the ratchet's whole-tree freeze unchanged, routes it to ci and precommit only through KNOWN_DETECTORS, refuses a baseline or roots entry outside the repository or a roots entry naming no directory (DetectorPackError), and §4.8 adds both constraints to the section's enablement instruction (ARCHITECTURE.md:72-73).
  - spec citation: `config/architecture/ARCHITECTURE.md:70-73`
- **C78** [shape_fit] [load-bearing]: Mandate.runs_at and MandateRegistry.active become the single definition of 'this row runs at this gate' for the Tier-1 gates; after the change no other Tier-1 site (cli_check_diff, posttooluse_gate, enforcement, the host runners) keeps its own active-row filter.
  - spec citation: `None`
- **C79** [shape_fit] [load-bearing]: After the design, deciding whether a path string from outside the code (registry row, host hit, harness payload) lies inside the repository has one implementation, acf.engine.resolve_under_root, used directly or through file_under_root by load_mandates, load_host_detector, _to_findings (for every host hit), scan_host_guards, the ratchet, citations.py, the PostToolUse hook's _collect_paths and tests/test_self_host.py:40; validate_posix_rel_path checks only a string's shape and every host hit gets both checks; parse_python is the one parse-or-skip (four scanners and scan_host_ast_file).
  - spec citation: `None`
- **C80** [shape_fit] [load-bearing]: Building Finding from a validated HostHit in acf.detectors.host is ADJACENT to, not a partial duplicate of, the TypeScript bridge's JSON-to-Finding coercion (typescript_bridge.py:75-95), because the inputs share no format.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:75-95`
- **C81** [shape_fit] [load-bearing]: Building Finding from a HostHit is ADJACENT to the judge's _to_finding (judge.py:238-255): the judge demotes severity by confidence and admits path="<diff>" and line=0, while host findings take severity from the row and require a relative path and line >= 1, so no shared constructor is warranted.
  - spec citation: `plugins/arch-compliance/python/acf/judge.py:236-253`
- **C82** [shape_fit] [load-bearing]: acf/detectors/host.py partially duplicates no existing mechanism: nothing in the plugin today loads or executes code from a registry-supplied file path, and the loader's one-time append of a host root to the end of sys.path is ADJACENT to the hooks' own start-up insertion of the plugin's python/ directory (posttooluse_gate.py:22-26, inject_constraints.py:28-29).
  - spec citation: `None`
- **C83** [shape_fit] [load-bearing]: make_line_lookup consolidates the only two line-lookup closures passed to apply_registry; no third LineLookup implementation exists (e.g. in cli_check_llm.py, the judge, or any skill snippet) that would remain a second definition.
  - spec citation: `None`
- **C84** [shape_fit] [load-bearing]: Detector-reference validation lives in two cooperating places only, Mandate._row_shape (row-local rules, every caller) and load_mandates with known_detectors (built-in contracts and host-file existence); no other validator (the acf-mandate skill's ## Validate snippet, test_profile_drift.py, the architecture-review skill, acf-setup) independently checks detector ids or call sites in a way that would diverge.
  - spec citation: `None`
- **C85** [shape_fit] [load-bearing]: The §4.7 contract-against-dispatch test ties KNOWN_DETECTORS' call_sites to the gates' dispatch: a detector the table says runs at a gate but which that gate does not dispatch fails the test; the opposite drift cannot attach a finding to any loaded row, because _check_builtin refuses a row declaring that site and apply_registry drops a finding whose row does not run at the gate, so it over-refuses and never silently drops a row.
  - spec citation: `None`
- **C86** [shape_fit] [load-bearing]: resolve_under_root SUBSUMES the PostToolUse hook's Path.is_absolute() join with its relative_to/except ValueError containment test (posttooluse_gate.py:203-204, :242-245) and the ratchet walk filter's except ValueError (fail_loud_ratchet.py:59-62): each decides by hand whether a path lies in the root; the spec deletes those branches and keeps only relative_to(...).as_posix() as the conversion of an already-contained Path to its key, and §4.1, §4.6, §4.9 and §5.2 state this consistently.
  - spec citation: `None`
- **C87** [shape_fit] [load-bearing]: The spec's account of where host code runs is consistent: Decision 7 guarantees that every failure raised while a runner calls host code (module execution, callable lookup, the call, consuming and rebuilding its result, formatting its exception) becomes a typed ACF error, and states that the wrapping does not confine host code (atexit handlers, threads); no other section claims that host code runs only inside the wrapped regions; and the fresh_host_loader fixture is the single reset of loader state.
  - spec citation: `None`
- **C88** [shape_fit] [load-bearing]: TS_MANDATE_IDS is the single Python definition of the TypeScript mandate ids: the bridge stamps from it, KNOWN_DETECTORS reads it, and no other non-test Python site spells 'fail-loud.empty-catch' or 'no-shims.explicit-any' as a runtime value; the Node literals are checked against it on every finding.
  - spec citation: `None`
- **C89** [shape_fit]: apply_registry is the single owner of Finding.severity on the Tier-1 path (enforcement.py:52); the host runner's severity value is a required-field fill that apply_registry overwrites, as §4.4 item 5 and §5.2 state.
  - spec citation: `None`
- **C90** [shape_fit] [load-bearing]: The join-and-is_file in _scan_changed (cli_check_diff.py:118-119) is ADJACENT to file_under_root, not a duplicate: its path comes only from git diff --name-only --diff-filter=ACMR (diff.py:56), is repo-relative by construction, and is never registry- or host-supplied, so file_under_root's containment job does not apply.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:118-119`
- **C91** [shape_fit]: The not-found refusals of file_under_root's callers (load_mandates, load_host_detector, scan_ratchet) are ADJACENT to acf.loader.require_file (loader.py:24-28): require_file takes an already-built Path for an operator input file and always raises AcfInputError, while these callers first decide containment of a registry-supplied string and raise their phase's error (UnknownDetectorError at load, DetectorPackError in the ratchet).
  - spec citation: `plugins/arch-compliance/python/acf/loader.py:24-28`
- **C92** [shape_fit]: load_baseline beside load_model_file is ADJACENT by an approved decision (ADR_GATE_HOST_CONTRACT.md:292-294 records it as a pre-existing second loader outside this phase), and the design changes only how the baseline path is resolved and contained; scan_host_guards' errors='replace' line read is ADJACENT to the gates' strict reads of the code files they parse, because its lines serve only the exemption-token lookup and a guard may flag a binary or a document.
  - spec citation: `docs/design/ADR_GATE_HOST_CONTRACT.md:292-294`
- **C93** [shape_fit] [load-bearing]: The loader keeps one record of loaded host modules, sys.modules under a name that is a pure function of rel_path; no second cache keyed by rel_path exists in the design, and the fresh_host_loader fixture resets the loader's state by resetting _ACTIVE_ROOT and removing the _acf_host_ entries a test added.
  - spec citation: `None`
- **C94** [sweep] [load-bearing]: Sweep: the call-site vocabulary in use across shipped registries, tests and the origin host is within CallSite {ci, precommit, hook, posttooluse, audit}; after each ast/guard row declaring ci also declares precommit, every active ast/guard row routes to at least one Tier-1 site at which its detector runs, and audit stays read by no Tier-1 gate.
  - spec citation: `None`
- **C95** [sweep] [load-bearing]: Sweep: the test changes in spec §4.7 cover every existing test the design breaks or makes stale, including test_unenforced_mandate_does_not_gate (test_diff_cli.py:102-108, which gains an active no-shims.hasattr row so the empty-selection refusal does not fire), the ten main([...]) calls in test_diff_cli.py (now passing --call-site), the ten apply_registry calls in test_enforcement.py, test_hooks.py:199-218, test_registry.py:30, test_typescript_pack.py:6 and :14, tests/test_self_host.py:23, :40 and :5, test_acf_mandate_skill.py:2 and test_portable_guards.py.
  - spec citation: `None`
- **C96** [sweep]: The §4.7/§4.8 sites cover every shipped doc, skill, docstring, config and test the design makes stale, including each command line or instruction that runs acf-check-diff whether or not it names the tool: the sites the §4.8 recipe prints (.github/workflows/ci.yml:40, README.md:57-58, acf-setup SKILL.md:24, :184, :193, :206, :207, :217, :219, :250 and its success criteria, acf-mandate SKILL.md:131, CLAUDE.md:36, docs/guides/SUPERPOWERS_COMPLEMENT.md:82-83, PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:454), plus the instructions that run the gate without a command line (acf-setup SKILL.md:228, SUPERPOWERS_COMPLEMENT.md:70-71, README.md:112); the upgrade note for previously installed hosts; KNOWN_DETECTORS described as a union; the hook's call-site behaviour; apply_registry's drop rules; and the deleted detector-id sets.
  - spec citation: `None`
- **C97** [sweep]: The §4.8 rows cover the prose this revision makes stale: ARCHITECTURE.md ## Fail-loud ratchet enablement text (:72-73), ARCHITECTURE.md:226-228 naming acf.cli_check_diff.KNOWN_DETECTORS, the acf-mandate SKILL.md:58 partial-row advice and the upgrade note for partial rows, and docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:161 (PostToolUse scans in-repo paths only).
  - spec citation: `None`
- **C98** [mechanism_justification] [load-bearing]: Deferring host import to dispatch (load_mandates checks reference syntax, Tier-1 site, languages, built-in contracts and host-file existence, and imports nothing) is justified: a missing file still fails at load, an import failure or missing callable fails loud at dispatch as UnknownDetectorError caught by both gates' except tuples, and importing at load would run host code in the SubagentStart hook and acf-check-llm and import CI-only guards on every edit.
  - spec citation: `None`
- **C99** [mechanism_justification] [load-bearing]: The row-shape checks on Mandate (host-reference syntax, a Tier-1 site, host ast languages) together with the per-detector BuiltinDetector contracts (known id, matching mandate_id, declared Tier-1 sites within the contract's call_sites) are sufficient to prevent an active ast/guard row that loads with known_detectors yet is run by neither acf-check-diff (DIFF_CALL_SITES) nor the hook (HOOK_CALL_SITES), or whose findings land on no row.
  - spec citation: `None`
- **C100** [mechanism_justification] [load-bearing]: Refusing a second host root in one process (AcfInputError) rather than evicting the old root is justified: every production caller resolves one repository per process, so the refusal never fires in production, and the only multi-root producer (in-process tests) is handled by the test-only fresh_host_loader fixture; no repair mechanism lives in production code.
  - spec citation: `None`
- **C101** [mechanism_justification] [load-bearing]: Declaring, per built-in detector, the mandate id it reports to and the call sites where a gate runs it (BuiltinDetector in KNOWN_DETECTORS) is justified over the alternatives: the scanners stamp fixed mandate ids and run at fixed gates, so the contract records an existing fact rather than adding a capability; the accepted cost (at most one active row per built-in detector) affects no shipped registry.
  - spec citation: `None`
- **C102** [mechanism_justification] [load-bearing]: Moving the row-local rules onto a Mandate model_validator (rather than keeping them in load_mandates) is justified because it makes the SubagentStart hook, acf-check-llm and any direct Mandate construction reject the same malformed rows as the gates; inject_constraints.py catches AcfInputError around load_mandates, and acf-check-llm (cli_check_llm.py:54) leaves it uncaught, so a malformed row there already ends non-zero and the new refusals reach it the same way (spec §3 In scope table).
  - spec citation: `None`
- **C103** [mechanism_justification]: Parsing a Python file once and sharing the tree across every host ast detector on it is justified by avoiding N parses per file; built-in scanners keep their own parses unchanged.
  - spec citation: `None`
- **C104** [mechanism_justification] [load-bearing]: Having host callables return HostHit (path, line, message) and building Finding in the runner from the mandate row, rather than accepting Finding and overwriting fields, is justified because apply_registry matches findings to rows by mandate_id (enforcement.py:37-53) and a host-supplied mandate_id/detector/severity could otherwise attach a finding to the wrong row.
  - spec citation: `None`
- **C105** [mechanism_justification] [load-bearing]: Treating the host's own pre-commit/CI invocation of acf-check-diff as its opt-in to running host code, and gating only the automatic hooks on .acf/enabled, is justified because .acf/ is gitignored and CI would otherwise be disabled; a user who runs acf-check-diff manually in an untrusted checkout is the residual case the design accepts.
  - spec citation: `.gitignore:8`
- **C106** [mechanism_justification] [load-bearing]: The call_sites filter added to apply_registry is needed in addition to the scanners' registry.active(call_sites) selection, because some built-in scanners emit findings by detector id without consulting the registry's call_sites, so without the filter a finding for a row not declared at this gate would survive. (The spec states the filter but gives no reason it is not redundant.)
  - spec citation: `None`
- **C107** [mechanism_justification] [load-bearing]: Appending the host root to the end of sys.path rather than inserting it at the front is justified: it adds no shadowing of standard-library, third-party or plugin modules under the hook and console-script entry points, keeps host intra-repo absolute imports working from the host root, and its stated cost (a host top-level name an earlier entry provides resolves to that entry) fails at import or callable lookup as UnknownDetectorError in the common case; dropping the acf/ refusal removes a check with no producer.
  - spec citation: `None`
- **C108** [mechanism_justification] [load-bearing]: Reading flagged files in scan_host_guards, inside each gate's scan try, instead of lazily in the line lookup is justified: it keeps apply_registry free of I/O and new errors, converts an unreadable file to DetectorPackError where both gates already report it, and limits new exemption lines to files a host guard flagged.
  - spec citation: `None`
- **C109** [mechanism_justification]: Enforcing llm prompt ids at load (llm_prompt_ids, passed by acf-check-diff) is justified: it gives acf.judge.LLM_PROMPT_IDS a runtime consumer after it leaves KNOWN_DETECTORS, makes the acf-mandate skill's stated rule true, and refuses no shipped row; registry.py cannot import acf.judge, so the ids are passed in rather than imported.
  - spec citation: `None`
- **C110** [mechanism_justification] [load-bearing]: A required --call-site argument on acf-check-diff, rather than a default or a site derived from --mode/--base, is justified: the origin host's per-site row selection (hm:scripts/ci/run_guards.py:116), the fact that a missing value then fails loud (usage error) instead of silently running the wrong rows, and the practice of declaring rather than defaulting, which the spec applies by choice (the ## Declared, never defaulted section governs only the ADR gate's host values); the cost, adding the flag at each existing invocation, is listed per site.
  - spec citation: `None`
- **C111** [mechanism_justification] [load-bearing]: Refusing a --call-site that selects no active ast/guard row (AcfInputError), and adding precommit to every shipped row that declares ci, are justified together: without them the documented pre-commit invocation would run no row and report clean, the false green the origin host's runner already refuses (hm:scripts/ci/run_guards.py:126-130).
  - spec citation: `None`
- **C112** [mechanism_justification] [load-bearing]: Rebuilding each yielded item inside _call_host (exact type, exact field types, then validation) is justified over checking the type in _to_findings: field access and comparisons on an unvalidated host object can run host code, so they must happen inside the wrapped region, and a rebuilt HostHit holds only plain str and int values.
  - spec citation: `None`
- **C113** [mechanism_justification]: Decision 8 (delete the existing definitions §4.9 lists and switch their callers) is justified over recording them as debt: it removes code, removes completeness claims about remaining breaches, and each switch's behaviour change is checked against every shipped value (spec §4.9, Appendix); where an approved spec chose otherwise (AdrHostConfig's path fields, ADR_GATE_HOST_CONTRACT.md:295-301), the design keeps that decision.
  - spec citation: `None`
- **C114** [mechanism_justification] [load-bearing]: _describe (format the host exception inside its own try, fall back to a constant message for any exception but KeyboardInterrupt) is justified by a named producer: an exception carrying an origin-host object whose __str__ raises (hm:scripts/ci/genre_conditional_guard.py:33-40); without it, formatting the typed error's message would raise outside the wrapped region and end in a traceback.
  - spec citation: `None`
- **C115** [implementability] [load-bearing]: Mandate (registry.py:14-27) is a Pydantic BaseModel exposing every field the design reads: id, severity, status, detection, detector, call_sites (list[str]), languages (Literal including 'none'), and params (dict or None); adding an @property is_active and a plain method runs_at to it, and a method active to MandateRegistry, is compatible with its model_config.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:14-27`
- **C116** [implementability] [load-bearing]: Finding (acf/finding.py) can be constructed as Finding(mandate_id=, severity=Severity(mandate.severity), path=, line=, message=, detector=, detection=): those are its fields, Severity is constructible from Mandate.severity's value, and no other required field is missing.
  - spec citation: `None`
- **C117** [implementability] [load-bearing]: apply_registry (enforcement.py) looks up each finding's row via registry.by_id, drops it on the status check at :47 (replaceable by runs_at), and handles exemptions and severity at :49-52 using a LineLookup type that make_line_lookup can return.
  - spec citation: `plugins/arch-compliance/python/acf/enforcement.py:47`
- **C118** [implementability] [load-bearing]: cli_check_diff.py has the hook points the design names with the needed names in scope: load at :70 inside a try whose except tuple at :72 lists AcfInputError, UnknownDetectorError and DetectorPackError (and wraps both load and scan); lookup and apply_registry at :76-82; in the .py branch after scan_fsm_writes (:140-150) repo, text, posix, lines and registry; in the .ts/.tsx branch (:151-156) a read that can bind text; and after the ratchet loop (:168-182) the changed-file list.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:72`
- **C119** [implementability] [load-bearing]: posttooluse_gate.py has the hook points the design names: deferred imports at :91-104, the load try at :106-110, the scan try at :113-117 (whose except can be widened to AcfInputError, DetectorPackError, UnknownDetectorError), lookup/apply_registry at :119-125, _collect_paths' resolve-and-dedupe loop at :200-209 where file_under_root replaces the join, the is_file skip at :239 and the relative_to/ValueError fallback at :242-245 that are deleted, inline filters at :229-236 and :284-286, the build-artifact loop at :284-294, and text and rel in scope in the .py and TypeScript branches of _scan_paths.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:113-117`
- **C120** [implementability] [load-bearing]: Host-detector failures reach an existing fail-loud handler in both gates, never a traceback: load_host_detector raises UnknownDetectorError for any exception but KeyboardInterrupt during import or lookup and for a stat OSError, AcfInputError for a second root; _call_host raises DetectorPackError for any exception but KeyboardInterrupt from the call, from consuming the result and from rebuilding each item; scan_host_guards raises DetectorPackError for a stat or read OSError; apply_registry does no I/O; cli_check_diff.py:72 and the hook's widened scan except catch all three error types.
  - spec citation: `None`
- **C121** [implementability] [load-bearing]: load_host_detector is implementable as stated: a module-level _ACTIVE_ROOT, sys.modules under a name derived from rel_path as the one record of a loaded module, a one-time sys.path.append of the root, file_under_root for the module path, spec_from_file_location with a None spec or loader refused inside the wrapped region, registering in sys.modules before exec_module and removing the entry when this call registered it and the load or lookup raises, and exec plus getattr in one try; the fresh_host_loader fixture, which resets _ACTIVE_ROOT and deletes the _acf_host_ sys.modules keys a test added, isolates in-process tests over several roots, including test_diff_cli.py's in-process main() calls.
  - spec citation: `None`
- **C122** [implementability] [load-bearing]: Registering the module in sys.modules under its name before spec.loader.exec_module(mod) is what lets a host module define a @dataclass under `from __future__ import annotations` (dataclasses resolves sys.modules[cls.__module__]); importlib.util.spec_from_file_location with a synthetic name supports this.
  - spec citation: `None`
- **C123** [implementability] [load-bearing]: The imports the design adds are cycle-free and allowed: acf.registry imports acf.engine, dataclass and Mapping, and nothing from acf.detectors; acf.detectors/__init__ imports acf.registry (BuiltinDetector, call-site sets) and the scanner modules' constants without a cycle; acf.cli_check_diff re-exports KNOWN_DETECTORS from acf.detectors; acf.detectors.host imports registry, finding, engine and exceptions; acf/adr/citations.py importing acf.engine is permitted by test_adr_import_graph.py; and the hook's new deferred imports (from acf.detectors, not acf.cli_check_diff) do not reach acf.adr or acf.judge.
  - spec citation: `plugins/arch-compliance/tests/test_adr_import_graph.py:70-76`
- **C124** [implementability] [load-bearing]: load_mandates today loads rows via load_model_file(path, Mandate, subject='mandates file', fmt='yaml', many=True) returning a list of Mandate, and builds MandateRegistry(mandates=..., source_path=path.as_posix()), so the §4.2 body is a drop-in extension of the existing function.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:48-64`
- **C125** [implementability]: plugins/arch-compliance/tests/test_repo_paths.py:47-48 pins the text of posttooluse_gate.py's docstring line :11 and not :12, so rewording :12 and keeping :11 verbatim breaks no test.
  - spec citation: `plugins/arch-compliance/tests/test_repo_paths.py:47-48`
- **C126** [implementability]: config/architecture/mandates.yml:60 declares fail-loud.bare-except-ok for fail-loud.bare-except; the design's handlers are `except BaseException` handlers, which _is_bare_or_exception (python_pack.py:78-82) does not flag because it matches only a bare handler or the name Exception, so they pass the gate whether or not they carry the token, and spec §6 says so.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/python_pack.py:78-82`
- **C127** [implementability]: acf/engine.py already defines contains_backslash and is stdlib-only, so adding looks_absolute, resolve_under_root and validate_posix_rel_path with `import re` and `from pathlib import Path` keeps it stdlib-only and gives validate_posix_rel_path its backslash test without a new dependency.
  - spec citation: `plugins/arch-compliance/python/acf/engine.py`
- **C128** [implementability] [load-bearing]: The new tests are implementable against the shipped files: test_builtin_detectors.py can parse the README.md detector table (:66-74) for detector ids and mandate ids and read mandate_id values from emptyCatch.ts:23 and explicitAny.ts:15; and the test_registry.py cases (a fail_loud_ratchet row declaring hook, a fail_loud_bare_except row with another id, an ast row naming an LLM prompt id, a module that raises at import not imported by load_mandates) can be expressed as inline YAML registries like the existing :24 and :35 rows.
  - spec citation: `None`
- **C129** [implementability] [load-bearing]: The contract-against-dispatch test is implementable: acf-check-diff runs in process on a temporary git repository once with --call-site ci and once with --call-site precommit, and the hook in a subprocess with .acf/enabled; a fixture tree can trigger each built-in detector the table assigns to that gate, with one active row per such detector declaring only that gate's sites.
  - spec citation: `None`
- **C130** [implementability] [load-bearing]: scan_host_guards(repo_root, changed_files, registry, file_lines, *, call_sites) is implementable in both gates: file_lines is in scope after each gate's dispatch (cli_check_diff _scan_changed returns it; _scan_paths builds it), the call can run inside _scan_changed and _scan_paths so it sits under each gate's scan try, and filling only missing keys keeps the gate's own reads.
  - spec citation: `None`
- **C131** [implementability] [load-bearing]: The required --call-site argument is implementable at cli_check_diff.py:29-71: argparse required=True with choices=sorted(DIFF_CALL_SITES) exits 2 on a missing or unknown value (SystemExit in process, so test_diff_cli asserts it with pytest.raises), sites = frozenset({args.call_site}) reaches _scan_changed and apply_registry, and the empty-selection refusal can raise AcfInputError inside the existing try at :69-74.
  - spec citation: `None`
