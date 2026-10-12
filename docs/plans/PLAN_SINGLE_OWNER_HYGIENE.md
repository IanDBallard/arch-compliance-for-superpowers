# Single-Owner Hygiene Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give each of five duplicated responsibilities in this plugin exactly one owner, and turn one silent fallback into a refusal, without adding any new capability.

**Architecture:** Five independent consolidations of code that already exists. A new stdlib-only `acf.repo` module owns the host path constants both hooks currently declare twice. A new `load_model_file` absorbs the two Pydantic file loaders, taking the stricter error handling of each. `run_git` exposes a completed process while `_git` stays its raise-on-non-zero wrapper. `render_template` becomes the one placeholder substituter, called by the constraints hook and by the judge. The constraints hook stops substituting prose for a missing doctrine document and exits naming it instead. No new commands, no new configuration, no new file formats.

**Tech Stack:** Python 3.11+, Pydantic v2, PyYAML, pytest. No new dependencies. No packaging changes.

**Spec:** `docs/plans/PLAN_SINGLE_OWNER_HYGIENE.md` is self-contained. Design provenance is section 5(a) and section 6.1 of `docs/design/ADR_GATE_PLUGIN_COMPONENT.md` in the `HistoricMansionsV3` repository.

**Read this before starting.** That source spec is **BLOCKED** and is not an approved design. This plan deliberately implements only the subset of it whose claims survived three independent blind adversarial reviews without ever drawing an adverse verdict. The parts of that spec which were refuted (the adversarial-review gate itself, the `acf.yml` host configuration, the `doctrine` document list, the mandate-anchor rewrite, and the run ledger and its manifest) are **out of scope here and must not be implemented by this plan.** If a task seems to need any of them, stop and raise it rather than reaching for them.

## Global Constraints

- **Python floor is `>=3.11`** and the Pydantic floor is `>=2.0`. Both are already declared in `pyproject.toml`; do not change either.
- **No new third-party dependency, and no change to `[tool.setuptools.packages.find]` or any packaging table.** Every template this plan introduces is read relative to `Path(__file__)`, which is the precedent already in the tree at `hooks/inject_constraints.py:32`.
- **Both hooks must stay a true no-op with no third-party import** when `.acf/enabled` is absent. `acf.repo` may be imported at module scope **only because it imports nothing but `pathlib`.** Any import of `pydantic`, `yaml`, or any other third-party package must stay deferred inside `main()`. `plugins/arch-compliance/python/acf/__init__.py` is empty (0 bytes) and must stay empty.
- **New exception types subclass `AcfError`** in `plugins/arch-compliance/python/acf/exceptions.py`, with no second base class. Every one of the nine existing subclasses is declared `(AcfError)` alone; match that.
- **Error messages render paths with `.as_posix()`.** This is the plugin's third governing principle and every current raise already does it.
- **Fail loud.** No bare `except:`, no silent `None` default, no substituted prose standing in for a file that is missing. The plugin's first governing principle is `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:47`.
- **Verification command for every task** is run from the repository root: `python -m pytest -q`. The green baseline at base commit `c63cb70` is **77 passed**. The TypeScript lane is `npm test --prefix plugins/arch-compliance/detectors/typescript` and prints `self-test OK`. The Python suite needs `npm ci --prefix plugins/arch-compliance/detectors/typescript` to have been run once, or four TypeScript bridge tests fail for want of `node_modules`.

## Review Focus

Five input classes this consolidation will meet that no task below would otherwise exercise. Each one has a test assigned to the task that owns the code.

1. **An unreadable mandates file** (exists, but the read raises `OSError`). Today it escapes `load_mandates` as a bare `OSError`, because `registry.py:44-47` catches only `yaml.YAMLError`. A caller that catches the plugin's own error type never sees it. After Task 3 it must be one `AcfInputError` naming the path. Test lands in Task 3.
2. **A mandates file whose YAML root is a mapping rather than a list.** Already refused at `registry.py:48-49`; the merge must not lose that refusal, and the message must still name the path. Test lands in Task 3.
3. **A host that is enabled, has a mandates file, and has no doctrine document.** This is the exact case Task 4 changes from silent substitution to a refusal, and the current suite has no test for it at all. Test lands in Task 4.
4. **A template whose text contains a placeholder the mapping cannot fill, and a mapping carrying a key the text never uses.** `str.replace` is silent in both directions today, so a renaming typo ships a prompt with a literal `{{TOKEN}}` in it. Test lands in Task 5.
5. **`run_git` pointed at a directory that is not a git repository.** The existing wrapper must keep raising `GitError`, and the new raw accessor must report the non-zero status as data without raising. Test lands in Task 2.

---

## File Structure

| File | Responsibility | Task |
|---|---|---|
| `plugins/arch-compliance/python/acf/repo.py` | **Create.** Stdlib-only. The one declaration of the host config directory, the three host-relative paths, and host-root resolution. | 1 |
| `plugins/arch-compliance/tests/test_repo_paths.py` | **Create.** Pins single ownership by recipe, not by eye. | 1 |
| `plugins/arch-compliance/hooks/inject_constraints.py` | **Modify.** Drops its four path constants; imports `acf.repo` at module scope. Later drops the silent doctrine substitute and calls the shared renderer. | 1, 4, 5 |
| `plugins/arch-compliance/hooks/posttooluse_gate.py` | **Modify.** Drops its two duplicate path constants. | 1 |
| `plugins/arch-compliance/python/acf/cli_check_diff.py` | **Modify.** Uses `acf.repo` instead of an inline path literal; catches the new input error. | 1, 3 |
| `plugins/arch-compliance/python/acf/cli_check_llm.py` | **Modify.** Same. | 1, 3 |
| `plugins/arch-compliance/python/acf/diff.py` | **Modify.** Adds `run_git`; `_git` becomes its wrapper. | 2 |
| `plugins/arch-compliance/tests/test_diff_cli.py` | **Modify.** Adds the raw-accessor tests; updates the registry error-message assertion. | 2, 3 |
| `plugins/arch-compliance/python/acf/loader.py` | **Create.** The one load-parse-validate-refuse implementation. | 3 |
| `plugins/arch-compliance/tests/test_loader.py` | **Create.** Covers both formats, both root cardinalities, and both strictness axes. | 3 |
| `plugins/arch-compliance/python/acf/exceptions.py` | **Modify.** Adds `AcfInputError`; removes `RegistryLoadError`. | 3 |
| `plugins/arch-compliance/python/acf/registry.py` | **Modify.** `load_mandates` becomes a caller; keeps only the known-detectors check. | 3 |
| `plugins/arch-compliance/python/acf/baseline.py` | **Modify.** `load_baseline` becomes a caller; `BaselineError` keeps only its write-side raise. | 3 |
| `plugins/arch-compliance/tests/test_baseline.py` | **Modify.** Read-side expectations move to `AcfInputError`; adds the first test for the surviving write-side raise. | 3 |
| `plugins/arch-compliance/tests/test_registry.py` | **Modify.** Expectations move to `AcfInputError`. | 3 |
| `plugins/arch-compliance/tests/test_hooks.py` | **Modify.** Adds the missing-doctrine refusal test and the gate's own missing-registry test. | 4 |
| `plugins/arch-compliance/python/acf/template.py` | **Create.** `render_template` plus its strict token check. | 5 |
| `plugins/arch-compliance/tests/test_template.py` | **Create.** Both silent failure modes become loud. | 5 |
| `plugins/arch-compliance/python/acf/judge_prompt.md` | **Create.** The judge skeleton, lifted verbatim out of the f-string. | 5 |
| `plugins/arch-compliance/python/acf/judge.py` | **Modify.** `_build_prompt` becomes a caller of `render_template`. | 5 |
| `plugins/arch-compliance/tests/test_judge.py` | **Leave unchanged.** It exists but asserts no prompt text; its only prompt-adjacent test is `test_llm_prompt_ids_exported`. Verified at base commit. | 5 |
| `skills/acf-setup/SKILL.md`, `skills/acf-mandate/SKILL.md`, `skills/architecture-review/SKILL.md` | **Modify.** Four prose lines name a deleted exception. | 3 |

## Staging

Three pull requests, in increasing risk order. Do not open the next until the previous merges.

| PR | Tasks | Risk | Behaviour change |
|---|---|---|---|
| **PR 1** `feat/single-owner-hygiene` | 1, 2 | Lowest | None. Pure consolidation; every message and exception type is unchanged. |
| **PR 2** `feat/one-file-loader` | 3, 4 | Medium | Error types and two operator messages change; one silent fallback becomes a refusal. |
| **PR 3** `feat/one-template-renderer` | 5 | Medium | A template typo becomes an exception instead of a literal token in output. |

