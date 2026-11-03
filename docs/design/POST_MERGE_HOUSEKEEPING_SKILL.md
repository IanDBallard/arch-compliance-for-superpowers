# Portable `post-merge-housekeeping` Skill in `arch-compliance`

**Status:** v1 — draft for adversarial design review (`writing-plans` blocked until CLEARED).
**Adversarial review:** pending
**Spec kinds:** `feature`
**Repo:** `IanDBallard/arch-compliance-for-superpowers`, `main` at `5623832`; implemented on branch `feat/post-merge-housekeeping`.
**Workstream:** HistoricMansions Workstream E (portable governance skills), discharging `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:563-565` follow-up 2 (plugin side).
**Governing mandates:** `config/architecture/ARCHITECTURE.md` sections `## Fail loud` (`:24-41`), `## No shims` (`:43-53`), `## POSIX paths` (`:55-64`), `## One base exception` (`:99-103`), `## One owner for host paths` (`:105-116`), `## Declared, never defaulted` (`:118-133`), `## Prose names no host` (`:135-141`), `## Frozen ledger format` (`:143-149`), `## Live consumers` (`:151-155`), `## No completeness claims` (`:157-167`), `## Declared text decoding` (`:169-180`), `## Release discipline` (`:182-191`), `## Single point of definition` (`:193-206`), `## Scoped refactor` (`:208-212`), and the five portable governing principles at `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51`.
**No state-machine surface.** This design adds or modifies no state machine and no transition.

---

## 0. Citation convention

Unprefixed paths refer to this repository (`IanDBallard/arch-compliance-for-superpowers`) at `main` (`5623832`). Paths prefixed `hm:` refer to the sibling repository `HistoricMansions` at `b652fab05` (`main`), following the precedent established in `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:10-32`. Every path is written in full with POSIX slashes and without `...` ellipses.

---

## 1. Goal

Extract and generalize the `post-merge-housekeeping` skill from `hm:.claude/skills/post-merge-housekeeping/SKILL.md` into `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` so that any repository using Superpowers and `arch-compliance` — regardless of its constituent technology stack (Python, TypeScript/React, C/C++ firmware, Flutter/Dart, Go, Rust) or directory layout — runs one canonical post-merge ritual from the plugin.

Moving `post-merge-housekeeping` into the plugin closes three gaps recorded in prior specs:

1. **Cross-skill handoff completion:** In `docs/design/ADR_GATE_HOST_CONTRACT.md:172-174, 213`, `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:363` and `plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:223` had to replace `post-merge-housekeeping` with `"by the host's post-merge process"` solely because `post-merge-housekeeping` was still HM-local. With `post-merge-housekeeping` in `plugins/arch-compliance/skills/`, both gate skills name `post-merge-housekeeping` directly again.
2. **Ledger-amendment row-identity rule after a verification pass or user override:** `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:563-565` scheduled the `post-merge-housekeeping` spec to add the row-identity rule for `LedgerAmendment` when a spec cleared via a controller verification pass or user override (`plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:437-453`), because neither writes a new `LedgerRow` and the spec header's `(repo @ <sha>)` differs from the last full dispatch's `LedgerRow.commit_sha`.
3. **Prose portability & byte-check coverage:** `plugins/arch-compliance/tests/test_adr_skill_prose.py`, `plugins/arch-compliance/tests/test_adr_skill_invariants.py`, and `scripts/check_installed_skills.py` are extended so `post-merge-housekeeping/SKILL.md` is held to the same `## Prose names no host`, AST-valid Python snippet, POSIX-slash, and installed-copy byte-identity invariants as `adversarial-design-review` and `responding-to-adversarial-review`.

---

## 2. Decisions this design records

