# Host Detector Local Approval Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Host detector rows run only with a per-user, fingerprint-bound approval (`acf-allow`) or, for the diff gate, an explicit `--trusted-checkout`; and the PostToolUse hook exits `2` on gate-input failures so the agent sees them (issues #29, #30).

**Architecture:** A new `acf.approval` module owns the store (`~/.acf/approvals.json`), the fingerprint over the active host rows and the SHA-256 of their files, and the approval check. Both gates call it: the hook skips host rows with a notice when unapproved, the diff gate refuses. Host detector files are compiled from source and, when approved, checked against the approved digest before they run.

**Tech Stack:** Python 3.11+, pydantic v2, PyYAML, pytest; `importlib.machinery.SourceFileLoader`.

**Spec:** `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md` (v4, cleared by verification pass at `86c3c36`). Section references (§) below are to the spec. Where this plan is silent, the spec governs.
**Merged:** PR #33 (`7bec270`, 2026-11-12). The final review's fix wave (`a14bddf`) added work beyond these tasks: the diff-gate `as_posix()` fixes in two tests, `write_approval` taking the printed `digests` so `acf-allow` records exactly what it showed, `{}` as the not-needed digests value in both gates, and prose fixes. Follow-ups filed: #34 (TypeScript bridge `shell=True` on Windows, spec §3), #35 (`acf-allow` prints no `params`), #36 (hook notice lists CI-only host rows).

## Global Constraints

- Version: `pyproject.toml:3` and `plugins/arch-compliance/.claude-plugin/plugin.json:3` go `"0.2.4"` → `"0.2.5"`.
- Every new failure is `AcfInputError` or `UnknownDetectorError`; no new exception class (`## One base exception`).
- Repository paths go through `RepoTree` (`file`, `contained`, `root`, `key`); never join, resolve or compare against the root by hand. `repo / MANDATES_REL` and `Path.home() / STORE_REL` are the only joins.
- Persisted paths use `as_posix()`. Text reads pass `encoding="utf-8"`.
- Messages name no host repository; they interpolate only reasons, row ids, paths of the repo being checked, and the command names `acf-allow` / `--trusted-checkout`.
- The hook's no-marker path (`posttooluse_gate.py:74-83`) imports nothing beyond `acf.repo`; `acf.approval` is imported only inside the deferred-import `try` (`:93-107`).
- Any broad `except Exception` added carries the `fail-loud.bare-except-ok` token with its reason.
- No test reads or writes the real `~/.acf/approvals.json` (Task 4 adds the fixture that guarantees it).
- On Windows run tests and the diff gate with `PYTHONUTF8=1`.
- Exact strings (copy verbatim):
  - refusal: `host detectors need approval: <reason>; rows: <ids>. Ask the user to review the detector files and run acf-allow; a CI workflow, or a run with --mandates naming another file, passes --trusted-checkout.`
  - hook notice: `acf: host detectors not run: <reason>; rows skipped: <ids>. Ask the user to review the detector files and run acf-allow in this repository; do not run it yourself.`
  - `<reason>` by state: `MISSING` → `no approval for this repository`; `STALE` → `the host rows or detector files changed since approval`; `STORE_IN_REPO` → `the approval store <store path as_posix> is inside the repository`. `<ids>` is `", ".join` of the approval rows' ids, sorted.
  - loader refusal: `ImportError("changed since approval")`.
  - hook internal error: `acf: internal error: <type>: <message>` followed by the traceback.
  - `--trusted-checkout` help: `Run host detectors without a local approval. For CI checkouts, where the workflow file is the opt-in.`

## Rulings (stricter choices within the spec)

