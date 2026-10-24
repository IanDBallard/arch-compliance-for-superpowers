from __future__ import annotations
from collections import Counter
from pathlib import Path
from typing import Any, Literal
from pydantic import BaseModel
from acf.exceptions import AcfInputError, UnknownDetectorError
from acf.loader import load_model_file

Detection = Literal["ast", "llm", "grep", "guard", "manual"]
Status = Literal["enforced", "partial", "unenforced"]
Language = Literal["python", "typescript", "both", "none"]


class Mandate(BaseModel):
    id: str
    title: str
    severity: Literal["BLOCK", "WARN"]
    detection: Detection
    detector: str
    languages: Language
    call_sites: list[str]
    exemption_tokens: list[str]
    status: Status
    arch_anchor: str
    auditor: str | None = None
    params: dict[str, Any] | None = None


class MandateRegistry(BaseModel):
    mandates: list[Mandate]
    source_path: str

    @property
    def by_id(self) -> dict[str, Mandate]:
        return {m.id: m for m in self.mandates}


def load_mandates(
    path: Path,
    *,
    known_detectors: frozenset[str] | None = None,
) -> MandateRegistry:
    mandates = load_model_file(
        path, Mandate, subject="mandates file", fmt="yaml", many=True
    )
    repeated = sorted(i for i, n in Counter(m.id for m in mandates).items() if n > 1)
    if repeated:
        raise AcfInputError(
            f"mandates file {path.as_posix()} repeats mandate id(s) {repeated}; "
            "by_id would keep only the last row of each"
        )
    if known_detectors is not None:
        for m in mandates:
            if m.status != "enforced":
                continue
            if m.detection in {"ast", "guard"} and m.detector not in known_detectors:
                raise UnknownDetectorError(
                    f"enforced mandate {m.id!r} references unknown detector {m.detector!r}"
                )
    return MandateRegistry(mandates=mandates, source_path=path.as_posix())


def missing_anchors(registry: MandateRegistry, doctrine_text: str) -> list[str]:
    """Ids of rows whose ``arch_anchor`` is not a literal substring of the doctrine."""
    return [m.id for m in registry.mandates if m.arch_anchor not in doctrine_text]
