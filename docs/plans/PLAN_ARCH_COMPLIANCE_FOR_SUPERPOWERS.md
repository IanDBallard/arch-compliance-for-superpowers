# Architecture Compliance for Superpowers — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship an installable Claude Code marketplace plugin that provides a four-tier architecture compliance spine (registry, dual TS/Python deterministic packs, LLM judge, audit) as a Superpowers companion.

**Architecture:** Marketplace repo hosts one plugin (`plugins/arch-compliance`). Python owns registry, findings, Python AST pack, CLI orchestration, and LLM judge; a Node `ts-morph` scanner owns the TypeScript/React pack and is invoked by the Python CLI. Host projects get config via `/acf-setup`; the plugin never treats bundled profiles as runtime defaults after setup.

**Tech Stack:** Python 3.11+, Pydantic v2, PyYAML, pytest; Node 20+, TypeScript, ts-morph; Gemini API (env key) for Tier 2; Claude Code plugin manifests (`.claude-plugin/`).

**Spec:** `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md`

---

## Architectural Contract

1. `mandates.yml` is the only mandate list; load only through `acf.registry.load_mandates()`.
2. One shared `Finding` schema for Python pack, TS pack, LLM judge, and audit.
3. Paths persisted to YAML/JSON use forward slashes / `Path.as_posix()`.
4. Enforced `detection: llm` mandates hard-fail if the judge is not configured (no silent skip).
5. Superpowers owns workflow shape; this plugin owns mandate content, gates, and constraint injection — host architecture + registry win on conflict.

## State & Data Definitions

- **No HFSM** in the plugin itself.
- **Pydantic models:** `Mandate`, `MandateRegistry`, `Finding`, `JudgeResult`, `Baseline`, `DriftReport`.
- **Exceptions** (all subclass `acf.exceptions.AcfError`): `RegistryLoadError`, `UnknownMandateError`, `UnknownDetectorError`, `JudgeNotConfiguredError`, `EmptyTargetTreeError`, `DetectorPackError`.

## Definition of Done

- `pytest` green for registry, both packs, diff CLI, judge fixtures.
- `node detectors/typescript` fixture scan green.
- `claude --plugin-dir ./plugins/arch-compliance` loads without manifest errors.
- README documents marketplace install + `/acf-setup` friend success bar.
- GitHub repo `IanDBallard/arch-compliance-for-superpowers` published (public).

## Development Workspace & Integration

**Worktree (user-approved):** implement **in-place** at `c:\Users\iball\Projects\arch-compliance-for-superpowers` (new dedicated repo, not an HM worktree). Branch: rename/use `main`.

### Implementation Decision Overrides

| Decision | Override | Rationale | Approved |
|----------|----------|-----------|----------|
| Workspace | In-place on sibling repo (not HM `.claude/worktrees/`) | Separate product repo | User, 2026-07-27 |
| Branch | `main` | New repo; design already on `master` — rename to `main` in Task 1 | User, 2026-07-27 |
| Merge path | Push `main` to new GitHub remote | Marketplace install requires public git host | User, 2026-07-27 |
| CI gates | Local pytest + node fixture scans; GitHub Actions basic in Task 12 | No HM `run_ci.sh` | User, 2026-07-27 |

---

## File Structure

