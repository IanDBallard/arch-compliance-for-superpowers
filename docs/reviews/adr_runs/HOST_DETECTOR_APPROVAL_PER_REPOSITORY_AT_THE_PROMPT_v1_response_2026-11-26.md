# Response: HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT v1

- **Spec:** `docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md`
- **Reviewed commit:** `3b860c5`
- **Run record:** `HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT_v1_2026-11-26.md`
- **Declared revision class:** mechanism. `run_git`'s decoding, `git_common_dir`'s failure classification and its environment all change.

All scratch commands ran in a scratch directory `gd/` (git 2.49.0.windows.1, Python 3.13.2, Windows locale `cp1252`).

## Blocking reasons

### C9 (premise, load-bearing, REFUTED): "a non-ASCII path … can only cause a MISSING"

**Resolution (mechanism).**
- §4's sentence is deleted.
- New §1.3 G4 records what actually happens: on Windows the locale decode fails inside `subprocess`'s reader thread, and `stdout` comes back `None` with no exception. This is worse than the reviewer's traceback, because it is silent.
- §5.1 changes `run_git` to capture bytes and decode them as strict UTF-8. Non-UTF-8 stdout raises `GitError` on every platform.
- `git_common_dir` turns any unexpected result into `GitError`.
- §5.1's table routes `GitError` into each entry point's existing handler. The PostToolUse hook and `acf-allow` gain `GitError` in their tuples.
- §7 records the effect on the diff gate's other git calls.

Falsifier (the decode failure and the UTF-8 fix):

```
$ mkdir "Á_dir" && cd "Á_dir" && git init -q
$ PYTHONUTF8=0 python -X utf8=0 ../dec.py "$(pwd -W)"
Exception in thread Thread-1 (_readerthread):
...
UnicodeDecodeError: 'charmap' codec can't decode byte 0x81 in position 110: character maps to <undefined>
locale cp1252
locale-decode: None
utf8-decode: 'C:/Users/.../scratchpad/gd/\xc1_dir/.git\n\n'
```

`dec.py` runs `git rev-parse --path-format=absolute --git-common-dir --show-prefix` twice: once with `text=True`, once with `encoding="utf-8"`.

Falsifier (the callers that inherit the decoding change):

```
$ grep -rn "run_git\|_git(" plugins/arch-compliance/python plugins/arch-compliance/hooks scripts --include=*.py | grep -v "def "
plugins/arch-compliance/python/acf/adr/citations.py:73: ... _git([...])   # citations' own _git, not run_git
plugins/arch-compliance/python/acf/adr/citations.py:78: ...
plugins/arch-compliance/python/acf/adr/citations.py:90: ...
plugins/arch-compliance/python/acf/adr/citations.py:95: ...
plugins/arch-compliance/python/acf/diff.py:35:    proc = run_git(repo, *args)
plugins/arch-compliance/python/acf/diff.py:56:    out = _git(repo, "diff", ...)
plugins/arch-compliance/python/acf/diff.py:68:    out = _git(repo, "diff", ..., "-U0", "--", rel)
plugins/arch-compliance/python/acf/review/rollup.py:57:    done = run_git(...)
plugins/arch-compliance/python/acf/review/rollup.py:78:    blame = run_git(
plugins/arch-compliance/python/acf/review/rollup.py:82:        tracked = run_git(...)
plugins/arch-compliance/python/acf/review/rollup.py:90:    ancestry = run_git(...)
```

The `diff.py` and `rollup.py` sites are the ones §5.1 lists. `citations.py` has its own runner, which stays declared debt.

Falsifier (the entry points that receive a key `GitError`):

```
$ sed -n 106p plugins/arch-compliance/python/acf/cli_check_diff.py
    except (GitError, AcfInputError, UnknownDetectorError, DetectorPackError) as exc:
$ sed -n 141,145p plugins/arch-compliance/hooks/posttooluse_gate.py
    try:
        registry = load_mandates(mandates_path, known_detectors=KNOWN_DETECTORS, repo_root=repo)
        approval = check_approval(repo, registry, HOOK_CALL_SITES)
    except (AcfInputError, UnknownDetectorError) as exc:
```

