# Response to HOST_DETECTOR_EXTENSION_POINT v4 review

- **Spec:** `docs/design/HOST_DETECTOR_EXTENSION_POINT.md` (revised to v5)
- **Reviewed commit:** `ac526748ac3877dfab9b45884928aaee03b371fc`
- **Run record:** `docs/reviews/adr_runs/HOST_DETECTOR_EXTENSION_POINT_v4_2026-11-05.md`
- **Declared revision class:** mechanism. The required `--call-site` argument, the ratchet's path resolution, the `AdrHostConfig` path validation, the params-to-arguments functions, the deleted detector-id sets, `CallSite`, `file_under_root`, `parse_python`, `_describe` and the rebuilding of each `HostHit` all change the design.

Every command below was run in the worktree. The branch changes only `docs/`, so code lines are as at `a338cad`. Outputs are pasted as printed. `proto5.py` is in the session scratchpad.

**One rule answers the four scope blockers.** The new Decision 8: what this design makes redundant is deleted, and its callers switch to the one definition. §4.9 lists each deletion with its recipe and the behaviour it changes. The spec no longer records any of these as debt, and makes no claim about the rest of the tree.

## Blocking reasons

### C61 (shape_fit, load-bearing): "the ratchet joins are the one other registry-path-to-file implementation"

**Resolution: revised.** The run found a third owner: `AdrHostConfig.runs_dir` and `ledger_path`, checked only by `PosixStr` and joined as `repo / cfg.runs_dir` in the gate skills. Under Decision 8, both fields now validate through `validate_posix_rel_path`, which makes those joins contained without touching the skills. The ratchet switches to `resolve_under_root` instead of being recorded as debt. Both are §4.9 rows, and shipped values are checked in the Appendix. The claim that names "the one other" implementation is gone.

Falsify by showing a shipped `adr.yml` value the new validator would refuse, or the old field type still in force after the change:

```text
$ sed -n 24,25p plugins/arch-compliance/python/acf/adr/host.py
    runs_dir: PosixStr = Field(min_length=1)
    ledger_path: PosixStr = Field(min_length=1)
$ grep -n "runs_dir\|ledger_path" config/architecture/adr.yml
1:runs_dir: docs/reviews/adr_runs
2:ledger_path: docs/reviews/adversarial_design_ledger.jsonl
$ git -C <HistoricMansions> show b652fab05:config/architecture/adr.yml
runs_dir: docs/reviews/adr_runs
ledger_path: docs/reviews/adversarial_design_ledger.jsonl
```

### C72 (shape_fit, load-bearing, UNPROVEN): "host code runs in exactly two wrapped regions"

**Resolution: revised.** The run found two paths where host code could run outside the regions:
- **Exception formatting.** Both handlers formatted the host exception with `{exc}` after the `try` had exited. They now format it through `_describe`, which wraps `str(exc)` and falls back to the exception's type name.
- **Field access.** `_call_host` now rebuilds every item inside its `try` with `_revalidate`. That function refuses any type but exactly `HostHit`, so a host subclass whose properties could run host code is refused. It then validates the item's field values afresh, so a hit built with `model_construct` cannot carry host objects either. `_to_findings` only ever sees rebuilt hits.

Falsify by showing a host exception's `__str__` escaping through `_describe`, or a subclass or an unvalidated hit passing the rebuild:

```text
$ python proto5.py   # parts 1 and 2
1 f-string on host exc raised: str boom
1 _describe: Bad (message unavailable)
2 type(h) is HostHit: True | type(s) is HostHit: False | isinstance(s): True
$ python - (rebuild prototype, session scratchpad)
A model_construct hit refused: ValidationError
B rebuilt path type: str
C genuine passes: True
D host exception (message unavailable)
$ grep -c "def _describe" docs/design/HOST_DETECTOR_EXTENSION_POINT.md; grep -c "def _revalidate" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
1
1
```

### mandate claim C52 is REFUTED: "every population claim carries a recipe" ("One breach remains" had none)

**Resolution: revised.** The sentence is deleted. §6 now says the definitions listed in §4.9 are deleted, and that the spec makes no claim that §4.9 lists every duplicate in the tree. Each §4.9 row carries its own recipe and output.

Falsify by finding the unbacked census still in the spec:

```text
$ grep -c "One breach remains" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
0
$ grep -c "makes no claim that §4.9 lists every duplicate" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
1
```

