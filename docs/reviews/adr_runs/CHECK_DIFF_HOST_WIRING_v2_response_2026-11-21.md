# Response to the v2 review of `docs/design/CHECK_DIFF_HOST_WIRING.md`

- Spec: `docs/design/CHECK_DIFF_HOST_WIRING.md`
- Reviewed commit: `59ad23a96965e328756c759b06a711a4b8be7be4`
- Run record: `CHECK_DIFF_HOST_WIRING_v2_2026-11-21.md` (BLOCKED)
- Declared revision class: **mechanism**. The pre-push step no longer passes over a missing tool. It now refuses unless the environment declares `ACF_PREPUSH_OPTIONAL=1`; the user chose this. `/acf-setup` now reads the gate's own "selects no active" refusal instead of restating that predicate. The revision re-runs in full.

## Blocking reasons

### C42 (implementability, UNPROVEN): the pre-commit framework placement works as written

**Removed.** The spec no longer prescribes pre-commit framework fields, the `pre-push` stage, `--hook-type`, or how `sh -c` handles the entry. §4.3 now names three places for the snippet: a `pre-push` file in the `core.hooksPath` directory, `.git/hooks/pre-push`, or "the host's hook manager (husky, the pre-commit framework), configured to run the guarded command at pre-push". `/acf-setup` adapts that to the host. Nothing the design relies on is left without in-tree evidence.

Falsifier: the spec carries no framework specifics.

```
$ grep -n -i "hook-type\|stages:\|pass_filenames\|default_install_hook_types" docs/design/CHECK_DIFF_HOST_WIRING.md; echo "exit $?"
exit 1
```

## The mechanism the run flagged as repairing rather than refusing

The run's roll-up listed "pre-push skip when acf-check-diff is absent" under *Mechanisms that repair rather than refuse*. The hardening trace gave it design rung 5 against a highest applicable rung of 3. The user chose a declared opt-out. §2 decision 6 and the §4.3 snippet now refuse by default and print an install hint. The step skips only when the environment sets `ACF_PREPUSH_OPTIONAL=1`, which is kept out of committed files, so a fresh clone still refuses. Unset, or any other value, refuses. `## Declared, never defaulted` records that the variable has no default.

Falsifier: the snippet's branches, executed with the tool absent.

```
$ sh -c 'unset ACF_PREPUSH_OPTIONAL; if command -v no-such-acf-xyz >/dev/null 2>&1; then :; elif [ "${ACF_PREPUSH_OPTIONAL:-}" = "1" ]; then echo skipped; else echo refused >&2; exit 1; fi'; echo "unset: exit $?"
refused
unset: exit 1
$ ACF_PREPUSH_OPTIONAL=1 sh -c '…same…'; echo "=1: exit $?"
skipped
=1: exit 0
$ ACF_PREPUSH_OPTIONAL=yes sh -c '…same…'; echo "=yes: exit $?"
refused
=yes: exit 1
$ sh -c 'set -u; unset ACF_PREPUSH_OPTIONAL; [ "${ACF_PREPUSH_OPTIONAL:-}" = "1" ] || echo "set -u safe"'
set -u safe
```

## Advisories folded in

| Finding (source lens) | Resolution |
| --- | --- |
| This repository's `## Post-merge` bullet still names the `test` job (sweeper, compliance; converged) | §4.4: the bullet names the `test` and `action` jobs |
| Action defaults not recorded under `## Declared, never defaulted` (compliance) | §4.4 records them; added to the governing mandates |
| `--trusted-checkout` kept in the README and guide local examples (compliance) | Dropped there; their flag prose gains "the check-diff action passes it by default" |
| Stale `SKILL.md:249` and `:253`; README `:62` and COMPLEMENT `:87` (sweeper) | §4.3 rewrites `:249` whole and `:253`; `:62` and `:87` stay true and gain the action note |
| The fixture lacks a git identity (hardening, refuter) | §4.2: per-command `-c` identity, as `test_adr_citation_history.py:20` does |
| `exit` inside a function ends the script (hardening) | §4.3: only a `( … )` subshell confines `exit` |
| The tag could precede `main`'s first run of the empty-`base_ref` path (hardening) | §4.4: tag once `main`'s CI run for the merge commit has passed |
| A stale local `origin/<default>` (refuter) | §4.3: third known gap |
| "Cannot reach the venv" overstated (refuter) | §2 decision 8: the venv does not exist until the action creates it, and `host-setup` is the supported place |
| Uncaught exceptions also exit non-zero (refuter) | §2 decision 6 says so |