```text
arch-compliance-for-superpowers/
├── .claude-plugin/marketplace.json
├── .github/workflows/ci.yml
├── README.md
├── pyproject.toml
├── package.json                          # workspace root for TS detector deps
├── docs/
│   ├── design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md
│   ├── plans/PLAN_ARCH_COMPLIANCE_FOR_SUPERPOWERS.md
│   └── guides/SUPERPOWERS_COMPLEMENT.md
└── plugins/arch-compliance/
    ├── .claude-plugin/plugin.json
    ├── hooks/hooks.json
    ├── hooks/inject_constraints.py
    ├── hooks/posttooluse_gate.py
    ├── skills/acf-setup/SKILL.md
    ├── skills/acf-mandate/SKILL.md
    ├── skills/architecture-review/SKILL.md
    ├── skills/architecture-review/auditors/*.md
    ├── profiles/react-app/{mandates.yml,ARCHITECTURE.md}
    ├── profiles/python-service/{mandates.yml,ARCHITECTURE.md}
    ├── python/
    │   └── acf/
    │       ├── __init__.py
    │       ├── exceptions.py
    │       ├── finding.py
    │       ├── registry.py
    │       ├── diff.py
    │       ├── engine.py
    │       ├── judge.py
    │       ├── baseline.py
    │       ├── cli_check_diff.py
    │       ├── cli_check_llm.py
    │       └── detectors/
    │           ├── __init__.py
    │           └── python_pack.py
    ├── detectors/typescript/
    │   ├── package.json
    │   ├── tsconfig.json
    │   ├── src/scan.ts
    │   └── src/rules/*.ts
    └── tests/
        ├── fixtures/...
        ├── test_registry.py
        ├── test_python_pack.py
        ├── test_diff_cli.py
        ├── test_judge.py
        └── test_baseline.py
```

---

### Task 1: Repo skeleton, manifests, Python package layout

**Files:**
- Create: `.claude-plugin/marketplace.json`
- Create: `plugins/arch-compliance/.claude-plugin/plugin.json`
- Create: `pyproject.toml`
- Create: `README.md` (stub install section)
- Create: `plugins/arch-compliance/python/acf/__init__.py`
- Create: `plugins/arch-compliance/python/acf/exceptions.py`
- Modify: rename git branch `master` → `main`

- [ ] **Step 1: Rename branch to main**

```bash
cd /c/Users/iball/Projects/arch-compliance-for-superpowers
git branch -M main
git branch --show-current
```

Expected: `main`

- [ ] **Step 2: Write marketplace + plugin manifests**

`.claude-plugin/marketplace.json`:
```json
{
  "name": "arch-compliance-for-superpowers",
  "owner": {
    "name": "IanDBallard"
  },
  "plugins": [
    {
      "name": "arch-compliance",
      "source": "./plugins/arch-compliance",
      "description": "Architecture compliance spine that complements Superpowers: mandate registry, dual TS/Python gates, LLM judge, audit."
    }
  ]
}
```

`plugins/arch-compliance/.claude-plugin/plugin.json`:
```json
{
  "name": "arch-compliance",
  "version": "0.1.0",
  "description": "Architecture Compliance Framework companion for Superpowers (Claude Code).",
  "author": {
    "name": "IanDBallard"
  }
}
```

- [ ] **Step 3: Write pyproject.toml**

```toml
[project]
name = "acf"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "pydantic>=2.0",
  "pyyaml>=6.0",
  "httpx>=0.27",
]

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[project.scripts]
acf-check-diff = "acf.cli_check_diff:main"
acf-check-llm = "acf.cli_check_llm:main"

[tool.pytest.ini_options]
testpaths = ["plugins/arch-compliance/tests"]
pythonpath = ["plugins/arch-compliance/python"]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["plugins/arch-compliance/python"]
```

- [ ] **Step 4: Write exceptions module**

```python
# plugins/arch-compliance/python/acf/exceptions.py
class AcfError(Exception):
    """Base for all ACF failures (fail loud)."""


class RegistryLoadError(AcfError):
    pass


class UnknownMandateError(AcfError):
    pass


class UnknownDetectorError(AcfError):
    pass


class JudgeNotConfiguredError(AcfError):
    pass


class EmptyTargetTreeError(AcfError):
    pass


class DetectorPackError(AcfError):
    pass
```

- [ ] **Step 5: Stub README + commit**

```bash
git add .claude-plugin/marketplace.json plugins/arch-compliance/.claude-plugin/plugin.json pyproject.toml \
  plugins/arch-compliance/python/acf/__init__.py plugins/arch-compliance/python/acf/exceptions.py README.md
git commit -m "feat: scaffold marketplace manifests and Python package layout"
```

---

### Task 2: Finding schema + mandate registry loader

