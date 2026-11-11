# Host Detector Local Approval and Hook Failure Visibility

**Status:** Draft (v3)
**Date:** 2026-11-11
**Spec kinds:** `defect`
**Repo:** `IanDBallard/arch-compliance-for-superpowers`, `main` at `0da9864` (branch `feat/host-detector-approval`).
**Issues:** #29 (a committed `.acf/enabled` opts every clone into running host code on edit), #30 (PostToolUse gate-input failures exit 1, which the agent does not see).
**Supersedes:** Decision 7 (trust boundary) of `docs/design/HOST_DETECTOR_EXTENSION_POINT.md` (`:63-65`), which reads *"That marker is the opt-in for running host code on edit"* and *"`acf-check-diff` runs only when the host's own pre-commit or CI configuration invokes it … That invocation is the opt-in."* Also supersedes, for the hook, the description at `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:161` (*"runs host guards on every edited in-repo path"*): host guards now run there only with an approval.
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
2. **The approval is per user, outside the repository, and bound to a fingerprint.** It lives in one JSON store at `Path.home() / ".acf" / "approvals.json"`, keyed by `RepoTree(repo).root.as_posix()` (`## POSIX paths`: *"When persisting paths to YAML/JSON, use `Path.as_posix()`"*, `ARCHITECTURE.md:58`). A store inside the repository is refused: when `RepoTree(repo).contained(str(store_path))` is not `None`, the repository is treated as unapproved and the refusal names the reason. `Path.home()` reads `USERPROFILE` on Windows and `HOME` on POSIX, so the process environment decides where the store is; the containment check refuses the case where the store would be one of the repository's own files. A `RuntimeError` from `Path.home()` (no home directory can be determined) is an `AcfInputError`.
3. **One fingerprint covers every active host row and the files they name; a gate asks for it only when it would run a host row.** Rows: `registry.host_rows(TIER1_CALL_SITES)` (§4.1). Files: the path part of each row's `detector`. Any change to such a row, an added or removed row, or a changed byte in a named file changes the fingerprint and lapses the approval. Both gates check the same fingerprint, so one approval covers both. A gate run whose call sites select no host row (`registry.host_rows(call_sites)` empty) needs no approval: a `[hook]`-only host row never refuses a `--call-site ci` run.
4. **What is fingerprinted is what runs.** `load_host_detector` compiles the named file's source instead of letting the import system substitute bytecode from `__pycache__/`, and when the gate holds an approval it refuses to compile bytes whose SHA-256 differs from the approved digest for that file, so a file rewritten after the approval check is refused rather than run (§4.4).
5. **Row `params` hold JSON values only.** `load_mandates` refuses a row whose `params` would not round-trip through `json.dumps`/`json.loads` unchanged (a YAML set, date, binary value, non-string key or NaN), so the fingerprint is plain sorted JSON of each row and needs no canonicalisation of its own (§4.1).
6. **One approval command, `acf-allow`, run by a person.** It prints each fingerprinted row (id, detector) and each named file with its SHA-256, then writes the approval. `acf-allow --revoke` removes the repository's entry. Every message the gates send toward the agent asks it to have the user review the files and run `acf-allow`; skill prose tells the agent never to run `acf-allow` or add `--trusted-checkout` itself. A person approves the code they reviewed; an agent approving on its own would restore §1.1.
7. **An unapproved hook run is governed by built-ins and told so, not blocked.** When host rows exist and the approval is missing or stale, the hook skips them, runs the built-ins, and reports one notice to the agent and to the user naming the rows skipped and the command to run. It does not exit non-zero for that reason alone.
8. **An unapproved diff-gate run is refused unless the invocation declares a trusted checkout.** `acf-check-diff` gains `--trusted-checkout`. Without it, a registry with host rows and no matching approval is refused with exit `1` and a message naming `acf-allow` and `--trusted-checkout`; it never reports a clean run with host rows skipped. CI workflows pass `--trusted-checkout`, so the opt-in is written in the workflow file the host controls.
9. **The shared input loader types every bad-file failure.** `load_model_file` also turns a `UnicodeDecodeError` while reading and a `ValueError` or `RecursionError` while parsing into `AcfInputError`, so the approval store, the registry and every other input file are refused the same typed way (§4.7).
10. **Hook-mode failures exit 2.** When the output format is `hook`, the four returns of §1.2 return `2` with the same stderr message, and any other `Exception` raised after the format is known is reported on stderr (type, message, traceback) and returns `2`. Text and JSON formats keep exit `1` and the traceback.

