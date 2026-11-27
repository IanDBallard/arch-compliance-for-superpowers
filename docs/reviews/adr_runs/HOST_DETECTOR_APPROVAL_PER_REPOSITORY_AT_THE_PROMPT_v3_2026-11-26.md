# Adversarial design review — full detail

Spec: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md` @ `4c45591932f2b266bd91f358572d379f54837457`
Kinds: defect, feature
Outcome: **BLOCKED**
Claims: 56 · Reviewers: 4 · Converged: 0

## Blocking reasons

- load-bearing claim C46 (implementability) is SURVIVED but its evidence ('plugins/arch-compliance/python/acf/cli_allow.py:58-67') merely restates the spec's own citation ('plugins/arch-compliance/python/acf/cli_allow.py:58') — not independent verification, treated as UNPROVEN

## Absorptions

- SUBSUMED: 'acf.diff.git_common_dir' shares responsibility 'invoke git from runtime code' with plugins/arch-compliance/python/acf/diff.py:17 — git_common_dir is a consumer of run_git (with the new env keyword), not a sibling runner; the spec already does this.
- PARTIAL_OVERLAP: 'acf.approval.repo_key' shares responsibility 'derive the approval store key for a repository' with plugins/arch-compliance/python/acf/approval.py:135 — repo_key becomes the one key deriver. The inline RepoTree(repo).root.as_posix() at approval.py:135, approval.py:167 and cli_allow.py:76 (and the display at cli_allow.py:67) collapse into calls to it, as §5.1 and §5.3 state.
- PARTIAL_OVERLAP: 'acf.approval.describe_approval' shares responsibility 'render the approval review lines' with plugins/arch-compliance/python/acf/cli_allow.py:59-65 — describe_approval becomes the one renderer. cli_allow's print loop and _HELPER_LIMIT collapse into it, and acf-approval-status consumes it, as §5.2 states.
- PARTIAL_OVERLAP: 'acf.cli_approval_status.main' shares responsibility 'prepare the review inputs (registry, rows, digests) for a repository' with plugins/arch-compliance/python/acf/cli_allow.py:50-58 — Extract a preparer in acf.approval returning registry, rows and digests, with the 'no host rows' outcome. cli_allow.main and cli_approval_status.main both consume it, and describe_approval stays the renderer.
- PARTIAL_OVERLAP: 'approval_prompt.py APPROVAL_NEEDLES' shares responsibility 'define the set of commands treated as an approval' with plugins/arch-compliance/skills/acf-setup/SKILL.md:24 — APPROVAL_NEEDLES stays the canonical set. Decision 7's ask rules in /acf-setup prose are a recorded second encoding under ## Single point of definition, held together by §6.3's two-way pin test.
- IDENTICAL: 'approval_prompt.py sys.path bootstrap' shares responsibility 'make plugin python importable from a hook script' with plugins/arch-compliance/hooks/posttooluse_gate.py:37-41 — A stdlib-only hooks/_bootstrap.py, importable because the script directory is sys.path[0], would own the insert. posttooluse_gate.py:37-41, inject_constraints.py:27-29 and approval_prompt.py would import it.
- SUBSUMED: 'acf.repo.STORE_REL (moved)' shares responsibility "declare the approval store's home-relative path" with plugins/arch-compliance/python/acf/approval.py:36-37 — Move it to acf.repo. approval.store_path, the hook's needle and test_approval.py:12 import it from there, as §5.4 states.

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:135, plugins/arch-compliance/python/acf/approval.py:167, plugins/arch-compliance/python/acf/repo.py:112-113, plugins/arch-compliance/python/acf/cli_allow.py:76`
- reasoning: check_approval reads read_store(store).repos.get(RepoTree(repo).root.as_posix()) and write_approval writes data.repos[key] with key = RepoTree(repo).root.as_posix(). RepoTree.__init__ stores root.resolve(), a plain filesystem resolve with no git awareness, so every worktree folder resolves to its own distinct key. The fingerprint (approval.py:102-108) depends only on the rows and the digests, so byte-identical files in a new worktree still miss the entry and return MISSING (approval.py:136-137). cli_allow._revoke uses the same key.

#### C2 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:150-154, plugins/arch-compliance/hooks/posttooluse_gate.py:152-154, plugins/arch-compliance/skills/acf-setup/SKILL.md:24, plugins/arch-compliance/skills/acf-setup/SKILL.md:288, plugins/arch-compliance/skills/acf-mandate/SKILL.md:139, plugins/arch-compliance/python/acf/cli_allow.py:33-71`
- reasoning: Opened each site. The refusal text says 'Ask the user to review the detector files and run acf-allow'. The hook notice ends 'run acf-allow in this repository; do not run it yourself.' acf-setup :24 and :288 and acf-mandate :139 tell the agent never to run acf-allow itself. cli_allow.main parses --repo and --revoke, loads the registry and writes. It does not inspect its environment or caller. write_approval (approval.py:157-192) has no caller check either.

#### C3 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:68; gh issue view 62 --repo IanDBallard/arch-compliance-for-superpowers (read live)`
- reasoning: Ran gh issue view 62. The issue is open and authored by the owner. Its Problem section says the owner had to run acf-allow by hand at the machine for each worktree '(Remote Control's `!` does not execute)'. It also quotes the refusal 'acf: host detectors need approval: no approval for this repository'. The claim matches the issue text.

#### C4 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:68, docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:72, docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:73, docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:84, docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:127, docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:156, docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:251, docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:162-164`
- reasoning: Each cited line carries the text the Supersedes header quotes. :68 has the RepoTree(repo).root.as_posix() key. :72 has Decision 6, 'run by a person'. :73 has Decision 7's 'the command to run'. :84 has the two-clause residual. :90 has 'One approval per checkout directory'. :127 has the require_approval message and :156 the hook notice. :251 has the expectation that the notice contains acf-allow. PLUGIN_SELF_HOSTING item 11 at :162-164 says the hooks run on subagent start and Write/Edit/MultiEdit and no-op without .acf/enabled. The other cleared-spec lines that name acf-allow (:74 and :260, which say the refusal names acf-allow) stay true, because the new refusal still contains 'acf-allow --fingerprint'.

#### C5 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:112-113, plugins/arch-compliance/python/acf/approval.py:151, plugins/arch-compliance/python/acf/cli_check_diff.py:102, plugins/arch-compliance/python/acf/cli_check_diff.py:106-107`
- reasoning: reason(MISSING) returns 'no approval for this repository'. require_approval raises AcfInputError with the prefix 'host detectors need approval: ' plus that reason. cli_check_diff calls require_approval at :102, catches AcfInputError at :106 and prints 'acf: {exc}'. The output starts 'acf: host detectors need approval: no approval for this repository'.

#### C6 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:102-108, plugins/arch-compliance/python/acf/approval.py:83-99, plugins/arch-compliance/python/acf/registry.py:51-62, plugins/arch-compliance/python/acf/approval.py:138-139`
- reasoning: fingerprint() hashes the JSON of each row's model_dump plus the digests map. Digests are keyed by the repository-relative detector path and hold the file's SHA-256. Mandate's fields (id, title, severity, detection, detector, languages, call_sites, exemption_tokens, status, arch_anchor, auditor, params) hold no absolute path and nothing about the store key. A worktree with different rows or file bytes yields a different fingerprint, and check_approval returns STALE when an entry exists with a non-matching fingerprint.

#### C7 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:82, plugins/arch-compliance/python/acf/detectors/host.py:63, docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:83, plugins/arch-compliance/python/acf/approval.py:102-108`
- reasoning: load_host_detector appends the repository root to sys.path (host.py:82). The source-only loader checks expected_sha256 only for the detector module's own bytes (host.py:63). Imported helpers are never hashed. The fingerprint has no branch, HEAD or helper input, and approval.py has no reference to a branch or HEAD. So checking out another branch with the same detector bytes keeps APPROVED while its helpers differ. The cleared spec's :83 cites host.py:59 for the sys.path append, which is now at host.py:82 (stale line, same fact).

#### C8 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:84, plugins/arch-compliance/python/acf/approval.py:157-176, plugins/arch-compliance/python/acf/cli_allow.py:33-71`
- reasoning: The cleared residual's first clause reads 'Whoever can write the user's home directory, or run `acf-allow`, can approve. Claude Code's tool permissions govern an agent doing either'. write_approval takes repo and registry, checks only store containment, and writes. cli_allow.main does no caller check. A script that imports write_approval was already an accepted path, so a bypassable text-matching hook adds a prompt and removes nothing.

#### C9 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:24-30, docs/design/evidence/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT/run_git_decode_probe.py:53, docs/design/evidence/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT/run_git_decode_probe.out:20-23`
- reasoning: run_git calls subprocess.run with text=True and no encoding. I re-ran the committed probe (PYTHONDONTWRITEBYTECODE=1; it creates repositories only in a TemporaryDirectory). With git 2.49.0.windows.1 and locale cp1252, the A-acute and Y-acute directories gave returncode 0 and stdout None, with the reader-thread UnicodeDecodeError on bytes 0x81 and 0x9d. The e-acute, u-umlaut and CJK directories gave mojibake with no error. The ASCII control matched. run_git raised nothing in any case. My output matched the recorded .out row for row.

#### C10 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:46-49, plugins/arch-compliance/python/acf/approval.py:135, plugins/arch-compliance/python/acf/approval.py:167-176, plugins/arch-compliance/python/acf/cli_allow.py:76-77, config/architecture/ARCHITECTURE.md:53-55`
- reasoning: I grepped plugins/ and scripts/ for read_store, .repos, approvals.json and STORE_REL. The only runtime readers or writers of store keys are approval.py:135, approval.py:167-176 and cli_allow.py:76-77, and all of them switch to repo_key. The rest are tests the spec rewrites (§6.1 table). The tests' _approve helpers (test_hooks.py:406-407, test_diff_cli.py:346-347) go through write_approval, so they stay consistent. ApprovalStore.repos is dict[str, ApprovalEntry] with arbitrary keys, so stale root-keyed entries still parse. extra='forbid' constrains only entry fields. ARCHITECTURE.md:53-55 forbids compatibility shims.

