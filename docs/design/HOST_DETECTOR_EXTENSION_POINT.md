# Host Detector Extension Point (`ast` and `guard` Callables)

**Status:** Draft (v1)
**Date:** 2026-11-03
**Spec kinds:** `feature`
**Repo:** `IanDBallard/arch-compliance-for-superpowers`, `main` at `a338cad` (branch `feat/host-detector-extension`, which differs from `main` only by this spec).
**Workstream:** HistoricMansions Workstream E Phase 2 (prerequisite Spec 2a — Tier-1 host detector extension point).
**Governing mandates:** `config/architecture/ARCHITECTURE.md` sections `## Fail loud` (`:24-41`), `## No shims` (`:43-53`), `## POSIX paths` (`:55-64`), `## One base exception` (`:99-103`), `## One owner for host paths` (`:105-116`), `## Declared, never defaulted` (`:118-133`), `## Prose names no host` (`:135-143`), `## Frozen ledger format` (`:145-151`), `## Live consumers` (`:153-157`), `## No completeness claims` (`:159-169`), `## Declared text decoding` (`:171-182`), `## Release discipline` (`:184-194`), `## Single point of definition` (`:196-209`), `## Scoped refactor` (`:211-215`), and the five portable governing principles at `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51`.
**No state-machine surface.** This design adds or modifies no state machine and no transition.

---

## 0. Citation convention

Unprefixed paths refer to this repository (`IanDBallard/arch-compliance-for-superpowers`) on branch `feat/host-detector-extension`, whose only change from `main` at `a338cad` is this spec; every cited line is as at `a338cad`. Paths prefixed `hm:` refer to the sibling repository `HistoricMansions` at `b652fab05` (`main`), following `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:10-32`. Every path is written in full with POSIX forward slashes and without `...` ellipses.

---

## 1. Problem

`docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:102, 123, 125` specifies that `Mandate.detector` names a detector function, guard module, LLM prompt id, or manual verification pointer, and that both the Python and TypeScript packs provide extension points for project-specific detectors. However, at `a338cad`, `arch-compliance` has no mechanism to validate, load, or execute a host-defined `detection: ast` or `detection: guard` detector:

1. **`load_mandates` rejects every `ast` or `guard` detector outside the fixed built-in set (`plugins/arch-compliance/python/acf/registry.py:48-64`):**
   - `load_mandates(path: Path, *, known_detectors: frozenset[str] | None = None) -> MandateRegistry` raises `UnknownDetectorError` at `plugins/arch-compliance/python/acf/registry.py:60-63` whenever `m.status == "enforced"`, `m.detection in {"ast", "guard"}`, and `m.detector not in known_detectors`.
   - `KNOWN_DETECTORS` (`plugins/arch-compliance/python/acf/cli_check_diff.py:25`) is the closed union `ALL_PYTHON_DETECTOR_IDS | TS_DETECTOR_IDS | LLM_PROMPT_IDS` (11 built-in ids).
   - A host repository with domain-specific deterministic rules — such as `HistoricMansions`, whose `hm:config/architecture/mandates.yml` declares 17 enforced `detection: ast` rows backed by `DETECTOR_REGISTRY` in `hm:scripts/ci/arch_compliance/engine.py:1154-1173` and 25 enforced `detection: guard` rows backed by guard modules such as `hm:config/architecture/mandates.yml:97` (`scripts/ci/metadata_facade_guard.py`) and `hm:config/architecture/mandates.yml:109` (`scripts/ci/check_image_path_contract.py`) — cannot load its registry through `acf.registry.load_mandates(..., known_detectors=KNOWN_DETECTORS)` or run its detectors through `acf-check-diff` and `hooks/posttooluse_gate.py`.
2. **Neither `cli_check_diff.py` nor `hooks/posttooluse_gate.py` dispatches host `ast` or `guard` detectors (`plugins/arch-compliance/python/acf/cli_check_diff.py:102-184`, `plugins/arch-compliance/hooks/posttooluse_gate.py:213-295`):**
   - Both `_scan_changed` (`plugins/arch-compliance/python/acf/cli_check_diff.py:102-184`) and `_scan_paths` (`plugins/arch-compliance/hooks/posttooluse_gate.py:213-295`) hardcode calls to the built-in scanners (`scan_python_file`, `scan_facade_sinks`, `scan_fsm_writes`, `scan_typescript_file`, `scan_build_artifact_paths`, and in `cli_check_diff.py:168-182` `scan_ratchet`).
   - Accepting a repo-relative path in `load_mandates` without defining a callable contract and wiring dispatch in both `cli_check_diff.py` and `hooks/posttooluse_gate.py` would allow an active `BLOCK` mandate to pass validation while nothing ever executes it, violating `## Fail loud` (`config/architecture/ARCHITECTURE.md:24-41`).
3. **`hooks/posttooluse_gate.py` omits `known_detectors` when loading `mandates.yml` and duplicates `_line_lookup` (`plugins/arch-compliance/hooks/posttooluse_gate.py:107-125`):**
   - `plugins/arch-compliance/hooks/posttooluse_gate.py:107` calls `registry = load_mandates(mandates_path)` without `known_detectors=KNOWN_DETECTORS` and catches only `AcfInputError` at line 108 (not `UnknownDetectorError`). An active mandate with an unknown detector id silently produces zero findings in the `PostToolUse` hook instead of failing loud.
   - `plugins/arch-compliance/python/acf/cli_check_diff.py:76-81` and `plugins/arch-compliance/hooks/posttooluse_gate.py:119-124` define identical `_line_lookup` closures that only consult the pre-populated `file_lines` dict of changed `.py`, `.ts`, and `.tsx` files. When a repo-level `guard` detector emits a finding on an unchanged file or a non-code file (such as `.yml` or `.sh`), `_line_lookup` returns `""` and `apply_registry` (`plugins/arch-compliance/python/acf/enforcement.py:49-51`) fails to honor inline `exemption_tokens` on that line.
4. **No neutral relative-POSIX-path validator exists outside `acf.adr` (`plugins/arch-compliance/python/acf/engine.py:1-31`):**
   - `PosixStr` in `plugins/arch-compliance/python/acf/adr/contract.py:129` only rejects backslashes (`_reject_backslash`, `plugins/arch-compliance/python/acf/adr/contract.py:98-101`) and lives in `acf.adr`, which `hooks/posttooluse_gate.py` is forbidden from referencing (`plugins/arch-compliance/tests/test_adr_import_graph.py:70-76`).
   - Validating a repo-relative POSIX path for a host detector module requires a stdlib-only validator in `plugins/arch-compliance/python/acf/engine.py` that rejects empty/whitespace strings, backslashes (`contains_backslash`, `plugins/arch-compliance/python/acf/engine.py:17-25`), leading or trailing `/`, Windows drive roots (`C:`), and `.` or `..` path traversal segments.