---

## 3. Non-goals and residual exposure

- **Not confinement.** An approved detector still runs with the user's privileges (`ARCHITECTURE.md:178-179`).
- **Imported helpers are outside the fingerprint.** `load_host_detector` appends the repository root to `sys.path` (`host.py:59`), so a detector can import any repository module through the normal import system, bytecode cache included. A change confined to such a helper runs under the existing approval. `acf-allow` prints this limit beside the file list.
- **Whoever can write the user's home directory, or run `acf-allow`, can approve.** Claude Code's tool permissions govern an agent doing either; skill prose and every gate message tell the agent to leave approval to the user (Decision 6).
- **`--trusted-checkout` trusts whoever writes the command line.** A committed pre-commit configuration that adds the flag runs repository code at commit time; so does any command that configuration already runs, since `pre-commit install` is the user's consent to run the repository's hook commands. Skill prose puts the flag only in the CI sketch.
- **The store's location follows the process environment.** A `HOME`/`USERPROFILE` pointing at a location someone else controls hands that party the approvals; the design refuses only a store inside the repository.
- **A repository whose root is the home directory** (or an ancestor of it) always has the store inside it, so it is always unapproved: the hook never runs its host rows, and its diff gate runs them only with `--trusted-checkout`. Its `.acf/enabled` and the store share `~/.acf/`. `acf-allow` says so.
- **The SubagentStart hook** (`plugins/arch-compliance/hooks/inject_constraints.py`) runs no host code (recipe: `grep -n "acf.detectors\|scan_host\|load_host_detector" plugins/arch-compliance/hooks/inject_constraints.py` prints nothing; its `acf` imports, `grep -n "from acf" plugins/arch-compliance/hooks/inject_constraints.py` at `:31`, `:91`, `:92`, `:163` and `:170`, are `acf.repo`, `acf.exceptions`, `acf.registry`, `acf.loader` and `acf.template`) and keeps its exit codes.
- **Other repository-controlled input to the gates** is outside this design. One such path is recorded for a separate fix: on Windows the TypeScript bridge runs its scanner with `shell=True` (`plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:52-58`), passing the edited file's path on a command line.
- **One approval per checkout directory.** The key is the resolved root, so each clone and each git worktree needs its own `acf-allow`.
- **`acf-allow` approves the default registry** (`config/architecture/mandates.yml`). A diff-gate run with `--mandates` pointing at another file fingerprints that file's rows, so it needs `--trusted-checkout`; its refusal says so.
- **The hook loads the registry without prompt-id validation** (`posttooluse_gate.py:110`), so a registry with an active `llm` row naming an unknown prompt id reaches the approval notice in the hook, and `acf-allow` then refuses that registry with the prompt-id error, which names the row to fix.
- **No shared or team-wide approval.** A committed approval would reintroduce §1.1.

---

## 4. Design

### 4.1 One selector for host rows (`plugins/arch-compliance/python/acf/registry.py`)

`Mandate.is_host_row` (property) is `self.detection in {"ast", "guard"} and is_host_detector_ref(self.detector)`, the one statement of "this row runs host code". `MandateRegistry.host_rows(call_sites: frozenset[str], *, detection: str | None = None) -> list[Mandate]` returns `[m for m in self.active(call_sites, detection=detection) if m.is_host_row]`. A new `Mandate` validator, `_json_params`, raises `AcfInputError` naming the row when `params` is not `None` and `json.loads(json.dumps(params, allow_nan=False)) != params` (a `TypeError`, `ValueError` or `RecursionError` from `json.dumps` counts as unequal; a top-level non-string key never reaches it, since `params: dict[str, Any]` already refuses one). Consumers:

