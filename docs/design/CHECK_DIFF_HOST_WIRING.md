# One Shipped Way for a Host to Run `acf-check-diff` in CI and Before a Push

**Status:** v1 — approved by the user 2026-11-21; awaiting adversarial design review.
**Spec kinds:** `feature`
**Repo:** `IanDBallard/arch-compliance-for-superpowers`, `main` at `b9aaf77` (release 0.3.3).
**Workstream:** HistoricMansions Workstream E, host roll-out step R6 ("Wire `acf-check-diff`
into CI and pre-commit"; acceptance "A planted `catch {}` fails the CI job"). The plugin
ships the wiring once. Each host then adopts it with a few lines, and the first adopter's
pull request carries R6's acceptance (§8).
**Governing mandates:** `config/architecture/ARCHITECTURE.md` sections `## Host detectors
and call sites` (`:140-187`, the call-site rule and the trust boundary), `## Prose names no
host` (`:223-233`), `## No completeness claims` (`:249-259`), `## Release discipline`
(`:274-284`) and `## Live consumers` (`:243-247`).
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
pre-commit entry running `acf-check-diff --mode staged --call-site precommit`, and a CI
sketch running `acf-check-diff --base … --call-site ci --trusted-checkout`. The CI sketch
leaves out how `acf-check-diff` gets onto the runner, and that is the hard part. The
TypeScript detector finds its Node scanner relative to its own source file:

> `_PACK_ROOT = Path(__file__).resolve().parents[3] / "detectors" / "typescript"`
> (`plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:20`)

So a wheel install cannot scan `.ts` or `.tsx` files. The runner needs a source checkout of
this repository, an editable install of it, and `npm ci` in
`plugins/arch-compliance/detectors/typescript`. Every host would have to work that out and
keep its copy in step with each release.

This design ships that wiring as a composite GitHub Action in this repository, so a host's
whole CI wiring is a checkout and one `uses:` line pinned to a release tag. It also replaces
the pre-commit snippet with a pre-push step, which runs once per push rather than once per
commit and skips with a warning where `acf-check-diff` is not installed.

The gate then runs at three points in a host, each with its own job:

| Point | Call site | What it catches | Owner |
| --- | --- | --- | --- |
| Claude's edits | `hook` | the edited file, as it is written | the plugin's PostToolUse hook, unchanged (`.acf/enabled`) |
| Before a push | `precommit` | the branch's commits, before CI sees them | the host's pre-push hook, from the §4.3 snippet |
| Pull requests | `ci` | the pull request's diff against its base, from any author | the §4.1 action, from the host's workflow |

---

## 2. Decisions this design records

1. **A composite action, not a reusable workflow or templates.** The host keeps its own job
   (its triggers, any extra steps, what depends on it) and adds one step. A reusable
   workflow would own the whole job; templates copied into each host drift and need an edit
   in every host on every release.
2. **The action installs from its own download.** GitHub runs an action referenced as
   `owner/repo/path@ref` from that repository at that ref. The contexts reference says
   `github.action_path` lets an action reach files in the same repository as the action.
   The action therefore installs the `acf` package editable from the repository root
   (three levels above `github.action_path`) and runs `npm ci` there. No second checkout.
   A host's own detectors may need their own dependencies (a host detector that shells out
   to the host's ESLint needs the host's `node_modules`), so the action takes one host setup
   command and runs it after its own setup, with its Python and Node active (§4.1).
3. **Pull requests only.** On a push to the default branch `origin/<default>` is `HEAD`, so
   the three-dot diff is empty (`plugins/arch-compliance/python/acf/diff.py:43-46`) and a
   run there checks nothing. The snippet is a workflow triggered by `pull_request` alone.
4. **`--trusted-checkout` is on by default in the action, with an input to turn it off.**
   The trust boundary already makes the workflow file the opt-in for CI: "for
   `acf-check-diff`, when the invocation passes `--trusted-checkout`"
   (`config/architecture/ARCHITECTURE.md:178-181`), and the CI sketch says "in CI the
   workflow file is the opt-in" (`plugins/arch-compliance/skills/acf-setup/SKILL.md:249`).
   Naming the action in a workflow is that opt-in.
