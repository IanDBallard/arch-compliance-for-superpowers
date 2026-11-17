"""The review roll-up: group and finding counts, drift, staleness and provenance.

Drift, staleness and provenance are report-only; none affects the exit status.
Every git invocation goes through ``acf.diff.run_git``, which returns the exit
status as data; a missing ``git`` raises.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from acf.baseline import (
    Baseline,
    aggregate,
    compute_drift,
    load_baseline,
    render_drift_section,
)
from acf.diff import run_git
from acf.repo import RepoTree
from acf.review.aggregator import GroupResult
from acf.review.contract import AuditorFinding
from acf.review.host import ReviewHostConfig

Provenance = Literal["pre-baseline", "post-baseline", "uncommitted", "unresolved"]
_PROVENANCE_ORDER: tuple[Provenance, ...] = (
    "pre-baseline", "post-baseline", "uncommitted", "unresolved",
)
_SEVERITIES = ("blocking", "important", "nit", "suggestion")


@dataclass
class Staleness:
    age_days: int | None
    commits_behind: int | None
    warnings: list[str] = field(default_factory=list)
    unknown: str | None = None


def staleness(
    repo: Path, baseline: Baseline, *, max_age_days: int, max_commits: int, now: datetime
) -> Staleness:
    """Age and commit distance of the baseline, with a warning per threshold exceeded."""
    generated = datetime.fromisoformat(baseline.generated_at)
    if generated.tzinfo is None:
        generated = generated.replace(tzinfo=timezone.utc)
    age_days = (now - generated).days
    result = Staleness(age_days=age_days, commits_behind=None)
    if age_days > max_age_days:
        result.warnings.append(
            f"baseline is {age_days} days old (max {max_age_days}); "
            "run --update-baseline after the next full audit"
        )
    done = run_git(repo, "rev-list", "--count", f"{baseline.commit}..HEAD")
    if done.returncode != 0:
        result.unknown = "staleness unknown: " + done.stderr.strip()
        return result
    result.commits_behind = int(done.stdout.strip())
    if result.commits_behind > max_commits:
        result.warnings.append(
            f"baseline is {result.commits_behind} commits behind HEAD (max {max_commits}); "
            "run --update-baseline after the next full audit"
        )
    return result


def provenance(
    repo: Path, finding: AuditorFinding, baseline_commit: str
) -> tuple[Provenance, str | None]:
    """Classify a finding's line against the baseline commit by blame and ancestry.

    A line git attributes to no commit (all-zero id), or a path git does not track,
    is ``uncommitted``.
    """
    blame = run_git(
        repo, "blame", "--porcelain", "-L", f"{finding.line},{finding.line}", "--", finding.path
    )
    if blame.returncode != 0:
        tracked = run_git(repo, "ls-files", "--error-unmatch", "--", finding.path)
        if tracked.returncode != 0:
            return "uncommitted", None
        return "unresolved", blame.stderr.strip()
    tokens = blame.stdout.split()
    commit = tokens[0] if tokens else ""
    if commit and set(commit) == {"0"}:  # git's all-zero id for a not-yet-committed line, any hash length
        return "uncommitted", None
    ancestry = run_git(repo, "merge-base", "--is-ancestor", commit, baseline_commit)
    if ancestry.returncode == 0:
        return "pre-baseline", None
    if ancestry.returncode == 1:
        return "post-baseline", None
    return "unresolved", ancestry.stderr.strip()


def exit_status(results: list[GroupResult]) -> int:
    """1 when any group FAILED, else 0."""
    return 1 if any(r.status == "FAILED" for r in results) else 0


def render_rollup(
    *,
    repo: Path,
    cfg: ReviewHostConfig,
    findings: list[AuditorFinding],
    results: list[GroupResult],
    now: datetime,
) -> str:
    """The roll-up Markdown; drift, staleness and provenance only with a baseline."""
    groups = Counter(r.status for r in results)
    severities = Counter(f.severity for f in findings)
    error_notes = sum(len(r.payload.errors) for r in results if r.payload is not None)
    lines = [
        "## Roll-up",
        "",
        f"- Groups: OK: {groups['OK']}, FAILED: {groups['FAILED']}",
        "- Findings by severity: "
        + ", ".join(f"{s}: {severities[s]}" for s in _SEVERITIES),
        f"- Auditor error notes: {error_notes}",
        "",
    ]
    baseline_file = RepoTree(repo).file(cfg.baseline_path)
    if baseline_file is None:
        lines.append("no baseline (run --update-baseline to set one)")
        return "\n".join(lines) + "\n"
    baseline = load_baseline(baseline_file)

    report = compute_drift(aggregate(findings, prefixes=cfg.subsystems), baseline)
    lines.append(render_drift_section(report, baseline).rstrip("\n"))
    lines.append("")

    stale = staleness(
        repo,
        baseline,
        max_age_days=cfg.baseline_max_age_days,
        max_commits=cfg.baseline_max_commits,
        now=now,
    )
    lines += ["## Staleness", ""]
    if stale.unknown is not None:
        lines.append(stale.unknown)
    if stale.warnings:
        lines += [f"- {w}" for w in stale.warnings]
    elif stale.unknown is None:
        lines.append("fresh")
    lines.append("")

    classified = [(f, *provenance(repo, f, baseline.commit)) for f in findings]
    counts = Counter(cls for _f, cls, _e in classified)
    lines += ["## Provenance", ""]
    lines += [f"- {cls}: {counts[cls]}" for cls in _PROVENANCE_ORDER]
    for f, cls, error in classified:
        if cls == "unresolved":
            lines.append(f"- unresolved {f.mandate_id} {f.path}:{f.line}: {error}")
    return "\n".join(lines) + "\n"
