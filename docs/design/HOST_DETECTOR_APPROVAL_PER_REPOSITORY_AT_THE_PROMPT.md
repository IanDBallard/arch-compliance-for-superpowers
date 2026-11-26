# Host Detector Approval per Repository, Given at the Permission Prompt

**Status:** Draft (v1)
**Adversarial review:** not yet run
**Date:** 2026-11-26
**Spec kinds:** `feature`
**Repo:** `IanDBallard/arch-compliance-for-superpowers`, `main` at `58ed65c` (release 0.3.4), branch `feat/approval-by-repository`.
**Issues:** #62 (approvals keyed by worktree root, so each worktree of one repository needs its own `acf-allow`).
**Supersedes:** in `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md`: Decision 2's key (`:68`, *"keyed by `RepoTree(repo).root.as_posix()`"*); Decision 6's channel (`:72`, *"One approval command, `acf-allow`, run by a person"* and *"skill prose tells the agent never to run `acf-allow`"*); and the residual *"One approval per checkout directory"* (`:90`). Every other decision of that spec stands, the fingerprint (Decision 3) and source-only loading (Decision 4) above all.
**Governing mandates:** `config/architecture/ARCHITECTURE.md` sections `## Fail loud` (`:26-43`), `## No shims` (`:45-55`), `## POSIX paths` (`:57-66`), `## One owner for host paths` (`:115-138`), `## Host detectors and call sites` (`:140-188`, the trust boundary at `:179-186`), `## Declared, never defaulted` (`:190-228`), `## Prose names no host` (`:230-240`), `## Live consumers` (`:250-254`), `## No completeness claims` (`:256-266`), `## Declared text decoding` (`:268-279`), `## Release discipline` (`:281-293`), `## Single point of definition` (`:295-317`).
**No state-machine surface.** The design adds or modifies no state machine and no transition; `ApprovalState` keeps its five members.

---

## 0. Citation convention

Unprefixed paths are this repository at `58ed65c`. Paths prefixed `cy:` are the sibling repository `IanDBallard/Cayenne` (`main`), where #62 was observed; no step of this change reads or writes them, and the facts used are quoted beside each citation. Claims resting on the Claude Code documentation are marked *(external)* with the page: permissions `https://code.claude.com/docs/en/permissions.md`, permission modes `https://code.claude.com/docs/en/permission-modes.md`, hooks `https://code.claude.com/docs/en/hooks.md`, environment variables `https://code.claude.com/docs/en/env-vars.md`. Where those pages are silent, the claim is marked *(unverified)* and §8 tests it.

---

## 1. Problem

### 1.1 One approval per worktree (#62)

`check_approval` looks the repository up by its resolved root (`plugins/arch-compliance/python/acf/approval.py:135`, `read_store(store).repos.get(RepoTree(repo).root.as_posix())`) and `write_approval` writes that key (`:167`). Every git worktree has its own root, so a new worktree of an approved repository is `MISSING` even when its host rows and detector files are byte-identical to the approved ones. The cleared spec says so on purpose: *"The key is the resolved root, so each clone and each git worktree needs its own `acf-allow`"* (`docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:90`), and `/acf-setup` repeats it (`plugins/arch-compliance/skills/acf-setup/SKILL.md:24`).

