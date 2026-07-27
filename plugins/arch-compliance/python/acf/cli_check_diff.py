"""CLI: diff-scoped architecture compliance check."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from acf.diff import DiffMode, added_lines, changed_files
from acf.detectors.python_pack import scan_python_file
from acf.detectors.typescript_bridge import scan_typescript_file
from acf.finding import Finding, Severity
from acf.registry import load_mandates


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="acf-check-diff")
    parser.add_argument(
        "--mode",
        choices=("staged", "worktree"),
        default="staged",
        help="Git diff scope (default: staged)",
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=None,
        help="Repository root (default: cwd)",
    )
    parser.add_argument(
        "--mandates",
        type=Path,
        default=None,
        help="Path to mandates.yml (default: <repo>/config/architecture/mandates.yml)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit findings as JSON",
    )
    args = parser.parse_args(argv)

    repo: Path = (args.repo or Path.cwd()).resolve()
    mode: DiffMode = args.mode  # type: ignore[assignment]
    mandates_path: Path = (
        args.mandates.resolve()
        if args.mandates is not None
        else repo / "config" / "architecture" / "mandates.yml"
    )

    load_mandates(mandates_path)

    findings = _scan_changed(repo, mode)

    if args.json:
        print(json.dumps([f.model_dump(mode="json") for f in findings], indent=2))
    else:
        _print_human(findings)

    if any(f.severity == Severity.BLOCK for f in findings):
        return 1
    return 0


def _scan_changed(repo: Path, mode: DiffMode) -> list[Finding]:
    findings: list[Finding] = []
    for rel in changed_files(repo, mode):
        path = Path(rel)
        suffix = path.suffix.lower()
        abs_path = repo / path
        lines = frozenset(added_lines(repo, rel, mode))

        if suffix == ".py":
            text = abs_path.read_text(encoding="utf-8")
            findings.extend(scan_python_file(text, path.as_posix(), added_lines=lines))
        elif suffix in {".ts", ".tsx"}:
            findings.extend(scan_typescript_file(abs_path, added_lines=lines))
    return findings


def _print_human(findings: list[Finding]) -> None:
    if not findings:
        print("No findings.")
        return
    for f in findings:
        print(f"{f.severity.value} {f.mandate_id} {f.path}:{f.line} {f.message}")


if __name__ == "__main__":
    sys.exit(main())
