# Adversarial design review — full detail

Spec: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md` @ `42087f730b571fc5158a4eecdeb560b8afbf9cb2`
Kinds: defect, feature
Outcome: **BLOCKED**
Claims: 122 · Reviewers: 4 · Converged: 0

## Blocking reasons

- load-bearing claim C29 (premise) is REFUTED: The getattr fact holds: getattr with a default swallows only AttributeError. The sys.modules behaviour follows from the `_MODULE_CACHE.get(rel_path) is not mod` test, and cli_check_diff.py:72 catches UnknownDetectorError. But the claim says the shared try catches (Exception, SystemExit). Spec §4.4 item 3 actually catches BaseException and re-raises only KeyboardInterrupt, as does §6.1 ('any exception but KeyboardInterrupt'). The claim misstates the mechanism it describes, though the spec's actual handler is broader and still covers the case.
- load-bearing claim C55 (mandate) is REFUTED: Most of the claim holds. The parser's required=True gives exit 2. The TS bridge's existing except (KeyError, TypeError, ValueError) at typescript_bridge.py:94-95 wraps the new lookup and comparison. Stat OSErrors become UnknownDetectorError at load and DetectorPackError in scan_host_guards, and both sit inside each gate's try. The last sentence is false about the design, though: 'Every broad handler re-raises a typed error or KeyboardInterrupt.' The spec's own §4.4 item 4 defines a third `except BaseException` handler, `_describe`. Apart from KeyboardInterrupt, it returns the string 'host exception (message unavailable)' and re-raises nothing. That includes a SystemExit raised by a host __str__. §6 itself miscounts as well ('The two broad handlers (§4.4 items 3 and 4)'). The doctrine allows a broad handler that swallows only when it is 'explicitly exempted with a reason' (ARCHITECTURE.md:29-30). `_describe` carries the fail-loud.bare-except-ok token with a reason, so the design itself complies, and an `except BaseException` is not matched by the shipped detector anyway (python_pack.py:77-82). The fix is to reword the claim, not to change the mechanism. As written, though, the load-bearing universal is false.
- load-bearing claim C73 (shape_fit) is REFUTED: The parse_python half holds: ast.parse plus SyntaxError appears only at facade_sinks.py:51, fail_loud_ratchet.py:24, fsm_guard.py:37 and python_pack.py:35. The file_under_root half also holds for registry-supplied paths. The first conjunct fails. After the design, the hook still makes its own 'is this path string absolute' test, `Path(raw).is_absolute()` on the raw harness string at posttooluse_gate.py:203-204. It also keeps its own 'is it under the root' test, `abs_path.relative_to(repo)` with try/except ValueError at :242-245, and that test now decides which paths reach host code. §4.1 excludes :204 as 'Path.is_absolute() on a path resolved for I/O'. But at :203 `p = Path(raw)` is unresolved harness input; is_absolute decides how it gets resolved. That is exactly the 'whether a path string is absolute' job §4.1 gives acf.engine. So the string tests do not have one definition after the design.
- load-bearing claim C81 (shape_fit) is REFUTED: The hook does not start from 'an already-resolved absolute Path'. It starts from a raw harness string, `p = Path(raw)` at :203. It branches on is_absolute, joins with repo, resolves (:204), and then makes a containment decision with relative_to at :242-245. That pipeline (string, then resolved path, then 'inside root?') is what resolve_under_root does (`(base / rel).resolve()` then is_relative_to; base / an absolute path yields that path). The shared responsibility R is 'is this resolved path contained in the repo root'. It is implemented by is_relative_to in resolve_under_root (today citations.py:76) and by relative_to plus ValueError in the hook, and after the design the hook's version gates host dispatch. The spec's own §4.9 confirms the overlap at the ratchet site: it deletes the walk filter's `except ValueError: continue` (fail_loud_ratchet.py:59-62) because resolve_under_root's containment makes that branch unable to fire. That makes the branch the same job, not the opposite operation. The relative-string conversion (relative_to(...).as_posix()) is the only part that is the opposite direction.
- load-bearing claim C122 (implementability) is SURVIVED but its evidence ('plugins/arch-compliance/python/acf/cli_check_diff.py:29-74') merely restates the spec's own citation ('plugins/arch-compliance/python/acf/cli_check_diff.py:29-61') — not independent verification, treated as UNPROVEN
- mandate claim C55 is REFUTED: Most of the claim holds. The parser's required=True gives exit 2. The TS bridge's existing except (KeyError, TypeError, ValueError) at typescript_bridge.py:94-95 wraps the new lookup and comparison. Stat OSErrors become UnknownDetectorError at load and DetectorPackError in scan_host_guards, and both sit inside each gate's try. The last sentence is false about the design, though: 'Every broad handler re-raises a typed error or KeyboardInterrupt.' The spec's own §4.4 item 4 defines a third `except BaseException` handler, `_describe`. Apart from KeyboardInterrupt, it returns the string 'host exception (message unavailable)' and re-raises nothing. That includes a SystemExit raised by a host __str__. §6 itself miscounts as well ('The two broad handlers (§4.4 items 3 and 4)'). The doctrine allows a broad handler that swallows only when it is 'explicitly exempted with a reason' (ARCHITECTURE.md:29-30). `_describe` carries the fail-loud.bare-except-ok token with a reason, so the design itself complies, and an `except BaseException` is not matched by the shipped detector anyway (python_pack.py:77-82). The fix is to reword the claim, not to change the mechanism. As written, though, the load-bearing universal is false.

## Absorptions

- PARTIAL_OVERLAP: 'acf.engine.resolve_under_root' shares responsibility 'decide whether a resolved path lies inside the repository root' with plugins/arch-compliance/hooks/posttooluse_gate.py:242-245 — R = containment of a resolved path in the root. The hook's _collect_paths is_absolute/join/resolve (:203-204) plus relative_to/ValueError (:242-245) should call resolve_under_root(repo, raw) for the in-repo decision and keep only relative_to(...).as_posix() for the key string. resolve_under_root stays the single containment predicate.
- PARTIAL_OVERLAP: 'acf.engine.looks_absolute' shares responsibility 'decide whether a path string is absolute' with plugins/arch-compliance/hooks/posttooluse_gate.py:204 — R = absolute-string classification of untrusted path input. Folding the hook's Path.is_absolute branch into resolve_under_root (which handles absolute input by joining) removes the second, platform-dependent definition.
- BOUNDARY_CUT: 'acf.engine.resolve_under_root' shares responsibility 'keep walked paths inside the root' with plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:59-62 — The walk filter's except ValueError becomes dead once roots are contained (§4.9 deletes it). Restate §4.1/§5.2: the containment part moves to resolve_under_root; only the relative-string conversion stays.
- PARTIAL_OVERLAP: "file_under_root callers' 'not found' refusals (load_mandates host file, load_host_detector, scan_ratchet baseline)" shares responsibility 'refuse an absent input file with one message shape' with plugins/arch-compliance/python/acf/loader.py:24-28 — R = refuse-missing-file. Option: a require_file_under_root(root, rel, subject, error) beside require_file, or require_file accepting the file_under_root result. The ratchet's load_baseline existence check (fail_loud_ratchet.py:78) and the host-file checks then share one message shape.
- IDENTICAL: 'acf.engine.parse_python' shares responsibility 'parse Python or skip on SyntaxError' with plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37 — Delete the four scanner copies (python_pack.py:34-37, facade_sinks.py:50-53, fsm_guard.py:36-39, fail_loud_ratchet.py:23-26) and consume parse_python, as the spec states.
- SUBSUMED: 'acf.engine.looks_absolute / resolve_under_root' shares responsibility 'repo-relative path tests' with plugins/arch-compliance/python/acf/adr/citations.py:49-51 — Delete citations._looks_absolute/_escapes_repo; citations.py:161/:163 consume the engine helpers, as the spec states.
- mechanism 'TS_MANDATE_IDS stamp-and-compare in typescript_bridge' sits at rung 3 when rung 1 applies, with no written justification

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:48-64; plugins/arch-compliance/tests/test_registry.py:20-30`
- reasoning: load_mandates skips rows at :58 when status != 'enforced' and raises UnknownDetectorError at :60-63 only when detection is ast/guard and the detector is not in known_detectors. test_registry.py:20-30 pins the enforced unknown-detector case.

#### C2 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:25; plugins/arch-compliance/python/acf/judge.py:29-36; plugins/arch-compliance/python/acf/cli_check_diff.py:94-184`
- reasoning: The recipe `git grep KNOWN_DETECTORS -- plugins tests` shows only imports, uses as an argument, and skill prose; nothing extends the set. Running the recipe gives 13 ids, LLM prompt ids included. No Tier-1 scanner in _scan_changed dispatches on an llm_* id.

#### C3 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; plugins/arch-compliance/hooks/posttooluse_gate.py:229-236; plugins/arch-compliance/hooks/posttooluse_gate.py:284-286`
- reasoning: Both loops call only the imported built-in scanners. scan_python_file and scan_typescript_file run unconditionally, and the configurable scanners are selected by exact built-in id. The importlib/import_module/spec_from_file_location/exec_module git grep over python and hooks printed nothing.

#### C4 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:106-110; plugins/arch-compliance/python/acf/exceptions.py:5; plugins/arch-compliance/python/acf/exceptions.py:13`
- reasoning: The hook wraps load_mandates in `except AcfInputError` only. UnknownDetectorError(AcfError) is a sibling of AcfInputError(AcfError), not a subclass, so it would escape uncaught.

#### C5 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:21; plugins/arch-compliance/python/acf/enforcement.py:47; plugins/arch-compliance/python/acf/adr/ledger.py:83`
- reasoning: The git grep for call_sites over python and hooks prints registry.py:21 and ledger.py:42 and :83 (both surface_call_sites) and nothing else. The gate filters and apply_registry test detector and status only.

#### C6 — SURVIVED
- evidence: `config/architecture/mandates.yml:70; plugins/arch-compliance/tests/fixtures/mandates_valid.yml:18; plugins/arch-compliance/tests/test_hooks.py:199-218; plugins/arch-compliance/hooks/posttooluse_gate.py:254`
- reasoning: The no-shims.hasattr row declares [ci] in the config and in the fixture. The hook runs scan_python_file without reading call_sites, and apply_registry keeps the finding. The test asserts no-shims.hasattr appears in the hook's additionalContext.

#### C7 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_import_graph.py:70-76; plugins/arch-compliance/python/acf/adr/contract.py:20; plugins/arch-compliance/hooks/posttooluse_gate.py:92-95`
- reasoning: The test asserts only that the literal 'acf.adr' is absent from both hook files and states the import-graph intent in its docstring. The hook imports acf.enforcement and acf.registry, and contract.py:20 imports contains_backslash from acf.engine.

#### C8 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:214-230`
- reasoning: run_judge selects rows with detection == 'llm' (:214) and uses status == 'enforced' only for has_enforced in provider resolution (:218, :224). It reviews every llm row (:230) and has no unenforced or call-site filter.

#### C9 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:28; plugins/arch-compliance/hooks/posttooluse_gate.py:72-81; plugins/arch-compliance/hooks/posttooluse_gate.py:91-107; plugins/arch-compliance/tests/test_repo_paths.py:80-106`
- reasoning: acf.repo is the only module-scope acf import. The marker check returns 0 before the deferred imports and before load_mandates. test_repo_paths pins the marker-less exit 0 with pydantic and yaml poisoned.

#### C10 — SURVIVED
- evidence: `.gitignore:8; .github/workflows/ci.yml:40; plugins/arch-compliance/python/acf/cli_check_diff.py:22`
- reasoning: .acf/ is ignored and `git ls-files .acf` prints nothing. CI runs python -m acf.cli_check_diff. cli_check_diff imports only MANDATES_REL, RATCHET_BASELINE_REL and resolve_repo from acf.repo, not ENABLED_REL, so it never checks the marker.

#### C11 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:103-107; plugins/arch-compliance/python/acf/loader.py:70-73; plugins/arch-compliance/python/acf/cli_check_llm.py:54`
- reasoning: inject_constraints catches AcfInputError around load_mandates. Field ValidationErrors become AcfInputError in the loader. cli_check_llm leaves the call uncaught, so any AcfInputError already exits non-zero there.

#### C12 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:93-110; plugins/arch-compliance/python/acf/cli_check_llm.py:10-13; plugins/arch-compliance/python/acf/cli_check_llm.py:54-66`
- reasoning: Both entry points import only acf.exceptions, acf.registry, acf.judge, acf.repo and acf.loader, then call load_mandates and render or judge. Neither imports acf.detectors. In spec §4.2, load_mandates does only file_under_root (a stat) for host rows, so no path reaches load_host_detector.

#### C13 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/baseline.py:1`
- reasoning: No subpackage named 'review' exists, so the recipe prints nothing. But architecture-review runtime code does exist at a338cad: acf/baseline.py's docstring reads 'Compliance baseline + report-only drift for architecture-review'. The recipe misses it because it greps paths for 'review'. Not load-bearing, and this design touches neither.

#### C14 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:20; plugins/arch-compliance/python/acf/registry.py:24; hm:config/architecture/mandates.yml:5-14`
- reasoning: `git show b652fab05:config/architecture/mandates.yml | grep -c 'languages|arch_anchor'` prints 0. Its rows carry gemini_anchor and no languages, while Mandate requires both fields.

#### C15 — SURVIVED
- evidence: `hm:scripts/ci/arch_compliance/driver.py:150-162; hm:scripts/ci/arch_compliance/driver.py:141-146`
- reasoning: The driver catches SyntaxError per changed file. It raises in range mode and otherwise appends a WARN Finding at exc.lineno or 0. It reads cf.content from diff.changed_files(mode,...), so its results depend on diff mode. The spec states these gaps and leaves them to cutover.

#### C16 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:198-200; plugins/arch-compliance/python/acf/cli_check_diff.py:115-156; plugins/arch-compliance/hooks/posttooluse_gate.py:238-282`
- reasoning: The doctrine quote matches. The loops differ in diff scope (added_lines versus None) and in path source (git changed_files versus the payload, with an absolute fallback for out-of-repo paths). The file-suffix filter is the same in both gates. Advisory: under the design, the mapping from suffix to host language is restated in each gate.

#### C17 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:50-53; plugins/arch-compliance/python/acf/detectors/fsm_guard.py:36-39; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:23-26`
- reasoning: Each wraps ast.parse(text) in try/except SyntaxError and returns [] (0 in the ratchet).

#### C18 — SURVIVED
- evidence: `plugins/arch-compliance/skills/architecture-review/SKILL.md:62; plugins/arch-compliance/tests/test_registry.py:30; tests/test_self_host.py:23`
- reasoning: Ran the `git grep load_mandates(` recipe; it prints exactly the listed sites. known_detectors is passed only at cli_check_diff.py:70, acf-mandate SKILL.md:95, test_profile_drift.py:24, test_registry.py:30 and test_self_host.py:23.

#### C19 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:125; plugins/arch-compliance/python/acf/cli_check_diff.py:82; plugins/arch-compliance/tests/test_enforcement.py:54`
- reasoning: Ran the recipe; it prints exactly these plus the ten test_enforcement lines. Non-.py hits are prose only (acf-mandate SKILL.md:51).

#### C20 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; plugins/arch-compliance/hooks/posttooluse_gate.py:231; plugins/arch-compliance/python/acf/enforcement.py:47; plugins/arch-compliance/hooks/inject_constraints.py:158`
- reasoning: Both recipes reproduce the stated output exactly. The wider .status recipe adds only registry.py:58, judge.py:218 and the display at inject_constraints.py:158.

