# Architecture Review Port Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the plugin's four-auditor `/architecture-review` with a port of the origin repository's review. The port has twelve technology-independent rules, six plugin-shipped technology packs, a repository declaration (`review.yml`) and a hatch for repository prompts. It releases as `0.3.0`, and then the origin repository cuts over to it.

**Architecture:** New package `acf.review` holds:

- `contract`, `host`, `rules`, `packs`, `prepass`, `aggregator` and `rollup`;
- `doctrine_section` in `__init__`.

Shared helpers land first in existing modules and are adopted by their current callers:

- `acf.agent_payload.extract_json_block`;
- `acf.loader.write_text_record`;
- `acf.repo.path_matches` and `RepoTree.files`;
- `acf.registry.anchor_line`.

The skill prose drives the package step by step, as the ADR gate skill does. The origin stage is one PR in the HistoricMansions checkout, made after the plugin release is installed.

**Tech Stack:** Python ≥3.11, Pydantic v2, PyYAML, pytest. No new dependency.

**Spec:** `docs/design/ARCHITECTURE_REVIEW_PORT.md`. It is v4, cleared by a verification pass at `a6ff195`. Read it in full before any task: its section numbers are cited throughout, and its §5 tables are the origin stage's requirements, which this plan does not copy.

## Global Constraints

- **Path forms.** Unprefixed paths are this repository. `hm:` paths are `C:/Users/iball/Arduino/Projects/HistoricMansions`. `cy:` paths are the Cayenne checkout, which is read-only: nothing under `cy:` changes.
- **Version.** `0.2.5` becomes `0.3.0` in `pyproject.toml:3` and `plugins/arch-compliance/.claude-plugin/plugin.json:3`.
- **Text decoding.** Every file the package reads is read with `encoding="utf-8"` (`## Declared text decoding`).
- **Host paths.** Every host path string becomes a location through `acf.repo.RepoTree`: `contained` for write targets, `file`/`directory` for reads, `files` for globbing.
- **New exceptions.** Each new exception derives from `AcfError` alone, as `plugins/arch-compliance/tests/test_adr_exceptions.py:24-45` requires. The new ones are `AuditorContractViolationError` and `ReportWriteError`.
- **No host names.** No rule prompt, skill file, pack file or `acf.review` runtime message names a host repository, path, class or section (`## Prose names no host`).
- **Persisted paths.** Persisted and declared host paths use `PosixStr` (`plugins/arch-compliance/python/acf/adr/contract.py:129`).
- **Opt-in rules.** Every rule is opt-in through a mandate row: an active row with `auditor` set. `call_sites` never select review rows.
- **Running tests.** Run pytest from the worktree root as `PYTHONUTF8=1 python -m pytest -q`. `pyproject.toml` puts the worktree's `plugins/arch-compliance/python` first on the path. Never run `pip install -e` from a worktree.
- **Diff gate.** `PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main --call-site ci` passes before the release task.
- **Commit trailer.** Commits end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

### Stricter choices this plan makes within the spec

The first seven come from the v3 run's advisories.

1. **Exemption tokens.** `acf.review.aggregator.apply_exemptions` drops an `AuditorFinding` whose source line carries one of its row's `exemption_tokens`. It uses `acf.enforcement.token_exempted` (`enforcement.py:27-35`), the gates' own owner. Rule prompts carry no exemption prose. The report counts what was exempted.
2. **Runtime messages.** `acf.review` runtime messages are checked by the prose test (Task 11), which also gains the port's own vocabulary in `FORBIDDEN`.
3. **Origin import check.** In the origin stage, the import check runs over the whole tree outside `docs/`, not only `scripts tests` (Task 16).
4. **Blame.** Provenance uses `git blame --porcelain -L <n>,<n> -- <path>` and reads only the first token, the commit id. A decode failure is the debt `## Declared text decoding` already records, and Review Focus 2 pins it.
5. **Anchor prose.** `acf-setup` (`:115`, `:138-139`) and `acf-mandate` (`:67`, `:46`, `:109-110`) word the anchor rule as line equality everywhere, not as substring.
6. **`subsystem_of` callers.** `subsystem_of` takes the prefix list as a required keyword, and `plugins/arch-compliance/tests/test_baseline.py:52-60` passes `prefixes=[]`.
7. **Write-error advice.** `write_text_record` takes an optional `hint`, appended to its message, so `write_run_detail` keeps its operator advice (`run_detail.py:183-191`).
8. **Group identity.** An auditor payload echoes its group (the rule id or prompt path) as the ADR reviewer payload echoes its name. A mismatch is a contract violation.
9. **Finding paths.** A finding whose `path` is not a file in its row's surface is a contract violation.
10. **Error class.** A row whose `params` hold a wrong type or an undeclared key (on a non-`ast`/`guard` row) raises `AcfInputError` naming the mandate id. An unknown `auditor` raises `UnknownMandateError`, as §4.5 says.
11. **Test file name.** §7's `test_repo.py` is the existing `plugins/arch-compliance/tests/test_repo_tree.py`.

## Review Focus

These are the five inputs most likely to bite a user that the spec implies but no test exercises. Each is pinned in its owning task.

1. **A Windows-style glob.** A backslash in `--paths`, `surface`, `surface_exclude` or `exclude` (`admin\js\**`) is refused loudly, naming the pattern, rather than silently matching nothing (Task 2).
2. **A non-ASCII source line.** A finding on a line containing `é` gets a provenance classification, not a crash, under UTF-8 mode (Task 10).
3. **A file in a surface that is not UTF-8.** The pre-pass raises `AcfInputError` naming the POSIX path rather than skipping the file or crashing with a bare `UnicodeDecodeError` (Task 8).
4. **A bad finding path.** An auditor names a path outside its row's surface, or a line past the end of the file. The group is FAILED with the error, and the other groups still render (Task 9).
5. **A bad `--mandates` id.** An id that names no reviewed row (unknown, inactive, or no `auditor`) raises `UnknownMandateError` naming it, never yielding an empty run (Task 6).

---

## File Structure