---

## 2. Decisions this design records

1. **Unified `<posix_rel_path.py>:<callable_name>` host detector syntax for `detection: ast` and `detection: guard`.**
   - A `Mandate` (`plugins/arch-compliance/python/acf/registry.py:14-27`) with `detection in {"ast", "guard"}` has a `detector` string of one of two forms:
     1. **Built-in detector id** (`":" not in m.detector`): a bare identifier in `KNOWN_DETECTORS` (`plugins/arch-compliance/python/acf/cli_check_diff.py:25`).
     2. **Host detector reference** (`":" in m.detector`): `<posix_rel_path.py>:<callable_name>`, where `<posix_rel_path.py>` is a valid relative POSIX path (`validate_posix_rel_path` in `plugins/arch-compliance/python/acf/engine.py`) ending in `.py` (with at least one character before `.py`), and `<callable_name>` contains no `:` and satisfies `callable_name.isidentifier()`.
   - Supporting `<posix_rel_path.py>:<callable_name>` handles both many AST detectors in one module (such as HM's 17 AST detectors in `hm:scripts/ci/arch_compliance/engine.py:1154-1173`) and one guard per module (such as HM's 25 guard modules in `hm:config/architecture/mandates.yml`, e.g. `scripts/ci/metadata_facade_guard.py:scan_guard`) under a single deterministic syntax.
2. **Strict validation in `load_mandates` — no unexecuted active `ast`/`guard` rows and no guessed `repo_root`.**
   - `load_mandates` (`plugins/arch-compliance/python/acf/registry.py:48-64`) gains an optional keyword parameter `repo_root: Path | None = None`:
     ```python
     def load_mandates(
         path: Path,
         *,
         known_detectors: frozenset[str] | None = None,
         repo_root: Path | None = None,
     ) -> MandateRegistry:
     ```
   - **Unconditional syntax check on host detector references:** For every row `m` with `m.detection in {"ast", "guard"}` and `is_host_detector_ref(m.detector)` (`":" in m.detector`), `load_mandates` calls `parse_host_detector_ref(m.detector)` regardless of `m.status` or `known_detectors`. A malformed `<posix_rel_path.py>:<callable_name>` (e.g. containing a backslash, `..` traversal, leading `/`, Windows drive prefix, non-`.py` suffix, or non-identifier callable name) raises `UnknownDetectorError` immediately.
   - **Active (`m.status != "unenforced"`) detector & call-site check when `known_detectors is not None`:**
     - Both `status: enforced` and `status: partial` mandates are active in Tier 1 (`plugins/arch-compliance/python/acf/enforcement.py:47`, `plugins/arch-compliance/python/acf/cli_check_diff.py:98`, `plugins/arch-compliance/skills/acf-mandate/SKILL.md:57`). Therefore, when `known_detectors is not None`, `load_mandates` validates every `m` with `m.status != "unenforced"` and `m.detection in {"ast", "guard"}`:
       - If `not is_host_detector_ref(m.detector)`: requires `m.detector in known_detectors` or raises `UnknownDetectorError`.
       - If `is_host_detector_ref(m.detector)`:
         1. Requires `repo_root is not None` (raises `AcfInputError` if `repo_root is None` rather than guessing `path.parents[2]`, honoring `## Declared, never defaulted` at `config/architecture/ARCHITECTURE.md:118-133` and supporting custom `--mandates` paths in `plugins/arch-compliance/python/acf/cli_check_diff.py:51-55`).
         2. Requires `bool(set(m.call_sites) & TIER1_CALL_SITES)` where `TIER1_CALL_SITES = frozenset({"ci", "precommit", "hook", "posttooluse"})` (raises `AcfInputError` if the active host `ast`/`guard` row declares no Tier-1 call site, preventing a row that passes `load_mandates` yet is skipped by both `cli_check_diff.py` and `hooks/posttooluse_gate.py`).
         3. Calls `load_host_detector(repo_root, m.detector)` to verify that `(repo_root.resolve() / rel_path).is_file()` exists, imports cleanly, and exposes a callable `attr_name` (raising `UnknownDetectorError` on missing file, import failure, or missing/non-callable attribute).
3. **Single canonical owner for host detector loading, AST sharing, finding normalization, and call-site filtering (`plugins/arch-compliance/python/acf/detectors/host.py`).**
   - **Host `detection: ast` callable signature:**
     ```python
     def scan_ast(
         text: str,
         path: str,
         added_lines: frozenset[int] | None,
         *,
         tree: ast.Module | None = None,
         params: dict[str, Any] | None = None,
     ) -> Sequence[Finding]:
     ```
     - Invoked by `scan_host_ast_file` once per changed/edited file matching `mandate.languages` (`"python"` or `"both"` for `.py`; `"typescript"` or `"both"` for `.ts` / `.tsx`) and `allowed_call_sites`.
     - For `.py` files, `scan_host_ast_file` parses `tree = ast.parse(text)` once per file (returning `[]` on `SyntaxError`, matching `scan_python_file` at `plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37`, `scan_facade_sinks` at `plugins/arch-compliance/python/acf/detectors/facade_sinks.py:50-53`, and `scan_fsm_writes` at `plugins/arch-compliance/python/acf/detectors/fsm_guard.py:36-39`) and passes `tree=tree` to every active Python host `ast` detector on that file so multiple detectors share a single parse. For `.ts` / `.tsx` files, `tree` is `None`.
   - **Host `detection: guard` callable signature:**
     ```python
     def scan_guard(
         repo_root: Path,
         changed_files: Sequence[str],
         *,
         params: dict[str, Any] | None = None,
     ) -> Sequence[Finding]:
     ```
     - Invoked by `scan_host_guards` once per active host `guard` mandate whose `call_sites` intersects `allowed_call_sites`.
   - **Call-site routing between `acf-check-diff` and `PostToolUse`:**
     - `DIFF_CALL_SITES = frozenset({"ci", "precommit"})`: passed by `_scan_changed` in `plugins/arch-compliance/python/acf/cli_check_diff.py`.
     - `HOOK_CALL_SITES = frozenset({"hook", "posttooluse"})`: passed by `_scan_paths` in `plugins/arch-compliance/hooks/posttooluse_gate.py`.
     - This ensures whole-tree CI/pre-commit guards (`call_sites: [precommit, ci]` or `[ci]`) run in `acf-check-diff` without slowing down every file edit in `PostToolUse`, while edit-time AST detectors or guards that declare `hook` or `posttooluse` in `call_sites` run in `PostToolUse`.
   - **Finding normalization and fail-loud execution:**
     - `_normalize_findings` verifies that the detector return value is a non-`str`/`bytes` `Iterable` of `Finding` objects (`plugins/arch-compliance/python/acf/finding.py:11-19`), refuses any `Finding` whose `path` contains a backslash (`contains_backslash`, `plugins/arch-compliance/python/acf/engine.py:17-25`) or whose `line < 1`, and normalizes each `Finding` via `f.model_copy(update={"mandate_id": mandate.id, "detector": mandate.detector, "detection": mandate.detection})` so `apply_registry` (`plugins/arch-compliance/python/acf/enforcement.py:37-53`) always matches the mandate row and applies its `severity` and `exemption_tokens`.
     - Any exception raised by a host detector callable (or by `_normalize_findings` on a misshapen return value) is surfaced as `DetectorPackError` (`plugins/arch-compliance/python/acf/exceptions.py:29-30`), which both `cli_check_diff.py:72` and `hooks/posttooluse_gate.py:115` catch and report with exit code `1`.
