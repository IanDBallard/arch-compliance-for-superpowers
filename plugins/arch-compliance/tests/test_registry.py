from pathlib import Path
import pytest
from acf.registry import load_mandates, missing_anchors
from acf.exceptions import AcfInputError, UnknownDetectorError

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_valid_mandates():
    regs = load_mandates(FIXTURES / "mandates_valid.yml")
    assert len(regs.mandates) >= 2
    assert regs.by_id["fail-loud.bare-except"].severity == "BLOCK"


def test_missing_file_fails_loud():
    with pytest.raises(AcfInputError):
        load_mandates(FIXTURES / "does-not-exist.yml")


def test_enforced_unknown_detector_fails(tmp_path: Path):
    path = tmp_path / "mandates_bad_detector.yml"
    path.write_text(
        "- id: x\n  title: t\n  severity: BLOCK\n  detection: ast\n"
        "  detector: not_a_real_detector\n  languages: python\n"
        "  call_sites: [ci]\n  exemption_tokens: [x]\n  status: enforced\n"
        "  arch_anchor: '# X'\n",
        encoding="utf-8",
    )
    with pytest.raises(UnknownDetectorError):
        load_mandates(path, known_detectors=frozenset({"fail_loud_bare_except"}))


_ROW = (
    "- id: {id}\n  title: t\n  severity: WARN\n  detection: manual\n"
    "  detector: d\n  languages: python\n  call_sites: [audit]\n"
    "  exemption_tokens: [x]\n  status: enforced\n  arch_anchor: '{anchor}'\n"
)


def test_a_repeated_mandate_id_is_refused(tmp_path: Path):
    path = tmp_path / "mandates_dup.yml"
    path.write_text(
        _ROW.format(id="a", anchor="## A") + _ROW.format(id="a", anchor="## B"),
        encoding="utf-8",
    )
    with pytest.raises(AcfInputError, match="'a'"):
        load_mandates(path)


def test_missing_anchors_names_rows_whose_anchor_is_absent(tmp_path: Path):
    path = tmp_path / "mandates.yml"
    path.write_text(
        _ROW.format(id="kept", anchor="## Kept") + _ROW.format(id="gone", anchor="## Gone"),
        encoding="utf-8",
    )
    assert missing_anchors(load_mandates(path), "# Doctrine\n\n## Kept\n") == ["gone"]
