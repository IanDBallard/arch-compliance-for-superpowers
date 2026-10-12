"""Convergence candidate grouping.

Independent agreement under blindness is the highest-confidence signal this gate
produces (spec Amendment 2). Detecting it needs a similarity judgment, which would
put semantic reasoning in Python and violate Architectural Contract 6. So the split
is mechanical here, semantic in the controller (plan decision D2):

  * this module groups adverse findings by the file their evidence names and keeps
    only groups two or more distinct reviewers reached;
  * the controller reads each group's summaries and decides whether they are one
    finding, writing the ``ConvergedFinding`` if so.

Over-grouping is the intended failure mode: two reviewers flagging different
problems in one large file becomes a candidate the controller discards. Under-
grouping would lose the signal entirely.

Regex note: reuses ``contract.py``'s ``_FILE_LINE_RE`` rather than
declaring a second file-token expression, following the precedent
``gate.py`` already set (it imports the same name instead of redeclaring
one). An earlier version of this module forked a second regex, reasoning
that ``_FILE_LINE_RE`` has no named group to pull the bare path out of a
``path:line`` match without the line number. That reasoning did not survive
scrutiny: ``_FILE_LINE_RE``'s path portion excludes whitespace, ``:``, and
``\\``, so it structurally cannot contain a colon itself, and
``match.group(0).split(":", 1)[0]`` recovers exactly the bare path with no
second parsing step and no named group required — verified to produce
byte-identical output to the forked regex on every case this module needs,
including the ``path:13-15`` line range and the "section 3.1:2" prose edge
case. With that gap closed there is no remaining behavioral difference, so
a second expression would have been a second implementation of one
predicate — the exact anti-pattern this note originally warned about,
just introduced instead of avoided.

The alphabetic-only extension class (``[A-Za-z]+``, not ``[A-Za-z0-9]+``)
is still load-bearing and is why reuse is safe rather than merely
convenient: it is what keeps a prose reference like "section 3.1:2" from
resolving to a fabricated file named "3" — see
``test_evidence_file_does_not_mistake_a_prose_section_reference_for_a_file``.
"""
from __future__ import annotations

from acf.adr.contract import (
    ConvergenceCandidateGroup,
    ReviewerName,
    ReviewerPayload,
    _FILE_LINE_RE,
)


def evidence_file(evidence: str) -> str | None:
    """Return the case-folded POSIX file token an evidence string names, or None.

    Accepts bare ``path:line``, ``path:line-line``, and a token embedded in prose.
    The line number (and, for a range, everything from the second ``:`` on) is
    discarded: ``_FILE_LINE_RE``'s path group is ``[^\\s:\\\\]+``, which cannot
    itself contain a colon, so splitting the whole match on the first ``:``
    recovers the bare path without a second regex.
    """
    match = _FILE_LINE_RE.search(evidence)
    if match is None:
        return None
    return match.group(0).split(":", 1)[0].casefold()


def group_convergence_candidates(
    payloads: list[ReviewerPayload],
) -> list[ConvergenceCandidateGroup]:
    """Group adverse findings by evidence file; keep groups with ≥2 distinct reviewers.

    Adverse means every ``UnanchoredFinding`` plus every ``ClaimVerdict`` whose verdict
    is not ``SURVIVED``. Ordered by descending reviewer count, then by file, so the
    output is stable regardless of dispatch-completion order.
    """
    # The inner key is ``ReviewerName``, not ``str``: every value put here comes
    # from ``payload.reviewer``, which already is that Literal, and
    # ``ConvergenceCandidateGroup.reviewers`` requires it. Typing the bucket at
    # the source lets ``sorted(by_reviewer)`` infer ``list[ReviewerName]``
    # directly instead of needing a cast where the group is constructed.
    buckets: dict[str, dict[ReviewerName, list[str]]] = {}

    def add(file_token: str | None, reviewer: ReviewerName, summary: str) -> None:
        if file_token is None:
            return
        buckets.setdefault(file_token, {}).setdefault(reviewer, []).append(summary)

    for payload in payloads:
        for finding in payload.unanchored_findings:
            add(evidence_file(finding.evidence), payload.reviewer, finding.summary)
        for verdict in payload.claim_verdicts:
            if verdict.verdict == "SURVIVED":
                continue
            add(
                evidence_file(verdict.evidence),
                payload.reviewer,
                f"{verdict.id} {verdict.verdict}: {verdict.reasoning}",
            )

    groups = [
        ConvergenceCandidateGroup(
            evidence_file=file_token,
            reviewers=sorted(by_reviewer),
            summaries=[s for reviewer in sorted(by_reviewer) for s in by_reviewer[reviewer]],
        )
        for file_token, by_reviewer in buckets.items()
        if len(by_reviewer) >= 2
    ]
    groups.sort(key=lambda g: (-len(g.reviewers), g.evidence_file))
    return groups
