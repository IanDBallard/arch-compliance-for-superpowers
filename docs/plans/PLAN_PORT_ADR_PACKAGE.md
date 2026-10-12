# Port the Adversarial-Design-Review Package Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the adversarial-design-review Python package out of one host repository and into this plugin as `acf.adr`, faithfully, with its own test suite passing here and nothing about its behaviour changed.

**Architecture:** A port, not a design. Eight modules of pure logic — pydantic models, an outcome classifier, a citation resolver, a convergence grouper, a ledger writer, two renderers — arrive with 226 test functions that already pass in their origin. Two symbols they import from outside the package get rehomed into facilities this plugin already has. Nothing in the package reads a host path at import time, and nothing about running it here requires a new persisted format: the existing ledger format is kept exactly, so a host's history stays readable across the move.

**Tech Stack:** Python 3.11+, pydantic v2, pytest. No new dependency. One `package-data` entry if the prompt templates come across (Task 6 decides).

**Spec:** None, deliberately. This is phase **1b** of Workstream E in the host repository's canonical roadmap (`docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md`). That workstream records why this phase needs no adversarial review and why phase 1c does.

**Read this before starting.** A combined spec covering this port *plus* a host contract *plus* a ledger redesign was dispatched eleven times and blocked every time, at about 9M tokens and zero shipped artifacts. The decomposition that replaced it shipped three pull requests cleanly. **Do not re-expand this phase.** Specifically out of scope, and each is a later phase or a filed follow-up:

- **The host contract** — what a host declares instead of the paths the skills hardcode. Phase 1c, and it needs the gate.
- **The ledger record schema** ("v2"). Measured: the ledger module imports only stdlib, pydantic, its own package and one exception type. A new format is not required to run here. Demoted to a follow-up.
- **The host cutover** — installing the plugin in a host and deleting its local copies. Phase 1d.
- **The skill prose** (`SKILL.md`, the reviewer prompts). They still name host paths, which is exactly what 1c settles. See Task 6.

If a task seems to need any of these, stop and raise it.

## Global Constraints

- **Faithful port.** No behaviour change, no refactor, no "while I'm here". Every rename is mechanical and listed below. If a module looks improvable, file it; do not improve it in this plan.
- **Python floor `>=3.11`**, pydantic floor `>=2.0`. Both already declared; do not change either.
- **No new third-party dependency.**
- **New exception types subclass `AcfError`** in `plugins/arch-compliance/python/acf/exceptions.py`. All eleven existing classes derive from it with **no second parent** — see Task 1, which is the only real decision in this plan.
- **POSIX paths** in anything persisted (`.as_posix()`). The package already does this and has a predicate for it.
- **The persisted ledger format does not change.** Not one field name, not one default. A host's existing ledger must stay readable by the ported reader. This is what keeps 1b independent of the demoted schema work.
- **Verification** from the repository root: `python -m pytest -q`. Baseline at base commit `c043922` is **105 passed** (after `npm ci --prefix plugins/arch-compliance/detectors/typescript`). The TypeScript lane is `npm test --prefix plugins/arch-compliance/detectors/typescript`, printing `self-test OK`.

## Review Focus

Five things this port will meet that no step below would otherwise exercise.

1. **A citation that resolves against *this* repository's git history, not the origin's.** The origin's citation tests assert that one path is `current`, another `historical` (deleted but in history), another `external` (gitignored). Those verdicts are properties of *that* repository. Ported verbatim they would either fail or, worse, pass for the wrong reason. Task 5 re-bases them on a throwaway git repository built in `tmp_path`.
2. **A ledger file written by the origin, read by the ported reader.** The format must be unchanged. Task 4 pins it with a real record copied from a host ledger, not a synthesised one.
3. **An exception caught by the type the origin used.** The five rehomed types lose their stdlib second parent (Task 1), so any caller that caught `OSError` or `ValueError` rather than the ACF type changes behaviour. Task 1 enumerates every such catch before deciding.
4. **A module imported before pydantic is available.** Both hooks import `acf.repo` at module scope ahead of the enabled gate, and that contract is already pinned. Nothing in `acf.adr` may be imported from a hook, and Task 3 adds a test that the hooks' import graph still excludes it.
5. **The package's own `__init__` re-exports.** The origin's `__init__.py` is the public surface the skill prose imports from. If a name is dropped in the move, the failure appears only when a skill runs, which no test here covers. Task 3 asserts the re-export list matches.

---

## File Structure

