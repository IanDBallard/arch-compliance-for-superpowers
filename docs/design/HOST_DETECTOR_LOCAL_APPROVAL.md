# Host Detector Local Approval and Hook Failure Visibility

**Status:** Draft (v2)
**Date:** 2026-11-11
**Spec kinds:** `defect`
**Repo:** `IanDBallard/arch-compliance-for-superpowers`, `main` at `0da9864` (branch `feat/host-detector-approval`).
**Issues:** #29 (a committed `.acf/enabled` opts every clone into running host code on edit), #30 (PostToolUse gate-input failures exit 1, which the agent does not see).
**Supersedes:** Decision 7 (trust boundary) of `docs/design/HOST_DETECTOR_EXTENSION_POINT.md` (`:63-65`), which reads *"That marker is the opt-in for running host code on edit"* and *"`acf-check-diff` runs only when the host's own pre-commit or CI configuration invokes it … That invocation is the opt-in."*
**Governing mandates:** `config/architecture/ARCHITECTURE.md` sections `## Fail loud` (`:25-42`), `## POSIX paths` (`:56-65`), `## One base exception` (`:107-111`), `## One owner for host paths` (`:113-139`), `## Host detectors and call sites` (`:141-182`), `## Prose names no host` (`:201-209`), `## No completeness claims` (`:225-235`), `## Declared text decoding` (`:237-248`), `## Release discipline` (`:250-260`), `## Single point of definition` (`:262-275`).
**No state-machine surface.** This design adds or modifies no state machine and no transition.

---

## 0. Citation convention

Unprefixed paths refer to this repository. Every cited line is as at `main` `0da9864`; the branch adds only files under `docs/` (recipe: `git diff --stat 0da9864 HEAD -- . ':!docs'` prints nothing). Every path is written in full with POSIX forward slashes. One external document is cited, the Claude Code hooks reference (`https://code.claude.com/docs/en/hooks`), for what Claude Code does with a hook's exit code and JSON output; every claim resting on it is marked *(external)*.

---

## 1. Problem

### 1.1 The approval to run host code travels with the code (#29)

Host detector rows (`detector: <path>.py:<callable>`) make ACF import and call a repository's own Python. Two gates do that, and neither asks the person running it.

**The PostToolUse hook.** The plugin registers it, not the host: `plugins/arch-compliance/hooks/hooks.json:16-27` runs `posttooluse_gate.py --format hook` on every `Write|Edit|MultiEdit`, and the hook's own comment says it *"fires on every Write/Edit in every repo once the plugin is installed"* (`plugins/arch-compliance/hooks/posttooluse_gate.py:32-35`). Its only check is whether `.acf/enabled` (`plugins/arch-compliance/python/acf/repo.py:29`) is a file: `posttooluse_gate.py:74-83` returns `0` when it is not. Past that check `_scan_paths` calls `scan_host_ast_file` (`:273-277`, `:283-287`) and `scan_host_guards` (`:292-294`).

**The diff gate.** `acf-check-diff` calls the same runners (`plugins/arch-compliance/python/acf/cli_check_diff.py:167-182`, `:204`) with no check at all. Host pre-commit and CI configurations invoke it, and so does the plugin's own prose, which has the agent run it by hand in whatever checkout it is in:
- `plugins/arch-compliance/skills/acf-setup/SKILL.md:221-230` (Step 9, *"From the **host** root, run one of: `acf-check-diff --mode worktree --call-site precommit`"*);
- `plugins/arch-compliance/skills/acf-mandate/SKILL.md:136` (*"Reminder to re-run `acf-check-diff` … after meaningful enforcement changes"*);
- `README.md:57` (*"`acf-check-diff --mode staged --call-site precommit        # local`"*).

**What runs.** `load_host_detector` (`plugins/arch-compliance/python/acf/detectors/host.py:53-95`) builds a module spec from the named file and calls `spec.loader.exec_module(mod)` (`:83`) in the gate's own process; `_call_host` then calls the returned callable (`:108`). The doctrine states the consequence: *"The wrapping guarantees typed errors, not confinement: a host module runs in the gate's process with its privileges"* (`config/architecture/ARCHITECTURE.md:178-179`).