**Files:**
- Create: `plugins/arch-compliance/python/acf/finding.py`
- Create: `plugins/arch-compliance/python/acf/registry.py`
- Create: `plugins/arch-compliance/tests/test_registry.py`
- Create: `plugins/arch-compliance/tests/fixtures/mandates_valid.yml`

- [ ] **Step 1: Write failing registry tests**

```python
# plugins/arch-compliance/tests/test_registry.py
from pathlib import Path
import pytest
from acf.registry import load_mandates
from acf.exceptions import RegistryLoadError, UnknownDetectorError

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_valid_mandates():
    regs = load_mandates(FIXTURES / "mandates_valid.yml")
    assert len(regs.mandates) >= 2
    assert regs.by_id["fail-loud.bare-except"].severity == "BLOCK"


def test_missing_file_fails_loud():
    with pytest.raises(RegistryLoadError):
        load_mandates(FIXTURES / "does-not-exist.yml")


def test_enforced_unknown_detector_fails():
    path = FIXTURES / "mandates_bad_detector.yml"
    path.write_text(
        "- id: x\n  title: t\n  severity: BLOCK\n  detection: ast\n"
        "  detector: not_a_real_detector\n  languages: python\n"
        "  call_sites: [ci]\n  exemption_tokens: [x]\n  status: enforced\n"
        "  arch_anchor: '# X'\n",
        encoding="utf-8",
    )
    with pytest.raises(UnknownDetectorError):
        load_mandates(path, known_detectors=frozenset({"fail_loud_bare_except"}))
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
cd /c/Users/iball/Projects/arch-compliance-for-superpowers
pip install -e ".[dev]"
pytest plugins/arch-compliance/tests/test_registry.py -v
```

Expected: FAIL (`acf.registry` missing)

- [ ] **Step 3: Implement finding + registry**

```python
# plugins/arch-compliance/python/acf/finding.py
from __future__ import annotations
from enum import Enum
from pydantic import BaseModel, Field


class Severity(str, Enum):
    BLOCK = "BLOCK"
    WARN = "WARN"


class Finding(BaseModel):
    mandate_id: str
    severity: Severity
    path: str  # POSIX
    line: int
    message: str
    detector: str
    confidence: str | None = None
    detection: str = "ast"
```

```python
# plugins/arch-compliance/python/acf/registry.py
from __future__ import annotations
from pathlib import Path
from typing import Literal
import yaml
from pydantic import BaseModel, Field, field_validator
from acf.exceptions import RegistryLoadError, UnknownDetectorError

Detection = Literal["ast", "llm", "grep", "guard", "manual"]
Status = Literal["enforced", "partial", "unenforced"]
Language = Literal["python", "typescript", "both", "none"]


class Mandate(BaseModel):
    id: str
    title: str
    severity: Literal["BLOCK", "WARN"]
    detection: Detection
    detector: str
    languages: Language
    call_sites: list[str]
    exemption_tokens: list[str]
    status: Status
    arch_anchor: str
    auditor: str | None = None


class MandateRegistry(BaseModel):
    mandates: list[Mandate]
    source_path: str

    @property
    def by_id(self) -> dict[str, Mandate]:
        return {m.id: m for m in self.mandates}


def load_mandates(
    path: Path,
    *,
    known_detectors: frozenset[str] | None = None,
) -> MandateRegistry:
    if not path.is_file():
        raise RegistryLoadError(f"mandates file not found: {path.as_posix()}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise RegistryLoadError(f"invalid YAML in {path.as_posix()}: {e}") from e
    if not isinstance(raw, list):
        raise RegistryLoadError(f"mandates root must be a list: {path.as_posix()}")
    try:
        mandates = [Mandate.model_validate(row) for row in raw]
    except Exception as e:
        raise RegistryLoadError(f"mandate validation failed: {e}") from e
    if known_detectors is not None:
        for m in mandates:
            if m.status == "enforced" and m.detection == "ast" and m.detector not in known_detectors:
                raise UnknownDetectorError(
                    f"enforced mandate {m.id!r} references unknown detector {m.detector!r}"
                )
    return MandateRegistry(mandates=mandates, source_path=path.as_posix())
```

