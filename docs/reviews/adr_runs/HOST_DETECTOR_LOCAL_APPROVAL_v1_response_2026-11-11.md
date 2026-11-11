# Response — HOST_DETECTOR_LOCAL_APPROVAL v1

- **Spec:** `docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md` (revised to v2)
- **Reviewed commit:** `d7c6512beb31672b417e2117f074ed60bc03ba5a`
- **Run record:** `docs/reviews/adr_runs/HOST_DETECTOR_LOCAL_APPROVAL_v1_2026-11-11.md`
- **Declared revision class:** mechanism. The diff gate now requires the approval (user decision, 2026-11-11: "approval everywhere"; CI opts out with `--trusted-checkout`); detector loading changes to source-only; a shared host-row selector is added; hook mode exits 2 on any failure. Full re-run required.

## Blocking reasons

### C8 — UNPROVEN (external: non-2 exit codes reach the user only)

**Resolution:** external-data UNPROVEN, re-flagged not load-bearing in the spec text. §1.2 now marks the Claude Code behaviour *(external)* and states that the design depends only on the exit-2 half, which the hook already depends on (`posttooluse_gate.py:131`); if the user-only half were false, exit 2 would still be the documented agent channel. No attempt is made to "prove" external behaviour in-tree.

```
$ grep -n "(external)" docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md
16:Unprefixed paths refer to this repository. Every cited line is as at `main` `0da9864`; the branch adds only files und
58:The hook relies on exit `2` being the code whose stderr reaches the agent: *"Exit 2 feeds stderr back to Claude as bl
```

### C10 — REFUTED (diff gate run only by host config)

**Resolution:** mechanism change. The premise is withdrawn. §1.1 now names the hand-run sites the reviewer found (`acf-setup/SKILL.md:221-230`, `acf-mandate/SKILL.md:136`, `README.md:57`) as part of the problem. Decision 7: `acf-check-diff` requires the approval unless the invocation passes `--trusted-checkout`; §4.6 places `require_approval` inside the existing `try` (`cli_check_diff.py:83-100`); §4.7 adds the flag to the acf-setup CI sketch (`:208-209`) and approval notes to Step 9 and acf-mandate. The header records that this supersedes Decision 7 of `docs/design/HOST_DETECTOR_EXTENSION_POINT.md` (`:63-65`).

```
$ grep -n "trusted-checkout\|require_approval" docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md | wc -l
11
$ grep -n "^## Step 9\|^From the\|run: acf-check-diff\|# or: python" plugins/arch-compliance/skills/acf-setup/SKILL.md
208:  run: acf-check-diff --base "origin/${{ github.base_ref || 'main' }}" --repo . --call-site ci
209:  # or: python -m acf.cli_check_diff --base origin/main --repo . --call-site ci
221:## Step 9 — Smoke check
223:From the **host** root, run one of:
```

### C11 — UNPROVEN (Claude Code settings and folder trust)

**Resolution:** the claim is removed from the spec. The containment check (Decision 2) now stands on a fact that can be checked in-tree: `Path.home()` reads `USERPROFILE`/`HOME`, so the process environment chooses the store location, and refusing an in-repo store removes the route by which a repository supplies its own approval file. Nothing in the design rests on Claude Code's settings or folder trust.

```
$ grep -n "folder trust\|settings file" docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md
rc=1
```

### S1 — REFUTED (approval store duplicates nothing)

**Resolution:** absorbed. `read_store` is now an existence check plus `load_model_file(path, ApprovalStore, subject="approval store", fmt="json")` over pydantic `ApprovalEntry`/`ApprovalStore` models (`extra="forbid"`), the pattern `load_baseline` uses (`baseline.py:78-86`). The hand-rolled parse, shape check and OSError mapping are gone from the design.

