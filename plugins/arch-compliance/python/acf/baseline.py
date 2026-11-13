"""Compliance baseline + report-only drift for architecture-review.

Counts are per (mandate_id, subsystem). LLM auditors are non-deterministic, so
drift compares COUNTS, never finding identities. Drift never fails a run — it is
informational. Fail loud on a malformed baseline.
"""
from __future__ import annotations

from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from acf.exceptions import BaselineError
from acf.loader import load_model_file, write_text_record


class BaselineCell(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mandate_id: str
    subsystem: str
    count: int = Field(ge=0)


class Baseline(BaseModel):
    model_config = ConfigDict(extra="forbid")
    generated_at: str
    commit: str
    invocation: str
    counts: list[BaselineCell]


class DriftRow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mandate_id: str
    subsystem: str
    baseline_count: int
    current_count: int
    delta: int


class DriftReport(BaseModel):
    """Report-only drift; never gates CI or exit status."""

    model_config = ConfigDict(extra="forbid")
    rows: list[DriftRow]


class Locatable(Protocol):
    """Anything with a mandate and a POSIX path (e.g. ``AuditorFinding``)."""

    mandate_id: str
    path: str


def subsystem_of(posix_path: str, *, prefixes: Sequence[str]) -> str:
    """Map a finding path to a subsystem.

    With declared ``prefixes`` the longest prefix the normalised path starts with
    wins; an unmatched path is ``other``. With no prefixes, the first path segment
    is the subsystem (``other`` for a bare file name).
    """
    normalized = posix_path.replace("\\", "/")
    if prefixes:
        matches = [prefix for prefix in prefixes if normalized.startswith(prefix)]
        return max(matches, key=len) if matches else "other"
    parts = [p for p in normalized.split("/") if p]
    if len(parts) >= 2:
        return f"{parts[0]}/"
    return "other"


def aggregate(
    findings: Iterable[Locatable], *, prefixes: Sequence[str]
) -> dict[tuple[str, str], int]:
    """Fold findings into counts keyed by (mandate_id, subsystem)."""
    counts: dict[tuple[str, str], int] = {}
    for finding in findings:
        key = (finding.mandate_id, subsystem_of(finding.path, prefixes=prefixes))
        counts[key] = counts.get(key, 0) + 1
    return counts


def save_baseline(path: Path, data: Baseline) -> Path:
    """Write baseline JSON. Paths in error messages use POSIX form."""
    return write_text_record(path, data.model_dump_json(indent=2) + "\n", error=BaselineError)


def load_baseline(path: Path) -> Baseline:
    """Load + validate baseline. Fail loud on missing/malformed.

    Absence is a real state decided by the CALLER (existence check before load).
    The loader itself never returns None. Refusals are ``AcfInputError``, shared
    with every other input file; ``BaselineError`` now covers only the write
    side, where ACF is the producer rather than the reader.
    """
    return load_model_file(path, Baseline, subject="baseline", fmt="json")


def compute_drift(
    current: dict[tuple[str, str], int],
    baseline: Baseline,
) -> DriftReport:
    """Report-only drift rows. Worsening-first. No ratchet / no fail.

    Baseline cells whose mandate did not run are omitted, so a facet-filtered
    run never reports them as spuriously resolved.
    """
    current_mandates = {mandate_id for (mandate_id, _sub) in current}
    baseline_map = {(c.mandate_id, c.subsystem): c.count for c in baseline.counts}
    keys = set(current)
    for mandate_id, subsystem in baseline_map:
        if mandate_id in current_mandates:
            keys.add((mandate_id, subsystem))
    rows = [
        DriftRow(
            mandate_id=mandate_id,
            subsystem=subsystem,
            baseline_count=baseline_map.get((mandate_id, subsystem), 0),
            current_count=current.get((mandate_id, subsystem), 0),
            delta=current.get((mandate_id, subsystem), 0)
            - baseline_map.get((mandate_id, subsystem), 0),
        )
        for (mandate_id, subsystem) in keys
    ]
    rows.sort(key=lambda r: (-r.delta, r.mandate_id, r.subsystem))
    return DriftReport(rows=rows)


def render_drift_section(report: DriftReport, baseline: Baseline) -> str:
    """Markdown drift section for the architecture-review report."""
    lines: list[str] = [
        "## Drift vs baseline",
        "",
        (
            f"_Baseline {baseline.commit} @ {baseline.generated_at}. "
            "Counts may be LLM-derived and non-deterministic — small deltas are noise. "
            "Report-only; never fails the run._"
        ),
        "",
        "| Mandate | Subsystem | Baseline | Current | Δ |",
        "|---|---|---|---|---|",
    ]
    for row in report.rows:
        sign = f"+{row.delta}" if row.delta > 0 else str(row.delta)
        lines.append(
            f"| {row.mandate_id} | {row.subsystem} | {row.baseline_count} "
            f"| {row.current_count} | {sign} |"
        )
    if not report.rows:
        lines.append("| _no overlapping cells_ | | | | |")
    return "\n".join(lines) + "\n"
