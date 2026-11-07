# Host Detector Extension Point Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let a host run its own `ast` and `guard` detectors through the plugin's two Tier-1 gates, with rows routed by `call_sites`, built-in detectors held to declared contracts, and every repository path resolved through one façade.

**Architecture:** Path-string shape checks move to `acf.engine`; turning a path string into a repository location moves to one façade, `acf.repo.RepoTree`, enforced by an AST guard test. `acf.registry` gains call-site routing, row-shape validation and built-in contracts (`acf.detectors.KNOWN_DETECTORS`). A new `acf.detectors.host` loads host modules and runs host callables inside wrapped regions that turn every failure into a typed ACF error, and both gates call it.

**Tech Stack:** Python ≥ 3.11, pydantic 2, pytest; TypeScript pack on Node with `tsx` and `ts-morph`.

**Spec:** `docs/design/HOST_DETECTOR_EXTENSION_POINT.md` (v10, cleared by verification pass at `8d14b52`). The spec carries the exact code for every new function (§4.1–§4.5); this plan cites those blocks instead of repeating them. Read both.
**Merged:** PR #26 (`8677e45`, 2026-11-06). The final review added one fix beyond these tasks: `parse_python` strips a UTF-8 BOM (`46a36cc`). Follow-ups filed: #28 (`load_baseline` through `load_model_file`, the spec's own deferral), #29 (committed `.acf/enabled`), #30 (hook exit code for gate-input failures), #31 (Appendix census recipe quoting).

## Global Constraints

- `requires-python >=3.11` (`pyproject.toml:5`); behaviour must hold on 3.11, 3.12 and 3.13 (spec §4.1 on `resolve()` and `is_file()`).
- `acf/engine.py` stays stdlib-only. `acf/repo.py` imports only `__future__` and `pathlib` (`plugins/arch-compliance/tests/test_repo_paths.py:74-78`).
- The hooks never import `acf.adr`, and the PostToolUse hook never imports `acf.judge` (`plugins/arch-compliance/tests/test_adr_import_graph.py:70-76`; spec Decision 4).
- Every new exception is an existing `AcfError` subclass: `AcfInputError`, `UnknownDetectorError`, `DetectorPackError`. No new exception classes.
- Every broad handler is `except KeyboardInterrupt: raise` followed by `except BaseException ...:  # fail-loud.bare-except-ok: <the reason the spec gives>`.
- Every file read declares `encoding="utf-8"`. Every persisted or reported path is POSIX (`.as_posix()`).
- No `hasattr` probing (`## No shims`).
- Line numbers in this plan are as at `a338cad`; each task re-locates them with the recipe given before editing.
- On Windows, run every Python command with `PYTHONUTF8=1`; run commands from the worktree root.
- Version becomes `0.2.3` in `pyproject.toml:3` and `plugins/arch-compliance/.claude-plugin/plugin.json:3`. The branch `fix/reviewer-prompts-nested-null-keys` also bumps to `0.2.3`; whichever merges second takes `0.2.4`.

## Review Focus

1. **A Windows-native absolute path from the harness** (`C:\...\repo\pkg\a.py`) reaching the PostToolUse hook should be scanned under its POSIX relative key (`pkg/a.py`). Pinned in Task 10.
2. **A host reference written with backslashes** (`scripts\ci\guard.py:scan`) in `mandates.yml` should be refused at load with `AcfInputError`, naming the row, not passed to the loader. Pinned in Task 5.
3. **One host module referenced by both an `ast` row and a `guard` row** should execute once per process. Pinned in Task 9.
4. **A registry whose only rows active at `precommit` are host rows** should pass `acf-check-diff --call-site precommit`'s selection check, since host rows are `ast`/`guard` rows too. Pinned in Task 10.
5. **A host guard that flags the same file several times** should cause that file to be read once for exemption lines. Pinned in Task 9.

---

### Task 1: Engine path-string and hit-field checks

**Files:**
- Modify: `plugins/arch-compliance/python/acf/engine.py`
- Test: `plugins/arch-compliance/tests/test_engine_paths.py` (extend; keep existing cases)

**Interfaces:**
- Produces: `looks_absolute(path: str) -> bool`; `validate_posix_rel_path(value: str) -> str` (raises `ValueError`); `validate_hit_fields(line: object, message: object) -> tuple[int, str]` (raises `ValueError`); `parse_python(text: str) -> ast.Module | None`. Bodies exactly as spec §4.1's `acf/engine.py` block, including `_ABSOLUTE_RE`.

- [x] **Step 1: Write the failing tests**

