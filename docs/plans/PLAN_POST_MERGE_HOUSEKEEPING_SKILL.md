# Portable `post-merge-housekeeping` Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract and generalize `post-merge-housekeeping` into `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` as a stack-, forge-, and layout-neutral governance skill, restore cross-skill handoffs from `adversarial-design-review` and `responding-to-adversarial-review`, and extend the skill-prose portability, invariant, self-host, and installed-skill checks.

**Architecture:** `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` reads host-specific operational conventions from the `## Post-merge` section of the host's doctrine (`config/architecture/ARCHITECTURE.md`) and ADR paths (`runs_dir`, `ledger_path`) from `config/architecture/adr.yml` via `acf.repo.resolve_repo`, `acf.repo.ADR_REL`, and `acf.adr.load_host_config`. Step 6 resolves `dispatch_commit_sha` from line 3 of the highest-`(int(N), YYYY-MM-DD)` `<STEM>_v<N>_<YYYY-MM-DD>.md` run-detail file in `repo / cfg.runs_dir` (excluding `_response_` files), matching the aligned Step 2b-ii rule in `adversarial-design-review/SKILL.md`.

**Tech Stack:** Python 3.11+, pytest, Markdown skill definitions (`plugins/arch-compliance/skills/`), YAML mandate registry (`config/architecture/mandates.yml`).

**Spec:** `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md`

## Global Constraints

- **No origin-host vocabulary in skill prose (`## Prose names no host`):** `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` must contain zero literals from `FORBIDDEN` (`"GEMINI"`, `"CLAUDE.md"`, `"SKILL_PROVENANCE"`, `"scripts.core"`, `"docs/design"`, `"docs/reviews"`, `"docs/architecture"`, `".cursor"`, `"run_cms_e2e"`, `"expected_branch.txt"`, `"CMS_SKIP_BRANCH_GUARD"`, `"ARCHITECTURE_REVIEW_2026"`).
- **No backslashes in skill prose (`## POSIX paths`):** Every `.md` file under `plugins/arch-compliance/skills/{adversarial-design-review,responding-to-adversarial-review,post-merge-housekeeping}` must contain zero `\` characters (`test_no_skill_file_contains_a_backslash`).
- **Valid AST & existing imports in skill Python blocks:** Every fenced ```` ```python ```` block in `post-merge-housekeeping/SKILL.md` must parse with `ast.parse`, import only existing `acf.*` symbols, and never hardcode `absorbed=0`.
- **Declared, never defaulted (`## Declared, never defaulted`):** Omitted checks under `## Post-merge` are explicitly reported as `<check>: not declared in ## Post-merge, skipped` in Step 8; default branch resolution in Step 1 is strictly read-only and never guesses `main`.
- **Release discipline (`## Release discipline`):** Bump version to `"0.2.2"` in both `pyproject.toml` and `plugins/arch-compliance/.claude-plugin/plugin.json`, add `"post-merge-housekeeping"` to `GATE_SKILLS` in `scripts/check_installed_skills.py`, and update `CLAUDE.md`, `config/architecture/ARCHITECTURE.md`, `config/architecture/mandates.yml`, `README.md`, and `docs/guides/SUPERPOWERS_COMPLEMENT.md`.

## Review Focus

