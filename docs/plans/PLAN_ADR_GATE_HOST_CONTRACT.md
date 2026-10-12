# The ADR Gate's Host Contract — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let any host run the adversarial-design-review gate from this plugin: the gate reads its two storage locations from one declared host file and its doctrine from the plugin's fixed doctrine path, and the two skills' prose moves here with no host value left in it.

**Architecture:** One new pydantic model and loader (`acf.adr.host`), one constant (`acf.repo.ADR_REL`), and one helper extracted from the existing loader (`acf.loader.require_file`) that the constraints hook also uses. The two ported defaults that carry the origin host's layout are deleted. The skill prose is copied from the origin host and rewritten line by line against the spec's census, and tests pin that the prose's Python resolves against this package and names no host.

**Tech Stack:** Python 3.11+, pydantic v2, PyYAML, pytest. No new dependency.

**Spec:** `C:/Users/iball/Arduino/Projects/HistoricMansions/docs/design/ADR_GATE_HOST_CONTRACT.md` (v4, approved by user override 2026-10-12, HistoricMansions commit `86f93f95`). Its §4.2 table is the authority for every prose edit in Task 5. Section references below (§N) are to that spec.

## Global Constraints

- **Origin repository is read-only.** `C:/Users/iball/Arduino/Projects/HistoricMansions` — copy from it, never write to it (spec DoD 9).
- **Python floor `>=3.11`, pydantic `>=2.0`.** Unchanged; no new third-party dependency.
- **`acf.repo` stays stdlib-only** (`plugins/arch-compliance/tests/test_repo_paths.py:74-78`).
- **New exceptions subclass `AcfError` alone** (`plugins/arch-compliance/tests/test_adr_exceptions.py:34`).
- **The ledger record format does not change** — not a field, not the `TouchedSurface` vocabulary (§3).
- **Hook message text is preserved byte-for-byte:** `doctrine document not found: <path>`.
- **Both `adr.yml` fields are required, `PosixStr`, `Field(min_length=1)`.** No defaults (§5.1–§5.2).
- **Verification** from the repository root: `python -m pytest -q` (baseline at `277bcca4`: **372 passed**) and `npm test --prefix plugins/arch-compliance/detectors/typescript` → `self-test OK`.

## Review Focus

1. **A host run from a subdirectory.** `resolve_repo(None)` resolves the process directory (`acf/repo.py:41`); run from below the host root, `load_host_config` must refuse loudly (no `adr.yml` there), not create records in the wrong place. Task 2 pins it.
2. **An `adr.yml` written on Windows with backslashes, or with an empty value.** Both must be refused at load, before any reviewer is dispatched. Task 2 pins both.
3. **The constraints hook on a host with `.acf/enabled` but no `ARCHITECTURE.md`.** It must still print one `acf: doctrine document not found: …` line and exit 1 — now via `AcfInputError`. Task 1 pins it with the existing hook test plus an exact-message assertion.
4. **A prose Python step copied but not rewritten.** The deleted `runs_dir` default turns a missed `run_detail_path` edit into a runtime `TypeError` after four reviewers have run; Task 5's AST test catches the call shape before that.
5. **A run-detail or ledger write landing outside the declared host.** The acceptance test (Task 6) runs from a process directory that is *not* the fixture host and asserts nothing is written outside it.

## Architectural Contract

1. The plugin's only host-relative path constants live in `acf/repo.py`; `adr.yml` is located by `ADR_REL` there.
2. Every "input file is wrong" refusal on a pydantic-path caller goes through `acf.loader` (`require_file`, `load_model_file`) and raises `AcfInputError`.
3. The moved skill prose contains no origin-host value: every host value comes from `resolve_repo(None)`, `load_host_config(repo)`, or `config/architecture/ARCHITECTURE.md` and the documents it points to.
4. Persisted paths stay POSIX; `adr.yml` path fields refuse a backslash rather than normalizing it.

## State & Data Definitions

- **HFSM:** none. The design adds or changes no state and no transition.
- **Pydantic schemas added:** `acf.adr.host.AdrHostConfig` — `extra="forbid"`; `runs_dir: PosixStr = Field(min_length=1)`; `ledger_path: PosixStr = Field(min_length=1)`.
- **Persisted format added:** host file `config/architecture/adr.yml` (two keys above). Ledger and run-detail formats unchanged.
- **Exceptions added:** `acf.exceptions.UnresolvableCitationError(AcfError)`. No other new type; refusals reuse `AcfInputError`.
- **Public interface changes (`acf.adr`):** add `AdrHostConfig`, `load_host_config`; remove `LEDGER_PATH`, `RUNS_DIR`; `run_detail_path(..., runs_dir=...)` becomes required. Code review required before merge (GEMINI.md §2 in the origin host).

## Shape Fit

New functionality, extending existing shapes (spec §6): `ADR_REL` beside `MANDATES_REL`/`ARCH_REL`/`RATCHET_BASELINE_REL`; `load_host_config` as a third caller of `load_model_file` (after `registry.py:42`, `baseline.py:86`); `require_file` extracted from `load_model_file`'s own first check; `PosixStr` reused from `acf/adr/contract.py:129`; `resolve_repo` reused; skills dropped into `skills/` beside the existing three. Second ways created on purpose are declared debt in the origin host's roadmap (*Phase 1c declared debt*). Pattern sweep: the spec's recipes A–D; Tasks 4 and 5 add tests that keep the swept classes from returning.

## Development Workspace & Integration

**Branch:** `feat/adr-host-contract` from `main` at `277bcca4`, in the plugin checkout `C:/Users/iball/Arduino/Projects/arch-compliance-for-superpowers` (the way phase 1b ran). Every task's first action: `git -C C:/Users/iball/Arduino/Projects/arch-compliance-for-superpowers branch --show-current` must print `feat/adr-host-contract`; abort **BLOCKED** otherwise.

**Integration:** one PR to `main` after Task 7; merge only after the full suite and the TypeScript lane pass and a whole-branch review has run.

### Implementation Decision Overrides