1. **Doctrine-driven host conventions + existing `config/architecture/adr.yml`; no new YAML configuration file.** (user, 2026-11-03)
   - `post-merge-housekeeping` introduces no `config/architecture/housekeeping.yml` and no new Pydantic config loader.
   - Its only Python package inputs are the existing `acf.repo` constants (`ADR_REL`, `ARCH_REL`, `resolve_repo` at `plugins/arch-compliance/python/acf/repo.py:18-44`) and `acf.adr` (`load_host_config`, `LedgerAmendment`, `append_amendment` at `plugins/arch-compliance/python/acf/adr/host.py:28-33` and `plugins/arch-compliance/python/acf/adr/ledger.py:132-172, 231-237`).
   - Host-specific operational conventions (whether the host uses a shared-checkout branch lock file, whether tests spawn background daemons/simulators from worktrees and how to probe them, whether post-merge CI/deploy workflows must be verified on the default branch, and where the host files deferred review items and guard escapes) are read from the host's doctrine (`config/architecture/ARCHITECTURE.md` and the documents it points to).
2. **Technology- and layout-neutral checklist steps.** (user, 2026-11-03)
   - **Step 0 (Shared checkout check):** Checks current branch (`git -C <main-checkout> branch --show-current`) and `git -C <main-checkout> status --short`, plus any branch-lock file or branch guard declared by the host's doctrine; never silences checkout output or bypasses a host branch guard.
   - **Step 1 (Read-only squash-aware merge & post-merge CI verification):** Verifies content presence on the remote default branch (`origin/main` or the repository's default branch via `git show` / `git grep`, never by SHA ancestry or `git diff main <branch>`), and when the repository uses GitHub Actions / CI workflows (`gh run list`), verifies the post-merge run on the default branch did not fail.
   - **Step 2.5 (Worktree process & resource sweep before `git worktree remove`):** Replaces the HM-specific `run_cms_e2e.py` / `Name LIKE 'python%'` / `/api/tuner/content-items` probe with a stack-neutral procedure: (a) check for lingering processes whose command line or working directory references `<worktree-path>` (PowerShell `Get-CimInstance Win32_Process` on Windows; `pgrep -af` / `/proc/<pid>/cwd` on POSIX), and (b) if the host's doctrine names a background test server, simulator, or container spawned from worktrees, run its functional readiness probe (verifying a real data/content operation, never an in-memory `/health` flag that survives after its worktree files are deleted).
   - **Step 5 (Out-of-branch tracking-doc reconciliation):** Uses `git grep -il "<changed-surface-keyword>" -- '*.md'` across tracked Markdown files rather than hardcoding `docs/architecture docs/reviews docs/design` (so hosts that store docs under `SpecificationDocumentation/` or root `ROADMAP.md` are covered without configuration).
   - **Steps 6 & 6.5 (Review-round sweep, spec filing-claims audit, ADR ledger amendment, and live guard-escape check):** Files deferred items and live guard escapes into the durable tracking document or issue tracker named by the host's doctrine (without prescribing HM's `Priority board` `Now`/`Next`/`Parked` or `S`/`L`/`D`/`A` columns in the plugin prompt), and runs the `acf.adr` ledger amendment whenever the merged work had an ADR-reviewed spec and `config/architecture/adr.yml` is present.
3. **Row-identity rule for `LedgerAmendment` after a verification pass or user override.**
   - A controller verification pass (`plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:443-453`) or user override writes no `LedgerRow`; only a full 4-reviewer dispatch writes a `LedgerRow`.
   - Therefore, when `post-merge-housekeeping` Step 6 constructs `LedgerAmendment(spec_path=..., commit_sha=..., date=..., absorbed=..., rejected=..., blocks_overturned=..., escapes=...)`, `commit_sha` MUST be the `commit_sha` of the **last `LedgerRow` in `repo / cfg.ledger_path` for that `spec_path`**, never the verification-pass or user-override commit SHA from the spec's `**Adversarial review:**` header when those differ.
4. **Plugin-only change Surface in Slice 1.**
   - Per `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:55-57` (Decision 1: *"A spec lives in the repository whose files its change surface names. A mixed spec splits along that line"*), this spec modifies only `arch-compliance-for-superpowers`. Deleting `hm:.claude/skills/post-merge-housekeeping/`, updating `hm:GEMINI.md:61`, and updating HM Workstream E exit criterion 6 belong to the HM cutover slice (Slice 3).

---

## 3. Non-goals