**Root cause.** The only opt-in either gate has is something the repository itself supplies: the hook's marker file in the working tree, and, for the diff gate, nothing beyond being invoked. The doctrine records the hook half: *"The PostToolUse hook runs host code only when `.acf/enabled` exists; committing `.acf/` therefore opts every clone in"* (`ARCHITECTURE.md:175-176`), and the setup skill recommends committing it: *"Suggest adding `.acf/` to git if the team wants hooks enabled for everyone"* (`plugins/arch-compliance/skills/acf-setup/SKILL.md:150`). Neither gate holds state outside the working tree that records a person's approval of particular code, so approval and code arrive together with a `git clone` or `git checkout`.

**Consequences, in order of likelihood:**

1. Checking out a contributor's branch and asking the agent to edit a file, or to run the diff gate, runs that branch's detector code with the user's privileges, including in a repository the user trusts, because the code changed after the user last looked at it.
2. Cloning an unfamiliar repository that commits `.acf/enabled` and a host row runs that repository's code on the agent's first edit.
3. A host detector's finding messages reach the agent's context (`posttooluse_gate.py:137-147`, `additionalContext`; `:132`, stderr on exit 2), so an unapproved detector also writes text the agent reads.

Before host rows existed (`git log --diff-filter=A --format=%h -- plugins/arch-compliance/python/acf/detectors/host.py` prints `8677e45`), neither gate imported a repository module: at `8677e45^`, `git grep -n "importlib\|exec_module\|runpy" -- plugins/arch-compliance/python plugins/arch-compliance/hooks` prints nothing.

### 1.2 A gate-input failure in the hook reaches the user but not the agent (#30)

`posttooluse_gate.py` returns `1` on four gate-input failures, whatever the output format:

| Line | Condition |
| --- | --- |
| `:85-91` | `.acf/enabled` present, `config/architecture/mandates.yml` missing |
| `:99-107` | the `acf` package's dependencies cannot be imported |
| `:109-113` | `load_mandates` raises `AcfInputError` or `UnknownDetectorError` |
| `:116-120` | `_scan_paths` raises `AcfInputError`, `DetectorPackError` or `UnknownDetectorError` |

Any other exception raised after the marker check ends the process with a traceback and exit `1` as well, for example a `UnicodeDecodeError` from `abs_path.read_text(encoding="utf-8")` on a non-UTF-8 edited file (`:249`), which none of the `except` tuples names.

The hook relies on exit `2` being the code whose stderr reaches the agent: *"Exit 2 feeds stderr back to Claude as blocking feedback."* (`posttooluse_gate.py:131`). *(external)* The Claude Code hooks reference states that for PostToolUse an exit code of `2` shows stderr to Claude and that other non-zero codes show stderr to the user only. The design depends only on the first half, which the hook already depends on; the second half is why exit `1` is the wrong code, and if it were false exit `2` would still be the documented agent channel.

**Root cause.** The exit code was chosen for the text-mode contract (a script or a person reads exit `1`) and carried into hook mode unchanged; hook-mode failure paths share the text-mode code, and the paths no `except` names have no hook-mode handling at all.

---

## 2. Decisions

