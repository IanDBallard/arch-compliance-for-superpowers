# Adversarial design review — full detail

Spec: `docs/design/CHECK_DIFF_HOST_WIRING.md` @ `9f4eec4c61fe8617fdccc0281673db012b4d98be`
Kinds: feature
Outcome: **BLOCKED**
Claims: 34 · Reviewers: 4 · Converged: 3

## Blocking reasons

- load-bearing claim C7 (premise) is UNPROVEN: The claim is about GitHub runner behaviour: a remote composite action's whole repository is downloaded at the ref, so ../../.. from action_path is the repository root. No file in either repository shows it, and I have no web access to GitHub's documentation. For the local './.github/actions/check-diff' case it follows from the workspace checkout, but the remote case cannot be re-derived here. The spec itself defers the proof to §8's first-adopter run. Load-bearing and not established by a second reader.
- load-bearing claim C10 (premise) is UNPROVEN: The relative half holds. Today's sketch already passes --trusted-checkout (SKILL.md:245), and a host's CI already runs PR code (Cayenne's CI runs npm test on pull_request), so the action adds no new class of exposure compared with the sketch. The stated cause, that fork pull_request runs get a read-only GITHUB_TOKEN and no secrets, is GitHub platform behaviour with no repository file to resolve. Cayenne's ci.yml:64-65 comment assumes the no-secrets half, but that is a host's belief, not proof, and nothing touches the read-only-token half. Repository settings can also change this behaviour, for example sending write tokens or secrets to fork PRs in private repositories. Not re-derivable here.
- load-bearing claim C13 (premise) is UNPROVEN: That setup-python and setup-node write GITHUB_PATH, so the change persists past a composite action for the rest of the job, is GitHub runner behaviour that no repository file shows; I cannot re-derive it here. The causal chain's conclusion is also overstated. Node dependencies installed before the action stay on disk and are found by path: Cayenne's detector locates ESLint at a fixed file path (:31-33) and only runs 'node' from PATH (:44). An 'npm ci --prefix cayenne-web' step before the action would therefore still work with the action's Node, barring native-addon ABI mismatches. The real reason Python detector dependencies must go through host-setup is that step 3 builds an isolated venv (spec :132-134), not PATH supersession. Load-bearing; the premise is not established and the 'must' does not follow as stated.
- load-bearing claim C18 (mandate) is REFUTED: The mandate reads 'An export has a live call site in the package, a hook or a skill. A test is not a consumer' (:245-246). The claim offers the new `action` CI job as the live consumer of scripts/make_action_fixture_host.py. The spec itself titles that job 'The action's test' (spec :151), and the job does what a test does: it builds fixtures, runs the action, and asserts outcomes (spec :164-170). It is also neither the package, a hook nor a skill. So the claim's stated reason is exactly what the mandate rules out. The action half survives: acf-setup step 8, a skill, prints it for hosts (spec :176-191). For the script, the accurate framing is that it is test scaffolding, the test itself rather than production code with a test attached. The rule's 'dead code with a test attached' then does not describe it, which suggests either placing it as test infrastructure or saying the rule does not govern fixture builders. As written, the claim misstates the mandate. The fix is precision only.
- load-bearing claim C32 (implementability) is REFUTED: The row as §4.2:156-158 lists it (id, BLOCK, ast, empty_catch, typescript, call_sites [ci], enforced, arch_anchor) leaves out two Mandate fields that have no default: `title: str` (registry.py:52) and `exemption_tokens: list[str]` (registry.py:58). Validating that row raises ValidationError, which load_model_file turns into AcfInputError (loader.py:70-73), and the CLI exits 1 with `acf: invalid mandates file`. The first adopter's real row carries both fields (cy mandates.yml:8, :14). The fix is precision only: add a title and `exemption_tokens: []`. Everything else in the claim checks out. empty_catch is a built-in that reports to fail-loud.empty-catch at every Tier-1 site including ci (detectors/__init__.py:44-47; registry.py:201-217), so a [ci]-only row passes the Tier-1 and contract checks (registry.py:99-103). There are no host rows, so check_approval returns NOT_NEEDED (approval.py:128-129) and --trusted-checkout does not matter. acf-check-diff never reads ARCHITECTURE.md (missing_anchors has no caller), .acf/enabled (hook only), or adr.yml, so those files are harmless but not needed. `--base main` becomes `git diff main...HEAD`, a local three-dot that needs no remote (diff.py:42-45). An added empty `catch {}` produces a finding on the catch line (detectors/typescript/src/rules/emptyCatch.ts:11-26), kept by apply_registry as BLOCK (enforcement.py:60-67), and the run exits 1 (cli_check_diff.py:119-120). Because the fixture row as written would not load, the claim that it 'loads without error' is false.
- mandate claim C18 is REFUTED: The mandate reads 'An export has a live call site in the package, a hook or a skill. A test is not a consumer' (:245-246). The claim offers the new `action` CI job as the live consumer of scripts/make_action_fixture_host.py. The spec itself titles that job 'The action's test' (spec :151), and the job does what a test does: it builds fixtures, runs the action, and asserts outcomes (spec :164-170). It is also neither the package, a hook nor a skill. So the claim's stated reason is exactly what the mandate rules out. The action half survives: acf-setup step 8, a skill, prints it for hosts (spec :176-191). For the script, the accurate framing is that it is test scaffolding, the test itself rather than production code with a test attached. The rule's 'dead code with a test attached' then does not describe it, which suggests either placing it as test infrastructure or saying the rule does not govern fixture builders. As written, the claim misstates the mandate. The fix is precision only.
- implementability claim C32 is REFUTED: The row as §4.2:156-158 lists it (id, BLOCK, ast, empty_catch, typescript, call_sites [ci], enforced, arch_anchor) leaves out two Mandate fields that have no default: `title: str` (registry.py:52) and `exemption_tokens: list[str]` (registry.py:58). Validating that row raises ValidationError, which load_model_file turns into AcfInputError (loader.py:70-73), and the CLI exits 1 with `acf: invalid mandates file`. The first adopter's real row carries both fields (cy mandates.yml:8, :14). The fix is precision only: add a title and `exemption_tokens: []`. Everything else in the claim checks out. empty_catch is a built-in that reports to fail-loud.empty-catch at every Tier-1 site including ci (detectors/__init__.py:44-47; registry.py:201-217), so a [ci]-only row passes the Tier-1 and contract checks (registry.py:99-103). There are no host rows, so check_approval returns NOT_NEEDED (approval.py:128-129) and --trusted-checkout does not matter. acf-check-diff never reads ARCHITECTURE.md (missing_anchors has no caller), .acf/enabled (hook only), or adr.yml, so those files are harmless but not needed. `--base main` becomes `git diff main...HEAD`, a local three-dot that needs no remote (diff.py:42-45). An added empty `catch {}` produces a finding on the catch line (detectors/typescript/src/rules/emptyCatch.ts:11-26), kept by apply_registry as BLOCK (enforcement.py:60-67), and the run exits 1 (cli_check_diff.py:119-120). Because the fixture row as written would not load, the claim that it 'loads without error' is false.

## Absorptions

- PARTIAL_OVERLAP: 'action input `base` (empty means origin/<github.base_ref> or the default branch)' shares responsibility 'derive the diff base ref for a pull-request run' with .github/workflows/ci.yml:40 — R = choose the base ref from the GitHub event. Either have the plugin's own gate step call the action (`uses: ./.github/actions/check-diff`, `repo: .`) so the action is the one owner, or state in the action that ci.yml:40 deliberately keeps its own derivation and why.
- PARTIAL_OVERLAP: 'action step 6 (refuse a shallow clone, naming fetch-depth: 0)' shares responsibility 'refuse when no merge base is available' with plugins/arch-compliance/python/acf/diff.py:33-39 — R = fail when the three-dot diff has no merge base. acf-check-diff already refuses through GitError (cli_check_diff.py:106-108). The action's check only improves the message, so keep it as a precondition hint and treat GitError as the authoritative refusal; no other logic should depend on the action's check.
- IDENTICAL: '/acf-setup step 8 guarded pre-push command' shares responsibility 'invoke acf-check-diff at the precommit call site' with plugins/arch-compliance/skills/acf-setup/SKILL.md:214-227 — Replace in place, as §4.3 states: the pre-commit block is deleted and the pre-push block takes its place.

## Converged findings

- [2 reviewers: refuter, hardening] The action's `repo` input is defined as relative to the workspace, but the §4.2 test points it at fixtures under $RUNNER_TEMP, outside the workspace; the input must also accept an absolute path.
  - evidence: `docs/design/CHECK_DIFF_HOST_WIRING.md:122`
  - evidence: `docs/design/CHECK_DIFF_HOST_WIRING.md:164-166`
- [2 reviewers: refuter, hardening] The reason given for host-setup is overstated for Node: node_modules installed by a step before the action stay on disk and are found by path after setup-node; only Python packages truly need to land in the action's venv.
  - evidence: `C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/detectors/eslint_rules.py:33`
  - evidence: `plugins/arch-compliance/python/acf/detectors/host.py:102-109`
- [2 reviewers: sweeper, compliance] The base-ref derivation gains a second owner: the action computes origin/<base_ref or default branch> while the plugin's own CI step keeps its inline `origin/${{ github.base_ref || 'main' }}`.
  - evidence: `.github/workflows/ci.yml:40`

## refuter

### Claim verdicts

#### C1 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:20; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:98-103; pyproject.toml:31-40`
- reasoning: _PACK_ROOT is parents[3] of the bridge file. In the source tree that is plugins/arch-compliance, so it resolves to plugins/arch-compliance/detectors/typescript, which holds package.json and package-lock.json. scan_typescript_file raises DetectorPackError when that directory or its node_modules is missing (:98-103). pyproject's package-data covers only judge_prompt.md and review/packs/*.yml (:39-40), and packages.find is rooted at plugins/arch-compliance/python (:31-32). A wheel therefore ships no detectors/typescript, and from site-packages parents[3] points at no pack. The pyproject comment at :34-36 says the editable install hides this. One nuance: running from the source tree via PYTHONPATH would also work, so 'editable install' is sufficient but not strictly the only route. That does not affect the design.

#### C2 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:42-45; plugins/arch-compliance/python/acf/diff.py:56; plugins/arch-compliance/python/acf/diff.py:68; plugins/arch-compliance/python/acf/cli_check_diff.py:135; plugins/arch-compliance/python/acf/cli_check_diff.py:148`
- reasoning: With base set, _diff_args returns [f'{base}...HEAD']. changed_files (:56) and added_lines (:68) both use it, and _scan_changed calls both with base (:135, :148). When origin/<default> equals HEAD the merge base is HEAD, so the diff is empty and every per-file scan is skipped. Caveat, reported separately as an unanchored finding: whole-tree checks still run regardless of the diff (the fail_loud_ratchet loop at cli_check_diff.py:212-226 and scan_host_guards at :228-230). So 'checks nothing' is exact only for per-file rows. The rationale for pull_request-only still holds for diff-scoped rows.

#### C3 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:106-108; plugins/arch-compliance/python/acf/cli_check_diff.py:119-120; plugins/arch-compliance/python/acf/approval.py:150-154; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:100-103; plugins/arch-compliance/python/acf/diff.py:36-38`
- reasoning: GitError, AcfInputError, UnknownDetectorError and DetectorPackError are all caught. The handler prints 'acf: {exc}' and returns 1 (:106-108). A BLOCK finding also returns 1 (:119-120). Each of the three named refusals names its fix. A missing or stale approval raises AcfInputError that says to run acf-allow (approval.py:150-154). Missing node_modules raises DetectorPackError carrying _npm_ci_hint (typescript_bridge.py:100-103, :26-30). An unresolvable base raises GitError quoting the failing 'git diff <base>...HEAD' and git's stderr (diff.py:36-38). Not every refusal names a fix, though (advisory below).

#### C4 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:145; plugins/arch-compliance/python/acf/cli_check_diff.py:153; plugins/arch-compliance/python/acf/cli_check_diff.py:189; plugins/arch-compliance/python/acf/repo.py:123-126`
- reasoning: RepoTree.file returns the existing regular file on disk inside the root (repo.py:123-126), so the text read at :153 and :189 is the working-tree copy. The line numbers come from the committed three-dot diff (:148). Uncommitted edits can therefore shift a reported line in a local run.

#### C5 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:274-284; ran `git tag` (empty), `git for-each-ref refs/tags | wc -l` (0) and `git ls-remote --tags origin` (exit 0, no output)`
- reasoning: There are no local tags and the remote lists none. The current Release discipline section (ARCHITECTURE.md:274-284) has no tagging rule, which fits no tag having been cut.

#### C6 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:223; plugins/arch-compliance/skills/acf-setup/SKILL.md:245; plugins/arch-compliance/skills/acf-setup/SKILL.md:258`
- reasoning: The pre-commit entry is 'acf-check-diff --mode staged --call-site precommit' (:223). The CI sketch runs 'acf-check-diff --base ... --repo . --call-site ci --trusted-checkout' (:245) and has no install step. Step 8 does close with a generic reminder: install the acf package into the environment used by hooks or CI, via pip or editable install per the README (:258). It says nothing about the TypeScript pack's npm ci on the runner and gives no concrete runner recipe. The claim holds for the sketch as worded.

#### C7 — UNPROVEN
- evidence: `searched both repositories for github.action_path / GITHUB_ACTION_PATH usage (none outside the spec); no repository file documents the runner's download layout for owner/repo/path@ref`
- reasoning: The claim is about GitHub runner behaviour: a remote composite action's whole repository is downloaded at the ref, so ../../.. from action_path is the repository root. No file in either repository shows it, and I have no web access to GitHub's documentation. For the local './.github/actions/check-diff' case it follows from the workspace checkout, but the remote case cannot be re-derived here. The spec itself defers the proof to §8's first-adopter run. Load-bearing and not established by a second reader.

#### C8 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/detectors/eslint_rules.py:20-33; C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/detectors/eslint_rules.py:41-44; C:/Users/iball/Arduino/Projects/Cayenne/.github/workflows/ci.yml:94; C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/mandates.yml:143; C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/mandates.yml:162; C:/Users/iball/Arduino/Projects/Cayenne/cayenne-web/eslint.config.js:45`
- reasoning: The imports are stdlib plus acf.detectors.host and acf.engine (:20-29); acf.engine.is_in_scope exists at plugins/arch-compliance/python/acf/engine.py:70. ESLINT is cayenne-web/node_modules/eslint/bin/eslint.js (:33), run by 'node' from PATH (:44), and the detector raises if it is missing (:41-42). Cayenne CI pins node-version '22' (ci.yml:94). On the obligation: Cayenne at 7313bca5 has exactly two host rows, soft.state-machines and soft.device-storage-owner. Both are enforced ast/typescript rows with call_sites [ci, precommit, audit], and both live in eslint_rules.py (mandates.yml:143, :162); config/architecture/detectors/ holds only that file. Their ESLint config imports only packages from cayenne-web and local files, and is not type-aware (parserOptions sets just the parser, eslint.config.js:45). So nothing beyond cayenne-web's node_modules and a node on PATH is needed. Side effect: cayenne-web's prepare script runs svelte-kit sync and install-hooks.mjs (cayenne-web/package.json:14) during host-setup's npm ci. Cayenne CI already does this, so it is harmless.

#### C9 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/Cayenne/.github/workflows/ci.yml:6-7; ran `git grep -c -i acf 7313bca5 -- .github .githooks` in Cayenne (exit 1, no output); ran `gh api repos/IanDBallard/Cayenne/branches/main/protection` (404 'Branch not protected'); C:/Users/iball/Arduino/Projects/Cayenne/.githooks/pre-push:1-18`
- reasoning: No acf reference exists under .github or .githooks at the cited commit. The pre-push hook runs only check, lint and test. The ci.yml comment says main has no required status checks, and the protection API confirms it.

#### C10 — UNPROVEN
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:245; C:/Users/iball/Arduino/Projects/Cayenne/.github/workflows/ci.yml:64-65`
- reasoning: The relative half holds. Today's sketch already passes --trusted-checkout (SKILL.md:245), and a host's CI already runs PR code (Cayenne's CI runs npm test on pull_request), so the action adds no new class of exposure compared with the sketch. The stated cause, that fork pull_request runs get a read-only GITHUB_TOKEN and no secrets, is GitHub platform behaviour with no repository file to resolve. Cayenne's ci.yml:64-65 comment assumes the no-secrets half, but that is a host's belief, not proof, and nothing touches the read-only-token half. Repository settings can also change this behaviour, for example sending write tokens or secrets to fork PRs in private repositories. Not re-derivable here.

#### C11 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-100; plugins/arch-compliance/python/acf/registry.py:72-73; plugins/arch-compliance/python/acf/detectors/host.py:191; plugins/arch-compliance/python/acf/detectors/host.py:220; plugins/arch-compliance/python/acf/detectors/__init__.py:59-72`
- reasoning: cli_check_diff imports no LLM or judge runner and only checks for active ast or guard rows (:94-100). Host rows are by definition ast or guard (registry.py:72-73), and the host scanners select detection='ast' (host.py:191) and 'guard' (host.py:220). load_gate_registry imports acf.judge only to read LLM_PROMPT_IDS for validation (__init__.py:59-72). The provider-key environment reads in judge.py (:66-95) sit inside functions, so no provider key is needed.

#### C12 — REFUTED
- evidence: `config/architecture/ARCHITECTURE.md:260-271; plugins/arch-compliance/python/acf/diff.py:24-30; CLAUDE.md (Windows note: run the diff gate with PYTHONUTF8=1)`
- reasoning: The deferral itself is a design choice and is fine. The factual sub-claim is not: Windows support would not be 'the same design plus a venv-layout branch' alone. The doctrine's 'Declared text decoding' section records that run_git (diff.py:24-30), the gate's git runner, decodes with text=True and no declared encoding, along with the Node scanner bridge. The repository's own Windows note requires PYTHONUTF8=1 for the diff gate until that is fixed. A Windows branch would also need the UTF-8 environment, or the follow-up-1 fix. Not load-bearing.

#### C13 — UNPROVEN
- evidence: `C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/detectors/eslint_rules.py:31-33; C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/detectors/eslint_rules.py:44; docs/design/CHECK_DIFF_HOST_WIRING.md:132-134`
- reasoning: That setup-python and setup-node write GITHUB_PATH, so the change persists past a composite action for the rest of the job, is GitHub runner behaviour that no repository file shows; I cannot re-derive it here. The causal chain's conclusion is also overstated. Node dependencies installed before the action stay on disk and are found by path: Cayenne's detector locates ESLint at a fixed file path (:31-33) and only runs 'node' from PATH (:44). An 'npm ci --prefix cayenne-web' step before the action would therefore still work with the action's Node, barring native-addon ABI mismatches. The real reason Python detector dependencies must go through host-setup is that step 3 builds an isolated venv (spec :132-134), not PATH supersession. Load-bearing; the premise is not established and the 'must' does not follow as stated.

### Unanchored findings

- **important**: The action's `repo` input is defined as relative to the workspace, but the design's own CI test (§4.2) builds its fixtures under $RUNNER_TEMP, outside GITHUB_WORKSPACE. The spec never says the input also accepts absolute paths, which the test needs.
  - evidence: `docs/design/CHECK_DIFF_HOST_WIRING.md:122`
- **advisory**: Whole-tree checks run regardless of an empty diff. The fail_loud_ratchet scans the full tree against its baseline and host guards are called on every run. So a push-to-default run is not strictly empty, and making the gate pull_request-only removes a post-merge ratchet check that hosts with a ci ratchet row may rely on; the spec does not state this.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:212-226`
- **advisory**: Decision 6's statement that 'each refusal prints acf: naming its fix' does not cover every refusal. A missing pack directory, the wheel-install case, prints only 'TypeScript detector pack not found'. An OSError from RepoTree.file at cli_check_diff.py:145 falls outside the caught exception tuple and exits with a traceback, with no acf: line.
  - evidence: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:99-100`
- **advisory**: The pre-push snippet blocks every push with the 'selects no active ast or guard mandate' refusal when a host's rows do not declare precommit. §4.3 does not tell /acf-setup to check that rows declare precommit before proposing the hook.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:94-100`
- **advisory**: The workflow snippet pins actions/checkout@v4, while this repository's CI and the first adopter's CI both use actions/checkout@v7.
  - evidence: `.github/workflows/ci.yml:13`

### Looked for but did not find

- any git tag, local or on origin, in the plugin repository
- any acf reference under .github or .githooks in Cayenne at 7313bca5
- a third host detector file or host row in Cayenne beyond eslint_rules.py's two rows
- type-aware ESLint parserOptions (project/projectService) in cayenne-web/eslint.config.js that would need a generated .svelte-kit tsconfig at lint time
- a module-level LLM provider key read in acf.judge that importing it from load_gate_registry would trigger
- package-data in pyproject.toml shipping detectors/typescript in a wheel
- any repository file documenting github.action_path or the remote composite-action download layout
- a code path in cli_check_diff that runs llm-detection rows

## compliance

### Claim verdicts

#### C14 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:178-181; plugins/arch-compliance/skills/acf-setup/SKILL.md:249; plugins/arch-compliance/python/acf/cli_check_diff.py:76-82; plugins/arch-compliance/python/acf/cli_check_diff.py:102; docs/design/CHECK_DIFF_HOST_WIRING.md:123; docs/design/CHECK_DIFF_HOST_WIRING.md:217-218`
- reasoning: The doctrine says both gates run host code only with an approval 'or, for `acf-check-diff`, when the invocation passes `--trusted-checkout`' (ARCHITECTURE.md:178-181). The spec quotes this correctly. In the design, the action's own acf-check-diff invocation passes the flag when the input is 'true' (spec :123, :144-145), and cli_check_diff.py:102 skips require_approval only in that case. So the boundary's mechanism is unchanged. SKILL.md:249 ('in CI the workflow file is the opt-in. Only the CI sketch carries it. Never add it to the pre-commit snippet') is kept: the pre-push snippet (spec :205-206) has no flag, and spec :217-218 restates the rule. The flag's own help text (cli_check_diff.py:79-80) gives the same 'workflow file is the opt-in' rationale. One caveat, which does not refute the claim: with the input defaulting to true, the opt-in is no longer a visible token in the host's workflow file, only the `uses:` line. The spec deals with this by having the skill paragraph name the input as 'the place it lives' (spec :199-200).

#### C15 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:276-281; scripts/check_installed_skills.py:18-22; pyproject.toml:3; plugins/arch-compliance/.claude-plugin/plugin.json:3; docs/design/CHECK_DIFF_HOST_WIRING.md:237-238`
- reasoning: The doctrine says 'A change to a skill's prose bumps the plugin version in plugins/arch-compliance/.claude-plugin/plugin.json and pyproject.toml' (:276-277). Both files are at 0.3.3 today (pyproject.toml:3, plugin.json:3), and the design bumps both to 0.3.4 (spec :237-238). The byte check covers 'the two gate skills, post-merge-housekeeping and architecture-review' (:278-281). GATE_SKILLS in scripts/check_installed_skills.py:18-22 lists adversarial-design-review, responding-to-adversarial-review, post-merge-housekeeping and architecture-review, and acf-setup is not among them. The design edits none of those four trees, so the section asks for no other step. The added tagging sentence (spec :235-236) extends the section; it does not contradict it.

#### C16 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:154-158; plugins/arch-compliance/python/acf/registry.py:18; plugins/arch-compliance/python/acf/cli_check_diff.py:64-69; docs/design/CHECK_DIFF_HOST_WIRING.md:232-234`
- reasoning: The call-site rule defines a closed vocabulary in which `ci` and `precommit` are the diff sites (ARCHITECTURE.md:154-158). DIFF_CALL_SITES is frozenset({'ci','precommit'}) (registry.py:18), and --call-site accepts only sorted(DIFF_CALL_SITES) (cli_check_diff.py:64-69). The pre-push snippet passes `--call-site precommit` (spec :206), which adds no site value. The new doctrine sentence (spec :232-234) defines which hook may invoke the existing site and does not change the vocabulary or the rule that a run executes only active rows declaring that site. The fixture row's `call_sites: [ci]` (spec :157) is a Tier-1 site, and the built-in empty_catch row carries its own mandate id, as the built-in contracts require (:169-174).

#### C17 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:225-226; docs/design/CHECK_DIFF_HOST_WIRING.md:126; docs/design/CHECK_DIFF_HOST_WIRING.md:179-191; docs/design/CHECK_DIFF_HOST_WIRING.md:205-209; docs/design/CHECK_DIFF_HOST_WIRING.md:281-285`
- reasoning: The rule reads 'Skill prose and runtime messages name no host repository, path or section' (:225-226). The skill text the design proposes uses generic placeholders: `.github/workflows/arch-compliance.yml` is a file the host adds, `<default-branch>`, `<version>`, and the host-setup example `npm ci --prefix web` (spec :126). The only repository named in the snippet is the plugin's own repository in the `uses:` line, which says where the action lives and does not name a host. The action's messages name only `fetch-depth: 0`, the input name and Windows (spec :123, :130, :141-143). The first adopter's `cayenne-web` appears only in §8, which records a change in the adopter's own repository (spec :281-285). No test currently holds acf-setup to the rule (:233, 'acf-setup ... have no row yet'), so review is the only check.

#### C18 — REFUTED
- evidence: `config/architecture/ARCHITECTURE.md:245-246; docs/design/CHECK_DIFF_HOST_WIRING.md:151; docs/design/CHECK_DIFF_HOST_WIRING.md:164-170`
- reasoning: The mandate reads 'An export has a live call site in the package, a hook or a skill. A test is not a consumer' (:245-246). The claim offers the new `action` CI job as the live consumer of scripts/make_action_fixture_host.py. The spec itself titles that job 'The action's test' (spec :151), and the job does what a test does: it builds fixtures, runs the action, and asserts outcomes (spec :164-170). It is also neither the package, a hook nor a skill. So the claim's stated reason is exactly what the mandate rules out. The action half survives: acf-setup step 8, a skill, prints it for hosts (spec :176-191). For the script, the accurate framing is that it is test scaffolding, the test itself rather than production code with a test attached. The rule's 'dead code with a test attached' then does not describe it, which suggests either placing it as test infrastructure or saying the rule does not govern fixture builders. As written, the claim misstates the mandate. The fix is precision only.

#### C19 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:191-196; config/architecture/ARCHITECTURE.md:212-221; docs/design/CHECK_DIFF_HOST_WIRING.md:119-126`
- reasoning: `## Declared, never defaulted` covers the adversarial-design-review gate's host values in adr.yml and the /architecture-review values in review.yml (:191-196). It records the package's built-in meanings and three defaults 'elsewhere in the package' that fall outside the rule (:212-221). The action's inputs (spec :119-126) are none of these. They are composite-action inputs outside the Python package and are not host declarations the gate reads. `base` is derived from github.base_ref or the default branch, not substituted for a declared value. The trust default is governed by `## Host detectors and call sites` (see C14), not this section. The spec's silence on the section is therefore not a breach. A self-contained spec could still have said in one line why the section does not apply.

#### C20 — UNPROVEN
- evidence: `config/architecture/ARCHITECTURE.md:121-122; plugins/arch-compliance/python/acf/repo.py:21; plugins/arch-compliance/python/acf/repo.py:24; docs/design/CHECK_DIFF_HOST_WIRING.md:153-159`
- reasoning: The doctrine says 'The repository-level tests/ and scripts/ follow the rule by importing the acf.repo constants, which review checks' (:121-122), and the constants exist (MANDATES_REL at repo.py:21, ARCH_REL at repo.py:24). The new scripts/make_action_fixture_host.py writes exactly config/architecture/mandates.yml and config/architecture/ARCHITECTURE.md into the fixture (spec :156-159). The spec does not say whether it imports MANDATES_REL and ARCH_REL or hardcodes the strings, so conformance cannot be established from the design.

#### C21 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:251-254; docs/design/CHECK_DIFF_HOST_WIRING.md:93; docs/design/CHECK_DIFF_HOST_WIRING.md:261; docs/design/CHECK_DIFF_HOST_WIRING.md:265; plugins/arch-compliance/python/acf/cli_check_diff.py:94-96`
- reasoning: The rule makes a factual claim about the tree non-load-bearing on 'every/all/only/complete/untouched/no second' unless a re-runnable recipe backs it (:251-254). I grepped the spec for those quantifiers. Each tree-fact hit is backed: 'no tags' by `git tag` (spec :93, :261); 'imports only the standard library and acf' by a line range (spec :265), which I re-ran: cy:config/architecture/detectors/eslint_rules.py:20-29 imports __future__, json, re, subprocess, collections.abc, pathlib and acf.* only; and 'LLM rows stay out of every automatic gate' (spec :105) by cli_check_diff.py:94-96, which selects ast/guard rows only. The other hits are design or normative statements ('No second checkout', 'never carries'), not claims about the tree. Separately, 'the one known gap' (spec :219) is a design statement rather than a tree census, but it omits a second gap; see the unanchored finding.

### Unanchored findings

- **important**: The scripts/make_action_fixture_host.py claim treats the action's CI test job as a 'live consumer', contrary to the Live consumers rule; the script should be framed as test scaffolding (C18).
  - evidence: `config/architecture/ARCHITECTURE.md:245-246`
- **advisory**: The spec does not say whether the new repository-level fixture script imports the acf.repo constants (MANDATES_REL, ARCH_REL) for the two config paths it writes, which `## One owner for host paths` requires of scripts/ and lists as a high-frequency miss.
  - evidence: `config/architecture/ARCHITECTURE.md:121-122`
- **advisory**: The pre-push command diffs `origin/<default-branch>...HEAD` (diff.py builds `{base}...HEAD`), so it checks the checked-out branch, not the refs git is pushing (`git push origin other-branch` checks the wrong commits); the spec's 'the one known gap' (spec :219) leaves this second gap out.
  - evidence: `plugins/arch-compliance/python/acf/diff.py:43-45`

### Looked for but did not find

- ## Fail loud / principle 1 (ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:47): the pre-push skip prints a line rather than passing silently, and the action stops with messages on Windows, a shallow clone and an invalid trusted-checkout value (spec :85-92, :123, :130, :141-143). Not breached.
- ## No shims: the action adds no fallback path; an installed gate that refuses blocks the push (spec :87-92). Not touched.
- ## POSIX paths: the fixture's mandates.yml carries no path fields (spec :156-158). Not touched.
- ## Build artifacts: the virtual environment and fixtures live under $RUNNER_TEMP, outside the repository (spec :132, :165). Not touched.
- ## One base exception: no exception class is added. Not touched.
- ## Declared text decoding: its scope is the package and hooks (:263-266); the new script is under scripts/, outside it. Not governing.
- ## Frozen ledger format: no ledger field changes. Not touched.
- ## Scoped refactor: edits are confined to acf-setup step 8, its upgrading line, one guide line, the doctrine and the version (spec :172-238). Within scope.
- ## Post-merge: housekeeping verifies runs of declared workflows (post-merge-housekeeping SKILL.md:144-157), and the new `action` job sits inside the already-declared .github/workflows/ci.yml, so no new declaration is owed. The parenthetical '(`test` job on main)' at ARCHITECTURE.md:330 becomes incomplete but stays accurate as a workflow declaration.
- ## Host detectors and call sites, built-in contracts: the fixture row (empty_catch, mandate id fail-loud.empty-catch, call_sites [ci]) conforms to ARCHITECTURE.md:169-174.
- High-frequency misses checked first: completeness claims (C21), default re-entering for a declared value (C19), host name in skill prose (C17), stdlib exception mixin (none added), subprocess text without encoding (the new script is outside the package/hooks scope), check re-implemented instead of consumed (C20, acf.repo constants).

### Unstated mandates

- ## One owner for host paths — the new scripts/make_action_fixture_host.py writes config/architecture/mandates.yml and ARCHITECTURE.md, and the section (ARCHITECTURE.md:121-122) requires repository-level scripts to import the acf.repo constants; the spec's governing-mandates line (spec :10-13) omits it and §4.2 is silent.
- ## Single point of definition — the action becomes a third copy of the plugin install recipe (setup-python, pip install -e, npm ci in detectors/typescript), alongside ci.yml's `test` job (ci.yml:17-34) and acf-setup step 4 (SKILL.md:71-85), plus a second base-ref computation beside ci.yml:40; §5 addresses only the gate step's overlap, not the install recipe.

## sweeper

### Claim verdicts

#### C22 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:91-121; plugins/arch-compliance/python/acf/registry.py:18; .github/workflows/ci.yml:39-40; plugins/arch-compliance/skills/acf-setup/SKILL.md:210-249`
- reasoning: Row selection (registry.active per call site, cli_check_diff.py:93-100), the trust decision (:102), scanning and the BLOCK exit (:119-121) all stay in acf-check-diff. The action as specified (§4.1 steps 1-7) passes only flags that already exist (--repo, --base, --call-site, --trusted-checkout at cli_check_diff.py:44-82). ci.yml:39-40 is untouched; the spec only adds a separate `action` job. Step 8 (SKILL.md:210-249) is rewritten in place. One caveat on the quantifier 'every decision about what fails': the action adds failure decisions of its own that come before the gate (Windows runner, an invalid trusted-checkout value, a failed host-setup command, a shallow clone). The shallow-clone check (step 6) partly duplicates a refusal acf-check-diff already makes: git diff base...HEAD fails with no merge base, raises GitError (diff.py:33-39), and comes out as an `acf:` refusal with exit 1 (cli_check_diff.py:106-108). It gives a better message and is not compliance logic, so this is not a second gate. It is recorded in relationships and does not refute the claim.

#### C23 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/registry.py:17-18; plugins/arch-compliance/python/acf/diff.py:42-45; .github/workflows/ci.yml:40`
- reasoning: `precommit` is already one of the two diff call sites (DIFF_CALL_SITES = {ci, precommit}, registry.py:18; doctrine ARCHITECTURE.md:154-158), so the pre-push command adds no new spelling. Its `--base origin/<default>` goes through the same _diff_args three-dot branch (diff.py:43-45) that the plugin's own CI uses (ci.yml:40). No new diff mode is added. I searched for other diff-scope builders (`_diff_args`, `--cached`, `...HEAD`) and found only diff.py:42-48.

#### C24 — SURVIVED
- evidence: `.github/workflows/ci.yml:3-7; .github/workflows/ci.yml:29-40; plugins/arch-compliance/skills/acf-setup/SKILL.md:240-247`
- reasoning: Globbed .github/**, scripts/**, **/action.yml, **/action.yaml and **/*.sh. The only results were .github/dependabot.yml, .github/workflows/ci.yml and scripts/check_installed_skills.py, which checks skill bytes and does not install anything. ci.yml has push and pull_request triggers only, with no workflow_call (:3-7), so it is not reusable by a host. It installs and runs the gate on this repository only (:29-40). Grepping for `workflow_call`, `uses:`, `pip install` and `npm ci` outside docs/design, docs/plans and docs/reviews found nothing that installs acf for a host on a runner. The SKILL.md CI sketch (:240-247) runs the gate but leaves out the install, as the spec says. Searched by behaviour (install plus invoke), not by name.

#### C25 — REFUTED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:285; plugins/arch-compliance/skills/acf-setup/SKILL.md:258`
- reasoning: I redid the sweep with grep -i for 'pre-commit|precommit|pre-push' and for install-to-CI wording across the tree, excluding docs/design, docs/plans and docs/reviews. The enumerated sites check out: frontmatter :3, checklist :25, step 8 :210-249, upgrading bullets :251-256, SUPERPOWERS_COMPLEMENT.md:40. The sweep's 'the places ... are' list leaves out two stale descriptions in the same skill. (1) SKILL.md:285, the Step 10 done summary, tells the agent to report 'That pre-commit/CI snippets were printed'. After §4.3 the snippets are pre-push and CI, and no clause of §4.3 touches Step 10. (2) SKILL.md:258 sits in the upgrading section just past the cited :251-256 range. It tells the host to 'Install the acf package into the environment used by hooks/CI'. Under the action, CI installs acf itself (§4.1 step 3), so that instruction now contradicts the new wiring. I also checked README.md:57-58, :62, :136 and :141-142 and SUPERPOWERS_COMPLEMENT.md:70 and :82-83. They describe this repository's developer commands or historical upgrade notes, so they are not stale wiring descriptions.

### Unanchored findings

- **advisory**: §4.3 rewrites step 8 but leaves two stale lines in the same skill: the Step 10 summary still reports 'pre-commit/CI snippets' (SKILL.md:285), and SKILL.md:258 still tells hosts to install acf into their CI environment, which the action now does for them.
  - evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:285`
- **advisory**: The base-ref default gets a second owner. The action derives `origin/<github.base_ref>` or the default branch when `base` is empty, while the plugin's own CI step keeps its inline `origin/${{ github.base_ref || 'main' }}`. The two can drift, and the spec's shape-fit row calls this 'none: different subjects' although the action accepts `repo: .`.
  - evidence: `.github/workflows/ci.yml:40`
- **advisory**: Dependabot's github-actions entry scans only directory '/', so the actions pinned inside the new composite action at .github/actions/check-diff/action.yml (setup-python, setup-node) would not get version updates unless that directory is added. The spec does not mention it.
  - evidence: `.github/dependabot.yml:19-22`
- **advisory**: Every earlier host-facing release has an 'Upgrading a host ...' note in README.md (for example v0.3.3 at :112-115). The spec changes host wiring in 0.3.4 (pre-commit becomes pre-push, a new pinned action, a release tag) but plans no README upgrade note for it.
  - evidence: `README.md:112`

### Looked for but did not find

- An existing reusable workflow, composite action or install script that installs acf for a host CI: globbed .github/**, scripts/**, **/action.yml, **/action.yaml, **/*.sh; grepped 'workflow_call', 'uses:', 'pip install', 'npm ci'
- Another builder of a diff scope (a second spelling of base/three-dot): grepped '_diff_args', '...HEAD', '--cached'; found only plugins/arch-compliance/python/acf/diff.py:42-48
- Another spelling of the local git-hook call site (for example 'pre-push' or 'prepush' in a registry vocabulary): grepped 'pre-push|precommit|pre-commit'; the only vocabulary is registry.py:17-18
- A shipped hook script or .pre-commit-hooks.yaml that the pre-push snippet would duplicate: globbed **/*.sh and grepped 'pre-commit-hooks'; none
- Existing release-tag automation that the 'tag by hand' rule would conflict with: grepped 'tag' in .github and scripts; none

### Relationships

- ADJACENT: `.github/actions/check-diff/action.yml steps 2-4 (setup-python, pip install -e, setup-node, npm ci in the TS pack)` — responsibility `install acf and the TypeScript pack on a GitHub runner` — existing `.github/workflows/ci.yml:17-34`
  - resolution: None required. The plugin's own job installs `.[dev]` for pytest and the TS self-test, which the action does not need.
  - non-merge: ci.yml's test job needs the dev extras and the pack for pytest and npm test in the same job; the action installs into an isolated venv for a host. The plugin CI could only reuse the action by installing twice.
- PARTIAL_OVERLAP: `action input `base` (empty means origin/<github.base_ref> or the default branch)` — responsibility `derive the diff base ref for a pull-request run` — existing `.github/workflows/ci.yml:40`
  - resolution: R = choose the base ref from the GitHub event. Either have the plugin's own gate step call the action (`uses: ./.github/actions/check-diff`, `repo: .`) so the action is the one owner, or state in the action that ci.yml:40 deliberately keeps its own derivation and why.
- PARTIAL_OVERLAP: `action step 6 (refuse a shallow clone, naming fetch-depth: 0)` — responsibility `refuse when no merge base is available` — existing `plugins/arch-compliance/python/acf/diff.py:33-39`
  - resolution: R = fail when the three-dot diff has no merge base. acf-check-diff already refuses through GitError (cli_check_diff.py:106-108). The action's check only improves the message, so keep it as a precondition hint and treat GitError as the authoritative refusal; no other logic should depend on the action's check.
- IDENTICAL: `/acf-setup step 8 guarded pre-push command` — responsibility `invoke acf-check-diff at the precommit call site` — existing `plugins/arch-compliance/skills/acf-setup/SKILL.md:214-227`
  - resolution: Replace in place, as §4.3 states: the pre-commit block is deleted and the pre-push block takes its place.

### Two-owner counts

- derive the PR diff base ref (origin/<base_ref> or default): 2
- install acf and the TS pack on a GitHub runner: 2
- refuse a diff with no merge base: 2

### Document conflicts

- `plugins/arch-compliance/skills/acf-setup/SKILL.md:285` (contradicts): That pre-commit/CI snippets were printed (not necessarily applied)
- `plugins/arch-compliance/skills/acf-setup/SKILL.md:258` (contradicts): Install the `acf` package into the environment used by hooks/CI

## hardening

### Claim verdicts

#### C26 — SURVIVED
- evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:239-245; plugins/arch-compliance/skills/acf-setup/SKILL.md:217-225; docs/design/CHECK_DIFF_HOST_WIRING.md:147-149`
- reasoning: Today's wiring is a template that hosts paste: SKILL.md:239-245 is a CI sketch with no version pin and no install step, and SKILL.md:217-225 is a pasted pre-commit block. Each host holds its own copy, so the drift argument against templates rests on the current tree. A composite action is one versioned artifact that the host's job calls with `uses:`, so the host keeps its triggers, `needs:` and any later steps. That is a real difference from a reusable workflow, which takes the job over. The trade-off is written down in decision 1. One weakness: §4.1:147-149 itself tells hosts to run the action in a job of their own, because setup-python and setup-node replace the host's interpreters. That narrows the 'host keeps its own job, extra steps' advantage to steps after the action plus the choice of runner. The spec also leaves out a stronger reason for the composite form: `github.action_path` hands the action its own repository files at the pinned ref, while a reusable workflow would need a second checkout of the plugin repository at a ref it cannot easily learn. The justification holds on balance.

#### C27 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/detectors/host.py:102-109; C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/detectors/eslint_rules.py:31-33; C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/detectors/eslint_rules.py:43-44`
- reasoning: Host detector modules load in-process through importlib.util.spec_from_file_location and exec_module (host.py:102-109). Their third-party imports therefore resolve against the sys.path of the interpreter running acf-check-diff, which is the venv's. A host's `pip install` before the action goes to the host's Python, and the venv cannot see it unless it was built with --system-site-packages, which step 3 rules out on purpose. That makes the Python half of the justification correct. The Node half is overstated. The first adopter's detector shells out to `node <WEB>/node_modules/eslint/bin/eslint.js` (eslint_rules.py:33, :43-44), and node_modules is just files on disk. An `npm ci --prefix cayenne-web` step placed before the action would still be there after setup-node swaps the active node, so the reason 'the action's setup would replace their Node' fails for pure-JS Node dependencies; it would bite only native modules or an ABI mismatch. Even so, one input that runs after setup with the venv's bin first on PATH covers both the Python and Node cases from one place. The mechanism holds, and the stated reason is partly broader than needed.

#### C28 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:106-108; plugins/arch-compliance/python/acf/cli_check_diff.py:119-121`
- reasoning: Every typed refusal (GitError, AcfInputError, UnknownDetectorError, DetectorPackError) prints `acf: <msg>` to stderr and returns 1 (cli_check_diff.py:106-108). A BLOCK finding also returns 1 (:119-120). The exit code cannot tell the two apart, so a hook that wanted to pass refusals through would have to parse stderr, as the claim says. The fallback fires only on `command -v` failure, which is an external-environment boundary: a cloud session or a fresh clone without the plugin. It is announced on stderr rather than silent, and the CI action stays the backstop. Pre-push semantics, once per push rather than per commit, are standard git behaviour. The justification is written in §2 decision 6.

#### C29 — SURVIVED
- evidence: `plugins/arch-compliance/python/acf/diff.py:33-39; plugins/arch-compliance/python/acf/diff.py:42-45; plugins/arch-compliance/python/acf/cli_check_diff.py:106-107`
- reasoning: With a missing merge base or an unfetched base ref, `git diff <base>...HEAD` exits non-zero. _git wraps that as GitError carrying git's own stderr (diff.py:33-39, three-dot built at :42-45), and the CLI prints it as `acf: git diff ... failed: <git stderr>` (cli_check_diff.py:106-107). Git's text says 'no merge base' or 'unknown revision', which names neither fetch-depth nor actions/checkout. The pre-check refuses rather than repairs: it does not run `git fetch --unshallow`. It sits at the rung-3 fail-loud position with a better message, and the producer, a host checkout at the default depth, is also hardened by the §4.3 snippet setting fetch-depth: 0. Non-load-bearing, and justified.

#### C30 — SURVIVED
- evidence: `config/architecture/ARCHITECTURE.md:276-281; .github/workflows/ci.yml:3-7`
- reasoning: `git tag` at 9f4eec4 prints nothing, which confirms the repository has no tags today. ARCHITECTURE.md:276-281 confirms that post-merge-housekeeping is one of the four skill trees byte-checked against the installed copy, so adding a tagging step there is a byte-checked skill edit that forces a reinstall cycle, as the claim says. The current CI (ci.yml:3-7) has no tagging job, so a tagging workflow would be a new CI surface needing contents: write to push tags. The design holds no mechanism, only a doctrine sentence. A forgotten tag fails loudly but late, at the host: `uses: ...@v<version>` cannot resolve. Non-load-bearing; the justification is written.

#### C31 — SURVIVED
- evidence: `pyproject.toml:18-21; pyproject.toml:31-36; plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:20; plugins/arch-compliance/python/acf/detectors/host.py:102-109; .github/workflows/ci.yml:29-34`
- reasoning: [project.scripts] declares acf-check-diff = acf.cli_check_diff:main (pyproject.toml:20), so `pip install -e` puts the console script in <venv>/bin. Packages are found under plugins/arch-compliance/python (:31-32). The comment at :34-36 records that an editable install makes Path(__file__) resolve into the source tree. The repository's own CI already depends on exactly that, with `pip install -e` and then `npm ci` in the pack (ci.yml:29-34). typescript_bridge.py:20 computes parents[3]/detectors/typescript from the resolved source file, which lands at plugins/arch-compliance/detectors/typescript inside the downloaded repository. Host modules run in the gate's process through importlib (host.py:102-109; ARCHITECTURE.md trust boundary, 'a host module runs in the gate's process'). The gate is the venv's interpreter, through the console-script shebang, so a `pip install` resolved through the venv's bin on PATH lands in the site-packages the host imports read.

#### C32 — REFUTED
- evidence: `plugins/arch-compliance/python/acf/registry.py:50-63; plugins/arch-compliance/python/acf/loader.py:70-73; C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/mandates.yml:7-16`
- reasoning: The row as §4.2:156-158 lists it (id, BLOCK, ast, empty_catch, typescript, call_sites [ci], enforced, arch_anchor) leaves out two Mandate fields that have no default: `title: str` (registry.py:52) and `exemption_tokens: list[str]` (registry.py:58). Validating that row raises ValidationError, which load_model_file turns into AcfInputError (loader.py:70-73), and the CLI exits 1 with `acf: invalid mandates file`. The first adopter's real row carries both fields (cy mandates.yml:8, :14). The fix is precision only: add a title and `exemption_tokens: []`. Everything else in the claim checks out. empty_catch is a built-in that reports to fail-loud.empty-catch at every Tier-1 site including ci (detectors/__init__.py:44-47; registry.py:201-217), so a [ci]-only row passes the Tier-1 and contract checks (registry.py:99-103). There are no host rows, so check_approval returns NOT_NEEDED (approval.py:128-129) and --trusted-checkout does not matter. acf-check-diff never reads ARCHITECTURE.md (missing_anchors has no caller), .acf/enabled (hook only), or adr.yml, so those files are harmless but not needed. `--base main` becomes `git diff main...HEAD`, a local three-dot that needs no remote (diff.py:42-45). An added empty `catch {}` produces a finding on the catch line (detectors/typescript/src/rules/emptyCatch.ts:11-26), kept by apply_registry as BLOCK (enforcement.py:60-67), and the run exits 1 (cli_check_diff.py:119-120). Because the fixture row as written would not load, the claim that it 'loads without error' is false.

#### C33 — SURVIVED
- evidence: `.github/workflows/ci.yml:40; C:/Users/iball/Arduino/Projects/Cayenne/.github/workflows/ci.yml:296`
- reasoning: In-tree corroboration covers part of the claim. This repository's CI already depends on github.base_ref being empty outside pull_request, through its `github.base_ref || 'main'` fallback (ci.yml:40). The first adopter's CI uses step and job `continue-on-error: true` (cy ci.yml:296). `git rev-parse --is-shallow-repository` is a real flag in git 2.15 and later; on this full clone it prints `false` (git 2.49). Composite actions' `uses:` steps, `steps.<id>.outcome` reading `failure` under continue-on-error, and github.event.repository.default_branch on pull_request payloads are documented GitHub platform behaviour. I checked the ones I could exercise and none of the hooks is speculative. One detail: §4.2 passes fixture paths under $RUNNER_TEMP to the `repo` input, which §4.1 defines as 'relative to the workspace'. An absolute path works with `--repo` and `git -C`, but the input's definition should allow it.

#### C34 — SURVIVED
- evidence: `C:/Users/iball/Arduino/Projects/Cayenne/.githooks/pre-push:5-11; plugins/arch-compliance/skills/acf-setup/SKILL.md:217-225`
- reasoning: In the first adopter, `git config core.hooksPath` prints `.githooks`, and .githooks/pre-push runs under `set -e` (:5), skipping docs-only pushes with `exit 0` (:7-11). A guarded `if command -v ...; then acf-check-diff ...; else echo ...; fi` placed after line 11 aborts the hook when acf-check-diff exits non-zero: set -e exempts only the `if` condition, not commands in the `then` body, so the push is blocked. The `else` branch's echo returns 0 and the push continues. A fresh .git/hooks/pre-push holding only the snippet exits with the `if` compound's status, which is acf-check-diff's. The pre-commit framework syntax (repo: local, language: system, stages) is already in the shipped snippet (SKILL.md:217-225), so changing `stages` to [pre-push] and using `entry: sh -c '...'` is a minimal change; exit status propagates through sh -c. Two caveats for other hosts are filed as findings: a hook without set -e that has the snippet inserted mid-file swallows the failure, and the pre-commit framework needs the pre-push hook type installed.

### Unanchored findings

- **important**: The §4.2 fixture row omits the required Mandate fields `title` and `exemption_tokens`, which have no defaults, so the fixture as specified fails to load; add both, for example `exemption_tokens: []`.
  - evidence: `plugins/arch-compliance/python/acf/registry.py:50-63`
- **advisory**: The action CI job asserts only that the planted run's outcome is `failure`, which any refusal also produces (exit 1 for refusals and findings alike), so it does not prove the BLOCK fail-loud.empty-catch finding fired; asserting that the planted run's output contains `BLOCK fail-loud.empty-catch` would close that gap.
  - evidence: `plugins/arch-compliance/python/acf/cli_check_diff.py:106-108`
- **advisory**: The §4.3 pre-push placement text says a non-zero exit blocks the push, but that holds only where the hook runs under `set -e` or the snippet is the last command. A host hook without set -e that gets the snippet inserted mid-file swallows the failure, so the text should tell hosts to append `|| exit 1` or check for set -e.
  - evidence: `C:/Users/iball/Arduino/Projects/Cayenne/.githooks/pre-push:5`
- **advisory**: For the pre-commit framework placement, §4.3 names only `stages: [pre-push]` and `entry`. It does not say that the pre-push hook type must be installed (`pre-commit install --hook-type pre-push` or `default_install_hook_types`), and it drops `pass_filenames: false` and `language: system` from the current snippet; without the install step the entry never runs.
  - evidence: `plugins/arch-compliance/skills/acf-setup/SKILL.md:217-225`
- **advisory**: §2 decision 1 justifies the composite action by saying the host keeps its own job and extra steps, but §4.1 itself requires the action to run in a job of its own because setup-python and setup-node replace the host's interpreters. That leaves the stated advantage at steps after the action, while the stronger reason (action_path delivers the plugin source at the pinned ref without a second checkout) goes unstated.
  - evidence: `docs/design/CHECK_DIFF_HOST_WIRING.md:147-149`

### Looked for but did not find

- A repair path in the action: none. Every added check (Windows, trusted-checkout value, host-setup exit, shallow clone) stops the action; none repairs (no `git fetch --unshallow`, no value coercion)
- A requirement that acf-check-diff read ARCHITECTURE.md, .acf/enabled or adr.yml: none. missing_anchors (registry.py:229) has no caller in cli_check_diff.py; .acf/enabled gates only the hook (repo.py:38)
- An approval requirement for the no-host-row fixture: check_approval returns NOT_NEEDED when there are no host rows (approval.py:128-129)
- A wheel-only install path that would break the TS pack under the action: the action uses `pip install -e`, matching ci.yml:29-34
- A first-adopter registry without precommit rows, which would make the pre-push step refuse every push: cy mandates.yml rows declare [ci, precommit, ...] (:13, :24, :35, :145, :164)

### Mechanism traces

- **pre-push step skips when acf-check-diff is absent**
  - invalid state: `command -v acf-check-diff` exits non-zero in the environment running the push hook
  - producer: `C:/Users/iball/Arduino/Projects/Cayenne/.githooks/pre-push:1`
  - rung 5 (highest applicable 5); repairs=False
  - hardening rejected because: A cloud session or a fresh clone may not have `acf-check-diff`. The pre-push step then prints one line saying the check was skipped and that CI runs it, and lets the push continue.
  - spec citation: `docs/design/CHECK_DIFF_HOST_WIRING.md:85-92`
- **shallow-clone check in the action (step 6)**
  - invalid state: `git -C <repo> rev-parse --is-shallow-repository` prints `true`, so merge-base(<base>, HEAD) cannot be computed
  - producer: `plugins/arch-compliance/skills/acf-setup/SKILL.md:239-241`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: the three-dot diff needs the merge base; the §4.3 snippet sets fetch-depth: 0 at the producer, and this check names the fix when a host omits it
  - spec citation: `docs/design/CHECK_DIFF_HOST_WIRING.md:141-143`
- **trusted-checkout input validation (any value other than true or false stops the action)**
  - invalid state: inputs.trusted-checkout not in {'true','false'}
  - producer: `docs/design/CHECK_DIFF_HOST_WIRING.md:198`
  - rung 3 (highest applicable 3); repairs=False
  - spec citation: `docs/design/CHECK_DIFF_HOST_WIRING.md:123`
- **Windows runner stop (step 1)**
  - invalid state: runner.os == 'Windows'
  - producer: `docs/design/CHECK_DIFF_HOST_WIRING.md:185`
  - rung 3 (highest applicable 3); repairs=False
  - hardening rejected because: Windows runners are a non-goal (§3)
  - spec citation: `docs/design/CHECK_DIFF_HOST_WIRING.md:102-103`
- **composite action replacing copied CI templates**
  - invalid state: a host's pasted CI wiring differs from the wiring of the plugin release it has installed (missing install step, stale flags)
  - producer: `plugins/arch-compliance/skills/acf-setup/SKILL.md:239-245`
  - rung 2 (highest applicable 2); repairs=False
  - hardening rejected because: A reusable workflow would own the whole job; templates copied into each host drift and need an edit in every host on every release.
  - spec citation: `docs/design/CHECK_DIFF_HOST_WIRING.md:61-64`
- **host-setup input**
  - invalid state: a host detector's third-party import or external tool (for example <host>/node_modules/eslint/bin/eslint.js) is absent from the environment the gate runs in
  - producer: `C:/Users/iball/Arduino/Projects/Cayenne/config/architecture/detectors/eslint_rules.py:33`
  - rung 2 (highest applicable 2); repairs=False
  - hardening rejected because: Steps 2 and 4 change the job's python and node for any later step, and replace any a host set up before the action, so ... a host's detector dependencies go in host-setup, not in steps before the action.
  - spec citation: `docs/design/CHECK_DIFF_HOST_WIRING.md:137-140`
- **manual release tagging**
  - invalid state: plugin.json version V is merged on main and no tag v<V> exists, so a host's `uses: ...@v<V>` cannot resolve
  - producer: `config/architecture/ARCHITECTURE.md:276-278`
  - rung 5 (highest applicable 2); repairs=False
  - hardening rejected because: No skill or workflow does it (decision 7). C30's reasons: a post-merge-housekeeping step is a byte-checked skill edit, and a tagging workflow is a new CI surface with a token that can push tags.
  - spec citation: `docs/design/CHECK_DIFF_HOST_WIRING.md:93-96`

## Claims

- **C1** [premise] [load-bearing]: The TypeScript detector bridge locates its Node scanner relative to its own source file (_PACK_ROOT = Path(__file__).resolve().parents[3] / 'detectors' / 'typescript'), so a non-editable (wheel/site-packages) install of the acf package cannot scan .ts/.tsx files; scanning needs an editable install from a source checkout of the plugin repository plus `npm ci` in plugins/arch-compliance/detectors/typescript.
  - spec citation: `plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:20`
- **C2** [premise] [load-bearing]: `acf-check-diff --base <ref>` diffs merge-base(<ref>, HEAD) to HEAD (git three-dot), both for the changed-file list and for added lines; therefore on a push to the default branch, where origin/<default> equals HEAD, the diff is empty and a CI run there checks nothing. This is the reason the design triggers the action on pull_request only.
  - spec citation: `plugins/arch-compliance/python/acf/diff.py:43-46`
- **C3** [premise] [load-bearing]: `acf-check-diff` exits 1 both when a BLOCK finding is reported and when it refuses to run (a host-row approval missing, a TypeScript pack without `npm ci` raising DetectorPackError, a base ref git cannot resolve raising GitError), so the exit code cannot distinguish a finding from a refusal; and each such refusal prints a line beginning `acf:` that names its fix (acf-allow, npm ci, the unresolvable ref). The design's pre-push step blocks on every non-zero exit on the strength of this.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:36-121`
- **C4** [premise]: Under --base the gate takes the changed files and added line numbers from the committed diff but reads each changed file's text from the working tree (RepoTree.file then read_text, cli_check_diff.py:145, :153, :189), so uncommitted edits to a changed file can move a reported line in a local pre-push run; a clean CI checkout has no such gap. Stated as the pre-push step's one known gap.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:145`
- **C5** [premise]: The plugin repository has no git tags today (`git tag` prints nothing), so hosts cannot yet pin a release by tag. No file citation is offered; the recipe is `git tag`.
  - spec citation: `None`
- **C6** [premise]: /acf-setup step 8 today prints a pre-commit framework entry running `acf-check-diff --mode staged --call-site precommit` and a GitHub Actions CI sketch running `acf-check-diff --base ... --call-site ci --trusted-checkout`; the CI sketch does not say how acf-check-diff (and the TypeScript pack) gets installed on the runner.
  - spec citation: `plugins/arch-compliance/skills/acf-setup/SKILL.md:210-249`
- **C7** [premise] [load-bearing]: When a workflow references a composite action as `owner/repo/path@ref` (or as a local `./path`), the runner makes the whole repository at that ref available, so `$GITHUB_ACTION_PATH/../../..` (action at .github/actions/check-diff/) is the plugin repository root, containing pyproject.toml and plugins/arch-compliance/detectors/typescript. The spec cites GitHub's contexts reference for github.action_path (external documentation, no repository file) and defers end-to-end proof of the remote case to the first adopter's run (§8). If false, the action would need its own checkout of the plugin repository.
  - spec citation: `None`
- **C8** [premise] [load-bearing]: The first adopter's (Cayenne, at 7313bca5) host detectors run the ESLint binary at cayenne-web/node_modules/eslint/bin/eslint.js, which nothing in the action installs; they import only the standard library and acf (eslint_rules.py:20-29); Cayenne's CI uses Node '22' (cy:.github/workflows/ci.yml:94). This is why the action needs a `host-setup` input and why the first adopter passes `host-setup: npm ci --prefix cayenne-web`. Obligation: confirm which of Cayenne's enforced rows declaring `ci` are host rows and whether any of them needs anything beyond cayenne-web's node_modules.
  - spec citation: `cy:config/architecture/detectors/eslint_rules.py:33`
- **C9** [premise]: The first adopter's CI does not run acf-check-diff today (no 'acf' match under .github or .githooks at 7313bca5), and its main branch has no required status checks (ci.yml comment; branch protection API returns 404 'Branch not protected').
  - spec citation: `cy:.github/workflows/ci.yml:6-7`
- **C10** [premise] [load-bearing]: Deferral (risk table): running host detectors under --trusted-checkout on a pull request from a fork is the same exposure as today's /acf-setup CI sketch, because `pull_request` runs triggered from forks get a read-only token and no secrets. No citation is offered for the GitHub behaviour.
  - spec citation: `None`
- **C11** [premise] [load-bearing]: Deferral (non-goal): acf-check-diff runs only `ast` and `guard` rows, never `llm` rows, so the action needs no LLM provider key and the LLM rows stay out of the automatic gates without any change.
  - spec citation: `None`
- **C12** [premise]: Deferral (non-goal): Windows runners are out of scope; the action stops with a message on runner.os == 'Windows'. Not load-bearing: supporting Windows would be the same design plus a venv-layout branch (Scripts/ vs bin/).
  - spec citation: `None`
- **C13** [premise] [load-bearing]: Running actions/setup-python and actions/setup-node inside a composite action changes `python` and `node` on PATH for every later step of the job and supersedes any version a host set up in earlier steps; so a host's detector dependencies must be installed through the action's `host-setup` input (run after the action's own setup) rather than in steps before the action, and the snippet runs the action in a job of its own.
  - spec citation: `None`
- **C14** [mandate] [load-bearing]: Trust boundary: `--trusted-checkout` appears only in CI (the action, default on, input `trusted-checkout`), never in the local pre-push command, and naming the action in a workflow is the CI opt-in the doctrine's trust boundary and acf-setup SKILL.md:249 describe.
  - spec citation: `config/architecture/ARCHITECTURE.md:178-181`
- **C15** [mandate] [load-bearing]: Release discipline: because acf-setup's prose changes, the design bumps the version to 0.3.4 in plugins/arch-compliance/.claude-plugin/plugin.json and pyproject.toml, and adds a tagging rule to the section; acf-setup is not among the four skill trees scripts/check_installed_skills.py byte-checks, so no other release step is owed.
  - spec citation: `config/architecture/ARCHITECTURE.md:274-284`
- **C16** [mandate] [load-bearing]: Call-site rule: reusing the `precommit` call site for a pre-push hook, with the doctrine sentence '`precommit` is the local git-hook site, whichever hook (pre-commit or pre-push) runs it', is consistent with the closed call-site vocabulary and DIFF_CALL_SITES and introduces no new site value.
  - spec citation: `config/architecture/ARCHITECTURE.md:140-187`
- **C17** [mandate] [load-bearing]: Prose names no host: the acf-setup changes and the action name no host repository, path or section (the host-setup example is the generic `npm ci --prefix web`; the first adopter appears only in the spec's §8, not in skill prose or the action).
  - spec citation: `config/architecture/ARCHITECTURE.md:223-233`
- **C18** [mandate] [load-bearing]: Live consumers: the new scripts/make_action_fixture_host.py has a live consumer (the new `action` CI job), and the new action has live consumers (that CI job and hosts' workflows), so neither is dead code under the rule that a test is not a consumer.
  - spec citation: `config/architecture/ARCHITECTURE.md:243-247`
- **C19** [mandate] [load-bearing]: The action's input defaults (trusted-checkout 'true', base computed from github.base_ref or the default branch, python-version '3.12', node-version '22', repo '.') do not breach `## Declared, never defaulted`; the spec does not list that section among its governing mandates and offers no citation for why it does not apply.
  - spec citation: `None`
- **C20** [mandate]: One owner for host paths: the new repository-level script scripts/make_action_fixture_host.py, which writes config/architecture/mandates.yml and ARCHITECTURE.md into a fixture repository, follows the rule that repository-level scripts import the acf.repo constants; the spec says nothing about it.
  - spec citation: `None`
- **C21** [mandate]: No completeness claims: the spec's factual claims about the tree are backed by recipes a reader can re-run (for example `git tag`, the cited file:line receipts in §6), and it makes no unbacked 'every/all/only/no second' claim.
  - spec citation: `config/architecture/ARCHITECTURE.md:249-259`
- **C22** [shape_fit] [load-bearing]: The composite action creates no second gate: every decision about what runs and what fails stays in acf-check-diff, which the action only installs and calls with flags it already has; the plugin's own CI gate step (.github/workflows/ci.yml:39-40) is unchanged; /acf-setup step 8 is rewritten in place rather than gaining a parallel snippet.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:36-121`
- **C23** [shape_fit] [load-bearing]: The pre-push step reuses the existing `precommit` call site and the existing `--base` scope CI uses, creating no second spelling of a call site and no second diff scope.
  - spec citation: `config/architecture/ARCHITECTURE.md:140-187`
- **C24** [shape_fit] [load-bearing]: No existing mechanism in the repository already installs and runs acf-check-diff for a host in CI (no reusable workflow, action, or install script for hosts), so the action duplicates nothing; the only existing CI invocation is the plugin's own self-check from its own editable install.
  - spec citation: `None`
- **C25** [sweep]: The places that describe or print the pre-commit wiring and must change are: acf-setup SKILL.md frontmatter description, checklist item 8, the step 8 heading and body, and the upgrading section (:251-256); and docs/guides/SUPERPOWERS_COMPLEMENT.md:40. Step 9's smoke command and the friend-bar tip deliberately keep --mode worktree / --mode staged. Obligation: sweep the tracked tree (outside docs/design, docs/plans, docs/reviews) for other pre-commit wiring descriptions the design leaves stale.
  - spec citation: `docs/guides/SUPERPOWERS_COMPLEMENT.md:40`
- **C26** [mechanism_justification] [load-bearing]: A composite action is justified over a reusable workflow (which would own the host's whole job) and over templates copied into each host (which drift and need an edit per host per release).
  - spec citation: `None`
- **C27** [mechanism_justification] [load-bearing]: A single `host-setup` shell-command input, run after the action's own Python/Node setup with the venv's bin first on PATH, is justified over letting hosts add steps before the action (the action's setup would replace their Node/Python) or over letting the venv inherit the host's Python packages (step 3's isolation).
  - spec citation: `None`
- **C28** [mechanism_justification] [load-bearing]: Replacing the pre-commit snippet with a pre-push step that skips only when acf-check-diff is absent and blocks on every non-zero exit (refusals included) is justified: pre-push runs once per push rather than per commit; CI holds where the tool is absent; a refusal names its fix, and distinguishing refusals from findings would need stderr parsing.
  - spec citation: `None`
- **C29** [mechanism_justification]: The action's explicit shallow-clone check (stop with a message naming fetch-depth: 0 when `git rev-parse --is-shallow-repository` prints true) earns its place although acf-check-diff already fails with a GitError when the merge base is missing, because git's own message does not name the fix.
  - spec citation: `None`
- **C30** [mechanism_justification]: Tagging releases by hand (whoever merges a version bump tags and pushes v<version>) is justified over a post-merge-housekeeping step (a byte-checked skill edit) or a tagging workflow (a new CI surface and a token that can push tags).
  - spec citation: `None`
- **C31** [implementability] [load-bearing]: `pip install -e <plugin repo root>` into a fresh venv installs the console script at <venv>/bin/acf-check-diff (pyproject [project.scripts]) with the acf package importable from the source tree, so the TypeScript bridge's _PACK_ROOT resolves into the downloaded repository; and host detector modules the gate imports run in the gate's own process (ARCHITECTURE.md trust boundary), so a `pip install` done by host-setup with the venv's bin first on PATH lands where the gate imports host detectors from.
  - spec citation: `pyproject.toml`
- **C32** [implementability] [load-bearing]: The §4.2 fixture works as specified: a mandates.yml holding only the `fail-loud.empty-catch` row (BLOCK, ast, empty_catch, typescript, call_sites [ci], enforced, arch_anchor '## Fail loud') loads without error alongside an ARCHITECTURE.md carrying that line; with no host rows no approval is needed, so the run succeeds without --trusted-checkout mattering; `--base main` resolves against a fixture repository with no `origin` remote; a `try { ... } catch {}` added on branch `feature` yields BLOCK fail-loud.empty-catch and exit 1; the clean change yields exit 0. Obligation: check the registry/load rules (Tier-1 site requirement, built-in contract sites, anchor matching, any required files such as .acf/enabled or adr.yml) against this fixture.
  - spec citation: `plugins/arch-compliance/python/acf/cli_check_diff.py:101-102`
- **C33** [implementability] [load-bearing]: The hooks the action assumes exist and behave as stated: `git rev-parse --is-shallow-repository` prints `true` on a shallow clone; a composite action step can `uses:` actions/setup-python and actions/setup-node; a composite step's non-zero exit fails the action and a calling step's `continue-on-error: true` with `steps.<id>.outcome` reads `failure`; github.base_ref is empty on non-pull_request events and github.event.repository.default_branch is available.
  - spec citation: `None`
- **C34** [implementability] [load-bearing]: The pre-push placements the acf-setup text names work: a `pre-push` file in the `git config core.hooksPath` directory or `.git/hooks/pre-push`; `.husky/pre-push`; and a pre-commit framework hook with `stages: [pre-push]`, `language: system` and `entry: sh -c '<guarded command>'`. In a host hook running under `set -e` (as the first adopter's .githooks/pre-push does), the guarded command's non-zero exit blocks the push and the absent-tool branch lets it continue.
  - spec citation: `None`
