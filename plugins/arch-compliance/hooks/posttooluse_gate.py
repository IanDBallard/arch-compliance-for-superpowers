#!/usr/bin/env python3
"""PostToolUse gate: run Tier-1 detectors on edited file paths.

Runnable as:
  python hooks/posttooluse_gate.py path/a.py path/b.tsx
  python hooks/posttooluse_gate.py --repo /path/to/host path/a.py
  echo '{"tool_input":{"file_path":"..."}}' | python hooks/posttooluse_gate.py --format hook

Behavior:
  - If ``.acf/enabled`` is absent: exit 0 (no-op), optional stderr warning.
  - If enabled and ``config/architecture/mandates.yml`` is missing: non-zero exit.
  - Otherwise scan ``.py`` / ``.ts`` / ``.tsx`` paths and print findings.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_HOOKS_DIR = Path(__file__).resolve().parent
_PLUGIN_ROOT = _HOOKS_DIR.parent
_PYTHON_ROOT = _PLUGIN_ROOT / "python"
if str(_PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(_PYTHON_ROOT))

from acf.detectors.python_pack import scan_python_file  # noqa: E402
from acf.detectors.typescript_bridge import scan_typescript_file  # noqa: E402
from acf.exceptions import DetectorPackError, RegistryLoadError  # noqa: E402
from acf.finding import Finding, Severity  # noqa: E402
from acf.registry import load_mandates  # noqa: E402

_MANDATES_REL = Path("config") / "architecture" / "mandates.yml"
_ENABLED_REL = Path(".acf") / "enabled"
_CODE_SUFFIXES = {".py", ".ts", ".tsx"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="posttooluse_gate")
    parser.add_argument(
        "--repo",
        type=Path,
        default=None,
        help="Host repository root (default: cwd, or stdin JSON cwd)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "hook", "json"),
        default=None,
        help="Output format (default: hook when stdin has hook_event_name, else text)",
    )
    parser.add_argument(
        "--quiet-disabled",
        action="store_true",
        help="Suppress stderr warning when .acf/enabled is absent",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Edited file paths (absolute or repo-relative)",
    )
    args = parser.parse_args(argv)

    stdin_payload = _maybe_read_stdin_json()
    repo = _resolve_repo(args.repo, stdin_payload)
    out_format = args.format or (
        "hook"
        if isinstance(stdin_payload, dict) and stdin_payload.get("hook_event_name")
        else "text"
    )

    enabled = repo / _ENABLED_REL
    if not enabled.is_file():
        if not args.quiet_disabled:
            print(
                "acf: hooks inactive (.acf/enabled missing); run /acf-setup",
                file=sys.stderr,
            )
        if out_format == "hook":
            print(json.dumps({"continue": True}))
        return 0

    mandates_path = repo / _MANDATES_REL
    if not mandates_path.is_file():
        print(
            f"acf: .acf/enabled present but mandates missing: {mandates_path.as_posix()}",
            file=sys.stderr,
        )
        return 1

    try:
        load_mandates(mandates_path)
    except RegistryLoadError as exc:
        print(f"acf: {exc}", file=sys.stderr)
        return 1

    paths = _collect_paths(args.paths, stdin_payload, repo)
    try:
        findings = _scan_paths(repo, paths)
    except DetectorPackError as exc:
        print(f"acf: {exc}", file=sys.stderr)
        return 1

    if out_format == "json":
        print(json.dumps([f.model_dump(mode="json") for f in findings], indent=2))
    elif out_format == "hook":
        event = "PostToolUse"
        if isinstance(stdin_payload, dict):
            event = str(stdin_payload.get("hook_event_name") or event)
        context = _format_findings(findings)
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": event,
                        "additionalContext": context,
                    }
                }
            )
        )
    else:
        print(_format_findings(findings))

    if out_format != "hook" and any(f.severity == Severity.BLOCK for f in findings):
        return 1
    return 0


def _resolve_repo(explicit: Path | None, stdin_payload: dict | None) -> Path:
    if explicit is not None:
        return explicit.resolve()
    if isinstance(stdin_payload, dict) and stdin_payload.get("cwd"):
        return Path(str(stdin_payload["cwd"])).resolve()
    return Path.cwd().resolve()


def _maybe_read_stdin_json() -> dict | None:
    if sys.stdin.isatty():
        return None
    raw = sys.stdin.read()
    if not raw.strip():
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _collect_paths(
    argv_paths: list[str],
    stdin_payload: dict | None,
    repo: Path,
) -> list[Path]:
    collected: list[str] = list(argv_paths)
    if isinstance(stdin_payload, dict):
        for key in ("paths", "files"):
            raw = stdin_payload.get(key)
            if isinstance(raw, list):
                collected.extend(str(p) for p in raw)
        tool_input = stdin_payload.get("tool_input")
        if isinstance(tool_input, dict):
            fp = tool_input.get("file_path") or tool_input.get("path")
            if fp:
                collected.append(str(fp))
            # MultiEdit-style edits array
            edits = tool_input.get("edits")
            if isinstance(edits, list):
                for edit in edits:
                    if isinstance(edit, dict) and edit.get("file_path"):
                        collected.append(str(edit["file_path"]))

    resolved: list[Path] = []
    seen: set[str] = set()
    for raw in collected:
        p = Path(raw)
        abs_path = p.resolve() if p.is_absolute() else (repo / p).resolve()
        key = abs_path.as_posix()
        if key in seen:
            continue
        seen.add(key)
        resolved.append(abs_path)
    return resolved


def _scan_paths(repo: Path, paths: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for abs_path in paths:
        if not abs_path.is_file():
            continue
        suffix = abs_path.suffix.lower()
        if suffix not in _CODE_SUFFIXES:
            continue
        try:
            rel = abs_path.relative_to(repo).as_posix()
        except ValueError:
            rel = abs_path.as_posix()

        if suffix == ".py":
            text = abs_path.read_text(encoding="utf-8")
            findings.extend(scan_python_file(text, rel, added_lines=None))
        else:
            findings.extend(scan_typescript_file(abs_path, added_lines=None))
    return findings


def _format_findings(findings: list[Finding]) -> str:
    if not findings:
        return "ACF PostToolUse gate: no findings."
    lines = ["ACF PostToolUse gate findings:"]
    for f in findings:
        lines.append(
            f"- {f.severity.value} {f.mandate_id} {f.path}:{f.line} {f.message}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