```
$ grep -n "load_model_file" docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md
111:| `read_store(path: Path) -> ApprovalStore` | `ApprovalStore()` when `path.is_file()` is false; otherwise `load_mode
```

### S3 — REFUTED (test population recipe)

**Resolution:** replaced the by-name grep with an executed census (§2a): `docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/host_row_gate_tests.py` walks every tracked test module's AST and lists each test function that both runs a gate (hook or `acf-check-diff`) and builds a host row, following module-level helpers one level deep. Validated against the known sites: it reproduces the four hook tests and finds the three diff-gate tests the reviewer's behaviour sweep pointed to (`test_diff_cli.py:316`, `:326` are inside the `_host_rows` helper those tests call). §6.1's table is the census output, with a disposition per test.

```
$ python docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/host_row_gate_tests.py
plugins/arch-compliance/tests/test_diff_cli.py:350 test_host_ast_and_guard_rows_run_at_ci_and_block
plugins/arch-compliance/tests/test_diff_cli.py:367 test_host_guard_exemption_token_on_a_non_code_file_is_honoured
plugins/arch-compliance/tests/test_diff_cli.py:379 test_host_guard_only_row_at_precommit_passes_selection_and_reports
plugins/arch-compliance/tests/test_hooks.py:406 test_gate_disabled_does_not_import_a_host_module
plugins/arch-compliance/tests/test_hooks.py:440 test_gate_runs_hook_host_rows_and_not_ci_only_host_guards
plugins/arch-compliance/tests/test_hooks.py:464 test_gate_edited_file_outside_repo_yields_no_finding_and_no_host_call
plugins/arch-compliance/tests/test_hooks.py:488 test_gate_native_absolute_path_is_reported_under_its_posix_key
$ grep -n "_seed_host_rows" docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md
rc=1
```

### H5 — REFUTED (model_dump is deterministic for every row) — both lines of the run detail

**Resolution:** mechanism change in `fingerprint`: it hashes `_canonical(m.model_dump(mode="python"))`, where `_canonical` turns a `set`/`frozenset` into a list sorted by each element's canonical JSON text. §6.2 adds a test running the fingerprint under `PYTHONHASHSEED` 1, 2, 3. Probe of the canonicalisation over a YAML `!!set`:

```
$ for s in 1 2 3; do PYTHONHASHSEED=$s python -c "<load '!!set {alpha, beta, gamma, delta}' with yaml.safe_load; print raw order and canonical JSON>"; done
['beta', 'delta', 'gamma', 'alpha'] {"p": ["alpha", "beta", "delta", "gamma"]}
['delta', 'gamma', 'alpha', 'beta'] {"p": ["alpha", "beta", "delta", "gamma"]}
['gamma', 'delta', 'beta', 'alpha'] {"p": ["alpha", "beta", "delta", "gamma"]}
$ grep -n "_canonical\|PYTHONHASHSEED" docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md
114:| `fingerprint(rows, digests) -> str` | SHA-256 hex of `json.dumps({"rows": [_canonical(m.model_dump(mode="python"))
214:- A row whose `params` hold a YAML `!!set` gives the same fingerprint in subprocesses run with `PYTHONHASHSEED` `1`,
```

### H11 — UNPROVEN (os.replace atomic on Windows; not load-bearing)

**Resolution:** the atomicity claim is removed. The spec now says only that `write_approval` moves a complete temporary file into place with `os.replace` and that an `OSError` (including Windows refusing the replace while the store is open) is an `AcfInputError` naming the path; the risk table records a lost write as recoverable by re-running.

```
$ grep -n "atomic" docs/design/HOST_DETECTOR_LOCAL_APPROVAL.md
rc=1
```

## Other findings absorbed (not blocking lines)

| Finding | Absorption |
| --- | --- |
| Committed unchecked hash-based `.pyc` runs instead of the approved source | Decision 4 and §4.4: `_SourceOnlyLoader` overrides `get_code` to compile the source; §6.2 pins it. Probe: default loader runs `pyc`, source-only loader runs `source`. |
| Failures outside the four returns exit 1 in hook mode (UnicodeDecodeError, OSError from fingerprint) | Decision 8 and §4.5 step 5: in hook mode any `Exception` after the format is known exits 2 with type, message and traceback; `file_digests` wraps `OSError` as `AcfInputError`; §6.3 tests a non-UTF-8 file. |
| `acf-allow`'s missing-file branch unreachable; `UnknownDetectorError` unhandled | §4.3: the branch is removed; `acf-allow` handles `AcfInputError` and `UnknownDetectorError` with exit 1, citing `registry.py:160-172`. |
| `hook_host_rows` re-spells the runners' selection (Single point of definition) | §4.1: `MandateRegistry.host_rows` is the one selector, consumed by both runners and `acf.approval`. |
| cli_allow would recompute per-file digests | §4.2: `file_digests` is exposed and `fingerprint` takes its result. |
| Prose sites missed (README:108, acf-setup:159, hooks.json:2, hook docstring) | §4.7 lists them, plus the CI sketch, Step 9 and acf-mandate:136. |
| Unstated mandates (POSIX paths, Prose names no host, Single point of definition) | Added to the header with line ranges; Decision 2 quotes `ARCHITECTURE.md:58`. |
| Supersession of HOST_DETECTOR_EXTENSION_POINT Decision 7 unrecorded | **Supersedes:** header line with the quoted decision. |
| exec_module cited at host.py:81 | Now `:83`. |
| Home-directory repository is always STORE_IN_REPO | §3 states the case and its consequence. |
| Windows TS bridge `shell=True` path injection | Out of scope; recorded in §3 for a separate fix. |
| test_repo_paths.py omitted from guards | §6.5 lists it. |

