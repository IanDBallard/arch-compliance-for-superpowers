from __future__ import annotations
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal
from pydantic import BaseModel, model_validator
from acf.engine import validate_posix_rel_path
from acf.exceptions import AcfInputError, UnknownDetectorError
from acf.loader import load_model_file
from acf.repo import RepoTree

Detection = Literal["ast", "llm", "grep", "guard", "manual"]
Status = Literal["enforced", "partial", "unenforced"]
Language = Literal["python", "typescript", "both", "none"]
CallSite = Literal["ci", "precommit", "hook", "posttooluse", "audit"]
DIFF_CALL_SITES: frozenset[str] = frozenset({"ci", "precommit"})
HOOK_CALL_SITES: frozenset[str] = frozenset({"hook", "posttooluse"})
TIER1_CALL_SITES: frozenset[str] = DIFF_CALL_SITES | HOOK_CALL_SITES
_ACTIVE_HOST_AST_LANGUAGES = frozenset({"python", "typescript", "both"})


@dataclass(frozen=True)
class BuiltinDetector:
    mandate_id: str
    call_sites: frozenset[str]


def is_host_detector_ref(detector: str) -> bool:
    return ":" in detector


def parse_host_detector_ref(detector: str) -> tuple[str, str]:
    rel_path, _, attr = detector.partition(":")
    if not attr.isidentifier():
        raise AcfInputError(
            f"host detector {detector!r}: callable must be an identifier "
            "('<posix_rel_path.py>:<callable_name>')"
        )
    try:
        validate_posix_rel_path(rel_path)
    except ValueError as exc:
        raise AcfInputError(f"host detector {detector!r}: {exc}") from exc
    if not rel_path.endswith(".py") or rel_path.rsplit("/", 1)[-1] == ".py":
        raise AcfInputError(f"host detector {detector!r}: path must name a .py file")
    return rel_path, attr


class Mandate(BaseModel):
    id: str
    title: str
    severity: Literal["BLOCK", "WARN"]
    detection: Detection
    detector: str
    languages: Language
    call_sites: list[CallSite]
    exemption_tokens: list[str]
    status: Status
    arch_anchor: str
    auditor: str | None = None
    params: dict[str, Any] | None = None

    @property
    def is_active(self) -> bool:
        return self.status != "unenforced"

    def runs_at(self, call_sites: frozenset[str]) -> bool:
        return self.is_active and bool(call_sites.intersection(self.call_sites))

    @model_validator(mode="after")
    def _row_shape(self) -> Mandate:
        if self.detection not in {"ast", "guard"}:
            return self
        host = is_host_detector_ref(self.detector)
        if host:
            parse_host_detector_ref(self.detector)
        if not self.is_active:
            return self
        if not TIER1_CALL_SITES.intersection(self.call_sites):
            raise AcfInputError(
                f"active mandate {self.id!r} declares no Tier-1 call site "
                f"{sorted(TIER1_CALL_SITES)}; got {self.call_sites!r}"
            )
        if host and self.detection == "ast" and self.languages not in _ACTIVE_HOST_AST_LANGUAGES:
            raise AcfInputError(
                f"active host ast mandate {self.id!r} must declare languages in "
                f"{sorted(_ACTIVE_HOST_AST_LANGUAGES)}; got {self.languages!r}"
            )
        return self


class MandateRegistry(BaseModel):
    mandates: list[Mandate]
    source_path: str

    @model_validator(mode="after")
    def _unique_ids(self) -> MandateRegistry:
        repeated = sorted(i for i, n in Counter(m.id for m in self.mandates).items() if n > 1)
        if repeated:
            raise AcfInputError(
                f"mandates file {self.source_path} repeats mandate id(s) {repeated}; "
                "by_id would keep only the last row of each"
            )
        return self

    @property
    def by_id(self) -> dict[str, Mandate]:
        return {m.id: m for m in self.mandates}

    def active(
        self,
        call_sites: frozenset[str],
        *,
        detector: str | None = None,
        detection: str | None = None,
    ) -> list[Mandate]:
        return [
            m for m in self.mandates
            if m.runs_at(call_sites)
            and (detector is None or m.detector == detector)
            and (detection is None or m.detection == detection)
        ]


def load_mandates(
    path: Path,
    *,
    known_detectors: Mapping[str, BuiltinDetector] | None = None,
    llm_prompt_ids: frozenset[str] | None = None,
    repo_root: Path | None = None,
) -> MandateRegistry:
    mandates = load_model_file(path, Mandate, subject="mandates file", fmt="yaml", many=True)
    if llm_prompt_ids is not None:
        for m in mandates:
            if m.is_active and m.detection == "llm" and m.detector not in llm_prompt_ids:
                raise UnknownDetectorError(
                    f"active mandate {m.id!r} references unknown llm prompt id {m.detector!r}"
                )
    if known_detectors is not None:
        reserved = {c.mandate_id for c in known_detectors.values()}
        for m in mandates:
            if not m.is_active:
                continue
            builtin_row = m.detection in {"ast", "guard"} and not is_host_detector_ref(m.detector)
            if m.id in reserved and not builtin_row:
                raise AcfInputError(
                    f"active mandate {m.id!r} uses an id a built-in detector reports to; "
                    "it would receive that detector's findings"
                )
            if m.detection not in {"ast", "guard"}:
                continue
            if not is_host_detector_ref(m.detector):
                _check_builtin(m, known_detectors)
                continue
            if repo_root is None:
                raise AcfInputError(
                    f"active mandate {m.id!r} uses host detector {m.detector!r}; "
                    "pass repo_root to load_mandates"
                )
            rel_path, _ = parse_host_detector_ref(m.detector)
            try:
                module_path = RepoTree(repo_root).file(rel_path)
            except OSError as exc:
                raise UnknownDetectorError(
                    f"active mandate {m.id!r}: cannot stat host detector file "
                    f"{rel_path!r} under {repo_root.as_posix()}: {exc}"
                ) from exc
            if module_path is None:
                raise UnknownDetectorError(
                    f"active mandate {m.id!r}: host detector file not found: "
                    f"{rel_path!r} under {repo_root.as_posix()}"
                )
    return MandateRegistry(mandates=mandates, source_path=path.as_posix())


def _check_builtin(m: Mandate, known: Mapping[str, BuiltinDetector]) -> None:
    contract = known.get(m.detector)
    if contract is None:
        raise UnknownDetectorError(
            f"active mandate {m.id!r} references unknown detector {m.detector!r}"
        )
    if m.id != contract.mandate_id:
        raise AcfInputError(
            f"active mandate {m.id!r}: detector {m.detector!r} reports only to mandate "
            f"{contract.mandate_id!r}, so this row would never receive a finding"
        )
    unserved = TIER1_CALL_SITES.intersection(m.call_sites) - contract.call_sites
    if unserved:
        raise AcfInputError(
            f"active mandate {m.id!r}: detector {m.detector!r} runs only at "
            f"{sorted(contract.call_sites)}, not at {sorted(unserved)}"
        )


def missing_anchors(registry: MandateRegistry, doctrine_text: str) -> list[str]:
    """Ids of rows whose ``arch_anchor`` is not a stripped line of the doctrine."""
    lines = {line.strip() for line in doctrine_text.splitlines()}
    return [m.id for m in registry.mandates if m.arch_anchor.strip() not in lines]
