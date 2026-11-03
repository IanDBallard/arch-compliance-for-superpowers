# Portable `post-merge-housekeeping` Skill in `arch-compliance`

**Status:** v1 — draft for adversarial design review (`writing-plans` blocked until CLEARED).
**Adversarial review:** pending
**Spec kinds:** `feature`
**Repo:** `IanDBallard/arch-compliance-for-superpowers`, `main` at `2929331`; implemented on branch `feat/post-merge-housekeeping`.
**Workstream:** HistoricMansions Workstream E (portable governance skills), discharging `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:563-565` follow-up 2 (plugin side).
**Governing mandates:** `config/architecture/ARCHITECTURE.md` sections `## Fail loud` (`:24-41`), `## No shims` (`:43-53`), `## POSIX paths` (`:55-64`), `## One base exception` (`:99-103`), `## One owner for host paths` (`:105-116`), `## Declared, never defaulted` (`:118-133`), `## Prose names no host` (`:135-141`), `## Frozen ledger format` (`:143-149`), `## Live consumers` (`:151-155`), `## No completeness claims` (`:157-167`), `## Declared text decoding` (`:169-180`), `## Release discipline` (`:182-191`), `## Single point of definition` (`:193-206`), `## Scoped refactor` (`:208-212`), and the five portable governing principles at `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-51`.
**No state-machine surface.** This design adds or modifies no state machine and no transition.

---

## 0. Citation convention

Unprefixed paths refer to this repository (`IanDBallard/arch-compliance-for-superpowers`) at `main` (`2929331`, which merges `origin/main` `1aac816` with `feat/self-host` `731095f`, `feat/executed-census-response` `80b80f1`, and `feat/judge-provider-neutral` `5623832`). Paths prefixed `hm:` refer to the sibling repository `HistoricMansions` at `b652fab05` (`main`), following the precedent established in `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:10-32`. Every path is written in full with POSIX slashes and without `...` ellipses.

---

## 1. Goal

Extract and generalize the `post-merge-housekeeping` skill from `hm:.claude/skills/post-merge-housekeeping/SKILL.md` into `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` so that any repository using Superpowers and `arch-compliance` — regardless of its constituent technology stack (Python, TypeScript/React, C/C++ firmware, Flutter/Dart, Go, Rust), git default branch name, or directory layout — runs one canonical post-merge ritual from the plugin.

Moving `post-merge-housekeeping` into the plugin closes three gaps recorded in prior specs:

1. **Cross-skill handoff completion:** In `docs/design/ADR_GATE_HOST_CONTRACT.md:172-174, 213`, `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:363` and `plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:223` had to replace `post-merge-housekeeping` with `"by the host's post-merge process"` solely because `post-merge-housekeeping` was still HM-local. With `post-merge-housekeeping` in `plugins/arch-compliance/skills/`, both gate skills name `post-merge-housekeeping` directly again.
2. **Ledger-amendment row-identity rule after a verification pass or user override:** `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:563-565` scheduled the `post-merge-housekeeping` spec to add the row-identity rule for `LedgerAmendment` when a spec cleared via a controller verification pass or user override (`plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:437-453`), because neither writes a new `LedgerRow` and the spec header's `(repo @ <sha>)` differs from the last full dispatch's `LedgerRow.commit_sha`.
3. **Origin-host vocabulary, AST, and byte-check coverage:** `plugins/arch-compliance/tests/test_adr_skill_prose.py`, `plugins/arch-compliance/tests/test_adr_skill_invariants.py`, and `scripts/check_installed_skills.py` are extended so `post-merge-housekeeping/SKILL.md` is held to the same `FORBIDDEN` origin-host vocabulary check, AST-valid Python snippet check, POSIX-slash check, and installed-copy byte-identity check as `adversarial-design-review` and `responding-to-adversarial-review`.

---

## 2. Decisions this design records

1. **Doctrine-driven host conventions under a canonical `## Post-merge` heading + existing `config/architecture/adr.yml`; no new YAML configuration file.** (user, 2026-11-03)
   - `post-merge-housekeeping` introduces no `config/architecture/housekeeping.yml` and no new Pydantic config loader.
   - Its only Python package inputs are the existing `acf.repo` constants (`ADR_REL`, `ARCH_REL`, `resolve_repo` at `plugins/arch-compliance/python/acf/repo.py:18-44`) and `acf.adr` (`load_host_config`, `LedgerAmendment`, `append_amendment` at `plugins/arch-compliance/python/acf/adr/host.py:28-33` and `plugins/arch-compliance/python/acf/adr/ledger.py:132-172, 231-237`).
   - Host-specific operational conventions are read from a named `## Post-merge` section in the host's doctrine (`config/architecture/ARCHITECTURE.md` or a document it points to):
     1. **Shared-checkout branch lock** (lock file path and branch-guard hook/env var, if the host shares a checkout across sessions).
     2. **Worktree daemon probe** (process filter and functional readiness endpoint/command, if tests spawn background servers/simulators from worktrees).
     3. **Post-merge CI / deploy workflows** (workflow names or commands to check on the default branch after merge).
     4. **Durable tracking target** (the roadmap, remediation ledger, or issue tracker where deferred review items and guard escapes are filed).
   - **No silent skipping when `## Post-merge` omits a check (`## Declared, never defaulted`):** If the host doctrine has no `## Post-merge` section or does not declare one of (1)–(3), the Step 8 summary must explicitly report `<check>: not declared in ## Post-merge, skipped` rather than omitting it silently. If (4) is not declared and review follow-ups or guard escapes exist, Step 6 stops and asks the user where to file them rather than dropping them in chat.
