# Adversarial design review — full detail

Spec: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md` @ `d7c6512beb31672b417e2117f074ed60bc03ba5a`
Kinds: defect
Outcome: **BLOCKED**
Claims: 40 · Reviewers: 4 · Converged: 3

## Blocking reasons

- load-bearing claim C8 (premise) is UNPROVEN: The exit-2 half is corroborated only as the repo's own belief (hook comment :131, hooks.json:2, README.md:108 all say exit 2 feeds stderr to Claude). The load-bearing other half - that any other non-zero code shows stderr to the user only, not the agent - rests solely on the external Claude Code hooks reference, which I cannot open; grepped the repo for 'shown to the user', 'non-blocking error' and similar and found nothing outside this spec. I cannot re-derive it from reachable evidence.
- load-bearing claim C10 (premise) is REFUTED: The doctrine sentence exists, but the premise 'runs host rows only when the host's own pre-commit or CI configuration invokes it' is false for the shipped plugin: the plugin's own skills instruct the agent to run acf-check-diff directly - acf-setup step 9 (:24, :222-228) runs `acf-check-diff --mode worktree --call-site precommit` from the host root, and acf-mandate's done summary (:136) asks for a re-run after enforcement changes; this repo's CLAUDE.md also has the diff gate run by hand. Any of these in a clone/checked-out contributor branch whose mandates.yml has host rows with precommit/ci sites executes that branch's detector code with no host config involved and (under this design) no approval. That is section 1.1's consequence 1 via a second route, so the deferral rests on a false premise.
- load-bearing claim C11 (premise) is UNPROVEN: The claim rests on Claude Code behaviour (a committed settings file can set env and declare hooks; folder trust governs it). The repo carries no source for it: no tracked settings file exists in the worktree and no doc or test describes folder trust. I cannot re-derive it.
- load-bearing claim S1 (shape_fit) is REFUTED: The narrow fact holds (no per-user/out-of-repository store exists: searched plugins/arch-compliance for Path.home, expanduser, XDG_, APPDATA, USERPROFILE, platformdirs, tempfile, os.replace - none). But the conclusion 'duplicates nothing' fails when swept by responsibility (load/parse/validate shape/refuse with AcfInputError naming the path) rather than by component: acf/loader.py:1-8 declares itself 'The one load-parse-validate-refuse implementation. Every input file ACF reads goes through here', and load_model_file (loader.py:43-77) does exactly what read_store's contract re-specifies: OSError -> AcfInputError naming the path (:61-62), invalid JSON -> AcfInputError (:65-66), wrong shape -> AcfInputError (:74-77). Existing consumers: registry.py:132, baseline.py:86, adr/host.py:31. The 'missing file gives {}' difference is already handled at the caller by baseline.py:78-86 ('Absence is a real state decided by the CALLER'). approval.py already depends on acf.registry (which imports pydantic and acf.loader, registry.py:7,10), so there is no import-weight reason to avoid it. Doctrine `## Single point of definition` (config/architecture/ARCHITECTURE.md:264-266) applies.
- load-bearing claim S3 (sweep) is REFUTED: The recipe's stated output is wrong: `_seed_host_rows(` matches at :391 (def), :409, :447, :471, :491 - the cited :406/:440/:464/:488 are the test-definition lines, which the grep does not print, so a reader re-running the recipe sees different numbers. The method is also a by-name sweep (the helper's name) for a by-behaviour claim ('no other test file runs the hook with host rows'): a test seeding host rows inline or via another helper is invisible to it. Re-swept by behaviour (tests that run posttooluse_gate.py; tests writing `detector: <path>.py:<callable>` rows): test_builtin_detectors.py:177-181 runs the hook but with built-in rows only (_row at :109-135 uses KNOWN_DETECTORS ids); test_diff_cli.py:316/:326 write host rows but run the diff gate; no tracked .yml fixture holds a host reference. So the four-test population is currently correct, but the recipe would not catch the next one.
- load-bearing claim H5 (implementability) is REFUTED: Mandates load via yaml.safe_load (loader.py:64) and params is dict[str, Any] (registry.py:61). SafeLoader constructs a Python set from `!!set`; pydantic model_dump(mode='json') serialises the set as a list in iteration order, which follows the string hash seed. Verified read-only: the same row under PYTHONHASHSEED=1/2/3 yielded three different list orders; sort_keys does not reorder lists. Each hook process has a random hash seed, so such a row's fingerprint differs on every run - permanent STALE (fail-safe, but approval is unattainable). Other shapes checked are deterministic (int nested keys become '1', dates become ISO strings). So 'for every loadable row' is false; fix by rejecting non-JSON-native params at load or canonicalising sets before hashing.
- implementability claim H5 is REFUTED: Mandates load via yaml.safe_load (loader.py:64) and params is dict[str, Any] (registry.py:61). SafeLoader constructs a Python set from `!!set`; pydantic model_dump(mode='json') serialises the set as a list in iteration order, which follows the string hash seed. Verified read-only: the same row under PYTHONHASHSEED=1/2/3 yielded three different list orders; sort_keys does not reorder lists. Each hook process has a random hash seed, so such a row's fingerprint differs on every run - permanent STALE (fail-safe, but approval is unattainable). Other shapes checked are deterministic (int nested keys become '1', dates become ISO strings). So 'for every loadable row' is false; fix by rejecting non-JSON-native params at load or canonicalising sets before hashing.
- implementability claim H11 is UNPROVEN: POSIX rename(2) is atomic; on Windows os.replace uses MoveFileExW(MOVEFILE_REPLACE_EXISTING), and Python documents atomicity only as a POSIX requirement. No in-repo or stdlib source line establishes Windows atomicity. The weaker property (temp file complete before rename, so readers never see a half-written store) holds. Separately, on Windows os.replace raises PermissionError if another process holds the destination open (Python's open() does not share delete). Not load-bearing.

## Absorptions

- PARTIAL_OVERLAP: 'acf.approval.read_store' shares responsibility 'load, parse, validate and refuse a JSON input file with AcfInputError naming the path' with plugins/arch-compliance/python/acf/loader.py:43 — Declare an ApprovalStore pydantic model (extra='forbid', version: Literal[1], repos: dict[str, ApprovalEntry]) and read it with load_model_file(path, ApprovalStore, subject='approval store', fmt='json'); read_store collapses to an existence check plus that call, as baseline.load_baseline (baseline.py:78-86) does. Delete the private JSON decode, shape check and OSError mapping.
- PARTIAL_OVERLAP: 'acf.approval.hook_host_rows' shares responsibility 'select the host ast/guard rows that run at a call site' with plugins/arch-compliance/python/acf/detectors/host.py:162 — Extract one selector (e.g. acf.registry.MandateRegistry.host_rows(call_sites, detection=None) returning active rows with is_host_detector_ref true) consumed by scan_host_ast_file (host.py:162-166, which then applies its language filter), scan_host_guards (host.py:192-194) and hook_host_rows (which sorts by id).

## Converged findings

- [2 reviewers: compliance, sweeper] hook_host_rows restates the runners' host-row selection (registry.active + is_host_detector_ref), so the fingerprinted and executed row sets have two owners (Single point of definition).
  - evidence: `plugins/arch-compliance/python/acf/detectors/host.py:162-166`
  - evidence: `plugins/arch-compliance/python/acf/detectors/host.py:192-194`
- [3 reviewers: refuter, compliance, hardening] Failures outside the four explicit returns (an OSError from fingerprint's stat/read_bytes, a UnicodeDecodeError or OSError elsewhere in the hook) escape the except tuple and exit 1 with a traceback, the user-only channel Decision 7 means to close.
  - evidence: `plugins/arch-compliance/python/acf/repo.py:61-64`
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:249`
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:109-113`
- [2 reviewers: compliance, sweeper] The section 4.4 prose list misses sites that state the hook runs host detectors unconditionally or exits 2 only on BLOCK: the hook docstring posttooluse_gate.py:12-14 (both), plus README.md:108, acf-setup SKILL.md:159 and hooks.json:2.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:12-14`
  - evidence: `README.md:108`
  - evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:159`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:74-83, plugins/arch-compliance/hooks/posttooluse_gate.py:117, plugins/arch-compliance/hooks/posttooluse_gate.py:273-277, plugins/arch-compliance/hooks/posttooluse_gate.py:292-294, plugins/arch-compliance/python/acf/repo.py:29, plugins/arch-compliance/python/acf/repo.py:32-44`
- reasoning: Read main() end to end: the only gate is `enabled = repo / ENABLED_REL; if not enabled.is_file(): return 0`, ENABLED_REL = `.acf/enabled` (repo.py:29). After the mandates/deps checks, _scan_paths is called unconditionally (:117) and calls scan_host_ast_file (:273-277, :283-287) and scan_host_guards (:292-294). `repo` comes from resolve_repo (--repo, stdin cwd, or process cwd), i.e. the working tree. Grepped python and hooks trees for os.environ/getenv: only judge.py reads env. No home-directory or other out-of-tree state is consulted before host code runs.

#### C2 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/hooks.json:16-27, plugins/arch-compliance/hooks/posttooluse_gate.py:32-35, plugins/arch-compliance/hooks/hooks.json:2`
- reasoning: hooks.json registers PostToolUse with matcher `Write|Edit|MultiEdit` running `python "${CLAUDE_PLUGIN_ROOT}/hooks/posttooluse_gate.py" --format hook`; this is plugin-level, not written into a host. The hook's own comment (:32-35) states it 'fires on every Write/Edit in every repo once the plugin is installed', and hooks.json:2 says it 'no-ops until the host has .acf/enabled', consistent with the claim.

#### C3 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:78-83, plugins/arch-compliance/python/acf/detectors/host.py:176, plugins/arch-compliance/python/acf/detectors/host.py:198, plugins/arch-compliance/python/acf/detectors/host.py:108`
- reasoning: load_host_detector builds a spec via importlib.util.spec_from_file_location and calls `spec.loader.exec_module(mod)` in the current process; scan_host_ast_file (:176) and scan_host_guards (:198) call it, and _call_host invokes the returned fn in-process (:108). No subprocess or sandbox. Citation drift: the spec puts exec_module at `:81`; it is at host.py:83 (:81 is module_from_spec).

#### C4 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:150, plugins/arch-compliance/skills/acf-setup/SKILL.md:148, docs/design/HOST_DETECTOR_EXTENSION_POINT.md:542`
- reasoning: SKILL.md:150 reads 'Suggest adding `.acf/` to git if the team wants hooks enabled for everyone ... committing `.acf/` opts every clone into running the host's detectors on edit.' :148 calls the marker the opt-in, host detectors included. The extension-point spec's change table (:542) records adding this text.

#### C5 — SURVIVED
- evidence: `git grep at 8677e45^ for importlib|exec_module|__import__|runpy|subprocess under plugins/arch-compliance/python and hooks; plugins/arch-compliance/python/acf/detectors/host.py:1-6; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:19, plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:52-58; plugins/arch-compliance/python/acf/loader.py:64`
- reasoning: git log --follow shows host.py introduced in 8677e45. At 8677e45^ the python/hooks trees contain no importlib/exec_module/runpy; the only subprocess users are adr/citations.py and diff.py (git) and the TS bridge, which runs the plugin's own pack (cwd=_PACK_ROOT, typescript_bridge.py:19,54); scan.ts builds its ts-morph Project with skipAddingFilesFromTsConfig; YAML is safe_load (loader.py:64). So by design no repository module was imported or executed at edit time before host rows. Caveat (unanchored finding): on Windows the TS bridge has passed the repo-controlled edited path through shell=True since before host rows, so a crafted .ts filename could already inject a command. The claim holds as a statement of what the design permitted.

#### C6 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:138-147, plugins/arch-compliance/hooks/posttooluse_gate.py:298-306, plugins/arch-compliance/hooks/posttooluse_gate.py:137-147, plugins/arch-compliance/hooks/posttooluse_gate.py:130-133`
- reasoning: _to_findings copies host `hit.message` into Finding.message (host.py:144); _format_findings writes `f.message` into each line (:304); in hook mode that text becomes `additionalContext` (:137-147) when nothing blocks, or stderr with exit 2 (:132-133) when something does.

#### C7 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:85-91, plugins/arch-compliance/hooks/posttooluse_gate.py:99-107, plugins/arch-compliance/hooks/posttooluse_gate.py:109-113, plugins/arch-compliance/hooks/posttooluse_gate.py:116-120, plugins/arch-compliance/hooks/posttooluse_gate.py:151-153`
- reasoning: Four explicit `return 1` with no out_format branch, at exactly the stated lines and catching exactly the stated exception tuples. The only other return 1 (:151-152) is guarded by `out_format != "hook"`. So these four are the explicit gate-input failure returns in hook mode. Not covered by the claim: uncaught exceptions also end in exit 1 (unanchored finding).

#### C8 — UNPROVEN
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:131, plugins/arch-compliance/hooks/hooks.json:2, README.md:108; searched repo for any in-tree statement of non-2 exit-code semantics`
- reasoning: The exit-2 half is corroborated only as the repo's own belief (hook comment :131, hooks.json:2, README.md:108 all say exit 2 feeds stderr to Claude). The load-bearing other half - that any other non-zero code shows stderr to the user only, not the agent - rests solely on the external Claude Code hooks reference, which I cannot open; grepped the repo for 'shown to the user', 'non-blocking error' and similar and found nothing outside this spec. I cannot re-derive it from reachable evidence.

#### C9 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/inject_constraints.py:31, plugins/arch-compliance/hooks/inject_constraints.py:91-92, plugins/arch-compliance/hooks/inject_constraints.py:163, plugins/arch-compliance/hooks/inject_constraints.py:170, plugins/arch-compliance/python/acf/registry.py:7-11, plugins/arch-compliance/python/acf/loader.py:11-18`
- reasoning: Recipe grep printed nothing (rc=1). Followed every import: the hook imports acf.repo, acf.exceptions, acf.registry, acf.loader, acf.template; registry.py imports only pydantic, acf.engine, acf.exceptions, acf.loader, acf.repo; loader imports yaml, pydantic, acf.exceptions; engine and repo are stdlib only; acf/__init__.py is empty. load_mandates is called without known_detectors (:104). None reaches acf.detectors or importlib.

#### C10 — REFUTED
- evidence: `config/architecture/ARCHITECTURE.md:176-178, plugins/arch-compliance/skills/acf-setup/SKILL.md:24, plugins/arch-compliance/skills/acf-setup/SKILL.md:222-228, plugins/arch-compliance/skills/acf-mandate/SKILL.md:136`
- reasoning: The doctrine sentence exists, but the premise 'runs host rows only when the host's own pre-commit or CI configuration invokes it' is false for the shipped plugin: the plugin's own skills instruct the agent to run acf-check-diff directly - acf-setup step 9 (:24, :222-228) runs `acf-check-diff --mode worktree --call-site precommit` from the host root, and acf-mandate's done summary (:136) asks for a re-run after enforcement changes; this repo's CLAUDE.md also has the diff gate run by hand. Any of these in a clone/checked-out contributor branch whose mandates.yml has host rows with precommit/ci sites executes that branch's detector code with no host config involved and (under this design) no approval. That is section 1.1's consequence 1 via a second route, so the deferral rests on a false premise.

#### C11 — UNPROVEN
- evidence: `searched the repo for a tracked .claude settings file and for 'folder trust'/'workspace trust'; only HOST_DETECTOR_LOCAL_APPROVAL.md:76 mentions it`
- reasoning: The claim rests on Claude Code behaviour (a committed settings file can set env and declare hooks; folder trust governs it). The repo carries no source for it: no tracked settings file exists in the worktree and no doc or test describes folder trust. I cannot re-derive it.

#### C12 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:58-60, plugins/arch-compliance/python/acf/detectors/host.py:78-83`
- reasoning: load_host_detector appends the repository root to sys.path (host.py:59), so a host detector can import any repo module, while only the named file is loaded via spec_from_file_location (:78). A fingerprint over row JSON plus named-file bytes (section 4.1) therefore cannot see a changed helper; the stated limitation is real. It is incomplete: compiled bytecode is a second way to change what runs without changing the fingerprint (unanchored finding).

#### C13 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:175-176, plugins/arch-compliance/skills/acf-setup/SKILL.md:150, plugins/arch-compliance/skills/acf-setup/SKILL.md:148`
- reasoning: Grepped the repo (excluding reviews and this spec) for 'opts every clone', 'every clone', 'hooks enabled for everyone', 'host detectors included': only the doctrine sentence, SKILL.md:148/:150 and the historical spec HOST_DETECTOR_EXTENSION_POINT.md. No test or code reads these sentences, so removing them breaks no consumer. Section 4.3's runtime changes modify posttooluse_gate.py rather than delete code. Precision: section 4.4 also rewrites SKILL.md:148, README.md:110 and SUPERPOWERS_COMPLEMENT.md:87, so 'removes only' understates; they are replacements, not deletions.

#### C14 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:68-72, plugins/arch-compliance/hooks/posttooluse_gate.py:91, plugins/arch-compliance/hooks/posttooluse_gate.py:107, plugins/arch-compliance/hooks/posttooluse_gate.py:113, plugins/arch-compliance/hooks/posttooluse_gate.py:120`
- reasoning: out_format is assigned at :68-72 in main()'s straight-line code, before the enabled check; all four returns (:91, :107, :113, :120) occur later in the same function scope, so the expression is available at each.

#### C15 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_hooks.py:145-155, plugins/arch-compliance/tests/test_hooks.py:318-328, plugins/arch-compliance/tests/test_hooks.py:424-436, plugins/arch-compliance/tests/test_hooks.py:23-38`
- reasoning: :145 (deps missing) calls _run with no --format and stdin=None; :318 (mandates missing) calls subprocess.run with input="", which _maybe_read_stdin_json turns into None, so out_format is text; :424 (unknown detector) passes `--format text` explicitly. None carries hook_event_name, so all three remain text-mode exit 1.

### Unanchored findings

- **important**: The fingerprint hashes detector source bytes, but load_host_detector loads via SourceFileLoader, which executes an unchecked hash-based .pyc in a committed __pycache__/ without comparing it to the source - so an approved, innocuous source file can run different committed bytecode, and `acf-allow` would print only the source hash.
  - evidence: `plugins/arch-compliance/python/acf/detectors/host.py:78`
- **important**: Hook-mode failures outside the four explicit returns still exit 1 via an uncaught traceback, invisible to the agent: a non-UTF-8 edited .py/.ts file (UnicodeDecodeError from read_text, not in the AcfInputError/DetectorPackError/UnknownDetectorError tuple) and an OSError from RepoTree.file in _collect_paths (outside any try). Decision 7 leaves these at exit 1.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:249`
- **important**: On Windows the TS bridge runs with shell=True and passes the edited file's absolute path unquoted unless it contains a space (list2cmdline renders 'C:/r/x&calc&.ts' bare), so a repo-supplied .ts filename containing '&' injects a cmd.exe command at edit time on the marker alone - a repo-controlled execution path the approval layer does not cover, qualifying the 'no repository code before host rows' premise.
  - evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:52-58`
- **important**: The plugin's own skills (acf-setup step 9, acf-mandate's re-run reminder) direct the agent to run acf-check-diff - and thus host code - in whatever checkout it is in, outside the host's pre-commit/CI; Decision 6 exempts this route from approval on the premise that only host config invokes it.
  - evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:226`
- **advisory**: The spec cites exec_module at host.py:81; it is at :83 (:81 is module_from_spec).
  - evidence: `plugins/arch-compliance/python/acf/detectors/host.py:83`

### Looked for but did not find

- any out-of-tree state (env var, home-directory file) consulted by posttooluse_gate.py before host code runs
- an import of acf.detectors, importlib or scan_host anywhere in inject_constraints.py's transitive acf imports (registry, loader, template, engine, repo, exceptions, acf/__init__.py)
- importlib/exec_module/runpy anywhere in plugins/arch-compliance/python or hooks at 8677e45^
- unsafe yaml.load in acf/loader.py (it uses safe_load at :64)
- a test or code consumer of the doctrine sentence or the SKILL.md:150 warning that removing them would break
- an in-repo statement of Claude Code's non-2 exit-code or folder-trust semantics

## compliance

### Claim verdicts

#### M1 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:53-59; plugins/arch-compliance/tests/test_repo_tree_guard.py:12-16; plugins/arch-compliance/tests/test_repo_tree_guard.py:59-66; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:93; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:62`
- reasoning: Doctrine (ARCHITECTURE.md:126-130): callers hand RepoTree the string they hold and never join, resolve or compare against the root themselves. The design reads detector files only via `RepoTree(repo).file(rel)` (spec :93) and compares the store only via `RepoTree(repo).contained(str(store_path))` (spec :62); `contained` takes an absolute path as is and resolves it, so a store inside the repo (or reaching it via symlink) is detected (repo.py:53-59). The guard flags only resolve/relative_to/is_relative_to/joinpath calls, os.path helpers, and `/` joins whose left name is repo/repo_root/root/ROOT/base/host_root with a non-constant right (test_repo_tree_guard.py:12-14, 59-66). `Path.home() / STORE_REL` (left name `home`, right an uppercase constant), `.root.as_posix()`, and `--repo` resolution via `resolve_repo` (in repo.py, which the guard skips) all pass; no new allowlist entry is needed.

#### M2 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:30-35; plugins/arch-compliance/hooks/posttooluse_gate.py:74-83; plugins/arch-compliance/tests/test_repo_paths.py:81-108; plugins/arch-compliance/tests/test_adr_import_graph.py:79-100`
- reasoning: The hook imports only `acf.repo` at module scope (posttooluse_gate.py:30); the no-marker branch returns at :83 before the deferred third-party imports at :93-98. `acf.approval` depends on `acf.registry` (pydantic), so it can only be imported after that point, which spec :86 states. `acf.repo` is unchanged, so `test_acf_repo_still_imports_without_pydantic` (test_adr_import_graph.py:79) holds. Note: the test that actually pins the no-marker path with pydantic/yaml poisoned is test_repo_paths.py:81-108 (the `plugin.one-owner-host-paths` row's own test); the spec does not name it, but the design leaves it passing.

#### M3 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:252-253; pyproject.toml:3; plugins/arch-compliance/.claude-plugin/plugin.json:3; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:135`
- reasoning: Doctrine: 'A change to a skill's prose bumps the plugin version in plugins/arch-compliance/.claude-plugin/plugin.json and pyproject.toml.' The design changes acf-setup/SKILL.md:16-25, :148, :150 and bumps both files; both currently read 0.2.4 (pyproject.toml:3, plugin.json:3), so 0.2.5 is the bump.

#### M4 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:239-241; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:96`
- reasoning: Doctrine: every subprocess call reading text declares encoding="utf-8"; every file read of prose declares its encoding. `read_store` reads with explicit `encoding="utf-8"`; `fingerprint` hashes `read_bytes()` (no decoding). The design adds no subprocess call.

#### M5 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:109-110; plugins/arch-compliance/python/acf/exceptions.py:5; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:96`
- reasoning: Doctrine: every ACF exception subclasses AcfError, no stdlib mixin. The design declares no exception class and raises only the existing `AcfInputError(AcfError)` (exceptions.py:5); `ApprovalState` is an enum, not an exception. The claim's secondary clause that registry failures are AcfInputError is imprecise: `load_mandates` raises `UnknownDetectorError` for a missing/unstat-able host detector file (registry.py:164-172, 179) - not a breach of this mandate, but it affects acf-allow's handling (unanchored finding).

#### M6 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:27-31; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:118-123; plugins/arch-compliance/python/acf/registry.py:168-172`
- reasoning: Doctrine: 'Errors must surface... Failures must not disappear.' Hook-mode gate-input failures move to exit 2, the code whose stderr reaches the agent (spec :123, posttooluse_gate.py:131). Unapproved host rows are not silently dropped: one notice reaches the agent (additionalContext / stderr on BLOCK) and the user (systemMessage), naming rows and remedy (spec :118-122). Genuine failures (e.g. missing host detector file) still fail as gate-input errors before the approval logic, because load_mandates refuses them (registry.py:168-172), so approval cannot mask them. Residual: an OSError from `read_bytes` inside `fingerprint` is outside the hook's `except (AcfInputError, UnknownDetectorError)` and would surface as an uncaught traceback with exit 1 (user-only) - filed as advisory.

#### M7 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:227-230; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:151; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:161; plugins/arch-compliance/tests/test_hooks.py:391; plugins/arch-compliance/hooks/inject_constraints.py:2`
- reasoning: Doctrine: a tree claim load-bearing on 'only'/'no other' etc. needs a re-runnable recipe. Section 5's 'No other runtime file changes' carries a git-diff recipe (:151); section 6.1 carries a grep recipe (:161) - I re-ran its pattern: hits at :391 (def), :409, :447, :471, :491, inside the tests at :406/:440/:464/:488 as listed. The SubagentStart recipe pattern has no match in inject_constraints.py and 'host' appears exactly at :2, :6, :13 as claimed. The 'four returns' in section 1.2 are enumerated line by line (:85-91, :99-107, :109-113, :116-120), and those are the only explicit gate-input `return 1`s in posttooluse_gate.py.

#### M8 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:175-182; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:129`
- reasoning: The Trust boundary paragraph (:175-180) contains the one sentence the design falsifies ('runs host code only when .acf/enabled exists'); spec :129 replaces it, keeps the acf-check-diff, confinement and load_mandates sentences, and adds the two new test files to the 'No row: enforced by' line at :182. Minor residual: the Call-site rule sentence 'The PostToolUse hook runs rows declaring hook or posttooluse' (:161-162) becomes conditionally true for host rows; the rewritten Trust boundary qualifies it, so the section stays consistent read as a whole. The hook's own module docstring (posttooluse_gate.py:12-13, 'host detectors included') is not in section 4.4's prose list.

### Unanchored findings

- **important**: acf-allow's 'named file missing' branch (spec section 4.2, :109) is unreachable and its error handling (:112) catches only AcfInputError: loading the registry 'as the hook does' (known_detectors + repo_root) already raises UnknownDetectorError for a missing/unstat-able host detector file, so acf-allow would die with a traceback instead of printing a refusal; the section 6.4 'Missing detector file: exit 1' test would pass only because an uncaught exception also exits 1.
  - evidence: `plugins/arch-compliance/python/acf/registry.py:160-172`
- **important**: Single point of definition: `hook_host_rows` re-spells the 'which host rows run at the hook's call sites' rule already written in each runner (registry.active(...detection=...) + is_host_detector_ref); a drift between the copies would fingerprint a different set than the hook executes. Separately, acf-allow must print a SHA-256 per file and detect a missing file, but `fingerprint` returns only the combined hex, so cli_allow would have to recompute file digests a second time outside approval.py.
  - evidence: `plugins/arch-compliance/python/acf/detectors/host.py:164-165`
- **advisory**: In the hook, `approval_state` is placed inside `except (AcfInputError, UnknownDetectorError)` (spec section 4.3 step 1), but `fingerprint`'s `read_bytes()` OSError (e.g. permission denied) is not wrapped, so it exits 1 with a traceback - the user-only channel #30 exists to fix - instead of exit 2.
  - evidence: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:93`
- **advisory**: Section 6.5's 'guards that must keep passing' omits test_repo_paths.py, which is the actual test of the `plugin.one-owner-host-paths` row (mandates.yml:159-163) and the one that pins the hook's no-marker stdlib-only path that M2 relies on.
  - evidence: `plugins/arch-compliance/tests/test_repo_paths.py:81-108`

### Looked for but did not find

- ## High-frequency misses: unbacked completeness claim - section 5, section 6.1 and SubagentStart claims each carry a recipe; checked section 6.1 and SubagentStart recipes against the tree - no miss.
- ## High-frequency misses: stdlib mixin on an exception class - the design adds no exception class.
- ## High-frequency misses: subprocess text call without encoding - the design adds no subprocess call.
- ## High-frequency misses: re-implemented check instead of consumed - the registry is loaded through `load_mandates` with KNOWN_DETECTORS and the mandates path via MANDATES_REL (spec :106); the row-selection duplication is filed as a finding.
- ## Declared, never defaulted - `--repo` defaults to `resolve_repo(None)`, an already-recorded fallback (ARCHITECTURE.md:192-193); the store location is a fixed path, not a default standing in for a declared value - not breached.
- ## No shims - no hasattr probing or `any` in the design.
- ## Build artifacts, ## Fail-loud ratchet, ## Facade sinks, ## FSM transitions, ## Soft fail-loud smells, ## React boundaries - no surface of theirs is touched by this design.
- ## Frozen ledger format - the design does not touch LedgerRow or LedgerAmendment.
- ## Live consumers - every new export (`approval_state`, `ApprovalState`, `write_approval`, `hook_host_rows`, `fingerprint`, `read_store`, `store_path`) has a non-test call site in the hook, cli_allow or approval.py itself.
- ## Scoped refactor - the change surface stays within the hook, two new modules, the console script and the prose describing them.
- ## Post-merge - the design touches no operational declarations.

### Unstated mandates

- ## POSIX paths - the design writes a path into JSON (the store key `RepoTree(repo).root.as_posix()`, spec :62); it complies by using as_posix, but the section is not among the governing mandates at spec :8.
- ## Prose names no host - the design adds skill prose (acf-setup/SKILL.md:16-25, :148, :150) and a new runtime message (the section 4.3 notice); this section governs both. The drafted text names no host, but the spec does not state the section applies.
- ## Single point of definition - `hook_host_rows` and `fingerprint` restate logic that already exists in host.py:164-165/193 (host row selection), and cli_allow needs per-file digests that `fingerprint` does not expose; the spec does not name the section.

## sweeper

### Claim verdicts

#### S1 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/loader.py:43`
- reasoning: The narrow fact holds (no per-user/out-of-repository store exists: searched plugins/arch-compliance for Path.home, expanduser, XDG_, APPDATA, USERPROFILE, platformdirs, tempfile, os.replace - none). But the conclusion 'duplicates nothing' fails when swept by responsibility (load/parse/validate shape/refuse with AcfInputError naming the path) rather than by component: acf/loader.py:1-8 declares itself 'The one load-parse-validate-refuse implementation. Every input file ACF reads goes through here', and load_model_file (loader.py:43-77) does exactly what read_store's contract re-specifies: OSError -> AcfInputError naming the path (:61-62), invalid JSON -> AcfInputError (:65-66), wrong shape -> AcfInputError (:74-77). Existing consumers: registry.py:132, baseline.py:86, adr/host.py:31. The 'missing file gives {}' difference is already handled at the caller by baseline.py:78-86 ('Absence is a real state decided by the CALLER'). approval.py already depends on acf.registry (which imports pydantic and acf.loader, registry.py:7,10), so there is no import-weight reason to avoid it. Doctrine `## Single point of definition` (config/architecture/ARCHITECTURE.md:264-266) applies.

#### S2 — SURVIVED
- evidence: `pyproject.toml:18-20; plugins/arch-compliance/python/acf/cli_check_diff.py:35; plugins/arch-compliance/python/acf/cli_check_llm.py:16; plugins/arch-compliance/python/acf/repo.py:32`
- reasoning: [project.scripts] maps each console script to `acf.cli_<name>:main`; both existing modules define `main(argv: list[str] | None = None) -> int` (cli_check_diff.py:35, cli_check_llm.py:16) and resolve the repository through acf.repo.resolve_repo (cli_check_diff.py:76, cli_check_llm.py:52), matching section 4.2's `--repo PATH` default of resolve_repo(None). No test or other file enumerates the scripts (grep project.scripts/console_scripts/entry_points outside docs found only pyproject.toml), so a third entry forks nothing.

#### S3 — REFUTED
- evidence: `plugins/arch-compliance/tests/test_hooks.py:409`
- reasoning: The recipe's stated output is wrong: `_seed_host_rows(` matches at :391 (def), :409, :447, :471, :491 - the cited :406/:440/:464/:488 are the test-definition lines, which the grep does not print, so a reader re-running the recipe sees different numbers. The method is also a by-name sweep (the helper's name) for a by-behaviour claim ('no other test file runs the hook with host rows'): a test seeding host rows inline or via another helper is invisible to it. Re-swept by behaviour (tests that run posttooluse_gate.py; tests writing `detector: <path>.py:<callable>` rows): test_builtin_detectors.py:177-181 runs the hook but with built-in rows only (_row at :109-135 uses KNOWN_DETECTORS ids); test_diff_cli.py:316/:326 write host rows but run the diff gate; no tracked .yml fixture holds a host reference. So the four-test population is currently correct, but the recipe would not catch the next one.

#### S4 — REFUTED
- evidence: `README.md:108`
- reasoning: The sweep was by phrasing ('marker is the opt-in' / 'commit .acf/') rather than by the responsibility being changed (prose stating when the hook runs host code). Swept that way, tracked sites that become false are absent from section 4.4: (1) README.md:108 states the hook 'runs the active rows declaring `hook` or `posttooluse` ... and host guards on every edited path' and 'BLOCK findings exit 2' with no approval and no gate-input exit 2; (2) plugins/arch-compliance/skills/acf-setup/SKILL.md:159, the PostToolUse table row: 'Run Tier-1 Python/TS detectors, host detectors and host guards on edited paths' (the approved docs/design/HOST_DETECTOR_EXTENSION_POINT.md:542 shows this line was written specifically to assert host detectors run at the hook); (3) plugins/arch-compliance/hooks/hooks.json:2 describes the gate as 'exit 2 on BLOCK findings' (quoted by section 1.2), incomplete under Decision 7; (4) the module docstring plugins/arch-compliance/hooks/posttooluse_gate.py:12-14 'host detectors included' (file is in section 5). The five listed sites themselves exist (ARCHITECTURE.md:175-180, acf-setup SKILL.md:148/:150, README.md:110, SUPERPOWERS_COMPLEMENT.md:87).

#### S5 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:53; plugins/arch-compliance/python/acf/registry.py:29-33; plugins/arch-compliance/python/acf/registry.py:110`
- reasoning: Every runtime API the design consumes already exists: RepoTree.contained and .root (repo.py:51-59; an absolute string is taken as is, so contained(str(store_path)) works), RepoTree.file (repo.py:61), is_host_detector_ref / parse_host_detector_ref (registry.py:29-46), MandateRegistry.active(call_sites, detection=...) (registry.py:110-122), HOOK_CALL_SITES (registry.py:18), load_mandates (registry.py:125), and Mandate is a pydantic model so model_dump(mode='json') is available (registry.py:49). No acf.repo constant is needed because the store is home-relative, not host-relative. So no runtime file beyond approval.py, cli_allow.py and posttooluse_gate.py must change for the mechanism. Caveat: hooks.json:2 is a runtime-directory file whose description goes stale (see S4); if the author updates it, the section 5 recipe will list a fourth file under plugins/arch-compliance/hooks.

#### S6 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:130-147; plugins/arch-compliance/tests/test_hooks.py:196-197; plugins/arch-compliance/tests/test_hooks.py:230-231`
- reasoning: The hook already reports via stderr+exit 2 on BLOCK (posttooluse_gate.py:130-133, pinned by test_hooks.py:196-197), via hookSpecificOutput.additionalContext otherwise (:134-147, pinned by test_hooks.py:230-231), and via stderr for text/json-mode refusals (:87-120). The notice reuses these channels; systemMessage appears nowhere in plugins/ today (grep), so it is a new field on the existing JSON object, not a second reporting mechanism. The nearest existing 'ACF did not run' notice is the inactive warning (posttooluse_gate.py:77-80, stderr only, exit 0), which covers a different situation (whole plugin off, user opted out), so the notice is adjacent, not a duplicate.

### Unanchored findings

- **important**: read_store re-implements the package's one load-parse-validate-refuse path (acf.loader.load_model_file) with a hand-rolled JSON parse, shape check and OSError mapping, adding a third owner of that responsibility contrary to `## Single point of definition`; a pydantic ApprovalStore model read via load_model_file after a caller-side existence check (the pattern baseline.py:78-86 already uses) replaces it.
  - evidence: `plugins/arch-compliance/python/acf/loader.py:43`
- **advisory**: hook_host_rows re-derives 'which host rows run at the hook' independently of the runners' own selection (host.py:162-166 for ast, :192-194 for guard), so the fingerprinted set and the executed set have two owners; today the fingerprint is a superset (ignores the runners' language filter), which is safe, but nothing ties them if either changes.
  - evidence: `plugins/arch-compliance/python/acf/detectors/host.py:162`
