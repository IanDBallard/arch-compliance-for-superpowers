# Response to HOST_DETECTOR_EXTENSION_POINT v7 review

- **Spec:** `docs/design/HOST_DETECTOR_EXTENSION_POINT.md` (revised to v8)
- **Reviewed commit:** `51b5df51ac465ad5cfb102cc125109936b71a452`
- **Run record:** `docs/reviews/adr_runs/HOST_DETECTOR_EXTENSION_POINT_v7_2026-11-05.md`
- **Declared revision class:** mechanism. Host hits are contained by `resolve_under_root`, a non-built-in row using a built-in mandate id is refused at load, the loader keeps one module record (`sys.modules`), and the ratchet reuses the pack's bare-except predicate. The rest is wording and prose-list changes.
- **Verification run on this revision, by the author's choice:** the author's own premise checks and mechanical stop, plus one fresh reviewer over the claims this revision added or changed (section "Changed-claims check" below). No full gate run was made on v8, so no ledger row records it, and `writing-plans` waits for a gate run that clears.

Every command below was run in the worktree. The branch changes only `docs/`, so code lines are as at `a338cad`. Outputs are pasted as printed.

## Blocking reasons

### C76 (shape_fit, load-bearing): "deciding whether an outside path string lies inside the root has one implementation, resolve_under_root"

**Resolution: revised (mechanism).** Host hits were checked only by `validate_posix_rel_path`, which judges a path's text. A lexically valid path that escapes through an in-repo directory symlink still became a finding, and `scan_host_guards` mapped its lines to `[]`. Now `_to_findings` takes `repo_root` and refuses (`DetectorPackError`) any hit for which `resolve_under_root(repo_root, hit.path)` is `None`. Both runners pass `repo_root`. `validate_posix_rel_path` is described as a shape check only, and §5.2 records the two checks as different jobs. `scan_host_guards`' `None` case no longer lists "a path outside the root". §4.7 adds the symlink-escape test, and §6.1 adds the refusal row.

Falsify by finding a host-hit path that reaches a `Finding` without `resolve_under_root`, or the old `[]` wording:

```text
$ grep -o "refuses (\`DetectorPackError\`) any hit for which \`resolve_under_root(repo_root, hit.path)\` is \`None\`" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
refuses (`DetectorPackError`) any hit for which `resolve_under_root(repo_root, hit.path)` is `None`

$ grep -n "_to_findings(..., repo_root=repo_root" docs/design/HOST_DETECTOR_EXTENSION_POINT.md | cut -c1-12
421:   - Each
422:7. **`scan

$ grep -c "a path outside the root, and a symlink loop" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
0

$ grep -o "| A host hit whose path resolves outside the repository[^|]*| \`_to_findings\` | \`DetectorPackError\` |" docs/design/HOST_DETECTOR_EXTENSION_POINT.md
| A host hit whose path resolves outside the repository or cannot be resolved | `_to_findings` | `DetectorPackError` |
```

## Non-blocking findings folded in

| Finding | Change |
|---|---|
| C91: the `--call-site` sweep missed `acf-setup SKILL.md:228`, which runs the tool without naming it | The §4.8 row adds the tip at `:228`. |
| A non-built-in row whose id equals a built-in mandate id receives that scanner's findings | `load_mandates` with `known_detectors` refuses it (`AcfInputError`, §4.2, Decision 3, §6.1); the Appendix census shows no shipped row is refused; §4.7 adds the test. |
| Two records of a loaded host module (`_MODULE_CACHE` beside `sys.modules`) | `sys.modules` under the derived name is the one record (§4.4 item 3); the fixture no longer resets a second cache. |
| The bare-except predicate is defined twice | The ratchet imports the pack's predicate, renamed `is_bare_or_exception` (§4.9, §5.2, §6.2). |
| `load_baseline` stays a second JSON loader | §5.2 records it `ADJACENT`, quoting the approved contract's record of it as a pre-existing second loader. |
| Two decoding policies for exemption lines | §4.4 item 7 and §5.2 state why the guard read is lenient (its lines serve only the token lookup; a guard may flag a binary or a document). |

Advisories not folded in: the judge's `mandate_id` taken from the provider is Tier-2, outside this design's scope (Decision 2). `fresh_host_loader` matching namespace subpackages by `__file__`, the `allowlist_globs` "equivalent rather than equal" wording, and the absent shipped ratchet baseline are left unchanged. The `LLM_PROMPT_IDS` move to a lightweight module and the TypeScript rung-1 stamping are left for a later change.

```text
$ sed -n 228p plugins/arch-compliance/skills/acf-setup/SKILL.md
Optional friend-bar tip: plant a temporary empty `catch {}` (TS) or bare `except:` (Python), stage it, re-run with `--mode staged`, confirm BLOCK/WARN, then revert.