4. **Shared `make_line_lookup` in `plugins/arch-compliance/python/acf/enforcement.py`.**
   - Replaces the two duplicate `_line_lookup` closures at `plugins/arch-compliance/python/acf/cli_check_diff.py:76-81` and `plugins/arch-compliance/hooks/posttooluse_gate.py:119-124` with one helper `make_line_lookup(repo_root: Path, file_lines: dict[str, list[str]]) -> LineLookup` in `plugins/arch-compliance/python/acf/enforcement.py`.
   - On cache miss for a relative POSIX `path`, if `(repo_root / path).is_file()`, `make_line_lookup` populates `file_lines[path]` by reading `(repo_root / path).read_text(encoding="utf-8", errors="replace").splitlines()`, so inline `# <token>: <reason>` exemptions work on findings emitted by repo-level `guard` detectors even when the flagged file was not in the changed `.py`/`.ts`/`.tsx` set.
5. **Explicit `.acf/enabled` trust boundary.**
   - Importing and executing a host detector runs Python code from the host repository.
   - In `plugins/arch-compliance/hooks/posttooluse_gate.py:72-81`, `.acf/enabled` (`acf.repo.ENABLED_REL`) is the local opt-in marker created by `/acf-setup`: when `.acf/enabled` is absent, `posttooluse_gate.py` exits `0` before loading `mandates.yml` or importing any host module.
   - This trust boundary is documented in `config/architecture/ARCHITECTURE.md`, `plugins/arch-compliance/skills/acf-setup/SKILL.md`, and `plugins/arch-compliance/skills/acf-mandate/SKILL.md`.

---

## 3. Scope and Non-Goals

### In Scope
- Adding `validate_posix_rel_path(value: str) -> str` to `plugins/arch-compliance/python/acf/engine.py`.
- Creating `plugins/arch-compliance/python/acf/detectors/host.py` with `DIFF_CALL_SITES`, `HOOK_CALL_SITES`, `TIER1_CALL_SITES`, `is_host_detector_ref`, `parse_host_detector_ref`, `load_host_detector`, `scan_host_ast_file`, and `scan_host_guards`, and re-exporting them in `plugins/arch-compliance/python/acf/detectors/__init__.py`.
- Extending `load_mandates` in `plugins/arch-compliance/python/acf/registry.py:48-64` to accept `repo_root: Path | None = None`, validate host detector syntax on all `ast`/`guard` rows with `":" in m.detector`, and validate active (`m.status != "unenforced"`) built-in and host `ast`/`guard` detectors when `known_detectors is not None`.
- Adding `make_line_lookup(repo_root: Path, file_lines: dict[str, list[str]]) -> LineLookup` to `plugins/arch-compliance/python/acf/enforcement.py`.
- Wiring `repo_root=repo`, `scan_host_ast_file`, `scan_host_guards`, and `make_line_lookup` in `plugins/arch-compliance/python/acf/cli_check_diff.py` and `plugins/arch-compliance/hooks/posttooluse_gate.py` (including passing `known_detectors=KNOWN_DETECTORS, repo_root=repo` and catching `UnknownDetectorError` in `hooks/posttooluse_gate.py`).
- Updating `tests/test_self_host.py:23`, `plugins/arch-compliance/skills/acf-mandate/SKILL.md`, `plugins/arch-compliance/skills/acf-setup/SKILL.md`, `config/architecture/ARCHITECTURE.md`, and `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:184`, and bumping the plugin version from `"0.2.2"` to `"0.2.3"` in `pyproject.toml:3` and `plugins/arch-compliance/.claude-plugin/plugin.json:3`.

### Non-Goals
- **No `acf.architecture_review` runtime package and no architecture-review host configuration file:** Both belong to Spec 2b (architecture-review portability), which is not yet written; neither exists in this repository today.
- **No `PosixRelPath` Pydantic `Annotated` alias in `acf.engine` yet:** Because `acf.engine` is stdlib-only and `parse_host_detector_ref` calls `validate_posix_rel_path` directly, adding an unused `PosixRelPath` alias in Spec 2a would violate `## Live consumers` (`config/architecture/ARCHITECTURE.md:153-157`). Spec 2b will wrap `validate_posix_rel_path` in `Annotated[str, AfterValidator(validate_posix_rel_path)]` where `ReviewHostConfig` consumes it.
- **No changes to `HistoricMansions` in this slice:** Porting HM's 17 AST detectors and 25 guards to `<posix_rel_path.py>:<callable_name>` in `hm:config/architecture/mandates.yml` belongs to Slice 3 (HM cutover).

---

## 4. Design

### 4.1 Relative POSIX Path Validator (`plugins/arch-compliance/python/acf/engine.py`)

`plugins/arch-compliance/python/acf/engine.py` remains stdlib-only (`import re`, `from pathlib import Path`) and adds `validate_posix_rel_path`:

```python
_WIN_DRIVE_PREFIX_RE = re.compile(r"^[A-Za-z]:")


def validate_posix_rel_path(value: str) -> str:
    """Validate that ``value`` is a non-empty, normalized POSIX relative path.

    Refuses empty/whitespace strings, leading/trailing whitespace, backslashes
    (via ``contains_backslash``), leading or trailing ``/``, Windows drive
    prefixes (``C:``), empty segments (``//``), and ``.`` or ``..`` segments.
    """
    if not isinstance(value, str) or not value or not value.strip() or value != value.strip():
        raise ValueError(f"path must be a non-empty relative POSIX path: {value!r}")
    if contains_backslash(value):
        raise ValueError(f"path must be POSIX (no backslashes): {value!r}")
    if value.startswith("/") or value.endswith("/") or _WIN_DRIVE_PREFIX_RE.match(value):
        raise ValueError(f"path must be relative POSIX (no leading/trailing '/' or drive): {value!r}")
    parts = value.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise ValueError(f"path must not contain empty, '.' or '..' segments: {value!r}")
    return value
```

### 4.2 Host Detector Loader and Runner (`plugins/arch-compliance/python/acf/detectors/host.py`)

Create `plugins/arch-compliance/python/acf/detectors/host.py` as the single owner for parsing, importing, and executing host `ast` and `guard` detectors:

1. **Call-site constants:**
   ```python
   DIFF_CALL_SITES: frozenset[str] = frozenset({"ci", "precommit"})
   HOOK_CALL_SITES: frozenset[str] = frozenset({"hook", "posttooluse"})
   TIER1_CALL_SITES: frozenset[str] = DIFF_CALL_SITES | HOOK_CALL_SITES
   ```
2. **Reference predicate and parser (`is_host_detector_ref`, `parse_host_detector_ref`):**
   - `is_host_detector_ref(detector: str) -> bool`: returns `":" in detector`.
   - `parse_host_detector_ref(detector: str) -> tuple[str, str]`:
     - Requires `":" in detector`; splits `rel_path, attr_name = detector.split(":", 1)`.
     - If `":" in attr_name` or `not attr_name.isidentifier()`: raises `UnknownDetectorError(f"invalid host detector callable name in {detector!r}; expected '<posix_rel_path.py>:<callable_name>'")`.
     - Calls `validate_posix_rel_path(rel_path)` inside `try ... except ValueError as exc: raise UnknownDetectorError(f"invalid host detector path in {detector!r}: {exc}") from exc`.
     - Requires `rel_path.endswith(".py")` and `not rel_path.endswith("/.py")` and `len(rel_path) > 3`; else raises `UnknownDetectorError(f"host detector path must be a '.py' file in {detector!r}")`.
     - Returns `(rel_path, attr_name)`.
3. **Module and callable loader (`load_host_detector(repo_root: Path, detector: str) -> Callable[..., Sequence[Finding]]`):**
   - Calls `rel_path, attr_name = parse_host_detector_ref(detector)`.
   - Resolves `root = repo_root.resolve()` and `module_path = (root / rel_path).resolve()`.
   - Verifies `module_path.is_relative_to(root)` and `module_path.is_file()`; if not, raises `UnknownDetectorError(f"host detector file not found for {detector!r}: {(root / rel_path).as_posix()}")`.
   - Caches loaded modules in `_MODULE_CACHE: dict[tuple[str, str, int, int], ModuleType]` keyed by `(root.as_posix(), rel_path, stat.st_mtime_ns, stat.st_size)` so:
     - Multiple detectors in the same module (e.g. 17 AST functions in one `.py` file) import the module once per run;
     - Separate `tmp_path` repositories in test suites never collide;
     - Edits to a detector file on disk invalidate the cache entry automatically.
   - On cache miss:
     - Ensures `str(root)` is at the front of `sys.path` if not already present in `sys.path`, so intra-repo imports inside the host module resolve against `root`.
     - Builds a module spec via `importlib.util.spec_from_file_location(module_name, module_path)`, registers `sys.modules[module_name] = mod` before `spec.loader.exec_module(mod)` (so `@dataclass` and `from __future__ import annotations` lookups against `sys.modules[cls.__module__]` succeed), and removes `sys.modules[module_name]` on any exception during `exec_module`, raising `UnknownDetectorError(f"failed to import host detector module {rel_path!r} for {detector!r}: {exc}") from exc`.
   - Looks up `fn = getattr(mod, attr_name, None)`. If `not callable(fn)`, raises `UnknownDetectorError(f"host detector {detector!r} has no callable {attr_name!r} in {rel_path!r}")`.
   - Returns `fn`.
4. **Finding validation and normalization (`_normalize_findings(raw: object, mandate: Mandate) -> list[Finding]`):**
   - If `raw is None` or `isinstance(raw, (str, bytes))` or `not isinstance(raw, Iterable)`:
     raises `DetectorPackError(f"host detector {mandate.detector!r} for mandate {mandate.id!r} must return an iterable of Finding, got {type(raw).__name__}")`.
   - Iterates over `raw`; for each item `f`:
     - If `not isinstance(f, Finding)`: raises `DetectorPackError(f"host detector {mandate.detector!r} for mandate {mandate.id!r} yielded {type(f).__name__}, expected Finding")`.
     - If `contains_backslash(f.path)` or `not f.path.strip()`: raises `DetectorPackError(f"host detector {mandate.detector!r} for mandate {mandate.id!r} emitted invalid or non-POSIX path {f.path!r}")`.
     - If `f.line < 1`: raises `DetectorPackError(f"host detector {mandate.detector!r} for mandate {mandate.id!r} emitted invalid line {f.line} (must be >= 1)")`.
     - Appends `f.model_copy(update={"mandate_id": mandate.id, "detector": mandate.detector, "detection": mandate.detection})`.
5. **Per-file host `ast` runner (`scan_host_ast_file`):**
   ```python
   def scan_host_ast_file(
       repo_root: Path,
       text: str,
       path: str,
       added_lines: frozenset[int] | None,
       registry: MandateRegistry,
       *,
       language: Literal["python", "typescript"],
       allowed_call_sites: frozenset[str],
   ) -> list[Finding]:
   ```
   - Filters `mandates = [m for m in registry.mandates if m.status != "unenforced" and m.detection == "ast" and is_host_detector_ref(m.detector) and m.languages in {language, "both"} and bool(set(m.call_sites) & allowed_call_sites)]`.
   - If `not mandates`, returns `[]`.
   - If `language == "python"`: parses `tree = ast.parse(text)` once; on `SyntaxError`, returns `[]`. Else `tree = None`.
   - Normalizes `posix = posix_path(path)`.
   - For each `mandate` in `mandates`:
     - Calls `fn = load_host_detector(repo_root, mandate.detector)`.
     - Calls `raw = fn(text, posix, added_lines, tree=tree, params=mandate.params)` inside `try ... except AcfError: raise except Exception as exc: raise DetectorPackError(f"host ast detector {mandate.detector!r} for mandate {mandate.id!r} failed on {posix!r}: {exc}") from exc`.
     - Extends `findings` with `_normalize_findings(raw, mandate)`.
   - Returns `findings`.
