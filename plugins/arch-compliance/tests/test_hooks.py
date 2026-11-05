"""Unit tests for ACF Claude Code hooks."""

from __future__ import annotations

import json
import os
import re
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


def _set_call_sites(repo: Path, mandate_id: str, call_sites: str) -> None:
    """Rewrite one fixture row's call_sites flow list."""
    path = repo / "config" / "architecture" / "mandates.yml"
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"(- id: {re.escape(mandate_id)}\n(?:  .*\n)*?  call_sites: )\[[^\]]*\]"
    )
    text, count = pattern.subn(lambda m: m.group(1) + call_sites, text)
    assert count == 1, mandate_id
    path.write_text(text, encoding="utf-8")


def test_gate_hook_mode_warn_finding_stays_exit_0_with_context(tmp_path: Path) -> None:
    repo = _seed_host(tmp_path, enabled=True, mandates=True)
    _set_call_sites(repo, "no-shims.hasattr", "[ci, hook]")
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


def test_gate_does_not_report_a_row_without_the_hook_site(tmp_path: Path) -> None:
    repo = _seed_host(tmp_path, enabled=True, mandates=True)
    _set_call_sites(repo, "fail-loud.bare-except", "[ci]")
    bad = repo / "bad.py"
    bad.write_text(
        "def f():\n    try:\n        g()\n    except Exception:\n        pass\n",
        encoding="utf-8",
    )
    proc = _run(GATE, "--repo", str(repo), "--format", "text", str(bad), cwd=repo)
    assert proc.returncode == 0
    assert "fail-loud.bare-except" not in proc.stdout


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


def test_inject_fails_loud_when_doctrine_document_missing(tmp_path: Path) -> None:
    """Review Focus 3: enabled, registry present, doctrine document absent.

    Previously the hook substituted a placeholder sentence and exited 0, so a
    subagent received a constraint block that looked complete.
    """
    repo = _seed_host(tmp_path, enabled=True, mandates=True)
    (repo / "config" / "architecture" / "ARCHITECTURE.md").unlink()

    proc = subprocess.run(
        [sys.executable, str(INJECT), "--repo", str(repo)],
        capture_output=True,
        text=True,
        input="",
    )
    assert proc.returncode == 1, proc.stdout
    assert "ARCHITECTURE.md" in proc.stderr
    assert "not found" in proc.stderr.lower()
    assert "use mandates above" not in proc.stdout


def test_inject_succeeds_when_doctrine_document_present(tmp_path: Path) -> None:
    """The happy path still works and carries the real doctrine text."""
    repo = _seed_host(tmp_path, enabled=True, mandates=True)
    (repo / "config" / "architecture" / "ARCHITECTURE.md").write_text(
        "# Host doctrine\n\nDISTINCTIVE_DOCTRINE_MARKER\n", encoding="utf-8"
    )

    proc = subprocess.run(
        [sys.executable, str(INJECT), "--repo", str(repo)],
        capture_output=True,
        text=True,
        input="",
    )
    assert proc.returncode == 0, proc.stderr
    assert "DISTINCTIVE_DOCTRINE_MARKER" in proc.stdout


def test_gate_fails_loud_when_enabled_without_mandates(tmp_path: Path) -> None:
    """The gate's own refusal has never had a test; pin it before it moves."""
    repo = _seed_host(tmp_path, enabled=True, mandates=False)

    proc = subprocess.run(
        [sys.executable, str(GATE), "--repo", str(repo)],
        capture_output=True,
        text=True,
        input="",
    )
    assert proc.returncode == 1
    assert "mandates" in proc.stderr.lower()


def test_inject_doctrine_refusal_message_is_unchanged(tmp_path: Path) -> None:
    """The refusal moved to acf.loader.require_file; its text did not change."""
    repo = _seed_host(tmp_path, enabled=True, mandates=True)
    doctrine = repo / "config" / "architecture" / "ARCHITECTURE.md"
    doctrine.unlink()
    proc = subprocess.run(
        [sys.executable, str(INJECT), "--repo", str(repo)],
        capture_output=True, text=True, input="",
    )
    assert proc.returncode == 1
    assert f"acf: doctrine document not found: {doctrine.as_posix()}" in proc.stderr


# ---------------------------------------------------------------- host detectors

_HOST_MODULE = '''import json
from pathlib import Path

from acf.detectors.host import HostHit


def _log(params, entry):
    with open(params["log"], "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\\n")


def scan_ast(text, path, added_lines, *, tree, params):
    _log(params, ["ast", path])
    for n, line in enumerate(text.splitlines(), 1):
        if "HOST_MARKER" in line:
            yield HostHit(path=path, line=n, message="host ast marker")


def scan_guard(repo_root, changed_files, *, params):
    _log(params, ["guard", params["name"], list(changed_files)])
    for rel in changed_files:
        if rel.endswith(".md"):
            yield HostHit(path=rel, line=1, message="host guard on a document")
'''


def _host_row(mid: str, detection: str, fn: str, sites: str, log: Path, *, name: str = "") -> str:
    languages = "python" if detection == "ast" else "none"
    return f"""- id: {mid}
  title: {mid}
  severity: BLOCK
  detection: {detection}
  detector: hostdet/rules.py:{fn}
  languages: {languages}
  call_sites: {sites}
  exemption_tokens: []
  status: enforced
  arch_anchor: "# Fail loud"
  params:
    log: "{log.as_posix()}"
    name: "{name}"
"""


