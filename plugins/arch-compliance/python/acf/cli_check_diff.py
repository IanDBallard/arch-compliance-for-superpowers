"""CLI: diff-scoped architecture compliance check."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from acf.diff import DiffMode, added_lines, changed_files
from acf.detectors.python_pack import PYTHON_DETECTOR_IDS, scan_python_file
from acf.detectors.typescript_bridge import TS_DETECTOR_IDS, scan_typescript_file
from acf.enforcement import apply_registry
from acf.finding import Finding, Severity
from acf.judge import LLM_PROMPT_IDS
from acf.registry import load_mandates

KNOWN_DETECTORS = PYTHON_DETECTOR_IDS | TS_DETECTOR_IDS | LLM_PROMPT_IDS


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="acf-check-diff")
    parser.add_argument(
        "--mode",
        choices=("staged", "worktree"),
        default="staged",
        help="Git diff scope (default: staged)",
    )
    parser.add_argument(
        "--base",
        default=None,
        help=(
            "Diff against merge-base of <ref> and HEAD (git three-dot). "
            "Overrides --mode; use in CI, e.g. --base origin/main"
        ),
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

    registry = load_mandates(mandates_path, known_detectors=KNOWN_DETECTORS)

    raw_findings, file_lines = _scan_changed(repo, mode, args.base)

    def _line_lookup(posix: str, line: int) -> str:
        lines = file_lines.get(posix)
        if not lines or not (0 < line <= len(lines)):
            return ""
        return lines[line - 1]

    findings = apply_registry(raw_findings, registry, _line_lookup)

    if args.json:
        print(json.dumps([f.model_dump(mode="json") for f in findings], indent=2))
    else:
        _print_human(findings)

    if any(f.severity == Severity.BLOCK for f in findings):
        return 1
    return 0


def _scan_changed(
    repo: Path, mode: DiffMode, base: str | None = None
) -> tuple[list[Finding], dict[str, list[str]]]:
    findings: list[Finding] = []
    file_lines: dict[str, list[str]] = {}
    for rel in changed_files(repo, mode, base=base):
        path = Path(rel)
        suffix = path.suffix.lower()
        abs_path = repo / path
        lines = frozenset(added_lines(repo, rel, mode, base=base))

        if suffix == ".py":
            text = abs_path.read_text(encoding="utf-8")
            file_lines[path.as_posix()] = text.splitlines()
            findings.extend(scan_python_file(text, path.as_posix(), added_lines=lines))
        elif suffix in {".ts", ".tsx"}:
            file_lines[path.as_posix()] = abs_path.read_text(
                encoding="utf-8"
            ).splitlines()
            findings.extend(
                f.model_copy(update={"path": path.as_posix()})
                for f in scan_typescript_file(abs_path, added_lines=lines)
            )
    return findings, file_lines


def _print_human(findings: list[Finding]) -> None:
    if not findings:
        print("No findings.")
        return
    for f in findings:
        print(f"{f.severity.value} {f.mandate_id} {f.path}:{f.line} {f.message}")


if __name__ == "__main__":
    sys.exit(main())