#### C21 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/build_artifacts.py:31; plugins/arch-compliance/python/acf/detectors/python_pack.py:97; plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23; plugins/arch-compliance/python/acf/enforcement.py:46`
- reasoning: Each detector stamps one literal mandate_id (python_pack has three detectors, each with its own). apply_registry looks findings up with by_id.get(finding.mandate_id).

#### C22 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:168-182; plugins/arch-compliance/hooks/posttooluse_gate.py:213-295`
- reasoning: Only cli_check_diff imports and calls scan_ratchet. The hook calls scan_python_file (:254), the facade and fsm scanners (:255-277), scan_typescript_file (:279-282) and the build-artifact scanner (:284-294), matching the §4.3 table.

#### C23 — SURVIVED
- evidence: `config/architecture/mandates.yml:70; plugins/arch-compliance/tests/test_diff_cli.py:71-81; plugins/arch-compliance/tests/test_registry.py:22-30; plugins/arch-compliance/tests/test_hooks.py:220-226`
- reasoning: Census run over every shipped and fixture YAML. Every active ast/guard row has a built-in detector, its id equals the stamped mandate id, and its call_sites are subsets of {ci,hook}. Facade, FSM and ratchet rows are unenforced. Inline rows: bare-except [ci,hook] passes, not_a_real_detector raises UnknownDetectorError, manual and llm rows are skipped. test_hooks edits only status to unenforced, and test_acf_mandate_skill copies profile rows.

#### C24 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/loader.py:70-73; plugins/arch-compliance/python/acf/registry.py:33-41; plugins/arch-compliance/tests/test_enforcement.py:19-30`
- reasoning: With pydantic 2.13.3, ran a model_validator raising a non-ValueError exception: it propagates with its own type through model_validate and through direct construction. The loader catches only ValidationError. The direct constructions are an ast row with call_sites [ci] and two llm rows, none refused by _row_shape.

#### C25 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:91-112; plugins/arch-compliance/tests/test_profile_drift.py:7; tests/test_self_host.py:14; config/architecture/ARCHITECTURE.md:228`
- reasoning: Each user imports the name, passes it to load_mandates, sorts it, or names it in prose. All of these work on a Mapping (sorted() yields its keys). test_registry.py:30 passes a frozenset, which would have no .get, and the spec lists it as changing.

#### C26 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:63; plugins/arch-compliance/hooks/posttooluse_gate.py:65; plugins/arch-compliance/hooks/hooks.json:20-25`
- reasoning: Each entry point resolves the repository once. The hook is a separate python command per PostToolUse event. In-process main() calls over several repos occur only in test_diff_cli.

#### C27 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:25; plugins/arch-compliance/python/acf/detectors/python_pack.py:16-22`
- reasoning: Ran the import: len 13, of which 4 are llm_* ids, leaving 9 Python and TypeScript ids.

#### C28 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:29-36; config/architecture/mandates.yml:136; plugins/arch-compliance/profiles/react-app/mandates.yml:40`
- reasoning: Every llm row (config :45 and :136, python-service :95, react-app :40, test_judge.py:390) names llm_react_boundaries or llm_fail_loud, both in LLM_PROMPT_IDS. The fixture and test_diff_cli inline rows have no llm row.

#### C29 — REFUTED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:355-367`
- reasoning: The getattr fact holds: getattr with a default swallows only AttributeError. The sys.modules behaviour follows from the `_MODULE_CACHE.get(rel_path) is not mod` test, and cli_check_diff.py:72 catches UnknownDetectorError. But the claim says the shared try catches (Exception, SystemExit). Spec §4.4 item 3 actually catches BaseException and re-raises only KeyboardInterrupt, as does §6.1 ('any exception but KeyboardInterrupt'). The claim misstates the mechanism it describes, though the spec's actual handler is broader and still covers the case.

#### C30 — SURVIVED
- evidence: `pyproject.toml:5; C:/Python313/Lib/pathlib/_local.py:664-670`
- reasoning: requires-python is >=3.11. In 3.13, non-strict resolve is os.path.realpath, which does not raise on a loop. In 3.11 and 3.12, pathlib's resolve calls p.stat() after realpath and maps ELOOP (and Windows error 1921) to RuntimeError. Catching RuntimeError and returning None feeds each stated None branch.

#### C31 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:82-95; plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23; plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15`
- reasoning: Finding construction sits in a try whose except (KeyError, TypeError, ValueError) re-raises DetectorPackError. The Node literals are fail-loud.empty-catch and no-shims.explicit-any, emitted with detectors empty_catch (emptyCatch.ts:28) and explicit_any (explicitAny.ts:22).

#### C32 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:22-28; pyproject.toml:19-20; .github/workflows/ci.yml:40; hm:scripts/ci/metadata_facade_guard.py:66`
- reasoning: The hook inserts the plugin's python/ at the front when absent and imports acf.repo next. The console script's sys.path[0] is its scripts directory. With -m, the working directory goes first. HM line 66 is `from scripts.ci.arch_compliance.facade_sinks import (`, and hm:scripts/__init__.py exists.

#### C33 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:29-61; hm:scripts/ci/run_guards.py:107-111; hm:scripts/ci/run_guards.py:116; hm:scripts/ci/run_guards.py:126-130; hm:scripts/ci/run_guards.py:317-321`
- reasoning: The argparse options are only --mode, --base, --repo, --mandates and --json. run_guards refuses an unknown site, filters with `site not in entry.call_sites`, refuses an empty selection, and defaults --site to 'ci'.

#### C34 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:126; plugins/arch-compliance/python/acf/cli_check_diff.py:152; plugins/arch-compliance/hooks/posttooluse_gate.py:248-252; plugins/arch-compliance/python/acf/detectors/build_artifacts.py:27-34`
- reasoning: file_lines is populated only in the .py and .ts/.tsx branches. A staged dist/x.py is read into file_lines['dist/x.py'], and lstrip('./') leaves that path unchanged, so its line-1 build-artifact finding matches the key.

#### C35 — SURVIVED
- evidence: `config/architecture/mandates.yml:70; plugins/arch-compliance/profiles/python-service/mandates.yml:18; plugins/arch-compliance/tests/fixtures/mandates_valid.yml:18`
- reasoning: `git grep precommit -- '*.yml'` prints nothing. The census counts 9, 7, 3 and 3 ast/guard rows declaring ci. Every active ast/guard row declares ci, so adding precommit reproduces today's acf-check-diff selection, which ignores call_sites.

#### C36 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:389-397`
- reasoning: Under pydantic 2.13.3, a model like HostHit built from a str subclass and an IntEnum stores exact str and int in __dict__, so genuine hits pass the exact-type check. model_construct stores raw values in __dict__ (extras dropped under extra=forbid). type(True) is not int, so bools are refused. _to_findings then reads only rebuilt plain values.

#### C37 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:138-141; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:273-283; C:/Python313/Lib/pathlib/_abc.py:31-40`
- reasoning: Path.is_file ignores ENOENT, ENOTDIR, EBADF, ELOOP and the Windows ignorable codes, and re-raises other OSError (verified in the 3.13 source). In spec §4.2, §4.4 item 3, §4.4 item 7 and §4.9, each caller converts OSError to its typed error.

#### C38 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/host.py:24-25; docs/design/ADR_GATE_HOST_CONTRACT.md:295-301`
- reasoning: Both fields are PosixStr with min_length=1. The approved contract declines the absolute and '..' refusal ('That is a visible host choice...'). The spec's only mention (§5.2) keeps them unchanged.

#### C39 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:122-125; plugins/arch-compliance/tests/test_portable_guards.py:107; config/architecture/mandates.yml:92; plugins/arch-compliance/python/acf/cli_check_diff.py:72`
- reasoning: Joining an absolute path inside the root replaces the base, and the result is_relative_to the root, so it is accepted; escapes are refused. The shipped baseline is relative, roots ['.'] resolves to the root itself, RATCHET_BASELINE_REL (repo.py:26) is relative, and the test passes roots=['pkg']. DetectorPackError is in the :72 except tuple.

#### C40 — SURVIVED
- evidence: `hm:scripts/ci/genre_conditional_guard.py:32-40`
- reasoning: @dataclass Finding is not frozen, and its __str__ calls self.line_text.strip(). Ran str(ValueError(F(None))) on an equivalent dataclass: it raises AttributeError ('NoneType' object has no attribute 'strip').

#### C41 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:377-381`
- reasoning: items = list(raw) runs inside the try before the _revalidate comprehension. A generator is exhausted (its finally runs) or raises inside the try, so none is left suspended when _revalidate refuses an item.

#### C42 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_diff_cli.py:102-108; plugins/arch-compliance/tests/test_diff_cli.py:84-90; plugins/arch-compliance/tests/test_diff_cli.py:185-193`
- reasoning: Every other main() test uses the fixture copy (active rows) or the active bare-except row, or fails before the refusal (missing mandates). bad.py contains no hasattr, so an added [ci] hasattr row yields no finding and the exit stays 0.

#### C43 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:47; plugins/arch-compliance/python/acf/registry.py:58; plugins/arch-compliance/python/acf/cli_check_diff.py:98`
- reasoning: Partial rows pass the gate filters and apply_registry. load_mandates skips them at :58, so a partial ast/guard row with an unknown detector loads, and no scanner dispatches on it.

#### C44 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:107; plugins/arch-compliance/hooks/posttooluse_gate.py:229-294`
- reasoning: No known_detectors is passed, and _scan_paths dispatches only built-in ids, so a row with an unknown detector silently produces nothing.

#### C45 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80; plugins/arch-compliance/hooks/posttooluse_gate.py:119-123; plugins/arch-compliance/python/acf/enforcement.py:49-50`
- reasoning: The two closures are textually identical and read only file_lines, which holds code files only. apply_registry passes the looked-up line to token_exempted, so a finding on an unread file gets ''.

#### C46 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/citations.py:49-51; plugins/arch-compliance/python/acf/adr/citations.py:74-76; plugins/arch-compliance/python/acf/adr/citations.py:161-163`
- reasoning: The git grep shows only the definitions and these two call sites, and no test references either name. The old regex requires [\\/] after 'X:'; the new one does not, so only drive-relative strings change. The escape tests are equivalent except RuntimeError mapping to None. No test_adr_citations case uses a drive-relative string.

#### C47 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; config/architecture/mandates.yml:70; plugins/arch-compliance/profiles/react-app/mandates.yml:7-29`
- reasoning: The census shows every active ast/guard row in every shipped registry declares [ci,hook], except no-shims.hasattr ([ci]) in the config, the python-service profile and the fixture. Facade, FSM and ratchet rows are unenforced, so hasattr leaving the hook is the only selection change.

#### C48 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:60; plugins/arch-compliance/python/acf/cli_check_diff.py:21`
- reasoning: known_detectors is consulted only under detection in {ast,guard}. The git grep shows LLM_PROMPT_IDS consumed at runtime only at cli_check_diff.py:21/25, plus tests and prose.

#### C49 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:67; plugins/arch-compliance/tests/test_repo_paths.py:53-71; plugins/arch-compliance/tests/test_portable_guards.py:107`
- reasoning: The constants hold the same strings. The only test reading plugin source text (test_repo_paths) looks for config/architecture spellings, which mandate-id constants do not contain. No test reads scanner source otherwise.

#### C50 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80; plugins/arch-compliance/hooks/posttooluse_gate.py:119-123`
- reasoning: The proposed make_line_lookup body (spec §4.5) is token-identical to both closures and performs no I/O. file_lines gains entries only from scan_host_guards.

#### C51 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/__init__.py:11-34; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:14; plugins/arch-compliance/tests/test_typescript_pack.py:6`
- reasoning: The recipe output matches the spec's list exactly. Caveat: the new TS_MANDATE_IDS keys repeat the two TypeScript ids, but KNOWN_DETECTORS is keyed from them and the spec records the bridge as a checked echo.

#### C52 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/facade_sinks.py:24-25; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:46; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:88-90; plugins/arch-compliance/python/acf/detectors/build_artifacts.py:16-23`
- reasoning: The scanners use the optional values only as `x or []`, as truthiness, or by iteration. So passing a raw value gives the same result as the gates' list(...) and bool(...) coercions. The absent-key defaults match: [] versus None (both mean no globs), True, and None prefixes.

#### C53 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:23-26; plugins/arch-compliance/python/acf/detectors/fsm_guard.py:36-39`
- reasoning: The git grep for ast.parse and SyntaxError over python and hooks finds only the four scanner sites.

#### C54 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:45-62; plugins/arch-compliance/tests/test_portable_guards.py:107`
- reasoning: rglob yields paths that start lexically with the search directory. A search directory that resolve_under_root contains is lexically under root = repo_root.resolve(), so relative_to cannot fail. scan_tree's only callers are scan_ratchet (:126) and the test.

### Unanchored findings

- **important**: Hosts that followed the acf-mandate skill's advice to use status: partial for a detector or prompt that does not exist yet will be refused at load by both Tier-1 gates (UnknownDetectorError), and acf-check-diff will refuse such llm rows. This migration consequence is not among the spec's 'Consequence, accepted' items or its upgrade notes.
  - evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:58`
- **advisory**: Architecture-review runtime code already exists at acf/baseline.py, so the non-goal's recipe (`git ls-files ... | grep -i review`) does not establish that no architecture-review runtime exists.
  - evidence: `plugins/arch-compliance/python/acf/baseline.py:1`
- **advisory**: Half of the approved ADR-contract rationale for not refusing absolute or '..' runs_dir/ledger_path values no longer holds once the repo-relative test moves to acf.engine as a shared helper: a refusal would no longer be 'a second implementation'. Only the 'visible host choice' half remains.
  - evidence: `docs/design/ADR_GATE_HOST_CONTRACT.md:301-303`

### Looked for but did not find

- any shipped, fixture or test-written registry row whose detector contains ':' (none; only manual rows carry paths)
- an active fail_loud_ratchet row declaring hook in any shipped registry (all ratchet rows are unenforced, [ci])
- a test that reads scanner source text in a way mandate-id constants would break
- a non-test production caller that runs acf-check-diff main() in-process over more than one repository
- a call_sites value outside {ci, hook, audit} in any tracked YAML or inline test registry
- a tracked .acf/enabled file

## compliance

### Claim verdicts

#### C55 — REFUTED
- evidence: `config/architecture/ARCHITECTURE.md:29-30; plugins/arch-compliance/python/acf/detectors/python_pack.py:77-82`
- reasoning: Most of the claim holds. The parser's required=True gives exit 2. The TS bridge's existing except (KeyError, TypeError, ValueError) at typescript_bridge.py:94-95 wraps the new lookup and comparison. Stat OSErrors become UnknownDetectorError at load and DetectorPackError in scan_host_guards, and both sit inside each gate's try. The last sentence is false about the design, though: 'Every broad handler re-raises a typed error or KeyboardInterrupt.' The spec's own §4.4 item 4 defines a third `except BaseException` handler, `_describe`. Apart from KeyboardInterrupt, it returns the string 'host exception (message unavailable)' and re-raises nothing. That includes a SystemExit raised by a host __str__. §6 itself miscounts as well ('The two broad handlers (§4.4 items 3 and 4)'). The doctrine allows a broad handler that swallows only when it is 'explicitly exempted with a reason' (ARCHITECTURE.md:29-30). `_describe` carries the fail-loud.bare-except-ok token with a reason, so the design itself complies, and an `except BaseException` is not matched by the shipped detector anyway (python_pack.py:77-82). The fix is to reword the claim, not to change the mechanism. As written, though, the load-bearing universal is false.

#### C56 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:56-63; plugins/arch-compliance/python/acf/enforcement.py:46; plugins/arch-compliance/python/acf/cli_check_diff.py:168-182`
- reasoning: Today load_mandates checks only enforced rows against a union that includes LLM ids (registry.py:56-63), and apply_registry matches by the stamped mandate_id (enforcement.py:46). The ratchet is dispatched only by the diff CLI (cli_check_diff.py:168-182). The designed _check_builtin refuses each gap. A detector missing from a map without LLM ids raises UnknownDetectorError. A row id other than contract.mandate_id raises AcfInputError. A Tier-1 site outside contract.call_sites, with the ratchet mapped to DIFF_CALL_SITES, raises AcfInputError. Mandate._row_shape refuses an active ast/guard row with no Tier-1 site for every caller. Unique ids (registry.py:33-41) plus id==mandate_id leave at most one row per built-in. Both gates now pass known_detectors, the hook included. Host rows go through registry.active(call_sites) in both runners. The fail-loud goal holds.

