# Response: HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT v2

- **Spec:** `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md`
- **Reviewed commit:** `82dd643`
- **Run record:** `HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT_v2_2026-11-26.md`
- **Declared revision class:** mechanism. `STORE_REL` moves to `acf.repo`, and the approval hook imports `acf.repo`. That replaces a pinned copy of the store file name. A new pin test covers the ask rules against the hook's needles.

Both blocking reasons rested on evidence outside the tracked tree. Each is now answered by a probe committed under `docs/design/evidence/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT/`, with its recorded output beside it. Machine: Windows 11, Python 3.13.2, git 2.49.0.windows.1, locale `cp1252`, Claude Code 2.1.330.

## Blocking reasons

### C9 (premise, load-bearing, counted UNPROVEN): G4, today's `run_git` loses a non-ASCII path on Windows without raising

**Cause.** The claim's only in-repository evidence was the spec's own `diff.py:24-30` citation. The confirming source, CPython's `subprocess.py`, is outside the tree.

**Resolution.** Revised text. `run_git_decode_probe.py` calls `acf.diff.run_git` from this checkout in a child interpreter with `PYTHONUTF8=0`, over six directory names, and records what comes back. G4 now cites its output line by line. The output also corrects the claim's breadth:
- Names whose UTF-8 bytes include a byte `cp1252` leaves undefined (`Á`, `Ý`) come back `None`.
- Every other non-ASCII name tested (`é`, `ü`, CJK) comes back as wrong text, with no error at all.

G4's row, its follow-on paragraph and the §6.1 test (now `Á` and `é`) say so.

Command that would falsify G4 as revised (a run where every non-ASCII row has `stdout_matches_utf8_truth: true` refutes it):

```
$ python docs/design/evidence/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT/run_git_decode_probe.py
git version 2.49.0.windows.1
{
  "python": "3.13.2",
  "platform": "win32",
  "locale_encoding": "cp1252",
  "utf8_mode": 0,
  "rows": [
    { "dir": "ascii_dir", ... "stdout": "<tmp>/ascii_dir/.git\n", "stdout_matches_utf8_truth": true, "reader_thread_error": [] },
    { "dir": "Á_dir", "utf8_bytes_of_name": "c3 81 5f 64 69 72", "returncode": 0, "stdout": null,
      "stdout_matches_utf8_truth": false,
      "reader_thread_error": ["UnicodeDecodeError: 'charmap' codec can't decode byte 0x81 in position 47: character maps to <undefined>"] },
    { "dir": "Ý_dir", ... "stdout": null, ... "byte 0x9d in position 47" ... },
    { "dir": "é_dir", ... "stdout": "<tmp>/Ã©_dir/.git\n", "stdout_matches_utf8_truth": false, "reader_thread_error": [] },
    { "dir": "ü_dir", ... "stdout": "<tmp>/Ã¼_dir/.git\n", "stdout_matches_utf8_truth": false, "reader_thread_error": [] },
    { "dir": "日本_dir", ... "stdout": "<tmp>/æ—¥æœ¬_dir/.git\n", "stdout_matches_utf8_truth": false, "reader_thread_error": [] }
  ]
}
```

(Abridged with `...`. The full output is `run_git_decode_probe.out`, 62 lines.)

### C51 (implementability, UNPROVEN): whether a PreToolUse JSON `deny` is honoured in `bypassPermissions`

**Cause.** The documentation does not name the mode for a JSON `deny`. It documents only that an exit-`2` hook stops the call before permission rules are evaluated.

**Resolution.** Revised text, evidence from the build itself. The live headless spike (`bypass_hook_probe.py`) could not run here: a nested `claude -p` fails with *"OAuth session expired and could not be refreshed"*, because the standalone CLI's login on this machine has expired. The user chose to proceed on source evidence. `hook_deny_source_probe.py` instead reads the JavaScript bundled in the Claude Code 2.1.330 binary, anchoring on string literals, and records the excerpts with the binary's SHA-256. They show four things:
- A1: an exit-`2` hook becomes `{behavior:"deny", decisionReason:{type:"hook"}}`.
- A2: a JSON `permissionDecision` other than allow, ask or defer becomes the same shape.
- A3: the resolver handles a hook `deny` in its first hook branch, ahead of the hook-`allow` branch that reads the permission mode.
- A4: the function that branch returns through hands back a deny unless a mod or policy check changes it.

So the JSON `deny` takes the same path as the documented exit `2`. Decision 4 keeps the JSON `deny`, since it carries a reason for the user, and cites A1 to A4. §8 item 4 now names `bypass_hook_probe.py` as the live check and states its expected output. The §7 risk row says the claim rests on one build's source.

Command that would falsify the revised claim (an A1 or A2 excerpt that yields anything but `behavior:"deny"`, or an A3 deny branch that calls the permission-mode path first):

