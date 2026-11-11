# Host Detector Local Approval and Hook Failure Visibility

**Status:** Draft (v1)
**Date:** 2026-11-11
**Spec kinds:** `defect`
**Repo:** `IanDBallard/arch-compliance-for-superpowers`, `main` at `0da9864` (branch `feat/host-detector-approval`).
**Issues:** #29 (a committed `.acf/enabled` opts every clone into running host code on edit), #30 (PostToolUse gate-input failures exit 1, which the agent does not see).
**Governing mandates:** `config/architecture/ARCHITECTURE.md` sections `## Fail loud` (`:25-42`), `## One base exception` (`:107-111`), `## One owner for host paths` (`:113-139`), `## Host detectors and call sites` (`:141-182`), `## No completeness claims` (`:225-235`), `## Declared text decoding` (`:237-248`), `## Release discipline` (`:250-260`).
**No state-machine surface.** This design adds or modifies no state machine and no transition.

---

## 0. Citation convention

Unprefixed paths refer to this repository. Every cited line is as at `main` `0da9864`; the branch adds only this file (recipe: `git diff --stat 0da9864 HEAD -- . ':!docs'` prints nothing). Every path is written in full with POSIX forward slashes. One external document is cited, the Claude Code hooks reference (`https://code.claude.com/docs/en/hooks`), for the meaning of a PostToolUse hook's exit code and JSON output fields; it is `external` and is quoted where it is relied on.

---

## 1. Problem

### 1.1 The approval to run host code travels with the code (#29)

The PostToolUse hook is registered by the plugin, not by the host: `plugins/arch-compliance/hooks/hooks.json:16-27` runs `posttooluse_gate.py --format hook` on every `Write|Edit|MultiEdit`. A user installs the plugin once, so the hook fires in every repository that user opens.

The only check between "plugin installed" and "this repository's Python runs" is a file in the repository's working tree:

- `plugins/arch-compliance/hooks/posttooluse_gate.py:74-83` returns `0` when `.acf/enabled` (`plugins/arch-compliance/python/acf/repo.py:29`, `ENABLED_REL`) is not a file. Past that check, `_scan_paths` calls `scan_host_ast_file` (`posttooluse_gate.py:273-277`, `:283-287`) and `scan_host_guards` (`:292-294`).
- Those runners import the file a host row names and call it in the hook's own process: `load_host_detector` (`plugins/arch-compliance/python/acf/detectors/host.py:53-95`) runs `spec.loader.exec_module(mod)` (`:81`) and the runners call the returned callable.
- The doctrine records this as the trust boundary and states the consequence: *"The PostToolUse hook runs host code only when `.acf/enabled` exists; committing `.acf/` therefore opts every clone in"* (`config/architecture/ARCHITECTURE.md:175-176`). It also states what the wrapping does not give: *"The wrapping guarantees typed errors, not confinement: a host module runs in the gate's process with its privileges"* (`:178-180`).
- The setup skill recommends committing the marker: *"Suggest adding `.acf/` to git if the team wants hooks enabled for everyone"* (`plugins/arch-compliance/skills/acf-setup/SKILL.md:150`).

**Root cause.** The opt-in is a file the repository itself can carry. Approval and code therefore come from the same source, and a `git clone` or `git checkout` that brings a host row and its detector file can also bring the approval to run it. The hook has no state outside the working tree that could record a person's approval of particular code.

**Consequences, in order of likelihood:**

1. Checking out a contributor's branch locally and asking the agent to edit any file runs that branch's detector code with the user's privileges. This holds in a repository the user trusts, because the code changed after the user last looked at it.
2. Cloning an unfamiliar repository that commits `.acf/enabled` and a host row runs that repository's code on the agent's first edit, with no step by the user beyond asking for an edit.
3. A host detector's finding messages reach the agent's context (`posttooluse_gate.py:137-147`, `additionalContext`; `:132`, stderr on exit 2), so an unapproved detector also writes text the agent reads.

Before host detectors existed, a committed marker enabled only the plugin's own detectors, configured through row `params`; host rows are what turned the marker into permission to run code.

### 1.2 A gate-input failure in the hook reaches the user but not the agent (#30)

`posttooluse_gate.py` returns `1` on four gate-input failures, whatever the output format:

