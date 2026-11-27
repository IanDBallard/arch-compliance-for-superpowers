from __future__ import annotations

from pathlib import Path

import pytest

from acf.approval import (
    HELPER_LIMIT,
    approval_rows,
    file_digests,
    fingerprint,
    store_path,
)
from acf.cli_allow import main as allow_main
from acf.cli_approval_status import main
from acf.detectors import load_gate_registry
from acf.exceptions import GitError
from acf.repo import MANDATES_REL

from test_cli_allow import _host, _llm, _repo


def test_status_prints_state_and_review(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _repo(tmp_path, [_host("host-a")])
    assert main(["--repo", str(repo)]) == 0
    out = capsys.readouterr().out
    lines = out.splitlines()
    assert lines[0] == "state: MISSING"
    registry = load_gate_registry(repo, repo / MANDATES_REL)
    rows = approval_rows(registry)
    assert f"fingerprint: {fingerprint(rows, file_digests(repo, rows))}" in out
    assert HELPER_LIMIT in out
    assert "host-a" in out


def test_status_fingerprint_is_accepted_by_allow(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _repo(tmp_path, [_host("host-a")])
    assert main(["--repo", str(repo)]) == 0
    printed = next(
        line for line in capsys.readouterr().out.splitlines() if line.startswith("fingerprint: ")
    )
    assert allow_main(["--repo", str(repo), "--fingerprint", printed.split(": ", 1)[1]]) == 0
    capsys.readouterr()
    assert main(["--repo", str(repo)]) == 0
    assert capsys.readouterr().out.splitlines()[0] == "state: APPROVED"


def test_status_writes_nothing(tmp_path: Path) -> None:
    repo = _repo(tmp_path, [_host("host-a")])
    assert not store_path().exists()
    assert main(["--repo", str(repo)]) == 0
    assert not store_path().exists()


def test_status_no_host_rows(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = _repo(tmp_path, [_llm("llm_fail_loud")])
    assert main(["--repo", str(repo)]) == 0
    assert "no host detector rows" in capsys.readouterr().out
    assert not store_path().exists()


def test_status_missing_detector_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _repo(tmp_path, [_host("host-a", file="absent.py")])
    assert main(["--repo", str(repo)]) == 1
    assert "acf: " in capsys.readouterr().err


def test_status_reports_key_git_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _repo(tmp_path, [_host("host-a")])

    def boom(_repo: Path) -> None:
        raise GitError("cannot compute the approval key for x: y")

    monkeypatch.setattr("acf.approval.git_common_dir", boom)
    assert main(["--repo", str(repo)]) == 1
    assert "acf: cannot compute the approval key" in capsys.readouterr().err
