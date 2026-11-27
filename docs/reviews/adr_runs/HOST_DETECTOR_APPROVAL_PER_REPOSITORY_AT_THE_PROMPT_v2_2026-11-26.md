# Adversarial design review — full detail

Spec: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md` @ `82dd64323616a560b4fd4cec965249ae0237bd46`
Kinds: defect, feature
Outcome: **BLOCKED**
Claims: 51 · Reviewers: 4 · Converged: 1

## Blocking reasons

- load-bearing claim C9 (premise) is SURVIVED but its evidence ('plugins/arch-compliance/python/acf/diff.py:24-30; C:/Python313/Lib/subprocess.py Popen._communicate (Windows branch) and Popen._readerthread') merely restates the spec's own citation ('plugins/arch-compliance/python/acf/diff.py:24-30') — not independent verification, treated as UNPROVEN
- implementability claim C51 is UNPROVEN: Neither hooks.md nor permission-modes.md says explicitly that a PreToolUse JSON 'deny' is honoured in bypassPermissions. permission-modes.md:30 covers deny rules, not hook decisions. permissions.md:683 says a hook exiting 2 stops the call before permission rules are evaluated, which strongly suggests a hook block holds in bypass mode but still does not name the mode. The spec already marks this unverified and does not rest on it (Decision 7's ask rule is the stated guarantee).

## Absorptions

- PARTIAL_OVERLAP: "hooks/approval_prompt.py needle 'approvals.json'" shares responsibility 'define the approval store file name' with plugins/arch-compliance/python/acf/approval.py:37 — STORE_REL stays canonical. The hook's literal copy is pinned to STORE_REL.name by test_approval_prompt.py and recorded under ## Single point of definition, as §5.3/§5.7 already propose.
- SUBSUMED: 'acf.approval.describe_approval' shares responsibility 'render the approval review (rows, file digests, helper limit)' with plugins/arch-compliance/python/acf/cli_allow.py:58 — cli_allow's loop at :58-65 collapses into describe_approval, as the spec states, and _HELPER_LIMIT moves to acf.approval.HELPER_LIMIT.

## Converged findings

- [2 reviewers: refuter, sweeper] The Supersedes header omits lines of the cleared spec HOST_DETECTOR_LOCAL_APPROVAL.md that this design replaces, above all the require_approval message text at :127 that §5.5 rewrites.
  - evidence: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:127`
  - evidence: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:176`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:135; plugins/arch-compliance/python/acf/approval.py:167; plugins/arch-compliance/python/acf/repo.py:113; plugins/arch-compliance/python/acf/cli_allow.py:76; `git worktree list` shows linked worktrees under .claude/worktrees/ with roots distinct from the main checkout`
- reasoning: check_approval reads read_store(store).repos.get(RepoTree(repo).root.as_posix()) at :135 and write_approval writes data.repos[key] with key = RepoTree(repo).root.as_posix() at :167. RepoTree.__init__ sets self.root = root.resolve() (repo.py:113), so the key is the resolved folder. A linked worktree has a different folder, so its lookup misses and :136-137 returns MISSING before the fingerprint is compared, whatever its bytes are. cli_allow._revoke uses the same key (:76).

#### C2 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:150-154; plugins/arch-compliance/hooks/posttooluse_gate.py:150-155; plugins/arch-compliance/skills/acf-setup/SKILL.md:24; plugins/arch-compliance/skills/acf-setup/SKILL.md:288; plugins/arch-compliance/skills/acf-mandate/SKILL.md:139; plugins/arch-compliance/python/acf/cli_allow.py:33-71`
- reasoning: Each cited message or skill line tells the agent to have the user run acf-allow and not to run it itself (posttooluse :152-154 says 'do not run it yourself'; acf-setup :24 and :288 say never/do not run acf-allow; acf-mandate :139 says never run it). cli_allow.main parses --repo/--revoke, loads the registry, checks only that the store is outside the repo (:56), and writes. It inspects nothing about who called it: no environment, tty or parent-process check. write_approval (approval.py:157-176) checks only store containment.

#### C3 — SURVIVED
- evidence: ``gh issue view 62 --repo IanDBallard/arch-compliance-for-superpowers` output; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:58`
- reasoning: I fetched issue #62 myself. It is open and filed by the owner, and its Problem section says the owner had to run acf-allow by hand at the machine for each worktree '(Remote Control's `!` does not execute)'. So the issue can be read with the stated command and backs the premise.

#### C4 — REFUTED
- evidence: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:68; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:72; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:73; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:84; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:90; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:127; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:156; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:251; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:162-164`
- reasoning: The listed lines match: :68 is the root key, :72 Decision 6, :84 the two-clause residual, :90 'One approval per checkout directory', :156 the hook notice, and PLUGIN_SELF_HOSTING :162-164 the no-op statement. The closing claim 'No other part of those specs is contradicted' is false. Three more parts of the cleared spec are contradicted and not superseded. (1) :127 fixes the require_approval message text ('Ask the user to review the detector files and run acf-allow; ...'), and §5.5 replaces it. (2) Decision 7 at :73 has the hook notice name 'the command to run', but the new notice in §5.5 names the acf-approve skill and no command. (3) The test expectation at :251 says additionalContext/systemMessage 'contain `acf-allow`', and §6.4 says the new notice no longer contains acf-allow. Also, PLUGIN_SELF_HOSTING :162-163 says the plugin's hooks run on 'each subagent start and each Write/Edit/MultiEdit'. The new hook also runs on Bash, PowerShell and NotebookEdit, and only the no-op clause is superseded.

#### C5 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:112-113; plugins/arch-compliance/python/acf/approval.py:150-151; plugins/arch-compliance/python/acf/cli_check_diff.py:102; plugins/arch-compliance/python/acf/cli_check_diff.py:106-107`
- reasoning: reason(MISSING) returns 'no approval for this repository' (:113). require_approval raises AcfInputError with message f'host detectors need approval: {reason(...)}; ...' (:151). cli_check_diff calls require_approval (:102), catches AcfInputError and prints f'acf: {exc}' (:106-107). Together that gives 'acf: host detectors need approval: no approval for this repository'.

#### C6 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:102-108; plugins/arch-compliance/python/acf/approval.py:79-80; plugins/arch-compliance/python/acf/approval.py:83-99; plugins/arch-compliance/python/acf/approval.py:138-139`
- reasoning: fingerprint() hashes the JSON of the rows' model_dump and the digests map only (:102-108). The rows are approval_rows, every active TIER1 host row (:79-80), and the digests are SHA-256 of the named files (:83-99). No key or path to the repository enters it. When an entry exists, check_approval returns STALE if the stored fingerprint differs (:138-139). So a worktree that shares the key but has different bytes reads STALE. One caveat: a missing detector file raises AcfInputError from file_digests (:92-95) instead of returning STALE.

#### C7 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:82; plugins/arch-compliance/python/acf/approval.py:102-108; docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:83`
- reasoning: load_host_detector appends the repository root to sys.path (host.py:82), so any repository module can be imported. The fingerprint covers only rows and the named detector files (approval.py:102-108). With per-folder keying, a branch checkout in the same folder keeps the same key, and if the detector files are unchanged the fingerprint matches, so the other branch's helpers run under the existing approval. Nothing in approval.py reads the branch or HEAD.

#### C8 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:84; plugins/arch-compliance/python/acf/cli_allow.py:33-71; plugins/arch-compliance/python/acf/approval.py:157-176`
- reasoning: The first clause at :84 reads 'Whoever can write the user's home directory, or run `acf-allow`, can approve.' cli_allow.main does no caller check, and write_approval checks only that the store is outside the repo (:165-166) before writing. So today a script that imports write_approval can already approve, and a hook that matches text adds no new path for it.

#### C9 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:24-30; C:/Python313/Lib/subprocess.py Popen._communicate (Windows branch) and Popen._readerthread`
- reasoning: run_git calls subprocess.run with capture_output=True and text=True and no encoding (diff.py:24-30), so it decodes with the locale codec. In the Windows _communicate I read from the installed CPython 3.13.2, stdout is read by a daemon thread running _readerthread (buffer.append(fh.read())). An exception in that thread leaves the buffer empty, and _communicate sets stdout = stdout[0] if stdout else None. So a decode error leaves stdout None and nothing is raised to the caller. UTF-8 'Á' is C3 81, and 0x81 is undefined in cp1252, which matches the quoted 'charmap' error. I did not run the experiment; the mechanism is established from source.

#### C10 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:46-49; plugins/arch-compliance/python/acf/approval.py:135; plugins/arch-compliance/python/acf/approval.py:167-170; plugins/arch-compliance/python/acf/cli_allow.py:67; plugins/arch-compliance/python/acf/cli_allow.py:76-77; plugins/arch-compliance/tests/test_hooks.py:406-407; plugins/arch-compliance/tests/test_diff_cli.py:346-347; config/architecture/ARCHITECTURE.md:53-55`
- reasoning: git grep over plugins/ and scripts/ for read_store, .repos and root.as_posix finds only these production readers of the store key: approval.py:135 and :167-173, and cli_allow.py:67 and :76-77. The spec re-keys every one of them (§5.1, and §5.3 item 4 for :67). The test helpers _approve in test_hooks and test_diff_cli go through write_approval, so they follow the new key. The root-key assertions in test_approval and test_cli_allow are listed in §6.1. ApprovalStore.repos is dict[str, ApprovalEntry] (:49), so leftover entries still parse, and write_approval carries them through its read-modify-write. ARCHITECTURE.md:53-55 forbids compatibility shims, as quoted.

