# Response to HOST_DETECTOR_EXTENSION_POINT v8 review

- **Spec:** `docs/design/HOST_DETECTOR_EXTENSION_POINT.md` (revised to v9)
- **Reviewed commit:** `ce6ccb364708c6107d6f08e4c7c9b0fcc7ca10df`
- **Run record:** `docs/reviews/adr_runs/HOST_DETECTOR_EXTENSION_POINT_v8_2026-11-05.md`
- **Declared revision class:** mechanism. The design adds a repository-path façade (`acf.repo.RepoTree`) with a guard test (Decision 9), moves the diff gate onto it, and adds one hit-field check (`validate_hit_fields`) shared by the TypeScript bridge and `HostHit`. The Node rules stop emitting `mandate_id`. The rest is wording.

Every command below was run in the worktree. The branch changes only `docs/`, so code lines are as at `a338cad`. Outputs are pasted as printed.

## Root-cause triage

Since v6, each run has found one more site doing its own path containment: the hook, then host hits, then the diff gate. Each fix added a caller to a shared helper, but nothing stopped the next site from joining the root by hand, so the completeness claim kept being refuted. v9 changes the shape instead of the list. One façade owns turning a path string into a repository location, as the origin host's persistence façades own their artifacts. A guard test then refuses bypasses, so the claim rests on an executed check rather than on an enumeration.

## Blocking reasons

### C45 (premise, load-bearing): "a non-built-in row using a built-in mandate id would receive that scanner's findings"

**Resolution: revised (wording).** The reason held for the five ids stamped by the always-running Python and TypeScript scanners, but not for the four scanners that run once per row of their own. A colliding row there never receives a finding. Decision 3 now states both cases and keeps the refusal for every built-in id, because either way the row does not do what it declares.

```text
$ grep -o "so every built-in mandate id is reserved" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
so every built-in mandate id is reserved
```

### C50 (deletion, load-bearing): "deleting the citations helpers changes exactly two behaviours"

**Resolution: revised (wording).** A third change exists: a citation with an embedded NUL now classifies as `unresolved` instead of raising `ValueError`. §4.1 and the §4.9 citations row list all three.

```text
$ grep -o "Three behaviours change" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
Three behaviours change

$ grep -c "Two behaviours change" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
0
```

### C80 (shape_fit, load-bearing): "HostHit → Finding is ADJACENT to the TypeScript bridge; they share only the constructor"

**Resolution: revised (mechanism).** Both sites validate a detector hit's line and message, and the bridge's version was weaker. `acf.engine.validate_hit_fields` is now the one check: the bridge calls it inside its existing `try`, and `HostHit` calls it in a `before` validator that also requires exact types. The Node rules stop emitting `mandate_id`, so `TS_MANDATE_IDS` is the only spelling of the two TypeScript ids, and the runtime comparison is gone. §5.2 records the shared check as `SUBSUMED` and states which parts stay separate.

```text
$ grep -o "| \`validate_hit_fields\` | the TypeScript bridge[^|]*|" docs/design/HOST_DETECTOR_EXTENSION_POINT.md | cut -c1-120
| `validate_hit_fields` | the TypeScript bridge's `int(item["line"])` and `str(item["message"])` (`plugins/arch-

$ grep -c "checked echo" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
0
```

### C90 (shape_fit, load-bearing): "the diff gate's join-and-is_file is ADJACENT to file_under_root"

**Resolution: revised (mechanism).** The diff gate turned git paths into files with a lexical join that follows symlinks out of the repository, and handed host guards paths that `_to_findings` would then refuse. `_scan_changed` now uses `RepoTree.file` and `RepoTree.key`, and host guards receive only the accepted paths. The two gates now agree on symlinks and keys.

```text
$ grep -o "abs_path = tree.file(rel)\`, skipping \`None\`" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
abs_path = tree.file(rel)`, skipping `None`

$ grep -o "scan_host_guards(repo, in_repo, registry" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
scan_host_guards(repo, in_repo, registry
```

The executed census behind Decision 9 is committed beside the spec. Every non-allowlisted line it prints is a site the design switches to the façade:

```text
$ python docs/design/evidence/HOST_DETECTOR_EXTENSION_POINT/path_census.py . | cut -f1,2
plugins/arch-compliance/python/acf/adr/citations.py:75	resolve
plugins/arch-compliance/python/acf/adr/citations.py:76	is_relative_to
plugins/arch-compliance/python/acf/adr/citations.py:168	join
plugins/arch-compliance/python/acf/adr/citations.py:76	resolve
plugins/arch-compliance/python/acf/adr/citations.py:76	join
plugins/arch-compliance/python/acf/cli_check_diff.py:66	resolve
plugins/arch-compliance/python/acf/cli_check_diff.py:118	join
plugins/arch-compliance/python/acf/cli_check_llm.py:50	resolve
plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:45	resolve
plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:46	join
plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:124	join
plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:60	relative_to
plugins/arch-compliance/python/acf/detectors/typescript_bridge.py:27	resolve
plugins/arch-compliance/hooks/posttooluse_gate.py:204	resolve
plugins/arch-compliance/hooks/posttooluse_gate.py:204	resolve
plugins/arch-compliance/hooks/posttooluse_gate.py:204	join
plugins/arch-compliance/hooks/posttooluse_gate.py:243	relative_to
```

