"""Host detector loader and wrapped runners (spec 4.4, 4.7)."""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

from acf.detectors import host
from acf.detectors.host import HostHit, load_host_detector, scan_host_ast_file, scan_host_guards
from acf.exceptions import AcfInputError, DetectorPackError, UnknownDetectorError
from acf.registry import Mandate, MandateRegistry

CI = frozenset({"ci"})
IMPORT_HIT = "from acf.detectors.host import HostHit\n"


def write(root: Path, rel: str, body: str) -> Path:
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(textwrap.dedent(body), encoding="utf-8")
    return target


def row(detector, detection="ast", *, id="host.row", languages="python", call_sites=("ci",), status="enforced"):
    return Mandate(
        id=id, title="t", severity="BLOCK", detection=detection, detector=detector,
        languages=languages, call_sites=list(call_sites), exemption_tokens=[],
        status=status, arch_anchor="x", params=None,
    )


def registry(*rows):
    return MandateRegistry(mandates=list(rows), source_path="mandates.yml")


def run_ast(root, body, *, path="a.py", text="x = 1\n", detector="g.py:scan", language="python"):
    write(root, "g.py", IMPORT_HIT + textwrap.dedent(body))
    return scan_host_ast_file(
        root, text, path, None, registry(row(detector, languages="both")), language=language, call_sites=CI
    )


def run_guard(root, body, *, files=("a.md",), file_lines=None, detector="g.py:scan"):
    write(root, "g.py", IMPORT_HIT + textwrap.dedent(body))
    lines = {} if file_lines is None else file_lines
    found = scan_host_guards(root, files, registry(row(detector, "guard")), lines, call_sites=CI)
    return found, lines


AST_OK = """
def scan(text, path, added_lines, *, tree, params):
    return [HostHit(path=path, line=1, message="m")]
"""


# ---------------------------------------------------------------- loader


def test_imports_sibling_package_and_frozen_dataclass_with_future_annotations(tmp_path, fresh_host_loader):
    write(tmp_path, "hostpkg/__init__.py", "VALUE = 7\n")
    write(tmp_path, "hostpkg/util.py", "def f():\n    return 1\n")
    (tmp_path / "g.py").write_text(
        "from __future__ import annotations\n"
        "from dataclasses import dataclass\n"
        "from acf.detectors.host import HostHit\n"
        "from hostpkg.util import f\n\n"
        "@dataclass(frozen=True)\n"
        "class Rec:\n    n: int\n    label: str\n\n"
        "def scan(text, path, added_lines, *, tree, params):\n"
        "    rec = Rec(f(), 'x')\n"
        "    return [HostHit(path=path, line=rec.n, message=rec.label)]\n",
        encoding="utf-8",
    )
    found = scan_host_ast_file(
        tmp_path, "x\n", "a.py", None, registry(row("g.py:scan")), language="python", call_sites=CI
    )
    assert [(f.path, f.line, f.message) for f in found] == [("a.py", 1, "x")]


def test_two_callables_in_one_file_load_one_module(tmp_path, fresh_host_loader):
    write(tmp_path, "g.py", "def one(): return []\ndef two(): return []\n")
    before = {k for k in sys.modules if k.startswith("_acf_host_")}
    load_host_detector(tmp_path, "g.py:one")
    load_host_detector(tmp_path, "g.py:two")
    assert len({k for k in sys.modules if k.startswith("_acf_host_")} - before) == 1


def test_failed_first_load_removes_entry_and_failed_lookup_keeps_it(tmp_path, fresh_host_loader):
    def hosts():
        return {k for k in sys.modules if k.startswith("_acf_host_")}

    write(tmp_path, "bad.py", "raise RuntimeError('boom')\n")
    base = hosts()
    with pytest.raises(UnknownDetectorError, match="boom"):
        load_host_detector(tmp_path, "bad.py:scan")
    assert hosts() == base
    write(tmp_path, "ok.py", "def scan(): return []\n")
    load_host_detector(tmp_path, "ok.py:scan")
    loaded = hosts()
    assert len(loaded) == len(base) + 1
    with pytest.raises(UnknownDetectorError, match="not a callable"):
        load_host_detector(tmp_path, "ok.py:missing")
    assert hosts() == loaded


def test_root_is_appended_to_end_of_sys_path(tmp_path, fresh_host_loader):
    write(tmp_path, "g.py", "def scan(): return []\n")
    load_host_detector(tmp_path, "g.py:scan")
    assert sys.path[-1] == str(tmp_path.resolve())


def test_missing_file(tmp_path, fresh_host_loader):
    with pytest.raises(UnknownDetectorError, match="no file"):
        load_host_detector(tmp_path, "nope.py:scan")


