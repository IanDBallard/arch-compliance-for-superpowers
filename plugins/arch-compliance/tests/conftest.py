from __future__ import annotations

import sys
from pathlib import Path

import pytest

import acf.detectors.host as host


@pytest.fixture
def fresh_host_loader(monkeypatch):
    """Isolate the host loader's process state (root, sys.path, host modules) per test."""
    monkeypatch.setattr(host, "_ACTIVE_ROOT", None)
    path_before = list(sys.path)
    keys_before = set(sys.modules)
    try:
        yield host
    finally:
        root = host._ACTIVE_ROOT
        sys.path[:] = path_before
        for key in set(sys.modules) - keys_before:
            mod_file = getattr(sys.modules.get(key), "__file__", None)
            under_root = (
                root is not None
                and isinstance(mod_file, str)
                and root in Path(mod_file).resolve().parents
            )
            if key.startswith("_acf_host_") or under_root:
                sys.modules.pop(key, None)
