# Rule: posix-paths

**Principle.** A persisted path is a POSIX string (forward slashes, repository- or
root-relative) carried in a declared path type. Nothing written to committed
configuration, metadata or records holds a host-native path.

## Settings

- `surface`, `surface_exclude`: already applied by the controller; you audit the
  row's surface as given. It may hold source files and committed data files
  (YAML, JSON, TOML) alike.
- `docs`: documents to read in full before auditing.
- `path_types`: the names of the repository's declared path types (for example a
  string alias that refuses backslashes). When set, a persisted path field must be
  typed as one of `{path_types}` (check 4). When empty, check 4 is off.

An absent scalar turns its check off; an absent list is empty.

## Flag

1. **Path persisted without POSIX form.** A path object converted with `str(...)`, an
   un-normalised path, or a string built with the host separator, flowing into a
   serialiser (`yaml.dump`, `json.dump(s)`, `JSON.stringify`, a model's dump) or into
   `.write_text`/`writeFile` of a config, metadata or record file. Confirm from the
   surrounding code that the value really is a path.
2. **Backslash separators in committed data.** A literal `\` path separator in a
   committed `.yml`, `.yaml`, `.json` or `.toml` file. Flag the line.
3. **Mixed separators** in a path-like string literal destined for on-disk
   configuration.
4. **Persisted path field outside the declared types** (only with `path_types` set). A
   model, schema or record field that holds a persisted path but is typed as a plain
   string or path object rather than one of `{path_types}`.

## Do not flag

- Backslashes inside regular expressions, escape sequences, or Windows examples in
  documentation.
- URLs and other non-filesystem strings.
- `str(path)` in a log line or an exception message: these are not persisted (at most
  `nit`).
- A host-native path used only in memory for a filesystem call and never written.

## Severity

- `blocking`: a path value written to persisted data without POSIX form; a literal
  backslash path in a committed data file.
- `important`: a persisted path field typed outside `{path_types}`; mixed separators
  in a configuration literal.
- `nit`: `str(path)` in log output or exception text.
- `suggestion`: a value that may be a path but whose type cannot be confirmed; name the
  doubt in `why`.

## Examples

```python
yaml.safe_dump({"build_dir": str(build_dir)}, handle)   # blocking: use as_posix()
```

```yaml
build_dir: out\site     # blocking: backslash in committed data
```