#### C11 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/detectors/eslint_rules.py:58-60, C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/detectors/eslint_rules.py:41`
- reasoning: In the Cayenne checkout on main at f325b349, eslint_rules.py:58-60 runs subprocess.run(["node", str(ESLINT), "--stdin", ...], cwd=WEB). ESLINT is cayenne-web/node_modules/eslint/bin/eslint.js (:41), which is not a fingerprinted detector file.

#### C12 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:78-79; scratch repos under system temp (git 2.49.0.windows.1)`
- reasoning: In a scratch repository w and its linked worktree wt (git worktree add), `git rev-parse --path-format=absolute --git-common-dir --show-prefix` printed two lines. The common directory C:/.../w/.git was identical in both, and the prefix was empty at the top and 'sub/' in sub/. In a temp directory outside any repository it printed 'fatal: not a git repository (or any of the parent directories): .git' and exited 128.

#### C13 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:80; scratch pre-push hook test under system temp`
- reasoning: I installed a pre-push hook in the scratch repository and pushed from both checkouts to a bare remote. From the main checkout, GIT_DIR was unset and sub/ printed 'sub/'. From the linked worktree, the hook saw GIT_DIR=C:/.../w/.git/worktrees/wt with GIT_WORK_TREE unset, and in sub/ the prefix line was empty. After `unset $(git rev-parse --local-env-vars)` it printed 'sub/'. `git rev-parse --local-env-vars` listed 15 names, including GIT_DIR, GIT_WORK_TREE, GIT_COMMON_DIR, GIT_CONFIG_PARAMETERS and GIT_CONFIG_COUNT. It exited 0 outside a repository and also with GIT_DIR pointing at a nonexistent path.

#### C14 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:35, plugins/arch-compliance/python/acf/review/rollup.py:57, plugins/arch-compliance/python/acf/review/rollup.py:78-95, plugins/arch-compliance/skills/architecture-review/SKILL.md:289, plugins/arch-compliance/python/acf/cli_check_diff.py:28`
- reasoning: grep over python/hooks/skills/scripts finds run_git calls at diff.py:35 and rollup.py:57, :78, :82, :90, and the skill snippet at SKILL.md:289. diff._git callers are diff.py:56 and :68. cli_check_diff imports only changed_files and added_lines. adr/citations.py has its own _git. rollup.provenance already returns ('unresolved', stderr) for git failures at :85 and :95, so mapping a blame GitError there stays report-only. The other run_git outputs are ASCII: rev-list --count, ls-files --error-unmatch (path quoted by default), merge-base and rev-parse HEAD. They cannot newly raise.

#### C15 — SURVIVED
- evidence: `.github/workflows/ci.yml:11, .github/workflows/ci.yml:46, CLAUDE.md:37-39`
- reasoning: Both CI jobs run on ubuntu-latest. On Linux, Python's text=True decodes with the locale's preferred encoding, which is UTF-8 under C.UTF-8, and PEP 538/540 coerce a plain C or POSIX locale to UTF-8. CLAUDE.md:37-39 instructs PYTHONUTF8=1 for the Windows diff-gate run. The runner's actual locale variable is not visible in the repository; that part rests on the Python coercion rule.

#### C16 — SURVIVED
- evidence: `docs/design/evidence/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT/hook_deny_source_probe.out:14, docs/design/evidence/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT/hook_deny_source_probe.out:11, docs/design/evidence/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT/hook_deny_source_probe.py:37-58; permissions.md lines 661 and 669-671 (fetched)`
- reasoning: I found the installed 2.1.330 binary (Claude-Data/.../claude-code/2.1.330/9424831ad51c/claude.exe, 387754656 bytes) and re-ran the probe. Its output was byte-identical to the committed .out, including the SHA-256. In the deny branch (:11), the hook deny goes to kte, the :14 function, which evaluates it through the nrt/MVa checks before returning it. The fetched permissions.md says a mod handling tool.check answers after PreToolUse hooks. Without managed settings or a Team/Enterprise login it 'can approve a call that a PreToolUse hook blocked', and it can skip the prompt from an ask rule or a PreToolUse hook. Minification keeps me from naming nrt as the mod check by identifier, but the doc corroborates the behaviour.

### Unanchored findings

- **advisory**: After the re-key, `acf-allow --revoke` in a git repository computes the repo_key and so cannot remove the user's pre-upgrade root-keyed entry. The only removal path is hand-editing ~/.acf/approvals.json, but §5.6 forbids the agent from editing ~/.acf/ and the hook prompts for it. The README note says old entries are deletable but no command deletes them.
  - evidence: `plugins/arch-compliance/python/acf/cli_allow.py:74-83`
- **advisory**: The cleared spec's residual at :83, which this spec cites for the imported-helper deferral, gives host.py:59 for the sys.path append. The append now sits at host.py:82, so the deferral's evidence chain carries a stale line number.
  - evidence: `plugins/arch-compliance/python/acf/detectors/host.py:82`
- **advisory**: run_git's docstring contract is 'never raises on a non-zero status; the caller decides' (pinned by test_run_git_reports_nonzero_as_data). §5.1 makes it raise GitError on undecodable stdout whatever the status, and stdout of `git diff -U0` (diff.py:68) carries file content. Any changed non-UTF-8 text file in a host's diff therefore turns the diff gate into a GitError. The §7 risk row covers this generally, but the docstring and that test's framing need updating, and §5.1 does not list them.
  - evidence: `plugins/arch-compliance/python/acf/diff.py:18-23`

### Looked for but did not find

- any runtime reader of ApprovalStore.repos keys other than approval.py:135, approval.py:167-176 and cli_allow.py:76-77 (grep of plugins/ and scripts/ for read_store, .repos, approvals.json, STORE_REL)
- any path-dependent or worktree-dependent field in Mandate.model_dump that would make the fingerprint differ between byte-identical worktrees (registry.py:51-62)
- any branch, HEAD or helper-module hash input to fingerprint() or check_approval in approval.py
- any caller check (environment, parent process, TTY) in cli_allow.main or write_approval
- any run_git or diff._git caller beyond those §5.1 lists (grep of python/hooks/skills/scripts; tests excluded)
- a difference between my re-run of run_git_decode_probe.py or hook_deny_source_probe.py and the committed .out files (both matched)

## compliance

### Claim verdicts

#### C17 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:53-55; plugins/arch-compliance/python/acf/approval.py:135; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:187`
- reasoning: The section lifts 'Temporary bridge code, compatibility shims, or just-in-case logic to mask architectural misalignments are forbidden'. Today's lookup is keyed only by RepoTree(repo).root.as_posix() (approval.py:135). The design swaps that for repo_key(repo).key at the same sites (spec :187) and adds no second lookup. A fallback read of the old root keys would be exactly a just-in-case compatibility path kept for upgraders, so declining it complies. Non-git folders keep their key unchanged, so for them nothing is migrated or shimmed.

#### C18 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:213-216; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:180-185; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:301`
- reasoning: The section keeps package defaults that are not host declarations in an explicit list ('Three defaults elsewhere in the package are outside this rule and recorded here', :213). No host declares the approval key, and the folder key is chosen only on git's exit 128 with 'not a git repository' (spec :180-185); every other outcome raises. That makes it a derived outcome, not a default standing in for a declaration. Adding it to the recorded list (spec :301) and printing the scope keeps it visible, as the section's practice requires. No host-declared value is replaced by a default.

#### C19 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_repo_tree_guard.py:12-17; plugins/arch-compliance/tests/test_repo_tree_guard.py:59-66; plugins/arch-compliance/python/acf/repo.py:1-6; config/architecture/ARCHITECTURE.md:117-119`
- reasoning: The guard flags only calls to resolve, relative_to, is_relative_to or joinpath, os.path realpath, abspath, relpath or commonpath, and '/' joins on repo or root names with a non-constant right side (test_repo_tree_guard.py:12-14, :59-66). The designed code does none of these. repo_key builds f"{common.as_posix()}::{prefix}" from git's output, and its folder branch goes through RepoTree. git_common_dir does Path(line1) and rstrip. cli_approval_status joins repo / MANDATES_REL, which the guard spares as constantish. So no new allowlist entry is needed. STORE_REL is home-relative, not a host path. Because acf.repo will now hold it, the section's first sentence and repo.py:1-6 ('Host repository layout', 'Both hooks import this') would go stale. Spec §5.7 updates both, and acf.repo needs no new import (pathlib is already allowed, test_repo_paths.py:77).

#### C20 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:297-302; plugins/arch-compliance/python/acf/diff.py:17-39; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:252-253; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:407`
- reasoning: The section requires one canonical implementation and records current breaches 'recorded not hidden' (:299-302). run_git is the package's runner, and _git wraps it (diff.py:17-39). git_common_dir and the env keyword build on it, so no third runner appears. The needle reads STORE_REL.name from its single definition (spec :252). The second encoding of the approval command set, in the user's settings, cannot be imported by the plugin. The design records it in the section and pins it both ways by test (spec :253, :407), which matches the section's practice.

#### C21 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:28-32; plugins/arch-compliance/python/acf/cli_check_diff.py:106; plugins/arch-compliance/hooks/posttooluse_gate.py:140-145; plugins/arch-compliance/python/acf/cli_allow.py:68; plugins/arch-compliance/hooks/posttooluse_gate.py:89`
- reasoning: The section says errors must surface and bars broad handlers that swallow, unless exempted with a reason. git_common_dir returns None on exactly one recognised outcome and raises GitError carrying stderr on every other. Each entry point reports it on its existing channel. cli_check_diff.py:106 already catches GitError and exits 1. The hook's handler (:143) and cli_allow's (:68) gain GitError and print without a traceback; the hook returns its failure code, 2 in hook format. The new hook's broad handler reports to stderr, exits 2 and carries the fail-loud.bare-except-ok token with a reason, following the posttooluse_gate.py:89 precedent. rollup.provenance turns a GitError into its existing 'unresolved' outcome with the message attached, so it is reported, not swallowed. The roll-up is report-only (rollup.py:3).

