"""Bridge to the Node ts-morph TypeScript/React detector pack."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from acf.exceptions import DetectorPackError
from acf.finding import Finding, Severity
from acf.engine import posix_path, validate_hit_fields
from acf.repo import RepoTree

TS_MANDATE_IDS = {
    "empty_catch": "fail-loud.empty-catch",
    "explicit_any": "no-shims.explicit-any",
}

_PACK_ROOT = Path(__file__).resolve().parents[3] / "detectors" / "typescript"


_SHIM_SUFFIXES = frozenset({".cmd", ".bat"})


def _npm_ci_hint() -> str:
    return (
        f"Run: npm ci --prefix {_PACK_ROOT.as_posix()} "
        f"(or npm ci inside {_PACK_ROOT.as_posix()})"
    )


def _node_executable() -> str:
    node = shutil.which("node")
    if node is None:
        raise DetectorPackError(
            "Node.js executable 'node' not found on PATH; the TypeScript detector "
            "pack needs it to run its scanner"
        )
    if Path(node).suffix.lower() in _SHIM_SUFFIXES:
        raise DetectorPackError(
            f"'node' on PATH resolves to a batch shim ({node}); refusing to run the "
            "TypeScript scanner through cmd.exe. Put the real node executable on PATH"
        )
    return node


def _tsx_entry(pack: Path) -> Path:
    """The tsx JS entry point named by node_modules/tsx/package.json `bin`."""
    manifest = pack / "node_modules" / "tsx" / "package.json"
    if not manifest.is_file():
        raise DetectorPackError(
            "TypeScript detector dependency tsx is not installed "
            f"({manifest.as_posix()} missing). {_npm_ci_hint()}"
        )
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise DetectorPackError(
            f"Unreadable tsx manifest {manifest.as_posix()}: {exc}. {_npm_ci_hint()}"
        ) from exc
    bin_field = data.get("bin") if isinstance(data, dict) else None
    if isinstance(bin_field, dict):
        bin_field = bin_field.get("tsx")
    if not isinstance(bin_field, str) or not bin_field.strip():
        raise DetectorPackError(
            f"tsx manifest {manifest.as_posix()} names no 'bin' entry for tsx; "
            f"cannot locate the tsx entry point. {_npm_ci_hint()}"
        )
    # RepoTree is the one owner of path containment: the entry must resolve
    # inside the tsx package, so a manifest cannot point node at a file elsewhere.
    entry = RepoTree(manifest.parent).contained(bin_field)
    if entry is None:
        raise DetectorPackError(
            f"tsx 'bin' entry {bin_field!r} in {manifest.as_posix()} resolves outside "
            f"the tsx package; refusing to run it. {_npm_ci_hint()}"
        )
    if entry.suffix.lower() in _SHIM_SUFFIXES:
        raise DetectorPackError(
            f"tsx 'bin' entry {entry.as_posix()} is a batch shim; refusing to run it"
        )
    if not entry.is_file():
        raise DetectorPackError(
            f"tsx entry point {entry.as_posix()} named by {manifest.as_posix()} is "
            f"missing. {_npm_ci_hint()}"
        )
    return entry


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
    if not (_PACK_ROOT / "node_modules").is_dir():
        raise DetectorPackError(
            f"TypeScript detector dependencies are not installed. {_npm_ci_hint()}"
        )

    # Never a shell and never a .cmd/.bat shim: on Windows CreateProcess runs a
    # batch file through cmd.exe, which would re-parse the repository-controlled
    # file path (issue #34). Run the real node executable on tsx's JS entry.
    cmd = [
        _node_executable(),
        str(_tsx_entry(_PACK_ROOT)),
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
            line, message = validate_hit_fields(item["line"], item["message"])
            findings.append(
                Finding(
                    mandate_id=TS_MANDATE_IDS[item["detector"]],
                    severity=Severity(item["severity"]),
                    path=posix_path(item["path"]),
                    line=line,
                    message=message,
                    detector=item["detector"],
                    detection="ast",
                )
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise DetectorPackError(f"Invalid finding from TypeScript scanner: {exc}") from exc

    return findings
