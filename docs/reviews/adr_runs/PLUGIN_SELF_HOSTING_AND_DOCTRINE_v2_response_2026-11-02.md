# Author response — PLUGIN_SELF_HOSTING_AND_DOCTRINE v2

- **Spec:** `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` (revised to v3)
- **Reviewed commit:** `9c8c283747f2e95bdc9aa348e2e89542f2c6ac06`
- **Run record:** `docs/reviews/adr_runs/PLUGIN_SELF_HOSTING_AND_DOCTRINE_v2_2026-10-24.md` (Outcome: BLOCKED)
- **Declared revision class:** **mechanism.** `acf.registry.missing_anchors` switches from substring search to stripped-line matching; `MandateRegistry` gains `@model_validator(mode="after") _unique_ids` (moving repeated-id refusal from rung 3 to rung 1); `plugin.prose-names-no-host` splits into two manual rows (`plugin.adr-code-names-no-host` and `plugin.gate-prose-names-no-host`); unused `PYTHON_DETECTOR_IDS` is removed; `tests/test_check_installed_skills.py` imports `GATE_SKILLS` from `scripts/check_installed_skills.py`. Re-run in full, blind.

All commands ran from the worktree root on Windows with `PYTHONUTF8=1`, and with
`PYTHONPATH=plugins/arch-compliance/python` wherever the CLI or package is invoked.

## Blocking reasons

### 1. Load-bearing claim C39 & mandate claim C39 (mandate) — REFUTED

**Finding.** The executable snippet at `plugins/arch-compliance/skills/architecture-review/SKILL.md:62` is `reg = load_mandates(Path("config/architecture/mandates.yml"))`, a second spelling of `acf.repo.MANDATES_REL` that the doctrine's `## Single point of definition` and `## One owner for host paths` did not record as a current breach.

**Resolution (spec + doctrine).** Executed a full census across all `.py` files and `plugins/arch-compliance/skills/*/SKILL.md` files for host-path and anchor-check spellings (`git grep -n -E "mandates\.yml|ARCHITECTURE\.md|adr\.yml|arch_anchor|missing_anchors" -- "*.py" "plugins/arch-compliance/skills/*/SKILL.md"`). Under `## Scoped refactor`, the skill snippets in `/architecture-review` and `/acf-setup` are not rewritten in this PR, and both `plugins/arch-compliance/skills/architecture-review/SKILL.md:62` (`Path("config/architecture/mandates.yml")`) and `plugins/arch-compliance/skills/acf-setup/SKILL.md:137` (by-eye anchor check) are now explicitly recorded as current skill-prose breaches in `config/architecture/ARCHITECTURE.md` (`## One owner for host paths` and `## Single point of definition`) and in spec §4.1 item 14, §5.2, §7 and §9 follow-up 4.

**Falsify — executed census of host-path and anchor-check spellings in code and skills:**

```
$ git grep -n -E "MANDATES_REL|ARCH_REL|ADR_REL|missing_anchors" -- "*.py" "plugins/arch-compliance/skills/*/SKILL.md"
plugins/arch-compliance/hooks/inject_constraints.py:13:from acf.repo import ARCH_REL, CONFIG_DIR, MANDATES_REL, is_enabled, resolve_repo
plugins/arch-compliance/hooks/posttooluse_gate.py:42:from acf.repo import CONFIG_DIR, ENABLED_REL, MANDATES_REL, is_enabled, resolve_repo
plugins/arch-compliance/python/acf/adr/host.py:11:from acf.repo import ADR_REL, ARCH_REL
plugins/arch-compliance/python/acf/cli_check_diff.py:21:from acf.repo import MANDATES_REL, resolve_repo
plugins/arch-compliance/python/acf/cli_check_llm.py:16:from acf.repo import MANDATES_REL, resolve_repo
plugins/arch-compliance/python/acf/registry.py:67:def missing_anchors(registry: MandateRegistry, doctrine_text: str) -> list[str]:
plugins/arch-compliance/python/acf/repo.py:15:MANDATES_REL = CONFIG_DIR / "mandates.yml"
plugins/arch-compliance/python/acf/repo.py:18:ARCH_REL = CONFIG_DIR / "ARCHITECTURE.md"
plugins/arch-compliance/python/acf/repo.py:21:ADR_REL = CONFIG_DIR / "adr.yml"
plugins/arch-compliance/skills/acf-mandate/SKILL.md:92:from acf.repo import ARCH_REL, MANDATES_REL
plugins/arch-compliance/skills/acf-mandate/SKILL.md:99:missing = missing_anchors(reg, ARCH_REL.read_text(encoding='utf-8'))
plugins/arch-compliance/tests/test_profile_drift.py:27:        missing = missing_anchors(regs, arch_text)
plugins/arch-compliance/tests/test_registry.py:62:    assert missing_anchors(load_mandates(path), doctrine) == ["gone"]
tests/test_self_host.py:15:from acf.registry import load_mandates, missing_anchors
tests/test_self_host.py:16:from acf.repo import ARCH_REL, MANDATES_REL

$ git grep -n "load_mandates(" -- "plugins/arch-compliance/skills/*/SKILL.md"
plugins/arch-compliance/skills/acf-mandate/SKILL.md:94:reg = load_mandates(
plugins/arch-compliance/skills/architecture-review/SKILL.md:62:reg = load_mandates(Path("config/architecture/mandates.yml"))
```

