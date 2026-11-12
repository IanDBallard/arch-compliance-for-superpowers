#!/usr/bin/env python3
"""PostToolUse gate: run Tier-1 detectors on edited file paths.

Runnable as:
  python hooks/posttooluse_gate.py path/a.py path/b.tsx
  python hooks/posttooluse_gate.py --repo /path/to/host path/a.py
  echo '{"tool_input":{"file_path":"..."}}' | python hooks/posttooluse_gate.py --format hook

Behavior:
  - If ``.acf/enabled`` is absent: exit 0 (no-op), optional stderr warning.
  - If enabled and ``config/architecture/mandates.yml`` is missing: non-zero exit.
  - Otherwise run the active rows declaring ``hook`` or ``posttooluse`` on the
    edited in-repo paths and print findings; host guards receive every edited
    in-repo path.
  - Host detector rows run repository code, so they run only under a local
    approval (``acf-allow``) that still matches the rows and detector files.
    Without one the hook skips them, runs the built-in rows, and prints one
    notice naming the skipped rows (``additionalContext`` plus ``systemMessage``
    in hook format; stderr otherwise). It never approves anything itself.

Exit codes: 0 clean; 1 findings at BLOCK (text/json formats) or a gate-input
failure in text/json formats; 2 in hook format for a BLOCK finding, any
gate-input failure (missing mandates or dependencies, malformed registry or
approval store, unreadable detector file, failing detector) and any other
internal error, so the agent sees it on stderr.
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from collections.abc import Mapping
from pathlib import Path

_HOOKS_DIR = Path(__file__).resolve().parent
_PLUGIN_ROOT = _HOOKS_DIR.parent
_PYTHON_ROOT = _PLUGIN_ROOT / "python"
if str(_PYTHON_ROOT) not in sys.path:
    sys.path.insert(0, str(_PYTHON_ROOT))

from acf.repo import ENABLED_REL, MANDATES_REL, RepoTree, resolve_repo

# NOTE: third-party acf imports (pydantic, yaml) are deferred into main() so
# this hook stays a true no-op (exit 0, no third-party imports) in repos
# without .acf/enabled — the hook fires on every Write/Edit in every repo
# once the plugin is installed. acf.repo is stdlib-only and is safe here.

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

    try:
        return _gate(args, stdin_payload, repo, out_format)
    except Exception as exc:  # fail-loud.bare-except-ok: hook mode reports any failure on the agent's channel (exit 2); other formats re-raise
        if out_format != "hook":
            raise
        print(f"acf: internal error: {type(exc).__name__}: {exc}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return 2


def _gate(
    args: argparse.Namespace, stdin_payload: dict | None, repo: Path, out_format: str
) -> int:
    # Hook mode exits 2 so the agent sees the failure; other formats exit 1.
    failure = 2 if out_format == "hook" else 1

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
        return failure

    try:
        from acf.detectors import KNOWN_DETECTORS
        from acf.enforcement import apply_registry, make_line_lookup
        from acf.exceptions import AcfInputError, DetectorPackError, UnknownDetectorError
        from acf.finding import Severity
        from acf.registry import HOOK_CALL_SITES, load_mandates

        from acf.approval import ApprovalState, approval_rows, check_approval, reason, store_path
    except ImportError as exc:
        print(
            "acf: ACF is enabled here but its Python dependencies are missing "
            f"({exc}). Install the acf package into this interpreter: "
            'pip install -e ".[dev]" from the arch-compliance-for-superpowers '
            "checkout (see plugin README).",
            file=sys.stderr,
        )
        return failure

    try:
        registry = load_mandates(mandates_path, known_detectors=KNOWN_DETECTORS, repo_root=repo)
        approval = check_approval(repo, registry, HOOK_CALL_SITES)
    except (AcfInputError, UnknownDetectorError) as exc:
        print(f"acf: {exc}", file=sys.stderr)
        return failure

    run_host = approval.state in {ApprovalState.NOT_NEEDED, ApprovalState.APPROVED}
    notice = ""
    if not run_host:
        ids = ", ".join(m.id for m in approval_rows(registry))
        notice = (
            f"acf: host detectors not run: {reason(approval.state, store_path())}; "
            f"rows skipped: {ids}. Ask the user to review the detector files and run "
            "acf-allow in this repository; do not run it yourself."
        )
    # NOT_NEEDED selects no host row at these call sites, so the empty map is never indexed.
    digests = approval.digests

    paths = _collect_paths(args.paths, stdin_payload, repo)
    try:
        raw_findings, file_lines = _scan_paths(
            repo, paths, registry, run_host=run_host, digests=digests
        )
    except (AcfInputError, DetectorPackError, UnknownDetectorError) as exc:
        print(f"acf: {exc}", file=sys.stderr)
        return failure

    findings = apply_registry(
        raw_findings, registry, make_line_lookup(file_lines), call_sites=HOOK_CALL_SITES
    )
    has_block = any(f.severity == Severity.BLOCK for f in findings)

    if notice and (out_format != "hook" or has_block):
        print(notice, file=sys.stderr)

    if out_format == "json":
        print(json.dumps([f.model_dump(mode="json") for f in findings], indent=2))
    elif out_format == "hook":
        if has_block:
            # Exit 2 feeds stderr back to Claude as blocking feedback.
            print(_format_findings(findings), file=sys.stderr)
            return 2
        event = "PostToolUse"
        if isinstance(stdin_payload, dict):
            event = str(stdin_payload.get("hook_event_name") or event)
        context = _format_findings(findings)
        output: dict = {}
        if notice:
            context = f"{notice}\n\n{context}"
            output["systemMessage"] = notice
        output["hookSpecificOutput"] = {
            "hookEventName": event,
            "additionalContext": context,
        }
        print(json.dumps(output))
    else:
        print(_format_findings(findings))

    if out_format != "hook" and has_block:
        return 1
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

    tree = RepoTree(repo)
    resolved: list[Path] = []
    seen: set[str] = set()
    for raw in collected:
        abs_path = tree.file(raw)
        if abs_path is None:
            continue
        key = abs_path.as_posix()
        if key in seen:
            continue
        seen.add(key)
        resolved.append(abs_path)
    return resolved


def _scan_paths(
    repo: Path,
    paths: list[Path],
    registry,
    *,
    run_host: bool,
    digests: Mapping[str, str] | None,
) -> tuple[list[Finding], dict[str, list[str]]]:
    from acf.detectors.build_artifacts import (
        BUILD_ARTIFACT_DETECTOR_ID,
        build_artifact_args,
        scan_build_artifact_paths,
    )
    from acf.detectors.facade_sinks import (
        FACADE_SINK_DETECTOR_ID,
        facade_sink_args,
        scan_facade_sinks,
    )
    from acf.detectors.fsm_guard import FSM_GUARD_DETECTOR_ID, fsm_guard_args, scan_fsm_writes
    from acf.detectors.host import scan_host_ast_file, scan_host_guards
    from acf.detectors.python_pack import scan_python_file
    from acf.detectors.typescript_bridge import scan_typescript_file
    from acf.registry import HOOK_CALL_SITES

    tree = RepoTree(repo)
    findings: list[Finding] = []
    file_lines: dict[str, list[str]] = {}
    rel_paths: list[str] = []

    facade_specs = registry.active(HOOK_CALL_SITES, detector=FACADE_SINK_DETECTOR_ID)
    fsm_specs = registry.active(HOOK_CALL_SITES, detector=FSM_GUARD_DETECTOR_ID)

    for abs_path in paths:
        suffix = abs_path.suffix.lower()
        rel = tree.key(abs_path)
        rel_paths.append(rel)

        if suffix not in _CODE_SUFFIXES:
            continue

        text = abs_path.read_text(encoding="utf-8")
        file_lines[rel] = text.splitlines()
        if suffix == ".py":
            findings.extend(scan_python_file(text, rel, added_lines=None))
            for mandate in facade_specs:
                params = mandate.params or {}
                findings.extend(
                    scan_facade_sinks(
                        text,
                        rel,
                        None,
                        **facade_sink_args(params),
                    )
                )
            for mandate in fsm_specs:
                params = mandate.params or {}
                findings.extend(
                    scan_fsm_writes(
                        text,
                        rel,
                        None,
                        **fsm_guard_args(params),
                    )
                )
            if run_host:
                findings.extend(
                    scan_host_ast_file(
                        repo,
                        text,
                        rel,
                        None,
                        registry,
                        language="python",
                        call_sites=HOOK_CALL_SITES,
                        digests=digests,
                    )
                )
        else:
            findings.extend(
                f.model_copy(update={"path": rel})
                for f in scan_typescript_file(abs_path, added_lines=None)
            )
            if run_host:
                findings.extend(
                    scan_host_ast_file(
                        repo,
                        text,
                        rel,
                        None,
                        registry,
                        language="typescript",
                        call_sites=HOOK_CALL_SITES,
                        digests=digests,
                    )
                )

    for mandate in registry.active(HOOK_CALL_SITES, detector=BUILD_ARTIFACT_DETECTOR_ID):
        params = mandate.params or {}
        findings.extend(scan_build_artifact_paths(rel_paths, **build_artifact_args(params)))
    if run_host:
        findings.extend(
            scan_host_guards(
                repo,
                rel_paths,
                registry,
                file_lines,
                call_sites=HOOK_CALL_SITES,
                digests=digests,
            )
        )
    return findings, file_lines


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
