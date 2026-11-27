---
name: acf-setup
description: Use when installing Architecture Compliance Framework (ACF) into a host repo, running /acf-setup, wiring mandates.yml or ARCHITECTURE.md for the first time, enabling .acf hooks, or adding pre-push/CI gates with acf-check-diff.
---

# /acf-setup — Host Project Bootstrap

Bootstrap Architecture Compliance Framework (ACF) into the **host** repository. Bundled plugin profiles are templates only; after setup, runtime always loads host `config/architecture/`.

**Prerequisite:** Superpowers must already be installed. If the user has not installed Superpowers, stop and tell them to install it first (`/plugin install superpowers@superpowers-dev` or their marketplace equivalent). Do not continue setup without that confirmation.

## Checklist

Complete these steps in order. Create a todo per step and check each off.

1. Confirm Superpowers prerequisite
2. Resolve plugin root + host root
3. Detect languages
4. Install runtime dependencies (Python package; TS detector `npm ci` when TypeScript detected)
5. Copy or merge profile(s) into host `config/architecture/`
6. Align ARCHITECTURE.md (prompt if host already has one)
6b. Write `config/architecture/review.yml` (ask the user for every value)
7. Write `.acf/enabled` marker
   - When `mandates.yml` has host rows, follow `acf-approve`; one approval covers every worktree of the repository whose host rows and detector files match. Never add `--trusted-checkout`
   - Offer the user these `permissions.ask` rules for `~/.claude/settings.json`, which back the plugin's approval hook with a documented prompt: `Bash(acf-allow:*)`, `Bash(python -m acf.cli_allow:*)`, `PowerShell(acf-allow:*)`, `PowerShell(python -m acf.cli_allow:*)` and `Edit(~/.acf/**)`. Add them only on the user's yes
8. Print pre-push / CI snippets
9. Smoke-run `acf-check-diff --call-site precommit`
10. Summarize what was written and next steps (`/acf-mandate`, `/architecture-review`)

## Step 1 — Superpowers prerequisite

Ask (or verify from context) that Superpowers is installed. If not:

> ACF is a Superpowers companion. Install Superpowers first, then re-run `/acf-setup`.

Do not copy profiles or write `.acf/enabled` until this is satisfied.

## Step 2 — Resolve roots

- **Host root:** current project / git top-level (`${CLAUDE_PROJECT_DIR}` when set, else `pwd` / workspace root).
- **Plugin root:** `${CLAUDE_PLUGIN_ROOT}` when set. If unset, locate the `arch-compliance` plugin directory that contains `profiles/react-app/` and `profiles/python-service/` (common caches: Claude plugins dir, or this marketplace checkout under `plugins/arch-compliance`).

Profile sources (relative to plugin root):

| Language signal | Profile directory |
|-----------------|-------------------|
| TypeScript/React | `profiles/react-app/` |
| Python | `profiles/python-service/` |

Each profile contains `mandates.yml` and `ARCHITECTURE.md`.

## Step 3 — Detect languages

Scan the host repo (ignore `node_modules`, `.venv`, `dist`, `build`, `__pycache__`):

**TypeScript / React** — true if **either**:
- `package.json` exists at host root (or a clear app package), **and** there is at least one `*.ts`, `*.tsx`, `*.jsx` source file; **or**
- substantial `*.ts` / `*.tsx` / `*.jsx` tree without needing to over-parse (prefer presence of `package.json` + TS/JSX sources).

**Python** — true if **either**:
- `pyproject.toml` or `setup.py` / `requirements.txt` at a sensible root; **or**
- non-trivial `*.py` sources outside virtualenvs.

Both may be true (polyglot host). Neither → ask the user which profile(s) to install; do not invent a third profile.

Announce detection result before copying, e.g. `Detected: typescript` / `python` / `both`.

## Step 4 — Install runtime dependencies

The hooks and CLI need two things on the host machine:

1. **Python package** — the `acf` package importable by the `python` on PATH:

   ```bash
   pip install -e ".[dev]"   # from the arch-compliance-for-superpowers checkout root
   ```

   Hooks invoke `python` (not `python3`). Verify `python -c "import acf"` succeeds with the
   interpreter that `python` resolves to. On macOS/Linux where only `python3` exists, ensure
   `python` resolves to Python 3.11+ (venv, conda, pyenv, or `python-is-python3`).

2. **TypeScript detector node_modules** (only when TypeScript was detected):

   ```bash
   npm ci --prefix "${CLAUDE_PLUGIN_ROOT}/detectors/typescript"
   ```

   Without this, any `.ts`/`.tsx` scan fails loud with a `DetectorPackError` telling the
   user to run exactly that command.