- **advisory**: Section 4.4's prose list misses tracked sites that state the hook runs host detectors on edit unconditionally or that it exits 2 only on BLOCK: README.md:108, acf-setup SKILL.md:159 (a skill-prose site, so also covered by the version bump) and hooks.json:2.
  - evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:159`
- **advisory**: The design reverses the approved host-detector spec's trust-boundary decision ('That marker is the opt-in for running host code on edit') without naming that spec; it cites only the doctrine restatement and issue #29, so the supersession of an Approved document is unrecorded.
  - evidence: `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:64`

### Looked for but did not find

- an existing per-user / home-directory state store in acf: Path.home, expanduser, XDG_, APPDATA, LOCALAPPDATA, USERPROFILE, platformdirs, appdirs, tempfile, os.replace, '~/.' across plugins/ and the tracked tree
- an existing fingerprint / content-hash approval of host code: hashlib, sha256 (only host.py:73, which hashes a path to name a module)
- other tests running the hook with host rows: posttooluse_gate, GATE, hostdet, '.py:scan' across plugins/arch-compliance/tests; 'detector: <x>.py:' in tracked .yml
- an existing systemMessage producer: systemMessage, additionalContext across plugins/
- a test pinning [project.scripts]: project.scripts, console_scripts, entry_points, acf-check-llm

### Relationships

- PARTIAL_OVERLAP: `acf.approval.read_store` — responsibility `load, parse, validate and refuse a JSON input file with AcfInputError naming the path` — existing `plugins/arch-compliance/python/acf/loader.py:43`
  - resolution: Declare an ApprovalStore pydantic model (extra='forbid', version: Literal[1], repos: dict[str, ApprovalEntry]) and read it with load_model_file(path, ApprovalStore, subject='approval store', fmt='json'); read_store collapses to an existence check plus that call, as baseline.load_baseline (baseline.py:78-86) does. Delete the private JSON decode, shape check and OSError mapping.
- PARTIAL_OVERLAP: `acf.approval.hook_host_rows` — responsibility `select the host ast/guard rows that run at a call site` — existing `plugins/arch-compliance/python/acf/detectors/host.py:162`
  - resolution: Extract one selector (e.g. acf.registry.MandateRegistry.host_rows(call_sites, detection=None) returning active rows with is_host_detector_ref true) consumed by scan_host_ast_file (host.py:162-166, which then applies its language filter), scan_host_guards (host.py:192-194) and hook_host_rows (which sorts by id).
- ADJACENT: `acf.approval.write_approval` — responsibility `persist a JSON document, creating its parent directory` — existing `plugins/arch-compliance/python/acf/baseline.py:68`
  - resolution: none
  - non-merge: save_baseline writes an in-repo, operator-reviewed artifact non-atomically and raises BaselineError; write_approval does a read-modify-write of a shared per-user file and needs os.replace atomicity. Two writers with different durability needs do not yet justify a shared helper.
- ADJACENT: `acf-allow (acf.cli_allow.main)` — responsibility `console-script entry resolving the repo and loading the registry` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:35`
  - resolution: none
  - non-merge: Follows the existing cli_<name>:main shape and consumes resolve_repo/load_mandates rather than re-implementing them; its job (approve/revoke) is distinct from running a gate.
