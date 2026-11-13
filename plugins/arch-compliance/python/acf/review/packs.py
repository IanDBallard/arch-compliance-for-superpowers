"""Technology packs: regular-expression hints per rule, shipped inside the package.

A hint is a plain, generic pattern and a short ``tell``; precision is the auditor's job.
"""
from __future__ import annotations

import re
from collections.abc import Sequence
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from acf.exceptions import AcfInputError
from acf.loader import load_model_file
from acf.registry import Mandate
from acf.review.rules import RULES

PACKS_DIR = Path(__file__).parent / "packs"

_ROW_LANGUAGES: dict[str, frozenset[str]] = {
    "python": frozenset({"python"}),
    "typescript": frozenset({"typescript"}),
    "both": frozenset({"python", "typescript"}),
    "none": frozenset(),
}


class Hint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pattern: str
    tell: str

    @field_validator("pattern")
    @classmethod
    def _compiles(cls, value: str) -> str:
        try:
            re.compile(value)
        except re.error as exc:
            raise ValueError(f"hint pattern {value!r} does not compile: {exc}") from exc
        return value


class TechPack(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    language: Literal["python", "typescript", "none"]
    extends: str | None = None
    files: list[str]
    hints: dict[str, list[Hint]] = Field(default_factory=dict)


def _available() -> list[str]:
    return sorted(path.stem for path in PACKS_DIR.glob("*.yml"))


def load_packs(ids: Sequence[str]) -> dict[str, TechPack]:
    """Load the declared packs, in declared order, and refuse an inconsistent declaration."""
    packs: dict[str, TechPack] = {}
    for pack_id in ids:
        path = PACKS_DIR / f"{pack_id}.yml"
        if not path.is_file():
            raise AcfInputError(
                f"unknown technology pack {pack_id!r}; available: {_available()}"
            )
        pack = load_model_file(path, TechPack, subject=f"technology pack {pack_id!r}", fmt="yaml")
        if pack.id != pack_id:
            raise AcfInputError(f"technology pack file {pack_id!r} declares id {pack.id!r}")
        unknown = sorted(set(pack.hints) - set(RULES))
        if unknown:
            raise AcfInputError(
                f"technology pack {pack_id!r}: hint keys {unknown} are not rule ids {sorted(RULES)}"
            )
        packs[pack_id] = pack
    for pack in packs.values():
        if pack.extends is not None and pack.extends not in packs:
            raise AcfInputError(
                f"technology pack {pack.id!r} extends {pack.extends!r}, "
                f"which is not declared; declared: {list(packs)}"
            )
    return packs


def packs_for_row(row: Mandate, packs: dict[str, TechPack]) -> list[TechPack]:
    languages = _ROW_LANGUAGES[row.languages]
    return [p for p in packs.values() if p.language == "none" or p.language in languages]


def hint_files(pack: TechPack, packs: dict[str, TechPack]) -> list[str]:
    """The globs ``pack``'s hints scan: its own, plus every declared add-on's."""
    globs = list(pack.files)
    for other in packs.values():
        if other.extends == pack.id:
            globs.extend(g for g in other.files if g not in globs)
    return globs
