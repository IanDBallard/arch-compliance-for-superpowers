"""Registry-driven enforcement layer.

Detectors report raw evidence; this layer makes the host's mandate registry
the source of truth for what actually gates:

- findings whose mandate is absent from the registry are dropped (not mandated
  by this host);
- findings whose mandate is ``status: unenforced`` are dropped;
- severity always comes from the registry row, not the detector default;
- the registry row's ``exemption_tokens`` are honored as inline comment
  exemptions (``#`` and ``//`` comment styles, reason required).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Sequence

from acf.finding import Finding, Severity
from acf.registry import MandateRegistry

# (posix_path, 1-based line) -> source line text ("" when unavailable)
LineLookup = Callable[[str, int], str]


def token_exempted(line: str, tokens: Iterable[str]) -> bool:
    """True if ``line`` carries a registry exemption token with a non-empty
    reason, in either ``# <token>: reason`` or ``// <token>: reason`` form."""
    for token in tokens:
        escaped = re.escape(token)
        m = re.search(rf"(?:#|//)\s*{escaped}\s*:\s*(\S.*)$", line)
        if m and m.group(1).strip():
            return True
    return False


def apply_registry(
    findings: Sequence[Finding],
    registry: MandateRegistry,
    line_lookup: LineLookup,
) -> list[Finding]:
    """Filter and normalize detector findings against the host registry."""
    by_id = registry.by_id
    kept: list[Finding] = []
    for finding in findings:
        mandate = by_id.get(finding.mandate_id)
        if mandate is None or mandate.status == "unenforced":
            continue
        source_line = line_lookup(finding.path, finding.line)
        if mandate.exemption_tokens and token_exempted(source_line, mandate.exemption_tokens):
            continue
        kept.append(finding.model_copy(update={"severity": Severity(mandate.severity)}))
    return kept
