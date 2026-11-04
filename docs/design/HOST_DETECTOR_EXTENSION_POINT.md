# Host Detector Extension Point (`ast` and `guard` Callables)

**Status:** Draft (v2)
**Date:** 2026-11-04
**Spec kinds:** `defect`, `feature`
**Repo:** `IanDBallard/arch-compliance-for-superpowers`, `main` at `a338cad` (branch `feat/host-detector-extension`).
**Workstream:** HistoricMansions Workstream E Phase 2 (prerequisite Spec 2a — Tier-1 host detector extension point).
**Governing mandates:** `config/architecture/ARCHITECTURE.md` sections `## Fail loud` (`:24-41`), `## No shims` (`:43-53`), `## POSIX paths` (`:55-64`), `## One base exception` (`:99-103`), `## One owner for host paths` (`:105-116`), `## Declared, never defaulted` (`:118-133`), `## Prose names no host` (`:135-143`), `## Frozen ledger format` (`:145-151`), `## Live consumers` (`:153-157`), `## No completeness claims` (`:159-169`), `## Declared text decoding` (`:171-182`), `## Release discipline` (`:184-194`), `## Single point of definition` (`:196-209`), `## Scoped refactor` (`:211-215`), and the five portable governing principles at `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51`.
**No state-machine surface.** This design adds or modifies no state machine and no transition.

---

## 0. Citation convention

Unprefixed paths refer to this repository. Every cited line is as at `main` `a338cad`; the branch adds only files under `docs/` (recipe: `git diff --stat a338cad HEAD -- . ':!docs'` prints nothing). Paths prefixed `hm:` refer to the sibling repository `HistoricMansions` at `b652fab05` (`main`), following `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:10-32`. Every path is written in full with POSIX forward slashes.

---

## 1. Problem

`docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:102` defines `Mandate.detector` as *"Detector fn / guard module / LLM prompt id / manual verification pointer"*, and `:123` and `:125` each call for *"Extension points for project-specific detectors"*. At `a338cad` the plugin has no way to run a host-defined `detection: ast` or `detection: guard` detector, and its registry validation and gates disagree about which rows are live.

1. **A host detector can be declared but is never run, and only `enforced` rows are checked.**
   - `load_mandates` (`plugins/arch-compliance/python/acf/registry.py:48-64`) skips every row whose status is not `enforced` (`:58`) and raises `UnknownDetectorError` (`:60-63`) only for an `enforced` `ast`/`guard` row whose detector is not in `known_detectors`.
   - `KNOWN_DETECTORS` (`plugins/arch-compliance/python/acf/cli_check_diff.py:25`) is the closed union `ALL_PYTHON_DETECTOR_IDS | TS_DETECTOR_IDS | LLM_PROMPT_IDS`; nothing extends it (recipe: `git grep -n "KNOWN_DETECTORS" -- plugins tests`).
   - A `status: partial` row is live in both gates (`plugins/arch-compliance/python/acf/enforcement.py:47` drops only `unenforced`), yet `load_mandates` never checks it. So a host can name a detector of its own in a `partial` `ast`/`guard` row today, load cleanly with `known_detectors=KNOWN_DETECTORS`, and have nothing ever execute it.
   - Neither gate can execute a non-built-in detector: `_scan_changed` (`plugins/arch-compliance/python/acf/cli_check_diff.py:102-184`) and `_scan_paths` (`plugins/arch-compliance/hooks/posttooluse_gate.py:213-295`) call only built-in scanners, selected by exact built-in id (`cli_check_diff.py:94-99`, `posttooluse_gate.py:229-236`, `:284-286`). No dynamic loader exists to reuse: `git grep -n "importlib\|import_module\|spec_from_file_location\|exec_module" -- plugins/arch-compliance/python plugins/arch-compliance/hooks` prints nothing.
2. **The PostToolUse hook skips detector validation.** `plugins/arch-compliance/hooks/posttooluse_gate.py:107` calls `load_mandates(mandates_path)` without `known_detectors`, and `:108` catches only `AcfInputError`. `UnknownDetectorError` subclasses `AcfError`, not `AcfInputError` (`plugins/arch-compliance/python/acf/exceptions.py:5`, `:13`). An active row naming an unknown detector produces zero findings at edit time instead of failing loud.
3. **`call_sites` is declared but read by no gate.** `Mandate.call_sites` is `list[str]` (`plugins/arch-compliance/python/acf/registry.py:21`). The gates select rows on detector id and status only (`cli_check_diff.py:94-99`; `posttooluse_gate.py:229-236`, `:284-286`), and `apply_registry` on status only (`enforcement.py:47`); `git grep -n "call_sites" -- plugins/arch-compliance/python plugins/arch-compliance/hooks` prints only the field declaration at `registry.py:21` and two unrelated `surface_call_sites` lines in `plugins/arch-compliance/python/acf/adr/ledger.py`. This repository's `no-shims.hasattr` row declares `call_sites: [ci]` (`config/architecture/mandates.yml:70`), yet the hook reports it at edit time, and `plugins/arch-compliance/tests/test_hooks.py:199-218` pins that behaviour. Routing host detectors by `call_sites` without changing this would give one field two meanings.
4. **Exemptions are honoured only on files the gate pre-read.** The `_line_lookup` closures (`cli_check_diff.py:76-80`, `posttooluse_gate.py:119-123`) are token-identical and consult only `file_lines`, which holds changed `.py`/`.ts`/`.tsx` files (`cli_check_diff.py:126`, `:152`; `posttooluse_gate.py:248-252`). A finding on any other file gets `""`, so `apply_registry` (`enforcement.py:49-50`) cannot see an inline exemption token on it.
5. **Path-shape checks live only inside `acf.adr`.** `PosixStr` (`plugins/arch-compliance/python/acf/adr/contract.py:129`, via `_reject_backslash` at `:60`) refuses only backslashes; `_looks_absolute` (`plugins/arch-compliance/python/acf/adr/citations.py:49-51`) and `_escapes_repo` (`:74-76`) classify citation strings. `hooks/posttooluse_gate.py` may not reference `acf.adr` (`plugins/arch-compliance/tests/test_adr_import_graph.py:70-76`), so none of these serve a hook-reachable caller.

