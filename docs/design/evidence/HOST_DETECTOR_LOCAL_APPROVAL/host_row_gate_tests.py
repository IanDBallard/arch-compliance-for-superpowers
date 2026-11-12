"""Census: test functions that run a gate (the PostToolUse hook or acf-check-diff)
with host detector rows in the registry.

A test is listed when its body, together with the module-level helpers it calls and
the module-level fixtures it takes as parameters (one level deep), both runs a gate
and builds a host row. A host row is recognised by shape (a detector string
`<path>.py:` followed by an identifier or an f-string field) and by the current
helper names. Run from the repository root:

    python docs/design/evidence/HOST_DETECTOR_LOCAL_APPROVAL/host_row_gate_tests.py
"""
import ast
import re
import subprocess
from pathlib import Path

GATE_MARKERS = re.compile(r"\bGATE\b|posttooluse_gate|cli_check_diff|acf-check-diff|\bmain\(")
HOST_ROW = re.compile(r"\.py:[A-Za-z_{]|_host_row\(|_seed_host_rows\(|_host_rows\(|_host_repo\(")


def module_functions(tree, src):
    out = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("test_"):
            out[node.name] = ast.get_source_segment(src, node) or ""
    return out


def main():
    files = subprocess.run(
        ["git", "ls-files", "plugins/arch-compliance/tests/*.py", "tests/*.py"],
        capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout.split()
    for rel in files:
        src = Path(rel).read_text(encoding="utf-8")
        tree = ast.parse(src)
        helpers = module_functions(tree, src)
        for node in ast.walk(tree):
            if not (isinstance(node, ast.FunctionDef) and node.name.startswith("test_")):
                continue
            body = ast.get_source_segment(src, node) or ""
            called = {n.func.id for n in ast.walk(node) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
            fixtures = {a.arg for a in node.args.args}
            expanded = body + "".join(helpers.get(c, "") for c in called | fixtures)
            if GATE_MARKERS.search(expanded) and HOST_ROW.search(expanded):
                print(f"{rel}:{node.lineno} {node.name}")


if __name__ == "__main__":
    main()