Observed 2026-11-25/26 (#62): three agent sessions in three worktrees of `cy:` were each refused by the pre-push diff gate (*"acf: host detectors need approval: no approval for this repository"*) after their test suites passed. The one detector file (`cy:config/architecture/detectors/eslint_rules.py`) was unchanged and already approved in the main checkout.

### 1.2 Approval is possible only at a terminal the user sits at

Decision 6 of the cleared spec has the user run `acf-allow` themselves, and every gate message tells the agent not to: the diff gate's refusal (`approval.py:149-154`, *"Ask the user to review the detector files and run acf-allow"*), the hook's notice (`plugins/arch-compliance/hooks/posttooluse_gate.py:150-155`, *"… run acf-allow in this repository; do not run it yourself"*), `/acf-setup` (`SKILL.md:24`, `:288`) and `/acf-mandate` (`plugins/arch-compliance/skills/acf-mandate/SKILL.md:139`). A user following a session over Remote Control cannot run a command: in #62 the owner reports that Remote Control's `!` prefix does not execute, so each refusal waited until the owner was back at the machine.

**Root cause, both halves.** The approval binds code (the fingerprint, which is sound) to two things that are not about the code: the folder the checkout happens to live in, and the device the person happens to be at. Neither adds review; both add waiting.

---

## 2. Approaches considered

| Approach | What it trades | Outcome |
| --- | --- | --- |
| **A. Key by the git common directory; approve through Claude Code's permission prompt, behind a plugin hook.** | Works from any device the session reaches. Not a hard wall against an agent determined to approve itself (§3), which the cleared design is not either. | **Chosen** by the user, 2026-11-26. |
| B. Approve through GitHub: `acf-allow` posts the fingerprint to an issue and records the approval when the owner answers there. | Agents run `gh` with the user's credentials, so an agent could post the owner's answer. Needs the network. | Rejected. |
| C. Key by the git common directory only; approval stays at the terminal. | Would have avoided every refusal in #62 (nothing had changed), but a real detector change while the user is away still waits. | Rejected as incomplete; it is the first half of A. |
| D. The agent judges the risk and approves. | Restores the cleared spec's §1.1: an agent, possibly following injected text, gets its own code run. | Rejected. |

---

## 3. Decisions

1. **The store key is the repository, not the folder.** The key is the absolute POSIX path git prints for `git rev-parse --path-format=absolute --git-common-dir` run in the repository, which every worktree of one repository shares, joined with `::` to the host root's path inside its worktree (`--show-prefix`, empty at the top level). The prefix keeps two hosts in one git repository (a monorepo package with its own `config/architecture/mandates.yml`, or a folder inside a dotfiles repository) on separate entries, so approving one never makes the other `STALE`; the same subfolder in two worktrees shares one entry. When that command does not exit `0` or git cannot be started, the key is `RepoTree(repo).root.as_posix()` as today, and the scope is *"this folder only"*. The fingerprint is unchanged, so an approval covers a worktree exactly when that worktree's active host rows and detector files match what was approved; a change in any worktree makes every worktree whose bytes differ `STALE`.
2. **Old entries are not migrated.** An entry written under a worktree root before this change is never read again for a git repository (its key is no longer computed) and still matches for a non-git folder (whose key is unchanged). Each user approves each git repository once after upgrading. Reading old root keys as a fallback would be the compatibility shim `## No shims` forbids (`ARCHITECTURE.md:53-55`, *"compatibility shims … are forbidden"*); old entries are inert data, and the README's upgrade note says they can be deleted.
3. **An agent may start `acf-allow`, and only the user's answer at a Claude Code permission prompt lets it run.** The agent prepares a review (Decision 6), then runs `acf-allow --fingerprint <hex>`. The approval is the user's Allow at the prompt; their Deny ends it. *(external, permissions.md: "A message from an agent doesn't count as your approval for a pending permission prompt"; background subagents' prompts surface in the main session.)*
4. **The plugin forces that prompt with a PreToolUse hook that fails closed.** `plugins/arch-compliance/hooks/approval_prompt.py` (§5.4) returns `ask` for any shell command that mentions approval and for any file tool aimed at the store, and `deny` for the same calls in `bypassPermissions` mode. It is registered with `"onFailure": "block"` so a crash, a timeout or a missing interpreter blocks the call instead of letting it through. *(external, hooks.md: a failing hook is a non-blocking error unless `"onFailure": "block"` is set, Claude Code v2.1.295 or later; a hook's `ask` reason is "shown to the user in the permission prompt"; `permission_mode` is a common input field.)* The hook runs in every repository whatever `.acf/enabled` says, because the store it guards is per user.
5. **`acf-allow` binds the user's Allow to the reviewed fingerprint.** `--fingerprint HEX` makes `acf-allow` refuse, writing nothing, unless the repository's current fingerprint equals `HEX`, so the bytes approved are the bytes the agent showed. When Claude Code started the process (`CLAUDE_CODE_CHILD_SESSION` is `1`; *external, env-vars.md*: set only by Claude Code for its Bash, PowerShell, Monitor, hook and status-line subprocesses), `acf-allow` without `--fingerprint` is refused. A person at their own terminal runs `acf-allow` as today.
6. **A read-only status command gives the agent what to review.** `acf-approval-status` prints the key and its scope, the state, the rows, the files with their SHA-256, the fingerprint and the imported-helper limit, and writes nothing. Its name avoids every string the hook matches (§5.4), so running it never prompts. A new skill, `acf-approve`, is the procedure the gate messages point at.
7. **A documented permission rule backs the hook in bypass mode.** `/acf-setup` offers to add `permissions.ask` rules to the user's `~/.claude/settings.json`, with the user's consent: `Bash(acf-allow:*)`, `Bash(python -m acf.cli_allow:*)`, `PowerShell(acf-allow:*)`, `PowerShell(python -m acf.cli_allow:*)`, `Write(~/.acf/**)` and `Edit(~/.acf/**)`. *(external, permissions.md: ask rules apply when any subcommand of a compound command matches; a rule does not match the same program started another way, which the hook's text match covers.)* *(external, permission-modes.md: tools matched by an explicit ask rule are not auto-approved "in any mode, including bypassPermissions".)* The hook's `deny` in bypass mode is *(unverified)*; the rule is the documented guarantee there.

---

## 4. Non-goals and residual exposure

- **Not a wall against a determined agent.** The hook matches text. A script the agent writes that imports `acf.approval.write_approval`, a command that builds the string `acf-allow` at run time, or a tool the hook does not match passes it. The cleared spec already accepts the same exposure: *"Whoever can write the user's home directory, or run `acf-allow`, can approve. Claude Code's tool permissions govern an agent doing either"* (`HOST_DETECTOR_LOCAL_APPROVAL.md:84`). This design makes the honest path work remotely and the naive path prompt; it does not make the dishonest path impossible.
- **Imported helpers and executed tools stay outside the fingerprint** (`HOST_DETECTOR_LOCAL_APPROVAL.md:83`). Per-folder keying never covered them either: `git checkout` of another branch in an approved folder runs that branch's helpers under the existing approval. One example in `cy:`: `cy:config/architecture/detectors/eslint_rules.py:58-60` runs `node` on the repository's ESLint with the repository's configuration, none of it fingerprinted. `acf-approval-status` and `acf-allow` keep printing the limit; `acf-approve` has the agent say what each detector executes.
- **The user reviews the agent's summary, not the code.** On a phone the review is the agent's text plus the fingerprint. The skill makes the summary concrete (§5.6); the user can still Deny and approve later at a terminal.
- **A user who wants no remote approval** sets a `permissions.deny` rule for `acf-allow`; out of scope to automate.
- **No team-wide or committed approval** (`HOST_DETECTOR_LOCAL_APPROVAL.md:93`).
- **The git runner's decoding debt** (`ARCHITECTURE.md:274-276`, `acf/diff.py:24-30` reads git output with the locale codec) applies to the key: a non-ASCII path may decode wrongly, but it decodes the same way at approval and at check, so it can only cause a `MISSING`, never a false `APPROVED`. The fix stays with spec `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` §9 follow-up 1.

---

## 5. Design

### 5.1 The repository key

**`acf.diff.git_common_dir(repo: Path) -> tuple[Path, str] | None`** (new, beside `run_git` at `plugins/arch-compliance/python/acf/diff.py:17`, the one git runner the doctrine names for runtime code). It runs `run_git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir", "--show-prefix")`, which prints two lines; returns `(Path(line1), line2)` (the prefix with its trailing `/` removed, empty at the top level) when the exit code is `0` and the first line is non-empty; returns `None` on any other exit code or when `subprocess` raises `OSError` (git not installed). `--path-format` needs git 2.31; an older git exits non-zero and the folder key applies, which §5.3 reports.

**`acf.approval.repo_key(repo: Path) -> RepoKey`** (new). `RepoKey` is a frozen dataclass `(key: str, scope: Literal["repository", "folder"])`: `(f"{common.as_posix()}::{prefix}", "repository")` when `git_common_dir(repo)` returns `(common, prefix)`, else `(RepoTree(repo).root.as_posix(), "folder")`. A folder key could equal a repository key only for a POSIX folder literally named `<common dir>::<prefix>`; even then the fingerprint still decides, so the collision can cause a `STALE`, never a false `APPROVED` for different bytes. `check_approval` (`approval.py:135`) and `write_approval` (`:167`) use `repo_key(repo).key` in place of `RepoTree(repo).root.as_posix()`. Git computes the path; `approval.py` joins and resolves nothing, so `test_repo_tree_guard.py` needs no allowlist entry.

The fallback to the folder key is recorded in `## Declared, never defaulted` (§5.7): it is not a host declaration, it keeps an approval per folder exactly as before, and `acf-allow` and `acf-approval-status` print the scope, so it is visible rather than silent.

### 5.2 `acf-approval-status` (new console script, `plugins/arch-compliance/python/acf/cli_approval_status.py`)

`pyproject.toml:18-21` gains `acf-approval-status = "acf.cli_approval_status:main"`. Arguments: `--repo PATH`. Loads the registry with `load_gate_registry` as `acf-allow` does (`cli_allow.py:50`). Prints, in order: `repository: <key> (<scope>)` where the scope reads `every worktree of this repository` or `this folder only`; `state: <state name>` from `check_approval(repo, registry, TIER1_CALL_SITES)`; per row `id` and `detector`; per file its path and SHA-256 from `file_digests`; `fingerprint: <hex>` from `fingerprint(rows, digests)`; the imported-helper limit (`cli_allow.py:27-30`, moved to `acf.approval.HELPER_LIMIT` so both scripts print one text). No host rows: prints that, exits `0`. `AcfInputError` or `UnknownDetectorError`: stderr, exit `1`. It writes nothing.

### 5.3 `acf-allow` (`plugins/arch-compliance/python/acf/cli_allow.py`)

1. New argument `--fingerprint HEX`. After `digests = file_digests(repo, rows)` (`:58`), when given and `HEX != fingerprint(rows, digests)`: stderr `acf: the host rows or detector files changed since the review (reviewed <HEX>, now <current>); nothing approved`, exit `1`, store untouched.
2. When `os.environ.get("CLAUDE_CODE_CHILD_SESSION") == "1"` and `--fingerprint` is absent (and `--revoke` is absent): stderr `acf: run from Claude Code, acf-allow needs --fingerprint: run acf-approval-status and pass the fingerprint it prints, or run acf-allow in a terminal outside Claude Code`, exit `1`. This also applies when the user types `! acf-allow` in a local session, if Claude Code sets the variable for `!` commands *(unverified)*; the message tells them the two ways through, and the README upgrade note says so.
3. The closing line (`:67`) becomes `Approved <key> (<scope>) in <store>.` with the scope text of §5.2; `_revoke` (`:74-83`) uses `repo_key(repo).key`.
4. The module docstring (`:1-5`, *"Run by the user, never by an agent"*) states Decision 3: an agent may start it, the user's permission-prompt answer approves.

### 5.4 The approval hook (`plugins/arch-compliance/hooks/approval_prompt.py`, new)

Registered in `plugins/arch-compliance/hooks/hooks.json` under a new `PreToolUse` key: matcher `Bash|PowerShell|Write|Edit|MultiEdit|NotebookEdit`, command `python "${CLAUDE_PLUGIN_ROOT}/hooks/approval_prompt.py"`, `"timeout": 10`, `"onFailure": "block"`. *(external, tools-reference: `PowerShell` is a tool name; permissions.md calls `MultiEdit` legacy, so listing it is harmless if it never matches.)*

Standard library only, and no `acf` import, so it costs one interpreter start and cannot fail on a missing dependency. Behaviour:

1. Read stdin as bytes. If none of the needles occurs in the raw bytes, exit `0` at once. This is the common path.
2. Parse the JSON. For `Bash` and `PowerShell`, the subject is `tool_input.command`; for `Write`, `Edit`, `MultiEdit` and `NotebookEdit`, the subject is `tool_input.file_path` or `tool_input.notebook_path`. File content is never a subject, so editing a document that mentions `acf-allow` does not prompt.
3. Needles, case-insensitive. A shell command matches on any of `acf-allow`, `cli_allow`, `write_approval`, `approvals.json`; a file tool's path matches on `approvals.json` only, so editing `cli_allow.py` or its tests does not prompt. `approvals.json` equals `acf.approval.STORE_REL.name`; a test pins the two (§6.3), since the hook does not import `acf`.
4. Subject matches and `permission_mode` is `bypassPermissions`: print `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "ACF approval needs your answer at a permission prompt, which bypass mode skips. Leave bypass mode, or run acf-allow in your own terminal."}}`, exit `0`.
5. Subject matches otherwise: the same shape with `"ask"` and the reason `ACF approval: allowing this approves the host detector code the agent just summarized, for every worktree of this repository whose files match. Deny if you have not read the summary.`
6. No match: exit `0`.
7. Any exception after step 1 found a needle: print `acf: approval hook failed: <type>: <message>` to stderr and exit `2`, which blocks the call. *(external, hooks.md: exit 2 blocks the tool call.)* The handler carries the `fail-loud.bare-except-ok` token with that reason.

Other modes. In `auto` mode a hook's `ask` goes to the person's prompt and the classifier does not decide it *(external, hooks.md)*, and explicit ask rules still prompt *(external, permission-modes.md)*; so the agent cannot approve itself through the classifier. `dontAsk` mode turns `ask` into a denial, and a non-interactive `-p` run denies calls that need approval *(external, permission-modes.md)*; both are the intended outcome. `default`, `acceptEdits` and `plan` are covered by the ask-rule statement for "any mode" *(external, permission-modes.md)*; that a hook's `ask` prompts in `acceptEdits` for a file tool is *(unverified)*, so Decision 7's rules include the store path for the file tools, and §8 item 4 tests it.

### 5.5 Gate messages

- `require_approval` (`approval.py:149-154`): `host detectors need approval: <reason>; rows: <ids>. Ask the user to approve them: follow the acf-approve skill (acf-approval-status, a review for the user, then acf-allow --fingerprint at a permission prompt the user answers). A CI workflow, or a run with --mandates naming another file, passes --trusted-checkout.`
- The hook's notice (`posttooluse_gate.py:150-155`): `acf: host detectors not run: <reason>; rows skipped: <ids>. To have them run, follow the acf-approve skill; the user approves at a permission prompt. Never approve another way.`

Both name no host (`ARCHITECTURE.md:232-233`).

### 5.6 The `acf-approve` skill (`plugins/arch-compliance/skills/acf-approve/SKILL.md`, new)

Description: use when a gate reports that host detectors need approval, when a host row or detector file changed, or when running `/acf-approve`. Procedure:

1. Run `acf-approval-status`. If the state is `APPROVED` or `NOT_NEEDED`, stop. If it is `STORE_IN_REPO`, tell the user and stop.
2. For each detector file: what changed (`git log -n 5 --format="%h %an %ad %s" -- <file>` and `git diff <default branch>... -- <file>`; for a first approval, the whole file); what it executes (subprocesses, network, writes outside the repository); which repository modules it imports, which the approval does not cover.
3. Post one message to the user: the repository and its scope, each file's path, SHA-256 and changes, the execution summary, the helper limit and the fingerprint. Say whether anything looks like more than a detector.
4. Run `acf-allow --fingerprint <hex>` once. The user answers the prompt.
5. Denied, refused or blocked: stop; do not retry, rephrase the command, edit `~/.acf/`, write a script that approves, add `--trusted-checkout`, or ask another session to approve. Tell the user they can approve later at their terminal.

### 5.7 Doctrine and prose

| File | Change |
| --- | --- |
| `config/architecture/ARCHITECTURE.md:179-186` (`**Trust boundary.**`) | The approval is keyed by the repository's git common directory (the folder for a non-git directory), so it covers every worktree whose host rows and files match. An agent may start `acf-allow --fingerprint`; the plugin's PreToolUse hook makes it prompt, and the user's answer is the approval. The closing line (`:188`) gains `test_approval_prompt.py` and `test_cli_approval_status.py`. |
| `config/architecture/ARCHITECTURE.md:213-228` (`## Declared, never defaulted`, the recorded defaults) | Add: the approval key falls back to the folder when git cannot report a common directory (`acf.approval.repo_key`), and says so in `acf-allow` and `acf-approval-status`. |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md:24` | Replace the sub-bullet: when `mandates.yml` has host rows, follow `acf-approve`; one approval covers every worktree of the repository; offer the user the `permissions.ask` rules of Decision 7 for `~/.claude/settings.json` and add them only on their yes. |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md:185`, `:187`, `:206`, `:262`, `:288` | "each person's `acf-allow`" becomes "each person's approval (`acf-approve`)"; `:288` drops "Do not run `acf-allow` … yourself" for "approve only through `acf-approve`; never add `--trusted-checkout`". |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md:189-198` (hook table) | A `PreToolUse` row for `approval_prompt.py`. |
| `plugins/arch-compliance/skills/acf-mandate/SKILL.md:139` | The re-run needs a new approval (`acf-approve`) after a host row or detector file changes; never add `--trusted-checkout`. |
| `README.md:26-35` (skills table), `:64`, `:105-112` (hooks), and a new upgrade note `### Upgrading to repository-wide, prompt-given approval (v0.3.5)` before `:114` | The key, the prompt channel, `acf-approval-status`, the hook and its `onFailure` minimum Claude Code version, one re-approval per repository after upgrading, old entries deletable. `:143`'s *"One approval per checkout directory"* sentence is historical and stays under its v0.2.5 heading. |
| `docs/guides/SUPERPOWERS_COMPLEMENT.md:89` | The same facts in one sentence. |
| `plugins/arch-compliance/hooks/hooks.json:2` (`description`) | Adds the PreToolUse approval prompt. |
| `pyproject.toml:3`, `plugins/arch-compliance/.claude-plugin/plugin.json:3` | `0.3.4` → `0.3.5` (`ARCHITECTURE.md:283-284`). |

---

## 6. Tests

Subprocess tests set `HOME` and `USERPROFILE` under `tmp_path` and clear `CLAUDE_CODE_CHILD_SESSION` unless the test sets it; in-process tests monkeypatch `Path.home` and the environment. No test touches the real store.

### 6.1 `test_approval.py` and a new `test_diff.py` case

- `git_common_dir`: in a `git init` repository it equals `<repo>/.git`; in a `git worktree add` of it, the same path; in a plain directory `None`; with `run_git` patched to raise `FileNotFoundError`, `None`.
- `repo_key`: scope `repository` in a repository and its worktree with equal keys; two subfolder hosts `a/` and `b/` of one repository get different keys, and `a/` in the main checkout and in a worktree get one key; scope `folder` and the resolved root in a plain directory.
- Two subfolder hosts of one repository: approving `a/` leaves `b/`'s state unchanged.
- Approve in the main checkout; the worktree is `APPROVED` with no further write. Edit a detector file in the worktree: the worktree is `STALE`, the main checkout stays `APPROVED`. Approve in the worktree after the edit; the main checkout (old bytes) is now `STALE`.
- Two separate `git init` repositories with identical files: approving one leaves the other `MISSING`.
- A store holding only a root-keyed entry for a git repository's checkout: `MISSING` (Decision 2). The same for a plain directory: `APPROVED`.
- The existing tests use `tmp_path` directories. Where `tmp_path` is not inside a git repository they exercise the folder key; where it is, each gets a distinct `repository` key from its prefix. Either way their outcomes do not change, since they compare check and write in the same directory.

### 6.2 `test_cli_allow.py` and `test_cli_approval_status.py` (new)

- `--fingerprint` equal to the current one: writes, exits `0`, prints the scope. Different: exit `1`, message names both values, store byte-identical.
- `CLAUDE_CODE_CHILD_SESSION=1` without `--fingerprint`: exit `1`, store untouched; with it: writes. `--revoke` under the variable works without `--fingerprint`.
- `acf-approval-status`: prints key, scope, state, rows, digests, the fingerprint `acf-allow --fingerprint` accepts, and `HELPER_LIMIT`; store unchanged (absent before, absent after); no host rows: exit `0`; missing detector file: exit `1`.

### 6.3 `test_approval_prompt.py` (new, subprocess runs of the hook)

- `Bash` with `acf-allow --fingerprint abc`: `ask` with the reason; same in `PowerShell`; `python -m acf.cli_allow`: `ask`; `cd x && ACF-ALLOW`: `ask`.
- `bypassPermissions` with `acf-allow`: `deny`.
- `Write` with `file_path` `<home>/.acf/approvals.json`: `ask`. `Write` whose content mentions `acf-allow` and whose path is `docs/x.md`: exit `0`, no output.
- `Bash` `acf-approval-status`: exit `0`, no output. `Bash` `ls`: exit `0`, no output.
- Malformed JSON containing `acf-allow`: exit `2`, stderr `acf: approval hook failed`. Malformed JSON without a needle: exit `0`.
- The needle `approvals.json` equals `acf.approval.STORE_REL.name`.
- `hooks.json` registers the hook under `PreToolUse` with `onFailure` `block` and the matcher of §5.4.
- The hook imports nothing outside the standard library (the AST check `test_repo_paths.py:81-108` uses, applied to the new file).

### 6.4 `test_hooks.py`, `test_diff_cli.py`

The tests that assert the notice or refusal text (`test_hooks.py` unapproved and stale cases; `test_diff_cli.py` no-approval refusal) assert `acf-approve` where they asserted `acf-allow`. The diff-gate refusal still names `--trusted-checkout`.

### 6.5 Guards that must keep passing

`test_repo_tree_guard.py` (no new allowlist entry), `test_repo_paths.py:81-108`, `test_adr_skill_prose.py` (the new skill is outside its list; its prose names no host by review).

---

## 7. Risks

| Risk | Mitigation |
| --- | --- |
| Claude Code older than v2.1.295 ignores `onFailure`, so a failing hook lets the call through. | The README note gives the minimum version; Decision 7's permission rule still prompts; `acf-allow` still needs `--fingerprint` when Claude starts it. |
| With `onFailure: "block"`, a broken hook or a missing `python` blocks every `Bash`, `PowerShell` and file-tool call in every repository. | The hook's common path is one byte scan; its tests run it; the plugin already needs `python` on PATH for its other hooks (`hooks.json:2`). The failure is loud, not silent, and uninstalling the plugin clears it. |
| Read-only commands that mention a needle (`grep -n acf-allow README.md`) prompt. | Accepted: the reason says what allowing does, and in a host that is rare. In this repository it is common while editing approval prose. |
| Every user must approve each git repository once after upgrading. | One prompt per repository; the README note says so. |
| The hook's `deny` in bypass mode is *(unverified)*. | §8 item 4 tests it; Decision 7's rule is the documented guarantee. |
| Remote Control's handling of a hook-raised `ask` prompt is *(unverified)*. | §8 item 3 tests it; if it fails, the design still delivers #62 and the terminal path. |

---

## 8. Acceptance

1. All tests pass, including §6.
2. In a scratch git repository with `.acf/enabled` and a host row: `acf-allow` in the main checkout; a `git worktree add` folder is `APPROVED` per `acf-approval-status` and its pre-push `acf-check-diff --call-site precommit` runs the host row; editing the detector file in the worktree makes it `STALE`.
3. From a Remote Control session on that repository, the agent follows `acf-approve`; the permission prompt appears on the remote device with the hook's reason; Allow records the approval; on a second run, Deny records nothing.
4. In `bypassPermissions` mode, the agent's `acf-allow --fingerprint` is denied with the hook's reason. In `auto` mode it prompts and is not decided by the classifier. In `acceptEdits` mode, an agent `Write` to `~/.acf/approvals.json` prompts.
5. With the hook script temporarily renamed, a `Bash` call is blocked (`onFailure`), not run.
6. The diff gate on this branch (`PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main --call-site ci`) exits `0`.
7. `pyproject.toml:3` and `plugins/arch-compliance/.claude-plugin/plugin.json:3` read `"0.3.5"`.

## 9. Left to the builder

Test file layout beyond the names above; the exact wording of `acf-approve` around the fixed steps of §5.6; whether `RepoKey` lives in `approval.py` or beside `git_common_dir`, as long as `approval.py` stays its one consumer.
