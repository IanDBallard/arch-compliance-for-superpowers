# Adversarial design review — full detail

Spec: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md` @ `e7dce40d3c231230ed235b559c7346b98238dfd2`
Kinds: defect, feature
Outcome: **BLOCKED**
Claims: 76 · Reviewers: 4 · Converged: 4

## Blocking reasons

- load-bearing claim C10 (premise) is REFUTED: The factual parts hold: PosixStr wraps _reject_backslash and refuses only backslashes, and the two citations helpers classify strings. The final link fails. test_hooks_do_not_reach_acf_adr only asserts that the literal text 'acf.adr' is absent from the two hook source files. Its docstring's reason is the pre-gate, pydantic-free import graph. After the .acf/enabled gate the hook already imports pydantic-backed modules (acf.enforcement, acf.registry at :91-95). acf.adr imports only acf.engine and acf.exceptions from the rest of the package (contract.py:20), so there is no cycle. A hook-reachable module such as acf.registry could import from acf.adr.citations and pass that test. The test does not establish that these helpers cannot serve a hook-reachable caller. Moving them to acf.engine may still be right on layering grounds, but this premise does not prove it.
- load-bearing claim C29 (mandate) is UNPROVEN: ARCHITECTURE.md:29-30 forbids broad `except Exception` handlers that swallow errors unless they are exempted with a reason. Both handlers re-raise as typed errors and carry the token, so that half of the claim holds: python_pack.py:80 flags `except Exception`, and mandates.yml:60 declares the token. The other half is that every §6.1 state is refused 'by the named component with the named error'. The design does not establish it. §4.3 item 5 (spec :247) wraps only the call `fn(...)`. The signature returns `Iterable[HostHit]`, and the natural way to write that is a generator using `yield HostHit(...)`. A generator body runs only when it is iterated, which happens in `_to_findings` (spec :243), and the design does not place that inside the try. So an exception raised in a generator body escapes unwrapped. That includes a `HostHit` ValidationError, which §6.1 says is 'raised inside the callable, wrapped'. It never becomes DetectorPackError, and neither gate's except tuple catches it (cli_check_diff.py:72; posttooluse_gate.py:115). Two smaller gaps. `except Exception` does not catch SystemExit, which contradicts '(any exception)' at spec :384. The §6.1 row 'Active host row, no repo_root given → load_mandates' (spec :380) omits the 'with known_detectors' condition that the §4.2 code imposes.
- load-bearing claim C30 (mandate) is REFUTED: The claim is that no active ast/guard row can load with known_detectors and then never be executed by either Tier-1 gate. Under the §4.2 checks that is false, and the design creates one of the counterexamples itself. (1) A `fail_loud_ratchet` guard row with `call_sites: [hook]` or `[posttooluse]` passes load. It intersects TIER1_CALL_SITES, and its id is in KNOWN_DETECTORS. But only acf-check-diff runs the ratchet (cli_check_diff.py:168), and §4.5 changes that loop to `registry.active(DIFF_CALL_SITES, ...)`, which skips the row. The hook never imports a ratchet scanner (posttooluse_gate.py:216-223). The row loads and nothing ever runs it. (2) KNOWN_DETECTORS includes LLM_PROMPT_IDS (cli_check_diff.py:25). An active `detection: ast` row whose detector is `llm_fail_loud` passes the built-in check, and no Tier-1 scanner dispatches on that id. (3) Built-in scanners stamp a fixed mandate_id (python_pack.py:67). An active row with its own id and `detector: fail_loud_bare_except` loads, but its findings carry the fixed id and never map to that row. All three are rows that load and never execute: the silent failure ## Fail loud forbids, and the defect §1 item 1 sets out to close.
- load-bearing claim C58 (mechanism_justification) is REFUTED: The two checks are not sufficient. (1) The hook never runs fail_loud_ratchet: _scan_paths (posttooluse_gate.py:213-295) has no ratchet call, and only cli_check_diff.py:168-182 runs it. An active `guard` row with detector fail_loud_ratchet and call_sites [hook] passes the Tier-1 check, since hook is in TIER1, and passes the known_detectors check. The diff gate then drops it because it is not in DIFF_CALL_SITES, and the hook never dispatches it, so no gate runs it. (2) KNOWN_DETECTORS (cli_check_diff.py:25) includes LLM_PROMPT_IDS. An `ast` row naming llm_fail_loud with [ci, hook] loads, but no Tier-1 scanner emits for it. (3) Built-in scanners hard-code mandate_id (python_pack.py:66 emits 'fail-loud.bare-except'), and apply_registry matches by mandate_id (enforcement.py:46). An active row with any other id and detector fail_loud_bare_except therefore loads and never produces a kept finding. The load check is per row and does not ask whether a gate at that row's call site actually dispatches that detector.
- load-bearing claim C59 (mechanism_justification) is REFUTED: The import at hm metadata_facade_guard.py:66 (`from scripts.ci.arch_compliance.facade_sinks import ...`) justifies putting the root on sys.path. It does not justify eviction, which needs a second root, and one root is enough for that import. Every production caller resolves exactly one repo per process (cli_check_diff.py:63, posttooluse_gate.py:65; the hook is a fresh process per edit). The only producer of the multi-root state is in-process tests, such as test_diff_cli.py:48 calling main() once per tmp repo. The spec's whole justification is "the eviction keeps in-process test runs over several tmp_path roots isolated". That puts a silent repair in production code for a state only the test harness produces. A rung-3 alternative was not considered: the loader raises on a second distinct root, and multi-root tests run the gate in a subprocess, as test_diff_cli.py:129 already does, or reset the loader through a test fixture.
- load-bearing claim C69 (implementability) is REFUTED: The spec wraps only the call `fn(text, path, added_lines, ...)` (spec :247, and :248 for guards). _to_findings (spec :243) refuses only shape errors. The host contract returns Iterable[HostHit], which invites a generator. A generator's body, including HostHit(...) construction, runs during iteration inside _to_findings, outside the wrapping try. An exception raised there therefore escapes unwrapped. That includes a pydantic ValidationError (a ValueError, not an AcfError) for a bad path or line, which spec §6.1 claims is 'raised inside the callable, wrapped'. Neither cli_check_diff.py:72 nor the hook's widened except catches it, so it ends as a traceback. In addition, `except Exception` does not catch SystemExit or KeyboardInterrupt, so a host callable that calls sys.exit also escapes. The claim that 'no host failure escapes as a traceback' does not hold as written.
- mandate claim C30 is REFUTED: The claim is that no active ast/guard row can load with known_detectors and then never be executed by either Tier-1 gate. Under the §4.2 checks that is false, and the design creates one of the counterexamples itself. (1) A `fail_loud_ratchet` guard row with `call_sites: [hook]` or `[posttooluse]` passes load. It intersects TIER1_CALL_SITES, and its id is in KNOWN_DETECTORS. But only acf-check-diff runs the ratchet (cli_check_diff.py:168), and §4.5 changes that loop to `registry.active(DIFF_CALL_SITES, ...)`, which skips the row. The hook never imports a ratchet scanner (posttooluse_gate.py:216-223). The row loads and nothing ever runs it. (2) KNOWN_DETECTORS includes LLM_PROMPT_IDS (cli_check_diff.py:25). An active `detection: ast` row whose detector is `llm_fail_loud` passes the built-in check, and no Tier-1 scanner dispatches on that id. (3) Built-in scanners stamp a fixed mandate_id (python_pack.py:67). An active row with its own id and `detector: fail_loud_bare_except` loads, but its findings carry the fixed id and never map to that row. All three are rows that load and never execute: the silent failure ## Fail loud forbids, and the defect §1 item 1 sets out to close.
- implementability claim C69 is REFUTED: The spec wraps only the call `fn(text, path, added_lines, ...)` (spec :247, and :248 for guards). _to_findings (spec :243) refuses only shape errors. The host contract returns Iterable[HostHit], which invites a generator. A generator's body, including HostHit(...) construction, runs during iteration inside _to_findings, outside the wrapping try. An exception raised there therefore escapes unwrapped. That includes a pydantic ValidationError (a ValueError, not an AcfError) for a bad path or line, which spec §6.1 claims is 'raised inside the callable, wrapped'. Neither cli_check_diff.py:72 nor the hook's widened except catches it, so it ends as a traceback. In addition, `except Exception` does not catch SystemExit or KeyboardInterrupt, so a host callable that calls sys.exit also escapes. The claim that 'no host failure escapes as a traceback' does not hold as written.

## Absorptions

- SUBSUMED: 'acf.engine.looks_absolute / resolve_under_root' shares responsibility 'classify a path string as absolute / escaping the repo root' with plugins/arch-compliance/python/acf/adr/citations.py:49-51 — As designed: citations' _looks_absolute and _escapes_repo are deleted and their call sites consume acf.engine.
- PARTIAL_OVERLAP: 'acf.engine.resolve_under_root' shares responsibility 'decide whether a path lies under the repo root' with plugins/arch-compliance/hooks/posttooluse_gate.py:242-245 — R = repo-membership test. Route the hook's relative_to/ValueError test (used for host-dispatch eligibility) and fail_loud_ratchet.py:59-62 through resolve_under_root, or justify in writing why the resolved-Path relative_to stays a separate owner.
- PARTIAL_OVERLAP: 'acf.engine.resolve_under_root' shares responsibility 'decide whether a path lies under the repo root' with plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:59-62 — Same R as above. The ratchet's walk-filter becomes a resolve_under_root consumer, or it is listed as an out-of-scope owner under ## Scoped refactor.
- SUBSUMED: 'Mandate.runs_at / MandateRegistry.active' shares responsibility 'decide whether a row is live at a gate' with plugins/arch-compliance/python/acf/cli_check_diff.py:94-99 — As designed: _active_mandates, the three hook filters and the enforcement.py:47 filter call runs_at/active.
- PARTIAL_OVERLAP: 'load_mandates host-reference existence check' shares responsibility 'verify a detector field names an existing file under the repo root' with tests/test_self_host.py:40 — R = detector-file existence under root. Expose one registry helper (resolve_under_root + is_file) used by load_mandates' host branch and by test_self_host's manual-row check.
- IDENTICAL: 'make_line_lookup' shares responsibility "resolve a finding's source line for exemption checks" with plugins/arch-compliance/hooks/posttooluse_gate.py:119-123 — As designed: both closures (this one and cli_check_diff.py:76-80) are deleted in favour of enforcement.make_line_lookup.
- PARTIAL_OVERLAP: 'load_host_detector sys.path insertion' shares responsibility 'control import resolution order via sys.path[0]' with plugins/arch-compliance/hooks/posttooluse_gate.py:25-26 — R = owning sys.path order in the hook process. State the precedence between the plugin python/ root and the host root (for example, append the host root, or refuse a host root that would shadow 'acf'). Restrict eviction to modules registered by the loader, not every module under the old root.
- PARTIAL_OVERLAP: 'scan_host_ast_file shared ast.parse' shares responsibility 'parse Python source, skipping on SyntaxError' with plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37 — R = parse-or-skip. Add an engine-level parse helper consumed by python_pack, facade_sinks, fsm_guard, fail_loud_ratchet and the host runner, or record it as deferred under ## Scoped refactor.
- mechanism 'parse_host_detector_ref syntax validation in load_mandates (every load)' sits at rung 3 when rung 1 applies, with no written justification
- mechanism 'Tier-1 call-site requirement for active ast/guard rows (load_mandates with known_detectors)' sits at rung 3 when rung 1 applies, with no written justification

## Converged findings

- [3 reviewers: refuter, sweeper, hardening] plugins/arch-compliance/tests/test_engine_paths.py already exists and is tracked (contains_backslash/posix_path tests); spec section 4.6 marks it '(new)', so the new cases must extend it rather than create it.
  - evidence: `plugins/arch-compliance/tests/test_engine_paths.py:1-26`
- [2 reviewers: compliance, hardening] The DetectorPackError wrap covers only the call fn(...); a host callable written as a generator (the natural Iterable[HostHit] form) raises during iteration inside _to_findings, outside the try, so its exceptions, including HostHit ValidationError, escape both gates as tracebacks; SystemExit is not caught by except Exception either.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:247`
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:243`
- [2 reviewers: compliance, hardening] Active built-in ast/guard rows can still load with known_detectors and be run by no gate: a fail_loud_ratchet row declaring only hook/posttooluse (only acf-check-diff runs the ratchet), an ast/guard row naming an LLM prompt id (KNOWN_DETECTORS includes LLM_PROMPT_IDS), and a row whose id differs from the built-in scanner's hard-coded mandate_id.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:168`
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:25`
  - evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:66`
