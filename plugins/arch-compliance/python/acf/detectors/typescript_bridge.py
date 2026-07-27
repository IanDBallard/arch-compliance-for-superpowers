"""Bridge to the Node ts-morph TypeScript/React detector pack."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from acf.exceptions import DetectorPackError
from acf.finding import Finding, Severity
from acf.engine import posix_path

TS_DETECTOR_IDS = frozenset({"empty_catch", "explicit_any"})

_PACK_ROOT = Path(__file__).resolve().parents[3] / "detectors" / "typescript"


def scan_typescript_file(
    path: str | Path,
    added_lines: frozenset[int] | None = None,
) -> list[Finding]:
    """Run the Node scanner and return Finding objects.

    Raises DetectorPackError on non-zero exit or invalid JSON.
    """
    file_path = Path(path).resolve()
    if not _PACK_ROOT.is_dir():
        raise DetectorPackError(f"TypeScript detector pack not found: {_PACK_ROOT}")

    cmd = [
        "npx",
        "--no-install",
        "tsx",
        "src/scan.ts",
        "--file",
        str(file_path),
    ]
    if added_lines:
        cmd.extend(["--lines", ",".join(str(n) for n in sorted(added_lines))])

    try:
        proc = subprocess.run(
            cmd,
            cwd=_PACK_ROOT,
            capture_output=True,
            text=True,
            check=False,
            shell=sys.platform == "win32",
        )
    except OSError as exc:
        raise DetectorPackError(f"Failed to invoke TypeScript scanner: {exc}") from exc

    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        raise DetectorPackError(
            f"TypeScript scanner exited {proc.returncode}: {err or '(no output)'}"
        )

    raw = (proc.stdout or "").strip()
    if not raw:
        return []

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise DetectorPackError(f"TypeScript scanner returned invalid JSON: {exc}") from exc

    if not isinstance(data, list):
        raise DetectorPackError("TypeScript scanner JSON must be an array")

    findings: list[Finding] = []
    for item in data:
        if not isinstance(item, dict):
            raise DetectorPackError("TypeScript scanner finding must be an object")
        try:
            findings.append(
                Finding(
                    mandate_id=item["mandate_id"],
                    severity=Severity(item["severity"]),
                    path=posix_path(item["path"]),
                    line=int(item["line"]),
                    message=str(item["message"]),
                    detector=str(item["detector"]),
                    detection="ast",
                )
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise DetectorPackError(f"Invalid finding from TypeScript scanner: {exc}") from exc

    return findings