6. **Repo/diff-level host `guard` runner (`scan_host_guards`):**
   ```python
   def scan_host_guards(
       repo_root: Path,
       changed_files: Sequence[str],
       registry: MandateRegistry,
       *,
       allowed_call_sites: frozenset[str],
   ) -> list[Finding]:
   ```
   - Filters `mandates = [m for m in registry.mandates if m.status != "unenforced" and m.detection == "guard" and is_host_detector_ref(m.detector) and bool(set(m.call_sites) & allowed_call_sites)]`.
   - If `not mandates`, returns `[]`.
   - Normalizes `posix_changed = tuple(posix_path(p) for p in changed_files)` and `root = repo_root.resolve()`.
   - For each `mandate` in `mandates`:
     - Calls `fn = load_host_detector(root, mandate.detector)`.
     - Calls `raw = fn(root, posix_changed, params=mandate.params)` inside `try ... except AcfError: raise except Exception as exc: raise DetectorPackError(f"host guard detector {mandate.detector!r} for mandate {mandate.id!r} failed: {exc}") from exc`.
     - Extends `findings` with `_normalize_findings(raw, mandate)`.
   - Returns `findings`.

### 4.3 Registry Validation (`plugins/arch-compliance/python/acf/registry.py:48-64`)

Update `load_mandates` in `plugins/arch-compliance/python/acf/registry.py:48-64`:

```python
def load_mandates(
    path: Path,
    *,
    known_detectors: frozenset[str] | None = None,
    repo_root: Path | None = None,
) -> MandateRegistry:
    from acf.detectors.host import (
        TIER1_CALL_SITES,
        is_host_detector_ref,
        load_host_detector,
        parse_host_detector_ref,
    )

    mandates = load_model_file(
        path, Mandate, subject="mandates file", fmt="yaml", many=True
    )
    for m in mandates:
        if m.detection in {"ast", "guard"} and is_host_detector_ref(m.detector):
            parse_host_detector_ref(m.detector)
    if known_detectors is not None:
        for m in mandates:
            if m.status == "unenforced" or m.detection not in {"ast", "guard"}:
                continue
            if is_host_detector_ref(m.detector):
                if repo_root is None:
                    raise AcfInputError(
                        f"active mandate {m.id!r} uses host detector {m.detector!r}; "
                        "pass repo_root to load_mandates"
                    )
                if not (set(m.call_sites) & TIER1_CALL_SITES):
                    raise AcfInputError(
                        f"active mandate {m.id!r} with host detector {m.detector!r} "
                        f"must declare at least one Tier-1 call site in {sorted(TIER1_CALL_SITES)}, "
                        f"got {m.call_sites!r}"
                    )
                load_host_detector(repo_root, m.detector)
            elif m.detector not in known_detectors:
                raise UnknownDetectorError(
                    f"active mandate {m.id!r} references unknown detector {m.detector!r}"
                )
    return MandateRegistry(mandates=mandates, source_path=path.as_posix())
```

### 4.4 Shared Line Lookup (`plugins/arch-compliance/python/acf/enforcement.py`)

Add `make_line_lookup` to `plugins/arch-compliance/python/acf/enforcement.py`:

```python
def make_line_lookup(
    repo_root: Path,
    file_lines: dict[str, list[str]],
) -> LineLookup:
    """Build a ``LineLookup`` backed by ``file_lines`` with on-demand repo file reads."""
    root = repo_root.resolve()

    def _lookup(posix: str, line: int) -> str:
        lines = file_lines.get(posix)
        if lines is None and not contains_backslash(posix):
            candidate = (root / posix).resolve()
            if candidate.is_relative_to(root) and candidate.is_file():
                try:
                    lines = candidate.read_text(encoding="utf-8", errors="replace").splitlines()
                except OSError:
                    lines = []
                file_lines[posix] = lines
        if not lines or not (0 < line <= len(lines)):
            return ""
        return lines[line - 1]

    return _lookup
```

### 4.5 Wiring `cli_check_diff.py` and `hooks/posttooluse_gate.py`

1. **`plugins/arch-compliance/python/acf/cli_check_diff.py`:**
   - Line 70: pass `repo_root=repo` into `load_mandates(mandates_path, known_detectors=KNOWN_DETECTORS, repo_root=repo)`.
   - Lines 76-82: replace the inline `_line_lookup` closure with `findings = apply_registry(raw_findings, registry, make_line_lookup(repo, file_lines))`.
   - In `_scan_changed` (`plugins/arch-compliance/python/acf/cli_check_diff.py:124-184`):
     - For `.py` files (after `scan_fsm_writes` at line 150): append `findings.extend(scan_host_ast_file(repo, text, posix, lines, registry, language="python", allowed_call_sites=DIFF_CALL_SITES))`.
     - For `.ts` / `.tsx` files (lines 151-156): read `text = abs_path.read_text(encoding="utf-8")`, set `file_lines[posix] = text.splitlines()`, run `scan_typescript_file`, and append `findings.extend(scan_host_ast_file(repo, text, posix, lines, registry, language="typescript", allowed_call_sites=DIFF_CALL_SITES))`.
     - After `scan_ratchet` (line 182): append `findings.extend(scan_host_guards(repo, changed, registry, allowed_call_sites=DIFF_CALL_SITES))`.
2. **`plugins/arch-compliance/hooks/posttooluse_gate.py`:**
   - Lines 91-118: import `KNOWN_DETECTORS` from `acf.cli_check_diff`, `make_line_lookup` from `acf.enforcement`, and `UnknownDetectorError` from `acf.exceptions`; call `registry = load_mandates(mandates_path, known_detectors=KNOWN_DETECTORS, repo_root=repo)` catching `(AcfInputError, UnknownDetectorError)`; and replace the inline `_line_lookup` closure at lines 119-125 with `findings = apply_registry(raw_findings, registry, make_line_lookup(repo, file_lines))`.
   - In `_scan_paths` (`plugins/arch-compliance/hooks/posttooluse_gate.py:213-295`):
     - Import `HOOK_CALL_SITES`, `scan_host_ast_file`, and `scan_host_guards` from `acf.detectors.host`.
     - For `.py` files (after `scan_fsm_writes` at line 277): append `findings.extend(scan_host_ast_file(repo, text, rel, None, registry, language="python", allowed_call_sites=HOOK_CALL_SITES))`.
     - For `.ts` / `.tsx` files (after `scan_typescript_file` at line 282): append `findings.extend(scan_host_ast_file(repo, text, rel, None, registry, language="typescript", allowed_call_sites=HOOK_CALL_SITES))`.
     - After `scan_build_artifact_paths` (line 294): append `findings.extend(scan_host_guards(repo, rel_paths, registry, allowed_call_sites=HOOK_CALL_SITES))`.