Do not proceed to the smoke check until both succeed (skip the npm step for Python-only hosts).

## Step 5 — Copy or merge into `config/architecture/`

Target directory (create if missing):

```text
<host>/config/architecture/mandates.yml
<host>/config/architecture/ARCHITECTURE.md
```

### Single language

Copy the matching profile’s `mandates.yml` and `ARCHITECTURE.md` into that directory.

If files already exist, **do not overwrite silently**. Ask: keep existing, replace from profile, or merge.

### Both languages (preferred: one merged pair)

Prefer **one** `mandates.yml` and **one** `ARCHITECTURE.md`:

1. **mandates.yml** — YAML list union of both profiles’ rows.
   - Keep every mandate `id` unique. If the same `id` appears in both (should not for stock profiles), stop and ask; never silently drop a row.
   - Preserve all schema fields per row.
   - Order: TypeScript/React mandates first, then Python (or keep profile order within each group).
2. **ARCHITECTURE.md** — merge prose under shared heading anchors.
   - Stock anchors that must survive (each mandate `arch_anchor` must remain a whole line of the file, equal after stripping): `## Fail loud`, `## No shims`, plus language-specific sections (`## React boundaries`, `## Soft fail-loud smells`, etc.).
   - If both profiles define the same `##` heading, merge body bullets under one heading; do not duplicate the heading.
   - Keep a short intro noting the host is polyglot.

**Conflict guidance:** If merge is ambiguous (customized host files, conflicting severity for related rules), present a short diff of choices and wait for confirmation. Never invent new mandate ids during setup.

### Fallback (only if user refuses merge)

Copy both profiles into clearly named siblings and tell the user ACF’s default path is still `config/architecture/mandates.yml` — they must pick one active registry or finish the merge themselves:

```text
config/architecture/mandates.yml          # must be the active registry
config/architecture/ARCHITECTURE.md
config/architecture/react-app.mandates.yml.bak
config/architecture/python-service.mandates.yml.bak
```

## Step 6 — ARCHITECTURE.md path

After copy/merge:

1. If the host already has architecture docs elsewhere (`docs/architecture/`, `ARCHITECTURE.md` at root, etc.), **ask** whether to:
   - keep the new stub at `config/architecture/ARCHITECTURE.md`, or
   - replace the stub with a copy/symlink/pointer note to their real doc, ensuring every `arch_anchor` from `mandates.yml` still appears as a whole line, equal after stripping, in the file ACF will use.
2. Remind: mandate `arch_anchor` values are matched by line equality (the stripped line must equal the anchor) against ARCHITECTURE.md — renaming headings without updating mandates breaks drift checks.

## Step 6b — Write `review.yml`

`/architecture-review` reads its host values from `<host>/config/architecture/review.yml`.
There is no default for a missing file or a missing field: every field is required, and
the review refuses to run without the file and names `/acf-setup`. Ask the user for each
value; do not invent them. If the file already exists, ask before replacing it.

| Field | Meaning |
|-------|---------|
| `report_dir` | repository-relative POSIX directory where `ARCHITECTURE_REVIEW_<date>.md` is written |
| `baseline_path` | repository-relative POSIX path of the drift baseline file (it need not exist yet; without it the review reports `no baseline`) |
| `baseline_max_age_days` | integer above 0: warn when the baseline is older than this many days |
| `baseline_max_commits` | integer above 0: warn when the baseline is more than this many commits behind `HEAD` |
| `packs` | list of technology pack ids the repository uses, from the six shipped ids `python`, `ts-js`, `react`, `svelte`, `html-templates`, `sql`; their file globs form the default target tree |
| `subsystems` | list of repository-relative POSIX directory prefixes used as drift buckets (longest prefix wins, an unmatched path is `other`); `[]` buckets by first path segment |
| `exclude` | list of globs added to the review's built-in exclusions; `[]` adds none |

Write all seven keys, for example:

```yaml
report_dir: <where reports go>
baseline_path: <where the baseline lives>
baseline_max_age_days: <integer above 0>
baseline_max_commits: <integer above 0>
packs: [<ids from the six above>]
subsystems: []
exclude: []
```

A reviewed mandate row without a declared `params.surface` sees only its packs' files, so a
`posix-paths` row meant to check committed data files (YAML, JSON, TOML) needs an explicit
`surface` naming them.

Paths use forward slashes; a backslash is refused.

## Step 7 — Enable hooks marker

Write an empty (or one-line) marker file:

```text
<host>/.acf/enabled
```

