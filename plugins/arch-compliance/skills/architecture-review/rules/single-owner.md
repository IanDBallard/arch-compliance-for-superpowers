# Rule: single-owner

**Principle.** A declared persisted artifact is read and written only through its
declared owner. An inventory tracks the known exceptions so that each one is either
being migrated or has been, and no new one appears unnoticed.

## Settings

- `surface`, `surface_exclude`: already applied by the controller; you audit the
  row's surface as given.
- `docs`: documents to read in full before auditing (for example the owner's design
  note and its rules).
- `target_literal_re`: a regular expression matching how the artifact is named in
  code (its file name or path literal). A line that reads, writes, opens, parses or
  builds a path to a literal matching `{target_literal_re}` is a **direct access**.
  When absent, the direct-access check is off and this row reports nothing.
- `allowlist_globs`: path patterns of the owner (the modules allowed direct access).
  They match as `fnmatch` patterns over the repository-relative path, where `*` also
  crosses `/`. Direct access in a file matching one of `{allowlist_globs}` is the
  owner doing its job: never flag it. When empty, no file is the owner.
- `inventory`: the path of a document listing files known to access the artifact
  directly, each marked compliant, non-compliant or in migration. When set, read it in
  full first and reconcile every file against it (table below). When absent, the
  reconciliation is off and every direct access outside the owner counts as untracked.

An absent scalar turns its check off; an absent list is empty.

## Flag

A direct access to the artifact outside `{allowlist_globs}`: a raw parse or dump, an
`open` or file read, a path joined to the artifact's literal, or a query or client call
naming it, that bypasses the owner. Reconcile each file of the surface with the
inventory:

| File in `{inventory}` as | Direct access present | Direct access absent |
|---|---|---|
| non-compliant | `important` (known debt) | `suggestion`: ready to mark compliant |
| in migration | `important` | `suggestion`: migration appears complete |
| compliant | `blocking` (regression) | no finding |
| not listed, or no inventory | `blocking`: new untracked direct access | no finding |

A `suggestion` for a file with no direct access cites the file's first line.

## Do not flag

- Access through the owner's own interface (its methods or functions).
- Files matching `{allowlist_globs}`.
- A literal matching `{target_literal_re}` in a log line, a docstring, a comment or an
  error message that opens nothing.
- Test fixtures, if they are in the surface at all, that build a throwaway copy of the
  artifact for a test.

## Severity

- `blocking`: new direct access not in the inventory, or a regression in a file the
  inventory marks compliant.
- `important`: direct access in a file the inventory marks non-compliant or in
  migration.
- `nit`: a direct access that only reads the artifact's location (for example to
  print it) without reading or writing its content.
- `suggestion`: an inventory entry that looks ready to update. Inventory edits are a
  human action; you never make them.

## Example

A file not in the inventory and not matching `{allowlist_globs}` contains a raw parse
of a path matching `{target_literal_re}`: `blocking`, "new direct access not tracked
in the inventory"; fix: route the read through the owner, or add the file to the
inventory if the access is intended.
