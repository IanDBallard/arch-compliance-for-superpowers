# One Shipped Way for a Host to Run `acf-check-diff` in CI and Before a Push

**Status:** v4 — approved by the user 2026-11-21 (declared opt-out for the pre-push step chosen by the user); precision revision of v3, cleared by verification pass.
**Adversarial review:** v4 — 2026-11-21, verification pass over the v3 full run
(BLOCKED; all blocking findings precision-class, absorbed and re-measured),
user-approved (repo @ bc86c69)
**Spec kinds:** `feature`
**Repo:** `IanDBallard/arch-compliance-for-superpowers`, `main` at `b9aaf77` (release 0.3.3).
**Workstream:** HistoricMansions Workstream E, host roll-out step R6 ("Wire `acf-check-diff`
into CI and pre-commit"; acceptance "A planted `catch {}` fails the CI job"). The plugin
ships the wiring once. Each host then adopts it with a few lines, and the first adopter's
pull request carries R6's acceptance (§8).
**Governing mandates:** `config/architecture/ARCHITECTURE.md` sections `## One owner for
host paths` (`:115-138`), `## Host detectors and call sites` (`:140-187`, the call-site rule
and the trust boundary), `## Declared, never defaulted` (`:189-221`), `## Prose names no
host` (`:223-233`), `## Live consumers`
(`:243-247`), `## No completeness claims` (`:249-259`), `## Release discipline`
(`:274-284`), `## Single point of definition` (`:286-303`), `## Declared text decoding`
(`:261-272`, cited for the Windows limits) and `## Post-merge` (`:324-335`).
**No state-machine surface.** The design adds or modifies no state machine and no
transition.

---

## 0. Citation convention

Unprefixed paths are this repository at `b9aaf77`. Paths prefixed `cy:` are the sibling
repository `IanDBallard/Cayenne` at `7313bca5` (`main`), the first adopter. No step of the
plugin's change reads or writes them. The rules relied on are quoted beside each citation.

---

## 1. Goal

Today a host that wants the diff gate outside Claude's edits gets two pasted snippets from
`/acf-setup` step 8 (`plugins/arch-compliance/skills/acf-setup/SKILL.md:210-249`): a
pre-commit entry running `acf-check-diff --mode staged --call-site precommit` (`:223`), and
a CI sketch running `acf-check-diff --base … --call-site ci --trusted-checkout` (`:245`).
The CI sketch has no install step; the nearest text is a generic reminder to install the
`acf` package "into the environment used by hooks/CI" (`:258`), which says nothing about the
TypeScript pack. That pack is the hard part. The TypeScript detector finds its Node scanner
relative to its own source file:

> `_PACK_ROOT = Path(__file__).resolve().parents[3] / "detectors" / "typescript"`
> (`plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:20`)

and `pyproject.toml`'s package data ships no `detectors/typescript` (`:39-40`). So a wheel
install cannot scan `.ts` or `.tsx` files. The runner needs a source checkout of this
repository, an editable install of it, and `npm ci` in
`plugins/arch-compliance/detectors/typescript`. Every host would have to work that out and
keep its copy in step with each release.

This design ships that wiring as a composite GitHub Action in this repository, so a host's
CI wiring is a checkout and one `uses:` line pinned to a release tag. It also replaces the
pre-commit snippet with a pre-push step, which runs once per push rather than once per
commit and refuses where `acf-check-diff` is not installed, unless the environment declares
the check optional (§2 decision 6).

The gate then runs at three points in a host, each with its own job:

| Point | Call site | What it catches | Owner |
| --- | --- | --- | --- |
| Claude's edits | `hook` | the edited file, as it is written | the plugin's PostToolUse hook, unchanged (`.acf/enabled`) |
| Before a push | `precommit` | the checked-out branch's commits, before CI sees them | the host's pre-push hook, from the §4.3 snippet |
| Pull requests | `ci` | the pull request's diff against its base, from any author | the §4.1 action, from the host's workflow |

---

## 2. Decisions this design records

1. **A composite action, not a reusable workflow or templates.** Templates copied into
   each host drift and need an edit in every host on every release; the current CI sketch
   is such a template (`acf-setup/SKILL.md:239-247`). A reusable workflow owns the host's
   whole job. A composite action is one versioned artifact the host's job calls; the host
   keeps its triggers, the runner and whatever depends on the job.
2. **The action installs from the files GitHub hands it, and checks them first.** The
   action installs the `acf` package editable from the repository root three levels above
   its own directory (`$GITHUB_ACTION_PATH/../../..`) and runs `npm ci` there, with no
   second checkout. That location holding this repository at the pinned ref is GitHub
   platform behaviour, which this repository does not document (§6 gives the recipe). The design therefore does
   not rely on it silently: the action's first step stops, naming what is missing, unless
   that directory holds `pyproject.toml` and `plugins/arch-compliance/detectors/typescript/package.json`
   (§4.1 step 1). The `action` CI job (§4.2) runs the action by local path; the first
   adopter's run (§8) is the first use from another repository.
3. **Pull requests by default; also pushes to the default branch for hosts with whole-tree
   rows.** With `--base`, the changed-file list and added lines are the three-dot diff
   (`plugins/arch-compliance/python/acf/diff.py:43-46`), so on a push where
   `origin/<default>` is `HEAD` every per-file check sees nothing. Two kinds of row still
   run on an empty diff: an active `fail_loud_ratchet` row, which scans the tree against its
   baseline (`plugins/arch-compliance/python/acf/cli_check_diff.py:212-226`), and host
   guard rows, which are called whatever the diff holds (`:228-230`). The snippet triggers on
   `pull_request`; `/acf-setup` adds `push` to the default branch when the host's registry
   has either kind of row active at `ci`.
4. **`--trusted-checkout` is on by default in the action, with an input to turn it off.**
   The trust boundary already makes the workflow file the opt-in for CI: host code runs
   "for `acf-check-diff`, when the invocation passes `--trusted-checkout`"
   (`config/architecture/ARCHITECTURE.md:178-181`), and the CI sketch says "in CI the
   workflow file is the opt-in" (`acf-setup/SKILL.md:249`). Naming the action in a workflow
   is that opt-in. Pull requests from forks run the pull request's own host detectors under
   it, as today's sketch already does (`:245`); a host that does not want that sets
   `trusted-checkout: false`, and its host rows then need an approval the runner does not
   have.
5. **Pre-push replaces pre-commit in `/acf-setup`.** The `precommit` call site keeps its
   name and means the local git-hook site, whichever hook runs it. Pre-push diffs the
   checked-out branch against `origin/<default>` with `--base`, the scope CI uses.
6. **The local step refuses when the gate is absent, unless the environment declares
   otherwise.** When `acf-check-diff` is not on `PATH`, the pre-push step blocks the push
   and says how to install it. It lets the push continue, printing that the check was
   skipped and that CI runs it, only when the environment sets `ACF_PREPUSH_OPTIONAL=1`.
   That variable is set by whoever owns an environment where CI is meant to be the only
   gate (a cloud session's environment settings, say) and is never committed to the
   repository, so a fresh clone that has not installed the tool is stopped, not silently
   passed. Unset, or any other value, means refuse. Once the command is installed, any
   non-zero exit blocks the push. `acf-check-diff` returns 1 for a BLOCK finding and for a
   refusal alike (`cli_check_diff.py:106-108`, `:119-121`); the refusals it catches print a
   line beginning `acf:`, and a missing approval, a TypeScript pack without `npm ci` and an
   unresolvable base each say what failed. An uncaught exception or a usage error also
   exits non-zero and blocks. A local gate that is installed but cannot run is fixed, not
   passed over; telling a refusal from a finding would mean parsing stderr.
7. **Releases are tagged, by hand.** The repository has no tags today (`git tag` prints
   nothing). Hosts pin the action to `v<version>`, so whoever merges a version bump tags
   its merge commit on `main` `v<version>` and pushes the tag, starting with `v0.3.4`. No
   skill or workflow does it.
8. **Host detector dependencies go through one input.** The gate imports a host detector
   module into its own process (`plugins/arch-compliance/python/acf/detectors/host.py:102-109`),
   so a host detector's third-party Python packages must be installed in the environment
   that runs `acf-check-diff`, which is the action's own virtual environment (§4.1 step 4).
   That environment does not exist until the action creates it. The `host-setup` input,
   the supported place for these dependencies, runs after the action's setup with that
   environment first on `PATH`, so one place takes both a host's Python packages and its
   Node ones (a host detector that shells
   out to the host's ESLint needs the host's `node_modules`; files installed by an earlier
   step would also stay on disk, and `host-setup` is the documented place for them).

---

## 3. Non-goals

- Windows runners. The action stops with a message on Windows (`runner.os == 'Windows'`).
  Supporting them would take more than a virtual-environment layout branch: the diff gate's
  git runner does not declare its text encoding (`ARCHITECTURE.md`, `## Declared text
  decoding`), and this repository's own Windows note runs the gate under `PYTHONUTF8=1`.
- Changing `acf-check-diff` itself, its flags or its exit codes.
- The LLM rows (`detection: llm`, `acf-check-llm`). `acf-check-diff` selects only `ast` and
  `guard` rows (`cli_check_diff.py:94-96`), so they stay out of every automatic gate.
- A `.pre-commit-hooks.yaml` or any hook script shipped by the plugin. Hosts wire hooks
  differently, so `/acf-setup` adapts a snippet to the host's own mechanism.
- Publishing to the GitHub Marketplace.
- Adoption by any host other than the first (§8). Each is its own change.

---

## 4. Design

### 4.1 `.github/actions/check-diff/action.yml` (new)

A composite action. Inputs, each a string:

| Input | Default | Meaning |
| --- | --- | --- |
| `base` | empty | the ref to diff against; empty means `origin/<github.base_ref>`, or `origin/<github.event.repository.default_branch>` when there is no base ref |
| `repo` | `.` | the host repository's root: an absolute path, or a path relative to the workspace |
| `trusted-checkout` | `true` | `true` passes `--trusted-checkout`; `false` does not; any other value stops the action with a message naming the input |
| `python-version` | `3.12` | handed to `actions/setup-python` |
| `node-version` | `22` | handed to `actions/setup-node` |
| `host-setup` | empty | a shell command run from `repo` before the gate, for the host detectors' own dependencies (for example `npm ci --prefix web`); empty runs nothing |

Steps, in order:

1. Stop with a message unless `$GITHUB_ACTION_PATH/../../../pyproject.toml` and
   `$GITHUB_ACTION_PATH/../../../plugins/arch-compliance/detectors/typescript/package.json`
   exist; the message names both paths and says the action expects to run from a full copy
   of the plugin repository (§2 decision 2).
2. Stop with a message on a Windows runner.
3. `actions/setup-python` with `python-version`.
4. Create a virtual environment under `$RUNNER_TEMP` and `pip install -e` the repository
   root into it. The virtual environment keeps the plugin's dependencies out of the host's
   own Python environment.
5. `actions/setup-node` with `node-version`, then `npm ci` in
   `plugins/arch-compliance/detectors/typescript` under the repository root.
6. When `host-setup` is not empty, run it with `bash` from `repo`, the virtual
   environment's `bin` first on `PATH` (so a `pip install` there lands in the environment
   the gate imports host detectors from) and step 5's Node active. A non-zero exit stops the
   action.
7. Stop with a message naming `fetch-depth: 0` when
   `git -C <repo> rev-parse --is-shallow-repository` prints `true`. Where the merge base is
   missing, this replaces `acf-check-diff`'s own `GitError` refusal (`diff.py:33-39`,
   `cli_check_diff.py:106-108`) with a message naming the fix, and that refusal stays the
   authoritative one. The stop is also stricter than the gate: it refuses a shallow clone
   deep enough to hold the merge base, which the gate would complete. That is deliberate;
   the snippet checks out with `fetch-depth: 0`, so a shallow checkout means the host left
   the snippet, and one predicate is simpler than computing the merge base twice.
