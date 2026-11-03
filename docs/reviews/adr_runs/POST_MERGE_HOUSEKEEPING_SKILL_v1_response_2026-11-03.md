# Author response record — `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md` v1

- **Spec:** `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md`
- **Reviewed commit (v1):** `19ff011267f7e2e2bdfafc2e9a59fc72dd03b7b6`
- **Run detail answered:** `docs/reviews/adr_runs/POST_MERGE_HOUSEKEEPING_SKILL_v1_2026-11-03.md`
- **Declared revision class:** precision-only (fixing `C4` line citations in `plugins/arch-compliance/python/acf/adr/run_detail.py:43` and `plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:133`, removing the literal `\.` backslash from the spec's prose filename pattern, aligning `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:128-131` to the same `(int(N), <date>)` tie-breaking rule, and expanding §4.1 Recipe B to include `:133` and `:143` of `hm:.claude/skills/post-merge-housekeeping/SKILL.md`).

## Blocking reasons

### C4 — `load-bearing claim C4 (premise) is REFUTED`

- **Blocking line:** `load-bearing claim C4 (premise) is REFUTED: Two citations and one quoted line in this claim are false against the current tree. First, in plugins/arch-compliance/python/acf/adr/run_detail.py, line 47 is 'out: list[str] = []' inside _verdict_lines(payload); the filename template 'return Path(runs_dir) / f"{stem}_v{version}_{date}.md"' is at line 43 (and the Appendix at docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md:277 quotes 'Line 47: name = f"{stem}_v{version}_{date}.md"', a variable assignment that does not exist in run_detail.py). Second, in plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md, line 110 is the Markdown table delimiter '|---|---|---|' inside section 2a; the response-record filename pattern ('<SPEC_STEM>_v<N>_response_<date>.md') is at line 133 (corroborated by plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:134). Only line 84 of plugins/arch-compliance/python/acf/adr/run_detail.py ('f"Spec: `{run.spec_path}` @ `{run.commit_sha}`"' as line 3 of render_run_detail output) holds.`
- **Resolution (revised text):**
  1. Replaced every `plugins/arch-compliance/python/acf/adr/run_detail.py:47` citation across §2 Decision 3 (`:50, :53`), §3 (`:62`), §5.2 (`:177`), and the Appendix (`:278`) with `plugins/arch-compliance/python/acf/adr/run_detail.py:43` (`return Path(runs_dir) / f"{stem}_v{version}_{date}.md"`).
  2. Replaced `plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:110` across §2 Decision 3 (`:52`), §5.2 (`:177`), and the Appendix (`:278`) with `plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md:133` (and `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:134`).
  3. Absorbed the 3-reviewer converged finding (`refuter`, `sweeper`, `hardening`), `sweeper`'s `PARTIAL_OVERLAP` on run-detail selection, and `refuter`'s `important` finding on §4.1/§4.2 row 3:
     - Replaced `^<STEM>_v([0-9]+)_([0-9]{4}-[0-9]{2}-[0-9]{2})\.md$` with backslash-free `<STEM>_v<N>_<YYYY-MM-DD>.md` (excluding `_response_` files) ordered by highest `(int(N), YYYY-MM-DD)`, and aligned `plugins/arch-compliance/skills/adversarial-design-review/SKILL.md:128-131` (Step 2b-ii) to the same `(int(N), <date>)` rule.
     - Added `Name LIKE|127\.0\.0\.1` to §4.1 Recipe B so lines `:133` and `:143` of `hm:.claude/skills/post-merge-housekeeping/SKILL.md` are matched by Recipe B (18 additional lines, 25 total across Recipes A and B) and listed in §4.2 row 3.
- **Falsification command and output:**

```text
$ python -c "
from pathlib import Path
import re
repo = Path('.')
rd = (repo / 'plugins/arch-compliance/python/acf/adr/run_detail.py').read_text(encoding='utf-8').splitlines()
print('run_detail.py:42:', rd[41])
print('run_detail.py:43:', rd[42])
print('run_detail.py:84:', rd[83])
resp = (repo / 'plugins/arch-compliance/skills/responding-to-adversarial-review/SKILL.md').read_text(encoding='utf-8').splitlines()
print('responding/SKILL.md:133:', resp[132])
adr = (repo / 'plugins/arch-compliance/skills/adversarial-design-review/SKILL.md').read_text(encoding='utf-8').splitlines()
print('adr/SKILL.md:134:', adr[133])
spec = (repo / 'docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md').read_text(encoding='utf-8').splitlines()
pat = re.compile(r'run_detail\.py:47|:110[^-]|\\\\\.md\$|int\(version\)|23 lines|16 additional|16 lines')
print('stale hits in spec:', [i for i, l in enumerate(spec, 1) if pat.search(l)])
"
run_detail.py:42:     stem = Path(spec_path).stem
run_detail.py:43:     return Path(runs_dir) / f"{stem}_v{version}_{date}.md"
run_detail.py:84:         f"Spec: `{run.spec_path}` @ `{run.commit_sha}`",
responding/SKILL.md:133: the declared `runs_dir` as `<SPEC_STEM>_v<N>_response_<date>.md` (N = the blocked version
adr/SKILL.md:134:   named `<SPEC_STEM>_v<N>_response_<date>.md` (`N` = the blocked
stale hits in spec: []
```

## Sentence-type sweep

| # | Refutation-prone type | Hits in `docs/design/POST_MERGE_HOUSEKEEPING_SKILL.md` | Disposition |
|---|---|---|---|
| T1 | Population/consumer claim without a recipe | `post-merge process` occurrences across `plugins/arch-compliance/skills/` (§1 item 1, §5.3.1, Appendix `:276`) | Backed by `git grep -n "post-merge process" -- plugins/arch-compliance/skills/`, verified across all 15 Markdown files under `plugins/arch-compliance/skills/` (`C17` `SURVIVED`) |
| T2 | Aggregate count or partition as a claim | 25 origin-host lines in `hm:.claude/skills/post-merge-housekeeping/SKILL.md` (§4.1, §4.2, §6, Appendix `:275`) | Backed by §4.1 Recipe A (7 lines) + Recipe B (18 additional lines) and the full per-line disposition table in §4.2 |
| T3 | Universally quantified claim | `FORBIDDEN` origin-host vocabulary check (§1 item 3, §5.3.3, §5.4.1) | Explicitly scoped to the enumerated `FORBIDDEN` list of known origin-host (`HistoricMansions`) vocabulary per `## No completeness claims` (`C12` `SURVIVED`) |
| T4 | Prose-only measurement of tool/library behavior | `ast.parse` on fenced Python blocks and installed-skill byte comparison (§5.3.2, §5.4) | Pinned by in-tree tests `plugins/arch-compliance/tests/test_adr_skill_prose.py`, `plugins/arch-compliance/tests/test_adr_skill_invariants.py`, and `tests/test_check_installed_skills.py` (`C18` `SURVIVED`) |
| T5 | Named hook/method/attribute without an existence receipt | `ADR_REL`, `ARCH_REL`, `resolve_repo`, `load_host_config`, `LedgerAmendment`, `append_amendment`, `run_detail_path`, `GATE_SKILLS` | Every symbol carries its exact `file:line` receipt in `plugins/arch-compliance/python/acf/` or `scripts/check_installed_skills.py:18`, verified at `:42-43, :84` of `run_detail.py` |
| T6 | Mandate/doc attribution without the quoted trigger | `## Declared, never defaulted`, `## One owner for host paths`, `## Single point of definition`, `## Prose names no host`, `## Frozen ledger format`, `## One base exception`, `## Release discipline` | Every governing section is cited with its line range at `:8` and quoted or stated adjacent to the inference in §2, §5.2, and §5.3 (`C9..C14` all `SURVIVED`) |
| T7 | Completeness claim backed only by a recipe validated on known sites | None; no universal completeness claim is made | §4.2 claims disposition of the lines selected by §4.1 Recipes A and B, and §5.4.1 scopes `FORBIDDEN` to the enumerated list |