- ADJACENT: `unapproved-host notice in posttooluse_gate` — responsibility `tell the operator that some or all of ACF did not run` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:77`
  - resolution: none
  - non-merge: The inactive warning reports a deliberate plugin-wide opt-out (stderr only, suppressible with --quiet-disabled); the new notice reports a partial skip the agent must learn about, so it goes through additionalContext and systemMessage.

### Two-owner counts

- load/parse/validate/refuse a JSON input file: 3
- select host rows that run at the hook call sites: 3

### Document conflicts

- `docs/design/HOST_DETECTOR_EXTENSION_POINT.md:64` (contradicts): That marker is the opt-in for running host code on edit.
- `config/architecture/ARCHITECTURE.md:175` (contradicts): The PostToolUse hook runs host code only when `.acf/enabled` exists; committing `.acf/` therefore opts every clone in.

## hardening

### Claim verdicts

#### H1 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:74-83; plugins/arch-compliance/python/acf/detectors/host.py:76-83; plugins/arch-compliance/python/acf/registry.py:160-172`
- reasoning: The only gate is `.acf/enabled` being a file (posttooluse_gate.py:74-83); past it, load_mandates checks only that a host detector file exists (registry.py:160-172) and load_host_detector executes whatever bytes are on disk (host.py:83 exec_module). Any rule on the marker itself (refusing it when tracked, or moving it into .git/ to make it per-clone) would stop consequence 2 (clone-carried opt-in) but not consequence 1: in an already-enabled clone, checking out a contributor branch changes the detector bytes while the marker is unchanged. The marker carries no information about which code was approved, so a content-bound record outside the working tree is required. The claim holds; the spec does not write this alternative out explicitly, it only states the hook 'has no state outside the working tree' (spec:32).