def _seed_host_rows(tmp_path: Path, rows: str, *, enabled: bool = True) -> Path:
    repo = _seed_host(tmp_path, enabled=enabled, mandates=True)
    mandates = repo / "config" / "architecture" / "mandates.yml"
    mandates.write_text(mandates.read_text(encoding="utf-8") + "\n" + rows, encoding="utf-8")
    (repo / "hostdet").mkdir()
    (repo / "hostdet" / "rules.py").write_text(_HOST_MODULE, encoding="utf-8")
    return repo


def _read_log(log: Path) -> list:
    if not log.is_file():
        return []
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]


def test_gate_disabled_does_not_import_a_host_module(tmp_path: Path) -> None:
    marker = tmp_path / "imported.txt"
    log = tmp_path / "log.jsonl"
    repo = _seed_host_rows(
        tmp_path, _host_row("host.ast-marker", "ast", "scan_ast", "[hook]", log), enabled=False
    )
    (repo / "hostdet" / "rules.py").write_text(
        f"open({marker.as_posix()!r}, 'w').close()\nraise RuntimeError('imported')\n",
        encoding="utf-8",
    )
    edited = repo / "a.py"
    edited.write_text("x = 1  # HOST_MARKER\n", encoding="utf-8")
    proc = _run(GATE, "--repo", str(repo), "--quiet-disabled", str(edited), cwd=repo)
    assert proc.returncode == 0, proc.stderr
    assert not marker.exists()
    assert "Traceback" not in proc.stderr


def test_gate_unknown_detector_exits_1_when_enabled(tmp_path: Path) -> None:
    repo = _seed_host(tmp_path, enabled=True, mandates=True)
    mandates = repo / "config" / "architecture" / "mandates.yml"
    mandates.write_text(
        mandates.read_text(encoding="utf-8").replace(
            "detector: no_shims_hasattr", "detector: no_such_detector"
        ),
        encoding="utf-8",
    )
    edited = repo / "a.py"
    edited.write_text("x = 1\n", encoding="utf-8")
    proc = _run(GATE, "--repo", str(repo), "--format", "text", str(edited), cwd=repo)
    assert proc.returncode == 1
    assert "no_such_detector" in proc.stderr


def test_gate_runs_hook_host_rows_and_not_ci_only_host_guards(tmp_path: Path) -> None:
    log = tmp_path / "log.jsonl"
    rows = (
        _host_row("host.ast-marker", "ast", "scan_ast", "[hook]", log)
        + _host_row("host.doc-guard", "guard", "scan_guard", "[hook]", log, name="hook")
        + _host_row("host.ci-guard", "guard", "scan_guard", "[ci]", log, name="ci")
    )
    repo = _seed_host_rows(tmp_path, rows)
    code = repo / "a.py"
    code.write_text("x = 1  # HOST_MARKER\n", encoding="utf-8")
    doc = repo / "notes.md"
    doc.write_text("plain\n", encoding="utf-8")
    proc = _run(
        GATE, "--repo", str(repo), "--format", "json", str(code), str(doc), cwd=repo
    )
    assert proc.returncode == 1, proc.stderr
    found = sorted((f["mandate_id"], f["path"]) for f in json.loads(proc.stdout))
    assert found == [("host.ast-marker", "a.py"), ("host.doc-guard", "notes.md")]
    entries = _read_log(log)
    assert ["ast", "a.py"] in entries
    assert ["guard", "hook", ["a.py", "notes.md"]] in entries
    assert not [e for e in entries if e[0] == "guard" and e[1] == "ci"]


def test_gate_edited_file_outside_repo_yields_no_finding_and_no_host_call(
    tmp_path: Path,
) -> None:
    log = tmp_path / "log.jsonl"
    rows = _host_row("host.ast-marker", "ast", "scan_ast", "[hook]", log) + _host_row(
        "host.doc-guard", "guard", "scan_guard", "[hook]", log, name="hook"
    )
    repo = _seed_host_rows(tmp_path, rows)
    outside_dir = tmp_path / "elsewhere"
    outside_dir.mkdir()
    outside = outside_dir / "bad.py"
    outside.write_text(
        "def f():\n    try:\n        g()\n    except Exception:\n        pass\n"
        "x = 1  # HOST_MARKER\n",
        encoding="utf-8",
    )
    proc = _run(GATE, "--repo", str(repo), "--format", "json", str(outside), cwd=repo)
    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout) == []
    entries = _read_log(log)
    assert not [e for e in entries if e[0] == "ast"]
    assert entries == [["guard", "hook", []]]


def test_gate_native_absolute_path_is_reported_under_its_posix_key(tmp_path: Path) -> None:
    """Review Focus 1: str(abs_path) is Windows-native on Windows."""
    log = tmp_path / "log.jsonl"
    repo = _seed_host_rows(tmp_path, _host_row("host.ast-marker", "ast", "scan_ast", "[hook]", log))
    (repo / "pkg").mkdir()
    edited = repo / "pkg" / "a.py"
    edited.write_text(
        "def f():\n    try:\n        g()\n    except Exception:\n        pass\n"
        "x = 1  # HOST_MARKER\n",
        encoding="utf-8",
    )
    proc = _run(GATE, "--repo", str(repo), "--format", "json", str(edited), cwd=repo)
    assert proc.returncode == 1, proc.stderr
    found = sorted((f["mandate_id"], f["path"]) for f in json.loads(proc.stdout))
    assert found == [("fail-loud.bare-except", "pkg/a.py"), ("host.ast-marker", "pkg/a.py")]
    assert ["ast", "pkg/a.py"] in _read_log(log)