- **No changes to `LedgerRow` or `LedgerAmendment` schemas** (`plugins/arch-compliance/python/acf/adr/ledger.py:67-172`; governed by `## Frozen ledger format` at `config/architecture/ARCHITECTURE.md:143-149`).
- **No changes to Python runtime modules under `plugins/arch-compliance/python/acf/` or hooks under `plugins/arch-compliance/hooks/`.** The existing `acf.repo` and `acf.adr` exports already provide every function `post-merge-housekeeping` calls.
- **No `architecture-review` or detector-extension changes.** Those belong to Slice 2 (`Workstream E Phase 2`).
- **No changes to `HistoricMansions` or `Cayenne` in this slice.**

---

## 4. Census of Origin-Host & Stack-Specific Lines in `hm:.claude/skills/post-merge-housekeeping/SKILL.md`

### 4.1 Census recipes

Run against `hm:.claude/skills/post-merge-housekeeping/SKILL.md` (349 lines at `hm` commit `b652fab05`):

```bash
# Recipe A — origin-host path roots, doctrine names, and provenance pointers
grep -nE "GEMINI|CLAUDE\.md|docs/design|docs/reviews|docs/architecture|scripts\.core|scripts/|SKILL_PROVENANCE|§[0-9]|HistoricMansions|book root|index\.yml|LEDGER_PATH|RUNS_DIR" \
  hm:.claude/skills/post-merge-housekeeping/SKILL.md

# Recipe B — origin-host operational/stack vocabulary (branch lock, e2e script, tuner API, priority board)
grep -nE "\.cursor|\.claude/|book_root|run_cms_e2e|expected_branch|CMS_SKIP_BRANCH_GUARD|tuner|Priority board|Guardrail gaps|ARCHITECTURE_REVIEW_2026|playwright\.config|temp_e2e_root|sandbox:true" \
  hm:.claude/skills/post-merge-housekeeping/SKILL.md
```

### 4.2 Line-by-line disposition

Every line selected by Recipe A (7 lines: `:14, :113, :124, :159, :214, :278, :326`) or Recipe B (15 additional lines: `:59, :64, :125, :126, :134, :141, :144, :155, :158, :161, :169, :286, :325, :334, :347`) is dispositioned below:

| `hm:.claude/skills/post-merge-housekeeping/SKILL.md` lines | What they carry | Plugin disposition in `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` |
|---|---|---|
| `:14, :113` | Pointers to `docs/architecture/SKILL_PROVENANCE.md` | Removed (matching `docs/design/ADR_GATE_HOST_CONTRACT.md:205`); the 2026-10-28 timestamp-vs-`headRefOid` rationale at `:110-113` stays inline without the external file pointer |
| `:59, :64, :325, :347` | `.claude/expected_branch.txt` and `CMS_SKIP_BRANCH_GUARD=1` | Generalized to: check `git -C <main-checkout> branch --show-current` and `git -C <main-checkout> status --short`, plus any shared-checkout branch lock or branch-guard hook declared by the host's doctrine; never bypass a host branch guard or rewrite another session's lock file |
| `:124-126, :134, :141, :144, :155, :158-159, :161, :326, :334` | `run_cms_e2e.py`, `Name LIKE 'python%'`, `/api/health` (`sandbox:true`), `/api/tuner/content-items`, `temp_e2e_root_<port>/`, `playwright.config.js`, `CMS_E2E_BASE_URL`, "book root" | Generalized to **Step 2.5 Worktree process & resource sweep**: before `git worktree remove <worktree-path>`, check for processes whose command line or working directory references `<worktree-path>` (PowerShell `Get-CimInstance Win32_Process` on Windows; `pgrep -af` / `readlink /proc/<pid>/cwd` on POSIX), and if the host's doctrine declares a worktree-spawned test server/daemon, probe a functional data endpoint rather than an in-memory `/health` flag whose backing files were deleted with a worktree |
| `:169` | `git worktree remove .claude/worktrees/<slug>` | `git worktree remove <worktree-path>` |
| `:214` | `rg -il "<changed-surface-keyword>" docs/architecture docs/reviews docs/design` | `git grep -il "<changed-surface-keyword>" -- '*.md'` across tracked Markdown files (plus any non-Markdown tracking files named by host doctrine) |
| `:242-256` | Prose inline call to `acf.adr.append_amendment` without a fenced ```` ```python ```` block and without the verification-pass / user-override `commit_sha` lookup rule | Replaced by a fenced ```` ```python ```` block (parsed by `ast.parse` in `test_adr_skill_prose.py`) that checks `(repo / ADR_REL).is_file()`, loads `cfg = load_host_config(repo)`, resolves `commit_sha` from the last `LedgerRow` (`"outcome" in r`) for `spec_path` in `repo / cfg.ledger_path` (the row-identity rule of §5.2), and calls `append_amendment(LedgerAmendment(...), repo / cfg.ledger_path)` |
| `:278, :286` (and surrounding `:276-290`) | [`docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md`], **Guardrail gaps** table, and **Priority board** (`Now`, `Next`, `Parked`, impact classes `S`, `L`, `D`, `A`) | Generalized to: record the live guard-escape search (and any live instance found) and file deferred items in the canonical roadmap, remediation ledger, or issue tracker named by the host's doctrine |