| Consumer | Today | After |
| --- | --- | --- |
| `Mandate._row_shape` (`registry.py:69-76`) | `self.detection not in {"ast", "guard"}` then `is_host_detector_ref` | `self.is_host_row` |
| `load_mandates` (`registry.py:144-154`) | `m.detection in {"ast", "guard"} and not is_host_detector_ref(...)`, then `is_host_detector_ref` again | `m.is_host_row` |
| `scan_host_ast_file` (`host.py:162-166`) | `registry.active(call_sites, detection="ast")` filtered by `is_host_detector_ref` and language | `registry.host_rows(call_sites, detection="ast")` filtered by language |
| `scan_host_guards` (`host.py:192-194`) | `registry.active(call_sites, detection="guard")` filtered by `is_host_detector_ref` | `registry.host_rows(call_sites, detection="guard")` |
| `acf.approval` (§4.2) | — | `registry.host_rows(TIER1_CALL_SITES)` |

### 4.2 `acf.approval` (new module, `plugins/arch-compliance/python/acf/approval.py`)

It imports `acf.loader`, `acf.registry`, `acf.repo` and `acf.exceptions`, so it needs pydantic; the hook imports it only after its third-party imports succeed (`posttooluse_gate.py:93-107`), and the hook's no-marker path (`:74-83`) still imports nothing beyond `acf.repo`.

| Name | Contract |
| --- | --- |
| `STORE_REL = Path(".acf") / "approvals.json"` | Relative to `Path.home()`. |
| `ApprovalEntry`, `ApprovalStore` | Pydantic models, `extra="forbid"`: `ApprovalEntry(fingerprint: str, approved: str)`; `ApprovalStore(version: Literal[1] = 1, repos: dict[str, ApprovalEntry] = {})`. |
| `store_path() -> Path` | `Path.home() / STORE_REL`; a `RuntimeError` from `Path.home()` raises `AcfInputError`. |
| `read_store(path: Path) -> ApprovalStore` | `ApprovalStore()` when `path.is_file()` is false; otherwise `load_model_file(path, ApprovalStore, subject="approval store", fmt="json")` (`plugins/arch-compliance/python/acf/loader.py:43-77`). That is the split `load_baseline`'s docstring prescribes: *"Absence is a real state decided by the CALLER (existence check before load). The loader itself never returns None."* (`plugins/arch-compliance/python/acf/baseline.py:81-82`). Every refusal is that loader's `AcfInputError`. |
| `approval_rows(registry) -> list[Mandate]` | `registry.host_rows(TIER1_CALL_SITES)` sorted by `id`. Consumed by `check_approval` and `acf-allow`. |
| `file_digests(repo: Path, rows) -> dict[str, str]` | For each distinct path part (`parse_host_detector_ref`), the SHA-256 hex of `RepoTree(repo).file(rel).read_bytes()`. `file` returning `None`, or an `OSError` from `file` or `read_bytes`, raises `AcfInputError` naming the path. |
| `fingerprint(rows, digests) -> str` | SHA-256 hex of `json.dumps({"rows": [m.model_dump(mode="json") for m in rows], "files": digests}, sort_keys=True, separators=(",", ":"))`. Every value is JSON-native (Decision 5), so the text is the same in every process. |
| `ApprovalState` | `enum.Enum`: `NOT_NEEDED`, `APPROVED`, `MISSING`, `STALE`, `STORE_IN_REPO`. |
| `Approval` | Frozen dataclass: `state: ApprovalState`, `digests: dict[str, str]` (empty unless `APPROVED`). |
| `check_approval(repo, registry, call_sites: frozenset[str]) -> Approval` | `NOT_NEEDED` when `registry.host_rows(call_sites)` is empty. Otherwise, with `rows = approval_rows(registry)` (every active host row, whatever `call_sites` is, so the hook, the diff gate and `acf-allow` compute one fingerprint): `STORE_IN_REPO` when the store is contained in the repository; else `digests = file_digests(repo, rows)` and `APPROVED`, `MISSING` or `STALE` by comparing `fingerprint(rows, digests)` with the store entry. |
| `require_approval(repo, registry, call_sites) -> Approval` | Returns `check_approval(...)` when it is `NOT_NEEDED` or `APPROVED`; raises `AcfInputError` when it is `MISSING`, `STALE` or `STORE_IN_REPO`. Message: `host detectors need approval: <reason>; rows: <ids>. Ask the user to review the detector files and run acf-allow; a CI workflow, or a run with --mandates naming another file, passes --trusted-checkout.` |
| `write_approval(repo, registry, *, revoke: bool = False) -> None` | Reads the store, sets or removes the repository's entry (`approved` is an ISO-8601 UTC timestamp), writes `model_dump_json` to a temporary file in the same directory and moves it into place with `os.replace`, creating `~/.acf/` when missing. An `OSError` raises `AcfInputError` naming the path. Adjacent to `save_baseline` (`baseline.py:68-75`), which writes an in-repository artifact in place and raises `BaselineError`; the approval store is a per-user file read and rewritten by concurrent processes, so it is replaced whole rather than written in place, and no helper is shared. |