| Line | Condition |
| --- | --- |
| `:85-91` | `.acf/enabled` present, `config/architecture/mandates.yml` missing |
| `:99-107` | the `acf` package's dependencies cannot be imported |
| `:109-113` | `load_mandates` raises `AcfInputError` or `UnknownDetectorError` |
| `:116-120` | `_scan_paths` raises `AcfInputError`, `DetectorPackError` or `UnknownDetectorError` (an unloadable or failing host detector, among others) |

The hook already relies on exit `2` being the code whose stderr reaches the agent: *"Exit 2 feeds stderr back to Claude as blocking feedback."* (`posttooluse_gate.py:131`), and `hooks.json:2` describes the hook as *"PostToolUse Tier-1 gate (exit 2 on BLOCK findings)"*. The Claude Code hooks reference (external) states that for PostToolUse an exit code of 2 shows stderr to Claude, the tool having already run, and that other non-zero exit codes show stderr to the user only. So the agent that made an edit is not told the gate could not run, and it keeps editing as though the gate had passed. `## Fail loud` requires *"Errors must surface"* (`ARCHITECTURE.md:27`); in hook mode, surfacing to the user alone does not reach the actor whose edit is being gated.

**Root cause.** The exit code was chosen for the text-mode contract (a script or a person reads exit `1`) and carried into hook mode unchanged; the hook-mode return paths above share the text-mode code.

---

## 2. Decisions

1. **The `.acf/enabled` marker keeps its meaning for built-in detectors and stops being sufficient for host code.** With the marker present the hook runs built-in detectors as today. It runs a host `ast` or `guard` row only when a local approval (Decision 2) matches the current host rows and detector files.
2. **The approval is per user, outside the repository, and bound to a fingerprint.** It lives in one JSON store at `Path.home() / ".acf" / "approvals.json"`, keyed by the repository root `RepoTree(repo).root.as_posix()`. Each entry records a fingerprint (Decision 3). A store the repository could supply is refused: when `RepoTree(repo).contained(str(store_path))` is not `None`, the hook treats the repository as unapproved and says why (§4.3).
3. **The fingerprint covers the host rows the hook would run and the files they name.** Rows: those `registry.active(HOOK_CALL_SITES)` returns with `detection` in `{"ast", "guard"}` and `is_host_detector_ref(m.detector)` true. Files: the path part of each row's `detector`. Any change to such a row (its whole `model_dump(mode="json")`), any added or removed such row, or any change to such a file's bytes changes the fingerprint and lapses the approval. A host row that declares only diff sites (`ci`, `precommit`) is outside the fingerprint, because the hook does not run it.
4. **One approval command, `acf-allow`.** It prints each fingerprinted row (id, detector) and each named file with its SHA-256, then writes the approval. `acf-allow --revoke` removes the repository's entry. It refuses when a named file is missing or when the store lies inside the repository.
5. **An unapproved repository is governed by built-ins and told so, not blocked.** When host rows exist and the approval is missing or stale, the hook skips every host row, runs the built-ins, and reports one notice to the agent and to the user naming the rows skipped and the command to run. It does not exit non-zero for this reason alone.
6. **The diff gate is unchanged.** `acf-check-diff` runs host rows whenever the host's own pre-commit or CI configuration invokes it; that invocation stays the opt-in (`ARCHITECTURE.md:176-178`). No approval is read or required there.
7. **Hook-mode gate-input failures exit 2.** When the output format is `hook`, the four returns of §1.2 return `2` with the same stderr message. Text and JSON formats keep exit `1`.

---

## 3. Non-goals and residual exposure

- **Not confinement.** An approved detector still runs with the user's privileges (`ARCHITECTURE.md:178-180`). Approval answers "did this person agree to run this code", not "is this code safe".
- **Imported helpers are outside the fingerprint.** A detector file that imports another repository module is re-approved only when the detector file, a fingerprinted row, or the row set changes. A change confined to an imported helper runs under the existing approval. `acf-allow` prints this limit beside the file list.
- **An agent or process that can write the user's home directory can write the store.** So can an agent permitted to run `acf-allow`. Either is equivalent to that actor running code, which Claude Code's own tool permissions govern; this design does not add a second permission layer above them.
- **A repository that can set the hook's environment can already run commands.** A committed Claude Code settings file can set environment variables and declare hooks of its own; Claude Code's folder trust governs that. Decision 2's containment check refuses the one case where such an environment points `Path.home()` at a store the repository itself supplies.
- **The SubagentStart hook** (`plugins/arch-compliance/hooks/inject_constraints.py`) runs no host code (recipe: `grep -n "acf.detectors\|scan_host\|load_host_detector" plugins/arch-compliance/hooks/inject_constraints.py` prints nothing; its three `host` matches, `:2`, `:6`, `:13`, name the host repository) and keeps its exit codes; #30 names the PostToolUse hook only.
- **No shared or team-wide approval.** A team that wants host detectors on for every member has each member run `acf-allow`; a committed approval would reintroduce §1.1.