- **R1 — the hook keeps its own `load_mandates` call** (no prompt ids). Spec §4.3 and §3 say so explicitly, and `acf.judge` imports `httpx` at module scope (`judge.py:11`), which the hook must not need. The v3 response record's item "the hook loads its registry through `load_gate_registry`" is superseded by this ruling.
- **R2 — the runners' `digests` parameter is keyword-only with no default**: `digests: Mapping[str, str] | None`. Every caller states it, so no call site runs unchecked by omission.
- **R3 — setup prose uses the `acf-check-diff` console script**, never `python -m acf.cli_check_diff`, which puts the current directory first on `sys.path` and could import a host's own `acf/` package before any check. This repository's own `CLAUDE.md` and `ci.yml` keep `python -m` (no host rows here; out of scope).
- **R4 — the `acf-mandate` skill's validation snippet** (`plugins/arch-compliance/skills/acf-mandate/SKILL.md:88-104`) calls `load_gate_registry` instead of re-spelling it.
- **R5 — test isolation of the store** is an autouse fixture that sets `HOME` and `USERPROFILE` to a fresh `tmp_path_factory.mktemp("home")` (a sibling of each test's `tmp_path`, so never inside a seeded repo) and pins `PYTHONUSERBASE` to the value `site.getuserbase()` had before, so POSIX subprocesses keep user-site packages. `Path.home()` reads those variables, so in-process and subprocess code see the same store; only the `RuntimeError` test monkeypatches `Path.home`.

## Review Focus

1. **An empty or truncated store file** (a crash mid-write by another tool, or `touch`): `read_store` refuses it with `AcfInputError` naming the path; the hook reports it on stderr and exits `2`, never a traceback. Tests: Task 4 `test_read_store_empty_file_refused`, Task 7 `test_gate_hook_empty_store_exits_2`.
2. **Two rows naming the same detector file**: one digest entry; approval and the digest check work for both rows. Test: Task 4 `test_two_rows_one_file_single_digest`.
3. **The same checkout spelled two ways** (`acf-allow --repo .` from inside the repo vs. the hook's absolute path): the key is the resolved root, so the approval matches. Test: Task 5 `test_allow_relative_repo_matches_absolute_check`.
4. **Approving one repository keeps the others**: `write_approval` for repo B leaves repo A's entry byte-identical; revoking B leaves A. Test: Task 4 `test_write_approval_preserves_other_repos`.
5. **A detector file deleted after approval**: the registry load refuses it (`UnknownDetectorError`), so the hook exits `2` with an `acf:` line naming the file, not a silent skip. Test: Task 7 `test_gate_hook_deleted_detector_file_exits_2`.

---

### Task 1: One host-row selector and JSON-only params (`registry.py`, `host.py` selectors)

**Files:**
- Modify: `plugins/arch-compliance/python/acf/registry.py:48-90` (`Mandate`), `:94-123` (`MandateRegistry`), `:144-154` (`load_mandates` loop)
- Modify: `plugins/arch-compliance/python/acf/detectors/host.py:162-166`, `:192-194` (selectors only)
- Test: `plugins/arch-compliance/tests/test_registry.py`

**Interfaces:**
- Produces: `Mandate.is_host_row -> bool` (property); `MandateRegistry.host_rows(call_sites: frozenset[str], *, detection: str | None = None) -> list[Mandate]`; `Mandate._json_params` validator.

- [x] **Step 1: Write the failing tests** in `test_registry.py`:
  - `test_is_host_row`: an `ast` row with `detector: "x.py:f"` → `True`; `ast` with `"no_shims_hasattr"` → `False`; `llm` row with a colon in `detector` → `False`.
  - `test_host_rows_filters_active_host_rows`: registry with a `[hook]` host ast row, a `[ci]` host guard row, an unenforced host row and a built-in row: `host_rows(HOOK_CALL_SITES)` → the hook row only; `host_rows(TIER1_CALL_SITES)` → both active host rows; `host_rows(TIER1_CALL_SITES, detection="guard")` → the guard row.
  - `test_non_json_params_refused` parametrized over YAML params texts `"k: !!set {a: null}"`, `"k: 2026-11-11"`, `"k: !!binary aGk="`, `"k: {1: a}"`, `"k: .nan"`: `load_mandates` on a one-row file raises `AcfInputError` whose message contains the row id.
  - `test_top_level_int_key_still_refused_by_pydantic`: `params: {1: a}` at top level raises `AcfInputError` (via the loader's `ValidationError` mapping).
  - `test_json_native_params_load`: params `{s: "x", n: 1, f: 1.5, b: true, z: null, l: [1, "a"], m: {k: [true]}}` loads and `m.params` equals the parsed value.

- [x] **Step 2: Run** `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_registry.py -q` — expected: the new tests FAIL (`AttributeError: is_host_row` / no refusal).

- [x] **Step 3: Implement** in `registry.py`:
  - `is_host_row`: `self.detection in {"ast", "guard"} and is_host_detector_ref(self.detector)`.
  - `host_rows`: `[m for m in self.active(call_sites, detection=detection) if m.is_host_row]`.
  - `_json_params` (`@model_validator(mode="after")`): when `params is not None`, compute `json.loads(json.dumps(self.params, allow_nan=False))` inside `try` catching `TypeError, ValueError, RecursionError` (unequal on any); unequal → `raise AcfInputError(f"mandate {self.id!r}: params must hold JSON values only (no YAML sets, dates, binary values, non-string keys or NaN)")`. `AcfInputError` is not a `ValueError`, so pydantic propagates it unwrapped, as it does `_row_shape`'s.
  - `_row_shape`: `host = self.is_host_row` (after the existing `detection` early return).
  - `load_mandates` loop: `builtin_row = m.detection in {"ast", "guard"} and not m.is_host_row`; the later `if not is_host_detector_ref(m.detector)` becomes `if not m.is_host_row`.
  - `host.py`: `scan_host_ast_file` selects `registry.host_rows(call_sites, detection="ast")` filtered by language; `scan_host_guards` selects `registry.host_rows(call_sites, detection="guard")`. Drop the now-unused `is_host_detector_ref` import from `host.py` if nothing else uses it.

- [x] **Step 4: Run** `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests -q` — expected: all PASS (existing `test_host_detectors.py` results unchanged, §6.2 last-but-three bullet).

- [x] **Step 5: Commit** `git commit -m "feat(registry): one host-row selector; refuse non-JSON params"`.

### Task 2: Shared loader types every bad-file failure (`loader.py`)

**Files:**
- Modify: `plugins/arch-compliance/python/acf/loader.py:59-66`
- Test: `plugins/arch-compliance/tests/test_loader.py`

**Interfaces:**
- Produces: `load_model_file` raises `AcfInputError` naming the path for non-UTF-8 text, an over-long JSON integer, and over-deep nesting.

- [x] **Step 1: Write the failing tests**:
  - `test_non_utf8_file_refused`: file bytes `b"\xff\xfe\x00"` loaded as yaml → `AcfInputError`, message contains the path's `as_posix()`.
  - `test_overlong_json_integer_refused`: JSON text `"1" * 5000` loaded as json → `AcfInputError` naming the path.
  - `test_overdeep_nesting_refused`: JSON text `"[" * 100_000 + "]" * 100_000` → `AcfInputError` naming the path.

- [x] **Step 2: Run** `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_loader.py -q` — expected: the three FAIL with `UnicodeDecodeError` / `ValueError` / `RecursionError`.

- [x] **Step 3: Implement**: read `except (OSError, UnicodeDecodeError)`; parse `except (yaml.YAMLError, ValueError, RecursionError)` (`json.JSONDecodeError` is a `ValueError`). Messages keep the existing `cannot read …` / `invalid {fmt} in …` forms. The `ValidationError` handling at `:67-77` is untouched.

- [x] **Step 4: Run** the full suite — expected: PASS.

- [x] **Step 5: Commit** `git commit -m "fix(loader): type decode, integer-limit and recursion failures as AcfInputError"`.

### Task 3: Source-only, digest-checked host loading (`host.py`)

**Files:**
- Modify: `plugins/arch-compliance/python/acf/detectors/host.py:53-95`, `:152-198`
- Modify (callers, pass `digests=None` for now): `plugins/arch-compliance/hooks/posttooluse_gate.py:273-294`, `plugins/arch-compliance/python/acf/cli_check_diff.py:167-204`
- Test: `plugins/arch-compliance/tests/test_host_detectors.py`

**Interfaces:**
- Consumes: `MandateRegistry.host_rows` (Task 1).
- Produces: `load_host_detector(repo_root: Path, detector: str, *, expected_sha256: str | None = None)`; `scan_host_ast_file(..., *, language: str, call_sites: frozenset[str], digests: Mapping[str, str] | None)`; `scan_host_guards(..., *, call_sites: frozenset[str], digests: Mapping[str, str] | None)` — `digests` required (R2); when not `None` each row passes `expected_sha256=digests[rel_path]` where `rel_path` is `parse_host_detector_ref(m.detector)[0]`.

- [x] **Step 1: Write the failing tests** (use the `fresh_host_loader` fixture):
  - `test_unchecked_hash_pyc_is_not_run`: write `g.py` defining `scan` that yields a hit with message `"source"`; compile a second source (message `"pyc"`) with `py_compile.compile(other, cfile=importlib.util.cache_from_source(str(g)), invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH)`; run `scan_host_ast_file(..., digests=None)` → the hit message is `"source"`. (Model: `docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/pyc_probe.py`.)
  - `test_changed_since_approval_refused_without_running`: module body first writes a marker file; call `load_host_detector(root, "g.py:scan", expected_sha256="0" * 64)` → `UnknownDetectorError` whose message contains `changed since approval`; the marker does not exist; `"_acf_host_…"` for it is not left in `sys.modules`.
  - `test_matching_digest_runs`: `expected_sha256=hashlib.sha256(g.read_bytes()).hexdigest()` → returns the callable.
  - `test_runners_pass_digest_per_row`: guard and ast rows with `digests={"g.py": "0"*64}` → `UnknownDetectorError` with `changed since approval`; with the true digest → findings as without digests.
  - Update every existing `scan_host_ast_file` / `scan_host_guards` call in this file to pass `digests=None`.

- [x] **Step 2: Run** `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_host_detectors.py -q` — expected: new tests FAIL (`TypeError: unexpected keyword 'digests'` / `expected_sha256`).

- [x] **Step 3: Implement**:
  - `class _SourceOnlyLoader(importlib.machinery.SourceFileLoader)` with `__init__(self, fullname: str, path: str, expected_sha256: str | None)` and `get_code(self, fullname)`: `data = self.get_data(self.path)`; when `expected_sha256` is set and `hashlib.sha256(data).hexdigest() != expected_sha256` raise `ImportError("changed since approval")`; return `compile(data, self.path, "exec", dont_inherit=True)`.
  - `load_host_detector` passes `loader=_SourceOnlyLoader(name, str(module_path), expected_sha256)` to `spec_from_file_location`. The existing handler (`:85-93`) turns the `ImportError` into `UnknownDetectorError` and pops the module.
  - Runners: add the required `digests` keyword and pass `expected_sha256` per row.
  - Hook and diff-gate callers pass `digests=None` (replaced in Tasks 6 and 7).

- [x] **Step 4: Run** the full suite — expected: PASS.

- [x] **Step 5: Commit** `git commit -m "feat(host): compile detector source only and check it against an approved digest"`.

### Task 4: `acf.approval` and store isolation for tests

**Files:**
- Create: `plugins/arch-compliance/python/acf/approval.py`
- Modify: `plugins/arch-compliance/tests/conftest.py` (autouse fixture, R5)
- Test: `plugins/arch-compliance/tests/test_approval.py` (new)

**Interfaces:**
- Consumes: `host_rows`, `TIER1_CALL_SITES`, `parse_host_detector_ref` (registry); `load_model_file`; `RepoTree`.
- Produces (exact names and contracts from §4.2): `STORE_REL`, `ApprovalEntry(fingerprint: str, approved: str)`, `ApprovalStore(version: Literal[1] = 1, repos: dict[str, ApprovalEntry] = {})` (both `extra="forbid"`), `store_path() -> Path`, `read_store(path: Path) -> ApprovalStore`, `approval_rows(registry) -> list[Mandate]`, `file_digests(repo: Path, rows) -> dict[str, str]`, `fingerprint(rows, digests) -> str`, `ApprovalState` (`NOT_NEEDED`, `APPROVED`, `MISSING`, `STALE`, `STORE_IN_REPO`), `Approval(state: ApprovalState, digests: dict[str, str])` frozen dataclass, `check_approval(repo, registry, call_sites: frozenset[str]) -> Approval`, `require_approval(repo, registry, call_sites) -> Approval`, `write_approval(repo, registry, *, revoke: bool = False) -> None`, and `reason(state: ApprovalState, store: Path) -> str` returning the Global Constraints reason text (consumed by the hook notice, the refusal and `acf-allow`).

- [x] **Step 1: Add the R5 fixture** to `conftest.py`: `@pytest.fixture(autouse=True) def _isolated_home(monkeypatch, tmp_path_factory)` that records `site.getuserbase()`, then `setenv("PYTHONUSERBASE", <recorded>)`, `setenv("HOME", home)`, `setenv("USERPROFILE", home)` with `home = tmp_path_factory.mktemp("home")`.

- [x] **Step 2: Write the failing tests** in `test_approval.py` (registries built by writing a `mandates.yml` and calling `load_mandates(..., known_detectors=KNOWN_DETECTORS, repo_root=repo)`; a helper `_repo(tmp_path, rows)` writes rows and detector files under `tmp_path / "repo"`):
  - `test_store_path_under_home`: `store_path() == Path.home() / ".acf" / "approvals.json"`.
  - `test_store_path_runtime_error_is_acf_input_error`: monkeypatch `Path.home` to raise `RuntimeError` → `AcfInputError`.
  - `test_read_store_missing_is_empty`, `test_read_store_invalid_json_refused`, `test_read_store_wrong_shape_refused` (`{"version": 1, "repos": {}, "x": 1}`), `test_read_store_empty_file_refused` (Review Focus 1): the refusals are `AcfInputError` containing the path.
  - `test_fingerprint_changes` (one assertion per bullet of §6.2 first item): host row `params` change, added host row, detector byte change, `[ci]`-only host row change → differ; built-in row change → equal.
  - `test_fingerprint_stable_across_hash_seeds`: run `python -c` printing `fingerprint(approval_rows(reg), file_digests(repo, rows))` with `PYTHONHASHSEED` `1`, `2`, `3` → one value.
  - `test_check_approval_states`: `NOT_NEEDED` (no host rows); `MISSING`; after `write_approval`, `APPROVED` with `digests == {"hostdet/rules.py": <sha256>}`; after editing the detector, `STALE` with empty `digests`; with `HOME`/`USERPROFILE` set to the repo itself, `STORE_IN_REPO`.
  - `test_not_needed_when_call_sites_select_no_host_row`: only a `[hook]` host row → `check_approval(..., DIFF_CALL_SITES).state is NOT_NEEDED`.
  - `test_one_approval_covers_hook_and_diff`: a `[hook]` and a `[ci]` host row, one `write_approval` → `APPROVED` for both `HOOK_CALL_SITES` and `DIFF_CALL_SITES`.
  - `test_require_approval_raises_with_refusal_text`: `MISSING` → `AcfInputError`; message starts `host detectors need approval: no approval for this repository; rows: ` and contains `acf-allow` and `--trusted-checkout`.
  - `test_revoke_removes_only_that_repo` and `test_write_approval_preserves_other_repos` (Review Focus 4).
  - `test_file_digests_unreadable_file_refused`: a row naming a file that `RepoTree.file` cannot find → `AcfInputError` naming the path.
  - `test_two_rows_one_file_single_digest` (Review Focus 2).

- [x] **Step 3: Run** `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_approval.py -q` — expected: FAIL (`ModuleNotFoundError: acf.approval`).

- [x] **Step 4: Implement `approval.py`** to §4.2's table. Notes the table leaves open: `approved` is `datetime.now(timezone.utc).isoformat(timespec="seconds")`; `write_approval` creates `store.parent` with `mkdir(parents=True, exist_ok=True)`, writes `model_dump_json(indent=2)` to `tempfile.NamedTemporaryFile(dir=store.parent, delete=False, suffix=".tmp", mode="w", encoding="utf-8")`, then `os.replace`; it refuses (`AcfInputError`) when the store is inside the repository; it writes the fingerprint `check_approval` would compute. Its docstring names `save_baseline` (`baseline.py:68-75`) and the reason no helper is shared (§4.2 last row).

- [x] **Step 5: Run** the full suite — expected: PASS (the fixture changes nothing for existing tests).

- [x] **Step 6: Commit** `git commit -m "feat(approval): per-user fingerprint-bound approval store"`.

### Task 5: `load_gate_registry` and `acf-allow`

**Files:**
- Modify: `plugins/arch-compliance/python/acf/detectors/__init__.py`
- Create: `plugins/arch-compliance/python/acf/cli_allow.py`
- Modify: `pyproject.toml` (`[project.scripts]`: `acf-allow = "acf.cli_allow:main"`)
- Test: `plugins/arch-compliance/tests/test_cli_allow.py` (new)

**Interfaces:**
- Produces: `load_gate_registry(repo: Path, mandates_path: Path) -> MandateRegistry` (imports `LLM_PROMPT_IDS` from `acf.judge` inside the function; add to `__all__`); `cli_allow.main(argv: list[str] | None = None) -> int`.

- [x] **Step 1: Write the failing tests** (in-process `main([...])` with `capsys`):
  - `test_allow_prints_and_writes`: output contains each row id, each detector, `hostdet/rules.py` with its SHA-256, and the imported-helper limit sentence (`imported modules are not covered`); exit `0`; `read_store(store_path()).repos` has the repo's `RepoTree(repo).root.as_posix()` key.
  - `test_allow_no_host_rows_writes_nothing`: exit `0`; store file absent.
  - `test_allow_missing_detector_file`: exit `1`; stderr names the file; store unchanged.
  - `test_allow_store_inside_repo`: `HOME`/`USERPROFILE` = repo → exit `1`; stderr contains `inside the repository`.
  - `test_allow_revoke`: after approving, `--revoke` → exit `0`, entry gone, stdout says it was removed.
  - `test_allow_relative_repo_matches_absolute_check` (Review Focus 3): `monkeypatch.chdir(repo)`, `main(["--repo", "."])`, then `check_approval(repo_absolute, registry, HOOK_CALL_SITES).state is APPROVED`.
  - `test_load_gate_registry_refuses_unknown_prompt_id`: an active `llm` row with an unknown detector → `UnknownDetectorError`.
  - `test_detectors_import_does_not_import_httpx`: subprocess `python -c "import acf.detectors, sys; print('httpx' in sys.modules)"` prints `False`.

- [x] **Step 2: Run** `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_cli_allow.py -q` — expected: FAIL.

- [x] **Step 3: Implement** `load_gate_registry` (§4.3) and `cli_allow.main` to §4.3's bullets: `--repo PATH`, `--revoke`; `repo = resolve_repo(args.repo)`; registry via `load_gate_registry(repo, repo / MANDATES_REL)`; the store-inside-repo refusal prints `acf: ` + `reason(STORE_IN_REPO, store_path())`; the helper-limit sentence is `Note: imported modules are not covered; a change confined to a module a detector imports runs under this approval.`; the home-is-repo case is the store-inside-repo case. `AcfInputError` / `UnknownDetectorError` → `acf: <message>` on stderr, exit `1`.

- [x] **Step 4: Run** `pip install -e .` (registers the script), then the full suite — expected: PASS; `acf-allow --help` prints usage.

- [x] **Step 5: Commit** `git commit -m "feat(cli): acf-allow approves the active host rows for this checkout"`.

### Task 6: Diff gate requires approval or `--trusted-checkout`

**Files:**
- Modify: `plugins/arch-compliance/python/acf/cli_check_diff.py:35-118` (`main`), `:121-205` (`_scan_changed`)
- Test: `plugins/arch-compliance/tests/test_diff_cli.py`

**Interfaces:**
- Consumes: `load_gate_registry` (Task 5), `require_approval` (Task 4), runner `digests` (Task 3).
- Produces: `--trusted-checkout`; `_scan_changed(repo, mode, base, registry, sites, *, digests: Mapping[str, str] | None)`.

- [x] **Step 1: Seed the existing host-row tests** (`test_diff_cli.py:350`, `:367`, `:379`): add helper `_approve(repo: Path) -> None` = `write_approval(repo, load_gate_registry(repo, repo / MANDATES_REL))`, called after `_host_repo(...)` in each; assertions unchanged.

- [x] **Step 2: Write the failing tests**:
  - `test_host_rows_unapproved_refused`: exit `1`; stderr contains `acf-allow` and `--trusted-checkout`; the host module's side-effect marker absent.
  - `test_host_rows_trusted_checkout_runs`: `--trusted-checkout`, no approval → same findings as `test_host_ast_and_guard_rows_run_at_ci_and_block`.
  - `test_host_rows_approved_runs_without_flag`.
  - `test_no_host_rows_no_approval_unchanged`: a built-in-only registry runs as before.
  - `test_hook_only_host_row_does_not_refuse_ci`: a `[hook]` host row and a built-in `[ci]` row, no approval, `--call-site ci` → not refused (exit per built-in findings).
  - `test_stale_approval_refused`: approve, edit the detector file, run → exit `1`, stderr contains `changed since approval`.

- [x] **Step 3: Run** `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_diff_cli.py -q` — expected: new tests FAIL (no refusal / unknown flag); seeded tests PASS.

- [x] **Step 4: Implement** per §4.6: add the flag; replace the `load_mandates(...)` call with `load_gate_registry(repo, mandates_path)` and drop the module-level `LLM_PROMPT_IDS` import; after the empty-selection refusal, `digests = None if args.trusted_checkout else require_approval(repo, registry, sites).digests`; thread `digests` through `_scan_changed` to both runners. The refusal is caught by the existing `except` (`:98`).

- [x] **Step 5: Run** the full suite — expected: PASS.

- [x] **Step 6: Commit** `git commit -m "feat(diff): refuse unapproved host rows unless --trusted-checkout"`.

### Task 7: PostToolUse hook — skip-with-notice and exit 2

**Files:**
- Modify: `plugins/arch-compliance/hooks/posttooluse_gate.py` (docstring `:1-15`; `main` `:40-157`; `_scan_paths` `:223-295`)
- Test: `plugins/arch-compliance/tests/test_hooks.py`

**Interfaces:**
- Consumes: `check_approval`, `reason`, `ApprovalState` (Task 4); runner `digests` (Task 3).
- Produces: `_scan_paths(repo, paths, registry, *, run_host: bool, digests: Mapping[str, str] | None)`.

- [x] **Step 1: Seed the existing host-row tests** (`test_hooks.py:440`, `:464`, `:488`): helper `_approve(repo: Path) -> None` as in Task 6, called after `_seed_host_rows(...)`; `:406` unchanged.

- [x] **Step 2: Write the failing tests** (hook payload on stdin: `{"hook_event_name": "PostToolUse", "cwd": <repo>, "tool_input": {"file_path": <path>}}`):
  - `test_gate_unapproved_hook_skips_host_rows_with_notice`: no host log entries; a built-in WARN finding still in `additionalContext`; exit `0`; `additionalContext` and `systemMessage` both contain `acf-allow` and `host.ast-marker`.
  - `test_gate_unapproved_hook_block_exits_2_with_notice`: a bare-except edit → exit `2`; stderr contains the notice line before the finding.
  - `test_gate_stale_approval_notice`: approve, edit the detector → no host call; notice contains `changed since approval`.
  - `test_gate_unapproved_json_stdout_parses`: `--format json` → `json.loads(stdout)` succeeds; notice on stderr.
  - `test_gate_hook_exit_2_on_gate_input_failures` parametrized: mandates missing; `_no_deps_env`; unknown built-in detector; an approved host detector that raises; a non-UTF-8 edited `.py` (`b"\xff"`) → each exit `2` with a stderr line starting `acf:`.
  - `test_gate_hook_empty_store_exits_2` (Review Focus 1) and `test_gate_hook_deleted_detector_file_exits_2` (Review Focus 5).
  - The text-format exit-1 tests (`test_hooks.py:145`, `:318`, `:424`) stay unchanged.

- [x] **Step 3: Run** `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_hooks.py -q` — expected: new tests FAIL; seeded tests PASS.

- [x] **Step 4: Implement** per §4.5:
  - Split the body after `out_format` is known into `_gate(args, stdin_payload, repo, out_format) -> int`; `main` calls it inside `try/except Exception as exc:` — hook format prints `acf: internal error: {type(exc).__name__}: {exc}` and `traceback.format_exc()` to stderr and returns `2`; other formats `raise`. Token comment on the `except` line: `# fail-loud.bare-except-ok: hook mode reports any failure on the agent's channel (exit 2); other formats re-raise`.
  - The four `return 1` of §1.2 become `return 2 if out_format == "hook" else 1`.
  - Import `check_approval`, `reason`, `ApprovalState` from `acf.approval` in the deferred-import `try`; compute `approval = check_approval(repo, registry, HOOK_CALL_SITES)` in the same `try` as `load_mandates` (R1: that call is unchanged).
  - `run_host = approval.state in {NOT_NEEDED, APPROVED}`; pass `run_host` and `approval.digests` (or `None` when `NOT_NEEDED`) to `_scan_paths`, which skips the three host calls when `run_host` is false.
  - Notice (Global Constraints text) when not `run_host`: hook without BLOCK → prefix `additionalContext` with the notice and a blank line, and add top-level `"systemMessage": <notice>`; hook with BLOCK → print to stderr before the findings; text/json → stderr.
  - Docstring states the approval rule and the exit codes.

- [x] **Step 5: Run** the full suite plus `plugins/arch-compliance/tests/test_repo_paths.py` and `test_repo_tree_guard.py` — expected: PASS.

- [x] **Step 6: Commit** `git commit -m "feat(hook): skip unapproved host rows with a notice; exit 2 on gate failures"`.

### Task 8: Doctrine, prose, version

**Files:** the §4.8 table, plus R3 and R4:
- `config/architecture/ARCHITECTURE.md:9-12`, `:175-182`
- `plugins/arch-compliance/skills/acf-setup/SKILL.md:16-25`, `:148`, `:150`, `:159`, `:164`, `:182-196`, `:208-209`, `:221-238`, and R3 at `:193`, `:209`, `:228`, `:260`
- `plugins/arch-compliance/skills/acf-mandate/SKILL.md:88-104` (R4), `:136`
- `README.md:57-62`, `:108`, `:110`, new upgrade note after `:112-117`
- `docs/guides/SUPERPOWERS_COMPLEMENT.md:82-87`
- `plugins/arch-compliance/hooks/hooks.json:2`
- `pyproject.toml:3`, `plugins/arch-compliance/.claude-plugin/plugin.json:3`

- [x] **Step 1: Edit each file** to the §4.8 row text. R3: replace each `python -m acf.cli_check_diff` in `acf-setup/SKILL.md` with `acf-check-diff` (same arguments). R4: the snippet becomes `from acf.detectors import load_gate_registry` / `reg = load_gate_registry(repo, repo / MANDATES_REL)`, dropping the `KNOWN_DETECTORS`, `LLM_PROMPT_IDS` and `load_mandates` imports it no longer uses. The CI sketch gets `--trusted-checkout`; the pre-commit snippet does not.

- [x] **Step 2: Verify**:
  - `grep -n "python -m acf.cli_check_diff" plugins/arch-compliance/skills` → no output.
  - `grep -n "trusted-checkout" plugins/arch-compliance/skills/acf-setup/SKILL.md` → only the CI sketch lines and the agent-never-adds sentence.
  - `grep -n '"0.2.5"' pyproject.toml plugins/arch-compliance/.claude-plugin/plugin.json` → both.
  - Run the R4 snippet from the repository root → prints `OK: … mandates`.
  - `PYTHONUTF8=1 python -m pytest -q` → PASS (prose-anchor tests included).

- [x] **Step 3: Commit** `git commit -m "docs: approval rule, --trusted-checkout in CI, hook exit 2; v0.2.5"`.

### Task 9: Acceptance

- [x] **Step 1:** `PYTHONUTF8=1 python -m pytest -q` → all pass (§8 item 1; covers the test-built registries the params census lists `NOT-STATIC`).
- [x] **Step 2:** `python docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/params_census.py` → exit `0`; `python docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/host_row_gate_tests.py` → its listed tests are the ones Tasks 6 and 7 seeded.
- [x] **Step 3:** `PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main --call-site ci` → exit `0` (§8 item 3).
- [x] **Step 4 (§8 item 2, scratch host under the scratchpad, never this repo):** `.acf/enabled`, a `mandates.yml` with one host guard row at `[hook, precommit]`, a detector that logs each call. Edit a file there through Claude Code (fallback when that cannot be driven: pipe the same PostToolUse payload into `hooks/posttooluse_gate.py --format hook`, and say so) → notice, no log line; `acf-check-diff --call-site precommit` → exit `1` naming `acf-allow`; `acf-allow` → both run the row; edit the detector → both back to unapproved. Record the four outputs in the PR description.
- [x] **Step 5:** `git diff --stat main -- plugins/arch-compliance/python plugins/arch-compliance/hooks` lists exactly the runtime rows of spec §5.
