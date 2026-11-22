# Check-Diff Host Wiring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a composite GitHub Action that installs and runs `acf-check-diff` for a host, test it in this repository's CI, and rewrite `/acf-setup` step 8 to print that action plus a guarded pre-push command (release 0.3.4).

**Architecture:** `.github/actions/check-diff/action.yml` installs the plugin editable from its own files into a venv under `$RUNNER_TEMP`, runs an optional `host-setup` command, and then runs `acf-check-diff --call-site ci`. A fixture builder under `tests/` makes throwaway host repos. A new `action` CI job runs the action against a planted fixture, a clean fixture and this repository. The docs, the doctrine and the version follow.

**Tech Stack:** GitHub Actions (composite), bash/POSIX sh, Python 3.11+ (pytest), Node 22 for the TS pack.

**Spec:** `docs/design/CHECK_DIFF_HOST_WIRING.md` (v4, cleared by verification pass). Its §4 and §7 are this plan's scope. Its §8, the first adopter's pull request, is a separate change in another repository after the `v0.3.4` tag.

## Global Constraints

- Action inputs and defaults, exactly: `base` "" · `repo` "." · `trusted-checkout` "true" · `python-version` "3.12" · `node-version` "22" · `host-setup` "".
- Empty `base` means `origin/<github.base_ref>`, or `origin/<github.event.repository.default_branch>` when `github.base_ref` is empty.
- `trusted-checkout` accepts only `true` or `false`; any other value stops the action with a message naming the input.
- The gate's stdout is written through `tee` under `set -o pipefail` to `$RUNNER_TEMP/acf-check-diff.txt`, overwriting it.
- Linux and macOS runners only; step 2 stops on `runner.os == 'Windows'`.
- The pre-push command never carries `--trusted-checkout`. Only the action does.
- `ACF_PREPUSH_OPTIONAL` has no default. Only the exact value `1` skips; unset or any other value refuses.
- Skill prose names no host repository, path or section (`## Prose names no host`).
- The version is `0.3.4` in both `plugins/arch-compliance/.claude-plugin/plugin.json` and `pyproject.toml`.
- Host paths in `tests/` come from `acf.repo` (`MANDATES_REL`, `ARCH_REL`).
- Subprocess text calls in new Python declare `encoding="utf-8"`. This is outside the doctrine's runtime scope, but cheap.

## Review Focus

1. **The action is run from another repository and the plugin files are not three levels up.** Expected: step 1 stops and names both paths. Task 2's structural test pins that step 1 exists and checks both paths. The run itself is proven only at the first adopter.
2. **A host sets `trusted-checkout: false` while it has host rows.** Expected: the gate refuses for lack of an approval, loudly, with exit 1. Task 2's structural test pins that the flag is passed only for `true`, and the input validation step refuses other values.
3. **A shallow checkout (no `fetch-depth: 0`).** Expected: step 7 stops with a message naming `fetch-depth: 0`. Task 2's structural test pins the predicate and the message text.
4. **A push to the default branch, where `base_ref` is empty.** Expected: the base becomes `origin/<default_branch>`, the diff is empty, and the run passes. This is exercised by the `action` job's third run on the post-merge push. Task 2's structural test pins the fallback expression.
5. **A pre-push run with the tool absent, under each `ACF_PREPUSH_OPTIONAL` value.** Expected: unset refuses (exit 1), `1` skips (exit 0), and any other value refuses. Task 3's snippet test executes the printed snippet under each value.

---

### Task 1: Fixture builder, proven against the gate locally

**Files:**
- Create: `tests/action_fixture_host.py`
- Test: `tests/test_action_fixture_host.py`

**Interfaces:**
- Produces: `python tests/action_fixture_host.py <dest> --plant {empty-catch,clean}`, run with `PYTHONPATH=plugins/arch-compliance/python`. It leaves `<dest>` as a git repo with branch `main` (base) and branch `feature` (checked out, one commit on top). It also exposes `build(dest: Path, plant: Literal["empty-catch", "clean"]) -> None` for the test.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_action_fixture_host.py
import subprocess, sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from action_fixture_host import build  # noqa: E402

def _gate(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "acf.cli_check_diff", "--repo", str(repo),
         "--base", "main", "--call-site", "ci"],
        capture_output=True, text=True, encoding="utf-8",
    )