| File | Responsibility | Task |
|---|---|---|
| `python/acf/exceptions.py` | **Modify.** Gains the five ADR exception types under `AcfError`. | 1 |
| `python/acf/engine.py` | **Modify.** Gains `contains_backslash` beside the existing `posix_path`. | 2 |
| `python/acf/adr/__init__.py` | **Create.** The package's public surface, re-exporting what the origin's `__init__` did. | 3 |
| `python/acf/adr/contract.py` | **Create.** Port. The pydantic models: `Claim`, `ReviewerPayload`, `ConvergedFinding`, the `PosixStr` predicate. 364 lines. | 3 |
| `python/acf/adr/gate.py` | **Create.** Port. `classify_outcome` and its five blocking rules. 295 lines. | 3 |
| `python/acf/adr/citations.py` | **Create.** Port. `classify_citations`, `resolve_citation`, suffix matching. 249 lines. | 3 |
| `python/acf/adr/ledger.py` | **Create.** Port. `LedgerRow`, `LedgerAmendment`, `append_row`, the preamble. 241 lines. | 3 |
| `python/acf/adr/run_detail.py` | **Create.** Port. `write_run_detail`, `run_detail_path`. 196 lines. | 3 |
| `python/acf/adr/rollup.py` | **Create.** Port. `format_rollup`. 173 lines. | 3 |
| `python/acf/adr/convergence.py` | **Create.** Port. `group_convergence_candidates`. 108 lines. | 3 |
| `python/acf/adr/parser.py` | **Create.** Port. `parse_reviewer_payload`. 98 lines. | 3 |
| `tests/test_adr_contract.py` … `tests/test_adr_rollup.py` | **Create.** Seven ported test modules, ~197 test functions. | 4 |
| `tests/test_adr_citations.py` | **Create.** Twenty tests, re-based on a fixture git repository. | 5 |
| `tests/test_adr_import_graph.py` | **Create.** The hooks must not reach `acf.adr`; the re-export list must hold. | 3 |

**Not ported:** the origin's `test_*_skill_install.py` modules (nine tests). They assert that a host's `.claude/` and `.cursor/` skill trees are byte-identical, which is a property of a host, not of this plugin. They stay where they are. Task 6 records that rather than leaving it to inference.

## Staging

| PR | Tasks | Risk | Behaviour change |
|---|---|---|---|
| **PR A** | 1, 2 | Lowest | Five exception types and one predicate added to existing modules. Nothing consumes them yet. |
| **PR B** | 3, 4 | Medium | The package arrives with 197 of its tests. Still no consumer in this repo. |
| **PR C** | 5, 6 | Medium | The citation tests, re-based; the ported surface declared complete. |

Branch each from `main` after the previous merges. Tasks 3 and 4 both create files under `acf/adr/`, and Task 5 edits a test Task 4 does not create, so the split is clean.

---

## Task 1: Rehome the five ADR exception types

**Files:**
- Modify: `plugins/arch-compliance/python/acf/exceptions.py`
- Create: `plugins/arch-compliance/tests/test_adr_exceptions.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `AcfError` subclasses `ReviewerContractViolationError`, `SpecKindUndeterminedError`, `CitationHistoryUnavailableError`, `LedgerWriteError`, `RunDetailWriteError`.

**The one real decision in this plan.** In the origin these five carry a stdlib second parent:

```python
class ReviewerContractViolationError(AdversarialDesignReviewError, ValueError): ...
class SpecKindUndeterminedError(AdversarialDesignReviewError, ValueError): ...
class CitationHistoryUnavailableError(AdversarialDesignReviewError, RuntimeError): ...
class LedgerWriteError(AdversarialDesignReviewError, OSError): ...
class RunDetailWriteError(AdversarialDesignReviewError, OSError): ...
```

Every one of this plugin's eleven exceptions derives from `AcfError` alone. **Drop the mixins**, for two reasons: the plugin's second governing principle is one way to do a thing, and a type that is both `AcfError` and `OSError` invites a caller to catch the wrong one. But dropping them is only safe if no live caller relies on the stdlib half, so **measure before deciding, not after.**

- [x] **Step 1: Measure whether any caller depends on the stdlib parent**

Run, in the origin repository (the host that currently owns the package):

```bash
grep -rnE 'except [^#]*(OSError|ValueError|RuntimeError)' \
  scripts/core/adversarial_design/ .claude/skills/adversarial-design-review/ \
  .claude/skills/responding-to-adversarial-review/
