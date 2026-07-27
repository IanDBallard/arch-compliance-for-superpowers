"""Unit tests for ACF Claude Code hooks."""

from __future__ import annotations

import json
import os
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


def _run(
    script: Path,
    *args: str,
    cwd: Path,
    stdin: str | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        cwd=cwd,
        input=stdin,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def _no_deps_env(tmp_path: Path) -> dict[str, str]:
    """Environment where importing pydantic/yaml fails, simulating a host
    machine that has not pip-installed the acf package."""
    poison = tmp_path / "poison"
    poison.mkdir(exist_ok=True)
    for mod in ("pydantic", "yaml"):
        (poison / f"{mod}.py").write_text(
            f"raise ImportError('{mod} unavailable (poisoned by test)')\n",
            encoding="utf-8",
        )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(poison)
    return env


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


def test_inject_noop_without_enabled_even_without_deps(tmp_path: Path) -> None:
    repo = _seed_host(tmp_path, enabled=False, mandates=False)
    proc = _run(
        INJECT,
        "--repo",
        str(repo),
        "--quiet-disabled",
        cwd=repo,
        env=_no_deps_env(tmp_path),
    )
    assert proc.returncode == 0, proc.stderr
    assert "Traceback" not in proc.stderr


def test_inject_clear_error_when_enabled_without_deps(tmp_path: Path) -> None:
    repo = _seed_host(tmp_path, enabled=True, mandates=True)
    proc = _run(INJECT, "--repo", str(repo), cwd=repo, env=_no_deps_env(tmp_path))
    assert proc.returncode == 1
    assert "acf:" in proc.stderr
    assert "pip install" in proc.stderr
    assert "Traceback" not in proc.stderr


def test_gate_noop_without_enabled_even_without_deps(tmp_path: Path) -> None:
    repo = _seed_host(tmp_path, enabled=False, mandates=False)
    bad = repo / "bad.py"
    bad.write_text("try:\n  x()\nexcept Exception:\n  pass\n", encoding="utf-8")
    proc = _run(
        GATE,
        "--repo",
        str(repo),
        "--quiet-disabled",
        str(bad),
        cwd=repo,
        env=_no_deps_env(tmp_path),
    )
    assert proc.returncode == 0, proc.stderr
    assert "Traceback" not in proc.stderr


def test_gate_clear_error_when_enabled_without_deps(tmp_path: Path) -> None:
    repo = _seed_host(tmp_path, enabled=True, mandates=True)
    bad = repo / "bad.py"
    bad.write_text("try:\n  x()\nexcept Exception:\n  pass\n", encoding="utf-8")
    proc = _run(
        GATE, "--repo", str(repo), str(bad), cwd=repo, env=_no_deps_env(tmp_path)
    )
    assert proc.returncode == 1
    assert "acf:" in proc.stderr
    assert "pip install" in proc.stderr
    assert "Traceback" not in proc.stderr


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


def test_gate_hook_mode_block_finding_exits_2_with_stderr(tmp_path: Path) -> None:
    """BLOCK findings must reach Claude as blocking feedback (exit 2 +
    stderr), not as ignorable additionalContext."""
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
    assert proc.returncode == 2
    assert "fail-loud.bare-except" in proc.stderr


def test_gate_hook_mode_warn_finding_stays_exit_0_with_context(tmp_path: Path) -> None:
    repo = _seed_host(tmp_path, enabled=True, mandates=True)
    warn = repo / "warn.py"
    warn.write_text(
        "def f(o):\n    return hasattr(o, 'x')\n",
        encoding="utf-8",
    )
    payload = json.dumps(
        {
            "cwd": str(repo),
            "hook_event_name": "PostToolUse",
            "tool_name": "Edit",
            "tool_input": {"file_path": str(warn)},
        }
    )
    proc = _run(GATE, "--format", "hook", cwd=repo, stdin=payload)
    assert proc.returncode == 0
    data = json.loads(proc.stdout)
    assert "no-shims.hasattr" in data["hookSpecificOutput"]["additionalContext"]


def test_gate_unenforced_mandate_not_reported(tmp_path: Path) -> None:
    repo = _seed_host(tmp_path, enabled=True, mandates=True)
    mandates_path = repo / "config" / "architecture" / "mandates.yml"
    text = mandates_path.read_text(encoding="utf-8").replace(
        "status: enforced", "status: unenforced"
    )
    mandates_path.write_text(text, encoding="utf-8")
    bad = repo / "bad.py"
    bad.write_text(
        "def f():\n    try:\n        g()\n    except Exception:\n        pass\n",
        encoding="utf-8",
    )
    proc = _run(GATE, "--repo", str(repo), "--format", "text", str(bad), cwd=repo)
    assert proc.returncode == 0
    assert "fail-loud.bare-except" not in proc.stdout


def test_gate_registry_exemption_token_exempts(tmp_path: Path) -> None:
    repo = _seed_host(tmp_path, enabled=True, mandates=True)
    bad = repo / "bad.py"
    bad.write_text(
        "def f():\n"
        "    try:\n"
        "        g()\n"
        "    except Exception:  # fail-loud.bare-except-ok: CLI top-level guard\n"
        "        raise SystemExit(1)\n",
        encoding="utf-8",
    )
    proc = _run(GATE, "--repo", str(repo), "--format", "text", str(bad), cwd=repo)
    assert proc.returncode == 0
    assert "fail-loud.bare-except" not in proc.stdout