| Path | Responsibility | Task |
|---|---|---|
| `plugins/arch-compliance/python/acf/agent_payload.py` (new) | one fenced-JSON extractor | 1 |
| `plugins/arch-compliance/python/acf/exceptions.py` | `AuditorContractViolationError`, `ReportWriteError` | 1 |
| `plugins/arch-compliance/python/acf/loader.py` | `write_text_record` | 1 |
| `plugins/arch-compliance/python/acf/adr/parser.py`, `adr/run_detail.py` | adopt the helpers | 1 |
| `plugins/arch-compliance/python/acf/repo.py` | `REVIEW_REL`, `path_matches`, `RepoTree.files` | 2 |
| `plugins/arch-compliance/python/acf/registry.py` | `anchor_line`; `missing_anchors` on it | 3 |
| `plugins/arch-compliance/python/acf/review/__init__.py` (new) | `doctrine_section` | 3 |
| `plugins/arch-compliance/python/acf/baseline.py` | protocol aggregation, prefix subsystems, `write_text_record` | 4 |
| `plugins/arch-compliance/python/acf/review/contract.py`, `review/host.py` (new) | finding/payload models; `review.yml` loader | 5 |
| `plugins/arch-compliance/python/acf/review/rules.py` (new) | settings models, `RULES`, `check_auditors`, `select_rows` | 6 |
| `plugins/arch-compliance/python/acf/review/packs.py`, `review/packs/*.yml` (new) | `TechPack`, loading, hint routing | 7 |
| `plugins/arch-compliance/python/acf/review/prepass.py` (new) | target tree, row surfaces, hint scan | 8 |
| `plugins/arch-compliance/python/acf/review/aggregator.py` (new) | payload parsing, exemptions, report render and write | 9 |
| `plugins/arch-compliance/python/acf/review/rollup.py` (new) | drift, staleness, provenance, roll-up | 10 |
| `plugins/arch-compliance/skills/architecture-review/rules/` (new) | twelve rule prompts, `_contract.md`; `auditors/` deleted | 11 |
| `plugins/arch-compliance/skills/architecture-review/SKILL.md` | controller procedure (§4.7) | 12 |
| doctrine, mandates, profiles, other skills, self-host tests | §6 rows | 13 |
| release files | `0.3.0`, README, installed-skill check | 14 |
| origin repository (`hm:`) | §5 | 16–17 |

---

### Task 1: Shared payload extractor, record writer, new exceptions

**Files:**
- Create: `plugins/arch-compliance/python/acf/agent_payload.py`, `plugins/arch-compliance/tests/test_agent_payload.py`
- Modify: `plugins/arch-compliance/python/acf/exceptions.py`, `plugins/arch-compliance/python/acf/loader.py`, `plugins/arch-compliance/python/acf/adr/parser.py:53-63`, `plugins/arch-compliance/python/acf/adr/run_detail.py:178-191`, `plugins/arch-compliance/tests/test_loader.py`, `plugins/arch-compliance/tests/test_adr_exceptions.py`

**Interfaces:**
- Produces:
  - `extract_json_block(payload: str, *, subject: str, error: type[AcfError]) -> Any`;
  - `write_text_record(path: Path, text: str, *, error: type[AcfError], hint: str = "") -> Path`;
  - `AuditorContractViolationError(AcfError)`;
  - `ReportWriteError(AcfError)`.

- [ ] **Step 1: Write the failing tests**

```python
# test_agent_payload.py
import pytest
from acf.agent_payload import extract_json_block
from acf.exceptions import AuditorContractViolationError, ReviewerContractViolationError

@pytest.mark.parametrize("err", [AuditorContractViolationError, ReviewerContractViolationError])
def test_zero_blocks_raise_passed_class(err):
    with pytest.raises(err, match="g1 payload contains no ```json fenced block"):
        extract_json_block("no fence", subject="g1", error=err)

def test_two_blocks_raise():
    two = "```json\n{}\n```\n```json\n{}\n```"
    with pytest.raises(AuditorContractViolationError, match=r"multiple \(2\)"):
        extract_json_block(two, subject="g1", error=AuditorContractViolationError)

def test_bad_json_raises():
    with pytest.raises(AuditorContractViolationError, match="g1 JSON parse failed"):
        extract_json_block("```json\n{nope\n```", subject="g1", error=AuditorContractViolationError)

def test_returns_decoded():
    assert extract_json_block('```json\n{"a": 1}\n```', subject="g", error=AuditorContractViolationError) == {"a": 1}
```

```python
# test_loader.py (add)
def test_write_text_record_wraps_oserror(tmp_path):
    blocker = tmp_path / "f"; blocker.write_text("x", encoding="utf-8")
    with pytest.raises(ReportWriteError, match=r"f/out\.md.*rerun") as ei:
        write_text_record(blocker / "out.md", "t", error=ReportWriteError, hint="rerun")
    assert isinstance(ei.value.__cause__, OSError)

def test_write_text_record_makes_parents(tmp_path):
    p = write_text_record(tmp_path / "a" / "b.md", "é\n", error=ReportWriteError)
    assert p.read_text(encoding="utf-8") == "é\n"
