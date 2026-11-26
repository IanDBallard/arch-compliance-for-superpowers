"""Probe: which PreToolUse outcomes stop a Bash call in ``bypassPermissions`` mode.

Run from the repository root, naming the Claude Code binary to probe:

    python docs/design/evidence/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT/bypass_hook_probe.py <claude>

For each variant the probe makes a fresh project directory whose
``.claude/settings.json`` holds that variant's hook or rule, then runs

    <claude> -p <PROMPT> --permission-mode bypassPermissions
             --permission-prompts none --setting-sources project
             --model haiku --output-format json

in it. ``--setting-sources project`` keeps the user's own settings, hooks and
plugins out. ``--permission-prompts none`` means nobody answers a prompt, so a
call that would prompt is denied instead of waiting. The prompt asks the model
to run ``echo probe > marker.txt`` once. The probe records whether
``marker.txt`` exists afterwards (the call ran), the ``permission_mode`` the
hook received on stdin, and the result's ``permission_denials``.

Variants:
  control   hook logs its input and exits 0 with no output
  json_deny hook prints a PreToolUse ``permissionDecision: deny`` and exits 0
  json_ask  hook prints a PreToolUse ``permissionDecision: ask`` and exits 0
  exit2     hook prints a reason to stderr and exits 2
  ask_rule  logging hook as in control, plus ``permissions.ask: ["Bash(echo probe*)"]``
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

PROMPT = (
    "Use the Bash tool to run exactly this command, once, and nothing else: "
    "echo probe > marker.txt\n"
    "If the call is blocked or denied, do not retry and do not try another way. "
    "Then reply with the single word DONE."
)

HOOK = r'''
import json, sys
variant, log = sys.argv[1], sys.argv[2]
data = json.load(sys.stdin)
with open(log, "a", encoding="utf-8") as fh:
    fh.write(json.dumps({"tool_name": data.get("tool_name"),
                         "permission_mode": data.get("permission_mode"),
                         "command": (data.get("tool_input") or {}).get("command")}) + "\n")
if variant in ("json_deny", "json_ask"):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": variant.split("_")[1],
        "permissionDecisionReason": "probe " + variant}}))
    sys.exit(0)
if variant == "exit2":
    print("probe exit2", file=sys.stderr)
    sys.exit(2)
sys.exit(0)
'''

VARIANTS = ["control", "json_deny", "json_ask", "exit2", "ask_rule"]


def run(claude: str, variant: str, root: Path) -> dict:
    proj = root / variant
    (proj / ".claude").mkdir(parents=True)
    hook = root / "hook.py"
    log = proj / "hook_log.jsonl"
    hook_variant = "control" if variant == "ask_rule" else variant
    settings: dict = {
        "hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [{
            "type": "command",
            "command": f'python "{hook.as_posix()}" {hook_variant} "{log.as_posix()}"',
        }]}]},
    }
    if variant == "ask_rule":
        settings["permissions"] = {"ask": ["Bash(echo probe*)"]}
    (proj / ".claude" / "settings.json").write_text(json.dumps(settings), encoding="utf-8")
    proc = subprocess.run(
        [claude, "-p", PROMPT, "--permission-mode", "bypassPermissions",
         "--permission-prompts", "none", "--setting-sources", "project",
         "--model", "haiku", "--output-format", "json"],
        cwd=proj, capture_output=True, check=False, timeout=300,
    )
    out = proc.stdout.decode("utf-8", "replace")
    try:
        result = json.loads(out)
    except json.JSONDecodeError:
        result = {"unparsed_stdout": out[-2000:], "stderr": proc.stderr.decode("utf-8", "replace")[-2000:]}
    hook_calls = (
        [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
        if log.exists() else []
    )
    return {
        "variant": variant,
        "exit_code": proc.returncode,
        "call_ran (marker.txt exists)": (proj / "marker.txt").exists(),
        "hook_calls": hook_calls,
        "permission_denials": [
            {"tool_name": d.get("tool_name"), "command": (d.get("tool_input") or {}).get("command")}
            for d in result.get("permission_denials", [])
        ],
        "final_text": (result.get("result") or "")[:200],
        **({"raw": result} if "unparsed_stdout" in result else {}),
    }


def main() -> None:
    claude = sys.argv[1]
    version = subprocess.run([claude, "--version"], capture_output=True, text=True, check=True)
    print(version.stdout.strip())
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "hook.py").write_text(HOOK, encoding="utf-8")
        for variant in (sys.argv[2:] or VARIANTS):
            print(json.dumps(run(claude, variant, root), ensure_ascii=True, indent=2)
                  .replace(root.as_posix(), "<tmp>"))


if __name__ == "__main__":
    main()
