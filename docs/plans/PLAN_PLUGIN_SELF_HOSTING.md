# Plugin Self-Hosting and Doctrine — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** This repository declares itself a host of the plugin's adversarial-design-review gate, gains a written doctrine in the plugin's own registry format, and proves both with a live gate run on the spec that designed them.

**Architecture:** `/acf-setup` bootstraps the stock registry and doctrine pair into `config/architecture/`; the pair is then extended with the plugin's own rules (five of them as `detection: manual` registry rows pointing at the tests that enforce them). A root-level test pins the declaration, the anchors and the rows. `CLAUDE.md` records the session process, CI runs the diff gate on the repository's own changes, and the host-contract spec moves here from HM. The acceptance run writes the first records under `docs/reviews/`.

**Tech Stack:** Python 3.11+, pydantic v2, PyYAML, pytest; Claude Code plugin CLI; the `acf` package (editable install). No new dependency.

**Spec:** `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` (v1, user-approved 2026-10-22; repo @ `8dabe82`). Section references (§N) are the spec's. Read it in full; its §0 citation convention also governs this plan.

## Global Constraints

- **Start condition (§5.7 step 1, §4.1 item 13):** HM phase 1d has merged, so (a) `plugins/arch-compliance/tests/test_adr_skill_invariants.py` is on this repository's `main`, and (b) the plugin is installed on this node from this clone (`claude plugin list` shows `arch-compliance@arch-compliance-for-superpowers`). Nothing in this plan installs the plugin.
- **Worktree:** `C:/Users/iball/Arduino/Projects/arch-compliance-worktrees/self-host`, branch `feat/self-host`, base = `origin/main` at or after the 1d pin merge. Every task verifies `git branch --show-current` prints `feat/self-host` before editing (abort BLOCKED otherwise). All commands run from the worktree root unless a step says otherwise.
- **`config/architecture/adr.yml` is exactly** (§5.1): `runs_dir: docs/reviews/adr_runs` / `ledger_path: docs/reviews/adversarial_design_ledger.jsonl`. No other key.
- **Every stock anchor survives verbatim** in `ARCHITECTURE.md` (§5.2): `## Fail loud`, `## No shims`, `## POSIX paths`, `## Build artifacts`, `## Fail-loud ratchet`, `## Façade sinks`, `## FSM transitions`, `## Soft fail-loud smells`, `## React boundaries`.
- **Stock rows that do not apply are `status: unenforced`, never deleted** (§5.2): `facade.forbid-sink`, `fsm.transition-guard`, `soft.react-boundaries`.
- **A manual row's `detector` names an existing test module** under `plugins/arch-compliance/tests/` (§5.2, §5.5). No row names a future test.
- **No change** to `acf.adr.ledger` models, any detector, any skill prose, or `plugins/arch-compliance/` outside this plan's file list (§3).
- **Windows:** run `acf.cli_check_diff` with `PYTHONUTF8=1` until §9 item 1 is fixed. Edit tracked files with the Edit tool or byte-level Python only (never `sed -i`, never a text-mode write).
- **Verification baseline** at `8dabe82`: `python -m pytest -q` → 395 passed (plus 1d's pins once merged); `npm test --prefix plugins/arch-compliance/detectors/typescript` → `self-test OK` (after `npm ci` there).
- **Commits** end with `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.

## Review Focus

1. **The same mandate id in both stock profiles** (`ops.no-build-artifacts`) — expected: one row after the merge, `languages: both`, never two rows one of which `by_id` silently shadows. Pinned by `test_mandate_ids_are_unique` (Task 3) and the merge check in Task 2.
2. **A `detection: manual` row reaching the diff gate** — expected: no detector emits its id, so it produces no finding and no error; the CLI exits 0 on a clean tree. Pinned in Task 4 step 7.
3. **A CRLF checkout of `ARCHITECTURE.md`** — expected: anchors still match, because the test and the plugin read through `read_text` (universal newlines). Pinned by `test_every_anchor_is_in_the_doctrine` reading with `read_text` (Task 3).
4. **The diff gate run from `plugins/arch-compliance/` instead of the root** — expected: a loud `acf: mandates file not found` on stderr and exit 1, never a silent pass. Pinned in Task 5 step 6.
5. **The self-host tests on a node with no `.acf/enabled` and no installed plugin (CI)** — expected: they pass from tracked files and the `acf` package alone. Pinned in Task 3 step 7.

---

### Task 1: Start condition and worktree

**Files:** none.

**Interfaces:**
- Produces: the worktree every later task runs in; `BASE_SHA` recorded in the ledger.

- [ ] **Step 1: Verify the start condition**

```bash
cd C:/Users/iball/Arduino/Projects/arch-compliance-for-superpowers
git fetch origin && git checkout main && git pull --ff-only
git ls-tree --name-only origin/main -- plugins/arch-compliance/tests/test_adr_skill_invariants.py
claude plugin list
```

Expected: the test path prints (1d Task 1 merged); `arch-compliance@arch-compliance-for-superpowers` is listed. If either is missing, stop: the plan does not start before 1d (spec §5.7 step 1). Record the install path `claude plugin list` reports as `INSTALL_PATH` in the ledger.

- [ ] **Step 2: Worktree**

```bash
git worktree add C:/Users/iball/Arduino/Projects/arch-compliance-worktrees/self-host -b feat/self-host origin/main
cd C:/Users/iball/Arduino/Projects/arch-compliance-worktrees/self-host
git branch --show-current          # feat/self-host
git rev-parse --short HEAD         # record as BASE_SHA
npm ci --prefix plugins/arch-compliance/detectors/typescript
python -m pytest -q                # expect all passed; record the count as BASELINE_TESTS
```

---

### Task 2: Bootstrap through `/acf-setup` (user-confirmed)

**Files:**
- Create: `config/architecture/mandates.yml`, `config/architecture/ARCHITECTURE.md` (stock merge), `.acf/enabled` (ignored, `.gitignore:8`)

**Interfaces:**
- Produces: the stock pair that Task 4 extends; the ids present after the merge:
  `fail-loud.bare-except`, `no-shims.hasattr`, `posix-paths.str-serialization`,
  `ops.no-build-artifacts`, `fail-loud.ratchet`, `facade.forbid-sink`, `fsm.transition-guard`,
  `soft.fail-loud`, `fail-loud.empty-catch`, `no-shims.explicit-any`, `soft.react-boundaries`.

- [ ] **Step 1: Ask the user, then run `/acf-setup` in a Claude Code session whose cwd is the worktree root.** It writes a per-developer marker and installs nothing new (the `acf` package and `node_modules` are already present from Task 1). Answers to its prompts, fixed by the spec: languages = **both** (Python under `plugins/arch-compliance/python/`, TypeScript with its own `package.json` under `plugins/arch-compliance/detectors/typescript/`; announce this if detection says Python only); step 5 = **one merged pair**; the duplicate id `ops.no-build-artifacts` = **keep one row, `languages: both`** (the python profile's row already says `both`); step 6 = **keep the new file at `config/architecture/ARCHITECTURE.md`** (this repository has no other doctrine); step 8 = print the snippets only (Task 6 edits CI).

- [ ] **Step 2: Check the merge**

```bash
grep -c '^- id:' config/architecture/mandates.yml                      # 11
grep -c 'id: ops.no-build-artifacts' config/architecture/mandates.yml  # 1
grep -nE '^## ' config/architecture/ARCHITECTURE.md
test -f .acf/enabled && echo marker
git status --short                                                      # only the two config files
```

Expected: 11 rows, one build-artifacts row, the nine stock anchors of Global Constraints, the marker, nothing else changed.

- [ ] **Step 3: Set the three non-applicable rows to `status: unenforced`** with the Edit tool (`facade.forbid-sink` and `fsm.transition-guard` already are in the python profile; `soft.react-boundaries` needs the edit). Add one comment line above each: `# unenforced here: <reason from spec §5.2>`. The two TypeScript rows (`fail-loud.empty-catch`, `no-shims.explicit-any`) stay `enforced` (spec §11, decided here): the bridge's `node_modules` is present locally from Task 1 and in CI from `npm ci`, and a `.ts` edit without it fails loud with `DetectorPackError` rather than passing silently.

- [ ] **Step 4: Smoke the gate**

```bash
PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --mode worktree
```

Expected: exit 0, no `acf:` error line (the config files are not `.py`/`.ts`).

- [ ] **Step 5: Commit**

```bash
git add config/architecture/mandates.yml config/architecture/ARCHITECTURE.md
git commit -m "chore(host): bootstrap the stock registry and doctrine pair via /acf-setup (both profiles merged)"
```

---

### Task 3: Declaration and the self-host test

**Files:**
- Create: `config/architecture/adr.yml`, `tests/test_self_host.py` (repository root)
- Modify: `pyproject.toml` (`[tool.pytest.ini_options] testpaths`)

**Interfaces:**
- Consumes: `acf.adr.load_host_config(repo: Path) -> AdrHostConfig`; `acf.registry.load_mandates(path, *, known_detectors)`; the detector-id union exactly as `plugins/arch-compliance/tests/test_profile_drift.py:9-14` builds it.
- Produces: the four test names below; `ROOT = Path(__file__).resolve().parents[1]`.

- [ ] **Step 1: Add the root tests directory to `pyproject.toml`**: `testpaths = ["plugins/arch-compliance/tests", "tests"]`. `pythonpath` is unchanged.

- [ ] **Step 2: Write the failing tests**

```python
"""This repository is a host of its own gate: the declaration, the doctrine and the
registry agree (spec docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md §5.5)."""
from __future__ import annotations

from pathlib import Path

from acf.adr import load_host_config
from acf.detectors import ALL_PYTHON_DETECTOR_IDS
from acf.detectors.typescript_bridge import TS_DETECTOR_IDS
from acf.judge import LLM_PROMPT_IDS
from acf.registry import load_mandates

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "architecture"
KNOWN_DETECTORS = ALL_PYTHON_DETECTOR_IDS | TS_DETECTOR_IDS | LLM_PROMPT_IDS


def _registry():
    return load_mandates(CONFIG / "mandates.yml", known_detectors=KNOWN_DETECTORS)


def test_declaration_names_the_reviews_tree():
    cfg = load_host_config(ROOT)
    assert cfg.runs_dir == "docs/reviews/adr_runs"
    assert cfg.ledger_path == "docs/reviews/adversarial_design_ledger.jsonl"


def test_every_anchor_is_in_the_doctrine():
    doctrine = (CONFIG / "ARCHITECTURE.md").read_text(encoding="utf-8")
    missing = [m.id for m in _registry().mandates if m.arch_anchor not in doctrine]
    assert missing == []


def test_every_manual_row_names_an_existing_test_module():
    rows = [m for m in _registry().mandates if m.detection == "manual"]
    assert rows, "no manual rows: Task 4 adds five"
    missing = [m.id for m in rows if not (ROOT / m.detector).is_file()
               or not m.detector.startswith("plugins/arch-compliance/tests/")]
    assert missing == []


def test_mandate_ids_are_unique():
    ids = [m.id for m in _registry().mandates]
    assert sorted(set(ids)) == sorted(ids)
```

- [ ] **Step 3: Run — expect FAIL**

Run: `python -m pytest tests/test_self_host.py -v`
Expected: `test_declaration_names_the_reviews_tree` fails with `AcfInputError` (no `adr.yml`); `test_every_manual_row_names_an_existing_test_module` fails on its first assert (no manual rows yet); the other two pass.

- [ ] **Step 4: Create `config/architecture/adr.yml`** with the two lines of Global Constraints, LF, no trailing whitespace.

- [ ] **Step 5: Run — expect 3 passed, 1 failed** (the manual-row test, until Task 4).

- [ ] **Step 6: Falsify, then restore.** Rename `adr.yml` into the scratchpad → the declaration test fails; restore. Byte-edit one anchor in `ARCHITECTURE.md` (`## No shims` → `## No shim`) → the anchor test fails; restore. Duplicate one `- id:` row by a byte-level copy → the uniqueness test fails; restore. `git status --short` shows only the intended files afterwards.

- [ ] **Step 7: Review Focus 5 — run without the marker**

```bash
mv .acf <scratch>/acf.bak && python -m pytest tests/test_self_host.py -q ; mv <scratch>/acf.bak .acf
```

Expected: the same 3 passed / 1 failed as step 5. The tests never read the marker.

- [ ] **Step 8: Commit**

```bash
git add config/architecture/adr.yml tests/test_self_host.py pyproject.toml
git commit -m "feat(host): adr.yml declaration and the self-host test (declaration, anchors, manual rows, unique ids)"
```

---

### Task 4: The doctrine and its registry rows

**Files:**
- Modify: `config/architecture/ARCHITECTURE.md`, `config/architecture/mandates.yml`

**Interfaces:**
- Consumes: the stock pair from Task 2; the four tests from Task 3.
- Produces: the nine plugin sections, two lifted anchors and `## High-frequency misses` in the doctrine; five manual rows.

- [ ] **Step 1: Replace the doctrine's title and intro.** Title `# Architecture doctrine — arch-compliance plugin`. Intro, three sentences: this file and `config/architecture/mandates.yml` govern the Python package under `plugins/arch-compliance/python/acf/`, the hooks, the skill prose and the TypeScript bridge; where a Superpowers default conflicts with a rule here, the rule here wins (`docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-52`, principle 5); the five governing principles there are not restated here. Keep every stock section and its body; append the lifted quotes of step 2 under the stock anchors they belong to.

- [ ] **Step 2: Quote the lifted rules under their stock anchors** (spec §5.2, attribution in parentheses after each quote):
  - under `## Fail loud`: the three GEMINI §3 sentences the spec quotes (`hm:GEMINI.md:102-106`);
  - under `## No shims`: the GEMINI §4 sentence (`hm:GEMINI.md:110-112`);
  - under `## POSIX paths`: the two GEMINI §10 sentences (`hm:GEMINI.md:190-194`).

- [ ] **Step 3: Add the plugin's own sections, in this order, each two to three sentences stating the rule and naming its source as spec §5.2's table gives it.** Headings are exact (they are anchors):
  `## One base exception` · `## One owner for host paths` · `## Declared, never defaulted` · `## Prose names no host` · `## Frozen ledger format` · `## Live consumers` · `## No completeness claims` · `## Declared text decoding` · `## Release discipline` · `## Single point of definition` · `## Scoped refactor`.
  The last two carry the GEMINI §7 quotes (`hm:GEMINI.md:134` and `:129`). `## Single point of definition` names the two git runners (`plugins/arch-compliance/python/acf/diff.py:17`, `plugins/arch-compliance/python/acf/adr/citations.py:54`) as the current breach. The four sections without a row (`Live consumers`, `No completeness claims`, `Declared text decoding`, `Release discipline`) and the two lifted anchors end with the sentence: `No row: no test enforces this yet.`

- [ ] **Step 4: Append `## High-frequency misses`** listing the five items of spec §5.2's last paragraph, one line each, as the compliance reviewer's first checks.

- [ ] **Step 5: Add the five manual rows at the end of `mandates.yml`**, this shape, ids and anchors exact:

```yaml
- id: plugin.one-base-exception
  title: Every ACF exception subclasses AcfError alone
  severity: BLOCK
  detection: manual
  detector: plugins/arch-compliance/tests/test_adr_exceptions.py
  languages: python
  call_sites: [review]
  exemption_tokens: [plugin.one-base-exception-ok]
  status: enforced
  arch_anchor: "## One base exception"
```

The other four, same shape: `plugin.one-owner-host-paths` (WARN, `plugins/arch-compliance/tests/test_repo_paths.py`, `"## One owner for host paths"`); `plugin.declared-never-defaulted` (BLOCK, `plugins/arch-compliance/tests/test_adr_host.py`, `"## Declared, never defaulted"`); `plugin.prose-names-no-host` (WARN, `plugins/arch-compliance/tests/test_adr_code_portability.py`, `"## Prose names no host"`); `plugin.frozen-ledger-format` (BLOCK, `plugins/arch-compliance/tests/test_adr_ledger.py`, `"## Frozen ledger format"`).

- [ ] **Step 6: Run — expect PASS**

Run: `python -m pytest tests/test_self_host.py -v`
Expected: 4 passed.

- [ ] **Step 7: Review Focus 2 — the gate with manual rows present**

```bash
PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --mode worktree
PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main
```

Expected: both exit 0 with no `acf:` line on stderr.

- [ ] **Step 8: Commit**

```bash
git add config/architecture/ARCHITECTURE.md config/architecture/mandates.yml
git commit -m "feat(host): the plugin's doctrine — nine sections, lifted rules quoted, five manual registry rows"
```

---

### Task 5: Session process, README, and the installed-skills check

**Files:**
- Create: `CLAUDE.md`, `scripts/check_installed_skills.py`, `tests/test_check_installed_skills.py`
- Modify: `README.md:81-85` (append one paragraph after the host-enablement paragraph)

**Interfaces:**
- Produces: `check_installed_skills.py` with `main(argv: list[str] | None = None) -> int`: `argv = [INSTALL_PATH]`; compares every file under `<clone>/plugins/arch-compliance/skills/{adversarial-design-review,responding-to-adversarial-review}` byte-for-byte with the same relative path under `<INSTALL_PATH>/skills/…`; prints `installed gate skills identical to the clone` and returns 0, or prints each differing or missing relative path and returns 1. `<clone>` is the script's own repository root (`Path(__file__).resolve().parents[1]`). Task 8 runs it.

- [ ] **Step 1: Write the failing tests**

```python
def test_identical_trees_return_zero(tmp_path, capsys):
    # two copies of a two-file skill tree under tmp_path/clone and tmp_path/inst
    assert main([str(inst)], clone=clone) == 0
    assert "identical" in capsys.readouterr().out

def test_a_changed_byte_is_reported(tmp_path, capsys):
    # same, then one byte appended to inst/.../SKILL.md
    assert main([str(inst)], clone=clone) == 1
    assert "adversarial-design-review/SKILL.md" in capsys.readouterr().out
```

`main` takes a keyword-only `clone: Path | None = None` defaulting to the repository root, so the tests can point it at `tmp_path`.

- [ ] **Step 2: Run — expect FAIL** (`ModuleNotFoundError`). Run: `python -m pytest tests/test_check_installed_skills.py -v`. The test imports the script by path with `importlib.util.spec_from_file_location`, since `scripts/` is not a package.

- [ ] **Step 3: Implement `scripts/check_installed_skills.py`** per Interfaces; `filecmp.cmp(a, b, shallow=False)`; the algorithm is the 1d plan's Task 8 step 1 block (`hm-1d:docs/plans/PLAN_ADR_GATE_HM_CUTOVER.md`), with `clone` as a parameter.

- [ ] **Step 4: Run — expect PASS** (2 passed).

- [ ] **Step 5: Write `CLAUDE.md`** with exactly these parts (spec §5.3), short: title; "Doctrine: `config/architecture/ARCHITECTURE.md` and `config/architecture/mandates.yml`; read both before substantive work"; the four Superpowers overrides as bullets (spec at `docs/design/<TOPIC>.md`; plan at `docs/plans/PLAN_<TOPIC>.md`; brainstorming ends at `/arch-compliance:adversarial-design-review <spec>` then `writing-plans`, `BLOCKED` returns through `arch-compliance:responding-to-adversarial-review`; before any gate run, `python scripts/check_installed_skills.py <INSTALL_PATH>` must print `identical`); the citation convention (unprefixed = this repository; another repository by prefix for the reader, its rule quoted; the controller maps a prefix to the sibling checkout before classification, as spec §0); the Windows note (`PYTHONUTF8=1` for `acf.cli_check_diff`, run from the repository root). Nothing else.

- [ ] **Step 6: Review Focus 4 — the gate from a subdirectory**

```bash
cd plugins/arch-compliance && PYTHONUTF8=1 python -m acf.cli_check_diff --mode worktree; echo "exit $?"; cd ../..
```

Expected: one `acf: … mandates file …` line on stderr and `exit 1`.

- [ ] **Step 7: README paragraph**, appended after `README.md:85` ("…`arch_anchor` values name."): "**This repository is a host of its own gate.** It declares `config/architecture/adr.yml`, keeps its doctrine and registry under `config/architecture/`, and records its reviews under `docs/reviews/` (spec `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md`). Specs about the plugin are written, reviewed and recorded here."

- [ ] **Step 8: Commit**

```bash
git add CLAUDE.md README.md scripts/check_installed_skills.py tests/test_check_installed_skills.py
git commit -m "docs(host): CLAUDE.md session process, README host note, installed-skills byte check"
```

---

### Task 6: CI runs the diff gate on this repository

**Files:**
- Modify: `.github/workflows/ci.yml:13` (checkout step) and after `:34-35` (the pytest step)

- [ ] **Step 1: Edit the workflow.** Give `actions/checkout@v4` `with: fetch-depth: 0` (the merge-base needs history). After the `Run pytest` step add:

```yaml
      - name: Architecture compliance (diff vs base)
        run: python -m acf.cli_check_diff --repo . --base "origin/${{ github.base_ref || 'main' }}"
```

- [ ] **Step 2: Verify locally what CI will run**

```bash
PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main; echo "exit $?"
```

Expected: `exit 0`.

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: run acf-check-diff against the base branch on every push and PR"
```

---

### Task 7: The host-contract spec moves here

**Files:**
- Create: `docs/design/ADR_GATE_HOST_CONTRACT.md`

- [ ] **Step 1: Copy from HM `main`, byte-exact**

```bash
HM=C:/Users/iball/Arduino/Projects/HistoricMansions
git -C $HM log -1 --format=%h -- docs/design/ADR_GATE_HOST_CONTRACT.md    # expect 86f93f95; record as HM_SPEC_SHA
git -C $HM show main:docs/design/ADR_GATE_HOST_CONTRACT.md > docs/design/ADR_GATE_HOST_CONTRACT.md
wc -l docs/design/ADR_GATE_HOST_CONTRACT.md                                 # 512
```

(`git show main:path` on Git Bash: set `MSYS_NO_PATHCONV=1` if the colon is rewritten.)

- [ ] **Step 2: Insert the provenance block** with the Edit tool, after the title line:

```markdown
> **Provenance.** Moved from `HistoricMansionsV3/docs/design/ADR_GATE_HOST_CONTRACT.md`
> at HM commit `<HM_SPEC_SHA>` on <date>, per its decision 6, by
> `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md`. Its citation convention is
> unchanged and inverted relative to this repository's: **unprefixed paths are
> HistoricMansions at the commit its §0 names; `acf:` paths are this repository.** Its
> ledger records stay in HM's ledger under the HM path.
```

- [ ] **Step 3: Commit**

```bash
git add docs/design/ADR_GATE_HOST_CONTRACT.md
git commit -m "docs: ADR_GATE_HOST_CONTRACT.md moves here from HistoricMansions (its decision 6), provenance noted"
```

---

### Task 8: Cache check and the acceptance run (fresh session, user-confirmed)

**Files:**
- Create (by the run): `docs/reviews/adr_runs/PLUGIN_SELF_HOSTING_AND_DOCTRINE_v1_<date>.md`, `docs/reviews/adversarial_design_ledger.jsonl`

- [ ] **Step 1: Byte-check the installed skills**

```bash
python scripts/check_installed_skills.py "<INSTALL_PATH>"
```

Expected: `installed gate skills identical to the clone`. Otherwise reinstall (1d Task 2 step 2 after `claude plugin uninstall arch-compliance@arch-compliance-for-superpowers`) and repeat.

- [ ] **Step 2: Acceptance run.** The user starts a fresh Claude Code session with cwd = the worktree root and runs `/arch-compliance:adversarial-design-review docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md`. The controller applies spec §0 before classifying citations: `hm:` → `C:/Users/iball/Arduino/Projects/HistoricMansions/`, `hm-1d:` → `…/HistoricMansions/.claude/worktrees/adr-gate-hm-cutover/`, mapped paths handed to reviewers and counted as cited files. **The verdict binds** (spec §6): `CLEARED` / `CLEARED_WITH_ABSORPTIONS` proceeds; `BLOCKED` returns to the spec via `arch-compliance:responding-to-adversarial-review`, and a revision of any §5.2 rule re-runs in full, blind, after Task 4 is updated to match.

- [ ] **Step 3: Read the records back and commit them**

```bash
ls docs/reviews/adr_runs/
tail -1 docs/reviews/adversarial_design_ledger.jsonl | python -c "import json,sys; r=json.load(sys.stdin); print(r['spec_path'], r['outcome'])"
python -m pytest tests/test_self_host.py -q     # still 4 passed
git add docs/reviews && git commit -m "docs(adr): PLUGIN_SELF_HOSTING_AND_DOCTRINE v1 gate run — <OUTCOME>"
```

Expected: `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md CLEARED` (or `CLEARED_WITH_ABSORPTIONS`).

- [ ] **Step 4: Repeat rule.** If any non-record commit lands after step 2, bump the spec's Status version, commit, and repeat from step 1.

---

### Task 9: Gates, code review, PR

- [ ] **Step 1: Full verification**

```bash
python -m pytest -q                                                     # BASELINE_TESTS + 6
npm test --prefix plugins/arch-compliance/detectors/typescript          # self-test OK
PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main   # exit 0
git status --short                                                      # clean
```

- [ ] **Step 2: DoD 4** — `git diff --stat origin/main` lists only: `config/architecture/{adr.yml,mandates.yml,ARCHITECTURE.md}`, `tests/test_self_host.py`, `tests/test_check_installed_skills.py`, `scripts/check_installed_skills.py`, `pyproject.toml`, `CLAUDE.md`, `README.md`, `.github/workflows/ci.yml`, `docs/design/ADR_GATE_HOST_CONTRACT.md`, `docs/reviews/…` (two files).

- [ ] **Step 3: Code review** — `requesting-code-review` over `BASE_SHA..HEAD`, naming: the five manual rows and their severities, the unenforced stock rows, `pyproject.toml` testpaths, the CI base expression. Fix findings in new commits; a change to any §5.2 rule returns to Task 8 step 4.

- [ ] **Step 4: Push and PR**

```bash
git push -u origin feat/self-host
gh pr create --base main --title "feat(host): this repository hosts its own adversarial-design-review gate" --body "<spec path; acceptance run detail filename and outcome; the five manual rows; BASE_SHA; HM_SPEC_SHA>"
```

The body ends with `🤖 Generated with [Claude Code](https://claude.com/claude-code)`. CI must show the new step green (DoD 7). **The user squash-merges.**

---

### Task 10: HM roadmap and stub (docs-only, after 1d's roadmap edits are on HM `main`)

**Files (HM):**
- Modify: `docs/design/ADR_GATE_HOST_CONTRACT.md` (replace body with a stub), `docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md`

- [ ] **Step 1: Precondition** — in HM: `git log origin/main --oneline -5 -- docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md` shows 1d's Task 6 commit ("docs(roadmap): Workstream E 1d …"). Branch `docs/workstream-e-1e` from HM `origin/main` in a new HM worktree (HM's rules: `hm:CLAUDE.md`, GEMINI §2 worktree clause).

- [ ] **Step 2: The stub.** Replace the spec body with its title line, the `**Status:**` line changed to `**Status:** moved — now at \`arch-compliance-for-superpowers/docs/design/ADR_GATE_HOST_CONTRACT.md\` (plugin commit <PR merge SHA>); this path is kept so the ledger's rows for it keep resolving.`, and one sentence saying nothing else is kept here.

- [ ] **Step 3: Roadmap rows** (find each by grep, never by line number):
  - Workstream E table: add row **1e** after 1d: "Plugin self-hosting: the plugin repository declares itself a host of its gate, proposes its doctrine, moves `ADR_GATE_HOST_CONTRACT.md` to the plugin; first live gate run outside HM | spec `acf:docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` | ✅ Merged <date>, plugin PR #<N>". Rename the second-repository row to **1f**.
  - Exit criterion 5: the spec §10 wording ("the plugin repository is the first such host (1e), Cayenne the foreign-stack proof (1f)").
  - 1c row: append "spec moved to the plugin repository in 1e".
  - Priority board: one row each (class A, Parked) for spec §9 follow-ups 1 (git runner decoding + one-runner consolidation) and 2 (post-merge-housekeeping extraction; revises exit criterion 6 and GEMINI.md §1 item 8); follow-up 3 is already filed by 1d — confirm with `grep -n 'quiet-disabled'`.

- [ ] **Step 4: Commit and PR in HM**

```bash
git add docs/design/ADR_GATE_HOST_CONTRACT.md docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md
git commit -m "docs(roadmap): Workstream E 1e — plugin self-hosting merged; host-contract spec moved; follow-ups filed"
gh pr create --base main
```

DoD 8: merged, or open and linked from this plan's ledger.
