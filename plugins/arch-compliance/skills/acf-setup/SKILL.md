---
name: acf-setup
description: Use when installing Architecture Compliance Framework (ACF) into a host repo, running /acf-setup, wiring mandates.yml or ARCHITECTURE.md for the first time, enabling .acf hooks, or adding pre-commit/CI gates with acf-check-diff.
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
7. Write `.acf/enabled` marker
8. Print pre-commit / CI snippets
9. Smoke-run `acf-check-diff`
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
   - Stock anchors that must survive (mandates `arch_anchor` must remain literal substrings of the file): `## Fail loud`, `## No shims`, plus language-specific sections (`## React boundaries`, `## Soft fail-loud smells`, etc.).
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
   - replace the stub with a copy/symlink/pointer note to their real doc, ensuring every `arch_anchor` from `mandates.yml` still appears as an exact heading substring in the file ACF will use.
2. Remind: mandate `arch_anchor` values are matched as literal substrings of ARCHITECTURE.md — renaming headings without updating mandates breaks drift checks.

## Step 7 — Enable hooks marker

Write an empty (or one-line) marker file:

```text
<host>/.acf/enabled
```

Create `.acf/` if needed. Plugin hooks (see below) no-op until this file exists; once present, missing `config/architecture/mandates.yml` is a hard failure. Do **not** write the marker before mandates are in place.

Suggest adding `.acf/` to git if the team wants hooks enabled for everyone; otherwise document that each clone needs the marker.

### Hook registration (Claude Code)

The plugin ships `hooks/hooks.json` which registers:

| Event | Script | Purpose |
|-------|--------|---------|
| `SubagentStart` | `hooks/inject_constraints.py --format hook` | Inject host mandates + ARCHITECTURE excerpt into subagent context |
| `PostToolUse` (`Write\|Edit\|MultiEdit`) | `hooks/posttooluse_gate.py --format hook` | Run Tier-1 Python/TS detectors on edited paths; feed findings back |

No host-side hook copy is required when the plugin is installed — Claude Code loads plugin `hooks/hooks.json` automatically. Manual smoke:

```bash
# from host repo (with .acf/enabled + mandates)
python "${CLAUDE_PLUGIN_ROOT}/hooks/inject_constraints.py" --repo .
python "${CLAUDE_PLUGIN_ROOT}/hooks/posttooluse_gate.py" --repo . path/to/edited.py
```

If `CLAUDE_PLUGIN_ROOT` is unset, use the absolute path to `plugins/arch-compliance` in this marketplace checkout.

## Step 8 — Print pre-commit / CI snippets

Print these for the user to paste (adapt package manager / paths as needed). Do not silently edit their CI unless they ask.

### Pre-commit (local)

```yaml
# .pre-commit-config.yaml — example local repo hook
repos:
  - repo: local
    hooks:
      - id: acf-check-diff
        name: acf-check-diff
        entry: acf-check-diff --mode staged
        language: system
        pass_filenames: false
        stages: [pre-commit]
```

Fallback if console script is not on PATH:

```bash
python -m acf.cli_check_diff --mode staged
```

### CI (GitHub Actions sketch)

In CI the checkout is clean, so `--mode staged` / `--mode worktree` see an empty
diff and always pass. Use `--base` to diff the branch against its merge-base:

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0   # --base needs history for merge-base
- name: Architecture compliance (diff vs base)
  run: acf-check-diff --base "origin/${{ github.base_ref || 'main' }}" --repo .
  # or: python -m acf.cli_check_diff --base origin/main --repo .
```

Remind them the CLI defaults to `<repo>/config/architecture/mandates.yml`. Install the `acf` package into the environment used by hooks/CI (`pip install` from the marketplace plugin’s Python package / editable install as documented in the repo README).

## Step 9 — Smoke check

From the **host** root, run one of:

```bash
acf-check-diff --mode worktree
# or
python -m acf.cli_check_diff --mode worktree
```

Success criteria:

- Mandates load without `RegistryLoadError` / `UnknownDetectorError`.
- Exit 0 if no `BLOCK` findings on the current diff; exit 1 only for real BLOCK findings (still a successful smoke of the toolchain).
- If the command is missing, help install the plugin Python package, then retry. Do not claim setup complete until the CLI runs.

Optional friend-bar tip: plant a temporary empty `catch {}` (TS) or bare `except:` (Python), stage it, re-run with `--mode staged`, confirm BLOCK/WARN, then revert.

## Step 10 — Done summary

Tell the user:

- Languages detected and which profile(s) were applied
- Paths written: `config/architecture/mandates.yml`, `config/architecture/ARCHITECTURE.md`, `.acf/enabled`
- That pre-commit/CI snippets were printed (not necessarily applied)
- Smoke command result
- Next: customize with `/acf-mandate`; full audit later with `/architecture-review` (when available)
- Host config overrides plugin templates from now on

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Skipping Superpowers | Stop; install Superpowers first |
| Overwriting customized mandates | Ask before replace; prefer merge |
| Writing `.acf/enabled` before mandates | Write marker last among config steps |
| Leaving polyglot hosts with two active registries | Merge into one `mandates.yml` |
| Changing ARCHITECTURE headings without updating `arch_anchor` | Keep literal heading strings or update registry |
| Claiming success without CLI smoke | Run `acf-check-diff` or `python -m acf.cli_check_diff` |
