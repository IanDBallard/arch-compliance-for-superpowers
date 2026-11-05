# Response to HOST_DETECTOR_EXTENSION_POINT v5 review

- **Spec:** `docs/design/HOST_DETECTOR_EXTENSION_POINT.md` (revised to v6)
- **Reviewed commit:** `aac6142575d32471c0b6f419d5855985d6dcf2ac`
- **Run record:** `docs/reviews/adr_runs/HOST_DETECTOR_EXTENSION_POINT_v5_2026-11-05.md`
- **Declared revision class:** mechanism. The `AdrHostConfig` switch is dropped, and `_call_host` consumes the result fully before rebuilding it; the rest is wording, test-list and prose changes.

Every command below was run in the worktree. The branch changes only `docs/`, so code lines are as at `a338cad`. Outputs are pasted as printed.

## Blocking reasons

### C31 (deletion, load-bearing): "deleting the citations helpers changes exactly one classification"

**Resolution: carried unchanged (spec).** The refutation is correct about the claim text, which the controller carried forward with stale wording. The spec already states both behaviour changes: a drive-relative string becomes `external`, and on Python 3.11 and 3.12 a symlink-loop citation classifies `unresolved` instead of raising. §4.1 says so, and so does the §4.9 citations row. No spec edit is needed; the next run's claim for this deletion states two changes.

Falsify by finding the spec stating one change:

```text
$ grep -n "Two behaviours change" docs/design/HOST_DETECTOR_EXTENSION_POINT.md | cut -c1-80
156:`acf/adr/citations.py` imports `looks_absolute` and `resolve_under_root` and
```

### C77 (sweep, load-bearing): "§4.7 covers every existing test the design breaks"

**Resolution: revised.** `test_unenforced_mandate_does_not_gate` writes a registry whose only row is unenforced, so the new empty-selection refusal would turn its expected exit `0` into exit `1`. §4.7 now changes it: it adds an active row on another detector declaring `ci`, so the call site selects a row, and the test still asserts that the unenforced row does not gate.

Falsify by showing the test's registry has another active row today, or that §4.7 still lists it only as adding `--call-site`:

```text
$ sed -n 102,108p plugins/arch-compliance/tests/test_diff_cli.py
def test_unenforced_mandate_does_not_gate(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write_mandates(repo, _BARE_EXCEPT_ROW.format(severity="BLOCK", status="unenforced"))
    _stage_bad_py(repo)

    code = main(["--mode", "staged", "--repo", str(repo)])
    assert code == 0
$ grep -c "test_unenforced_mandate_does_not_gate" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
1
```

### C80 (shape_fit, load-bearing): "host code runs only inside the wrapped regions"

**Resolution: revised (narrowed), plus one mechanism fix.**
- **Narrowed guarantee.** Decision 7 now states what the wrapping guarantees: every failure raised while a runner calls host code becomes a typed ACF error. It also says what the wrapping does not do. Host code runs in the gate's process and can register an `atexit` handler or start a thread that runs after the runner returns. That code is the host's own, run because the host opted in.
- **Mechanism fix.** `_call_host` now consumes the result fully (`items = list(raw)`) before rebuilding any item. A generator therefore finishes, or raises, inside the `try`, instead of being abandoned when `_revalidate` refuses an item and finalised later.
- **Test.** A test case yields one valid hit and then an invalid item.

Falsify by finding the universal "only inside" claim, or the rebuild still iterating the raw result:

```text
$ grep -c "What the wrapping guarantees" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
1
$ grep -c "items = list(raw)" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
1
$ grep -c "only inside" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
0
```

### mandate claim C64 is REFUTED: "every existing definition a new definition duplicates is deleted"

**Resolution: revised.** Decision 8 no longer makes a universal claim. It says the existing definitions listed in §4.9 are deleted, and that the spec makes no claim §4.9 lists every duplicate. The site the reviewer found, `abs_path = repo / path; if not abs_path.is_file()` in `_scan_changed`, is a different job. Its path comes from git's own `--name-only` output, so it is repo-relative by construction; the check only skips a path that is not a regular file. §5.2 records it as `ADJACENT` with that reason.