def test_planted_fixture_blocks(tmp_path):
    build(tmp_path / "h", "empty-catch")
    r = _gate(tmp_path / "h")
    assert r.returncode == 1
    assert "BLOCK fail-loud.empty-catch src/app.ts:" in r.stdout

def test_clean_fixture_passes(tmp_path):
    build(tmp_path / "h", "clean")
    r = _gate(tmp_path / "h")
    assert r.returncode == 0, r.stderr
    assert "No findings." in r.stdout

def test_fixture_branches(tmp_path):
    build(tmp_path / "h", "clean")
    head = subprocess.run(["git", "-C", str(tmp_path / "h"), "branch", "--show-current"],
                          capture_output=True, text=True, encoding="utf-8").stdout.strip()
    assert head == "feature"
    assert subprocess.run(["git", "-C", str(tmp_path / "h"), "rev-parse", "--verify", "main"],
                          capture_output=True).returncode == 0
```

- [ ] **Step 2: Run them to verify they fail**

Run: `PYTHONUTF8=1 python -m pytest tests/test_action_fixture_host.py -v`
Expected: collection error, `ModuleNotFoundError: No module named 'action_fixture_host'`.

- [ ] **Step 3: Implement `build(dest, plant)` and a `main(argv)` CLI in `tests/action_fixture_host.py`**

- Run git with `git -c init.defaultBranch=main init`, and pass `-c user.name=ci -c user.email=ci@example.invalid -c commit.gpgsign=false` on every commit, as `plugins/arch-compliance/tests/test_adr_citation_history.py:20` does.
- Import `MANDATES_REL` and `ARCH_REL` from `acf.repo`. Write `MANDATES_REL` with the spec §4.2 row verbatim: id, title "Empty catch blocks must not swallow errors", BLOCK, ast, empty_catch, typescript, `call_sites: [ci]`, `exemption_tokens: []`, enforced, `arch_anchor: "## Fail loud"`. Write `ARCH_REL` holding the line `## Fail loud`. Write `src/app.ts` with one function.
- Commit on `main`, then `git checkout -b feature`. For `empty-catch`, append a function containing `try { … } catch {}`. For `clean`, append a function with no catch. Commit.
- Import nothing beyond the stdlib and `acf.repo`.

- [ ] **Step 4: Run the tests to verify they pass**

Run: `PYTHONUTF8=1 python -m pytest tests/test_action_fixture_host.py -v`
Expected: 3 passed. This needs `npm ci` already run in `plugins/arch-compliance/detectors/typescript`.

- [ ] **Step 5: Confirm pytest does not collect the builder itself**

Run: `python -m pytest --collect-only -q tests | grep -c action_fixture_host.py::`
Expected: `0`.

- [ ] **Step 6: Commit**

```bash
git add tests/action_fixture_host.py tests/test_action_fixture_host.py
git commit -m "test: fixture host builder for the check-diff action"
```

---

### Task 2: The composite action and its CI job

**Files:**
- Create: `.github/actions/check-diff/action.yml`
- Modify: `.github/workflows/ci.yml` (remove the gate step at `:39-40`; add job `action`)
- Modify: `.github/dependabot.yml` (add a `github-actions` entry for `/.github/actions/check-diff`)
- Test: `tests/test_check_diff_action.py`

**Interfaces:**
- Consumes: the Task 1 CLI, `PYTHONPATH=plugins/arch-compliance/python python tests/action_fixture_host.py <dest> --plant …`.
- Produces: the action `uses: ./.github/actions/check-diff` (and `IanDBallard/arch-compliance-for-superpowers/.github/actions/check-diff@v0.3.4` once tagged), with the inputs in Global Constraints.

- [ ] **Step 1: Write the failing structural test**

