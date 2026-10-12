"""A host laid out unlike the origin runs the gate's storage path end to end."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

from acf.adr import (
    Claim, ClaimVerdict, DesignReviewRun, LedgerRow, UnanchoredFinding, append_row,
    classify_citations, classify_outcome, load_host_config, run_detail_path,
    write_run_detail,
)
from acf.adr.contract import RefuterPayload


def _git(repo: Path, *args: str, empty_config: Path) -> None:
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           # Hermetic: no user/system config, so no global hooks, signing or
           # autocrlf settings can change what the fixture records.
           "GIT_CONFIG_GLOBAL": str(empty_config),
           "GIT_CONFIG_NOSYSTEM": "1"}
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, env=env)


def _host(root: Path) -> Path:
    host = root / "host"
    arch = host / "config" / "architecture"
    arch.mkdir(parents=True)
    (arch / "adr.yml").write_text(
        "runs_dir: reviews/runs\nledger_path: reviews/ledger.jsonl\n", encoding="utf-8")
    (arch / "ARCHITECTURE.md").write_text("# Doctrine\n", encoding="utf-8")
    (host / "specs").mkdir()
    (host / "specs" / "THING.md").write_text("# Thing\n", encoding="utf-8")
    empty_config = root / "empty.gitconfig"
    empty_config.write_text("", encoding="utf-8")
    _git(host, "init", "-q", empty_config=empty_config)
    _git(host, "add", "-A", empty_config=empty_config)
    _git(host, "commit", "-qm", "init", empty_config=empty_config)
    return host


def _run():
    claims = [Claim(id="C1", family="shape_fit", statement="Extends S",
                    spec_citation="specs/THING.md:1", load_bearing=True)]
    payloads = [RefuterPayload(
        reviewer="refuter",
        claim_verdicts=[ClaimVerdict(id="C1", verdict="SURVIVED",
                                     evidence="src/s.py:3", reasoning="Opened it.")],
        unanchored_findings=[UnanchoredFinding(summary="none blocking",
                                               evidence="src/s.py:4", severity="advisory")],
        looked_for_but_did_not_find=["a second owner"],
    )]
    result = classify_outcome(spec_kinds=["feature"], claims=claims,
                              payloads=payloads, converged=[])
    run = DesignReviewRun(spec_path="specs/THING.md", spec_kinds=["feature"],
                          commit_sha="b" * 40, claims=claims, payloads=payloads,
                          converged=[], outcome=result.outcome)
    return run, result


def _row() -> LedgerRow:
    return LedgerRow(
        spec_path="specs/THING.md", commit_sha="b" * 40, date="2026-10-12",
        spec_kinds=["feature"], new_design_elements=1, phases=1, cited_files=1,
        touched_surfaces=["none"], surface_call_sites=0, filter_would_skip=True,
        holdout=False, outcome="CLEARED",
        findings_by_lens_severity={"refuter": {"blocking": 0, "important": 0, "advisory": 1}},
        converged_count=0, absorbed=0, rejected=0, blocks_overturned=0,
        tokens=1, wall_clock_s=1,
    )


def test_a_non_origin_host_runs_the_storage_path(tmp_path, monkeypatch):
    host = _host(tmp_path)
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)          # Review Focus 5: the process dir is not the host

    cfg = load_host_config(host)
    assert classify_citations(["specs/THING.md"], repo_root=host) == {"specs/THING.md": "current"}

    run, result = _run()
    detail = run_detail_path("specs/THING.md", version=1, date="2026-10-12",
                             runs_dir=host / cfg.runs_dir)
    write_run_detail(run, result, detail)
    assert detail.parent == host / "reviews" / "runs"
    assert detail.is_file()

    ledger = host / cfg.ledger_path
    append_row(_row(), ledger)
    lines = ledger.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2 and lines[0].startswith("{")    # preamble, then the row
    assert list(elsewhere.iterdir()) == []                  # nothing written outside the host
