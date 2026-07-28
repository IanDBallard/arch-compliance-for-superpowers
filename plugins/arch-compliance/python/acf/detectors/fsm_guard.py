"""Config-driven FSM transition guard (generic field + validator names)."""

from __future__ import annotations

import ast
from collections.abc import Iterable
from pathlib import Path

from acf.engine import is_in_scope, posix_path
from acf.exceptions import DetectorPackError
from acf.finding import Finding, Severity

FSM_GUARD_DETECTOR_ID = "fsm_transition_guard"


def scan_fsm_writes(
    text: str,
    path: str | Path,
    added_lines: frozenset[int] | None,
    *,
    state_field: str,
    validator_name: str,
) -> list[Finding]:
    """Flag assignments to ``state_field`` in scopes that never call ``validator_name``.

    Matches attribute writes (``obj.<field> = …``) and subscript writes
    (``obj['<field>'] = …``). Nested functions are separate scopes.
    """
    field = (state_field or "").strip()
    validator = (validator_name or "").strip()
    if not field or not validator:
        raise DetectorPackError(
            "fsm_transition_guard requires params.state_field and params.validator_name"
        )

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    posix = posix_path(path)
    lines = text.splitlines()
    findings: list[Finding] = []
    for scope in _iter_function_scopes(tree):
        if _scope_calls_validator(scope, validator):
            continue
        for node in _walk_own_body(scope):
            if not isinstance(node, ast.Assign):
                continue
            for target in node.targets:
                if not _is_state_write(target, field):
                    continue
                line = getattr(node, "lineno", 0)
                if not is_in_scope(line, added_lines):
                    continue
                snippet = lines[line - 1].strip() if 0 < line <= len(lines) else ""
                findings.append(
                    Finding(
                        mandate_id="fsm.transition-guard",
                        severity=Severity.BLOCK,
                        path=posix,
                        line=line,
                        message=(
                            f"Write to {field!r} without {validator!r} in the "
                            f"same function scope ({snippet[:120]})"
                        ),
                        detector=FSM_GUARD_DETECTOR_ID,
                        detection="ast",
                    )
                )
    return findings


def _is_state_write(target: ast.expr, field: str) -> bool:
    if isinstance(target, ast.Attribute) and target.attr == field:
        return True
    if (
        isinstance(target, ast.Subscript)
        and isinstance(target.slice, ast.Constant)
        and target.slice.value == field
    ):
        return True
    return False


def _walk_own_body(scope: ast.AST) -> Iterable[ast.AST]:
    stack = list(ast.iter_child_nodes(scope))
    while stack:
        current = stack.pop()
        yield current
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        stack.extend(ast.iter_child_nodes(current))


def _scope_calls_validator(scope: ast.AST, validator_name: str) -> bool:
    for node in _walk_own_body(scope):
        if isinstance(node, ast.Attribute) and node.attr == validator_name:
            return True
        if isinstance(node, ast.Name) and node.id == validator_name:
            return True
    return False


def _iter_function_scopes(tree: ast.Module) -> Iterable[ast.AST]:
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            yield node
