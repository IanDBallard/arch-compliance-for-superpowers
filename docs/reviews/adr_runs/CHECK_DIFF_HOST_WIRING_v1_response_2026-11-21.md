# Response to the v1 review of `docs/design/CHECK_DIFF_HOST_WIRING.md`

- Spec: `docs/design/CHECK_DIFF_HOST_WIRING.md`
- Reviewed commit: `9f4eec4c61fe8617fdccc0281673db012b4d98be`
- Run record: `CHECK_DIFF_HOST_WIRING_v1_2026-11-21.md` (BLOCKED)
- Declared revision class: **mechanism**. The revision adds an action step (the self-check on the plugin's files), adds the trigger rule for hosts with whole-tree rows, moves the plugin's own gate step onto the action, and changes the reason for `host-setup`. It re-runs in full.

## Blocking reasons

### C7 (premise, UNPROVEN): the runner hands the action a copy of its repository at the ref

The premise is GitHub platform behaviour, and no file in this repository records it. The revision does not try to prove it. It stops depending on it silently: §4.1 step 1 makes the action stop, naming both paths, unless `pyproject.toml` and `plugins/arch-compliance/detectors/typescript/package.json` sit three levels above `$GITHUB_ACTION_PATH`. §2 decision 2 says so. If the premise is false, the design is unchanged and fails loudly at the first adopter's run (§8, §9). The re-extracted claim is therefore flagged not load-bearing.

Falsifier: the two files step 1 checks exist at the repository root, which is three levels above `.github/actions/check-diff/`:

```
$ ls pyproject.toml plugins/arch-compliance/detectors/typescript/package.json
plugins/arch-compliance/detectors/typescript/package.json  289B
pyproject.toml  1.4K
```

### C10 (premise, UNPROVEN): fork pull requests get a read-only token and no secrets

**Withdrawn.** The GitHub policy claim is gone from the spec. §2 decision 4 keeps only the half the review confirmed: today's CI sketch already passes `--trusted-checkout`, so the action adds no exposure, and a host that does not want it sets `trusted-checkout: false`.

Falsifier: the current sketch's flag.

```
$ grep -n "trusted-checkout" plugins/arch-compliance/skills/acf-setup/SKILL.md | sed -n 3p
245:  run: acf-check-diff --base "origin/${{ github.base_ref || 'main' }}" --repo . --call-site ci --trusted-checkout
```

### C13 (premise, UNPROVEN): setup-python and setup-node take over PATH, so host setup must follow the action's setup

**Replaced.** The reason now rests on in-tree code (new §2 decision 8). The gate imports a host detector module into its own process, so the module's third-party Python packages must be installed in the action's virtual environment, which a host cannot reach from a step before the action. The PATH-persistence premise is gone. The spec now says plainly that Node dependencies installed earlier stay on disk, and `host-setup` is documented as the one place for both kinds. The "job of its own" sentence no longer asserts anything about GitHub; it says the snippet isolates the action so that nothing else depends on its versions.

Falsifier: in-process import.

```
$ sed -n 102,109p plugins/arch-compliance/python/acf/detectors/host.py
            spec = importlib.util.spec_from_file_location(
                name, module_path, loader=_SourceOnlyLoader(name, str(module_path), expected_sha256)
            )
            if spec is None or spec.loader is None:
                raise ImportError(f"no loader for {rel_path!r}")
            mod = importlib.util.module_from_spec(spec)
            sys.modules[name] = mod
            spec.loader.exec_module(mod)
```

### C18 (mandate, REFUTED; listed twice): the fixture script's CI job is its live consumer

**Revised (precision).** The fixture builder moves from `scripts/` to `tests/action_fixture_host.py`, and the spec calls it test scaffolding, which no package code, hook or skill calls. `## Live consumers` governs exports, so it does not apply to the builder. The action's live consumer is the `/acf-setup` skill, which prints it. The revision also folds in the unstated `## One owner for host paths`: the builder takes `MANDATES_REL` and `ARCH_REL` from `acf.repo`.

Falsifier: the rule's text.

```
$ sed -n 245,246p config/architecture/ARCHITECTURE.md
An export has a live call site in the package, a hook or a skill. A test is not a
consumer: a function only tests call is dead code with a test attached. Source: reviewer
```

### C32 (implementability, REFUTED; listed twice): the fixture row loads

**Revised (precision).** §4.2 now prints the row in full, with `title` and `exemption_tokens: []` added.

Falsifier: the required fields.

```
$ sed -n 52,58p plugins/arch-compliance/python/acf/registry.py
    title: str
    severity: Literal["BLOCK", "WARN"]
    detection: Detection
    detector: str
    languages: Language
    call_sites: list[CallSite]
    exemption_tokens: list[str]
```

## Other findings folded in

| Finding (source lens) | Resolution |
| --- | --- |
| Whole-tree rows still run on an empty diff, so pull-request-only loses them (refuter) | §2 decision 3: `/acf-setup` adds a `push` trigger when an active `fail_loud_ratchet` or host guard row is declared at `ci` |
| The `repo` input says workspace-relative, but the test uses `$RUNNER_TEMP` (refuter, hardening; converged) | §4.1: absolute or workspace-relative |
| The test asserts only the outcome, and a refusal also exits 1 (hardening) | §4.2: the planted run's output must contain `BLOCK fail-loud.empty-catch` |
| The pre-push gaps were understated: hidden violations, deleted files, the wrong branch (refuter, compliance) | §4.3 states both gaps |
| The base ref has a second owner (sweeper, compliance; converged) | §4.2: the action's third run replaces `ci.yml:39-40` |
| Unstated `## Single point of definition` and `## One owner for host paths` (compliance) | Added to the governing mandates; §4.4 and §5 record the three install copies |
| Stale `SKILL.md:258` and `:285`; README note; Dependabot (sweeper) | §4.3 change surface |
| `set -e` dependence; pre-commit framework install (hardening) | `|| exit 1` in the snippet; framework fields and `--hook-type pre-push` |
| The pre-push step refuses every push when no row declares `precommit` (refuter) | §4.3: `/acf-setup` checks, using package APIs |
| `actions/checkout@v4` (refuter) | `@v7` |
| The Windows reason was understated (refuter) | §3 names the encoding gap |
| The stronger reason for the composite form was unstated (hardening) | §2 decision 1, reworded |

## Evidence-availability check (before the pre-flight)

Each load-bearing claim of the revision was checked for evidence a reviewer can resolve in the tracked tree or the mapped sibling checkout.

| Claim | In-tree evidence | Disposition |
| --- | --- | --- |
| Pytest does not collect `tests/action_fixture_host.py` | executed (below) | kept |
| `|| exit 1` ends a hook without `set -e`; the absent-tool branch continues | executed (below) | kept |
| Platform hooks: composite `uses:`, `continue-on-error` with `steps.<id>.outcome`, `default_branch`, `tee` with `pipefail` | partial: `pipefail` at `cy:.github/workflows/ci.yml:580-587`, the `base_ref` fallback at `ci.yml:40` | kept as platform behaviour that the `action` job exercises before any tag |
| The runner hands the action a copy of its repository at the ref | none possible | made non-load-bearing by the step 1 self-check |
| Fork token policy | none possible | withdrawn |
| setup-python/node PATH persistence | none possible | withdrawn; the reason now rests on `host.py:102-109` |
| Pre-commit framework `--hook-type pre-push` | none possible | flagged not load-bearing (host placement prose) |

```
$ cd <scratch>/pyc && python -m pytest --collect-only -q      # tests/action_fixture_host.py beside tests/test_real.py, testpaths=["tests"]
tests/test_real.py::test_b
1 test collected in 0.48s

$ sh -c 'f(){ return 1; }; if true; then f || exit 1; fi; echo REACHED'; echo "exit $?"
exit 1
$ sh -c 'set -e; if false; then :; else echo skip-branch >&2; fi; echo REACHED'; echo "exit $?"
skip-branch
REACHED
exit 0
```

## Pre-flight (rehearsal, not the gate)

The pre-flight is one agent carrying the prompts of every lens among the 26 claims this revision added or changed. That was all four lenses (families: premise 9, implementability 7, mechanism_justification 4, mandate 3, shape_fit 2, sweep 1). It reviewed the uncommitted v2 text, wrote no ledger row, and cost 180,537 tokens.

| Claims | Lenses | SURVIVED | UNPROVEN | REFUTED | Load-bearing UNPROVEN/REFUTED |
| --- | --- | --- | --- | --- | --- |
| 26 | refuter, compliance, sweeper, hardening | 21 | 3 | 2 | 2 (C36 importability; C38 shallow-clone sub-claim) |

| Pre-flight finding | Folded in as |
| --- | --- |
| The fixture builder cannot import `acf` in the `action` job (important; load-bearing UNPROVEN) | §4.2: run it with `PYTHONPATH=plugins/arch-compliance/python`; `acf.repo` is stdlib-only (`repo.py:1-7`) |
| The `action` job's `fetch-depth: 0` was unstated | §4.2 states it |
| The shallow-clone hook's failure would not turn CI red (load-bearing REFUTED, narrow) | Claim re-extracted: the hook only degrades a message, and `GitError` stays authoritative (§4.1 step 7 already says so) |
| The sweep missed README `:53-58` and COMPLEMENT `:78-83` (not load-bearing REFUTED) | §4.3 change surface |
| `|| exit 1` "wherever" overclaims inside a subshell or function | §4.3: place it at the hook's top level |
| No check that `ci` selects an active row before the workflow is printed | §4.3: `/acf-setup` checks `ci` too |
| A multi-line `if` in `entry: sh -c` needs `;` | §4.3 says so |
| Three installs per `action` job | accepted and stated in §4.2 |

## Sentence-type sweep

The whole v2 spec was swept with `grep -n -o -i -E '\b(every|all|only|none|no other|nothing|each|always|never|any)\b[^.|]{0,50}'`, plus a read for counts and attributions.

| # | Type | Hit | Disposition |
| --- | --- | --- | --- |
| T3 | Universal | "every per-file check sees nothing" (§2.3) | Backed: the per-file loops iterate `changed` (`cli_check_diff.py:142-210`), and the two exceptions are named with lines |
| T3 | Universal | "only `ast` and `guard` rows" (§3) | Backed by `cli_check_diff.py:94-96` |
| T3 | Universal | "every field `Mandate` requires" (§4.2) | Backed by `registry.py:50-61`, row printed in full |
| T3 | Universal | "only improves the message" (§4.1 step 7) | Design statement; the authoritative refusal is cited (`diff.py:33-39`) |
| T3 | Universal | "nothing else in a host's CI depends on" | Design statement about the snippet's own job, not a tree claim |
| T1 | Population | "no package code, hook or skill calls it" (§4.2) | The file is new; a statement of design |
| T5 | Named hook | `load_gate_registry`, `active`, `host_rows` | Receipt `registry.py:130-147`; `detectors/__init__.py:59` |
| T6 | Attribution | trust boundary, One owner, Live consumers | Quoted adjacent (`ARCHITECTURE.md:178-181`, `:120-122`, `:245`) |
| T2 | Count | "three installs", "three times" | Per-item table in §5; the three runs listed in §4.2 |
| T4 | Tool behaviour | pytest collection, `|| exit 1` | Executed above; the remaining GitHub hooks are exercised by the `action` job before any tag |
| T7 | Completeness by recipe | change-surface list (§4.3) | Re-swept by behaviour by the pre-flight; its two additions folded in |