Write `tests/fixtures/mandates_valid.yml` with at least `fail-loud.bare-except` and `no-shims.hasattr` (python) plus one typescript row.

- [ ] **Step 4: Run tests — expect PASS**

```bash
pytest plugins/arch-compliance/tests/test_registry.py -v
```

- [ ] **Step 5: Commit**

```bash
git add plugins/arch-compliance/python/acf/finding.py plugins/arch-compliance/python/acf/registry.py \
  plugins/arch-compliance/tests/
git commit -m "feat: add Finding schema and mandate registry loader"
```

---

### Task 3: Python detector pack

**Files:**
- Create: `plugins/arch-compliance/python/acf/detectors/python_pack.py`
- Create: `plugins/arch-compliance/python/acf/engine.py`
- Create: `plugins/arch-compliance/tests/test_python_pack.py`
- Create: `plugins/arch-compliance/tests/fixtures/python/bad_except.py`
- Create: `plugins/arch-compliance/tests/fixtures/python/good.py`

- [ ] **Step 1: Write failing detector tests**

```python
from pathlib import Path
from acf.detectors.python_pack import scan_python_file
from acf.finding import Severity

FIX = Path(__file__).parent / "fixtures" / "python"


def test_bare_except_detected():
    text = (FIX / "bad_except.py").read_text(encoding="utf-8")
    findings = scan_python_file(text, "bad_except.py", added_lines=frozenset({3}))
    assert any(f.mandate_id == "fail-loud.bare-except" and f.severity == Severity.BLOCK for f in findings)


def test_clean_file_no_findings():
    text = (FIX / "good.py").read_text(encoding="utf-8")
    findings = scan_python_file(text, "good.py", added_lines=frozenset({1, 2, 3}))
    assert findings == []


def test_exemption_skips():
    text = "try:\n    x()\nexcept Exception:  # fail-loud.bare-except-ok: legacy bridge\n    pass\n"
    findings = scan_python_file(text, "ex.py", added_lines=frozenset({3}))
    assert findings == []
```

Fixture `bad_except.py`:
```python
def f():
    try:
        g()
    except Exception:
        pass
```

- [ ] **Step 2: Run — expect FAIL**

```bash
pytest plugins/arch-compliance/tests/test_python_pack.py -v
```

- [ ] **Step 3: Implement python_pack + engine helpers**

Implement AST walkers for:
- bare/`except Exception` → `fail-loud.bare-except`
- `hasattr(` → `no-shims.hasattr`
- backslash string literals that look like Windows paths in `.yml`/`.json` companion check can live in a separate path helper later; for Python source, flag `str(pathy)` serialization pattern optionally.

Reuse exemption forms:
- `# <token>-ok: <reason>`
- `# arch-ok: <token> <reason>`

Export `PYTHON_DETECTOR_IDS = frozenset({...})` for registry validation.

Diff-scope: only emit findings whose `line` is in `added_lines` (if `added_lines` non-empty); if empty, scan whole file (audit mode).

- [ ] **Step 4: Run — expect PASS + commit**

```bash
pytest plugins/arch-compliance/tests/test_python_pack.py -v
git add plugins/arch-compliance/python/acf/detectors plugins/arch-compliance/python/acf/engine.py \
  plugins/arch-compliance/tests/test_python_pack.py plugins/arch-compliance/tests/fixtures/python
git commit -m "feat: add Python AST detector pack"
```

---

### Task 4: TypeScript/React detector pack (ts-morph)