grep -rn 'AdversarialDesignReviewError' scripts/ .claude/ tests/
```

Expected: the first returns nothing inside the package, and the second returns the base class plus its five subclasses. Record both outputs in the commit message. **If a caller does catch the stdlib parent, stop and raise it** — that changes this task from a rename to a contract change, which is not what this plan authorises.

- [x] **Step 2: Write the failing test**

Create `plugins/arch-compliance/tests/test_adr_exceptions.py`:

```python
"""The ported ADR exceptions obey this plugin's single-base convention."""
from __future__ import annotations

import inspect

import pytest

from acf import exceptions as exc

ADR_TYPES = [
    "ReviewerContractViolationError",
    "SpecKindUndeterminedError",
    "CitationHistoryUnavailableError",
    "LedgerWriteError",
    "RunDetailWriteError",
]


@pytest.mark.parametrize("name", ADR_TYPES)
def test_adr_exception_exists(name: str) -> None:
    assert hasattr(exc, name), f"{name} was not rehomed into acf.exceptions"


@pytest.mark.parametrize("name", ADR_TYPES)
def test_adr_exception_derives_from_acferror_alone(name: str) -> None:
    """No stdlib second parent: the origin had mixins, this plugin does not."""
    cls = getattr(exc, name)
    assert cls.__bases__ == (exc.AcfError,), (
        f"{name} must derive from AcfError alone, got {cls.__bases__}. "
        "Every other exception in this module does."
    )


def test_every_exception_in_the_module_uses_one_base() -> None:
    """The convention this task is preserving, asserted over the whole module."""
    offenders = {}
    for name, obj in vars(exc).items():
        if not inspect.isclass(obj) or not issubclass(obj, exc.AcfError):
            continue
        if obj is exc.AcfError:
            continue
        if obj.__bases__ != (exc.AcfError,):
            offenders[name] = obj.__bases__
    assert offenders == {}, f"exceptions with a second parent: {offenders}"
```

- [x] **Step 3: Run the tests to verify they fail**

Run: `python -m pytest plugins/arch-compliance/tests/test_adr_exceptions.py -v`
Expected: the five existence tests FAIL with `AssertionError: ... was not rehomed`; `test_every_exception_in_the_module_uses_one_base` PASSES already, because it describes the convention the module currently satisfies. That pass is the guard, not a gap.

- [x] **Step 4: Add the five types**

Append to `plugins/arch-compliance/python/acf/exceptions.py`:

```python
class ReviewerContractViolationError(AcfError):
    """A reviewer payload does not satisfy the contract it was dispatched under."""


class SpecKindUndeterminedError(AcfError):
    """A spec is neither a defect nor a feature and is not declared docs/measurement."""


class CitationHistoryUnavailableError(AcfError):
    """A citation's history could not be read, so its kind cannot be decided."""


class LedgerWriteError(AcfError):
    """The efficacy ledger could not be appended to."""


class RunDetailWriteError(AcfError):
    """A run detail could not be written, so the run has no record."""
```

Do **not** port the origin's `AdversarialDesignReviewError` intermediate base. `AcfError` is this plugin's one base, and a second intermediate would be the shim principle 2 forbids. Task 3's import rewrite maps it away.

- [x] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest plugins/arch-compliance/tests/test_adr_exceptions.py -v`
Expected: 11 passed.

Run: `python -m pytest -q`
Expected: **116 passed** (105 baseline plus 11).

- [x] **Step 6: Commit**

```bash
git add plugins/arch-compliance/python/acf/exceptions.py \
        plugins/arch-compliance/tests/test_adr_exceptions.py
git commit -m "feat: rehome the five ADR exception types under AcfError

The origin gave each a stdlib second parent (ValueError, OSError,
RuntimeError). Dropped: every one of this plugin's exceptions derives
from AcfError alone, and a type that is both AcfError and OSError invites
a caller to catch the wrong one.

Measured before dropping them: no caller in the package or either skill
catches the stdlib parent. Output in the PR body.

The origin's AdversarialDesignReviewError intermediate base is NOT
ported; AcfError is this plugin's one base."
```

---

## Task 2: Absorb the backslash predicate

**Files:**
- Modify: `plugins/arch-compliance/python/acf/engine.py`
- Create: `plugins/arch-compliance/tests/test_engine_paths.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `acf.engine.contains_backslash(value: str) -> bool`.

**Why `engine.py`.** It is already this plugin's home for shared path helpers and already holds `posix_path`, which *normalizes* a backslash. The ported predicate *detects* one, for refusing rather than fixing. Those belong together, and putting the predicate anywhere else would give path-string handling a second home.

The origin's implementation is two lines. It is reproduced rather than imported because the whole point of the phase is that the package stops depending on the host.

- [x] **Step 1: Write the failing test**

Create `plugins/arch-compliance/tests/test_engine_paths.py`:

```python
"""contains_backslash detects what posix_path normalizes."""
from __future__ import annotations