Branch PR 2 from `main` after PR 1 merges, and PR 3 from `main` after PR 2 merges. Tasks 3 and 5 both touch `inject_constraints.py`, so serialising avoids a conflict you would otherwise have to resolve twice.

---

## Task 1: One owner for the host paths

**Files:**
- Create: `plugins/arch-compliance/python/acf/repo.py`
- Create: `plugins/arch-compliance/tests/test_repo_paths.py`
- Modify: `plugins/arch-compliance/hooks/inject_constraints.py:32-36` (constants), `:79`, `:157`, `:164`
- Modify: `plugins/arch-compliance/hooks/posttooluse_gate.py:32-33`
- Modify: `plugins/arch-compliance/python/acf/cli_check_diff.py:67`
- Modify: `plugins/arch-compliance/python/acf/cli_check_llm.py:39`

**Interfaces:**
- Consumes: nothing.
- Produces: module `acf.repo` exporting `CONFIG_DIR: Path`, `MANDATES_REL: Path`, `ARCH_REL: Path`, `RATCHET_BASELINE_REL: Path`, `ENABLED_REL: Path`, and `resolve_repo(explicit: Path | None, stdin_cwd: str | None) -> Path`.

**The census is eleven lines and they are not all the same kind.** Run `grep -rnE 'config.{0,6}architecture' python hooks` from `plugins/arch-compliance` before you start. You will get these eleven, and the plan disposes of each by kind rather than treating them as one population:

| Site | Kind | Disposition |
|---|---|---|
| `inject_constraints.py:33`, `:34` | Path construction | Deleted; import from `acf.repo` |
| `posttooluse_gate.py:32` | Path construction | Deleted; import from `acf.repo` |
| `cli_check_diff.py:67` | Path construction | Replaced with `repo / MANDATES_REL` |
| `cli_check_llm.py:39` | Path construction | Replaced with `resolve_repo(None) / MANDATES_REL` |
| `cli_check_diff.py:171` | **A different artifact**: a string default for the ratchet baseline, `config/architecture/fail_loud_ratchet.json` | Replaced with `RATCHET_BASELINE_REL.as_posix()`, a new constant |
| `cli_check_diff.py:53`, `cli_check_llm.py:27` | `argparse` help text for a human | **Kept.** Allowlisted in the test with a reason |
| `inject_constraints.py:11`, `posttooluse_gate.py:11` | Module docstring describing behaviour | **Kept.** Allowlisted in the test with a reason |

A twelfth match, `hooks/constraints_template.md:20`, is injected prose telling a subagent which host file to re-read. It is not Python and the test does not scan it. Leave it.

**The test allowlists by line, with reasons, rather than claiming a universal.** A test that asserts "this pattern appears only in `repo.py`" is false the moment someone writes a legitimate help string, and the pressure is then to weaken the test. An explicit per-site allowlist makes a genuinely new duplicate fail while letting documentation say what it needs to.

**Why this is safe at module scope.** `acf/__init__.py` is 0 bytes and `repo.py` imports only `pathlib`, so importing `acf.repo` before the `.acf/enabled` gate pulls in no third-party package. Both hooks already insert `plugins/arch-compliance/python` at `sys.path[0]` at module scope, computed from `__file__` (`inject_constraints.py:22-26`, `posttooluse_gate.py:22-26`), so the import resolves inside the plugin checkout regardless of the host's interpreter.

- [ ] **Step 1: Write the failing test**

Create `plugins/arch-compliance/tests/test_repo_paths.py`:

```python
"""The host config directory is declared once, and the hooks stay import-light."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
PYTHON_ROOT = PLUGIN_ROOT / "python"
HOOKS = PLUGIN_ROOT / "hooks"

# Matches both spellings: the string literal and the Path-segment form.
CONFIG_ARCH_RE = re.compile(r"config.{0,6}architecture")


def _tracked_py_files() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "python", "hooks"],
        cwd=PLUGIN_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [PLUGIN_ROOT / line for line in out.splitlines() if line.endswith(".py")]


# Sites that may name the host config directory for a human to read. Each
# entry is a disposition, not a blanket exemption: a NEW line in one of these
# files still fails, because the allowlist is keyed by exact text.
ALLOWED_DOC_LINES = {
    # argparse help: tells an operator what the default is. A constant name
    # would be useless to someone reading --help.
    "python/acf/cli_check_diff.py": {
        "help=\"Path to mandates.yml (default: <repo>/config/architecture/mandates.yml)\","
    },
    "python/acf/cli_check_llm.py": {
        "help=\"Path to mandates.yml (default: config/architecture/mandates.yml under cwd)\","
    },
    # Module docstrings describing the hook's own contract.
    "hooks/inject_constraints.py": {
        "- If enabled and ``config/architecture/mandates.yml`` is missing: non-zero exit."
    },
    "hooks/posttooluse_gate.py": {
        "- If enabled and ``config/architecture/mandates.yml`` is missing: non-zero exit."
    },
}


def test_host_config_dir_has_one_code_owner() -> None:
    """Every executable spelling lives in acf/repo.py; prose is allowlisted."""
    offenders: dict[str, list[str]] = {}
    for path in _tracked_py_files():
        if path.name == "repo.py":
            continue
        rel = path.relative_to(PLUGIN_ROOT).as_posix()
        allowed = ALLOWED_DOC_LINES.get(rel, set())
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if not CONFIG_ARCH_RE.search(stripped):
                continue
            if stripped.startswith("#") or stripped in allowed:
                continue
            offenders.setdefault(rel, []).append(f"{lineno}: {stripped}")
    assert offenders == {}, (
        "the host config directory is spelled outside acf/repo.py. Either route "
        f"it through a repo.py constant or add it to ALLOWED_DOC_LINES: {offenders}"
    )


def test_repo_module_imports_only_stdlib() -> None:
    source = (PYTHON_ROOT / "acf" / "repo.py").read_text(encoding="utf-8")
    imports = re.findall(r"^\s*(?:from|import)\s+([A-Za-z_][\w.]*)", source, re.M)
    allowed = {"__future__", "pathlib"}
    assert set(imports) <= allowed, f"acf.repo must stay stdlib-only, got {imports}"


def test_hooks_import_repo_without_pulling_third_party(tmp_path) -> None:
    """A marker-less host must still exit 0 with pydantic and yaml poisoned.

    The poison modules go in tmp_path, never inside the repository: a file
    named pydantic.py under tests/ would shadow the real package for any other
    run that happens to put tests/ on sys.path.
    """
    import os

    poison = tmp_path / "poison"
    poison.mkdir()
    for name in ("pydantic.py", "yaml.py"):
        (poison / name).write_text("raise ImportError('poisoned')\n", encoding="utf-8")

    host = tmp_path / "host"          # no .acf/enabled -> both hooks no-op
    host.mkdir()

    env = {**os.environ, "PYTHONPATH": str(poison), "PYTHONIOENCODING": "utf-8"}
    for hook in ("inject_constraints.py", "posttooluse_gate.py"):
        proc = subprocess.run(
            [sys.executable, str(HOOKS / hook), "--repo", str(host)],
            capture_output=True,
            text=True,
            env=env,
            input="",
        )
        assert proc.returncode == 0, f"{hook} exited {proc.returncode}: {proc.stderr}"
        assert "Traceback" not in proc.stderr, f"{hook} raised: {proc.stderr}"
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest plugins/arch-compliance/tests/test_repo_paths.py -v`

Expected: `test_host_config_dir_has_one_code_owner` FAILS listing the six Path-construction and string-default sites (the four allowlisted documentation lines are already excluded), and `test_repo_module_imports_only_stdlib` FAILS with `FileNotFoundError` because `acf/repo.py` does not exist yet.

- [ ] **Step 3: Create the module**

Create `plugins/arch-compliance/python/acf/repo.py`:

