# Rule: path-provenance

**Principle.** An externally sourced path is classified by the declared cross-platform
helper, never by the host platform's absolute-path test. A path written on one
operating system can be read on another: the host test calls a foreign absolute path
relative (`C:/x` on a POSIX host), and the classification silently fails.

## Settings

- `surface`, `surface_exclude`: already applied by the controller; you audit the
  row's surface as given.
- `docs`: documents to read in full before auditing (for example the path
  classification design note).
- `classifier`: the name of the repository's cross-platform classification helper
  (with its module, if the setting gives one). Read its definition first. When absent,
  this rule's check is off: report no findings for the row and add one `errors`
  string, `"check off: classifier absent"`.

An absent scalar turns its check off; an absent list is empty.

## Flag

A host-platform absolute-path test (`Path(value).is_absolute()`,
`os.path.isabs(value)`, `path.isAbsolute(value)`, or an equivalent) applied to a value
whose origin is **external**, instead of `{classifier}`. External origins include:

- a field read from a persisted document or record in the repository;
- a request body, query parameter or form field;
- a configuration file or registry entry;
- any value that another machine or user could have written.

For each candidate, trace the classified variable back to its assignment; cite the
line of the test.

## Do not flag

- A value that provably originates on the current host: a command-line argument, a
  path the process derives at runtime, a local tool's own artifact.
- A value already screened for foreign absolute paths before the host test runs.
- Uses of `{classifier}` itself, and the classifier's own implementation.
- A host test whose result only shapes a log or error message.

## Severity

- `blocking`: an external path classified by the host test where the result decides
  where something is written or whether an external path is accepted.
- `important`: any other external path classified by the host test.
- `nit`: a host test on a value that is host-derived in practice but whose origin the
  code does not make plain.
- `suggestion`: a value whose origin you cannot trace; name the doubt in `why`.

## Example

`if Path(payload["image"]).is_absolute(): ...` where `payload` is a request body:
`important` (or `blocking` if the branch chooses a write target); fix: classify with
`{classifier}`.
