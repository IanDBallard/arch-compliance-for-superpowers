"""Extraction of the single fenced JSON block an agent's final message must carry.

Reviewers and auditors both answer with exactly one ```json block. This is the one
implementation of that rule; each caller names the subject in its own vocabulary
and the exception class its contract raises.
"""
from __future__ import annotations

import json
import re
from typing import Any

from acf.exceptions import AcfError

_JSON_FENCE_RE = re.compile(r"```json\s*\n(?P<body>.*?)\n```", re.DOTALL)


def extract_json_block(payload: str, *, subject: str, error: type[AcfError]) -> Any:
    """Return the decoded JSON of the one fenced block in ``payload``.

    Raises ``error`` on: no fenced json block, more than one, or JSON parse failure.
    """
    matches = list(_JSON_FENCE_RE.finditer(payload))
    if not matches:
        raise error(
            f"{subject} payload contains no ```json fenced block.\n"
            f"--- raw payload (first 500 chars) ---\n{payload[:500]}"
        )
    if len(matches) > 1:
        raise error(
            f"{subject} payload contains multiple ({len(matches)}) "
            "```json blocks; expected exactly one."
        )
    raw = matches[0].group("body")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise error(
            f"{subject} JSON parse failed: {e}\n--- raw block ---\n{raw}"
        ) from e