- [2 reviewers: refuter, sweeper] Row activity keeps a separate Tier-2 definition (run_judge reviews every llm row, unenforced included), so the 'one definition' of row activity holds only within Decision 2's Tier-1 scope and section 6 should say so.
  - evidence: `plugins/arch-compliance/python/acf/judge.py:214`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:56-63; plugins/arch-compliance/tests/test_registry.py:20-30`
- reasoning: load_mandates checks rows only when known_detectors is given (:56). It skips any row whose status != 'enforced' (:58) and raises UnknownDetectorError only for detection in {ast, guard} with a detector not in known_detectors (:60-63). test_registry.py:20-30 pins the enforced/ast case.

#### C2 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:47; plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; plugins/arch-compliance/hooks/posttooluse_gate.py:229-236,284-286; plugins/arch-compliance/python/acf/registry.py:58`
- reasoning: apply_registry drops only unenforced or unknown rows. _active_mandates and the hook's inline filters keep any status != 'unenforced', so partial rows are live in both gates. registry.py:58 skips partial rows, so a partial ast/guard row with an arbitrary detector loads cleanly with KNOWN_DETECTORS. Both gates dispatch only built-in scanners by fixed id, so nothing would execute such a row. Each link holds.

#### C3 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:25; plugins/arch-compliance/python/acf/detectors/__init__.py:28; tests/test_self_host.py:23`
- reasoning: I ran git grep -n KNOWN_DETECTORS -- plugins tests. Hits: the definition at cli_check_diff.py:25, the use at :70, SKILL.md:91-112 (import and prose), test_profile_drift.py:7,24 and test_self_host.py:5,14,23. All are reads; none mutates or extends the set. It is the union of frozensets ALL_PYTHON_DETECTOR_IDS | TS_DETECTOR_IDS | LLM_PROMPT_IDS.

#### C4 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:112-182; plugins/arch-compliance/hooks/posttooluse_gate.py:216-294`
- reasoning: Both scan functions import and call only built-in scanners: scan_python_file, scan_facade_sinks, scan_fsm_writes, scan_typescript_file, scan_build_artifact_paths, plus scan_ratchet in the diff gate. Config-driven ones are picked by exact built-in id constants. scan_python_file and scan_typescript_file run unconditionally and emit built-in ids. The git grep for importlib|import_module|spec_from_file_location|exec_module over the plugin python and hooks trees printed nothing.

#### C5 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:107; plugins/arch-compliance/hooks/posttooluse_gate.py:213-295`
- reasoning: :107 calls load_mandates(mandates_path) with no known_detectors, so no detector-id check runs. _scan_paths dispatches only built-in scanners, so a row naming an unknown detector yields no findings and the hook exits 0 instead of failing.

#### C6 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:106-110; plugins/arch-compliance/python/acf/exceptions.py:5,13`
- reasoning: The hook's try around load_mandates catches only AcfInputError (:108). UnknownDetectorError(AcfError) is a sibling of AcfInputError(AcfError), not a subclass, so it would escape uncaught unless the except is widened.

#### C7 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:21; plugins/arch-compliance/python/acf/adr/ledger.py:42,83; plugins/arch-compliance/python/acf/enforcement.py:47`
- reasoning: git grep -n call_sites over the plugin python and hooks trees printed exactly registry.py:21 and ledger.py:42 and :83 (surface_call_sites, unrelated). Row selection in both gates and in apply_registry reads only detector and status.

#### C8 — SURVIVED
- evidence: `config/architecture/mandates.yml:64-72; plugins/arch-compliance/tests/fixtures/mandates_valid.yml:12-20; plugins/arch-compliance/tests/test_hooks.py:55-62,199-218`
- reasoning: This repo's no-shims.hasattr declares call_sites [ci] (:70). test_hooks.py:199-218 seeds the host from the fixture mandates_valid.yml (_seed_host copies MANDATES_SRC), whose no-shims.hasattr is also [ci]. It then asserts that the hook reports 'no-shims.hasattr' in additionalContext. So the test pins hook reporting of a [ci]-only row, as claimed. Strictly it pins the fixture's row, not mandates.yml:70; spec section 4.6 states that correctly.

#### C9 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:119-123,248-252; plugins/arch-compliance/python/acf/cli_check_diff.py:76-80,124-126,151-152; plugins/arch-compliance/python/acf/enforcement.py:49-50`
- reasoning: The two closures are textually identical. file_lines is filled only in the .py and .ts/.tsx branches; the hook skips non-code suffixes at :248-249 before :251-252. A finding on any other path, such as a build-artifact guard finding on a changed non-code path, gets an empty line, so token_exempted cannot match.

#### C10 — REFUTED
- evidence: `plugins/arch-compliance/tests/test_adr_import_graph.py:70-76; plugins/arch-compliance/hooks/posttooluse_gate.py:91-95; plugins/arch-compliance/python/acf/adr/contract.py:20,60; plugins/arch-compliance/python/acf/adr/citations.py:49-51,74-76`
- reasoning: The factual parts hold: PosixStr wraps _reject_backslash and refuses only backslashes, and the two citations helpers classify strings. The final link fails. test_hooks_do_not_reach_acf_adr only asserts that the literal text 'acf.adr' is absent from the two hook source files. Its docstring's reason is the pre-gate, pydantic-free import graph. After the .acf/enabled gate the hook already imports pydantic-backed modules (acf.enforcement, acf.registry at :91-95). acf.adr imports only acf.engine and acf.exceptions from the rest of the package (contract.py:20), so there is no cycle. A hook-reachable module such as acf.registry could import from acf.adr.citations and pass that test. The test does not establish that these helpers cannot serve a hook-reachable caller. Moving them to acf.engine may still be right on layering grounds, but this premise does not prove it.

#### C11 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:214-230; plugins/arch-compliance/python/acf/cli_check_llm.py:54-66`
- reasoning: run_judge selects rows by detection == 'llm' (:214) and reads status == 'enforced' only to set has_enforced for provider resolution (:218-224). It reviews every llm row (:230). cli_check_llm passes registry.mandates unfiltered and does not call apply_registry. Neither path uses _active_mandates or the hook filters, so the Tier-1 replacement does not touch it.

#### C12 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:15-28,72-81; plugins/arch-compliance/python/acf/repo.py:1-9`
- reasoning: Module-scope imports are stdlib plus acf.repo, which is stdlib-only (repo.py:1-9), and acf/__init__.py is empty. main() parses args, reads stdin JSON and resolves the repo, then returns 0 at :72-81 when .acf/enabled is absent. All other acf imports and load_mandates come after :91, so no host module can be imported before the gate.

#### C13 — SURVIVED
- evidence: `.gitignore:8; .github/workflows/ci.yml:40; plugins/arch-compliance/python/acf/cli_check_diff.py:63-71`
- reasoning: .acf/ is ignored (.gitignore:8) and git ls-files .acf prints nothing. CI runs python -m acf.cli_check_diff (ci.yml:40). cli_check_diff never references ENABLED_REL; a git grep shows it only in repo.py:29 and the hooks. So requiring the marker would make CI no-op or fail.

#### C14 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:103-107; plugins/arch-compliance/python/acf/cli_check_llm.py:54`
- reasoning: inject_constraints wraps load_mandates in except AcfInputError (:104-105). cli_check_llm:54 has no handler, so an AcfInputError surfaces as a traceback and non-zero exit. That is the same treatment it gives any malformed registry today, so it still fails loud and needs no change. A clean message would need one.

#### C15 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:14-17; plugins/arch-compliance/hooks/inject_constraints.py:31,91-92,163,170; plugins/arch-compliance/python/acf/cli_check_llm.py:10-13`
- reasoning: The SubagentStart hook imports acf.repo, acf.exceptions, acf.registry, acf.loader and acf.template. acf-check-llm imports acf.finding, acf.judge, acf.registry and acf.repo; judge imports exceptions, finding, registry and template. None imports acf.detectors. Under the design registry imports only acf.engine (stdlib), so neither entry point reaches a host loader, and load_mandates does no import as specified.

