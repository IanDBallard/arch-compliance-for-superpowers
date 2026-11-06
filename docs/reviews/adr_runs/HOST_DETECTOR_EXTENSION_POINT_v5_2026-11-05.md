# Adversarial design review — full detail

Spec: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md` @ `aac6142575d32471c0b6f419d5855985d6dcf2ac`
Kinds: defect, feature
Outcome: **BLOCKED**
Claims: 116 · Reviewers: 4 · Converged: 2

## Blocking reasons

- load-bearing claim C31 (deletion) is REFUTED: Deleting the helpers is safe: git grep finds references only at citations.py:49, :74, :161 and :163, and no test uses them. Order is preserved, and the regex change newly matches only drive-relative strings. But 'changes exactly one classification' is false. On Python 3.11 (pathlib.py:987-1005, a bundled 3.11 stdlib I opened) and on 3.12, which CI runs (ci.yml:20), a non-strict Path.resolve() raises RuntimeError on a symlink loop. So _escapes_repo raised out of resolve_citation, whereas resolve_under_root now returns None and the citation classifies 'unresolved'. Spec §4.1 itself lists 'Two behaviours change'; the claim is stale against the spec body.
- load-bearing claim C77 (sweep) is REFUTED: test_unenforced_mandate_does_not_gate writes a registry whose only row is an unenforced ast row and asserts main(...) == 0. §4.6 adds a refusal for any site that selects no active ast or guard row (AcfInputError, exit 1), and §4.7 adds a new case asserting exactly that exit 1. Adding --call-site to this call therefore turns it into exit 1, and the test fails. §4.7 lists this call only as 'passes --call-site', so the test changes do not cover every test the design breaks.
- load-bearing claim C80 (shape_fit) is REFUTED: exec_module runs arbitrary host module code with full process privileges. That code can call atexit.register, start threads, install signal or excepthook handlers, or rebind attributes of already-imported acf modules. Any of these later runs host code outside load_host_detector's and _call_host's handlers. A host generator abandoned mid-iteration (for example when _revalidate raises) is also finalized when its frame unwinds, after the try has exited. Its finally or except-GeneratorExit body then runs unwrapped and surfaces only as an unraisable warning. The handlers cover exceptions raised synchronously in their regions; they do not confine where host code runs.
- mandate claim C64 is REFUTED: The claim says every existing definition that a new definition duplicates is deleted. By the spec's own standard that is false. §4.9 (spec :506) counts `(ROOT / m.detector).is_file()` at tests/test_self_host.py:40 as a definition that file_under_root replaces. The same shape, `abs_path = repo / path; if not abs_path.is_file()`, is at cli_check_diff.py:118-119 inside _scan_changed, which the design rewrites (§4.6). It is neither switched nor listed. The doctrine's lifted text asks to 'remove legacy dependencies or non-contractual patterns in code paths you are changing'. The universal claim also has no recipe behind it, against ## No completeness claims, and it contradicts C63's own disclaimer that §4.9 is not exhaustive.
- implementability claim C111 is REFUTED: mandates.yml:60 does declare fail-loud.bare-except-ok. But the design's handlers (§4.4 items 3 and 4, and _describe) are `except BaseException as exc:`, not tuple handlers `except (Exception, SystemExit)`. The claim and spec §6's 'does not flag a tuple handler' misdescribe the design. The conclusion still holds for another reason: _is_bare_or_exception flags only a bare handler or Name 'Exception' (:78-82), and 'BaseException' is neither.
- mechanism '_describe fallback message for host exceptions whose __str__ raises' has no named producer for the state it handles (host exception exc for which f'{type(exc).__name__}: {exc}' raises) — superstition

## Absorptions

- PARTIAL_OVERLAP: 'acf.engine.file_under_root' shares responsibility 'decide that an input path names an existing regular file' with plugins/arch-compliance/python/acf/loader.py:24-28 — R = the existence decision via Path.is_file(). require_file refuses with a subject message; file_under_root adds containment and returns None. Either have require_file accept an optional root and delegate to file_under_root, or state in §5.2 why gate-owned input files keep their own check. The ratchet baseline, which §4.9 touches, should then go through one of them (ideally load_model_file) rather than a third hand-rolled loader.
- BOUNDARY_CUT: 'validate_posix_rel_path on AdrHostConfig.runs_dir / ledger_path' shares responsibility 'decide whether a host-declared ADR records path may lie outside the repository' with docs/design/ADR_GATE_HOST_CONTRACT.md:295-303 — The approved ADR contract owns this decision and says host-chosen. Either name the rejection and amend ADR_GATE_HOST_CONTRACT.md's 'Not adopted' paragraph as a recorded reversal, or drop the AdrHostConfig switch from §4.9.
- SUBSUMED: 'acf.engine.resolve_under_root (ratchet roots)' shares responsibility 'keep ratchet-scanned files under the root' with plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:59-62 — Once each roots entry is contained, the walk filter's except ValueError cannot fire. Delete the filter (keep the relative_to conversion) per Decision 8.
- SUBSUMED: 'Mandate.runs_at / MandateRegistry.active' shares responsibility 'decide whether a row runs at this Tier-1 gate' with plugins/arch-compliance/python/acf/cli_check_diff.py:94-99 — _active_mandates, the hook's three inline filters and enforcement.py:47 all call the new definition, as §4.6 and §4.5 state.
- mechanism "TS_MANDATE_IDS stamping with run-time comparison against the Node rule's mandate_id" sits at rung 3 when rung 2 applies, with no written justification

## Converged findings

- [2 reviewers: compliance, hardening] Spec section 6's Fail-loud row justifies the broad handlers as tuple handlers the bare-except detector does not flag, but section 4.4 writes them as `except BaseException`; they pass because the detector flags only a bare handler or Name 'Exception', so the stated reason is wrong.
  - evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:78-82`
- [2 reviewers: refuter, sweeper] The new refusal of a call site that selects no active ast/guard row breaks the existing test_unenforced_mandate_does_not_gate (unenforced-only registry, asserts exit 0), which section 4.7 lists only as adding --call-site.
  - evidence: `plugins/arch-compliance/tests/test_diff_cli.py:102-108`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:56-63; plugins/arch-compliance/python/acf/cli_check_diff.py:70`
- reasoning: I opened load_mandates. Line 58 skips any row whose status is not 'enforced'. Lines 60-63 raise UnknownDetectorError only for an ast/guard row whose detector is not in known_detectors. cli_check_diff.py:70 is the production caller that passes known_detectors.

#### C2 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:47; plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; plugins/arch-compliance/hooks/posttooluse_gate.py:229-236; plugins/arch-compliance/python/acf/registry.py:58`
- reasoning: apply_registry drops only 'unenforced' rows, and both gates' row filters use status != 'unenforced', so a partial row is live. registry.py:58 skips partial rows before the detector check. A partial ast/guard row naming a non-built-in detector therefore loads cleanly, and no scanner dispatches on its id. Each link of the chain holds.

#### C3 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:25; plugins/arch-compliance/python/acf/judge.py:29-36; plugins/arch-compliance/python/acf/detectors/__init__.py:28`
- reasoning: KNOWN_DETECTORS is the union of ALL_PYTHON_DETECTOR_IDS, TS_DETECTOR_IDS and LLM_PROMPT_IDS. The git grep shows only consumers and no extension. The four llm_* ids are members, so an enforced ast row naming one passes registry.py:60. No scanner in _scan_changed or _scan_paths selects on an llm_* id.

#### C4 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:112-182; plugins/arch-compliance/hooks/posttooluse_gate.py:216-294`
- reasoning: Both dispatch loops import and call only the built-in scanners, and they select rows by exact built-in ids. git grep for importlib|import_module|spec_from_file_location|exec_module over plugins/arch-compliance/python and plugins/arch-compliance/hooks printed nothing.

#### C5 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:107; plugins/arch-compliance/hooks/posttooluse_gate.py:229-236`
- reasoning: The hook calls load_mandates(mandates_path) without known_detectors, so no detector id is ever validated. _scan_paths dispatches only built-in ids, so a row naming an unknown detector silently yields no findings.

#### C6 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:106-110; plugins/arch-compliance/python/acf/exceptions.py:5; plugins/arch-compliance/python/acf/exceptions.py:13`
- reasoning: The hook catches only AcfInputError around load_mandates. UnknownDetectorError(AcfError) is a sibling of AcfInputError(AcfError), not a subclass, so it would escape uncaught.

#### C7 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:21; plugins/arch-compliance/python/acf/adr/ledger.py:42; plugins/arch-compliance/python/acf/adr/ledger.py:83; plugins/arch-compliance/python/acf/enforcement.py:47`
- reasoning: The git grep printed exactly registry.py:21 and the two surface_call_sites lines in ledger.py. The gates filter on detector and status, and apply_registry filters on status only.

#### C8 — SURVIVED
- evidence: `config/architecture/mandates.yml:70; plugins/arch-compliance/tests/fixtures/mandates_valid.yml (no-shims.hasattr call_sites [ci]); plugins/arch-compliance/hooks/posttooluse_gate.py:254; plugins/arch-compliance/tests/test_hooks.py:199-218`
- reasoning: Line 70 is 'call_sites: [ci]' on no-shims.hasattr. The hook runs scan_python_file unconditionally, and apply_registry ignores call_sites, so the WARN reaches the hook today. test_hooks.py:199-218 copies the fixture, whose hasattr row is also [ci], and asserts 'no-shims.hasattr' in additionalContext.

#### C9 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80; plugins/arch-compliance/hooks/posttooluse_gate.py:119-123; plugins/arch-compliance/python/acf/cli_check_diff.py:126; plugins/arch-compliance/python/acf/cli_check_diff.py:152; plugins/arch-compliance/hooks/posttooluse_gate.py:248-252; plugins/arch-compliance/python/acf/enforcement.py:49-50`
- reasoning: The two closures are token-identical and read only file_lines. file_lines is filled only on the .py and .ts/.tsx branches; the hook skips non-code suffixes at 248-249. A finding on any other file gets '', so token_exempted cannot match.

#### C10 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_import_graph.py:70-76; plugins/arch-compliance/hooks/posttooluse_gate.py:92-95; plugins/arch-compliance/python/acf/adr/contract.py:20; plugins/arch-compliance/python/acf/engine.py:8`
- reasoning: The test asserts only that the literal 'acf.adr' is absent from the two hook sources. The hook imports acf.enforcement and acf.registry. contract.py:20 imports acf.engine. engine.py imports only pathlib, so the helpers can live there without pulling acf.adr into the hook's import graph.

#### C11 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:214-230`
- reasoning: run_judge selects rows by detection == 'llm' (:214). It reads status == 'enforced' only to compute has_enforced for resolve_provider (:218, :224), and it reviews every llm row (:230). It does not use the Tier-1 filters.

#### C12 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:28; plugins/arch-compliance/hooks/posttooluse_gate.py:72-81; plugins/arch-compliance/hooks/posttooluse_gate.py:91-107`
- reasoning: At module scope the hook imports only stdlib modules and acf.repo. It returns 0 when .acf/enabled is absent (72-81), before the deferred imports (91-104) and before load_mandates (107).

#### C13 — SURVIVED
- evidence: `.gitignore:8; .github/workflows/ci.yml:40; plugins/arch-compliance/python/acf/cli_check_diff.py:22`
- reasoning: .gitignore:8 is '.acf/'. ci.yml:40 runs python -m acf.cli_check_diff. cli_check_diff imports MANDATES_REL, RATCHET_BASELINE_REL and resolve_repo but not ENABLED_REL, and it never checks the marker.

#### C14 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:104-105; plugins/arch-compliance/python/acf/cli_check_llm.py:54; plugins/arch-compliance/python/acf/loader.py:70-73`
- reasoning: inject_constraints catches AcfInputError around load_mandates. cli_check_llm calls load_mandates bare, so any AcfInputError already exits non-zero (as a traceback, which is existing behaviour). Without known_detectors, every new refusal is AcfInputError: a CallSite ValidationError is converted by the loader, and _row_shape raises it directly.

#### C15 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:91-92; plugins/arch-compliance/python/acf/cli_check_llm.py:10-13; plugins/arch-compliance/python/acf/judge.py:14-17`
- reasoning: inject_constraints imports acf.exceptions, acf.registry, acf.loader and acf.template. cli_check_llm imports acf.judge and acf.registry. acf.judge imports exceptions, finding, registry and template. None of these imports acf.detectors, and the spec keeps acf.registry free of acf.detectors. So neither entry point can reach load_host_detector.

#### C16 — SURVIVED
- evidence: `plugins/arch-compliance/skills/architecture-review/SKILL.md:62`
- reasoning: git ls-files plugins/arch-compliance/python/acf | grep -i review printed nothing (rc=1). config/ tracks only ARCHITECTURE.md, adr.yml and mandates.yml. architecture-review exists only as a skill whose snippet calls load_mandates directly.

#### C17 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:20; plugins/arch-compliance/python/acf/registry.py:24; hm:config/architecture/mandates.yml (git show b652fab05)`
- reasoning: Both fields are required, with no default. grep -c for 'languages' or 'arch_anchor' in HM's mandates.yml at b652fab05 printed 0; its rows carry gemini_anchor instead.

#### C18 — SURVIVED
- evidence: `hm:scripts/ci/arch_compliance/driver.py:150-163; hm:scripts/ci/arch_compliance/driver.py:92`
- reasoning: At b652fab05 the driver turns a SyntaxError into a WARN finding with exc.lineno or 0, or raises in range mode. Its facade guards read cf.content, the staged, HEAD or range blob (docstring at :92). The design does skip unparseable files and gives scan_guard no diff mode, as the spec states.

#### C19 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:198-200; plugins/arch-compliance/python/acf/cli_check_diff.py:110-127; plugins/arch-compliance/hooks/posttooluse_gate.py:238-254`
- reasoning: The rule text matches. The two loops do differ: the diff gate uses changed_files and added_lines, while the hook uses edited paths with added_lines=None and also collects rel_paths for out-of-repo paths. Under the design both gates call the same two host runners.

#### C20 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:50-53; plugins/arch-compliance/python/acf/detectors/fsm_guard.py:36-39; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:23-26`
- reasoning: Each wraps ast.parse in try/except SyntaxError and returns [] (0 in the ratchet).

#### C21 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:104; plugins/arch-compliance/skills/acf-mandate/SKILL.md:95; plugins/arch-compliance/tests/test_registry.py:30; tests/test_self_host.py:23`
- reasoning: The recipe printed exactly the listed callers, plus the prose hit at SKILL.md:141. Only cli_check_diff:70, SKILL.md:95, test_profile_drift:24, test_registry:30 and test_self_host:23 pass known_detectors.

#### C22 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:125; plugins/arch-compliance/python/acf/cli_check_diff.py:82; plugins/arch-compliance/tests/test_enforcement.py:54`
- reasoning: git grep 'apply_registry(' -- '*.py' printed the two gates plus test_enforcement at 54, 60, 66, 72, 84, 94, 104, 110, 125 and 130, besides the definition.

