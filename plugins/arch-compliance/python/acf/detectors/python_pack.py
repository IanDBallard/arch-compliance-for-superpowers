"""Python AST detector pack.

Detectors emit raw evidence only. Inline exemptions and severity are applied
later by ``acf.enforcement.apply_registry`` using the host mandate registry.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from acf.engine import is_in_scope, posix_path
from acf.finding import Finding, Severity

PYTHON_AST_DETECTOR_IDS = frozenset(
    {
        "fail_loud_bare_except",
        "no_shims_hasattr",
        "posix_paths_str_serialization",
    }
)

# Back-compat alias used by CLI / drift tests.
PYTHON_DETECTOR_IDS = PYTHON_AST_DETECTOR_IDS

_PATHY_RE = re.compile(r"path|dir|file", re.IGNORECASE)


def scan_python_file(
    text: str,
    path: str | Path,
    added_lines: frozenset[int] | None = None,
) -> list[Finding]:
    posix = posix_path(path)
    lines = text.splitlines()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    findings: list[Finding] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            finding = _check_bare_except(node, lines, posix, added_lines)
            if finding is not None:
                findings.append(finding)
        elif isinstance(node, ast.Call):
            finding = _check_hasattr(node, lines, posix, added_lines)
            if finding is not None:
                findings.append(finding)

    findings.extend(_find_str_path_in_serialization(tree, posix, added_lines))
    return findings


def _check_bare_except(
    node: ast.ExceptHandler,
    lines: list[str],
    path: str,
    added_lines: frozenset[int] | None,
) -> Finding | None:
    if not _is_bare_or_exception(node):
        return None
    line = node.lineno
    if not is_in_scope(line, added_lines):
        return None
    return Finding(
        mandate_id="fail-loud.bare-except",
        severity=Severity.BLOCK,
        path=path,
        line=line,
        message="Bare except or broad `except Exception` swallows errors",
        detector="fail_loud_bare_except",
        detection="ast",
    )


def _is_bare_or_exception(node: ast.ExceptHandler) -> bool:
    if node.type is None:
        return True
    if isinstance(node.type, ast.Name) and node.type.id == "Exception":
        return True
    return False


def _check_hasattr(
    node: ast.Call,
    lines: list[str],
    path: str,
    added_lines: frozenset[int] | None,
) -> Finding | None:
    if not isinstance(node.func, ast.Name) or node.func.id != "hasattr":
        return None
    line = node.lineno
    if not is_in_scope(line, added_lines):
        return None
    return Finding(
        mandate_id="no-shims.hasattr",
        severity=Severity.WARN,
        path=path,
        line=line,
        message="`hasattr` probes are no-shim violations",
        detector="no_shims_hasattr",
        detection="ast",
    )


def _is_str_call_of_pathy(node: ast.AST) -> bool:
    if not (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "str"
    ):
        return False
    if not node.args:
        return False
    arg = node.args[0]
    if isinstance(arg, ast.Name):
        return bool(_PATHY_RE.search(arg.id))
    if isinstance(arg, ast.Attribute):
        return bool(_PATHY_RE.search(arg.attr))
    return False


def _find_str_path_in_serialization(
    tree: ast.AST,
    path: str,
    added_lines: frozenset[int] | None,
) -> list[Finding]:
    findings: list[Finding] = []
    seen: set[int] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in {"dump", "safe_dump", "dumps"}
        ):
            for sub in ast.walk(node):
                if _is_str_call_of_pathy(sub) and id(sub) not in seen:
                    seen.add(id(sub))
                    line = getattr(sub, "lineno", 0)
                    if is_in_scope(line, added_lines):
                        findings.append(
                            Finding(
                                mandate_id="posix-paths.str-serialization",
                                severity=Severity.BLOCK,
                                path=path,
                                line=line,
                                message=(
                                    "Do not str()-coerce path-like values into "
                                    "YAML/JSON serialization; use Path.as_posix()"
                                ),
                                detector="posix_paths_str_serialization",
                                detection="ast",
                            )
                        )
        if isinstance(node, ast.Dict):
            for value in node.values:
                if (
                    value is not None
                    and _is_str_call_of_pathy(value)
                    and id(value) not in seen
                ):
                    # Only when the dict is an argument to dump/dumps — covered above
                    # via walk of Call. Flag bare dicts assigned for later dump too?
                    # Keep HM parity: flag dict values with str(pathy) as evidence of
                    # serialization payloads.
                    seen.add(id(value))
                    line = getattr(value, "lineno", 0)
                    if is_in_scope(line, added_lines):
                        findings.append(
                            Finding(
                                mandate_id="posix-paths.str-serialization",
                                severity=Severity.BLOCK,
                                path=path,
                                line=line,
                                message=(
                                    "Do not str()-coerce path-like values into "
                                    "serialized dict payloads; use Path.as_posix()"
                                ),
                                detector="posix_paths_str_serialization",
                                detection="ast",
                            )
                        )
    return findings
