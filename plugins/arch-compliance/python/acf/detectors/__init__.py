"""Built-in detector contracts."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType

from acf.detectors.build_artifacts import BUILD_ARTIFACT_DETECTOR_ID, BUILD_ARTIFACTS_MANDATE_ID
from acf.detectors.facade_sinks import FACADE_SINK_DETECTOR_ID, FACADE_SINK_MANDATE_ID
from acf.detectors.fail_loud_ratchet import (
    FAIL_LOUD_RATCHET_DETECTOR_ID,
    FAIL_LOUD_RATCHET_MANDATE_ID,
)
from acf.detectors.fsm_guard import FSM_GUARD_DETECTOR_ID, FSM_GUARD_MANDATE_ID
from acf.detectors.python_pack import (
    FAIL_LOUD_BARE_EXCEPT_DETECTOR_ID,
    FAIL_LOUD_BARE_EXCEPT_MANDATE_ID,
    NO_SHIMS_HASATTR_DETECTOR_ID,
    NO_SHIMS_HASATTR_MANDATE_ID,
    POSIX_PATHS_STR_DETECTOR_ID,
    POSIX_PATHS_STR_MANDATE_ID,
)
from acf.detectors.typescript_bridge import TS_MANDATE_IDS
from acf.registry import (
    DIFF_CALL_SITES,
    TIER1_CALL_SITES,
    BuiltinDetector,
    MandateRegistry,
    load_mandates,
)

KNOWN_DETECTORS: Mapping[str, BuiltinDetector] = MappingProxyType(
    {
        FAIL_LOUD_BARE_EXCEPT_DETECTOR_ID: BuiltinDetector(
            FAIL_LOUD_BARE_EXCEPT_MANDATE_ID, TIER1_CALL_SITES
        ),
        NO_SHIMS_HASATTR_DETECTOR_ID: BuiltinDetector(
            NO_SHIMS_HASATTR_MANDATE_ID, TIER1_CALL_SITES
        ),
        POSIX_PATHS_STR_DETECTOR_ID: BuiltinDetector(
            POSIX_PATHS_STR_MANDATE_ID, TIER1_CALL_SITES
        ),
        **{
            detector_id: BuiltinDetector(mandate_id, TIER1_CALL_SITES)
            for detector_id, mandate_id in TS_MANDATE_IDS.items()
        },
        FACADE_SINK_DETECTOR_ID: BuiltinDetector(FACADE_SINK_MANDATE_ID, TIER1_CALL_SITES),
        FSM_GUARD_DETECTOR_ID: BuiltinDetector(FSM_GUARD_MANDATE_ID, TIER1_CALL_SITES),
        BUILD_ARTIFACT_DETECTOR_ID: BuiltinDetector(
            BUILD_ARTIFACTS_MANDATE_ID, TIER1_CALL_SITES
        ),
        FAIL_LOUD_RATCHET_DETECTOR_ID: BuiltinDetector(
            FAIL_LOUD_RATCHET_MANDATE_ID, DIFF_CALL_SITES
        ),
    }
)

def load_gate_registry(repo: Path, mandates_path: Path) -> MandateRegistry:
    """Load a registry the way every gate validates it (known detectors and prompt ids).

    ``acf.judge`` imports ``httpx``; it is imported here so that importing
    ``acf.detectors`` (the hook's path) stays free of it.
    """
    from acf.judge import LLM_PROMPT_IDS

    return load_mandates(
        mandates_path,
        known_detectors=KNOWN_DETECTORS,
        llm_prompt_ids=LLM_PROMPT_IDS,
        repo_root=repo,
    )


__all__ = ["KNOWN_DETECTORS", "load_gate_registry"]