5. **Pre-push replaces pre-commit in `/acf-setup`.** The `precommit` call site keeps its
   name and means the local git-hook site, whichever hook runs it. Pre-push diffs the
   branch against `origin/<default>` with `--base`, the same scope CI uses.
6. **The local step skips only when the gate is absent.** A cloud session or a fresh clone
   may not have `acf-check-diff`. The pre-push step then prints one line saying the check
   was skipped and that CI runs it, and lets the push continue. Once the command is
   installed, any non-zero exit blocks the push, a refusal included: `acf-check-diff`
   returns 1 for a finding and for a refusal alike (a missing `acf-allow`, a TypeScript pack
   without `npm ci`, a base it cannot resolve), and each refusal prints `acf: …` naming its
   fix. A local gate that is installed but cannot run is fixed, not passed over; telling the
   two apart would mean parsing stderr.
7. **Releases are tagged, by hand.** The repository has no tags today (`git tag` prints
   nothing). Hosts pin the action to `v<version>`, so whoever merges a version bump tags
   its merge commit on `main` `v<version>` and pushes the tag, starting with `v0.3.4`. No
   skill or workflow does it.

---

## 3. Non-goals

- Windows runners. The action supports Linux and macOS runners and stops with a message on
  Windows (`runner.os == 'Windows'`).
- Changing `acf-check-diff` itself, its flags or its exit codes.
- The LLM rows (`detection: llm`, `acf-check-llm`). They stay out of every automatic gate.
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
| `base` | empty | the ref to diff against; empty means `origin/<github.base_ref>`, or `origin/<the repository's default branch>` when there is no base ref |
| `repo` | `.` | the host repository's root, relative to the workspace |
| `trusted-checkout` | `true` | `true` passes `--trusted-checkout`; `false` does not; any other value stops the action with a message naming the input |
| `python-version` | `3.12` | handed to `actions/setup-python` |
| `node-version` | `22` | handed to `actions/setup-node` |
| `host-setup` | empty | a shell command run from `repo` before the gate, for the host detectors' own dependencies (for example `npm ci --prefix web`); empty runs nothing |

Steps, in order:

1. Stop with a message on a Windows runner.
2. `actions/setup-python` with `python-version`.
3. Create a virtual environment under `$RUNNER_TEMP` and `pip install -e` the repository
   root at `$GITHUB_ACTION_PATH/../../..` into it. The virtual environment keeps the
   plugin's dependencies out of the host's own Python environment.
4. `actions/setup-node` with `node-version`, then `npm ci` in
   `$GITHUB_ACTION_PATH/../../../plugins/arch-compliance/detectors/typescript`.
5. When `host-setup` is not empty, run it with `bash` from `repo`, the virtual
   environment's `bin` first on `PATH` (so a `pip install` there lands in the environment
   the gate imports host detectors from) and step 4's Node active. A non-zero exit stops the
   action.
6. Stop with a message naming `fetch-depth: 0` when
   `git -C <repo> rev-parse --is-shallow-repository` prints `true`: the three-dot diff needs
   the merge base.
7. Run the virtual environment's `acf-check-diff --repo <repo> --base <base> --call-site ci`,
   with `--trusted-checkout` when the input is `true`. Its exit status is the step's.

Steps 2 and 4 change the job's `python` and `node` for any later step, and replace any a
host set up before the action, so the snippet runs the action in a job of its own and a
host's detector dependencies go in `host-setup`, not in steps before the action.

### 4.2 The action's test: `scripts/make_action_fixture_host.py` (new) and a CI job

`scripts/make_action_fixture_host.py <dest> --plant {empty-catch,clean}` builds a git
repository at `<dest>`:

- On `main`: `config/architecture/mandates.yml` with one row, `fail-loud.empty-catch`
  (`BLOCK`, `ast`, `empty_catch`, `typescript`, `call_sites: [ci]`, `enforced`,
  `arch_anchor: "## Fail loud"`), `config/architecture/ARCHITECTURE.md` carrying the
  `## Fail loud` line, and `src/app.ts` with a function.
- On a branch `feature` cut from `main`, checked out: one commit changing `src/app.ts`.
  With `--plant empty-catch` the change adds a `try { … } catch {}`; with `--plant clean`
  it adds a function with no `catch`.

