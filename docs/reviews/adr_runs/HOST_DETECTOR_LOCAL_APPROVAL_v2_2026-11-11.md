# Adversarial design review — full detail

Spec: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md` @ `0af637490db28a6abbae86a2366857e87b404afb`
Kinds: defect
Outcome: **BLOCKED**
Claims: 55 · Reviewers: 4 · Converged: 3

## Blocking reasons

- load-bearing claim C12 (premise) is UNPROVEN: The window is real by construction: the proposed file_digests reads the bytes once, and load_host_detector reads the file again at exec time (host.py:78-83). The load-bearing part is the rationale ('a process that can rewrite the working tree during a gate run can already run code as the user'), and it does not follow from anything I can resolve. The spec's own threat model (section 2 Decision 5, section 3) puts an agent's actions under Claude Code tool permissions. An agent allowed Write/Edit but not Bash can rewrite the tree yet cannot directly run code; with parallel Edit calls (overlapping PostToolUse hook processes) it could time a detector-file rewrite between another hook's fingerprint check and its load. The justification holds partly in approved state when the detector imports a helper (helper edits already run unfingerprinted, C11), but fails for a detector that imports no repository module, so the accepted residual is not shown to add nothing beyond existing capability.
- load-bearing claim S4 (sweep) is REFUTED: The instance list is correct at 0da9864: host-row tests exist only in test_hooks.py, test_diff_cli.py, test_host_detectors.py and test_registry.py, and the last two call the runners/loader directly, never a gate; the seven listed tests match my reading. But the method is a name sweep: HOST_ROW (:15) matches the current helper names `_host_row(`, `_seed_host_rows(`, `_host_rows(`, `_host_repo(`, and its only shape pattern `detector:\s*[\w./-]+\.py:\w+` does not match how these tests actually build rows (test_hooks.py:379 writes `detector: hostdet/rules.py:{fn}`; `{` is not `\w`), so every test_hooks hit depends on the helper name. Pytest fixtures are never followed (a fixture is a parameter, not an ast.Call). Section 6.1 instructs the implementer to re-run this census before editing; a re-run would miss any test that seeds host rows through a new helper or fixture (including the helpers test_approval.py/test_cli_allow.py will add) or through a dict/f-string detector.
- load-bearing claim H5 (mechanism_justification) is SURVIVED but its evidence ('plugins/arch-compliance/python/acf/detectors/host.py:78') merely restates the spec's own citation ('plugins/arch-compliance/python/acf/detectors/host.py:78') — not independent verification, treated as UNPROVEN
- load-bearing claim H9 (implementability) is SURVIVED but its evidence ('plugins/arch-compliance/python/acf/repo.py:53-59') merely restates the spec's own citation ('plugins/arch-compliance/python/acf/repo.py:53-59') — not independent verification, treated as UNPROVEN
- load-bearing claim H13 (implementability) is SURVIVED but its evidence ('plugins/arch-compliance/python/acf/detectors/host.py:78-84') merely restates the spec's own citation ('plugins/arch-compliance/python/acf/detectors/host.py:78') — not independent verification, treated as UNPROVEN
- load-bearing claim H14 (implementability) is SURVIVED but its evidence ('plugins/arch-compliance/python/acf/cli_check_diff.py:83-100') merely restates the spec's own citation ('plugins/arch-compliance/python/acf/cli_check_diff.py:83-100') — not independent verification, treated as UNPROVEN
- load-bearing claim H16 (implementability) is REFUTED: The model shape fits (Literal[1] and a dict of entries validate via model_validate; ValidationError becomes AcfInputError at :74-77), but 'every bad-file case' is false. read_text catches only OSError (:59-62), so a non-UTF-8 store raises UnicodeDecodeError (a ValueError subclass); the parse step catches only YAMLError/JSONDecodeError (:63-66). Tested on 3.13: json.loads of a >4300-digit integer raises plain ValueError and deeply nested arrays raise RecursionError, neither caught. The result is a traceback in the diff gate and acf-allow, and an 'internal error' exit 2 in the hook, instead of the AcfInputError section 4.2 says is 'Every refusal'.
- implementability claim H10 is UNPROVEN: External claim about the Claude Code hooks reference, which I cannot read; live code emits only hookSpecificOutput.additionalContext (:138-147) and nothing in the repo evidences a top-level systemMessage being accepted alongside it. Not load-bearing: the notice still reaches the agent through additionalContext.
- implementability claim H16 is REFUTED: The model shape fits (Literal[1] and a dict of entries validate via model_validate; ValidationError becomes AcfInputError at :74-77), but 'every bad-file case' is false. read_text catches only OSError (:59-62), so a non-UTF-8 store raises UnicodeDecodeError (a ValueError subclass); the parse step catches only YAMLError/JSONDecodeError (:63-66). Tested on 3.13: json.loads of a >4300-digit integer raises plain ValueError and deeply nested arrays raise RecursionError, neither caught. The result is a traceback in the diff gate and acf-allow, and an 'internal error' exit 2 in the hook, instead of the AcfInputError section 4.2 says is 'Every refusal'.

## Absorptions

- PARTIAL_OVERLAP: 'MandateRegistry.host_rows' shares responsibility 'decide whether a row is a host ast/guard row' with plugins/arch-compliance/python/acf/registry.py:144 — Extract the predicate `m.detection in {"ast","guard"} and is_host_detector_ref(m.detector)` as a module-level `is_host_row(m)` in registry.py (or a Mandate property) consumed by host_rows, load_mandates' file-existence loop (:144, :150-154) and Mandate._row_shape (:72-76), so the predicate is stated once; host_rows keeps the call-site/detection filtering and load_mandates keeps its stat check.
- PARTIAL_OVERLAP: 'cli_allow.main registry load' shares responsibility "load the host registry with the gate's full validation arguments" with plugins/arch-compliance/python/acf/cli_check_diff.py:84-89 — `load_mandates(repo / MANDATES_REL, known_detectors=KNOWN_DETECTORS, llm_prompt_ids=LLM_PROMPT_IDS, repo_root=repo)` is repeated in cli_check_diff, the new cli_allow and (minus llm_prompt_ids) posttooluse_gate.py:110; a `load_gate_registry(repo, mandates_path=None)` helper would make all three gates validate a registry identically, so acf-allow cannot approve a registry the gates would refuse.
- mechanism 'Fingerprint canonicalisation (_canonical over model_dump)' sits at rung 2 when rung 1 applies, with no written justification

## Converged findings

- [2 reviewers: refuter, sweeper] approval_state's fingerprint operand is bound to registry.host_rows(call_sites) while acf-allow writes the TIER1 fingerprint, so the two gates and acf-allow compute different fingerprints and a registry with a [ci]-only host row is permanently STALE in the hook.
  - evidence: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:116`
  - evidence: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:112`
  - evidence: `plugins/arch-compliance/tests/test_hooks.py:445`
- [2 reviewers: compliance, hardening] _canonical maps a YAML date and the equal ISO string to the same canonical text, so switching a params value or key between the two forms does not lapse the approval.
  - evidence: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:114`
  - evidence: `plugins/arch-compliance/python/acf/registry.py:61`
- [2 reviewers: refuter, hardening] The fingerprint reads each detector file once and the loader reads it again; the accepted check-to-load residual is not justified for an Edit-permitted agent, and hashing and compiling one buffer would close it.
  - evidence: `plugins/arch-compliance/python/acf/detectors/host.py:78-83`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:74-83; plugins/arch-compliance/hooks/posttooluse_gate.py:109-117; plugins/arch-compliance/python/acf/cli_check_diff.py:83-97; plugins/arch-compliance/python/acf/cli_check_diff.py:166-182; plugins/arch-compliance/python/acf/cli_check_diff.py:204; plugins/arch-compliance/python/acf/registry.py:160-172`
- reasoning: Hook: the only gate before scanning is `enabled.is_file()` (:74-83); after that it loads mandates and calls `_scan_paths`, which calls scan_host_ast_file/scan_host_guards. cli_check_diff.main: loads mandates, empty-selection refusal, then _scan_changed which calls the host runners at :167-182 and :204 with no approval check. load_mandates only stats the host detector file (registry.py:160-172). A grep of plugins/arch-compliance/python and hooks for `approv`, `Path.home`, `expanduser`, `trusted` returns nothing, so no out-of-tree state is consulted.

#### C2 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/hooks.json:16-27; plugins/arch-compliance/hooks/posttooluse_gate.py:32-35`
- reasoning: hooks.json registers `python "${CLAUDE_PLUGIN_ROOT}/hooks/posttooluse_gate.py" --format hook` under PostToolUse with matcher `Write|Edit|MultiEdit`; it is plugin-level registration, and the hook's own comment states it fires on every Write/Edit in every repo once the plugin is installed. Caveat: 'every repository' assumes user-scope plugin enablement; a project-scoped enablement would narrow it, but the code side matches the claim.

#### C3 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:78-83; plugins/arch-compliance/python/acf/detectors/host.py:107-108; plugins/arch-compliance/python/acf/detectors/host.py:176-178; plugins/arch-compliance/hooks/posttooluse_gate.py:228`
- reasoning: load_host_detector builds a spec via spec_from_file_location (:78) and calls spec.loader.exec_module(mod) (:83); _call_host calls fn(*args, **kwargs) at :108; scan_host_ast_file calls load_host_detector then _call_host (:176-178). The hook imports these runners in-process (posttooluse_gate.py:228), so host code runs in the gate's own process.

#### C4 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:150; plugins/arch-compliance/skills/acf-setup/SKILL.md:148; config/architecture/ARCHITECTURE.md:175-176`
- reasoning: SKILL.md:150: 'Suggest adding `.acf/` to git if the team wants hooks enabled for everyone'; :148 frames `.acf/enabled` as the opt-in for hooks including host detectors; doctrine ARCHITECTURE.md:175-176 records that committing `.acf/` opts every clone in.

#### C5 — SURVIVED
- evidence: `git grep -n "importlib\|exec_module\|runpy" 8677e45^ -- plugins/arch-compliance/python plugins/arch-compliance/hooks (empty, rc=1); same pattern at HEAD matches plugins/arch-compliance/python/acf/detectors/host.py:12 and :83`
- reasoning: The pattern returns nothing at 8677e45^, and at HEAD the same pattern matches host.py:12/:78/:81/:83, so the alternation is valid. `git log --diff-filter=A -- .../host.py` prints 8677e45. At 8677e45^ the only process-spawning code is subprocess (diff.py, typescript_bridge.py, adr/citations.py), which runs git and the plugin's own Node pack, not a repository module.

#### C6 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:139-147; plugins/arch-compliance/hooks/posttooluse_gate.py:298-306; plugins/arch-compliance/hooks/posttooluse_gate.py:130-147`
- reasoning: HostHit.message becomes Finding.message (host.py:144); _format_findings embeds f.message in the text (:304); that text goes to stderr with exit 2 on BLOCK (:130-133) or into hookSpecificOutput.additionalContext otherwise (:137-147). That additionalContext/exit-2 stderr reach the agent's context is the external Claude Code behaviour the code relies on.

#### C7 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:85-91; plugins/arch-compliance/hooks/posttooluse_gate.py:99-107; plugins/arch-compliance/hooks/posttooluse_gate.py:111-113; plugins/arch-compliance/hooks/posttooluse_gate.py:118-120; plugins/arch-compliance/hooks/posttooluse_gate.py:249; plugins/arch-compliance/hooks/posttooluse_gate.py:309-310`
- reasoning: Each of the four branches prints to stderr and returns 1 regardless of out_format. The except tuples name only ImportError, (AcfInputError, UnknownDetectorError) and (AcfInputError, DetectorPackError, UnknownDetectorError); `abs_path.read_text(encoding="utf-8")` at :249 runs inside _scan_paths under the :116 try, and a UnicodeDecodeError matches none of them, so it propagates through `sys.exit(main())` (:310); an uncaught exception yields a traceback and exit 1.

#### C8 — UNPROVEN
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:130-133 (code half); external https://code.claude.com/docs/en/hooks not available`
- reasoning: The code half holds: the hook relies on exit 2 + stderr for BLOCK feedback (:131-133). The Claude Code semantics of exit 2 versus other non-zero codes rest on an external document I cannot open, so they cannot be re-derived here. Not load-bearing.

#### C9 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:31; plugins/arch-compliance/hooks/inject_constraints.py:91-92; plugins/arch-compliance/hooks/inject_constraints.py:104; plugins/arch-compliance/python/acf/registry.py:1-11; plugins/arch-compliance/python/acf/loader.py:11-18; plugins/arch-compliance/python/acf/engine.py:8-10`
- reasoning: A grep of inject_constraints.py for acf.detectors/scan_host/load_host_detector/KNOWN_DETECTORS returns nothing. Its acf imports are acf.repo, acf.exceptions, acf.registry, acf.loader, acf.template. Followed transitively: repo is stdlib; registry imports acf.engine, exceptions, loader, repo; loader imports json, yaml, pydantic, exceptions; engine imports ast, re, pathlib; template imports re, exceptions; acf/__init__.py is empty. No module on that path imports acf.detectors, importlib or exec_module. inject calls load_mandates(mandates_path) without known_detectors (:104), so the host-file stat branch is not even entered.

#### C10 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:221-230; plugins/arch-compliance/skills/acf-mandate/SKILL.md:136; README.md:57`
- reasoning: Step 9 (SKILL.md:221) instructs the agent to run `acf-check-diff --mode worktree --call-site precommit` (:226) from the host root; acf-mandate:136 reminds the user to re-run acf-check-diff; README.md:57 shows `acf-check-diff --mode staged --call-site precommit # local`. All three are hand invocations, not host CI/pre-commit configuration.

#### C11 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:58-60; plugins/arch-compliance/python/acf/detectors/host.py:78`
- reasoning: The first load appends the resolved repository root to sys.path (:58-60); only the named file goes through spec_from_file_location (:78), so any `import x` inside the detector resolves through the normal path finders, including __pycache__ bytecode. Per spec section 4.2, file_digests hashes only each row's named path, so a helper's bytes are outside the fingerprint, as claimed.

#### C12 — UNPROVEN
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:78-83`
- reasoning: The window is real by construction: the proposed file_digests reads the bytes once, and load_host_detector reads the file again at exec time (host.py:78-83). The load-bearing part is the rationale ('a process that can rewrite the working tree during a gate run can already run code as the user'), and it does not follow from anything I can resolve. The spec's own threat model (section 2 Decision 5, section 3) puts an agent's actions under Claude Code tool permissions. An agent allowed Write/Edit but not Bash can rewrite the tree yet cannot directly run code; with parallel Edit calls (overlapping PostToolUse hook processes) it could time a detector-file rewrite between another hook's fingerprint check and its load. The justification holds partly in approved state when the detector imports a helper (helper edits already run unfingerprinted, C11), but fails for a detector that imports no repository module, so the accepted residual is not shown to add nothing beyond existing capability.

#### C13 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:53-59; plugins/arch-compliance/python/acf/repo.py:50-51`
- reasoning: RepoTree.contained resolves the path against root (an absolute path is taken as is) and returns it whenever it is_relative_to(root); existence is not required. With root == home, `~/.acf/approvals.json` is always relative to root, so the proposed STORE_IN_REPO state is permanent for that repository, as claimed (the same holds for any repo rooted at an ancestor of home).

#### C14 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:40-47; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:52-58`
- reasoning: The cmd list includes `--file str(file_path)` (the edited file, :46), and subprocess.run is called with `shell=sys.platform == "win32"` (:58), so on Windows the list is passed to cmd.exe as one command line and the repository-controlled file name is shell-interpreted. The path is a separate input route from host rows, as stated.

#### C15 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:68-72; plugins/arch-compliance/hooks/posttooluse_gate.py:85-91`
- reasoning: out_format is assigned at :68-72, before the marker check at :74; the first exit-1 return is at :91 and the others at :107, :113, :120, all later in the same straight-line function body.

#### C16 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_hooks.py:145-155; plugins/arch-compliance/tests/test_hooks.py:318-329; plugins/arch-compliance/tests/test_hooks.py:424-437; plugins/arch-compliance/tests/test_hooks.py:23-37`
- reasoning: :424's test passes `--format text` explicitly (:435); :318's test passes input="" with no --format, so stdin JSON is None and the gate defaults to text; :145's test passes no --format and stdin=None (inherited by _run, :23-37), so absent a hook_event_name stdin payload it defaults to text - text mode in practice though not explicitly pinned. All three assert returncode 1.

#### C17 — SURVIVED
- evidence: `config/architecture/mandates.yml:152; plugins/arch-compliance/python/acf/registry.py:29-30; .github/workflows/ci.yml:40`
- reasoning: `grep -nE "^\s*detector:\s*\S*:" config/architecture/mandates.yml` returns nothing (rc=1), and so does the spec's own grep. is_host_detector_ref is `":" in detector` (registry.py:29-30); path-like detectors (e.g. :152) are `detection: manual` with no colon. So host_rows(ci) is empty, the proposed approval_state returns NOT_NEEDED, and ci.yml:40 (`python -m acf.cli_check_diff ... --call-site ci`) needs no flag.

#### C18 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:175-179; plugins/arch-compliance/skills/acf-setup/SKILL.md:148; plugins/arch-compliance/skills/acf-setup/SKILL.md:150; plugins/arch-compliance/python/acf/detectors/host.py:162-166`
- reasoning: The change surface (spec section 5) adds modules and modifies runtime code (host.py inline filters at :162-166/:192-194 replaced by host_rows, loader swap, exit codes) but removes no function or file. git grep outside docs/ for 'Trust boundary', 'opts every clone', 'hooks enabled for everyone', 'is the opt-in' finds only the prose being replaced (ARCHITECTURE.md:175-176, SKILL.md:148, :150), and no test pins those sentences. Minor: the trust-boundary sentence about acf-check-diff continues to :178, which section 4.7 covers as :175-180 although the claim cites :175-176.

### Unanchored findings

- **important**: In the approval_state contract (section 4.2) the fingerprint operand `rows` is unbound; its nearest antecedent is `registry.host_rows(call_sites)`, which differs between the hook (HOOK_CALL_SITES) and the diff gate (a single DIFF site). Read that way the two gates would compute different fingerprints, contradicting Decision 3's 'one approval covers both'. It must be `approval_rows(registry)` (TIER1).
  - evidence: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:116`
- **advisory**: The C12 deferral rests on 'whoever can rewrite the working tree can already run code', which does not hold for an Edit-permitted, Bash-denied agent racing parallel PostToolUse hooks against a detector that imports no repository helper; the residual is narrow but its justification is unstated for that case.
  - evidence: `plugins/arch-compliance/python/acf/detectors/host.py:78-83`
- **advisory**: For a repository rooted at home, `.acf/enabled` resolves to `~/.acf/enabled`, the same directory as the proposed per-user store `~/.acf/approvals.json`; the spec covers the store-containment refusal but not that the marker and the store share a directory.
  - evidence: `plugins/arch-compliance/python/acf/repo.py:29`

### Looked for but did not find

- any read of Path.home, expanduser, an approvals file or a 'trusted' flag anywhere under plugins/arch-compliance/python or plugins/arch-compliance/hooks
- a transitive import from inject_constraints.py (acf.repo, acf.exceptions, acf.registry, acf.loader, acf.template, acf.engine) reaching acf.detectors, importlib or exec_module
- a colon-bearing `detector:` value (host row) in config/architecture/mandates.yml
- importlib/exec_module/runpy anywhere under plugins/arch-compliance/python or hooks at 8677e45^
- a test or doc outside docs/ that pins the ARCHITECTURE.md trust-boundary sentence or acf-setup SKILL.md:148/:150 wording being replaced
- an except clause in posttooluse_gate.py main() covering UnicodeDecodeError or generic Exception after the marker check

## compliance

### Claim verdicts

#### M1 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_repo_tree_guard.py:12-16, plugins/arch-compliance/tests/test_repo_tree_guard.py:57-66, plugins/arch-compliance/python/acf/repo.py:53-73, config/architecture/ARCHITECTURE.md:126-132, docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:111-120`
- reasoning: Doctrine: callers 'hand it the string they hold and never join, resolve or compare against the root themselves' (ARCHITECTURE.md:128-130). The guard flags resolve/relative_to/is_relative_to/joinpath calls, os.path.realpath/abspath/relpath/commonpath, and `/` joins whose left operand is named repo/repo_root/root/ROOT/base/host_root with a non-constant right. The design: the store key is `RepoTree(repo).root.as_posix()`, containment is `RepoTree(repo).contained(str(store_path))` (handles absolute paths and symlink resolution, repo.py:53-59), detector files are read via `RepoTree(repo).file(rel)`, `store_path()` is `Path.home() / STORE_REL` (left operand a call to `home`, not a root name; right an uppercase constant), and cli_allow uses `resolve_repo(args.repo)` and `repo / MANDATES_REL` (constant right) with no `--mandates` argument (the reason cli_check_diff.main needs an allowlist entry). No new allowlist entry is needed, provided the implementer does not call `.resolve()` on the store path, which the spec never asks for.

#### M2 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:74-83, plugins/arch-compliance/hooks/posttooluse_gate.py:30-35, plugins/arch-compliance/tests/test_repo_paths.py:95-108, docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:104`
- reasoning: The no-marker path (posttooluse_gate.py:74-83) returns before the deferred third-party import block at :93-107; the only module-scope acf import is acf.repo (:30), which is stdlib-only (repo.py:1-9). The design imports acf.approval after that block succeeds, and the new broad try/except Exception in section 4.5.5 wraps code after :72 without adding an import. test_repo_paths.py:95-108 runs both hooks against a marker-less host with pydantic/yaml poisoned and asserts exit 0 and no traceback; nothing in the design reaches that path.

#### M3 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:252-253, pyproject.toml:3, plugins/arch-compliance/.claude-plugin/plugin.json:3, docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:157-166`
- reasoning: Doctrine: 'A change to a skill's prose bumps the plugin version in plugins/arch-compliance/.claude-plugin/plugin.json and pyproject.toml.' Section 4.7 changes acf-setup/SKILL.md and acf-mandate/SKILL.md; both version files read 0.2.4 today, so bumping both to 0.2.5 satisfies the rule.

#### M4 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/loader.py:60, config/architecture/ARCHITECTURE.md:239-240, docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:111-113`
- reasoning: Rule: every subprocess text call declares encoding='utf-8' and every prose file read declares its encoding. The store is read through load_model_file, which calls `path.read_text(encoding="utf-8")` at loader.py:60 (the spec cites :61, the OSError handler - a harmless off-by-one). file_digests and _SourceOnlyLoader read bytes (no decoding). No new component (approval.py, cli_allow.py, hook/diff-gate edits) makes a subprocess call. write_approval's temp-file write encoding is unspecified, but the rule as written covers reads.

#### M5 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/exceptions.py:5, config/architecture/ARCHITECTURE.md:109-110, docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:106-118`
- reasoning: Rule: every ACF exception subclasses AcfError and nothing else. The new names in section 4.2 are pydantic models, an Enum and functions; _SourceOnlyLoader (section 4.4) is a loader, not an exception. No exception class is introduced; failures use the existing `class AcfInputError(AcfError)`.

#### M6 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:27-31, config/architecture/mandates.yml:53-62, plugins/arch-compliance/hooks/posttooluse_gate.py:85-120, docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:140-150`
- reasoning: Doctrine forbids broad `except Exception:` handlers 'that swallow errors ... unless explicitly exempted with a reason'. The new hook handler prints type/message/traceback to stderr and returns 2 in hook mode (re-raises otherwise) and carries `fail-loud.bare-except-ok` with a reason (token declared at mandates.yml:60). The four exit-1 returns (posttooluse_gate.py:91, :107, :113, :120) become exit 2 in hook mode with stderr unchanged, routing the failure to the agent channel the hook already relies on (:131). Unapproved hook runs emit a notice through additionalContext/systemMessage or stderr rather than skipping silently, and the diff gate raises AcfInputError, which the existing handler (cli_check_diff.py:98-100) turns into exit 1 instead of a clean report.

#### M7 — SURVIVED
- evidence: `docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/host_row_gate_tests.py:26-42, docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/host_row_gate_tests.out:1-7, config/architecture/ARCHITECTURE.md:227-230`
- reasoning: Rule: a quantified tree claim needs a re-runnable recipe. The section 6.1 test population is an executed census with a re-runnable script whose committed output matches the section 6.1 table row for row; 'no repository module imported before 8677e45' (section 1.1) carries a git grep recipe; 'SubagentStart runs no host code' (section 3) carries a grep recipe; 'this repo has no host row' (section 7) carries a grep recipe, and I checked mandates.yml: no `detector:` value contains `.py:`. The section 1.2 four-return table is an enumerated per-line list, checked against posttooluse_gate.py:91/:107/:113/:120. Remaining 'every' sentences are normative design requirements, which ARCHITECTURE.md:230-231 exempts.

#### M8 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:175-182, config/architecture/ARCHITECTURE.md:159-163, docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:156`
- reasoning: The current Trust boundary paragraph (:175-180) makes `.acf/enabled` and the invocation the opt-in. The rewrite replaces exactly those two sentences while keeping the confinement and load_mandates sentences. The diff-gate refusal fits the Call-site rule's existing 'refused, not reported as a clean run' stance (:160-161), and the hook's skipping of unapproved host rows qualifies ':162-163 The PostToolUse hook runs rows declaring hook or posttooluse' via the Trust boundary paragraph rather than contradicting it. The closing 'No row: enforced by' line (:182) gains test_approval.py and test_cli_allow.py, keeping the section's enforcement pointer complete for the new tests.

#### M9 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:58-59, plugins/arch-compliance/python/acf/repo.py:50-51, plugins/arch-compliance/python/acf/registry.py:33-46`
- reasoning: Rule: 'When persisting paths to YAML/JSON, use Path.as_posix()'. The single persisted path, the store key, is `RepoTree(repo).root.as_posix()` (root is a resolved Path, repo.py:51). Detector file names inside the fingerprint input come from parse_host_detector_ref, which runs validate_posix_rel_path, so they are already POSIX strings. `str(store_path)` goes to RepoTree.contained, not into a serialization payload.

#### M10 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:203-204, docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:117, docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:142`
- reasoning: Rule: 'Skill prose and runtime messages name no host repository, path or section.' The refusal text (section 4.2 require_approval) and the notice text (section 4.5.3) are fully specified and name only `acf-allow`, `--trusted-checkout`, row ids and generic instructions; the section 4.7 prose changes describe generic behaviour (approval, `.acf/enabled`, CI flag) and name no host.

#### M11 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:264-266, plugins/arch-compliance/python/acf/detectors/host.py:162-166, plugins/arch-compliance/python/acf/detectors/host.py:192-194, plugins/arch-compliance/python/acf/baseline.py:68-86, plugins/arch-compliance/python/acf/loader.py:43-57`
- reasoning: Rule: one canonical implementation for an operation more than one module needs. The two existing host-row selections (host.py:162-166 and :192-194, each `registry.active(...)` + `is_host_detector_ref`) are consolidated into MandateRegistry.host_rows, which acf.approval also uses; other uses of is_host_detector_ref (registry.py:74, :144, :152) are row validation, not selection. The store is read through the shared load_model_file with the caller-decides-absence split documented at baseline.py:81-82. No package-wide atomic-write helper exists today (grep for os.replace/tempfile under plugins/arch-compliance finds none), and write_approval is named beside save_baseline with a reason for its different write semantics, so no second copy of an existing operation is created.

### Unanchored findings

- **advisory**: _canonical with json.dumps(default=str) maps a YAML date and the equal-text string to the same canonical JSON text (both as values and as keys), so a params change from `2024-01-01` to `"2024-01-01"` leaves the fingerprint, and the approval, unchanged - contrary to the claim that any change to a host row lapses the approval.
  - evidence: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:114`

### Looked for but did not find

- ## High-frequency misses: completeness claims (recipes present; see M7), defaults re-entering for declared values (none), host names in prose/messages (none; see M10), stdlib exception mixins (no new exception class), subprocess text calls without encoding (no subprocess added), check re-implemented instead of consumed (load_mandates, KNOWN_DETECTORS and acf.repo constants are consumed; cli_allow reuses the diff gate's load_mandates call)
- ## No shims: the design adds no hasattr probing and no `any` escape hatch - not touched
- ## Build artifacts / ## Fail-loud ratchet / ## Facade sinks / ## FSM transitions / ## Soft fail-loud smells / ## React boundaries: no change to those detectors or rows - not touched
- ## Declared, never defaulted: the section governs the ADR gate's host values in adr.yml; the store's fixed location under Path.home() is not a default standing in for a missing host declaration, and cli_allow's use of the resolve_repo cwd fallback is already recorded there (ARCHITECTURE.md:192-193) - not breached
- ## Frozen ledger format: no LedgerRow/LedgerAmendment change - not touched
- ## Scoped refactor: the host.py selector refactor is confined to code paths the design changes; the typescript_bridge shell=True issue is deferred, not folded in - conforms
- ## Post-merge: no change to the operational declarations - not touched

### Unstated mandates

- ## Live consumers - the design adds new exports (approval_rows, read_store, store_path, file_digests, fingerprint, require_approval, write_approval, ApprovalState, MandateRegistry.host_rows), and the doctrine requires each to have a live call site in the package, a hook or a skill. The spec does not name the section; most exports have an evident consumer (cli_allow, the hook, cli_check_diff, host.py), but approval_rows has no consumer the section 4.2/4.3 text names explicitly.

## sweeper

### Claim verdicts

#### S1 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/loader.py:58-77, plugins/arch-compliance/python/acf/baseline.py:78-86, plugins/arch-compliance/python/acf/registry.py:132`
- reasoning: load_model_file already owns existence (require_file at :58), read, json/yaml parse and pydantic validation, raising AcfInputError at every step; load_baseline (baseline.py:86) and load_mandates (registry.py:132) consume it identically, so it is the shared single point. A read_store made of `is_file()` -> empty ApprovalStore plus load_model_file adds no second parse/validate path; the caller-side absence check is the split baseline.py:81-82 prescribes. Searched the python tree for other `json.loads`/`model_validate` loaders of persisted stores: none outside loader.py.

#### S2 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:164-165, plugins/arch-compliance/python/acf/detectors/host.py:193, plugins/arch-compliance/python/acf/cli_check_diff.py:167-182, plugins/arch-compliance/python/acf/cli_check_diff.py:204, plugins/arch-compliance/hooks/posttooluse_gate.py:273-294, plugins/arch-compliance/python/acf/registry.py:139-172`
- reasoning: Behaviour sweep (every `.active(`, `is_host_detector_ref`, `load_host_detector`, `scan_host` in python and hooks trees, excluding tests): only scan_host_ast_file (host.py:164-165) and scan_host_guards (host.py:193) select host rows to run, and both gates reach host code only through them (cli_check_diff.py:167,179,204; posttooluse_gate.py:274,284,293). The other predicate uses do not select rows to run: load_mandates (registry.py:144,152-172) selects active ast/guard host rows to stat their files, and cli_check_diff.py:90-92 counts active ast/guard rows (host included) for its empty-selection refusal. So the claim holds as stated, but the predicate itself keeps a second owner (see relationships).

#### S3 — SURVIVED
- evidence: `pyproject.toml:18-20, plugins/arch-compliance/python/acf/cli_check_llm.py:17`
- reasoning: `[project.scripts]` holds exactly `acf-check-diff = "acf.cli_check_diff:main"` and `acf-check-llm = "acf.cli_check_llm:main"`; the only cli modules in acf/ are cli_check_diff.py and cli_check_llm.py, each with `main(argv)` and an argparse prog. `acf-allow = "acf.cli_allow:main"` follows the shape; no test asserts the script list (searched project.scripts / console_scripts / entry_points).

#### S4 — REFUTED
- evidence: `docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/host_row_gate_tests.py:15, plugins/arch-compliance/tests/test_hooks.py:379, plugins/arch-compliance/tests/test_diff_cli.py:311`
- reasoning: The instance list is correct at 0da9864: host-row tests exist only in test_hooks.py, test_diff_cli.py, test_host_detectors.py and test_registry.py, and the last two call the runners/loader directly, never a gate; the seven listed tests match my reading. But the method is a name sweep: HOST_ROW (:15) matches the current helper names `_host_row(`, `_seed_host_rows(`, `_host_rows(`, `_host_repo(`, and its only shape pattern `detector:\s*[\w./-]+\.py:\w+` does not match how these tests actually build rows (test_hooks.py:379 writes `detector: hostdet/rules.py:{fn}`; `{` is not `\w`), so every test_hooks hit depends on the helper name. Pytest fixtures are never followed (a fixture is a parameter, not an ast.Call). Section 6.1 instructs the implementer to re-run this census before editing; a re-run would miss any test that seeds host rows through a new helper or fixture (including the helpers test_approval.py/test_cli_allow.py will add) or through a dict/f-string detector.

#### S5 — REFUTED
- evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:161`
- reasoning: Searched tracked prose (plugins/**/*.md, README, CLAUDE.md, docs/guides, docs/design, hooks.json, ci.yml) for acf-check-diff, cli_check_diff, exit codes, `host detector`, `.acf/enabled`, `host code`, `opt-in`. docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md (Status: Implementing / plan approved) states at :161 the PostToolUse hook 'runs host guards on every edited in-repo path' - a statement of when the hook runs host code that becomes false under Decision 6, with no section 4.7 row. Also unlisted: the acf-setup pre-commit snippet and local smoke (plugins/arch-compliance/skills/acf-setup/SKILL.md:164, :182-184, :193-196), whose pre-commit entry (:184) will now be refused for any host with host rows until each person runs acf-allow.

#### S6 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:23, plugins/arch-compliance/hooks/posttooluse_gate.py:228, plugins/arch-compliance/tests/test_repo_tree_guard.py:16-17`
- reasoning: Host runners are imported only by cli_check_diff.py:23 and posttooluse_gate.py:228; inject_constraints and cli_check_llm only call load_mandates; the TS bridge runs the plugin's own pack (typescript_bridge.py:19,54), not repository code. No new exception type is needed (AcfInputError/UnknownDetectorError exist). The planned path operations (`Path.home() / STORE_REL`, `repo / MANDATES_REL`, temp file under the store's parent) do not trip the RepoTree guard rules (ROOT_NAMES join with non-constant, resolve, relative_to), so no allowlist entry or repo.py change is required. The fail-loud ratchet row is unenforced (config/architecture/mandates.yml:94), so the new hook `except Exception` needs no baseline-file change.

#### S7 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:138-147, plugins/arch-compliance/hooks/posttooluse_gate.py:77-80, plugins/arch-compliance/hooks/inject_constraints.py:121-123`
- reasoning: The hook already emits additionalContext JSON (:138-147) and already writes advisory `acf:` notices to stderr (:77-80, disabled warning); inject_constraints uses the same hookSpecificOutput/additionalContext shape. Nothing in the plugin emits systemMessage today (grep across plugins/), so it is one new top-level field on the existing JSON object, not a parallel reporting mechanism. Validity of systemMessage itself is external and unverifiable here.

#### S8 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/baseline.py:68-75, plugins/arch-compliance/python/acf/adr/run_detail.py:185, plugins/arch-compliance/python/acf/adr/ledger.py:207`
- reasoning: Swept every persisted-file writer (write_text, open('w'/'a'), tempfile, os.replace): save_baseline writes in place raising BaselineError, run_detail writes in place, the ledger appends; no existing helper does a temp-file + os.replace whole-file swap. write_approval therefore duplicates no existing writer; the two share only `model_dump_json` + mkdir, a two-line idiom that does not justify a shared helper given different error types (BaselineError vs AcfInputError) and concurrency models.

#### S9 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:36-74, plugins/arch-compliance/hooks/posttooluse_gate.py:41-64, plugins/arch-compliance/python/acf/judge.py:66`
- reasoning: Neither gate's argparse surface has a flag that bypasses host-row execution; the only ACF_* environment variables are judge settings (judge.py:66,81); no config key bypasses it. The literal word 'configures' is overbroad: `--call-site` (cli_check_diff.py:63-68), row `call_sites`/`status`, and the `.acf/enabled` marker (posttooluse_gate.py:74-83) all configure which host rows run - but the spec names all three itself (Decisions 1, 3), and none of them can skip an approval once host rows are selected. `--mandates` points at an alternate registry, but its rows change the fingerprint (yielding STALE, not a bypass). The load-bearing part - --trusted-checkout is the only bypass - holds.

### Unanchored findings

- **important**: Section 4.2 contradicts Decision 3 on which rows approval_state fingerprints: approval_state's contract has `rows` = `registry.host_rows(call_sites)`, while acf-allow writes the fingerprint of approval_rows = host_rows(TIER1_CALL_SITES). As written, any registry with a [ci]-only host row is permanently STALE in the hook, and the 'seed an approval; assertions unchanged' disposition of test_hooks.py:440 (which carries a [ci]-only host guard) fails.
  - evidence: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:116, docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:112, plugins/arch-compliance/tests/test_hooks.py:445`
- **advisory**: The section 6.1 census matches test helpers by current name; its only shape regex cannot match the f-string detector at test_hooks.py:379 and it never follows fixtures, so the re-run section 6.1 prescribes will miss tests seeded through any new helper.
  - evidence: `docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/host_row_gate_tests.py:15`
- **advisory**: Section 4.7 omits the plan-approved design's hook row (runs host guards on every edited in-repo path) and the acf-setup pre-commit snippet, whose diff-gate run is refused for hosts with host rows until each person runs acf-allow; section 7 names only CI and hand runs.
  - evidence: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:161, plugins/arch-compliance/skills/acf-setup/SKILL.md:184`

### Looked for but did not find

- Another selector that picks host rows to run: grep `.active(`, `is_host_detector_ref`, `load_host_detector`, `scan_host` across plugins/arch-compliance/python and hooks
- An existing per-user / home-directory store: grep `Path.home`, `expanduser`, `os.environ`, `getenv`, `ACF_`
- An existing atomic-replace writer: grep `tempfile`, `NamedTemporaryFile`, `os.replace`, `open(...'w'/'a')`, `write_text(`
- An existing fingerprint/hash of detector files or rows: grep `hashlib`, `sha256` (only host.py:73 module-name hashing, a different job)
- Existing systemMessage emission: grep `systemMessage|additionalContext|hookSpecificOutput` in plugins/
- Existing bypass flags or env vars for host execution: argparse definitions in cli_check_diff.py and posttooluse_gate.py
- A test asserting the console-script list: grep `project.scripts|console_scripts|entry_points|acf-check-llm`
- Other gate tests with host rows outside the census: grep `.py:[a-zA-Z_]`, `_host_row`, `_seed_host`, `_host_repo` in plugins/arch-compliance/tests and tests/

### Relationships

- PARTIAL_OVERLAP: `MandateRegistry.host_rows` — responsibility `decide whether a row is a host ast/guard row` — existing `plugins/arch-compliance/python/acf/registry.py:144`
  - resolution: Extract the predicate `m.detection in {"ast","guard"} and is_host_detector_ref(m.detector)` as a module-level `is_host_row(m)` in registry.py (or a Mandate property) consumed by host_rows, load_mandates' file-existence loop (:144, :150-154) and Mandate._row_shape (:72-76), so the predicate is stated once; host_rows keeps the call-site/detection filtering and load_mandates keeps its stat check.
- PARTIAL_OVERLAP: `cli_allow.main registry load` — responsibility `load the host registry with the gate's full validation arguments` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:84-89`
  - resolution: `load_mandates(repo / MANDATES_REL, known_detectors=KNOWN_DETECTORS, llm_prompt_ids=LLM_PROMPT_IDS, repo_root=repo)` is repeated in cli_check_diff, the new cli_allow and (minus llm_prompt_ids) posttooluse_gate.py:110; a `load_gate_registry(repo, mandates_path=None)` helper would make all three gates validate a registry identically, so acf-allow cannot approve a registry the gates would refuse.
- ADJACENT: `approval.read_store` — responsibility `load/parse/validate a persisted JSON model` — existing `plugins/arch-compliance/python/acf/baseline.py:86`
  - resolution: None - both are consumers of loader.load_model_file.
  - non-merge: Both delegate to the one loader; each owns only its model and subject string, as load_baseline and load_mandates already do.
- ADJACENT: `approval.write_approval` — responsibility `persist a pydantic model as JSON` — existing `plugins/arch-compliance/python/acf/baseline.py:68-75`
  - resolution: None.
  - non-merge: save_baseline writes an in-repository artifact in place raising BaselineError; write_approval rewrites a per-user, concurrently read file via temp+os.replace raising AcfInputError; the shared part is a two-line model_dump_json idiom.
- ADJACENT: `approval.require_approval (diff-gate refusal)` — responsibility `refuse rather than report a clean run` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:90-96`
  - resolution: None - both raise AcfInputError inside the same try and exit 1 through :98-100.
  - non-merge: Different conditions (no selected rows vs unapproved host rows) already share the one refusal channel; no logic is duplicated.
- ADJACENT: `hook unapproved notice` — responsibility `report a non-fatal gate condition to agent and user` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:77-80`
  - resolution: None.
  - non-merge: The disabled warning fires before any third-party import and only on stderr; the approval notice fires after registry load and needs additionalContext/systemMessage delivery. Shared prefix `acf:` only; distinct delivery points.

### Two-owner counts

- host ast/guard row predicate (detection in ast/guard and host detector ref): 2
- load registry with gate validation arguments: 3
- emit Claude Code hook JSON with additionalContext: 2
- persist a pydantic model as JSON: 2

### Document conflicts

- `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:161` (contradicts): runs rows declaring `hook`/`posttooluse`, runs host guards on every edited in-repo path
- `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:64` (contradicts): That marker is the opt-in for running host code on edit.
- `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:65` (contradicts): `acf-check-diff` runs only when the host's own pre-commit or CI configuration invokes it ... That invocation is the opt-in.
- `config/architecture/ARCHITECTURE.md:175` (contradicts): The PostToolUse hook runs host code only when `.acf/enabled` exists; committing `.acf/` therefore opts every clone in.
- `plugins/arch-compliance/skills/acf-setup/SKILL.md:148` (contradicts): `.acf/enabled` is the opt-in for the automatic hooks, host detectors included

## hardening

### Claim verdicts

#### H1 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:74-75; plugins/arch-compliance/python/acf/detectors/host.py:78-83`
- reasoning: The only opt-in today is `enabled.is_file()` (posttooluse_gate.py:74-75) - a presence bit with no content; load_host_detector execs whatever bytes the named file holds at load time (host.py:78-83). A marker rule therefore has no place to record which bytes were approved, so a checkout that changes the detector file under an unchanged marker runs new code. The claim holds by construction.

#### H2 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:66-83; plugins/arch-compliance/python/acf/registry.py:160-172`
- reasoning: Load resolves the detector path from the row (registry.py:160-172 only checks existence) and execs current bytes (host.py:66-83); a per-repository boolean would carry over any later row or byte change. Binding to rows plus file digests is the minimal record that makes a changed branch re-prompt.

#### H3 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:130-133; plugins/arch-compliance/hooks/hooks.json:16-27`
- reasoning: The hook fires on every Write|Edit|MultiEdit (hooks.json:16-27) and exit 2 is the code it uses as blocking agent feedback (posttooluse_gate.py:130-133); a refusal on missing approval would put that on every edit in the repository. Skipping host rows while keeping built-ins and emitting a named notice is a loud, not silent, degradation - the notice names the skipped rows and the command.

#### H4 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:90-96; plugins/arch-compliance/python/acf/cli_check_diff.py:111-113; .github/workflows/ci.yml:39`
- reasoning: The diff gate's only output contract is exit 0/1 (cli_check_diff.py:111-113) and it already refuses rather than report a clean run when the call site selects nothing (:90-96), so a skipped host row reported as exit 0 would violate that same rule. The CI invocation is a literal command line in the workflow file (ci.yml:39), so an added flag there is an explicit, host-owned opt-in; no environment detection is involved.

#### H5 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:78`
- reasoning: Throwaway experiment (scratch dir, Python 3.13.2): compiled det.py with py_compile UNCHECKED_HASH, then rewrote the source; loading via spec_from_file_location with the default loader (the host.py:78 call shape) returned the .pyc's function ('pyc'), not the source's. The default SourceFileLoader does execute an unchecked hash-based .pyc without reading the source, so what runs can differ from what was fingerprinted. A committed __pycache__/ arrives with git checkout and can produce exactly this.

#### H6 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:162-166; plugins/arch-compliance/python/acf/detectors/host.py:192-194; plugins/arch-compliance/python/acf/registry.py:17-19; plugins/arch-compliance/python/acf/registry.py:110-122`
- reasoning: The only host call sites are scan_host_ast_file (host.py:162-166: active ast + is_host_detector_ref + language) and scan_host_guards (host.py:192-194: active guard + is_host_detector_ref). host_rows is the union of both selections minus the language filter, so it is a superset at any call_sites; HOOK_CALL_SITES and DIFF_CALL_SITES are both subsets of TIER1_CALL_SITES (registry.py:17-19), so host_rows(TIER1) covers every row either gate can run. Empty host_rows(call_sites) implies no host call. The converse in 'exactly' does not hold (an ast-only host row with no edited .py/.ts file makes no call yet still requires approval), which is conservative, not unsafe (see advisory finding).

#### H7 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:61; plugins/arch-compliance/python/acf/loader.py:64`
- reasoning: params is dict[str, Any] (registry.py:61); a top-level int key is refused by pydantic (tested: Mandate.model_validate(params={1:2}) raises ValidationError). Nested values are Any from yaml.safe_load (loader.py:64). Tested: safe_load yields sets, date keys, int/str keys and bytes (!!binary), refuses unhashable (list/dict) keys with ConstructorError, and never yields tuples, so the 'tuples' case is vacuous. Implemented the spec's _canonical as written and fingerprinted a row whose params held a !!set of mixed str/date/int/float and a mapping with date, 1, '1', bytes and .nan keys: no exception, and an identical SHA-256 under PYTHONHASHSEED 1, 2 and 3. Caveat (advisory): a date key and the equal string key canonicalise to the same text and merge silently.

#### H8 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:243-250; plugins/arch-compliance/hooks/posttooluse_gate.py:273-294; plugins/arch-compliance/python/acf/detectors/host.py:201-210`
- reasoning: rel_paths and file_lines are filled at :243-250 before and independently of the host calls; the three host calls (:273-277, :283-287, :292-294) are standalone findings.extend statements whose results no built-in call reads. The one side effect of skipping is that scan_host_guards no longer adds flagged files to file_lines (host.py:201-210), which only serves exemption lookup for host findings that are absent when skipped.

#### H9 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:53-59`
- reasoning: contained() computes (root / path).resolve(); an absolute path replaces root under pathlib join, so the absolute store path is resolved as-is (symlinks followed) and is_relative_to(root) is tested against the resolved root (repo.py:51); on Windows the comparison is case-insensitive via PureWindowsPath semantics. Path.home() uses expanduser semantics: USERPROFILE on Windows (HOME ignored since 3.8), HOME on POSIX. Gap: RuntimeError/ValueError makes contained() return None ('not in repo'), only for a symlink loop or NUL in the home path, where the store then reads as absent (MISSING).

#### H10 — UNPROVEN
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:138-147`
- reasoning: External claim about the Claude Code hooks reference, which I cannot read; live code emits only hookSpecificOutput.additionalContext (:138-147) and nothing in the repo evidences a top-level systemMessage being accepted alongside it. Not load-bearing: the notice still reaches the agent through additionalContext.

#### H11 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:109-113; plugins/arch-compliance/python/acf/loader.py:58-77`
- reasoning: The try at :109-113 catches (AcfInputError, UnknownDetectorError), so an AcfInputError raised by approval_state placed inside it is caught as claimed. Not every approval_state failure is an AcfInputError, though: a non-UTF-8 or >4300-digit-int store raises UnicodeDecodeError/ValueError out of load_model_file (see H16), and Path.home() raises RuntimeError when no home can be determined; these escape this tuple and land in the new catch-all (exit 2 in hook mode, traceback otherwise).

#### H12 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:40-44; plugins/arch-compliance/python/acf/repo.py:51; plugins/arch-compliance/hooks/posttooluse_gate.py:156-160; plugins/arch-compliance/python/acf/cli_check_diff.py:76`
- reasoning: The hook calls resolve_repo(explicit, stdin cwd) (posttooluse_gate.py:156-160), the diff gate resolve_repo(args.repo) (cli_check_diff.py:76); both go through Path.resolve() (repo.py:40-44) and RepoTree re-resolves (repo.py:51). On Windows resolve() is realpath via GetFinalPathNameByHandle, normalising case, junctions and subst drives for existing directories, so the same checkout directory yields the same as_posix() key. A subdirectory cwd yields a different key, but there the hook no-ops (no .acf/enabled) and acf-allow fails to load mandates, so no mismatched approval is written.

#### H13 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:78-84`
- reasoning: Throwaway experiment: spec_from_file_location(name, path, loader=L(name, path)) with L subclassing importlib.machinery.SourceFileLoader and overriding get_code as the spec states; with a stale UNCHECKED_HASH .pyc in __pycache__/ it returned 'source' (default loader returned 'pyc'). Module behaviour matched host.py:78-84: module_from_spec, sys.modules registration, exec_module and getattr all worked and __file__ was set. The override also skips writing a .pyc.

#### H14 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:83-100`
- reasoning: The try spans :83-97 and :98 catches (GitError, AcfInputError, UnknownDetectorError, DetectorPackError), printing f"acf: {exc}" to stderr and returning 1 (:99-100). A require_approval call placed after the empty-selection refusal (:90-96) and before _scan_changed (:97) has its AcfInputError handled exactly so. (Store-decoding errors that are not AcfInputError escape as a traceback - see H16.)

#### H15 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:68-72; plugins/arch-compliance/python/acf/detectors/python_pack.py:54-74; plugins/arch-compliance/python/acf/enforcement.py:27-35; config/architecture/mandates.yml:53-62`
- reasoning: out_format is bound at :68-72 before every later return, so the rest of main can sit in one try. The fail-loud.bare-except finding is reported at node.lineno of the ExceptHandler (python_pack.py:62-70) and fires for `except Exception` (:73-77); apply_registry drops a finding whose source line carries `# fail-loud.bare-except-ok: <reason>` (enforcement.py:27-35, 64-65), the row's exemption token (mandates.yml:53-62). host.py:49/87/115 already use this pattern. The fail-loud.ratchet row is unenforced (mandates.yml:86-94), so the added handler raises no count.

#### H16 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/loader.py:59-66`
- reasoning: The model shape fits (Literal[1] and a dict of entries validate via model_validate; ValidationError becomes AcfInputError at :74-77), but 'every bad-file case' is false. read_text catches only OSError (:59-62), so a non-UTF-8 store raises UnicodeDecodeError (a ValueError subclass); the parse step catches only YAMLError/JSONDecodeError (:63-66). Tested on 3.13: json.loads of a >4300-digit integer raises plain ValueError and deeply nested arrays raise RecursionError, neither caught. The result is a traceback in the diff gate and acf-allow, and an 'internal error' exit 2 in the hook, instead of the AcfInputError section 4.2 says is 'Every refusal'.

#### H17 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:139-172`
- reasoning: With known_detectors passed, every active ast/guard host row has its file checked: OSError from stat raises UnknownDetectorError (:161-167), a missing file raises UnknownDetectorError (:168-172). host_rows selects only active ast/guard host rows, so every approval row passed this check. Section 4.3 maps UnknownDetectorError to stderr + exit 1, as cli_check_diff does at :98.

### Unanchored findings

- **important**: The approval store is read through load_model_file, which lets UnicodeDecodeError (non-UTF-8 file), ValueError (oversized JSON integer) and RecursionError (deep nesting) escape untyped; section 4.2's 'Every refusal is that loader's AcfInputError' is false, and the hardening belongs in the shared loader (one owner), not a new catch-all at each gate.
  - evidence: `plugins/arch-compliance/python/acf/loader.py:59-66`
- **important**: The store-in-repo containment check refuses only a store resolving inside the repository; if the process environment's HOME/USERPROFILE points at an out-of-tree location someone else controls (on Windows a UNC share), the store passes. Decision 2's 'removes the one route' is a completeness claim the containment predicate does not cover.
  - evidence: `plugins/arch-compliance/python/acf/repo.py:53-59`
- **advisory**: Path.home() raises RuntimeError when no home directory can be determined; in approval_state that is outside the hook's (AcfInputError, UnknownDetectorError) tuple, so on such a host every edit becomes an 'internal error' exit 2 instead of a typed refusal or an unapproved notice.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:109-113`
- **advisory**: The fingerprint is computed from one read of each detector file and the loader compiles a second read; hashing and compiling the same byte buffer (load_host_detector refusing bytes whose digest is not the approved one) would close the check-to-load gap at rung 1 instead of accepting it as residual.
  - evidence: `plugins/arch-compliance/python/acf/detectors/host.py:78-83`
- **advisory**: host_rows ignores the language filter and the edited-file set, so with only host ast rows the unapproved notice fires on edits (e.g. to .md files) that would make no host call, adding to the per-edit noise the risk table already accepts.
  - evidence: `plugins/arch-compliance/python/acf/detectors/host.py:162-167`
- **advisory**: --trusted-checkout trusts whoever writes the command line - the 'invocation is the opt-in' rule Decision 7 supersedes - covering a committed pre-commit config and an agent as well as a CI workflow; only skill prose keeps an agent from adding the flag.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:63-68`
- **advisory**: _canonical maps a date key and the equal ISO string key to the same canonical text, so they merge silently in the fingerprint; switching such a nested params key between the two forms does not lapse the approval.
  - evidence: `plugins/arch-compliance/python/acf/registry.py:61`

### Looked for but did not find

- A second chokepoint executing host code besides load_host_detector's exec_module (searched host.py, cli_check_diff.py, posttooluse_gate.py): none; scan_host_ast_file and scan_host_guards both route through host.py:176/198.
- A built-in detector call in _scan_paths that reads a value produced by a host call: none; built-ins read only text, rel_paths and file_lines.
- A YAML safe_load construct yielding a tuple or an unhashable key inside params: tuples are never produced; list/dict keys are refused with ConstructorError.
- A pydantic path accepting a non-string top-level params key: refused (ValidationError).
- A repo-root resolution difference between the hook and the diff gate / acf-allow: both use resolve_repo and RepoTree.resolve.
- An active fail-loud.ratchet row that would count the new except Exception handler: the row is unenforced.
- A guard the design defers to that needed executing: none - the design relies on no existing guard to cover a site.

### Mechanism traces

- **Per-user fingerprint approval check (approval_state / require_approval) before host rows run**
  - invalid state: registry.host_rows(call_sites) non-empty AND fingerprint(host_rows(TIER1), sha256 of each named file) != store.repos[RepoTree(repo).root.as_posix()].fingerprint (or no entry)
  - producer: `plugins/arch-compliance/hooks/posttooluse_gate.py:74-75`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: The rows and files arrive by git clone/checkout, outside ACF; the spec states 'Neither gate holds state outside the working tree that records a person's approval of particular code, so approval and code arrive together with a git clone or git checkout.'
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:116-117`
- **Unapproved hook run skips host rows, runs built-ins and emits a notice (_scan_paths run_host=False)**
  - invalid state: hook run where approval_state(repo, registry, HOOK_CALL_SITES) in {MISSING, STALE, STORE_IN_REPO}
  - producer: `plugins/arch-compliance/hooks/posttooluse_gate.py:273-294`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: Decision 6: 'An unapproved hook run is governed by built-ins and told so, not blocked.'
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:141-143`
- **Store-inside-repository refusal (STORE_IN_REPO via RepoTree.contained)**
  - invalid state: RepoTree(repo).contained(str(Path.home() / '.acf' / 'approvals.json')) is not None
  - producer: `plugins/arch-compliance/python/acf/repo.py:42-43`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: Spec: 'Path.home() reads USERPROFILE on Windows and HOME on POSIX, so the process environment decides where the store is; the containment check removes the one route by which a repository could supply its own approval file through that environment.'
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:67`
- **_SourceOnlyLoader (source-only compile of the detector file)**
  - invalid state: __pycache__/ holds a .pyc for the detector file whose code object differs from compile(source bytes) and that the default SourceFileLoader would execute (unchecked-hash pyc)
  - producer: `plugins/arch-compliance/python/acf/detectors/host.py:78`
  - rung 2 (highest applicable 1); repairs=False
  - hardening rejected because: For the residual second read: 'A process that can rewrite the working tree during a gate run can already run code as the user.'
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:136`
- **Fingerprint canonicalisation (_canonical over model_dump)**
  - invalid state: Mandate.model_dump(mode='python') contains a set/frozenset or non-str dict key nested in params, on which json.dumps(sort_keys=True) raises or orders by hash seed
  - producer: `plugins/arch-compliance/python/acf/loader.py:64`
  - rung 2 (highest applicable 1); repairs=True
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:114`
- **Hook-mode catch-all `except Exception` returning 2**
  - invalid state: an exception raised after out_format is set whose type no except tuple names, e.g. UnicodeDecodeError from read_text(encoding='utf-8') on a non-UTF-8 edited file
  - producer: `plugins/arch-compliance/hooks/posttooluse_gate.py:249`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:144`
- **--trusted-checkout flag on acf-check-diff**
  - invalid state: diff-gate run with non-empty host_rows(sites) on a machine with no per-user store entry (fresh CI runner)
  - producer: `.github/workflows/ci.yml:39`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: Decision 7: 'CI workflows pass --trusted-checkout, so the opt-in is written in the workflow file the host controls.'
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:72`

## Claims

- **C1** [root_cause] [load-bearing]: Neither gate holds state outside the working tree recording a person's approval of particular host code: the PostToolUse hook's only check is whether `.acf/enabled` is a file (`posttooluse_gate.py:74-83`), and `acf-check-diff` calls the host runners (`cli_check_diff.py:167-182`, `:204`) with no check at all.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:74-83`
- **C2** [premise] [load-bearing]: `hooks.json` registers `posttooluse_gate.py --format hook` for `Write|Edit|MultiEdit` at plugin level, so once installed the hook fires in every repository the user opens.
  - spec citation: `plugins/arch-compliance/hooks/hooks.json:16-27`
- **C3** [premise] [load-bearing]: `load_host_detector` imports the named file with `spec.loader.exec_module(mod)` (`host.py:83`) in the gate's own process, and `_call_host` calls the returned callable (`:108`).
  - spec citation: `plugins/arch-compliance/python/acf/detectors/host.py:53-95`
- **C4** [premise]: The acf-setup skill recommends committing `.acf/` when a team wants hooks enabled for everyone.
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:150`
- **C5** [premise]: Before host rows were added (`8677e45`), neither gate imported a repository module: `git grep -n "importlib\|exec_module\|runpy" 8677e45^ -- plugins/arch-compliance/python plugins/arch-compliance/hooks` prints nothing.
  - spec citation: `None`
- **C6** [premise]: Host detector finding messages reach the agent's context via `additionalContext` on a non-blocking hook run and via stderr on exit 2.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:137-147`
- **C7** [root_cause] [load-bearing]: In hook mode the gate returns exit 1 on four gate-input failures (`posttooluse_gate.py:85-91`, `:99-107`, `:109-113`, `:116-120`), and any other exception raised after the marker check that no `except` tuple names (for example `UnicodeDecodeError` from `read_text` at `:249`) ends the process with a traceback and exit 1.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:85-120`
- **C8** [premise]: (External) For a PostToolUse hook, exit 2 shows stderr to Claude and other non-zero codes show stderr to the user only; the design depends only on the exit-2 half, which the hook already relies on (`posttooluse_gate.py:131`).
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:131`
- **C9** [premise] [load-bearing]: Deferral: the SubagentStart hook `inject_constraints.py` runs no host code; `grep -n "acf.detectors\|scan_host\|load_host_detector" plugins/arch-compliance/hooks/inject_constraints.py` prints nothing and its `acf` imports (`:31`, `:91`, `:92`, `:163`, `:170`) are acf.repo, acf.exceptions, acf.registry, acf.loader and acf.template. Verify no transitive route reaches host detector machinery.
  - spec citation: `plugins/arch-compliance/hooks/inject_constraints.py`
- **C10** [premise] [load-bearing]: The plugin's own prose has the agent or a person run `acf-check-diff` by hand, outside host CI or pre-commit configuration: `plugins/arch-compliance/skills/acf-setup/SKILL.md:221-230` (Step 9), `plugins/arch-compliance/skills/acf-mandate/SKILL.md:136`, `README.md:57`.
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:221-230`
- **C11** [premise] [load-bearing]: Deferral: a change confined to a module a detector imports is outside the fingerprint, because `load_host_detector` appends the repository root to `sys.path` (`host.py:59`) and such imports go through the normal import system; the design accepts this as a printed limitation.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/host.py:59`
- **C12** [premise] [load-bearing]: Deferral: a file rewritten between the gate's fingerprint check and the detector load runs unapproved bytes; accepted because a process that can rewrite the working tree during a gate run can already run code as the user.
  - spec citation: `None`
- **C13** [premise]: Deferral: a repository whose root is the home directory always has the store inside it and is always unapproved (hook never runs its host rows; diff gate only with `--trusted-checkout`).
  - spec citation: `None`
- **C14** [premise]: Deferral: the Windows TypeScript bridge's `shell=True` call (`typescript_bridge.py:52-58`) is another repository-controlled input path, recorded for a separate fix and outside this design.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:52-58`
- **C15** [premise] [load-bearing]: Each of the four hook-mode exit-1 returns is reached after `out_format` is computed (`:68-72`).
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:68-72`
- **C16** [premise]: The text-format exit-1 hook tests at `test_hooks.py:145`, `:318`, `:424` run in text mode, so they stay valid when only hook mode changes.
  - spec citation: `plugins/arch-compliance/tests/test_hooks.py`
- **C17** [premise] [load-bearing]: This repository's `config/architecture/mandates.yml` has no host row (`grep -n "detector: .*\.py:" config/architecture/mandates.yml` prints nothing), so its CI step (`.github/workflows/ci.yml:40`) needs no `--trusted-checkout`.
  - spec citation: `.github/workflows/ci.yml:40`
- **C18** [deletion]: The design deletes no runtime code; it replaces the doctrine trust-boundary sentence (`ARCHITECTURE.md:175-176`), acf-setup's commit-opt-in wording (`SKILL.md:148`, `:150`) and other prose listed in section 4.7, and adds an approval layer.
  - spec citation: `config/architecture/ARCHITECTURE.md:175-176`
- **M1** [mandate] [load-bearing]: `acf.approval` and `acf.cli_allow` turn repository path strings into locations only through `RepoTree` and `resolve_repo`, and compare the store path with the repository only through `RepoTree.contained`, complying with `## One owner for host paths`; `test_repo_tree_guard.py` needs no new allowlist entry.
  - spec citation: `config/architecture/ARCHITECTURE.md:113-139`
- **M2** [mandate] [load-bearing]: The hook's no-marker path still imports nothing beyond `acf.repo`, because `acf.approval` is imported only after the third-party imports (`posttooluse_gate.py:93-107`); `test_repo_paths.py:81-108` keeps passing.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:93-107`
- **M3** [mandate]: `## Release discipline` requires the version bump because acf-setup and acf-mandate skill prose change; both version files go to 0.2.5.
  - spec citation: `config/architecture/ARCHITECTURE.md:250-260`
- **M4** [mandate]: `## Declared text decoding`: the store is read through `load_model_file`, which reads with `encoding="utf-8"` (`loader.py:61`); the design adds no subprocess call.
  - spec citation: `config/architecture/ARCHITECTURE.md:237-248`
- **M5** [mandate]: `## One base exception`: the design adds no exception class; failures use `AcfInputError`.
  - spec citation: `config/architecture/ARCHITECTURE.md:107-111`
- **M6** [mandate] [load-bearing]: `## Fail loud`: hook-mode failures exit 2 with a stderr report; an unapproved hook run reports a notice rather than silently skipping; an unapproved diff-gate run is refused rather than reported clean; the hook's broad `except Exception` reports and re-raises outside hook mode and carries the `fail-loud.bare-except-ok` token with a reason.
  - spec citation: `config/architecture/ARCHITECTURE.md:25-42`
- **M7** [mandate]: `## No completeness claims`: the spec's population claims are backed by recipes or the executed census in `docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/`.
  - spec citation: `config/architecture/ARCHITECTURE.md:225-235`
- **M8** [mandate]: The rewritten Trust boundary paragraph keeps `## Host detectors and call sites` consistent, and its closing `No row: enforced by` line (`:182`) gains the two new test files.
  - spec citation: `config/architecture/ARCHITECTURE.md:175-182`
- **M9** [mandate]: `## POSIX paths`: the store key is `RepoTree(repo).root.as_posix()` (Decision 2 quotes `ARCHITECTURE.md:58`).
  - spec citation: `config/architecture/ARCHITECTURE.md:56-65`
- **M10** [mandate]: `## Prose names no host`: the new skill prose and the notice and refusal messages name no host repository, path or section.
  - spec citation: `config/architecture/ARCHITECTURE.md:201-209`
- **M11** [mandate] [load-bearing]: `## Single point of definition`: `MandateRegistry.host_rows` is the one host-row selector, the store is read through the one loader, and `write_approval` is named adjacent to `save_baseline` with a reason for not sharing a helper.
  - spec citation: `config/architecture/ARCHITECTURE.md:262-275`
- **S1** [shape_fit] [load-bearing]: `read_store` is an existence check plus `load_model_file(path, ApprovalStore, subject="approval store", fmt="json")` (`loader.py:43-77`); it adds no second load/parse/validate path.
  - spec citation: `plugins/arch-compliance/python/acf/loader.py:43-77`
- **S2** [shape_fit] [load-bearing]: `MandateRegistry.host_rows` becomes the one selector of host rows; `scan_host_ast_file` (`host.py:162-166`), `scan_host_guards` (`host.py:192-194`) and `acf.approval` consume it, and no other code in the python or hooks trees selects host rows to run.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/host.py:162-166`
- **S3** [shape_fit]: `acf-allow` follows the `acf.cli_<name>:main` console-script shape in `pyproject.toml` `[project.scripts]`.
  - spec citation: `pyproject.toml:18-20`
- **S4** [sweep] [load-bearing]: The executed census `docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/host_row_gate_tests.py` (committed output `host_row_gate_tests.out`) lists every test function that runs a gate with host rows; section 6.1 gives each a disposition.
  - spec citation: `docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/host_row_gate_tests.py`
- **S5** [sweep]: Section 4.7's prose table covers the tracked prose that states when either gate runs host code, how CI invokes the diff gate, or which exit codes the hook uses.
  - spec citation: `None`
- **S6** [sweep] [load-bearing]: Section 5 lists the runtime files that change: `approval.py` (new), `cli_allow.py` (new), `registry.py`, `detectors/host.py`, `posttooluse_gate.py`, `cli_check_diff.py`, `hooks.json`; the mechanism needs no other runtime file.
  - spec citation: `None`
- **S7** [shape_fit]: The hook notice reuses the existing output channels (`additionalContext`, stderr) plus the documented `systemMessage` field rather than inventing a second reporting mechanism.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:130-147`
- **S8** [shape_fit]: `write_approval` is adjacent to, not a duplicate of, `save_baseline` (`baseline.py:68-75`): different file owner, concurrency and error type.
  - spec citation: `plugins/arch-compliance/python/acf/baseline.py`
- **S9** [shape_fit] [load-bearing]: `--trusted-checkout` is the one new way to run host rows without an approval; no existing flag, environment variable or config key already bypasses or configures host-row execution in either gate.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py`
- **H1** [mechanism_justification] [load-bearing]: A content-bound record outside the working tree is needed rather than a rule on `.acf/enabled`: a marker rule cannot record which code was approved, so a checked-out branch that changes detector bytes runs under an unchanged marker.
  - spec citation: `None`
- **H2** [mechanism_justification] [load-bearing]: Binding the approval to a fingerprint of rows and named-file bytes is necessary so a changed branch re-prompts; a per-repository flag would approve future code.
  - spec citation: `None`
- **H3** [mechanism_justification] [load-bearing]: An unapproved hook run should run built-ins with a notice rather than block every edit, because blocking would make an unapproved repository unusable.
  - spec citation: `None`
- **H4** [mechanism_justification] [load-bearing]: An unapproved diff-gate run must be refused rather than skip host rows, because the diff gate's result is read as pass/fail and a skipped row would report a clean run; CI opts out with an explicit flag in its own workflow file rather than an environment detection.
  - spec citation: `None`
- **H5** [mechanism_justification] [load-bearing]: Source-only loading is needed to make what runs equal what was fingerprinted: Python's default `SourceFileLoader` executes an unchecked hash-based `.pyc` from `__pycache__/` without reading the source.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/host.py:78`
- **H6** [implementability] [load-bearing]: `registry.host_rows(TIER1_CALL_SITES)` covers every host row either gate can run, and `registry.host_rows(call_sites)` is empty exactly when a gate run at `call_sites` would make no host call (the runners select with `registry.active(call_sites, detection=...)` plus `is_host_detector_ref`).
  - spec citation: `plugins/arch-compliance/python/acf/detectors/host.py:162-166`
- **H7** [implementability] [load-bearing]: `_canonical(m.model_dump(mode="python"))` followed by `json.dumps(sort_keys=True, default=str)` is deterministic across processes and does not raise for any row `load_mandates` accepts (sets, non-string keys, dates, tuples in `params`).
  - spec citation: `plugins/arch-compliance/python/acf/registry.py`
- **H8** [implementability] [load-bearing]: `_scan_paths` can take a `run_host` flag and skip the three host calls without affecting built-in calls or `file_lines`/`rel_paths` (filled at `:243-250`).
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:214-295`
- **H9** [implementability] [load-bearing]: `Path.home()` reads `USERPROFILE` on Windows and `HOME` on POSIX, and `RepoTree(repo).contained(str(absolute_path))` returns non-None exactly when the path lies inside the root.
  - spec citation: `plugins/arch-compliance/python/acf/repo.py:53-59`
- **H10** [implementability]: (External) A PostToolUse hook's JSON output may carry a top-level `systemMessage` together with `hookSpecificOutput.additionalContext` on exit 0.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:137-147`
- **H11** [implementability] [load-bearing]: `approval_state` can run inside the hook's existing `load_mandates` try (`:109-113`), whose `except (AcfInputError, UnknownDetectorError)` catches its `AcfInputError`.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:109-113`
- **H12** [implementability] [load-bearing]: The hook's repository root (`resolve_repo` with stdin cwd) and `acf-allow`'s (`resolve_repo(args.repo)`) give the same `RepoTree(repo).root.as_posix()` key for the same checkout.
  - spec citation: `plugins/arch-compliance/python/acf/repo.py:32-45`
- **H13** [implementability] [load-bearing]: `importlib.util.spec_from_file_location(name, path, loader=...)` accepts a loader, and a `SourceFileLoader` subclass overriding `get_code` to `compile(self.get_data(self.path), self.path, "exec", dont_inherit=True)` executes the source even when `__pycache__/` holds an unchecked hash-based `.pyc` from other source, while keeping the module behaviour `load_host_detector` relies on (`sys.modules` registration, `getattr` of the callable).
  - spec citation: `plugins/arch-compliance/python/acf/detectors/host.py:78`
- **H14** [implementability] [load-bearing]: `require_approval` inside the diff gate's existing `try` (`cli_check_diff.py:83-100`) has its `AcfInputError` caught at `:98`, printed as `acf: <message>`, exit 1.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:83-100`
- **H15** [implementability] [load-bearing]: The hook body after `out_format` is set (`:68-72`) can be wrapped in one `try/except Exception` that returns 2 in hook format and re-raises otherwise, and the `fail-loud.bare-except-ok` token on that `except` line suppresses the repository's own `fail-loud.bare-except` finding.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:68-153`
- **H16** [implementability] [load-bearing]: `load_model_file(path, ApprovalStore, subject=..., fmt="json")` fits a pydantic model with `extra="forbid"`, `version: Literal[1]` and `repos: dict[str, ApprovalEntry]`, and turns every bad-file case into `AcfInputError`.
  - spec citation: `plugins/arch-compliance/python/acf/loader.py:43-77`
- **H17** [implementability] [load-bearing]: `acf-allow` loading the registry with `known_detectors=KNOWN_DETECTORS, llm_prompt_ids=LLM_PROMPT_IDS, repo_root=repo` refuses a missing host detector file with `UnknownDetectorError` (`registry.py:160-172`), which `acf-allow` maps to exit 1.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:160-172`
