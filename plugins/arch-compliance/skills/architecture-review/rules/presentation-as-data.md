# Rule: presentation-as-data

**Principle.** Layout and styling are data, not code. Appearance values live in a
declared style schema; every structural element is declared for every variant; one
schema version is live.

## Settings

- `surface`, `surface_exclude`: already applied by the controller; you audit the
  row's surface as given. Findings on the style document need it in the surface.
- `docs`: documents to read in full before auditing (for example the style schema's
  specification).
- `bindings`: path patterns of the binding files that realise appearance (templates,
  stylesheets, layout macros). When empty, check B is off.
- `style_schema`: the path or path pattern of the declared style documents. When
  absent, checks A and B are off.
- `element_key`: the key in a style document that lists or maps the structural
  elements (for example openers, dividers, headers). When absent, check A is off.
- `variant_key`: the key in a style document that lists or maps the variants the
  document exposes. When absent, check A is off.

An absent scalar turns its check off; an absent list is empty.

## Flag

- **A. Element × variant gap.** In a style document matching `{style_schema}`, read the
  variants under `{variant_key}` and the elements under `{element_key}`. An element the
  document realises for one variant but leaves undeclared for another variant it also
  exposes is a gap: every pair must be declared, whether as a realisation or as an
  explicit omission. Silent absence renders empty. Cite the element's line.
- **B. Style values living in a binding.** A binding file matching `{bindings}` holds an
  appearance value (font, size, spacing, colour, dimension) that encodes a design
  decision `{style_schema}` should own. Look especially for values a line-level lint
  cannot see: assembled across lines, passed through a macro or variable, computed.
- **C. More than one live schema version.** A binding or loader that accepts or branches
  on more than one version of the style schema. A multi-version loader is a shim.

## Do not flag

- Values a binding reads from the style document and only passes through.
- Structural constants with no design meaning (zero, one, `100%` of a container).
- A version check that refuses every version but the live one: that is failing loud.
- Inline literals a deterministic guard in the repository already reports, if the
  doctrine section says so; your job is the semantic facets.

## Severity

- `blocking`: C (more than one live schema version).
- `important`: A (element × variant gap); B (a design value living in a binding).
- `nit`: a borderline value whose design meaning is slight.
- `suggestion`: a value you cannot confirm is a design decision; name the doubt in
  `why`.

## Example

A style document exposes two variants under `{variant_key}`; its `{element_key}` map
realises a divider element for the first and says nothing for the second:
`important`, A; fix: declare the divider for the second variant, as a realisation or
an explicit omission.
