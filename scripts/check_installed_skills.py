"""Byte-check the installed gate skills against this clone.

Usage: python scripts/check_installed_skills.py <INSTALL_PATH>

INSTALL_PATH is the installed plugin's directory (the `installPath` that
`~/.claude/plugins/installed_plugins.json` records). Every file under this clone's
`plugins/arch-compliance/skills/{adversarial-design-review,responding-to-adversarial-review}`
must exist at the same relative path under `<INSTALL_PATH>/skills/` with identical bytes.
Prints `installed gate skills identical to the clone` and exits 0, or prints each differing
or missing relative path and exits 1 (spec docs/design/PLUGIN_SELF_HOSTING_AND_DOCTRINE.md §5.3).
"""
from __future__ import annotations

import filecmp
import sys
from pathlib import Path

GATE_SKILLS = ("adversarial-design-review", "responding-to-adversarial-review")
REPO_ROOT = Path(__file__).resolve().parents[1]


def differing_files(install_path: Path, clone: Path) -> list[str]:
    plugin = clone / "plugins" / "arch-compliance"
    bad: list[str] = []
    for skill in GATE_SKILLS:
        skill_dir = plugin / "skills" / skill
        for f in sorted(skill_dir.rglob("*")):
            if not f.is_file():
                continue
            g = install_path / "skills" / skill / f.relative_to(skill_dir)
            if not g.is_file() or not filecmp.cmp(f, g, shallow=False):
                bad.append(f.relative_to(plugin).as_posix())
    return bad


def main(argv: list[str] | None = None, *, clone: Path | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    bad = differing_files(Path(args[0]), REPO_ROOT if clone is None else clone)
    if bad:
        for path in bad:
            print(path)
        return 1
    print("installed gate skills identical to the clone")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
