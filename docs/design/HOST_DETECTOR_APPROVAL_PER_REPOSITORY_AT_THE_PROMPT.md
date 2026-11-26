# Host Detector Approval per Repository, Given at the Permission Prompt

**Status:** Draft (v2)
**Adversarial review:** in progress
**Date:** 2026-11-26
**Spec kinds:** `feature`
**Repo:** `IanDBallard/arch-compliance-for-superpowers`, `main` at `58ed65c` (release 0.3.4), branch `feat/approval-by-repository`.
**Issues:** #62 (approvals keyed by worktree root, so each worktree of one repository needs its own `acf-allow`).
**Supersedes:**
- In `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md`:
  - Decision 2's key (`:68`, *"keyed by `RepoTree(repo).root.as_posix()`"*).
  - Decision 6's channel (`:72`, *"One approval command, `acf-allow`, run by a person"* and *"skill prose tells the agent never to run `acf-allow`"*).
  - The second clause of the residual at `:84` (*"skill prose and every gate message tell the agent to leave approval to the user (Decision 6)"*); its first clause stands and §4 quotes it.
  - The hook notice text at `:156`.
  - The residual *"One approval per checkout directory"* (`:90`).
  - Every other decision of that spec stands, above all the fingerprint (Decision 3) and source-only loading (Decision 4).
- In `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md`, item 11's statement that the plugin's hooks *"no-op without `.acf/enabled`"* (`:162-164`): it stays true for the two existing hooks. The new approval hook (Decision 4) runs whatever `.acf/enabled` says.

**Governing mandates:** `config/architecture/ARCHITECTURE.md` sections `## Fail loud` (`:26-43`), `## No shims` (`:45-55`), `## POSIX paths` (`:57-66`), `## One owner for host paths` (`:115-138`), `## Host detectors and call sites` (`:140-188`, the trust boundary at `:179-186`), `## Declared, never defaulted` (`:190-228`), `## Prose names no host` (`:230-240`), `## Live consumers` (`:250-254`), `## No completeness claims` (`:256-266`), `## Declared text decoding` (`:268-279`), `## Release discipline` (`:281-293`), `## Single point of definition` (`:295-317`).
**No state-machine surface.** The design adds or modifies no state machine and no transition; `ApprovalState` keeps its five members.

---

## 0. Citation convention

Unprefixed paths are this repository at `753a42e`. Paths prefixed `cy:` are the sibling repository `IanDBallard/Cayenne` (`main`), where #62 was observed; no step of this change reads or writes them, and the facts used are quoted beside each citation.

Claims resting on the Claude Code documentation are marked *(external)* and name their page:
- permissions: `https://code.claude.com/docs/en/permissions.md`
- permission modes: `https://code.claude.com/docs/en/permission-modes.md`
- hooks: `https://code.claude.com/docs/en/hooks.md`
- environment variables: `https://code.claude.com/docs/en/env-vars.md`

Where those pages are silent, the claim is marked *(unverified)* and §8 tests it. Claims about git's behaviour that this design depends on are pinned by tests in §6.1 against the git on the test machine; the observations quoted in §1.3 were made with git 2.49.0.windows.1.

---

## 1. Problem

### 1.1 One approval per worktree (#62)

`check_approval` looks the repository up by its resolved root (`plugins/arch-compliance/python/acf/approval.py:135`, `read_store(store).repos.get(RepoTree(repo).root.as_posix())`), and `write_approval` writes that key (`:167`). Every git worktree has its own root. So a new worktree of an approved repository is `MISSING`, even when its host rows and detector files are byte-identical to the approved ones.

The cleared spec says so on purpose: *"The key is the resolved root, so each clone and each git worktree needs its own `acf-allow`"* (`docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md:90`). `/acf-setup` repeats it (`plugins/arch-compliance/skills/acf-setup/SKILL.md:24`).