### 2. Load-bearing claim C58 (sweep) — REFUTED

**Finding.** Sweeping `hm:docs/design/` by filename prefix (`ADR_*` + `ARCH_COMPLIANCE_SHIFT_LEFT_GATING.md`) was a name sweep rather than a subject sweep and missed `hm:docs/design/ADVERSARIAL_DESIGN_REVIEW.md` (the gate's origin spec) and the three `hm:docs/design/ARCHITECTURE_COMPLIANCE_FRAMEWORK*.md` specs.

**Resolution (spec).** Executed a Python subject census across all 46 `hm:docs/design/*.md` files and all rows in `hm:docs/reviews/adversarial_design_ledger.jsonl`, identifying all 12 specs in `hm:docs/design/` whose subject is the ADR gate or ACF (7 post-plugin `ADR_*.md` specs and 5 pre-extraction HM origin specs). Spec v3 §1, §7, §10 and the appendix table now state the subject criterion and list all 12 specs with their ledger row counts and dispositions.

**Falsify — executed census over `hm:docs/design/*.md` and `hm:docs/reviews/adversarial_design_ledger.jsonl`:**

```
Total .md files in HM docs/design: 46
Specs whose subject is ADR gate or ACF: 12
  docs/design/ADR_EXTRACTION_TO_PLUGIN.md                      | ledger_rows=7
  docs/design/ADR_GATE_HM_ADOPTION.md                          | ledger_rows=0
  docs/design/ADR_GATE_HM_CUTOVER.md                           | ledger_rows=6
  docs/design/ADR_GATE_HOST_CONTRACT.md                        | ledger_rows=4
  docs/design/ADR_GATE_PLUGIN_COMPONENT.md                     | ledger_rows=3
  docs/design/ADR_PER_FINDING_REVISION_CLASSING.md             | ledger_rows=0
  docs/design/ADR_REVISION_EVIDENCE_AND_CARRYOVER_INSTRUMENTATION.md | ledger_rows=4
  docs/design/ADVERSARIAL_DESIGN_REVIEW.md                     | ledger_rows=0
  docs/design/ARCHITECTURE_COMPLIANCE_FRAMEWORK.md             | ledger_rows=0
  docs/design/ARCHITECTURE_COMPLIANCE_FRAMEWORK_TIER2_LLM_JUDGE.md | ledger_rows=0
  docs/design/ARCHITECTURE_COMPLIANCE_FRAMEWORK_TIER3_AUDIT.md | ledger_rows=0
  docs/design/ARCH_COMPLIANCE_SHIFT_LEFT_GATING.md             | ledger_rows=0
```

### 3. Load-bearing claim C80 & implementability claim C80 (implementability) — REFUTED

**Finding.** `missing_anchors` tested `m.arch_anchor not in doctrine_text` (substring). Because `config/architecture/ARCHITECTURE.md:17` quotes `` `## Fail loud` `` and `` `## React boundaries` `` inline in backticks, dropping either heading line from `config/architecture/ARCHITECTURE.md` still returned `[]` from `missing_anchors`, falsifying DoD 2 for 2 of 14 anchors.

**Resolution (mechanism).** Changed `missing_anchors` in `plugins/arch-compliance/python/acf/registry.py:67-70` to match `m.arch_anchor.strip()` against `{line.strip() for line in doctrine_text.splitlines()}`. Updated `test_missing_anchors_names_rows_whose_anchor_is_absent` in `plugins/arch-compliance/tests/test_registry.py:55-62` so the fixture doctrine contains an inline backtick mention of `` `## Gone` `` and asserts `missing_anchors` still reports `["gone"]`.

**Falsify — in-process heading-drop check across all 14 unique anchors (17 rows) in `config/architecture/mandates.yml`:**

```
Total mandates: 17
Unique anchors: 14
Drop '## Build artifacts'           -> missing_anchors = ['ops.no-build-artifacts']
Drop '## Declared, never defaulted' -> missing_anchors = ['plugin.declared-never-defaulted']
Drop '## FSM transitions'           -> missing_anchors = ['fsm.transition-guard']
Drop '## Fail loud'                 -> missing_anchors = ['fail-loud.empty-catch', 'fail-loud.bare-except']
Drop '## Fail-loud ratchet'         -> missing_anchors = ['fail-loud.ratchet']
Drop '## Façade sinks'              -> missing_anchors = ['facade.forbid-sink']
Drop '## Frozen ledger format'      -> missing_anchors = ['plugin.frozen-ledger-format']
Drop '## No shims'                  -> missing_anchors = ['no-shims.explicit-any', 'no-shims.hasattr']
Drop '## One base exception'        -> missing_anchors = ['plugin.one-base-exception']
Drop '## One owner for host paths'  -> missing_anchors = ['plugin.one-owner-host-paths']
Drop '## POSIX paths'               -> missing_anchors = ['posix-paths.str-serialization']
Drop '## Prose names no host'       -> missing_anchors = ['plugin.adr-code-names-no-host', 'plugin.gate-prose-names-no-host']
Drop '## React boundaries'          -> missing_anchors = ['soft.react-boundaries']
Drop '## Soft fail-loud smells'     -> missing_anchors = ['soft.fail-loud']
ALL 14/14 ANCHORS VERIFIED!
```

### 4. Load-bearing claim C81 & implementability claim C81 (implementability) — UNPROVEN

**Finding.** `/acf-setup`'s TypeScript detection clauses ("(or a clear app package)" and "substantial tree") are judgment prose and not proven to fire on the three-file TypeScript detector bridge; the plan (`docs/plans/PLAN_PLUGIN_SELF_HOSTING.md:78`) pre-answers `languages = both`.

**Resolution (spec).** Spec v3 §4.1 item 4 and §5.2 now state that Python is detected via `pyproject.toml`, that `/acf-setup`'s TypeScript clauses may report Python only on the three-file bridge package, and that the user supplies `both` at the language prompt as recorded in `docs/plans/PLAN_PLUGIN_SELF_HOSTING.md:78`.

**Falsify:**

```
$ sed -n 78p docs/plans/PLAN_PLUGIN_SELF_HOSTING.md
- [ ] **Step 1: Ask the user, then run `/acf-setup` in a Claude Code session whose cwd is the worktree root.** ... Answers to its prompts, fixed by the spec: languages = **both** (Python under `plugins/arch-compliance/python/`, TypeScript with its own `package.json` under `plugins/arch-compliance/detectors/typescript/`; announce this if detection says Python only) ...
```

### 5. Mandate claim C38 (mandate) — REFUTED

**Finding.** §0 asserted `"Every unprefixed citation in this spec is a full repository-relative path with no shorthand"` without a recipe, and the spec itself contained shorthand (`:47`, `:32-44`, bare `ARCH_COMPLIANCE_FOR_SUPERPOWERS.md`, `bad_except.py:4`, etc., and unprefixed HM names in §10). Also census item 15 asserted `"the package has no anchor-check function"` without an appendix recipe row.

**Resolution (spec).** Removed the false universal from §0, expanded every shorthand citation in the spec to its full repository-relative (or `hm:`-prefixed) path, verified zero bare `:line` tokens and zero `unresolved_citations` across all 272 path-like citations in the spec, and added the appendix recipe row for census item 15 (`git grep -n "arch_anchor" c0281bf -- plugins/arch-compliance/python`).

**Falsify — citation and shorthand check on `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` (v3):**

```
$ python check_spec_v3.py
Total path-like citations: 272 (unprefixed=219, hm=53)
Unique cited files (count_cited_files): 87
Unresolved self: []
Unresolved HM:   []
Bare :line tokens: []

$ git grep -n "arch_anchor" c0281bf -- plugins/arch-compliance/python
c0281bf:plugins/arch-compliance/python/acf/judge.py:154:        arch_anchor=mandate.arch_anchor,
c0281bf:plugins/arch-compliance/python/acf/registry.py:23:    arch_anchor: str
```

### 6. Implementability claim C83 (implementability) — REFUTED

**Finding.** `plugin.prose-names-no-host` had title `"Skill prose and runtime messages name no host repository, path or section"`, but its `detector` was `plugins/arch-compliance/tests/test_adr_code_portability.py` (which scans only `acf/adr/*.py` and two runtime strings, and reads no skill prose; gate skill prose is checked by `plugins/arch-compliance/tests/test_adr_skill_prose.py`). Also `config/architecture/ARCHITECTURE.md:129-130` named `test_adr_skill_prose.py` by file path, violating §5.2's rule ("the doctrine section names the row id, not the test path").

**Resolution (mechanism).** Split `plugin.prose-names-no-host` in `config/architecture/mandates.yml` into two manual rows under `arch_anchor: "## Prose names no host"`:
- `plugin.adr-code-names-no-host` (`detector: plugins/arch-compliance/tests/test_adr_code_portability.py`, title: `The gate's package and runtime messages name no origin host`)
- `plugin.gate-prose-names-no-host` (`detector: plugins/arch-compliance/tests/test_adr_skill_prose.py`, title: `The gate skills' prose names no origin host`)

Updated `config/architecture/ARCHITECTURE.md` (`## Prose names no host`) and spec §5.2 to name only those two row ids and state that the other three skills in `plugins/arch-compliance/skills/` have no row yet.

**Falsify:**

```
$ python -m pytest tests/test_self_host.py plugins/arch-compliance/tests/test_adr_code_portability.py plugins/arch-compliance/tests/test_adr_skill_prose.py -q
8 passed in 1.12s
```

### 7. Additional blocking reason entries in `## Blocking reasons`

- **Mandate claim C39 — REFUTED:** duplicate of load-bearing claim C39; resolved in entry 1.
- **Implementability claim C80 — REFUTED:** duplicate of load-bearing claim C80; resolved in entry 3.
- **Implementability claim C81 — UNPROVEN:** duplicate of load-bearing claim C81; resolved in entry 4.

## Absorptions, converged findings and unanchored items folded into v3

| Item | Where answered in v3 |
|---|---|
| Converged 1 (`plugin.prose-names-no-host` detector mismatch & raw test path in doctrine) | Entry 6 (`plugin.adr-code-names-no-host` + `plugin.gate-prose-names-no-host` in `config/architecture/mandates.yml` and `config/architecture/ARCHITECTURE.md`) |
| Converged 2 (shorthand citations & unprefixed HM names in §0 / §10 / appendix) | Entry 5 |
| Converged 3 & Absorption 2 (unused `PYTHON_DETECTOR_IDS` alias in `python_pack.py` and `detectors/__init__.py`) | Deleted `PYTHON_DETECTOR_IDS` from `plugins/arch-compliance/python/acf/detectors/python_pack.py` and `plugins/arch-compliance/python/acf/detectors/__init__.py`; zero hits in code (`git grep -n "PYTHON_DETECTOR_IDS" -- "*.py"` returns nothing) |
| Absorption 1 (`/acf-setup` Step 6 by-eye anchor check at `plugins/arch-compliance/skills/acf-setup/SKILL.md:137`) | Recorded as current breach in `config/architecture/ARCHITECTURE.md` (`## Single point of definition`) and spec §4.1 item 14, §5.2, §7, §9 follow-up 4 |
| Absorption 4 (`tests/test_check_installed_skills.py` duplicated `SKILLS` tuple) | `tests/test_check_installed_skills.py` now reads `_load_script().GATE_SKILLS` instead of defining a second tuple |
| Absorption 6 (repeated-id check at rung 3 instead of rung 1) | Moved to `@model_validator(mode="after") def _unique_ids` on `MandateRegistry` in `plugins/arch-compliance/python/acf/registry.py:33-41` |
| C62 ("where a rule applies to Python" overstates the 8 lifted HM clauses) | Spec §2 item 2 and §5.2 now state that the doctrine lifts the eight general clauses listed in §5.2 |
| Unanchored: `PosixStr` line citation off by 1 (`contract.py:128` vs `:129`) | Updated to `plugins/arch-compliance/python/acf/adr/contract.py:129` in `config/architecture/ARCHITECTURE.md:64` and spec §5.2 |
| Unanchored: `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:102,184` `detector` / unknown-detector wording vs `manual` rows | Updated lines 102 and 184 of `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md` to include manual verification pointers and scope unknown-detector errors to enforced `ast` or `guard` rows |
| Unanchored: `pyproject.toml:15,36` comment says `tests/test_packaging.py` | Updated both comments in `pyproject.toml` to `plugins/arch-compliance/tests/test_packaging.py` |
| Unanchored: `PostToolUse` also runs `no_build_artifacts` path guard (`posttooluse_gate.py:284-294`) and `SubagentStart` blindness scope | Added to spec §4.1 item 11, §5.4 and the appendix table |

## Sentence-type sweep

Swept `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` (v3) across all 71 lines containing quantifiers (`every|all|only|none|nothing|never|always|complete|untouched|each`), aggregate counts, named constructs, attributions, and self-exemptions.

| Type | Hits | Disposition |
|---|---|---|
| T1 population/consumer claim | §4.1 item 15 (`no anchor-check function`); §5.5 consumers of `missing_anchors` and `KNOWN_DETECTORS`; §5.5 HM tracked files naming `acf.registry` | Backed by executed grep recipes in the appendix and Entry 1 / Entry 5 above |
| T2 aggregate count | "Twelve specs in `hm:docs/design/`", "eight general clauses", "seven findings", "404 tests", "Three subprocess calls", "Five sections have rows (six manual rows in total)", "14 anchor headings" | Each is backed by a per-item enumeration or table (§10, §5.2, §5.4) and an executed recipe in the appendix |
| T3 universal quantifier | Removed §0's false universal; remaining hits are bounded to enumerated sets ("each rule this spec lifts ... (§5.2 lists the eight lifted clauses)", "Every stock anchor survives verbatim" followed by the 9 stock anchors and verified by `verify_dod2.py` across 14/14 anchors, "each path in `git diff --stat main` has a row in §4.2") or quotes of cited rules | Verified by `check_spec_v3.py` and `verify_dod2.py` |
| T4 prose-only tool behaviour | `/acf-setup` TypeScript detection clauses (`§4.1 item 4`, `§5.2`); `PostToolUse` exit 2 after write (`§5.4`); CI three-dot diff on push (`§5.6`) | `/acf-setup` language prompt is explicitly answered `both` by the user (`docs/plans/PLAN_PLUGIN_SELF_HOSTING.md:78`); hook and diff behaviour cite `plugins/arch-compliance/hooks/posttooluse_gate.py:131-134` and `plugins/arch-compliance/python/acf/diff.py:42-45` |
| T5 named construct without receipt | `MandateRegistry._unique_ids`, `missing_anchors`, `KNOWN_DETECTORS`, `by_id`, `_render_constraints`, `PosixStr`, `PYTHON_DETECTOR_IDS`, `GATE_SKILLS` | Every construct carries a `path:line` receipt at point of use |
| T6 attribution without quoted trigger | `/acf-setup` merge rule and Step 6 prose; `ARCH_COMPLIANCE_FOR_SUPERPOWERS.md` `detector` vocabulary; `/acf-mandate` manual-row guidance; host-contract decision 6 | Quoted adjacent to the inference |
| T7 self-exemption without authority | Skill-prose breaches in `plugins/arch-compliance/skills/architecture-review/SKILL.md:62` and `plugins/arch-compliance/skills/acf-setup/SKILL.md:137` | Explicitly cites `## Scoped refactor` (`hm:GEMINI.md:129`), records both breaches in `config/architecture/ARCHITECTURE.md`, and files §9 follow-up 4 |

Mechanical stop (gate step 2b) on `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` (v3): no literal tabs, no placeholders, no slice or phase tags, zero `unresolved_citations`, and no prior-verdict archaeology in the spec body.
