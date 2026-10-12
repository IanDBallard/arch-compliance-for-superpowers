#!/usr/bin/env python3
"""SubagentStart hook: inject host ACF constraints into subagent context.

Runnable as:
  python hooks/inject_constraints.py
  python hooks/inject_constraints.py --repo /path/to/host
  python hooks/inject_constraints.py --format hook   # Claude Code JSON

Behavior:
  - If ``.acf/enabled`` is absent: exit 0 (no-op), optional stderr warning.
  - If enabled and ``config/architecture/mandates.yml`` is missing: non-zero exit.
  - If enabled and ``config/architecture/ARCHITECTURE.md`` is missing: non-zero
    exit. A placeholder excerpt would tell a subagent it has the host's rules
    when it does not.
  - Otherwise print a constraint block (text) or Claude Code ``additionalContext`` JSON.
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

from acf.repo import ARCH_REL, ENABLED_REL, MANDATES_REL, resolve_repo

# NOTE: third-party acf imports (pydantic, yaml) are deferred into main() so
# this hook stays a true no-op (exit 0, no third-party imports) in repos
# without .acf/enabled — the hook fires in every repo once the plugin is
# installed. acf.repo is stdlib-only and is safe to import here.

_TEMPLATE = _HOOKS_DIR / "constraints_template.md"
_ARCH_EXCERPT_MAX = 4000


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="inject_constraints")
    parser.add_argument(
        "--repo",
        type=Path,
        default=None,
        help="Host repository root (default: cwd, or stdin JSON cwd)",
    )
    parser.add_argument(
        "--format",
        choices=("text", "hook"),
        default=None,
        help="Output format (default: hook when stdin has hook_event_name, else text)",
    )
    parser.add_argument(
        "--quiet-disabled",
        action="store_true",
        help="Suppress stderr warning when .acf/enabled is absent",
    )
    args = parser.parse_args(argv)

    stdin_payload = _maybe_read_stdin_json()
    repo = _resolve_repo(args.repo, stdin_payload)
    out_format = args.format or (
        "hook"
        if isinstance(stdin_payload, dict) and stdin_payload.get("hook_event_name")
        else "text"
    )

    enabled = repo / ENABLED_REL
    if not enabled.is_file():
        if not args.quiet_disabled:
            print(
                "acf: hooks inactive (.acf/enabled missing); run /acf-setup",
                file=sys.stderr,
            )
        if out_format == "hook":
            print(json.dumps({"continue": True}))
        return 0

    mandates_path = repo / MANDATES_REL
    if not mandates_path.is_file():
        print(
            f"acf: .acf/enabled present but mandates missing: {mandates_path.as_posix()}",
            file=sys.stderr,
        )
        return 1

    try:
        from acf.exceptions import AcfInputError
        from acf.registry import load_mandates
    except ImportError as exc:
        print(
            "acf: ACF is enabled here but its Python dependencies are missing "
            f"({exc}). Install the acf package into this interpreter: "
            'pip install -e ".[dev]" from the arch-compliance-for-superpowers '
            "checkout (see plugin README).",
            file=sys.stderr,
        )
        return 1

    try:
        registry = load_mandates(mandates_path)
    except AcfInputError as exc:
        print(f"acf: {exc}", file=sys.stderr)
        return 1

    try:
        block = _render_constraints(repo, registry.mandates)
    except (FileNotFoundError, OSError) as exc:
        print(f"acf: {exc}", file=sys.stderr)
        return 1
    if out_format == "hook":
        event = "SubagentStart"
        if isinstance(stdin_payload, dict):
            event = str(stdin_payload.get("hook_event_name") or event)
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": event,
                        "additionalContext": block,
                    }
                }
            )
        )
    else:
        print(block)
    return 0


def _resolve_repo(explicit: Path | None, stdin_payload: dict | None) -> Path:
    stdin_cwd = None
    if isinstance(stdin_payload, dict):
        stdin_cwd = stdin_payload.get("cwd")
    return resolve_repo(explicit, stdin_cwd)


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


def _render_constraints(repo: Path, mandates: list) -> str:
    template = _TEMPLATE.read_text(encoding="utf-8")
    mandate_lines = []
    for m in mandates:
        mandate_lines.append(
            f"- `{m.id}` [{m.severity}/{m.status}] {m.title} "
            f"(detection={m.detection}, detector={m.detector})"
        )
    mandates_block = "\n".join(mandate_lines) if mandate_lines else "_No mandates listed._"

    arch_path = repo / ARCH_REL
    if not arch_path.is_file():
        raise FileNotFoundError(
            f"doctrine document not found: {arch_path.as_posix()}"
        )
    excerpt = arch_path.read_text(encoding="utf-8").strip()
    if len(excerpt) > _ARCH_EXCERPT_MAX:
        excerpt = excerpt[:_ARCH_EXCERPT_MAX].rstrip() + "\n\n…(truncated)…"

    return (
        template.replace("{{MANDATES}}", mandates_block).replace(
            "{{ARCHITECTURE_EXCERPT}}", excerpt
        )
    )


if __name__ == "__main__":
    sys.exit(main())