@pytest.mark.parametrize(
    ("body", "match"),
    [
        ("import not_a_real_module_xyz\n", "ModuleNotFoundError"),
        ("import sys\nsys.exit(0)\n", "SystemExit"),
        ("def scan(): return []\ndef __getattr__(name):\n    raise RuntimeError('lookup boom')\n", "lookup boom"),
    ],
)
def test_unloadable_module_is_unknown_detector(tmp_path, fresh_host_loader, body, match):
    write(tmp_path, "g.py", body)
    attr = "other" if "__getattr__" in body else "scan"
    with pytest.raises(UnknownDetectorError, match=match):
        load_host_detector(tmp_path, f"g.py:{attr}")


def test_missing_callable(tmp_path, fresh_host_loader):
    write(tmp_path, "g.py", "x = 1\n")
    with pytest.raises(UnknownDetectorError, match="not a callable"):
        load_host_detector(tmp_path, "g.py:scan")


def test_stat_permission_error_is_unknown_detector(tmp_path, fresh_host_loader, monkeypatch):
    write(tmp_path, "g.py", "def scan(): return []\n")
    original = Path.is_file

    def is_file(self, *a, **k):
        if self.name == "g.py":
            raise PermissionError("denied")
        return original(self, *a, **k)

    monkeypatch.setattr(Path, "is_file", is_file)
    with pytest.raises(UnknownDetectorError, match="PermissionError"):
        load_host_detector(tmp_path, "g.py:scan")


def test_second_root_is_refused(tmp_path, fresh_host_loader):
    first, second = tmp_path / "one", tmp_path / "two"
    write(first, "g.py", "def scan(): return []\n")
    write(second, "g.py", "def scan(): return []\n")
    load_host_detector(first, "g.py:scan")
    with pytest.raises(AcfInputError, match="one host root per process"):
        load_host_detector(second, "g.py:scan")


# ---------------------------------------------------------------- ast runner


def test_two_ast_rows_parse_once(tmp_path, fresh_host_loader, monkeypatch):
    write(tmp_path, "g.py", IMPORT_HIT + "def one(text, path, added_lines, *, tree, params):\n    return []\n"
          "def two(text, path, added_lines, *, tree, params):\n    return []\n")
    calls = []
    real = host.parse_python
    monkeypatch.setattr(host, "parse_python", lambda t: calls.append(t) or real(t))
    scan_host_ast_file(
        tmp_path, "x = 1\n", "a.py", None,
        registry(row("g.py:one", id="h.one"), row("g.py:two", id="h.two")),
        language="python", call_sites=CI,
    )
    assert len(calls) == 1


def test_ast_runner_filters_by_language_and_call_site(tmp_path, fresh_host_loader):
    write(tmp_path, "g.py", IMPORT_HIT + AST_OK)
    ts_row = registry(row("g.py:scan", languages="typescript"))
    assert scan_host_ast_file(tmp_path, "x\n", "a.py", None, ts_row, language="python", call_sites=CI) == []
    hook_row = registry(row("g.py:scan", call_sites=("hook",)))
    assert scan_host_ast_file(tmp_path, "x\n", "a.py", None, hook_row, language="python", call_sites=CI) == []
    ok = registry(row("g.py:scan"))
    assert len(scan_host_ast_file(tmp_path, "x\n", "a.py", None, ok, language="python", call_sites=CI)) == 1


def test_ast_runner_skips_unparsable_python(tmp_path, fresh_host_loader):
    write(tmp_path, "g.py", IMPORT_HIT + AST_OK)
    found = scan_host_ast_file(
        tmp_path, "def (:\n", "a.py", None, registry(row("g.py:scan")), language="python", call_sites=CI
    )
    assert found == []


def test_typescript_ast_receives_no_tree(tmp_path, fresh_host_loader):
    body = """
    def scan(text, path, added_lines, *, tree, params):
        assert tree is None
        return [HostHit(path=path, line=1, message="ts")]
    """
    found = run_ast(tmp_path, body, path="a.ts", language="typescript")
    assert [f.message for f in found] == ["ts"]


def test_finding_is_built_from_the_row(tmp_path, fresh_host_loader):
    found = run_ast(tmp_path, AST_OK)
    assert (found[0].mandate_id, found[0].severity.value, found[0].detector, found[0].detection) == (
        "host.row", "BLOCK", "g.py:scan", "ast"
    )