3. **`tests/test_self_host.py:23`:**
   - Update `_registry()` to `return load_mandates(ROOT / MANDATES_REL, known_detectors=KNOWN_DETECTORS, repo_root=ROOT)`.

### 4.6 Doctrine, Skill Prose, Design Doc, and Version Alignment

1. **`config/architecture/ARCHITECTURE.md`:**
   - Add a `## Host detector extension and trust boundary` section (ending with `No row: enforced by plugins/arch-compliance/tests/test_host_detectors.py, plugins/arch-compliance/tests/test_registry.py, plugins/arch-compliance/tests/test_diff_cli.py, and plugins/arch-compliance/tests/test_hooks.py.`) recording the `<posix_rel_path.py>:<callable_name>` host detector contract for `detection: ast` and `detection: guard`, the `DIFF_CALL_SITES` (`ci`, `precommit`) and `HOOK_CALL_SITES` (`hook`, `posttooluse`) dispatch rule, and the `.acf/enabled` trust boundary.
2. **`plugins/arch-compliance/skills/acf-mandate/SKILL.md`:**
   - Update lines 41, 55, 58, 68, 88-112, 120, 122, and 138 to document host detector references (`<posix_rel_path.py>:<callable_name>`), the `scan_ast` and `scan_guard` signatures, the requirement that active (`enforced` or `partial`) `ast`/`guard` rows resolve to an existing built-in or host detector (using `status: unenforced` until a missing detector stub is implemented), and pass `repo_root=repo` in the `## Validate` snippet (`:88-103`) via `repo = resolve_repo()`.
3. **`plugins/arch-compliance/skills/acf-setup/SKILL.md`:**
   - Update `## Step 7 — Enable hooks marker` (`:140-151`) to state that `.acf/enabled` is the trust opt-in marker for executing host-defined `<posix_rel_path.py>:<callable_name>` detectors in `PostToolUse` and `acf-check-diff`.
4. **`docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:184`:**
   - Update `- Unknown detector id referenced by an enforced ast or guard row → drift/registry validation fail.` to `- Unknown built-in detector id or unresolvable host detector reference (<posix_rel_path.py>:<callable_name>) referenced by an active (enforced or partial) ast or guard row → drift/registry validation fail.`
5. **Version bump (`## Release discipline`, `config/architecture/ARCHITECTURE.md:184-187`):**
   - Bump `version` from `"0.2.2"` to `"0.2.3"` in `pyproject.toml:3` and `plugins/arch-compliance/.claude-plugin/plugin.json:3`.

---

## 5. Document Relationships and Shape Fit

### 5.1 Document Relationships

| Document | Relationship | Scope & Disposition |
|---|---|---|
| `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md` | `ADJACENT` | Parent v1 architecture spec for the plugin; lines 102, 123, 125 already call for project-specific detector extension points, and line 184 is updated in lockstep (§4.6 item 4). Kept separate because `ARCH_COMPLIANCE_FOR_SUPERPOWERS.md` covers the entire plugin across Tiers 0–3, skills, hooks, and profiles. |
| `docs/design/ADR_GATE_HOST_CONTRACT.md` | `DISJOINT` | Governs the adversarial-design-review gate (`acf.adr`). `hooks/posttooluse_gate.py` remains isolated from `acf.adr` (`plugins/arch-compliance/tests/test_adr_import_graph.py:70-76`). |
| `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` | `ADJACENT` | Governs self-hosting this repository under `config/architecture/` and `tests/test_self_host.py`. `tests/test_self_host.py:23` passes `repo_root=ROOT` to `load_mandates` (§4.5 item 3). Kept separate because `PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` is a completed Phase 1 spec. |
| `docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md` | `DISJOINT` | Governs the Tier-2 LLM judge (`acf.judge`, `acf.cli_check_llm`). |
| `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md` | `DISJOINT` | Governs the `post-merge-housekeeping` skill (`plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md`). |

### 5.2 Shape Fit Table

| New / Modified Element | Existing Site | Relationship & Resolution |
|---|---|---|
| `validate_posix_rel_path` in `plugins/arch-compliance/python/acf/engine.py` | `contains_backslash` in `plugins/arch-compliance/python/acf/engine.py:17-25` and `PosixStr` in `plugins/arch-compliance/python/acf/adr/contract.py:129` | `ADJACENT` — `validate_posix_rel_path` delegates backslash refusal to `contains_backslash` in the same stdlib-only `acf.engine` module while adding relative-path checks (no leading/trailing `/`, no Windows drive prefix, no `.` or `..` segments); kept outside `acf.adr` because `hooks/posttooluse_gate.py` is forbidden from importing `acf.adr` (`plugins/arch-compliance/tests/test_adr_import_graph.py:70-76`). |
| `plugins/arch-compliance/python/acf/detectors/host.py` (`is_host_detector_ref`, `parse_host_detector_ref`, `load_host_detector`, `scan_host_ast_file`, `scan_host_guards`) | `plugins/arch-compliance/python/acf/detectors/__init__.py:1-35`, `plugins/arch-compliance/python/acf/detectors/python_pack.py:27-52` | `ADJACENT` — sibling detector module under `acf.detectors` owning host `<posix_rel_path.py>:<callable_name>` resolution and execution; consumed by `acf.registry.load_mandates`, `acf.cli_check_diff._scan_changed`, and `hooks/posttooluse_gate._scan_paths`. |
| `make_line_lookup` in `plugins/arch-compliance/python/acf/enforcement.py` | Duplicate `_line_lookup` closures in `plugins/arch-compliance/python/acf/cli_check_diff.py:76-81` and `plugins/arch-compliance/hooks/posttooluse_gate.py:119-124` | `IDENTICAL` (consolidated) — deletes both duplicate `_line_lookup` closures and replaces them with one canonical `make_line_lookup` in `acf.enforcement`. |
| Host detector validation in `load_mandates` (`plugins/arch-compliance/python/acf/registry.py:48-64`) | Built-in detector check in `plugins/arch-compliance/python/acf/registry.py:56-63` | Extends `load_mandates` in-place rather than introducing a second validator function. |

---

## 6. Doctrine Compliance

