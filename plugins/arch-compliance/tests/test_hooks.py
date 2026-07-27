"""Unit tests for ACF Claude Code hooks."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1] / "hooks"
INJECT = HOOKS / "inject_constraints.py"
GATE = HOOKS / "posttooluse_gate.py"
FIXTURES = Path(__file__).parent / "fixtures"
MANDATES_SRC = FIXTURES / "mandates_valid.yml"
ARCH_SRC = (
    Path(__file__).resolve().parents[1] / "profiles" / "python-service" / "ARCHITECTURE.md"
)


def _run(script: Path, *args: str, cwd: Path, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=cwd,
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
    )


def _seed_host(tmp_path: Path, *, enabled: bool, mandates: bool) -> Path:
    repo = tmp_path / "host"
    repo.mkdir()
    if mandates:
        dest = repo / "config" / "architecture"
        dest.mkdir(parents=True)
        shutil.copy(MANDATES_SRC, dest / "mandates.yml")
        shutil.copy(ARCH_SRC, dest / "ARCHITECTURE.md")
    if enabled:
        marker = repo / ".acf"
        marker.mkdir(parents=True)
        (marker / "enabled").write_text("", encoding="utf-8")
    return repo


def test_inject_noop_without_enabled(tmp_path: Path) -> None:
    repo = _seed_host(tmp_path, enabled=False, mandates=False)
    proc = _run(INJECT, "--repo", str(repo), "--quiet-disabled", cwd=repo)
    assert proc.returncode == 0
    assert proc.stdout.strip() == ""


def test_inject_fails_loud_when_enabled_without_mandates(tmp_path: Path) -> None:
    repo = _seed_host(tmp_path, enabled=True, mandates=False)
    proc = _run(INJECT, "--repo", str(repo), cwd=repo)
    assert proc.returncode == 1
    assert "mandates missing" in proc.stderr


def test_inject_prints_constraint_block(tmp_path: Path) -> None:
    repo = _seed_host(tmp_path, enabled=True, mandates=True)
    proc = _run(INJECT, "--repo", str(repo), "--format", "text", cwd=repo)
    assert proc.returncode == 0
    assert "fail-loud.bare-except" in proc.stdout
    assert "Fail loud" in proc.stdout


def test_inject_hook_json_format(tmp_path: Path) -> None:
    repo = _seed_host(tmp_path, enabled=True, mandates=True)
    payload = json.dumps(
        {"cwd": str(repo), "hook_event_name": "SubagentStart", "agent_type": "Explore"}
    )
    proc = _run(INJECT, "--format", "hook", cwd=repo, stdin=payload)
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    ctx = data["hookSpecificOutput"]["additionalContext"]
    assert "fail-loud.bare-except" in ctx


def test_gate_noop_without_enabled(tmp_path: Path) -> None:
    repo = _seed_host(tmp_path, enabled=False, mandates=False)
    bad = repo / "bad.py"
    bad.write_text("try:\n  x()\nexcept Exception:\n  pass\n", encoding="utf-8")
    proc = _run(GATE, "--repo", str(repo), "--quiet-disabled", str(bad), cwd=repo)
    assert proc.returncode == 0


def test_gate_detects_bare_except(tmp_path: Path) -> None:
    repo = _seed_host(tmp_path, enabled=True, mandates=True)
    bad = repo / "bad.py"
    bad.write_text(
        "def f():\n    try:\n        g()\n    except Exception:\n        pass\n",
        encoding="utf-8",
    )
    proc = _run(GATE, "--repo", str(repo), "--format", "text", str(bad), cwd=repo)
    assert proc.returncode == 1
    assert "fail-loud.bare-except" in proc.stdout


def test_gate_reads_paths_from_stdin_json(tmp_path: Path) -> None:
    repo = _seed_host(tmp_path, enabled=True, mandates=True)
    bad = repo / "bad.py"
    bad.write_text(
        "def f():\n    try:\n        g()\n    except Exception:\n        pass\n",
        encoding="utf-8",
    )
    payload = json.dumps(
        {
            "cwd": str(repo),
            "hook_event_name": "PostToolUse",
            "tool_name": "Edit",
            "tool_input": {"file_path": str(bad)},
        }
    )
    proc = _run(GATE, "--format", "hook", cwd=repo, stdin=payload)
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert "fail-loud.bare-except" in data["hookSpecificOutput"]["additionalContext"]
