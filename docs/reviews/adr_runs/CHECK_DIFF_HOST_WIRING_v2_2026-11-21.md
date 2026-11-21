# Adversarial design review — full detail

Spec: `docs/design/CHECK_DIFF_HOST_WIRING.md` @ `59ad23a96965e328756c759b06a711a4b8be7be4`
Kinds: feature
Outcome: **BLOCKED**
Claims: 42 · Reviewers: 4 · Converged: 1

## Blocking reasons

- implementability claim C42 is UNPROVEN: The tree only shows the current repo-local hook with language: system, pass_filenames: false and stages: [pre-commit] (SKILL.md:222-226). Nothing in the repository records how pre-commit splits an `sh -c '...'` entry, that `pre-push` is a valid stage, or how `pre-commit install --hook-type pre-push` / default_install_hook_types behave. pre-commit is not installed in this environment (importing pre_commit fails), so I could not read its source. The claim is not load-bearing; the spec says the mechanism is unchanged if a detail differs.

## Absorptions

- PARTIAL_OVERLAP: '.github/actions/check-diff/action.yml (install steps 3-5)' shares responsibility "install the acf package and the TypeScript pack's node_modules" with .github/workflows/ci.yml:29-34 — The spec records three install recipes under '## Single point of definition': acf-setup SKILL.md:67-90, ci.yml:29-34 and the action. The shared verbs are 'pip install -e the repository root' and 'npm ci in plugins/arch-compliance/detectors/typescript'. They are kept apart on purpose: different environments, and the test job needs .[dev].
- IDENTICAL: '.github/actions/check-diff/action.yml (empty-base derivation)' shares responsibility 'derive the CI diff base ref' with .github/workflows/ci.yml:40 — The design already deletes the ci.yml:40 step and the acf-setup SKILL.md:245 sketch, so the action is the single owner.
- SUBSUMED: 'acf-setup step 8 pre-push guarded command' shares responsibility 'run acf-check-diff at the precommit site locally' with plugins/arch-compliance/skills/acf-setup/SKILL.md:216-227 — The guarded command replaces the pre-commit snippet in place; no sibling remains.

## Converged findings

- [2 reviewers: sweeper, compliance] This repository's own ## Post-merge CI bullet names `.github/workflows/ci.yml` (`test` job on `main`), but the design moves the gate run into the new `action` job and updates only the first adopter's ## Post-merge.
  - evidence: `config/architecture/ARCHITECTURE.md:330`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:20; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:99-104; pyproject.toml:39-40; plugins/arch-compliance/tests/test_packaging.py:71-115; ci.yml:29-34 (.github/workflows/ci.yml:29-34)`
- reasoning: parents[3] of plugins/arch-compliance/python/acf/detectors/typescript_bridge.py is plugins/arch-compliance, so _PACK_ROOT is plugins/arch-compliance/detectors/typescript. The scanner raises DetectorPackError when that directory or its node_modules is missing (:99-104). pyproject's package-data lists only judge_prompt.md and review/packs/*.yml (:39-40). There is no setup.py, setup.cfg or MANIFEST.in. A wheel puts acf under site-packages, where parents[3]/detectors/typescript does not exist, so TS scans refuse. Today's CI does exactly what the claim describes: an editable install plus npm ci (.github/workflows/ci.yml:29-34). One small overstatement: PYTHONPATH pointing at a source checkout would also work, as §4.2 itself does for the fixture. A source checkout is the real requirement.

#### C2 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:43-46; plugins/arch-compliance/python/acf/cli_check_diff.py:135-147; plugins/arch-compliance/python/acf/cli_check_diff.py:212-230; plugins/arch-compliance/python/acf/detectors/host.py:211-225`
- reasoning: With base set, _diff_args returns only '{base}...HEAD' (diff.py:45-46). changed_files and added_lines both use it, so when base equals HEAD the loop at cli_check_diff.py:142 iterates nothing, and build_artifact (:208-210) gets an empty list. The ratchet loop (:212-226) calls scan_ratchet(repo, baseline...) with no changed-file argument. scan_host_guards is called unconditionally (:228-230), and host.py:223-225 calls every active host guard row with tuple(changed_files) even when it is empty. Both kinds of whole-tree row therefore run on an empty diff, as claimed.

#### C3 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:106-108; plugins/arch-compliance/python/acf/cli_check_diff.py:119-121; plugins/arch-compliance/python/acf/approval.py:143-154; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:101-104; plugins/arch-compliance/python/acf/diff.py:33-38`
- reasoning: Caught GitError, AcfInputError, UnknownDetectorError and DetectorPackError print 'acf: {exc}' to stderr and return 1 (:106-108). A BLOCK finding also returns 1 (:119-121). The three named refusals each name what failed. A missing approval raises AcfInputError 'host detectors need approval: ...' (approval.py:150-154). A missing node_modules raises DetectorPackError with the npm ci hint (typescript_bridge.py:101-104). An unresolvable base raises GitError 'git diff ... failed' (diff.py:33-38). Two exits are not caught refusals: argparse usage errors exit 2, and an uncaught exception (for example a UnicodeDecodeError at :153/:189) exits 1 with a traceback and no 'acf:' line. Both are non-zero, so blocking on any non-zero exit still holds.

#### C4 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:145-153; plugins/arch-compliance/python/acf/cli_check_diff.py:189; plugins/arch-compliance/python/acf/repo.py:123-126; plugins/arch-compliance/python/acf/diff.py:43-46`
- reasoning: RepoTree.file returns the on-disk working-tree path, or None when the file is absent (repo.py:123-126). The gate skips a None path (:146-147) and otherwise reads the working-tree text (:153, :189). Added lines come from the committed diff '{base}...HEAD'. Both gaps follow: an uncommitted edit or deletion distorts or skips the scan, and HEAD is the checked-out branch whatever ref is pushed.

#### C5 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:274-284; .github/workflows/ci.yml:3-7; ran `git tag` and `git ls-remote --tags origin` in the worktree`
- reasoning: `git tag` printed nothing, and `git ls-remote --tags origin` (origin is github.com/IanDBallard/arch-compliance-for-superpowers) printed nothing and exited 0. Two in-tree sites agree. The Release discipline section names no tagging step (ARCHITECTURE.md:274-284), and CI has no tag trigger (ci.yml:3-7).

#### C6 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:223; plugins/arch-compliance/skills/acf-setup/SKILL.md:240-247; plugins/arch-compliance/skills/acf-setup/SKILL.md:258`
- reasoning: Line 223 is 'entry: acf-check-diff --mode staged --call-site precommit'. Line 245 runs acf-check-diff --base ... --call-site ci --trusted-checkout, in a sketch of a checkout step plus the run step only (240-247), with no install. Line 258 is the generic 'Install the acf package into the environment used by hooks/CI' and does not mention the TypeScript pack. The pack install appears only in step 4 (SKILL.md:81-88), for a developer machine.

#### C7 — UNPROVEN
- evidence: `searched the repository for any file recording where GitHub materialises a remote composite action (.github/, docs/, README.md); none exists`
- reasoning: The spec says this is GitHub platform behaviour with no repository record, and that holds: I found no in-tree evidence and cannot open GitHub's documentation with my tools. The claim is not load-bearing. The proposed step 1 check (§4.1) turns a false premise into a loud failure at the first adopter.

#### C8 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/detectors/eslint_rules.py:20-33 (git show 7313bca5); C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/detectors/eslint_rules.py:41-44; C:/Users/iball/Arduino/Projects/Cayenne/.github/workflows/ci.yml:94; C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/mandates.yml:139-166`
- reasoning: At 7313bca5 the imports are stdlib plus acf.detectors.host and acf.engine only (:20-29). ESLINT is cayenne-web/node_modules/eslint/bin/eslint.js (:33), run with `node` (:44), and it raises if missing (:41-42). ci.yml:94 sets node-version '22'. The registry's only host rows are two detection: ast rows (mandates.yml:139-147, 158-166). The other active rows are built-in empty_catch, explicit_any and no_build_artifacts (a built-in guard, not a host guard) plus llm/manual rows. There is no fail_loud_ratchet row and no host guard row, so pull_request alone follows from §2 decision 3.

