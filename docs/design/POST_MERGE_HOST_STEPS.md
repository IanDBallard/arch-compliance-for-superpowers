# Host Pre-flight Checks, Plan Record and Host Steps for `post-merge-housekeeping`

**Status:** v1 — draft for `/arch-compliance:adversarial-design-review`.
**Spec kinds:** `feature`
**Repo:** `IanDBallard/arch-compliance-for-superpowers`, `main` at `e9dd881` (release 0.3.2).
**Workstream:** HistoricMansions Workstream E, host roll-out step R5. Closes issue #50. A host
with a richer post-merge procedure than the portable skill can then cut over to it without
dropping steps.
**Governing mandates:** `config/architecture/ARCHITECTURE.md` sections `## Declared, never
defaulted` (`:189-216`), `## Prose names no host` (`:218-228`), `## No completeness claims`
(`:244-254`), `## Release discipline` (`:269-279`), `## Single point of definition`
(`:281-298`) and `## Post-merge` (`:319-328`).
**No state-machine surface.** The design adds or modifies no state machine and no
transition.

---

## 0. Citation convention

Unprefixed paths are this repository at `e9dd881`. Paths prefixed `cy:` are the sibling
repository `IanDBallard/Cayenne` at `fffc2954` (`main`). They are cited here as the live
instance that motivates the design. No step of the design reads or writes them. The rules
relied on are quoted beside each citation.

---

## 1. Goal

`plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md` reads a host's
operational conventions from the `## Post-merge` section of the host's doctrine. The
skill's overview names four of them (`SKILL.md:20-24`): "shared-checkout branch lock,
worktree daemon probe, post-merge CI workflows, and durable tracking target". Step 5 also
reads "any non-Markdown tracking files declared under `## Post-merge`" (`SKILL.md:244-245`).
A host can declare *values* for those checks. It cannot declare:

1. **A check the skill must run before its first step.** Example: Cayenne's "Whether
   someone is already closing these books. Check this first, before writing a line"
   (`cy:.claude/skills/post-merge-housekeeping/SKILL.md:21-28`, written after two sessions
   opened competing housekeeping pull requests, Cayenne #60 and #61). Its other checks of
   this kind are that the merge's base is `main` (`:31-35`) and that any cross-repository
   twin pull request has also merged (`:38-40`).
2. **A plan-record convention that differs from step 4.** Step 4 says "open the plan,
   tick every completed step `[x]`, and add a merge annotation" (`SKILL.md:235-236`).
   Cayenne's rule is the opposite: "**Do not tick the checkboxes.** Where rulings amended
   steps during execution, ticking them asserts a history nobody verified; the header
   carries the truth instead" (`cy:...SKILL.md:65-66`).
3. **A host step with its own rules.** Examples: closing `F-###` items in
   `cy:SpecificationDocumentation/FIX_ROADMAP.md` against the diff (`cy:...SKILL.md:76-83`);
   taking the next free `F-###` across `main` and every open pull request (`:181-201`);
   marking in-app bug reports fixed, which emails each tester and so must run only after
   the deploy is verified live (`:117-129`).
4. **The host's report fields.** Cayenne's report has `Gate:` and `Fixes:` lines
   (`cy:...SKILL.md:214-223`) that step 8's one-or-two-sentence report does not carry.

So a host whose procedure needs any of these must keep a local copy of the skill. That
leaves two live copies, which the workstream's strangler rule forbids, or a cutover that
silently drops the steps. This design adds four optional sub-sections to `## Post-merge`:
`### Pre-flight`, `### Plan record`, `### Host steps` and `### Report`. The portable
skill reads them and runs, applies or reports each one.

---

## 2. Decisions this design records

1. **Prose, not a parser.** The skill already reads `## Post-merge` as prose that the agent
   interprets (`SKILL.md:20-24`, `:62-64`, `:123-126`, `:180-184`, `:244-245`,
   `:262-266`). The four sub-sections are read the same way. No Python model, loader or
   test fixture parses `## Post-merge`, and none is added. (author's call)
2. **Declared, never defaulted.** An absent sub-section means no host checks, no override
   or no host steps. As with the existing checks, step 8 reports it as `<sub-section>: not
   declared in ## Post-merge, skipped`. The skill never invents a host step. (follows
   `## Declared, never defaulted`)
3. **A pre-flight check can stop the run, and a host step cannot skip a portable step.**
   A pre-flight check whose declared stop condition holds ends the run before step 0, and
   the check's own text says what to do instead. Host steps run after step 6.5 and before
   step 7. They add work; they never replace or reorder steps 0–6.5. The one portable
   behaviour a host may replace is step 4's tick rule, through `### Plan record`. (author's
   call)
4. **Host steps keep their own preconditions.** A host step may name a precondition (for
   example "only after the deploy declared under post-merge CI is verified live"). The
   skill checks the precondition and records an unmet one as `<host step>: precondition
   unmet (<what>), not run` in step 8. It never runs the step anyway. (author's call)
5. **One release.** The skill text, its invariant test and the version bump to 0.3.3 land
   together, as `## Release discipline` requires: "A change to a skill's prose bumps the
   plugin version" (`config/architecture/ARCHITECTURE.md:271-272`). (follows the mandate)

---

## 3. Non-goals

- Cayenne's cutover: its `## Post-merge` section and the deletion of
  `cy:.claude/skills/post-merge-housekeeping/` are a Cayenne adoption plan once this
  release ships. The same goes for HistoricMansions' cutover (its roadmap's
  `post-merge-housekeeping` row).
- No change to steps 0–3.5, 5, 6, 6.5 or 7 beyond the sentences that hand off to the new
  sub-sections.
- No Python change. `acf.repo.ARCH_REL` already names the doctrine file the skill reads
  (`plugins/arch-compliance/python/acf/repo.py`). Nothing else in the package reads
  `## Post-merge`. The recipe for that claim is in §6.
- No host vocabulary in the skill. Every example in the new prose is generic, as
  `## Prose names no host` requires: "Skill prose and runtime messages name no host
  repository, path or section" (`config/architecture/ARCHITECTURE.md:220-221`).

---

## 4. Design

### 4.1 The sub-sections a host may declare

Under its `## Post-merge` heading, a host may add these `###` sub-sections, each optional:

| Sub-section | What it holds | When the skill uses it |
|---|---|---|
| `### Pre-flight` | An ordered list of checks. Each says what to read and what result stops the run, and what to do then | Before step 0. Each check runs in order; the first whose stop condition holds ends the run |
| `### Plan record` | The host's rule for recording a merged plan's status (for example "a status header only; do not tick checkboxes") | In step 4, in place of "tick every completed step" |
| `### Host steps` | An ordered list of named steps, each with its action, its optional precondition and what to report | After step 6.5, before step 7 |
| `### Report` | Extra fields step 8's report must carry (for example a gate line and a fixes line) | In step 8, appended to the one-or-two-sentence report |

The four existing declarations stay bullets in the section body, as this repository's own
`## Post-merge` writes them (`config/architecture/ARCHITECTURE.md:321-326`). So does
step 5's non-Markdown tracking files.

### 4.2 `plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md`

- **Overview** (`:16-24`): after the four declared conventions, add one sentence naming the
  four sub-sections and pointing to a new `## Host sub-sections` section.
- **New `## Host sub-sections`** (placed before `## The Checklist`): §4.1's table and
  decisions 2–4, written generically.
- **New step `### -1. Host pre-flight checks`** before step 0. Read `### Pre-flight` under
  the host's `## Post-merge`. If it is absent, record `pre-flight: not declared in
  ## Post-merge, skipped` for step 8. Otherwise run each check in order and stop on the
  first whose stop condition holds, saying which one stopped and what it says to do.
  Pre-flight checks are reads, like steps 1–2: they run before any teardown and never
  touch the main checkout.
- **Step 4** (`:233-239`): prefix "If the host declares `### Plan record` under
  `## Post-merge`, apply it instead of the tick rule below, and record that you did."
  The rest of step 4 is unchanged for hosts that declare no override.
- **New step `### 6.7 Host steps`** between 6.5 and 7. Read `### Host steps`. If it is
  absent, record `host steps: not declared in ## Post-merge, skipped`. Otherwise run each
  in order. Check each one's precondition first. An unmet precondition is recorded as
  `<host step>: precondition unmet (<what>), not run`, never run around. A step that fails
  is reported, and the remaining steps still run. Host steps run in the main session, with
  no subagents in flight, like everything from step 3.5 on (`SKILL.md:38-42`).
- **Step 8** (`:372-377`): add "and every field the host's `### Report` declares, or
  `report: not declared in ## Post-merge, skipped`".
- **`## When NOT to use`** and **Rationalizations**: one row, "A host step looks redundant
  with a portable step, so skip it | It is there because the portable step missed
  something on that host. Run both; report both."

### 4.3 Tests

`plugins/arch-compliance/tests/test_adr_skill_invariants.py::test_housekeeping_skill_invariants`
(`:105-133`) gains these required strings: `### Pre-flight`, `### Plan record`,
`### Host steps`, `### Report`, `pre-flight: not declared in ## Post-merge, skipped`,
`host steps: not declared in ## Post-merge, skipped`, and `precondition unmet`. They join
the existing `"## Post-merge"` and `"not declared in ## Post-merge, skipped"` pins
(`:117-118`).

`plugins/arch-compliance/tests/test_adr_skill_prose.py` already scans this skill against
`FORBIDDEN` (`HOUSEKEEPING`, `:14`). No change is needed. The new prose must pass it.

### 4.4 Doctrine, version, installed-skills check

- `config/architecture/ARCHITECTURE.md` `## Post-merge` (`:319-328`): add one line saying
  this repository declares no `### Pre-flight`, `### Plan record`, `### Host steps` or
  `### Report`. The skill's own host then reports them as not declared, not as missing.
- `plugins/arch-compliance/.claude-plugin/plugin.json` and `pyproject.toml`: `0.3.2` →
  `0.3.3`.
- `scripts/check_installed_skills.py` already byte-checks `post-merge-housekeeping`
  (`config/architecture/ARCHITECTURE.md:273-275`). No change.

---

## 5. Shape fit

**What existing shape does this extend?** The host declaration in `## Post-merge`. The
skill already reads four host values and a list of tracking files from it, reports an
absent one as "not declared … skipped", and never defaults one (`SKILL.md:20-24`, `:62-64`,
`:123-126`, `:180-184`, `:244-245`, `:262-266`). The four sub-sections are more
declarations in the same section, read the same way, with the same absent-value report.

**What second way does it create?** None. There is still one place a host declares
post-merge conventions, and one skill that reads it. A host that keeps a local skill
because of these gaps has two live procedures. This design is what removes that second
way.

**Pattern sweep.** §6, recipe B lists every place the skill reads `## Post-merge` today.
Each new reading site is added next to an existing one (overview, step 4, after step 6.5,
step 8), never in a new file.

---

## 6. Premise verification (authoring time, 2026-11-19, at `e9dd881`)

Recipe A, the places in the package that read the doctrine's `## Post-merge`:

```bash
git grep -n "Post-merge" -- plugins/arch-compliance/python plugins/arch-compliance/hooks
```

Output: no lines. Python code does not read the section. This is a negative from one
method. Recipe B is the second method: it shows the readers are skill prose.

Recipe B, the places in the skill that read it:

```bash
git grep -n "Post-merge" -- plugins/arch-compliance/skills/post-merge-housekeeping/SKILL.md
```

Output: lines 22, 23, 24, 63, 64, 117 (heading text "Post-merge CI check"), 123, 125,
180, 183, 245, 263, 264, 350, 376 and 413. Each is a prose instruction or a report string. The
sub-section handoffs in §4.2 go next to lines 22, 233 (step 4), 350 (end of step 6.5) and
376.

Recipe C, the test pins:

```bash
git grep -n "Post-merge" -- plugins/arch-compliance/tests
```

Output: `test_adr_skill_invariants.py:117-118`. These are the two strings §4.3 adds to.

---

## 7. Definition of done

1. `SKILL.md` carries `## Host sub-sections`, step `-1`, the step 4 override sentence,
   step `6.7` and the step 8 report clause, as §4.2 states. The new prose contains no
   `FORBIDDEN` vocabulary.
2. `test_housekeeping_skill_invariants` pins the seven strings in §4.3 and passes. The
   rest of the suite passes too: `pytest -q` from the repository root.
3. `config/architecture/ARCHITECTURE.md` `## Post-merge` carries the one-line "declares
   none" note (§4.4).
4. The version is `0.3.3` in `plugin.json` and `pyproject.toml`.
5. After the merge, the plugin is reinstalled and `scripts/check_installed_skills.py`
   reports the installed copy identical to the clone.
6. The PR body names issue #50 as closed. It also names the Cayenne and HistoricMansions
   cutovers as adoption work this release unblocks, filed in HistoricMansions' workstream
   E table (R5) and its `post-merge-housekeeping` cutover row.

---

## 8. Risks

| Risk | Mitigation |
|---|---|
| A host writes a host step that duplicates or contradicts a portable step | Decision 3: host steps add work and never replace a portable step. Step 8 reports both. Only step 4's tick rule is overridable, and only explicitly |
| A pre-flight check stops a run that should have continued | The check's own text says what to do instead. The run is read-only up to that point, so nothing is half done |
| A side-effecting host step (one that emails users) runs before its precondition holds | Decision 4: the skill checks a declared precondition and records an unmet one as not run. A host that omits the precondition owns that choice in its doctrine |
| The prose grows the skill past easy reading | §4.2 adds one section and two short steps. The sub-section table is the single statement, and the steps point to it |
