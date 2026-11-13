# Rule: layer-boundaries

**Principle.** Code in one tier reaches another tier's resources only through a
declared boundary. The boundary module itself is where the crossing is defined; every
other file uses it.

## Settings

- `surface`, `surface_exclude`: already applied by the controller; you audit the
  row's surface as given.
- `docs`: documents to read in full before auditing (for example the tier
  architecture's design notes).
- `tiers`: a list of `{name, paths}`. A file belongs to the tier whose `paths` patterns
  match it. A file in no tier is not judged.
- `crossings`: a list of `{from_tier, to_tier, root_names, via}`, one per sanctioned
  crossing:
  - `from_tier`, `to_tier`: tier names from `tiers`;
  - `root_names`: the names (variables, parameters, attributes, constants) that hold a
    root of the `to_tier` resources, such as a data root passed to the code;
  - `via`: the boundary: the modules, classes or functions through which code in
    `from_tier` must reach `to_tier` resources.

  Only declared crossings are checked.

An absent scalar turns its check off; an absent list is empty. When `tiers` or
`crossings` is empty, every check is off: report no findings for the row and add one
`errors` string naming the empty setting, for example `"check off: tiers absent"`.

## Flag

1. **Inline crossing.** A file in `from_tier`, outside the `via` modules, builds a path
   or address into `to_tier` resources directly: joining onto one of the crossing's
   `root_names` (`root / "content" / name`, `os.path.join(root, ...)`, a template
   string) or defining its own local accessor that does so, instead of calling `via`.
2. **Hard-coded reach.** A file in `from_tier` reads a `to_tier` resource through a
   hard-coded relative path (`Path("some/tier/dir/file.tpl")`) instead of through
   `via`.
3. **Ambient root.** A file in `from_tier` obtains one of `root_names` from a global,
   an environment default or a module-level constant, where the tier contract says it
   is passed in explicitly. Judge this only where the doctrine section or `docs` state
   that contract.

## Do not flag

- The definitions inside a `via` module that join an explicitly passed root to a
  relative path: they are the boundary being defined, not a bypass of it.
- Call sites that obtain the path by calling `via`.
- Paths within a file's own tier.
- A root name appearing in a log line, docstring or error message.

## Severity

- `blocking`: an inline crossing (check 1).
- `important`: a hard-coded reach (check 2); an ambient root (check 3).
- `nit`: an inline join that only builds a path for display or logging.
- `suggestion`: a crossing whose tiers you cannot determine with confidence; name the
  doubt in `why`.

## Example

A file in a crossing's `from_tier`, outside its `via` modules, contains
`<a root name> / "items" / f"{slug}.md"`, where the root name is one of the
crossing's `root_names`: `blocking`, inline crossing; fix: call the `via` accessor
that returns that path.
