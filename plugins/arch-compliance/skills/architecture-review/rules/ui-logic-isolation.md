# Rule: ui-logic-isolation

**Principle.** The UI renders and dispatches. It does not decide domain rules and it
does not mirror backend state. The violation is the UI **deciding**; rendering a
decision the backend already made is fine.

## Settings

This rule has no settings of its own.

- `surface`: the UI files you audit (scripts, components, templates, markup). Already
  resolved by the controller; audit it as given.
- `surface_exclude`: already applied by the controller.
- `docs`: documents to read in full before auditing (for example the API contract
  that says which decisions the backend returns).

An absent list is empty.

## Flag

**Blocking shapes**

- A client-side state machine or state object that mirrors or predicts backend state
  and drives the UI (a local draft or status object computing which actions are
  enabled).
- The client **overriding** an enablement or state the backend returned:
  `let enabled = resp.enabled; if (localCheck()) enabled = false;`.
- Domain or policy decisions computed in a view: authorisation, pricing, eligibility,
  aggregation that the backend should own.

**Important shapes**

- Business or schema logic in the UI: visibility, enablement or values derived from a
  domain rule (`fields.hidden = record.type !== "x"`) rather than from a backend field.
- Client-side validation that duplicates a backend rule.
- Client dirty-state or derived state driving enablement of a domain action.
- Fetching and business transformation mixed into one view, where it belongs in a
  service, loader or store.
- Reactive declarations (derived values, effects, computed properties) that compute a
  domain value rather than a presentational one.

## Do not flag

- Rendering a backend field: `button.disabled = !resp.actions.publish.enabled`.
- Pure presentation: open and closed panels, spinners, focus, hover, show or hide
  during a fetch, class-name maps, image fallbacks.
- Thin hooks or handlers that only wire props and events to the backend.
- Generic plumbing: request wrappers, notification helpers, routing.

## Method

Start from the candidates: open each `file:line` and classify it against the shapes
above. Then search the surface for what patterns miss: local objects named like state
or drafts, enablement and visibility assignments whose right-hand side is a local
conditional, and template conditionals that branch on domain values. Cite the exact
line of each real violation.

## Severity

- `blocking`: a client-side state machine driving the UI; the client overriding a
  backend decision; domain or policy decisions in a view.
- `important`: business or schema logic in the UI; duplicated validation; dirty-state
  enablement; fetch-and-transform pipelines inside views.
- `nit`: a local table mapping backend state names to presentation that duplicates a
  little backend knowledge.
- `suggestion`: a borderline display map or conditional; name the ambiguity in `why`.

## Examples

- `finalize.disabled = isFinalized || !isLast;` beside a client-held draft object:
  `blocking`, client-side state machine.
- `save.disabled = !hasUnsavedChanges` on a domain action: `important`.
- `save.disabled = !data.enabled`: not flagged, pure render.