1. **`.acf/enabled` keeps its meaning for built-in detectors and stops being sufficient for host code.** With the marker present the hook runs built-in detectors as today. Host rows need an approval (Decision 2) in both gates.
2. **The approval is per user, outside the repository, and bound to a fingerprint.** It lives in one JSON store at `Path.home() / ".acf" / "approvals.json"`, keyed by `RepoTree(repo).root.as_posix()` (`## POSIX paths`: *"When persisting paths to YAML/JSON, use `Path.as_posix()`"*, `ARCHITECTURE.md:58`). A store inside the repository is refused: when `RepoTree(repo).contained(str(store_path))` is not `None`, the repository is treated as unapproved and the refusal names the reason. `Path.home()` reads `USERPROFILE` on Windows and `HOME` on POSIX, so the process environment decides where the store is; the containment check removes the one route by which a repository could supply its own approval file through that environment.
3. **One fingerprint covers every active host row and the files they name; a gate asks for it only when it would run a host row.** Rows: `registry.host_rows(TIER1_CALL_SITES)` (§4.1). Files: the path part of each row's `detector`. Any change to such a row, an added or removed row, or a changed byte in a named file changes the fingerprint and lapses the approval. Both gates check the same fingerprint, so one approval covers both. A gate run whose call sites select no host row (`registry.host_rows(call_sites)` empty) needs no approval: a `[hook]`-only host row never refuses a `--call-site ci` run.
4. **What is fingerprinted is what runs.** `load_host_detector` compiles the named file's source on every load instead of letting the import system substitute bytecode from `__pycache__/` (§4.4).
5. **One approval command, `acf-allow`, run by a person.** It prints each fingerprinted row (id, detector) and each named file with its SHA-256, then writes the approval. `acf-allow --revoke` removes the repository's entry. Every message the gates send toward the agent asks it to have the user review the files and run `acf-allow`; skill prose tells the agent never to run `acf-allow` or add `--trusted-checkout` itself. A person approves the code they reviewed; an agent approving on its own would restore §1.1.
6. **An unapproved hook run is governed by built-ins and told so, not blocked.** When host rows exist and the approval is missing or stale, the hook skips them, runs the built-ins, and reports one notice to the agent and to the user naming the rows skipped and the command to run. It does not exit non-zero for that reason alone.
7. **An unapproved diff-gate run is refused unless the invocation declares a trusted checkout.** `acf-check-diff` gains `--trusted-checkout`. Without it, a registry with host rows and no matching approval is refused with exit `1` and a message naming `acf-allow` and `--trusted-checkout`; it never reports a clean run with host rows skipped. CI workflows pass `--trusted-checkout`, so the opt-in is written in the workflow file the host controls.
8. **Hook-mode failures exit 2.** When the output format is `hook`, the four returns of §1.2 return `2` with the same stderr message, and any other `Exception` raised after the format is known is reported on stderr (type, message, traceback) and returns `2`. Text and JSON formats keep exit `1` and the traceback.

---

## 3. Non-goals and residual exposure

- **Not confinement.** An approved detector still runs with the user's privileges (`ARCHITECTURE.md:178-179`).
- **Imported helpers are outside the fingerprint.** `load_host_detector` appends the repository root to `sys.path` (`host.py:59`), so a detector can import any repository module through the normal import system, bytecode cache included. A change confined to such a helper runs under the existing approval. `acf-allow` prints this limit beside the file list.
- **Between the check and the load.** The fingerprint is computed when the gate starts and the file is read again when it is loaded; a file rewritten in between runs unapproved bytes. A process that can rewrite the working tree during a gate run can already run code as the user.
- **Whoever can write the user's home directory, or run `acf-allow`, can approve.** That actor can already run code; Claude Code's tool permissions govern an agent doing either.
- **A repository whose root is the home directory** always has the store inside it, so it is always unapproved: the hook never runs its host rows, and its diff gate runs them only with `--trusted-checkout`. `acf-allow` says so.
- **The SubagentStart hook** (`plugins/arch-compliance/hooks/inject_constraints.py`) runs no host code (recipe: `grep -n "acf.detectors\|scan_host\|load_host_detector" plugins/arch-compliance/hooks/inject_constraints.py` prints nothing; its `acf` imports, `grep -n "from acf" plugins/arch-compliance/hooks/inject_constraints.py` at `:31`, `:91`, `:92`, `:163` and `:170`, are `acf.repo`, `acf.exceptions`, `acf.registry`, `acf.loader` and `acf.template`) and keeps its exit codes.
- **Other repository-controlled input to the gates** is outside this design. One such path is recorded for a separate fix: on Windows the TypeScript bridge runs its scanner with `shell=True` (`plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:52-58`), passing the edited file's path on a command line.
- **No shared or team-wide approval.** A committed approval would reintroduce §1.1.

---

## 4. Design

