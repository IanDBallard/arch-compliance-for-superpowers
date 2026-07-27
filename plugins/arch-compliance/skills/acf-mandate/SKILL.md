---
name: acf-mandate
description: Use when adding, editing, or deprecating rows in config/architecture/mandates.yml, changing mandate severity/detection/status, validating the ACF registry schema, or running /acf-mandate.
---

# /acf-mandate — Registry Row Maintenance

Edit the **host** mandate registry at `config/architecture/mandates.yml`. This skill validates schema and loads the registry; it does **not** generate detector implementations or LLM prompt packs.

**Hard rule:** New `detection: ast` or `detection: llm` mandates need matching code or prompt stubs elsewhere. Tell the user what is missing. Do **not** invent full detector codegen, new AST visitors, or complete judge prompts in this skill.

## Checklist

1. Confirm host registry path and existing ARCHITECTURE.md
2. Clarify intent: add / edit / deprecate
3. Apply schema-valid row changes
4. Ensure `arch_anchor` exists in ARCHITECTURE.md
5. Validate with `load_mandates` + known detector union
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
| `detector` | string | Detector or prompt id (must exist when enforced+ast) |
| `languages` | `python` \| `typescript` \| `both` \| `none` | Pack applicability |
| `call_sites` | list of strings | e.g. `ci`, `hook`, `audit` |
| `exemption_tokens` | list of strings | Inline exemption markers |
| `status` | `enforced` \| `partial` \| `unenforced` | Enforcement maturity |
| `arch_anchor` | string | Literal substring of ARCHITECTURE.md (usually a `##` heading) |
| `auditor` | string \| omit | Optional; Tier-3 auditor name for soft/llm facets |

Match the Pydantic model in `acf.registry.Mandate`. Unknown extra fields should be avoided.

### Status / detection rules of thumb

- `status: enforced` + `detection: ast` → `detector` **must** be in the known detector union (validation fails otherwise).
- `status: enforced` + `detection: llm` → judge must be configured at runtime or gates hard-fail; still requires a known prompt id in `LLM_PROMPT_IDS` for drift discipline.
- Prefer `partial` or `unenforced` when the detector/prompt does not exist yet.
- Deprecate by setting `status: unenforced` (and optionally lowering `call_sites`); do **not** delete historical ids unless the user explicitly wants removal (ids may appear in baselines).

## Operations

### Add

1. Choose a new unique `id` (fail if collision).
2. Fill all required fields; set `status` honestly.
3. Add or reuse an `arch_anchor` heading in `ARCHITECTURE.md` — the exact `arch_anchor` string must appear in that file.
4. If `detection` is `ast` or `llm`, list the stub the user still needs (see below) and prefer `partial`/`unenforced` until the stub exists.

### Edit

1. Load current row by `id`.
2. Change only requested fields; keep `id` stable unless the user explicitly renames (then update baselines/docs references).
3. Re-check `arch_anchor` and detector known-set after edits.

### Deprecate

1. Set `status: unenforced` (typical).
2. Optionally remove from `call_sites` or set `severity: WARN` if still informative.
3. Leave the row in place unless the user insists on deletion.
4. Note that `.acf` hooks / CI may still load the row; unenforced rows should not gate as BLOCK via AST enforcement paths.

## Validate (mandatory before finishing)

From an environment where the `acf` package is importable, run:

```bash
python -c "
from pathlib import Path
from acf.registry import load_mandates
from acf.detectors.python_pack import PYTHON_DETECTOR_IDS
from acf.detectors.typescript_bridge import TS_DETECTOR_IDS
from acf.judge import LLM_PROMPT_IDS

path = Path('config/architecture/mandates.yml')
known = PYTHON_DETECTOR_IDS | TS_DETECTOR_IDS | LLM_PROMPT_IDS
reg = load_mandates(path, known_detectors=known)
print(f'OK: {len(reg.mandates)} mandates from {reg.source_path}')
for m in reg.mandates:
    print(f'  {m.id} status={m.status} detection={m.detection} detector={m.detector}')
"
```

Also verify each `arch_anchor` is a substring of `config/architecture/ARCHITECTURE.md` (same discipline as profile drift tests).

If `UnknownDetectorError` or `RegistryLoadError` occurs: fix the YAML; do not weaken validation by omitting `known_detectors` for “convenience.”

Known detector union today:

- Python AST: `fail_loud_bare_except`, `no_shims_hasattr`
- TypeScript AST: `empty_catch`, `explicit_any`
- LLM prompts: `llm_react_boundaries`, `llm_fail_loud`, `llm_no_shims`, `llm_posix_paths`

## Detector / prompt stubs — remind, do not codegen

When the user adds or promotes a mandate whose `detector` is **not** in the known union:

| `detection` | What to remind | Do **not** do |
|-------------|----------------|---------------|
| `ast` | Need a pack function / ts-morph rule registered under that detector id; keep `status` non-enforced until shipped | Write a full new AST detector implementation in this skill turn |
| `llm` | Need a prompt id in `LLM_PROMPT_IDS` + judge wiring; enforced llm hard-fails if judge unset | Author a complete production prompt pack / judge pipeline |
| `grep` / `guard` / `manual` | Document how humans or external tools satisfy the mandate; often `unenforced`/`partial` | Pretend deterministic coverage exists |

Say explicitly: `/acf-mandate` updates registry rows only. Implementing detectors is a separate engineering task.

## Done summary

- Action taken (add/edit/deprecate) and mandate `id`s
- Validation command result
- Any missing detector/prompt/auditor stubs
- Reminder to re-run `acf-check-diff` after meaningful enforcement changes

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Editing plugin `profiles/*` instead of host config | Only change host `config/architecture/` |
| `enforced` + unknown `detector` | Use `partial`/`unenforced` or implement stub first |
| `arch_anchor` not in ARCHITECTURE.md | Add heading or fix anchor string |
| Full detector codegen in this skill | Refuse; list stub locations only |
| Skipping `load_mandates(..., known_detectors=...)` | Always validate before claiming done |