import pytest

from acf.engine import contains_backslash, posix_path


@pytest.mark.parametrize(
    "value,expected",
    [
        ("scripts/core/x.py", False),
        ("", False),
        ("scripts\\core\\x.py", True),
        ("C:\\Users\\x", True),
        ("a/b\\c", True),
    ],
)
def test_contains_backslash(value: str, expected: bool) -> None:
    assert contains_backslash(value) is expected


def test_predicate_and_normalizer_agree() -> None:
    """Anything the predicate flags, the normalizer changes - and vice versa."""
    for value in ("a/b", "a\\b", "", "a\\b/c"):
        assert contains_backslash(value) == (posix_path(value) != value)
```

- [x] **Step 2: Run to verify it fails**

Run: `python -m pytest plugins/arch-compliance/tests/test_engine_paths.py -v`
Expected: collection FAILS with `ImportError: cannot import name 'contains_backslash' from 'acf.engine'`.

- [x] **Step 3: Add the predicate**

Add to `plugins/arch-compliance/python/acf/engine.py`, directly after `posix_path`:

```python
def contains_backslash(value: str) -> bool:
    """True if ``value`` carries a platform-native separator.

    The refusing counterpart to ``posix_path``: this detects, that normalizes.
    Persisted paths are refused rather than silently fixed, so a producer
    writing a Windows path learns about it.
    """
    return "\\" in value
```

- [x] **Step 4: Run to verify it passes**

Run: `python -m pytest plugins/arch-compliance/tests/test_engine_paths.py -v`
Expected: 6 passed.

Run: `python -m pytest -q`
Expected: **122 passed**.

- [x] **Step 5: Commit, then open PR A**

```bash
git add plugins/arch-compliance/python/acf/engine.py \
        plugins/arch-compliance/tests/test_engine_paths.py
git commit -m "feat: contains_backslash beside posix_path in acf.engine

The refusing counterpart to the existing normalizer, and the second of
the two symbols the ADR package imported from its origin host. Two
lines, reproduced rather than imported: the point of the port is that
the package stops depending on a host."
```

```bash
npm test --prefix plugins/arch-compliance/detectors/typescript
python -m pytest -q
git push -u origin feat/port-adr-package
gh pr create --title "Port groundwork: ADR exception types and the backslash predicate" --body "First of three. Adds the two things the ADR package imported from outside itself, so the package itself can arrive with no host dependency. Nothing consumes them yet. Suite 105 to 122. See docs/plans/PLAN_PORT_ADR_PACKAGE.md."
```

---

## Task 3: Port the eight modules

**Files:**
- Create: `plugins/arch-compliance/python/acf/adr/__init__.py` and the eight modules listed in File Structure
- Create: `plugins/arch-compliance/tests/test_adr_import_graph.py`

**Interfaces:**
- Consumes: the five exception types (Task 1) and `contains_backslash` (Task 2).
- Produces: the `acf.adr` package, whose public surface is whatever the origin's `__init__.py` re-exported.

**The import rewrite is mechanical and exhaustive.** Exactly these substitutions, and no others:

| Origin | Ported |
|---|---|
| `from scripts.core.adversarial_design.<m> import` | `from acf.adr.<m> import` |
| `from scripts.core.exceptions import <the five>` | `from acf.exceptions import <the five>` |
| `from scripts.schemas.types import contains_backslash` | `from acf.engine import contains_backslash` |
| `AdversarialDesignReviewError` | *(delete; it was only a base)* |

Any other `from scripts.` import is a dependency this plan did not measure. **If you find one, stop** — the measurement said there were exactly two external symbols, and a third means the measurement was wrong.

- [x] **Step 1: Copy the modules and apply the rewrite**

From the origin repository, copy the nine files (`__init__.py` plus eight modules) into `plugins/arch-compliance/python/acf/adr/`. Then apply the table above. Verify the result has no host import left:

```bash
grep -rn '^from scripts\|^import scripts\|AdversarialDesignReviewError' \
  plugins/arch-compliance/python/acf/adr/
