"""CLI: diff-scoped architecture compliance check."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from acf.detectors import ALL_PYTHON_DETECTOR_IDS
from acf.detectors.build_artifacts import BUILD_ARTIFACT_DETECTOR_ID, scan_build_artifact_paths
from acf.detectors.facade_sinks import FACADE_SINK_DETECTOR_ID, scan_facade_sinks
from acf.detectors.fail_loud_ratchet import FAIL_LOUD_RATCHET_DETECTOR_ID, scan_ratchet
from acf.detectors.fsm_guard import FSM_GUARD_DETECTOR_ID, scan_fsm_writes
from acf.detectors.python_pack import scan_python_file
from acf.detectors.typescript_bridge import TS_DETECTOR_IDS, scan_typescript_file
from acf.diff import DiffMode, added_lines, changed_files
from acf.enforcement import apply_registry
from acf.exceptions import DetectorPackError, GitError, RegistryLoadError, UnknownDetectorError
from acf.finding import Finding, Severity
from acf.judge import LLM_PROMPT_IDS
from acf.registry import Mandate, MandateRegistry, load_mandates

KNOWN_DETECTORS = ALL_PYTHON_DETECTOR_IDS | TS_DETECTOR_IDS | LLM_PROMPT_IDS


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

    try:
        registry = load_mandates(mandates_path, known_detectors=KNOWN_DETECTORS)
        raw_findings, file_lines = _scan_changed(repo, mode, args.base, registry)
    except (GitError, RegistryLoadError, UnknownDetectorError, DetectorPackError) as exc:
        print(f"acf: {exc}", file=sys.stderr)
        return 1

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


def _active_mandates(registry: MandateRegistry, detector: str) -> list[Mandate]:
    return [
        m
        for m in registry.mandates
        if m.detector == detector and m.status != "unenforced"
    ]


def _scan_changed(
    repo: Path,
    mode: DiffMode,
    base: str | None,
    registry: MandateRegistry,
) -> tuple[list[Finding], dict[str, list[str]]]:
    findings: list[Finding] = []
    file_lines: dict[str, list[str]] = {}
    changed = changed_files(repo, mode, base=base)

    facade_specs = _active_mandates(registry, FACADE_SINK_DETECTOR_ID)
    fsm_specs = _active_mandates(registry, FSM_GUARD_DETECTOR_ID)

    for rel in changed:
        path = Path(rel)
        suffix = path.suffix.lower()
        abs_path = repo / path
        if not abs_path.is_file():
            continue
        lines = frozenset(added_lines(repo, rel, mode, base=base))
        posix = path.as_posix()

        if suffix == ".py":
            text = abs_path.read_text(encoding="utf-8")
            file_lines[posix] = text.splitlines()
            findings.extend(scan_python_file(text, posix, added_lines=lines))
            for mandate in facade_specs:
                params = mandate.params or {}
                findings.extend(
                    scan_facade_sinks(
                        text,
                        posix,
                        lines,
                        target_literal_re=str(params.get("target_literal_re", "")),
                        allowlist_globs=list(params.get("allowlist_globs") or []),
                        atomic_is_sink=bool(params.get("atomic_is_sink", True)),
                    )
                )
            for mandate in fsm_specs:
                params = mandate.params or {}
                findings.extend(
                    scan_fsm_writes(
                        text,
                        posix,
                        lines,
                        state_field=str(params.get("state_field", "")),
                        validator_name=str(params.get("validator_name", "")),
                    )
                )
        elif suffix in {".ts", ".tsx"}:
            file_lines[posix] = abs_path.read_text(encoding="utf-8").splitlines()
            findings.extend(
                f.model_copy(update={"path": posix})
                for f in scan_typescript_file(abs_path, added_lines=lines)
            )

    for mandate in _active_mandates(registry, BUILD_ARTIFACT_DETECTOR_ID):
        params = mandate.params or {}
        prefixes = params.get("path_prefixes")
        findings.extend(
            scan_build_artifact_paths(
                changed,
                path_prefixes=list(prefixes) if prefixes else None,
            )
        )

    for mandate in _active_mandates(registry, FAIL_LOUD_RATCHET_DETECTOR_ID):
        params = mandate.params or {}
        baseline = params.get("baseline", "config/architecture/fail_loud_ratchet.json")
        findings.extend(
            scan_ratchet(
                repo,
                baseline_path=str(baseline),
                roots=list(params["roots"]) if params.get("roots") else None,
                exclude_globs=(
                    list(params["exclude_globs"])
                    if params.get("exclude_globs")
                    else None
                ),
            )
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
