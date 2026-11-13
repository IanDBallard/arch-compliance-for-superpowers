"""Auditor payload parsing, inline exemptions and the review report."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import ValidationError

from acf.agent_payload import extract_json_block
from acf.enforcement import token_exempted
from acf.exceptions import AuditorContractViolationError, ReportWriteError
from acf.loader import write_text_record
from acf.repo import RepoTree
from acf.review.contract import AuditorFinding, AuditorPayload
from acf.review.host import ReviewHostConfig
from acf.review.rules import ReviewRow

SEVERITY_ORDER = ("blocking", "important", "nit", "suggestion")


@dataclass
class GroupResult:
    group: str
    status: Literal["OK", "FAILED"]
    payload: AuditorPayload | None
    raw: str
    error: str | None


def _file_lines(tree: RepoTree, path: str) -> list[str] | None:
    """The lines of ``path`` split on newline, a final terminator not counting as a line; None if unreadable."""
    location = tree.file(path)
    if location is None:
        return None
    try:
        text = location.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    lines = text.split("\n")
    if len(lines) > 1 and lines[-1] == "":
        lines.pop()
    return lines


def parse_auditor_payload(
    payload: str,
    *,
    group: str,
    rows: list[ReviewRow],
    surfaces: dict[str, list[str]],
    tree: RepoTree,
) -> AuditorPayload:
    data = extract_json_block(payload, subject=group, error=AuditorContractViolationError)
    try:
        parsed = AuditorPayload.model_validate(data)
    except ValidationError as exc:
        raise AuditorContractViolationError(
            f"group {group!r}: payload does not match the auditor contract: {exc}"
        ) from exc
    if parsed.group != group:
        raise AuditorContractViolationError(
            f"group {group!r}: payload names group {parsed.group!r}"
        )
    known = {row.mandate.id for row in rows}
    cache: dict[str, list[str] | None] = {}
    for finding in parsed.findings:
        if finding.mandate_id not in known:
            raise AuditorContractViolationError(
                f"group {group!r}: finding names mandate {finding.mandate_id!r}, "
                f"which is not among the group's rows {sorted(known)}"
            )
        if finding.path not in surfaces.get(finding.mandate_id, []):
            raise AuditorContractViolationError(
                f"group {group!r}: finding path {finding.path!r} is not in the surface "
                f"of mandate {finding.mandate_id!r}"
            )
        if finding.path not in cache:
            cache[finding.path] = _file_lines(tree, finding.path)
        lines = cache[finding.path]
        if lines is None:
            raise AuditorContractViolationError(
                f"group {group!r}: cannot read {finding.path!r} to check line {finding.line}"
            )
        if finding.line > len(lines):
            raise AuditorContractViolationError(
                f"group {group!r}: finding line {finding.line} is past the end of "
                f"{finding.path!r} ({len(lines)} lines)"
            )
    return parsed


def apply_exemptions(
    findings: list[AuditorFinding], rows: dict[str, ReviewRow], tree: RepoTree
) -> tuple[list[AuditorFinding], int]:
    kept: list[AuditorFinding] = []
    exempted = 0
    cache: dict[str, list[str] | None] = {}
    for finding in findings:
        row = rows.get(finding.mandate_id)
        tokens = row.mandate.exemption_tokens if row is not None else []
        if not tokens:
            kept.append(finding)
            continue
        if finding.path not in cache:
            cache[finding.path] = _file_lines(tree, finding.path)
        lines = cache[finding.path]
        if (
            lines is not None
            and finding.line <= len(lines)
            and token_exempted(lines[finding.line - 1], tokens)
        ):
            exempted += 1
        else:
            kept.append(finding)
    return kept, exempted


def render_report(
    *,
    commit: str,
    invocation: str,
    results: list[GroupResult],
    findings: list[AuditorFinding],
    exempted: int,
    rollup_md: str,
) -> str:
    out = [
        "# Architecture review",
        "",
        f"- Commit: {commit}",
        f"- Invocation: {invocation}",
        "",
        "## Groups",
        "",
        "| Group | Status | Findings |",
        "| --- | --- | --- |",
    ]
    for result in results:
        count = len(result.payload.findings) if result.payload is not None else 0
        out.append(f"| {result.group} | {result.status} | {count} |")
    out += ["", "## Findings", ""]
    if not findings:
        out += ["No findings.", ""]
    for severity in SEVERITY_ORDER:
        group = [f for f in findings if f.severity == severity]
        if not group:
            continue
        out += [f"### {severity}", ""]
        for f in group:
            out += [
                f"- `{f.path}:{f.line}` — {f.rule} — {f.mandate_id}",
                f"  - Why: {f.why}",
                f"  - Snippet: `{f.snippet}`",
                f"  - Suggested fix: {f.suggested_fix}",
            ]
        out.append("")
    out += [f"{exempted} findings exempted by inline tokens.", "", rollup_md, ""]
    failed = [r for r in results if r.status == "FAILED"]
    if failed:
        out += ["## Failed groups", ""]
        for r in failed:
            out += [f"### {r.group}", "", f"Error: {r.error}", "", "```", r.raw, "```", ""]
    return "\n".join(out)


def write_report(tree: RepoTree, cfg: ReviewHostConfig, text: str, today: date) -> Path:
    """Write the report under ``report_dir`` without overwriting a same-day report."""
    stem = f"ARCHITECTURE_REVIEW_{today.isoformat()}"
    n = 1
    while True:
        name = f"{stem}.md" if n == 1 else f"{stem}_{n}.md"
        rel = f"{cfg.report_dir.rstrip('/')}/{name}"
        target = tree.contained(rel)
        if target is None:
            raise ReportWriteError(f"report path {rel!r} escapes the repository root")
        if not target.exists():
            return write_text_record(target, text, error=ReportWriteError)
        n += 1
