# Response to ARCHITECTURE_REVIEW_PORT v2 gate run

- **Spec:** `docs/design/ARCHITECTURE_REVIEW_PORT.md`
- **Reviewed commit:** `f1511be` (run detail `ARCHITECTURE_REVIEW_PORT_v2_2026-11-12.md`, recorded at `ec43351`)
- **Revised as:** v3
- **Declared revision class:** mechanism. v3 defines one path matcher for include, surface and exclusion patterns (`acf.repo.path_matches`), changes how staleness and provenance report git failures, states that `auditor` (not `call_sites`) selects review rows, refuses undeclared settings keys on rows with no params-reading detector, and adds a producer-side `auditor` check (`check_auditors`) used by the review and the `acf-mandate` snippet. The remaining entries are precision.

Commands ran from the repository root; `hm` is `C:/Users/iball/Arduino/Projects/HistoricMansions`.

## Blocking reasons

### C10 (premise, SURVIVED on the spec's own citation) — carried unchanged

The claim held; the verdict was downgraded because the reviewer's evidence repeated the spec's citation. The citation is to the line itself, and its text bears the claim out:

```
$ git -C hm show b2611977f:docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md | sed -n 360p | grep -o "Cursor copies of [^.]*"
Cursor copies of `arch-compliance:adversarial-design-review` and `arch-compliance:responding-to-adversarial-review` from the plugin so other `GEMINI
```

### C21 (premise, REFUTED) — the ratchet counts the renamed key as growth

Accepted (precision). §5.4 now names three growth keys, `MandateEntry.arch_anchor`, `languages` and `params`, with the ratchet's name-matching rule cited.

```
$ git -C hm show b2611977f:scripts/ci/dead_code_ratchet.py | sed -n 377,381p
    moved = sorted(base_unref & cur_test)     # a test now consumes it
    return LaneDiff(
        grown={"unreferenced": sorted(cur_unref - base_unref),
               "test_only": sorted(cur_test - base_test - set(moved))},
        shrunk={"unreferenced": sorted(base_unref - cur_unref - set(moved)),
$ grep -c "reports three keys as growth" docs/design/ARCHITECTURE_REVIEW_PORT.md
1
```

### C23 (mandate, REFUTED; the line *"mandate claim C23 is REFUTED"* is the same finding) — unrecorded built-in meanings

Accepted. §4.4 now records every built-in meaning the review gives an absent or empty value: the built-in exclusion list, the built-in test-path list, an absent `surface`, an empty `subsystems`, and absent optional rule settings (a scalar turns its check off; a list is empty).

```
$ grep -c "the built-in test-path list" docs/design/ARCHITECTURE_REVIEW_PORT.md
1
```

### C30 (mandate, UNPROVEN) — staleness folded every git failure into "commit not in history"

Accepted (mechanism). §4.7 step 7: a non-zero `rev-list` is reported as "staleness unknown" with git's own error text, and a failed blame as "unresolved" with git's text; no cause is guessed. `run_git` returns the status and stderr as data, so this needs no new runner.

```
$ grep -c "commit not in history" docs/design/ARCHITECTURE_REVIEW_PORT.md
0
$ grep -c "staleness unknown" docs/design/ARCHITECTURE_REVIEW_PORT.md
2
$ sed -n 24,30p plugins/arch-compliance/python/acf/diff.py
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
```

### C41 (shape_fit, UNPROVEN) — "declared once" only holds on one row

Accepted (precision). Decision 10 now states the true scope: a fact is declared once when the rule and the detector share a row, and repeats across rows, as between two detector rows today. The census behind it is unchanged: no row today carries both an `auditor` and detector `params` (C45 survived in v2). `allowlist_globs` keeps its detector's `fnmatch` rule and is never matched by the review (§4.2).

```
$ grep -c "on two rows a fact repeats" docs/design/ARCHITECTURE_REVIEW_PORT.md
1
```

## Absorbed non-blocking findings

- **Path-pattern semantics (converged: three reviewers):** one matcher, `acf.repo.path_matches`, with the three pattern forms stated in §4.7 step 2; trailing-`/` and basename patterns match at any depth, so nested test directories are excluded.

```
$ grep -c "path_matches" docs/design/ARCHITECTURE_REVIEW_PORT.md
4
```

- **Staleness folding (converged: two reviewers):** answered under C30.
- **Call sites:** `auditor` selects review rows independently of `call_sites`, and the doctrine's call-site rule gains a sentence saying so (decision 17, §4.5, §6). Requiring `audit` instead was rejected: on the origin it would make the guard runner run four enforced guard rows (`hm:scripts/ci/run_guards.py:105-130`). `## Host detectors and call sites` is now a governing mandate.
- **Unread settings keys:** refused on rows whose detection is not `ast`/`guard`, listed on those rows (§4.2).
- **`auditor` validated at the producer:** `check_auditors`, called by the review and the `acf-mandate` snippet (§4.5).
- **Installed Python not covered by the skill check:** the cutover PR records the imported `acf` path, its version `0.3.0`, and its checkout's `HEAD` (§5).
- **Encoding debt citation:** moved to `## Declared text decoding` (`config/architecture/ARCHITECTURE.md:246-251`).
- **"Literal substring" prose:** `acf-mandate/SKILL.md:46` and `acf-setup/SKILL.md:139` reworded to line equality (§6).
- **Severity scale and `## Scoped refactor`:** both justified in §4.8.
- **Hook suffix map and the ratchet's file walk:** named in §10 for part two.
- **Origin anchor test:** `hm:tests/test_mandate_registry_drift.py:60-62` stays and checks anchors against their home, `hm:GEMINI.md` (§5.4).

## Sentence-type sweep

Swept the v3 spec with the same quantifier grep as the v1 record plus a read of every changed paragraph.

| # | Hits in changed text | Disposition |
|---|---|---|
| T1 population claims | none new | — |
| T2 aggregates | "three keys as growth" (§5.4) | each key named beside the count |
| T3 universal quantifiers | "each git failure reaches the report as itself" (§4.7) | normative behaviour of the design, backed by `run_git` returning status as data |
| T4 tool behaviour | the ratchet's name matching | cited at `hm:scripts/ci/dead_code_ratchet.py:377-380` |
| T5 named hooks | `fnmatch` in `facade_sinks.py:59`; `run_git` (`diff.py:17-30`) | cited; `path_matches`, `check_auditors` are new in §6 |
| T6 mandate attributions | call-site rule (`ARCHITECTURE.md:156-165`); `## Scoped refactor` (`:280-284`); encoding debt (`:246-251`) | cited adjacent |
| T7 completeness backed only by known sites | none new | — |