1. **Backslash introduced in bash/PowerShell/regex examples inside `post-merge-housekeeping/SKILL.md`** — `test_no_skill_file_contains_a_backslash` in Task 1 pins zero `\` across the entire skill file, and a mutation step verifies planting `\` fails `pytest`.
2. **Origin-host housekeeping literal (`run_cms_e2e`, `expected_branch.txt`, `CMS_SKIP_BRANCH_GUARD`, `ARCHITECTURE_REVIEW_2026`) leaking into skill prose** — `FORBIDDEN` in `test_adr_skill_prose.py` (Task 1) scans every line of `post-merge-housekeeping/SKILL.md`, verified by planting and restoring a forbidden token.
3. **`absorbed=0` hardcoded in Step 6's `LedgerAmendment` snippet** — `test_housekeeping_skill_invariants` (Task 1) extracts fenced ```` ```python ```` blocks and asserts `"absorbed=0"` is absent while prose discussing `LedgerRow` dispatch-time zeros remains allowed.
4. **Verification-pass or `_response_` file collision when looking up `dispatch_commit_sha`** — `test_housekeeping_skill_invariants` (Task 1) and `test_gate_names_the_pre_dispatch_stop_and_the_ledger_reread` (Task 2) pin `_response_` exclusion and `(int(N),` ordering in both `post-merge-housekeeping/SKILL.md` and `adversarial-design-review/SKILL.md`.
5. **Doctrine anchor mismatch in `config/architecture/ARCHITECTURE.md` after adding `## Post-merge` and updating `mandates.yml`** — `tests/test_self_host.py` (Task 3) verifies every `mandates.yml` `arch_anchor` resolves in `ARCHITECTURE.md` and `## Post-merge` ends with a `No row:` line.

---

### Task 1: Create `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` and extend skill prose & invariant tests

**Files:**
- Modify: `plugins/arch-compliance/tests/test_adr_skill_prose.py:9-42`
- Modify: `plugins/arch-compliance/tests/test_adr_skill_invariants.py:12-99`
- Create: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md`

**Interfaces:**
- Consumes: `acf.adr.{LedgerAmendment, append_amendment, load_host_config}`, `acf.repo.{ADR_REL, resolve_repo}`
- Produces: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md`, updated `FILES` / `FORBIDDEN` / `_python_bodies()` in `plugins/arch-compliance/tests/test_adr_skill_prose.py`, and `test_housekeeping_skill_invariants()` in `plugins/arch-compliance/tests/test_adr_skill_invariants.py`

- [x] **Step 1: Write the failing tests in `test_adr_skill_prose.py` and `test_adr_skill_invariants.py`**

Update `plugins/arch-compliance/tests/test_adr_skill_prose.py` lines 9–46 to add `HOUSEKEEPING`:

```python
SKILLS = Path(__file__).resolve().parents[1] / "skills"
GATE = SKILLS / "adversarial-design-review"
RESPOND = SKILLS / "responding-to-adversarial-review"
HOUSEKEEPING = SKILLS / "post-merge-housekeeping"
FILES = [
    GATE / "SKILL.md", GATE / "claims" / "extraction.md",
    GATE / "reviewers" / "compliance.md", GATE / "reviewers" / "hardening.md",
    GATE / "reviewers" / "refuter.md", GATE / "reviewers" / "sweeper.md",
    RESPOND / "SKILL.md",
    HOUSEKEEPING / "SKILL.md",
]
FORBIDDEN = [
    "GEMINI", "CLAUDE.md", "SKILL_PROVENANCE", "scripts.core",
    "docs/design", "docs/reviews", "docs/architecture", ".cursor",
    "run_cms_e2e", "expected_branch.txt", "CMS_SKIP_BRANCH_GUARD",
    "ARCHITECTURE_REVIEW_2026",
]


def _python_bodies() -> list[tuple[str, str]]:
    bodies = []
    for skill in (GATE / "SKILL.md", RESPOND / "SKILL.md", HOUSEKEEPING / "SKILL.md"):
        text = skill.read_text(encoding="utf-8")
        bodies += [(f"{skill.parent.name}:python", b) for b in re.findall(r"```python\n(.*?)```", text, re.S)]
        bodies += [(f"{skill.parent.name}:python -c", b) for b in re.findall(r'python -c "\n(.*?)"\n', text, re.S)]
    return bodies
```

Update `plugins/arch-compliance/tests/test_adr_skill_invariants.py` to add `HOUSEKEEPING`, include it in frontmatter and backslash checks, and add `test_housekeeping_skill_invariants()`:

