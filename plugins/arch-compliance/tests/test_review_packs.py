"""Technology packs: shipped files load, refusals are typed, row matching follows §4.3."""
from __future__ import annotations

import re
from pathlib import Path

import pytest
from pydantic import ValidationError

from acf.exceptions import AcfInputError
from acf.registry import Mandate
from acf.review import packs as packs_mod
from acf.review.packs import TechPack, hint_files, load_packs, packs_for_row
from acf.review.rules import RULES

SHIPPED = ["python", "ts-js", "react", "svelte", "html-templates", "sql"]
FORBIDDEN_NAMES = [
    "GEMINI", "CLAUDE.md", "scripts.core", "scripts/core", "docs/design", "docs/reviews",
    "docs/architecture", ".cursor", "ContentMetadataService", "index.yml", "DeclaredFSM",
    "HistoricMansions", "PosixPathStr", "structural_realizations", "IMAGES_YAML",
    "templates/families",
]


def _row(languages: str) -> Mandate:
    return Mandate(
        id="m", title="t", severity="WARN", detection="llm", detector="x",
        languages=languages, call_sites=["audit"], exemption_tokens=[],
        status="unenforced", arch_anchor="a", auditor="fail-loud",
    )


def _pack(**over: object) -> dict:
    base = {"id": "p", "language": "none", "extends": None, "files": ["**/*.x"], "hints": {}}
    base.update(over)
    return base


def test_every_shipped_pack_loads() -> None:
    packs = load_packs(SHIPPED)
    assert list(packs) == SHIPPED
    for pack_id, pack in packs.items():
        assert pack.id == pack_id
        assert pack.files
        assert pack.hints


def test_hint_keys_are_rule_ids_and_patterns_compile() -> None:
    for pack in load_packs(SHIPPED).values():
        for rule, hints in pack.hints.items():
            assert rule in RULES
            assert hints
            for hint in hints:
                re.compile(hint.pattern)
                assert hint.tell


def test_pack_files_name_no_host() -> None:
    for path in (Path(packs_mod.__file__).parent / "packs").glob("*.yml"):
        text = path.read_text(encoding="utf-8")
        for name in FORBIDDEN_NAMES:
            assert name not in text, f"{path.name} names {name}"


@pytest.mark.parametrize(
    ("pack_id", "rule", "line"),
    [
        ("python", "fail-loud", "    except:"),
        ("python", "fail-loud", "if hasattr(x, 'y'):"),
        ("python", "no-shims", "for i in range(3):"),
        ("ts-js", "ui-logic-isolation", "btn.disabled = a && !b;"),
        ("ts-js", "data-access-boundary", "const r = supabase.from('t').select()"),
        ("svelte", "ui-logic-isolation", "let total = $derived(a + b);"),
        ("sql", "data-access-boundary", "CREATE TABLE notes (id int);"),
    ],
)
def test_hints_fire_on_their_shape(pack_id: str, rule: str, line: str) -> None:
    pack = load_packs(["ts-js", pack_id] if pack_id == "svelte" else [pack_id])[pack_id]
    assert any(re.search(h.pattern, line) for h in pack.hints[rule])


def test_unknown_pack_names_id_and_available() -> None:
    with pytest.raises(AcfInputError) as err:
        load_packs(["nope"])
    assert "nope" in str(err.value)
    assert "ts-js" in str(err.value)


def test_addon_without_base_is_refused() -> None:
    with pytest.raises(AcfInputError, match="ts-js"):
        load_packs(["react"])
    with pytest.raises(AcfInputError, match="ts-js"):
        load_packs(["python", "svelte"])
    assert set(load_packs(["ts-js", "react"])) == {"ts-js", "react"}


def test_detectors_key_is_refused() -> None:
    TechPack.model_validate(_pack())
    with pytest.raises(ValidationError):
        TechPack.model_validate(_pack(detectors={"fail-loud": ["x"]}))


def test_uncompilable_pattern_is_refused() -> None:
    bad = _pack(hints={"fail-loud": [{"pattern": "(", "tell": "t"}]})
    with pytest.raises(ValidationError):
        TechPack.model_validate(bad)


def test_unknown_hint_key_and_bad_pattern_in_file_are_input_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(packs_mod, "PACKS_DIR", tmp_path)
    (tmp_path / "a.yml").write_text(
        "id: a\nlanguage: none\nextends: null\nfiles: ['**/*.x']\n"
        "hints:\n  not-a-rule:\n    - {pattern: x, tell: t}\n",
        encoding="utf-8",
    )
    with pytest.raises(AcfInputError, match="not-a-rule"):
        load_packs(["a"])
    (tmp_path / "b.yml").write_text(
        "id: b\nlanguage: none\nextends: null\nfiles: ['**/*.x']\n"
        "hints:\n  fail-loud:\n    - {pattern: '(', tell: t}\n",
        encoding="utf-8",
    )
    with pytest.raises(AcfInputError, match="b"):
        load_packs(["b"])


def _ids(language: str, packs: dict[str, TechPack]) -> list[str]:
    return [p.id for p in packs_for_row(_row(language), packs)]


def test_rows_receive_packs_by_language_in_declared_order() -> None:
    packs = load_packs(SHIPPED)
    assert _ids("python", packs) == ["python", "html-templates", "sql"]
    assert _ids("typescript", packs) == ["ts-js", "react", "svelte", "html-templates", "sql"]
    assert _ids("both", packs) == SHIPPED
    assert _ids("none", packs) == ["html-templates", "sql"]


def test_hint_files_include_addon_globs_for_the_base() -> None:
    packs = load_packs(["ts-js", "svelte"])
    assert "**/*.svelte" in hint_files(packs["ts-js"], packs)
    assert "**/*.ts" in hint_files(packs["ts-js"], packs)
    assert hint_files(packs["svelte"], packs) == ["**/*.svelte"]
    alone = load_packs(["ts-js"])
    assert "**/*.svelte" not in hint_files(alone["ts-js"], alone)
