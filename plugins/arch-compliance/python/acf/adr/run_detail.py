"""Persist a review run's findings, so they outlive the run that produced them.

The ledger is counts-only by design (see ``LEDGER_PREAMBLE``): it answers "did a
review happen, what did it cost, what did it conclude". It cannot answer "what
did it *say*" — and ``absorbed``/``rejected`` are adjudicated against findings,
not against counts.

Without this module that adjudication was done from the spec's own account of
itself, which is how a §14 citation recorded as absorbed — but never applied —
survived two reviews and inflated a backfill by one. ``architecture_review`` has
written a ``_last_run.json`` sidecar since it shipped; this is the same idea in
the form this skill's output actually takes (prose findings, not counts), and in
a **tracked** location, because the run that motivated it wrote its detail to
gitignored ``.claude/tmp/``.

§10: every persisted path is POSIX. §3: an unwritable sidecar raises rather than
being skipped — skipping it reproduces the exact failure it exists to prevent
while looking like success.
"""
from __future__ import annotations

from pathlib import Path

from acf.adr.contract import (
    CompliancePayload,
    DesignReviewRun,
    GateResult,
    HardeningPayload,
    SweeperPayload,
)
from acf.exceptions import RunDetailWriteError

#: Tracked sibling of the ledger. NOT ``.claude/tmp`` — that is gitignored, and a
#: detail file nobody can read after the session is the problem, not the fix.
RUNS_DIR = "docs/reviews/adr_runs"


def run_detail_path(
    spec_path: str, *, version: int, date: str, runs_dir: Path | str = RUNS_DIR
) -> Path:
    """Return the detail path for a run: ``<runs_dir>/<SPEC_STEM>_v<N>_<date>.md``.

    Keyed by spec stem + version + date so successive reviews of the same spec
    sit side by side in reading order rather than overwriting one another — the
    series is the point (v4 said canonical, v5 retracted, v6 could not check).
    """
    stem = Path(spec_path).stem
    return Path(runs_dir) / f"{stem}_v{version}_{date}.md"


def _verdict_lines(payload) -> list[str]:
    out: list[str] = []
    for verdict in payload.claim_verdicts:
        out.append(f"#### {verdict.id} — {verdict.verdict}")
        out.append(f"- evidence: `{verdict.evidence}`")
        out.append(f"- reasoning: {verdict.reasoning}")
        out.append("")
    return out


def _claim_lines(claims) -> list[str]:
    """The extracted claims, statements included — verdicts-by-ID alone lose
    the statement when the run's session ends, and both the response-record
    author (M1) and the next run's carryover adjudication (M3) need it."""
    out = ["## Claims", ""]
    for claim in claims:
        load = " [load-bearing]" if claim.load_bearing else ""
        disposition = (
            f" ({claim.revision_disposition})" if claim.revision_disposition else ""
        )
        out.append(f"- **{claim.id}** [{claim.family}]{load}{disposition}: "
                   f"{claim.statement}")
        out.append(f"  - spec citation: `{claim.spec_citation}`")
    out.append("")
    return out


