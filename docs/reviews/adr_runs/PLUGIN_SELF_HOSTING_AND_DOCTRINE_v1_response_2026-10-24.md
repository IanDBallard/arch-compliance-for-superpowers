# Author response — PLUGIN_SELF_HOSTING_AND_DOCTRINE v1

- **Spec:** `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` (revised to v2)
- **Reviewed commit:** `4efe8616e1e25b178689c115dec5dd8f0e8f9ec7`
- **Run record:** `docs/reviews/adr_runs/PLUGIN_SELF_HOSTING_AND_DOCTRINE_v1_2026-10-24.md` (Outcome: BLOCKED)
- **Declared revision class:** **mechanism.** The registry loader gains a refusal and a
  function, a skill's validation snippet changes, two fixtures gain exemption tokens, and
  the host test is redesigned. Re-run in full, blind.
- **Implementation commits on `feat/self-host`:** `bea94b2` (loader, tests, skill,
  fixtures, version 0.2.1), `9b1f158` (doctrine, registry rows, `CLAUDE.md`); the spec,
  plan and this record are committed together after them.

All commands ran from the worktree root on Windows with `PYTHONUTF8=1`, and with
`PYTHONPATH=plugins/arch-compliance/python` wherever the CLI is invoked, so the branch's
package is the one measured (the node's editable install points at the main clone).

## Blocking reasons

### 1. Load-bearing claim C25 (shape_fit) — REFUTED

**Finding.** The host test re-implemented package checks: the anchor loop of the profile
drift test, a third copy of the detector union, and mandate-id uniqueness and
manual-detector validation at the host tier instead of the loader.

**Resolution (mechanism).** Spec v2 decision 8 and §5.5:

- `load_mandates` refuses a repeated id with `AcfInputError` for every host
  (`plugins/arch-compliance/python/acf/registry.py:46-51`); the host's uniqueness test is
  deleted.
- `acf.registry.missing_anchors` is the one anchor check
  (`plugins/arch-compliance/python/acf/registry.py:63`). Live consumer: the `/acf-mandate`
  Validate snippet. Test consumers: `test_profile_drift.py`, `tests/test_self_host.py`.
- `KNOWN_DETECTORS` has one definition (`plugins/arch-compliance/python/acf/cli_check_diff.py:25`);
  the drift test, the host test and the skill snippet import it. The snippet's own union
  was narrower and rejected a stock profile's guard row (spec §4.1 item 14), now pinned by
  `plugins/arch-compliance/tests/test_acf_mandate_skill.py`.
- `tests/test_self_host.py` imports `ARCH_REL` and `MANDATES_REL` from `acf.repo`.
- The manual-row detector check stays host-tier as a stated non-merge (spec §3, §5.5):
  the registry contract leaves a manual row's `detector` free text, quoted from the design
  document and the `/acf-mandate` skill; "names a test module under
  `plugins/arch-compliance/tests/`" is this host's policy.
- Spec §7 now states each relationship in a table instead of "duplicates no existing check".

**Falsify — one detector-union definition in code and skills:**

```
$ git grep -n "KNOWN_DETECTORS =" -- "*.py" "*.md"
docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:571:| Detector-union spellings at the base | ... (appendix prose)
docs/plans/PLAN_PLUGIN_SELF_HOSTING.md:140:KNOWN_DETECTORS = ALL_PYTHON_DETECTOR_IDS | TS_DETECTOR_IDS | LLM_PROMPT_IDS   (v1 task text, marked superseded)
plugins/arch-compliance/python/acf/cli_check_diff.py:25:KNOWN_DETECTORS = ALL_PYTHON_DETECTOR_IDS | TS_DETECTOR_IDS | LLM_PROMPT_IDS
```

**Falsify — one anchor check and its consumers:**

```
$ git grep -n "missing_anchors(" -- "*.py" "*.md"   (docs/ lines omitted)
plugins/arch-compliance/python/acf/registry.py:63:def missing_anchors(registry: MandateRegistry, doctrine_text: str) -> list[str]:
plugins/arch-compliance/skills/acf-mandate/SKILL.md:99:missing = missing_anchors(reg, ARCH_REL.read_text(encoding='utf-8'))
plugins/arch-compliance/tests/test_profile_drift.py:27:        missing = missing_anchors(regs, arch_text)
plugins/arch-compliance/tests/test_registry.py:56:    assert missing_anchors(load_mandates(path), "# Doctrine\n\n## Kept\n") == ["gone"]
tests/test_self_host.py:34:    assert missing_anchors(_registry(), doctrine) == []
```

**Falsify — the loader refuses a repeat (RED before, GREEN after):**

```
# before (branch code at 4efe861, same loader as c0281bf): two rows with id "a"
current behaviour: loaded 2 rows; by_id keeps 1 -> ## B

# after: duplicate the first row of config/architecture/mandates.yml, run the host tests
acf.exceptions.AcfInputError: mandates file .../config/architecture/mandates.yml repeats mandate id(s) ['fail-loud.empty-catch']; by_id would keep only the last row of each
(file restored byte-identical)

$ python -m pytest plugins/arch-compliance/tests/test_registry.py plugins/arch-compliance/tests/test_profile_drift.py plugins/arch-compliance/tests/test_acf_mandate_skill.py tests/test_self_host.py -q
11 passed in 2.02s
```

**Falsify — the skill snippet (RED on the v1 prose, GREEN after):**

```
# RED, snippet as written at c0281bf, against a python-service host:
acf.exceptions.UnknownDetectorError: enforced mandate 'ops.no-build-artifacts' references unknown detector 'no_build_artifacts'
FAILED test_snippet_accepts_a_stock_profile_with_guard_rows
FAILED test_snippet_refuses_a_missing_anchor[## Fail loud]
# GREEN after the rewrite:
2 passed in 1.55s
```

### 2. Load-bearing claim C33 (implementability) — REFUTED

**Finding.** `/acf-setup`'s merge rule does not resolve the duplicate; it stops and asks,
and its "(should not for stock profiles)" premise is false. The one-row outcome was a
human decision.

**Resolution.** Spec v2 §4.1 item 4 quotes the rule beside the two profile lines, and
§5.2 states that the answer "keep one row" is the user's, given in advance in the plan
and recorded in its ledger; the skill does not produce it. Language detection is stated
with the clauses it rests on. The skill-text fix is filed as §9 follow-up 4, not made
here. Since the loader now refuses a repeat (entry 1), a merge that kept both rows fails
loud at the skill's own smoke step.

**Falsify:**

```
$ grep -n "should not for stock" plugins/arch-compliance/skills/acf-setup/SKILL.md
110:   - Keep every mandate `id` unique. If the same `id` appears in both (should not for stock profiles), stop and ask; never silently drop
$ grep -n "^- id: ops.no-build-artifacts" plugins/arch-compliance/profiles/*/mandates.yml
plugins/arch-compliance/profiles/python-service/mandates.yml:34:- id: ops.no-build-artifacts
plugins/arch-compliance/profiles/react-app/mandates.yml:23:- id: ops.no-build-artifacts
```

### 3. Load-bearing claim C38 (implementability) — REFUTED

**Finding.** The PostToolUse hook scans whole files, so a pre-existing finding returns on
any edit to its file and a BLOCK exits 2; and the host registry yields seven findings,
including a second BLOCK in `bad.tsx` the spec never dispositioned.

**Resolution (mechanism).** Spec v2 §4.1 item 11 and §5.4 describe the hook as it is
(whole-file, exit 2 as post-write blocking feedback, and the SubagentStart injection the
marker also turns on). §5.4 dispositions each of the seven findings in a table. The two
BLOCK fixture lines carry their row's exemption token with a reason, applying the spec's
own rule for a legitimate BLOCK line; the scanners still flag both lines because the
detector tests bypass the registry layer.

**Falsify — the hook scans whole files and exits 2 on BLOCK:**

```
$ grep -n "added_lines=None\|return 2" plugins/arch-compliance/hooks/posttooluse_gate.py
134:            return 2
254:            findings.extend(scan_python_file(text, rel, added_lines=None))
281:                for f in scan_typescript_file(abs_path, added_lines=None)
```

**Falsify — seven findings before, five WARN after:**

```
# detached worktree at c0281bf, npm ci, this branch's config/architecture/ copied in:
$ python -m acf.cli_check_diff --repo . --base dfff93f5 --json     -> exit 1
BLOCK fail-loud.bare-except plugins/arch-compliance/tests/fixtures/python/bad_except.py:4
BLOCK fail-loud.empty-catch plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:4
WARN no-shims.explicit-any plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:7
WARN no-shims.explicit-any plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:8
WARN no-shims.hasattr plugins/arch-compliance/tests/test_adr_exceptions.py:22
WARN no-shims.hasattr plugins/arch-compliance/tests/test_adr_import_graph.py:46
WARN no-shims.hasattr plugins/arch-compliance/tests/test_adr_skill_prose.py:53

# this branch:
$ PYTHONPATH=plugins/arch-compliance/python python -m acf.cli_check_diff --repo . --base dfff93f5; echo "exit $?"
WARN no-shims.explicit-any plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:7 Explicit `any` type is a no-shim escape hatch
WARN no-shims.explicit-any plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:8 Explicit `as any` assertion is a no-shim escape hatch
WARN no-shims.hasattr plugins/arch-compliance/tests/test_adr_exceptions.py:22 `hasattr` probes are no-shim violations
WARN no-shims.hasattr plugins/arch-compliance/tests/test_adr_import_graph.py:46 `hasattr` probes are no-shim violations
WARN no-shims.hasattr plugins/arch-compliance/tests/test_adr_skill_prose.py:53 `hasattr` probes are no-shim violations
exit 0
```

**Falsify — the detectors still see the fixture lines; the hook returns WARN context only:**

```
scan_python_file(bad_except.py)    -> [('fail-loud.bare-except', 4)]
scan_typescript_file(bad.tsx)      -> [('fail-loud.empty-catch', 4), ('no-shims.explicit-any', 7), ('no-shims.explicit-any', 8)]
$ python -m pytest plugins/arch-compliance/tests/test_python_pack.py plugins/arch-compliance/tests/test_typescript_pack.py -q
12 passed in 10.46s
$ npm test --prefix plugins/arch-compliance/detectors/typescript | tail -1
self-test OK: bad.tsx (3 findings), good.tsx (clean), line filter
$ python plugins/arch-compliance/hooks/posttooluse_gate.py --repo . plugins/arch-compliance/tests/fixtures/python/bad_except.py plugins/arch-compliance/tests/fixtures/typescript/bad.tsx; echo "exit $?"
ACF PostToolUse gate findings:
- WARN no-shims.explicit-any plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:7 Explicit `any` type is a no-shim escape hatch
- WARN no-shims.explicit-any plugins/arch-compliance/tests/fixtures/typescript/bad.tsx:8 Explicit `as any` assertion is a no-shim escape hatch
exit 0
```

### 4. Implementability claim C33 — REFUTED

Same claim and finding as entry 2; resolved there.

### 5. Implementability claim C38 — REFUTED

Same claim and finding as entry 3; resolved there.

## Converged findings and absorptions (not blocking; folded in)

| Item | Where answered in v2 |
|---|---|
| Third undeclared-encoding call (`typescript_bridge.py:53`) | §4.1 item 7, doctrine `## Declared text decoding` with its recipe and runtime-code scope, §9 follow-up 1 |
| §4.2 omitted branch files; test counts disagreed | §4.2 has a row per branch path; DoD 1 names each test |
| Host test re-spelled the config directory | `tests/test_self_host.py` imports `acf.repo` constants; doctrine `## One owner for host paths` states its test's scope |
| Detector union and anchor loop duplicated | Entry 1 |
| Doctrine scope omitted root `tests/` and `scripts/` | Doctrine opening paragraph; spec §5.2 |
| `CLAUDE.md` restated `## Release discipline` | `CLAUDE.md` carries the command and points to the section |
| Doctrine named enforcing tests beside the rows | Sections name the row id only |
| HM citations off at the pin; `hm-1d:` prefix | Re-pinned to HM `22eae4f9`, lines re-measured; prefix retired since 1d merged |
| Stale start condition, ledger count, root documents | §4.1 items 1, 13; §10 per-spec table with recipe |
| SubagentStart injection unstated | §4.1 item 11, §5.4 |
| CI step on push events | §5.6 |
| `call_sites: [review]` undefined | `[audit]` from the design document's vocabulary |
| Byte check covers the gate skills alone | Doctrine `## Release discipline`; §9 follow-up 5 |
| `No completeness claims`, `Declared, never defaulted` unscoped | Scopes stated in the doctrine |
| "Three stock rows are set unenforced" overstated | §5.2: two arrive unenforced, one is changed |

A premise this response authored and then refuted itself before commit: a first draft said
HM's registry "loads under the refusal". Running it showed HM's `mandates.yml` is in HM's
own schema and does not load through `load_mandates` at all; §5.5 and §9 now say so, with
the command in the appendix.

## Sentence-type sweep

Swept the whole revised spec (changed and carried text) with
`python -I spec_checks.py . <hm> docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md`, which
lists each line carrying a quantifier (`every|all|only|none|nothing|never|always|complete|untouched|each`),
and by reading for counts, named constructs and attributions.

| Type | Hits | Disposition |
|---|---|---|
| T1 population/consumer claim | §5.5 consumers of `missing_anchors` and `KNOWN_DETECTORS`; §5.5 "HM's tracked files name `acf.registry` … only in design and review prose" | Recipes above and in the appendix; the HM recipe validated against known prose hits before trusting its negative |
| T2 aggregate count | "Eight such specs", "seven findings", "404 tests", "Three subprocess calls", "Five sections have a row" | Each is backed by a per-item table (§10, §5.4, §5.2) or an appendix recipe; none is the claim on its own |
| T3 universal quantifier | §0 "Every unprefixed citation … is a full repository-relative path"; §5.2 "Every stock anchor survives verbatim"; §0 "each rule this spec lifts" | Citation check: the gate's own `unresolved_citations` over 135 unprefixed citations returns `[]`; anchors: the enumerated list plus `test_every_anchor_is_in_the_doctrine`; lifted rules: enumerated in §5.2 ("§5.2 lists them"). Other hits are quotes of cited text, normative rules, or bounded to an enumerated table |
| T4 prose-only tool behaviour | PostToolUse exit 2 "after the write"; CI three-dot diff empty on push | Exit 2 cites `posttooluse_gate.py:131-134` and the hook's event name; the push case cites `plugins/arch-compliance/python/acf/diff.py:42-45`. Neither has an in-tree executable pin; recorded, stands |
| T5 named construct without receipt | `missing_anchors`, `KNOWN_DETECTORS`, `by_id`, `_render_constraints`, `PosixStr`, `PYTHON_DETECTOR_IDS` | Each now carries a `path:line` receipt beside it |
| T6 attribution without quoted trigger | `/acf-setup` merge rule; design-document `detector` vocabulary; `/acf-mandate` manual-row guidance; host-contract decision 6; README setup line; acf-mandate's eye-check sentence | Each is quoted adjacent to the inference |

Mechanical stop (gate step 2b) on the revised spec: no literal tabs, no placeholders, no
slice or phase tags. Archaeology scan hits are role names ("the compliance reviewer
reads") and outcome vocabulary (`BLOCKED`, `CLEARED`) in the design's own procedure; the
spec body names no prior version, run or verdict.
