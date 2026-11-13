from __future__ import annotations
import re
from acf.exceptions import AcfInputError
from acf.registry import anchor_line

_HEADING = re.compile(r"^(#+) ")


def _level(line: str) -> int | None:
    match = _HEADING.match(line)
    return len(match.group(1)) if match else None


def doctrine_section(doctrine_text: str, anchor: str, *, mandate_id: str) -> str:
    """The doctrine lines from the anchor to the next heading of the same or higher level."""
    start = anchor_line(doctrine_text, anchor)
    if start is None:
        raise AcfInputError(
            f"mandate {mandate_id!r}: arch_anchor {anchor!r} matches no doctrine line"
        )
    lines = doctrine_text.splitlines()
    # A non-heading anchor has no level, so any heading ends it.
    anchor_level = _level(lines[start]) or 99
    end = len(lines)
    for index in range(start + 1, len(lines)):
        level = _level(lines[index])
        if level is not None and level <= anchor_level:
            end = index
            break
    return "\n".join(lines[start:end]).rstrip()
