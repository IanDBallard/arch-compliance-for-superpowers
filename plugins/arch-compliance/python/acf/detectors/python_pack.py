"""Python AST detector pack.

Detectors emit raw evidence only. Inline exemptions and severity are applied
later by ``acf.enforcement.apply_registry`` using the host mandate registry.
"""

from __future__ import annotations

import ast
from pathlib import Path

from acf.engine import is_in_scope, posix_path
from acf.finding import Finding, Severity

PYTHON_DETECTOR_IDS = frozenset({"fail_loud_bare_except", "no_shims_hasattr"})


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
