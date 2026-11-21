# Adversarial design review — full detail

Spec: `docs/design/CHECK_DIFF_HOST_WIRING.md` @ `1c7d93759039feeb460bbd19e6821de7c4bffa75`
Kinds: feature
Outcome: **BLOCKED**
Claims: 43 · Reviewers: 4 · Converged: 1

## Blocking reasons

- mandate claim C22 is REFUTED: The doctrine says a tree claim is 'not load-bearing on "every", "all", "only", ... or "no second" unless a recipe that a reader can re-run backs the quantifier' (:251-254). The spec's claim that it makes no unbacked quantified claim is false. (1) Spec:443-444 says the first adopter's registry 'has no `fail_loud_ratchet` row and no host guard row', and §8 builds on that to decide 'so `pull_request` alone'. Neither §6 nor §8 gives a recipe or receipt for it. The statement is true at 7313bca5: the cy mandates.yml host rows at :143 and :162 are `detection: ast`, and the only guard is no_build_artifacts at :33. But no recipe backs it. (2) Spec:207-208, 'pyproject.toml sets no `python_files`', has no recipe. It holds today (pyproject.toml:23-25). (3) Spec:76-77, 'which no file in this repository records', is an unbacked negative. Each can be fixed by adding a §6 row with a grep or a file:line.

## Absorptions

- IDENTICAL: '.github/actions/check-diff step 8 (run acf-check-diff --base <derived> --call-site ci)' shares responsibility 'run the diff gate on this repository in CI with a derived base ref' with .github/workflows/ci.yml:39-40 — Delete the test job's inline gate step and consume the action (the spec does this in §4.2 run 3).
- PARTIAL_OVERLAP: '.github/actions/check-diff steps 3-5 (setup-python, editable pip install of the repository root, setup-node, npm ci in detectors/typescript)' shares responsibility 'install the acf package and the TypeScript detector pack' with .github/workflows/ci.yml:17-34 — Shared R: an editable install of the repository root plus npm ci in plugins/arch-compliance/detectors/typescript. Private to the test job: the [dev] extra and the system interpreter. Private to the action: a $RUNNER_TEMP virtual environment. A possible common abstraction is one install step (for example a setup composite with an extras input) that both the test job and check-diff consume. The spec instead keeps three copies (acf-setup step 4 at SKILL.md:67-90, the test job, the action) and records them under ## Single point of definition (§4.4, §5). That records the breach, as the doctrine allows.
- PARTIAL_OVERLAP: '.github/actions/check-diff step 7 (shallow-clone stop)' shares responsibility 'refuse a diff whose merge base is unavailable' with plugins/arch-compliance/python/acf/diff.py:33-39 — Shared R: refusing when the merge base cannot be computed. The gate's GitError is the authoritative check. Either narrow the action's check to the actual condition (the merge base is unresolvable) so it only re-words the gate's refusal, or state in §4.1 step 7 that it also refuses shallow clones the gate would accept.

## Converged findings

- [2 reviewers: sweeper, hardening] The action's shallow-clone stop refuses every shallow clone, including one deep enough to hold the merge base that acf-check-diff would complete, so it adds a refusal rather than only improving GitError's message.
  - evidence: `plugins/arch-compliance/python/acf/diff.py:33-45`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:20; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:98-103; pyproject.toml:31-32; pyproject.toml:39-40; plugins/arch-compliance/detectors/typescript (package.json, package-lock.json, src/ present)`
- reasoning: _PACK_ROOT is Path(__file__).resolve().parents[3]/'detectors'/'typescript'. For a file at plugins/arch-compliance/python/acf/detectors/typescript_bridge.py that is plugins/arch-compliance/detectors/typescript, which sits outside the acf package. Packages are found under plugins/arch-compliance/python (:31-32), and package-data for acf is only judge_prompt.md and review/packs/*.yml (:39-40), so no wheel carries the pack. From a wheel, __file__ resolves into site-packages and the pack path does not exist, so scan_typescript_file raises DetectorPackError 'pack not found' (:98-99). Without node_modules it raises 'dependencies are not installed' with the npm ci hint (:100-103). An editable install from a source checkout plus npm ci in the pack directory is therefore what the runner needs.

#### C2 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:43-46; plugins/arch-compliance/python/acf/cli_check_diff.py:135-150; plugins/arch-compliance/python/acf/cli_check_diff.py:212-230; plugins/arch-compliance/python/acf/detectors/host.py:220-225`
- reasoning: With base set, _diff_args returns [f'{base}...HEAD'] (diff.py:43-46). When base equals HEAD, changed is empty, the per-file loop (:142-206) does nothing and in_repo stays empty. The ratchet loop (:212-226) calls scan_ratchet(repo, baseline...) with no reference to changed. scan_host_guards (:228-230, host.py:220-225) loads and calls every active host guard row with tuple(changed_files), even when that tuple is empty. The build-artifact guard (:208-210) runs over changed only, so an empty diff gives it nothing. Every link of the stated reasoning holds.

#### C3 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:106-108; plugins/arch-compliance/python/acf/cli_check_diff.py:119-121; plugins/arch-compliance/python/acf/cli_check_diff.py:64-69; plugins/arch-compliance/python/acf/approval.py:150-154; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:100-103; plugins/arch-compliance/python/acf/diff.py:33-39`
- reasoning: A caught GitError, AcfInputError, UnknownDetectorError or DetectorPackError prints 'acf: <exc>' to stderr and returns 1 (:106-108). Any BLOCK finding also returns 1 (:119-121). Each named refusal carries a specific message. A missing approval raises AcfInputError 'host detectors need approval ... rows: ...' (approval.py:150-154). A pack without npm ci raises DetectorPackError naming the npm ci command (typescript_bridge.py:100-103). A bad base raises GitError with git's stderr (diff.py:36-38). --call-site is required=True (:66), so leaving it out is an argparse usage error (exit 2). resolve_repo at :85 sits outside the try, so an exception there is uncaught and exits non-zero. Exit codes alone cannot separate a refusal from a finding.

#### C4 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:145-148; plugins/arch-compliance/python/acf/cli_check_diff.py:153; plugins/arch-compliance/python/acf/cli_check_diff.py:189; plugins/arch-compliance/python/acf/diff.py:43-46; C:/Users/iball/Arduino/Projects/Cayenne/.githooks/pre-push:7; C:/Users/iball/Arduino/Projects/Cayenne/scripts/lib/pre-push-scope.mjs:63-65`
- reasoning: Line numbers come from the committed three-dot diff (added_lines, :148), but the text is read from the working tree (tree.file at :145, read_text at :153 and :189). An uncommitted edit can therefore shift a line or remove a committed violation. A file deleted in the working tree gives tree.file None and is skipped (:146-147). The diff is base...HEAD, which is the checked-out branch. Nothing in the snippet fetches. The first adopter's hook runs pre-push-scope.mjs at :7, and that script reads process.stdin to its end (:63-65), so stdin is consumed.

#### C5 — UNPROVEN
- evidence: `ran `git tag` and `git ls-remote --tags origin` in the worktree at 1c7d9375: both printed nothing (ls-remote rc=0); no repository file records tag absence, so no file:line can carry it`
- reasoning: Both commands confirm the fact as of this review. The verdict contract requires a file:line for SURVIVED, and a ref's absence has no file:line. Recorded as UNPROVEN on format grounds only. The claim is not load-bearing.

#### C6 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:210; plugins/arch-compliance/skills/acf-setup/SKILL.md:223; plugins/arch-compliance/skills/acf-setup/SKILL.md:240-247; plugins/arch-compliance/skills/acf-setup/SKILL.md:258`
- reasoning: The step 8 heading is at :210. The pre-commit entry is 'acf-check-diff --mode staged --call-site precommit' (:223). The CI sketch (:240-247) is a checkout plus the --base ... --call-site ci --trusted-checkout run at :245, with no install step. :258 is the generic 'Install the acf package into the environment used by hooks/CI' and does not mention the TypeScript pack or npm ci.