```

Expected: no output. If anything prints, it is either a missed rewrite or the third dependency that stops this task.

- [x] **Step 2: Write the import-graph and surface test**

Create `plugins/arch-compliance/tests/test_adr_import_graph.py`:

```python
"""acf.adr is importable here, carries its public surface, and stays out of the hooks."""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
ADR = PLUGIN_ROOT / "python" / "acf" / "adr"

# The names the origin's __init__ re-exported. The skill prose imports from this
# surface, so a dropped name fails only when a skill runs - which no test covers.
EXPECTED_SURFACE = {
    "Claim",
    "ConvergedFinding",
    "DesignReviewRun",
    "LedgerRow",
    "LEDGER_PATH",
    "append_row",
    "classify_outcome",
    "format_rollup",
    "group_convergence_candidates",
    "parse_reviewer_payload",
    "run_detail_path",
    "write_run_detail",
}


def test_public_surface_is_complete() -> None:
    import acf.adr as adr

    missing = sorted(n for n in EXPECTED_SURFACE if not hasattr(adr, n))
    assert not missing, (
        f"acf.adr dropped these re-exports in the port: {missing}. The skill "
        "prose imports from this surface, so the failure would not appear here."
    )


def test_no_adr_module_imports_a_host() -> None:
    offenders = {}
    for path in sorted(ADR.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            mod = None
            if isinstance(node, ast.ImportFrom):
                mod = node.module or ""
            elif isinstance(node, ast.Import):
                mod = node.names[0].name
            if mod and mod.split(".")[0] == "scripts":
                offenders.setdefault(path.name, []).append(mod)
    assert offenders == {}, f"acf.adr still imports from a host: {offenders}"


def test_hooks_do_not_reach_acf_adr() -> None:
    """Both hooks import acf.repo at module scope, before any third party is
    available. acf.adr pulls in pydantic, so it must never enter that graph.
    """
    for hook in ("inject_constraints.py", "posttooluse_gate.py"):
        src = (PLUGIN_ROOT / "hooks" / hook).read_text(encoding="utf-8")
        assert "acf.adr" not in src, f"{hook} must not reference acf.adr"


def test_acf_repo_still_imports_without_pydantic(tmp_path) -> None:
    """The pre-gate import contract is unchanged by this package arriving."""
    import os

    poison = tmp_path / "poison"
    poison.mkdir()
    for name in ("pydantic.py", "yaml.py"):
        (poison / name).write_text("raise ImportError('poisoned')\n", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, "-c", "import acf.repo; print('ok')"],
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "PYTHONPATH": os.pathsep.join(
                [str(poison), str(PLUGIN_ROOT / "python")]
            ),
            "PYTHONIOENCODING": "utf-8",
        },
    )
    assert proc.returncode == 0, proc.stderr
    assert "ok" in proc.stdout
```

Before running, open the origin's `__init__.py` and replace `EXPECTED_SURFACE` with its **actual** `__all__` or re-export list. Do not trust the list above; it is a starting point written from the skill's import sites, not from the file.

- [x] **Step 3: Run to verify the surface test fails for the right reason, then passes**

Run: `python -m pytest plugins/arch-compliance/tests/test_adr_import_graph.py -v`

If `test_public_surface_is_complete` fails, a name was dropped in the copy — fix the port, not the test. The other three should pass immediately; they are regression guards for properties the copy must not break.

- [x] **Step 4: Run the whole suite**

Run: `python -m pytest -q`
Expected: **126 passed** (122 after PR A, plus 4).

- [x] **Step 5: Commit**

```bash
git add plugins/arch-compliance/python/acf/adr plugins/arch-compliance/tests/test_adr_import_graph.py
git commit -m "feat: port the adversarial-design-review package as acf.adr

Eight modules of pure logic, 1,792 lines, copied faithfully with a
mechanical import rewrite and no behaviour change. The origin's
AdversarialDesignReviewError intermediate base is dropped; the five
subclasses now derive from AcfError.

The persisted ledger format is unchanged - not one field name - so a
host's existing ledger stays readable. That is what keeps this port
independent of the ledger-schema work, which is a filed follow-up and
not required to run here.