**Files:**
- Create: `plugins/arch-compliance/detectors/typescript/package.json`
- Create: `plugins/arch-compliance/detectors/typescript/tsconfig.json`
- Create: `plugins/arch-compliance/detectors/typescript/src/scan.ts`
- Create: `plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts`
- Create: `plugins/arch-compliance/detectors/typescript/src/rules/explicitAny.ts`
- Create: `plugins/arch-compliance/tests/fixtures/typescript/bad.tsx`
- Create: `plugins/arch-compliance/tests/fixtures/typescript/good.tsx`
- Create: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py`
- Create: `plugins/arch-compliance/tests/test_typescript_pack.py`

- [ ] **Step 1: Scaffold Node package**

```json
{
  "name": "acf-typescript-detectors",
  "private": true,
  "type": "module",
  "scripts": {
    "scan": "tsx src/scan.ts",
    "test": "tsx src/scan.ts --self-test"
  },
  "dependencies": {
    "ts-morph": "^24.0.0",
    "typescript": "^5.6.0"
  },
  "devDependencies": {
    "tsx": "^4.19.0"
  }
}
```

- [ ] **Step 2: Implement scanner CLI emitting JSON findings**

`scan.ts` argv: `--file <path> --lines 1,2,3` (optional line filter). stdout:
```json
[{"mandate_id":"fail-loud.empty-catch","severity":"BLOCK","path":"x.tsx","line":4,"message":"...","detector":"empty_catch"}]
```

Rules (v1 equal-peer set):
- empty `catch` / catch with only comment → `fail-loud.empty-catch`
- explicit `: any` / `as any` → `no-shims.explicit-any` (WARN by default in profile)

- [ ] **Step 3: Python bridge + test**

```python
# typescript_bridge.py — subprocess to node scanner; raise DetectorPackError on non-zero/invalid JSON
```

```python
def test_empty_catch_via_bridge(tmp_path):
    # write bad.tsx, call bridge, assert mandate_id
```

- [ ] **Step 4: Install deps, run tests, commit**

```bash
cd plugins/arch-compliance/detectors/typescript && npm install
cd /c/Users/iball/Projects/arch-compliance-for-superpowers
pytest plugins/arch-compliance/tests/test_typescript_pack.py -v
git add plugins/arch-compliance/detectors/typescript plugins/arch-compliance/python/acf/detectors/typescript_bridge.py \
  plugins/arch-compliance/tests/test_typescript_pack.py plugins/arch-compliance/tests/fixtures/typescript
git commit -m "feat: add TypeScript/React detector pack via ts-morph"
```

---

### Task 5: Diff driver + `acf-check-diff` CLI

**Files:**
- Create: `plugins/arch-compliance/python/acf/diff.py`
- Create: `plugins/arch-compliance/python/acf/cli_check_diff.py`
- Create: `plugins/arch-compliance/tests/test_diff_cli.py`

- [ ] **Step 1: Failing CLI test**

Use a temp git repo fixture with a planted bare `except` in an added line; invoke `main(["--mode", "staged", "--repo", str(tmp)])` or run as module; expect exit code 1 and BLOCK in stdout/JSON.

- [ ] **Step 2: Implement**

- `diff.changed_files(repo, mode=staged|worktree)` via `git diff --name-only` / `--cached`
- `diff.added_lines(repo, path, mode)` via `git diff -U0` parse
- Resolve host `config/architecture/mandates.yml` (fail loud if missing)
- Dispatch `.py` → python pack; `.ts`/`.tsx` → typescript bridge
- Exit 1 if any BLOCK; print findings as text + optional `--json`

- [ ] **Step 3: Pass + commit**

```bash
pytest plugins/arch-compliance/tests/test_diff_cli.py -v
git add plugins/arch-compliance/python/acf/diff.py plugins/arch-compliance/python/acf/cli_check_diff.py \
  plugins/arch-compliance/tests/test_diff_cli.py