@pytest.mark.parametrize(
    "expr",
    [
        "5",
        "type('Sub', (HostHit,), {'boom': property(lambda self: 1 / 0)})(path=path, line=1, message='m')",
        "HostHit.model_construct(path=b'a.py', line=1, message='m')",
        "HostHit.model_construct(path=5, line=1, message='m')",
        "HostHit.model_construct(path=path, line='5', message='m')",
        "HostHit.model_construct(path=path, line=True, message='m')",
        "HostHit(path='b.py', line=1, message='m')",
    ],
    ids=["non-hit", "subclass", "bytes-path", "int-path", "str-line", "bool-line", "wrong-path"],
)
def test_ast_runner_refuses_bad_items(tmp_path, fresh_host_loader, expr):
    body = f"def scan(text, path, added_lines, *, tree, params):\n    return [{expr}]\n"
    with pytest.raises(DetectorPackError):
        run_ast(tmp_path, body)


def test_str_subclass_path_and_bool_line_refused_at_construction(tmp_path, fresh_host_loader):
    for args in ("path=S(path), line=1", "path=path, line=True"):
        body = (
            "class S(str):\n    pass\n"
            "def scan(text, path, added_lines, *, tree, params):\n"
            f"    return [HostHit({args}, message='m')]\n"
        )
        with pytest.raises(DetectorPackError, match="ValidationError"):
            run_ast(tmp_path, body)


def test_str_return_is_refused(tmp_path, fresh_host_loader):
    with pytest.raises(DetectorPackError, match="returned str"):
        run_ast(tmp_path, "def scan(text, path, added_lines, *, tree, params):\n    return 'abc'\n")


_DATACLASS = (
    "from dataclasses import dataclass\n"
    "@dataclass\nclass Rec:\n    line_text: object\n    def __str__(self):\n        return self.line_text.strip()\n"
)


@pytest.mark.parametrize(
    "body",
    [
        "def scan(text, path, added_lines, *, tree, params):\n    raise AcfInputError('x')\n",
        "def scan(text, path, added_lines, *, tree, params):\n    yield HostHit(path=path, line=1, message='m')\n    raise RuntimeError('mid')\n",
        "def scan(text, path, added_lines, *, tree, params):\n    yield HostHit(path='/abs', line=1, message='m')\n",
        "import sys\ndef scan(text, path, added_lines, *, tree, params):\n    sys.exit(0)\n",
        "class E(Exception):\n    def __str__(self):\n        raise RuntimeError('str')\n"
        "def scan(text, path, added_lines, *, tree, params):\n    raise E('x')\n",
        _DATACLASS + "def scan(text, path, added_lines, *, tree, params):\n    raise ValueError(Rec(None))\n",
        "class E(Exception):\n    def __str__(self):\n        raise SystemExit(1)\n"
        "def scan(text, path, added_lines, *, tree, params):\n    raise E('x')\n",
        "def scan(text, path, added_lines, *, tree, params):\n    yield HostHit(path=path, line=1, message='m')\n    yield 5\n",
        "class Weird(BaseException):\n    pass\n"
        "def scan(text, path, added_lines, *, tree, params):\n    raise Weird()\n",
    ],
    ids=["acf-error", "gen-mid", "gen-invalid-hit", "sys-exit", "str-raises", "dataclass-arg",
         "str-raises-systemexit", "valid-then-invalid", "custom-base-exception"],
)
def test_ast_runner_wraps_host_failures(tmp_path, fresh_host_loader, body):
    body = "from acf.exceptions import AcfInputError\n" + body
    with pytest.raises(DetectorPackError, match="host.row"):
        run_ast(tmp_path, body)


def test_unprintable_exception_is_still_reported(tmp_path, fresh_host_loader):
    body = (
        "class E(Exception):\n    def __str__(self):\n        raise RuntimeError('str')\n"
        "def scan(text, path, added_lines, *, tree, params):\n    raise E('x')\n"
    )
    with pytest.raises(DetectorPackError, match="message unavailable"):
        run_ast(tmp_path, body)


def test_keyboard_interrupt_propagates(tmp_path, fresh_host_loader):
    with pytest.raises(KeyboardInterrupt):
        run_ast(tmp_path, "def scan(text, path, added_lines, *, tree, params):\n    raise KeyboardInterrupt()\n")


# ---------------------------------------------------------------- guard runner


def test_guard_adds_lines_of_flagged_file(tmp_path, fresh_host_loader):
    (tmp_path / "notes.md").write_text("one\ntwo\n", encoding="utf-8")
    body = "def scan(repo_root, changed_files, *, params):\n    return [HostHit(path='notes.md', line=2, message='m')]\n"
    found, lines = run_guard(tmp_path, body)
    assert len(found) == 1
    assert lines == {"notes.md": ["one", "two"]}


