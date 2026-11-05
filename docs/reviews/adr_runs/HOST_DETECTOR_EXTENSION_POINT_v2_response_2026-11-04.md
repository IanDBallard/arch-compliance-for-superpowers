# Response to HOST_DETECTOR_EXTENSION_POINT v2 review

- **Spec:** `docs/design/HOST_DETECTOR_EXTENSION_POINT.md` (revised to v3 in the commit that adds this record)
- **Reviewed commit:** `e7dce40d3c231230ed235b559c7346b98238dfd2`
- **Run record:** `docs/reviews/adr_runs/HOST_DETECTOR_EXTENSION_POINT_v2_2026-11-04.md` (BLOCKED)
- **Declared revision class:** mechanism. Built-in detector contracts are checked at load, row-shape rules move onto `Mandate`, the host-call wrap now covers iteration, and root eviction is replaced by refusing a second root.
- **User decisions carried from v2, not reopened:** unified `call_sites` routing; invocation as the opt-in for `acf-check-diff`; one shared engine path helper.

Every command below was run in the worktree at `a338cad`-equivalent code (the branch changes only `docs/`). Outputs are pasted as printed.

## Blocking reasons

### C10 (premise, load-bearing): "the hook may not reference acf.adr, so these helpers cannot serve a hook-reachable caller"

**Resolution: revised.** §1 item 5 no longer infers impossibility from the test. It quotes the test's stated intent, says the test pins only the literal text, and gives the layering reason: `acf.registry` and `acf.enforcement` are imported by the hook, so a generic check imported from `acf.adr` would put `acf.adr` in the hook's graph without tripping the test; `acf.adr` already imports `acf.engine`, so the helpers move with the existing dependency direction.

Falsify by showing the test does more than pin the literal, or that `acf.adr` does not already depend on `acf.engine`:

```text
$ sed -n 70,76p plugins/arch-compliance/tests/test_adr_import_graph.py
def test_hooks_do_not_reach_acf_adr() -> None:
    """Both hooks import acf.repo at module scope, before any third party is
    available. acf.adr pulls in pydantic, so it must never enter that graph.
    """
    for hook in ("inject_constraints.py", "posttooluse_gate.py"):
        src = (PLUGIN_ROOT / "hooks" / hook).read_text(encoding="utf-8")
        assert "acf.adr" not in src, f"{hook} must not reference acf.adr"
$ grep -rn "^from acf\.\|^import acf" plugins/arch-compliance/python/acf/adr/*.py | grep -v "from acf\.adr"
plugins/arch-compliance/python/acf/adr/citations.py:34:from acf.exceptions import CitationHistoryUnavailableError
plugins/arch-compliance/python/acf/adr/contract.py:20:from acf.engine import contains_backslash
plugins/arch-compliance/python/acf/adr/gate.py:51:from acf.exceptions import SpecKindUndeterminedError
plugins/arch-compliance/python/acf/adr/host.py:15:from acf.loader import load_model_file, require_file
plugins/arch-compliance/python/acf/adr/host.py:16:from acf.repo import ADR_REL, ARCH_REL
plugins/arch-compliance/python/acf/adr/ledger.py:32:from acf.exceptions import LedgerWriteError
plugins/arch-compliance/python/acf/adr/parser.py:24:from acf.exceptions import ReviewerContractViolationError
plugins/arch-compliance/python/acf/adr/run_detail.py:31:from acf.exceptions import RunDetailWriteError
```

### C29 (mandate, load-bearing, UNPROVEN): "every §6.1 state is refused by the named component with the named error"

**Resolution: revised.** Three gaps were named.
1. Generator iteration ran outside the wrap. §4.4 item 4 adds `_call_host`, the single wrapped region, which calls the host and materialises the result with `hits = list(raw)` inside the `try`. `_to_findings` now receives a list.
2. `SystemExit` escaped `except Exception`. Both broad handlers (import, call) are now `except (Exception, SystemExit)`. `KeyboardInterrupt` is deliberately not caught.
3. The §6.1 "no `repo_root`" row omitted its condition. Every §6.1 row now names its condition ("with `known_detectors`", "any caller"), and the table gains rows for the new refusals.

Falsify by showing that a generator yielding an invalid `HostHit`, or raising `SystemExit` mid-iteration, escapes the wrapped region as specified. The prototype mirrors §4.4 item 4 (`proto3.py` in the session scratchpad):

```text
$ python proto3.py
...
gen_bad -> wrapped ValidationError
gen_exit -> wrapped SystemExit
$ grep -n "hits = list(raw)\|except (Exception, SystemExit)" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
301:       hits = list(raw)
302:   except (Exception, SystemExit) as exc:  # fail-loud.bare-except-ok: <reason>
```

