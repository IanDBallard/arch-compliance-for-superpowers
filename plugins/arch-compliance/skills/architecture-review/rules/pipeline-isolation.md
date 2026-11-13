# Rule: pipeline-isolation

**Principle.** Shared stages never branch on the output variant. Variant stages
consume only the canonical intermediate artifact, never the raw sources it was built
from.

## Settings

- `surface`, `surface_exclude`: already applied by the controller; you audit the
  row's surface as given.
- `docs`: documents to read in full before auditing (for example the pipeline's
  design note).
- `shared_stages`: path patterns of the shared stages, which must be variant-agnostic.
  When empty, checks A and B are off.
- `variant_stages`: path patterns of the variant-specific stages. When empty, checks C,
  D and E are off.
- `exempt`: path patterns of files never flagged by this rule (for example an upstream
  conversion step whose job is to read raw sources).
- `variant_terms`: the names and literal values that identify a variant: discriminator
  variable or attribute names and the values they take. When empty, checks A and E
  are off.
- `raw_sources`: what counts as a raw source: file extensions, directories, or the
  libraries that read them. When empty, check C is off.
- `canonical_artifact`: a description or path of the canonical intermediate artifact
  the variant stages consume. When absent, check D is off.

A file matching both stage lists is judged as both. An absent scalar turns its check
off; an absent list is empty. When `shared_stages` and `variant_stages` are both
empty, every check is off: report no findings for the row and add one `errors`
string, `"check off: shared_stages and variant_stages absent"`.

## Flag

- **A. Variant branch in a shared stage.** A file matching `{shared_stages}` branches on
  one of `{variant_terms}` so that it selects different content, structure or
  post-processing per variant.
- **B. Shape leakage in a shared stage.** A shared stage derives structure or behaviour
  from input cardinality or input shape (`if len(items) == 1:` choosing a different
  structure), rather than from declared configuration and the content itself.
- **C. Raw source read in a variant stage.** A file matching `{variant_stages}` opens,
  imports a reader for, or enumerates anything matching `{raw_sources}`.
- **D. Bypassing the canonical artifact.** A variant stage reads individual source
  inputs instead of `{canonical_artifact}`. Reading the canonical artifact, or its
  declared derivatives, is compliant.
- **E. Hard-coded variant in a variant stage.** A variant stage binds one of
  `{variant_terms}` to a literal instead of reading the declared variant.

## Do not flag

- Files matching `{exempt}`.
- A variant term in a log line, docstring, comment or error message, or as a metadata
  value passed through unchanged (at most `nit`).
- Benign length checks: iteration bounds, validation messages, logging.
- A dictionary key or argument that happens to equal a variant value but does not
  select variant behaviour.

## Severity

- `blocking`: A (variant branch in a shared stage); B (shape-gated structure in a
  shared stage); C (raw source read in a variant stage); E (hard-coded variant).
- `important`: D (a variant stage bypassing the canonical artifact).
- `nit`: a variant term in a shared stage used only for logging or metadata.
- `suggestion`: a branch whose effect on output you cannot confirm; name the doubt in
  `why`.

## Example

A shared-stage file contains `if output_format == "pdf": include_index = True` where
`output_format` and `"pdf"` are in `{variant_terms}`: `blocking`, A; fix: always emit
the index anchor and let the variant stage decide whether to realise it.
