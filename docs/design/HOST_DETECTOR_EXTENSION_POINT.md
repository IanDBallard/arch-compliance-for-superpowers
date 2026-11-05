# Host Detector Extension Point (`ast` and `guard` Callables)

**Status:** Draft (v3)
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

1. **A row can be declared, load cleanly, and never run.**
   - `load_mandates` (`plugins/arch-compliance/python/acf/registry.py:48-64`) skips every row whose status is not `enforced` (`:58`) and raises `UnknownDetectorError` (`:60-63`) only for an `enforced` `ast`/`guard` row whose detector is not in `known_detectors`.
   - `KNOWN_DETECTORS` (`plugins/arch-compliance/python/acf/cli_check_diff.py:25`) is the closed union `ALL_PYTHON_DETECTOR_IDS | TS_DETECTOR_IDS | LLM_PROMPT_IDS`; nothing extends it (recipe: `git grep -n "KNOWN_DETECTORS" -- plugins tests`). Because it includes the LLM prompt ids, an `ast` row naming an LLM prompt id passes the check although no Tier-1 scanner dispatches on that id.
   - A `status: partial` row is live in both gates (`plugins/arch-compliance/python/acf/enforcement.py:47` drops only `unenforced`), yet `load_mandates` never checks it. So a host can name a detector of its own in a `partial` `ast`/`guard` row today, load cleanly with `known_detectors=KNOWN_DETECTORS`, and have nothing ever execute it.
   - Every built-in scanner stamps one fixed `mandate_id` on its findings (recipe: `git grep -n 'mandate_id="' -- plugins/arch-compliance/python/acf/detectors`; TypeScript: `plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23`, `plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15`), and `apply_registry` matches findings to rows by that id (`enforcement.py:46`). A row whose `id` differs from the id its detector stamps loads and never receives a finding. And `fail_loud_ratchet` runs only in `acf-check-diff` (`cli_check_diff.py:168-182`; `_scan_paths` at `plugins/arch-compliance/hooks/posttooluse_gate.py:213-295` has no ratchet call).
   - Neither gate can execute a non-built-in detector: `_scan_changed` (`cli_check_diff.py:102-184`) and `_scan_paths` call only built-in scanners, selected by exact built-in id (`cli_check_diff.py:94-99`, `posttooluse_gate.py:229-236`, `:284-286`). No dynamic loader exists to reuse: `git grep -n "importlib\|import_module\|spec_from_file_location\|exec_module" -- plugins/arch-compliance/python plugins/arch-compliance/hooks` prints nothing.
2. **The PostToolUse hook skips detector validation.** `plugins/arch-compliance/hooks/posttooluse_gate.py:107` calls `load_mandates(mandates_path)` without `known_detectors`, and `:108` catches only `AcfInputError`. `UnknownDetectorError` subclasses `AcfError`, not `AcfInputError` (`plugins/arch-compliance/python/acf/exceptions.py:5`, `:13`). An active row naming an unknown detector produces zero findings at edit time instead of failing loud.
3. **`call_sites` is declared but read by no gate.** `Mandate.call_sites` is `list[str]` (`plugins/arch-compliance/python/acf/registry.py:21`). The gates select rows on detector id and status only (`cli_check_diff.py:94-99`; `posttooluse_gate.py:229-236`, `:284-286`), and `apply_registry` on status only (`enforcement.py:47`); `git grep -n "call_sites" -- plugins/arch-compliance/python plugins/arch-compliance/hooks` prints only the field declaration at `registry.py:21` and two unrelated `surface_call_sites` lines in `plugins/arch-compliance/python/acf/adr/ledger.py`. This repository's `no-shims.hasattr` row declares `call_sites: [ci]` (`config/architecture/mandates.yml:70`), yet the hook reports it at edit time, and `plugins/arch-compliance/tests/test_hooks.py:199-218` pins that behaviour with the fixture's identical row. Routing host detectors by `call_sites` without changing this would give one field two meanings.
4. **Exemptions are honoured only on files the gate pre-read.** The `_line_lookup` closures (`cli_check_diff.py:76-80`, `posttooluse_gate.py:119-123`) are token-identical and consult only `file_lines`, which holds changed `.py`/`.ts`/`.tsx` files (`cli_check_diff.py:126`, `:152`; `posttooluse_gate.py:248-252`). A finding on any other file gets `""`, so `apply_registry` (`enforcement.py:49-50`) cannot see an inline exemption token on it.
5. **The repo-relative path checks live in the ADR gate's package.** `_looks_absolute` (`plugins/arch-compliance/python/acf/adr/citations.py:49-51`) and `_escapes_repo` (`:74-76`) are private to `acf.adr`, the ADR gate's package (`docs/design/ADR_GATE_HOST_CONTRACT.md`). The hooks must not reach `acf.adr`: `plugins/arch-compliance/tests/test_adr_import_graph.py:70-76` states the intent (*"acf.adr pulls in pydantic, so it must never enter that graph"*) and pins only the literal text `acf.adr` in the two hook files. `acf.registry` and `acf.enforcement` are imported by the hook, so a generic check they import from `acf.adr` would put `acf.adr` in the hook's graph without tripping that test. `acf.adr` already imports `acf.engine` (`plugins/arch-compliance/python/acf/adr/contract.py:20`), so moving the checks there keeps the dependency pointing the way it already points.

---

## 2. Decisions this design records

