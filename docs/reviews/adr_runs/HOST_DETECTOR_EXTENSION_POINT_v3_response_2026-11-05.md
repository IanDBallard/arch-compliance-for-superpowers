# Response to HOST_DETECTOR_EXTENSION_POINT v3 review

- **Spec:** `docs/design/HOST_DETECTOR_EXTENSION_POINT.md` (revised to v4)
- **Reviewed commit:** `34337fed4cd62e5a8f3635e3f0a498057869ddd0`
- **Run record:** `docs/reviews/adr_runs/HOST_DETECTOR_EXTENSION_POINT_v3_2026-11-05.md`
- **Declared revision class:** mechanism (the import-and-lookup region, guard-line reading, the TypeScript bridge's mandate id, the `sys.path` position, the dropped `acf` refusal, the new prompt-id check and the contract-against-dispatch test change the design)

Every command below was run in the worktree. The branch changes only `docs/`, so code lines are as at `a338cad`. Outputs are pasted as printed. `proto4.py` is in the session scratchpad.

## Blocking reasons

### C19 (premise, load-bearing, UNPROVEN): "no shared Tier-1 dispatcher, per `## Scoped refactor`"

**Resolution: revised.** §3's non-goal no longer leans on `## Scoped refactor`. It now quotes `## Single point of definition` and places the host decision procedure in one module, `acf.detectors.host`. Each gate calls `scan_host_ast_file` and `scan_host_guards` the way it already calls each built-in scanner. The two dispatch loops exist today. The spec says they stay separate only to keep the change small, and it no longer claims any rule sanctions that. A universal sentence about doctrine ("No doctrine rule requires it or forbids it") was deleted in the sentence-type sweep.

Falsify by finding the host decision procedure implemented in either gate rather than in `acf.detectors.host`, or by finding the deferral still attributed to `## Scoped refactor`:

```text
$ sed -n 198,200p config/architecture/ARCHITECTURE.md
Lifted: "When the same operation, constant set, or decision procedure … is needed by more
than one module, it must have exactly one canonical implementation that every call site
consumes" (HistoricMansions `GEMINI.md` §7, `hm:GEMINI.md:136`). Current breaches,
$ grep -n "No shared Tier-1 dispatcher" docs/design/HOST_DETECTOR_EXTENSION_POINT.md | cut -c1-140
79:- **No shared Tier-1 dispatcher.** `## Single point of definition` asks that a *"decision procedure … needed by more than one module"* 
$ grep -c "Scoped refactor\`, \`config/architecture/ARCHITECTURE.md:211-215\`); extracting" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
0
```

### C54 (shape_fit, load-bearing): "`resolve_under_root` subsumes the string-level tests; the ratchet's `Path.is_absolute()` is a different responsibility"

**Resolution: revised.** The ratchet's `params.baseline` and `params.roots` joins do the same job as `resolve_under_root`, without containment. §5.2 now records them as `PARTIAL_OVERLAP` debt. §3 has a non-goal for them, and §4.8 adds them to the doctrine's `## Single point of definition` list of current breaches. The ratchet is otherwise untouched, so converting it is left to a follow-up.

Falsify by showing the ratchet joins are contained today, or that the spec still calls them a different responsibility:

```text
$ sed -n 122,124p plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py; sed -n 46p plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py
    baseline_file = Path(baseline_path)
    if not baseline_file.is_absolute():
        baseline_file = repo_root / baseline_file
    search_roots = [root / r for r in (roots or ["."])]
$ grep -n "PARTIAL_OVERLAP\`, recorded as debt" docs/design/HOST_DETECTOR_EXTENSION_POINT.md | cut -c1-60
439:| `looks_absolute`, `resolve_under_root` | the ratchet's
```

### C63 (shape_fit, load-bearing): "`KNOWN_DETECTORS` is the single definition of where each built-in runs"

**Resolution: revised.** The spec now says it plainly: `KNOWN_DETECTORS` *declares* where each built-in runs, and the gates' dispatch *decides* it. A new test ties the two together. For each gate, a fixture tree triggers every built-in detector, and a registry has one active row per detector whose contract includes that gate. The test asserts that the gate's findings carry exactly those mandate ids. The opposite drift (a gate that starts dispatching a detector the table excludes) cannot attach a finding to a loaded row, because `_check_builtin` refuses a row that declares that site. That drift over-refuses; it never drops a row silently. The §6 Single point of definition row says the same.

Falsify by showing that only `acf-check-diff` runs the ratchet (the asymmetry the test must observe), and that the spec's test row covers both gates:

```text
$ git grep -n "scan_ratchet" -- plugins/arch-compliance/python plugins/arch-compliance/hooks
plugins/arch-compliance/python/acf/cli_check_diff.py:13:from acf.detectors.fail_loud_ratchet import FAIL_LOUD_RATCHET_DETECTOR_ID, scan_ratchet
plugins/arch-compliance/python/acf/cli_check_diff.py:172:            scan_ratchet(
plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:115:def scan_ratchet(
$ grep -c "Contract against dispatch:" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
1
```

### C65 (shape_fit, load-bearing, UNPROVEN): "`_call_host` is the single wrapped region for invoking host callables"

**Resolution: revised.** §4.4 item 4 now calls `_call_host` the one wrapped region for *calling a host callable and consuming its result*. It says that module execution and callable lookup are wrapped separately in `load_host_detector` (item 3) and raise `UnknownDetectorError`. The fixture remains the single reset of loader state.

Falsify by finding the old unqualified wording:

```text
$ grep -n "the one wrapped region" docs/design/HOST_DETECTOR_EXTENSION_POINT.md | cut -c1-150
321:4. **`_call_host(fn, mandate, where, *args, **kwargs) -> list[HostHit]`:** the one wrapped region for calling a host callable and consuming its re
```

### C81 (implementability, load-bearing): "host-detector failures never escape as a traceback"

**Resolution: revised, two changes.**

1. **Callable lookup.** `exec_module` and `getattr(mod, attr, None)` now share one `try` in `load_host_detector`, with the code written out in §4.4 item 3. A module-level `__getattr__` that raises is wrapped as `UnknownDetectorError`.
2. **Unreadable flagged file.** `make_line_lookup` no longer reads files. It is the two gates' closures, unchanged. Lines for files a host guard flags are read by `scan_host_guards` and returned with its findings. That read happens inside each gate's scan `try`, and an `OSError` there raises `DetectorPackError`, which both gates catch. `apply_registry` does no I/O.

This also removes a side effect the v3 lazy read had: line-1 findings from the ratchet and the build-artifact guard on unread files could have become exemptable. They do not now.

Falsify by showing that `getattr` with a default swallows a raising `__getattr__` (it does not), or that `apply_registry` sits inside a `try` (it does not, so I/O had to leave it):

```text
$ python proto4.py   # part 1
1 getattr(mod, attr, None) raised: RuntimeError boom from host __getattr__
1 v4 region: wrapped as UnknownDetectorError stand-in: boom from host __getattr__
$ grep -n "apply_registry(raw_findings" plugins/arch-compliance/python/acf/cli_check_diff.py plugins/arch-compliance/hooks/posttooluse_gate.py
plugins/arch-compliance/python/acf/cli_check_diff.py:82:    findings = apply_registry(raw_findings, registry, _line_lookup)
plugins/arch-compliance/hooks/posttooluse_gate.py:125:    findings = apply_registry(raw_findings, registry, _line_lookup)
$ sed -n 69,74p plugins/arch-compliance/python/acf/cli_check_diff.py
    try:
        registry = load_mandates(mandates_path, known_detectors=KNOWN_DETECTORS)
        raw_findings, file_lines = _scan_changed(repo, mode, args.base, registry)
    except (GitError, AcfInputError, UnknownDetectorError, DetectorPackError) as exc:
        print(f"acf: {exc}", file=sys.stderr)
        return 1
$ grep -n "line=1" plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py plugins/arch-compliance/python/acf/detectors/build_artifacts.py
plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:135:                line=1,
plugins/arch-compliance/python/acf/detectors/build_artifacts.py:34:                    line=1,
```

### mandate claim C48 is REFUTED: "each built-in mandate id is defined once"

**Resolution: revised.** The TypeScript bridge now stamps `mandate_id=TS_MANDATE_IDS[item["detector"]]` instead of copying the Node value. An unknown `detector` raises `KeyError`, and a differing Node `mandate_id` raises `ValueError`. Both happen inside the existing `try` at `typescript_bridge.py:82-95`, which already re-raises them as `DetectorPackError`. The Node literal becomes a checked echo of the one Python definition. §5.2 records `TS_MANDATE_IDS` as `SUBSUMED`, and §6.2 now names `scan_typescript_file` as its caller.

Falsify by showing the bridge's current copy-through and the existing handler the new checks rely on:

```text
$ sed -n 85p plugins/arch-compliance/python/acf/detectors/typescript_bridge.py
                    mandate_id=item["mandate_id"],
$ sed -n 94,95p plugins/arch-compliance/python/acf/detectors/typescript_bridge.py
        except (KeyError, TypeError, ValueError) as exc:
            raise DetectorPackError(f"Invalid finding from TypeScript scanner: {exc}") from exc
```

### implementability claim C81 is REFUTED (duplicate line)

The same claim as the C81 entry above. Resolution as C81.

Falsifying command and output:

```text
$ python proto4.py   # part 1
1 getattr(mod, attr, None) raised: RuntimeError boom from host __getattr__
1 v4 region: wrapped as UnknownDetectorError stand-in: boom from host __getattr__
```

### mechanism 'Refuse a host root containing acf/ or acf.py' has no named producer — superstition

**Resolution: revised (deleted).** The refusal is gone. The plugin's `acf` is a regular package, imported before any dispatch (`posttooluse_gate.py:28`), so a host `acf/` cannot shadow it. The real risk, raised in the same run, is a host top-level module shadowing a module the process imports later. Decision 6 now appends the host root to `sys.path` rather than inserting it at the front, and states the cost: a host name that an earlier entry already provides resolves to that entry. §6.1 drops the refusal, and the loader test checks the append.

Falsify by showing a host `acf/` shadowing the plugin's package, or a root appended to the end shadowing a stdlib module:

```text
$ sed -n 28p plugins/arch-compliance/hooks/posttooluse_gate.py; ls plugins/arch-compliance/python/acf/__init__.py
from acf.repo import ENABLED_REL, MANDATES_REL, resolve_repo
plugins/arch-compliance/python/acf/__init__.py
$ python proto4.py   # parts 2 and 3
2 inserted at [0] -> shadowed: True
2 appended -> shadowed: False
3 acf.registry from acf/registry.py
3 host acf.hostonly not importable: No module named 'acf.hostonly'
$ grep -c 'root containing `"acf/"`' docs/design/HOST_DETECTOR_EXTENSION_POINT.md
0
```

## Non-blocking findings folded in

| Finding (reviewer, severity) | Disposition |
|---|---|
| `LLM_PROMPT_IDS` loses its only runtime consumer; the acf-mandate skill's prompt-id rule is unenforced (compliance, important) | Folded. `load_mandates` gains `llm_prompt_ids`, and `acf-check-diff` passes `LLM_PROMPT_IDS` (Decision 4, §4.2, §4.6). The skill snippet passes it too. Census: every shipped active `llm` row names a known prompt id (Appendix). |
| `make_line_lookup` makes line-1 ratchet and build-artifact findings exemptable (refuter, important) | Folded with C81: the lookup reads no file; only host-guard-flagged files are read (§4.5). |
| `make_line_lookup` OSError outside the gates' `try` (refuter, hardening; converged) | Folded with C81. |
| Host root at `sys.path[0]` shadows later imports (refuter; converged with the `acf` refusal finding) | Folded: the root is appended (Decision 6). |
| Two owners of "detector runs at gate" (sweeper, important) | Folded with C63. |
| Ratchet path joins duplicate `resolve_under_root` (sweeper, advisory) | Folded with C54, as recorded debt. |
| `_to_findings` severity is a third owner (sweeper, advisory) | Folded: §4.4 item 5 and §5.2 name `apply_registry` the owner. |
| §4.8 misses acf-mandate `SKILL.md:18` and the `tests/test_self_host.py:5` docstring (sweeper, advisory) | Folded into §4.8 and §4.7. |
| `except (Exception, ...)` tuples are not flagged by `fail-loud.bare-except`, so the token is decorative (hardening, compliance) | Folded: §6 says so; the token stays to mark breadth. |
| `ast` path check at rung 3 with no justification (hardening, advisory) | Folded: §4.4 item 5 gives the reason. |
| `in_repo_rel_paths` parallel list; `detector` field's two meanings; path-less `ast` hit type (hardening, advisory) | Not changed. The parallel list keeps the build-artifact guard's input unchanged. The `:` syntax is Decision 1. The hit type is answered in §4.4 item 5. |
| `scan_host_ast_file` silent skip on `SyntaxError` (compliance, advisory) | Not changed; disclosed as the built-in convention (§3, §4.4 item 6). |
| Convention claim C71 ("each caller already handles `AcfInputError`") (hardening, not load-bearing) | The claim was the controller's wording. §3 already says `cli_check_llm.py` surfaces it uncaught; no spec change. |

## Design-simplification pass

Elements removed: the `acf` refusal, and the file read and `repo_root` parameter in `make_line_lookup`. Elements added: the `llm_prompt_ids` parameter and check, the guard-line return from `scan_host_guards`, and the contract-against-dispatch test. A shared dispatcher and a map-driven dispatch were considered and left out (§3, §4.7).

## Delta pre-flight

One fresh agent with the sweeper and refuter prompts reviewed the 13 claims this revision added or changed, against the uncommitted v4 text. It is a rehearsal and writes no ledger row.

| Claim | Verdict | Fix folded into v4 |
|---|---|---|
| P1 `exec_module` and `getattr` share one wrapped region | SURVIVED | — |
| P2 No host failure reaches a traceback through the exemption path | UNPROVEN | `Path.resolve()` raises `RuntimeError` on a symlink loop on Python 3.11/3.12 (`pyproject.toml:5`: `requires-python = ">=3.11"`). `resolve_under_root` now maps that to `None` (§4.1), with a test (§4.7). |
| P3 Line-1 built-in findings on unread files stay non-exemptable | SURVIVED | — |
| P4 TypeScript bridge stamps from `TS_MANDATE_IDS` inside the existing `try` | SURVIVED | — |
| P5 Appending the root prevents shadowing; a host `acf/` cannot shadow the plugin | REFUTED | `python -m acf.cli_check_diff` run from the host root (`.github/workflows/ci.yml:40`) already puts the host root first. Decision 6 now has a per-entry-point table, and says the `-m` exposure predates this design. It also states that host modules cannot use relative imports. |
| P7 Only host-guard findings gain lines | REFUTED | Built-in findings on a guard-flagged file become exemptable, as built-in findings on changed code files already are. §4.5 now states that exemption follows the file. |
| S1 The host decision procedure has one implementation | REFUTED | The guard-line merge rule was written in both gates. It moved into `scan_host_guards`, which now takes the gate's `file_lines` (§4.4 item 7, §4.6). |
| S2 `TS_MANDATE_IDS` is the single Python definition | SURVIVED | — |
| S3 Contract-against-dispatch test ties table to dispatch | SURVIVED | — |
| S4 Ratchet debt recorded consistently | REFUTED | §4.1 had called `fail_loud_ratchet.py:123` a legitimate I/O check; it now names it as the §3 debt. |
| S5 Prose sweep covers stale sites | REFUTED | Added `tests/test_acf_mandate_skill.py:2` docstring (§4.7), `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:425`, `:500` and the `enforcement.py:6-8` docstring (§4.8). |
| S6 `apply_registry` owns severity | SURVIVED | — |

Advisory, also folded: Decision 2 now states that `ci` and `precommit`, and `hook` and `posttooluse`, are not told apart.

```text
$ sed -n 5p pyproject.toml
requires-python = ">=3.11"
$ sed -n 40p .github/workflows/ci.yml
        run: python -m acf.cli_check_diff --repo . --base "origin/${{ github.base_ref || 'main' }}"
$ sed -n 2p plugins/arch-compliance/tests/test_acf_mandate_skill.py
stock profile: it loads the registry with the package's detector union and refuses
```

## Sentence-type sweep

Swept the whole revised spec. Hits in changed text and their disposition:

| # | Type | Hit | Disposition |
|---|---|---|---|
| T1 | Population without recipe | "every shipped active `llm` row names a known prompt id" | Converted: Appendix row with the recipe and per-row output. |
| T2 | Aggregate as claim | None added. | — |
| T3 | Universal quantifier | "No doctrine rule requires it or forbids it" (§3) | Deleted. |
| T3 | Universal quantifier | "a host top-level module cannot shadow a standard-library, third-party or plugin module that the process imports later" (Decision 6) | Converted after the pre-flight: replaced by a per-entry-point table, which says the claim holds for the hook and the console script and not for `python -m` from the host root. The loader test pins the append; `proto4.py` part 2 shows the difference. |
| T3 | Universal quantifier | "`apply_registry` does no I/O and raises nothing new" (§4.5) | Stands: `make_line_lookup` is the unchanged closure body, shown in the §4.5 code; `apply_registry`'s other change is the `call_sites` filter. |
| T3 | Universal quantifier | "never silently drops" (§4.7 contract test) | Stands with its reason in the same sentence (`_check_builtin` refuses a row declaring that site). |
| T4 | Prose-only tool behaviour | `getattr` with a default does not swallow a raising `__getattr__`; `sys.path` append vs insert | Pinned by `test_host_detectors.py` cases (§4.7); prototype output above. |
| T5 | Named construct without receipt | `typescript_bridge.py:82-95` `try` and `:94-95` handler | Receipt above. |
| T6 | Doctrine attribution without quote | `## Single point of definition` (§3) | Quoted adjacent. acf-mandate `SKILL.md:56` quoted in Decision 4. |
| T7 | Completeness by recipe only | Ratchet joins as the only uncontained registry-path join | Not claimed: the spec records the ratchet as one breach and does not say it is the only one. |

Carried text was swept with the same patterns; the carried hits were dispositioned in the v1 and v2 response records and are unchanged.