#### C22 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:179-188; config/architecture/ARCHITECTURE.md:9-13; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:300`
- reasoning: In the section, the only text tying approval to a human-run command is ':181 (acf-allow, run by the user)'. The rest of :140-188 covers reference syntax, the HostHit contract, call sites, built-in contracts and the .acf/enabled rule for the PostToolUse hook, which stays true. The doctrine's introduction (:9-13) mentions only 'an approval' and --trusted-checkout. The §5.7 row (spec :300) rewrites the key and channel sentences and extends the :188 test list, which keeps the section consistent with the designed code.

#### C23 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:270-277; plugins/arch-compliance/python/acf/diff.py:24-30; plugins/arch-compliance/python/acf/adr/citations.py:59-61; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:120-126`
- reasoning: The rule requires every runtime subprocess call that reads text to declare utf-8. With run_git capturing bytes and decoding stdout as strict UTF-8 itself, its output is decoded as declared UTF-8, and the recipe's text=True hit at diff.py:28 disappears. A grep for text=True over the package and hooks finds exactly three hits today: diff.py:28, citations.py:61 and typescript_bridge.py:124. After the change, 'Two calls' is therefore accurate. The corrected citations :59-61 and :120-126 match the current subprocess.run spans. The design's other new code reads stdin as bytes and decodes UTF-8 explicitly, and spawns no other subprocess.

#### C24 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:283-284; pyproject.toml:3; plugins/arch-compliance/.claude-plugin/plugin.json:3`
- reasoning: The rule says 'A change to a skill's prose bumps the plugin version in plugin.json and pyproject.toml'. Both files read 0.3.4 today, and the design changes the acf-setup and acf-mandate prose and adds acf-approve, so the bump to 0.3.5 in both files satisfies the rule. Tagging the merge commit is post-merge procedure and not a design obligation.

#### C25 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:232-233; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:254-255; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:267-268; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:274-290`
- reasoning: The rule says skill prose and runtime messages name no host repository, path or section. The deny and ask reasons (spec :254-255), the require_approval refusal and hook notice (:267-268) and the fixed steps of acf-approve (:274-290) name only plugin commands, skills and flags. The repository key is printed as runtime data. The cy: example appears only in the spec, not in any shipped text. The new skill sits outside test_adr_skill_prose.py's list, so this rests on review, and §5.7 records that gap at :309.

#### C26 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:59-60; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:185; plugins/arch-compliance/python/acf/approval.py:167`
- reasoning: The rule says paths persisted to JSON use Path.as_posix(). The new key is f"{common.as_posix()}::{prefix}" (spec :185), and git prints the prefix with '/'. The folder branch keeps RepoTree(repo).root.as_posix(), the current form at approval.py:167. The key is persisted in POSIX form on every platform. A POSIX directory name holding a literal backslash would pass through unchanged, the same as today, and the store's dict keys are not PosixStr-validated now either.

#### C27 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:252-253; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:183-189; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:211; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:276`
- reasoning: The rule says 'An export has a live call site in the package, a hook or a skill'. Each new export has a non-test consumer in this change. git_common_dir and the env keyword are used by repo_key. repo_key and RepoKey are used by check_approval, write_approval and _revoke. describe_approval and HELPER_LIMIT are used by cli_allow and cli_approval_status. cli_approval_status.main is the console script that the acf-approve skill runs at step 1. STORE_REL in acf.repo is used by store_path and the hook.

#### C28 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:258-261; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:173; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:191; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:294-296; plugins/arch-compliance/python/acf/review/rollup.py:57-90`
- reasoning: The rule allows a quantifier only when a re-runnable recipe backs it. Each enumeration in the spec is per-item with a recipe. The run_git caller list (:173) matches the tree: diff.py:35, :56 and :68, rollup.py:57, :78, :82 and :90, and the architecture-review SKILL.md:289 snippet. The GitError entry-point table (:191) matches the check_approval, require_approval and write_approval sites (cli_check_diff.py:102, posttooluse_gate.py:142, cli_allow.py:66 and :81). The test-site tables carry recipes. The §5.7 lead disclaims completeness (:294).

#### C29 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:321-323; plugins/arch-compliance/python/acf/diff.py:24-30; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:559-562`
- reasoning: The lifted text says 'remove legacy dependencies or non-contractual patterns in code paths you are changing. Do not expand scope to unrelated modules'. The new key query runs through run_git (diff.py:24-30), so its locale decoding sits in a changed code path. adr/citations.py _git and the TypeScript bridge are not on that path, and they remain declared debt under follow-up 1 (PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:559-562), of which this change lands only the run_git part.

### Unanchored findings

- **advisory**: The Trust boundary's closing enforcement list gains test_approval_prompt.py and test_cli_approval_status.py but not test_git_runner.py. That file pins the git facts (G1-G3) behind the new repository keying, which the revised Trust boundary paragraph will state.
  - evidence: `config/architecture/ARCHITECTURE.md:188`
- **advisory**: §6.3 adds a second 'imports only the standard library' check, walking the AST against sys.stdlib_module_names, beside the regex allowlist in test_repo_module_imports_only_stdlib. That leaves two test implementations of one decision procedure, which `## Single point of definition` asks to consolidate or record.
  - evidence: `plugins/arch-compliance/tests/test_repo_paths.py:74-78`

### Looked for but did not find

- ## One base exception: checked whether the design adds an exception class. It reuses GitError and AcfInputError, and RepoKey is a dataclass, so there is no new base to check.
- ## Frozen ledger format: no LedgerRow or LedgerAmendment field is touched.
- ## Build artifacts, ## Fail-loud ratchet, ## Façade sinks, ## FSM transitions, ## React boundaries: no generated tree, ratchet baseline, façade, state field or React view is touched.
- ## Soft fail-loud smells: the only new fallback-shaped paths (the folder key, provenance's 'unresolved') are explicit and reported, not silent degradation.
- ## Post-merge: the spec's follow-up is filed as an issue at merge (spec §9), which matches the declared filing rule of gh issue create.
- High-frequency misses, checked first: completeness claims (recipes present); a default re-entering for a declared value (none; the folder key is recorded); host names in prose or messages (none in §5.4-§5.6); stdlib mixins (no new exception); subprocess text without encoding (run_git fixed, no new subprocess); a package check re-implemented in a test or skill (acf-approve consumes acf-approval-status, and the hook consumes STORE_REL from acf.repo).
- The spec's Governing mandates line names every doctrine section the design touches, so unstated_mandates is empty.

## sweeper

### Claim verdicts

#### C30 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:24-30; plugins/arch-compliance/python/acf/adr/citations.py:51-62; config/architecture/ARCHITECTURE.md:300-302; plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:383`
- reasoning: run_git (diff.py:17-30) is the git runner that git_common_dir would call. The only other runtime git runner is citations._git (citations.py:51-62), which already exists and is recorded as a breach at ARCHITECTURE.md:300-302. The new function adds no third runner. I searched by behaviour for code that strips git env vars or passes env= to git: 'GIT_DIR|GIT_WORK_TREE|local-env-vars|common_dir|common-dir', then 'env=|os.environ|environ.copy' over plugins/arch-compliance and scripts. Runtime code has no hit (judge.py only reads ACF_* and API keys). The env= hits are all in tests. The one existing computation of the shared common dir is skill prose: adversarial-design-review/SKILL.md:383 has the controller compare `git rev-parse --git-common-dir` to the tree's own .git, to warn that the ledger is branch-local. That is a different job with no executable code to share; it is listed as ADJACENT.

#### C31 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_allow.py:50; plugins/arch-compliance/python/acf/approval.py:132; plugins/arch-compliance/python/acf/approval.py:137; plugins/arch-compliance/python/acf/approval.py:139; plugins/arch-compliance/python/acf/cli_allow.py:59; plugins/arch-compliance/python/acf/cli_allow.py:62; plugins/arch-compliance/python/acf/cli_check_diff.py:93`
- reasoning: load_gate_registry is used by cli_allow.py:50 and cli_check_diff.py:93. check_approval returns empty digests for STORE_IN_REPO (:132), MISSING (:137) and STALE (:139), and returns real digests only for APPROVED (:140). So the status command does need its own file_digests call. The header strings are at cli_allow.py:59 and :62, and the per-row and per-file loop is :59-65. The approval state still has one implementation (check_approval) and the fingerprint has one (approval.fingerprint). check_approval computes digests internally at :134 and then discards them for non-APPROVED states. That is a deliberate safety property: digests are the trust-bound bytes for loading host code. So it is ADJACENT, not a merge candidate. The leftover duplication of the review-preparation pipeline is filed as advisory below.

#### C32 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/hooks.json:10; plugins/arch-compliance/hooks/hooks.json:22; plugins/arch-compliance/hooks/hooks.json:4-27`
- reasoning: Both registered hooks use the form `python "${CLAUDE_PLUGIN_ROOT}/hooks/<file>.py"` (hooks.json:10 for SubagentStart, :22 for PostToolUse). The only event keys are SubagentStart and PostToolUse. I searched for an existing permission mechanism with 'PreToolUse|permissionDecision|permissions.ask|permissions.deny|onFailure' outside this spec. The only hits are this spec's own evidence probes under docs/design/evidence/. Nothing in plugins/ or config/ does this job.

#### C33 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_allow.py:27-30; plugins/arch-compliance/python/acf/cli_allow.py:56; plugins/arch-compliance/python/acf/approval.py:121-122; plugins/arch-compliance/tests/test_cli_allow.py:68`
- reasoning: _HELPER_LIMIT is defined only at cli_allow.py:27-30 and printed at :65. A grep for 'imported modules are not covered' finds it elsewhere only as the test assertion at test_cli_allow.py:68. cli_allow.py:56 `RepoTree(repo).contained(str(store)) is not None` is character-for-character the body of approval._store_inside_repo (approval.py:121-122). Replacing one with the other changes no behaviour.

#### C34 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:135; plugins/arch-compliance/python/acf/approval.py:167-173; plugins/arch-compliance/python/acf/cli_allow.py:76-77; plugins/arch-compliance/python/acf/cli_allow.py:67`
- reasoning: I swept by behaviour, not by name. First, every reader of the store's map ('read_store|\.repos\b|approvals\.json' outside docs). Second, every 'root.as_posix()' in plugins/arch-compliance. Runtime store-key consumers are exactly approval.py:135 (get), approval.py:167/170/173 (pop or assign under the key from :167) and cli_allow.py:76-77 (the revoke membership test). cli_allow.py:67 also prints the root as the approved key. That is display, not store access, and §5.3 item 4 replaces it. Every other hit is in tests, which C36 covers, or in error-message text.