### 4.1 One selector for host rows (`plugins/arch-compliance/python/acf/registry.py`)

`MandateRegistry.host_rows(call_sites: frozenset[str], *, detection: str | None = None) -> list[Mandate]` returns `[m for m in self.active(call_sites, detection=detection) if m.detection in {"ast", "guard"} and is_host_detector_ref(m.detector)]`. Its consumers:

| Consumer | Today | After |
| --- | --- | --- |
| `scan_host_ast_file` (`host.py:162-166`) | `registry.active(call_sites, detection="ast")` filtered by `is_host_detector_ref` and language | `registry.host_rows(call_sites, detection="ast")` filtered by language |
| `scan_host_guards` (`host.py:192-194`) | `registry.active(call_sites, detection="guard")` filtered by `is_host_detector_ref` | `registry.host_rows(call_sites, detection="guard")` |
| `acf.approval` (§4.2) | — | `registry.host_rows(TIER1_CALL_SITES)` |

### 4.2 `acf.approval` (new module, `plugins/arch-compliance/python/acf/approval.py`)

It imports `acf.loader`, `acf.registry`, `acf.repo` and `acf.exceptions`, so it needs pydantic; the hook imports it only after its third-party imports succeed (`posttooluse_gate.py:93-107`), and the hook's no-marker path (`:74-83`) still imports nothing beyond `acf.repo`.

| Name | Contract |
| --- | --- |
| `STORE_REL = Path(".acf") / "approvals.json"` | Relative to `Path.home()`. |
| `ApprovalEntry`, `ApprovalStore` | Pydantic models, `extra="forbid"`: `ApprovalEntry(fingerprint: str, approved: str)`; `ApprovalStore(version: Literal[1] = 1, repos: dict[str, ApprovalEntry] = {})`. |
| `store_path() -> Path` | `Path.home() / STORE_REL`. |
| `read_store(path: Path) -> ApprovalStore` | `ApprovalStore()` when `path.is_file()` is false; otherwise `load_model_file(path, ApprovalStore, subject="approval store", fmt="json")` (`plugins/arch-compliance/python/acf/loader.py:43-77`). That is the split `load_baseline`'s docstring prescribes: *"Absence is a real state decided by the CALLER (existence check before load). The loader itself never returns None."* (`plugins/arch-compliance/python/acf/baseline.py:81-82`). Every refusal is that loader's `AcfInputError`. |
| `approval_rows(registry) -> list[Mandate]` | `registry.host_rows(TIER1_CALL_SITES)` sorted by `id`. |
| `file_digests(repo: Path, rows) -> dict[str, str]` | For each distinct path part (`parse_host_detector_ref`), the SHA-256 hex of `RepoTree(repo).file(rel).read_bytes()`. `file` returning `None`, or an `OSError` from `file` or `read_bytes`, raises `AcfInputError` naming the path. |
| `fingerprint(rows, digests) -> str` | SHA-256 hex of `json.dumps({"rows": [_canonical(m.model_dump(mode="python")) for m in rows], "files": digests}, sort_keys=True, separators=(",", ":"), default=str)`. `_canonical` recurses through dicts and lists; it turns a `set` or `frozenset` into a list sorted by each element's canonical JSON text, and replaces each dict key with its canonical JSON text (so `1` and `"1"` stay distinct, and a date or tuple key from YAML becomes a string `json.dumps` can sort). A YAML `!!set` or non-string key in `params` therefore hashes the same in every process and never raises inside `json.dumps`. |
| `ApprovalState` | `enum.Enum`: `NOT_NEEDED` (no rows), `APPROVED`, `MISSING`, `STALE`, `STORE_IN_REPO`. |
| `approval_state(repo, registry, call_sites: frozenset[str]) -> ApprovalState` | `NOT_NEEDED` when `registry.host_rows(call_sites)` is empty; `STORE_IN_REPO` when the store is contained in the repository; otherwise compares `fingerprint(rows, file_digests(repo, rows))` with the store entry. |
| `require_approval(repo, registry, call_sites) -> None` | Raises `AcfInputError` when `approval_state(repo, registry, call_sites)` is `MISSING`, `STALE` or `STORE_IN_REPO`. Message: `host detectors need approval: <reason>; rows: <ids>. Ask the user to review the detector files and run acf-allow; a CI workflow passes --trusted-checkout.` |
| `write_approval(repo, registry, *, revoke: bool = False) -> None` | Reads the store, sets or removes the repository's entry (`approved` is an ISO-8601 UTC timestamp), writes `model_dump_json` to a temporary file in the same directory and moves it into place with `os.replace`, creating `~/.acf/` when missing. An `OSError` raises `AcfInputError` naming the path. Adjacent to `save_baseline` (`baseline.py:68-75`), which writes an in-repository artifact in place and raises `BaselineError`; the approval store is a per-user file read and rewritten by concurrent processes, so it is replaced whole rather than written in place, and no helper is shared. |

