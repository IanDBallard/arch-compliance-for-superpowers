# Adversarial design review — full detail

Spec: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md` @ `0eb992ad79fe0725a81a555a4fe04793eae7c0c8`
Kinds: defect
Outcome: **BLOCKED**
Claims: 66 · Reviewers: 4 · Converged: 2

## Blocking reasons

- load-bearing claim S6 (sweep) is REFUTED: The claim's list omits two runtime files the spec itself changes: section 4.3 adds load_gate_registry to acf/detectors/__init__.py (today it defines only KNOWN_DETECTORS, :26-52), and section 4.7 widens the except clauses in loader.py:59-66. The spec's own section 5 table lists both, so the claim contradicts the spec it summarises and its 'needs no other runtime file' is false as worded.
- load-bearing claim S12 (sweep) is REFUTED: The instance list is correct: I read every params block in config/architecture/mandates.yml (:37, :96, :112, :128), both profiles, and the tests (test_hooks.py:385-387 quoted strings; test_builtin_detectors.py:132-133 emits json.dumps values; no fixture YAML has params) - all string-keyed lists/strings/booleans. But the method is name-based: the recipe greps only '!!' tags and ISO dates, so it cannot find .nan/.inf, integer or YAML-1.1 boolean keys (on:/yes:) in nested maps, or other implicit types - which Decision 5 itself names (NaN, non-string keys) - and it does not cover the test suite the claim names. The right sweep is behavioural: load each registry and run the proposed json round-trip on every row's params.
- mandate claim M7 is REFUTED: Doctrine bars a load-bearing "no"/"none" tree claim "unless a recipe that a reader can re-run backs the quantifier". The section 7 risk row asserts the bundled profiles and mandates.yml hold no non-JSON params value ("a YAML set, date or binary value, a non-string key"), but its recipe `git grep -n "!!\|[0-9]{4}-[0-9]{2}-[0-9]{2}"` matches only explicit tags and ISO dates; it cannot detect a non-string (e.g. integer, or YAML-1.1 `on:`/`yes:`/`no:` -> bool) key, nor a `.nan`/`.inf` float, which Decision 5 (:70) also refuses. So one of the spec's population claims is not backed by its recipe, and the claim that every population claim is backed is false. Narrow fix: extend the recipe, replace it with a load-and-check census, or narrow the sentence to what the grep proves.
- implementability claim H10 is UNPROVEN: External claim about the Claude Code hooks reference, which I cannot read; the live hook emits only hookSpecificOutput.additionalContext (:138-147), and `git grep systemMessage` finds no emitter in plugin code. Not load-bearing: the notice still reaches the agent through additionalContext.

## Absorptions

- SUBSUMED: 'Mandate.is_host_row' shares responsibility 'decide whether a row runs host code' with plugins/arch-compliance/python/acf/registry.py:72-76 — The property becomes the single predicate; registry.py:74, :144, :150-152 and host.py:165, :193 consume it, as the spec proposes.
- SUBSUMED: 'MandateRegistry.host_rows' shares responsibility 'select active host rows for a set of call sites' with plugins/arch-compliance/python/acf/detectors/host.py:162-166 — Replace the inline filters at host.py:162-166 and :192-194 with host_rows; acf.approval consumes the same selector.
- SUBSUMED: 'load_gate_registry' shares responsibility 'load the registry with full gate validation (built-in detectors, prompt ids, host files)' with plugins/arch-compliance/python/acf/cli_check_diff.py:84-89 — Move the cli_check_diff call into load_gate_registry; the diff gate and acf-allow both call it.
- PARTIAL_OVERLAP: 'approval.file_digests' shares responsibility "resolve a host detector's file in the repository and refuse a missing one" with plugins/arch-compliance/python/acf/registry.py:160-172 — Extract resolve_host_detector_file(repo, detector) -> Path (parse_host_detector_ref + RepoTree.file, one error type for missing/unstat-able) called by load_mandates, load_host_detector (host.py:65-72) and file_digests; file_digests keeps only read_bytes + hash.
- SUBSUMED: '_SourceOnlyLoader' shares responsibility 'compile and execute a host detector module' with plugins/arch-compliance/python/acf/detectors/host.py:78-83 — Passed as the loader for the existing spec_from_file_location call inside load_host_detector; no second load path.

## Converged findings

- [2 reviewers: compliance, sweeper] The doctrine's opening scope paragraph (ARCHITECTURE.md:9-11) still says both gates run the registry's detectors and host guards see every changed file, unconditionally; section 4.8 rewrites only the Trust boundary paragraph.
  - evidence: `config/architecture/ARCHITECTURE.md:9-11`
- [2 reviewers: compliance, sweeper] The params-type recipe greps only YAML tags and ISO dates, so it cannot back the claim that no shipped registry holds a non-JSON params value (it misses .nan/.inf and non-string or YAML-1.1 boolean keys); a load-and-round-trip census is needed.
  - evidence: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:279`
  - evidence: `config/architecture/mandates.yml:37-38`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:74-83; plugins/arch-compliance/hooks/posttooluse_gate.py:273-294; plugins/arch-compliance/python/acf/cli_check_diff.py:82-97; plugins/arch-compliance/python/acf/cli_check_diff.py:166-182; plugins/arch-compliance/python/acf/cli_check_diff.py:204`
- reasoning: Hook: the only gate before the host runners is `enabled.is_file()` at :74-75 (ENABLED_REL, repo.py:29 `.acf/enabled`); past it the flow goes straight to load_mandates and _scan_paths, which calls scan_host_ast_file (:273-277, :283-287) and scan_host_guards (:292-294). cli_check_diff.main: :82-97 loads the registry, applies the empty-selection refusal and calls _scan_changed, which calls the host runners at :166-182 and :204. Neither path reads any state outside the working tree (grep across python/acf and hooks for any per-user store found none).

#### C2 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/hooks.json:16-27; plugins/arch-compliance/hooks/posttooluse_gate.py:32-35`
- reasoning: hooks.json registers PostToolUse with matcher `Write|Edit|MultiEdit` and command `python "${CLAUDE_PLUGIN_ROOT}/hooks/posttooluse_gate.py" --format hook` (:18, :22), i.e. in the plugin's own hooks.json, not host config. The gate's own comment at :32-35 states it 'fires on every Write/Edit in every repo once the plugin is installed'; acf-setup SKILL.md:161 confirms plugin hooks load automatically.

#### C3 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:78-83; plugins/arch-compliance/python/acf/detectors/host.py:107-108; plugins/arch-compliance/python/acf/detectors/host.py:176-178`
- reasoning: load_host_detector builds the spec via spec_from_file_location (:78) and runs `spec.loader.exec_module(mod)` (:83) in-process; _call_host calls `fn(*args, **kwargs)` (:108); scan_host_ast_file chains them (:176-178), as does scan_host_guards (:198-199). No subprocess is involved.

#### C4 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:150; plugins/arch-compliance/skills/acf-setup/SKILL.md:148; config/architecture/ARCHITECTURE.md:175-176`
- reasoning: SKILL.md:150: 'Suggest adding `.acf/` to git if the team wants hooks enabled for everyone' and that this opts every clone in; :148 frames the marker as the opt-in for host detector code; the doctrine at ARCHITECTURE.md:175-176 restates the consequence.

#### C5 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:12; plugins/arch-compliance/python/acf/detectors/host.py:83`
- reasoning: Ran `git log --diff-filter=A --format=%h -- plugins/arch-compliance/python/acf/detectors/host.py` -> 8677e45. Ran `git grep -n "importlib\|exec_module\|runpy" 8677e45^ -- plugins/arch-compliance/python plugins/arch-compliance/hooks` -> no output (rc=1). At HEAD the only matches are in host.py (:12, :78, :81, :83). At 8677e45^ the only process launches were subprocess calls to git and the plugin's own Node scanner, not repository-module imports.

#### C6 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:130-147; plugins/arch-compliance/hooks/posttooluse_gate.py:298-306; plugins/arch-compliance/python/acf/detectors/host.py:138-145`
- reasoning: _to_findings copies hit.message into Finding.message (host.py:144); _format_findings interpolates f.message into each line (:304); in hook format that text goes to stderr with return 2 on BLOCK (:130-133), otherwise into hookSpecificOutput.additionalContext (:137-147).

