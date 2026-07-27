from __future__ import annotations
from enum import Enum
from pydantic import BaseModel


class Severity(str, Enum):
    BLOCK = "BLOCK"
    WARN = "WARN"


class Finding(BaseModel):
    mandate_id: str
    severity: Severity
    path: str  # POSIX
    line: int
    message: str
    detector: str
    confidence: str | None = None
    detection: str = "ast"