#### C35 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:263; CLAUDE.md:37-39; plugins/arch-compliance/hooks/posttooluse_gate.py:10; plugins/arch-compliance/hooks/inject_constraints.py:34-35; plugins/arch-compliance/python/acf/cli_allow.py:4; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:365-366`
- reasoning: I re-ran the §5.7 recipe over README.md, docs/guides, config/architecture, skills, hooks and python/acf. Every hit that would contradict the design is in the table, or in §5.3/§5.5 (cli_allow.py:4 docstring, posttooluse_gate.py:154 notice). The recipe hits the table leaves out are posttooluse_gate.py:10/:46-48 and inject_constraints.py:10/:34-35. They describe their own hook's no-op and stay true. I then swept by behaviour with 'yourself|by a person|never by an agent|run by the user|each worktree|each clone|git runner|declare its encoding|PYTHONUTF8'. That found no live site outside the table. PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:365-366 ('the marker turns on both hooks') and :643 are an Approved spec's record and stay true of the two existing hooks. CHECK_DIFF_HOST_WIRING.md:141, :330-331 and :333 match the spec's 'left as written' row.

#### C36 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_approval.py:229; plugins/arch-compliance/tests/test_approval.py:236; plugins/arch-compliance/tests/test_approval.py:239-240; plugins/arch-compliance/tests/test_approval.py:265; plugins/arch-compliance/tests/test_cli_allow.py:70; plugins/arch-compliance/tests/test_cli_allow.py:103; plugins/arch-compliance/tests/test_approval.py:209; plugins/arch-compliance/tests/test_hooks.py:554; plugins/arch-compliance/tests/test_diff_cli.py:400`
- reasoning: I searched the store by behaviour ('read_store|\.repos\b' and 'root.as_posix()|resolve().as_posix()' over the tests). Root-keyed indexing is exactly test_approval.py:229 (on the keys set read at :228), :236, :239, :240 and :265, plus test_cli_allow.py:70 and :103. test_hooks.py:666 writes an empty store and indexes no key. 'acf-allow|acf\.cli_allow' over the tests finds the gate-message assertions at test_approval.py:209, test_diff_cli.py:400 and test_hooks.py:554. The other hit, test_cli_allow.py:12, is an import, not a message assertion. Test sites that git init the repo (test_diff_cli.py:219-239, :347) write and read through write_approval and the gate together, so both sides move to repo_key with no edit.

#### C37 — SURVIVED
- evidence: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:162-164; docs/design/CHECK_DIFF_HOST_WIRING.md:333; docs/design/HOST_DETECTOR_EXTENSION_POINT.md:64; docs/design/ARCHITECTURE_REVIEW_PORT.md:45; docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:559-561`
- reasoning: I grepped docs/design for 'no-op|acf-allow|approvals.json|keyed by|.acf/enabled|PreToolUse'. These are the hits outside the superseded HOST_DETECTOR_LOCAL_APPROVAL.md and this spec. PLUGIN_SELF_HOSTING item 11 (:162-164) is in the Supersedes header. CHECK_DIFF_HOST_WIRING:333 (each person's acf-allow) is explicitly left as an Approved record. HOST_DETECTOR_EXTENSION_POINT:64 says the marker is the opt-in for running host code on edit, which stays true. ARCHITECTURE_REVIEW_PORT:45/:205 say an auditor prompt needs no acf-allow, which is unaffected. PLUGIN_SELF_HOSTING:365-366 and :643 stay true of the two existing hooks. PLUGIN_SELF_HOSTING §9 follow-up 1 (:559-561) is partly landed here (run_git's encoding). The spec says so and leaves the other two calls under that follow-up, so this is a restatement, not a contradiction. I found no Approved doc stating a per-checkout key, human-only acf-allow, or an all-hooks no-op that the spec leaves unsuperseded.

### Unanchored findings

- **advisory**: acf-approval-status repeats acf-allow's review-preparation pipeline: load_gate_registry, approval_rows, the 'no host rows' branch and file_digests. Only the rendering is shared (describe_approval). A shared preparer in acf.approval (registry, rows, digests) would leave both CLIs as consumers and stop the two 'no rows' outcomes from drifting.
  - evidence: `plugins/arch-compliance/python/acf/cli_allow.py:50-58`
- **advisory**: approval_prompt.py adds a third copy of the hook sys.path bootstrap (_PYTHON_ROOT insert), already duplicated in posttooluse_gate.py and inject_constraints.py. A stdlib-only sibling module in hooks/ (the script directory is on sys.path[0]) could own it. The spec copies the pattern without naming the copy.
  - evidence: `plugins/arch-compliance/hooks/posttooluse_gate.py:37-41`

### Looked for but did not find

- runtime code stripping git environment variables or passing env= to git: 'GIT_DIR|GIT_WORK_TREE|local-env-vars', 'env=|os.environ|environ.copy' over plugins/arch-compliance and scripts
- runtime code computing a worktree-shared repository identity: 'common_dir|common-dir|git-common-dir' (only skill prose at adversarial-design-review/SKILL.md:383)
- an existing PreToolUse hook or permission-rule mechanism: 'PreToolUse|permissionDecision|permissions.ask|permissions.deny|onFailure'
- other runtime readers or writers of the approval store's key: 'read_store|\.repos\b|approvals\.json', 'root.as_posix()'
- other live prose binding approval to a folder or a human-only command: 'yourself|by a person|never by an agent|run by the user|each worktree|each clone|per checkout|resolved root'
- other live prose blaming the git runner's encoding: 'git runner|declare its (own|text) encoding|PYTHONUTF8'
- other definitions of the imported-helper limit text: 'imported modules are not covered'

### Relationships

- SUBSUMED: `acf.diff.git_common_dir` — responsibility `invoke git from runtime code` — existing `plugins/arch-compliance/python/acf/diff.py:17`
  - resolution: git_common_dir is a consumer of run_git (with the new env keyword), not a sibling runner; the spec already does this.
- ADJACENT: `acf.diff.git_common_dir` — responsibility `find the shared git common directory of a worktree` — existing `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:383`
  - resolution: none
  - non-merge: The skill line tells the gate controller, in prose, to compare git-common-dir with the tree's own .git so it can warn that the ledger row is branch-local. It is an instruction to an agent, not code, and it never keys anything. There is no executable to consume.
- PARTIAL_OVERLAP: `acf.approval.repo_key` — responsibility `derive the approval store key for a repository` — existing `plugins/arch-compliance/python/acf/approval.py:135`
  - resolution: repo_key becomes the one key deriver. The inline RepoTree(repo).root.as_posix() at approval.py:135, approval.py:167 and cli_allow.py:76 (and the display at cli_allow.py:67) collapse into calls to it, as §5.1 and §5.3 state.
- PARTIAL_OVERLAP: `acf.approval.describe_approval` — responsibility `render the approval review lines` — existing `plugins/arch-compliance/python/acf/cli_allow.py:59-65`
  - resolution: describe_approval becomes the one renderer. cli_allow's print loop and _HELPER_LIMIT collapse into it, and acf-approval-status consumes it, as §5.2 states.
- PARTIAL_OVERLAP: `acf.cli_approval_status.main` — responsibility `prepare the review inputs (registry, rows, digests) for a repository` — existing `plugins/arch-compliance/python/acf/cli_allow.py:50-58`
  - resolution: Extract a preparer in acf.approval returning registry, rows and digests, with the 'no host rows' outcome. cli_allow.main and cli_approval_status.main both consume it, and describe_approval stays the renderer.
- ADJACENT: `acf.cli_approval_status.main (own file_digests call)` — responsibility `compute detector file digests for a non-APPROVED state` — existing `plugins/arch-compliance/python/acf/approval.py:134`
  - resolution: none
  - non-merge: check_approval computes digests but returns them only for APPROVED, because Approval.digests is what host loading trusts. Returning them for MISSING or STALE would hand callers bytes nobody approved. The second computation is the price of keeping that boundary.
- PARTIAL_OVERLAP: `approval_prompt.py APPROVAL_NEEDLES` — responsibility `define the set of commands treated as an approval` — existing `plugins/arch-compliance/skills/acf-setup/SKILL.md:24`
  - resolution: APPROVAL_NEEDLES stays the canonical set. Decision 7's ask rules in /acf-setup prose are a recorded second encoding under ## Single point of definition, held together by §6.3's two-way pin test.
- IDENTICAL: `approval_prompt.py sys.path bootstrap` — responsibility `make plugin python importable from a hook script` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:37-41`
  - resolution: A stdlib-only hooks/_bootstrap.py, importable because the script directory is sys.path[0], would own the insert. posttooluse_gate.py:37-41, inject_constraints.py:27-29 and approval_prompt.py would import it.
- ADJACENT: `approval_prompt.py stdin handling` — responsibility `read the hook's stdin JSON payload` — existing `plugins/arch-compliance/hooks/posttooluse_gate.py:211-221`
  - resolution: none
  - non-merge: posttooluse_gate reads stdin leniently: malformed JSON becomes None. The approval hook must fail closed: a needle in malformed JSON exits 2. It also byte-scans before parsing. Sharing the lenient reader would break that fail-closed contract.
- SUBSUMED: `acf.repo.STORE_REL (moved)` — responsibility `declare the approval store's home-relative path` — existing `plugins/arch-compliance/python/acf/approval.py:36-37`
  - resolution: Move it to acf.repo. approval.store_path, the hook's needle and test_approval.py:12 import it from there, as §5.4 states.

### Two-owner counts