The import handler (§4.4 item 3) uses the same `except (Exception, SystemExit)` form. §4.7 adds the four cases to `test_host_detectors.py`: a generator that raises mid-iteration, a generator yielding an invalid `HostHit`, `sys.exit(0)` from a callable, and `sys.exit(0)` at import.

### C30 (mandate, load-bearing): "no active ast/guard row can load (with known_detectors) yet never be executed"

**Resolution: revised.** Each of the three counterexamples is now refused at load:
1. A `fail_loud_ratchet` row declaring `hook`.
2. An `ast` row naming an LLM prompt id.
3. A built-in row whose `id` differs from the id its scanner stamps.

How the refusal works (Decision 3, §4.2 `_check_builtin`, §4.3):
- `KNOWN_DETECTORS` becomes a mapping from each built-in `ast`/`guard` id to a `BuiltinDetector(mandate_id, call_sites)` contract. Each `mandate_id` is the constant the scanner itself uses. LLM prompt ids are dropped.
- `load_mandates` refuses a row whose detector is not in the map (`UnknownDetectorError`).
- It refuses a row whose `id` is not the detector's `mandate_id`, and a row declaring a Tier-1 site at which no gate runs the detector (`AcfInputError`).

Falsify by producing a shipped row the contract refuses, or a counterexample row it admits. The prototype applies the §4.2 rules with the §4.3 table to every shipped registry, then to the three counterexamples:

```text
$ python proto3.py
REFUSED SHIPPED ROWS: []
('x', 'fail_loud_ratchet', ['hook']) id site
('y', 'llm_fail_loud', ['ci']) unknown
('z', 'fail_loud_bare_except', ['ci']) id
...
$ grep -n "def _check_builtin\|reports only to mandate\|runs only at" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
235:def _check_builtin(m: Mandate, known: Mapping[str, BuiltinDetector]) -> None:
243:            f"active mandate {m.id!r}: detector {m.detector!r} reports only to mandate "
249:            f"active mandate {m.id!r}: detector {m.detector!r} runs only at "
```

The table's mandate ids come from the scanners (Appendix row "Built-in mandate ids", `git grep -n 'mandate_id="' -- plugins/arch-compliance/python/acf/detectors`, plus `emptyCatch.ts:23` and `explicitAny.ts:15`). `test_builtin_detectors.py` pins the TypeScript pair against the rule files.

### C58 (mechanism_justification, load-bearing): "TIER1_CALL_SITES plus the languages check is necessary and sufficient"

**Resolution: revised, with C30.** The sufficiency claim is withdrawn. The row-shape checks (Tier-1 site, host `ast` languages) and the per-detector contracts together prevent an active row that loads and runs nowhere. A host row is dispatched by both gates' host runners, so any Tier-1 site serves it. A built-in row is served only at the sites its contract lists. Same falsifying command and output as C30.

Falsifying command and output (as C30):

```text
$ python proto3.py
REFUSED SHIPPED ROWS: []
('x', 'fail_loud_ratchet', ['hook']) id site
('y', 'llm_fail_loud', ['ci']) unknown
('z', 'fail_loud_bare_except', ['ci']) id
...
$ grep -n "def _check_builtin\|reports only to mandate\|runs only at" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
235:def _check_builtin(m: Mandate, known: Mapping[str, BuiltinDetector]) -> None:
243:            f"active mandate {m.id!r}: detector {m.detector!r} reports only to mandate "
249:            f"active mandate {m.id!r}: detector {m.detector!r} runs only at "
```

### C59 (mechanism_justification, load-bearing): "one-root-per-process eviction is justified"

**Resolution: revised (mechanism removed).** Eviction is gone. Decision 6 and §4.4 item 3 record the first root and raise `AcfInputError` for any other root in the same process. That refuses the state instead of repairing it. Multi-root tests reset the loader through the new test-only fixture `fresh_host_loader` (§4.7, `plugins/arch-compliance/tests/conftest.py`). The module name hashes only `rel_path`, since one root is active.

Falsify by finding an eviction step left in the spec, or a production caller that serves two roots in one process:

```text
$ grep -n "evict" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
(no output; exit 1)
$ sed -n 63p plugins/arch-compliance/python/acf/cli_check_diff.py
    repo: Path = resolve_repo(args.repo)
$ sed -n 65p plugins/arch-compliance/hooks/posttooluse_gate.py
    repo = _resolve_repo(args.repo, stdin_payload)
```