#### C57 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:120-122; plugins/arch-compliance/python/acf/adr/host.py:19-33`
- reasoning: The section requires that 'no default stands in for a missing declaration, and a missing declaration fails loud' (ARCHITECTURE.md:120-122). Its exemplar is AdrHostConfig, whose fields have no defaults (host.py:19-33). The design follows that pattern. With known_detectors, load_mandates raises AcfInputError when repo_root is None for an active host row, and it never derives a root from the mandates path. apply_registry's new call_sites keyword has no default. The new --call-site is also required=True, unlike the origin runner's default site. `repo_root` still defaults to None for callers without known_detectors, but those callers never import host code (Decision 4), so nothing is derived in its place.

#### C58 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:48-49; plugins/arch-compliance/python/acf/detectors/python_pack.py:91`
- reasoning: The doctrine forbids probing 'optional attributes with hasattr to paper over missing interfaces' (ARCHITECTURE.md:48-49). The loader does getattr(mod, attr, None) inside the wrapped region, then `if not callable(fn): raise UnknownDetectorError`. A missing attribute is refused, not papered over, and there is no hasattr call to trip the detector (python_pack.py:91). Each host failure path in §4.4 ends in a typed error. The None-to-[] mappings are fail-safe and keep the finding.

#### C59 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:62-64; plugins/arch-compliance/python/acf/engine.py:17-24`
- reasoning: The doctrine says persisted path fields 'refuse a backslash rather than normalize it' (ARCHITECTURE.md:62-64). validate_posix_rel_path calls contains_backslash (engine.py:17-24) and raises, and HostHit.path applies it through AfterValidator. The resulting Finding.path is what --json serialises. The designed messages render Paths with .as_posix() (repo_root / rel_path, _ACTIVE_ROOT). The other messages interpolate rel_path strings that have already been validated as POSIX.

#### C60 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/exceptions.py:13; plugins/arch-compliance/python/acf/exceptions.py:29; config/architecture/ARCHITECTURE.md:101-102`
- reasoning: AcfInputError (:5), UnknownDetectorError (:13) and DetectorPackError (:29) each subclass AcfError alone, as ARCHITECTURE.md:101-102 requires. The design adds no class. Because none of them carries a ValueError mixin, the AcfInputError raised in Mandate._row_shape propagates unchanged through pydantic and load_model_file, which converts only ValidationError (loader.py:70-73).

#### C61 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:107-110; plugins/arch-compliance/tests/test_repo_paths.py:53-71`
- reasoning: acf.repo is the one declaration of host paths (ARCHITECTURE.md:107-110), and test_repo_paths.py:53-71 flags any config.{0,6}architecture spelling under python/ and hooks/. The designed code for registry.py, engine.py, detectors/__init__.py and host.py and the new runtime messages spell no such path. The hook keeps its pinned docstring line :11 (test_repo_paths.py:47-48). The acf-mandate snippet switches to MANDATES_REL and resolve_repo.

#### C62 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:137-138; plugins/arch-compliance/tests/test_adr_code_portability.py:8`
- reasoning: The rule says 'Skill prose and runtime messages name no host repository, path or section' (ARCHITECTURE.md:137-138). Every message string in §4.2, §4.4 and §4.6 is generic: 'one host root per process', 'selects no active ast or guard mandate', the '<posix_rel_path.py>:<callable_name>' syntax. None matches the origin-host vocabulary (GEMINI, scripts/, HistoricMansions; test_adr_code_portability.py:8). The citations.py edit only imports engine helpers. 'posttooluse' is a call-site value, not a host name.

#### C63 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:155-156; plugins/arch-compliance/python/acf/cli_check_diff.py:21; plugins/arch-compliance/python/acf/judge.py:29`
- reasoning: The rule: 'An export has a live call site in the package, a hook or a skill' (ARCHITECTURE.md:155-156). Each §6.2 export has a package or hook caller in the design. LLM_PROMPT_IDS has no use inside judge.py beyond its definition (:29), so its one runtime consumer stays the cli_check_diff import (:21), now feeding llm_prompt_ids=. A grep for _DETECTOR_IDS outside docs hits only the sites §4.9 deletes and test_typescript_pack.py:6/:14, which §4.7 rewrites. Deleting the five sets leaves no stale import.

