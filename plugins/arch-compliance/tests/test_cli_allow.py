from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

from acf.approval import ApprovalState, check_approval, read_store, store_path
from acf.cli_allow import main
from acf.detectors import load_gate_registry
from acf.exceptions import UnknownDetectorError
from acf.registry import HOOK_CALL_SITES
from acf.repo import MANDATES_REL, RepoTree

PY_DIR = Path(__file__).resolve().parents[1] / "python"
RULES_SOURCE = "def check(*a, **k):\n    return []\n"


def _host(mid: str, *, file: str = "rules.py") -> str:
    return f"""- id: {mid}
  title: {mid}
  severity: BLOCK
  detection: guard
  detector: hostdet/{file}:check
  languages: none
  call_sites: [hook]
  exemption_tokens: []
  status: enforced
  arch_anchor: "# Fail loud"
  params:
    name: "a"
"""


def _llm(detector: str) -> str:
    return f"""- id: llm-row
  title: llm-row
  severity: WARN
  detection: llm
  detector: {detector}
  languages: none
  call_sites: [audit]
  exemption_tokens: []
  status: enforced
  arch_anchor: "# Fail loud"
"""


def _repo(tmp_path: Path, rows: list[str]) -> Path:
    repo = tmp_path / "repo"
    (repo / "hostdet").mkdir(parents=True)
    (repo / "hostdet" / "rules.py").write_text(RULES_SOURCE, encoding="utf-8")
    mandates = repo / MANDATES_REL
    mandates.parent.mkdir(parents=True)
    mandates.write_text("\n".join(rows), encoding="utf-8")
    return repo


def test_allow_prints_and_writes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = _repo(tmp_path, [_host("host-a"), _host("host-b")])
    assert main(["--repo", str(repo)]) == 0
    out = capsys.readouterr().out
    digest = hashlib.sha256((repo / "hostdet" / "rules.py").read_bytes()).hexdigest()
    for fragment in ("host-a", "host-b", "hostdet/rules.py:check", "hostdet/rules.py", digest,
                     "imported modules are not covered"):
        assert fragment in out
    assert RepoTree(repo).root.as_posix() in read_store(store_path()).repos


def test_allow_no_host_rows_writes_nothing(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = _repo(tmp_path, [_llm("llm_fail_loud")])
    assert main(["--repo", str(repo)]) == 0
    assert not store_path().exists()
    assert "No host detector rows" in capsys.readouterr().out


def test_allow_missing_detector_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = _repo(tmp_path, [_host("host-a", file="absent.py")])
    assert main(["--repo", str(repo)]) == 1
    assert "absent.py" in capsys.readouterr().err
    assert not store_path().exists()


def test_allow_store_inside_repo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _repo(tmp_path, [_host("host-a")])
    monkeypatch.setenv("HOME", str(repo))
    monkeypatch.setenv("USERPROFILE", str(repo))
    assert main(["--repo", str(repo)]) == 1
    assert "inside the repository" in capsys.readouterr().err


def test_allow_revoke(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = _repo(tmp_path, [_host("host-a")])
    assert main(["--repo", str(repo)]) == 0
    capsys.readouterr()
    assert main(["--repo", str(repo), "--revoke"]) == 0
    assert "Removed" in capsys.readouterr().out
    assert RepoTree(repo).root.as_posix() not in read_store(store_path()).repos


def test_allow_revoke_without_entry(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    repo = _repo(tmp_path, [_host("host-a")])
    assert main(["--repo", str(repo), "--revoke"]) == 0
    assert "nothing to remove" in capsys.readouterr().out


def test_allow_relative_repo_matches_absolute_check(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _repo(tmp_path, [_host("host-a")])
    monkeypatch.chdir(repo)
    assert main(["--repo", "."]) == 0
    registry = load_gate_registry(repo, repo / MANDATES_REL)
    assert check_approval(repo, registry, HOOK_CALL_SITES).state is ApprovalState.APPROVED


def test_load_gate_registry_refuses_unknown_prompt_id(tmp_path: Path) -> None:
    repo = _repo(tmp_path, [_llm("no-such-prompt")])
    with pytest.raises(UnknownDetectorError):
        load_gate_registry(repo, repo / MANDATES_REL)


def test_detectors_import_does_not_import_httpx() -> None:
    env = {**os.environ, "PYTHONPATH": PY_DIR.as_posix()}
    result = subprocess.run(
        [sys.executable, "-c", "import acf.detectors, sys; print('httpx' in sys.modules)"],
        capture_output=True,
        text=True,
        env=env,
        check=True,
    )
    assert result.stdout.strip() == "False"