Falsify by finding the universal wording, or showing that the `_scan_changed` path can come from the registry or a host:

```text
$ grep -c "makes no claim that §4.9 lists every duplicate" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
2
$ sed -n 118,119p plugins/arch-compliance/python/acf/cli_check_diff.py; sed -n 56p plugins/arch-compliance/python/acf/diff.py
        abs_path = repo / path
        if not abs_path.is_file():
    out = _git(repo, "diff", *_diff_args(mode, base), "--name-only", "--diff-filter=ACMR")
```

### implementability claim C111 is REFUTED: "the design's handlers are tuple handlers the detector does not flag"

**Resolution: revised.** The §6 Fail-loud row now says the handlers are `except BaseException`, and that the detector does not flag them because it matches only a bare handler or the name `Exception`. It also says `_describe`'s handler returns a fallback for the secondary failure only, while the primary failure is still raised as a typed error.

Falsify by finding "tuple handler" in the spec, or a detector that flags `BaseException`:

```text
$ grep -c "tuple handler" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
0
$ sed -n 76,82p plugins/arch-compliance/python/acf/detectors/python_pack.py

def _is_bare_or_exception(node: ast.ExceptHandler) -> bool:
    if node.type is None:
        return True
    if isinstance(node.type, ast.Name) and node.type.id == "Exception":
        return True
    return False
```

### mechanism '_describe fallback message for host exceptions whose __str__ raises' has no named producer — superstition

**Resolution: revised (producer named).** The state has a concrete producer in the origin host's guard code. `BaseException.__str__` returns `str(args[0])` for a one-argument exception, so an exception carrying a host object renders through that object's `__str__`. `hm:scripts/ci/genre_conditional_guard.py:33-40` declares a non-frozen dataclass `Finding` whose `__str__` calls `self.line_text.strip()`. A dataclass does not enforce its annotations. So `ValueError(Finding("a.md", 3, None, "..."))` is a host exception whose `str()` raises `AttributeError`. §4.4 item 4 names this producer, and §4.7 pins it with that exact shape.

Falsify by showing that such an exception formats without raising, or that the cited guard's `__str__` is safe on a `None` field:

```text
$ git -C <HistoricMansions> show b652fab05:scripts/ci/genre_conditional_guard.py | sed -n 33,40p
class Finding:
    path_name: str
    line_no: int
    line_text: str
    reason: str

    def __str__(self) -> str:  # pragma: no cover - trivial formatting
        return f"{self.path_name}:{self.line_no}: {self.reason}: {self.line_text.strip()}"
$ python - (prototype of that dataclass; session scratchpad)
ValueError -> str(exc) raised AttributeError 'NoneType' object has no attribute 'strip'
RuntimeError -> str(exc) raised AttributeError 'NoneType' object has no attribute 'strip'
KeyError formatted: Finding(path_name='a.md', line_no=3, lin
```

## Non-blocking findings folded in

| Finding (reviewer, severity) | Disposition |
|---|---|
| `AdrHostConfig` validation reverses an approved ADR-contract decision (sweeper, important) | Dropped. §5.2 now quotes the contract's *"a visible host choice, not a state the gate must prevent"* (`docs/design/ADR_GATE_HOST_CONTRACT.md:295-301`) and keeps the fields unchanged; the §3, §4.7, §4.8, §4.9, §6.1 and Appendix entries for the switch are removed. |
| Installed hosts' registries lack `precommit` (refuter, important) | Decision 2 states the consequence (a refused, never silent, pre-commit run until the host adds `precommit`), and §4.8 adds an upgrade note to the README and acf-setup. |
| Ratchet walk filter's `except ValueError` becomes unreachable (sweeper, advisory) | Deleted with the ratchet switch (§4.9). |
| `--call-site` invocation list had no recipe (compliance, advisory) | The §4.8 row now carries its `git grep` recipe. |
| `PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:531` is another documented invocation (sweeper, advisory) | Named with the other past-run records left unedited (§4.8). |
| `## Declared, never defaulted` cited for the flag although scoped to `adr.yml` (hardening, advisory) | The spec cites the fail-loud reason and the origin host's per-site selection; the doctrine rule is not cited for the flag. |
| Hook has no empty-selection refusal; `acf-check-llm` does not pass `llm_prompt_ids`; contract-against-dispatch test vs table-driven dispatch; Node literal kept; pydantic versions below 2.13.3 (advisory) | Not changed: each is outside this revision's scope or already argued in the spec (§3 non-goals, §4.3, §4.7). |

