"""Terminal roll-up for an adversarial design review run.

The spec produces no separate report — findings are folded into the spec body by
its author. This roll-up is the only output, so it must be readable in one screen
and must lead with convergence, which is the highest-confidence signal the design
produces (spec Amendment 2).
"""
from __future__ import annotations

from acf.adr.contract import (
    CompliancePayload,
    DesignReviewRun,
    GateResult,
    HardeningPayload,
    SweeperPayload,
)

_NEXT_STEP = {
    "BLOCKED": "BLOCKED — do not proceed to writing-plans; revise the spec and re-run in full.",
    "CLEARED_WITH_ABSORPTIONS": (
        "CLEARED_WITH_ABSORPTIONS — fold the findings below into the spec body (or "
        "record an Implementation Decision Override with written rationale) before "
        "writing-plans."
    ),
    "CLEARED": "CLEARED — proceed to writing-plans.",
}


#: One quoted contract sentence must not push the roll-up past one screen.
_QUOTE_MAX = 80


def _plural(count: int, noun: str) -> str:
    """``"1 reviewer"``, ``"0 reviewers"``, ``"3 reviewers"`` — never re-derived per call site."""
    return f"{count} {noun}{'s' if count != 1 else ''}"


def _truncate(text: str, limit: int = _QUOTE_MAX) -> str:
    """Return ``text`` in quotes, elided past ``limit`` characters."""
    collapsed = " ".join(text.split())
    if len(collapsed) <= limit:
        return f'"{collapsed}"'
    return f'"{collapsed[:limit]}..."'


def format_rollup(run: DesignReviewRun, result: GateResult) -> str:
    """Return the terminal summary for ``run``.

    Deliberately does NOT scan its own output for backslashes. §10 applies to
    *path* fields, and every path-bearing field reaching this text is already
    ``PosixStr``-validated at construction in ``contract.py`` — that is where
    the rule belongs and where it is enforced. The prose fields the roll-up also
    prints (``ClaimVerdict.reasoning``, ``UnanchoredFinding.summary``,
    ``ResponsibilityRelationship.required_resolution``,
    ``MechanismTrace.invalid_state``, ``unstated_mandates``,
    ``DocumentConflict.contract_quote``) are plain ``str`` by design, because a
    reviewer must be able to quote a regex (``[^\\s:\\\\]+``), a LaTeX macro
    (``\\dimexpr``), or a Windows path it is *reporting as a defect*. A
    whole-text scan added nothing for its stated purpose and instead aborted the
    run: the caller prints this roll-up before appending the ledger row, so a
    single backslash in a reviewer's reasoning produced no output and no ledger
    row for an otherwise correctly-classified BLOCKED verdict.
    """
    reviewers = len(run.payloads)
    lines: list[str] = [
        f"Adversarial design review — {run.spec_path}",
        f"Outcome: {result.outcome}   (repo @ {run.commit_sha}, "
        f"kinds: {', '.join(run.spec_kinds)})",
        f"{_plural(reviewers, 'reviewer')}, "
        f"{_plural(len(run.claims), 'claim')} extracted",
        "",
        "Converged (reached independently by blind reviewers):",
    ]
    if not run.converged:
        lines.append("  No convergence — every finding was reached by one reviewer only.")
    else:
        for finding in run.converged:
            lines.append(
                f"  [{len(finding.reviewers)} reviewers] {finding.summary} "
                f"({', '.join(finding.evidence)})"
            )

    lines.append("")
    lines.append("Blocking:")
    if not result.blocking_reasons:
        lines.append("  No blocking findings.")
    else:
        lines.extend(f"  - {reason}" for reason in result.blocking_reasons)

    lines.append("")
    lines.append("Absorptions:")
    if not result.absorptions:
        lines.append("  None — no absorptions required.")
    else:
        lines.extend(f"  - {item}" for item in result.absorptions)

    two_owner = {
        responsibility: count
        for payload in run.payloads
        if isinstance(payload, SweeperPayload)
        for responsibility, count in payload.two_owner_counts.items()
        if count >= 2
    }
    if two_owner:
        lines.append("")
        lines.append("Responsibilities with two or more implementations after landing:")
        lines.extend(
            f"  - {responsibility}: {count}"
            for responsibility, count in sorted(two_owner.items())
        )

    # A spec that silently violates a mandate, or restates/contradicts an
    # Approved doc on the record, must not reach CLEARED with nothing on the
    # author's screen — the gate does not consult either field (neither is
    # one of its five blocking or four absorption triggers), so this roll-up
    # is the only place either ever surfaces. Printed only when non-empty,
    # same rule as the two-owner block above.
    unstated_mandates = sorted(
        mandate
        for payload in run.payloads
        if isinstance(payload, CompliancePayload)
        for mandate in payload.unstated_mandates
    )
    if unstated_mandates:
        lines.append("")
        lines.append("Unstated governing mandates:")
        lines.extend(f"  - {mandate}" for mandate in unstated_mandates)

    document_conflicts = sorted(
        (
            (conflict.doc_path, conflict.doc_line, conflict.conflict_kind,
             conflict.contract_quote)
            for payload in run.payloads
            if isinstance(payload, SweeperPayload)
            for conflict in payload.document_conflicts
        )
    )
    if document_conflicts:
        lines.append("")
        lines.append("Document conflicts:")
        # The quote is what makes "previously rejected on the record" actionable
        # — a bare doc_path:line tells the author only that something over there
        # disagrees. Truncated so one long contract sentence cannot push the
        # roll-up past one screen.
        lines.extend(
            f"  - {doc_path}:{doc_line} ({conflict_kind}) "
            f"{_truncate(contract_quote)}"
            for doc_path, doc_line, conflict_kind, contract_quote in document_conflicts
        )

    # Failure by silence. The spec: a mechanism that REPAIRS rather than REFUSES
    # "is flagged regardless of rung" (ADVERSARIAL_DESIGN_REVIEW.md). The gate
    # has no trigger for it — ``repairs_rather_than_refuses`` is not one of its
    # five blocking or four absorption triggers, and the under-hardening
    # absorption keys on rung distance, which a silent repair at the correct
    # rung does not trip. So, exactly like the two sections above, this roll-up
    # is the only path from the flag to the author's screen. Printed only when
    # non-empty.
    silent_paths = sorted(
        mechanism
        for payload in run.payloads
        if isinstance(payload, HardeningPayload)
        for mechanism in payload.silent_paths
    )
    if silent_paths:
        lines.append("")
        lines.append("Mechanisms that repair rather than refuse (failure by silence):")
        lines.extend(f"  - {mechanism}" for mechanism in silent_paths)

    lines.append("")
    lines.append(_NEXT_STEP[result.outcome])

    return "\n".join(lines)
