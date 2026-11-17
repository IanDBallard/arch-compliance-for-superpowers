"""Per-rule settings models and the validation of a mandate's review rows.

Every key is optional: an absent scalar is None and an absent list is empty,
which turns the check that key feeds off.
"""
from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from acf.exceptions import AcfInputError, UnknownMandateError
from acf.registry import Mandate, MandateRegistry
from acf.repo import RepoTree


class RuleSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    surface: list[str] | None = None
    surface_exclude: list[str] = Field(default_factory=list)
    docs: list[str] = Field(default_factory=list)


class ExceptionBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    class_name: str
    module: str


class Tier(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    paths: list[str] = Field(default_factory=list)


class Crossing(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_tier: str
    to_tier: str
    root_names: list[str] = Field(default_factory=list)
    via: list[str] = Field(default_factory=list)


class FailLoudSettings(RuleSettings):
    exception_base: ExceptionBase | None = None


class NoShimsSettings(RuleSettings):
    exempt_paths: list[str] = Field(default_factory=list)


class PosixPathsSettings(RuleSettings):
    path_types: list[str] = Field(default_factory=list)


class ClassCohesionSettings(RuleSettings):
    facades: list[str] = Field(default_factory=list)


class UiLogicIsolationSettings(RuleSettings):
    pass


class SingleOwnerSettings(RuleSettings):
    target_literal_re: str | None = None
    allowlist_globs: list[str] = Field(default_factory=list)
    inventory: str | None = None

    @field_validator("target_literal_re")
    @classmethod
    def _compiles(cls, value: str | None) -> str | None:
        if value is not None:
            try:
                re.compile(value)
            except re.error as exc:
                raise ValueError(f"target_literal_re does not compile: {exc}") from exc
        return value


class PipelineIsolationSettings(RuleSettings):
    shared_stages: list[str] = Field(default_factory=list)
    variant_stages: list[str] = Field(default_factory=list)
    exempt: list[str] = Field(default_factory=list)
    variant_terms: list[str] = Field(default_factory=list)
    raw_sources: list[str] = Field(default_factory=list)
    canonical_artifact: str | None = None


class PresentationAsDataSettings(RuleSettings):
    bindings: list[str] = Field(default_factory=list)
    style_schema: str | None = None
    element_key: str | None = None
    variant_key: str | None = None


class LayerBoundariesSettings(RuleSettings):
    tiers: list[Tier] = Field(default_factory=list)
    crossings: list[Crossing] = Field(default_factory=list)


class StateMachineDisciplineSettings(RuleSettings):
    base_classes: list[str] = Field(default_factory=list)
    state_field: str | None = None
    validator_name: str | None = None


class PathProvenanceSettings(RuleSettings):
    classifier: str | None = None


class DataAccessBoundarySettings(RuleSettings):
    client_paths: list[str] = Field(default_factory=list)
    policy_files: list[str] = Field(default_factory=list)
    privileged_credentials: list[str] = Field(default_factory=list)
    replication_rules: list[str] = Field(default_factory=list)


RULES: dict[str, type[RuleSettings]] = {
    "fail-loud": FailLoudSettings,
    "no-shims": NoShimsSettings,
    "posix-paths": PosixPathsSettings,
    "class-cohesion": ClassCohesionSettings,
    "ui-logic-isolation": UiLogicIsolationSettings,
    "single-owner": SingleOwnerSettings,
    "pipeline-isolation": PipelineIsolationSettings,
    "presentation-as-data": PresentationAsDataSettings,
    "layer-boundaries": LayerBoundariesSettings,
    "state-machine-discipline": StateMachineDisciplineSettings,
    "path-provenance": PathProvenanceSettings,
    "data-access-boundary": DataAccessBoundarySettings,
}


@dataclass(frozen=True)
class ReviewRow:
    mandate: Mandate
    settings: RuleSettings | None
    prompt: Path | None
    undeclared: list[str]


def _rule_row(mandate: Mandate, model: type[RuleSettings]) -> ReviewRow:
    params = mandate.params or {}
    try:
        settings = model.model_validate(params)
    except ValidationError as exc:
        raise AcfInputError(f"mandate {mandate.id!r}: {exc}") from exc
    undeclared = sorted(set(params) - set(model.model_fields))
    if undeclared and mandate.detection not in {"ast", "guard"}:
        raise AcfInputError(
            f"mandate {mandate.id!r}: params keys {undeclared} are not settings of "
            f"rule {mandate.auditor!r}"
        )
    return ReviewRow(mandate=mandate, settings=settings, prompt=None, undeclared=undeclared)


def check_auditors(registry: MandateRegistry, repo: Path) -> list[ReviewRow]:
    """The reviewed rows: every active row with an ``auditor``, whatever its ``call_sites``."""
    tree = RepoTree(repo)
    rows: list[ReviewRow] = []
    for mandate in registry.mandates:
        auditor = mandate.auditor
        if not mandate.is_active or auditor is None:
            continue
        if auditor in RULES:
            rows.append(_rule_row(mandate, RULES[auditor]))
        elif auditor.endswith(".md"):
            prompt = tree.file(auditor)
            if prompt is None:
                raise UnknownMandateError(
                    f"mandate {mandate.id!r}: auditor prompt file not found: {auditor!r}"
                )
            rows.append(ReviewRow(mandate=mandate, settings=None, prompt=prompt, undeclared=[]))
        else:
            raise UnknownMandateError(
                f"mandate {mandate.id!r}: auditor {auditor!r} is neither a rule "
                f"{sorted(RULES)} nor a .md prompt file"
            )
    return rows


def select_rows(rows: list[ReviewRow], ids: Sequence[str] | None) -> list[ReviewRow]:
    if ids is None:
        return rows
    known = {row.mandate.id for row in rows}
    for wanted in ids:
        if wanted not in known:
            raise UnknownMandateError(f"mandate id {wanted!r} matches no reviewed row")
    return [row for row in rows if row.mandate.id in set(ids)]


def group_rows(rows: list[ReviewRow]) -> dict[str, list[ReviewRow]]:
    groups: dict[str, list[ReviewRow]] = {}
    for row in rows:
        groups.setdefault(row.mandate.auditor or "", []).append(row)
    return groups
