# Adversarial design review — full detail

Spec: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md` @ `5895daf47accce0d5733f842965693a15e41d063`
Kinds: defect, feature
Outcome: **BLOCKED**
Claims: 52 · Reviewers: 4 · Converged: 3

## Blocking reasons

- load-bearing claim C2 (premise) is REFUTED: The first half holds. KNOWN_DETECTORS is a closed module-level union (cli_check_diff.py:25), and a git grep found no extension hook, entry point or mutation. The second half is false as worded. registry.py:58 validates only status == 'enforced', but a status: partial row is active (enforcement.py:47 drops only unenforced). So a host CAN name its own detector in an active (partial) ast/guard row and still load with known_detectors=KNOWN_DETECTORS. The row is then silently never executed. The real gap is 'validated-or-executed', not 'cannot load'.
- load-bearing claim C18 (mandate) is REFUTED: The claim says no path lets an active ast/guard row load without being executable. The spec's decision-2 heading (:46) promises 'no unexecuted active ast/guard rows'. load_mandates (§4.3) checks only that call_sites meets TIER1_CALL_SITES. The Language literal allows 'none' (registry.py:11), and scan_host_ast_file runs a row only when m.languages is in {language, 'both'} (:203). So an enforced host ast row with languages: none and call_sites: [ci] passes load_mandates, and neither gate ever runs it. That is the very failure §1.2 calls a Fail loud violation ('pass validation while nothing ever executes it'). The other mechanics hold: UnknownDetectorError/AcfInputError/DetectorPackError are raised as described, and the hook catches UnknownDetectorError at load. The universal claim does not.
- load-bearing claim C32 (shape_fit) is REFUTED: Searched by behaviour (absolute/drive check, '..'/escape check, is_relative_to, startswith('/')) rather than by the name 'validator'. acf.adr already has two path-shape decisions besides PosixStr, and the claim's exclusion does not cover them: _looks_absolute (citations.py:49-51, regex ^([A-Za-z]:[\\/]|/|\\\\)) decides 'drive-rooted or root-anchored', and _escapes_repo (citations.py:74-76) decides 'climbs out of the tree'. validate_posix_rel_path re-decides both with a different rule: it treats 'C:a/b.py' as drive-rooted, which _looks_absolute does not, and it refuses '..' lexically where citations resolves and tests is_relative_to. The design also adds two more is_relative_to containment checks of its own (load_host_detector and make_line_lookup, spec §4.2 item 3 and §4.4). After the design there is a second, divergent way to decide 'is this a repo-relative path', so the 'creates no second way' claim fails. The sweep looked only for whole validators, by name and type (PosixStr), not for the verbs.
- load-bearing claim C38 (sweep) is REFUTED: The cited line filters on detector and status only (m.detector == detector and m.status != 'unenforced'), not on call_sites. The hook does the same (plugins/arch-compliance/hooks/posttooluse_gate.py:229-236, 284-286). Grepping call_sites across python/ and hooks/ finds no gate that reads the field. The Mandate model accepts any string (plugins/arch-compliance/python/acf/registry.py:21, call_sites: list[str]), so there is no accepted vocabulary to match. Values in use are ci, hook and audit (config/architecture/mandates.yml:11,47,154), and the design doc lists precommit, ci, posttooluse and audit (docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:104). The premise that the routing matches what the existing gates filter on is false: the design creates call-site routing, and only for host rows.
- load-bearing claim C40 (mechanism_justification) is REFUTED: The justification says a syntax-only check would 'let the row go inert'. That is false against the spec's own runners. scan_host_guards (spec 4.2 item 6) runs every active guard row in its call-site set on every invocation, in the repo-level slot after scan_ratchet (cli_check_diff.py:168-182). It calls load_host_detector outside the try, so a missing or broken module raises UnknownDetectorError at dispatch anyway. scan_host_ast_file does the same whenever a matching file changes. The spec gives no written rejection of dispatch-time validation; 'alternatives rejected' appears nowhere. The cost is also unstated: load_mandates imports every active host row whatever its call_sites, so the PostToolUse hook (fresh process per edit, load at posttooluse_gate.py:107) imports and runs the top-level code of CI-only guard modules on every edit. That contradicts spec 2.3's stated goal of 'without slowing down every file edit in PostToolUse'.
- load-bearing claim C41 (mechanism_justification) is REFUTED: TIER1 = DIFF | HOOK, so a non-empty intersection does guarantee some runner's call-site filter admits the row. It is not sufficient. Language = Literal['python','typescript','both','none'] (registry.py:11), and Mandate.languages is required (registry.py:20). scan_host_ast_file filters on m.languages in {language, 'both'} (spec 4.2 item 5). So an active host ast row with languages: none and call_sites: [ci] passes load_mandates, including the module import, and is run by neither _scan_changed nor _scan_paths. That is exactly the inert active BLOCK row the check exists to prevent. load_mandates does not check languages for host ast rows.
- load-bearing claim C50 (implementability) is REFUTED: cli_check_diff.py:69-74 wraps both load_mandates and _scan_changed and catches GitError, AcfInputError, UnknownDetectorError and DetectorPackError. In the hook, the scan try at :113-117 catches only DetectorPackError. The spec's runners do 'except AcfError: raise' (spec 4.2 items 5/6) and call load_host_detector outside the try. So a host callable raising any AcfError subclass (AcfInputError, UnknownDetectorError, BaselineError...), or a scan-time UnknownDetectorError, escapes _scan_paths unhandled as a traceback. In cli_check_diff, AcfError subclasses outside its four-tuple escape too. The failures stay loud via traceback but do not reach 'an existing fail-loud handler'.
- load-bearing claim C52 (implementability) is REFUTED: module_name is never defined in the spec, so isolation of the sys.modules registration is unspecified. If it derives from rel_path, two roots with the same rel_path overwrite each other's sys.modules entry. Independently, the spec puts str(root) at the front of sys.path permanently, once per root. Host modules' intra-repo imports resolve through sys.modules first. HM guards do 'from scripts.ci.arch_compliance.facade_sinks import ...' (metadata_facade_guard.py:66), and HM has scripts/__init__.py. Once one root's 'scripts' package is cached, a second root's module silently binds the first root's helpers. The 'never collide' claim fails, and nothing refuses.
- mandate claim C18 is REFUTED: The claim says no path lets an active ast/guard row load without being executable. The spec's decision-2 heading (:46) promises 'no unexecuted active ast/guard rows'. load_mandates (§4.3) checks only that call_sites meets TIER1_CALL_SITES. The Language literal allows 'none' (registry.py:11), and scan_host_ast_file runs a row only when m.languages is in {language, 'both'} (:203). So an enforced host ast row with languages: none and call_sites: [ci] passes load_mandates, and neither gate ever runs it. That is the very failure §1.2 calls a Fail loud violation ('pass validation while nothing ever executes it'). The other mechanics hold: UnknownDetectorError/AcfInputError/DetectorPackError are raised as described, and the hook catches UnknownDetectorError at load. The universal claim does not.
- mandate claim C29 is REFUTED: The rule says a factual claim is 'not load-bearing on "every", "all", "only"... unless a recipe that a reader can re-run backs the quantifier'. It asks for a re-runnable recipe, not an enumerated list, so the claim paraphrases it wrongly. The spec also carries universals with neither: decision 2's 'no unexecuted active ast/guard rows' (:46) is false (see C18), and ':6 differs from main only by this spec' has no recipe.
- implementability claim C50 is REFUTED: cli_check_diff.py:69-74 wraps both load_mandates and _scan_changed and catches GitError, AcfInputError, UnknownDetectorError and DetectorPackError. In the hook, the scan try at :113-117 catches only DetectorPackError. The spec's runners do 'except AcfError: raise' (spec 4.2 items 5/6) and call load_host_detector outside the try. So a host callable raising any AcfError subclass (AcfInputError, UnknownDetectorError, BaselineError...), or a scan-time UnknownDetectorError, escapes _scan_paths unhandled as a traceback. In cli_check_diff, AcfError subclasses outside its four-tuple escape too. The failures stay loud via traceback but do not reach 'an existing fail-loud handler'.
- implementability claim C52 is REFUTED: module_name is never defined in the spec, so isolation of the sys.modules registration is unspecified. If it derives from rel_path, two roots with the same rel_path overwrite each other's sys.modules entry. Independently, the spec puts str(root) at the front of sys.path permanently, once per root. Host modules' intra-repo imports resolve through sys.modules first. HM guards do 'from scripts.ci.arch_compliance.facade_sinks import ...' (metadata_facade_guard.py:66), and HM has scripts/__init__.py. Once one root's 'scripts' package is cached, a second root's module silently binds the first root's helpers. The 'never collide' claim fails, and nothing refuses.
- mechanism '_MODULE_CACHE keyed by (root, rel_path, st_mtime_ns, st_size)' has no named producer for the state it handles (a cached host module whose source file's mtime or size changed on disk since it was imported within the same process) — superstition

## Absorptions

- PARTIAL_OVERLAP: 'validate_posix_rel_path (acf.engine)' shares responsibility 'decide whether a path string is absolute/drive-rooted or escapes the repo root' with plugins/arch-compliance/python/acf/adr/citations.py:49-51 — Responsibility R is 'classify a path's relative/absolute/escaping shape'. Put one stdlib-only predicate in acf.engine (e.g. posix_rel_path_problem(value) -> str | None). validate_posix_rel_path raises on a non-None result, and citations._looks_absolute / _escapes_repo branch on it. The two containment checks the spec adds (load_host_detector is_relative_to, make_line_lookup is_relative_to) collapse into one acf.engine resolve_under_root(root, rel) helper.
- PARTIAL_OVERLAP: 'acf.detectors.host._normalize_findings' shares responsibility 'validate external detector output and convert it into Finding rows, raising DetectorPackError' with plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:75-95 — Responsibility R is 'coerce untrusted detector output into Finding, failing loud'. Both should use one shared coercion helper in acf.finding with a single path policy: the bridge silently normalizes backslashes with posix_path, while the host path refuses them. Each keeps only its private part (JSON decoding for the bridge, mandate_id/detector/detection stamping for host rows).
- PARTIAL_OVERLAP: 'scan_host_ast_file / scan_host_guards mandate filters' shares responsibility "select active mandates (status != 'unenforced') for a detector or detection" with plugins/arch-compliance/python/acf/cli_check_diff.py:94-99 — Responsibility R is 'which registry rows are live for this scan'. Add one MandateRegistry.active(detector=None, detection=None, call_sites=None) method in acf.registry. cli_check_diff._active_mandates, the inline filters in posttooluse_gate.py:229-236 and :284-286, and the two new host.py list comprehensions all become calls to it, which also gives built-in and host rows the same call_sites semantics.
- PARTIAL_OVERLAP: 'host ast/guard wiring in _scan_changed and _scan_paths' shares responsibility 'per-file Tier-1 dispatch over built-in and host detectors' with plugins/arch-compliance/hooks/posttooluse_gate.py:213-295 — Responsibility R is 'run every active Tier-1 detector on a file set'. _scan_changed (cli_check_diff.py:102-184) and _scan_paths are already parallel copies, and the spec adds the same three host calls to both. Extracting one acf.tier1.scan_files(repo, files, added_lines_fn, registry, allowed_call_sites) leaves each gate with only path collection and the diff/hook scope difference.
- PARTIAL_OVERLAP: 'scan_host_ast_file single ast.parse' shares responsibility 'parse a .py file into an AST for Tier-1 scanning' with plugins/arch-compliance/python/acf/detectors/python_pack.py:35 — Responsibility R is 'parse once per file'. Parse in the shared dispatcher and pass tree= to scan_python_file, scan_facade_sinks (facade_sinks.py:51) and scan_fsm_writes (fsm_guard.py:37) as well as to host detectors. Otherwise the 'one parse per file' claim covers only host detectors.
- PARTIAL_OVERLAP: 'make_line_lookup on-demand read' shares responsibility "read a repo file's lines into file_lines" with plugins/arch-compliance/python/acf/cli_check_diff.py:125-126 — Responsibility R is 'load file lines for exemption lookup'. The gates read strict utf-8 (cli_check_diff.py:125,152; posttooluse_gate.py:251), while make_line_lookup reads with errors='replace'. Have the gates populate through the same reader, or state why the decoding policies differ.
- SUBSUMED: 'load_mandates host validation branch' shares responsibility 'validate ast/guard detector references at registry load' with plugins/arch-compliance/python/acf/registry.py:56-63 — Extend in place, as the spec does. The built-in membership check becomes one branch of the generalized active-row check, and no sibling validator is added.
- IDENTICAL: 'make_line_lookup (acf.enforcement)' shares responsibility 'map (posix, line) to source text for exemption matching' with plugins/arch-compliance/hooks/posttooluse_gate.py:119-124 — Delete both closures (here and cli_check_diff.py:76-81) and have both gates consume make_line_lookup, as the spec states.
- mechanism 'TIER1_CALL_SITES requirement in load_mandates' sits at rung 3 when rung 1 applies, with no written justification
- mechanism '_MODULE_CACHE keyed by (root, rel_path, st_mtime_ns, st_size)' sits at rung 5 when rung 2 applies, with no written justification
- mechanism '_normalize_findings overwrite of mandate_id/detector/detection' sits at rung 5 when rung 1 applies, with no written justification
- mechanism '_normalize_findings refusals (non-iterable, non-Finding item, backslash or blank path, line < 1)' sits at rung 3 when rung 1 applies, with no written justification

## Converged findings

- [2 reviewers: compliance, hardening] The .acf/enabled trust boundary the spec documents for acf-check-diff does not exist: cli_check_diff.main never checks the marker and the design adds no check (and .acf/ is gitignored, so CI could never carry it).
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:63-71`
  - evidence: `.gitignore:8`