Observed 2026-11-25/26 (#62): three agent sessions in three worktrees of `cy:` were each refused by the pre-push diff gate after their test suites passed. The refusal read *"acf: host detectors need approval: no approval for this repository"*. The one detector file (`cy:config/architecture/detectors/eslint_rules.py`) was unchanged and already approved in the main checkout.

### 1.2 Approval is meant to happen only at a terminal the user sits at

Decision 6 of the cleared spec has the user run `acf-allow` themselves, and these gate messages and skills tell the agent not to:
- the diff gate's refusal (`approval.py:149-154`, *"Ask the user to review the detector files and run acf-allow"*);
- the hook's notice (`plugins/arch-compliance/hooks/posttooluse_gate.py:150-155`, *"… run acf-allow in this repository; do not run it yourself"*);
- `/acf-setup` (`SKILL.md:24`, `:288`);
- `/acf-mandate` (`plugins/arch-compliance/skills/acf-mandate/SKILL.md:139`).

This is a convention in prose. `cli_allow.main` (`plugins/arch-compliance/python/acf/cli_allow.py:33-71`) checks nothing about its caller, so an agent that ignored the prose could run it today.

A user following a session over Remote Control cannot run a command. In #62 the owner reports that Remote Control's `!` prefix does not execute, so each refusal waited until the owner was back at the machine.

**Root cause, both halves.** The approval binds code (the fingerprint, which is sound) to two things that are not about the code: the folder the checkout happens to live in, and the device the person happens to be at. Neither adds review; both add waiting.

### 1.3 Facts about git this design rests on

Each was observed with the command shown, in a scratch directory, and is pinned by a §6.1 test.

| # | Fact | Observed |
| --- | --- | --- |
| G1 | `git rev-parse --path-format=absolute --git-common-dir --show-prefix` prints the common directory and the prefix on two lines. Both worktrees of one repository print the same common directory. | Main checkout `w` and linked worktree `wt`: both printed `…/gd/w/.git`. |
| G2 | Outside any repository, the command exits `128` and its stderr says *"not a git repository"*. | `fatal: not a git repository (or any of the parent directories): .git`, `exit=128`. |
| G3 | In a linked worktree's `pre-push` hook, git sets `GIT_DIR` to the worktree's git directory. With `GIT_DIR` set and `GIT_WORK_TREE` unset, `--show-prefix` in a subfolder prints an empty line, not the subfolder. | Hook env had `GIT_DIR=…/w/.git/worktrees/wt`. In `sub/`, the prefix line was empty. In the main checkout's `pre-push`, `GIT_DIR` was not set and `sub/` printed `sub/`. |
| G4 | Git for Windows prints a non-ASCII path in UTF-8. Decoding it with the Windows locale codec (cp1252) fails inside `subprocess`'s reader thread. `CompletedProcess.stdout` then comes back `None`, and the caller sees no exception. Decoding as UTF-8 gives the right path. | For directory `Á_dir` under `cp1252`: the reader thread printed `UnicodeDecodeError: 'charmap' codec can't decode byte 0x81`, and `stdout` was `None`. With `encoding="utf-8"`, stdout was `…/gd/\xc1_dir/.git`. |

G4 means `run_git` (`plugins/arch-compliance/python/acf/diff.py:24-30`, `text=True` with no `encoding`) can lose a path's output on Windows without raising. That is the declared debt at `ARCHITECTURE.md:274-276`. Any key built from its output would inherit the loss.

---

## 2. Approaches considered

| Approach | What it trades | Outcome |
| --- | --- | --- |
| **A. Key by the git common directory; approve through Claude Code's permission prompt, behind a plugin hook.** | Works from any device the session reaches. It is not a hard wall against an agent determined to approve itself (§4), and the cleared design is not one either. | **Chosen** by the user, 2026-11-26. |
| B. Approve through GitHub: `acf-allow` posts the fingerprint to an issue and records the approval when the owner answers there. | Agents run `gh` with the user's credentials, so an agent could post the owner's answer. Needs the network. | Rejected. |
| C. Key by the git common directory only; approval stays at the terminal. | Would have avoided every refusal in #62, since nothing had changed. A real detector change while the user is away still waits. | Rejected as incomplete; it is the first half of A. |
| D. The agent judges the risk and approves. | Brings back the cleared spec's §1.1 risk: an agent, possibly following injected text, gets its own code run. | Rejected. |

---

## 3. Decisions

1. **The store key is the repository, not the folder.**
   - The key is the common directory git prints (G1), joined with `::` to the host root's prefix inside its worktree (empty at the top level).
   - The prefix keeps two hosts in one git repository on separate entries, so approving one never makes the other `STALE`. Examples: a monorepo package with its own `config/architecture/mandates.yml`, or a folder inside a dotfiles repository. The same subfolder in two worktrees shares one entry.
   - Git is asked with its repository-locating environment variables removed, so a hook's inherited `GIT_DIR` cannot change the prefix (G3).
   - Only one git outcome gives the folder key `RepoTree(repo).root.as_posix()` (scope *"this folder only"*): exit `128` with *"not a git repository"* on stderr (G2). Every other failure raises `GitError` with git's own message and fails loud (§5.1). That covers git missing, git older than 2.31, a refused or dubious-ownership repository, and output that is not UTF-8.
   - The fingerprint is unchanged. An approval covers a worktree exactly when that worktree's active host rows and detector files match what was approved. Re-approving after a change makes every worktree whose bytes differ from the new approval `STALE`.
2. **Old entries are not migrated.**
   - An entry written under a worktree root before this change is never read again for a git repository, because its key is no longer computed. It still matches for a non-git folder, whose key is unchanged.
   - Each user approves each git repository once after upgrading.
   - Reading old root keys as a fallback would be the compatibility shim `## No shims` forbids (`ARCHITECTURE.md:53-55`, *"compatibility shims … are forbidden"*).
   - Old entries are inert data; the README's upgrade note says they can be deleted.
   - #62's own text proposed reading old keys as a migration; this design declines that for the reason above.
3. **An agent may start `acf-allow`, and only the user's answer at a Claude Code permission prompt lets it run.**
   - The agent prepares a review (Decision 6), then runs `acf-allow --fingerprint <hex>`.
   - The approval is the user's Allow at the prompt; their Deny ends it.
   - *(external, permissions.md: "A message from an agent doesn't count as your approval for a pending permission prompt"; background subagents' prompts surface in the main session.)*
4. **The plugin forces that prompt with a PreToolUse hook that fails closed.**
   - `plugins/arch-compliance/hooks/approval_prompt.py` (§5.4) returns `ask` for any shell command that mentions approval and for any file tool aimed at the store.
   - It is registered with `"onFailure": "block"`, so a crash, a timeout or a missing interpreter blocks the call instead of letting it through. *(external, hooks.md: a failing hook is a non-blocking error unless `"onFailure": "block"` is set, Claude Code v2.1.295 or later. A hook's `ask` reason is "shown to the user in the permission prompt". `permission_mode` is a common input field.)*
   - In `bypassPermissions` mode it returns `deny`. Whether Claude Code honours a PreToolUse `deny` in that mode is *(unverified)*. In bypass mode, only Decision 7's ask rule is documented to stop the call.
   - The hook runs in every repository whatever `.acf/enabled` says, because the store it guards is per user. An agent in a repository without the marker could otherwise approve another repository with `acf-allow --repo`.
   - On its common path it reads its input and exits `0` without importing anything beyond the standard library (§5.4 step 1). §5.7 updates every sentence listed there that says the plugin's hooks no-op without the marker.
5. **`acf-allow` binds the user's Allow to the reviewed fingerprint.**
   - `--fingerprint HEX` makes `acf-allow` refuse, writing nothing, unless the repository's current fingerprint equals `HEX`. So the bytes approved are the bytes the agent showed.
   - When Claude Code started the process, `acf-allow` without `--fingerprint` is refused. Claude Code is detected by `CLAUDE_CODE_CHILD_SESSION` being `1`. *(external, env-vars.md: set only by Claude Code for its Bash, PowerShell, Monitor, hook and status-line subprocesses.)*
   - A person at their own terminal runs `acf-allow` as today.
6. **A read-only status command gives the agent what to review.**
   - `acf-approval-status` prints the key and its scope, the state, the rows, the files with their SHA-256, the fingerprint and the imported-helper limit. It writes nothing.
   - Its name contains none of the hook's needles (§5.4 step 3), so running it never prompts.
   - `acf-allow` and `acf-approval-status` print the review through one function, `acf.approval.describe_approval` (§5.2).
   - A new skill, `acf-approve`, is the procedure the gate messages point at.
7. **A documented permission rule backs the hook.**
   - `/acf-setup` offers to add these `permissions.ask` rules to the user's `~/.claude/settings.json`, only with the user's consent: `Bash(acf-allow:*)`, `Bash(python -m acf.cli_allow:*)`, `PowerShell(acf-allow:*)`, `PowerShell(python -m acf.cli_allow:*)` and `Edit(~/.acf/**)`.
   - *(external, permissions.md: Edit rules apply to all built-in tools that edit files. Ask rules apply when any subcommand of a compound command matches. A rule does not match the same program started another way; the hook's text match covers that case.)*
   - *(external, permission-modes.md: tools matched by an explicit ask rule are not auto-approved "in any mode, including bypassPermissions".)*

---

## 4. Non-goals and residual exposure

- **Not a wall against a determined agent.**
  - The hook matches text. Three things pass it: a script the agent writes that imports `acf.approval.write_approval`, a command that builds the string `acf-allow` at run time, and a tool the hook does not match.
  - The first clause of the cleared spec's residual still holds and is accepted here: *"Whoever can write the user's home directory, or run `acf-allow`, can approve. Claude Code's tool permissions govern an agent doing either"* (`HOST_DETECTOR_LOCAL_APPROVAL.md:84`).
  - This design makes the honest path work remotely and the naive path prompt. It does not make the dishonest path impossible.
- **Imported helpers and executed tools stay outside the fingerprint** (`HOST_DETECTOR_LOCAL_APPROVAL.md:83`).
  - Per-folder keying never covered them either: `git checkout` of another branch in an approved folder runs that branch's helpers under the existing approval.
  - An example in `cy:`: `cy:config/architecture/detectors/eslint_rules.py:58-60` runs `node` on the repository's ESLint with the repository's configuration, none of it fingerprinted.
  - `describe_approval` keeps printing the limit, and `acf-approve` has the agent say what each detector executes.
- **One fingerprint per repository.** Two worktrees with different detector bytes cannot both be `APPROVED` at once. Approving one makes the other `STALE` until it is approved again. #62 asked for one approval per repository; this is the cost of one entry per repository.
- **The user reviews the agent's summary, not the code.** On a phone, the review is the agent's text plus the fingerprint. The skill makes the summary concrete (§5.6), and the user can still Deny and approve later at a terminal.
- **A user who wants no remote approval** sets a `permissions.deny` rule for `acf-allow`. Automating that is out of scope.
- **No team-wide or committed approval** (`HOST_DETECTOR_LOCAL_APPROVAL.md:93`).
- **Keys are compared as git prints them.** The design does not normalise case or drive letters. If git prints the common directory differently in two worktrees of one repository, they get two keys, and the second reads `MISSING` and asks for one more approval. That fails closed. §6.1 pins G1 for `git worktree add` with the path as given.
- **Git's inherited `GIT_DIR` and the existing diff calls.** G3 also applies to the diff gate's own `git diff` calls for a subfolder host run from a linked worktree's `pre-push` hook. This design strips the variables only for the key query (§5.1). The diff calls are unchanged and outside this spec; they are follow-up 1 in §9.

---

## 5. Design

### 5.1 The repository key

**`run_git` decodes UTF-8 and fails loud** (`plugins/arch-compliance/python/acf/diff.py:17-30`).
- It captures bytes and decodes them itself: stdout as UTF-8 in strict mode, stderr as UTF-8 with `errors="replace"`, since stderr is only diagnostic text.
- A stdout that is not UTF-8 raises `GitError` naming the command and the byte offset, on every platform. This replaces the silent `None` of G4.
- It gains a keyword-only `env: Mapping[str, str] | None = None`, passed to `subprocess.run`.
- Its return type stays `subprocess.CompletedProcess[str]`.
- This lands the `run_git` part of `## Declared text decoding`. §5.7 removes `run_git` from that section's declared debt and from its recipe's expected hits. The other two calls there, `adr/citations.py` `_git` and the TypeScript bridge, stay declared debt under `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` §9 follow-up 1.
- Every caller found by the recipe `grep -rn "run_git\|_git(" plugins/arch-compliance/python plugins/arch-compliance/hooks plugins/arch-compliance/skills scripts` gets UTF-8 instead of the locale codec. The call sites are `diff.py:35`, `:56`, `:68`, `acf/review/rollup.py:57`, `:78`, `:82`, `:90`, and the `architecture-review` skill's step 8 snippet (`plugins/arch-compliance/skills/architecture-review/SKILL.md:289`, `run_git(repo, "rev-parse", "HEAD")`). `adr/citations.py`'s hits are its own `_git`, not `run_git`.
- `git blame --porcelain` stdout carries the source line. So `rollup.provenance` (`acf/review/rollup.py:70-95`) can now get a `GitError` for a line that is not UTF-8. The roll-up is report-only (`acf/review/rollup.py:3`, *"Drift, staleness and provenance are report-only"*), so `provenance` catches `GitError` from its blame call and returns `("unresolved", <message>)`, its existing outcome for a git failure (`:86`, `:95`). The module docstring (`:4-5`, *"a missing ``git`` raises"*) adds that undecodable output raises `GitError`. CI runs on Linux with a UTF-8 locale, and the repository's Windows instruction already sets `PYTHONUTF8=1` (`CLAUDE.md`, *"Run the diff gate from the repository root with `PYTHONUTF8=1`"*). So those runs already decode UTF-8, and this makes the default match them.

**`acf.diff.git_common_dir(repo: Path) -> tuple[Path, str] | None`** (new, beside `run_git`).
1. Run `run_git(repo, "rev-parse", "--local-env-vars")`, which prints the names of git's repository-locating variables (`GIT_DIR`, `GIT_WORK_TREE`, `GIT_COMMON_DIR` and the rest), one per line. A non-zero exit raises `GitError` with git's stderr. Git owns that list; the plugin does not copy it.
2. Build `env` as `os.environ` without those names, with `LC_ALL=C` so git's messages are in English for step 4. Git 2.49 lists `GIT_CONFIG_PARAMETERS` and `GIT_CONFIG_COUNT` among them, so configuration passed through the environment does not reach this query either. A `safe.directory` given only that way then refuses, and the refusal fails loud by step 5. CI passes `--trusted-checkout` and computes no key.
3. Run `run_git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir", "--show-prefix", env=env)`.
4. Exit `0` with two lines: return `(Path(line1), line2.rstrip("/"))`. Exit `128` with `not a git repository` in stderr: return `None`.
5. Any other result raises `GitError("cannot compute the approval key for <repo>: git rev-parse failed: <stderr or exit code>")`. That covers another exit code, exit `0` without two lines, or an `OSError` from starting git (wrapped, `from exc`). `--path-format` needs git 2.31; an older git falls in this case and says so in its stderr.

**`acf.approval.repo_key(repo: Path) -> RepoKey`** (new).
- `RepoKey` is a frozen dataclass `(key: str, scope: Literal["repository", "folder"])`.
- When `git_common_dir(repo)` returns `(common, prefix)`, the result is `(f"{common.as_posix()}::{prefix}", "repository")`. When it returns `None`, the result is `(RepoTree(repo).root.as_posix(), "folder")`. A `GitError` propagates.
- A folder key could equal a repository key only for a POSIX folder literally named `<common dir>::<prefix>`. Even then the fingerprint still decides, so the collision can cause a `STALE`, never a false `APPROVED` for different bytes.
- `check_approval` (`approval.py:135`), `write_approval` (`:167`) and `cli_allow._revoke` (`cli_allow.py:76`) use `repo_key(repo).key` in place of `RepoTree(repo).root.as_posix()`.
- `check_approval` calls it only after its `NOT_NEEDED` return (`:128-129`), so a repository without host rows at the call sites runs no git for approval.
- Git computes the path; `approval.py` joins and resolves nothing, so `test_repo_tree_guard.py` needs no allowlist entry.

**Where a `GitError` from the key lands.** Each entry point that calls `check_approval`, `write_approval` or `repo_key` gets `GitError` in its existing handler. Recipe: `grep -rn "check_approval\|require_approval\|write_approval\|repo_key" plugins/arch-compliance/python plugins/arch-compliance/hooks --include=*.py`.

| Entry point | Handler today | Change |
| --- | --- | --- |
| `cli_check_diff.py:106` | Already catches `GitError`, prints `acf: <message>`, exits `1`. | None. |
| `posttooluse_gate.py:141-145` (`check_approval`) | Catches `AcfInputError` and `UnknownDetectorError`. | Add `GitError` to that tuple, so the message prints without a traceback and the hook exits `2`. |
| `cli_allow.py:68` | Catches `AcfInputError` and `UnknownDetectorError`. | Add `GitError`; exit `1`. |
| `cli_approval_status.py` (new) | Not present. | Catches the same three; exit `1`. |

The folder key for a non-git directory is recorded in `## Declared, never defaulted` (§5.7). It is not a host declaration: it applies only when git reports that the directory is not a repository, and it keeps one approval per folder as before. `describe_approval` prints the scope.

### 5.2 `describe_approval` and `acf-approval-status`

**`acf.approval.describe_approval(repo: Path, rows: list[Mandate], digests: Mapping[str, str]) -> list[str]`** (new). It returns the review lines, in order:
1. `repository: <key> (<scope>)`, where the scope reads `every worktree of this repository` or `this folder only`.
2. `Approving these host detector rows:` (`cli_allow.py:59`), then per row its `id` and `detector`.
3. `and these detector files (SHA-256):` (`cli_allow.py:62`), then per file its path and SHA-256.
4. `fingerprint: <hex>`.
5. The imported-helper limit (`cli_allow.py:27-30`, moved to `acf.approval.HELPER_LIMIT`).

`acf-allow` prints these lines in place of its own loop (`cli_allow.py:58-65`); `acf-approval-status` prints them after the state.

**`acf-approval-status`** (new console script, `plugins/arch-compliance/python/acf/cli_approval_status.py`).
- `pyproject.toml:18-21` gains `acf-approval-status = "acf.cli_approval_status:main"`.
- Arguments: `--repo PATH`. It loads the registry with `load_gate_registry`, as `acf-allow` does (`cli_allow.py:50`).
- It prints `state: <state name>` from `check_approval(repo, registry, TIER1_CALL_SITES)`, then the lines of `describe_approval`.
- No host rows: it prints that and exits `0`.
- `AcfInputError`, `UnknownDetectorError` or `GitError`: stderr, exit `1`.
- It writes nothing.

### 5.3 `acf-allow` (`plugins/arch-compliance/python/acf/cli_allow.py`)

1. **New argument `--fingerprint HEX`.** After `digests = file_digests(repo, rows)` (`:58`), when it is given and `HEX != fingerprint(rows, digests)`: stderr `acf: the host rows or detector files changed since the review (reviewed <HEX>, now <current>); nothing approved`, exit `1`, store untouched.
2. **Refusal under Claude Code.** When `os.environ.get("CLAUDE_CODE_CHILD_SESSION") == "1"` and neither `--fingerprint` nor `--revoke` is given: stderr `acf: run from Claude Code, acf-allow needs --fingerprint: run acf-approval-status and pass the fingerprint it prints, or run acf-allow in a terminal outside Claude Code`, exit `1`.
   - This also applies when the user types `! acf-allow` in a local session, if Claude Code sets the variable for `!` commands *(unverified)*.
   - The message tells them the two ways through, and the README upgrade note says so.
3. **Store check reuse.** The in-repository store check at `:56` calls `acf.approval._store_inside_repo` (`approval.py:121-122`) instead of repeating its expression.
4. **Closing line.** The closing line (`:67`) becomes `Approved <key> (<scope>) in <store>.`, with the scope text of §5.2.
5. **Docstring.** The module docstring (`:1-5`, *"Run by the user, never by an agent"*) states Decision 3: an agent may start it, and the user's permission-prompt answer approves.

### 5.4 The approval hook (`plugins/arch-compliance/hooks/approval_prompt.py`, new)

It is registered in `plugins/arch-compliance/hooks/hooks.json` under a new `PreToolUse` key:
- matcher `Bash|PowerShell|Write|Edit|MultiEdit|NotebookEdit`;
- command `python "${CLAUDE_PLUGIN_ROOT}/hooks/approval_prompt.py"`;
- `"timeout": 10`;
- `"onFailure": "block"`.

*(external, tools-reference: `PowerShell` is a tool name. permissions.md calls `MultiEdit` legacy, so listing it is harmless if it never matches.)*

It uses the standard library only and no `acf` import. So it costs one interpreter start, cannot fail on a missing dependency, and runs the same in a repository without `.acf/enabled`. Behaviour:

1. Read stdin as bytes. If none of the needles occurs in the raw bytes (compared case-insensitively), exit `0` at once. This is the common path.
2. Parse the JSON as UTF-8. The subject depends on the tool:
   - For `Bash` and `PowerShell`, the subject is `tool_input.command`.
   - For `Write`, `Edit`, `MultiEdit` and `NotebookEdit`, the subject is `tool_input.file_path` or `tool_input.notebook_path`.
   - File content is never a subject, so editing a document that mentions `acf-allow` does not prompt.
3. Needles, case-insensitive:
   - A shell command matches on any of `acf-allow`, `acf.cli_allow`, `approvals.json`. `acf.cli_allow` is the module form (`python -m acf.cli_allow`). Paths such as `acf/cli_allow.py` and `tests/test_cli_allow.py` do not contain it, so running, staging or testing that module's files does not prompt. A script that imports `write_approval` is not matched; §4's first bullet accepts that.
   - A file tool's path matches on `approvals.json` only, so editing `cli_allow.py` or its tests does not prompt.
   - `approvals.json` equals `acf.approval.STORE_REL.name`. A test pins the two (§6.3), since the hook does not import `acf`. §5.7 records this copy under `## Single point of definition`, and the `STORE_REL` line gains a comment naming the hook.
4. Subject matches and `permission_mode` is `bypassPermissions`: print `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "ACF approval needs your answer at a permission prompt, which bypass mode skips. Leave bypass mode, or run acf-allow in your own terminal."}}` and exit `0`.
5. Subject matches otherwise: the same shape with `"ask"` and the reason `ACF approval: allowing this approves the host detector code the agent just summarized, for every worktree of this repository whose files match. Deny if you have not read the summary.`
6. No match: exit `0`.
7. Any exception after step 1 found a needle: print `acf: approval hook failed: <type>: <message>` to stderr and exit `2`, which blocks the call. *(external, hooks.md: exit 2 blocks the tool call.)* The handler carries the `fail-loud.bare-except-ok` token with that reason, as `posttooluse_gate.py:89` does.

**Other modes.**
- In `auto` mode, a hook's `ask` goes to the person's prompt and the classifier does not decide it *(external, hooks.md)*. Explicit ask rules still prompt *(external, permission-modes.md)*. So the agent cannot approve itself through the classifier.
- `dontAsk` mode turns `ask` into a denial, and a non-interactive `-p` run denies calls that need approval *(external, permission-modes.md)*. Both are the intended outcome.
- `default`, `acceptEdits` and `plan` are covered by the ask-rule statement for "any mode" *(external, permission-modes.md)*.
- Whether a hook's `ask` prompts in `acceptEdits` for a file tool is *(unverified)*. That is why Decision 7's rules include the store path for the file tools, and §8 item 4 tests it.

### 5.5 Gate messages

- `require_approval` (`approval.py:149-154`): `host detectors need approval: <reason>; rows: <ids>. Ask the user to approve them: follow the acf-approve skill (acf-approval-status, a review for the user, then acf-allow --fingerprint at a permission prompt the user answers). A CI workflow, or a run with --mandates naming another file, passes --trusted-checkout.`
- The hook's notice (`posttooluse_gate.py:150-155`): `acf: host detectors not run: <reason>; rows skipped: <ids>. To have them run, follow the acf-approve skill; the user approves at a permission prompt. Never approve another way.`

Neither names a host (`ARCHITECTURE.md:232-233`).

### 5.6 The `acf-approve` skill (`plugins/arch-compliance/skills/acf-approve/SKILL.md`, new)

Description: use when a gate reports that host detectors need approval, when a host row or detector file changed, or when running `/acf-approve`. Procedure:

1. Run `acf-approval-status`. If the state is `APPROVED` or `NOT_NEEDED`, stop. If it is `STORE_IN_REPO`, tell the user and stop. If it fails, report its message and stop.
2. For each detector file, find out:
   - what changed (`git log -n 5 --format="%h %an %ad %s" -- <file>` and `git diff <default branch>... -- <file>`; for a first approval, the whole file);
   - what it executes (subprocesses, network, writes outside the repository);
   - which repository modules it imports, which the approval does not cover.
3. Post one message to the user with the repository and its scope, each file's path, SHA-256 and changes, the execution summary, the helper limit and the fingerprint. Say whether anything looks like more than a detector.
4. Run `acf-allow --fingerprint <hex>` once. The user answers the prompt.
5. If it is denied, refused or blocked, stop. Do not:
   - retry or rephrase the command;
   - edit `~/.acf/`;
   - write a script that approves;
   - add `--trusted-checkout`;
   - ask another session to approve.

   Tell the user they can approve later at their terminal.

### 5.7 Doctrine, code comments and prose

Each row below is a site found by the recipe in the next paragraph, or by reading the files the design changes. The list is per item and claims no completeness. The plan re-runs the recipe and adds any new hit.

Recipe: `grep -rn "acf-allow\|resolved root\|per checkout\|no-op\|\.acf/enabled" README.md docs/guides config/architecture plugins/arch-compliance/skills plugins/arch-compliance/hooks plugins/arch-compliance/python/acf/approval.py plugins/arch-compliance/python/acf/cli_allow.py docs/design/CHECK_DIFF_HOST_WIRING.md`.

| File | Change |
| --- | --- |
| `config/architecture/ARCHITECTURE.md:179-186` (`**Trust boundary.**`) | The approval is keyed by the repository's git common directory and the host's prefix (the folder for a non-git directory), so it covers every worktree whose host rows and files match. An agent may start `acf-allow --fingerprint`; the plugin's PreToolUse hook makes it prompt, and the user's answer is the approval. The closing line (`:188`) gains `test_approval_prompt.py` and `test_cli_approval_status.py`. |
| `config/architecture/ARCHITECTURE.md:213-228` (`## Declared, never defaulted`) | *"Three defaults elsewhere in the package"* becomes *"Four defaults"*, adding: the approval key is the folder when git reports the directory is not a repository (`acf.approval.repo_key`), and `describe_approval` prints the scope. |
| `config/architecture/ARCHITECTURE.md:270-277` (`## Declared text decoding`) | `run_git` leaves the declared debt: *"Three calls breach the rule today"* becomes *"Two calls"*, naming `adr/citations.py` `_git` and the TypeScript bridge. Their stale line citations are corrected while the sentence is rewritten: `citations.py:62-65` becomes `:59-61`, and `typescript_bridge.py:49-56` becomes `:120-126`. |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md:263` and `CLAUDE.md:36-38` (Windows `PYTHONUTF8=1` note) | The reason *"the git runner does not declare its text encoding"* becomes *"the TypeScript bridge does not declare its text encoding"* (still declared debt). The instruction itself stays. |
| `plugins/arch-compliance/python/acf/repo.py:4-5` (module docstring) | *"Both hooks import this"* becomes *"The two gate hooks import this"*; the approval prompt imports no `acf` code. |
| `plugins/arch-compliance/python/acf/review/rollup.py:4-5` (module docstring) | The `GitError` sentence of §5.1. |
| `config/architecture/ARCHITECTURE.md:299-302` (`## Single point of definition`) | Record the hook's copy of the store file name (`approvals.json` in `approval_prompt.py`, beside `acf.approval.STORE_REL`), kept because the hook imports no `acf`, and pinned by `test_approval_prompt.py`. The git-runner sentence keeps its substance; its citation `citations.py:54` becomes `:51`, where `_git` is defined. |
| `config/architecture/ARCHITECTURE.md:236-240` (`## Prose names no host`, coverage) | *"the other two skills … `acf-mandate` and `acf-setup`, have no row yet"* names `acf-approve` too: three skills, no row yet. |
| `plugins/arch-compliance/python/acf/approval.py:3-5` (module docstring) | *"keyed by the repository's resolved root"* becomes keyed by `repo_key` (git common directory and prefix, or the folder). |
| `plugins/arch-compliance/python/acf/approval.py:37` (`STORE_REL`) | A trailing comment: `hooks/approval_prompt.py` matches this file name; `test_approval_prompt.py` pins it. |
| `plugins/arch-compliance/hooks/posttooluse_gate.py:16-19` (module docstring) | *"(``acf-allow``)"* becomes *"(given through ``acf-approve``)"*. |
| `plugins/arch-compliance/hooks/hooks.json:2` (`description`) | Adds the PreToolUse approval prompt, says host detectors need an approval through `acf-approve`, and says the approval prompt runs whatever `.acf/enabled` says, while the other hooks no-op without it. |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md:24` | Replace the sub-bullet: when `mandates.yml` has host rows, follow `acf-approve`; one approval covers every worktree of the repository; offer the user the `permissions.ask` rules of Decision 7 for `~/.claude/settings.json`, and add them only on their yes. |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md:185` | *"plugin hooks (see below) no-op until this file exists"* gains *"except the approval prompt, which guards the per-user store in every repository"*; *"each person's `acf-allow`"* becomes *"each person's approval (`acf-approve`)"*. |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md:187`, `:206`, `:260`, `:262` | *"each person's `acf-allow`"* and *"a missing `acf-allow`"* become *"each person's approval (`acf-approve`)"* and *"a missing approval"*. |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md:288` | Drops *"Do not run `acf-allow` … yourself"* for *"approve only through `acf-approve`; never add `--trusted-checkout`"*. |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md:189-198` (hook table) | A `PreToolUse` row for `approval_prompt.py`. |
| `plugins/arch-compliance/skills/acf-mandate/SKILL.md:139` | The re-run needs a new approval (`acf-approve`) after a host row or detector file changes; never add `--trusted-checkout`. |
| `README.md:26-35` (skills table), `:64`, `:105-110` (hooks) | `acf-approve` and `acf-approval-status`, and the PreToolUse hook with its `onFailure` minimum Claude Code version. The clauses at `:64` and `:110` that have the user run `acf-allow` become approval through `acf-approve` at a permission prompt. |
| `README.md:112` | *"Hooks are a true no-op … until `.acf/enabled` exists"* gains the approval-prompt exception; *"each person runs `acf-allow` themselves"* becomes *"each person approves through `acf-approve`"*. |
| `README.md`, new upgrade note `### Upgrading to repository-wide, prompt-given approval (v0.3.5)` before `:114` | The key, the prompt channel, `acf-approval-status`, the hook and its minimum version, one re-approval per repository after upgrading, old entries deletable, and the `CLAUDE_CODE_CHILD_SESSION` refusal with its two ways through. `:143`'s *"One approval per checkout directory"* sentence is historical and stays under its v0.2.5 heading. |
| `docs/guides/SUPERPOWERS_COMPLEMENT.md:89` | *"Hooks are a true no-op until the host has `.acf/enabled`"* gains the approval-prompt exception; *"(`acf-allow`, which the user runs after reviewing the detector files)"* becomes the prompt-given approval through `acf-approve`. |
| `docs/design/CHECK_DIFF_HOST_WIRING.md:333` | Left as written: it is an Approved spec's record of the v0.3.4 text, and this spec's Supersedes header covers the approval channel. |
| `pyproject.toml:3`, `plugins/arch-compliance/.claude-plugin/plugin.json:3` | `0.3.4` → `0.3.5` (`ARCHITECTURE.md:283-284`). |

---

## 6. Tests

`plugins/arch-compliance/tests/conftest.py`'s autouse `_isolated_home` (`:10-17`) also runs `monkeypatch.delenv("CLAUDE_CODE_CHILD_SESSION", raising=False)`, so a suite started from inside Claude Code does not trip Decision 5. Subprocess tests pass an environment derived from it. No test touches the real store.

### 6.1 `test_git_runner.py` (new: git facts and the runner) and `test_approval.py`

**`run_git`:**
- A command whose stdout is not UTF-8 raises `GitError`. The test uses `git hash-object -w` to store `b"\xff\xfe"` as a blob, then runs `git cat-file -p <oid>`.
- A UTF-8 non-ASCII path is returned intact: G4, a repository under a `tmp_path / "Á"` directory.

**`git_common_dir`:**
- In a `git init` repository it returns `(<repo>/.git, "")`. In a `git worktree add` of it, it returns the same path (G1).
- In a subfolder `sub/` of each: prefix `sub`.
- With `GIT_DIR` set in the environment to the worktree's git directory, the `sub/` prefix is still `sub` (G3).
- In a plain `tmp_path` directory: `None` (G2). The test first asserts that `git rev-parse` exits `128` there, so a `tmp_path` inside a repository fails the test loudly instead of passing it wrongly.
- With `run_git` patched to return exit `128` and a different stderr, or exit `1`, or to raise `FileNotFoundError`: `GitError`, carrying git's stderr where there is one.

**`repo_key`:**
- Scope `repository` in a repository and in its worktree, with equal keys.
- Two subfolder hosts `a/` and `b/` of one repository get different keys. `a/` in the main checkout and in a worktree get one key.
- Scope `folder` and the resolved root in a plain directory.
- `GitError` from `git_common_dir` propagates.

**Approval behaviour:**
- Approve in the main checkout; the worktree is `APPROVED` with no further write. Edit a detector file in the worktree: the worktree is `STALE`, the main checkout stays `APPROVED`. Approve in the worktree after the edit; the main checkout (old bytes) is now `STALE`.
- Two subfolder hosts of one repository: approving `a/` leaves `b/`'s state unchanged.
- Two separate `git init` repositories with identical files: approving one leaves the other `MISSING`.
- A store holding only a root-keyed entry for a git repository's checkout: `MISSING` (Decision 2). The same for a plain directory: `APPROVED`.
- A repository without host rows: `check_approval` returns `NOT_NEEDED` with `run_git` patched to raise. This pins that it runs no git.

**Existing assertions that index the store by the root key.** They pass today only because `tmp_path` lies outside any git repository and so takes the folder key. Each is rewritten to index by `repo_key(<dir>).key`:

| Site | Today |
| --- | --- |
| `test_approval.py:229` | `assert keys == {repo_b.resolve().as_posix()}` |
| `test_approval.py:236` | `read_store(store_path()).repos[repo_a.resolve().as_posix()]` |
| `test_approval.py:239` | `repos[repo_a.resolve().as_posix()] == entry_a` |
| `test_approval.py:240` | `set(repos) == {repo_a.resolve().as_posix(), repo_b.resolve().as_posix()}` |
| `test_approval.py:265` | `read_store(store_path()).repos[repo.resolve().as_posix()]` |
| `test_cli_allow.py:70` | `RepoTree(repo).root.as_posix() in read_store(store_path()).repos` |
| `test_cli_allow.py:103` | `RepoTree(repo).root.as_posix() not in read_store(store_path()).repos` |

Recipe that found them: `grep -n "resolve().as_posix()\|root.as_posix()" plugins/arch-compliance/tests/test_approval.py plugins/arch-compliance/tests/test_cli_allow.py`. The plan re-runs it over `plugins/arch-compliance/tests/`.

### 6.2 `test_cli_allow.py` and `test_cli_approval_status.py` (new)

- `--fingerprint` equal to the current one: writes, exits `0`, prints the scope. Different: exit `1`, the message names both values, the store is byte-identical.
- `CLAUDE_CODE_CHILD_SESSION=1` without `--fingerprint`: exit `1`, store untouched. With it: writes. `--revoke` under the variable works without `--fingerprint`.
- A `GitError` from the key (`run_git` patched): `acf-allow` and `acf-approval-status` exit `1` with `acf: cannot compute the approval key`.
- `acf-approval-status`:
  - prints the state and the `describe_approval` lines, including the fingerprint `acf-allow --fingerprint` accepts and `HELPER_LIMIT`;
  - leaves the store unchanged (absent before, absent after);
  - with no host rows: exit `0`;
  - with a missing detector file: exit `1`.
- `acf-allow`'s review lines equal `describe_approval`'s for the same repository.

### 6.3 `test_approval_prompt.py` (new, subprocess runs of the hook)

**Prompts:**
- `Bash` with `acf-allow --fingerprint abc`: `ask` with the reason.
- The same in `PowerShell`.
- `python -m acf.cli_allow`: `ask`.
- `cd x && ACF-ALLOW`: `ask`.
- `bypassPermissions` with `acf-allow`: `deny`.
- `Write` with `file_path` `<home>/.acf/approvals.json`: `ask`.

**Silent passes:**
- `Write` whose content mentions `acf-allow` and whose path is `docs/x.md`: exit `0`, no output.
- `Bash` `acf-approval-status`: exit `0`, no output.
- `Bash` `ls`: exit `0`, no output.
- `Bash` `pytest plugins/arch-compliance/tests/test_cli_allow.py` and `git add plugins/arch-compliance/python/acf/cli_allow.py`: exit `0`, no output, in `bypassPermissions` mode too.
- Run in a `tmp_path` with no `.acf/enabled` and a `Bash` `acf-allow` payload: `ask`. This pins Decision 4's "whatever `.acf/enabled` says".

**Failure:**
- Malformed JSON containing `acf-allow`: exit `2`, stderr `acf: approval hook failed`.
- Malformed JSON without a needle: exit `0`.

**Pins:**
- The needle `approvals.json` equals `acf.approval.STORE_REL.name`.
- `hooks.json` registers the hook under `PreToolUse` with `onFailure` `block` and the matcher of §5.4.
- **The hook imports only the standard library** (new, modelled on `test_repo_module_imports_only_stdlib`, `plugins/arch-compliance/tests/test_repo_paths.py:74-78`, which checks `acf/repo.py` with a regex over its import lines). This test walks `approval_prompt.py`'s AST instead. For every `Import` and `ImportFrom` node it asserts that the top-level module name is in `sys.stdlib_module_names` (Python 3.10 or later; `pyproject.toml:5` requires 3.11). `acf` is not in that set, so the same assertion refuses an `acf` import.

### 6.4 `test_hooks.py`, `test_diff_cli.py`, `test_approval.py`

The tests that assert `acf-allow` in a gate message are `test_approval.py:209`, `test_hooks.py:554` and `test_diff_cli.py:400`. Recipe: `grep -n "acf-allow" plugins/arch-compliance/tests/*.py`.
- The new hook notice (§5.5) no longer contains `acf-allow`, so `test_hooks.py:554` asserts `acf-approve`.
- The new refusal still contains `acf-allow` (*"then acf-allow --fingerprint"*) and `--trusted-checkout`, so `test_approval.py:209` and `test_diff_cli.py:400` keep passing. Each also gains an assertion for `acf-approve`.
- A new `test_hooks.py` case: with `check_approval` raising `GitError`, the PostToolUse hook prints `acf: cannot compute the approval key` without a traceback and exits `2`.

### 6.5 Guards that must keep passing

- `test_repo_tree_guard.py`, with no new allowlist entry.
- `test_repo_paths.py`: its poisoned-module subprocess test (`:81-108`) runs the two existing hooks and is unchanged.
- `test_adr_skill_prose.py`: the new skill is outside its list (§5.7 records that), and its prose names no host by review.

---

## 7. Risks

| Risk | Mitigation |
| --- | --- |
| Claude Code older than v2.1.295 ignores `onFailure`, so a failing hook lets the call through. | The README note gives the minimum version. Decision 7's permission rule still prompts. `acf-allow` still needs `--fingerprint` when Claude starts it. |
| With `onFailure: "block"`, a broken hook or a missing `python` blocks every `Bash`, `PowerShell` and file-tool call in every repository. | The hook's common path is one byte scan, and its tests run it. The plugin's other hooks already need `python` on PATH (`hooks.json:2`). The failure is loud, not silent, and uninstalling the plugin clears it. |
| Commands that only mention a needle prompt: `grep -n acf-allow README.md`, or a `git commit -m` whose message names `acf-allow`. In `bypassPermissions` mode the hook denies them instead. | Accepted: the reason says what allowing does, and in a host that is rare. In this repository it is common while editing approval prose; there, leave bypass mode or rephrase the message. |
| Every user must approve each git repository once after upgrading. | One prompt per repository, and the README note says so. |
| A host whose git output is not UTF-8 now gets `GitError` from the diff gate's existing git calls, where the locale codec may have decoded it. | On Windows the locale codec already lost such output without an error (G4). CI on Linux and the documented `PYTHONUTF8=1` runs already decode UTF-8, so for them nothing changes. The error names the command. |
| A machine whose git is older than 2.31 now gets `GitError` from the key, where it had a folder approval. | Git 2.31 shipped in March 2021. The error carries git's own message, which names the unknown option. |
| The hook's `deny` in bypass mode is *(unverified)*. | §8 item 4 tests it. Decision 7's rule is the documented guarantee. |
| Remote Control's handling of a hook-raised `ask` prompt is *(unverified)*. | §8 item 3 tests it. If it fails, the design still fixes #62 and keeps the terminal path. |

---

## 8. Acceptance

1. All tests pass, including §6.
2. In a scratch git repository with `.acf/enabled` and a host row:
   - run `acf-allow` in the main checkout;
   - a `git worktree add` folder is then `APPROVED` per `acf-approval-status`, and its `pre-push` hook's `acf-check-diff --call-site precommit` runs the host row;
   - editing the detector file in the worktree makes it `STALE`.
3. From a Remote Control session on that repository, the agent follows `acf-approve`. The permission prompt appears on the remote device with the hook's reason. Allow records the approval; on a second run, Deny records nothing.
4. Mode checks:
   - In `bypassPermissions` mode, the agent's `acf-allow --fingerprint` is denied with the hook's reason.
   - In `auto` mode, it prompts and is not decided by the classifier.
   - In `acceptEdits` mode, an agent `Write` to `~/.acf/approvals.json` prompts.
5. With the hook script temporarily renamed, a `Bash` call is blocked (`onFailure`), not run.
6. The diff gate on this branch (`PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main --call-site ci`) exits `0`, and so does the same command without `PYTHONUTF8`.
7. `pyproject.toml:3` and `plugins/arch-compliance/.claude-plugin/plugin.json:3` read `"0.3.5"`.

## 9. Left to the builder, and follow-ups

**Left to the builder:**
- Test file layout beyond the names above.
- The exact wording of `acf-approve` around the fixed steps of §5.6.
- Whether `RepoKey` lives in `approval.py` or beside `git_common_dir`. Its consumers are `approval.py`, `cli_allow.py` and `cli_approval_status.py`.

**Follow-ups, filed as issues when this merges:**
1. The diff gate's own `git diff` calls inherit `GIT_DIR` from a linked worktree's `pre-push` hook (G3). For a subfolder host they may diff against the wrong tree. Whether to strip the variables in `run_git` for every call is a separate design.
