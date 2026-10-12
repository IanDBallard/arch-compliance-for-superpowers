"""The one load-parse-validate-refuse implementation.

Every input file ACF reads goes through here, so an operator meets one error
type and one message shape no matter which file was wrong. ``subject`` carries
the operator's vocabulary for the file ("mandates file", "baseline"), which is
why one implementation can serve several callers without flattening their
messages.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal, TypeVar, overload

import yaml
from pydantic import BaseModel, ValidationError

from acf.exceptions import AcfInputError

Fmt = Literal["yaml", "json"]
M = TypeVar("M", bound=BaseModel)


def require_file(path: Path, *, subject: str) -> Path:
    """Refuse an absent input file with the message shape every caller shares."""
    if not path.is_file():
        raise AcfInputError(f"{subject} not found: {path.as_posix()}")
    return path


@overload
def load_model_file(
    path: Path, model: type[M], *, subject: str, fmt: Fmt, many: Literal[False] = False
) -> M: ...


@overload
def load_model_file(
    path: Path, model: type[M], *, subject: str, fmt: Fmt, many: Literal[True]
) -> list[M]: ...


def load_model_file(
    path: Path,
    model: type[M],
    *,
    subject: str,
    fmt: Fmt,
    many: bool = False,
) -> M | list[M]:
    """Load ``path``, parse it as ``fmt``, validate against ``model``.

    Raises ``AcfInputError`` for every way the file itself can be wrong: absent,
    unreadable, unparsable, wrong root cardinality, or failing validation. A bug
    inside validation is NOT caught -- only ``ValidationError`` is, so an
    internal error keeps its own type instead of posing as a bad input file.
    """
    require_file(path, subject=subject)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise AcfInputError(f"cannot read {subject} {path.as_posix()}: {exc}") from exc
    try:
        raw: Any = yaml.safe_load(text) if fmt == "yaml" else json.loads(text)
    except (yaml.YAMLError, json.JSONDecodeError) as exc:
        raise AcfInputError(f"invalid {fmt} in {path.as_posix()}: {exc}") from exc
    if many:
        if not isinstance(raw, list):
            raise AcfInputError(f"{subject} root must be a list: {path.as_posix()}")
        try:
            return [model.model_validate(row) for row in raw]
        except ValidationError as exc:
            raise AcfInputError(f"invalid {subject} {path.as_posix()}: {exc}") from exc
    try:
        return model.model_validate(raw)
    except ValidationError as exc:
        raise AcfInputError(f"invalid {subject} {path.as_posix()}: {exc}") from exc
