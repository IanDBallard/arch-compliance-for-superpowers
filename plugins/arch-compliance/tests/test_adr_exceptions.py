"""The ported ADR exceptions obey this plugin's single-base convention."""
from __future__ import annotations

import inspect

import pytest

from acf import exceptions as exc

ADR_TYPES = [
    "ReviewerContractViolationError",
    "SpecKindUndeterminedError",
    "CitationHistoryUnavailableError",
    "LedgerWriteError",
    "RunDetailWriteError",
    "UnresolvableCitationError",
]


@pytest.mark.parametrize("name", ADR_TYPES)
def test_adr_exception_exists(name: str) -> None:
    assert hasattr(exc, name), f"{name} was not rehomed into acf.exceptions"


@pytest.mark.parametrize("name", ADR_TYPES)
def test_adr_exception_derives_from_acferror_alone(name: str) -> None:
    """No stdlib second parent: the origin had mixins, this plugin does not."""
    cls = getattr(exc, name)
    assert cls.__bases__ == (exc.AcfError,), (
        f"{name} must derive from AcfError alone, got {cls.__bases__}. "
        "Every other exception in this module does."
    )


def test_every_exception_in_the_module_uses_one_base() -> None:
    """The convention this task is preserving, asserted over the whole module."""
    offenders = {}
    for name, obj in vars(exc).items():
        if not inspect.isclass(obj) or not issubclass(obj, exc.AcfError):
            continue
        if obj is exc.AcfError:
            continue
        if obj.__bases__ != (exc.AcfError,):
            offenders[name] = obj.__bases__
    assert offenders == {}, f"exceptions with a second parent: {offenders}"