```

In `test_adr_exceptions.py`, add both new classes to the derive-from-`AcfError`-alone parametrisation.

- [ ] **Step 2: Run them and see them fail**

Run: `PYTHONUTF8=1 python -m pytest -q plugins/arch-compliance/tests/test_agent_payload.py plugins/arch-compliance/tests/test_loader.py plugins/arch-compliance/tests/test_adr_exceptions.py`
Expected: FAIL with ImportError.

- [ ] **Step 3: Implement**

- Move the fence regex, the count checks and the decode out of `parser.py:53-63` into `extract_json_block`. Keep the three message texts verbatim, with `{subject}` where they now have `{expected_reviewer}`. `parse_reviewer_payload` calls it with `subject=expected_reviewer, error=ReviewerContractViolationError` and keeps its identity check and schema step.
- `write_text_record` makes the parent directory and writes UTF-8. On `OSError` it raises `error(f"cannot write {path.as_posix()}: {exc}" + (f". {hint}" if hint else ""))` from the original exception.
- `write_run_detail` calls it with `error=RunDetailWriteError` and passes its current advice sentence as `hint`.

- [ ] **Step 4: Run the full suite**

Run: `PYTHONUTF8=1 python -m pytest -q`
Expected: PASS. The existing `test_adr_parser.py` and `test_adr_run_detail.py` pass unchanged.

- [ ] **Step 5: Commit**

`git commit -m "feat(acf): shared JSON-block extractor and record writer"`

---

### Task 2: `path_matches`, `RepoTree.files`, `REVIEW_REL`

**Files:**
- Modify: `plugins/arch-compliance/python/acf/repo.py`, `plugins/arch-compliance/tests/test_repo_tree.py`

**Interfaces:**
- Produces:
  - `REVIEW_REL = CONFIG_DIR / "review.yml"`;
  - `path_matches(key: str, pattern: str) -> bool`;
  - `RepoTree.files(self, include: Sequence[str], exclude: Sequence[str]) -> list[Path]`, sorted by key, regular files only, never outside the root.

- [ ] **Step 1: Write the failing tests.** The cases are §4.7 step 2's pattern forms, verbatim.

```python
@pytest.mark.parametrize("key,pattern,hit", [
    ("tests/a.py", "tests/", True),
    ("plugins/arch-compliance/tests/x.py", "tests/", True),     # single-segment, any depth
    ("docs/reviews/r.md", "docs/reviews/", True),
    ("x/docs/reviews/r.md", "docs/reviews/", False),            # multi-segment, from root
    ("a/b/test_x.py", "test_*.py", True),                       # basename, any depth
    ("templates/families/f.tex", "templates/families/**/*.tex", True),  # ** = zero segments
    ("templates/families/a/b/f.tex", "templates/families/**/*.tex", True),
    ("admin/js/vendor/x/y.js", "admin/js/vendor/**", True),     # trailing /**
    ("templates/families/a/style.yml", "templates/families/*/style.yml", True),
    ("templates/families/a/b/style.yml", "templates/families/*/style.yml", False),  # * within one segment
    ("src/a.test.ts", "**/*.test.*", True),
    ("archive/x.py", "archive/", True),
])
def test_path_matches_forms(key, pattern, hit):
    assert path_matches(key, pattern) is hit

def test_backslash_pattern_refused():   # Review Focus 1
    with pytest.raises(AcfInputError, match="backslash"):
        path_matches("admin/js/a.js", "admin\\js\\**")

def test_files_includes_excludes_and_stays_in_root(tmp_path): ...
    # build a/x.py, a/tests/y.py, b/z.ts; files(["**/*.py"], ["tests/"]) == [root/"a/x.py"]