def test_guard_keeps_entry_the_gate_holds(tmp_path, fresh_host_loader):
    (tmp_path / "notes.md").write_text("disk\n", encoding="utf-8")
    body = "def scan(repo_root, changed_files, *, params):\n    return [HostHit(path='notes.md', line=1, message='m')]\n"
    _, lines = run_guard(tmp_path, body, file_lines={"notes.md": ["gate"]})
    assert lines == {"notes.md": ["gate"]}


def test_guard_maps_missing_file_and_directory_to_empty(tmp_path, fresh_host_loader):
    (tmp_path / "adir").mkdir()
    body = (
        "def scan(repo_root, changed_files, *, params):\n"
        "    return [HostHit(path='gone.md', line=1, message='m'), HostHit(path='adir', line=1, message='m')]\n"
    )
    found, lines = run_guard(tmp_path, body)
    assert len(found) == 2
    assert lines == {"gone.md": [], "adir": []}


def test_guard_read_oserror_is_detector_pack_error(tmp_path, fresh_host_loader, monkeypatch):
    (tmp_path / "notes.md").write_text("x\n", encoding="utf-8")
    original = Path.read_text

    def read_text(self, *a, **k):
        if self.name == "notes.md":
            raise PermissionError("denied")
        return original(self, *a, **k)

    monkeypatch.setattr(Path, "read_text", read_text)
    body = "def scan(repo_root, changed_files, *, params):\n    return [HostHit(path='notes.md', line=1, message='m')]\n"
    with pytest.raises(DetectorPackError, match="notes.md"):
        run_guard(tmp_path, body)


def test_guard_receives_root_and_changed_tuple(tmp_path, fresh_host_loader):
    body = (
        "def scan(repo_root, changed_files, *, params):\n"
        "    assert isinstance(changed_files, tuple)\n"
        "    return [HostHit(path=changed_files[0], line=1, message=str(repo_root.is_absolute()))]\n"
    )
    found, _ = run_guard(tmp_path, body, files=["x.md"])
    assert found[0].message == "True"


def test_guard_hit_through_symlink_outside_root_is_refused(tmp_path, fresh_host_loader):
    repo, outside = tmp_path / "repo", tmp_path / "outside"
    repo.mkdir()
    outside.mkdir()
    try:
        (repo / "link").symlink_to(outside, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("platform cannot create symlinks")
    body = "def scan(repo_root, changed_files, *, params):\n    return [HostHit(path='link/x.md', line=1, message='m')]\n"
    with pytest.raises(DetectorPackError, match="outside the repository"):
        run_guard(repo, body)


def test_guard_wraps_failures_and_refuses_str_return(tmp_path, fresh_host_loader):
    with pytest.raises(DetectorPackError):
        run_guard(tmp_path, "def scan(repo_root, changed_files, *, params):\n    return 'abc'\n")
    with pytest.raises(DetectorPackError):
        run_guard(tmp_path, "def scan(repo_root, changed_files, *, params):\n    raise RuntimeError('x')\n")


# ---------------------------------------------------------------- review focus tests


def test_module_shared_by_ast_and_guard_rows_executes_once(tmp_path, fresh_host_loader):  # Review Focus 3
    counter = tmp_path / "count.txt"
    write(tmp_path, "g.py", IMPORT_HIT + f"with open({str(counter)!r}, 'a') as fh:\n    fh.write('x')\n"
          "def scan_ast(text, path, added_lines, *, tree, params):\n    return []\n"
          "def scan_guard(repo_root, changed_files, *, params):\n    return []\n")
    reg = registry(row("g.py:scan_ast", id="h.ast"), row("g.py:scan_guard", "guard", id="h.guard"))
    scan_host_ast_file(tmp_path, "x\n", "a.py", None, reg, language="python", call_sites=CI)
    scan_host_guards(tmp_path, ["a.py"], reg, {}, call_sites=CI)
    assert counter.read_text(encoding="utf-8") == "x"


def test_guard_flagging_one_file_twice_reads_it_once(tmp_path, fresh_host_loader, monkeypatch):  # Review Focus 5
    (tmp_path / "notes.md").write_text("a\nb\n", encoding="utf-8")
    reads = []
    original = Path.read_text

    def spy(self, *a, **k):
        reads.append(self.name)
        return original(self, *a, **k)

    monkeypatch.setattr(Path, "read_text", spy)
    body = (
        "def scan(repo_root, changed_files, *, params):\n"
        "    return [HostHit(path='notes.md', line=1, message='m'), HostHit(path='notes.md', line=2, message='n')]\n"
    )
    found, lines = run_guard(tmp_path, body)
    assert len(found) == 2
    assert reads.count("notes.md") == 1
    assert lines["notes.md"] == ["a", "b"]