#### C7 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:91; plugins/arch-compliance/hooks/posttooluse_gate.py:107; plugins/arch-compliance/hooks/posttooluse_gate.py:113; plugins/arch-compliance/hooks/posttooluse_gate.py:120; plugins/arch-compliance/hooks/posttooluse_gate.py:249; plugins/arch-compliance/python/acf/exceptions.py:1-29`
- reasoning: Four `return 1` at :91 (mandates missing), :107 (ImportError), :113 (AcfInputError/UnknownDetectorError), :120 (AcfInputError/DetectorPackError/UnknownDetectorError), none conditioned on out_format. `abs_path.read_text(encoding="utf-8")` at :249 runs inside _scan_paths; its UnicodeDecodeError is a ValueError, not an AcfError subclass (exceptions.py: all ACF errors derive from AcfError(Exception)), so the :118 except tuple misses it and the uncaught exception prints a traceback and exits with status 1 in CPython.

#### C8 — UNPROVEN
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:131-133 (in-repo half only); external hooks reference not reachable`
- reasoning: The in-repo half holds: the comment at :131 relies on exit 2 feeding stderr to Claude, and :133 returns 2. The external half (exit 2 -> Claude, other non-zero -> user only) rests on https://code.claude.com/docs/en/hooks, which is unavailable to me; nothing in the repo independently establishes Claude Code's handling of exit 1.

#### C9 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:31; plugins/arch-compliance/hooks/inject_constraints.py:91-92; plugins/arch-compliance/hooks/inject_constraints.py:163; plugins/arch-compliance/hooks/inject_constraints.py:170; plugins/arch-compliance/python/acf/registry.py:1-11; plugins/arch-compliance/python/acf/loader.py:9-18`
- reasoning: grep for `acf.detectors|scan_host|load_host_detector` in inject_constraints.py prints nothing. Its acf imports are acf.repo, acf.exceptions, acf.registry, acf.loader, acf.template. Followed one more level: registry imports acf.engine, acf.exceptions, acf.loader, acf.repo; loader imports acf.exceptions; template imports acf.exceptions; engine/repo/exceptions import no acf.detectors; acf/__init__.py is empty (0 bytes). The only importlib/exec_module in python/acf and hooks is in detectors/host.py. load_mandates only stats host detector files (registry.py:160-172), never imports them.

#### C10 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:221-230; plugins/arch-compliance/skills/acf-mandate/SKILL.md:136; README.md:57; plugins/arch-compliance/skills/acf-setup/SKILL.md:260`
- reasoning: Step 9 (SKILL.md:221-230) instructs running `acf-check-diff --mode worktree --call-site precommit` from the host root; acf-mandate SKILL.md:136 reminds the agent to re-run acf-check-diff; README.md:57 shows the local staged run; SKILL.md:260 additionally tells the agent to run the CLI smoke before claiming success.

#### C11 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:58-60; plugins/arch-compliance/python/acf/detectors/host.py:78-83`
- reasoning: load_host_detector does `sys.path.append(str(root))` on first load (:58-60); only the detector file itself goes through spec_from_file_location (:78), so any `import helper` inside it resolves via normal sys.path finders, including the bytecode cache. No custom meta-path finder exists in the tree.

#### C12 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:73-77; plugins/arch-compliance/hooks/hooks.json:22; plugins/arch-compliance/tests/conftest.py:10-22`
- reasoning: The reuse is real but located at host.py:74-77 (`cached = sys.modules.get(name)` ... `if mod is None:` skips the load), not :80-81 as cited (:80-81 are the no-loader raise and module_from_spec). The hook runs as a fresh `python ...posttooluse_gate.py` per event (hooks.json:22) and the diff gate is a console script, so production runs are one process each. Existing diff tests call main() in-process and isolate host-module state with the fresh_host_loader fixture (conftest.py:10-22); new in-process tests need it too or a stale module would skip the digest check.

#### C13 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:53-59`
- reasoning: RepoTree.contained resolves `root / path` (an absolute path is taken as is) and returns non-None when the result is_relative_to(root). With root at home or an ancestor, `~/.acf/approvals.json` is always contained, so check_approval yields STORE_IN_REPO; the hook then has run_host false (section 4.5) and the diff gate skips require_approval only with --trusted-checkout (section 4.6). The deferral follows.