### mandate claim C55 is REFUTED: "the one remaining breach is the ratchet's path joins"

**Resolution: revised.** The run found the params-to-arguments code for the facade, FSM and build-artifact scanners duplicated across both gates, in loops this design edits. Each scanner module now owns one function (`facade_sink_args`, `fsm_guard_args`, `build_artifact_args`) with today's defaults. Both gates call it, the two copies are deleted (§4.3, §4.6, §4.9), and a test pins the defaults (§4.7). The ratchet joins are converted rather than kept as "the one breach" (C61).

Falsify by showing the duplicated extraction sites the §4.9 row names:

```text
$ git grep -n 'params.get("target_literal_re"\|params.get("state_field"\|params.get("path_prefixes")' -- '*.py'
plugins/arch-compliance/hooks/posttooluse_gate.py:262:                        target_literal_re=str(params.get("target_literal_re", "")),
plugins/arch-compliance/hooks/posttooluse_gate.py:274:                        state_field=str(params.get("state_field", "")),
plugins/arch-compliance/hooks/posttooluse_gate.py:288:        prefixes = params.get("path_prefixes")
plugins/arch-compliance/python/acf/cli_check_diff.py:135:                        target_literal_re=str(params.get("target_literal_re", "")),
plugins/arch-compliance/python/acf/cli_check_diff.py:147:                        state_field=str(params.get("state_field", "")),
plugins/arch-compliance/python/acf/cli_check_diff.py:160:        prefixes = params.get("path_prefixes")
```

### mandate claim C56 is REFUTED: "the consolidations touch only code paths this design changes" (the citations change is out of scope by the spec's own ratchet test)

**Resolution: revised.** The inconsistency is removed in the direction the doctrine points: everything this design makes redundant is deleted, the ratchet included. Decision 8 quotes `## Scoped refactor`'s *"remove legacy dependencies or non-contractual patterns in code paths you are changing"*. A shared helper introduced here changes the paths that duplicate it, so the old copies go. The spec now applies one test to citations, the ratchet and `AdrHostConfig`. The shared dispatcher and parse helper remain non-goals, because this design does not make those loops redundant (§6 Scoped refactor row).

Falsify by finding the quoted clause absent, or a §4.9 switch whose old caller the spec leaves as recorded debt:

```text
$ sed -n 213,215p config/architecture/ARCHITECTURE.md
Lifted: "Within an approved plan or ticket, remove legacy dependencies or non-contractual
patterns in code paths you are changing. Do not expand scope to unrelated modules"
(HistoricMansions `GEMINI.md` §7, `hm:GEMINI.md:129`). No row: no test enforces this yet.
$ grep -n "^### 4.9" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
485:### 4.9 What this design deletes, and what each switch changes
$ grep -c "PARTIAL_OVERLAP" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
0
```

## Non-blocking findings folded in

| Finding (reviewer, severity) | Disposition |
|---|---|
| Old detector-id sets orphaned and a second definition (compliance, sweeper; converged; important) | Deleted under Decision 8; `KNOWN_DETECTORS` is the one list (§4.3, §4.9). |
| `TS_DETECTOR_IDS` duplicates `TS_MANDATE_IDS` keys (sweeper, advisory) | Deleted (§4.9). |
| Guard read raises on a missing file, a directory, or a 3.13 symlink loop (compliance, hardening, refuter; converged) | `scan_host_guards` checks `candidate is None or not candidate.is_file()` before reading (§4.4 item 7). `proto5.py` part 3: `loop is_file: False`, `dir is_file: False`, `missing is_file: False`. |
| `call_sites` is a free `list[str]`; a typo silently narrows routing (hardening, important) | `CallSite` literal (Decision 2, §4.2). Census: every shipped and test value is `ci`, `hook` or `audit`, or the list is empty (Appendix). `proto5.py` part 4: `typo refused: ValidationError`. |
| Shared mutable AST (hardening, advisory) | Contract states detectors do not change the tree (§4.4 item 6). |
| `fresh_host_loader` evicts unrelated modules (hardening, advisory) | Evicts only host modules (§4.7). |
| `spec_from_file_location` `None` handling unspecified (refuter, advisory) | Shown inside the wrapped region (§4.4 item 3). |
| Decision 6 table had the hooks dir before `python/` (refuter, advisory) | Corrected. |
| Symlink-loop citations change classification (refuter, advisory) | Stated in §4.1 and §4.9. |
| Build-artifact `lstrip` breaks the exemption key for dot-prefixed paths (refuter, advisory) | Stated in §4.5; behaviour unchanged. |
| §5.2 bridge row said `mandate_id` comes from Node; judge cite off by two lines (sweeper, advisory) | Both corrected. |
| `llm_prompt_ids` guards a label nothing dispatches on (hardening, advisory) | Not changed: the check enforces the rule the acf-mandate skill states, and gives `LLM_PROMPT_IDS` its consumer. |
| C76 sub-reason for deferring import (hardening, advisory) | That reason was the controller's claim wording, not spec text; no spec change. |

