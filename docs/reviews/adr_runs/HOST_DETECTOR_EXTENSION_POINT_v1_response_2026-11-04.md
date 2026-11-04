# Response to HOST_DETECTOR_EXTENSION_POINT v1 review

- **Spec:** `docs/design/HOST_DETECTOR_EXTENSION_POINT.md` (revised to v2)
- **Reviewed commit:** `5895daf47accce0d5733f842965693a15e41d063`
- **Run record:** `docs/reviews/adr_runs/HOST_DETECTOR_EXTENSION_POINT_v1_2026-11-04.md` (BLOCKED)
- **Revision class:** mechanism. The registry contract, call-site semantics, host return type, load-time behaviour, exception routing and the loader's import isolation all change, so the re-run is a full blind dispatch.
- **User decisions taken for this revision (2026-11-04):** call-site routing is unified for built-in and host rows; invoking `acf-check-diff` is the opt-in for host code there, and `.acf/enabled` gates only the automatic hooks; the path-shape helpers move to `acf.engine` and `acf/adr/citations.py` uses them.

All commands run from the branch root against `a338cad` code (the branch changes only `docs/`).

## Blocking reasons

### C2 (premise, load-bearing): "a host cannot name its own detector in an active row and still load"

**Resolution, revised text (spec §1 item 1).** The problem statement now says what the code does. `load_mandates` checks only `enforced` rows, so a `partial` host row loads and is never executed. The design closes that by validating every active (`status != "unenforced"`) `ast`/`guard` row (spec §2 Decision 3, §4.2).

```
$ sed -n 56,63p plugins/arch-compliance/python/acf/registry.py
    if known_detectors is not None:
        for m in mandates:
            if m.status != "enforced":
                continue
            if m.detection in {"ast", "guard"} and m.detector not in known_detectors:
                raise UnknownDetectorError(
                    f"enforced mandate {m.id!r} references unknown detector {m.detector!r}"
                )
$ grep -n 'partial. .ast./.guard. row today' docs/design/HOST_DETECTOR_EXTENSION_POINT.md
26:   - A `status: partial` row is live in both gates (...) yet `load_mandates` never checks it. So a host can name a detector of its own in a `partial` `ast`/`guard` row today, load cleanly with `known_detectors=KNOWN_DETECTORS`, and have nothing ever execute it.
```

### C18 (mandate, load-bearing): "no path lets an active ast/guard row load without being executable"

**Resolution, revised mechanism (spec §2 Decision 3, §4.2, §6.1).** `load_mandates` now refuses an active host `ast` row whose `languages` is not `python`, `typescript` or `both` (`AcfInputError`). It also refuses any active `ast`/`guard` row, built-in or host, with no Tier-1 call site. Under unified routing (Decision 2), a row that passes both checks is selected by `MandateRegistry.active` in at least one gate: guards on every run, and host `ast` rows on every changed file in their language.

```
$ grep -n '^Language = ' plugins/arch-compliance/python/acf/registry.py
11:Language = Literal["python", "typescript", "both", "none"]
$ grep -n '_ACTIVE_HOST_AST_LANGUAGES' docs/design/HOST_DETECTOR_EXTENSION_POINT.md
121:_ACTIVE_HOST_AST_LANGUAGES = frozenset({"python", "typescript", "both"})
203:            if m.detection == "ast" and m.languages not in _ACTIVE_HOST_AST_LANGUAGES:
206:                    f"{sorted(_ACTIVE_HOST_AST_LANGUAGES)}; got {m.languages!r}"
```

### C32 (shape_fit, load-bearing): "validate_posix_rel_path creates no second way to decide path shape"

