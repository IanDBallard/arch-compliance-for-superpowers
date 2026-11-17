"""The auditor finding contract: what a review auditor reports for one mandate."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from acf.adr.contract import PosixStr

AuditorSeverity = Literal["blocking", "important", "nit", "suggestion"]


class AuditorFinding(BaseModel):
    """One finding, anchored to a file and line."""

    model_config = ConfigDict(extra="forbid")

    mandate_id: str
    path: PosixStr
    line: int = Field(ge=1)
    snippet: str
    severity: AuditorSeverity
    rule: str
    why: str
    suggested_fix: str


class AuditorPayload(BaseModel):
    """One auditor group's report."""

    model_config = ConfigDict(extra="forbid")

    group: str
    files_examined: int = Field(ge=0)
    findings: list[AuditorFinding]
    errors: list[str]