8. Run the virtual environment's `acf-check-diff --repo <repo> --base <base> --call-site ci`,
   with `--trusted-checkout` when the input is `true`, writing its standard output both to
   the log and, overwriting it, to `$RUNNER_TEMP/acf-check-diff.txt` (through `tee`, with
   `pipefail` so the step's exit status stays the gate's).

The snippet gives the action a job of its own, so nothing else in a host's CI depends on
the Python and Node versions the action selects.

### 4.2 The action's test: `tests/action_fixture_host.py` (new) and a CI job

`tests/action_fixture_host.py <dest> --plant {empty-catch,clean}` is test scaffolding: it
builds a git repository at `<dest>` for the CI job below, and no package code, hook or
skill calls it. A runner may have no git identity configured, so it commits with its own
(`git -c user.name=… -c user.email=… -c commit.gpgsign=false commit`), as the repository's
git-fixture tests do (`plugins/arch-compliance/tests/test_adr_citation_history.py:20`
passes exactly these `-c` options). It creates the repository with its first branch named
`main` (`git -c init.defaultBranch=main init`), since a runner's git may default to
`master` and both runs diff against `main`. It takes the two config paths from `acf.repo` (`MANDATES_REL`, `ARCH_REL`,
`plugins/arch-compliance/python/acf/repo.py:21`, `:24`), as `## One owner for host paths`
asks of the repository-level `tests/` and `scripts/` (`ARCHITECTURE.md:120-122`). pytest
does not collect it: its name matches neither of pytest's default file patterns,
`test_*.py` and `*_test.py`, and no pytest configuration sets `python_files` (§6 gives the
recipe). It writes:

- On `main`: `MANDATES_REL` with one row,

  ```yaml
  - id: fail-loud.empty-catch
    title: Empty catch blocks must not swallow errors
    severity: BLOCK
    detection: ast
    detector: empty_catch
    languages: typescript
    call_sites: [ci]
    exemption_tokens: []
    status: enforced
    arch_anchor: "## Fail loud"
  ```

  carrying every field `Mandate` requires (`plugins/arch-compliance/python/acf/registry.py:50-61`);
  `ARCH_REL` holding the line `## Fail loud`; and `src/app.ts` with a function.
- On a branch `feature` cut from `main`, checked out: one commit changing `src/app.ts`.
  With `--plant empty-catch` the change adds a `try { … } catch {}`; with `--plant clean`
  it adds a function with no `catch`.

A new job `action` in `.github/workflows/ci.yml` checks out with `fetch-depth: 0` (the
third run needs the merge base) and builds both fixtures with
`PYTHONPATH=plugins/arch-compliance/python python tests/action_fixture_host.py …`: the
script needs only `acf.repo`, which imports the standard library and `acf.exceptions`
alone (`repo.py:1-7`), so it runs without an install. The job then runs the action from the
pull request's own tree (`uses: ./.github/actions/check-diff`) three times, each run
installing the plugin afresh (about three installs per job, accepted for a test that
exercises the action whole):