**Resolution, revised mechanism (spec §4.1, §5.2).** `acf.engine` gains `looks_absolute` and `resolve_under_root`. `acf/adr/citations.py` deletes `_looks_absolute` (`:49-51`) and `_escapes_repo` (`:74-76`) and calls the engine helpers at its two call sites (`:161`, `:163`). `validate_posix_rel_path`, `load_mandates`, `load_host_detector` and `make_line_lookup` use the same two helpers. The only classification change is that a drive-relative citation (`C:a/b.py`) becomes `external`, pinned by a new `test_adr_citations.py` case. The spec no longer claims a single owner for all path handling; it names the resolve-for-I/O sites it leaves alone.

```
$ grep -n 'def _looks_absolute\|def _escapes_repo\|_looks_absolute(path)\|_escapes_repo(path' plugins/arch-compliance/python/acf/adr/citations.py
49:def _looks_absolute(path: str) -> bool:
74:def _escapes_repo(path: str, repo_root: Path) -> bool:
161:    if _looks_absolute(path):
163:    if _escapes_repo(path, repo_root):
$ git grep -n "is_relative_to\|isabs\|is_absolute()" -- plugins/arch-compliance/python plugins/arch-compliance/hooks
plugins/arch-compliance/hooks/posttooluse_gate.py:204:        abs_path = p.resolve() if p.is_absolute() else (repo / p).resolve()
plugins/arch-compliance/python/acf/adr/citations.py:76:    return not (root / path).resolve().is_relative_to(root)
plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:123:    if not baseline_file.is_absolute():
$ python -I proto.py   # scratch prototype of the spec's §4.1 code
validator ok; citations-old C:a -> False new -> True
```

### C38 (sweep, load-bearing): "the call-site vocabulary matches what the existing gates filter on"

**Resolution, revised mechanism (spec §1 item 3, §2 Decision 2, §4.4, §4.5).** No gate reads `call_sites` today. The design now defines the semantics: `Mandate.runs_at` and `MandateRegistry.active` replace every active-row filter, and `apply_registry` takes a required `call_sites`. This applies to built-in and host rows alike. The behaviour change it causes (`no-shims.hasattr`, declared `[ci]`, leaves the edit hook) is stated, and the pinning test `test_hooks.py:199-218` is rewritten.

```
$ git grep -n 'call_sites' -- plugins/arch-compliance/python plugins/arch-compliance/hooks
plugins/arch-compliance/python/acf/adr/ledger.py:42:        "Read by eye, sorted by surface_call_sites; do not fit a model. Holdout rows "
plugins/arch-compliance/python/acf/adr/ledger.py:83:    surface_call_sites: int = Field(ge=0)      # blast radius
plugins/arch-compliance/python/acf/registry.py:21:    call_sites: list[str]
$ git grep -n "_active_mandates\|status != \"unenforced\"\|status == \"unenforced\"" -- '*.py' ':!*/tests/*'
plugins/arch-compliance/hooks/posttooluse_gate.py:231 / :235 / :285
plugins/arch-compliance/python/acf/cli_check_diff.py:94 / :98 / :112 / :113 / :158 / :168
plugins/arch-compliance/python/acf/enforcement.py:47
```

Every hit above is listed in spec §4.5 or §4.4 as replaced. The active-row census of `call_sites` (spec Appendix) shows each active built-in `ast`/`guard` row already declares `ci`, so the new Tier-1 requirement rejects no live registry.

### C40 (mechanism_justification, load-bearing): "importing host modules at load time is justified"

**Resolution, mechanism removed (spec §2 Decision 3, §4.2).** `load_mandates` no longer imports host code. It checks syntax, the Tier-1 call site, `languages` for `ast` rows, and file existence under `repo_root`. Import and callable lookup happen only at dispatch, inside the gate whose call sites select the row. The edit hook therefore imports only modules for rows declaring `hook` or `posttooluse`, and `inject_constraints.py`, `cli_check_llm.py` and the acf-mandate snippet run no host code.

```
$ awk '/^def load_mandates/,/return MandateRegistry/' docs/design/HOST_DETECTOR_EXTENSION_POINT.md | grep -n 'load_host_detector\|import_module\|exec_module' || echo '(no import in load_mandates)'
(no import in load_mandates)
```