```

- [ ] **Step 2: Run them and see them fail**

Run: `PYTHONUTF8=1 python -m pytest -q plugins/arch-compliance/tests/test_repo_tree.py`
Expected: FAIL with ImportError.

- [ ] **Step 3: Implement**

- `path_matches` translates the pattern to a regex: `**/` matches zero or more `segment/`, a trailing `/**` matches everything below, `*` matches `[^/]*`, `?` matches `[^/]`. The trailing-`/` and no-`/` forms are handled before translation, exactly as §4.7 step 2 says.
- A pattern containing `\` raises `AcfInputError` whose message says `backslash` and names the pattern.
- `files` walks `self.root` with `os.walk` and does not follow symlinked directories. It keys each file through `self.key` and keeps a file that matches any `include` and no `exclude`.

- [ ] **Step 4: Run the tests and see them pass.** Same command. Expected: PASS.

- [ ] **Step 5: Commit**

`git commit -m "feat(acf): one repository glob matcher and RepoTree.files"`

---

### Task 3: `anchor_line` and `doctrine_section`

**Files:**
- Modify: `plugins/arch-compliance/python/acf/registry.py:220-223`, `plugins/arch-compliance/tests/test_registry.py`
- Create: `plugins/arch-compliance/python/acf/review/__init__.py`, `plugins/arch-compliance/tests/test_review_doctrine.py`

**Interfaces:**
- Produces:
  - `anchor_line(doctrine_text: str, anchor: str) -> int | None` (0-based index of the first line whose stripped text equals `anchor.strip()`);
  - `doctrine_section(doctrine_text: str, anchor: str, *, mandate_id: str) -> str`.

- [ ] **Step 1: Write the failing tests**

```python
def test_anchor_line_first_match():
    assert anchor_line("x\n## A\n## A\n", "## A") == 1
    assert anchor_line("x\n", "## A") is None

DOC = "# T\n## A\na1\n### A.1\na2\n## B\nb\n"
def test_section_stops_at_same_or_higher_heading():
    assert doctrine_section(DOC, "## A", mandate_id="m") == "## A\na1\n### A.1\na2"
def test_non_heading_anchor_stops_at_any_heading():
    assert doctrine_section(DOC, "a1", mandate_id="m") == "a1"
def test_unresolved_anchor_names_mandate():
    with pytest.raises(AcfInputError, match="'m'.*## Z"):
        doctrine_section(DOC, "## Z", mandate_id="m")
```

Leave the existing `missing_anchors` test unchanged.

- [ ] **Step 2: Run them and see them fail.** `PYTHONUTF8=1 python -m pytest -q plugins/arch-compliance/tests/test_registry.py plugins/arch-compliance/tests/test_review_doctrine.py` → FAIL.

- [ ] **Step 3: Implement.** Rewrite `missing_anchors` as `[m.id for m in registry.mandates if anchor_line(doctrine_text, m.arch_anchor) is None]`, with the same signature. `doctrine_section` returns the lines joined by `\n`, with trailing blank lines stripped.

- [ ] **Step 4: Run the full suite** → PASS. This covers the self-host and profile-drift tests that call `missing_anchors`.

- [ ] **Step 5: Commit**

`git commit -m "feat(acf): one anchor resolver shared by missing_anchors and the review"`

---

### Task 4: Baseline aggregation over a protocol, declared subsystems

**Files:**
- Modify: `plugins/arch-compliance/python/acf/baseline.py:50-75`, `plugins/arch-compliance/tests/test_baseline.py`

**Interfaces:**
- Produces:
  - `class Locatable(Protocol): mandate_id: str; path: str`;
  - `subsystem_of(posix_path: str, *, prefixes: Sequence[str]) -> str`;
  - `aggregate(findings: Iterable[Locatable], *, prefixes: Sequence[str]) -> dict[tuple[str, str], int]`.
- `save_baseline` writes through `write_text_record(..., error=BaselineError)`.

- [ ] **Step 1: Write the failing tests**

- Update `:52-60` so both tests pass `prefixes=[]`.
- Update the existing `aggregate` test the same way.
- Add these:

```python
def test_prefix_longest_wins_and_other():
    pre = ["scripts/", "scripts/core/"]
    assert subsystem_of("scripts/core/x.py", prefixes=pre) == "scripts/core/"
    assert subsystem_of("scripts/y.py", prefixes=pre) == "scripts/"
    assert subsystem_of("admin/a.js", prefixes=pre) == "other"

def test_aggregate_accepts_a_second_model():
    @dataclass
    class F:
        mandate_id: str
        path: str
    assert aggregate([F("m", "scripts/a.py")], prefixes=["scripts/"]) == {("m", "scripts/"): 1}
```

The dataclass stands in for `AuditorFinding`, so this task does not depend on Task 5.

- [ ] **Step 2: Run them and see them fail.**

- [ ] **Step 3: Implement.** Only an empty `prefixes` keeps the first-segment rule. The current skill's `bl.aggregate(findings)` call goes away in Task 12; nothing else calls it.

- [ ] **Step 4: Run the full suite** → PASS.

- [ ] **Step 5: Commit**

`git commit -m "feat(acf): baseline aggregation over a protocol with declared subsystems"`

---

### Task 5: Review contract and host declaration

**Files:**
- Create: `plugins/arch-compliance/python/acf/review/contract.py`, `plugins/arch-compliance/python/acf/review/host.py`, `plugins/arch-compliance/tests/test_review_host.py`

**Interfaces:**
- Produces (every model uses `extra="forbid"`):
  - `AuditorSeverity = Literal["blocking", "important", "nit", "suggestion"]`;
  - `AuditorFinding(mandate_id: str, path: PosixStr, line: int ≥ 1, snippet: str, severity: AuditorSeverity, rule: str, why: str, suggested_fix: str)`;
  - `AuditorPayload(group: str, files_examined: int ≥ 0, findings: list[AuditorFinding], errors: list[str])`;
  - `ReviewHostConfig(report_dir: PosixStr, baseline_path: PosixStr, baseline_max_age_days: int > 0, baseline_max_commits: int > 0, packs: list[str], subsystems: list[PosixStr], exclude: list[str])`, every field required;
  - `load_review_config(repo: Path) -> ReviewHostConfig`, built on `require_file` and `load_model_file` as `adr/host.py:28-33` is. Its missing-file message names `/acf-setup`.

- [ ] **Step 1: Write the failing tests**

They cover a missing field, an extra field, a backslash in `report_dir` and a missing file. Each raises `AcfInputError`, and the missing-file case matches `acf-setup`. Add one valid load.

- [ ] **Step 2: Run them and see them fail. Step 3: Implement. Step 4: Run them and see them pass.**

- [ ] **Step 5: Commit**

`git commit -m "feat(review): finding contract and review.yml declaration"`

---

### Task 6: Rule settings, `RULES`, `check_auditors`, row selection

**Files:**
- Create: `plugins/arch-compliance/python/acf/review/rules.py`, `plugins/arch-compliance/tests/test_review_rules.py`

**Interfaces:**
- Produces:
  - `RuleSettings(BaseModel)`: `extra="ignore"`, with `surface: list[str] | None = None`, `surface_exclude: list[str] = []` and `docs: list[str] = []`.
  - The twelve models below, each subclassing `RuleSettings`. Every key is optional: an absent scalar is `None` and an absent list is `[]` (§4.4).
  - `RULES: dict[str, type[RuleSettings]]`.
  - `@dataclass(frozen=True) ReviewRow(mandate: Mandate, settings: RuleSettings | None, prompt: Path | None, undeclared: list[str])`.
  - `check_auditors(registry: MandateRegistry, repo: Path) -> list[ReviewRow]`.
  - `select_rows(rows: list[ReviewRow], ids: Sequence[str] | None) -> list[ReviewRow]`.
  - `group_rows(rows: list[ReviewRow]) -> dict[str, list[ReviewRow]]`, keyed by `auditor`.

| Rule id | Model fields beyond `RuleSettings` |
|---|---|
| `fail-loud` | `exception_base: ExceptionBase \| None` (`class_name: str`, `module: str`) |
| `no-shims` | `exempt_paths: list[str]` |
| `posix-paths` | `path_types: list[str]` |
| `class-cohesion` | `facades: list[str]` |
| `ui-logic-isolation` | — |
| `single-owner` | `target_literal_re: str \| None` (must compile), `allowlist_globs: list[str]`, `inventory: str \| None` |
| `pipeline-isolation` | `shared_stages`, `variant_stages`, `exempt`, `variant_terms`, `raw_sources: list[str]`; `canonical_artifact: str \| None` |
| `presentation-as-data` | `bindings: list[str]`; `style_schema`, `element_key`, `variant_key: str \| None` |
| `layer-boundaries` | `tiers: list[Tier]` (`name: str`, `paths: list[str]`); `crossings: list[Crossing]` (`from_tier`, `to_tier: str`, `root_names`, `via: list[str]`) |
| `state-machine-discipline` | `base_classes: list[str]`; `state_field`, `validator_name: str \| None` |
| `path-provenance` | `classifier: str \| None` |
| `data-access-boundary` | `client_paths`, `policy_files`, `privileged_credentials`, `replication_rules: list[str]` |

`check_auditors` takes active rows with `auditor` set, whatever their `call_sites`, and handles each by its `auditor` value:

- **A key of `RULES`.** It validates `params or {}` with that model; a `ValidationError` becomes `AcfInputError(f"mandate {id!r}: ...")`. Undeclared keys are the params keys minus the model's fields: they go in `undeclared` on an `ast`/`guard` row and raise `AcfInputError` naming the id and the keys on any other row.
- **A value ending in `.md`.** It is resolved with `RepoTree(repo).file(auditor)`. A `None` raises `UnknownMandateError` naming the row and the path.
- **Anything else.** It raises `UnknownMandateError` naming the row and the value.

`select_rows` returns `rows` when `ids` is `None`. Otherwise it returns the rows whose ids are in `ids`, and an id matching no row raises `UnknownMandateError` naming it.

- [ ] **Step 1: Write the failing tests.** Build each registry with `MandateRegistry.model_validate`. Use a `_row(**over)` helper that fills a valid `llm` row with `call_sites: [ci]`.

```python
def test_wrong_type_names_mandate(): # single-owner, allowlist_globs: "x" -> AcfInputError match "'r1'"
def test_undeclared_key_listed_on_ast_row_refused_on_llm_row(): ...
def test_unknown_auditor_and_missing_hatch(tmp_path): ...  # both UnknownMandateError
def test_hatch_resolves(tmp_path): ...                      # prompt == tmp_path/"p.md"
def test_inactive_row_not_reviewed(): ...                   # status unenforced -> []
def test_reviewed_whatever_call_sites(): ...                # call_sites [ci] -> reviewed
def test_uncompilable_target_literal_re(): ...
def test_select_rows_unknown_id(): ...                      # Review Focus 5
def test_absent_settings_are_off(): ...                     # fail-loud row, no params -> exception_base is None
```

- [ ] **Step 2: Run them and see them fail. Step 3: Implement. Step 4: Run them and see them pass.**

- [ ] **Step 5: Commit**

`git commit -m "feat(review): rule settings models and auditor validation"`

---

### Task 7: Technology packs

**Files:**
- Create:
  - `plugins/arch-compliance/python/acf/review/packs.py`;
  - `plugins/arch-compliance/python/acf/review/packs/{python,ts-js,react,svelte,html-templates,sql}.yml`;
  - `plugins/arch-compliance/tests/test_review_packs.py`.
- Modify: `pyproject.toml` (`[tool.setuptools.package-data]` `acf = ["judge_prompt.md", "review/packs/*.yml"]`)

**Interfaces:**
- Produces:
  - `Hint(pattern: str, tell: str)`, whose pattern must compile;
  - `TechPack(id: str, language: Literal["python", "typescript", "none"], extends: str | None, files: list[str], hints: dict[str, list[Hint]])`, with `extra="forbid"`, so a `detectors` key is refused;
  - `load_packs(ids: Sequence[str]) -> dict[str, TechPack]`, which reads the declared packs from the package directory, refuses an unknown id, a hint key not in `RULES`, and an add-on whose `extends` base is not also declared;
  - `packs_for_row(row: Mandate, packs: dict[str, TechPack]) -> list[TechPack]` (§4.3 matching: `both` is python and typescript; `none`-language packs always apply);
  - `hint_files(pack: TechPack, packs: dict[str, TechPack]) -> list[str]`, the file globs a pack's hints scan: its own `files`, plus every add-on's `files` when the pack is the base of a declared add-on.

Pack contents follow §4.3's table:

- Python hints port the "Detection patterns" sections of `hm:.claude/skills/architecture-review/auditors/*.md`, with every repository value replaced by a reference to a settings key.
- The `ts-js` UI tells copy `hm:scripts/core/architecture_review/ui_logic_prepass.py:31-52`.
- `react` copies the "Check" shapes of `plugins/arch-compliance/skills/architecture-review/auditors/react-boundaries.md`.
- `svelte` covers `$derived(`, `$state(` and `$effect(`, with `files: ["**/*.svelte"]`.
- `html-templates` covers `files: ["**/*.html", "**/*.htm"]`.
- `sql` covers `files: ["**/*.sql"]`.

