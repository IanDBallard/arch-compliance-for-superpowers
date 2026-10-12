"""The host contract: where a host keeps the gate's records.

A host declares two storage locations in its ADR declaration file (located by
``acf.repo.ADR_REL``). Its doctrine is not declared: it is the host's
architecture doctrine document (``acf.repo.ARCH_REL``) and the documents that
file points to, which must exist before any review runs.
"""
from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from acf.adr.contract import PosixStr
from acf.loader import load_model_file, require_file
from acf.repo import ADR_REL, ARCH_REL


class AdrHostConfig(BaseModel):
    """The two host values the gate cannot derive."""

    model_config = ConfigDict(extra="forbid")

    runs_dir: PosixStr = Field(min_length=1)
    ledger_path: PosixStr = Field(min_length=1)


def load_host_config(repo: Path) -> AdrHostConfig:
    """Refuse a host without its doctrine document, then load its declaration."""
    require_file(repo / ARCH_REL, subject="doctrine document")
    return load_model_file(
        repo / ADR_REL, AdrHostConfig, subject="ADR host config", fmt="yaml"
    )
