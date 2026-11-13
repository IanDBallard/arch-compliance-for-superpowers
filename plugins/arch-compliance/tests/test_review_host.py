"""The review host declaration: review.yml."""
from __future__ import annotations

from pathlib import Path

import pytest

from acf.exceptions import AcfInputError
from acf.review.host import ReviewHostConfig, load_review_config

FIELDS = {
    "report_dir": "reviews/out",
    "baseline_path": "reviews/baseline.json",
    "baseline_max_age_days": "30",
    "baseline_max_commits": "200",
    "packs": "[core]",
    "subsystems": "[src/a, src/b]",
    "exclude": "['**/gen/**']",
}


def _host(root: Path, fields: dict[str, str] | None = None, extra: str = "") -> Path:
    cfg = root / "config" / "architecture"
    cfg.mkdir(parents=True)
    body = "".join(f"{k}: {v}\n" for k, v in (FIELDS if fields is None else fields).items())
    (cfg / "review.yml").write_text(body + extra, encoding="utf-8")
    return root


def test_a_valid_declaration_loads(tmp_path):
    cfg = load_review_config(_host(tmp_path))
    assert isinstance(cfg, ReviewHostConfig)
    assert cfg.report_dir == "reviews/out"
    assert cfg.baseline_max_age_days == 30
    assert cfg.subsystems == ["src/a", "src/b"]
    assert cfg.exclude == ["**/gen/**"]


def test_a_missing_field_is_refused(tmp_path):
    fields = {k: v for k, v in FIELDS.items() if k != "packs"}
    with pytest.raises(AcfInputError):
        load_review_config(_host(tmp_path, fields))


def test_an_extra_field_is_refused(tmp_path):
    with pytest.raises(AcfInputError):
        load_review_config(_host(tmp_path, extra="surprise: 1\n"))


def test_a_backslash_in_report_dir_is_refused(tmp_path):
    fields = {**FIELDS, "report_dir": "'reviews\\out'"}
    with pytest.raises(AcfInputError):
        load_review_config(_host(tmp_path, fields))


def test_a_missing_file_names_acf_setup(tmp_path):
    with pytest.raises(AcfInputError, match="acf-setup"):
        load_review_config(tmp_path)
