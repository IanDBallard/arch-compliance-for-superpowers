"""Staleness, provenance and the roll-up, against real temporary git repositories."""
from __future__ import annotations

import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

from acf.baseline import Baseline, BaselineCell, save_baseline
from acf.review.aggregator import GroupResult
from acf.review import rollup
from acf.review.contract import AuditorFinding, AuditorPayload
from acf.review.host import ReviewHostConfig
from acf.review.rollup import exit_status, provenance, render_rollup, staleness

NOW = datetime(2026, 11, 12, tzinfo=timezone.utc)


def _git(repo: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, encoding="utf-8", check=True
    )
    return done.stdout.strip()


def _repo(tmp_path: Path) -> tuple[Path, str, str]:
    """A repo with two commits; returns (repo, first sha, second sha)."""
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "T")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "core.autocrlf", "false")
    (tmp_path / "old.py").write_text('x = "é"\n', encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "one")
    first = _git(tmp_path, "rev-parse", "HEAD")
    (tmp_path / "new.py").write_text("y = 1\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "two")
    return tmp_path, first, _git(tmp_path, "rev-parse", "HEAD")


def _baseline(commit: str, generated_at: str = "2026-11-11T00:00:00+00:00") -> Baseline:
    return Baseline(
        generated_at=generated_at,
        commit=commit,
        invocation="test",
        counts=[BaselineCell(mandate_id="M1", subsystem="other", count=1)],
    )


def _finding(path: str, line: int = 1) -> AuditorFinding:
    return AuditorFinding(
        mandate_id="M1", path=path, line=line, snippet="s", severity="nit",
        rule="r", why="w", suggested_fix="f",
    )


def _cfg(**over) -> ReviewHostConfig:
    values = dict(
        report_dir="reports", baseline_path="base.json", baseline_max_age_days=30,
        baseline_max_commits=1, packs=[], subsystems=[], exclude=[],
    )
    values.update(over)
    return ReviewHostConfig(**values)


def test_staleness_by_age(tmp_path):
    repo, first, _ = _repo(tmp_path)
    old = _baseline(first, "2026-01-01T00:00:00")  # naive -> UTC
    s = staleness(repo, old, max_age_days=30, max_commits=50, now=NOW)
    assert s.age_days == (NOW - datetime(2026, 1, 1, tzinfo=timezone.utc)).days
    assert len(s.warnings) == 1 and "days" in s.warnings[0]
    assert s.unknown is None


def test_staleness_by_commits(tmp_path):
    repo, first, _ = _repo(tmp_path)
    s = staleness(repo, _baseline(first), max_age_days=30, max_commits=0, now=NOW)
    assert s.commits_behind == 1
    assert len(s.warnings) == 1 and "commits" in s.warnings[0]


def test_fresh_baseline_has_no_warning(tmp_path):
    repo, _, second = _repo(tmp_path)
    s = staleness(repo, _baseline(second), max_age_days=30, max_commits=50, now=NOW)
    assert s.warnings == [] and s.unknown is None and s.commits_behind == 0


def test_unknown_commit_reports_git_text(tmp_path):
    repo, _, _ = _repo(tmp_path)
    s = staleness(repo, _baseline("deadbeef"), max_age_days=30, max_commits=50, now=NOW)
    assert s.commits_behind is None
    assert s.unknown is not None and s.unknown.startswith("staleness unknown: ")
    assert "deadbeef" in s.unknown


def test_provenance_classes(tmp_path):
    repo, first, _ = _repo(tmp_path)
    assert provenance(repo, _finding("old.py"), first) == ("pre-baseline", None)
    assert provenance(repo, _finding("new.py"), first) == ("post-baseline", None)
    (repo / "new.py").write_text("y = 2\n", encoding="utf-8")
    assert provenance(repo, _finding("new.py"), first) == ("uncommitted", None)
    cls, err = provenance(repo, _finding("old.py", line=9), first)  # tracked, blame fails
    assert cls == "unresolved" and err


def test_provenance_untracked_file_is_uncommitted(tmp_path):
    repo, first, _ = _repo(tmp_path)
    (repo / "fresh.py").write_text("z = 1\n", encoding="utf-8")
    assert provenance(repo, _finding("fresh.py"), first) == ("uncommitted", None)


def test_provenance_all_zero_commit_of_any_length_is_uncommitted(tmp_path, monkeypatch):
    calls = []

    def fake_run_git(repo, *args):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, "0" * 64 + " 1 1 1\n", "")

    monkeypatch.setattr(rollup, "run_git", fake_run_git)
    assert provenance(tmp_path, _finding("a.py"), "abc") == ("uncommitted", None)
    assert [a[0] for a in calls] == ["blame"]


def test_provenance_unresolved_when_baseline_commit_unknown(tmp_path):
    repo, _, _ = _repo(tmp_path)
    cls, err = provenance(repo, _finding("old.py"), "deadbeef")
    assert cls == "unresolved" and err


def test_review_focus_2_non_ascii_line_is_pre_baseline(tmp_path):
    repo, first, _ = _repo(tmp_path)
    assert provenance(repo, _finding("old.py"), first)[0] == "pre-baseline"


def test_rollup_without_baseline(tmp_path):
    repo, _, _ = _repo(tmp_path)
    results = [GroupResult(group="g", status="OK", payload=None, raw="", error=None)]
    text = render_rollup(repo=repo, cfg=_cfg(), findings=[_finding("old.py")], results=results, now=NOW)
    assert "no baseline (run --update-baseline to set one)" in text
    assert "## Roll-up" in text
    for heading in ("## Drift", "## Staleness", "## Provenance"):
        assert heading not in text


def test_rollup_with_baseline(tmp_path):
    repo, first, _ = _repo(tmp_path)
    save_baseline(repo / "base.json", _baseline(first))
    results = [
        GroupResult(group="g", status="OK", payload=None, raw="", error=None),
        GroupResult(group="h", status="FAILED", payload=None, raw="", error="boom"),
    ]
    findings = [_finding("old.py"), _finding("new.py"), _finding("old.py", line=9)]
    text = render_rollup(repo=repo, cfg=_cfg(), findings=findings, results=results, now=NOW)
    for heading in ("## Roll-up", "## Drift", "## Staleness", "## Provenance"):
        assert heading in text
    assert "no baseline" not in text
    assert "old.py:9" in text
    assert "fresh" in text  # 1 commit behind is within baseline_max_commits=1
    assert "pre-baseline: 1" in text and "post-baseline: 1" in text and "unresolved: 1" in text
    assert "FAILED: 1" in text and "OK: 1" in text
    assert exit_status(results) == 1


def test_rollup_counts_auditor_error_notes(tmp_path):
    repo, _, _ = _repo(tmp_path)
    results = [
        GroupResult(
            group="g", status="OK",
            payload=AuditorPayload(group="g", files_examined=2, findings=[], errors=["a", "b"]),
            raw="", error=None,
        ),
        GroupResult(
            group="h", status="OK",
            payload=AuditorPayload(group="h", files_examined=1, findings=[], errors=["c"]),
            raw="", error=None,
        ),
        GroupResult(group="k", status="FAILED", payload=None, raw="", error="boom"),
    ]
    text = render_rollup(repo=repo, cfg=_cfg(), findings=[], results=results, now=NOW)
    assert "- Auditor error notes: 3" in text
