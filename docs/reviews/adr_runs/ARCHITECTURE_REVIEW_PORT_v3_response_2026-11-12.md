# Response to ARCHITECTURE_REVIEW_PORT v3 gate run

- **Spec:** `docs/design/ARCHITECTURE_REVIEW_PORT.md`
- **Reviewed commit:** `b7965d0`
- **Run record:** `docs/reviews/adr_runs/ARCHITECTURE_REVIEW_PORT_v3_2026-11-12.md` (BLOCKED)
- **Declared revision class:** precision-only. No reviewer attacked the mechanism. Every blocking line asks for a census row, a stated meaning, or a narrower claim. The user approved clearing v4 by the controller verification pass on 2026-11-12.

## Blocking lines

### C17 (deletion, REFUTED): census gaps

The reviewer named three gaps.

- **(1) `params` growth.** The dead-code row no longer says `MandateEntry.params` will be reported. §5.1 and the §5.4 dead-code row now name the expected growth: `arch_anchor` (test-only) and `languages`. The ratchet runs `--check` first, the PR quotes that output, and the PR states whatever growth `--check` showed.
- **(2) The 48 `gemini_anchor:` keys.** They have their own census row (recipe B, `hm:config/architecture/mandates.yml`, for example `:14`).
- **(3) Stale references.** The `hm:scripts/core/exceptions.py:1525` docstring gets its own row (recipe C), which removes the sentence naming `BaselineError`. The hook row now covers `hm:scripts/setup_git_hooks.py:137-138`, removing the comment as well as the line.

Falsifier:

```
$ git -C HistoricMansions grep -c gemini_anchor b2611977f -- config/architecture/mandates.yml
b2611977f:config/architecture/mandates.yml:48
$ git -C HistoricMansions show b2611977f:scripts/core/exceptions.py | grep -n BaselineError
1456:class BaselineError(HistoricMansionsError):
1525:    or a key carries a backslash (§10). Deliberately NOT a BaselineError
$ git -C HistoricMansions show b2611977f:scripts/setup_git_hooks.py | sed -n 136,138p
# Advisory: warn when the compliance drift baseline is stale (never blocks).
python -m scripts.ci.baseline_staleness || true
```

### C21 (premise, REFUTED): the "exactly three keys" claim

The claim is replaced. The spec now states the expected growth (`arch_anchor`, `languages`) and why `params` is not reported. That outcome is not asserted as a fact: `--check` measures it on the cutover branch.

Executed census (scratchpad `v4_census_params.py`): an AST sweep of `hm:scripts` at `b2611977f` for loads of each name, plus vulture 2.16 run on a sandbox model.

```
params 22 ['scripts/cms_server/routes/tuner_print.py:216', 'scripts/cms_server/routes/tuner_print.py:307', ...]
languages 0 []
arch_anchor 0 []
vulture: <sandbox>\m.py:3: unused variable 'arch_anchor' (60% confidence)
<sandbox>\m.py:4: unused variable 'languages' (60% confidence)
```

Vulture does not report `params` when a function loads a local of that name. It does report `languages` and `arch_anchor`.

### C23 (mandate, UNPROVEN): an absent baseline

§4.4's list of built-in meanings now includes "no file at `baseline_path`". In that case the drift, staleness and provenance sections are omitted, and the roll-up says `no baseline (run --update-baseline to set one)`, as the current skill does for drift. §4.7 step 7 opens with that branch, and §7 adds the test.

Falsifier:

```
$ sed -n 140p plugins/arch-compliance/skills/architecture-review/SKILL.md
- No baseline file → omit Drift section; rollup notes `no baseline (run --update-baseline to set one)`.
```

### C26 (mandate, UNPROVEN): the second glob dialect

§6's doctrine edits now record a new breach under `## Single point of definition`. The breach is two path-glob dialects: `path_matches`, and `fnmatch` at `facade_sinks.py:59` and `fail_loud_ratchet.py:68`. They are kept apart for the reason §10 gives.

Falsifier:

