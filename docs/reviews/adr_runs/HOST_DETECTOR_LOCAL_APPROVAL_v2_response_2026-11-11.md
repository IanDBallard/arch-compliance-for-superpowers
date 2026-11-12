# Response — HOST_DETECTOR_LOCAL_APPROVAL v2

- **Spec:** `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md` (revised to v3)
- **Reviewed commit:** `0af637490db28a6abbae86a2366857e87b404afb`
- **Run record:** `docs/reviews/adr_runs/HOST_DETECTOR_LOCAL_APPROVAL_v2_2026-11-11.md`
- **Declared revision class:** mechanism. Detector loading now verifies the approved digest (closing the check-to-load gap); row `params` are refused unless JSON-native (replacing fingerprint canonicalisation); the shared loader types decode and parse failures; `Mandate.is_host_row` and `load_gate_registry` become single owners. Full re-run required.

## Blocking reasons

### C12 — UNPROVEN (check-to-load residual justified by existing capability)

**Resolution:** mechanism change; the residual is removed rather than justified. Decision 4 and §4.4: `_SourceOnlyLoader.get_code` reads the detector file once, refuses bytes whose SHA-256 differs from the approved digest (`expected_sha256`), and compiles those same bytes. The hook and the diff gate pass the digests they approved through the runners. The §3 bullet that accepted the gap is deleted. §6.2 adds a test that a changed file is refused and its code does not run.

```
$ grep -c "expected_sha256" docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md
2
$ grep -c "Between the check and the load" docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md
0
```

### S4 — REFUTED (census matched helper names; f-string detector and fixtures missed)

**Resolution:** the census script now matches a host detector string by shape (`\.py:[A-Za-z_{]`, which covers the f-string `hostdet/rules.py:{fn}` at `test_hooks.py:379`) and follows module-level fixtures taken as parameters as well as called helpers. §6.1 adds a second method, `git grep -n "\.py:[A-Za-z_{]" -- plugins/arch-compliance/tests tests`, and states why its other hits are not gate tests. The "re-run before editing" instruction is replaced by the safety net that makes a missed test loud: an unapproved hook run makes no host call (host assertions fail) and an unapproved diff-gate run exits 1.

```
$ python docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/host_row_gate_tests.py
plugins/arch-compliance/tests/test_diff_cli.py:350 test_host_ast_and_guard_rows_run_at_ci_and_block
plugins/arch-compliance/tests/test_diff_cli.py:367 test_host_guard_exemption_token_on_a_non_code_file_is_honoured
plugins/arch-compliance/tests/test_diff_cli.py:379 test_host_guard_only_row_at_precommit_passes_selection_and_reports
plugins/arch-compliance/tests/test_hooks.py:406 test_gate_disabled_does_not_import_a_host_module
plugins/arch-compliance/tests/test_hooks.py:440 test_gate_runs_hook_host_rows_and_not_ci_only_host_guards
plugins/arch-compliance/tests/test_hooks.py:464 test_gate_edited_file_outside_repo_yields_no_finding_and_no_host_call
plugins/arch-compliance/tests/test_hooks.py:488 test_gate_native_absolute_path_is_reported_under_its_posix_key
$ git grep -n "\.py:[A-Za-z_{]" -- plugins/arch-compliance/tests tests | cut -d: -f1 | sort | uniq -c
      2 plugins/arch-compliance/tests/test_diff_cli.py
      1 plugins/arch-compliance/tests/test_hooks.py
     22 plugins/arch-compliance/tests/test_host_detectors.py
      3 plugins/arch-compliance/tests/test_registry.py
$ grep -n "posttooluse_gate\|cli_check_diff\|GATE\b\|import main\|subprocess" plugins/arch-compliance/tests/test_registry.py plugins/arch-compliance/tests/test_host_detectors.py
(no output)
```

### H5 — SURVIVED, scored UNPROVEN (evidence restated the spec's citation)

**Resolution:** carried, with an in-tree pin added. The reviewer's own experiment confirmed the claim. The spec now cites the committed probe `docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/pyc_probe.py` and its output, and §6.2 turns it into a test.

```
$ python -I docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/pyc_probe.py
default loader runs: pyc
source-only loader runs: source
```

### H9 — SURVIVED, scored UNPROVEN (evidence restated the spec's citation)

**Resolution:** carried unchanged. The reviewer's reasoning confirms `RepoTree.contained` and `Path.home()` behave as stated; the spec's citation (`repo.py:53-59`) is the defining code, so a reviewer resolving it independently lands on the same lines. §6.2's `STORE_IN_REPO` test and §6's `HOME`/`USERPROFILE` test setup pin both behaviours.

```
$ sed -n 53,59p plugins/arch-compliance/python/acf/repo.py | head -2
    def contained(self, path: str) -> Path | None:
        """``path`` resolved against the root (an absolute ``path`` is taken as is); None when it leaves the root or cannot be resolved."""
```

### H13 — SURVIVED, scored UNPROVEN (evidence restated the spec's citation)

**Resolution:** carried, with the same committed probe as H5 (`pyc_probe.py`, output above) and the §6.2 tests (source over `.pyc`; digest mismatch refused).

### H14 — SURVIVED, scored UNPROVEN (evidence restated the spec's citation)

**Resolution:** carried unchanged; the cited `try`/`except` (`cli_check_diff.py:83-100`) is the defining code. §6.4's "no approval, no flag: exit 1, stderr names acf-allow" test pins it.

```
$ sed -n 98,100p plugins/arch-compliance/python/acf/cli_check_diff.py
    except (GitError, AcfInputError, UnknownDetectorError, DetectorPackError) as exc:
        print(f"acf: {exc}", file=sys.stderr)
        return 1
```

### H16 — REFUTED (load_model_file does not type every bad-file failure) — both lines of the run detail

