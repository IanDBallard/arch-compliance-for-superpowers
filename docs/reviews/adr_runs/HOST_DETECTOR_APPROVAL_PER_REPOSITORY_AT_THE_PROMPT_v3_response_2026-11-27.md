# Response: HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT v3

- **Spec:** `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md`
- **Reviewed commit:** `4c45591`
- **Run record:** `HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT_v3_2026-11-26.md`
- **Declared revision class:** precision-only. The revision (`8254a4d`) changes citations, one corrected measurement (§7), change-surface entries for files the design already changes, residual statements and follow-ups. No contract, schema, state, exception or sequencing changes. Cleared by a controller verification pass, user-approved 2026-11-27 (*"fold in and then self review then move to plan per repo convention on non-mechanical changes"*). The mechanism-shaped advisories are follow-ups 2 to 4, not design changes.

## Blocking reasons

### C46 (implementability, load-bearing, counted UNPROVEN): the `--fingerprint` check fits between `file_digests` and the store write

**Cause.** The reviewer's evidence (`cli_allow.py:58-67`) overlapped the spec's citation (`cli_allow.py:58`).

**Resolution.** Revised text. §5.2 and §5.3 item 1 now cite the write the check must precede, `write_approval(repo, registry, digests=digests)` at `:66`, beside `:58`. Re-measured:

```
$ sed -n '58p;66p' plugins/arch-compliance/python/acf/cli_allow.py
        digests = file_digests(repo, rows)
        write_approval(repo, registry, digests=digests)
```

## Advisories absorbed

| Finding | Change |
| --- | --- |
| Strict UTF-8 also hits `git diff -U0` content (`diff.py:68`, `cli_check_diff.py:148`); `run_git` docstring and `test_run_git_reports_nonzero_as_data` framing | §5.1 bullets; §7 risk row rewritten with the measured outcome (accepted, fails loud). |
| `acf-allow --revoke` cannot remove old root-keyed entries | Decision 2 and the README-note row say so; removal is by hand, by the user. |
| Cleared spec's residual cites `host.py:59` | §4 names `host.py:82`. |
| Skill-injected commands fire `PreSkillShellCommand` | §4 residual; §9 follow-up 2. |
| Third copy of the hooks' `sys.path` block; second stdlib-imports check | §5.4 names the copy; §5.7 `## Single point of definition` row records both; §9 follow-up 3. |
| Shared review preparer | §9 follow-up 4. |
| `test_git_runner.py` missing from `ARCHITECTURE.md:188` | §5.7 Trust-boundary row adds it. |

## Sentence-type sweep

| # | Hits and disposition |
| --- | --- |
| T1 | New: none. Carried populations keep their recipes. |
| T2 | *"every byte except the five it leaves undefined"* (§7): cp1252 leaves 0x81, 0x8D, 0x8F, 0x90, 0x9D undefined; stands as a fact of the codec. |
| T3 | *"No command deletes one"* (Decision 2): backed by the store-writer census in the v3 run (refuter's looked-for list: readers of `.repos` are `approval.py:135`, `:167-176`, `cli_allow.py:76-77`). |
| T4 | `PreSkillShellCommand` behaviour is marked *(external)*; its interaction with ask rules *(unverified)*. |
| T5 | `write_approval` at `cli_allow.py:66`, `host.py:82`, `inject_constraints.py:25-29`, `posttooluse_gate.py:37-41`, `test_diff_cli.py:216`: each opened. |
| T6 | `test_diff_cli.py:216` docstring quoted. |
| T7 | No new completeness claim. |