### C17 (mandate, load-bearing, UNPROVEN): `git_common_dir` returning `None` on any failure meets Fail loud

**Resolution (mechanism).**
- `git_common_dir` returns `None` for one outcome only: exit `128` with `not a git repository` in stderr (G2). Git runs under `LC_ALL=C`, so that message is in English.
- Every other result raises `GitError` carrying git's stderr: another exit code, malformed output, or an `OSError`.
- The folder fallback no longer hides a broken git.
- §6.1 pins each branch. It includes a self-check that `tmp_path` really is outside a repository, so a misplaced `tmp_path` cannot make the `None` test pass wrongly.
- `## Declared, never defaulted` records the folder key with that narrower condition.

Falsifier (git's outcome outside a repository, under `LC_ALL=C`):

```
$ cd gd/plain && LC_ALL=C git rev-parse --path-format=absolute --git-common-dir --show-prefix; echo "exit=$?"
fatal: not a git repository (or any of the parent directories): .git
exit=128
```

Falsifier (the doctrine clause the resolution answers):

```
$ sed -n 31,32p config/architecture/ARCHITECTURE.md
Failures must not disappear. Bare `except:` and broad `except Exception:` handlers that
swallow errors are forbidden unless explicitly exempted with a reason.
$ sed -n 42p config/architecture/ARCHITECTURE.md
"No 'defaulting' to None to avoid a crash" (`hm:GEMINI.md:104`). "`hasattr()`-based
```

**Found while answering C17, not in the run record: the key under an inherited `GIT_DIR` (G3).**
- In a linked worktree's `pre-push` hook, git sets `GIT_DIR`, and `--show-prefix` in a subfolder then prints an empty prefix. So a subfolder host would get the top-level key.
- §5.1 now asks git for its own list of repository-locating variables (`rev-parse --local-env-vars`) and strips them for the key query.
- §4 and §9 record that the diff gate's own git calls have the same exposure, as follow-up 1.

```
$ git worktree add -q ../wt && cd ../wt && mkdir -p sub && git commit -q --allow-empty -m y && git push -q ../remote.git HEAD:wtb
$ cat ../hookenv.txt          # pre-push: env | grep ^GIT_; then (cd sub && git rev-parse ... --show-prefix)
GIT_DIR=C:/Users/.../gd/w/.git/worktrees/wt
GIT_EXEC_PATH=C:/Program Files/Git/mingw64/libexec/git-core
GIT_PREFIX=
GIT_EDITOR=true
/tmp/.../gd/wt
C:/Users/.../gd/w/.git
                              # <- empty prefix line in sub/
$ cd sub && GIT_DIR=<wt git dir> sh -c 'git rev-parse --show-prefix; env -u GIT_DIR git rev-parse --show-prefix'

sub/
$ git rev-parse --local-env-vars     # outside any repository
GIT_ALTERNATE_OBJECT_DIRECTORIES
GIT_CONFIG
GIT_CONFIG_PARAMETERS
GIT_CONFIG_COUNT
GIT_OBJECT_DIRECTORY
GIT_DIR
GIT_WORK_TREE
GIT_IMPLICIT_WORK_TREE
GIT_GRAFT_FILE
GIT_INDEX_FILE
GIT_NO_REPLACE_OBJECTS
GIT_REPLACE_REF_BASE
GIT_PREFIX
GIT_SHALLOW_FILE
GIT_COMMON_DIR
exit=0
```

The same push from the main checkout `w` printed no `GIT_DIR`, and its prefix was `sub/`.

### C47 (implementability, REFUTED): "the AST check `test_repo_paths.py:81-108` uses, applied to the new file"

**Resolution (mechanism, test design).**
- §6.3 specifies a new test that walks `approval_prompt.py`'s AST. It asserts that every imported top-level module is in `sys.stdlib_module_names`, which also refuses `acf`.
- It is modelled on `test_repo_module_imports_only_stdlib` (`:74-78`).
- §6.5 states what `:81-108` actually is: a poisoned-module subprocess test over the two existing hooks.

```
$ sed -n 81,82p plugins/arch-compliance/tests/test_repo_paths.py
def test_hooks_import_repo_without_pulling_third_party(tmp_path) -> None:
    """A marker-less host must still exit 0 with pydantic and yaml poisoned.
$ sed -n 99p plugins/arch-compliance/tests/test_repo_paths.py
    for hook in ("inject_constraints.py", "posttooluse_gate.py"):
$ sed -n 74,78p plugins/arch-compliance/tests/test_repo_paths.py
def test_repo_module_imports_only_stdlib() -> None:
    source = (PYTHON_ROOT / "acf" / "repo.py").read_text(encoding="utf-8")
    imports = re.findall(r"^\s*(?:from|import)\s+([A-Za-z_][\w.]*)", source, re.M)
    ...
$ python -c "import sys;n=sys.stdlib_module_names;print({m:(m in n) for m in ['json','sys','os','acf','pydantic']})"
{'json': True, 'sys': True, 'os': True, 'acf': False, 'pydantic': False}
$ sed -n 5p pyproject.toml
requires-python = ">=3.11"
```

### C49 (implementability, UNPROVEN, not load-bearing): the hook's `deny` stops the call in bypass mode

**Resolution (precision).**
- Decision 4 now says Claude Code may not honour a PreToolUse `deny` in that mode *(unverified)*, and that in bypass mode only Decision 7's ask rule is documented to stop the call.
- §7 and §8 item 4 keep the live test.
- No proof is added: the claim rests on external behaviour.

```
$ grep -n "unverified" docs/design/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT.md | grep -i bypass
109:   - In `bypassPermissions` mode it returns `deny`. Whether Claude Code honours a PreToolUse `deny` in that mode is *(unverified)*. In bypass mode, only Decision 7's ask rule is documented to stop the call.
```

## Important and advisory findings absorbed

| Finding | Where in v2 |
| --- | --- |
| The hook runs without `.acf/enabled`, against the prose contract | Decision 4 states it and why. The Supersedes header adds `PLUGIN_SELF_HOSTING_AND_DOCTRINE.md:162-164`. §5.7 rows for `README.md:112`, `SUPERPOWERS_COMPLEMENT.md:89`, `hooks.json:2` and `acf-setup SKILL.md:185`. §6.3 pins it. |
| Existing tests index the store by the root key | §6.1 table of the seven sites, with the recipe. |
| `conftest.py` should clear `CLAUDE_CODE_CHILD_SESSION` | §6 opening paragraph. |
| §5.7 missed `approval.py:3-5`, `acf-setup SKILL.md:260` and the `posttooluse_gate.py:16` docstring | §5.7 rows, plus a recipe line. |
| Gate-text tests: only `test_hooks.py:554` must change | §6.4. |
| Inherited `GIT_*` changes the key | §1.3 G3, §5.1 step 1-2, §6.1, §9 follow-up 1. |
| `Write(~/.acf/**)` never matches | Dropped from Decision 7. |
| One review renderer; `cli_allow.py:56` should reuse `_store_inside_repo` | `describe_approval` (Decision 6, §5.2), §5.3 item 3, §6.2. |
| `run_git` is not "the one git runner" | Wording removed. The runner change is in §5.1. |
| Old spec `:84` and `:156` not listed as superseded | Supersedes header. |
| `ARCHITECTURE.md:239-240` coverage goes stale | §5.7 row. |
| "Three defaults" count | §5.7 row. |
| `STORE_REL` needle copy | §5.4 step 3 and §5.7 rows (`## Single point of definition`, the `STORE_REL` comment). |
| §9 "one consumer" wording | §9 names the three consumers. |
| #62 proposed migrating old keys | Decision 2, last bullet. |
| One fingerprint per repository: parallel worktrees with different bytes alternate `STALE` | §4 bullet. |
| `CHECK_DIFF_HOST_WIRING.md:333` | §5.7 row: left as written, with the reason. |
| §1.2 overstated "possible only at a terminal" | Retitled. §1.2 says it is a convention, with no check in `cli_allow.main`. |

## Delta pre-flight

One agent ran the refuter and sweeper lenses over eight claims this revision added. It writes no ledger row.

| Claim | Verdict | Fix in the spec |
| --- | --- | --- |
| D1 callers of `run_git` | REFUTED | The recipe now covers `plugins/arch-compliance/skills`, which adds `architecture-review/SKILL.md:289`. `rollup.provenance` maps a blame `GitError` to `unresolved` (report-only), and its docstring is in §5.7. |
| D2 `GitError` entry points | SURVIVED | none |
| D3 `NOT_NEEDED` before the key | SURVIVED | none |
| D4 `describe_approval` keeps the output | REFUTED | `describe_approval` keeps the two header lines (`cli_allow.py:59`, `:62`). |
| D5 §5.7 sweep | REFUTED | Rows added for `acf-setup SKILL.md:263` and `CLAUDE.md:36-38` (the `PYTHONUTF8` reason), `repo.py:4-5` and `rollup.py:4-5`. The `README.md:64`/`:110` change text is made explicit. |
| D6 test sites | SURVIVED | none |
| D7 doctrine counts | SURVIVED | The stale line citations in the rewritten sentences are corrected (§5.7). |
| D8 no duplicate helper | SURVIVED | none |

Unanchored findings absorbed:
- In bypass mode the shell needles `cli_allow` and `write_approval` denied routine development commands. The needles are narrowed to `acf-allow`, `acf.cli_allow` and `approvals.json`, and §6.3 pins that `pytest …test_cli_allow.py` and `git add …cli_allow.py` pass.
- The bypass-mode deny of commands that only mention a needle is now in §7.
- Key comparison without case normalisation is a §4 bullet.

## Sentence-type sweep

Swept the whole revised spec. Recipe: `grep -nEio "[^.]{0,50}\b(every|all|only|never|none|no other|always)\b[^.]{0,40}"`, plus a read for counts, named constructs and attributions.

| # | Hits and disposition |
| --- | --- |
| T1 population claims | Callers of `run_git` (§5.1): converted to a recipe plus the listed hits. Entry points receiving `GitError` (§5.1 table): recipe given. Gate-text tests (§6.4): recipe given. Root-key test sites (§6.1): recipe plus table. §5.7: recipe plus per-item table, with the claim of completeness withdrawn in its lead paragraph. |
| T2 aggregate counts | "Four defaults" and "Two calls" in §5.7 are edits to doctrine counts, each with its items named. The seven test sites are a table, not a total. |
| T3 universal quantifiers | "Every git worktree has its own root" (§1.1): definitional, stands. "Only one git outcome gives the folder key" (Decision 1): it is the design's own rule, implemented by §5.1 steps 4-5 and pinned by §6.1. "Every other failure raises" (Decision 1): same. "§5.7 updates every sentence listed there" (Decision 4): scoped to the listed rows. "Every caller already found by the recipe" (§5.1): scoped to the recipe. "Re-approving … makes every worktree whose bytes differ … STALE" (Decision 1): follows from one fingerprint per key, pinned by §6.1. "Never read again for a git repository" (Decision 2): follows from the key not being computed, pinned by §6.1. The §1.1 "every refusal in #62" claim is scoped to #62's three refusals. |
| T4 prose-only tool measurements | G1-G4 (git and `subprocess` behaviour) were measured in prose and are each pinned by a committed test in §6.1. `sys.stdlib_module_names` membership is pinned by the §6.3 test itself. Claude Code behaviour stays *(external)* or *(unverified)*, with §8 live checks. |
| T5 named constructs without receipts | `run_git` (`diff.py:17`), `_store_inside_repo` (`approval.py:121`), `check_approval`'s `NOT_NEEDED` return (`:128-129`), `_revoke`'s key (`cli_allow.py:76`), the store check (`cli_allow.py:56`), the hook's except tuple (`posttooluse_gate.py:141-145`), the `cli_check_diff` handler (`:106`), `test_repo_module_imports_only_stdlib` (`test_repo_paths.py:74-78`) and `_isolated_home` (`conftest.py:10-17`): each read at the cited lines in this revision. `git rev-parse --local-env-vars`: output pasted above. |
| T6 doctrine attributions | `## No shims` (Decision 2), `## Declared text decoding` and `## Fail loud`: quoted in the spec or above. The `PYTHONUTF8=1` instruction (§5.1): `CLAUDE.md` quoted adjacent. |
| T7 completeness claims backed only by a validated recipe | None remain. §5.7 and the §6.1 test table each say the plan re-runs their recipe. |
