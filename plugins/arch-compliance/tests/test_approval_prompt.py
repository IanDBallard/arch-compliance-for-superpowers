"""The PreToolUse approval hook: prompts, silent passes, failure, registration, imports."""
from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
HOOK = PLUGIN_ROOT / "hooks" / "approval_prompt.py"
HOOKS_JSON = PLUGIN_ROOT / "hooks" / "hooks.json"

ASK_REASON = (
    "ACF approval: allowing this approves the host detector code the agent just "
    "summarized, for every worktree of this repository whose files match. "
    "Deny if you have not read the summary."
)
DENY_REASON = (
    "ACF approval needs your answer at a permission prompt, which bypass mode skips. "
    "Leave bypass mode, or run acf-allow in your own terminal."
)


def run_hook(payload, cwd) -> subprocess.CompletedProcess:
    data = payload if isinstance(payload, bytes) else json.dumps(payload).encode("utf-8")
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=data,
        capture_output=True,
        cwd=cwd,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )


def decision(proc: subprocess.CompletedProcess) -> dict:
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout.decode("utf-8"))["hookSpecificOutput"]
    assert out["hookEventName"] == "PreToolUse"
    return out


def shell(command: str, tool: str = "Bash", mode: str = "default", **extra) -> dict:
    return {
        "tool_name": tool,
        "tool_input": {"command": command, **extra},
        "permission_mode": mode,
    }


def file_tool(path: str, tool: str = "Write", mode: str = "default", **extra) -> dict:
    return {
        "tool_name": tool,
        "tool_input": {"file_path": path, **extra},
        "permission_mode": mode,
    }


@pytest.mark.parametrize(
    "payload",
    [
        shell("acf-allow --fingerprint abc"),
        shell("acf-allow --fingerprint abc", tool="PowerShell"),
        shell("python -m acf.cli_allow"),
        shell("cd x && ACF-ALLOW"),
        file_tool(str(Path.home() / ".acf" / "approvals.json")),
        file_tool(r"C:\Users\x\.acf\APPROVALS.JSON"),
        {"tool_name": "NotebookEdit", "tool_input": {"notebook_path": "/h/.acf/approvals.json"}},
        # no permission_mode: not bypass, so ask
        {"tool_name": "Bash", "tool_input": {"command": "acf-allow"}},
    ],
)
def test_prompts(payload, tmp_path) -> None:
    out = decision(run_hook(payload, tmp_path))
    assert out["permissionDecision"] == "ask"
    assert out["permissionDecisionReason"] == ASK_REASON


def test_prompts_without_enabled_marker(tmp_path) -> None:
    assert not (tmp_path / ".acf").exists()
    out = decision(run_hook(shell("acf-allow"), tmp_path))
    assert out["permissionDecision"] == "ask"


def test_bypass_mode_denies(tmp_path) -> None:
    out = decision(run_hook(shell("acf-allow", mode="bypassPermissions"), tmp_path))
    assert out["permissionDecision"] == "deny"
    assert out["permissionDecisionReason"] == DENY_REASON


@pytest.mark.parametrize("mode", ["default", "bypassPermissions"])
@pytest.mark.parametrize(
    "payload",
    [
        shell("acf-approval-status"),
        shell("ls"),
        shell("pytest plugins/arch-compliance/tests/test_cli_allow.py"),
        shell("git add plugins/arch-compliance/python/acf/cli_allow.py"),
        shell("ls", description="then acf-allow"),
        file_tool("docs/x.md", content="run acf-allow, see approvals.json"),
        file_tool("plugins/arch-compliance/python/acf/cli_allow.py", tool="Edit"),
    ],
)
def test_silent(payload, mode, tmp_path) -> None:
    payload = {**payload, "permission_mode": mode}
    proc = run_hook(payload, tmp_path)
    assert proc.returncode == 0
    assert proc.stdout == b""


def test_malformed_json_with_needle_fails_closed(tmp_path) -> None:
    proc = run_hook(b"{not json acf-allow", tmp_path)
    assert proc.returncode == 2
    assert proc.stderr.decode("utf-8").startswith("acf: approval hook failed")


def test_invalid_utf8_with_needle_fails_closed(tmp_path) -> None:
    proc = run_hook(b'{"tool_input":{"command":"acf-allow \xff"}}', tmp_path)
    assert proc.returncode == 2
    assert proc.stderr.decode("utf-8").startswith("acf: approval hook failed")


def test_malformed_json_without_needle_passes(tmp_path) -> None:
    proc = run_hook(b"{not json", tmp_path)
    assert proc.returncode == 0
    assert proc.stdout == b""


def test_hooks_json_registers_the_hook() -> None:
    config = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
    (entry,) = config["hooks"]["PreToolUse"]
    assert entry["matcher"] == "Bash|PowerShell|Write|Edit|MultiEdit|NotebookEdit"
    (hook,) = entry["hooks"]
    assert hook["type"] == "command"
    assert hook["command"] == 'python "${CLAUDE_PLUGIN_ROOT}/hooks/approval_prompt.py"'
    assert hook["timeout"] == 10
    assert hook["onFailure"] == "block"


def test_hook_imports_only_stdlib_and_acf_repo() -> None:
    tree = ast.parse(HOOK.read_text(encoding="utf-8"))
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            assert node.level == 0, "relative import"
            modules.append(node.module or "")
    assert modules
    for module in modules:
        assert module == "acf.repo" or module.split(".")[0] in sys.stdlib_module_names, module