```python
SKILLS = Path(__file__).resolve().parents[1] / "skills"
GATE = SKILLS / "adversarial-design-review"
RESPOND = SKILLS / "responding-to-adversarial-review"
HOUSEKEEPING = SKILLS / "post-merge-housekeeping"
```

```python
_ACF_REPO_IMPORT_RE = re.compile(r"^from acf\.repo import .*$", re.MULTILINE)
_PY_FENCE_BODY_RE = re.compile(r"```python\n(.*?)```", re.S)
```

```python
def test_both_skills_have_frontmatter_with_a_name_and_description():
    for root in (GATE, RESPOND, HOUSEKEEPING):
        body = _read(root / "SKILL.md")
        assert body.startswith("---\n"), root.name
        assert f"name: {root.name}\n" in body, root.name
        assert "description:" in body, root.name
```

```python
def test_no_skill_file_contains_a_backslash():
    for root in (GATE, RESPOND, HOUSEKEEPING):
        for path in sorted(root.rglob("*.md")):
            assert "\\" not in _read(path), path.relative_to(SKILLS).as_posix()
```

```python
def test_housekeeping_skill_invariants():
    body = _read(HOUSEKEEPING / "SKILL.md")
    adr_imported = "\n".join(_ACF_ADR_IMPORT_RE.findall(body))
    for symbol in ("LedgerAmendment", "append_amendment", "load_host_config"):
        assert symbol in adr_imported, f"{symbol} must be imported in a real `from acf.adr import` line"
    repo_imported = "\n".join(_ACF_REPO_IMPORT_RE.findall(body))
    for symbol in ("ADR_REL", "resolve_repo"):
        assert symbol in repo_imported, f"{symbol} must be imported in a real `from acf.repo import` line"
    for required in (
        "dispatch_commit_sha",
        "_response_",
        "(int(N),",
        "## Post-merge",
        "not declared in ## Post-merge, skipped",
        "refs/remotes/origin/HEAD",
        "git ls-remote --symref origin HEAD",
        "headRefOid",
        "git fetch --prune",
        "What ALREADY gets through the guard we just shipped?",
    ):
        assert required in body, f"missing required housekeeping invariant: {required}"
    py_blocks = _PY_FENCE_BODY_RE.findall(body)
    assert py_blocks, "expected at least one fenced ```python block in post-merge-housekeeping/SKILL.md"
    for block in py_blocks:
        assert "absorbed=0" not in block.replace(" ", "")
```

- [x] **Step 2: Run pytest to verify the new tests fail because `post-merge-housekeeping/SKILL.md` does not exist yet**

Run: `python -m pytest plugins/arch-compliance/tests/test_adr_skill_prose.py plugins/arch-compliance/tests/test_adr_skill_invariants.py -q`
Expected: FAIL (`FileNotFoundError` / `missing` on `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md`).

- [x] **Step 3: Create `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md`**

Create `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` with zero backslashes and zero `FORBIDDEN` tokens, implementing Steps 0 through 8 and the fenced Python `LedgerAmendment` snippet of spec §5.1–§5.2.

- [x] **Step 4: Run pytest to verify `test_adr_skill_prose.py` and `test_adr_skill_invariants.py` pass, and run the negative mutation check (DoD 2)**

Run: `python -m pytest plugins/arch-compliance/tests/test_adr_skill_prose.py plugins/arch-compliance/tests/test_adr_skill_invariants.py -q`
Expected: PASS.
Also verify DoD 2: temporarily plant a `FORBIDDEN` token (`run_cms_e2e`) and a backslash in `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md`, confirm `pytest` fails, and restore.

---

### Task 2: Restore cross-skill handoffs in `adversarial-design-review` and `responding-to-adversarial-review` and align Step 2b-ii run-detail selection

**Files:**
- Modify: `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:128-131, 363`
- Modify: `plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:223`
- Modify: `plugins/arch-compliance/tests/test_adr_skill_invariants.py:49-55, 95-125`

**Interfaces:**
- Consumes: `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md`
- Produces: Cross-skill references to `post-merge-housekeeping` in both gate skills and aligned `(int(N), <date>)` run-detail selection in `adversarial-design-review/SKILL.md:128-131`

- [x] **Step 1: Add cross-skill assertions to `plugins/arch-compliance/tests/test_adr_skill_invariants.py`**

In `test_housekeeping_skill_invariants()`, add:

```python
    assert "post-merge-housekeeping" in _read(GATE / "SKILL.md")
    assert "(int(N), <date>)" in _read(GATE / "SKILL.md")
    assert "post-merge-housekeeping" in _read(RESPOND / "SKILL.md")