1. against the planted fixture under `$RUNNER_TEMP`, `repo` its absolute path, `base: main`,
   `continue-on-error: true`;
2. against the clean fixture, likewise, with `host-setup: touch "$RUNNER_TEMP/host-setup-ran"`;
3. against this repository itself (`repo: .`, `base` empty), replacing today's gate step in
   the `test` job (`.github/workflows/ci.yml:39-40`), so the base-ref derivation has one
   owner, the action.

A step right after the planted run fails the job unless that run's outcome is `failure`
and `$RUNNER_TEMP/acf-check-diff.txt` contains `BLOCK fail-loud.empty-catch` (a refusal
also exits 1, so the outcome alone does not prove the finding fired). A step after the clean
run fails the job unless its outcome is `success` and `$RUNNER_TEMP/host-setup-ran` exists. The job runs on every trigger of the workflow, so a
change to the action is tested before it is tagged.

### 4.3 `plugins/arch-compliance/skills/acf-setup/SKILL.md`

- **Frontmatter `description`, checklist item 8, the step 8 heading and the step 10 summary
  line (`:285`):** "pre-commit" becomes "pre-push".
- **Step 8, CI.** The sketch becomes a workflow file the host adds,
  `.github/workflows/arch-compliance.yml`:

  ```yaml
  name: Architecture compliance
  on:
    pull_request:
  jobs:
    arch-compliance:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v7
          with:
            fetch-depth: 0
        - uses: IanDBallard/arch-compliance-for-superpowers/.github/actions/check-diff@v<version>
  ```

  `<version>` is the installed plugin's version, so CI and the local hooks run the same
  detectors. The text says:
  - it runs on pull requests; when the host's registry has an active `fail_loud_ratchet`
    row or a host guard row at `ci`, `/acf-setup` adds `push: branches: [<default-branch>]`
    (§2 decision 3);
  - it carries no `paths-ignore`, so a host that makes it a required check never leaves a
    docs-only pull request waiting; a host may add its own;
  - a host with one CI workflow may instead add the job there under
    `if: github.event_name == 'pull_request'` (or the push condition above);
  - a host whose host detectors need dependencies adds `with: host-setup: <command>`;
    `/acf-setup` reads the host rows' detector files and proposes the command;
  - the action installs the plugin itself, so the host installs nothing for CI.

  The paragraph on `--trusted-checkout` keeps its rule and names the action's input as the
  place it lives.
