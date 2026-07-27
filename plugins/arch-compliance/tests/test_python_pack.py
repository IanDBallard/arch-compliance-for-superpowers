from pathlib import Path

from acf.detectors.python_pack import scan_python_file
from acf.finding import Severity

FIX = Path(__file__).parent / "fixtures" / "python"


def test_bare_except_detected():
    text = (FIX / "bad_except.py").read_text(encoding="utf-8")
    # except Exception is on line 4 of the fixture
    findings = scan_python_file(text, "bad_except.py", added_lines=frozenset({4}))
    assert any(
        f.mandate_id == "fail-loud.bare-except" and f.severity == Severity.BLOCK
        for f in findings
    )


def test_clean_file_no_findings():
    text = (FIX / "good.py").read_text(encoding="utf-8")
    findings = scan_python_file(text, "good.py", added_lines=frozenset({1, 2, 3}))
    assert findings == []


def test_exemption_skips():
    text = "try:\n    x()\nexcept Exception:  # fail-loud.bare-except-ok: legacy bridge\n    pass\n"
    findings = scan_python_file(text, "ex.py", added_lines=frozenset({3}))
    assert findings == []


def test_hasattr_detected():
    text = "def f(obj):\n    return hasattr(obj, 'x')\n"
    findings = scan_python_file(text, "hasattr.py", added_lines=frozenset({2}))
    assert any(
        f.mandate_id == "no-shims.hasattr" and f.severity == Severity.WARN
        for f in findings
    )