- [2 reviewers: compliance, hardening] An active host ast row with languages: none passes load_mandates (Tier-1 call-site check and import included) but is matched by neither scan_host_ast_file language filter, so it is an inert active row the design claims cannot exist.
  - evidence: `plugins/arch-compliance/python/acf/registry.py:11`
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:203`
- [2 reviewers: refuter, sweeper] The new unconditional host-ref syntax check raises UnknownDetectorError for every load_mandates caller, but hooks/inject_constraints.py catches only AcfInputError, so a malformed host ref crashes the SubagentStart hook; the spec gives that caller no disposition.
  - evidence: `plugins/arch-compliance/hooks/inject_constraints.py:103-107`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:56-63; plugins/arch-compliance/tests/test_registry.py:20-30`
- reasoning: At 5895daf, registry.py:58 skips every row whose status != 'enforced'. Then :60 raises UnknownDetectorError only when detection is in {ast, guard} and the detector is not in known_detectors. So partial rows are never checked. test_registry.py:20-30 pins the enforced-row rejection.

#### C2 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:25; plugins/arch-compliance/python/acf/registry.py:58; plugins/arch-compliance/python/acf/enforcement.py:47`
- reasoning: The first half holds. KNOWN_DETECTORS is a closed module-level union (cli_check_diff.py:25), and a git grep found no extension hook, entry point or mutation. The second half is false as worded. registry.py:58 validates only status == 'enforced', but a status: partial row is active (enforcement.py:47 drops only unenforced). So a host CAN name its own detector in an active (partial) ast/guard row and still load with known_detectors=KNOWN_DETECTORS. The row is then silently never executed. The real gap is 'validated-or-executed', not 'cannot load'.

#### C3 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:16-22; plugins/arch-compliance/python/acf/detectors/__init__.py:11-28; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:14; plugins/arch-compliance/python/acf/judge.py:29-36`
- reasoning: KNOWN_DETECTORS has 13 ids, not 11. They are 3 Python AST ids, 4 guard ids, 2 TS ids and 4 LLM prompt ids. Importing the module and printing len(KNOWN_DETECTORS) gave 13: empty_catch, explicit_any, fail_loud_bare_except, fail_loud_ratchet, forbid_facade_sink, fsm_transition_guard, llm_fail_loud, llm_no_shims, llm_posix_paths, llm_react_boundaries, no_build_artifacts, no_shims_hasattr, posix_paths_str_serialization.

#### C4 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99; plugins/arch-compliance/python/acf/cli_check_diff.py:124-182; plugins/arch-compliance/hooks/posttooluse_gate.py:229-294`
- reasoning: _scan_changed calls scan_python_file, scan_facade_sinks, scan_fsm_writes, scan_typescript_file, scan_build_artifact_paths and scan_ratchet. It selects them only by exact match against hardcoded built-in ids (_active_mandates compares m.detector == <constant>). _scan_paths has the same shape, without scan_ratchet. Neither resolves a detector from a registry-supplied reference, so a non-built-in detector string is never run.

#### C5 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:107; plugins/arch-compliance/hooks/posttooluse_gate.py:229-236; plugins/arch-compliance/python/acf/registry.py:56`
- reasoning: The hook calls load_mandates(mandates_path) with no known_detectors, so registry.py:56 skips the whole check. Its scanners dispatch only on built-in ids (:229-236, :284-285). An active row naming an unknown id therefore yields zero findings with exit 0 instead of failing.

#### C6 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:106-110; plugins/arch-compliance/python/acf/exceptions.py:5-14`
- reasoning: The hook wraps load_mandates in `except AcfInputError` only. exceptions.py:13 defines UnknownDetectorError(AcfError), a sibling of AcfInputError(AcfError) at :5, not a subclass. So it would escape as an uncaught traceback.

#### C7 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80; plugins/arch-compliance/python/acf/cli_check_diff.py:124-152; plugins/arch-compliance/hooks/posttooluse_gate.py:248-252; plugins/arch-compliance/python/acf/enforcement.py:49-50`
- reasoning: Both closures read only file_lines.get(posix) and return '' on a miss. file_lines is filled only for changed .py/.ts/.tsx files (cli :126, :152; the hook skips non-code suffixes at :248). apply_registry calls token_exempted on the looked-up line (enforcement.py:49-50), and '' never matches. So exemptions on any other file are ignored.

#### C8 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:47; plugins/arch-compliance/python/acf/cli_check_diff.py:98; plugins/arch-compliance/hooks/posttooluse_gate.py:231; plugins/arch-compliance/skills/acf-mandate/SKILL.md:45; plugins/arch-compliance/skills/acf-mandate/SKILL.md:57`
- reasoning: apply_registry drops only status == 'unenforced'. Both the CLI and the hook select mandates with status != 'unenforced'. SKILL.md:45 and :57 state that partial still gates.

#### C9 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/contract.py:60-91; plugins/arch-compliance/python/acf/adr/contract.py:129; plugins/arch-compliance/tests/test_adr_import_graph.py:70-76`
- reasoning: The substance holds. PosixStr = Annotated[str, AfterValidator(_reject_backslash)] at :129, and _reject_backslash only checks contains_backslash. It lives in acf.adr, and test_adr_import_graph.py:70-76 fails if either hook's source text contains 'acf.adr'. The spec's cited location for _reject_backslash is wrong: it is at contract.py:60-91, not :98-101 (lines 94-103 are regex constants). A grep of the non-adr acf modules found no other relative-path validator. acf/adr/citations.py:76 has an escape check, but it is also inside acf.adr.

#### C10 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/engine.py:1-31; plugins/arch-compliance/python/acf/adr/contract.py:20`
- reasoning: engine.py has exactly 31 lines. Its only import is `from pathlib import Path`. It defines posix_path (:11-14), contains_backslash (:17-25) and is_in_scope (:27-31). contract.py:20 imports contains_backslash from it.

#### C11 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/arch_compliance/engine.py:1154-1173; C:/Users/iball/Arduino/Projects/HistoricMansions/config/architecture/mandates.yml:97`
- reasoning: I parsed git show b652fab05:config/architecture/mandates.yml and counted (status, detection) pairs. The counts were enforced/guard 25, enforced/ast 17, partial/llm 5 and enforced/manual 1. The 17 ast detector names equal the 17 DETECTOR_REGISTRY keys at engine.py:1155-1172. Lines :97 and :109 carry scripts/ci/metadata_facade_guard.py and scripts/ci/check_image_path_contract.py.

#### C12 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/config/architecture/mandates.yml:11; C:/Users/iball/Arduino/Projects/HistoricMansions/config/architecture/mandates.yml:5-25`
- reasoning: Every enforced ast row at b652fab05 declares [precommit, posttooluse, ci]. Every enforced guard row declares [precommit, ci], [ci] or [precommit] (check_ui_prepass_staged.py). All of these intersect {ci, precommit, hook, posttooluse}. Unstated: the HM rows carry no `languages` or `arch_anchor` field (they use gemini_anchor), and the plugin Mandate model requires both (registry.py:20,24). The cutover must therefore rewrite every row, not just the detector field.