Guards added: no module imports a host, the public re-export surface is
complete, neither hook reaches acf.adr, and acf.repo still imports with
pydantic poisoned."
```

---

## Task 4: Port the seven portable test modules

**Files:**
- Create: `tests/test_adr_contract.py`, `test_adr_gate.py`, `test_adr_ledger.py`, `test_adr_parser.py`, `test_adr_rollup.py`, `test_adr_run_detail.py`, `test_adr_convergence.py`

**Interfaces:**
- Consumes: `acf.adr` (Task 3).
- Produces: nothing other tasks consume.

These seven carry about **197 test functions** and use only pytest builtins — `tmp_path`, `monkeypatch`, and `parametrize`. Measured in the origin: **no ADR test uses any fixture from that repository's `conftest.py`.** That is why they port by copy plus the same import rewrite.

The eighth module, the citation tests, is Task 5 because its assertions are about a specific repository's git history.

- [x] **Step 1: Copy and rewrite**

Copy the seven files, apply the Task 3 import table, and rename each to `test_adr_<module>.py`.

- [x] **Step 2: Run them and read every failure**

Run: `python -m pytest plugins/arch-compliance/tests/test_adr_*.py -q`

Expected: all pass. **Any failure is information about the port, not a licence to edit the test.** Triage by cause:

- An `ImportError` means a missed rewrite. Fix the import.
- A failure naming a host path means the test was not as portable as measured. Stop and report it; do not delete the assertion.
- A failure about a pydantic message means a version difference. Record the actual message and the pydantic version; do not loosen the assertion to match.

- [x] **Step 3: Pin the ledger format against a real host record**

The Review Focus names this: the format must be readable, and a synthesised record would not prove it. Append to `tests/test_adr_ledger.py`:

```python
def test_a_real_host_ledger_record_still_validates(tmp_path):
    """A record written by the origin, before the port, must still load.

    Copied verbatim from a host ledger. If this fails, the port changed the
    persisted format, which this plan forbids.
    """
    from acf.adr.ledger import LedgerRow

    row = {
        # PASTE a real non-preamble line from a host's
        # docs/reviews/adversarial_design_ledger.jsonl here, verbatim.
    }
    assert row, "paste a real record before running this"
    parsed = LedgerRow.model_validate(row)
    assert parsed.spec_path
    assert parsed.outcome
```

Paste a real row before running it. The empty-dict assertion makes an unfilled test fail loudly rather than pass vacuously.

- [x] **Step 4: Run the whole suite**

Run: `python -m pytest -q`
Expected: about **324 passed** (126 after Task 3, plus roughly 197 ported plus the format pin). Record the exact number in the commit; this plan does not predict it precisely because parametrize expansion is counted by pytest, not by me.

- [x] **Step 5: Commit, then open PR B**

```bash
git add plugins/arch-compliance/tests/
git commit -m "test: port the ADR package's seven portable test modules

About 197 test functions, copied with the same mechanical import
rewrite. They use only pytest builtins - measured in the origin: no ADR
test uses any fixture from that repository's conftest.

Adds a format pin: a real ledger record written by the origin, before
the port, must still validate. A synthesised record would not prove the
persisted format survived."
```

---

## Task 5: Re-base the citation tests on a fixture repository

**Files:**
- Create: `plugins/arch-compliance/tests/test_adr_citations.py`

**Interfaces:**
- Consumes: `acf.adr.citations` (Task 3).
- Produces: nothing.

**Why these twenty cannot be copied.** The origin's citation tests assert that one path is `current`, another `historical` (deleted, but present in git history), another `external` (gitignored or absolute). Every one of those verdicts is a fact about *that* repository. Ported verbatim they would fail — or, worse, pass because some unrelated path in this repository happens to match, which is the unfalsifiable-test failure mode.

Re-basing them on a repository this test builds is strictly better than the originals: the fixture states the git history the assertions need, instead of inheriting it.

- [x] **Step 1: Write the fixture**

Create `plugins/arch-compliance/tests/test_adr_citations.py`:

```python
"""Citation classification, against a git history this test builds.

The origin's version of these tests asserted verdicts about its own tracked
files, deleted files and ignored paths. Those are facts about one repository.
Here the history is constructed, so each assertion states the condition it
depends on.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from acf.adr.citations import classify_citation


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        env={
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@t",
            "PATH": __import__("os").environ.get("PATH", ""),
        },
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A repository with one tracked file, one deleted-but-in-history file,
    and one ignored path."""
    r = tmp_path / "host"
    (r / "src").mkdir(parents=True)
    _git(r, "init", "-q")
    (r / ".gitignore").write_text("build/\n", encoding="utf-8")
    (r / "src" / "live.py").write_text("x = 1\n", encoding="utf-8")
    (r / "src" / "gone.py").write_text("y = 2\n", encoding="utf-8")
    _git(r, "add", "-A")
    _git(r, "commit", "-qm", "both files")
    (r / "src" / "gone.py").unlink()
    _git(r, "add", "-A")
    _git(r, "commit", "-qm", "delete one")
    (r / "build").mkdir()
    (r / "build" / "out.md").write_text("built\n", encoding="utf-8")
    return r