Repository paths go through `RepoTree` (`ARCHITECTURE.md:125-130`: *"Callers hand it the string they hold and never join, resolve or compare against the root themselves"*); the store path is compared with the repository only through `RepoTree.contained`.

### 4.3 `acf-allow` (new console script, `plugins/arch-compliance/python/acf/cli_allow.py`)

`pyproject.toml:18-20` gains `acf-allow = "acf.cli_allow:main"`, the `acf.cli_<name>:main` shape of the two existing scripts.

- `main(argv: list[str] | None = None) -> int`; arguments `--repo PATH` and `--revoke`; the repository is `resolve_repo(args.repo)`, as in `cli_check_diff.main` (`cli_check_diff.py:76`), so no new path resolution enters the module.
- Loads the registry as the diff gate does (`load_mandates(repo / MANDATES_REL, known_detectors=KNOWN_DETECTORS, llm_prompt_ids=LLM_PROMPT_IDS, repo_root=repo)`). A missing or unstat-able host detector file is refused there with `UnknownDetectorError` (`registry.py:160-172`).
- No approval rows: says so, exits `0`, writes nothing.
- Store inside the repository: prints the refusal, exits `1`.
- Otherwise prints, per row, `id` and `detector`; per file, its repository-relative path and SHA-256 from `file_digests`; then the imported-helper limit of §3; writes the approval; exits `0`.
- `--revoke`: removes the entry if present, says what it did, exits `0`.
- `AcfInputError` or `UnknownDetectorError`: message to stderr, exit `1`.

### 4.4 Source-only loading (`plugins/arch-compliance/python/acf/detectors/host.py`)

`load_host_detector` passes `loader=_SourceOnlyLoader(name, str(module_path))` to `importlib.util.spec_from_file_location` (`host.py:78`). `_SourceOnlyLoader` subclasses `importlib.machinery.SourceFileLoader` and overrides `get_code(self, fullname)` to return `compile(self.get_data(self.path), self.path, "exec", dont_inherit=True)`, so the bytes executed are the bytes `file_digests` hashed, and no `.pyc` in `__pycache__/` is read for the detector file. A committed test pins this (§6.2).

### 4.5 PostToolUse hook (`plugins/arch-compliance/hooks/posttooluse_gate.py`)

1. After `load_mandates` succeeds (`:109-113`), compute `state = approval_state(repo, registry, HOOK_CALL_SITES)` inside the same `try`; its `AcfInputError` is handled like a malformed registry.
2. `_scan_paths(repo, paths, registry, *, run_host: bool)` skips the three host calls (`:273-277`, `:283-287`, `:292-294`) when `run_host` is false; `run_host` is `state in {NOT_NEEDED, APPROVED}`. `rel_paths` and `file_lines` are filled before the host calls (`:243-250`) and the built-in calls read only them.
3. For `MISSING`, `STALE` or `STORE_IN_REPO`, one notice: `acf: host detectors not run: <reason>; rows skipped: <ids>. Ask the user to review the detector files and run acf-allow in this repository; do not run it yourself.`
4. Delivery: `hook` format without a BLOCK finding prepends the notice to `additionalContext` (`:137-147`) and sets a top-level `systemMessage` *(external: the hooks reference lists `systemMessage` among the JSON fields any hook may return, shown to the user)*; `hook` format with a BLOCK finding prints it to stderr before the findings (`:130-133`); `text` and `json` formats print it to stderr, leaving stdout parseable.
5. Exit codes (Decision 8): each of the four returns of §1.2 becomes `return 2 if out_format == "hook" else 1` (`out_format` is set at `:68-72`, before the first). The code after `:72` runs inside `try: … except Exception as exc:` that, in `hook` format, prints `acf: internal error: <type>: <message>` and the traceback to stderr and returns `2`, and otherwise re-raises. The handler carries the `fail-loud.bare-except-ok` exemption token (`config/architecture/mandates.yml:60`) with that reason, since it reports rather than swallows.
6. The module docstring (`:9-14`) states the approval rule and the exit codes.

