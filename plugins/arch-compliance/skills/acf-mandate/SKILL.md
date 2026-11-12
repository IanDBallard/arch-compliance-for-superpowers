---
name: acf-mandate
description: Use when adding, editing, or deprecating rows in config/architecture/mandates.yml, changing mandate severity/detection/status, validating the ACF registry schema, or running /acf-mandate.
---

# /acf-mandate — Registry Row Maintenance

Edit the **host** mandate registry at `config/architecture/mandates.yml`. This skill validates schema and loads the registry; it does **not** generate detector implementations or LLM prompt packs.

**Hard rule:** New `detection: ast`, `detection: guard` or `detection: llm` mandates need matching code or prompt stubs elsewhere: a built-in detector id, a host callable named by `detector: <path>.py:<callable>`, or a prompt id. Tell the user what is missing. Do **not** invent full detector codegen, new AST visitors, host detector callables, or complete judge prompts in this skill.

## Checklist

1. Confirm host registry path and existing ARCHITECTURE.md
2. Clarify intent: add / edit / deprecate
3. Apply schema-valid row changes
4. Ensure `arch_anchor` exists in ARCHITECTURE.md
5. Validate with `load_mandates` + the built-in contracts and LLM prompt ids
6. Remind about detector / prompt / auditor stubs when needed
7. Summarize diff of mandate ids touched

## Host paths

```text
<host>/config/architecture/mandates.yml      # required
<host>/config/architecture/ARCHITECTURE.md   # required for arch_anchor checks
```

If `mandates.yml` is missing, stop and tell the user to run `/acf-setup` first.

## Schema (every row)

Root YAML type: **list** of mandate objects. Required fields:

| Field | Type / allowed values | Notes |
|-------|----------------------|--------|
| `id` | string | Stable dotted id, e.g. `fail-loud.empty-catch` |
| `title` | string | Human-readable |
| `severity` | `BLOCK` \| `WARN` | BLOCK fails gates |
| `detection` | `ast` \| `llm` \| `grep` \| `guard` \| `manual` | How evidence is produced |
| `detector` | string | Built-in detector id, host reference `<posix_rel_path.py>:<callable>` (`ast`/`guard` rows; the file must exist inside the repository), or prompt id (must exist when the row is active) |
| `languages` | `python` \| `typescript` \| `both` \| `none` | Pack applicability |
| `call_sites` | list of strings | Closed vocabulary: `ci`, `precommit`, `hook`, `posttooluse`, `audit`; any other spelling is refused. `ci` and `precommit` are the sites `acf-check-diff --call-site` runs; `hook` and `posttooluse` are two spellings of the PostToolUse hook; `audit` is not a Tier-1 gate. A row runs only at the sites it declares: a `[ci]`-only row is not reported by the hook or by `--call-site precommit` |
| `exemption_tokens` | list of strings | Inline exemption markers |
| `status` | `enforced` \| `partial` \| `unenforced` | Enforcement maturity (`unenforced` never gates; `partial` still gates) |
| `arch_anchor` | string | Literal substring of ARCHITECTURE.md (usually a `##` heading) |
| `auditor` | string \| omit | Optional; Tier-3 auditor name for soft/llm facets |

Match the Pydantic model in `acf.registry.Mandate`. Unknown extra fields should be avoided.

`exemption_tokens` are the **only** inline exemption markers. Detectors emit raw findings; `apply_registry` drops a finding when the source line contains `# <token>: reason` or `// <token>: reason` (non-empty reason required). Changing tokens here is how hosts customize exemptions — do not expect detectors to hardcode `-ok` forms.

### Status / detection rules of thumb

- An active (`enforced` or `partial`) `detection: ast` or `guard` row → a built-in `detector` must be a key of `acf.detectors.KNOWN_DETECTORS` and the row's `id` must be that detector's mandate id; a host reference must name an existing `.py` file inside the repository (validation fails otherwise). Every built-in mandate id is reserved for its built-in row.
- `status: enforced` + `detection: llm` → judge must be configured at runtime or gates hard-fail; still requires a known prompt id in `LLM_PROMPT_IDS` for drift discipline.
- `status: partial` still **gates** when detectors emit findings — it means coverage is incomplete, not “warn-only / skip.”
- Use `unenforced` when the detector/prompt does not exist yet: an active row (`enforced` or `partial`) naming one is refused at load.
- An active `ast`/`guard` row must keep at least one Tier-1 call site (`ci`, `precommit`, `hook`, `posttooluse`) at which its detector runs, and a built-in row's `id` is its detector's mandate id; deprecate by setting `status: unenforced`, not by emptying `call_sites`; do **not** delete historical ids unless the user explicitly wants removal (ids may appear in baselines).

