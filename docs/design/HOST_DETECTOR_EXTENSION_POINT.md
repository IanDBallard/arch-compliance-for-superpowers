# Host Detector Extension Point (`ast` and `guard` Callables)

**Status:** Draft (v7)
**Date:** 2026-11-05
**Spec kinds:** `defect`, `feature`
**Repo:** `IanDBallard/arch-compliance-for-superpowers`, `main` at `a338cad` (branch `feat/host-detector-extension`).
**Workstream:** HistoricMansions Workstream E Phase 2 (prerequisite Spec 2a — Tier-1 host detector extension point).
**Governing mandates:** `config/architecture/ARCHITECTURE.md` sections `## Fail loud` (`:24-41`), `## No shims` (`:43-53`), `## POSIX paths` (`:55-64`), `## Fail-loud ratchet` (`:70-73`), `## One base exception` (`:99-103`), `## One owner for host paths` (`:105-116`), `## Declared, never defaulted` (`:118-133`), `## Prose names no host` (`:135-143`), `## Frozen ledger format` (`:145-151`), `## Live consumers` (`:153-157`), `## No completeness claims` (`:159-169`), `## Declared text decoding` (`:171-182`), `## Release discipline` (`:184-194`), `## Single point of definition` (`:196-209`), `## Scoped refactor` (`:211-215`), and the five portable governing principles at `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51`.
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
   - `Mandate.call_sites` becomes `list[CallSite]`, where `CallSite = Literal["ci", "precommit", "hook", "posttooluse", "audit"]` is defined once in `acf.registry`. Now that `call_sites` routes rows, a misspelled site (`[ci, hooks]`) is refused at row construction instead of silently dropping the row from a gate.
   - `acf.registry` gains `DIFF_CALL_SITES = frozenset({"ci", "precommit"})`, `HOOK_CALL_SITES = frozenset({"hook", "posttooluse"})`, `TIER1_CALL_SITES = DIFF_CALL_SITES | HOOK_CALL_SITES`, the property `Mandate.is_active` (`status != "unenforced"`), the method `Mandate.runs_at(call_sites) -> bool` (`is_active` and `call_sites` intersects the row's `call_sites`), and `MandateRegistry.active(call_sites, *, detector=None, detection=None) -> list[Mandate]`.
   - `acf-check-diff` gains a required `--call-site {ci,precommit}` argument (argparse `required=True`, `choices`), and runs with `frozenset({args.call_site})`. The invocation declares which gate it is. The origin host's guard runner works the same way: it selects rows per site (`hm:scripts/ci/run_guards.py:116`), refuses an unknown site (`:107-111`) and refuses a site that selects nothing (`:126-130`), though its `--site` defaults to `ci` (`:317-321`). A missing or unknown value exits `2` with argparse's usage error. A site that selects no active `ast` or `guard` row is refused with `AcfInputError` (exit `1`) rather than reported as a clean run (§4.6).
   - Every shipped `ast`/`guard` row that declares `ci` also declares `precommit`: 9 rows in `config/architecture/mandates.yml`, 7 in `plugins/arch-compliance/profiles/python-service/mandates.yml`, 3 in `plugins/arch-compliance/profiles/react-app/mandates.yml`, and 3 in the test fixture `plugins/arch-compliance/tests/fixtures/mandates_valid.yml` (Appendix). `acf-check-diff` serves pre-commit today without telling it from CI, so this keeps each row's pre-commit behaviour unchanged. The PostToolUse hook is one entry point, so it runs with `HOOK_CALL_SITES`: `hook` and `posttooluse` are two spellings of that one site in the vocabulary, used by this repository and by the origin host respectively.
   - `apply_registry` gains a required keyword `call_sites` and drops findings whose row does not `runs_at` it. This filter is needed at that one sink because the built-in scanners emit findings without consulting the registry (`plugins/arch-compliance/python/acf/detectors/python_pack.py:27-52`). `acf-check-diff` passes its declared site; the hook passes `HOOK_CALL_SITES`.
   - `cli_check_diff._active_mandates` and the hook's three inline filters are replaced by `registry.active(...)`.
   - Scope: the two Tier-1 gates only. The Tier-2 judge reviews every `llm` row it is given, unenforced included, and reads `status == "enforced"` only to decide whether a provider is required (`plugins/arch-compliance/python/acf/judge.py:213-218`, `:230`); it keeps that separate definition and is unchanged.
   - Consequence, accepted: a row declaring only `[ci]` is no longer reported by the PostToolUse hook, nor by a `--call-site precommit` run. This covers this repository's `no-shims.hasattr` row, the same row in the `python-service` profile (`plugins/arch-compliance/profiles/python-service/mandates.yml:18`), and so every host that `/acf-setup` installed from that profile: each loses that row's edit-time `WARN`. `plugins/arch-compliance/tests/test_hooks.py:199-218` is rewritten (§4.7), and the profile row is left as its authors declared it.
   - Consequence, accepted: hosts that `/acf-setup` installed before this change hold copies of the profile registries without `precommit`. Until a host adds `precommit` to the rows it wants in pre-commit, its `--call-site precommit` run is refused ("selects no active" mandate, exit `1`), never a silent pass. §4.8 adds that upgrade step to the README and the acf-setup skill.
   - Consequence, accepted: every existing `acf-check-diff` invocation must add `--call-site`. The ones shipped or documented here are listed in §4.8 (this repository's `.github/workflows/ci.yml:40`, the README, the acf-setup snippets, `CLAUDE.md`, the guide), and `plugins/arch-compliance/tests/test_diff_cli.py` passes it in each `main([...])` call (§4.7). A host's own pre-commit or CI configuration that omits it fails loud with the usage error until updated.
3. **Every built-in detector declares where it runs and which row it reports to.** `acf.registry.BuiltinDetector` is a frozen dataclass `(mandate_id: str, call_sites: frozenset[str])`. `acf.detectors.KNOWN_DETECTORS` maps each built-in `ast`/`guard` id to one, built from detector-id and mandate-id constants that each scanner module also uses at its `Finding` construction (§4.3). It replaces the five detector-id sets, which are deleted (§4.9). LLM prompt ids are not in it. With `known_detectors` given, `load_mandates` refuses an active built-in `ast`/`guard` row whose detector is not in the map (`UnknownDetectorError`), whose `id` is not the detector's `mandate_id`, or which declares a Tier-1 call site at which no gate runs its detector (`AcfInputError`). So each of the cases in §1 item 1 is refused at load. Consequence, accepted: with unique row ids (`registry.py:33-41`), a host has at most one active row per built-in detector. Today a second `forbid_facade_sink` or `fsm_transition_guard` row runs the scanner with its own `params`, but its findings carry the fixed id and land on the other row (`cli_check_diff.py:128-150`); no shipped registry has such a pair (Appendix). Consequence, accepted: "active" includes `partial`, which gates like `enforced` (*"`status: partial` still **gates** when detectors emit findings"*, `plugins/arch-compliance/skills/acf-mandate/SKILL.md:57`), so the load refusals here and in Decision 4 reach `partial` rows. A host that followed the skill's advice *"Prefer `partial` or `unenforced` when the detector/prompt does not exist yet"* (`:58`) and wrote a `partial` row naming a detector or prompt that does not exist has its registry refused at load until that row is set to `unenforced`. §4.8 rewrites `:58`, and the same advice at `:68` and `:138`, to name `unenforced` only, and adds the step to the upgrade note.
4. **Row-shape rules live on `Mandate`; rules that need outside data live in `load_mandates`.** A `Mandate` `model_validator` refuses (`AcfInputError`), for every caller that builds a row: a malformed host reference on an `ast`/`guard` row (any status); an active `ast`/`guard` row with no Tier-1 call site; an active host `ast` row whose `languages` is not in `{"python", "typescript", "both"}`. `load_mandates` with `known_detectors` adds the built-in contract (Decision 3) and, for host rows, requires an explicit `repo_root` (`AcfInputError`) and an existing file under it (`UnknownDetectorError`). `load_mandates` with `llm_prompt_ids` refuses an active `llm` row whose detector is not a prompt id (`UnknownDetectorError`). That is the rule the acf-mandate skill states today, *"still requires a known prompt id in `LLM_PROMPT_IDS` for drift discipline"* (`plugins/arch-compliance/skills/acf-mandate/SKILL.md:56`), which nothing enforces: `registry.py:60` consults `known_detectors` only for `ast`/`guard` rows. `acf-check-diff` passes `acf.judge.LLM_PROMPT_IDS`, which keeps that export's one runtime consumer once it leaves `KNOWN_DETECTORS`. The PostToolUse hook does not pass it: the hook runs no `llm` row, and importing `acf.judge` would add `httpx` (`plugins/arch-compliance/python/acf/judge.py:11`) to every edit. So an active row with an unknown prompt id is refused by `acf-check-diff` at pre-commit and CI and by the acf-mandate `## Validate` snippet, not at edit time. Import and callable lookup happen only at dispatch (§4.4), so `load_mandates` runs no host code for any caller.
5. **Host callables return `HostHit`, never `Finding`.** `acf.detectors.host.HostHit` is a frozen Pydantic model with exactly `path` (validated by `validate_posix_rel_path`), `line` (`>= 1`) and `message` (non-empty). The runner builds each `Finding` from the hit and the mandate row, so a host cannot attach a finding to the wrong row and no field is overwritten. The runner materialises the callable's result inside the region that wraps failures, so a generator's errors are wrapped too.
6. **One host root per process, refused rather than repaired, and appended to `sys.path`.** `load_host_detector` records the first root it serves and raises `AcfInputError` for any other root in the same process. Production callers resolve one repository per process (`plugins/arch-compliance/python/acf/cli_check_diff.py:63`; `plugins/arch-compliance/hooks/posttooluse_gate.py:65`, a fresh process per edit). In-process tests over several roots reset the loader through a test fixture (§4.6). The root is appended to `sys.path`, not inserted at the front, so the loader adds no shadowing of its own: a host top-level name that an earlier `sys.path` entry provides resolves to that entry. How early the host root already sits depends on the entry point, and the loader does not change it:

| Entry point | Host root already on `sys.path`? | Effect of appending |
|---|---|---|
| PostToolUse hook (`python <plugin>/hooks/posttooluse_gate.py`; `plugins/arch-compliance/hooks/hooks.json`) | No: the hook inserts the plugin's `python/` at `sys.path[0]`, ahead of the hooks directory (`posttooluse_gate.py:22-26`) | Host modules cannot shadow standard-library, third-party or plugin modules; the plugin's `acf` is imported first (`posttooluse_gate.py:28`) |
| `acf-check-diff` console script (`pyproject.toml:19-20`) | No: `sys.path[0]` is the script's directory | As for the hook |
| `python -m acf.cli_check_diff` run from the host root (this repository's `.github/workflows/ci.yml:40`) | Yes: `-m` puts the working directory first | None. The host root already precedes every other entry, as it does today, so a host top-level module (including a host `acf/`) already shadows later imports there. This design does not create that exposure, and it does not remove it. |

A host detector module is loaded under a synthetic top-level name (§4.4 item 3), so it cannot use relative imports. If it is also imported elsewhere by its dotted name, it exists twice in the process. Host detector modules use absolute imports from the host root.
7. **Trust boundary.**
   - Automatic hooks: the PostToolUse hook exits `0` before importing anything beyond `acf.repo` when `.acf/enabled` is absent (`plugins/arch-compliance/hooks/posttooluse_gate.py:72-81`). That marker is the opt-in for running host code on edit.
   - Explicit invocation: `acf-check-diff` runs only when the host's own pre-commit or CI configuration invokes it (this repository: `.github/workflows/ci.yml:40`). That invocation is the opt-in. `.acf/` is gitignored here (`.gitignore:8`), so a CI checkout never carries the marker, and requiring it there would disable CI. A person running `acf-check-diff` by hand in a checkout they do not trust is the residual case, accepted.
   - What the wrapping guarantees: every failure raised while a runner calls host code (module execution, callable lookup, the call, consuming and rebuilding its result, formatting its exception) becomes a typed ACF error (§4.4). It does not confine host code. A host module runs in the gate's process with its privileges and can, for example, register an `atexit` handler or start a thread that runs after the runner returns; that code is the host's own, run because the host opted in above.
   - The SubagentStart hook (`plugins/arch-compliance/hooks/inject_constraints.py:104`) and `acf-check-llm` (`plugins/arch-compliance/python/acf/cli_check_llm.py:54`) call `load_mandates`, which never imports host code (Decision 4), so neither runs host code.
8. **What this design makes redundant is deleted, and its callers switch to the one definition.** `## Scoped refactor` asks to *"remove legacy dependencies or non-contractual patterns in code paths you are changing"* (`config/architecture/ARCHITECTURE.md:213-215`). The existing definitions listed in §4.9, each of which a new definition here duplicates, are deleted rather than recorded as debt; §4.9 gives each one's recipe and the behaviour its switch changes at the old caller. The spec makes no claim that §4.9 lists every duplicate in the tree. A switch that refuses input the old code accepted is checked against every shipped value first (§4.9, Appendix).

---

## 3. Scope and Non-Goals

### In scope

| File | Change |
|---|---|
| `plugins/arch-compliance/python/acf/engine.py` | Add `looks_absolute`, `resolve_under_root`, `validate_posix_rel_path` (§4.1). |
| `plugins/arch-compliance/python/acf/adr/citations.py` | `_looks_absolute` and `_escapes_repo` are deleted; their two call sites (`:161`, `:163`) call `acf.engine.looks_absolute` and `acf.engine.resolve_under_root` (§4.1). |
| `plugins/arch-compliance/python/acf/registry.py` | Call-site constants, `BuiltinDetector`, `Mandate.is_active`/`runs_at`/row-shape validator, `MandateRegistry.active`, `is_host_detector_ref`, `parse_host_detector_ref`, extended `load_mandates` (§4.2). |
| `plugins/arch-compliance/python/acf/detectors/__init__.py`, the five scanner modules and `typescript_bridge.py` | Detector-id and mandate-id constants, `TS_MANDATE_IDS` (stamped by the bridge), `KNOWN_DETECTORS`, and one params-to-arguments function per configurable scanner (§4.3); the five detector-id sets are deleted, and the ratchet resolves its paths with `resolve_under_root` (§4.9). |
| `plugins/arch-compliance/python/acf/detectors/host.py` (new) | `HostHit`, `load_host_detector`, `scan_host_ast_file`, `scan_host_guards` (§4.4). |
| `plugins/arch-compliance/python/acf/enforcement.py` | `apply_registry(..., *, call_sites)`; `make_line_lookup` (§4.5). |
| `plugins/arch-compliance/python/acf/cli_check_diff.py` | Wiring (§4.6). |
| `plugins/arch-compliance/hooks/posttooluse_gate.py` | Wiring (§4.6). |
| `plugins/arch-compliance/hooks/inject_constraints.py` | None: every new load-time refusal without `known_detectors` is `AcfInputError`, which `:105` already catches. |
| `plugins/arch-compliance/python/acf/cli_check_llm.py` | None: a malformed registry already surfaces at `:54` as an uncaught `AcfInputError` and non-zero exit; the new refusals reach it the same way. |
| `.github/workflows/ci.yml` | `:40` passes `--call-site ci` (Decision 2, §4.8). |
| `config/architecture/mandates.yml`, `plugins/arch-compliance/profiles/*/mandates.yml`, `plugins/arch-compliance/tests/fixtures/mandates_valid.yml` | Each `ast`/`guard` row declaring `ci` adds `precommit` (Decision 2, Appendix). |
| Tests, prose, version | §4.7 and §4.8. |

### Non-goals

- **No architecture-review runtime package and no architecture-review host configuration file.** Both belong to Spec 2b (architecture-review portability), not yet written. The existing compliance-baseline module that architecture-review uses (`plugins/arch-compliance/python/acf/baseline.py`) is not modified.
- **No `PosixRelPath` Pydantic alias in `acf.engine`.** `acf.engine` stays stdlib-only; `HostHit` applies `validate_posix_rel_path` through its own `AfterValidator`.
- **No change to `HistoricMansions` in this slice.** Its rows would still need rewriting at cutover: they carry no `languages` or `arch_anchor` field, both required by `Mandate` (`plugins/arch-compliance/python/acf/registry.py:20`, `:24`). Two behaviours of its driver are not reproduced by this contract and are left to the cutover spec: it reports an unparseable changed file as a `WARN` (or raises in range mode) with `exc.lineno or 0` as the line (`hm:scripts/ci/arch_compliance/driver.py:150-163`), while `scan_host_ast_file` skips unparseable files like the built-in scanners do and `HostHit.line` must be `>= 1`; and its guards read the staged or range blob, so they depend on diff mode, which `scan_guard` does not receive (it reads the worktree).
- **No shared Tier-1 dispatcher.** `## Single point of definition` asks that a *"decision procedure … needed by more than one module"* have *"exactly one canonical implementation that every call site consumes"* (`config/architecture/ARCHITECTURE.md:198-200`). The host decision procedure (which rows run, how a callable is loaded, called, wrapped and turned into findings) has one implementation, `acf.detectors.host`; each gate consumes it through `scan_host_ast_file` and `scan_host_guards`, as it already consumes each built-in scanner. What stays two-fold is the pair of dispatch loops, which exist today and differ in diff scope (added lines vs whole file), path collection and file filter (`cli_check_diff.py:102-184`, `posttooluse_gate.py:213-295`). Each gate calling the two host runners is two call sites of one procedure, not a second definition of it, so Decision 8 does not apply; merging the pre-existing loops is left out to keep this change small.

---

## 4. Design

### 4.1 Path helpers (`plugins/arch-compliance/python/acf/engine.py`)

`acf.engine` stays stdlib-only (`import ast`, `import re`, `from pathlib import Path`) and owns two string-to-path tests: whether a path string is absolute, and whether a path string resolves inside a root. `resolve_under_root` is the one containment test for a path string from outside the code (a registry row, a host hit, a harness payload). An absolute string is taken as is and then tested like any other, because `base / rel` yields `rel` when `rel` is absolute. Two sites do this job by hand today and switch to it (§4.9): the PostToolUse hook's `Path.is_absolute()` join (`plugins/arch-compliance/hooks/posttooluse_gate.py:203-204`) with its `relative_to(repo)` / `except ValueError` test (`:242-245`), and the ratchet's joins of `params.baseline` and `params.roots` (`plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:46`, `:122-124`) with its walk filter's `except ValueError: continue` (`:59-62`). After the switch, each of those sites converts an already-contained `Path` to its relative string with `relative_to(...).as_posix()`, which cannot fail there, and keeps no containment branch of its own.

```python
_ABSOLUTE_RE = re.compile(r"^([A-Za-z]:|/|\\\\)")


def looks_absolute(path: str) -> bool:
    """True for a drive-prefixed (``C:`` or ``C:/``), root-anchored or UNC path."""
    return bool(_ABSOLUTE_RE.match(path))


def resolve_under_root(root: Path, rel: str) -> Path | None:
    """Resolve ``rel`` against ``root`` (an absolute ``rel`` is taken as is); None when the result leaves ``root`` or cannot be resolved."""
    base = root.resolve()
    try:
        candidate = (base / rel).resolve()
    except RuntimeError:  # symlink loop on Python 3.11 and 3.12
        return None
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


def file_under_root(root: Path, rel: str) -> Path | None:
    """The existing regular file ``rel`` names under ``root``, else None. An OSError from stat propagates."""
    candidate = resolve_under_root(root, rel)
    return candidate if candidate is not None and candidate.is_file() else None


def parse_python(text: str) -> ast.Module | None:
    """Parse Python source; None when it does not parse (the scanners' skip convention)."""
    try:
        return ast.parse(text)
    except SyntaxError:
        return None
```

`Path.is_file()` returns `False` for a missing path, a directory and a symlink loop (it ignores `ENOENT`, `ENOTDIR`, `EBADF` and `ELOOP`), and re-raises any other `OSError`, such as permission denied on a parent directory. `file_under_root` lets that error propagate. Each caller in §4.2, §4.4 and §4.9 turns it into its own typed error; the PostToolUse hook's `_collect_paths` lets it propagate, as its `abs_path.is_file()` (`posttooluse_gate.py:239`) does today (§4.6). That re-raise is the behaviour of Python 3.11 to 3.13. `pyproject.toml:5` also admits later versions; where `is_file()` returns `False` for every `OSError`, such a path reports as missing (`UnknownDetectorError` at load, `[]` lines in `scan_host_guards`), which is still a typed or fail-safe outcome, not a traceback.

`pyproject.toml:5` allows Python 3.11, where a non-strict `Path.resolve()` raises `RuntimeError` on a symlink loop; Python 3.13 returns a path instead. `resolve_under_root` maps the loop to `None`, the value every caller already treats as "not under the root". So a looping host path reports as a missing file (`UnknownDetectorError` at load), yields no exemption lines, or classifies as `unresolved`; it never ends as a traceback.

`acf/adr/citations.py` imports `looks_absolute` and `resolve_under_root` and deletes its private copies. `resolve_citation` (`:129-185`) keeps its order (`proposed`, `asserted_absent`, then absolute → `external`, then escaping → `unresolved`), with `resolve_under_root(repo_root, path) is None` as the escape test. Two behaviours change: a drive-relative string such as `"C:a/b.py"` becomes `external` rather than going on to the existence checks, and on Python 3.11 and 3.12 a citation through a symlink loop classifies as `unresolved` instead of raising `RuntimeError`.

### 4.2 Registry (`plugins/arch-compliance/python/acf/registry.py`)

```python
CallSite = Literal["ci", "precommit", "hook", "posttooluse", "audit"]
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
    ...  # fields unchanged except:
    call_sites: list[CallSite]

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
    llm_prompt_ids: frozenset[str] | None = None,
    repo_root: Path | None = None,
) -> MandateRegistry:
    mandates = load_model_file(path, Mandate, subject="mandates file", fmt="yaml", many=True)
    if llm_prompt_ids is not None:
        for m in mandates:
            if m.is_active and m.detection == "llm" and m.detector not in llm_prompt_ids:
                raise UnknownDetectorError(
                    f"active mandate {m.id!r} references unknown llm prompt id {m.detector!r}"
                )
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
            try:
                module_path = file_under_root(repo_root, rel_path)
            except OSError as exc:
                raise UnknownDetectorError(
                    f"active mandate {m.id!r}: cannot stat host detector file "
                    f"{(repo_root / rel_path).as_posix()}: {exc}"
                ) from exc
            if module_path is None:
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

`registry.py` imports `file_under_root` and `validate_posix_rel_path` from `acf.engine`, `dataclass` and `Mapping` from the standard library, and nothing from `acf.detectors`. A `model_validator` that raises `AcfInputError` propagates that error with its own type through `load_model_file`, which converts only `ValidationError` (`plugins/arch-compliance/python/acf/loader.py:54-56`, `:70-73`); `MandateRegistry._unique_ids` (`registry.py:33-41`) already raises `AcfInputError` this way.

### 4.3 Built-in detector contracts (`plugins/arch-compliance/python/acf/detectors/`)

- Each scanner module gains a mandate-id constant and uses it at its `Finding` construction in place of the literal: `python_pack.py` (`FAIL_LOUD_BARE_EXCEPT_MANDATE_ID` at `:67`, `NO_SHIMS_HASATTR_MANDATE_ID` at `:97`, `POSIX_PATHS_STR_MANDATE_ID` at `:144` and `:172`), `build_artifacts.py:31`, `facade_sinks.py:69`, `fail_loud_ratchet.py:132`, `fsm_guard.py:59`. `python_pack.py` also gains three detector-id constants (`FAIL_LOUD_BARE_EXCEPT_DETECTOR_ID`, `NO_SHIMS_HASATTR_DETECTOR_ID`, `POSIX_PATHS_STR_DETECTOR_ID`) used at its `detector=` literals (`:72`, `:102`, `:152`, `:180`); the other four scanners already have theirs (`build_artifacts.py:10`, `facade_sinks.py:14`, `fail_loud_ratchet.py:19`, `fsm_guard.py:13`).
- Each configurable scanner module gains one function that turns a row's `params` into its keyword arguments: `facade_sink_args(params)`, `fsm_guard_args(params)` and `build_artifact_args(params)`. A required argument (`target_literal_re`; `state_field` and `validator_name`) is passed as `str(params.get(key, ""))`, as the gates pass it today. An optional one (`allowlist_globs`, `atomic_is_sink`) is passed through unchanged when its key is present in `params`, a `null` value included, and `path_prefixes` only when it is present and non-empty. Each scanner treats a passed value exactly as today's `list(...)` or `bool(...)` coercion did (`facade_sinks.py:46`, `:88-90`), so the scanner's own signature default (`facade_sinks.py:24-25`, `build_artifacts.py:16`, `:23`) stays the one default. Both gates call `scanner(..., **scanner_args(mandate.params or {}))`, and the two hand-written copies of each extraction (`cli_check_diff.py:128-166`, `posttooluse_gate.py:255-294`) are deleted (§4.9). The ratchet's arguments are built at one site only (`cli_check_diff.py:168-182`) and stay there.
- `python_pack.py:34-37`, `facade_sinks.py:50-53`, `fsm_guard.py:36-39` and `fail_loud_ratchet.py:23-26` call `acf.engine.parse_python` in place of their own parse-and-skip, each keeping its empty result (`[]`, or `0` in the ratchet) when it returns `None` (§4.9). `typescript_bridge.py` gains `TS_MANDATE_IDS = {"empty_catch": "fail-loud.empty-catch", "explicit_any": "no-shims.explicit-any"}`, and its `Finding` construction (`typescript_bridge.py:84-92`) takes `mandate_id=TS_MANDATE_IDS[item["detector"]]` instead of copying `item["mandate_id"]`. The lookup and the comparison run inside the existing `try` (`typescript_bridge.py:82-95`): an unknown `detector` raises `KeyError`, and a `mandate_id` that differs from the mapped value raises `ValueError`. The existing `except (KeyError, TypeError, ValueError)` (`:94-95`) already re-raises both as `DetectorPackError`. The Node rules still emit their literal (`emptyCatch.ts:23`, `explicitAny.ts:15`), so every TypeScript finding is checked against the one Python definition at run time, and a test pins the literals too (§4.7).
- `acf/detectors/__init__.py` defines `KNOWN_DETECTORS: Mapping[str, BuiltinDetector]` (a `MappingProxyType`), keyed by the detector-id constants and the `TS_MANDATE_IDS` keys. It is the one list of built-in detector ids: `PYTHON_AST_DETECTOR_IDS` (`python_pack.py:16`), `GUARD_DETECTOR_IDS`, `CONFIG_AST_DETECTOR_IDS` and `ALL_PYTHON_DETECTOR_IDS` (`detectors/__init__.py:11-28`) and `TS_DETECTOR_IDS` (`typescript_bridge.py:14`) are deleted (§4.9), and the module docstring (`detectors/__init__.py:1`, *"Portable detector id registries."*) becomes "Built-in detector contracts."

| Detector id | `mandate_id` constant | `call_sites` | Where it runs |
|---|---|---|---|
| `fail_loud_bare_except`, `no_shims_hasattr`, `posix_paths_str_serialization` | the three `python_pack` constants | `TIER1_CALL_SITES` | `scan_python_file` in both gates (`cli_check_diff.py:127`, `posttooluse_gate.py:254`) |
| `empty_catch`, `explicit_any` | `TS_MANDATE_IDS` | `TIER1_CALL_SITES` | `scan_typescript_file` in both gates (`cli_check_diff.py:153-156`, `posttooluse_gate.py:278-282`) |
| `forbid_facade_sink`, `fsm_transition_guard` | `facade_sinks` / `fsm_guard` constants | `TIER1_CALL_SITES` | both gates' `.py` branch (`cli_check_diff.py:128-150`, `posttooluse_gate.py:255-277`) |
| `no_build_artifacts` | `build_artifacts` constant | `TIER1_CALL_SITES` | both gates (`cli_check_diff.py:158-166`, `posttooluse_gate.py:284-294`) |
| `fail_loud_ratchet` | `fail_loud_ratchet` constant | `DIFF_CALL_SITES` | `acf-check-diff` only (`cli_check_diff.py:168-182`) |

- `cli_check_diff.py:25` becomes `from acf.detectors import KNOWN_DETECTORS`, so existing importers of `acf.cli_check_diff.KNOWN_DETECTORS` keep working. Its import of `LLM_PROMPT_IDS` (`:21`) stays and now feeds `load_mandates(..., llm_prompt_ids=LLM_PROMPT_IDS)` (§4.6). The hook imports `KNOWN_DETECTORS` from `acf.detectors`, not from `acf.cli_check_diff`, so it does not pull in `acf.judge`.

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
   - **Root.** Module-level `_ACTIVE_ROOT: Path | None = None` and `_MODULE_CACHE: dict[str, ModuleType] = {}`. On the first call the loader appends `str(root)` to `sys.path` (Decision 6) and sets `_ACTIVE_ROOT = root`. A later call with `root != _ACTIVE_ROOT` raises `AcfInputError(f"host detectors already loaded from {_ACTIVE_ROOT.as_posix()}; one host root per process")`. Host modules' intra-repo imports (such as `hm:scripts/ci/metadata_facade_guard.py:66`, `from scripts.ci.arch_compliance.facade_sinks import ...`) resolve against that root unless an earlier `sys.path` entry provides the same top-level name.
   - `module_path = file_under_root(root, rel_path)`; `UnknownDetectorError` if it is `None` or if the stat raises `OSError`.
   - **Module and callable.** The module is cached in `_MODULE_CACHE` by `rel_path`, under the name `"_acf_host_" + hashlib.sha256(rel_path.encode()).hexdigest()[:16]`. Executing the module and looking up the callable share one wrapped region:
     ```python
     mod = _MODULE_CACHE.get(rel_path)
     try:
         if mod is None:  # not cached
             spec = importlib.util.spec_from_file_location(name, module_path)
             if spec is None or spec.loader is None:
                 raise ImportError(f"no loader for {rel_path!r}")
             mod = importlib.util.module_from_spec(spec)
             sys.modules[name] = mod
             spec.loader.exec_module(mod)
             _MODULE_CACHE[rel_path] = mod
         fn = getattr(mod, attr, None)
     except BaseException as exc:  # fail-loud.bare-except-ok: <reason>
         if isinstance(exc, KeyboardInterrupt):
             raise
         if _MODULE_CACHE.get(rel_path) is not mod:
             sys.modules.pop(name, None)
         raise UnknownDetectorError(
             f"failed to load host detector {detector!r} from {rel_path!r}: {_describe(exc)}"
         ) from exc
     if not callable(fn):
         raise UnknownDetectorError(f"host detector {detector!r}: {attr!r} is not a callable in {rel_path!r}")
     ```
     The module is registered in `sys.modules` before `exec_module`, which `dataclasses` needs to resolve string annotations, and removed if `exec_module` raises. A module-level `__getattr__` that raises during the lookup is wrapped as well.
4. **`_call_host(fn, mandate, where, *args, **kwargs) -> list[HostHit]`:** the one wrapped region for calling a host callable and consuming its result. Module execution and callable lookup are wrapped separately, in `load_host_detector` (item 3), and raise `UnknownDetectorError` instead.
   ```python
   try:
       raw = fn(*args, **kwargs)
       if raw is None or isinstance(raw, (str, bytes)):
           raise TypeError(f"returned {type(raw).__name__}, not an iterable of HostHit")
       items = list(raw)
       hits = [_revalidate(item) for item in items]
   except BaseException as exc:  # fail-loud.bare-except-ok: <reason>
       if isinstance(exc, KeyboardInterrupt):
           raise
       raise DetectorPackError(
           f"host detector {mandate.detector!r} for mandate {mandate.id!r} failed {where}: {_describe(exc)}"
       ) from exc
   ```
   ```python
   def _revalidate(item: object) -> HostHit:
       if type(item) is not HostHit:
           raise TypeError(f"yielded {type(item).__name__}, not HostHit")
       fields = dict(item.__dict__)
       if (type(fields.get("path")) is not str or type(fields.get("line")) is not int
               or type(fields.get("message")) is not str):
           raise TypeError("HostHit fields must be exactly str, int and str")
       return HostHit.model_validate(fields)
   ```
   Consuming the result and rebuilding each item inside the `try` means three things become `DetectorPackError`: an exception raised while a generator runs (a `HostHit` `ValidationError` included); an item whose type is not exactly `HostHit`, a host subclass whose properties could run host code included; and a `HostHit` built with `model_construct` or altered after construction whose fields are not exactly `str`, `int` and `str` or do not validate. The exact-type check comes first because pydantic's default (lax) validation would coerce `b"a.py"` or `"5"`; a `HostHit` built normally always holds exact types, since validation turns a `str` subclass into a plain `str`. The result is consumed to the end with `list(raw)` before any item is rebuilt, so a generator finishes (or raises) inside the `try` rather than being abandoned mid-iteration and finalised later. Every hit leaving `_call_host` is a fresh, validated `HostHit` holding plain `str` and `int` values, so `_to_findings` runs no host code. Both handlers catch every exception except `KeyboardInterrupt`, which they re-raise, so a host `SystemExit`, `GeneratorExit` or custom `BaseException` subclass is wrapped too. Both handlers format the host's exception through one helper, because `str(exc)` runs host code after the `try` has exited. That code can raise: `BaseException.__str__` returns `str(args[0])` for a one-argument exception, so an exception carrying a host object renders through that object's `__str__`. The origin host's guards define such objects; `hm:scripts/ci/genre_conditional_guard.py:33-40` declares a non-frozen dataclass `Finding` whose `__str__` calls `self.line_text.strip()`, and a dataclass does not enforce its annotations, so `ValueError(Finding("a.md", 3, None, "..."))` is an exception whose `str()` raises `AttributeError`. A test pins that case (§4.7):
   ```python
   def _describe(exc: BaseException) -> str:
       try:
           return f"{type(exc).__name__}: {exc}"
       except BaseException as err:  # fail-loud.bare-except-ok: a host exception whose __str__ or type name raises is still reported
           if isinstance(err, KeyboardInterrupt):
               raise
           return "host exception (message unavailable)"
   ```
5. **`_to_findings(hits: list[HostHit], mandate: Mandate, *, expected_path: str | None) -> list[Finding]`:** receives only hits rebuilt by `_call_host` (item 4), and refuses (`DetectorPackError`), for `ast` rows, any hit whose `path != expected_path`. Each hit becomes `Finding(mandate_id=mandate.id, severity=Severity(mandate.severity), path=hit.path, line=hit.line, message=hit.message, detector=mandate.detector, detection=mandate.detection)`. `severity` is filled only because `Finding` requires it; `apply_registry` stays its owner and sets it from the row for every Tier-1 finding (`plugins/arch-compliance/python/acf/enforcement.py:52`). The `ast` path check refuses rather than making a wrong path unrepresentable, because one `HostHit` type serves both callable kinds, and a path-less `ast` hit would be a second type carrying the same facts.
6. **`scan_host_ast_file(repo_root, text, path, added_lines, registry, *, language, call_sites) -> list[Finding]`:**
   - `mandates = [m for m in registry.active(call_sites, detection="ast") if is_host_detector_ref(m.detector) and m.languages in {language, "both"}]`; returns `[]` if none.
   - For `language == "python"`: `tree = parse_python(text)` once, shared by every host `ast` detector on the file; when it is `None` the runner returns `[]`, the skip convention `parse_python` carries for every scanner (§4.1). For TypeScript, `tree=None`. The contract says host `ast` detectors read the tree and do not change it; a detector that needs to transform it works on its own `copy.deepcopy(tree)`.
   - Each callable runs through `_call_host(fn, mandate, f"on {path!r}", text, path, added_lines, tree=tree, params=mandate.params)`, then `_to_findings(..., expected_path=path)`.
7. **`scan_host_guards(repo_root, changed_files, registry, file_lines, *, call_sites) -> list[Finding]`:** selects `[m for m in registry.active(call_sites, detection="guard") if is_host_detector_ref(m.detector)]` and runs each through `_call_host(fn, mandate, "as a guard", repo_root.resolve(), tuple(changed_files), params=mandate.params)`, then `_to_findings(..., expected_path=None)`. For the exemption check (§4.5), it adds to the gate's `file_lines` mapping the lines of each file its findings name that the mapping does not already hold; entries the gate already read are kept. Each such file is read once, inside one `try`: `candidate = file_under_root(repo_root, hit.path)`; when it is `None` the path maps to `[]`, which leaves the finding in place. That covers a missing file, a directory, a path outside the root, and a symlink loop on Python 3.11 through 3.13 (3.11 and 3.12 through `resolve_under_root`'s `None`; on 3.13, `is_file()` returns `False` for a looping path). Otherwise the lines are `candidate.read_text(encoding="utf-8", errors="replace").splitlines()`. An `OSError` from the stat or the read (for example, permission denied on a parent directory, which `is_file()` re-raises) raises `DetectorPackError` naming the path and the mandate. The read sits inside each gate's scan `try`, so that error reaches the gate's handler. This precedence rule (gate-read lines win; guard-read lines fill gaps) lives here once, not in each gate.

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


def make_line_lookup(file_lines: Mapping[str, list[str]]) -> LineLookup:
    def _lookup(posix: str, line: int) -> str:
        lines = file_lines.get(posix)
        if not lines or not (0 < line <= len(lines)):
            return ""
        return lines[line - 1]
    return _lookup
```

`make_line_lookup` is the two gates' closures (`cli_check_diff.py:76-80`, `posttooluse_gate.py:119-123`) moved into `acf.enforcement` unchanged; it reads no file. Lines for files a host guard flags enter `file_lines` from `scan_host_guards` (§4.4 item 7), inside each gate's scan `try`. So `apply_registry` does no I/O and raises nothing new. Exemption follows the file, not the detector, as it does today: any finding on a file whose lines the gate holds honours its row's token on that line. Today that already covers built-in line-1 findings (`plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:135`, `plugins/arch-compliance/python/acf/detectors/build_artifacts.py:34`) on a changed code file, such as a staged `dist/x.py`, whenever the finding's path equals the file's key (the build-artifact guard strips leading `.` and `/` characters from the paths it reports, `build_artifacts.py:27`, so a path such as `".next/x.py"` does not match and stays non-exemptable, as today). After this design it also covers a file a host guard flagged. A built-in finding on any other file still gets `""` and stays non-exemptable. The guard read uses `errors="replace"` because an exemption token is ASCII: a stray undecodable byte elsewhere on the line must neither crash the gate nor hide the token.

### 4.6 Wiring

1. **`plugins/arch-compliance/python/acf/cli_check_diff.py`:**
   - The argument parser (`:29-61`) adds `--call-site` with `required=True` and `choices=sorted(DIFF_CALL_SITES)`; `sites = frozenset({args.call_site})` is passed to `_scan_changed` (`:71`). Inside the `try` at `:69-74`, after `load_mandates`, a site with no active `ast` or `guard` row raises `AcfInputError(f"call site {args.call_site!r} selects no active ast or guard mandate; refusing to report a clean run")`.
   - `:70`: `load_mandates(mandates_path, known_detectors=KNOWN_DETECTORS, llm_prompt_ids=LLM_PROMPT_IDS, repo_root=repo)`.
   - `:76-82`: `findings = apply_registry(raw_findings, registry, make_line_lookup(file_lines), call_sites=sites)`.
   - `_active_mandates` (`:94-99`) is deleted; its four call sites (`:112`, `:113`, `:158`, `:168`) become `registry.active(sites, detector=...)`.
   - The facade, FSM and build-artifact calls (`:128-150`, `:158-166`) pass `**facade_sink_args(params)`, `**fsm_guard_args(params)` and `**build_artifact_args(params)` in place of their inline extraction (§4.3).
   - `.py` branch, after `scan_fsm_writes` (`:140-150`): `findings.extend(scan_host_ast_file(repo, text, posix, lines, registry, language="python", call_sites=sites))`.
   - `.ts`/`.tsx` branch (`:151-156`): bind `text = abs_path.read_text(encoding="utf-8")` and use it for `file_lines[posix]`, then `findings.extend(scan_host_ast_file(..., language="typescript", call_sites=sites))`.
   - After the ratchet loop (`:168-182`): `findings.extend(scan_host_guards(repo, changed, registry, file_lines, call_sites=sites))`.
   - The `except` tuple at `:72` already lists `AcfInputError`, `UnknownDetectorError` and `DetectorPackError` around both load and scan.
2. **`plugins/arch-compliance/hooks/posttooluse_gate.py`:**
   - Deferred imports (`:91-104`) add `KNOWN_DETECTORS` (from `acf.detectors`), `HOOK_CALL_SITES`, `make_line_lookup`, `UnknownDetectorError`, `scan_host_ast_file` and `scan_host_guards`.
   - `:106-110`: `load_mandates(mandates_path, known_detectors=KNOWN_DETECTORS, repo_root=repo)` inside `except (AcfInputError, UnknownDetectorError)`.
   - `:113-117`: the scan `except` becomes `(AcfInputError, DetectorPackError, UnknownDetectorError)`, matching `acf-check-diff`.
   - `:119-125`: `findings = apply_registry(raw_findings, registry, make_line_lookup(file_lines), call_sites=HOOK_CALL_SITES)`.
   - `_scan_paths`: the three inline filters (`:229-236`, `:284-286`) become `registry.active(HOOK_CALL_SITES, detector=...)`, and the facade, FSM and build-artifact calls (`:255-277`, `:287-294`) use the three `*_args` functions, as in `acf-check-diff` (`:284-294` for the build-artifact loop). The `.py` and TypeScript branches call `scan_host_ast_file(repo, text, rel, None, registry, language=..., call_sites=HOOK_CALL_SITES)`, and after the build-artifact loop (`:284-294`) `findings.extend(scan_host_guards(repo, rel_paths, registry, file_lines, call_sites=HOOK_CALL_SITES))` runs.
   - `_collect_paths` (`:200-209`): `abs_path = p.resolve() if p.is_absolute() else (repo / p).resolve()` (`:203-204`) becomes `abs_path = file_under_root(repo, raw)`, and a path for which it returns `None` is skipped. The dedupe by `abs_path.as_posix()` (`:205-208`) stays. So `_scan_paths` receives only existing regular files inside the repository. Its `is_file()` skip (`:239`) and its `try`/`except ValueError` (`:242-245`) are deleted, and `rel = abs_path.relative_to(repo).as_posix()` cannot fail (`resolve_repo` returns a resolved path, `plugins/arch-compliance/python/acf/repo.py:41-44`). An `OSError` from the stat propagates, as `abs_path.is_file()` at `:239` lets it propagate today. Consequence, accepted: an edited file outside the repository is no longer scanned. Today it is scanned under its absolute POSIX path, and the build-artifact guard sees that absolute string (`:242-246`). Findings on files outside the host's repository are not that repository's mandates. `git grep -n "outside\|out_of_repo\|absolute" -- plugins/arch-compliance/tests/test_hooks.py` prints nothing, so no test exercises the dropped case. §4.7 adds one.
   - Docstring `:12` is reworded to state that the hook runs active rows declaring `hook` or `posttooluse`, including host detectors, which receive every edited in-repo path. Line `:11` stays verbatim: `plugins/arch-compliance/tests/test_repo_paths.py:47-48` pins its text.

### 4.7 Tests

| File | Change |
|---|---|
| `plugins/arch-compliance/tests/test_engine_paths.py` (exists; extended) | Its current cases are kept. Added: `validate_posix_rel_path` accepts `"scripts/ci/guard.py"`, `"a/b/c.py"`, `"guard.py"`, and rejects `""`, `" a.py"`, a backslash path, `"/a.py"`, `"a/"`, `"C:/a.py"`, `"C:a.py"`, `"a//b.py"`, `"./a.py"`, `"a/./b.py"`, `"../a.py"` and `"a/../b.py"`; `looks_absolute` and `resolve_under_root` get one positive and one negative case each, and `resolve_under_root` returns `None` when `Path.resolve` raises `RuntimeError` (monkeypatched). `file_under_root` returns the path for a file, `None` for a directory or a missing path, and propagates an `OSError` from `is_file` (monkeypatched); `parse_python` returns a module, and `None` on a `SyntaxError`. |
| `plugins/arch-compliance/tests/conftest.py` (new) | Fixture `fresh_host_loader`: monkeypatches `acf.detectors.host._ACTIVE_ROOT` to `None` and `_MODULE_CACHE` to `{}`, snapshots `sys.path` and the keys of `sys.modules`, and afterwards restores `sys.path` and deletes the `sys.modules` keys added during the test that name a host module: a `_acf_host_` name, or a module whose `__file__` lies under the root the loader served. Third-party and plugin modules first imported during a test stay loaded. |
| `plugins/arch-compliance/tests/test_host_detectors.py` (new) | All cases use `fresh_host_loader`. Loader: imports a module that imports a sibling package from the root and defines a `@dataclass(frozen=True)` class under `from __future__ import annotations`; caches across two callables in one file; appends the root to the end of `sys.path`; raises `UnknownDetectorError` on a missing file, an import failure, a module that calls `sys.exit(0)`, a missing callable, a module whose `__getattr__` raises `RuntimeError`, and a module file whose stat raises `PermissionError` (monkeypatched); raises `AcfInputError` for a second root. Runners: one `ast.parse` for two host `ast` rows on a file (spy count `== 1`); filters by `languages` and `call_sites`; refuses a non-`HostHit` item, an instance of a `HostHit` subclass whose property raises, `HostHit.model_construct` hits whose `path` is `b"a.py"` or `5`, or whose `line` is `"5"` or `True`, a mismatched `ast` path and a `str` return; wraps a raised `AcfInputError`, a generator that raises mid-iteration, a generator that yields an invalid `HostHit`, `sys.exit(0)`, an exception whose `__str__` raises, `ValueError(obj)` where `obj` is a dataclass like `hm:scripts/ci/genre_conditional_guard.py:33-40` with `line_text=None`, one whose `__str__` raises `SystemExit`, a generator that yields one valid hit and then an invalid item, and a callable that raises a custom `BaseException` subclass, as `DetectorPackError`; `KeyboardInterrupt` propagates. `scan_host_guards` adds the lines of a flagged file to `file_lines`, keeps an entry the gate already holds, adds `[]` for a flagged path that does not exist and for a flagged directory, and raises `DetectorPackError` when reading a flagged file raises `OSError` (monkeypatched `Path.read_text`). |
| `plugins/arch-compliance/tests/test_builtin_detectors.py` (new) | No LLM prompt id is a key of `KNOWN_DETECTORS`; `facade_sink_args({})` returns `{"target_literal_re": ""}`, `fsm_guard_args({})` returns `state_field` and `validator_name` as `""`, `build_artifact_args({})` and `build_artifact_args({"path_prefixes": []})` return `{}`, and set params pass through; each `TS_MANDATE_IDS` value appears as `mandate_id: "<value>"` in its rule file under `plugins/arch-compliance/detectors/typescript/src/rules/`; `fail_loud_ratchet` maps to `DIFF_CALL_SITES` and every other id to `TIER1_CALL_SITES`; every row of the `README.md` detector table names a key of `KNOWN_DETECTORS`, its mandate id is that key's `mandate_id`, and every Python key appears in the table. **Contract against dispatch:** for each gate (`acf-check-diff` on a temporary git repository, in process, once with `--call-site ci` and once with `--call-site precommit`; the PostToolUse hook in a subprocess with `.acf/enabled`), a fixture tree that triggers every built-in detector and a registry with one active row per detector whose contract includes that gate's call sites, each row declaring only those sites. The test asserts that the gate's findings carry exactly the `mandate_id` of every such detector. A detector the table says runs at a gate but which that gate does not dispatch fails this test. The opposite drift (a gate dispatching a detector the table excludes) cannot attach a finding to any loaded row, because `_check_builtin` refuses a row declaring that site, so it over-refuses and never silently drops. |
| `plugins/arch-compliance/tests/test_typescript_pack.py` | `:6` and `:14` assert on `TS_MANDATE_IDS` keys instead of the deleted `TS_DETECTOR_IDS`. A scanner item whose `mandate_id` differs from `TS_MANDATE_IDS[detector]`, and one whose `detector` is not a key, raise `DetectorPackError` (the subprocess result is monkeypatched). |
| `plugins/arch-compliance/tests/test_registry.py` | `:30` passes `known_detectors=KNOWN_DETECTORS`. A malformed host reference raises `AcfInputError` with and without `known_detectors` and for an `unenforced` row; an active `ast` row with only `[audit]` and an active host `ast` row with `languages: none` raise `AcfInputError` without `known_detectors`. With `known_detectors`: an active `partial` unknown built-in raises `UnknownDetectorError`; an `ast` row naming an LLM prompt id raises `UnknownDetectorError`; a `fail_loud_bare_except` row with another `id`, and a `fail_loud_ratchet` row declaring `hook`, raise `AcfInputError`; a host row raises `AcfInputError` without `repo_root` and `UnknownDetectorError` for a missing file; an existing host file loads, and a module that raises at import time is not imported by `load_mandates`. With `llm_prompt_ids=LLM_PROMPT_IDS`: an active `llm` row naming `llm_not_a_prompt` raises `UnknownDetectorError`, and an `unenforced` one loads. A row with `call_sites: [ci, hooks]` is refused at row construction. |
| `plugins/arch-compliance/tests/test_portable_guards.py` | `scan_ratchet` with `baseline_path="../x.json"`, an absolute path outside the root, or a missing file, and `scan_tree` with `roots=["../x"]` or a `roots` entry naming no existing directory (`roots=["missing"]`), raise `DetectorPackError`; the existing `scan_tree(tmp_path, roots=["pkg"], ...)` case (`:107`) passes unchanged. |
| `plugins/arch-compliance/tests/test_enforcement.py` | Every `apply_registry` call (`:54`, `:60`, `:66`, `:72`, `:84`, `:94`, `:104`, `:110`, `:125`, `:130`) passes `call_sites=`. A new case drops a finding whose row lacks the given call site. `make_line_lookup` returns `""` for a path not in its mapping. |
| `plugins/arch-compliance/tests/test_hooks.py` | `:199-218` keeps its WARN-context coverage by setting the copied fixture's `no-shims.hasattr` row to `call_sites: [ci, hook]`. A new case asserts the hook does not report a `[ci]`-only row. New cases (the hook runs in a subprocess, `:22-29`): exit `0` without importing a host module when `.acf/enabled` is absent (the module raises at import); exit `1` on an unknown detector when enabled; host `ast` and `guard` rows declaring `hook` run, `[ci]`-only host guards do not; an edited `.py` file outside the repository (a second `tmp_path` directory, passed by absolute path) yields no finding and no host call, while an in-repo file passed by absolute path is scanned under its relative key. |
| `plugins/arch-compliance/tests/test_diff_cli.py` | `test_unenforced_mandate_does_not_gate` (`:102-108`) would hit the new refusal, since its registry's only row is unenforced; it adds an active `no-shims.hasattr` row (`detector: no_shims_hasattr`, `call_sites: [ci]`), which does not fire on the staged `"bad.py"` (it contains no `hasattr`), so the call site selects a row and the test still asserts that the unenforced row does not gate (exit `0`). Every `main([...])` call (`:48`, `:61`, `:98`, `:107`, `:124`, `:153`, `:154`, `:173`, `:178`, `:191`) passes `--call-site`. New cases: a `[ci]`-only row is reported with `--call-site ci` and not with `--call-site precommit`; omitting `--call-site` exits `2` (asserted with `pytest.raises(SystemExit)`, since `main` runs in process); a registry with no active row for the given site exits `1` with the refusal message. New cases use `fresh_host_loader`: host `ast` and `guard` rows declaring `ci` run and exit `1` on `BLOCK`; an exemption token on a non-code file flagged by a host guard is honoured. |
| `plugins/arch-compliance/tests/test_adr_citations.py` | A drive-relative citation (`"C:a/b.py"`) classifies `external`. Existing cases pass unchanged. |
| `plugins/arch-compliance/tests/test_acf_mandate_skill.py` | Its cases are unchanged; it runs the acf-mandate `## Validate` snippet (`:20-25`), so the rewritten snippet (§4.8) keeps the fenced `bash` / `python -c "..."` shape it extracts. The module docstring at `:2` (*"loads the registry with the package's detector union"*) is reworded to "the built-in detector contracts and LLM prompt ids". |
| `tests/test_self_host.py` | `:23` passes `repo_root=ROOT` and `llm_prompt_ids=LLM_PROMPT_IDS`. `:40` checks each manual row with `file_under_root(ROOT, m.detector)` (adding the escape check) instead of `(ROOT / m.detector).is_file()`. The module docstring at `:5` (*"`KNOWN_DETECTORS` the one detector union"*) is reworded to "the built-in detector contracts". |

### 4.8 Prose and version

| Site | Change |
|---|---|
| `config/architecture/ARCHITECTURE.md` | New `## Host detectors and call sites` section: the reference syntax, the `HostHit` contract, the call-site rule and the built-in contracts (Decisions 2 and 3), and the trust boundary (Decision 7). It ends `No row: enforced by plugins/arch-compliance/tests/test_host_detectors.py, test_builtin_detectors.py, test_registry.py, test_hooks.py and test_diff_cli.py.` |
| `config/architecture/ARCHITECTURE.md:9-11` | The preamble's "run the registry's detectors on changed `.py`, `.ts` and `.tsx` files" adds that host guards see every changed path and that rows run where their `call_sites` say. |
| `plugins/arch-compliance/skills/acf-mandate/SKILL.md` | `:10`, `:18` ("known detector union" becomes "the built-in contracts and LLM prompt ids"), `:41`, `:43` (call-site vocabulary and its effect), `:55`, `:58`, `:68`, `:74`, `:88-112` (snippet uses `repo = resolve_repo(None)` and `load_mandates(repo / MANDATES_REL, known_detectors=KNOWN_DETECTORS, llm_prompt_ids=LLM_PROMPT_IDS, repo_root=repo)`, importing `LLM_PROMPT_IDS` from `acf.judge`; the detector union text at `:106-112` becomes "the built-in contracts in `acf.detectors.KNOWN_DETECTORS`, and `acf.judge.LLM_PROMPT_IDS` for `llm` rows"), `:116`, `:120`, `:122`, `:138`. `:56` and `:121` stay: the prompt-id rule they state is now enforced (Decision 4). `:58`, `:68` and `:138` drop `partial` from the advice for a detector or prompt that does not exist yet and name `unenforced` (Decision 3). |
| `plugins/arch-compliance/skills/acf-mandate/SKILL.md` (call-site advice) | `:59` and `:79`: an active `ast`/`guard` row must keep at least one Tier-1 site at which its detector runs, and a built-in row's `id` is its detector's mandate id; deprecate with `status: unenforced`. |
| `plugins/arch-compliance/skills/acf-setup/SKILL.md` | `## Step 7` (`:140-151`): `.acf/enabled` is the opt-in for the automatic hooks, host detectors included; `:150` adds that committing `.acf/` opts every clone into running host detectors on edit. `:159`: the PostToolUse row covers host detectors and edited non-code paths. |
| `README.md` | `:62`, `:76` and `:106`: the gates run active rows by `call_sites` (`:76` adds it to the status rule), and host guards see every changed path. The detector table (`:66-74`) gains a call-sites column (`fail_loud_ratchet`: `ci`/`precommit` only) and is pinned by `plugins/arch-compliance/tests/test_builtin_detectors.py`. `:108` unchanged. |
| `--call-site` at shipped and documented invocations. Recipe: `git grep -nE "acf-check-diff|acf\.cli_check_diff" -- ':!docs/reviews' ':!docs/plans' ':!docs/design/HOST_DETECTOR_EXTENSION_POINT.md'`. Each hit is a command line or instruction listed here, a past-run record named here, or a mention of the tool's name that runs nothing (for example `README.md:62`, `docs/guides/SUPERPOWERS_COMPLEMENT.md:40`, `:61`, `:70`, and the `KNOWN_DETECTORS` imports) | `.github/workflows/ci.yml:40`, `README.md:58`, `plugins/arch-compliance/skills/acf-setup/SKILL.md:206`, `CLAUDE.md:36` and `docs/guides/SUPERPOWERS_COMPLEMENT.md:83` add `--call-site ci`; `README.md:57`, `plugins/arch-compliance/skills/acf-setup/SKILL.md:184`, `:193`, the Step 9 smoke check (`:217`, `:219`) and `docs/guides/SUPERPOWERS_COMPLEMENT.md:82` add `--call-site precommit`; the CI fallback comment (`:207`) adds `--call-site ci`; the prose instructions `plugins/arch-compliance/skills/acf-setup/SKILL.md:24`, `:250` and `plugins/arch-compliance/skills/acf-mandate/SKILL.md:131` name the flag; and the smoke check's success criteria (`:222-225`) add that an exit `2` usage error or a "selects no active" refusal means the invocation or the registry needs fixing. The verification steps and receipts of approved specs (`docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md:313`, `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:253`, `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:223`, `:531`, `:624-625`) record past runs and are not edited. `README.md` and `plugins/arch-compliance/skills/acf-setup/SKILL.md` gain an upgrade note: a host installed before this release adds `precommit` to each row it wants checked in pre-commit, or its pre-commit run is refused; and it sets to `unenforced` any `partial` row whose detector or prompt does not exist yet, or its registry is refused at load (Decision 3). `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:454`, which quotes the CI line, is updated to match. Each says that `--call-site` selects the rows that run. |
| `config/architecture/ARCHITECTURE.md` `## Fail-loud ratchet` (`:72-73`) | *"Enable the mandate and commit a … baseline"* adds the constraints this design enforces: the row runs at `ci` and `precommit` only (`acf-check-diff`; a row declaring `hook` is refused at load), and `params.baseline` and each `params.roots` entry must name a path inside the repository, each root an existing directory (`DetectorPackError` otherwise, §4.9). |
| `config/architecture/ARCHITECTURE.md` `## High-frequency misses` (`:226-228`) | *"`acf.cli_check_diff.KNOWN_DETECTORS`"* becomes `acf.detectors.KNOWN_DETECTORS`, the definition's home (Decision 3); `acf.cli_check_diff` keeps re-exporting it. |
| `plugins/arch-compliance/python/acf/enforcement.py` module docstring (`:6-8`) | The drop rules add "findings whose row does not run at the gate's call sites are dropped". |
| `docs/guides/SUPERPOWERS_COMPLEMENT.md:87` | The gating rule adds that a row gates only at the call sites it declares (a `[ci]`-only row is not reported by the PostToolUse hook). |
| `docs/design/ADR_GATE_HOST_CONTRACT.md:302-303` | The citation of `citations.py:49` / `:74` as owners of the repo-relative test now names `acf.engine.looks_absolute` and `resolve_under_root`. |
| `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md` | `:104`: the call-site vocabulary and the Tier-1 sets. `:161`: the PostToolUse row runs rows declaring `hook`/`posttooluse`, host guards on every edited in-repo path, and edited files outside the repository are not scanned. `:111`: drift covers the built-in contracts and resolvable host references. `:184`: *"Unknown built-in detector id, a built-in row whose id or call sites disagree with its detector, an unresolvable host reference, or no Tier-1 call site on an active (enforced or partial) `ast` or `guard` row → registry validation fail."* |
| `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` | `:425` (the snippet loads with `KNOWN_DETECTORS`) and `:500` (the "detector union" row, *"All three import `KNOWN_DETECTORS`; one definition"*): the snippet and the tests load with the built-in contracts, and the snippet also with `LLM_PROMPT_IDS`. `:421-424`: the detector-id sets it kept are deleted too; `KNOWN_DETECTORS` is the one list. `:84` and `:418-420`: `KNOWN_DETECTORS` is defined in `acf.detectors` and re-exported by `acf.cli_check_diff`; the stated reason for its home (`acf.registry` cannot import `acf.judge`) still holds, since `acf.detectors` imports `acf.registry` and neither imports `acf.judge`. `:266-268`: as the doctrine preamble change above. `:373-376`: PostToolUse runs rows declaring `hook`/`posttooluse` and passes every edited in-repo path to host guards. `:389-393`: the `no-shims.hasattr` rows (`[ci]` only) are no longer reported by the hook; the census text says the hook reports the two `explicit-any` WARN rows. |
| `pyproject.toml:3`, `plugins/arch-compliance/.claude-plugin/plugin.json:3` | `"0.2.2"` → `"0.2.3"`. |

### 4.9 What this design deletes, and what each switch changes

Per Decision 8. Each row's recipe is re-run before the deletion task; the counts below are as at `a338cad`.

| Deleted | Replaced by | Live references (recipe → result) | Behaviour change at the old caller |
|---|---|---|---|
| `citations._looks_absolute`, `_escapes_repo` (`plugins/arch-compliance/python/acf/adr/citations.py:49-51`, `:74-76`) | `acf.engine.looks_absolute`, `resolve_under_root` | `git grep -n "_looks_absolute\|_escapes_repo" -- '*.py'` → `citations.py:49`, `:74`, `:161`, `:163` | Drive-relative citations classify `external`; symlink loops on 3.11/3.12 classify `unresolved` (§4.1). |
| `PYTHON_AST_DETECTOR_IDS`, `GUARD_DETECTOR_IDS`, `CONFIG_AST_DETECTOR_IDS`, `ALL_PYTHON_DETECTOR_IDS`, `TS_DETECTOR_IDS` | `KNOWN_DETECTORS` keys | `git grep -n "_DETECTOR_IDS" -- plugins tests` → `cli_check_diff.py:10`, `:16`, `:25`; `detectors/__init__.py:9`, `:11`, `:21`, `:28`, `:31`, `:32`, `:33`, `:34`; `python_pack.py:16`; `typescript_bridge.py:14`; `tests/test_typescript_pack.py:6`, `:14` | None at run time; one test assertion changes (§4.7). |
| Parse-and-skip in `python_pack.py:34-37`, `facade_sinks.py:50-53`, `fsm_guard.py:36-39`, `fail_loud_ratchet.py:23-26` | `acf.engine.parse_python` | `git grep -n "ast.parse(text)" -- plugins/arch-compliance/python` → `facade_sinks.py:51`, `fail_loud_ratchet.py:24`, `fsm_guard.py:37`, `python_pack.py:35` | None: each keeps its empty result. |
| `(ROOT / m.detector).is_file()` in `tests/test_self_host.py:40` | `acf.engine.file_under_root` | the one line | The test also refuses a manual-row path that escapes the root. |
| The PostToolUse hook's own containment: the `Path.is_absolute()` join (`posttooluse_gate.py:203-204`), the `is_file()` skip (`:239`) and the `relative_to(repo)` / `except ValueError` fallback (`:242-245`) | `file_under_root(repo, raw)` in `_collect_paths` (§4.6) | `git grep -n "is_absolute()\|relative_to(" -- plugins/arch-compliance/hooks plugins/arch-compliance/python` → `posttooluse_gate.py:204`, `:243`; `citations.py:76` (deleted, row 1); `fail_loud_ratchet.py:60` (the walk's conversion, kept without its `except`), `:123` (deleted, last row) | An edited file outside the repository is no longer scanned (§4.6); in-repo files are scanned as today. |
| The two gates' `_line_lookup` closures (`cli_check_diff.py:76-80`, `posttooluse_gate.py:119-123`) | `make_line_lookup` | `git grep -n "def _line_lookup" -- '*.py'` → those two lines | None (§4.5). |
| `_active_mandates` and the hook's inline row filters | `MandateRegistry.active` | Appendix, "Active-row filters" | Rows run only at their declared call sites (Decision 2). |
| Inline params extraction for the facade, FSM and build-artifact scanners, in both gates (`cli_check_diff.py:128-166`, `posttooluse_gate.py:255-294`) | `facade_sink_args`, `fsm_guard_args`, `build_artifact_args` | `git grep -n "params.get(\"target_literal_re\"\|params.get(\"state_field\"\|params.get(\"path_prefixes\")" -- '*.py'` → `cli_check_diff.py:135`, `:147`, `:160`; `posttooluse_gate.py:262`, `:274`, `:288` | None: same defaults (§4.7 pins them). |
| The ratchet's hand-rolled joins of `params.baseline` and `params.roots` (`fail_loud_ratchet.py:46`, `:122-124`), and `load_baseline`'s own `is_file()` check (`:78`) | `file_under_root` for `baseline`, `resolve_under_root` plus `is_dir()` for each `roots` entry, replacing `scan_tree`'s silent `if not search.exists(): continue` (`:56-57`); the walk filter's `except ValueError: continue` (`:59-62`), which can no longer fire once each root is contained, is deleted; `None`, a `roots` entry that is not an existing directory, or an `OSError` from the stat raises `DetectorPackError` naming the parameter | `git grep -n "repo_root / baseline_file\|root / r for r" -- '*.py'` → `fail_loud_ratchet.py:124`, `:46` | A `baseline` or `roots` entry that escapes the root (an absolute path outside it included) or loops is refused instead of followed, and a misspelled `roots` entry is refused instead of counting zero; a `roots` entry that is an in-repo symlink to another in-repo directory now reports its files under the target's path (`target/a.py`, not `link/a.py`), so baseline keys written under the link path no longer match; an absolute path inside the root is still accepted, as today. Shipped values: `baseline: config/architecture/fail_loud_ratchet.json`, `roots: ["."]` (Appendix). |

---

## 5. Relationships and shape fit

### 5.1 Documents

| Document | Relationship | Disposition |
|---|---|---|
| `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md` | `ADJACENT` | Parent architecture; `:102`, `:123`, `:125` call for this extension point; `:104`, `:111`, `:161` and `:184` are updated (§4.8). |
| `docs/design/ADR_GATE_HOST_CONTRACT.md` | `ADJACENT` | Owns `acf.adr`; `acf/adr/citations.py` changes only to consume the shared engine helpers (§4.1, §4.9), and `acf/adr/host.py` is unchanged (§5.2). Its `:302-303` is updated (§4.8). |
| `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` | `ADJACENT` | `tests/test_self_host.py:23`, `:40` change (§4.7); its `KNOWN_DETECTORS` placement (`:84`, `:418-420`), preamble restatement (`:266-268`), PostToolUse description and census (`:373-376`, `:389-393`) are updated (§4.8). |
| `docs/design/LLM_JUDGE_PROVIDER_NEUTRAL.md` | `DISJOINT` | Tier-2 judge; `cli_check_llm.py` is unchanged. |
| `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md` | `DISJOINT` | Housekeeping skill. |

### 5.2 Elements

| New / changed element | Existing site | Relationship and resolution |
|---|---|---|
| `looks_absolute`, `resolve_under_root` | `plugins/arch-compliance/python/acf/adr/citations.py:49-51`, `:74-76` | `SUBSUMED`: citations' private copies are deleted and its two call sites use the engine helpers. `load_host_detector`, `load_mandates`, `scan_host_guards` and `tests/test_self_host.py:40` use `resolve_under_root` too. |
| `resolve_under_root` (through `file_under_root`) | the PostToolUse hook's `Path.is_absolute()` join and `relative_to(repo)` / `except ValueError` (`plugins/arch-compliance/hooks/posttooluse_gate.py:203-204`, `:242-245`); the ratchet's walk filter `except ValueError: continue` (`plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:59-62`) | `SUBSUMED`: each decides whether a path lies inside the root, by hand. The hook calls `file_under_root` and the ratchet contains its roots with `resolve_under_root`; both `except ValueError` branches and the hook's absolute test are deleted (§4.9). Each keeps only `relative_to(...).as_posix()`, the conversion of an already-contained `Path` to its key, which cannot fail there. |
| `resolve_under_root` | the ratchet's `params.baseline` and `params.roots` joins (`plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:46`, `:122-124`) | `SUBSUMED`: the same job (registry path string to a location under the root) done by hand with `Path.is_absolute()` and no containment; the ratchet switches to `resolve_under_root` (§4.9). |
| `validate_posix_rel_path` | `AdrHostConfig.runs_dir` and `ledger_path` (`plugins/arch-compliance/python/acf/adr/host.py:24-25`), checked only by `PosixStr` | `ADJACENT`, by an approved decision: the ADR gate contract declines to refuse absolute or `..` values there, *"That is a visible host choice, not a state the gate must prevent"* (`docs/design/ADR_GATE_HOST_CONTRACT.md:295-301`). Those fields name where a host chooses to keep its records; a registry or host-detector path must lie inside the repository. The fields are unchanged. |
| `KNOWN_DETECTORS` keys | `PYTHON_AST_DETECTOR_IDS` (`python_pack.py:16`), `GUARD_DETECTOR_IDS`, `CONFIG_AST_DETECTOR_IDS`, `ALL_PYTHON_DETECTOR_IDS` (`detectors/__init__.py:11-28`), `TS_DETECTOR_IDS` (`typescript_bridge.py:14`) | `SUBSUMED`: the five sets are deleted (§4.9). |
| `parse_python` | the parse-and-skip in four scanners (§4.9) | `IDENTICAL`: the four copies are deleted. |
| `file_under_root` | `abs_path = repo / path` then `is_file()` in `_scan_changed` (`plugins/arch-compliance/python/acf/cli_check_diff.py:118-119`) | `ADJACENT`: the path comes from `git diff --name-only` over the repository, so it is repo-relative by construction, and the check only skips a path that is not a regular file in the worktree (`changed_files` already excludes deletions with `--diff-filter=ACMR`, `plugins/arch-compliance/python/acf/diff.py:56`); no registry- or host-supplied string reaches it. |
| `file_under_root` | `resolve_under_root` followed by `is_file()` in `load_mandates`, `load_host_detector`, `scan_host_guards`, the hook's `_collect_paths` and `tests/test_self_host.py:40` | `SUBSUMED`: one helper, used at each site. |
| The not-found refusals of `file_under_root`'s callers (`load_mandates`, `load_host_detector`, `scan_ratchet`) | `acf.loader.require_file` (`plugins/arch-compliance/python/acf/loader.py:24-28`) | `ADJACENT`: `require_file` takes an already-built `Path` for an operator input file and always raises `AcfInputError`. These callers first decide containment of a string from a registry row, and each raises its phase's error (`UnknownDetectorError` at load, `DetectorPackError` in the ratchet), which `require_file` cannot express without a new error-type parameter. A `None` from `file_under_root` covers both "outside the root" and "missing"; `require_file` has no containment case. |
| `facade_sink_args`, `fsm_guard_args`, `build_artifact_args` | the inline params extraction in both gates (`cli_check_diff.py:128-166`, `posttooluse_gate.py:255-294`) | `IDENTICAL`: the two copies of each extraction are deleted (§4.9). |
| `TS_MANDATE_IDS` | the Node rules' literal `mandate_id` (`plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:23`, `plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts:15`) | `SUBSUMED`: the bridge stamps the Python value and refuses a Node value that differs (§4.3), so the Node literal is a checked echo, not a second source. |
| `validate_posix_rel_path` | `PosixStr` (`plugins/arch-compliance/python/acf/adr/contract.py:129`) | `ADJACENT`: `PosixStr` refuses backslashes in persisted ADR record fields, which may hold any path text; `validate_posix_rel_path` refuses any non-relative path, using `contains_backslash` and `looks_absolute`. `PosixStr` is unchanged, as are the two `AdrHostConfig` path fields (row above). |
| `Mandate.runs_at`, `MandateRegistry.active` | `cli_check_diff.py:94-99`; `posttooluse_gate.py:229-236`, `:284-286`; `enforcement.py:47` | `SUBSUMED`: each of these sites calls the new definition. |
| `Mandate.runs_at` | `run_judge` (`plugins/arch-compliance/python/acf/judge.py:214-230`) | `ADJACENT`: Tier-2 reviews every `llm` row it is given and reads status only to require a provider (Decision 2 scope). |
| `KNOWN_DETECTORS` contracts | `KNOWN_DETECTORS` frozenset (`cli_check_diff.py:25`); the literal mandate ids in the five scanner modules | `SUBSUMED`: the frozenset becomes the mapping's import; each literal becomes the constant the mapping also reads. |
| Host-reference and row-shape validation | `plugins/arch-compliance/python/acf/registry.py:56-63` | `SUBSUMED`: moved onto `Mandate` and extended in `load_mandates`. |
| Host-file existence check in `load_mandates` | manual-row check (`tests/test_self_host.py:40`) | `SUBSUMED` in mechanism: both use `resolve_under_root` and `is_file()` (§4.7). The test keeps its host-specific prefix rule. |
| `HostHit` → `Finding` construction | `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:75-95` | `ADJACENT`: the bridge decodes untyped JSON from a plugin-owned Node subprocess, coerces path, line and severity from it and stamps `mandate_id` from `TS_MANDATE_IDS` (§4.3); the host runner receives typed `HostHit` objects and takes `mandate_id` and severity from the row. They share only the `Finding` constructor. |
| `HostHit` → `Finding` construction | `_to_finding` (`plugins/arch-compliance/python/acf/judge.py:238-255`) | `ADJACENT`: the judge demotes severity by confidence and admits `path="<diff>"` and `line=0`; host findings take severity straight from the row and require a relative path and `line >= 1`. |
| `make_line_lookup` | `cli_check_diff.py:76-80`, `posttooluse_gate.py:119-123` | `IDENTICAL`: both closures are deleted; `make_line_lookup` is their body. |
| `HostHit` → `Finding` severity | `apply_registry` (`plugins/arch-compliance/python/acf/enforcement.py:52`) | `ADJACENT`: `apply_registry` owns severity for every Tier-1 finding; the runner fills the field only because `Finding` requires it (§4.4 item 5). |
| `load_host_detector` `sys.path` change | `posttooluse_gate.py:22-26`; `plugins/arch-compliance/hooks/inject_constraints.py:28-29` | `ADJACENT`: the hooks put the plugin's own `python/` on the path at start-up. The loader appends one host root once per process, after every existing entry (Decision 6). |
| `_WIN_DRIVE_RE` | `plugins/arch-compliance/python/acf/adr/contract.py:95` | `ADJACENT`: finds backslash drive paths inside persisted ADR text; unchanged. |

---

## 6. Doctrine compliance

| Anchor (`config/architecture/ARCHITECTURE.md`) | Mandate id | How the design complies |
|---|---|---|
| `## Fail loud` (`:24-41`) | `fail-loud.bare-except` | §6.1 lists each invalid state and the error that refuses it. The design has three broad handlers. The load handler (§4.4 item 3) and the call handler (§4.4 item 4) re-raise every exception but `KeyboardInterrupt` as a typed error, so they swallow nothing. `_describe`'s handler (§4.4 item 4) does swallow: when formatting the host's exception itself raises, it returns a constant message, and the typed error that called it is still raised with that message. The doctrine allows that: *"handlers that swallow errors are forbidden unless explicitly exempted with a reason"* (`:29-30`), and `_describe`'s handler carries the `fail-loud.bare-except-ok` token with its reason. The other two carry the token too, to mark the breadth for readers. They are `except BaseException` handlers, which the shipped detector does not flag: it matches only a bare handler or the name `Exception` (`plugins/arch-compliance/python/acf/detectors/python_pack.py:78-82`). |
| `## No shims` (`:43-53`) | `no-shims.hasattr` | Callable lookup is `getattr(mod, attr, None)` followed by `callable(...)` and a raise; no `hasattr`. |
| `## POSIX paths` (`:55-64`) | `posix-paths.str-serialization` | `HostHit.path` is validated by `validate_posix_rel_path`; error messages use `.as_posix()`. |
| `## Fail-loud ratchet` (`:70-73`) | the fail-loud ratchet rows | Its routing is declared in `KNOWN_DETECTORS` (`ci`/`precommit` only), its `baseline` and `roots` must lie inside the repository, and each root must exist (§4.9). §4.8 adds both constraints to the section's enablement instruction. |
| `## One base exception` (`:99-103`) | `plugin.one-base-exception` | No new exception class; uses `AcfInputError`, `UnknownDetectorError`, `DetectorPackError` (`plugins/arch-compliance/python/acf/exceptions.py:5`, `:13`, `:29`). |
| `## One owner for host paths` (`:105-116`) | `plugin.one-owner-host-paths` | `plugins/arch-compliance/python/acf/engine.py`, `plugins/arch-compliance/python/acf/registry.py`, `plugins/arch-compliance/python/acf/detectors/__init__.py` and `plugins/arch-compliance/python/acf/detectors/host.py` spell no `config/architecture` path; the skill snippet takes `MANDATES_REL` and `resolve_repo` from `acf.repo`. |
| `## Declared, never defaulted` (`:118-133`) | `plugin.declared-never-defaulted` | The section governs the ADR gate's host values in `config/architecture/adr.yml` (`:120-123`), and this design adds none. The design follows the same practice by choice for the values it adds: `repo_root` is required for an active host row (`AcfInputError` otherwise), `apply_registry`'s `call_sites` has no default, and `--call-site` is required. |
| `## Prose names no host` (`:135-143`) | `plugin.adr-code-names-no-host`, `plugin.gate-prose-names-no-host` | The runtime messages in §4.2–§4.4 and the prose in §4.8 name no origin host. |
| `## Live consumers` (`:153-157`) | — | §6.2 lists each new export and its runtime caller. |
| `## No completeness claims` (`:159-169`) | — | Population claims carry their recipe (§1, §3, Appendix) or are per-item tables (§4.3, §4.7, §4.8, §6.1, §6.2). |
| `## Declared text decoding` (`:171-182`) | — | New `read_text` calls (`cli_check_diff.py` TypeScript branch, `scan_host_guards`) declare `encoding="utf-8"`. No subprocess is added. |
| `## Release discipline` (`:184-194`) | — | Skill prose changes, so the version is bumped in both files `:186-187` names. |
| `## Single point of definition` (`:196-209`) | — | Within the Tier-1 gates: the absolute and under-root string tests live in `acf.engine`, and the hook and the ratchet consume them instead of their own containment branches (§4.9); row activity in `Mandate.runs_at` (Tier-2 keeps its own, Decision 2); each built-in mandate id in one Python constant, with the TypeScript ids stamped by the bridge from `TS_MANDATE_IDS`; host loading and running in `acf.detectors.host`; line lookup in `make_line_lookup` (§5.2). Where each built-in runs is declared in `KNOWN_DETECTORS` and decided by the gates' dispatch; the contract-against-dispatch test ties the two together (§4.7). The existing definitions listed in §4.9 are deleted and their callers switched; the spec makes no claim that §4.9 lists every duplicate in the tree. |
| `## Scoped refactor` (`:211-215`) | — | Decision 8: what this design makes redundant is deleted in the paths it changes (§4.9). The shared parse helper is in scope, because the host runner would otherwise add one more copy (§4.9). Each gate calling the host runners is two call sites of one procedure, so merging the pre-existing dispatch loops stays a non-goal (§3). |
| `## Frozen ledger format` (`:145-151`) | `plugin.frozen-ledger-format` | No ledger model changes. |

### 6.1 Invalid states and their refusal

| Invalid state | Refused by | Error |
|---|---|---|
| Malformed host reference on an `ast`/`guard` row (any status, any caller) | `Mandate._row_shape` | `AcfInputError` |
| Active `ast`/`guard` row with no Tier-1 call site (any caller) | `Mandate._row_shape` | `AcfInputError` |
| Active host `ast` row with `languages: none` (any caller) | `Mandate._row_shape` | `AcfInputError` |
| Active built-in row naming an id not in `KNOWN_DETECTORS` (LLM prompt ids included) | `load_mandates` with `known_detectors` | `UnknownDetectorError` |
| Active `llm` row naming an id not in `LLM_PROMPT_IDS` | `load_mandates` with `llm_prompt_ids` | `UnknownDetectorError` |
| Active built-in row whose `id` is not its detector's mandate id | `load_mandates` with `known_detectors` | `AcfInputError` |
| Active built-in row declaring a Tier-1 site where no gate runs its detector | `load_mandates` with `known_detectors` | `AcfInputError` |
| Active host row, no `repo_root` | `load_mandates` with `known_detectors` | `AcfInputError` |
| Active host row whose file is missing or outside the root | `load_mandates` with `known_detectors`; `load_host_detector` | `UnknownDetectorError` |
| A second host root in one process | `load_host_detector` | `AcfInputError` |
| Host module fails to import (any exception but `KeyboardInterrupt`), its attribute lookup raises, or it has no such callable | `load_host_detector` at dispatch | `UnknownDetectorError` |
| A file a host guard flags cannot be read (`OSError`) | `scan_host_guards` | `DetectorPackError` |
| TypeScript scanner item with an unknown `detector` or a `mandate_id` other than `TS_MANDATE_IDS[detector]` | `scan_typescript_file` | `DetectorPackError` |
| Host callable raises, or its returned iterable raises while consumed (any exception but `KeyboardInterrupt`: `SystemExit` and custom `BaseException` subclasses included) | `_call_host` | `DetectorPackError` |
| Host returns `None`, a `str`/`bytes`, or a non-iterable | `_call_host` | `DetectorPackError` |
| Host yields an item whose type is not exactly `HostHit` (a subclass included), or a `HostHit` whose fields do not validate (built with `model_construct` or altered after construction) | `_call_host`, rebuilding each item | `DetectorPackError` |
| An `ast` hit on another file | `_to_findings` | `DetectorPackError` |
| `acf-check-diff` without `--call-site`, or with a value outside `ci`/`precommit` | the argument parser | usage error, exit `2` |
| A `--call-site` that selects no active `ast` or `guard` row | `acf-check-diff` after load | `AcfInputError`, exit `1` |
| A host path whose stat raises `OSError` (permission denied, for example) | `load_mandates` and `load_host_detector`; `scan_host_guards` | `UnknownDetectorError`; `DetectorPackError` |
| Host exception whose `__str__` raises | `_describe`, inside each handler | reported as "host exception (message unavailable)" within the `UnknownDetectorError` or `DetectorPackError` |
| `call_sites` value outside `CallSite` | `Mandate` field validation | `AcfInputError` through `load_model_file`; pydantic `ValidationError` on direct construction |
| Ratchet `baseline` or `roots` entry that escapes the root (an absolute path outside it included) or loops, a `baseline` that is missing or cannot be stat'ed, or a `roots` entry that is not an existing directory | `scan_ratchet`, `scan_tree` | `DetectorPackError` |
| `HostHit` with a non-relative or backslash path, `line < 1`, or empty message | `HostHit` validation, raised inside `_call_host` | `DetectorPackError` |

### 6.2 New exports and their callers

| Export | Runtime caller |
|---|---|
| `acf.engine.looks_absolute` | `validate_posix_rel_path`; `acf/adr/citations.py` |
| `acf.engine.resolve_under_root` | `file_under_root`; `scan_ratchet`, `scan_tree`; `acf/adr/citations.py` |
| `acf.engine.file_under_root` | `load_mandates`; `load_host_detector`; `scan_host_guards`; `scan_ratchet`; `posttooluse_gate._collect_paths` |
| `acf.engine.parse_python` | `scan_python_file`, `scan_facade_sinks`, `scan_fsm_writes`, `count_bare_excepts`; `scan_host_ast_file` |
| `acf.engine.validate_posix_rel_path` | `parse_host_detector_ref`; `HostHit` |
| `DIFF_CALL_SITES` / `HOOK_CALL_SITES` | `acf-check-diff`'s `--call-site` choices / `posttooluse_gate.py`; `KNOWN_DETECTORS` |
| `TIER1_CALL_SITES` | `Mandate._row_shape`; `_check_builtin`; `KNOWN_DETECTORS` |
| `BuiltinDetector` | `KNOWN_DETECTORS`; `load_mandates` |
| `Mandate.is_active` | `Mandate.runs_at`; `Mandate._row_shape`; `load_mandates` |
| `Mandate.runs_at` | `MandateRegistry.active`; `apply_registry` |
| `MandateRegistry.active` | both gates; both host runners |
| `is_host_detector_ref`, `parse_host_detector_ref` | `Mandate._row_shape`; `load_mandates`; host runners; `load_host_detector` |
| `acf.detectors.KNOWN_DETECTORS` | both gates (`load_mandates` calls) |
| scanner mandate-id constants; `python_pack`'s three detector-id constants | their scanners; `KNOWN_DETECTORS` |
| `CallSite` | `Mandate.call_sites` |
| `facade_sink_args`, `fsm_guard_args`, `build_artifact_args` | both gates |
| `TS_MANDATE_IDS` | `scan_typescript_file`; `KNOWN_DETECTORS` |
| `acf.judge.LLM_PROMPT_IDS` (existing; loses its `KNOWN_DETECTORS` use) | `acf-check-diff` (`load_mandates(..., llm_prompt_ids=...)`); the acf-mandate `## Validate` snippet |
| `HostHit` | host callables (imported by host code); `_to_findings` |
| `load_host_detector` | `scan_host_ast_file`; `scan_host_guards` |
| `scan_host_ast_file`, `scan_host_guards` | both gates |
| `make_line_lookup` | both gates |

---

## 7. Verification and definition of done

1. The §4.7 tests exist and pass.
2. `PYTHONUTF8=1 python -m pytest -q`, `PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main --call-site ci` and `npm test --prefix plugins/arch-compliance/detectors/typescript` pass.
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
| Shipped `llm` rows against `LLM_PROMPT_IDS` | `python -c "import yaml,glob; [print(f, m['status'], m['id'], m['detector']) for f in ['config/architecture/mandates.yml', *glob.glob('plugins/arch-compliance/profiles/*/mandates.yml'), 'plugins/arch-compliance/tests/fixtures/mandates_valid.yml'] for m in yaml.safe_load(open(f, encoding='utf-8')) if m['detection'] == 'llm']"` | `config/architecture/mandates.yml`: `soft.react-boundaries` (`unenforced`, `llm_react_boundaries`), `soft.fail-loud` (`partial`, `llm_fail_loud`); `profiles/python-service`: `soft.fail-loud` (`partial`, `llm_fail_loud`); `profiles/react-app`: `soft.react-boundaries` (`partial`, `llm_react_boundaries`). Each detector is in `LLM_PROMPT_IDS` (`plugins/arch-compliance/python/acf/judge.py:29-36`). The inline `llm` row at `plugins/arch-compliance/tests/test_judge.py:390` is `unenforced`. |
| Shipped values the §4.9 switches newly validate | `git grep -n "baseline:\|roots:" -- config/architecture/mandates.yml 'plugins/arch-compliance/profiles/*/mandates.yml'` | Ratchet rows (`config/architecture/mandates.yml:97-98`, `plugins/arch-compliance/profiles/python-service/mandates.yml:58-59`): `baseline: config/architecture/fail_loud_ratchet.json`, `roots: ["."]`. Each is a relative POSIX path with no `..`, so no switch refuses a shipped value. Test value: `test_portable_guards.py:107` passes `roots=["pkg"]`. |
| Rows that add `precommit` | `python -c "import yaml,glob; [print(f, m['id'], m['status'], m['call_sites']) for f in ['config/architecture/mandates.yml', *sorted(glob.glob('plugins/arch-compliance/profiles/*/mandates.yml')), 'plugins/arch-compliance/tests/fixtures/mandates_valid.yml'] for m in yaml.safe_load(open(f, encoding='utf-8')) if m['detection'] in ('ast', 'guard') and 'ci' in m['call_sites']]"` | `config/architecture/mandates.yml` 9 rows (`fail-loud.empty-catch`, `no-shims.explicit-any`, `ops.no-build-artifacts`, `fail-loud.bare-except`, `no-shims.hasattr`, `posix-paths.str-serialization`, `fail-loud.ratchet`, `facade.forbid-sink`, `fsm.transition-guard`); `profiles/python-service` 7 (`fail-loud.bare-except`, `no-shims.hasattr`, `posix-paths.str-serialization`, `ops.no-build-artifacts`, `fail-loud.ratchet`, `facade.forbid-sink`, `fsm.transition-guard`); `profiles/react-app` 3 (`fail-loud.empty-catch`, `no-shims.explicit-any`, `ops.no-build-artifacts`); `tests/fixtures/mandates_valid.yml` 3 (`fail-loud.bare-except`, `no-shims.hasattr`, `fail-loud.empty-catch`). No shipped row declares `precommit` before this change. |
| Shipped `call_sites` values against `CallSite` | `git grep -n "call_sites" -- '*.yml' 'plugins/arch-compliance/tests/*.py'` | Every value is one of `ci`, `hook`, `audit` (the inline `test_template.py:80` row declares `[]`). |
| `KNOWN_DETECTORS` size | `python -c "from acf.cli_check_diff import KNOWN_DETECTORS as K; print(len(K))"` | `13` today (9 Python and TypeScript ids plus 4 LLM prompt ids); `9` after this design. |