## Design-simplification pass

Removed: the four detector-id sets; the six inline params extractions; the ratchet's hand-rolled joins; the debt rows and the "one breach" claim; the §4.8 breach-list addition. Added: three `*_args` functions, `CallSite`, `_describe`, the exact-type check, the `is_file` check, and the §4.9 table. Net code in the plan shrinks: each deletion removes more lines than its replacement call adds.

## Delta pre-flight

### Round 1

One fresh agent with the sweeper and refuter prompts reviewed the 10 claims this revision added or changed, against the uncommitted text. It is a rehearsal and writes no ledger row.

| Claim | Verdict | Fix folded in |
|---|---|---|
| P1 Deleting the four id sets breaks nothing outside §4.9 | SURVIVED | — |
| P2 `*_args` keep today's defaults; no third extraction site | SURVIVED | — |
| P3 Ratchet switch refuses no shipped value | SURVIVED | — |
| P4 `AdrHostConfig` switch refuses no shipped value; joins contained | SURVIVED | "Contained" narrowed to lexical containment: a symlinked directory inside the repository can still point outside, as today (§4.9, §5.2). |
| P5 `CallSite` refuses no shipped row | SURVIVED | — |
| P6 Host code runs only inside the regions | REFUTED | A `HostHit` built with `model_construct` passed the exact-type check carrying host objects. Every item is now rebuilt and validated inside `_call_host` (§4.4 item 4). `_describe` also missed a `__str__` raising `SystemExit` and an overridden metaclass `__name__`; it now catches both and returns a constant. |
| P7 Guard read maps every non-file case to `[]` | REFUTED | `is_file()` re-raises permission denied. The new `acf.engine.file_under_root` does resolve plus existence. Each caller (`load_mandates`, `load_host_detector`, `scan_host_guards`) turns its `OSError` into its own typed error (§4.1, §4.2, §4.4). |
| S1 Each §4.9 item has one definition | REFUTED | A fifth id set, `CONFIG_AST_DETECTOR_IDS`, had no consumer; it is deleted too, found by a by-behaviour recipe (`_DETECTOR_IDS`). The `*_args` functions now pass optional params only when set, so each default lives once, in the scanner's signature. |
| S2 Decision 8 applied consistently | REFUTED | The host runner adds one more parse-and-skip, so by Decision 8 the shared helper is in scope: `acf.engine.parse_python`, used by four scanners and the host runner. The dispatcher stays out, with the reason now stated: two call sites of one procedure are not a second definition. |
| S3 Prose sweep complete | REFUTED | The `python-service` profile's `[ci]`-only `no-shims.hasattr` row loses its edit-time `WARN` for every host installed from it; this is now an accepted consequence in Decision 2. The `detectors/__init__.py:1` docstring is reworded (§4.3). |

The round's important finding: the origin host's guard runner keeps `ci` and `precommit` apart (`hm:scripts/ci/run_guards.py:116`). v5's draft merged them. With the user's choice, `acf-check-diff` now takes a required `--call-site {ci,precommit}` (Decision 2, §4.6), and every shipped or documented invocation is updated (§4.8).

```text
$ git -C <HistoricMansions> show b652fab05:scripts/ci/run_guards.py | grep -n "known = known_call_sites()\|if site not in entry.call_sites\|Unknown call site"
107:    known = known_call_sites()
110:            f"Unknown call site {site!r}. Registered call sites: {', '.join(sorted(known))}."
116:        if site not in entry.call_sites:
$ git grep -n "_DETECTOR_IDS" -- plugins tests   # adds detectors/__init__.py:21 and :32, CONFIG_AST_DETECTOR_IDS
$ python - (is_file under a monkeypatched PermissionError)
E is_file raised: PermissionError
```