- **Step 8, pre-push.** The pre-commit block is replaced by the command a pre-push hook
  runs, guarded:

  ```sh
  if command -v acf-check-diff >/dev/null 2>&1; then
    acf-check-diff --base "origin/<default-branch>" --repo . --call-site precommit || exit 1
  elif [ "${ACF_PREPUSH_OPTIONAL:-}" = "1" ]; then
    echo "acf-check-diff is not installed; ACF_PREPUSH_OPTIONAL=1, so skipping the architecture check (the pull request's CI job runs it)." >&2
  else
    echo "acf-check-diff is not installed: install the arch-compliance Python package (/acf-setup step 4), or set ACF_PREPUSH_OPTIONAL=1 where CI is the only gate." >&2
    exit 1
  fi
  ```

  `|| exit 1` and the final `exit 1` end the hook, with or without `set -e`, when the
  snippet sits at the hook's top level; inside a `( … )` subshell, `exit` leaves only the
  subshell, so the text tells hosts to place it at top level. The text says where to put
  it: a `pre-push` file in the directory `git config core.hooksPath` names, or
  `.git/hooks/pre-push` when it is unset, or the host's hook manager (husky, the pre-commit
  framework), configured to run the guarded command at pre-push. Where the host's hook
  already skips some pushes (docs only, say), the command goes after that skip. It says
  that `ACF_PREPUSH_OPTIONAL=1` belongs in an environment's own settings, never in a
  committed file, and that the opt-out is only as strong as what stops a red CI job from
  merging: a required status check where the host has one, otherwise the person merging
  reading the check. Before proposing the pre-push step and the workflow, `/acf-setup` runs
  `acf-check-diff --mode worktree --call-site precommit` and the same with
  `--call-site ci`, and reads a "selects no active" refusal (`cli_check_diff.py:94-100`) as
  "this site has no active row; do not wire it", since such a site would refuse every push
  or every pull request. The gate's own predicate decides; the skill does not restate it.
  The CI push-trigger check consumes the package, never a by-eye read of the YAML:
  `acf.detectors.load_gate_registry` loads the registry,
  `active(sites, detector="fail_loud_ratchet")` selects the ratchet and
  `host_rows(sites, detection="guard")` the host guards
  (`plugins/arch-compliance/python/acf/registry.py:130-147`). On a Windows machine the text
  tells the host to run the gate, in the hook as elsewhere, under `PYTHONUTF8=1`: the git
  runner does not declare its text encoding (`ARCHITECTURE.md`, `## Declared text
  decoding`). The local command never carries `--trusted-checkout`, so a host with
  host rows needs each person's `acf-allow`. The text states three known gaps; CI, on a
  clean checkout of the pull request, has none of them:
  - the diff is of committed work, but the gate reads each changed file from the working
    tree (`cli_check_diff.py:145`, `:153`, `:189`): an uncommitted edit can move a reported
    line, hide a committed violation, or, when the file is deleted, skip it;
  - the diff is of the checked-out branch, so `git push origin <another-branch>` checks the
    wrong commits;
  - the base is the local `origin/<default-branch>`, not fetched by the hook, so a stale one
    widens the checked range to commits already merged (extra findings, not misses).

  The hook does not refuse the states behind the first two, although both are detectable:
  refusing a dirty working tree would block every push made with unrelated uncommitted
  work, which is ordinary; refusing a push whose refs differ from `HEAD` means reading the
  refs git passes on standard input, which a host's own hook may already consume (the first
  adopter's does, `cy:.githooks/pre-push:7`), so the snippet stays free of standard input.
  Neither gap can pass a change into the default branch unseen: the pull request's CI job
  checks a clean checkout of exactly what merges.