## Evidence-availability check

| Load-bearing claim (changed) | In-tree evidence | Disposition |
| --- | --- | --- |
| The opt-out snippet's branches | executed (above) | kept |
| `/acf-setup` site check through the gate's refusal | `cli_check_diff.py:94-100` runs before `:102` (approval) | kept |
| Fixture identity and branch name | `test_adr_citation_history.py:20` (the same `-c` options) | kept |
| Pre-commit framework behaviour | none possible | removed from the spec |

## Pre-flight (rehearsal, not the gate)

The pre-flight is one agent carrying the prompts of every lens among the 11 claims this revision changed: premise, mandate, implementability, sweep and mechanism_justification, so all four lenses. It reviewed the uncommitted v3 text, wrote no ledger row, and cost 172,073 tokens.

| Claims | Lenses | SURVIVED | UNPROVEN | REFUTED | Load-bearing UNPROVEN/REFUTED |
| --- | --- | --- | --- | --- | --- |
| 11 | refuter, compliance, sweeper, hardening | 11 | 0 | 0 | 0 |

It classified every mechanism the claims describe. Each refuses, except the declared opt-out (which passes over the missing tool, declared and printed) and the documented pre-push gaps (passed over).

| Pre-flight finding | Folded in as |
| --- | --- |
| F1 (important): the gaps pass over states detectable at the producer | §4.3 gives the written reasons the hook does not refuse them: dirty trees are ordinary, and the refs arrive on stdin, which hosts' hooks already consume (`cy:.githooks/pre-push:7`). The pull request's CI job checks a clean checkout of what merges |
| F2 (important): the opt-out's "CI runs it" overstates protection where CI is not required | The skip line says the pull request's CI job runs it. §4.3 says the opt-out is only as strong as what stops a red job from merging |
| F3: fixture branch name | §4.2: `git -c init.defaultBranch=main init` |
| F4: a second owner of the "selects no active" predicate | §4.3: `/acf-setup` runs the gate and reads its refusal instead |
| F5: governing-mandates header incomplete | Adds `## Declared, never defaulted`, `## Declared text decoding` and `## Post-merge` |
| F6: Windows local hooks without `PYTHONUTF8` | §4.3 tells Windows hosts to run the gate under `PYTHONUTF8=1` |
| F7: weaker citation for the `-c` identity | Cites `test_adr_citation_history.py:20` |
| F8: partial quote of `:249` | Rewritten whole |
| F9: the action is outside the doctrine's scope | §4.4 adds `.github/actions/` to the doctrine's opening scope |
| F10: wording of the first adopter's skip | §8 corrected; the snippet goes before its final `exit 0` |

## Sentence-type sweep

The whole v3 spec was re-swept with `grep -n -o -i -E '\b(every|all|only|none|no other|nothing|each|always|never|any)\b[^.|]{0,50}'`. The dispositions recorded for v2 stand. New or changed hits:

| # | Type | Hit | Disposition |
| --- | --- | --- | --- |
| T3 | Universal | "never committed to the repository" (§2.6) | Normative rule for environment owners, not a tree claim |
| T3 | Universal | "Unset, or any other value, means refuse" | Executed above |
| T3 | Universal | "Neither gap can pass a change into the default branch unseen" (§4.3) | Backed: the CI job runs on the pull request's clean checkout (§4.2, §2.3); conditional on the host merging only after reading or requiring the check, which §4.3 states |
| T6 | Attribution | `## Declared, never defaulted` records package defaults | Quoted section lines `:212-221` |
| T5 | Named hook | "selects no active" refusal precedes approval | `cli_check_diff.py:94-100` before `:102` |