```
$ sed -n 59p plugins/arch-compliance/python/acf/detectors/facade_sinks.py
        if fnmatch.fnmatch(posix, glob):
$ sed -n 68p plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py
            if any(fnmatch.fnmatch(rel, g) for g in excludes):
```

### C62 (mandate, REFUTED; listed twice in the run record): what `audit` means

Decision 17 now says it amends the call-site rule rather than complying with it as written. It also states the meaning `audit` keeps: an annotation that the review, not a Tier-1 gate, holds the row. No package code reads it, and the architecture review neither requires it nor reads it. §6's doctrine edit records that sentence.

Falsifier:

```
$ git grep -n -w audit -- plugins/arch-compliance/python
plugins/arch-compliance/python/acf/registry.py:17:CallSite = Literal["ci", "precommit", "hook", "posttooluse", "audit"]
```

### C64 (mechanism_justification, REFUTED): the write-time claim

The claim is narrowed. §4.5 now says `check_auditors` runs in three places:

- the review's step 1;
- the `acf-mandate` snippet, when a row is written through that skill;
- two of this repository's tests, over the self-host rows and every profile's rows. §6 and §7 add both tests: `tests/test_self_host.py` and `plugins/arch-compliance/tests/test_profile_drift.py`.

A row written any other way is refused when the review next runs. In the origin, that is the only point of refusal. The design does not change.

Falsifier, showing today's tests check anchors only:

```
$ grep -n -e "missing_anchors" -e "check_auditors" tests/test_self_host.py plugins/arch-compliance/tests/test_profile_drift.py
tests/test_self_host.py:5:`missing_anchors` is the one anchor check, `KNOWN_DETECTORS` the built-in detector contracts,
tests/test_self_host.py:16:from acf.registry import load_mandates, missing_anchors
tests/test_self_host.py:40:    assert missing_anchors(_registry(), doctrine) == []
plugins/arch-compliance/tests/test_profile_drift.py:9:from acf.registry import load_mandates, missing_anchors
plugins/arch-compliance/tests/test_profile_drift.py:30:        missing = missing_anchors(regs, arch_text)
```

## Carried to the implementation plan (advisories, not spec changes)

- Exemption-token owner for the review rows.
- Runtime messages under `acf/review`, and a test that checks they name no host.
- Scope of the §5.4 recipes beyond `-- ':!docs'`.
- Decoding of blame output.
- The remaining substring wording in `acf-setup` (`:115`) and `acf-mandate` (`:67`).
- `plugins/arch-compliance/tests/test_baseline.py:52-60`.
- The advice text in `run_detail` messages.

## Sentence-type sweep

I swept the whole revised spec for T1–T7.

- **T1 / T7 (population claims).** The §5.4 census is still backed by recipes A, B and C. The two population claims added in this revision rest on executed checks:
  - the 48 keys, by `git grep -c`;
  - `params` not being reported, by the AST sweep plus vulture above, with `--check` as the in-branch measurement.

  §5.2's "25 rows" stands on its recorded `yaml.safe_load` recipe.
- **T2 (aggregates).** "Expected growth" is stated as an expectation that `--check` measures, not as a count claim. "Twelve rules" and "twelve anchors" stand: each is enumerated in a table or by its recipe.
- **T3 (universals).** "No package code reads it" is backed by the `git grep -w audit` output. The "exactly three keys" universal was removed. "Every rule settings key is optional" stands as a design statement about the models this spec defines.
- **T4 (tool behaviour).** The vulture behaviour was observed in a sandbox run. The cutover's `--check` output is the in-tree pin.
- **T5 (named hooks).** Every new citation has a line receipt:
  - `dead_code_ratchet.py:492-493`;
  - `facade_sinks.py:59`;
  - `fail_loud_ratchet.py:68`;
  - `registry.py:17`;
  - `SKILL.md:140`;
  - `tuner_print.py:216`;
  - `exceptions.py:1525`;
  - `setup_git_hooks.py:137-138`.
- **T6 (doctrine attribution).** Decision 17 now calls itself an amendment rather than claiming compliance. The `## Single point of definition` breach is recorded in the form that section already uses.