```

- [x] **Step 2: Run pytest to verify the new assertions fail**

Run: `python -m pytest plugins/arch-compliance/tests/test_adr_skill_invariants.py -q`
Expected: FAIL on `assert "post-merge-housekeeping" in _read(GATE / "SKILL.md")`.

- [x] **Step 3: Update `adversarial-design-review/SKILL.md` and `responding-to-adversarial-review/SKILL.md`**

In `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:128-131`:

```markdown
**2b-ii. Revision-evidence check (re-runs only).** A run is a re-run when a run
detail for this spec exists in this checkout under the declared `runs_dir` — a file
shaped `<SPEC_STEM>_v<N>_<date>.md`, **excluding** files with a `_response_` segment.
Select the one with the highest `(int(N), <date>)` and read its `Outcome:` line.
```

In `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:363`:

```markdown
(`absorbed`, `rejected`, `blocks_overturned`, `escapes`) are `0` / `None` at write time
and are amended later by `post-merge-housekeeping` appending a superseding record
```

In `plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:223`:

```markdown
has re-read the row it just wrote. After merge, `post-merge-housekeeping` owns the
`absorbed` / `rejected` / `escapes` amendment — do not leave those at the write-time
zeros.
```

- [x] **Step 4: Run pytest to verify `test_adr_skill_invariants.py` and `test_adr_skill_prose.py` pass**

Run: `python -m pytest plugins/arch-compliance/tests/test_adr_skill_prose.py plugins/arch-compliance/tests/test_adr_skill_invariants.py -q`
Expected: PASS.

---

### Task 3: Update `scripts/check_installed_skills.py`, `CLAUDE.md`, `config/architecture/ARCHITECTURE.md`, `config/architecture/mandates.yml`, `README.md`, `docs/guides/SUPERPOWERS_COMPLEMENT.md`, and bump version to `0.2.2`

**Files:**
- Modify: `scripts/check_installed_skills.py:1-19`
- Modify: `CLAUDE.md:20-24`
- Modify: `config/architecture/ARCHITECTURE.md:135-142, 182-192, 214-225`
- Modify: `config/architecture/mandates.yml:192-194`
- Modify: `README.md:28-35`
- Modify: `docs/guides/SUPERPOWERS_COMPLEMENT.md:38-43`
- Modify: `pyproject.toml:3`
- Modify: `plugins/arch-compliance/.claude-plugin/plugin.json:3`
- Modify: `tests/test_self_host.py`

**Interfaces:**
- Consumes: `scripts/check_installed_skills.py`, `config/architecture/ARCHITECTURE.md`, `config/architecture/mandates.yml`
- Produces: `GATE_SKILLS` with 3 skills, `## Post-merge` section in `config/architecture/ARCHITECTURE.md`, version `"0.2.2"` in `pyproject.toml` and `plugin.json`

- [x] **Step 1: Add self-host assertions in `tests/test_self_host.py`**

Read `tests/test_self_host.py` and add a test asserting that `## Post-merge` exists in `config/architecture/ARCHITECTURE.md`, ends with `No row: host operational declarations; no test enforces this.`, and `GATE_SKILLS` in `scripts/check_installed_skills.py` contains `"post-merge-housekeeping"`.