#### H2 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:66-83; plugins/arch-compliance/python/acf/detectors/host.py:162-166`
- reasoning: Every hook process re-resolves and executes the current file named by each active host row (host.py:66-83), selected from the current registry with no record of prior state (host.py:162-166, 192-194). A per-repo boolean therefore approves arbitrary future rows/bytes; only a binding to rows plus file bytes makes a branch checkout that changes them re-prompt. The binding is incomplete for imported helpers, which spec section 3 declares.

#### H3 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:167-204; plugins/arch-compliance/hooks/posttooluse_gate.py:129-133`
- reasoning: The diff gate runs host rows on its own path (cli_check_diff.py:167-204), which the spec leaves untouched, so CI enforcement is unchanged. In the hook, exit 2 is the blocking, agent-fed code (posttooluse_gate.py:129-133); using it for 'unapproved' would block every edit in every host-row repo until approval. Decision 5 refuses the host rows with a notice to agent and user; it does not silently repair.

#### H4 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:162-166; plugins/arch-compliance/python/acf/detectors/host.py:192-194; plugins/arch-compliance/python/acf/registry.py:84-88`
- reasoning: scan_host_ast_file selects registry.active(call_sites, detection='ast') with is_host_detector_ref and languages in {language,'both'} (host.py:162-166), called with 'python' and 'typescript' (posttooluse_gate.py:273-287); Mandate._row_shape forces every active host ast row to declare languages in {python,typescript,both} (registry.py:84-88), so the union over both calls is every active host ast row. scan_host_guards selects active guard host rows with no further filter (host.py:192-194). The proposed filter therefore selects exactly that union - a superset of any single edit's rows (ast rows only run for a matching suffix), which is the right approval scope.