#### C7 — UNPROVEN
- evidence: `searched the repository for any record of where GitHub places a remotely referenced composite action (no .github/actions exists yet; .github/workflows/ci.yml:1-45 uses no composite action); none found`
- reasoning: This is platform behaviour, and as the claim itself says, no repository file records it. I could not re-derive it from the tree. It is not load-bearing, and the design guards it with the step-1 path check, so a false premise would fail loudly rather than silently.

#### C8 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/detectors/eslint_rules.py:20-29; C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/detectors/eslint_rules.py:33; C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/detectors/eslint_rules.py:41-45; C:/Users/iball/Arduino/Projects/Cayenne/.github/workflows/ci.yml:94; C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/mandates.yml:29-37; C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/mandates.yml:139-166; plugins/arch-compliance/python/acf/registry.py:30-31; plugins/arch-compliance/python/acf/registry.py:144-147`
- reasoning: Cayenne HEAD is 7313bca5. ESLINT = WEB/'node_modules'/'eslint'/'bin'/'eslint.js' (:33). The detector runs 'node <ESLINT>' with cwd cayenne-web and raises if the file is missing (:41-45). Its imports are json, re, subprocess, collections.abc, pathlib and acf.* only (:20-29). CI uses node-version '22' (ci.yml:94). In mandates.yml, the only guard row is ops.no-build-artifacts with detector no_build_artifacts. That detector has no ':', so is_host_detector_ref is false and host_rows excludes it. The host rows (state_from_transition, device_storage_owner) are detection: ast, and no row names fail_loud_ratchet. cayenne-web/package-lock.json is tracked, so `npm ci --prefix cayenne-web` is viable.

#### C9 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/Cayenne/.github/workflows/ci.yml:6-7; C:/Users/iball/Arduino/Projects/Cayenne/.githooks/pre-push:1-18; ran `git grep -n -i acf 7313bca5 -- .github .githooks` (rc=1, no output), `gh api repos/IanDBallard/Cayenne/branches/main/protection` (404 Branch not protected), `gh api repos/IanDBallard/Cayenne/rules/branches/main` (rules: deletion, non_fast_forward, pull_request; no required_status_checks)`
- reasoning: The pre-push hook (:1-18) and the workflows contain no acf invocation, and git grep at the cited commit found no match. Branch protection is absent. The ruleset carries no required_status_checks rule, which agrees with the ci.yml:6-7 comment.

#### C10 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:245; plugins/arch-compliance/skills/acf-setup/SKILL.md:249; plugins/arch-compliance/python/acf/cli_check_diff.py:102; plugins/arch-compliance/python/acf/approval.py:66-70; plugins/arch-compliance/python/acf/approval.py:143-154; config/architecture/ARCHITECTURE.md:178-182`
- reasoning: Today's sketch passes --trusted-checkout (:245), so a pull request's own host detectors already run under it. Without the flag, cli_check_diff.py:102 calls require_approval. That reads ~/.acf/approvals.json (store_path, approval.py:66-70), which a fresh runner does not have, so it raises AcfInputError (approval.py:150-154). This matches the doctrine's trust boundary (ARCHITECTURE.md:178-182).

#### C11 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-96; plugins/arch-compliance/python/acf/cli_check_diff.py:11-33; plugins/arch-compliance/python/acf/detectors/host.py:191; plugins/arch-compliance/python/acf/detectors/host.py:220; plugins/arch-compliance/python/acf/detectors/__init__.py:59-72`
- reasoning: The refusal predicate counts only ast and guard rows (:94-96). Host rows are selected with detection='ast' (host.py:191) and detection='guard' (host.py:220). cli_check_diff imports no judge or provider code (:11-33). load_gate_registry imports acf.judge only to obtain LLM_PROMPT_IDS for validation (__init__.py:65), which needs httpx installed (a declared dependency) but no provider key. Nothing calls an LLM.

#### C12 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:261-272; plugins/arch-compliance/python/acf/diff.py:24-30`
- reasoning: The doctrine records run_git (diff.py:24-30) as declared debt: text=True with no encoding. In the code, subprocess.run uses text=True and no encoding= argument. The repository CLAUDE.md Windows note runs the gate under PYTHONUTF8=1. Not load-bearing.

#### C13 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:102-109; plugins/arch-compliance/python/acf/detectors/host.py:81-83; plugins/arch-compliance/python/acf/detectors/host.py:224-225; C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/detectors/eslint_rules.py:28-29`
- reasoning: load_host_detector uses spec_from_file_location plus exec_module inside the gate process (:102-109). It appends the host root to sys.path (:81-83) and then calls the callable in-process (:224-225). Any import a host module makes, such as acf.* in the Cayenne detector, therefore resolves against the interpreter running acf-check-diff. A package that must be importable has to live in that interpreter's environment.

#### C43 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:330; .github/workflows/ci.yml:10; .github/workflows/ci.yml:39-40`
- reasoning: ARCHITECTURE.md:330 reads 'Post-merge CI workflows: .github/workflows/ci.yml (test job on main)'. ci.yml's only job is test (:10), and its gate step is at :39-40, the step the design moves into the action job.

### Unanchored findings


### Looked for but did not find