#### C9 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/Cayenne/.github/workflows/ci.yml:6-7; C:/Users/iball/Arduino/Projects/Cayenne/.githooks/pre-push:1-18; ran `git grep -n -i acf 7313bca5 -- .github .githooks` (exit 1) and `gh api repos/IanDBallard/Cayenne/branches/main/protection` (404) and `gh api repos/IanDBallard/Cayenne/rules/branches/main``
- reasoning: At 7313bca5, .github and .githooks hold only ci.yml and pre-push, and git grep for 'acf' found nothing. pre-push:15 runs npm check/lint/test only. Branch protection returns 404 'Branch not protected'. The ruleset rules on main are deletion, non_fast_forward and pull_request (0 approvals), with no required_status_checks rule. The ci.yml:6-7 comment says the same.

#### C10 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:245; plugins/arch-compliance/skills/acf-setup/SKILL.md:249; plugins/arch-compliance/python/acf/cli_check_diff.py:102; plugins/arch-compliance/python/acf/approval.py:125-154; config/architecture/ARCHITECTURE.md:178-181`
- reasoning: Today's sketch passes --trusted-checkout (:245) and calls the workflow file the opt-in (:249). With the flag, digests is None and approval is never consulted (cli_check_diff.py:102). Without it, require_approval reads ~/.acf/approvals.json. A fresh runner has no entry, so with host rows the state is MISSING and the gate raises AcfInputError (approval.py:136-137, 150-154). That matches 'an approval the runner does not have'. ARCHITECTURE.md:178-181 states the same trust boundary.

#### C11 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-96; plugins/arch-compliance/python/acf/cli_check_diff.py:135-230; plugins/arch-compliance/python/acf/registry.py:164-174; plugins/arch-compliance/python/acf/enforcement.py:50-68; config/architecture/mandates.yml:135-140`
- reasoning: The scan path calls only built-in scanners and host_rows(detection='ast'/'guard'), and never acf.judge's LLM call. apply_registry keeps findings by mandate_id regardless of detection. Leakage is still impossible, because load_mandates refuses any active non-ast/guard row whose id is a built-in detector's reserved id (registry.py:164-174). This repository's active llm row (llm_fail_loud, partial, call_sites [ci, audit], mandates.yml:135-140) is therefore never run by acf-check-diff. load_gate_registry imports acf.judge for prompt ids only, and no key is read.

#### C12 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:261-272; plugins/arch-compliance/python/acf/diff.py:24-30; CLAUDE.md:37-39`
- reasoning: ARCHITECTURE.md:267 declares run_git (diff.py:24-30, text=True with no encoding) as debt. CLAUDE.md:37-39 runs the gate under PYTHONUTF8=1 until that is fixed. Both halves of the deferral premise hold.

#### C13 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:100-109; plugins/arch-compliance/python/acf/detectors/host.py:81-83; plugins/arch-compliance/python/acf/cli_check_diff.py:176-206`
- reasoning: load_host_detector builds a spec with spec_from_file_location and runs exec_module in the gate's own process (host.py:102-109). That load is reached from the gate's scan loop (cli_check_diff.py:177, 196). sys.path gets only the host root appended (host.py:81-83), so a host detector's third-party imports must resolve in the interpreter running acf-check-diff. One overstatement: an earlier step could make packages importable to the venv's python without installing into it, by pip install --target plus PYTHONPATH exported through GITHUB_ENV. 'Cannot reach' is therefore strong, though host-setup remains the cleaner single place.

### Unanchored findings

- **advisory**: The fixture script creates commits in a fresh repository on a GitHub runner, where no git user.name/user.email is configured, and the spec does not say the script supplies an identity (for example `git -c user.name=... -c user.email=...`). Otherwise `git commit` fails before the action runs.
  - evidence: `docs/design/CHECK_DIFF_HOST_WIRING.md:188-215`
- **advisory**: §2 decision 8 says a host 'cannot reach' the action's virtual environment from an earlier step, but an earlier step can export PYTHONPATH via GITHUB_ENV to a --target install, because host modules import in the gate's process with ordinary sys.path resolution; the rationale for host-setup is convenience, not impossibility.
  - evidence: `plugins/arch-compliance/python/acf/detectors/host.py:81-83`
- **advisory**: Decision 6 says the refusals the gate catches print 'acf:', but uncaught exceptions (for example UnicodeDecodeError from the working-tree read_text) also exit 1, with a traceback and no 'acf:' line; the pre-push design is unaffected because it blocks on any non-zero exit.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:153`

### Looked for but did not find

- setup.py, setup.cfg or MANIFEST.in, or any package-data entry that would ship detectors/typescript in a wheel
- a built-in whole-tree detector other than fail_loud_ratchet that would run on an empty --base diff
- any code path in cli_check_diff.py that invokes acf.judge or an LLM provider
- an 'acf' reference anywhere under cy: .github or .githooks at 7313bca5
- a required_status_checks rule in Cayenne's main branch ruleset
- a fail_loud_ratchet row or host guard row in cy: config/architecture/mandates.yml at 7313bca5
- third-party imports in acf/__init__.py or acf/exceptions.py that would stop the fixture script running without an install
- a pytest python_files setting or conftest under tests/ that would collect tests/action_fixture_host.py
- any git tag locally or on origin

## compliance

### Claim verdicts

#### C14 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:178-181; plugins/arch-compliance/skills/acf-setup/SKILL.md:249; plugins/arch-compliance/python/acf/cli_check_diff.py:102; docs/design/CHECK_DIFF_HOST_WIRING.md:280`
- reasoning: The doctrine says the diff gate runs host code with an approval or 'when the invocation passes `--trusted-checkout`'. The skill says 'in CI the workflow file is the opt-in. Only the CI sketch carries it. Never add it to the pre-commit snippet or to a command you run yourself.' The proposed pre-push command (spec:280) carries no `--trusted-checkout`, and the action passes the flag only when its input is `true`. At cli_check_diff.py:102 the flag simply skips require_approval, so the action's invocation is the same mechanism today's CI sketch uses. One caveat: the claim's wording 'appears only in the CI action' is broader than the design. Spec §4.3 (lines 321-323) keeps `--trusted-checkout` in the README and guide command blocks as a local command for this repository. That keeps the claim from being literally true, but it breaks no trust-boundary rule; see the advisory finding.

#### C15 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:276-281; scripts/check_installed_skills.py:18-23; pyproject.toml:3; plugins/arch-compliance/.claude-plugin/plugin.json:3`
- reasoning: The doctrine says 'A change to a skill's prose bumps the plugin version in plugin.json and pyproject.toml'. Both files are at 0.3.3 today, and the spec moves both to 0.3.4 (spec:338-339). GATE_SKILLS holds four trees (adversarial-design-review, responding-to-adversarial-review, post-merge-housekeeping, architecture-review), and acf-setup is not one of them. The byte-check therefore does not cover the changed skill, and no reinstall is owed under the rule as written. The spec also adds the tagging sentence to the section (spec:334-335).

#### C16 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:154-160; plugins/arch-compliance/python/acf/cli_check_diff.py:64-69`
- reasoning: Per the doctrine, `call_sites` is a closed vocabulary (`ci`, `precommit`, `hook`, `posttooluse`, `audit`), and `ci` and `precommit` are the diff sites. The CLI's `--call-site` choices are DIFF_CALL_SITES. The pre-push command runs `--call-site precommit`, which is an existing value, so nothing is added to the vocabulary. The new sentence (spec:331-333) only says which local hook may invoke the site. The 'selects no active' refusal (doctrine :159-160) is kept by the precondition check at spec:296-298.