```python
# tests/test_check_diff_action.py
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]
ACTION = ROOT / ".github/actions/check-diff/action.yml"

def _a():
    return yaml.safe_load(ACTION.read_text(encoding="utf-8"))

def test_composite_with_pinned_inputs():
    a = _a()
    assert a["runs"]["using"] == "composite"
    assert {k: v.get("default") for k, v in a["inputs"].items()} == {
        "base": "", "repo": ".", "trusted-checkout": "true",
        "python-version": "3.12", "node-version": "22", "host-setup": ""}

def test_step_order_and_guards():
    text = ACTION.read_text(encoding="utf-8")
    first = _a()["runs"]["steps"][0]["run"]
    assert "pyproject.toml" in first
    assert "plugins/arch-compliance/detectors/typescript/package.json" in first
    assert "runner.os == 'Windows'" in text
    assert "--is-shallow-repository" in text and "fetch-depth: 0" in text
    assert "github.event.repository.default_branch" in text
    assert "set -o pipefail" in text and "acf-check-diff.txt" in text
    assert "--call-site ci" in text

def test_trusted_checkout_only_when_true():
    text = ACTION.read_text(encoding="utf-8")
    assert "trusted-checkout" in text and "must be true or false" in text
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest tests/test_check_diff_action.py -v`
Expected: FAIL with `FileNotFoundError` for `action.yml`.

- [ ] **Step 3: Write `.github/actions/check-diff/action.yml`**

Write the composite action with steps 1–8 in spec §4.1 order, each `run:` step using `shell: bash`.
- **Step 1:** a `test -f` on both paths under `"$GITHUB_ACTION_PATH/../../.."`. The message names both paths and says the action expects a full copy of the plugin repository.
- **Step 2:** `if: runner.os == 'Windows'`, with an error and `exit 1`.
- **`trusted-checkout`:** validated in an early step, with the message `trusted-checkout must be true or false, got '<value>'`.
- **Steps 3–5:** `actions/setup-python@v7` / `actions/setup-node@v7`, pinned like `.github/workflows/ci.yml:13-23`. Then `python -m venv "$RUNNER_TEMP/acf-venv"`, then `pip install -e "$GITHUB_ACTION_PATH/../../.."`, then `npm ci` in the pack.
- **Step 6:** runs only `if: inputs.host-setup != ''`, with `PATH="$RUNNER_TEMP/acf-venv/bin:$PATH"` and `working-directory: ${{ inputs.repo }}`.
- **Step 7:** shallow-clone stop.
- **Step 8:** computes the base with the Global Constraints fallback and runs the gate through `tee` under `pipefail`.
- **`repo`:** an absolute path or a workspace-relative one; resolve it relative to `$GITHUB_WORKSPACE` only when it is not absolute.

- [ ] **Step 4: Run the structural test to verify it passes**

Run: `python -m pytest tests/test_check_diff_action.py -v`
Expected: 3 passed.

- [ ] **Step 5: Edit `.github/workflows/ci.yml`**

- Delete the `Architecture compliance (diff vs base)` step (`:39-40`).
- Add job `action`: `runs-on: ubuntu-latest`, checkout `@v7` with `fetch-depth: 0`. Then a step that runs the Task 1 CLI twice into `$RUNNER_TEMP/planted` and `$RUNNER_TEMP/clean`.
- Add three action runs:
  1. id `planted`: `repo: ${{ runner.temp }}/planted`, `base: main`, `continue-on-error: true`. Next step: fail unless `steps.planted.outcome == 'failure'` and `grep -q 'BLOCK fail-loud.empty-catch' "$RUNNER_TEMP/acf-check-diff.txt"`.
  2. id `clean`: `repo: ${{ runner.temp }}/clean`, `base: main`, `host-setup: touch "$RUNNER_TEMP/host-setup-ran"`. Next step: fail unless the outcome is `success` and `test -f "$RUNNER_TEMP/host-setup-ran"`.
  3. id `self`: `repo: .`, `base` empty.

- [ ] **Step 6: Add the Dependabot entry**

In `.github/dependabot.yml`, add a second `github-actions` block with `directory: /.github/actions/check-diff` and a weekly schedule, mirroring `:19-22`.

- [ ] **Step 7: Check the YAML parses and the suite is green**

Run: `python -c "import yaml,sys;[yaml.safe_load(open(p,encoding='utf-8')) for p in sys.argv[1:]]" .github/workflows/ci.yml .github/dependabot.yml .github/actions/check-diff/action.yml && PYTHONUTF8=1 python -m pytest -q`
Expected: no exception; all tests pass.

- [ ] **Step 8: Commit**

```bash
git add .github/actions/check-diff/action.yml .github/workflows/ci.yml .github/dependabot.yml tests/test_check_diff_action.py
git commit -m "feat(ci): check-diff composite action, tested on fixture hosts and this repository"
```

---

### Task 3: `/acf-setup` step 8 and the user docs

