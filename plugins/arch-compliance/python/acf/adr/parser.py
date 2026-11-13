"""Reviewer payload parsing — the choke point for Architectural Contract 5.

A reviewer's final message body is exactly one fenced ```json block matching its
schema. Anything else raises ``ReviewerContractViolationError`` and aborts the run.
Unlike architecture-review, there is no per-reviewer FAILED status: silently
absorbing a malformed verdict is indistinguishable from a clean pass.
"""
from __future__ import annotations

import difflib

from pydantic import BaseModel, TypeAdapter, ValidationError

from acf.adr.contract import (
    CompliancePayload,
    HardeningPayload,
    RefuterPayload,
    ReviewerName,
    ReviewerPayload,
    SweeperPayload,
)
from acf.agent_payload import extract_json_block
from acf.exceptions import ReviewerContractViolationError

# Annotated as ``type[BaseModel]``: without it the inferred value type collapses
# to Pydantic's ``ModelMetaclass``, on which ``.model_fields`` (read below to
# build the key diff) does not resolve for mypy. The annotation is the fix — a
# ``type: ignore`` would suppress the report without giving the checker the
# model surface it needs.
_PAYLOAD_CLASSES: dict[str, type[BaseModel]] = {
    "refuter": RefuterPayload,
    "compliance": CompliancePayload,
    "sweeper": SweeperPayload,
    "hardening": HardeningPayload,
}

_ADAPTER: TypeAdapter = TypeAdapter(ReviewerPayload)


def parse_reviewer_payload(payload: str, expected_reviewer: ReviewerName) -> ReviewerPayload:
    """Extract and validate the single JSON block from a reviewer's final message.

    ``expected_reviewer`` is the identity the controller dispatched. A payload
    claiming a different identity is a violation — a reviewer that answered as
    someone else did not receive its own claim subset.

    Raises ``ReviewerContractViolationError`` on: no fenced json block, more than
    one, JSON parse failure, schema violation, or reviewer-identity mismatch.
    """
    data = extract_json_block(
        payload, subject=expected_reviewer, error=ReviewerContractViolationError
    )

    if isinstance(data, dict) and data.get("reviewer") != expected_reviewer:
        raise ReviewerContractViolationError(
            f"payload claims reviewer {data.get('reviewer')!r} but was dispatched as "
            f"{expected_reviewer!r}; a reviewer answering as another did not receive "
            "its own claim subset."
        )

    try:
        return _ADAPTER.validate_python(data)
    except ValidationError as e:
        expected_cls = _PAYLOAD_CLASSES[expected_reviewer]
        expected_keys = sorted(expected_cls.model_fields.keys())
        actual_keys = sorted(data.keys()) if isinstance(data, dict) else []
        diff = "\n".join(difflib.unified_diff(
            [f"{k}\n" for k in expected_keys],
            [f"{k}\n" for k in actual_keys],
            fromfile=f"expected ({expected_cls.__name__})",
            tofile=f"actual ({expected_reviewer} payload)",
            lineterm="",
        ))
        message = (
            f"{expected_reviewer} payload failed schema validation.\n"
            f"Validation errors (Pydantic):\n{e}\nKey diff:\n{diff}"
        )
        if "POSIX" in str(e) or "backslashes" in str(e):
            message += "\nHint: every path field must be POSIX (no backslashes)."
        raise ReviewerContractViolationError(message) from e
