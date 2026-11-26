# Adversarial design review — full detail

Spec: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md` @ `3b860c5853c43d5ae5360cc70d749881f850dcab`
Kinds: defect, feature
Outcome: **BLOCKED**
Claims: 49 · Reviewers: 4 · Converged: 3

## Blocking reasons

- load-bearing claim C9 (premise) is REFUTED: run_git uses text=True without encoding (locale codec, strict errors), declared debt. The claim fails at 'can only cause MISSING': under a Windows cp1252 locale, git's UTF-8 output for chars like C3 81/8D/8F/90/9D contains bytes undefined in cp1252, so subprocess.run raises UnicodeDecodeError. Per §5.1 git_common_dir returns None only on non-zero exit or OSError, so the exception propagates out of repo_key/check_approval; cli_check_diff catches only GitError/AcfInputError/UnknownDetectorError/DetectorPackError (crash with traceback); the PostToolUse hook catches only AcfInputError/UnknownDetectorError around check_approval (generic exit-2 handler). Today's key comes from Path.resolve with no subprocess decode, so such paths work now. The key also includes the absolute path with the Windows user folder name. 'Decodes the same way at approval and at check' is not guaranteed either (different PYTHONUTF8/locale between acf-allow and the gate), though that only yields MISSING. 'Never a false APPROVED' holds since the fingerprint decides.
- load-bearing claim C17 (mandate) is UNPROVEN: Hook half holds (matches posttooluse_gate.py:89 precedent: stderr, exit 2, token with reason). git_common_dir half not established: Fail loud says failures must not disappear and no defaulting to None to avoid a crash (:42). git_common_dir returns None on any non-zero exit and on OSError and discards git's stderr, conflating real git failures (git missing from PATH, dubious ownership, git < 2.31, corrupt repo) with 'not a git repository'. Scope is printed only by acf-allow and acf-approval-status; the gate texts (§5.5) say only 'no approval for this repository', so inside a gate the failure vanishes into a misleading MISSING. Fails closed, but recording the default elsewhere does not by itself satisfy fail-loud.
- implementability claim C47 is REFUTED: test_repo_paths.py:81-108 is test_hooks_import_repo_without_pulling_third_party: poisoned pydantic.py/yaml.py on PYTHONPATH, runs the two existing hooks, asserts exit 0. Subprocess check, not AST; does not pin stdlib-only or no acf import; no ast usage in the file. The nearest import check is test_repo_module_imports_only_stdlib (:74-78), a regex allowlist for repo.py only. The new hook needs its own check, modelled on :74-78.
- implementability claim C49 is UNPROVEN: permission-modes.md:30 says deny rules block in bypassPermissions; no statement that a PreToolUse hook's deny is honoured there (hooks.md:1697 says so only for PreSkillShellCommand). Not load-bearing.

## Absorptions

- SUBSUMED: 'acf.diff.git_common_dir' shares responsibility 'invoke git from runtime code' with plugins/arch-compliance/python/acf/diff.py:17 — git_common_dir consumes run_git; adds no runner. The pre-existing second runner (adr/citations.py:51) stays the recorded breach, consolidated per PLUGIN_SELF_HOSTING_AND_DOCTRINE.md §9 follow-up 1.
- PARTIAL_OVERLAP: 'acf-approval-status (cli_approval_status.main)' shares responsibility 'present the rows, file digests and helper limit a person reviews before approving' with plugins/arch-compliance/python/acf/cli_allow.py:59 — Extract one renderer in acf.approval (e.g. describe_approval(repo, registry) -> lines, built on approval_rows, file_digests, fingerprint and repo_key) that both CLIs print; acf-allow keeps its write and fingerprint-match step; acf-approval-status keeps state and fingerprint lines. HELPER_LIMIT and scope wording collapse into it.
- SUBSUMED: 'acf-approval-status store-in-repository handling' shares responsibility 'refuse a store that lies inside the repository' with plugins/arch-compliance/python/acf/approval.py:121 — Status reaches it through check_approval (STORE_IN_REPO). The pre-existing duplicate at cli_allow.py:56 should call approval._store_inside_repo or rely on write_approval's refusal at approval.py:165.
- PARTIAL_OVERLAP: "approval_prompt.py needle 'approvals.json'" shares responsibility "spell the approval store's file name" with plugins/arch-compliance/python/acf/approval.py:37 — Deliberate second literal since the hook must not import acf; the §6.3 pinning test reconciles it. Keep it and name the hook in approval.py's STORE_REL comment.

## Converged findings

- [3 reviewers: refuter, compliance, hardening] git_common_dir catches only OSError and a non-zero exit; run_git decodes git output with the locale codec and strict errors, so an undecodable repository path raises UnicodeDecodeError out of repo_key/check_approval, crashing the diff gate and exiting 2 in the PostToolUse hook; §4's 'can only cause a MISSING' is false.
  - evidence: `plugins/arch-compliance/python/acf/diff.py:24-30`
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:106-108`
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:142`
- [2 reviewers: compliance, sweeper] §5.7's prose table omits sites that will contradict the design: the acf.approval module docstring ('keyed by the repository's resolved root') and acf-setup/SKILL.md:260 ('a missing acf-allow').
  - evidence: `plugins/arch-compliance/python/acf/approval.py:3-5`
  - evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:260`
- [2 reviewers: hardening, sweeper] §6.3 names test_repo_paths.py:81-108 as an AST import check to reuse; it is a poison-module subprocess test over two hard-coded hooks and cannot pin 'standard library only'; the new hook needs its own import check (model: the regex allowlist at :74-78).
  - evidence: `plugins/arch-compliance/tests/test_repo_paths.py:81`
  - evidence: `plugins/arch-compliance/tests/test_repo_paths.py:99`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:135; plugins/arch-compliance/python/acf/approval.py:167; plugins/arch-compliance/python/acf/repo.py:113; plugins/arch-compliance/python/acf/repo.py:49-53; plugins/arch-compliance/tests/test_approval.py:236; plugins/arch-compliance/tests/test_cli_allow.py:70`
- reasoning: check_approval reads read_store(store).repos.get(RepoTree(repo).root.as_posix()) and write_approval writes data.repos[key] with key = RepoTree(repo).root.as_posix(). RepoTree.root is root.resolve() of the passed directory; resolve_repo gives --repo / harness cwd / process cwd resolved. Each git worktree has its own directory, so a different key; absent entry returns MISSING (approval.py:136-137) regardless of bytes. Tests pin the key as repo.resolve().as_posix(). Nuance: the key is the resolved invocation directory, not git's toplevel, which does not change the claim.

#### C2 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:149-154; plugins/arch-compliance/hooks/posttooluse_gate.py:150-155; plugins/arch-compliance/skills/acf-setup/SKILL.md:24; plugins/arch-compliance/skills/acf-setup/SKILL.md:288; plugins/arch-compliance/skills/acf-mandate/SKILL.md:139; plugins/arch-compliance/python/acf/cli_allow.py:1-5`
- reasoning: All five messages match. The terminal-only constraint is policy expressed in prose; there is no mechanism in cli_allow.py preventing an agent process from running it (see unanchored finding).

#### C3 — SURVIVED
- evidence: `gh issue view 62 --repo IanDBallard/arch-compliance-for-superpowers (body: 'the owner had to run it by hand at the machine for each worktree (Remote Control's `!` does not execute)'); docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:31`
- reasoning: Read issue #62 directly. It reports that Remote Control's ! does not execute. The existence of the report survives; the underlying product behaviour cannot be verified from the repo and is taken as the owner's report.

#### C4 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:68; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:72; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:90; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:69-70; plugins/arch-compliance/skills/acf-setup/SKILL.md:24`
- reasoning: Line 68 Decision 2 keyed by root; :72 Decision 6; :90 per-checkout residual; Decisions 3 and 4 at :69-70; acf-setup :24 repeats it. The 'exactly' is weakened by :84 whose second clause depends on Decision 6 and is not listed as superseded (see unanchored finding).

