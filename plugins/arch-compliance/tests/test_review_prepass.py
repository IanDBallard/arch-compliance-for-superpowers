"""Target tree, row surfaces and the hint pre-pass."""
from __future__ import annotations

import pytest

from acf.exceptions import AcfInputError, EmptyTargetTreeError
from acf.registry import MandateRegistry
from acf.repo import RepoTree
from acf.review.host import ReviewHostConfig
from acf.review.packs import load_packs
from acf.review.prepass import (
    BUILTIN_EXCLUDES,
    TEST_PATHS,
    Candidate,
    render_candidates,
    row_surface,
    scan,
    target_tree,
)
from acf.review.rules import check_auditors


def _cfg(**over):
    base = dict(
        report_dir="reports",
        baseline_path="base.json",
        baseline_max_age_days=30,
        baseline_max_commits=50,
        packs=["python", "ts-js"],
        subsystems=[],
        exclude=[],
    )
    base.update(over)
    return ReviewHostConfig(**base)


def _row(tmp_path, **over):
    row = {
        "id": "r1",
        "title": "t",
        "severity": "WARN",
        "detection": "llm",
        "detector": "some-prompt",
        "languages": "both",
        "call_sites": ["ci"],
        "exemption_tokens": [],
        "status": "enforced",
        "arch_anchor": "## A",
        "auditor": "fail-loud",
    }
    row.update(over)
    reg = MandateRegistry.model_validate({"mandates": [row], "source_path": "m.yml"})
    return check_auditors(reg, tmp_path)[0]


def _write(root, rel, text="x = 1\n"):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _ctx(tmp_path, **cfg):
    config = _cfg(**cfg)
    return RepoTree(tmp_path), config, load_packs(config.packs)


def test_constants_are_tuples():
    assert ".git/" in BUILTIN_EXCLUDES and "node_modules/" in BUILTIN_EXCLUDES
    assert "tests/" in TEST_PATHS and "test_*.py" in TEST_PATHS


def test_target_tree_excludes_builtin_and_tests(tmp_path):
    _write(tmp_path, "src/a.py")
    _write(tmp_path, "node_modules/x/b.py")
    _write(tmp_path, "tests/t.py")
    _write(tmp_path, "src/test_c.py")
    _write(tmp_path, "web/app.test.ts")
    tree, cfg, packs = _ctx(tmp_path)
    assert target_tree(tree, cfg, packs, paths=None, include_tests=False) == ["src/a.py"]
    with_tests = target_tree(tree, cfg, packs, paths=None, include_tests=True)
    assert with_tests == sorted(["src/a.py", "tests/t.py", "src/test_c.py", "web/app.test.ts"])


def test_target_tree_paths_and_cfg_exclude(tmp_path):
    _write(tmp_path, "src/a.py")
    _write(tmp_path, "gen/b.py")
    _write(tmp_path, "notes/n.txt")
    tree, cfg, packs = _ctx(tmp_path, exclude=["gen/"])
    assert target_tree(tree, cfg, packs, paths=None, include_tests=False) == ["src/a.py"]
    assert target_tree(tree, cfg, packs, paths=["notes/**"], include_tests=False) == ["notes/n.txt"]


def test_empty_tree_raises(tmp_path):
    tree, cfg, packs = _ctx(tmp_path)
    with pytest.raises(EmptyTargetTreeError):
        target_tree(tree, cfg, packs, paths=None, include_tests=False)


def test_default_surface_follows_row_languages(tmp_path):
    _write(tmp_path, "a.py")
    _write(tmp_path, "b.ts")
    tree, cfg, packs = _ctx(tmp_path)
    target = target_tree(tree, cfg, packs, paths=None, include_tests=False)
    py = _row(tmp_path, languages="python")
    assert row_surface(tree, cfg, packs, py, target, include_tests=False, paths_given=False) == ["a.py"]
    both = _row(tmp_path, languages="both")
    assert row_surface(tree, cfg, packs, both, target, include_tests=False, paths_given=False) == ["a.py", "b.ts"]


def test_surface_exclude_applies_with_and_without_declared_surface(tmp_path):
    _write(tmp_path, "src/a.py")
    _write(tmp_path, "src/skip/b.py")
    tree, cfg, packs = _ctx(tmp_path)
    target = target_tree(tree, cfg, packs, paths=None, include_tests=False)
    undeclared = _row(tmp_path, params={"surface_exclude": ["src/skip/**"]})
    assert row_surface(tree, cfg, packs, undeclared, target, include_tests=False, paths_given=False) == ["src/a.py"]
    declared = _row(tmp_path, params={"surface": ["src/**"], "surface_exclude": ["src/skip/**"]})
    assert row_surface(tree, cfg, packs, declared, target, include_tests=False, paths_given=False) == ["src/a.py"]


def test_declared_surface_ignores_paths_and_tests(tmp_path):
    _write(tmp_path, "docs/x.md")
    _write(tmp_path, "src/a.py")
    _write(tmp_path, "tests/t.py")
    tree, cfg, packs = _ctx(tmp_path)
    target = target_tree(tree, cfg, packs, paths=["src/**"], include_tests=False)
    row = _row(tmp_path, params={"surface": ["docs/**", "tests/**"]})
    assert row_surface(tree, cfg, packs, row, target, include_tests=False, paths_given=True) == ["docs/x.md"]
    assert row_surface(tree, cfg, packs, row, target, include_tests=True, paths_given=True) == [
        "docs/x.md",
        "tests/t.py",
    ]