```python
@pytest.mark.parametrize("ok", ["scripts/ci/guard.py", "a/b/c.py", "guard.py"])
def test_validate_posix_rel_path_accepts(ok): assert validate_posix_rel_path(ok) == ok

@pytest.mark.parametrize("bad", ["", " a.py", "a\\b.py", "/a.py", "a/", "C:/a.py", "C:a.py",
                                 "a//b.py", "./a.py", "a/./b.py", "../a.py", "a/../b.py"])
def test_validate_posix_rel_path_refuses(bad):
    with pytest.raises(ValueError): validate_posix_rel_path(bad)

def test_looks_absolute():
    assert looks_absolute("C:a") and looks_absolute("/x") and looks_absolute("\\\\srv\\s")
    assert not looks_absolute("a/b.py")

def test_validate_hit_fields():
    assert validate_hit_fields(1, "m") == (1, "m")
    for line, msg in [("5", "m"), (True, "m"), (0, "m"), (1, ""), (1, b"m")]:
        with pytest.raises(ValueError): validate_hit_fields(line, msg)

def test_parse_python():
    assert isinstance(parse_python("x = 1"), ast.Module)
    assert parse_python("def (") is None
```

- [x] **Step 2: Run to verify failure**
Run: `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_engine_paths.py -q`
Expected: FAIL with `ImportError` on the new names.

- [x] **Step 3: Implement the four functions in `acf/engine.py`** as spec §4.1, adding `import ast` and `import re`. `validate_posix_rel_path` calls the existing `contains_backslash`.

- [x] **Step 4: Run to verify pass**
Run: the Step 2 command. Expected: PASS.

- [x] **Step 5: Commit**
`git add plugins/arch-compliance/python/acf/engine.py plugins/arch-compliance/tests/test_engine_paths.py && git commit -m "feat(engine): path-string shape checks, hit-field check, parse_python"`

---

### Task 2: `RepoTree`, the repository-path façade

**Files:**
- Modify: `plugins/arch-compliance/python/acf/repo.py`
- Test: `plugins/arch-compliance/tests/test_repo_tree.py` (create; holds the `RepoTree` cases that spec §4.7 lists under `test_repo_tree_guard.py`, so they can land before the guard)

**Interfaces:**
- Produces: `class RepoTree(root: Path)` with `.root: Path` (resolved), `.contained(path: str) -> Path | None`, `.file(path: str) -> Path | None`, `.directory(path: str) -> Path | None`, `.key(location: Path) -> str`. Bodies as spec §4.1's `acf/repo.py` block. `contained` catches `(RuntimeError, ValueError)` and returns `None`; `file`/`directory` let `OSError` propagate.

- [x] **Step 1: Write the failing tests**

```python
def test_contained_refuses_escape(tmp_path):
    t = RepoTree(tmp_path)
    assert t.contained("../x") is None
    assert t.contained(str(tmp_path.parent / "elsewhere.py")) is None

def test_contained_absolute_inside_root(tmp_path):
    assert RepoTree(tmp_path).contained(str(tmp_path / "a.py")) == (tmp_path / "a.py").resolve()

def test_contained_symlink_escape(tmp_path):
    outside = tmp_path / "out"; outside.mkdir(); repo = tmp_path / "repo"; repo.mkdir()
    try: (repo / "link").symlink_to(outside, target_is_directory=True)
    except OSError: pytest.skip("platform cannot create symlinks")
    assert RepoTree(repo).contained("link/a.py") is None

@pytest.mark.parametrize("exc", [RuntimeError, ValueError])
def test_contained_maps_resolve_errors(tmp_path, monkeypatch, exc):
    tree = RepoTree(tmp_path)                      # resolve the root before patching
    def boom(self, strict=False): raise exc("x")
    monkeypatch.setattr(Path, "resolve", boom)
    assert tree.contained("a.py") is None
```

```python
def test_file_and_directory(tmp_path):
    (tmp_path / "d").mkdir(); (tmp_path / "f.py").write_text("x", encoding="utf-8")
    t = RepoTree(tmp_path)
    assert t.file("f.py") and t.file("d") is None and t.file("missing.py") is None
    assert t.directory("d") and t.directory("f.py") is None

def test_key(tmp_path):
    t = RepoTree(tmp_path); assert t.key(t.root / "a" / "b.py") == "a/b.py"
```

- [x] **Step 2: Run to verify failure**
Run: `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_repo_tree.py plugins/arch-compliance/tests/test_repo_paths.py -q`
Expected: FAIL with `ImportError: cannot import name 'RepoTree'`; `test_repo_paths.py` still passes.

- [x] **Step 3: Add `RepoTree` to `acf/repo.py`** as spec §4.1, importing nothing new beyond `pathlib`.

- [x] **Step 4: Run to verify pass**
Run: the Step 2 command. Expected: PASS, including `test_repo_module_imports_only_stdlib`.

- [x] **Step 5: Commit**
`git commit -m "feat(repo): RepoTree, the one owner of repository path resolution"` (add both files).

---

### Task 3: Citations onto `looks_absolute` and `RepoTree`

