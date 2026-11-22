"""The check-diff action's fixture hosts, proven against the real gate."""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from action_fixture_host import build  # noqa: E402


def _gate(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "acf.cli_check_diff", "--repo", str(repo),
         "--base", "main", "--call-site", "ci"],
        capture_output=True, text=True, encoding="utf-8",
    )


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, encoding="utf-8")


def test_planted_fixture_blocks(tmp_path):
    build(tmp_path / "h", "empty-catch")
    r = _gate(tmp_path / "h")
    assert r.returncode == 1, r.stderr
    assert "BLOCK fail-loud.empty-catch src/app.ts:" in r.stdout


def test_clean_fixture_passes(tmp_path):
    build(tmp_path / "h", "clean")
    r = _gate(tmp_path / "h")
    assert r.returncode == 0, r.stderr
    assert "No findings." in r.stdout


def test_fixture_branches(tmp_path):
    build(tmp_path / "h", "clean")
    assert _git(tmp_path / "h", "branch", "--show-current").stdout.strip() == "feature"
    assert _git(tmp_path / "h", "rev-parse", "--verify", "main").returncode == 0