#### H5 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/registry.py:61; plugins/arch-compliance/python/acf/loader.py:64`
- reasoning: Mandates load via yaml.safe_load (loader.py:64) and params is dict[str, Any] (registry.py:61). SafeLoader constructs a Python set from `!!set`; pydantic model_dump(mode='json') serialises the set as a list in iteration order, which follows the string hash seed. Verified read-only: the same row under PYTHONHASHSEED=1/2/3 yielded three different list orders; sort_keys does not reorder lists. Each hook process has a random hash seed, so such a row's fingerprint differs on every run - permanent STALE (fail-safe, but approval is unattainable). Other shapes checked are deterministic (int nested keys become '1', dates become ISO strings). So 'for every loadable row' is false; fix by rejecting non-JSON-native params at load or canonicalising sets before hashing.

#### H6 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:241-250; plugins/arch-compliance/hooks/posttooluse_gate.py:289-291`
- reasoning: rel_paths and file_lines are populated at :243-250 before and independently of the host calls; the built-in calls (:252-272, :279-282, :289-291) take only text/rel/params/rel_paths, never host output. The three host calls only extend `findings` (and scan_host_guards adds host-flagged files to file_lines, host.py:201-215). Skipping them removes only host findings and their line entries; apply_registry (:122-124) is unaffected for built-ins.