def test_a_tracked_file_is_current(repo: Path) -> None:
    assert classify_citation("src/live.py", repo_root=repo) == "current"


def test_a_line_reference_is_stripped_before_resolution(repo: Path) -> None:
    assert classify_citation("src/live.py:10", repo_root=repo) == "current"
    assert classify_citation("src/live.py:10-20", repo_root=repo) == "current"


def test_a_deleted_file_still_in_history_is_historical(repo: Path) -> None:
    assert classify_citation("src/gone.py", repo_root=repo) == "historical"


def test_an_ignored_path_is_external(repo: Path) -> None:
    assert classify_citation("build/out.md", repo_root=repo) == "external"


def test_an_absolute_path_is_external(repo: Path) -> None:
    assert classify_citation("C:/elsewhere/x.md", repo_root=repo) == "external"


def test_a_declared_proposed_path_is_proposed(repo: Path) -> None:
    proposed = {"src/not_yet.py"}
    assert (
        classify_citation("src/not_yet.py", repo_root=repo, proposed=proposed)
        == "proposed"
    )


def test_an_unknown_path_is_unresolved(repo: Path) -> None:
    assert classify_citation("src/never_existed.py", repo_root=repo) == "unresolved"
```

Open the origin's twenty tests and port every behaviour they cover, not only the seven shapes above. The seven are the skeleton; the origin also covers suffix matching, bare basenames, and the `asserted_absent` kind. **Each ported case keeps its original intent and gains an explicit fixture condition.**

- [x] **Step 2: Run and compare coverage against the origin**

Run: `python -m pytest plugins/arch-compliance/tests/test_adr_citations.py -v`

Then confirm nothing was lost:

```bash
# in the origin repo
grep -c '^def test_' tests/test_adversarial_design_citations.py   # expect 20
# here
grep -c '^def test_' plugins/arch-compliance/tests/test_adr_citations.py
```

If the second number is lower, name which origin behaviours are unported and why, in the commit message. A silently smaller suite is the failure this task exists to avoid.

- [x] **Step 3: Prove the fixture is load-bearing**

A fixture-based test can pass for the wrong reason if the fixture does not actually create the condition. Falsify it: temporarily change the `historical` test to cite `src/live.py` and confirm it fails; change the `external` test to cite `src/live.py` and confirm it fails. Restore both. Record that you did it.

- [x] **Step 4: Run the whole suite and commit**

Run: `python -m pytest -q`

```bash
git add plugins/arch-compliance/tests/test_adr_citations.py
git commit -m "test: re-base the ADR citation tests on a constructed git history

The origin's twenty asserted verdicts about its own tracked, deleted and
ignored paths - facts about one repository, which cannot travel. Ported
verbatim they would fail, or pass because an unrelated path here happens
to match, which is worse.

The fixture builds a repository with one tracked file, one
deleted-but-in-history file and one ignored path, so every assertion
states the condition it depends on. Falsified: the historical and
external cases fail when pointed at the tracked file."
```

---

## Task 6: Declare what did not come, and why

**Files:**
- Modify: `plugins/arch-compliance/README.md`
- Modify: `docs/plans/PLAN_PORT_ADR_PACKAGE.md` (this file — record the outcome)

**Interfaces:** none.

A port is finished when what *stayed* is as clear as what moved. Two things stayed, and both must be recorded rather than inferred from absence.

- [x] **Step 1: Record the skill prose as out of scope**

The gate's `SKILL.md` and its four reviewer prompts still live in the origin host, and they still name host paths — a spec directory, a reviews directory, a mandate document. That is phase 1c's subject, not this plan's. Add to `README.md`, under whatever section describes the plugin's Python surface:

```markdown
### `acf.adr` — the adversarial-design-review gate

The gate's Python package lives here: claim and payload models, outcome
classification, citation resolution, convergence grouping, the efficacy ledger
and the run-detail writer. The persisted ledger format is the one a host
already has, so an existing ledger stays readable.