**Files:**
- Modify: `plugins/arch-compliance/python/acf/adr/citations.py` (delete `_looks_absolute` `:49-51` and `_escapes_repo` `:74-76`; switch `:161`, `:163`, `:168`)
- Test: `plugins/arch-compliance/tests/test_adr_citations.py`

**Interfaces:**
- Consumes: `acf.engine.looks_absolute`; `acf.repo.RepoTree.contained`.

- [x] **Step 1: Re-run the census.** `git grep -n "_looks_absolute\|_escapes_repo" -- '*.py'` must print exactly `citations.py:49`, `:74`, `:161`, `:163`. Stop and report if it differs.

- [x] **Step 2: Write the failing test**

```python
def test_drive_relative_is_external(tmp_path):
    assert resolve_citation("C:a/b.py", repo_root=tmp_path, proposed=frozenset())[0] == "external"
```

- [x] **Step 3: Run to verify failure**
Run: `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_adr_citations.py -q`
Expected: the new case FAILS; existing cases PASS.

- [x] **Step 4: Switch citations.** Absolute test → `looks_absolute(path)`. Escape test → `contained = RepoTree(repo_root).contained(path)`, escaping when `contained is None`. The existence check at `:168` uses `contained.exists()`. Keep `resolve_citation`'s order (spec §4.1).

- [x] **Step 5: Run to verify pass**
Run: the Step 3 command plus `test_adr_citation_history.py`. Expected: PASS. Re-run the Step 1 grep; expected: no output.

- [x] **Step 6: Commit**
`git commit -m "refactor(adr): citations consume engine and RepoTree path checks"`

---

### Task 4: Scanner constants, `*_args` functions, shared parse and predicate

A behaviour-preserving refactor; every existing test stays green.

**Files:**
- Modify: `plugins/arch-compliance/python/acf/detectors/python_pack.py`, `build_artifacts.py`, `facade_sinks.py`, `fail_loud_ratchet.py`, `fsm_guard.py`
- Modify: `plugins/arch-compliance/python/acf/cli_check_diff.py:128-166`, `plugins/arch-compliance/hooks/posttooluse_gate.py:255-294` (inline params extraction → `*_args`)
- Test: `plugins/arch-compliance/tests/test_builtin_detectors.py` (create)

**Interfaces:**
- Produces, per spec §4.3:
  - mandate-id constants `FAIL_LOUD_BARE_EXCEPT_MANDATE_ID`, `NO_SHIMS_HASATTR_MANDATE_ID`, `POSIX_PATHS_STR_MANDATE_ID` (in `python_pack`);
  - one `*_MANDATE_ID` constant each in `build_artifacts`, `facade_sinks`, `fail_loud_ratchet` and `fsm_guard`, each holding today's literal;
  - detector-id constants `FAIL_LOUD_BARE_EXCEPT_DETECTOR_ID`, `NO_SHIMS_HASATTR_DETECTOR_ID`, `POSIX_PATHS_STR_DETECTOR_ID` (in `python_pack`);
  - `facade_sink_args(params: Mapping) -> dict`, `fsm_guard_args(params: Mapping) -> dict`, `build_artifact_args(params: Mapping) -> dict`;
  - `python_pack.is_bare_or_exception(node: ast.ExceptHandler) -> bool`, which is `_is_bare_or_exception` renamed.
- Consumes: `acf.engine.parse_python`.

- [x] **Step 1: Re-run the censuses** from spec §4.9 rows 3, 4 and 8 (`_is_bare_or_exception`, `ast.parse(text)`, the three `params.get(...)` lines). Each must match the counts listed there.

- [x] **Step 2: Write the failing tests**

```python
def test_args_defaults():
    assert facade_sink_args({}) == {"target_literal_re": ""}
    assert fsm_guard_args({}) == {"state_field": "", "validator_name": ""}
    assert build_artifact_args({}) == {} and build_artifact_args({"path_prefixes": []}) == {}

def test_args_pass_through():
    assert facade_sink_args({"target_literal_re": "x", "allowlist_globs": None, "atomic_is_sink": False}) == \
        {"target_literal_re": "x", "allowlist_globs": None, "atomic_is_sink": False}
    assert build_artifact_args({"path_prefixes": ["dist/"]}) == {"path_prefixes": ["dist/"]}

def test_ratchet_uses_pack_predicate():
    import acf.detectors.fail_loud_ratchet as r, acf.detectors.python_pack as p
    assert r.is_bare_or_exception is p.is_bare_or_exception
```

- [x] **Step 3: Run to verify failure**
Run: `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_builtin_detectors.py -q`
Expected: FAIL with `ImportError`.

- [x] **Step 4: Implement.**
  - Constants replace the literals at their `Finding` constructions.
  - `*_args` follow spec §4.3's rules: required keys `str(params.get(k, ""))`; optional keys only when present; `path_prefixes` only when present and non-empty.
  - Both gates call `scanner(..., **scanner_args(mandate.params or {}))` and their inline extraction is deleted.
  - The four parse-and-skips become `tree = parse_python(text)`, returning the scanner's empty result on `None`.
  - `count_bare_excepts` calls `is_bare_or_exception`.