Create `.acf/` if needed. `.acf/enabled` turns on the automatic hooks for the built-in detectors: plugin hooks (see below) no-op until this file exists, except the approval prompt, which guards the per-user store in every repository; once present, missing `config/architecture/mandates.yml` is a hard failure. Host detectors (`detector: <path>.py:<callable>` rows) also need each person's approval (`acf-approve`). Do **not** write the marker before mandates are in place.

Suggest adding `.acf/` to git if the team wants hooks enabled for everyone; otherwise document that each clone needs the marker. Say plainly that committing `.acf/` approves no host code: each person's approval (`acf-approve`) is their own.

### Hook registration (Claude Code)

The plugin ships `hooks/hooks.json` which registers:

| Event | Script | Purpose |
|-------|--------|---------|
| `SubagentStart` | `hooks/inject_constraints.py --format hook` | Inject host mandates + ARCHITECTURE excerpt into subagent context |
| `PreToolUse` (`Bash\|PowerShell\|Write\|Edit\|MultiEdit\|NotebookEdit`) | `hooks/approval_prompt.py` | Force a permission prompt around any approval command or edit of the per-user approval store, in every repository whatever `.acf/enabled` says; fails closed |
| `PostToolUse` (`Write\|Edit\|MultiEdit`) | `hooks/posttooluse_gate.py --format hook` | Run Tier-1 Python/TS detectors, host detectors and host guards on edited paths (rows declaring `hook` or `posttooluse`; edited files outside the repository are not scanned; host detectors and host guards run only with an approval); feed findings back |

No host-side hook copy is required when the plugin is installed — Claude Code loads plugin `hooks/hooks.json` automatically. Manual smoke:

```bash
# from host repo (with .acf/enabled + mandates)
python "${CLAUDE_PLUGIN_ROOT}/hooks/inject_constraints.py" --repo .
python "${CLAUDE_PLUGIN_ROOT}/hooks/posttooluse_gate.py" --repo . path/to/edited.py
```

With host rows, the second command skips them (with a notice) until the user has approved (`acf-approve`).

If `CLAUDE_PLUGIN_ROOT` is unset, use the absolute path to `plugins/arch-compliance` in this marketplace checkout.

## Step 8 — Print pre-push / CI snippets

Print these for the user to paste (adapt package manager / paths as needed). Do not silently edit their CI or hooks unless they ask.

Before printing either, check that the site would gate something. From the host root run `acf-check-diff --mode worktree --call-site precommit` and `acf-check-diff --mode worktree --call-site ci`. A refusal that says the site "selects no active" `ast`/`guard` row means that site has no active row: do not wire it (it would refuse every push or every pull request); tell the user which rows need the site added. Any other result means the site has rows. The gate's own check decides; do not restate it by reading the YAML.

### CI (GitHub Actions)

Add a workflow file, `.github/workflows/arch-compliance.yml`:

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

- `<version>` is the installed plugin's version, so CI and the local hooks run the same detectors.
- The action installs the plugin itself (from its own files, into its own virtual environment); the host installs nothing for CI. It runs on Linux and macOS runners.
- It runs on pull requests. On a push to the default branch the diff is empty, so per-file rows check nothing. Add `push: branches: [<default-branch>]` only when the registry has an active `fail_loud_ratchet` row or a host guard row at `ci`, which run on an empty diff. Decide with the package, never by eye: `acf.detectors.load_gate_registry(repo, repo / acf.repo.MANDATES_REL)`, then `registry.active(frozenset({"ci"}), detector="fail_loud_ratchet")` and `registry.host_rows(frozenset({"ci"}), detection="guard")`.
- It carries no `paths-ignore`, so a host that makes it a required check never leaves a docs-only pull request waiting; the host may add its own.
- A host with one CI workflow may instead add the job there under `if: github.event_name == 'pull_request'` (or the push condition above).
- When host detectors need dependencies (a Python package, or `node_modules` for a tool they run), add `with: host-setup: <command>` to the `uses:` step. Read the host rows' detector files and propose the command (for example `npm ci --prefix web`). It runs from the host root after the action's own setup, with its virtual environment first on `PATH`.
- Other inputs: `base` (default: the pull request's base, or the default branch), `repo` (default `.`), `trusted-checkout` (default `true`), `python-version` (`3.12`), `node-version` (`22`).

`--trusted-checkout` runs host detectors without a local approval; in CI the workflow file is the opt-in. Only the CI action carries it (its `trusted-checkout` input). Never add it to the pre-push command or to a command you run yourself.

### Pre-push (local)

The command a pre-push hook runs, guarded:

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

- Put it in a `pre-push` file in the directory `git config core.hooksPath` names, or `.git/hooks/pre-push` when it is unset, or configure the host's hook manager (husky, the pre-commit framework) to run it at pre-push. Place it at the hook's top level, not inside a `( … )` subshell, where `exit` would leave only the subshell. Where the hook already skips some pushes (documentation only, say), put it after that skip.
- Any non-zero exit blocks the push: a finding, a refusal (a missing approval, a TypeScript pack without `npm ci`, a base it cannot resolve) or a crash. Fix the local gate rather than passing over it.
- `ACF_PREPUSH_OPTIONAL=1` belongs in an environment's own settings (a cloud session's environment, say), never in a committed file, so a fresh clone still refuses. Unset, or any other value, refuses. The opt-out is only as strong as what stops a red CI job from merging: a required status check where the host has one, otherwise the person merging reading the check.
- With host rows, a pre-push run needs each person's approval (`acf-approve`); the command carries no `--trusted-checkout`.
- On Windows, run the gate under `PYTHONUTF8=1`: the TypeScript bridge does not declare its text encoding.
- Known gaps, which the pull request's CI job (a clean checkout of exactly what merges) does not have:
  - the diff is of committed work, but changed files are read from the working tree, so an uncommitted edit can move a reported line, hide a committed violation or, when the file is deleted, skip it;
  - the diff is of the checked-out branch, so `git push origin <another-branch>` checks the wrong commits;
  - the base is the local `origin/<default-branch>`, not fetched by the hook, so a stale one widens the checked range to commits already merged.