#### C5 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:112-113; plugins/arch-compliance/python/acf/approval.py:136-137; plugins/arch-compliance/python/acf/approval.py:150-151; plugins/arch-compliance/python/acf/cli_check_diff.py:102-107; plugins/arch-compliance/tests/test_approval.py:207`
- reasoning: Absent entry -> MISSING -> reason 'no approval for this repository' -> require_approval raises 'host detectors need approval: <reason>; ...' -> cli_check_diff prints 'acf: {exc}'. A test pins the text.

#### C6 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:102-108; plugins/arch-compliance/python/acf/approval.py:83-99; plugins/arch-compliance/python/acf/approval.py:138-139`
- reasoning: fingerprint() is SHA-256 over sorted JSON of active host rows plus per-file SHA-256 map; no path or key enters. check_approval returns STALE when the entry exists and fingerprint differs.

#### C7 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:81-83; plugins/arch-compliance/python/acf/approval.py:102-108; plugins/arch-compliance/python/acf/approval.py:125-140; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:83`
- reasoning: load_host_detector appends the repo root to sys.path so repository modules import unfingerprinted; fingerprint covers only rows and named detector files; check_approval reads nothing about HEAD, branch or helper bytes. Condition still holds.

#### C8 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:84; plugins/arch-compliance/python/acf/cli_allow.py:33-71; plugins/arch-compliance/python/acf/approval.py:157-176`
- reasoning: The cleared spec accepts that whoever can write home or run acf-allow can approve. Neither cli_allow.main nor write_approval checks the caller today, so a bypassable text hook widens no exposure.

#### C9 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/diff.py:24-30; config/architecture/ARCHITECTURE.md:274-276; plugins/arch-compliance/python/acf/cli_check_diff.py:106-108; plugins/arch-compliance/hooks/posttooluse_gate.py:141-145`
- reasoning: run_git uses text=True without encoding (locale codec, strict errors), declared debt. The claim fails at 'can only cause MISSING': under a Windows cp1252 locale, git's UTF-8 output for chars like C3 81/8D/8F/90/9D contains bytes undefined in cp1252, so subprocess.run raises UnicodeDecodeError. Per §5.1 git_common_dir returns None only on non-zero exit or OSError, so the exception propagates out of repo_key/check_approval; cli_check_diff catches only GitError/AcfInputError/UnknownDetectorError/DetectorPackError (crash with traceback); the PostToolUse hook catches only AcfInputError/UnknownDetectorError around check_approval (generic exit-2 handler). Today's key comes from Path.resolve with no subprocess decode, so such paths work now. The key also includes the absolute path with the Windows user folder name. 'Decodes the same way at approval and at check' is not guaranteed either (different PYTHONUTF8/locale between acf-allow and the gate), though that only yields MISSING. 'Never a false APPROVED' holds since the fingerprint decides.

#### C10 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:46-49; plugins/arch-compliance/python/acf/approval.py:135; plugins/arch-compliance/python/acf/approval.py:167-170; plugins/arch-compliance/python/acf/cli_allow.py:76-77; config/architecture/ARCHITECTURE.md:53-55`
- reasoning: Only check_approval, write_approval and cli_allow._revoke read/write the store by key; §5.3 moves _revoke to repo_key. ApprovalStore.repos is dict[str, ApprovalEntry]; extra=forbid constrains entry fields not keys, so leftover entries load. Side effect: --revoke in a git repo no longer removes an old root-keyed entry; harmless since inert.

#### C11 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/detectors/eslint_rules.py:58-60; C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/detectors/eslint_rules.py:40-41`
- reasoning: Lines 58-60 run subprocess.run(['node', str(ESLINT), '--stdin', ...], cwd=WEB); ESLINT is cayenne-web/node_modules/eslint/bin/eslint.js; none fingerprinted (approval.py:83-99 hashes only the named detector file).

#### C12 — UNPROVEN
- evidence: `searched the repo for permissions.deny / settings.json handling: nothing local; deny-over-hook-ask precedence is external Claude Code behaviour (permissions.md), not openable read-only here`
- reasoning: Whether a user permissions.deny rule overrides the plugin hook's ask is external behaviour not evidenced in the repo. Not load-bearing.

### Unanchored findings

- **important**: The new git subprocess in check_approval introduces a decode-crash path (UnicodeDecodeError from run_git under a cp1252 locale) into every gate run for repositories with host rows; §5.1 handles only non-zero exit and OSError, so the diff gate crashes with a traceback and the hook exits 2 where today's Path.resolve key works.
  - evidence: `plugins/arch-compliance/python/acf/diff.py:24-30`
- **advisory**: The spec silently diverges from issue #62: #62 asks that editing a detector make every worktree report STALE until re-approved once and proposes reading old root-keyed entries as migration; the spec leaves worktrees with old bytes APPROVED, lets one shared per-repository fingerprint ping-pong between parallel worktrees with differing detector bytes, and declines migration.
  - evidence: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:50-51`
- **advisory**: §1.2's 'Approval is possible only at a terminal' is a prose convention, not a mechanism; acf-allow has no caller check today, so the root-cause statement overstates the current constraint; the new hook plus CLAUDE_CODE_CHILD_SESSION guard is the first mechanical check.
  - evidence: `plugins/arch-compliance/python/acf/cli_allow.py:33-71`
- **advisory**: The cleared spec's residual at :84 rests on the superseded Decision 6, yet the Supersedes header does not list it and §4 quotes :84 as if it stands unchanged.
  - evidence: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:84`

### Looked for but did not find

- any runtime reader of ~/.acf/approvals.json other than acf/approval.py and cli_allow._revoke (grep read_store, .repos, approvals.json across plugins/ and scripts/ excluding tests)
- any existing git rev-parse --git-common-dir or --show-toplevel call in acf runtime code (only adr/citations.py uses rev-parse, for --is-shallow-repository)
- any dependence of fingerprint() on the store key, HEAD, the branch or helper-module bytes
- any caller or environment check in cli_allow.py or write_approval that would stop an agent process today
- a catch for UnicodeDecodeError around check_approval in cli_check_diff.py or posttooluse_gate.py

## compliance

### Claim verdicts

#### C13 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:53-55; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:51; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:153; plugins/arch-compliance/python/acf/approval.py:135`
- reasoning: The section forbids compatibility shims or just-in-case logic. The store is read by one key today (approval.py:135); Decision 2 replaces that key without a second lookup, and §6.1 pins that a git checkout's root-keyed entry reads MISSING. A non-git folder keeps its key because the key is unchanged, not via fallback. Not reading old keys complies; reading them would be the forbidden shim.