| Decision | Override | Rationale | Approved |
|---|---|---|---|
| Workspace | Branch in the plugin's own checkout, not a git worktree | Separate repository from the origin host; phase 1b ran the same way without incident | Default practice for this plugin, carried from 1b |
| CI gates | `python -m pytest -q` + TypeScript self-test (the plugin's whole gate), not the origin host's `run_ci.sh` | The plugin has no `run_ci.sh`; these are its complete test lanes | Same |

## File Structure

| File | Change | Task |
|---|---|---|
| `plugins/arch-compliance/python/acf/loader.py` | Add `require_file`; `load_model_file` calls it | 1 |
| `plugins/arch-compliance/hooks/inject_constraints.py` | Doctrine read via `require_file`; except clause gains `AcfInputError` | 1 |
| `plugins/arch-compliance/tests/test_loader.py`, `tests/test_hooks.py` | `require_file` tests; exact hook message | 1 |
| `plugins/arch-compliance/python/acf/repo.py` | `ADR_REL` | 2 |
| `plugins/arch-compliance/python/acf/adr/host.py` | **Create.** `AdrHostConfig`, `load_host_config` | 2 |
| `plugins/arch-compliance/python/acf/exceptions.py` | `UnresolvableCitationError` | 2 |
| `plugins/arch-compliance/python/acf/adr/__init__.py` | Export host names (2); drop the two constants (3) | 2, 3 |
| `plugins/arch-compliance/tests/test_adr_host.py` | **Create.** | 2 |
| `plugins/arch-compliance/tests/test_adr_exceptions.py`, `test_adr_import_graph.py` | Lists updated | 2, 3 |
| `plugins/arch-compliance/python/acf/adr/ledger.py`, `run_detail.py` | Delete `LEDGER_PATH`, `RUNS_DIR`; `runs_dir` required | 3 |
| `plugins/arch-compliance/tests/test_adr_ledger.py`, `test_adr_run_detail.py` | Remove value pins | 3 |
| `README.md` | `:84` rewritten (3); Override contract names the gate (7) | 3, 7 |
| `plugins/arch-compliance/python/acf/adr/*.py` (contract, convergence, gate, ledger, parser, rollup, run_detail, citations) | Host references in comments and two runtime strings rewritten | 4 |
| `plugins/arch-compliance/tests/test_adr_code_portability.py` | **Create.** | 4 |
| `plugins/arch-compliance/skills/adversarial-design-review/**`, `skills/responding-to-adversarial-review/SKILL.md` | **Create** by copy from the origin host, then rewrite | 5 |
| `plugins/arch-compliance/tests/test_adr_skill_prose.py` | **Create.** | 5 |
| `plugins/arch-compliance/tests/test_adr_host_acceptance.py` | **Create.** | 6 |
| `docs/plans/PLAN_ADR_GATE_HOST_CONTRACT.md` | Outcome section | 7 |

---

### Task 1: One refusal for an absent doctrine document

**Files:**
- Modify: `plugins/arch-compliance/python/acf/loader.py:51-52`
- Modify: `plugins/arch-compliance/hooks/inject_constraints.py:111`, `:163-167`
- Test: `plugins/arch-compliance/tests/test_loader.py`, `plugins/arch-compliance/tests/test_hooks.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `acf.loader.require_file(path: Path, *, subject: str) -> Path` — raises `AcfInputError(f"{subject} not found: {path.as_posix()}")` when `path` is not a file; returns `path` otherwise.

- [ ] **Step 1: Branch guard**

Run: `git -C C:/Users/iball/Arduino/Projects/arch-compliance-for-superpowers checkout feat/adr-host-contract && git -C C:/Users/iball/Arduino/Projects/arch-compliance-for-superpowers branch --show-current` (the branch was cut from `277bcca4` with this plan's commit)
Expected: `feat/adr-host-contract`

- [ ] **Step 2: Write the failing tests**

Append to `plugins/arch-compliance/tests/test_loader.py`:

```python
def test_require_file_refuses_an_absent_path_naming_it(tmp_path):
    from acf.loader import require_file

    missing = tmp_path / "ARCHITECTURE.md"
    with pytest.raises(AcfInputError) as excinfo:
        require_file(missing, subject="doctrine document")
    assert str(excinfo.value) == f"doctrine document not found: {missing.as_posix()}"


def test_require_file_returns_the_path_when_present(tmp_path):
    from acf.loader import require_file

    present = tmp_path / "doc.md"
    present.write_text("x\n", encoding="utf-8")
    assert require_file(present, subject="doc") == present
```

Append to `plugins/arch-compliance/tests/test_hooks.py` (it already defines `_seed_host`, `INJECT`, `subprocess`, `sys`):

```python
def test_inject_doctrine_refusal_message_is_unchanged(tmp_path: Path) -> None:
    """The refusal moved to acf.loader.require_file; its text did not change."""
    repo = _seed_host(tmp_path, enabled=True, mandates=True)
    doctrine = repo / "config" / "architecture" / "ARCHITECTURE.md"
    doctrine.unlink()
    proc = subprocess.run(
        [sys.executable, str(INJECT), "--repo", str(repo)],
        capture_output=True, text=True, input="",
    )
    assert proc.returncode == 1
    assert f"acf: doctrine document not found: {doctrine.as_posix()}" in proc.stderr
```

- [ ] **Step 3: Run to verify the loader tests fail**

Run: `python -m pytest plugins/arch-compliance/tests/test_loader.py -k require_file -v`
Expected: 2 FAIL with `ImportError: cannot import name 'require_file'`. (The hook test passes today — it pins behaviour that must survive Step 4.)

- [ ] **Step 4: Implement**

In `plugins/arch-compliance/python/acf/loader.py`, add above `load_model_file`'s overloads:

```python
def require_file(path: Path, *, subject: str) -> Path:
    """Refuse an absent input file with the message shape every caller shares."""
    if not path.is_file():
        raise AcfInputError(f"{subject} not found: {path.as_posix()}")
    return path
```

and replace `load_model_file`'s first two body lines (`:51-52`) with:

```python
    require_file(path, subject=subject)
```

In `plugins/arch-compliance/hooks/inject_constraints.py`, replace `:163-167`:

```python
    arch_path = repo / ARCH_REL
    if not arch_path.is_file():
        raise FileNotFoundError(
            f"doctrine document not found: {arch_path.as_posix()}"
        )
```

with (a deferred import, like the `acf.template` import below it):

```python
    from acf.loader import require_file

    arch_path = require_file(repo / ARCH_REL, subject="doctrine document")
```

and change `:111` from `except (FileNotFoundError, OSError) as exc:` to `except (AcfInputError, FileNotFoundError, OSError) as exc:` (`AcfInputError` is already imported at `:91`).

- [ ] **Step 5: Run the tests**

Run: `python -m pytest plugins/arch-compliance/tests/test_loader.py plugins/arch-compliance/tests/test_hooks.py -v`
Expected: all pass, including `test_inject_fails_loud_when_doctrine_document_missing` (`:253`) and `test_hooks_import_repo_without_pulling_third_party`.

Run: `python -m pytest -q`
Expected: **375 passed** (372 + 3).

- [ ] **Step 6: Commit**

```bash
git add plugins/arch-compliance/python/acf/loader.py plugins/arch-compliance/hooks/inject_constraints.py plugins/arch-compliance/tests/test_loader.py plugins/arch-compliance/tests/test_hooks.py
git commit -m "refactor: one refusal for an absent doctrine document

Extract load_model_file's absent-file check as acf.loader.require_file and
call it from the constraints hook's doctrine read, which raised a builtin
FileNotFoundError with the same text. The message is unchanged; the hook's
except clause now also catches AcfInputError."
```

---

### Task 2: The host declaration

**Files:**
- Modify: `plugins/arch-compliance/python/acf/repo.py` (after `ARCH_REL`)
- Create: `plugins/arch-compliance/python/acf/adr/host.py`
- Modify: `plugins/arch-compliance/python/acf/exceptions.py` (append)
- Modify: `plugins/arch-compliance/python/acf/adr/__init__.py`
- Create: `plugins/arch-compliance/tests/test_adr_host.py`
- Modify: `plugins/arch-compliance/tests/test_adr_exceptions.py:10-16`, `plugins/arch-compliance/tests/test_adr_import_graph.py:14-40`

**Interfaces:**
- Consumes: `acf.loader.require_file` (Task 1).
- Produces: `acf.repo.ADR_REL: Path`; `acf.adr.AdrHostConfig` (`runs_dir: str`, `ledger_path: str`); `acf.adr.load_host_config(repo: Path) -> AdrHostConfig`; `acf.exceptions.UnresolvableCitationError`.

- [ ] **Step 1: Branch guard** — `git branch --show-current` prints `feat/adr-host-contract`.

- [ ] **Step 2: Write the failing tests**

Create `plugins/arch-compliance/tests/test_adr_host.py`:

```python
"""The host contract: adr.yml plus the fixed doctrine document."""
from __future__ import annotations

from pathlib import Path

import pytest

from acf.adr import AdrHostConfig, load_host_config
from acf.exceptions import AcfInputError

VALID = "runs_dir: reviews/runs\nledger_path: reviews/ledger.jsonl\n"


def _host(root: Path, adr_yml: str | None = VALID, doctrine: bool = True) -> Path:
    cfg = root / "config" / "architecture"
    cfg.mkdir(parents=True)
    if adr_yml is not None:
        (cfg / "adr.yml").write_text(adr_yml, encoding="utf-8")
    if doctrine:
        (cfg / "ARCHITECTURE.md").write_text("# Doctrine\n", encoding="utf-8")
    return root


def test_a_valid_declaration_loads(tmp_path):
    cfg = load_host_config(_host(tmp_path))
    assert isinstance(cfg, AdrHostConfig)
    assert cfg.runs_dir == "reviews/runs"
    assert cfg.ledger_path == "reviews/ledger.jsonl"


def test_storage_locations_need_not_exist_yet(tmp_path):
    host = _host(tmp_path)
    assert not (host / "reviews").exists()
    load_host_config(host)


@pytest.mark.parametrize(
    "adr_yml,fragment",
    [
        (None, "ADR host config not found"),
        (VALID + "spec_dir: specs\n", "invalid ADR host config"),
        ("ledger_path: reviews/ledger.jsonl\n", "invalid ADR host config"),
        ("runs_dir: reviews/runs\n", "invalid ADR host config"),
        ('runs_dir: ""\nledger_path: reviews/ledger.jsonl\n', "invalid ADR host config"),
        ("runs_dir: reviews\\runs\nledger_path: reviews/ledger.jsonl\n", "invalid ADR host config"),
    ],
    ids=["absent", "unknown-key", "missing-runs_dir", "missing-ledger_path", "empty-value", "backslash"],
)
def test_a_bad_declaration_is_refused(tmp_path, adr_yml, fragment):
    with pytest.raises(AcfInputError) as excinfo:
        load_host_config(_host(tmp_path, adr_yml=adr_yml))
    assert fragment in str(excinfo.value)


def test_an_absent_doctrine_document_is_refused(tmp_path):
    with pytest.raises(AcfInputError) as excinfo:
        load_host_config(_host(tmp_path, doctrine=False))
    assert "doctrine document not found" in str(excinfo.value)


def test_a_subdirectory_is_not_a_host(tmp_path):
    """Review Focus 1: run below the host root, the load refuses — it never guesses."""
    host = _host(tmp_path)
    sub = host / "src"
    sub.mkdir()
    with pytest.raises(AcfInputError):
        load_host_config(sub)
```

In `plugins/arch-compliance/tests/test_adr_exceptions.py`, add `"UnresolvableCitationError",` to `ADR_TYPES` (`:10-16`).

In `plugins/arch-compliance/tests/test_adr_import_graph.py`, add `"AdrHostConfig",` and `"load_host_config",` to `EXPECTED_SURFACE` (`:14-40`).

- [ ] **Step 3: Run to verify they fail**

Run: `python -m pytest plugins/arch-compliance/tests/test_adr_host.py plugins/arch-compliance/tests/test_adr_exceptions.py plugins/arch-compliance/tests/test_adr_import_graph.py -q`
Expected: collection error in `test_adr_host.py` (`cannot import name 'AdrHostConfig'`); `UnresolvableCitationError` existence tests FAIL; surface test FAILS.

- [ ] **Step 4: Implement**

`plugins/arch-compliance/python/acf/repo.py`, after `ARCH_REL`:

```python
#: Host-relative path to the adversarial-design-review gate's declaration.
ADR_REL = CONFIG_DIR / "adr.yml"
```

`plugins/arch-compliance/python/acf/exceptions.py`, append:

```python
class UnresolvableCitationError(AcfError):
    """A spec cites a path that is not current, historical, proposed, asserted absent or external."""
```

Create `plugins/arch-compliance/python/acf/adr/host.py`:

```python
"""The host contract: where a host keeps the gate's records.

A host declares two storage locations in ``config/architecture/adr.yml``. Its
doctrine is not declared: it is ``config/architecture/ARCHITECTURE.md`` and the
documents that file points to, which must exist before any review runs.
"""
from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from acf.adr.contract import PosixStr
from acf.loader import load_model_file, require_file
from acf.repo import ADR_REL, ARCH_REL


class AdrHostConfig(BaseModel):
    """The two host values the gate cannot derive."""

    model_config = ConfigDict(extra="forbid")

    runs_dir: PosixStr = Field(min_length=1)
    ledger_path: PosixStr = Field(min_length=1)


def load_host_config(repo: Path) -> AdrHostConfig:
    """Refuse a host without its doctrine document, then load its declaration."""
    require_file(repo / ARCH_REL, subject="doctrine document")
    return load_model_file(
        repo / ADR_REL, AdrHostConfig, subject="ADR host config", fmt="yaml"
    )
```

`plugins/arch-compliance/python/acf/adr/__init__.py`: after the `acf.adr.run_detail` import block add

```python
from acf.adr.host import AdrHostConfig, load_host_config
```

and add `"AdrHostConfig",` and `"load_host_config",` to `__all__` in sorted position.

- [ ] **Step 5: Run the tests**

Run: `python -m pytest plugins/arch-compliance/tests/test_adr_host.py plugins/arch-compliance/tests/test_adr_exceptions.py plugins/arch-compliance/tests/test_adr_import_graph.py plugins/arch-compliance/tests/test_repo_paths.py -v`
Expected: all pass (the stdlib-only and one-owner tests in `test_repo_paths.py` included).

Run: `python -m pytest -q`
Expected: **387 passed** (375 + 10 in `test_adr_host.py` — 2 plain, 6 parametrized, 2 plain — + 2 from the `ADR_TYPES` parametrization).

- [ ] **Step 6: Commit**

```bash
git add plugins/arch-compliance/python/acf/repo.py plugins/arch-compliance/python/acf/adr/host.py plugins/arch-compliance/python/acf/exceptions.py plugins/arch-compliance/python/acf/adr/__init__.py plugins/arch-compliance/tests/test_adr_host.py plugins/arch-compliance/tests/test_adr_exceptions.py plugins/arch-compliance/tests/test_adr_import_graph.py
git commit -m "feat: the ADR gate's host declaration (adr.yml) and UnresolvableCitationError

AdrHostConfig holds the two storage locations a host must declare; both are
required, POSIX, non-empty. load_host_config refuses a host without its
doctrine document, then loads config/architecture/adr.yml through the
plugin's one loader. UnresolvableCitationError arrives with the prose that
raises it."
```

---

### Task 3: Delete the ported defaults

**Files:**
- Modify: `plugins/arch-compliance/python/acf/adr/ledger.py:34`, `plugins/arch-compliance/python/acf/adr/run_detail.py:35-40`, `plugins/arch-compliance/python/acf/adr/__init__.py`
- Modify: `plugins/arch-compliance/tests/test_adr_ledger.py:10, 67-68`, `plugins/arch-compliance/tests/test_adr_run_detail.py:31, 100`, `plugins/arch-compliance/tests/test_adr_import_graph.py`
- Modify: `README.md:83-85`

**Interfaces:**
- Consumes: nothing from Tasks 1–2.
- Produces: `run_detail_path(spec_path: str, *, version: int, date: str, runs_dir: Path | str) -> Path` (`runs_dir` required); `acf.adr` no longer exports `LEDGER_PATH` or `RUNS_DIR`.

- [ ] **Step 1: Branch guard** — `git branch --show-current` prints `feat/adr-host-contract`.

- [ ] **Step 2: Census before deleting (spec §5.3)**

Run: `git grep -n "LEDGER_PATH\|RUNS_DIR"`
Expected: exactly the §5.3 sites — `ledger.py:34`, `run_detail.py:35, 39`, `adr/__init__.py:19, 36, 48, 51`, `test_adr_import_graph.py:20, 23`, `test_adr_ledger.py:10, 68`, `test_adr_run_detail.py:31, 100`, `README.md:84`, `docs/plans/PLAN_PORT_ADR_PACKAGE.md:376, 788`. Any other hit: stop, report BLOCKED.

- [ ] **Step 3: Write the failing tests**

In `plugins/arch-compliance/tests/test_adr_import_graph.py`, remove `"LEDGER_PATH",` and `"RUNS_DIR",` from `EXPECTED_SURFACE`. Append to `plugins/arch-compliance/tests/test_adr_run_detail.py`:

```python
def test_run_detail_path_requires_runs_dir():
    with pytest.raises(TypeError):
        run_detail_path("docs/X.md", version=1, date="2026-10-12")  # type: ignore[call-arg]
```

(`pytest` is already imported there; if not, add `import pytest`.)

- [ ] **Step 4: Run to verify they fail**

Run: `python -m pytest plugins/arch-compliance/tests/test_adr_import_graph.py plugins/arch-compliance/tests/test_adr_run_detail.py -q`
Expected: surface-equality test FAILS (extra names present); `test_run_detail_path_requires_runs_dir` FAILS (`DID NOT RAISE`).

- [ ] **Step 5: Implement**

- `ledger.py`: delete the `LEDGER_PATH = ...` line (`:34`) and any comment that documents only it.
- `run_detail.py`: delete `RUNS_DIR = ...` (`:35`) and its comment; change the signature at `:38-40` to `def run_detail_path(spec_path: str, *, version: int, date: str, runs_dir: Path | str) -> Path:`.
- `adr/__init__.py`: remove `LEDGER_PATH,` and `RUNS_DIR,` from the import blocks and from `__all__`.
- `tests/test_adr_ledger.py`: remove `LEDGER_PATH,` from the import (`:10`) and delete `test_ledger_path_is_the_spec_location` (`:67-68`).
- `tests/test_adr_run_detail.py`: remove `RUNS_DIR,` from the import (`:31`) and delete only the assertion line `assert RUNS_DIR == "docs/reviews/adr_runs"` (`:100`); the test keeps its POSIX and file-name assertions.
- `README.md:83-85`: replace "For the same reason the package's `LEDGER_PATH` and `RUNS_DIR` defaults still carry the origin host's relative paths; both are overridable arguments, not import-time reads." with "Where a host keeps the gate's run details and ledger is declared in `config/architecture/adr.yml` (`runs_dir`, `ledger_path`) and read by `acf.adr.load_host_config`; the package carries no default for either."

- [ ] **Step 6: Run the tests and the census**

Run: `python -m pytest -q`
Expected: **387 passed** (one ledger pin deleted, one `TypeError` test added).

Run: `git grep -n "LEDGER_PATH\|RUNS_DIR" -- plugins README.md`
Expected: no output.

- [ ] **Step 7: Commit**

```bash
git add -A plugins/arch-compliance README.md
git commit -m "feat!: delete the LEDGER_PATH/RUNS_DIR defaults; runs_dir is required

Both carried the origin host's layout; with adr.yml declaring the two
locations they were a second source for the same value, and a host that
forgot to declare would have written into another repository's paths."
```

---

### Task 4: No host references in the package's code

**Files:**
- Create: `plugins/arch-compliance/tests/test_adr_code_portability.py`
- Modify (comments/docstrings, two runtime strings): `plugins/arch-compliance/python/acf/adr/{contract,convergence,gate,ledger,parser,rollup,run_detail,citations}.py` at the lines spec §4.2 lists for recipe D1; `plugins/arch-compliance/tests/test_adr_contract.py:1`, `plugins/arch-compliance/tests/test_adr_ledger.py:141`

**Interfaces:**
- Consumes: nothing.
- Produces: nothing other tasks consume. Behaviour unchanged except two message strings.

- [ ] **Step 1: Branch guard** — `git branch --show-current` prints `feat/adr-host-contract`.

- [ ] **Step 2: Write the failing test**

Create `plugins/arch-compliance/tests/test_adr_code_portability.py`:

```python
"""The gate's package names no origin host: no doctrine, section numbers, paths or data."""
from __future__ import annotations

import re
from pathlib import Path

ADR = Path(__file__).resolve().parents[1] / "python" / "acf" / "adr"
HOST = re.compile(r"GEMINI|§\d|scripts/|scripts\.core|HistoricMansions|book[ _]|book_order")


def test_no_module_in_acf_adr_names_the_origin_host():
    offenders = [
        f"{path.name}:{n}: {line.strip()}"
        for path in sorted(ADR.glob("*.py"))
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        if HOST.search(line)
    ]
    assert offenders == [], "\n".join(offenders)


def test_runtime_messages_name_no_host_section():
    parser = (ADR / "parser.py").read_text(encoding="utf-8")
    gate = (ADR / "gate.py").read_text(encoding="utf-8")
    assert "every path field must be POSIX (no backslashes)." in parser
    assert "presumptively papering over the crack\"" in gate
```

- [ ] **Step 3: Run to verify it fails**

Run: `python -m pytest plugins/arch-compliance/tests/test_adr_code_portability.py -v`
Expected: first test FAILS listing the recipe-D1 lines (spec §4.2: `contract.py:7, 8, 61, 67, 76, 78, 83, 162`; `convergence.py:17, 31`; `gate.py:43, 44, 49, 93, 189, 276, 280`; `ledger.py:53, 70, 71, 116, 179, 202`; `parser.py:6, 97`; `rollup.py:49`; `run_detail.py:9, 16`; `citations.py:10, 16, 116, 117, 151, 157, 174, 175`). Second test FAILS.

- [ ] **Step 4: Rewrite each listed line**

Rules, applied line by line (no behaviour change except the two runtime strings):

- Runtime strings: `parser.py:97` becomes `message += "\nHint: every path field must be POSIX (no backslashes)."`; `gate.py:279-280` becomes `"defect spec extracts no deletion claim — an addition-only design is "` / `"presumptively papering over the crack"`.
- `§3` → "fail loud"; `§4` → "no shims"; `§7` → "one point of definition"; `§10` → "POSIX paths"; `§14` → "class cohesion"; `§1.7` → "the shape-fit rule"; "GEMINI.md" → "the doctrine". A sentence that only cites a section number with no remaining content loses the citation.
- `ledger.py:52-56` (the `TouchedSurface` comment): "Must stay in step with `filter_would_skip`'s surface list in the adversarial-design-review skill, which is derived from it: …" — keep the rest of the rationale, drop "GEMINI.md item 8".
- Origin-host paths and incidents used as examples (`scripts/x.py`, `scripts/ci/arch_compliance/engine.py`, `scripts/schemas/oakville_import.py`, `scripts/core/book_registry.py`, `scripts/api/routes/content.py`, `scripts/cms_server/routes/`, `check_book_tier_drift.py`, "book root(s)", `ledger.py:116`'s spec reference): replace with neutral examples (`src/x.py`, "a host's own detector", "a module in the host", "a renamed routes directory", "a host checker script", "a live data directory") or delete the clause when it only names the incident.
- `tests/test_adr_contract.py:1` and `tests/test_adr_ledger.py:141`: same rules (test data at `test_adr_contract.py:62` and `test_adr_ledger.py:588` stays — fixtures).

- [ ] **Step 5: Run the tests**

Run: `python -m pytest plugins/arch-compliance/tests/test_adr_code_portability.py -v` → PASS.
Run: `git grep -n "GEMINI\|scripts\.core\|HistoricMansions\|§[0-9]\|scripts/\|book" -- plugins/arch-compliance/python plugins/arch-compliance/hooks`
Expected: only `python/acf/judge.py` lines (the Gemini API — spec §4.2 keeps them).
Run: `python -m pytest -q` → **389 passed**.

- [ ] **Step 6: Commit**

```bash
git add -A plugins/arch-compliance
git commit -m "refactor: the ADR package names no origin host

Comments and docstrings cited the origin host's section numbers, doctrine
and module paths; two runtime messages (the backslash hint and the
addition-only absorption) showed every host its section numbers. Rewritten
to name the rule itself. A test keeps the class out."
```

---

### Task 5: Move the skill prose

**Files:**
- Create (copy then edit): `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md`, `…/claims/extraction.md`, `…/reviewers/{compliance,hardening,refuter,sweeper}.md`; `plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md`
- Create: `plugins/arch-compliance/tests/test_adr_skill_prose.py`

**Interfaces:**
- Consumes: `acf.adr.load_host_config`, `acf.repo.resolve_repo`, `acf.exceptions.UnresolvableCitationError` (Task 2); required `runs_dir` (Task 3).
- Produces: the two skills, invocable from the plugin.

- [ ] **Step 1: Branch guard** — `git branch --show-current` prints `feat/adr-host-contract`.

- [ ] **Step 2: Write the failing test**

Create `plugins/arch-compliance/tests/test_adr_skill_prose.py`:

```python
"""The moved gate prose: its Python resolves here, and it names no origin host."""
from __future__ import annotations

import ast
import importlib
import re
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[1] / "skills"
GATE = SKILLS / "adversarial-design-review"
RESPOND = SKILLS / "responding-to-adversarial-review"
FILES = [
    GATE / "SKILL.md", GATE / "claims" / "extraction.md",
    GATE / "reviewers" / "compliance.md", GATE / "reviewers" / "hardening.md",
    GATE / "reviewers" / "refuter.md", GATE / "reviewers" / "sweeper.md",
    RESPOND / "SKILL.md",
]
FORBIDDEN = ["GEMINI", "CLAUDE.md", "SKILL_PROVENANCE", "scripts.core",
             "docs/design", "docs/reviews", "docs/architecture", ".cursor"]


def _python_bodies() -> list[tuple[str, str]]:
    bodies = []
    for skill in (GATE / "SKILL.md", RESPOND / "SKILL.md"):
        text = skill.read_text(encoding="utf-8")
        bodies += [(f"{skill.parent.name}:python", b) for b in re.findall(r"```python\n(.*?)```", text, re.S)]
        bodies += [(f"{skill.parent.name}:python -c", b) for b in re.findall(r'python -c "\n(.*?)"\n', text, re.S)]
    return bodies


def test_the_seven_files_moved():
    missing = [p.as_posix() for p in FILES if not p.is_file()]
    assert missing == []


def test_the_prose_names_no_origin_host():
    hits = [f"{p.relative_to(SKILLS).as_posix()}:{n}: {lit}"
            for p in FILES
            for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
            for lit in FORBIDDEN if lit in line]
    assert hits == [], "\n".join(hits)


def test_every_python_body_parses_and_its_acf_imports_exist():
    bodies = _python_bodies()
    assert len(bodies) >= 12  # ten fenced blocks and two python -c bodies at move time
    for where, body in bodies:
        tree = ast.parse(body)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("acf"):
                module = importlib.import_module(node.module)
                for alias in node.names:
                    assert hasattr(module, alias.name), f"{where}: {node.module}.{alias.name}"


def _calls(name: str):
    for _, body in _python_bodies():
        for node in ast.walk(ast.parse(body)):
            if isinstance(node, ast.Call) and getattr(node.func, "id", getattr(node.func, "attr", None)) == name:
                yield node


def test_host_values_are_passed_explicitly():
    for call in _calls("run_detail_path"):
        assert "runs_dir" in {k.arg for k in call.keywords}
    for fn in ("classify_citations", "unresolved_citations"):
        for call in _calls(fn):
            repo_root = {k.arg: k.value for k in call.keywords}.get("repo_root")
            assert repo_root is not None
            assert not (isinstance(repo_root, ast.Call) and getattr(repo_root.func, "id", "") == "Path")


def test_no_python_c_body_opens_a_literal_ledger_path():
    for where, body in _python_bodies():
        if not where.endswith("python -c"):
            continue
        for node in ast.walk(ast.parse(body)):
            if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "open":
                assert not (node.args and isinstance(node.args[0], ast.Constant)), where
```

- [ ] **Step 3: Run to verify it fails**

Run: `python -m pytest plugins/arch-compliance/tests/test_adr_skill_prose.py -v`
Expected: `test_the_seven_files_moved` FAILS (nothing there yet); the others FAIL or error for the same reason.

- [ ] **Step 4: Copy the seven files from the origin host**

```bash
O=C:/Users/iball/Arduino/Projects/HistoricMansions/.claude/skills
P=C:/Users/iball/Arduino/Projects/arch-compliance-for-superpowers/plugins/arch-compliance/skills
mkdir -p "$P/adversarial-design-review/claims" "$P/adversarial-design-review/reviewers" "$P/responding-to-adversarial-review"
cp "$O/adversarial-design-review/SKILL.md" "$P/adversarial-design-review/"
cp "$O/adversarial-design-review/claims/extraction.md" "$P/adversarial-design-review/claims/"
cp "$O"/adversarial-design-review/reviewers/{compliance,hardening,refuter,sweeper}.md "$P/adversarial-design-review/reviewers/"
cp "$O/responding-to-adversarial-review/SKILL.md" "$P/responding-to-adversarial-review/"
git -C C:/Users/iball/Arduino/Projects/HistoricMansions log -1 --format=%h -- .claude/skills/adversarial-design-review .claude/skills/responding-to-adversarial-review
```

Record that commit in the Task 5 commit message. If it is newer than `86f93f95`, diff the files since `86f93f95` and dispose any new host value by the rules below before continuing.

- [ ] **Step 5: Apply the edits (spec §4.2 and §4.3)**

Line numbers are the copied files' (identical to the origin at copy time). Edit bottom-up within each file so earlier line numbers stay valid.

`adversarial-design-review/SKILL.md`:

| Line(s) | Change |
|---|---|
| `:3` | "against a committed docs/design/*.md" → "against a committed spec"; "per GEMINI.md §1 item 8" → "where the host's doctrine requires it" |
| `:10-12` | "This file is the procedure. The incidents … not when running it." → "This file is the procedure." |
| `:14-18` | Delete the *Install* block and its verifier line |
| `:22` | `<docs/design/TOPIC.md>` → `<path/to/SPEC.md>` |
| Step 1 (first paragraph, `:36`) | Prepend: "**Load the host's values first.** Run the block below; it stops the run before any reviewer is dispatched if the host has no `config/architecture/adr.yml` or no `config/architecture/ARCHITECTURE.md`. Every later Python step reuses `repo` and `cfg`." followed by a ```` ```python ```` block: `from acf.repo import resolve_repo` / `from acf.adr import load_host_config` / `repo = resolve_repo(None)` / `cfg = load_host_config(repo)` |
| `:51`, `:75` | `from scripts.core.exceptions import` → `from acf.exceptions import` |
| `:69` | `from scripts.core.adversarial_design.citations import (` → `from acf.adr.citations import (` |
| `:72-73` | `repo_root=Path(".")` → `repo_root=repo` (both lines) |
| `:97` | "absolute (live book roots)" → "absolute (outside the repository)" |
| `:126`, `:131`, `:293` | `docs/reviews/adr_runs/` → "the declared `runs_dir`" (`:293`: "This lands under the declared `runs_dir` — tracked.") |
| `:160, 222, 237, 246, 258, 276, 288` | `from scripts.core.adversarial_design import` → `from acf.adr import` |
| `:163` | `spec_citation="scripts/x.py:12"` → `spec_citation="src/x.py:12"` |
| Step 5 dispatch list (the bullet "Every citation's resolved path and kind (step 2).") | Add after it: "- For the sweeper only: the directories that contain `repo / cfg.runs_dir` and `repo / cfg.ledger_path`, which it must exclude from its corpus." |
| `:289` | `run_detail_path(spec_path, version=N, date=today_iso)` → `run_detail_path(spec_path, version=N, date=today_iso, runs_dir=repo / cfg.runs_dir)` |
| `:302` | `from scripts.core.adversarial_design import LEDGER_PATH, LedgerRow, append_row` → `from acf.adr import LedgerRow, append_row` |
| `:307–319` (inside the fence) | Every `…` → `...` (§4.3) |
| `:320` | `Path(LEDGER_PATH),` → `repo / cfg.ledger_path,` |
| `:328` | `scripts.core.adversarial_design.citations` → `acf.adr.citations` |
| `:347-349` | "That list is GEMINI.md §1 item 8's future trigger list; change both together." → "Change it together with `TouchedSurface` in `acf.adr.ledger`, the persisted vocabulary it is a subset of." |
| `:361` | "amended later by `post-merge-housekeeping`" → "amended later by the host's post-merge process" |
| `:426` | Delete "(GEMINI.md §1 item 8)" |
| `:455` | Delete the sentence "See `docs/architecture/SKILL_PROVENANCE.md` (Series hygiene)." |
| `:474` | "Diagnosis lives in GEMINI.md §1 item 7, not in a third skill." → "Diagnosis belongs to the host's doctrine, not to this gate." |

`adversarial-design-review/reviewers/compliance.md`:

| Line(s) | Change |
|---|---|
| `:3` | "**GEMINI.md conformance**" → "**conformance to the host's doctrine**" |
| `:12-19` | Replace with: "The full spec text, and its `mandate`-family claims. Read `config/architecture/ARCHITECTURE.md` in full, then every document it points to — do not work from memory of them. Also read any document the spec's mandates point to." |
| `:28`, `:44`, `:127` | "GEMINI.md line" / "section of GEMINI.md" → "doctrine line" / "section of the doctrine" |
| `:36-38` | "claimed as §4-compliant" → "claimed as satisfying a no-shims rule"; "claimed as §3 fail-loud" → "claimed as fail-loud"; "claimed as §10" → "claimed as satisfying a POSIX-paths rule" |
| `:50-52` | "Walk the numbered sections of GEMINI.md" → "Walk the sections of the doctrine"; `"§N — why it governs here"` → `"<doctrine section> — why it governs here"` |
| `:54-79` | Replace the header and list with: "If the doctrine names its own high-frequency misses, check each of those first." |
| `:93` | The example "§12: no format token reaches Stage 1 in this design" → "<section>: <what you checked> — not touched by this design" |

`adversarial-design-review/claims/extraction.md:30`: "about GEMINI.md sections" → "about the host's doctrine".

`adversarial-design-review/reviewers/hardening.md`: `:62` "`book_order`" → "`position`"; `:81` "(§3)" → "(fail loud)"; `:83` "(§4)" → "(no shims)".

`adversarial-design-review/reviewers/refuter.md:74`: "anywhere under `scripts/`" → "anywhere in the tree".

`adversarial-design-review/reviewers/sweeper.md`: `:13` the corpus sentence → "Your corpus is the tracked tree — code and documents alike — **excluding** the directories the controller names as holding prior run records and the ledger; an Approved document stating a contract this design restates or contradicts is a finding."; `:35` "(§1.7: every exclusion justified)" → "(every exclusion justified)"; `:43` "Search `docs/design/` and `docs/architecture/` for Approved" → "Search the tracked documents in your corpus for Approved"; `:144` `docs/design/SOME_DOC.md` → `docs/SOME_DOC.md`.

`responding-to-adversarial-review/SKILL.md`:

| Line(s) | Change |
|---|---|
| `:13-15` | → "This file is the procedure." |
| `:17-19` | Delete the *Install* block |
| `:37` | "The pass is defined in `CLAUDE.md` (superpowers overrides)." → "Use the host's design-simplification pass, if its doctrine defines one." |
| `:49-56` and `:168-172` (`python -c` bodies) | Replace the `rows = …` line in each with three lines: `from acf.repo import resolve_repo` / `from acf.adr import load_host_config` / `repo = resolve_repo(None); cfg = load_host_config(repo)` followed by `rows = [json.loads(l) for l in open(repo / cfg.ledger_path, encoding='utf-8') if l.startswith('{')]` |
| `:91-92` | "across `scripts/`, `tests/`, `config/`, and `docs/`" → "across the tracked tree" |
| `:110`, `:201` | `docs/reviews/adr_runs/` → "the declared `runs_dir`" |
| `:196` | "`post-merge-housekeeping` owns" → "the host's post-merge process owns" |
| `:205-208` | Replace with: "Diagnosis belongs to the host's doctrine, not to this skill. Do not invent a competing owner." |
| `:222` | "GEMINI.md §1 item 7 owns diagnosis." → "The host's doctrine owns diagnosis." |
| `:224-225` | "The recorded BLOCKED responses that earned §2 and §3 are listed in `docs/architecture/SKILL_PROVENANCE.md`; GREEN is the next live re-run, not a claim this file makes." → "GREEN is the next live re-run, not a claim this file makes." |

The skill's own `§2`/`§3`/`§4` references (`:27, 81, 104, 120, 176, 189, 200`) stay.

- [ ] **Step 6: Run the tests**

Run: `python -m pytest plugins/arch-compliance/tests/test_adr_skill_prose.py -v` → all PASS.
Then read each of the seven files end to end against spec §4.2 (Risks: a host assumption neither recipe names). Fix any found; note them in the commit.
Run: `python -m pytest -q` → **394 passed**.

- [ ] **Step 7: Commit**

```bash
git add plugins/arch-compliance/skills plugins/arch-compliance/tests/test_adr_skill_prose.py
git commit -m "feat: the adversarial-design-review and responding skills move into the plugin

Copied from the origin host at <sha from Step 4> and rewritten line by line
against the spec's census: host values come from resolve_repo + adr.yml, the
doctrine from config/architecture/ARCHITECTURE.md and what it points to. A
test parses every Python body, resolves its acf imports, checks host values
are passed explicitly, and refuses origin-host literals."
```

---

### Task 6: Fixture-host acceptance

**Files:**
- Create: `plugins/arch-compliance/tests/test_adr_host_acceptance.py`

**Interfaces:**
- Consumes: Tasks 2–3.
- Produces: nothing.

- [ ] **Step 1: Branch guard** — `git branch --show-current` prints `feat/adr-host-contract`.

- [ ] **Step 2: Write the test**

Create `plugins/arch-compliance/tests/test_adr_host_acceptance.py` (inputs follow the existing helpers `_run` in `tests/test_adr_run_detail.py:38-66` and `_row` in `tests/test_adr_ledger.py:31-55`):

```python
"""A host laid out unlike the origin runs the gate's storage path end to end."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from acf.adr import (
    Claim, ClaimVerdict, DesignReviewRun, LedgerRow, UnanchoredFinding, append_row,
    classify_citations, classify_outcome, load_host_config, run_detail_path,
    write_run_detail,
)
from acf.adr.contract import RefuterPayload


def _git(repo: Path, *args: str) -> None:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           "GIT_CONFIG_NOSYSTEM": "1"}
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, env=env)


def _host(root: Path) -> Path:
    host = root / "host"
    arch = host / "config" / "architecture"
    arch.mkdir(parents=True)
    (arch / "adr.yml").write_text(
        "runs_dir: reviews/runs\nledger_path: reviews/ledger.jsonl\n", encoding="utf-8")
    (arch / "ARCHITECTURE.md").write_text("# Doctrine\n", encoding="utf-8")
    (host / "specs").mkdir()
    (host / "specs" / "THING.md").write_text("# Thing\n", encoding="utf-8")
    _git(host, "init", "-q")
    _git(host, "add", "-A")
    _git(host, "commit", "-qm", "init")
    return host


def _run():
    claims = [Claim(id="C1", family="shape_fit", statement="Extends S",
                    spec_citation="specs/THING.md:1", load_bearing=True)]
    payloads = [RefuterPayload(
        reviewer="refuter",
        claim_verdicts=[ClaimVerdict(id="C1", verdict="SURVIVED",
                                     evidence="src/s.py:3", reasoning="Opened it.")],
        unanchored_findings=[UnanchoredFinding(summary="none blocking",
                                               evidence="src/s.py:4", severity="advisory")],
        looked_for_but_did_not_find=["a second owner"],
    )]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    run = DesignReviewRun(spec_path="specs/THING.md", spec_kinds=["feature"],
                          commit_sha="b" * 40, claims=claims, payloads=payloads,
                          converged=[], outcome=result.outcome)
    return run, result


def _row() -> LedgerRow:
    return LedgerRow(
        spec_path="specs/THING.md", commit_sha="b" * 40, date="2026-10-12",
        spec_kinds=["feature"], new_design_elements=1, phases=1, cited_files=1,
        touched_surfaces=["none"], surface_call_sites=0, filter_would_skip=True,
        holdout=False, outcome="CLEARED",
        findings_by_lens_severity={"refuter": {"blocking": 0, "important": 0, "advisory": 1}},
        converged_count=0, absorbed=0, rejected=0, blocks_overturned=0,
        tokens=1, wall_clock_s=1,
    )


def test_a_non_origin_host_runs_the_storage_path(tmp_path, monkeypatch):
    host = _host(tmp_path)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)          # Review Focus 5: the process dir is not the host

    cfg = load_host_config(host)
    assert classify_citations(["specs/THING.md"], repo_root=host) == {"specs/THING.md": "current"}

    run, result = _run()
    detail = run_detail_path("specs/THING.md", version=1, date="2026-10-12",
                             runs_dir=host / cfg.runs_dir)
    write_run_detail(run, result, detail)
    assert detail.parent == host / "reviews" / "runs"
    assert detail.is_file()

    ledger = host / cfg.ledger_path
    append_row(_row(), ledger)
    lines = ledger.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2 and lines[0].startswith("{")    # preamble, then the row
    assert list(elsewhere.iterdir()) == []                  # nothing written outside the host
```

If a model rejects one of these inputs (e.g. a `findings_by_lens_severity` that must name all four reviewers), build the input the way the existing helper it is modelled on does, and keep the six assertions unchanged.

- [ ] **Step 3: Run it**

Run: `python -m pytest plugins/arch-compliance/tests/test_adr_host_acceptance.py -v`
Expected: PASS. (Written after Tasks 2–3 exist, so it is a regression pin. Falsify it once: temporarily change the `runs_dir=` argument to `runs_dir=Path("reviews/runs")` and confirm the `elsewhere` assertion FAILS; restore.) Then `python -m pytest -q` → **395 passed**.

- [ ] **Step 4: Commit**

```bash
git add plugins/arch-compliance/tests/test_adr_host_acceptance.py
git commit -m "test: a non-origin host runs the gate's storage path end to end"
```

---

### Task 7: Document the override; close the plan

**Files:**
- Modify: `README.md` (*Override contract*, `:22-25`; the `acf.adr` section)
- Modify: `docs/plans/PLAN_ADR_GATE_HOST_CONTRACT.md` (Outcome)

**Interfaces:** none.

- [ ] **Step 1: Branch guard** — `git branch --show-current` prints `feat/adr-host-contract`.

- [ ] **Step 2: README**

Append to the *Override contract* paragraph (`README.md:24`): "The `adversarial-design-review` skill is one such override: it is a gate between Superpowers' brainstorming and writing-plans steps, run where the host's doctrine requires it."

In the `acf.adr` section, replace the paragraph beginning "**The gate's skill prose is not here yet.**" with: "**The gate's skills live here too** (`skills/adversarial-design-review/`, `skills/responding-to-adversarial-review/`). A host enables them by writing `config/architecture/adr.yml` (`runs_dir`, `ledger_path`) and keeping its doctrine at `config/architecture/ARCHITECTURE.md`, which may point to other documents; a pointer still carries every heading its mandates' `arch_anchor` values name."

- [ ] **Step 3: Whole-suite gates and DoD checks**

Run: `python -m pytest -q` → all pass; record the count.
Run: `npm test --prefix plugins/arch-compliance/detectors/typescript` → `self-test OK`.
Run: `git -C C:/Users/iball/Arduino/Projects/HistoricMansions status --porcelain` → nothing from this plan (spec DoD 9).
Falsify each guard once (spec DoD 7): plant `GEMINI` in a moved file; restore. Plant `§3` in an `acf/adr` comment; restore. Remove `runs_dir=` from the `:289` call in the moved SKILL.md; restore. Each must turn its test red.

- [ ] **Step 4: Outcome and commit**

Append an `## Outcome` section to this plan: final test count, the origin commit the prose was copied from, and any host assumption found in Task 5's end-to-end read.

```bash
git add README.md docs/plans/PLAN_ADR_GATE_HOST_CONTRACT.md
git commit -m "docs: README names the gate as a Superpowers override and documents adr.yml"
```

Then push and open the PR to `main`.

---

## Definition of Done

1. `python -m pytest -q` passes; TypeScript lane prints `self-test OK`.
2. `load_host_config` refuses: absent `adr.yml`, unknown key, missing `runs_dir`, missing `ledger_path`, empty value, backslash, absent `ARCHITECTURE.md`, a subdirectory as host (Task 2).
3. `require_file` is the one owner of the doctrine refusal; the hook test's message is byte-identical (Task 1).
4. `acf.adr` exports `AdrHostConfig`, `load_host_config`; not `LEDGER_PATH`, `RUNS_DIR`; `run_detail_path` without `runs_dir` raises `TypeError` (Tasks 2–3).
5. `acf/adr/*.py` names no origin host (Task 4); recipe D1 returns only `judge.py`.
6. The seven skill files are in `plugins/arch-compliance/skills/`; their Python parses, imports resolve, host values are explicit; no forbidden literal (Task 5).
7. A non-origin fixture host runs the storage path with nothing written outside it (Task 6).
8. Each guard falsified once (Task 7 Step 3).
9. The origin repository is untouched.
10. README documents the gate as a Superpowers override and `adr.yml` (Task 7).
11. Whole-branch code review before merge (public interface change).

## Risks

| Risk | Mitigation |
|---|---|
| The origin prose changes between the spec (`86f93f95`) and Task 5's copy | Task 5 Step 4 records the copy commit and diffs from `86f93f95` |
| A host assumption no recipe names survives the move | Task 5 Step 6's end-to-end read against §4.2 |
| Task 6's helpers need richer inputs than sketched | The step says to read the two existing helpers end to end and keep the assertions |
| The hook change alters behaviour for an enabled host | Task 1 pins exit code and exact message; `test_hooks_import_repo_without_pulling_third_party` pins the pre-gate import contract |