**Files:**
- Modify: `plugins/arch-compliance/skills/acf-setup/SKILL.md`: `:3`, `:25`, `:210-258`, `:285`
- Modify: `README.md`: `:53-58`, `:62`, and a new upgrade note before `:112`
- Modify: `docs/guides/SUPERPOWERS_COMPLEMENT.md`: `:40`, `:78-83`, `:87`
- Test: `tests/test_acf_setup_wiring.py`

**Interfaces:**
- Consumes: the action path and inputs from Task 2.
- Produces: in SKILL.md, a fenced `yaml` workflow block and the fenced `sh` pre-push snippet from spec §4.3, exactly. Task 3's test extracts the `sh` block that contains `ACF_PREPUSH_OPTIONAL`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_acf_setup_wiring.py
import re, subprocess, os, shutil
from pathlib import Path
SKILL = Path(__file__).resolve().parents[1] / "plugins/arch-compliance/skills/acf-setup/SKILL.md"

def _snippet() -> str:
    blocks = re.findall(r"```sh\n(.*?)```", SKILL.read_text(encoding="utf-8"), re.S)
    [s] = [b for b in blocks if "ACF_PREPUSH_OPTIONAL" in b]
    return s

def _run(env_value):
    env = {k: v for k, v in os.environ.items() if k != "ACF_PREPUSH_OPTIONAL"}
    env["PATH"] = "/nonexistent"          # acf-check-diff absent
    if env_value is not None:
        env["ACF_PREPUSH_OPTIONAL"] = env_value
    return subprocess.run([SH, "-c", _snippet()], env=env, capture_output=True,
                          text=True, encoding="utf-8")

SH = shutil.which("sh")   # resolved before PATH is emptied; dash on CI, Git Bash's sh on Windows

def test_absent_unset_refuses():
    r = _run(None); assert r.returncode == 1 and "ACF_PREPUSH_OPTIONAL=1" in r.stderr

def test_absent_optional_skips():
    r = _run("1"); assert r.returncode == 0 and "skipping" in r.stderr

def test_absent_other_value_refuses():
    assert _run("yes").returncode == 1

def test_snippet_has_no_trusted_checkout():
    s = _snippet()
    assert "--trusted-checkout" not in s and "--call-site precommit" in s and "|| exit 1" in s

def test_workflow_uses_action_and_no_sketch():
    text = SKILL.read_text(encoding="utf-8")
    assert ".github/actions/check-diff@v" in text and "fetch-depth: 0" in text
    assert "stages: [pre-commit]" not in text
    assert "pre-commit/CI snippets" not in text
```

`SH` must be a POSIX sh: dash on CI, Git Bash's `sh` on Windows (run with `PYTHONUTF8=1`).

- [ ] **Step 2: Run them to verify they fail**

Run: `PYTHONUTF8=1 python -m pytest tests/test_acf_setup_wiring.py -v`
Expected: FAIL, because `_snippet()` finds no block (`ValueError: not enough values to unpack`).

- [ ] **Step 3: Rewrite SKILL.md as spec §4.3 lists**

- Change the frontmatter, checklist item 8, the step 8 heading and the step 10 line to say "pre-push".
- **CI subsection:** the workflow block verbatim, plus these points:
  - pull requests only;
  - add `push` for active ratchet or host-guard rows at `ci`, decided with `load_gate_registry`, `active(sites, detector="fail_loud_ratchet")` and `host_rows(sites, detection="guard")`, the mandates path from `acf.repo.MANDATES_REL`;
  - no `paths-ignore`;
  - the single-workflow alternative;
  - `host-setup`;
  - the action installs its own plugin.
- **Pre-push subsection:** the snippet verbatim, plus:
  - place it at the hook's top level;
  - where it can go;
  - after any existing skip;
  - the opt-out belongs in environment settings, and is only as strong as what stops a red job from merging;
  - the site checks run `acf-check-diff --mode worktree --call-site {precommit,ci}` and read "selects no active";
  - no `--trusted-checkout`;
  - the three known gaps;
  - `PYTHONUTF8=1` on Windows.
- **`:249`:** replace it with the sentence spec §4.3 gives.
- **`:253`, `:254`, `:258`:** change them as spec §4.3 lists.
- **Leave alone:** step 9 and the friend-bar tip.

- [ ] **Step 4: Edit the README and the guide**

- **README `:53-58` and COMPLEMENT `:78-83`:** drop `--trusted-checkout` from the local CI-style line, and add one line saying CI here and in hosts runs the check-diff action.
- **README `:62` and COMPLEMENT `:87`:** append "(the check-diff action passes it by default)".
- **COMPLEMENT `:40`:** "pre-commit/CI" becomes "pre-push/CI".
- **README:** add `### Upgrading a host to the check-diff action (v0.3.4)` before the v0.3.3 note at `:112`. It says:
  - replace a pasted CI sketch with the workflow pinned at `@v0.3.4`;
  - move a pre-commit entry to pre-push with the guarded snippet;
  - set `ACF_PREPUSH_OPTIONAL=1` only in environments where CI is the only gate;
  - pass `host-setup` for host-detector dependencies.

