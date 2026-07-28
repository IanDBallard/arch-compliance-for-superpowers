"""Config-driven façade sink scanner (generic; host supplies target regex)."""

from __future__ import annotations

import ast
import fnmatch
import re
from pathlib import Path

from acf.engine import is_in_scope, posix_path
from acf.exceptions import DetectorPackError
from acf.finding import Finding, Severity

FACADE_SINK_DETECTOR_ID = "forbid_facade_sink"
_WRITE_MODE_RE = re.compile(r"[wax]")


def scan_facade_sinks(
    text: str,
    path: str | Path,
    added_lines: frozenset[int] | None,
    *,
    target_literal_re: str,
    allowlist_globs: list[str] | None = None,
    atomic_is_sink: bool = True,
) -> list[Finding]:
    """Flag write sinks targeting paths matching ``target_literal_re``.

    Allowlisted source files (fnmatch against the file's POSIX path) are skipped
    entirely. Detectors emit raw findings; registry exemptions apply later.
    """
    pattern = (target_literal_re or "").strip()
    if not pattern:
        raise DetectorPackError(
            "forbid_facade_sink requires params.target_literal_re "
            "(regex matching the protected filename/path fragment)"
        )
    try:
        target_re = re.compile(pattern)
    except re.error as exc:
        raise DetectorPackError(
            f"forbid_facade_sink: invalid target_literal_re {pattern!r}: {exc}"
        ) from exc

    posix = posix_path(path)
    for glob in allowlist_globs or []:
        if fnmatch.fnmatch(posix, glob):
            return []

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    findings: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        sink = _classify_sink(node, atomic_is_sink=atomic_is_sink)
        if sink is None:
            continue
        if not _call_mentions_target(node, target_re):
            continue
        line = getattr(node, "lineno", 0)
        if not is_in_scope(line, added_lines):
            continue
        findings.append(
            Finding(
                mandate_id="facade.forbid-sink",
                severity=Severity.BLOCK,
                path=posix,
                line=line,
                message=f"Direct {sink} write to façade target matching /{pattern}/",
                detector=FACADE_SINK_DETECTOR_ID,
                detection="ast",
            )
        )
    return findings


def _classify_sink(call: ast.Call, *, atomic_is_sink: bool) -> str | None:
    if isinstance(call.func, ast.Name) and call.func.id == "open":
        return "open_write" if _mode_is_write(call, 1) else None
    if isinstance(call.func, ast.Attribute) and call.func.attr == "open":
        return "path_open_write" if _mode_is_write(call, 0) else None
    if isinstance(call.func, ast.Attribute) and call.func.attr == "write_text":
        return "write_text"
    if atomic_is_sink and isinstance(call.func, ast.Name) and call.func.id == "atomic_write_yaml":
        return "atomic_write_yaml"
    if atomic_is_sink and isinstance(call.func, ast.Attribute) and call.func.attr == "atomic_write_yaml":
        return "atomic_write_yaml"
    return None


def _mode_is_write(call: ast.Call, mode_arg_index: int) -> bool:
    mode: str | None = None
    if len(call.args) > mode_arg_index:
        arg = call.args[mode_arg_index]
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            mode = arg.value
    for kw in call.keywords:
        if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
            if isinstance(kw.value.value, str):
                mode = kw.value.value
    if mode is None:
        return False
    return bool(_WRITE_MODE_RE.search(mode))


def _call_mentions_target(call: ast.Call, target_re: re.Pattern[str]) -> bool:
    for node in ast.walk(call):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if target_re.search(node.value):
                return True
    return False