### 4.6 Diff gate (`plugins/arch-compliance/python/acf/cli_check_diff.py`)

1. `--trusted-checkout` (store true): *"Run host detectors without a local approval. For CI checkouts, where the workflow file is the opt-in."*
2. Inside the existing `try` (`:83-100`), after `load_mandates` and the empty-selection refusal, `require_approval(repo, registry, sites)` unless `args.trusted_checkout`. Its `AcfInputError` is caught at `:98` and exits `1`, like every other refusal there.

### 4.7 Doctrine and prose

| File | Change |
| --- | --- |
| `config/architecture/ARCHITECTURE.md:175-180` (`**Trust boundary.**`) | Both gates run host rows only when `~/.acf/approvals.json` holds an approval matching the fingerprint of the active host rows and their files (`acf-allow`), or, for `acf-check-diff`, when the invocation passes `--trusted-checkout`; the hook runs built-ins and reports skipped rows without one; the diff gate refuses. Keep the confinement and `load_mandates` sentences. Add: in hook mode, gate failures exit `2`. The closing line (`:182`) gains `test_approval.py` and `test_cli_allow.py`. |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md:16-25` (steps) | After step 7, a step: when `mandates.yml` has host rows, show the user the detector files and ask them to run `acf-allow` themselves; the agent never runs `acf-allow` or adds `--trusted-checkout`. |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md:148`, `:150` | `.acf/enabled` turns on the hooks for built-in detectors; host detectors also need each person's `acf-allow`. Committing `.acf/` approves no host code. |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md:159` (PostToolUse row) | Host detectors and host guards run only with an approval. |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md:208-209` (CI sketch) | Add `--trusted-checkout` to both lines. |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md:221-238` (Step 9) | A registry with host rows needs `acf-allow` first; a refusal naming `acf-allow` is not a pass. |
| `plugins/arch-compliance/skills/acf-mandate/SKILL.md:136` | The re-run needs `acf-allow` again after a host row or detector file changes. |
| `README.md:57-62`, `:108`, `:110`, and a new upgrade note after the v0.2.4 note (`:112-117`) | The approval rule, `--trusted-checkout` in CI, hook exit `2` on gate failures. |
| `docs/guides/SUPERPOWERS_COMPLEMENT.md:82-87` | The same facts. |
| `plugins/arch-compliance/hooks/hooks.json:2` (`description`) | *"exit 2 on BLOCK findings and on gate failures; host detectors need acf-allow"*. |
| `pyproject.toml:3`, `plugins/arch-compliance/.claude-plugin/plugin.json:3` | `"0.2.4"` → `"0.2.5"` (`ARCHITECTURE.md:252-253`: *"A change to a skill's prose bumps the plugin version"*). |

New prose and the notice name no host repository (`## Prose names no host`, `ARCHITECTURE.md:203`).

---

## 5. Change surface