---

## 2. Decisions this design records

1. **Host detector reference syntax `<posix_rel_path.py>:<callable_name>`.** For `detection in {"ast", "guard"}`, a `detector` containing `":"` is a host reference; otherwise it is a built-in id. The path part is a relative POSIX path accepted by `validate_posix_rel_path` (§4.1) and ending in `.py`; the callable part satisfies `str.isidentifier()`.
2. **One definition of "this row runs at this gate", for built-in and host rows alike.**
   - `acf.registry` gains `DIFF_CALL_SITES = frozenset({"ci", "precommit"})`, `HOOK_CALL_SITES = frozenset({"hook", "posttooluse"})`, `TIER1_CALL_SITES = DIFF_CALL_SITES | HOOK_CALL_SITES`, the property `Mandate.is_active` (`status != "unenforced"`), the method `Mandate.runs_at(call_sites) -> bool` (`is_active` and `call_sites` intersects the row's `call_sites`), and `MandateRegistry.active(call_sites, *, detector=None, detection=None) -> list[Mandate]`.
   - `apply_registry` gains a required keyword `call_sites` and drops findings whose row does not `runs_at` it. `acf-check-diff` passes `DIFF_CALL_SITES`; the hook passes `HOOK_CALL_SITES`.
   - `cli_check_diff._active_mandates` and the hook's three inline filters are replaced by `registry.active(...)`.
   - Scope: the two Tier-1 gates only. The Tier-2 judge selects `llm` rows by detection and reads `status == "enforced"` only to decide whether a provider is required (`plugins/arch-compliance/python/acf/judge.py:213-218`); it is unchanged.
   - Consequence, accepted: a row declaring only `[ci]` (this repository's `no-shims.hasattr`) is no longer reported by the PostToolUse hook. `plugins/arch-compliance/tests/test_hooks.py:199-218` is rewritten (§4.6).
3. **Registry load validates; it never imports host code.** With `known_detectors` given, every active (`status != "unenforced"`) `ast`/`guard` row must (a) intersect `TIER1_CALL_SITES` (`AcfInputError`), and (b) name a built-in id in `known_detectors` or a host reference whose file exists under an explicit `repo_root` (`UnknownDetectorError`). An active host `ast` row must also declare `languages` in `{"python", "typescript", "both"}` (`AcfInputError`), because a `languages: none` row matches no file. A malformed host reference raises `AcfInputError` on every load, with or without `known_detectors`. Import and callable lookup happen only at dispatch (§4.3), so `load_mandates` runs no host code for any caller.
4. **Host callables return `HostHit`, never `Finding`.** `acf.detectors.host.HostHit` is a frozen Pydantic model with exactly `path` (validated by `validate_posix_rel_path`), `line` (`>= 1`) and `message` (non-empty). The runner builds each `Finding` from the hit and the mandate row, so a host cannot attach a finding to the wrong row and no field is overwritten.
5. **Trust boundary.**
   - Automatic hooks: the PostToolUse hook exits `0` before importing anything beyond `acf.repo` when `.acf/enabled` is absent (`plugins/arch-compliance/hooks/posttooluse_gate.py:72-81`). That marker is the opt-in for running host code on edit.
   - Explicit invocation: `acf-check-diff` runs only when the host's own pre-commit or CI configuration invokes it (this repository: `.github/workflows/ci.yml:40`). That invocation is the opt-in. `.acf/` is gitignored (`.gitignore:8`), so a CI checkout never carries the marker, and requiring it there would disable CI.
   - The SubagentStart hook (`plugins/arch-compliance/hooks/inject_constraints.py:104`) and `acf-check-llm` (`plugins/arch-compliance/python/acf/cli_check_llm.py:54`) call `load_mandates`, which never imports host code (Decision 3), so neither runs host code.

---

## 3. Scope and Non-Goals

### In scope

| File | Change |
|---|---|
| `plugins/arch-compliance/python/acf/engine.py` | Add `looks_absolute`, `resolve_under_root`, `validate_posix_rel_path` (§4.1). |
| `plugins/arch-compliance/python/acf/adr/citations.py` | `_looks_absolute` and `_escapes_repo` are deleted; their two call sites (`:161`, `:163`) call `acf.engine.looks_absolute` and `acf.engine.resolve_under_root` (§4.1). |
| `plugins/arch-compliance/python/acf/registry.py` | Call-site constants, `Mandate.runs_at`, `MandateRegistry.active`, `is_host_detector_ref`, `parse_host_detector_ref`, extended `load_mandates` (§4.2). |
| `plugins/arch-compliance/python/acf/detectors/host.py` (new) | `HostHit`, `load_host_detector`, `scan_host_ast_file`, `scan_host_guards` (§4.3). |
| `plugins/arch-compliance/python/acf/enforcement.py` | `apply_registry(..., *, call_sites)`; `make_line_lookup` (§4.4). |
| `plugins/arch-compliance/python/acf/cli_check_diff.py` | Wiring (§4.5). |
| `plugins/arch-compliance/hooks/posttooluse_gate.py` | Wiring (§4.5). |
| `plugins/arch-compliance/hooks/inject_constraints.py` | None: a malformed host reference raises `AcfInputError`, which `:105` already catches. |
| Tests, prose, version | §4.6 and §4.7. |

### Non-goals

- **No architecture-review runtime package and no architecture-review host configuration file.** Both belong to Spec 2b (architecture-review portability), not yet written. The recipe `git ls-files plugins/arch-compliance/python/acf | grep -i review` prints nothing at `a338cad`.
- **No `PosixRelPath` Pydantic alias in `acf.engine`.** `acf.engine` stays stdlib-only; `HostHit` applies `validate_posix_rel_path` through its own `AfterValidator`.
- **No change to `HistoricMansions` in this slice.** Its rows would still need rewriting at cutover: they carry no `languages` or `arch_anchor` field, both required by `Mandate` (`plugins/arch-compliance/python/acf/registry.py:20`, `:24`). Two behaviours of its driver are not reproduced by this contract and are left to the cutover spec: it reports unparseable files (`hm:scripts/ci/arch_compliance/driver.py:139-157`), while `scan_host_ast_file` skips them like the built-in scanners do, and its guards can depend on diff mode, which `scan_guard` does not receive. A host that needs parse-failure reporting declares it as a `guard`.
- **No shared Tier-1 dispatcher.** `_scan_changed` and `_scan_paths` differ in diff scope (added lines vs whole file), path collection and file filter. This design adds the same three host calls to each; extracting a common dispatcher is a separate refactor (`## Scoped refactor`, `config/architecture/ARCHITECTURE.md:211-215`).

---

## 4. Design

### 4.1 Path helpers (`plugins/arch-compliance/python/acf/engine.py`)

`acf.engine` stays stdlib-only (`import re`, `from pathlib import Path`) and owns the absolute-path test and the under-root test that this design and `acf/adr/citations.py` use. Other path handling in the plugin (for example `plugins/arch-compliance/hooks/posttooluse_gate.py:204` and `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:123`) resolves paths for I/O and is unchanged.

```python
_ABSOLUTE_RE = re.compile(r"^([A-Za-z]:|/|\\\\)")


def looks_absolute(path: str) -> bool:
    """True for a drive-prefixed (``C:`` or ``C:/``), root-anchored or UNC path."""
    return bool(_ABSOLUTE_RE.match(path))


def resolve_under_root(root: Path, rel: str) -> Path | None:
    """Resolve ``rel`` against ``root``; None when the result leaves ``root``."""
    base = root.resolve()
    candidate = (base / rel).resolve()
    return candidate if candidate.is_relative_to(base) else None


def validate_posix_rel_path(value: str) -> str:
    """Refuse anything but a normalized, relative POSIX path."""
    if not value or value != value.strip():
        raise ValueError(f"path must be a non-empty relative POSIX path: {value!r}")
    if contains_backslash(value):
        raise ValueError(f"path must be POSIX (no backslashes): {value!r}")
    if looks_absolute(value) or value.endswith("/"):
        raise ValueError(f"path must be relative with no trailing '/': {value!r}")
    if any(part in ("", ".", "..") for part in value.split("/")):
        raise ValueError(f"path must not contain empty, '.' or '..' segments: {value!r}")
    return value
```

`acf/adr/citations.py` imports `looks_absolute` and `resolve_under_root` and deletes its private copies. `resolve_citation` (`:129-185`) keeps its order (`proposed`, `asserted_absent`, then absolute → `external`, then escaping → `unresolved`), with `resolve_under_root(repo_root, path) is None` as the escape test. One classification changes: a drive-relative string such as `"C:a/b.py"` becomes `external` rather than going on to the existence checks.

### 4.2 Registry (`plugins/arch-compliance/python/acf/registry.py`)

```python
DIFF_CALL_SITES: frozenset[str] = frozenset({"ci", "precommit"})
HOOK_CALL_SITES: frozenset[str] = frozenset({"hook", "posttooluse"})
TIER1_CALL_SITES: frozenset[str] = DIFF_CALL_SITES | HOOK_CALL_SITES
_ACTIVE_HOST_AST_LANGUAGES = frozenset({"python", "typescript", "both"})


class Mandate(BaseModel):
    ...  # fields unchanged

    @property
    def is_active(self) -> bool:
        return self.status != "unenforced"

    def runs_at(self, call_sites: frozenset[str]) -> bool:
        return self.is_active and bool(call_sites.intersection(self.call_sites))


class MandateRegistry(BaseModel):
    ...  # unchanged

    def active(
        self,
        call_sites: frozenset[str],
        *,
        detector: str | None = None,
        detection: str | None = None,
    ) -> list[Mandate]:
        return [
            m for m in self.mandates
            if m.runs_at(call_sites)
            and (detector is None or m.detector == detector)
            and (detection is None or m.detection == detection)
        ]


def is_host_detector_ref(detector: str) -> bool:
    return ":" in detector


def parse_host_detector_ref(detector: str) -> tuple[str, str]:
    rel_path, _, attr = detector.partition(":")
    if not attr.isidentifier():
        raise AcfInputError(
            f"host detector {detector!r}: callable must be an identifier "
            "('<posix_rel_path.py>:<callable_name>')"
        )
    try:
        validate_posix_rel_path(rel_path)
    except ValueError as exc:
        raise AcfInputError(f"host detector {detector!r}: {exc}") from exc
    if not rel_path.endswith(".py") or rel_path.rsplit("/", 1)[-1] == ".py":
        raise AcfInputError(f"host detector {detector!r}: path must name a .py file")
    return rel_path, attr


def load_mandates(
    path: Path,
    *,
    known_detectors: frozenset[str] | None = None,
    repo_root: Path | None = None,
) -> MandateRegistry:
    mandates = load_model_file(path, Mandate, subject="mandates file", fmt="yaml", many=True)
    for m in mandates:
        if m.detection in {"ast", "guard"} and is_host_detector_ref(m.detector):
            parse_host_detector_ref(m.detector)
    if known_detectors is not None:
        for m in mandates:
            if not m.is_active or m.detection not in {"ast", "guard"}:
                continue
            if not TIER1_CALL_SITES.intersection(m.call_sites):
                raise AcfInputError(
                    f"active mandate {m.id!r} declares no Tier-1 call site "
                    f"{sorted(TIER1_CALL_SITES)}; got {m.call_sites!r}"
                )
            if not is_host_detector_ref(m.detector):
                if m.detector not in known_detectors:
                    raise UnknownDetectorError(
                        f"active mandate {m.id!r} references unknown detector {m.detector!r}"
                    )
                continue
            if repo_root is None:
                raise AcfInputError(
                    f"active mandate {m.id!r} uses host detector {m.detector!r}; "
                    "pass repo_root to load_mandates"
                )
            if m.detection == "ast" and m.languages not in _ACTIVE_HOST_AST_LANGUAGES:
                raise AcfInputError(
                    f"active host ast mandate {m.id!r} must declare languages in "
                    f"{sorted(_ACTIVE_HOST_AST_LANGUAGES)}; got {m.languages!r}"
                )
            rel_path, _ = parse_host_detector_ref(m.detector)
            module_path = resolve_under_root(repo_root, rel_path)
            if module_path is None or not module_path.is_file():
                raise UnknownDetectorError(
                    f"active mandate {m.id!r}: host detector file not found: "
                    f"{(repo_root / rel_path).as_posix()}"
                )
    return MandateRegistry(mandates=mandates, source_path=path.as_posix())
```

`registry.py` imports `resolve_under_root` and `validate_posix_rel_path` from `acf.engine`; it imports nothing from `acf.detectors`.

### 4.3 Host loader and runners (`plugins/arch-compliance/python/acf/detectors/host.py`)

1. **`HostHit`:**
   ```python
   class HostHit(BaseModel):
       model_config = ConfigDict(frozen=True, extra="forbid")
       path: Annotated[str, AfterValidator(validate_posix_rel_path)]
       line: int = Field(ge=1)
       message: str = Field(min_length=1)
   ```
2. **Callable signatures a host implements:**
   ```python
   def scan_ast(text: str, path: str, added_lines: frozenset[int] | None, *,
                tree: ast.Module | None, params: dict[str, Any] | None) -> Iterable[HostHit]: ...

   def scan_guard(repo_root: Path, changed_files: Sequence[str], *,
                  params: dict[str, Any] | None) -> Iterable[HostHit]: ...
   ```
3. **`load_host_detector(repo_root: Path, detector: str) -> Callable[..., Iterable[HostHit]]`:**
   - `rel_path, attr = parse_host_detector_ref(detector)`; `root = repo_root.resolve()`; `module_path = resolve_under_root(root, rel_path)`, and `UnknownDetectorError` if it is `None` or not a file.
   - **One host root per process.** A module-level `_ACTIVE_ROOT: Path | None` and `_MODULE_CACHE: dict[str, ModuleType]`, keyed by `rel_path`. When `root != _ACTIVE_ROOT`, the loader evicts the previous root: it removes every `sys.modules` entry whose `__file__` resolves under the old root, removes the old root's string from `sys.path`, clears `_MODULE_CACHE`, inserts `str(root)` at `sys.path[0]`, and sets `_ACTIVE_ROOT = root`. A host module's intra-repo imports (such as `hm:scripts/ci/metadata_facade_guard.py:66`, `from scripts.ci.arch_compliance.facade_sinks import ...`) therefore resolve against the current root only. Production callers are one process per gate run; the eviction keeps in-process test runs over several `tmp_path` roots isolated.
   - **Module name:** `"_acf_host_" + hashlib.sha256(f"{root.as_posix()}\0{rel_path}".encode()).hexdigest()[:16]`. The module is registered in `sys.modules` before `spec.loader.exec_module(mod)` and removed if `exec_module` raises. The import failure is re-raised as `UnknownDetectorError(f"failed to import host detector module {rel_path!r} for {detector!r}: {exc}")`. That `except Exception` line carries `# fail-loud.bare-except-ok: <reason>` (token at `config/architecture/mandates.yml:60`).
   - `fn = getattr(mod, attr, None)`; `UnknownDetectorError` if `not callable(fn)`.
4. **`_to_findings(raw: object, mandate: Mandate, *, expected_path: str | None) -> list[Finding]`:** refuses (`DetectorPackError`) a `raw` that is `None`, `str`, `bytes` or not iterable, any item that is not a `HostHit`, and, for `ast` rows, any hit whose `path != expected_path`. Each hit becomes `Finding(mandate_id=mandate.id, severity=Severity(mandate.severity), path=hit.path, line=hit.line, message=hit.message, detector=mandate.detector, detection=mandate.detection)`.
5. **`scan_host_ast_file(repo_root, text, path, added_lines, registry, *, language, call_sites) -> list[Finding]`:**
   - `mandates = [m for m in registry.active(call_sites, detection="ast") if is_host_detector_ref(m.detector) and m.languages in {language, "both"}]`; returns `[]` if none.
   - For `language == "python"`: `tree = ast.parse(text)` once, shared by every host `ast` detector on the file; on `SyntaxError` it returns `[]`, the convention of `scan_python_file` (`plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37`). Built-in scanners keep their own parses (unchanged). For TypeScript, `tree=None`.
   - Each callable is invoked as `fn(text, path, added_lines, tree=tree, params=mandate.params)`. Any exception it raises, `AcfError` included, becomes `DetectorPackError(f"host ast detector {mandate.detector!r} for mandate {mandate.id!r} failed on {path!r}: {exc}")`; that `except Exception` line carries `# fail-loud.bare-except-ok: <reason>`.
6. **`scan_host_guards(repo_root, changed_files, registry, *, call_sites) -> list[Finding]`:** selects `[m for m in registry.active(call_sites, detection="guard") if is_host_detector_ref(m.detector)]` and calls `fn(repo_root.resolve(), tuple(changed_files), params=mandate.params)`. Exceptions are wrapped as in item 5, and `_to_findings(..., expected_path=None)` builds the findings.

### 4.4 Enforcement (`plugins/arch-compliance/python/acf/enforcement.py`)

```python
def apply_registry(findings, registry, line_lookup, *, call_sites: frozenset[str]) -> list[Finding]:
    by_id = registry.by_id
    kept = []
    for finding in findings:
        mandate = by_id.get(finding.mandate_id)
        if mandate is None or not mandate.runs_at(call_sites):
            continue
        ...  # exemption and severity handling unchanged (:49-52)


def make_line_lookup(repo_root: Path, file_lines: dict[str, list[str]]) -> LineLookup:
    def _lookup(posix: str, line: int) -> str:
        lines = file_lines.get(posix)
        if lines is None:
            candidate = None if contains_backslash(posix) else resolve_under_root(repo_root, posix)
            lines = (
                candidate.read_text(encoding="utf-8", errors="replace").splitlines()
                if candidate is not None and candidate.is_file() else []
            )
            file_lines[posix] = lines
        return lines[line - 1] if 0 < line <= len(lines) else ""
    return _lookup
```

`make_line_lookup` reads with `errors="replace"`: an exemption token is ASCII, so a stray undecodable byte elsewhere on the line must neither crash `apply_registry` nor hide the token. An `OSError` from `read_text` propagates.

### 4.5 Wiring

1. **`plugins/arch-compliance/python/acf/cli_check_diff.py`:**
   - `:70`: `load_mandates(mandates_path, known_detectors=KNOWN_DETECTORS, repo_root=repo)`.
   - `:76-82`: `findings = apply_registry(raw_findings, registry, make_line_lookup(repo, file_lines), call_sites=DIFF_CALL_SITES)`.
   - `_active_mandates` (`:94-99`) is deleted; its four call sites (`:112`, `:113`, `:158`, `:168`) become `registry.active(DIFF_CALL_SITES, detector=...)`.
   - `.py` branch, after `scan_fsm_writes` (`:140-150`): `findings.extend(scan_host_ast_file(repo, text, posix, lines, registry, language="python", call_sites=DIFF_CALL_SITES))`.
   - `.ts`/`.tsx` branch (`:151-156`): bind `text = abs_path.read_text(encoding="utf-8")` and use it for `file_lines[posix]`, then `findings.extend(scan_host_ast_file(..., language="typescript", call_sites=DIFF_CALL_SITES))`.
   - After the ratchet loop (`:168-182`): `findings.extend(scan_host_guards(repo, changed, registry, call_sites=DIFF_CALL_SITES))`.
   - The `except` tuple at `:72` already lists `AcfInputError`, `UnknownDetectorError` and `DetectorPackError`.
2. **`plugins/arch-compliance/hooks/posttooluse_gate.py`:**
   - Deferred imports (`:91-104`) add `KNOWN_DETECTORS`, `HOOK_CALL_SITES`, `make_line_lookup`, `UnknownDetectorError`, `scan_host_ast_file` and `scan_host_guards`.
   - `:106-110`: `load_mandates(mandates_path, known_detectors=KNOWN_DETECTORS, repo_root=repo)` inside `except (AcfInputError, UnknownDetectorError)`.
   - `:113-117`: the scan `except` becomes `(DetectorPackError, UnknownDetectorError)`. Dispatch-time loading raises `UnknownDetectorError`; host callable failures arrive as `DetectorPackError` (§4.3).
   - `:119-125`: `findings = apply_registry(raw_findings, registry, make_line_lookup(repo, file_lines), call_sites=HOOK_CALL_SITES)`.
   - `_scan_paths`: the three inline filters (`:229-236`, `:284-286`) become `registry.active(HOOK_CALL_SITES, detector=...)`. Host dispatch is given only in-repo paths: a file outside `repo` (the fallback at `:244-245`) is excluded from `scan_host_ast_file` and from the list passed to `scan_host_guards`. The `.py` and TypeScript branches call `scan_host_ast_file(repo, text, rel, None, registry, language=..., call_sites=HOOK_CALL_SITES)`, and after the build-artifact loop (`:284-294`) `scan_host_guards(repo, in_repo_rel_paths, registry, call_sites=HOOK_CALL_SITES)` runs.
   - Docstring `:12` is reworded to state that the hook runs active rows declaring `hook` or `posttooluse`, including host detectors, which receive every edited in-repo path. Line `:11` stays verbatim: `plugins/arch-compliance/tests/test_repo_paths.py:47-48` pins its text.

### 4.6 Tests

| File | Change |
|---|---|
| `plugins/arch-compliance/tests/test_engine_paths.py` (new) | `validate_posix_rel_path` accepts `"scripts/ci/guard.py"`, `"a/b/c.py"`, `"guard.py"`. It rejects `""`, `" a.py"`, a backslash path, `"/a.py"`, `"a/"`, `"C:/a.py"`, `"C:a.py"`, `"a//b.py"`, `"./a.py"`, `"a/./b.py"`, `"../a.py"` and `"a/../b.py"`. `looks_absolute` and `resolve_under_root` get one positive and one negative case each. |
| `plugins/arch-compliance/tests/test_host_detectors.py` (new) | Loader: imports a module that imports a sibling package from the root and defines a `@dataclass(frozen=True)` class under `from __future__ import annotations`; caches across two callables in one file; raises `UnknownDetectorError` on a missing file, an import failure and a missing callable. Two `tmp_path` roots, each with a `"helpers/value.py"` returning a different constant, loaded in sequence, each see their own constant. Runners: one `ast.parse` for two host `ast` rows on a file (spy count `== 1`); filters by `languages` and `call_sites`; refuses a non-`HostHit` item, a mismatched `ast` path and a `str` return; wraps a raised `AcfInputError` as `DetectorPackError`. |
| `plugins/arch-compliance/tests/test_registry.py` | A malformed host reference raises `AcfInputError` with and without `known_detectors` and for an `unenforced` row. With `known_detectors`: an active `partial` unknown built-in raises `UnknownDetectorError`; an active row with only `[audit]` raises `AcfInputError`; a host row raises `AcfInputError` without `repo_root`, `AcfInputError` for an `ast` row with `languages: none`, and `UnknownDetectorError` for a missing file; an existing host file loads, and a module that raises at import time is not imported by `load_mandates`. |
| `plugins/arch-compliance/tests/test_enforcement.py` | Every `apply_registry` call (`:54`, `:60`, `:66`, `:72`, `:84`, `:94`, `:104`, `:110`, `:125`, `:130`) passes `call_sites=`. A new case drops a finding whose row lacks the given call site. |
| `plugins/arch-compliance/tests/test_hooks.py` | `:199-218` keeps its WARN-context coverage by setting the copied fixture's `no-shims.hasattr` row to `call_sites: [ci, hook]`. A new case asserts the hook does not report a `[ci]`-only row. New cases: exit `0` without importing a host module when `.acf/enabled` is absent (the module raises at import); exit `1` on an unknown detector when enabled; host `ast` and `guard` rows declaring `hook` run, `[ci]`-only host guards do not. |
| `plugins/arch-compliance/tests/test_diff_cli.py` | Host `ast` and `guard` rows declaring `ci` run and exit `1` on `BLOCK`; an exemption token on a non-code file flagged by a host guard is honoured. |
| `plugins/arch-compliance/tests/test_adr_citations.py` | A drive-relative citation (`"C:a/b.py"`) classifies `external`. Existing cases pass unchanged. |
| `tests/test_self_host.py` | `:23` passes `repo_root=ROOT`. |

### 4.7 Prose and version

| Site | Change |
|---|---|
| `config/architecture/ARCHITECTURE.md` | New `## Host detectors and call sites` section: the reference syntax, the `HostHit` contract, the call-site rule (Decision 2), and the trust boundary (Decision 5). It ends `No row: enforced by plugins/arch-compliance/tests/test_host_detectors.py, test_registry.py, test_hooks.py and test_diff_cli.py.` |
| `plugins/arch-compliance/skills/acf-mandate/SKILL.md` | `:10`, `:41`, `:43` (call-site vocabulary and its effect), `:55`, `:58`, `:68`, `:74`, `:88-112` (snippet uses `repo = resolve_repo(None)` and `load_mandates(repo / MANDATES_REL, known_detectors=KNOWN_DETECTORS, repo_root=repo)`), `:116`, `:120`, `:122`, `:138`. |
| `plugins/arch-compliance/skills/acf-mandate/SKILL.md` (call-site advice) | `:59` and `:79`: lowering or removing `call_sites` on a still-active `ast`/`guard` row must leave at least one Tier-1 site, or the row fails to load; deprecate with `status: unenforced` instead. |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md` | `## Step 7` (`:140-151`): `.acf/enabled` is the opt-in for the automatic hooks, host detectors included. `:159`: the PostToolUse row covers host detectors and edited non-code paths. |
| `README.md` | `:62`, `:76` and `:106`: the gates run active rows by `call_sites` (`:76` adds it to the status rule), and host guards see every changed path. `:108` unchanged. |
| `config/architecture/ARCHITECTURE.md:9-11` | The preamble's "run the registry's detectors on changed `.py`, `.ts` and `.tsx` files" adds that host guards see every changed path and that rows run where their `call_sites` say. |
| `docs/design/ADR_GATE_HOST_CONTRACT.md:302-303` | The citation of `citations.py:49` / `:74` as owners of the repo-relative test now names `acf.engine.looks_absolute` and `resolve_under_root`. |
| `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md` | `:104`: the call-site vocabulary and the Tier-1 sets. `:161`: the PostToolUse row runs rows declaring `hook`/`posttooluse`, host guards on every edited path. `:111`: drift covers registered built-in ids and resolvable host references. `:184`: *"Unknown built-in detector id, unresolvable host reference, or no Tier-1 call site on an active (enforced or partial) `ast` or `guard` row → registry validation fail."* |
| `pyproject.toml:3`, `plugins/arch-compliance/.claude-plugin/plugin.json:3` | `"0.2.2"` → `"0.2.3"`. |

---

## 5. Relationships and shape fit

### 5.1 Documents

| Document | Relationship | Disposition |
|---|---|---|
| `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md` | `ADJACENT` | Parent architecture; `:102`, `:123`, `:125` call for this extension point; `:104`, `:111` and `:184` are updated (§4.7). |
| `docs/design/ADR_GATE_HOST_CONTRACT.md` | `ADJACENT` | Owns `acf.adr`; `acf/adr/citations.py` changes only to consume the shared engine helpers (§4.1). Its `:302-303` names the citations helpers as owners of the repo-relative test and is updated to the engine helpers (§4.7). |
| `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` | `ADJACENT` | `tests/test_self_host.py:23` passes `repo_root` (§4.6). |
| `docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md` | `DISJOINT` | Tier-2 judge; `cli_check_llm.py` is unchanged. |
| `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md` | `DISJOINT` | Housekeeping skill. |

### 5.2 Elements

| New / changed element | Existing site | Relationship and resolution |
|---|---|---|
| `looks_absolute`, `resolve_under_root` | `plugins/arch-compliance/python/acf/adr/citations.py:49-51`, `:74-76` | `SUBSUMED`: citations' private copies are deleted and its two call sites use the engine helpers. `load_host_detector`, `load_mandates` and `make_line_lookup` use `resolve_under_root` too. |
| `validate_posix_rel_path` | `PosixStr` (`plugins/arch-compliance/python/acf/adr/contract.py:129`) | `ADJACENT`: `PosixStr` refuses backslashes in persisted ADR text fields; `validate_posix_rel_path` refuses any non-relative path, using `contains_backslash` and `looks_absolute`. `PosixStr` is unchanged. |
| `Mandate.runs_at`, `MandateRegistry.active` | `cli_check_diff.py:94-99`; `posttooluse_gate.py:229-236`, `:284-286`; `enforcement.py:47` | `SUBSUMED`: each of these sites calls the new definition. |
| Host-reference validation in `load_mandates` | `plugins/arch-compliance/python/acf/registry.py:56-63` | `SUBSUMED`: extended in place. |
| `HostHit` → `Finding` construction | `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:75-95` | `ADJACENT`: the bridge decodes JSON from a plugin-owned Node subprocess; the host runner receives typed `HostHit` objects that Pydantic has already validated. They share no input format. |
| `HostHit` → `Finding` construction | `_to_finding` (`plugins/arch-compliance/python/acf/judge.py:236-253`) | `ADJACENT`: the judge demotes severity by confidence and admits `path="<diff>"` and `line=0`; host findings take severity straight from the row and require a relative path and `line >= 1`. Different invariants, so no shared constructor. |
| Hook's in-repo test for host dispatch | `abs_path.relative_to(repo)` (`plugins/arch-compliance/hooks/posttooluse_gate.py:242-245`) | `ADJACENT`: the hook already computes each edited file's repo-relative path; host dispatch reuses that result (the `ValueError` branch marks out-of-repo files) rather than testing again. `_WIN_DRIVE_RE` (`plugins/arch-compliance/python/acf/adr/contract.py:95`) finds backslash drive paths inside persisted ADR text and is unchanged. |
| `make_line_lookup` | `cli_check_diff.py:76-80`, `posttooluse_gate.py:119-123` | `IDENTICAL`: both closures are deleted. |
| `load_host_detector` `sys.path` insertion | `posttooluse_gate.py:22-26` | `ADJACENT`: the hook puts the plugin's own `python/` on the path at start-up; the loader puts the host root on the path at dispatch. |

---

## 6. Doctrine compliance

| Anchor (`config/architecture/ARCHITECTURE.md`) | Mandate id | How the design complies |
|---|---|---|
| `## Fail loud` (`:24-41`) | `fail-loud.bare-except` | §6.1 lists each invalid state and the error that refuses it. The two `except Exception` handlers (§4.3 items 3 and 5) re-raise as typed errors and carry the `fail-loud.bare-except-ok` token with a reason, which `:29-30` requires. |
| `## No shims` (`:43-53`) | `no-shims.hasattr` | Callable lookup is `getattr(mod, attr, None)` followed by `callable(...)` and a raise; no `hasattr`. |
| `## POSIX paths` (`:55-64`) | `posix-paths.str-serialization` | `HostHit.path` is validated by `validate_posix_rel_path`; error messages use `.as_posix()`. |
| `## One base exception` (`:99-103`) | `plugin.one-base-exception` | No new exception class; uses `AcfInputError`, `UnknownDetectorError`, `DetectorPackError` (`plugins/arch-compliance/python/acf/exceptions.py:5`, `:13`, `:29`). |
| `## One owner for host paths` (`:105-116`) | `plugin.one-owner-host-paths` | `plugins/arch-compliance/python/acf/engine.py`, `plugins/arch-compliance/python/acf/registry.py` and `plugins/arch-compliance/python/acf/detectors/host.py` spell no `config/architecture` path; the skill snippet takes `MANDATES_REL` and `resolve_repo` from `acf.repo`. |
| `## Declared, never defaulted` (`:118-133`) | `plugin.declared-never-defaulted` | `repo_root` is required for an active host row (`AcfInputError` otherwise), and `apply_registry`'s `call_sites` has no default. |
| `## Prose names no host` (`:135-143`) | `plugin.adr-code-names-no-host`, `plugin.gate-prose-names-no-host` | The runtime messages in §4.2–§4.3 and the prose in §4.7 name no origin host. |
| `## Live consumers` (`:153-157`) | — | §6.2 lists each new export and its runtime caller. |
| `## No completeness claims` (`:159-169`) | — | Every population claim in this spec carries its recipe (§1, §3, Appendix) or is a per-item table. |
| `## Declared text decoding` (`:171-182`) | — | New `read_text` calls (`cli_check_diff.py` TypeScript branch, `make_line_lookup`) declare `encoding="utf-8"`. No subprocess is added. |
| `## Release discipline` (`:184-194`) | — | Skill prose changes, so the version is bumped in both files `:186-187` names. |
| `## Single point of definition` (`:196-209`) | — | Path shape: `acf.engine`. Row activity: `Mandate.runs_at`. Host loading and running: `acf.detectors.host`. Line lookup: `make_line_lookup` (§5.2). |
| `## Scoped refactor` (`:211-215`) | — | Consolidations touch only the code paths this design changes; the shared dispatcher is a non-goal (§3). |
| `## Frozen ledger format` (`:145-151`) | `plugin.frozen-ledger-format` | No ledger model changes. |

### 6.1 Invalid states and their refusal

| Invalid state | Refused by | Error |
|---|---|---|
| Malformed host reference (any status, any caller) | `parse_host_detector_ref` in `load_mandates` | `AcfInputError` |
| Active `ast`/`guard` row with no Tier-1 call site | `load_mandates` (with `known_detectors`) | `AcfInputError` |
| Active built-in row naming an unknown id | `load_mandates` (with `known_detectors`) | `UnknownDetectorError` |
| Active host row, no `repo_root` given | `load_mandates` | `AcfInputError` |
| Active host `ast` row with `languages: none` | `load_mandates` | `AcfInputError` |
| Active host row whose file is missing or outside the root | `load_mandates`; `load_host_detector` | `UnknownDetectorError` |
| Host module fails to import, or has no such callable | `load_host_detector` at dispatch | `UnknownDetectorError` |
| Host callable raises (any exception) | `scan_host_ast_file`, `scan_host_guards` | `DetectorPackError` |
| Host returns a non-iterable, a `str`, a non-`HostHit` item, or an `ast` hit on another file | `_to_findings` | `DetectorPackError` |
| `HostHit` with a non-relative or backslash path, `line < 1`, or empty message | `HostHit` validation (raised inside the callable, wrapped) | `DetectorPackError` |

### 6.2 New exports and their callers

| Export | Runtime caller |
|---|---|
| `acf.engine.looks_absolute` | `validate_posix_rel_path`; `acf/adr/citations.py` |
| `acf.engine.resolve_under_root` | `load_mandates`; `load_host_detector`; `make_line_lookup`; `acf/adr/citations.py` |
| `acf.engine.validate_posix_rel_path` | `parse_host_detector_ref`; `HostHit` |
| `DIFF_CALL_SITES` / `HOOK_CALL_SITES` | `cli_check_diff.py` / `posttooluse_gate.py` |
| `TIER1_CALL_SITES` | `load_mandates` |
| `Mandate.is_active` | `Mandate.runs_at`; `load_mandates` |
| `Mandate.runs_at` | `MandateRegistry.active`; `apply_registry` |
| `MandateRegistry.active` | both gates; both host runners |
| `is_host_detector_ref`, `parse_host_detector_ref` | `load_mandates`; host runners; `load_host_detector` |
| `HostHit` | host callables (imported by host code); `_to_findings` |
| `load_host_detector`, `scan_host_ast_file`, `scan_host_guards` | both gates |
| `make_line_lookup` | both gates |

---

## 7. Verification and definition of done

1. The §4.6 tests exist and pass.
2. `PYTHONUTF8=1 python -m pytest -q`, `PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main` and `npm test --prefix plugins/arch-compliance/detectors/typescript` pass.
3. `pyproject.toml:3` and `plugins/arch-compliance/.claude-plugin/plugin.json:3` read `"0.2.3"`.
4. This spec clears `/adversarial-design-review`, with its run detail and ledger row committed on the branch.

---

## Appendix — Receipts at `a338cad`

| Premise | Recipe | Observed |
|---|---|---|
| `load_mandates` callers | `git grep -n "load_mandates(" -- plugins tests ':!plugins/arch-compliance/python/acf/registry.py'` | `plugins/arch-compliance/hooks/inject_constraints.py:104`, `plugins/arch-compliance/hooks/posttooluse_gate.py:107`, `plugins/arch-compliance/python/acf/cli_check_diff.py:70`, `plugins/arch-compliance/python/acf/cli_check_llm.py:54`, `plugins/arch-compliance/skills/acf-mandate/SKILL.md:95` (plus a prose mention at `:141`), `plugins/arch-compliance/skills/architecture-review/SKILL.md:62`, `plugins/arch-compliance/tests/test_profile_drift.py:24`, `plugins/arch-compliance/tests/test_registry.py:10,17,30,47,57`, `tests/test_self_host.py:23`. Only `cli_check_diff.py:70`, `SKILL.md:95`, `test_profile_drift.py:24`, `test_registry.py:30` and `test_self_host.py:23` pass `known_detectors`. The others reach only the syntax check, which raises `AcfInputError`. |
| `apply_registry` callers | `git grep -n "apply_registry(" -- '*.py'` | `plugins/arch-compliance/hooks/posttooluse_gate.py:125`, `plugins/arch-compliance/python/acf/cli_check_diff.py:82`, and `plugins/arch-compliance/tests/test_enforcement.py` at `:54,60,66,72,84,94,104,110,125,130`. |
| Active-row filters | `git grep -n "_active_mandates\|status != \"unenforced\"\|status == \"unenforced\"" -- '*.py' ':!*/tests/*'` | `plugins/arch-compliance/hooks/posttooluse_gate.py:231,235,285`; `plugins/arch-compliance/python/acf/cli_check_diff.py:94,98,112,113,158,168`; `plugins/arch-compliance/python/acf/enforcement.py:47`. A wider recipe, `git grep -n "\.status\b" -- plugins/arch-compliance/python plugins/arch-compliance/hooks ':!*/adr/*'`, adds `registry.py:58` (replaced by §4.2), `judge.py:218` (Tier-2, unchanged) and a display-only read at `inject_constraints.py:158`. |
| `call_sites` of active `ast`/`guard` rows | `python -c "import yaml,glob; [print(f, m['id'], m['call_sites']) for f in ['config/architecture/mandates.yml', *glob.glob('plugins/arch-compliance/profiles/*/mandates.yml'), 'plugins/arch-compliance/tests/fixtures/mandates_valid.yml'] for m in yaml.safe_load(open(f, encoding='utf-8')) if m['detection'] in ('ast','guard') and m['status'] != 'unenforced']"` | Each row printed includes `ci`. `no-shims.hasattr` is `[ci]` in `config/architecture/mandates.yml`, in the `python-service` profile and in `mandates_valid.yml`; the other rows are `[ci, hook]`. |
| `KNOWN_DETECTORS` size | `python -c "from acf.cli_check_diff import KNOWN_DETECTORS as K; print(len(K))"` | `13` |
| No `partial` `ast`/`guard` row exists to be newly rejected | the `call_sites` recipe above with `m['status'] == 'partial'` | No row printed. |