- **The `--trusted-checkout` paragraph (`:249`):** "Only the CI sketch carries it. Never
  add it to the pre-commit snippet or to a command you run yourself." becomes "Only the CI
  action carries it (its `trusted-checkout` input). Never add it to the pre-push command or
  to a command you run yourself."
- **Upgrading section (`:251-258`):** "checked in pre-commit" (`:253`) becomes "checked
  before a push", "pre-commit invocations" becomes "local hook invocations", and the
  closing reminder to install the `acf` package for "hooks/CI" becomes "for local hooks;
  the CI action installs its own".
- **Step 9 and the friend-bar tip** keep `--mode worktree` / `--mode staged`: they smoke the
  toolchain on the current checkout, not the pushed branch.

`docs/guides/SUPERPOWERS_COMPLEMENT.md:40` changes "print pre-commit/CI snippets" to "print
pre-push/CI snippets". The README's upgrade notes for v0.2.4 and v0.2.5 (`README.md:136`,
`:141-142`) mention pre-commit and CI configuration as it stood at those releases; they are
history and stay as written, and the new v0.3.4 note supersedes them. The developer command
blocks in `README.md:53-58` ("developers / CI")
and `docs/guides/SUPERPOWERS_COMPLEMENT.md:78-83` each print a CI invocation
(`acf-check-diff --base origin/main --call-site ci --trusted-checkout`); both keep it as a
local command for this repository without `--trusted-checkout` (this repository has no
host rows, and the flag is for CI alone) and say that CI, here and in hosts, runs the
action. Their prose on the flag (`README.md:62`, `docs/guides/SUPERPOWERS_COMPLEMENT.md:87`,
"which CI workflows pass") stays true and gains "(the check-diff action passes it by
default)". `README.md` gains an "Upgrading a host to the check-diff action
(v0.3.4)" note beside the v0.3.3 one (`:112`): replace a pasted CI sketch with the action,
move a pre-commit entry to pre-push, and pin `v0.3.4`. `.github/dependabot.yml` gains a
`github-actions` entry for `/.github/actions/check-diff`, whose `uses:` lines the root entry
(`:19-22`) does not scan.

### 4.4 Doctrine and version

- `config/architecture/ARCHITECTURE.md`, `## Host detectors and call sites`, call-site rule:
  add after the sentence naming the diff sites: "`precommit` is the local git-hook site,
  whichever hook (pre-commit or pre-push) runs it."
- `## Release discipline`: add "Whoever merges a version bump tags its merge commit on
  `main` `v<version>`, once `main`'s CI run for that commit has passed, and pushes the tag;
  hosts pin the check-diff action to that tag." (The `action` job's run on the push to
  `main` is the first to exercise the empty-`base_ref` path.)
- `## Declared, never defaulted`: record the action's input defaults beside the package
  defaults it already lists (`:212-221`): `repo` `.`, `trusted-checkout` `true` (the
  workflow file is the opt-in), `base` derived from the event, and the Python and Node
  versions. They are action inputs, not host declarations a gate reads, so they sit
  outside the rule. The pre-push step's `ACF_PREPUSH_OPTIONAL` has no default: unset means
  refuse.
