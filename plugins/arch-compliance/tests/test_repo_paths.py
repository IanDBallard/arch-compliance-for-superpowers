"""The host config directory is declared once, and the hooks stay import-light."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
PYTHON_ROOT = PLUGIN_ROOT / "python"
HOOKS = PLUGIN_ROOT / "hooks"

# Matches both spellings: the string literal and the Path-segment form.
CONFIG_ARCH_RE = re.compile(r"config.{0,6}architecture")


def _tracked_py_files() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "python", "hooks"],
        cwd=PLUGIN_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [PLUGIN_ROOT / line for line in out.splitlines() if line.endswith(".py")]


# Sites that may name the host config directory for a human to read. Each
# entry is a disposition, not a blanket exemption: a NEW line in one of these
# files still fails, because the allowlist is keyed by exact text.
ALLOWED_DOC_LINES = {
    # argparse help: tells an operator what the default is. A constant name
    # would be useless to someone reading --help.
    "python/acf/cli_check_diff.py": {
        'help="Path to mandates.yml (default: <repo>/config/architecture/mandates.yml)",'
    },
    "python/acf/cli_check_llm.py": {
        'help="Path to mandates.yml (default: config/architecture/mandates.yml under cwd)",'
    },
    # Module docstrings describing the hook's own contract.
    "hooks/inject_constraints.py": {
        "- If enabled and ``config/architecture/mandates.yml`` is missing: non-zero exit."
    },
    "hooks/posttooluse_gate.py": {
        "- If enabled and ``config/architecture/mandates.yml`` is missing: non-zero exit."
    },
}


def test_host_config_dir_has_one_code_owner() -> None:
    """Every executable spelling lives in acf/repo.py; prose is allowlisted."""
    offenders: dict[str, list[str]] = {}
    for path in _tracked_py_files():
        if path.name == "repo.py":
            continue
        rel = path.relative_to(PLUGIN_ROOT).as_posix()
        allowed = ALLOWED_DOC_LINES.get(rel, set())
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if not CONFIG_ARCH_RE.search(stripped):
                continue
            if stripped.startswith("#") or stripped in allowed:
                continue
            offenders.setdefault(rel, []).append(f"{lineno}: {stripped}")
    assert offenders == {}, (
        "the host config directory is spelled outside acf/repo.py. Either route "
        f"it through a repo.py constant or add it to ALLOWED_DOC_LINES: {offenders}"
    )


def test_repo_module_imports_only_stdlib() -> None:
    source = (PYTHON_ROOT / "acf" / "repo.py").read_text(encoding="utf-8")
    imports = re.findall(r"^\s*(?:from|import)\s+([A-Za-z_][\w.]*)", source, re.M)
    allowed = {"__future__", "pathlib"}
    assert set(imports) <= allowed, f"acf.repo must stay stdlib-only, got {imports}"


def test_hooks_import_repo_without_pulling_third_party(tmp_path) -> None:
    """A marker-less host must still exit 0 with pydantic and yaml poisoned.

    The poison modules go in tmp_path, never inside the repository: a file
    named pydantic.py under tests/ would shadow the real package for any other
    run that happens to put tests/ on sys.path.
    """
    import os

    poison = tmp_path / "poison"
    poison.mkdir()
    for name in ("pydantic.py", "yaml.py"):
        (poison / name).write_text("raise ImportError('poisoned')\n", encoding="utf-8")

    host = tmp_path / "host"          # no .acf/enabled -> both hooks no-op
    host.mkdir()

    env = {**os.environ, "PYTHONPATH": str(poison), "PYTHONIOENCODING": "utf-8"}
    for hook in ("inject_constraints.py", "posttooluse_gate.py"):
        proc = subprocess.run(
            [sys.executable, str(HOOKS / hook), "--repo", str(host)],
            capture_output=True,
            text=True,
            env=env,
            input="",
        )
        assert proc.returncode == 0, f"{hook} exited {proc.returncode}: {proc.stderr}"
        assert "Traceback" not in proc.stderr, f"{hook} raised: {proc.stderr}"
