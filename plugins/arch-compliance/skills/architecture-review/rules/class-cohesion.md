# Rule: class-cohesion

**Principle.** A class holds one responsibility. Judge cohesion, not size: a wide
class that does one thing is fine, and a small class doing three things is the defect
this rule exists to catch.

## Settings

- `surface`, `surface_exclude`: already applied by the controller; you audit the
  row's surface as given.
- `docs`: documents to read in full before auditing (for example the repository's
  register of sanctioned facades).
- `facades`: names of classes that are sanctioned facades over one artifact or
  subsystem. Their breadth is intended: never flag a class in `{facades}` for width
  or method count, only for mixing responsibilities. When empty, no class has that
  standing, and width alone is still never a finding.

An absent scalar turns its check off; an absent list is empty.

## Flag

- Orchestration, I/O and policy (business rules) concentrated in one class.
- Methods that fall into disjoint clusters sharing no instance state: two classes
  wearing one name.
- A class whose honest one-sentence job description needs "and" between unrelated
  responsibilities. Treat the "and" as a prompt to re-check, not as a finding by itself.

## Do not flag

- Width alone: method count or line count. A deterministic size check, if the
  repository has one, runs elsewhere; do not repeat it.
- A wide class whose methods all serve one responsibility over shared state.
- Data classes, enums and protocol or interface declarations.

## Method

A surface can hold hundreds of classes; reading every body exhausts context long
before it exhausts the surface. Triage, then deep-read a bounded set.

1. **Enumerate** every class declaration site (`file:line`) in the surface.
2. **Rank cheaply** without reading whole bodies: public method count and the number
   of distinct instance attributes touched. Many methods over many unrelated
   attributes is the shape this rule hunts; many methods over one attribute cluster
   is a facade.
3. **Deep-read the top classes you can afford** and judge them properly. For each,
   list the public methods and the responsibility each serves (orchestration, I/O,
   policy, presentation), and check whether they share instance state.
4. **Report the cutoff.** `files_examined` counts the files you deep-read, and one
   `errors` entry names the ranking and the cutoff, for example
   `"triage: deep-read top 40 of 312 classes, ranked by public methods x distinct attributes"`.

Every finding cites the class declaration line, names the disjoint clusters and says
which one should move out.

## Severity

- `blocking`: orchestration, I/O and policy all in one class, with methods in
  disjoint clusters sharing no state.
- `important`: two of orchestration, I/O and policy mixed, and the job description
  needs "and", though the clusters still share meaningful state.
- `nit`: a cohesion smell confined to one method (one accessor reaching into an
  unrelated subsystem), not the class's shape.
- `suggestion`: a plausible smell that needs human judgment; name it in `why`.

## Example

```python
class Publisher:
    def render(self, doc): ...        # rendering state
    def compile(self, source): ...    # rendering state
    def validate_code(self, c): ...   # pricing state, unrelated
    def compute_price(self, d): ...   # pricing state, unrelated
```

`blocking`: two disjoint clusters share no state; extract the pricing methods into
their own class.