- The doctrine's opening scope (`:3-9`) adds the shipped action under `.github/actions/`,
  so the action is held to this doctrine like the hooks and the package.
- `## Post-merge`, post-merge CI bullet (`:330`): "(`test` job on `main`)" becomes
  "(`test` and `action` jobs on `main`)", since the gate run moves to the `action` job.
- `## Single point of definition`: record the install recipe's three copies and why they
  stay apart (§5).
- Version 0.3.4 in `plugins/arch-compliance/.claude-plugin/plugin.json` and
  `pyproject.toml` (a skill's prose changes). `acf-setup` is not one of the four skill
  trees `scripts/check_installed_skills.py` byte-checks, so no reinstall is owed.

---

## 5. Shape fit

| Existing responsibility | This design | Overlap |
| --- | --- | --- |
| `acf-check-diff` (`cli_check_diff.py:36-121`) decides what runs and what fails | the action installs it and calls it with flags it already has; its own stops (missing plugin files, Windows, a bad input value, a failed `host-setup`, a shallow clone) come before the gate and judge no code | none in what the gate decides |
| The plugin's own CI gate step (`.github/workflows/ci.yml:39-40`) derives the base ref and runs the gate on this repository | removed; the `action` job's third run does it through the action | one owner after the change |
| Installing `acf` and the TypeScript pack: `/acf-setup` step 4 (`acf-setup/SKILL.md:67-90`, a developer machine), the `test` job (`ci.yml:29-34`, `.[dev]` for pytest and the TypeScript self-test) and the action (a host's runner, its own virtual environment) | adds the third | three installs for three environments, recorded under `## Single point of definition`; merging them would make the `test` job install twice or put pytest in hosts' runners |
| `/acf-setup` step 8 prints the host's wiring | rewritten in place | replaces, does not duplicate |
| The PostToolUse hook (`hook` site) | unchanged | none |

---

## 6. Premise verification (authoring time, 2026-11-21, at `b9aaf77`)

| Premise | Receipt |
| --- | --- |
| The TS bridge resolves its pack from its source path, and no wheel carries the pack | `typescript_bridge.py:20`, quoted in §1; `pyproject.toml:39-40` |
| `--call-site` is required and `--trusted-checkout` exists | `cli_check_diff.py:64-82` |
| `--base` is a three-dot diff to `HEAD` | `diff.py:43-46`: `return [f"{base}...HEAD"]` |
| The ratchet and host guards run whatever the diff holds | `cli_check_diff.py:212-230` |
| Refusals and findings both exit 1; caught refusals print `acf:` | `cli_check_diff.py:106-108`, `:119-121` |
| The gate reads changed files from the working tree | `cli_check_diff.py:145` (`tree.file(rel)`) and `:153`/`:189` (`read_text`) |
| Host detector modules run in the gate's process | `host.py:102-109` (`spec_from_file_location`, `exec_module`) |
| `Mandate` requires `title` and `exemption_tokens` | `registry.py:50-61` |
| The repository has no tags | `git tag` prints nothing; `git ls-remote --tags origin` prints nothing |
| `/acf-setup` prints a pre-commit entry and a CI sketch with no install step | `acf-setup/SKILL.md:214-249`, `:258` |
| The first adopter's CI does not run the gate | `MSYS_NO_PATHCONV=1 git grep -c -i acf origin/main -- .github .githooks` in `cy:` exits 1 with no output |
| The first adopter's `main` has no required checks | `cy:.github/workflows/ci.yml:6-7`: "main has no required status checks"; `gh api repos/IanDBallard/Cayenne/branches/main/protection` returns 404 "Branch not protected" |
| The first adopter's registry has no `fail_loud_ratchet` row and no host guard row | `MSYS_NO_PATHCONV=1 git show 7313bca5:config/architecture/mandates.yml \| grep -n -E "^\s*(detection\|detector):"` in `cy:` lists one `guard` row, the built-in `no_build_artifacts` (`cy:config/architecture/mandates.yml:32-33`), and two host rows, both `ast` (`:142-143`, `:161-162`); `grep -c fail_loud_ratchet` prints 0 |
| This repository's registry has no host rows | `grep -n -E "^\s*detector:" config/architecture/mandates.yml \| grep -c ":.*\.py:"` prints 0: no `detector` names a `<path>.py:<callable>` reference (`ARCHITECTURE.md:142-145`, reference syntax) |
| No pytest configuration sets `python_files` | `grep -n python_files pyproject.toml` exits 1 (`pyproject.toml:23-25` sets only `testpaths` and `pythonpath`); `ls pytest.ini setup.cfg tox.ini tests/conftest.py` finds none |
| The repository does not document where GitHub places a remote action's files | `grep -rn "GITHUB_ACTION_PATH\|action_path"` outside `docs/design`, `docs/plans` and `docs/reviews` exits 1 |
| The first adopter's host detectors need its own `node_modules` | `cy:config/architecture/detectors/eslint_rules.py:33`: `ESLINT = WEB / "node_modules" / "eslint" / "bin" / "eslint.js"`; it imports only the standard library and `acf` (`:20-29`); its CI uses Node `'22'` (`cy:.github/workflows/ci.yml:94`) |

---

## 7. Definition of done

- The `action` CI job passes on this repository's pull request: the planted fixture fails
  the action with `BLOCK fail-loud.empty-catch` in `$RUNNER_TEMP/acf-check-diff.txt`, the clean fixture passes,
  `host-setup` ran, and the run against this repository passes.
- `/acf-setup` step 8 prints the workflow and the guarded pre-push command of §4.3.
- Version 0.3.4 merged, its merge commit tagged `v0.3.4` and the tag pushed.

---

## 8. First adopter (R6 acceptance; a change in `cy:`, after `v0.3.4`)

Recorded here so the plan can sequence it; it lands as its own pull request in `cy:`.

- `cy:.github/workflows/arch-compliance.yml`, the §4.3 workflow at `@v0.3.4`, with
  `host-setup: npm ci --prefix cayenne-web`: its host rows run the ESLint in
  `cayenne-web/node_modules`. Its registry has no `fail_loud_ratchet` row and no host guard
  row (§6 gives the recipe), so `pull_request` alone.
- `cy:.githooks/pre-push`: the guarded command at top level after its existing docs-only
  skip (`scope=$(node scripts/lib/pre-push-scope.mjs)`; the hook exits 0 when it prints
  `skip`) and before its final `exit 0`. Cloud
  sessions that push to it and do not install the plugin set `ACF_PREPUSH_OPTIONAL=1` in
  their environment settings; that is outside the repository and outside this design.
- `cy:config/architecture/ARCHITECTURE.md`, `## Post-merge`, post-merge CI bullet: it names
  `.github/workflows/ci.yml` on `main`. The new workflow runs on pull requests only, so it
  joins no post-merge list; the bullet gains one sentence saying the architecture check is
  a pull-request gate and has no post-merge run.
- Acceptance: a throwaway commit on that pull request adds a `catch {}` to a `.ts` file;
  the `arch-compliance` job fails with `BLOCK fail-loud.empty-catch`; the commit is
  reverted before merge and the job passes. This run is also the first use of the action
  from another repository (§2 decision 2): if the files it expects are not there, step 1
  says so.

---

## 9. Risks

| Risk | Answer |
| --- | --- |
| The pinned ref's files are not where the action expects them | step 1 stops and names both paths; the first adopter's pull request finds it before any other host adopts |
| A host pins a tag that does not match its installed plugin | CI and local runs disagree until both are upgraded; `/acf-setup` tells the host to pin the installed version |
| A forgotten tag | the host's `uses: …@v<version>` fails to resolve, at the host, loudly |
| A tag pushed on a commit whose `plugin.json` and `pyproject.toml` versions differ from its name | nothing in this design catches it; a read-only check comparing a pushed tag with those two fields is a follow-up outside this change |
| The action's install adds about a minute to each pull request | one job per pull request; pushes to the default branch only for hosts with whole-tree rows |
