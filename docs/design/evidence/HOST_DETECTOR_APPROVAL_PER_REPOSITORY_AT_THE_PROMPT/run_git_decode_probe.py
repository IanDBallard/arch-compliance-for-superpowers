"""Probe: what today's ``acf.diff.run_git`` returns for a repository under a
non-ASCII directory name, decoded with the interpreter's locale codec.

Run from the repository root:

    python docs/design/evidence/HOST_DETECTOR_APPROVAL_PER_REPOSITORY_AT_THE_PROMPT/run_git_decode_probe.py

The probe re-launches itself in a child interpreter with ``PYTHONUTF8=0`` so the
locale codec is the platform's, not UTF-8 mode, and imports ``run_git`` from this
checkout's ``plugins/arch-compliance/python``. For each directory name it records
the locale codec, ``returncode``, ``repr(stdout)``, whether ``stdout`` equals the
UTF-8-decoded truth, and any exception the reader thread raised (caught through
``threading.excepthook``, which is where ``subprocess`` on Windows reports it).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

NAMES = [
    "ascii_dir",
    "Á_dir",   # A acute: UTF-8 C3 81; 0x81 is undefined in cp1252
    "Ý_dir",   # Y acute: UTF-8 C3 9D; 0x9D is undefined in cp1252
    "é_dir",   # e acute: UTF-8 C3 A9; both bytes defined in cp1252
    "ü_dir",   # u umlaut: UTF-8 C3 BC; both bytes defined in cp1252
    "日本_dir",  # CJK: UTF-8 E6 97 A5 E6 9C AC
]

REPO = Path(__file__).resolve().parents[4]
PKG = REPO / "plugins" / "arch-compliance" / "python"


def child(root: str) -> None:
    import locale
    import threading

    sys.path.insert(0, str(PKG))
    from acf.diff import run_git

    thread_errors: list[str] = []
    threading.excepthook = lambda a: thread_errors.append(
        f"{a.exc_type.__name__}: {a.exc_value}"
    )
    rows = []
    for name in NAMES:
        repo = Path(root) / name
        thread_errors.clear()
        proc = run_git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")
        truth = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            cwd=repo, capture_output=True, check=False,
        ).stdout.decode("utf-8")
        rows.append({
            "dir": name,
            "utf8_bytes_of_name": name.encode("utf-8").hex(" "),
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stdout_matches_utf8_truth": proc.stdout == truth,
            "reader_thread_error": list(thread_errors),
        })
    print(json.dumps({
        "python": sys.version.split()[0],
        "platform": sys.platform,
        "locale_encoding": locale.getpreferredencoding(False),
        "utf8_mode": sys.flags.utf8_mode,
        "rows": rows,
    }, ensure_ascii=True, indent=2))


def main() -> None:
    git = subprocess.run(["git", "--version"], capture_output=True, text=True, check=True)
    with tempfile.TemporaryDirectory() as root:
        for name in NAMES:
            d = Path(root) / name
            d.mkdir()
            subprocess.run(["git", "init", "-q", str(d)], check=True)
        env = {**os.environ, "PYTHONUTF8": "0"}
        env.pop("PYTHONIOENCODING", None)
        out = subprocess.run(
            [sys.executable, __file__, "--child", root],
            capture_output=True, env=env, check=True,
        ).stdout.decode("ascii")
    print(git.stdout.strip())
    print(out.replace(root.replace("\\", "\\\\"), "<tmp>").replace(
        Path(root).as_posix(), "<tmp>"))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--child":
        child(sys.argv[2])
    else:
        main()