#### C13 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/arch_compliance/engine.py:36-44; C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/arch_compliance/engine.py:1200-1218; C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/metadata_facade_guard.py:295-318; C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/check_image_path_contract.py:10-22`
- reasoning: The inputs fit. HM AST detectors have the shape find(tree, ctx, path) and yield nodes. ctx is a frozen EngineContext built from module constants (default_context(), engine.py:511-519), so an adapter given (text, path, added_lines, tree, params) can rebuild ctx, filter by added_lines and emit Finding(line=node.lineno). metadata_facade_guard needs only repo_root (scan_direct_index_writers(repo_root)). check_image_path_contract needs only fixed paths under the repo root. Its file-level errors with no line, and metadata_facade_guard's stale-allowlist failures, must be mapped to line 1. HM's '<tok>-ok:' exemption form can be matched by setting exemption_tokens to '<tok>-ok'. I found no '# arch-ok:' uses outside the engine. The 'no further plugin change' part does not fully hold for parse-failure semantics; see unanchored finding 2.

#### C14 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:12-29; plugins/arch-compliance/skills/architecture-review/SKILL.md:62`
- reasoning: git ls-files shows no acf/architecture_review package. plugins/arch-compliance/python/acf contains only adr/, detectors/ and flat modules. The config/ tree holds only ARCHITECTURE.md, adr.yml and mandates.yml. acf.repo declares no review-config constant. The architecture-review skill is prose and auditors only.

#### C15 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-80; plugins/arch-compliance/hooks/posttooluse_gate.py:119-123`
- reasoning: The two closures are token-for-token identical. In the proposed make_line_lookup, a key already present in file_lines (including an empty list) is not re-read and returns the same value. Hook keys that are absolute paths for files outside the repo (posttooluse_gate.py:245) fail is_relative_to(root) and return ''. So current behavior is preserved for every key already in file_lines.

#### C16 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37; plugins/arch-compliance/python/acf/detectors/facade_sinks.py:50-53; plugins/arch-compliance/python/acf/detectors/fsm_guard.py:36-39`
- reasoning: I opened all three. Each wraps ast.parse(text) in `try ... except SyntaxError: return []` at exactly the cited lines.

#### C17 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:104; plugins/arch-compliance/python/acf/cli_check_llm.py:54; plugins/arch-compliance/tests/test_registry.py:57; tests/test_self_host.py:23`
- reasoning: I ran the spec's own git grep. Its call/definition lines match the list exactly. The other matches are import lines and one docstring mention (plugins/arch-compliance/tests/test_loader.py:70), so the list is accurate as a call-site list, not as raw grep output.

### Unanchored findings

- **important**: The new unconditional host-ref syntax check in load_mandates raises UnknownDetectorError even without known_detectors. inject_constraints.py (SubagentStart hook) catches only AcfInputError and cli_check_llm.py catches nothing, so a malformed host ref crashes both with an uncaught traceback. The spec adds the extra catch only to posttooluse_gate.py.
  - evidence: `plugins/arch-compliance/hooks/inject_constraints.py:103-107`
- **important**: scan_host_ast_file returns [] on SyntaxError before calling any host detector, and scan_guard gets no diff-mode input. The HM driver this design is meant to absorb instead emits a WARN 'parse' finding in staged/head mode and fails loud in range mode, so porting HM's AST lane silently drops unparseable files unless the plugin changes, contrary to the 'no further plugin change' deferral.
  - evidence: `C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/ci/arch_compliance/driver.py:139-157`
- **advisory**: In the hook, rel_paths falls back to an absolute POSIX path for files outside the repo, and the design passes rel_paths straight to scan_host_guards as changed_files. Host guards could therefore receive absolute paths despite the repo-relative contract.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:242-246`
- **advisory**: Built-in scanners in the hook ignore call_sites (for example no-shims.hasattr declares only [ci] but scan_python_file always runs in PostToolUse), while host detectors would be routed by call_sites. The same registry field would mean different things for built-in and host rows.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:254`
- **advisory**: The spec cites _reject_backslash at contract.py:98-101, but it is defined at :60-91; lines 94-103 are regex constants.
  - evidence: `plugins/arch-compliance/python/acf/adr/contract.py:60`
- **advisory**: HM mandate rows have no `languages` or `arch_anchor` fields, both required by the plugin Mandate model, and scan_host_ast_file filters on m.languages. The cutover must add both to every HM row, which the deferral does not state.
  - evidence: `plugins/arch-compliance/python/acf/registry.py:20`

### Looked for but did not find

