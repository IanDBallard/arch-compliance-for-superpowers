"""The host contract: adr.yml plus the fixed doctrine document."""
from __future__ import annotations

from pathlib import Path

import pytest

from acf.adr import AdrHostConfig, load_host_config
from acf.exceptions import AcfInputError

VALID = "runs_dir: reviews/runs\nledger_path: reviews/ledger.jsonl\n"


def _host(root: Path, adr_yml: str | None = VALID, doctrine: bool = True) -> Path:
    cfg = root / "config" / "architecture"
    cfg.mkdir(parents=True)
    if adr_yml is not None:
        (cfg / "adr.yml").write_text(adr_yml, encoding="utf-8")
    if doctrine:
        (cfg / "ARCHITECTURE.md").write_text("# Doctrine\n", encoding="utf-8")
    return root


def test_a_valid_declaration_loads(tmp_path):
    cfg = load_host_config(_host(tmp_path))
    assert isinstance(cfg, AdrHostConfig)
    assert cfg.runs_dir == "reviews/runs"
    assert cfg.ledger_path == "reviews/ledger.jsonl"


def test_storage_locations_need_not_exist_yet(tmp_path):
    host = _host(tmp_path)
    assert not (host / "reviews").exists()
    load_host_config(host)


@pytest.mark.parametrize(
    "adr_yml,fragment",
    [
        (None, "ADR host config not found"),
        (VALID + "spec_dir: specs\n", "invalid ADR host config"),
        ("ledger_path: reviews/ledger.jsonl\n", "invalid ADR host config"),
        ("runs_dir: reviews/runs\n", "invalid ADR host config"),
        ('runs_dir: ""\nledger_path: reviews/ledger.jsonl\n', "invalid ADR host config"),
        ("runs_dir: reviews\\runs\nledger_path: reviews/ledger.jsonl\n", "invalid ADR host config"),
    ],
    ids=["absent", "unknown-key", "missing-runs_dir", "missing-ledger_path", "empty-value", "backslash"],
)
def test_a_bad_declaration_is_refused(tmp_path, adr_yml, fragment):
    with pytest.raises(AcfInputError) as excinfo:
        load_host_config(_host(tmp_path, adr_yml=adr_yml))
    assert fragment in str(excinfo.value)


def test_an_absent_doctrine_document_is_refused(tmp_path):
    with pytest.raises(AcfInputError) as excinfo:
        load_host_config(_host(tmp_path, doctrine=False))
    assert "doctrine document not found" in str(excinfo.value)


def test_a_subdirectory_is_not_a_host(tmp_path):
    """Review Focus 1: run below the host root, the load refuses — it never guesses."""
    host = _host(tmp_path)
    sub = host / "src"
    sub.mkdir()
    with pytest.raises(AcfInputError):
        load_host_config(sub)
