"""The one placeholder substituter.

Tokens are literal ``{{UPPER_SNAKE}}`` runs in the template text, so the
required token set is derived from the text itself and needs no declaration
anywhere else. Substitution is single-pass: a value that happens to contain a
token is data, not template.

Refuses in both directions. ``str.replace`` is silent when a token has no value
(the literal token ships to the reader) and when a value has no token (the
caller believes it supplied something that was dropped).
"""
from __future__ import annotations

import re

from acf.exceptions import TemplateRenderError

_TOKEN_RE = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")


def required_tokens(text: str) -> set[str]:
    """The token names ``text`` consumes."""
    return set(_TOKEN_RE.findall(text))


def render_template(text: str, mapping: dict[str, str]) -> str:
    """Substitute every ``{{TOKEN}}`` in ``text`` from ``mapping``.

    Raises ``TemplateRenderError`` if the two sides disagree in either
    direction.
    """
    needed = required_tokens(text)
    supplied = set(mapping)
    missing = sorted(needed - supplied)
    unused = sorted(supplied - needed)
    if missing or unused:
        parts = []
        if missing:
            parts.append(f"no value for {', '.join(missing)}")
        if unused:
            parts.append(f"no token for {', '.join(unused)}")
        raise TemplateRenderError("; ".join(parts))
    return _TOKEN_RE.sub(lambda m: mapping[m.group(1)], text)