- [x] **Step 5: Run the whole suite**
Run: `PYTHONUTF8=1 python -m pytest -q`. Expected: PASS (no behaviour change). Re-run the Step 1 censuses; the deleted sites are gone.

- [x] **Step 6: Commit**
`git commit -m "refactor(detectors): mandate-id constants, *_args, shared parse and bare-except predicate"`

---

### Task 5: Registry contracts and `KNOWN_DETECTORS`

**Files:**
- Modify: `plugins/arch-compliance/python/acf/registry.py`, `plugins/arch-compliance/python/acf/detectors/__init__.py`, `plugins/arch-compliance/python/acf/detectors/python_pack.py:16`, `plugins/arch-compliance/python/acf/cli_check_diff.py:10-25,70`
- Test: `plugins/arch-compliance/tests/test_registry.py`, `test_profile_drift.py:24`, `tests/test_self_host.py:5,14,23,40`, `test_builtin_detectors.py`

**Interfaces:**
- Produces in `acf.registry` (spec §4.2 block, verbatim names):
  - `CallSite`, `DIFF_CALL_SITES`, `HOOK_CALL_SITES` and `TIER1_CALL_SITES`;
  - `BuiltinDetector(mandate_id: str, call_sites: frozenset[str])`;
  - `is_host_detector_ref(detector: str) -> bool` and `parse_host_detector_ref(detector: str) -> tuple[str, str]`;
  - `Mandate.call_sites: list[CallSite]`, `Mandate.is_active`, `Mandate.runs_at(call_sites) -> bool` and `Mandate._row_shape`;
  - `MandateRegistry.active(call_sites, *, detector=None, detection=None) -> list[Mandate]`;
  - `load_mandates(path, *, known_detectors: Mapping[str, BuiltinDetector] | None = None, llm_prompt_ids: frozenset[str] | None = None, repo_root: Path | None = None)`, including the reserved-id check and `_check_builtin`.
- Produces in `acf.detectors`: `KNOWN_DETECTORS: Mapping[str, BuiltinDetector]` (a `MappingProxyType`) per the spec §4.3 table. `fail_loud_ratchet` maps to `DIFF_CALL_SITES` and every other id to `TIER1_CALL_SITES`. The docstring becomes "Built-in detector contracts."
- `cli_check_diff` imports `KNOWN_DETECTORS` from `acf.detectors` (a re-export) and loads with `known_detectors=KNOWN_DETECTORS, llm_prompt_ids=LLM_PROMPT_IDS, repo_root=repo`.
- Produces in `typescript_bridge`: the constant `TS_MANDATE_IDS = {"empty_catch": "fail-loud.empty-catch", "explicit_any": "no-shims.explicit-any"}`, which `KNOWN_DETECTORS` reads for its two TypeScript keys. The bridge starts using it in Task 6.
- Deleted: `PYTHON_AST_DETECTOR_IDS`, `GUARD_DETECTOR_IDS`, `CONFIG_AST_DETECTOR_IDS`, `ALL_PYTHON_DETECTOR_IDS` (and their `__all__` entries). `TS_DETECTOR_IDS` goes in Task 6.

- [x] **Step 1: Re-run** the spec §4.9 `_DETECTOR_IDS` census, plus the Appendix rows "Shipped `ast`/`guard` rows against the contracts", "Shipped `llm` rows against `LLM_PROMPT_IDS`" and "Non-built-in rows using a built-in mandate id". Each must print what the Appendix records.

- [x] **Step 2: Write the failing tests** in `test_registry.py`, one per case spec §4.7 lists for that file, plus:

```python
def test_backslash_host_reference_refused(tmp_path):   # Review Focus 2
    with pytest.raises(AcfInputError, match="scripts"):
        load_mandates(_write(tmp_path, detector="scripts\\ci\\guard.py:scan", detection="guard"))
```

`_write` is the file's existing inline-YAML helper pattern (`:22-27`); give the row `call_sites: [ci]`. In `test_builtin_detectors.py`, add:
  - `assert not (set(KNOWN_DETECTORS) & LLM_PROMPT_IDS)`;
  - `assert KNOWN_DETECTORS["fail_loud_ratchet"].call_sites == DIFF_CALL_SITES`;
  - every other key maps to `TIER1_CALL_SITES`.

Update `test_profile_drift.py:24` and `tests/test_self_host.py:23` to pass `llm_prompt_ids=LLM_PROMPT_IDS` (and `repo_root=ROOT` in self-host). `tests/test_self_host.py:40` checks each manual row with `RepoTree(ROOT).file(m.detector)`.

- [x] **Step 3: Run to verify failure**
Run: `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_registry.py plugins/arch-compliance/tests/test_builtin_detectors.py -q`
Expected: FAIL on the new cases.