#### C17 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:225-226; docs/design/CHECK_DIFF_HOST_WIRING.md:257; docs/design/CHECK_DIFF_HOST_WIRING.md:154; docs/design/CHECK_DIFF_HOST_WIRING.md:289-294`
- reasoning: The rule is 'Skill prose and runtime messages name no host repository, path or section'. The proposed acf-setup prose uses placeholders: `<version>`, `<default-branch>`, `npm ci --prefix web` as a generic example, and generic hook mechanisms (core.hooksPath, .husky, the pre-commit framework). The only repository it names is the plugin's own (`IanDBallard/arch-compliance-for-superpowers/.github/actions/check-diff`), which is the gate's source and not a host. The first adopter's paths (`cayenne-web`, `.githooks/pre-push`) appear only in spec §8. acf-setup has no prose-test row (doctrine :232-233), so this is held by review, as the spec implies.

#### C18 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:245-246; plugins/arch-compliance/skills/acf-setup/SKILL.md:210-249; docs/design/CHECK_DIFF_HOST_WIRING.md:188-190`
- reasoning: The rule reads 'An export has a live call site in the package, a hook or a skill. A test is not a consumer'. tests/action_fixture_host.py is a repository-level test script that the CI job runs. It exports nothing to the package, so the export rule does not reach it. The action itself is consumed by a skill: rewritten acf-setup step 8 prints the `uses:` line that hosts adopt (spec:257), which replaces the step-8 sketch in place.

#### C19 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:120-123; plugins/arch-compliance/python/acf/repo.py:21; plugins/arch-compliance/python/acf/repo.py:24; plugins/arch-compliance/python/acf/detectors/__init__.py:59-72; plugins/arch-compliance/python/acf/registry.py:130-147`
- reasoning: The doctrine says 'The repository-level `tests/` and `scripts/` follow the rule by importing the `acf.repo` constants' and that 'Executable skill snippets follow the rule too'. MANDATES_REL and ARCH_REL exist at repo.py:21 and :24, and the fixture takes them from there (spec:190-191). The package functions the spec names all exist: load_gate_registry (detectors/__init__.py:59), MandateRegistry.active with detector=/detection= keywords (registry.py:130-142) and host_rows (registry.py:144-147). load_gate_registry calls load_mandates, which never imports host code (doctrine :185), so step 8 can call it before any approval. The spec does not show the exact snippet, and the ratchet selection uses the string literal "fail_loud_ratchet" rather than FAIL_LOUD_RATCHET_DETECTOR_ID, as cli_check_diff.py:212 does. Both are minor and do not break the rule.

#### C20 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:290-302; .github/workflows/ci.yml:39-40; plugins/arch-compliance/skills/acf-setup/SKILL.md:245`
- reasoning: The lifted rule requires 'exactly one canonical implementation that every call site consumes', and the section records breaches as 'recorded not hidden'. Lines :298-302 set a precedent for a breach kept apart with a stated reason (the two glob dialects). Today the CI base-ref expression `origin/${{ github.base_ref || 'main' }}` exists twice, at ci.yml:40 and SKILL.md:245. The design removes ci.yml:39-40 and replaces the sketch, which leaves the action as the one CI derivation. The pre-push `origin/<default-branch>` is a local derivation for another environment. The three install copies are recorded in the section with a reason, which fits the section's form. README.md:56 and docs/guides/SUPERPOWERS_COMPLEMENT.md:81 also carry `pip install -e ".[dev]"`, but they are the developer-machine recipe, the same environment as step 4.

#### C21 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:191-193; config/architecture/ARCHITECTURE.md:212-221; docs/design/CHECK_DIFF_HOST_WIRING.md:147-154`
- reasoning: The section's rule covers the ADR gate's host values (adr.yml), the review's (review.yml) and the post-merge refinements: 'no default stands in for a missing declaration'. The action inputs (spec:147-154) are none of these. They are not host declarations that a gate reads from config/architecture/, so the rule is not breached. The section does keep a practice of recording package defaults that sit outside the rule (:212-221, for example resolve_repo's fallback to the process directory). The action's `repo: '.'` and `trusted-checkout: 'true'` are close analogues and are not recorded there; see unstated_mandates.

#### C22 — UNPROVEN
- evidence: `config/architecture/ARCHITECTURE.md:251-254; docs/design/CHECK_DIFF_HOST_WIRING.md:73-74; docs/design/CHECK_DIFF_HOST_WIRING.md:368`
- reasoning: The doctrine says a tree claim 'is not load-bearing on "every", "all", "only", "complete", "untouched" or "no second" unless a recipe that a reader can re-run backs the quantifier'. Most of the spec's negatives carry receipts. Examples: no tags (spec:368, git tag), no python_files (I read pyproject.toml:23-25 and it holds), acf-setup is not byte-checked (check_installed_skills.py:18-23). C22 itself, though, is an unbacked universal about the spec, and at least one tree negative has no recipe: 'GitHub platform behaviour, which no file in this repository records' (spec:73-74). That negative is not load-bearing, because §4.1 step 1 guards the premise either way, so the doctrine is not violated. The claim's 'makes no unbacked … claim' still cannot be established as stated.

### Unanchored findings

- **advisory**: Spec §4.3 keeps `acf-check-diff --base origin/main --call-site ci --trusted-checkout` in README and the guide as 'a local command for this repository'. That contradicts C14's 'appears only in the CI action' and sits against acf-setup's 'Never add it … to a command you run yourself'. It is harmless here because this repository has no host rows, but the trusted invocation should be framed as CI-only or the flag dropped from the local example.
  - evidence: `README.md:58`
- **advisory**: The plugin's own `## Post-merge` CI bullet says '`.github/workflows/ci.yml` (`test` job on `main`)', but the design moves the diff gate run out of the `test` job into the new `action` job of the same workflow. The parenthetical goes stale, and the spec updates the first adopter's `## Post-merge` but not this repository's.
  - evidence: `config/architecture/ARCHITECTURE.md:330`
- **advisory**: The action's defaults (`repo: '.'`, `trusted-checkout: 'true'`, the base fallback to the default branch) are not recorded under `## Declared, never defaulted`. That section records package defaults that sit outside its rule (resolve_repo's directory fallback, the judge's default provider), and the trust-relevant `trusted-checkout: true` is the closest analogue.
  - evidence: `config/architecture/ARCHITECTURE.md:212-216`
- **advisory**: C22 is itself an unbacked completeness claim, and the spec carries at least one recipe-less tree negative ('which no file in this repository records'). It is not load-bearing, but it should be deleted or given a recipe per the T3 rule.
  - evidence: `docs/design/CHECK_DIFF_HOST_WIRING.md:73`

### Looked for but did not find

- ## High-frequency misses / stdlib mixin on an exception class: the design adds no exception classes, so not touched
- ## High-frequency misses / subprocess text call without an encoding: no new runtime code in plugins/arch-compliance/python or hooks; the fixture script is under tests/, which ARCHITECTURE.md:265-266 places outside the decoding rule's runtime scope
- ## High-frequency misses / check re-implemented in a skill: step 8's registry checks consume load_gate_registry, MandateRegistry.active and host_rows (registry.py:130-147); the only residue is a string literal for the ratchet detector id, which is minor
- ## High-frequency misses / host name in skill prose: the acf-setup snippets use placeholders and name only the plugin repository; see C17
- ## Fail loud: the pre-push skip prints to stderr and only applies when the command is absent; any non-zero exit blocks the push (spec:279-283); the action's tee uses pipefail (spec:180-181), so not a swallowed failure
- ## POSIX paths: the fixture writes no serialized path fields (the mandate row holds no paths), so not touched
- ## Build artifacts: the virtual environment lives under $RUNNER_TEMP and is never staged, so not touched
- ## Host detectors and call sites / Built-in contracts: the fixture row (empty_catch, fail-loud.empty-catch, [ci]) matches typescript_bridge.py:16 and declares a Tier-1 site, so it conforms
- ## Frozen ledger format: no ledger fields change, so not touched
- ## Declared text decoding: invoked by the spec only to justify the Windows non-goal, with no new runtime subprocess
- ## Scoped refactor: README, guide and dependabot edits follow directly from replacing the step-8 snippets, so in scope

### Unstated mandates

- ## Post-merge — the post-merge CI bullet names `.github/workflows/ci.yml` (`test` job on `main`) (ARCHITECTURE.md:330), and the design moves this repository's gate run into a new `action` job; the spec revises the first adopter's ## Post-merge but says nothing about this repository's
- ## Declared, never defaulted — not breached, but the section records package defaults outside its rule (ARCHITECTURE.md:212-221), and the action ships analogous defaults (`repo: '.'`, `trusted-checkout: 'true'`, the base fallback) that the spec neither lists nor records

