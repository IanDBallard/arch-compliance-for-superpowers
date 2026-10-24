"""The installed-skills byte check (spec docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md §5.3):
every file of the two gate skills in the clone is byte-identical to the installed copy."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_installed_skills.py"
SKILLS = ("adversarial-design-review", "responding-to-adversarial-review")


def _load_script():
    spec = importlib.util.spec_from_file_location("check_installed_skills", SCRIPT)
    assert spec is not None and spec.loader is not None, f"missing {SCRIPT}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _skill_tree(base: Path) -> None:
    for skill in SKILLS:
        d = base / "skills" / skill
        (d / "reviewers").mkdir(parents=True)
        (d / "SKILL.md").write_bytes(b"# " + skill.encode() + b"\n")
        (d / "reviewers" / "compliance.md").write_bytes(b"reviewer body\n")


@pytest.fixture
def trees(tmp_path: Path) -> tuple[Path, Path]:
    clone = tmp_path / "clone"
    inst = tmp_path / "inst"
    _skill_tree(clone / "plugins" / "arch-compliance")
    _skill_tree(inst)
    return clone, inst


def test_identical_trees_return_zero(trees, capsys):
    clone, inst = trees
    main = _load_script().main
    assert main([str(inst)], clone=clone) == 0
    assert "identical" in capsys.readouterr().out


def test_a_changed_byte_is_reported(trees, capsys):
    clone, inst = trees
    target = inst / "skills" / "adversarial-design-review" / "SKILL.md"
    target.write_bytes(target.read_bytes() + b"x")
    main = _load_script().main
    assert main([str(inst)], clone=clone) == 1
    assert "adversarial-design-review/SKILL.md" in capsys.readouterr().out


def test_a_missing_installed_file_is_reported(trees, capsys):
    clone, inst = trees
    (inst / "skills" / "responding-to-adversarial-review" / "reviewers" / "compliance.md").unlink()
    main = _load_script().main
    assert main([str(inst)], clone=clone) == 1
    assert "responding-to-adversarial-review/reviewers/compliance.md" in capsys.readouterr().out