- [ ] **Step 1: Write the failing tests**

Each shipped pack loads. Hint keys are rule ids. An add-on without its base is refused. A `detectors` key is refused (write a temporary pack dict and validate it). A `python` row receives the `python` and `sql`/`html-templates` packs and not `ts-js`. `hint_files` for `ts-js` with `svelte` declared includes `**/*.svelte`.

- [ ] **Step 2: Run them and see them fail. Step 3: Implement. Step 4: Run them and see them pass,** including `test_packaging.py`, which now sees the yml files in the wheel.

- [ ] **Step 5: Commit**

`git commit -m "feat(review): technology packs"`

---

### Task 8: Target tree, row surfaces, pre-pass

**Files:**
- Create: `plugins/arch-compliance/python/acf/review/prepass.py`, `plugins/arch-compliance/tests/test_review_prepass.py`

**Interfaces:**
- Consumes: `RepoTree.files`, `path_matches` (Task 2); `ReviewRow` (Task 6); `TechPack`, `packs_for_row`, `hint_files` (Task 7); `ReviewHostConfig` (Task 5).
- Produces:
  - `BUILTIN_EXCLUDES` and `TEST_PATHS`, the tuples of §4.7 step 2, verbatim;
  - `target_tree(tree: RepoTree, cfg: ReviewHostConfig, packs: dict[str, TechPack], *, paths: Sequence[str] | None, include_tests: bool) -> list[str]`, which returns keys and raises `EmptyTargetTreeError` when empty;
  - `row_surface(tree, cfg, packs, row: ReviewRow, target: list[str], *, include_tests: bool) -> list[str]`, the §4.7 step 3 rules (a declared surface ignores `--paths`; one matching no file raises `AcfInputError` naming the mandate id; a hatch row with no surface uses its `languages` the same way);
  - `Candidate(path: str, line: int, tell: str, snippet: str)`;
  - `scan(tree, row: ReviewRow, surface: list[str], packs) -> list[Candidate]`;
  - `render_candidates(cands) -> str` (`file:line [tell] snippet`, one per line).

- [ ] **Step 1: Write the failing tests** in a `tmp_path` tree:
  - candidates per pack and language;
  - `surface_exclude` applies;
  - a rule with no hints yields `[]`;
  - test paths drop unless `include_tests`;
  - an empty tree raises;
  - a declared surface matching nothing raises with the id;
  - Review Focus 3: a file holding the bytes `b"\xff\xfe"` inside the surface raises `AcfInputError` matching its POSIX key.