Repository paths go through `RepoTree` (`ARCHITECTURE.md:125-130`: *"Callers hand it the string they hold and never join, resolve or compare against the root themselves"*); the store path is compared with the repository only through `RepoTree.contained`.

### 4.3 `acf-allow` (new console script, `plugins/arch-compliance/python/acf/cli_allow.py`)

`pyproject.toml:18-20` gains `acf-allow = "acf.cli_allow:main"`, the `acf.cli_<name>:main` shape of the two existing scripts.

- `main(argv: list[str] | None = None) -> int`; arguments `--repo PATH` and `--revoke`; the repository is `resolve_repo(args.repo)`, as in `cli_check_diff.main` (`cli_check_diff.py:76`), so no new path resolution enters the module.
- Loads the registry through `load_gate_registry(repo, repo / MANDATES_REL)`, a new function in `plugins/arch-compliance/python/acf/detectors/__init__.py` that returns `load_mandates(mandates_path, known_detectors=KNOWN_DETECTORS, llm_prompt_ids=LLM_PROMPT_IDS, repo_root=repo)` and imports `LLM_PROMPT_IDS` from `acf.judge` inside the function, so the hook's import of `acf.detectors` gains no `httpx`. `cli_check_diff.main` calls the same function (`cli_check_diff.py:84-89` today), so `acf-allow` and the diff gate refuse the same registries. The hook keeps its own call (`posttooluse_gate.py:110`), which passes no prompt ids. A missing or unstat-able host detector file is refused with `UnknownDetectorError` (`registry.py:160-172`).
- No approval rows: says so, exits `0`, writes nothing.
- Store inside the repository: prints the refusal, exits `1`.
- Otherwise prints, per row, `id` and `detector`; per file, its repository-relative path and SHA-256 from `file_digests`; then the imported-helper limit of §3; writes the approval; exits `0`.
- `--revoke`: removes the entry if present, says what it did, exits `0`.
- `AcfInputError` or `UnknownDetectorError`: message to stderr, exit `1`.

### 4.4 Source-only loading (`plugins/arch-compliance/python/acf/detectors/host.py`)

`load_host_detector(repo_root, detector, *, expected_sha256: str | None = None)` passes `loader=_SourceOnlyLoader(name, str(module_path), expected_sha256)` to `importlib.util.spec_from_file_location` (`host.py:78`). `_SourceOnlyLoader` subclasses `importlib.machinery.SourceFileLoader` and overrides `get_code(self, fullname)`: it reads `data = self.get_data(self.path)` once, raises `ImportError("changed since approval")` when `expected_sha256` is set and `hashlib.sha256(data).hexdigest()` differs, and returns `compile(data, self.path, "exec", dont_inherit=True)`. The `ImportError` becomes `UnknownDetectorError` through the existing handler (`host.py:85-93`). The check runs at a module's first load in a process; a module already in `sys.modules` (`host.py:80-81`) is reused, which is safe for the hook and the diff gate because each run is its own process. No `.pyc` in `__pycache__/` is read for the detector file, and the bytes compiled are the bytes checked.

`scan_host_ast_file` and `scan_host_guards` gain `digests: Mapping[str, str] | None = None` and pass `expected_sha256=digests[rel_path]` for each row when `digests` is not `None`. The hook passes the `Approval.digests` it holds when approved; the diff gate passes `require_approval(...).digests` when approved and `None` with `--trusted-checkout`.

Committed probe: `docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/pyc_probe.py`, output in `pyc_probe.out`, shows the default loader running an unchecked hash-based `.pyc` and the source-only loader running the source; §6.2 turns it into a test.