```python
"""Host repository layout: the one declaration of where ACF looks in a host.

Stdlib-only on purpose. Both hooks import this at module scope, before the
``.acf/enabled`` gate decides whether ACF is active at all, so this module must
never pull in a third-party package.
"""
from __future__ import annotations

from pathlib import Path

#: Host-relative directory holding the mandate registry and the doctrine document.
CONFIG_DIR = Path("config") / "architecture"

#: Host-relative path to the mandate registry.
MANDATES_REL = CONFIG_DIR / "mandates.yml"

#: Host-relative path to the host's architecture doctrine document.
ARCH_REL = CONFIG_DIR / "ARCHITECTURE.md"

#: Host-relative default for the fail-loud ratchet baseline. A mandate may
#: override it via its ``params.baseline``; this is the value used when it does
#: not.
RATCHET_BASELINE_REL = CONFIG_DIR / "fail_loud_ratchet.json"

#: Host-relative marker that activates ACF in a host repository.
ENABLED_REL = Path(".acf") / "enabled"


def resolve_repo(explicit: Path | None, stdin_cwd: str | None = None) -> Path:
    """Resolve the host repository root.

    Precedence: an explicit ``--repo`` argument, then the invoking directory a
    harness supplies on stdin, then the process directory. The last branch is a
    genuine fallback, not a guarantee -- a caller that needs certainty must pass
    ``explicit``.
    """
    if explicit is not None:
        return explicit.resolve()
    if stdin_cwd:
        return Path(str(stdin_cwd)).resolve()
    return Path.cwd().resolve()
```

- [ ] **Step 4: Point `inject_constraints.py` at the module**

Replace the constant block at `:32-36`:

```python
_TEMPLATE = _HOOKS_DIR / "constraints_template.md"
_MANDATES_REL = Path("config") / "architecture" / "mandates.yml"
_ARCH_REL = Path("config") / "architecture" / "ARCHITECTURE.md"
_ENABLED_REL = Path(".acf") / "enabled"
_ARCH_EXCERPT_MAX = 4000
```

with:

```python
from acf.repo import ARCH_REL, ENABLED_REL, MANDATES_REL, resolve_repo

_TEMPLATE = _HOOKS_DIR / "constraints_template.md"
_ARCH_EXCERPT_MAX = 4000
```

Place that `from acf.repo import ...` line immediately after the `sys.path.insert` block at `:25-26`, because it depends on it. Then update the comment at `:28-30` to say what is now true:

```python
# NOTE: third-party acf imports (pydantic, yaml) are deferred into main() so
# this hook stays a true no-op in repos without .acf/enabled. acf.repo is
# stdlib-only and is safe to import here.
```

Replace every remaining use of the old names in this file: `_MANDATES_REL` at `:79` becomes `MANDATES_REL`, `_ARCH_REL` at `:157` and `:164` becomes `ARCH_REL`, and `_ENABLED_REL` wherever it appears becomes `ENABLED_REL`. Then replace the body of `_resolve_repo` at `:126-131` with a delegation, keeping the existing call sites untouched:

```python
def _resolve_repo(explicit: Path | None, stdin_payload: dict | None) -> Path:
    stdin_cwd = None
    if isinstance(stdin_payload, dict):
        stdin_cwd = stdin_payload.get("cwd")
    return resolve_repo(explicit, stdin_cwd)
```

- [ ] **Step 5: Point `posttooluse_gate.py` at the module**

Replace `:32-33`:

```python
_MANDATES_REL = Path("config") / "architecture" / "mandates.yml"
_ENABLED_REL = Path(".acf") / "enabled"
```

with an import placed after the `sys.path.insert` block, keeping `_CODE_SUFFIXES` where it is:

```python
from acf.repo import ENABLED_REL, MANDATES_REL, resolve_repo
```

Replace every `_MANDATES_REL` and `_ENABLED_REL` in the file with the imported names, and replace this hook's own `_resolve_repo` body with the same delegation shown in Step 4. Update its deferred-import comment at `:28-30` the same way.

- [ ] **Step 6: Point both CLIs at the module**

In `cli_check_diff.py`, add `from acf.repo import MANDATES_REL, resolve_repo` to the existing `acf` imports, then replace `:62-68`:

```python
    repo: Path = (args.repo or Path.cwd()).resolve()
    mode: DiffMode = args.mode  # type: ignore[assignment]
    mandates_path: Path = (
        args.mandates.resolve()
        if args.mandates is not None
        else repo / "config" / "architecture" / "mandates.yml"
    )
```

with:

```python
    repo: Path = resolve_repo(args.repo)
    mode: DiffMode = args.mode  # type: ignore[assignment]
    mandates_path: Path = (
        args.mandates.resolve() if args.mandates is not None else repo / MANDATES_REL
    )
```

In `cli_check_llm.py`, add the same import and replace `:36-40`:

```python
    mandates_path: Path = (
        args.mandates.resolve()
        if args.mandates is not None
        else Path.cwd() / "config" / "architecture" / "mandates.yml"
    )
```

with:

```python
    mandates_path: Path = (
        args.mandates.resolve()
        if args.mandates is not None
        else resolve_repo(None) / MANDATES_REL
    )
```

Then handle `cli_check_diff.py:171`, which is a **different host artifact** and the one site easy to mistake for a duplicate of the registry path. It reads:

```python
        baseline = params.get("baseline", "config/architecture/fail_loud_ratchet.json")
```

Replace it with the new constant, keeping POSIX form because the value flows on to `scan_ratchet(baseline_path=str(baseline))`:

```python
        baseline = params.get("baseline", RATCHET_BASELINE_REL.as_posix())
```

Add `RATCHET_BASELINE_REL` to the `from acf.repo import ...` line in that module.

Leave the four allowlisted documentation lines alone: the two `argparse` help strings and the two module docstrings. They are already in `ALLOWED_DOC_LINES`, and a constant name in `--help` output would tell an operator nothing.

- [ ] **Step 7: Run the new tests and then the whole suite**

Run: `python -m pytest plugins/arch-compliance/tests/test_repo_paths.py -v`
Expected: 3 passed.

Run: `python -m pytest -q`
Expected: **80 passed** (the 77 baseline plus the 3 new).

If any pre-existing test fails, you have changed behaviour. This task must not. Read the failure and fix the consolidation, not the test.

- [ ] **Step 8: Commit**

```bash
git add plugins/arch-compliance/python/acf/repo.py \
        plugins/arch-compliance/tests/test_repo_paths.py \
        plugins/arch-compliance/hooks/inject_constraints.py \
        plugins/arch-compliance/hooks/posttooluse_gate.py \
        plugins/arch-compliance/python/acf/cli_check_diff.py \
        plugins/arch-compliance/python/acf/cli_check_llm.py
git commit -m "refactor: one owner for the host config paths

acf.repo is stdlib-only so both hooks can import it at module scope,
ahead of the .acf/enabled gate, without pulling in pydantic or yaml.
Replaces two identical constant pairs and four inline spellings of the
host config directory. No behaviour change."
```

---

## Task 2: One git runner, two contracts

**Files:**
- Modify: `plugins/arch-compliance/python/acf/diff.py:17-28`
- Modify: `plugins/arch-compliance/tests/test_diff_cli.py`

**Interfaces:**
- Consumes: nothing from Task 1.
- Produces: `acf.diff.run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]`, which never raises on a non-zero status. `_git(repo, *args) -> str` keeps its current contract exactly: raise `GitError` on non-zero, else return stdout.

**Why.** `_git` destroys the return code inside the helper, so no caller can read a non-zero status as data. That is the right default for the two existing callers and the wrong one for a future caller that needs to distinguish "this path is ignored" (exit 1, no output) from "git failed". Splitting the runner from the policy keeps one place that knows how to invoke git.

- [ ] **Step 1: Write the failing tests**

Append to `plugins/arch-compliance/tests/test_diff_cli.py`:

```python
def test_run_git_reports_nonzero_as_data(tmp_path):
    """run_git never raises on a non-zero status; the caller decides."""
    from acf.diff import run_git

    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    proc = run_git(tmp_path, "rev-parse", "--verify", "refs/heads/nope")
    assert proc.returncode != 0
    assert proc.stdout == "" or "nope" not in proc.stdout


def test_run_git_returns_stdout_on_success(tmp_path):
    from acf.diff import run_git

    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    proc = run_git(tmp_path, "rev-parse", "--is-inside-work-tree")
    assert proc.returncode == 0
    assert proc.stdout.strip() == "true"


def test_git_wrapper_still_raises_on_nonzero(tmp_path):
    """The existing contract is unchanged: _git raises, callers rely on it."""
    from acf.diff import _git
    from acf.exceptions import GitError

    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    with pytest.raises(GitError) as excinfo:
        _git(tmp_path, "rev-parse", "--verify", "refs/heads/nope")
    assert "rev-parse" in str(excinfo.value)


def test_git_wrapper_raises_outside_a_repository(tmp_path):
    """Review Focus 5: a directory that is not a git repository."""
    from acf.diff import _git, run_git
    from acf.exceptions import GitError

    plain = tmp_path / "not_a_repo"
    plain.mkdir()
    with pytest.raises(GitError):
        _git(plain, "status", "--porcelain")
    proc = run_git(plain, "status", "--porcelain")
    assert proc.returncode != 0
```