## sweeper

### Claim verdicts

#### C23 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-108; plugins/arch-compliance/python/acf/diff.py:33-45; plugins/arch-compliance/python/acf/cli_check_diff.py:119-121`
- reasoning: I looked for any code-judging decision in the action that the gate does not already make. Every outcome about code comes from cli_check_diff.main. It selects the active ast/guard rows and refuses an empty selection (:94-100). Git failures become GitError and are caught as the 'acf:' refusal (diff.py:33-39 into cli_check_diff.py:106-108). BLOCK findings decide exit 1 (:119-121). The action's own stops (step 1 file check, Windows, the trusted-checkout value check, a host-setup exit code, the shallow check) inspect the environment, not code, and tee+pipefail keeps the gate's exit status. On the shallow stop: with actions/checkout at depth N>0 the default base origin/<base_ref> is not fetched, so `git diff origin/X...HEAD` fails in _git and becomes GitError. The stop therefore pre-empts a refusal the gate already makes. There is one narrow exception, filed as an advisory finding below.

#### C24 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:18; plugins/arch-compliance/python/acf/cli_check_diff.py:44-51; plugins/arch-compliance/python/acf/cli_check_diff.py:64-68`
- reasoning: DIFF_CALL_SITES is exactly {ci, precommit} (registry.py:18), and --call-site draws its choices from it (cli_check_diff.py:67). The pre-push command uses the existing 'precommit' value and the existing --base flag (cli_check_diff.py:44-51), whose diff scope is the single three-dot form in diff.py:42-45. I grepped the package for call-site literals and found no new spelling. The doctrine sentence §4.4 adds ('precommit is the local git-hook site') redefines no vocabulary. The closed vocabulary stays at config/architecture/ARCHITECTURE.md:154-158.

#### C25 — SURVIVED
- evidence: `.github/workflows/ci.yml:29-40; plugins/arch-compliance/skills/acf-setup/SKILL.md:240-247`
- reasoning: Glob for action.yml/action.yaml/*.sh/install*/setup* across the tree returned nothing. Grep for 'workflow_call' found no reusable workflow outside docs/design, docs/plans and the excluded docs/reviews. The only CI invocations of the gate are this repository's self-check (ci.yml:39-40, with install at :29-34) and the acf-setup step 8 sketch (SKILL.md:240-247). The sketch is a paste template with no install step (the only install text is the generic reminder at :258). So nothing installs and runs acf-check-diff for a host in CI today.

#### C26 — SURVIVED
- evidence: `.github/workflows/ci.yml:3-7; .github/workflows/ci.yml:40; config/architecture/mandates.yml:8-94`
- reasoning: The workflow triggers only on push to main and pull_request to main (ci.yml:3-7). Today's derivation, `github.base_ref || 'main'` (:40), therefore yields origin/<base_ref> on pull requests and origin/main on pushes. The action's empty-base rule yields origin/<base_ref>, else origin/<default_branch>, which is main here, so the results match on every trigger. Grep for base_ref/default_branch found only one other CI derivation, the acf-setup sketch (SKILL.md:245), which §4.3 replaces. The pre-push '<default-branch>' is a local site, not CI. Defaulting trusted-checkout to true does not change coverage for this repository: mandates.yml has no host rows (every ast/guard detector is a built-in id with no ':'), so --trusted-checkout is inert. The TypeScript pack is installed by the action's step 5, as by ci.yml:32-34.

#### C27 — REFUTED
- evidence: `config/architecture/ARCHITECTURE.md:330; plugins/arch-compliance/skills/acf-setup/SKILL.md:249; plugins/arch-compliance/skills/acf-setup/SKILL.md:253; README.md:62`
- reasoning: I redid the sweep by behaviour, grepping for pre-commit|precommit|acf-check-diff|ci.yml|workflow file|.github/ outside docs/design, docs/plans and docs/reviews. It finds stale wiring descriptions the claim's list omits. (1) ARCHITECTURE.md:330 '## Post-merge' declares 'Post-merge CI workflows: .github/workflows/ci.yml (test job on main)'. The design moves this repository's self-gate out of the test job into the new action job, yet §8 updates the first adopter's equivalent post-merge bullet and leaves this one alone. (2) acf-setup SKILL.md:249 still says 'Only the CI sketch carries it. Never add it to the pre-commit snippet'. §4.3 says only that the paragraph 'keeps its rule and names the action's input'; it renames neither the sketch nor the snippet. (3) SKILL.md:253, in the upgrading section, says 'each ast/guard row the host wants checked in pre-commit'. §4.3 rewrites only the :254 phrase and the :258 reminder in that section. (4) README.md:62 describes the CI invocation as '--trusted-checkout, which CI workflows pass', and SUPERPOWERS_COMPLEMENT.md:87 says the same. §4.3 touches only the command blocks at README.md:53-58 and SUPERPOWERS_COMPLEMENT.md:78-83. The release notes at README.md:136 and :141-142 are historical and may defensibly stay. The listed instances are correct, but the list is not the whole population.

### Unanchored findings

- **advisory**: This repository's own '## Post-merge' declaration names the CI 'test job on main' as the post-merge workflow. The design moves the self-gate run into a new 'action' job without updating that declaration, while §8 does update the first adopter's equivalent bullet. The design is internally inconsistent here and leaves a stale host declaration that post-merge-housekeeping reads.
  - evidence: `config/architecture/ARCHITECTURE.md:330`
- **advisory**: The acf-setup prose still says 'Only the CI sketch carries it. Never add it to the pre-commit snippet' (:249) and 'rows the host wants checked in pre-commit' (:253). §4.3 does not list these for rewording, so after the change the skill still names a CI sketch and a pre-commit snippet it no longer prints.
  - evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:249`
- **advisory**: The shallow-clone stop (§4.1 step 7) fires whenever --is-shallow-repository is true. A host that fetches the base itself at partial depth with the merge base reachable would pass acf-check-diff but be stopped by the action. In that narrow case the claim that the stop 'only improves the message for a refusal acf-check-diff already makes' does not hold.
  - evidence: `plugins/arch-compliance/python/acf/diff.py:42-45`

### Looked for but did not find

- An existing composite action, reusable workflow or install script for hosts: Glob for **/{action.yml,action.yaml,*.sh,install*,setup*} and Grep for 'workflow_call' (none)
- A second CI base-ref derivation that survives the change: Grep for 'base_ref|default_branch|--base' (only ci.yml:40 and acf-setup SKILL.md:245, both replaced; post-merge-housekeeping's default_branch is a git-side derivation for verification, a different job)
- Host rows in this repository's registry that the trusted-checkout default would newly activate: Grep for 'detector:' in config/architecture/mandates.yml (built-in ids only)
- A second call-site spelling introduced by the pre-push step: Grep for 'CALL_SITES|precommit' in plugins/arch-compliance/python/acf (single vocabulary at registry.py:17-20)
- Code-judging logic outside cli_check_diff.main that the action could duplicate: read cli_check_diff.py:36-231 and diff.py:17-57

### Relationships

- PARTIAL_OVERLAP: `.github/actions/check-diff/action.yml (install steps 3-5)` — responsibility `install the acf package and the TypeScript pack's node_modules` — existing `.github/workflows/ci.yml:29-34`
  - resolution: The spec records three install recipes under '## Single point of definition': acf-setup SKILL.md:67-90, ci.yml:29-34 and the action. The shared verbs are 'pip install -e the repository root' and 'npm ci in plugins/arch-compliance/detectors/typescript'. They are kept apart on purpose: different environments, and the test job needs .[dev].
- IDENTICAL: `.github/actions/check-diff/action.yml (empty-base derivation)` — responsibility `derive the CI diff base ref` — existing `.github/workflows/ci.yml:40`
  - resolution: The design already deletes the ci.yml:40 step and the acf-setup SKILL.md:245 sketch, so the action is the single owner.