1. **Host detector reference syntax `<posix_rel_path.py>:<callable_name>`.** For `detection in {"ast", "guard"}`, a `detector` containing `":"` is a host reference; otherwise it is a built-in id. The path part is a relative POSIX path accepted by `validate_posix_rel_path` (§4.1) and ending in `.py`; the callable part satisfies `str.isidentifier()`.
2. **One definition of "this row runs at this Tier-1 gate", for built-in and host rows alike.**
   - `acf.registry` gains `DIFF_CALL_SITES = frozenset({"ci", "precommit"})`, `HOOK_CALL_SITES = frozenset({"hook", "posttooluse"})`, `TIER1_CALL_SITES = DIFF_CALL_SITES | HOOK_CALL_SITES`, the property `Mandate.is_active` (`status != "unenforced"`), the method `Mandate.runs_at(call_sites) -> bool` (`is_active` and `call_sites` intersects the row's `call_sites`), and `MandateRegistry.active(call_sites, *, detector=None, detection=None) -> list[Mandate]`.
   - `apply_registry` gains a required keyword `call_sites` and drops findings whose row does not `runs_at` it. This filter is needed at that one sink because the built-in scanners emit findings without consulting the registry (`plugins/arch-compliance/python/acf/detectors/python_pack.py:27-52`). `acf-check-diff` passes `DIFF_CALL_SITES`; the hook passes `HOOK_CALL_SITES`.
   - `cli_check_diff._active_mandates` and the hook's three inline filters are replaced by `registry.active(...)`.
   - Scope: the two Tier-1 gates only. The Tier-2 judge reviews every `llm` row it is given, unenforced included, and reads `status == "enforced"` only to decide whether a provider is required (`plugins/arch-compliance/python/acf/judge.py:213-218`, `:230`); it keeps that separate definition and is unchanged.
   - Consequence, accepted: a row declaring only `[ci]` (this repository's `no-shims.hasattr`) is no longer reported by the PostToolUse hook. `plugins/arch-compliance/tests/test_hooks.py:199-218` is rewritten (§4.6).
3. **Every built-in detector declares where it runs and which row it reports to.** `acf.registry.BuiltinDetector` is a frozen dataclass `(mandate_id: str, call_sites: frozenset[str])`. `acf.detectors.KNOWN_DETECTORS` maps each built-in `ast`/`guard` id to one, built from mandate-id constants that each scanner module also uses at its `Finding` construction (§4.3). LLM prompt ids are not in it. With `known_detectors` given, `load_mandates` refuses an active built-in `ast`/`guard` row whose detector is not in the map (`UnknownDetectorError`), whose `id` is not the detector's `mandate_id`, or which declares a Tier-1 call site at which no gate runs its detector (`AcfInputError`). So each of the cases in §1 item 1 is refused at load. Consequence, accepted: with unique row ids (`registry.py:33-41`), a host has at most one active row per built-in detector. Today a second `forbid_facade_sink` or `fsm_transition_guard` row runs the scanner with its own `params`, but its findings carry the fixed id and land on the other row (`cli_check_diff.py:128-150`); no shipped registry has such a pair (Appendix).
4. **Row-shape rules live on `Mandate`; rules that need outside data live in `load_mandates`.** A `Mandate` `model_validator` refuses (`AcfInputError`), for every caller that builds a row: a malformed host reference on an `ast`/`guard` row (any status); an active `ast`/`guard` row with no Tier-1 call site; an active host `ast` row whose `languages` is not in `{"python", "typescript", "both"}`. `load_mandates` with `known_detectors` adds the built-in contract (Decision 3) and, for host rows, requires an explicit `repo_root` (`AcfInputError`) and an existing file under it (`UnknownDetectorError`). Import and callable lookup happen only at dispatch (§4.4), so `load_mandates` runs no host code for any caller.
5. **Host callables return `HostHit`, never `Finding`.** `acf.detectors.host.HostHit` is a frozen Pydantic model with exactly `path` (validated by `validate_posix_rel_path`), `line` (`>= 1`) and `message` (non-empty). The runner builds each `Finding` from the hit and the mandate row, so a host cannot attach a finding to the wrong row and no field is overwritten. The runner materialises the callable's result inside the region that wraps failures, so a generator's errors are wrapped too.
6. **One host root per process, refused rather than repaired.** `load_host_detector` records the first root it serves and raises `AcfInputError` for any other root in the same process. Production callers resolve one repository per process (`plugins/arch-compliance/python/acf/cli_check_diff.py:63`; `plugins/arch-compliance/hooks/posttooluse_gate.py:65`, a fresh process per edit). In-process tests over several roots reset the loader through a test fixture (§4.6).
7. **Trust boundary.**
   - Automatic hooks: the PostToolUse hook exits `0` before importing anything beyond `acf.repo` when `.acf/enabled` is absent (`plugins/arch-compliance/hooks/posttooluse_gate.py:72-81`). That marker is the opt-in for running host code on edit.
   - Explicit invocation: `acf-check-diff` runs only when the host's own pre-commit or CI configuration invokes it (this repository: `.github/workflows/ci.yml:40`). That invocation is the opt-in. `.acf/` is gitignored here (`.gitignore:8`), so a CI checkout never carries the marker, and requiring it there would disable CI. A person running `acf-check-diff` by hand in a checkout they do not trust is the residual case, accepted.
   - The SubagentStart hook (`plugins/arch-compliance/hooks/inject_constraints.py:104`) and `acf-check-llm` (`plugins/arch-compliance/python/acf/cli_check_llm.py:54`) call `load_mandates`, which never imports host code (Decision 4), so neither runs host code.

---

## 3. Scope and Non-Goals

### In scope

| File | Change |
|---|---|
| `plugins/arch-compliance/python/acf/engine.py` | Add `looks_absolute`, `resolve_under_root`, `validate_posix_rel_path` (§4.1). |
| `plugins/arch-compliance/python/acf/adr/citations.py` | `_looks_absolute` and `_escapes_repo` are deleted; their two call sites (`:161`, `:163`) call `acf.engine.looks_absolute` and `acf.engine.resolve_under_root` (§4.1). |
| `plugins/arch-compliance/python/acf/registry.py` | Call-site constants, `BuiltinDetector`, `Mandate.is_active`/`runs_at`/row-shape validator, `MandateRegistry.active`, `is_host_detector_ref`, `parse_host_detector_ref`, extended `load_mandates` (§4.2). |
| `plugins/arch-compliance/python/acf/detectors/__init__.py` and the five scanner modules | Mandate-id constants and `KNOWN_DETECTORS` (§4.3). |
| `plugins/arch-compliance/python/acf/detectors/host.py` (new) | `HostHit`, `load_host_detector`, `scan_host_ast_file`, `scan_host_guards` (§4.4). |
| `plugins/arch-compliance/python/acf/enforcement.py` | `apply_registry(..., *, call_sites)`; `make_line_lookup` (§4.5). |
| `plugins/arch-compliance/python/acf/cli_check_diff.py` | Wiring (§4.6). |
| `plugins/arch-compliance/hooks/posttooluse_gate.py` | Wiring (§4.6). |
| `plugins/arch-compliance/hooks/inject_constraints.py` | None: every new load-time refusal without `known_detectors` is `AcfInputError`, which `:105` already catches. |
| `plugins/arch-compliance/python/acf/cli_check_llm.py` | None: a malformed registry already surfaces at `:54` as an uncaught `AcfInputError` and non-zero exit; the new refusals reach it the same way. |
| Tests, prose, version | §4.7 and §4.8. |

### Non-goals

- **No architecture-review runtime package and no architecture-review host configuration file.** Both belong to Spec 2b (architecture-review portability), not yet written. The recipe `git ls-files plugins/arch-compliance/python/acf | grep -i review` prints nothing at `a338cad`.
- **No `PosixRelPath` Pydantic alias in `acf.engine`.** `acf.engine` stays stdlib-only; `HostHit` applies `validate_posix_rel_path` through its own `AfterValidator`.
- **No change to `HistoricMansions` in this slice.** Its rows would still need rewriting at cutover: they carry no `languages` or `arch_anchor` field, both required by `Mandate` (`plugins/arch-compliance/python/acf/registry.py:20`, `:24`). Two behaviours of its driver are not reproduced by this contract and are left to the cutover spec: it reports an unparseable changed file as a `WARN` (or raises in range mode) with `exc.lineno or 0` as the line (`hm:scripts/ci/arch_compliance/driver.py:150-163`), while `scan_host_ast_file` skips unparseable files like the built-in scanners do and `HostHit.line` must be `>= 1`; and its guards read the staged or range blob, so they depend on diff mode, which `scan_guard` does not receive (it reads the worktree).
- **No shared Tier-1 dispatcher.** `_scan_changed` and `_scan_paths` differ in diff scope (added lines vs whole file), path collection and file filter. This design adds the same three host calls to each; extracting a common dispatcher is a separate refactor (`## Scoped refactor`, `config/architecture/ARCHITECTURE.md:211-215`).
- **No shared parse-or-skip helper.** `python_pack`, `facade_sinks`, `fsm_guard` and `fail_loud_ratchet` each parse and skip on `SyntaxError`; `scan_host_ast_file` adds one more parse. Consolidating them touches four scanners this design does not otherwise change (`## Scoped refactor`).

---

## 4. Design

### 4.1 Path helpers (`plugins/arch-compliance/python/acf/engine.py`)

`acf.engine` stays stdlib-only (`import re`, `from pathlib import Path`) and owns two string-to-path tests: whether a path string is absolute, and whether a relative string resolves inside a root. Converting an already-resolved absolute `Path` to its relative string (`abs_path.relative_to(repo)` at `plugins/arch-compliance/hooks/posttooluse_gate.py:242-245`, the ratchet's walk filter at `plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:59-62`) is the opposite direction and stays where it is; so does `Path.is_absolute()` on paths resolved for I/O (`posttooluse_gate.py:204`, `fail_loud_ratchet.py:123`).

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


@dataclass(frozen=True)
class BuiltinDetector:
    mandate_id: str
    call_sites: frozenset[str]


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


class Mandate(BaseModel):
    ...  # fields unchanged

    @property
    def is_active(self) -> bool:
        return self.status != "unenforced"

    def runs_at(self, call_sites: frozenset[str]) -> bool:
        return self.is_active and bool(call_sites.intersection(self.call_sites))

    @model_validator(mode="after")
    def _row_shape(self) -> Mandate:
        if self.detection not in {"ast", "guard"}:
            return self
        host = is_host_detector_ref(self.detector)
        if host:
            parse_host_detector_ref(self.detector)
        if not self.is_active:
            return self
        if not TIER1_CALL_SITES.intersection(self.call_sites):
            raise AcfInputError(
                f"active mandate {self.id!r} declares no Tier-1 call site "
                f"{sorted(TIER1_CALL_SITES)}; got {self.call_sites!r}"
            )
        if host and self.detection == "ast" and self.languages not in _ACTIVE_HOST_AST_LANGUAGES:
            raise AcfInputError(
                f"active host ast mandate {self.id!r} must declare languages in "
                f"{sorted(_ACTIVE_HOST_AST_LANGUAGES)}; got {self.languages!r}"
            )
        return self


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


def load_mandates(
    path: Path,
    *,
    known_detectors: Mapping[str, BuiltinDetector] | None = None,
    repo_root: Path | None = None,
) -> MandateRegistry:
    mandates = load_model_file(path, Mandate, subject="mandates file", fmt="yaml", many=True)
    if known_detectors is not None:
        for m in mandates:
            if not m.is_active or m.detection not in {"ast", "guard"}:
                continue
            if not is_host_detector_ref(m.detector):
                _check_builtin(m, known_detectors)
                continue
            if repo_root is None:
                raise AcfInputError(
                    f"active mandate {m.id!r} uses host detector {m.detector!r}; "
                    "pass repo_root to load_mandates"
                )
            rel_path, _ = parse_host_detector_ref(m.detector)
            module_path = resolve_under_root(repo_root, rel_path)
            if module_path is None or not module_path.is_file():
                raise UnknownDetectorError(
                    f"active mandate {m.id!r}: host detector file not found: "
                    f"{(repo_root / rel_path).as_posix()}"
                )
    return MandateRegistry(mandates=mandates, source_path=path.as_posix())


def _check_builtin(m: Mandate, known: Mapping[str, BuiltinDetector]) -> None:
    contract = known.get(m.detector)
    if contract is None:
        raise UnknownDetectorError(
            f"active mandate {m.id!r} references unknown detector {m.detector!r}"
        )
    if m.id != contract.mandate_id:
        raise AcfInputError(
            f"active mandate {m.id!r}: detector {m.detector!r} reports only to mandate "
            f"{contract.mandate_id!r}, so this row would never receive a finding"
        )
    unserved = TIER1_CALL_SITES.intersection(m.call_sites) - contract.call_sites
    if unserved:
        raise AcfInputError(
            f"active mandate {m.id!r}: detector {m.detector!r} runs only at "
            f"{sorted(contract.call_sites)}, not at {sorted(unserved)}"
        )
```

`registry.py` imports `resolve_under_root` and `validate_posix_rel_path` from `acf.engine`, `dataclass` and `Mapping` from the standard library, and nothing from `acf.detectors`. A `model_validator` that raises `AcfInputError` propagates that error with its own type through `load_model_file`, which converts only `ValidationError` (`plugins/arch-compliance/python/acf/loader.py:54-56`, `:70-73`); `MandateRegistry._unique_ids` (`registry.py:33-41`) already raises `AcfInputError` this way.

### 4.3 Built-in detector contracts (`plugins/arch-compliance/python/acf/detectors/`)

- Each scanner module gains a mandate-id constant and uses it at its `Finding` construction in place of the literal: `python_pack.py` (`FAIL_LOUD_BARE_EXCEPT_MANDATE_ID` at `:67`, `NO_SHIMS_HASATTR_MANDATE_ID` at `:97`, `POSIX_PATHS_STR_MANDATE_ID` at `:144` and `:172`), `build_artifacts.py:31`, `facade_sinks.py:69`, `fail_loud_ratchet.py:132`, `fsm_guard.py:59`. `typescript_bridge.py` gains `TS_MANDATE_IDS = {"empty_catch": "fail-loud.empty-catch", "explicit_any": "no-shims.explicit-any"}`, the values the Node rules stamp (`emptyCatch.ts:23`, `explicitAny.ts:15`); a test pins that agreement (§4.7).
- `acf/detectors/__init__.py` defines `KNOWN_DETECTORS: Mapping[str, BuiltinDetector]` (a `MappingProxyType`):

| Detector id | `mandate_id` constant | `call_sites` | Where it runs |
|---|---|---|---|
| `fail_loud_bare_except`, `no_shims_hasattr`, `posix_paths_str_serialization` | the three `python_pack` constants | `TIER1_CALL_SITES` | `scan_python_file` in both gates (`cli_check_diff.py:127`, `posttooluse_gate.py:254`) |
| `empty_catch`, `explicit_any` | `TS_MANDATE_IDS` | `TIER1_CALL_SITES` | `scan_typescript_file` in both gates (`cli_check_diff.py:153-156`, `posttooluse_gate.py:278-282`) |
| `forbid_facade_sink`, `fsm_transition_guard` | `facade_sinks` / `fsm_guard` constants | `TIER1_CALL_SITES` | both gates' `.py` branch (`cli_check_diff.py:128-150`, `posttooluse_gate.py:255-277`) |
| `no_build_artifacts` | `build_artifacts` constant | `TIER1_CALL_SITES` | both gates (`cli_check_diff.py:158-166`, `posttooluse_gate.py:284-294`) |
| `fail_loud_ratchet` | `fail_loud_ratchet` constant | `DIFF_CALL_SITES` | `acf-check-diff` only (`cli_check_diff.py:168-182`) |

- `cli_check_diff.py:25` becomes `from acf.detectors import KNOWN_DETECTORS`, so existing importers of `acf.cli_check_diff.KNOWN_DETECTORS` keep working, and its import of `LLM_PROMPT_IDS` (`:21`) is removed. The hook imports `KNOWN_DETECTORS` from `acf.detectors`, not from `acf.cli_check_diff`, so it does not pull in `acf.judge`.

### 4.4 Host loader and runners (`plugins/arch-compliance/python/acf/detectors/host.py`)

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
   `added_lines` follows the built-in convention of `acf.engine.is_in_scope` (`plugins/arch-compliance/python/acf/engine.py:27-31`): `None` or empty means the whole file, otherwise only the listed lines. A host detector calls `is_in_scope` rather than restating the rule. The diff gate passes an empty set for a file whose change only deletes lines (`cli_check_diff.py:121`).
3. **`load_host_detector(repo_root: Path, detector: str) -> Callable[..., Iterable[HostHit]]`:**
   - `rel_path, attr = parse_host_detector_ref(detector)`; `root = repo_root.resolve()`.
   - **Root.** Module-level `_ACTIVE_ROOT: Path | None = None` and `_MODULE_CACHE: dict[str, ModuleType] = {}`. On the first call, if `root / "acf"` or `root / "acf.py"` exists the loader raises `AcfInputError` (a host package named `acf` would shadow the plugin's own lazy `acf.*` imports); otherwise it inserts `str(root)` at `sys.path[0]` and sets `_ACTIVE_ROOT = root`. A later call with `root != _ACTIVE_ROOT` raises `AcfInputError(f"host detectors already loaded from {_ACTIVE_ROOT.as_posix()}; one host root per process")`. Host modules' intra-repo imports (such as `hm:scripts/ci/metadata_facade_guard.py:66`, `from scripts.ci.arch_compliance.facade_sinks import ...`) resolve against that root.
   - `module_path = resolve_under_root(root, rel_path)`, and `UnknownDetectorError` if it is `None` or not a file.
   - **Module.** Cached in `_MODULE_CACHE` by `rel_path`. The name is `"_acf_host_" + hashlib.sha256(rel_path.encode()).hexdigest()[:16]`. The module is registered in `sys.modules` before `spec.loader.exec_module(mod)`, which `dataclasses` needs to resolve string annotations, and removed if `exec_module` raises. The handler is `except (Exception, SystemExit) as exc:  # fail-loud.bare-except-ok: <reason>` and re-raises `UnknownDetectorError(f"failed to import host detector module {rel_path!r} for {detector!r}: {exc}")`.
   - `fn = getattr(mod, attr, None)`; `UnknownDetectorError` if `not callable(fn)`.
4. **`_call_host(fn, mandate, where, *args, **kwargs) -> list[HostHit]`:** the one wrapped region.
   ```python
   try:
       raw = fn(*args, **kwargs)
       if raw is None or isinstance(raw, (str, bytes)):
           raise TypeError(f"returned {type(raw).__name__}, not an iterable of HostHit")
       hits = list(raw)
   except (Exception, SystemExit) as exc:  # fail-loud.bare-except-ok: <reason>
       raise DetectorPackError(
           f"host detector {mandate.detector!r} for mandate {mandate.id!r} failed {where}: {exc}"
       ) from exc
   ```
   Materialising with `list(raw)` inside the `try` means an exception raised while a generator runs, including a `HostHit` `ValidationError`, becomes `DetectorPackError`. `KeyboardInterrupt` is not caught.
5. **`_to_findings(hits: list[HostHit], mandate: Mandate, *, expected_path: str | None) -> list[Finding]`:** refuses (`DetectorPackError`) any item that is not a `HostHit` and, for `ast` rows, any hit whose `path != expected_path`. Each hit becomes `Finding(mandate_id=mandate.id, severity=Severity(mandate.severity), path=hit.path, line=hit.line, message=hit.message, detector=mandate.detector, detection=mandate.detection)`.
6. **`scan_host_ast_file(repo_root, text, path, added_lines, registry, *, language, call_sites) -> list[Finding]`:**
   - `mandates = [m for m in registry.active(call_sites, detection="ast") if is_host_detector_ref(m.detector) and m.languages in {language, "both"}]`; returns `[]` if none.
   - For `language == "python"`: `tree = ast.parse(text)` once, shared by every host `ast` detector on the file; on `SyntaxError` it returns `[]`, the convention of `scan_python_file` (`plugins/arch-compliance/python/acf/detectors/python_pack.py:34-37`). For TypeScript, `tree=None`.
   - Each callable runs through `_call_host(fn, mandate, f"on {path!r}", text, path, added_lines, tree=tree, params=mandate.params)`, then `_to_findings(..., expected_path=path)`.
7. **`scan_host_guards(repo_root, changed_files, registry, *, call_sites) -> list[Finding]`:** selects `[m for m in registry.active(call_sites, detection="guard") if is_host_detector_ref(m.detector)]` and runs each through `_call_host(fn, mandate, "as a guard", repo_root.resolve(), tuple(changed_files), params=mandate.params)`, then `_to_findings(..., expected_path=None)`.

A broken host `ast` module is reported when a file in its language changes, because import happens at dispatch; a missing module file is reported at every load.

### 4.5 Enforcement (`plugins/arch-compliance/python/acf/enforcement.py`)

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

`make_line_lookup` reads with `errors="replace"`: an exemption token is ASCII, so a stray undecodable byte elsewhere on the line must neither crash `apply_registry` nor hide the token. A missing or out-of-root file yields `""`, which leaves the finding in place. An `OSError` from `read_text` propagates.

### 4.6 Wiring

1. **`plugins/arch-compliance/python/acf/cli_check_diff.py`:**
   - `:70`: `load_mandates(mandates_path, known_detectors=KNOWN_DETECTORS, repo_root=repo)`.
   - `:76-82`: `findings = apply_registry(raw_findings, registry, make_line_lookup(repo, file_lines), call_sites=DIFF_CALL_SITES)`.
   - `_active_mandates` (`:94-99`) is deleted; its four call sites (`:112`, `:113`, `:158`, `:168`) become `registry.active(DIFF_CALL_SITES, detector=...)`.
   - `.py` branch, after `scan_fsm_writes` (`:140-150`): `findings.extend(scan_host_ast_file(repo, text, posix, lines, registry, language="python", call_sites=DIFF_CALL_SITES))`.
   - `.ts`/`.tsx` branch (`:151-156`): bind `text = abs_path.read_text(encoding="utf-8")` and use it for `file_lines[posix]`, then `findings.extend(scan_host_ast_file(..., language="typescript", call_sites=DIFF_CALL_SITES))`.
   - After the ratchet loop (`:168-182`): `findings.extend(scan_host_guards(repo, changed, registry, call_sites=DIFF_CALL_SITES))`.
   - The `except` tuple at `:72` already lists `AcfInputError`, `UnknownDetectorError` and `DetectorPackError` around both load and scan.
2. **`plugins/arch-compliance/hooks/posttooluse_gate.py`:**
   - Deferred imports (`:91-104`) add `KNOWN_DETECTORS` (from `acf.detectors`), `HOOK_CALL_SITES`, `make_line_lookup`, `UnknownDetectorError`, `scan_host_ast_file` and `scan_host_guards`.
   - `:106-110`: `load_mandates(mandates_path, known_detectors=KNOWN_DETECTORS, repo_root=repo)` inside `except (AcfInputError, UnknownDetectorError)`.
   - `:113-117`: the scan `except` becomes `(AcfInputError, DetectorPackError, UnknownDetectorError)`, matching `acf-check-diff`.
   - `:119-125`: `findings = apply_registry(raw_findings, registry, make_line_lookup(repo, file_lines), call_sites=HOOK_CALL_SITES)`.
   - `_scan_paths`: the three inline filters (`:229-236`, `:284-286`) become `registry.active(HOOK_CALL_SITES, detector=...)`. The `try`/`except ValueError` at `:242-245` also records which paths are in the repository, in a separate list `in_repo_rel_paths`; `rel_paths` keeps its current contents for the build-artifact guard. Only in-repo paths reach host dispatch: the `.py` and TypeScript branches call `scan_host_ast_file(repo, text, rel, None, registry, language=..., call_sites=HOOK_CALL_SITES)` for in-repo files, and after the build-artifact loop (`:284-294`) `scan_host_guards(repo, in_repo_rel_paths, registry, call_sites=HOOK_CALL_SITES)` runs.
   - Docstring `:12` is reworded to state that the hook runs active rows declaring `hook` or `posttooluse`, including host detectors, which receive every edited in-repo path. Line `:11` stays verbatim: `plugins/arch-compliance/tests/test_repo_paths.py:47-48` pins its text.

### 4.7 Tests

| File | Change |
|---|---|
| `plugins/arch-compliance/tests/test_engine_paths.py` (exists; extended) | Its current cases are kept. Added: `validate_posix_rel_path` accepts `"scripts/ci/guard.py"`, `"a/b/c.py"`, `"guard.py"`, and rejects `""`, `" a.py"`, a backslash path, `"/a.py"`, `"a/"`, `"C:/a.py"`, `"C:a.py"`, `"a//b.py"`, `"./a.py"`, `"a/./b.py"`, `"../a.py"` and `"a/../b.py"`; `looks_absolute` and `resolve_under_root` get one positive and one negative case each. |
| `plugins/arch-compliance/tests/conftest.py` (new) | Fixture `fresh_host_loader`: monkeypatches `acf.detectors.host._ACTIVE_ROOT` to `None` and `_MODULE_CACHE` to `{}`, snapshots `sys.path` and the keys of `sys.modules`, and afterwards restores `sys.path` and deletes every `sys.modules` key added during the test. |
| `plugins/arch-compliance/tests/test_host_detectors.py` (new) | All cases use `fresh_host_loader`. Loader: imports a module that imports a sibling package from the root and defines a `@dataclass(frozen=True)` class under `from __future__ import annotations`; caches across two callables in one file; raises `UnknownDetectorError` on a missing file, an import failure, a module that calls `sys.exit(0)` and a missing callable; raises `AcfInputError` for a second root and for a root containing `acf/`. Runners: one `ast.parse` for two host `ast` rows on a file (spy count `== 1`); filters by `languages` and `call_sites`; refuses a non-`HostHit` item, a mismatched `ast` path and a `str` return; wraps a raised `AcfInputError`, a generator that raises mid-iteration, a generator that yields an invalid `HostHit`, and `sys.exit(0)` as `DetectorPackError`. |
| `plugins/arch-compliance/tests/test_builtin_detectors.py` (new) | `set(KNOWN_DETECTORS) == ALL_PYTHON_DETECTOR_IDS \| TS_DETECTOR_IDS`; no LLM prompt id is a key; each `TS_MANDATE_IDS` value appears as `mandate_id: "<value>"` in its rule file under `plugins/arch-compliance/detectors/typescript/src/rules/`; `fail_loud_ratchet` maps to `DIFF_CALL_SITES` and every other id to `TIER1_CALL_SITES`; every row of the `README.md` detector table names a key of `KNOWN_DETECTORS`, its mandate id is that key's `mandate_id`, and every Python key appears in the table. |
| `plugins/arch-compliance/tests/test_registry.py` | `:30` passes `known_detectors=KNOWN_DETECTORS`. A malformed host reference raises `AcfInputError` with and without `known_detectors` and for an `unenforced` row; an active `ast` row with only `[audit]` and an active host `ast` row with `languages: none` raise `AcfInputError` without `known_detectors`. With `known_detectors`: an active `partial` unknown built-in raises `UnknownDetectorError`; an `ast` row naming an LLM prompt id raises `UnknownDetectorError`; a `fail_loud_bare_except` row with another `id`, and a `fail_loud_ratchet` row declaring `hook`, raise `AcfInputError`; a host row raises `AcfInputError` without `repo_root` and `UnknownDetectorError` for a missing file; an existing host file loads, and a module that raises at import time is not imported by `load_mandates`. |
| `plugins/arch-compliance/tests/test_enforcement.py` | Every `apply_registry` call (`:54`, `:60`, `:66`, `:72`, `:84`, `:94`, `:104`, `:110`, `:125`, `:130`) passes `call_sites=`. A new case drops a finding whose row lacks the given call site. |
| `plugins/arch-compliance/tests/test_hooks.py` | `:199-218` keeps its WARN-context coverage by setting the copied fixture's `no-shims.hasattr` row to `call_sites: [ci, hook]`. A new case asserts the hook does not report a `[ci]`-only row. New cases (the hook runs in a subprocess, `:22-29`): exit `0` without importing a host module when `.acf/enabled` is absent (the module raises at import); exit `1` on an unknown detector when enabled; host `ast` and `guard` rows declaring `hook` run, `[ci]`-only host guards do not. |
| `plugins/arch-compliance/tests/test_diff_cli.py` | New cases use `fresh_host_loader`: host `ast` and `guard` rows declaring `ci` run and exit `1` on `BLOCK`; an exemption token on a non-code file flagged by a host guard is honoured. |
| `plugins/arch-compliance/tests/test_adr_citations.py` | A drive-relative citation (`"C:a/b.py"`) classifies `external`. Existing cases pass unchanged. |
| `plugins/arch-compliance/tests/test_acf_mandate_skill.py` | Unchanged; it runs the acf-mandate `## Validate` snippet (`:20-25`), so the rewritten snippet (§4.8) keeps the fenced `bash` / `python -c "..."` shape it extracts. |
| `tests/test_self_host.py` | `:23` passes `repo_root=ROOT`. `:40` checks each manual row with `resolve_under_root(ROOT, m.detector)` (adding the escape check) instead of `(ROOT / m.detector).is_file()`. |

### 4.8 Prose and version

| Site | Change |
|---|---|
| `config/architecture/ARCHITECTURE.md` | New `## Host detectors and call sites` section: the reference syntax, the `HostHit` contract, the call-site rule and the built-in contracts (Decisions 2 and 3), and the trust boundary (Decision 7). It ends `No row: enforced by plugins/arch-compliance/tests/test_host_detectors.py, test_builtin_detectors.py, test_registry.py, test_hooks.py and test_diff_cli.py.` |
| `config/architecture/ARCHITECTURE.md:9-11` | The preamble's "run the registry's detectors on changed `.py`, `.ts` and `.tsx` files" adds that host guards see every changed path and that rows run where their `call_sites` say. |
| `plugins/arch-compliance/skills/acf-mandate/SKILL.md` | `:10`, `:41`, `:43` (call-site vocabulary and its effect), `:55`, `:58`, `:68`, `:74`, `:88-112` (snippet uses `repo = resolve_repo(None)` and `load_mandates(repo / MANDATES_REL, known_detectors=KNOWN_DETECTORS, repo_root=repo)`; the detector union text at `:106-112` becomes "the built-in contracts in `acf.detectors.KNOWN_DETECTORS`"), `:116`, `:120`, `:122`, `:138`. |
| `plugins/arch-compliance/skills/acf-mandate/SKILL.md` (call-site advice) | `:59` and `:79`: an active `ast`/`guard` row must keep at least one Tier-1 site at which its detector runs, and a built-in row's `id` is its detector's mandate id; deprecate with `status: unenforced`. |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md` | `## Step 7` (`:140-151`): `.acf/enabled` is the opt-in for the automatic hooks, host detectors included; `:150` adds that committing `.acf/` opts every clone into running host detectors on edit. `:159`: the PostToolUse row covers host detectors and edited non-code paths. |
| `README.md` | `:62`, `:76` and `:106`: the gates run active rows by `call_sites` (`:76` adds it to the status rule), and host guards see every changed path. The detector table (`:66-74`) gains a call-sites column (`fail_loud_ratchet`: `ci`/`precommit` only) and is pinned by `plugins/arch-compliance/tests/test_builtin_detectors.py`. `:108` unchanged. |
| `docs/guides/SUPERPOWERS_COMPLEMENT.md:87` | The gating rule adds that a row gates only at the call sites it declares (a `[ci]`-only row is not reported by the PostToolUse hook). |
| `docs/design/ADR_GATE_HOST_CONTRACT.md:302-303` | The citation of `citations.py:49` / `:74` as owners of the repo-relative test now names `acf.engine.looks_absolute` and `resolve_under_root`. |
| `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md` | `:104`: the call-site vocabulary and the Tier-1 sets. `:161`: the PostToolUse row runs rows declaring `hook`/`posttooluse`, host guards on every edited path. `:111`: drift covers the built-in contracts and resolvable host references. `:184`: *"Unknown built-in detector id, a built-in row whose id or call sites disagree with its detector, an unresolvable host reference, or no Tier-1 call site on an active (enforced or partial) `ast` or `guard` row → registry validation fail."* |
| `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` | `:84` and `:418-420`: `KNOWN_DETECTORS` is defined in `acf.detectors` and re-exported by `acf.cli_check_diff`; the stated reason for its home (`acf.registry` cannot import `acf.judge`) still holds, since `acf.detectors` imports `acf.registry` and neither imports `acf.judge`. `:266-268`: as the doctrine preamble change above. `:373-376`: PostToolUse runs rows declaring `hook`/`posttooluse` and passes every edited in-repo path to host guards. `:389-393`: the `no-shims.hasattr` rows (`[ci]` only) are no longer reported by the hook; the census text says the hook reports the two `explicit-any` WARN rows. |
| `pyproject.toml:3`, `plugins/arch-compliance/.claude-plugin/plugin.json:3` | `"0.2.2"` → `"0.2.3"`. |

---

## 5. Relationships and shape fit

### 5.1 Documents

| Document | Relationship | Disposition |
|---|---|---|
| `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md` | `ADJACENT` | Parent architecture; `:102`, `:123`, `:125` call for this extension point; `:104`, `:111`, `:161` and `:184` are updated (§4.8). |
| `docs/design/ADR_GATE_HOST_CONTRACT.md` | `ADJACENT` | Owns `acf.adr`; `acf/adr/citations.py` changes only to consume the shared engine helpers (§4.1). Its `:302-303` is updated (§4.8). |
| `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` | `ADJACENT` | `tests/test_self_host.py:23`, `:40` change (§4.7); its `KNOWN_DETECTORS` placement (`:84`, `:418-420`), preamble restatement (`:266-268`), PostToolUse description and census (`:373-376`, `:389-393`) are updated (§4.8). |
| `docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md` | `DISJOINT` | Tier-2 judge; `cli_check_llm.py` is unchanged. |
| `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md` | `DISJOINT` | Housekeeping skill. |

### 5.2 Elements

| New / changed element | Existing site | Relationship and resolution |
|---|---|---|
| `looks_absolute`, `resolve_under_root` | `plugins/arch-compliance/python/acf/adr/citations.py:49-51`, `:74-76` | `SUBSUMED`: citations' private copies are deleted and its two call sites use the engine helpers. `load_host_detector`, `load_mandates`, `make_line_lookup` and `tests/test_self_host.py:40` use `resolve_under_root` too. |
| `resolve_under_root` | `abs_path.relative_to(repo)` (`plugins/arch-compliance/hooks/posttooluse_gate.py:242-245`); the ratchet's walk filter (`plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:59-62`) | `ADJACENT`: `resolve_under_root` turns a relative string into a contained `Path`; those two turn an already-resolved absolute `Path` into its relative string and skip what has none. The hook's result decides host-dispatch eligibility (§4.6). The ratchet's filter runs on unresolved paths, so a `params.roots` entry containing `..` is not contained by it; the ratchet is unchanged by this design (`## Scoped refactor`). |
| `validate_posix_rel_path` | `PosixStr` (`plugins/arch-compliance/python/acf/adr/contract.py:129`) | `ADJACENT`: `PosixStr` refuses backslashes in persisted ADR text fields; `validate_posix_rel_path` refuses any non-relative path, using `contains_backslash` and `looks_absolute`. `PosixStr` is unchanged. |
| `Mandate.runs_at`, `MandateRegistry.active` | `cli_check_diff.py:94-99`; `posttooluse_gate.py:229-236`, `:284-286`; `enforcement.py:47` | `SUBSUMED`: each of these sites calls the new definition. |
| `Mandate.runs_at` | `run_judge` (`plugins/arch-compliance/python/acf/judge.py:214-230`) | `ADJACENT`: Tier-2 reviews every `llm` row it is given and reads status only to require a provider (Decision 2 scope). |
| `KNOWN_DETECTORS` contracts | `KNOWN_DETECTORS` frozenset (`cli_check_diff.py:25`); the literal mandate ids in the five scanner modules | `SUBSUMED`: the frozenset becomes the mapping's import; each literal becomes the constant the mapping also reads. |
| Host-reference and row-shape validation | `plugins/arch-compliance/python/acf/registry.py:56-63` | `SUBSUMED`: moved onto `Mandate` and extended in `load_mandates`. |
| Host-file existence check in `load_mandates` | manual-row check (`tests/test_self_host.py:40`) | `SUBSUMED` in mechanism: both use `resolve_under_root` and `is_file()` (§4.7). The test keeps its host-specific prefix rule. |
| `HostHit` → `Finding` construction | `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:75-95` | `ADJACENT`: the bridge decodes JSON from a plugin-owned Node subprocess and takes `mandate_id` and severity from it; the host runner receives typed `HostHit` objects and takes both from the row. |
| `HostHit` → `Finding` construction | `_to_finding` (`plugins/arch-compliance/python/acf/judge.py:236-253`) | `ADJACENT`: the judge demotes severity by confidence and admits `path="<diff>"` and `line=0`; host findings take severity straight from the row and require a relative path and `line >= 1`. |
| `make_line_lookup` | `cli_check_diff.py:76-80`, `posttooluse_gate.py:119-123` | `IDENTICAL`: both closures are deleted. |
| `load_host_detector` `sys.path` insertion | `posttooluse_gate.py:22-26`; `plugins/arch-compliance/hooks/inject_constraints.py:28-29` | `ADJACENT`: the hooks put the plugin's own `python/` on the path at start-up. The loader inserts one host root once per process, ahead of it, and refuses a root that would shadow `acf` (§4.4 item 3). |
| `_WIN_DRIVE_RE` | `plugins/arch-compliance/python/acf/adr/contract.py:95` | `ADJACENT`: finds backslash drive paths inside persisted ADR text; unchanged. |

---

## 6. Doctrine compliance

| Anchor (`config/architecture/ARCHITECTURE.md`) | Mandate id | How the design complies |
|---|---|---|
| `## Fail loud` (`:24-41`) | `fail-loud.bare-except` | §6.1 lists each invalid state and the error that refuses it. The two broad handlers (§4.4 items 3 and 4) re-raise as typed errors and carry the `fail-loud.bare-except-ok` token with a reason (`:29-30`). |
| `## No shims` (`:43-53`) | `no-shims.hasattr` | Callable lookup is `getattr(mod, attr, None)` followed by `callable(...)` and a raise; no `hasattr`. |
| `## POSIX paths` (`:55-64`) | `posix-paths.str-serialization` | `HostHit.path` is validated by `validate_posix_rel_path`; error messages use `.as_posix()`. |
| `## One base exception` (`:99-103`) | `plugin.one-base-exception` | No new exception class; uses `AcfInputError`, `UnknownDetectorError`, `DetectorPackError` (`plugins/arch-compliance/python/acf/exceptions.py:5`, `:13`, `:29`). |
| `## One owner for host paths` (`:105-116`) | `plugin.one-owner-host-paths` | `plugins/arch-compliance/python/acf/engine.py`, `plugins/arch-compliance/python/acf/registry.py`, `plugins/arch-compliance/python/acf/detectors/__init__.py` and `plugins/arch-compliance/python/acf/detectors/host.py` spell no `config/architecture` path; the skill snippet takes `MANDATES_REL` and `resolve_repo` from `acf.repo`. |
| `## Declared, never defaulted` (`:118-133`) | `plugin.declared-never-defaulted` | `repo_root` is required for an active host row (`AcfInputError` otherwise), and `apply_registry`'s `call_sites` has no default. |
| `## Prose names no host` (`:135-143`) | `plugin.adr-code-names-no-host`, `plugin.gate-prose-names-no-host` | The runtime messages in §4.2–§4.4 and the prose in §4.8 name no origin host. |
| `## Live consumers` (`:153-157`) | — | §6.2 lists each new export and its runtime caller. |
| `## No completeness claims` (`:159-169`) | — | Population claims carry their recipe (§1, §3, Appendix) or are per-item tables (§4.3, §4.7, §4.8, §6.1, §6.2). |
| `## Declared text decoding` (`:171-182`) | — | New `read_text` calls (`cli_check_diff.py` TypeScript branch, `make_line_lookup`) declare `encoding="utf-8"`. No subprocess is added. |
| `## Release discipline` (`:184-194`) | — | Skill prose changes, so the version is bumped in both files `:186-187` names. |
| `## Single point of definition` (`:196-209`) | — | Within the Tier-1 gates: the absolute and under-root string tests live in `acf.engine`; row activity in `Mandate.runs_at` (Tier-2 keeps its own, Decision 2); each built-in mandate id in one constant; host loading and running in `acf.detectors.host`; line lookup in `make_line_lookup` (§5.2). |
| `## Scoped refactor` (`:211-215`) | — | Consolidations touch only the code paths this design changes; the shared dispatcher and the shared parse helper are non-goals (§3). |
| `## Frozen ledger format` (`:145-151`) | `plugin.frozen-ledger-format` | No ledger model changes. |

### 6.1 Invalid states and their refusal

| Invalid state | Refused by | Error |
|---|---|---|
| Malformed host reference on an `ast`/`guard` row (any status, any caller) | `Mandate._row_shape` | `AcfInputError` |
| Active `ast`/`guard` row with no Tier-1 call site (any caller) | `Mandate._row_shape` | `AcfInputError` |
| Active host `ast` row with `languages: none` (any caller) | `Mandate._row_shape` | `AcfInputError` |
| Active built-in row naming an id not in `KNOWN_DETECTORS` (LLM prompt ids included) | `load_mandates` with `known_detectors` | `UnknownDetectorError` |
| Active built-in row whose `id` is not its detector's mandate id | `load_mandates` with `known_detectors` | `AcfInputError` |
| Active built-in row declaring a Tier-1 site where no gate runs its detector | `load_mandates` with `known_detectors` | `AcfInputError` |
| Active host row, no `repo_root` | `load_mandates` with `known_detectors` | `AcfInputError` |
| Active host row whose file is missing or outside the root | `load_mandates` with `known_detectors`; `load_host_detector` | `UnknownDetectorError` |
| A second host root in one process, or a root containing `"acf/"` or `"acf.py"` | `load_host_detector` | `AcfInputError` |
| Host module fails to import (`SystemExit` included), or has no such callable | `load_host_detector` at dispatch | `UnknownDetectorError` |
| Host callable raises, or its returned iterable raises while consumed (`SystemExit` included) | `_call_host` | `DetectorPackError` |
| Host returns `None`, a `str`/`bytes`, or a non-iterable | `_call_host` | `DetectorPackError` |
| Host yields a non-`HostHit` item, or an `ast` hit on another file | `_to_findings` | `DetectorPackError` |
| `HostHit` with a non-relative or backslash path, `line < 1`, or empty message | `HostHit` validation, raised inside `_call_host` | `DetectorPackError` |

### 6.2 New exports and their callers

| Export | Runtime caller |
|---|---|
| `acf.engine.looks_absolute` | `validate_posix_rel_path`; `acf/adr/citations.py` |
| `acf.engine.resolve_under_root` | `load_mandates`; `load_host_detector`; `make_line_lookup`; `acf/adr/citations.py` |
| `acf.engine.validate_posix_rel_path` | `parse_host_detector_ref`; `HostHit` |
| `DIFF_CALL_SITES` / `HOOK_CALL_SITES` | `cli_check_diff.py` / `posttooluse_gate.py`; `KNOWN_DETECTORS` |
| `TIER1_CALL_SITES` | `Mandate._row_shape`; `_check_builtin`; `KNOWN_DETECTORS` |
| `BuiltinDetector` | `KNOWN_DETECTORS`; `load_mandates` |
| `Mandate.is_active` | `Mandate.runs_at`; `Mandate._row_shape`; `load_mandates` |
| `Mandate.runs_at` | `MandateRegistry.active`; `apply_registry` |
| `MandateRegistry.active` | both gates; both host runners |
| `is_host_detector_ref`, `parse_host_detector_ref` | `Mandate._row_shape`; `load_mandates`; host runners; `load_host_detector` |
| `acf.detectors.KNOWN_DETECTORS` | both gates (`load_mandates` calls) |
| scanner mandate-id constants, `TS_MANDATE_IDS` | their scanners; `KNOWN_DETECTORS` |
| `HostHit` | host callables (imported by host code); `_to_findings` |
| `load_host_detector` | `scan_host_ast_file`; `scan_host_guards` |
| `scan_host_ast_file`, `scan_host_guards` | both gates |
| `make_line_lookup` | both gates |

---

## 7. Verification and definition of done

1. The §4.7 tests exist and pass.
2. `PYTHONUTF8=1 python -m pytest -q`, `PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main` and `npm test --prefix plugins/arch-compliance/detectors/typescript` pass.
3. `pyproject.toml:3` and `plugins/arch-compliance/.claude-plugin/plugin.json:3` read `"0.2.3"`.
4. This spec clears `/adversarial-design-review`, with its run detail and ledger row committed on the branch.

---

## Appendix — Receipts at `a338cad`

| Premise | Recipe | Observed |
|---|---|---|
| `load_mandates` callers | `git grep -n "load_mandates(" -- plugins tests ':!plugins/arch-compliance/python/acf/registry.py'` | `plugins/arch-compliance/hooks/inject_constraints.py:104`, `plugins/arch-compliance/hooks/posttooluse_gate.py:107`, `plugins/arch-compliance/python/acf/cli_check_diff.py:70`, `plugins/arch-compliance/python/acf/cli_check_llm.py:54`, `plugins/arch-compliance/skills/acf-mandate/SKILL.md:95` (plus a prose mention at `:141`), `plugins/arch-compliance/skills/architecture-review/SKILL.md:62`, `plugins/arch-compliance/tests/test_profile_drift.py:24`, `plugins/arch-compliance/tests/test_registry.py:10,17,30,47,57`, `tests/test_self_host.py:23`. Only `cli_check_diff.py:70`, `SKILL.md:95`, `test_profile_drift.py:24`, `test_registry.py:30` and `test_self_host.py:23` pass `known_detectors`; the others reach only the `Mandate` row-shape checks, which raise `AcfInputError`. |
| `KNOWN_DETECTORS` users | `git grep -n "KNOWN_DETECTORS" -- '*.py' '*.md' ':!docs'` | `plugins/arch-compliance/python/acf/cli_check_diff.py:25,70`, `plugins/arch-compliance/skills/acf-mandate/SKILL.md:91,95,106,111,112`, `plugins/arch-compliance/tests/test_profile_drift.py:7,24`, `tests/test_self_host.py:5,14,23`, and prose at `config/architecture/ARCHITECTURE.md:228`. Each imports it from `acf.cli_check_diff`, passes it to `load_mandates`, sorts its keys or names it in prose; the re-export keeps every one of those working. |
| `apply_registry` callers | `git grep -n "apply_registry(" -- '*.py'` | `plugins/arch-compliance/hooks/posttooluse_gate.py:125`, `plugins/arch-compliance/python/acf/cli_check_diff.py:82`, and `plugins/arch-compliance/tests/test_enforcement.py` at `:54,60,66,72,84,94,104,110,125,130`. |
| Direct `Mandate` construction | `git grep -n "Mandate(" -- '*.py'` | `plugins/arch-compliance/tests/test_enforcement.py:19` (`detection="ast"`, `call_sites=["ci"]`), `plugins/arch-compliance/tests/test_judge.py:41` and `plugins/arch-compliance/tests/test_template.py:73` (`detection="llm"`), besides the class itself. None is refused by `Mandate._row_shape`. |
| Active-row filters | `git grep -n "_active_mandates\|status != \"unenforced\"\|status == \"unenforced\"" -- '*.py' ':!*/tests/*'` | `plugins/arch-compliance/hooks/posttooluse_gate.py:231,235,285`; `plugins/arch-compliance/python/acf/cli_check_diff.py:94,98,112,113,158,168`; `plugins/arch-compliance/python/acf/enforcement.py:47`. A wider recipe, `git grep -n "\.status\b" -- plugins/arch-compliance/python plugins/arch-compliance/hooks ':!*/adr/*'`, adds `registry.py:58` (replaced by §4.2), `judge.py:218` (Tier-2, unchanged) and a display-only read at `inject_constraints.py:158`. |
| Built-in mandate ids | `git grep -n 'mandate_id="' -- plugins/arch-compliance/python/acf/detectors` | `build_artifacts.py:31` `ops.no-build-artifacts`; `facade_sinks.py:69` `facade.forbid-sink`; `fail_loud_ratchet.py:132` `fail-loud.ratchet`; `fsm_guard.py:59` `fsm.transition-guard`; `python_pack.py:67` `fail-loud.bare-except`, `:97` `no-shims.hasattr`, `:144` and `:172` `posix-paths.str-serialization`. |
| Shipped `ast`/`guard` rows against the contracts | `python -c "import yaml,glob; [print(f, m['status'], m['id'], m['detector'], m['call_sites']) for f in ['config/architecture/mandates.yml', *glob.glob('plugins/arch-compliance/profiles/*/mandates.yml'), 'plugins/arch-compliance/tests/fixtures/mandates_valid.yml'] for m in yaml.safe_load(open(f, encoding='utf-8')) if m['detection'] in ('ast','guard')]"` | In each printed row the `id` is the mandate id its detector stamps (row above and `emptyCatch.ts:23`, `explicitAny.ts:15`). Every active row declares `ci`, and `[ci, hook]` except `no-shims.hasattr` (`[ci]`). The only `fail_loud_ratchet` rows declare `[ci]` and are `unenforced`. No row is `partial`. |
| Inline test registries | `git grep -n "detector:" -- 'plugins/arch-compliance/tests/*.py'` | YAML rows: `test_diff_cli.py:75` (`fail-loud.bare-except` / `fail_loud_bare_except`, `[ci, hook]`); `test_registry.py:24` (`not_a_real_detector`, `[ci]`, expected to raise `UnknownDetectorError`); `test_registry.py:35` (`manual`, `[audit]`); `test_judge.py:390` (`llm`, `unenforced`). The remaining hits are keyword defaults of test helpers (`test_baseline.py:28` builds a `Finding`; `test_enforcement.py:16` and `test_judge.py:39` build the `Mandate` rows listed above). |
| `KNOWN_DETECTORS` size | `python -c "from acf.cli_check_diff import KNOWN_DETECTORS as K; print(len(K))"` | `13` today (9 Python and TypeScript ids plus 4 LLM prompt ids); `9` after this design. |