#### C11 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/detectors/eslint_rules.py:58-60; C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/detectors/eslint_rules.py:41`
- reasoning: :41 sets ESLINT = WEB/node_modules/eslint/bin/eslint.js, and :58-60 start subprocess.run(['node', str(ESLINT), '--stdin', ...], cwd=WEB). So the detector runs the repository's own node_modules ESLint and config, and none of those files is fingerprinted.

#### C12 — SURVIVED
- evidence: `C:/Program Files/Git/mingw64/share/doc/git-doc/git-rev-parse.html:757; plugins/arch-compliance/python/acf/diff.py:24-30; commands run with git 2.49.0.windows.1 in the repo root, plugins/, linked worktree .claude/worktrees/lucid-greider-c3b1d4 and $TEMP`
- reasoning: I ran the command myself. The repo root printed '<repo>/.git' then an empty line. plugins/ printed the same common dir then 'plugins/'. The linked worktree lucid-greider-c3b1d4 printed the same '<repo>/.git', and 'plugins/' in its subfolder. In $TEMP (/tmp, outside any repo) it printed 'fatal: not a git repository (or any of the parent directories): .git' with exit=128. git-rev-parse.html:757 documents --path-format.

#### C13 — SURVIVED
- evidence: `C:/Program Files/Git/mingw64/share/doc/git-doc/githooks.html:480; C:/Program Files/Git/mingw64/share/doc/git-doc/git-rev-parse.html:750-753; commands run in .claude/worktrees/lucid-greider-c3b1d4/plugins`
- reasoning: githooks.html:480 says GIT_DIR, GIT_WORK_TREE etc. are exported to hooks. In the linked worktree's plugins/ folder, with GIT_DIR set to that worktree's git dir and GIT_WORK_TREE unset, the prefix line came out empty; with GIT_DIR unset it was 'plugins/'. `git rev-parse --local-env-vars` run in /tmp exited 0 and listed GIT_DIR, GIT_WORK_TREE, GIT_COMMON_DIR, GIT_CONFIG_PARAMETERS, GIT_CONFIG_COUNT and others (documented at git-rev-parse.html:750-753). I did not observe a real pre-push hook environment; the documentation says such variables are exported. I did not check the specific claim that the main checkout's pre-push leaves GIT_DIR unset.

