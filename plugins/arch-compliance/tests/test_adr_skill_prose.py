"""The moved gate prose: its Python resolves here, and it names no origin host."""
from __future__ import annotations

import ast
import importlib
import re
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[1] / "skills"
GATE = SKILLS / "adversarial-design-review"
RESPOND = SKILLS / "responding-to-adversarial-review"
FILES = [
    GATE / "SKILL.md", GATE / "claims" / "extraction.md",
    GATE / "reviewers" / "compliance.md", GATE / "reviewers" / "hardening.md",
    GATE / "reviewers" / "refuter.md", GATE / "reviewers" / "sweeper.md",
    RESPOND / "SKILL.md",
]
FORBIDDEN = ["GEMINI", "CLAUDE.md", "SKILL_PROVENANCE", "scripts.core",
             "docs/design", "docs/reviews", "docs/architecture", ".cursor"]


def _python_bodies() -> list[tuple[str, str]]:
    bodies = []
    for skill in (GATE / "SKILL.md", RESPOND / "SKILL.md"):
        text = skill.read_text(encoding="utf-8")
        bodies += [(f"{skill.parent.name}:python", b) for b in re.findall(r"```python\n(.*?)```", text, re.S)]
        bodies += [(f"{skill.parent.name}:python -c", b) for b in re.findall(r'python -c "\n(.*?)"\n', text, re.S)]
    return bodies


def test_the_seven_files_moved():
    missing = [p.as_posix() for p in FILES if not p.is_file()]
    assert missing == []


def test_the_prose_names_no_origin_host():
    hits = [f"{p.relative_to(SKILLS).as_posix()}:{n}: {lit}"
            for p in FILES
            for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
            for lit in FORBIDDEN if lit in line]
    assert hits == [], "\n".join(hits)


def test_every_python_body_parses_and_its_acf_imports_exist():
    bodies = _python_bodies()
    assert len(bodies) >= 12  # ten fenced blocks and two python -c bodies at move time
    for where, body in bodies:
        tree = ast.parse(body)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and (node.module or "").startswith("acf"):
                module = importlib.import_module(node.module)
                for alias in node.names:
                    assert hasattr(module, alias.name), f"{where}: {node.module}.{alias.name}"


def _calls(name: str):
    for _, body in _python_bodies():
        for node in ast.walk(ast.parse(body)):
            if isinstance(node, ast.Call) and getattr(node.func, "id", getattr(node.func, "attr", None)) == name:
                yield node


def test_host_values_are_passed_explicitly():
    detail_calls = list(_calls("run_detail_path"))
    assert detail_calls, "no run_detail_path call found in the skill prose"
    for call in detail_calls:
        assert "runs_dir" in {k.arg for k in call.keywords}
    for fn in ("classify_citations", "unresolved_citations"):
        fn_calls = list(_calls(fn))
        assert fn_calls, f"no {fn} call found in the skill prose"
        for call in fn_calls:
            repo_root = {k.arg: k.value for k in call.keywords}.get("repo_root")
            assert repo_root is not None
            assert not (isinstance(repo_root, ast.Call) and getattr(repo_root.func, "id", "") == "Path")


def test_no_python_c_body_opens_a_literal_ledger_path():
    for where, body in _python_bodies():
        if not where.endswith("python -c"):
            continue
        for node in ast.walk(ast.parse(body)):
            if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "open":
                assert not (node.args and isinstance(node.args[0], ast.Constant)), where