| Path | Change |
| --- | --- |
| `plugins/arch-compliance/python/acf/approval.py` (new) | §4.2 |
| `plugins/arch-compliance/python/acf/cli_allow.py` (new) | §4.3 |
| `plugins/arch-compliance/python/acf/registry.py` | `host_rows` (§4.1) |
| `plugins/arch-compliance/python/acf/detectors/host.py` | selector use (§4.1), `_SourceOnlyLoader` (§4.4) |
| `plugins/arch-compliance/hooks/posttooluse_gate.py` | §4.5 |
| `plugins/arch-compliance/python/acf/cli_check_diff.py` | §4.6 |
| `plugins/arch-compliance/hooks/hooks.json` | description (§4.7) |
| `pyproject.toml`, `plugins/arch-compliance/.claude-plugin/plugin.json` | script, version |
| `config/architecture/ARCHITECTURE.md`, `plugins/arch-compliance/skills/acf-setup/SKILL.md`, `plugins/arch-compliance/skills/acf-mandate/SKILL.md`, `README.md`, `docs/guides/SUPERPOWERS_COMPLEMENT.md` | §4.7 |
| `plugins/arch-compliance/tests/test_approval.py` (new), `plugins/arch-compliance/tests/test_cli_allow.py` (new), `plugins/arch-compliance/tests/test_hooks.py`, `plugins/arch-compliance/tests/test_diff_cli.py`, `plugins/arch-compliance/tests/test_host_detectors.py` | §6 |

Recipe after implementation: `git diff --stat main -- plugins/arch-compliance/python plugins/arch-compliance/hooks` lists the runtime rows of this table.

---

## 6. Tests

Subprocess tests set `HOME` and `USERPROFILE` to a directory under `tmp_path` beside (not inside) the seeded repository; in-process tests monkeypatch `Path.home`. No test touches the real store.

### 6.1 Existing tests that run a gate with host rows

Population: the executed census `docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/host_row_gate_tests.py`, which lists each test function that both runs a gate (the hook or `acf-check-diff`) and builds a host row, following module-level helpers one level deep. Its committed output, `host_row_gate_tests.out`, at `0da9864`:

| Test | Disposition |
| --- | --- |
| `plugins/arch-compliance/tests/test_diff_cli.py:350` `test_host_ast_and_guard_rows_run_at_ci_and_block` | Seed an approval with `write_approval`; assertions unchanged. |
| `test_diff_cli.py:367` `test_host_guard_exemption_token_on_a_non_code_file_is_honoured` | Same. |
| `test_diff_cli.py:379` `test_host_guard_only_row_at_precommit_passes_selection_and_reports` | Same. |
| `plugins/arch-compliance/tests/test_hooks.py:406` `test_gate_disabled_does_not_import_a_host_module` | Unchanged: no `.acf/enabled`, so the hook returns before any approval is read. |
| `test_hooks.py:440` `test_gate_runs_hook_host_rows_and_not_ci_only_host_guards` | Seed an approval; assertions unchanged. |
| `test_hooks.py:464` `test_gate_edited_file_outside_repo_yields_no_finding_and_no_host_call` | Same. |
| `test_hooks.py:488` `test_gate_native_absolute_path_is_reported_under_its_posix_key` | Same. |

The implementer re-runs the census before editing and gives any new line the matching disposition.

### 6.2 `test_approval.py` (new) and `test_host_detectors.py`

- `fingerprint` changes when a host row's `params` change, when a host row is added, when a detector file's bytes change, and when a `[ci]`-only host row changes; it does not change when a built-in row changes.
- A row whose `params` hold a YAML `!!set` gives the same fingerprint in subprocesses run with `PYTHONHASHSEED` `1`, `2` and `3`.
- A row whose `params` hold mixed `int`/`str` keys, a date key and a tuple key fingerprints without raising, and `{1: x}` and `{"1": x}` fingerprint differently.
- `approval_state(..., call_sites)` is `NOT_NEEDED` for `DIFF_CALL_SITES` when every host row is `[hook]`-only.
- `approval_state`: `NOT_NEEDED`, `MISSING`, `APPROVED` after `write_approval`, `STALE` after editing a detector file, `STORE_IN_REPO` with `HOME`/`USERPROFILE` inside the repository.
- `read_store`: a missing file gives an empty store; invalid JSON and a wrong shape each raise `AcfInputError` naming the path.
- `write_approval(..., revoke=True)` removes only that repository's entry.
- `file_digests` raises `AcfInputError` when a named file cannot be read.
- `test_host_detectors.py`: a detector whose `__pycache__/` holds an unchecked hash-based `.pyc` (`py_compile.compile(..., invalidation_mode=PycInvalidationMode.UNCHECKED_HASH)`) compiled from different source runs the source, not the `.pyc`.
- The `registry.host_rows` selector: `scan_host_ast_file` and `scan_host_guards` keep their existing test results (`test_host_detectors.py`).

