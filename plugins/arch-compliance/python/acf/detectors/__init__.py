"""Portable detector id registries."""

from __future__ import annotations

from acf.detectors.build_artifacts import BUILD_ARTIFACT_DETECTOR_ID
from acf.detectors.facade_sinks import FACADE_SINK_DETECTOR_ID
from acf.detectors.fail_loud_ratchet import FAIL_LOUD_RATCHET_DETECTOR_ID
from acf.detectors.fsm_guard import FSM_GUARD_DETECTOR_ID
from acf.detectors.python_pack import PYTHON_AST_DETECTOR_IDS, PYTHON_DETECTOR_IDS

GUARD_DETECTOR_IDS = frozenset(
    {
        BUILD_ARTIFACT_DETECTOR_ID,
        FAIL_LOUD_RATCHET_DETECTOR_ID,
        FACADE_SINK_DETECTOR_ID,
        FSM_GUARD_DETECTOR_ID,
    }
)

# AST detectors that are config-driven (still detection: ast in registry).
CONFIG_AST_DETECTOR_IDS = frozenset(
    {
        FACADE_SINK_DETECTOR_ID,
        FSM_GUARD_DETECTOR_ID,
    }
)

ALL_PYTHON_DETECTOR_IDS = PYTHON_AST_DETECTOR_IDS | GUARD_DETECTOR_IDS

__all__ = [
    "ALL_PYTHON_DETECTOR_IDS",
    "CONFIG_AST_DETECTOR_IDS",
    "GUARD_DETECTOR_IDS",
    "PYTHON_AST_DETECTOR_IDS",
    "PYTHON_DETECTOR_IDS",
]