| Doctrine Anchor (`config/architecture/ARCHITECTURE.md`) | Mandate ID (`config/architecture/mandates.yml`) | How This Design Complies |
|---|---|---|
| `## Fail loud` (`:24-41`) | `fail-loud.bare-except` | Malformed `<posix_rel_path.py>:<callable_name>` syntax, missing `.py` files, import errors, and non-callable targets raise `UnknownDetectorError`. Active host detector rows without `repo_root` or without a Tier-1 call site raise `AcfInputError`. Exceptions or invalid return shapes from a host detector callable raise `DetectorPackError`. `hooks/posttooluse_gate.py` now passes `known_detectors=KNOWN_DETECTORS, repo_root=repo` and catches `UnknownDetectorError`. |
| `## No shims` (`:43-53`) | `no-shims.hasattr` | Uses `getattr(mod, attr_name, None)` with `callable(...)` rather than `hasattr`. No silent fallback when a host detector fails to import or raises. |
| `## POSIX paths` (`:55-64`) | `posix-paths.str-serialization` | `validate_posix_rel_path` refuses backslashes via `contains_backslash`, and `_normalize_findings` refuses any `Finding` whose `path` contains a backslash. |
| `## One base exception` (`:99-103`) | `plugin.one-base-exception` | Reuses `AcfInputError`, `UnknownDetectorError`, and `DetectorPackError` (`plugins/arch-compliance/python/acf/exceptions.py:5-30`), all subclassing `AcfError` alone. |
| `## One owner for host paths` (`:105-116`) | `plugin.one-owner-host-paths` | Neither `acf/engine.py` nor `acf/detectors/host.py` spells `config/architecture`; `plugins/arch-compliance/skills/acf-mandate/SKILL.md` continues to import `ARCH_REL`, `MANDATES_REL`, and `resolve_repo` from `acf.repo`. |
| `## Declared, never defaulted` (`:118-133`) | `plugin.declared-never-defaulted` | When `load_mandates` validates an active host detector row with `known_detectors is not None`, it requires explicit `repo_root: Path` and raises `AcfInputError` if `repo_root is None` rather than guessing `path.parents[2]`. |
| `## Prose names no host` (`:135-143`) | `plugin.adr-code-names-no-host`, `plugin.gate-prose-names-no-host` | Runtime messages and skill prose in `acf-mandate` and `acf-setup` name no origin host (`HistoricMansions`, `GEMINI.md`, etc.). |
| `## Live consumers` (`:153-157`) | *(doctrine rule)* | Every added function and constant has a live runtime call site: `validate_posix_rel_path` is called by `parse_host_detector_ref`; `DIFF_CALL_SITES`, `HOOK_CALL_SITES`, `TIER1_CALL_SITES`, `is_host_detector_ref`, `parse_host_detector_ref`, `load_host_detector`, `scan_host_ast_file`, and `scan_host_guards` are called by `load_mandates`, `cli_check_diff.py`, and `hooks/posttooluse_gate.py`; `make_line_lookup` is called by `cli_check_diff.py` and `hooks/posttooluse_gate.py`. |
| `## Declared text decoding` (`:171-182`) | *(doctrine rule)* | Every `read_text` call added or touched (`cli_check_diff.py`, `enforcement.py`, `acf-mandate/SKILL.md`) declares `encoding="utf-8"`. |
| `## Release discipline` (`:184-194`) | *(doctrine rule)* | Bumps `version` from `"0.2.2"` to `"0.2.3"` in `pyproject.toml:3` and `plugins/arch-compliance/.claude-plugin/plugin.json:3` because `skills/acf-mandate/SKILL.md` and `skills/acf-setup/SKILL.md` prose changes. |
| `## Single point of definition` (`:196-209`) | *(doctrine rule)* | `acf.detectors.host` is the single owner of host detector parsing, loading, and execution across `load_mandates`, `cli_check_diff.py`, and `hooks/posttooluse_gate.py`; `make_line_lookup` in `acf.enforcement` consolidates the two duplicate `_line_lookup` closures. |

---

## 7. Mechanism and Hardening Trace

| Added / Updated Mechanism | Producer (`file:line` target) | Consumer (`file:line` target) | Failure-Mode Guard |
|---|---|---|---|
| `validate_posix_rel_path` | `plugins/arch-compliance/python/acf/engine.py` (`validate_posix_rel_path`) | `plugins/arch-compliance/python/acf/detectors/host.py` (`parse_host_detector_ref` calling `validate_posix_rel_path(rel_path)`) | Rejects empty/whitespace strings, backslashes, leading/trailing `/`, Windows drive letters, empty segments (`//`), and `.` or `..` segments with `ValueError` (translated to `UnknownDetectorError` by `parse_host_detector_ref`). |
| `parse_host_detector_ref` & `load_host_detector` | `plugins/arch-compliance/python/acf/detectors/host.py` (`parse_host_detector_ref`, `load_host_detector`) | `plugins/arch-compliance/python/acf/registry.py:48-64` (`load_mandates`), `plugins/arch-compliance/python/acf/detectors/host.py` (`scan_host_ast_file`, `scan_host_guards`) | Raises `UnknownDetectorError` on malformed `<posix_rel_path.py>:<callable_name>`, missing `.py` file, module import exception, or missing/non-callable attribute; raises `AcfInputError` in `load_mandates` when `repo_root is None` or `call_sites` lacks a Tier-1 site. |
| `scan_host_ast_file` & `scan_host_guards` | `plugins/arch-compliance/python/acf/detectors/host.py` (`scan_host_ast_file`, `scan_host_guards`) | `plugins/arch-compliance/python/acf/cli_check_diff.py:102-184` (`_scan_changed`) and `plugins/arch-compliance/hooks/posttooluse_gate.py:213-295` (`_scan_paths`) | Shares one `ast.parse(text)` per `.py` file across all active Python host `ast` detectors; normalizes `mandate_id`, `detector`, `detection` on every returned `Finding`; raises `DetectorPackError` on callable exceptions, non-`Finding` items, backslash paths, or `line < 1`. |
| `make_line_lookup` | `plugins/arch-compliance/python/acf/enforcement.py` (`make_line_lookup`) | `plugins/arch-compliance/python/acf/cli_check_diff.py:76-82` (`main`) and `plugins/arch-compliance/hooks/posttooluse_gate.py:119-125` (`main`) | Populates `file_lines[posix]` on demand from `(repo_root / posix)` when a `guard` detector flags a file outside the pre-read `.py`/`.ts`/`.tsx` diff cache, so `apply_registry` honors inline `exemption_tokens` on any repo file. |

---

## 8. Verification and Definition of Done