## Design-simplification pass

Removed: the `AdrHostConfig` switch and its test, prose, `§6.1` and Appendix entries; the ratchet walk filter's unreachable branch. Added: one line (`items = list(raw)`) and one test case. Net code shrinks.

## Delta pre-flight

One fresh agent with the sweeper and refuter prompts reviewed the 8 claims this revision added or changed.

| Claim | Verdict | Fix folded in |
|---|---|---|
| P1 The raising-`__str__` producer is real | SURVIVED | — |
| P2 `list(raw)` finishes a generator inside the `try` | SURVIVED | — (a generator the host keeps in its own module state stays the host's, as Decision 7 says) |
| P3 `test_unenforced_mandate_does_not_gate` is the one test the refusal breaks | SURVIVED | The repair now names its added row: an active `no-shims.hasattr` row, which does not fire on the staged `bad.py`. |
| P4 The `_scan_changed` path is git-supplied | SURVIVED | — |
| P5 The ratchet walk filter's `except ValueError` cannot fire | SURVIVED | — |
| S1 No section still changes `AdrHostConfig` | REFUTED | The §5.1 row for `ADR_GATE_HOST_CONTRACT.md` still named `acf/adr/host.py` and `:262`; it now says `host.py` is unchanged and updates only `:302-303`. |
| S2 No section claims host code is confined | SURVIVED | — |
| S3 The invocation recipe prints only listed sites | REFUTED | The §4.8 row now classifies every hit: listed command lines and instructions (adding acf-setup `SKILL.md:24`, `:250` and acf-mandate `SKILL.md:131`), named past-run records (adding `PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:223`), or name mentions that run nothing. |

Also folded: `resolve_under_root` accepts an absolute path that lies inside the root, so §4.7, §4.9 and §6.1 now say the ratchet refuses an escaping entry (an absolute path outside the root included), and still accepts an absolute in-root path as today.

```text
$ sed -n 86,87p plugins/arch-compliance/tests/test_diff_cli.py
    bad.write_text(
        "def f():
    try:
        g()
    except Exception:
        pass
",
$ sed -n 24p plugins/arch-compliance/skills/acf-setup/SKILL.md; sed -n 250p plugins/arch-compliance/skills/acf-setup/SKILL.md
9. Smoke-run `acf-check-diff`
| Claiming success without CLI smoke | Run `acf-check-diff` or `python -m acf.cli_check_diff` |
```

## Sentence-type sweep

Swept the whole revised spec. Hits in changed text and their disposition:

| # | Type | Hit | Disposition |
|---|---|---|---|
| T1 | Population without recipe | `--call-site` "at every shipped or documented invocation" (§4.8) | Converted: the row now carries its `git grep` recipe. |
| T3 | Universal quantifier | "Where a new definition here does the job of an existing one, the existing one is deleted" (Decision 8) | Narrowed to the §4.9 list, with an explicit no-completeness statement. |
| T3 | Universal quantifier | "every failure raised while a runner calls host code becomes a typed ACF error" (Decision 7) | Stands, scoped to raised failures; the same bullet says the wrapping does not confine host code. |
| T4 | Prose-only tool behaviour | `BaseException.__str__` rendering `str(args[0])` | Pinned by the §4.7 `test_host_detectors.py` case; prototype output above. |
| T5 | Named construct without receipt | `hm:scripts/ci/genre_conditional_guard.py:33-40`; `diff.py:56` | Receipts above. |
| T6 | Doctrine attribution without quote | ADR contract decision on `AdrHostConfig` | Quoted adjacent in §5.2. |
| T7 | Completeness by recipe only | §4.9 | Not claimed complete; the spec says so. |

Carried text was swept with the same patterns; the carried hits were dispositioned in the v1 to v4 response records and are unchanged.
