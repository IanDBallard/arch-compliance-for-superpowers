"""Census of repository-path operations in plugin runtime code.

Flags, outside acf/repo.py:
  - calls to .resolve(), .relative_to(), .is_relative_to(), os.path.realpath/abspath/relpath/commonpath
  - a `/` join whose left operand is a Name or attribute named like a repo root and whose
    right operand is not a constant or an ALL_CAPS name
Prints file:line and the source line, so the result is the migration list.
"""
import ast
import sys
from pathlib import Path

ROOT_NAMES = {"repo", "repo_root", "root", "ROOT", "base", "host_root"}
CALLS = {"resolve", "relative_to", "is_relative_to", "joinpath"}
OSPATH = {"realpath", "abspath", "relpath", "commonpath"}


def name_of(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Call):
        return name_of(node.func)
    return None


def is_constantish(node):
    if isinstance(node, ast.Constant):
        return True
    n = name_of(node)
    return bool(n) and n.isupper()


def from_file_dunder(node):
    for sub in ast.walk(node):
        if isinstance(sub, ast.Name) and sub.id == "__file__":
            return True
    return False


repo = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
targets = sorted((repo / "plugins/arch-compliance/python").rglob("*.py")) + sorted((repo / "plugins/arch-compliance/hooks").rglob("*.py"))
for f in targets:
    rel = f.relative_to(repo).as_posix()
    if rel.endswith("acf/repo.py") or "__pycache__" in rel:
        continue
    src = f.read_text(encoding="utf-8")
    lines = src.splitlines()
    for node in ast.walk(ast.parse(src)):
        kind = None
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in CALLS and not from_file_dunder(node.func.value):
                kind = node.func.attr
            if node.func.attr in OSPATH and name_of(node.func.value) == "path":
                kind = "os.path." + node.func.attr
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            if name_of(node.left) in ROOT_NAMES and not is_constantish(node.right):
                kind = "join"
        if kind:
            print(f"{rel}:{node.lineno}\t{kind}\t{lines[node.lineno - 1].strip()}")
