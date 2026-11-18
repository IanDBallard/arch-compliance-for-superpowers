from pathlib import Path

import pytest

from acf.detectors import typescript_bridge
from acf.detectors.typescript_bridge import TS_MANDATE_IDS, scan_typescript_file
from acf.exceptions import DetectorPackError
from acf.finding import Severity

FIX = Path(__file__).parent / "fixtures" / "typescript"


def test_detector_ids():
    assert set(TS_MANDATE_IDS) == {"empty_catch", "explicit_any"}


def _fake_tsx(pack: Path, bin_field: object = "./dist/cli.mjs") -> Path:
    import json

    tsx = pack / "node_modules" / "tsx"
    (tsx / "dist").mkdir(parents=True)
    (tsx / "dist" / "cli.mjs").write_text("// fake tsx cli\n", encoding="utf-8")
    (tsx / "package.json").write_text(json.dumps({"name": "tsx", "bin": bin_field}), encoding="utf-8")
    return tsx


def _stub_pack(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, items: list) -> None:
    import json
    import subprocess

    pack = tmp_path / "typescript"
    _fake_tsx(pack)
    monkeypatch.setattr(typescript_bridge, "_PACK_ROOT", pack)
    monkeypatch.setattr(typescript_bridge.shutil, "which", lambda name: str(tmp_path / "node"))

    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args, 0, stdout=json.dumps(items), stderr="")

    monkeypatch.setattr(typescript_bridge.subprocess, "run", fake_run)


def _item(**over):
    base = {
        "detector": "empty_catch",
        "severity": "BLOCK",
        "path": "a.ts",
        "line": 3,
        "message": "m",
    }
    return {**base, **over}


@pytest.mark.parametrize(
    "over",
    [
        {"detector": "nope"},
        {"line": "5"},
        {"line": 0},
        {"line": True},
        {"message": ""},
    ],
)
def test_bad_ts_item_is_refused(tmp_path, monkeypatch, over):
    _stub_pack(monkeypatch, tmp_path, [_item(**over)])
    with pytest.raises(DetectorPackError):
        scan_typescript_file(tmp_path / "a.ts")


@pytest.mark.parametrize("detector", sorted(TS_MANDATE_IDS))
def test_valid_item_is_stamped_by_the_bridge(tmp_path, monkeypatch, detector):
    _stub_pack(monkeypatch, tmp_path, [_item(detector=detector)])
    (finding,) = scan_typescript_file(tmp_path / "a.ts")
    assert finding.mandate_id == TS_MANDATE_IDS[detector]