def test_declared_surface_matching_nothing_names_mandate(tmp_path):
    _write(tmp_path, "a.py")
    tree, cfg, packs = _ctx(tmp_path)
    target = target_tree(tree, cfg, packs, paths=None, include_tests=False)
    row = _row(tmp_path, params={"surface": ["nowhere/**"]})
    with pytest.raises(AcfInputError, match="'r1'"):
        row_surface(tree, cfg, packs, row, target, include_tests=False, paths_given=False)


def test_hatch_row_uses_languages(tmp_path):
    _write(tmp_path, "a.py")
    _write(tmp_path, "b.ts")
    (tmp_path / "p.md").write_text("x", encoding="utf-8")
    tree, cfg, packs = _ctx(tmp_path)
    target = target_tree(tree, cfg, packs, paths=None, include_tests=False)
    row = _row(tmp_path, auditor="p.md", languages="typescript")
    assert row.settings is None
    assert row_surface(tree, cfg, packs, row, target, include_tests=False, paths_given=False) == ["b.ts"]


def test_empty_default_surface_names_mandate_languages_and_packs(tmp_path):
    _write(tmp_path, "a.py")
    tree, cfg, packs = _ctx(tmp_path)
    target = target_tree(tree, cfg, packs, paths=None, include_tests=False)
    row = _row(tmp_path, languages="typescript")
    with pytest.raises(AcfInputError) as caught:
        row_surface(tree, cfg, packs, row, target, include_tests=False, paths_given=False)
    message = str(caught.value)
    assert "'r1'" in message and "typescript" in message
    assert "python" in message and "ts-js" in message


def test_empty_default_surface_under_paths_is_out_of_scope(tmp_path):
    _write(tmp_path, "a.py")
    _write(tmp_path, "b.ts")
    tree, cfg, packs = _ctx(tmp_path)
    target = target_tree(tree, cfg, packs, paths=["*.py"], include_tests=False)
    row = _row(tmp_path, languages="typescript")
    assert row_surface(tree, cfg, packs, row, target, include_tests=False, paths_given=True) == []


def test_scan_candidates_per_pack_and_language(tmp_path):
    _write(tmp_path, "a.py", "try:\n    pass\nexcept:\n    pass\n")
    _write(tmp_path, "b.ts", "const x = 1;\n")
    tree, cfg, packs = _ctx(tmp_path)
    row = _row(tmp_path, languages="python")
    cands = scan(tree, row, ["a.py", "b.ts"], packs)
    assert cands == [Candidate("a.py", 3, "bare except", "except:")]
    assert render_candidates(cands) == "a.py:3 [bare except] except:"


def test_scan_truncates_snippet_and_sorts(tmp_path):
    _write(tmp_path, "z.py", "except:" + " " * 300 + "y\n")
    _write(tmp_path, "a.py", "\n\nexcept:\n")
    tree, cfg, packs = _ctx(tmp_path)
    row = _row(tmp_path, languages="python")
    cands = scan(tree, row, ["z.py", "a.py"], packs)
    assert [(c.path, c.line) for c in cands] == [("a.py", 3), ("z.py", 1)]
    assert len(cands[1].snippet) <= 200


def test_rule_without_hints_and_hatch_row_yield_nothing(tmp_path):
    _write(tmp_path, "a.py", "except:\n")
    (tmp_path / "p.md").write_text("x", encoding="utf-8")
    tree, cfg, packs = _ctx(tmp_path)
    hatch = _row(tmp_path, auditor="p.md")
    assert scan(tree, hatch, ["a.py"], packs) == []
    nohint = _row(tmp_path, auditor="layer-boundaries")
    assert scan(tree, nohint, ["a.py"], packs) == []


def test_non_utf8_file_raises_with_posix_key(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "bad.py").write_bytes(b"\xff\xfe")
    tree, cfg, packs = _ctx(tmp_path)
    row = _row(tmp_path, languages="python")
    with pytest.raises(AcfInputError, match="pkg/bad.py"):
        scan(tree, row, ["pkg/bad.py"], packs)


def test_python_hint_does_not_scan_files_outside_pack_globs(tmp_path):
    _write(tmp_path, "b.ts", "except:\n")
    tree, cfg, packs = _ctx(tmp_path)
    row = _row(tmp_path, languages="python")
    assert scan(tree, row, ["b.ts"], packs) == []


def test_extends_addon_files_scanned_by_base_pack(tmp_path):
    _write(tmp_path, "c.svelte", "const xs = items.filter(f);\n")
    row = _row(tmp_path, auditor="ui-logic-isolation", languages="typescript")
    tree, cfg, packs = _ctx(tmp_path, packs=["ts-js", "svelte"])
    cands = scan(tree, row, ["c.svelte"], packs)
    assert [(c.path, c.line, c.tell) for c in cands] == [
        ("c.svelte", 1, "client-side aggregation")
    ]
    tree, cfg, packs = _ctx(tmp_path, packs=["ts-js"])
    assert scan(tree, row, ["c.svelte"], packs) == []


def test_hintless_row_still_decodes_surface(tmp_path):
    (tmp_path / "bad.py").write_bytes(b"\xff\xfe")
    tree, cfg, packs = _ctx(tmp_path, packs=["python"])
    row = _row(tmp_path, auditor="ui-logic-isolation", languages="python")
    with pytest.raises(AcfInputError, match="bad.py"):
        scan(tree, row, ["bad.py"], packs)


def test_line_numbers_split_on_newline_only(tmp_path):
    _write(tmp_path, "a.py", "x = 1\x0c\x1c\u2028\nexcept:\r\n")
    tree, cfg, packs = _ctx(tmp_path)
    row = _row(tmp_path, languages="python")
    (cand,) = scan(tree, row, ["a.py"], packs)
    assert (cand.line, cand.snippet) == (2, "except:")