- [x] **Step 4: Implement** registry and `KNOWN_DETECTORS` as spec §4.2–§4.3. Repoint `test_registry.py:30` to `known_detectors=KNOWN_DETECTORS`.

- [x] **Step 5: Run the whole suite**
Run: `PYTHONUTF8=1 python -m pytest -q`. Expected: PASS. Every shipped and fixture registry loads, as the Appendix census shows.

- [x] **Step 6: Commit**
`git commit -m "feat(registry): call-site routing types, row-shape rules, built-in contracts"`

---

### Task 6: TypeScript pack stops emitting `mandate_id`; the bridge stamps and validates

**Files:**
- Modify: `plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:4,23`, `src/rules/explicitAny.ts:15`, `src/scan.ts:83,94-96`
- Modify: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:14,84-92`
- Test: `plugins/arch-compliance/tests/test_typescript_pack.py:6,14`, `test_builtin_detectors.py`

**Interfaces:**
- Consumes: `TS_MANDATE_IDS` (Task 5). `TS_DETECTOR_IDS` is deleted here, with its users at `typescript_bridge.py:14`, `detectors/__init__.py` and `test_typescript_pack.py:6,14`.
- Consumes: `acf.engine.validate_hit_fields`.

- [x] **Step 1: Write the failing tests.** In `test_typescript_pack.py`, with the subprocess result monkeypatched:
  - an item with `detector: "nope"` raises `DetectorPackError`;
  - so do items with `line` of `"5"`, `0` or `True`, and with `message: ""`;
  - a valid item's `Finding.mandate_id == TS_MANDATE_IDS[item["detector"]]`.

  Repoint `:6`/`:14` to `TS_MANDATE_IDS` keys. In `test_builtin_detectors.py`, no file under `plugins/arch-compliance/detectors/typescript/src/` contains `mandate_id`, and each `TS_MANDATE_IDS` key appears in its rule file as `detector: "<key>"`.

- [x] **Step 2: Run to verify failure**
Run: `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_typescript_pack.py plugins/arch-compliance/tests/test_builtin_detectors.py -q`
Expected: FAIL.

- [x] **Step 3: Implement.**
  - Node: drop the `mandate_id` field from the `Finding` type and both rules. `scan.ts`'s `expectFinding` matches `f.detector === detector` and its three calls pass `"empty_catch"` / `"explicit_any"`.
  - Python: `mandate_id=TS_MANDATE_IDS[item["detector"]]`, and `line, message = validate_hit_fields(item["line"], item["message"])` inside the existing `try` (spec §4.3).

- [x] **Step 4: Run to verify pass**
Run: `npm ci --prefix plugins/arch-compliance/detectors/typescript && npm test --prefix plugins/arch-compliance/detectors/typescript`, then the Step 2 command, then `PYTHONUTF8=1 python -m pytest -q`.
Expected: the Node self-test prints no failures; pytest PASSES.

- [x] **Step 5: Commit**
`git commit -m "feat(ts): one spelling of TypeScript mandate ids; bridge validates hits"`

---

### Task 7: Ratchet onto `RepoTree`

**Files:**
- Modify: `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:45-62,77-81,122-124`
- Test: `plugins/arch-compliance/tests/test_portable_guards.py`

**Interfaces:**
- Consumes: `RepoTree.file`, `.directory`, `.key`. `scan_tree`/`scan_ratchet` signatures are unchanged.

- [x] **Step 1: Write the failing tests**

```python
@pytest.mark.parametrize("baseline", ["../x.json", "missing.json"])
def test_ratchet_refuses_bad_baseline(tmp_path, baseline):
    with pytest.raises(DetectorPackError, match="baseline"):
        scan_ratchet(tmp_path, baseline_path=baseline)

def test_ratchet_refuses_absolute_outside(tmp_path):
    outside = tmp_path.parent / "x.json"
    with pytest.raises(DetectorPackError, match="baseline"):
        scan_ratchet(tmp_path, baseline_path=str(outside))

@pytest.mark.parametrize("roots", [["../x"], ["missing"]])
def test_scan_tree_refuses_bad_root(tmp_path, roots):
    with pytest.raises(DetectorPackError, match="roots"): scan_tree(tmp_path, roots=roots)