#### C14 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:35; plugins/arch-compliance/python/acf/diff.py:56; plugins/arch-compliance/python/acf/diff.py:68; plugins/arch-compliance/python/acf/review/rollup.py:57; plugins/arch-compliance/python/acf/review/rollup.py:78; plugins/arch-compliance/python/acf/review/rollup.py:82; plugins/arch-compliance/python/acf/review/rollup.py:90; plugins/arch-compliance/skills/architecture-review/SKILL.md:289; plugins/arch-compliance/python/acf/cli_check_diff.py:28; plugins/arch-compliance/python/acf/cli_check_diff.py:106`
- reasoning: git grep for run_git and _git( over plugins/ and scripts/, excluding tests, finds exactly the listed sites. The only other importer of acf.diff is cli_check_diff (changed_files/added_lines), which already catches GitError at :106. rollup's existing outcomes are 'unresolved' with stderr (:86, :95). The rev-list --count (:57) and merge-base (:90) stdouts are ASCII. The ls-files (:82) stdout is a path that git quotes by default, so only the blame call can realistically hit undecodable stdout, and the design catches that one. One small omission: test_diff_cli.py:215-255 also calls run_git and _git directly, and those assertions still hold under UTF-8 decoding.

#### C15 — SURVIVED
- evidence: `.github/workflows/ci.yml:11; .github/workflows/ci.yml:20; CLAUDE.md:37-38`
- reasoning: CI runs on ubuntu-latest (ci.yml:11) with Python 3.12 (:20). On Linux, the default runner locale is UTF-8, and PEP 538 coerces a C locale to UTF-8, so text=True decodes UTF-8 there. CLAUDE.md:37-38 tells Windows users to run the diff gate with PYTHONUTF8=1, which makes text=True decode UTF-8. The runner's locale comes from platform knowledge, not from a file in this repository.

### Unanchored findings

- **advisory**: The Supersedes header leaves out parts of the cleared spec that this design contradicts: the require_approval message text (:127), Decision 7's notice naming 'the command to run' (:73), and the test expectation that the hook notice contains acf-allow (:251).
  - evidence: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:127`
- **advisory**: PLUGIN_SELF_HOSTING item 11 says the plugin's hooks run only on subagent start and Write/Edit/MultiEdit. The new PreToolUse hook also matches Bash, PowerShell and NotebookEdit, and the spec supersedes only the item's no-op clause.
  - evidence: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:162-163`
- **advisory**: Issue #62's acceptance asks that editing a detector file in any worktree make every worktree STALE. Under the spec, the edited worktree goes STALE and the main checkout stays APPROVED (§6.1). The spec explains why it declines #62's migration proposal but not why it departs from this acceptance criterion.
  - evidence: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:333`

### Looked for but did not find

- a production reader of the approval store key other than approval.py:135/:167 and cli_allow.py:67/:76-77 (git grep for read_store, .repos and root.as_posix over plugins/ and scripts/)
- a test that hand-writes a store entry keyed by the root into a git repository (grep for ApprovalEntry, "repos" and _approve in plugins/arch-compliance/tests)
- a run_git or diff._git caller outside diff.py, rollup.py, the architecture-review skill snippet and tests (git grep for run_git and acf.diff)
- any caller-identity check (environment variable, tty, parent process) in cli_allow.main or write_approval

## compliance

### Claim verdicts

#### C16 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:53-55; plugins/arch-compliance/python/acf/approval.py:135; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:96-99,171`
- reasoning: The section forbids "compatibility shims, or 'just-in-case' logic to mask architectural misalignments". Today's lookup (approval.py:135) reads exactly one key. The design swaps that key for repo_key(repo).key at the same three sites (spec :171) and adds no second lookup under the old root key. A fallback read of the old root-keyed entries would be the just-in-case bridge the section forbids. Non-git folders keep their old key because the key is unchanged, not because of a fallback.

#### C17 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:192-194,213-218; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:94,184,189,283`
- reasoning: The rule binds host declarations: adr.yml and review.yml values, where 'no default stands in for a missing declaration'. It records the package defaults outside that scope ('Three defaults elsewhere in the package are outside this rule and recorded here'). The approval key is not a host declaration. The folder key applies only when git says the directory is not a repository (exit 128 plus that message, spec :94). Every other git outcome raises, so it never stands in for a value the host declared. The design records it as a fourth default (spec :283) and prints the scope (spec :189). This matches how resolve_repo's fallback is recorded at :215-216.

#### C18 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:125-131; plugins/arch-compliance/tests/test_repo_tree_guard.py:12-17,59-66; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:164,169,173`
- reasoning: The section makes RepoTree the one place where runtime code 'turns a path string into a location in the host repository'. Callers never 'join, resolve or compare against the root'. repo_key formats a store key, f"{common.as_posix()}::{prefix}", from git's two printed lines (spec :164, :169) and uses it as a dict key, not as a location to open. The non-git branch reuses RepoTree(repo).root, as approval.py:135 does today. The guard flags `.resolve`, `relative_to`, `joinpath`, `os.path` real/abs/rel/commonpath calls and `root / x` joins (test_repo_tree_guard.py:12-14, 59-66). The design uses none of them, so no allowlist entry is needed.

#### C19 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:297-302; plugins/arch-compliance/python/acf/diff.py:17-30; plugins/arch-compliance/python/acf/approval.py:37; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:154,163,235,288`
- reasoning: The section requires one canonical implementation and lists current breaches as 'recorded not hidden'. git_common_dir calls run_git twice (spec :161, :163), and the env keyword is a parameter of that runner (spec :154). Neither adds a third git runner beside diff.py:17 and citations.py:51. The hook's literal 'approvals.json' copies STORE_REL.name (approval.py:37). The design records that copy in this section (spec :288), comments it at STORE_REL and pins it with a test (spec :235), as the section's practice asks. A related duplication the spec does not record is filed separately.

#### C20 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:28-32; plugins/arch-compliance/python/acf/cli_check_diff.py:106-108; plugins/arch-compliance/hooks/posttooluse_gate.py:87-94,140-145; plugins/arch-compliance/python/acf/cli_allow.py:47-49,68-70; plugins/arch-compliance/python/acf/exceptions.py:33`
- reasoning: The rule is that errors surface and broad handlers carry an exemption with a reason. GitError subclasses AcfError (exceptions.py:33). cli_check_diff already catches it and exits 1 (:106-108). The PostToolUse hook's check_approval handler (:140-145) gains GitError, and even without it the hook's catch-all exits 2 (:87-94). In cli_allow, _revoke is called inside the try (:47-49), so adding GitError at :68 covers both the revoke path and the approve path. The None return is bounded to exit 128 plus 'not a git repository' under LC_ALL=C (spec :164-165). The new hook's handler prints to stderr, exits 2 and carries fail-loud.bare-except-ok with a reason, mirroring posttooluse_gate.py:89. rollup.provenance turning GitError into ('unresolved', message) is the module's existing report-only outcome for git failures, not a silent swallow.

#### C21 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:179-188; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:282`
- reasoning: Within the section, the only text that has a person run the approval is ':179-181 (`acf-allow`, run by the user)'. Reference syntax, the HostHit contract, the call-site rule and built-in contracts (:142-177) say nothing about who approves. The §5.7 row (spec :282) rewrites :179-186 to the repository key and the prompt-given approval, and adds the two new tests to the :188 enforcement list. The statements 'PostToolUse hook also needs .acf/enabled' and 'Committing .acf/ approves no host code' stay true under the design.

#### C22 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:270-277; plugins/arch-compliance/python/acf/diff.py:24-30; plugins/arch-compliance/python/acf/adr/citations.py:59-62; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:120-126`
- reasoning: The rule asks every subprocess call that reads text in runtime code to declare encoding="utf-8", and its recipe greps for text=True. run_git today uses text=True without an encoding (diff.py:24-30). Capturing bytes and decoding strict UTF-8 itself declares the decoding explicitly and takes run_git out of the recipe's hits. The other two breaches stay and are re-cited correctly: citations.py's subprocess.run is at :59-61 (text=True at :61), and typescript_bridge.py's is at :120-126. Those match the spec's corrected line numbers.

#### C23 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:283-284; pyproject.toml:3; plugins/arch-compliance/.claude-plugin/plugin.json:3`
- reasoning: The rule reads 'A change to a skill's prose bumps the plugin version in plugin.json and pyproject.toml.' Both files read 0.3.4 at line 3 today. The design edits acf-setup and acf-mandate prose and adds acf-approve, and bumps both to 0.3.5 (spec §5.7 last row, §8 item 7).

#### C24 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:232-233; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:236-237,249-250,256-272`
- reasoning: The rule reads 'Skill prose and runtime messages name no host repository, path or section.' The hook's deny and ask reasons (spec :236-237), the two gate messages (spec :249-250) and the acf-approve procedure (spec :256-272) name only plugin commands, skills and generic git invocations. No host repository, path or section appears in them. The cy: references stay in the spec's problem statement and are not shipped prose.

#### C25 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:59-60; plugins/arch-compliance/python/acf/approval.py:49,135; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:164,169`
- reasoning: The rule reads 'When persisting paths to YAML/JSON, use Path.as_posix()'. The key is persisted as a dict key in the JSON store (approval.py:49). The design builds it as common.as_posix() plus git's --show-prefix line, which git prints with forward slashes and the design strips of its trailing '/' (spec :164, :169). The folder key keeps RepoTree(repo).root.as_posix(), as approval.py:135 does today.

#### C26 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:252-253; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:161-163,169-171,193-195,198,258`
- reasoning: The rule reads 'An export has a live call site in the package, a hook or a skill.' Each new export has one in the same change. The env keyword is used by git_common_dir (spec :162-163). git_common_dir is used by repo_key (:169). repo_key is used by check_approval, write_approval and _revoke (:171). describe_approval is used by acf-allow and acf-approval-status (:195). HELPER_LIMIT is used by describe_approval (:193). cli_approval_status.main is a console script (:198) that the acf-approve skill runs (:258). RepoKey is repo_key's return type.

#### C27 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:258-261; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:157,175,276-278,351,393`
- reasoning: The rule allows a quantified claim about the tree when 'a recipe that a reader can re-run backs the quantifier'. Each enumeration has one: run_git callers (spec :157), GitError entry points (:175), prose sites (:278, with the explicit disclaimer at :276), root-keyed test assertions (:351) and gate-message tests (:393). I re-ran the run_git caller search with Grep. Its hits match the listed sites: diff.py:35,56,68; rollup.py:57,78,82,90; architecture-review SKILL.md:289; citations.py hits are its own _git.

### Unanchored findings

- **advisory**: The set of commands treated as an approval is defined twice and not recorded: once as the hook's needles (acf-allow, acf.cli_allow, approvals.json) and once as Decision 7's permissions.ask rules in /acf-setup prose (Bash/PowerShell acf-allow, python -m acf.cli_allow, Edit(~/.acf/**)). Only the approvals.json copy is recorded and pinned under ## Single point of definition, so the two lists can drift, for example when a console script or module is renamed.
  - evidence: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:122,233,288`

### Looked for but did not find

- ## One base exception: no new exception class; the design reuses GitError, which subclasses AcfError (plugins/arch-compliance/python/acf/exceptions.py:33). Not touched.
- ## Fail-loud ratchet: the row is unenforced (config/architecture/mandates.yml:94), so the new hook's exempted broad handler needs no baseline entry. Not touched.
- ## Build artifacts, ## Façade sinks, ## FSM transitions, ## React boundaries, ## Soft fail-loud smells: no generated trees, protected sinks, state fields or React views. Not touched.
- ## Frozen ledger format: no LedgerRow or LedgerAmendment field changes. Not touched.
- ## Post-merge: the follow-up is to be filed as an issue, consistent with the declared filing rule (gh issue create). No conflict.
- High-frequency miss, check re-implemented instead of consumed: cli_allow's store-in-repo check is moved onto acf.approval._store_inside_repo (spec §5.3 item 3); the hook's stdlib-only test walks the AST and refuses acf imports. No re-implementation of load_mandates, missing_anchors, KNOWN_DETECTORS or acf.repo constants found.
- High-frequency miss, subprocess text call without encoding: the only new subprocess path goes through run_git, which now decodes bytes itself; the hook spawns no subprocess.
- High-frequency miss, stdlib mixin on an exception: none added.

### Unstated mandates

- ## Scoped refactor — the design changes code paths beyond the approval key: run_git's decoding for every caller, rollup.provenance's GitError handling and docstring, the architecture-review skill's snippet behaviour, and stale ARCHITECTURE.md citations. It explicitly declines the GIT_DIR stripping for the diff calls (follow-up 1), which is in the spirit of the section, but the spec never names the section that bounds how far it reaches.

## sweeper

### Claim verdicts

#### C28 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:24, plugins/arch-compliance/python/acf/adr/citations.py:59, config/architecture/ARCHITECTURE.md:300`
- reasoning: I searched plugins/ and scripts/ for subprocess git calls ('["git"', '"git",') and found two runtime runners. One is run_git (diff.py:24). The other is citations._git (citations.py:59), which already exists and is recorded as a breach at ARCHITECTURE.md:300. Every other hit is in tests. git_common_dir calls run_git, so it adds no third runner. I searched for env stripping and repository identity ('GIT_DIR', 'GIT_WORK_TREE', 'local-env-vars', 'git-common-dir', 'env=', 'os.environ'), excluding tests. The only runtime environment reads are judge.py:66-95, for provider keys. The only use of --git-common-dir is prose in adversarial-design-review/SKILL.md:383, where the agent checks whether it is in a linked worktree; no runtime code computes a repository identity.

#### C29 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:102, plugins/arch-compliance/python/acf/approval.py:83, plugins/arch-compliance/python/acf/approval.py:125, plugins/arch-compliance/python/acf/cli_allow.py:50, plugins/arch-compliance/python/acf/cli_allow.py:59, plugins/arch-compliance/python/acf/cli_allow.py:62`
- reasoning: fingerprint (approval.py:102), file_digests (:83), check_approval (:125) and load_gate_registry (used at cli_allow.py:50) are the single existing implementations. A grep for 'fingerprint(' and 'sha256' in acf/ shows no other approval-fingerprint computation. The two header lines sit at cli_allow.py:59 and :62, and the review loop is :58-65. The other messages that list row ids, at posttooluse_gate.py:150-155 and approval.py:149-154, are refusal notices, not reviews, so describe_approval does not compete with them. One gap: check_approval returns empty digests except for APPROVED (approval.py:129-140). acf-approval-status therefore has to call file_digests itself to pass digests to describe_approval, and the spec leaves that call unstated. It still reuses the same function.

#### C30 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/hooks.json:10, plugins/arch-compliance/hooks/hooks.json:22`
- reasoning: hooks.json registers its two command hooks as 'python "${CLAUDE_PLUGIN_ROOT}/hooks/<file>.py"' (lines 10 and 22) under SubagentStart and PostToolUse. A grep of the tree, excluding docs/reviews and .claude, for 'PreToolUse', 'permissionDecision', 'permissions.ask' and 'onFailure' finds them only in the spec under review. No plugin code reads 'permission_mode' or 'CLAUDE_CODE*'. The new hook's stdlib-only common path follows the 'true no-op' shape at posttooluse_gate.py:45-48 and inject_constraints.py:33-36.

#### C31 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_allow.py:27, plugins/arch-compliance/python/acf/cli_allow.py:56, plugins/arch-compliance/python/acf/approval.py:121`
- reasoning: _HELPER_LIMIT is defined at cli_allow.py:27-30 and used once, at :65. No other module defines the 'imported modules are not covered' text; I grepped for that phrase. cli_allow.py:56 'RepoTree(repo).contained(str(store)) is not None' is the same expression as approval.py:122 inside _store_inside_repo, so reusing it changes nothing. write_approval (approval.py:165) repeats the same check before writing; cli_allow's earlier check only refuses before the review is printed.

#### C32 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:135, plugins/arch-compliance/python/acf/approval.py:167, plugins/arch-compliance/python/acf/cli_allow.py:76, plugins/arch-compliance/python/acf/cli_allow.py:77`
- reasoning: I searched by behaviour, for store reads and writes rather than names: 'read_store', '.repos', 'store_path', 'STORE_REL' and 'approvals.json' across the tree. The only runtime reads and writes of the store dict are approval.py:135 (get), :170/:173 (pop/assign, keyed at :167) and cli_allow.py:77 (membership, keyed at :76). posttooluse_gate.py:129/152 imports store_path only for reason text, and cli_check_diff.py:102 goes through require_approval. cli_allow.py:67 also prints RepoTree(repo).root as the approved key, but that is display, not keying, and §5.3 item 4 changes it.

#### C33 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:24, plugins/arch-compliance/python/acf/cli_allow.py:4, plugins/arch-compliance/hooks/hooks.json:2, CLAUDE.md:39`
- reasoning: I re-ran the recipe terms over the whole tree, excluding docs/reviews, .claude, docs/plans and tests, then searched by behaviour ('run it yourself', 'person-run', 'never by an agent', 'leave approval', 'PYTHONUTF8', 'declare its encoding', 'git runner'). Every live site I found is in §5.7, §5.3 or §5.5: README :64/:110/:112/:143, ARCHITECTURE.md :180-182, acf-setup SKILL :24/:185/:187/:206/:260/:262/:263/:288, acf-mandate :139, posttooluse_gate :16/:154, approval.py :4-5/:152, cli_allow :1-4, hooks.json :2, SUPERPOWERS_COMPLEMENT :89 and CHECK_DIFF_HOST_WIRING :333. There are two precision gaps. First, the CLAUDE.md row cites :36-38, but the encoding clause is on :39 and reads 'until the git runner declares its own encoding', not the quoted 'does not declare its text encoding'. Second, CHECK_DIFF_HOST_WIRING.md:141 and :330-331 make the same encoding statement and are not listed, although the neighbouring :333 is. Both are in Approved design records, not live prose.

#### C34 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_approval.py:229, plugins/arch-compliance/tests/test_cli_allow.py:70, plugins/arch-compliance/tests/test_hooks.py:554, plugins/arch-compliance/tests/test_diff_cli.py:400`
- reasoning: I grepped plugins/arch-compliance/tests for 'resolve().as_posix()', 'root.as_posix()', 'acf-allow', 'ApprovalStore(', 'ApprovalEntry(', 'approvals.json', 'yourself' and 'Ask the user'. Root-key indexing appears exactly at test_approval.py:229, 236, 239, 240, 265 and test_cli_allow.py:70, 103. 'acf-allow' in a gate message is asserted exactly at test_approval.py:209, test_hooks.py:554 and test_diff_cli.py:400. test_hooks.py:666 writes an empty store file, which is not keyed. No test asserts 'do not run it yourself' or the 'Approved <root>' closing line.

#### C35 — SURVIVED
- evidence: `docs/design/CHECK_DIFF_HOST_WIRING.md:333, docs/design/ARCHITECTURE_REVIEW_PORT.md:45, docs/design/HOST_DETECTOR_EXTENSION_POINT.md:64, docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:643`
- reasoning: I searched docs/design for 'acf-allow', '.acf/enabled', 'no-op', 'resolved root' and 'per checkout'. Outside the two superseded documents I found these. CHECK_DIFF_HOST_WIRING.md:333 ('needs each person's acf-allow') is handled in §5.7. ARCHITECTURE_REVIEW_PORT.md:45 and :205 say auditor prompts need no acf-allow, which does not conflict. HOST_DETECTOR_EXTENSION_POINT.md:64 is about the PostToolUse hook only, which stays true. ADR_GATE_HOST_CONTRACT.md:362 ('one resolved root') is about artifact paths, not approval. PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:643 is the verification row for item 11, which is superseded. One omission: the Supersedes header lists the cleared spec's hook notice at :156 but not its require_approval message at HOST_DETECTOR_LOCAL_APPROVAL.md:127, which §5.5 rewrites. Decision 6's channel covers it in substance.

### Unanchored findings

- **advisory**: The §5.7 row for the Windows note cites CLAUDE.md:36-38 and quotes the wording 'the git runner does not declare its text encoding'. The clause is actually on CLAUDE.md:39 and reads 'until the git runner declares its own encoding (spec §9, follow-up 1)', so the planned replacement does not match that file's text.
  - evidence: `CLAUDE.md:39`
- **advisory**: CHECK_DIFF_HOST_WIRING.md:141 (Windows non-goal) and :330-331 also say the diff gate's git runner does not declare its text encoding, which this design makes untrue for run_git. §5.7 records only the neighbouring :333 as left as written.
  - evidence: `docs/design/CHECK_DIFF_HOST_WIRING.md:141`
- **advisory**: acf-approval-status passes digests to describe_approval, but check_approval returns an empty digest map for MISSING, STALE and STORE_IN_REPO. The status command therefore needs its own file_digests call, and §5.2 does not state it.
  - evidence: `plugins/arch-compliance/python/acf/approval.py:137`
- **advisory**: The Supersedes header lists the cleared spec's hook-notice text (:156) but not its require_approval message text (:127), which §5.5 also replaces.
  - evidence: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:127`

### Looked for but did not find

- Second runtime git runner or env-stripping git call: '["git"', '"git",', 'env=', 'os.environ', 'GIT_DIR', 'local-env-vars' in plugins/ and scripts/
- Existing repository-identity or worktree-sharing computation: 'git-common-dir', 'common-dir', 'worktree' in runtime code
- Other store keying consumers: 'read_store', '.repos', 'store_path', 'STORE_REL', 'approvals.json'
- Existing PreToolUse or permission mechanism in the plugin: 'PreToolUse', 'permissionDecision', 'permissions.ask', 'onFailure', 'permission_mode'
- Existing Claude Code process detection: 'CLAUDE_CODE', 'CLAUDECODE'
- Other copies of the helper-limit text: 'imported modules are not covered'
- Prose asserting human-only approval in other words: 'run it yourself', 'person-run', 'never by an agent', 'leave approval', 'run by the user'

### Relationships

- ADJACENT: `acf.diff.git_common_dir` — responsibility `run git to get repository facts` — existing `plugins/arch-compliance/python/acf/adr/citations.py:51`
  - resolution: Build on run_git as the spec does. citations._git is the already-recorded second runner (ARCHITECTURE.md:300), and merging it is follow-up 1 of PLUGIN_SELF_HOSTING_AND_DOCTRINE §9.
  - non-merge: This design adds no runner. git_common_dir is a caller of run_git, and consolidating the existing second runner is out of scope and already tracked.
- ADJACENT: `acf.diff.git_common_dir` — responsibility `decide whether a checkout is a linked worktree of a shared repository` — existing `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:383`
  - resolution: None. The skill prose is an agent-run shell check that only warns about ledger merge conflicts.
  - non-merge: The skill step is an instruction to the agent with no runtime call site; it decides whether to print a warning, not an approval key.
- PARTIAL_OVERLAP: `hooks/approval_prompt.py needle 'approvals.json'` — responsibility `define the approval store file name` — existing `plugins/arch-compliance/python/acf/approval.py:37`
  - resolution: STORE_REL stays canonical. The hook's literal copy is pinned to STORE_REL.name by test_approval_prompt.py and recorded under ## Single point of definition, as §5.3/§5.7 already propose.
- ADJACENT: `hooks/approval_prompt.py payload parsing` — responsibility `extract tool_input.file_path from a hook payload` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:235`
  - resolution: Keep them separate.
  - non-merge: posttooluse_gate is a script, not an importable module. The new hook must import only the standard library, and on malformed JSON it must fail closed (exit 2), where _maybe_read_stdin_json returns None.
- SUBSUMED: `acf.approval.describe_approval` — responsibility `render the approval review (rows, file digests, helper limit)` — existing `plugins/arch-compliance/python/acf/cli_allow.py:58`
  - resolution: cli_allow's loop at :58-65 collapses into describe_approval, as the spec states, and _HELPER_LIMIT moves to acf.approval.HELPER_LIMIT.
- ADJACENT: `acf.approval.describe_approval` — responsibility `list the unapproved host row ids in a message` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:150`
  - resolution: None.
  - non-merge: The gate notices are one-line refusals naming row ids. describe_approval is a multi-line review with files, SHA-256 values and the fingerprint.
- ADJACENT: `hooks/approval_prompt.py stdlib-only common path` — responsibility `stay a cheap no-op in repositories where the hook has nothing to do` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:45`
  - resolution: Follows the same shape. The AST stdlib-import test is modelled on test_repo_paths.py:74-78.
  - non-merge: The existing hooks key their no-op on .acf/enabled. The new hook keys it on a needle scan and must ignore .acf/enabled, so no shared helper fits.

### Two-owner counts

- run git as a subprocess from runtime code: 2
- define the approval store file name: 2
- extract tool_input.file_path from a hook payload: 2

### Document conflicts

- `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:127` (contradicts): Message: `host detectors need approval: <reason>; rows: <ids>. Ask the user to review the detector files and run acf-allow; a CI workflow, or a run with --mandates naming another file, passes --trusted-checkout.`
- `docs/design/CHECK_DIFF_HOST_WIRING.md:141` (contradicts): the diff gate's git runner does not declare its text encoding (`ARCHITECTURE.md`, `## Declared text decoding`)
- `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:643` (contradicts): Hooks no-op without the marker

## hardening

### Claim verdicts

#### C36 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:135; plugins/arch-compliance/python/acf/approval.py:167; plugins/arch-compliance/python/acf/cli_allow.py:38; plugins/arch-compliance/skills/acf-setup/SKILL.md:259`
- reasoning: Today the key is RepoTree(repo).root.as_posix() (approval.py:135, :167), so every worktree root gets its own entry. The fingerprint alone decides what is approved, so moving the key to the common dir adds no review and removes none. I checked the prefix argument: without it, two hosts in one repository would share one entry, and one fingerprint would overwrite the other, so each would flip the other to STALE. Scratch repro with git 2.49.0.windows.1, a worktree wt with sub/: the plain run printed '<w>/.git' and 'sub/'. With GIT_DIR set to the worktree's git dir the prefix line came out empty (G3 holds). With GIT_DIR unset it printed 'sub/' again. The pre-push hook the plugin tells hosts to install (acf-setup SKILL.md:259) is where git sets GIT_DIR, so stripping the variables is needed. In a plain temp dir, rev-parse exited 128 with 'not a git repository', which is the only branch that gets the folder key (spec §5.1 step 4). `rev-parse --local-env-vars` exits 0 there and lists GIT_DIR, GIT_WORK_TREE, GIT_COMMON_DIR, GIT_CONFIG_PARAMETERS and GIT_CONFIG_COUNT.

#### C37 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:24-30; plugins/arch-compliance/python/acf/diff.py:35-39`
- reasoning: Reproduced G4 in a scratch dir 'Á_dir' with Python 3.13 under cp1252, using subprocess.run(text=True) as diff.py:24-30 does. The reader thread printed UnicodeDecodeError 'charmap' byte 0x81, run() returned stdout=None with returncode 0, and no exception reached the caller. _git (diff.py:35-39) would then return None. The fix sits at the producer, the one runner every caller uses (callers: diff.py:35, rollup.py:57/78/82/90, architecture-review SKILL.md:289), so it is rung 3 at the source rather than a catch in one consumer. On POSIX, communicate() already raises UnicodeDecodeError in the main thread, so strict UTF-8 plus GitError makes the platforms agree and turns a traceback into a typed error. The one added catch is rollup.provenance, which is report-only and returns 'unresolved' with the message, so it is not silent.

#### C38 — SURVIVED
- evidence: `docs/en/hooks.md:942 (code.claude.com, fetched); docs/en/permissions.md:173; docs/en/plugins/manifest-reference.md:612-626; plugins/arch-compliance/python/acf/cli_allow.py:38`
- reasoning: The plugin manifest reference lists the plugin components (skills, commands, agents, hooks, .mcp.json, .lsp.json, output styles, workflows, themes, monitors, bin). There is no settings or permissions component, so a plugin cannot ship permission rules. permissions.md:173 says a command written another way is not matched by a Bash rule. hooks.md:942 says that on most events a failing or timed-out hook still lets the action run unless onFailure 'block' is set (v2.1.295+). cli_allow.py:38 has --repo, and approval.store_path() is per user (approval.py:66-70). So an agent in an unmarked repository could write another repository's entry, which justifies running the hook whatever .acf/enabled says.

#### C39 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_allow.py:58; plugins/arch-compliance/python/acf/approval.py:173-174; plugins/arch-compliance/python/acf/cli_allow.py:33-71`
- reasoning: write_approval stores fingerprint(rows, digests) from the digests cli_allow computes at :58 (approval.py:173-174). Comparing --fingerprint to fingerprint(rows, digests) before the write therefore binds the stored entry to the bytes whose hex appears in the prompted command. Today cli_allow.main checks nothing about its caller (:33-71). The CLAUDE_CODE_CHILD_SESSION refusal forces the hex into the command the user sees at the prompt. It is a refusal, not a repair. The refusal can be sidestepped with an env override such as `env -u CLAUDE_CODE_CHILD_SESSION acf-allow`, but that command still contains the needle, so the hook still asks; spec §4 already accepts this kind of residual.

#### C40 — SURVIVED
- evidence: `docs/en/permission-modes.md:34-36 (code.claude.com, fetched); pyproject.toml:19`
- reasoning: A Python check confirmed that 'acf-approval-status' contains none of 'acf-allow', 'acf.cli_allow' or 'approvals.json', case-insensitively. permission-modes.md:34-36 says Claude Code never auto-approves tools matched by an explicit ask rule in any mode, bypassPermissions included. So the ask rules are the documented guarantee in bypass mode, and the hook's deny there is not. The console-script table at pyproject.toml:18-21 has room for the new entry beside acf-allow (:19).

#### C41 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:17-30; plugins/arch-compliance/python/acf/diff.py:35-39; plugins/arch-compliance/python/acf/review/rollup.py:57-95; plugins/arch-compliance/tests/test_review_rollup.py:115`
- reasoning: run_git is one subprocess.run call (diff.py:24-30). It can capture bytes, decode them itself, and return subprocess.CompletedProcess(args, returncode, stdout_str, stderr_str), which keeps the CompletedProcess[str] annotation. All callers read only .returncode, .stdout and .stderr as strings: _git at diff.py:35-39, and rollup.py:57-95. They pass no extra kwargs, so a keyword-only env defaulting to None leaves them unchanged. The existing fake at test_review_rollup.py:115 is fake_run_git(repo, *args), and rollup never passes env, so it still fits.

#### C42 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:128-129; plugins/arch-compliance/python/acf/approval.py:135; plugins/arch-compliance/python/acf/approval.py:167; plugins/arch-compliance/python/acf/cli_allow.py:76`
- reasoning: check_approval returns NOT_NEEDED at :128-129, before _store_inside_repo and before any key work. _store_inside_repo (:121-122) uses only RepoTree containment and runs no git. The key appears as the single expression RepoTree(repo).root.as_posix() at approval.py:135 (inside .repos.get(...)), approval.py:167 (key = ...) and cli_allow.py:76 (key = ...). Each can become repo_key(repo).key. require_approval (:143-154) only wraps check_approval, so the NOT_NEEDED ordering carries over to the diff gate.

#### C43 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:106; plugins/arch-compliance/hooks/posttooluse_gate.py:125; plugins/arch-compliance/hooks/posttooluse_gate.py:140-145; plugins/arch-compliance/python/acf/cli_allow.py:47-70; plugins/arch-compliance/python/acf/exceptions.py`
- reasoning: cli_check_diff.py:106 catches (GitError, AcfInputError, UnknownDetectorError, DetectorPackError), and require_approval at :102 is inside that try. posttooluse_gate.py imports its exception types inside the deferred import block (:125), so GitError joins that import. The try at :140-145 covers check_approval and returns `failure`, which is 2 in hook format (:101). Without the change, the outer handler at :89-94 would print a traceback and exit 2, so adding GitError removes only the traceback. cli_allow.py's try begins at :47 and its `if args.revoke: return _revoke(repo)` sits inside it, so a GitError raised in _revoke reaches the :68 handler. GitError subclasses AcfError, not AcfInputError (exceptions.py), so it really does need adding.

#### C44 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_allow.py:58; plugins/arch-compliance/python/acf/cli_allow.py:59-65; plugins/arch-compliance/python/acf/cli_allow.py:67`
- reasoning: :58 is `digests = file_digests(repo, rows)`, and rows plus digests are all fingerprint() needs, so the comparison can follow it before write_approval at :66. The closing print is at :67. One precision note: the review output is :59-65. Line :58 is the digests assignment that both describe_approval and the comparison consume, so it must stay; §5.2's 'in place of its own loop (cli_allow.py:58-65)' should read :59-65.

#### C45 — SURVIVED
- evidence: `docs/en/hooks.md:460 (code.claude.com, fetched); docs/en/hooks.md:942; docs/en/hooks.md:762; docs/en/hooks.md:2092; docs/en/hooks.md:283; docs/en/hooks.md:1888-1908; plugins/arch-compliance/hooks/hooks.json:16-27`
- reasoning: hooks.md:460 lists onFailure ('continue'|'block', v2.1.295+) as a command-hook field. :942 shows a PreToolUse example with onFailure 'block' and timeout. :283 says a matcher made of letters and '|' is an exact-name list, and :394 says a Bash matcher on PreToolUse also covers Monitor commands as Bash calls. :762 makes permission_mode a common input field with the value 'bypassPermissions'. :1884-1908 documents tool_name, tool_input.command and tool_input.file_path. :2092 says the reason for 'ask' is shown in the permission prompt. permissions.md:683 says exit 2 stops the call. The existing hooks.json:16-27 already uses the same plugin hook shape. One gap: tool_input.notebook_path is not documented in hooks.md. The hook reads file_path or notebook_path, and Edit(~/.acf/**) covers NotebookEdit (tools-reference.md:95), so the gap does not break anything.

#### C46 — SURVIVED
- evidence: `docs/en/hooks.md:2139 (code.claude.com, fetched); docs/en/permission-modes.md:34-36; docs/en/permissions.md:361`
- reasoning: hooks.md:2139: in auto mode a PreToolUse 'ask' normally goes to the permission prompt and the classifier does not decide it. The exceptions are protected-path writes, unsandboxed retries and SubagentHandback; ~/.acf is none of them. permission-modes.md:34-36: tools matched by an explicit ask rule are not auto-approved in any mode, including bypassPermissions. permissions.md:361: Edit rules apply to all built-in tools that edit files.

#### C47 — SURVIVED
- evidence: `docs/en/env-vars.md:225 (code.claude.com, fetched)`
- reasoning: env-vars.md:225: CLAUDE_CODE_CHILD_SESSION is set to 1 in subprocesses spawned by the Bash, PowerShell and Monitor tools, hooks and status lines. I observed it directly: echo in this session's Bash tool printed CCS=1, and $env:CLAUDE_CODE_CHILD_SESSION in the PowerShell tool printed CCS=1. Caveat: env-vars.md:315 notes the variable is inherited by processes such as a screen session first started from the Bash tool, so a person's terminal inside one would also be refused. The refusal message gives the --fingerprint route.

#### C48 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_repo_paths.py:74-78; pyproject.toml:5`
- reasoning: The model test exists at test_repo_paths.py:74-78 (a regex over import lines with an allowlist). pyproject.toml:5 is requires-python >=3.11, and sys.stdlib_module_names exists from 3.10. On the local Python 3.13.2, '__future__' in sys.stdlib_module_names is True, so `from __future__ import annotations` passes, and 'acf' is not a stdlib name, so an acf import is refused.

#### C49 — SURVIVED
- evidence: `plugins/arch-compliance/tests/conftest.py:10-17`
- reasoning: _isolated_home is autouse and already takes monkeypatch (conftest.py:10-17), so adding monkeypatch.delenv('CLAUDE_CODE_CHILD_SESSION', raising=False) fits. tempfile.gettempdir() on this machine is C:\Users\iball\AppData\Local\Temp, and `git rev-parse --git-dir` there returned 128, so tmp_path is outside any repository. The self-check the spec asks for is sound.

#### C50 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_allow.py:1; plugins/arch-compliance/tests/test_cli_allow.py:1`
- reasoning: Ran a case-insensitive substring check of the needles ['acf-allow', 'acf.cli_allow', 'approvals.json'] in Python. 'pytest plugins/arch-compliance/tests/test_cli_allow.py' -> False. 'git add plugins/arch-compliance/python/acf/cli_allow.py' -> False ('acf/cli_allow' has a slash, not a dot). 'python -m acf.cli_allow' -> True. 'acf-allow --fingerprint abc123' -> True. 'cd x && ACF-ALLOW' -> True. 'acf-approval-status' -> False. The step-1 raw-byte scan sees the JSON-escaped payload, where these ASCII needles appear literally.

#### C51 — UNPROVEN
- evidence: `docs/en/permissions.md:683 (code.claude.com, fetched); docs/en/permission-modes.md:30`
- reasoning: Neither hooks.md nor permission-modes.md says explicitly that a PreToolUse JSON 'deny' is honoured in bypassPermissions. permission-modes.md:30 covers deny rules, not hook decisions. permissions.md:683 says a hook exiting 2 stops the call before permission rules are evaluated, which strongly suggests a hook block holds in bypass mode but still does not name the mode. The spec already marks this unverified and does not rest on it (Decision 7's ask rule is the stated guarantee).

### Unanchored findings

- **advisory**: The hook's copy of 'approvals.json' (kept consistent by a pin test, rung 3) could instead come from one definition: STORE_REL could live in the stdlib-only acf.repo, which the existing hooks already import before any third-party code. That is rung 1, and the spec's reason ('the hook does not import acf') does not hold for acf.repo.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:43`
- **advisory**: §4's list of ways past the hook omits one: where there are no managed settings or Team/Enterprise login, a user-installed mod handling tool.check can approve a call a PreToolUse hook sent to the prompt, or one an ask rule matched.
  - evidence: `docs/en/permissions.md:661-671`
- **advisory**: In bypassPermissions the hook returns a JSON 'deny', whose effect in that mode is undocumented. Exit 2 with the reason on stderr is documented to stop the call before permission rules are evaluated, so it would put Decision 4's bypass branch on documented behaviour.
  - evidence: `docs/en/permissions.md:683`
- **advisory**: §5.2 says describe_approval replaces cli_allow.py:58-65, but :58 is the digests assignment that describe_approval and the --fingerprint check both consume; the review output to replace is :59-65.
  - evidence: `plugins/arch-compliance/python/acf/cli_allow.py:58`

### Looked for but did not find

- a second run_git caller that passes kwargs or relies on stdout being None (only diff.py:35 and rollup.py:57/78/82/90; the architecture-review SKILL.md:289 snippet reads stdout as text)
- a check_approval/require_approval/write_approval caller outside cli_check_diff.py:102, posttooluse_gate.py:142 and cli_allow.py:66/81
- git rev-parse --local-env-vars failing outside a repository (it exits 0 in a plain temp dir, so the folder-key path is reachable)
- a plugin component that ships permission rules (manifest-reference lists none)
- Monitor tool calls escaping the hook (hooks.md:394: a Bash matcher on PreToolUse also receives Monitor commands as Bash calls)
- ~/.acf being a protected path that would let the auto-mode classifier deny before the prompt (hooks.md:2141 lists protected paths and sandbox retries; ~/.acf is neither)

### Mechanism traces

- **run_git decodes UTF-8 and fails loud**
  - invalid state: CompletedProcess.returncode == 0 and stdout is None (or mis-decoded) because git's UTF-8 output was decoded with the locale codec
  - producer: `plugins/arch-compliance/python/acf/diff.py:24-30`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:151-155`
- **git_common_dir strips git's local env vars (rev-parse --local-env-vars) before the key query**
  - invalid state: GIT_DIR in the inherited environment and cwd a subfolder of a linked worktree, so --show-prefix prints '' instead of the subfolder
  - producer: `plugins/arch-compliance/skills/acf-setup/SKILL.md:259`
  - rung 5 (highest applicable 5); repairs=False
  - hardening rejected because: The diff calls are unchanged and outside this spec; they are follow-up 1 in §9 (git sets GIT_DIR in the pre-push hook, an external boundary).
  - spec citation: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:161-163`
- **repo_key folder key when git reports 'not a git repository'**
  - invalid state: git rev-parse exits 128 with 'not a git repository' for the host root (no common dir exists to key on)
  - producer: `plugins/arch-compliance/python/acf/repo.py:49-53`
  - rung 2 (highest applicable 2); repairs=False
  - hardening rejected because: It is not a host declaration: it applies only when git reports that the directory is not a repository, and it keeps one approval per folder as before.
  - spec citation: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:94`
- **PreToolUse approval_prompt.py hook (ask; deny in bypass; onFailure block)**
  - invalid state: an agent tool call whose shell command contains acf-allow/acf.cli_allow/approvals.json, or whose file-tool path contains approvals.json, runs with no user answer at a prompt
  - producer: `plugins/arch-compliance/python/acf/cli_allow.py:33-71`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: a plugin cannot ship user permission rules, and a rule does not match the same program started another way; acf-allow itself cannot see the user's consent, so the producer is hardened only as far as Decision 5 (fingerprint and env refusal)
  - spec citation: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:215-239`
- **acf-allow --fingerprint binding**
  - invalid state: stored entry fingerprint != the fingerprint printed in the review the user read, because rows or files changed between acf-approval-status and acf-allow
  - producer: `plugins/arch-compliance/python/acf/cli_allow.py:58`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:207`
- **acf-allow refusal under CLAUDE_CODE_CHILD_SESSION=1 without --fingerprint**
  - invalid state: an approval written from a Claude Code subprocess whose command carried no reviewed fingerprint
  - producer: `plugins/arch-compliance/python/acf/cli_allow.py:33-71`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:208`
- **rollup.provenance catches GitError from git blame and returns ('unresolved', message)**
  - invalid state: git blame --porcelain stdout for the finding's line is not valid UTF-8
  - producer: `plugins/arch-compliance/python/acf/review/rollup.py:78-80`
  - rung 5 (highest applicable 5); repairs=False
  - hardening rejected because: The roll-up is report-only (acf/review/rollup.py:3), so provenance returns its existing outcome for a git failure.
  - spec citation: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:158`
- **test pin of the hook's 'approvals.json' needle against acf.approval.STORE_REL.name**
  - invalid state: the hook's literal needle != STORE_REL.name after STORE_REL is renamed
  - producer: `plugins/arch-compliance/python/acf/approval.py:37`
  - rung 3 (highest applicable 1); repairs=False
  - hardening rejected because: A test pins the two, since the hook does not import acf.
  - spec citation: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:235`

## Claims

- **C1** [root_cause] [load-bearing]: check_approval looks the store entry up by RepoTree(repo).root.as_posix() (approval.py:135) and write_approval writes under the same key (approval.py:167). Every git worktree has its own root, so a new worktree of an approved repository reads as MISSING even when its active host rows and detector files are byte-identical to the approved ones.
  - spec citation: `plugins/arch-compliance/python/acf/approval.py:135`
- **C2** [root_cause] [load-bearing]: Approval is meant to be given only by the user at a terminal. This is a prose convention: the diff gate's refusal (approval.py:149-154), the PostToolUse hook's notice (posttooluse_gate.py:150-155), /acf-setup (acf-setup/SKILL.md:24 and :288) and /acf-mandate (acf-mandate/SKILL.md:139) tell the agent to ask the user to run acf-allow and not to run it itself, and cli_allow.main (cli_allow.py:33-71) checks nothing about its caller.
  - spec citation: `plugins/arch-compliance/python/acf/approval.py:149-154`
- **C3** [premise] [load-bearing]: In issue #62 the owner reports that Remote Control's `!` prefix does not execute a command, so a user following a session remotely cannot run acf-allow. The issue is readable with `gh issue view 62 --repo IanDBallard/arch-compliance-for-superpowers`.
  - spec citation: `None`
- **C4** [premise]: The cleared spec HOST_DETECTOR_LOCAL_APPROVAL.md keyed approval per checkout on purpose (:90), and the superseded items listed in the header are its Decision 2 key (:68), its Decision 6 channel (:72), the second clause of the residual at :84, the hook notice at :156 and the residual at :90. Item 11 of PLUGIN_SELF_HOSTING_AND_DOCTRINE.md (:162-164) says the plugin's hooks no-op without .acf/enabled. No other part of those specs is contradicted.
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:90`
- **C5** [premise]: The #62 refusal text 'acf: host detectors need approval: no approval for this repository' is what the current code prints for an absent store entry (MISSING reason via require_approval and cli_check_diff).
  - spec citation: `None`
- **C6** [premise] [load-bearing]: The fingerprint covers the active host rows and the SHA-256 digests of the detector files, and nothing in it depends on the store key. So re-keying leaves fingerprint semantics unchanged, and a worktree whose host rows or detector files differ from the approved bytes is STALE rather than APPROVED.
  - spec citation: `None`
- **C7** [premise] [load-bearing]: Deferral: imported helpers and executed tools are outside the fingerprint (HOST_DETECTOR_LOCAL_APPROVAL.md:83). Per-folder keying never covered them either, since `git checkout` of another branch in an approved folder runs that branch's helpers under the existing approval. Nothing today ties approval to the branch or to helper bytes.
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:83`
- **C8** [premise] [load-bearing]: Deferral: the cleared spec's first clause at :84 accepts that whoever can write the user's home directory or run acf-allow can approve. So a text-matching hook that a determined agent can bypass (by importing write_approval in a script, or building the command string at run time) widens no exposure the cleared design had not accepted. Today neither cli_allow.main nor write_approval checks its caller.
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:84`
- **C9** [premise] [load-bearing]: G4: run_git (diff.py:24-30) uses text=True with no encoding. On Windows under cp1252, git's UTF-8 output for a non-ASCII path fails to decode inside subprocess's reader thread, and CompletedProcess.stdout comes back None without an exception reaching the caller. Decoding the same output as UTF-8 gives the correct path.
  - spec citation: `plugins/arch-compliance/python/acf/diff.py:24-30`
- **C10** [deletion] [load-bearing]: The design removes per-folder keying for git repositories and does not read or migrate old root-keyed entries. Nothing else reads the store by root key (so no live consumer breaks), and the store schema tolerates leaving those entries in place.
  - spec citation: `config/architecture/ARCHITECTURE.md:53-55`
- **C11** [premise]: Example of an executed tool outside the fingerprint: the Cayenne detector config/architecture/detectors/eslint_rules.py:58-60 runs node on the repository's ESLint. The sibling checkout is at C:/Users/iball/Arduino/Projects/Cayenne.
  - spec citation: `C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/detectors/eslint_rules.py:58-60`
- **C12** [premise] [load-bearing]: G1 and G2: `git rev-parse --path-format=absolute --git-common-dir --show-prefix` prints the common directory and the prefix on two lines, and both worktrees of one repository print the same common directory. Outside any repository it exits 128 with 'not a git repository' on stderr. Verifiable read-only in this repository, in a linked worktree (git worktree list), and in a directory outside any repository such as the system temp directory.
  - spec citation: `None`
- **C13** [premise] [load-bearing]: G3: in a linked worktree's pre-push hook git sets GIT_DIR to the worktree's git directory, and with GIT_DIR set and GIT_WORK_TREE unset, `--show-prefix` in a subfolder prints an empty line instead of the subfolder. `git rev-parse --local-env-vars` lists GIT_DIR, GIT_WORK_TREE and git's other repository-locating variables, works outside a repository, and stripping them restores the correct prefix.
  - spec citation: `None`
- **C14** [premise] [load-bearing]: The callers of run_git (directly or through diff._git) are diff.py:35, :56, :68, acf/review/rollup.py:57, :78, :82, :90 and the architecture-review skill snippet (architecture-review/SKILL.md:289). Switching run_git to strict UTF-8 decoding, with GitError on undecodable stdout, keeps each caller's contract. rollup.provenance (rollup.py:70-95) maps a blame GitError to its existing 'unresolved' outcome, keeping the roll-up report-only.
  - spec citation: `plugins/arch-compliance/python/acf/review/rollup.py:70-95`
- **C15** [premise]: CI runs on Linux with a UTF-8 locale and the repository's Windows instruction already sets PYTHONUTF8=1 (CLAUDE.md), so those runs already decode git output as UTF-8, and making run_git declare UTF-8 matches them.
  - spec citation: `None`
- **C16** [mandate] [load-bearing]: `## No shims`: not reading old root-keyed entries complies, and reading them would be a compatibility shim the section forbids.
  - spec citation: `config/architecture/ARCHITECTURE.md:53-55`
- **C17** [mandate] [load-bearing]: `## Declared, never defaulted`: the folder key used only when git reports that the directory is not a repository is not a host declaration. Recording it in the section's list of recorded defaults (changing 'Three defaults' to 'Four defaults') and printing the scope through describe_approval satisfies the mandate.
  - spec citation: `config/architecture/ARCHITECTURE.md:213-228`
- **C18** [mandate] [load-bearing]: `## One owner for host paths`: approval.py joins two strings git printed and resolves nothing itself, so it adds no host-path resolution outside RepoTree and needs no allowlist entry in test_repo_tree_guard.py.
  - spec citation: `config/architecture/ARCHITECTURE.md:115-138`
- **C19** [mandate] [load-bearing]: `## Single point of definition`: git_common_dir and the new env keyword are built on run_git and add no further git runner. The hook's copy of the store file name ('approvals.json') is a second definition of acf.approval.STORE_REL.name, kept because the hook imports no acf, and is recorded in the section and pinned by a test, as the section's 'recorded not hidden' practice requires.
  - spec citation: `config/architecture/ARCHITECTURE.md:295-317`
- **C20** [mandate] [load-bearing]: `## Fail loud`: git_common_dir returns None only for exit 128 with 'not a git repository' (under LC_ALL=C), and raises GitError carrying git's stderr for every other outcome (another exit, malformed output, OSError, undecodable output). Each entry point reports that GitError on its existing channel (cli_check_diff exit 1, PostToolUse hook exit 2, acf-allow and acf-approval-status exit 1). The new hook's broad handler prints to stderr, exits 2 and carries the fail-loud.bare-except-ok token with a reason. Together these comply with the section.
  - spec citation: `config/architecture/ARCHITECTURE.md:26-43`
- **C21** [mandate] [load-bearing]: `## Host detectors and call sites` trust boundary: revising the Trust boundary paragraph (:179-186) and its closing test list (:188) as §5.7 states keeps the doctrine consistent with the code, and nothing else in the section requires a human-run terminal command.
  - spec citation: `config/architecture/ARCHITECTURE.md:179-186`
- **C22** [mandate] [load-bearing]: `## Declared text decoding`: making run_git capture bytes and decode them as strict UTF-8 itself satisfies the section for run_git, so run_git leaves its declared debt ('Three calls' becomes 'Two calls'), and the remaining two (adr/citations.py _git and the TypeScript bridge) stay declared.
  - spec citation: `config/architecture/ARCHITECTURE.md:268-279`
- **C23** [mandate]: `## Release discipline`: the design changes skill prose and adds a skill, so it bumps pyproject.toml:3 and plugin.json:3 from 0.3.4 to 0.3.5.
  - spec citation: `config/architecture/ARCHITECTURE.md:283-284`
- **C24** [mandate]: `## Prose names no host`: the new gate-message texts (§5.5), the hook's reasons (§5.4) and the acf-approve skill name no host repository.
  - spec citation: `config/architecture/ARCHITECTURE.md:232-233`
- **C25** [mandate]: `## POSIX paths`: the stored key uses as_posix() on the git common dir with git's forward-slash prefix, so keys are POSIX on every platform.
  - spec citation: `config/architecture/ARCHITECTURE.md:57-66`
- **C26** [mandate]: `## Live consumers`: each new function and constant (git_common_dir, the env keyword of run_git, repo_key/RepoKey, describe_approval, HELPER_LIMIT, cli_approval_status.main) has a live consumer in the same change.
  - spec citation: `config/architecture/ARCHITECTURE.md:250-254`
- **C27** [mandate]: `## No completeness claims`: the spec's enumerations (run_git callers, GitError entry points, prose sites, test sites) are per-item lists backed by recipes, and the §5.7 lead disclaims completeness.
  - spec citation: `config/architecture/ARCHITECTURE.md:256-266`
- **C28** [shape_fit] [load-bearing]: git_common_dir and the env keyword extend the existing acf.diff git-runner shape (beside run_git) and create no second way to run git from runtime code; nothing in the tree already strips git environment variables or computes a repository identity shared by worktrees.
  - spec citation: `plugins/arch-compliance/python/acf/diff.py:17`
- **C29** [shape_fit] [load-bearing]: acf-approval-status reuses load_gate_registry, check_approval, file_digests and fingerprint, so there is still one way to compute an approval state and a fingerprint. describe_approval gives acf-allow and acf-approval-status one review renderer, and keeps cli_allow's current review lines, including the two header lines at cli_allow.py:59 and :62.
  - spec citation: `plugins/arch-compliance/python/acf/cli_allow.py:50`
- **C30** [shape_fit] [load-bearing]: The new PreToolUse approval hook fits the plugin's existing hook shape: hooks.json registers command hooks as `python "${CLAUDE_PLUGIN_ROOT}/hooks/<file>.py"`, and no existing PreToolUse hook or permission mechanism in the plugin does this job.
  - spec citation: `plugins/arch-compliance/hooks/hooks.json:2`
- **C31** [shape_fit]: Moving the imported-helper limit text from cli_allow.py:27-30 to acf.approval.HELPER_LIMIT gives the two scripts one text, and cli_allow.py:56 reusing approval._store_inside_repo (approval.py:121-122) removes a repeated expression with identical behaviour.
  - spec citation: `plugins/arch-compliance/python/acf/cli_allow.py:27-30`
- **C32** [sweep] [load-bearing]: The places that read or write the approval store by key are check_approval (approval.py:135), write_approval (approval.py:167) and cli_allow._revoke (cli_allow.py:76). Switching those three to repo_key(repo).key leaves no consumer keying by the worktree root.
  - spec citation: `plugins/arch-compliance/python/acf/approval.py:135`
- **C33** [sweep]: The §5.7 table (with §5.3 and §5.5) lists the tracked prose and code sites that would contradict the design: approval per folder or resolved root, acf-allow run only by the user, plugin hooks no-op without .acf/enabled, and the git runner not declaring its encoding.
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:24`
- **C34** [sweep]: The existing test assertions that index the approval store by the root key are test_approval.py:229, :236, :239, :240, :265 and test_cli_allow.py:70, :103. The tests asserting acf-allow in a gate message are test_approval.py:209, test_hooks.py:554 and test_diff_cli.py:400.
  - spec citation: `None`
- **C35** [shape_fit]: No tracked Approved design document other than those in the Supersedes header states a contract (per-checkout approval key, human-only acf-allow, every plugin hook a no-op without .acf/enabled) that this design contradicts without superseding it.
  - spec citation: `None`
- **C36** [mechanism_justification] [load-bearing]: Keying by `<git common dir>::<prefix>` is justified because the folder adds no review. The prefix keeps two hosts in one repository from flipping each other STALE. Stripping git's local env vars is needed because an inherited GIT_DIR changes the prefix (G3). The folder key exists only for directories git says are not repositories.
  - spec citation: `None`
- **C37** [mechanism_justification] [load-bearing]: Hardening run_git itself (strict UTF-8, GitError on undecodable stdout) rather than adding recovery around the key is the right rung: it removes the silent None of G4 at the failure point for every caller, instead of catching UnicodeDecodeError in one consumer.
  - spec citation: `None`
- **C38** [mechanism_justification] [load-bearing]: A plugin-shipped PreToolUse hook is justified because a plugin cannot ship user permission rules, and a rule does not match the same program started another way (python -m acf.cli_allow). onFailure 'block' is justified so a crashed or missing hook cannot let an approval through. The hook runs without .acf/enabled because the store is per user and an agent in an unmarked repository could approve another repository with --repo.
  - spec citation: `None`
- **C39** [mechanism_justification] [load-bearing]: The --fingerprint binding is needed so the bytes approved at the prompt are the bytes the agent summarized. Refusing acf-allow without --fingerprint when CLAUDE_CODE_CHILD_SESSION=1 is needed so an agent cannot obtain approval of unreviewed bytes through the prompt.
  - spec citation: `None`
- **C40** [mechanism_justification] [load-bearing]: A separate read-only acf-approval-status command, whose name contains none of the hook's needles (acf-allow, acf.cli_allow, approvals.json), is needed so the agent can gather the review without prompting. /acf-setup's offered permissions.ask rules are needed as the documented guarantee in bypassPermissions mode.
  - spec citation: `None`
- **C41** [implementability] [load-bearing]: run_git (diff.py:17-30) can be changed to capture bytes, decode stdout as strict UTF-8 (GitError on failure) and stderr with errors='replace', take a keyword-only env mapping passed to subprocess.run, and still return subprocess.CompletedProcess[str], with diff._git and the other callers unchanged.
  - spec citation: `plugins/arch-compliance/python/acf/diff.py:17-30`
- **C42** [implementability] [load-bearing]: check_approval returns NOT_NEEDED (approval.py:128-129) before any key computation, so a repository without host rows at the call sites runs no git for approval. check_approval (:135), write_approval (:167) and cli_allow._revoke (cli_allow.py:76) each compute the key in one expression replaceable by repo_key(repo).key.
  - spec citation: `plugins/arch-compliance/python/acf/approval.py:128-129`
- **C43** [implementability] [load-bearing]: A GitError from the key reaches a handler at each entry point. cli_check_diff.py:106 already catches GitError. posttooluse_gate.py:141-145 and cli_allow.py:68 (whose try also covers _revoke) can add GitError to their tuples. The PostToolUse hook then prints the message and exits 2 without a traceback.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:141-145`
- **C44** [implementability] [load-bearing]: In cli_allow.py, `digests = file_digests(repo, rows)` is at :58, so the --fingerprint comparison can follow it before the store write. The review lines at :58-65 can be replaced by describe_approval, and the closing print is at :67.
  - spec citation: `plugins/arch-compliance/python/acf/cli_allow.py:58`
- **C45** [implementability] [load-bearing]: Claude Code's plugin hooks.json accepts a PreToolUse entry with matcher `Bash|PowerShell|Write|Edit|MultiEdit|NotebookEdit`, a command hook, `timeout` and `"onFailure": "block"` (v2.1.295+). The hook's stdin JSON carries permission_mode, tool_name and tool_input (command / file_path / notebook_path). hookSpecificOutput with permissionDecision 'ask' and a reason is honoured and the reason shown, and exit 2 blocks the call. External: https://code.claude.com/docs/en/hooks.md (fetchable read-only with `curl -s`).
  - spec citation: `plugins/arch-compliance/hooks/hooks.json:2`
- **C46** [implementability] [load-bearing]: In auto mode a hook's 'ask' goes to the person's prompt and is not decided by the classifier, and an explicit permissions.ask rule prompts in every mode including bypassPermissions. Edit(...) rules apply to all built-in file-editing tools. External: https://code.claude.com/docs/en/hooks.md, https://code.claude.com/docs/en/permission-modes.md, https://code.claude.com/docs/en/permissions.md (fetchable read-only with `curl -s`).
  - spec citation: `None`
- **C47** [implementability] [load-bearing]: Claude Code sets CLAUDE_CODE_CHILD_SESSION=1 in the environment of the Bash and PowerShell subprocesses it starts. External: https://code.claude.com/docs/en/env-vars.md; also observable read-only from a Bash tool's own environment.
  - spec citation: `None`
- **C48** [implementability]: A test can pin the hook as standard-library-only by walking approval_prompt.py's AST and asserting every imported top-level module is in sys.stdlib_module_names (Python 3.10+; pyproject requires 3.11), modelled on test_repo_module_imports_only_stdlib (test_repo_paths.py:74-78). The same assertion refuses an acf import.
  - spec citation: `plugins/arch-compliance/tests/test_repo_paths.py:74-78`
- **C49** [implementability]: conftest.py's autouse _isolated_home (:10-17) can also delete CLAUDE_CODE_CHILD_SESSION through monkeypatch, so a suite started from Claude Code does not trip Decision 5. tmp_path lies outside any git repository on the test machine, so the §6.1 'plain directory' test can self-check that with git exit 128.
  - spec citation: `plugins/arch-compliance/tests/conftest.py:10-17`
- **C50** [implementability]: The hook's narrowed shell needles (acf-allow, acf.cli_allow, approvals.json) do not match `pytest plugins/arch-compliance/tests/test_cli_allow.py` or `git add plugins/arch-compliance/python/acf/cli_allow.py`, while matching `python -m acf.cli_allow` and `acf-allow --fingerprint <hex>`.
  - spec citation: `None`
- **C51** [implementability]: A PreToolUse hook's 'deny' is honoured in bypassPermissions mode (marked unverified in the spec; Decision 7's ask rule is the stated guarantee there).
  - spec citation: `None`