- invoke git from runtime code (run_git, citations._git; pre-existing, declared): 2
- define the set of commands treated as an approval (APPROVAL_NEEDLES, acf-setup permissions.ask rules): 2
- make plugin python importable from a hook script (inject_constraints, posttooluse_gate, approval_prompt): 3
- prepare approval review inputs: registry, rows, digests (cli_allow.main, cli_approval_status.main): 2
- compute detector file digests in one acf-approval-status run (check_approval internal, status's own call): 2
- render the refusal text for unapproved host rows (require_approval, posttooluse_gate notice; pre-existing): 2

### Document conflicts

- `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:90` (contradicts): One approval per checkout directory. The key is the resolved root, so each clone and each git worktree needs its own `acf-allow`.
- `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:164` (contradicts): and no-op without `.acf/enabled`
- `docs/design/CHECK_DIFF_HOST_WIRING.md:333` (contradicts): host rows needs each person's `acf-allow`
- `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:559` (restates): Text decoding and one git runner. The three subprocess calls of §4.1 item 7 declare `encoding="utf-8"`, and the two git runners become one
- `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:365` (restates): `/acf-setup` writes `.acf/enabled`, and the marker turns on both hooks for this repository

## hardening

### Claim verdicts

#### C38 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:135; plugins/arch-compliance/python/acf/diff.py:24-30`
- reasoning: Today's key is RepoTree(repo).root.as_posix() (approval.py:135, :167), so every worktree root is its own entry. I reproduced G1, G2 and G3 in a scratch repo under %TEMP% with git 2.49.0.windows.1. Main checkout w and linked worktree wt both print <tmp>/w/.git. With GIT_DIR=<w>/.git/worktrees/wt, wt/sub printed an empty prefix line; with GIT_DIR stripped it printed 'sub/'. A plain dir gave 'fatal: not a git repository' with exit 128. `git rev-parse --local-env-vars` lists GIT_DIR, GIT_WORK_TREE, GIT_COMMON_DIR, GIT_CONFIG_PARAMETERS, GIT_CONFIG_COUNT and the rest. It exits 0 outside a repo and with GIT_DIR set to a nonexistent path, so step 1 of git_common_dir cannot fail on the env it is meant to clean. run_git (diff.py:24-30) passes no env today, so it inherits the hook's GIT_DIR, and stripping is needed. The prefix keeps two hosts in one repo apart, and the fingerprint still decides the state.

#### C39 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:24-30; plugins/arch-compliance/python/acf/diff.py:35-39`
- reasoning: The silent None comes from run_git itself: subprocess.run(text=True) with no encoding (diff.py:24-30). On Windows a reader-thread UnicodeDecodeError leaves stdout None with exit 0. _git (diff.py:35-39) then returns that None. Strict decoding in run_git hardens the producer for every caller (diff.py:35, rollup.py:57/:78/:82/:90, the architecture-review snippet at SKILL.md:289). That is rung 3 at the producer, not recovery in one consumer. One side effect is reported separately as an unanchored advisory: added_lines decodes diff content.

#### C40 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/hooks.json:16-27; plugins/arch-compliance/hooks/posttooluse_gate.py:103-112`
- reasoning: Per plugins-reference.md (Standard layout table), a plugin can ship hooks, skills, agents, MCP/LSP servers, monitors, bin/ and so on, but no permission rules. userConfig writes only pluginConfigs. So the hook is the one channel a plugin owns. permissions.md:271 says a Bash rule 'doesn't match the same program invoked in a different form'. hooks.md:809/:908/:942 say a failing or timed-out PreToolUse hook lets the call through unless onFailure is 'block' (v2.1.295+). The existing hooks no-op without .acf/enabled (posttooluse_gate.py:103-112). The store is per user at Path.home()/STORE_REL (approval.py:66-70), and acf-allow takes --repo (cli_allow.py:38), so a marker gate would leave the store unguarded from unmarked repositories.

#### C41 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_allow.py:58; plugins/arch-compliance/python/acf/approval.py:102-108`
- reasoning: fingerprint(rows, digests) (approval.py:102-108) is a pure function of the rows and file digests, and digests are computed at cli_allow.py:58 just before the write at :66. Comparing --fingerprint HEX there refuses whenever the bytes differ from those reviewed. cli_allow.main checks nothing about its caller today (cli_allow.py:33-71). Without the CLAUDE_CODE_CHILD_SESSION refusal, an agent's bare `acf-allow` would put a prompt in front of the user that is bound to no reviewed fingerprint. The refusal is env-based and an agent can strip the variable, but the text hook still prompts. §4 declares this residual.

#### C42 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:250; plugins/arch-compliance/python/acf/approval.py:37`
- reasoning: I checked case-insensitively in Python. 'acf-approval-status' and 'python -m acf.cli_approval_status' contain none of 'acf-allow', 'acf.cli_allow' or 'approvals.json'. The ask rule Bash(acf-allow:*), equal to 'acf-allow *' per permissions.md:208, does not prefix-match 'acf-approval-status'. Step 1 scans raw bytes and can hit a needle in another field, such as the Bash tool's description. Step 2 then checks only tool_input.command, so the status command still passes silently. permission-modes.md:34-36 says explicit ask rules are not auto-approved 'in any mode, including bypassPermissions'. So the offered rules are the documented guarantee there.

#### C43 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:17-30; plugins/arch-compliance/python/acf/review/rollup.py:57-60`
- reasoning: run_git is one subprocess.run call (diff.py:24-30). Capturing bytes, decoding stdout strictly and stderr with replace, and building subprocess.CompletedProcess(args, returncode, str, str) keeps the declared return type. Every caller reads only .returncode, .stdout and .stderr as str: _git at diff.py:35-39 and rollup.py:57-60/:78-95. The test fake fake_run_git(repo, *args) (test_review_rollup.py:115) is unaffected, because rollup passes no env. test_diff_cli.py:215-229 pins 'never raises on a non-zero status', which still holds: the new raise is for undecodable stdout only. Only rollup.provenance's body changes (the spec's GitError catch), not its call to run_git.

#### C44 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:128-129; plugins/arch-compliance/python/acf/approval.py:135; plugins/arch-compliance/python/acf/approval.py:167; plugins/arch-compliance/python/acf/cli_allow.py:76`
- reasoning: check_approval returns NOT_NEEDED at :128-129, before the store check (:131), the digests (:134) and the key (:135), so no git runs for approval there. The key is a single expression at approval.py:135 (inside .get()), at approval.py:167 (key = ...) and at cli_allow.py:76 (key = ...). Each is replaceable by repo_key(repo).key. _revoke then calls write_approval (cli_allow.py:81), which recomputes the key, so the two agree.

#### C45 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:106; plugins/arch-compliance/hooks/posttooluse_gate.py:140-145; plugins/arch-compliance/python/acf/cli_allow.py:47-70`
- reasoning: cli_check_diff.py:106 is `except (GitError, AcfInputError, UnknownDetectorError, DetectorPackError)` and wraps require_approval at :102. posttooluse_gate.py:140-145 wraps load_mandates and check_approval and catches (AcfInputError, UnknownDetectorError). GitError subclasses AcfError, not AcfInputError (exceptions.py:33), so it must be added, along with an import at :125. It then prints 'acf: <msg>' and returns failure=2 in hook mode (:101), with no traceback, unlike the outer handler at :89-94. cli_allow's try at :47 covers `return _revoke(repo)` at :49, so one tuple at :68 covers both paths. The grep found no other caller of check_approval, require_approval or write_approval.

#### C46 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_allow.py:58-67`
- reasoning: Line 58 is `digests = file_digests(repo, rows)`. Lines 59-65 print the rows header, the rows, the files header, the files and _HELPER_LIMIT. Line 66 writes, and line 67 is the closing print. The fingerprint comparison fits between :58 and :59, so refusal happens before the write at :66.

#### C47 — SURVIVED
- evidence: `plugins/arch-compliance/hooks/hooks.json:16-27; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:234-238`
- reasoning: The existing hooks.json already uses a pipe matcher with a command hook and timeout (hooks.json:16-27). I fetched hooks.md read-only. :460/:512 list `onFailure` 'continue' or 'block', requiring v2.1.295. :120/:127 show matcher 'Bash|PowerShell'. :762 makes permission_mode a common input field with 'bypassPermissions' among its values. :1882-1884 says PreToolUse receives tool_name and tool_input. :2091-2092 says 'ask' prompts and permissionDecisionReason 'For "ask", shown to the user in the permission prompt'. :2100 adds that the prompt is labelled [plugin:<name>]. Exit 2 blocks (permissions.md:683).

#### C48 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:260; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:136-138`
- reasoning: Fetched read-only. hooks.md:2139 says a PreToolUse 'ask' in auto mode normally sends the call to the permission prompt and the classifier doesn't decide it. The exceptions are protected paths, which the classifier may deny (a fail-closed outcome), and SubagentHandback. permission-modes.md:34-36 says explicit ask rules are not auto-approved 'in any mode, including bypassPermissions'. permissions.md:361 says Edit rules apply to all built-in tools that edit files. permissions.md:394 supports the `~/path` anchor used by Edit(~/.acf/**).

#### C49 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:128; plugins/arch-compliance/tests/conftest.py:10-17`
- reasoning: I observed it read-only: CLAUDE_CODE_CHILD_SESSION=1 in this session's Bash tool and in its PowerShell tool. env-vars.md:225 says it is set to 1 in subprocesses spawned via the Bash, PowerShell and Monitor tools, hook commands and status line commands, by Claude Code only (v2.1.172+). The same line warns that it can be inherited by a screen session or background launcher first started from the Bash tool. That causes a false refusal only, which the error message's 'terminal outside Claude Code' route resolves.

#### C50 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_repo_paths.py:74-78; plugins/arch-compliance/tests/test_repo_paths.py:81-108; pyproject.toml:5`
- reasoning: test_repo_module_imports_only_stdlib (:74-78) is a regex allowlist over repo.py. An AST walk with sys.stdlib_module_names is buildable. pyproject.toml:5 requires >=3.11, and I checked on 3.13 that '__future__' is in sys.stdlib_module_names, so `from __future__ import annotations` passes. The poisoned-module test (:81-108) loops over hooks with input=''. approval_prompt.py needs its own subprocess call with a Bash acf-allow payload, which the fixture's poison/env setup supports.