#### C23 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; plugins/arch-compliance/hooks/posttooluse_gate.py:231; plugins/arch-compliance/hooks/posttooluse_gate.py:285; plugins/arch-compliance/python/acf/enforcement.py:47; plugins/arch-compliance/hooks/inject_constraints.py:158`
- reasoning: Both recipes printed exactly the listed sites. The wider .status recipe added only registry.py:58, judge.py:218 and the display read at inject_constraints.py:158.

#### C24 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/build_artifacts.py:31; plugins/arch-compliance/python/acf/detectors/python_pack.py:67; plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23; plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15; plugins/arch-compliance/python/acf/enforcement.py:46`
- reasoning: Each detector constructs its Finding with one literal mandate_id: one per scanner, and one per detector in python_pack. apply_registry looks up by_id.get(finding.mandate_id), so a row with a different id never matches.

#### C25 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:168-182; plugins/arch-compliance/hooks/posttooluse_gate.py:216-223; plugins/arch-compliance/hooks/posttooluse_gate.py:254; plugins/arch-compliance/hooks/posttooluse_gate.py:279-282; plugins/arch-compliance/hooks/posttooluse_gate.py:284-294`
- reasoning: The hook imports no ratchet. python_pack, TypeScript, facade, FSM and build-artifact all run in both gates, at the lines given in the section 4.3 table.

#### C26 — SURVIVED
- evidence: `config/architecture/mandates.yml:70; plugins/arch-compliance/tests/test_diff_cli.py:72-82; plugins/arch-compliance/tests/test_registry.py:24-25; plugins/arch-compliance/tests/test_hooks.py:223-226; plugins/arch-compliance/tests/test_judge.py:390-394`
- reasoning: I loaded every shipped and fixture registry with yaml and printed id, detector, status, call_sites and languages. Every active ast/guard row has a built-in detector, an id equal to its stamped mandate_id, and call_sites within ci/hook. The only ratchet rows are unenforced. No row carries ':' or is a partial ast/guard row. The inline test rows are clean ([ci, hook] bare-except; manual [audit]; llm unenforced), and test_hooks only flips enforced to unenforced. not_a_real_detector is the one refusal, and it is intended.

#### C27 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/loader.py:70-73; plugins/arch-compliance/python/acf/registry.py:33-41; plugins/arch-compliance/tests/test_registry.py:46-47; plugins/arch-compliance/tests/test_enforcement.py:19-30`
- reasoning: The loader converts only ValidationError. A probe with pydantic 2.13.3 showed a custom Exception raised in a mode='after' model_validator propagating with its own type through both model_validate and direct construction; test_registry:46 relies on this for _unique_ids. The direct constructions are an ast row with built-in detector empty_catch and call_sites [ci] (test_enforcement:19), and llm rows (test_judge:41, test_template:73). None is refused.

#### C28 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:91-112; plugins/arch-compliance/tests/test_profile_drift.py:7; tests/test_self_host.py:14; config/architecture/ARCHITECTURE.md:228`
- reasoning: Each user imports the name from acf.cli_check_diff, passes it as known_detectors, sorts it (sorted over a Mapping yields keys) or names it in prose. All keep working with a re-exported Mapping. test_registry.py:30's frozenset has no .get, and §4.7 changes it.

#### C29 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:63; plugins/arch-compliance/hooks/posttooluse_gate.py:65; plugins/arch-compliance/hooks/hooks.json`
- reasoning: acf-check-diff resolves one repo per invocation. The hook resolves one repo in a fresh 'python posttooluse_gate.py' process per edit, per hooks.json.

#### C30 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:16-22; plugins/arch-compliance/python/acf/detectors/__init__.py:11-18; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:14; plugins/arch-compliance/python/acf/judge.py:29-36`
- reasoning: 3 python_pack ids, 4 guard ids (the CONFIG_AST ids are a subset) and 2 TypeScript ids make 9; adding 4 LLM ids gives 13.

#### C31 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/adr/citations.py:74-76; plugins/arch-compliance/python/acf/adr/citations.py:161-163; C:/Program Files/KiCad/9.0/bin/Lib/pathlib.py:987-1005; .github/workflows/ci.yml:20`
- reasoning: Deleting the helpers is safe: git grep finds references only at citations.py:49, :74, :161 and :163, and no test uses them. Order is preserved, and the regex change newly matches only drive-relative strings. But 'changes exactly one classification' is false. On Python 3.11 (pathlib.py:987-1005, a bundled 3.11 stdlib I opened) and on 3.12, which CI runs (ci.yml:20), a non-strict Path.resolve() raises RuntimeError on a symlink loop. So _escapes_repo raised out of resolve_citation, whereas resolve_under_root now returns None and the citation classifies 'unresolved'. Spec §4.1 itself lists 'Two behaviours change'; the claim is stale against the spec body.

#### C32 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; plugins/arch-compliance/hooks/posttooluse_gate.py:229-236; config/architecture/mandates.yml:70; plugins/arch-compliance/profiles/python-service/mandates.yml:18`
- reasoning: runs_at is the old status != 'unenforced' test plus a call_sites intersection. In every shipped registry, each active ast/guard row declares [ci, hook] except no-shims.hasattr, which declares [ci]; facade, FSM and ratchet rows are unenforced. With precommit added, diff-gate selection is unchanged, and the hook loses only hasattr.

#### C33 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:60; plugins/arch-compliance/python/acf/cli_check_diff.py:21; plugins/arch-compliance/python/acf/cli_check_diff.py:25`
- reasoning: known_detectors is consulted only inside the ast/guard condition. The consumer census shows no code reading KNOWN_DETECTORS for llm rows. The :21 import is used today only at :25, and the design moves it to the llm_prompt_ids argument.

#### C34 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_repo_paths.py:17-25; plugins/arch-compliance/python/acf/detectors/python_pack.py:67`
- reasoning: A constant holding the same string yields an identical Finding. I grepped the tests for getsource, scanner filenames and source reads. The only test that reads source is test_repo_paths, which scans tracked python/hooks files for a 'config…architecture' spelling, and that pattern is unaffected by mandate-id constants.

#### C35 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:29-36; config/architecture/mandates.yml:45; plugins/arch-compliance/skills/acf-mandate/SKILL.md:56; plugins/arch-compliance/skills/acf-mandate/SKILL.md:121`
- reasoning: The yaml dump shows llm rows only with llm_react_boundaries and llm_fail_loud (the config registry, both profiles), and both are in LLM_PROMPT_IDS. The fixture and the test_diff_cli rows have no llm rows, and test_judge:390 is unenforced. SKILL.md:56 and :121 state the prompt-id rule.

#### C36 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:69-74; plugins/arch-compliance/python/acf/exceptions.py:13`
- reasoning: getattr's default suppresses only AttributeError, by Python semantics. The spec's handler is broader than the claim says: BaseException minus KeyboardInterrupt, not (Exception, SystemExit). It still catches both, so every conclusion holds. The UnknownDetectorError raised at dispatch sits inside _scan_changed, within the try at :69-74 whose :72 tuple lists UnknownDetectorError. A failed exec_module leaves _MODULE_CACHE unset, so the 'is not mod' check pops sys.modules. A failed lookup on a cached module leaves it cached.

#### C37 — SURVIVED
- evidence: `pyproject.toml:5; C:/Program Files/KiCad/9.0/bin/Lib/pathlib.py:987-1005; C:/Python313/Lib/pathlib/_local.py:664-670`
- reasoning: requires-python is >=3.11. The 3.11 pathlib's resolve(strict=False) calls stat() and turns ELOOP (or winerror 1921) into RuntimeError. The 3.13 resolve is a bare os.path.realpath and does not raise. Mapping RuntimeError to None feeds the None branches the spec gives for load, guard lines and citations.

#### C38 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:82-95; plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23-28; plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15-21`
- reasoning: Finding construction sits in a try whose except (KeyError, TypeError, ValueError) re-raises DetectorPackError. A dict lookup on an unknown detector gives KeyError, and a raised ValueError on mismatch is caught too. The Node rules emit empty_catch/fail-loud.empty-catch and explicit_any/no-shims.explicit-any, equal to the proposed TS_MANDATE_IDS.

#### C39 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80; plugins/arch-compliance/hooks/posttooluse_gate.py:119-123; plugins/arch-compliance/python/acf/enforcement.py:49-50`
- reasoning: make_line_lookup as specified is the closures' exact body over the same mapping and does no I/O. Only scan_host_guards adds entries, so exemption results for built-in findings change only on files a host guard flagged.

#### C40 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:22-28; plugins/arch-compliance/hooks/hooks.json; pyproject.toml:19-20; .github/workflows/ci.yml:40; hm:scripts/ci/metadata_facade_guard.py:66`
- reasoning: The hook runs as 'python <plugin>/hooks/posttooluse_gate.py', so sys.path[0] is the hooks dir, and it inserts python/ at index 0 before importing acf.repo. The console script's sys.path[0] is the script directory. CI runs 'python -m' from the repo root, so cwd is first. HM :66 imports 'from scripts.ci.arch_compliance.facade_sinks'; HM tracks scripts/__init__.py, so it is a regular package that resolves from the host root.

#### C41 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:29-61; hm:scripts/ci/run_guards.py:107-111; hm:scripts/ci/run_guards.py:116; hm:scripts/ci/run_guards.py:126-130; hm:scripts/ci/run_guards.py:317-321`
- reasoning: acf-check-diff offers only --mode, --base, --repo, --mandates and --json. At b652fab05, run_guards refuses an unknown site (107-111), filters rows by site (116), refuses an empty selection (126-130), and defaults --site to ci (317-321).

#### C42 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:135; plugins/arch-compliance/python/acf/detectors/build_artifacts.py:27-34; plugins/arch-compliance/python/acf/cli_check_diff.py:124-126`
- reasoning: Both built-ins report line 1. file_lines holds only changed .py/.ts/.tsx files. A staged dist/x.py takes the .py branch, so its lines are read today under the key 'dist/x.py', which equals the build-artifact finding's path after lstrip.

#### C43 — SURVIVED
- evidence: `config/architecture/mandates.yml:11; plugins/arch-compliance/profiles/python-service/mandates.yml:18; plugins/arch-compliance/tests/fixtures/mandates_valid.yml`
- reasoning: git grep precommit over *.yml and *.yaml printed nothing. My yaml census counts ast/guard rows declaring ci as 9, 7 (python-service), 3 (react-app) and 3 (fixture). Today acf-check-diff runs every active row regardless of call_sites, and every shipped active ast/guard row declares ci, so after precommit is added the precommit selection is identical. This holds for shipped files only; see the unanchored finding on installed host copies.

#### C44 — SURVIVED
- evidence: `pyproject.toml:7; plugins/arch-compliance/python/acf/registry.py:5`
- reasoning: I probed pydantic 2.13.3, the installed version. A model with an AfterValidator str, an int with ge=1 and a str field yields exact str and int after normal validation from a str subclass, a str-Enum, True, an int subclass, an IntEnum and 2.0. So a genuine hit passes the exact-type checks. type(True) is int and type(b'') is str are False, so model_construct or mutated hits are refused before lax coercion. I probed only 2.13.3, while pyproject allows >=2.0.

#### C45 — SURVIVED
- evidence: `C:/Program Files/KiCad/9.0/bin/Lib/pathlib.py:1261-1273; C:/Python313/Lib/pathlib/_abc.py:31-40; C:/Python313/Lib/pathlib/_abc.py:476-488`
- reasoning: In 3.11 and 3.13, is_file ignores ENOENT, ENOTDIR, EBADF, ELOOP and three winerrors, returns False for directories, and re-raises other OSErrors such as EACCES. Combined with resolve_under_root's None for out-of-root paths and loops, file_under_root behaves as stated. Each spec caller wraps it in except OSError and raises a typed error.

#### C46 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/host.py:24-32; config/architecture/adr.yml:1-2; hm:config/architecture/adr.yml (git show b652fab05); plugins/arch-compliance/tests/test_adr_host.py:11; plugins/arch-compliance/tests/test_adr_host_acceptance.py:31; plugins/arch-compliance/python/acf/loader.py:74-77`
- reasoning: Both adr.yml files declare docs/reviews/adr_runs and docs/reviews/adversarial_design_ledger.jsonl, and the tests use reviews/runs and reviews/ledger.jsonl; all are valid relative POSIX paths. An AfterValidator ValueError becomes a ValidationError, which the loader reports as 'invalid ADR host config'.

#### C47 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:46; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:122-124; config/architecture/mandates.yml:97-98; plugins/arch-compliance/profiles/python-service/mandates.yml:58-59; plugins/arch-compliance/python/acf/repo.py:26; plugins/arch-compliance/tests/test_portable_guards.py:107; plugins/arch-compliance/python/acf/cli_check_diff.py:72`
- reasoning: The shipped baseline is a relative path, roots ['.'] resolves to the root itself, RATCHET_BASELINE_REL is relative, and roots=['pkg'] resolves under tmp_path. A missing baseline already raises DetectorPackError at :78, and :72 catches DetectorPackError.

#### C48 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/__init__.py:9-34; plugins/arch-compliance/python/acf/detectors/python_pack.py:16; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:14; plugins/arch-compliance/tests/test_typescript_pack.py:6; plugins/arch-compliance/tests/test_typescript_pack.py:14`
- reasoning: git grep '_DETECTOR_IDS' -- plugins tests printed exactly the spec's list, and each hit is rewritten in §4.3, §4.7 or §4.9. TS_MANDATE_IDS is keyed by TS detector ids but is the source KNOWN_DETECTORS is built from, not a parallel set.

#### C49 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/facade_sinks.py:24-25; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:46; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:88-90; plugins/arch-compliance/python/acf/detectors/build_artifacts.py:16; plugins/arch-compliance/python/acf/detectors/build_artifacts.py:23; plugins/arch-compliance/python/acf/cli_check_diff.py:135-164`
- reasoning: The call is not literally identical (raw values replace list()/bool()), but the behaviour is equal. The scanner applies 'allowlist_globs or []', truthiness for atomic_is_sink, and 'path_prefixes or default' plus iteration. Absent keys fall back to defaults (None, True, None) equivalent to what the gates pass today. A present null, a string or a non-iterable behaves identically, including raising the same TypeError.

#### C50 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:23-26`
- reasoning: git grep 'ast.parse|SyntaxError|compile(' over python and hooks printed only the four scanner sites. parse_python catches the same SyntaxError, so the output is identical; ValueError from null bytes on 3.11 propagates in both old and new code.

### Unanchored findings

- **important**: Under §4.6, a registry whose ast/guard rows are all unenforced is refused ('selects no active ast or guard mandate', exit 1). test_unenforced_mandate_does_not_gate writes only an unenforced bare-except row and asserts exit 0, yet §4.7 only adds --call-site to it, so the design breaks a test its definition of done requires to pass.
  - evidence: `plugins/arch-compliance/tests/test_diff_cli.py:102-108`
