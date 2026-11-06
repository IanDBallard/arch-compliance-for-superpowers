"""Guard: forbid committing / staging paths under build-output prefixes."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from acf.engine import posix_path
from acf.finding import Finding, Severity

BUILD_ARTIFACT_DETECTOR_ID = "no_build_artifacts"
BUILD_ARTIFACTS_MANDATE_ID = "ops.no-build-artifacts"


def build_artifact_args(params: Mapping[str, Any]) -> dict[str, Any]:
    """Scanner kwargs for a row's params; ``path_prefixes`` only when present and non-empty."""
    prefixes = params.get("path_prefixes")
    return {"path_prefixes": prefixes} if prefixes else {}


def scan_build_artifact_paths(
    changed_paths: Sequence[str],
    *,
    path_prefixes: Iterable[str] | None = None,
) -> list[Finding]:
    """Emit one finding per changed path under a forbidden prefix.

    Default prefixes: ``dist/``, ``build/``. Prefixes are matched on POSIX
    relative paths (case-sensitive).
    """
    prefixes = [p.replace("\\", "/") for p in (path_prefixes or ("dist/", "build/"))]
    prefixes = [p if p.endswith("/") else f"{p}/" for p in prefixes]
    findings: list[Finding] = []
    for raw in changed_paths:
        rel = posix_path(raw).lstrip("./")
        if any(rel == p.rstrip("/") or rel.startswith(p) for p in prefixes):
            findings.append(
                Finding(
                    mandate_id=BUILD_ARTIFACTS_MANDATE_ID,
                    severity=Severity.BLOCK,
                    path=rel,
                    line=1,
                    message=(
                        f"Build output path must not be tracked/staged "
                        f"(matched prefixes: {', '.join(prefixes)})"
                    ),
                    detector=BUILD_ARTIFACT_DETECTOR_ID,
                    detection="guard",
                )
            )
    return findings