Each gate resolves one `repo` in `main`, and the hook is a fresh process per edit. The two v2 advisories about `sys.path` order (a host `acf` package shadowing the plugin; eviction removing the plugin's own modules when the old root was this repository) are answered here too:
- the eviction no longer exists;
- the loader refuses a root containing `"acf/"` or `"acf.py"` (§4.4 item 3, §6.1).

### C69 (implementability, load-bearing): "no host failure escapes as a traceback"

**Resolution: revised, with C29.** `_call_host` wraps the call and the materialisation, catching `(Exception, SystemExit)`. The hook's scan `except` becomes `(AcfInputError, DetectorPackError, UnknownDetectorError)` (§4.6 item 2), matching the `acf-check-diff` tuple at `cli_check_diff.py:72`, so the new second-root and `acf`-shadow refusals are caught in both gates as well. Same falsifying command and output as C29.

Falsifying command and output (as C29):

```text
$ python proto3.py
...
gen_bad -> wrapped ValidationError
gen_exit -> wrapped SystemExit
$ grep -n "hits = list(raw)\|except (Exception, SystemExit)" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
301:       hits = list(raw)
302:   except (Exception, SystemExit) as exc:  # fail-loud.bare-except-ok: <reason>
```

### mandate claim C30 is REFUTED (duplicate line)

The same claim as the C30 entry above, listed again under its reviewer heading. Resolution and command as C30.

Falsifying command and output:

```text
$ python proto3.py
REFUSED SHIPPED ROWS: []
('x', 'fail_loud_ratchet', ['hook']) id site
('y', 'llm_fail_loud', ['ci']) unknown
('z', 'fail_loud_bare_except', ['ci']) id
...
$ grep -n "def _check_builtin\|reports only to mandate\|runs only at" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
235:def _check_builtin(m: Mandate, known: Mapping[str, BuiltinDetector]) -> None:
243:            f"active mandate {m.id!r}: detector {m.detector!r} reports only to mandate "
249:            f"active mandate {m.id!r}: detector {m.detector!r} runs only at "
```

### implementability claim C69 is REFUTED (duplicate line)

The same claim as the C69 entry above. Resolution and command as C29 and C69.

Falsifying command and output:

```text
$ python proto3.py
...
gen_bad -> wrapped ValidationError
gen_exit -> wrapped SystemExit
$ grep -n "hits = list(raw)\|except (Exception, SystemExit)" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
301:       hits = list(raw)
302:   except (Exception, SystemExit) as exc:  # fail-loud.bare-except-ok: <reason>
```

## Non-blocking findings folded in

| Finding (run detail) | Disposition in v3 |
|---|---|
| `test_engine_paths.py` already exists (3 reviewers, converged) | §4.7 marks it "(exists; extended)" and keeps its current cases. |
| Rung 1 applies to row-shape checks (absorption, two mechanisms) | Decision 4: host-reference syntax, the Tier-1 requirement and the host `ast` languages rule move to a `Mandate` `model_validator`, applying to every caller. A `model_validator` raising `AcfInputError` propagates with its type (`loader.py:54-56`, `:70-73`; precedent `registry.py:33-41`); checked by running a validator that raises it (prints `AcfInputError boom`). |
| Row activity has a separate Tier-2 definition (converged) | Decision 2 names the Tier-2 scope and `judge.py:230`; §5.2 adds the `ADJACENT` row; §6 says "Within the Tier-1 gates". |
| `PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:373-376`, `:389-393` contradict the new hook contract | §4.8 updates both; §5.1 lists them. |
| `acf-setup/SKILL.md:150` advises committing `.acf/` | §4.8: committing it opts every clone into running host detectors on edit. |
| Under-root test has three owners | §4.1 and §5.2 separate the two directions (relative string → contained `Path` vs resolved `Path` → relative string) and keep the latter where it is. |
| Parse-or-skip implemented five times | §3 non-goal under `## Scoped refactor`. |
| `test_self_host.py:40` shares the file-existence check | §4.7: it uses `resolve_under_root`; §5.2 `SUBSUMED`. |
| `test_acf_mandate_skill.py` runs the rewritten snippet | §4.7 row: the snippet keeps the shape the test extracts. |
| `cli_check_llm.py:54` gets a traceback on a malformed host reference | §3 row: the same handling it gives any malformed registry today. |
| §6.2 named the gates as `load_host_detector` callers | Corrected to the two runners. |
| HM driver lines and the lossy parse-failure advice | §3 non-goal cites `hm:scripts/ci/arch_compliance/driver.py:150-163`, states the `line >= 1` and diff-mode gaps, and drops the "declare it as a guard" advice. |
| Hook import of `KNOWN_DETECTORS` would pull in `acf.judge` | §4.3: the hook imports it from `acf.detectors`. |
| Broken host `ast` module reported only when a matching file changes | Stated at the end of §4.4. |
| Hook's `rel_paths` mixes in-repo and absolute strings | §4.6: a separate `in_repo_rel_paths` list feeds host dispatch. |

## Delta pre-flight

One fresh agent with the sweeper and refuter prompts, the v3 spec, and only the 13 claims this revision added or changed (238,071 tokens). It executed the P4 census over every YAML registry and inline test row (no row refused except `test_registry.py`'s intended `not_a_real_detector`). 11 SURVIVED, 2 REFUTED, all folded into v3 before commit:

| Pre-flight finding | Folded in as |
|---|---|
| S1 REFUTED: `README.md:66-74` hand-keeps a detector-id → mandate-id table | §4.8 adds a call-sites column; §4.7 `test_builtin_detectors.py` pins every row against `KNOWN_DETECTORS`. |
| S4 REFUTED: missed prose at `PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:266-268` and `docs/guides/SUPERPOWERS_COMPLEMENT.md:87` | Both added to §4.8. |
| `PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:84`, `:418-420` fix `KNOWN_DETECTORS` in `cli_check_diff.py` | §4.8 updates them; the stated reason (no `acf.registry` → `acf.judge` import) still holds. |
| Host `scan_ast` contract did not say empty `added_lines` means whole file | §4.4 item 2 adopts `acf.engine.is_in_scope` (`engine.py:27-31`). |
| One active row per configurable built-in is a behaviour change | Stated in Decision 3 as an accepted consequence. |
| The ratchet's walk filter is lexical, not containing | §5.2 notes it and leaves the ratchet unchanged. |

## Sentence-type sweep

Swept over the whole v3 spec, carried text included.

| # | Type | Hits and disposition |
|---|---|---|
| T1 | Population claim without a recipe | `load_mandates` callers, `KNOWN_DETECTORS` users, `apply_registry` callers, direct `Mandate` construction, active-row filters, built-in mandate ids, shipped rows, inline test registries: each has an Appendix recipe and its observed output. "Every built-in scanner stamps one fixed mandate_id" (§1 item 1) cites the `mandate_id="` recipe and the two TypeScript lines. |
| T2 | Aggregate count as a claim | `KNOWN_DETECTORS` size `13` → `9` is a precision receipt, listed as 9 Python and TypeScript ids plus 4 LLM ids. The §4.3 table is per item. No other total is used as a claim. |
| T3 | Universal quantifier | "each of the cases in §1 item 1 is refused at load" (Decision 3): backed by the §6.1 rows and the prototype. "Every printed row's id is the mandate id its detector stamps" (Appendix): backed by the shipped-rows recipe. "None is refused by `Mandate._row_shape`": backed by the direct-construction recipe with each row's detection and call sites. "for every caller that builds a row" (Decision 4): true by construction of a `model_validator`. |
| T4 | Prose-only measurement of library behaviour | `model_validator` raising `AcfInputError` propagates its type: a run is recorded above, and the existing `MandateRegistry._unique_ids` path (`registry.py:33-41`) already depends on it. `dataclasses` needing `sys.modules`: pinned by the §4.7 loader test (frozen dataclass under `from __future__ import annotations`). Generator materialisation: pinned by the §4.7 runner tests. |
| T5 | Named hook without an existence receipt | New anchors were re-read: `loader.py:54-56`, `:70-73`; `registry.py:33-41`; `cli_check_diff.py:63`, `:127`, `:128-150`, `:151-156`, `:158-166`, `:168-182`; `posttooluse_gate.py:65`, `:254`, `:255-277`, `:278-282`, `:284-294`; `judge.py:214`, `:218`, `:230`; `inject_constraints.py:28-29`; `test_hooks.py:22-29`; `test_acf_mandate_skill.py:20-25`; `emptyCatch.ts:23`; `explicitAny.ts:15`; `PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:373-376`, `:389-393`; `acf-setup/SKILL.md:150`; `hm:scripts/ci/arch_compliance/driver.py:150-163` (at `b652fab05`). |
| T6 | Doc attribution without the quoted trigger | §1 item 5 quotes the import-graph test's docstring. §1 cites `ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:102` and `:123`/`:125` by quotation. The §6 rows name the section line ranges they rely on. |
| T7 | Completeness claim backed only by a validated recipe | "no shipped row is refused by the contract" rests on an executed census (`proto3.py` over every shipped registry: `REFUSED SHIPPED ROWS: []`), not on a grep alone. |