- **important**: Hosts installed by /acf-setup hold copies of the profile registries made before this change, with no 'precommit' site. After upgrading, the documented pre-commit invocation 'acf-check-diff --call-site precommit' selects no row and is refused (exit 1) on every commit. Decision 2 lists only the CLI flag as the migration and says pre-commit behaviour is unchanged, which holds only for the shipped profile files.
  - evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:101`
- **advisory**: The claim C36 cites describes §4.4 item 3's handler as catching (Exception, SystemExit), but the spec code catches BaseException minus KeyboardInterrupt. The claim text and the spec disagree, harmlessly.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:72`
- **advisory**: _revalidate assumes normal pydantic validation always yields exact str and int, which I confirmed only on pydantic 2.13.3. pyproject admits pydantic>=2.0, and nothing pins the behaviour on older 2.x releases.
  - evidence: `pyproject.toml:7`

### Looked for but did not find

- any importlib/import_module/spec_from_file_location/exec_module use in plugins/arch-compliance/python or hooks
- any reference to _looks_absolute or _escapes_repo outside citations.py:49,74,161,163 in *.py
- any test reading scanner source text (getsource, scanner filenames, detector-path read_text) that a mandate-id constant would break
- any shipped, fixture or inline-test ast/guard row that is partial, uses a ':' host reference, lacks a Tier-1 site while active, or whose id differs from its detector's stamped mandate_id
- any 'precommit' value in tracked *.yml or *.yaml files
- any second SyntaxError-skipping ast.parse site in plugins/arch-compliance/python beyond the four scanners
- any HistoricMansions call_sites value outside ci/precommit/posttooluse/audit at b652fab05
- any acf-check-diff reference to ENABLED_REL or .acf/enabled

## compliance

### Claim verdicts

#### C51 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:29-30; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:360-367; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:94-95; plugins/arch-compliance/python/acf/cli_check_diff.py:69-74`
- reasoning: The doctrine forbids broad handlers that swallow errors unless they are exempted with a reason. The loader and _call_host handlers catch BaseException, re-raise KeyboardInterrupt, and raise UnknownDetectorError or DetectorPackError otherwise. The TypeScript KeyError and ValueError paths reach the existing except tuple, which already raises DetectorPackError. The acf-check-diff try already lists AcfInputError, UnknownDetectorError and DetectorPackError. Each invalid state in §6.1 has a typed refusal. One part of the wording is inaccurate: _describe's handler (spec :401) returns a fallback string rather than re-raising. It swallows only the secondary __str__ failure, the primary error is still raised as a typed error, and the handler carries the exemption token with a reason, so the mandate is met (see the advisory finding).

#### C52 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:286-302; plugins/arch-compliance/python/acf/enforcement.py:46; plugins/arch-compliance/python/acf/cli_check_diff.py:168-182`
- reasoning: apply_registry matches findings to rows by the stamped mandate_id (enforcement.py:46), and the ratchet runs only in acf-check-diff (cli_check_diff.py:168). _check_builtin refuses three things: an id not in KNOWN_DETECTORS (prompt ids are not keys), a row id that differs from contract.mandate_id, and any Tier-1 site outside contract.call_sites (fail_loud_ratchet is DIFF only). _row_shape (spec :204-223) refuses an active ast/guard row with no Tier-1 site. Built-in scanners ignore languages. I found no remaining case where an active built-in row passes load and never receives a finding.

#### C53 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:120-133; plugins/arch-compliance/python/acf/repo.py:32-44; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:265-269`
- reasoning: The section says no default stands in for a missing declaration, and it records resolve_repo's cwd fallback as outside the rule (repo.py:32-44). load_mandates does not derive repo_root: an active host row with repo_root=None raises AcfInputError (spec :265-269). apply_registry's call_sites keyword has no default, and --call-site is required=True. The repo that callers pass comes from resolve_repo, whose fallback the doctrine already records.

#### C54 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:48-49; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:359-369`
- reasoning: The doctrine says not to probe with hasattr to paper over missing interfaces. The design looks up the callable with getattr(mod, attr, None) inside the wrapped region (spec :359), then a non-callable raises UnknownDetectorError (:368-369). The design adds no hasattr. Load, call and result failures all raise typed errors.

#### C55 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:57-64; plugins/arch-compliance/python/acf/engine.py:17-24; plugins/arch-compliance/python/acf/cli_check_diff.py:84-85; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:330`
- reasoning: Host finding paths reach JSON through --json (cli_check_diff.py:84-85). HostHit.path goes through validate_posix_rel_path, which calls contains_backslash (engine.py:17-24), so it refuses a backslash rather than normalising it. That matches the doctrine's stricter stance at :62-64. The design's messages use .as_posix() or rel_path strings that are already validated.

#### C56 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:101-102; plugins/arch-compliance/python/acf/exceptions.py:1-14; plugins/arch-compliance/python/acf/exceptions.py:29`
- reasoning: AcfInputError (:5), UnknownDetectorError (:13) and DetectorPackError (:29) each subclass AcfError and nothing else. §4.2–§4.4 raise only these. The internal ImportError and TypeError are raised inside wrapped regions and leave them as typed ACF errors. The design defines no new exception class.

#### C57 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:107-110; plugins/arch-compliance/python/acf/repo.py:15; plugins/arch-compliance/python/acf/registry.py:1-7`
- reasoning: acf.repo declares MANDATES_REL (repo.py:15). registry.py and engine.py spell no config/architecture path today, and the design adds none to them, to detectors/__init__.py or to the new host.py. The rewritten acf-mandate snippet takes resolve_repo and MANDATES_REL from acf.repo.

#### C58 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:137-143; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:180-190`
- reasoning: None of the runtime messages in §4.2–§4.4 (for example the host-reference message at spec :180-190 and the loader and _call_host messages) names HistoricMansions or any host path. The §4.8 prose edits describe call sites, contracts and the trust boundary in generic terms. The origin-host rationale for the posttooluse spelling stays in the spec, not in the prose.

#### C59 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:155-157; plugins/arch-compliance/python/acf/cli_check_diff.py:21; plugins/arch-compliance/python/acf/detectors/__init__.py:30-35; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:604-629`
- reasoning: Each export in §6.2 names a package or hook caller, not a test. LLM_PROMPT_IDS keeps cli_check_diff (which already imports it at :21) as its runtime consumer through llm_prompt_ids. Deleting the five sets leaves detectors/__init__.py's __all__ (:30-35) to be replaced by KNOWN_DETECTORS. The *_DETECTOR_ID constants those sets used stay live in both gates.

#### C60 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:161-164; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:642-658`
- reasoning: The census claims in §1, §2 and §3 carry grep or python recipes, and the Appendix (spec :642-658) holds the receipts. One quantifier has no recipe: the §4.8 row '--call-site at every shipped or documented invocation'. I grepped it myself and the listed sites match every non-plan invocation (ci.yml:40, README.md:57-58, acf-setup SKILL.md:184/193/206/207/217/219, CLAUDE.md:36, SUPERPOWERS_COMPLEMENT.md:82-83). A missed site would fail loud with exit 2, so the claim is not load-bearing. Note that the doctrine names only a recipe, not a per-item table, as backing for a quantifier.

#### C61 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:173-175; plugins/arch-compliance/python/acf/cli_check_diff.py:152; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:411`
- reasoning: The rule requires a declared encoding on subprocess text calls and file reads. The TS-branch read already declares utf-8 (cli_check_diff.py:152), and the design keeps it while binding text. scan_host_guards declares encoding='utf-8'. errors='replace' does not affect the declared encoding, and the design adds no subprocess.

#### C62 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:186-187; pyproject.toml:3; plugins/arch-compliance/.claude-plugin/plugin.json:3`
- reasoning: A change to skill prose bumps both files. Both read 0.2.2 today, §4.8 bumps both to 0.2.3, and §4.8 changes the acf-mandate and acf-setup SKILL.md files.

#### C63 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:198-200; plugins/arch-compliance/python/acf/cli_check_diff.py:76-80; plugins/arch-compliance/hooks/posttooluse_gate.py:119-123`
- reasoning: The two _line_lookup closures are token-identical and are replaced by make_line_lookup. The other §4.9 items exist at the cited sites (citations.py:49/:74, detectors/__init__.py:11-28, python_pack.py:16, typescript_bridge.py:14, the four ast.parse sites). The scanners' signature defaults (facade_sinks.py:24-25) become the one default once the inline True/[] fallbacks go. The claim explicitly does not say §4.9 is exhaustive, so the leftover join-and-is_file at cli_check_diff.py:118-119 (see C64) does not refute it.

#### C64 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:118-119; tests/test_self_host.py:40; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:506`
- reasoning: The claim says every existing definition that a new definition duplicates is deleted. By the spec's own standard that is false. §4.9 (spec :506) counts `(ROOT / m.detector).is_file()` at tests/test_self_host.py:40 as a definition that file_under_root replaces. The same shape, `abs_path = repo / path; if not abs_path.is_file()`, is at cli_check_diff.py:118-119 inside _scan_changed, which the design rewrites (§4.6). It is neither switched nor listed. The doctrine's lifted text asks to 'remove legacy dependencies or non-contractual patterns in code paths you are changing'. The universal claim also has no recipe behind it, against ## No completeness claims, and it contradicts C63's own disclaimer that §4.9 is not exhaustive.

#### C65 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:147-148; plugins/arch-compliance/python/acf/adr/ledger.py:75-76`
- reasoning: The rule covers LedgerRow and LedgerAmendment fields. No item in §3's scope touches acf/adr/ledger.py. The one acf.adr model change is AdrHostConfig.runs_dir/ledger_path (adr/host.py:24-25), which is the host config, not a ledger model.

#### C66 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:47-50; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:123-125; plugins/arch-compliance/python/acf/registry.py:21`
- reasoning: Principle 1 (typed errors, no silent load defaults) is met by the §6.1 refusals. Principle 2 (one finding schema) holds because HostHit is turned into a Finding by the runner. Principle 3 holds through validated POSIX paths. Principle 4 says call sites must agree with the registry, and call_sites is now read where it was declared and never read (registry.py:21). Host ast/guard callables in Python and TypeScript provide the extension points that :123 and :125 call for.

#### C67 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:49-51; plugins/arch-compliance/python/acf/cli_check_diff.py:69-74; plugins/arch-compliance/hooks/posttooluse_gate.py:113-117`
- reasoning: A path that file_under_root cannot resolve maps to [], so the lookup returns '' and token_exempted finds no token. The finding is kept (enforcement.py:49-51), which is fail-safe, not a hidden failure. An OSError becomes DetectorPackError inside each gate's scan try, which catches DetectorPackError at cli_check_diff.py:72 and posttooluse_gate.py:115. make_line_lookup only indexes a mapping.

### Unanchored findings

- **advisory**: §6's Fail-loud row justifies the token by saying the detector 'does not flag a tuple handler', but the new handlers are `except BaseException`, not tuples. The detector misses them because it matches only bare `except:` and `except Exception`. Also, _describe's handler returns a fallback string, so C51's 'every broad handler re-raises' wording is inaccurate.
  - evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:77-82`
- **advisory**: The new llm prompt-id refusal is wired only into acf-check-diff and the acf-mandate snippet. acf-check-llm, the only command that runs llm rows, still loads without llm_prompt_ids, and run_judge accepts any detector string, so an unknown prompt id still runs silently at Tier 2.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_llm.py:54`
- **advisory**: HOOK_CALL_SITES makes 'hook' and 'posttooluse' synonyms so this repository's rows and the origin host's spelling both route to the hook. That is a vocabulary alias over a misalignment between the parent spec (:104 lists posttooluse) and the shipped rows (hook), and the spec does not weigh it against ## No shims or ## Single point of definition.
  - evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:104`
- **advisory**: The §4.8 list of acf-check-diff invocations that must add --call-site is stated as 'every shipped or documented invocation' with no recipe. A grep confirms the list is complete today, but ## No completeness claims asks for the recipe.
  - evidence: `config/architecture/ARCHITECTURE.md:161-164`

### Looked for but did not find

- ## Build artifacts: the design only moves the build-artifact params extraction into build_artifact_args with the same defaults; the guard's behaviour is unchanged. Not touched.
- ## Fail-loud ratchet: the shipped baseline/roots values (mandates.yml:97-98) pass the new resolve_under_root checks, and the DIFF-only contract matches cli_check_diff.py:168. The doctrine text is not contradicted.
- ## Façade sinks / ## FSM transitions: an empty required param still reaches the scanners' DetectorPackError (facade_sinks.py:32-37, fsm_guard.py:29-34), so the '' default fails loud. Shipped row ids equal the stamped ids.
- ## Soft fail-loud smells / ## React boundaries: the shipped llm rows name ids in LLM_PROMPT_IDS (judge.py:29-36). Tier-2 behaviour is unchanged.
- ## Post-merge: the design declares no host operational values. Not touched.
- High-frequency misses: no new exception class or stdlib mixin, no new subprocess, and no host name in the runtime messages. The package checks are still consumed (acf.cli_check_diff.KNOWN_DETECTORS is re-exported, so ARCHITECTURE.md:228 stays valid).
- unstated_mandates is empty: every doctrine section this design touches is named in its Governing mandates header and §6 table.

## sweeper

### Claim verdicts

#### C68 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; plugins/arch-compliance/hooks/posttooluse_gate.py:229-236; plugins/arch-compliance/hooks/posttooluse_gate.py:284-286; plugins/arch-compliance/python/acf/enforcement.py:47; plugins/arch-compliance/hooks/inject_constraints.py:158; plugins/arch-compliance/python/acf/judge.py:218`
- reasoning: I searched the plugin's Python, hooks and skills for status-based row filters (`unenforced`, `.status`, `enforced"`). The Tier-1 hits are exactly the four sites the spec replaces: cli_check_diff._active_mandates, the hook's three inline filters, and apply_registry. The remaining hits are of other kinds. inject_constraints.py:158 only displays the status. judge.py:218 is Tier-2, which the spec scopes out. registry.py:58 is the load check, which becomes is_active rather than a per-gate filter. The skill's status mentions are prose. No other Tier-1 active-row filter exists.

