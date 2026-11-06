# The Adversarial-Design-Review Gate's Host Contract

> **Provenance.** Moved from `HistoricMansionsV3/docs/design/ADR_GATE_HOST_CONTRACT.md`
> at HM commit `86f93f95` on 2026-10-24, per its decision 6, by
> `docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md`. Its citation convention is
> unchanged and inverted relative to this repository's: **unprefixed paths are
> HistoricMansions at the commit its §0 names; `acf:` paths are this repository.** Its
> ledger records stay in HM's ledger under the HM path.

**Status:** v4 — approved by user override; next: `writing-plans`.
**Adversarial review:** v4 — 2026-10-12, user override after the v3 full run (BLOCKED; five load-bearing completeness claims refuted, the mechanism not attacked; all five and the converged finding absorbed and re-measured against the tree), user-approved (repo @ 2a95b612)
**Spec kinds:** `feature`
**Workstream:** E, phase **1c** (`docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md`,
section *Workstream E — Portable governance skills*).
**Supersedes:** `docs/design/ADR_GATE_PLUGIN_COMPONENT.md` in full. Its run manifest,
ledger record schema and command surface leave scope; its host contract is replaced
by this document. `docs/design/ADR_GATE_HM_ADOPTION.md` is not superseded: it is
phase 1d's input and is re-derived against this document's outcome when 1d starts.
**Governing mandates:** GEMINI.md §1 items 7–8 (shape fit; this gate), §2 (code review
for a public interface), §3 (fail loud), §4 (no shims), §7 (single point of definition;
Pydantic for configuration), §10 (POSIX paths). In the plugin, its *Governing
principles (portable)* at `acf:docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:43-52`:
1 (fail loud; no silent empty defaults for config load); 2 ("No shims — one registry
façade; one finding schema; do not dual-run parallel mandate lists"); 3 (POSIX paths);
4 ("Registry is the spine — prose anchors, detectors, auditors, and call sites must
agree or tests fail"); 5 (the Superpowers override contract — "document that
explicitly"). The design runs against principles 2 and 4 on purpose for one
responsibility: the compliance reviewer takes its mandates from host doctrine, not
from the registry. That is declared debt (§6), approved by decision 1, and reconciling
the two is phase 2's registry work. Principle 5 is met by the plugin README naming the
gate as an override of Superpowers' brainstorming → writing-plans flow (§7, DoD 10).
**No state-machine surface.** The design adds or changes no state and no transition.

## 0. Citation convention

This spec spans two repositories, at fixed commits:

| Prefix | Tree | Commit |
|---|---|---|
| *(none)* | HistoricMansions, this checkout | `9bbfd563` |
| `acf:` | `IanDBallard/arch-compliance-for-superpowers`, a separate clone | `277bcca4` |

Paths are written in full; the six basenames below appear bare only in this
paragraph. Those six module basenames now exist in **both** trees (`ledger.py`,
`contract.py`, `gate.py`, `citations.py`, `run_detail.py`, `rollup.py`), because phase
1b ported `scripts/core/adversarial_design/` to
`acf:plugins/arch-compliance/python/acf/adr/`. A bare basename is ambiguous and is not
used.

## 1. Goal

The gate's Python package already lives in the plugin (phase 1b). Its **skill prose**
does not, because the prose names this repository's paths, doctrine documents and
mandate checklist. After this phase the two skills — `adversarial-design-review` and
`responding-to-adversarial-review` — live in the plugin. They read the host's two
storage locations from one declared, validated file, and the host's doctrine from the
one doctrine path the plugin already defines. A repository other than this one can
then run the gate against its own layout and its own doctrine.

This repository is **not changed** by this phase. It keeps running its local copies
until phase 1d writes its declaration, installs the plugin and deletes them.

## 2. Decisions this design records (user, 2026-10-12)

Inputs, not tree-derivable claims:

1. **The compliance reviewer's repository-specific mandate checklist leaves the
   plugin prompt.** The prompt keeps the generic instruction; a host supplies its own
   checklist as doctrine content (§5.4). Reading the ACF mandate registry instead was
   not chosen: it would couple this phase to the registry-schema reconciliation that
   blocks phase 2.
2. **The declaration is one file, `config/architecture/adr.yml`, loaded through the
   plugin's existing loader.** (Chosen over an `adr:` block in `mandates.yml` and over
   per-run arguments.)
3. **This phase is plugin-only.** The prose moves into the plugin here; this
   repository writes its declaration and deletes its copies in 1d.
4. **The two defaults that phase 1b ported verbatim are deleted**, not kept as
   fallbacks.
5. **The doctrine is read from the plugin's single doctrine path,
   `config/architecture/ARCHITECTURE.md`, and from every document it points to.** No
   doctrine field is declared. A host whose doctrine lives elsewhere writes that file
   as a pointer; this repository does so in 1d, naming `GEMINI.md`, `CLAUDE.md` and its
   checklist. A pointer file still carries every heading its mandates' `arch_anchor`
   values name, because the plugin matches those as literal substrings of this file
   (`acf:plugins/arch-compliance/skills/acf-mandate/SKILL.md:104`; enforced for profiles
   by `acf:plugins/arch-compliance/tests/test_profile_drift.py:31`).
6. **This spec stays in this repository until 1d, and moves to the plugin repository
   after 1d's acceptance run.**
7. **Acceptance in this phase is an automated fixture-host test.** The first live gate
   run from the plugin is 1d's: this repository on its own declaration, then a second
   repository (the workstream's exit criterion 5).

## 3. Non-goals

- **The ledger record format.** Unchanged, byte for byte, including the
  `TouchedSurface` vocabulary at `acf:plugins/arch-compliance/python/acf/adr/ledger.py:58-61`
  (`facade`, `persistence_format`, `hfsm`, `metadata_facade`, `public_interface`, `ui`,
  `none`). A host without the first five surfaces records `none` or `ui`. Freeing the
  vocabulary reopens the persisted format, which is the filed ledger-schema follow-up.
- **A command-line surface, a run manifest, a schema version.** The prose calls the
  package's functions directly, as it does today.
- **Writing `adr.yml` from `/acf-setup`.** A host authors the two-line file; a missing
  file is refused with its path named (§5.6). Extending the setup skill is a follow-up,
  not a precondition: no host runs the plugin's gate before 1d.
- **What the constraints hook injects.** The hook injects the text of
  `config/architecture/ARCHITECTURE.md`, truncated, and follows no pointers
  (`acf:plugins/arch-compliance/hooks/inject_constraints.py:167-170`). For a host whose
  doctrine file is a pointer, subagents receive the pointer text. The hook runs only
  where `.acf/enabled` exists, which this repository does not have; whether this
  repository's `ARCHITECTURE.md` is a pointer or an excerpt is 1d's decision, filed as
  declared debt (§6). This phase changes only the hook's doctrine *refusal* (§5.2).
- **The plugin's `architecture-review` skill's own report paths.** It names
  `docs/architecture/` locations in its prose
  (`acf:plugins/arch-compliance/skills/architecture-review/SKILL.md:118`). Whether
  `adr.yml` becomes a plugin-wide host-layout declaration belongs to phase 2, with that
  skill.
- **This repository's cutover**: its `adr.yml`, its pointer `ARCHITECTURE.md`, its
  checklist document, deleting `.claude/skills/adversarial-design-review/`,
  `.claude/skills/responding-to-adversarial-review/`, their `.cursor/skills/` mirrors
  and `scripts/core/adversarial_design/`, and updating the exception-name list at
  `scripts/ci/arch_compliance/engine.py:905-909`. All phase 1d.
- **`docs/architecture/SKILL_PROVENANCE.md`.** It stays in this repository. It also
  holds the provenance of `post-merge-housekeeping` (heading at
  `docs/architecture/SKILL_PROVENANCE.md:205`), which is not moving. The moved prose
  drops its pointers to it (§4.2); whether 1d copies the two skills' sections into the
  plugin repository is 1d's decision.
- **Cursor packaging of the moved skills.** This repository's dual-tree invariant
  (`scripts/core/skill_install.py`, asserted by
  `tests/test_adversarial_design_skill_install.py`) is a property of this host and is
  settled in 1d.
- **The plugin's `architecture-review` skill and the mandate registry.** Phase 2.

## 4. What the prose hardcodes today

### 4.1 Census of host-specific lines in the files that move

Seven files move:
`.claude/skills/adversarial-design-review/{SKILL.md, claims/extraction.md, reviewers/compliance.md, reviewers/hardening.md, reviewers/refuter.md, reviewers/sweeper.md}`
and `.claude/skills/responding-to-adversarial-review/SKILL.md`. Two recipes, run from
`.claude/skills/`:

```bash
# A — names: path roots, doctrine names, the old import path, and the two package
#     constants that carry a host path by indirection
grep -rnE "GEMINI|CLAUDE\.md|docs/design|docs/reviews|docs/architecture|scripts\.core|scripts/|SKILL_PROVENANCE|§[0-9]|HistoricMansions|book root|index\.yml|LEDGER_PATH|RUNS_DIR" \
  adversarial-design-review responding-to-adversarial-review
# B — behaviour: this repository's concepts, tools and layout, by vocabulary
grep -rniE "\.cursor|cursor|\.claude/|install|book|admin|cms|hfsm|facade|façade|index\.yml|style\.yml|pdf|epub|latex|pandoc|zotero|oakville|mansion|drive|worktree|config/|tests/|scripts|stage 1|family|ruamel|book_root" \
  adversarial-design-review responding-to-adversarial-review
```

Recipe B was validated against three sites recipe A cannot see — the install block at
`adversarial-design-review/SKILL.md:14-16`, the same block at
`responding-to-adversarial-review/SKILL.md:17-19`, and the `book_order` example at
`adversarial-design-review/reviewers/hardening.md:62` — and returns all three.

Two further recipes cover what a vocabulary net cannot: the skills the prose hands
work to, and host references in the plugin code the moved prose runs.

```bash
# C — skills the prose names (run from .claude/skills/)
grep -rnoE "post-merge-housekeeping|superpowers:[a-z-]+|writing-plans|brainstorming|receiving-code-review|dispatching-parallel-agents|finishing-a-development-branch" \
  adversarial-design-review responding-to-adversarial-review
# D1 — host references in the plugin's code: doctrine names, section numbers, this
#      repository's paths and vocabulary (run in the plugin clone)
git grep -n "GEMINI\|scripts\.core\|HistoricMansions\|§[0-9]\|scripts/\|book" -- \
  plugins/arch-compliance/python plugins/arch-compliance/hooks
# D2 — doctrine references in the plugin's tests (their path strings are fixtures)
git grep -n "GEMINI\|scripts\.core\|HistoricMansions" -- plugins/arch-compliance/tests
```

Recipe C's hits split into Superpowers skills, which the plugin already requires
(`acf:README.md:9`, "**Superpowers** installed first"), and `post-merge-housekeeping`, a
skill only this repository has. Recipe D's hits are dispositioned in §4.2's last rows;
two of them are runtime strings a host sees (`acf:plugins/arch-compliance/python/acf/adr/parser.py:97`,
`acf:plugins/arch-compliance/python/acf/adr/gate.py:280`), and the rest are comments, docstrings and test text.
All four recipes are pattern nets; the plan reads each moved file end to end against
§4.2 (Risks).

### 4.2 Disposition, line by line

Paths are relative to `.claude/skills/`. Each line either recipe selects appears in a
row; `adversarial-design-review/SKILL.md:302` and
`responding-to-adversarial-review/SKILL.md:224` each carry two host values and appear in
both rows that apply.

| Lines | What they carry | Disposition |
|---|---|---|
| `adversarial-design-review/SKILL.md:51, 69, 75, 160, 222, 237, 246, 258, 276, 288, 302, 328` | Old import path `scripts.core.adversarial_design` / `scripts.core.exceptions` | `acf.adr` / `acf.exceptions` |
| `adversarial-design-review/SKILL.md:3` | Description: "against a committed docs/design/*.md" and "per GEMINI.md §1 item 8" | "against a committed spec"; the clause becomes "where the host's doctrine requires it" |
| `adversarial-design-review/SKILL.md:22` | Invocation example `<docs/design/TOPIC.md>` | `<path/to/SPEC.md>` |
| `adversarial-design-review/SKILL.md:126, 131, 293`; `responding-to-adversarial-review/SKILL.md:110, 201` | Run-detail directory `docs/reviews/adr_runs/` | "the declared `runs_dir`" |
| `adversarial-design-review/SKILL.md:302, 320` | Ledger path via `LEDGER_PATH` | `repo / cfg.ledger_path` (§5.4); the constant is deleted (§5.3) |
| `responding-to-adversarial-review/SKILL.md:51, 170` | Ledger path inline in two `python -c` bodies | Each body loads `cfg` and opens `repo / cfg.ledger_path` |
| `adversarial-design-review/reviewers/compliance.md:3, 12, 28, 44, 50, 127`; `adversarial-design-review/claims/extraction.md:30` | `GEMINI.md` as the document to read | "the doctrine document and every document it points to" (§5.4) |
| `adversarial-design-review/reviewers/compliance.md:16-19, 37-38, 54, 56-78, 93` | The repository-specific checklist: four architecture documents to read, the §3–§14 trigger list and its header ("The high-frequency misses in this repo:"), and examples naming its sections | Removed from the plugin prompt. This repository's checklist document holds them verbatim in 1d, reached through its pointer doctrine |
| `adversarial-design-review/SKILL.md:347-349` | `filter_would_skip`'s surface list, with "That list is GEMINI.md §1 item 8's future trigger list; change both together" | The list stays. The obligation is re-pointed inside the plugin: "change it together with `TouchedSurface`" (`acf:plugins/arch-compliance/python/acf/adr/ledger.py:58-61`), the persisted vocabulary it is a subset of |
| `acf:plugins/arch-compliance/python/acf/adr/ledger.py:52-56` | Comment: `TouchedSurface` "Must stay in step with GEMINI.md item 8's trigger list" | Comment rewritten to name `filter_would_skip`'s list in the skill as its partner. Comment only; no code change |
| `adversarial-design-review/SKILL.md:426` | "(GEMINI.md §1 item 8)" after the re-run-scope rule, which the paragraph states in full | Citation removed; the rule text stays and the plugin skill owns it |
| `adversarial-design-review/SKILL.md:474`; `responding-to-adversarial-review/SKILL.md:205, 222` | "Diagnosis lives in GEMINI.md §1 item 7" — a delegation, not a stated rule | "Diagnosis belongs to the host's doctrine, not to this gate" |
| `adversarial-design-review/reviewers/hardening.md:81, 83` | "(§3)" and "(§4)" after the fail-loud and no-shims rungs | "(fail loud)" and "(no shims)" |
| `adversarial-design-review/reviewers/sweeper.md:35` | "(§1.7: every exclusion justified)" | "(every exclusion justified)" |
| `responding-to-adversarial-review/SKILL.md:37` | "The pass is defined in `CLAUDE.md`" | "re-run the host's design-simplification pass, if its doctrine defines one" |
| `adversarial-design-review/reviewers/sweeper.md:13, 43` | Corpus roots `scripts/`, `admin/`, `docs/design/`, `docs/architecture/` | "the tracked tree — code and documents alike — **excluding** the directories that contain the declared `runs_dir` and `ledger_path`". Those directories hold prior verdicts, and in this repository also the roadmap that records them in prose (both live under `docs/reviews/`, which the current roots already leave out); a blind reviewer must not read them (`adversarial-design-review/SKILL.md:428-429`, "reviewers must be blind to prior verdicts or they anchor"). The controller passes the two excluded directories to the sweeper in its dispatch, alongside the citation map it already passes |
| `adversarial-design-review/SKILL.md:11, 455`; `responding-to-adversarial-review/SKILL.md:15, 224, 225` | Pointers to `docs/architecture/SKILL_PROVENANCE.md` | Removed (§3) |
| `adversarial-design-review/SKILL.md:14-18`; `responding-to-adversarial-review/SKILL.md:17-19` | The dual-tree *Install* block and its `scripts.core.skill_install` verifier | Removed: the plugin ships one copy |
| `adversarial-design-review/SKILL.md:97` ("live book roots"), `:163` (`scripts/x.py:12`); `adversarial-design-review/reviewers/refuter.md:74` ("under `scripts/`"); `adversarial-design-review/reviewers/sweeper.md:144` (`docs/design/SOME_DOC.md`); `adversarial-design-review/reviewers/hardening.md:62` (`book_order`); `responding-to-adversarial-review/SKILL.md:91-92` (`scripts/`, `tests/`, `config/`, `docs/`) | Examples naming this repository's layout or data | Neutral examples: "absolute paths outside the repository", `src/x.py:12`, "anywhere in the tree", `docs/SOME_DOC.md`, "rows whose `position` has gaps", "the tracked tree" |
| `adversarial-design-review/SKILL.md:336, 338-339`; `adversarial-design-review/reviewers/hardening.md:80` | `touched_surfaces` vocabulary and a "façade" example | Kept: the vocabulary is the persisted one (§3); "façade" is generic |
| `responding-to-adversarial-review/SKILL.md:27, 81, 104, 120, 176, 189, 200, 224` | The skill's own section references `§2`/`§3`/`§4` (its headings at `:59`, `:98`, `:162`) | Kept unchanged |
| `adversarial-design-review/SKILL.md:39, 162, 168, 200, 381`; `adversarial-design-review/claims/extraction.md:24, 93`; `adversarial-design-review/reviewers/hardening.md:22, 39, 43`; `responding-to-adversarial-review/SKILL.md:192` | Recipe-B vocabulary used generically ("family", "worktree", "bookkeeping") | Kept unchanged |
| `adversarial-design-review/SKILL.md:72-73` | `classify_citations(cited, repo_root=Path("."), …)` and `unresolved_citations(…, repo_root=Path("."), …)` | `repo_root=repo` (§5.4) |
| `adversarial-design-review/SKILL.md:289` | `run_detail_path(spec_path, version=N, date=today_iso)`, which relies on the deleted default | `run_detail_path(spec_path, version=N, date=today_iso, runs_dir=repo / cfg.runs_dir)` |
| `adversarial-design-review/SKILL.md:361`; `responding-to-adversarial-review/SKILL.md:196` | The ledger amendments are owed by `post-merge-housekeeping`, a skill only this repository has (recipe C) | "by the host's post-merge process" — the obligation stays, its owner becomes the host's |
| `responding-to-adversarial-review/SKILL.md:206-208` | "Two recurring probes that item already carries: …" — a paraphrase of this repository's diagnosis rule | Removed with the delegation at `:205` it continues |
| `adversarial-design-review/SKILL.md:195, 369, 388, 397`; `responding-to-adversarial-review/SKILL.md:195, 223` (recipe C) | Superpowers skills: `superpowers:dispatching-parallel-agents`, `writing-plans`, `superpowers:receiving-code-review` | Kept: the plugin requires Superpowers (`acf:README.md:9`) |
| `acf:plugins/arch-compliance/python/acf/adr/parser.py:97` (recipe D1) | Runtime hint "every path field must be POSIX (no backslashes) — GEMINI.md §10." shown to every host | The doctrine reference is dropped: "every path field must be POSIX (no backslashes)." |
| `acf:plugins/arch-compliance/python/acf/adr/gate.py:280` (recipe D1) | Runtime absorption message ending "presumptively papering over the crack (§1.7)", shown to every host | The section reference is dropped |
| `acf:plugins/arch-compliance/python/acf/adr/contract.py:7, 8, 61, 67, 76, 78, 83, 162`; `acf:plugins/arch-compliance/python/acf/adr/convergence.py:17, 31`; `acf:plugins/arch-compliance/python/acf/adr/gate.py:43, 44, 49, 93, 189, 276`; `acf:plugins/arch-compliance/python/acf/adr/ledger.py:70, 71, 116, 179, 202`; `acf:plugins/arch-compliance/python/acf/adr/parser.py:6`; `acf:plugins/arch-compliance/python/acf/adr/rollup.py:49`; `acf:plugins/arch-compliance/python/acf/adr/run_detail.py:9, 16`; `acf:plugins/arch-compliance/python/acf/adr/citations.py:10, 16, 116, 117, 151, 157, 174, 175` (recipe D1) | Comments and docstrings citing this repository's section numbers (`§3`, `§7`, `§10`, `§14`, `§1.7`), its doctrine, its module paths, or its incidents and data (book roots, `check_book_tier_drift.py`) | Rewritten: a section number becomes the principle's name (fail loud, one point of definition, POSIX paths); host paths and incidents become neutral examples or are removed. No behaviour change |
| `acf:plugins/arch-compliance/tests/test_adr_contract.py:1`; `acf:plugins/arch-compliance/tests/test_adr_ledger.py:141` (recipe D2) | Test docstring and comment citing `GEMINI.md` | Rewritten the same way |
| `acf:plugins/arch-compliance/tests/test_adr_contract.py:62`; `acf:plugins/arch-compliance/tests/test_adr_ledger.py:588` (recipe D2) | Test data: a Windows path as backslash input, and the provenance of a real ledger row | Kept: fixtures, not host references |
| `acf:plugins/arch-compliance/python/acf/judge.py:32, 52, 64, 110`; `acf:plugins/arch-compliance/tests/test_judge.py:49, 58` (recipes D1, D2) | `GEMINI_API_KEY` and the Gemini API URL — the LLM judge's model provider | Kept: unrelated to this repository's `GEMINI.md` |

### 4.3 The prose's Python

`adversarial-design-review/SKILL.md` holds ten fenced ```` ```python ```` blocks
(opening at `:50, 67, 159, 221, 236, 245, 257, 275, 286, 300`);
`responding-to-adversarial-review/SKILL.md` holds two `python -c` bodies inside fenced
```` ```bash ```` blocks (`:48-57`, `:167-173`). The block opening at
`adversarial-design-review/SKILL.md:300` uses the character `…` (U+2026) as a bare
placeholder (`:307`, `new_design_elements=…, phases=…, cited_files=…`), which is not
Python. Disposition: inside every fenced ```` ```python ```` block, `…` becomes `...`.
Measured at authoring time: with that substitution all ten blocks and both bodies
parse under `ast.parse`; without it, the `:300` block alone fails.

## 5. Design

### 5.1 The declaration

A new host file, `config/architecture/adr.yml`, beside the mandate registry:

```yaml
runs_dir: reviews/runs
ledger_path: reviews/ledger.jsonl
```

| Field | Required | Must exist at load |
|---|---|---|
| `runs_dir` | yes | no — `write_run_detail` creates its parents |
| `ledger_path` | yes | no — `append_row` creates the file with its preamble |

The doctrine is not declared here: it is `config/architecture/ARCHITECTURE.md`, the
plugin's existing doctrine path (`ARCH_REL`), which must exist at load (§5.2).

### 5.2 The model and its loader

In `acf:plugins/arch-compliance/python/acf/repo.py`, one constant beside its siblings:
`ADR_REL = CONFIG_DIR / "adr.yml"`.

In a new module `acf:plugins/arch-compliance/python/acf/adr/host.py`:

- `AdrHostConfig` — a pydantic model, `extra="forbid"`, both fields typed as the
  package's existing `PosixStr` (`acf:plugins/arch-compliance/python/acf/adr/contract.py:129`,
  `Annotated[str, AfterValidator(_reject_backslash)]`), which refuses a backslash, and
  each declared `Field(min_length=1)` as the package already does for required paths
  (`acf:plugins/arch-compliance/python/acf/adr/contract.py:236`), so an empty value is
  refused at load rather than resolving to the repository root.
- `load_host_config(repo: Path) -> AdrHostConfig` — calls
  `require_file(repo / ARCH_REL, subject="doctrine document")`, then loads
  `repo / ADR_REL` through `acf.loader.load_model_file(..., fmt="yaml")`.

Both are re-exported from `acf.adr`.

**One refusal for an absent doctrine document.** `load_model_file` begins with its own
absent-file check (`acf:plugins/arch-compliance/python/acf/loader.py:51-52`,
`if not path.is_file(): raise AcfInputError(f"{subject} not found: {path.as_posix()}")`).
That check is extracted, unchanged, as `acf.loader.require_file(path: Path, *, subject: str) -> Path`,
and has three callers: `load_model_file` itself, `load_host_config`, and the
constraints hook's doctrine read, which today raises builtin `FileNotFoundError` with
the same message shape (`acf:plugins/arch-compliance/hooks/inject_constraints.py:163-167`).
The hook can call it: its `main()` already imports `AcfInputError` and the pydantic
registry loader after the `.acf/enabled` gate (`:91-92`) and calls `_render_constraints`
afterwards (`:110`). Its `except (FileNotFoundError, OSError)` around that call (`:111`)
gains `AcfInputError`; the message text is unchanged, so
`acf:plugins/arch-compliance/tests/test_hooks.py:253-271` (exit 1, "ARCHITECTURE.md" and
"not found" in stderr) holds as written.

Other absent-file refusals in the plugin keep their own owners, and this design does
not touch them: the two hooks' mandates pre-checks
(`acf:plugins/arch-compliance/hooks/inject_constraints.py:83-88`,
`acf:plugins/arch-compliance/hooks/posttooluse_gate.py:84-89`) run *before* the
third-party import gate, and `acf.loader` imports `yaml` and `pydantic` at module scope,
so they cannot call `require_file`; and `fail_loud_ratchet.load_baseline`
(`acf:plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:77-98`) is a
pre-existing second loader outside this phase.
Not adopted: a refusal of absolute paths or `..` segments in the two fields. Both
writers accept any path (`acf:plugins/arch-compliance/python/acf/adr/run_detail.py:48`
returns `Path(runs_dir) / name`; `acf:plugins/arch-compliance/python/acf/adr/ledger.py:204`
wraps `Path(path)`). A host that declares a location outside its repository gets what
it declared: the gate reads and writes there, and the records are not committed with
the spec. That is a visible host choice, not a state the gate must prevent, and a
refusal would be a second implementation of the repo-relative test that
`acf:plugins/arch-compliance/python/acf/engine.py` (`looks_absolute`) and
`acf:plugins/arch-compliance/python/acf/repo.py` (`RepoTree`) already own.

### 5.3 Deleting the ported defaults

`LEDGER_PATH` (`acf:plugins/arch-compliance/python/acf/adr/ledger.py:34`) and
`RUNS_DIR` (`acf:plugins/arch-compliance/python/acf/adr/run_detail.py:35`) carry this
repository's layout. With a declaration available they are a second source for the
same value, and a host that forgot to declare would write into this repository's paths
without a word. Both are deleted. `run_detail_path`'s `runs_dir` — keyword-only, after
the bare `*` in `def run_detail_path(spec_path: str, *, version: int, date: str, runs_dir: Path | str = RUNS_DIR)`
(`acf:plugins/arch-compliance/python/acf/adr/run_detail.py:38-40`) — loses its default.
`append_row` and `append_amendment` already require their path
(`acf:plugins/arch-compliance/python/acf/adr/ledger.py:226, 235`).

Consumer census, recipe `git grep -n "LEDGER_PATH\|RUNS_DIR"` over the whole plugin
repository at `277bcca4`:

| Site | Kind | Disposition |
|---|---|---|
| `acf:plugins/arch-compliance/python/acf/adr/ledger.py:34` | definition | deleted |
| `acf:plugins/arch-compliance/python/acf/adr/run_detail.py:35` | definition | deleted |
| `acf:plugins/arch-compliance/python/acf/adr/run_detail.py:39` | default argument | removed; parameter required |
| `acf:plugins/arch-compliance/python/acf/adr/__init__.py:19, 36, 48, 51` | re-export, `__all__` | removed |
| `acf:plugins/arch-compliance/tests/test_adr_ledger.py:10, 68` | import, and the sole assertion of `test_ledger_path_is_the_spec_location` (`:67-68`) | import removed; that test deleted |
| `acf:plugins/arch-compliance/tests/test_adr_run_detail.py:31, 100` | import, and one assertion inside `test_detail_path_is_posix_and_lands_under_the_tracked_runs_dir` (`:93-100`), which also pins POSIX output and the file name | import and the `:100` assertion removed; the test and its other pins stay |
| `acf:plugins/arch-compliance/tests/test_adr_import_graph.py:20, 23` | surface pin | names swapped (§7) |
| `acf:README.md:84` | prose describing the defaults | rewritten to describe `adr.yml` |
| `acf:docs/plans/PLAN_PORT_ADR_PACKAGE.md:376, 788` | executed plan's record | kept: a dated record of what phase 1b shipped |

This repository's own copy, `scripts/core/adversarial_design/`, keeps both constants
until 1d deletes it. Its consumers here — `tests/test_adversarial_design_ledger.py:10, 68`,
`tests/test_adversarial_design_run_detail.py:31, 100`, and
`.claude/skills/adversarial-design-review/SKILL.md:302, 320` with its `.cursor/skills/`
mirror at the same lines — import `scripts.core.adversarial_design`, not `acf.adr`, and
are unaffected by this phase.

### 5.4 The prose

Both skill directories move to `acf:plugins/arch-compliance/skills/`, beside the three
skills already there, applying §4.2 and §4.3.

**Host values.** The gate's step 1, before any classification or dispatch, runs

```python
from acf.repo import resolve_repo
from acf.adr import load_host_config
repo = resolve_repo(None)
cfg = load_host_config(repo)
```

so an absent `adr.yml` or doctrine document stops the run before a reviewer is
dispatched. Later steps reuse `repo` and `cfg`: they pass `repo_root=repo`,
`runs_dir=repo / cfg.runs_dir` and `repo / cfg.ledger_path` to the functions that
already take them (§4.2 rows for `.claude/skills/adversarial-design-review/SKILL.md:72-73`, `:289`, `:302`, `:320`), and the
responding skill's two `python -c` bodies run the same two lines. `resolve_repo` is the
plugin's owner of host-root resolution
(`acf:plugins/arch-compliance/python/acf/repo.py:29-41`). With no argument it resolves
the process directory (`:41`, `return Path.cwd().resolve()`), so the gate is run from
the host root, as today; joining with `repo` anchors every artifact location to that
one resolved root.

**Doctrine.** The compliance reviewer reads `config/architecture/ARCHITECTURE.md` in
full, then every document it points to, and walks the doctrine's sections — the
generic instruction already at
`.claude/skills/adversarial-design-review/reviewers/compliance.md:50-52`, reporting
each section that governs but goes unnamed. Its output format becomes
`"<doctrine section> — why it governs here"`, since `§N` is this repository's numbering.
A host's repository-specific *high-frequency misses* are part of its doctrine, reached
the same way. With none, the walk alone is the review.

### 5.5 The sixth exception

`UnresolvableCitationError` is raised by the prose at
`.claude/skills/adversarial-design-review/SKILL.md:75-76` and listed in its failure
table at `:486`. Phase 1b did not port it because no package code raised it. Its
raising prose now arrives, so it joins `acf:plugins/arch-compliance/python/acf/exceptions.py`
under `AcfError` alone, like the five before it.

This repository's version has a second base, `FileNotFoundError`
(`scripts/core/exceptions.py:2277`). Dropping it changes nothing for a caller: recipe
`git grep -n "except.*FileNotFoundError\|except.*OSError"` over
`.claude/skills/adversarial-design-review`, `.claude/skills/responding-to-adversarial-review`
and `scripts/core/adversarial_design` returns two sites,
`scripts/core/adversarial_design/ledger.py:218` and
`scripts/core/adversarial_design/run_detail.py:191`. Each wraps a file write whose try
block cannot raise `UnresolvableCitationError`; the prose raises it and stops.

### 5.6 Refusals

No exception type beyond §5.5's. Each refusal names the file:

| Condition | Raised by | Type |
|---|---|---|
| `adr.yml` absent, unreadable (`OSError`), not YAML, unknown key, missing or empty field, wrong type | `load_model_file` | `AcfInputError` |
| A field with a backslash | `PosixStr` → `load_model_file` | `AcfInputError` |
| `config/architecture/ARCHITECTURE.md` absent | `require_file`, from `load_host_config` and from the constraints hook | `AcfInputError` (the hook prints it and exits 1, as it does today) |
| `runs_dir` or `ledger_path` unwritable at first use | the existing writers | `RunDetailWriteError` / `LedgerWriteError` |

## 6. Shape fit (GEMINI.md §1 item 7)

This is new functionality. GEMINI.md:39 asks three questions of it.

**What existing shape does it extend?**

| Element | Existing shape |
|---|---|
| `ADR_REL` | `acf:plugins/arch-compliance/python/acf/repo.py` — `MANDATES_REL`, `ARCH_REL`, `RATCHET_BASELINE_REL`, the plugin's constants for host-relative paths |
| Loading `adr.yml` | `acf:plugins/arch-compliance/python/acf/loader.py:36` `load_model_file`, already called by `acf:plugins/arch-compliance/python/acf/registry.py:42` and `acf:plugins/arch-compliance/python/acf/baseline.py:86` |
| Refusing an absent doctrine document | `load_model_file`'s own absent-file check (`acf:plugins/arch-compliance/python/acf/loader.py:51-52`), extracted as `require_file` and called by the gate and the constraints hook's doctrine read; the hooks' pre-import mandates checks keep their own (§5.2) |
| Field type | `PosixStr`, `acf:plugins/arch-compliance/python/acf/adr/contract.py:129` |
| Doctrine location | `ARCH_REL`, the path the constraints hook reads (`acf:plugins/arch-compliance/hooks/inject_constraints.py:163`) — one doctrine path, three readers (the gate, the hook, `arch_anchor` matching) |
| Host-root resolution | `resolve_repo`, `acf:plugins/arch-compliance/python/acf/repo.py:29` |
| The moved skills | `acf:plugins/arch-compliance/skills/` — `acf-mandate/`, `acf-setup/`, `architecture-review/` — which ship with no manifest entry (`acf:plugins/arch-compliance/.claude-plugin/plugin.json` has keys name, version, description, author, homepage, repository, license) |
| `UnresolvableCitationError` | the five ADR types phase 1b added to `acf:plugins/arch-compliance/python/acf/exceptions.py` |

**What second way to do something does it create?** Those below, each approved by a §2
decision and filed as declared debt in the canonical roadmap
(`docs/reviews/ARCHITECTURE_REVIEW_2026-07-30_REMEDIATION.md`, *Phase 1c declared
debt*):

| Responsibility | The two owners | Status |
|---|---|---|
| The gate's prose | this repository's copy and the plugin's | Debt removed in 1d, which deletes the local copy; until then edits to the local prose are mirrored |
| Telling an AI reviewer which host mandates to weigh | the host's doctrine (read by the compliance reviewer) and the ACF mandate registry (rendered into subagent context by `acf:plugins/arch-compliance/hooks/inject_constraints.py:155-161`) | Debt, by decision 1; reconciling them is phase 2's registry work |
| What `ARCHITECTURE.md`'s content means | three readers: the compliance reviewer follows the documents it points to; the constraints hook injects its text and follows nothing (`acf:plugins/arch-compliance/hooks/inject_constraints.py:167-170`); mandate `arch_anchor` checks match its text as substrings (`acf:plugins/arch-compliance/skills/acf-mandate/SKILL.md:104`) | Debt, by decision 5. A pointer satisfies all three only if it keeps its mandates' anchor headings (decision 5); the hook still injects pointer text. Settled in 1d, where this repository chooses pointer or excerpt |

**What would the day-one design be?** The same: a skill that reads a declared host
file and a fixed doctrine path, with no host value in its text.

**Pattern sweep.** The defect class this phase removes is *a host value in portable
prose*. Swept by §4.1's two recipes, recipe B validated against the three sites recipe
A misses; every selected line is in §4.2. The guard in §7 keeps the named literals
from re-entering.

## 7. Definition of done

In the plugin repository, `python -m pytest -q` from its root:

1. **Declaration.** Tests for `load_host_config`: a valid config; and one refusal test
   each for an absent file, an unknown key, a missing `runs_dir`, a missing
   `ledger_path`, an empty value in a field, a backslash in a field, and an absent
   `ARCHITECTURE.md`. A test that
   `require_file` refuses an absent path with `AcfInputError` naming it, and the existing
   loader tests unchanged. The constraints hook's existing missing-doctrine test
   (`acf:plugins/arch-compliance/tests/test_hooks.py:253-271`) passes with the hook now
   calling `require_file`.
2. **Defaults deleted.** `acf.adr` no longer exports `LEDGER_PATH` or `RUNS_DIR`;
   calling `run_detail_path` without `runs_dir` raises `TypeError`; the public-surface
   test asserts the new set by equality.
3. **The prose's Python resolves.** Every fenced ```` ```python ```` block in the moved
   SKILL.md files, and every `python -c` body inside a fenced ```` ```bash ```` block,
   parses with `ast`, and every name it imports from `acf.adr` (including its
   submodules, e.g. `acf.adr.citations`), `acf.exceptions` or `acf.repo` exists there.
   The same walk checks the host-value calls: every `run_detail_path` call passes
   `runs_dir`, every `classify_citations` / `unresolved_citations` call passes a
   `repo_root` that is not `Path(".")`, and no `python -c` body opens a literal
   ledger file path.
4. **Prose portability guard.** No file under the two moved skill directories contains
   `GEMINI`, `CLAUDE.md`, `SKILL_PROVENANCE`, `scripts.core`, `docs/design`,
   `docs/reviews`, `docs/architecture` or `.cursor`. Its scope, stated: it catches these
   literals, not a host value spelled some new way; item 5 is the behavioural proof.
5. **Fixture-host acceptance.** A host built in `tmp_path` with a layout unlike this
   repository's (`reviews/runs/`, `reviews/ledger.jsonl`, an `ARCHITECTURE.md`) and a git
   history: `load_host_config(host)` succeeds; `classify_citations` with
   `repo_root=host` classifies a tracked file `current`;
   `run_detail_path(..., runs_dir=host / cfg.runs_dir)` plus `write_run_detail` lands the
   detail under `reviews/runs/`; `append_row(row, host / cfg.ledger_path)` lands a row
   with its preamble. Nothing is written outside `tmp_path`.
6. **`UnresolvableCitationError`** is added to `ADR_TYPES` in
   `acf:plugins/arch-compliance/tests/test_adr_exceptions.py:10-16`, and the module-wide
   single-base test (`:34`) covers it.
7. Each guard in items 2–4 is falsified: plant the offender, watch the test fail,
   restore.
8. `npm test --prefix plugins/arch-compliance/detectors/typescript` prints
   `self-test OK`.
9. This repository is untouched: `git status --porcelain` here shows nothing from this
   phase.
10. **The plugin README** (`acf:README.md`, its *Override contract* section at `:22-25`)
    names the gate as an explicit override of Superpowers' brainstorming → writing-plans
    flow (plugin principle 5, "document that explicitly"), and `acf:README.md:84`'s
    description of the deleted defaults is replaced by a description of `adr.yml`.

Code review is required before merge (GEMINI.md:92 — "Required for tasks that change
public interfaces, persistence formats, …"): `acf.adr`'s exports and
`run_detail_path`'s signature change.

## 8. Risks

| Risk | Mitigation |
|---|---|
| A moved prompt keeps a host assumption neither recipe names | DoD 4 cannot see it. The plan reads each moved file end to end against §4.2 before the guard is trusted |
| The two prose copies diverge before 1d | Edits to the local prose between now and 1d are mirrored; the 1d plan diffs the two |
| The plugin is installed in this repository's harness before 1d, making both copies invocable here | Not the case today (no `.acf/` here; the project `.claude/settings.json` carries an empty `enabledPlugins`). Do not install the plugin here before 1d; 1d installs it and deletes the local copies in one change |

## Appendix — premise verification (authoring time)

| Claim | Command | Output |
|---|---|---|
| Recipe A selects the §4.2 name rows | §4.1 recipe A | 26 lines in `adversarial-design-review/SKILL.md`, 26 in `reviewers/compliance.md`, 4 in `reviewers/sweeper.md`, 2 in `reviewers/hardening.md`, 1 in `reviewers/refuter.md`, 1 in `claims/extraction.md`, 18 in `responding-to-adversarial-review/SKILL.md` |
| §4.2 places each line the two recipes select | run both recipes, parse every `file:line` range in §4.2's first column, compare | 103 selected lines, 0 uncovered; `adversarial-design-review/SKILL.md:302` and `responding-to-adversarial-review/SKILL.md:224` in two rows each |
| Recipe B reproduces the three sites A misses | §4.1 recipe B | includes `adversarial-design-review/SKILL.md:14-16`, `responding-to-adversarial-review/SKILL.md:17-19`, `adversarial-design-review/reviewers/hardening.md:62` |
| Only the `:300` block fails `ast.parse`; `…` → `...` fixes it | `ast.parse` over each fenced block and `python -c` body | nine blocks and both bodies parse as-is; `adversarial-design-review/SKILL.md:300` fails "invalid character '…' (U+2026)" at body line 7 and parses after substitution |
| The `:348` line is a co-maintenance obligation | `sed -n 347,349p .claude/skills/adversarial-design-review/SKILL.md` | "`public_interface`. That list is GEMINI.md §1 item 8's future trigger list; change both together." |
| The plugin comment ties `TouchedSurface` to GEMINI | `sed -n 52,56p acf:plugins/arch-compliance/python/acf/adr/ledger.py` | "#: Must stay in step with GEMINI.md item 8's trigger list, because ``filter_would_skip`` is derived from it" |
| `SKILL_PROVENANCE.md` covers a skill that is not moving | `grep -n "^## post-merge-housekeeping" docs/architecture/SKILL_PROVENANCE.md` | `:205` |
| The hook refuses an absent doctrine with a builtin | `sed -n 163,167p acf:plugins/arch-compliance/hooks/inject_constraints.py` | `if not arch_path.is_file(): raise FileNotFoundError(f"doctrine document not found: …")` |
| The hook calls a pydantic loader before its doctrine read | `grep -n` in `acf:plugins/arch-compliance/hooks/inject_constraints.py` for the imports, the registry load and the render call | `:91` `from acf.exceptions import AcfInputError`, `:92` `from acf.registry import load_mandates`, `:104` `registry = load_mandates(...)`, `:110` `block = _render_constraints(...)`, `:111` `except (FileNotFoundError, OSError)` |
| `require_file`'s message equals the hook's today | `sed -n 51,52p` of `acf:plugins/arch-compliance/python/acf/loader.py`; `sed -n 164,167p` of the hook | `f"{subject} not found: {path.as_posix()}"`; `f"doctrine document not found: {arch_path.as_posix()}"` — identical with `subject="doctrine document"` |
| Recipe C's host-only skill | §4.1 recipe C | `post-merge-housekeeping` at `adversarial-design-review/SKILL.md:361`, `responding-to-adversarial-review/SKILL.md:196`; every other hit a Superpowers skill |
| Recipe D's hits | §4.1 recipe D in the plugin clone | `acf:plugins/arch-compliance/python/acf/adr/contract.py:7, 8, 67`; `acf:plugins/arch-compliance/python/acf/adr/gate.py:43, 49`; `acf:plugins/arch-compliance/python/acf/adr/ledger.py:53`; `acf:plugins/arch-compliance/python/acf/adr/parser.py:97`; `acf:plugins/arch-compliance/python/acf/judge.py:32, 52, 64, 110`; `acf:plugins/arch-compliance/tests/test_adr_contract.py:1, 62`; `acf:plugins/arch-compliance/tests/test_adr_ledger.py:141, 588`; `acf:plugins/arch-compliance/tests/test_judge.py:49, 58` |
| The two value pins' test shapes | `sed -n 67,68p` of `acf:plugins/arch-compliance/tests/test_adr_ledger.py`; `sed -n 93,100p` of `acf:plugins/arch-compliance/tests/test_adr_run_detail.py` | a one-assertion test; a test whose last of three assertions (`:98`, `:99`, `:100`) is the `RUNS_DIR` pin |
| Both writers accept any path | `sed -n 48p` of `acf:plugins/arch-compliance/python/acf/adr/run_detail.py`; `sed -n 204p` of `acf:plugins/arch-compliance/python/acf/adr/ledger.py` | `return Path(runs_dir) / name`; `path = Path(path)` |
| `resolve_repo` falls back to the process directory | read `acf:plugins/arch-compliance/python/acf/repo.py:29-41` | `return Path.cwd().resolve()` on the last branch |
| No caller relies on `UnresolvableCitationError` being a `FileNotFoundError` | §5.5 recipe | the two writer sites only |
| Plugin consumers of the two constants | §5.3 recipe | the rows tabulated, including `acf:README.md:84` and the executed plan |
| The plugin manifest lists no skills | `cat acf:plugins/arch-compliance/.claude-plugin/plugin.json` | keys name, version, description, author, homepage, repository, license |
| `acf.repo` stays stdlib-only | `acf:plugins/arch-compliance/tests/test_repo_paths.py:74-78` | `allowed = {"__future__", "pathlib"}` |