def render_run_detail(run: DesignReviewRun, result: GateResult) -> str:
    """Return the full markdown record of ``run`` — every finding, verbatim.

    Deliberately not elided. ``format_rollup`` truncates for one-screen reading;
    this is the archive the author triages from and the record a later
    ``absorbed``/``rejected`` amendment is adjudicated against, so nothing here
    is shortened.
    """
    lines: list[str] = [
        "# Adversarial design review — full detail",
        "",
        f"Spec: `{run.spec_path}` @ `{run.commit_sha}`",
        f"Kinds: {', '.join(run.spec_kinds)}",
        f"Outcome: **{run.outcome}**",
        f"Claims: {len(run.claims)} · Reviewers: {len(run.payloads)} · "
        f"Converged: {len(run.converged)}",
        "",
    ]

    if result.blocking_reasons:
        lines += ["## Blocking reasons", ""]
        lines += [f"- {reason}" for reason in result.blocking_reasons]
        lines.append("")
    if result.absorptions:
        lines += ["## Absorptions", ""]
        lines += [f"- {item}" for item in result.absorptions]
        lines.append("")
    if run.converged:
        lines += ["## Converged findings", ""]
        for finding in run.converged:
            lines.append(
                f"- [{len(finding.reviewers)} reviewers: "
                f"{', '.join(finding.reviewers)}] {finding.summary}"
            )
            lines += [f"  - evidence: `{item}`" for item in finding.evidence]
        lines.append("")

    for payload in run.payloads:
        lines += [f"## {payload.reviewer}", "", "### Claim verdicts", ""]
        lines += _verdict_lines(payload)

        lines += ["### Unanchored findings", ""]
        # Distinct name from the ``finding`` bound at :90: that one is a
        # ConvergedFinding, and reusing the variable made mypy infer that type for
        # this loop too, so ``.severity`` (which only UnanchoredFinding has) read
        # as an attribute error. Runtime was always correct; the types were not.
        for unanchored in payload.unanchored_findings:
            lines.append(f"- **{unanchored.severity}**: {unanchored.summary}")
            lines.append(f"  - evidence: `{unanchored.evidence}`")
        lines.append("")

        lines += ["### Looked for but did not find", ""]
        lines += [f"- {item}" for item in payload.looked_for_but_did_not_find]
        lines.append("")

        if isinstance(payload, CompliancePayload) and payload.unstated_mandates:
            lines += ["### Unstated mandates", ""]
            lines += [f"- {item}" for item in payload.unstated_mandates]
            lines.append("")
        if isinstance(payload, SweeperPayload):
            lines += ["### Relationships", ""]
            for rel in payload.relationships:
                lines.append(
                    f"- {rel.relationship}: `{rel.new_element}` — "
                    f"responsibility `{rel.responsibility}` — "
                    f"existing `{rel.existing_site}`"
                )
                lines.append(f"  - resolution: {rel.required_resolution}")
                if rel.non_merge_justification:
                    lines.append(f"  - non-merge: {rel.non_merge_justification}")
            lines += ["", "### Two-owner counts", ""]
            lines += [
                f"- {resp}: {count}"
                for resp, count in payload.two_owner_counts.items()
            ]
            lines += ["", "### Document conflicts", ""]
            for conflict in payload.document_conflicts:
                lines.append(
                    f"- `{conflict.doc_path}:{conflict.doc_line}` "
                    f"({conflict.conflict_kind}): {conflict.contract_quote}"
                )
            lines.append("")
        if isinstance(payload, HardeningPayload):
            lines += ["### Mechanism traces", ""]
            for trace in payload.mechanism_traces:
                lines.append(f"- **{trace.mechanism}**")
                lines.append(f"  - invalid state: {trace.invalid_state}")
                lines.append(f"  - producer: `{trace.producer}`")
                lines.append(
                    f"  - rung {trace.design_rung} (highest applicable "
                    f"{trace.highest_applicable_rung}); "
                    f"repairs={trace.repairs_rather_than_refuses}"
                )
                if trace.hardening_rejected_because:
                    lines.append(
                        f"  - hardening rejected because: "
                        f"{trace.hardening_rejected_because}"
                    )
                lines.append(f"  - spec citation: `{trace.spec_citation}`")
            lines.append("")

    lines += _claim_lines(run.claims)
    return "\n".join(lines).rstrip() + "\n"


def write_run_detail(run: DesignReviewRun, result: GateResult, path: Path) -> None:
    """Write the run detail to ``path``, creating parents.

    Raises ``RunDetailWriteError`` on any OS failure — never skip the write.
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_run_detail(run, result), encoding="utf-8")
    except OSError as exc:
        raise RunDetailWriteError(
            f"could not write the run detail to {path.as_posix()}: {exc}. "
            "The ledger row alone cannot support a later absorbed/rejected "
            "amendment — do not proceed without the detail."
        ) from exc