A `test_registry.py` case pins it: a host module that raises at import time is not imported by `load_mandates` (spec §4.6).

### C41 (mechanism_justification, load-bearing): "TIER1_CALL_SITES is necessary and sufficient to prevent an inert active row"

**Resolution, revised mechanism.** Same change as C18. Tier-1 intersection is necessary; the `languages` check on host `ast` rows supplies the missing condition. See C18's command and output.

### C50 (implementability, load-bearing): "host-detector failures reach an existing fail-loud handler"

**Resolution, revised mechanism (spec §4.3 items 5–6, §4.5).** The runners now wrap every exception a host callable raises, `AcfError` included, as `DetectorPackError`. Dispatch-time loading raises `UnknownDetectorError`. The hook's scan handler becomes `except (DetectorPackError, UnknownDetectorError)`. `cli_check_diff.py:72` already catches both. A `test_host_detectors.py` case pins the wrapping of a raised `AcfInputError`.

```
$ sed -n 113,117p plugins/arch-compliance/hooks/posttooluse_gate.py
    try:
        raw_findings, file_lines = _scan_paths(repo, paths, registry)
    except DetectorPackError as exc:
        print(f"acf: {exc}", file=sys.stderr)
        return 1
$ grep -n 'DetectorPackError, UnknownDetectorError' docs/design/HOST_DETECTOR_EXTENSION_POINT.md
292:   - `:113-117`: the scan `except` becomes `(DetectorPackError, UnknownDetectorError)`. ...
```

### C52 (implementability, load-bearing): "load_host_detector isolates distinct repository roots"

**Resolution, revised mechanism (spec §4.3 item 3).** The module name is defined from a hash of root and path. The loader holds one active root per process. Switching roots evicts every `sys.modules` entry whose file lies under the old root, removes the old root from `sys.path` and clears the cache. A `test_host_detectors.py` case loads two roots that each have `helpers/value.py` with different constants. The scratch prototype of exactly this logic:

```
$ python -I proto.py
eviction isolates roots: ['ONE', 'TWO']
$ grep -n '_acf_host_\|One host root per process' docs/design/HOST_DETECTOR_EXTENSION_POINT.md
240:   - **One host root per process.** ...
241:   - **Module name:** `"_acf_host_" + hashlib.sha256(...)...`
```

### mandate claim C18 is REFUTED (duplicate line)

Answered under C18 above.

### mandate claim C29 is REFUTED: universal statements need a re-runnable recipe

**Resolution, revised text.** Each population or universal statement in the spec now carries a re-runnable recipe or a per-item table. The added recipes cover: no dynamic loader in the plugin (§1 item 1); `call_sites` read by no gate (§1 item 3); the branch touches only `docs/` (§0); no review package exists (§3). §6.1 and §6.2 are per-item tables. The spec's Doctrine row for `## No completeness claims` now says "recipe or per-item table", matching the rule's wording at `config/architecture/ARCHITECTURE.md:161-163`. See the sentence-type sweep below.

```
$ git diff --stat a338cad HEAD -- . ':!docs'
(no output)
$ git grep -n "importlib\|import_module\|spec_from_file_location\|exec_module" -- plugins/arch-compliance/python plugins/arch-compliance/hooks
(no output)
$ git ls-files plugins/arch-compliance/python/acf | grep -i review
(no output)
```

### implementability claim C50 is REFUTED (duplicate line)

Answered under C50 above.

### implementability claim C52 is REFUTED (duplicate line)

Answered under C52 above.

### mechanism '_MODULE_CACHE keyed by (root, rel_path, st_mtime_ns, st_size)' has no named producer

**Resolution, mechanism removed.** The cache is keyed by `rel_path` within the one active root and is cleared on root switch. No mtime or size component remains.

```
$ grep -n 'mtime\|st_size' docs/design/HOST_DETECTOR_EXTENSION_POINT.md || echo '(no mtime/size cache key)'
(no mtime/size cache key)
```