`--call-site {ci,precommit}` is required and selects the rows that run: only active rows that declare that site. `precommit` is the local git-hook site, whichever hook runs it. A site that selects no active `ast`/`guard` row is refused (exit 1), not reported as a clean run.

### Upgrading a host installed before `--call-site` (v0.2.4)

- Add `precommit` to the `call_sites` of each `ast`/`guard` row the host wants checked before a push. Registries copied from a profile before this release declare no `precommit` site (typically `[ci, hook]`), and a `--call-site precommit` run that selects no active row is refused ("selects no active", exit 1), never a silent pass.
- Add `--call-site ci` / `--call-site precommit` to the host's own CI and local hook invocations; omitting it exits 2 with a usage error.
- Set `status: unenforced` on any `partial` row whose detector or prompt does not exist yet; an active (`enforced` or `partial`) row naming a missing one is refused when the registry loads.
- Load-time refusals also cover a `call_sites` value outside `ci`, `precommit`, `hook`, `posttooluse`, `audit` (for example `pre-commit` is refused; use `precommit`), an active `ast`/`guard` row whose only site is `audit`, and an active non-built-in row that reuses a built-in mandate id (reserved).

Remind them the CLI defaults to `<repo>/config/architecture/mandates.yml`. Install the `acf` package into the environment used by local hooks; the CI action installs its own (`pip install` from the marketplace plugin’s Python package / editable install as documented in the repo README).

## Step 9 — Smoke check

From the **host** root, run one of:

```bash
acf-check-diff --mode worktree --call-site precommit
```

If `mandates.yml` has host rows, the user's approval must exist first; a refusal that names `acf-allow` is not a pass. Approve only through `acf-approve`; never add `--trusted-checkout`.

Success criteria:

- Mandates load without `AcfInputError` / `UnknownDetectorError`.
- Exit 0 if no `BLOCK` findings on the current diff; exit 1 only for real BLOCK findings (still a successful smoke of the toolchain).
- An exit 2 usage error (a missing or unknown `--call-site`) or a "selects no active" refusal means the invocation or the registry needs fixing (for example a registry whose rows declare no `precommit` needs `precommit` added); it is not a pass.
- If the command is missing, help install the plugin Python package, then retry. Do not claim setup complete until the CLI runs.

Optional friend-bar tip: plant a temporary empty `catch {}` (TS) or bare `except:` (Python), stage it, re-run with `--mode staged --call-site precommit`, confirm BLOCK/WARN, then revert.

## Step 10 — Done summary

Tell the user:

- Languages detected and which profile(s) were applied
- Paths written: `config/architecture/mandates.yml`, `config/architecture/ARCHITECTURE.md`, `config/architecture/review.yml`, `.acf/enabled`
- That pre-push/CI snippets were printed (not necessarily applied)
- Smoke command result
- Next: customize with `/acf-mandate`; full audit later with `/architecture-review`
- Host config overrides plugin templates from now on

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Skipping Superpowers | Stop; install Superpowers first |
| Overwriting customized mandates | Ask before replace; prefer merge |
| Writing `.acf/enabled` before mandates | Write marker last among config steps |
| Leaving polyglot hosts with two active registries | Merge into one `mandates.yml` |
| Changing ARCHITECTURE headings without updating `arch_anchor` | Keep literal heading strings or update registry |
| Claiming success without CLI smoke | Run `acf-check-diff --call-site precommit` |