- [ ] **Step 2: Run them and see them fail. Step 3: Implement.** Read each file with `encoding="utf-8"` and wrap a `UnicodeDecodeError` in `AcfInputError(f"{key}: not UTF-8 ...")`. **Step 4: Run them and see them pass.**

- [ ] **Step 5: Commit**

`git commit -m "feat(review): target tree, surfaces and hint pre-pass"`

---

### Task 9: Payload parsing, exemptions, report

**Files:**
- Create: `plugins/arch-compliance/python/acf/review/aggregator.py`, `plugins/arch-compliance/tests/test_review_aggregator.py`

**Interfaces:**
- Consumes: `extract_json_block`, `AuditorContractViolationError`, `write_text_record`, `ReportWriteError` (Task 1); `AuditorPayload` (Task 5); `ReviewRow` (Task 6).
- Produces:
  - `parse_auditor_payload(payload: str, *, group: str, rows: list[ReviewRow], surfaces: dict[str, list[str]], tree: RepoTree) -> AuditorPayload`. It raises `AuditorContractViolationError` on any of these:
    - an extractor failure;
    - a schema failure;
    - `group` mismatch;
    - a `mandate_id` not among `rows`;
    - a `path` not in that row's surface;
    - a `line` past the file's end.
  - `@dataclass GroupResult(group: str, status: Literal["OK", "FAILED"], payload: AuditorPayload | None, raw: str, error: str | None)`.
  - `apply_exemptions(findings: list[AuditorFinding], rows: dict[str, ReviewRow], tree: RepoTree) -> tuple[list[AuditorFinding], int]`, using `token_exempted` over the source line.
  - `render_report(*, commit: str, invocation: str, results: list[GroupResult], findings: list[AuditorFinding], exempted: int, rollup_md: str) -> str`.
  - `write_report(tree: RepoTree, cfg: ReviewHostConfig, text: str, today: date) -> Path`, which writes `ARCHITECTURE_REVIEW_<date>.md`, then `_2`, `_3` and so on, never overwriting, through `tree.contained` and `write_text_record(error=ReportWriteError)`.

- [ ] **Step 1: Write the failing tests:**
  - a good payload parses;
  - a finding outside the group's rows is a violation;
  - group mismatch is a violation;
  - Review Focus 4: an out-of-surface path and a line past the end are violations, and `render_report` with one FAILED and one OK group shows both, the FAILED one with its raw payload and error;
  - an exempted line is dropped and counted;
  - a second same-day report gets `_2`.

- [ ] **Step 2: Run them and see them fail. Step 3: Implement. Step 4: Run them and see them pass.**

- [ ] **Step 5: Commit**

`git commit -m "feat(review): auditor payloads, exemptions and report"`

---

### Task 10: Drift, staleness, provenance, roll-up

**Files:**
- Create: `plugins/arch-compliance/python/acf/review/rollup.py`, `plugins/arch-compliance/tests/test_review_rollup.py`

**Interfaces:**
- Consumes: `acf.diff.run_git`; `load_baseline`, `compute_drift`, `aggregate`, `render_drift_section` (Task 4); `AuditorFinding`.
- Produces:
  - `Staleness(age_days: int | None, commits_behind: int | None, warnings: list[str], unknown: str | None)`;
  - `staleness(repo: Path, baseline: Baseline, *, max_age_days: int, max_commits: int, now: datetime) -> Staleness`, ported from `hm:scripts/ci/baseline_staleness.py:24-76`, where a non-zero `rev-list` sets `unknown = "staleness unknown: " + stderr.strip()`;
  - `Provenance = Literal["pre-baseline", "post-baseline", "uncommitted", "unresolved"]`;
  - `provenance(repo: Path, finding: AuditorFinding, baseline_commit: str) -> tuple[Provenance, str | None]` (stricter choice 4; an all-zero commit id is `uncommitted`; `merge-base --is-ancestor <c> <baseline_commit>` gives 0 for pre-baseline, 1 for post-baseline, anything else unresolved with git's stderr; a failed blame is unresolved with git's stderr);
  - `render_rollup(*, repo: Path, cfg: ReviewHostConfig, findings: list[AuditorFinding], results: list[GroupResult], now: datetime) -> str`. With no file at `cfg.baseline_path` it omits drift, staleness and provenance and writes `no baseline (run --update-baseline to set one)`. Neither drift, staleness nor provenance affects the exit status.
  - `exit_status(results: list[GroupResult]) -> int`, which is 1 if any group is FAILED and 0 otherwise.

- [ ] **Step 1: Write the failing tests** against a real temporary git repo (`git init`, two commits):
  - staleness by age and by commits;
  - a fresh baseline gives no warning;
  - a baseline commit `deadbeef` gives `unknown` containing git's text;
  - provenance gives pre-baseline, post-baseline and uncommitted, and unresolved for a missing path;
  - no baseline file gives the `no baseline` line and no drift, staleness or provenance heading;
  - Review Focus 2: a committed line `x = "é"` classifies as pre-baseline under `PYTHONUTF8=1`.

- [ ] **Step 2: Run them and see them fail. Step 3: Implement. Step 4: Run them and see them pass.**

- [ ] **Step 5: Commit**

`git commit -m "feat(review): drift, staleness and provenance roll-up"`

---

### Task 11: Rule prompts, output contract, prose checks

**Files:**
- Create: `plugins/arch-compliance/skills/architecture-review/rules/{fail-loud,no-shims,posix-paths,class-cohesion,ui-logic-isolation,single-owner,pipeline-isolation,presentation-as-data,layer-boundaries,state-machine-discipline,path-provenance,data-access-boundary}.md`, `.../rules/_contract.md`
- Delete: `plugins/arch-compliance/skills/architecture-review/auditors/` (four files)
- Modify: `plugins/arch-compliance/tests/test_adr_skill_prose.py`; add a correspondence test to `test_review_rules.py`

Each prompt states:

- its principle (§4.2 table);
- what to flag;
- what not to flag;
- a severity rubric over the four levels;
- how each settings key is used. Settings arrive as `{key}` values in the dispatch, never as literals in the prompt.