#### C14 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:40-47; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:52-58`
- reasoning: cmd includes `str(file_path)` (the edited file's resolved path, :46) and subprocess.run passes `shell=sys.platform == "win32"` (:58), so on Windows the repository-chosen file name is interpreted by cmd.exe.

#### C15 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:68-72; plugins/arch-compliance/hooks/posttooluse_gate.py:91; plugins/arch-compliance/hooks/posttooluse_gate.py:107; plugins/arch-compliance/hooks/posttooluse_gate.py:113; plugins/arch-compliance/hooks/posttooluse_gate.py:120`
- reasoning: out_format is assigned at :68-72; all four exit-1 returns follow later in straight-line code (:91, :107, :113, :120).

#### C16 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_hooks.py:145-155; plugins/arch-compliance/tests/test_hooks.py:318-329; plugins/arch-compliance/tests/test_hooks.py:424-437; plugins/arch-compliance/tests/test_hooks.py:23-37`
- reasoning: None of the three passes --format hook or a hook_event_name payload: :424 passes `--format text`; :318 passes input="" so _maybe_read_stdin_json returns None -> text; :145 passes no stdin (_run input=None) and no --format -> text unless inherited stdin carries hook JSON, which pytest capture does not provide. Each asserts returncode == 1, so they stay valid when only hook mode changes.

#### C17 — SURVIVED
- evidence: `config/architecture/mandates.yml:9-207; .github/workflows/ci.yml:40`
- reasoning: `grep -n "detector: .*\.py:"` on mandates.yml prints nothing; every detector value is a built-in id or a `.py` path without a colon on a `detection: manual` row (:152-207), so is_host_detector_ref (registry.py:29-30) is false for all. The CI step at ci.yml:40 is `python -m acf.cli_check_diff --repo . --base ... --call-site ci`; with no host rows check_approval is NOT_NEEDED.

#### C18 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:175-178; plugins/arch-compliance/skills/acf-setup/SKILL.md:148; plugins/arch-compliance/skills/acf-setup/SKILL.md:150`
- reasoning: The replaced prose exists at the cited lines; `git grep` for its distinctive phrases ('opts every clone', 'invocation is the opt-in', 'hooks enabled for everyone', 'opt-in for the automatic hooks') outside docs/ finds no test or code consumer, so replacing it breaks nothing. The runtime edits in sections 4.1, 4.4, 4.6 swap predicates and loaders rather than deleting behaviour (one equivalence caveat filed below).

#### C19 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:57-62; plugins/arch-compliance/python/acf/cli_check_diff.py:78-89; plugins/arch-compliance/python/acf/registry.py:92-94`
- reasoning: `--mandates` exists (:57-62) and replaces the registry path (:78-89), but the section 4.2 fingerprint covers only the rows' model_dump plus file digests, keyed by repo root; Mandate has no source field (source_path lives on MandateRegistry, registry.py:92-94, and is not dumped). So a `--mandates` file whose active host rows and files equal the default registry's matches the stored approval and runs without --trusted-checkout, and one whose selected call sites pick no host row is NOT_NEEDED. 'Needs --trusted-checkout' holds only when that file's host rows differ - a benign gap (the approved code is what runs), but the deferral and the refusal text overstate it.

#### C20 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:110; plugins/arch-compliance/python/acf/registry.py:133-138`
- reasoning: The hook calls `load_mandates(mandates_path, known_detectors=KNOWN_DETECTORS, repo_root=repo)` with no llm_prompt_ids (:110), and load_mandates checks prompt ids only when llm_prompt_ids is not None (registry.py:133). The diff gate passes LLM_PROMPT_IDS (cli_check_diff.py:84-89), and its UnknownDetectorError names the row: `active mandate {m.id!r} references unknown llm prompt id`.

#### C21 — REFUTED
- evidence: `plugins/arch-compliance/tests/test_diff_cli.py:367-376; plugins/arch-compliance/tests/test_diff_cli.py:350-364; plugins/arch-compliance/tests/test_diff_cli.py:379-393; plugins/arch-compliance/tests/test_hooks.py:440-461`
- reasoning: The conclusion (each listed test fails unseeded; :406 unaffected) holds, but the stated mechanism is wrong for :367: that test asserts `code == 0` before `_json_ids`, so after the refusal (exit 1 via the :98 handler) it fails on the exit-code assertion and never parses stdout. :350 and :379 assert `code == 1` (also satisfied by the refusal), then fail on json.loads of empty stdout as claimed. On the hook side, :440 also fails first on `returncode == 1` (no built-in BLOCK on `x = 1`) before its host assertions - contradicting the spec's companion sentence that an exit-code-only assertion 'would not show the difference'.

### Unanchored findings

- **important**: `python -m acf.cli_check_diff` (used by the plugin's own prose, this repo's CI and CLAUDE.md) puts the working directory first on sys.path, so a checkout that commits an `acf/` package runs its own code before any approval check; --trusted-checkout and acf-allow cannot gate this route, yet section 3's residual-exposure list names only the TypeScript bridge.
  - evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:228; plugins/arch-compliance/skills/acf-setup/SKILL.md:193; .github/workflows/ci.yml:40; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:60`
- **advisory**: Section 4.4 / section 3 cite `host.py:80-81` for the sys.modules reuse; the reuse is at host.py:74-77 (:80-81 are the no-loader raise and module_from_spec).
  - evidence: `plugins/arch-compliance/python/acf/detectors/host.py:74-77`
- **advisory**: The section 4.1 table replaces load_mandates' `builtin_row = m.detection in {ast,guard} and not is_host_detector_ref(...)` with `m.is_host_row`, but `not m.is_host_row` is not equivalent (it is also true for llm/grep/manual rows), so a literal substitution would stop refusing a non-built-in row that reuses a reserved built-in id.
  - evidence: `plugins/arch-compliance/python/acf/registry.py:144-149`
- **advisory**: New in-process tests (section 6.2 test_host_detectors digest refusal, section 6.4 in-process main runs) must use the fresh_host_loader fixture, or a detector module cached in sys.modules from an earlier test is reused and the first-load-only digest check never runs.
  - evidence: `plugins/arch-compliance/tests/conftest.py:10-22`

### Looked for but did not find

- any importlib/exec_module/__import__ under plugins/arch-compliance/python/acf or hooks outside detectors/host.py
- an acf import chain from inject_constraints.py (repo, exceptions, registry, loader, template, engine) reaching acf.detectors
- a host row (detector value containing ':') in config/architecture/mandates.yml
- a test or code consumer pinning the ARCHITECTURE.md trust-boundary sentence or acf-setup SKILL.md:148/:150 wording
- any per-user/home-directory state read by posttooluse_gate.py or cli_check_diff.py today
- a custom meta-path finder or import hook that would route detector helper imports through the source-only loader

## compliance

### Claim verdicts

#### M1 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:53-64; plugins/arch-compliance/tests/test_repo_tree_guard.py:12-16; plugins/arch-compliance/tests/test_repo_tree_guard.py:99; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:121; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:125; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:135`
- reasoning: Doctrine (ARCHITECTURE.md:126-130): callers hand RepoTree the string they hold and never join, resolve or compare against the root themselves. The design routes file_digests through RepoTree(repo).file(rel), the store check through RepoTree(repo).contained(str(store_path)), the key through RepoTree(repo).root.as_posix(), and acf-allow's repo through resolve_repo. The only join, `repo / MANDATES_REL`, has a constant right-hand side, which the guard does not flag (test_repo_tree_guard.py:99), and `Path.home() / STORE_REL` has left name `home`, not in the guard's ROOT_NAMES (:12). No new guarded function is hit, so the ALLOWED set (:16) needs no entry.

#### M2 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:74-83; plugins/arch-compliance/hooks/posttooluse_gate.py:30-35; plugins/arch-compliance/tests/test_repo_paths.py:95-108`
- reasoning: The no-marker return (:74-83) precedes every deferred import, and module scope imports only acf.repo (:30). The spec places acf.approval after the third-party import block and adds no module-scope import in section 4.5. The guard test runs both hooks against a marker-less host with pydantic/yaml poisoned (test_repo_paths.py:95-108); that path still returns before any approval import under this design.

#### M3 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:252-253; pyproject.toml:3; plugins/arch-compliance/.claude-plugin/plugin.json:3; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:174-180`
- reasoning: Doctrine: "A change to a skill's prose bumps the plugin version in plugin.json and pyproject.toml." Section 4.8 changes acf-setup/SKILL.md and acf-mandate/SKILL.md prose; both version files read 0.2.4 today and the spec bumps both to 0.2.5.

#### M4 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:239-241; plugins/arch-compliance/python/acf/loader.py:60; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:119`
- reasoning: The rule covers runtime subprocess text calls and prose file reads. read_store goes through load_model_file, which reads with encoding="utf-8" (loader.py:60). The other new reads are binary: file_digests uses read_bytes; _SourceOnlyLoader uses get_data and compiles bytes. No new runtime subprocess call appears in sections 4.2-4.7; test subprocesses are outside the rule's scope (ARCHITECTURE.md:241-242).

#### M5 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/exceptions.py:5; config/architecture/ARCHITECTURE.md:109-110`
- reasoning: Doctrine: every ACF exception subclasses AcfError alone. The design defines no exception class; failures are AcfInputError (exceptions.py:5, `class AcfInputError(AcfError)`) and UnknownDetectorError; the stdlib ImportError raised inside _SourceOnlyLoader is converted by the existing handler (host.py:85-93), not defined as a new class.

#### M6 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:30-31; config/architecture/mandates.yml:60; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:155-157; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:73`
- reasoning: Doctrine forbids broad `except Exception:` handlers that swallow errors "unless explicitly exempted with a reason". The new handler prints type, message and traceback and returns 2 in hook mode (re-raises otherwise) - reporting, not swallowing - and carries the fail-loud.bare-except-ok token (mandates.yml:60) with a reason. Unapproved hook runs emit a notice on additionalContext/systemMessage or stderr; unapproved diff-gate runs exit 1 with a refusal rather than reporting clean (Decision 8).

#### M7 — REFUTED
- evidence: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:279; config/architecture/ARCHITECTURE.md:227-230; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:70`
- reasoning: Doctrine bars a load-bearing "no"/"none" tree claim "unless a recipe that a reader can re-run backs the quantifier". The section 7 risk row asserts the bundled profiles and mandates.yml hold no non-JSON params value ("a YAML set, date or binary value, a non-string key"), but its recipe `git grep -n "!!\|[0-9]{4}-[0-9]{2}-[0-9]{2}"` matches only explicit tags and ISO dates; it cannot detect a non-string (e.g. integer, or YAML-1.1 `on:`/`yes:`/`no:` -> bool) key, nor a `.nan`/`.inf` float, which Decision 5 (:70) also refuses. So one of the spec's population claims is not backed by its recipe, and the claim that every population claim is backed is false. Narrow fix: extend the recipe, replace it with a load-and-check census, or narrow the sentence to what the grep proves.

#### M8 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:155-164; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:173`
- reasoning: The rewritten Trust boundary keeps the confinement and load_mandates sentences, replaces the two opt-in sentences (Decision 7 of the extension-point spec, explicitly superseded in the header), and adds the hook exit-2 rule; the neighbouring Call-site rule (:155-164) stays consistent (an empty selection is still refused; the diff gate's new approval refusal is likewise a refusal, not a clean run). Section 4.8 adds test_approval.py and test_cli_allow.py to the closing `No row: enforced by` line. One residual inconsistency outside :175-182 (the doctrine's opening paragraph) is filed as advisory.

#### M9 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:58; plugins/arch-compliance/python/acf/repo.py:51; plugins/arch-compliance/python/acf/registry.py:40-43; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:67`
- reasoning: Rule: "When persisting paths to YAML/JSON, use Path.as_posix()". The store key is RepoTree(repo).root.as_posix() (root resolved at repo.py:51). The other persisted path-like value, the `files` keys inside the fingerprint text, comes from parse_host_detector_ref, which validates a POSIX relative path (registry.py:40-43). No str(path) reaches a serialized payload.

#### M10 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:203-204; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:126; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:155; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:174-180`
- reasoning: Doctrine: "Skill prose and runtime messages name no host repository, path or section; a host reaches the gate only through its declaration". The refusal text (:126) and notice (:155) interpolate only the reason and row ids (the host's own declaration) plus the generic command names acf-allow / --trusted-checkout; the section 4.8 skill prose changes are generic.

#### M11 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:264-266; plugins/arch-compliance/python/acf/registry.py:144-154; plugins/arch-compliance/python/acf/detectors/host.py:162-166; plugins/arch-compliance/python/acf/detectors/host.py:192-194; plugins/arch-compliance/python/acf/baseline.py:68-86; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:127`
- reasoning: The lifted rule requires one canonical implementation every call site consumes. The host-row predicate, today spelled at registry.py:74, :144-154, host.py:165 and :193, is routed through Mandate.is_host_row and host_rows (section 4.1), and acf.approval uses the same selector; the diff gate and acf-allow share load_gate_registry; the store is read through load_model_file, whose failure typing Decision 9 fixes there; write_approval is named next to save_baseline (baseline.py:68-75) with the stated replace-whole vs write-in-place and AcfInputError vs BaselineError reasons. The claim holds as scoped to the diff gate and acf-allow; a skill snippet that will re-spell load_gate_registry is filed separately.

### Unanchored findings

- **important**: The acf-mandate skill's validation snippet already spells the exact call section 4.3 makes the new package helper load_gate_registry (load_mandates with KNOWN_DETECTORS, LLM_PROMPT_IDS and repo_root=repo); the spec edits that skill (only :136) but neither points the snippet at the helper nor records it as a breach, so it becomes a re-spelled copy of a package helper - the doctrine's high-frequency miss 'a check re-implemented in a skill instead of consumed from the package' (## Single point of definition records such snippets as breaches).
  - evidence: `plugins/arch-compliance/skills/acf-mandate/SKILL.md:96`
- **advisory**: The doctrine's opening scope paragraph still says the diff gate and PostToolUse hook run the registry's detectors with host guards seeing every changed file and rows running where their call_sites say; after this design host rows also need an approval or --trusted-checkout, but section 4.8 rewrites only the Trust boundary paragraph, leaving this sentence describing the old rule.
  - evidence: `config/architecture/ARCHITECTURE.md:9-12`

### Looked for but did not find

- ## No shims: no hasattr probing or `any` escapes; _SourceOnlyLoader is an explicit subclass overriding get_code - not breached.
- ## Declared, never defaulted: the store location Path.home()/.acf/approvals.json is a fixed per-user location, not a default standing in for a host declaration; acf-allow's cwd fallback is the already-recorded resolve_repo fallback (ARCHITECTURE.md:192-193) - not breached.
- ## Build artifacts, ## Fail-loud ratchet, ## Facade sinks, ## FSM transitions: built-in detector behaviour unchanged (the hook still runs built-ins when unapproved) - not touched.
- ## Frozen ledger format: the design does not touch LedgerRow or LedgerAmendment - not touched.
- ## Soft fail-loud smells / ## React boundaries: no LLM-judge or React surface - not touched.
- ## High-frequency misses: no stdlib mixin on an exception class; no host name in new messages; no new runtime subprocess text call; no default re-entering for a declared value. The completeness-recipe miss (M7) and the skill re-spelling miss (acf-mandate SKILL.md:96) were found and filed.

### Unstated mandates

- ## Live consumers - acf.approval adds ~10 exports (store_path, read_store, approval_rows, file_digests, fingerprint, check_approval, require_approval, write_approval, ApprovalState, Approval) and registry/detectors add is_host_row, host_rows, load_gate_registry; the doctrine requires each export to have a live non-test call site. Sections 4.2-4.6 appear to give each a consumer (hook, cli_check_diff, cli_allow), but the spec never names the section, and section 4.3 only says acf-allow 'writes the approval' without naming write_approval as the call.
- ## Scoped refactor - the spec changes acf-mandate/SKILL.md and introduces load_gate_registry; the section asks for removing non-contractual patterns in code paths being changed, which here is the snippet at acf-mandate/SKILL.md:96, on which the spec is silent.

## sweeper

### Claim verdicts

#### S1 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/loader.py:43-77; plugins/arch-compliance/python/acf/baseline.py:78-86`
- reasoning: load_model_file (loader.py:43-77) is the single load-parse-validate-refuse path: it calls require_file itself (:58) and raises AcfInputError on OSError, YAML/JSON parse errors and ValidationError. load_baseline (baseline.py:86) already uses exactly the split the spec proposes for read_store - caller decides absence, then load_model_file(path, Model, subject=..., fmt="json"). read_store as specified adds only an is_file() check returning the default ApprovalStore, so no second parse/validate path is created (require_file merely repeats the is_file check, harmless).

#### S2 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:192-194; plugins/arch-compliance/python/acf/cli_check_diff.py:204; plugins/arch-compliance/hooks/posttooluse_gate.py:292-294`
- reasoning: Grepped the plugins tree for is_host_detector_ref, parse_host_detector_ref and .active(. Only host.py:162-166 (ast) and host.py:192-194 (guard) select host rows to run; the diff gate (cli_check_diff.py:167-182, :204) and the hook (posttooluse_gate.py:273-294) reach host rows only through those two runners. Every other .active( call selects a built-in by detector id (posttooluse_gate.py:238-239, :289; cli_check_diff.py:129-130, :184-188), and cli_check_diff.py:91 is the empty-selection check over all ast/guard rows, not a host-row selector. registry.py:144-160 classifies rows for validation and runs nothing. No other exec_module/importlib host loading exists outside host.py in the python and hooks trees.

#### S3 — SURVIVED
- evidence: `pyproject.toml:18-20; plugins/arch-compliance/python/acf/cli_check_diff.py:35`
- reasoning: [project.scripts] holds acf-check-diff = "acf.cli_check_diff:main" and acf-check-llm = "acf.cli_check_llm:main", and cli_check_diff.py:35 defines main(argv: list[str] | None = None) -> int. acf-allow = "acf.cli_allow:main" with the same main signature follows that shape.

#### S4 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_diff_cli.py:311-340; plugins/arch-compliance/tests/test_hooks.py:373-397; plugins/arch-compliance/tests/test_registry.py:82`
- reasoning: Independently ran the shape search \.py:[A-Za-z_{] over the tests trees: hits are test_diff_cli.py:316/:326 (inside _host_rows), test_hooks.py:379 (inside _host_row), many lines in test_host_detectors.py (direct load_host_detector / scan_host_ast_file / scan_host_guards calls, never a gate), and test_registry.py:82/:110/:126 (load_mandates only). Fixture YAML files hold no '.py:' detector. test_builtin_detectors.py:185 calls cli_check_diff.main but with built-in rows only. The gate-running tests using the builders are test_diff_cli.py:350/:367/:379 and test_hooks.py:406/:440/:464/:488, matching host_row_gate_tests.out. The census is behavioural (detector-shape match plus helper expansion), not a test-name search.

#### S5 — REFUTED
- evidence: `config/architecture/ARCHITECTURE.md:9-11; config/architecture/ARCHITECTURE.md:159-162; plugins/arch-compliance/skills/acf-setup/SKILL.md:215; docs/guides/SUPERPOWERS_COMPLEMENT.md:70; README.md:121`
- reasoning: The prose table is section 4.8 (the claim says 4.7). Swept tracked prose for acf-check-diff, cli_check_diff, host guard, host detector, .acf/enabled and exit codes. Prose stating when the gates run host code or how CI invokes the diff gate that the table does not cover: ARCHITECTURE.md:9-11 ('The CI diff gate and the PostToolUse hook run the registry's detectors ... host guards see every changed file'); ARCHITECTURE.md:159-162 (hook 'runs rows declaring hook'; acf-check-diff 'runs only rows that are active ... and declare that site'); acf-setup SKILL.md:215 (how CI and pre-commit invoke the gate); acf-setup SKILL.md:24 (step-9 summary line); SUPERPOWERS_COMPLEMENT.md:70 and README.md:121 (smoke runs expecting the gate to fail/pass). Each still states the gates run host rows without an approval condition.

#### S6 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/detectors/__init__.py:1-52; plugins/arch-compliance/python/acf/loader.py:59-66`
- reasoning: The claim's list omits two runtime files the spec itself changes: section 4.3 adds load_gate_registry to acf/detectors/__init__.py (today it defines only KNOWN_DETECTORS, :26-52), and section 4.7 widens the except clauses in loader.py:59-66. The spec's own section 5 table lists both, so the claim contradicts the spec it summarises and its 'needs no other runtime file' is false as worded.

#### S7 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:130-147`
- reasoning: The hook already has two agent-facing channels: stderr on exit 2 (:130-133) and hookSpecificOutput.additionalContext (:137-147). systemMessage has no existing use (grep), so it is a new key on the same JSON object printed at :138-147, not a separate reporting mechanism. Text/json formats keep stdout for findings (:127-128, :149), so routing the notice to stderr reuses the existing stderr channel.

#### S8 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/baseline.py:68-75; plugins/arch-compliance/python/acf/adr/ledger.py:207; plugins/arch-compliance/python/acf/adr/run_detail.py:185`
- reasoning: Grepped the python tree for os.replace, write_text, write_bytes, mkstemp and append-mode opens: writers are save_baseline (write in place, BaselineError), the ledger (append) and run_detail (write_text); none writes atomically via temp file + os.replace, and there is no shared write helper that write_approval would duplicate. Distinct owner, error type and write discipline make 'adjacent' hold.

#### S9 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:36-74; plugins/arch-compliance/python/acf/judge.py:66-95`
- reasoning: The diff gate's flags are --mode, --base, --repo, --mandates, --call-site, --json (cli_check_diff.py:36-74); the only environment variables read anywhere in the package are ACF_JUDGE_PROVIDER/ACF_JUDGE_MODEL and provider API keys for the LLM judge (judge.py:66-95). The hook's only switch is .acf/enabled (posttooluse_gate.py:74-83), which turns host-row execution on, never on without an approval since no approval exists today. --call-site and row call_sites/status select which rows run but bypass nothing. No existing flag or variable does --trusted-checkout's job.

#### S10 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:70-76; plugins/arch-compliance/python/acf/registry.py:144-154`
- reasoning: _row_shape returns early unless detection is ast/guard (:72-73), so host = is_host_detector_ref(...) (:74) equals detection in {ast,guard} and is_host_detector_ref, the proposed is_host_row: no behaviour change. load_mandates:144 computes builtin_row = detection in {ast,guard} and not is_host_detector_ref, and :150-152 repeat both halves. Caveat: builtin_row is not simply 'not m.is_host_row' (it still needs the detection-set test, since llm/grep/manual rows are neither), so the table's 'After' cell (m.is_host_row) abbreviates; the predicate itself remains single-sourced with unchanged behaviour.

#### S11 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:84-89; plugins/arch-compliance/python/acf/judge.py:11-17; plugins/arch-compliance/python/acf/detectors/__init__.py:24`
- reasoning: cli_check_diff.py:84-89 is the only load_mandates call passing known_detectors + llm_prompt_ids + repo_root together; the hook (posttooluse_gate.py:110) passes no prompt ids, and cli_check_llm.py:54 and inject_constraints.py:104 pass neither. acf.judge imports httpx (:11) and acf.registry (:16) but not acf.detectors, and acf.detectors imports acf.registry only (:24), so a function-local import of acf.judge inside acf.detectors creates no cycle and keeps httpx out of the hook's module-level import of acf.detectors (posttooluse_gate.py:94).

#### S12 — REFUTED
- evidence: `config/architecture/mandates.yml:37-38; plugins/arch-compliance/profiles/python-service/mandates.yml:57-60; plugins/arch-compliance/tests/test_hooks.py:385-387; plugins/arch-compliance/tests/test_builtin_detectors.py:130-134`
- reasoning: The instance list is correct: I read every params block in config/architecture/mandates.yml (:37, :96, :112, :128), both profiles, and the tests (test_hooks.py:385-387 quoted strings; test_builtin_detectors.py:132-133 emits json.dumps values; no fixture YAML has params) - all string-keyed lists/strings/booleans. But the method is name-based: the recipe greps only '!!' tags and ISO dates, so it cannot find .nan/.inf, integer or YAML-1.1 boolean keys (on:/yes:) in nested maps, or other implicit types - which Decision 5 itself names (NaN, non-string keys) - and it does not cover the test suite the claim names. The right sweep is behavioural: load each registry and run the proposed json round-trip on every row's params.

### Unanchored findings

- **advisory**: After this design three places resolve a host row's detector file through RepoTree.file and refuse a missing one: load_mandates (UnknownDetectorError), load_host_detector (UnknownDetectorError) and the new approval.file_digests (AcfInputError) - the same missing-file condition gets a different error type depending on the caller; one helper (e.g. registry.resolve_host_detector_file(repo, detector) -> Path) raising one type would serve all three.
  - evidence: `plugins/arch-compliance/python/acf/registry.py:160-172`
- **advisory**: The doctrine's opening scope paragraph states unconditionally that the CI diff gate and PostToolUse hook run the registry's detectors and that host guards see every changed file; the design falsifies this but section 4.8 edits only the Trust boundary paragraph (:175-182).
  - evidence: `config/architecture/ARCHITECTURE.md:9-11`
- **advisory**: test_repo_paths.py allowlists, by exact text, the posttooluse_gate docstring line naming config/architecture/mandates.yml; section 4.5.6 rewrites that docstring (:9-14), and acf-allow's --help may name the same path, yet test_repo_paths.py is neither in the section 5 change surface nor in the section 6.5 guard list (only :81-108). Rewording that line or a new help string fails test_host_config_dir_has_one_code_owner.
  - evidence: `plugins/arch-compliance/tests/test_repo_paths.py:47-49`

### Looked for but did not find

- An existing per-user / out-of-repo state store: searched Path.home, expanduser, USERPROFILE across *.py; none
- An existing file-fingerprint or content-hash helper: searched sha256, hashlib, digest in plugins/ and scripts/; only the module-name hash at host.py:73
- An existing atomic-write helper (temp file + os.replace): searched os.replace, mkstemp, NamedTemporaryFile, write_text, write_bytes, append-mode open in the python tree; none
- An existing bypass/config for host-row execution: searched os.environ, getenv, ACF_ and argparse flags in cli_check_diff and the hook; only the LLM judge env vars and .acf/enabled
- Other code that loads host modules: searched exec_module, importlib, runpy, load_host_detector, scan_host across *.py; only host.py, the two gates, tests and the evidence probe
- A prior on-record rejection of a local approval store: searched HOST_DETECTOR_EXTENSION_POINT.md for opt-in/exit text; :65 accepted hand runs as residual, which the spec names as the superseded Decision 7

### Relationships

- SUBSUMED: `Mandate.is_host_row` — responsibility `decide whether a row runs host code` — existing `plugins/arch-compliance/python/acf/registry.py:72-76`
  - resolution: The property becomes the single predicate; registry.py:74, :144, :150-152 and host.py:165, :193 consume it, as the spec proposes.
- SUBSUMED: `MandateRegistry.host_rows` — responsibility `select active host rows for a set of call sites` — existing `plugins/arch-compliance/python/acf/detectors/host.py:162-166`
  - resolution: Replace the inline filters at host.py:162-166 and :192-194 with host_rows; acf.approval consumes the same selector.
- SUBSUMED: `load_gate_registry` — responsibility `load the registry with full gate validation (built-in detectors, prompt ids, host files)` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:84-89`
  - resolution: Move the cli_check_diff call into load_gate_registry; the diff gate and acf-allow both call it.
- PARTIAL_OVERLAP: `approval.file_digests` — responsibility `resolve a host detector's file in the repository and refuse a missing one` — existing `plugins/arch-compliance/python/acf/registry.py:160-172`
  - resolution: Extract resolve_host_detector_file(repo, detector) -> Path (parse_host_detector_ref + RepoTree.file, one error type for missing/unstat-able) called by load_mandates, load_host_detector (host.py:65-72) and file_digests; file_digests keeps only read_bytes + hash.
- ADJACENT: `approval.read_store` — responsibility `load and validate a JSON input file into a pydantic model` — existing `plugins/arch-compliance/python/acf/baseline.py:86`
  - resolution: None - both consume load_model_file.
  - non-merge: Both are thin callers of the shared loader with different models and subjects; neither reimplements loading.
- ADJACENT: `approval.write_approval` — responsibility `persist a pydantic model as JSON` — existing `plugins/arch-compliance/python/acf/baseline.py:68-75`
  - resolution: None.
  - non-merge: save_baseline writes an in-repo artifact in place raising BaselineError; write_approval rewrites a per-user, concurrently shared file atomically via os.replace raising AcfInputError - different discipline, owner and error type.
- SUBSUMED: `_SourceOnlyLoader` — responsibility `compile and execute a host detector module` — existing `plugins/arch-compliance/python/acf/detectors/host.py:78-83`
  - resolution: Passed as the loader for the existing spec_from_file_location call inside load_host_detector; no second load path.

### Two-owner counts

- resolve a host detector file in the repository and refuse a missing one: 3
- load the mandates registry with built-in detector validation: 2

### Document conflicts

- `config/architecture/ARCHITECTURE.md:9` (contradicts): The CI diff gate and the PostToolUse hook run the registry's detectors on changed `.py`, `.ts` and `.tsx` files anywhere in the repository, host guards see every changed file inside the repository
- `config/architecture/ARCHITECTURE.md:175` (contradicts): The PostToolUse hook runs host code only when `.acf/enabled` exists; committing `.acf/` therefore opts every clone in. `acf-check-diff` runs host code only when the host's own pre-commit or CI configuration invokes it, and that invocation is the opt-in.
- `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:65` (contradicts): A person running `acf-check-diff` by hand in a checkout they do not trust is the residual case, accepted.
- `plugins/arch-compliance/skills/acf-setup/SKILL.md:148` (contradicts): `.acf/enabled` is the opt-in for the automatic hooks, host detectors included

## hardening

### Claim verdicts

#### H1 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:74-75, plugins/arch-compliance/python/acf/repo.py:29`
- reasoning: The hook's only opt-in today is `(repo / ENABLED_REL).is_file()` with ENABLED_REL = `.acf/enabled` inside the working tree. A file-existence predicate carries no content, so it cannot record which detector bytes were approved; a checkout that keeps the marker and changes detector bytes passes the identical check and the host runners at :273-294 run. Any rule on the marker inherits this, since the marker is a working-tree file that travels with checkout.

#### H2 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:78-83, plugins/arch-compliance/python/acf/detectors/host.py:176`
- reasoning: load_host_detector executes whatever bytes the named file holds at run time (spec_from_file_location -> exec_module), invoked per row by each runner (:176, :198). A per-repository flag carries no content, so it would cover arbitrary later bytes; only a value derived from rows plus file bytes changes when they change. Rows matter too: a changed `detector` or `params` changes what runs (params reach the host callable at :178/:199).

#### H3 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/hooks.json:18-22, plugins/arch-compliance/hooks/posttooluse_gate.py:130-133`
- reasoning: The hook fires on every Write|Edit|MultiEdit (hooks.json:18), and exit 2 is the hook-format 'blocking feedback' channel (:131). Refusing an unapproved repository would put blocking feedback on every edit until acf-allow runs; running built-ins and reporting skipped rows keeps the gate loud (skip without notice would be silent - the spec requires the notice). 'Unusable' overstates it (PostToolUse exit 2 does not undo the edit), but the trade-off is written and sound.

#### H4 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:90-96, .github/workflows/ci.yml:40`
- reasoning: The diff gate already refuses an empty selection with 'refusing to report a clean run' (:90-96), and its result is the 0/1 exit code (:111-113). Skipping host rows would yield exit 0 with no findings, indistinguishable from a clean pass, so refusing matches precedent. CI invokes the gate from a committed workflow line (ci.yml:40), so adding `--trusted-checkout` there puts the opt-in in a host-controlled file without environment sniffing.

#### H5 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:78, plugins/arch-compliance/python/acf/detectors/host.py:83`
- reasoning: host.py:78 calls spec_from_file_location with no loader, so the default SourceFileLoader is used, whose get_code consults __pycache__/. Ran the committed probe (python -I, temp dir, self-deleting): 'default loader runs: pyc' / 'source-only loader runs: source'. An unchecked-hash .pyc is never compared against its source, so a branch committing one runs code the fingerprint never saw; compiling from source closes this at rung 1 (bytecode never consulted).

#### H6 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:79-83, plugins/arch-compliance/python/acf/registry.py:110-122`
- reasoning: _row_shape refuses any active ast/guard row declaring no Tier-1 site (:79-83), and active(cs) keeps active rows whose call_sites intersect cs (:117-122 via runs_at :67-68). Every active host row selected for any call-site set is therefore in host_rows(TIER1_CALL_SITES), so the hook (HOOK_CALL_SITES), the diff gate ({ci} or {precommit}) and acf-allow fingerprint the same row set from the same file; call_sites only gates NOT_NEEDED. The registry object model is identical whether or not llm_prompt_ids is passed (prompt-id validation only refuses, never filters, :133-138).

#### H7 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:61, plugins/arch-compliance/python/acf/loader.py:64`
- reasoning: With Decision 5 enforced, every params value is str/int/float/bool/None/list/str-keyed dict. Temp-dir experiment: the proposed predicate refused YAML set, date, timestamp, binary, nested int and bool keys, .nan, 1.0e+400 and a recursive anchor, and passed JSON-native values. All other Mandate fields are str, Literal or list[str], so model_dump(mode='json') with sort_keys=True has only str keys and cannot raise TypeError on key sorting; a YAML integer over the digit limit already fails inside yaml.safe_load at loader.py:64 (ValueError observed). No hash-seeded ordering survives sort_keys, and lists keep YAML order.

#### H8 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:243-250, plugins/arch-compliance/python/acf/enforcement.py:38-44`
- reasoning: rel_paths and file_lines are filled at :243-250 before any host call; the built-in calls (:252-272, :281, :289-291) read only text, rel and rel_paths. scan_host_guards adds flagged files to file_lines (host.py:201-210) only for its own host findings; make_line_lookup reads file_lines for exemption lookups of the findings it is handed, so skipping the three host calls changes nothing for built-in findings.

#### H9 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:51, plugins/arch-compliance/python/acf/repo.py:56-59`
- reasoning: On the installed Python 3.13, Path.home() is cls('~').expanduser(), delegating to os.path.expanduser: USERPROFILE on Windows, HOME on POSIX (pwd fallback), raising RuntimeError when the result still starts with '~' (inspected via inspect.getsource). In contained(), `self.root / abs_path` yields abs_path, which is resolved and tested with is_relative_to against the resolved root (:51), so non-None exactly for paths inside the root; a symlinked ~/.acf pointing into the repository resolves inside and is caught.

#### H10 — UNPROVEN
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:138-147`
- reasoning: External claim about the Claude Code hooks reference, which I cannot read; the live hook emits only hookSpecificOutput.additionalContext (:138-147), and `git grep systemMessage` finds no emitter in plugin code. Not load-bearing: the notice still reaches the agent through additionalContext.

#### H11 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:111, plugins/arch-compliance/python/acf/loader.py:72-77`
- reasoning: The except at :111 names AcfInputError and UnknownDetectorError. check_approval's possible failures are all specified to map to AcfInputError: store_path's RuntimeError, file_digests' None/OSError, and read_store through load_model_file (which already maps ValidationError at :72-77; Decision 9 adds decode/parse errors). NOT_NEEDED is decided before any store read, so a host-row-free registry never touches the home directory. (The claim names `approval_state`; the spec's function is `check_approval` - a naming slip, not a missing hook.)

#### H12 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:40-44, plugins/arch-compliance/hooks/posttooluse_gate.py:156-160`
- reasoning: Both routes end in Path.resolve(): `explicit.resolve()`, `Path(stdin_cwd).resolve()` or `Path.cwd().resolve()` (repo.py:40-44), then RepoTree re-resolves (:51); acf-allow uses resolve_repo(args.repo) as cli_check_diff.py:76 does. Experiment: Path('c:/users/iball').resolve() -> 'C:\Users\iball', so Windows case/drive differences normalise to on-disk case. A subdirectory stdin cwd fails the marker check at :74-75 (no host run); acf-allow from a subdirectory fails registry load (missing mandates). Neither writes a wrong key.

#### H13 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:78-83, docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/pyc_probe.py:29-35`
- reasoning: inspect.signature(importlib.util.spec_from_file_location) is (name, location=None, *, loader=None, submodule_search_locations=...), so a loader is accepted. Running the probe confirmed a SourceFileLoader subclass overriding get_code runs the source while a hash-unchecked .pyc of other code sits in the cache. sys.modules registration and getattr are done by host.py itself (:82, :84), not the loader; module_from_spec/exec_module come from the base class, so that behaviour is kept. A three-argument constructor needs a trivial __init__ override.

#### H14 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:98-100, plugins/arch-compliance/python/acf/cli_check_diff.py:90-97`
- reasoning: The try opens at :83 and wraps registry load, the selection refusal (:90-96) and _scan_changed (:97); the handler at :98 names AcfInputError, prints f'acf: {exc}' to stderr (:99) and returns 1 (:100). Placing require_approval after the selection refusal and before _scan_changed is inside that region.

#### H15 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/python_pack.py:62, plugins/arch-compliance/python/acf/enforcement.py:32`
- reasoning: The bare-except finding is reported at node.lineno of the ExceptHandler (python_pack.py:62, flagged by is_bare_or_exception :76-81), i.e. the `except` line; apply_registry drops a finding whose line matches `(?:#|//)\s*<token>\s*:\s*(\S.*)$` with a non-empty reason (enforcement.py:32, :65), and mandates.yml:60 declares fail-loud.bare-except-ok for that row. `except Exception` does not catch SystemExit/KeyboardInterrupt, so argparse exits are unaffected. The ratchet that also counts handlers is unenforced in this repository (mandates.yml:94).

#### H16 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/loader.py:59-66, plugins/arch-compliance/python/acf/loader.py:70-77`
- reasoning: Today read_text's UnicodeDecodeError (a ValueError, not OSError) escapes the :61 handler. Experiments: json.loads of 5000 digits -> ValueError (digit limit); json.loads('['*100000) -> RecursionError; yaml.safe_load of a 5000-digit int -> ValueError; yaml.safe_load('['*5000) -> RecursionError - none caught today. Both try blocks wrap only the read and parse calls; the model_validate calls sit in separate try blocks catching only ValidationError, so no validation bug is masked.

#### H17 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:168-172, plugins/arch-compliance/python/acf/registry.py:139-143`
- reasoning: When known_detectors is passed (:139), every active ast/guard host row is checked: without repo_root it raises AcfInputError (:155-159); with repo_root, RepoTree.file returning None raises UnknownDetectorError (:168-172), and a stat OSError raises it too (:163-167). Inactive rows are skipped (:142-143), and approval_rows holds only active rows. acf.judge imports httpx at module scope (judge.py:11), so a function-local import is needed to keep it out of the hook, as the spec states.

#### H18 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:85-92, plugins/arch-compliance/python/acf/detectors/host.py:81-83`
- reasoning: exec_module calls get_code before executing anything, so an ImportError raised inside get_code means no module code runs; that ImportError is inside the try (:76-84), and the BaseException handler (:87) pops the sys.modules entry this call registered (:88-89) and raises UnknownDetectorError whose message includes 'ImportError: changed since approval' via _describe. Reading once and compiling those same bytes leaves no check-to-compile window.

#### H19 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:176, plugins/arch-compliance/python/acf/registry.py:79-83`
- reasoning: Both runners resolve each row's file via load_host_detector (:176, :198); the digest key must be the detector path from parse_host_detector_ref (not the scanned-file `path` parameter of scan_host_ast_file) - the spec's `rel_path` is ambiguous there but implementable by parsing mandate.detector, as file_digests does. Every row a runner selects is an active host row, which by registry.py:79-83 declares a Tier-1 site, so it is in approval_rows and its key exists. Under NOT_NEEDED, host_rows(call_sites) is empty, so the runners' host_rows(call_sites, detection=...) selections are empty too, even though Approval.digests is {} rather than None.

#### H20 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:80-83, plugins/arch-compliance/python/acf/loader.py:70-73`
- reasoning: AcfInputError subclasses AcfError(Exception), not ValueError (acf/exceptions.py), so pydantic does not wrap it into ValidationError; it escapes model_validate exactly as _row_shape's raise at :80-83 does, and load_model_file catches only ValidationError (:72). Experiment with pydantic 2.13.3 and a dict[str, Any] field: the predicate refused !!set, date, timestamp, !!binary, {1: x}, {true: x}, .nan, 1.0e+400 and a recursive anchor, and passed lists, floats, bools, nulls and str-keyed maps; a top-level int key failed in pydantic first (ValidationError, str key type).

#### H21 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/loader.py:64, plugins/arch-compliance/python/acf/registry.py:61`
- reasoning: The producer of non-JSON params is yaml.safe_load at loader.py:64, which builds date/datetime/set/bytes values that `params: dict[str, Any]` (:61) accepts unchanged (confirmed by experiment). Refusing them in the Mandate validator makes the state unconstructible at the single load path; canonicalising inside fingerprint would map date(2024,1,1) and '2024-01-01' to one value and leave every other params consumer seeing the odd type. The spec states this rationale in writing (Decision 5).

#### H22 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:111, plugins/arch-compliance/python/acf/cli_check_diff.py:98`
- reasoning: Path.home() on the installed Python 3.13 raises RuntimeError('Could not determine home directory.') when expanduser cannot resolve '~' (pathlib source inspected). store_path is reached only from check_approval/require_approval, which the spec places inside the try blocks whose handlers at posttooluse_gate.py:111 and cli_check_diff.py:98 name AcfInputError.

### Unanchored findings

- **advisory**: The runners' new `digests: Mapping[str, str] | None = None` defaults to 'no check', so approval enforcement lives only in the two callers; a future (or forgetful) caller runs host code unchecked. A required keyword with no default would force every caller to choose, putting enforcement at rung 2.
  - evidence: `plugins/arch-compliance/python/acf/detectors/host.py:152-160`
- **advisory**: The hook-mode catch-all (Decision 10) handles the UnicodeDecodeError from reading a non-UTF-8 edited file at the boundary rather than typing that read; the spec gives no reason for not hardening the read itself, and the diff gate's identical read stays an untyped traceback.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:249`

### Looked for but did not find

- Callers of scan_host_ast_file / scan_host_guards / load_host_detector besides the hook and the diff gate (git grep): none - the two approval checks cover every current runner call
- An active host row with no Tier-1 site that would split the hook and diff-gate fingerprints: refused by registry.py:79-83
- A path by which an AcfInputError from a Mandate validator becomes a ValidationError: none (AcfInputError is not a ValueError)
- A producer of a non-str key that sort_keys=True would trip on once Decision 5 holds: none (nested int/bool keys refused by experiment; top-level refused by pydantic)
- A Windows case/drive-letter mismatch between the hook's and acf-allow's root key: resolve() canonicalises (experiment)
- A Path.home() variant on Python 3.13 that returns '~' silently instead of raising: none - expanduser raises RuntimeError
- The fail-loud ratchet counting the new exempted handler: ratchet unenforced here (mandates.yml:94)

### Mechanism traces

- **Fingerprint-bound per-user approval store checked by both gates (check_approval / require_approval)**
  - invalid state: an active host row in registry.host_rows(call_sites) is executed while approvals.json has no entry for RepoTree(repo).root.as_posix() whose fingerprint equals fingerprint(approval_rows(registry), file_digests(repo, rows))
  - producer: `plugins/arch-compliance/hooks/posttooluse_gate.py:273-294`
  - rung 3 (highest applicable 2); repairs=False
  - hardening rejected because: A marker rule cannot record which code was approved; a committed approval would reintroduce section 1.1 (no shared or team-wide approval).
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:67-68`
- **Unapproved hook run: skip host rows, run built-ins, emit notice**
  - invalid state: check_approval(repo, registry, HOOK_CALL_SITES).state in {MISSING, STALE, STORE_IN_REPO} while host_rows(HOOK_CALL_SITES) is non-empty
  - producer: `plugins/arch-compliance/hooks/posttooluse_gate.py:74-75`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: An unapproved hook run is governed by built-ins and told so, not blocked; blocking every edit would make an unapproved repository unusable.
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:72`
- **--trusted-checkout flag on acf-check-diff**
  - invalid state: a CI checkout (fresh clone, no per-user store) with host rows selected at the invoked call site, where requiring a local approval would refuse every run
  - producer: `.github/workflows/ci.yml:40`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: CI workflows pass --trusted-checkout, so the opt-in is written in the workflow file the host controls.
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:73`
- **_SourceOnlyLoader (compile source, never __pycache__)**
  - invalid state: __pycache__/ holds a .pyc for the detector file whose code object differs from compile(source) and which the default loader accepts without reading source (unchecked-hash pyc)
  - producer: `plugins/arch-compliance/python/acf/detectors/host.py:78`
  - rung 1 (highest applicable 1); repairs=False
  - hardening rejected because: What is fingerprinted is what runs; the default loader executes an unchecked hash-based .pyc without reading the source.
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:145`
- **expected_sha256 check inside _SourceOnlyLoader.get_code**
  - invalid state: sha256(bytes of the detector file at compile time) != digests[rel_path] computed by check_approval earlier in the same run
  - producer: `plugins/arch-compliance/python/acf/detectors/host.py:176`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: A file rewritten after the approval check is refused rather than run; the bytes compiled are the bytes checked.
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:69`
- **Mandate._json_params validator**
  - invalid state: row.params is not None and json.loads(json.dumps(row.params, allow_nan=False)) != row.params, or json.dumps raises
  - producer: `plugins/arch-compliance/python/acf/loader.py:64`
  - rung 1 (highest applicable 1); repairs=False
  - hardening rejected because: Refusing at load is preferred to canonicalising in the fingerprint, which would merge distinct values and leave refusal to every later consumer.
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:100`
- **load_model_file typed decode/parse failures (UnicodeDecodeError, ValueError, RecursionError)**
  - invalid state: an input file whose bytes are not UTF-8, or whose parse exceeds the int digit limit or the recursion limit, escapes load_model_file as an untyped exception
  - producer: `plugins/arch-compliance/python/acf/loader.py:60`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:74`
- **Hook-mode exit 2 and except Exception catch-all after out_format**
  - invalid state: out_format == 'hook' and the process ends with exit 1 (stderr shown only to the user) because of a gate-input failure or an exception none of the except tuples names
  - producer: `plugins/arch-compliance/hooks/posttooluse_gate.py:249`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:75`
- **STORE_IN_REPO containment refusal**
  - invalid state: RepoTree(repo).contained(str(store_path())) is not None, i.e. the approval store is one of the repository's own files
  - producer: `plugins/arch-compliance/python/acf/repo.py:40-44`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: The process environment decides where the store is; the containment check refuses the case where the store would be one of the repository's own files.
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:67`
- **write_approval temp file + os.replace**
  - invalid state: approvals.json holds a partially written document after a crash or interleaved write
  - producer: `plugins/arch-compliance/python/acf/baseline.py:68-75`
  - rung 2 (highest applicable 2); repairs=False
  - hardening rejected because: The approval store is a per-user file read and rewritten by concurrent processes, so it is replaced whole rather than written in place.
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:127`

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
- **C12** [premise] [load-bearing]: Deferral: the digest check runs at a module's first load in a process; a module already in `sys.modules` (`host.py:80-81`) is reused without re-checking, which is safe for the hook and the diff gate because each gate run is its own process.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/host.py:80-81`
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
- **C19** [premise]: Deferral: `acf-allow` approves only the default registry; a diff-gate run with `--mandates` naming another file fingerprints that file's rows and needs `--trusted-checkout`, and the refusal text says so.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:57-62`
- **C20** [premise]: Deferral: the hook loads the registry without prompt-id validation (`posttooluse_gate.py:110`), so an unknown llm prompt id reaches the approval notice, and `acf-allow` then refuses with the prompt-id error naming the row.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:110`
- **C21** [premise]: Each test listed in section 6.1 fails if left unseeded after the change: `test_diff_cli.py:350`, `:367`, `:379` parse an empty stdout as JSON after the refusal; `test_hooks.py:440`, `:464`, `:488` assert host findings or host-call log entries an unapproved run never produces; `test_hooks.py:406` runs without `.acf/enabled` and is unaffected.
  - spec citation: `plugins/arch-compliance/tests/test_diff_cli.py:350`
- **H1** [mechanism_justification] [load-bearing]: A content-bound record outside the working tree is needed rather than a rule on `.acf/enabled`: a marker rule cannot record which code was approved, so a checked-out branch that changes detector bytes runs under an unchanged marker.
  - spec citation: `None`
- **H2** [mechanism_justification] [load-bearing]: Binding the approval to a fingerprint of rows and named-file bytes is necessary so a changed branch re-prompts; a per-repository flag would approve future code.
  - spec citation: `None`
- **H3** [mechanism_justification] [load-bearing]: An unapproved hook run should run built-ins with a notice rather than block every edit, because blocking would make an unapproved repository unusable.
  - spec citation: `None`
- **H4** [mechanism_justification] [load-bearing]: An unapproved diff-gate run must be refused rather than skip host rows, because the diff gate's result is read as pass/fail and a skipped row would report a clean run; CI opts out with an explicit flag in its own workflow file rather than an environment detection.
  - spec citation: `None`
- **H5** [mechanism_justification] [load-bearing]: Source-only loading is needed so what runs equals what was approved: the default `SourceFileLoader` executes an unchecked hash-based `.pyc` from `__pycache__/` without reading the source (committed probe `docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/pyc_probe.py`, output `pyc_probe.out`).
  - spec citation: `docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/pyc_probe.py`
- **H6** [implementability] [load-bearing]: `check_approval` fingerprints `approval_rows(registry)` = `registry.host_rows(TIER1_CALL_SITES)` whatever `call_sites` is, and uses `registry.host_rows(call_sites)` only to decide `NOT_NEEDED`; since every active host row declares a Tier-1 site, the hook, the diff gate and `acf-allow` compute one fingerprint for one registry.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:17-19`
- **H7** [implementability] [load-bearing]: With `params` JSON-native (Decision 5), `json.dumps({"rows": [m.model_dump(mode="json") ...], "files": digests}, sort_keys=True, separators=(",", ":"))` is deterministic across processes and does not raise for any row `load_mandates` accepts.
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
- **H16** [implementability] [load-bearing]: Adding `UnicodeDecodeError` to the read handler (`loader.py:59-62`) and `ValueError`/`RecursionError` to the parse handler (`loader.py:63-66`) makes `load_model_file` raise `AcfInputError` for a non-UTF-8 file, an over-long JSON integer and over-deep nesting, without masking a validation bug (the `ValidationError` handling at `:67-77` is separate).
  - spec citation: `plugins/arch-compliance/python/acf/loader.py:59-66`
- **H17** [implementability] [load-bearing]: `acf-allow` loading the registry with `known_detectors=KNOWN_DETECTORS, llm_prompt_ids=LLM_PROMPT_IDS, repo_root=repo` refuses a missing host detector file with `UnknownDetectorError` (`registry.py:160-172`), which `acf-allow` maps to exit 1.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:160-172`
- **H18** [implementability] [load-bearing]: `_SourceOnlyLoader.get_code` reading `self.get_data(self.path)` once, raising `ImportError` when `expected_sha256` is set and differs, and compiling the same bytes, makes `load_host_detector` raise `UnknownDetectorError` through the existing handler (`host.py:85-93`) on a changed file without executing its module code.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/host.py:85-93`
- **H19** [implementability] [load-bearing]: `scan_host_ast_file` and `scan_host_guards` can take `digests: Mapping[str, str] | None` and pass `expected_sha256=digests[rel_path]` per row; when approved, every row they run is in `approval_rows(registry)`, so the key exists, and when `NOT_NEEDED` no host row runs.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/host.py:162-198`
- **H20** [implementability] [load-bearing]: A `Mandate` validator raising `AcfInputError` when `json.loads(json.dumps(params, allow_nan=False)) != params` (a `TypeError`, `ValueError` or `RecursionError` counting as unequal) refuses YAML sets, dates, binary values, nested integer keys and `.nan` from `yaml.safe_load`, passes JSON-native params, and its `AcfInputError` propagates out of `load_model_file` as `_row_shape`'s do.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:69-90`
- **H21** [mechanism_justification] [load-bearing]: Refusing non-JSON `params` at load (the producer) is preferred to canonicalising them in the fingerprint, because canonicalisation merges distinct values (a date and its ISO string) and leaves the refusal of odd params to every later consumer.
  - spec citation: `None`
- **H22** [implementability]: `store_path()` can map a `RuntimeError` from `Path.home()` to `AcfInputError`, which the hook's existing `except (AcfInputError, UnknownDetectorError)` (`posttooluse_gate.py:111`) and the diff gate's `except` (`cli_check_diff.py:98`) already catch.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:111`
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
- **M11** [mandate] [load-bearing]: `## Single point of definition`: `Mandate.is_host_row` is the one host-row predicate, `MandateRegistry.host_rows` the one selector, `load_gate_registry` the one gate-validation registry load for the diff gate and `acf-allow`, the store is read through the one loader (whose failure typing is fixed there, not at each caller), and `write_approval` is named adjacent to `save_baseline` with a reason for not sharing a helper.
  - spec citation: `config/architecture/ARCHITECTURE.md:262-275`
- **S1** [shape_fit] [load-bearing]: `read_store` is an existence check plus `load_model_file(path, ApprovalStore, subject="approval store", fmt="json")` (`loader.py:43-77`); it adds no second load/parse/validate path.
  - spec citation: `plugins/arch-compliance/python/acf/loader.py:43-77`
- **S2** [shape_fit] [load-bearing]: `MandateRegistry.host_rows` becomes the one selector of host rows; `scan_host_ast_file` (`host.py:162-166`), `scan_host_guards` (`host.py:192-194`) and `acf.approval` consume it, and no other code in the python or hooks trees selects host rows to run.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/host.py:162-166`
- **S3** [shape_fit]: `acf-allow` follows the `acf.cli_<name>:main` console-script shape in `pyproject.toml` `[project.scripts]`.
  - spec citation: `pyproject.toml:18-20`
- **S4** [sweep] [load-bearing]: The AST census `docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/host_row_gate_tests.py` (shape match `\.py:[A-Za-z_{]` plus current helper names, following module-level helpers and fixtures one level deep; output `host_row_gate_tests.out`) lists the tests at `0da9864` that run a gate with host rows; the `git grep -n "\.py:[A-Za-z_{]"` cross-check finds only the host-row builders the census expands from and runner-level tests in `test_host_detectors.py` and `test_registry.py`, which never run a gate.
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
- **S10** [shape_fit] [load-bearing]: `Mandate.is_host_row` becomes the one statement of the host-row predicate, consumed by `_row_shape` (`registry.py:69-76`), `load_mandates` (`registry.py:144-154`) and `host_rows`, with no behaviour change for built-in rows.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:69-76`
- **S11** [shape_fit] [load-bearing]: `load_gate_registry(repo, mandates_path)` in `acf/detectors/__init__.py` becomes the one gate-validation registry load for the diff gate (`cli_check_diff.py:84-89` today) and `acf-allow`, importing `LLM_PROMPT_IDS` from `acf.judge` inside the function so the hook's import of `acf.detectors` gains no `acf.judge`/`httpx`, and adding no import cycle.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:84-89`
- **S12** [sweep] [load-bearing]: No row `params` in `config/architecture/mandates.yml`, `plugins/arch-compliance/profiles/*/mandates.yml` or the test suite's fixtures holds a non-JSON-native value, so the new `_json_params` validator breaks no shipped registry or existing test (recipe: `git grep -n "!!\|[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}" -- config/architecture/mandates.yml plugins/arch-compliance/profiles` prints nothing).
  - spec citation: `None`
