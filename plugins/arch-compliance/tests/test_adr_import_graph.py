"""acf.adr is importable here, carries its public surface, and stays out of the hooks."""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
ADR = PLUGIN_ROOT / "python" / "acf" / "adr"

# The origin's ``__init__.__all__``, verbatim. The skill prose imports from this
# surface, so a dropped name fails only when a skill runs - which no test covers.
EXPECTED_SURFACE = {
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
}


def test_public_surface_is_complete() -> None:
    import acf.adr as adr

    missing = sorted(n for n in EXPECTED_SURFACE if not hasattr(adr, n))
    assert not missing, (
        f"acf.adr dropped these re-exports in the port: {missing}. The skill "
        "prose imports from this surface, so the failure would not appear here."
    )
    assert set(adr.__all__) == EXPECTED_SURFACE


def test_no_adr_module_imports_a_host() -> None:
    offenders = {}
    for path in sorted(ADR.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            mods: list[str] = []
            if isinstance(node, ast.ImportFrom):
                mods = [node.module or ""]
            elif isinstance(node, ast.Import):
                mods = [alias.name for alias in node.names]
            for mod in mods:
                if mod.split(".")[0] == "scripts":
                    offenders.setdefault(path.name, []).append(mod)
    assert offenders == {}, f"acf.adr still imports from a host: {offenders}"


def test_hooks_do_not_reach_acf_adr() -> None:
    """Both hooks import acf.repo at module scope, before any third party is
    available. acf.adr pulls in pydantic, so it must never enter that graph.
    """
    for hook in ("inject_constraints.py", "posttooluse_gate.py"):
        src = (PLUGIN_ROOT / "hooks" / hook).read_text(encoding="utf-8")
        assert "acf.adr" not in src, f"{hook} must not reference acf.adr"


def test_acf_repo_still_imports_without_pydantic(tmp_path) -> None:
    """The pre-gate import contract is unchanged by this package arriving."""
    import os

    poison = tmp_path / "poison"
    poison.mkdir()
    for name in ("pydantic.py", "yaml.py"):
        (poison / name).write_text("raise ImportError('poisoned')\n", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, "-c", "import acf.repo; print('ok')"],
        capture_output=True,
        text=True,
        env={
            **os.environ,
            "PYTHONPATH": os.pathsep.join(
                [str(poison), str(PLUGIN_ROOT / "python")]
            ),
            "PYTHONIOENCODING": "utf-8",
        },
    )
    assert proc.returncode == 0, proc.stderr
    assert "ok" in proc.stdout
