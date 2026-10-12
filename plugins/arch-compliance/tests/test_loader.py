"""One loader, one error type, the stricter half of each behavioural axis."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import BaseModel, ConfigDict

from acf.exceptions import AcfInputError
from acf.loader import load_model_file


class Row(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    count: int


def test_missing_file_names_its_subject_and_path(tmp_path):
    missing = tmp_path / "mandates.yml"
    with pytest.raises(AcfInputError) as excinfo:
        load_model_file(missing, Row, subject="mandates file", fmt="yaml", many=True)
    message = str(excinfo.value)
    assert "mandates file not found" in message
    assert missing.as_posix() in message


def test_yaml_list_root_loads_many(tmp_path):
    path = tmp_path / "rows.yml"
    path.write_text("- name: a\n  count: 1\n- name: b\n  count: 2\n", encoding="utf-8")
    rows = load_model_file(path, Row, subject="rows file", fmt="yaml", many=True)
    assert [r.name for r in rows] == ["a", "b"]


def test_json_object_root_loads_one(tmp_path):
    path = tmp_path / "row.json"
    path.write_text(json.dumps({"name": "a", "count": 1}), encoding="utf-8")
    row = load_model_file(path, Row, subject="row file", fmt="json")
    assert row.count == 1


def test_wrong_root_cardinality_is_refused(tmp_path):
    """Review Focus 2: a mapping where a list is required."""
    path = tmp_path / "rows.yml"
    path.write_text("name: a\ncount: 1\n", encoding="utf-8")
    with pytest.raises(AcfInputError) as excinfo:
        load_model_file(path, Row, subject="rows file", fmt="yaml", many=True)
    assert "must be a list" in str(excinfo.value)
    assert path.as_posix() in str(excinfo.value)


def test_unparsable_text_is_refused(tmp_path):
    path = tmp_path / "rows.yml"
    path.write_text("name: [unclosed\n", encoding="utf-8")
    with pytest.raises(AcfInputError):
        load_model_file(path, Row, subject="rows file", fmt="yaml", many=True)


def test_validation_failure_is_refused(tmp_path):
    path = tmp_path / "rows.yml"
    path.write_text("- name: a\n  count: not_an_int\n", encoding="utf-8")
    with pytest.raises(AcfInputError):
        load_model_file(path, Row, subject="rows file", fmt="yaml", many=True)


def test_unreadable_file_is_one_input_error_not_a_bare_oserror(tmp_path, monkeypatch):
    """Review Focus 1: an existing file whose read raises OSError.

    Today this escapes load_mandates as a bare OSError because registry.py
    catches only yaml.YAMLError. The merged loader must surface one type.
    """
    path = tmp_path / "rows.yml"
    path.write_text("- name: a\n  count: 1\n", encoding="utf-8")

    real_read_text = Path.read_text

    def boom(self, *args, **kwargs):
        if self == path:
            raise OSError("permission denied")
        return real_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", boom)
    with pytest.raises(AcfInputError) as excinfo:
        load_model_file(path, Row, subject="rows file", fmt="yaml", many=True)
    assert path.as_posix() in str(excinfo.value)


def test_internal_error_is_not_reported_as_bad_input(tmp_path, monkeypatch):
    """registry.py:52 catches bare Exception; the merge must not.

    A bug inside model validation is not a bad input file, and mislabelling it
    sends the operator to the wrong place.
    """
    path = tmp_path / "rows.yml"
    path.write_text("- name: a\n  count: 1\n", encoding="utf-8")

    def explode(cls, *args, **kwargs):
        raise RuntimeError("internal bug")

    monkeypatch.setattr(Row, "model_validate", classmethod(explode))
    with pytest.raises(RuntimeError):
        load_model_file(path, Row, subject="rows file", fmt="yaml", many=True)


def test_require_file_refuses_an_absent_path_naming_it(tmp_path):
    from acf.loader import require_file

    missing = tmp_path / "ARCHITECTURE.md"
    with pytest.raises(AcfInputError) as excinfo:
        require_file(missing, subject="doctrine document")
    assert str(excinfo.value) == f"doctrine document not found: {missing.as_posix()}"


def test_require_file_returns_the_path_when_present(tmp_path):
    from acf.loader import require_file

    present = tmp_path / "doc.md"
    present.write_text("x\n", encoding="utf-8")
    assert require_file(present, subject="doc") == present