- [x] **Step 2: Run `pytest tests/test_self_host.py tests/test_check_installed_skills.py -q` to verify it fails**

Run: `python -m pytest tests/test_self_host.py tests/test_check_installed_skills.py -q`
Expected: FAIL on missing `## Post-merge` and missing `"post-merge-housekeeping"` in `GATE_SKILLS`.

- [x] **Step 3: Apply the updates to `scripts/check_installed_skills.py`, `CLAUDE.md`, `config/architecture/ARCHITECTURE.md`, `config/architecture/mandates.yml`, `README.md`, `docs/guides/SUPERPOWERS_COMPLEMENT.md`, `pyproject.toml`, and `plugins/arch-compliance/.claude-plugin/plugin.json`**

1. In `scripts/check_installed_skills.py`:
   ```python
   GATE_SKILLS = (
       "adversarial-design-review",
       "responding-to-adversarial-review",
       "post-merge-housekeeping",
   )
   ```
   and update the module docstring (`{adversarial-design-review,responding-to-adversarial-review,post-merge-housekeeping}`).
2. In `CLAUDE.md:20-23`:
   ```markdown
   - **Before any gate or post-merge-housekeeping run:** `python scripts/check_installed_skills.py <INSTALL_PATH>`
     (`INSTALL_PATH` is the plugin's `installPath` in
     `~/.claude/plugins/installed_plugins.json`). The rule and what to do on a mismatch are
     the doctrine's `## Release discipline`; never hand-run the review.
   ```
3. In `config/architecture/ARCHITECTURE.md`:
   - Update `## Prose names no host` (`:135-141`) to state that `plugin.gate-prose-names-no-host` (`plugins/arch-compliance/tests/test_adr_skill_prose.py`) checks the two gate skills and `post-merge-housekeeping` against the enumerated `FORBIDDEN` list of known origin-host (`HistoricMansions`) vocabulary (the other three skills in `plugins/arch-compliance/skills/` have no row yet).
   - Update `## Release discipline` (`:182-191`) from `"the two gate skills"` / `"those two skill trees"` to `"the two gate skills and post-merge-housekeeping"` / `"those three skill trees"`.
   - Append `## Post-merge`:
     ```markdown
     ## Post-merge

     Host operational declarations read by `post-merge-housekeeping`:

     - **Shared-checkout branch lock:** none declared.
     - **Worktree daemon probe:** none declared (tests spawn no background server).
     - **Post-merge CI workflows:** `.github/workflows/ci.yml` (`test` job on `main`).
     - **Durable tracking target:** GitHub Issues on `IanDBallard/arch-compliance-for-superpowers` (`gh issue create`), so filing a follow-up or guard escape never edits an already-cleared spec.

     No row: host operational declarations; no test enforces this.
     ```
4. In `config/architecture/mandates.yml:193`:
   ```yaml
   - id: plugin.gate-prose-names-no-host
     title: The gate and housekeeping skills' prose contains no known origin-host vocabulary
   ```
5. In `README.md:28-35`, add:
   ```markdown
   | `/post-merge-housekeeping` | Post-merge verification, worktree/branch teardown, doc reconciliation, and ADR ledger amendment |
   ```
6. In `docs/guides/SUPERPOWERS_COMPLEMENT.md:38-43`, add rows for `/adversarial-design-review`, `/responding-to-adversarial-review`, and `/post-merge-housekeeping`.
7. In `pyproject.toml:3` and `plugins/arch-compliance/.claude-plugin/plugin.json:3`, bump `"0.2.1"` to `"0.2.2"`.

- [x] **Step 4: Run full verification suite**

Run:
- `python -m pytest -q`
- `PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main`
- `npm test --prefix plugins/arch-compliance/detectors/typescript`
Expected: All pass with 0 BLOCK findings and `self-test OK`.

- [x] **Step 5: Commit and verify clean git status**

Commit all changes on `feat/post-merge-housekeeping`.