## Sentence-type sweep

Swept the whole v2 spec (changed and carried text) with a quantifier/count scan (`every|all|only|no other|none|nothing|never|any|always|each|<n> tests/rows/...`).

| Type | Hits and disposition |
| --- | --- |
| T1 population without recipe | §6.1 test population → executed census (T7 device). §5 runtime files → recipe kept. SubagentStart → grep recipe plus the listed import lines. |
| T2 aggregate as claim | "four gate-input failures" (§1.2) → per-line table, each row cited. No other totals. |
| T3 universal quantifier | "Its only check is whether `.acf/enabled`…" (§1.1) → backed by the cited range `:74-83` and the end-to-end read of `main`; "neither gate imported a repository module" → recipe at `8677e45^`; "none of the `except` tuples names" (§1.2) → the tuples are cited at `:111`, `:118`; "the built-in calls read only them" (§4.5) → cited `:243-250`. Normative "every"/"each" in decisions and test steps are requirements, not census. |
| T4 tool/library behaviour in prose | `!!set` ordering → §6.2 `PYTHONHASHSEED` test; `.pyc` substitution → §6.2 unchecked-hash test; `Path.home()` env vars → used by §6 test setup, which fails if wrong. Claude Code exit-code/`systemMessage` behaviour → marked *(external)*, not pinned. |
| T5 named hook without receipt | `SourceFileLoader.get_code` → probe output above; `load_model_file` → `loader.py:43-77`; `RepoTree.contained`/`file` → `repo.py:53-64`; `MandateRegistry.active` → `registry.py:110-122`; `TIER1_CALL_SITES` → `registry.py:19`. |
| T6 attribution without quote | Decision 2 quotes `## POSIX paths`; §4.2 quotes `## One owner for host paths`; §4.7 quotes `## Release discipline`; Supersedes header quotes Decision 7; §1.1 quotes the doctrine, the skills and the README. |
| T7 completeness backed by known-site recipe | §6.1 → executed census, output committed (`host_row_gate_tests.out`). |

## Delta pre-flight (rehearsal, not the gate)

One rehearsal agent with the refuter and sweeper stances adjudicated the twelve v2 claims; all survived. Its findings, absorbed before requesting the gate:

| Finding | Absorption |
| --- | --- |
| Agent-facing messages invite the agent to run `acf-allow` or add `--trusted-checkout` | Decision 5: approval is run by a person; the hook notice and the diff-gate refusal ask the agent to have the user review and run `acf-allow`; acf-setup prose forbids the agent running either. |
| Diff-gate refusal over-broad: a `[hook]`-only host row refused a `--call-site ci` run | Decision 3: a gate needs the approval only when `registry.host_rows(call_sites)` is non-empty; `approval_state`/`require_approval` take `call_sites`; tests added in §6.2 and §6.4; §7 risk row narrowed. |
| `json.dumps(sort_keys=True)` raises `TypeError` on non-str dict keys | `_canonical` replaces each dict key with its canonical JSON text; §6.2 test added. |
| `acf-allow` could add a guarded `.resolve()` | §4.3: the repository is `resolve_repo(args.repo)`, as in `cli_check_diff.py:76`. |
| `write_approval` overlaps `save_baseline` unnamed | §4.2 names it ADJACENT, with the reason no helper is shared. |
| `load_baseline` wording | §4.2 quotes its docstring (`baseline.py:81-82`) instead of claiming a caller. |
| test_hooks.py `:145`, `:318`, `:424` said not to match | Checked: those are the `def` lines (`grep -n "def test_gate_clear_error_when_enabled_without_deps\|def test_gate_fails_loud_when_enabled_without_mandates\|def test_gate_unknown_detector_exits_1"` prints 145, 318, 424); carried unchanged. |
