# Response to HOST_DETECTOR_EXTENSION_POINT v6 review

- **Spec:** `docs/design/HOST_DETECTOR_EXTENSION_POINT.md` (revised to v7)
- **Reviewed commit:** `42087f730b571fc5158a4eecdeb560b8afbf9cb2`
- **Run record:** `docs/reviews/adr_runs/HOST_DETECTOR_EXTENSION_POINT_v6_2026-11-05.md`
- **Declared revision class:** mechanism. The PostToolUse hook switches its own path-containment code to `file_under_root` and stops scanning files outside the repository, and the ratchet refuses a `roots` entry that names no directory. The rest is wording, citation and prose-list changes.

Every command below was run in the worktree. The branch changes only `docs/`, so code lines are as at `a338cad`. Outputs are pasted as printed.

## Blocking reasons

### C29 (premise, load-bearing): "exec_module and the lookup share one try catching (Exception, SystemExit)"

**Resolution: carried unchanged (spec).** The refutation is right about the claim text, which misstated the spec. The spec's handler is `except BaseException`, which re-raises `KeyboardInterrupt` and wraps everything else (§4.4 item 3, §6.1). The reviewer confirmed the rest of the claim. No spec edit is needed; the next run's claim states the handler as the spec writes it.

Falsify by finding a handler in the spec that catches a tuple:

```text
$ grep -n "except BaseException as exc" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
361:     except BaseException as exc:  # fail-loud.bare-except-ok: <reason>
381:   except BaseException as exc:  # fail-loud.bare-except-ok: <reason>

$ grep -n "if isinstance(exc, KeyboardInterrupt)" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
362:         if isinstance(exc, KeyboardInterrupt):
382:       if isinstance(exc, KeyboardInterrupt):
```

### C55 (mandate, load-bearing): "every broad handler re-raises a typed error or KeyboardInterrupt"

**Resolution: revised.** `_describe`'s handler does not re-raise: it returns a constant message when formatting the host's exception itself fails. The §6 `## Fail loud` row now counts three broad handlers and says which one swallows, and what. It quotes the doctrine clause that permits a swallowing handler exempted with a reason, which `_describe`'s token carries. The miscount ("two broad handlers") is gone.

Falsify by finding the old count, or by showing the doctrine clause differs from the quote:

```text
$ grep -o "The design has three broad handlers[^.]*\." docs/design/HOST_DETECTOR_EXTENSION_POINT.md
The design has three broad handlers.

$ grep -c "two broad handlers" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
0

$ sed -n 29,30p config/architecture/ARCHITECTURE.md
Failures must not disappear. Bare `except:` and broad `except Exception:` handlers that
swallow errors are forbidden unless explicitly exempted with a reason.
```

### C73 (shape_fit, load-bearing): "the absolute and under-root string tests have one definition in acf.engine"

**Resolution: revised (mechanism).** The hook kept its own absolute-string test (`Path(raw).is_absolute()`, `posttooluse_gate.py:203-204`) and its own containment test (`relative_to(repo)` with `except ValueError`, `:242-245`), and after the design those decide which paths reach host code. The hook now calls `file_under_root(repo, raw)` in `_collect_paths`. That deletes the absolute join, the `is_file()` skip at `:239` and the `except ValueError` fallback, so `_scan_paths` sees only existing in-repo files. The separate `in_repo_rel_paths` list is gone. Consequence, accepted and stated in §4.6: an edited file outside the repository is no longer scanned. No test exercises that case today, and §4.7 adds one.

Falsify with the recipe now in §4.9: every hit must be a site the spec switches, deletes, or keeps only as a conversion of an already-contained path.

```text
$ git grep -n "is_absolute()\|relative_to(" -- plugins/arch-compliance/hooks plugins/arch-compliance/python
plugins/arch-compliance/hooks/posttooluse_gate.py:204:        abs_path = p.resolve() if p.is_absolute() else (repo / p).resolve()
plugins/arch-compliance/hooks/posttooluse_gate.py:243:            rel = abs_path.relative_to(repo).as_posix()
plugins/arch-compliance/python/acf/adr/citations.py:76:    return not (root / path).resolve().is_relative_to(root)
plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:60:                rel = path.relative_to(root).as_posix()
plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:123:    if not baseline_file.is_absolute():

$ grep -o "becomes \`abs_path = file_under_root(repo, raw)\`[^.]*\." docs/design/HOST_DETECTOR_EXTENSION_POINT.md
becomes `abs_path = file_under_root(repo, raw)`, and a path for which it returns `None` is skipped.

$ grep -n "outside\|out_of_repo\|absolute" plugins/arch-compliance/tests/test_hooks.py | wc -l
0
```

The `relative_to` at `:243` cannot fail after the switch because both sides are resolved:

```text
$ sed -n 41,44p plugins/arch-compliance/python/acf/repo.py
        return explicit.resolve()
    if stdin_cwd:
        return Path(str(stdin_cwd)).resolve()
    return Path.cwd().resolve()
```

### C81 (shape_fit, load-bearing): "resolve_under_root is ADJACENT to the hook's relative_to and the ratchet walk filter"

**Resolution: revised.** The relationship is now `SUBSUMED` (§5.2). Each of those sites decides by hand whether a path lies inside the root. The spec deletes their containment branches and keeps only `relative_to(...).as_posix()` as the conversion of an already-contained path to its key. §4.1 no longer says the walk filter "stays where it is", which contradicted §4.9's deletion of its `except` branch.

Falsify by finding the old wording:

```text
$ grep -c "stays where it is\|in_repo_rel_paths" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
0
```

### C122 (implementability, load-bearing): SURVIVED, but evidence restated the claim's citation