$ git grep -n "_is_bare_or_exception\|node.type.id == \"Exception\"" -- '*.py'
plugins/arch-compliance/python/acf/detectors/fail_loud_ratchet.py:33:        elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
plugins/arch-compliance/python/acf/detectors/python_pack.py:61:    if not _is_bare_or_exception(node):
plugins/arch-compliance/python/acf/detectors/python_pack.py:77:def _is_bare_or_exception(node: ast.ExceptHandler) -> bool:
plugins/arch-compliance/python/acf/detectors/python_pack.py:80:    if isinstance(node.type, ast.Name) and node.type.id == "Exception":
```

The reserved-id census (the Appendix recipe) printed the nine stamped ids and no colliding row.

## Design-simplification pass

Re-run on the whole spec. The revision removes one store (`_MODULE_CACHE`) and one duplicate predicate. It adds one check (containment of host hits) and one load refusal (reserved ids). Each of those closes a route by which a finding reaches the wrong place, so neither is removable without losing a stated guarantee.

## Changed-claims check

One fresh agent ran the refuter and sweeper prompts over the eight claims this revision added or changed. Those claims cover:

- the reserved-id refusal (premise);
- the shared bare-except predicate (deletion);
- the single `sys.modules` record (premise);
- host-hit containment (premise);
- the single containment implementation (shape fit);
- the two `ADJACENT` relationships (shape fit);
- the `--call-site` sweep;
- the test and table coverage (sweep).

Seven survived. The agent searched by behaviour (`relative_to(`, `is_relative_to`, `.resolve(`, `is_absolute(`, `os.path` helpers, joins of a root with an outside string) and found no containment decision on an outside string beyond the sites the spec switches.

**Refuted: the `--call-site` sweep.** Two friend-success-bar instructions run the diff gate on a planted violation without giving a command line: `docs/guides/SUPERPOWERS_COMPLEMENT.md:70-71` and `README.md:112`. §4.8 had listed the first as a mention that runs nothing. Both are now in the §4.8 row's instruction list, quoted. The row no longer counts `:70` as a mention.

```text
$ sed -n 70p docs/guides/SUPERPOWERS_COMPLEMENT.md
4. See `acf-check-diff` (or the PostToolUse hook) **fail**.

$ sed -n 112p README.md | cut -c1-80
After `/acf-setup` on a React repo: plant a Tier-1 violation → gate fails; fix i
```

Its advisories, folded in:

| Advisory | Change |
|---|---|
| An embedded NUL in a path makes a non-strict `resolve()` raise `ValueError` on POSIX, which escaped every handler | `resolve_under_root` maps `ValueError` to `None` with `RuntimeError` (§4.1), so the path is refused as outside the root; §4.7 adds the case. |
| A module that executes cleanly but lacks the callable stays registered, and a `KeyboardInterrupt` skips the removal | §4.4 item 3 states both; the §4.7 removal test uses an import failure. |
| The ratchet's walk still reads an in-root `.py` symlink to a file outside the repository | Stated in the §4.9 ratchet row as unchanged behaviour. |

This check is a rehearsal by one agent over the changed claims only. It is not the four-reviewer gate, and it writes no ledger row.

## Sentence-type sweep

Swept the whole revised spec. Hits in changed text and their disposition:

| # | Type | Hit | Disposition |
|---|---|---|---|
| T1 | Population without recipe | "No shipped or fixture row has such an id" (Decision 3) | Converted: the Appendix row carries the recipe and its output. |
| T1 | Population without recipe | The bare-except predicate's sites (§4.9) | Converted: the row carries its `git grep` recipe. |
| T3 | Universal quantifier | "containment is `resolve_under_root`'s alone" (§4.4 item 5) | Stands. Every host hit passes `_to_findings`, which applies it; §5.2 lists the shape check as a different job. |
| T5 | Named construct without receipt | `_is_bare_or_exception` (`python_pack.py:77-82`); `load_model_file` (`loader.py:43-77`) | Receipts above and in §5.2. |
| T6 | Doctrine attribution without quote | `load_baseline` as a second loader | Quoted adjacent in §5.2. |
| T7 | Completeness by recipe only | §4.9 | Not claimed complete; the spec says so. |

Carried text was swept with the same patterns; carried hits were dispositioned in the earlier response records and are unchanged.
