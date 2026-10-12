"""The gate's package names no origin host: no doctrine, section numbers, paths or data."""
from __future__ import annotations

import re
from pathlib import Path

ADR = Path(__file__).resolve().parents[1] / "python" / "acf" / "adr"
HOST = re.compile(r"GEMINI|§\d|scripts/|scripts\.core|HistoricMansions|book[ _]|book_order")


def test_no_module_in_acf_adr_names_the_origin_host():
    offenders = [
        f"{path.name}:{n}: {line.strip()}"
        for path in sorted(ADR.glob("*.py"))
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        if HOST.search(line)
    ]
    assert offenders == [], "\n".join(offenders)


def test_runtime_messages_name_no_host_section():
    parser = (ADR / "parser.py").read_text(encoding="utf-8")
    gate = (ADR / "gate.py").read_text(encoding="utf-8")
    assert "every path field must be POSIX (no backslashes)." in parser
    assert "presumptively papering over the crack\"" in gate