Check the top of `test_diff_cli.py` and add `import subprocess` and `import pytest` only if they are not already imported.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest plugins/arch-compliance/tests/test_diff_cli.py -k run_git -v`
Expected: FAIL with `ImportError: cannot import name 'run_git' from 'acf.diff'`.

- [ ] **Step 3: Split the runner from the policy**

Replace `diff.py:17-28` in full:

```python
def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    """Invoke git and return the completed process, non-zero status included.

    The one place that knows how to invoke git. Callers that treat a non-zero
    status as a failure should use ``_git``; callers that need the status as
    data (an exit code that MEANS something, such as ``check-ignore``) use this.
    """
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def _git(repo: Path, *args: str) -> str:
    """Run git and return stdout, raising ``GitError`` on a non-zero status."""
    proc = run_git(repo, *args)
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        raise GitError(f"git {' '.join(args)} failed: {err or proc.returncode}")
    return proc.stdout
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest plugins/arch-compliance/tests/test_diff_cli.py -v`
Expected: all pass, including the pre-existing tests in that file.

Run: `python -m pytest -q`
Expected: **84 passed** (80 after Task 1, plus 4 new).

- [ ] **Step 5: Commit, then open PR 1**

```bash
git add plugins/arch-compliance/python/acf/diff.py \
        plugins/arch-compliance/tests/test_diff_cli.py
git commit -m "refactor: split the git runner from the raise-on-nonzero policy

run_git returns the completed process so a caller can read a non-zero
status as data; _git keeps its exact contract as the wrapper both current
callers use. No behaviour change for changed_files or added_lines."
```

```bash
npm ci --prefix plugins/arch-compliance/detectors/typescript
npm test --prefix plugins/arch-compliance/detectors/typescript
python -m pytest -q
git push -u origin feat/single-owner-hygiene
gh pr create --title "Single owner for host paths and the git runner" --body "$(cat <<'BODY'
Two consolidations with no behaviour change.

- `acf.repo` is the one declaration of the host config directory, the three
  host-relative paths, and host-root resolution. It is stdlib-only, so both
  hooks import it at module scope ahead of the `.acf/enabled` gate without
  pulling in pydantic or yaml. Replaces two identical constant pairs and four
  inline spellings.
- `run_git` returns the completed process so a future caller can read a
  non-zero status as data. `_git` keeps its exact contract as the wrapper the
  two current callers use.

Every existing message and exception type is unchanged. Suite goes 77 to 84.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
BODY
)"
```

---

## Task 3: One file loader, one input error

**Files:**
- Create: `plugins/arch-compliance/python/acf/loader.py`
- Create: `plugins/arch-compliance/tests/test_loader.py`
- Modify: `plugins/arch-compliance/python/acf/exceptions.py:5-6`
- Modify: `plugins/arch-compliance/python/acf/registry.py:6`, `:37-62`
- Modify: `plugins/arch-compliance/python/acf/baseline.py:15`, `:78-93`
- Modify: `plugins/arch-compliance/python/acf/cli_check_diff.py:19`, `:73`
- Modify: `plugins/arch-compliance/hooks/inject_constraints.py:88`, `:102`
- Modify: `plugins/arch-compliance/hooks/posttooluse_gate.py:92`, `:107`
- Modify: `plugins/arch-compliance/tests/test_registry.py`, `tests/test_baseline.py`, `tests/test_diff_cli.py:193`
- Modify: `skills/acf-setup/SKILL.md:224`, `skills/acf-mandate/SKILL.md:106`, `skills/architecture-review/SKILL.md:164`, `:174`

**Interfaces:**
- Consumes: nothing from Tasks 1 and 2.
- Produces: `acf.loader.load_model_file(path, model, *, subject, fmt, many=False)` returning a validated model instance or a list of them, and raising only `AcfInputError`. `acf.exceptions.AcfInputError(AcfError)` replaces `RegistryLoadError`, which is deleted.

**The `subject` parameter is load-bearing.** Without it the merged loader cannot produce the operator-facing message `mandates file not found: <path>`, which `tests/test_diff_cli.py:193` pins. The parameter is what lets one implementation keep two different operator vocabularies.

**Both strictness axes resolve toward the stricter form.** `registry.py:44-47` catches only `yaml.YAMLError`, so an unreadable registry escapes as a bare `OSError`; `baseline.py:88` catches `(OSError, json.JSONDecodeError)`. The merge catches read errors. `registry.py:52` catches bare `Exception` around validation, which would report an internal bug as a bad input file; `baseline.py:92` catches `ValidationError`. The merge catches only validation errors.

- [ ] **Step 1: Write the failing tests**

Create `plugins/arch-compliance/tests/test_loader.py`:

```python
"""One loader, one error type, the stricter half of each behavioural axis."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import BaseModel, ConfigDict

from acf.exceptions import AcfInputError
from acf.loader import load_model_file


class Row(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    count: int


def test_missing_file_names_its_subject_and_path(tmp_path):
    missing = tmp_path / "mandates.yml"
    with pytest.raises(AcfInputError) as excinfo:
        load_model_file(missing, Row, subject="mandates file", fmt="yaml", many=True)
    message = str(excinfo.value)
    assert "mandates file not found" in message
    assert missing.as_posix() in message


def test_yaml_list_root_loads_many(tmp_path):
    path = tmp_path / "rows.yml"
    path.write_text("- name: a\n  count: 1\n- name: b\n  count: 2\n", encoding="utf-8")
    rows = load_model_file(path, Row, subject="rows file", fmt="yaml", many=True)
    assert [r.name for r in rows] == ["a", "b"]


def test_json_object_root_loads_one(tmp_path):
    path = tmp_path / "row.json"
    path.write_text(json.dumps({"name": "a", "count": 1}), encoding="utf-8")
    row = load_model_file(path, Row, subject="row file", fmt="json")
    assert row.count == 1


def test_wrong_root_cardinality_is_refused(tmp_path):
    """Review Focus 2: a mapping where a list is required."""
    path = tmp_path / "rows.yml"
    path.write_text("name: a\ncount: 1\n", encoding="utf-8")
    with pytest.raises(AcfInputError) as excinfo:
        load_model_file(path, Row, subject="rows file", fmt="yaml", many=True)
    assert "must be a list" in str(excinfo.value)
    assert path.as_posix() in str(excinfo.value)


def test_unparsable_text_is_refused(tmp_path):
    path = tmp_path / "rows.yml"
    path.write_text("name: [unclosed\n", encoding="utf-8")
    with pytest.raises(AcfInputError):
        load_model_file(path, Row, subject="rows file", fmt="yaml", many=True)


def test_validation_failure_is_refused(tmp_path):
    path = tmp_path / "rows.yml"
    path.write_text("- name: a\n  count: not_an_int\n", encoding="utf-8")
    with pytest.raises(AcfInputError):
        load_model_file(path, Row, subject="rows file", fmt="yaml", many=True)


def test_unreadable_file_is_one_input_error_not_a_bare_oserror(tmp_path, monkeypatch):
    """Review Focus 1: an existing file whose read raises OSError.

    Today this escapes load_mandates as a bare OSError because registry.py
    catches only yaml.YAMLError. The merged loader must surface one type.
    """
    path = tmp_path / "rows.yml"
    path.write_text("- name: a\n  count: 1\n", encoding="utf-8")

    real_read_text = Path.read_text

    def boom(self, *args, **kwargs):
        if self == path:
            raise OSError("permission denied")
        return real_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", boom)
    with pytest.raises(AcfInputError) as excinfo:
        load_model_file(path, Row, subject="rows file", fmt="yaml", many=True)
    assert path.as_posix() in str(excinfo.value)


def test_internal_error_is_not_reported_as_bad_input(tmp_path, monkeypatch):
    """registry.py:52 catches bare Exception; the merge must not.

    A bug inside model validation is not a bad input file, and mislabelling it
    sends the operator to the wrong place.
    """
    path = tmp_path / "rows.yml"
    path.write_text("- name: a\n  count: 1\n", encoding="utf-8")

    def explode(cls, *args, **kwargs):
        raise RuntimeError("internal bug")

    monkeypatch.setattr(Row, "model_validate", classmethod(explode))
    with pytest.raises(RuntimeError):
        load_model_file(path, Row, subject="rows file", fmt="yaml", many=True)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest plugins/arch-compliance/tests/test_loader.py -v`
Expected: every test FAILS at collection with `ImportError: cannot import name 'AcfInputError'`.

- [ ] **Step 3: Add the exception and delete the old one**

In `exceptions.py`, replace `:5-6`:

```python
class RegistryLoadError(AcfError):
    pass
```

with:

```python
class AcfInputError(AcfError):
    """An input file ACF must read is missing, unparsable, or misshapen."""
```

- [ ] **Step 4: Write the loader**

Create `plugins/arch-compliance/python/acf/loader.py`:

```python
"""The one load-parse-validate-refuse implementation.