**The gate's skill prose is not here yet.** `SKILL.md` and the four reviewer
prompts still live in the host that owns them, because they name host paths —
a spec directory, a reviews directory, a mandate document. Giving a host a way
to *declare* those instead is the next phase of this work; until then this
package is the portable half and the prose is not.
```

- [x] **Step 2: Record the nine skill-install tests as deliberately unported**

They assert that a host's `.claude/` and `.cursor/` skill trees are byte-identical. That is a property of a host, not of this plugin, and it has no meaning here until the skills themselves move. Note it in the same README section in one sentence, so a later reader does not "restore" them.

- [x] **Step 3: Run the whole suite, commit, open PR C**

```bash
npm test --prefix plugins/arch-compliance/detectors/typescript
python -m pytest -q
git add -A
git commit -m "docs: record what the port deliberately left behind

The gate's skill prose and the dual-tree install tests stayed in the
origin host: the prose names host paths, which the next phase settles,
and the install tests assert a property of a host, not of this plugin.
Recorded so a later reader does not restore them by mistake."
```

---

## Definition of Done

1. `python -m pytest -q` passes from the repository root, at the count Task 4 recorded, with the TypeScript lane printing `self-test OK`.
2. `grep -rn '^from scripts\|^import scripts' plugins/arch-compliance/python/acf/adr/` returns nothing.
3. `grep -rn 'AdversarialDesignReviewError' plugins/` returns nothing.
4. `acf.adr`'s public re-export surface matches the origin's, asserted by test, not by eye.
5. Neither hook references `acf.adr`, and `import acf.repo` still succeeds with pydantic and yaml poisoned.
6. A real ledger record written before the port validates against the ported `LedgerRow`.
7. The citation tests build their own git history, and the `historical` and `external` cases have been shown to fail when pointed at a tracked file.
8. No change to `[project.dependencies]`. Confirm with `git diff c043922 -- pyproject.toml`.
9. The origin repository is **untouched** by this plan. Confirm with `git -C <origin> status --porcelain`, which must be empty. The cutover is phase 1d.
10. `README.md` records both the skill prose and the install tests as deliberately absent.

## Risks

| Risk | Mitigation |
|---|---|
| A third host dependency exists that the measurement missed. | Task 3 Step 1 greps for it and stops the task. The measurement found exactly two; a third means the measurement was wrong and the plan needs revising, not working around. |
| A ported test fails for a pydantic version difference and gets loosened to pass. | Task 4 Step 2 names this explicitly: record the message and version, do not loosen. |
| The citation tests lose coverage in the re-basing. | Task 5 Step 2 counts both suites and requires naming any unported behaviour in the commit. |
| Two copies of the package now exist, and they drift. | Real, and the reason phase 1d should follow promptly. The ported copy has **no consumer** in this plugin, so it cannot drift *in behaviour* — only in code. The objective's "never two live copies" holds: only one is live. |
| The ledger format changes by accident during the copy. | Definition of Done item 6 pins it with a real record, and the Global Constraints forbid touching it. |

## Outcome (2026-10-12)

All six tasks complete; every Definition of Done item verified by command. Suite **105 → 365 passed**; TypeScript lane `self-test OK`.

| PR | Branch | Tasks | Suite after |
|---|---|---|---|
| #7 | `feat/port-adr-package` | 1, 2 | 122 |
| #8 | `feat/port-adr-package-b` (stacked on #7) | 3, 4 | 345 |
| PR C | `feat/port-adr-package-c` (stacked on #8) | 5, 6 | 365 |

PRs B and C are stacked rather than branched from `main` after each merge, because merging is the owner's call; retarget each to `main` as its parent merges.

What the plan did not predict, each a recorded ruling in the execution ledger:

- **The public surface is 25 names**, not the 12 listed in Task 3. The test asserts the origin's `__all__` verbatim, and equality rather than containment.
- **Two host-relative defaults travel with the package**: `LEDGER_PATH` and `RUNS_DIR`. They are overridable arguments, not import-time reads, and are among the values the host contract replaces. Ported verbatim, as a faithful port must.
- **A sixth origin exception, `UnresolvableCitationError`, is not ported.** It is raised by the skill prose and nowhere in the package, so here it would be an export with no consumer. It arrives with the prose.
- **Task 5's skeleton fixture would have failed.** It created the ignored file on disk, but the classifier tests existence before the ignore check, so an ignored file that exists is `current`. In the origin the cited build file is absent; the fixture now matches.
- **Measured beyond the plan's pins:** test count parity with the origin (218 = 218 for the seven modules, 20 = 20 for citations); no `pytest.raises` target depends on a dropped stdlib parent; all 329 rows of the origin's ledger classify identically under origin and ported models (231 rows / 86 amendments / 12 legacy rows that validate under neither, a pre-existing condition).
