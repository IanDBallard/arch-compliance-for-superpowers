from __future__ import annotations
from pathlib import Path
from typing import Literal
import yaml
from pydantic import BaseModel
from acf.exceptions import RegistryLoadError, UnknownDetectorError

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
    if not path.is_file():
        raise RegistryLoadError(f"mandates file not found: {path.as_posix()}")
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise RegistryLoadError(f"invalid YAML in {path.as_posix()}: {e}") from e
    if not isinstance(raw, list):
        raise RegistryLoadError(f"mandates root must be a list: {path.as_posix()}")
    try:
        mandates = [Mandate.model_validate(row) for row in raw]
    except Exception as e:
        raise RegistryLoadError(f"mandate validation failed: {e}") from e
    if known_detectors is not None:
        for m in mandates:
            if m.status == "enforced" and m.detection == "ast" and m.detector not in known_detectors:
                raise UnknownDetectorError(
                    f"enforced mandate {m.id!r} references unknown detector {m.detector!r}"
                )
    return MandateRegistry(mandates=mandates, source_path=path.as_posix())