Every input file ACF reads goes through here, so an operator meets one error
type and one message shape no matter which file was wrong. ``subject`` carries
the operator's vocabulary for the file ("mandates file", "baseline"), which is
why one implementation can serve several callers without flattening their
messages.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal, TypeVar, overload

import yaml
from pydantic import BaseModel, ValidationError

from acf.exceptions import AcfInputError

Fmt = Literal["yaml", "json"]
M = TypeVar("M", bound=BaseModel)


@overload
def load_model_file(
    path: Path, model: type[M], *, subject: str, fmt: Fmt, many: Literal[False] = False
) -> M: ...


@overload
def load_model_file(
    path: Path, model: type[M], *, subject: str, fmt: Fmt, many: Literal[True]
) -> list[M]: ...


def load_model_file(
    path: Path,
    model: type[M],
    *,
    subject: str,
    fmt: Fmt,
    many: bool = False,
) -> M | list[M]:
    """Load ``path``, parse it as ``fmt``, validate against ``model``.

    Raises ``AcfInputError`` for every way the file itself can be wrong: absent,
    unreadable, unparsable, wrong root cardinality, or failing validation. A bug
    inside validation is NOT caught -- only ``ValidationError`` is, so an
    internal error keeps its own type instead of posing as a bad input file.
    """
    if not path.is_file():
        raise AcfInputError(f"{subject} not found: {path.as_posix()}")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise AcfInputError(f"cannot read {subject} {path.as_posix()}: {exc}") from exc
    try:
        raw: Any = yaml.safe_load(text) if fmt == "yaml" else json.loads(text)
    except (yaml.YAMLError, json.JSONDecodeError) as exc:
        raise AcfInputError(f"invalid {fmt} in {path.as_posix()}: {exc}") from exc
    if many:
        if not isinstance(raw, list):
            raise AcfInputError(f"{subject} root must be a list: {path.as_posix()}")
        try:
            return [model.model_validate(row) for row in raw]
        except ValidationError as exc:
            raise AcfInputError(f"invalid {subject} {path.as_posix()}: {exc}") from exc
    try:
        return model.model_validate(raw)
    except ValidationError as exc:
        raise AcfInputError(f"invalid {subject} {path.as_posix()}: {exc}") from exc
```

- [ ] **Step 5: Run the loader tests to verify they pass**

Run: `python -m pytest plugins/arch-compliance/tests/test_loader.py -v`
Expected: 8 passed.

- [ ] **Step 6: Make `load_mandates` a caller**

In `registry.py`, change the import at `:6` to `from acf.exceptions import UnknownDetectorError` and add `from acf.loader import load_model_file`. Drop the now-unused `import yaml` and `from pathlib import Path` only if nothing else in the file uses them; `Path` is used in the signature, so keep it. Replace `:37-62` in full:

```python
def load_mandates(
    path: Path,
    *,
    known_detectors: frozenset[str] | None = None,
) -> MandateRegistry:
    mandates = load_model_file(
        path, Mandate, subject="mandates file", fmt="yaml", many=True
    )
    if known_detectors is not None:
        for m in mandates:
            if m.status != "enforced":
                continue
            if m.detection in {"ast", "guard"} and m.detector not in known_detectors:
                raise UnknownDetectorError(
                    f"enforced mandate {m.id!r} references unknown detector {m.detector!r}"
                )
    return MandateRegistry(mandates=mandates, source_path=path.as_posix())
```

- [ ] **Step 7: Make `load_baseline` a caller**

In `baseline.py`, keep `from acf.exceptions import BaselineError` (the write-side raise at `:74` still uses it) and add `from acf.loader import load_model_file`. Replace `:78-93` in full:

```python
def load_baseline(path: Path) -> Baseline:
    """Load + validate baseline. Fail loud on missing/malformed.

    Absence is a real state decided by the CALLER (existence check before load).
    The loader itself never returns None. Refusals are ``AcfInputError``, shared
    with every other input file; ``BaselineError`` now covers only the write
    side, where ACF is the producer rather than the reader.
    """
    return load_model_file(path, Baseline, subject="baseline", fmt="json")
```

Drop `import json` and `ValidationError` from this module's imports only if nothing else uses them. Check first: `json` may be unused after this change, and `ValidationError` almost certainly is.

- [ ] **Step 8: Update the three catch sites and the two deferred hook imports**

In `cli_check_diff.py`, change `:19` to import `AcfInputError` instead of `RegistryLoadError`, and change the tuple at `:73` to `except (GitError, AcfInputError, UnknownDetectorError, DetectorPackError) as exc:`.

In `inject_constraints.py`, change the deferred import at `:88` to `from acf.exceptions import AcfInputError` and the handler at `:102` to `except AcfInputError as exc:`. Do the same in `posttooluse_gate.py` at `:92` and `:107`.

- [ ] **Step 9: Update the tests that pin the old type and message**

In `test_registry.py`, replace the `RegistryLoadError` import and every `pytest.raises(RegistryLoadError)` with `AcfInputError`.

In `test_baseline.py`, the three read-side `pytest.raises(BaselineError)` at the missing, unreadable, and invalid cases become `pytest.raises(AcfInputError)`. Keep the `BaselineError` import only if the write-side test below uses it. Then add the first test for the surviving raise, which currently has none:

```python
def test_save_baseline_fails_loud_when_unwritable(tmp_path, monkeypatch):
    """The write-side BaselineError is the one that survives; pin it."""
    from acf.baseline import Baseline, save_baseline
    from acf.exceptions import BaselineError

    data = Baseline(generated_at="2026-01-01", commit="a" * 40, invocation="test", counts=[])
    target = tmp_path / "nested" / "baseline.json"

    def boom(self, *args, **kwargs):
        raise OSError("read-only file system")

    monkeypatch.setattr(Path, "write_text", boom)
    with pytest.raises(BaselineError) as excinfo:
        save_baseline(target, data)
    assert target.as_posix() in str(excinfo.value)
```

Confirm `Path` and `pytest` are imported at the top of `test_baseline.py`; add them if not.

`test_diff_cli.py:193` asserts `"mandates file not found"`. The loader's message for `subject="mandates file"` is exactly `mandates file not found: <path>`, so that assertion should still pass unchanged. Run it and confirm rather than assuming.

- [ ] **Step 10: Update the four prose sites**

`grep -rn 'RegistryLoadError\|BaselineError' skills/` returns four live lines. Rewrite each to name the new type:

- `skills/acf-setup/SKILL.md:224`
- `skills/acf-mandate/SKILL.md:106`
- `skills/architecture-review/SKILL.md:164` and `:174` — these two describe the baseline **read** path, which is now `AcfInputError`.

Leave `docs/plans/PLAN_ARCH_COMPLIANCE_FOR_SUPERPOWERS.md` alone. It is an executed historical record of code as it was written, and editing it would falsify the record. Its nine occurrences are why the check in Step 11 is scoped to the live tree.

- [ ] **Step 11: Verify the deletion is complete in the live tree**

Run:

```bash
grep -rn RegistryLoadError plugins/ skills/ README.md docs/guides/ || echo "CLEAN"
```

Expected: `CLEAN`. If anything remains, disposition it.

Run: `python -m pytest -q`
Expected: **93 passed** (84 after PR 1, plus 8 loader tests and 1 write-side baseline test).

- [ ] **Step 12: Commit**

```bash
git add -A
git commit -m "refactor: one file loader, one input error

load_model_file absorbs load_mandates and load_baseline, taking the
stricter half of both behavioural axes: it catches read errors (which
registry.py did not, so an unreadable registry escaped as a bare
OSError) and catches only ValidationError around validation (which
registry.py did not, so an internal bug was reported as a bad input
file). The subject parameter keeps each caller's operator vocabulary.