#### C64 — UNPROVEN
- evidence: `config/architecture/ARCHITECTURE.md:161-164; plugins/arch-compliance/python/acf/cli_check_diff.py:172`
- reasoning: The doctrine makes 'every'/'only' claims about the tree non-load-bearing without a re-runnable recipe (ARCHITECTURE.md:161-164). Most population claims do carry recipes: §1, the Appendix, the §4.8 --call-site grep (I re-ran it, and the unlisted hits are name mentions such as acf-setup SKILL.md:3 and :182-183 and PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:84, :407 and :630), and the §4.9 rows. Some are not backed that way. §4.3's 'The ratchet's arguments are built at one site only (cli_check_diff.py:168-182)' carries a single citation, not a recipe. It is true by my grep (the only scan_ratchet( call is cli_check_diff.py:172), but it does not meet the stated form. Decision 6's 'Production callers resolve one repository per process' is likewise cited by example. The claim's own universal ('every population claim carries a recipe') cannot be established, and at least one counterexample to its form exists.

#### C65 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:173-174; plugins/arch-compliance/python/acf/cli_check_diff.py:152`
- reasoning: The rule: subprocess text calls declare encoding='utf-8', and 'every file read of prose declares its encoding' (ARCHITECTURE.md:173-174). The TS branch already reads with encoding='utf-8' (cli_check_diff.py:152), and the design only binds that result to `text`. scan_host_guards declares encoding='utf-8', and errors='replace' is outside what the rule governs. Host modules load through importlib, not a text read. No runtime subprocess is added. The new hook subprocess runs only in tests, which the doctrine scopes out.

#### C66 — SURVIVED
- evidence: `pyproject.toml:3; plugins/arch-compliance/.claude-plugin/plugin.json:3; config/architecture/ARCHITECTURE.md:186-187`
- reasoning: The rule: 'A change to a skill's prose bumps the plugin version in plugins/arch-compliance/.claude-plugin/plugin.json and pyproject.toml' (ARCHITECTURE.md:186-187). Both files read 0.2.2 at line 3, and no other non-doc file carries 0.2.2. §4.8 edits the acf-mandate and acf-setup skill prose and bumps both to 0.2.3.

#### C67 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:198-200; plugins/arch-compliance/python/acf/cli_check_diff.py:128-150; plugins/arch-compliance/hooks/posttooluse_gate.py:255-277`
- reasoning: The rule requires 'exactly one canonical implementation that every call site consumes' (ARCHITECTURE.md:198-200). I confirmed the listed duplicates: the identical params extraction (cli_check_diff.py:128-150 vs posttooluse_gate.py:255-277), the identical _line_lookup closures (:76-80 vs :119-123), and the parse-and-skip copies (python_pack.py:34-37, facade_sinks.py:50-53, fsm_guard.py:36-39, fail_loud_ratchet.py:23-26). Each is replaced by one helper. The gates' second definition of optional-param defaults (atomic_is_sink True) is removed, leaving the scanner signature defaults (facade_sinks.py:24-25) as the only ones. The spec explicitly disclaims completeness of §4.9.

#### C68 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:213-214; plugins/arch-compliance/python/acf/cli_check_diff.py:118-119`
- reasoning: The lifted rule: 'remove legacy dependencies or non-contractual patterns in code paths you are changing. Do not expand scope to unrelated modules' (ARCHITECTURE.md:213-214). Each §4.9 deletion sits in a module the design already edits, and is duplicated by a new helper this design needs. cli_check_diff.py:118-119 joins a git-supplied repo-relative name and calls is_file, a different job from containing a registry string, and the spec rightly records it as ADJACENT. The ADR citations change is justified by single point of definition and records its behaviour change (§4.1).

#### C69 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:147-148; plugins/arch-compliance/python/acf/adr/ledger.py:64`
- reasoning: The rule: 'A LedgerRow or LedgerAmendment field changes only through a spec and a gate run' (ARCHITECTURE.md:147-148). The §3 scope table lists no change to acf/adr/ledger.py, whose LedgerRow (:64) and LedgerAmendment (:132) models stay untouched. The only acf.adr file the design touches is citations.py.

#### C70 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:47-50; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:123-125`
- reasoning: The principles are fail loud with typed errors and no silent empty registry/config defaults; one registry façade; POSIX paths; 'Registry is the spine … call sites must agree or tests fail'; and the Superpowers override (:47-51). The design routes on call_sites and refuses contract disagreement at load, which serves principle 4. It adds no parallel mandate list (KNOWN_DETECTORS is a detector contract keyed by detector id). It types every host failure. It gives Python and TypeScript files a host ast extension point (:123, :125), with host guards alongside. One caveat is filed as an advisory finding: the retained silent skip of a missing ratchet root.

#### C71 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:26-34; plugins/arch-compliance/python/acf/enforcement.py:49-50; plugins/arch-compliance/hooks/posttooluse_gate.py:113-117`
- reasoning: apply_registry drops a finding only when token_exempted matches its line (enforcement.py:49-50). That requires a '#'/'//' token with a reason (:26-34), so an empty line list yields '' and the finding is kept. errors='replace' changes only undecodable bytes and cannot fabricate an ASCII token. scan_host_guards runs inside _scan_paths, which sits within the hook's scan try (posttooluse_gate.py:113-117). On the diff side it runs within _scan_changed, inside cli_check_diff.py:69-74. Its DetectorPackError therefore reaches a handler that already lists that type. make_line_lookup is the existing closure body, a dict lookup with no I/O.

### Unanchored findings

- **advisory**: §4.9 rewrites the ratchet's roots resolution but keeps scan_tree's `if not search.exists(): continue`. A misspelled params.roots entry still counts zero bare excepts silently, while an escaping entry is now refused. That leaves a silent empty default for registry config in a code path this design changes (Fail loud; portable principle 1).
  - evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:56-57`

### Looked for but did not find

- ## Build artifacts: the build-artifact guard's dispatch and path stripping (build_artifacts.py:27) are unchanged apart from the params helper and its constant. Not touched in substance.
- ## Façade sinks / ## FSM transitions: only the params extraction moves into facade_sink_args/fsm_guard_args, and the scanners still refuse an empty required param (facade_sinks.py:32-37, fsm_guard.py:29-34). The shipped rows already use the detectors' stamped ids, so the enablement instructions stay valid.
- ## Soft fail-loud smells / ## React boundaries: the Tier-2 judge is unchanged, and the new llm_prompt_ids check accepts both shipped llm detectors (judge.py:29-36).
- ## Post-merge: no change to the host operational declarations.
- ## One base exception: no new exception class. The model_validator's AcfInputError propagates because it carries no ValueError mixin (loader.py:70-73).
- ## Fail loud, narrow None-returning handlers: resolve_under_root (RuntimeError) and parse_python (SyntaxError) return None. Every caller turns that None into a typed error or a fail-safe that keeps the finding, so nothing is swallowed.
- ## Scoped refactor vs the ADR gate: the citations.py edit consumes the shared helpers, discloses both behaviour changes (§4.1), and updates ADR_GATE_HOST_CONTRACT.md:302-303. It is justified by single point of definition, not scope creep.
- ## Release discipline (installed-copy check): the design changes hooks/ and python/, which the byte check does not compare (ARCHITECTURE.md:191-193). That is not a new obligation; the version bump is covered.

### Unstated mandates

- ## Fail-loud ratchet: the design changes the ratchet's routing (the KNOWN_DETECTORS contract is DIFF_CALL_SITES only, so an enabled ratchet row declaring hook is refused at load). It also changes its baseline/roots handling (§4.9: escaping or looping values are refused, and the baseline goes through file_under_root). §6 does not name this section, and §4.8 does not update its enablement instruction ('Enable the mandate and commit a … baseline', ARCHITECTURE.md:72-73) to state those constraints.
- ## High-frequency misses: ARCHITECTURE.md:226-228 names `acf.cli_check_diff.KNOWN_DETECTORS` as the package check to consume. The design moves the definition to `acf.detectors.KNOWN_DETECTORS` and rewrites the acf-mandate prose to name that home (§4.8, SKILL.md:106-112). The spec's Appendix notes the :228 prose, but §4.8 leaves it naming the re-export.

## sweeper

### Claim verdicts

#### C72 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; plugins/arch-compliance/hooks/posttooluse_gate.py:229-236; plugins/arch-compliance/hooks/posttooluse_gate.py:284-286; plugins/arch-compliance/python/acf/enforcement.py:47`
- reasoning: Searched by behaviour for the active-row test (unenforced / .status reads) across the tree, docs excluded. Tier-1 hits: cli_check_diff.py:98, posttooluse_gate.py:231, :235, :285 and enforcement.py:47. The design replaces each one with registry.active or runs_at. The other hits are registry.py:58 (rewritten in §4.2), judge.py:218 (Tier-2, out of scope by Decision 2), inject_constraints.py:158 (display only) and skill prose. No skill snippet filters rows by status for a Tier-1 gate.

#### C73 — REFUTED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:203-204; plugins/arch-compliance/hooks/posttooluse_gate.py:242-245; plugins/arch-compliance/python/acf/adr/citations.py:49-51`
- reasoning: The parse_python half holds: ast.parse plus SyntaxError appears only at facade_sinks.py:51, fail_loud_ratchet.py:24, fsm_guard.py:37 and python_pack.py:35. The file_under_root half also holds for registry-supplied paths. The first conjunct fails. After the design, the hook still makes its own 'is this path string absolute' test, `Path(raw).is_absolute()` on the raw harness string at posttooluse_gate.py:203-204. It also keeps its own 'is it under the root' test, `abs_path.relative_to(repo)` with try/except ValueError at :242-245, and that test now decides which paths reach host code. §4.1 excludes :204 as 'Path.is_absolute() on a path resolved for I/O'. But at :203 `p = Path(raw)` is unresolved harness input; is_absolute decides how it gets resolved. That is exactly the 'whether a path string is absolute' job §4.1 gives acf.engine. So the string tests do not have one definition after the design.

#### C74 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:84-92; plugins/arch-compliance/python/acf/cli_check_diff.py:153-156`
- reasoning: The bridge decodes a JSON dict from a Node subprocess and coerces severity, path and line with int() and Severity(). Each gate then rewrites path via model_copy (cli_check_diff.py:154, posttooluse_gate.py:280), because the Node output's path is not the repo-relative key. The host runner receives typed HostHit objects and takes severity and mandate_id from the row. The only shared part is the Finding constructor.

#### C75 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:241-251`
- reasoning: _to_finding is at judge.py:238-255; the claim's spec_citation of 236-253 is two lines off. It demotes BLOCK to WARN on confidence (:242-245) and admits path '<diff>' and line 0 (:249-250). It takes mandate_id from JudgeResult, which judge.py:326 stamps from the row. The host runner's rules differ (row severity, line >= 1, relative path). A shared constructor would have to parameterise all three rules, so ADJACENT is justified.

#### C76 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:25-26; plugins/arch-compliance/hooks/inject_constraints.py:28-29; tests/test_check_installed_skills.py:15-18`
- reasoning: Searched importlib, import_module, spec_from_file_location, exec_module, runpy, exec( and sys.path.insert/append over the whole tree. In the plugin, only the two hooks' start-up sys.path.insert(0, plugin python/) match. Neither loads a registry-supplied path. Outside the plugin, tests/test_check_installed_skills.py:15-18 uses spec_from_file_location/exec_module to load a fixed repo script. That is the same mechanism as load_host_detector but test-only, with no trust boundary or cache, so ADJACENT (listed under relationships).

#### C77 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80; plugins/arch-compliance/hooks/posttooluse_gate.py:119-123; plugins/arch-compliance/tests/test_enforcement.py:48`
- reasoning: Grepped line_lookup, LineLookup and '[line - 1]'. The only runtime closures passed to apply_registry are the two gate closures. Every other apply_registry caller is a test stub in test_enforcement.py, and no skill snippet calls apply_registry. A similar bounds-checked indexing lives at fsm_guard.py:56 as an inline snippet extraction. It is not a LineLookup, so the claim's scope holds.

#### C78 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:56-63; plugins/arch-compliance/tests/test_profile_drift.py:24; plugins/arch-compliance/skills/acf-mandate/SKILL.md:95; plugins/arch-compliance/skills/architecture-review/SKILL.md:62`
- reasoning: The registry.py:56-63 check is the only detector-id check today. test_profile_drift.py:24 and the acf-mandate snippet (:95) delegate to load_mandates(known_detectors=...). architecture-review SKILL.md:62 calls load_mandates with no detector set. acf-setup SKILL.md has no detector or call_sites check (grep for detector|call_sites|load_mandates). None re-implements the check.

#### C79 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:238-246`
- reasoning: The try/except ValueError at :242-245 is the hook's existing in-repo test, and rel_paths (:246) collects in-repo and absolute out-of-repo strings alike for the build-artifact guard. Recording a separate in_repo_rel_paths there adds no second test inside the hook. Note: only paths that pass is_file at :239 get that far. The better reuse would be resolve_under_root (see C81).

#### C80 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:46-47; plugins/arch-compliance/python/acf/cli_check_diff.py:168-182; plugins/arch-compliance/hooks/posttooluse_gate.py:284-295`
- reasoning: The ratchet is dispatched only in cli_check_diff.py:168-182; the hook's _scan_paths ends at :295 without it. apply_registry already matches by mandate_id at enforcement.py:46, and the design adds a runs_at drop there. Take the opposite drift, a gate dispatching a detector its contract excludes. A row declaring that site is refused at load by _check_builtin, and a row not declaring it has its finding dropped by apply_registry. Neither path lets the row silently fail to receive a finding it declared.

#### C81 — REFUTED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:202-204; plugins/arch-compliance/hooks/posttooluse_gate.py:242-245; plugins/arch-compliance/python/acf/adr/citations.py:74-76; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:59-62`
- reasoning: The hook does not start from 'an already-resolved absolute Path'. It starts from a raw harness string, `p = Path(raw)` at :203. It branches on is_absolute, joins with repo, resolves (:204), and then makes a containment decision with relative_to at :242-245. That pipeline (string, then resolved path, then 'inside root?') is what resolve_under_root does (`(base / rel).resolve()` then is_relative_to; base / an absolute path yields that path). The shared responsibility R is 'is this resolved path contained in the repo root'. It is implemented by is_relative_to in resolve_under_root (today citations.py:76) and by relative_to plus ValueError in the hook, and after the design the hook's version gates host dispatch. The spec's own §4.9 confirms the overlap at the ratchet site: it deletes the walk filter's `except ValueError: continue` (fail_loud_ratchet.py:59-62) because resolve_under_root's containment makes that branch unable to fire. That makes the branch the same job, not the opposite operation. The relative-string conversion (relative_to(...).as_posix()) is the only part that is the opposite direction.

#### C82 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:65; plugins/arch-compliance/python/acf/detectors/__init__.py:1-35`
- reasoning: Decision 7 (spec :65) says plainly that the wrapping does not confine host code (atexit, threads). Searched the spec for 'only inside', 'runs no host code' and 'does not confine'. The remaining statements are scoped: _to_findings runs no host code, and load_mandates imports none. Neither contradicts Decision 7. No loader-state reset exists in the tree today (acf.detectors has no _ACTIVE_ROOT or cache), so the proposed fixture would be the only reset. Not contradicted, though unenumerated finalizers (__del__ on a returned iterable after _call_host returns) also fall outside the wrap, consistent with the stated non-confinement.

#### C83 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:85; plugins/arch-compliance/detectors/typescript/src/scan.ts:94-96`
- reasoning: Grepped both literals over the tree, docs excluded. Python hits are tests only (test_enforcement, test_baseline, test_typescript_pack); YAML hits are registry rows. Today the bridge copies item['mandate_id'] (:85), which the design replaces. Node spells the literals in the rules (emptyCatch.ts:23, explicitAny.ts:15) and again in its self-test (scan.ts:94-96). The run-time check against TS_MANDATE_IDS covers the rule literals.

#### C84 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:52; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:133`
- reasoning: Every Tier-1 Finding passes through apply_registry, which overwrites severity from the row (:52). Scanner severities, such as the ratchet's Severity.BLOCK at :133, are required-field fills like the host runner's. Nothing after apply_registry touches severity in either gate (cli_check_diff.py:82-91, posttooluse_gate.py:125-126).

#### C85 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:56; plugins/arch-compliance/python/acf/cli_check_diff.py:115-120`
- reasoning: changed_files runs `git diff --name-only --diff-filter=ACMR`. Its output is repo-root-relative and enumerated by git, not taken from a registry string. A tracked symlink could still resolve outside the root, but that is pre-existing and not a registry/host-supplied path string, so file_under_root's job (containing a declared path) does not apply.

#### C86 — SURVIVED
- evidence: `config/architecture/mandates.yml:70; plugins/arch-compliance/profiles/python-service/mandates.yml:18; plugins/arch-compliance/tests/test_registry.py:35`
- reasoning: Grepped call_sites over every yml and test file here and over hm:config/architecture/mandates.yml (the HM checkout at C:/Users/iball/Arduino/Projects/HistoricMansions, opened directly; e.g. its :246 [audit, precommit], :513 [precommit], :525 [precommit, posttooluse, ci]). Here the values are ci, hook and audit; HM uses precommit, posttooluse, ci and audit. All fall within CallSite. This repo's [ci]-only active ast row (no-shims.hasattr, :70) gains precommit, and the [ci] ratchet rows are unenforced. Active [audit]-only rows here are manual or llm, so the Tier-1 row-shape rule refuses none.

#### C87 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_registry.py:30; plugins/arch-compliance/tests/test_diff_cli.py:102-108; plugins/arch-compliance/tests/test_hooks.py:199-218; plugins/arch-compliance/tests/test_typescript_pack.py:14`
- reasoning: Swept tests by behaviour: frozenset known_detectors (test_registry.py:30), _DETECTOR_IDS imports, apply_registry callers, main([...]) callers, fixture rows relying on [ci]-only hook reporting, and scan_tree/scan_ratchet callers. Also checked the Mandate constructions (test_enforcement.py:19, test_judge.py:41, test_template.py:73 with []) and the hook ImportError/no-op paths. Every break found is listed. test_profile_drift.py:24 and test_acf_mandate_skill keep passing because profile ids match the contracts. test_invalid_base_ref_exits_1 still raises GitError after the empty-selection check, since the fixture has active rows.

#### C88 — SURVIVED
- evidence: `README.md:57-58; plugins/arch-compliance/skills/acf-setup/SKILL.md:184; plugins/arch-compliance/skills/acf-setup/SKILL.md:219; docs/guides/SUPERPOWERS_COMPLEMENT.md:82-83; config/architecture/ARCHITECTURE.md:228`
- reasoning: Re-ran the acf-check-diff|acf.cli_check_diff grep and a 'detector union' grep, excluding docs/reviews and docs/plans. Every command line or instruction found is in the §4.8 list or its 'not edited' past-run list. One unlisted hit, config/architecture/ARCHITECTURE.md:228, names `acf.cli_check_diff.KNOWN_DETECTORS` as the package check. It stays valid through the re-export, so it is not stale.

### Unanchored findings

- **important**: After the design the PostToolUse hook keeps its own absolute-string test (Path(raw).is_absolute(), :204) and its own under-root test (relative_to/ValueError, :242-245). Together they decide which paths reach host code, so they are a second owner of the two tests §4.1 assigns to acf.engine. The spec excludes :204 as 'a path resolved for I/O', but it is raw harness input; host-dispatch eligibility should be resolve_under_root(repo, raw) is not None.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:203-204`
- **advisory**: The new existence refusals (host file in load_mandates, load_host_detector, and the ratchet baseline that replaces load_baseline's is_file at fail_loud_ratchet.py:78) partially duplicate acf.loader.require_file. That module states it is 'the one load-parse-validate-refuse implementation' with one message shape. The spec never names it and adds a further 'not found' message shape at the very loader ADR_GATE_HOST_CONTRACT.md:292-294 records as a pre-existing second loader.
  - evidence: `plugins/arch-compliance/python/acf/loader.py:24-28`
- **advisory**: The spec contradicts itself on the ratchet walk filter. §4.1 says it 'stays where it is' and §5.2 calls it ADJACENT to resolve_under_root. §4.9 deletes its `except ValueError: continue` because resolve_under_root's containment makes it unable to fire, which shows the branch is the same containment job.
  - evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:59-62`

### Looked for but did not find

- another active-row filter at a Tier-1 site: grep 'unenforced|\.status\b' over non-doc tree
- another parse-or-skip: grep 'ast\.parse|SyntaxError' (only four scanners plus test helpers)
- another drive/absolute regex: grep 'A-Za-z\]:|startswith("/")' (only citations.py:51, contract.py:95)
- another dynamic module loader in the plugin: grep 'importlib|import_module|spec_from_file_location|exec_module|runpy|exec\(|__import__'
- a third LineLookup passed to apply_registry: grep 'line_lookup|LineLookup|\[line - 1\]|apply_registry\('
- an independent detector-id or call_sites check in skills or tests: grep 'detector|call_sites|load_mandates' in architecture-review and acf-setup skills; read test_profile_drift.py and the acf-mandate Validate snippet
- a non-test Python runtime spelling of the TS mandate ids: grep 'fail-loud\.empty-catch|no-shims\.explicit-any'
- call-site values outside CallSite in shipped registries, tests or HM: grep 'call_sites' in yml and tests here and in hm:config/architecture/mandates.yml
- a prior on-record rejection of call_sites routing or host detector loading: grep 'call_sites|call-site|host detector|rejected' in docs/design
- tests broken but unlisted: grep '_DETECTOR_IDS|KNOWN_DETECTORS|scan_ratchet|scan_tree|baseline_path'; read test_diff_cli.py, test_hooks.py 160-250, test_acf_mandate_skill.py, test_adr_import_graph.py 40-90
- stale acf-check-diff command lines: grep 'acf-check-diff|acf\.cli_check_diff' excluding docs/reviews and docs/plans

### Relationships

- PARTIAL_OVERLAP: `acf.engine.resolve_under_root` — responsibility `decide whether a resolved path lies inside the repository root` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:242-245`
  - resolution: R = containment of a resolved path in the root. The hook's _collect_paths is_absolute/join/resolve (:203-204) plus relative_to/ValueError (:242-245) should call resolve_under_root(repo, raw) for the in-repo decision and keep only relative_to(...).as_posix() for the key string. resolve_under_root stays the single containment predicate.
- PARTIAL_OVERLAP: `acf.engine.looks_absolute` — responsibility `decide whether a path string is absolute` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:204`
  - resolution: R = absolute-string classification of untrusted path input. Folding the hook's Path.is_absolute branch into resolve_under_root (which handles absolute input by joining) removes the second, platform-dependent definition.
- BOUNDARY_CUT: `acf.engine.resolve_under_root` — responsibility `keep walked paths inside the root` — existing `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:59-62`
  - resolution: The walk filter's except ValueError becomes dead once roots are contained (§4.9 deletes it). Restate §4.1/§5.2: the containment part moves to resolve_under_root; only the relative-string conversion stays.
- PARTIAL_OVERLAP: `file_under_root callers' 'not found' refusals (load_mandates host file, load_host_detector, scan_ratchet baseline)` — responsibility `refuse an absent input file with one message shape` — existing `plugins/arch-compliance/python/acf/loader.py:24-28`
  - resolution: R = refuse-missing-file. Option: a require_file_under_root(root, rel, subject, error) beside require_file, or require_file accepting the file_under_root result. The ratchet's load_baseline existence check (fail_loud_ratchet.py:78) and the host-file checks then share one message shape.
- ADJACENT: `acf.detectors.host._to_findings (HostHit to Finding)` — responsibility `build Finding from external detector output` — existing `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:84-92`
  - resolution: none
  - non-merge: Input formats differ: untyped JSON with detector-supplied severity and a path the gates rewrite, versus a validated HostHit with row-supplied severity and id. Only the Finding constructor is shared.
- ADJACENT: `acf.detectors.host._to_findings (HostHit to Finding)` — responsibility `build Finding from external detector output` — existing `plugins/arch-compliance/python/acf/judge.py:238-255`
  - resolution: none
  - non-merge: The judge demotes severity by confidence and admits '<diff>'/line 0; host findings use row severity and require line >= 1 and a relative path.
- ADJACENT: `load_host_detector sys.path append` — responsibility `make a module tree importable by mutating sys.path` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:25-26`
  - resolution: none
  - non-merge: The hooks prepend the plugin's own python/ before any acf import; the loader appends one host root once per process for host-owned imports, at a different position and for a different trust level.
- ADJACENT: `load_host_detector spec_from_file_location/exec_module` — responsibility `load a Python module from a file path` — existing `tests/test_check_installed_skills.py:15-18`
  - resolution: none
  - non-merge: A test-only load of one fixed repository script, with no trust boundary, caching, root guard or failure wrapping. It is not a runtime consumer.
- ADJACENT: `acf.enforcement.make_line_lookup` — responsibility `fetch 1-based line text with a bounds check` — existing `plugins/arch-compliance/python/acf/detectors/fsm_guard.py:56`
  - resolution: none
  - non-merge: fsm_guard indexes its own already-split lines inline for a message snippet. It is not a path-keyed LineLookup and does not feed exemption checks.
- ADJACENT: `Mandate.runs_at / MandateRegistry.active` — responsibility `decide whether a row is live at a gate` — existing `plugins/arch-compliance/python/acf/judge.py:218`
  - resolution: none
  - non-merge: Tier-2 reviews every llm row and reads status only to decide whether a provider is required (Decision 2 scope).
- IDENTICAL: `acf.engine.parse_python` — responsibility `parse Python or skip on SyntaxError` — existing `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37`
  - resolution: Delete the four scanner copies (python_pack.py:34-37, facade_sinks.py:50-53, fsm_guard.py:36-39, fail_loud_ratchet.py:23-26) and consume parse_python, as the spec states.
- SUBSUMED: `acf.engine.looks_absolute / resolve_under_root` — responsibility `repo-relative path tests` — existing `plugins/arch-compliance/python/acf/adr/citations.py:49-51`
  - resolution: Delete citations._looks_absolute/_escapes_repo; citations.py:161/:163 consume the engine helpers, as the spec states.

### Two-owner counts

- decide whether a resolved path lies inside the repository root (resolve_under_root; posttooluse_gate.py:242-245): 2
- decide whether a path string is absolute (looks_absolute; posttooluse_gate.py:204 Path.is_absolute): 2
- refuse an absent input file (loader.require_file; load_mandates host-file check; load_host_detector; scan_ratchet baseline): 4
- decide whether a row is live at a gate (Mandate.runs_at; judge.py:218): 2
- build Finding from external detector output (host _to_findings; typescript_bridge.py:84-92; judge._to_finding): 3
- mutate sys.path for imports (posttooluse_gate.py:25-26; inject_constraints.py:28-29; load_host_detector): 3
- load a module from a file path (load_host_detector; tests/test_check_installed_skills.py:15-18): 2
- spell the TypeScript mandate ids (TS_MANDATE_IDS; emptyCatch.ts:23/explicitAny.ts:15; scan.ts:94-96): 3
- fetch 1-based line text with bounds check (make_line_lookup; fsm_guard.py:56): 2

### Document conflicts

- `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:184` (contradicts): Unknown detector id referenced by an enforced `ast` or `guard` row → drift/registry validation fail.
- `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:161` (contradicts): PostToolUse | Diff-scoped Tier 1 on edited `.py` / `.ts` / `.tsx` (and configured config paths); feed findings into the turn.
- `docs/design/ADR_GATE_HOST_CONTRACT.md:300` (restates): a refusal would be a second implementation of the repo-relative test that ... citations.py:49 (`_looks_absolute`) and `:74` (`_escapes_repo`) already own.
- `docs/design/ADR_GATE_HOST_CONTRACT.md:292` (restates): `fail_loud_ratchet.load_baseline` ... is a pre-existing second loader outside this phase.
- `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:500` (restates): All three import `KNOWN_DETECTORS`; one definition; unused `PYTHON_DETECTOR_IDS` removed
- `config/architecture/ARCHITECTURE.md:228` (restates): A check re-implemented in a test or a skill instead of consumed from the package (`acf.registry.load_mandates`, `acf.registry.missing_anchors`, `acf.cli_check_diff.KNOWN_DETECTORS`, the `acf.repo` constants).

## hardening

### Claim verdicts

#### C89 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:72; plugins/arch-compliance/hooks/posttooluse_gate.py:113-117; plugins/arch-compliance/hooks/inject_constraints.py:104; plugins/arch-compliance/python/acf/cli_check_llm.py:54`
- reasoning: load_mandates today imports nothing (registry.py:48-64). The spec puts the host-file existence check in load_mandates and the import/getattr in load_host_detector. load_host_detector raises UnknownDetectorError, which cli_check_diff.py:72 already catches, and which the hook's widened scan except (today :115) will catch. I resolved the part about CI-only guards myself: the hook loads every row, the [ci]-only ones included, so importing at load would run CI-only host guards on every edit. That justifies the deferral by itself. One caveat: the stated counterfactual that importing at load would run host code in the SubagentStart hook and in acf-check-llm is overstated. Neither passes known_detectors (inject_constraints.py:104, cli_check_llm.py:54), so an import-at-load gated on known_detectors, as the existence check already is, would not reach them. The spec also states the cost: a broken host ast module stays silent until a file in its language changes.

#### C90 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:124-182; plugins/arch-compliance/hooks/posttooluse_gate.py:238-294; plugins/arch-compliance/python/acf/enforcement.py:46`
- reasoning: I enumerated the row kinds. A host ast row with an allowed language is called by both gates' .py/.ts branches whenever its declared Tier-1 site matches. A host guard row is called by scan_host_guards after each dispatch loop. For a built-in row, _row_shape requires at least one Tier-1 site and _check_builtin requires the declared Tier-1 sites to be a subset of the contract's sites. The dispatch sites I read match the contract table: ratchet only at cli :168-182, every other detector in both gates. Findings land on the row because the row id is required to equal the contract's mandate_id, which is the id the scanner stamps (python_pack.py:67, :97), and apply_registry matches on that id (enforcement.py:46). Host findings take mandate.id from the row. The remaining drift between table and dispatch is closed by the contract-against-dispatch test, not at runtime.

#### C91 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:63; plugins/arch-compliance/hooks/posttooluse_gate.py:65; plugins/arch-compliance/tests/test_diff_cli.py:24-36`
- reasoning: Both production entry points resolve one repo per process: cli :63 calls resolve_repo once, and hook :65 resolves once in a fresh process per edit. The only multi-root producer is in-process tests: test_diff_cli _init_repo builds a fresh tmp repo per test and calls main() in process. The refusal is fail-loud at rung 3. The reset lives only in the test fixture, so production code holds no repair.

#### C92 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:67; plugins/arch-compliance/python/acf/detectors/python_pack.py:97; plugins/arch-compliance/python/acf/cli_check_diff.py:168-182; config/architecture/mandates.yml:59`
- reasoning: Every scanner stamps a fixed literal mandate_id, and the ratchet runs only in acf-check-diff, so the contract records facts already true in the code. I ran a read-only yaml census over the shipped and fixture registries: no active built-in detector appears on more than one row, and every row id equals its stamped id. The accepted cost touches no shipped registry. The design still stops at rung 3 for built-ins where rung 1 exists (see the unanchored findings).

#### C93 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:33-41; plugins/arch-compliance/python/acf/loader.py:70-73; plugins/arch-compliance/hooks/inject_constraints.py:103-107; plugins/arch-compliance/python/acf/cli_check_llm.py:54`
- reasoning: MandateRegistry._unique_ids already raises AcfInputError from a model_validator, and load_model_file converts only ValidationError (loader.py:70-73), so AcfInputError propagates with its own type. inject_constraints catches AcfInputError at :105. One sub-assertion is inaccurate: cli_check_llm.py:54 sits in no try, so 'handles' there means an uncaught traceback with non-zero exit. That is the same outcome as today, so the 'no caller change' conclusion holds.

#### C94 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37; plugins/arch-compliance/python/acf/engine.py:8`
- reasoning: Built-in scanners parse once each (python_pack.py:34-37). Sharing one parse across N host ast detectors on a file is a plain efficiency choice. The skip-on-SyntaxError convention is kept, and adding parse_python to engine keeps engine stdlib-only.

#### C95 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:46-52; plugins/arch-compliance/python/acf/finding.py:11-19`
- reasoning: apply_registry looks up the row through by_id.get(finding.mandate_id) at :46. A host-supplied Finding could carry any mandate_id or detector and so attach to another row. Building the Finding from a HostHit that has only path, line and message, with mandate_id taken from the row, makes the wrong-row state unrepresentable (rung 1).

#### C96 — SURVIVED
- evidence: `.gitignore:8; .github/workflows/ci.yml:40; plugins/arch-compliance/hooks/posttooluse_gate.py:72-81`
- reasoning: .gitignore:8 is '.acf/', so a CI checkout never has .acf/enabled. Requiring the marker for acf-check-diff would therefore disable ci.yml:40. The hook exits 0 before any deferred import when the marker is absent (:72-81). The residual manual-run case is stated and accepted in writing.

#### C97 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:27-52; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:78-93; plugins/arch-compliance/hooks/posttooluse_gate.py:254`
- reasoning: scan_python_file emits all three Python detectors' findings without consulting the registry, and scan_typescript_file emits both TS detectors the same way. The hook calls scan_python_file unconditionally at :254. Without the filter, the [ci]-only no-shims.hasattr row (mandates.yml) would still be reported by the hook. The filter is not redundant. The claim's parenthetical is wrong: spec Decision 2 does give the reason, citing python_pack.py:27-52.

#### C98 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:22-28; pyproject.toml:19-20; hm:scripts/ci/metadata_facade_guard.py:66`
- reasoning: The hook inserts the plugin's python/ at sys.path[0] and imports acf first. The console script's sys.path[0] is its own script directory. Appending the host root after those entries therefore cannot shadow stdlib, third-party or plugin modules. The origin host's intra-repo import (from scripts.ci.arch_compliance...) resolves from the root unless an earlier entry provides 'scripts'. In that case import or getattr fails inside load_host_detector's wrapped region and surfaces as UnknownDetectorError. The -m exposure from the host root predates this design and is disclosed.

#### C99 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:113-117; plugins/arch-compliance/python/acf/cli_check_diff.py:69-74; plugins/arch-compliance/python/acf/enforcement.py:49`
- reasoning: Both gates' file_lines dicts are built inside the function the scan try wraps (_scan_changed under cli :69-74, _scan_paths under hook :113-117), so an OSError raised as DetectorPackError there reaches an existing handler. apply_registry only calls line_lookup (:49), so keeping the lookup pure keeps apply_registry free of I/O. Reads use encoding='utf-8' with errors='replace'. That fits the 'Declared text decoding' rule (ARCHITECTURE.md:173-175), which requires a declared encoding.

#### C100 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:16; plugins/arch-compliance/python/acf/judge.py:29-36; plugins/arch-compliance/skills/acf-mandate/SKILL.md:56; plugins/arch-compliance/python/acf/registry.py:60`
- reasoning: judge.py:16 imports acf.registry, so registry importing acf.judge would create a cycle and the ids must be passed in. Today registry.py:60 checks only ast/guard rows, so the SKILL.md:56 rule is unenforced. The yaml census shows the shipped llm rows use llm_react_boundaries and llm_fail_loud, and both are in LLM_PROMPT_IDS (judge.py:29-36).

#### C101 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:29-61; config/architecture/ARCHITECTURE.md:120-133; hm:scripts/ci/run_guards.py:317-321`
- reasoning: A required argparse choice fails loud at the invocation that produces the ambiguity, which is rung 3 at the producer. Of the three stated reasons, only 'missing value fails loud instead of running the wrong rows' holds fully. The doctrine rule cited is scoped to the ADR gate's host values in adr.yml and explicitly lists other package defaults as outside it (ARCHITECTURE.md:120-133). The origin host's runner defaults --site to ci (run_guards.py:317-321), which the spec itself concedes. The mechanism is justified, but by less than is claimed.

#### C102 — SURVIVED
- evidence: `hm:scripts/ci/run_guards.py:126-130; config/architecture/mandates.yml:59`
- reasoning: run_guards.py:126-130 refuses a site that resolves to zero guards, so the zero-row false green is a real, previously observed state. The census shows no shipped row declares precommit today. Without adding precommit, a --call-site precommit run would select nothing, so the refusal and the registry edit are a coherent pair.

#### C103 — SURVIVED
- evidence: `C:/Users/iball/AppData/Roaming/Python/Python313/site-packages/pydantic/main.py:377; hm:scripts/ci/genre_conditional_guard.py:32-40`
- reasoning: Pydantic v2 stores field values in the instance __dict__ (model_construct sets __dict__ at main.py:377). After an exact-type check, dict(item.__dict__) therefore reads plain values without dispatching to host properties, and type() checks run no host __eq__. The origin host defines plain objects with code-running dunders (genre_conditional_guard.py:32-40). Doing the access inside the wrapped try is the right place for this external boundary.

#### C104 — SURVIVED
- evidence: `docs/design/ADR_GATE_HOST_CONTRACT.md:295-303; plugins/arch-compliance/python/acf/adr/citations.py:49-51; plugins/arch-compliance/python/acf/adr/citations.py:74-76; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:122-124`
- reasoning: The duplicates exist as listed: citations' private helpers, and the ratchet's hand join with no containment check. The shipped ratchet values are relative with no '..'. The approved ADR decision at :295-301 is kept. One of its two stated reasons, that a refusal would be a second implementation of citations' test, disappears once the test moves to acf.engine. The 'visible host choice' reason still carries it.

#### C105 — SURVIVED
- evidence: `hm:scripts/ci/genre_conditional_guard.py:32-40`
- reasoning: The named producer is real. A non-frozen @dataclass Finding has __str__ returning ...self.line_text.strip(), and a dataclass does not enforce types, so line_text=None makes str() raise AttributeError. Formatting such an exception outside a try would escape the typed error. The fallback substitutes only the message, and the primary failure is still raised as a typed error.

#### C106 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:14-27; plugins/arch-compliance/python/acf/registry.py:43-45`
- reasoning: Mandate is a pydantic BaseModel with no model_config and all the named fields: Language includes 'none' (:11), call_sites is list[str] (:21), params is dict|None (:26). MandateRegistry already carries an @property by_id (:43-45), so adding a property and methods is compatible.

#### C107 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/finding.py:6-19; plugins/arch-compliance/python/acf/registry.py:17`
- reasoning: Finding's required fields are mandate_id, severity, path, line, message and detector. confidence and detection have defaults, and detection is a str. Severity is a str Enum with members BLOCK and WARN, matching Mandate.severity's Literal['BLOCK','WARN'].

#### C108 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:23; plugins/arch-compliance/python/acf/enforcement.py:43-52`
- reasoning: by_id is at :43/:46, the unenforced drop at :47, the exemption check at :49-51 and the severity override at :52. LineLookup = Callable[[str,int],str] at :23 is satisfied by the proposed closure.

#### C109 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:69-82; plugins/arch-compliance/python/acf/cli_check_diff.py:140-156; plugins/arch-compliance/python/acf/cli_check_diff.py:168-184`
- reasoning: load is at :70 and scan at :71, both inside the try whose :72 except lists AcfInputError, UnknownDetectorError and DetectorPackError. The closure and apply_registry are at :76-82. repo, text, posix, lines and registry are in scope after :150. The .ts branch reads at :152 and can bind text. changed (:110) is in scope after the ratchet loop.

#### C110 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:91-125; plugins/arch-compliance/hooks/posttooluse_gate.py:229-294`
- reasoning: Deferred imports are at :91-104, the load try at :106-110 and the scan try at :113-117 (today except DetectorPackError only). The lookup and apply_registry are at :119-125, the inline filters at :229-236 and :284-286, and the relative_to/ValueError at :242-245. text (:251) and rel (:243) are in scope in both branches.

#### C111 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:72; plugins/arch-compliance/hooks/posttooluse_gate.py:113-117; plugins/arch-compliance/python/acf/enforcement.py:43-53`
- reasoning: Every host call sits inside _scan_changed or _scan_paths, which run under the gates' scan try. The cli except at :72 already lists all three types, and the hook's will once widened. apply_registry (:43-53) does no I/O, so a host-flagged file's lines cannot raise there. load_mandates' new raises (UnknownDetectorError, AcfInputError) sit in the cli try and in the hook's widened load except.

#### C112 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_diff_cli.py:24-36; C:/Python313/Lib/dataclasses.py:757`
- reasoning: The cleanup in the spec's code is correct. It pops sys.modules only when the cached entry is not this mod: after a failed exec, yes; after a getattr failure on a cached mod, no; when the spec or module_from_spec fails with mod None, nothing was registered. Module-level globals can be monkeypatched by the fixture. test_diff_cli builds a separate tmp repo per test and calls main() in process, so without the fixture the second-root refusal would fire. The spec confines host rows to fixture-using cases, and existing cases never reach the loader because the runners return before loading when no host row is selected.

#### C113 — SURVIVED
- evidence: `C:/Python313/Lib/dataclasses.py:757`
- reasoning: dataclasses._is_type does sys.modules.get(cls.__module__).__dict__ (:757) for string annotations. Without registration this raises AttributeError on None. cls.__module__ is the synthetic name spec_from_file_location gives the module, so registering under that name before exec_module satisfies it.

#### C114 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:5-7; plugins/arch-compliance/python/acf/detectors/python_pack.py:13-14; plugins/arch-compliance/python/acf/judge.py:16; plugins/arch-compliance/tests/test_adr_import_graph.py:70-76`
- reasoning: registry imports exceptions, loader and pydantic. No scanner module imports registry; they import only engine, finding and exceptions. So acf.detectors/__init__ importing registry creates no cycle, and neither reaches acf.judge (judge imports registry, not the reverse). test_adr_import_graph checks only that acf.adr imports no 'scripts' and that the hooks' text lacks 'acf.adr'. acf.adr already imports acf.engine (contract.py:20), so citations doing the same is permitted.

#### C115 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:53-64`
- reasoning: The call is exactly load_model_file(path, Mandate, subject='mandates file', fmt='yaml', many=True), and the function returns MandateRegistry(mandates=..., source_path=path.as_posix()).

#### C116 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_repo_paths.py:47-48; plugins/arch-compliance/hooks/posttooluse_gate.py:11-12`
- reasoning: The pinned string is '- If enabled and ``config/architecture/mandates.yml`` is missing: non-zero exit.', which is the hook docstring at :11. Line :12 ('Otherwise scan ...') is not pinned.

#### C117 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:77-82; config/architecture/mandates.yml:60`
- reasoning: _is_bare_or_exception matches node.type None or Name 'Exception' only, so 'except BaseException' is not flagged. mandates.yml:60 declares fail-loud.bare-except-ok. The detector misses BaseException, which is broader than Exception, so the token marks the handlers for readers but no gate checks it.

#### C118 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/engine.py:8; plugins/arch-compliance/python/acf/engine.py:17-24`
- reasoning: engine imports only pathlib.Path and defines contains_backslash at :17. Adding re (and ast for parse_python) keeps it stdlib-only.

#### C119 — SURVIVED
- evidence: `README.md:66-74; plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23; plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15; plugins/arch-compliance/tests/test_registry.py:20-31`
- reasoning: The README table at :66-74 has 7 rows of detector id and mandate id, and the TS ids are absent, matching the spec's Python-keys-only assertion. Each TS rule file carries a parseable mandate_id literal at the cited lines. test_registry already writes inline YAML rows to tmp files at :20-31 and :34-38.

#### C120 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_diff_cli.py:24-48; plugins/arch-compliance/tests/test_hooks.py:22-32`
- reasoning: test_diff_cli already builds tmp git repos and runs main() in process, and test_hooks already runs the hook in a subprocess with cwd set. The hook reads repo/MANDATES_REL, so a per-test registry can be written. Triggering the ratchet needs a baseline file and the TS rules need the Node pack installed; both are fixture setup, not missing hooks.

#### C121 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:109-184; plugins/arch-compliance/hooks/posttooluse_gate.py:226-295`
- reasoning: _scan_changed creates file_lines at :109 and returns it at :184. _scan_paths creates it at :226 and returns it at :295. Calling scan_host_guards before each return keeps it under the scan try, and setdefault-style filling preserves the gate's own reads.

#### C122 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:29-74`
- reasoning: The parser is built at :29-61, and argparse's parser.error raises SystemExit(2) in process for a missing or unknown choice. args is in scope at :63-74, so sites can be passed to _scan_changed (a signature change). An AcfInputError raised after load inside the :69-74 try reaches the :72 handler.

### Unanchored findings

- **advisory**: The TS mandate-id check keeps two definitions (the Node literal and TS_MANDATE_IDS) and adds a runtime comparison. Rung 1, where Node stops emitting mandate_id and the bridge stamps it from the detector, is never considered, and the spec gives no reason for keeping the Node literal.
  - evidence: `plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23`
- **advisory**: Built-in rows are held at rung 3: _check_builtin refuses a row id that differs from the stamped id, and only one active row per built-in detector is allowed. The host runner already reaches rung 1 by stamping mandate_id from the selecting row, and the gates could do the same for built-ins; the per-row facade/FSM loops already have the row in hand.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:128-150`
- **advisory**: The --call-site justification cites the 'Declared, never defaulted' rule, but that rule is scoped to the ADR gate's host values and explicitly lists other package defaults as outside it, so the spec's doctrine table stretches its scope without saying so.
  - evidence: `config/architecture/ARCHITECTURE.md:120-133`
- **advisory**: C93's claim that each caller already handles AcfInputError is false for acf-check-llm: load_mandates there is outside any try, so new row-shape refusals end in a traceback rather than a handled message (unchanged from today).
  - evidence: `plugins/arch-compliance/python/acf/cli_check_llm.py:54`
- **advisory**: The deferral's counterfactual is overstated: the SubagentStart hook and acf-check-llm do not pass known_detectors, so an import-at-load gated on known_detectors (as the existence check is) would not run host code there; only the CI-only-guards-on-every-edit reason carries the decision.
  - evidence: `plugins/arch-compliance/hooks/inject_constraints.py:104`

### Looked for but did not find

- A production caller of the gates that serves two repository roots in one process (searched resolve_repo use in cli_check_diff.py:63 and posttooluse_gate.py:65); none, so the second-root refusal has only a test producer
- A shipped registry with two active rows for one built-in detector (yaml census over config, both profiles and the fixture); none
- A shipped active ast/guard row whose id differs from its detector's stamped mandate_id; none
- A shipped llm row naming an id outside LLM_PROMPT_IDS; none
- A shipped row declaring precommit before this change; none
- An import cycle from registry->detectors or detectors->judge (grepped all detector and registry imports); none
- A pydantic wrapper that would turn a model_validator's AcfInputError into ValidationError; precedent registry.py:33-41 shows it propagates unwrapped
- A repair-on-load or normalizer in production code for host hits (the design refuses every malformed HostHit); none besides _describe's message fallback and errors='replace' on exemption reads

### Mechanism traces

- **Mandate._row_shape model_validator (host reference syntax, Tier-1 site, host ast languages)**
  - invalid state: row with detection in {ast,guard} and (':' in detector and the ref fails parse) or (is_active and call_sites ∩ TIER1 = ∅) or (host ast and languages == 'none')
  - producer: `config/architecture/mandates.yml:59`
  - rung 1 (highest applicable 1); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:816-835`
- **CallSite Literal on Mandate.call_sites**
  - invalid state: call_sites contains a value not in {ci, precommit, hook, posttooluse, audit}
  - producer: `plugins/arch-compliance/python/acf/registry.py:21`
  - rung 1 (highest applicable 1); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:772`
- **_check_builtin built-in contract check in load_mandates**
  - invalid state: active built-in ast/guard row with detector ∉ KNOWN_DETECTORS, or id != contract.mandate_id, or (call_sites ∩ TIER1) ⊄ contract.call_sites
  - producer: `plugins/arch-compliance/python/acf/detectors/python_pack.py:67`
  - rung 3 (highest applicable 1); repairs=False
  - hardening rejected because: the scanners stamp fixed mandate ids and run at fixed gates, so the contract records an existing fact rather than adding a capability; the accepted cost (at most one active row per built-in detector) affects no shipped registry
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:898-914`
- **TS_MANDATE_IDS stamp-and-compare in typescript_bridge**
  - invalid state: Node scanner item where item['detector'] ∉ TS_MANDATE_IDS or item['mandate_id'] != TS_MANDATE_IDS[item['detector']]
  - producer: `plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23`
  - rung 3 (highest applicable 1); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:923`
- **apply_registry call_sites filter**
  - invalid state: finding f whose row m=by_id[f.mandate_id] has m.call_sites ∩ gate_sites = ∅
  - producer: `plugins/arch-compliance/python/acf/detectors/python_pack.py:27-52`
  - rung 2 (highest applicable 2); repairs=False
  - hardening rejected because: This filter is needed at that one sink because the built-in scanners emit findings without consulting the registry
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:655`
- **load_mandates host-file existence and repo_root requirement**
  - invalid state: active host row where repo_root is None or file_under_root(repo_root, rel_path) is None or stat raises OSError
  - producer: `config/architecture/mandates.yml:59`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:877-894`
- **llm_prompt_ids check in load_mandates**
  - invalid state: active llm row with detector ∉ LLM_PROMPT_IDS
  - producer: `plugins/arch-compliance/python/acf/registry.py:60`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:864-869`
- **one host root per process refusal in load_host_detector**
  - invalid state: load_host_detector called with repo_root.resolve() != _ACTIVE_ROOT after a first call
  - producer: `plugins/arch-compliance/tests/test_diff_cli.py:24-36`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: Production callers resolve one repository per process ... In-process tests over several roots reset the loader through a test fixture
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:957`
- **fresh_host_loader test fixture (reset _ACTIVE_ROOT, _MODULE_CACHE, sys.path, host sys.modules)**
  - invalid state: loader globals hold a root/module from a previous test's tmp repo
  - producer: `plugins/arch-compliance/tests/test_diff_cli.py:48`
  - rung 5 (highest applicable 5); repairs=True
  - hardening rejected because: In-process tests over several roots reset the loader through a test fixture
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:1077`
- **load_host_detector wrapped exec/getattr (BaseException -> UnknownDetectorError, sys.modules cleanup)**
  - invalid state: host module raises any non-KeyboardInterrupt exception at exec or attribute lookup, or attr is not callable
  - producer: `hm:scripts/ci/metadata_facade_guard.py:66`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:960-982`
- **_call_host wrapped call and consumption (BaseException -> DetectorPackError)**
  - invalid state: host callable raises, returns None/str/bytes/non-iterable, or its iterator raises during list()
  - producer: `hm:scripts/ci/genre_conditional_guard.py:32-40`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:986-998`
- **_revalidate rebuild of each yielded HostHit**
  - invalid state: yielded item with type(item) is not HostHit, or __dict__ fields not exactly (str,int,str), or failing HostHit validation
  - producer: `C:/Users/iball/AppData/Roaming/Python/Python313/site-packages/pydantic/main.py:377`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:1000-1007`
- **_describe fallback message**
  - invalid state: host exception exc where f'{type(exc).__name__}: {exc}' raises
  - producer: `hm:scripts/ci/genre_conditional_guard.py:39-40`
  - rung 5 (highest applicable 5); repairs=True
  - hardening rejected because: str(exc) runs host code after the try has exited. That code can raise
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:1011-1017`
- **_to_findings ast path check**
  - invalid state: ast-row hit with hit.path != expected_path
  - producer: `hm:scripts/ci/arch_compliance/driver.py:150-163`
  - rung 3 (highest applicable 1); repairs=False
  - hardening rejected because: one HostHit type serves both callable kinds, and a path-less ast hit would be a second type carrying the same facts
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:1019`
- **scan_host_guards exemption-line fill (gate-read lines win; errors='replace' decode)**
  - invalid state: host-guard finding on a path p with p ∉ file_lines, so line_lookup returns '' and the exemption token is invisible
  - producer: `plugins/arch-compliance/python/acf/cli_check_diff.py:124-152`
  - rung 2 (highest applicable 2); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:1024`
- **resolve_under_root RuntimeError -> None mapping**
  - invalid state: rel whose (root/rel).resolve() raises RuntimeError (symlink loop, Python 3.11-3.12) or resolves outside root
  - producer: `plugins/arch-compliance/python/acf/adr/citations.py:74-76`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:726-733`
- **ratchet baseline/roots containment switch**
  - invalid state: params.baseline or a params.roots entry resolving outside repo_root or looping
  - producer: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:122-124`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:1121`
- **required --call-site and empty-selection refusal**
  - invalid state: acf-check-diff run with no declared site, or a site where registry.active(sites) has no ast/guard row
  - producer: `.github/workflows/ci.yml:40`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:1055`
- **contract-against-dispatch test**
  - invalid state: detector d with gate g ∈ KNOWN_DETECTORS[d].call_sites where g's dispatch code does not call d's scanner
  - producer: `plugins/arch-compliance/hooks/posttooluse_gate.py:213-295`
  - rung 3 (highest applicable 2); repairs=False
  - hardening rejected because: merging the pre-existing loops is left out to keep this change small
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:1079`

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
- **C13** [premise]: Deferral: no architecture-review runtime package and no architecture-review host configuration file exist at a338cad (recipe git ls-files plugins/arch-compliance/python/acf | grep -i review prints nothing); both belong to an unwritten Spec 2b. (Not load-bearing: this design touches neither.)
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
- **C29** [premise] [load-bearing]: getattr(mod, attr, None) swallows only AttributeError, so a host module-level __getattr__ raising anything else escapes a bare lookup; in spec §4.4 item 3 exec_module and the lookup share one try catching (Exception, SystemExit) that raises UnknownDetectorError, which cli_check_diff.py:72 and the hook's widened scan except catch. A failed exec_module removes the module from sys.modules; a failed lookup on a cached module leaves it cached.
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
- **C37** [premise] [load-bearing]: acf.engine.file_under_root (resolve_under_root, then Path.is_file, OSError from stat propagating) returns None for a missing path, a directory, an out-of-root path and a symlink loop on Python 3.11 to 3.13, and each runtime caller (load_mandates, load_host_detector, scan_host_guards, scan_ratchet) catches OSError around it and raises its typed error, so a permission-denied stat ends in UnknownDetectorError or DetectorPackError, not a traceback.
  - spec citation: `None`
- **C38** [premise] [load-bearing]: The design leaves AdrHostConfig.runs_dir and ledger_path (plugins/arch-compliance/python/acf/adr/host.py:24-25) unchanged, consistent with the approved ADR gate contract's decision not to refuse absolute or '..' values there ('That is a visible host choice, not a state the gate must prevent', ADR_GATE_HOST_CONTRACT.md:295-301); no section of the spec validates, tests or documents those fields as refused.
  - spec citation: `docs/design/ADR_GATE_HOST_CONTRACT.md:295-301`
- **C39** [premise] [load-bearing]: Switching the ratchet to file_under_root for params.baseline and resolve_under_root for each params.roots entry refuses an entry that escapes the root (an absolute path outside it included) or loops, still accepts an absolute path inside the root as today, refuses no shipped or tested value (baseline config/architecture/fail_loud_ratchet.json, roots ['.'], RATCHET_BASELINE_REL, test_portable_guards.py:107 roots=['pkg']), and raises DetectorPackError, which acf-check-diff already catches (cli_check_diff.py:72).
  - spec citation: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:122-124`
- **C40** [premise] [load-bearing]: A host exception whose str() raises has a concrete producer: BaseException.__str__ returns str(args[0]) for a one-argument exception, and hm:scripts/ci/genre_conditional_guard.py:33-40 declares a non-frozen dataclass Finding whose __str__ calls self.line_text.strip(); a dataclass does not enforce its annotations, so ValueError(Finding('a.md', 3, None, '...')) raises AttributeError when formatted, the case _describe handles inside each handler.
  - spec citation: `hm:scripts/ci/genre_conditional_guard.py:33-40`
- **C41** [premise] [load-bearing]: In _call_host, items = list(raw) inside the try consumes a host iterator to completion, or lets its exception propagate, before _revalidate runs, so a generator the runner holds is never left suspended when _revalidate refuses an item, and any finally body of that generator runs inside the wrapped region.
  - spec citation: `None`
- **C42** [premise] [load-bearing]: test_unenforced_mandate_does_not_gate is the only existing test whose registry has no active ast/guard row, so it is the only existing test the empty-selection refusal reaches; an added active no-shims.hasattr row with call_sites [ci] does not fire on the staged bad.py (which contains no hasattr), so the test still exits 0 and still shows the unenforced row does not gate.
  - spec citation: `plugins/arch-compliance/tests/test_diff_cli.py:102-108`
- **C43** [root_cause] [load-bearing]: Root cause of the registry/gate disagreement: a status: partial row is live in both Tier-1 gates (enforcement.py:47 drops only 'unenforced'; the gates' row filters likewise), yet load_mandates never checks it, so a host can name a non-built-in detector in a partial ast/guard row today, load cleanly with known_detectors=KNOWN_DETECTORS, and have nothing ever execute it.
  - spec citation: `plugins/arch-compliance/python/acf/enforcement.py:47`
- **C44** [root_cause] [load-bearing]: Root cause of the hook defect: posttooluse_gate.py:107 calls load_mandates(mandates_path) without known_detectors, so an active row naming an unknown detector is never validated in the PostToolUse hook and produces zero findings at edit time instead of failing loud.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:107`
- **C45** [root_cause] [load-bearing]: Root cause of the exemption defect: the _line_lookup closures (cli_check_diff.py:76-80, posttooluse_gate.py:119-123) are token-identical and consult only file_lines, which holds changed .py/.ts/.tsx files (cli_check_diff.py:126, :152; posttooluse_gate.py:248-252), so a finding on any other file gets "" and apply_registry (enforcement.py:49-50) cannot see an inline exemption token on it.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80`
- **C46** [deletion] [load-bearing]: Deleting citations._looks_absolute (:49-51) and _escapes_repo (:74-76) is safe: their only references are the call sites at citations.py:161 and :163, no test imports them, resolve_citation keeps its order, and exactly two behaviours change, both stated in spec §4.1 and §4.9: a drive-relative string such as 'C:a/b.py' classifies external, and on Python 3.11 and 3.12 a symlink-loop citation classifies unresolved instead of raising RuntimeError.
  - spec citation: `plugins/arch-compliance/python/acf/adr/citations.py:74-76`
- **C47** [deletion] [load-bearing]: Deleting cli_check_diff._active_mandates and the hook's inline filters in favour of registry.active(call_sites, detector=...) changes no selection except by call_sites: for every shipped registry, the only built-in row that stops running at a gate is no-shims.hasattr leaving the PostToolUse hook (it declares [ci]).
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99`
- **C48** [deletion] [load-bearing]: Removing LLM_PROMPT_IDS from KNOWN_DETECTORS changes behaviour only for ast/guard rows naming an LLM prompt id: load_mandates consults known_detectors only for ast/guard rows (registry.py:60), and no code reads KNOWN_DETECTORS for llm rows. The import at cli_check_diff.py:21 stays and feeds load_mandates(..., llm_prompt_ids=LLM_PROMPT_IDS), so LLM_PROMPT_IDS keeps a runtime consumer.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:21`
- **C49** [deletion] [load-bearing]: Replacing the literal mandate ids in the five scanner modules with module constants changes no emitted finding, and no test asserts on the scanner source text in a way the change would break.
  - spec citation: `None`
- **C50** [deletion] [load-bearing]: Deleting the two _line_lookup closures (cli_check_diff.py:76-80, posttooluse_gate.py:119-123) for make_line_lookup(file_lines), which is their body unchanged and reads no file, changes no exemption result for any finding at a338cad. The only new lines in file_lines are those scan_host_guards adds for files a host guard flags, so a built-in finding on such a file becomes exemptable as built-in findings on changed code files already are; a built-in finding on any other file still gets ''.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80`
- **C51** [deletion] [load-bearing]: Deleting the five detector-id sets (PYTHON_AST_DETECTOR_IDS, GUARD_DETECTOR_IDS, CONFIG_AST_DETECTOR_IDS, ALL_PYTHON_DETECTOR_IDS, TS_DETECTOR_IDS) touches only the references git grep -n "_DETECTOR_IDS" -- plugins tests prints, each of which the spec rewrites, and leaves KNOWN_DETECTORS as the only set of built-in detector ids in plugins/arch-compliance/python.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/__init__.py:11-28`
- **C52** [deletion] [load-bearing]: Replacing the inline params extraction in both gates with facade_sink_args, fsm_guard_args and build_artifact_args (required arguments as str(params.get(key, '')); allowlist_globs and atomic_is_sink passed unchanged when the key is present, null included; path_prefixes only when present and non-empty) produces the same scanner call for every row as today, because the scanners' signature defaults (facade_sinks.py:24-25, build_artifacts.py:16, :23) equal what the gates pass today when the param is absent.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/facade_sinks.py:24-25`
- **C53** [deletion] [load-bearing]: Replacing the four parse-and-skip copies with acf.engine.parse_python changes no scanner output, and no other site in plugins/arch-compliance/python parses Python with a SyntaxError skip.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37`
- **C54** [deletion] [load-bearing]: Once each params.roots entry is resolved and contained with resolve_under_root, every path rglob yields under it keeps the resolved root as a lexical prefix, so the walk filter's except ValueError: continue (fail_loud_ratchet.py:59-62) cannot fire and deleting that branch changes no count; scan_tree's callers are scan_ratchet and test_portable_guards.py:107.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:59-62`
- **C55** [mandate] [load-bearing]: ## Fail loud: every invalid state in spec §6.1 is refused by the named component with the named error, including: acf-check-diff without --call-site (usage error, exit 2) or with a site selecting no active ast/guard row (AcfInputError); a host module whose import or callable lookup raises any exception but KeyboardInterrupt (UnknownDetectorError); a host callable or its result raising any exception but KeyboardInterrupt, or yielding a non-exact-type or invalid HostHit (DetectorPackError); a host path whose stat raises OSError (typed error at each caller); a TypeScript item with an unknown detector or differing mandate_id; an llm row with an unknown prompt id. Every broad handler re-raises a typed error or KeyboardInterrupt.
  - spec citation: `None`
- **C56** [mandate] [load-bearing]: ## Fail loud: no active built-in ast/guard row can load with known_detectors yet never receive a finding from either Tier-1 gate: _check_builtin refuses a detector not in KNOWN_DETECTORS (LLM prompt ids are not keys), a row id that differs from the detector's stamped mandate_id, and any declared Tier-1 call site outside the detector's contract call_sites (fail_loud_ratchet: DIFF only); and Mandate._row_shape refuses an active ast/guard row with no Tier-1 site. Host rows are dispatched by both gates' host runners at any Tier-1 site.
  - spec citation: `None`
- **C57** [mandate] [load-bearing]: ## Declared, never defaulted: load_mandates requires an explicit repo_root for an active host detector row (AcfInputError otherwise, never derived), and apply_registry's new call_sites keyword has no default.
  - spec citation: `config/architecture/ARCHITECTURE.md:118-133`
- **C58** [mandate]: ## No shims: callable lookup is getattr(mod, attr, None) followed by callable() and a raise; no hasattr, and no host-detector failure has a silent fallback.
  - spec citation: `config/architecture/ARCHITECTURE.md:43-53`
- **C59** [mandate]: ## POSIX paths: HostHit.path is validated by validate_posix_rel_path (which refuses backslashes) and error messages use .as_posix().
  - spec citation: `config/architecture/ARCHITECTURE.md:55-64`
- **C60** [mandate]: ## One base exception: the design adds no exception class and uses AcfInputError, UnknownDetectorError and DetectorPackError (exceptions.py:5, :13, :29), all subclassing AcfError.
  - spec citation: `plugins/arch-compliance/python/acf/exceptions.py:5`
- **C61** [mandate]: ## One owner for host paths: acf/engine.py, acf/registry.py, acf/detectors/__init__.py and the new acf/detectors/host.py spell no config/architecture path, and the acf-mandate skill snippet takes MANDATES_REL and resolve_repo from acf.repo.
  - spec citation: `None`
- **C62** [mandate]: ## Prose names no host: the runtime messages in §4.2-§4.4 and the prose changes in §4.8 name no origin host.
  - spec citation: `config/architecture/ARCHITECTURE.md:135-143`
- **C63** [mandate]: ## Live consumers: each new export in §6.2 has the named non-test caller (file_under_root: load_mandates, load_host_detector, scan_host_guards, scan_ratchet; parse_python: four scanners and scan_host_ast_file; the *_args functions: both gates; CallSite: Mandate.call_sites; DIFF_CALL_SITES: acf-check-diff's --call-site choices and KNOWN_DETECTORS), acf.judge.LLM_PROMPT_IDS keeps a runtime consumer, and the five deleted detector-id sets leave no dead export behind.
  - spec citation: `None`
- **C64** [mandate]: ## No completeness claims: every population claim in the spec carries a re-runnable recipe (§1, §3, Appendix) or is a per-item table, as ARCHITECTURE.md:159-169 requires.
  - spec citation: `config/architecture/ARCHITECTURE.md:159-169`
- **C65** [mandate]: ## Declared text decoding: the new read_text calls (cli_check_diff.py TypeScript branch, scan_host_guards' read of flagged files) declare encoding='utf-8'; errors='replace' in scan_host_guards is permitted by that rule, which governs the declared encoding; no subprocess is added.
  - spec citation: `None`
- **C66** [mandate]: ## Release discipline: because shipped skill prose changes, the version is bumped 0.2.2 -> 0.2.3 in both files ARCHITECTURE.md:186-187 names (pyproject.toml:3, plugins/arch-compliance/.claude-plugin/plugin.json:3).
  - spec citation: `config/architecture/ARCHITECTURE.md:184-194`
- **C67** [mandate]: ## Single point of definition: each existing definition listed in spec §4.9 is deleted and its callers switched (citations' path helpers, the five detector-id sets, the line-lookup closures, the active-row filters, the duplicated params extraction, the ratchet's joins, existence check and unreachable walk-filter branch, the four parse-and-skip copies, test_self_host's resolve-and-is_file), the scanners' signature defaults stay the one default for optional params, and the spec makes no claim that §4.9 lists every duplicate in the tree.
  - spec citation: `None`
- **C68** [mandate]: ## Scoped refactor: Decision 8 deletes the existing definitions §4.9 lists, each duplicated by a new definition in this design, in the code paths it changes, and makes no claim beyond that list; the two pre-existing dispatch loops stay (two call sites of one procedure), and the git-supplied join-and-is_file in _scan_changed (cli_check_diff.py:118-119) is a different job recorded as ADJACENT.
  - spec citation: `config/architecture/ARCHITECTURE.md:213-215`
- **C69** [mandate]: ## Frozen ledger format: the design changes no ledger model.
  - spec citation: `config/architecture/ARCHITECTURE.md:145-151`
- **C70** [mandate]: The design complies with the five portable governing principles at docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51 and fulfils that spec's call for project-specific detector extension points (:102, :123, :125).
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51`
- **C71** [mandate]: ## Fail loud: scan_host_guards mapping a flagged path for which file_under_root returns None (missing, directory, outside the root, symlink loop) to [] and decoding with errors='replace' hides no failure: such a path has no line that could carry an exemption token, so the finding stays; an OSError from the stat or the read raises DetectorPackError inside each gate's scan try; and make_line_lookup does no I/O.
  - spec citation: `None`
- **C72** [shape_fit] [load-bearing]: Mandate.runs_at and MandateRegistry.active become the single definition of 'this row runs at this gate' for the Tier-1 gates; after the change no other Tier-1 site (cli_check_diff, posttooluse_gate, enforcement, the host runners) keeps its own active-row filter.
  - spec citation: `None`
- **C73** [shape_fit] [load-bearing]: After the design, the absolute and under-root string tests have one definition in acf.engine, consumed by validate_posix_rel_path, file_under_root, citations.py and the ratchet; file_under_root is the one resolve-plus-existence check for a registry- or host-supplied file path (load_mandates, load_host_detector, scan_host_guards, scan_ratchet, tests/test_self_host.py:40), and parse_python the one parse-or-skip (four scanners and scan_host_ast_file).
  - spec citation: `None`
- **C74** [shape_fit] [load-bearing]: Building Finding from a validated HostHit in acf.detectors.host is ADJACENT to, not a partial duplicate of, the TypeScript bridge's JSON-to-Finding coercion (typescript_bridge.py:75-95), because the inputs share no format.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:75-95`
- **C75** [shape_fit] [load-bearing]: Building Finding from a HostHit is ADJACENT to the judge's _to_finding (judge.py:238-255): the judge demotes severity by confidence and admits path="<diff>" and line=0, while host findings take severity from the row and require a relative path and line >= 1, so no shared constructor is warranted.
  - spec citation: `plugins/arch-compliance/python/acf/judge.py:236-253`
- **C76** [shape_fit] [load-bearing]: acf/detectors/host.py partially duplicates no existing mechanism: nothing in the plugin today loads or executes code from a registry-supplied file path, and the loader's one-time append of a host root to the end of sys.path is ADJACENT to the hooks' own start-up insertion of the plugin's python/ directory (posttooluse_gate.py:22-26, inject_constraints.py:28-29).
  - spec citation: `None`
- **C77** [shape_fit] [load-bearing]: make_line_lookup consolidates the only two line-lookup closures passed to apply_registry; no third LineLookup implementation exists (e.g. in cli_check_llm.py, the judge, or any skill snippet) that would remain a second definition.
  - spec citation: `None`
- **C78** [shape_fit] [load-bearing]: Detector-reference validation lives in two cooperating places only, Mandate._row_shape (row-local rules, every caller) and load_mandates with known_detectors (built-in contracts and host-file existence); no other validator (the acf-mandate skill's ## Validate snippet, test_profile_drift.py, the architecture-review skill, acf-setup) independently checks detector ids or call sites in a way that would diverge.
  - spec citation: `None`
- **C79** [shape_fit]: Host dispatch in the hook reuses the hook's existing abs_path.relative_to(repo) try/except ValueError (posttooluse_gate.py:242-245) to record in-repo paths in a separate in_repo_rel_paths list, rather than adding a second in-repo test; rel_paths keeps its current contents for the build-artifact guard.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:242-245`
- **C80** [shape_fit] [load-bearing]: The §4.7 contract-against-dispatch test ties KNOWN_DETECTORS' call_sites to the gates' dispatch: a detector the table says runs at a gate but which that gate does not dispatch fails the test; the opposite drift cannot attach a finding to any loaded row, because _check_builtin refuses a row declaring that site and apply_registry drops a finding whose row does not run at the gate, so it over-refuses and never silently drops a row.
  - spec citation: `None`
- **C81** [shape_fit] [load-bearing]: resolve_under_root (relative string -> contained Path) is ADJACENT to abs_path.relative_to(repo) at posttooluse_gate.py:242-245 and the ratchet walk filter at fail_loud_ratchet.py:59-62 (resolved absolute Path -> relative string): they are opposite operations, not two implementations of one.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:242-245`
- **C82** [shape_fit] [load-bearing]: The spec's account of where host code runs is consistent: Decision 7 guarantees that every failure raised while a runner calls host code (module execution, callable lookup, the call, consuming and rebuilding its result, formatting its exception) becomes a typed ACF error, and states that the wrapping does not confine host code (atexit handlers, threads); no other section claims that host code runs only inside the wrapped regions; and the fresh_host_loader fixture is the single reset of loader state.
  - spec citation: `None`
- **C83** [shape_fit] [load-bearing]: TS_MANDATE_IDS is the single Python definition of the TypeScript mandate ids: the bridge stamps from it, KNOWN_DETECTORS reads it, and no other non-test Python site spells 'fail-loud.empty-catch' or 'no-shims.explicit-any' as a runtime value; the Node literals are checked against it on every finding.
  - spec citation: `None`
- **C84** [shape_fit]: apply_registry is the single owner of Finding.severity on the Tier-1 path (enforcement.py:52); the host runner's severity value is a required-field fill that apply_registry overwrites, as §4.4 item 5 and §5.2 state.
  - spec citation: `None`
- **C85** [shape_fit] [load-bearing]: The join-and-is_file in _scan_changed (cli_check_diff.py:118-119) is ADJACENT to file_under_root, not a duplicate: its path comes only from git diff --name-only --diff-filter=ACMR (diff.py:56), is repo-relative by construction, and is never registry- or host-supplied, so file_under_root's containment job does not apply.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:118-119`
- **C86** [sweep] [load-bearing]: Sweep: the call-site vocabulary in use across shipped registries, tests and the origin host is within CallSite {ci, precommit, hook, posttooluse, audit}; after each ast/guard row declaring ci also declares precommit, every active ast/guard row routes to at least one Tier-1 site at which its detector runs, and audit stays read by no Tier-1 gate.
  - spec citation: `None`
- **C87** [sweep] [load-bearing]: Sweep: the test changes in spec §4.7 cover every existing test the design breaks or makes stale, including test_unenforced_mandate_does_not_gate (test_diff_cli.py:102-108, which gains an active no-shims.hasattr row so the empty-selection refusal does not fire), the ten main([...]) calls in test_diff_cli.py (now passing --call-site), the ten apply_registry calls in test_enforcement.py, test_hooks.py:199-218, test_registry.py:30, test_typescript_pack.py:6 and :14, tests/test_self_host.py:23, :40 and :5, test_acf_mandate_skill.py:2 and test_portable_guards.py.
  - spec citation: `None`
- **C88** [sweep]: The §4.7/§4.8 sites cover every shipped doc, skill, docstring, config and test the design makes stale: each command line or instruction for acf-check-diff that the §4.8 recipe prints (.github/workflows/ci.yml:40, README.md:57-58, acf-setup SKILL.md:24, :184, :193, :206, :207, :217, :219, :250 and its success criteria, acf-mandate SKILL.md:131, CLAUDE.md:36, docs/guides/SUPERPOWERS_COMPLEMENT.md:82-83, PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:454), the upgrade note for previously installed hosts (README.md, acf-setup SKILL.md), KNOWN_DETECTORS described as a union, the hook's call-site behaviour, apply_registry's drop rules, and the deleted detector-id sets.
  - spec citation: `None`
- **C89** [mechanism_justification] [load-bearing]: Deferring host import to dispatch (load_mandates checks reference syntax, Tier-1 site, languages, built-in contracts and host-file existence, and imports nothing) is justified: a missing file still fails at load, an import failure or missing callable fails loud at dispatch as UnknownDetectorError caught by both gates' except tuples, and importing at load would run host code in the SubagentStart hook and acf-check-llm and import CI-only guards on every edit.
  - spec citation: `None`
- **C90** [mechanism_justification] [load-bearing]: The row-shape checks on Mandate (host-reference syntax, a Tier-1 site, host ast languages) together with the per-detector BuiltinDetector contracts (known id, matching mandate_id, declared Tier-1 sites within the contract's call_sites) are sufficient to prevent an active ast/guard row that loads with known_detectors yet is run by neither acf-check-diff (DIFF_CALL_SITES) nor the hook (HOOK_CALL_SITES), or whose findings land on no row.
  - spec citation: `None`
- **C91** [mechanism_justification] [load-bearing]: Refusing a second host root in one process (AcfInputError) rather than evicting the old root is justified: every production caller resolves one repository per process, so the refusal never fires in production, and the only multi-root producer (in-process tests) is handled by the test-only fresh_host_loader fixture; no repair mechanism lives in production code.
  - spec citation: `None`
- **C92** [mechanism_justification] [load-bearing]: Declaring, per built-in detector, the mandate id it reports to and the call sites where a gate runs it (BuiltinDetector in KNOWN_DETECTORS) is justified over the alternatives: the scanners stamp fixed mandate ids and run at fixed gates, so the contract records an existing fact rather than adding a capability; the accepted cost (at most one active row per built-in detector) affects no shipped registry.
  - spec citation: `None`
- **C93** [mechanism_justification]: Moving the row-local rules onto a Mandate model_validator (rather than keeping them in load_mandates) is justified because it makes the SubagentStart hook, acf-check-llm and any direct Mandate construction reject the same malformed rows as the gates, with no caller change since each already handles AcfInputError.
  - spec citation: `None`
- **C94** [mechanism_justification]: Parsing a Python file once and sharing the tree across every host ast detector on it is justified by avoiding N parses per file; built-in scanners keep their own parses unchanged.
  - spec citation: `None`
- **C95** [mechanism_justification] [load-bearing]: Having host callables return HostHit (path, line, message) and building Finding in the runner from the mandate row, rather than accepting Finding and overwriting fields, is justified because apply_registry matches findings to rows by mandate_id (enforcement.py:37-53) and a host-supplied mandate_id/detector/severity could otherwise attach a finding to the wrong row.
  - spec citation: `None`
- **C96** [mechanism_justification] [load-bearing]: Treating the host's own pre-commit/CI invocation of acf-check-diff as its opt-in to running host code, and gating only the automatic hooks on .acf/enabled, is justified because .acf/ is gitignored and CI would otherwise be disabled; a user who runs acf-check-diff manually in an untrusted checkout is the residual case the design accepts.
  - spec citation: `.gitignore:8`
- **C97** [mechanism_justification] [load-bearing]: The call_sites filter added to apply_registry is needed in addition to the scanners' registry.active(call_sites) selection, because some built-in scanners emit findings by detector id without consulting the registry's call_sites, so without the filter a finding for a row not declared at this gate would survive. (The spec states the filter but gives no reason it is not redundant.)
  - spec citation: `None`
- **C98** [mechanism_justification] [load-bearing]: Appending the host root to the end of sys.path rather than inserting it at the front is justified: it adds no shadowing of standard-library, third-party or plugin modules under the hook and console-script entry points, keeps host intra-repo absolute imports working from the host root, and its stated cost (a host top-level name an earlier entry provides resolves to that entry) fails at import or callable lookup as UnknownDetectorError in the common case; dropping the acf/ refusal removes a check with no producer.
  - spec citation: `None`
- **C99** [mechanism_justification] [load-bearing]: Reading flagged files in scan_host_guards, inside each gate's scan try, instead of lazily in the line lookup is justified: it keeps apply_registry free of I/O and new errors, converts an unreadable file to DetectorPackError where both gates already report it, and limits new exemption lines to files a host guard flagged.
  - spec citation: `None`
- **C100** [mechanism_justification]: Enforcing llm prompt ids at load (llm_prompt_ids, passed by acf-check-diff) is justified: it gives acf.judge.LLM_PROMPT_IDS a runtime consumer after it leaves KNOWN_DETECTORS, makes the acf-mandate skill's stated rule true, and refuses no shipped row; registry.py cannot import acf.judge, so the ids are passed in rather than imported.
  - spec citation: `None`
- **C101** [mechanism_justification] [load-bearing]: A required --call-site argument on acf-check-diff, rather than a default or a site derived from --mode/--base, is justified: the doctrine's ## Declared, never defaulted rule, the origin host's per-site row selection, and the fact that a missing value then fails loud (usage error) instead of silently running the wrong rows; the cost, adding the flag at each existing invocation, is listed per site.
  - spec citation: `None`
- **C102** [mechanism_justification] [load-bearing]: Refusing a --call-site that selects no active ast/guard row (AcfInputError), and adding precommit to every shipped row that declares ci, are justified together: without them the documented pre-commit invocation would run no row and report clean, the false green the origin host's runner already refuses (hm:scripts/ci/run_guards.py:126-130).
  - spec citation: `None`
- **C103** [mechanism_justification] [load-bearing]: Rebuilding each yielded item inside _call_host (exact type, exact field types, then validation) is justified over checking the type in _to_findings: field access and comparisons on an unvalidated host object can run host code, so they must happen inside the wrapped region, and a rebuilt HostHit holds only plain str and int values.
  - spec citation: `None`
- **C104** [mechanism_justification]: Decision 8 (delete the existing definitions §4.9 lists and switch their callers) is justified over recording them as debt: it removes code, removes completeness claims about remaining breaches, and each switch's behaviour change is checked against every shipped value (spec §4.9, Appendix); where an approved spec chose otherwise (AdrHostConfig's path fields, ADR_GATE_HOST_CONTRACT.md:295-301), the design keeps that decision.
  - spec citation: `None`
- **C105** [mechanism_justification] [load-bearing]: _describe (format the host exception inside its own try, fall back to a constant message for any exception but KeyboardInterrupt) is justified by a named producer: an exception carrying an origin-host object whose __str__ raises (hm:scripts/ci/genre_conditional_guard.py:33-40); without it, formatting the typed error's message would raise outside the wrapped region and end in a traceback.
  - spec citation: `None`
- **C106** [implementability] [load-bearing]: Mandate (registry.py:14-27) is a Pydantic BaseModel exposing every field the design reads: id, severity, status, detection, detector, call_sites (list[str]), languages (Literal including 'none'), and params (dict or None); adding an @property is_active and a plain method runs_at to it, and a method active to MandateRegistry, is compatible with its model_config.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:14-27`
- **C107** [implementability] [load-bearing]: Finding (acf/finding.py) can be constructed as Finding(mandate_id=, severity=Severity(mandate.severity), path=, line=, message=, detector=, detection=): those are its fields, Severity is constructible from Mandate.severity's value, and no other required field is missing.
  - spec citation: `None`
- **C108** [implementability] [load-bearing]: apply_registry (enforcement.py) looks up each finding's row via registry.by_id, drops it on the status check at :47 (replaceable by runs_at), and handles exemptions and severity at :49-52 using a LineLookup type that make_line_lookup can return.
  - spec citation: `plugins/arch-compliance/python/acf/enforcement.py:47`
- **C109** [implementability] [load-bearing]: cli_check_diff.py has the hook points the design names with the needed names in scope: load at :70 inside a try whose except tuple at :72 lists AcfInputError, UnknownDetectorError and DetectorPackError (and wraps both load and scan); lookup and apply_registry at :76-82; in the .py branch after scan_fsm_writes (:140-150) repo, text, posix, lines and registry; in the .ts/.tsx branch (:151-156) a read that can bind text; and after the ratchet loop (:168-182) the changed-file list.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:72`
- **C110** [implementability] [load-bearing]: posttooluse_gate.py has the hook points the design names: deferred imports at :91-104, the load try at :106-110, the scan try at :113-117 (whose except can be widened to AcfInputError, DetectorPackError, UnknownDetectorError), lookup/apply_registry at :119-125, inline filters at :229-236 and :284-286, the relative_to with ValueError fallback at :242-245 where an in_repo_rel_paths list can be recorded, the build-artifact loop at :284-294, and text and rel in scope in the .py and TypeScript branches of _scan_paths.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:113-117`
- **C111** [implementability] [load-bearing]: Host-detector failures reach an existing fail-loud handler in both gates, never a traceback: load_host_detector raises UnknownDetectorError for any exception but KeyboardInterrupt during import or lookup and for a stat OSError, AcfInputError for a second root; _call_host raises DetectorPackError for any exception but KeyboardInterrupt from the call, from consuming the result and from rebuilding each item; scan_host_guards raises DetectorPackError for a stat or read OSError; apply_registry does no I/O; cli_check_diff.py:72 and the hook's widened scan except catch all three error types.
  - spec citation: `None`
- **C112** [implementability] [load-bearing]: load_host_detector is implementable as stated: module-level _ACTIVE_ROOT and _MODULE_CACHE, a one-time sys.path.append of the root, file_under_root for the module path, spec_from_file_location with a None spec or loader refused inside the wrapped region, registering in sys.modules before exec_module and removing it if exec_module raises, and exec plus getattr in one try; and the fresh_host_loader fixture isolates in-process tests over several roots, including test_diff_cli.py's in-process main() calls.
  - spec citation: `None`
- **C113** [implementability] [load-bearing]: Registering the module in sys.modules under its name before spec.loader.exec_module(mod) is what lets a host module define a @dataclass under `from __future__ import annotations` (dataclasses resolves sys.modules[cls.__module__]); importlib.util.spec_from_file_location with a synthetic name supports this.
  - spec citation: `None`
- **C114** [implementability] [load-bearing]: The imports the design adds are cycle-free and allowed: acf.registry imports acf.engine, dataclass and Mapping, and nothing from acf.detectors; acf.detectors/__init__ imports acf.registry (BuiltinDetector, call-site sets) and the scanner modules' constants without a cycle; acf.cli_check_diff re-exports KNOWN_DETECTORS from acf.detectors; acf.detectors.host imports registry, finding, engine and exceptions; acf/adr/citations.py importing acf.engine is permitted by test_adr_import_graph.py; and the hook's new deferred imports (from acf.detectors, not acf.cli_check_diff) do not reach acf.adr or acf.judge.
  - spec citation: `plugins/arch-compliance/tests/test_adr_import_graph.py:70-76`
- **C115** [implementability] [load-bearing]: load_mandates today loads rows via load_model_file(path, Mandate, subject='mandates file', fmt='yaml', many=True) returning a list of Mandate, and builds MandateRegistry(mandates=..., source_path=path.as_posix()), so the §4.2 body is a drop-in extension of the existing function.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:48-64`
- **C116** [implementability]: plugins/arch-compliance/tests/test_repo_paths.py:47-48 pins the text of posttooluse_gate.py's docstring line :11 and not :12, so rewording :12 and keeping :11 verbatim breaks no test.
  - spec citation: `plugins/arch-compliance/tests/test_repo_paths.py:47-48`
- **C117** [implementability]: config/architecture/mandates.yml:60 declares fail-loud.bare-except-ok for fail-loud.bare-except; the design's handlers are `except BaseException` handlers, which _is_bare_or_exception (python_pack.py:78-82) does not flag because it matches only a bare handler or the name Exception, so they pass the gate whether or not they carry the token, and spec §6 says so.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/python_pack.py:78-82`
- **C118** [implementability]: acf/engine.py already defines contains_backslash and is stdlib-only, so adding looks_absolute, resolve_under_root and validate_posix_rel_path with `import re` and `from pathlib import Path` keeps it stdlib-only and gives validate_posix_rel_path its backslash test without a new dependency.
  - spec citation: `plugins/arch-compliance/python/acf/engine.py`
- **C119** [implementability] [load-bearing]: The new tests are implementable against the shipped files: test_builtin_detectors.py can parse the README.md detector table (:66-74) for detector ids and mandate ids and read mandate_id values from emptyCatch.ts:23 and explicitAny.ts:15; and the test_registry.py cases (a fail_loud_ratchet row declaring hook, a fail_loud_bare_except row with another id, an ast row naming an LLM prompt id, a module that raises at import not imported by load_mandates) can be expressed as inline YAML registries like the existing :24 and :35 rows.
  - spec citation: `None`
- **C120** [implementability] [load-bearing]: The contract-against-dispatch test is implementable: acf-check-diff runs in process on a temporary git repository once with --call-site ci and once with --call-site precommit, and the hook in a subprocess with .acf/enabled; a fixture tree can trigger each built-in detector the table assigns to that gate, with one active row per such detector declaring only that gate's sites.
  - spec citation: `None`
- **C121** [implementability] [load-bearing]: scan_host_guards(repo_root, changed_files, registry, file_lines, *, call_sites) is implementable in both gates: file_lines is in scope after each gate's dispatch (cli_check_diff _scan_changed returns it; _scan_paths builds it), the call can run inside _scan_changed and _scan_paths so it sits under each gate's scan try, and filling only missing keys keeps the gate's own reads.
  - spec citation: `None`
- **C122** [implementability] [load-bearing]: The required --call-site argument is implementable at cli_check_diff.py:29-71: argparse required=True with choices=sorted(DIFF_CALL_SITES) exits 2 on a missing or unknown value (SystemExit in process, so test_diff_cli asserts it with pytest.raises), sites = frozenset({args.call_site}) reaches _scan_changed and apply_registry, and the empty-selection refusal can raise AcfInputError inside the existing try at :69-74.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:29-61`