### 4.5 PostToolUse hook (`plugins/arch-compliance/hooks/posttooluse_gate.py`)

1. After `load_mandates` succeeds (`:109-113`), compute `approval = check_approval(repo, registry, HOOK_CALL_SITES)` inside the same `try`; its `AcfInputError` is handled like a malformed registry.
2. `_scan_paths(repo, paths, registry, *, run_host: bool, digests: Mapping[str, str] | None)` skips the three host calls (`:273-277`, `:283-287`, `:292-294`) when `run_host` is false and otherwise passes `digests` to them; `run_host` is `approval.state in {NOT_NEEDED, APPROVED}` and `digests` is `approval.digests`. `rel_paths` and `file_lines` are filled before the host calls (`:243-250`) and the built-in calls read only them.
3. For `MISSING`, `STALE` or `STORE_IN_REPO`, one notice: `acf: host detectors not run: <reason>; rows skipped: <ids>. Ask the user to review the detector files and run acf-allow in this repository; do not run it yourself.`
4. Delivery: `hook` format without a BLOCK finding prepends the notice to `additionalContext` (`:137-147`) and sets a top-level `systemMessage` *(external: the hooks reference lists `systemMessage` among the JSON fields any hook may return, shown to the user)*; `hook` format with a BLOCK finding prints it to stderr before the findings (`:130-133`); `text` and `json` formats print it to stderr, leaving stdout parseable.
5. Exit codes (Decision 10): each of the four returns of §1.2 becomes `return 2 if out_format == "hook" else 1` (`out_format` is set at `:68-72`, before the first). The code after `:72` runs inside `try: … except Exception as exc:` that, in `hook` format, prints `acf: internal error: <type>: <message>` and the traceback to stderr and returns `2`, and otherwise re-raises. The handler carries the `fail-loud.bare-except-ok` exemption token (`config/architecture/mandates.yml:60`) with that reason, since it reports rather than swallows.
6. The module docstring (`:9-14`) states the approval rule and the exit codes.

### 4.6 Diff gate (`plugins/arch-compliance/python/acf/cli_check_diff.py`)

1. `--trusted-checkout` (store true): *"Run host detectors without a local approval. For CI checkouts, where the workflow file is the opt-in."*
2. Inside the existing `try` (`:83-100`), the registry comes from `load_gate_registry` (§4.3); after the empty-selection refusal, `digests = None if args.trusted_checkout else require_approval(repo, registry, sites).digests`, passed through `_scan_changed` to the host runners. The `AcfInputError` is caught at `:98` and exits `1`, like every other refusal there.

### 4.7 Shared loader (`plugins/arch-compliance/python/acf/loader.py`)

`load_model_file` (`:43-77`) catches `OSError` around `read_text` (`:59-62`) and `yaml.YAMLError`/`json.JSONDecodeError` around the parse (`:63-66`). It also catches `UnicodeDecodeError` at the read and `ValueError` and `RecursionError` at the parse (`json.JSONDecodeError` is a `ValueError`), each raised as `AcfInputError` naming the path. `plugins/arch-compliance/tests/test_loader.py` gains one case each: a non-UTF-8 file, a JSON integer longer than Python's digit limit, and nesting deeper than the recursion limit.

### 4.8 Doctrine and prose