#### C69 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/citations.py:49-51; plugins/arch-compliance/python/acf/adr/citations.py:74-76; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:46; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:122-124; tests/test_self_host.py:40; plugins/arch-compliance/python/acf/detectors/python_pack.py:35`
- reasoning: I grepped the tree for is_relative_to, relative_to(, is_absolute(, drive-regex and `..` tests. The string absolute/escape tests live only at citations.py:49 and :74 and in the ratchet's hand join at fail_loud_ratchet.py:123. posttooluse_gate.py:204 calls is_absolute on a path resolved for I/O, which the spec keeps. contract.py:95 `_WIN_DRIVE_RE` scans text, so it is a different job. The registry- or host-supplied path existence checks are test_self_host.py:40, fail_loud_ratchet.py:78 and the new sites. A grep for `ast.parse` + `except SyntaxError` outside tests and docs finds exactly the four scanners. Caveat: acf.loader.require_file (loader.py:24-28) is a separate absent-file check for gate-owned input files; it is not registry-supplied, so it sits outside the claim's population (see relationships).

#### C70 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:66-73; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:84-92`
- reasoning: The bridge decodes raw subprocess stdout as JSON (:66-73), then coerces severity, path, line and message out of untyped dicts (:84-92). The host runner receives typed HostHit objects and takes mandate_id and severity from the row. The only thing the two share is the Finding constructor call, so ADJACENT holds.

#### C71 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:241-245; plugins/arch-compliance/python/acf/judge.py:249-250`
- reasoning: Opened judge.py:238-255. The judge demotes BLOCK to WARN on its own verdict or confidence (:241-245). It admits path `<diff>` and line 0 (:249-250) and takes mandate_id from the provider's result, not the row. Host findings take everything identity-bearing from the row and require line >= 1. The overlap is only the constructor call.

#### C72 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:22-26; plugins/arch-compliance/hooks/inject_constraints.py:28-29; tests/test_check_installed_skills.py:15-18`
- reasoning: I grepped everything outside docs/ for importlib, import_module, spec_from_file_location, exec_module, runpy, __import__, exec( and sys.path.insert/append. No plugin code loads a module from a registry-supplied path. The one file-path loader in the tree is the repo-level test tests/test_check_installed_skills.py:15-18, which loads a fixed in-repo script and is test-only. The only sys.path mutations are the two hook start-up inserts of the plugin's own python/ directory. The new loader appends one host root, so ADJACENT is fair.

#### C73 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80; plugins/arch-compliance/hooks/posttooluse_gate.py:119-123`
- reasoning: I grepped for LineLookup, line_lookup, `lines[line - 1]` and splitlines()[ across the tree, docs excluded. Only the two gate closures are passed to apply_registry. cli_check_llm.py and the judge pass none. Tests use local helpers (_no_lines, lines). fsm_guard.py:56 indexes lines for a message snippet, which is not a LineLookup.

#### C74 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:95; plugins/arch-compliance/tests/test_profile_drift.py:24; plugins/arch-compliance/skills/architecture-review/SKILL.md:62; plugins/arch-compliance/skills/acf-setup/SKILL.md:224`
- reasoning: Each of the four candidate validators consumes load_mandates rather than re-implementing the check. The acf-mandate snippet and test_profile_drift call it with known_detectors. architecture-review calls it without. acf-setup only states the expected exception names. None checks detector ids or call sites independently.

#### C75 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:242-246; plugins/arch-compliance/hooks/posttooluse_gate.py:290-293`
- reasoning: The try/except ValueError already separates in-repo from out-of-repo paths (:242-245). rel_paths (:246) is consumed only by the build-artifact guard (:290-293). Recording a parallel in_repo list at that branch adds no second containment test.

#### C76 — SURVIVED
- evidence: `config/architecture/mandates.yml:70; plugins/arch-compliance/profiles/python-service/mandates.yml:18; C:/Users/iball/Arduino/Projects/HistoricMansions/config/architecture/mandates.yml:11; C:/Users/iball/Arduino/Projects/HistoricMansions/config/architecture/mandates.yml:246; C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/run_guards.py:116`
- reasoning: I listed every call_sites value in tracked YAML here (ci, hook, audit) and in the origin host's 48 rows (precommit, posttooluse, ci, audit). The test literals hold ci, hook, audit and []. All fall inside the five-value CallSite. In this repo, every active ast/guard row declares ci, which DIFF_CALL_SITES serves. No Tier-1 set contains audit.

#### C77 — REFUTED
- evidence: `plugins/arch-compliance/tests/test_diff_cli.py:102-108`
- reasoning: test_unenforced_mandate_does_not_gate writes a registry whose only row is an unenforced ast row and asserts main(...) == 0. §4.6 adds a refusal for any site that selects no active ast or guard row (AcfInputError, exit 1), and §4.7 adds a new case asserting exactly that exit 1. Adding --call-site to this call therefore turns it into exit 1, and the test fails. §4.7 lists this call only as 'passes --call-site', so the test changes do not cover every test the design breaks.

#### C78 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:168-182; plugins/arch-compliance/hooks/posttooluse_gate.py:284-295; plugins/arch-compliance/python/acf/enforcement.py:46-47`
- reasoning: Today's dispatch matches the proposed table: the ratchet runs only in the diff gate (cli_check_diff.py:168-182), and the hook's _scan_paths has no ratchet call. In the reverse drift, a gate runs a detector whose contract excludes that site. A finding from it can only attach to a row declaring the site, and _check_builtin refuses such a row at load. Any other row is dropped by the call_sites filter added at the existing by-id sink (enforcement.py:46-47). The drift therefore over-refuses at load and never silently loses a declared row.

#### C79 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:242-245; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:59-62; plugins/arch-compliance/python/acf/adr/citations.py:74-76`
- reasoning: resolve_under_root's model is citations.py:74-76: it turns a string into a resolved, contained Path. The hook and ratchet sites go the other way, from a Path to a relative string or a skip. They share only the one-line containment predicate, so ADJACENT is defensible. Side effect: once each `roots` entry is contained by resolve_under_root, rglob children are lexically under the root, and the walk filter's except ValueError at :59-62 can no longer fire (see unanchored finding).

#### C80 — REFUTED
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:357`
- reasoning: exec_module runs arbitrary host module code with full process privileges. That code can call atexit.register, start threads, install signal or excepthook handlers, or rebind attributes of already-imported acf modules. Any of these later runs host code outside load_host_detector's and _call_host's handlers. A host generator abandoned mid-iteration (for example when _revalidate raises) is also finalized when its frame unwinds, after the try has exited. Its finally or except-GeneratorExit body then runs unwrapped and surfaces only as an unraisable warning. The handlers cover exceptions raised synchronously in their regions; they do not confine where host code runs.

#### C81 — REFUTED
- evidence: `docs/design/ADR_GATE_HOST_CONTRACT.md:295-303`
- reasoning: I redid the doc sweep by behaviour. §4.8 updates ADR_GATE_HOST_CONTRACT.md:262 and rewrites the citation at :302-303. The paragraph containing that citation, :295-301 ('Not adopted: a refusal of absolute paths or `..` segments in the two fields ... a visible host choice, not a state the gate must prevent'), is exactly what §4.9 now adopts. It is neither listed nor reversed, so the edited doc ends up contradicting itself. Minor: docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:531 is another documented `acf.cli_check_diff` invocation the list does not name. It belongs to the same past-run category as the two specs exempted by name.

#### C82 — SURVIVED
- evidence: `plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23; plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:85`
- reasoning: I grepped for both literals across .py/.ts/.tsx under plugins/. The non-test runtime spellings are the two Node rule files and scan.ts self-test lines. In Python the only runtime handling is the bridge copying item['mandate_id'] (:85), which the design replaces with the TS_MANDATE_IDS lookup. Every Python hit is in tests (test_baseline, test_enforcement, test_typescript_pack).

#### C83 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:52; plugins/arch-compliance/python/acf/cli_check_diff.py:82; plugins/arch-compliance/hooks/posttooluse_gate.py:125`
- reasoning: apply_registry overwrites severity from the row on every kept finding (:52). Both gates print and gate on its output only (cli_check_diff.py:82-91, posttooluse_gate.py:125-126). Nothing reads a Tier-1 finding's severity before that call.

### Unanchored findings

- **important**: The new 'call site selects no active ast or guard row' refusal (exit 1) breaks the existing test_unenforced_mandate_does_not_gate, which asserts exit 0 with an unenforced-only registry; §4.7 lists that call only as 'adds --call-site'.
  - evidence: `plugins/arch-compliance/tests/test_diff_cli.py:102-108`
- **important**: Validating AdrHostConfig.runs_dir and ledger_path with validate_posix_rel_path re-proposes a refusal the approved ADR gate contract rejected on the record ('Not adopted ... a visible host choice, not a state the gate must prevent'). The spec only renames the citation inside that paragraph and never names or reverses the rejection.
  - evidence: `docs/design/ADR_GATE_HOST_CONTRACT.md:295-303`
- **advisory**: Host module code executed by exec_module can run outside both wrapped regions: atexit handlers, threads, monkeypatches of acf modules, and generator finalization. The 'host code runs only inside the wrapped regions' guarantee therefore covers synchronous exceptions only and should be worded as such.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:357`
- **advisory**: Once scan_tree's roots are contained by resolve_under_root, its walk filter (relative_to plus except ValueError: continue) can no longer fire. Decision 8 says redundancy made by the design is deleted, but §4.9 keeps this filter.
  - evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:59-62`
- **advisory**: §4.9 edits fail_loud_ratchet.load_baseline's existence check, yet leaves it as a hand-rolled second loader beside acf.loader, whose docstring claims every input file goes through it. The ADR contract deferred it as 'a pre-existing second loader outside this phase', and this spec now touches that code path without consolidating it.
  - evidence: `plugins/arch-compliance/python/acf/loader.py:1-7`

### Looked for but did not find

- Another Tier-1 active-row filter: grep `unenforced|\.status\b|enforced"` over plugins/arch-compliance excluding tests
- Another absolute/escape string test: grep `is_relative_to|relative_to\(|is_absolute\(|"\.\."|_looks_absolute|_escapes_repo|absolute|_WIN_DRIVE_RE` over *.py and acf/
- Another parse-or-skip: grep `ast\.parse|except SyntaxError` across the tree (docs/reviews excluded)
- Another dynamic loader or sys.path mutation: grep `importlib|import_module|spec_from_file_location|exec_module|runpy|__import__|exec\(|sys\.path\.(insert|append)` outside docs/
- Another LineLookup: grep `LineLookup|_line_lookup|line_lookup|lines\[line - 1\]`
- Another runtime spelling of TS mandate ids: grep `fail-loud\.empty-catch|no-shims\.explicit-any` in *.py/*.ts/*.tsx
- Another detector-id validator: read acf-mandate SKILL.md, test_profile_drift.py, architecture-review SKILL.md, acf-setup SKILL.md
- Undocumented acf-check-diff invocations: grep `check.diff|check_diff` in *.yml/*.toml/*.json/*.sh and docs; no .pre-commit-config exists
- Call-site values outside CallSite: grep `call_sites` in all tracked YAML here and in the origin host's mandates.yml

### Relationships

- PARTIAL_OVERLAP: `acf.engine.file_under_root` — responsibility `decide that an input path names an existing regular file` — existing `plugins/arch-compliance/python/acf/loader.py:24-28`
  - resolution: R = the existence decision via Path.is_file(). require_file refuses with a subject message; file_under_root adds containment and returns None. Either have require_file accept an optional root and delegate to file_under_root, or state in §5.2 why gate-owned input files keep their own check. The ratchet baseline, which §4.9 touches, should then go through one of them (ideally load_model_file) rather than a third hand-rolled loader.
- BOUNDARY_CUT: `validate_posix_rel_path on AdrHostConfig.runs_dir / ledger_path` — responsibility `decide whether a host-declared ADR records path may lie outside the repository` — existing `docs/design/ADR_GATE_HOST_CONTRACT.md:295-303`
  - resolution: The approved ADR contract owns this decision and says host-chosen. Either name the rejection and amend ADR_GATE_HOST_CONTRACT.md's 'Not adopted' paragraph as a recorded reversal, or drop the AdrHostConfig switch from §4.9.
- ADJACENT: `acf.engine.resolve_under_root` — responsibility `containment test of a resolved path under the repository root` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:242-245`
  - resolution: none
  - non-merge: resolve_under_root turns a relative string into a contained Path. The hook converts an already-resolved absolute Path into its relative string for display and dispatch keys. They share a one-line predicate but have opposite inputs and outputs.
- SUBSUMED: `acf.engine.resolve_under_root (ratchet roots)` — responsibility `keep ratchet-scanned files under the root` — existing `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:59-62`
  - resolution: Once each roots entry is contained, the walk filter's except ValueError cannot fire. Delete the filter (keep the relative_to conversion) per Decision 8.
- ADJACENT: `load_host_detector` — responsibility `load a Python module from a file path` — existing `tests/test_check_installed_skills.py:15-18`
  - resolution: none
  - non-merge: Test-only load of a fixed in-repo script with no caching, root policy or error typing; not a runtime consumer.
- ADJACENT: `load_host_detector sys.path append` — responsibility `mutate sys.path` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:22-26`
  - resolution: none
  - non-merge: The hooks put the plugin's own python/ first at start-up; the loader appends one host root once. Different directory, position and lifetime.
- ADJACENT: `_to_findings (HostHit -> Finding)` — responsibility `construct Finding from detector output` — existing `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:84-92`
  - resolution: none
  - non-merge: The bridge coerces untyped subprocess JSON; the host runner receives typed, revalidated HostHit and stamps identity from the row.
- ADJACENT: `_to_findings (HostHit -> Finding)` — responsibility `construct Finding from detector output` — existing `plugins/arch-compliance/python/acf/judge.py:238-255`
  - resolution: none
  - non-merge: The judge demotes severity by confidence, takes mandate_id from the provider result and admits `<diff>` with line 0; host findings take everything from the row and require line >= 1.
- ADJACENT: `make_line_lookup` — responsibility `look up a source line by 1-based index` — existing `plugins/arch-compliance/python/acf/detectors/fsm_guard.py:56`
  - resolution: none
  - non-merge: fsm_guard indexes its own parsed text for a message snippet; make_line_lookup serves exemption checks across files from the gate's file_lines map.
- SUBSUMED: `Mandate.runs_at / MandateRegistry.active` — responsibility `decide whether a row runs at this Tier-1 gate` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99`
  - resolution: _active_mandates, the hook's three inline filters and enforcement.py:47 all call the new definition, as §4.6 and §4.5 state.
- ADJACENT: `acf-check-diff --call-site required plus no-rows refusal` — responsibility `refuse a gate site that selects nothing` — existing `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/run_guards.py:116`
  - resolution: none
  - non-merge: The origin host's runner lives in another repository and is cited as precedent; it is not a second owner inside this codebase.

### Two-owner counts

- decide an input path names an existing regular file (require_file, file_under_root, hook pre-check posttooluse_gate.py:84): 3
- containment test of a resolved path under the repo root (resolve_under_root, posttooluse_gate.py:242-245, fail_loud_ratchet.py:59-62): 3
- load-parse-refuse an input file (acf.loader.load_model_file, fail_loud_ratchet.load_baseline): 2
- load a Python module from a file path (load_host_detector, tests/test_check_installed_skills.py:15-18): 2
- mutate sys.path (posttooluse_gate.py:26, inject_constraints.py:29, load_host_detector): 3
- Tier-1 dispatch loop over changed paths (cli_check_diff._scan_changed, posttooluse_gate._scan_paths): 2
- construct Finding from detector output (python scanners, typescript_bridge, judge._to_finding, host _to_findings): 4

### Document conflicts

- `docs/design/ADR_GATE_HOST_CONTRACT.md:295` (contradicts): Not adopted: a refusal of absolute paths or `..` segments in the two fields. ... That is a visible host choice, not a state the gate must prevent
- `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:418` (contradicts): `KNOWN_DETECTORS` stays where the diff CLI defines it (`plugins/arch-compliance/python/acf/cli_check_diff.py:25`)
- `docs/design/ADR_GATE_HOST_CONTRACT.md:292` (restates): `fail_loud_ratchet.load_baseline` ... is a pre-existing second loader outside this phase.

## hardening

### Claim verdicts

#### C84 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:69-74; plugins/arch-compliance/hooks/posttooluse_gate.py:113-117; plugins/arch-compliance/hooks/inject_constraints.py:104-107; plugins/arch-compliance/python/acf/cli_check_llm.py:54`
- reasoning: In cli_check_diff, load and _scan_changed both run inside the try at :69-74, and the except at :72 already lists UnknownDetectorError and DetectorPackError. Host dispatch runs inside _scan_changed, so a load or lookup failure there reaches that handler. In the hook, dispatch runs inside _scan_paths under the scan try at :113-117, which the spec widens to include UnknownDetectorError. inject_constraints.py:104 and cli_check_llm.py:54 call load_mandates without known_detectors, so §4.2's load_mandates (file-existence check only, no import) runs no host code for them. Importing at load time would run host code in both. A missing file is still refused at load through file_under_root.

#### C85 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:46; plugins/arch-compliance/python/acf/detectors/python_pack.py:27-52; plugins/arch-compliance/python/acf/cli_check_diff.py:168-182`
- reasoning: Built-in findings carry fixed ids (python_pack.py:67/97/144/172, fail_loud_ratchet.py:132, emptyCatch.ts:23, explicitAny.ts:15), and apply_registry matches them to rows by mandate_id (enforcement.py:46). _check_builtin refuses a row whose id differs from its detector's id, so a built-in row cannot load and then receive no findings. Of the built-ins, only the ratchet is dispatched at a single gate (cli_check_diff.py:168-182; the hook never calls it). The contract's DIFF_CALL_SITES, together with the 'unserved' check, refuses a ratchet row that declares hook. _row_shape refuses an active row with no Tier-1 site. Host findings are stamped mandate.id by _to_findings. I enumerated these cases: ratchet with [hook], [audit] only, id mismatch, LLM id under ast, host ast with languages none. Each is refused, and I found no loadable active ast/guard row that neither gate runs.

#### C86 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:63; plugins/arch-compliance/hooks/posttooluse_gate.py:65; plugins/arch-compliance/tests/test_diff_cli.py:48`
- reasoning: Each production entry point resolves one repo per process: cli_check_diff.py:63 and the hook at :65, which is a new process per edit. The only multi-root producer is in-process tests: test_diff_cli.py calls main() repeatedly, each time on a fresh tmp_path repo (:48, :61, :98...). The spec routes host-row cases through the fresh_host_loader fixture. The production code refuses rather than repairs. A second root cannot be supported anyway, because sys.path and sys.modules are process-global and a host's intra-repo imports (e.g. 'scripts.*') would resolve to the first root.

#### C87 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:97; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:132; plugins/arch-compliance/python/acf/cli_check_diff.py:168-182; config/architecture/mandates.yml:64-73`
- reasoning: The scanners hard-code mandate_id literals, e.g. python_pack.py:97 and fail_loud_ratchet.py:132. The ratchet runs only in cli_check_diff (:168-182); posttooluse_gate.py has no ratchet reference (grep empty). So the contract records facts that already hold. I ran a read-only YAML scan of config/architecture/mandates.yml, both profiles and tests/fixtures/mandates_valid.yml: none has two non-unenforced ast/guard rows on the same detector, so the one-row-per-built-in cost hits no shipped registry.

#### C88 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/loader.py:70-73; plugins/arch-compliance/python/acf/registry.py:33-41; plugins/arch-compliance/hooks/inject_constraints.py:104-107; plugins/arch-compliance/python/acf/cli_check_llm.py:54`
- reasoning: load_model_file converts only ValidationError (loader.py:72). Under pydantic 2.13.3 I confirmed that an exception raised inside a model_validator(mode='after') that is not a ValueError propagates with its own type, as _unique_ids already relies on (registry.py:33-41). So every caller that builds a Mandate sees the same AcfInputError. inject_constraints catches AcfInputError at :105. cli_check_llm.py:54 does NOT catch it: the error ends in a traceback and a non-zero exit, as a malformed registry already does today and as spec §3 says. 'Each already handles' is loose for that caller, but 'no caller change' holds.

#### C89 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:50-53`
- reasoning: Each built-in scanner parses its own tree (python_pack.py:35, facade_sinks.py:51), and the spec keeps those separate parses. Sharing one parse across N host ast callables on a file removes N-1 parses. This is an optimisation and handles no invalid state.

#### C90 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:46-52; plugins/arch-compliance/python/acf/finding.py:11-19`
- reasoning: apply_registry looks up the row by finding.mandate_id (:46), and Finding carries mandate_id, detector and severity as plain fields (finding.py:12-17). If a host built the Finding, it would choose which row the finding attaches to. HostHit(path, line, message) plus construction in the runner makes that state unrepresentable (rung 1).

#### C91 — SURVIVED
- evidence: `.gitignore:8; .github/workflows/ci.yml:40; plugins/arch-compliance/hooks/posttooluse_gate.py:72-81`
- reasoning: .gitignore:8 ignores .acf/, so a CI checkout has no marker, and ci.yml:40 invokes the CLI explicitly. The hook exits 0 before its deferred imports when .acf/enabled is absent (:72-81). Requiring the marker in acf-check-diff would therefore turn CI off. The spec states the residual case (a manual run in an untrusted checkout) as accepted.

#### C92 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:27-52; plugins/arch-compliance/hooks/posttooluse_gate.py:254; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:19-97`
- reasoning: scan_python_file always emits all three python_pack detectors and never consults the registry (python_pack.py:41-51). The hook calls it unconditionally (:254), and scan_typescript_file is likewise registry-blind. registry.active(call_sites) only selects which configurable scanners run, so it cannot remove those findings. Without the sink filter, a [ci]-only no-shims.hasattr finding survives at the hook, which is the behaviour test_hooks.py:199-218 pins today. The filter is not redundant.

#### C93 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:22-28; pyproject.toml:19-20; .github/workflows/ci.yml:40`
- reasoning: The hook inserts the plugin's python/ directory at sys.path[0] and imports acf before any host code (:22-28). The console scripts (pyproject.toml:19-20) start with sys.path[0] set to the script directory. Appending the host root therefore adds no shadowing. Under 'python -m' from the host root (ci.yml:40), cwd is already first, so the CLI's own acf would already come from a host acf/. A loader-time acf/ refusal would run after that and could not prevent it, so it has no producer the loader can address. A host top-level name taken by an earlier entry fails as ModuleNotFoundError or a missing attribute, which load_host_detector wraps as UnknownDetectorError.

#### C94 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:69-74; plugins/arch-compliance/hooks/posttooluse_gate.py:113-117; plugins/arch-compliance/python/acf/enforcement.py:49`
- reasoning: Both gates call apply_registry outside their try blocks (cli_check_diff.py:82, posttooluse_gate.py:125), and line_lookup is invoked at enforcement.py:49. Lazy I/O there would raise an uncaught OSError. Reading inside scan_host_guards puts the I/O under each gate's scan try, where DetectorPackError is already handled.

#### C95 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:16; plugins/arch-compliance/skills/acf-mandate/SKILL.md:56; plugins/arch-compliance/python/acf/registry.py:56-63`
- reasoning: judge.py:16 imports acf.registry, so registry importing acf.judge would create a cycle, and passing the ids in is required. SKILL.md:56 states the prompt-id rule, while registry.py:60 checks known_detectors only for ast/guard rows, so nothing enforces it today. The four shipped llm rows use ids in LLM_PROMPT_IDS (judge.py:29-36). The check fails loud at load (rung 3).

#### C96 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:29-61; config/architecture/ARCHITECTURE.md:118-133; hm:scripts/ci/run_guards.py:116`
- reasoning: A required argparse flag makes 'which gate is this' an explicit declaration, and a missing value exits 2 instead of silently running the wrong rows (rung 3 at the invoker). Caveat: ARCHITECTURE.md:120-122 scopes '## Declared, never defaulted' to the ADR gate's adr.yml values, and HM's runner defaults --site to ci (run_guards.py:319). So two of the three cited supports are analogies, not rules. The fail-loud reason stands on its own.

#### C97 — SURVIVED
- evidence: `hm:scripts/ci/run_guards.py:126-130; plugins/arch-compliance/profiles/python-service/mandates.yml:7; README.md:57`
- reasoning: No shipped row declares precommit today (profile rows are [ci, hook] or [ci]). The documented pre-commit invocation (README.md:57), with --call-site precommit, would therefore select nothing and print 'No findings.' (cli_check_diff.py:188-189). The refusal plus the one-shot data migration close that gap, matching HM's refusal at run_guards.py:126-130.

#### C98 — SURVIVED
- evidence: `pyproject.toml:7; plugins/arch-compliance/python/acf/finding.py:11-19`
- reasoning: I checked behaviour under pydantic 2.13.3, which matches pyproject.toml:7. A normally built HostHit stores exact str/int in __dict__. model_construct(path=b'a.py', line='5', junk=1) leaves bytes and a str in __dict__ and drops the extra key. So the exact-type check followed by model_validate catches what lax validation would coerce. type(item) runs no host code. Iteration, isinstance on raw, and property access on a host subclass all run inside the try, so _to_findings sees only plain values.

#### C99 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:211-215; plugins/arch-compliance/python/acf/cli_check_diff.py:76-80`
- reasoning: ## Scoped refactor (:211-215) asks for removal of non-contractual patterns in changed paths. The listed duplicates exist, e.g. the token-identical _line_lookup closures at cli_check_diff.py:76-80 and posttooluse_gate.py:119-123. Deleting them rather than recording debt is rung 2, a single owner.

#### C100 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:14-27; plugins/arch-compliance/python/acf/registry.py:43-45; plugins/arch-compliance/python/acf/registry.py:11`
- reasoning: Mandate is a BaseModel with no model_config and every named field (:15-26). languages is a Literal that includes 'none' (:11), and params is dict[str, Any] | None (:26). MandateRegistry already carries an @property (by_id, :43-45), so adding a property and plain methods is compatible.

#### C101 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/finding.py:11-19; plugins/arch-compliance/python/acf/enforcement.py:52`
- reasoning: Finding's required fields are mandate_id, severity, path, line, message and detector. confidence defaults to None and detection defaults to 'ast'. Severity is a str Enum, and enforcement.py:52 already builds Severity(mandate.severity).

#### C102 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:23; plugins/arch-compliance/python/acf/enforcement.py:43-52`
- reasoning: by_id is used at :43/:46, the status drop is at :47, and exemption and severity handling is at :49-52. LineLookup is Callable[[str, int], str] (:23), which make_line_lookup's closure satisfies.

#### C103 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:72; plugins/arch-compliance/python/acf/cli_check_diff.py:110; plugins/arch-compliance/python/acf/cli_check_diff.py:152`
- reasoning: load is at :70 and scan at :71, inside the try at :69-74, and the except at :72 lists GitError, AcfInputError, UnknownDetectorError and DetectorPackError. apply_registry is at :82. In the .py branch, repo, text, posix, lines and registry are all in scope (:118-150). The TS branch reads the file inline at :152, so the result can be bound to a variable. changed is bound at :110 and in scope after the ratchet loop.

#### C104 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:113-117; plugins/arch-compliance/hooks/posttooluse_gate.py:242-251; plugins/arch-compliance/hooks/posttooluse_gate.py:284-294`
- reasoning: The deferred imports are at :91-104, the load try at :106-110, and the scan try at :113-117, which catches only DetectorPackError today and can be widened. lookup and apply_registry are at :119-125, and the inline filters at :229-236 and :284-286. relative_to with its ValueError fallback is at :242-245, and the build-artifact loop at :284-294. text is read at :251 for every code suffix, so it is in scope in both the .py and the else (TS) branches, along with rel.

#### C105 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:69-74; plugins/arch-compliance/hooks/posttooluse_gate.py:106-117; plugins/arch-compliance/python/acf/exceptions.py:13`
- reasoning: Every new raise site is under a handler. load_host_detector, _call_host, _to_findings and scan_host_guards all run inside _scan_changed and _scan_paths. Those sit under cli_check_diff's try (:72 already lists all three types) and the hook's scan try, which §4.6 widens to all three. The hook's load try gains UnknownDetectorError. callable(fn) sits outside the try but runs no Python-level host code. apply_registry does no I/O (enforcement.py:43-53). Not new: on Python 3.11, parse_python's SyntaxError-only catch misses the ValueError ast.parse raises on null bytes, but scan_python_file already parses the same text first with the same catch.

#### C106 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_diff_cli.py:48; plugins/arch-compliance/tests/test_hooks.py:22-29; pyproject.toml:24`
- reasoning: The loader steps are plain importlib.util and module-global code, and the rollback branch is consistent. When spec lookup fails, mod is None and nothing was registered. When getattr fails on a cached module, the module stays registered. Tests run in one pytest process (pyproject.toml:24 pythonpath). test_diff_cli calls main() in process (:48), so module globals persist across tests. The fixture's monkeypatch of _ACTIVE_ROOT and _MODULE_CACHE, plus the sys.path and sys.modules snapshot, isolates them. Hook tests are subprocesses (:22-29) and need no reset.

#### C107 — SURVIVED
- evidence: `C:/Python313/Lib/dataclasses.py:757; pyproject.toml:5`
- reasoning: dataclasses._is_type evaluates `sys.modules.get(cls.__module__).__dict__` (dataclasses.py:757) for any string annotation with no module prefix. That happens for every field under `from __future__ import annotations`, and it raises AttributeError when the module is unregistered. Registering the module under the synthetic name before exec_module avoids this. spec_from_file_location accepts any name.

#### C108 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_import_graph.py:70-76; plugins/arch-compliance/python/acf/adr/contract.py:20; plugins/arch-compliance/python/acf/registry.py:6-7`
- reasoning: registry imports only acf.exceptions and acf.loader (:6-7). No scanner module imports acf.registry or the acf.detectors package (grep of the detectors' imports). judge imports registry (judge.py:16), not the reverse. acf.adr already imports acf.engine (contract.py:20). The import-graph test only forbids 'scripts' imports from acf.adr and the literal 'acf.adr' in the hook files. The hook's new imports (acf.detectors, acf.registry, acf.engine) do not reach acf.adr or acf.judge.

#### C109 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:48-64; plugins/arch-compliance/python/acf/loader.py:67-73`
- reasoning: load_mandates calls load_model_file(path, Mandate, subject='mandates file', fmt='yaml', many=True) at :53-55 and returns MandateRegistry(mandates=..., source_path=path.as_posix()) at :64. With many=True, loader.py:67-73 returns list[Mandate].

#### C110 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_repo_paths.py:47-48; plugins/arch-compliance/tests/test_repo_paths.py:61-67; plugins/arch-compliance/hooks/posttooluse_gate.py:11-12`
- reasoning: The only allowlisted line pinned for posttooluse_gate.py is the :11 text (test_repo_paths.py:47-48). The test only flags lines that mention config/architecture (:63). grep shows the :12 text 'Otherwise scan' appears nowhere else. A rewording of :12 that does not spell config/architecture breaks no test.

#### C111 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:78-82; config/architecture/mandates.yml:60`
- reasoning: mandates.yml:60 does declare fail-loud.bare-except-ok. But the design's handlers (§4.4 items 3 and 4, and _describe) are `except BaseException as exc:`, not tuple handlers `except (Exception, SystemExit)`. The claim and spec §6's 'does not flag a tuple handler' misdescribe the design. The conclusion still holds for another reason: _is_bare_or_exception flags only a bare handler or Name 'Exception' (:78-82), and 'BaseException' is neither.

#### C112 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/engine.py:8; plugins/arch-compliance/python/acf/engine.py:17-24`
- reasoning: engine.py imports only pathlib (:8) and defines contains_backslash (:17-24). Adding re, plus ast for parse_python, keeps it stdlib-only.

#### C113 — SURVIVED
- evidence: `README.md:66-74; plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23; plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15; plugins/arch-compliance/tests/test_registry.py:24`
- reasoning: README.md:66-74 is a parseable markdown table of 7 Python detector ids and mandate ids. emptyCatch.ts:23 and explicitAny.ts:15 hold `mandate_id: "..."` literals. test_registry.py:24 and :35 build inline YAML rows that new cases can copy. test_registry :30 must switch from a frozenset to KNOWN_DETECTORS, as the spec states, because _check_builtin calls .get.

#### C114 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_diff_cli.py:25-48; plugins/arch-compliance/tests/test_hooks.py:22-29`
- reasoning: test_diff_cli already builds a temporary git repo and runs main in process (:25-48), and test_hooks already runs the hook as a subprocess (:22-29). A fixture tree can trigger every detector: dist/x.py for build artifacts, a baseline JSON for the ratchet, params for facade and fsm. TS needs node_modules, which CI installs. Rows declaring DIFF_CALL_SITES or HOOK_CALL_SITES pass _check_builtin.

#### C115 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:109-184; plugins/arch-compliance/hooks/posttooluse_gate.py:226-295`
- reasoning: file_lines is a local dict in both _scan_changed (:109, returned at :184) and _scan_paths (:226, returned at :295). Both functions run under their gate's scan try, so a call at their end is covered, and filling only missing keys keeps the gate's own reads.

#### C116 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:29-61; plugins/arch-compliance/python/acf/cli_check_diff.py:69-74`
- reasoning: The parser is built at :29-61. argparse required=True with choices makes parser.error call sys.exit(2), which is SystemExit when main runs in process. args is in scope for `sites` before the try at :69. A refusal placed after load_mandates inside that try is caught by the AcfInputError arm at :72 and returns 1.

### Unanchored findings

- **advisory**: Which gates run each built-in detector is stated twice: in KNOWN_DETECTORS.call_sites and in the two hand-written dispatch loops. The design ties them together with a contract-against-dispatch test (rung 3) instead of having the gates choose built-in scanners from the contract (rung 2); the only reason given is the 'keep this change small' non-goal about merging the loops.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:102-184`
- **advisory**: TS_MANDATE_IDS makes the Python map the owner, yet the Node rules keep emitting their own mandate_id literal and the bridge compares the two at run time. The spec gives no reason for keeping the Node literal instead of dropping it from the scanner output, which would leave a single producer.
  - evidence: `plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23`
- **advisory**: acf-check-diff refuses a call site that selects no active ast/guard row so it cannot report a false clean run, but the PostToolUse hook gets no matching refusal. An enabled host whose rows declare no hook/posttooluse site gets a silent 'no findings' on every edit, the same false green the diff refusal exists to prevent.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:112-117`
- **advisory**: Spec §6's Fail-loud row justifies the two broad handlers as tuple handlers the detector does not flag, but §4.4 writes them as `except BaseException`. They do pass, because only a bare handler or Name 'Exception' is flagged, so the stated reason is wrong and should be corrected.
  - evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:78-82`
- **advisory**: The spec cites the doctrine's '## Declared, never defaulted' rule for making --call-site required, but that rule is scoped to the ADR gate's adr.yml values and explicitly lists other package defaults as outside it. The flag stands on its fail-loud reason, not on that rule.
  - evidence: `config/architecture/ARCHITECTURE.md:118-133`

### Looked for but did not find

- A producer for a second host root in production: each entry point resolves one repo per process (cli_check_diff.py:63, posttooluse_gate.py:65); the only producer is in-process tests
- Any shipped registry with two active rows on the same built-in detector (YAML scan of config/architecture/mandates.yml, both profiles, the test fixture): none
- Any shipped llm row whose detector is outside LLM_PROMPT_IDS: none
- Any shipped row that already declares precommit: none, which confirms the migration is needed
- A caller of apply_registry other than the two gates and test_enforcement.py
- Any path by which load_mandates imports host code under the §4.2 body: it only stats the file
- A handler gap for UnknownDetectorError or DetectorPackError raised from host dispatch in either gate, after the §4.6 widening
- A scanner module that imports acf.registry or the acf.detectors package, which would create an import cycle with KNOWN_DETECTORS: none

### Mechanism traces

- **Mandate._row_shape model_validator (malformed host ref, no Tier-1 site, host ast with languages none) and CallSite Literal**
  - invalid state: Mandate m with m.detection in {ast,guard} and (':' in m.detector and the ref fails parse) or (m.status != 'unenforced' and not TIER1 ∩ m.call_sites) or (host ast and m.languages == 'none'); or any call_sites value outside CallSite
  - producer: `config/architecture/mandates.yml:70`
  - rung 1 (highest applicable 1); repairs=False
  - spec citation: `None`
- **load_mandates built-in contract check (_check_builtin)**
  - invalid state: active ast/guard row m with m.detector not a host ref and (m.detector not in KNOWN_DETECTORS or m.id != KNOWN_DETECTORS[m.detector].mandate_id or (TIER1 ∩ m.call_sites) - contract.call_sites != ∅)
  - producer: `plugins/arch-compliance/tests/test_registry.py:24`
  - rung 3 (highest applicable 2); repairs=False
  - hardening rejected because: the scanners stamp fixed mandate ids and run at fixed gates, so the contract records an existing fact rather than adding a capability; the accepted cost (at most one active row per built-in detector) affects no shipped registry
  - spec citation: `None`
- **load_mandates llm_prompt_ids check**
  - invalid state: active row m with m.detection == 'llm' and m.detector not in LLM_PROMPT_IDS
  - producer: `plugins/arch-compliance/python/acf/registry.py:60`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `None`
- **Required --call-site argument on acf-check-diff**
  - invalid state: an acf-check-diff invocation whose argv names no site in {ci, precommit}
  - producer: `README.md:57`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `None`
- **Empty-selection refusal (call site selects no active ast or guard row) plus one-shot precommit addition to shipped rows**
  - invalid state: registry.active({site}) restricted to detection in {ast,guard} is empty for the declared site
  - producer: `plugins/arch-compliance/profiles/python-service/mandates.yml:7`
  - rung 4 (highest applicable 4); repairs=False
  - spec citation: `None`
- **apply_registry call_sites filter (drop findings whose row does not runs_at the gate's sites)**
  - invalid state: finding f where by_id[f.mandate_id].call_sites ∩ gate_sites == ∅
  - producer: `plugins/arch-compliance/hooks/posttooluse_gate.py:254`
  - rung 2 (highest applicable 2); repairs=False
  - spec citation: `None`
- **Contract-against-dispatch test (KNOWN_DETECTORS.call_sites vs the gates' dispatch)**
  - invalid state: built-in detector d and site s with s in KNOWN_DETECTORS[d].call_sites while the gate serving s does not dispatch d (or the reverse)
  - producer: `plugins/arch-compliance/hooks/posttooluse_gate.py:213-295`
  - rung 3 (highest applicable 2); repairs=False
  - hardening rejected because: merging the pre-existing loops is left out to keep this change small
  - spec citation: `None`
- **TS_MANDATE_IDS stamping with run-time comparison against the Node rule's mandate_id**
  - invalid state: TypeScript scanner item with item['detector'] not in TS_MANDATE_IDS or item['mandate_id'] != TS_MANDATE_IDS[item['detector']]
  - producer: `plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23`
  - rung 3 (highest applicable 2); repairs=False
  - spec citation: `None`
- **_call_host wrapped region with _revalidate (exact-type rebuild of each HostHit)**
  - invalid state: host callable raises, returns None/str/bytes/non-iterable, or yields item with type(item) is not HostHit or fields not exactly (str,int,str) or failing HostHit validation
  - producer: `hm:scripts/ci/metadata_facade_guard.py:66`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `None`
- **_to_findings ast path check (hit.path != expected_path refused)**
  - invalid state: HostHit h from an ast callable invoked on path p with h.path != p
  - producer: `hm:scripts/ci/arch_compliance/driver.py:150-163`
  - rung 3 (highest applicable 1); repairs=False
  - hardening rejected because: The ast path check refuses rather than making a wrong path unrepresentable, because one HostHit type serves both callable kinds, and a path-less ast hit would be a second type carrying the same facts.
  - spec citation: `None`
- **load_host_detector one-root-per-process refusal**
  - invalid state: load_host_detector called with repo_root.resolve() != _ACTIVE_ROOT after a first call
  - producer: `plugins/arch-compliance/tests/test_diff_cli.py:48`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: every production caller resolves one repository per process, so the refusal never fires in production, and the only multi-root producer (in-process tests) is handled by the test-only fresh_host_loader fixture
  - spec citation: `None`
- **fresh_host_loader test fixture (reset _ACTIVE_ROOT/_MODULE_CACHE, restore sys.path, evict host sys.modules entries)**
  - invalid state: between in-process tests, _ACTIVE_ROOT/_MODULE_CACHE/sys.path/sys.modules hold host state from a previous test's root
  - producer: `plugins/arch-compliance/tests/test_diff_cli.py:48`
  - rung 5 (highest applicable 5); repairs=True
  - hardening rejected because: In-process tests over several roots reset the loader through a test fixture
  - spec citation: `None`
- **load_host_detector sys.modules rollback on exec failure and UnknownDetectorError wrap**
  - invalid state: sys.modules[name] holds a partially executed host module after exec_module raised
  - producer: `hm:scripts/ci/metadata_facade_guard.py:66`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `None`
- **_describe fallback message for host exceptions whose __str__ raises**
  - invalid state: host exception exc for which f'{type(exc).__name__}: {exc}' raises
  - producer: `None`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `None`
- **resolve_under_root mapping a symlink-loop RuntimeError to None**
  - invalid state: rel under root whose non-strict Path.resolve() raises RuntimeError (symlink loop on Python 3.11/3.12)
  - producer: `pyproject.toml:5`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `None`
- **Ratchet baseline/roots containment via file_under_root/resolve_under_root, and AdrHostConfig path fields via validate_posix_rel_path**
  - invalid state: params.baseline or a params.roots entry, or AdrHostConfig.runs_dir/ledger_path, that is absolute, contains '..', escapes the root or loops
  - producer: `config/architecture/mandates.yml:97-98`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `None`

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
- **C20** [premise]: Each of the four built-in scanners that parse Python (python_pack.py:34-37, facade_sinks.py:50-53, fsm_guard.py:36-39, fail_loud_ratchet.py:23-26) wraps ast.parse in try/except SyntaxError and returns its empty result; acf.engine.parse_python returns None on SyntaxError, and scan_host_ast_file and each scanner keep their empty result on None.
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
- **C32** [deletion] [load-bearing]: Deleting cli_check_diff._active_mandates and the hook's inline filters in favour of registry.active(call_sites, detector=...) changes no selection except by call_sites: for every shipped registry, the only built-in row that stops running at a gate is no-shims.hasattr leaving the PostToolUse hook (it declares [ci]).
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99`
- **C33** [deletion] [load-bearing]: Removing LLM_PROMPT_IDS from KNOWN_DETECTORS changes behaviour only for ast/guard rows naming an LLM prompt id: load_mandates consults known_detectors only for ast/guard rows (registry.py:60), and no code reads KNOWN_DETECTORS for llm rows. The import at cli_check_diff.py:21 stays and feeds load_mandates(..., llm_prompt_ids=LLM_PROMPT_IDS), so LLM_PROMPT_IDS keeps a runtime consumer.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:21`
- **C34** [deletion] [load-bearing]: Replacing the literal mandate ids in the five scanner modules with module constants changes no emitted finding, and no test asserts on the scanner source text in a way the change would break.
  - spec citation: `None`
- **C35** [premise] [load-bearing]: load_mandates with llm_prompt_ids=LLM_PROMPT_IDS refuses no shipped row: every active llm row in config/architecture/mandates.yml, plugins/arch-compliance/profiles/*/mandates.yml, tests/fixtures/mandates_valid.yml and the inline registries loaded by acf-check-diff, tests/test_self_host.py or the acf-mandate snippet names an id in acf.judge.LLM_PROMPT_IDS (judge.py:29-36); the acf-mandate SKILL.md:56 and :121 prompt-id rule is then enforced at acf-check-diff.
  - spec citation: `None`
- **C36** [premise] [load-bearing]: getattr(mod, attr, None) swallows only AttributeError, so a host module-level __getattr__ raising anything else escapes a bare lookup; in spec §4.4 item 3 exec_module and the lookup share one try catching (Exception, SystemExit) that raises UnknownDetectorError, which cli_check_diff.py:72 and the hook's widened scan except catch. A failed exec_module removes the module from sys.modules; a failed lookup on a cached module leaves it cached.
  - spec citation: `None`
- **C37** [premise] [load-bearing]: pyproject.toml:5 allows Python 3.11, where a non-strict Path.resolve() raises RuntimeError on a symlink loop (3.13 does not); resolve_under_root catching RuntimeError and returning None makes a looping host path report as a missing file at load (UnknownDetectorError), yield [] exemption lines in scan_host_guards, or classify as unresolved in citations, never a traceback.
  - spec citation: `pyproject.toml:5`
- **C38** [premise] [load-bearing]: The TypeScript bridge's Finding construction sits in a try at typescript_bridge.py:82-95 whose except (KeyError, TypeError, ValueError) re-raises as DetectorPackError (:94-95); stamping mandate_id=TS_MANDATE_IDS[item['detector']] and raising ValueError on a differing item['mandate_id'] inside it yields DetectorPackError for an unknown detector or a mismatch, and the Node rules' literals (emptyCatch.ts:23, explicitAny.ts:15) equal the TS_MANDATE_IDS values, so no shipped finding is refused.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:82-95`
- **C39** [deletion] [load-bearing]: Deleting the two _line_lookup closures (cli_check_diff.py:76-80, posttooluse_gate.py:119-123) for make_line_lookup(file_lines), which is their body unchanged and reads no file, changes no exemption result for any finding at a338cad. The only new lines in file_lines are those scan_host_guards adds for files a host guard flags, so a built-in finding on such a file becomes exemptable as built-in findings on changed code files already are; a built-in finding on any other file still gets ''.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80`
- **C40** [premise] [load-bearing]: Decision 6's entry-point table is accurate: the PostToolUse hook inserts the plugin's python/ at sys.path[0] ahead of the hooks directory (posttooluse_gate.py:22-26) and imports acf first (:28), so the host root is not on sys.path before the loader appends it; the acf-check-diff console script (pyproject.toml:19-20) likewise; under python -m acf.cli_check_diff run from the host root (.github/workflows/ci.yml:40) the working directory is already sys.path[0], so appending changes nothing there. Host intra-repo imports such as hm:scripts/ci/metadata_facade_guard.py:66 resolve against the host root in the documented invocations.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:22-28`
- **C41** [premise] [load-bearing]: acf-check-diff today has no argument naming its call site (cli_check_diff.py:29-61 offers --mode, --base, --repo, --mandates, --json), so it cannot tell a pre-commit run from a CI run; the origin host's guard runner selects rows per --site (hm:scripts/ci/run_guards.py:116), refuses an unknown site (:107-111) and an empty selection (:126-130), with --site defaulting to ci (:317-321).
  - spec citation: `hm:scripts/ci/run_guards.py:116`
- **C42** [premise] [load-bearing]: file_lines holds only changed .py/.ts/.tsx files (cli_check_diff.py:126, :152; posttooluse_gate.py:248-252) plus, under the design, files a host guard flagged; built-in line-1 findings (fail_loud_ratchet.py:135, build_artifacts.py:34) on any other file still get '' and stay non-exemptable, as at a338cad, and a staged dist/x.py is already in file_lines today.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:135`
- **C43** [premise] [load-bearing]: No shipped or fixture registry row declares precommit today (git grep -n precommit -- '*.yml' prints nothing); adding precommit to each ast/guard row that declares ci (9 rows in config/architecture/mandates.yml, 7 in profiles/python-service, 3 in profiles/react-app, 3 in tests/fixtures/mandates_valid.yml) makes acf-check-diff --call-site precommit select exactly the rows acf-check-diff runs today, and refusing a site that selects no active ast/guard row prevents a clean report over an empty selection.
  - spec citation: `None`
- **C44** [premise] [load-bearing]: _revalidate (type(item) is HostHit, then exact type(...) is str/int/str checks on the item's __dict__ values, then HostHit.model_validate) inside _call_host's try refuses a host subclass and a model_construct or mutated hit with non-exact field types (b'a.py', '5', True, objects), rebuilds genuine hits unchanged (normal validation already yields exact str and int), and leaves _to_findings running no host code.
  - spec citation: `None`
- **C45** [premise] [load-bearing]: acf.engine.file_under_root (resolve_under_root, then Path.is_file, OSError from stat propagating) returns None for a missing path, a directory, an out-of-root path and a symlink loop on Python 3.11 to 3.13, and each runtime caller (load_mandates, load_host_detector, scan_host_guards, scan_ratchet) catches OSError around it and raises its typed error, so a permission-denied stat ends in UnknownDetectorError or DetectorPackError, not a traceback.
  - spec citation: `None`
- **C46** [premise] [load-bearing]: Validating AdrHostConfig.runs_dir and ledger_path with validate_posix_rel_path refuses no shipped or tested value (both adr.yml files declare docs/reviews/adr_runs and docs/reviews/adversarial_design_ledger.jsonl; test_adr_host.py and test_adr_host_acceptance.py declare reviews/runs and reviews/ledger.jsonl), surfaces a refusal as 'invalid ADR host config' through load_model_file, and keeps every repo / cfg.runs_dir and repo / cfg.ledger_path join lexically under the root.
  - spec citation: `plugins/arch-compliance/python/acf/adr/host.py:24-25`
- **C47** [premise] [load-bearing]: Switching the ratchet to file_under_root for params.baseline and resolve_under_root for each params.roots entry, with None or an OSError raising DetectorPackError, refuses no shipped or tested value (baseline config/architecture/fail_loud_ratchet.json and roots ['.'] in config/architecture/mandates.yml:97-98 and profiles/python-service/mandates.yml:58-59; RATCHET_BASELINE_REL as cli_check_diff's default; test_portable_guards.py:107 roots=['pkg']), and DetectorPackError is already caught by acf-check-diff (cli_check_diff.py:72).
  - spec citation: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:122-124`
- **C48** [deletion] [load-bearing]: Deleting the five detector-id sets (PYTHON_AST_DETECTOR_IDS, GUARD_DETECTOR_IDS, CONFIG_AST_DETECTOR_IDS, ALL_PYTHON_DETECTOR_IDS, TS_DETECTOR_IDS) touches only the references git grep -n "_DETECTOR_IDS" -- plugins tests prints, each of which the spec rewrites, and leaves KNOWN_DETECTORS as the only set of built-in detector ids in plugins/arch-compliance/python.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/__init__.py:11-28`
- **C49** [deletion] [load-bearing]: Replacing the inline params extraction in both gates with facade_sink_args, fsm_guard_args and build_artifact_args (required arguments as str(params.get(key, '')); allowlist_globs and atomic_is_sink passed unchanged when the key is present, null included; path_prefixes only when present and non-empty) produces the same scanner call for every row as today, because the scanners' signature defaults (facade_sinks.py:24-25, build_artifacts.py:16, :23) equal what the gates pass today when the param is absent.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/facade_sinks.py:24-25`
- **C50** [deletion] [load-bearing]: Replacing the four parse-and-skip copies with acf.engine.parse_python changes no scanner output, and no other site in plugins/arch-compliance/python parses Python with a SyntaxError skip.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37`
- **C51** [mandate] [load-bearing]: ## Fail loud: every invalid state in spec §6.1 is refused by the named component with the named error, including: acf-check-diff without --call-site (usage error, exit 2) or with a site selecting no active ast/guard row (AcfInputError); a host module whose import or callable lookup raises any exception but KeyboardInterrupt (UnknownDetectorError); a host callable or its result raising any exception but KeyboardInterrupt, or yielding a non-exact-type or invalid HostHit (DetectorPackError); a host path whose stat raises OSError (typed error at each caller); a TypeScript item with an unknown detector or differing mandate_id; an llm row with an unknown prompt id. Every broad handler re-raises a typed error or KeyboardInterrupt.
  - spec citation: `None`
- **C52** [mandate] [load-bearing]: ## Fail loud: no active built-in ast/guard row can load with known_detectors yet never receive a finding from either Tier-1 gate: _check_builtin refuses a detector not in KNOWN_DETECTORS (LLM prompt ids are not keys), a row id that differs from the detector's stamped mandate_id, and any declared Tier-1 call site outside the detector's contract call_sites (fail_loud_ratchet: DIFF only); and Mandate._row_shape refuses an active ast/guard row with no Tier-1 site. Host rows are dispatched by both gates' host runners at any Tier-1 site.
  - spec citation: `None`
- **C53** [mandate] [load-bearing]: ## Declared, never defaulted: load_mandates requires an explicit repo_root for an active host detector row (AcfInputError otherwise, never derived), and apply_registry's new call_sites keyword has no default.
  - spec citation: `config/architecture/ARCHITECTURE.md:118-133`
- **C54** [mandate]: ## No shims: callable lookup is getattr(mod, attr, None) followed by callable() and a raise; no hasattr, and no host-detector failure has a silent fallback.
  - spec citation: `config/architecture/ARCHITECTURE.md:43-53`
- **C55** [mandate]: ## POSIX paths: HostHit.path is validated by validate_posix_rel_path (which refuses backslashes) and error messages use .as_posix().
  - spec citation: `config/architecture/ARCHITECTURE.md:55-64`
- **C56** [mandate]: ## One base exception: the design adds no exception class and uses AcfInputError, UnknownDetectorError and DetectorPackError (exceptions.py:5, :13, :29), all subclassing AcfError.
  - spec citation: `plugins/arch-compliance/python/acf/exceptions.py:5`
- **C57** [mandate]: ## One owner for host paths: acf/engine.py, acf/registry.py, acf/detectors/__init__.py and the new acf/detectors/host.py spell no config/architecture path, and the acf-mandate skill snippet takes MANDATES_REL and resolve_repo from acf.repo.
  - spec citation: `None`
- **C58** [mandate]: ## Prose names no host: the runtime messages in §4.2-§4.4 and the prose changes in §4.8 name no origin host.
  - spec citation: `config/architecture/ARCHITECTURE.md:135-143`
- **C59** [mandate]: ## Live consumers: each new export in §6.2 has the named non-test caller (file_under_root: load_mandates, load_host_detector, scan_host_guards, scan_ratchet; parse_python: four scanners and scan_host_ast_file; the *_args functions: both gates; CallSite: Mandate.call_sites; DIFF_CALL_SITES: acf-check-diff's --call-site choices and KNOWN_DETECTORS), acf.judge.LLM_PROMPT_IDS keeps a runtime consumer, and the five deleted detector-id sets leave no dead export behind.
  - spec citation: `None`
- **C60** [mandate]: ## No completeness claims: every population claim in the spec carries a re-runnable recipe (§1, §3, Appendix) or is a per-item table, as ARCHITECTURE.md:159-169 requires.
  - spec citation: `config/architecture/ARCHITECTURE.md:159-169`
- **C61** [mandate]: ## Declared text decoding: the new read_text calls (cli_check_diff.py TypeScript branch, scan_host_guards' read of flagged files) declare encoding='utf-8'; errors='replace' in scan_host_guards is permitted by that rule, which governs the declared encoding; no subprocess is added.
  - spec citation: `None`
- **C62** [mandate]: ## Release discipline: because shipped skill prose changes, the version is bumped 0.2.2 -> 0.2.3 in both files ARCHITECTURE.md:186-187 names (pyproject.toml:3, plugins/arch-compliance/.claude-plugin/plugin.json:3).
  - spec citation: `config/architecture/ARCHITECTURE.md:184-194`
- **C63** [mandate]: ## Single point of definition: each existing definition listed in spec §4.9 is deleted and its callers switched (citations' path helpers, the five detector-id sets, the line-lookup closures, the active-row filters, the duplicated params extraction, the ratchet's joins and existence check, AdrHostConfig's path checks, the four parse-and-skip copies, test_self_host's resolve-and-is_file), the scanners' signature defaults stay the one default for optional params, and the spec makes no claim that §4.9 lists every duplicate in the tree.
  - spec citation: `None`
- **C64** [mandate]: ## Scoped refactor: Decision 8 applies the doctrine's 'remove legacy dependencies or non-contractual patterns in code paths you are changing' consistently: every existing definition a new definition in this design duplicates is deleted, the parse-or-skip helper included, while the two pre-existing dispatch loops stay because each gate calling the host runners is two call sites of one procedure, not a second definition.
  - spec citation: `config/architecture/ARCHITECTURE.md:213-215`
- **C65** [mandate]: ## Frozen ledger format: the design changes no ledger model.
  - spec citation: `config/architecture/ARCHITECTURE.md:145-151`
- **C66** [mandate]: The design complies with the five portable governing principles at docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51 and fulfils that spec's call for project-specific detector extension points (:102, :123, :125).
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51`
- **C67** [mandate]: ## Fail loud: scan_host_guards mapping a flagged path for which file_under_root returns None (missing, directory, outside the root, symlink loop) to [] and decoding with errors='replace' hides no failure: such a path has no line that could carry an exemption token, so the finding stays; an OSError from the stat or the read raises DetectorPackError inside each gate's scan try; and make_line_lookup does no I/O.
  - spec citation: `None`
- **C68** [shape_fit] [load-bearing]: Mandate.runs_at and MandateRegistry.active become the single definition of 'this row runs at this gate' for the Tier-1 gates; after the change no other Tier-1 site (cli_check_diff, posttooluse_gate, enforcement, the host runners) keeps its own active-row filter.
  - spec citation: `None`
- **C69** [shape_fit] [load-bearing]: After the design, the absolute and under-root string tests have one definition in acf.engine, consumed by validate_posix_rel_path, file_under_root, citations.py, the ratchet and AdrHostConfig's validation; file_under_root is the one resolve-plus-existence check for a registry- or host-supplied file path (load_mandates, load_host_detector, scan_host_guards, scan_ratchet, tests/test_self_host.py:40), and parse_python the one parse-or-skip (four scanners and scan_host_ast_file).
  - spec citation: `None`
- **C70** [shape_fit] [load-bearing]: Building Finding from a validated HostHit in acf.detectors.host is ADJACENT to, not a partial duplicate of, the TypeScript bridge's JSON-to-Finding coercion (typescript_bridge.py:75-95), because the inputs share no format.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:75-95`
- **C71** [shape_fit] [load-bearing]: Building Finding from a HostHit is ADJACENT to the judge's _to_finding (judge.py:238-255): the judge demotes severity by confidence and admits path="<diff>" and line=0, while host findings take severity from the row and require a relative path and line >= 1, so no shared constructor is warranted.
  - spec citation: `plugins/arch-compliance/python/acf/judge.py:236-253`
- **C72** [shape_fit] [load-bearing]: acf/detectors/host.py partially duplicates no existing mechanism: nothing in the plugin today loads or executes code from a registry-supplied file path, and the loader's one-time append of a host root to the end of sys.path is ADJACENT to the hooks' own start-up insertion of the plugin's python/ directory (posttooluse_gate.py:22-26, inject_constraints.py:28-29).
  - spec citation: `None`
- **C73** [shape_fit] [load-bearing]: make_line_lookup consolidates the only two line-lookup closures passed to apply_registry; no third LineLookup implementation exists (e.g. in cli_check_llm.py, the judge, or any skill snippet) that would remain a second definition.
  - spec citation: `None`
- **C74** [shape_fit] [load-bearing]: Detector-reference validation lives in two cooperating places only, Mandate._row_shape (row-local rules, every caller) and load_mandates with known_detectors (built-in contracts and host-file existence); no other validator (the acf-mandate skill's ## Validate snippet, test_profile_drift.py, the architecture-review skill, acf-setup) independently checks detector ids or call sites in a way that would diverge.
  - spec citation: `None`
- **C75** [shape_fit]: Host dispatch in the hook reuses the hook's existing abs_path.relative_to(repo) try/except ValueError (posttooluse_gate.py:242-245) to record in-repo paths in a separate in_repo_rel_paths list, rather than adding a second in-repo test; rel_paths keeps its current contents for the build-artifact guard.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:242-245`
- **C76** [sweep] [load-bearing]: Sweep: the call-site vocabulary in use across shipped registries, tests and the origin host is within CallSite {ci, precommit, hook, posttooluse, audit}; after each ast/guard row declaring ci also declares precommit, every active ast/guard row routes to at least one Tier-1 site at which its detector runs, and audit stays read by no Tier-1 gate.
  - spec citation: `None`
- **C77** [sweep] [load-bearing]: Sweep: the test changes in spec §4.7 cover every existing test the design breaks or makes stale: the ten main([...]) calls in test_diff_cli.py (now passing --call-site), the ten apply_registry calls in test_enforcement.py, test_hooks.py:199-218, test_registry.py:30, test_typescript_pack.py:6 and :14 (TS_DETECTOR_IDS), tests/test_self_host.py:23, :40 and its :5 docstring, test_acf_mandate_skill.py:2, test_adr_host.py and test_portable_guards.py; no other existing test depends on a removed name, the old apply_registry signature, the hook reporting a [ci]-only row, or acf-check-diff running without --call-site.
  - spec citation: `None`
- **C78** [shape_fit] [load-bearing]: The §4.7 contract-against-dispatch test ties KNOWN_DETECTORS' call_sites to the gates' dispatch: a detector the table says runs at a gate but which that gate does not dispatch fails the test; the opposite drift cannot attach a finding to any loaded row, because _check_builtin refuses a row declaring that site and apply_registry drops a finding whose row does not run at the gate, so it over-refuses and never silently drops a row.
  - spec citation: `None`
- **C79** [shape_fit] [load-bearing]: resolve_under_root (relative string -> contained Path) is ADJACENT to abs_path.relative_to(repo) at posttooluse_gate.py:242-245 and the ratchet walk filter at fail_loud_ratchet.py:59-62 (resolved absolute Path -> relative string): they are opposite operations, not two implementations of one.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:242-245`
- **C80** [shape_fit] [load-bearing]: Host code runs only inside load_host_detector's wrapped region (UnknownDetectorError), _call_host's wrapped region, which also rebuilds every yielded item (DetectorPackError), and _describe, which wraps str(exc) with a constant fallback; both handlers and _describe catch every exception but KeyboardInterrupt; the fresh_host_loader fixture is the single reset of loader state and evicts only host modules.
  - spec citation: `None`
- **C81** [sweep]: The §4.7/§4.8 sites cover every shipped doc, skill, docstring, config and test that the design makes stale: every shipped or documented acf-check-diff invocation (.github/workflows/ci.yml:40, README.md:57-58, acf-setup SKILL.md:184, :193, :206, :207, :217, :219 and its success criteria, CLAUDE.md:36, docs/guides/SUPERPOWERS_COMPLEMENT.md:82-83, PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:454), KNOWN_DETECTORS described as a union, the hook's call-site behaviour, apply_registry's drop rules, AdrHostConfig validation (ADR_GATE_HOST_CONTRACT.md:262), and the deleted detector-id sets (PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:421-424, the detectors/__init__.py docstring).
  - spec citation: `None`
- **C82** [shape_fit] [load-bearing]: TS_MANDATE_IDS is the single Python definition of the TypeScript mandate ids: the bridge stamps from it, KNOWN_DETECTORS reads it, and no other non-test Python site spells 'fail-loud.empty-catch' or 'no-shims.explicit-any' as a runtime value; the Node literals are checked against it on every finding.
  - spec citation: `None`
- **C83** [shape_fit]: apply_registry is the single owner of Finding.severity on the Tier-1 path (enforcement.py:52); the host runner's severity value is a required-field fill that apply_registry overwrites, as §4.4 item 5 and §5.2 state.
  - spec citation: `None`
- **C84** [mechanism_justification] [load-bearing]: Deferring host import to dispatch (load_mandates checks reference syntax, Tier-1 site, languages, built-in contracts and host-file existence, and imports nothing) is justified: a missing file still fails at load, an import failure or missing callable fails loud at dispatch as UnknownDetectorError caught by both gates' except tuples, and importing at load would run host code in the SubagentStart hook and acf-check-llm and import CI-only guards on every edit.
  - spec citation: `None`
- **C85** [mechanism_justification] [load-bearing]: The row-shape checks on Mandate (host-reference syntax, a Tier-1 site, host ast languages) together with the per-detector BuiltinDetector contracts (known id, matching mandate_id, declared Tier-1 sites within the contract's call_sites) are sufficient to prevent an active ast/guard row that loads with known_detectors yet is run by neither acf-check-diff (DIFF_CALL_SITES) nor the hook (HOOK_CALL_SITES), or whose findings land on no row.
  - spec citation: `None`
- **C86** [mechanism_justification] [load-bearing]: Refusing a second host root in one process (AcfInputError) rather than evicting the old root is justified: every production caller resolves one repository per process, so the refusal never fires in production, and the only multi-root producer (in-process tests) is handled by the test-only fresh_host_loader fixture; no repair mechanism lives in production code.
  - spec citation: `None`
- **C87** [mechanism_justification] [load-bearing]: Declaring, per built-in detector, the mandate id it reports to and the call sites where a gate runs it (BuiltinDetector in KNOWN_DETECTORS) is justified over the alternatives: the scanners stamp fixed mandate ids and run at fixed gates, so the contract records an existing fact rather than adding a capability; the accepted cost (at most one active row per built-in detector) affects no shipped registry.
  - spec citation: `None`
- **C88** [mechanism_justification]: Moving the row-local rules onto a Mandate model_validator (rather than keeping them in load_mandates) is justified because it makes the SubagentStart hook, acf-check-llm and any direct Mandate construction reject the same malformed rows as the gates, with no caller change since each already handles AcfInputError.
  - spec citation: `None`
- **C89** [mechanism_justification]: Parsing a Python file once and sharing the tree across every host ast detector on it is justified by avoiding N parses per file; built-in scanners keep their own parses unchanged.
  - spec citation: `None`
- **C90** [mechanism_justification] [load-bearing]: Having host callables return HostHit (path, line, message) and building Finding in the runner from the mandate row, rather than accepting Finding and overwriting fields, is justified because apply_registry matches findings to rows by mandate_id (enforcement.py:37-53) and a host-supplied mandate_id/detector/severity could otherwise attach a finding to the wrong row.
  - spec citation: `None`
- **C91** [mechanism_justification] [load-bearing]: Treating the host's own pre-commit/CI invocation of acf-check-diff as its opt-in to running host code, and gating only the automatic hooks on .acf/enabled, is justified because .acf/ is gitignored and CI would otherwise be disabled; a user who runs acf-check-diff manually in an untrusted checkout is the residual case the design accepts.
  - spec citation: `.gitignore:8`
- **C92** [mechanism_justification] [load-bearing]: The call_sites filter added to apply_registry is needed in addition to the scanners' registry.active(call_sites) selection, because some built-in scanners emit findings by detector id without consulting the registry's call_sites, so without the filter a finding for a row not declared at this gate would survive. (The spec states the filter but gives no reason it is not redundant.)
  - spec citation: `None`
- **C93** [mechanism_justification] [load-bearing]: Appending the host root to the end of sys.path rather than inserting it at the front is justified: it adds no shadowing of standard-library, third-party or plugin modules under the hook and console-script entry points, keeps host intra-repo absolute imports working from the host root, and its stated cost (a host top-level name an earlier entry provides resolves to that entry) fails at import or callable lookup as UnknownDetectorError in the common case; dropping the acf/ refusal removes a check with no producer.
  - spec citation: `None`
- **C94** [mechanism_justification] [load-bearing]: Reading flagged files in scan_host_guards, inside each gate's scan try, instead of lazily in the line lookup is justified: it keeps apply_registry free of I/O and new errors, converts an unreadable file to DetectorPackError where both gates already report it, and limits new exemption lines to files a host guard flagged.
  - spec citation: `None`
- **C95** [mechanism_justification]: Enforcing llm prompt ids at load (llm_prompt_ids, passed by acf-check-diff) is justified: it gives acf.judge.LLM_PROMPT_IDS a runtime consumer after it leaves KNOWN_DETECTORS, makes the acf-mandate skill's stated rule true, and refuses no shipped row; registry.py cannot import acf.judge, so the ids are passed in rather than imported.
  - spec citation: `None`
- **C96** [mechanism_justification] [load-bearing]: A required --call-site argument on acf-check-diff, rather than a default or a site derived from --mode/--base, is justified: the doctrine's ## Declared, never defaulted rule, the origin host's per-site row selection, and the fact that a missing value then fails loud (usage error) instead of silently running the wrong rows; the cost, adding the flag at each existing invocation, is listed per site.
  - spec citation: `None`
- **C97** [mechanism_justification] [load-bearing]: Refusing a --call-site that selects no active ast/guard row (AcfInputError), and adding precommit to every shipped row that declares ci, are justified together: without them the documented pre-commit invocation would run no row and report clean, the false green the origin host's runner already refuses (hm:scripts/ci/run_guards.py:126-130).
  - spec citation: `None`
- **C98** [mechanism_justification] [load-bearing]: Rebuilding each yielded item inside _call_host (exact type, exact field types, then validation) is justified over checking the type in _to_findings: field access and comparisons on an unvalidated host object can run host code, so they must happen inside the wrapped region, and a rebuilt HostHit holds only plain str and int values.
  - spec citation: `None`
- **C99** [mechanism_justification]: Decision 8 (delete what this design makes redundant and switch its callers) is justified over recording duplicates as debt: it removes code, removes completeness claims about remaining breaches, and each switch's behaviour change is checked against every shipped value (spec §4.9, Appendix).
  - spec citation: `None`
- **C100** [implementability] [load-bearing]: Mandate (registry.py:14-27) is a Pydantic BaseModel exposing every field the design reads: id, severity, status, detection, detector, call_sites (list[str]), languages (Literal including 'none'), and params (dict or None); adding an @property is_active and a plain method runs_at to it, and a method active to MandateRegistry, is compatible with its model_config.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:14-27`
- **C101** [implementability] [load-bearing]: Finding (acf/finding.py) can be constructed as Finding(mandate_id=, severity=Severity(mandate.severity), path=, line=, message=, detector=, detection=): those are its fields, Severity is constructible from Mandate.severity's value, and no other required field is missing.
  - spec citation: `None`
- **C102** [implementability] [load-bearing]: apply_registry (enforcement.py) looks up each finding's row via registry.by_id, drops it on the status check at :47 (replaceable by runs_at), and handles exemptions and severity at :49-52 using a LineLookup type that make_line_lookup can return.
  - spec citation: `plugins/arch-compliance/python/acf/enforcement.py:47`
- **C103** [implementability] [load-bearing]: cli_check_diff.py has the hook points the design names with the needed names in scope: load at :70 inside a try whose except tuple at :72 lists AcfInputError, UnknownDetectorError and DetectorPackError (and wraps both load and scan); lookup and apply_registry at :76-82; in the .py branch after scan_fsm_writes (:140-150) repo, text, posix, lines and registry; in the .ts/.tsx branch (:151-156) a read that can bind text; and after the ratchet loop (:168-182) the changed-file list.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:72`
- **C104** [implementability] [load-bearing]: posttooluse_gate.py has the hook points the design names: deferred imports at :91-104, the load try at :106-110, the scan try at :113-117 (whose except can be widened to AcfInputError, DetectorPackError, UnknownDetectorError), lookup/apply_registry at :119-125, inline filters at :229-236 and :284-286, the relative_to with ValueError fallback at :242-245 where an in_repo_rel_paths list can be recorded, the build-artifact loop at :284-294, and text and rel in scope in the .py and TypeScript branches of _scan_paths.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:113-117`
- **C105** [implementability] [load-bearing]: Host-detector failures reach an existing fail-loud handler in both gates, never a traceback: load_host_detector raises UnknownDetectorError for any exception but KeyboardInterrupt during import or lookup and for a stat OSError, AcfInputError for a second root; _call_host raises DetectorPackError for any exception but KeyboardInterrupt from the call, from consuming the result and from rebuilding each item; scan_host_guards raises DetectorPackError for a stat or read OSError; apply_registry does no I/O; cli_check_diff.py:72 and the hook's widened scan except catch all three error types.
  - spec citation: `None`
- **C106** [implementability] [load-bearing]: load_host_detector is implementable as stated: module-level _ACTIVE_ROOT and _MODULE_CACHE, a one-time sys.path.append of the root, file_under_root for the module path, spec_from_file_location with a None spec or loader refused inside the wrapped region, registering in sys.modules before exec_module and removing it if exec_module raises, and exec plus getattr in one try; and the fresh_host_loader fixture isolates in-process tests over several roots, including test_diff_cli.py's in-process main() calls.
  - spec citation: `None`
- **C107** [implementability] [load-bearing]: Registering the module in sys.modules under its name before spec.loader.exec_module(mod) is what lets a host module define a @dataclass under `from __future__ import annotations` (dataclasses resolves sys.modules[cls.__module__]); importlib.util.spec_from_file_location with a synthetic name supports this.
  - spec citation: `None`
- **C108** [implementability] [load-bearing]: The imports the design adds are cycle-free and allowed: acf.registry imports acf.engine, dataclass and Mapping, and nothing from acf.detectors; acf.detectors/__init__ imports acf.registry (BuiltinDetector, call-site sets) and the scanner modules' constants without a cycle; acf.cli_check_diff re-exports KNOWN_DETECTORS from acf.detectors; acf.detectors.host imports registry, finding, engine and exceptions; acf/adr/citations.py importing acf.engine is permitted by test_adr_import_graph.py; and the hook's new deferred imports (from acf.detectors, not acf.cli_check_diff) do not reach acf.adr or acf.judge.
  - spec citation: `plugins/arch-compliance/tests/test_adr_import_graph.py:70-76`
- **C109** [implementability] [load-bearing]: load_mandates today loads rows via load_model_file(path, Mandate, subject='mandates file', fmt='yaml', many=True) returning a list of Mandate, and builds MandateRegistry(mandates=..., source_path=path.as_posix()), so the §4.2 body is a drop-in extension of the existing function.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:48-64`
- **C110** [implementability]: plugins/arch-compliance/tests/test_repo_paths.py:47-48 pins the text of posttooluse_gate.py's docstring line :11 and not :12, so rewording :12 and keeping :11 verbatim breaks no test.
  - spec citation: `plugins/arch-compliance/tests/test_repo_paths.py:47-48`
- **C111** [implementability]: config/architecture/mandates.yml:60 declares fail-loud.bare-except-ok for fail-loud.bare-except; the design's handlers are tuple handlers `except (Exception, SystemExit)`, which _is_bare_or_exception (python_pack.py:78-82) does not flag, so they pass the gate whether or not they carry the token, and the spec says the token marks breadth for readers.
  - spec citation: `None`
- **C112** [implementability]: acf/engine.py already defines contains_backslash and is stdlib-only, so adding looks_absolute, resolve_under_root and validate_posix_rel_path with `import re` and `from pathlib import Path` keeps it stdlib-only and gives validate_posix_rel_path its backslash test without a new dependency.
  - spec citation: `plugins/arch-compliance/python/acf/engine.py`
- **C113** [implementability] [load-bearing]: The new tests are implementable against the shipped files: test_builtin_detectors.py can parse the README.md detector table (:66-74) for detector ids and mandate ids and read mandate_id values from emptyCatch.ts:23 and explicitAny.ts:15; and the test_registry.py cases (a fail_loud_ratchet row declaring hook, a fail_loud_bare_except row with another id, an ast row naming an LLM prompt id, a module that raises at import not imported by load_mandates) can be expressed as inline YAML registries like the existing :24 and :35 rows.
  - spec citation: `None`
- **C114** [implementability] [load-bearing]: The contract-against-dispatch test is implementable: acf-check-diff runs in process on a temporary git repository once with --call-site ci and once with --call-site precommit, and the hook in a subprocess with .acf/enabled; a fixture tree can trigger each built-in detector the table assigns to that gate, with one active row per such detector declaring only that gate's sites.
  - spec citation: `None`
- **C115** [implementability] [load-bearing]: scan_host_guards(repo_root, changed_files, registry, file_lines, *, call_sites) is implementable in both gates: file_lines is in scope after each gate's dispatch (cli_check_diff _scan_changed returns it; _scan_paths builds it), the call can run inside _scan_changed and _scan_paths so it sits under each gate's scan try, and filling only missing keys keeps the gate's own reads.
  - spec citation: `None`
- **C116** [implementability] [load-bearing]: The required --call-site argument is implementable at cli_check_diff.py:29-71: argparse required=True with choices=sorted(DIFF_CALL_SITES) exits 2 on a missing or unknown value (SystemExit in process, so test_diff_cli asserts it with pytest.raises), sites = frozenset({args.call_site}) reaches _scan_changed and apply_registry, and the empty-selection refusal can raise AcfInputError inside the existing try at :69-74.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:29-61`