**Resolution:** mechanism change in the shared loader, as the finding recommended (one owner). Decision 9 and §4.7: `load_model_file` also maps `UnicodeDecodeError` at the read and `ValueError`/`RecursionError` at the parse to `AcfInputError`; `test_loader.py` gains one case each.

```
$ grep -c "UnicodeDecodeError" docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md
3
$ sed -n 59,66p plugins/arch-compliance/python/acf/loader.py
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise AcfInputError(f"cannot read {subject} {path.as_posix()}: {exc}") from exc
    try:
        raw: Any = yaml.safe_load(text) if fmt == "yaml" else json.loads(text)
    except (yaml.YAMLError, json.JSONDecodeError) as exc:
        raise AcfInputError(f"invalid {fmt} in {path.as_posix()}: {exc}") from exc
```

### H10 — UNPROVEN (external `systemMessage`; not load-bearing)

**Resolution:** carried unchanged; external, marked *(external)* in §4.5, not load-bearing (the agent still receives the notice through `additionalContext`).

## Other findings absorbed

| Finding | Absorption |
| --- | --- |
| `approval_state` fingerprint operand bound to `host_rows(call_sites)` (converged) | §4.2 `check_approval`: rows are always `approval_rows(registry)` (TIER1); `call_sites` only decides `NOT_NEEDED`. §6.2 test with a `[ci]`-only host row. |
| `_canonical` merges a date and the equal string (converged); canonicalisation at rung 2 where rung 1 applies | Decision 5 and §4.1: `load_mandates` refuses non-JSON `params` (`_json_params`); `_canonical` is deleted (`grep -c "_canonical"` prints 0). |
| Check-to-load gap (converged) | C12 above. |
| Predicate `detection in {ast, guard} and is_host_detector_ref` has two owners | §4.1 `Mandate.is_host_row`, consumed by `_row_shape`, `load_mandates` and `host_rows`. |
| Registry load with gate arguments repeated in three places | §4.3 `load_gate_registry` in `acf.detectors`, used by `acf-allow` and the diff gate; the hook keeps its prompt-id-free call. |
| `Path.home()` `RuntimeError` | Decision 2 and §4.2 `store_path`: raised as `AcfInputError`; §6.2 test. |
| "removes the one route" completeness claim | Reworded; §3 states that the store follows the process environment. |
| `--trusted-checkout` trusts the command-line writer | §3 bullet: a committed pre-commit config is the repository's own command, consented to by `pre-commit install`. |
| ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:161 and acf-setup pre-commit snippet missed | Supersedes header covers `:161`; §4.8 adds the acf-setup `:164`, `:182-196` row; §7 adds the pre-commit risk. |
| `approval_rows` consumer unnamed (Live consumers) | §4.2 names `check_approval` and `acf-allow`. |
| Notice on edits that make no host call | §7 risk row. |
| Home-rooted repository shares `~/.acf/` with the store | §3 bullet. |

## Sentence-type sweep

Whole v3 spec re-swept with the quantifier/count scan used for v2.

| Type | Hits and disposition |
| --- | --- |
| T1 population without recipe | §6.1 → two methods (AST census, `git grep` recipe) with outputs; §5 → recipe; SubagentStart → recipe plus import lines; §7 params-type claim → `git grep` recipe. |
| T2 aggregate as claim | §1.2 four returns → per-line table. |
| T3 universal quantifier | "every bad-file failure" (Decision 9) → the three added exception types are named and each gets a test; "every active host row" (§4.2) → defined as `approval_rows(registry)`; "The removed claim 'removes the one route'" deleted. Normative "every"/"each" in decisions and tests are requirements. |
| T4 tool/library behaviour | `.pyc` substitution → committed probe plus §6.2 test; JSON round-trip refusal → §6.2 `test_registry.py` cases; loader exceptions → §6.2 `test_loader.py` cases; Claude Code behaviour → *(external)*. |
| T5 named hook without receipt | `SourceFileLoader.get_code` → `pyc_probe.out`; `load_model_file` → `loader.py:43-77`; `_row_shape` → `registry.py:69-76`; load loop → `registry.py:144-154`; handler → `host.py:85-93`; `LLM_PROMPT_IDS` → `acf/judge.py:29`; `KNOWN_DETECTORS` → `acf/detectors/__init__.py`. |
| T6 attribution without quote | Unchanged from v2 (quotes kept); Supersedes header now also quotes `ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:161`. |
| T7 completeness backed by known-site recipe | §6.1 → executed census plus independent grep, outputs committed, and a loud-failure safety net for misses. |

## Delta pre-flight (rehearsal, not the gate)

One rehearsal agent (hardening and sweeper stances) adjudicated ten v3 claims: eight survived, one was unproven (the census "together identify" wording) and one refuted as a universal (missed tests "cannot pass silently"). Absorbed before requesting the gate:

| Finding | Absorption |
| --- | --- |
| "Cannot pass silently" is a universal | §6.1 now states, per listed test, how it fails if unseeded, and that §6.3/§6.4 unapproved-run tests assert the notice or refusal text. |
| The grep cross-check finds builders, not tests | §6.1 says so and names the spellings outside both methods. |
| Top-level integer `params` key is refused by pydantic before `_json_params` | §4.1 and §6.2 say so; the test case is a nested integer key. |
| `RecursionError` from `json.dumps` | Named in §4.1's round-trip clause. |
| `acf-allow` cannot approve a `--mandates` registry | §3 bullet and the refusal text: such runs pass `--trusted-checkout`. |
| Hook loads without prompt-id validation | §3 bullet: `acf-allow` then reports the prompt-id error naming the row. |
| Digest check only at first load per process | §4.4 says so. |
| One approval per worktree | §3 bullet. |