| File | Change |
| --- | --- |
| `config/architecture/ARCHITECTURE.md:175-180` (`**Trust boundary.**`) | Both gates run host rows only when `~/.acf/approvals.json` holds an approval matching the fingerprint of the active host rows and their files (`acf-allow`), or, for `acf-check-diff`, when the invocation passes `--trusted-checkout`; the hook runs built-ins and reports skipped rows without one; the diff gate refuses. Keep the confinement and `load_mandates` sentences. Add: in hook mode, gate failures exit `2`. The closing line (`:182`) gains `test_approval.py` and `test_cli_allow.py`. |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md:16-25` (steps) | After step 7, a step: when `mandates.yml` has host rows, show the user the detector files and ask them to run `acf-allow` themselves; the agent never runs `acf-allow` or adds `--trusted-checkout`. |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md:148`, `:150` | `.acf/enabled` turns on the hooks for built-in detectors; host detectors also need each person's `acf-allow`. Committing `.acf/` approves no host code. |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md:159` (PostToolUse row) | Host detectors and host guards run only with an approval. |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md:164`, `:182-196` (manual smoke, pre-commit snippet) | With host rows, these runs need each person's `acf-allow`; the pre-commit snippet carries no `--trusted-checkout`. |
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
| `plugins/arch-compliance/python/acf/registry.py` | `Mandate.is_host_row`, `_json_params`, `host_rows` (§4.1) |
| `plugins/arch-compliance/python/acf/detectors/__init__.py` | `load_gate_registry` (§4.3) |
| `plugins/arch-compliance/python/acf/detectors/host.py` | selector use (§4.1), `_SourceOnlyLoader` and `digests` (§4.4) |
| `plugins/arch-compliance/python/acf/loader.py` | typed decode and parse failures (§4.7) |
| `plugins/arch-compliance/hooks/posttooluse_gate.py` | §4.5 |
| `plugins/arch-compliance/python/acf/cli_check_diff.py` | §4.6 |
| `plugins/arch-compliance/hooks/hooks.json` | description (§4.8) |
| `pyproject.toml`, `plugins/arch-compliance/.claude-plugin/plugin.json` | script, version |
| `config/architecture/ARCHITECTURE.md`, `plugins/arch-compliance/skills/acf-setup/SKILL.md`, `plugins/arch-compliance/skills/acf-mandate/SKILL.md`, `README.md`, `docs/guides/SUPERPOWERS_COMPLEMENT.md` | §4.8 |
| `plugins/arch-compliance/tests/test_approval.py` (new), `plugins/arch-compliance/tests/test_cli_allow.py` (new), `plugins/arch-compliance/tests/test_hooks.py`, `plugins/arch-compliance/tests/test_diff_cli.py`, `plugins/arch-compliance/tests/test_host_detectors.py`, `plugins/arch-compliance/tests/test_registry.py`, `plugins/arch-compliance/tests/test_loader.py` | §6 |

Recipe after implementation: `git diff --stat main -- plugins/arch-compliance/python plugins/arch-compliance/hooks` lists the runtime rows of this table.

---

## 6. Tests

Subprocess tests set `HOME` and `USERPROFILE` to a directory under `tmp_path` beside (not inside) the seeded repository; in-process tests monkeypatch `Path.home`. No test touches the real store.

### 6.1 Existing tests that run a gate with host rows

Population at `0da9864`, by two methods whose outputs agree. (1) The AST census `docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/host_row_gate_tests.py` lists each test function that both runs a gate (the hook or `acf-check-diff`) and builds a host row, matching a detector string by shape (`<path>.py:` followed by an identifier or an f-string field) as well as the current helper names, and following module-level helpers and pytest fixtures one level deep; its committed output is `host_row_gate_tests.out`. (2) As a cross-check of the builders the census expands from, `git grep -n "\.py:[A-Za-z_{]" -- plugins/arch-compliance/tests tests` prints the host-row builders `_host_row` (`test_hooks.py`) and `_host_rows` (`test_diff_cli.py`) and lines in `test_host_detectors.py` and `test_registry.py`, which call the runners or `load_mandates` directly and never a gate. A host row spelled another way (string concatenation, a YAML fixture file) is outside both methods.

| Test | Disposition |
| --- | --- |
| `plugins/arch-compliance/tests/test_diff_cli.py:350` `test_host_ast_and_guard_rows_run_at_ci_and_block` | Seed an approval with `write_approval`; assertions unchanged. |
| `test_diff_cli.py:367` `test_host_guard_exemption_token_on_a_non_code_file_is_honoured` | Same. |
| `test_diff_cli.py:379` `test_host_guard_only_row_at_precommit_passes_selection_and_reports` | Same. |
| `plugins/arch-compliance/tests/test_hooks.py:406` `test_gate_disabled_does_not_import_a_host_module` | Unchanged: no `.acf/enabled`, so the hook returns before any approval is read. |
| `test_hooks.py:440` `test_gate_runs_hook_host_rows_and_not_ci_only_host_guards` | Seed an approval; assertions unchanged. |
| `test_hooks.py:464` `test_gate_edited_file_outside_repo_yields_no_finding_and_no_host_call` | Same. |
| `test_hooks.py:488` `test_gate_native_absolute_path_is_reported_under_its_posix_key` | Same. |