#### C14 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:213-222; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:130; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:83; plugins/arch-compliance/python/acf/repo.py:41-53`
- reasoning: The section governs host declarations; package defaults that are not host declarations are recorded there (e.g. resolve_repo's cwd fallback, repo.py:41-53). The folder-key fallback reads no host declaration; §5.7 records it and §5.2/§5.3 print the scope. Note: the list's count 'Three defaults' must be edited. Whether a silent in-gate fallback meets Fail loud is separate (C17).

#### C15 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_repo_tree_guard.py:12-16; plugins/arch-compliance/tests/test_repo_tree_guard.py:57-68; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:77; config/architecture/ARCHITECTURE.md:125-131`
- reasoning: The guard flags resolve/relative_to/is_relative_to/joinpath, os.path real/abs/rel/commonpath, and / joins on a root name. repo_key builds an f-string from Path(git output).as_posix() and --show-prefix; none are flagged, so no ALLOWED entry. The folder branch still goes through RepoTree(repo).root.

#### C16 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:17-30; config/architecture/ARCHITECTURE.md:299-302; plugins/arch-compliance/python/acf/adr/citations.py:51-62; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:75`
- reasoning: git_common_dir goes through run_git and adds no subprocess call, so no third runner. The paraphrase is imprecise: the doctrine records two runners as a current breach (run_git and adr/citations.py _git) pending consolidation; run_git's docstring (diff.py:20) calls itself the one place that invokes git. Conclusion unaffected.

#### C17 — UNPROVEN
- evidence: `config/architecture/ARCHITECTURE.md:31-32; config/architecture/ARCHITECTURE.md:42; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:75; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:104; plugins/arch-compliance/hooks/posttooluse_gate.py:89-94`
- reasoning: Hook half holds (matches posttooluse_gate.py:89 precedent: stderr, exit 2, token with reason). git_common_dir half not established: Fail loud says failures must not disappear and no defaulting to None to avoid a crash (:42). git_common_dir returns None on any non-zero exit and on OSError and discards git's stderr, conflating real git failures (git missing from PATH, dubious ownership, git < 2.31, corrupt repo) with 'not a git repository'. Scope is printed only by acf-allow and acf-approval-status; the gate texts (§5.5) say only 'no approval for this repository', so inside a gate the failure vanishes into a misleading MISSING. Fails closed, but recording the default elsewhere does not by itself satisfy fail-loud.

#### C18 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:179-188; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:129`
- reasoning: Within the section only the Trust boundary paragraph ties approval to a person (:180-181). Other paragraphs (:142-177) require no human-run command. §5.7 rewrites :179-186 and extends the :188 list.

#### C19 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:270-277; plugins/arch-compliance/python/acf/diff.py:24-30; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:75`
- reasoning: run_git is a named declared debt; git_common_dir adds no subprocess call so the recipe's count is unchanged; the hook reads stdin as bytes and starts no subprocess. §4's side claim about the debt's consequence is wrong (unanchored).

#### C20 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:283-284; pyproject.toml:3; plugins/arch-compliance/.claude-plugin/plugin.json:3; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:138`
- reasoning: Both read 0.3.4; the design edits skill prose and adds a skill; §5.7 and §8 item 7 bump to 0.3.5.

#### C21 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:232-233; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:110-111; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:117-123; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:101-102`
- reasoning: Gate texts, hook reasons and skill procedure use only generic terms; no host name. The section's coverage text at :239-240 goes stale (unanchored).

#### C22 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:59-60; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:77; plugins/arch-compliance/python/acf/approval.py:167-176`
- reasoning: Key is f'{common.as_posix()}::{prefix}' with git's forward-slash prefix; folder branch keeps as_posix().

#### C23 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:252-254; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:77; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:83; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:89; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:119`
- reasoning: Each new export has a live call site in the same change. Wording slip: §9 says approval.py stays RepoKey's one consumer, contradicted by §5.2/§5.3; liveness unaffected.

#### C24 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:258-261; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:31; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:127-138; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:175`
- reasoning: Enumerations are per-item with file:line; none says all/every site. Sites the table omits are filed below; per-item lists do not claim completeness. §4's 'only ... MISSING' quantifier is filed below.

### Unanchored findings

- **important**: git_common_dir conflates a genuine git failure with 'not a git repository' and discards git's stderr; in the two gates (whose §5.5 texts do not report scope) a git failure such as missing git or a dubious-ownership refusal surfaces only as 'no approval for this repository', against Fail loud's 'Failures must not disappear'.
  - evidence: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:75`
- **advisory**: §4's claim that the decoding debt 'can only cause a MISSING' is false: run_git decodes with the locale codec and strict errors and git_common_dir catches only OSError, so an undecodable path raises UnicodeDecodeError; the PostToolUse hook, which runs no git today, would exit 2 on every edit in an enabled host with host rows. Loud, not a false APPROVED.
  - evidence: `plugins/arch-compliance/python/acf/diff.py:24-30`
- **advisory**: The new acf-approve skill makes the Prose-names-no-host coverage text at :239-240 ('the other two skills ... have no row yet') false; §5.7 does not list that doctrine line and §6.5 leaves the new skill unchecked.
  - evidence: `config/architecture/ARCHITECTURE.md:239-240`
- **advisory**: The hook duplicates the store file name ('approvals.json') instead of consuming acf.approval.STORE_REL, a second definition of one constant; a test pins them, but Single point of definition records each breach ('recorded not hidden') and §5.7 does not add this one.
  - evidence: `config/architecture/ARCHITECTURE.md:297-302`
- **advisory**: The §5.7 prose table omits sites that will contradict the design: approval.py's module docstring ('keyed by the repository's resolved root'), acf-setup SKILL.md:260 ('a missing acf-allow') and the posttooluse_gate.py:16 docstring.
  - evidence: `plugins/arch-compliance/python/acf/approval.py:3-5`

### Looked for but did not find

- ## One base exception: the design adds no exception class; CLIs reuse AcfInputError/UnknownDetectorError (cli_allow.py:68). Not touched.
- ## Frozen ledger format: no LedgerRow/LedgerAmendment change. Not touched.
- ## Build artifacts, ## Fail-loud ratchet, ## Facade sinks, ## FSM transitions, ## React boundaries, ## Soft fail-loud smells: no detector, ratchet baseline, sink, FSM field or React code changes. Not touched.
- ## Scoped refactor: moving _HELPER_LIMIT into acf.approval is within the modules being changed. No unrelated module is expanded.
- ## One owner for host paths, acf.repo constants half: the new hook names no config/architecture path (test_repo_paths.py:14 regex); compliant.
- ## High-frequency misses: completeness quantifier found in §4 (filed); no default re-entering for a declared value; no host name in prose/messages; no stdlib exception mixin; no new subprocess text call without encoding; no check re-implemented in a test or skill; store-name copy filed under Single point of definition.
- ## Post-merge: host operational declarations unchanged by this design.
- unstated_mandates empty: the spec's Governing mandates line names every doctrine section this design touches; gaps found are missed edits within named sections.

## sweeper

### Claim verdicts

#### C25 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:17, plugins/arch-compliance/python/acf/diff.py:35, config/architecture/ARCHITECTURE.md:300`
- reasoning: run_git (diff.py:17-30) returns the CompletedProcess with non-zero status as data; _git (diff.py:33-39) is built on it. A helper beside it adds no runner. The only other git runner is acf/adr/citations.py:51-68, pre-existing and recorded as a breach at ARCHITECTURE.md:300-302. Imprecision: §5.1 says run_git is 'the one git runner the doctrine names'; the doctrine names two (as a breach).

#### C26 — SURVIVED
- evidence: `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:383`
- reasoning: Behavioural search for git-common-dir, common_dir, show-prefix, show-toplevel, git-dir, rev-parse, worktree across *.py and tracked tree (excluding docs/reviews). Runtime calls rev-parse only for --is-shallow-repository (adr/citations.py:78). The one --git-common-dir use is skill prose at adversarial-design-review/SKILL.md:383 (linked-worktree warning), computing no key. RepoTree.key (repo.py:133-135) is a repository-relative file key, a different job.

#### C27 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:125, plugins/arch-compliance/python/acf/detectors/__init__.py:59, plugins/arch-compliance/python/acf/cli_allow.py:58`
- reasoning: load_gate_registry, check_approval, file_digests, fingerprint are single definitions; consumers are the hook, the diff gate and acf-allow. A status CLI calling them adds no second computation. The display overlaps (see relationships) but that is presentation.

#### C28 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/hooks.json:10, plugins/arch-compliance/hooks/hooks.json:22, plugins/arch-compliance/tests/test_repo_paths.py:99`
- reasoning: hooks.json registers python "${CLAUDE_PLUGIN_ROOT}/hooks/<file>.py" command hooks (:10 SubagentStart, :22 PostToolUse). Grep for PreToolUse, permissionDecision, permissions.ask, "ask" matches only the spec under review. A stdlib-only hook is stricter than the import-light rule. But test_repo_paths.py:81-108 is a runtime poison-module subprocess test over a hard-coded tuple of two hooks (:99), not an AST check (§6.3 mislabels it). The new hook also departs from the existing activation contract that hooks no-op without .acf/enabled (hooks.json:2); Decision 4 states it, the prose sweep omits it.

#### C29 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_allow.py:27, plugins/arch-compliance/python/acf/cli_allow.py:65, plugins/arch-compliance/tests/test_cli_allow.py:68`
- reasoning: The helper-limit text exists once outside docs (cli_allow.py:27-30), printed at :65, asserted by substring at test_cli_allow.py:68. Moving it yields one constant.

#### C30 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:135, plugins/arch-compliance/python/acf/approval.py:167, plugins/arch-compliance/python/acf/cli_allow.py:76, plugins/arch-compliance/hooks/posttooluse_gate.py:142, plugins/arch-compliance/python/acf/cli_check_diff.py:102`
- reasoning: Runtime code keys the store at exactly approval.py:135, approval.py:167-173 and cli_allow.py:76-77; the hook and the diff gate go through check_approval. Caveat: tests read the store by the root key (test_approval.py:229, :236, :239-240, :265; test_cli_allow.py:70, :103); not consumers under ARCHITECTURE.md:252-253 but left keying by root (see §6.1 finding).

#### C31 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/approval.py:3, plugins/arch-compliance/skills/acf-setup/SKILL.md:260`
- reasoning: Two sites missing: acf.approval module docstring (approval.py:3-4, 'keyed by the repository's resolved root') and acf-setup/SKILL.md:260 ('a missing acf-allow'). CHECK_DIFF_HOST_WIRING.md:333 restates old wording. The name-based sweep also missed the related prose contract the design breaks: 'hooks are a true no-op until .acf/enabled' (README.md:112, docs/guides/SUPERPOWERS_COMPLEMENT.md:89, hooks.json:2, acf-setup/SKILL.md:185).

#### C32 — REFUTED
- evidence: `plugins/arch-compliance/tests/test_approval.py:209, plugins/arch-compliance/tests/test_hooks.py:554, plugins/arch-compliance/tests/test_diff_cli.py:400`
- reasoning: test_approval.py:209 asserts 'acf-allow' in the require_approval message and is missing. In test_hooks.py only the unapproved case (:554) asserts 'acf-allow'; no stale case does (:567, :591 assert only _NOTICE_HEAD). The new refusal text still contains 'acf-allow --fingerprint', so test_approval.py:209 and test_diff_cli.py:400 keep passing; the new hook notice drops 'acf-allow', so test_hooks.py:554 is the one that must change.

#### C33 — SURVIVED
- evidence: `docs/design/CHECK_DIFF_HOST_WIRING.md:333, docs/design/ARCHITECTURE_REVIEW_PORT.md:45`
- reasoning: Outside HOST_DETECTOR_LOCAL_APPROVAL.md, CHECK_DIFF_HOST_WIRING.md:333 says a host 'needs each person's acf-allow' (per person, still true at a prompt). ARCHITECTURE_REVIEW_PORT.md:45 and :205 say auditors need no acf-allow. Neither states the reversed contracts. A different Approved contract is contradicted: PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:162-165 (hooks no-op without .acf/enabled), outside this claim's scope; listed in document_conflicts.

### Unanchored findings

- **important**: Decision 4 makes the new PreToolUse hook run in every repository regardless of .acf/enabled, but §5.7 omits the tracked prose promising every plugin hook is a true no-op until .acf/enabled exists (README.md:112, docs/guides/SUPERPOWERS_COMPLEMENT.md:89, hooks.json:2, acf-setup/SKILL.md:185, Approved PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:164); with onFailure:block the new hook can block every Bash call in a repository with no marker.
  - evidence: `README.md:112`
- **important**: §6.1's claim that existing approval tests keep their outcomes even when tmp_path is inside a git repository is wrong: seven assertions index the store directly by repo.resolve().as_posix() / RepoTree(repo).root.as_posix() (test_approval.py:229, :236, :239, :240, :265; test_cli_allow.py:70, :103), which will not equal '<common>::<prefix>'. The 'plain directory -> None' case has the same tmp_path dependence (e.g. home as a dotfiles repository).
  - evidence: `plugins/arch-compliance/tests/test_approval.py:236`
- **advisory**: §6.3 requires 'the AST check test_repo_paths.py:81-108 uses'; that range is a runtime poison-module subprocess test over a hard-coded tuple of two hooks (:99), not an AST check; the only static import check is the repo.py regex at :74-78.
  - evidence: `plugins/arch-compliance/tests/test_repo_paths.py:99`
- **advisory**: acf-approval-status re-implements acf-allow's review display (rows, digests, helper limit, store-inside-repo check, cli_allow.py:56-65); the spec shares only the helper-limit text and the scope wording without an owner for the scope wording; outputs can drift.
  - evidence: `plugins/arch-compliance/python/acf/cli_allow.py:59`
- **advisory**: §5.1 calls run_git 'the one git runner the doctrine names for runtime code'; the doctrine names two (run_git and adr/citations.py _git) as a recorded breach.
  - evidence: `config/architecture/ARCHITECTURE.md:300`

### Looked for but did not find

- an existing repository identity shared across worktrees in runtime code: git-common-dir, common_dir, show-prefix, show-toplevel, git-dir, rev-parse, worktree in *.py
- an existing PreToolUse hook or permission-rule mechanism in the plugin: PreToolUse, permissionDecision, permissions.ask, "ask"
- a second copy of the imported-helper limit text: 'imported modules are not covered', HELPER_LIMIT, 'not covered'
- other runtime readers or writers of the approval store by key: read_store, .repos, store_path(, approvals.json, STORE_REL
- a prior on-record rejection of keying approvals by the git common directory in docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md (none; only the :90 residual)
- existing reads of CLAUDE_CODE_CHILD_SESSION or any agent-versus-person detection in runtime code: CLAUDE_CODE, environ in python/ and hooks/ (none)

### Relationships

- SUBSUMED: `acf.diff.git_common_dir` — responsibility `invoke git from runtime code` — existing `plugins/arch-compliance/python/acf/diff.py:17`
  - resolution: git_common_dir consumes run_git; adds no runner. The pre-existing second runner (adr/citations.py:51) stays the recorded breach, consolidated per PLUGIN_SELF_HOSTING_AND_DOCTRINE.md §9 follow-up 1.
- ADJACENT: `acf.diff.git_common_dir / acf.approval.repo_key` — responsibility `derive whether a checkout is a linked worktree of a shared repository` — existing `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:383`
  - resolution: None required.
  - non-merge: The skill line is controller prose for a ledger-merge warning and computes no key; repo_key is runtime code building a persisted store key.
- PARTIAL_OVERLAP: `acf-approval-status (cli_approval_status.main)` — responsibility `present the rows, file digests and helper limit a person reviews before approving` — existing `plugins/arch-compliance/python/acf/cli_allow.py:59`
  - resolution: Extract one renderer in acf.approval (e.g. describe_approval(repo, registry) -> lines, built on approval_rows, file_digests, fingerprint and repo_key) that both CLIs print; acf-allow keeps its write and fingerprint-match step; acf-approval-status keeps state and fingerprint lines. HELPER_LIMIT and scope wording collapse into it.
- SUBSUMED: `acf-approval-status store-in-repository handling` — responsibility `refuse a store that lies inside the repository` — existing `plugins/arch-compliance/python/acf/approval.py:121`
  - resolution: Status reaches it through check_approval (STORE_IN_REPO). The pre-existing duplicate at cli_allow.py:56 should call approval._store_inside_repo or rely on write_approval's refusal at approval.py:165.
- PARTIAL_OVERLAP: `approval_prompt.py needle 'approvals.json'` — responsibility `spell the approval store's file name` — existing `plugins/arch-compliance/python/acf/approval.py:37`
  - resolution: Deliberate second literal since the hook must not import acf; the §6.3 pinning test reconciles it. Keep it and name the hook in approval.py's STORE_REL comment.
- ADJACENT: `approval_prompt.py PreToolUse hook` — responsibility `hook activation and failure reporting (exit 2 with an 'acf:' stderr line)` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:46`
  - resolution: Update the activation contract prose (hooks.json:2, README.md:112, SUPERPOWERS_COMPLEMENT.md:89, acf-setup/SKILL.md:185) to say the approval hook is exempt from the marker.
  - non-merge: Existing hooks gate host checking behind .acf/enabled and import acf; the approval hook guards a per-user store, must run everywhere and stay stdlib-only.
- DISJOINT: `Decision 7 permissions.ask rules` — responsibility `force a permission prompt before acf-allow or a store write runs` — existing `plugins/arch-compliance/hooks/hooks.json:16`
  - resolution: None: no existing plugin mechanism forces prompts; hook and rules are two owners by design (layered).

### Two-owner counts

- invoke git from runtime code (run_git, adr/citations._git): 2
- spell the approval store file name (STORE_REL, hook needle): 2
- render the approval review: rows, digests, helper limit (acf-allow, acf-approval-status): 2
- render the approval scope text (acf-allow closing line, acf-approval-status header): 2
- refuse a store inside the repository (approval._store_inside_repo, cli_allow.py:56): 2
- force a permission prompt for approval (PreToolUse hook, permissions.ask rules): 2
- stop an agent-started approval without review (hook ask/deny, CLAUDE_CODE_CHILD_SESSION check in acf-allow): 2

### Document conflicts

- `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:164` (contradicts): The plugin's hooks run on each subagent start and each Write/Edit/MultiEdit in a repository where the plugin is installed (`plugins/arch-compliance/hooks/hooks.json`), and no-op without `.acf/enabled`
- `docs/design/CHECK_DIFF_HOST_WIRING.md:333` (restates): The local command never carries `--trusted-checkout`, so a host with host rows needs each person's `acf-allow`.
- `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:84` (contradicts): Claude Code's tool permissions govern an agent doing either; skill prose and every gate message tell the agent to leave approval to the user (Decision 6).
- `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:156` (contradicts): Ask the user to review the detector files and run acf-allow in this repository; do not run it yourself.

## hardening

### Claim verdicts

#### C34 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:135, plugins/arch-compliance/python/acf/approval.py:167, plugins/arch-compliance/python/acf/diff.py:24`
- reasoning: Both check and write key by RepoTree(repo).root, so each worktree root gets its own entry; the fingerprint (approval.py:102-108) covers only rows and file bytes, so the folder adds no review. Ran the rev-parse in the main checkout and in worktree .claude/worktrees/lucid-greider-c3b1d4: same common dir; from plugins/ the prefix is 'plugins/', so subfolder hosts are distinguished. In %TEMP% it exits 128, so non-git folders need the fallback. Not justified in the spec: why the key is not the fingerprint alone (implicitly the per-repository helper limit). Not a refutation.

#### C35 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/hooks.json:16, code.claude.com/docs/en/permissions.md:271, code.claude.com/docs/en/hooks.md:942`
- reasoning: The plugin ships hooks only via hooks.json; permissions.md:271 says a Bash rule doesn't match the same program invoked differently. The hook's substring match covers spellings Decision 7's rules miss (python3 -m, py -m, a .venv path). hooks.md:942 and :960-979 confirm onFailure 'block' turns failure/timeout/missing script into a block, from v2.1.295 (hooks.md:460). Sub-claim 'a plugin cannot ship user permission rules' not confirmed from docs; the hook is justified by the different-form point alone.

#### C36 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_allow.py:58, plugins/arch-compliance/python/acf/cli_allow.py:66, plugins/arch-compliance/python/acf/approval.py:174`
- reasoning: cli_allow computes digests once (:58) and passes them to write_approval (:66), which stores fingerprint(rows, digests) from those digests (approval.py:174). A HEX comparison between :58 and :66 binds the entry to the compared bytes; later file changes yield STALE. The env-var refusal can be defeated by overriding the variable, but that command still contains the needle and prompts; 'cannot' holds only together with the hook, which §4 concedes.

#### C37 — SURVIVED
- evidence: `code.claude.com/docs/en/permission-modes.md:34, code.claude.com/docs/en/permissions.md:380, plugins/arch-compliance/python/acf/approval.py:37`
- reasoning: 'acf-approval-status' and 'cli_approval_status' contain none of the needles. permission-modes.md:34-36: explicit ask rules not auto-approved in any mode including bypassPermissions. Caveat: permissions.md:380-384 says Write(path) rules never match, so Write(~/.acf/**) is inert; Edit(~/.acf/**) covers Write/NotebookEdit/MultiEdit, so the guarantee survives (advisory). permissions.md:669-671 user-installed mod caveat is outside the agent threat model.

#### C38 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:24`
- reasoning: Ran read-only on git 2.49.0.windows.1: repo root printed the common dir then an empty line; from plugins/ the same dir and 'plugins/'; in the linked worktree the main repository's .git and an empty line; in %TEMP% 'fatal: not a git repository' exit 128. The git >= 2.31 floor not checked against an old git.

#### C39 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:17, plugins/arch-compliance/python/acf/diff.py:29`
- reasoning: run_git calls subprocess.run(['git', ...], capture_output=True, text=True, check=False): returns CompletedProcess, never raises on non-zero; missing git raises FileNotFoundError (OSError). Caveat: locale-codec strict decoding raises UnicodeDecodeError, not caught by 'None on OSError' (advisory).

#### C40 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:135, plugins/arch-compliance/python/acf/approval.py:167, plugins/arch-compliance/python/acf/cli_allow.py:76`
- reasoning: check_approval computes the key once inline (:135); write_approval assigns key once (:167) for pop and set; _revoke assigns key once (:76) then delegates to write_approval. Swapping each for repo_key(repo).key keeps them consistent; RepoTree is still needed for _store_inside_repo and file_digests.

#### C41 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_allow.py:58, plugins/arch-compliance/python/acf/cli_allow.py:67, plugins/arch-compliance/python/acf/approval.py:102`
- reasoning: digests at :58, rows bound at :51; fingerprint at approval.py:102 importable but not yet imported; store write at :66, closing print at :67; comparison fits between :58 and :66, ideally before the prints at :59-65.

#### C42 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/__init__.py:59, plugins/arch-compliance/python/acf/registry.py:20, plugins/arch-compliance/python/acf/approval.py:125`
- reasoning: load_gate_registry (detectors/__init__.py:59, used by cli_allow.py:50), TIER1_CALL_SITES (registry.py:20), check_approval (approval.py:125), file_digests (:83), fingerprint (:102) are public module-level. check_approval returns digests only on APPROVED, so status must call file_digests itself, as §5.2 says.

#### C43 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/hooks.json:16, code.claude.com/docs/en/hooks.md:2091, code.claude.com/docs/en/hooks.md:460`
- reasoning: hooks.json uses event/matcher/command/timeout shape; hooks.md:460 onFailure from v2.1.295; PreToolUse input (hooks.md:780-797) carries permission_mode, tool_name, tool_input.command; hooks.md:1888 file_path absolute (backslashes on Windows); hooks.md:2091-2092 ask prompts and the reason is shown; hooks.md:815/:855 exit 2 blocks; | matcher is an exact-name list (:283); Bash matcher also receives Monitor (:394-399). NotebookEdit's notebook_path not documented in the PreToolUse section (minor).

#### C44 — SURVIVED
- evidence: `code.claude.com/docs/en/hooks.md:2139, code.claude.com/docs/en/permission-modes.md:34, code.claude.com/docs/en/permission-modes.md:36`
- reasoning: hooks.md:2139: in auto mode a PreToolUse 'ask' sends the call to the prompt and the classifier doesn't decide it (exceptions: protected paths, unsandboxed retries, SubagentHandback; none apply). permission-modes.md:34-36: explicit ask rules not auto-approved in any mode including bypassPermissions. User-installed mod caveat (permissions.md:669-673) requires the user's own install; not filed.

#### C45 — SURVIVED
- evidence: `code.claude.com/docs/en/env-vars.md:225`
- reasoning: env-vars.md:225: CLAUDE_CODE_CHILD_SESSION set to 1 in Bash, PowerShell, Monitor, hook and status-line subprocesses, not by IDE extensions. Own Bash env shows it set. Caveat (env-vars.md:315): inherited, so a terminal launched from inside a Claude Code Bash call has it; that user is refused without --fingerprint, failing safe.

#### C46 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/hooks.json:2, plugins/arch-compliance/hooks/hooks.json:10`
- reasoning: hooks.json:2 says python on PATH is required; both hooks run python. What changes is the consequence: with onFailure block and a Bash|PowerShell matcher, a broken python blocks every shell call in every repository. §7 records it.

#### C47 — REFUTED
- evidence: `plugins/arch-compliance/tests/test_repo_paths.py:81, plugins/arch-compliance/tests/test_repo_paths.py:74`
- reasoning: test_repo_paths.py:81-108 is test_hooks_import_repo_without_pulling_third_party: poisoned pydantic.py/yaml.py on PYTHONPATH, runs the two existing hooks, asserts exit 0. Subprocess check, not AST; does not pin stdlib-only or no acf import; no ast usage in the file. The nearest import check is test_repo_module_imports_only_stdlib (:74-78), a regex allowlist for repo.py only. The new hook needs its own check, modelled on :74-78.

#### C48 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_cli_allow.py:70, plugins/arch-compliance/tests/test_approval.py:229, plugins/arch-compliance/tests/conftest.py:10`
- reasoning: No basetemp configured; tmp_path is under %TEMP% where rev-parse exits 128, so tests get the folder key and the root-key assertions hold. The 'inside git' branch is false for those assertions (they compare repo.resolve().as_posix()); it needs a non-default basetemp. Separately, in-process main() tests don't clear CLAUDE_CODE_CHILD_SESSION and conftest's autouse fixture (:10-17) clears only HOME/USERPROFILE; run from a Claude Code Bash tool they would hit the new refusal unless conftest clears it.

#### C49 — UNPROVEN
- evidence: `code.claude.com/docs/en/permission-modes.md:30`
- reasoning: permission-modes.md:30 says deny rules block in bypassPermissions; no statement that a PreToolUse hook's deny is honoured there (hooks.md:1697 says so only for PreSkillShellCommand). Not load-bearing.

### Unanchored findings

- **advisory**: git_common_dir runs git through run_git, which inherits the environment; git exports GIT_DIR, GIT_WORK_TREE etc. to hooks, so the key computed inside the pre-push gate can differ from the key acf-allow wrote (empty prefix, or folder-key fallback for a --repo <subfolder> host), giving MISSING refusals for exactly the subfolder hosts Decision 1 promises; the spec neither clears GIT_* nor tests it (§8 item 2 covers only a top-level host).
  - evidence: `plugins/arch-compliance/python/acf/diff.py:24`
- **advisory**: Decision 7's Write(~/.acf/**) ask rule never matches (permissions.md:380-384: Write(path) rules are accepted but not matched; use Edit(path)); Edit(~/.acf/**) already covers Write/NotebookEdit/MultiEdit, so the Write rule is dead text /acf-setup would add.
  - evidence: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:56`
- **advisory**: §6.3 calls test_repo_paths.py:81-108 'the AST check'; it is a poison-module subprocess test and cannot pin stdlib-only/no-acf-import for approval_prompt.py; a new import check is needed (regex allowlist at :74-78 is the model).
  - evidence: `plugins/arch-compliance/tests/test_repo_paths.py:81`
- **advisory**: git_common_dir catches only OSError; run_git decodes with the locale codec strictly, so on Windows cp1252 a repository path with e.g. 'Á' (C3 81) raises UnicodeDecodeError in check_approval, now on the PostToolUse hook path which never ran git before; a loud crash, not the MISSING §4 calls the only outcome.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:142`
- **advisory**: The CLAUDE_CODE_CHILD_SESSION refusal will break the existing in-process acf-allow tests whenever the suite runs from a Claude Code Bash tool, because the conftest autouse fixture does not clear the variable; §6 states the rule per test, but the single-owner fix is one delenv in conftest.
  - evidence: `plugins/arch-compliance/tests/conftest.py:10`

### Looked for but did not find

- A Monitor-tool route around the hook: hooks.md:394-399 says a Bash-matcher PreToolUse hook gets Monitor commands as Bash calls
- A TOCTOU between the --fingerprint comparison and the store write: the same digests from :58 go to write_approval (:66, approval.py:174), so a later change yields STALE
- A compatibility shim reading old root keys: Decision 2 declines one
- acf-approval-status as a repair mechanism: it is read-only reporting
- A needle collision for acf-approval-status or cli_approval_status
- Other writers of the approval store besides write_approval (approval.py:157-192): none in acf/; cli_allow is the only caller

### Mechanism traces

- **repo_key fallback to the folder key**
  - invalid state: `git rev-parse --path-format=absolute --git-common-dir --show-prefix` run in repo exits non-zero, raises OSError or prints an empty first line (non-git folder, git < 2.31, git missing, safe.directory refusal, inherited GIT_DIR mismatch)
  - producer: `plugins/arch-compliance/python/acf/diff.py:24`
  - rung 5 (highest applicable 3); repairs=True
  - hardening rejected because: it is not a host declaration, it keeps an approval per folder exactly as before, and acf-allow and acf-approval-status print the scope, so it is visible rather than silent
  - spec citation: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:77`
- **PreToolUse approval hook (approval_prompt.py) forcing ask, or deny in bypass mode**
  - invalid state: a Bash/PowerShell tool_input.command containing acf-allow|cli_allow|write_approval|approvals.json, or a file tool path containing approvals.json, that runs without a user permission prompt
  - producer: `plugins/arch-compliance/python/acf/cli_allow.py:66`
  - rung 5 (highest applicable 5); repairs=False
  - hardening rejected because: Not a wall against a determined agent. The hook matches text... This design makes the honest path work remotely and the naive path prompt; it does not make the dishonest path impossible.
  - spec citation: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:53`
- **onFailure: block registration of the approval hook**
  - invalid state: approval hook crashes, times out (>10 s) or cannot start while a matching tool call is pending
  - producer: `plugins/arch-compliance/hooks/hooks.json:10`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:94`
- **acf-allow --fingerprint HEX binding**
  - invalid state: fingerprint(rows, file_digests(repo, rows)) at write time != the HEX the agent showed the user
  - producer: `plugins/arch-compliance/python/acf/cli_allow.py:58`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:87`
- **CLAUDE_CODE_CHILD_SESSION refusal of acf-allow without --fingerprint**
  - invalid state: os.environ['CLAUDE_CODE_CHILD_SESSION'] == '1' and acf-allow invoked with neither --fingerprint nor --revoke
  - producer: `plugins/arch-compliance/python/acf/cli_allow.py:33`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:88`
- **permissions.ask rules offered by /acf-setup (Decision 7)**
  - invalid state: an acf-allow / python -m acf.cli_allow invocation or a file-tool edit under ~/.acf runs without a prompt in bypassPermissions mode, or when the hook did not run
  - producer: `plugins/arch-compliance/python/acf/cli_allow.py:66`
  - rung 5 (highest applicable 5); repairs=False
  - hardening rejected because: The hook's deny in bypass mode is (unverified); the rule is the documented guarantee there.
  - spec citation: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:56`

## Claims

- **C1** [root_cause] [load-bearing]: check_approval looks the store entry up by RepoTree(repo).root.as_posix() (approval.py:135) and write_approval writes under that same key (approval.py:167); because every git worktree has its own root, a new worktree of an already-approved repository reads as MISSING even when its active host rows and detector files are byte-identical to the approved ones.
  - spec citation: `plugins/arch-compliance/python/acf/approval.py:135`
- **C2** [root_cause] [load-bearing]: Approval today can only be given by the user at a terminal: the diff gate's refusal (approval.py:149-154), the PostToolUse hook's notice (plugins/arch-compliance/hooks/posttooluse_gate.py:150-155), /acf-setup (plugins/arch-compliance/skills/acf-setup/SKILL.md:24 and :288) and /acf-mandate (plugins/arch-compliance/skills/acf-mandate/SKILL.md:139) each tell the agent to ask the user to run acf-allow and not to run it itself.
  - spec citation: `plugins/arch-compliance/python/acf/approval.py:149-154`
- **C3** [premise] [load-bearing]: In issue #62 the owner reports that Remote Control's `!` prefix does not execute a command, so a user following a session remotely cannot run acf-allow. The spec offers no file citation; the issue is readable with `gh issue view 62 --repo IanDBallard/arch-compliance-for-superpowers`. If the `!` prefix did work remotely, the permission-prompt channel would not be needed.
  - spec citation: `None`
- **C4** [premise]: The cleared spec docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md deliberately keyed approval per checkout (:90, 'each clone and each git worktree needs its own acf-allow'), and /acf-setup (acf-setup/SKILL.md:24) repeats it; the superseded items are exactly Decision 2's key (:68), Decision 6's channel (:72) and the residual at :90, with Decision 3 (fingerprint) and Decision 4 (source-only loading) standing.
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:90`
- **C5** [premise]: The #62 refusals carried the diff-gate text 'acf: host detectors need approval: no approval for this repository' — i.e. the MISSING-state reason string produced by the current code for an absent store entry. Verify the current code can produce exactly that text for an absent entry.
  - spec citation: `None`
- **C6** [premise] [load-bearing]: The fingerprint covers the active host rows and the SHA-256 digests of the detector files, and nothing in it depends on the store key; therefore re-keying the store leaves fingerprint semantics unchanged, and a worktree whose host rows or detector files differ from the approved bytes is STALE rather than APPROVED. The spec cites no line for this.
  - spec citation: `None`
- **C7** [premise] [load-bearing]: Deferral: imported helpers and executed tools are outside the fingerprint (HOST_DETECTOR_LOCAL_APPROVAL.md:83), and per-folder keying never covered them either, because `git checkout` of another branch inside an already-approved folder runs that branch's helpers under the existing approval. Verify against the current fingerprint and approval code that this condition still holds (i.e. nothing today ties approval to the branch or to helper bytes).
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:83`
- **C8** [premise] [load-bearing]: Deferral: the cleared spec already accepts that whoever can write the user's home directory or run acf-allow can approve, with Claude Code's tool permissions governing an agent doing either (HOST_DETECTOR_LOCAL_APPROVAL.md:84); so a text-matching hook that a determined agent can bypass (by importing acf.approval.write_approval in a script, or building the command string at run time) widens no exposure the cleared design had not accepted.
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:84`
- **C9** [premise] [load-bearing]: Deferral: run_git reads git output with the locale codec (acf/diff.py:24-30; declared debt at ARCHITECTURE.md:274-276), and because the key is decoded the same way at approval time and at check time, a mis-decoded non-ASCII path can only cause MISSING, never a false APPROVED. Verify run_git's decoding and that both the check path and the write path would go through the same decode.
  - spec citation: `plugins/arch-compliance/python/acf/diff.py:24-30`
- **C10** [deletion] [load-bearing]: The design removes per-folder keying for git repositories and deliberately does not read or migrate old root-keyed store entries: an old entry is never read again for a git repository (its key is no longer computed) and still matches for a non-git folder (whose key is unchanged). Verify nothing else reads the store by root key (so no live consumer breaks) and that the store schema tolerates leaving those entries in place.
  - spec citation: `config/architecture/ARCHITECTURE.md:53-55`
- **C11** [premise]: Example of an executed tool outside the fingerprint: the Cayenne detector config/architecture/detectors/eslint_rules.py (lines 58-60) runs node on the repository's ESLint with the repository's configuration, none of which is fingerprinted. The sibling checkout is at C:/Users/iball/Arduino/Projects/Cayenne.
  - spec citation: `C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/detectors/eslint_rules.py:58-60`
- **C12** [premise]: Deferral, downgraded: a user who wants no remote approval can set a Claude Code permissions.deny rule for acf-allow; automating it is out of scope. If false, the design is the same (the rule is a user-side opt-out only).
  - spec citation: `None`
- **C13** [mandate] [load-bearing]: `## No shims`: not reading old root-keyed entries as a fallback complies, and reading them would be a compatibility shim the section forbids.
  - spec citation: `config/architecture/ARCHITECTURE.md:53-55`
- **C14** [mandate] [load-bearing]: `## Declared, never defaulted`: the fallback from the repository key to the folder key (when git cannot report a common directory) is not a host declaration; recording it in the section's list of recorded defaults, and printing the scope in acf-allow and acf-approval-status, satisfies the mandate.
  - spec citation: `config/architecture/ARCHITECTURE.md:213-228`
- **C15** [mandate] [load-bearing]: `## One owner for host paths`: approval.py will join two strings git printed and resolve nothing itself, so it adds no host-path resolution outside RepoTree and needs no allowlist entry in test_repo_tree_guard.py.
  - spec citation: `config/architecture/ARCHITECTURE.md:115-138`
- **C16** [mandate] [load-bearing]: `## Single point of definition`: the new acf.diff.git_common_dir is built on acf.diff.run_git (diff.py:17), the one git runner the doctrine names for runtime code, so it introduces no second git runner.
  - spec citation: `config/architecture/ARCHITECTURE.md:295-317`
- **C17** [mandate] [load-bearing]: `## Fail loud`: git_common_dir returning None on a non-zero git exit or OSError is a recorded fallback (C14), not a swallowed error; and the new hook's broad exception handler is compliant because it prints to stderr, exits 2 (blocking the call) and carries the `fail-loud.bare-except-ok` exemption token with a reason.
  - spec citation: `config/architecture/ARCHITECTURE.md:26-43`
- **C18** [mandate] [load-bearing]: `## Host detectors and call sites` trust boundary: the design changes who may start acf-allow (an agent may, the user's permission-prompt answer approves); revising the Trust boundary paragraph (:179-186) and its closing test list (:188) as §5.7 states keeps the doctrine consistent with the code, and nothing else in that section requires a human-run terminal command.
  - spec citation: `config/architecture/ARCHITECTURE.md:179-186`
- **C19** [mandate] [load-bearing]: `## Declared text decoding`: using run_git (which lacks a declared encoding) for the new key computation is permitted because run_git's decoding is already declared debt in that section; the design adds a consumer of declared debt rather than a new undeclared decode.
  - spec citation: `config/architecture/ARCHITECTURE.md:274-276`
- **C20** [mandate]: `## Release discipline`: the design changes skill prose and adds a skill, so it must bump pyproject.toml:3 and plugins/arch-compliance/.claude-plugin/plugin.json:3 from 0.3.4 to 0.3.5.
  - spec citation: `config/architecture/ARCHITECTURE.md:283-284`
- **C21** [mandate]: `## Prose names no host`: the new gate-message texts (§5.5) and the acf-approve skill name no host repository.
  - spec citation: `config/architecture/ARCHITECTURE.md:232-233`
- **C22** [mandate]: `## POSIX paths`: the stored key uses as_posix() on the git common dir, so keys are POSIX on every platform.
  - spec citation: `config/architecture/ARCHITECTURE.md:57-66`
- **C23** [mandate]: `## Live consumers`: each new function and constant (git_common_dir, repo_key/RepoKey, HELPER_LIMIT in acf.approval, cli_approval_status.main) has a live consumer in the same change.
  - spec citation: `config/architecture/ARCHITECTURE.md:250-254`
- **C24** [mandate]: `## No completeness claims`: the spec's enumerations of sites (gate messages, prose sites, tests to update) are given as per-item lists rather than universal claims.
  - spec citation: `config/architecture/ARCHITECTURE.md:256-266`
- **C25** [shape_fit] [load-bearing]: git_common_dir extends the existing acf.diff git-runner shape (placed beside run_git) and creates no second way to run git from runtime code.
  - spec citation: `plugins/arch-compliance/python/acf/diff.py:17`
- **C26** [shape_fit] [load-bearing]: Nothing in the tracked tree already computes a repository identity shared by worktrees (for example a helper calling `git rev-parse --git-common-dir`); repo_key therefore creates no second way to identify a repository. The spec cites nothing for this absence.
  - spec citation: `None`
- **C27** [shape_fit] [load-bearing]: acf-approval-status reuses the existing load_gate_registry, check_approval, file_digests and fingerprint functions, so there is still exactly one way to compute an approval state and a fingerprint.
  - spec citation: `plugins/arch-compliance/python/acf/cli_allow.py:50`
- **C28** [shape_fit] [load-bearing]: The new PreToolUse approval hook fits the plugin's existing hook shape: hooks.json already registers command hooks run as `python "${CLAUDE_PLUGIN_ROOT}/hooks/<file>.py"` (SubagentStart and PostToolUse), no existing PreToolUse hook or permission mechanism in the plugin already does this job, and the new hook keeps the existing import-light rule for hooks (test_repo_paths.py:81-108).
  - spec citation: `plugins/arch-compliance/hooks/hooks.json:2`
- **C29** [shape_fit]: Moving the imported-helper limit text from cli_allow.py:27-30 to acf.approval.HELPER_LIMIT gives the two scripts one text instead of two.
  - spec citation: `plugins/arch-compliance/python/acf/cli_allow.py:27-30`
- **C30** [sweep] [load-bearing]: The only places that read or write the approval store by key are check_approval (approval.py:135), write_approval (approval.py:167) and cli_allow's _revoke (cli_allow.py:74-83); switching those three to repo_key(repo).key re-keys every consumer, so no consumer is left keying by the worktree root.
  - spec citation: `plugins/arch-compliance/python/acf/approval.py:135`
- **C31** [sweep]: The tracked prose and code that describe per-checkout approval or tell the agent never to run acf-allow are: approval.py:149-154, posttooluse_gate.py:150-155, cli_allow.py:1-5, acf-setup/SKILL.md:24,:185,:187,:206,:262,:288 (and its hook table :189-198), acf-mandate/SKILL.md:139, README.md:26-35,:64,:105-112 (and :143, kept as history), docs/guides/SUPERPOWERS_COMPLEMENT.md:89, hooks.json:2, and ARCHITECTURE.md:179-188. A site missing from this list would be left contradicting the new design.
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:24`
- **C32** [sweep]: The tests that assert the acf-allow wording of the hook notice or the diff-gate refusal are the test_hooks.py unapproved and stale cases and the test_diff_cli.py no-approval refusal; no other test asserts that text.
  - spec citation: `None`
- **C33** [shape_fit]: No tracked Approved design document other than docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md states a contract (per-checkout approval key, or human-only acf-allow) that this design contradicts without superseding it.
  - spec citation: `None`
- **C34** [mechanism_justification] [load-bearing]: Keying by `<git common dir>::<show-prefix>` (rather than the worktree root) is justified because the folder adds no review; the prefix is needed so two hosts in one repository do not flip each other STALE; and the folder fallback is needed for non-git directories.
  - spec citation: `None`
- **C35** [mechanism_justification] [load-bearing]: A plugin-shipped PreToolUse hook (rather than permission rules alone) is justified because a plugin cannot ship user permission rules, and a permission rule does not match the same program started another way (e.g. `python -m acf.cli_allow`), which the hook's text match covers; registering it with onFailure 'block' is justified so a crashed or missing hook cannot let an approval through.
  - spec citation: `None`
- **C36** [mechanism_justification] [load-bearing]: The `--fingerprint HEX` binding in acf-allow is needed so the bytes the user approves at the prompt are exactly the bytes the agent summarized; and refusing acf-allow without --fingerprint when CLAUDE_CODE_CHILD_SESSION=1 is needed so an agent cannot obtain an approval of unreviewed bytes through the prompt.
  - spec citation: `None`
- **C37** [mechanism_justification] [load-bearing]: A separate read-only `acf-approval-status` command (whose name contains none of the hook's needles) is needed so the agent can gather the review material without triggering the prompt; and /acf-setup's offered permissions.ask rules are needed as the documented guarantee in bypassPermissions mode, where the hook's deny is unverified.
  - spec citation: `None`
- **C38** [implementability] [load-bearing]: `git rev-parse --path-format=absolute --git-common-dir --show-prefix` prints two lines — the absolute common dir, then the prefix with a trailing `/` (an empty line at the top level) — and in a linked worktree prints the main repository's .git as the common dir; it needs git >= 2.31. Verifiable by running it read-only in this repository and in a linked worktree (git worktree list shows existing worktrees).
  - spec citation: `None`
- **C39** [implementability] [load-bearing]: acf.diff.run_git(repo, *args) (diff.py:17) returns a result exposing the exit code and stdout without raising on a non-zero git exit, and raises OSError (e.g. FileNotFoundError) when git cannot be started — so git_common_dir can be written on it with the stated None-returning behaviour.
  - spec citation: `plugins/arch-compliance/python/acf/diff.py:17`
- **C40** [implementability] [load-bearing]: check_approval (approval.py:135), write_approval (approval.py:167) and cli_allow._revoke (cli_allow.py:74-83) each compute the store key in one expression that can be replaced by repo_key(repo).key without other changes to their logic.
  - spec citation: `plugins/arch-compliance/python/acf/approval.py:135`
- **C41** [implementability] [load-bearing]: In cli_allow.py, `digests = file_digests(repo, rows)` is at :58 and fingerprint(rows, digests) is computable at that point, so the --fingerprint comparison can be placed after it and before the store write; the closing print is at :67.
  - spec citation: `plugins/arch-compliance/python/acf/cli_allow.py:58`
- **C42** [implementability] [load-bearing]: load_gate_registry, check_approval(repo, registry, TIER1_CALL_SITES), file_digests and fingerprint are importable functions (and TIER1_CALL_SITES an importable constant) that cli_approval_status can call to print the state, digests and the exact fingerprint acf-allow --fingerprint compares against.
  - spec citation: `plugins/arch-compliance/python/acf/cli_allow.py:50`
- **C43** [implementability] [load-bearing]: Claude Code's plugin hooks.json accepts a PreToolUse entry with a matcher `Bash|PowerShell|Write|Edit|MultiEdit|NotebookEdit`, a command hook, `timeout`, and `"onFailure": "block"` (Claude Code v2.1.295+); a PreToolUse hook's stdin JSON carries `permission_mode`, `tool_name` and `tool_input` (command / file_path / notebook_path); printing hookSpecificOutput with permissionDecision 'ask' or 'deny' and a permissionDecisionReason is honoured, the reason is shown in the prompt, and exit code 2 blocks the call. External: https://code.claude.com/docs/en/hooks.md (fetchable read-only with `curl -s`).
  - spec citation: `plugins/arch-compliance/hooks/hooks.json:2`
- **C44** [implementability] [load-bearing]: In auto mode a hook's 'ask' goes to the person's permission prompt and is not decided by the auto-mode classifier, and an explicit permissions.ask rule prompts in every mode including bypassPermissions — so the agent cannot approve itself through the classifier or bypass mode. External: https://code.claude.com/docs/en/hooks.md and https://code.claude.com/docs/en/permission-modes.md (fetchable read-only with `curl -s`).
  - spec citation: `None`
- **C45** [implementability] [load-bearing]: Claude Code sets CLAUDE_CODE_CHILD_SESSION=1 in the environment of the Bash and PowerShell subprocesses it starts (and not in a user's own terminal), so acf-allow can tell it was started by Claude Code. External: https://code.claude.com/docs/en/env-vars.md; also observable read-only from your own Bash tool's environment.
  - spec citation: `None`
- **C46** [implementability]: The plugin already requires `python` on PATH for its existing hooks (hooks.json), so the new hook adds no new runtime dependency.
  - spec citation: `plugins/arch-compliance/hooks/hooks.json:2`
- **C47** [implementability]: test_repo_paths.py:81-108 contains an AST-based check that a hook imports only light modules, which can be applied to the new hook file to pin 'standard library only'.
  - spec citation: `plugins/arch-compliance/tests/test_repo_paths.py:81-108`
- **C48** [implementability]: The existing tests in test_approval.py and test_cli_allow.py keep their outcomes under repo_key, because they compare check and write in the same tmp_path directory (folder key when tmp_path is outside git, a distinct repository key from its prefix when inside). Note test_cli_allow.py asserts on the store key itself in some cases.
  - spec citation: `None`
- **C49** [implementability]: A PreToolUse hook's 'deny' is honoured in bypassPermissions mode (marked unverified in the spec; downgraded because Decision 7's ask rule is the stated guarantee there, so the design is the same if false).
  - spec citation: `None`
