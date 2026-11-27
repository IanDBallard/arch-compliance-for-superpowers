"""The PreToolUse approval hook: prompts, silent passes, failure, registration, imports."""
from __future__ import annotations

import ast
import fnmatch
import importlib.util
import json
import os
import re
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
        shell("echo {} > ~/.acf/approvals.json"),
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


@pytest.mark.parametrize(
    "payload",
    [
        {"tool_name": "Bash", "tool_input": "acf-allow"},
        {"tool_name": "Bash", "tool_input": {"command": ["acf-allow"]}},
    ],
)
def test_wrong_shape_with_needle_fails_closed(payload, tmp_path) -> None:
    proc = run_hook(payload, tmp_path)
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


SETUP_SKILL = PLUGIN_ROOT / "skills" / "acf-setup" / "SKILL.md"
ASK_RULE = re.compile(r"`(Bash|PowerShell|Edit)\([^)`]*\)`")


def _needles_and_store_name() -> tuple[tuple[str, ...], str]:
    spec = importlib.util.spec_from_file_location("approval_prompt_under_test", HOOK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.APPROVAL_NEEDLES, module.STORE_REL.name


def test_ask_rules_match_needles() -> None:
    needles, store_name = _needles_and_store_name()
    text = SETUP_SKILL.read_text(encoding="utf-8")
    rules = [(m.group(1), m.group(0)[len(m.group(1)) + 2 : -2]) for m in ASK_RULE.finditer(text)]
    assert rules, "acf-setup offers no permissions.ask rule"
    shell = [arg for tool, arg in rules if tool != "Edit"]
    edit = [arg for tool, arg in rules if tool == "Edit"]
    for arg in shell:
        assert any(n.lower() in arg.lower() for n in needles), arg
    store = (Path.home() / ".acf" / store_name).as_posix()
    for arg in edit:
        glob = arg.replace("~", Path.home().as_posix(), 1)
        assert fnmatch.fnmatch(store, glob), arg
    for needle in ("acf-allow", "acf.cli_allow"):
        assert any(needle in arg for arg in shell), needle
    assert any(fnmatch.fnmatch(store, arg.replace("~", Path.home().as_posix(), 1)) for arg in edit)