- a third-party import in acf/__init__.py or acf/exceptions.py that would break the fixture script's uninstalled `PYTHONPATH=... python tests/action_fixture_host.py` run (acf/__init__.py is empty; exceptions.py has no imports)
- a Mandate field the §4.2 fixture row omits, or a Language value it uses illegally (registry.py:50-61 fields all present; Language at registry.py:16 accepts 'typescript')
- a TypeScript empty_catch rule that would miss a binding-less `catch {}` (emptyCatch.ts:12-28 checks only the block's statements)
- a `python_files` override in pyproject.toml that would make pytest collect tests/action_fixture_host.py (pyproject.toml:23-25 sets only testpaths and pythonpath)
- a mismatch between the spec's ARCHITECTURE.md section line ranges and the headings (checked :115, :140, :189, :223, :243, :249, :261, :274, :286, :324)
- the `-c user.name/user.email/commit.gpgsign` options at plugins/arch-compliance/tests/test_adr_citation_history.py:20 differing from the spec's description (they match)
- a Dependabot github-actions entry already covering /.github/actions/check-diff (.github/dependabot.yml:19-22 names directory / only)
- a host guard or fail_loud_ratchet row in the first adopter's registry that would require the push trigger
- a second Python dependency of the first adopter's host detector beyond stdlib and acf
- a required_status_checks rule in the first adopter's repository ruleset

## compliance

### Claim verdicts

#### C14 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:178-181; plugins/arch-compliance/skills/acf-setup/SKILL.md:249; plugins/arch-compliance/python/acf/cli_check_diff.py:76-82; plugins/arch-compliance/python/acf/cli_check_diff.py:102; docs/design/CHECK_DIFF_HOST_WIRING.md:294; docs/design/CHECK_DIFF_HOST_WIRING.md:343-346; README.md:58; docs/guides/SUPERPOWERS_COMPLEMENT.md:83`
- reasoning: The trust boundary reads 'or, for `acf-check-diff`, when the invocation passes `--trusted-checkout`' (:178-181). It puts no limit on which CI invocation may pass the flag. SKILL.md:249 and the flag's own help text (cli_check_diff.py:80) both say the workflow file is the opt-in in CI. In the design, the only place the flag is passed is the action's input. The guarded pre-push command at spec:294 leaves it out. The README and guide lines that pass it today (README.md:58, SUPERPOWERS_COMPLEMENT.md:83) are rewritten without it (spec:357-359). The new wording for :249 is given verbatim at spec:343-346. /acf-setup's own probe runs (spec:313-315) also leave it out. Without an approval, a site that has host rows then fails at require_approval (cli_check_diff.py:102), which comes after the 'selects no active' check, so the probe still works.

#### C15 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:276-281; scripts/check_installed_skills.py:18-23; pyproject.toml:3; plugins/arch-compliance/.claude-plugin/plugin.json:3`
- reasoning: The doctrine says 'A change to a skill's prose bumps the plugin version in ... plugin.json and pyproject.toml' (:276-277). Both files are at 0.3.3 today, and the design moves them to 0.3.4 (spec:389-391). The byte-check covers exactly adversarial-design-review, responding-to-adversarial-review, post-merge-housekeeping and architecture-review (check_installed_skills.py:18-23), so a change limited to acf-setup's prose does not create a reinstall obligation under :278-281. The tagging sentence is added to the section (spec:373-376). No gate skill file is changed.

#### C16 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:154-158; plugins/arch-compliance/python/acf/registry.py:17-18; plugins/arch-compliance/python/acf/cli_check_diff.py:65-69`
- reasoning: The call-site rule lists a closed vocabulary ('`ci`, `precommit`, `hook`, `posttooluse` and `audit`'), and `ci` and `precommit` are the diff sites (:154-156; registry.py:17-18). `acf-check-diff --call-site` accepts only DIFF_CALL_SITES (cli_check_diff.py:65-69). The doctrine never ties `precommit` to the git pre-commit hook. The pre-push command passes `--call-site precommit` (spec:294), so no new value is added. The added sentence (spec:370-372) only clarifies what the existing value covers.

#### C17 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:225-226; docs/design/CHECK_DIFF_HOST_WIRING.md:260-272; docs/design/CHECK_DIFF_HOST_WIRING.md:292-300; docs/design/CHECK_DIFF_HOST_WIRING.md:437-458`
- reasoning: The rule is 'Skill prose and runtime messages name no host repository, path or section' (:225-226). The new acf-setup text uses placeholders: `<version>`, `<default-branch>`, `<command>`, plus generic hook locations and tool names such as husky and the pre-commit framework (spec:260-272, :292-311). The one repository slug it contains is the plugin's own action reference in `uses:`, and that names the plugin, not a host. The first adopter's paths appear only in spec §8 (spec:437-458) and in the spec's rationale (spec:340). The action's step-1 message names paths inside the plugin repository (spec:167-170). acf-setup has no test-backed row (:232-233), so review is the only check, which the spec's claim does not dispute.

#### C18 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:245-247; docs/design/CHECK_DIFF_HOST_WIRING.md:197-199; docs/design/CHECK_DIFF_HOST_WIRING.md:231-245; plugins/arch-compliance/skills/acf-setup/SKILL.md:210-249`
- reasoning: The rule reads 'An export has a live call site in the package, a hook or a skill. A test is not a consumer' (:245-246). tests/action_fixture_host.py is a CLI script that a CI job runs (spec:197-199, :231-233). It exports nothing for other code to import, so the export rule does not reach it. The action has consumers in two places: the plugin's own ci.yml `action` job (spec:236-245), and acf-setup step 8, which prints it as the host's workflow (spec:257-272, replacing SKILL.md:235-247).

#### C19 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:121-123; plugins/arch-compliance/python/acf/repo.py:21; plugins/arch-compliance/python/acf/repo.py:24; plugins/arch-compliance/python/acf/cli_check_diff.py:92-100; plugins/arch-compliance/python/acf/registry.py:130-147; plugins/arch-compliance/python/acf/detectors/__init__.py:59`
- reasoning: The doctrine says repository-level tests/ and scripts/ 'follow the rule by importing the `acf.repo` constants' (:121-122). The fixture takes MANDATES_REL and ARCH_REL from repo.py:21 and :24. The 'selects no active' refusal comes from the registry load and the active() checks (cli_check_diff.py:92-100), which run before any diff or approval work, so `--mode worktree` probes reach it, and /acf-setup reads the gate's own predicate. The push-trigger check calls load_gate_registry (detectors/__init__.py:59), active(..., detector=...) and host_rows(..., detection=...), which exist with the signatures the spec names (registry.py:130-147). Each stated element holds. The one gap, where that snippet gets the mandates path load_gate_registry needs, is filed separately as an advisory finding.

#### C20 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:288-303; .github/workflows/ci.yml:29-34; .github/workflows/ci.yml:39-40; plugins/arch-compliance/skills/acf-setup/SKILL.md:67-90`
- reasoning: The section asks for one canonical implementation and records the breaches it allows ('Current breaches, recorded not hidden', :290-302; the path-glob dialects are an example of a breach kept with a reason). Today the base derivation is inline in the gate step at ci.yml:39-40. The design removes that step and routes this repository's own run through the action (spec:243-245, :400). The three install copies exist: acf-setup step 4 (SKILL.md:67-90), the test job (ci.yml:29-34) and the new action. The spec records them under the section with the reason they stay separate (spec:387-388, :401), which matches how the section handles existing breaches.

#### C21 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:212-221; docs/design/CHECK_DIFF_HOST_WIRING.md:295-299; docs/design/CHECK_DIFF_HOST_WIRING.md:377-382; plugins/arch-compliance/python/acf/repo.py:41-50`
- reasoning: The section already lists, as outside the rule, defaults that are not host declarations a gate reads, such as resolve_repo falling back to the process directory (:212-216; repo.py:41-50). The action's input defaults are of the same kind and are recorded beside them (spec:377-382). For ACF_PREPUSH_OPTIONAL, the snippet tests `"${ACF_PREPUSH_OPTIONAL:-}" = "1"`, and every other value, including unset, falls to the refusing `else` branch with `exit 1` (spec:295-299). No default stands in for a declaration. The `trusted-checkout: true` default does not bring a default in where a declared value belongs: the trust boundary makes the CI invocation the opt-in, and the invocation here is the workflow naming the action.

#### C22 — REFUTED
- evidence: `config/architecture/ARCHITECTURE.md:251-254; docs/design/CHECK_DIFF_HOST_WIRING.md:443-444; docs/design/CHECK_DIFF_HOST_WIRING.md:207-208; docs/design/CHECK_DIFF_HOST_WIRING.md:76-77; C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/mandates.yml:143`
- reasoning: The doctrine says a tree claim is 'not load-bearing on "every", "all", "only", ... or "no second" unless a recipe that a reader can re-run backs the quantifier' (:251-254). The spec's claim that it makes no unbacked quantified claim is false. (1) Spec:443-444 says the first adopter's registry 'has no `fail_loud_ratchet` row and no host guard row', and §8 builds on that to decide 'so `pull_request` alone'. Neither §6 nor §8 gives a recipe or receipt for it. The statement is true at 7313bca5: the cy mandates.yml host rows at :143 and :162 are `detection: ast`, and the only guard is no_build_artifacts at :33. But no recipe backs it. (2) Spec:207-208, 'pyproject.toml sets no `python_files`', has no recipe. It holds today (pyproject.toml:23-25). (3) Spec:76-77, 'which no file in this repository records', is an unbacked negative. Each can be fixed by adding a §6 row with a grep or a file:line.

### Unanchored findings

- **advisory**: /acf-setup's push-trigger snippet calls load_gate_registry(repo, mandates_path), but the spec does not say where it gets mandates_path. The doctrine requires executable skill snippets to take host paths from the acf.repo constants (MANDATES_REL) and not restate 'config/architecture/mandates.yml'.
  - evidence: `plugins/arch-compliance/python/acf/detectors/__init__.py:59; config/architecture/ARCHITECTURE.md:122-123; docs/design/CHECK_DIFF_HOST_WIRING.md:318-322`

### Looked for but did not find

- High-frequency misses (:315-322) checked first. Completeness claims: filed as C22. Defaults re-entering a declared value: ACF_PREPUSH_OPTIONAL has no default, and the trusted-checkout default is the CI opt-in (C21). Host names in skill prose: none (C17). Stdlib exception mixin: the design adds no exception class. Subprocess text call without encoding: no package or hook code changes, and the fixture under tests/ is outside the scope of '## Declared text decoding' (:263-266). Check re-implemented in a skill: the site probe uses the gate's own refusal, and the push-trigger check uses registry helpers (C19).
- ## Fail loud / ## No shims: the action stops with a message on a missing plugin file, Windows, a bad input, a failed host-setup or a shallow clone (spec:167-190), and the pre-push snippet blocks on a missing tool unless the opt-out is declared. No swallowed failure, and no new Python/TS code in the package.
- ## POSIX paths: the fixture writes literal YAML text and serializes no Path object into YAML/JSON. Not touched.
- ## One base exception / ## Frozen ledger format / ## Build artifacts / ## Fail-loud ratchet / ## Façade sinks / ## FSM transitions / ## React boundaries / ## Soft fail-loud smells: the design adds no exception, ledger field, build output, or change to these detectors' behavior. Not touched.
- ## Declared text decoding: named by the spec for the Windows non-goal. Its scope (package and hooks runtime code) does not include the new action or the fixture.
- ## Post-merge: named. The spec updates the post-merge CI bullet at :330 to add the `action` job (spec:385-386).
- ## Scoped refactor: the edits to README, the guide, dependabot, ci.yml and the doctrine all follow from the feature (CI wiring, pre-push wording, the tag rule). There is no expansion into unrelated modules.
- Doctrine opening scope (:3-9): the spec extends it to `.github/actions/` (spec:383-384), so the action is not left ungoverned.
- unstated_mandates returned empty: every section whose surface this design touches is named in the spec header (spec:10-16).

## sweeper

### Claim verdicts

#### C23 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-108; plugins/arch-compliance/python/acf/cli_check_diff.py:119-121; plugins/arch-compliance/python/acf/diff.py:33-39; plugins/arch-compliance/python/acf/diff.py:45`
- reasoning: Opened cli_check_diff.main in full. Row selection and the no-active-row refusal (:94-100), the approval and trusted-checkout branch (:102), the scan, the caught-refusal exit 1 (:106-108) and the BLOCK exit 1 (:119-121) are all inside acf-check-diff. Spec §4.1 step 8 calls it only with existing flags (--repo, --base, --call-site, --trusted-checkout; :44-82). None of the action's stops (steps 1, 2, 6, 7 and the trusted-checkout input check) reads a source file or a finding, so no second judge of code appears. The base derivation the action takes on already sits outside the gate today, in the workflow (.github/workflows/ci.yml:40). A shallow merge base surfaces as GitError through _git (diff.py:33-39) on the three-dot diff (diff.py:45), and the gate catches it at cli_check_diff.py:106-108, so the claim that GitError stays authoritative holds. One sub-statement is imprecise: 'only improves the message' is not exactly true. `rev-parse --is-shallow-repository` prints true for every shallow clone, including a fetch-depth N checkout whose merge base is present, and acf-check-diff would complete that run. The stop is therefore slightly stricter than the gate. It still judges the checkout, not code, so the 'no second gate' shape holds; filed as advisory below.

#### C24 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:17-18; config/architecture/ARCHITECTURE.md:154-162; plugins/arch-compliance/python/acf/cli_check_diff.py:44-51; plugins/arch-compliance/python/acf/diff.py:42-45`
- reasoning: The precommit site already exists in the closed vocabulary (CallSite Literal and DIFF_CALL_SITES at registry.py:17-18; doctrine at ARCHITECTURE.md:154-158). The pre-push snippet adds no spelling: `pre-commit` is refused at load (README.md:144). Searched for anything that ties `precommit` to staged mode. --mode and --call-site are independent argparse options (cli_check_diff.py:38-43, :64-69), and nothing in diff.py or the registry reads the call site. Only docs pair precommit with --mode staged (README.md:57, acf-setup SKILL.md:223), and §4.3 rewrites or keeps those deliberately. --base is the existing three-dot scope (diff.py:42-45) that CI uses (ci.yml:40). The pre-push base is origin/<default-branch>, while CI's is origin/<base_ref>: the same scope mechanism with a different ref, not a second scope implementation.

#### C25 — SURVIVED
- evidence: `.github/workflows/ci.yml:29-40; plugins/arch-compliance/skills/acf-setup/SKILL.md:240-247; plugins/arch-compliance/skills/acf-setup/SKILL.md:258; .github/dependabot.yml:19-22`
- reasoning: Globbed .github/**, scripts/**, tests/** and plugins/arch-compliance/hooks/**. .github holds only workflows/ci.yml and dependabot.yml: no reusable workflow (no workflow_call) and no actions/ directory. scripts/ holds only check_installed_skills.py. Grepped the tree outside docs/design, docs/plans and docs/reviews for `pip install` and `npm ci`. The installs that run are the plugin's own test job (ci.yml:30, :34). The hosts' CI sketch (SKILL.md:240-247) runs acf-check-diff but installs nothing, and the only install text for host CI is the generic reminder at SKILL.md:258. Every other hit is developer-machine instructions or error hints (SKILL.md:74, :84; README.md:56; SUPERPOWERS_COMPLEMENT.md:81; posttooluse_gate.py:134; inject_constraints.py:97; typescript_bridge.py:28-29). The repository's only CI invocation of the gate is ci.yml:40, which §4.2 moves onto the action.

#### C26 — SURVIVED
- evidence: `.github/workflows/ci.yml:3-7; .github/workflows/ci.yml:40; config/architecture/mandates.yml:152-198`
- reasoning: ci.yml triggers only on push to main and pull_request to main (:3-7). Today's derivation `origin/${{ github.base_ref || 'main' }}` (:40) gives origin/<base_ref> on PRs and origin/main on pushes. The action's empty-base rule (spec §4.1 inputs table) gives origin/<base_ref>, or origin/<default_branch> when there is no base ref, and the default branch is main, so the two match on both triggers. No other base derivation exists in ci.yml, so removing :39-40 leaves the action as the only CI owner. On coverage: today's step passes no --trusted-checkout, while run 3 passes it by default. That is equivalent here because this registry has no host reference rows: every detector containing a path is an audit-only `.py` test path without `:<callable>` (mandates.yml:152-198), so require_approval would select nothing at ci. --call-site ci and --repo . are unchanged. The two pre-push/doc base spellings (origin/<default-branch>, origin/main) are local, not CI; they are recorded under relationships and two-owner counts.

#### C27 — REFUTED
- evidence: `README.md:136; README.md:141-142; plugins/arch-compliance/skills/acf-setup/SKILL.md:253-254`
- reasoning: Re-swept the tracked tree outside docs/design, docs/plans and docs/reviews by behaviour: any text that tells a host how to wire acf-check-diff into pre-commit or CI, or that names CI's invocation (terms: precommit, pre-commit, acf-check-diff, trusted-checkout, CI sketch, `pip install`, `npm ci`, \bCI\b). Every listed site resolves at the cited lines (SKILL.md:3, :25, :210, :249, :251-258, :285; SUPERPOWERS_COMPLEMENT.md:40, :80-85, :87; README.md:53-58, :62, :112; ARCHITECTURE.md:330; dependabot.yml:19-22). The list is not complete by the spec's own criterion. §4.3 rewrites the acf-setup v0.2.4 upgrade bullets (SKILL.md:253 'checked in pre-commit', :254 'CI and pre-commit invocations') as stale wiring text. README.md:141-142 carries the same two bullets in its own v0.2.4 upgrade note ('add it to your pre-commit and CI configuration', 'checked in pre-commit'), and README.md:136 (v0.2.5 note) says 'Add --trusted-checkout to the host's CI invocation of acf-check-diff; leave it out of pre-commit configuration'. None of the three is listed or excluded with a reason, unlike Step 9 and the friend-bar tip. Other hits checked and still true after the change, so no edit is needed: approval.py:152-153 ('a CI workflow ... passes --trusted-checkout'); cli_check_diff.py:47-50 and :79-80 (help text); pyproject.toml:35 and test_packaging.py:3 ('editable install used in development and CI'; the action installs editable); CLAUDE.md:39-40 ('as CI's own invocation does'; the action still passes --call-site ci); ARCHITECTURE.md:9; acf-mandate SKILL.md:139; README.md:148 and SUPERPOWERS_COMPLEMENT.md:70 (smoke invocations, not wiring).

### Unanchored findings

- **advisory**: The action's shallow-clone stop (§4.1 step 7) fires on `--is-shallow-repository`, which is true for any fetch-depth N checkout, including ones whose merge base is present and that acf-check-diff would complete. So the stop does more than improve the message of an existing GitError: it adds a stricter precondition. It judges no code, but the spec's wording in §4.1 step 7 and §5 overstates the equivalence.
  - evidence: `plugins/arch-compliance/python/acf/diff.py:33-45`
- **advisory**: The README's v0.2.4 and v0.2.5 upgrade notes carry the same pre-commit/CI wiring sentences that §4.3 rewrites in acf-setup's upgrade section, yet the sweep neither changes them nor says why it keeps them. The two documents would then disagree about the same historical upgrade.
  - evidence: `README.md:136`

### Looked for but did not find

- an existing composite action, reusable workflow (workflow_call) or host install script under .github/ or scripts/: Glob .github/**, scripts/**
- code that couples the precommit call site to --mode staged: Grep precommit across plugins/arch-compliance/python; only argparse choices and DIFF_CALL_SITES
- a test pinning ci.yml content, the acf-setup prose or dependabot.yml (which the change would break): Grep ci\.yml|workflows|acf-setup|base_ref|dependabot in tests/, plugins/arch-compliance/tests/, scripts/
- a second CI base-ref derivation in this repository: Grep base_ref across the tree outside docs; only ci.yml:40 and SKILL.md:245
- host reference rows in this repository's registry that would make --trusted-checkout change run 3's behaviour: Grep detector: in config/architecture/mandates.yml; none of the form <path>.py:<callable>

### Relationships

- IDENTICAL: `.github/actions/check-diff step 8 (run acf-check-diff --base <derived> --call-site ci)` — responsibility `run the diff gate on this repository in CI with a derived base ref` — existing `.github/workflows/ci.yml:39-40`
  - resolution: Delete the test job's inline gate step and consume the action (the spec does this in §4.2 run 3).
- PARTIAL_OVERLAP: `.github/actions/check-diff steps 3-5 (setup-python, editable pip install of the repository root, setup-node, npm ci in detectors/typescript)` — responsibility `install the acf package and the TypeScript detector pack` — existing `.github/workflows/ci.yml:17-34`
  - resolution: Shared R: an editable install of the repository root plus npm ci in plugins/arch-compliance/detectors/typescript. Private to the test job: the [dev] extra and the system interpreter. Private to the action: a $RUNNER_TEMP virtual environment. A possible common abstraction is one install step (for example a setup composite with an extras input) that both the test job and check-diff consume. The spec instead keeps three copies (acf-setup step 4 at SKILL.md:67-90, the test job, the action) and records them under ## Single point of definition (§4.4, §5). That records the breach, as the doctrine allows.
- ADJACENT: `§4.3 pre-push snippet `--base "origin/<default-branch>"`` — responsibility `choose the ref the three-dot diff is taken against` — existing `.github/workflows/ci.yml:40`
  - resolution: None; the CI derivation moves to the action, and the local base is filled in by /acf-setup.
  - non-merge: A local git hook has no github.base_ref or event context to derive from, so the base has to be spelled per host; the spec documents the stale-base consequence as a known gap.
- PARTIAL_OVERLAP: `.github/actions/check-diff step 7 (shallow-clone stop)` — responsibility `refuse a diff whose merge base is unavailable` — existing `plugins/arch-compliance/python/acf/diff.py:33-39`
  - resolution: Shared R: refusing when the merge base cannot be computed. The gate's GitError is the authoritative check. Either narrow the action's check to the actual condition (the merge base is unresolvable) so it only re-words the gate's refusal, or state in §4.1 step 7 that it also refuses shallow clones the gate would accept.
- ADJACENT: `action input trusted-checkout` — responsibility `opt a CI checkout into running host detectors` — existing `plugins/arch-compliance/python/acf/cli_check_diff.py:75-82`
  - resolution: None; the input passes the existing flag through.
  - non-merge: The input only decides whether to pass the existing flag; the trust decision stays in cli_check_diff.py:102.
- ADJACENT: `.github/actions/check-diff step 1 (pyproject.toml and detectors/typescript/package.json presence)` — responsibility `refuse when the TypeScript pack is unavailable` — existing `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:20-29`
  - resolution: None; each check covers a different failure.
  - non-merge: Step 1 checks before install that the action's own location is a full plugin checkout. The bridge refuses at scan time when node_modules/tsx is missing. They are different preconditions at different times.

### Two-owner counts

- install the acf package and TypeScript detector pack: 3
- choose the --base ref for the three-dot diff (action derivation, pre-push snippet): 2
- refuse when the merge base is unavailable (action step 7, diff._git GitError): 2

### Document conflicts

- `README.md:136` (restates): Add `--trusted-checkout` to the host's CI invocation of `acf-check-diff`; leave it out of pre-commit configuration.
- `README.md:141` (restates): `acf-check-diff` now requires `--call-site {ci,precommit}`; add it to your pre-commit and CI configuration

## hardening

### Claim verdicts

#### C28 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:240-247; .github/workflows/ci.yml:39-40`
- reasoning: The current CI wiring exists as hand-copied templates. One is the SKILL.md sketch at :240-247, with a base-ref expression and flags inlined. The other is this repository's own gate step at ci.yml:40, and it has already drifted from the sketch: it has no --trusted-checkout and uses `python -m` where the sketch uses the console script. That is the drift the claim names. A composite action is called from the host's own job (spec :260-272), so the host keeps its triggers, runner and dependants. A reusable workflow would replace the job. The justification holds against the tree.

#### C29 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:20; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:99-104; pyproject.toml:39-40`
- reasoning: The premise the self-check guards is real. _PACK_ROOT is a parents[3] path relative to the source file (typescript_bridge.py:20), and package-data ships no detectors/typescript (pyproject.toml:39-40). So the install must come from a full source tree. The bridge already refuses a missing pack (:99-104), but only when a .ts/.tsx file is in the diff. Step 1 (spec :167-170) makes the refusal unconditional and runs it before any install. It refuses and repairs nothing. A second checkout is the alternative the spec rejects, and the reason is written down. I trace it as a rung-3 refusal below.

#### C30 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:102-109; pyproject.toml:20`
- reasoning: host.py:102-109 loads host detector modules with spec_from_file_location and exec_module inside the gate's own interpreter. So a host detector's third-party imports resolve against the sys.path of whichever Python runs the acf-check-diff console script (pyproject.toml:20). That is the action's venv (spec :173-175). That venv exists only after step 4, so the only place a Python install can land in it is a step after step 4 with the venv's bin first on PATH (spec :178-181). The Node-side reasoning (files from earlier steps persist on disk) is correct and only says host-setup is a convention for Node.

#### C31 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:106-108; plugins/arch-compliance/python/acf/cli_check_diff.py:119-121; plugins/arch-compliance/python/acf/cli_check_diff.py:64-69`
- reasoning: Caught refusals print `acf: ...` and return 1 (:106-108). BLOCK findings return 1 (:119-121). A missing --call-site is an argparse usage error and exits 2 (:64-69). So exit status alone cannot tell a refusal from a finding, and the snippet's `|| exit 1` blocks on all of them. The default is to refuse (spec :297-299). The opt-out is an environment variable compared exactly with '1' (spec :295), and the spec keeps it out of committed files (:310-313). This is a declared flag, not a default.

#### C32 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:135-142; plugins/arch-compliance/python/acf/cli_check_diff.py:208-230; plugins/arch-compliance/python/acf/detectors/host.py:220-225; plugins/arch-compliance/python/acf/diff.py:42-45`
- reasoning: On a push, origin/<default>...HEAD has HEAD as its merge base (diff.py:45), so `changed` is empty. Every per-file scan loops over `changed`: python, TS, facade, fsm and host ast at :142-206, and build artifacts takes `changed` at :210. Only two kinds of row run regardless: the ratchet loop (:212-226), which scans the tree, and host guards (:228-230). The guards are called once per guard row whatever the file list holds (host.py:220-225). A push trigger therefore checks something only when one of these rows is active at ci, which is exactly the condition the spec's push-trigger rule uses.

#### C33 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:33-39; plugins/arch-compliance/python/acf/cli_check_diff.py:106-108; plugins/arch-compliance/python/acf/adr/citations.py:78-79`
- reasoning: When the merge base or ref is missing, _git raises GitError (diff.py:33-39). The CLI catches it and exits 1 with `acf: git diff ... failed` (cli_check_diff.py:106-108), and that message does not mention fetch-depth. The step repairs nothing. citations.py:78-79 already uses the same `--is-shallow-repository == "true"` predicate, so it is used elsewhere in the code. One caveat, filed below as an advisory: step 7 refuses every shallow clone, including one deep enough to hold the merge base, where the gate would have run correctly. So the step does more than improve the message: it adds a refusal that GitError would not have produced. The claim is non-load-bearing and its core holds.

#### C34 — SURVIVED
- evidence: `plugins/arch-compliance/.claude-plugin/plugin.json:3; pyproject.toml:3`
- reasoning: `git tag` prints nothing at this commit, so tagging is entirely new. A missing tag makes the host's `uses: ...@vX` fail to resolve, which is loud. The spec writes down why it rejected the alternatives (spec :117-120). The claim is non-load-bearing. One residual risk is not covered: nothing checks that the tag sits on a commit whose plugin.json:3 and pyproject.toml:3 versions match the tag name, and a wrong tag fails silently. Filed below as an advisory.

#### C35 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:50-61; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:15-17; plugins/arch-compliance/python/acf/registry.py:201-217; plugins/arch-compliance/python/acf/cli_check_diff.py:94-102; plugins/arch-compliance/detectors/typescript/src/rules/emptyCatch.ts:12-27; plugins/arch-compliance/python/acf/cli_check_diff.py:239`
- reasoning: The fixture row supplies every field Mandate declares without a default (registry.py:51-60). empty_catch is a built-in that reports to fail-loud.empty-catch (typescript_bridge.py:15-17, registered in detectors/__init__.py:44-47). So _check_builtin passes: the id matches the contract, and ci is within the TIER1 sites (registry.py:201-217). _row_shape requires a Tier-1 site, and ci is one (:99). With no `:` in the detector field, is_host_row is false (registry.py:30-31, :72-73), so no host row is selected and require_approval is NOT_NEEDED or skipped (:102). An ast row is active at ci, so the :94-100 refusal does not fire. `main` is a local branch, so `main...HEAD` resolves with no remote (diff.py:45). emptyCatch.ts:12-27 flags any CatchClause whose block has no statements, which includes `catch {}`, at the clause's start line, and that line is added. apply_registry takes severity BLOCK from the row (enforcement.py:67). _print_human emits `BLOCK fail-loud.empty-catch path:line ...` (:239) and the run exits 1 (:119-121). The clean variant gives no findings, prints 'No findings.' and exits 0. The ARCH_REL file is not read by acf-check-diff, which is harmless.

#### C36 — SURVIVED
- evidence: `pyproject.toml:23-25; plugins/arch-compliance/python/acf/repo.py:1-15; plugins/arch-compliance/python/acf/exceptions.py:1-6`
- reasoning: [tool.pytest.ini_options] sets testpaths and pythonpath but no python_files (pyproject.toml:23-25). No pytest.ini, setup.cfg, tox.ini or conftest.py exists at the root or in tests/ (checked with ls), so pytest's default patterns apply, and action_fixture_host.py matches neither. repo.py imports only os, re, collections.abc, pathlib and acf.exceptions (:10-15). exceptions.py defines plain Exception subclasses with no imports (:1-6). acf/__init__.py is 0 bytes (wc -c). tests/ holds only test_self_host.py and test_check_installed_skills.py, so nothing shadows `acf` when tests/ becomes sys.path[0].

#### C37 — SURVIVED
- evidence: `pyproject.toml:18-20; pyproject.toml:31-36; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:20; plugins/arch-compliance/python/acf/detectors/host.py:102-109; .github/workflows/ci.yml:30`
- reasoning: acf-check-diff is a [project.scripts] entry (pyproject.toml:20), so pip installs it into <venv>/bin. pyproject.toml:34-36 records that the editable install makes Path(__file__) resolve into the source tree, so _PACK_ROOT (typescript_bridge.py:20) lands at the repository's plugins/arch-compliance/detectors/typescript. Today's CI already depends on this (ci.yml:30 editable install, then the TS pack used from source). Host modules are exec'd in-process (host.py:102-109), so their imports resolve from the venv interpreter's sys.path. A `pip install` resolved through a PATH with <venv>/bin first runs the venv's pip and installs into that venv.

#### C38 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/adr/citations.py:78-79; plugins/arch-compliance/tests/test_adr_citation_history.py:48-57; C:/Users/iball/Arduino/Projects/Cayenne/.github/workflows/ci.yml:580-587`
- reasoning: The shallow predicate is already used at citations.py:78-79 and exercised against a real `--depth 1` clone in test_adr_citation_history.py:48-57. If it misreports, the spec's own job catches it, because the non-shallow fixture runs must proceed. I checked that each platform premise turns the action job red if it fails. A composite action unable to `uses:` setup-python or setup-node fails every run. If continue-on-error/outcome were read wrong, the assertion step after run 1 (spec :247-249) fails. If tee masked the exit status, run 1's outcome would be success and the same assertion fails. On the push to main, an empty base_ref with a missing default_branch yields `origin/`, which raises GitError and turns the run red (spec :375-376 names that run as the first exercise, and the tag waits for main's CI per spec :373-374). The cy: workflow at ci.yml:580-587 sets `set -o pipefail` before a tee for the same reason.

#### C39 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/Cayenne/.githooks/pre-push:1-18; plugins/arch-compliance/python/acf/cli_check_diff.py:106-108`
- reasoning: The snippet uses only POSIX sh: `command -v`, `[ = ]` and `${VAR:-}`. Commands in an if/elif condition are exempt from set -e. `cmd || exit 1` exits the top-level shell on any non-zero status. `${ACF_PREPUSH_OPTIONAL:-}` cannot trip set -u. The first adopter's hook is `#!/bin/sh` with `set -e` (:1, :5). Its docs-only skip is a top-level `exit 0` (:8-11) and it ends with `exit 0` (:18), so the snippet fits at top level between :11 and :17. That hook consumes stdin through node at :7, and acf-check-diff never reads stdin because git runs with capture_output (diff.py:24-30). `git config core.hooksPath` in the cy: checkout prints .githooks, so it matches the placement rule.

#### C40 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:93-102; plugins/arch-compliance/python/acf/registry.py:130-147; plugins/arch-compliance/python/acf/detectors/__init__.py:59-72; plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:21`
- reasoning: In main(), the registry loads at :93, the 'selects no active' refusal is :94-100, and require_approval is at :102. So for a site with no active ast/guard row, the refusal comes before any approval lookup, whatever host rows exist. A registry load failure refuses earlier with a different message, which the skill correctly does not read as 'no active row'. load_gate_registry(repo, mandates_path) exists (detectors/__init__.py:59-72). active() accepts a detector keyword (registry.py:130-142), and the ratchet's detector id is the string 'fail_loud_ratchet' (fail_loud_ratchet.py:21). host_rows() accepts a detection keyword (registry.py:144-147).

#### C41 — SURVIVED
- evidence: `config/architecture/mandates.yml:90-94; config/architecture/mandates.yml:152; plugins/arch-compliance/python/acf/registry.py:72-73; .github/workflows/ci.yml:13-15; .github/workflows/ci.yml:40`
- reasoning: No detector field in this repository's mandates.yml contains `:`. The path-valued detectors (:152 onward) are audit-site rows with no colon, so is_host_row (registry.py:72-73) is false for every row and --trusted-checkout changes nothing. The fail_loud_ratchet row is `status: unenforced` (:90-94), so a push run executes no whole-tree row. The existing job already checks out with fetch-depth 0 (ci.yml:13-15) and runs the same gate at ci (ci.yml:40). On a push to main the base derives to origin/main, the three-dot diff is empty, and active ast rows exist at ci (empty_catch :9-13 and others), so the run prints 'No findings.' and exits 0, as today's step does.

#### C44 — SURVIVED
- evidence: `plugins/arch-compliance/tests/test_adr_citation_history.py:20; plugins/arch-compliance/tests/test_adr_citation_history.py:23-24`
- reasoning: test_adr_citation_history.py:20 defines `-c user.email=... -c user.name=ci -c commit.gpgsign=false`, and :23-24 prepends it to every git call. That is per-command identity with no repo config, the exact pattern claimed, and the spec body cites it correctly at :201-202. The claim's own parenthetical cites test_diff_cli.py:32-33, which sets identity through `git config user.email/user.name`, not `-c`. That citation is imprecise but does not falsify the claim: both forms work without a global identity.

### Unanchored findings

- **advisory**: Step 7 refuses every shallow clone, including one deep enough to hold the merge base where acf-check-diff would run correctly, so it adds a refusal rather than 'only improving the message'. Narrowing it to stop only when the repository is shallow and `git merge-base <base> HEAD` fails would make it purely a message improvement over GitError.
  - evidence: `plugins/arch-compliance/python/acf/diff.py:33-45`
- **advisory**: Hand tagging leaves the tag-to-version correspondence unchecked: a tag pushed on a commit whose plugin.json/pyproject version differs from the tag name resolves fine at hosts and silently runs different detectors. A read-only check, needing no tag-pushing token, that compares the tag name with these version fields (on tag push, or in post-merge) would refuse at the producer.
  - evidence: `plugins/arch-compliance/.claude-plugin/plugin.json:3`

### Looked for but did not find

- A repair or fallback in any added mechanism: every stop the action adds (step 1 files, step 2 Windows, trusted-checkout value, failed host-setup, step 7 shallow) refuses; none rewrites or auto-fetches
- A pytest python_files override or conftest that would collect tests/action_fixture_host.py (none in pyproject.toml:23-25, no pytest.ini/setup.cfg/tox.ini/conftest.py)
- Host rows or an active ratchet in this repository's mandates.yml that would make --trusted-checkout or a push run consequential (none; ratchet unenforced at :90-94)
- A rung-1 alternative to the step-1 premise: shipping the TS pack as package-data (pyproject.toml:39-40) would still leave the action installing from its own path at the pinned ref, so the premise and its refusal remain; not raised as a finding
- An approval lookup ahead of the 'selects no active' refusal (none; cli_check_diff.py:102 follows :94-100)
- A stdin read by acf-check-diff that would conflict with the first adopter's hook consuming stdin (none; git runs with capture_output, diff.py:24-30)

### Mechanism traces

- **Step 1 self-check: stop unless pyproject.toml and the TS pack's package.json exist three levels above $GITHUB_ACTION_PATH**
  - invalid state: not exists($GITHUB_ACTION_PATH/../../../pyproject.toml) or not exists($GITHUB_ACTION_PATH/../../../plugins/arch-compliance/detectors/typescript/package.json)
  - producer: `docs/design/CHECK_DIFF_HOST_WIRING.md:271`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: That location holding this repository at the pinned ref is GitHub platform behaviour, which no file in this repository records. The design therefore does not rely on it silently (spec :76-80); a second checkout is the alternative not taken.
  - spec citation: `docs/design/CHECK_DIFF_HOST_WIRING.md:167-170`
- **Step 2: stop on a Windows runner**
  - invalid state: runner.os == 'Windows'
  - producer: `plugins/arch-compliance/python/acf/diff.py:24-30`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: Windows runners are a non-goal: the diff gate's git runner does not declare its text encoding (spec :136-139), deferred under ## Declared text decoding.
  - spec citation: `docs/design/CHECK_DIFF_HOST_WIRING.md:171`
- **trusted-checkout input validation: any value other than true/false stops the action**
  - invalid state: inputs.trusted-checkout not in {'true','false'}
  - producer: `docs/design/CHECK_DIFF_HOST_WIRING.md:283`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/CHECK_DIFF_HOST_WIRING.md:160`
- **Step 7: stop naming fetch-depth: 0 on a shallow clone**
  - invalid state: git rev-parse --is-shallow-repository == 'true' for <repo> (the defect it targets is the narrower: shallow and merge-base(base, HEAD) absent)
  - producer: `docs/design/CHECK_DIFF_HOST_WIRING.md:268-270`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: This only improves the message: without it, the missing merge base already makes acf-check-diff refuse with a GitError, and that refusal stays the authoritative one (spec :183-186).
  - spec citation: `docs/design/CHECK_DIFF_HOST_WIRING.md:182-186`
- **Pre-push guard flag ACF_PREPUSH_OPTIONAL=1 (skip when acf-check-diff is absent; refuse otherwise)**
  - invalid state: pre-push runs in an environment where `command -v acf-check-diff` fails
  - producer: `plugins/arch-compliance/skills/acf-setup/SKILL.md:67-75`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: That variable is set by whoever owns an environment where CI is meant to be the only gate ... and is never committed to the repository, so a fresh clone that has not installed the tool is stopped, not silently passed (spec :107-110).
  - spec citation: `docs/design/CHECK_DIFF_HOST_WIRING.md:292-301`

## Claims

- **C1** [premise] [load-bearing]: The TypeScript detector bridge locates its Node scanner relative to its own source file (_PACK_ROOT = Path(__file__).resolve().parents[3] / 'detectors' / 'typescript') and pyproject.toml's package data ships no detectors/typescript (pyproject.toml:39-40), so a wheel install cannot scan .ts/.tsx files; the runner needs an editable install from a source checkout plus `npm ci` in plugins/arch-compliance/detectors/typescript.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:20`
- **C2** [premise] [load-bearing]: With --base, the changed-file list and added lines are the three-dot diff (diff.py:43-46), so on a push where origin/<default> is HEAD every per-file check sees nothing; but an active fail_loud_ratchet row scans the tree against its baseline regardless of the diff (cli_check_diff.py:212-226) and host guard rows are called whatever the diff holds (:228-230). This is why the snippet triggers on pull_request and /acf-setup adds a push trigger only for hosts with either kind of row active at ci.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:212-230`
- **C3** [premise] [load-bearing]: acf-check-diff returns 1 for a BLOCK finding (:119-121) and for a caught refusal alike (:106-108); caught refusals print a line beginning `acf:`, and a missing approval, a TypeScript pack without `npm ci` and an unresolvable base each say what failed; an uncaught exception or a usage error also exits non-zero. The pre-push step blocks on every non-zero exit on the strength of this; telling a refusal from a finding would need stderr parsing.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:106-108`
- **C4** [premise]: The pre-push step's three known gaps hold as stated: working-tree reads against a committed diff (:145, :153, :189) can move a line, hide a committed violation or skip a deleted file; the diff is of the checked-out branch (diff.py:43-46); the local origin/<default-branch> is not fetched. The first two states are detectable but the spec rejects refusing them with written reasons (dirty trees are ordinary; refs arrive on stdin, which the first adopter's hook already consumes at cy:.githooks/pre-push:7), and the pull request's CI job checks a clean checkout of what merges.
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
- **C13** [premise] [load-bearing]: The gate imports a host detector module into its own process (spec_from_file_location / exec_module, host.py:102-109), so a host detector's third-party Python packages must be importable by the interpreter running acf-check-diff, which is the action's own venv; that venv does not exist until the action creates it, so host-setup (run after the action's setup, venv bin first on PATH) is the supported place to install into it.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/host.py:102-109`
- **C14** [mandate] [load-bearing]: Trust boundary: --trusted-checkout is carried by the CI action (default on, input trusted-checkout) and by no local command the design prints: the pre-push command omits it and the README and guide local examples drop it; naming the action in a workflow is the CI opt-in the trust boundary and acf-setup SKILL.md:249 describe, and :249's wording is updated to name the action and the pre-push command.
  - spec citation: `config/architecture/ARCHITECTURE.md:178-181`
- **C15** [mandate] [load-bearing]: Release discipline: acf-setup's prose changes, so the version goes to 0.3.4 in plugin.json and pyproject.toml; a tagging rule (tag the merge commit once main's CI run for it has passed) is added to the section; acf-setup is not among the four skill trees scripts/check_installed_skills.py byte-checks, so no reinstall is owed.
  - spec citation: `config/architecture/ARCHITECTURE.md:274-284`
- **C16** [mandate] [load-bearing]: Call-site rule: reusing the precommit call site for a pre-push hook, with the doctrine sentence '`precommit` is the local git-hook site, whichever hook (pre-commit or pre-push) runs it', stays inside the closed vocabulary and adds no site value.
  - spec citation: `config/architecture/ARCHITECTURE.md:140-187`
- **C17** [mandate] [load-bearing]: Prose names no host: the acf-setup changes and the action name no host repository, path or section (generic placeholders; the first adopter appears only in the spec's §8).
  - spec citation: `config/architecture/ARCHITECTURE.md:223-233`
- **C18** [mandate] [load-bearing]: Live consumers: tests/action_fixture_host.py is test scaffolding (no package code, hook or skill calls it; it builds fixtures for the action's CI test), not an export, so the rule ('An export has a live call site in the package, a hook or a skill') does not govern it; the action itself has a live consumer in a skill (/acf-setup step 8 prints it for hosts).
  - spec citation: `config/architecture/ARCHITECTURE.md:243-247`
- **C19** [mandate] [load-bearing]: One owner for host paths and Single point of definition: tests/action_fixture_host.py takes its two config paths from acf.repo (MANDATES_REL, ARCH_REL at repo.py:21, :24), as ARCHITECTURE.md:120-122 asks of repository-level tests/ and scripts/; /acf-setup decides whether a site has an active row by running acf-check-diff itself and reading its 'selects no active' refusal (cli_check_diff.py:94-100) rather than restating the predicate, and its CI push-trigger check consumes load_gate_registry / active / host_rows rather than reading the YAML by eye.
  - spec citation: `config/architecture/ARCHITECTURE.md:115-138`
- **C20** [mandate] [load-bearing]: Single point of definition: after the change the base-ref derivation has one owner (the action; the plugin's own inline gate step at ci.yml:39-40 is removed), and the install recipe's three copies (acf-setup step 4 for a developer machine, the test job's `.[dev]` install for pytest and the TS self-test, the action's venv on a host runner) are three installs for three environments, recorded in the section as declared breaches with the reason they stay apart.
  - spec citation: `config/architecture/ARCHITECTURE.md:286-303`
- **C21** [mandate] [load-bearing]: Declared, never defaulted: the pre-push opt-out ACF_PREPUSH_OPTIONAL has no default (unset or any value other than 1 means refuse), and the action's input defaults (repo '.', trusted-checkout 'true', base derived from the event, Python/Node versions) are recorded in the section beside the package defaults it already lists (:212-221) as outside the rule, being action inputs and not host declarations a gate reads.
  - spec citation: `config/architecture/ARCHITECTURE.md:189-221`
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
- **C27** [sweep]: The places describing or printing the pre-commit/CI wiring that change are: acf-setup SKILL.md frontmatter, checklist item 8, step 8 heading and body, the --trusted-checkout paragraph (:249), the upgrading section (:251-258, incl. :253 and the :258 install reminder) and the step 10 summary (:285); docs/guides/SUPERPOWERS_COMPLEMENT.md:40 and its command block :78-83 and flag prose :87; README.md command block :53-58, flag prose :62 and a new upgrade note beside :112; .github/dependabot.yml; and this repository's ## Post-merge CI bullet (ARCHITECTURE.md:330). Step 9 and the friend-bar tip deliberately keep --mode. Obligation: sweep the tracked tree outside docs/design, docs/plans and docs/reviews by behaviour for other stale wiring descriptions.
  - spec citation: `docs/guides/SUPERPOWERS_COMPLEMENT.md:40`
- **C28** [mechanism_justification] [load-bearing]: A composite action is justified over templates copied into each host (they drift; today's CI sketch at acf-setup SKILL.md:239-247 is such a template) and over a reusable workflow (it owns the host's whole job); the host keeps its triggers, runner and dependants.
  - spec citation: `None`
- **C29** [mechanism_justification] [load-bearing]: The action's step 1 self-check (stop, naming both paths, unless pyproject.toml and the TS pack's package.json are three levels above $GITHUB_ACTION_PATH) is justified over a second checkout of the plugin repository inside the action: it refuses rather than repairs, and it turns an unverifiable platform premise into a loud failure at the first adopter's run.
  - spec citation: `None`
- **C30** [mechanism_justification] [load-bearing]: One host-setup input, run after the action's setup with the venv's bin first on PATH, is justified because host detector modules run in the gate's process and so their Python packages must be in the action's venv; Node dependencies could also come from earlier steps (they stay on disk), and host-setup is the documented single place for both.
  - spec citation: `None`
- **C31** [mechanism_justification] [load-bearing]: The pre-push step refusing when acf-check-diff is absent unless the environment sets ACF_PREPUSH_OPTIONAL=1, and blocking on every non-zero exit once installed, is justified: an absent tool is stopped by default rather than silently passed; the opt-out is a declaration by whoever owns an environment where CI is the only gate, kept out of the repository so a fresh clone still refuses; refusals and findings share exit 1, so separating them would need stderr parsing.
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
- **C39** [implementability] [load-bearing]: The pre-push snippet behaves as written when placed at a hook's top level, with or without set -e: a gate failure ends the hook through `|| exit 1`; with the tool absent and ACF_PREPUSH_OPTIONAL unset or not '1' the final `exit 1` ends it with an install hint; with ACF_PREPUSH_OPTIONAL=1 it prints the skip line and continues; `${ACF_PREPUSH_OPTIONAL:-}` is safe under set -u. Placements: a pre-push file in the core.hooksPath directory or .git/hooks/pre-push, or the host's hook manager configured for pre-push. In the first adopter's .githooks/pre-push (set -e, a docs-only skip that exits 0 at top level) it goes at top level after the skip.
  - spec citation: `None`
- **C40** [implementability] [load-bearing]: /acf-setup's checks work as specified: `acf-check-diff --mode worktree --call-site <site>` reaches the 'selects no active' refusal (cli_check_diff.py:94-100) before any approval lookup (:102), so it answers the question even for a host with unapproved host rows; and the push-trigger check can use acf.detectors.load_gate_registry(repo, mandates_path), MandateRegistry.active(sites, detector='fail_loud_ratchet') and host_rows(sites, detection='guard').
  - spec citation: `plugins/arch-compliance/python/acf/registry.py:130-147`
- **C41** [implementability] [load-bearing]: The action's third run against this repository (repo: ., base empty, trusted-checkout default true) works in the new `action` job: this repository has no host rows, so --trusted-checkout changes nothing; the job checks out with fetch-depth 0; and the run on a push to main sees an empty diff and passes, as today's step does.
  - spec citation: `.github/workflows/ci.yml:39-40`
- **C43** [premise]: This repository's ## Post-merge CI bullet today names `.github/workflows/ci.yml` (`test` job on `main`); the design moves this repository's gate run into a new `action` job of the same workflow and updates the bullet to name both jobs.
  - spec citation: `config/architecture/ARCHITECTURE.md:330`
- **C44** [implementability] [load-bearing]: tests/action_fixture_host.py can commit on a runner with no git identity by passing one per command (`git -c user.name=... -c user.email=... -c commit.gpgsign=false commit`), as the repository's git-fixture tests set an identity (test_diff_cli.py:32-33).
  - spec citation: `plugins/arch-compliance/tests/test_diff_cli.py:32-33`