#### H7 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:53-59; pyproject.toml:5`
- reasoning: requires-python >=3.11 (pyproject.toml:5); since 3.8 Path.home() on Windows reads USERPROFILE and ignores HOME, POSIX reads HOME - confirmed on this machine (3.13, Windows): HOME=X:/h left Path.home() at C:\Users\iball, so setting both is required, as section 6 says. RepoTree.contained computes (root / path).resolve(); pathlib's join replaces root with an absolute right operand, so the path is taken as is, and it returns non-None exactly when the resolved candidate is_relative_to root (repo.py:56-59).

#### H8 — SURVIVED
- evidence: `C:/Users/iball/.claude/plugins/marketplaces/claude-plugins-official/plugins/hookify/core/rule_engine.py:72-79; C:/Users/iball/.claude/plugins/marketplaces/claude-plugins-official/plugins/hookify/hooks/posttooluse.py:48-58; plugins/arch-compliance/hooks/posttooluse_gate.py:137-147`
- reasoning: The external hooks reference is unavailable. Corroboration: the official hookify plugin returns one JSON object containing both `hookSpecificOutput` (hookEventName PostToolUse) and top-level `systemMessage` for PostToolUse (rule_engine.py:72-79), printed to stdout with exit 0 (posttooluse.py:48-58). The current hook already emits `hookSpecificOutput.additionalContext` on exit 0 (posttooluse_gate.py:137-147); adding a sibling top-level key matches an Anthropic-published plugin's usage.

#### H9 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:96; plugins/arch-compliance/hooks/posttooluse_gate.py:109-113`
- reasoning: AcfInputError is imported at :96 before the try at :109; the except clause names AcfInputError (:111), so a read_store AcfInputError raised inside the block is caught. acf.approval imports acf.registry (pydantic), so its import must sit in the :93-107 block, as section 4.1 states. Leak: fingerprint's OSError is not wrapped (see unanchored).

#### H10 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:40-44; plugins/arch-compliance/hooks/posttooluse_gate.py:156-160; plugins/arch-compliance/python/acf/repo.py:51`
- reasoning: The hook passes stdin cwd to resolve_repo -> Path(cwd).resolve(); acf-allow from the same directory -> Path.cwd().resolve() (repo.py:40-44); RepoTree re-resolves (repo.py:51). On Windows resolve() canonicalises case (verified: c:/users/IBALL/arduino -> C:\Users\iball\Arduino), so as_posix keys match for the same directory. Neither walks up to the git toplevel, but the hook only acts when cwd contains .acf/enabled, and acf-allow from a subdirectory fails loud at load_mandates (mandates.yml missing), so no mismatched key is written.