RegistryLoadError is deleted rather than aliased. BaselineError now
covers only the write side, where ACF is the producer, and that raise
gains its first test."
```

---

## Task 4: A missing doctrine document is a refusal, not a substitution

**Files:**
- Modify: `plugins/arch-compliance/hooks/inject_constraints.py:147-172`
- Modify: `plugins/arch-compliance/tests/test_hooks.py`

**Interfaces:**
- Consumes: `ARCH_REL` from Task 1.
- Produces: `_render_constraints` now raises `FileNotFoundError` when the doctrine document is absent; `main()` catches it and returns 1.

**Why.** `inject_constraints.py:162-166` substitutes the sentence `_ARCHITECTURE.md not found at ... use mandates above and host docs._` for the host's doctrine. The subagent is never told, so it proceeds believing it has the host's architecture rules when it has a placeholder. That is a silent empty default on a config-tier read, which the plugin's first governing principle prohibits in those words. The registry's absence already exits 1 at `:80-85`; the doctrine document gets the same treatment.

**Scope guard.** This task does **not** introduce `acf.yml`, a `doctrine` list, or any configuration of which document is the doctrine. `ARCH_REL` stays the single hardcoded answer. Those were the refuted parts of the source spec.

- [ ] **Step 1: Write the failing tests**

Append to `plugins/arch-compliance/tests/test_hooks.py`:

```python
def test_inject_fails_loud_when_doctrine_document_missing(tmp_path):
    """Review Focus 3: enabled, registry present, doctrine document absent.

    Previously the hook substituted a placeholder sentence and exited 0, so a
    subagent received a constraint block that looked complete.
    """
    repo = _seed_host(tmp_path, enabled=True, mandates=True)
    (repo / "config" / "architecture" / "ARCHITECTURE.md").unlink()

    proc = subprocess.run(
        [sys.executable, str(HOOK_INJECT), "--repo", str(repo)],
        capture_output=True,
        text=True,
        input="",
    )
    assert proc.returncode == 1, proc.stdout
    assert "ARCHITECTURE.md" in proc.stderr
    assert "not found" in proc.stderr.lower()
    assert "use mandates above" not in proc.stdout


def test_inject_succeeds_when_doctrine_document_present(tmp_path):
    """The happy path still works and carries the real doctrine text."""
    repo = _seed_host(tmp_path, enabled=True, mandates=True)
    (repo / "config" / "architecture" / "ARCHITECTURE.md").write_text(
        "# Host doctrine\n\nDISTINCTIVE_DOCTRINE_MARKER\n", encoding="utf-8"
    )

    proc = subprocess.run(
        [sys.executable, str(HOOK_INJECT), "--repo", str(repo)],
        capture_output=True,
        text=True,
        input="",
    )
    assert proc.returncode == 0, proc.stderr
    assert "DISTINCTIVE_DOCTRINE_MARKER" in proc.stdout


def test_gate_fails_loud_when_enabled_without_mandates(tmp_path):
    """The gate's own refusal has never had a test; pin it before it moves."""
    repo = _seed_host(tmp_path, enabled=True, mandates=False)

    proc = subprocess.run(
        [sys.executable, str(HOOK_GATE), "--repo", str(repo)],
        capture_output=True,
        text=True,
        input="",
    )
    assert proc.returncode == 1
    assert "mandates" in proc.stderr.lower()
```

Before running, open `test_hooks.py` and confirm the names this code uses. The module defines `_seed_host` at `:55`; find the constants it uses for the two hook script paths and substitute the real names for `HOOK_INJECT` and `HOOK_GATE`. Confirm `subprocess` and `sys` are imported.

Also note `_seed_host`'s single `if mandates:` guard at `:58` encloses both copies, so `mandates=True` gives you both the registry and an `ARCHITECTURE.md`, and the first test deletes the latter deliberately.

- [ ] **Step 2: Run the tests to verify the first one fails**

Run: `python -m pytest plugins/arch-compliance/tests/test_hooks.py -k doctrine -v`
Expected: `test_inject_fails_loud_when_doctrine_document_missing` FAILS with `assert 0 == 1`, because the hook currently exits 0 with a substituted sentence. The second doctrine test should already pass.

- [ ] **Step 3: Replace the substitution with a refusal**

In `_render_constraints`, replace the `if`/`else` at `:157-166`:

```python
    arch_path = repo / ARCH_REL
    if arch_path.is_file():
        excerpt = arch_path.read_text(encoding="utf-8").strip()
        if len(excerpt) > _ARCH_EXCERPT_MAX:
            excerpt = excerpt[:_ARCH_EXCERPT_MAX].rstrip() + "\n\n…(truncated)…"
    else:
        excerpt = (
            f"_ARCHITECTURE.md not found at `{_ARCH_REL.as_posix()}` — "
            "use mandates above and host docs._"
        )
```

with:

```python
    arch_path = repo / ARCH_REL
    if not arch_path.is_file():
        raise FileNotFoundError(
            f"doctrine document not found: {arch_path.as_posix()}"
        )
    excerpt = arch_path.read_text(encoding="utf-8").strip()
    if len(excerpt) > _ARCH_EXCERPT_MAX:
        excerpt = excerpt[:_ARCH_EXCERPT_MAX].rstrip() + "\n\n…(truncated)…"
```

Then wrap the call at `:106` so the refusal becomes an exit rather than a traceback:

```python
    try:
        block = _render_constraints(repo, registry.mandates)
    except (FileNotFoundError, OSError) as exc:
        print(f"acf: {exc}", file=sys.stderr)
        return 1
```

Use `FileNotFoundError` rather than `AcfInputError` here: this read is the hook's own, it happens after the deferred-import boundary only incidentally, and keeping it a stdlib error means `_render_constraints` needs no `acf` import. Catching `OSError` alongside it also covers an unreadable document, which the old code did not handle either.

Finally, update the module docstring at `:9-12` to record the new behaviour:

```
Behavior:
  - If ``.acf/enabled`` is absent: exit 0 (no-op), optional stderr warning.
  - If enabled and ``config/architecture/mandates.yml`` is missing: non-zero exit.
  - If enabled and ``config/architecture/ARCHITECTURE.md`` is missing: non-zero
    exit. A placeholder excerpt would tell a subagent it has the host's rules
    when it does not.
  - Otherwise print a constraint block (text) or Claude Code ``additionalContext`` JSON.
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest plugins/arch-compliance/tests/test_hooks.py -v`
Expected: all pass, including the three new ones.

Run: `python -m pytest -q`
Expected: **96 passed** (93 after Task 3, plus 3 new).

If a pre-existing hook test now fails because its fixture has no `ARCHITECTURE.md`, that is this change working. Give that fixture a doctrine document rather than weakening the refusal.

- [ ] **Step 5: Check the substituted sentence is gone**

Run:

```bash
grep -rn "use mandates above" plugins/ || echo "CLEAN"
```

Expected: `CLEAN`.

- [ ] **Step 6: Commit, then open PR 2**

```bash
git add -A
git commit -m "fix: refuse a missing doctrine document instead of substituting prose

The hook replaced an absent config/architecture/ARCHITECTURE.md with a
placeholder sentence and exited 0, so a subagent received a constraint
block that looked complete while carrying none of the host's rules. That
is the silent empty default on a config load that governing principle 1
prohibits. It now exits 1 naming the path, as the registry already did.

Adds the first test for the PostToolUse gate's own missing-registry
refusal, which was unpinned."
```

```bash
npm test --prefix plugins/arch-compliance/detectors/typescript
python -m pytest -q
git push -u origin feat/one-file-loader
gh pr create --title "One file loader, and a missing doctrine document fails loud" --body "$(cat <<'BODY'
Two changes that share the fail-loud theme.

**One loader.** `load_model_file` absorbs `load_mandates` and `load_baseline`,
taking the stricter half of both behavioural axes the two differed on: it
catches read errors, which `registry.py` did not (an unreadable registry
escaped as a bare `OSError`), and it catches only `ValidationError` around
validation, which `registry.py` did not (a bug inside validation was reported
as a bad input file). A `subject` parameter keeps each caller's operator
vocabulary, so `mandates file not found: <path>` survives verbatim.

`RegistryLoadError` is deleted rather than aliased. `BaselineError` now covers
only the write side, where ACF is the producer, and that raise gains its first
test.

**One fail-loud fix.** An absent `ARCHITECTURE.md` was replaced by a
placeholder sentence and the hook exited 0. A subagent could not tell it had
received no host doctrine. It now exits 1 naming the path.