- ADJACENT: `tests/action_fixture_host.py` — responsibility `build a throwaway git repository with a mandates.yml and a planted or clean change on a branch` — existing `plugins/arch-compliance/tests/test_diff_cli.py:28-39`
  - resolution: None required; see the justification.
  - non-merge: The existing _init_repo is a private pytest helper called in-process. The new script is a standalone CLI that a GitHub Actions job runs before the installed action exists, and it must run with only acf.repo on PYTHONPATH. Importing a test module from CI scaffolding would make a test file a dependency. The spec states none of this, so this is the reviewer's justification, not the design's.
- SUBSUMED: `acf-setup step 8 pre-push guarded command` — responsibility `run acf-check-diff at the precommit site locally` — existing `plugins/arch-compliance/skills/acf-setup/SKILL.md:216-227`
  - resolution: The guarded command replaces the pre-commit snippet in place; no sibling remains.

### Two-owner counts

- install acf package and TypeScript pack: 3

### Document conflicts

- `config/architecture/ARCHITECTURE.md:330` (contradicts): **Post-merge CI workflows:** `.github/workflows/ci.yml` (`test` job on `main`).

## hardening

### Claim verdicts

#### C28 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:241; .github/workflows/ci.yml:13`
- reasoning: The current CI sketch is a pasted template that has already drifted. It pins actions/checkout@v4 (SKILL.md:241), while this repository's own CI is on @v7 (ci.yml:13), so the 'templates drift' premise holds in the tree. A composite action is one versioned artifact called from inside the host's own job, so the host keeps its triggers and runner. The comparison with a reusable workflow (which is called at job level) is a design argument and contradicts nothing in the tree.

#### C29 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:20; pyproject.toml:39-40`
- reasoning: The TS bridge finds its pack relative to its own source file (typescript_bridge.py:20), and package-data ships no detectors/typescript (pyproject.toml:39-40). So the action really does need the whole tree at $GITHUB_ACTION_PATH/../../.. (parents of .github/actions/check-diff). Step 1 only tests that pyproject.toml and the pack's package.json exist and stops with both paths named. It repairs nothing and does no second checkout. A file-existence check is directly buildable. The repository has no .gitattributes, so no export-ignore rule could strip either file from a tag archive.

#### C30 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:102-109; C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/detectors/eslint_rules.py:33`
- reasoning: Host detectors are loaded with spec_from_file_location and exec_module inside the gate's own process (host.py:102-109). Their imports therefore resolve from the interpreter running acf-check-diff, which is the action's venv, and only a step inside the action, with that venv's bin first on PATH, can install into it. The first adopter's detector also needs the host's node_modules (eslint_rules.py:33). The spec admits Node files from earlier steps would also persist and calls host-setup the documented single place for them, which is accurate.

#### C31 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:106-108; plugins/arch-compliance/python/acf/cli_check_diff.py:119-121`
- reasoning: A caught refusal prints 'acf: ...' and returns 1 (lines 106-108). Any BLOCK finding also returns 1 (lines 119-121). The exit code cannot tell them apart, so blocking on any non-zero exit is the only rule that avoids parsing stderr. The skip branch only fires when the tool is absent, and CI is the backstop then.

#### C32 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:142-147; plugins/arch-compliance/python/acf/cli_check_diff.py:208-230; plugins/arch-compliance/python/acf/detectors/host.py:220-225`
- reasoning: With an empty three-dot diff, the per-file loop (lines 142-147) and build_artifacts (lines 208-210, which iterate over `changed`) see nothing. The fail_loud_ratchet rows scan the whole tree (lines 212-226). Host guard rows are loaded and called even with an empty changed_files tuple (cli_check_diff.py:228-230, host.py:220-225). So those two kinds of row are the only ones a push run can exercise. On a push, base resolves to origin/<default>, and merge-base(origin/<default>, HEAD) is HEAD even if origin has moved on, so the diff is empty.

#### C33 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:33-39; plugins/arch-compliance/python/acf/cli_check_diff.py:106-108`
- reasoning: _git raises GitError carrying git's own stderr on any non-zero status (diff.py:33-39), and changed_files calls it (diff.py:56). The CLI catches GitError and exits 1 (cli_check_diff.py:106-108). Git's message ('no merge base' or 'unknown revision') never mentions fetch-depth. The shallow-clone stop only adds a clearer message before that refusal and repairs nothing.

#### C34 — SURVIVED
- evidence: `scripts/check_installed_skills.py:7-8; scripts/check_installed_skills.py:21`
- reasoning: post-merge-housekeeping is one of the byte-checked skill trees (check_installed_skills.py:7-8, :21). Adding a tagging step to it would be a byte-checked edit that every user must reinstall, as the claim says. A forgotten tag fails loudly when the host's uses: line cannot resolve. That is GitHub platform behaviour, and it fails at the host rather than silently.

#### C35 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:50-61; plugins/arch-compliance/python/acf/detectors/__init__.py:44-47; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:15-16; plugins/arch-compliance/python/acf/cli_check_diff.py:94-102; plugins/arch-compliance/python/acf/diff.py:42-45; plugins/arch-compliance/python/acf/cli_check_diff.py:234-239`
- reasoning: The fixture row has every required Mandate field (registry.py:50-61); auditor and params default to None. languages: typescript is a legal Language. _check_builtin passes because empty_catch maps to mandate id fail-loud.empty-catch (typescript_bridge.py:15-16), and the contract serves TIER1 sites, which include ci (detectors/__init__.py:44-47). The llm-prompt check skips non-llm rows. arch_anchor is not checked on the gate's load path. The active ast row at ci avoids the 'selects no active' refusal (cli_check_diff.py:94-100). Trusted checkout or no host rows means no approval lookup (cli_check_diff.py:102). `--base main` becomes 'main...HEAD' (diff.py:42-45), which resolves against the local branch with no remote. emptyCatch.ts:12-27 emits BLOCK for a catch with no statements. _print_human writes 'BLOCK fail-loud.empty-catch path:line', which the grep in §4.2 matches (cli_check_diff.py:239), and exit is 1. The clean change prints 'No findings.' and exits 0.

#### C36 — SURVIVED
- evidence: `pyproject.toml:23-25; plugins/arch-compliance/python/acf/repo.py:10-15`
- reasoning: pyproject.toml:23-25 sets testpaths and pythonpath but no python_files. The repository root has no pytest.ini, setup.cfg or tox.ini, and tests/ has no conftest.py. So action_fixture_host.py matches neither default pattern and is not collected. repo.py imports only os, re, collections.abc, pathlib and acf.exceptions (lines 10-15). exceptions.py has no imports, and acf/__init__.py is 0 bytes. So PYTHONPATH=plugins/arch-compliance/python is enough to import acf.repo without an install.

#### C37 — SURVIVED
- evidence: `pyproject.toml:18-21; pyproject.toml:31-36; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:20; plugins/arch-compliance/python/acf/detectors/host.py:102-109`
- reasoning: project.scripts declares acf-check-diff (pyproject.toml:20), so the venv gets bin/acf-check-diff. packages.find points at plugins/arch-compliance/python, and the comment at pyproject.toml:34-36 records that an editable install makes Path(__file__) resolve into the source tree. parents[3] of acf/detectors/typescript_bridge.py is plugins/arch-compliance, so _PACK_ROOT is plugins/arch-compliance/detectors/typescript, where step 5 runs npm ci. Host modules are exec'd in the gate's interpreter (host.py:102-109), so packages that host-setup installs with the venv's pip first on PATH are importable.

#### C38 — SURVIVED
- evidence: `.github/workflows/ci.yml:3-7; C:/Users/iball/Arduino/Projects/Cayenne/.github/workflows/ci.yml:580-587`
- reasoning: None of these platform behaviours is recorded in the tree, so I traced whether the design turns each one into a red job instead. setup-python and setup-node run on every action run. continue-on-error plus outcome is checked by the step after the planted run, which needs outcome==failure and the BLOCK line (spec §4.2). If pipefail were lost, run 1 would report success and that check would fail. The cy file (lines 580-587) records that a step with no shell: runs as `bash -e` without pipefail, so the action stating pipefail explicitly is correct. The workflow fires on push to main as well as pull_request (ci.yml:3-7), so the empty-base_ref / default_branch path is exercised by the push run. The caveat is that this run happens after merge (see the unanchored advisory). is-shallow 'true' is never exercised, but a wrong answer there only degrades the message, because the GitError stays authoritative.

