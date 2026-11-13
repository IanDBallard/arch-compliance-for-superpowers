"""The auditor finding contract."""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from acf.review.contract import AuditorFinding

OK = dict(
    mandate_id="M1", path="src/a.py", line=1, snippet="x", severity="nit",
    rule="r", why="w", suggested_fix="f",
)


def test_a_valid_finding_builds():
    assert AuditorFinding(**OK).line == 1


def test_a_backslash_path_is_refused():
    with pytest.raises(ValidationError):
        AuditorFinding(**{**OK, "path": "src" + chr(92) + "a.py"})


def test_line_zero_is_refused():
    with pytest.raises(ValidationError):
        AuditorFinding(**{**OK, "line": 0})