- any mutation of or extension mechanism for KNOWN_DETECTORS (entry points, env var, host-supplied set) in plugins/ or tests/
- any existing active (enforced or partial) ast/guard row with an unknown detector in config/architecture/mandates.yml or plugins/arch-compliance/profiles/*/mandates.yml that the stricter partial check would newly reject
- a non-acf.adr relative-POSIX-path validator anywhere in plugins/arch-compliance/python/acf
- an acf/architecture_review package or a review host-config constant in acf/repo.py
- uses of the HM '# arch-ok: <token> reason' exemption form in HM scripts outside the engine, which plugin token_exempted could not match

## compliance

### Claim verdicts

#### C18 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/registry.py:11; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:203; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:46`
- reasoning: The claim says no path lets an active ast/guard row load without being executable. The spec's decision-2 heading (:46) promises 'no unexecuted active ast/guard rows'. load_mandates (§4.3) checks only that call_sites meets TIER1_CALL_SITES. The Language literal allows 'none' (registry.py:11), and scan_host_ast_file runs a row only when m.languages is in {language, 'both'} (:203). So an enforced host ast row with languages: none and call_sites: [ci] passes load_mandates, and neither gate ever runs it. That is the very failure §1.2 calls a Fail loud violation ('pass validation while nothing ever executes it'). The other mechanics hold: UnknownDetectorError/AcfInputError/DetectorPackError are raised as described, and the hook catches UnknownDetectorError at load. The universal claim does not.

#### C19 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:120-122; plugins/arch-compliance/python/acf/cli_check_diff.py:63-70; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:263`
- reasoning: The doctrine text is written for the adversarial-design-review gate's adr.yml values: 'no default stands in for a missing declaration, and a missing declaration fails loud'. Extending its spirit is sound. §4.3 raises AcfInputError('pass repo_root to load_mandates') rather than deriving a root. Both gates pass the repo they already resolve (cli_check_diff.py:63), so no new default enters. resolve_repo's cwd fallback is a default the doctrine records itself (:126-128).

#### C20 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:48-49; config/architecture/mandates.yml:64-73`
- reasoning: The rule forbids hasattr probing that papers over missing interfaces. The loader's getattr(mod, attr_name, None) is followed by not callable(fn) -> raise UnknownDetectorError, so nothing degrades silently. Import failure and callable exceptions both raise. Minor caveat: make_line_lookup's except OSError -> [] is a quiet path, but it is a line lookup, not a detector failure (see the advisory finding).

#### C21 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:62-64; plugins/arch-compliance/python/acf/engine.py:17-24`
- reasoning: The doctrine requires POSIX persisted paths, and this plugin refuses a backslash rather than normalising it. validate_posix_rel_path calls contains_backslash (engine.py:17-24). _normalize_findings refuses backslash paths before findings reach the JSON output. The loader error message uses .as_posix(). This matches the stricter refuse-not-normalise stance at :62-64.

#### C22 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/exceptions.py:5; plugins/arch-compliance/python/acf/exceptions.py:13; plugins/arch-compliance/python/acf/exceptions.py:29`
- reasoning: The doctrine says every ACF exception subclasses AcfError alone. The design adds no class. It reuses AcfInputError(AcfError), UnknownDetectorError(AcfError) and DetectorPackError(AcfError), none of which has a stdlib mixin.

#### C23 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:93; config/architecture/ARCHITECTURE.md:107-108`
- reasoning: acf.repo is the one declaration of host paths. The engine.py and host.py code in §4.1-4.2 spells no config/architecture path, and the hook keeps using ENABLED_REL/MANDATES_REL. The skill snippet already imports ARCH_REL and MANDATES_REL from acf.repo (SKILL.md:93). The design adds resolve_repo from the same module (§4.6 item 2), so 'keeps importing resolve_repo' is slightly off, but the rule holds.

#### C24 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:137-138; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:165; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:332`
- reasoning: The rule says skill prose and runtime messages name no host. Every runtime message the design spells out (e.g. :165, :263) is generic. The described skill-prose changes (:332, :334) name only the generic <posix_rel_path.py>:<callable_name> contract. HistoricMansions appears only in the spec's own motivation and non-goals, which this rule does not cover.

#### C25 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:155-156; plugins/arch-compliance/python/acf/cli_check_diff.py:70; plugins/arch-compliance/hooks/posttooluse_gate.py:107`
- reasoning: 'An export has a live call site in the package, a hook or a skill.' Each new export is reached from runtime code: TIER1_CALL_SITES, the predicate, parser and loader from load_mandates; DIFF_CALL_SITES and scan_* from _scan_changed; HOOK_CALL_SITES and scan_* from _scan_paths; make_line_lookup from both mains (which today hold the duplicate closures at these sites); validate_posix_rel_path from parse_host_detector_ref. Withholding PosixRelPath is consistent with the rule.

#### C26 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:173-174; plugins/arch-compliance/python/acf/cli_check_diff.py:152`
- reasoning: The rule requires an explicit encoding on subprocess text reads and on prose file reads. It says nothing about the errors= mode, so errors='replace' with encoding='utf-8' complies. The reads the design adds (the .ts text in _scan_changed, make_line_lookup) declare utf-8, matching the existing cli_check_diff.py:152. The design adds no subprocess call.

#### C27 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:186-187; pyproject.toml:3; plugins/arch-compliance/.claude-plugin/plugin.json:3; .claude-plugin/marketplace.json:7-11`
- reasoning: 'A change to a skill's prose bumps the plugin version in plugin.json and pyproject.toml.' Both files carry "0.2.2" today, and the design bumps both to 0.2.3. marketplace.json carries no version, so no third site exists. The installed-skill byte check is procedural and does not apply to the design.

#### C28 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:198-200; plugins/arch-compliance/python/acf/cli_check_diff.py:76-81; plugins/arch-compliance/hooks/posttooluse_gate.py:119-124`
- reasoning: The rule requires exactly one canonical implementation for an operation that several modules need. The two identical _line_lookup closures (cli_check_diff.py:76-81, posttooluse_gate.py:119-124) collapse into make_line_lookup. Host parsing, loading and running live only in acf.detectors.host, which load_mandates and both gates consume. The design adds no second copy.

#### C29 — REFUTED
- evidence: `config/architecture/ARCHITECTURE.md:161-163; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:46`
- reasoning: The rule says a factual claim is 'not load-bearing on "every", "all", "only"... unless a recipe that a reader can re-run backs the quantifier'. It asks for a re-runnable recipe, not an enumerated list, so the claim paraphrases it wrongly. The spec also carries universals with neither: decision 2's 'no unexecuted active ast/guard rows' (:46) is false (see C18), and ':6 differs from main only by this spec' has no recipe.

#### C30 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:147-148; config/architecture/ARCHITECTURE.md:213-215; plugins/arch-compliance/python/acf/cli_check_diff.py:152`
- reasoning: The design touches no LedgerRow or LedgerAmendment field. Folding _line_lookup into make_line_lookup and reading .ts text in _scan_changed (cli_check_diff.py:151-156) both change code paths the design is already rewriting. That matches 'remove... non-contractual patterns in code paths you are changing' without spreading to unrelated modules.

#### C31 — SURVIVED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:123; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:125; docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:47-50`
- reasoning: :123 and :125 each call for 'Extension points for project-specific detectors', and the design supplies one with a typed contract and one Finding schema (principle 2). Principle 1 (typed errors, no silent defaults on registry load) holds in its mechanism, apart from the languages:none gap filed under C18. Principle 4 (call sites agree) is enforced by the Tier-1 check. The :184 error-handling line is updated in step.

### Unanchored findings

- **important**: The design's two `except Exception as exc: raise DetectorPackError(...)` handlers in scan_host_ast_file and scan_host_guards will be flagged BLOCK by this repository's enforced fail-loud.bare-except row (call_sites [ci, hook]), whose detector flags any `except Exception` whatever its body. The spec never names the required `# fail-loud.bare-except-ok: <reason>` exemption, which contradicts its own definition of done that `acf.cli_check_diff --base origin/main` passes (:413). The rule allows such a handler only 'explicitly exempted with a reason' (ARCHITECTURE.md:29-30).
  - evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:77-81; config/architecture/mandates.yml:53-62; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:209; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:227`
- **important**: Decision 5 and the planned acf-setup prose (:334) describe `.acf/enabled` as the trust opt-in for running host detectors 'in PostToolUse and acf-check-diff'. cli_check_diff.main never checks `.acf/enabled`, and §4.5 adds no check. load_mandates(known_detectors=..., repo_root=...) would therefore import and run host Python in acf-check-diff and in the acf-mandate validate snippet without the marker, so the trust-boundary prose would be false.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:63-70; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:334`
- **advisory**: make_line_lookup swallows an OSError reading a flagged file into `lines = []` and caches it with no report. It fails toward keeping the finding, but it is a catch body that hides a read failure, which the Fail loud prose ('Do not swallow failures') discourages.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:298; config/architecture/ARCHITECTURE.md:26-27`

### Looked for but did not find

- ## High-frequency misses (ARCHITECTURE.md:217-228): checked all six. A completeness claim without a recipe was found (C29). No default re-enters for repo_root. No host name in runtime messages. No new exception class or mixin. No subprocess is added. KNOWN_DETECTORS and load_mandates are consumed from the package, not re-implemented.
- ## Build artifacts / ## Fail-loud ratchet / ## Façade sinks / ## FSM transitions: built-in dispatch in both gates is unchanged; the design only appends host calls after the existing scanners. Not touched.
- ## Soft fail-loud smells / ## React boundaries: no llm row or React surface touched. The only change to built-in validation (status != 'unenforced') applies to ast/guard only. Not touched.
- ## Post-merge: no change to housekeeping declarations. Not touched.
- Doctrine preamble scope (ARCHITECTURE.md:9-11, gates run on changed .py/.ts/.tsx): this repository declares no host detector rows, so the statement stays true here. Not a governing miss.
- unstated_mandates is empty because the spec's Governing mandates line names every doctrine section this design touches (Fail loud through Scoped refactor, plus the portable principles).

## sweeper

### Claim verdicts

#### C32 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/adr/citations.py:49-51`
- reasoning: Searched by behaviour (absolute/drive check, '..'/escape check, is_relative_to, startswith('/')) rather than by the name 'validator'. acf.adr already has two path-shape decisions besides PosixStr, and the claim's exclusion does not cover them: _looks_absolute (citations.py:49-51, regex ^([A-Za-z]:[\\/]|/|\\\\)) decides 'drive-rooted or root-anchored', and _escapes_repo (citations.py:74-76) decides 'climbs out of the tree'. validate_posix_rel_path re-decides both with a different rule: it treats 'C:a/b.py' as drive-rooted, which _looks_absolute does not, and it refuses '..' lexically where citations resolves and tests is_relative_to. The design also adds two more is_relative_to containment checks of its own (load_host_detector and make_line_lookup, spec §4.2 item 3 and §4.4). After the design there is a second, divergent way to decide 'is this a repo-relative path', so the 'creates no second way' claim fails. The sweep looked only for whole validators, by name and type (PosixStr), not for the verbs.

#### C33 — SURVIVED
- evidence: `tests/test_check_installed_skills.py:15`
- reasoning: Grepped the whole tree (*.py) for importlib, spec_from_file_location, import_module, exec_module, runpy and exec(. The only hits are tests: tests/test_check_installed_skills.py:15 loads a fixed script for testing, and plugins/arch-compliance/tests/test_adr_skill_prose.py:57 imports modules named in prose. The TypeScript bridge (plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:16,37-56) runs a fixed plugin-owned pack (_PACK_ROOT) as a subprocess; it never takes a path or callable from a registry row. judge.py reads a fixed _PROMPT_TEMPLATE (judge.py:260). Nothing loads code from a registry-supplied reference. One partial overlap exists on a different responsibility (validating external detector output into Finding); it is listed under relationships.

#### C34 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-82`
- reasoning: Grepped for line_lookup, LineLookup and apply_registry across the tree, excluding docs. The only runtime LineLookup implementations are cli_check_diff.py:76-81 and plugins/arch-compliance/hooks/posttooluse_gate.py:119-124, and each is passed to apply_registry (cli_check_diff.py:82, posttooluse_gate.py:125). cli_check_llm.py:54-66 calls run_judge and never calls apply_registry. The test_enforcement.py stubs are tests, not consumers. No skill snippet builds a LineLookup.

#### C35 — SURVIVED
- evidence: `tests/test_self_host.py:37-42`
- reasoning: Grepped for KNOWN_DETECTORS, *_DETECTOR_IDS and .detector across code, skills and tests. The only check of ast/guard detector strings is registry.py:56-63. tests/test_self_host.py:37-42 checks detector strings only for detection == 'manual' rows. The acf-mandate snippet (plugins/arch-compliance/skills/acf-mandate/SKILL.md:95) and test_profile_drift.py:24 delegate to load_mandates. acf-setup's smoke check (plugins/arch-compliance/skills/acf-setup/SKILL.md:217-224) delegates to the CLI. architecture-review/SKILL.md uses detector only as the auditor name (:108). None of them would independently reject a '<path.py>:<callable>' string.

#### C36 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:104`
- reasoning: Re-ran the caller sweep by behaviour (grep load_mandates excluding docs). It matches the appendix: inject_constraints.py:104, cli_check_llm.py:54 and skills/architecture-review/SKILL.md:62 pass no known_detectors, so they cannot reach the repo_root/AcfInputError branch. test_profile_drift.py:24 passes known_detectors, but both profiles use only built-in ids (plugins/arch-compliance/profiles/python-service/mandates.yml:5-95). test_registry.py:30 uses an inline built-in-style fixture. Caveat: the new unconditional syntax check reaches these callers too. inject_constraints.py:105 catches only AcfInputError, and UnknownDetectorError is a sibling under AcfError (plugins/arch-compliance/python/acf/exceptions.py:13), not a subclass. So a malformed host ref now escapes the SubagentStart hook as a traceback. Filed as an unanchored finding.

#### C37 — SURVIVED
- evidence: `config/architecture/mandates.yml:135-140`
- reasoning: Grepped every *.yml for detection/detector/status, and every *.py for 'partial'. The only partial rows are detection: llm: config/architecture/mandates.yml:135-140 (llm_fail_loud), plugins/arch-compliance/profiles/python-service/mandates.yml:94-99 and plugins/arch-compliance/profiles/react-app/mandates.yml:39-44. tests/fixtures/mandates_valid.yml has only enforced built-in rows. The one Python 'partial' (plugins/arch-compliance/tests/test_enforcement.py:65) builds a registry directly and never calls load_mandates. No partial ast/guard row exists to break.

#### C38 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99`
- reasoning: The cited line filters on detector and status only (m.detector == detector and m.status != 'unenforced'), not on call_sites. The hook does the same (plugins/arch-compliance/hooks/posttooluse_gate.py:229-236, 284-286). Grepping call_sites across python/ and hooks/ finds no gate that reads the field. The Mandate model accepts any string (plugins/arch-compliance/python/acf/registry.py:21, call_sites: list[str]), so there is no accepted vocabulary to match. Values in use are ci, hook and audit (config/architecture/mandates.yml:11,47,154), and the design doc lists precommit, ci, posttooluse and audit (docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:104). The premise that the routing matches what the existing gates filter on is false: the design creates call-site routing, and only for host rows.

#### C39 — REFUTED
- evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:116`
- reasoning: Grepped *.md for 'known detector', 'detector id', 'detector union', 'registered under' and '.py / .ts / .tsx'. The spec's update list for acf-mandate SKILL.md is lines 41, 55, 58, 68, 88-112, 120, 122 and 138. It omits :116 ('a mandate whose detector is not in the known union'), :74 ('detector known-set') and :10. Also not updated: docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:111 (the drift test against 'registered detector ids'), config/architecture/ARCHITECTURE.md:226-228 (names KNOWN_DETECTORS as the package check to consume), README.md:62 and README.md:106, plugins/arch-compliance/skills/acf-setup/SKILL.md:159, and the posttooluse_gate.py:12 docstring. The README, acf-setup and docstring lines all say Tier-1 runs on .py/.ts/.tsx only, but host guards receive every changed path.

### Unanchored findings

- **important**: Call-site routing applies only to host rows: a built-in row with call_sites [ci] (no-shims.hasattr) still runs in the PostToolUse hook via scan_python_file, while an identical host row would be skipped, so one registry field gets two meanings and the spec's claim that the gates already filter on these values is false.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99`
- **important**: The new unconditional host-ref syntax check in load_mandates raises UnknownDetectorError for every caller, but inject_constraints.py catches only AcfInputError (a sibling under AcfError), so a malformed host ref crashes the SubagentStart hook with a traceback; the spec gives that caller no disposition.
  - evidence: `plugins/arch-compliance/hooks/inject_constraints.py:103-107`
- **important**: The prescribed acf-mandate Validate snippet change says to get repo via 'repo = resolve_repo()', but resolve_repo's first parameter 'explicit' has no default, so the snippet as specified raises TypeError.
  - evidence: `plugins/arch-compliance/python/acf/repo.py:32`
- **advisory**: Path-shape and containment decisions get a second, divergent implementation: validate_posix_rel_path re-spells acf.adr.citations' _looks_absolute and _escapes_repo with different answers (e.g. 'C:a/b.py'), and the design adds two more is_relative_to containment checks (load_host_detector, make_line_lookup) instead of one engine helper.
  - evidence: `plugins/arch-compliance/python/acf/adr/citations.py:49-51`

### Looked for but did not find

- existing loader of registry-supplied Python code: importlib, spec_from_file_location, import_module, exec_module, runpy, exec( (hits only in tests)
- third LineLookup implementation: line_lookup, LineLookup, apply_registry callers (only cli_check_diff.py:76 and posttooluse_gate.py:119)
- second ast/guard detector validator: KNOWN_DETECTORS, _DETECTOR_IDS, .detector in skills/tests (test_self_host checks manual rows only)
- partial ast/guard rows in yml registries/profiles/fixtures: grep of 'status:' / 'detection:' across *.yml and 'partial' across *.py
- any gate filtering on call_sites: grep call_sites in python/ and hooks/ (none; only registry.py:21 declares the field)
- prior on-record rejection of a '<path>:<callable>' host detector design: grep 'host detector', 'extension point', 'callable_name', 'dotted' in docs/design and docs/plans (none; PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:97 only says phase 2 is blocked on the extension point)

### Relationships

- PARTIAL_OVERLAP: `validate_posix_rel_path (acf.engine)` — responsibility `decide whether a path string is absolute/drive-rooted or escapes the repo root` — existing `plugins/arch-compliance/python/acf/adr/citations.py:49-51`
  - resolution: Responsibility R is 'classify a path's relative/absolute/escaping shape'. Put one stdlib-only predicate in acf.engine (e.g. posix_rel_path_problem(value) -> str | None). validate_posix_rel_path raises on a non-None result, and citations._looks_absolute / _escapes_repo branch on it. The two containment checks the spec adds (load_host_detector is_relative_to, make_line_lookup is_relative_to) collapse into one acf.engine resolve_under_root(root, rel) helper.
- PARTIAL_OVERLAP: `acf.detectors.host._normalize_findings` — responsibility `validate external detector output and convert it into Finding rows, raising DetectorPackError` — existing `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:75-95`
  - resolution: Responsibility R is 'coerce untrusted detector output into Finding, failing loud'. Both should use one shared coercion helper in acf.finding with a single path policy: the bridge silently normalizes backslashes with posix_path, while the host path refuses them. Each keeps only its private part (JSON decoding for the bridge, mandate_id/detector/detection stamping for host rows).
- PARTIAL_OVERLAP: `scan_host_ast_file / scan_host_guards mandate filters` — responsibility `select active mandates (status != 'unenforced') for a detector or detection` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:94-99`
  - resolution: Responsibility R is 'which registry rows are live for this scan'. Add one MandateRegistry.active(detector=None, detection=None, call_sites=None) method in acf.registry. cli_check_diff._active_mandates, the inline filters in posttooluse_gate.py:229-236 and :284-286, and the two new host.py list comprehensions all become calls to it, which also gives built-in and host rows the same call_sites semantics.
- PARTIAL_OVERLAP: `host ast/guard wiring in _scan_changed and _scan_paths` — responsibility `per-file Tier-1 dispatch over built-in and host detectors` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:213-295`
  - resolution: Responsibility R is 'run every active Tier-1 detector on a file set'. _scan_changed (cli_check_diff.py:102-184) and _scan_paths are already parallel copies, and the spec adds the same three host calls to both. Extracting one acf.tier1.scan_files(repo, files, added_lines_fn, registry, allowed_call_sites) leaves each gate with only path collection and the diff/hook scope difference.
- PARTIAL_OVERLAP: `scan_host_ast_file single ast.parse` — responsibility `parse a .py file into an AST for Tier-1 scanning` — existing `plugins/arch-compliance/python/acf/detectors/python_pack.py:35`
  - resolution: Responsibility R is 'parse once per file'. Parse in the shared dispatcher and pass tree= to scan_python_file, scan_facade_sinks (facade_sinks.py:51) and scan_fsm_writes (fsm_guard.py:37) as well as to host detectors. Otherwise the 'one parse per file' claim covers only host detectors.
- PARTIAL_OVERLAP: `make_line_lookup on-demand read` — responsibility `read a repo file's lines into file_lines` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:125-126`
  - resolution: Responsibility R is 'load file lines for exemption lookup'. The gates read strict utf-8 (cli_check_diff.py:125,152; posttooluse_gate.py:251), while make_line_lookup reads with errors='replace'. Have the gates populate through the same reader, or state why the decoding policies differ.
- ADJACENT: `load_host_detector sys.path insertion` — responsibility `make a directory importable by mutating sys.path` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:22-26`
  - resolution: Keep separate.
  - non-merge: The hook inserts the plugin's own python/ root at script start-up so it can import acf. The loader inserts the host repo root so host modules can import siblings. They put different roots on the path at different lifecycle points, and neither can serve the other.
- SUBSUMED: `load_mandates host validation branch` — responsibility `validate ast/guard detector references at registry load` — existing `plugins/arch-compliance/python/acf/registry.py:56-63`
  - resolution: Extend in place, as the spec does. The built-in membership check becomes one branch of the generalized active-row check, and no sibling validator is added.
- IDENTICAL: `make_line_lookup (acf.enforcement)` — responsibility `map (posix, line) to source text for exemption matching` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:119-124`
  - resolution: Delete both closures (here and cli_check_diff.py:76-81) and have both gates consume make_line_lookup, as the spec states.

### Two-owner counts

- decide whether a path string is absolute or drive-rooted: 2
- refuse a path that escapes the repo root: 4
- select active mandates (status != unenforced) for a scan: 8
- coerce external detector output into Finding with DetectorPackError: 2
- parse a .py file to AST during a Tier-1 scan: 5
- read file lines into the file_lines cache: 4
- per-file Tier-1 dispatch over the registry: 2
- insert a directory into sys.path: 2

### Document conflicts

- `plugins/arch-compliance/skills/acf-mandate/SKILL.md:116` (contradicts): When the user adds or promotes a mandate whose `detector` is **not** in the known union
- `plugins/arch-compliance/skills/acf-mandate/SKILL.md:58` (contradicts): Prefer `partial` or `unenforced` when the detector/prompt does not exist yet.
- `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:184` (contradicts): Unknown detector id referenced by an enforced `ast` or `guard` row → drift/registry validation fail.
- `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:111` (restates): A **drift test** fails when example/profile prose anchors, registry rows, and registered detector ids disagree.
- `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:125` (restates): TypeScript/React pack (equal peer): ... Extension points for project-specific detectors.
- `config/architecture/ARCHITECTURE.md:226` (restates): A check re-implemented in a test or a skill instead of consumed from the package (`acf.registry.load_mandates`, `acf.registry.missing_anchors`, `acf.cli_check_diff.KNOWN_DETECTORS`, the `acf.repo` constants).

## hardening

### Claim verdicts

#### C40 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:168-182, plugins/arch-compliance/hooks/posttooluse_gate.py:107`
- reasoning: The justification says a syntax-only check would 'let the row go inert'. That is false against the spec's own runners. scan_host_guards (spec 4.2 item 6) runs every active guard row in its call-site set on every invocation, in the repo-level slot after scan_ratchet (cli_check_diff.py:168-182). It calls load_host_detector outside the try, so a missing or broken module raises UnknownDetectorError at dispatch anyway. scan_host_ast_file does the same whenever a matching file changes. The spec gives no written rejection of dispatch-time validation; 'alternatives rejected' appears nowhere. The cost is also unstated: load_mandates imports every active host row whatever its call_sites, so the PostToolUse hook (fresh process per edit, load at posttooluse_gate.py:107) imports and runs the top-level code of CI-only guard modules on every edit. That contradicts spec 2.3's stated goal of 'without slowing down every file edit in PostToolUse'.

#### C41 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/registry.py:11, plugins/arch-compliance/python/acf/registry.py:20`
- reasoning: TIER1 = DIFF | HOOK, so a non-empty intersection does guarantee some runner's call-site filter admits the row. It is not sufficient. Language = Literal['python','typescript','both','none'] (registry.py:11), and Mandate.languages is required (registry.py:20). scan_host_ast_file filters on m.languages in {language, 'both'} (spec 4.2 item 5). So an active host ast row with languages: none and call_sites: [ci] passes load_mandates, including the module import, and is run by neither _scan_changed nor _scan_paths. That is exactly the inert active BLOCK row the check exists to prevent. load_mandates does not check languages for host ast rows.

#### C42 — REFUTED
- evidence: `hm:scripts/ci/metadata_facade_guard.py:66, plugins/arch-compliance/hooks/posttooluse_gate.py:107`
- reasoning: Need 1 (import once per run when detectors share a file) is real, because scan_host_ast_file calls load_host_detector per file per mandate. Need 2 (no collision between tmp_path repos) is not delivered by the key. Collision happens outside the cache: sys.modules[module_name] (module_name undefined) and package entries such as 'scripts' get cached from the first root. HM guards import scripts.ci.arch_compliance.* (metadata_facade_guard.py:66), so a second root's module resolves the first root's packages. Need 3 (invalidate on edit) has no producer. CLI and hook are one process per invocation (posttooluse_gate.py:107 runs load_mandates fresh each time), and the spec's tests use distinct tmp_path roots. Even if it fired, only the top module would re-execute; its stale intra-repo imports stay in sys.modules.

#### C43 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:46, plugins/arch-compliance/python/acf/finding.py:12`
- reasoning: apply_registry looks up by_id.get(finding.mandate_id) and drops findings with no row (enforcement.py:46-48). The host callable signatures (scan_ast/scan_guard) receive no mandate id, yet Finding.mandate_id is required (finding.py:12). Under this contract the host must fabricate a value, so the runner must overwrite it. The claim holds as a necessity under the chosen contract. The contract itself is the hardening gap; see the mechanism trace and unanchored finding.

#### C44 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/finding.py:11-19, pyproject.toml:7`
- reasoning: Finding(BaseModel) declares mandate_id, severity, path: str, line: int, message, detector, confidence, detection (default 'ast'). It has no validators, so a backslash path and line <= 0 both construct and the _normalize_findings checks are live. pydantic>=2.0 (pyproject.toml:7) provides model_copy(update=...), already used at enforcement.py:52 and cli_check_diff.py:154.

#### C45 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:18-26, plugins/arch-compliance/python/acf/registry.py:11`
- reasoning: Mandate declares detection (Literal), detector: str, languages: Language, call_sites: list[str], status, and params: dict[str, Any] | None = None (registry.py:18-26). The Language literal is python/typescript/both/none (:11). It also includes 'none', which the runners never match (see C41).

#### C46 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/enforcement.py:23, plugins/arch-compliance/python/acf/enforcement.py:49-50`
- reasoning: LineLookup = Callable[[str, int], str] at :23. apply_registry(findings, registry, line_lookup: LineLookup) at :37-41 calls line_lookup(finding.path, finding.line) at :49 and token_exempted at :50.

#### C47 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:121-150, plugins/arch-compliance/python/acf/cli_check_diff.py:110, plugins/arch-compliance/python/acf/cli_check_diff.py:152`
- reasoning: _scan_changed(repo, mode, base, registry) has repo and registry in scope. changed is bound at :110 and still in scope after scan_ratchet (:182). In the .py branch, lines (frozenset of added lines, :121), posix (:122) and text (:125) are bound before scan_fsm_writes (:140-150). The .ts branch reads text inline without binding it (:152), as the claim states.

#### C48 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:251-252, plugins/arch-compliance/hooks/posttooluse_gate.py:279-282, plugins/arch-compliance/hooks/posttooluse_gate.py:284-294`
- reasoning: _scan_paths(repo, paths, registry) at :213-214. rel_paths is declared at :227 and appended at :246 for every file, code or not. rel is bound at :243-245 and text at :251, before both the .py branch (fsm ends :277) and the TS branch (:279-282). The build-artifact loop at :284-294 uses rel_paths. Side note: rel falls back to an absolute path for files outside repo (:244-245), and that would reach host callables.

#### C49 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:72-81, plugins/arch-compliance/hooks/posttooluse_gate.py:91-107`
- reasoning: The enabled check returns 0 at :72-81, before the third-party acf imports (:91-95) and before load_mandates (:107). Under the spec, load_mandates is the first point that imports host modules, so the hook seam holds. The parenthetical is confirmed: acf-check-diff has no ENABLED_REL check (only repo.py:29 defines it; cli_check_diff.py:63-71 loads directly). Filed as an unanchored finding.

#### C50 — REFUTED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:113-117, plugins/arch-compliance/python/acf/cli_check_diff.py:69-74`
- reasoning: cli_check_diff.py:69-74 wraps both load_mandates and _scan_changed and catches GitError, AcfInputError, UnknownDetectorError and DetectorPackError. In the hook, the scan try at :113-117 catches only DetectorPackError. The spec's runners do 'except AcfError: raise' (spec 4.2 items 5/6) and call load_host_detector outside the try. So a host callable raising any AcfError subclass (AcfInputError, UnknownDetectorError, BaselineError...), or a scan-time UnknownDetectorError, escapes _scan_paths unhandled as a traceback. In cli_check_diff, AcfError subclasses outside its four-tuple escape too. The failures stay loud via traceback but do not reach 'an existing fail-loud handler'.

#### C51 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:6-7, plugins/arch-compliance/python/acf/detectors/__init__.py:5-9, plugins/arch-compliance/tests/test_adr_import_graph.py:70-76`
- reasoning: acf.registry imports only exceptions and loader at module scope (:6-7), and the host import is lazy inside load_mandates, so host.py importing acf.registry at top level creates no cycle. acf.detectors/__init__ (:5-9) and every detector module import only engine, finding and exceptions, never registry or enforcement. The cli_check_diff module-scope imports (judge imports registry, finding, template) do not reach acf.adr. test_adr_import_graph only forbids the literal 'acf.adr' in hook source (:74-76) and 'scripts' imports inside acf/adr (:54-67), and the proposed imports violate neither.

#### C52 — REFUTED
- evidence: `hm:scripts/ci/metadata_facade_guard.py:66, C:/Users/iball/Arduino/Projects/HistoricMansions/scripts/__init__.py:1`
- reasoning: module_name is never defined in the spec, so isolation of the sys.modules registration is unspecified. If it derives from rel_path, two roots with the same rel_path overwrite each other's sys.modules entry. Independently, the spec puts str(root) at the front of sys.path permanently, once per root. Host modules' intra-repo imports resolve through sys.modules first. HM guards do 'from scripts.ci.arch_compliance.facade_sinks import ...' (metadata_facade_guard.py:66), and HM has scripts/__init__.py. Once one root's 'scripts' package is cached, a second root's module silently binds the first root's helpers. The 'never collide' claim fails, and nothing refuses.

### Unanchored findings

- **important**: The spec documents .acf/enabled as the trust opt-in for executing host detectors in acf-check-diff (sections 2.5 and 4.6 item 3), but acf-check-diff has no enabled check. .acf/ is gitignored, so CI can never carry the marker. As written, the doctrine and acf-setup prose would state a false boundary, and adding the check would silently disable CI.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:63-71, .gitignore:8, .github/workflows/ci.yml:40`
- **important**: load_mandates imports every active host module regardless of call_sites. The PostToolUse hook, a fresh process per edit, would therefore import and run the top-level code of CI-only guard modules on every file edit. That defeats the stated purpose of DIFF/HOOK call-site routing and runs CI-only host code at edit time.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:107`
- **important**: The Tier-1 call-site check does not prevent inert active rows: a host ast row with languages: none passes load_mandates (import included) and is matched by neither scan_host_ast_file language filter.
  - evidence: `plugins/arch-compliance/python/acf/registry.py:11`
- **important**: load_host_detector leaves module_name undefined and permanently prepends each repo root to sys.path. Host modules' intra-repo package imports (e.g. 'scripts.*') are cached by the first root, so a second root binds the wrong helpers. The 'separate tmp_path repositories never collide' guarantee does not hold.
  - evidence: `hm:scripts/ci/metadata_facade_guard.py:66`
- **important**: _normalize_findings silently overwrites mandate_id, detector and detection, and apply_registry overwrites severity. This is needed only because the host contract returns a full Finding whose required fields (mandate_id, severity) the host cannot know. A rung-1 contract would make the mis-attribution state unrepresentable: the callable returns only (path, line, message), with path runner-set for ast detectors, and the runner constructs Finding. The spec never considers it.
  - evidence: `plugins/arch-compliance/python/acf/finding.py:12-13`
- **advisory**: Host-callable AcfError subclasses are re-raised unwrapped, but the hook's scan handler catches only DetectorPackError, so they surface as an unhandled traceback rather than the gate's fail-loud message.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:113-117`
- **advisory**: The mtime_ns/size components of the module cache key handle a detector file changing within one process, which no production or planned test path produces. Keying on the resolved module path alone covers the real needs.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:107`
- **advisory**: make_line_lookup swallows OSError into an empty line list and decodes with errors='replace'. A read failure silently disables exemption matching instead of failing loud.
  - evidence: `plugins/arch-compliance/python/acf/enforcement.py:49`

### Looked for but did not find

- Any .acf/enabled (ENABLED_REL) check in acf-check-diff or any acf runtime module besides acf.repo's definition (repo.py:29); none found
- Any other load_mandates caller passing known_detectors without repo_root that would break on host rows: cli_check_llm.py:54, inject_constraints.py:104 and architecture-review SKILL.md:62 pass neither (syntax-only check, no import); test_profile_drift.py:24 passes known_detectors over plugin profiles, which carry no host refs
- A second Mandate construction path that would bypass the load_mandates syntax check in production: only load_model_file inside load_mandates (registry.py:53)
- An import cycle from the lazy acf.detectors.host import or the hook importing acf.cli_check_diff; none (detector modules import only engine, finding and exceptions)
- Validators on Finding that would make _normalize_findings' backslash/line checks dead: none (finding.py:11-19)
- A producer of within-process detector-file edits for the cache invalidation: none in the CLI, the hook, or the spec's test plan

### Mechanism traces

- **parse_host_detector_ref / validate_posix_rel_path syntax check in load_mandates**
  - invalid state: a Mandate with detection in {ast, guard} whose detector contains ':' and whose path part is not a normalized relative POSIX '.py' path, or whose callable part is not an identifier
  - producer: `hm:config/architecture/mandates.yml:97`
  - rung 3 (highest applicable 1); repairs=False
  - hardening rejected because: Because acf.engine is stdlib-only and parse_host_detector_ref calls validate_posix_rel_path directly, adding an unused PosixRelPath alias in Spec 2a would violate ## Live consumers
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:457`
- **load_host_detector import at load_mandates time**
  - invalid state: an active ast/guard row whose host detector file is absent, fails to import, or lacks a callable attribute
  - producer: `hm:config/architecture/mandates.yml:97`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:464`
- **TIER1_CALL_SITES requirement in load_mandates**
  - invalid state: an active host ast/guard row with set(call_sites) & {ci, precommit, hook, posttooluse} == empty (but not the languages == 'none' case, which it misses)
  - producer: `plugins/arch-compliance/python/acf/registry.py:21`
  - rung 3 (highest applicable 1); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:463`
- **_MODULE_CACHE keyed by (root, rel_path, st_mtime_ns, st_size)**
  - invalid state: a cached host module whose source file's mtime or size changed on disk since it was imported within the same process
  - producer: `None`
  - rung 5 (highest applicable 2); repairs=True
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:574`
- **_normalize_findings overwrite of mandate_id/detector/detection**
  - invalid state: a Finding returned by a host callable for mandate m with f.mandate_id != m.id or f.detector != m.detector or f.detection != m.detection
  - producer: `plugins/arch-compliance/python/acf/finding.py:12`
  - rung 5 (highest applicable 1); repairs=True
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:590`
- **_normalize_findings refusals (non-iterable, non-Finding item, backslash or blank path, line < 1)**
  - invalid state: host return value not an iterable of Finding, or an item with '\\' in path, path.strip() == '', or line < 1
  - producer: `plugins/arch-compliance/python/acf/finding.py:14-15`
  - rung 3 (highest applicable 1); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:584-589`
- **DetectorPackError wrapping of host callable exceptions**
  - invalid state: a host callable raises a non-AcfError exception during scan
  - producer: `hm:scripts/ci/metadata_facade_guard.py:66`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:610`
- **scan_host_ast_file returns [] on SyntaxError**
  - invalid state: a changed .py file whose text does not ast.parse
  - producer: `plugins/arch-compliance/python/acf/cli_check_diff.py:125`
  - rung 5 (highest applicable 3); repairs=True
  - hardening rejected because: matching scan_python_file at plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37, scan_facade_sinks ... and scan_fsm_writes
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:606`
- **make_line_lookup on-demand repo file read**
  - invalid state: a finding whose path is not a key of file_lines, so lookup returns '' and exemption_tokens are never honored for it
  - producer: `plugins/arch-compliance/python/acf/cli_check_diff.py:158-166`
  - rung 2 (highest applicable 2); repairs=True
  - spec citation: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:685-706`

## Claims

- **C1** [premise] [load-bearing]: Today load_mandates(path, *, known_detectors=None) raises UnknownDetectorError only when m.status == "enforced", m.detection is in {"ast","guard"}, and m.detector is not in known_detectors; rows with status "partial" are not checked. (The design extends the check to every status other than "unenforced".)
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:60-63`
- **C2** [premise] [load-bearing]: KNOWN_DETECTORS is a closed union ALL_PYTHON_DETECTOR_IDS | TS_DETECTOR_IDS | LLM_PROMPT_IDS of built-in ids, so a host repository cannot name any detector of its own in an active ast/guard row and still load its registry with known_detectors=KNOWN_DETECTORS.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:25`
- **C3** [premise]: KNOWN_DETECTORS contains exactly 11 built-in ids. (Precision fact: the count changes no mechanism.)
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:25`
- **C4** [premise] [load-bearing]: Both _scan_changed in cli_check_diff.py (:102-184) and _scan_paths in hooks/posttooluse_gate.py (:213-295) call only hardcoded built-in scanners (scan_python_file, scan_facade_sinks, scan_fsm_writes, scan_typescript_file, scan_build_artifact_paths, and scan_ratchet in cli_check_diff.py); neither has any path that dispatches a detector by a registry-supplied reference, so accepting a host path in load_mandates alone would leave an active BLOCK row validated but never executed.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:102-184`
- **C5** [root_cause] [load-bearing]: Root cause of the hook defect: hooks/posttooluse_gate.py:107 calls load_mandates(mandates_path) without known_detectors, so the unknown-detector check never runs in the PostToolUse hook, and an active mandate whose detector id names nothing silently produces zero findings at edit time instead of failing loud.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:107`
- **C6** [premise] [load-bearing]: hooks/posttooluse_gate.py catches only AcfInputError around load_mandates (line 108), and UnknownDetectorError is not a subclass of AcfInputError, so once known_detectors is passed the hook must also catch UnknownDetectorError explicitly or it would crash rather than report. (If UnknownDetectorError subclassed AcfInputError the added catch would be unnecessary.)
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:108`
- **C7** [root_cause] [load-bearing]: The _line_lookup closures in cli_check_diff.py:76-81 and hooks/posttooluse_gate.py:119-124 consult only the pre-populated file_lines dict of changed .py/.ts/.tsx files, so for a finding on any file not in that dict they return "" and apply_registry (enforcement.py:49-51) cannot honor an inline exemption token on that line. This is why a guard detector's findings on unchanged or non-code files would ignore exemptions.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-81`
- **C8** [premise] [load-bearing]: Both status "enforced" and status "partial" mandates are active in Tier 1 today: apply_registry and the cli_check_diff mandate filter treat partial rows as live (enforcement.py:47, cli_check_diff.py:98) and the acf-mandate skill documents this (plugins/arch-compliance/skills/acf-mandate/SKILL.md:57).
  - spec citation: `plugins/arch-compliance/python/acf/enforcement.py:47`
- **C9** [premise] [load-bearing]: The only existing POSIX-path validator, PosixStr (acf/adr/contract.py:129, via _reject_backslash at :98-101), rejects only backslashes and lives in acf.adr, and hooks/posttooluse_gate.py is forbidden by plugins/arch-compliance/tests/test_adr_import_graph.py:70-76 from referencing acf.adr; so a relative-path validator usable by the hook cannot be PosixStr.
  - spec citation: `plugins/arch-compliance/python/acf/adr/contract.py:129`
- **C10** [premise]: acf/engine.py is 31 lines, stdlib-only, and defines only posix_path (:11-14), contains_backslash (:17-25) and is_in_scope (:27-31).
  - spec citation: `plugins/arch-compliance/python/acf/engine.py:1-31`
- **C11** [premise]: The origin host's mandates.yml (hm:config/architecture/mandates.yml at b652fab05) has 17 enforced detection: ast rows matching the 17 keys of DETECTOR_REGISTRY at hm:scripts/ci/arch_compliance/engine.py:1154-1173, and 25 enforced detection: guard rows. (Precision fact: counts.)
  - spec citation: `hm:config/architecture/mandates.yml`
- **C12** [premise] [load-bearing]: Every enforced ast row in hm:config/architecture/mandates.yml declares call_sites [precommit, posttooluse, ci], and every enforced guard row declares call_sites drawn from [precommit, ci], [ci] or [precommit]; i.e. every motivating host row intersects TIER1_CALL_SITES = {ci, precommit, hook, posttooluse}, so the new Tier-1 call-site requirement and the DIFF/HOOK routing fit the motivating consumer.
  - spec citation: `hm:config/architecture/mandates.yml`
- **C13** [premise] [load-bearing]: Deferral: porting the origin host's 17 AST detectors and 25 guards onto <posix_rel_path.py>:<callable_name> belongs to a later HM cutover slice with no further plugin change. This presumes those detectors can be expressed as the proposed callables: an AST detector as scan_ast(text, path, added_lines, *, tree, params) returning Finding objects, and a guard (e.g. hm:scripts/ci/metadata_facade_guard.py, hm:scripts/ci/check_image_path_contract.py) as scan_guard(repo_root, changed_files, *, params). Verify against DETECTOR_REGISTRY's entries and at least the two named guard modules that the inputs they need are available through these signatures.
  - spec citation: `hm:scripts/ci/arch_compliance/engine.py:1154-1173`
- **C14** [premise]: Deferral: no acf.architecture_review runtime package and no architecture-review host configuration file exist in this repository today; both belong to a not-yet-written Spec 2b. (Downgraded from load-bearing: the design touches neither, so it is the same design whether or not they exist.) The spec cites no evidence.
  - spec citation: `None`
- **C15** [deletion] [load-bearing]: The design's only deletion is the two _line_lookup closures (cli_check_diff.py:76-81 and hooks/posttooluse_gate.py:119-124), which are behaviorally identical, so replacing both with one make_line_lookup preserves the current behavior of each caller for files already in file_lines.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:76-81`
- **C16** [premise]: scan_python_file (python_pack.py:34-37), scan_facade_sinks (facade_sinks.py:50-53) and scan_fsm_writes (fsm_guard.py:36-39) each return [] on SyntaxError, the convention scan_host_ast_file copies.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37`
- **C17** [premise]: The Appendix's list of load_mandates call sites (hooks/inject_constraints.py:104, hooks/posttooluse_gate.py:107, python/acf/cli_check_diff.py:70, python/acf/cli_check_llm.py:54, python/acf/registry.py:48, skills/acf-mandate/SKILL.md:95, skills/architecture-review/SKILL.md:62, tests/test_profile_drift.py:24, tests/test_registry.py:10,17,30,47,57, tests/test_self_host.py:23) is accurate at the reviewed commit. (Precision fact.)
  - spec citation: `None`
- **C18** [mandate] [load-bearing]: ## Fail loud: malformed host references, missing files, import errors and non-callable targets raise UnknownDetectorError; an active host row with no repo_root or no Tier-1 call site raises AcfInputError; exceptions or misshapen returns from a host callable raise DetectorPackError; and the hook now passes known_detectors and catches UnknownDetectorError. No path lets an active ast/guard row load without being executable.
  - spec citation: `config/architecture/ARCHITECTURE.md:24-41`
- **C19** [mandate] [load-bearing]: ## Declared, never defaulted: load_mandates requires an explicit repo_root for an active host detector row and raises AcfInputError rather than deriving one (e.g. path.parents[2]), consistent with custom --mandates paths.
  - spec citation: `config/architecture/ARCHITECTURE.md:118-133`
- **C20** [mandate]: ## No shims: the loader uses getattr(mod, attr_name, None) plus callable() rather than hasattr, and no host-detector failure has a silent fallback.
  - spec citation: `config/architecture/ARCHITECTURE.md:43-53`
- **C21** [mandate]: ## POSIX paths: validate_posix_rel_path refuses backslashes via contains_backslash, and _normalize_findings refuses any Finding whose path contains a backslash.
  - spec citation: `config/architecture/ARCHITECTURE.md:55-64`
- **C22** [mandate]: ## One base exception: the design adds no exception class and reuses AcfInputError, UnknownDetectorError and DetectorPackError (acf/exceptions.py:5-30), all subclassing AcfError alone.
  - spec citation: `config/architecture/ARCHITECTURE.md:99-103`
- **C23** [mandate]: ## One owner for host paths: neither acf/engine.py nor the new acf/detectors/host.py spells config/architecture, and the acf-mandate skill keeps importing ARCH_REL, MANDATES_REL and resolve_repo from acf.repo.
  - spec citation: `config/architecture/ARCHITECTURE.md:105-116`
- **C24** [mandate]: ## Prose names no host: runtime messages and the acf-mandate and acf-setup skill prose this design adds name no origin host.
  - spec citation: `config/architecture/ARCHITECTURE.md:135-143`
- **C25** [mandate]: ## Live consumers: every function and constant the design adds has a live runtime call site (validate_posix_rel_path by parse_host_detector_ref; the three call-site constants, the predicate, parser, loader and both runners by load_mandates, cli_check_diff.py and hooks/posttooluse_gate.py; make_line_lookup by both gates), and the PosixRelPath alias is withheld precisely because it would have none.
  - spec citation: `config/architecture/ARCHITECTURE.md:153-157`
- **C26** [mandate]: ## Declared text decoding: every read_text the design adds or touches declares encoding="utf-8", and the errors="replace" used in make_line_lookup is permitted by that rule.
  - spec citation: `config/architecture/ARCHITECTURE.md:171-182`
- **C27** [mandate]: ## Release discipline: because shipped skill prose changes (acf-mandate, acf-setup), the version is bumped 0.2.2 to 0.2.3 in both pyproject.toml:3 and plugins/arch-compliance/.claude-plugin/plugin.json:3, which is everything that rule requires.
  - spec citation: `config/architecture/ARCHITECTURE.md:184-194`
- **C28** [mandate]: ## Single point of definition: acf.detectors.host is the single owner of host detector parsing, loading and execution for load_mandates and both gates, and make_line_lookup is the single line-lookup definition.
  - spec citation: `config/architecture/ARCHITECTURE.md:196-209`
- **C29** [mandate]: ## No completeness claims: the spec's universally quantified statements (e.g. the Live consumers row's 'Every added function and constant has a live runtime call site', the Declared text decoding row's 'Every read_text call added or touched') are backed by an enumerated list as that rule requires.
  - spec citation: `config/architecture/ARCHITECTURE.md:159-169`
- **C30** [mandate]: ## Frozen ledger format and ## Scoped refactor (:211-215): the design changes no ledger model, and its refactors (consolidating _line_lookup; reading .ts text in _scan_changed) stay within the scope that rule allows.
  - spec citation: `config/architecture/ARCHITECTURE.md:145-151`
- **C31** [mandate]: The design complies with the five portable governing principles at docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51, and fulfils that spec's call for project-specific detector extension points (:102, :123, :125).
  - spec citation: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51`
- **C32** [shape_fit] [load-bearing]: validate_posix_rel_path is a new, non-duplicating validator: no existing function anywhere in plugins/arch-compliance/python/acf (outside acf.adr's backslash-only PosixStr) already validates a repo-relative POSIX path, so adding it creates no second way to do that.
  - spec citation: `plugins/arch-compliance/python/acf/engine.py:17-25`
- **C33** [shape_fit] [load-bearing]: acf/detectors/host.py partially duplicates no existing mechanism: nothing in the plugin today loads or executes code from a registry-supplied file path or dotted reference (e.g. no importlib/spec_from_file_location loader in acf.judge, acf.adr, profiles, or the TypeScript pack bridge) that host.py should extend instead.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/__init__.py:1-35`
- **C34** [shape_fit] [load-bearing]: make_line_lookup consolidates the only two line-lookup closures for apply_registry; no third LineLookup implementation exists (e.g. in cli_check_llm.py, the judge, or any skill snippet) that would remain a second definition.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:119-124`
- **C35** [shape_fit] [load-bearing]: Detector-reference validation lives only in load_mandates; no second validator (the acf-mandate skill's ## Validate snippet, the profile drift test, architecture-review, acf-setup) independently checks detector ids such that it would now reject or mis-handle a <posix_rel_path.py>:<callable_name> reference.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:56-63`
- **C36** [sweep] [load-bearing]: The design changes only four load_mandates callers (cli_check_diff.py, hooks/posttooluse_gate.py, tests/test_self_host.py, the acf-mandate skill snippet). Every other caller — hooks/inject_constraints.py:104, cli_check_llm.py:54, skills/architecture-review/SKILL.md:62, tests/test_profile_drift.py:24, tests/test_registry.py — either does not pass known_detectors or can never meet a host reference, so none needs repo_root or would start raising AcfInputError on a registry that uses host detectors. The spec gives no disposition for those callers.
  - spec citation: `None`
- **C37** [sweep] [load-bearing]: Extending the active-detector check from status enforced to status partial breaks no live registry: no partial ast/guard row in this repository's config/architecture/mandates.yml, the plugin's shipped profiles, or test fixtures names a detector outside KNOWN_DETECTORS. The spec offers no sweep for this.
  - spec citation: `None`
- **C38** [sweep] [load-bearing]: The call-site vocabulary {ci, precommit, hook, posttooluse} used for TIER1/DIFF/HOOK routing matches the call_sites values the Mandate model accepts and the values the existing gates filter on (cli_check_diff.py:98 and the posttooluse_gate equivalent); there is no other Tier-1 call-site value the routing omits.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:98`
- **C39** [sweep]: The prose updates listed (acf-mandate SKILL.md, acf-setup SKILL.md Step 7, config/architecture/ARCHITECTURE.md, docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:184) cover every shipped doc that states or implies detectors must be built-in ids or that names the detector forms; no other prose (README, docs/guides, other skills) would be left stating the old rule.
  - spec citation: `None`
- **C40** [mechanism_justification] [load-bearing]: Importing host modules at load_mandates time (not just at scan time) is justified: it is what makes an active BLOCK row with a missing or broken host detector fail at registry load, rather than an approach that only checks syntax and lets the row go inert. Alternatives (validate only at dispatch, or harden the registry author's workflow instead) are rejected for that reason.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:48-64`
- **C41** [mechanism_justification] [load-bearing]: The TIER1_CALL_SITES requirement in load_mandates is necessary and sufficient to prevent an active host ast/guard row that loads yet is run by neither acf-check-diff (DIFF_CALL_SITES) nor the PostToolUse hook (HOOK_CALL_SITES).
  - spec citation: `None`
- **C42** [mechanism_justification]: The module cache keyed by (root.as_posix(), rel_path, st_mtime_ns, st_size) is justified by three needs: one import per module per run when several detectors share a file, no collision between separate tmp_path repositories, and invalidation when a detector file is edited.
  - spec citation: `None`
- **C43** [mechanism_justification] [load-bearing]: _normalize_findings must overwrite mandate_id, detector and detection on every host Finding because apply_registry matches findings to mandate rows by mandate_id (enforcement.py:37-53); without the overwrite a host detector could attach findings to the wrong row or none.
  - spec citation: `plugins/arch-compliance/python/acf/enforcement.py:37-53`
- **C44** [implementability] [load-bearing]: Finding (finding.py:11-19) is a Pydantic model with fields path, line, mandate_id, detector and detection, supports model_copy(update=...), and does not itself already reject a backslash path or line < 1 (otherwise _normalize_findings' checks are dead code).
  - spec citation: `plugins/arch-compliance/python/acf/finding.py:11-19`
- **C45** [implementability] [load-bearing]: Mandate (registry.py:14-27) exposes every field the runners read: detection, detector, status, call_sites (a sequence), languages (with values python, typescript, both), and params (a dict, or None) passed to host callables as params=mandate.params.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:14-27`
- **C46** [implementability] [load-bearing]: enforcement.py defines a LineLookup type that make_line_lookup can return, and apply_registry(raw_findings, registry, lookup) takes it as its third argument, consulting it for exemption tokens at :49-51.
  - spec citation: `plugins/arch-compliance/python/acf/enforcement.py:49-51`
- **C47** [implementability] [load-bearing]: _scan_changed has the hook points the design names, with the needed names in scope: in the .py branch after scan_fsm_writes (~:150) — repo, text, posix, lines (added lines) and registry; in the .ts/.tsx branch (:151-156), where text is not read today; and after scan_ratchet (~:182), a changed-files sequence `changed`. registry is available inside _scan_changed.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:124-184`
- **C48** [implementability] [load-bearing]: _scan_paths in hooks/posttooluse_gate.py has the hook points the design names, with the needed names in scope: after scan_fsm_writes (~:277) and after scan_typescript_file (~:282) — repo, text, rel and registry; after scan_build_artifact_paths (~:294), a rel_paths sequence.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:213-295`
- **C49** [implementability] [load-bearing]: Trust-boundary seam: hooks/posttooluse_gate.py:72-81 exits 0 when .acf/enabled is absent before loading mandates.yml or importing anything a host module could reach, so no host code runs in the hook without the opt-in marker. (The spec states the same boundary applies to acf-check-diff, but cites no equivalent check there.)
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:72-81`
- **C50** [implementability] [load-bearing]: Both gates already catch DetectorPackError around the scan (cli_check_diff.py:72, hooks/posttooluse_gate.py:115) and exit 1, and cli_check_diff.main already catches UnknownDetectorError and AcfInputError from load_mandates at :70, so host-detector failures raised inside _scan_changed/_scan_paths or load_mandates reach an existing fail-loud handler.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:72`
- **C51** [implementability] [load-bearing]: The imports the design adds are cycle-free and allowed: acf.registry importing acf.detectors.host lazily inside load_mandates (host.py itself importing Finding, Mandate/MandateRegistry, engine and exceptions), and hooks/posttooluse_gate.py importing KNOWN_DETECTORS from acf.cli_check_diff, violate neither an import cycle nor the import-graph rules in plugins/arch-compliance/tests/test_adr_import_graph.py.
  - spec citation: `None`
- **C52** [implementability] [load-bearing]: load_host_detector as specified isolates distinct repository roots: the sys.modules name it registers (module_name, which the spec does not define) and the persistent sys.path insertion of each root do not let two repositories with the same rel_path, or a host module's intra-repo imports, collide or shadow each other — the spec's claim that separate tmp_path repositories 'never collide'.
  - spec citation: `None`
