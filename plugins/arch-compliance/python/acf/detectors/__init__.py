"""Built-in detector contracts."""

from __future__ import annotations

from collections.abc import Mapping
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
from acf.registry import DIFF_CALL_SITES, TIER1_CALL_SITES, BuiltinDetector

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
        "empty_catch": BuiltinDetector(TS_MANDATE_IDS["empty_catch"], TIER1_CALL_SITES),
        "explicit_any": BuiltinDetector(TS_MANDATE_IDS["explicit_any"], TIER1_CALL_SITES),
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

__all__ = ["KNOWN_DETECTORS"]
