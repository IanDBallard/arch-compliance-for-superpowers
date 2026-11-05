"""The /acf-mandate validation snippet runs as written against a host built from a
stock profile: it loads the registry with the built-in detector contracts and LLM prompt ids and refuses
a row whose arch_anchor is missing from the doctrine."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SKILL = PLUGIN_ROOT / "skills" / "acf-mandate" / "SKILL.md"
PROFILE = PLUGIN_ROOT / "profiles" / "python-service"


def _snippet() -> str:
    text = SKILL.read_text(encoding="utf-8")
    section = text.split("## Validate", 1)[1]
    match = re.search(r'```bash\npython -c "\n(.*?)\n"\n```', section, re.S)
    assert match, "the Validate section carries one python -c snippet"
    return match.group(1)


def _host(tmp_path: Path) -> Path:
    cfg = tmp_path / "host" / "config" / "architecture"
    cfg.mkdir(parents=True)
    shutil.copyfile(PROFILE / "mandates.yml", cfg / "mandates.yml")
    shutil.copyfile(PROFILE / "ARCHITECTURE.md", cfg / "ARCHITECTURE.md")
    return tmp_path / "host"


def _run(host: Path) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONPATH": str(PLUGIN_ROOT / "python"), "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        [sys.executable, "-c", _snippet()],
        cwd=host, env=env, capture_output=True, text=True, encoding="utf-8",
    )


def test_snippet_accepts_a_stock_profile_with_guard_rows(tmp_path):
    proc = _run(_host(tmp_path))
    assert proc.returncode == 0, proc.stderr
    assert "OK:" in proc.stdout


@pytest.mark.parametrize("anchor", ["## Fail loud"])
def test_snippet_refuses_a_missing_anchor(tmp_path, anchor):
    host = _host(tmp_path)
    doctrine = host / "config" / "architecture" / "ARCHITECTURE.md"
    doctrine.write_text(
        doctrine.read_text(encoding="utf-8").replace(anchor, "## Renamed"), encoding="utf-8"
    )
    proc = _run(host)
    assert proc.returncode != 0
    assert "fail-loud.bare-except" in proc.stderr + proc.stdout