Port the substance of the origin auditor named in §4.2's Source column, and of the plugin auditor where one is named. `data-access-boundary` is written from §4.2's paragraph. `_contract.md` fixes the payload: one fenced `json` block matching `AuditorPayload`, which echoes `group`, gives each finding the `mandate_id` of one of the dispatched rows, and draws paths only from the given surface.

- [ ] **Step 1: Write the failing tests**
  - `test_every_rule_has_a_prompt_and_back`: the set of `RULES` keys equals the set of `rules/*.md` stems minus `_contract`.
  - In `test_adr_skill_prose.py`, `FILES` gains the twelve prompts, `_contract.md`, `architecture-review/SKILL.md` and the six pack files.
  - `FORBIDDEN` gains `ContentMetadataService`, `index.yml`, `DeclaredFSM`, `HistoricMansions`, `PosixPathStr`, `structural_realizations`, `IMAGES_YAML`, `scripts/core`, `templates/families`.
  - A new test parses every `plugins/arch-compliance/python/acf/review/*.py` with `ast` and checks that no string constant contains a `FORBIDDEN` item (stricter choice 2).
  - `test_the_seven_files_moved` keeps its own list.

- [ ] **Step 2: Run them and see them fail. Step 3: Write the prompts and delete `auditors/`. Step 4: Run the full suite and see it pass.**

- [ ] **Step 5: Commit**

`git commit -m "feat(review): twelve generic rule prompts and the auditor contract"`

---

### Task 12: Rewrite the skill

**Files:**
- Modify: `plugins/arch-compliance/skills/architecture-review/SKILL.md`, `plugins/arch-compliance/tests/test_adr_skill_prose.py` (`_python_bodies` also covers this skill)

The skill keeps the invocation `[--paths <glob>] [--include-tests] [--mandates <id,...>] [--update-baseline]`. It carries §4.7's eight steps, each a short `python` block calling the Task 2–10 functions:

1. `resolve_repo` → `load_review_config`, `load_mandates(repo / MANDATES_REL)`, `load_packs(cfg.packs)`, `check_auditors`, `select_rows`, `group_rows`.
2. `target_tree`.
3. `row_surface` and `doctrine_section`, with the doctrine read from `ARCH_REL`.
4. `scan` and `render_candidates`.
5. Dispatch one read-only agent per group (tools `Read`, `Grep`, `Glob`), handing it:
   - the prompt (`rules/<id>.md` under `${CLAUDE_PLUGIN_ROOT}`, or the hatch path);
   - `_contract.md`;
   - its rows with id, title and settings (`model_dump(exclude_none=True)`, or raw `params` for a hatch);
   - surfaces, doctrine sections, `docs` and candidates;
   - the instruction *"Read `config/architecture/ARCHITECTURE.md` in full, then every document it points to"*.

   Dispatch with `superpowers:dispatching-parallel-agents`.
6. `parse_auditor_payload` per group. A violation marks the group FAILED with its raw payload and error, and the run continues.
7. `apply_exemptions`, then `render_rollup`.
8. `render_report`, `write_report`. With `--update-baseline`, `save_baseline(tree.contained(cfg.baseline_path), Baseline(..., counts from aggregate(findings, prefixes=cfg.subsystems)))`. Print the roll-up and exit with `exit_status`.

Remove the `Finding` mapping (`:108`) and `Path("config/architecture/mandates.yml")` (`:62`).

- [ ] **Step 1: Write the failing test.** `_python_bodies` includes `architecture-review/SKILL.md`. The existing import-resolution test then fails on the old body's names.
- [ ] **Step 2: Run it and see it fail. Step 3: Rewrite. Step 4: Run the full suite and see it pass,** including the prose test.
- [ ] **Step 5: Commit**

`git commit -m "feat(review): rewrite /architecture-review onto acf.review"`

---

### Task 13: Doctrine, registries, profiles, other skills, self-host tests

**Files:**
- Modify:
  - `config/architecture/ARCHITECTURE.md`;
  - `config/architecture/mandates.yml:51`;
  - `plugins/arch-compliance/profiles/react-app/mandates.yml:46`;
  - `plugins/arch-compliance/skills/acf-mandate/SKILL.md`;
  - `plugins/arch-compliance/skills/acf-setup/SKILL.md`;
  - `tests/test_self_host.py`;
  - `plugins/arch-compliance/tests/test_profile_drift.py`.
- Create: `config/architecture/review.yml`

**Changes:**

- **The two mandate rows.** `auditor: react-boundaries` becomes `auditor: ui-logic-isolation`.
- **`review.yml`.**

  ```yaml
  report_dir: docs/reviews
  baseline_path: docs/reviews/compliance_baseline.json
  baseline_max_age_days: 30
  baseline_max_commits: 250
  packs: [python, ts-js]
  subsystems: []
  exclude: []
  ```

- **`ARCHITECTURE.md`**, every edit in §6's `config/architecture/ARCHITECTURE.md` row:
  - `## React boundaries` names the rule.
  - `## Declared, never defaulted` names `review.yml` and §4.4's built-in meanings, the absent baseline included.
  - Retire the `architecture-review/SKILL.md:62` breach in `## One owner for host paths` and `## Single point of definition`.
  - Record the two path-glob dialects in `## Single point of definition`.
  - `## Release discipline` names the extended check.
  - In `## Host detectors and call sites`: `auditor`, not `call_sites`, selects review rows, and `audit` is an annotation no code reads.
- **`acf-mandate`.**
  - `:46` and `:109-110`, plus `:67` (stricter choice 5), say line equality.
  - `:47` says a rule id or a repository prompt path.
  - The validation snippet adds `from acf.review.rules import check_auditors` and calls `check_auditors(reg, repo)`, and the refusal list names the unknown-`auditor` and missing-prompt cases.
- **`acf-setup`.** It writes `review.yml` and asks for the field values. `:115` and `:138-139` say line equality.
- **The two tests.** `test_self_host.py` gains `test_every_auditor_resolves`, asserting `check_auditors(_registry(), ROOT)` returns without raising. `test_profile_drift.py` calls `check_auditors(regs, profile_dir)` in its loop.

