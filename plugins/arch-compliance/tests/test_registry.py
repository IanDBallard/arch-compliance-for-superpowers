from pathlib import Path
import pytest
import yaml
from acf.detectors import KNOWN_DETECTORS
from acf.judge import LLM_PROMPT_IDS
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
        load_mandates(path, known_detectors=KNOWN_DETECTORS)


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
    doctrine = "# Doctrine\n\nIntro mentions `## Gone` inline in backticks.\n\n## Kept\n"
    assert missing_anchors(load_mandates(path), doctrine) == ["gone"]


def _write(tmp_path: Path, **fields) -> Path:
    row = {
        "id": "fail-loud.bare-except",
        "title": "t",
        "severity": "BLOCK",
        "detection": "ast",
        "detector": "fail_loud_bare_except",
        "languages": "python",
        "call_sites": ["ci"],
        "exemption_tokens": ["x"],
        "status": "enforced",
        "arch_anchor": "# X",
    }
    row.update(fields)
    path = tmp_path / "mandates.yml"
    path.write_text(yaml.safe_dump([row]), encoding="utf-8")
    return path


_HOST_GUARD = "scripts/ci/guard.py:scan"


@pytest.mark.parametrize(
    "fields",
    [
        {"detection": "llm", "detector": "llm_fail_loud", "call_sites": ["audit"]},
        {"detection": "manual", "detector": "d", "call_sites": ["audit"]},
        {"detection": "guard", "detector": _HOST_GUARD, "call_sites": ["ci"]},
    ],
)
def test_non_builtin_active_row_with_builtin_mandate_id_refused(tmp_path, fields):
    with pytest.raises(AcfInputError, match="built-in"):
        load_mandates(
            _write(tmp_path, **fields),
            known_detectors=KNOWN_DETECTORS,
            llm_prompt_ids=LLM_PROMPT_IDS,
            repo_root=tmp_path,
        )
    loaded = load_mandates(
        _write(tmp_path, status="unenforced", **fields),
        known_detectors=KNOWN_DETECTORS,
        llm_prompt_ids=LLM_PROMPT_IDS,
        repo_root=tmp_path,
    )
    assert loaded.mandates[0].status == "unenforced"


@pytest.mark.parametrize("detector", ["scripts/g.py:", "../a.py:f", "a.txt:f", "scripts/g.py:1x"])
@pytest.mark.parametrize("status", ["enforced", "unenforced"])
@pytest.mark.parametrize("with_known", [True, False])
def test_malformed_host_reference_refused(tmp_path, detector, status, with_known):
    path = _write(tmp_path, id="host.row", detector=detector, status=status)
    kwargs = {"known_detectors": KNOWN_DETECTORS} if with_known else {}
    with pytest.raises(AcfInputError):
        load_mandates(path, **kwargs)


def test_backslash_host_reference_refused(tmp_path):
    with pytest.raises(AcfInputError, match="backslash"):
        load_mandates(
            _write(
                tmp_path,
                id="host.row",
                detector="scripts\\ci\\guard.py:scan",
                detection="guard",
                call_sites=["ci"],
            )
        )


def test_active_ast_row_with_only_audit_refused(tmp_path):
    with pytest.raises(AcfInputError, match="Tier-1"):
        load_mandates(_write(tmp_path, call_sites=["audit"]))


def test_active_host_ast_row_with_languages_none_refused(tmp_path):
    with pytest.raises(AcfInputError, match="languages"):
        load_mandates(_write(tmp_path, id="host.row", detector=_HOST_GUARD, languages="none"))


def test_partial_unknown_builtin_refused(tmp_path):
    path = _write(tmp_path, detector="not_a_real_detector", status="partial")
    with pytest.raises(UnknownDetectorError):
        load_mandates(path, known_detectors=KNOWN_DETECTORS)


def test_ast_row_naming_llm_prompt_id_refused(tmp_path):
    path = _write(tmp_path, detector="llm_fail_loud")
    with pytest.raises(UnknownDetectorError):
        load_mandates(path, known_detectors=KNOWN_DETECTORS)


def test_builtin_row_with_another_id_refused(tmp_path):
    path = _write(tmp_path, id="other.id")
    with pytest.raises(AcfInputError, match="never receive"):
        load_mandates(path, known_detectors=KNOWN_DETECTORS)


def test_ratchet_row_declaring_hook_refused(tmp_path):
    path = _write(
        tmp_path,
        id="fail-loud.ratchet",
        detector="fail_loud_ratchet",
        detection="guard",
        call_sites=["ci", "hook"],
    )
    with pytest.raises(AcfInputError, match="hook"):
        load_mandates(path, known_detectors=KNOWN_DETECTORS)


def test_host_row_without_repo_root_refused(tmp_path):
    path = _write(tmp_path, id="host.row", detection="guard", detector=_HOST_GUARD)
    with pytest.raises(AcfInputError, match="repo_root"):
        load_mandates(path, known_detectors=KNOWN_DETECTORS)


def test_host_row_with_missing_file_refused(tmp_path):
    path = _write(tmp_path, id="host.row", detection="guard", detector=_HOST_GUARD)
    with pytest.raises(UnknownDetectorError):
        load_mandates(path, known_detectors=KNOWN_DETECTORS, repo_root=tmp_path)


def test_host_row_with_existing_file_loads_without_importing_it(tmp_path):
    guard = tmp_path / "scripts" / "ci" / "guard.py"
    guard.parent.mkdir(parents=True)
    guard.write_text("raise RuntimeError('imported at load')\n", encoding="utf-8")
    path = _write(tmp_path, id="host.row", detection="guard", detector=_HOST_GUARD)
    loaded = load_mandates(path, known_detectors=KNOWN_DETECTORS, repo_root=tmp_path)
    assert loaded.mandates[0].detector == _HOST_GUARD


def test_active_llm_row_with_unknown_prompt_id_refused_unenforced_loads(tmp_path):
    fields = {"id": "soft.x", "detection": "llm", "detector": "llm_not_a_prompt",
              "call_sites": ["audit"]}
    with pytest.raises(UnknownDetectorError):
        load_mandates(_write(tmp_path, **fields), llm_prompt_ids=LLM_PROMPT_IDS)
    assert load_mandates(
        _write(tmp_path, status="unenforced", **fields), llm_prompt_ids=LLM_PROMPT_IDS
    ).mandates


def test_call_site_outside_vocabulary_refused_at_row_construction(tmp_path):
    with pytest.raises(AcfInputError):
        load_mandates(_write(tmp_path, call_sites=["ci", "hooks"]))