```

The existing `scan_tree(tmp_path, roots=["pkg"], ...)` case at `:107` is unchanged.

- [x] **Step 2: Run to verify failure**
Run: `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_portable_guards.py -q`. Expected: the new cases FAIL.

- [x] **Step 3: Implement** spec §4.9's ratchet row.
  - `baseline` resolves through `RepoTree.file`, and each `roots` entry through `RepoTree.directory`. A `None`, or an `OSError` from the stat, raises `DetectorPackError` naming the parameter.
  - Walked files are keyed by `tree.key(path)`.
  - Delete `if not search.exists(): continue` and the walk filter's `except ValueError: continue`.
  - `load_baseline` drops its own `is_file()` check. Its JSON parse and shape checks stay (spec §5.2: a recorded follow-up).

- [x] **Step 4: Run to verify pass**
Run: the Step 2 command and `PYTHONUTF8=1 python -m pytest -q`. Expected: PASS.

- [x] **Step 5: Commit**
`git commit -m "fix(ratchet): contain baseline and roots through RepoTree; refuse a missing root"`

---

### Task 8: Call-site routing in both gates

**Files:**
- Modify: `plugins/arch-compliance/python/acf/enforcement.py` (`apply_registry`, new `make_line_lookup`, docstring `:6-8`)
- Modify: `plugins/arch-compliance/python/acf/cli_check_diff.py` (parser `:29-61`, empty-selection refusal, `_active_mandates` `:94-99` deleted, `:76-82`)
- Modify: `plugins/arch-compliance/hooks/posttooluse_gate.py` (`:106-125`, inline filters `:229-236`, `:284-286`)
- Modify: `config/architecture/mandates.yml`, `plugins/arch-compliance/profiles/*/mandates.yml`, `plugins/arch-compliance/tests/fixtures/mandates_valid.yml` (each `ast`/`guard` row with `ci` adds `precommit`)
- Modify: `.github/workflows/ci.yml:40` (`--call-site ci`)
- Test: `test_enforcement.py`, `test_diff_cli.py`, `test_hooks.py:199-218`

**Interfaces:**
- Produces: `apply_registry(findings, registry, line_lookup, *, call_sites: frozenset[str]) -> list[Finding]`, which drops a finding whose row does not `runs_at(call_sites)`; `make_line_lookup(file_lines: Mapping[str, list[str]]) -> LineLookup` (spec §4.5).
- `acf-check-diff` gets a required `--call-site` with `choices=sorted(DIFF_CALL_SITES)`; `sites = frozenset({args.call_site})`.
- Consumes: `MandateRegistry.active`, `Mandate.runs_at`, `HOOK_CALL_SITES`, `DIFF_CALL_SITES`.

- [x] **Step 1: Re-run** the Appendix "Active-row filters" and "Rows that add `precommit`" recipes; counts must match (9 / 7 / 3 / 3 rows).

- [x] **Step 2: Write the failing tests.**
  - `test_enforcement.py`: every existing `apply_registry` call passes `call_sites=`. Add: a finding whose row lacks the site is dropped, and `make_line_lookup({})("x", 1) == ""`.
  - `test_diff_cli.py`: every `main([...])` passes `--call-site ci`. Add:
    - a `[ci]`-only row is reported with `ci` and not with `precommit`;
    - `pytest.raises(SystemExit)` without `--call-site`;
    - exit `1` with `"selects no active"` for a registry with no active row at the site.

    `test_unenforced_mandate_does_not_gate` adds an active `no-shims.hasattr` row (`detector: no_shims_hasattr`, `call_sites: [ci]`).
  - `test_hooks.py`: the `:199-218` test sets the copied fixture's `no-shims.hasattr` row to `[ci, hook]`; a new case asserts a `[ci]`-only row is not reported.

- [x] **Step 3: Run to verify failure**
Run: `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_enforcement.py plugins/arch-compliance/tests/test_diff_cli.py plugins/arch-compliance/tests/test_hooks.py -q`. Expected: FAIL.

- [x] **Step 4: Implement** spec §4.5 and the routing bullets of §4.6.
  - The gates use `registry.active(...)` in place of their filters.
  - Both gates use `make_line_lookup`.
  - The hook loads with `known_detectors=KNOWN_DETECTORS, repo_root=repo` and catches `(AcfInputError, UnknownDetectorError)` at load and `(AcfInputError, DetectorPackError, UnknownDetectorError)` at scan.
  - Add `precommit` to the 22 rows and `--call-site ci` to `ci.yml:40`.

- [x] **Step 5: Run to verify pass**
Run: `PYTHONUTF8=1 python -m pytest -q` and `PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main --call-site ci`. Expected: PASS, and the gate exits `0`.

- [x] **Step 6: Commit**
`git commit -m "feat(gates): route rows by call_sites; required --call-site; shared line lookup"`

---

### Task 9: Host loader and runners

**Files:**
- Create: `plugins/arch-compliance/python/acf/detectors/host.py`
- Create: `plugins/arch-compliance/tests/conftest.py`
- Create: `plugins/arch-compliance/tests/test_host_detectors.py`

**Interfaces:**
- Produces, in `acf.detectors.host`, as spec §4.4 items 1–7 with their code blocks verbatim:
  - `HostHit`;
  - `load_host_detector(repo_root: Path, detector: str) -> Callable[..., Iterable[HostHit]]`;
  - `_call_host`, `_revalidate`, `_describe` and `_to_findings(hits, mandate, *, repo_root, expected_path)`;
  - `scan_host_ast_file(repo_root, text, path, added_lines, registry, *, language, call_sites) -> list[Finding]`;
  - `scan_host_guards(repo_root, changed_files, registry, file_lines, *, call_sites) -> list[Finding]`.

  Module state is `_ACTIVE_ROOT: Path | None`; `sys.modules` is the only module record.
- Produces in `conftest.py`: the fixture `fresh_host_loader` (spec §4.7).
- Consumes: `RepoTree`, `parse_python`, `validate_posix_rel_path`, `validate_hit_fields`, `MandateRegistry.active`, `is_host_detector_ref`, `parse_host_detector_ref`.

- [x] **Step 1: Write the failing tests:** every case spec §4.7 lists for `test_host_detectors.py`, each using `fresh_host_loader` and host modules written under `tmp_path`. Add:

```python
def test_module_shared_by_ast_and_guard_rows_executes_once(tmp_path, fresh_host_loader):   # Review Focus 3
    # module body appends to a list in a sibling module; one ast row + one guard row name it
    ...  # run scan_host_ast_file then scan_host_guards; assert the counter == 1

def test_guard_flagging_one_file_twice_reads_it_once(tmp_path, fresh_host_loader, monkeypatch):  # Review Focus 5
    ...  # spy on Path.read_text; two hits on "notes.md"; assert one read of that path
```

- [x] **Step 2: Run to verify failure**
Run: `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_host_detectors.py -q`. Expected: FAIL with `ModuleNotFoundError: acf.detectors.host`.

- [x] **Step 3: Implement `host.py`** from spec §4.4.
  - Each broad handler's token reason is the one in the spec's code.
  - `scan_host_guards` reads each flagged file once, inside one `try`, with `errors="replace"`.

- [x] **Step 4: Run to verify pass**
Run: the Step 2 command, then `PYTHONUTF8=1 python -m pytest -q`. Expected: PASS.

- [x] **Step 5: Commit**
`git commit -m "feat(detectors): host detector loader and wrapped runners"`

---

### Task 10: Wire host runners and `RepoTree` into both gates

**Files:**
- Modify: `plugins/arch-compliance/python/acf/cli_check_diff.py` (`_scan_changed` `:110-184`)
- Modify: `plugins/arch-compliance/hooks/posttooluse_gate.py` (`_collect_paths` `:200-209`, `_scan_paths` `:213-295`, docstring `:12`; keep `:11` verbatim)
- Test: `test_diff_cli.py`, `test_hooks.py`, `test_builtin_detectors.py` (contract against dispatch)

**Interfaces:**
- Consumes: `scan_host_ast_file`, `scan_host_guards` (Task 9); `RepoTree.file`, `.key` (Task 2).

- [x] **Step 1: Write the failing tests.**
  - `test_diff_cli.py`, using `fresh_host_loader`:
    - host `ast` and `guard` rows declaring `ci` run, and exit `1` on `BLOCK`;
    - an exemption token on a non-code file flagged by a host guard is honoured;
    - Review Focus 4: a registry whose only active row at `precommit` is a host guard row passes the selection check under `--call-site precommit`, and its finding is reported.
  - `test_hooks.py`, with the hook in a subprocess:
    - exit `0` without importing a host module when `.acf/enabled` is absent (the module raises at import);
    - exit `1` on an unknown detector when enabled;
    - host rows declaring `hook` run, and `[ci]`-only host guards do not;
    - an edited `.py` outside the repository yields no finding and no host call;
    - Review Focus 1: an in-repo file passed as `str(abs_path)`, which is Windows-native on Windows, is reported under its POSIX relative key.
  - `test_builtin_detectors.py`: the contract-against-dispatch test as spec §4.7. Generate the fixture tree under `tmp_path`, run both diff-gate sites and the hook, and assert exactly the expected `mandate_id` set per gate.

- [x] **Step 2: Run to verify failure**
Run: `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_diff_cli.py plugins/arch-compliance/tests/test_hooks.py plugins/arch-compliance/tests/test_builtin_detectors.py -q`. Expected: FAIL.

- [x] **Step 3: Implement** the remaining §4.6 bullets.
  - Diff gate: `tree.file(rel)`, skipping `None`, with keys staying the git spelling; the `.py`/TS branches call `scan_host_ast_file`; `scan_host_guards(repo, in_repo, ...)` runs after the ratchet loop.
  - Hook: `_collect_paths` uses `tree.file(raw)`; `_scan_paths` drops `is_file()` and `try/except ValueError` and uses `rel = tree.key(abs_path)`; it calls both runners.

- [x] **Step 4: Run to verify pass**
Run: `PYTHONUTF8=1 python -m pytest -q`. Expected: PASS.

- [x] **Step 5: Commit**
`git commit -m "feat(gates): run host detectors; resolve changed and edited paths through RepoTree"`

---

### Task 11: The repository-path guard

**Files:**
- Create: `plugins/arch-compliance/tests/test_repo_tree_guard.py`

**Interfaces:**
- Consumes: the rules of `docs/design/evidence/HOST_DETECTOR_EXTENSION_POINT/path_census.py`, as Decision 9 states them.
  - Flag `.resolve`, `.relative_to`, `.is_relative_to` and `.joinpath` on a receiver not built from `__file__`.
  - Flag `os.path.realpath`, `abspath`, `relpath` and `commonpath`.
  - Flag a `/` join whose left operand is named one of `repo`, `repo_root`, `root`, `ROOT`, `base`, `host_root` and whose right operand is not a constant or an ALL_CAPS name.
  - Exclude `acf/repo.py`.

- [x] **Step 1: Write the tests**

```python
ALLOWED = {("cli_check_diff.py", "main"), ("cli_check_llm.py", "main"),
           ("typescript_bridge.py", "scan_typescript_file")}

def test_only_allowlisted_functions_resolve_repo_paths():
    hits = {(path.name, enclosing_function) for path, enclosing_function in _scan_tree()}
    assert hits == ALLOWED

def test_rules_flag_fixture():
    src = "def f(repo, name, path, root, x, p):\n    repo / name\n    path.resolve()\n    root.joinpath(x)\n    os.path.realpath(p)\n"
    assert len(_scan_source(src)) == 4

def test_rules_spare_constants_and_file_dunder():
    assert _scan_source("Path(__file__).resolve()\nrepo / MANDATES_REL\n") == []
```

`_scan_tree` walks `git ls-files plugins/arch-compliance/python plugins/arch-compliance/hooks` (excluding `acf/repo.py`) and maps each hit to its enclosing function name. `_scan_source` applies the rules to one source string.

- [x] **Step 2: Run**
Run: `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_repo_tree_guard.py -q`. Expected: PASS, because Tasks 3, 7 and 10 migrated every census site. If a hit outside `ALLOWED` appears, that site was missed: fix the site, never the allowlist.

- [x] **Step 3: Commit**
`git commit -m "test(repo): guard that RepoTree is the one owner of repository paths"`

---

### Task 12: Prose, doctrine and version

**Files:** every site in spec §4.8, plus `pyproject.toml:3` and `plugins/arch-compliance/.claude-plugin/plugin.json:3`.

- [x] **Step 1: Re-run** §4.8's `--call-site` recipe. Each hit must be a site the row lists or a named mention that runs nothing.

- [x] **Step 2: Write the failing test** in `test_builtin_detectors.py`:
  - every row of the `README.md` detector table (`:66-74`) names a key of `KNOWN_DETECTORS`;
  - its mandate-id column equals that key's `mandate_id`;
  - its new call-sites column matches the contract;
  - every Python key appears in the table.

- [x] **Step 3: Run to verify failure**
Run: `PYTHONUTF8=1 python -m pytest plugins/arch-compliance/tests/test_builtin_detectors.py -q`. Expected: FAIL until the README column exists.

- [x] **Step 4: Edit each §4.8 site** as its row states:
  - `ARCHITECTURE.md`: the new `## Host detectors and call sites` section, plus `:9-11`, `:72-73`, `:75-85`, `:105-116` and `:226-228`;
  - the `python-service` profile's `ARCHITECTURE.md` (`:25-39`);
  - the acf-mandate and acf-setup skills;
  - `README.md`, `CLAUDE.md`, `docs/guides/SUPERPOWERS_COMPLEMENT.md` and the four `docs/design/` documents;
  - the `enforcement.py` docstring;
  - the test docstrings at `test_acf_mandate_skill.py:2` and `tests/test_self_host.py:5`;
  - the version bump to `0.2.3`.

- [x] **Step 5: Run to verify pass**
Run: `PYTHONUTF8=1 python -m pytest -q`. Expected: PASS, including `test_acf_mandate_skill.py` (the rewritten snippet keeps its fenced `bash` / `python -c` shape) and `test_repo_paths.py`.

- [x] **Step 6: Commit**
`git commit -m "docs: host detectors, call-site routing and RepoTree in doctrine, skills and README (v0.2.3)"`

---

### Task 13: Definition of done

- [x] **Step 1:** `PYTHONUTF8=1 python -m pytest -q`. Expected: all pass.
- [x] **Step 2:** `npm test --prefix plugins/arch-compliance/detectors/typescript`. Expected: no failures.
- [x] **Step 3:** `PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main --call-site ci`. Expected: exit `0`.
- [x] **Step 4:** `python docs/design/evidence/HOST_DETECTOR_EXTENSION_POINT/path_census.py .`. Expected: only the three allowlisted functions' lines (`cli_check_diff.py` `main`, `cli_check_llm.py` `main`, `typescript_bridge.py` `scan_typescript_file`).
- [x] **Step 5:** `pyproject.toml:3` and `plugin.json:3` read `"0.2.3"`, or `"0.2.4"` if the reviewer-prompt branch merged first.
