"""Guard: forbid committing / staging paths under build-output prefixes."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from acf.engine import posix_path
from acf.finding import Finding, Severity

BUILD_ARTIFACT_DETECTOR_ID = "no_build_artifacts"


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
                    mandate_id="ops.no-build-artifacts",
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
