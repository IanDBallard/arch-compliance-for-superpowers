# Host Detector Approval per Repository, Given at the Permission Prompt — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Key host-detector approvals by the git repository instead of the worktree folder (#62), and let an agent start `acf-allow` so that the user approves at a Claude Code permission prompt, from any device.

**Architecture:** `run_git` decodes strict UTF-8 and takes an `env`. A new `git_common_dir` asks git for the common directory and prefix with git's locating variables removed. `acf.approval.repo_key` turns that into the store key and is the only key deriver. `acf-allow` gains `--fingerprint` and refuses without it under Claude Code. A new read-only `acf-approval-status` prints the review through a shared `describe_approval`. A new stdlib-only PreToolUse hook, `approval_prompt.py`, returns `ask` (or `deny` in bypass mode) for approval commands, registered with `onFailure: block`. A new `acf-approve` skill is the procedure the gate messages name.

**Tech Stack:** Python ≥3.11, Pydantic v2, pytest, git ≥2.31, Claude Code hooks (≥v2.1.295 for `onFailure`).

**Spec:** `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md` (v4). Section numbers below (§5.1 and so on) are that spec's. Read the spec's §3 and §5 before Task 1.

## Global Constraints

- Branch `feat/approval-by-repository`. Baseline: `python -m pytest -q` → **840 passed** at `04af612`.
- Run every test command from the repository root. Never `pip install -e` from a worktree.
- New errors reuse `GitError`, `AcfInputError`, `UnknownDetectorError` (`acf/exceptions.py`); no new exception class.
- `acf.repo` and `approval_prompt.py` import only the standard library (and, for the hook, `acf.repo`).
- Messages name no host repository, path or section (`ARCHITECTURE.md:232-233`). Paths in messages and in the store use `.as_posix()`.
- Exact copy is fixed by the spec: the `--fingerprint` mismatch message (§5.3 item 1), the Claude Code refusal (§5.3 item 2), the hook's deny and ask reasons (§5.4 steps 4-5), the hook failure prefix `acf: approval hook failed: ` (§5.4 step 7), the `require_approval` text and the hook notice (§5.5), the `git_common_dir` error prefix `cannot compute the approval key for <repo>: git rev-parse failed: ` (§5.1 step 5). Copy them verbatim.
- Scope strings: `every worktree of this repository` (scope `repository`) and `this folder only` (scope `folder`).
- `APPROVAL_NEEDLES = ("acf-allow", "acf.cli_allow", STORE_REL.name)`; a file tool matches on `STORE_REL.name` only; comparisons are case-insensitive.
- Version `0.3.4` → `0.3.5` in `pyproject.toml:3` and `plugins/arch-compliance/.claude-plugin/plugin.json:3` (Task 8).
- On Windows run the diff gate as `PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main --call-site ci`.

## Review Focus

Uncovered inputs a user will meet, each pinned by a test in the owning task:

1. **A Windows store path in a file tool, with backslashes and different case** (`C:\Users\x\.acf\APPROVALS.JSON`). The hook must still `ask`. Test in Task 7.
2. **Hook stdin that is not UTF-8 but contains a needle.** It must block (exit `2`), not pass. Test in Task 7.
3. **A shell payload whose needle is outside `tool_input.command`** (for example in `description`). It must pass silently: only the subject decides. Test in Task 7.
4. **A repository or worktree path containing a space.** `git_common_dir` must return it intact and both worktrees one key. Test in Task 2.
5. **`acf-allow --revoke --fingerprint <anything>` under `CLAUDE_CODE_CHILD_SESSION=1`.** Revoke proceeds and ignores the fingerprint. Test in Task 5.

---

### Task 1: `run_git` decodes strict UTF-8 and takes `env` (§5.1)

**Files:**
- Modify: `plugins/arch-compliance/python/acf/diff.py:17-30`
- Modify: `plugins/arch-compliance/python/acf/review/rollup.py:1-10` (docstring), `:70-95` (`provenance`)
- Modify: `plugins/arch-compliance/tests/test_diff_cli.py:216` (docstring only)
- Create: `plugins/arch-compliance/tests/test_git_runner.py`
- Test: `plugins/arch-compliance/tests/test_review_rollup.py`

**Interfaces:**
- Produces: `run_git(repo: Path, *args: str, env: Mapping[str, str] | None = None) -> subprocess.CompletedProcess[str]`. Raises `GitError` when stdout is not UTF-8, whatever the exit status. stderr is decoded with `errors="replace"`.