#### C39 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/Cayenne/.githooks/pre-push:5-11; plugins/arch-compliance/python/acf/cli_check_diff.py:106-121`
- reasoning: In POSIX sh, a failure on the left of `||` does not trigger set -e, so `|| exit 1` runs and ends the hook. A failing `command -v` in an if-condition also does not trigger set -e, so the else branch only warns and the push continues. In cy, the hook has `set -e` and the docs-only skip exits 0 at lines 7-11 at top level, so the snippet goes at top level after line 11, which matches the claim. 'Wherever the snippet sits' is broader than the spec's own top-level guidance (a `( ... )` subshell would swallow the exit). The spec text tells hosts to use top level, so the placement works as specified.

#### C40 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/__init__.py:59-72; plugins/arch-compliance/python/acf/registry.py:130-147`
- reasoning: load_gate_registry(repo, mandates_path) exists and is exported (detectors/__init__.py:59-75), and it is the same loader the gate uses (cli_check_diff.py:93). MandateRegistry.active takes call_sites plus keyword-only detector= and detection= filters (registry.py:130-142). host_rows(call_sites, detection=) filters active rows by is_host_row (registry.py:144-147). Each named call has its hook.

#### C41 — SURVIVED
- evidence: `config/architecture/mandates.yml:94; .github/workflows/ci.yml:13-15; plugins/arch-compliance/python/acf/cli_check_diff.py:101-102`
- reasoning: Every active ast/guard row in this repository's mandates.yml names a built-in detector id with no ':', so there are no host rows, and the approval/trusted path selects nothing (cli_check_diff.py:101-102). The fail_loud_ratchet row is unenforced (mandates.yml:94), so a push run with an empty diff scans nothing and passes. The existing job already checks out with fetch-depth 0 (ci.yml:13-15), and the spec gives the new job the same. With base empty on a PR, the action derives origin/<base_ref>, the same as today's ci.yml:40.