A new job `action` in `.github/workflows/ci.yml` builds both fixtures under
`$RUNNER_TEMP` and runs the action from the pull request's own tree
(`uses: ./.github/actions/check-diff`) against each, with `base: main`. The clean run also
passes `host-setup: touch "$RUNNER_TEMP/host-setup-ran"`. The planted run has
`continue-on-error: true`; a following step fails the job unless the planted run's outcome
is `failure`, the clean run's is `success`, and `$RUNNER_TEMP/host-setup-ran` exists. The job runs on every trigger of
the workflow, so a change to the action is tested before it is tagged.

### 4.3 `plugins/arch-compliance/skills/acf-setup/SKILL.md`

- **Frontmatter `description`, checklist item 8 and the step 8 heading:** "pre-commit" becomes
  "pre-push".
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
        - uses: actions/checkout@v4
          with:
            fetch-depth: 0
        - uses: IanDBallard/arch-compliance-for-superpowers/.github/actions/check-diff@v<version>
  ```

  `<version>` is the installed plugin's version, so CI and the local hooks run the same
  detectors. The text says: it runs on pull requests only (§2 decision 3); it carries no
  `paths-ignore`, so a host that makes it a required check never leaves a docs-only pull
  request waiting, and a host may add its own; and a host with one CI workflow may instead
  add the job there under `if: github.event_name == 'pull_request'`. A host whose host
  detectors need dependencies adds `with: host-setup: <command>` to the `uses:` step;
  `/acf-setup` reads the host rows' detector files and proposes the command. The paragraph on
  `--trusted-checkout` keeps its rule and names the action's input as the place it lives.
- **Step 8, pre-push.** The pre-commit block is replaced by the command a pre-push hook
  runs, guarded:

  ```sh
  if command -v acf-check-diff >/dev/null 2>&1; then
    acf-check-diff --base "origin/<default-branch>" --repo . --call-site precommit
  else
    echo "acf-check-diff is not installed; skipping the architecture check (CI runs it)." >&2
  fi
  ```

  The text says how to place it for the host's mechanism: a `pre-push` file in the
  directory `git config core.hooksPath` names, or `.git/hooks/pre-push` when it is unset;
  `.husky/pre-push`; or a pre-commit framework entry with `stages: [pre-push]` and
  `entry: sh -c '<the guarded command>'`. Where the host's hook already skips some pushes
  (docs only, say), the command goes after that skip. Once installed, a non-zero exit
  blocks the push, a refusal included (§2 decision 6). It keeps the existing rule that the
  local command never carries `--trusted-checkout`, so a host with host rows needs each
  person's `acf-allow`. It states the one known gap: the diff is of committed work, but the
  gate reads each changed file from the working tree, so uncommitted edits to a changed file
  can move a reported line; CI, on a clean checkout, has no such gap.
- **Upgrading section (`:251-256`):** "pre-commit invocations" becomes "local hook
  invocations".
- **Step 9 and the friend-bar tip** keep `--mode worktree` / `--mode staged`: they smoke the
  toolchain on the current checkout, not the pushed branch.

`docs/guides/SUPERPOWERS_COMPLEMENT.md:40` changes "print pre-commit/CI snippets" to "print
pre-push/CI snippets".

### 4.4 Doctrine and version

- `config/architecture/ARCHITECTURE.md`, `## Host detectors and call sites`, call-site rule:
  add after the sentence naming the diff sites: "`precommit` is the local git-hook site,
  whichever hook (pre-commit or pre-push) runs it."
- `## Release discipline`: add "Whoever merges a version bump tags its merge commit on
  `main` `v<version>` and pushes the tag; hosts pin the check-diff action to that tag."