- [ ] **Step 1: Write failing tests** in `test_git_runner.py`:
  - `test_run_git_raises_on_non_utf8_stdout`: `git init`; `oid = git hash-object -w --stdin` fed `b"\xff\xfe"`; `pytest.raises(GitError, match="cat-file")` around `run_git(repo, "cat-file", "-p", oid)`.
  - `test_run_git_returns_non_ascii_path_intact[Á, é]` (parametrized): `repo = tmp_path / name`, `git init`; `out = run_git(repo, "rev-parse", "--absolute-git-dir").stdout`; assert `out.strip().endswith(f"{name}/.git")` and `out` is not `None`.
  - `test_run_git_passes_env`: `run_git(repo, "var", "GIT_AUTHOR_IDENT", env={**os.environ, "GIT_AUTHOR_NAME": "Zed"})` stdout starts with `Zed`.
  - In `test_review_rollup.py`: `test_provenance_unresolved_on_git_error`: patch `acf.review.rollup.run_git` to raise `GitError("x")` for `blame`; assert `provenance(...)` returns `("unresolved", <str containing "x">)` (match the existing call shape of the other provenance tests).
- [ ] **Step 2: Run** `python -m pytest plugins/arch-compliance/tests/test_git_runner.py plugins/arch-compliance/tests/test_review_rollup.py -q`. Expected: the new tests FAIL (`TypeError` for `env`, no `GitError`, `None` stdout on Windows).
- [ ] **Step 3: Implement.** `run_git` calls `subprocess.run([...], cwd=repo, capture_output=True, check=False, env=env)` (bytes), decodes stdout with `.decode("utf-8")` inside `try`, and on `UnicodeDecodeError as exc` raises `GitError(f"git {' '.join(args)}: output is not UTF-8 at byte {exc.start}")` `from exc`. Returns `subprocess.CompletedProcess(proc.args, proc.returncode, stdout, stderr)`. Docstring keeps its first sentence and adds the `GitError` sentence. `provenance` catches `GitError` around its blame call and returns `("unresolved", str(exc))`. Rollup module docstring adds that undecodable git output raises `GitError`. `test_diff_cli.py:216` docstring: append "; undecodable stdout raises GitError".
- [ ] **Step 4: Run** the full suite `python -m pytest -q`. Expected: all pass (840 + new).
- [ ] **Step 5: Commit** `fix(diff): run_git decodes UTF-8 strictly and accepts env`.

### Task 2: `git_common_dir` (§5.1, G1-G3)

**Files:**
- Modify: `plugins/arch-compliance/python/acf/diff.py` (new function beside `run_git`)
- Test: `plugins/arch-compliance/tests/test_git_runner.py`

**Interfaces:**
- Consumes: `run_git(..., env=...)` (Task 1).
- Produces: `git_common_dir(repo: Path) -> tuple[Path, str] | None`. `None` only for exit `128` with `not a git repository` in stderr; every other failure raises `GitError` with the §5.1 step 5 prefix.

- [ ] **Step 1: Write failing tests** (helper `_init(path)` runs `git init -q` and one commit; `_worktree(repo, path)` runs `git worktree add`):
  - `test_common_dir_main_and_worktree_equal`: returns `(repo/.git resolved as git prints it, "")` in the repo; the worktree returns the same path.
  - `test_common_dir_subfolder_prefix`: in `sub/` of each → prefix `"sub"`.
  - `test_common_dir_ignores_inherited_git_dir`: `monkeypatch.setenv("GIT_DIR", <worktree git dir>)`; in the worktree's `sub/` the prefix is still `"sub"`.
  - `test_common_dir_none_outside_repo`: first assert `subprocess.run(["git","rev-parse"], cwd=tmp_path/"plain").returncode == 128`, then `git_common_dir(...) is None`.
  - `test_common_dir_raises_on_other_failures` (parametrized): patch `acf.diff.run_git` so the second call returns exit `128` with stderr `fatal: other`, or exit `1`, or raises `FileNotFoundError`; each → `GitError` matching `cannot compute the approval key`, and containing `fatal: other` in the first case.
  - Review Focus 4, `test_common_dir_path_with_space`: repo at `tmp_path / "my repo"`, worktree at `tmp_path / "my wt"`; both return the same common dir, whose `.as_posix()` contains `my repo`.
