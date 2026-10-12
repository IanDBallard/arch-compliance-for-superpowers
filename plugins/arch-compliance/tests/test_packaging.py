"""Non-Python files that acf code reads at runtime must survive a wheel build.

The editable install CI uses resolves ``Path(__file__)``-relative reads from the
source tree, so a missing ``package-data`` declaration is invisible to every
other test in this suite. This builds a real wheel and looks inside it.
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
ACF_PKG = REPO_ROOT / "plugins" / "arch-compliance" / "python" / "acf"


def _tracked_data_files() -> list[str]:
    """Tracked non-.py files under the acf package, as acf-relative posix paths."""
    out = subprocess.run(
        ["git", "ls-files", "plugins/arch-compliance/python/acf"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    rel = []
    for line in out.splitlines():
        if not line or line.endswith(".py"):
            continue
        rel.append(Path(line).relative_to("plugins/arch-compliance/python/acf").as_posix())
    return rel


def test_acf_data_files_ship_in_a_wheel(tmp_path: Path) -> None:
    """Every tracked non-.py file under acf/ is present in a built wheel.

    Derived from the tree rather than a hardcoded list, so a template added
    later is covered without touching this test.
    """
    expected = _tracked_data_files()
    assert expected, "no non-.py files tracked under acf/ - has the layout changed?"

    # Copy the tracked WORKING TREE, not `git archive HEAD`: a packaging change
    # must be verifiable before it is committed, or the test lags a commit
    # behind the thing it checks.
    src = tmp_path / "src"
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout.splitlines()
    for rel in tracked:
        if not rel:
            continue
        source = REPO_ROOT / rel
        if not source.is_file():      # a submodule or a deleted-but-tracked path
            continue
        dest = src / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)

    proc = subprocess.run(
        [
            sys.executable, "-m", "pip", "wheel",
            "--no-deps", "--no-build-isolation",
            "-w", str(tmp_path / "dist"), ".",
        ],
        cwd=src,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    if proc.returncode != 0:
        pytest.fail(
            "wheel build failed, so packaging could not be verified:\n"
            f"{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}"
        )

    wheels = glob.glob(str(tmp_path / "dist" / "*.whl"))
    assert wheels, "pip wheel reported success but produced no wheel"
    members = set(zipfile.ZipFile(wheels[0]).namelist())

    missing = [name for name in expected if f"acf/{name}" not in members]
    assert not missing, (
        "these files are read by acf code at runtime but are absent from the "
        f"wheel: {missing}. Declare them under [tool.setuptools.package-data] "
        "in pyproject.toml. An editable install hides this."
    )