def test_missing_node_modules_error_is_actionable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A fresh plugin install has no node_modules in the pack dir; the error
    must say exactly how to fix it, not fail with an opaque npx error."""
    fake_pack = tmp_path / "typescript"
    (fake_pack / "src").mkdir(parents=True)
    monkeypatch.setattr(typescript_bridge, "_PACK_ROOT", fake_pack)
    with pytest.raises(DetectorPackError) as exc_info:
        scan_typescript_file(FIX / "bad.tsx")
    message = str(exc_info.value)
    assert "npm ci" in message
    assert fake_pack.as_posix() in message


def test_empty_catch_via_bridge():
    path = FIX / "bad.tsx"
    # empty catch is on line 4 of the fixture
    findings = scan_typescript_file(path, added_lines=frozenset({4}))
    assert any(
        f.mandate_id == "fail-loud.empty-catch"
        and f.severity == Severity.BLOCK
        and f.detector == "empty_catch"
        for f in findings
    )


def test_clean_file_no_findings():
    path = FIX / "good.tsx"
    findings = scan_typescript_file(path, added_lines=frozenset({1, 2, 3, 4, 5, 6, 7, 8}))
    assert findings == []


def test_explicit_any_via_bridge():
    path = FIX / "bad.tsx"
    # `: any` on line 7, `as any` on line 8
    findings = scan_typescript_file(path, added_lines=frozenset({7, 8}))
    any_findings = [f for f in findings if f.mandate_id == "no-shims.explicit-any"]
    assert len(any_findings) >= 1
    assert all(f.severity == Severity.WARN and f.detector == "explicit_any" for f in any_findings)


def test_line_filter_excludes_other_lines():
    path = FIX / "bad.tsx"
    # Only request a clean line — should not report the empty catch on line 4
    findings = scan_typescript_file(path, added_lines=frozenset({1}))
    assert findings == []


# --- issue #34: the bridge runs node directly, never a shell or a .cmd shim ---


def test_argv_runs_node_directly_without_shell(monkeypatch: pytest.MonkeyPatch) -> None:
    import shutil
    import subprocess

    node = shutil.which("node")
    assert node is not None, "node must be on PATH for the TypeScript pack tests"
    captured: dict = {}

    def spy_run(cmd, **kwargs):
        captured["cmd"] = cmd
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(cmd, 0, stdout="[]", stderr="")

    monkeypatch.setattr(typescript_bridge.subprocess, "run", spy_run)
    assert scan_typescript_file(FIX / "good.tsx", added_lines=frozenset({1})) == []

    cmd = captured["cmd"]
    assert isinstance(cmd, list)
    assert not captured["kwargs"].get("shell", False)
    assert cmd[0] == node
    assert Path(cmd[0]).suffix.lower() not in {".cmd", ".bat"}
    assert not any(str(arg).lower().endswith((".cmd", ".bat")) for arg in cmd)
    entry = Path(cmd[1])
    assert entry.is_file()
    assert entry.parent.parent.name == "tsx"
    assert cmd[2:4] == ["src/scan.ts", "--file"]


def test_missing_node_is_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_pack(monkeypatch, tmp_path, [])
    monkeypatch.setattr(typescript_bridge.shutil, "which", lambda name: None)
    with pytest.raises(DetectorPackError, match="node"):
        scan_typescript_file(tmp_path / "a.ts")


@pytest.mark.parametrize("shim", ["node.cmd", "NODE.BAT"])
def test_node_shim_is_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, shim: str) -> None:
    _stub_pack(monkeypatch, tmp_path, [])
    monkeypatch.setattr(typescript_bridge.shutil, "which", lambda name: str(tmp_path / shim))
    with pytest.raises(DetectorPackError, match="shim"):
        scan_typescript_file(tmp_path / "a.ts")


def test_missing_tsx_package_is_refused_with_npm_ci_hint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    pack = tmp_path / "typescript"
    (pack / "node_modules").mkdir(parents=True)
    monkeypatch.setattr(typescript_bridge, "_PACK_ROOT", pack)
    with pytest.raises(DetectorPackError) as exc_info:
        scan_typescript_file(tmp_path / "a.ts")
    message = str(exc_info.value)
    assert "tsx" in message
    assert "npm ci" in message
    assert pack.as_posix() in message


@pytest.mark.parametrize(
    "bin_field",
    [None, 7, {"other": "./dist/cli.mjs"}, "./dist/missing.mjs", "./dist/tsx.cmd"],
)
def test_bad_tsx_bin_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, bin_field: object
) -> None:
    pack = tmp_path / "typescript"
    _fake_tsx(pack, bin_field)
    monkeypatch.setattr(typescript_bridge, "_PACK_ROOT", pack)
    with pytest.raises(DetectorPackError, match="tsx"):
        scan_typescript_file(tmp_path / "a.ts")


def test_tsx_bin_object_form_is_accepted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import subprocess

    pack = tmp_path / "typescript"
    tsx = _fake_tsx(pack, {"tsx": "./dist/cli.mjs"})
    monkeypatch.setattr(typescript_bridge, "_PACK_ROOT", pack)
    monkeypatch.setattr(typescript_bridge.shutil, "which", lambda name: str(tmp_path / "node"))
    captured: dict = {}

    def spy_run(cmd, **kwargs):
        captured["cmd"] = cmd
        return subprocess.CompletedProcess(cmd, 0, stdout="[]", stderr="")

    monkeypatch.setattr(typescript_bridge.subprocess, "run", spy_run)
    scan_typescript_file(tmp_path / "a.ts")
    assert Path(captured["cmd"][1]) == tsx / "dist" / "cli.mjs"


def _metachar_name(tmp_path: Path) -> str:
    """A file name carrying cmd.exe metacharacters; ^ only where the filesystem takes it."""
    candidate = "meta&x%PATH%^y.tsx"
    try:
        (tmp_path / candidate).write_text("", encoding="utf-8")
    except OSError:
        return "meta&x%PATH%y.tsx"
    (tmp_path / candidate).unlink()
    return candidate


def test_end_to_end_scan_of_file_named_with_shell_metacharacters(tmp_path: Path) -> None:
    name = _metachar_name(tmp_path)
    target = tmp_path / name
    target.write_text((FIX / "bad.tsx").read_text(encoding="utf-8"), encoding="utf-8")
    assert "&" in target.name and "%" in target.name

    findings = scan_typescript_file(target, added_lines=frozenset({4}))
    assert [f.mandate_id for f in findings] == ["fail-loud.empty-catch"]
    assert findings[0].path.endswith(name)
