from pathlib import Path

import pytest

from acf.detectors import typescript_bridge
from acf.detectors.typescript_bridge import TS_DETECTOR_IDS, scan_typescript_file
from acf.exceptions import DetectorPackError
from acf.finding import Severity

FIX = Path(__file__).parent / "fixtures" / "typescript"


def test_detector_ids():
    assert TS_DETECTOR_IDS == frozenset({"empty_catch", "explicit_any"})


def test_missing_node_modules_error_is_actionable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A fresh plugin install has no node_modules in the pack dir; the error
    must say exactly how to fix it, not fail with an opaque npx error."""
    fake_pack = tmp_path / "typescript"
    (fake_pack / "src").mkdir(parents=True)
    monkeypatch.setattr(typescript_bridge, "_PACK_ROOT", fake_pack)
    with pytest.raises(DetectorPackError) as exc_info:
        scan_typescript_file(FIX / "bad.tsx")
    message = str(exc_info.value)
    assert "npm ci" in message
    assert fake_pack.as_posix() in message


def test_empty_catch_via_bridge():
    path = FIX / "bad.tsx"
    # empty catch is on line 4 of the fixture
    findings = scan_typescript_file(path, added_lines=frozenset({4}))
    assert any(
        f.mandate_id == "fail-loud.empty-catch"
        and f.severity == Severity.BLOCK
        and f.detector == "empty_catch"
        for f in findings
    )


def test_clean_file_no_findings():
    path = FIX / "good.tsx"
    findings = scan_typescript_file(path, added_lines=frozenset({1, 2, 3, 4, 5, 6, 7, 8}))
    assert findings == []


def test_explicit_any_via_bridge():
    path = FIX / "bad.tsx"
    # `: any` on line 7, `as any` on line 8
    findings = scan_typescript_file(path, added_lines=frozenset({7, 8}))
    any_findings = [f for f in findings if f.mandate_id == "no-shims.explicit-any"]
    assert len(any_findings) >= 1
    assert all(f.severity == Severity.WARN and f.detector == "explicit_any" for f in any_findings)


def test_line_filter_excludes_other_lines():
    path = FIX / "bad.tsx"
    # Only request a clean line — should not report the empty catch on line 4
    findings = scan_typescript_file(path, added_lines=frozenset({1}))
    assert findings == []