**Resolution: carried unchanged (spec).** The reviewer cited the same file as the claim's `spec_citation` (`cli_check_diff.py:29-61`), so the gate treated the verdict as uncorroborated. The spec text is correct. The next run's claim carries no `spec_citation`, so independent evidence is judged on its own. The facts the claim rests on:

```text
$ sed -n 29,31p plugins/arch-compliance/python/acf/cli_check_diff.py
    parser = argparse.ArgumentParser(prog="acf-check-diff")
    parser.add_argument(
        "--mode",

$ sed -n 69,74p plugins/arch-compliance/python/acf/cli_check_diff.py
    try:
        registry = load_mandates(mandates_path, known_detectors=KNOWN_DETECTORS)
        raw_findings, file_lines = _scan_changed(repo, mode, args.base, registry)
    except (GitError, AcfInputError, UnknownDetectorError, DetectorPackError) as exc:
        print(f"acf: {exc}", file=sys.stderr)
        return 1
```

### "mandate claim C55 is REFUTED"

Same finding as C55 above; same resolution.

## Non-blocking findings folded in

| Finding | Change |
|---|---|
| `## Fail-loud ratchet` is not named and its enablement text is not updated | Named in the header's governing mandates and in §6; §4.8 adds both constraints to `ARCHITECTURE.md:72-73`. |
| `ARCHITECTURE.md:226-228` still names `acf.cli_check_diff.KNOWN_DETECTORS` | §4.8 row: it names `acf.detectors.KNOWN_DETECTORS`. |
| `partial` rows naming a detector or prompt that does not exist yet are refused at load, unlisted | Decision 3 states it as an accepted consequence, quoting `acf-mandate SKILL.md:57-58`; the upgrade note gains the step. |
| `scan_tree` silently counts zero for a misspelled `roots` entry | The ratchet refuses a `roots` entry that is not an existing directory (§4.9, §6.1); §4.7 adds the test. |
| The non-goal's `grep -i review` recipe misses `acf/baseline.py` | The recipe is removed; the non-goal says `acf/baseline.py` is not modified. |
| `require_file` overlap with the new not-found refusals | §5.2 records it as `ADJACENT` with its reason (different input, containment first, phase-specific error type). |
| `## Declared, never defaulted` is cited beyond its scope | §6 says the section governs the ADR gate's host values and the design follows the practice by choice. |
| A carried sentence said every `file_under_root` caller converts a stat `OSError` | §4.1 now says the hook lets it propagate, as `is_file()` at `:239` does today. |

Advisories not folded in: the hardening reviewer's two rung-1 suggestions (stamp TypeScript and built-in mandate ids instead of checking them) would change Node output or the built-in contract; they are left for a later change. The ADR contract's "second implementation" rationale (`ADR_GATE_HOST_CONTRACT.md:300`) keeps its other half; §4.8 already updates its citation.

## Design-simplification pass

Re-run on the whole spec. The hook switch removes three branches and one list (`in_repo_rel_paths`) rather than adding any, and the ratchet change replaces a silent skip with a refusal in the same loop. No element was found that could be removed without losing a stated guarantee.

## Delta pre-flight

One fresh agent ran the refuter and sweeper prompts over the seven claims this revision added or changed: the hook switch (premise), the `partial`-row consequence (premise), the ratchet `roots` refusal (deletion), the single containment implementation with its recipe (shape fit), the `SUBSUMED` relationship (shape fit), the `require_file` relationship (shape fit), and the prose sweep. All seven survived. It also searched by behaviour (`commonpath`, `is_relative_to`, `..` literals, `os.path` helpers, joins of a root with an outside string) and found no containment decision beyond the recipe's sites.

Its three advisories are folded in:

| Advisory | Change |
|---|---|
| `acf-mandate SKILL.md:68` and `:138` repeat the `partial` advice | Decision 3 and the §4.8 row name `:58`, `:68` and `:138`. |
| A `roots` entry that is an in-repo symlink now reports files under the target's path | Stated in the §4.9 ratchet row's behaviour change. |
| The hook does not pass `llm_prompt_ids`, so an unknown prompt id is not refused at edit time | Decision 4 states it and why: the hook runs no `llm` row, and importing `acf.judge` adds `httpx` (`judge.py:11`) to every edit. |

## Sentence-type sweep

Swept the whole revised spec. Hits in changed text and their disposition:

| # | Type | Hit | Disposition |
|---|---|---|---|
| T1 | Population without recipe | "no test exercises the dropped case" (§4.6) | Converted: carries its `git grep` recipe. |
| T1 | Population without recipe | The hook's and the ratchet's containment sites (§4.9 hook row) | Converted: the row carries its recipe and dispositions every hit. |
| T3 | Universal quantifier | "`resolve_under_root` is the one containment test for a path string from outside the code" (§4.1) | Stands, backed by the §4.9 recipe; §5.2 lists the `require_file` and `_scan_changed` sites as `ADJACENT` with reasons. |
| T3 | Universal quantifier | "cannot fail there" for the kept `relative_to` calls | Stands: both sides are resolved (`repo.py:41-44`) and the input is contained; receipt above. |
| T5 | Named construct without receipt | `require_file` (`loader.py:24-28`); `resolve_repo` (`repo.py:41-44`) | Receipts in §5.2 and above. |
| T6 | Doctrine attribution without quote | `## Fail loud` exemption; `acf-mandate` `partial` advice | Quoted adjacent in §6 and Decision 3. |
| T7 | Completeness by recipe only | §4.9 | Not claimed complete; the spec says so. |

Carried text was swept with the same patterns; carried hits were dispositioned in the earlier response records and are unchanged.
