"""Build a throwaway host repository for the check-diff action's CI test.

Test scaffolding, not a test module: pytest does not collect it (no ``test_`` prefix).
Run with ``PYTHONPATH=plugins/arch-compliance/python`` so ``acf.repo`` imports without
an install:

    python tests/action_fixture_host.py <dest> --plant {empty-catch,clean}

The repository gets a ``main`` branch holding one mandate row and a TypeScript file,
and a checked-out ``feature`` branch with one commit on top that either plants an
empty ``catch {}`` or adds clean code.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Literal

from acf.repo import ARCH_REL, MANDATES_REL

Plant = Literal["empty-catch", "clean"]

_GIT_ID = ["-c", "user.name=ci", "-c", "user.email=ci@example.invalid", "-c", "commit.gpgsign=false"]

_MANDATES = """\
- id: fail-loud.empty-catch
  title: Empty catch blocks must not swallow errors
  severity: BLOCK
  detection: ast
  detector: empty_catch
  languages: typescript
  call_sites: [ci]
  exemption_tokens: []
  status: enforced
  arch_anchor: "## Fail loud"
"""

_BASE_TS = """\
export function add(a: number, b: number): number {
  return a + b;
}
"""

_PLANTS: dict[str, str] = {
    "empty-catch": """
export function parse(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {}
  return null;
}
""",
    "clean": """
export function double(n: number): number {
  return n * 2;
}
""",
}


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *_GIT_ID, *args], cwd=repo, check=True,
                   capture_output=True, text=True, encoding="utf-8")


def build(dest: Path, plant: Plant) -> None:
    """Create the fixture repository at ``dest`` (which must not exist)."""
    if plant not in _PLANTS:
        raise ValueError(f"unknown plant {plant!r}; expected one of {sorted(_PLANTS)}")
    dest.mkdir(parents=True)
    subprocess.run(["git", "-c", "init.defaultBranch=main", "init"], cwd=dest, check=True,
                   capture_output=True, text=True, encoding="utf-8")
    (dest / MANDATES_REL).parent.mkdir(parents=True, exist_ok=True)
    (dest / MANDATES_REL).write_text(_MANDATES, encoding="utf-8")
    (dest / ARCH_REL).write_text("# Fixture doctrine\n\n## Fail loud\n", encoding="utf-8")
    app = dest / "src" / "app.ts"
    app.parent.mkdir()
    app.write_text(_BASE_TS, encoding="utf-8")
    _git(dest, "add", "-A")
    _git(dest, "commit", "-m", "base")
    _git(dest, "checkout", "-b", "feature")
    app.write_text(_BASE_TS + _PLANTS[plant], encoding="utf-8")
    _git(dest, "commit", "-am", f"feature ({plant})")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="action_fixture_host")
    parser.add_argument("dest", type=Path)
    parser.add_argument("--plant", required=True, choices=sorted(_PLANTS))
    args = parser.parse_args(argv)
    build(args.dest, args.plant)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
