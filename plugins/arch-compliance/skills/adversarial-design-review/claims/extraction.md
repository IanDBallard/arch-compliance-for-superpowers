# Claim extraction

Decompose the spec into falsifiable claims. Reviewers adjudicate this list rather
than free-reading prose, so **an unexamined claim is structurally impossible** — and
a claim you fail to extract is a claim nobody checks. Extraction is the gate's
blind spot; treat it as the highest-leverage step.

## Spec-kind classification

Emit a **set**. A spec can be both.

- **`defect`** — motivated by a bug, guardrail gap, or architecture finding. Tell:
  the spec explains why something is currently wrong.
- **`feature`** — pure enhancement. Tell: the spec explains what the system will
  newly do. A `feature` spec still makes assumptions about current behaviour; those
  are `premise` claims, not root causes.
- **`docs`** — documentation, measurement, or process with no code mechanism.

Both `defect` and `feature` apply when a spec fixes something *and* adds capability.
Extract both families' claims and expect both load-bearing families to be present.

## The eight claim families

| Family | What it captures | Reviewer |
|---|---|---|
| `premise` | Any factual assertion about the **current system**: "templates are factory-tier", "settings resolve in this order", "N live instances are affected", and **every deferral** (see below) | `refuter` |
| `root_cause` | The causal story: *this* code, doing *this*, produces the defect | `refuter` |
| `compensation` | "The defective code knows X that the source of truth cannot express" | `refuter` |
| `deletion` | What the design **removes**. An addition-only design is presumptively papering over | `refuter` |
| `mandate` | Every compliance claim the spec makes about the host's doctrine | `compliance` |
| `shape_fit` | "This extends existing shape S" / "this creates no second way to do X" | `sweeper` |
| `sweep` | "I swept for pattern P and found only these instances" / "exclusion E is justified because…" | `sweeper` |
| `mechanism_justification` | Every mechanism the design adds, and why hardening the producer was rejected | `hardening` |
| `implementability` | **Every hook a mechanism assumes the code provides** — a chokepoint said to be single, a field said to be settable/omittable, an extension point said to exist, a seam said to distinguish two paths. Extract one claim per hook, phrased so it can be refuted by opening the file. `UNPROVEN` blocks here as `REFUTED` does | `hardening` |

## Deferrals are premises

A design disposes of what it will not do with a small vocabulary:

> *already handled* · *filed to the roadmap* · *out of scope* · *allowlisted* ·
> *the guard covers it* · *known limitation* · *fixed in step N* ·
> *inert once nothing writes it*

**Every one of these is a factual claim about the current system, not a disposal.**
Extract each as a `premise` claim with `load_bearing: true` by default. A deferral
that no longer holds returns `REFUTED` and blocks — with no special gate logic.

Two obligations follow, and both are **executions, not readings**:

1. **If the design relies on a guard, the guard gets run** — not read and reasoned
   about. Its actual output is compared against the sites the design assumes it covers.
2. **If a deferral names a condition, the condition is verified to still hold.**
   Correct-when-written code becomes a violation the moment a precondition changes
   elsewhere, and nothing marks that transition.

Carry both obligations into the claim's `statement` so the reviewer inherits them.

## The `load_bearing` flag

`load_bearing: true` when **the design's mechanism changes if the claim is false.**
Not "the claim is important" — the test is counterfactual and mechanical:

- The claim is the reason a phase exists → load-bearing.
- The claim is the reason a field, write path, or migration is shaped the way it is
  → load-bearing.
- The claim is background colour, motivation, or a restatement of a mandate the design
  merely complies with → not load-bearing.
- **Every deferral** → load-bearing by default. Downgrade only when you can state, in
  the claim, what the design would look like if the deferral were false, and it is
  the same design.
- **Precision facts are not load-bearing.** A measurement, count, citation form, or
  attribution whose exact value leaves every mechanism identical fails the
  counterfactual test by definition — 31 records instead of 30 changes no contract,
  no schema, no gate. Extract it, cite it, let a reviewer refute it — but flag it
  `load_bearing: false`, so a one-digit correction surfaces as a finding to absorb
  rather than a block. (This repo's gate record contains exactly that false-block.)

Be honest here rather than generous: `UNPROVEN` on a load-bearing claim **blocks**,
so over-flagging produces false blocks, and a rising false-block rate is what makes a
gate get rationalized past. Under-flagging is worse — it lets the mechanism-defining
assumption through unchecked. When genuinely torn, flag it and say why in the statement.

## Citations

`spec_citation` is the evidence **the spec itself** offers, POSIX, as written.
`None` when the spec offers none — and `None` is itself a finding worth stating in
the claim statement, because an uncited assertion about live code is the exact shape
this gate exists to catch. Do not go find evidence yourself; that is the reviewer's
job, and doing it here would hand the reviewer your conclusion.

## Output

A numbered list of claims, `C1`, `C2`, …, each with `family`, `statement`,
`spec_citation`, and `load_bearing`. Statements are self-contained: a reviewer sees
the spec and its own subset, so a claim that only makes sense next to its neighbours
cannot be adjudicated.

Aim for the claim count the spec earns. A dense forensic spec yields 30–60 claims; a
one-mechanism enhancement yields 8–15. Splitting a compound assertion ("X happened,
therefore Y is the owner") into its parts is always right — a reviewer can refute one
half and confirm the other, and a merged claim forces a single verdict on both.