## Non-blocking findings folded in

- `HostHit` replaces returning `Finding`, so no field is overwritten (hardening, "repairs rather than refuses").
- A malformed host reference raises `AcfInputError`, which `inject_constraints.py:105` already catches; `cli_check_llm.py` is unchanged and lets any `AcfInputError` from `load_mandates` surface, as it does today.
- The `except Exception` handlers carry `# fail-loud.bare-except-ok:` with a reason.
- The trust boundary is restated per Decision 5. `KNOWN_DETECTORS` is now stated as 13 (by recipe). `_reject_backslash` is cited at `contract.py:60`. The hook excludes out-of-repo paths from host dispatch.
- `make_line_lookup` no longer swallows `OSError`; `errors="replace"` stays, with its reason.
- `resolve_repo(None)` in the acf-mandate snippet; prose sites `:10`, `:74`, `:116`, `README.md:62`/`:106` and the hook docstring were added to §4.7.
- The parse-failure and diff-mode differences of the origin host's driver are stated as cutover work, no longer as "no further plugin change".

## Delta pre-flight

A rehearsal reviewer (sweeper and refuter rules, the 16 claims this revision added or changed, no ledger row) returned 15 SURVIVED and 1 REFUTED (non-load-bearing: the §4.7 prose list), with six advisories. All are folded into the spec: §4.7 adds `config/architecture/ARCHITECTURE.md:9-11`, `docs/design/ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:161`, `acf-mandate` `SKILL.md:59`/`:79`, `README.md:76` and `docs/design/ADR_GATE_HOST_CONTRACT.md:302-303`; §4.5 keeps hook docstring `:11` verbatim (pinned by `plugins/arch-compliance/tests/test_repo_paths.py:47-48`); `Mandate.is_active` is the one "active" predicate; §5.2 adds the judge's `_to_finding`, the hook's `relative_to` and `contract.py:95` as `ADJACENT` with reasons.

## Sentence-type sweep

Swept the whole v2 spec with `grep -n -o -i -E '\b(every|all|only|none|no other|nothing|each|always|never|any)\b[^.|]{0,60}'` plus a read for counts and attributions.

| # | Type | Hits and disposition |
|---|---|---|
| T1 | Population/consumer claim without a recipe | "no dynamic loader", "`call_sites` read by no gate", "`load_mandates` callers", "`apply_registry` callers", "active-row filters": each carries its `git grep` recipe (§1, Appendix), validated against the known sites cited in the v1 run detail. |
| T2 | Aggregate count as a claim | "13" `KNOWN_DETECTORS` comes with its recipe and counts nothing load-bearing. No other totals; callers are listed per item. |
| T3 | Universal quantifier | "`load_mandates` never imports host code" is backed by the §4.2 code and a §4.6 test. "Every cited line is as at `a338cad`" is backed by the §0 recipe. "Each row printed includes `ci`" is the Appendix recipe's observed output. "one owner of path-shape decisions" was deleted and narrowed to the two named helpers. |
| T4 | Prose-only tool behaviour | Path validation, the drive-relative citation change and root eviction are each pinned by a §4.6 test. The prototype output in this record is supporting evidence, not the pin. |
| T5 | Named hook without receipt | Every existing symbol is cited at `file:line` (registry, gates, enforcement, citations `:49-51`/`:74-76`/`:161`/`:163`/`:129-185`, contract `:60`/`:129`, exceptions `:5`/`:13`/`:29`). New symbols are declared in §4. |
| T6 | Doctrine attribution without quote | §1 quotes `ARCH_COMPLIANCE_FOR_SUPERPOWERS.md:102` and `:123`/`:125`. The §6 rows cite anchor line ranges; the bare-except exemption rests on `ARCHITECTURE.md:29-30`. |
| T7 | Completeness backed only by a known-site recipe | The "no live registry is newly rejected" claim is backed by the executed Appendix census over every registry, profile and fixture file, not by a grep. |