#### C16 — SURVIVED
- evidence: `plugins/arch-compliance/skills/architecture-review/SKILL.md:62; config/architecture/adr.yml:1`
- reasoning: git ls-files plugins/arch-compliance/python/acf | grep -i review printed nothing. config/architecture holds only ARCHITECTURE.md, adr.yml (the ADR gate's declaration) and mandates.yml. The architecture-review skill is prose that loads the registry inline (SKILL.md:62); it has no runtime package or host config.

#### C17 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:20,24; hm:config/architecture/mandates.yml:5-14 (git show b652fab05)`
- reasoning: Mandate declares languages and arch_anchor without defaults (:20, :24). At b652fab05 the HM mandates.yml rows carry gemini_anchor and no languages field. grep -c 'languages|arch_anchor' printed 0. Every row would fail Mandate validation as-is.

#### C18 — SURVIVED
- evidence: `hm:scripts/ci/arch_compliance/driver.py:142-161; hm:scripts/ci/arch_compliance/driver.py:92-100; plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37`
- reasoning: In driver.run, a SyntaxError on a changed file raises in range mode and otherwise appends a WARN 'parse' finding. Those lines are 150-161; the cited 139-157 is slightly off and starts inside worst_severity. The guards read cf.content, the staged/HEAD/range blob (driver.py:92-96), so their input depends on diff mode. A host guard given repo_root and paths can re-parse, but from the worktree, not the staged blob.

#### C19 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:211-215; plugins/arch-compliance/python/acf/cli_check_diff.py:110-121; plugins/arch-compliance/hooks/posttooluse_gate.py:238-254`
- reasoning: _scan_changed takes paths from changed_files and passes added_lines per file. _scan_paths takes edited paths, passes added_lines=None (whole file) and filters on _CODE_SUFFIXES while collecting rel_paths for every file. The three differences are real. The Scoped refactor section exists at :211-215.

#### C20 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:23-26`
- reasoning: scan_python_file wraps ast.parse in try and returns [] on SyntaxError (:34-37). count_bare_excepts in fail_loud_ratchet.py:23-26 follows the same skip convention.

#### C21 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:104; plugins/arch-compliance/python/acf/cli_check_llm.py:54; plugins/arch-compliance/tests/test_registry.py:10,17,30,47,57; plugins/arch-compliance/tests/test_profile_drift.py:24; tests/test_self_host.py:23`
- reasoning: I re-ran the git grep recipe. Its output matches the appendix list exactly, including SKILL.md:95 and :141 and architecture-review SKILL.md:62. Only cli_check_diff.py:70, acf-mandate SKILL.md:95, test_profile_drift.py:24, test_registry.py:30 and test_self_host.py:23 pass known_detectors. The SKILL.md:95 snippet is also executed by plugins/arch-compliance/tests/test_acf_mandate_skill.py (see unanchored finding).

#### C22 — SURVIVED
- evidence: `config/architecture/mandates.yml:64-72; plugins/arch-compliance/profiles/react-app/mandates.yml; plugins/arch-compliance/tests/test_diff_cli.py:71-81; plugins/arch-compliance/tests/test_registry.py:20-30; plugins/arch-compliance/tests/test_enforcement.py:26`
- reasoning: I ran the census over mandates.yml, both profiles and mandates_valid.yml. Every active ast/guard row has 'ci' ([ci] or [ci, hook]). The only partial rows are llm rows (soft.fail-loud, react-app soft.react-boundaries), so no partial ast/guard row exists. Inline test registries: test_diff_cli's _BARE_EXCEPT_ROW is [ci, hook] with a built-in detector. test_registry's unknown-detector row is [ci], so it passes the Tier-1 check and still raises UnknownDetectorError. Its _ROW rows are manual/[audit] and are loaded without known_detectors. test_enforcement and test_judge build Mandate objects directly ([ci]) or use llm rows, which load_mandates never sees. None is newly rejected.

#### C23 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:16-22; plugins/arch-compliance/python/acf/detectors/__init__.py:11-18; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:14; plugins/arch-compliance/python/acf/judge.py:29-36`
- reasoning: I counted from source: 3 Python AST ids, 4 guard ids (build_artifacts, fail_loud_ratchet, facade_sink, fsm_guard), 2 TS ids and 4 LLM prompt ids. All are distinct, giving 13.

#### C24 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:125; plugins/arch-compliance/python/acf/cli_check_diff.py:82; plugins/arch-compliance/tests/test_enforcement.py:54`
- reasoning: git grep -n 'apply_registry(' -- '*.py' printed the definition at enforcement.py:37, posttooluse_gate.py:125, cli_check_diff.py:82 and test_enforcement.py:54,60,66,72,84,94,104,110,125,130. No other caller exists.

#### C25 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94,98,112,113,158,168; plugins/arch-compliance/hooks/posttooluse_gate.py:231,235,285; plugins/arch-compliance/python/acf/enforcement.py:47; plugins/arch-compliance/python/acf/judge.py:218; plugins/arch-compliance/hooks/inject_constraints.py:158`
- reasoning: I re-ran both recipes and the output matches. The wider '.status' recipe adds exactly registry.py:58, judge.py:218 and the display-only f-string at inject_constraints.py:158.

#### C26 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/citations.py:49-51,74-76,161,163; plugins/arch-compliance/tests/test_adr_citations.py:139-140; docs/design/ADR_GATE_HOST_CONTRACT.md:302-303`
- reasoning: git grep for _looks_absolute|_escapes_repo found code only at citations.py:49,74,161,163; ADR_GATE_HOST_CONTRACT.md:302-303 is prose that section 4.7 updates. No test imports either helper. The proposed regex ^([A-Za-z]:|/|\\) differs from the old ^([A-Za-z]:[\/]|/|\\) only for a single letter plus colon not followed by a separator, such as 'C:a/b.py' or a bare 'C:'. resolve_under_root(root, p) is None equals the old not (root.resolve()/p).resolve().is_relative_to(root.resolve()). The existing absolute-path test (G:/...) still classifies external.

#### C27 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80; plugins/arch-compliance/hooks/posttooluse_gate.py:119-123`
- reasoning: For a key present in file_lines, the new lookup returns lines[line-1] when 0 < line <= len and '' otherwise, the same as the old closure (an empty list gives '' either way). Only a missing key behaves differently: it now reads from disk under the root, or gives '' for a backslash, escaping or non-file path. It also caches into file_lines. An OSError propagates, as the spec says.

#### C28 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; plugins/arch-compliance/hooks/posttooluse_gate.py:229-236,284-286; config/architecture/mandates.yml:70; plugins/arch-compliance/profiles/python-service/mandates.yml`
- reasoning: registry.active(cs, detector=X) equals the old filter (detector == X and status != unenforced) plus the call_sites intersection. In every shipped registry, every active Tier-1 row includes 'ci', so the diff gate loses nothing. Rows without 'hook' are no-shims.hasattr (active, [ci]) and fail-loud.ratchet ([ci] but unenforced, already excluded), so only no-shims.hasattr leaves the hook. llm rows produce no Tier-1 findings.

### Unanchored findings

- **important**: Section 4.6 lists plugins/arch-compliance/tests/test_engine_paths.py as a new file, and the citation map calls it proposed. It already exists (commit 0b7b0af) with contains_backslash/posix_path tests, so the plan must extend it, not create it.
  - evidence: `plugins/arch-compliance/tests/test_engine_paths.py:1-26`
- **advisory**: plugins/arch-compliance/tests/test_acf_mandate_skill.py extracts and runs the acf-mandate SKILL.md Validate snippet with a regex (cwd=host). Section 4.7 rewrites that snippet but section 4.6 does not list this test, which constrains the snippet's shape and the resolve_repo(None) behaviour.
  - evidence: `plugins/arch-compliance/tests/test_acf_mandate_skill.py:20-25`
- **advisory**: The advice to report parse failures from a host guard is lossy. HostHit needs line >= 1 while the origin driver emits lineno 0 for some parse findings, and a guard row has one fixed severity and no diff mode, so it cannot reproduce WARN-in-staged / raise-in-range.
  - evidence: `hm:scripts/ci/arch_compliance/driver.py:150-161`
- **advisory**: Tier-2 run_judge reviews every detection: llm row, unenforced included, and cli_check_llm does not filter it through apply_registry. So Mandate.is_active is not the plugin-wide definition of a live row, even though Decision 2 presents it as 'one definition' (scoped to Tier-1).
  - evidence: `plugins/arch-compliance/python/acf/judge.py:214`

### Looked for but did not find

- any code reference to _looks_absolute or _escapes_repo outside citations.py:161,163 (tests or other modules)
- any mutation or extension of KNOWN_DETECTORS in plugins/ or tests/
- any dynamic import machinery (importlib, import_module, spec_from_file_location, exec_module) in plugins/arch-compliance/python or hooks
- any reader of Mandate.call_sites in the Tier-1 gates or apply_registry
- any status: partial ast/guard row in config/architecture/mandates.yml, the two profiles or mandates_valid.yml
- any inline test YAML registry with an active ast/guard row lacking ci/hook/precommit/posttooluse
- any check of .acf/enabled in cli_check_diff.py
- any import of acf.detectors from judge.py, template.py, loader.py or inject_constraints.py
- an import cycle risk from acf.adr importing acf.registry (acf.adr imports only acf.engine and acf.exceptions from the rest of the package)

## compliance

### Claim verdicts

#### C29 — UNPROVEN
- evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:247; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:243; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:384; plugins/arch-compliance/python/acf/detectors/python_pack.py:77-82; config/architecture/mandates.yml:60`
- reasoning: ARCHITECTURE.md:29-30 forbids broad `except Exception` handlers that swallow errors unless they are exempted with a reason. Both handlers re-raise as typed errors and carry the token, so that half of the claim holds: python_pack.py:80 flags `except Exception`, and mandates.yml:60 declares the token. The other half is that every §6.1 state is refused 'by the named component with the named error'. The design does not establish it. §4.3 item 5 (spec :247) wraps only the call `fn(...)`. The signature returns `Iterable[HostHit]`, and the natural way to write that is a generator using `yield HostHit(...)`. A generator body runs only when it is iterated, which happens in `_to_findings` (spec :243), and the design does not place that inside the try. So an exception raised in a generator body escapes unwrapped. That includes a `HostHit` ValidationError, which §6.1 says is 'raised inside the callable, wrapped'. It never becomes DetectorPackError, and neither gate's except tuple catches it (cli_check_diff.py:72; posttooluse_gate.py:115). Two smaller gaps. `except Exception` does not catch SystemExit, which contradicts '(any exception)' at spec :384. The §6.1 row 'Active host row, no repo_root given → load_mandates' (spec :380) omits the 'with known_detectors' condition that the §4.2 code imposes.

#### C30 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:25; plugins/arch-compliance/python/acf/cli_check_diff.py:168; plugins/arch-compliance/hooks/posttooluse_gate.py:216-223; plugins/arch-compliance/python/acf/detectors/python_pack.py:67`
- reasoning: The claim is that no active ast/guard row can load with known_detectors and then never be executed by either Tier-1 gate. Under the §4.2 checks that is false, and the design creates one of the counterexamples itself. (1) A `fail_loud_ratchet` guard row with `call_sites: [hook]` or `[posttooluse]` passes load. It intersects TIER1_CALL_SITES, and its id is in KNOWN_DETECTORS. But only acf-check-diff runs the ratchet (cli_check_diff.py:168), and §4.5 changes that loop to `registry.active(DIFF_CALL_SITES, ...)`, which skips the row. The hook never imports a ratchet scanner (posttooluse_gate.py:216-223). The row loads and nothing ever runs it. (2) KNOWN_DETECTORS includes LLM_PROMPT_IDS (cli_check_diff.py:25). An active `detection: ast` row whose detector is `llm_fail_loud` passes the built-in check, and no Tier-1 scanner dispatches on that id. (3) Built-in scanners stamp a fixed mandate_id (python_pack.py:67). An active row with its own id and `detector: fail_loud_bare_except` loads, but its findings carry the fixed id and never map to that row. All three are rows that load and never execute: the silent failure ## Fail loud forbids, and the defect §1 item 1 sets out to close.

#### C31 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:120-127; plugins/arch-compliance/python/acf/repo.py:32-44; plugins/arch-compliance/python/acf/cli_check_diff.py:63`
- reasoning: ## Declared, never defaulted says no default stands in for a missing declaration. §4.2 raises AcfInputError when repo_root is None for an active host row. §4.4 declares `call_sites` keyword-only with no default. The repo value both gates pass comes from resolve_repo, whose fallback to the process directory (repo.py:44) is explicitly recorded as outside this rule (ARCHITECTURE.md:124-127). The claim therefore holds at load_mandates and at apply_registry. The section's own scope is the ADR gate's adr.yml values; applying it here is by analogy, but nothing contradicts it.

#### C32 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:48-49; plugins/arch-compliance/python/acf/detectors/python_pack.py:91; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:242`
- reasoning: The rule is 'Do not probe optional attributes with `hasattr` to paper over missing interfaces.' The design looks the callable up with `getattr(mod, attr, None)`, then checks `callable(fn)`, and raises UnknownDetectorError on a miss. That fails loud; it is not a probe that degrades quietly. It also does not trip the hasattr detector (python_pack.py:91). The one skip, `ast.parse` SyntaxError → [], follows the built-in convention and is declared openly in §3 non-goals, so it is not a hidden fallback.

#### C33 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:57-58; plugins/arch-compliance/python/acf/engine.py:17-24; plugins/arch-compliance/python/acf/cli_check_diff.py:85`
- reasoning: The rule requires POSIX paths in persisted YAML/JSON. HostHit.path flows into Finding.path, which `--json` serializes (cli_check_diff.py:85). validate_posix_rel_path refuses backslashes through contains_backslash (engine.py:17-24) and also refuses absolute paths and paths with dot segments, which is stricter than the rule. The one path-bearing message in §4.2 uses `.as_posix()`.

#### C34 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:101-102; plugins/arch-compliance/python/acf/exceptions.py:13; plugins/arch-compliance/python/acf/exceptions.py:29`
- reasoning: The rule is that every ACF exception subclasses AcfError and nothing else. The design declares no exception class: HostHit is a Pydantic model, not an exception. It reuses AcfInputError (:5), UnknownDetectorError (:13) and DetectorPackError (:29), and each of those subclasses AcfError alone.

#### C35 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_repo_paths.py:14; plugins/arch-compliance/tests/test_repo_paths.py:53-71; plugins/arch-compliance/python/acf/repo.py:15`
- reasoning: The rule makes acf.repo the one declaration of host paths, and its test scans python/ and hooks/ for `config.{0,6}architecture`. The new engine, registry and host.py code shown in §4.1-§4.3 spells no such path; host.py puts the host root on sys.path, which is not a config path. The new acf-mandate snippet takes MANDATES_REL and resolve_repo from acf.repo. One small mismatch: SKILL.md:99 still reads `ARCH_REL` relative to the working directory, while :95 would use `repo / MANDATES_REL`. Both still come from acf.repo, so this is not a breach.

#### C36 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:137-143; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:241`
- reasoning: The rule is that runtime messages and skill prose name no host repository, path or section. The §4.2-§4.3 message strings use only generic words: 'host detector', 'active mandate', the mandate id and rel_path. The §4.7 prose describes call sites, the opt-in and the HostHit contract without naming an origin host. The only hm: reference, `metadata_facade_guard.py:66`, sits in spec rationale, not in runtime or skill text.

#### C37 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:155-156; plugins/arch-compliance/python/acf/cli_check_diff.py:112-113; plugins/arch-compliance/hooks/posttooluse_gate.py:229-236`
- reasoning: The rule is that every export has a live call site in the package, a hook or a skill. Each §6.2 export has a package or hook caller. The active() calls replace the filters at cli_check_diff.py:112-113 and posttooluse_gate.py:229-236, and TIER1_CALL_SITES, is_active and runs_at are used inside registry and enforcement. One inaccuracy: §6.2 says 'both gates' call load_host_detector, but §4.5's import list has the gates calling only scan_host_ast_file and scan_host_guards. load_host_detector's live caller is those runners, so the rule is still met.

#### C38 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:161-165; plugins/arch-compliance/tests/test_enforcement.py:54; plugins/arch-compliance/python/acf/adr/citations.py:51`
- reasoning: The rule is that a quantified claim about the tree needs a re-runnable recipe behind it. The spec's population claims have recipes: the KNOWN_DETECTORS extension, the call_sites readers, the review package, the load_mandates, apply_registry and active-filter callers, and the partial-row census. I spot-checked the apply_registry list, and test_enforcement.py's ten call sites match the Appendix. 'One classification changes' (§4.1) follows directly from comparing the old regex at citations.py:51 with the new one.

#### C39 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:173-174; plugins/arch-compliance/python/acf/cli_check_diff.py:152`
- reasoning: The rule requires every runtime subprocess text call to declare `encoding="utf-8"` and every file read to declare its encoding. Both new read_text calls declare utf-8. The rule says nothing about `errors=`, so `errors="replace"` does not conflict with it. The design adds no subprocess.

#### C40 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:186-187; pyproject.toml:3; plugins/arch-compliance/.claude-plugin/plugin.json:3`
- reasoning: The rule is that a change to skill prose bumps the version in plugin.json and pyproject.toml. Both read 0.2.2 today. §4.7 changes acf-mandate and acf-setup prose and bumps both files to 0.2.3. No other file carries 0.2.2 outside docs/.

#### C41 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:198-200; plugins/arch-compliance/python/acf/adr/contract.py:66; plugins/arch-compliance/python/acf/judge.py:218`
- reasoning: The rule is one canonical implementation per shared operation. The two token-identical line-lookup closures collapse into make_line_lookup. The three Tier-1 activity filters, plus the one in apply_registry, collapse into runs_at and active(). Citations' absolute and escape helpers move to acf.engine. PosixStr already delegates to engine.contains_backslash (contract.py:66). The judge's separate status read (judge.py:218) is explicitly scoped out as Tier-2 in Decision 2; it is a different decision, about whether a provider is required, not a second copy of this one.

#### C42 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:213-214; plugins/arch-compliance/python/acf/adr/citations.py:49-51; plugins/arch-compliance/python/acf/adr/citations.py:74-76`
- reasoning: The rule allows removing non-contractual patterns in code paths you are changing and forbids expanding scope to unrelated modules. Citations' helpers are not unrelated. Once acf.engine gains looks_absolute and resolve_under_root, citations.py:49-51 and :74-76 become duplicates, and ## Single point of definition then requires that they be consumed rather than copied. The shared dispatcher is declared a non-goal. The drive-relative reclassification is disclosed (§4.1) and tested (§4.6).

#### C43 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:147-148; plugins/arch-compliance/python/acf/adr/ledger.py:75-76`
- reasoning: The rule is that LedgerRow and LedgerAmendment fields change only through a spec and a gate run. The §3 in-scope table and §4.6 touch no ledger.py model. The only ledger mention in the design is the unrelated `surface_call_sites` grep hit in §1.

#### C44 — UNPROVEN
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:50; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:123; plugins/arch-compliance/hooks/posttooluse_gate.py:216-223`
- reasoning: The design does supply the 'Extension points for project-specific detectors' that :123 and :125 call for. Principles 1, 2, 3 and 5 are met: errors are typed, Finding stays the one finding schema (HostHit is converted into it), and paths are POSIX. Principle 4 says detectors and call sites 'must agree or tests fail'. The design checks only that a row's call_sites intersect TIER1_CALL_SITES, not that the named detector actually runs at the declared site. A fail_loud_ratchet row declaring only `hook` loads cleanly, yet the hook has no ratchet scanner (posttooluse_gate.py:216-223), and nothing fails. Full compliance with principle 4 is therefore not established.

#### C45 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:49-52; config/architecture/ARCHITECTURE.md:29-30`
- reasoning: apply_registry drops a finding only when token_exempted matches the looked-up line (enforcement.py:49-52). So an empty line from a missing file, an out-of-root file or a backslash path leaves the finding in place: that fails closed and hides nothing. An OSError from read_text propagates, and neither gate's except tuple catches it, so it surfaces as a crash. With `errors="replace"`, only the undecodable bytes are replaced; the ASCII exemption token stays visible. Nothing is swallowed.

### Unanchored findings

- **important**: Some active ast/guard rows pass load_mandates with known_detectors and are then run by neither Tier-1 gate. Example: a fail_loud_ratchet row whose call_sites name only hook or posttooluse. The ratchet runs only in acf-check-diff, which §4.5 now gates on DIFF_CALL_SITES, and the hook has no ratchet scanner. Also: ast/guard rows naming an LLM prompt id, which KNOWN_DETECTORS includes. So the design's Fail-loud premise (claim C30) is false.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:168`
- **important**: §4.3 wraps only the call fn(...) in its `except Exception`. A host callable written as a generator, the natural form for `Iterable[HostHit]`, raises when _to_findings iterates it. So its exceptions, including HostHit ValidationErrors, escape as raw tracebacks instead of the DetectorPackError §6.1 promises. The design must say the result is materialised inside the wrapped region.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:247`
- **advisory**: §6.1 says 'Host callable raises (any exception) → DetectorPackError', but `except Exception` does not catch SystemExit. A host callable or module that calls sys.exit(0) would end acf-check-diff with exit 0 and pass CI silently.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:384`
- **advisory**: The §6.1 row 'Active host row, no repo_root given → load_mandates' omits the 'with known_detectors' condition that the §4.2 code imposes. Callers that pass no known_detectors (inject_constraints, cli_check_llm, the architecture-review snippet) are never refused.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:380`

### Looked for but did not find

- ## High-frequency misses (ARCHITECTURE.md:217-228), checked first: no completeness claim without a recipe was found; no default re-enters for a declared value (repo_root and call_sites have no defaults); no host name appears in the new runtime messages or skill prose; no exception class or stdlib mixin is added; no subprocess is added; the hook and the skill snippet consume load_mandates, KNOWN_DETECTORS and the acf.repo constants rather than re-implementing them.
- ## Build artifacts: the design only reroutes the existing no_build_artifacts guard through registry.active and adds no generated tree. Not otherwise touched.
- ## Fail-loud ratchet: this repository's row is unenforced with call_sites [ci], so routing is unchanged here. The section's own rule (baseline file) is not touched; the routing hole for a [hook]-only ratchet row is reported as an unanchored finding rather than as an unstated mandate.
- ## Façade sinks / ## FSM transitions: both rows declare [ci, hook] and are only rerouted through registry.active. Their rules are not changed.
- ## Soft fail-loud smells / ## React boundaries: the Tier-2 judge and cli_check_llm are unchanged (Decision 2 scope, judge.py:213-218). Not touched.
- ## Post-merge: host operational declarations; the design changes none.
- ## One owner for host paths, ## Declared text decoding, ## Release discipline, ## Live consumers, ## No completeness claims, ## Single point of definition, ## Scoped refactor, ## Frozen ledger format, ## Prose names no host, ## One base exception, ## Fail loud, ## No shims, ## POSIX paths: all named in the spec's Governing mandates line and adjudicated above.
- unstated_mandates is empty because the spec's header names every doctrine section this design touches.

## sweeper

### Claim verdicts

#### C46 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:98; plugins/arch-compliance/hooks/posttooluse_gate.py:231; plugins/arch-compliance/hooks/posttooluse_gate.py:235; plugins/arch-compliance/hooks/posttooluse_gate.py:285; plugins/arch-compliance/python/acf/enforcement.py:47; plugins/arch-compliance/python/acf/registry.py:58`
- reasoning: I searched by behaviour for status filters (unenforced, .status, is_active) across python/ and hooks/. Tier-1 has exactly five active-row filters: cli_check_diff.py:98 (inside _active_mandates, called at :112, :113, :158, :168), posttooluse_gate.py:231, :235 and :285, and enforcement.py:47. All five become registry.active / runs_at, and load_mandates (registry.py:58) moves onto Mandate.is_active. Two status reads remain and neither is Tier-1: judge.py:218 (Tier-2 provider requirement) and inject_constraints.py:158 (display only). python_pack and typescript_bridge run without a registry and leave filtering to apply_registry. The Tier-1 scope holds. The broader §6 wording 'Row activity: Mandate.runs_at' does not hold outside Tier-1 (see unanchored finding).

#### C47 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/citations.py:51; plugins/arch-compliance/python/acf/adr/citations.py:76; plugins/arch-compliance/python/acf/adr/contract.py:95; plugins/arch-compliance/python/acf/adr/contract.py:129; plugins/arch-compliance/hooks/posttooluse_gate.py:204; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:123`
- reasoning: The claim holds as written. citations' _looks_absolute (:49-51) and _escapes_repo (:74-76) are the only regex absolute test and resolve+is_relative_to escape test in the package, and the engine helpers subsume them; the one difference is drive-relative strings, which the spec declares. PosixStr (contract.py:129 via _reject_backslash :60) and _WIN_DRIVE_RE (:95) detect backslashes or drives inside ADR text, so ADJACENT is right. posttooluse_gate.py:204 and fail_loud_ratchet.py:123 are Path.is_absolute calls that resolve inputs for I/O. Two caveats, found by searching for the behaviour (relative_to plus ValueError, is_relative_to) rather than the names: (1) under-root membership tests also live at posttooluse_gate.py:242-245, which the design keeps for host dispatch, and at fail_loud_ratchet.py:59-62; (2) the 'I/O is a different responsibility' line is blurred by the design itself, because make_line_lookup and load_host_detector do I/O through resolve_under_root. After the change the under-root test has three owners (filed as advisory).

#### C48 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:84-91; plugins/arch-compliance/python/acf/finding.py:11-19`
- reasoning: The bridge decodes JSON from its Node subprocess. It takes mandate_id and severity from the detector item (:85-86) and normalizes the path with posix_path (:87). The host runner instead takes mandate_id and severity from the row and gets typed, validated HostHit objects. Finding (finding.py:11-19) carries no validation, so neither path is duplicating a shared constructor. The two do share one small duty: refusing a malformed container or item with DetectorPackError (bridge :75-81 against _to_findings). That is too thin to need an abstraction, so ADJACENT stands.

#### C49 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/judge.py:241-250; plugins/arch-compliance/python/acf/finding.py:14-15`
- reasoning: I opened _to_finding. It demotes BLOCK to WARN on a WARN verdict or sub-high confidence (:241-245) and fills path='<diff>' and line=0 when the judge omits them (:249-250). Finding.path and Finding.line are unvalidated str and int (finding.py:14-15), so the model carries no shared invariant to put in a common constructor. Host findings need a relative path and line >= 1 and take severity straight from the row. The invariants differ, so ADJACENT is justified.

#### C50 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:25-26; plugins/arch-compliance/hooks/inject_constraints.py:28-29; tests/test_check_installed_skills.py:15-18`
- reasoning: I grepped for importlib, import_module, spec_from_file_location, exec_module, runpy, exec(, __import__ and sys.path across python/, hooks/, skills, scripts/ and tests. The only dynamic file loader is test-only (tests/test_check_installed_skills.py:15-18, loading a fixed script). Registry-supplied paths are read as data, never executed: the ratchet baseline JSON (fail_loud_ratchet.py:122-125). The sys.path insertions are at posttooluse_gate.py:25-26 and inject_constraints.py:28-29, two copies. 'ADJACENT' understates how they interact, though: the loader puts the host root at sys.path[0], ahead of the plugin python/ directory that the hook inserted (filed as advisory).

#### C51 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80; plugins/arch-compliance/hooks/posttooluse_gate.py:119-123; plugins/arch-compliance/python/acf/enforcement.py:23`
- reasoning: I grepped for LineLookup, line_lookup and _lookup( across the tracked tree, docs/reviews excluded. The only runtime implementations are the two token-identical closures. enforcement.py:23 defines the type and :49 is its only consumer. cli_check_llm and the judge never call apply_registry, and no skill snippet builds a lookup. test_enforcement.py uses local stubs (_no_lines and others), which are test doubles, not a second definition.

#### C52 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:95; plugins/arch-compliance/tests/test_profile_drift.py:24; tests/test_self_host.py:40`
- reasoning: The acf-mandate snippet (:95), the drift test (:24) and test_self_host (:23) all consume load_mandates with KNOWN_DETECTORS. architecture-review/SKILL.md:62 and cli_check_llm.py:54 call load_mandates without known_detectors. None re-checks detector ids itself. The nearest second check is tests/test_self_host.py:40, which requires each manual row's detector to name an existing file under ROOT. That shares the 'detector field names an existing file under the root' duty with the new host-reference existence check (PARTIAL_OVERLAP, see relationships). It only looks at detection == manual rows, so it neither rejects nor mishandles ast/guard host references.

#### C53 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:242-246; plugins/arch-compliance/hooks/posttooluse_gate.py:204`
- reasoning: _collect_paths resolves each edited path (:204) and repo comes from resolve_repo(...).resolve(), so abs_path.relative_to(repo) at :243 is a valid in-repo test. The ValueError branch (:244-245) falls back to the absolute POSIX string. Host dispatch can reuse that outcome, provided the implementation records which branch fired: rel_paths at :246 currently mixes both kinds of string.

#### C54 — SURVIVED
- evidence: `config/architecture/mandates.yml:70; config/architecture/mandates.yml:154; plugins/arch-compliance/profiles/python-service/mandates.yml:18; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:104; plugins/arch-compliance/skills/acf-mandate/SKILL.md:43`
- reasoning: I grepped call_sites values across yml, md and py (docs/reviews excluded). Shipped registries use only ci, hook and audit: config/architecture/mandates.yml, both profiles, and the fixture mandates_valid.yml. Docs add precommit and posttooluse (ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:104), and acf-mandate SKILL.md:43 lists ci, hook, audit. No 'pre-commit' (hyphenated) or 'review' value survives in shipped files. Every active ast/guard row includes ci. audit-only rows are all detection: manual (mandates.yml:148-212), and no Tier-1 gate reads them. llm rows with [ci, audit] go to Tier-2, which ignores call_sites.

#### C55 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_enforcement.py:54; plugins/arch-compliance/tests/test_hooks.py:217; plugins/arch-compliance/tests/test_registry.py:25; plugins/arch-compliance/tests/test_acf_mandate_skill.py:23`
- reasoning: I searched by behaviour, one changed surface at a time. apply_registry( has ten calls, all in test_enforcement.py (:54 through :130). No test references _looks_absolute or _escapes_repo. Of the tests that load with known_detectors, test_registry:25 uses [ci], profiles (test_profile_drift, test_acf_mandate_skill) give every active ast/guard row a ci site, and test_self_host's repository registry does too. The only hook test that depends on a [ci]-only row is test_hooks.py:199-218. One test the design touches without listing it: test_acf_mandate_skill.py extracts the Validate snippet by regex (:23) and runs it. §4.7 rewrites that snippet, so it must keep the ```bash python -c "..."``` shape. It does not break as long as the shape is kept.

#### C56 — REFUTED
- evidence: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:373-376; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:389`
- reasoning: The §4.7 site list misses an Approved shipped design doc that describes which files Tier-1 scans and what the hook reports. PLUGIN_SELF_HOSTING_AND_DOCTRINE.md §5.4 says PostToolUse checks the build-artifact guard and 'scans each edited .py, .ts or .tsx file whole' (:373-376). Its census (:389-393) has this repository's hook reporting no-shims.hasattr WARN rows. Under Decision 2 that row is [ci]-only and no longer reported, and host guards see every edited path. §4.7 does not update this doc, and §5.1 ties it only to test_self_host.

### Unanchored findings

- **important**: §4.6 marks plugins/arch-compliance/tests/test_engine_paths.py as '(new)', but the file already exists and is tracked (created by PLAN_PORT_ADR_PACKAGE) with contains_backslash/posix_path tests; a plan that creates it as new would overwrite existing coverage, so the new cases must be added to it.
  - evidence: `plugins/arch-compliance/tests/test_engine_paths.py:6`
- **advisory**: An Approved doc's statement of the PostToolUse contract (scans only edited .py/.ts/.tsx; reports this repo's no-shims.hasattr WARN rows) is contradicted by Decision 2 and the host-guard dispatch, yet the spec neither names it in §5.1 nor updates it in §4.7.
  - evidence: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:389`
- **advisory**: The under-root membership test keeps three owners after the change: engine.resolve_under_root, the hook's abs_path.relative_to(repo) (which the design reuses to decide host-dispatch eligibility while make_line_lookup in the same run uses resolve_under_root), and the ratchet's relative_to/ValueError skip. So 'Path shape: acf.engine' is not a single point of definition.
  - evidence: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:60`
- **advisory**: load_host_detector puts the host root at sys.path[0], ahead of the plugin python/ directory the hook inserted at start-up. A host with a top-level acf module would then shadow later lazy acf imports. The root-eviction step ('remove every sys.modules entry whose __file__ resolves under the old root') would also evict the plugin's own acf.* modules when the old root is this repository, whose tree contains plugins/arch-compliance/python/acf. So the two insertions interact rather than being ADJACENT.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:26`
- **advisory**: Parse-Python-or-skip-on-SyntaxError is implemented in python_pack, facade_sinks, fsm_guard and fail_loud_ratchet; scan_host_ast_file adds a fifth copy instead of a shared engine helper that all of them consume.
  - evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:35`
- **advisory**: Row activity keeps a second, divergent definition in Tier-2: cli_check_llm passes registry.mandates and run_judge reviews every llm row including unenforced ones (status read only for the provider requirement). So §6's 'Row activity: Mandate.runs_at' holds only within the Decision-2 Tier-1 scope, and the spec should say so.
  - evidence: `plugins/arch-compliance/python/acf/judge.py:214`
- **advisory**: test_self_host's manual-row check ((ROOT / m.detector).is_file()) and load_mandates' new host-reference existence check (resolve_under_root + is_file) share the responsibility 'detector field names an existing file under the repo root', and the test's version has no escape check.
  - evidence: `tests/test_self_host.py:40`

### Looked for but did not find

- Other Tier-1 active-row filters: grep 'unenforced|\.status\b|is_active' in plugins/**/*.py → only cli_check_diff.py:98, posttooluse_gate.py:231,235,285, enforcement.py:47, registry.py:58, judge.py:218 (Tier-2), inject_constraints.py:158 (display)
- Any gate or skill already reading call_sites: grep 'call_sites|call site' in *.py and plugins/**/*.md → only registry.py:21 field, adr surface_call_sites, prose in acf-mandate SKILL.md:43,59,79
- Call-site vocabulary values beyond ci/hook/audit/precommit/posttooluse: grep 'call_sites: \[' in yml/md → ci, hook, audit only in shipped registries
- Existing dynamic code loaders: grep 'importlib|import_module|spec_from_file_location|exec_module|runpy|exec\(|__import__' in python/, hooks/, skills, scripts, tests → test-only loader in tests/test_check_installed_skills.py
- A third LineLookup implementation: grep 'LineLookup|line_lookup|_lookup\(' → only the two closures and test stubs
- Second exemption-token interpreter: grep 'exemption|-ok' in python/acf → only enforcement.token_exempted
- Other absolute-path / under-root tests: grep 'is_absolute|is_relative_to|relative_to\(|\[A-Za-z\]:' → posttooluse_gate.py:204,243, fail_loud_ratchet.py:60,123, citations.py:51,76, contract.py:95
- Second detector-id validator in skills/tests: grep 'KNOWN_DETECTORS|nknown detector|load_mandates\(' → all consume load_mandates; test_self_host.py:40 checks manual rows only
- Tests depending on removed or changed surfaces: grep '_scan_paths|_scan_changed|_active_mandates|_looks_absolute|_escapes_repo|apply_registry\(' in tests → only test_enforcement apply_registry calls
- Shipped prose on file scope / built-in detectors / .acf/enabled: grep '\.tsx|built-in|registered detector|\.acf/enabled' in docs/design, README, plugins/**/*.md, hooks.json → PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:373-376,389 missing from §4.7

### Relationships

- SUBSUMED: `acf.engine.looks_absolute / resolve_under_root` — responsibility `classify a path string as absolute / escaping the repo root` — existing `plugins/arch-compliance/python/acf/adr/citations.py:49-51`
  - resolution: As designed: citations' _looks_absolute and _escapes_repo are deleted and their call sites consume acf.engine.
- PARTIAL_OVERLAP: `acf.engine.resolve_under_root` — responsibility `decide whether a path lies under the repo root` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:242-245`
  - resolution: R = repo-membership test. Route the hook's relative_to/ValueError test (used for host-dispatch eligibility) and fail_loud_ratchet.py:59-62 through resolve_under_root, or justify in writing why the resolved-Path relative_to stays a separate owner.
- PARTIAL_OVERLAP: `acf.engine.resolve_under_root` — responsibility `decide whether a path lies under the repo root` — existing `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:59-62`
  - resolution: Same R as above. The ratchet's walk-filter becomes a resolve_under_root consumer, or it is listed as an out-of-scope owner under ## Scoped refactor.
- ADJACENT: `acf.engine.validate_posix_rel_path` — responsibility `refuse a non-POSIX path string` — existing `plugins/arch-compliance/python/acf/adr/contract.py:129`
  - resolution: None. Both consume acf.engine.contains_backslash.
  - non-merge: PosixStr refuses only backslashes in persisted ADR fields; validate_posix_rel_path also refuses absolute paths, trailing '/' and dot segments. acf.adr is unreachable from hooks (test_adr_import_graph.py:70-76).
- SUBSUMED: `Mandate.runs_at / MandateRegistry.active` — responsibility `decide whether a row is live at a gate` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99`
  - resolution: As designed: _active_mandates, the three hook filters and the enforcement.py:47 filter call runs_at/active.
- ADJACENT: `Mandate.runs_at / MandateRegistry.active` — responsibility `decide whether a row is live at a gate` — existing `plugins/arch-compliance/python/acf/judge.py:214-218`
  - resolution: None within Decision 2's scope. §6's 'Row activity' line should name the Tier-2 exclusion.
  - non-merge: The Tier-2 judge selects llm rows by detection and reads status only to require a provider (spec Decision 2 scope).
- PARTIAL_OVERLAP: `load_mandates host-reference existence check` — responsibility `verify a detector field names an existing file under the repo root` — existing `tests/test_self_host.py:40`
  - resolution: R = detector-file existence under root. Expose one registry helper (resolve_under_root + is_file) used by load_mandates' host branch and by test_self_host's manual-row check.
- ADJACENT: `acf.detectors.host._to_findings` — responsibility `convert external detector output into Finding` — existing `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:75-95`
  - resolution: None
  - non-merge: JSON from a plugin subprocess with detector-supplied mandate_id and severity, versus typed HostHit objects with row-supplied mandate_id and severity. The input formats and the source of truth differ.
- ADJACENT: `acf.detectors.host._to_findings` — responsibility `convert external detector output into Finding` — existing `plugins/arch-compliance/python/acf/judge.py:238-255`
  - resolution: None
  - non-merge: The judge demotes severity by confidence and admits '<diff>' with line 0; host findings take severity from the row and need a relative path and line >= 1.
- IDENTICAL: `make_line_lookup` — responsibility `resolve a finding's source line for exemption checks` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:119-123`
  - resolution: As designed: both closures (this one and cli_check_diff.py:76-80) are deleted in favour of enforcement.make_line_lookup.
- PARTIAL_OVERLAP: `load_host_detector sys.path insertion` — responsibility `control import resolution order via sys.path[0]` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:25-26`
  - resolution: R = owning sys.path order in the hook process. State the precedence between the plugin python/ root and the host root (for example, append the host root, or refuse a host root that would shadow 'acf'). Restrict eviction to modules registered by the loader, not every module under the old root.
- PARTIAL_OVERLAP: `scan_host_ast_file shared ast.parse` — responsibility `parse Python source, skipping on SyntaxError` — existing `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37`
  - resolution: R = parse-or-skip. Add an engine-level parse helper consumed by python_pack, facade_sinks, fsm_guard, fail_loud_ratchet and the host runner, or record it as deferred under ## Scoped refactor.

### Two-owner counts

- under-root membership test of a path (resolve_under_root, posttooluse_gate.py:242-245, fail_loud_ratchet.py:59-62): 3
- absolute-path test (looks_absolute, posttooluse_gate.py:204 Path.is_absolute, fail_loud_ratchet.py:123 Path.is_absolute): 3
- decide whether a row is live at a gate (Mandate.runs_at for Tier-1; judge.py:214-218 for Tier-2): 2
- verify a detector field names an existing file under the root (load_mandates host branch; tests/test_self_host.py:40): 2
- sys.path insertion for import resolution (posttooluse_gate.py:25-26, inject_constraints.py:28-29, load_host_detector): 3
- parse Python source with SyntaxError skip (python_pack, facade_sinks, fsm_guard, fail_loud_ratchet, scan_host_ast_file): 5
- convert external detector output into Finding (typescript_bridge, judge._to_finding, host._to_findings): 3
- refuse malformed detector-output container with DetectorPackError (typescript_bridge.py:75-81, host._to_findings): 2

### Document conflicts

- `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:374` (contradicts): scans each edited `.py`, `.ts` or `.tsx` file whole
- `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:389` (contradicts): `plugins/arch-compliance/tests/test_adr_exceptions.py:22` `no-shims.hasattr` | WARN | Context only (hook census; :393 'the same command reports the five WARN rows')
- `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:184` (contradicts): Unknown detector id referenced by an enforced `ast` or `guard` row → drift/registry validation fail.
- `plugins/arch-compliance/skills/acf-setup/SKILL.md:150` (contradicts): Suggest adding `.acf/` to git if the team wants hooks enabled for everyone
- `docs/design/ADR_GATE_HOST_CONTRACT.md:302` (contradicts): `acf:plugins/arch-compliance/python/acf/adr/citations.py:49` (`_looks_absolute`) and `:74` (`_escapes_repo`) already own.

## hardening

### Claim verdicts

#### C57 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:69-74; plugins/arch-compliance/hooks/posttooluse_gate.py:113-117; plugins/arch-compliance/hooks/inject_constraints.py:104; plugins/arch-compliance/python/acf/cli_check_llm.py:54`
- reasoning: In cli_check_diff.py the try at :69 wraps both load_mandates (:70) and _scan_changed (:71), and its except tuple at :72 already lists UnknownDetectorError. So an UnknownDetectorError raised at dispatch inside _scan_changed is caught there and returns 1. The hook's scan try at :113-117 catches only DetectorPackError today, and the design widens it to (DetectorPackError, UnknownDetectorError), so both gates catch it. inject_constraints.py:104 and cli_check_llm.py:54 call load_mandates without known_detectors. Importing at load would therefore run host code in both, which supports the deferral argument. A missing file is still caught at load by the existence check (spec registry body). One caveat, not a refutation: a broken host ast module stays undetected until a file in its language changes, because import happens only on dispatch.

#### C58 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:25; plugins/arch-compliance/python/acf/cli_check_diff.py:168-182; plugins/arch-compliance/hooks/posttooluse_gate.py:213-295; plugins/arch-compliance/python/acf/detectors/python_pack.py:66; plugins/arch-compliance/python/acf/enforcement.py:46`
- reasoning: The two checks are not sufficient. (1) The hook never runs fail_loud_ratchet: _scan_paths (posttooluse_gate.py:213-295) has no ratchet call, and only cli_check_diff.py:168-182 runs it. An active `guard` row with detector fail_loud_ratchet and call_sites [hook] passes the Tier-1 check, since hook is in TIER1, and passes the known_detectors check. The diff gate then drops it because it is not in DIFF_CALL_SITES, and the hook never dispatches it, so no gate runs it. (2) KNOWN_DETECTORS (cli_check_diff.py:25) includes LLM_PROMPT_IDS. An `ast` row naming llm_fail_loud with [ci, hook] loads, but no Tier-1 scanner emits for it. (3) Built-in scanners hard-code mandate_id (python_pack.py:66 emits 'fail-loud.bare-except'), and apply_registry matches by mandate_id (enforcement.py:46). An active row with any other id and detector fail_loud_bare_except therefore loads and never produces a kept finding. The load check is per row and does not ask whether a gate at that row's call site actually dispatches that detector.

#### C59 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:63; plugins/arch-compliance/hooks/posttooluse_gate.py:65; plugins/arch-compliance/tests/test_diff_cli.py:48; plugins/arch-compliance/tests/test_diff_cli.py:129; C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/metadata_facade_guard.py:66`
- reasoning: The import at hm metadata_facade_guard.py:66 (`from scripts.ci.arch_compliance.facade_sinks import ...`) justifies putting the root on sys.path. It does not justify eviction, which needs a second root, and one root is enough for that import. Every production caller resolves exactly one repo per process (cli_check_diff.py:63, posttooluse_gate.py:65; the hook is a fresh process per edit). The only producer of the multi-root state is in-process tests, such as test_diff_cli.py:48 calling main() once per tmp repo. The spec's whole justification is "the eviction keeps in-process test runs over several tmp_path roots isolated". That puts a silent repair in production code for a state only the test harness produces. A rung-3 alternative was not considered: the loader raises on a second distinct root, and multi-root tests run the gate in a subprocess, as test_diff_cli.py:129 already does, or reset the loader through a test fixture.

#### C60 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37; plugins/arch-compliance/python/acf/cli_check_diff.py:127`
- reasoning: scan_python_file parses on every call (python_pack.py:34-37) and is called once per file (cli_check_diff.py:127). Sharing one parse across N host ast callables on the same file is a plain efficiency choice, and built-in scanners are left untouched. This is not a recovery mechanism. The SyntaxError→[] convention matches python_pack.py:36-37.

#### C61 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:46; plugins/arch-compliance/python/acf/finding.py:12-19`
- reasoning: apply_registry looks up the row with by_id.get(finding.mandate_id) (enforcement.py:46) and takes severity from that row (:52). If a host returned a full Finding (finding.py:12-19 has mandate_id, detector, detection), it could choose its own mandate_id and attach to any row. Returning HostHit (path, line, message) and building the Finding from the dispatching row makes a wrong-row finding impossible to construct, which is rung 1.

#### C62 — SURVIVED
- evidence: `.gitignore:8; .github/workflows/ci.yml:40; plugins/arch-compliance/hooks/posttooluse_gate.py:72-81`
- reasoning: .gitignore:8 ignores `.acf/`, so a CI checkout never has the marker. CI calls acf-check-diff explicitly at ci.yml:40, and the same workflow already runs repository code through pytest, so no new exposure is added there. The hook exits 0 before any third-party or host import when the marker is absent (posttooluse_gate.py:72-81). The residual case, a manual acf-check-diff run in an untrusted checkout, is accepted explicitly in writing.

#### C63 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:27-52; plugins/arch-compliance/python/acf/cli_check_diff.py:127; plugins/arch-compliance/hooks/posttooluse_gate.py:254; plugins/arch-compliance/hooks/posttooluse_gate.py:279-282`
- reasoning: scan_python_file emits findings for all three built-in AST detectors with hard-coded mandate_ids and never consults the registry (python_pack.py:27-52). Both gates call it for every .py file (cli_check_diff.py:127, posttooluse_gate.py:254), and scan_typescript_file is likewise registry-blind (:279-282). registry.active(call_sites) selection therefore cannot stop these findings. Without the apply_registry runs_at filter, a [ci]-only row such as no-shims.hasattr would still be reported by the hook. The filter at that single sink is not redundant.

#### C64 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:9-27; plugins/arch-compliance/python/acf/registry.py:29-45`
- reasoning: Mandate (registry.py:14-27) is a plain BaseModel with no model_config, so pydantic defaults apply and nothing forbids properties or methods. It declares id, severity, detection, detector, languages (Literal at :11 including 'none'), call_sites: list[str], status, and params: dict[str, Any] | None. MandateRegistry (:29-45) already carries a @property by_id, which shows that properties and methods sit alongside its fields.

#### C65 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/finding.py:6-19; plugins/arch-compliance/python/acf/registry.py:17`
- reasoning: Finding's required fields are mandate_id, severity, path, line, message and detector. confidence defaults to None and detection defaults to 'ast', and the design passes detection explicitly. Severity is a str Enum with values BLOCK and WARN, and Mandate.severity is Literal['BLOCK','WARN'] (registry.py:17), so Severity(mandate.severity) constructs.

#### C66 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:23; plugins/arch-compliance/python/acf/enforcement.py:43-52`
- reasoning: by_id lookup is at :43-46, and the status check `mandate.status == "unenforced"` is at :47, where runs_at can replace it. Exemption handling is at :49-51 and the severity rewrite at :52. LineLookup is Callable[[str, int], str] (:23), which make_line_lookup's _lookup satisfies.

#### C67 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:69-82; plugins/arch-compliance/python/acf/cli_check_diff.py:110-156; plugins/arch-compliance/python/acf/cli_check_diff.py:168-184`
- reasoning: load is at :70 inside a try that also wraps _scan_changed (:71), and the except at :72 is (GitError, AcfInputError, UnknownDetectorError, DetectorPackError). The lookup and apply_registry are at :76-82. In the .py branch after scan_fsm_writes (:140-150), repo, text (:125), posix (:122), lines (:121) and registry are all in scope. The .ts branch at :152 reads the file inline, and that read can be bound to text. `changed` (:110) is in scope after the ratchet loop (:168-182).

#### C68 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:91-125; plugins/arch-compliance/hooks/posttooluse_gate.py:229-254; plugins/arch-compliance/hooks/posttooluse_gate.py:284-294`
- reasoning: The anchors check out: deferred imports in a try/except ImportError at :91-104, load try at :106-110, scan try at :113-117, lookup and apply_registry at :119-125, inline filters at :229-236 and :284-286, and relative_to with the ValueError fallback at :242-245. The build-artifact loop is at :284-294. text (:251) and rel (:243/245) are bound before the .py/TS split at :253, so both branches have them. Caveat: KNOWN_DETECTORS exists only in acf.cli_check_diff (:25), so the new hook import pulls in acf.judge and httpx. httpx is a declared dependency and this does not reach acf.adr.

#### C69 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:72; plugins/arch-compliance/hooks/posttooluse_gate.py:113-117; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:247`
- reasoning: The spec wraps only the call `fn(text, path, added_lines, ...)` (spec :247, and :248 for guards). _to_findings (spec :243) refuses only shape errors. The host contract returns Iterable[HostHit], which invites a generator. A generator's body, including HostHit(...) construction, runs during iteration inside _to_findings, outside the wrapping try. An exception raised there therefore escapes unwrapped. That includes a pydantic ValidationError (a ValueError, not an AcfError) for a bad path or line, which spec §6.1 claims is 'raised inside the callable, wrapped'. Neither cli_check_diff.py:72 nor the hook's widened except catches it, so it ends as a traceback. In addition, `except Exception` does not catch SystemExit or KeyboardInterrupt, so a host callable that calls sys.exit also escapes. The claim that 'no host failure escapes as a traceback' does not hold as written.

#### C70 — SURVIVED
- evidence: `C:/Python313/Lib/importlib/_bootstrap_external.py:1384-1395; C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/__init__.py:1`
- reasoning: I traced the HM layout. scripts/ is a regular package (scripts/__init__.py exists), scripts/ci is a namespace portion (no __init__.py), and scripts/ci/arch_compliance is regular. Eviction by __file__ removes `scripts`, `scripts.ci.arch_compliance.*` and the hashed synthetic modules. It does not remove the namespace `scripts.ci`, whose __file__ is None, but _NamespacePath._recalculate (_bootstrap_external.py:1384-1395) recomputes when its parent path changes, so it re-points at the new root's scripts.__path__. The hashed name keys on root, so the same rel_path under two roots gets distinct names. Limits: the guarantee covers only modules and sys.path entries that the loader itself created. Host code that edits sys.path itself would defeat it, and `git grep sys.path.insert -- scripts/ci` in HM finds none. A pre-existing non-root module with a colliding top-level name is not evicted on first load, since _ACTIVE_ROOT is None then.

#### C71 — SURVIVED
- evidence: `C:/Python313/Lib/dataclasses.py:757`
- reasoning: dataclasses resolves string annotations with `ns = sys.modules.get(cls.__module__).__dict__` (dataclasses.py:757). If the module is not registered in sys.modules under its synthetic name before exec_module, that is None.__dict__ and raises AttributeError. spec_from_file_location(name, path) accepts any name, so registering before exec_module is the required hook and it exists.

#### C72 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/engine.py:6-8; plugins/arch-compliance/python/acf/adr/contract.py:20; plugins/arch-compliance/tests/test_adr_import_graph.py:54-76`
- reasoning: acf.engine imports only pathlib (:6-8) and imports nothing from acf, so registry→engine and host→{registry, finding, engine, exceptions} create no cycle. acf.adr already imports acf.engine (contract.py:20), so citations doing the same has precedent. test_adr_import_graph only forbids `scripts.*` imports from acf/adr (:54-67) and the literal 'acf.adr' in hook source (:70-76). None of the hook's new imports (registry, enforcement, detectors.host, cli_check_diff→judge) imports acf.adr.

#### C73 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:53-64; plugins/arch-compliance/python/acf/loader.py:71`
- reasoning: registry.py:53-55 calls load_model_file(path, Mandate, subject="mandates file", fmt="yaml", many=True), which returns a list of Mandate via model_validate per row (loader.py:71). :64 returns MandateRegistry(mandates=mandates, source_path=path.as_posix()). The §4.2 body keeps both calls and adds checks in between.

#### C74 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_repo_paths.py:47-48; plugins/arch-compliance/hooks/posttooluse_gate.py:11-12`
- reasoning: ALLOWED_DOC_LINES for hooks/posttooluse_gate.py (:47-48) allowlists exactly the stripped text of docstring line :11. The test fails only on a non-allowlisted line that spells config/architecture. Line :12 does not spell it today, so rewording :12 is safe as long as the new text does not spell config/architecture.

#### C75 — SURVIVED
- evidence: `config/architecture/mandates.yml:53-61; plugins/arch-compliance/python/acf/enforcement.py:26-34; plugins/arch-compliance/python/acf/detectors/python_pack.py:62-69`
- reasoning: mandates.yml:60 is `exemption_tokens: [fail-loud.bare-except-ok]` for row fail-loud.bare-except (:53, enforced, [ci, hook]). The detector reports node.lineno of the except handler (python_pack.py:62-69). apply_registry checks that same line with token_exempted, whose regex `(?:#|//)\s*<token>\s*:\s*(\S.*)$` (enforcement.py:31) accepts `# fail-loud.bare-except-ok: <reason>` when the reason is non-empty. The fail-loud.ratchet row is unenforced, so it does not count these handlers.

#### C76 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/engine.py:8; plugins/arch-compliance/python/acf/engine.py:17-24`
- reasoning: engine.py imports only `from pathlib import Path` (:8) and defines contains_backslash (:17-24). Adding `import re` keeps it stdlib-only.

### Unanchored findings

- **important**: The Tier-1 load check does not ensure a row actually runs. A [hook]-only fail_loud_ratchet guard row, an ast row naming an LLM prompt id, or a built-in row whose id differs from the scanner's hard-coded mandate_id all load and are executed by no gate, which reproduces Problem 1 ('declared but never run') for built-in ids.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:213-295`
- **important**: One-host-root eviction is a silent repair placed in production code for a state that only in-process tests produce, since every production caller is one root per process. Raising on a second root (rung 3), with multi-root tests run via subprocess or a fixture reset, would remove the mechanism.
  - evidence: `plugins/arch-compliance/tests/test_diff_cli.py:48`
- **important**: Wrapping covers only the host callable's invocation. Exceptions raised while iterating a generator return value, including HostHit ValidationError, and SystemExit from host code escape both gates' except tuples as tracebacks, contrary to spec §6.1.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:247`
- **advisory**: plugins/arch-compliance/tests/test_engine_paths.py is already tracked (it holds contains_backslash/posix_path tests), but spec §4.6 lists it as '(new)'. Creating it as written would clobber existing tests, so it should be extended instead.
  - evidence: `plugins/arch-compliance/tests/test_engine_paths.py:1`
- **advisory**: The host-ref syntax, Tier-1 and host-ast-languages checks are pure row-shape invariants. They are placed in load_mandates, and the latter two run only when known_detectors is given, rather than as a Mandate model_validator (rung 1). SubagentStart and acf-check-llm therefore accept registries that the gates reject, and the spec gives no reason.
  - evidence: `plugins/arch-compliance/python/acf/registry.py:14-27`
- **advisory**: acf-check-llm calls load_mandates outside any try, so the new every-load AcfInputError for a malformed host reference reaches it as a traceback. §3 accounts only for inject_constraints.py:105.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_llm.py:54`

### Looked for but did not find

- Production producer of the multi-root state: cli_check_diff.py:63 and posttooluse_gate.py:65 each resolve exactly one repo per process; none found
- sys.path mutation inside HM scripts/ci host modules that would defeat root eviction: git grep sys.path.insert/append -- scripts/ci prints nothing
- Mandate/MandateRegistry construction outside load_mandates in production code: only tests (test_enforcement.py:19, test_judge.py:41, test_template.py:73) construct them directly
- Producer of backslash Finding.path that make_line_lookup's contains_backslash guard handles: every built-in detector emits posix (build_artifacts.py:33, python_pack.py:69, typescript_bridge.py:87), and HostHit refuses backslashes; none found
- acf.adr reachable from the hook's new deferred imports (registry, enforcement, detectors.host, cli_check_diff→judge→template): none found
- An existing model_config on Mandate that would forbid adding a property or method: none (registry.py:14-27)
- An existing dynamic loader to reuse (importlib/spec_from_file_location in plugin python/hooks): none, consistent with spec §1

### Mechanism traces

- **parse_host_detector_ref syntax validation in load_mandates (every load)**
  - invalid state: an ast/guard row whose detector contains ':' and whose path part fails validate_posix_rel_path, or does not end in .py, or whose callable part is not str.isidentifier()
  - producer: `plugins/arch-compliance/python/acf/registry.py:53`
  - rung 3 (highest applicable 1); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:182`
- **Tier-1 call-site requirement for active ast/guard rows (load_mandates with known_detectors)**
  - invalid state: row with status != 'unenforced' and detection in {ast, guard} and set(call_sites) ∩ {ci, precommit, hook, posttooluse} == ∅
  - producer: `config/architecture/mandates.yml:70`
  - rung 3 (highest applicable 1); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:187`
- **Active host ast row languages check**
  - invalid state: active row with detection == 'ast' and ':' in detector and languages == 'none'
  - producer: `plugins/arch-compliance/python/acf/registry.py:53`
  - rung 3 (highest applicable 1); repairs=False
  - hardening rejected because: "because a `languages: none` row matches no file"
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:203`
- **Host detector file-existence check at load (and again in load_host_detector)**
  - invalid state: active host row where resolve_under_root(repo_root, rel_path) is None or not is_file()
  - producer: `plugins/arch-compliance/python/acf/registry.py:53`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:210`
- **Dispatch-time import/callable failure re-raised as UnknownDetectorError (sys.modules entry removed on exec_module failure)**
  - invalid state: host module raises during exec_module, or getattr(mod, attr) is not callable
  - producer: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/metadata_facade_guard.py:66`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: "importing at load would run host code in the SubagentStart hook and acf-check-llm" (Decision 3/5: load_mandates runs no host code for any caller)
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:241`
- **One host root per process: eviction of old root's sys.modules entries, sys.path entry and _MODULE_CACHE**
  - invalid state: _ACTIVE_ROOT is not None and load_host_detector is called with repo_root.resolve() != _ACTIVE_ROOT
  - producer: `plugins/arch-compliance/tests/test_diff_cli.py:48`
  - rung 5 (highest applicable 3); repairs=True
  - hardening rejected because: "Production callers are one process per gate run; the eviction keeps in-process test runs over several `tmp_path` roots isolated."
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:240`
- **HostHit frozen model (path validated by validate_posix_rel_path, line >= 1, non-empty message)**
  - invalid state: a host hit with a backslash/absolute/dotted path, line < 1, or empty message
  - producer: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/arch_compliance/driver.py:139`
  - rung 1 (highest applicable 1); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:224`
- **_to_findings shape refusal (None/str/bytes/non-iterable, non-HostHit item, ast hit on another path)**
  - invalid state: raw is None or isinstance(raw, (str, bytes)) or not iterable, or any item not HostHit, or (detection == 'ast' and hit.path != expected_path)
  - producer: `plugins/arch-compliance/python/acf/enforcement.py:46`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: "so a host cannot attach a finding to the wrong row and no field is overwritten"
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:243`
- **Wrapping any exception from a host callable as DetectorPackError**
  - invalid state: host callable raises any exception (AcfError included) during invocation
  - producer: `plugins/arch-compliance/hooks/posttooluse_gate.py:113-117`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:247`
- **apply_registry call_sites filter (runs_at) replacing the status check**
  - invalid state: a finding whose row has status == 'unenforced' or whose call_sites do not intersect the gate's call-site set
  - producer: `plugins/arch-compliance/python/acf/detectors/python_pack.py:27-52`
  - rung 2 (highest applicable 2); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:258`
- **make_line_lookup lazy read with errors="replace" and contains_backslash guard**
  - invalid state: a finding whose path is not in file_lines (a non-code file flagged by a guard), possibly with non-UTF-8 bytes or a backslash in its path
  - producer: `plugins/arch-compliance/python/acf/detectors/build_artifacts.py:33`
  - rung 5 (highest applicable 5); repairs=True
  - hardening rejected because: "an exemption token is ASCII, so a stray undecodable byte elsewhere on the line must neither crash `apply_registry` nor hide the token"
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:267`
- **Hook excludes out-of-repo edited paths from host dispatch**
  - invalid state: an edited path for which abs_path.relative_to(repo) raises ValueError
  - producer: `plugins/arch-compliance/hooks/posttooluse_gate.py:244-245`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:294`

## Claims

- **C1** [premise] [load-bearing]: Today load_mandates (registry.py:48-64) skips every row whose status is not 'enforced' (:58) and raises UnknownDetectorError (:60-63) only for an enforced ast/guard row whose detector is not in known_detectors.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:58`
- **C2** [root_cause] [load-bearing]: Root cause of the registry/gate disagreement: a status: partial row is live in both Tier-1 gates (enforcement.py:47 drops only 'unenforced'; the gates' row filters likewise), yet load_mandates never checks it, so a host can name a non-built-in detector in a partial ast/guard row today, load cleanly with known_detectors=KNOWN_DETECTORS, and have nothing ever execute it.
  - spec citation: `plugins/arch-compliance/python/acf/enforcement.py:47`
- **C3** [premise] [load-bearing]: KNOWN_DETECTORS (cli_check_diff.py:25) is the closed union ALL_PYTHON_DETECTOR_IDS | TS_DETECTOR_IDS | LLM_PROMPT_IDS and nothing in plugins/ or tests/ extends or mutates it (recipe: git grep -n "KNOWN_DETECTORS" -- plugins tests).
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
- **C10** [premise] [load-bearing]: Path-shape checks live only inside acf.adr: PosixStr (adr/contract.py:129, via _reject_backslash at :60) refuses only backslashes; _looks_absolute (adr/citations.py:49-51) and _escapes_repo (:74-76) classify citation strings; and hooks/posttooluse_gate.py may not reference acf.adr (test_adr_import_graph.py:70-76), so none of them can serve a hook-reachable caller.
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
- **C18** [premise] [load-bearing]: Deferral: the origin host's driver reports unparseable changed files (hm:scripts/ci/arch_compliance/driver.py:139-157) and its guards can depend on diff mode; scan_host_ast_file skips unparseable files like the built-in scanners and scan_guard receives no diff mode, and these gaps are left to the cutover spec. A host needing parse-failure reporting can declare it as a guard (scan_guard receives repo_root and every changed path, enough to re-parse).
  - spec citation: `hm:scripts/ci/arch_compliance/driver.py:139-157`
- **C19** [premise] [load-bearing]: Deferral: no shared Tier-1 dispatcher. _scan_changed and _scan_paths differ in diff scope (added lines vs whole file), path collection and file filter, so adding the same three host calls to each, rather than extracting a common dispatcher, is within ## Scoped refactor (ARCHITECTURE.md:211-215).
  - spec citation: `config/architecture/ARCHITECTURE.md:211-215`
- **C20** [premise]: scan_python_file returns [] on SyntaxError (python_pack.py:34-37), the convention scan_host_ast_file copies.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37`
- **C21** [premise] [load-bearing]: Appendix receipt: the load_mandates callers outside registry.py are exactly those the git grep recipe prints (inject_constraints.py:104, posttooluse_gate.py:107, cli_check_diff.py:70, cli_check_llm.py:54, acf-mandate SKILL.md:95 plus prose at :141, architecture-review SKILL.md:62, test_profile_drift.py:24, test_registry.py:10,17,30,47,57, tests/test_self_host.py:23); only cli_check_diff.py:70, SKILL.md:95, test_profile_drift.py:24, test_registry.py:30 and test_self_host.py:23 pass known_detectors, and the others reach only the syntax check. (Load-bearing: a caller passing known_detectors without repo_root raises AcfInputError on any active host row.)
  - spec citation: `None`
- **C22** [premise] [load-bearing]: Appendix census (executed): every active (status != unenforced) ast/guard row in config/architecture/mandates.yml, the plugin profiles (plugins/arch-compliance/profiles/*/mandates.yml) and tests/fixtures/mandates_valid.yml declares 'ci', and no partial ast/guard row exists; so the new Tier-1 call-site requirement and the extension of validation to partial rows reject no shipped registry. Also check inline YAML registries written by tests (test_diff_cli.py, test_hooks.py, test_registry.py, test_profile_drift.py, test_enforcement.py) for active ast/guard rows that lack a Tier-1 call site or name an unknown detector while passing known_detectors.
  - spec citation: `None`
- **C23** [premise]: KNOWN_DETECTORS has 13 ids. (Precision fact.)
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:25`
- **C24** [premise] [load-bearing]: Appendix receipt: apply_registry's callers are exactly posttooluse_gate.py:125, cli_check_diff.py:82 and test_enforcement.py at :54, 60, 66, 72, 84, 94, 104, 110, 125, 130 (recipe git grep -n "apply_registry(" -- '*.py'), so adding a required keyword call_sites touches only those.
  - spec citation: `None`
- **C25** [premise] [load-bearing]: Appendix receipt: the Tier-1 active-row filters are exactly cli_check_diff._active_mandates (:94-99; used at :112, :113, :158, :168), the hook's inline filters (posttooluse_gate.py:229-236 and :284-286, matched at :231, :235, :285) and apply_registry's status check (enforcement.py:47); the wider .status recipe adds only registry.py:58 (replaced), judge.py:218 (Tier-2) and a display-only read at inject_constraints.py:158.
  - spec citation: `None`
- **C26** [deletion] [load-bearing]: Deleting citations._looks_absolute (:49-51) and _escapes_repo (:74-76) is safe: their only references are the call sites at citations.py:161 and :163 (no test or other module imports them), resolve_citation (:129-185) keeps its order, and replacing them with acf.engine.looks_absolute and resolve_under_root changes exactly one classification: a drive-relative string such as "C:a/b.py" becomes external.
  - spec citation: `plugins/arch-compliance/python/acf/adr/citations.py:49-51`
- **C27** [deletion] [load-bearing]: Deleting the two _line_lookup closures (cli_check_diff.py:76-80, posttooluse_gate.py:119-123) in favour of make_line_lookup preserves their behaviour for every file already in file_lines and only adds a disk read (under the repo root, errors=replace) for files not in it.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80`
- **C28** [deletion] [load-bearing]: Deleting cli_check_diff._active_mandates and the hook's inline filters in favour of registry.active(call_sites, detector=...) changes no selection except by call_sites: for every shipped registry, the only built-in row that stops running at a gate is no-shims.hasattr leaving the PostToolUse hook (it declares [ci]).
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99`
- **C29** [mandate] [load-bearing]: ## Fail loud: every invalid state in spec §6.1 is refused by the named component with the named error, and the two `except Exception` handlers in acf.detectors.host (import failure; host callable failure) re-raise as typed errors and carry the fail-loud.bare-except-ok token with a reason, as ARCHITECTURE.md:29-30 requires.
  - spec citation: `config/architecture/ARCHITECTURE.md:24-41`
- **C30** [mandate] [load-bearing]: ## Fail loud: no path lets an active ast/guard row load (with known_detectors) yet never be executed by either Tier-1 gate: load_mandates requires a Tier-1 call site, a known built-in id or an existing host file, and languages in {python, typescript, both} for a host ast row.
  - spec citation: `config/architecture/ARCHITECTURE.md:24-41`
- **C31** [mandate] [load-bearing]: ## Declared, never defaulted: load_mandates requires an explicit repo_root for an active host detector row (AcfInputError otherwise, never derived), and apply_registry's new call_sites keyword has no default.
  - spec citation: `config/architecture/ARCHITECTURE.md:118-133`
- **C32** [mandate]: ## No shims: callable lookup is getattr(mod, attr, None) followed by callable() and a raise; no hasattr, and no host-detector failure has a silent fallback.
  - spec citation: `config/architecture/ARCHITECTURE.md:43-53`
- **C33** [mandate]: ## POSIX paths: HostHit.path is validated by validate_posix_rel_path (which refuses backslashes) and error messages use .as_posix().
  - spec citation: `config/architecture/ARCHITECTURE.md:55-64`
- **C34** [mandate]: ## One base exception: the design adds no exception class and uses AcfInputError, UnknownDetectorError and DetectorPackError (exceptions.py:5, :13, :29), all subclassing AcfError.
  - spec citation: `plugins/arch-compliance/python/acf/exceptions.py:5`
- **C35** [mandate]: ## One owner for host paths: acf/engine.py, acf/registry.py and the new acf/detectors/host.py spell no config/architecture path, and the acf-mandate skill snippet takes MANDATES_REL and resolve_repo from acf.repo.
  - spec citation: `config/architecture/ARCHITECTURE.md:105-116`
- **C36** [mandate]: ## Prose names no host: the runtime messages in §4.2-§4.3 and the prose changes in §4.7 name no origin host.
  - spec citation: `config/architecture/ARCHITECTURE.md:135-143`
- **C37** [mandate]: ## Live consumers: each export in §6.2 has the named runtime caller (e.g. HostHit is used by _to_findings and imported by host code; TIER1_CALL_SITES by load_mandates; Mandate.is_active by runs_at and load_mandates).
  - spec citation: `config/architecture/ARCHITECTURE.md:153-157`
- **C38** [mandate]: ## No completeness claims: every population claim in the spec carries a re-runnable recipe (§1, §3, Appendix) or is a per-item table, as ARCHITECTURE.md:159-169 requires.
  - spec citation: `config/architecture/ARCHITECTURE.md:159-169`
- **C39** [mandate]: ## Declared text decoding: the new read_text calls (cli_check_diff.py TypeScript branch, make_line_lookup) declare encoding="utf-8", errors="replace" in make_line_lookup is permitted by that rule, and no subprocess is added.
  - spec citation: `config/architecture/ARCHITECTURE.md:171-182`
- **C40** [mandate]: ## Release discipline: because shipped skill prose changes, the version is bumped 0.2.2 -> 0.2.3 in both files ARCHITECTURE.md:186-187 names (pyproject.toml:3, plugins/arch-compliance/.claude-plugin/plugin.json:3).
  - spec citation: `config/architecture/ARCHITECTURE.md:184-194`
- **C41** [mandate]: ## Single point of definition: path shape is defined once in acf.engine, row activity once in Mandate.runs_at, host loading and running once in acf.detectors.host, and line lookup once in make_line_lookup.
  - spec citation: `config/architecture/ARCHITECTURE.md:196-209`
- **C42** [mandate]: ## Scoped refactor: the consolidations (line lookup, active-row filters, citations' path helpers) touch only code paths this design changes; the shared dispatcher is a declared non-goal.
  - spec citation: `config/architecture/ARCHITECTURE.md:211-215`
- **C43** [mandate]: ## Frozen ledger format: the design changes no ledger model.
  - spec citation: `config/architecture/ARCHITECTURE.md:145-151`
- **C44** [mandate]: The design complies with the five portable governing principles at docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51 and fulfils that spec's call for project-specific detector extension points (:102, :123, :125).
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51`
- **C45** [mandate]: ## Fail loud: make_line_lookup returning [] for a missing or out-of-root file, and errors="replace" decoding, hide no failure: OSError from read_text propagates, and a missing file can only mean no exemption token exists.
  - spec citation: `config/architecture/ARCHITECTURE.md:24-41`
- **C46** [shape_fit] [load-bearing]: Mandate.runs_at and MandateRegistry.active become the single definition of 'this row runs at this gate' for the Tier-1 gates; after the change no other Tier-1 site (cli_check_diff, posttooluse_gate, enforcement, the host runners) keeps its own active-row filter.
  - spec citation: `None`
- **C47** [shape_fit] [load-bearing]: looks_absolute and resolve_under_root in acf.engine subsume citations' private helpers and are the only absolute-test and under-root test used by validate_posix_rel_path, load_mandates, load_host_detector, make_line_lookup and acf/adr/citations.py; PosixStr (adr/contract.py:129) and _WIN_DRIVE_RE (adr/contract.py:95) are ADJACENT (backslash/drive detection inside persisted ADR text), and the other path handling (posttooluse_gate.py:204, fail_loud_ratchet.py:123) resolves paths for I/O, a different responsibility.
  - spec citation: `plugins/arch-compliance/python/acf/adr/citations.py:74-76`
- **C48** [shape_fit] [load-bearing]: Building Finding from a validated HostHit in acf.detectors.host is ADJACENT to, not a partial duplicate of, the TypeScript bridge's JSON-to-Finding coercion (typescript_bridge.py:75-95), because the inputs share no format.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:75-95`
- **C49** [shape_fit] [load-bearing]: Building Finding from a HostHit is ADJACENT to the judge's _to_finding (judge.py:236-253): the judge demotes severity by confidence and admits path="<diff>" and line=0, while host findings take severity from the row and require a relative path and line >= 1, so no shared constructor is warranted.
  - spec citation: `plugins/arch-compliance/python/acf/judge.py:236-253`
- **C50** [shape_fit] [load-bearing]: acf/detectors/host.py partially duplicates no existing mechanism: nothing in the plugin today loads or executes code from a registry-supplied file path, and the loader's sys.path insertion is ADJACENT to the hook's own start-up insertion of the plugin's python/ directory (posttooluse_gate.py:22-26).
  - spec citation: `None`
- **C51** [shape_fit] [load-bearing]: make_line_lookup consolidates the only two line-lookup closures passed to apply_registry; no third LineLookup implementation exists (e.g. in cli_check_llm.py, the judge, or any skill snippet) that would remain a second definition.
  - spec citation: `None`
- **C52** [shape_fit] [load-bearing]: Detector-reference validation lives only in load_mandates; no second validator (the acf-mandate skill's ## Validate snippet, test_profile_drift.py, the architecture-review skill, acf-setup) independently checks detector ids in a way that would reject or mis-handle host references.
  - spec citation: `None`
- **C53** [shape_fit]: Host dispatch in the hook reuses the hook's existing abs_path.relative_to(repo) result (posttooluse_gate.py:242-245, whose ValueError branch marks out-of-repo files) rather than adding a second in-repo test.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:242-245`
- **C54** [sweep] [load-bearing]: Sweep: the call-site vocabulary in use across shipped registries and docs is {ci, precommit, hook, posttooluse, audit} (config/architecture/mandates.yml; ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:104); every value except audit falls in DIFF_CALL_SITES or HOOK_CALL_SITES, and audit is read by no Tier-1 gate, so the partition misroutes no shipped row.
  - spec citation: `None`
- **C55** [sweep] [load-bearing]: Sweep: the test changes in spec §4.6 cover every existing test the design breaks: the ten apply_registry calls in test_enforcement.py, test_hooks.py:199-218 (the [ci]-only row reported by the hook), tests/test_self_host.py:23; no other existing test depends on the hook reporting a [ci]-only row, on apply_registry's old signature, on citations._looks_absolute/_escapes_repo, or on load_mandates accepting an active row without a Tier-1 call site.
  - spec citation: `None`
- **C56** [sweep]: The prose sites in spec §4.7 cover every shipped doc (README.md, plugins/arch-compliance/skills/*/SKILL.md, docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md, docs/design/ADR_GATE_HOST_CONTRACT.md, config/architecture/ARCHITECTURE.md, hook docstrings) that states detectors must be built-in ids, describes call_sites, describes which files Tier-1 scans, or describes .acf/enabled as a trust gate.
  - spec citation: `None`
- **C57** [mechanism_justification] [load-bearing]: Deferring host import to dispatch (load_mandates validates only syntax, call sites, languages and file existence) is justified: a missing file still fails at load, an import failure or missing callable fails loud at dispatch as UnknownDetectorError caught by both gates, and importing at load would run host code in the SubagentStart hook and acf-check-llm and import CI-only guards on every edit. The spec offers no separate citation for the dispatch-time catch.
  - spec citation: `None`
- **C58** [mechanism_justification] [load-bearing]: The TIER1_CALL_SITES requirement together with the host-ast languages check is necessary and sufficient to prevent an active ast/guard row that loads (with known_detectors) yet is run by neither acf-check-diff (DIFF_CALL_SITES) nor the PostToolUse hook (HOOK_CALL_SITES).
  - spec citation: `None`
- **C59** [mechanism_justification] [load-bearing]: One-host-root-per-process eviction in load_host_detector (remove sys.modules entries whose __file__ resolves under the old root, remove the old root from sys.path, clear _MODULE_CACHE) is justified by host modules' intra-repo imports (e.g. hm:scripts/ci/metadata_facade_guard.py:66 importing scripts.ci.arch_compliance.facade_sinks) and by in-process test runs over several tmp_path roots; production callers run one process per gate run.
  - spec citation: `hm:scripts/ci/metadata_facade_guard.py:66`
- **C60** [mechanism_justification]: Parsing a Python file once and sharing the tree across every host ast detector on it is justified by avoiding N parses per file; built-in scanners keep their own parses unchanged.
  - spec citation: `None`
- **C61** [mechanism_justification] [load-bearing]: Having host callables return HostHit (path, line, message) and building Finding in the runner from the mandate row, rather than accepting Finding and overwriting fields, is justified because apply_registry matches findings to rows by mandate_id (enforcement.py:37-53) and a host-supplied mandate_id/detector/severity could otherwise attach a finding to the wrong row.
  - spec citation: `None`
- **C62** [mechanism_justification] [load-bearing]: Treating the host's own pre-commit/CI invocation of acf-check-diff as its opt-in to running host code, and gating only the automatic hooks on .acf/enabled, is justified because .acf/ is gitignored and CI would otherwise be disabled; a user who runs acf-check-diff manually in an untrusted checkout is the residual case the design accepts.
  - spec citation: `.gitignore:8`
- **C63** [mechanism_justification] [load-bearing]: The call_sites filter added to apply_registry is needed in addition to the scanners' registry.active(call_sites) selection, because some built-in scanners emit findings by detector id without consulting the registry's call_sites, so without the filter a finding for a row not declared at this gate would survive. (The spec states the filter but gives no reason it is not redundant.)
  - spec citation: `None`
- **C64** [implementability] [load-bearing]: Mandate (registry.py:14-27) is a Pydantic BaseModel exposing every field the design reads: id, severity, status, detection, detector, call_sites (list[str]), languages (Literal including 'none'), and params (dict or None); adding an @property is_active and a plain method runs_at to it, and a method active to MandateRegistry, is compatible with its model_config.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:14-27`
- **C65** [implementability] [load-bearing]: Finding (acf/finding.py) can be constructed as Finding(mandate_id=, severity=Severity(mandate.severity), path=, line=, message=, detector=, detection=): those are its fields, Severity is constructible from Mandate.severity's value, and no other required field is missing.
  - spec citation: `None`
- **C66** [implementability] [load-bearing]: apply_registry (enforcement.py) looks up each finding's row via registry.by_id, drops it on the status check at :47 (replaceable by runs_at), and handles exemptions and severity at :49-52 using a LineLookup type that make_line_lookup can return.
  - spec citation: `plugins/arch-compliance/python/acf/enforcement.py:47`
- **C67** [implementability] [load-bearing]: cli_check_diff.py has the hook points the design names with the needed names in scope: load at :70 inside a try whose except tuple at :72 lists AcfInputError, UnknownDetectorError and DetectorPackError (and wraps both load and scan); lookup and apply_registry at :76-82; in the .py branch after scan_fsm_writes (:140-150) repo, text, posix, lines and registry; in the .ts/.tsx branch (:151-156) a read that can bind text; and after the ratchet loop (:168-182) the changed-file list.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:72`
- **C68** [implementability] [load-bearing]: posttooluse_gate.py has the hook points the design names: deferred imports at :91-104, the load try at :106-110, the scan try at :113-117, lookup/apply_registry at :119-125, inline filters at :229-236 and :284-286, the relative_to with ValueError fallback at :242-245, the build-artifact loop at :284-294, and text and rel in scope in the .py and TypeScript branches of _scan_paths.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:113-117`
- **C69** [implementability] [load-bearing]: Host-detector failures reach an existing fail-loud handler in both gates: dispatch-time loading raises UnknownDetectorError and every exception from a host callable (AcfError subclasses included) is wrapped as DetectorPackError, and both are caught by cli_check_diff.py:72 and by the hook's widened scan except (DetectorPackError, UnknownDetectorError), so no host failure escapes as a traceback.
  - spec citation: `None`
- **C70** [implementability] [load-bearing]: load_host_detector isolates distinct repository roots: the hashed module name (sha256 of root and rel_path), eviction of the old root's sys.modules entries by __file__ and of its sys.path entry, and clearing _MODULE_CACHE together ensure a module loaded under one root never binds another root's helper modules.
  - spec citation: `None`
- **C71** [implementability] [load-bearing]: Registering the module in sys.modules under its name before spec.loader.exec_module(mod) is what lets a host module define a @dataclass under `from __future__ import annotations` (dataclasses resolves sys.modules[cls.__module__]); importlib.util.spec_from_file_location with a synthetic name supports this.
  - spec citation: `None`
- **C72** [implementability] [load-bearing]: The imports the design adds are cycle-free and allowed: acf.registry imports only acf.engine (nothing from acf.detectors); acf.detectors.host imports registry, finding, engine and exceptions; acf/adr/citations.py importing acf.engine is permitted by test_adr_import_graph.py; and the hook's new deferred imports do not reach acf.adr.
  - spec citation: `plugins/arch-compliance/tests/test_adr_import_graph.py:70-76`
- **C73** [implementability] [load-bearing]: load_mandates today loads rows via load_model_file(path, Mandate, subject='mandates file', fmt='yaml', many=True) returning a list of Mandate, and builds MandateRegistry(mandates=..., source_path=path.as_posix()), so the §4.2 body is a drop-in extension of the existing function.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:48-64`
- **C74** [implementability]: plugins/arch-compliance/tests/test_repo_paths.py:47-48 pins the text of posttooluse_gate.py's docstring line :11 and not :12, so rewording :12 and keeping :11 verbatim breaks no test.
  - spec citation: `plugins/arch-compliance/tests/test_repo_paths.py:47-48`
- **C75** [implementability] [load-bearing]: config/architecture/mandates.yml:60 declares fail-loud.bare-except-ok as the exemption token for the fail-loud.bare-except detector, and that detector honours it on an `except Exception` line, so the two handlers in acf.detectors.host pass the repository's own gate.
  - spec citation: `config/architecture/mandates.yml:60`
- **C76** [implementability]: acf/engine.py already defines contains_backslash and is stdlib-only, so adding looks_absolute, resolve_under_root and validate_posix_rel_path with `import re` and `from pathlib import Path` keeps it stdlib-only and gives validate_posix_rel_path its backslash test without a new dependency.
  - spec citation: `plugins/arch-compliance/python/acf/engine.py`