This does NOT add `acf.yml`, a doctrine list, or configurable doctrine paths.

Suite goes 84 to 96.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
BODY
)"
```

---

## Task 5: One template renderer, two consumers

**Files:**
- Create: `plugins/arch-compliance/python/acf/template.py`
- Create: `plugins/arch-compliance/tests/test_template.py`
- Create: `plugins/arch-compliance/python/acf/judge_prompt.md`
- Modify: `plugins/arch-compliance/python/acf/judge.py:142-156`
- Modify: `plugins/arch-compliance/hooks/inject_constraints.py:168-172`

**Interfaces:**
- Consumes: nothing from Tasks 1 to 4.
- Produces: `acf.template.render_template(text: str, mapping: dict[str, str]) -> str`, raising `TemplateRenderError` when the text carries a token the mapping cannot fill or the mapping carries a key the text never uses. `acf.exceptions.TemplateRenderError(AcfError)`.

**Why both consumers.** Doing only the hook would leave the judge building a prompt from a skeleton by f-string, which is a second owner of "render a prompt from a skeleton plus context" that no scan for `{{` can find. A review of the earlier design caught exactly that, and the fix is to migrate both or neither.

**Why no package data — THIS PARAGRAPH WAS WRONG. Amended after the final review.** The original reasoning was that the judge template is read `Path(__file__).parent / "judge_prompt.md"`, following the precedent at `inject_constraints.py:32`, and therefore needs no `[tool.setuptools.package-data]` table.

**The precedent does not transfer.** `hooks/` is not a packaged module — it is run from `${CLAUDE_PLUGIN_ROOT}`, so its template is always beside it on disk. `acf/` *is* a packaged module, and setuptools omits non-`.py` files from a wheel unless a `package-data` table or a `MANIFEST.in` names them. Verified by building a wheel: `judge_prompt.md` was absent, and `acf-check-llm` would raise `FileNotFoundError` on its first enforced LLM mandate under a plain `pip install .`.

Worse, the original paragraph claimed this choice "avoids a mechanism whose failure mode would be invisible under the editable install CI uses" — the choice it made has exactly that failure mode, which is why all 104 tests passed while the wheel was broken.

**What to do instead:** declare `[tool.setuptools.package-data] acf = ["judge_prompt.md"]`, and guard it with a test that builds a wheel from the tracked **working tree** and asserts every tracked non-`.py` file under `acf/` is a member. A characterization test is the right guard for the prompt's *bytes* and cannot be made into a guard for its *shipping*.

**Note on braces.** The judge prompt contains a literal JSON example with single `{` and `}` characters. The token scheme matches only `{{UPPER_SNAKE}}`, so single braces pass through untouched. Do not switch to `str.format`, which would choke on them.

- [ ] **Step 1: Write the failing tests**

Create `plugins/arch-compliance/tests/test_template.py`:

```python
"""Both silent substitution failures become loud."""
from __future__ import annotations

import pytest

from acf.exceptions import TemplateRenderError
from acf.template import render_template


def test_fills_every_token():
    out = render_template("a {{ONE}} b {{TWO}}", {"ONE": "1", "TWO": "2"})
    assert out == "a 1 b 2"


def test_repeated_token_is_filled_everywhere():
    out = render_template("{{X}} and {{X}}", {"X": "v"})
    assert out == "v and v"


def test_unfilled_token_is_refused():
    """Review Focus 4a: a token the mapping cannot fill.

    str.replace leaves the literal token in the output and says nothing, so a
    renamed placeholder ships '{{ARCHITECTURE_EXCERPT}}' to a subagent.
    """
    with pytest.raises(TemplateRenderError) as excinfo:
        render_template("a {{ONE}} b {{TWO}}", {"ONE": "1"})
    assert "TWO" in str(excinfo.value)


def test_unused_mapping_key_is_refused():
    """Review Focus 4b: a mapping key the text never uses."""
    with pytest.raises(TemplateRenderError) as excinfo:
        render_template("a {{ONE}}", {"ONE": "1", "STALE": "x"})
    assert "STALE" in str(excinfo.value)


def test_single_braces_are_left_alone():
    """The judge prompt carries a literal JSON example."""
    text = 'respond with {"violation": bool} and {{DIFF}}'
    out = render_template(text, {"DIFF": "d"})
    assert out == 'respond with {"violation": bool} and d'


def test_value_containing_a_token_is_not_rescanned():
    """A substituted value is data, not template."""
    out = render_template("{{A}}", {"A": "{{B}}"})
    assert out == "{{B}}"
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest plugins/arch-compliance/tests/test_template.py -v`
Expected: collection FAILS with `ImportError: cannot import name 'TemplateRenderError'`.

- [ ] **Step 3: Add the exception**

Append to `exceptions.py`:

```python
class TemplateRenderError(AcfError):
    """A template token had no value, or a supplied value had no token."""
```

- [ ] **Step 4: Write the renderer**

Create `plugins/arch-compliance/python/acf/template.py`:

```python
"""The one placeholder substituter.

Tokens are literal ``{{UPPER_SNAKE}}`` runs in the template text, so the
required token set is derived from the text itself and needs no declaration
anywhere else. Substitution is single-pass: a value that happens to contain a
token is data, not template.

Refuses in both directions. ``str.replace`` is silent when a token has no value
(the literal token ships to the reader) and when a value has no token (the
caller believes it supplied something that was dropped).
"""
from __future__ import annotations

import re

from acf.exceptions import TemplateRenderError

_TOKEN_RE = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")


def required_tokens(text: str) -> set[str]:
    """The token names ``text`` consumes."""
    return set(_TOKEN_RE.findall(text))


def render_template(text: str, mapping: dict[str, str]) -> str:
    """Substitute every ``{{TOKEN}}`` in ``text`` from ``mapping``.

    Raises ``TemplateRenderError`` if the two sides disagree in either
    direction.
    """
    needed = required_tokens(text)
    supplied = set(mapping)
    missing = sorted(needed - supplied)
    unused = sorted(supplied - needed)
    if missing or unused:
        parts = []
        if missing:
            parts.append(f"no value for {', '.join(missing)}")
        if unused:
            parts.append(f"no token for {', '.join(unused)}")
        raise TemplateRenderError("; ".join(parts))
    return _TOKEN_RE.sub(lambda m: mapping[m.group(1)], text)
```

- [ ] **Step 5: Run the renderer tests to verify they pass**

Run: `python -m pytest plugins/arch-compliance/tests/test_template.py -v`
Expected: 6 passed.

- [ ] **Step 6: Make the hook a caller**

In `inject_constraints.py`, replace the return at `:168-172`:

```python
    return (
        template.replace("{{MANDATES}}", mandates_block).replace(
            "{{ARCHITECTURE_EXCERPT}}", excerpt
        )
    )
```

with:

```python
    return render_template(
        template,
        {"MANDATES": mandates_block, "ARCHITECTURE_EXCERPT": excerpt},
    )
```

`render_template` imports `pydantic` indirectly? It does not — `acf.template` imports only `re` and `acf.exceptions`, and `acf.exceptions` imports nothing. But `_render_constraints` runs well after the `.acf/enabled` gate and after the deferred-import block, so import it there rather than at module scope, beside the other `acf` imports at `:88-89`:

```python
        from acf.template import render_template
```

Pass it into `_render_constraints` or re-import inside that function; re-importing inside the function is simplest and costs nothing after the first call.

Then confirm `hooks/constraints_template.md` has exactly the two tokens the mapping supplies. Run:

```bash
python -c "import re,pathlib; p=pathlib.Path('plugins/arch-compliance/hooks/constraints_template.md'); print(sorted(set(re.findall(r'\{\{([A-Z][A-Z0-9_]*)\}\}', p.read_text(encoding='utf-8')))))"
```

Expected: `['ARCHITECTURE_EXCERPT', 'MANDATES']`. If the lists disagree, the hook will now raise instead of silently shipping a token, which is the point; fix the mapping or the template so they match.

- [ ] **Step 7: Lift the judge skeleton into a template**

Create `plugins/arch-compliance/python/acf/judge_prompt.md` with the exact text the f-string produces, tokens substituted for the interpolations:

```
You are an architecture compliance judge.
Mandate id: {{MANDATE_ID}}
Title: {{TITLE}}
Severity: {{SEVERITY}}
Detector/prompt id: {{DETECTOR}}
Architecture anchor: {{ARCH_ANCHOR}}

Review the unified diff. Respond with JSON only:
{"violation": bool, "severity": "BLOCK"|"WARN", "confidence": "high"|"medium"|"low", "message": string, "path": string|null, "line": int|null}
Set violation=false when the diff does not violate the mandate.

DIFF:
{{DIFF_TEXT}}
```

- [ ] **Step 8: Write a test that pins the judge prompt's content**

Append to `plugins/arch-compliance/tests/test_template.py`:

```python
def test_judge_prompt_carries_every_field_the_builder_supplies():
    """The template and _build_prompt's mapping must agree, or render refuses."""
    from acf.judge import _build_prompt
    from acf.registry import Mandate

    mandate = Mandate(
        id="M1",
        title="A title",
        severity="BLOCK",
        detection="llm",
        detector="d1",
        languages="python",
        call_sites=[],
        exemption_tokens=[],
        status="enforced",
        arch_anchor="An Anchor",
    )
    out = _build_prompt(diff_text="DIFF_BODY", mandate=mandate)
    for expected in ("M1", "A title", "BLOCK", "d1", "An Anchor", "DIFF_BODY"):
        assert expected in out
    assert "{{" not in out
    assert '"violation": bool' in out
```

- [ ] **Step 9: Make the judge a caller**

In `judge.py`, add the imports. **`judge.py` does not currently import `Path`** — its imports are `json`, `os`, `re`, `typing`, `httpx`, `pydantic`, and three `acf` modules — so add the `pathlib` line too:

```python
from pathlib import Path

from acf.template import render_template

_PROMPT_TEMPLATE = Path(__file__).resolve().parent / "judge_prompt.md"
```

Put `from pathlib import Path` with the stdlib imports at the top and the `acf.template` import beside the other `acf` imports, matching the module's existing grouping. Then replace `:142-156` in full:

```python
def _build_prompt(*, diff_text: str, mandate: Mandate) -> str:
    return render_template(
        _PROMPT_TEMPLATE.read_text(encoding="utf-8"),
        {
            "MANDATE_ID": mandate.id,
            "TITLE": mandate.title,
            "SEVERITY": mandate.severity,
            "DETECTOR": mandate.detector,
            "ARCH_ANCHOR": mandate.arch_anchor,
            "DIFF_TEXT": diff_text,
        },
    )
```

- [ ] **Step 10: Run the tests to verify they pass**

Run: `python -m pytest plugins/arch-compliance/tests/test_template.py -v`
Expected: 7 passed.

Run: `python -m pytest -q`
Expected: **104 passed** (96 after PR 2, plus 6 template tests, the field-coverage test, and the byte-identity characterization test). The fix pass after the final review adds a packaging test, taking the branch to **105**.

`test_judge.py` was checked at the base commit and asserts nothing about the prompt's text, so it needs no change. Confirm that is still true rather than trusting this line: `grep -rn "architecture compliance judge" plugins/tests/` should return nothing.

- [ ] **Step 11: Verify one renderer, by behaviour not by convention**

The earlier design claimed a single renderer on the strength of a `{{` scan, which is a search by naming convention and cannot see an f-string skeleton. Check by behaviour instead:

```bash
grep -rn "replace(\"{{" plugins/ || echo "no inline token replace"
grep -rn "You are an architecture" plugins/ --include=*.py || echo "no inline judge skeleton"
```

Expected: both print their "no ..." message. Both prompt skeletons now live in files and both go through `render_template`.

- [ ] **Step 12: Commit, then open PR 3**

```bash
git add -A
git commit -m "refactor: one template renderer, called by the hook and the judge

render_template derives its required tokens from the template text and
refuses in both directions, replacing a chained str.replace that was
silent when a token had no value and when a value had no token.

Migrates BOTH consumers. Doing only the hook would leave judge._build_prompt
as a second owner of 'render a prompt from a skeleton plus context' that no
scan for '{{' could find. Templates are read relative to __file__, the
precedent already in this tree. (The packaging claim in this commit message was corrected by the follow-up fix: a package-data table IS required — see the Task 5 amendment above.)"
```

```bash
npm test --prefix plugins/arch-compliance/detectors/typescript
python -m pytest -q
git push -u origin feat/one-template-renderer
gh pr create --title "One template renderer, called by the hook and the judge" --body "$(cat <<'BODY'
`render_template` derives its required token set from the template text and
refuses in both directions: a token with no value, and a value with no token.
The chained `str.replace` it replaces was silent in both, so a renamed
placeholder shipped a literal `{{ARCHITECTURE_EXCERPT}}` to a subagent.

Both consumers migrate. Doing only the hook would leave `judge._build_prompt`
building a prompt from an f-string skeleton, a second owner of the same
responsibility that no scan for `{{` can find. The judge skeleton moves to
`acf/judge_prompt.md`, read relative to `__file__` like the hook's own
template, so no packaging table is involved.

Suite goes 96 to 103.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
BODY
)"
```

---

## Definition of Done

Branch-level gate. Every item must pass before the third PR merges.

1. `python -m pytest -q` from the repository root prints **105 passed**, with `npm ci --prefix plugins/arch-compliance/detectors/typescript` having been run once. (Amended from 103: Task 5 added a byte-identity characterization test, and the post-review fix pass added a wheel-packaging test.)
2. `npm test --prefix plugins/arch-compliance/detectors/typescript` prints `self-test OK`.
3. `grep -rnE 'config.{0,6}architecture' plugins/ --include=*.py` returns `acf/repo.py`'s constants plus exactly the four allowlisted documentation lines (two `argparse` help strings, two module docstrings) and nothing else. `test_repo_paths.py::test_host_config_dir_has_one_code_owner` is the executable form of this check and is the authority; the grep is for a human reading the diff.
4. `grep -rn RegistryLoadError plugins/ skills/ README.md docs/guides/` returns nothing. `docs/plans/` is excluded as an executed historical record.
5. `grep -rn "use mandates above" plugins/` returns nothing.
6. `grep -rn 'replace("{{' plugins/` returns nothing, and `grep -rn "You are an architecture" plugins/ --include=*.py` returns nothing.
7. `python -c "import acf.repo"` succeeds in an interpreter with no `pydantic` and no `yaml` installed, or equivalently `test_repo_paths.py::test_repo_module_imports_only_stdlib` passes.
8. Both hooks exit 0 with no traceback in a repository with no `.acf/enabled`, with `pydantic` and `yaml` poisoned on `PYTHONPATH`. Pinned by `test_repo_paths.py` and by the two pre-existing no-deps tests.
9. A host that is enabled and has a registry but no `ARCHITECTURE.md` makes `inject_constraints.py` exit 1 naming the path. Pinned by `test_hooks.py`.
10. `save_baseline`'s `BaselineError` has a test. `load_baseline`'s refusals are `AcfInputError`.
11. **AMENDED after the final review.** No new entry under `[project.dependencies]` and no change to `[tool.setuptools.packages.find]` — both still hold. But a `[tool.setuptools.package-data]` table **is now required**, because the original prohibition rested on a false premise (see the Task 5 amendment). Exactly one entry is expected, `acf = ["judge_prompt.md"]`, and `tests/test_packaging.py` builds a real wheel to prove it ships.
12. `acf.yml`, a `doctrine` list, a run ledger, a run manifest, and the adversarial-review gate itself appear **nowhere** in the diff. Confirm with `git diff c63cb70 --stat` and read the file list.

## Risks

| Risk | Mitigation |
|---|---|
| Task 4 changes hook behaviour, and a host without `ARCHITECTURE.md` that worked before now fails. | That is the intended change and it is the point of the task. It is called out in the PR body. `/acf-setup` step 5 already copies both files into the host, so a host set up by the documented path has the document. |
| The single-owner test in Task 1 is a shape check and will flag prose and help strings that legitimately name the path. | Step 6 says to reference the constant instead, with a marker escape hatch as the fallback. The test's job is to make a new duplicate visible, not to forbid documentation. |
| `test_hooks.py`'s fixture names are assumed by Task 4's test code. | Step 1 of Task 4 says explicitly to open the file and substitute the real names before running. |
| `monkeypatch` of `Path.read_text` and `Path.write_text` in Tasks 3 and 9 is broad and could affect unrelated reads within the test. | Task 3's patch guards on the exact path and delegates otherwise. Keep that pattern. |
| Deleting `RegistryLoadError` breaks an external consumer. | The type is six weeks old, the repository has no releases and no dependents, and `gh api` can confirm. The plugin's second governing principle forbids keeping an alias. |