### 6.3 `test_hooks.py` additions

- Unapproved, `hook` format: no host call (the detector's log stays empty); the built-in finding is still reported; exit `0` without a BLOCK; `additionalContext` and `systemMessage` contain `acf-allow` and the skipped row id.
- Unapproved with a BLOCK built-in finding: exit `2`; stderr holds the notice and the finding.
- Stale approval: no host call; the notice says the rows or files changed.
- `json` format, unapproved: stdout parses as JSON; the notice is on stderr.
- `hook` format exit `2` for each row of §1.2 (mandates missing; dependencies missing via `_no_deps_env`; unknown built-in detector; an approved host detector that raises), and for a non-UTF-8 edited `.py` file; each asserts an `acf:` line on stderr.
- The text-format exit-1 tests (`test_hooks.py:145`, `:318`, `:424`) stay as they are, pinning exit `1` outside hook mode.

### 6.4 `test_diff_cli.py` additions and `test_cli_allow.py` (new)

- Diff gate, host rows, no approval, no flag: exit `1`; stderr names `acf-allow` and `--trusted-checkout`; no host call.
- Same with `--trusted-checkout`: host rows run.
- Same after `write_approval`: host rows run without the flag.
- No host rows, no approval: unchanged behaviour (built-in rows only).
- A `[hook]`-only host row and no approval: `--call-site ci` runs and is not refused.
- `acf-allow` prints row ids, detectors, file hashes and the helper limit, writes an entry, exits `0`; no host rows: exit `0`, no store; missing detector file: exit `1`, store unchanged; store inside the repository: exit `1`; `--revoke` removes the entry.

### 6.5 Guards that must keep passing

`plugins/arch-compliance/tests/test_repo_tree_guard.py` (no new allowlist entry), `plugins/arch-compliance/tests/test_repo_paths.py:81-108` (the hook's no-marker path imports nothing third-party), `plugins/arch-compliance/tests/test_adr_import_graph.py:70-76` and `:79`.

---

## 7. Risks

| Risk | Mitigation |
| --- | --- |
| A host whose CI runs host rows at the invoked call site breaks on upgrade until its workflow adds `--trusted-checkout`; a run whose call site selects no host row is unaffected (Decision 3). | The refusal names the flag; the README upgrade note says so. This repository's own `mandates.yml` has no host row (`grep -n "detector: .*\.py:" config/architecture/mandates.yml` prints nothing), so its CI (`.github/workflows/ci.yml:40`) is unaffected. |
| Hand runs and the hook lose host detectors until each person runs `acf-allow`. | Not silently: the hook's notice and the diff gate's refusal both name the command. |
| The notice on every edit is noise for someone who never wants host detectors at edit time. | Accepted for this version. |
| CRLF and LF checkouts of one file hash differently. | The approval is per clone, so only that clone's bytes matter. |
| Concurrent `acf-allow` runs lose one write, or Windows refuses `os.replace` while the store is open. | A lost entry shows up as the notice and is fixed by re-running; the `OSError` is an `AcfInputError` naming the path. |

---

## 8. Acceptance

1. All tests pass, including §6.
2. In a scratch host with `.acf/enabled`, a host row and no approval: an edit through Claude Code shows the notice and makes no host call; `acf-check-diff --call-site precommit` is refused; after `acf-allow` both run the host row; after editing the detector file both are back to unapproved.
3. The diff gate on this branch (`PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main --call-site ci`) exits `0`.
4. `pyproject.toml:3` and `plugins/arch-compliance/.claude-plugin/plugin.json:3` read `"0.2.5"`.
