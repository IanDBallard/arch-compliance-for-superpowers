"""CLI: LLM judge over a unified diff (Tier 2)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from acf.finding import Severity
from acf.judge import run_judge
from acf.registry import load_mandates


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="acf-check-llm")
    parser.add_argument(
        "--diff-file",
        type=Path,
        default=None,
        help="Unified diff file (default: read stdin)",
    )
    parser.add_argument(
        "--mandates",
        type=Path,
        default=None,
        help="Path to mandates.yml (default: config/architecture/mandates.yml under cwd)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit findings as JSON",
    )
    args = parser.parse_args(argv)

    mandates_path: Path = (
        args.mandates.resolve()
        if args.mandates is not None
        else Path.cwd() / "config" / "architecture" / "mandates.yml"
    )
    registry = load_mandates(mandates_path)

    if args.diff_file is not None:
        diff_text = args.diff_file.read_text(encoding="utf-8")
    else:
        diff_text = sys.stdin.read()

    findings = run_judge(diff_text, registry.mandates)

    if args.json:
        print(json.dumps([f.model_dump(mode="json") for f in findings], indent=2))
    else:
        _print_human(findings)

    if any(f.severity == Severity.BLOCK for f in findings):
        return 1
    return 0


def _print_human(findings: list) -> None:
    if not findings:
        print("No findings.")
        return
    for f in findings:
        loc = f"{f.path}:{f.line}"
        conf = f" [{f.confidence}]" if f.confidence else ""
        print(f"{f.severity.value} {f.mandate_id} {loc}{conf} {f.message}")


if __name__ == "__main__":
    sys.exit(main())
