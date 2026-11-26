"""Probe: how a Claude Code build turns a PreToolUse hook's outcome into a
permission decision, read from the JavaScript bundled in its binary.

Run from the repository root, naming the Claude Code binary:

    python docs/design/evidence/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT/hook_deny_source_probe.py <claude>

The bundle is minified, so the probe anchors on string literals, not on
identifiers, and prints the bytes around each anchor verbatim:

  A1 ``if(it.blockingError){``  - an exit-2 hook (a "blocking error") becomes
     ``{behavior:"deny", decisionReason:{type:"hook"}}``.
  A2 ``Hook result has permissionBehavior=`` - a JSON ``permissionDecision``
     other than allow/ask/defer (that is, ``deny``) becomes the same
     ``{behavior:<deny>, decisionReason:{type:"hook"}}``.
  A3 ``Hook denied tool use for`` - the resolver that receives that result
     takes its ``behavior==="deny"`` branch before the hook-``allow`` branch
     that reads the permission mode. Each return in the deny branch is either
     the hook's deny unchanged or the hook's deny passed to the A4 function.
  A4 that function (anchored on its ``evaluate:()=>Promise.resolve(e)`` opening): it
     passes the decision through the mod and policy checks. When they leave it
     a deny, it is returned (``if(k.behavior!=="ask")return{decision:k,...}``,
     or the branch that reports a deny to ``canUseTool`` and still returns
     ``{decision:k}``). ``canUseTool``, the mode-aware permission path, decides
     the call only when those checks turned the deny into an allow or an ask.

The probe prints the binary's size and SHA-256 so the excerpt is tied to one
build. It does not run Claude Code; ``bypass_hook_probe.py`` does.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys

ANCHORS = [
    ("A1", b"if(it.blockingError){", 0, 520),
    ("A2", b"Hook result has permissionBehavior=", -40, 1500),
    ("A3", b'if(e?.behavior==="deny"){t(`Hook denied tool use for', -260, 820),
    ("A4", b'evaluate:()=>Promise.resolve(e)},o.assistantMessage.message.id)', -80, 1500),
]


def main() -> None:
    path = sys.argv[1]
    data = open(path, "rb").read()
    version = subprocess.run([path, "--version"], capture_output=True, text=True, check=True)
    print(version.stdout.strip())
    print(f"bytes {len(data)} sha256 {hashlib.sha256(data).hexdigest()}")
    for label, anchor, before, after in ANCHORS:
        # The last occurrence: an earlier one can be the string table, not code.
        at = data.rfind(anchor)
        print(f"\n== {label} anchor {anchor.decode()!r} last offset {at} "
              f"occurrences {data.count(anchor)}")
        if at < 0:
            continue
        print(data[at + before:at + after].decode("utf-8", "replace"))


if __name__ == "__main__":
    main()