- [ ] **Step 1: Write the two failing test additions.** Run them: they fail on `react-boundaries`, which is unknown.
- [ ] **Step 2: Make the edits. Step 3: Run the full suite and see it pass.**
- [ ] **Step 4: Commit**

`git commit -m "feat(review): self-host declaration, doctrine and skill prose for the port"`

---

### Task 14: Release 0.3.0

**Files:**
- Modify: `scripts/check_installed_skills.py:18-21` (`GATE_SKILLS` gains `"architecture-review"`), `tests/test_check_installed_skills.py`, `README.md`, `pyproject.toml:3`, `plugins/arch-compliance/.claude-plugin/plugin.json:3`

- [ ] **Step 1: Write the failing test.** `tests/test_check_installed_skills.py` asserts that a difference in `architecture-review/rules/fail-loud.md` is reported.
- [ ] **Step 2: Implement.**
  - Add the skill to the tuple.
  - Bump both versions to `0.3.0`.
  - Add a README upgrade note: `config/architecture/review.yml` is required, and `auditor` values are rule ids or repository prompt paths (`react-boundaries` became `ui-logic-isolation`).
- [ ] **Step 3: Run the full suite and the diff gate**, `PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main --call-site ci`. Expected: both pass.
- [ ] **Step 4: Commit**

`git commit -m "chore(release): v0.3.0 — architecture-review port"`

---

### Task 15: Plugin-stage acceptance (§9 items 1 and 3)

- [ ] **Step 1: Self-host run.** Run `/arch-compliance:architecture-review` in this worktree, using the worktree's skill and package. It must run end to end. The first run writes the report with `no baseline`. Then run it with `--update-baseline` and commit the report and the baseline.
- [ ] **Step 2: Scratch repository.** Use a temporary directory outside the repo with:
  - `config/architecture/{ARCHITECTURE.md,mandates.yml,review.yml}`;
  - `packs: [ts-js, svelte]`;
  - one `ui-logic-isolation` row;
  - one `.svelte` file using `$derived(`.

  Run the review end to end. Then run `grep -r -i -E "historic|gemini|scripts/core" <report>`. Expected: no output.
- [ ] **Step 3: Record both runs** in the PR description.
- [ ] **Step 4: Merge and install.** Push, open the PR, and merge on the user's approval. Then update the installed plugin and run `python scripts/check_installed_skills.py <INSTALL_PATH>`. Expected: it exits 0.

---

### Task 16: Origin stage — branch, schema, rows, census edits (in `hm:`)

Work in a new HistoricMansions worktree off its `main`. The requirements are the spec's §5.1–§5.7 tables. This task executes them; it does not restate them.

- [ ] **Step 1: Re-run the census.** Run recipes A, B and C of §5.4 against the worktree's `HEAD` and diff their hits against §5.4's Site column. Any hit not in the table stops the task: rule on its disposition, ledger it in the PR description, then continue. Also run the import check over the whole tree outside `docs` (stricter choice 3): `git grep -n -E "^\s*(from|import) acf\b" -- ':!docs'`. Expected: no output.
- [ ] **Step 2: §5.1 schema.** In `hm:scripts/core/architecture/registry.py`, rename `gemini_anchor` to `arch_anchor` and add `languages` and `params`. Every recipe B site is renamed: §5.4's rows, the 48 row keys included. Each row gains `languages` as §5.1 assigns.
- [ ] **Step 3: §5.2 rows.** Each origin row's `auditor` becomes its rule id, and each row takes the `params` of §5.2's table.
- [ ] **Step 4: §5.3, §5.5 and §5.6.** Add `hm:config/architecture/review.yml`, the twelve anchor headings and the Cursor follow-up row.
- [ ] **Step 5: §5.4 dispositions.** Apply every remaining row in order: deletions, the moved pre-pass, judge prompts, coverage map, exceptions (the `:1525` docstring included) and the hook lines `:137-138`.
- [ ] **Step 6: Dead-code ratchet.** Run `python -m scripts.ci.dead_code_ratchet --check`, quote its output in the PR, then run `--update-baseline`. State the growth `--check` showed. The expected growth is `MandateEntry.arch_anchor` (test-only) and `MandateEntry.languages`.
- [ ] **Step 7: Origin suite.** Run the origin's suite and guards as its CI does. Expected: they pass.
- [ ] **Step 8: Commit** on the origin branch, in origin commit style.

### Task 17: Origin stage — baseline reset and acceptance (§5.7, §9 item 2)

- [ ] **Step 1: Record the installed plugin.** Confirm `python -c "import acf, importlib.metadata as m; print(acf.__file__, m.version('acf'))"` prints version `0.3.0`, and that the installed checkout's `git rev-parse HEAD` equals the merged release commit. Record both in the PR.
- [ ] **Step 2: Reset the baseline.** Delete `hm:docs/architecture/compliance_baseline.json` and run `/arch-compliance:architecture-review --update-baseline` through the installed plugin, as the last change before merge.
- [ ] **Step 3: Compare.** Compare the per-rule finding counts with the last origin report and list the differences in the PR.
- [ ] **Step 4: Fix plugin defects first.** A plugin defect found here is fixed by a plugin patch release before this PR merges.
- [ ] **Step 5: Merge on the user's approval.**

---

## Self-review record

**Spec coverage.**

| Spec section | Task |
|---|---|
| §4.2 | 6, 11 |
| §4.3 | 7 |
| §4.4 | 5, 10, 13 |
| §4.5 | 6, 13 |
| §4.6 | 3, 12 |
| §4.7 | 8–10, 12 |
| §4.8 | 1, 4, 5, 9 |
| §4.9 | 6, 12 |
| §4.10 | 7, 11, 13 |
| §5 | 15–17 |
| §6 rows | 1–14 |
| §7 tests | in the owning tasks; `test_repo.py` → `test_repo_tree.py` (stricter choice 11) |
| §9 items 1, 3 | 15 |
| §9 item 2 | 17 |

**Type consistency.** `ReviewRow`, `GroupResult`, `AuditorPayload`, `Candidate` and `Staleness` are each defined once and consumed by name.

**Proportion.** The plan carries signatures and test assertions. Rule prompt bodies and pack hint lists are left to the implementer, with their sources named.
