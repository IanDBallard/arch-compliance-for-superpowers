# Response to HOST_DETECTOR_LOCAL_APPROVAL v3 gate run

- **Spec:** `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md`
- **Reviewed commit:** `0eb992a` (run detail `HOST_DETECTOR_LOCAL_APPROVAL_v3_2026-11-11.md`, recorded at `532c34f`)
- **Revised at:** `86c3c36` (v4)
- **Declared revision class:** precision-only. No contract, schema, state, exception or sequencing change; the revision replaces a recipe with an executed census, re-flags one external claim as not load-bearing, adds a prose-table row for an already-changed file, and corrects one line citation. Cleared by controller verification pass with the user's approval ("Precision v4 + pass", 2026-11-11), minted in the spec header. A verification pass writes no ledger row.

## Blocking reasons

### S6 (sweep, REFUTED) — carried unchanged (claim-extraction error)

The refuted statement was the controller's claim summary, not spec text: it listed the runtime files the change touches and left out `plugins/arch-compliance/python/acf/detectors/__init__.py` and `plugins/arch-compliance/python/acf/loader.py`. The spec's §5 table already lists both, as the reviewer noted. No spec edit.

```
$ grep -n "^| \`plugins/arch-compliance/python/acf/\(detectors/__init__\|loader\).py\`" docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md
198:| `plugins/arch-compliance/python/acf/detectors/__init__.py` | `load_gate_registry` (§4.3) |
200:| `plugins/arch-compliance/python/acf/loader.py` | typed decode and parse failures (§4.7) |
```

### S12 (sweep, REFUTED) and M7 (mandate, REFUTED) — recipe replaced by an executed census

§7's risk row now cites `docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/params_census.py`, which loads every tracked YAML registry and applies the proposed `_json_params` check to each row's `params`, after a control block that must refuse a set, a date, a binary value, an integer key, a `yes:` key, `.nan` and `.inf` (exit 2 otherwise). It lists test-built registries as `NOT-STATIC` and leaves them to the full test run. The known sites the reviewer read (`mandates.yml` `:37`, `:96`, `:112`, `:128`; `test_hooks.py:385-387`; `test_builtin_detectors.py:132-133`) all appear in its output.

```
$ python docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/params_census.py
control NOT-JSON  k: !!set {a: null}
control NOT-JSON  k: 2026-11-11
control NOT-JSON  k: !!binary aGk=
control NOT-JSON  k: {1: a}
control NOT-JSON  k: {yes: a}
control NOT-JSON  k: .nan
control NOT-JSON  k: .inf
ok               config/architecture/mandates.yml  ops.no-build-artifacts
ok               config/architecture/mandates.yml  fail-loud.ratchet
ok               config/architecture/mandates.yml  facade.forbid-sink
ok               config/architecture/mandates.yml  fsm.transition-guard
ok               plugins/arch-compliance/profiles/python-service/mandates.yml  ops.no-build-artifacts
ok               plugins/arch-compliance/profiles/python-service/mandates.yml  fail-loud.ratchet
ok               plugins/arch-compliance/profiles/python-service/mandates.yml  facade.forbid-sink
ok               plugins/arch-compliance/profiles/python-service/mandates.yml  fsm.transition-guard
ok               plugins/arch-compliance/profiles/react-app/mandates.yml  ops.no-build-artifacts
NOT-STATIC       plugins/arch-compliance/tests/test_builtin_detectors.py:132  -
NOT-STATIC       plugins/arch-compliance/tests/test_hooks.py:375  -
NOT-STATIC       plugins/arch-compliance/tests/test_hooks.py:381  -
checked 12 params values; NOT-JSON: 0
```

### H10 (implementability, UNPROVEN) — re-flagged external, not load-bearing

§4.5 step 4 now marks the `systemMessage` display claim *(external, not load-bearing)* and states the fallback: the agent receives the notice through `additionalContext`, which the hook already emits (`posttooluse_gate.py:137-147`). No proof from external data is attempted.

```
$ grep -c "external, not load-bearing" docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md
1
```

## Absorbed non-blocking findings (precision)

- Doctrine opening paragraph (`config/architecture/ARCHITECTURE.md:9-12`) added to the §4.8 table.
- `sys.modules` reuse citation corrected from `host.py:80-81` to `host.py:74-77`.

## Carried to the implementation plan (stricter choices within the spec, no spec change)

- The hook loads its registry through `load_gate_registry` like the diff gate and `acf-allow`.
- The runners' `digests` parameter becomes a required keyword.
- `acf-mandate/SKILL.md:96`'s validation snippet calls `load_gate_registry` instead of re-spelling it.
- Setup prose uses the `acf-check-diff` console script rather than `python -m acf.cli_check_diff` (current-directory import shadowing).
- Wording and citation nits from the v3 detail's absorptions.

## Sentence-type sweep

| # | Hits in the revised spec | Disposition |
| --- | --- | --- |
| T1 | §7 params row; §6.1 census; §3 SubagentStart recipe | Census or recipe cited beside each. |
| T2 | §7 params row lists per-file row counts | Each count is read off the committed census output line by line, not offered as the claim. |
| T3 | Decision 4 "no `.pyc` … is read for the detector file" | Backed by `pyc_probe.py` and the §6.2 test. |
| T4 | `pyc_probe.out` | Pinned by the §6.2 `test_host_detectors.py` test. |
| T5 | `_SourceOnlyLoader`, `get_code`, `get_data` | Stdlib `SourceFileLoader` methods; probe exercises them. |
| T6 | Mandate attributions in header and §2 | Clause quoted beside each. |
| T7 | §6.1 population, §7 params population | Executed censuses with committed outputs. |