#### C42 — UNPROVEN
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:226`
- reasoning: The tree only shows the current repo-local hook with language: system, pass_filenames: false and stages: [pre-commit] (SKILL.md:222-226). Nothing in the repository records how pre-commit splits an `sh -c '...'` entry, that `pre-push` is a valid stage, or how `pre-commit install --hook-type pre-push` / default_install_hook_types behave. pre-commit is not installed in this environment (importing pre_commit fails), so I could not read its source. The claim is not load-bearing; the spec says the mechanism is unchanged if a detail differs.

### Unanchored findings

- **advisory**: tests/action_fixture_host.py makes commits on a GitHub runner with no git identity configured. The spec does not say the script must set user.name/user.email (and commit.gpgsign=false), as the repository's existing git-fixture tests do, so a literal implementation fails at the first commit.
  - evidence: `plugins/arch-compliance/tests/test_diff_cli.py:32-33`
- **advisory**: The empty-base_ref branch (fallback to github.event.repository.default_branch) is only exercised by the action job's push-to-main run, which happens after merge. A hand tag placed right after merge could precede that run's result, so 'exercised before any tag' holds only if the tagger waits for main's CI.
  - evidence: `.github/workflows/ci.yml:3-7`
- **advisory**: Spec §4.3 says that inside a function `exit` leaves only that scope. In POSIX sh, exit in a function terminates the whole shell (only a `( ... )` subshell confines it). The guidance errs on the safe side, but the stated reason is wrong.
  - evidence: `docs/design/CHECK_DIFF_HOST_WIRING.md:286-288`

### Looked for but did not find

- Conditional push trigger (§2 decision 3): workflow configuration, not a mechanism handling invalid state; the empty-diff premise was checked against cli_check_diff.py:142-230
- CI assertion steps after the planted and clean runs: test checks, not runtime mechanisms; ordering was checked (the check reads acf-check-diff.txt before run 2 overwrites it)
- Tag rule added to Release discipline: a process rule, not a code mechanism
- Any repair-on-load, normalizer or retry in the action: none. Every added stop refuses before the gate, and the gate's own refusals stay authoritative
- Host guard rows in the first adopter's registry: both cy host rows are detection: ast (cy mandates.yml:141, :160), so pull_request alone is correct
- export-ignore that could strip pyproject.toml or the pack from a tag archive: no .gitattributes in the repository
- pytest python_files override that would collect action_fixture_host.py: none in pyproject.toml, setup.cfg, pytest.ini, tox.ini or tests/conftest.py

### Mechanism traces

- **step 1 self-check of $GITHUB_ACTION_PATH/../../..**
  - invalid state: not (exists(ACTION_PATH/../../../pyproject.toml) and exists(ACTION_PATH/../../../plugins/arch-compliance/detectors/typescript/package.json))
  - producer: `pyproject.toml:39-40 (package-data omits detectors/typescript, so the action depends on the runner-delivered tree; the delivery layout itself is external GitHub platform behaviour)`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: That location holding this repository at the pinned ref is GitHub platform behaviour, which no file in this repository records. The design therefore does not rely on it silently
  - spec citation: `docs/design/CHECK_DIFF_HOST_WIRING.md:158-161`
- **Windows runner stop**
  - invalid state: runner.os == 'Windows'
  - producer: `plugins/arch-compliance/python/acf/diff.py:24-30 (run_git uses text=True with no declared encoding, so the gate is not Windows-safe; the runner choice is the host workflow's)`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: Supporting them would take more than a virtual-environment layout branch: the diff gate's git runner does not declare its text encoding
  - spec citation: `docs/design/CHECK_DIFF_HOST_WIRING.md:162`
- **trusted-checkout input validation**
  - invalid state: inputs.trusted-checkout not in {'true','false'}
  - producer: `host workflow `with:` value (external input); action inputs are strings by platform, so rung 1 is unavailable`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/CHECK_DIFF_HOST_WIRING.md:151`
- **host-setup non-zero exit stops the action**
  - invalid state: exit_status(host-setup command) != 0
  - producer: `host-supplied command (external); the dependency it installs is needed because host.py:102-109 imports host modules in-process`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/CHECK_DIFF_HOST_WIRING.md:169-172`
- **shallow-clone stop naming fetch-depth: 0**
  - invalid state: git -C <repo> rev-parse --is-shallow-repository == 'true' (merge base with <base> possibly absent)
  - producer: `host workflow's actions/checkout without fetch-depth: 0 (external default depth 1); the authoritative refusal is plugins/arch-compliance/python/acf/diff.py:33-39`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: This only improves the message: without it, the missing merge base already makes acf-check-diff refuse with a GitError, and that refusal stays the authoritative one
  - spec citation: `docs/design/CHECK_DIFF_HOST_WIRING.md:173-177`
- **pre-push skip when acf-check-diff is absent**
  - invalid state: `command -v acf-check-diff` fails in the hook's environment
  - producer: `plugins/arch-compliance/skills/acf-setup/SKILL.md:69-80 (install step not run on that machine, e.g. a cloud session or fresh clone)`
  - rung 5 (highest applicable 3); repairs=True
  - hardening rejected because: A cloud session or a fresh clone may not have acf-check-diff. The pre-push step then prints one line saying the check was skipped and that CI runs it, and lets the push continue.
  - spec citation: `docs/design/CHECK_DIFF_HOST_WIRING.md:278-284`
- **/acf-setup registry pre-checks before printing the pre-push command and the workflow**
  - invalid state: registry.active({site}, detection='ast') + registry.active({site}, detection='guard') == [] for site in {precommit, ci}
  - producer: `host's config/architecture/mandates.yml (profile rows declaring no precommit, per plugins/arch-compliance/skills/acf-setup/SKILL.md upgrade note); the gate's own refusal is plugins/arch-compliance/python/acf/cli_check_diff.py:94-100`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/CHECK_DIFF_HOST_WIRING.md:296-305`

## Claims

- **C1** [premise] [load-bearing]: The TypeScript detector bridge locates its Node scanner relative to its own source file (_PACK_ROOT = Path(__file__).resolve().parents[3] / 'detectors' / 'typescript') and pyproject.toml's package data ships no detectors/typescript (pyproject.toml:39-40), so a wheel install cannot scan .ts/.tsx files; the runner needs an editable install from a source checkout plus `npm ci` in plugins/arch-compliance/detectors/typescript.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:20`
- **C2** [premise] [load-bearing]: With --base, the changed-file list and added lines are the three-dot diff (diff.py:43-46), so on a push where origin/<default> is HEAD every per-file check sees nothing; but an active fail_loud_ratchet row scans the tree against its baseline regardless of the diff (cli_check_diff.py:212-226) and host guard rows are called whatever the diff holds (:228-230). This is why the snippet triggers on pull_request and /acf-setup adds a push trigger only for hosts with either kind of row active at ci.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:212-230`
- **C3** [premise] [load-bearing]: acf-check-diff returns 1 for a BLOCK finding (:119-121) and for a caught refusal alike (:106-108); the refusals it catches print a line beginning `acf:`, and a missing approval, a TypeScript pack without `npm ci` and an unresolvable base each say what failed. The pre-push step blocks on every non-zero exit on the strength of this; telling a refusal from a finding would need stderr parsing.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:106-108`
- **C4** [premise]: Under --base the gate takes changed files and added lines from the committed diff but reads each changed file from the working tree (:145, :153, :189), so in a local pre-push run an uncommitted edit can move a reported line, hide a committed violation, or, when the file is deleted, skip it; and the diff is of the checked-out branch, so `git push origin <another-branch>` checks the wrong commits. The spec states both as the pre-push step's known gaps.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:145`
- **C5** [premise]: The plugin repository has no git tags locally or on origin today (`git tag` and `git ls-remote --tags origin` print nothing).
  - spec citation: `None`
- **C6** [premise]: /acf-setup step 8 today prints a pre-commit entry running `acf-check-diff --mode staged --call-site precommit` (:223) and a CI sketch running `acf-check-diff --base ... --call-site ci --trusted-checkout` (:245) with no install step; the nearest install text (:258) is a generic reminder to install the acf package into the environment used by hooks/CI and says nothing about the TypeScript pack.
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:210-249`
- **C7** [premise]: GitHub runs a composite action referenced as owner/repo/path@ref from a copy of that repository at that ref, so the directory three levels above $GITHUB_ACTION_PATH is the plugin repository root. This is platform behaviour no repository file records. Flagged not load-bearing because the design does not depend on it silently: the action's step 1 stops, naming both paths, unless that directory holds pyproject.toml and plugins/arch-compliance/detectors/typescript/package.json; if the premise were false the design would be the same and would fail loudly at the first adopter's run.
  - spec citation: `None`
- **C8** [premise] [load-bearing]: The first adopter's (Cayenne, at 7313bca5) host detectors run the ESLint at cayenne-web/node_modules/eslint/bin/eslint.js, which nothing in the action installs, and import only the standard library and acf (eslint_rules.py:20-29); Cayenne's CI uses Node '22' (cy:.github/workflows/ci.yml:94). Its registry has no fail_loud_ratchet row and no host guard row, so its workflow triggers on pull_request alone, with host-setup `npm ci --prefix cayenne-web`.
  - spec citation: `cy:config/architecture/detectors/eslint_rules.py:33`
- **C9** [premise]: The first adopter's CI does not run acf-check-diff today (no 'acf' match under .github or .githooks at 7313bca5), and its main branch has no required status checks.
  - spec citation: `cy:.github/workflows/ci.yml:6-7`
- **C10** [premise] [load-bearing]: Today's /acf-setup CI sketch already passes --trusted-checkout (SKILL.md:245), so running a fork pull request's own host detectors under it is exposure the action does not add; a host that does not want it sets trusted-checkout: false, and its host rows then need an approval the runner does not have.
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:245`
- **C11** [premise] [load-bearing]: Deferral (non-goal): acf-check-diff selects only ast and guard rows, never llm rows, so the action needs no LLM provider key and the LLM rows stay out of the automatic gates without change.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-96`
- **C12** [premise]: Deferral (non-goal): Windows runners are out of scope; supporting them would take more than a venv-layout branch, because the diff gate's git runner does not declare its text encoding (ARCHITECTURE.md `## Declared text decoding`) and the repository's Windows note runs the gate under PYTHONUTF8=1.
  - spec citation: `None`
- **C13** [premise] [load-bearing]: The gate imports a host detector module into its own process (spec_from_file_location / exec_module, host.py:102-109), so a host detector's third-party Python packages must be installed in the environment that runs acf-check-diff, the action's own venv, which a host cannot reach from a step before the action. This is the reason for the host-setup input (run after the action's setup, venv bin first on PATH).
  - spec citation: `plugins/arch-compliance/python/acf/detectors/host.py:102-109`
- **C14** [mandate] [load-bearing]: Trust boundary: --trusted-checkout appears only in the CI action (default on, input trusted-checkout), never in the local pre-push command; naming the action in a workflow is the CI opt-in the trust boundary and acf-setup SKILL.md:249 describe.
  - spec citation: `config/architecture/ARCHITECTURE.md:178-181`
- **C15** [mandate] [load-bearing]: Release discipline: acf-setup's prose changes, so the version goes to 0.3.4 in plugin.json and pyproject.toml; a tagging rule is added to the section; acf-setup is not among the four skill trees scripts/check_installed_skills.py byte-checks, so no reinstall is owed.
  - spec citation: `config/architecture/ARCHITECTURE.md:274-284`
- **C16** [mandate] [load-bearing]: Call-site rule: reusing the precommit call site for a pre-push hook, with the doctrine sentence '`precommit` is the local git-hook site, whichever hook (pre-commit or pre-push) runs it', stays inside the closed vocabulary and adds no site value.
  - spec citation: `config/architecture/ARCHITECTURE.md:140-187`
- **C17** [mandate] [load-bearing]: Prose names no host: the acf-setup changes and the action name no host repository, path or section (generic placeholders; the first adopter appears only in the spec's §8).
  - spec citation: `config/architecture/ARCHITECTURE.md:223-233`
- **C18** [mandate] [load-bearing]: Live consumers: tests/action_fixture_host.py is test scaffolding (no package code, hook or skill calls it; it builds fixtures for the action's CI test), not an export, so the rule ('An export has a live call site in the package, a hook or a skill') does not govern it; the action itself has a live consumer in a skill (/acf-setup step 8 prints it for hosts).
  - spec citation: `config/architecture/ARCHITECTURE.md:243-247`
- **C19** [mandate] [load-bearing]: One owner for host paths: tests/action_fixture_host.py takes the two config paths it writes from acf.repo (MANDATES_REL, ARCH_REL at repo.py:21, :24), as the section asks of repository-level tests/ and scripts/ (ARCHITECTURE.md:120-122); and /acf-setup's registry checks consume the package (load_gate_registry, MandateRegistry.active, host_rows) rather than reading the YAML by eye.
  - spec citation: `config/architecture/ARCHITECTURE.md:115-138`
- **C20** [mandate] [load-bearing]: Single point of definition: after the change the base-ref derivation has one owner (the action; the plugin's own inline gate step at ci.yml:39-40 is removed), and the install recipe's three copies (acf-setup step 4 for a developer machine, the test job's `.[dev]` install for pytest and the TS self-test, the action's venv on a host runner) are three installs for three environments, recorded in the section as declared breaches with the reason they stay apart.
  - spec citation: `config/architecture/ARCHITECTURE.md:286-303`
- **C21** [mandate]: The action's input defaults (trusted-checkout 'true', base derived from the event, python-version, node-version, repo '.') do not breach `## Declared, never defaulted`, which governs host declarations the gates read and records package defaults; the spec does not list that section.
  - spec citation: `None`
- **C22** [mandate]: No completeness claims: the spec's factual claims about the tree are backed by recipes or file:line receipts (§6), and it makes no unbacked every/all/only/no-second claim about the tree.
  - spec citation: `config/architecture/ARCHITECTURE.md:249-259`
- **C23** [shape_fit] [load-bearing]: The composite action creates no second gate: every decision about what code passes stays in acf-check-diff, which the action calls with flags it already has; the action's own stops (missing plugin files, Windows, a bad input value, a failed host-setup, a shallow clone) come before the gate and judge no code; the shallow-clone stop only improves the message for a refusal acf-check-diff already makes (GitError), which stays authoritative.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:36-121`
- **C24** [shape_fit] [load-bearing]: The pre-push step reuses the existing precommit call site and the existing --base scope CI uses, creating no second spelling of a call site and no second diff scope.
  - spec citation: `config/architecture/ARCHITECTURE.md:140-187`
- **C25** [shape_fit] [load-bearing]: No existing mechanism in the repository installs and runs acf-check-diff for a host in CI (no reusable workflow, action or install script for hosts); the only existing CI invocation is the plugin's own self-check, which the design moves onto the action.
  - spec citation: `None`
- **C26** [shape_fit] [load-bearing]: Replacing the test job's inline gate step (ci.yml:39-40, `--base "origin/${{ github.base_ref || 'main' }}"`) with the action's third run against this repository (repo: ., base empty) leaves one owner of the base-ref derivation and keeps today's coverage of this repository: the derived base is origin/<base_ref> on pull requests and origin/<default branch> otherwise, where this repository's default branch is main.
  - spec citation: `.github/workflows/ci.yml:39-40`
- **C27** [sweep]: The places describing or printing the pre-commit/CI wiring that change are: acf-setup SKILL.md frontmatter, checklist item 8, step 8 heading and body, the upgrading section (:251-258, including the :258 install reminder) and the step 10 summary line (:285); docs/guides/SUPERPOWERS_COMPLEMENT.md:40; a new README.md upgrade note beside :112; .github/dependabot.yml (a github-actions entry for /.github/actions/check-diff). Step 9 and the friend-bar tip deliberately keep --mode. Obligation: sweep the tracked tree outside docs/design, docs/plans and docs/reviews for other stale wiring descriptions.
  - spec citation: `docs/guides/SUPERPOWERS_COMPLEMENT.md:40`
- **C28** [mechanism_justification] [load-bearing]: A composite action is justified over templates copied into each host (they drift; today's CI sketch at acf-setup SKILL.md:239-247 is such a template) and over a reusable workflow (it owns the host's whole job); the host keeps its triggers, runner and dependants.
  - spec citation: `None`
- **C29** [mechanism_justification] [load-bearing]: The action's step 1 self-check (stop, naming both paths, unless pyproject.toml and the TS pack's package.json are three levels above $GITHUB_ACTION_PATH) is justified over a second checkout of the plugin repository inside the action: it refuses rather than repairs, and it turns an unverifiable platform premise into a loud failure at the first adopter's run.
  - spec citation: `None`
- **C30** [mechanism_justification] [load-bearing]: One host-setup input, run after the action's setup with the venv's bin first on PATH, is justified because host detector modules run in the gate's process and so their Python packages must be in the action's venv; Node dependencies could also come from earlier steps (they stay on disk), and host-setup is the documented single place for both.
  - spec citation: `None`
- **C31** [mechanism_justification] [load-bearing]: The pre-push step skipping only when acf-check-diff is absent and blocking on every non-zero exit (refusals included) is justified: pre-push runs once per push; CI holds where the tool is absent; refusals and findings share exit 1 and separating them would need stderr parsing.
  - spec citation: `None`
- **C32** [mechanism_justification] [load-bearing]: Adding a push trigger only for hosts whose registry has an active fail_loud_ratchet row or host guard row at ci, rather than always, is justified: for every other row a push run's empty diff checks nothing, so the trigger would only cost a runner minute.
  - spec citation: `None`
- **C33** [mechanism_justification]: The shallow-clone stop earns its place although acf-check-diff already refuses through GitError on a missing merge base, because git's message does not name fetch-depth; it repairs nothing and the GitError refusal stays authoritative.
  - spec citation: `None`
- **C34** [mechanism_justification]: Tagging releases by hand is justified over a post-merge-housekeeping step (a byte-checked skill edit) or a tagging workflow (a new CI surface and a token that can push tags); a forgotten tag fails loudly at the host's uses: line.
  - spec citation: `None`
- **C35** [implementability] [load-bearing]: The §4.2 fixture row (id fail-loud.empty-catch, title, BLOCK, ast, empty_catch, typescript, call_sites [ci], exemption_tokens [], enforced, arch_anchor '## Fail loud') carries every field Mandate requires and loads; with no host rows no approval is needed; `--base main` resolves in a fixture repository with no origin remote; an added `catch {}` yields BLOCK fail-loud.empty-catch and exit 1 and the clean change exit 0. Obligation: check the registry load rules against the fixture.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:50-61`
- **C36** [implementability] [load-bearing]: tests/action_fixture_host.py is not collected by pytest: its name matches neither default pattern (test_*.py, *_test.py) and pyproject.toml sets no python_files; and the `action` job runs it with PYTHONPATH=plugins/arch-compliance/python, under which `import acf.repo` succeeds without an install because acf.repo imports only the standard library and acf.exceptions (repo.py:1-7) and acf/__init__.py imports nothing.
  - spec citation: `None`
- **C37** [implementability] [load-bearing]: `pip install -e <plugin repo root>` into a fresh venv puts acf-check-diff at <venv>/bin with acf importable from the source tree, so the TS bridge's _PACK_ROOT resolves into that repository; host detector modules the gate imports resolve their imports from the venv, so a `pip install` run by host-setup with the venv's bin first on PATH lands where they are imported from.
  - spec citation: `pyproject.toml`
- **C38** [implementability] [load-bearing]: The platform hooks the action and its test assume behave as stated: `git rev-parse --is-shallow-repository` prints true on a shallow clone (if it did not, only the message degrades, since the GitError refusal stays authoritative); and, each exercised by the `action` CI job before any tag so that a failure turns it red: a composite action can `uses:` actions/setup-python and actions/setup-node; `continue-on-error: true` with `steps.<id>.outcome` reads failure; github.base_ref is empty off pull_request and github.event.repository.default_branch is set; `tee` under `set -o pipefail` keeps the gate's exit status (the first adopter's ci.yml:580-587 relies on the same pipefail behaviour).
  - spec citation: `None`
- **C39** [implementability] [load-bearing]: The pre-push snippet works where /acf-setup places it: with `|| exit 1` a gate failure ends the hook wherever the snippet sits, with or without `set -e`; the absent-tool branch lets the push continue; placements are a pre-push file in the core.hooksPath directory, .git/hooks/pre-push or .husky/pre-push. In the first adopter's .githooks/pre-push (set -e, docs-only skip that exits 0) the snippet goes after the skip.
  - spec citation: `None`
- **C40** [implementability] [load-bearing]: /acf-setup's registry checks can be done by consuming the package as the spec names: acf.detectors.load_gate_registry(repo, mandates_path) loads the registry; MandateRegistry.active(sites, detection=...) selects active ast/guard rows at precommit; active(sites, detector='fail_loud_ratchet') the ratchet; host_rows(sites, detection='guard') the host guards at ci.
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:130-147`
- **C41** [implementability] [load-bearing]: The action's third run against this repository (repo: ., base empty, trusted-checkout default true) works in the new `action` job: this repository has no host rows, so --trusted-checkout changes nothing; the job checks out with fetch-depth 0; and the run on a push to main sees an empty diff and passes, as today's step does.
  - spec citation: `.github/workflows/ci.yml:39-40`
- **C42** [implementability]: The pre-commit framework placement works as the acf-setup text gives it: a repo-local hook with language system, pass_filenames false, stages [pre-push] and entry sh -c '<guarded command>' runs at pre-push once installed with `pre-commit install --hook-type pre-push` (or default_install_hook_types), and sh -c propagates the exit status. Not load-bearing: it is placement prose for hosts using that framework; the mechanism is unchanged if a detail differs.
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:217-225`