- [ ] **Step 2: Run** `python -m pytest plugins/arch-compliance/tests/test_git_runner.py -q`. Expected: FAIL (`ImportError`).
- [ ] **Step 3: Implement** per §5.1 steps 1-5: `--local-env-vars` names removed from a copy of `os.environ`, `LC_ALL=C` set, then `rev-parse --path-format=absolute --git-common-dir --show-prefix`. Wrap `OSError` as `GitError(...) from exc`.
- [ ] **Step 4: Run** the file again. Expected: PASS.
- [ ] **Step 5: Commit** `feat(diff): git_common_dir for a worktree-independent repository identity`.

### Task 3: `repo_key` and the store re-key (§5.1, §5.4 `STORE_REL`, Decision 2)

**Files:**
- Modify: `plugins/arch-compliance/python/acf/repo.py:1-6` (docstring) and add `STORE_REL`
- Modify: `plugins/arch-compliance/python/acf/approval.py:3-5` (docstring), `:36-37` (remove `STORE_REL`, import it), `:135`, `:167`
- Modify: `plugins/arch-compliance/python/acf/cli_allow.py:76`
- Modify: `plugins/arch-compliance/tests/test_approval.py:12`, `:229`, `:236`, `:239`, `:240`, `:265`; `plugins/arch-compliance/tests/test_cli_allow.py:70`, `:103`

**Interfaces:**
- Consumes: `git_common_dir` (Task 2).
- Produces: in `acf.approval`: `@dataclass(frozen=True) class RepoKey: key: str; scope: Literal["repository", "folder"]` and `repo_key(repo: Path) -> RepoKey`. In `acf.repo`: `STORE_REL = Path(".acf") / "approvals.json"` with comment `Relative to ``Path.home()``.`