### Round 2

A second fresh agent reviewed the 9 claims round 1's fixes and the `--call-site` decision added.

| Claim | Verdict | Fix folded in |
|---|---|---|
| P1 Required `--call-site` is implementable and routes `[ci]`-only rows | SURVIVED | Decision 2 no longer says the origin host's runner "requires" the site: its `--site` defaults to `ci` (`hm:scripts/ci/run_guards.py:317-321`). |
| P2 §4.8 lists every invocation | REFUTED | Added the acf-setup CI fallback (`SKILL.md:207`) and the Step 9 smoke check (`:217`, `:219`) and its success criteria; approved specs' recorded verification steps are named and left as records. |
| P3 `_revalidate` refuses non-str/non-int hits; `_describe` cannot raise | REFUTED | Lax validation coerced `b"a.py"` and `"5"`; `_revalidate` now checks exact field types before validating. Custom `BaseException` subclasses escaped; all three handlers now catch every exception and re-raise only `KeyboardInterrupt`. |
| P4 `file_under_root` callers end in typed errors | SURVIVED | §4.1 states that this holds on Python 3.11 to 3.13; a later `is_file()` that swallows every `OSError` reports the path as missing, which is still typed or fail-safe. |
| P5 `parse_python` replaces the four copies unchanged | SURVIVED | — |
| P6 Five id sets are the only built-in id sets | SURVIVED | — |
| P7 `*_args` produce today's calls | SURVIVED | "Set" is defined as key present, `null` included (§4.3). |
| S1 `file_under_root` is the single resolve-plus-existence check | REFUTED | The ratchet's `load_baseline` kept its own `is_file()`; `scan_ratchet` now uses `file_under_root` for `baseline` (§4.9). |
| S2 Accepted consequences cover every reporting change | REFUTED | Blocking finding: no shipped row declared `precommit`, so `--call-site precommit` would have run nothing and passed. Each shipped `ast`/`guard` row declaring `ci` now also declares `precommit` (9, 7, 3 and 3 rows, Appendix), and a site that selects no active row is refused with `AcfInputError` (§4.6, §6.1), as the origin host's runner refuses an empty selection (`:126-130`). |

```text
$ git -C <HistoricMansions> show b652fab05:scripts/ci/run_guards.py | sed -n 126,130p
    if not modules:
        raise _runner_error(
            f"Call site {site!r} resolves to zero enforced guard mandates — "
            "refusing to report a green run over an empty guard set."
        )
$ git grep -n "precommit" -- '*.yml'   # before this change
(no output)
$ grep -n "is_file" plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py
78:    if not path.is_file():
```

## Sentence-type sweep

Swept the whole revised spec. Hits in changed text and their disposition:

| # | Type | Hit | Disposition |
|---|---|---|---|
| T1 | Population without recipe | "every shipped value" (Decision 8); shipped `call_sites` values | Converted: Appendix rows with recipes and outputs. |
| T2 | Aggregate as claim | None added. | — |
| T3 | Universal quantifier | "One breach remains" (§6) | Deleted. |
| T3 | Universal quantifier | "Each existing definition this design duplicates is deleted" (draft §6) | Narrowed to "the existing definitions listed in §4.9", with an explicit no-completeness statement. |
| T3 | Universal quantifier | "a symlink loop on every supported Python" (§4.4 item 7) | Narrowed to Python 3.11 through 3.13. |
| T3 | Universal quantifier | "refused before any field is read" (§4.4 item 5) | Stands: the type check precedes field access in the stated order; `proto5.py` part 2. |
| T4 | Prose-only tool behaviour | `is_file()` on a loop or directory; `f"{exc}"` running `__str__`; `Literal` refusing a typo | Pinned by `test_host_detectors.py` and `test_registry.py` cases (§4.7); prototype output above. |
| T5 | Named construct without receipt | `build_artifacts.py:27` `lstrip`; `adr/host.py:24-25` fields | Receipts above and in §4.9. |
| T6 | Doctrine attribution without quote | `## Scoped refactor` (Decision 8) | Quoted adjacent. |
| T7 | Completeness by recipe only | §4.9 | Not claimed complete; the spec says so. |

Carried text was swept with the same patterns; the carried hits were dispositioned in the v1 to v3 response records and are unchanged.