#### H11 — UNPROVEN
- evidence: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:97`
- reasoning: POSIX rename(2) is atomic; on Windows os.replace uses MoveFileExW(MOVEFILE_REPLACE_EXISTING), and Python documents atomicity only as a POSIX requirement. No in-repo or stdlib source line establishes Windows atomicity. The weaker property (temp file complete before rename, so readers never see a half-written store) holds. Separately, on Windows os.replace raises PermissionError if another process holds the destination open (Python's open() does not share delete). Not load-bearing.

### Unanchored findings

- **important**: fingerprint() hashes params via model_dump(mode='json'), which turns a YAML `!!set` in params into a hash-seed-ordered list; such a row's fingerprint changes every process, making approval impossible (perpetual STALE notice, fail-safe). Needs canonicalisation or rejection of non-JSON-native params at load.
  - evidence: `plugins/arch-compliance/python/acf/registry.py:61`
- **advisory**: fingerprint() calls RepoTree(repo).file(rel).read_bytes(); RepoTree.file propagates OSError from stat and read_bytes can raise OSError, neither an AcfInputError, so the hook's except (AcfInputError, UnknownDetectorError) at :111 misses it and the hook dies with a traceback (exit 1) in hook mode - the outcome Decision 7 targets. Wrap as AcfInputError in approval.py.
  - evidence: `plugins/arch-compliance/python/acf/repo.py:61-64`
- **advisory**: If the host repository root is the user's home directory (e.g. a dotfiles repo), ~/.acf/approvals.json is always contained by RepoTree(repo): the repo is permanently STORE_IN_REPO and acf-allow always refuses; the spec does not name this case or its escape.
  - evidence: `plugins/arch-compliance/python/acf/repo.py:53-59`
- **advisory**: Section 4.2 maps only AcfInputError to exit 1; an OSError from write_approval's os.replace (Windows PermissionError while the hook has the store open) makes acf-allow exit with a traceback, not the lost-write the risk-table row 4 assumes.
  - evidence: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:97`

### Looked for but did not find

- Repository code executed by the hook before the approval check: load_mandates uses yaml.safe_load (loader.py:64) and only checks detector-file existence (registry.py:160-172); the TS bridge runs the plugin's own pack, not repo code (typescript_bridge.py:19,52-58).
- A second hook path that runs host rows outside the three _scan_paths calls: grep scan_host found only posttooluse_gate.py:273-294 and cli_check_diff.py:167-204.
- Built-in detectors depending on host-call output in _scan_paths: none.
- Detector-file symlink escape from the fingerprint: RepoTree.contained resolves and requires containment (repo.py:56-59), so the hashed file is always the in-repo file that is executed.
- Section 6.1 population: grep `_seed_host_rows(` prints :391 (definition), :409, :447, :471, :491 - consistent with the spec's four call sites (:406/:440/:464/:488 are the test definitions).
- Exit-2 change (Decision 7): a return-code change, not a recovery mechanism; out_format is computed at :68-72, before the first failure return at :91.

### Mechanism traces