## Operations

### Add

1. Choose a new unique `id` (fail if collision).
2. Fill all required fields; set `status` honestly.
3. Add or reuse an `arch_anchor` heading in `ARCHITECTURE.md` — the exact `arch_anchor` string must appear in that file.
4. If `detection` is `ast`, `guard` or `llm`, list the stub the user still needs (see below) and use `unenforced` until the stub exists. For a built-in detector the row's `id` is the detector's mandate id and its `call_sites` stay within the sites that detector runs at.

### Edit

1. Load current row by `id`.
2. Change only requested fields; keep `id` stable unless the user explicitly renames (then update baselines/docs references).
3. Re-check `arch_anchor`, the built-in contract (mandate id, call sites) or host reference, and the prompt id after edits.

### Deprecate

1. Set `status: unenforced` (typical).
2. Optionally set `severity: WARN` if still informative. Do not empty `call_sites` on an active `ast`/`guard` row; once the row is `unenforced` it may keep its sites.
3. Leave the row in place unless the user insists on deletion.
4. Note that `.acf` hooks / CI may still load the row; unenforced rows should not gate as BLOCK via AST enforcement paths.

## Validate (mandatory before finishing)

From an environment where the `acf` package is importable, run:

```bash
python -c "
import sys
from acf.detectors import load_gate_registry
from acf.registry import missing_anchors
from acf.repo import ARCH_REL, MANDATES_REL, resolve_repo

repo = resolve_repo(None)
reg = load_gate_registry(repo, repo / MANDATES_REL)
print(f'OK: {len(reg.mandates)} mandates from {reg.source_path}')
for m in reg.mandates:
    print(f'  {m.id} status={m.status} detection={m.detection} detector={m.detector}')
missing = missing_anchors(reg, (repo / ARCH_REL).read_text(encoding='utf-8'))
if missing:
    sys.exit(f'arch_anchor not found in {ARCH_REL.as_posix()} for: {missing}')
"
```

The snippet refuses a repeated mandate id, an active `ast`/`guard` row that breaks its
detector's contract (unknown built-in detector, a row `id` that is not the detector's mandate
id, a Tier-1 call site at which no gate runs it, or no Tier-1 call site), a host reference
that does not resolve to an existing file inside the repository, an active `llm` row whose
prompt id is unknown, and a row whose `arch_anchor` is not a literal substring of
`config/architecture/ARCHITECTURE.md` (the same check the profile drift test runs).

If `UnknownDetectorError` or `AcfInputError` occurs, or an anchor is reported missing: fix
the YAML or the heading; do not weaken validation by omitting `known_detectors` for
“convenience.” The valid built-in detectors are the contracts in
`acf.detectors.KNOWN_DETECTORS`, and `acf.judge.LLM_PROMPT_IDS` for `llm` rows; print them
with `python -c "from acf.detectors import KNOWN_DETECTORS; print(sorted(KNOWN_DETECTORS))"`.

## Detector / prompt stubs — remind, do not codegen

When the user adds or promotes a mandate whose `detector` is **not** a built-in contract, an existing host callable, or a prompt id:

| `detection` | What to remind | Do **not** do |
|-------------|----------------|---------------|
| `ast` | Need a pack function / ts-morph rule registered under that detector id, or a host callable `<path>.py:<callable>` returning `HostHit` values; keep `status: unenforced` until shipped | Write a full new AST detector implementation in this skill turn |
| `llm` | Need a prompt id in `LLM_PROMPT_IDS` + judge wiring; enforced llm hard-fails if judge unset | Author a complete production prompt pack / judge pipeline |
| `grep` / `guard` / `manual` | Document how humans or external tools satisfy the mandate (a `guard` row needs its built-in id or host callable); often `unenforced` | Pretend deterministic coverage exists |

Say explicitly: `/acf-mandate` updates registry rows only. Implementing detectors is a separate engineering task.

## Done summary

- Action taken (add/edit/deprecate) and mandate `id`s
- Validation command result
- Any missing detector/prompt/auditor stubs
- Reminder to re-run `acf-check-diff` (with `--call-site ci` or `--call-site precommit`, which selects the rows that run) after meaningful enforcement changes; the re-run needs the user to run `acf-allow` again after a host row or detector file changes (never run it or add `--trusted-checkout` yourself)

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Editing plugin `profiles/*` instead of host config | Only change host `config/architecture/` |
| Active (`enforced` or `partial`) + unknown `detector` | Use `unenforced` or implement stub first |
| `arch_anchor` not in ARCHITECTURE.md | Add heading or fix anchor string |
| Full detector codegen in this skill | Refuse; list stub locations only |
| Skipping `load_mandates(..., known_detectors=...)` | Always validate before claiming done |