- [ ] **Step 1: Write failing tests** in `test_approval.py` (repositories via `git init` and a committed host row and detector file, using the file's existing fixtures for rows):
  - `test_repo_key_repository_scope_shared_by_worktree`; `test_repo_key_subfolders_differ_and_match_across_worktrees` (`a/`, `b/`); `test_repo_key_folder_scope_outside_git` (key `== tmp.resolve().as_posix()`, scope `"folder"`); `test_repo_key_propagates_git_error`.
  - `test_worktree_approved_by_main_checkout_approval`, then edit in worktree → worktree `STALE`, main `APPROVED`; approve worktree → main `STALE`.
  - `test_approving_subfolder_a_leaves_b_unchanged`; `test_separate_repositories_do_not_share`; `test_old_root_key_ignored_for_git_repo` (store holds only `{root.as_posix(): entry}` → `MISSING`) and `test_old_root_key_still_used_for_plain_folder` (→ `APPROVED`).
  - `test_not_needed_runs_no_git`: patch `acf.diff.run_git` (and `acf.approval`'s reference if imported by name) to raise; `check_approval` on a registry without host rows returns `NOT_NEEDED`.
  - Rewrite the seven root-key assertions of spec §6.1's table to index by `repo_key(<dir>).key`; `test_approval.py:12` imports `STORE_REL` from `acf.repo`.
- [ ] **Step 2: Run** `python -m pytest plugins/arch-compliance/tests/test_approval.py plugins/arch-compliance/tests/test_cli_allow.py -q`. Expected: new tests FAIL.
- [ ] **Step 3: Implement** `repo_key` per §5.1; replace the three `RepoTree(repo).root.as_posix()` key expressions with `repo_key(repo).key`; `check_approval` computes it after the `NOT_NEEDED` and `STORE_IN_REPO` returns. Update the two docstrings (§5.7 rows for `repo.py` and `approval.py`).
- [ ] **Step 4: Run** `python -m pytest -q` and re-run the recipe `grep -rn "resolve().as_posix()\|root.as_posix()" plugins/arch-compliance/tests/`; every remaining hit is a folder-scope assertion, not a store index. Expected: all pass.
- [ ] **Step 5: Commit** `feat(approval): key approvals by git common directory and prefix (#62)`.

### Task 4: `GitError` handlers and the new gate messages (§5.1 table, §5.5)

**Files:**
- Modify: `plugins/arch-compliance/hooks/posttooluse_gate.py:16-19` (docstring), `:141-145`, `:150-155`
- Modify: `plugins/arch-compliance/python/acf/approval.py:149-154`
- Modify: `plugins/arch-compliance/tests/test_hooks.py:554`, `test_approval.py:209`, `test_diff_cli.py:400`

**Interfaces:**
- Consumes: `repo_key` raising `GitError` (Task 3).

- [ ] **Step 1: Write failing tests:** `test_hooks.py:554` asserts `acf-approve` in the notice; `test_approval.py:209` and `test_diff_cli.py:400` add `assert "acf-approve" in msg`; new `test_posttooluse_reports_key_git_error`: patch `check_approval` to raise `GitError("cannot compute the approval key for x: ...")`; the hook exits `2`, stderr contains `acf: cannot compute the approval key` and no `Traceback`.
- [ ] **Step 2: Run** those three files. Expected: FAIL.
- [ ] **Step 3: Implement:** add `GitError` to the hook's except tuple; set both messages to the §5.5 copy; docstring per §5.7.
- [ ] **Step 4: Run** `python -m pytest -q`. Expected: PASS.
- [ ] **Step 5: Commit** `feat(approval): gate messages point at acf-approve; report key failures`.

### Task 5: `describe_approval` and `acf-allow --fingerprint` (§5.2, §5.3, Decision 5)

**Files:**
- Modify: `plugins/arch-compliance/python/acf/approval.py` (add `HELPER_LIMIT`, `describe_approval`)
- Modify: `plugins/arch-compliance/python/acf/cli_allow.py:1-5`, `:27-30`, `:38-44`, `:56`, `:58-67`, `:68`
- Modify: `plugins/arch-compliance/tests/conftest.py:10-17`
- Test: `plugins/arch-compliance/tests/test_cli_allow.py`

**Interfaces:**
- Consumes: `repo_key` (Task 3).
- Produces: `HELPER_LIMIT: str` (the text now at `cli_allow.py:27-30`, unchanged) and `describe_approval(repo: Path, rows: list[Mandate], digests: Mapping[str, str]) -> list[str]` returning the five §5.2 groups in order; line 1 is `repository: <key> (<scope text>)`, the fingerprint line is `fingerprint: <hex>`.

- [ ] **Step 1: Write failing tests:**
  - conftest's `_isolated_home` adds `monkeypatch.delenv("CLAUDE_CODE_CHILD_SESSION", raising=False)`.
  - `test_fingerprint_match_writes`: `main(["--repo", r, "--fingerprint", fingerprint(rows, file_digests(r, rows))])` → `0`, store has `repo_key(r).key`, stdout contains `every worktree of this repository`.
  - `test_fingerprint_mismatch_refuses`: store bytes identical before and after (or absent), exit `1`, stderr contains `reviewed deadbeef` and the current hex and `nothing approved`.
  - `test_child_session_requires_fingerprint`: `monkeypatch.setenv("CLAUDE_CODE_CHILD_SESSION", "1")`; no flag → `1`, stderr contains `needs --fingerprint`, store untouched; with the right fingerprint → `0`.
  - `test_child_session_revoke_without_fingerprint` → `0`. Review Focus 5, `test_child_session_revoke_ignores_fingerprint`: `--revoke --fingerprint bad` → `0`, entry removed.
  - `test_allow_reports_key_git_error`: patch `acf.approval.git_common_dir` to raise `GitError("cannot compute the approval key for x: y")` → exit `1`, stderr contains `acf: cannot compute the approval key`.
  - `test_allow_review_lines_equal_describe_approval`: the stdout lines before the closing line equal `describe_approval(...)`.
- [ ] **Step 2: Run** `python -m pytest plugins/arch-compliance/tests/test_cli_allow.py -q`. Expected: FAIL.
- [ ] **Step 3: Implement** §5.3 items 1-5: the comparison sits between `file_digests` and `write_approval`; the refusal check runs after argument parsing and before any work; `:56` calls `_store_inside_repo(repo, store)`; closing line `Approved <key> (<scope text>) in <store>.`; `_revoke` prints the new key; add `GitError` to the except tuple.
- [ ] **Step 4: Run** `python -m pytest -q`. Expected: PASS.
- [ ] **Step 5: Commit** `feat(cli_allow): bind approval to a reviewed fingerprint; refuse bare runs under Claude Code`.

### Task 6: `acf-approval-status` (§5.2, Decision 6)

**Files:**
- Create: `plugins/arch-compliance/python/acf/cli_approval_status.py`
- Modify: `pyproject.toml:18-21`
- Create: `plugins/arch-compliance/tests/test_cli_approval_status.py`

**Interfaces:**
- Consumes: `check_approval`, `approval_rows`, `file_digests`, `describe_approval`, `load_gate_registry`, `TIER1_CALL_SITES` (from `acf.registry`, as `approval.py:27-28` imports it).
- Produces: `main(argv: list[str] | None = None) -> int`, console script `acf-approval-status`.

- [ ] **Step 1: Write failing tests:** prints `state: MISSING` then the `describe_approval` lines (the fingerprint printed is accepted by `acf-allow --fingerprint`, and `HELPER_LIMIT` appears); store absent before and after; no host rows → `0` and a "no host detector rows" line; missing detector file → `1` with `acf: ` on stderr; `GitError` from the key → `1`, `acf: cannot compute the approval key`. (`test_packaging.py` asserts no console-script list today; nothing to add there.)
- [ ] **Step 2: Run** the new file. Expected: FAIL (`ModuleNotFoundError`).
- [ ] **Step 3: Implement** per §5.2. It writes nothing.
- [ ] **Step 4: Run** `python -m pytest -q`; then `pip install -e .` from the main checkout only (memory rule) and `acf-approval-status --repo .` prints a state. Expected: PASS and a state line.
- [ ] **Step 5: Commit** `feat: acf-approval-status prints the approval review without writing`.

### Task 7: The approval hook (§5.4, Decision 4)

**Files:**
- Create: `plugins/arch-compliance/hooks/approval_prompt.py`
- Modify: `plugins/arch-compliance/hooks/hooks.json` (new `PreToolUse` key; `description` per §5.7)
- Modify: `plugins/arch-compliance/tests/test_repo_paths.py:81-108`
- Create: `plugins/arch-compliance/tests/test_approval_prompt.py`

**Interfaces:**
- Consumes: `acf.repo.STORE_REL` (Task 3).
- Produces: module constant `APPROVAL_NEEDLES`; stdout JSON `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask"|"deny", "permissionDecisionReason": <§5.4 copy>}}`.

- [ ] **Step 1: Write failing tests** (helper `run_hook(payload: dict | bytes, cwd=tmp_path) -> CompletedProcess` runs `sys.executable approval_prompt.py` with the conftest-derived env; payloads carry `tool_name`, `tool_input`, `permission_mode`):
  - Prompts (`permissionDecision == "ask"`, reason equals the §5.4 step 5 copy): Bash `acf-allow --fingerprint abc`; PowerShell same; `python -m acf.cli_allow`; `cd x && ACF-ALLOW`; Write `file_path` `<home>/.acf/approvals.json`; Review Focus 1: Write `file_path` `C:\Users\x\.acf\APPROVALS.JSON`; Bash `acf-allow` run in a `tmp_path` without `.acf/enabled`.
  - `bypassPermissions` with `acf-allow` → `deny` with the step 4 copy.
  - Silent (exit `0`, empty stdout): Write to `docs/x.md` whose content mentions `acf-allow`; `acf-approval-status`; `ls`; `pytest plugins/arch-compliance/tests/test_cli_allow.py` and `git add plugins/arch-compliance/python/acf/cli_allow.py`, each also in `bypassPermissions`; Review Focus 3: Bash `{"command": "ls", "description": "then acf-allow"}`.
  - Failure: malformed JSON containing `acf-allow` → exit `2`, stderr starts `acf: approval hook failed`; Review Focus 2: bytes `b'{"tool_input":{"command":"acf-allow \xff"}}'` → exit `2`; malformed JSON without a needle → exit `0`.
  - Pins: `hooks.json` has `PreToolUse` with matcher `Bash|PowerShell|Write|Edit|MultiEdit|NotebookEdit`, command `python "${CLAUDE_PLUGIN_ROOT}/hooks/approval_prompt.py"`, `timeout` `10`, `onFailure` `block`. AST import test per spec §6.3 last bullet.
  - `test_repo_paths.py` poisoned-module test: add a run of `approval_prompt.py` with a Bash `acf-allow` payload; stdout contains `"ask"`.
- [ ] **Step 2: Run** `python -m pytest plugins/arch-compliance/tests/test_approval_prompt.py plugins/arch-compliance/tests/test_repo_paths.py -q`. Expected: FAIL.
- [ ] **Step 3: Implement** §5.4 steps 1-7: bytes scan with `needle.encode().lower() in raw.lower()` first; then `json.loads(raw.decode("utf-8"))`; subject by tool; the broad handler carries the `fail-loud.bare-except-ok` token with its reason (as `posttooluse_gate.py:89`). The `sys.path` block copies `posttooluse_gate.py:37-41` (the recorded copy, follow-up 3).
- [ ] **Step 4: Run** `python -m pytest -q`. Expected: PASS.
- [ ] **Step 5: Commit** `feat(hooks): PreToolUse approval prompt that fails closed`.

### Task 8: `acf-approve` skill, prose, doctrine, README, version (§5.6, §5.7, Decision 7)

**Files:**
- Create: `plugins/arch-compliance/skills/acf-approve/SKILL.md`
- Modify: every row of spec §5.7 (`ARCHITECTURE.md` five sections, `acf-setup/SKILL.md` lines `:24`, `:185`, `:187`, `:189-198`, `:206`, `:260`, `:262`, `:263`, `:288`, `acf-mandate/SKILL.md:139`, `CLAUDE.md:37-39`, `README.md`, `docs/guides/SUPERPOWERS_COMPLEMENT.md:89`, `pyproject.toml:3`, `plugin.json:3`)
- Test: `plugins/arch-compliance/tests/test_approval_prompt.py`

**Interfaces:**
- Consumes: `APPROVAL_NEEDLES` (Task 7), `STORE_REL`, the commands of Tasks 5-6.

- [ ] **Step 1: Write the failing pin test** `test_ask_rules_match_needles` per spec §6.3 ("The ask rules and the needles agree"), regex ``re.compile(r"`(Bash|PowerShell|Edit)\([^)`]*\)`")`` over `acf-setup/SKILL.md`, asserting both directions and that at least one rule exists.
- [ ] **Step 2: Run** it. Expected: FAIL (no rules yet).
- [ ] **Step 3: Write the skill and prose.** `acf-approve/SKILL.md` carries §5.6's description and steps 1-5 verbatim in substance, naming no host. `acf-setup/SKILL.md:24` gains the five Decision 7 rules as backticked tokens, offered only on the user's yes. Apply each remaining §5.7 row as written; the README gets the v0.3.5 upgrade note (including the by-hand removal of old entries and the `CLAUDE_CODE_CHILD_SESSION` refusal's two ways through). Bump both versions to `0.3.5`. Re-run the §5.7 recipe and handle any new hit; leave `CHECK_DIFF_HOST_WIRING.md` as written.
- [ ] **Step 4: Run** `python -m pytest -q` (includes `test_adr_skill_prose.py`, `test_review_doctrine.py`, `test_packaging.py`). Expected: PASS.
- [ ] **Step 5: Commit** `docs: acf-approve skill and repository-wide prompt-given approval prose; 0.3.5`.

### Task 9: Acceptance (§8)

**Files:**
- Create (when run): `docs/design/evidence/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT/bypass_hook_probe.out`

- [ ] **Step 1:** `python -m pytest -q` and `npm test --prefix plugins/arch-compliance/detectors/typescript`. Expected: all pass, `self-test OK`.
- [ ] **Step 2:** `PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main --call-site ci`, then the same without `PYTHONUTF8`. Expected: exit `0` both times.
- [ ] **Step 3:** §8 item 2 in a scratch repository (`acf-allow` in main checkout; `git worktree add`; `acf-approval-status` there reads `APPROVED`; its `pre-push` runs the host row; an edit there reads `STALE`). Record the commands and output in the PR body.
- [ ] **Step 4:** After the user refreshes the standalone CLI login, `python docs/design/evidence/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT/bypass_hook_probe.py <claude> <variant>` for `control`, `json_deny`, `exit2`, `ask_rule`; expected `call_ran` `true`, `false`, `false`, `false`. Commit the output as `bypass_hook_probe.out`.
- [ ] **Step 5:** Hand the user §8 items 3 (Remote Control prompt, Allow then Deny), 4 (bypass, auto, acceptEdits) and 5 (hook renamed → `Bash` blocked) with the plugin installed at 0.3.5; these need their session and device. Record their results in the PR body.
- [ ] **Step 6:** Before merge, run `python scripts/check_installed_skills.py <INSTALL_PATH>` only if a gate or housekeeping run follows; file §9 follow-ups 1-4 as issues at merge.