1. **`validate_posix_rel_path` unit tests (`plugins/arch-compliance/tests/test_engine_paths.py`):**
   - Accepts valid relative POSIX paths (`"scripts/ci/guard.py"`, `"a/b/c.py"`, `"guard.py"`).
   - Rejects `""`, `"   "`, `" a/b.py"`, backslash-containing paths (`"a" + chr(92) + "b.py"`), `"/a/b.py"`, `"a/b/"`, `"C:/a/b.py"`, `"C:a/b.py"`, `"a//b.py"`, `"./a.py"`, `"a/./b.py"`, `"../a.py"`, and `"a/../b.py"` with `ValueError`.
2. **Host detector parser, loader, and runner unit tests (`plugins/arch-compliance/tests/test_host_detectors.py`):**
   - `parse_host_detector_ref` accepts `"scripts/guards/my_guard.py:scan_guard"` and rejects missing `:`, multiple `:`, non-`.py` paths, backslash/`..`/leading-`/` paths, and non-identifier callable names with `UnknownDetectorError`.
   - `load_host_detector` loads a callable from a host `.py` file (including a module that imports a sibling package from `repo_root` and defines a `@dataclass(frozen=True)` class under `from __future__ import annotations`), caches the module across multiple detector functions in the same file, and raises `UnknownDetectorError` when the file is missing, fails to import, or lacks a callable attribute.
   - `scan_host_ast_file` parses a `.py` file once (`ast.parse` spy count `== 1` when two host `ast` mandates run on the same `.py` file), passes `tree` and `params`, filters by `languages` and `allowed_call_sites`, normalizes `mandate_id` / `detector` / `detection` on returned `Finding` rows, and wraps callable exceptions or invalid return items/backslash paths into `DetectorPackError`.
   - `scan_host_guards` passes `(repo_root, posix_changed, params=mandate.params)`, filters by `allowed_call_sites`, and normalizes findings.
3. **Registry validation tests (`plugins/arch-compliance/tests/test_registry.py`):**
   - `load_mandates` rejects malformed `<path>:<callable>` syntax with `UnknownDetectorError` even when `status: unenforced` or `known_detectors=None`.
   - When `known_detectors=KNOWN_DETECTORS`, `load_mandates` rejects an active (`enforced` or `partial`) host detector row when `repo_root is None` (`AcfInputError`), when `call_sites` contains no Tier-1 site (`AcfInputError`), or when the `.py` file or callable does not exist (`UnknownDetectorError`), and accepts an `enforced` host detector row when the `.py` file and callable exist under `repo_root`.
4. **End-to-end CLI and Hook tests (`plugins/arch-compliance/tests/test_diff_cli.py`, `plugins/arch-compliance/tests/test_hooks.py`):**
   - `cli_check_diff.main` executes active host `ast` and `guard` detectors (`call_sites: [ci]` / `[precommit]`), honors `exemption_tokens` (including on a file flagged by a host `guard` that was not in the staged `.py` diff, via `make_line_lookup`), and exits `1` on `BLOCK` findings.
   - `hooks/posttooluse_gate.py` exits `0` without importing any host detector module when `.acf/enabled` is absent (even if `mandates.yml` points at a module that raises `RuntimeError("must not import")` at top level), fails loud (exit `1`) when `.acf/enabled` is present and an active row has an unknown built-in or missing host detector, executes active host `ast` and `guard` detectors whose `call_sites` intersects `{"hook", "posttooluse"}`, and skips host `guard` rows with `call_sites: [ci]`.
5. **Skill, self-host, and diff-gate checks:**
   - `plugins/arch-compliance/tests/test_acf_mandate_skill.py` and `tests/test_self_host.py` pass.
   - `pyproject.toml:3` and `plugins/arch-compliance/.claude-plugin/plugin.json:3` are bumped to `"0.2.3"`.
   - `PYTHONUTF8=1 python -m pytest -q`, `PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main`, and `npm test --prefix plugins/arch-compliance/detectors/typescript` pass.
6. **Adversarial design review gate:**
   - This spec clears `/adversarial-design-review`, with its run detail under `docs/reviews/adr_runs/` and its `LedgerRow` in `docs/reviews/adversarial_design_ledger.jsonl` committed on the branch.

---

## Appendix — Premise Verification Receipts at `a338cad`

| Premise | Command | Observed output at `a338cad` |
|---|---|---|
| `load_mandates` call sites across runtime, hooks, skills, and tests | `git grep -n "load_mandates" -- plugins/arch-compliance/python plugins/arch-compliance/hooks plugins/arch-compliance/skills plugins/arch-compliance/tests tests` | `hooks/inject_constraints.py:104`, `hooks/posttooluse_gate.py:107`, `python/acf/cli_check_diff.py:70`, `python/acf/cli_check_llm.py:54`, `python/acf/registry.py:48`, `skills/acf-mandate/SKILL.md:95`, `skills/architecture-review/SKILL.md:62`, `tests/test_profile_drift.py:24`, `tests/test_registry.py:10,17,30,47,57`, `tests/test_self_host.py:23` |
| Duplicate `_line_lookup` closures in `cli_check_diff.py` and `hooks/posttooluse_gate.py` | `git grep -n "_line_lookup" -- plugins/arch-compliance/python plugins/arch-compliance/hooks` | `plugins/arch-compliance/hooks/posttooluse_gate.py:119,125` and `plugins/arch-compliance/python/acf/cli_check_diff.py:76,82` |
| `acf.engine` has only `posix_path`, `contains_backslash`, and `is_in_scope` | Inspect `plugins/arch-compliance/python/acf/engine.py:1-31` | 31 lines; stdlib-only (`from pathlib import Path`); defines `posix_path` (`:11-14`), `contains_backslash` (`:17-25`), `is_in_scope` (`:27-31`) |
| `HM` has 17 `detection: ast` rows and 25 `detection: guard` rows in `hm:config/architecture/mandates.yml` | Count `detection == "ast"` and `detection == "guard"` in `hm:config/architecture/mandates.yml` at `b652fab05` | 17 enforced `ast` rows (matching the 17 keys of `DETECTOR_REGISTRY` in `hm:scripts/ci/arch_compliance/engine.py:1154-1173`, all `call_sites: [precommit, posttooluse, ci]`) and 25 enforced `guard` rows (`call_sites` in `[precommit, ci]`, `[ci]`, or `[precommit]`) |
| Current plugin version is `0.2.2` | Inspect `pyproject.toml:3` and `plugins/arch-compliance/.claude-plugin/plugin.json:3` | Both carry `"0.2.2"` |