## Non-blocking findings folded in

| Finding | Change |
|---|---|
| Two broad handlers carried the placeholder `<reason>` | Each token now states its reason. |
| `isinstance(exc, KeyboardInterrupt)` inside a handler can read a host-overridden `__class__` | Each handler is preceded by `except KeyboardInterrupt: raise`. |
| `_describe`'s producer is latent | §4.4 says no origin-host code raises such an exception today; the helper guards the boundary with arbitrary host code. |
| `_revalidate` relied on pydantic 2.13's coercion | `HostHit`'s `before` validator enforces exact types, so no pydantic version's coercion matters. |
| The Node literal plus a runtime comparison kept two spellings | The Node rules stop emitting `mandate_id`. |
| `test_profile_drift` never checks the profiles against the prompt ids | §4.7 adds `llm_prompt_ids` there. |
| The contract-against-dispatch fixture tree had no stated home | §4.7: generated under `tmp_path`, never committed. |
| The Node scanner's undeclared subprocess encoding sits in an edited function | §6 states it stays declared debt under self-hosting spec §9 follow-up 1. |
| `## Façade sinks` and `## FSM transitions` enablement text omits the new contract | §4.8 adds both. |
| `test_diff_cli` did not say which `--call-site` value | §4.7: `--call-site ci`. |

Advisories not folded in: stamping built-in ids per row (lifting the one-row-per-detector limit), a path-less `ast` hit type, a single entry point for the full-validation `load_mandates` call, `fresh_host_loader` and namespace subpackages, and the judge's provider-supplied `mandate_id` (Tier-2, out of scope).

## Design-simplification pass

Re-run on the whole spec. The façade replaces two free helpers and five hand-written containment sites with one small class. The hit-field check replaces a coercion in the bridge, two `Field` constraints and the exact-type block in `_revalidate`. Dropping the Node literal removes a runtime comparison. No element was found that could be removed without losing a stated guarantee.

## Changed-claims check

One fresh agent ran the refuter and sweeper prompts over the eight claims this revision added or changed:

- behaviour preserved by `RepoTree` at each migrated site;
- the path census and the guard's outcome;
- the Node change;
- `HostHit`'s exact-type validator;
- the citations behaviours;
- the façade as the one owner;
- the shared hit-field check;
- the spec's internal consistency.

Five survived. The agent re-ran the census and got output identical to the committed file. It searched by behaviour (joins, `Path(` construction, `os.path`, string concatenation) for sites the guard's blind spots could hide, and found none.

Three were refuted, and each is fixed:

| Refuted | Fix |
|---|---|
| The guard's three-function outcome: §5.2 and the §4.9 hook row still said the ratchet and hook keep `relative_to(...).as_posix()`, which the guard flags | Both passages now say the conversion goes through `RepoTree.key`. |
| "Same key for every in-repo regular file": on a case-insensitive checkout, a resolved path takes the on-disk case, so the diff gate would key `Foo.py` as `foo.py`, and the ratchet would re-key a `roots` entry spelled in another case | The diff gate keeps git's spelling for every key, and `tree.file` decides only containment and which file is read. The hook's key is the resolved spelling, as today. The ratchet's case change is stated in §4.9. |
| Internal consistency: §1 item 5 still justified moving containment into `acf.engine`, and the parent design's finding schema (`ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:118`) still lists `mandate_id` for both packs | §1 item 5 names `acf.engine` for the absolute-string check and `acf.repo` for containment (`acf.adr` already imports `acf.repo`, `adr/host.py:16`); §4.8 updates `:118`. |

```text
$ grep -c "relative_to(...).as_posix()" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
0

$ sed -n 16p plugins/arch-compliance/python/acf/adr/host.py
from acf.repo import ADR_REL, ARCH_REL
```

The plan document's mention of the Node stdout contract (`docs/plans/PLAN_ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:509`) is a past plan's record and is not edited, as §4.8 treats other past-run records.

This check is a rehearsal by one agent over the changed claims only. It is not the four-reviewer gate, and it writes no ledger row.

## Sentence-type sweep

Swept the whole revised spec. Hits in changed text and their disposition:

| # | Type | Hit | Disposition |
|---|---|---|---|
| T1 | Population without recipe | "Sites that do this job by hand today switch to the façade" (§4.1) | Converted: the Appendix path-census row and the committed script and output. |
| T3 | Universal quantifier | "`acf.repo.RepoTree` is the one place runtime code turns a path string into a location" (Decision 9) | Stands, enforced by the guard test; its blind spots are stated. |
| T4 | Prose-only tool behaviour | `mode="before"` validator sees raw input | Pinned by the §4.7 `test_host_detectors.py` exact-type cases. |
| T5 | Named construct without receipt | `hm:GEMINI.md:131`; `typescript_bridge.py:88-89`; `emptyCatch.ts:4`; `ARCHITECTURE.md:75-85`, `:176-181` | Opened and quoted or cited at the line. |
| T6 | Doctrine attribution without quote | The origin host's façade rule | Quoted adjacent in Decision 9. |
| T7 | Completeness by recipe only | The path census | Executed census committed beside the spec, with its output (§2a); the guard test re-runs it on every test run. |

Carried text was swept with the same patterns; carried hits were dispositioned in the earlier response records and are unchanged.