#### C51 — SURVIVED
- evidence: `plugins/arch-compliance/tests/conftest.py:10-17; plugins/arch-compliance/tests/test_approval.py:229`
- reasoning: _isolated_home already takes monkeypatch and uses setenv (conftest.py:10-17), so delenv(..., raising=False) fits. This matters: this session's shell has CLAUDE_CODE_CHILD_SESSION=1, so a suite started here would trip Decision 5. On this machine `git rev-parse` in a fresh mktemp dir under %TEMP% exited 128 with 'not a git repository'. The existing root-keyed assertions (test_approval.py:229 and following) already depend on that.

#### C52 — SURVIVED
- evidence: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:250; docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:398`
- reasoning: I computed this in Python: any(n in cmd.lower() for n in ('acf-allow','acf.cli_allow','approvals.json')). 'pytest plugins/arch-compliance/tests/test_cli_allow.py' is False and 'git add plugins/arch-compliance/python/acf/cli_allow.py' is False ('acf/cli_allow' is not 'acf.cli_allow'). 'python -m acf.cli_allow' is True, 'acf-allow --fingerprint abc' is True and 'cd x && ACF-ALLOW' is True. This repository's cwd path contains no needle, so the raw-byte prefilter does not fire on cwd alone.

#### C53 — SURVIVED
- evidence: `docs/design/evidence/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT/hook_deny_source_probe.out:11; docs/design/evidence/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT/hook_deny_source_probe.out:14`
- reasoning: I re-ran the committed probe against the named 2.1.330 binary with PYTHONIOENCODING=utf-8. Its output is byte-identical to the committed .out, ignoring CR, including SHA-256 fa797c1b... at :2. Line :5 shows blockingError mapped to {behavior:'deny',decisionReason:{type:'hook'}}. Line :11 shows r4s taking `if(e?.behavior==="deny")` before the allow/ask branch. Its returns are kte(e,...), {decision:e}, or a deny with the hook's decisionReason restored. Line :14 shows kte returning {decision:k} whenever the mod/policy result k is not 'ask', and canUseTool deciding only on an ask. Two non-hook pre-checks (mU(o), TIe()) precede the deny branch. Their semantics are not visible, which is why the claim is correctly non-load-bearing and §8 item 4 is the live check.

#### C54 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/repo.py:13; plugins/arch-compliance/python/acf/approval.py:36-37; plugins/arch-compliance/python/acf/approval.py:68; plugins/arch-compliance/hooks/posttooluse_gate.py:37-43`
- reasoning: repo.py:13 is `from pathlib import Path`, so STORE_REL = Path('.acf')/'approvals.json' needs no new import there. The regex allowlist in test_repo_paths.py:76-77 is unchanged. approval.py:68 is the only store_path use. test_approval.py:12 lists STORE_REL in its acf.approval import, and :85 asserts its value. Both still work after the move, whether the test imports from acf.repo or through the re-export. posttooluse_gate.py:37-43 shows the sys.path insert followed by a module-scope `from acf.repo import`. repo.py:3-6 declares it stdlib plus acf.exceptions only.

#### C55 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:24; plugins/arch-compliance/python/acf/approval.py:37`
- reasoning: I ran re.findall(r'`(?:Bash|PowerShell|Edit)\([^`]*\)`') over all 319 lines of acf-setup/SKILL.md, which returned []. So any token found later is a Decision 7 rule. fnmatch('~/.acf/approvals.json', '~/.acf/**') is True. The shell rules Bash(acf-allow:*) and Bash(python -m acf.cli_allow:*) each contain a needle. STORE_REL.name at approval.py:37 is 'approvals.json'.

#### C56 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/approval.py:134-140; plugins/arch-compliance/python/acf/approval.py:173-176`
- reasoning: State is decided by comparing entry.fingerprint with fingerprint(rows, file_digests(repo, rows)) for the worktree being checked (approval.py:134-140). One entry per repository (approval.py:173-176) therefore yields APPROVED for any worktree whose bytes equal the approved ones, and STALE for any that differ. Marking an unedited worktree STALE would need a second datum that this design deliberately does not keep. The departure follows directly from the fingerprint.

### Unanchored findings

- **advisory**: Strict UTF-8 in run_git also applies to `git diff -U0`, which acf-check-diff runs on every changed in-repo file whatever its suffix (before the .py/.ts filter). On Windows, a changed non-UTF-8 text file (cp1252 .txt/.csv/.ini) now raises GitError and refuses the whole gate. The default cp1252 codec used to decode all but five byte values, and added_lines needs only the ASCII hunk headers. So §7's mitigation (the locale codec 'already lost such output without an error (G4)') is true only for those five bytes. The risk row should state this outcome. It matches what Linux CI already does: there, text=True's strict locale decode raises UnicodeDecodeError on the same diff.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:148`
- **advisory**: Commands that a skill injects at load time fire PreSkillShellCommand, not PreToolUse (hooks.md 'Commands that reach a PreSkillShellCommand hook': they run after the injected-command permission check, also in bypassPermissions). The approval hook is registered only under PreToolUse. So an agent can write a project skill whose injected command is `acf-allow --fingerprint X` and invoke it, and the hook never sees it. In bypass mode without the optional Decision 7 ask rules, nothing prompts. The same script could be registered under PreSkillShellCommand too: that event takes the same tool_name, tool_input.command and permission_mode, and treats 'ask' as a block. §4's residual list could also name this path.
  - evidence: `plugins/arch-compliance/hooks/hooks.json:16-27`

### Looked for but did not find

- A second caller of check_approval/require_approval/write_approval outside cli_check_diff.py:102, posttooluse_gate.py:142 and cli_allow.py:66/:81 (none in python/, hooks/, skills/ or scripts/)
- A run_git caller that passes keyword arguments or relies on text=True semantics beyond .returncode/.stdout/.stderr (none: diff.py:35, rollup.py:57/:78/:82/:90, architecture-review SKILL.md:289)
- A failure of `git rev-parse --local-env-vars` outside a repository or with a bogus inherited GIT_DIR (it exits 0 in both)
- A git-locating variable that survives stripping and still changes the prefix (GIT_DIR, GIT_WORK_TREE, GIT_COMMON_DIR, GIT_PREFIX, GIT_CONFIG_PARAMETERS, GIT_CONFIG_COUNT are all in git 2.49's list)
- Any way for a plugin to ship permission rules (plugins-reference.md standard layout has none)
- A backticked Bash(/PowerShell(/Edit( token already in acf-setup/SKILL.md (none, so the pin test has no false positives today)
- Drift between the committed hook_deny_source_probe.out and the binary (the re-run is identical)
- A needle hit on this repository's own routine commands (pytest of test_cli_allow.py and git add of cli_allow.py do not match)

### Mechanism traces

- **run_git decodes UTF-8 and fails loud (GitError on undecodable stdout)**
  - invalid state: proc.returncode == 0 and (proc.stdout is None or proc.stdout != git_stdout_bytes.decode('utf-8'))
  - producer: `plugins/arch-compliance/python/acf/diff.py:24-30`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:167-171`
- **git_common_dir strips git's --local-env-vars from the environment of the key query**
  - invalid state: 'GIT_DIR' in os.environ and 'GIT_WORK_TREE' not in os.environ and cwd is a subfolder, so `--show-prefix` prints '' instead of the subfolder
  - producer: `plugins/arch-compliance/python/acf/diff.py:24-30`
  - rung 2 (highest applicable 2); repairs=False
  - hardening rejected because: This design strips the variables only for the key query (§5.1). The diff calls are unchanged and outside this spec; they are follow-up 1 in §9.
  - spec citation: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:177-179`
- **repo_key folder-key fallback for a directory git reports is not a repository**
  - invalid state: git rev-parse exit == 128 and 'not a git repository' in stderr (every other non-zero or malformed result raises GitError)
  - producer: `plugins/arch-compliance/python/acf/approval.py:135`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: It is not a host declaration: it applies only when git reports that the directory is not a repository, and it keeps one approval per folder as before.
  - spec citation: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:104`
- **approval_prompt.py PreToolUse hook (ask on needle match, deny in bypassPermissions, onFailure block, exit 2 on internal error)**
  - invalid state: a Bash/PowerShell tool_input.command containing 'acf-allow'|'acf.cli_allow'|'approvals.json' (case-insensitive), or a file tool path containing 'approvals.json', executing with no user answer at a permission prompt
  - producer: `plugins/arch-compliance/python/acf/cli_allow.py:33-71`
  - rung 5 (highest applicable 5); repairs=False
  - hardening rejected because: This design makes the honest path work remotely and the naive path prompt. It does not make the dishonest path impossible.
  - spec citation: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:232-257`
- **acf-allow --fingerprint binding**
  - invalid state: args.fingerprint is not None and args.fingerprint != fingerprint(rows, file_digests(repo, rows)) at write time
  - producer: `plugins/arch-compliance/python/acf/cli_allow.py:58`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:224`
- **Refusal of acf-allow without --fingerprint under CLAUDE_CODE_CHILD_SESSION=1**
  - invalid state: os.environ.get('CLAUDE_CODE_CHILD_SESSION') == '1' and not args.fingerprint and not args.revoke
  - producer: `plugins/arch-compliance/python/acf/cli_allow.py:46-66`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:225`
- **Decision 7 permissions.ask rules offered by /acf-setup, pinned to APPROVAL_NEEDLES by test**
  - invalid state: a needle in APPROVAL_NEEDLES with no covering ask rule in acf-setup/SKILL.md, or an ask rule containing no needle
  - producer: `plugins/arch-compliance/skills/acf-setup/SKILL.md:24`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: The rules live in the user's settings, which the plugin cannot import, so the copy stays. test_approval_prompt.py pins the two (§6.3).
  - spec citation: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:135-138`
- **rollup.provenance catches GitError from its blame call and returns ('unresolved', message)**
  - invalid state: git blame --porcelain stdout bytes for the finding's line are not valid UTF-8
  - producer: `plugins/arch-compliance/python/acf/review/rollup.py:78-80`
  - rung 5 (highest applicable 5); repairs=True
  - hardening rejected because: The roll-up is report-only (acf/review/rollup.py:3, "Drift, staleness and provenance are report-only"), so provenance catches GitError from its blame call and returns ("unresolved", <message>), its existing outcome for a git failure.
  - spec citation: `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md:174`

## Claims

