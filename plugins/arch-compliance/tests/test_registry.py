from pathlib import Path
import pytest
from acf.registry import load_mandates
from acf.exceptions import RegistryLoadError, UnknownDetectorError

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_valid_mandates():
    regs = load_mandates(FIXTURES / "mandates_valid.yml")
    assert len(regs.mandates) >= 2
    assert regs.by_id["fail-loud.bare-except"].severity == "BLOCK"


def test_missing_file_fails_loud():
    with pytest.raises(RegistryLoadError):
        load_mandates(FIXTURES / "does-not-exist.yml")


def test_enforced_unknown_detector_fails():
    path = FIXTURES / "mandates_bad_detector.yml"
    path.write_text(
        "- id: x\n  title: t\n  severity: BLOCK\n  detection: ast\n"
        "  detector: not_a_real_detector\n  languages: python\n"
        "  call_sites: [ci]\n  exemption_tokens: [x]\n  status: enforced\n"
        "  arch_anchor: '# X'\n",
        encoding="utf-8",
    )
    with pytest.raises(UnknownDetectorError):
        load_mandates(path, known_detectors=frozenset({"fail_loud_bare_except"}))