```
$ python docs/design/evidence/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT/hook_deny_source_probe.py <claude.exe 2.1.330>
2.1.330 (Claude Code)
bytes 387754656 sha256 fa797c1bc7d4a3511da42622bae53a2b7f1276ae328c668f2bfef44635301caa

== A1 anchor 'if(it.blockingError){' last offset 333538225 occurrences 1
if(it.blockingError){let ft=A7(`PreToolUse:${o.name}`,it.blockingError);if(!(it.blockingError.hookDidNotFinish&&Q?.behavior==="deny"))Q={behavior:"deny",message:ft,decisionReason:{type:"hook",...
== A2 anchor 'Hook result has permissionBehavior=' last offset 333539725 occurrences 2
... else{let jt={behavior:it.permissionBehavior,message:it.hookPermissionDecisionReason||`Hook PreToolUse:${o.name} ...`,decisionReason:ft};Q=jt,yield{type:"hookPermissionResult",hookPermissionResult:jt}} ...
== A3 anchor 'if(e?.behavior==="deny"){t(`Hook denied tool use for' last offset 333533120 occurrences 1
... if(e?.behavior==="deny"){t(`Hook denied tool use for ${o.name}`);...;if(!PC())return kte(e,Oe);...if(Ue!==null&&xZt(Ue))return{decision:e,input:r};if(Ue?.behavior!=="deny"||!P8(Ue.decisionReason))return kte(e,Oe);...}if(e?.behavior!=="allow"&&e?.behavior!=="ask")...
== A4 anchor 'evaluate:()=>Promise.resolve(e)},o.assistantMessage.message.id)' last offset 333536392 occurrences 1
... k=await MVa(o.tool,o.input,y,o.toolUseID,o.toolUseContext) ... if(k.behavior!=="ask")return{decision:k,input:o.input};return{decision:await o.canUseTool(...,k),input:o.input}}
```

(Abridged with `...`. The full excerpts are `hook_deny_source_probe.out`.)

The live spike's attempt, for the record:

```
$ python docs/design/evidence/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT/bypass_hook_probe.py <claude.exe 2.1.330> control
2.1.330 (Claude Code)
{
  "variant": "control",
  "exit_code": 1,
  "call_ran (marker.txt exists)": false,
  "hook_calls": [],
  "permission_denials": [],
  "final_text": "Failed to authenticate: OAuth session expired and could not be refreshed"
}
```

## Important and advisory findings absorbed

| Finding | Change |
| --- | --- |
| C4 REFUTED (not load-bearing) and its advisories: the Supersedes header misses `HOST_DETECTOR_LOCAL_APPROVAL.md:73`, `:127`, `:251`, and `PLUGIN_SELF_HOSTING_AND_DOCTRINE.md` item 11's trigger list | Header lists each, with what replaces it. |
| G4 understates the loss: most accented letters garble rather than vanish | G4 rewritten from the probe (C9 above). |
| `CLAUDE.md` row cites `:36-38` and the wrong wording | New row at `CLAUDE.md:37-39` quoting *"until the git runner declares its own encoding (spec §9, follow-up 1)"*. |
| `CHECK_DIFF_HOST_WIRING.md:141` and `:330-331` restate the encoding claim | Added to the left-as-written row with `:333`, with the reason. |
| `acf-approval-status` needs its own `file_digests` call | §5.2 states it, citing `approval.py:132`, `:137`, `:139`. |
| `cli_allow.py:58-65` should be `:59-65` | §5.2 fixed; `:58` named as kept. |
| #62's acceptance criterion (every worktree `STALE` after an edit) is departed from silently | New §4 bullet giving the reason. |
| `STORE_REL` could live in the stdlib-only `acf.repo` (rung 1) | Adopted: §5.4 step 3, Decision 4, §5.7 rows for `repo.py` and `## One owner for host paths`, §6.3 import test, §6.5 poisoned-module test. The pin test and the `## Single point of definition` row for the copied name are gone. |
| The approval command set is defined twice (needles and ask rules) | `APPROVAL_NEEDLES` named; `## Single point of definition` row records the copy; §6.3 pin test both ways. |
| `## Scoped refactor` not stated as governing | Added to Governing mandates, quoted. |
| §4 omits a user-installed `tool.check` mod | New §4 bullet, tied to excerpt A4. |
| Exit 2 would put the bypass branch on documented behaviour | Answered by A1 to A4: the JSON `deny` and exit `2` reach the same decision. The JSON form stays for its reason text. |

## Sentence-type sweep

Swept the whole revised spec, carried text included.

| # | Hits and disposition |
| --- | --- |
| T1 population without recipe | §5.1 caller list, §5.1 handler table, §5.7 table, §6.1 assertion table and §6.4 test list each carry their recipe (carried). New: §6.3's *"each one found is a Decision 7 rule"* rests on the count below. |
| T2 aggregate as claim | *"three shell needles"* is the literal tuple beside it. *"Four defaults"* in §5.7 is a sentence to be written, not a claim. Stands. |
| T3 universal quantifier | §0's *"the branch changes only this spec, its evidence directory and review records"*: backed by `git diff --name-only 58ed65c HEAD`, which before this revision printed the spec, three run records, the v1 response and the ledger. The commit adds the evidence directory and this record. §6.3's *"today there are none"*: backed by the regex ``re.compile(r"`(Bash|PowerShell|Edit)\([^)`]*\)`")``. Over `acf-setup/SKILL.md` it found `[]`. Validated over this spec, where it found the five Decision 7 rules: `Bash(acf-allow:*)`, `Bash(python -m acf.cli_allow:*)`, `PowerShell(acf-allow:*)`, `PowerShell(python -m acf.cli_allow:*)`, `Edit(~/.acf/**)`. If such a token appears that is not a rule, the test fails loud. |
| T4 prose-only tool behaviour | G1 to G3 are pinned by §6.1 tests. G4 is now an executed probe with committed output. Decision 4's bypass claim is a committed source probe, with the live probe named in §8. Claude Code documentation claims stay marked *(external)*. |
| T5 named construct without receipt | `STORE_REL` at `approval.py:37`, `store_path` at `:68`, `test_repo_module_imports_only_stdlib` at `test_repo_paths.py:74`, the import block at `posttooluse_gate.py:38-43`, `pathlib` at `repo.py:13`: each opened and cited. `APPROVAL_NEEDLES` is new (proposed). |
| T6 doctrine attribution without quote | `## Scoped refactor` now quoted. `repo.py:3-6` quoted for the stdlib contract. `## No shims` quoted (carried). |
| T7 completeness from a recipe | §5.7 states it claims no completeness and the plan re-runs its recipe (carried). No new completeness claim. |