---

## 4. Design

### 4.1 `acf.approval` (new module, `plugins/arch-compliance/python/acf/approval.py`)

Standard library plus `acf.repo`, `acf.registry` and `acf.exceptions`. It is imported only after the hook has imported its third-party dependencies (`posttooluse_gate.py:93-107`), so the hook's no-marker path (`:74-83`) still imports nothing beyond `acf.repo`.

| Name | Contract |
| --- | --- |
| `STORE_REL = Path(".acf") / "approvals.json"` | Relative to `Path.home()`. |
| `store_path() -> Path` | `Path.home() / STORE_REL`. |
| `hook_host_rows(registry: MandateRegistry) -> list[Mandate]` | Decision 3's rows, sorted by `id`. |
| `fingerprint(repo: Path, rows: list[Mandate]) -> str` | SHA-256 hex of `json.dumps({"rows": [m.model_dump(mode="json") for m in rows], "files": {rel: digest}}, sort_keys=True, separators=(",", ":"))`, where `rel` is each distinct path part from `parse_host_detector_ref` and `digest` is the SHA-256 hex of `RepoTree(repo).file(rel).read_bytes()`, or `None` when `file` returns `None`. |
| `ApprovalState` | `enum.Enum` with `NOT_NEEDED` (no rows), `APPROVED`, `MISSING` (no entry), `STALE` (entry, different fingerprint), `STORE_IN_REPO` (Decision 2's refusal). |
| `approval_state(repo: Path, registry: MandateRegistry) -> ApprovalState` | Computes rows; `NOT_NEEDED` when empty; `STORE_IN_REPO` when the store is contained in the repository; reads the store (missing file means no entries); compares fingerprints. |
| `read_store(path: Path) -> dict[str, dict[str, str]]` | `{}` when the file does not exist. Reads with `encoding="utf-8"`. Raises `AcfInputError` naming the path when the JSON does not parse or is not `{"version": 1, "repos": {<str>: {"fingerprint": <str>, "approved": <str>}}}`. An `OSError` other than not-found is re-raised as `AcfInputError` naming the path. |
| `write_approval(repo: Path, registry: MandateRegistry, *, revoke: bool = False) -> None` | Reads the store, sets or removes the repository's entry (`approved` is an ISO-8601 UTC timestamp), and writes by `os.replace` from a temporary file in the same directory, creating `~/.acf/` when missing. |

Every path into the repository goes through `RepoTree` (`ARCHITECTURE.md:125-128`); the store path is under the home directory, not the repository, and is compared against the repository only through `RepoTree.contained`.

### 4.2 `acf-allow` (new console script, `plugins/arch-compliance/python/acf/cli_allow.py`)

`pyproject.toml:18-20` gains `acf-allow = "acf.cli_allow:main"`.

- Arguments: `--repo PATH` (default `resolve_repo(None)`), `--revoke`.
- Loads the registry as the hook does (`load_mandates(MANDATES_REL under the repo, known_detectors=KNOWN_DETECTORS, repo_root=repo)`).
- No rows: prints that the repository has no host rows the hook would run, exits `0`, writes nothing.
- Store inside the repository: prints the refusal, exits `1`.
- A named file missing (`fingerprint` would record `None`): names it, exits `1`, writes nothing.
- Otherwise prints, per row, `id` and `detector`; per file, its repository-relative path and SHA-256; then the imported-helper limit of §3; writes the approval; exits `0`.
- `--revoke`: removes the entry if present, prints what it did, exits `0`.
- `AcfInputError` from the store or the registry: message to stderr, exit `1`.

### 4.3 PostToolUse hook changes (`plugins/arch-compliance/hooks/posttooluse_gate.py`)

1. After `load_mandates` succeeds (`:109-113`), compute `state = approval_state(repo, registry)` inside the same `try`, so a malformed store is an `AcfInputError` handled like a malformed registry.
2. `_scan_paths(repo, paths, registry, *, run_host: bool)`: when `run_host` is false, the three host calls (`:273-277`, `:283-287`, `:292-294`) are skipped. `run_host` is `state in {NOT_NEEDED, APPROVED}`.
3. When `state` is `MISSING`, `STALE` or `STORE_IN_REPO`, build one notice: `acf: host detectors not run: <reason>; rows skipped: <ids>. Review the detector files, then run acf-allow in this repository.` The reason is `no local approval`, `host rows or detector files changed since approval`, or `approval store is inside this repository`.
4. Notice delivery:
   - `hook` format, no BLOCK finding: the notice is prepended to `additionalContext` (`:137-147`) and also set as the top-level `systemMessage` field. The Claude Code hooks reference (external) lists `systemMessage` among the JSON fields every hook may return, as a message shown to the user.
   - `hook` format, a BLOCK finding: the notice is printed to stderr before the findings (`:130-133`).
   - `text` and `json` formats: the notice is printed to stderr; stdout is unchanged, so JSON output stays parseable.
5. Exit codes (Decision 7): each of the four returns in §1.2 becomes `return 2 if out_format == "hook" else 1`. `out_format` is computed at `:68-72`, before the first of them.

### 4.4 Doctrine and prose

| File | Change |
| --- | --- |
| `config/architecture/ARCHITECTURE.md:175-180` (`**Trust boundary.**`) | Replace the first sentence: the hook runs built-in detectors when `.acf/enabled` exists and host rows only when a local approval in `~/.acf/approvals.json` matches the fingerprint of the hook's host rows and their files (`acf-allow`); an unapproved repository runs built-ins and reports the skipped rows. Keep the `acf-check-diff` sentence, the confinement sentence and the `load_mandates` sentence. Add: in hook mode, gate-input failures exit `2`. Add `test_approval.py` and `test_cli_allow.py` to the section's closing `No row: enforced by …` line (`:182`). |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md:148` | `.acf/enabled` turns on the automatic hooks for built-in detectors; host detectors also need `acf-allow`, run by each person in their own clone after reading the detector files. |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md:150` | Committing `.acf/` turns on built-in hooks for every clone; it does not approve host code. Replace the opt-in warning with that sentence. |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md:16-25` (step list) | After step 7, a step: when `mandates.yml` has host rows the hook runs, show the user the `acf-allow` output and ask them to run it themselves. |
| `README.md:110` | Add: host detectors in the hook need `acf-allow`; in hook mode a gate-input failure exits `2` so the agent sees it. |
| `docs/guides/SUPERPOWERS_COMPLEMENT.md:87` | The same two facts. |
| `pyproject.toml:3`, `plugins/arch-compliance/.claude-plugin/plugin.json:3` | `"0.2.4"` → `"0.2.5"`, because `acf-setup`'s prose changes (`ARCHITECTURE.md:252-253`). |

---

## 5. Change surface

| Path | Change |
| --- | --- |
| `plugins/arch-compliance/python/acf/approval.py` (new) | §4.1 |
| `plugins/arch-compliance/python/acf/cli_allow.py` (new) | §4.2 |
| `plugins/arch-compliance/hooks/posttooluse_gate.py` | §4.3 |
| `pyproject.toml` | `acf-allow` script; version |
| `plugins/arch-compliance/.claude-plugin/plugin.json` | version |
| `config/architecture/ARCHITECTURE.md`, `plugins/arch-compliance/skills/acf-setup/SKILL.md`, `README.md`, `docs/guides/SUPERPOWERS_COMPLEMENT.md` | §4.4 |
| `plugins/arch-compliance/tests/test_approval.py` (new), `plugins/arch-compliance/tests/test_cli_allow.py` (new), `plugins/arch-compliance/tests/test_hooks.py` | §6 |

No other runtime file changes (recipe after implementation: `git diff --stat main -- plugins/arch-compliance/python plugins/arch-compliance/hooks` lists only the three runtime files above).

---

## 6. Tests

Hook tests run the hook in a subprocess with `HOME` and `USERPROFILE` set to a directory under `tmp_path`, so `Path.home()` resolves there on POSIX and Windows and no test touches the real store.

### 6.1 Existing hook tests that run host rows

Recipe for the population: `grep -n "_seed_host_rows(" plugins/arch-compliance/tests/test_hooks.py`. At `0da9864` it prints the helper's definition (`:391`) and the call sites below; each is listed with its disposition.

| Test | Disposition |
| --- | --- |
| `test_gate_disabled_does_not_import_a_host_module` (`test_hooks.py:406`) | Unchanged: it runs without `.acf/enabled`, so the hook returns before any approval is read. |
| `test_gate_runs_hook_host_rows_and_not_ci_only_host_guards` (`test_hooks.py:440`) | Seeds an approval with `write_approval` before running the hook; assertions unchanged. |
| `test_gate_edited_file_outside_repo_yields_no_finding_and_no_host_call` (`:464`) | Same. |
| `test_gate_native_absolute_path_is_reported_under_its_posix_key` (`:488`) | Same. |

The implementer re-runs the recipe before editing and gives any further call site the same disposition; a call site whose test means to exercise the unapproved path is instead left unseeded and its assertion moved to §6.3's expectations.

### 6.2 `test_approval.py` (new)

- `fingerprint` changes when a fingerprinted row's `params` change, when a host row is added, when a detector file's bytes change; it does not change when a `[ci]`-only host row changes or a built-in row changes.
- `approval_state`: `NOT_NEEDED` with no host hook rows; `MISSING` with an empty store; `APPROVED` after `write_approval`; `STALE` after editing the detector file; `STORE_IN_REPO` when `HOME` points inside the repository.
- `read_store`: missing file gives `{}`; invalid JSON and a wrong shape each raise `AcfInputError` naming the path.
- `write_approval(..., revoke=True)` removes only that repository's entry; a second repository's entry survives.
- Two worktree roots of one repository have separate entries.

### 6.3 `test_hooks.py` additions

- Unapproved, `hook` format: no host call is made (the detector's log file stays empty), the built-in bare-except finding is still reported, exit is `0` with no BLOCK, `additionalContext` and `systemMessage` both contain `acf-allow` and the skipped row id.
- Unapproved with a BLOCK built-in finding, `hook` format: exit `2`, stderr contains the notice and the finding.
- Stale approval (detector file edited after `write_approval`): no host call; the notice names `changed since approval`.
- Approved: host rows run as in §6.1.
- `json` format, unapproved: stdout parses as JSON; the notice is on stderr.
- `hook` format exit `2` for each row of §1.2: mandates missing; dependencies missing (`_no_deps_env`); unknown built-in detector; a host detector that raises (approved, so it runs). Each asserts the `acf:` message on stderr.
- The existing text-format exit-1 tests (`test_hooks.py:145`, `:318`, `:424`) stay as they are, pinning that text mode keeps exit `1`.

### 6.4 `test_cli_allow.py` (new)

- Prints each row id, detector and file hash, and the imported-helper limit; writes an entry; exit `0`.
- No host hook rows: exit `0`, store not created.
- Missing detector file: exit `1`, store unchanged.
- Store inside the repository: exit `1`.
- `--revoke` removes the entry.

### 6.5 Guards that must keep passing

`plugins/arch-compliance/tests/test_repo_tree_guard.py` (no new allowlist entry: the new modules resolve repository paths only through `RepoTree`), `plugins/arch-compliance/tests/test_adr_import_graph.py:70-76` (the hook gains no `acf.adr` reference), and `test_acf_repo_still_imports_without_pydantic` (`test_adr_import_graph.py:79`; `acf.repo` is unchanged).

---

## 7. Risks

| Risk | Mitigation |
| --- | --- |
| A team that relied on the committed marker loses host detectors at edit time after upgrading, silently. | Not silently: Decision 5's notice reaches both agent and user on every edit until `acf-allow` runs. The diff gate in CI is unchanged, so enforcement at merge is unaffected. |
| The notice on every edit is noise for someone who never wants host detectors at edit time. | Accepted for this version; a quieter "declined" state is a follow-up if asked for. |
| CRLF and LF checkouts of one file hash differently. | The approval is per clone, so only that clone's bytes matter. |
| Concurrent `acf-allow` runs lose one write. | `os.replace` keeps the file whole; a lost entry shows up as the notice and is fixed by re-running. |

---

## 8. Acceptance

1. All tests pass, including §6.
2. In a scratch host with `.acf/enabled`, a host row and no approval, an edit through Claude Code shows the notice and no host call; after `acf-allow` the host row runs; after editing the detector file the notice returns.
3. The diff gate on this branch (`PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main --call-site ci`) exits `0`.
4. `pyproject.toml:3` and `plugins/arch-compliance/.claude-plugin/plugin.json:3` read `"0.2.5"`.