2. **Technology-, forge-, and layout-neutral checklist steps.** (user, 2026-11-03)
   - **Read-only default branch resolution (Step 1):** Resolves the remote default branch once via `default_branch=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')`, with a purely read-only fallback `git ls-remote --symref origin HEAD | awk '/^ref:/ {sub("refs/heads/", "", $2); print $2}'` when `refs/remotes/origin/HEAD` is unset locally (never writing a ref in Step 1 and never guessing `main`), then uses `$default_branch` / `origin/$default_branch` across Steps 1, 2, 3, and 3.5.
   - **Step 0 (Shared checkout & installed-skill check):** Before mutating the main checkout (Step 3.5), checks `git -C <main-checkout> branch --show-current`, `git -C <main-checkout> status --short`, and any branch-lock file declared under `## Post-merge`. Never silences `git checkout` / `git pull` with `-q` and never bypasses a host branch guard.
   - **Step 1 (Read-only squash-aware merge & post-merge CI verification):** Verifies content presence on `origin/$default_branch` (`git show "origin/$default_branch:<path>"` or `git grep '<symbol>' "origin/$default_branch" -- <path>`, never by SHA ancestry or `git diff "$default_branch" <branch>`), and checks post-merge CI (`gh run list --branch "$default_branch" --limit 5` or the workflow check declared under `## Post-merge`).
   - **Step 2.5 (Worktree process & resource sweep before `git worktree remove`):** Replaces the HM-specific `run_cms_e2e.py` / `Name LIKE 'python%'` / `/api/tuner/content-items` probe with a stack-neutral procedure: (a) check for lingering processes whose command line or working directory references `<worktree-path>` (PowerShell `Get-CimInstance Win32_Process` on Windows; `pgrep -af` / `readlink /proc/<pid>/cwd` on POSIX), and (b) if `## Post-merge` declares a worktree daemon probe, run that probe against its declared functional data endpoint (never trusting an in-memory `/health` flag whose backing files were deleted with a worktree).
   - **Step 5 (Out-of-branch tracking-doc reconciliation):** Uses `git grep -il "<changed-surface-keyword>" -- '*.md'` across tracked Markdown files rather than hardcoding `docs/architecture docs/reviews docs/design` (so hosts that store docs under `SpecificationDocumentation/` or root `ROADMAP.md` are covered without configuration).
   - **Steps 6 & 6.5 (Review-round sweep, spec filing-claims audit, ADR ledger amendment, and live guard-escape check):** Includes an explicit non-`gh` fallback in Step 6 (when `gh` is unavailable or the host does not use GitHub PRs, sweep in-session subagent review reports and branch commit messages, and ask the user for any external PR/MR review comments rather than skipping). Files deferred items and live guard escapes into the tracking target declared under `## Post-merge` (without prescribing HM's `Priority board` `Now`/`Next`/`Parked` or `S`/`L`/`D`/`A` columns in the plugin prompt), and runs the `acf.adr` ledger amendment whenever the merged work had an ADR-reviewed spec and `(repo / ADR_REL).is_file()` is true.
3. **Single-source row-identity rule for `LedgerAmendment` after a verification pass or user override.**
   - A controller verification pass (`plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:443-453`) or user override writes no `LedgerRow`; only a full 4-reviewer dispatch writes a `LedgerRow` and a run-detail file (`plugins/arch-compliance/python/acf/adr/run_detail.py:47`, `{stem}_v{version}_{date}.md`).
   - Furthermore, as `plugins/arch-compliance/python/acf/adr/ledger.py:146-149` states, *"Nothing reads this file back to find the row being amended (no read-back exists here or anywhere in the pipeline); the amender is expected to already know which spec+commit it is amending."*
   - Note that `repo / cfg.runs_dir` also holds author response records named `<STEM>_v<N>_response_<date>.md` (`plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:110`), which have no `Spec: ... @ ...` line, and lexicographic sorting fails once `<N>` reaches `10` (`v10` sorts before `v9`).
   - Therefore, Step 6 defines **one** rule (`## Single point of definition`) to obtain `dispatch_commit_sha` for `spec_path` (with `<STEM> = Path(spec_path).stem`): among files in `repo / cfg.runs_dir` matching `^<STEM>_v([0-9]+)_([0-9]{4}-[0-9]{2}-[0-9]{2})\.md$` (which matches `run_detail_path`'s `{stem}_v{version}_{date}.md` format at `plugins/arch-compliance/python/acf/adr/run_detail.py:47` and excludes every `_response_` file), pick the file with the **highest integer `int(version)`** and read `<commit_sha>` from its line 3 (`Spec: \`<spec_path>\` @ \`<commit_sha>\``, produced by `plugins/arch-compliance/python/acf/adr/run_detail.py:84`). Do not read `commit_sha` from the spec's `**Adversarial review:**` header and do not parse the ledger file inline.
4. **Plugin-only change surface in Slice 1.**
   - Per `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:55-57` (Decision 1: *"A spec lives in the repository whose files its change surface names. A mixed spec splits along that line"*), this spec modifies only `arch-compliance-for-superpowers`. Deleting `hm:.claude/skills/post-merge-housekeeping/`, updating `hm:GEMINI.md:61`, and updating HM Workstream E exit criterion 6 belong to the HM cutover slice (Slice 3).

---

## 3. Non-goals

- **No changes to `LedgerRow` or `LedgerAmendment` schemas** (`plugins/arch-compliance/python/acf/adr/ledger.py:67-172`; governed by `## Frozen ledger format` at `config/architecture/ARCHITECTURE.md:143-149`).
- **No changes to Python runtime modules under `plugins/arch-compliance/python/acf/` or hooks under `plugins/arch-compliance/hooks/`.** The existing `acf.repo` and `acf.adr` exports already provide every function `post-merge-housekeeping` calls, and reading `dispatch_commit_sha` from line 3 of the highest-versioned `{stem}_v{version}_{date}.md` run-detail file (`plugins/arch-compliance/python/acf/adr/run_detail.py:47, 84`) avoids any need for a ledger reader in skill prose or runtime code.
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
grep -nE "\.cursor|\.claude/|book_root|run_cms_e2e|expected_branch|CMS_SKIP_BRANCH_GUARD|tuner|Priority board|or Parked|Guardrail gaps|ARCHITECTURE_REVIEW_2026|playwright\.config|temp_e2e_root|sandbox:true" \
  hm:.claude/skills/post-merge-housekeeping/SKILL.md
```

### 4.2 Line-by-line disposition

Every line selected by Recipe A (7 lines: `:14, :113, :124, :159, :214, :278, :326`) or Recipe B (16 additional lines: `:59, :64, :125, :126, :134, :141, :144, :155, :158, :161, :169, :286, :287, :325, :334, :347`) is dispositioned below:

| `hm:.claude/skills/post-merge-housekeeping/SKILL.md` lines | What they carry | Plugin disposition in `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` |
|---|---|---|
| `:14, :113` | Pointers to `docs/architecture/SKILL_PROVENANCE.md` | Removed (matching `docs/design/ADR_GATE_HOST_CONTRACT.md:205`); the 2026-10-28 timestamp-vs-`headRefOid` rationale at `:110-113` stays inline without the external file pointer |
| `:59, :64, :325, :347` | `.claude/expected_branch.txt` and `CMS_SKIP_BRANCH_GUARD=1` | Generalized to: check `git -C <main-checkout> branch --show-current` and `git -C <main-checkout> status --short`, plus any shared-checkout branch lock or branch-guard hook declared under `## Post-merge` in the host's doctrine; if none is declared, report `branch lock: not declared in ## Post-merge, skipped` in Step 8; never bypass a host branch guard or rewrite another session's lock file |
| `:124-126, :134, :141, :144, :155, :158-159, :161, :326, :334` | `run_cms_e2e.py`, `Name LIKE 'python%'`, `/api/health` (`sandbox:true`), `/api/tuner/content-items`, `temp_e2e_root_<port>/`, `playwright.config.js`, `CMS_E2E_BASE_URL`, "book root" | Generalized to **Step 2.5 Worktree process & resource sweep**: before `git worktree remove <worktree-path>`, (a) check for processes whose command line or working directory references `<worktree-path>` (PowerShell `Get-CimInstance Win32_Process` on Windows; `pgrep -af` / `readlink /proc/<pid>/cwd` on POSIX), and (b) if `## Post-merge` in the host's doctrine declares a worktree daemon probe, probe its declared functional data endpoint rather than an in-memory `/health` flag whose backing files were deleted with a worktree (if none is declared, report `worktree daemon probe: not declared in ## Post-merge, skipped` alongside the worktree-path process check in Step 8) |
| `:169` | `git worktree remove .claude/worktrees/<slug>` | `git worktree remove <worktree-path>` |
| `:214` | `rg -il "<changed-surface-keyword>" docs/architecture docs/reviews docs/design` | `git grep -il "<changed-surface-keyword>" -- '*.md'` across tracked Markdown files (plus any non-Markdown tracking files named under `## Post-merge` in host doctrine) |
| `:242-256` | Prose inline call to `acf.adr.append_amendment` without a fenced ```` ```python ```` block and without the verification-pass / user-override `commit_sha` rule | Replaced by a fenced ```` ```python ```` block (parsed by `ast.parse` in `test_adr_skill_prose.py`) that checks `(repo / ADR_REL).is_file()`, loads `cfg = load_host_config(repo)`, passes `commit_sha=dispatch_commit_sha` (resolved via the single run-detail regex rule of §5.2) and caller-measured `...` placeholders (or `None` when unmeasured) to `LedgerAmendment`, and calls `append_amendment(..., repo / cfg.ledger_path)` |
| `:278, :286, :287` (and surrounding `:276-290`) | [`docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md`], **Guardrail gaps** table, and **Priority board** (`Now`, `Next`, `Parked`, impact classes `S`, `L`, `D`, `A`) | Generalized to: record the live guard-escape search (and any live instance found) and file deferred items in the durable tracking target declared under `## Post-merge` in the host's doctrine (stopping to ask the user if none is declared and items need filing) |

---

## 5. Design

### 5.1 `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md`

The skill file has YAML frontmatter (`name: post-merge-housekeeping`, `description: ...`) and no backslashes (`\` is forbidden across skill prose by `plugins/arch-compliance/tests/test_adr_skill_invariants.py:70-73`). It reads host-specific post-merge rules from the `## Post-merge` section of `config/architecture/ARCHITECTURE.md` (or a document it points to). Its checklist steps are:

- **Step 0 — Shared checkout & installed-skill check before mutation:**
  - Steps 1–2 are strictly read-only. Before moving HEAD or committing on the main checkout (Step 3.5), inspect `git -C <main-checkout> branch --show-current`, `git -C <main-checkout> status --short`, and any branch-lock file declared under `## Post-merge` in the host's doctrine. If another workstream holds the checkout or uncommitted changes exist, stop and ask the user. Never silence `git checkout` / `git pull` with `-q`.
- **Step 1 — Resolve default branch, verify content landed, & check post-merge CI (read-only, squash-aware):**
  - Run `git fetch origin` and resolve the remote default branch once without writing any ref:
    ```bash
    default_branch=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')
    if [ -z "$default_branch" ]; then
      default_branch=$(git ls-remote --symref origin HEAD | awk '/^ref:/ {sub("refs/heads/", "", $2); print $2}')
    fi
    ```
    (If `$default_branch` is still empty, stop and ask the user — never guess `main`.)
  - Inspect PR merge metadata (`gh pr view <N> --json mergedAt,mergeCommit,headRefOid`, or `git log --format='%H %cI %s' -1 --grep='(#<N>)' "origin/$default_branch"` when `gh` is absent), and verify by **content presence** on `origin/$default_branch` (`git show "origin/$default_branch:<path>"` or `git grep '<symbol>' "origin/$default_branch" -- <path>`), never by SHA ancestry or `git diff "$default_branch" <branch>`.
  - Check post-merge CI on `$default_branch`: run `gh run list --branch "$default_branch" --limit 5` (plus any post-merge workflow check declared under `## Post-merge`). If `gh` is absent and no CI check is declared under `## Post-merge`, record `post-merge CI check: not declared / gh absent, skipped` in Step 8.
- **Step 2 — Stranded-commit check (`headRefOid..<branch>`):**
  - Compare `git log --format='%h %cI %s' "$head"..<branch>` against the merged `headRefOid` (never against `mergedAt` timestamps). When `gh` is absent or there is no PR, treat every `"origin/$default_branch"..<branch>` commit as stranded until its whole diff is verified on `origin/$default_branch`.
- **Step 2.5 — Worktree process & resource sweep (before `git worktree remove`):**
  - Before removing `<worktree-path>`, check for any lingering process whose command line or working directory references `<worktree-path>` (Windows PowerShell `Get-CimInstance Win32_Process` filtering `CommandLine` by the worktree slug/path; POSIX `pgrep -af '<worktree-slug>'` and `readlink /proc/<pid>/cwd`).
  - If `## Post-merge` in the host's doctrine declares a background test server, simulator, or container probe, run that probe against its declared functional/data endpoint (never trusting an in-memory `/health` flag whose backing files were deleted when a worktree was removed). If `## Post-merge` declares no daemon probe, report `worktree daemon probe: not declared in ## Post-merge, skipped` in Step 8 (still reporting the result of the worktree-path process check).
- **Step 3 — Teardown:**
  - `git ls-remote --heads origin <branch>`, `git push origin --delete <branch>` (if still present after Step 2 is clear), `git worktree remove <worktree-path>` (from the main checkout), `git branch -D <branch>` (only after Steps 1–2 pass), `git fetch --prune origin` (mandatory so local `remotes/origin/<branch>` refs do not linger), `git worktree prune && git worktree list`, `git branch -a`.
- **Step 3.5 — Take the checkout:**
  - Re-verify Step 0, then `git -C <main-checkout> checkout "$default_branch" && git -C <main-checkout> pull --ff-only`.
- **Step 4 — Plan truthfulness:**
  - If the branch executed a tracked implementation plan, tick completed steps `[x]`, annotate the merge (PR #, squash SHA, date), and remove or update any plan code blocks that review rounds superseded.
- **Step 5 — Out-of-branch tracking-doc reconciliation:**
  - Run `git grep -il "<changed-surface-keyword>" -- '*.md'` across tracked Markdown files to find roadmaps, status tables, and architecture docs outside the branch's diff that still describe pre-merge state, and update them with dates.
- **Step 6 — Review-round sweep, spec filing-claims audit, & ADR ledger amendment:**
  - Sweep PR review comments (`gh pr view <N> --comments`) and in-session subagent review reports for any item tagged "follow-up", "out of scope", "pre-existing", or "not a blocker". **No `gh` or non-GitHub host?** Sweep in-session subagent review reports and branch commit messages, and ask the user for any external PR/MR review notes rather than skipping. File each item in the durable tracking target declared under `## Post-merge` (if none is declared and items exist, stop and ask the user where to file them).
  - If the branch shipped or implemented a spec, grep the spec for "filed", "recorded in", "to be written", and "follow-up" claims and verify each named target exists and carries the promised entry.
  - Classify any review follow-up or escaped defect by spec-stage lens (`refuter`, `compliance`, `sweeper`, `hardening`, or `none`) in the tracking doc entry, and when the merged work had an ADR-reviewed spec and `(repo / ADR_REL).is_file()` is true, append a `LedgerAmendment` (§5.2).
- **Step 6.5 — Live guard-escape check (when the slice shipped a guard or retired a defect class):**
  - Ask: *"What ALREADY gets through the guard we just shipped? Name one live instance — file and line — or state, after actually searching, that you found none."* Record the search command and file any live escape in the tracking target declared under `## Post-merge`.
- **Step 7 — Memory / status notes** and **Step 8 — Report before moving on** (explicitly listing the outcome of every check, including any host-specific check reported as `not declared in ## Post-merge, skipped`).

### 5.2 Step 6's `acf.adr` Python snippet and the single-source row-identity rule

When the merged work had a spec-stage review under `/adversarial-design-review` and `(repo / ADR_REL).is_file()` is true, Step 6 runs the following fenced ```` ```python ```` block from the repository root (using `...` placeholders for caller-supplied values, matching `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:303-325` and `docs/design/ADR_GATE_HOST_CONTRACT.md:229-233`):

```python
from acf.adr import LedgerAmendment, append_amendment, load_host_config
from acf.repo import ADR_REL, resolve_repo

repo = resolve_repo(None)
if (repo / ADR_REL).is_file():
    cfg = load_host_config(repo)
    append_amendment(
        LedgerAmendment(
            spec_path=spec_path,
            # The commit_sha of the last full 4-reviewer dispatch for spec_path:
            # among files in `repo / cfg.runs_dir` matching
            # `<STEM>_v<N>_<YYYY-MM-DD>.md` (excluding `_response_` files), pick
            # the highest integer N and read `<commit_sha>` from line 3
            # (`Spec: `<spec_path>` @ `<commit_sha>``):
            commit_sha=dispatch_commit_sha,
            date=today_iso,
            # From the spec's own absorption/response record when the merged work
            # had a spec-stage review; pass None for any counter not measured here:
            absorbed=...,
            rejected=...,
            blocks_overturned=...,
            # Count of review follow-ups or CI/production defects from this merge
            # attributed to a spec-stage lens (refuter/compliance/sweeper/hardening):
            escapes=...,
        ),
        repo / cfg.ledger_path,
    )
```

**Why `dispatch_commit_sha` uses one run-detail recipe (and why no ledger reader, spec-header fallback, or `0` default is used):**

1. **Single-source row identity after any clearance (`## Single point of definition`):** A controller verification pass (`plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:443-453`) or a user override after a blocked full run updates the spec's `**Adversarial review:**` header to the verification-pass or override commit SHA, but writes **no** `LedgerRow`. `LedgerAmendment` matches the prior `LedgerRow` by `spec_path` + `commit_sha` (`plugins/arch-compliance/python/acf/adr/ledger.py:139-140`, `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:362-365`). Meanwhile, `repo / cfg.runs_dir` contains both full-dispatch detail files named `{stem}_v{version}_{date}.md` (`plugins/arch-compliance/python/acf/adr/run_detail.py:47`) and author response files named `<STEM>_v<N>_response_<date>.md` (`plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:110`), and lexicographic sorting fails once `version >= 10`. Selecting the file in `repo / cfg.runs_dir` matching `^<STEM>_v([0-9]+)_([0-9]{4}-[0-9]{2}-[0-9]{2})\.md$` with the **highest integer `int(version)`** and reading `<commit_sha>` from its line 3 (`Spec: \`<spec_path>\` @ \`<commit_sha>\``, produced by `plugins/arch-compliance/python/acf/adr/run_detail.py:84`) gives one unambiguous source for every clearance kind without a second source ("or from the spec header"), without an inline JSONL ledger parser (`plugins/arch-compliance/python/acf/adr/ledger.py:146-149`), and without any `assert` statement (`## One base exception`).
2. **Counter provenance (`absorbed`, `rejected`, `blocks_overturned`, `escapes`):** `LedgerRow` writes `absorbed=0, rejected=0, blocks_overturned=0` at dispatch time (`plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:320, 362-364`). Step 6 fills `absorbed`, `rejected`, and `blocks_overturned` from the spec's own absorption/response record, and fills `escapes` with the count of review follow-ups or CI/production defects attributed to a spec-stage lens (`refuter`, `compliance`, `sweeper`, `hardening`). Any counter not measured by the step is left `None` (`plugins/arch-compliance/python/acf/adr/ledger.py:161-166`: *"an amender sets only the counter(s) it knows, leaving the rest None so a reader is never told '0' when the true answer is 'unknown'"*), never hardcoded to `0`.

### 5.3 Cross-skill handoffs, doctrine, registry, version bump, and installed-skills check

1. **Cross-skill handoffs restored:**
   - `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:363`: `"amended later by the host's post-merge process"` $\rightarrow$ `"amended later by post-merge-housekeeping"`.
   - `plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:223`: `"After merge, the host's post-merge process owns"` $\rightarrow$ `"After merge, post-merge-housekeeping owns"`.
2. **Installed-skills byte check (`scripts/check_installed_skills.py`):**
   - `GATE_SKILLS` at `scripts/check_installed_skills.py:18` gains `"post-merge-housekeeping"`:
     `GATE_SKILLS = ("adversarial-design-review", "responding-to-adversarial-review", "post-merge-housekeeping")`.
   - **Stated trade-off:** Keeping all three ADR-lifecycle skills in `GATE_SKILLS` means one byte-check command (`python scripts/check_installed_skills.py <INSTALL_PATH>`) verifies all three skills together, and drift in `post-merge-housekeeping` also blocks a gate run until reinstalled. To ensure `post-merge-housekeeping` itself is checked before it runs in this repository, `CLAUDE.md` is updated to run `python scripts/check_installed_skills.py <INSTALL_PATH>` before `/arch-compliance:post-merge-housekeeping` as well as before `/arch-compliance:adversarial-design-review`.
   - `tests/test_check_installed_skills.py:22-28` already iterates over `_load_script().GATE_SKILLS` and synthesizes its own temporary fixture tree for each entry, so no edit to `tests/test_check_installed_skills.py` is required.
3. **Doctrine and mandate registry (`config/architecture/ARCHITECTURE.md` & `config/architecture/mandates.yml`):**
   - `config/architecture/ARCHITECTURE.md:135-141` (`## Prose names no host`): update `plugin.gate-prose-names-no-host` to state that `plugins/arch-compliance/tests/test_adr_skill_prose.py` checks the two gate skills and `post-merge-housekeeping` against the enumerated `FORBIDDEN` list of known origin-host (`HistoricMansions`) vocabulary (honoring `## No completeness claims` at `config/architecture/ARCHITECTURE.md:157-167`).
   - `config/architecture/ARCHITECTURE.md:182-191` (`## Release discipline`): update `"the two gate skills"` / `"those two skill trees"` to `"the two gate skills and post-merge-housekeeping"` / `"those three skill trees"`.
   - Add a `## Post-merge` section to `config/architecture/ARCHITECTURE.md` declaring this repository's own post-merge conventions:
     - **Shared-checkout branch lock:** none declared.
     - **Worktree daemon probe:** none declared (no background test server).
     - **Post-merge CI workflows:** `.github/workflows/ci.yml` (`test` job on `main`).
     - **Durable tracking target:** GitHub Issues on `IanDBallard/arch-compliance-for-superpowers` (`gh issue create`), so filing a follow-up or guard escape never edits an already-cleared spec.
     - Ends with `No row: host operational declarations; no test enforces this.` (matching the section convention of `config/architecture/ARCHITECTURE.md:155, 167, 180, 191, 205-206, 212`).
   - `config/architecture/mandates.yml:193`: update `title` of `plugin.gate-prose-names-no-host` to `"The gate and housekeeping skills' prose contains no known origin-host vocabulary"`.
4. **Version bump (`## Release discipline`, `config/architecture/ARCHITECTURE.md:184-185`):**
   - Bump `version` from `"0.2.1"` to `"0.2.2"` in `plugins/arch-compliance/.claude-plugin/plugin.json:3` and `pyproject.toml:3`.
5. **User-facing skill tables (`README.md` & `docs/guides/SUPERPOWERS_COMPLEMENT.md`):**
   - Add `/post-merge-housekeeping` to the Skills table in `README.md:28-35` and add `/adversarial-design-review`, `/responding-to-adversarial-review`, and `/post-merge-housekeeping` to the Skills table in `docs/guides/SUPERPOWERS_COMPLEMENT.md:38-43`.

### 5.4 Test suite extensions (`test_adr_skill_prose.py` & `test_adr_skill_invariants.py`)

1. **`plugins/arch-compliance/tests/test_adr_skill_prose.py`:**
   - Add `HOUSEKEEPING = SKILLS / "post-merge-housekeeping"` and append `HOUSEKEEPING / "SKILL.md"` to `FILES` (`:12-17`, now 8 files).
   - Extend `FORBIDDEN` (`:18-19`) with known origin-host (`HistoricMansions`) housekeeping literals: `"run_cms_e2e"`, `"expected_branch.txt"`, `"CMS_SKIP_BRANCH_GUARD"`, `"ARCHITECTURE_REVIEW_2026"`. (Its scope, per `## No completeness claims`: it catches these enumerated HM literals, not vocabulary from an arbitrary unenumerated host.)
   - Include `HOUSEKEEPING / "SKILL.md"` in `_python_bodies()` (`:24`) so its fenced ```` ```python ```` block is parsed with `ast.parse` and every `from acf... import ...` symbol is verified to exist in the package (`test_every_python_body_parses_and_its_acf_imports_exist`, `:44-54`).
2. **`plugins/arch-compliance/tests/test_adr_skill_invariants.py`:**
   - Add `HOUSEKEEPING = SKILLS / "post-merge-housekeeping"`.
   - Include `HOUSEKEEPING` in `test_both_skills_have_frontmatter_with_a_name_and_description` (`:41-47`) and `test_no_skill_file_contains_a_backslash` (`:70-73`).
   - Add `test_housekeeping_skill_invariants()` asserting that `post-merge-housekeeping/SKILL.md`:
     - imports `LedgerAmendment`, `append_amendment`, and `load_host_config` in a real `from acf.adr import` line and `ADR_REL`, `resolve_repo` in a real `from acf.repo import` line;
     - names `dispatch_commit_sha`, `_response_`, and `## Post-merge`, and does not contain `absorbed=0` inside any fenced ```` ```python ```` block (scoped to fenced Python blocks so prose explaining that `LedgerRow` writes zeros at dispatch time is unaffected);
     - preserves the core post-merge safety checks (`refs/remotes/origin/HEAD`, `git ls-remote --symref origin HEAD`, `headRefOid`, `git fetch --prune`, `What ALREADY gets through the guard we just shipped?`);
     - is named by both `adversarial-design-review/SKILL.md` and `responding-to-adversarial-review/SKILL.md`.

---

## 6. Shape fit

### What existing shape does this extend?

| Element | Existing shape extended | Relationship |
|---|---|---|
| `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` | `plugins/arch-compliance/skills/adversarial-design-review/` and `plugins/arch-compliance/skills/responding-to-adversarial-review/`, ported from HM in phase 1c (`docs/design/ADR_GATE_HOST_CONTRACT.md` §5.4) | `ADJACENT` — third portable governance skill in `plugins/arch-compliance/skills/`; shares the same `acf.repo` + `acf.adr` host contract |
| Step 6 `LedgerAmendment` snippet in `post-merge-housekeeping/SKILL.md` | `acf.adr.LedgerAmendment`, `acf.adr.append_amendment` (`plugins/arch-compliance/python/acf/adr/ledger.py:132-172, 231-237`), `acf.adr.load_host_config` (`plugins/arch-compliance/python/acf/adr/host.py:28-33`), `acf.repo.ADR_REL`, `acf.repo.resolve_repo` (`plugins/arch-compliance/python/acf/repo.py:21, 32-44`) | Live skill consumer of `LedgerAmendment` and `append_amendment` (`## Live consumers`, `config/architecture/ARCHITECTURE.md:151-155`), with `...` placeholders matching `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:303-325` |
| `HOUSEKEEPING` in `plugins/arch-compliance/tests/test_adr_skill_prose.py` | `FILES`, `FORBIDDEN`, and `_python_bodies()` in `plugins/arch-compliance/tests/test_adr_skill_prose.py:12-28` | Extends the existing prose-portability and AST-import test module (`plugin.gate-prose-names-no-host`) rather than creating a second prose scanner |
| `HOUSEKEEPING` in `plugins/arch-compliance/tests/test_adr_skill_invariants.py` | Frontmatter, no-backslash, and import-pin tests in `plugins/arch-compliance/tests/test_adr_skill_invariants.py:41-99` | Extends the existing skill-invariants test module |
| `"post-merge-housekeeping"` in `scripts/check_installed_skills.py:18` | `GATE_SKILLS` in `scripts/check_installed_skills.py:18`, consumed by `tests/test_check_installed_skills.py:23` | Single definition of `GATE_SKILLS` (`## Single point of definition`) |

### What second way to do something does it create?

None in this repository. Across repositories, `hm:.claude/skills/post-merge-housekeeping/SKILL.md` and `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` coexist temporarily until Slice 3 (HM cutover) deletes HM's local copy, identical to the phase 1c $\rightarrow$ 1d transition for `adversarial-design-review` and `responding-to-adversarial-review` (`docs/design/ADR_GATE_HOST_CONTRACT.md:425`).

### Pattern sweep

The defect class this design retires in `post-merge-housekeeping` is *origin-host paths, doctrine names, and stack-specific assumptions embedded in portable skill prose*. Swept across `hm:.claude/skills/post-merge-housekeeping/SKILL.md` by §4.1 Recipes A and B (23 lines across 7 groups, all dispositioned in §4.2) and guarded against known origin-host vocabulary and backslashes by `plugins/arch-compliance/tests/test_adr_skill_prose.py` and `plugins/arch-compliance/tests/test_adr_skill_invariants.py`.

---

## 7. Definition of done

1. `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` exists and passes all checks in `plugins/arch-compliance/tests/test_adr_skill_prose.py` and `plugins/arch-compliance/tests/test_adr_skill_invariants.py` (including the new `test_housekeeping_skill_invariants` test of §5.4.2).
2. Planting any `FORBIDDEN` origin-host literal (`"GEMINI"`, `"CLAUDE.md"`, `"SKILL_PROVENANCE"`, `"scripts.core"`, `"docs/design"`, `"docs/reviews"`, `"docs/architecture"`, `".cursor"`, `"run_cms_e2e"`, `"expected_branch.txt"`, `"CMS_SKIP_BRANCH_GUARD"`, `"ARCHITECTURE_REVIEW_2026"`) or a backslash (`\`) in `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` fails `pytest`, and restoring passes.
3. `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:363` and `plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:223` name `post-merge-housekeeping` directly.
4. `scripts/check_installed_skills.py:18` includes `"post-merge-housekeeping"` in `GATE_SKILLS`, `CLAUDE.md` names the byte check before `/arch-compliance:post-merge-housekeeping`, and `tests/test_check_installed_skills.py` passes.
5. `config/architecture/ARCHITECTURE.md` (updated `## Prose names no host` and `## Release discipline`, plus new `## Post-merge` section ending with `No row: host operational declarations; no test enforces this.`) and `config/architecture/mandates.yml` (`plugin.gate-prose-names-no-host` title) are updated per §5.3.3, and `tests/test_self_host.py` passes.
6. `README.md:28-35` and `docs/guides/SUPERPOWERS_COMPLEMENT.md:38-43` list `/post-merge-housekeeping` (and `/adversarial-design-review`, `/responding-to-adversarial-review` in `SUPERPOWERS_COMPLEMENT.md`) per §5.3.5.
7. `plugins/arch-compliance/.claude-plugin/plugin.json` and `pyproject.toml` versions are bumped to `"0.2.2"`.
8. `python -m pytest -q` and `PYTHONUTF8=1 python -m acf.cli_check_diff --repo . --base origin/main` (after `main` `2929331` is merged to `origin/main` via PR; `--base main` prior to that merge) pass with zero BLOCK findings.
9. `npm test --prefix plugins/arch-compliance/detectors/typescript` prints `self-test OK`.
10. This spec clears `/adversarial-design-review`, with its run detail under `docs/reviews/adr_runs/` and its `LedgerRow` in `docs/reviews/adversarial_design_ledger.jsonl` committed on the branch.

---

## 8. Risks

| Risk | Mitigation |
|---|---|
| An agent copying the Step 6 `LedgerAmendment` snippet overwrites real `absorbed` / `rejected` / `blocks_overturned` counts with `0` | The snippet uses `...` placeholders (never `0`) and explicitly instructs passing the counts from the spec's absorption record or `None` when unmeasured; `test_housekeeping_skill_invariants` asserts `"absorbed=0"` does not appear in any fenced Python block of `post-merge-housekeeping/SKILL.md` |
| `repo / cfg.runs_dir` contains `<STEM>_v<N>_response_<date>.md` files or reaches `v10`, causing naive filename sorting to pick the wrong file | Step 6 specifies matching `^<STEM>_v([0-9]+)_([0-9]{4}-[0-9]{2}-[0-9]{2})\.md$` (excluding `_response_` files) and picking the highest integer `int(version)` |
| A host without `config/architecture/adr.yml` runs `post-merge-housekeeping` on a bounded PR and hits `AcfInputError` in Step 6 | Step 6 gates `load_host_config(repo)` on `(repo / ADR_REL).is_file()` and on the merged branch having an ADR-reviewed spec (§5.2) |
| A host without a `## Post-merge` section in `ARCHITECTURE.md` silently skips branch-lock or worktree-daemon checks | Step 8 requires reporting `<check>: not declared in ## Post-merge, skipped` whenever `## Post-merge` omits a check (§2 Decision 1, §5.1) |
| Installed skill copies drift from the repository clone after editing three skills | Bump version to `0.2.2`, sync installed skills, and verify with `python scripts/check_installed_skills.py <INSTALL_PATH>` |

---

## Appendix — premise verification (authoring time, 2026-11-03)

| Premise | Command | Observed output |
|---|---|---|
| Recipe A & B hits in `hm:.claude/skills/post-merge-housekeeping/SKILL.md` | Run §4.1 Recipe A and Recipe B against `hm:.claude/skills/post-merge-housekeeping/SKILL.md` at `b652fab05` | Recipe A: 7 lines (`:14, :113, :124, :159, :214, :278, :326`); Recipe B (excluding A): 16 lines (`:59, :64, :125, :126, :134, :141, :144, :155, :158, :161, :169, :286, :287, :325, :334, :347`) |
| Both gate skills currently say `"the host's post-merge process"` | `git grep -n "post-merge process" -- plugins/arch-compliance/skills/` | `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:363` and `plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:223` |
| `LedgerAmendment` has optional `None`-defaulted counters and no read-back in the pipeline | Inspect `plugins/arch-compliance/python/acf/adr/ledger.py:132-166` | Docstring at `:139-140, :146-149` states match by `spec_path` + `commit_sha` and no read-back in pipeline; fields `absorbed`, `rejected`, `blocks_overturned`, `escapes` default to `None` (`:163-166`) |
| Run-detail file naming and header format | Inspect `plugins/arch-compliance/python/acf/adr/run_detail.py:47, 81-85` | Line 47: `name = f"{stem}_v{version}_{date}.md"`; Line 84: `f"Spec: \`{run.spec_path}\` @ \`{run.commit_sha}\`"` |
| `GATE_SKILLS` in `scripts/check_installed_skills.py` has 2 skills at `2929331` | `sed -n 18p scripts/check_installed_skills.py` | `GATE_SKILLS = ("adversarial-design-review", "responding-to-adversarial-review")` |
| Current plugin version is `0.2.1` | Inspect `pyproject.toml:3` and `plugins/arch-compliance/.claude-plugin/plugin.json:3` | Both carry `"0.2.1"` |