- **C1** [root_cause] [load-bearing]: check_approval looks the store entry up by RepoTree(repo).root.as_posix() (approval.py:135) and write_approval writes under the same key (approval.py:167). Every git worktree has its own root, so a new worktree of an approved repository reads as MISSING even when its active host rows and detector files are byte-identical to the approved ones.
  - spec citation: `plugins/arch-compliance/python/acf/approval.py:135`
- **C2** [root_cause] [load-bearing]: Approval is meant to be given only by the user at a terminal. This is a prose convention: the diff gate's refusal (approval.py:149-154), the PostToolUse hook's notice (posttooluse_gate.py:150-155), /acf-setup (acf-setup/SKILL.md:24 and :288) and /acf-mandate (acf-mandate/SKILL.md:139) tell the agent to ask the user to run acf-allow and not to run it itself, and cli_allow.main (cli_allow.py:33-71) checks nothing about its caller.
  - spec citation: `plugins/arch-compliance/python/acf/approval.py:149-154`
- **C3** [premise] [load-bearing]: In issue #62 the owner reports that Remote Control's `!` prefix does not execute a command, so a user following a session remotely cannot run acf-allow. The issue is readable with `gh issue view 62 --repo IanDBallard/arch-compliance-for-superpowers`.
  - spec citation: `None`
- **C4** [premise]: The Supersedes header lists the parts of HOST_DETECTOR_LOCAL_APPROVAL.md this design replaces: Decision 2's key (:68), Decision 6's channel (:72), Decision 7's notice naming 'the command to run' (:73), the require_approval message text (:127), the hook notice text (:156), the test expectation that the notice contains acf-allow (:251), the second clause of the residual at :84 and the residual at :90. From PLUGIN_SELF_HOSTING_AND_DOCTRINE.md item 11 (:162-164) it supersedes the list of when the hooks run and the no-op-without-marker statement for the new hook. Every other decision of the cleared spec stands.
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:90`
- **C5** [premise]: The #62 refusal text 'acf: host detectors need approval: no approval for this repository' is what the current code prints for an absent store entry (MISSING reason via require_approval and cli_check_diff).
  - spec citation: `None`
- **C6** [premise] [load-bearing]: The fingerprint covers the active host rows and the SHA-256 digests of the detector files, and nothing in it depends on the store key. So re-keying leaves fingerprint semantics unchanged, and a worktree whose host rows or detector files differ from the approved bytes is STALE rather than APPROVED.
  - spec citation: `None`
- **C7** [premise] [load-bearing]: Deferral: imported helpers and executed tools are outside the fingerprint (HOST_DETECTOR_LOCAL_APPROVAL.md:83). Per-folder keying never covered them either, since `git checkout` of another branch in an approved folder runs that branch's helpers under the existing approval. Nothing today ties approval to the branch or to helper bytes.
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:83`
- **C8** [premise] [load-bearing]: Deferral: the cleared spec's first clause at :84 accepts that whoever can write the user's home directory or run acf-allow can approve. So a text-matching hook that a determined agent can bypass (by importing write_approval in a script, or building the command string at run time) widens no exposure the cleared design had not accepted. Today neither cli_allow.main nor write_approval checks its caller.
  - spec citation: `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:84`
- **C9** [premise] [load-bearing]: G4: today's run_git (diff.py:24-30, text=True, no encoding) decodes git's UTF-8 output with the locale codec. Under cp1252 on Windows, for a directory name whose UTF-8 bytes include a byte cp1252 leaves undefined (Á = C3 81, Ý = C3 9D), subprocess's reader thread raises UnicodeDecodeError and CompletedProcess.stdout is None with exit 0; for other non-ASCII names (é, ü, CJK) stdout is wrong text; in neither case does an exception reach the caller. The committed probe docs/design/evidence/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT/run_git_decode_probe.py, which calls acf.diff.run_git from this checkout with PYTHONUTF8=0, reproduces this; its recorded output is run_git_decode_probe.out beside it.
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
- **C16** [premise]: §4 residual: where no managed settings or Team/Enterprise login restrict them, a user-installed Claude Code mod handling tool.check can approve a call that a PreToolUse hook sent to the prompt or that an ask rule matched (external, permissions.md), and in Claude Code 2.1.330 the hook's deny passes through the mod checks before it is returned (hook_deny_source_probe.out:14).
  - spec citation: `docs/design/evidence/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT/hook_deny_source_probe.out:14`
- **C17** [mandate] [load-bearing]: `## No shims`: not reading old root-keyed entries complies, and reading them would be a compatibility shim the section forbids.
  - spec citation: `config/architecture/ARCHITECTURE.md:53-55`
- **C18** [mandate] [load-bearing]: `## Declared, never defaulted`: the folder key used only when git reports that the directory is not a repository is not a host declaration. Recording it in the section's list of recorded defaults (changing 'Three defaults' to 'Four defaults') and printing the scope through describe_approval satisfies the mandate.
  - spec citation: `config/architecture/ARCHITECTURE.md:213-228`
- **C19** [mandate] [load-bearing]: `## One owner for host paths`: approval.py joins two strings git printed and resolves nothing itself, so it adds no host-path resolution outside RepoTree and needs no allowlist entry in test_repo_tree_guard.py. Moving STORE_REL (the per-user store's home-relative path) into acf.repo, with the section's first sentence (:117-119) and repo.py's docstring (:1-6) updated to say acf.repo also declares it, keeps the section consistent.
  - spec citation: `config/architecture/ARCHITECTURE.md:115-138`
- **C20** [mandate] [load-bearing]: `## Single point of definition`: git_common_dir and the new env keyword are built on run_git and add no further git runner. The hook reads the store file name from STORE_REL in acf.repo, its one definition. The approval command set's second encoding (the hook's APPROVAL_NEEDLES versus the permissions.ask rules /acf-setup offers) stays because the rules live in the user's settings, and it is recorded in the section and pinned both ways by a test, as the section's 'recorded not hidden' practice requires.
  - spec citation: `config/architecture/ARCHITECTURE.md:295-317`
- **C21** [mandate] [load-bearing]: `## Fail loud`: git_common_dir returns None only for exit 128 with 'not a git repository' (under LC_ALL=C), and raises GitError carrying git's stderr for every other outcome (another exit, malformed output, OSError, undecodable output). Each entry point reports that GitError on its existing channel (cli_check_diff exit 1, PostToolUse hook exit 2, acf-allow and acf-approval-status exit 1). The new hook's broad handler prints to stderr, exits 2 and carries the fail-loud.bare-except-ok token with a reason. Together these comply with the section.
  - spec citation: `config/architecture/ARCHITECTURE.md:26-43`
- **C22** [mandate] [load-bearing]: `## Host detectors and call sites` trust boundary: revising the Trust boundary paragraph (:179-186) and its closing test list (:188) as §5.7 states keeps the doctrine consistent with the code, and nothing else in the section requires a human-run terminal command.
  - spec citation: `config/architecture/ARCHITECTURE.md:179-186`
- **C23** [mandate] [load-bearing]: `## Declared text decoding`: making run_git capture bytes and decode them as strict UTF-8 itself satisfies the section for run_git, so run_git leaves its declared debt ('Three calls' becomes 'Two calls'), and the remaining two (adr/citations.py _git and the TypeScript bridge) stay declared.
  - spec citation: `config/architecture/ARCHITECTURE.md:268-279`
- **C24** [mandate]: `## Release discipline`: the design changes skill prose and adds a skill, so it bumps pyproject.toml:3 and plugin.json:3 from 0.3.4 to 0.3.5.
  - spec citation: `config/architecture/ARCHITECTURE.md:283-284`
- **C25** [mandate]: `## Prose names no host`: the new gate-message texts (§5.5), the hook's reasons (§5.4) and the acf-approve skill name no host repository.
  - spec citation: `config/architecture/ARCHITECTURE.md:232-233`
- **C26** [mandate]: `## POSIX paths`: the stored key uses as_posix() on the git common dir with git's forward-slash prefix, so keys are POSIX on every platform.
  - spec citation: `config/architecture/ARCHITECTURE.md:57-66`
- **C27** [mandate]: `## Live consumers`: each new function and constant (git_common_dir, the env keyword of run_git, repo_key/RepoKey, describe_approval, HELPER_LIMIT, cli_approval_status.main) has a live consumer in the same change.
  - spec citation: `config/architecture/ARCHITECTURE.md:250-254`
- **C28** [mandate]: `## No completeness claims`: the spec's enumerations (run_git callers, GitError entry points, prose sites, test sites) are per-item lists backed by recipes, and the §5.7 lead disclaims completeness.
  - spec citation: `config/architecture/ARCHITECTURE.md:256-266`
- **C29** [mandate]: `## Scoped refactor` ('remove legacy dependencies or non-contractual patterns in code paths you are changing. Do not expand scope to unrelated modules'): fixing run_git's decoding, which the new key query calls, and leaving adr/citations.py _git and the TypeScript bridge as declared debt complies.
  - spec citation: `config/architecture/ARCHITECTURE.md:319-323`
- **C30** [shape_fit] [load-bearing]: git_common_dir and the env keyword extend the existing acf.diff git-runner shape (beside run_git) and create no second way to run git from runtime code; nothing in the tree already strips git environment variables or computes a repository identity shared by worktrees.
  - spec citation: `plugins/arch-compliance/python/acf/diff.py:17`
- **C31** [shape_fit] [load-bearing]: acf-approval-status reuses load_gate_registry, check_approval, approval_rows, file_digests and fingerprint, so there is still one way to compute an approval state and a fingerprint. It computes digests itself because check_approval's Approval.digests is empty for MISSING, STALE and STORE_IN_REPO (approval.py:132, :137, :139). describe_approval gives acf-allow and acf-approval-status one review renderer and keeps cli_allow's current review lines, including the two header lines at cli_allow.py:59 and :62.
  - spec citation: `plugins/arch-compliance/python/acf/cli_allow.py:50`
- **C32** [shape_fit] [load-bearing]: The new PreToolUse approval hook fits the plugin's existing hook shape: hooks.json registers command hooks as `python "${CLAUDE_PLUGIN_ROOT}/hooks/<file>.py"`, and no existing PreToolUse hook or permission mechanism in the plugin does this job.
  - spec citation: `plugins/arch-compliance/hooks/hooks.json:2`
