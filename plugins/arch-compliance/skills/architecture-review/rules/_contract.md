# Auditor contract

Every review auditor receives this contract with its rule prompt (or with a
repository's own prompt). It fixes what you may do and what your answer looks like.
Where a rule prompt and this contract disagree, this contract wins.

## What the dispatch gives you

- `group`: the name of your dispatch (a rule id or a repository prompt path).
- One or more **rows**. Each row has an `id`, a `title`, its **settings** (the values
  of the row's `params`, as the rule prompt describes them), its **doctrine section**
  and its **surface**: the repository-relative POSIX paths you audit for that row.
- The path of the repository's doctrine file. Read it in full, then every document it
  points to, before you judge anything; the rows' doctrine sections are where to start,
  not the whole rule.
- The documents in each row's `docs` setting. Read each one in full.
- Pre-pass **candidates**, one per line as `file:line [tell] snippet`. They are
  high-recall pattern matches, not findings: classify each one, and look past them for
  violations no pattern matched. A rule with no candidates is still audited.

The controller has already resolved each surface (globs, exclusions and test paths
applied). The surface bounds where findings may be reported: audit all of it, and cite
nothing outside it. Files a row's settings name as evidence (an inventory, a base
class's module, policy files, a style document) may be read wherever they are in the
repository; only the line a finding cites must be in the surface.

When a rule prompt says its whole check is off for a row because a setting is absent
or empty, report no findings for that row and add one `errors` string naming the
setting, for example `"check off: classifier absent"`. A rule that returns nothing
without saying why looks like a clean pass.

## Read-only

Use only `Read`, `Grep` and `Glob`. Do not edit, write, move or delete any file, and
run no command. `suggested_fix` is prose, never a diff. The controller writes the
report.

## Your answer

Your final message contains **exactly one** fenced `json` block and no other `json`
block anywhere. It matches this shape, with no extra keys:

```json
{
  "group": "<the group name, exactly as given>",
  "files_examined": 0,
  "findings": [
    {
      "mandate_id": "<the id of one of your rows>",
      "path": "<a path from that row's surface>",
      "line": 1,
      "snippet": "<the offending source excerpt, at most 200 characters>",
      "severity": "blocking",
      "rule": "<rule id>: <the sub-rule broken>",
      "why": "<one sentence>",
      "suggested_fix": "<one or two sentences of prose>"
    }
  ],
  "errors": []
}
```

- `group` echoes the dispatch's group name character for character.
- Each finding's `mandate_id` is the `id` of one of the rows you were given: the row
  whose settings and doctrine section the finding is judged against. A violation that
  breaks two rows gives one finding per row.
- `path` is a repository-relative POSIX path (forward slashes, no leading `./`) taken
  from **that row's** surface. A violation you cannot anchor to a line of a file in
  that surface is not a finding; say what you saw in `errors`.
- `line` is a 1-based line number that exists in that file, on the offending line
  itself (for an import, the import's own line).
- `severity` is one of `blocking`, `important`, `nit`, `suggestion`; there is no
  "pass". Grade by the rule prompt's rubric.
- `files_examined` is the number of files you actually read, not the surface size.
- `errors` holds one string per file you could not read (path and reason), and one
  string for any triage cutoff or any part of a surface you did not cover. Never skip
  silently: a run that reports a full surface it did not read is a false clean.
- Report only real violations. No entries for clean files, no "no violation" findings.