---

## 5. Design

### 5.1 `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md`

The skill file has YAML frontmatter (`name: post-merge-housekeeping`, `description: ...`) and no backslashes (`\` is forbidden across skill prose by `plugins/arch-compliance/tests/test_adr_skill_invariants.py:70-73`). Its checklist steps are:

- **Step 0 — Shared checkout check before mutation:**
  - Steps 1–2 are strictly read-only. Before moving HEAD or committing on the main checkout (Step 3.5), inspect `git -C <main-checkout> branch --show-current`, `git -C <main-checkout> status --short`, and any branch-lock file declared by the host's doctrine (`config/architecture/ARCHITECTURE.md` and documents it points to). If another workstream holds the checkout or uncommitted changes exist, stop and ask the user. Never silence `git checkout` / `git pull` with `-q`.
- **Step 1 — Verify content landed & post-merge CI (read-only, squash-aware):**
  - Run `git fetch origin`, inspect PR merge metadata (`gh pr view <N> --json mergedAt,mergeCommit,headRefOid`, or `git log --format='%H %cI %s' -1 --grep='(#<N>)' origin/main` when `gh` is absent), and verify by **content presence** on the remote default branch (`git show origin/main:<path>` or `git grep '<symbol>' origin/main -- <path>`), never by SHA ancestry or `git diff main <branch>`.
  - When the repository runs CI workflows on push to the default branch and `gh` is available, check `gh run list --branch main --limit 5` (or the repository's default branch) to confirm the post-merge CI / deploy run succeeded.
- **Step 2 — Stranded-commit check (`headRefOid..<branch>`):**
  - Compare `git log --format='%h %cI %s' "$head"..<branch>` against the merged `headRefOid` (never against `mergedAt` timestamps). When `gh` is absent or there is no PR, treat every `origin/main..<branch>` commit as stranded until its whole diff is verified on `origin/main`.
- **Step 2.5 — Worktree process & resource sweep (before `git worktree remove`):**
  - Before removing `<worktree-path>`, check for any lingering process whose command line or working directory references `<worktree-path>` (Windows PowerShell `Get-CimInstance Win32_Process` filtering `CommandLine` by the worktree slug/path; POSIX `pgrep -af '<worktree-slug>'` and `/proc/<pid>/cwd`).
  - If the host's doctrine declares a background test server, simulator, or container spawned from worktrees, run its declared probe against a real functional/data endpoint (never trusting an in-memory `/health` flag whose backing files were deleted when a worktree was removed). Terminate only confirmed orphan/zombie processes, re-verify the PID is gone, and report the sweep outcome in Step 8.
- **Step 3 — Teardown:**
  - `git ls-remote --heads origin <branch>`, `git push origin --delete <branch>` (if still present after Step 2 is clear), `git worktree remove <worktree-path>` (from the main checkout), `git branch -D <branch>` (only after Steps 1–2 pass), `git fetch --prune origin` (mandatory so local `remotes/origin/<branch>` refs do not linger), `git worktree prune && git worktree list`, `git branch -a`.
- **Step 3.5 — Take the checkout:**
  - Re-verify Step 0, then `git -C <main-checkout> checkout main && git -C <main-checkout> pull --ff-only`.
- **Step 4 — Plan truthfulness:**
  - If the branch executed a tracked implementation plan, tick completed steps `[x]`, annotate the merge (PR #, squash SHA, date), and remove or update any plan code blocks that review rounds superseded.
- **Step 5 — Out-of-branch tracking-doc reconciliation:**
  - Run `git grep -il "<changed-surface-keyword>" -- '*.md'` across tracked Markdown files to find roadmaps, status tables, and architecture docs outside the branch's diff that still describe pre-merge state, and update them with dates.
- **Step 6 — Review-round sweep, spec filing-claims audit, & ADR ledger amendment:**
  - Sweep PR review comments and in-session subagent review reports for any item tagged "follow-up", "out of scope", "pre-existing", or "not a blocker", and file each one in the durable tracking document or issue tracker named by the host's doctrine.
  - If the branch shipped or implemented a spec, grep the spec for "filed", "recorded in", "to be written", and "follow-up" claims and verify each named target exists and carries the promised entry.
  - Classify any review follow-up or escaped defect by spec-stage lens (`refuter`, `compliance`, `sweeper`, `hardening`, or `none`) in the tracking doc entry, and when the merged work had an ADR-reviewed spec and `(repo / ADR_REL).is_file()` is true, append a `LedgerAmendment` (§5.2).
- **Step 6.5 — Live guard-escape check (when the slice shipped a guard or retired a defect class):**
  - Ask: *"What ALREADY gets through the guard we just shipped? Name one live instance — file and line — or state, after actually searching, that you found none."* Record the search command and file any live escape in the host's tracking document.
- **Step 7 — Memory / status notes** and **Step 8 — Report before moving on**.

### 5.2 Step 6's `acf.adr` Python snippet and the row-identity rule

When the merged work had a spec-stage review under `/adversarial-design-review` and the host declares `config/architecture/adr.yml`, Step 6 runs the following fenced ```` ```python ```` block from the repository root:

```python
import datetime
import json
from acf.adr import LedgerAmendment, append_amendment, load_host_config
from acf.repo import ADR_REL, resolve_repo

repo = resolve_repo(None)
if (repo / ADR_REL).is_file():
    cfg = load_host_config(repo)
    ledger_file = repo / cfg.ledger_path
    spec_path = "docs/SPEC.md"
    rows = [
        json.loads(line)
        for line in ledger_file.read_text(encoding="utf-8").splitlines()
        if line.startswith("{")
    ]
    dispatch_rows = [
        r for r in rows if r.get("spec_path") == spec_path and "outcome" in r
    ]
    assert dispatch_rows, f"no LedgerRow found for {spec_path}"
    last_dispatch_sha = dispatch_rows[-1]["commit_sha"]
    amendment = LedgerAmendment(
        spec_path=spec_path,
        commit_sha=last_dispatch_sha,
        date=datetime.date.today().isoformat(),
        absorbed=0,
        rejected=0,
        blocks_overturned=0,
        escapes=0,
    )
    append_amendment(amendment, ledger_file)
```

**Why `last_dispatch_sha` is resolved from `dispatch_rows[-1]["commit_sha"]` (`"outcome" in r`):**
A controller verification pass (`plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:443-453`) or a user override after a blocked full run updates the spec's `**Adversarial review:**` header to the verification-pass or override commit SHA, but writes **no** `LedgerRow`. `LedgerAmendment` matches the prior `LedgerRow` by `(spec_path, commit_sha)` (`plugins/arch-compliance/python/acf/adr/ledger.py:139-140`, `plugins/arch-compliance/python/acf/adr/rollup.py:67-86`). Reading the last record for `spec_path` that carries `"outcome"` (which only `LedgerRow` has; `LedgerAmendment` has no `outcome` field at `plugins/arch-compliance/python/acf/adr/ledger.py:155-166`) guarantees the amendment binds to the last full dispatch's `LedgerRow` whether the spec cleared on a full dispatch, a verification pass, or a user override.

Note also:
- Every path constant comes from `acf.repo` (`ADR_REL`, `resolve_repo`), honoring `## One owner for host paths` (`config/architecture/ARCHITECTURE.md:105-116`).
- `ledger_file.read_text(encoding="utf-8")` explicitly declares `encoding="utf-8"`, honoring `## Declared text decoding` (`config/architecture/ARCHITECTURE.md:169-180`).
- No backslash appears anywhere in the snippet or skill file, honoring `test_no_skill_file_contains_a_backslash` (`plugins/arch-compliance/tests/test_adr_skill_invariants.py:70-73`).

### 5.3 Cross-skill handoffs, doctrine, registry, version bump, and installed-skills check

1. **Cross-skill handoffs restored:**
   - `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:363`: `"amended later by the host's post-merge process"` $\rightarrow$ `"amended later by post-merge-housekeeping"`.
   - `plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:223`: `"After merge, the host's post-merge process owns"` $\rightarrow$ `"After merge, post-merge-housekeeping owns"`.
2. **Installed-skills byte check (`scripts/check_installed_skills.py`):**
   - `GATE_SKILLS` at `scripts/check_installed_skills.py:18` gains `"post-merge-housekeeping"`:
     `GATE_SKILLS = ("adversarial-design-review", "responding-to-adversarial-review", "post-merge-housekeeping")`.
   - `tests/test_check_installed_skills.py:22-28` imports `GATE_SKILLS` from `scripts/check_installed_skills.py` (`docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:504`), so its three tests automatically cover all three skills; `_skill_tree` in `tests/test_check_installed_skills.py:22-28` is updated so skills without a `reviewers/` subdirectory (`responding-to-adversarial-review`, `post-merge-housekeeping`) still test `SKILL.md` byte comparison and missing-file detection cleanly.
3. **Doctrine and mandate registry (`config/architecture/ARCHITECTURE.md` & `config/architecture/mandates.yml`):**
   - `config/architecture/ARCHITECTURE.md:140-141` (`## Prose names no host`): update the description of `plugin.gate-prose-names-no-host` from `"the two gate skills' prose; the other three skills in plugins/arch-compliance/skills/ have no row yet"` to `"the two gate skills' and post-merge-housekeeping's prose; the other three skills in plugins/arch-compliance/skills/ have no row yet"`.
   - `config/architecture/ARCHITECTURE.md:186-189` (`## Release discipline`): update `"the two gate skills"` / `"those two skill trees"` to `"the two gate skills and post-merge-housekeeping"` / `"those three skill trees"`.
   - `config/architecture/mandates.yml:193`: update `title` of `plugin.gate-prose-names-no-host` to `"The gate and housekeeping skills' prose names no origin host"`.
4. **Version bump (`## Release discipline`, `config/architecture/ARCHITECTURE.md:184-185`):**
   - Bump `version` from `"0.2.1"` to `"0.2.2"` in `plugins/arch-compliance/.claude-plugin/plugin.json:3` and `pyproject.toml:3`.
5. **User-facing skill tables (`README.md` & `docs/guides/SUPERPOWERS_COMPLEMENT.md`):**
   - Add `/post-merge-housekeeping` to the Skills table in `README.md:28-35` and add `/adversarial-design-review`, `/responding-to-adversarial-review`, and `/post-merge-housekeeping` to the Skills table in `docs/guides/SUPERPOWERS_COMPLEMENT.md:38-43`.

### 5.4 Test suite extensions (`test_adr_skill_prose.py` & `test_adr_skill_invariants.py`)

1. **`plugins/arch-compliance/tests/test_adr_skill_prose.py`:**
   - Add `HOUSEKEEPING = SKILLS / "post-merge-housekeeping"` and append `HOUSEKEEPING / "SKILL.md"` to `FILES` (`:12-17`, now 8 files).
   - Extend `FORBIDDEN` (`:18-19`) with origin-host housekeeping literals: `"run_cms_e2e"`, `"expected_branch.txt"`, `"CMS_SKIP_BRANCH_GUARD"`, `"ARCHITECTURE_REVIEW_2026"`.
   - Include `HOUSEKEEPING / "SKILL.md"` in `_python_bodies()` (`:24`) so its fenced ```` ```python ```` block is parsed with `ast.parse` and every `from acf... import ...` symbol is verified to exist in the package (`test_every_python_body_parses_and_its_acf_imports_exist`, `:44-54`).
2. **`plugins/arch-compliance/tests/test_adr_skill_invariants.py`:**
   - Add `HOUSEKEEPING = SKILLS / "post-merge-housekeeping"`.
   - Include `HOUSEKEEPING` in `test_both_skills_have_frontmatter_with_a_name_and_description` (`:41-47`) and `test_no_skill_file_contains_a_backslash` (`:70-73`).
   - Add `test_housekeeping_skill_invariants()` asserting that `post-merge-housekeeping/SKILL.md`:
     - imports `LedgerAmendment`, `append_amendment`, and `load_host_config` in a real `from acf.adr import` line and `ADR_REL`, `resolve_repo` in a real `from acf.repo import` line;
     - states the verification-pass / user-override row-identity rule (`"outcome" in r` / `last_dispatch_sha`);
     - preserves the core post-merge safety checks (`headRefOid`, `git fetch --prune`, `What ALREADY gets through the guard we just shipped?`);
     - is named by both `adversarial-design-review/SKILL.md` and `responding-to-adversarial-review/SKILL.md`.

---

## 6. Shape fit

### What existing shape does this extend?

| Element | Existing shape extended |Relationship |
|---|---|---|
| `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` | `plugins/arch-compliance/skills/adversarial-design-review/` and `plugins/arch-compliance/skills/responding-to-adversarial-review/`, ported from HM in phase 1c (`docs/design/ADR_GATE_HOST_CONTRACT.md` §5.4) | `ADJACENT` — third portable governance skill in `plugins/arch-compliance/skills/`; shares the same `acf.repo` + `acf.adr` host contract |
| Step 6 `LedgerAmendment` snippet in `post-merge-housekeeping/SKILL.md` | `acf.adr.LedgerAmendment`, `acf.adr.append_amendment` (`plugins/arch-compliance/python/acf/adr/ledger.py:132-172, 231-237`), `acf.adr.load_host_config` (`plugins/arch-compliance/python/acf/adr/host.py:28-33`), `acf.repo.ADR_REL`, `acf.repo.resolve_repo` (`plugins/arch-compliance/python/acf/repo.py:21, 32-44`) | Live skill consumer of `LedgerAmendment` and `append_amendment` (`## Live consumers`, `config/architecture/ARCHITECTURE.md:151-155`) |
| `HOUSEKEEPING` in `plugins/arch-compliance/tests/test_adr_skill_prose.py` | `FILES`, `FORBIDDEN`, and `_python_bodies()` in `plugins/arch-compliance/tests/test_adr_skill_prose.py:12-28` | Extends the existing prose-portability and AST-import test module (`plugin.gate-prose-names-no-host`) rather than creating a second prose scanner |
| `HOUSEKEEPING` in `plugins/arch-compliance/tests/test_adr_skill_invariants.py` | Frontmatter, no-backslash, and import-pin tests in `plugins/arch-compliance/tests/test_adr_skill_invariants.py:41-99` | Extends the existing skill-invariants test module |
| `"post-merge-housekeeping"` in `scripts/check_installed_skills.py:18` | `GATE_SKILLS` in `scripts/check_installed_skills.py:18`, consumed by `tests/test_check_installed_skills.py:23` | Single definition of `GATE_SKILLS` (`## Single point of definition`) |

### What second way to do something does it create?

None in this repository. Across repositories, `hm:.claude/skills/post-merge-housekeeping/SKILL.md` and `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` coexist temporarily until Slice 3 (HM cutover) deletes HM's local copy, identical to the phase 1c $\rightarrow$ 1d transition for `adversarial-design-review` and `responding-to-adversarial-review` (`docs/design/ADR_GATE_HOST_CONTRACT.md:425`).

### Pattern sweep

The defect class this design retires in `post-merge-housekeeping` is *origin-host paths, doctrine names, and stack-specific assumptions embedded in portable skill prose*. Swept across `hm:.claude/skills/post-merge-housekeeping/SKILL.md` by §4.1 Recipes A and B (22 lines across 7 groups, all dispositioned in §4.2) and guarded by `plugins/arch-compliance/tests/test_adr_skill_prose.py` and `plugins/arch-compliance/tests/test_adr_skill_invariants.py`.

---

## 7. Definition of done

1. `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` exists and passes all checks in `plugins/arch-compliance/tests/test_adr_skill_prose.py` and `plugins/arch-compliance/tests/test_adr_skill_invariants.py`.
2. Planting any `FORBIDDEN` literal (`"GEMINI"`, `"CLAUDE.md"`, `"SKILL_PROVENANCE"`, `"scripts.core"`, `"docs/design"`, `"docs/reviews"`, `"docs/architecture"`, `".cursor"`, `"run_cms_e2e"`, `"expected_branch.txt"`, `"CMS_SKIP_BRANCH_GUARD"`, `"ARCHITECTURE_REVIEW_2026"`) or a backslash (`\`) in `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` fails `pytest`, and restoring passes. (Note: in the Step 6 Python snippet, the placeholder spec path uses `"docs/SPEC.md"` so `"docs/design"` never appears in the skill prose.)
3. `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:363` and `plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:223` name `post-merge-housekeeping` directly.
4. `scripts/check_installed_skills.py:18` includes `"post-merge-housekeeping"` in `GATE_SKILLS`, and `tests/test_check_installed_skills.py` passes.
5. `plugins/arch-compliance/.claude-plugin/plugin.json` and `pyproject.toml` versions are bumped to `"0.2.2"`.
6. `python -m pytest -q` and `python -m acf.cli_check_diff --repo . --base main` pass with zero BLOCK findings.
7. `npm test --prefix plugins/arch-compliance/detectors/typescript` prints `self-test OK`.
8. This spec clears `/adversarial-design-review`, with its run detail under `docs/reviews/adr_runs/` and its `LedgerRow` in `docs/reviews/adversarial_design_ledger.jsonl` committed on the branch.

---

## 8. Risks

| Risk | Mitigation |
|---|---|
| The Step 6 Python snippet's example `spec_path` triggers `FORBIDDEN` in `test_adr_skill_prose.py` if spelled `"docs/design/..."` | Use `"docs/SPEC.md"` as the example string in `post-merge-housekeeping/SKILL.md` (matching `docs/SOME_DOC.md` in `docs/design/ADR_GATE_HOST_CONTRACT.md:207` and DoD item 2) |
| A host without `config/architecture/adr.yml` runs `post-merge-housekeeping` on a bounded PR and hits `AcfInputError` in Step 6 | Step 6 gates `load_host_config(repo)` on `(repo / ADR_REL).is_file()` and on the merged branch having an ADR-reviewed spec (§5.2) |
| Installed skill copies drift from the repository clone after editing three skills | Bump version to `0.2.2`, sync installed skills, and verify with `python scripts/check_installed_skills.py <INSTALL_PATH>` |

---

## Appendix — premise verification (authoring time, 2026-11-03)

| Premise | Command | Observed output |
|---|---|---|
| Recipe A & B hits in `hm:.claude/skills/post-merge-housekeeping/SKILL.md` | Run §4.1 Recipe A and Recipe B against `hm:.claude/skills/post-merge-housekeeping/SKILL.md` at `b652fab05` | Recipe A: 7 lines (`:14, :113, :124, :159, :214, :278, :326`); Recipe B (excluding A): 15 lines (`:59, :64, :125, :126, :134, :141, :144, :155, :158, :161, :169, :286, :325, :334, :347`) |
| Both gate skills currently say `"the host's post-merge process"` | `git grep -n "post-merge process" -- plugins/arch-compliance/skills/` | `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:363` and `plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:223` |
| `LedgerAmendment` has no `outcome` field while `LedgerRow` requires `outcome` | Inspect `plugins/arch-compliance/python/acf/adr/ledger.py:67-172` | `LedgerRow` defines `outcome: Literal["BLOCKED", "CLEARED_WITH_ABSORPTIONS", "CLEARED"]` (`:96`); `LedgerAmendment` defines only `spec_path`, `commit_sha`, `date`, `absorbed`, `rejected`, `blocks_overturned`, `escapes` (`:157-166`) |
| `GATE_SKILLS` in `scripts/check_installed_skills.py` has 2 skills at `5623832` | `sed -n 18p scripts/check_installed_skills.py` | `GATE_SKILLS = ("adversarial-design-review", "responding-to-adversarial-review")` |
| Current plugin version is `0.2.1` | Inspect `pyproject.toml:3` and `plugins/arch-compliance/.claude-plugin/plugin.json:3` | Both carry `"0.2.1"` |