- **C33** [shape_fit]: Moving the imported-helper limit text from cli_allow.py:27-30 to acf.approval.HELPER_LIMIT gives the two scripts one text, and cli_allow.py:56 reusing approval._store_inside_repo (approval.py:121-122) removes a repeated expression with identical behaviour.
  - spec citation: `plugins/arch-compliance/python/acf/cli_allow.py:27-30`
- **C34** [sweep] [load-bearing]: The places that read or write the approval store by key are check_approval (approval.py:135), write_approval (approval.py:167) and cli_allow._revoke (cli_allow.py:76). Switching those three to repo_key(repo).key leaves no consumer keying by the worktree root.
  - spec citation: `plugins/arch-compliance/python/acf/approval.py:135`
- **C35** [sweep]: The §5.7 table (with §5.3 and §5.5) lists the tracked prose and code sites that would contradict the design: approval per folder or resolved root, acf-allow run only by the user, plugin hooks no-op without .acf/enabled, the git runner not declaring its encoding (including CLAUDE.md:37-39 and acf-setup/SKILL.md:263), and acf.repo declaring only host paths; CHECK_DIFF_HOST_WIRING.md :141, :330-331 and :333 are left as an Approved spec's record.
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:24`
- **C36** [sweep]: The existing test assertions that index the approval store by the root key are test_approval.py:229, :236, :239, :240, :265 and test_cli_allow.py:70, :103. The tests asserting acf-allow in a gate message are test_approval.py:209, test_hooks.py:554 and test_diff_cli.py:400.
  - spec citation: `None`
- **C37** [shape_fit]: No tracked Approved design document other than those in the Supersedes header states a contract (per-checkout approval key, human-only acf-allow, every plugin hook a no-op without .acf/enabled) that this design contradicts without superseding it.
  - spec citation: `None`
- **C38** [mechanism_justification] [load-bearing]: Keying by `<git common dir>::<prefix>` is justified because the folder adds no review. The prefix keeps two hosts in one repository from flipping each other STALE. Stripping git's local env vars is needed because an inherited GIT_DIR changes the prefix (G3). The folder key exists only for directories git says are not repositories.
  - spec citation: `None`
- **C39** [mechanism_justification] [load-bearing]: Hardening run_git itself (strict UTF-8, GitError on undecodable stdout) rather than adding recovery around the key is the right rung: it removes the silent None of G4 at the failure point for every caller, instead of catching UnicodeDecodeError in one consumer.
  - spec citation: `None`
- **C40** [mechanism_justification] [load-bearing]: A plugin-shipped PreToolUse hook is justified because a plugin cannot ship user permission rules, and a rule does not match the same program started another way (python -m acf.cli_allow). onFailure 'block' is justified so a crashed or missing hook cannot let an approval through. The hook runs without .acf/enabled because the store is per user and an agent in an unmarked repository could approve another repository with --repo.
  - spec citation: `None`
- **C41** [mechanism_justification] [load-bearing]: The --fingerprint binding is needed so the bytes approved at the prompt are the bytes the agent summarized. Refusing acf-allow without --fingerprint when CLAUDE_CODE_CHILD_SESSION=1 is needed so an agent cannot obtain approval of unreviewed bytes through the prompt.
  - spec citation: `None`
- **C42** [mechanism_justification] [load-bearing]: A separate read-only acf-approval-status command, whose name contains none of the hook's needles (acf-allow, acf.cli_allow, approvals.json), is needed so the agent can gather the review without prompting. /acf-setup's offered permissions.ask rules are needed as the documented guarantee in bypassPermissions mode.
  - spec citation: `None`
- **C43** [implementability] [load-bearing]: run_git (diff.py:17-30) can be changed to capture bytes, decode stdout as strict UTF-8 (GitError on failure) and stderr with errors='replace', take a keyword-only env mapping passed to subprocess.run, and still return subprocess.CompletedProcess[str], with diff._git and the other callers unchanged.
  - spec citation: `plugins/arch-compliance/python/acf/diff.py:17-30`
- **C44** [implementability] [load-bearing]: check_approval returns NOT_NEEDED (approval.py:128-129) before any key computation, so a repository without host rows at the call sites runs no git for approval. check_approval (:135), write_approval (:167) and cli_allow._revoke (cli_allow.py:76) each compute the key in one expression replaceable by repo_key(repo).key.
  - spec citation: `plugins/arch-compliance/python/acf/approval.py:128-129`
- **C45** [implementability] [load-bearing]: A GitError from the key reaches a handler at each entry point. cli_check_diff.py:106 already catches GitError. posttooluse_gate.py:141-145 and cli_allow.py:68 (whose try also covers _revoke) can add GitError to their tuples. The PostToolUse hook then prints the message and exits 2 without a traceback.
  - spec citation: `plugins/arch-compliance/hooks/posttooluse_gate.py:141-145`
- **C46** [implementability] [load-bearing]: In cli_allow.py, `digests = file_digests(repo, rows)` is at :58 and stays, so the --fingerprint comparison can follow it before the store write. The review lines at :59-65 can be replaced by describe_approval, and the closing print is at :67.
  - spec citation: `plugins/arch-compliance/python/acf/cli_allow.py:58`
- **C47** [implementability] [load-bearing]: Claude Code's plugin hooks.json accepts a PreToolUse entry with matcher `Bash|PowerShell|Write|Edit|MultiEdit|NotebookEdit`, a command hook, `timeout` and `"onFailure": "block"` (v2.1.295+). The hook's stdin JSON carries permission_mode, tool_name and tool_input (command / file_path / notebook_path). hookSpecificOutput with permissionDecision 'ask' and a reason is honoured and the reason shown, and exit 2 blocks the call. External: https://code.claude.com/docs/en/hooks.md (fetchable read-only with `curl -s`).
  - spec citation: `plugins/arch-compliance/hooks/hooks.json:2`
- **C48** [implementability] [load-bearing]: In auto mode a hook's 'ask' goes to the person's prompt and is not decided by the classifier, and an explicit permissions.ask rule prompts in every mode including bypassPermissions. Edit(...) rules apply to all built-in file-editing tools. External: https://code.claude.com/docs/en/hooks.md, https://code.claude.com/docs/en/permission-modes.md, https://code.claude.com/docs/en/permissions.md (fetchable read-only with `curl -s`).
  - spec citation: `None`
- **C49** [implementability] [load-bearing]: Claude Code sets CLAUDE_CODE_CHILD_SESSION=1 in the environment of the Bash and PowerShell subprocesses it starts. External: https://code.claude.com/docs/en/env-vars.md; also observable read-only from a Bash tool's own environment.
  - spec citation: `None`
- **C50** [implementability]: A test can pin the hook's imports by walking approval_prompt.py's AST and asserting each imported module is acf.repo or has a top-level name in sys.stdlib_module_names (Python 3.10+; pyproject requires 3.11), modelled on test_repo_module_imports_only_stdlib (test_repo_paths.py:74-78); any other acf module fails it. The poisoned-module subprocess test (test_repo_paths.py:81-108) can also run approval_prompt.py with a Bash acf-allow payload and expect ask.
  - spec citation: `plugins/arch-compliance/tests/test_repo_paths.py:74-78`
- **C51** [implementability]: conftest.py's autouse _isolated_home (:10-17) can also delete CLAUDE_CODE_CHILD_SESSION through monkeypatch, so a suite started from Claude Code does not trip Decision 5. tmp_path lies outside any git repository on the test machine, so the §6.1 'plain directory' test can self-check that with git exit 128.
  - spec citation: `plugins/arch-compliance/tests/conftest.py:10-17`
- **C52** [implementability]: The hook's narrowed shell needles (acf-allow, acf.cli_allow, approvals.json) do not match `pytest plugins/arch-compliance/tests/test_cli_allow.py` or `git add plugins/arch-compliance/python/acf/cli_allow.py`, while matching `python -m acf.cli_allow` and `acf-allow --fingerprint <hex>`.
  - spec citation: `None`
- **C53** [implementability]: In bypassPermissions mode the hook's JSON permissionDecision 'deny' stops the call. Basis: in Claude Code 2.1.330's bundled source (hook_deny_source_probe.out, build SHA-256 at :2), an exit-2 hook becomes {behavior:'deny', decisionReason:{type:'hook'}} (:5) and a JSON deny becomes the same shape (:8); the resolver handles that deny in its first hook branch, ahead of the hook-allow branch that reads the permission mode, and each return there is the deny or the deny passed through the mod and policy checks (:11, :14). The documentation states an exit-2 hook stops the call before permission rules are evaluated (external, permissions.md). The live check is §8 item 4 (bypass_hook_probe.py).
  - spec citation: `docs/design/evidence/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT/hook_deny_source_probe.out:5`
- **C54** [implementability] [load-bearing]: STORE_REL can move from acf.approval (approval.py:36-37) to acf.repo with no new import there (pathlib.Path is already imported at repo.py:13); acf.approval imports it for store_path (approval.py:68); test_approval.py:12 imports it from acf.repo with :85 unchanged. approval_prompt.py can import acf.repo after putting plugins/arch-compliance/python on sys.path as posttooluse_gate.py:38-43 does, and acf.repo's contract keeps that import standard-library only (repo.py:3-6).
  - spec citation: `plugins/arch-compliance/python/acf/repo.py:13`
- **C55** [implementability]: A test can pin the ask rules and the needles together: acf-setup/SKILL.md has no backticked Bash(...), PowerShell(...) or Edit(...) token today, so once /acf-setup's prose carries the Decision 7 rules, each token found is a rule; the test asserts each shell rule contains a needle, each Edit rule's glob matches ~/.acf/ joined with STORE_REL.name under fnmatch, and each needle is covered by some rule.
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:24`
- **C56** [mechanism_justification]: Departing from #62's acceptance wording (an edit in any worktree makes every worktree STALE) is justified: under the fingerprint an unedited worktree still runs exactly the approved bytes, so marking it STALE would ask for an approval that adds no review; once the edit is approved, every worktree still on the old bytes turns STALE.
  - spec citation: `None`