- [ ] **Step 5: Run the tests to verify they pass**

Run: `PYTHONUTF8=1 python -m pytest tests/test_acf_setup_wiring.py -v`
Expected: 5 passed.

- [ ] **Step 6: Check the prose names no host**

Run: `grep -n -i -E "cayenne|historicmansions|recipeparser" plugins/arch-compliance/skills/acf-setup/SKILL.md README.md docs/guides/SUPERPOWERS_COMPLEMENT.md; echo "exit $?"`
Expected: `exit 1`; every existing match must predate this change, so compare with `git diff`.

- [ ] **Step 7: Commit**

```bash
git add plugins/arch-compliance/skills/acf-setup/SKILL.md README.md docs/guides/SUPERPOWERS_COMPLEMENT.md tests/test_acf_setup_wiring.py
git commit -m "docs(acf-setup): print the check-diff action and a guarded pre-push step"
```

---

### Task 4: Doctrine, version 0.3.4, final checks

**Files:**
- Modify: `config/architecture/ARCHITECTURE.md`: opening scope `:3-9`, call-site rule `:154-158`, `## Declared, never defaulted` `:212-221`, `## Release discipline` `:274-284`, `## Single point of definition` `:286-303`, `## Post-merge` `:330`
- Modify: `plugins/arch-compliance/.claude-plugin/plugin.json:3` and `pyproject.toml:3`, to `0.3.4`

**Interfaces:**
- Consumes: the file names from Tasks 1–3, for the doctrine text.

- [ ] **Step 1: Edit the doctrine as spec §4.4 lists**

- **Opening scope:** add `.github/actions/`.
- **Call-site rule:** add the `precommit` sentence verbatim.
- **Declared, never defaulted:** record the action-input defaults and `ACF_PREPUSH_OPTIONAL` has no default.
- **Release discipline:** add the tagging sentence verbatim, including "once `main`'s CI run for that commit has passed".
- **Single point of definition:** record the three install copies and why they stay apart: `acf-setup/SKILL.md` step 4, the `ci.yml` `test` job, and the action.
- **Post-merge `:330`:** it becomes "(`test` and `action` jobs on `main`)".

- [ ] **Step 2: Bump the version**

Set `"version": "0.3.4"` in `plugin.json` and `version = "0.3.4"` in `pyproject.toml`.

- [ ] **Step 3: Run the full suite and the diff gate**

Run: `PYTHONUTF8=1 python -m pytest -q && PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main --call-site ci`
Expected: all tests pass; the gate prints `No findings.` with exit 0.

- [ ] **Step 4: Check that the installed gate skills are untouched**

Run: `python scripts/check_installed_skills.py "C:\Users\iball\.claude\plugins\cache\arch-compliance-for-superpowers\arch-compliance\0.3.3"`
Expected: `installed gate skills identical to the clone`. Only `acf-setup` changed, and it is outside the byte check.

- [ ] **Step 5: Commit**

```bash
git add config/architecture/ARCHITECTURE.md plugins/arch-compliance/.claude-plugin/plugin.json pyproject.toml
git commit -m "chore(release): 0.3.4 — check-diff action doctrine and version"
```

- [ ] **Step 6: Stop before push.**

Push, the pull request and the merge each need the user's OK. After the merge, and once `main`'s CI for the merge commit is green, tag `v0.3.4` with the user's OK: `git tag v0.3.4 <merge-sha> && git push origin v0.3.4`. The pull request's `action` job is the definition of done in spec §7. The first adopter's change, spec §8, follows as its own pull request in that repository.
