#!/usr/bin/env python3
"""PreToolUse hook: force a permission prompt around ACF approval.

An agent may start ``acf-allow``, and only the user's answer at a Claude Code
permission prompt lets it run. This hook returns ``ask`` for a shell command that
mentions approval and for a file tool aimed at the per-user approval store, and
``deny`` in ``bypassPermissions`` mode, where nobody is shown a prompt.

It runs in every repository whatever ``.acf/enabled`` says, because the store it
guards is per user. It imports the standard library and ``acf.repo`` only. It is
registered with ``"onFailure": "block"``: once a needle is found, any failure
exits 2 and blocks the call. The common path reads stdin and exits 0.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_HOOKS_DIR = Path(__file__).resolve().parent
_PLUGIN_ROOT = _HOOKS_DIR.parent
_PYTHON_ROOT = _PLUGIN_ROOT / "python"
if str(_PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(_PYTHON_ROOT))

from acf.repo import STORE_REL

#: A shell command matches on any of these, case-insensitively. ``acf.cli_allow`` is
#: the module form (``python -m acf.cli_allow``). A file tool's path matches on the
#: store's file name only.
APPROVAL_NEEDLES = ("acf-allow", "acf.cli_allow", STORE_REL.name)

_SHELL_TOOLS = ("Bash", "PowerShell")
_FILE_TOOLS = ("Write", "Edit", "MultiEdit", "NotebookEdit")

_DENY_REASON = (
    "ACF approval needs your answer at a permission prompt, which bypass mode skips. "
    "Leave bypass mode, or run acf-allow in your own terminal."
)
_ASK_REASON = (
    "ACF approval: allowing this approves the host detector code the agent just "
    "summarized, for every worktree of this repository whose files match. "
    "Deny if you have not read the summary."
)


def _subject_matches(payload: object) -> bool:
    if not isinstance(payload, dict):
        raise TypeError(f"hook input is {type(payload).__name__}, not an object")
    tool = payload.get("tool_name")
    tool_input = payload.get("tool_input")
    if tool in _SHELL_TOOLS:
        if not isinstance(tool_input, dict):
            raise TypeError("tool_input is not an object")
        subject = tool_input.get("command", "")
        needles = APPROVAL_NEEDLES
    elif tool in _FILE_TOOLS:
        if not isinstance(tool_input, dict):
            raise TypeError("tool_input is not an object")
        subject = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
        needles = (STORE_REL.name,)
    else:
        return False
    if not isinstance(subject, str):
        raise TypeError(f"the subject is {type(subject).__name__}, not a string")
    lowered = subject.lower()
    return any(needle.lower() in lowered for needle in needles)


def _decision(decision: str, reason: str) -> str:
    return json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": decision,
                "permissionDecisionReason": reason,
            }
        }
    )


def main() -> int:
    raw = sys.stdin.buffer.read()
    lowered = raw.lower()
    if not any(needle.encode().lower() in lowered for needle in APPROVAL_NEEDLES):
        return 0
    try:
        payload = json.loads(raw.decode("utf-8"))
        if not _subject_matches(payload):
            return 0
        if payload.get("permission_mode") == "bypassPermissions":
            print(_decision("deny", _DENY_REASON))
        else:
            print(_decision("ask", _ASK_REASON))
        return 0
    except Exception as exc:  # fail-loud.bare-except-ok: a needle was found, so any failure must block the call (exit 2) rather than let an unreviewed approval through
        print(f"acf: approval hook failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
