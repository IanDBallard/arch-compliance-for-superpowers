# Rule: state-machine-discipline

**Principle.** State changes only through the declared state-machine base class's own
transition methods, or through the declared validator. A transition raises its declared
failure types on its failure path.

## Settings

- `surface`, `surface_exclude`: already applied by the controller; you audit the
  row's surface as given.
- `docs`: documents to read in full before auditing (for example the state machine's
  design note).
- `base_classes`: the names of the declared state-machine base classes. Read each
  one's definition first and note its transition methods and how a transition declares
  its failure types. A state machine is a class deriving from one of `{base_classes}`.
  When empty, check 2 is off and check 1 judges only files that use
  `{validator_name}`.
- `state_field`: the attribute that holds a machine's state. When absent, check 1 is
  off.
- `validator_name`: the name of the declared transition validator (a function or class
  through which a transition may be applied). A state change made through it is
  compliant. When absent, only the base classes' transition methods sanction a change.

An absent scalar turns its check off; an absent list is empty.

## Flag

1. **Mutation outside a transition.** An assignment to `{state_field}` (directly,
   through `setattr`, or by mutating it in place) on a state machine, made anywhere
   other than inside a transition method of one of `{base_classes}` or through
   `{validator_name}`. This includes subclasses assigning state in ordinary methods and
   outside code assigning a machine's state.
2. **Declared failure not raised.** A transition that declares failure types (in its
   signature, decorator, table or docstring, as the base class defines) whose failure
   path returns, logs or swallows instead of raising one of them.

## Do not flag

- The base classes' own transition machinery assigning `{state_field}`.
- Initial state set in a constructor, if the base class's design says so.
- Reading `{state_field}`.
- Classes that do not derive from `{base_classes}` and do not use `{validator_name}`,
  even if they have an attribute of the same name.

## Severity

- `blocking`: a state mutation outside a declared transition (check 1).
- `important`: a transition missing its declared failure type (check 2).
- `nit`: a mutation inside a helper called only from a transition, where the base
  class's design does not forbid it but obscures the transition.
- `suggestion`: a mutation whose call path you cannot trace to a transition; name the
  doubt in `why`.

## Example

A subclass of one of `{base_classes}` has a method `reset(self)` containing
`self.<state_field> = "idle"`: `blocking`, mutation outside a transition; fix: declare
the reset as a transition and apply it through the base class.