- **Per-user fingerprinted approval store gating host rows (approval_state / acf-allow)**
  - invalid state: hook executes a host ast/guard row while (hook host rows' model_dump, detector-file SHA-256s) differs from any tuple the current user approved for this repo root
  - producer: `plugins/arch-compliance/hooks/posttooluse_gate.py:74-83`
  - rung 2 (highest applicable 2); repairs=False
  - hardening rejected because: The opt-in is a file the repository itself can carry ... The hook has no state outside the working tree that could record a person's approval of particular code.
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:62-63`
- **STORE_IN_REPO containment check**
  - invalid state: RepoTree(repo).contained(str(Path.home()/'.acf'/'approvals.json')) is not None
  - producer: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:76`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: A committed Claude Code settings file can set environment variables and declare hooks of its own; Claude Code's folder trust governs that.
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:62`
- **Unapproved repository: skip host rows, run built-ins, emit notice (Decision 5)**
  - invalid state: approval_state(repo, registry) in {MISSING, STALE, STORE_IN_REPO} while hook_host_rows(registry) is non-empty
  - producer: `plugins/arch-compliance/python/acf/detectors/host.py:162-166`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: blocking every edit would make an unapproved repository unusable; the diff gate in CI is unchanged, so enforcement at merge is unaffected
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:65`
- **read_store shape validation raising AcfInputError**
  - invalid state: approvals.json does not parse or is not {version:1, repos:{str:{fingerprint:str, approved:str}}}
  - producer: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:97`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:96`
- **Atomic store write by os.replace from a same-directory temp file**
  - invalid state: approvals.json truncated or partially written after an interrupted or concurrent write_approval
  - producer: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:211`
  - rung 2 (highest applicable 2); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:97`

## Claims

- **C1** [root_cause] [load-bearing]: The only check between 'plugin installed' and host detector code running at edit time is whether `.acf/enabled` is a file in the repository working tree; past that check `_scan_paths` calls `scan_host_ast_file` and `scan_host_guards`. No state outside the working tree records a person's approval of particular host code.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:74-83`
- **C2** [premise] [load-bearing]: `hooks.json` registers `posttooluse_gate.py --format hook` for `Write|Edit|MultiEdit` at plugin level, so once the plugin is installed the hook fires in every repository the user opens, not only repositories that opted in.
  - spec citation: `plugins/arch-compliance/hooks/hooks.json:16-27`
- **C3** [premise] [load-bearing]: `load_host_detector` imports the host-named file with `spec.loader.exec_module` in the hook's own process, so host module code runs with the user's privileges.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/host.py:53-95`
- **C4** [premise]: The acf-setup skill recommends committing `.acf/` when a team wants hooks enabled for everyone.
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:150`
- **C5** [premise] [load-bearing]: Before host detectors existed, a committed `.acf/enabled` enabled only the plugin's own built-in detectors (configured through row `params`); no repository-supplied code ran at edit time. Host rows are what turned the marker into permission to run code.
  - spec citation: `None`
- **C6** [premise]: Host detector finding messages reach the agent's context: via `additionalContext` on a non-blocking hook run and via stderr on exit 2.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:137-147`
- **C7** [root_cause] [load-bearing]: `posttooluse_gate.py` returns exit code 1 on four gate-input failures regardless of output format: mandates missing (`:85-91`), dependencies not importable (`:99-107`), `load_mandates` raising `AcfInputError`/`UnknownDetectorError` (`:109-113`), and `_scan_paths` raising `AcfInputError`/`DetectorPackError`/`UnknownDetectorError` (`:116-120`). These are the gate-input failure returns in hook mode.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:85-120`
- **C8** [premise] [load-bearing]: For a Claude Code PostToolUse hook, exit code 2 shows stderr to Claude (the agent) and other non-zero exit codes show stderr to the user only; the hook's own comment relies on this. (External: Claude Code hooks reference, https://code.claude.com/docs/en/hooks.)
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:131`
- **C9** [premise] [load-bearing]: Deferral: the SubagentStart hook `inject_constraints.py` runs no host code (recipe: `grep -n "acf.detectors\|scan_host\|load_host_detector" plugins/arch-compliance/hooks/inject_constraints.py` prints nothing), so it is out of scope for both issues. Run the recipe and confirm it imports no host detector machinery by any other route.
  - spec citation: `plugins/arch-compliance/hooks/inject_constraints.py`
- **C10** [premise] [load-bearing]: Deferral: the diff gate (`acf-check-diff`) needs no approval because it runs host rows only when the host's own pre-commit or CI configuration invokes it, and that invocation is the opt-in recorded in doctrine.
  - spec citation: `config/architecture/ARCHITECTURE.md:176-178`
- **C11** [premise] [load-bearing]: Deferral: a repository that can set the hook's environment variables can already run commands through a committed Claude Code settings file (env and hooks), which Claude Code's folder trust governs; so the design need not defend against environment manipulation beyond refusing a store path that lies inside the repository. The spec offers no citation for Claude Code's settings behaviour.
  - spec citation: `None`
- **C12** [premise] [load-bearing]: Deferral: a change confined to a module imported by a host detector file is outside the fingerprint and runs under an existing approval; the design accepts this as a known limitation printed by `acf-allow`.
  - spec citation: `None`
- **C13** [deletion]: The design removes no runtime code; it removes only the doctrine sentence that committing `.acf/` opts every clone in (`ARCHITECTURE.md:175-176`) and acf-setup's commit-opt-in warning (`SKILL.md:150`), and adds an approval layer.
  - spec citation: `config/architecture/ARCHITECTURE.md:175-176`
- **C14** [premise] [load-bearing]: Each of the four exit-1 returns in hook mode is reached after `out_format` is computed (`:68-72`), so `return 2 if out_format == "hook" else 1` is available at each.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:68-72`
- **C15** [premise]: The existing text-format exit-1 hook tests at `test_hooks.py:145`, `:318` and `:424` run the hook in text mode (no hook-format argument and no stdin carrying `hook_event_name`), so they stay valid when only hook mode changes to exit 2.
  - spec citation: `plugins/arch-compliance/tests/test_hooks.py`
- **M1** [mandate] [load-bearing]: `acf.approval` and `acf.cli_allow` turn repository path strings into locations only through `RepoTree` and compare the store path to the repository only through `RepoTree.contained`, complying with `## One owner for host paths`; `test_repo_tree_guard.py` needs no new allowlist entry.
  - spec citation: `config/architecture/ARCHITECTURE.md:113-139`
- **M2** [mandate] [load-bearing]: The hook's no-marker path still imports nothing beyond `acf.repo` because `acf.approval` is imported only after the third-party imports (`posttooluse_gate.py:93-107`), preserving the stdlib-only pre-gate contract of `acf.repo` (`repo.py:1-6`) and `test_adr_import_graph.py`.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:93-107`
- **M3** [mandate]: `## Release discipline` requires a version bump because acf-setup's skill prose changes; the design bumps `pyproject.toml:3` and `plugin.json:3` to 0.2.5.
  - spec citation: `config/architecture/ARCHITECTURE.md:250-260`
- **M4** [mandate]: `read_store` reads with `encoding="utf-8"`, complying with `## Declared text decoding`.
  - spec citation: `config/architecture/ARCHITECTURE.md:237-248`
- **M5** [mandate]: The design adds no exception class; store and registry failures raise the existing `AcfInputError`, complying with `## One base exception`.
  - spec citation: `config/architecture/ARCHITECTURE.md:107-111`
- **M6** [mandate] [load-bearing]: Exit 2 for hook-mode gate-input failures and an explicit notice (not a silent skip) for unapproved host rows comply with `## Fail loud` ('Errors must surface'); skipping host rows with a notice does not count as swallowing a failure.
  - spec citation: `config/architecture/ARCHITECTURE.md:25-42`
- **M7** [mandate]: The spec's population claims (section 5 runtime files, section 6.1 test call sites, the SubagentStart recipe) are backed by re-runnable recipes, complying with `## No completeness claims`.
  - spec citation: `config/architecture/ARCHITECTURE.md:225-235`
- **M8** [mandate]: The design keeps `## Host detectors and call sites` consistent with doctrine: the Trust boundary paragraph is rewritten, its `acf-check-diff`, confinement and `load_mandates` sentences kept, and the section's `No row: enforced by ...` line (`:182`) gains the two new test files.
  - spec citation: `config/architecture/ARCHITECTURE.md:175-182`
- **S1** [shape_fit] [load-bearing]: `acf.approval` creates no second way to do something the package already does: no existing per-user or out-of-repository state store exists in `acf`, so the approval store duplicates nothing.
  - spec citation: `None`
- **S2** [shape_fit]: `acf-allow` follows the existing console-script shape of `acf-check-diff` and `acf-check-llm` in `pyproject.toml` `[project.scripts]`.
  - spec citation: `pyproject.toml:18-20`
- **S3** [sweep] [load-bearing]: `grep -n "_seed_host_rows(" plugins/arch-compliance/tests/test_hooks.py` at the reviewed commit prints the helper definition (`:391`) and call sites in `test_gate_disabled_does_not_import_a_host_module` (`:406`), `test_gate_runs_hook_host_rows_and_not_ci_only_host_guards` (`:440`), `test_gate_edited_file_outside_repo_yields_no_finding_and_no_host_call` (`:464`) and `test_gate_native_absolute_path_is_reported_under_its_posix_key` (`:488`); no other test file runs the hook with host rows.
  - spec citation: `plugins/arch-compliance/tests/test_hooks.py`
- **S4** [sweep]: The prose change list in section 4.4 covers the tracked prose sites that state the marker is the opt-in for host code or recommend committing `.acf/` for that purpose: `ARCHITECTURE.md:175-180`, `acf-setup/SKILL.md:148`, `:150`, `README.md:110`, `docs/guides/SUPERPOWERS_COMPLEMENT.md:87`.
  - spec citation: `None`
- **S5** [sweep] [load-bearing]: Only three runtime files under `plugins/arch-compliance/python` and `plugins/arch-compliance/hooks` change: `acf/approval.py` (new), `acf/cli_allow.py` (new) and `hooks/posttooluse_gate.py`.
  - spec citation: `None`
- **S6** [shape_fit]: The unapproved-host notice extends the hook's existing output channels (`additionalContext`, stderr) plus the documented `systemMessage` field rather than inventing a second reporting mechanism.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:130-147`
- **H1** [mechanism_justification] [load-bearing]: A new mechanism (a per-user approval store) is needed rather than hardening the existing marker: no rule applied to `.acf/enabled` itself (for example refusing it when tracked by git) can distinguish a person's consent from repository content, because a tracked-ness check says nothing about which code was approved; the spec does not discuss this alternative explicitly.
  - spec citation: `None`
- **H2** [mechanism_justification] [load-bearing]: Binding the approval to a fingerprint of the hook's host rows and named detector files is necessary so a changed branch (a checked-out contributor PR) re-prompts; an unbound per-repository flag would approve future code.
  - spec citation: `None`
- **H3** [mechanism_justification] [load-bearing]: An unapproved repository should run built-ins with a notice instead of blocking (exit 2) or failing, because blocking every edit would make an unapproved repository unusable while CI enforcement is unchanged.
  - spec citation: `None`
- **H4** [implementability] [load-bearing]: `registry.active(HOOK_CALL_SITES)` filtered to `detection in {ast, guard}` and `is_host_detector_ref(m.detector)` selects exactly the rows `scan_host_ast_file` and `scan_host_guards` would run in the hook (their own filters use `registry.active(call_sites, detection=...)` and `is_host_detector_ref`).
  - spec citation: `plugins/arch-compliance/python/acf/detectors/host.py`
- **H5** [implementability] [load-bearing]: `Mandate.model_dump(mode="json")` yields a JSON-serialisable value for every loadable row, including `params: dict[str, Any] | None`, so `json.dumps(..., sort_keys=True)` over it is deterministic.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py`
- **H6** [implementability] [load-bearing]: `_scan_paths` can take a `run_host` flag and skip the three host calls (`:273-277`, `:283-287`, `:292-294`) without affecting built-in detector calls or the population of `file_lines`/`rel_paths` that built-ins and `apply_registry` use.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:214-295`
- **H7** [implementability] [load-bearing]: `Path.home()` honours `HOME` on POSIX and `USERPROFILE` on Windows, so tests can redirect the store by setting both; and `RepoTree(repo).contained(str(absolute_path))` takes an absolute path as is and returns non-None exactly when it lies inside the repository root.
  - spec citation: `plugins/arch-compliance/python/acf/repo.py:53-59`
- **H8** [implementability] [load-bearing]: A Claude Code PostToolUse hook's JSON output may carry a top-level `systemMessage` (shown to the user) together with `hookSpecificOutput.additionalContext` (shown to the agent) in one object on exit 0. (External: Claude Code hooks reference.)
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:137-147`
- **H9** [implementability] [load-bearing]: `approval_state` can run inside the existing `load_mandates` try block (`:109-113`), whose `except (AcfInputError, UnknownDetectorError)` will catch a malformed-store `AcfInputError`.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:109-113`
- **H10** [implementability] [load-bearing]: The hook's repository root (`resolve_repo(args.repo, stdin cwd)`) and `acf-allow`'s (`resolve_repo(None)` from the same checkout) produce the same `RepoTree(repo).root.as_posix()` key, so an approval written by `acf-allow` is found by the hook.
  - spec citation: `plugins/arch-compliance/python/acf/repo.py:32-45`
- **H11** [implementability]: `os.replace` from a temporary file in the same directory replaces an existing store atomically on Windows and POSIX.
  - spec citation: `None`
