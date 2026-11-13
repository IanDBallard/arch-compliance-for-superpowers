"""The moved gate prose and the review prose: Python resolves here, and nothing names an origin host."""
from __future__ import annotations

import ast
import importlib
import re
from pathlib import Path

from acf.review.rules import RULES

SKILLS = Path(__file__).resolve().parents[1] / "skills"
GATE = SKILLS / "adversarial-design-review"
RESPOND = SKILLS / "responding-to-adversarial-review"
HOUSEKEEPING = SKILLS / "post-merge-housekeeping"
REVIEW_SKILL = SKILLS / "architecture-review" / "SKILL.md"
FILES = [
    GATE / "SKILL.md", GATE / "claims" / "extraction.md",
    GATE / "reviewers" / "compliance.md", GATE / "reviewers" / "hardening.md",
    GATE / "reviewers" / "refuter.md", GATE / "reviewers" / "sweeper.md",
    RESPOND / "SKILL.md",
    HOUSEKEEPING / "SKILL.md",
]
RULES_DIR = SKILLS / "architecture-review" / "rules"
REVIEW_PY = Path(__file__).resolve().parents[1] / "python" / "acf" / "review"
PACK_IDS = ["python", "ts-js", "react", "svelte", "html-templates", "sql"]
REVIEW_FILES = (
    [RULES_DIR / f"{rule}.md" for rule in sorted(RULES)]
    + [RULES_DIR / "_contract.md", REVIEW_SKILL]
    + [REVIEW_PY / "packs" / f"{pack}.yml" for pack in PACK_IDS]
)
FORBIDDEN = [
    "GEMINI", "CLAUDE.md", "SKILL_PROVENANCE", "scripts.core",
    "docs/design", "docs/reviews", "docs/architecture", ".cursor",
    "run_cms_e2e", "expected_branch.txt", "CMS_SKIP_BRANCH_GUARD",
    "ARCHITECTURE_REVIEW_2026",
    "ContentMetadataService", "index.yml", "DeclaredFSM", "HistoricMansions",
    "PosixPathStr", "structural_realizations", "IMAGES_YAML", "scripts/core",
    "templates/families",
]


def test_review_string_constants_name_no_origin_host():
    modules = sorted(REVIEW_PY.glob("*.py"))
    assert modules
    hits = []
    for module in modules:
        tree = ast.parse(module.read_text(encoding="utf-8"), filename=str(module))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                hits += [f"{module.name}:{node.lineno}: {lit}" for lit in FORBIDDEN if lit in node.value]
    assert hits == [], "\n".join(hits)


def _python_bodies() -> list[tuple[str, str]]:
    bodies = []
    for skill in (GATE / "SKILL.md", RESPOND / "SKILL.md", HOUSEKEEPING / "SKILL.md", REVIEW_SKILL):
        text = skill.read_text(encoding="utf-8")
        bodies += [(f"{skill.parent.name}:python", b) for b in re.findall(r"```python\n(.*?)```", text, re.S)]
        bodies += [(f"{skill.parent.name}:python -c", b) for b in re.findall(r'python -c "\n(.*?)"\n', text, re.S)]
    return bodies


def test_the_seven_files_moved():
    missing = [p.as_posix() for p in FILES if not p.is_file()]
    assert missing == []


def test_the_review_files_exist():
    missing = [p.as_posix() for p in REVIEW_FILES if not p.is_file()]
    assert missing == []


def test_the_prose_names_no_origin_host():
    root = SKILLS.parent
    hits = [f"{p.relative_to(root).as_posix()}:{n}: {lit}"
            for p in FILES + REVIEW_FILES
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
