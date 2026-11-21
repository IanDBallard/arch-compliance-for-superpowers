"""/acf-setup step 8 prints the check-diff action and a guarded pre-push command that behaves as written."""

import os
import re
import shutil
import subprocess
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "plugins/arch-compliance/skills/acf-setup/SKILL.md"
SH = shutil.which("sh")  # resolved before PATH is emptied; dash on CI, Git Bash's sh on Windows


def _snippet() -> str:
    blocks = re.findall(r"```sh\n(.*?)```", SKILL.read_text(encoding="utf-8"), re.S)
    [snippet] = [b for b in blocks if "ACF_PREPUSH_OPTIONAL" in b]
    return snippet


def _run_absent(optional: str | None) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if k != "ACF_PREPUSH_OPTIONAL"}
    env["PATH"] = "/nonexistent"  # acf-check-diff absent
    if optional is not None:
        env["ACF_PREPUSH_OPTIONAL"] = optional
    return subprocess.run([SH, "-c", _snippet()], env=env, capture_output=True,
                          text=True, encoding="utf-8")


def test_absent_unset_refuses():
    r = _run_absent(None)
    assert r.returncode == 1
    assert "ACF_PREPUSH_OPTIONAL=1" in r.stderr


def test_absent_optional_skips():
    r = _run_absent("1")
    assert r.returncode == 0
    assert "skipping" in r.stderr


def test_absent_other_value_refuses():
    assert _run_absent("yes").returncode == 1


def test_snippet_has_no_trusted_checkout():
    s = _snippet()
    assert "--trusted-checkout" not in s
    assert "--call-site precommit" in s
    assert "|| exit 1" in s


def test_workflow_uses_action_and_no_sketch():
    text = SKILL.read_text(encoding="utf-8")
    assert ".github/actions/check-diff@v" in text and "fetch-depth: 0" in text
    assert "stages: [pre-commit]" not in text
    assert "pre-commit/CI snippets" not in text
