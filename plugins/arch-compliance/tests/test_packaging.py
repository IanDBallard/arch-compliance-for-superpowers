"""Non-Python files that acf code reads at runtime must survive a wheel build.

The editable install used in development and CI resolves
``Path(__file__)``-relative reads from the source tree, so a missing
``package-data`` declaration is invisible to every other test in this suite.
This builds a real wheel and looks inside it.
"""
from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
ACF_REL = "plugins/arch-compliance/python/acf"

_NO_SETUPTOOLS_HINT = (
    "If the output below says \"Cannot import 'setuptools.build_meta'\", this "
    "environment has no setuptools. The dev extra declares it for exactly this "
    "test, because Python 3.12+ ships none by default. Install with: "
    'pip install -e ".[dev]"'
)


def _tracked_data_files() -> list[str]:
    """Tracked non-.py files under the acf package, as acf-relative posix paths."""
    out = subprocess.run(
        ["git", "ls-files", ACF_REL],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [
        Path(line).relative_to(ACF_REL).as_posix()
        for line in out.splitlines()
        if line and not line.endswith(".py")
    ]


def _copy_tracked_working_tree(dest: Path) -> None:
    """Copy the tracked WORKING TREE, not ``git archive HEAD``.

    A packaging change must be verifiable before it is committed, or this test
    lags one commit behind the thing it checks.
    """
    tracked = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    for rel in tracked:
        if not rel:
            continue
        source = REPO_ROOT / rel
        if not source.is_file():  # submodule, or tracked-but-deleted
            continue
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def test_acf_data_files_ship_in_a_wheel(tmp_path: Path) -> None:
    """Every tracked non-.py file under acf/ is present in a built wheel.

    Derived from the tree rather than a hardcoded list, so a template added
    later is covered without touching this test.
    """
    expected = _tracked_data_files()
    assert expected, "no non-.py files tracked under acf/ - has the layout changed?"

    src = tmp_path / "src"
    _copy_tracked_working_tree(src)

    dist = tmp_path / "dist"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            "--no-deps",
            "--no-build-isolation",
            "-w",
            str(dist),
            ".",
        ],
        cwd=src,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    if proc.returncode != 0:
        pytest.fail(
            "wheel build failed, so packaging could not be verified. "
            f"{_NO_SETUPTOOLS_HINT}\n"
            f"{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}"
        )

    wheels = glob.glob(str(dist / "*.whl"))
    assert wheels, "pip wheel reported success but produced no wheel"
    members = set(zipfile.ZipFile(wheels[0]).namelist())

    missing = [name for name in expected if f"acf/{name}" not in members]
    assert not missing, (
        "these files are read by acf code at runtime but are absent from the "
        f"wheel: {missing}. Declare them under [tool.setuptools.package-data] "
        "in pyproject.toml. An editable install hides this."
    )
