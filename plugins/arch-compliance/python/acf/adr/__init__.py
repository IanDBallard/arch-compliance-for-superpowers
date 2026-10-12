"""Python helpers for the adversarial-design-review skill.

The skill's judgment lives in its Markdown prompts. This package owns only the
mechanical parts: schemas, a strict payload parser, deterministic convergence
grouping, the gate truth table, the roll-up formatter, and the efficacy ledger.
"""
from acf.adr.contract import (
    Claim,
    ClaimVerdict,
    ConvergedFinding,
    DesignReviewRun,
    GateResult,
    ReviewerPayload,
    UnanchoredFinding,
)
from acf.adr.convergence import group_convergence_candidates
from acf.adr.gate import classify_outcome
from acf.adr.ledger import (
    LEDGER_PATH,
    LedgerAmendment,
    LedgerRow,
    append_amendment,
    append_row,
)
from acf.adr.parser import parse_reviewer_payload
from acf.adr.rollup import format_rollup

from acf.adr.citations import (
    classify_citation,
    classify_citations,
    count_cited_files,
    resolve_citation,
    unresolved_citations,
)
from acf.adr.run_detail import (
    RUNS_DIR,
    render_run_detail,
    run_detail_path,
    write_run_detail,
)

__all__ = [
    "Claim",
    "ClaimVerdict",
    "ConvergedFinding",
    "DesignReviewRun",
    "GateResult",
    "LEDGER_PATH",
    "LedgerAmendment",
    "LedgerRow",
    "RUNS_DIR",
    "ReviewerPayload",
    "UnanchoredFinding",
    "append_amendment",
    "append_row",
    "classify_citation",
    "classify_citations",
    "classify_outcome",
    "count_cited_files",
    "format_rollup",
    "group_convergence_candidates",
    "parse_reviewer_payload",
    "render_run_detail",
    "resolve_citation",
    "run_detail_path",
    "unresolved_citations",
    "write_run_detail",
]