git commit -m "feat: add diff-scoped check-diff CLI"
```

---

### Task 6: LLM judge (Tier 2 full)

**Files:**
- Create: `plugins/arch-compliance/python/acf/judge.py`
- Create: `plugins/arch-compliance/python/acf/cli_check_llm.py`
- Create: `plugins/arch-compliance/tests/test_judge.py`
- Create: `plugins/arch-compliance/tests/fixtures/judge_corpus/*.json`

- [ ] **Step 1: Failing tests**

```python
def test_judge_not_configured_hard_fails(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    with pytest.raises(JudgeNotConfiguredError):
        run_judge(diff_text="...", mandates=[enforced_llm_mandate])


def test_confidence_gating():
    # mock provider returning confidence "medium" → WARN not BLOCK
```

- [ ] **Step 2: Implement provider interface**

```python
class JudgeProvider(Protocol):
    def review(self, *, diff_text: str, mandate: Mandate) -> JudgeResult: ...


class GeminiProvider:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"): ...
```

`JudgeResult`: mandate_id, severity suggestion, confidence (`high`|`medium`|`low`), message, path?, line?

Gating: `high` → keep BLOCK if mandate severity BLOCK; else force WARN.

- [ ] **Step 3: Calibration fixtures (n≥4 python + n≥4 ts)** documenting expected labels; unit test mock provider precision on fixtures.

- [ ] **Step 4: Pass + commit**

```bash
pytest plugins/arch-compliance/tests/test_judge.py -v
git commit -m "feat: add confidence-gated Gemini LLM judge"
```

---

### Task 7: Profiles (react-app + python-service)

**Files:**
- Create: `plugins/arch-compliance/profiles/react-app/mandates.yml`
- Create: `plugins/arch-compliance/profiles/react-app/ARCHITECTURE.md`
- Create: `plugins/arch-compliance/profiles/python-service/mandates.yml`
- Create: `plugins/arch-compliance/profiles/python-service/ARCHITECTURE.md`
- Create: `plugins/arch-compliance/tests/test_profile_drift.py`

- [ ] **Step 1: Author portable mandate rows** (no HM façades). Each `arch_anchor` must exist in the profile `ARCHITECTURE.md`. Detectors referenced must exist in pack registries.

- [ ] **Step 2: Drift test** loads profile mandates with `known_detectors=PYTHON_DETECTOR_IDS | TS_DETECTOR_IDS | LLM_PROMPT_IDS` and asserts every `arch_anchor` heading exists in the sibling ARCHITECTURE.md.

- [ ] **Step 3: Commit**

```bash
git commit -m "feat: add react-app and python-service starter profiles"
```

---

### Task 8: Skills — `/acf-setup` and `/acf-mandate`

**Files:**
- Create: `plugins/arch-compliance/skills/acf-setup/SKILL.md`
- Create: `plugins/arch-compliance/skills/acf-mandate/SKILL.md`

- [ ] **Step 1: Write `/acf-setup` skill** with exact steps: detect languages (glob `package.json`+`tsx`/`jsx`, `pyproject.toml`/`*.py`); copy matching profile(s) to host `config/architecture/`; prompt for ARCHITECTURE.md path; print pre-commit snippet invoking `acf-check-diff`; run smoke check command; remind Superpowers prerequisite.

- [ ] **Step 2: Write `/acf-mandate` skill** with schema fields, validation via `python -c "from acf.registry import load_mandates; ..."`, rules for add/edit/deprecate, and reminder that new `ast`/`llm` detectors need code/prompt stubs (no codegen).

- [ ] **Step 3: Commit**

```bash
git commit -m "feat: add acf-setup and acf-mandate Claude skills"
```

---

### Task 9: Skill — `/architecture-review` + baseline/drift

**Files:**
- Create: `plugins/arch-compliance/skills/architecture-review/SKILL.md`
- Create: `plugins/arch-compliance/skills/architecture-review/auditors/{fail-loud,no-shims,posix-paths,react-boundaries}.md`
- Create: `plugins/arch-compliance/python/acf/baseline.py`
- Create: `plugins/arch-compliance/tests/test_baseline.py`

- [ ] **Step 1: Baseline module tests** — aggregate findings → cells keyed by `(mandate_id, subsystem)`; load/save JSON with POSIX paths; drift report-only.

- [ ] **Step 2: Skill** — resolve mandates/facets; dispatch parallel read-only auditors (Superpowers `dispatching-parallel-agents`); parse payloads; write Markdown report under host `docs/architecture/`; optional `--update-baseline`.

- [ ] **Step 3: Commit**

```bash
git commit -m "feat: add architecture-review skill and baseline/drift"
```

---

### Task 10: Hooks — constraint injection + PostToolUse gate

**Files:**
- Create: `plugins/arch-compliance/hooks/hooks.json`
- Create: `plugins/arch-compliance/hooks/inject_constraints.py`
- Create: `plugins/arch-compliance/hooks/posttooluse_gate.py`
- Create: `plugins/arch-compliance/hooks/constraints_template.md`

- [ ] **Step 1: `inject_constraints.py`** reads host `config/architecture/mandates.yml` + ARCHITECTURE excerpt; prints constraint block for SubagentStart (fail loud if registry missing when hook enabled — or no-op with clear stderr if not yet set up? **Spec: fail loud when hook runs and config expected**; `/acf-setup` documents enabling hooks only after setup). Prefer: if `config/architecture/mandates.yml` absent, exit 0 with empty injection and stderr warning once — setup skill enables “strict” mode via marker file `.acf/enabled`. **Lock:** marker file `.acf/enabled` written by setup; hooks no-op until present; when present, missing registry → non-zero.

- [ ] **Step 2: `posttooluse_gate.py`** runs python/ts detectors on edited paths; returns findings to stdout for Claude to consume.

- [ ] **Step 3: Document hook registration in README + setup skill.**

- [ ] **Step 4: Commit**

```bash
git commit -m "feat: add SubagentStart constraint injection and PostToolUse gate hooks"
```

---

### Task 11: Docs — Superpowers complement + README polish

**Files:**
- Create: `docs/guides/SUPERPOWERS_COMPLEMENT.md`
- Modify: `README.md`
- Modify: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md` (status → plan approved / implementing)

- [ ] **Step 1: Guide** explains install order (Superpowers first), override contract, skills list, env vars (`GEMINI_API_KEY`), friend success bar.

- [ ] **Step 2: README** with:

```text
/plugin marketplace add IanDBallard/arch-compliance-for-superpowers
/plugin install arch-compliance@arch-compliance-for-superpowers
```

- [ ] **Step 3: Commit**

```bash
git commit -m "docs: add Superpowers complement guide and install README"
```

---

### Task 12: CI workflow + GitHub publish

**Files:**
- Create: `.github/workflows/ci.yml`
- Remote: `IanDBallard/arch-compliance-for-superpowers`

- [ ] **Step 1: CI** — setup Python + Node; `pip install -e ".[dev]"`; `npm ci` in TS detector dir; `pytest`; TS self-test.

- [ ] **Step 2: Create public GitHub repo and push**

```bash
cd /c/Users/iball/Projects/arch-compliance-for-superpowers
gh repo create IanDBallard/arch-compliance-for-superpowers --public --source=. --remote=origin --push
```

If repo exists: `git remote add origin …` && `git push -u origin main`.

- [ ] **Step 3: Smoke**

```bash
claude --plugin-dir ./plugins/arch-compliance -p "reply with ok" 
# or document manual /plugin marketplace add for the friend
```

- [ ] **Step 4: Final commit if needed + verify remote**

```bash
git status
gh repo view IanDBallard/arch-compliance-for-superpowers --json url -q .url
```

---

## Spec coverage checklist (self-review)

| Spec requirement | Task |
|---|---|
| Marketplace + plugin manifests | 1, 12 |
| Registry spine + drift | 2, 7 |
| Finding schema | 2 |
| Python pack | 3 |
| TS/React pack | 4 |
| Diff gate CLI | 5 |
| Full LLM judge + hard-fail if missing | 6 |
| Profiles react + python | 7 |
| `/acf-setup`, `/acf-mandate` | 8 |
| `/architecture-review` + baseline | 9 |
| Hooks injection + PostToolUse | 10 |
| Superpowers complement docs | 11 |
| GitHub publish for friend install | 12 |
| No HM-specific detectors | 3–7 (portable only) |
| No auto-remediation / no Cursor packaging | honored (omitted) |

---

## Execution handoff

Plan saved to `docs/plans/PLAN_ARCH_COMPLIANCE_FOR_SUPERPOWERS.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)** — fresh subagent per task, review between tasks  
2. **Inline Execution** — execute tasks in this session with checkpoints  

Which approach?
