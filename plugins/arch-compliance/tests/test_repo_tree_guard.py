"""Guard: RepoTree (acf/repo.py) is the one owner of repository path resolution.

The rules are copied from docs/design/evidence/HOST_DETECTOR_EXTENSION_POINT/path_census.py
(Decision 9), not imported, so the test does not depend on docs/ being importable.
"""
import ast
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

ROOT_NAMES = {"repo", "repo_root", "root", "ROOT", "base", "host_root"}
CALLS = {"resolve", "relative_to", "is_relative_to", "joinpath"}
OSPATH = {"realpath", "abspath", "relpath", "commonpath"}

ALLOWED = {("cli_check_diff.py", "main"), ("cli_check_llm.py", "main"),
           ("typescript_bridge.py", "scan_typescript_file")}


def _name_of(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Call):
        return _name_of(node.func)
    return None


def _is_constantish(node):
    if isinstance(node, ast.Constant):
        return True
    n = _name_of(node)
    return bool(n) and n.isupper()


def _from_file_dunder(node):
    return any(isinstance(s, ast.Name) and s.id == "__file__" for s in ast.walk(node))


def _scan_source(src):
    """Return [(lineno, kind, enclosing_function)] for every flagged node in src."""
    tree = ast.parse(src)
    parents = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent

    def enclosing(node):
        while node in parents:
            node = parents[node]
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return node.name
        return "<module>"

    hits = []
    for node in ast.walk(tree):
        kind = None
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in CALLS and not _from_file_dunder(node.func.value):
                kind = node.func.attr
            if node.func.attr in OSPATH and _name_of(node.func.value) == "path":
                kind = "os.path." + node.func.attr
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            if _name_of(node.left) in ROOT_NAMES and not _is_constantish(node.right):
                kind = "join"
        if kind:
            hits.append((node.lineno, kind, enclosing(node)))
    return hits


def _scan_tree():
    out = subprocess.run(
        ["git", "ls-files", "plugins/arch-compliance/python", "plugins/arch-compliance/hooks"],
        cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout.splitlines()
    results = []
    for rel in out:
        if not rel.endswith(".py") or rel.endswith("acf/repo.py"):
            continue
        path = REPO_ROOT / rel
        for _lineno, _kind, func in _scan_source(path.read_text(encoding="utf-8")):
            results.append((path, func))
    return results


def test_only_allowlisted_functions_resolve_repo_paths():
    hits = {(path.name, enclosing_function) for path, enclosing_function in _scan_tree()}
    assert hits == ALLOWED


def test_rules_flag_fixture():
    src = ("def f(repo, name, path, root, x, p):\n    repo / name\n    path.resolve()\n"
           "    root.joinpath(x)\n    os.path.realpath(p)\n")
    assert len(_scan_source(src)) == 4


def test_rules_spare_constants_and_file_dunder():
    assert _scan_source("Path(__file__).resolve()\nrepo / MANDATES_REL\n") == []