- Version 0.3.4 in `plugins/arch-compliance/.claude-plugin/plugin.json` and
  `pyproject.toml` (a skill's prose changes).

---

## 5. Shape fit

| Existing responsibility | This design | Overlap |
| --- | --- | --- |
| `acf-check-diff` (`plugins/arch-compliance/python/acf/cli_check_diff.py:36-121`) decides what runs and what fails | the action installs it and calls it with flags it already has | none: no gate logic in the action |
| The plugin's own CI step (`.github/workflows/ci.yml:39-40`) runs the gate on this repository from its own editable install | unchanged; the new `action` job tests the action on fixtures | none: different subjects |
| `/acf-setup` step 8 prints the host's wiring | rewritten in place | replaces, does not duplicate |
| The PostToolUse hook (`hook` site) | unchanged | none |

---

## 6. Premise verification (authoring time, 2026-11-21, at `b9aaf77`)

| Premise | Receipt |
| --- | --- |
| The TS bridge resolves its pack from its source path | `typescript_bridge.py:20`, quoted in §1 |
| `--call-site` is required and `--trusted-checkout` exists | `cli_check_diff.py:64-82` |
| `--base` is a three-dot diff to `HEAD` | `diff.py:43-46`: `return [f"{base}...HEAD"]` |
| The gate reads changed files from the working tree | `cli_check_diff.py:145` (`tree.file(rel)`) and `:153`/`:189` (`read_text`) |
| The repository has no tags | `git tag` prints nothing |
| `/acf-setup` prints a pre-commit entry and a CI sketch | `acf-setup/SKILL.md:214-249` |
| The first adopter's CI does not run the gate | `MSYS_NO_PATHCONV=1 git grep -c -i acf origin/main -- .github .githooks` in `cy:` exits 1 with no output |
| The first adopter's `main` has no required checks | `cy:.github/workflows/ci.yml:6-7`: "main has no required status checks"; `gh api repos/IanDBallard/Cayenne/branches/main/protection` returns 404 "Branch not protected" |
| The first adopter's host detectors need its own `node_modules` | `cy:config/architecture/detectors/eslint_rules.py:33`: `ESLINT = WEB / "node_modules" / "eslint" / "bin" / "eslint.js"`; it imports only the standard library and `acf` (`:20-29`); its CI uses Node `'22'` (`cy:.github/workflows/ci.yml:94`) |
| An action can reach its own repository's files | GitHub's contexts reference, `github.action_path`: "The path where an action is located." with the note that it reaches files in the action's repository. Proven end to end by §8's run, which uses the action from another repository |

---

## 7. Definition of done

- The `action` CI job passes on this repository's pull request: the planted fixture fails
  the action and the clean fixture passes it.
- `/acf-setup` step 8 prints the workflow and the guarded pre-push command of §4.3.
- Version 0.3.4 merged, its merge commit tagged `v0.3.4` and the tag pushed.

---

## 8. First adopter (R6 acceptance; a change in `cy:`, after `v0.3.4`)

Recorded here so the plan can sequence it; it lands as its own pull request in `cy:`.

- `cy:.github/workflows/arch-compliance.yml`, the §4.3 workflow at `@v0.3.4`, with
  `host-setup: npm ci --prefix cayenne-web`: its host rows run the ESLint in
  `cayenne-web/node_modules`.
- `cy:.githooks/pre-push`: the guarded command after its existing docs-only skip
  (`scope=$(node scripts/lib/pre-push-scope.mjs)`, which exits early on `skip`).
- `cy:config/architecture/ARCHITECTURE.md`, `## Post-merge`, post-merge CI bullet: it names
  `.github/workflows/ci.yml` on `main`. The new workflow runs on pull requests only, so it
  joins no post-merge list; the bullet gains one sentence saying the architecture check is
  a pull-request gate and has no post-merge run.
- Acceptance: a throwaway commit on that pull request adds a `catch {}` to a `.ts` file;
  the `arch-compliance` job fails with `BLOCK fail-loud.empty-catch`; the commit is
  reverted before merge and the job passes.

---

## 9. Risks

| Risk | Answer |
| --- | --- |
| A fork's pull request runs its own host detectors under `--trusted-checkout` | the same exposure as today's CI sketch; `pull_request` runs from forks get a read-only token and no secrets. A host that wants otherwise sets `trusted-checkout: false` and has no host rows |
| A host pins a tag that does not match its installed plugin | CI and local runs disagree until both are upgraded; `/acf-setup` tells the host to pin the installed version |
| The action's install adds about a minute to each pull request | one job per pull request, none on pushes to the default branch |