How each listed test fails if left unseeded: `test_diff_cli.py:350`, `:367` and `:379` parse an empty stdout as JSON after the refusal; `test_hooks.py:440`, `:464` and `:488` assert host findings or host-call log entries that an unapproved run never produces. A test asserting only an exit code would not show the difference, so the §6.3 and §6.4 tests for unapproved runs assert the notice or refusal text.

### 6.2 `test_approval.py` (new) and `test_host_detectors.py`

- `fingerprint` changes when a host row's `params` change, when a host row is added, when a detector file's bytes change, and when a `[ci]`-only host row changes; it does not change when a built-in row changes.
- `fingerprint` of one registry is identical in subprocesses run with `PYTHONHASHSEED` `1`, `2` and `3`.
- `check_approval(..., call_sites)` is `NOT_NEEDED` for `DIFF_CALL_SITES` when every host row is `[hook]`-only, and the hook's and the diff gate's `APPROVED` results come from one `write_approval` when the registry also has a `[ci]`-only host row.
- `check_approval`: `NOT_NEEDED`, `MISSING`, `APPROVED` (with the per-file digests) after `write_approval`, `STALE` after editing a detector file, `STORE_IN_REPO` with `HOME`/`USERPROFILE` inside the repository.
- `store_path` raises `AcfInputError` when `Path.home` raises `RuntimeError` (monkeypatched).
- `read_store`: a missing file gives an empty store; invalid JSON and a wrong shape each raise `AcfInputError` naming the path.
- `write_approval(..., revoke=True)` removes only that repository's entry.
- `file_digests` raises `AcfInputError` when a named file cannot be read.
- `test_host_detectors.py`: a detector whose `__pycache__/` holds an unchecked hash-based `.pyc` (`py_compile.compile(..., invalidation_mode=PycInvalidationMode.UNCHECKED_HASH)`) compiled from different source runs the source, not the `.pyc`.
- `test_host_detectors.py`: with `digests` set, a detector file whose bytes differ from its digest is refused with `UnknownDetectorError` naming `changed since approval`, and its module code does not run.
- The `registry.host_rows` selector: `scan_host_ast_file` and `scan_host_guards` keep their existing test results (`test_host_detectors.py`).
- `test_registry.py`: `load_mandates` refuses a row whose `params` hold a YAML `!!set`, a date, a `!!binary` value, a nested integer key or `.nan`, each naming the row (a top-level integer key stays refused by pydantic's `dict[str, Any]`); JSON-native `params` (strings, numbers, booleans, null, lists, string-keyed maps) load as before.
- `test_loader.py`: a non-UTF-8 file, an over-long JSON integer and over-deep nesting each raise `AcfInputError` naming the path.

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
| The notice on every edit is noise for someone who never wants host detectors at edit time; with only host `ast` rows it appears even on edits that would make no host call (a `.md` file). | Accepted for this version. |
| A host's pre-commit hook running `acf-check-diff` is refused until that person runs `acf-allow`. | Each developer approves once per change to the host rows or files; the refusal names the command. |
| A registry whose `params` hold a non-JSON value (a YAML set, date or binary value, a non-string key) stops loading. | The refusal names the row; the bundled profiles and this repository's `mandates.yml` hold none (`git grep -n "!!\|[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}" -- config/architecture/mandates.yml plugins/arch-compliance/profiles` prints nothing). |
| CRLF and LF checkouts of one file hash differently. | The approval is per clone, so only that clone's bytes matter. |
| Concurrent `acf-allow` runs lose one write, or Windows refuses `os.replace` while the store is open. | A lost entry shows up as the notice and is fixed by re-running; the `OSError` is an `AcfInputError` naming the path. |

---

## 8. Acceptance

1. All tests pass, including §6.
2. In a scratch host with `.acf/enabled`, a host row and no approval: an edit through Claude Code shows the notice and makes no host call; `acf-check-diff --call-site precommit` is refused; after `acf-allow` both run the host row; after editing the detector file both are back to unapproved.
3. The diff gate on this branch (`PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main --call-site ci`) exits `0`.
4. `pyproject.toml:3` and `plugins/arch-compliance/.claude-plugin/plugin.json:3` read `"0.2.5"`.
